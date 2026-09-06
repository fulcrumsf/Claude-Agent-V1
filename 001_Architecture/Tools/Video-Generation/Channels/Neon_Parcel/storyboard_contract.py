#!/usr/bin/env python3
"""Validate and render structured Neon Parcel storyboard specifications."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_TOP_LEVEL = (
    "shot_id",
    "overall_summary",
    "tone",
    "capture_style",
    "visual_style",
    "visual_realism",
    "audio_policy",
    "audio_exclusions",
    "camera_lock",
    "continuity_invariants",
    "frames",
    "panel_convention",
    "hard_constraints",
)
REQUIRED_FRAME_FIELDS = (
    "frame",
    "visible_subjects",
    "object_states",
    "spatial_relationships",
    "action",
    "caption",
)


def _require_text(value: Any, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")


def _require_list(value: Any, label: str) -> None:
    if not isinstance(value, list) or not value or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise ValueError(f"{label} must be a non-empty list of non-empty strings")


def validate_spec(spec: dict[str, Any]) -> dict[str, Any]:
    """Validate one storyboard spec and return it unchanged for downstream use."""
    if not isinstance(spec, dict):
        raise ValueError("storyboard spec must be a JSON object")

    missing = [field for field in REQUIRED_TOP_LEVEL if field not in spec]
    if missing:
        raise ValueError("missing required storyboard fields: " + ", ".join(missing))

    for field in REQUIRED_TOP_LEVEL:
        if field in {"continuity_invariants", "hard_constraints", "audio_exclusions"}:
            _require_list(spec[field], field)
        elif field != "frames":
            _require_text(spec[field], field)

    frames = spec["frames"]
    if not isinstance(frames, list) or not frames:
        raise ValueError("frames must be a non-empty list")

    expected_numbers = list(range(1, len(frames) + 1))
    actual_numbers = []
    for index, frame in enumerate(frames):
        if not isinstance(frame, dict):
            raise ValueError(f"frames[{index}] must be an object")
        missing_frame = [field for field in REQUIRED_FRAME_FIELDS if field not in frame]
        if missing_frame:
            raise ValueError(
                f"frame {index + 1} missing required fields: " + ", ".join(missing_frame)
            )
        number = frame["frame"]
        if not isinstance(number, int):
            raise ValueError(f"frame {index + 1} number must be an integer")
        actual_numbers.append(number)
        for field in REQUIRED_FRAME_FIELDS:
            if field in {"visible_subjects", "object_states", "spatial_relationships"}:
                _require_list(frame[field], f"frame {number}.{field}")
            elif field != "frame":
                _require_text(frame[field], f"frame {number}.{field}")

        if index == 0 and frame.get("transition_from_previous"):
            raise ValueError("frame 1 cannot claim a transition from a previous frame")
        if "transition_from_previous" in frame:
            _require_text(frame["transition_from_previous"], f"frame {number}.transition_from_previous")

    if actual_numbers != expected_numbers:
        raise ValueError(
            f"frames must be consecutively numbered from 1; got {actual_numbers}"
        )
    return spec


def render_prompt(spec: dict[str, Any]) -> str:
    """Render a stable storyboard prompt from a validated specification."""
    validate_spec(spec)
    lines = [
        "Create a planning storyboard sheet for the shot below.",
        "Do not invent a different prompt structure. Follow every numbered frame literally.",
        "",
        "OVERALL SUMMARY:",
        spec["overall_summary"],
        "",
        "TONE:",
        spec["tone"],
        "",
        "CAPTURE STYLE:",
        spec["capture_style"],
        "",
        "VISUAL STYLE:",
        spec["visual_style"],
        "",
        "VISUAL REALISM:",
        spec["visual_realism"],
        "",
        "AUDIO POLICY:",
        spec["audio_policy"],
        "Audio exclusions: " + "; ".join(spec["audio_exclusions"]) + ".",
        "",
        "CAMERA LOCK:",
        spec["camera_lock"],
        "",
        "CONTINUITY INVARIANTS:",
    ]
    lines.extend(f"- {item}" for item in spec["continuity_invariants"])
    lines.extend(["", "FRAME-BY-FRAME STORYBOARD SEQUENCE:"])

    for frame in spec["frames"]:
        lines.extend(
            [
                f"FRAME {frame['frame']}:",
                f"Visible subjects: {'; '.join(frame['visible_subjects'])}.",
                f"Object states: {'; '.join(frame['object_states'])}.",
                f"Spatial relationships: {'; '.join(frame['spatial_relationships'])}.",
                f"Action/state: {frame['action']}",
                f"Caption (render this exact text in the caption band): {frame['caption']}",
            ]
        )
        if frame.get("transition_from_previous"):
            lines.append(f"Transition from previous frame: {frame['transition_from_previous']}")
        lines.append("")

    lines.extend(["PANEL CONVENTION:", spec["panel_convention"], "", "HARD CONSTRAINTS:"])
    lines.extend(f"- {item}" for item in spec["hard_constraints"])
    lines.extend(
        [
            "",
            "Before finishing, check every panel against its frame number, visible subjects, object state, action, and exact caption.",
            "This is a storyboard reference image only, not a video frame and not a clean temporal first frame.",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    rendered = render_prompt(spec) + "\n"
    if args.out:
        args.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
