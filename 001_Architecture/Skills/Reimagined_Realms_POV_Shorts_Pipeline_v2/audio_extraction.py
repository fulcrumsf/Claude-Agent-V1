import subprocess
from pathlib import Path


def extract_audio(video_path: Path, output_path: Path) -> Path:
    """
    Extract audio from a video file and save as mp3.

    Args:
        video_path: Path to the input video file
        output_path: Path where the extracted audio mp3 should be saved

    Returns:
        The output_path as a Path object
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        ["ffmpeg", "-y", "-i", str(video_path), "-vn", "-c:a", "libmp3lame", str(output_path)],
        check=True, capture_output=True, text=True,
    )
    return output_path


def stitch_audio_files(audio_paths: list[Path], output_path: Path) -> Path:
    """
    Concatenate multiple audio files into a single track.

    Proactive hardening: raises ValueError if audio_paths is empty to prevent
    writing a filelist before validation, matching Task 1's fix pattern from
    concatenate_videos.

    Args:
        audio_paths: List of paths to audio files to concatenate
        output_path: Path where the stitched audio should be saved

    Returns:
        The output_path as a Path object

    Raises:
        ValueError: If audio_paths is empty
    """
    if not audio_paths:
        raise ValueError("audio_paths must not be empty")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Proactive hardening: unique filelist name per output to prevent collisions
    # when multiple calls target the same output directory (learned from Task 1)
    filelist_path = output_path.parent / f"_audio_concat_filelist_{output_path.stem}.txt"
    filelist_path.write_text("\n".join(f"file '{Path(p)}'" for p in audio_paths))

    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(filelist_path), "-c", "copy", str(output_path)],
        check=True, capture_output=True, text=True,
    )
    return output_path
