#!/usr/bin/env python3
"""Generate and finish Neon Parcel shots 8-12 without approval pauses."""

import json
import os
import subprocess
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

TOOLS = Path("/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools")
sys.path.insert(0, str(TOOLS))
from kie_market_api import create_guarded_task, create_task, download, poll_task  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "Data/Generation_Log.json"
URLS = ROOT / "Data/Reference_Urls_v1.json"
SHOTS = {8: 12, 9: 10, 10: 10, 11: 10, 12: 12}


def update_log(shot: int, **fields: object) -> None:
    data = json.loads(LOG.read_text(encoding="utf-8"))
    for item in data.get("assets", []):
        if item.get("shot_id") == f"Shot-{shot:02d}" and item.get("version") == "v1":
            item.update(fields)
    LOG.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


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


def normalize(source: Path, destination: Path) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(source), "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-movflags", "+faststart", str(destination)],
        check=True,
    )


def main() -> None:
    refs = json.loads(URLS.read_text(encoding="utf-8"))
    for shot, duration in SHOTS.items():
        key = f"Shot-{shot:02d}"
        prompt_file = ROOT / f"Prompts/{key}-Seedance-2-Mini-v1.md"
        raw = ROOT / f"Working/{key}-Seedance-2-Mini-480p-v1.mp4"
        topaz = ROOT / f"Intermediate/{key}-Topaz-2x-v1.mp4"
        final = ROOT / f"Video_Clips/{key}-1080p-v1.mp4"
        prompt = prompt_file.read_text(encoding="utf-8")

        if not raw.exists():
            task_id = create_guarded_task(
                "bytedance/seedance-2-mini",
                {"prompt": prompt, "resolution": "480p", "duration": duration, "generate_audio": True, "reference_image_urls": [refs[key]]},
                generation_log=LOG,
                shot_id=key,
                version="v1",
                prompt_file=prompt_file,
            )
            result = poll_task(task_id)
            urls = result.get("resultUrls") or []
            if not urls:
                raise RuntimeError(f"Seedance task {task_id} returned no result URL")
            download(urls[0], raw)
        if not topaz.exists():
            source_url = upload(raw)
            topaz_task_id = create_task("topaz/video-upscale", {"video_url": source_url, "upscale_factor": "2"})
            update_log(shot, status="topaz_submitted", topaz_task_id=topaz_task_id, topaz_source_url=source_url)
            result = poll_task(topaz_task_id)
            urls = result.get("resultUrls") or []
            if not urls:
                raise RuntimeError(f"Topaz task {topaz_task_id} returned no result URL")
            download(urls[0], topaz)
        if not final.exists():
            normalize(topaz, final)
        update_log(shot, status="completed", raw_output=str(raw.relative_to(ROOT)), topaz_output=str(topaz.relative_to(ROOT)), final_output=str(final.relative_to(ROOT)), resolution="1920x1080", postprocess="topaz-2x-then-ffmpeg-1920x1080")
        print(f"Completed {key}: {final}", flush=True)


if __name__ == "__main__":
    main()
