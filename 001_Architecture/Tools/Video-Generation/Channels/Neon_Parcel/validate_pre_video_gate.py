#!/usr/bin/env python3
"""Validate Neon Parcel evidence before a paid video generation request."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from storyboard_handoff import validate_handoff


GATES = (
    "visual_realism",
    "camera_plausibility",
    "meaningful_visual_beat",
    "humor_context",
)
OVERLAY_TERMS = ("caption", "title card", "overlay", "watermark", "emoji", "ranking")
NEGATIVE_SCOPE_MARKERS = ("no ", "not ", "never ", "without ", "don't ", "do not ")


def _contains_positive_overlay_instruction(prompt_text: str) -> bool:
    """Ignore overlay terms when they occur only in an explicit exclusion."""
    for sentence in re.split(r"[.!?\n]+", prompt_text.lower()):
        for term in OVERLAY_TERMS:
            position = sentence.find(term)
            if position >= 0 and not any(marker in sentence[:position] for marker in NEGATIVE_SCOPE_MARKERS):
                return True
    return False


def _validate_reference_routing(shot: dict[str, Any], failures: list[str]) -> None:
    """Reject storyboard-as-frame mistakes before any provider call."""
    first_frame = shot.get("first_frame_url")
    references = shot.get("reference_image_urls")
    if first_frame and references:
        failures.append("reference_routing:first_frame_and_reference_images_are_mutually_exclusive")
    if isinstance(first_frame, str) and any(token in first_frame.lower() for token in ("storyboard", "story-board", "contact-sheet")):
        failures.append("reference_routing:storyboard_must_not_be_first_frame")
    if references is not None and (not isinstance(references, list) or not references or any(not item for item in references)):
        failures.append("reference_routing:reference_image_urls_invalid")


def _validate_storyboard_handoff(shot: dict[str, Any], failures: list[str]) -> None:
    """Require a selected passing storyboard before the Mini storyboard route."""
    manifest_value = shot.get("storyboard_handoff_manifest")
    if not manifest_value:
        failures.append("storyboard_handoff:manifest_missing")
        return
    manifest_path = Path(str(manifest_value))
    if not manifest_path.is_file():
        failures.append("storyboard_handoff:manifest_missing")
        return
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        validate_handoff(manifest)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        failures.append(f"storyboard_handoff:invalid:{error}")
        return
    references = shot.get("reference_image_urls") or []
    if manifest.get("storyboard_reference_url") not in references:
        failures.append("storyboard_handoff:reference_url_mismatch")


def _status(value: Any) -> str | None:
    if isinstance(value, str):
        return value.lower()
    if isinstance(value, dict):
        candidate = value.get("status")
        return candidate.lower() if isinstance(candidate, str) else None
    return None


def validate_shot(shot: dict[str, Any]) -> dict[str, Any]:
    """Return an auditable result; never calls a provider."""
    failures: list[str] = []
    evidence: dict[str, str | None] = {}
    _validate_reference_routing(shot, failures)
    for gate in GATES:
        value = _status(shot.get(gate))
        evidence[gate] = value
        if value != "pass":
            failures.append(f"{gate}:{value or 'missing'}")

    prompt_file = shot.get("prompt_file")
    if not prompt_file or not Path(str(prompt_file)).is_file():
        failures.append("prompt_file:missing")

    prompt_text = str(shot.get("generation_prompt", "")).lower()
    if _contains_positive_overlay_instruction(prompt_text):
        failures.append("prompt_scope:post-production overlay content detected")

    route = shot.get("route")
    postprocess = shot.get("postprocess", {})
    if route == "seedance_1_5_start_end":
        if postprocess.get("topaz"):
            failures.append("route:seedance_1_5_1080p_must_bypass_topaz")
        if shot.get("output_resolution") not in (None, "1920x1080", [1920, 1080]):
            failures.append("route:seedance_1_5_output_must_be_1920x1080")
    elif route == "seedance_2_mini_storyboard":
        _validate_storyboard_handoff(shot, failures)
        if not shot.get("reference_image_urls"):
            failures.append("reference_routing:mini_storyboard_reference_missing")
        if shot.get("reference_role") == "storyboard_sheet" and shot.get("provider_verified_storyboard_sheet") is not True:
            failures.append("provider_contract:composite_storyboard_sheet_not_verified_for_video")
        if shot.get("generation_resolution") != "480p":
            failures.append("route:mini_generation_must_be_480p")
        if postprocess.get("topaz_factor") != "2x":
            failures.append("route:mini_requires_topaz_2x")
        if postprocess.get("final_normalization") != "1920x1080":
            failures.append("route:mini_requires_ffmpeg_1920x1080")
    elif route == "seedance_2_mini_first_last":
        if not shot.get("first_frame_url"):
            failures.append("temporal_routing:first_frame_missing")
        if not shot.get("last_frame_url"):
            failures.append("temporal_routing:last_frame_missing")
        if shot.get("reference_image_urls"):
            failures.append("temporal_routing:reference_images_forbidden")
        if shot.get("generation_resolution") != "480p":
            failures.append("route:mini_generation_must_be_480p")
        if postprocess.get("topaz") or postprocess.get("topaz_factor"):
            failures.append("route:manual_review_blocks_upscale")

    return {
        "shot_id": shot.get("shot_id", shot.get("id")),
        "ready_for_paid_generation": not failures,
        "gate_evidence": evidence,
        "failures": failures,
    }


def validate_document(document: Any) -> dict[str, Any]:
    shots = document.get("shots") if isinstance(document, dict) else document
    if not isinstance(shots, list):
        raise ValueError("Input must be a shot object list or an object with a 'shots' list")
    results = [validate_shot(shot) for shot in shots]
    return {
        "ready_for_paid_generation": all(item["ready_for_paid_generation"] for item in results),
        "shots": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = validate_document(json.loads(args.input.read_text(encoding="utf-8")))
    rendered = json.dumps(result, indent=2) + "\n"
    if args.out:
        args.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    if not result["ready_for_paid_generation"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
