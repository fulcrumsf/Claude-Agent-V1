#!/usr/bin/env python3
"""
diagram_research_and_illustrate.py — Scientific Diagram sub-pipeline, steps 1-2.

Step 1: search Openverse (open-licensed images, already in the API stack)
        for a real reference image of the subject, so the illustration is
        anatomically grounded rather than pure AI invention.
Step 2: generate a clean illustration with an explicit no-text/no-label
        negative prompt (fixes the garbled-text diagram problem seen in the
        Bioluminescence Weapon video's anatomical diagram — see Report_Card.md).
        Labels are added later in a separate Remotion step (Tasks 5-6), NOT here.

Polling/download pattern matches the proven working
001_Architecture/Tools/Image-Generation/kie_image_gen.py (createTask +
recordInfo poll loop, exponential backoff, resultUrls extraction).
Model slug verified against Reimagined Realms' working batch_generate_images.py
and Global_Agent_Memory.md: gpt-image-2-text-to-image (NOT the "-1k" variant,
which is a pricing-tier catalog id, not the callable API model id, and 422s).

Usage:
  python3 diagram_research_and_illustrate.py <subject_query> <style_description> <output_dir>

Example:
  python3 diagram_research_and_illustrate.py "anglerfish esca illicium" \\
      "glowing neon-green bioluminescent line-art, deep-sea documentary style" \\
      002_Channels/001_Anomalous-Wild/.../scene_07/
"""
import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path.home() / ".env-secrets")

KIE_CREATE_URL = "https://api.kie.ai/api/v1/jobs/createTask"
KIE_STATUS_URL = "https://api.kie.ai/api/v1/jobs/recordInfo"
MODEL = "gpt-image-2-text-to-image"


def search_openverse_reference(query: str, out_path: Path) -> bool:
    """Search Openverse for a real reference image and save it. Returns True on success."""
    try:
        resp = requests.get(
            "https://api.openverse.org/v1/images/",
            params={"q": query, "license_type": "all-cc"},
            timeout=15,
        )
        resp.raise_for_status()
    except Exception as e:
        print(f"  WARNING: Openverse search failed for '{query}': {e}")
        return False

    results = resp.json().get("results", [])
    if not results:
        print(f"  No Openverse results for '{query}'")
        return False

    image_url = results[0]["url"]
    try:
        img = requests.get(image_url, stream=True, timeout=30)
        img.raise_for_status()
    except Exception as e:
        print(f"  WARNING: failed to download Openverse reference image: {e}")
        return False

    out_path.write_bytes(img.content)
    print(f"  Saved reference: {out_path} (source: {results[0].get('foreign_landing_url', image_url)})")
    return True


def generate_clean_illustration(subject_query: str, style_description: str, out_path: Path) -> bool:
    """Generate a clean, label-free illustration via kie.ai GPT-Image-2 and save it to out_path.

    Returns True on success, False on failure (never raises for API-level failures —
    callers should check the return value and flag to Tony rather than assume success).
    """
    key = os.getenv("KIE_API_KEY")
    if not key:
        print("  ERROR: KIE_API_KEY not found in ~/.env-secrets")
        return False

    prompt = (
        f"Scientific illustration of {subject_query}, {style_description}. "
        "NO TEXT, NO LABELS, NO WORDS, NO NUMBERS, NO CALLOUT LINES, NO ANNOTATION MARKS, "
        "no watermark. Clean anatomical illustration only."
    )
    payload = {
        "model": MODEL,
        "input": {
            "prompt": prompt,
            "aspect_ratio": "16:9",
            "output_format": "png",
        },
    }
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    print(f"  Requesting illustration from {MODEL}...")
    try:
        resp = requests.post(KIE_CREATE_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"  ERROR: failed to submit illustration task: {e}")
        if "resp" in locals():
            print(f"  Response body: {resp.text}")
        return False

    data = resp.json()
    task_id = data.get("taskId") or data.get("data", {}).get("taskId")
    if not task_id:
        print(f"  ERROR: no taskId in response: {data}")
        return False

    print(f"  Illustration task: {task_id} — polling with exponential backoff...")

    poll_interval = 5
    attempts = 0
    max_attempts = 60  # ~roughly 10+ minutes worst case with backoff

    while attempts < max_attempts:
        try:
            status_resp = requests.get(
                KIE_STATUS_URL, headers=headers, params={"taskId": task_id}, timeout=15
            )
            status_json = status_resp.json()
            data_block = status_json.get("data", {})
            state = data_block.get("state")
            flag = data_block.get("successFlag")

            if state == "success" or flag == 1:
                result_str = data_block.get("resultJson", "{}")
                img_url = None
                try:
                    result_obj = json.loads(result_str)
                    urls = result_obj.get("resultUrls", [])
                    img_url = urls[0] if urls else result_obj.get("url")
                except Exception:
                    pass
                if not img_url:
                    img_url = data_block.get("url")
                if not img_url:
                    print(f"  ERROR: task succeeded but no image URL found. Data: {data_block}")
                    return False

                print(f"  Generation complete, downloading from {img_url}...")
                r = requests.get(img_url, stream=True, timeout=30)
                if r.status_code != 200:
                    print(f"  ERROR: failed to download illustration image (HTTP {r.status_code})")
                    return False
                out_path.parent.mkdir(parents=True, exist_ok=True)
                with open(out_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"  Saved illustration: {out_path}")
                return True

            elif state == "fail" or flag in (2, 3):
                print(f"  ERROR: illustration generation failed: {data_block}")
                return False

            else:
                print(f"  state={state} flag={flag}... sleeping {poll_interval}s", flush=True)

        except Exception as e:
            print(f"  Polling warning: {e}", flush=True)

        time.sleep(poll_interval)
        attempts += 1
        if attempts % 3 == 0 and poll_interval < 20:
            poll_interval += 5

    print("  ERROR: polling timed out without a final state.")
    return False


def main():
    if len(sys.argv) < 4:
        sys.exit("Usage: diagram_research_and_illustrate.py <subject_query> <style_description> <output_dir>")
    subject_query, style_description, output_dir = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    output_dir.mkdir(parents=True, exist_ok=True)

    found = search_openverse_reference(subject_query, output_dir / "reference_image.jpg")
    if not found:
        print("  WARNING: no reference found — illustration will not be anatomically grounded. Flag to Tony.")

    ok = generate_clean_illustration(subject_query, style_description, output_dir / "illustration.png")
    if not ok:
        sys.exit("  FAILED: illustration generation did not complete. See errors above.")


if __name__ == "__main__":
    main()
