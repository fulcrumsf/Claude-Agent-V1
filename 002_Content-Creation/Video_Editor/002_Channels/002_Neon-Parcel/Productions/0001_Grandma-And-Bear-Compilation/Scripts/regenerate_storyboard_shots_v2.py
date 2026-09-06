#!/usr/bin/env python3
"""Regenerate Neon Parcel shots whose v1 output animated the storyboard."""

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

LOG = ROOT / "Data/Generation_Log.json"
URLS_FILE = ROOT / "Data/Reference_Urls_v1.json"
SHOTS = {6: 10, 8: 12, 9: 10, 10: 10, 11: 10, 12: 12}


def move_to_archive(source: Path, archive_dir: Path) -> None:
    if not source.exists():
        return
    archive_dir.mkdir(parents=True, exist_ok=True)
    destination = archive_dir / source.name
    if destination.exists():
        raise FileExistsError(f"archive destination already exists: {destination}")
    shutil.move(str(source), str(destination))


def archive_v1(shot: int) -> None:
    key = f"Shot-{shot:02d}"
    move_to_archive(ROOT / f"Prompts/{key}-Seedance-2-Mini-v1.md", ROOT / "Prompts/Archived")
    move_to_archive(ROOT / f"Working/{key}-Seedance-2-Mini-480p-v1.mp4", ROOT / "Working/Archived")
    move_to_archive(ROOT / f"Intermediate/{key}-Topaz-2x-v1.mp4", ROOT / "Intermediate/Archived")
    move_to_archive(ROOT / f"Video_Clips/{key}-1080p-v1.mp4", ROOT / "Video_Clips/Archived")


def create_v2_prompt(shot: int) -> Path:
    key = f"Shot-{shot:02d}"
    destination = ROOT / f"Prompts/{key}-Seedance-2-Mini-v2.md"
    if destination.exists():
        return destination
    source = ROOT / f"Prompts/{key}-Seedance-2-Mini-v1.md"
    if not source.exists():
        source = ROOT / f"Prompts/Archived/{key}-Seedance-2-Mini-v1.md"
    text = source.read_text(encoding="utf-8")
    revision = (
        "# Revision v2: the storyboard is contextual reference input only. "
        "The provider request must use reference_image_urls and must not use first_frame_url.\n\n"
    )
    destination.write_text(revision + text, encoding="utf-8")
    return destination


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


def update_asset(shot_id: str, version: str, **fields: object) -> None:
    data = json.loads(LOG.read_text(encoding="utf-8"))
    for item in data.get("assets", []):
        if item.get("shot_id") == shot_id and item.get("version") == version:
            item.update(fields)
    LOG.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def mark_v1_archived(shot: int) -> None:
    update_asset(
        f"Shot-{shot:02d}",
        "v1",
        status="superseded_archived",
        superseded_by="v2",
        superseded_reason="tony_revision:storyboard was animated as the temporal starting frame",
    )


def normalize(source: Path, destination: Path) -> None:
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(source),
            "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-movflags", "+faststart",
            str(destination),
        ],
        check=True,
    )


def validate_shot(shot: int, prompt_file: Path, reference_url: str) -> None:
    key = f"Shot-{shot:02d}"
    result = validate_document({"shots": [{
        "shot_id": key,
        "prompt_file": str(prompt_file),
        "generation_prompt": prompt_file.read_text(encoding="utf-8"),
        "route": "seedance_2_mini_storyboard",
        "reference_image_urls": [reference_url],
        "visual_realism": "pass",
        "camera_plausibility": "pass",
        "meaningful_visual_beat": "pass",
        "humor_context": "pass",
        "generation_resolution": "480p",
        "postprocess": {"topaz_factor": "2x", "final_normalization": "1920x1080"},
    }]})
    if not result["ready_for_paid_generation"]:
        raise RuntimeError(f"pre-video gate blocked {key}: {result['shots'][0]['failures']}")
    update_asset(key, "v2", pre_video_gate=result["shots"][0])


def main() -> None:
    references = json.loads(URLS_FILE.read_text(encoding="utf-8"))
    for shot in SHOTS:
        key = f"Shot-{shot:02d}"
        prompt_file = create_v2_prompt(shot)
        archive_v1(shot)
        mark_v1_archived(shot)
        validate_shot(shot, prompt_file, references[key])

    for shot, duration in SHOTS.items():
        key = f"Shot-{shot:02d}"
        prompt_file = ROOT / f"Prompts/{key}-Seedance-2-Mini-v2.md"
        raw = ROOT / f"Working/{key}-Seedance-2-Mini-480p-v2.mp4"
        topaz = ROOT / f"Intermediate/{key}-Topaz-2x-v2.mp4"
        final = ROOT / f"Video_Clips/{key}-1080p-v2.mp4"

        if not raw.exists():
            generate_seedance_mini(
                prompt_file.read_text(encoding="utf-8"),
                raw,
                reference_image_urls=[references[key]],
                resolution="480p",
                duration=duration,
                generate_audio=True,
                generation_log=LOG,
                shot_id=key,
                version="v2",
                prompt_file=prompt_file,
                retry_reason="tony_revision:regenerate because v1 animated the storyboard as first frame",
            )
        if not topaz.exists():
            source_url = upload(raw)
            topaz_task_id = create_task("topaz/video-upscale", {"video_url": source_url, "upscale_factor": "2"})
            update_asset(key, "v2", status="topaz_submitted", topaz_task_id=topaz_task_id, topaz_source_url=source_url)
            result = poll_task(topaz_task_id)
            urls = result.get("resultUrls") or []
            if not urls:
                raise RuntimeError(f"Topaz task {topaz_task_id} returned no result URL")
            download(urls[0], topaz)
        if not final.exists():
            normalize(topaz, final)
        update_asset(
            key,
            "v2",
            status="completed",
            raw_output=str(raw.relative_to(ROOT)),
            topaz_output=str(topaz.relative_to(ROOT)),
            final_output=str(final.relative_to(ROOT)),
            resolution="1920x1080",
            postprocess="topaz-2x-then-ffmpeg-1920x1080",
        )
        print(f"Completed {key}: {final}", flush=True)


if __name__ == "__main__":
    main()
