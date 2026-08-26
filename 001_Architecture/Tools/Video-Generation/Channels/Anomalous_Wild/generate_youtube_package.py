#!/usr/bin/env python3
"""
generate_youtube_package.py — Anomalous Wild YouTube package generator.

Adapts Reimagined Realms' Phase 10 title/description/thumbnail formulas
(curiosity gap, search-intent description) to Anomalous Wild's science/
nature-documentary framing.

Thumbnail generation is a locked two-stage pipeline (template v2, locked
2026-08-24 after 0002_Mantis_Shrimp_Color_Vision — see
002_Channels/001_Anomalous-Wild/Anomalos_Wild__Thumbnail_Style.json):

  Stage 1 (base concept): gpt-image-2-text-to-image generates a textless,
  full-brightness photoreal close-up of the subject in its real environment.
  3 concepts, each with its own emotion/palette (intrigued/cool, alarmed/
  warm, awed/purple).

  Stage 2 (treatment edit): each stage-1 image is uploaded to Cloudinary
  (kie.ai image-to-image requires a public URL) and edited via
  gpt-image-2-image-to-image in a single pass that: darkens the background
  ~50% (keeping real scene detail, never flattened to a gradient), adds a
  neon glow rim-light around the subject (color varies per concept), and
  bakes in the headline text + a red curved arrow pointing at the specific
  anatomy tied to the video's hook fact. A base concept alone (concept_N.png)
  is NOT a finished thumbnail — concept_N_text.png (post stage-2) is what
  goes to Tony for review.

Headlines and the arrow target are NOT auto-derived from string templates —
Python string formatting produces weak curiosity copy (proven during the
Mantis Shrimp session). The orchestrating Claude session must draft 3 short
(2-6 word), lowercase, curiosity-gap headlines and identify the specific
anatomy the arrow should point to, then pass them via --headlines and
--arrow-target. This keeps headline quality at "Claude wrote it," not
"a template guessed it," while still requiring zero manual Tony review per
his 2026-08-24 approval of automatic headline generation.

Usage:
  python3 generate_youtube_package.py <production_folder> <subject> <hook_fact> \\
    --headlines "headline one|headline two|headline three" \\
    --arrow-target "the mantis shrimp's two eyestalks/eyes"

If --headlines/--arrow-target are omitted, falls back to template-generated
copy (lower quality — only use for a quick placeholder, not final delivery).
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

import cloudinary
import cloudinary.uploader
import requests
from dotenv import load_dotenv

load_dotenv(Path.home() / ".env-secrets")

KIE_CREATE_URL = "https://api.kie.ai/api/v1/jobs/createTask"
KIE_STATUS_URL = "https://api.kie.ai/api/v1/jobs/recordInfo"
BASE_MODEL = "gpt-image-2-text-to-image"
EDIT_MODEL = "gpt-image-2-image-to-image"

CLOUDINARY_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_KEY = os.getenv("CLOUDINARY_API_Key")
CLOUDINARY_SECRET = os.getenv("CLOUDINARY_API_Secret")

# (emotion, palette, glow_color) per concept — template v2 (2026-08-24):
# emotion/palette drive stage-1 mood, glow_color drives the stage-2 rim-light.
# Structural treatment (darken %, text style, arrow style) stays fixed across
# all 3 so the channel reads as consistent even though color varies.
THUMBNAIL_VARIATIONS = [
    ("intrigued", "cool blue-green", "cool cyan-teal"),
    ("alarmed", "warm amber-red", "warm amber-orange"),
    ("awed", "deep purple-teal", "vivid magenta-violet"),
]

MAX_TITLE_LEN = 100


def build_titles(subject: str, hook_fact: str) -> list[str]:
    titles = [
        f"This {subject.title()} {hook_fact.capitalize()}. Scientists Still Don't Know Why.",
        f"What Science Just Discovered About {subject.title()}",
        f"{subject.title()} Isn't What You Think. It's Something Stranger.",
    ]
    return [t[:MAX_TITLE_LEN] for t in titles]


def build_description(subject: str, chapters: list[tuple[str, str]]) -> str:
    chapter_lines = "\n".join(f"{ts} {label}" for ts, label in chapters)
    return f"""How does {subject} actually work?

