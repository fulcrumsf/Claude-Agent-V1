#!/usr/bin/env python3
"""
gemini_scene_analysis.py — Second-by-second video analysis for audio stem design.

Uploads a local video to Google Files API, runs Gemini analysis focused on
visual content per second so an audio composer can design stems with precise
fade-in/fade-out timing.

Usage:
  python3 gemini_scene_analysis.py <video_path> [--output <output.md>] [--model <model>]

Output:
  Markdown file with timestamped scene descriptions, suitable for audio stem mapping.
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

from google import genai

PROMPT = """
You are analyzing this video to help an audio composer design sound stems for it.

Provide a **second-by-second scene description** of the full video. For every second
(or whenever the visual content changes significantly), describe:

1. **What is in frame** — subjects, objects, environment
2. **People/crowd** — how many, what they are doing, density (sparse/moderate/dense)
3. **Animals or vehicles** — type, count, movement (e.g., 2 horses walking, cart rolling)
4. **Camera movement** — static / pan / dolly / aerial / tilt
5. **Emotional tone** — calm / tense / chaotic / mournful / dramatic
6. **Natural sounds present** — what sounds would realistically come from this scene
   (e.g., footsteps on cobblestone, crowd murmur, wind, rumble, horse hooves, cart wheels)

Format your response as a timestamped list:

**[0:00–0:03]**
- In frame: ...
- People: ...
- Camera: ...
- Tone: ...
- Natural sounds: ...

**[0:03–0:07]**
- In frame: ...
...

Be specific and granular. The composer needs to know exactly when to fade in crowd
sounds vs. silence, when horses enter/exit frame, when the visual shifts from calm
street life to eruption chaos. Do not summarize — describe every distinct visual moment.

At the end, provide a **Stem Map Summary** listing each recommended audio stem layer
with its approximate start time, end time, and fade behavior:

## Stem Map Summary
| Stem | Description | In | Out | Fade In | Fade Out |
|------|-------------|-----|-----|---------|----------|
| ... | ... | 0:00 | 0:45 | 2s | 3s |
"""


def load_api_key():
    result = subprocess.run(
        "source ~/.env-secrets && echo $GEMINI_API_KEY",
        shell=True, executable="/bin/zsh", capture_output=True, text=True
    )
    key = result.stdout.strip()
    if key:
        os.environ["GEMINI_API_KEY"] = key
    return os.environ.get("GEMINI_API_KEY", "")


def upload_video(client, video_path: Path):
    print(f"Uploading {video_path.name} to Google Files API...")
    print(f"  File size: {video_path.stat().st_size / 1_000_000:.1f} MB")

    video_file = client.files.upload(file=str(video_path))
    print(f"  Upload complete — URI: {video_file.uri}")

    # Wait for file to be processed
    print("  Waiting for processing...", end="", flush=True)
    while video_file.state.name == "PROCESSING":
        time.sleep(5)
        video_file = client.files.get(name=video_file.name)
        print(".", end="", flush=True)
    print()

    if video_file.state.name == "FAILED":
        raise RuntimeError(f"File processing failed: {video_file.state}")

    print(f"  Ready — state: {video_file.state.name}")
    return video_file


def analyze(video_path: Path, model: str, output_path: Path):
    api_key = load_api_key()
    if not api_key:
        sys.exit("ERROR: GEMINI_API_KEY not found in ~/.env-secrets")

    client = genai.Client(api_key=api_key)

    video_file = upload_video(client, video_path)

    print(f"\nSending to Gemini ({model}) for scene analysis...")
    print("This may take 1–3 minutes for a 2.5-minute video...")

    response = client.models.generate_content(
        model=model,
        contents=[video_file, PROMPT],
    )

    result = response.text
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result)
    print(f"\n✓ Analysis saved → {output_path}")
    print(f"  {len(result.splitlines())} lines, {len(result)} characters")

    # Clean up uploaded file
    client.files.delete(name=video_file.name)
    print("  Temp file deleted from Google Files API")

    return result


def main():
    parser = argparse.ArgumentParser(description="Second-by-second Gemini video analysis for audio stem design")
    parser.add_argument("video_path", help="Path to local video file")
    parser.add_argument("--output", help="Output markdown file path (default: <video_dir>/gemini_scene_analysis.md)")
    parser.add_argument("--model", default="gemini-2.5-pro", help="Gemini model to use (default: gemini-2.5-pro)")
    args = parser.parse_args()

    video_path = Path(args.video_path).resolve()
    if not video_path.exists():
        sys.exit(f"ERROR: Video not found: {video_path}")

    output_path = Path(args.output).resolve() if args.output else video_path.parent / "gemini_scene_analysis.md"

    analyze(video_path, args.model, output_path)


if __name__ == "__main__":
    main()
