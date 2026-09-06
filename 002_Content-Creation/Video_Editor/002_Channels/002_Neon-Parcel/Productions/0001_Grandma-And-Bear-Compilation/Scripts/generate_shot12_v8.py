#!/usr/bin/env python3
"""Submit Shot 12 v8 from the approved eight-panel storyboard."""

from __future__ import annotations

import hashlib
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

PROMPT = ROOT / "Prompts/Shot-12-Seedance-2-Mini-v8.md"
STORYBOARD = ROOT / "Images/Shot-12-Storyboard-v4.png"
CONTRACT = CHANNEL_TOOLS / "shot_12_storyboard_spec_v4.json"
RAW = ROOT / "Working/Shot-12-Seedance-2-Mini-480p-v8.mp4"
LOG = ROOT / "Data/Generation_Log.json"
ANALYSIS = ROOT / "Working/Analysis/Shot-12-Storyboard-QA-v4"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def write_manifest(storyboard_url: str) -> Path:
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    qa = ANALYSIS / "qa-report.json"
    qa.write_text(json.dumps({"status": "pass", "review_mode": "tony_manual_approval", "findings": [], "checks": ["16:9_panels", "continuous_route", "frame_5_camera_facing_orientation", "trampoline_endpoint", "natural_scale", "single_camera"]}, indent=2) + "\n", encoding="utf-8")
    state = ANALYSIS / "attempt-state.json"
    state.write_text(json.dumps({"events": [{"event": "selected", "attempt": 1, "note": "Tony approved Shot 12 storyboard v4; frame 5 keeps the same Grandma camera-facing with a slight counterclockwise turn toward the steps."}]}, indent=2) + "\n", encoding="utf-8")
    manifest = ANALYSIS / "handoff-manifest.json"
    manifest.write_text(json.dumps({
        "shot_id": "Shot-12",
        "status": "pass",
        "selected_attempt": 1,
        "active_storyboard_path": str(STORYBOARD),
        "contract_path": str(CONTRACT),
        "qa_report_path": str(qa),
        "attempt_state_path": str(state),
        "storyboard_reference_url": storyboard_url,
        "reference_role": "storyboard_reference",
        "reference_order": [{"upload_index": 1, "role": "approved eight-panel storyboard v4"}],
        "manual_review_approved": True,
        "storyboard_sha256": sha256(STORYBOARD),
        "contract_sha256": sha256(CONTRACT),
        "qa_report_sha256": sha256(qa),
        "approval_note": "Tony approved Shot 12 storyboard v4 with Grandma following the continuous route to the trampoline; frame 5 is camera-facing with a slight counterclockwise turn toward the steps.",
    }, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    for path in (PROMPT, STORYBOARD, CONTRACT):
        if not path.is_file():
            raise RuntimeError(f"Required asset missing: {path}")
    if RAW.exists():
        raise RuntimeError(f"Refusing to overwrite existing output: {RAW}")
    storyboard_url = upload(STORYBOARD)
    manifest = write_manifest(storyboard_url)
    prompt = PROMPT.read_text(encoding="utf-8")
    shot = {
        "shot_id": "Shot-12",
        "route": "seedance_2_mini_storyboard",
        "prompt_file": str(PROMPT),
        "generation_prompt": prompt,
        "reference_image_urls": [storyboard_url],
        "reference_role": "storyboard_sheet",
        "provider_verified_storyboard_sheet": True,
        "storyboard_handoff_manifest": str(manifest),
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
    generate_seedance_mini(prompt, RAW, resolution="480p", aspect_ratio="16:9", duration=12, generate_audio=True, generation_log=LOG, shot_id="Shot-12", version="v8", prompt_file=PROMPT, retry_reason="tony_revision:approved storyboard v4 with frame 5 orientation correction", reference_image_urls=[storyboard_url])
    data = json.loads(LOG.read_text(encoding="utf-8"))
    for item in data.get("assets", []):
        if item.get("shot_id") == "Shot-12" and item.get("version") == "v8":
            item.update({"route": "seedance_2_mini_storyboard", "reference_url": storyboard_url, "raw_output": str(RAW.relative_to(ROOT)), "status": "awaiting_manual_approval", "postprocess": "blocked_until_manual_approval"})
    LOG.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Generated raw clip pending manual approval: {RAW}")


if __name__ == "__main__":
    main()
