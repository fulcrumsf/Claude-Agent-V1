import subprocess
from pathlib import Path

def concatenate_videos(video_paths: list[Path], output_path: Path) -> Path:
    if not video_paths:
        raise ValueError("video_paths must not be empty")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    filelist_path = output_path.parent / f"_concat_filelist_{output_path.stem}.txt"
    filelist_path.write_text("\n".join(f"file '{Path(p)}'" for p in video_paths))

    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(filelist_path),
            "-map", "0:v:0", "-an", "-c:v", "copy", str(output_path),
        ],
        check=True, capture_output=True, text=True,
    )
    return output_path
