import re
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


def measure_lufs(audio_path: Path) -> float:
    result = subprocess.run(
        ["ffmpeg", "-i", str(audio_path), "-af", "loudnorm=I=-16:LRA=11:TP=-1.5:print_format=json", "-f", "null", "-"],
        check=True, capture_output=True, text=True,
    )
    match = re.search(r'"input_i"\s*:\s*"(-?[\d.]+)"', result.stderr)
    if match is None:
        raise RuntimeError(
            "measure_lufs: failed to parse 'input_i' from ffmpeg loudnorm output. "
            f"ffmpeg exited successfully but its stderr did not contain the expected "
            f"loudnorm JSON field. stderr excerpt: {result.stderr[:500]!r}"
        )
    return float(match.group(1))


def calculate_gain(measured_lufs: float, target_lufs: float) -> float:
    gain_db = target_lufs - measured_lufs
    return 10 ** (gain_db / 20)


def mix_and_normalize(foley_path: Path, music_path: Path, output_path: Path, target_lufs: float = -14.0) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    foley_lufs = measure_lufs(foley_path)
    music_lufs = measure_lufs(music_path)

    foley_gain = calculate_gain(foley_lufs, target_lufs)
    music_gain = calculate_gain(music_lufs, target_lufs - 9.0)  # music sits ~9dB under foley, per the style guide's sound-design bed convention

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(foley_path), "-i", str(music_path),
            "-filter_complex",
            f"[0:a]volume={foley_gain}[a0];[1:a]volume={music_gain}[a1];[a0][a1]amix=inputs=2:duration=longest[aout]",
            "-map", "[aout]", str(output_path),
        ],
        check=True, capture_output=True, text=True,
    )
    return output_path


def get_next_version(production_dir: Path) -> int:
    production_dir = Path(production_dir)
    existing = list(production_dir.glob("Final_v*.mp4"))
    if not existing:
        return 1

    versions = []
    for path in existing:
        match = re.search(r"Final_v(\d+)\.mp4", path.name)
        if match:
            versions.append(int(match.group(1)))

    return max(versions, default=0) + 1


def mux_final(video_path: Path, audio_path: Path, production_dir: Path) -> Path:
    production_dir = Path(production_dir)
    version = get_next_version(production_dir)
    output_path = production_dir / f"Final_v{version}.mp4"

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(video_path), "-i", str(audio_path),
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "copy", "-c:a", "aac", "-shortest",
            str(output_path),
        ],
        check=True, capture_output=True, text=True,
    )
    return output_path
