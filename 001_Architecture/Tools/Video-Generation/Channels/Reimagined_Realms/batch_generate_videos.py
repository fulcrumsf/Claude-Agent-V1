"""
Reimagined Realms — Batch Video Generation (image-to-video)
Models: Seedance 1.5 Pro (≤12s) / Seedance 2.0 (>12s) via kie.ai
Usage: python3 batch_generate_videos.py <production_folder> [--clips C1 C3 C5] [--audio] [--overwrite]

Reads:  <production_folder>/Images/C01_0.0s-3.8s.png    — reference frames
        <production_folder>/Production/Shot_List.md       — video prompts
        <production_folder>/Data/Beatmap.json             — clip filenames + target_final_duration_s
Saves:  <production_folder>/Video_Clips/C01_0.0s-3.8s.mp4 ...

Generation duration = ceil(target_final_duration_s + 1s padding), min 4s.
Model selection: Seedance 1.5 Pro if generate_duration ≤ 12s, Seedance 2.0 if >12s.
Hard rule: beatmap clips should never exceed 8s final duration (ideal 3–6s).

Skips clips that already exist — safe to re-run after partial failures.
Use --overwrite to force regeneration of existing clips.
Images are uploaded to Cloudinary to get public URLs (required by kie.ai).

Flags:
  --audio      Enable ambient/environmental audio (foley, wind, crowd, etc.)
               Doubles generation cost: $0.075/s vs $0.0375/s at 1080p.
               No dialogue is generated — environmental sound only.
  --overwrite  Regenerate clips even if output file already exists.

API parameter reference (confirmed from https://kie.ai/seedance-1-5-pro):
  input_urls: [image_url]  — reference frame (array, 0-2 images)
  prompt: str
  aspect_ratio: "16:9"
  resolution: "1080p"
  duration: int (seconds)
  nsfw_checker: bool
  enable_audio: bool       — ambient audio on/off (with-audio pricing tier)
"""

import os
import re
import sys
import json
import math
import time
import argparse
import subprocess
import requests
from pathlib import Path
from dotenv import load_dotenv

# Model IDs
MODEL_1_5 = "bytedance/seedance-1.5-pro"          # max 12s generation
MODEL_2_0 = "bytedance/seedance-2"                  # max 15s generation

# Duration rules
PADDING_S    = 1   # seconds added to every clip's final duration before generating
MIN_GEN_S    = 4   # Seedance minimum supported duration
MAX_1_5_S    = 12  # Seedance 1.5 Pro maximum — above this, switch to 2.0

RESOLUTION = "1080p"
AUDIO      = False   # overridden by --audio flag; doubles cost ($0.075/s vs $0.0375/s)

load_dotenv(Path.home() / ".env-secrets")
KIE_KEY           = os.getenv("KIE_API_KEY")
CLOUDINARY_NAME   = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_KEY    = os.getenv("CLOUDINARY_API_Key")
CLOUDINARY_SECRET = os.getenv("CLOUDINARY_API_Secret")

if not KIE_KEY:
    sys.exit("ERROR: KIE_API_KEY not found in ~/.env-secrets")
if not all([CLOUDINARY_NAME, CLOUDINARY_KEY, CLOUDINARY_SECRET]):
    sys.exit("ERROR: Cloudinary credentials missing from ~/.env-secrets")

KIE_HEADERS = {
    "Authorization": f"Bearer {KIE_KEY}",
    "Content-Type": "application/json",
}

# ── Clip map from Beatmap.json ─────────────────────────────────────────────────

def build_clip_map(production_root):
    """Returns (clip_map, duration_map) — stem names and final target durations keyed by clip ID."""
    data = json.loads((production_root / "Data" / "Beatmap.json").read_text())
    clip_map, duration_map = {}, {}
    i = 1
    for act in data["acts"]:
        for sb in act["sub_beats"]:
            start_s = round(sb["start_ms"] / 1000, 1)
            end_s   = round(sb["end_ms"]   / 1000, 1)
            clip_id = sb["clip"]
            clip_map[clip_id]     = f"C{i:02d}_{start_s}s-{end_s}s"
            duration_map[clip_id] = sb["target_final_duration_s"]
            i += 1
    return clip_map, duration_map


def generation_params(target_final_s):
    """Compute (model, generate_duration) for a clip given its target final duration."""
    generate_s = min(max(MIN_GEN_S, math.ceil(target_final_s + PADDING_S)), MAX_1_5_S)
    model = MODEL_2_0 if generate_s > MAX_1_5_S else MODEL_1_5
    return model, generate_s

# ── Video prompts from Shot_List.md ───────────────────────────────────────────

def parse_video_prompts(production_root):
    text = (production_root / "Production" / "Shot_List.md").read_text()
    prompts = {}
    for block in re.split(r"(?=###\s+C\d+\s+\|)", text):
        m = re.match(r"###\s+(C\d+)\s+\|", block)
        if not m:
            continue
        clip_id = m.group(1)
        p = re.search(r"\*\*Video:\*\*\s*(.+?)(?:\n###|$)", block, re.DOTALL)
        if p:
            prompts[clip_id] = p.group(1).strip()
    return prompts

# ── Upload image to Cloudinary ─────────────────────────────────────────────────

def upload_to_cloudinary(image_path, public_id):
    import cloudinary
    import cloudinary.uploader
    cloudinary.config(
        cloud_name=CLOUDINARY_NAME,
        api_key=CLOUDINARY_KEY,
        api_secret=CLOUDINARY_SECRET,
        secure=True,
    )
    result = cloudinary.uploader.upload(
        str(image_path),
        public_id=public_id,
        overwrite=True,
        resource_type="image",
    )
    return result["secure_url"]

