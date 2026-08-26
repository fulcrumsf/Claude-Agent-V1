"""Thin wrapper around kie.ai's unified Market API (/api/v1/jobs/createTask +
/api/v1/jobs/recordInfo) for models the @felores/kie-cli npm package doesn't
wrap yet (e.g. bytedance/seedance-2-mini, grok-imagine/upscale).

Not a CLI replacement -- kie-cli covers the vast majority of models and is
kept as the default per Tool-Manager. This exists only for the specific gap
models, so it can be extended with one function per model as new gaps show
up, without taking on maintenance of a full CLI.

Docs: https://docs.kie.ai/market/quickstart.md
"""
import json
import os
import time
from pathlib import Path

import requests

BASE_URL = "https://api.kie.ai/api/v1"


def _headers() -> dict:
    api_key = os.environ.get("KIE_API_KEY")
    if not api_key:
        raise ValueError("KIE_API_KEY is missing from the environment (source ~/.env-secrets first)")
    return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}


def create_task(model: str, input_params: dict, callback_url: str | None = None) -> str:
    """Submits a task to the unified Market createTask endpoint. Returns taskId."""
    payload = {"model": model, "input": input_params}
    if callback_url:
        payload["callBackUrl"] = callback_url

    resp = requests.post(f"{BASE_URL}/jobs/createTask", headers=_headers(), json=payload, timeout=30)
    if not resp.ok:
        raise RuntimeError(f"createTask failed for model={model}: {resp.status_code} {resp.text}")
    body = resp.json()
    # kie.ai returns HTTP 200 even for API-level errors (insufficient credits, invalid
    # params, etc.) -- the real status is in the "code" field, and "data" is null on
    # failure. Check code before assuming data.taskId exists.
    if body.get("code") != 200:
        raise RuntimeError(f"createTask rejected for model={model}: {body.get('msg')} (code={body.get('code')})")
    task_id = (body.get("data") or {}).get("taskId")
    if not task_id:
        raise RuntimeError(f"createTask returned no taskId for model={model}: {body}")
    return task_id


def poll_task(task_id: str, poll_interval_s: float = 5.0, max_wait_s: float = 900.0) -> dict:
    """Polls the unified recordInfo endpoint until state is success/fail. Returns the resultJson dict."""
    elapsed = 0.0
    while elapsed < max_wait_s:
        resp = requests.get(f"{BASE_URL}/jobs/recordInfo", headers=_headers(), params={"taskId": task_id}, timeout=15)
        resp.raise_for_status()
        data = resp.json().get("data", {})
        state = data.get("state")

        if state == "success":
            return json.loads(data.get("resultJson") or "{}")
        if state == "fail":
            raise RuntimeError(f"Task {task_id} failed: {data}")

        time.sleep(poll_interval_s)
        elapsed += poll_interval_s

    raise TimeoutError(f"Task {task_id} did not complete within {max_wait_s}s")


def download(url: str, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    resp = requests.get(url, stream=True, timeout=60)
    resp.raise_for_status()
    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    return output_path


# ---- Gap-model functions (add one per model as new gaps show up) ----

def generate_seedance_mini(
    prompt: str,
    output_path: Path,
    first_frame_url: str | None = None,
    resolution: str = "480p",
    duration: int = 5,
    generate_audio: bool = False,
) -> Path:
    """bytedance/seedance-2-mini -- not wrapped by kie-cli as of 2026-08-17."""
    input_params = {
        "prompt": prompt,
        "resolution": resolution,
        "duration": duration,
        "generate_audio": generate_audio,
    }
    if first_frame_url:
        input_params["first_frame_url"] = first_frame_url

    task_id = create_task("bytedance/seedance-2-mini", input_params)
    result = poll_task(task_id)
    urls = result.get("resultUrls") or []
    if not urls:
        raise RuntimeError(f"Task {task_id} succeeded but returned no resultUrls: {result}")
    return download(urls[0], output_path)


def upscale_grok_video(task_id: str, output_path: Path) -> Path:
    """grok-imagine/upscale -- DO NOT USE for non-Grok clips. Despite the docs prose
    suggesting it accepts a taskId from any Kie AI video model, live-tested
    2026-08-17 against a real Seedance-2-mini task_id and it hard-rejects with
    {"code":422,"msg":"record result error"}. Kept here only in case a future
    Grok-generated clip needs upscaling; for Seedance output use
    upscale_topaz_video() instead."""
    result_task_id = create_task("grok-imagine/upscale", {"task_id": task_id})
    result = poll_task(result_task_id)
    urls = result.get("resultUrls") or []
    if not urls:
        raise RuntimeError(f"Upscale task {result_task_id} succeeded but returned no resultUrls: {result}")
    return download(urls[0], output_path)


def upscale_topaz_video(video_url: str, output_path: Path, upscale_factor: str = "2") -> Path:
    """topaz/video-upscale -- takes any hosted video_url directly (not scoped to
    Kie AI-generated content, unlike grok-imagine/upscale). Confirmed 2026-08-17
    via https://docs.kie.ai/market/topaz/video-upscale.md. Max input size 50MB,
    mp4/mov/mkv. upscale_factor: '1', '2', or '4' (doubles/quadruples width+height)."""
    task_id = create_task("topaz/video-upscale", {"video_url": video_url, "upscale_factor": upscale_factor})
    result = poll_task(task_id)
    urls = result.get("resultUrls") or []
    if not urls:
        raise RuntimeError(f"Upscale task {task_id} succeeded but returned no resultUrls: {result}")
    return download(urls[0], output_path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="kie.ai Market API gap-model wrapper")
    sub = parser.add_subparsers(dest="command", required=True)

    p_mini = sub.add_parser("seedance_mini", help="Generate video via bytedance/seedance-2-mini")
    p_mini.add_argument("prompt")
    p_mini.add_argument("output")
    p_mini.add_argument("--first_frame_url", default=None)
    p_mini.add_argument("--resolution", default="480p", choices=["480p", "720p"])
    p_mini.add_argument("--duration", type=int, default=5)
    p_mini.add_argument("--generate_audio", action="store_true")

    p_upscale = sub.add_parser("grok_upscale", help="Upscale any Kie AI-generated video via grok-imagine/upscale")
    p_upscale.add_argument("task_id")
    p_upscale.add_argument("output")

    args = parser.parse_args()

    if args.command == "seedance_mini":
        out = generate_seedance_mini(
            args.prompt, Path(args.output), args.first_frame_url, args.resolution, args.duration, args.generate_audio
        )
        print(f"Saved {out}")
    elif args.command == "grok_upscale":
        out = upscale_grok_video(args.task_id, Path(args.output))
        print(f"Saved {out}")
