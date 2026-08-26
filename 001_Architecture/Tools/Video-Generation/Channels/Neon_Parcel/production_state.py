#!/usr/bin/env python3
"""Record explicit Neon Parcel production checkpoints without overwriting history."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


STATES = {
    "scaffolded",
    "candidates_pending",
    "reference_selected",
    "shot_list_pending",
    "clip_1_pending",
    "clips_2_5_pending",
    "batch_release_pending",
    "rough_cut_pending",
    "narration_pending",
    "package_pending",
    "final_approval_pending",
    "publish_ready",
    "published",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _state_path(root: Path) -> Path:
    return root / "Data" / "Checkpoint_State.json"


def _log_path(root: Path) -> Path:
    return root / "Data" / "History" / "Decision_Log.jsonl"


def record_state(root: Path, state: str, note: str, actor: str = "Tony") -> dict:
    """Write the latest checkpoint and append the human decision that caused it."""
    root = Path(root).resolve()
    if state not in STATES:
        raise ValueError(f"Unknown state: {state}")
    if not note.strip():
        raise ValueError("A decision note is required")

    state_path = _state_path(root)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    current = {"state": "scaffolded", "updated_at": None, "actor": None}
    if state_path.exists():
        current.update(json.loads(state_path.read_text(encoding="utf-8")))

    event = {
        "timestamp": _now(),
        "from_state": current.get("state"),
        "to_state": state,
        "actor": actor,
        "note": note.strip(),
    }
    state_path.write_text(
        json.dumps(
            {"state": state, "updated_at": event["timestamp"], "actor": actor},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    log_path = _log_path(root)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event) + "\n")
    return event


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("production_folder", type=Path)
    parser.add_argument("state", choices=sorted(STATES))
    parser.add_argument("--note", required=True)
    parser.add_argument("--actor", default="Tony")
    args = parser.parse_args()
    event = record_state(args.production_folder, args.state, args.note, args.actor)
    print(json.dumps(event, indent=2))


if __name__ == "__main__":
    main()
