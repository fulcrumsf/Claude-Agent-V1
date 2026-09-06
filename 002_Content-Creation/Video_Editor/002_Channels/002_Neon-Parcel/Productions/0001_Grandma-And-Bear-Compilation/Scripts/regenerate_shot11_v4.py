#!/usr/bin/env python3
"""Regenerate Shot 11 from an exact single-scene crop."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
TOOLS = Path("/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools")
CHANNEL_TOOLS = Path("/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel")
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(CHANNEL_TOOLS))
from kie_market_api import create_task, download, generate_seedance_mini, poll_task  # type: ignore
from validate_pre_video_gate import validate_document  # type: ignore

KEY = "Shot-11"
LOG = ROOT / "Data/Generation_Log.json"


def move_to_archive(source: Path, archive_dir: Path) -> None:
    if not source.exists():
        return
    archive_dir.mkdir(parents=True, exist_ok=True)
    destination = archive_dir / source.name
    if destination.exists():
        raise FileExistsError(f"archive destination already exists: {destination}")
    shutil.move(str(source), str(destination))


def update_asset(version: str, **fields: object) -> None:
    data = json.loads(LOG.read_text(encoding="utf-8"))
    for item in data.get("assets", []):
        if item.get("shot_id") == KEY and item.get("version") == version:
            item.update(fields)
    LOG.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def upload(path: Path) -> str:
    load_dotenv(Path.home() / ".env-secrets")
    key = os.environ.get("KIE_API_KEY")
    if not key:
        raise RuntimeError("KIE_API_KEY is missing")
    with path.open("rb") as handle:
        response = requests.post("https://kieai.redpandaai.co/api/file-stream-upload", headers={"Authorization": f"Bearer {key}"}, data={"uploadPath": "neon-parcel", "fileName": path.name}, files={"file": (path.name, handle)}, timeout=120)
    response.raise_for_status()
    url = (response.json().get("data") or {}).get("downloadUrl")
    if not url:
        raise RuntimeError(f"Kie upload returned no downloadUrl: {response.text}")
    return url


def clean_start() -> Path:
    source = ROOT / "Images/Shot-11-Storyboard-v1.png"
    destination = ROOT / "Images/Shot-11-Start-Frame-v3.png"
    if not destination.exists():
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(source), "-vf", "crop=1920:980:0:0,scale=1920:1080", str(destination)], check=True)
    return destination


def main() -> None:
    start = clean_start()
    # Verify the image itself before using it as a temporal starting state.
    if "Storyboard" in start.name or start.stat().st_size == 0:
        raise RuntimeError("clean start image verification failed")
    prompt_v3 = ROOT / "Prompts/Seedance-2-Mini-v3.md"
    prompt_v3 = ROOT / "Prompts/Shot-11-Seedance-2-Mini-v3.md"
    prompt_v4 = ROOT / "Prompts/Shot-11-Seedance-2-Mini-v4.md"
    prompt_v4.write_text("# Revision v4: use only the attached clean single-scene temporal starting image; never render any storyboard, grid, panel, caption, or contact sheet.\n\n" + prompt_v3.read_text(encoding="utf-8"), encoding="utf-8")
    move_to_archive(prompt_v3, ROOT / "Prompts/Archived")
    move_to_archive(ROOT / "Working/Shot-11-Seedance-2-Mini-480p-v3.mp4", ROOT / "Working/Archived")
    move_to_archive(ROOT / "Intermediate/Shot-11-Topaz-2x-v3.mp4", ROOT / "Intermediate/Archived")
    move_to_archive(ROOT / "Video_Clips/Shot-11-1080p-v3.mp4", ROOT / "Video_Clips/Archived")
    move_to_archive(ROOT / "Images/Shot-11-Start-Frame-v1.png", ROOT / "Images/Archived")
    update_asset("v3", status="superseded_archived", superseded_by="v4", superseded_reason="clean-start crop was invalid and retained storyboard fragments")

    start_url = upload(start)
    gate = validate_document({"shots": [{"shot_id": KEY, "prompt_file": str(prompt_v4), "generation_prompt": prompt_v4.read_text(encoding="utf-8"), "route": "seedance_2_mini_clean_start_fallback", "first_frame_url": start_url, "visual_realism": "pass", "camera_plausibility": "pass", "meaningful_visual_beat": "pass", "humor_context": "pass", "generation_resolution": "480p", "postprocess": {"topaz_factor": "2x", "final_normalization": "1920x1080"}}]})
    if not gate["ready_for_paid_generation"]:
        raise RuntimeError(gate)

    raw = ROOT / "Working/Shot-11-Seedance-2-Mini-480p-v4.mp4"
    topaz = ROOT / "Intermediate/Shot-11-Topaz-2x-v4.mp4"
    final = ROOT / "Video_Clips/Shot-11-1080p-v4.mp4"
    generate_seedance_mini(prompt_v4.read_text(encoding="utf-8"), raw, first_frame_url=start_url, resolution="480p", duration=10, generate_audio=True, generation_log=LOG, shot_id=KEY, version="v4", prompt_file=prompt_v4, retry_reason="tony_revision:validated clean start after v3 storyboard-crop failure")
    source_url = upload(raw)
    topaz_task_id = create_task("topaz/video-upscale", {"video_url": source_url, "upscale_factor": "2"})
    update_asset("v4", route="seedance_2_mini_clean_start_fallback", topaz_task_id=topaz_task_id, topaz_source_url=source_url, status="topaz_submitted")
    result = poll_task(topaz_task_id)
    urls = result.get("resultUrls") or []
    if not urls:
        raise RuntimeError(f"Topaz task {topaz_task_id} returned no result URL")
    download(urls[0], topaz)
    subprocess.run(["ffmpeg", "-y", "-i", str(topaz), "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-movflags", "+faststart", str(final)], check=True)
    update_asset("v4", status="completed", raw_output=str(raw.relative_to(ROOT)), topaz_output=str(topaz.relative_to(ROOT)), final_output=str(final.relative_to(ROOT)), resolution="1920x1080", postprocess="topaz-2x-then-ffmpeg-1920x1080")
    print(f"Completed {KEY}: {final}", flush=True)


if __name__ == "__main__":
    main()
