#!/usr/bin/env python3
"""Recover the approved Shot 12 v8 raw clip and upscale it once."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import requests
from dotenv import load_dotenv

import sys

TOOLS = Path("/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools")
sys.path.insert(0, str(TOOLS))
from kie_market_api import create_task, download, poll_task  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "Data/Generation_Log.json"
RAW = ROOT / "Working/Shot-12-Seedance-2-Mini-480p-v8.mp4"
TOPAZ = ROOT / "Intermediate/Shot-12-Topaz-2x-v8.mp4"
FINAL = ROOT / "Video_Clips/Shot-12-1080p-v8.mp4"
TASK_ID = "598a54640b1872a89e542efa537f8aa2"


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


def update_log(**fields: object) -> None:
    data = json.loads(LOG.read_text(encoding="utf-8"))
    for item in data.get("assets", []):
        if item.get("shot_id") == "Shot-12" and item.get("version") == "v8":
            item.update(fields)
    LOG.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def existing_topaz_task_id() -> str | None:
    data = json.loads(LOG.read_text(encoding="utf-8"))
    for item in data.get("assets", []):
        if item.get("shot_id") == "Shot-12" and item.get("version") == "v8":
            return item.get("topaz_task_id")
    return None


def main() -> None:
    if not RAW.exists():
        result = poll_task(TASK_ID)
        urls = result.get("resultUrls") or []
        if not urls:
            raise RuntimeError(f"Seedance task {TASK_ID} returned no result URL")
        download(urls[0], RAW)
        update_log(status="raw_downloaded", provider_output_url=urls[0], raw_output=str(RAW.relative_to(ROOT)), postprocess="blocked_until_manual_approval")
    if not TOPAZ.exists():
        topaz_task_id = existing_topaz_task_id()
        if not topaz_task_id:
            source_url = upload(RAW)
            topaz_task_id = create_task("topaz/video-upscale", {"video_url": source_url, "upscale_factor": "2"})
            update_log(status="topaz_submitted", topaz_task_id=topaz_task_id, topaz_source_url=source_url)
        result = poll_task(topaz_task_id)
        urls = result.get("resultUrls") or []
        if not urls:
            raise RuntimeError(f"Topaz task {topaz_task_id} returned no result URL")
        download(urls[0], TOPAZ)
    if not FINAL.exists():
        FINAL.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-y", "-i", str(TOPAZ), "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-movflags", "+faststart", str(FINAL)], check=True)
    update_log(status="completed", raw_output=str(RAW.relative_to(ROOT)), topaz_output=str(TOPAZ.relative_to(ROOT)), final_output=str(FINAL.relative_to(ROOT)), resolution="1920x1080", postprocess="topaz-2x-then-ffmpeg-1920x1080", approval_note="Tony approved Shot 12 v8 raw video before upscale.")
    print(FINAL)


if __name__ == "__main__":
    main()
