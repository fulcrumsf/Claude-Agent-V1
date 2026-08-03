import json
from pathlib import Path

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
