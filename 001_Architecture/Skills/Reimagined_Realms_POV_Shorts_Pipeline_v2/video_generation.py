# video_generation.py — v2: Seedance 2.0 via kie.ai, first-frame-anchored generation
#
# v1 generated each shot from a single per-shot first-frame image (Seedance 1.5 Pro
# via WaveSpeed). v2's first POC round conditioned every shot on two fixed,
# production-wide reference images only (character sheet + environment sheet),
# no per-shot image at all — chosen as the simpler variant to test first.
#
# 2026-08-06 update: that POC round surfaced real problems (see the Titanic Stoker
# production review) — no per-shot camera lock meant several shots drifted from
# their intended action or composition. Fixed by wiring back in a per-shot
# first_frame_url, now sourced from storyboard_generation.py's individual POV-locked
# panel images (one full-resolution 9:16 image per beat) rather than a generic sheet.
#
# 2026-08-08 correction: the 2026-08-06 note above assumed first_frame_url and
# reference_image_urls could be passed together (first_frame_url anchoring the
# shot's composition, reference_image_urls carrying character/environment
# consistency). Confirmed live against the real kie.ai endpoint that this is
# false — the API rejects the combination outright ("The reference image and
# the first and last frames are mutually exclusive, and only one scene can be
# selected"). This was never actually wrong to assume conceptually, either:
# this pipeline's sheet-driven architecture already bakes character/prop/
# environment consistency into each scene's first-frame image at the image-
# generation stage (character_sheet_generation.py, prop_sheet_generation.py,
# environment_sheet_generation.py, storyboard_generation.py) — first_frame_url
# alone is the correct and sufficient reference for video generation. Passing
# reference_image_urls on top of it was both technically invalid and logically
# redundant. reference_image_urls remains available only as a fallback for the
# rare case where a shot has no first-frame image at all (not used by this
# pipeline's primary path — see shot_list_builder.py's character_roles note).
import argparse
import json
import shutil
import subprocess
import time
from pathlib import Path

import requests

SEEDANCE_MODE = "standard"  # seedance-2, higher quality — quality is the stated priority over speed/cost


SUBMIT_RETRY_ATTEMPTS = 3
SUBMIT_RETRY_DELAY_SECONDS = 5.0


def submit_video_task(
    video_prompt: str,
    first_frame_url: str | None = None,
    reference_image_urls: list[str] | None = None,
    duration: int = 5,
    resolution: str = "720p",
    aspect_ratio: str = "9:16",
) -> str:
    if first_frame_url and reference_image_urls:
        raise ValueError(
            "first_frame_url and reference_image_urls are mutually exclusive on kie.ai's "
            "bytedance_seedance_video endpoint (confirmed live 2026-08-08) — pass exactly one, "
            "never both. In this pipeline's sheet-driven architecture, first_frame_url alone is "
            "correct: character/prop/environment consistency is already baked into that image at "
            "generation time, so no separate reference_image_urls are needed on top of it."
        )

    cmd = [
        "kie-cli", "bytedance_seedance_video",
        "--prompt", video_prompt,
        "--mode", SEEDANCE_MODE,
        "--duration", str(duration),
        "--resolution", resolution,
        "--aspect_ratio", aspect_ratio,
        "--generate_audio", "true",
        "--json",
    ]
    if first_frame_url:
        cmd += ["--first_frame_url", first_frame_url]
    for url in reference_image_urls or []:
        cmd += ["--reference_image_urls", url]

    for attempt in range(SUBMIT_RETRY_ATTEMPTS):
        if attempt > 0:
            time.sleep(SUBMIT_RETRY_DELAY_SECONDS)
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            return json.loads(result.stdout)["task_id"]
        except subprocess.CalledProcessError:
            # kie-cli submission occasionally fails transiently (rate limiting,
            # network blips) — confirmed 2026-08-05 when an identical command
            # succeeded on manual retry seconds later. Retry a few times before
            # giving up rather than failing the whole batch on one flaky call.
            if attempt == SUBMIT_RETRY_ATTEMPTS - 1:
                raise


