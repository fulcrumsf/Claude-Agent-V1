# image_generation.py — shared GPT-Image-2 call wrapper for reference-sheet skills.
# Self-contained per skill (matches the existing pattern in
# Reimagined_Realms_POV_Shorts_Pipeline and _v2, which each keep their own copy
# rather than cross-import) so this skill works standalone in any channel.
#
# 2026-08-16: kie-cli's --input_urls requires real public HTTPS URLs — a local
# file path fails with a Zod "Invalid url" validation error. Fixed by
# auto-uploading any local path to Cloudinary first (the documented workspace
# pattern in TOOLBOX.md for exactly this: "upload local images to get public
# HTTPS URLs for AI APIs that require hosted image URLs").
#
# 2026-08-17: Cloudinary's free-tier upload cap is 10MB — a 4K reference sheet
# (e.g. a character sheet with a baked-in text panel) can exceed that and fail
# the whole generation call. Fixed by downscaling/recompressing to a temp file
# before upload ONLY when the source exceeds the cap; the original full-res
# file on disk is never touched, this only affects what gets sent as a
# reference for THIS call.
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path

import requests

CLOUDINARY_MAX_BYTES = 10 * 1024 * 1024  # 10MB free-tier cap


def _shrink_for_upload(path: str) -> str:
    """Returns a path safe to upload to Cloudinary — either the original path
    unchanged, or a temp downscaled/recompressed copy if the original exceeds
    the free-tier size cap."""
    size = Path(path).stat().st_size
    if size <= CLOUDINARY_MAX_BYTES:
        return path

    from PIL import Image

    img = Image.open(path).convert("RGB")
    quality = 90
    scale = 1.0
    tmp_path = tempfile.mktemp(suffix=".jpg")

    while True:
        w, h = int(img.width * scale), int(img.height * scale)
        resized = img.resize((w, h), Image.LANCZOS) if scale < 1.0 else img
        resized.save(tmp_path, "JPEG", quality=quality)
        if Path(tmp_path).stat().st_size <= CLOUDINARY_MAX_BYTES:
            return tmp_path
        # Still too big — reduce quality first, then scale, and retry.
        if quality > 60:
            quality -= 10
        else:
            scale *= 0.85


def _resolve_to_public_url(path_or_url: str) -> str:
    """Pass through anything that's already a URL; upload local file paths to
    Cloudinary so kie.ai's endpoint (which validates input_urls as real URLs,
    not local paths) can fetch them."""
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        return path_or_url

    import cloudinary
    import cloudinary.uploader

    cloudinary.config(
        cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
        api_key=os.environ["CLOUDINARY_API_Key"],
        api_secret=os.environ["CLOUDINARY_API_Secret"],
        secure=True,
    )
    upload_path = _shrink_for_upload(path_or_url)
    result = cloudinary.uploader.upload(upload_path, overwrite=True)
    return result["secure_url"]


def submit_image_task(
    prompt: str,
    aspect_ratio: str = "1:1",
    resolution: str = "2K",
    input_urls: list[str] | None = None,
) -> str:
    resolved_urls = [_resolve_to_public_url(u) for u in (input_urls or [])]

    cmd = [
        "kie-cli", "gpt_image_2",
        "--prompt", prompt,
        "--aspect_ratio", aspect_ratio,
        "--resolution", resolution,
        "--json",
    ]
    for url in resolved_urls:
        cmd += ["--input_urls", url]

    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)["task_id"]


def poll_image_task(task_id: str, poll_interval_seconds: float = 15.0, max_attempts: int = 12) -> str:
    for attempt in range(max_attempts):
        if attempt > 0:
            time.sleep(poll_interval_seconds)

        result = subprocess.run(
            ["kie-cli", "get_task_status", "--task_id", task_id, "--json"],
            check=True, capture_output=True, text=True,
        )
        data = json.loads(result.stdout)
        status = data.get("status")
        # kie-cli's real response uses status: "success" (not "completed") and
        # result_urls: [...] (a list, not a singular result_url) — confirmed
        # live 2026-08-16 after this exact mismatch caused a false timeout on
        # a task that had actually completed in 67 seconds.
        if status == "success":
            result_urls = data.get("result_urls") or []
            if result_urls:
                return result_urls[0]
            raise RuntimeError(f"Image task {task_id} reported success but returned no result_urls: {data}")
        if status in ("failed", "fail"):
            raise RuntimeError(f"Image task {task_id} failed: {data.get('error')}")

    raise TimeoutError(f"Image task {task_id} did not complete after {max_attempts} attempts")


def generate_image(
    prompt: str,
    output_path: Path,
    aspect_ratio: str = "1:1",
    resolution: str = "2K",
    input_urls: list[str] | None = None,
) -> Path:
    task_id = submit_image_task(prompt, aspect_ratio, resolution, input_urls)
    result_url = poll_image_task(task_id)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    resp = requests.get(result_url, timeout=60)
    resp.raise_for_status()
    output_path.write_bytes(resp.content)
    return output_path