Nature found a solution that seems almost impossible — and it evolved independently, more than once.

---

📍 Chapters
{chapter_lines}

---

This channel explores real science using illustrated diagrams and AI-generated visuals. All content is for educational and entertainment purposes.

#{subject.replace(' ', '')} #Science #Nature #Biology #Documentary #AnomalousWild
"""


def build_base_prompt(subject: str, emotion: str, palette: str) -> str:
    return (
        f"Close-up of {subject}, {palette} palette matching a {emotion} mood, "
        "dramatic lighting, deep vanishing point, photorealistic, cinematic, "
        "no text, no captions"
    )


def build_treatment_prompt(headline: str, arrow_target: str, glow_color: str) -> str:
    """Template v2 stage-2 edit prompt — locked 2026-08-24. Do not revert to
    a flat-gradient background (v1); Tony explicitly prefers the darkened
    real-photo look."""
    return (
        "Edit this photorealistic thumbnail image. Keep the exact same subject, "
        "pose, framing, and background scene/composition — do not replace the "
        "background with a solid color or gradient, and do not change what is "
        "depicted in it. Apply these edits on top:\n"
        "1. Darken the background only by roughly 50% (reduce its brightness/"
        "exposure) so it reads as noticeably dimmer and less busy, while its "
        "original detail, colors, and composition are still faintly visible "
        "underneath. Keep the animal subject itself bright, sharp, and in full "
        "clear focus — do not darken the subject.\n"
        f"2. Add a soft {glow_color} neon glow rim-light around the subject's "
        "silhouette, separating it cleanly from the darkened background, like "
        "dramatic wildlife-documentary thumbnail lighting.\n"
        f"3. Add bold, rounded, all-lowercase white headline text reading exactly "
        f"'{headline}' — large and highly readable, with a soft dark drop shadow. "
        "Place it in the top-left area of the frame with generous padding from "
        "the top and left edges (at least 8% of the frame), and make sure the "
        "text does not overlap or cover any part of the animal subject.\n"
        f"4. Add one single thick, bold red curved arrow that starts near the "
        f"bottom of the headline text and curves clearly to point directly at "
        f"{arrow_target} — the arrow must not cross through or overlap the "
        "headline text, and its tip must land precisely on the target feature, "
        "not on empty background or another body part.\n"
        "No other text, no captions, no watermarks, no logos, no extra graphics "
        "anywhere in the image including the corners. Clean, bold, mobile-"
        "readable composition."
    )


def upload_to_cloudinary(image_path: Path, public_id: str) -> str:
    cloudinary.config(
        cloud_name=CLOUDINARY_NAME,
        api_key=CLOUDINARY_KEY,
        api_secret=CLOUDINARY_SECRET,
        secure=True,
    )
    result = cloudinary.uploader.upload(
        str(image_path), public_id=public_id, overwrite=True, resource_type="image"
    )
    return result["secure_url"]


def _poll_and_download(task_id: str, headers: dict, out_path: Path) -> bool:
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
                    print(f"  ERROR: failed to download image (HTTP {r.status_code})")
                    return False
                out_path.parent.mkdir(parents=True, exist_ok=True)
                with open(out_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"  Saved: {out_path}")
                return True

            elif state == "fail" or flag in (2, 3):
                print(f"  ERROR: generation failed: {data_block}")
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


def generate_base_thumbnail(prompt: str, out_path: Path) -> bool:
    """Stage 1: textless photoreal base concept via gpt-image-2-text-to-image."""
    key = os.getenv("KIE_API_KEY")
    if not key:
        print("  ERROR: KIE_API_KEY not found in ~/.env-secrets")
        return False

    payload = {
        "model": BASE_MODEL,
        "input": {"prompt": prompt, "aspect_ratio": "16:9", "output_format": "png"},
    }
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    print(f"  Requesting base concept from {BASE_MODEL}...")
    try:
        resp = requests.post(KIE_CREATE_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"  ERROR: failed to submit base task: {e}")
        if "resp" in locals():
            print(f"  Response body: {resp.text}")
        return False

    data = resp.json()
    task_id = data.get("taskId") or data.get("data", {}).get("taskId")
    if not task_id:
        print(f"  ERROR: no taskId in response: {data}")
        return False

    print(f"  Base task: {task_id} — polling...")
    return _poll_and_download(task_id, headers, out_path)


def generate_treatment(prompt: str, image_url: str, out_path: Path) -> bool:
    """Stage 2: darken + glow + headline + arrow, applied to the stage-1 image."""
    key = os.getenv("KIE_API_KEY")
    if not key:
        print("  ERROR: KIE_API_KEY not found in ~/.env-secrets")
        return False

    payload = {
        "model": EDIT_MODEL,
        "input": {
            "prompt": prompt,
            "image_urls": [image_url],
            "aspect_ratio": "16:9",
            "output_format": "png",
        },
    }
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    print(f"  Requesting treatment edit from {EDIT_MODEL}...")
    try:
        resp = requests.post(KIE_CREATE_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"  ERROR: failed to submit treatment task: {e}")
        if "resp" in locals():
            print(f"  Response body: {resp.text}")
        return False

    data = resp.json()
    task_id = data.get("taskId") or data.get("data", {}).get("taskId")
    if not task_id:
        print(f"  ERROR: no taskId in response: {data}")
        return False

    print(f"  Treatment task: {task_id} — polling...")
    return _poll_and_download(task_id, headers, out_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("production_folder")
    parser.add_argument("subject")
    parser.add_argument("hook_fact")
    parser.add_argument(
        "--headlines",
        help="3 headlines separated by '|', one per concept. Claude should "
        "author these (2-6 words, lowercase, curiosity-gap) — see "
        "Anomalos_Wild__Thumbnail_Style.json headline_generation rules. "
        "Falls back to weak template copy if omitted.",
    )
    parser.add_argument(
        "--arrow-target",
        help="Description of the specific anatomy the arrow should point to "
        "(e.g. 'the mantis shrimp's two eyestalks/eyes'). Falls back to a "
        "generic 'the subject' target if omitted.",
    )
    args = parser.parse_args()

    production_root = Path(args.production_folder).resolve()
    subject, hook_fact = args.subject, args.hook_fact

    headlines = args.headlines.split("|") if args.headlines else None
    if headlines and len(headlines) != 3:
        sys.exit(f"--headlines must contain exactly 3 entries separated by '|', got {len(headlines)}")
    arrow_target = args.arrow_target or f"the {subject}'s most unusual feature"

    titles = build_titles(subject, hook_fact)
    description = build_description(subject, chapters=[("0:00", "Hook")])

    package_dir = production_root / "Package"
    package_dir.mkdir(parents=True, exist_ok=True)
    (package_dir / "YouTube_Package.md").write_text(
        "# Title Options\n\n" + "\n".join(f"{i+1}. {t}" for i, t in enumerate(titles)) +
        "\n\n# Description\n\n" + description
    )
    print(f"Wrote {package_dir / 'YouTube_Package.md'}")

    thumbnails_dir = package_dir / "Thumbnails"
    thumbnails_dir.mkdir(parents=True, exist_ok=True)
    failures = []

    for i, (emotion, palette, glow_color) in enumerate(THUMBNAIL_VARIATIONS, start=1):
        base_prompt = build_base_prompt(subject, emotion, palette)
        base_path = thumbnails_dir / f"concept_{i}.png"
        if not generate_base_thumbnail(base_prompt, base_path):
            failures.append(str(base_path))
            continue

        headline = headlines[i - 1] if headlines else f"the truth about {subject}"
        print(f"  Uploading {base_path.name} to Cloudinary for treatment edit...")
        image_url = upload_to_cloudinary(base_path, f"aw_thumb_{production_root.name}_{i}")

        treatment_prompt = build_treatment_prompt(headline, arrow_target, glow_color)
        text_path = thumbnails_dir / f"concept_{i}_text.png"
        if not generate_treatment(treatment_prompt, image_url, text_path):
            failures.append(str(text_path))

    if failures:
        sys.exit(f"  FAILED: {len(failures)} thumbnail stage(s) did not generate: {failures}")


if __name__ == "__main__":
    main()
