"""
Reimagined Realms — Batch Image Generation
Model: gpt-image-2-text-to-image via kie.ai
Usage: python3 batch_generate_images.py <production_folder>

Reads:  <production_folder>/Data/Beatmap.json       — clip filenames
        <production_folder>/Production/Shot_List.md  — image prompts
Saves:  <production_folder>/Images/C01_0.0s-3.8s.png ...

Skips clips that already exist — safe to re-run after partial failures.
"""

import os
import re
import sys
import json
import time
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv

MODEL = "gpt-image-2-text-to-image"

load_dotenv(Path.home() / ".env-secrets")
KIE_KEY = os.getenv("KIE_API_KEY")
if not KIE_KEY:
    sys.exit("ERROR: KIE_API_KEY not found in ~/.env-secrets")

HEADERS = {
    "Authorization": f"Bearer {KIE_KEY}",
    "Content-Type": "application/json",
}

# ── Clip map from Beatmap.json ─────────────────────────────────────────────────

def build_clip_map(production_root):
    data = json.loads((production_root / "Data" / "Beatmap.json").read_text())
    clip_map = {}
    all_subs = (sb for act in data["acts"] for sb in act["sub_beats"])
    for i, sb in enumerate(all_subs, start=1):
        start_s = round(sb["start_ms"] / 1000, 1)
        end_s   = round(sb["end_ms"]   / 1000, 1)
        clip_map[sb["clip"]] = f"C{i:02d}_{start_s}s-{end_s}s"
    return clip_map

# ── Image prompts from Shot_List.md ───────────────────────────────────────────

def parse_shot_list(production_root):
    text = (production_root / "Production" / "Shot_List.md").read_text()
    prompts = {}
    for block in re.split(r"(?=###\s+C\d+\s+\|)", text):
        m = re.match(r"###\s+(C\d+)\s+\|", block)
        if not m:
            continue
        clip_id = m.group(1)
        p = re.search(r"\*\*Image:\*\*\s*(.+?)(?:\n\*\*Video:|$)", block, re.DOTALL)
        if p:
            prompts[clip_id] = p.group(1).strip()
    return prompts

# ── Generate one image ─────────────────────────────────────────────────────────

def generate_image(prompt, output_path):
    payload = {
        "model": MODEL,
        "input": {
            "prompt": prompt,
            "aspect_ratio": "16:9",
            "output_format": "png",
            "quality": "standard",
        }
    }
    resp = requests.post(
        "https://api.kie.ai/api/v1/jobs/createTask",
        headers=HEADERS, json=payload, timeout=30
    )
    resp.raise_for_status()
    data = resp.json()
    task_id = data.get("taskId") or (data.get("data") or {}).get("taskId")
    if not task_id:
        raise RuntimeError(f"No taskId: {data}")

    status_url = f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}"
    poll_interval = 5
    for attempt in range(60):
        time.sleep(poll_interval)
        block = requests.get(status_url, headers=HEADERS, timeout=15).json().get("data", {})
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
            r = requests.get(url, stream=True, timeout=60)
            r.raise_for_status()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            return
        elif state == "fail" or flag in [2, 3]:
            raise RuntimeError(f"Generation failed: {block}")
        else:
            print(f"    [{attempt+1}] {state} — waiting {poll_interval}s", flush=True)
            if attempt > 0 and attempt % 3 == 0 and poll_interval < 20:
                poll_interval += 5

    raise RuntimeError("Timed out")

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Batch generate images for a Reimagined Realms production")
    parser.add_argument("production_folder", help="Path to production folder (e.g. .../0001_Pompeii_The_Escape)")
    parser.add_argument("--clips", nargs="+", metavar="CLIP",
                        help="Only generate these clip IDs (e.g. --clips C20 C21)")
    parser.add_argument("--overwrite", action="store_true",
                        help="Regenerate even if output already exists")
    args = parser.parse_args()

    production_root = Path(args.production_folder).resolve()
    if not production_root.exists():
        sys.exit(f"ERROR: Folder not found: {production_root}")

    only_clips = {c.upper() for c in args.clips} if args.clips else None

    clip_map = build_clip_map(production_root)
    prompts  = parse_shot_list(production_root)
    images_dir = production_root / "Images"
    images_dir.mkdir(parents=True, exist_ok=True)

    clips_sorted = sorted(prompts.keys(), key=lambda c: int(c[1:]))
    if only_clips:
        clips_sorted = [c for c in clips_sorted if c.upper() in only_clips]
    total = len(clips_sorted)
    print(f"\n=== Image Batch — {production_root.name} | {total} clips | {MODEL} ===\n")

    success, failed = 0, []

    for clip_id in clips_sorted:
        stem = clip_map.get(clip_id)
        if not stem:
            print(f"  SKIP {clip_id} — not in beatmap")
            continue

        out = images_dir / f"{stem}.png"
        if out.exists() and not args.overwrite:
            print(f"  SKIP {clip_id} → {out.name} (exists)")
            success += 1
            continue

        prompt = prompts[clip_id]
        print(f"  [{clip_id}] → {out.name}")
        print(f"    {prompt[:100]}{'...' if len(prompt) > 100 else ''}")

        try:
            generate_image(prompt, out)
            print(f"    ✓ Saved", flush=True)
            success += 1
        except Exception as e:
            print(f"    ✗ FAILED: {e}", flush=True)
            failed.append(clip_id)

        time.sleep(2)

    print(f"\n=== Done: {success}/{total} succeeded ===")
    if failed:
        print(f"Failed: {', '.join(failed)} — re-run to retry")
    else:
        print("All images generated successfully!")

if __name__ == "__main__":
    main()
