#!/usr/bin/env python3
"""
generate_narration_with_timestamps.py — Anomalous Wild narration generator.

Thin wrapper around the existing generate_voiceover_with_timestamps() —
does not duplicate ElevenLabs logic, just applies it per-scene for a
production and writes beat_sheet.json alongside each scene's audio.mp3.

Usage:
  python3 generate_narration_with_timestamps.py <production_folder> <voice_id>

Reads:
  <production_folder>/Scripts/Narration.md  (## SCENE_ID headers, narration text below each)

Writes:
  <production_folder>/Narration_Audio/<scene_id>.mp3
  <production_folder>/Narration_Audio/<scene_id>_beat_sheet.json
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, "/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools")
sys.path.insert(0, "/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Text-To-Speech")
from audio_tts import generate_voiceover_with_timestamps


def parse_narration_sections(md_text: str) -> dict[str, str]:
    """## scene_01 \n narration text... -> {"scene_01": "narration text..."}"""
    sections = {}
    matches = list(re.finditer(r"^##\s+(\S+)\s*$", md_text, re.MULTILINE))
    for i, m in enumerate(matches):
        scene_id = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md_text)
        sections[scene_id] = md_text[start:end].strip()
    return sections


def main():
    if len(sys.argv) < 3:
        sys.exit("Usage: generate_narration_with_timestamps.py <production_folder> <voice_id>")
    production_root = Path(sys.argv[1]).resolve()
    voice_id = sys.argv[2]

    narration_path = production_root / "Scripts" / "Narration.md"
    if not narration_path.exists():
        sys.exit(f"ERROR: {narration_path} not found")

    sections = parse_narration_sections(narration_path.read_text())
    out_dir = production_root / "Narration_Audio"
    out_dir.mkdir(parents=True, exist_ok=True)

    for scene_id, text in sections.items():
        if not text:
            print(f"  {scene_id}: no narration text, skipping")
            continue
        audio_path = out_dir / f"{scene_id}.mp3"
        print(f"  Generating {scene_id} ({len(text)} chars)...")
        _, words = generate_voiceover_with_timestamps(text, str(audio_path), voice_id)
        beat_sheet_path = out_dir / f"{scene_id}_beat_sheet.json"
        beat_sheet_path.write_text(json.dumps({"scene_id": scene_id, "words": words}, indent=2))
        print(f"    saved {audio_path.name} + {beat_sheet_path.name} ({len(words)} words)")


if __name__ == "__main__":
    main()
