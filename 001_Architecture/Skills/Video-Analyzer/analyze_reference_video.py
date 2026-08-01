# analyze_reference_video.py
import argparse
import subprocess
from pathlib import Path

def download_video(url: str, out_dir: Path) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    video_path = out_dir / "Video.mp4"
    subprocess.run(
        ["yt-dlp", "-f", "mp4", "-o", str(video_path), url],
        check=True, capture_output=True,
    )
    return video_path
