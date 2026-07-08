#!/usr/bin/env python3
"""
generate_youtube_package.py — Anomalous Wild YouTube package generator.

Adapts Reimagined Realms' Phase 10 title/description/thumbnail formulas
(curiosity gap, search-intent description, no-text thumbnail with emotion-
matched palette) to Anomalous Wild's science/nature-documentary framing.

Usage:
  python3 generate_youtube_package.py <production_folder> <subject> <hook_fact>
Thumbnail generation reuses the proven kie.ai createTask + recordInfo poll
loop from diagram_research_and_illustrate.py's generate_clean_illustration()
(same endpoints, same model slug, same polling/backoff pattern), adapted for
photorealistic dramatic thumbnails (16:9, no no-text-avoidance requirement —
build_thumbnail_prompt() already asks for "no text, no captions" itself).

Usage:
  python3 generate_youtube_package.py <production_folder> <subject> <hook_fact>
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

# (emotion, palette) variations for the 3 thumbnail concepts — chosen to give
# a nature/science documentary channel a spread of moods: curious/investigative,
# alarmed/dramatic, and awed/wonder.
THUMBNAIL_VARIATIONS = [
    ("intrigued", "cool blue-green"),
    ("alarmed", "warm amber-red"),
    ("awed", "deep purple-teal"),
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


def build_thumbnail_prompt(subject: str, emotion: str, palette: str) -> str:
    return (
        f"Close-up of {subject}, {palette} palette matching a {emotion} mood, "
        "dramatic lighting, deep vanishing point, photorealistic, cinematic, "
        "no text, no captions"
    )


def generate_thumbnail(prompt: str, out_path: Path) -> bool:
    """Generate one thumbnail via kie.ai GPT-Image-2 and save it to out_path.

    Mirrors diagram_research_and_illustrate.py's generate_clean_illustration()
    createTask + recordInfo poll loop (same endpoints, same model slug, same
    exponential backoff), adapted for 16:9 photorealistic thumbnails instead
    of label-free diagrams. Returns True on success, False on failure — never
    raises for API-level failures so callers can flag to Tony rather than
    assume success.
    """
    key = os.getenv("KIE_API_KEY")
    if not key:
        print("  ERROR: KIE_API_KEY not found in ~/.env-secrets")
        return False

    payload = {
        "model": MODEL,
        "input": {
            "prompt": prompt,
            "aspect_ratio": "16:9",
            "output_format": "png",
        },
    }
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    print(f"  Requesting thumbnail from {MODEL}...")
    try:
        resp = requests.post(KIE_CREATE_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"  ERROR: failed to submit thumbnail task: {e}")
        if "resp" in locals():
            print(f"  Response body: {resp.text}")
        return False

    data = resp.json()
    task_id = data.get("taskId") or data.get("data", {}).get("taskId")
    if not task_id:
        print(f"  ERROR: no taskId in response: {data}")
        return False

    print(f"  Thumbnail task: {task_id} — polling with exponential backoff...")

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
                    print(f"  ERROR: failed to download thumbnail image (HTTP {r.status_code})")
                    return False
                out_path.parent.mkdir(parents=True, exist_ok=True)
                with open(out_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"  Saved thumbnail: {out_path}")
                return True

            elif state == "fail" or flag in (2, 3):
                print(f"  ERROR: thumbnail generation failed: {data_block}")
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
        sys.exit("Usage: generate_youtube_package.py <production_folder> <subject> <hook_fact>")
    production_root = Path(sys.argv[1]).resolve()
    subject, hook_fact = sys.argv[2], sys.argv[3]

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
    for i, (emotion, palette) in enumerate(THUMBNAIL_VARIATIONS, start=1):
        prompt = build_thumbnail_prompt(subject, emotion, palette)
        out_path = thumbnails_dir / f"concept_{i}.png"
        ok = generate_thumbnail(prompt, out_path)
        if not ok:
            failures.append(str(out_path))

    if failures:
        sys.exit(f"  FAILED: {len(failures)} thumbnail(s) did not generate: {failures}")


if __name__ == "__main__":
    main()
