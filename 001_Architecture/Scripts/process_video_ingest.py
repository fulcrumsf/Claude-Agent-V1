#!/usr/bin/env python3
import argparse
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def to_kebab_case(s):
    """Converts a filename to descriptive kebab-case."""
    name = os.path.splitext(s)[0]
    kebab = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    return kebab

def main():
    parser = argparse.ArgumentParser(description="Ingest a video, extract keyframes, and transcribe it.")
    parser.add_argument("input_video", help="Path to the input video file")
    args = parser.parse_args()

    input_path = Path(args.input_video).resolve()
    if not input_path.exists():
        print(f"Error: Input video '{input_path}' does not exist.")
        sys.exit(1)

    kebab_name = to_kebab_case(input_path.name)
    workspace_root = Path("/Users/tonymacbook2025/Documents/Agent-OS")
    resource_lib = workspace_root / "007_Resource_Library" / "Videos" / kebab_name
    
    # 1. Create Directories
    resource_lib.mkdir(parents=True, exist_ok=True)
    keyframes_dir = resource_lib / "Keyframes"
    keyframes_dir.mkdir(exist_ok=True)

    # 2. Move Video
    target_video_path = resource_lib / f"{kebab_name}{input_path.suffix.lower()}"
    if input_path != target_video_path:
        print(f"Moving video to {target_video_path}...")
        shutil.move(str(input_path), str(target_video_path))

    # 3. Extract Scene-Detected Keyframes via FFmpeg
    # select='gt(scene,0.3)' - filters frames that have a scene change probability > 0.3
    # vsync vfr - outputs variable frame rate (only the selected frames)
    print("Extracting scene keyframes using FFmpeg...")
    ffmpeg_cmd = [
        "ffmpeg", "-y", "-i", str(target_video_path),
        "-vf", "select='gt(scene,0.3)'",
        "-vsync", "vfr",
        str(keyframes_dir / "%03d.jpg")
    ]
    subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # If no keyframes were generated (i.e., a single static scene), just grab the first frame
    if not list(keyframes_dir.glob("*.jpg")):
        print("No scene changes detected. Extracting first frame...")
        ffmpeg_cmd_fallback = [
            "ffmpeg", "-y", "-i", str(target_video_path),
            "-vframes", "1",
            str(keyframes_dir / "001.jpg")
        ]
        subprocess.run(ffmpeg_cmd_fallback, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 4. Transcribe using Whisper
    print("Transcribing audio using Whisper...")
    # --model base is relatively fast. --output_format txt outputs a plain text transcript.
    whisper_cmd = [
        "whisper", str(target_video_path),
        "--model", "base",
        "--output_format", "txt",
        "--output_dir", str(resource_lib)
    ]
    subprocess.run(whisper_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Whisper creates the output based on the input filename
    txt_output = resource_lib / f"{target_video_path.stem}.txt"
    transcript_output = resource_lib / f"{kebab_name}-Transcript.md"
    
    today = datetime.now().strftime('%Y-%m-%d')

    if txt_output.exists():
        txt_content = txt_output.read_text()
        
        # Format it nicely with YAML frontmatter
        md_content = f"""---
title: "{input_path.stem} Transcript"
type: video-transcript
category: video-production
tags:
  - video-ingest
  - raw-transcript
created: {today}
---

# {input_path.stem} - Transcript

{txt_content}
"""
        transcript_output.write_text(md_content)
        txt_output.unlink() # Delete the original txt file
    else:
        print("Warning: Whisper transcription output not found.")

    # 5. Create empty Tutorial scaffold
    tutorial_scaffold = resource_lib / f"{kebab_name}-Tutorial.md"
    if not tutorial_scaffold.exists():
        tutorial_scaffold.write_text(f"""---
title: "{input_path.stem} Tutorial"
type: tutorial
category: video-production
tags:
  - video-tutorial
  - how-to
created: {today}
---

# {input_path.stem} Tutorial

## Summary
[Agent: Synthesize a summary based on the transcript here]

## Reference Keyframes
![[Keyframes/001.jpg]]

## Step-by-Step Breakdown
1. 
""")

    print(f"\\n✅ Video ingestion complete! Knowledge Package created at:\\n{resource_lib}")

if __name__ == "__main__":
    main()
