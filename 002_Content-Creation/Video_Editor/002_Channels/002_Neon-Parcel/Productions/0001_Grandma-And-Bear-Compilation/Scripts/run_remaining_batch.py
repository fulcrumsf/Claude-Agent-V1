#!/usr/bin/env python3
"""Generate and finish the unreviewed Neon Parcel clips exactly once."""

from __future__ import annotations

import json
import hashlib
import hmac
import os
import subprocess
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
TOOLS = Path("/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools")
sys.path.insert(0, str(TOOLS))

from kie_market_api import (  # type: ignore
    create_task,
    download,
    generate_seedance_mini,
    poll_task,
)


SHOTS = {
    6: 10,
    7: 10,
    8: 12,
    9: 10,
    10: 10,
    11: 10,
    12: 12,
}
LOG = ROOT / "Data/Generation_Log.json"
URLS_FILE = ROOT / "Data/Reference_Urls_v1.json"


def upload_reference(path: Path) -> str:
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
    result = response.json()
    url = (result.get("data") or {}).get("downloadUrl")
    if not url:
        raise RuntimeError(f"Kie upload returned no downloadUrl: {result}")
    return url


def save_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def update_log(shot: int, status: str, **fields: object) -> None:
    data = json.loads(LOG.read_text(encoding="utf-8"))
    for item in data.get("assets", []):
        if item.get("shot_id") in {f"Shot-{shot:02d}", f"shot_{shot}"} and item.get("version") == "v1":
            item.update({"status": status, **fields})
    save_json(LOG, data)


def run_ffmpeg(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(source),
            "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-movflags", "+faststart",
            str(destination),
        ],
        check=True,
    )


def main() -> None:
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    reference_urls: dict[str, str] = {}
    if URLS_FILE.exists():
        reference_urls = json.loads(URLS_FILE.read_text(encoding="utf-8"))

    # Upload each storyboard once so the video requests use the exact generated asset.
    for shot in SHOTS:
        key = f"Shot-{shot:02d}"
        image = ROOT / f"Images/{key}-Storyboard-v1.png"
        if key not in reference_urls:
            reference_urls[key] = upload_reference(image)
            save_json(URLS_FILE, reference_urls)

    for shot, duration in SHOTS.items():
        key = f"Shot-{shot:02d}"
        prompt_file = ROOT / f"Prompts/{key}-Seedance-2-Mini-v1.md"
        prompt = prompt_file.read_text(encoding="utf-8")
        raw = ROOT / f"Working/{key}-Seedance-2-Mini-480p-v1.mp4"
        topaz = ROOT / f"Intermediate/{key}-Topaz-2x-v1.mp4"
        final = ROOT / f"Video_Clips/{key}-1080p-v1.mp4"

        if not raw.exists():
            update_log(shot, "submitted", route="seedance-2-mini-480p-topaz-2x-ffmpeg-1080p")
            generate_seedance_mini(
                prompt,
                raw,
                reference_image_urls=[reference_urls[key]],
                resolution="480p",
                duration=duration,
                generate_audio=True,
                generation_log=LOG,
                shot_id=key,
                version="v1",
                prompt_file=prompt_file,
            )
        if not topaz.exists():
            topaz_url = upload_reference(raw)
            topaz_task_id = create_task(
                "topaz/video-upscale",
                {"video_url": topaz_url, "upscale_factor": "2"},
            )
            update_log(shot, "topaz_submitted", topaz_task_id=topaz_task_id)
            result = poll_task(topaz_task_id)
            urls = result.get("resultUrls") or []
            if not urls:
                raise RuntimeError(f"Topaz task {topaz_task_id} succeeded without a result URL")
            download(urls[0], topaz)
        if not final.exists():
            run_ffmpeg(topaz, final)
        update_log(
            shot,
            "completed",
            raw_output=str(raw.relative_to(ROOT)),
            topaz_output=str(topaz.relative_to(ROOT)),
            final_output=str(final.relative_to(ROOT)),
            resolution="1920x1080",
            postprocess="topaz-2x-then-ffmpeg-1920x1080",
        )
        print(f"Completed {key}: {final}", flush=True)


if __name__ == "__main__":
    main()
