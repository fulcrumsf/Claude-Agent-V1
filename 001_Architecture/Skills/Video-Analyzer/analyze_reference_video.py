# analyze_reference_video.py
import argparse
import re
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

def detect_scenes(video_path: Path, threshold: float = 0.3) -> list[tuple[float, float]]:
    duration_result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)],
        check=True, capture_output=True, text=True,
    )
    duration = float(duration_result.stdout.strip())

    scene_result = subprocess.run(
        ["ffmpeg", "-i", str(video_path), "-filter:v",
         f"select='gt(scene,{threshold})',showinfo", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    cut_points = [float(m) for m in re.findall(r"pts_time:([\d.]+)", scene_result.stderr)]

    boundaries = [0.0] + sorted(cut_points) + [duration]
    return [(boundaries[i], boundaries[i + 1]) for i in range(len(boundaries) - 1)]
