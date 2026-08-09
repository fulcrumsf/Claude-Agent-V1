import argparse
import json
import subprocess
from pathlib import Path
from foley_config import FOLEY_MODEL, FOLEY_MODELS

def upload_video(video_path: Path) -> str:
    result = subprocess.run(
        ["wavespeed", "upload", str(video_path), "--json"],
        check=True, capture_output=True, text=True,
    )
    return json.loads(result.stdout)["url"]


def generate_foley(video_path: Path, output_path: Path, prompt: str = "", model: str | None = None) -> Path:
    model_id = FOLEY_MODELS[model or FOLEY_MODEL]
    video_url = upload_video(video_path)

    cmd = ["wavespeed", "run", model_id, "-i", f"video={video_url}"]
    if prompt:
        cmd += ["-i", f"prompt={prompt}"]
    cmd += ["--download", str(output_path)]

    subprocess.run(cmd, check=True, capture_output=True, text=True)

    if not output_path.exists():
        # Some models (e.g. Mirelo) return multiple candidate outputs; wavespeed
        # then suffixes the filename with "-{index}" instead of writing the exact
        # path requested. Take the first candidate and normalize it to output_path.
        candidates = sorted(output_path.parent.glob(f"{output_path.stem}-*{output_path.suffix}"))
        if not candidates:
            raise FileNotFoundError(f"wavespeed did not produce expected output at {output_path}")
        candidates[0].rename(output_path)
        for extra in candidates[1:]:
            extra.unlink()

    return output_path


def main(video: str, out: str, prompt: str = "", model: str | None = None) -> None:
    generate_foley(Path(video), Path(out), prompt, model)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate synced Foley/SFX audio for a video clip via a swappable model (Mirelo or Sonilo)."
    )
    parser.add_argument("video", help="Path to local video clip")
    parser.add_argument("--out", required=True, help="Output audio file path")
    parser.add_argument("--prompt", default="", help="Optional text hint guiding the sound effect generation")
    parser.add_argument(
        "--model", choices=["mirelo", "sonilo"], default=None,
        help="Override the default FOLEY_MODEL (from foley_config.py) for this single call",
    )
    args = parser.parse_args()
    main(args.video, args.out, args.prompt, args.model)
