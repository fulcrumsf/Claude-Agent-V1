#!/usr/bin/env python3
"""Create a non-destructive Neon Parcel long-form production scaffold."""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path


CHANNEL_ROOT = Path(
    "/Users/tonymacbook2025/Documents/Agent-OS/"
    "002_Content-Creation/Video_Editor/002_Channels/002_Neon-Parcel"
)
END_SCREEN_HORIZONTAL = CHANNEL_ROOT / "Assets" / "Neon_Parcel_Endscreen_Horizontal_1080.mp4"
PRODUCTIONS_ROOT = CHANNEL_ROOT / "Productions"

FOLDERS = (
    "References",
    "Research",
    "Scripts",
    "Prompts",
    "Production",
    "Images",
    "Video_Clips",
    "Video_Clips/Archived",
    "Working",
    "Intermediate",
    "Narration_Audio",
    "Audio_Stems",
    "Assembly/Versions",
    "Shorts/Versions",
    "Package",
    "Data/Checkpoints",
    "Data/History",
)


def _write_if_missing(path: Path, content: str) -> None:
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def _numbered_production_root(requested_root: Path) -> Path:
    """Assign the next four-digit production number unless one was supplied."""
    requested_root = Path(requested_root).resolve()
    if re.match(r"^\d{4}_", requested_root.name):
        return requested_root

    productions_root = requested_root.parent
    existing_numbers = []
    for child in productions_root.iterdir() if productions_root.exists() else ():
        match = re.match(r"^(\d{4})_", child.name)
        if match:
            existing_numbers.append(int(match.group(1)))
    next_number = max(existing_numbers, default=0) + 1
    return productions_root / f"{next_number:04d}_{requested_root.name}"


def scaffold(production_root: Path) -> Path:
    production_root = _numbered_production_root(production_root)
    production_root.mkdir(parents=True, exist_ok=True)

    for relative in FOLDERS:
        (production_root / relative).mkdir(parents=True, exist_ok=True)

    manifest = {
        "pipeline": "neonparcel-reference-inspired-compilation",
        "version": "0.1",
        "status": "scaffolded",
        "created": date.today().isoformat(),
        "production_root": str(production_root),
        "long_form": {"target_duration_minutes": [6, 8], "aspect_ratio": "16:9"},
        "shorts": {
            "target_duration_seconds": 60,
            "target_is_soft": True,
            "max_duration_seconds": None,
            "overlay_frames": [1, 30],
            "aspect_ratio": "9:16",
        },
        "approval_policy": {
            "first_clip": "human_required",
            "first_five_clips": "human_required",
            "remaining_batch": "human_release_required",
            "final_package": "human_required",
            "blotato_publish": "human_required",
        },
    }
    _write_if_missing(
        production_root / "Data" / "Production_Manifest.json",
        json.dumps(manifest, indent=2) + "\n",
    )
    _write_if_missing(
        production_root / "Data" / "Generation_Log.json",
        json.dumps({"production": production_root.name, "pipeline": manifest["pipeline"], "assets": []}, indent=2) + "\n",
    )
    _write_if_missing(
        production_root / "Data" / "Checkpoint_State.json",
        json.dumps({"state": "scaffolded", "updated_at": None, "actor": None}, indent=2) + "\n",
    )
    _write_if_missing(production_root / "Data" / "History" / "Decision_Log.jsonl", "")
    _write_if_missing(
        production_root / "Data" / "Report_Card.json",
        json.dumps({"production": production_root.name, "grade": None, "reviews": [], "autonomy_readiness": None}, indent=2) + "\n",
    )
    _write_if_missing(
        production_root / "Data" / "Report_Card.md",
        """---\ntitle: \"Neon Parcel Production Report Card\"\ntype: report\ndomain: video-production\ntags: [report, neon-parcel, video-production]\n---\n\n# Neon Parcel Production Report Card\n\n**Production:**\n**Grade:**\n**Autonomy readiness:**\n**Review date:**\n\n## Critique Notes\n\n## Revisions\n\n## Final Approval\n\n**Blotato published:** No\n""",
    )
    _write_if_missing(
        production_root / "Production" / "end_screen_reference.txt",
        str(END_SCREEN_HORIZONTAL) + "\n",
    )
    return production_root


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: scaffold_new_production.py <production_folder>")
    root = scaffold(Path(sys.argv[1]))
    print(f"Scaffolded Neon Parcel production at {root}")


if __name__ == "__main__":
    main()