def poll_video_task(task_id: str, poll_interval_seconds: float = 45.0, max_attempts: int = 20) -> str:
    for attempt in range(max_attempts):
        if attempt > 0:
            time.sleep(poll_interval_seconds)

        result = subprocess.run(
            ["kie-cli", "get_task_status", "--task_id", task_id, "--json"],
            check=True, capture_output=True, text=True,
        )
        data = json.loads(result.stdout)
        status = data.get("status")

        # Match image_generation.py's precedent: accept both the "completed"/"failed"
        # vocabulary the CLI docs describe and the raw upstream "success"/"fail"
        # strings observed in practice, so this doesn't silently time out.
        if status in ("completed", "success"):
            return data["result_urls"][0]
        if status in ("failed", "fail"):
            raise RuntimeError(f"Video generation task {task_id} failed: {data.get('error')}")

    raise TimeoutError(f"Video generation task {task_id} did not complete within {max_attempts} attempts")


def download_video(url: str, output_path: Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    response = requests.get(url, timeout=60)
    response.raise_for_status()
    output_path.write_bytes(response.content)
    return output_path


def generate_video(
    video_prompt: str,
    output_path: Path,
    first_frame_url: str | None = None,
    reference_image_urls: list[str] | None = None,
    duration: int = 5,
    resolution: str = "720p",
    aspect_ratio: str = "9:16",
) -> Path:
    task_id = submit_video_task(
        video_prompt, first_frame_url, reference_image_urls, duration, resolution, aspect_ratio,
    )
    video_url = poll_video_task(task_id)
    return download_video(video_url, Path(output_path))


def trim_to_best_window(video_path: Path, output_path: Path, target_seconds: float = 5.0) -> Path:
    video_path = Path(video_path)
    output_path = Path(output_path)

    duration_result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)],
        check=True, capture_output=True, text=True,
    )
    duration = float(duration_result.stdout.strip())

    if duration <= target_seconds:
        shutil.copy(video_path, output_path)
        return output_path

    # Heuristic: take the middle window, skipping likely slow-start/slow-end motion
    # at the clip's edges. This is not motion-aware — a future improvement could use
    # scene/motion detection to pick a genuinely "best" window instead of the geometric middle.
    start_time = round((duration - target_seconds) / 2, 1)
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(video_path), "-ss", str(start_time), "-t", str(target_seconds),
         "-c:v", "libx264", "-c:a", "aac", str(output_path)],
        check=True, capture_output=True, text=True,
    )
    return output_path


def main(
    video_prompt: str,
    out: str,
    first_frame_url: str | None = None,
    reference_image_urls: list[str] | None = None,
    duration: int = 5,
    resolution: str = "720p",
    aspect_ratio: str = "9:16",
) -> None:
    generate_video(
        video_prompt, Path(out), first_frame_url, reference_image_urls, duration, resolution, aspect_ratio,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a POV scene video clip via Seedance 2.0 (kie.ai), anchored to a specific "
                     "shot's starting image (--first_frame_url, typically that shot's own scene image from "
                     "storyboard_generation.py). first_frame_url and reference_image_urls are mutually "
                     "exclusive on kie.ai's live endpoint — pass exactly one, never both. This pipeline's "
                     "sheet-driven architecture bakes character/prop/environment consistency into the "
                     "first-frame image itself, so first_frame_url alone is the correct and normal path; "
                     "reference_image_urls is only a fallback for the rare shot with no first-frame image."
    )
    parser.add_argument("prompt", help="Video prompt (must already include the negative-prompt closer)")
    parser.add_argument("--out", required=True, help="Output video file path")
    parser.add_argument(
        "--first_frame_url", default=None,
        help="Public URL of this shot's own starting image — the normal path for this pipeline",
    )
    parser.add_argument(
        "--reference_image_urls", nargs="*", default=None,
        help="Fallback only, mutually exclusive with --first_frame_url: character/environment sheet URLs",
    )
    parser.add_argument("--duration", type=int, default=5)
    parser.add_argument("--resolution", default="720p", choices=["480p", "720p"])
    parser.add_argument("--aspect_ratio", default="9:16")
    args = parser.parse_args()
    main(
        args.prompt, args.out, args.first_frame_url, args.reference_image_urls,
        args.duration, args.resolution, args.aspect_ratio,
    )
