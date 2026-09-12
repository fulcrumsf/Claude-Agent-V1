#!/usr/bin/env python3
"""Build the corrected Neon Parcel review cut with a full-length audio bed."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLIPS = ROOT / "Video_Clips"
AUDIO = ROOT / "Narration_Audio/v1/narration"
WORKING = ROOT / "Assembly/Versions/v2"
CONCAT = WORKING / "clips.txt"
BASE = ROOT / "Assembly/Versions/v1/picture-and-original-audio.mp4"
OUTPUT = WORKING / "Neon-Parcel-Grandma-And-Bear-Compilation-VO-Review-v2.mp4"
REPORT = WORKING / "assembly-report.json"
CLIP_PATHS = [
    CLIPS / "Shot-01-1080p-v3.mp4", CLIPS / "Shot-02-1080p-v4.mp4",
    CLIPS / "Shot-03-1080p-v3.mp4", CLIPS / "Shot-04-1080p-v3.mp4",
    CLIPS / "Shot-05-1080p-v1.mp4", CLIPS / "Shot-06-1080p-v7.mp4",
    CLIPS / "Shot-07-1080p-v2.mp4", CLIPS / "Shot-08-1080p-v4.mp4",
    CLIPS / "Shot-09-1080p-v2.mp4", CLIPS / "Shot-10-1080p-v2.mp4",
    CLIPS / "Shot-11-1080p-v5.mp4", CLIPS / "Shot-12-1080p-v8.mp4",
]


def duration(path: Path) -> float:
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    WORKING.mkdir(parents=True, exist_ok=True)
    total = sum(duration(path) for path in CLIP_PATHS)
    starts, cursor = [], 0.0
    for path in CLIP_PATHS:
        starts.append(cursor)
        cursor += duration(path)
    voice_files = [AUDIO / f"scene_{index:02d}.mp3" for index in range(1, 14)]
    voice_durations = [duration(path) for path in voice_files]
    placements = [start + 0.35 for start in starts] + [max(0.0, starts[-1] + duration(CLIP_PATHS[-1]) - voice_durations[-1] - 0.25)]
    if any(voice_durations[index] >= duration(CLIP_PATHS[index]) for index in range(12)):
        raise RuntimeError("A narration line is not shorter than its associated clip")
    inputs = ["-i", str(BASE)]
    for path in voice_files:
        inputs += ["-i", str(path)]
    filters, delayed = [], []
    for index, delay in enumerate(placements, start=1):
        ms = round(delay * 1000)
        filters.append(f"[{index}:a]adelay={ms}|{ms},volume=1.25[vo{index}]")
        delayed.append(f"[vo{index}]")
    filters.append("".join(delayed) + f"amix=inputs={len(voice_files)}:duration=longest:dropout_transition=0:normalize=0[vo]")
    filters.append(f"[0:a]volume=0.65,apad=whole_dur={total:.3f},atrim=duration={total:.3f}[orig]")
    filters.append("[orig][vo]sidechaincompress=threshold=0.04:ratio=2.5:attack=25:release=450[ducked]")
    filters.append("[ducked][vo]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[aout]")
    command = ["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filters), "-map", "0:v:0", "-map", "[aout]", "-t", f"{total:.3f}", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(OUTPUT)]
    subprocess.run(command, check=True)
    REPORT.write_text(json.dumps({"version": "v2", "source_duration_s": round(total, 3), "voice_durations_s": [round(value, 3) for value in voice_durations], "voice_placements_s": [round(value, 3) for value in placements], "original_audio_preserved": True, "original_audio_padded_to_picture_length": True, "music_added": False, "status": "review_cut"}, indent=2) + "\n", encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
