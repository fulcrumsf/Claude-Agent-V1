#!/usr/bin/env python3
"""
compliance_vision_scan.py — Phase 3 post-build vision scan.

Reuses the exact keyframe-extraction approach already proven in
analyze_clips.py (same skill folder), pointed at FINISHED edit files instead
of raw clips, with a compliance-focused prompt (RULE-001/002/003 from
Compliance-Ledger.md: third-party logos, watermarks, brand marks).

Usage:
  python3 compliance_vision_scan.py <edit_video_path> <out_dir>
"""
import base64
import os
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import requests
except ImportError:
    print("Missing: pip install requests")
    sys.exit(1)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
MODEL = "qwen/qwen2.5-vl-72b-instruct"
SCENE_THRESHOLD = 0.35
MAX_FRAMES = 10

COMPLIANCE_PROMPT = (
    "You are checking a TikTok Shop affiliate video for policy compliance before it is posted.\n\n"
    "Look at every frame below and identify ANY of the following (per TikTok's Creator Campaign Terms "
    "and Best Practices for Promotional Content policies):\n"
    "1. Any third-party brand name, logo, trademark, or service mark (including partial, blurred, or "
    "background logos — e.g. a fast-food sign, a competitor product box, a clothing brand logo)\n"
    "2. Any platform watermark or sticker from another app (e.g. a screen-recording watermark)\n\n"
    "For each frame, state what you see. Then end your response with exactly one line: "
    "'VERDICT: FLAG' if any issue was found in any frame, or 'VERDICT: CLEAR' if none were found."
)


def parse_verdict(vision_response_text: str) -> str:
    for line in reversed(vision_response_text.strip().splitlines()):
        stripped = line.strip().upper()
        if stripped == "VERDICT: CLEAR":
            return "CLEAR"
        if stripped == "VERDICT: FLAG":
            return "FLAG"
    return "FLAG"  # fail safe: ambiguous response is treated as a flag


def extract_scene_keyframes(video_path: str, out_dir: str) -> list:
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
                timestamps.append(float(line.split("pts_time:")[1].split()[0]))
            except (IndexError, ValueError):
                pass
    if not timestamps or timestamps[0] > 0.5:
        timestamps.insert(0, 0.5)
    if len(timestamps) > MAX_FRAMES:
        step = len(timestamps) / MAX_FRAMES
        timestamps = [timestamps[int(i * step)] for i in range(MAX_FRAMES)]

    frames = []
    for i, ts in enumerate(timestamps):
        frame_path = os.path.join(out_dir, f"frame_{i:03d}_{ts:.2f}s.jpg")
        subprocess.run(
            ["ffmpeg", "-ss", str(ts), "-i", video_path, "-frames:v", "1", "-q:v", "3", frame_path, "-y"],
            capture_output=True
        )
        if os.path.exists(frame_path):
            frames.append((ts, frame_path))
    return frames


def encode_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def scan_video(video_path: Path, out_dir: Path) -> Path:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY not set. Run: source ~/.env-secrets")

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        frames = extract_scene_keyframes(str(video_path), tmp)
        content = [{"type": "text", "text": COMPLIANCE_PROMPT}]
        for ts, frame_path in frames:
            content.append({"type": "text", "text": f"\n[Frame at {ts:.2f}s]"})
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(frame_path)}"}})

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json",
                      "HTTP-Referer": "https://agent-os.local"},
            json={"model": MODEL, "messages": [{"role": "user", "content": content}], "max_tokens": 600},
            timeout=60,
        )
        response_text = response.json()["choices"][0]["message"]["content"]

    verdict = parse_verdict(response_text)
    report_path = out_dir / f"{Path(video_path).stem}-vision-scan.md"
    report_path.write_text(f"# Vision Scan — {Path(video_path).name}\n\n{response_text}\n\nVerdict: {verdict}\n")
    return report_path


def main():
    if len(sys.argv) < 3:
        sys.exit("Usage: compliance_vision_scan.py <edit_video_path> <out_dir>")
    report = scan_video(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"Vision scan report: {report}")


if __name__ == "__main__":
    main()
