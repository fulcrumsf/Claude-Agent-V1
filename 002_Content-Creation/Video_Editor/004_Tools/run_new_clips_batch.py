"""
Batch generator for new_clips_prompts.json — handles both video (Kie.ai) and image (Fal.ai Flux Pro).

Usage:
  python3 004_Tools/run_new_clips_batch.py <prompts.json> [--priority critical|high|medium|all] [--type video|image|all]

Examples:
  python3 004_Tools/run_new_clips_batch.py 002_Channels/001_Anomalous-Wild/001_Bioluminescence-Weapon/new_clips_prompts.json --priority critical
  python3 004_Tools/run_new_clips_batch.py 002_Channels/001_Anomalous-Wild/001_Bioluminescence-Weapon/new_clips_prompts.json --priority high --type video
  python3 004_Tools/run_new_clips_batch.py 002_Channels/001_Anomalous-Wild/001_Bioluminescence-Weapon/new_clips_prompts.json --type image

Skips any entry where the output file already exists.

Quality rules enforced automatically (from Video 001 report card):
  - Video entries with "requires_reference": true must have a "reference_image" path that exists.
    Missing reference = WARNING printed + entry skipped (use --force-no-ref to override).
  - Image entries with "is_diagram": true have the scientific negative prompt
    auto-appended if not already present:
    "no text, no labels, no callout lines, no arrows, no annotation marks"
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

HOME_SECRETS = Path.home() / ".env-secrets"
load_dotenv(HOME_SECRETS)

KIE_API_KEY = os.getenv("KIE_API_KEY")
# .env key is "FAL.AI_API_KEY" — dotenv loads it with the dot
FAL_API_KEY = os.getenv("FAL.AI_API_KEY")

# ── Kie.ai constants ──────────────────────────────────────────────────────────
KIE_POLL_INTERVAL = 20        # seconds between polls
KIE_MAX_POLLS     = 90        # 30 minutes max per clip

# ── Fal.ai constants ──────────────────────────────────────────────────────────
FAL_FLUX_ENDPOINT = "https://fal.run/fal-ai/flux-pro"
FAL_TIMEOUT_S     = 120       # Flux Pro sync call timeout

# Map aspect_ratio string → fal.ai image_size value
FAL_SIZE_MAP = {
    "16:9":  "landscape_16_9",
    "9:16":  "portrait_16_9",
    "1:1":   "square_hd",
    "4:3":   "landscape_4_3",
    "3:4":   "portrait_4_3",
    "21:9":  "landscape_21_9",
}


# ── Video generation (Kie.ai) ─────────────────────────────────────────────────
# Veo3:  POST /api/v1/veo/generate  + poll /api/v1/veo/record-info
# Kling: POST /api/v1/jobs/createTask + poll /api/v1/jobs/recordInfo

KIE_HEADERS = lambda: {
    "Authorization": f"Bearer {KIE_API_KEY}",
    "Content-Type": "application/json",
}


def _extract_video_url(data: dict) -> str:
    """Pull video URL from a completed kie.ai task data block."""
    result_str = data.get("resultJson", "{}")
    try:
        obj = json.loads(result_str) if isinstance(result_str, str) else result_str
        urls = obj.get("resultUrls", [])
        if urls:
            return urls[0]
        if obj.get("url"):
            return obj["url"]
    except Exception:
        pass
    # Veo3 fallback
    response = data.get("response", {}) or {}
    urls = response.get("resultUrls", [])
    return urls[0] if urls else (data.get("url") or data.get("videoUrl") or "")


def _generate_veo3(entry: dict, output_path: Path) -> bool:
    """Generate via Veo3 endpoint (/api/v1/veo/generate)."""
    prompt       = entry["video_prompt"]
    model        = entry.get("model", "veo3_fast")
    aspect_ratio = entry.get("aspect_ratio", "16:9")

    resp = requests.post(
        "https://api.kie.ai/api/v1/veo/generate",
        headers=KIE_HEADERS(),
        json={"model": model, "prompt": prompt, "aspect_ratio": aspect_ratio, "generationType": "TEXT_2_VIDEO"},
        timeout=30,
    )
    if not resp.ok:
        print(f"  ✗ Queue failed: {resp.status_code} — {resp.text[:200]}", flush=True)
        return False

    data    = resp.json()
    nested  = data.get("data") or {}
    task_id = data.get("taskId") or nested.get("taskId")
    if not task_id:
        print(f"  ✗ No taskId: {data}", flush=True)
        return False

    print(f"    Task: {task_id}", flush=True)
    poll_url = f"https://api.kie.ai/api/v1/veo/record-info?taskId={task_id}"

    for attempt in range(KIE_MAX_POLLS):
        time.sleep(KIE_POLL_INTERVAL)
        try:
            block = requests.get(poll_url, headers=KIE_HEADERS(), timeout=15).json().get("data") or {}
            flag  = block.get("successFlag")
            if flag == 1:
                vid_url = _extract_video_url(block)
                if not vid_url:
                    print(f"  ✗ No URL in response: {block}", flush=True)
                    return False
                dl = requests.get(vid_url, timeout=120)
                dl.raise_for_status()
                output_path.write_bytes(dl.content)
                print(f"  ✓ Saved: {output_path} ({output_path.stat().st_size/1024/1024:.1f} MB)", flush=True)
                return True
            elif flag == -1:
                print(f"  ✗ Failed: {block.get('response', {}).get('failedMsg', 'unknown')}", flush=True)
                return False
            else:
                print(f"    [{(attempt+1)*KIE_POLL_INTERVAL}s] pending...", flush=True)
        except Exception as e:
            print(f"    Poll error: {e}", flush=True)

    print(f"  ✗ Timed out", flush=True)
    return False


def _generate_kling(entry: dict, output_path: Path) -> bool:
    """Generate via Kling 3.0 endpoint (/api/v1/jobs/createTask)."""
    prompt       = entry["video_prompt"]
    aspect_ratio = entry.get("aspect_ratio", "16:9")
    duration     = str(entry.get("duration_s", 8))

    resp = requests.post(
        "https://api.kie.ai/api/v1/jobs/createTask",
        headers=KIE_HEADERS(),
        json={
            "model": "kling-3.0/video",
            "input": {
                "prompt": prompt,
                "sound": False,
                "duration": duration,
                "aspect_ratio": aspect_ratio,
                "mode": "pro",
                "multi_shots": False,
            },
        },
        timeout=30,
    )
    if not resp.ok:
        print(f"  ✗ Queue failed: {resp.status_code} — {resp.text[:200]}", flush=True)
        return False

    body    = resp.json()
    nested  = body.get("data") or {}
    task_id = body.get("taskId") or nested.get("taskId")
    if not task_id:
        print(f"  ✗ No taskId: {body}", flush=True)
        return False

    print(f"    Task: {task_id}", flush=True)
    poll_url = f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}"
    start    = time.time()
    interval = 8

    while time.time() - start < KIE_MAX_POLLS * KIE_POLL_INTERVAL:
        time.sleep(interval)
        interval = min(interval + 4, 30)
        try:
            data  = requests.get(poll_url, headers=KIE_HEADERS(), timeout=20).json().get("data", {})
            state = data.get("state")
            flag  = data.get("successFlag")
            if state == "success" or flag == 1:
                vid_url = _extract_video_url(data)
                if not vid_url:
                    print(f"  ✗ No URL: {data}", flush=True)
                    return False
                dl = requests.get(vid_url, timeout=120)
                dl.raise_for_status()
                output_path.write_bytes(dl.content)
                print(f"  ✓ Saved: {output_path} ({output_path.stat().st_size/1024/1024:.1f} MB)", flush=True)
                return True
            elif state == "fail" or flag in [2, 3]:
                print(f"  ✗ Task failed: {data}", flush=True)
                return False
            else:
                print(f"    [{int(time.time()-start)}s] state={state}", flush=True)
        except Exception as e:
            print(f"    Poll error: {e}", flush=True)

    print(f"  ✗ Timed out", flush=True)
    return False


_DIAGRAM_NEGATIVE_PROMPT = (
    "no text, no labels, no callout lines, no arrows, no annotation marks, "
    "no letters, no numbers, no words, no captions"
)


def _check_reference_image(entry: dict, force: bool = False) -> bool:
    """
    If entry has requires_reference=true, verify reference_image path exists.
    Returns False (and prints warning) if the reference is missing and force=False.
    """
    if not entry.get("requires_reference"):
        return True
    ref = entry.get("reference_image", "")
    if not ref:
        print(
            f"  ⚠ REFERENCE MISSING: {entry['scene_id']} has requires_reference=true "
            f"but no reference_image path set.",
            flush=True,
        )
        print(
            f"    Fix: add a 'reference_image' path to this entry, or set "
            f"'requires_reference': false to skip the check.",
            flush=True,
        )
        return force
    if not Path(ref).exists():
        print(
            f"  ⚠ REFERENCE FILE NOT FOUND: {entry['scene_id']} → {ref}",
            flush=True,
        )
        print(
            f"    Save the reference image to that path before generating, "
            f"or use --force-no-ref to skip the check.",
            flush=True,
        )
        return force
    print(f"  ✓ Reference image verified: {Path(ref).name}", flush=True)
    return True


def _enforce_diagram_negative_prompt(entry: dict) -> dict:
    """
    For image entries with is_diagram=true, auto-append the scientific negative
    prompt if it isn't already present. Returns the (possibly modified) entry.
    """
    if not entry.get("is_diagram"):
        return entry
    prompt = entry.get("image_prompt", "")
    neg_key = "no text"
    if neg_key not in prompt.lower():
        entry = dict(entry)  # don't mutate the original
        entry["image_prompt"] = prompt.rstrip(" ,") + ", " + _DIAGRAM_NEGATIVE_PROMPT
        print(
            f"  ℹ Diagram negative prompt auto-appended for: {entry['scene_id']}",
            flush=True,
        )
    return entry


def generate_video(entry: dict, force_no_ref: bool = False) -> bool:
    output_folder = Path(entry["output_folder"])
    output_folder.mkdir(parents=True, exist_ok=True)
    output_path = output_folder / "video.mp4"

    if output_path.exists():
        print(f"  ✓ Already exists, skipping: {entry['scene_id']}", flush=True)
        return True

    if not _check_reference_image(entry, force=force_no_ref):
        return False

    model = entry.get("model", "kling_v2")
    print(f"\n  → Queuing: {entry['scene_id']} [{entry.get('priority','?')}] ({model})", flush=True)
    print(f"    {entry['video_prompt'][:90]}...", flush=True)

    if "veo" in model.lower():
        return _generate_veo3(entry, output_path)
    else:
        return _generate_kling(entry, output_path)


# ── Image generation (Fal.ai Flux Pro) ───────────────────────────────────────

def generate_image(entry: dict) -> bool:
    entry = _enforce_diagram_negative_prompt(entry)

    output_folder = Path(entry["output_folder"])
    output_folder.mkdir(parents=True, exist_ok=True)
    output_path = output_folder / "image.png"

    if output_path.exists():
        print(f"  ✓ Already exists, skipping: {entry['scene_id']}")
        return True

    prompt       = entry["image_prompt"]
    aspect_ratio = entry.get("aspect_ratio", "16:9")
    image_size   = FAL_SIZE_MAP.get(aspect_ratio, "landscape_16_9")

    print(f"\n  → Generating image: {entry['scene_id']} [{entry.get('priority','?')}]")
    print(f"    {prompt[:90]}...")

    headers = {
        "Authorization": f"Key {FAL_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "prompt": prompt,
        "image_size": image_size,
        "num_inference_steps": 28,
        "guidance_scale": 3.5,
        "num_images": 1,
        "safety_tolerance": "2",
        "output_format": "png",
    }

    try:
        resp = requests.post(FAL_FLUX_ENDPOINT, headers=headers, json=payload, timeout=FAL_TIMEOUT_S)
    except requests.exceptions.Timeout:
        print(f"  ✗ Fal.ai request timed out after {FAL_TIMEOUT_S}s")
        return False

    if not resp.ok:
        print(f"  ✗ Fal.ai error: {resp.status_code} — {resp.text[:300]}")
        return False

    data = resp.json()
    images = data.get("images", [])
    if not images:
        print(f"  ✗ No images in response: {data}")
        return False

    img_url = images[0].get("url")
    if not img_url:
        print(f"  ✗ No URL in image result: {images[0]}")
        return False

    print(f"    Downloading: {img_url[:70]}...")
    dl = requests.get(img_url, timeout=60)
    dl.raise_for_status()
    with open(output_path, "wb") as f:
        f.write(dl.content)
    size_kb = output_path.stat().st_size / 1024
    print(f"  ✓ Saved: {output_path} ({size_kb:.0f} KB)")
    return True


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tools/run_new_clips_batch.py <prompts.json> [--priority critical|high|medium|all] [--type video|image|all]")
        sys.exit(1)

    prompts_file = Path(sys.argv[1])
    if not prompts_file.exists():
        print(f"File not found: {prompts_file}")
        sys.exit(1)

    # Parse flags
    priority_filter  = "all"
    type_filter      = "all"
    force_no_ref     = "--force-no-ref" in sys.argv

    if "--priority" in sys.argv:
        idx = sys.argv.index("--priority")
        priority_filter = sys.argv[idx + 1]

    if "--type" in sys.argv:
        idx = sys.argv.index("--type")
        type_filter = sys.argv[idx + 1]

    entries = json.loads(prompts_file.read_text())

    # Filter by priority
    if priority_filter != "all":
        entries = [e for e in entries if e.get("priority") == priority_filter]

    # Filter by type
    if type_filter != "all":
        entries = [e for e in entries if e.get("generation_type") == type_filter]

    video_entries = [e for e in entries if e.get("generation_type") == "video"]
    image_entries = [e for e in entries if e.get("generation_type") == "image"]

    print(f"\n=== New Clips Batch Generator ===")
    print(f"Priority filter : {priority_filter}")
    print(f"Type filter     : {type_filter}")
    print(f"Video entries   : {len(video_entries)}")
    print(f"Image entries   : {len(image_entries)}")
    if force_no_ref:
        print(f"⚠ --force-no-ref active: reference image checks bypassed")
    print()

    # Validate API keys
    if video_entries and not KIE_API_KEY:
        print("ERROR: KIE_API_KEY not set in .env — cannot generate videos")
        sys.exit(1)
    if image_entries and not FAL_API_KEY:
        print("ERROR: FAL.AI_API_KEY not set in .env — cannot generate images")
        sys.exit(1)

    results: list = []

    # ── Videos first (sequential to spare the M3 Max) ─────────────────────
    for entry in video_entries:
        ok = generate_video(entry, force_no_ref=force_no_ref)
        results.append((entry["scene_id"], ok))

    # ── Images after videos ────────────────────────────────────────────────
    for entry in image_entries:
        ok = generate_image(entry)
        results.append((entry["scene_id"], ok))

    total   = len(results)
    failed  = [sid for sid, ok in results if not ok]
    success = total - len(failed)
    print(f"\n=== Done ===")
    print(f"Generated: {success}/{total}")
    if failed:
        print(f"Failed   : {', '.join(failed)}")


if __name__ == "__main__":
    main()
