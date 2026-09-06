#!/usr/bin/env python3
"""Decide whether a Seedance 1.5 shot needs an end-frame image."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REQUIRED_FOR_END_FRAME = (
    "materially_different_state",
    "stable_camera_geometry",
    "consistent_subject_count",
    "clear_endpoint",
)


def decide(shot: dict[str, Any]) -> dict[str, Any]:
    shot_id = shot.get("shot_id", shot.get("id"))
    if shot.get("route") != "seedance_1_5_start_end":
        return {"shot_id": shot_id, "decision": "not_applicable", "reason": "shot is not routed to Seedance 1.5"}
    evidence = shot.get("endpoint_assessment")
    if not isinstance(evidence, dict):
        return {"shot_id": shot_id, "decision": "manual_review", "reason": "structured endpoint assessment is missing"}
    explicit = evidence.get("decision")
    if explicit in {"start_frame_only", "manual_review"}:
        return {"shot_id": shot_id, "decision": explicit, "reason": evidence.get("reason", "explicit endpoint decision")}
    missing = [field for field in REQUIRED_FOR_END_FRAME if evidence.get(field) is not True]
    if missing:
        return {"shot_id": shot_id, "decision": "start_frame_only", "reason": "end frame is not justified; missing or negative evidence: " + ", ".join(missing), "missing_evidence": missing}
    return {"shot_id": shot_id, "decision": "use_end_frame", "reason": "endpoint is materially different, stable, count-consistent, and clear", "missing_evidence": []}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    document = json.loads(args.input.read_text(encoding="utf-8"))
    shots = document.get("shots") if isinstance(document, dict) else document
    if not isinstance(shots, list):
        shots = [document]
    rendered = json.dumps({"decisions": [decide(shot) for shot in shots]}, indent=2) + "\n"
    if args.out:
        args.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
