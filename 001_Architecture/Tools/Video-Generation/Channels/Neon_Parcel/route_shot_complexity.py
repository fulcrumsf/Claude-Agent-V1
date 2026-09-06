#!/usr/bin/env python3
"""Route Neon Parcel shots to the least-complex suitable video workflow.

This is a conservative, explainable pre-generation check. It does not call a
video provider or approve paid generation. Human overrides are preserved in
the input and echoed in the result.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


DIMENSIONS = (
    "action_count",
    "physics",
    "object_continuity",
    "precision",
    "character_interaction",
    "spatial_continuity",
    "timing_precision",
    "dialogue_sync",
    "failure_risk",
    "storyboard_value",
)

COMPLEX_PATTERNS = {
    "physics": (
        r"\b(buckle|seat ?belt|catch|fall|break|spill|pour|balance|swing|throw|land|impact|pull|push)\b",
    ),
    "object_continuity": (
        r"\b(hand(?:s|ing)?|grab(?:s|bed)?|pick(?:s|ed)? up|insert|attach|remove|transfer|slide|carry|pass)\b",
    ),
    "precision": (
        r"\b( buckle|latch|receiver|lock|unlock|turn|press|open|close|aim|thread|wrap)\b",
    ),
    "character_interaction": (
        r"\b(between|while .* (?:talks|holds|films)|hands? .* to|pulls? .* away|chases?|attacks?|rescues?)\b",
    ),
    "spatial_continuity": (
        r"\b(then|afterward|returns?|walks? back|enters?|exits?|through the|across the|inside|outside)\b",
    ),
    "timing_precision": (
        r"\b(immediately|at the same time|before|after|in sequence|in order|exactly|sync(?:hronized)?)\b",
    ),
    "dialogue_sync": (
        r"\b(says?|shouts?|yells?|calls? out|dialogue|speaks?|voice)\b",
    ),
}

HARD_COMPLEX_PATTERNS = (
    r"\b(buckle|seat ?belt|catch|caught|latch|insert|break(?:s|ing)?|pour(?:s|ing)?|spill(?:s|ing)?)\b",
    r"\b(three|four|five|six|seven|eight|nine|ten)\s+(?:ordered\s+)?(?:actions?|steps?|beats?)\b",
)


def _text(shot: dict[str, Any]) -> str:
    fields = ("description", "action", "prompt", "dialogue", "notes")
    return " ".join(str(shot.get(field, "")) for field in fields).strip().lower()


def _score_dimension(dimension: str, text: str, shot: dict[str, Any]) -> int:
    """Return 0 (low), 1 (moderate), or 2 (high) complexity."""
    assessment = shot.get("semantic_assessment")
    if not isinstance(assessment, dict):
        assessment = shot.get("complexity")
    explicit = assessment.get(dimension) if isinstance(assessment, dict) else None
    if explicit is not None:
        return max(0, min(2, int(explicit)))

    matches = sum(bool(re.search(pattern, text)) for pattern in COMPLEX_PATTERNS.get(dimension, ()))
    if dimension == "action_count":
        action_text = shot.get("description", shot.get("action", ""))
        verbs = re.findall(r"\b(?:opens?|closes?|pulls?|pushes?|grabs?|hands?|walks?|runs?|turns?|catches?|drops?|says?|looks?|reaches?|buckles?)\b", str(action_text).lower())
        return 2 if len(verbs) >= 4 else 1 if len(verbs) >= 2 else 0
    if dimension == "storyboard_value":
        return 2 if matches >= 2 else 1 if matches else 0
    return 2 if matches >= 2 else 1 if matches else 0


def route_shot(shot: dict[str, Any]) -> dict[str, Any]:
    """Classify one shot and return an auditable routing decision."""
    text = _text(shot)
    scores = {dimension: _score_dimension(dimension, text, shot) for dimension in DIMENSIONS}
    total = sum(scores.values())
    hard_flags = [pattern for pattern in HARD_COMPLEX_PATTERNS if re.search(pattern, text)]
    has_semantic_assessment = isinstance(shot.get("semantic_assessment"), dict)

    override = shot.get("route_override")
    if override in {"force_simple", "force_complex"}:
        route = "seedance_1_5_start_end" if override == "force_simple" else "seedance_2_mini_storyboard"
        status = "overridden"
    elif not has_semantic_assessment:
        route = "manual_review"
        status = "semantic_assessment_required"
    elif hard_flags or total >= 8:
        route = "seedance_2_mini_storyboard"
        status = "auto"
    elif total <= 4:
        route = "seedance_1_5_start_end"
        status = "auto"
    else:
        route = "manual_review"
        status = "review_required"

    reasons = [dimension.replace("_", " ") for dimension, score in scores.items() if score == 2]
    if not has_semantic_assessment:
        reasons = ["structured semantic assessment is missing; keyword signals are advisory only"]
    elif hard_flags:
        reasons.append("hard physics/ordered-action trigger")
    if not reasons:
        reasons.append("low interaction and continuity burden")

    return {
        "shot_id": shot.get("shot_id", shot.get("id")),
        "route": route,
        "status": status,
        "complexity_score": total,
        "complexity_scale": "0-20",
        "dimension_scores": scores,
        "reasons": reasons,
        "hard_triggered": bool(hard_flags),
        "assessment_source": "semantic_assessment" if has_semantic_assessment else "keyword_advisory_only",
        "human_override": override,
        "generation_policy": {
            "seedance_1_5_start_end": "Use start and end frames; preserve natural duration.",
            "seedance_2_mini_storyboard": "Use the storyboard for planning and QA only; do not send a composite storyboard sheet to Kie until a provider adapter is verified. Use approved clean temporal frames for video conditioning.",
            "manual_review": "Do not generate automatically; ask for a human route decision or clarify the shot.",
        }[route],
    }


def route_document(document: Any) -> Any:
    if isinstance(document, list):
        return {"shots": [route_shot(shot) for shot in document]}
    if isinstance(document, dict) and "shots" in document:
        return {**document, "routing": [route_shot(shot) for shot in document["shots"]]}
    if isinstance(document, dict):
        return route_shot(document)
    raise ValueError("Input must be a shot object, a list of shots, or an object with a 'shots' list")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON shot object, list, or document with a shots list")
    parser.add_argument("--out", type=Path, help="Optional JSON output path; defaults to stdout")
    args = parser.parse_args()
    result = route_document(json.loads(args.input.read_text(encoding="utf-8")))
    rendered = json.dumps(result, indent=2) + "\n"
    if args.out:
        args.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
