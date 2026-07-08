#!/usr/bin/env python3
"""
build_beat_table.py — Anomalous Wild beat table builder.

Universal narration chunking (same principle as Reimagined Realms), plus:
  - 8-second max clip length, but ONLY for beats already routed to live-footage
    generation (same reasoning as RR: generation model limits + engagement pacing)
  - No length cap for diagram/data-viz beats, but a hard "no static frame >
    3-5 seconds" rule attached as metadata for the assembly step to honor

Usage (called by the orchestrator, not run standalone in production):
  python3 build_beat_table.py <production_folder>
Reads:
  Narration_Audio/*_beat_sheet.json (per-scene word timestamps)
  Production/Scene_Routing.json (scene_id -> routing decision from Tool-Manager)
Writes:
  Production/Beat_Table.json
"""
import json
import sys
from pathlib import Path

LIVE_FOOTAGE_MAX_CLIP_S = 8.0
DIAGRAM_MAX_STATIC_S = 5.0


def build_beat_table(scenes: list[dict]) -> list[dict]:
    """scenes: [{"scene_id": str, "words": [{"word","start_s","end_s"}], "routing": str}]"""
    beats = []
    for scene in scenes:
        words = scene["words"]
        if not words:
            continue
        start_s = words[0]["start_s"]
        end_s = words[-1]["end_s"]
        routing = scene["routing"]
        beat = {
            "scene_id": scene["scene_id"],
            "start_s": start_s,
            "end_s": end_s,
            "routing": routing,
            "max_clip_s": LIVE_FOOTAGE_MAX_CLIP_S if routing == "live_footage" else None,
            "max_static_s": None if routing == "live_footage" else DIAGRAM_MAX_STATIC_S,
        }
        beats.append(beat)
    return beats


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: build_beat_table.py <production_folder>")
    production_root = Path(sys.argv[1]).resolve()

    routing_path = production_root / "Production" / "Scene_Routing.json"
    if not routing_path.exists():
        sys.exit(f"ERROR: {routing_path} not found — run Tool-Manager routing first")
    routing = json.loads(routing_path.read_text())  # {"scene_01": "live_footage", ...}

    narration_dir = production_root / "Narration_Audio"
    scenes = []
    for beat_sheet_path in sorted(narration_dir.glob("*_beat_sheet.json")):
        data = json.loads(beat_sheet_path.read_text())
        scene_id = data["scene_id"]
        if scene_id not in routing:
            sys.exit(f"ERROR: no routing decision for {scene_id} in Scene_Routing.json")
        scenes.append({"scene_id": scene_id, "words": data["words"], "routing": routing[scene_id]})

    beats = build_beat_table(scenes)
    out_path = production_root / "Production" / "Beat_Table.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"beats": beats}, indent=2))
    print(f"Wrote {out_path} — {len(beats)} beats")


if __name__ == "__main__":
    main()
