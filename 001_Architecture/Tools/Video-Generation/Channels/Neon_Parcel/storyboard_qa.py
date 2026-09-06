#!/usr/bin/env python3
"""Fail-closed QA for generated storyboard sheets."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from storyboard_contract import validate_spec


FRAME_CHECKS = (
    "subject_presence",
    "object_state",
    "spatial_relationship",
    "action_state",
    "caption",
)
TRANSITION_CHECKS = (
    "causal_transition",
    "chronology",
    "camera_geometry",
    "physics",
)
ALLOWED_STATUSES = {"pass", "fail", "ambiguous", "missing"}
MIN_CONFIDENCE = 0.75


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _status(value: Any, label: str) -> str:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    result = value.get("status")
    if result not in ALLOWED_STATUSES:
        raise ValueError(f"{label}.status must be one of {sorted(ALLOWED_STATUSES)}")
    confidence = value.get("confidence")
    if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        raise ValueError(f"{label}.confidence must be a number from 0 to 1")
    evidence = value.get("evidence")
    if not isinstance(evidence, str) or not evidence.strip():
        raise ValueError(f"{label}.evidence must be a non-empty string")
    if result == "pass" and confidence < MIN_CONFIDENCE:
        return "ambiguous"
    return result


def normalize_vision_report(vision_report: dict[str, Any]) -> dict[str, Any]:
    """Normalize equivalent provider naming without relaxing the QA schema."""
    if not isinstance(vision_report, dict):
        raise ValueError("vision report must be an object")
    normalized = dict(vision_report)
    if "frame_checks" not in normalized and isinstance(normalized.get("frame_analysis"), list):
        normalized["frame_checks"] = normalized["frame_analysis"]
    if "transition_checks" not in normalized and isinstance(normalized.get("transition_analysis"), list):
        transitions = []
        for item in normalized["transition_analysis"]:
            if not isinstance(item, dict):
                transitions.append(item)
                continue
            value = dict(item)
            frames = value.pop("frames", None)
            if isinstance(frames, str) and "-" in frames:
                start, end = frames.split("-", 1)
                try:
                    value["from_frame"] = int(start)
                    value["to_frame"] = int(end)
                except ValueError:
                    pass
            transitions.append(value)
        normalized["transition_checks"] = transitions
    return normalized


def build_inspection_prompt(spec: dict[str, Any]) -> str:
    """Build the vision instruction from the exact contract being checked."""
    validate_spec(spec)
    lines = [
        "Inspect the attached storyboard sheet against the structured contract below.",
        "Return JSON only. Do not infer missing visual evidence and do not mark ambiguity as pass.",
        "For every frame, report subject_presence, object_state, spatial_relationship, action_state, and caption.",
        "For every adjacent frame pair, report causal_transition, chronology, camera_geometry, and physics.",
        "Each check must contain status (pass, fail, ambiguous, or missing), confidence from 0 to 1, and concrete visual evidence.",
        "Caption status is pass only when the rendered caption matches the exact contract text.",
        "Physics status is pass only when the visible transition is physically plausible and causally supported.",
        "",
        "CONTRACT:",
        json.dumps(spec, indent=2, ensure_ascii=True),
    ]
    return "\n".join(lines)


def _finding(frame: str, category: str, check: dict[str, Any]) -> dict[str, Any]:
    status = check["status"]
    return {
        "frame": frame,
        "category": category,
        "severity": "error" if status == "fail" else "warning",
        "status": status,
        "confidence": check["confidence"],
        "evidence": check["evidence"],
        "recommendation": (
            "Regenerate the storyboard while preserving the contract."
            if status == "fail"
            else "Require human review or stronger visual evidence before retrying."
        ),
    }


def evaluate_report(
    spec: dict[str, Any],
    vision_report: dict[str, Any],
    candidate_image: Path,
    contract_path: Path | None = None,
) -> dict[str, Any]:
    """Normalize a vision report into a strict, auditable QA decision."""
    validate_spec(spec)
    candidate_image = Path(candidate_image)
    now = datetime.now(timezone.utc).isoformat()
    base = {
        "evaluated_at": now,
        "candidate_image": str(candidate_image),
        "candidate_sha256": _sha256(candidate_image) if candidate_image.is_file() else None,
        "contract_path": str(contract_path) if contract_path else None,
        "contract_sha256": _sha256(contract_path) if contract_path and contract_path.is_file() else None,
        "status": "manual_review",
        "overall_confidence": 0.0,
        "checked_frames": [],
        "checked_transitions": [],
        "findings": [],
    }
    if not candidate_image.is_file():
        base["findings"].append(
            {
                "frame": "all",
                "category": "candidate_image",
                "severity": "error",
                "status": "missing",
                "confidence": 1.0,
                "evidence": "Candidate storyboard image does not exist.",
                "recommendation": "Generate or restore the candidate before QA.",
            }
        )
        return base
    vision_report = normalize_vision_report(vision_report)

    frame_reports = vision_report.get("frame_checks")
    transition_reports = vision_report.get("transition_checks")
    if not isinstance(frame_reports, list) or not isinstance(transition_reports, list):
        base["findings"].append(
            {
                "frame": "all",
                "category": "report_schema",
                "severity": "error",
                "status": "missing",
                "confidence": 1.0,
                "evidence": "Vision report is missing frame_checks or transition_checks.",
                "recommendation": "Retry vision inspection with the required JSON schema.",
            }
        )
        return base

    expected_frames = list(range(1, len(spec["frames"]) + 1))
    expected_transitions = [(number, number + 1) for number in expected_frames[:-1]]
    by_frame = {item.get("frame"): item for item in frame_reports if isinstance(item, dict)}
    by_transition = {
        (item.get("from_frame"), item.get("to_frame")): item
        for item in transition_reports
        if isinstance(item, dict)
    }
    all_statuses: list[str] = []
    confidences: list[float] = []

    for frame_number in expected_frames:
        report = by_frame.get(frame_number)
        if not isinstance(report, dict):
            check = {"status": "missing", "confidence": 1.0, "evidence": "No report for this panel."}
            for category in FRAME_CHECKS:
                base["findings"].append(_finding(f"{frame_number}", category, check))
                all_statuses.append("missing")
            continue
        base["checked_frames"].append(frame_number)
        for category in FRAME_CHECKS:
            try:
                check_status = _status(report.get(category), f"frame {frame_number}.{category}")
                check = dict(report[category])
                check["status"] = check_status
            except ValueError as error:
                check_status = "missing"
                check = {"status": "missing", "confidence": 1.0, "evidence": str(error)}
            all_statuses.append(check_status)
            confidences.append(float(check["confidence"]))
            if check_status != "pass":
                base["findings"].append(_finding(str(frame_number), category, check))

    for from_frame, to_frame in expected_transitions:
        report = by_transition.get((from_frame, to_frame))
        if not isinstance(report, dict):
            check = {"status": "missing", "confidence": 1.0, "evidence": "No report for this transition."}
            for category in TRANSITION_CHECKS:
                base["findings"].append(_finding(f"{from_frame}->{to_frame}", category, check))
                all_statuses.append("missing")
            continue
        base["checked_transitions"].append(f"{from_frame}->{to_frame}")
        for category in TRANSITION_CHECKS:
            try:
                check_status = _status(report.get(category), f"transition {from_frame}->{to_frame}.{category}")
                check = dict(report[category])
                check["status"] = check_status
            except ValueError as error:
                check_status = "missing"
                check = {"status": "missing", "confidence": 1.0, "evidence": str(error)}
            all_statuses.append(check_status)
            confidences.append(float(check["confidence"]))
            if check_status != "pass":
                base["findings"].append(_finding(f"{from_frame}->{to_frame}", category, check))

    overall_confidence = float(vision_report.get("overall_confidence", 0))
    if not isinstance(vision_report.get("overall_confidence"), (int, float)) or not 0 <= overall_confidence <= 1:
        overall_confidence = 0.0
    base["overall_confidence"] = min([overall_confidence, *confidences], default=0.0)
    if "fail" in all_statuses:
        base["status"] = "fail"
    elif any(status in {"ambiguous", "missing"} for status in all_statuses):
        base["status"] = "manual_review"
    else:
        base["status"] = "pass"
    return base


def render_report(report: dict[str, Any]) -> str:
    """Render a compact human-readable QA report."""
    lines = [
        f"Storyboard QA: {report.get('status', 'manual_review').upper()}",
        f"Candidate: {report.get('candidate_image', 'unknown')}",
        f"Candidate SHA-256: {report.get('candidate_sha256') or 'unavailable'}",
        f"Contract: {report.get('contract_path') or 'embedded input'}",
        f"Overall confidence: {report.get('overall_confidence', 0):.2f}",
        "",
        "Findings:",
    ]
    findings = report.get("findings", [])
    if not findings:
        lines.append("- None")
    else:
        for finding in findings:
            lines.append(
                f"- [{finding['status']}] {finding['frame']} / {finding['category']}: "
                f"{finding['evidence']}"
            )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("candidate_image", type=Path)
    parser.add_argument("vision_report", type=Path)
    parser.add_argument("--contract-path", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    report = json.loads(args.vision_report.read_text(encoding="utf-8"))
    result = evaluate_report(spec, report, args.candidate_image, args.contract_path)
    rendered = json.dumps(result, indent=2) + "\n"
    if args.out:
        args.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
