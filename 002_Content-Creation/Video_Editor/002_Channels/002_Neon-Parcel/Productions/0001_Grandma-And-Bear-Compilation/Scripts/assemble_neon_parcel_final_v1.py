#!/usr/bin/env python3
"""Build the first Neon Parcel music and end-screen review master."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLIPS = ROOT / "Video_Clips"
ENDSCREEN = ROOT / "../../../../002_Channels/002_Neon-Parcel/Assets/Neon_Parcel_Endscreen_Horizontal_1080.mp4"
# Resolve from the production root because the end screen belongs to the channel.
ENDSCREEN = Path("/Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/002_Channels/002_Neon-Parcel/Assets/Neon_Parcel_Endscreen_Horizontal_1080.mp4")
AUDIO = ROOT / "Narration_Audio/v1/narration"
CTA = ROOT / "Narration_Audio/v1/cta/narration/scene_14.mp3"
MUSIC = ROOT / "Audio_Stems/Neon-Parcel-Comical-Quirky-Instrumental-v1.mp3"
WORKING = ROOT / "Assembly/Versions/v5"
OUTPUT = WORKING / "Neon-Parcel-Grandma-And-Bear-Compilation-Music-Endscreen-Review-v1.mp4"
CLIP_PATHS = [CLIPS / name for name in [
    "Shot-01-1080p-v3.mp4", "Shot-02-1080p-v4.mp4", "Shot-03-1080p-v3.mp4",
    "Shot-04-1080p-v3.mp4", "Shot-05-1080p-v1.mp4", "Shot-06-1080p-v7.mp4",
    "Shot-07-1080p-v2.mp4", "Shot-08-1080p-v4.mp4", "Shot-09-1080p-v2.mp4",
    "Shot-10-1080p-v2.mp4", "Shot-11-1080p-v5.mp4", "Shot-12-1080p-v8.mp4",
]] + [ENDSCREEN]


def probe(path: Path, entries: str, select: str = "v:0") -> str:
    result = subprocess.run(["ffprobe", "-v", "error", "-select_streams", select, "-show_entries", entries, "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True)
    return result.stdout.strip()


def duration(path: Path) -> float:
    return float(probe(path, "format=duration", "v:0"))


def has_audio(path: Path) -> bool:
    return bool(probe(path, "stream=index", "a:0"))


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    if any(not path.is_file() for path in CLIP_PATHS + [MUSIC, CTA]):
        raise FileNotFoundError([str(path) for path in CLIP_PATHS + [MUSIC, CTA] if not path.is_file()])
    WORKING.mkdir(parents=True, exist_ok=True)
    clip_durations = [duration(path) for path in CLIP_PATHS]
    total = sum(clip_durations)
    starts, cursor = [], 0.0
    for clip_duration in clip_durations:
        starts.append(cursor)
        cursor += clip_duration
    voice_files = [AUDIO / f"scene_{index:02d}.mp3" for index in range(1, 14)] + [CTA]
    voice_durations = [duration(path) for path in voice_files]
    placements = [start + 0.35 for start in starts[:12]] + [starts[11] + clip_durations[11] - voice_durations[12] - 0.25, starts[12] + 0.5]
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
    voice_start = len(CLIP_PATHS)
    for index, (path, delay) in enumerate(zip(voice_files, placements), start=voice_start):
        inputs += ["-i", str(path)]
        ms = round(delay * 1000)
        filters.append(f"[{index}:a]aresample=48000:async=1,adelay={ms}|{ms},volume=1.6[vo{index}]")
    voice_labels = "".join(f"[vo{index}]" for index in range(voice_start, voice_start + len(voice_files)))
    filters.append(voice_labels + f"amix=inputs={len(voice_files)}:duration=longest:dropout_transition=0:normalize=0[vox]")
    inputs += ["-i", str(MUSIC)]
    music_index = voice_start + len(voice_files)
    filters.append(f"[{music_index}:a]aresample=48000,volume=0.12,aloop=loop=-1:size=2147483647,atrim=duration={total:.3f}[music]")
    filters.append("[basea]volume=0.55[orig]")
    filters.append("[orig][vox][music]amix=inputs=3:duration=first:dropout_transition=0:normalize=0,atrim=duration=" + f"{total:.3f}[aout]")
    command = ["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filters), "-map", "[basev]", "-map", "[aout]", "-t", f"{total:.3f}", "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k", "-movflags", "+faststart", str(OUTPUT)]
    subprocess.run(command, check=True)
    (WORKING / "assembly-report.json").write_text(json.dumps({"version": "music-end-screen-review-v1", "source_duration_s": round(total, 3), "end_screen_duration_s": round(clip_durations[-1], 3), "voice_durations_s": [round(value, 3) for value in voice_durations], "voice_placements_s": [round(value, 3) for value in placements], "music_file": str(MUSIC), "music_volume": 0.12, "original_audio_volume": 0.55, "narration_volume": 1.6, "audio_sample_rate": 48000, "status": "review_cut"}, indent=2) + "\n", encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
