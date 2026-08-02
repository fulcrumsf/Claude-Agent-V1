import subprocess
from pathlib import Path

SEEDANCE_MODEL = "bytedance/seedance-v1.5-pro/image-to-video"


def generate_video(
    image_url: str,
    video_prompt: str,
    output_path: Path,
    duration: int = 5,
    resolution: str = "1080p",
    aspect_ratio: str = "9:16",
) -> Path:
    output_path = Path(output_path)

    cmd = [
        "wavespeed", "run", SEEDANCE_MODEL,
        "-i", f"image={image_url}",
        "-i", f"prompt={video_prompt}",
        "-i", f"duration={duration}",
        "-i", f"resolution={resolution}",
        "-i", f"aspect_ratio={aspect_ratio}",
        "-i", "generate_audio=true",
        "--download", str(output_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)

    if not output_path.exists():
        candidates = sorted(output_path.parent.glob(f"{output_path.stem}-*{output_path.suffix}"))
        if not candidates:
            raise FileNotFoundError(
                f"No output found at {output_path} or as a numbered candidate after wavespeed run"
            )
        candidates[0].rename(output_path)
        for extra in candidates[1:]:
            extra.unlink()

    return output_path


def main(image_url: str, prompt: str, out: str, duration: int = 5, resolution: str = "1080p", aspect_ratio: str = "9:16") -> None:
    generate_video(image_url, prompt, Path(out), duration, resolution, aspect_ratio)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate a POV scene video clip via Seedance 1.5 Pro (native audio).")
    parser.add_argument("image_url", help="Public URL of the reference image")
    parser.add_argument("prompt", help="Video prompt (must already include the negative-prompt closer)")
    parser.add_argument("--out", required=True, help="Output video file path")
    parser.add_argument("--duration", type=int, default=5)
    parser.add_argument("--resolution", default="1080p", choices=["480p", "720p", "1080p"])
    parser.add_argument("--aspect_ratio", default="9:16")
    args = parser.parse_args()
    main(args.image_url, args.prompt, args.out, args.duration, args.resolution, args.aspect_ratio)