# ── Generate one video ─────────────────────────────────────────────────────────

def generate_video(image_url, prompt, output_path, model, duration, enable_audio=False):
    payload = {
        "model": model,
        "input": {
            "prompt": prompt,
            "input_urls": [image_url],
            "aspect_ratio": "16:9",
            "resolution": RESOLUTION,
            "duration": duration,
            "nsfw_checker": True,
            "enable_audio": enable_audio,
        }
    }
    resp = requests.post(
        "https://api.kie.ai/api/v1/jobs/createTask",
        headers=KIE_HEADERS, json=payload, timeout=30
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 200:
        raise RuntimeError(f"API error {data.get('code')}: {data.get('msg')}")
    task_id = (data.get("data") or {}).get("taskId")
    if not task_id:
        raise RuntimeError(f"No taskId: {data}")

    print(f"    taskId={task_id}", flush=True)
    status_url = f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}"
    poll_interval = 10

    for attempt in range(90):
        time.sleep(poll_interval)
        block = requests.get(status_url, headers=KIE_HEADERS, timeout=15).json().get("data", {})
        state, flag = block.get("state"), block.get("successFlag")

        if state == "success" or flag == 1:
            try:
                result = json.loads(block.get("resultJson", "{}"))
                url = (result.get("resultUrls") or [None])[0] or result.get("url")
            except Exception:
                url = None
            url = url or block.get("url")
            if not url:
                raise RuntimeError(f"No URL in result: {block}")
            r = requests.get(url, stream=True, timeout=120)
            r.raise_for_status()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            size_mb = output_path.stat().st_size / 1_000_000
            print(f"    ✓ Saved {output_path.name} ({size_mb:.1f} MB)", flush=True)
            return
        elif state == "fail" or flag in [2, 3]:
            raise RuntimeError(f"Generation failed: {block}")
        else:
            print(f"    [{attempt+1}] {state} — waiting {poll_interval}s", flush=True)
            if attempt > 5 and poll_interval < 20:
                poll_interval = 20

    raise RuntimeError("Timed out")

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Batch generate videos for a Reimagined Realms production")
    parser.add_argument("production_folder", help="Path to production folder (e.g. .../0001_Pompeii_The_Escape)")
    parser.add_argument("--clips", nargs="+", help="Only process specific clips (e.g. --clips C1 C2 C3)")
    parser.add_argument("--audio", action="store_true", help="Enable ambient environmental audio (doubles cost: $0.075/s vs $0.0375/s)")
    parser.add_argument("--overwrite", action="store_true", help="Regenerate clips even if output file already exists")
    args = parser.parse_args()
    enable_audio = args.audio

    production_root = Path(args.production_folder).resolve()
    if not production_root.exists():
        sys.exit(f"ERROR: Folder not found: {production_root}")

    clip_map, duration_map = build_clip_map(production_root)
    prompts  = parse_video_prompts(production_root)
    images_dir     = production_root / "Images"
    video_clips_dir = production_root / "Video_Clips"
    video_clips_dir.mkdir(parents=True, exist_ok=True)

    clips_sorted = sorted(prompts.keys(), key=lambda c: int(c[1:]))
    if args.clips:
        clips_sorted = [c for c in clips_sorted if c in args.clips]

    total = len(clips_sorted)
    prod_name = production_root.name
    audio_label = "with-audio" if enable_audio else "no-audio"
    overwrite_label = " | --overwrite" if args.overwrite else ""
    print(f"\n=== Video Batch — {prod_name} | {total} clips | {audio_label}{overwrite_label} ===\n")

    success, failed = 0, []

    for clip_id in clips_sorted:
        stem = clip_map.get(clip_id)
        if not stem:
            print(f"  SKIP {clip_id} — not in beatmap")
            continue

        image_path = images_dir / f"{stem}.png"
        out_path   = video_clips_dir / f"{stem}.mp4"

        if out_path.exists() and not args.overwrite:
            print(f"  SKIP {clip_id} → {out_path.name} (exists)")
            success += 1
            continue

        if not image_path.exists():
            print(f"  SKIP {clip_id} — reference image not found: {image_path.name}")
            failed.append(clip_id)
            continue

        final_s = duration_map.get(clip_id, 5.0)
        model, gen_s = generation_params(final_s)
        model_label = "Seedance-2.0" if model == MODEL_2_0 else "Seedance-1.5"

        prompt = prompts[clip_id]
        print(f"  [{clip_id}] → {out_path.name} | {model_label} | generate={gen_s}s → trim={final_s}s")
        print(f"    Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")

        try:
            public_id = f"reimagined_realms/{prod_name.lower()}/{stem}"
            print(f"    Uploading to Cloudinary...", flush=True)
            image_url = upload_to_cloudinary(image_path, public_id)
            generate_video(image_url, prompt, out_path, model=model, duration=gen_s, enable_audio=enable_audio)
            # Verify actual output duration meets target
            probe = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", str(out_path)],
                capture_output=True, text=True
            )
            actual_s = float(probe.stdout.strip()) if probe.stdout.strip() else 0
            if actual_s < final_s:
                print(f"    ⚠ Output is {actual_s:.2f}s — under target {final_s}s — needs Seedance 2.0 retry", flush=True)
                failed.append(clip_id)
            else:
                success += 1
        except Exception as e:
            print(f"    ✗ FAILED: {e}", flush=True)
            failed.append(clip_id)

        time.sleep(3)

    print(f"\n=== Done: {success}/{total} succeeded ===")
    if failed:
        print(f"Failed: {', '.join(failed)} — re-run to retry")
    else:
        print("All videos generated successfully!")

if __name__ == "__main__":
    main()
