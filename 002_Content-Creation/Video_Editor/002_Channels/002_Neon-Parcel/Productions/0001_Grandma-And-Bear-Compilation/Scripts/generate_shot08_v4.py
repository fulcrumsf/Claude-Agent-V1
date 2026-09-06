#!/usr/bin/env python3
"""Generate Shot 08 v4 from the approved storyboard route; hold before upscale."""

from __future__ import annotations

import json
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


PROMPT = ROOT / "Prompts/Shot-08-Seedance-2-Mini-v4.md"
STORYBOARD = ROOT / "Images/Shot-08-Storyboard-v3.png"
LOG = ROOT / "Data/Generation_Log.json"
RAW = ROOT / "Working/Shot-08-Seedance-2-Mini-480p-v4.mp4"
MANIFEST = ROOT / "Working/Analysis/Shot-08-Storyboard-QA-v3/handoff-manifest.json"


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
    for path in (PROMPT, STORYBOARD, MANIFEST):
        if not path.is_file():
            raise RuntimeError(f"Required asset missing: {path}")
    storyboard_url = upload(STORYBOARD)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["storyboard_reference_url"] = storyboard_url
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    prompt = PROMPT.read_text(encoding="utf-8")
    shot = {
        "shot_id": "Shot-08",
        "route": "seedance_2_mini_storyboard",
        "prompt_file": str(PROMPT),
        "generation_prompt": prompt,
        "reference_image_urls": [storyboard_url],
        "storyboard_handoff_manifest": str(MANIFEST),
        "visual_realism": "pass",
        "camera_plausibility": "pass",
        "meaningful_visual_beat": "pass",
        "humor_context": "pass",
        "generation_resolution": "480p",
        "postprocess": {"topaz_factor": "2x", "final_normalization": "1920x1080"},
    }
    gate = validate_document({"shots": [shot]})
    if not gate["ready_for_paid_generation"]:
        raise RuntimeError(gate)
    generate_seedance_mini(
        prompt,
        RAW,
        resolution="480p",
        duration=12,
        generate_audio=True,
        generation_log=LOG,
        shot_id="Shot-08",
        version="v4",
        prompt_file=PROMPT,
        retry_reason="tony_revision:approved storyboard v3 with explicit bear and Grandma origin paths",
        reference_image_urls=[storyboard_url],
    )
    data = json.loads(LOG.read_text(encoding="utf-8"))
    for item in data.get("assets", []):
        if item.get("shot_id") == "Shot-08" and item.get("version") == "v4":
            item.update({"route": "seedance_2_mini_storyboard", "reference_url": storyboard_url, "raw_output": str(RAW.relative_to(ROOT)), "status": "awaiting_manual_approval", "postprocess": "blocked_until_manual_approval"})
    LOG.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Generated raw clip pending manual approval: {RAW}")


if __name__ == "__main__":
    main()
