import json
import subprocess
from pathlib import Path

REMOTION_PROJECT_DIR = Path("/Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/003_Remotion")
REMOTION_PUBLIC_DIR = REMOTION_PROJECT_DIR / "public"

def build_caption_props(background_video_file: str, captions: list[dict], fps: int = 24) -> dict:
    return {
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
