#!/usr/bin/env python3
"""Upscale and normalize the approved Shot 06 Seedance v3 render."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from regenerate_storyboard_shots_v2 import upload

from kie_market_api import create_task, download, poll_task


ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "Data/Generation_Log.json"
RAW = ROOT / "Working/Shot-06-Seedance-2-Mini-480p-v3.mp4"
TOPAZ = ROOT / "Intermediate/Shot-06-Topaz-2x-v3.mp4"
FINAL = ROOT / "Video_Clips/Shot-06-1080p-v3.mp4"


def update_log(**fields: object) -> None:
    data = json.loads(LOG.read_text(encoding="utf-8"))
    for item in data.get("assets", []):
        if item.get("shot_id") == "Shot-06" and item.get("version") == "v3":
            item.update(fields)
    LOG.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    if not RAW.is_file():
        raise FileNotFoundError(RAW)
    if not TOPAZ.is_file():
        source_url = upload(RAW)
        task_id = create_task("topaz/video-upscale", {"video_url": source_url, "upscale_factor": "2"})
        update_log(status="topaz_submitted", topaz_task_id=task_id, topaz_source_url=source_url)
        result = poll_task(task_id)
        urls = result.get("resultUrls") or []
        if not urls:
            raise RuntimeError(f"Topaz task {task_id} returned no result URL")
        download(urls[0], TOPAZ)
    if not FINAL.is_file():
        FINAL.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(TOPAZ),
                "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-movflags", "+faststart",
                str(FINAL),
            ],
            check=True,
        )
    update_log(
        status="completed",
        raw_output=str(RAW.relative_to(ROOT)),
        topaz_output=str(TOPAZ.relative_to(ROOT)),
        final_output=str(FINAL.relative_to(ROOT)),
        resolution="1920x1080",
        postprocess="topaz-2x-then-ffmpeg-1920x1080",
    )
    print(FINAL)


if __name__ == "__main__":
    main()
