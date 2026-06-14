#!/usr/bin/env python3
"""
Analyze video clips for editorial decisions.
Extracts scene-change keyframes via FFmpeg, then sends them to Qwen-VL
via OpenRouter to get timestamped visual descriptions.

Usage:
    python analyze_clips.py <folder_with_clips>
    python analyze_clips.py .  (run from the drop folder)

Output:
    clip_analysis.md — timestamped visual breakdown of every clip
"""

import os
import sys
import json
import base64
import subprocess
import tempfile
from pathlib import Path

try:
    import requests
except ImportError:
    print("Missing: pip install requests")
    sys.exit(1)

# ── Config ────────────────────────────────────────────────────────────────────

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
MODEL = "qwen/qwen2.5-vl-72b-instruct"  # cheap, strong vision
SCENE_THRESHOLD = 0.35   # lower = more sensitive to scene changes (0.2–0.5)
MAX_FRAMES_PER_CLIP = 10  # cap to control cost

VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4a", ".MOV", ".MP4"}

# ── Helpers ───────────────────────────────────────────────────────────────────

def get_duration(video_path: str) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", video_path],
        capture_output=True, text=True
    )
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 0.0


def extract_scene_keyframes(video_path: str, out_dir: str) -> list[tuple[float, str]]:
    """Extract frames at scene changes. Returns list of (timestamp, frame_path)."""
    # Pass 1: detect scene change timestamps
    detect_result = subprocess.run(
        ["ffmpeg", "-i", video_path,
         "-vf", f"select='gt(scene,{SCENE_THRESHOLD})',showinfo",
         "-vsync", "vfr", "-f", "null", "-"],
        capture_output=True, text=True
    )

    timestamps = []
    for line in detect_result.stderr.splitlines():
        if "pts_time:" in line:
            try:
                pts_time = float(line.split("pts_time:")[1].split()[0])
                timestamps.append(pts_time)
            except (IndexError, ValueError):
                pass

    # Always include first frame
    if not timestamps or timestamps[0] > 0.5:
        timestamps.insert(0, 0.5)

    # Cap frames
    if len(timestamps) > MAX_FRAMES_PER_CLIP:
        step = len(timestamps) / MAX_FRAMES_PER_CLIP
        timestamps = [timestamps[int(i * step)] for i in range(MAX_FRAMES_PER_CLIP)]

    # Pass 2: extract the actual frames
    frames = []
    for i, ts in enumerate(timestamps):
        frame_path = os.path.join(out_dir, f"frame_{i:03d}_{ts:.2f}s.jpg")
        subprocess.run(
            ["ffmpeg", "-ss", str(ts), "-i", video_path,
             "-frames:v", "1", "-q:v", "3", frame_path, "-y"],
            capture_output=True
        )
        if os.path.exists(frame_path):
            frames.append((ts, frame_path))

    return frames


def encode_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def analyze_frames(clip_name: str, frames: list[tuple[float, str]], duration: float) -> str:
    """Send frames to Qwen-VL via OpenRouter and get editorial description."""
    if not OPENROUTER_API_KEY:
        return "ERROR: OPENROUTER_API_KEY not set. Run: source ~/.env-secrets"

    content = [
        {
            "type": "text",
            "text": (
                f"You are helping an editor choose the best segments of a product demo video "
                f"for a 15-second TikTok Shop affiliate clip.\n\n"
                f"Clip: {clip_name} (total duration: {duration:.1f}s)\n"
                f"Below are {len(frames)} keyframes extracted at scene changes.\n\n"
                f"For each frame, briefly describe:\n"
                f"1. What the product is doing or being shown\n"
                f"2. Shot type (close-up, medium, wide, overhead, etc.)\n"
                f"3. Visual quality (sharp/blurry, good/poor lighting, clean/cluttered background)\n"
                f"4. Whether this moment is high-impact for a viewer seeing the product for the first time\n\n"
                f"End with a 2-3 sentence EDITORIAL SUMMARY recommending the best 8-12 second window "
                f"to use from this clip and why."
            )
        }
    ]

    for ts, frame_path in frames:
        content.append({
            "type": "text",
            "text": f"\n[Frame at {ts:.2f}s]"
        })
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{encode_image(frame_path)}"
            }
        })

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://agent-os.local",
        },
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": content}],
            "max_tokens": 600,
        },
        timeout=60
    )

    if response.status_code != 200:
        return f"ERROR {response.status_code}: {response.text[:200]}"

    return response.json()["choices"][0]["message"]["content"]


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else "."
    folder = Path(folder).resolve()

    if not OPENROUTER_API_KEY:
        print("ERROR: OPENROUTER_API_KEY not set.")
        print("Run: source ~/.env-secrets && python analyze_clips.py <folder>")
        sys.exit(1)

    video_clips = sorted([
        f for f in folder.iterdir()
        if f.suffix in VIDEO_EXTENSIONS and f.is_file()
    ])

    if not video_clips:
        print(f"No video clips found in {folder}")
        sys.exit(1)

    print(f"Found {len(video_clips)} clip(s). Analyzing...\n")

    output_lines = ["# Clip Analysis\n", f"Folder: `{folder}`\n\n---\n"]

    with tempfile.TemporaryDirectory() as tmp:
        for clip in video_clips:
            print(f"  Extracting keyframes: {clip.name}")
            duration = get_duration(str(clip))
            frames = extract_scene_keyframes(str(clip), tmp)

            if not frames:
                print(f"  Warning: no scene changes detected in {clip.name}, using fixed intervals")
                # Fallback: sample at fixed intervals
                n = min(6, max(1, int(duration / 5)))
                for i in range(n):
                    ts = (duration / n) * i + 0.5
                    frame_path = os.path.join(tmp, f"frame_fixed_{i:03d}.jpg")
                    subprocess.run(
                        ["ffmpeg", "-ss", str(ts), "-i", str(clip),
                         "-frames:v", "1", "-q:v", "3", frame_path, "-y"],
                        capture_output=True
                    )
                    if os.path.exists(frame_path):
                        frames.append((ts, frame_path))

            print(f"  Sending {len(frames)} frames to Qwen-VL...")
            analysis = analyze_frames(clip.name, frames, duration)

            output_lines.append(f"## {clip.name}  ({duration:.1f}s)\n")
            output_lines.append(f"Keyframes analyzed: {len(frames)}\n\n")
            output_lines.append(analysis)
            output_lines.append("\n\n---\n")
            print(f"  Done: {clip.name}\n")

    out_path = folder / "clip_analysis.md"
    out_path.write_text("\n".join(output_lines))
    print(f"Analysis saved to: {out_path}")


if __name__ == "__main__":
    main()
