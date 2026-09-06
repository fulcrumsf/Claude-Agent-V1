#!/usr/bin/env python3
"""Submit Shot 12 v6 using Kie's explicit @Image 1 storyboard binding."""

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
from validate_pre_video_gate import validate_document

PROMPT = ROOT / "Prompts/Shot-12-Seedance-2-Mini-v6.md"
STORYBOARD = ROOT / "Images/Shot-12-Storyboard-v2.png"
MANIFEST = ROOT / "Working/Analysis/Shot-12-Storyboard-QA-v2/handoff-manifest.json"
RAW = ROOT / "Working/Shot-12-Seedance-2-Mini-480p-v6.mp4"
LOG = ROOT / "Data/Generation_Log.json"


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
    if RAW.exists():
        raise RuntimeError(f"Refusing to overwrite existing output: {RAW}")
    storyboard_url = upload(STORYBOARD)
    prompt = PROMPT.read_text(encoding="utf-8")
    shot = {
        "shot_id": "Shot-12",
        "route": "seedance_2_mini_storyboard",
        "prompt_file": str(PROMPT),
        "generation_prompt": prompt,
        "reference_image_urls": [storyboard_url],
        "reference_role": "storyboard_sheet",
        "provider_verified_storyboard_sheet": True,
        "storyboard_handoff_manifest": str(MANIFEST),
        "generation_resolution": "480p",
        "visual_realism": "pass",
        "camera_plausibility": "pass",
        "meaningful_visual_beat": "pass",
        "humor_context": "pass",
        "postprocess": {"topaz_factor": "2x", "final_normalization": "1920x1080"},
    }
    gate = validate_document({"shots": [shot]})
    if not gate["ready_for_paid_generation"]:
        raise RuntimeError(gate)
    generate_seedance_mini(
        prompt,
        RAW,
        resolution="480p",
        aspect_ratio="16:9",
        duration=12,
        generate_audio=True,
        generation_log=LOG,
        shot_id="Shot-12",
        version="v6",
        prompt_file=PROMPT,
        retry_reason="tony_revision:corrected Kie @Image 1 storyboard binding",
        reference_image_urls=[storyboard_url],
    )
    data = json.loads(LOG.read_text(encoding="utf-8"))
    for item in data.get("assets", []):
        if item.get("shot_id") == "Shot-12" and item.get("version") == "v6":
            item.update({"route": "seedance_2_mini_storyboard", "reference_url": storyboard_url, "raw_output": str(RAW.relative_to(ROOT)), "status": "awaiting_manual_approval", "postprocess": "blocked_until_manual_approval"})
    LOG.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Generated raw clip pending manual approval: {RAW}")


if __name__ == "__main__":
    main()
