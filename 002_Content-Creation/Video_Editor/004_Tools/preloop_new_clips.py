"""
Creates video_looped.mp4 for any new clip folder that has video.mp4 but not video_looped.mp4.
New clips are 8s AI-generated clips — no actual looping needed, just a clean re-encode
with fast-seek keyframes so Remotion OffthreadVideo can seek into them accurately.

Usage:
  python3 004_Tools/preloop_new_clips.py [base_dir]
  python3 004_Tools/preloop_new_clips.py 002_Channels/001_Anomalous-Wild/001_Bioluminescence-Weapon/

Reads new_clips_prompts.json from base_dir to know which folders are "new" clips.
Skips folders that already have video_looped.mp4.
"""

import subprocess
import sys
import json
from pathlib import Path

BASE_DEFAULT = Path("002_Channels/001_Anomalous-Wild/001_Bioluminescence-Weapon")


def get_duration(path: Path) -> float:
    """Return duration in seconds via ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True
    )
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 8.0  # fallback


def preloop(src: Path, dst: Path, duration: float):
    """Re-encode src → dst trimmed to duration with clean keyframes."""
    # -stream_loop 1 ensures we never run short even if clip is slightly under 8s
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "1",
        "-i", str(src),
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-an",
        str(dst),
        "-loglevel", "error",
    ]
    result = subprocess.run(cmd)
    return result.returncode == 0


def main():
    base = Path(sys.argv[1]) if len(sys.argv) > 1 else BASE_DEFAULT
    prompts_file = base / "new_clips_prompts.json"

    if not prompts_file.exists():
        print(f"ERROR: {prompts_file} not found")
        sys.exit(1)

    entries = json.loads(prompts_file.read_text())
    video_entries = [e for e in entries if e.get("generation_type") == "video"]

    print(f"=== Preloop New Clips ===")
    print(f"Base: {base}")
    print(f"New clip entries: {len(video_entries)}")
    print()

    done, skipped, missing, failed = 0, 0, 0, 0

    for entry in video_entries:
        folder = Path(entry["output_folder"])
        src    = folder / "video.mp4"
        dst    = folder / "video_looped.mp4"

        if dst.exists():
            print(f"  ✓ {entry['scene_id']} — already exists")
            skipped += 1
            continue

        if not src.exists():
            print(f"  ✗ {entry['scene_id']} — video.mp4 not yet generated, skipping")
            missing += 1
            continue

        duration = get_duration(src)
        print(f"  → {entry['scene_id']} — encoding {duration:.1f}s clip...")

        ok = preloop(src, dst, duration)
        if ok and dst.exists():
            size_mb = dst.stat().st_size / (1024 * 1024)
            print(f"  ✓ {entry['scene_id']} — {dst.name} ({size_mb:.1f} MB)")
            done += 1
        else:
            print(f"  ✗ {entry['scene_id']} — ffmpeg failed")
            failed += 1

    print()
    print(f"=== Done ===")
    print(f"Created : {done}")
    print(f"Skipped : {skipped}")
    print(f"Missing : {missing} (not yet generated)")
    print(f"Failed  : {failed}")


if __name__ == "__main__":
    main()
