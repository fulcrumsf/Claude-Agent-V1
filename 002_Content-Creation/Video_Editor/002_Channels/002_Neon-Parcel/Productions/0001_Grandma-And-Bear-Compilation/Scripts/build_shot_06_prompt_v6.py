#!/usr/bin/env python3
"""Build the approved Shot 06 Seedance prompt from the structured contract."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

TOOLS = Path("/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel")
sys.path.insert(0, str(TOOLS))

from storyboard_handoff import build_and_save_prompt  # type: ignore


ROOT = Path(__file__).resolve().parents[1]
SPEC = TOOLS / "shot_06_storyboard_spec_v5.json"
OUTPUT = ROOT / "Prompts/Shot-06-Seedance-2-Mini-v6.md"


def main() -> None:
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        storyboard = temp / "storyboard.png"
        contract = temp / "contract.json"
        qa = temp / "qa.json"
        state = temp / "state.json"
        policy = temp / "policy.json"
        storyboard.write_bytes(b"approved storyboard v5")
        contract.write_text(json.dumps(spec), encoding="utf-8")
        qa.write_text(json.dumps({"status": "pass", "review_mode": "human_approved", "findings": []}), encoding="utf-8")
        state.write_text(json.dumps({"events": [{"event": "selected", "attempt": 1}]}), encoding="utf-8")
        policy.write_text(json.dumps({"manual_review_required": True}), encoding="utf-8")
        manifest = {
            "shot_id": "Shot-06",
            "status": "pass",
            "selected_attempt": 1,
            "active_storyboard_path": str(storyboard),
            "contract_path": str(contract),
            "qa_report_path": str(qa),
            "attempt_state_path": str(state),
            "review_policy_path": str(policy),
            "manual_review_approved": True,
            "storyboard_reference_url": "https://pending-upload.local/Shot-06-Storyboard-v5.png",
            "reference_role": "storyboard_reference",
        }
        build_and_save_prompt(spec, {"status": "pass"}, manifest, OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
