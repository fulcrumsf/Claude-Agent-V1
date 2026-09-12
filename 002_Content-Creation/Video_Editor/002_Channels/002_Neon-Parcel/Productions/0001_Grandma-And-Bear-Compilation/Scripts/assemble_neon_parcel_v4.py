#!/usr/bin/env python3
"""Build a sync-safe Neon Parcel narration review cut."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLIPS = ROOT / "Video_Clips"
AUDIO = ROOT / "Narration_Audio/v1/narration"
WORKING = ROOT / "Assembly/Versions/v4"
OUTPUT = WORKING / "Neon-Parcel-Grandma-And-Bear-Compilation-VO-Review-v4.mp4"
CLIP_PATHS = [CLIPS / name for name in [
    "Shot-01-1080p-v3.mp4", "Shot-02-1080p-v4.mp4", "Shot-03-1080p-v3.mp4",
    "Shot-04-1080p-v3.mp4", "Shot-05-1080p-v1.mp4", "Shot-06-1080p-v7.mp4",
    "Shot-07-1080p-v2.mp4", "Shot-08-1080p-v4.mp4", "Shot-09-1080p-v2.mp4",
    "Shot-10-1080p-v2.mp4", "Shot-11-1080p-v5.mp4", "Shot-12-1080p-v8.mp4",
]]


def probe(path: Path, entries: str) -> str:
    result = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", entries, "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True)
    return result.stdout.strip()


def duration(path: Path) -> float:
    return float(probe(path, "format=duration"))


def has_audio(path: Path) -> bool:
    result = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=index", "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True)
    return bool(result.stdout.strip())


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    WORKING.mkdir(parents=True, exist_ok=True)
    clip_durations = [duration(path) for path in CLIP_PATHS]
    total = sum(clip_durations)
    starts, cursor = [], 0.0
    for clip_duration in clip_durations:
        starts.append(cursor)
        cursor += clip_duration
    voice_files = [AUDIO / f"scene_{index:02d}.mp3" for index in range(1, 14)]
    voice_durations = [duration(path) for path in voice_files]
    placements = [start + 0.35 for start in starts] + [starts[-1] + clip_durations[-1] - voice_durations[-1] - 0.25]
    if any(voice_durations[index] >= clip_durations[index] for index in range(12)):
        raise RuntimeError("A narration line is not shorter than its associated clip")

    inputs = []
    filters = []
    concat_labels = []
    for index, (path, clip_duration) in enumerate(zip(CLIP_PATHS, clip_durations)):
        inputs += ["-i", str(path)]
        filters.append(f"[{index}:v]setpts=PTS-STARTPTS,fps=24,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1[v{index}]")
        if has_audio(path):
            filters.append(f"[{index}:a]aresample=48000:async=1:first_pts=0,apad,atrim=duration={clip_duration:.3f},asetpts=PTS-STARTPTS[a{index}]")
        else:
            filters.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={clip_duration:.3f},asetpts=PTS-STARTPTS[a{index}]")
        concat_labels += [f"[v{index}]", f"[a{index}]"]
    filters.append("".join(concat_labels) + f"concat=n={len(CLIP_PATHS)}:v=1:a=1[basev][basea]")

    for index, (path, delay) in enumerate(zip(voice_files, placements), start=len(CLIP_PATHS)):
        inputs += ["-i", str(path)]
        ms = round(delay * 1000)
        filters.append(f"[{index}:a]aresample=48000:async=1,adelay={ms}|{ms},volume=1.6[vo{index}]")
    voice_labels = "".join(f"[vo{index}]" for index in range(len(CLIP_PATHS), len(CLIP_PATHS) + len(voice_files)))
    filters.append(voice_labels + f"amix=inputs={len(voice_files)}:duration=longest:dropout_transition=0:normalize=0[vox]")
    filters.append("[basea]volume=0.55[orig]")
    filters.append("[orig][vox]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,atrim=duration=" + f"{total:.3f}[aout]")

    command = ["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filters), "-map", "[basev]", "-map", "[aout]", "-t", f"{total:.3f}", "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k", "-movflags", "+faststart", str(OUTPUT)]
    subprocess.run(command, check=True)
    (WORKING / "assembly-report.json").write_text(json.dumps({"version": "v4", "source_duration_s": round(total, 3), "source_clip_count": len(CLIP_PATHS), "clips_without_audio": [path.name for path in CLIP_PATHS if not has_audio(path)], "voice_durations_s": [round(value, 3) for value in voice_durations], "voice_placements_s": [round(value, 3) for value in placements], "original_audio_preserved": True, "audio_sample_rate": 48000, "timestamp_safe_concat": True, "music_added": False, "status": "review_cut"}, indent=2) + "\n", encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
