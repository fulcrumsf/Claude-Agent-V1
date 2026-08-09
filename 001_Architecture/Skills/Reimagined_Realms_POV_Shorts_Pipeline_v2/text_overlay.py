import json
import subprocess
from pathlib import Path

REMOTION_PROJECT_DIR = Path("/Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/003_Remotion")
REMOTION_PUBLIC_DIR = REMOTION_PROJECT_DIR / "public"


def measure_video_duration_seconds(video_path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)],
        check=True, capture_output=True, text=True,
    )
    return float(result.stdout.strip())


def build_caption_props(
    background_video_file: str,
    captions: list[dict],
    fps: int = 24,
    duration_in_frames: int | None = None,
) -> dict:
    """duration_in_frames should be the actual background video's length in frames (round(seconds * fps)),
    passed through to the POVShort Composition's calculateMetadata in Root.tsx. Confirmed failure
    2026-08-09: the Composition's hardcoded default (1560 frames / 65.0s) silently truncated a
    65.785s render — every production's runtime differs, so this must always be supplied by the
    caller rather than left to that default. Use measure_video_duration_seconds() on the actual
    assembled Final_vN.mp4 to compute it, not the sum of caption durations (which could drift
    from the real file if a caption is ever written slightly short).
    """
    props = {
        "backgroundVideoFile": background_video_file,
        "captions": [
            {
                "text": c["text"],
                "startS": c["start_s"],
                "durationS": c["duration_s"],
                "variant": c["variant"],
            }
            for c in captions
        ],
    }
    if duration_in_frames is not None:
        props["durationInFrames"] = duration_in_frames
    return props


def write_props_file(props: dict, output_path: Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(props, indent=2))
    return output_path


def ensure_public_symlink(production_dir: Path, symlink_name: str) -> Path:
    production_dir = Path(production_dir)
    symlink_path = REMOTION_PUBLIC_DIR / symlink_name

    if not symlink_path.is_symlink():
        symlink_path.symlink_to(production_dir)

    return symlink_path


def render_text_overlay(props_path: Path, output_path: Path) -> Path:
    props_path = Path(props_path)
    output_path = Path(output_path)

    subprocess.run(
        ["npx", "remotion", "render", "POVShort", str(output_path), f"--props={props_path}", "--codec", "h264"],
        cwd=str(REMOTION_PROJECT_DIR),
        check=True, capture_output=True, text=True,
    )
    return output_path
