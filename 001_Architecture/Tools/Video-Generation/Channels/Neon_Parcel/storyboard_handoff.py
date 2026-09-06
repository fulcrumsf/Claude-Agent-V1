#!/usr/bin/env python3
"""Build and validate the selected storyboard handoff for Seedance."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from storyboard_contract import validate_spec
from storyboard_ensemble import load_policy


SECTION_ORDER = (
    "TONE:",
    "CAPTURE STYLE:",
    "CAMERA LOCK:",
    "SCENE CONTINUITY:",
    "ACTION TIMELINE:",
    "AUDIO:",
    "VISUAL REALISM:",
    "HARD CONSTRAINTS:",
)


def _sha256(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def _require_file(value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty path")
    path = Path(value)
    if not path.is_file():
        raise ValueError(f"{label} does not exist: {path}")
    return path


def validate_handoff(manifest: dict[str, Any]) -> dict[str, Any]:
    """Validate a selected passing storyboard manifest before prompt creation."""
    if not isinstance(manifest, dict):
        raise ValueError("handoff manifest must be an object")
    required = (
        "shot_id",
        "status",
        "selected_attempt",
        "active_storyboard_path",
        "contract_path",
        "qa_report_path",
        "attempt_state_path",
        "storyboard_reference_url",
        "reference_role",
    )
    missing = [field for field in required if field not in manifest]
    if missing:
        raise ValueError("handoff manifest missing required fields: " + ", ".join(missing))
    if manifest["status"] != "pass":
        raise ValueError("storyboard handoff requires status == pass")
    if not isinstance(manifest["selected_attempt"], int) or manifest["selected_attempt"] < 1:
        raise ValueError("selected_attempt must be a positive integer")
    if manifest["reference_role"] != "storyboard_reference":
        raise ValueError("storyboard reference role must be storyboard_reference")
    policy = load_policy(Path(manifest["review_policy_path"])) if manifest.get("review_policy_path") else load_policy()
    if policy["manual_review_required"] and manifest.get("manual_review_approved") is not True:
        raise ValueError("manual storyboard review approval is required before Seedance handoff")
    storyboard = _require_file(manifest["active_storyboard_path"], "active_storyboard_path")
    contract = _require_file(manifest["contract_path"], "contract_path")
    qa_report = _require_file(manifest["qa_report_path"], "qa_report_path")
    attempt_state = _require_file(manifest["attempt_state_path"], "attempt_state_path")
    if not isinstance(manifest["storyboard_reference_url"], str) or not manifest["storyboard_reference_url"].strip():
        raise ValueError("storyboard_reference_url must be a non-empty URL")
    if manifest.get("first_frame_url") and manifest.get("first_frame_url") == manifest["storyboard_reference_url"]:
        raise ValueError("storyboard reference cannot also be the temporal first frame")
    if manifest.get("storyboard_sha256") and manifest["storyboard_sha256"] != _sha256(storyboard):
        raise ValueError("storyboard_sha256 does not match active storyboard")
    if manifest.get("contract_sha256") and manifest["contract_sha256"] != _sha256(contract):
        raise ValueError("contract_sha256 does not match contract file")
    if manifest.get("qa_report_sha256") and manifest["qa_report_sha256"] != _sha256(qa_report):
        raise ValueError("qa_report_sha256 does not match QA report")
    try:
        qa_value = json.loads(qa_report.read_text(encoding="utf-8"))
        state_value = json.loads(attempt_state.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"handoff evidence JSON is invalid: {error}") from error
    if not isinstance(qa_value, dict) or qa_value.get("status") != "pass":
        raise ValueError("qa_report_path must contain a passing QA report")
    events = state_value.get("events") if isinstance(state_value, dict) else None
    selected = [
        event for event in events or []
        if isinstance(event, dict)
        and event.get("event") == "selected"
        and event.get("attempt") == manifest["selected_attempt"]
    ]
    if not selected:
        raise ValueError("attempt_state_path does not record the selected attempt")
    return manifest


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value.strip()))


def _action_timeline(spec: dict[str, Any]) -> list[str]:
    beats = []
    for index, frame in enumerate(spec["frames"], start=1):
        cause = frame.get("transition_from_previous", "Initial visible state established by the opening panel.")
        result = "; ".join(frame["object_states"])
        beats.append(
            f"Shot 1, panel {index}: {frame['action']} Physical cause: {cause} Observable result: {result}."
        )
    return beats


def _reference_order(manifest: dict[str, Any]) -> list[str]:
    """Render provider reference tags from the exact upload order."""
    references = manifest.get("reference_order")
    if not references:
        return ["@Image 1 = the first uploaded image, the approved storyboard sheet."]
    if not isinstance(references, list):
        raise ValueError("reference_order must be a list")
    lines = []
    for index, reference in enumerate(references, start=1):
        if not isinstance(reference, dict):
            raise ValueError("each reference_order entry must be an object")
        if reference.get("upload_index", index) != index:
            raise ValueError("reference_order upload_index must match list order")
        role = str(reference.get("role", "")).strip()
        if not role:
            raise ValueError("reference_order entries require a role")
        lines.append(f"@Image {index} = the {role}, uploaded in position {index}.")
    return lines


def build_seedance_prompt(spec: dict[str, Any], qa_report: dict[str, Any], manifest: dict[str, Any]) -> str:
    """Build the Seedance prompt only from a validated passing handoff."""
    validate_spec(spec)
    validate_handoff(manifest)
    if not isinstance(qa_report, dict) or qa_report.get("status") != "pass":
        raise ValueError("QA report must have status == pass before prompt construction")

    subjects = _unique(
        subject
        for frame in spec["frames"]
        for subject in frame["visible_subjects"]
    )
    object_states = _unique(
        state
        for frame in spec["frames"]
        for state in frame["object_states"]
    )
    spatial = _unique(
        relation
        for frame in spec["frames"]
        for relation in frame["spatial_relationships"]
    )
    duration = spec.get("duration_s") or manifest.get("duration_s") or "the approved shot duration"
    lines = [
        f"Shots: 1 | Duration: {duration} seconds | Aspect Ratio: 16:9",
        "",
        "REFERENCE ORDER:",
        *_reference_order(manifest),
        "",
        "Follow this storyboard @Image 1 to create one continuous shot. Animate the panels in chronological order as one uninterrupted video, not as separate cuts or a reproduced storyboard layout.",
        "",
        SECTION_ORDER[0],
        spec["tone"],
        "",
        SECTION_ORDER[1],
        spec["capture_style"],
        "",
        SECTION_ORDER[2],
        spec["camera_lock"],
        "",
        SECTION_ORDER[3],
        f"Validated scene intent: {spec['overall_summary']}",
        "Subjects and continuity: " + "; ".join(subjects) + ".",
        "Validated object states: " + "; ".join(object_states) + ".",
        "Validated spatial relationships: " + "; ".join(spatial) + ".",
        "",
        SECTION_ORDER[4],
    ]
    lines.extend(_action_timeline(spec))
    lines.extend(
        [
            "",
            SECTION_ORDER[5],
            spec["audio_policy"],
            "Audio exclusions: " + "; ".join(spec["audio_exclusions"]) + ".",
            "",
            SECTION_ORDER[6],
            spec["visual_realism"],
            "",
            SECTION_ORDER[7],
        ]
    )
    lines.extend(f"- {constraint}" for constraint in spec["hard_constraints"])
    lines.extend(
        [
            "- Follow the approved storyboard sequence through @Image 1; do not reproduce its panels, captions, borders, grid, or sheet layout in the video.",
            "- Preserve the validated subject count, object states, camera geometry, and chronological action.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_and_save_prompt(
    spec: dict[str, Any], qa_report: dict[str, Any], manifest: dict[str, Any], output_path: Path
) -> Path:
    """Persist the exact handoff prompt before any provider submission."""
    prompt = build_seedance_prompt(spec, qa_report, manifest)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(prompt, encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("qa_report", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    prompt = build_and_save_prompt(
        json.loads(args.spec.read_text(encoding="utf-8")),
        json.loads(args.qa_report.read_text(encoding="utf-8")),
        json.loads(args.manifest.read_text(encoding="utf-8")),
        args.out,
    )
    print(prompt)


if __name__ == "__main__":
    main()
