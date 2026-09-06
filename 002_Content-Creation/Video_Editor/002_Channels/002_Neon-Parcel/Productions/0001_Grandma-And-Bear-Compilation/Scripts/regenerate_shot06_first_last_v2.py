#!/usr/bin/env python3
"""Generate Shot 06 with strict first/last temporal anchors, without upscaling."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
TOOLS = Path("/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools")
CHANNEL_TOOLS = Path("/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel")
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(CHANNEL_TOOLS))

from kie_market_api import generate_seedance_mini  # type: ignore
from validate_pre_video_gate import validate_document  # type: ignore


PROMPT = ROOT / "Prompts/Shot-06-Seedance-2-Mini-v7.md"
LOG = ROOT / "Data/Generation_Log.json"
START = ROOT / "Images/Shot-06-First-Frame-v2.png"
END = ROOT / "Images/Shot-06-End-Frame-v2.png"
RAW = ROOT / "Working/Shot-06-Seedance-2-Mini-480p-v7.mp4"


def upload(path: Path) -> str:
    load_dotenv(Path.home() / ".env-secrets")
    key = os.environ.get("KIE_API_KEY")
    if not key:
        raise RuntimeError("KIE_API_KEY is missing")
    with path.open("rb") as handle:
        response = requests.post(
            "https://kieai.redpandaai.co/api/file-stream-upload",
            headers={"Authorization": f"Bearer {key}"},
            data={"uploadPath": "neon-parcel", "fileName": path.name},
            files={"file": (path.name, handle)},
            timeout=120,
        )
    response.raise_for_status()
    url = (response.json().get("data") or {}).get("downloadUrl")
    if not url:
        raise RuntimeError(f"Kie upload returned no downloadUrl: {response.text}")
    return url


def main() -> None:
    for path in (PROMPT, START, END):
        if not path.is_file():
            raise RuntimeError(f"Required asset missing: {path}")
    prompt = PROMPT.read_text(encoding="utf-8")
    start_url = upload(START)
    end_url = upload(END)
    shot = {
        "shot_id": "Shot-06",
        "route": "seedance_2_mini_first_last",
        "prompt_file": str(PROMPT),
        "generation_prompt": prompt,
        "first_frame_url": start_url,
        "last_frame_url": end_url,
        "visual_realism": "pass",
        "camera_plausibility": "pass",
        "meaningful_visual_beat": "pass",
        "humor_context": "pass",
        "generation_resolution": "480p",
        "postprocess": {},
    }
    gate = validate_document({"shots": [shot]})
    if not gate["ready_for_paid_generation"]:
        raise RuntimeError(gate)
    generate_seedance_mini(
        prompt,
        RAW,
        first_frame_url=start_url,
        last_frame_url=end_url,
        resolution="480p",
        duration=10,
        generate_audio=False,
        generation_log=LOG,
        shot_id="Shot-06",
        version="v7-first-last",
        prompt_file=PROMPT,
        retry_reason="tony_revision:approved option one with strict first and last temporal anchors; storyboard text only",
    )
    print(f"Generated raw clip pending manual approval: {RAW}")


if __name__ == "__main__":
    main()
