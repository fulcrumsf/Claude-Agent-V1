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
