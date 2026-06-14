"""
Update Asset Notes with real vision-based descriptions using Gemini 2.5 Flash.

Scans all resource library folders for images whose Asset Notes have filler
descriptions. For each flagged file, calls Gemini vision to extract visible
text (tool names, UI elements, headings, prices, metrics, etc.) and writes
a specific, searchable ai_description + AI Analysis section.

Usage:
    python3 update_asset_notes_vision.py
    python3 update_asset_notes_vision.py --dry-run
    python3 update_asset_notes_vision.py --limit 10
    python3 update_asset_notes_vision.py --dir 007_Resource_Library/Tools
"""
import os
import sys
import json
import base64
import argparse
import time
import re
import urllib.request
import urllib.error

WORKSPACE = "/Users/tonymacbook2025/Documents/Agent-OS"
RESOURCE_LIB = f"{WORKSPACE}/007_Resource_Library"

# Directories where image + Asset Note live in the SAME folder
SAME_DIR_FOLDERS = [
    f"{RESOURCE_LIB}/Tools",
    f"{RESOURCE_LIB}/Docs",
    f"{RESOURCE_LIB}/Tutorials",
    f"{RESOURCE_LIB}/Bookmarks",
]

# Visual_Assets: image here, note in Asset_Notes/
VISUAL_ASSETS_DIR = f"{RESOURCE_LIB}/Obsidian_Attachments/Visual_Assets"
ASSET_NOTES_DIR   = f"{RESOURCE_LIB}/Asset_Notes"

IMAGE_EXT = ('.png', '.jpg', '.jpeg', '.webp', '.gif', '.PNG', '.JPG', '.JPEG', '.WEBP')

FILLER_PATTERNS = [
    "likely a saved reference",
    "general visual reference",
    "it can be kept as a general visual",
    "this appears to be a screenshot of",
    "can be kept as a general",
    "for later comparison or idea capture",
]

VISION_PROMPT = """You are analyzing a screenshot saved by a content creator and digital entrepreneur.
Your job is to read ALL visible text in this image and describe exactly what it shows.

Focus on:
1. Every piece of visible text: tool names, headings, button labels, URLs, prices, metrics, dates, usernames
2. What platform or app is shown (TikTok, Instagram, YouTube, GitHub, a SaaS tool, a website, etc.)
3. What specific content is visible (e.g. "Spain Tour 2025 — 9 venue/date entries", "QWEN Image Edit: Camera Angle Control feature", "agentkit pricing page showing $29/mo plan")
4. Why the user likely saved it: tool to try, content idea, travel research, investment, tutorial, bookmark

Return ONLY a JSON object with exactly these two fields:
{
  "ai_description": "<one sentence: platform + specific visible content + why saved>",
  "analysis": "<2-4 sentences: what tool/page is shown, what text you can read, what it does, how it fits a content creator or entrepreneur workflow>"
}

Rules for ai_description:
- Be specific — name the tool/platform, include key visible text or numbers
- Bad: "Screenshot of a tool, likely a saved reference for research."
- Good: "TikTok creator dashboard showing 4.2M views and $1,847 earnings for @boardnomad — saved as revenue benchmark."
- Good: "QWEN Image Edit tool on Hugging Face showing Camera Angle Control feature — LLM-powered image editing API."
- Good: "GitHub repo 'agentkit-openai-platform' README with install instructions — bookmarked AI agent framework."

Output ONLY the JSON object. No markdown, no explanation."""


def is_filler(description):
    if not description:
        return True
    d = description.lower().strip()
    if len(d) < 60:
        return True
    return any(p in d for p in FILLER_PATTERNS)


def read_frontmatter_field(note_path, field):
    """Read a single field from YAML frontmatter."""
    try:
        with open(note_path, 'r', encoding='utf-8') as f:
            content = f.read()
        m = re.search(rf'^{field}:\s*["\']?(.*?)["\']?\s*$', content, re.MULTILINE)
        if m:
            return m.group(1).strip().strip('"').strip("'")
    except Exception:
        pass
    return None


def update_note(note_path, ai_description, analysis, dry_run=False):
    """Update ai_description in frontmatter and ## AI Analysis section."""
    try:
        with open(note_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return False, f"read error: {e}"

    # Update ai_description in frontmatter
    new_content = re.sub(
        r'^ai_description:.*$',
        f'ai_description: "{ai_description}"',
        content,
        flags=re.MULTILINE
    )

    # Update ## AI Analysis section (everything after it until next ## or end)
    analysis_pattern = r'(## AI Analysis\n).*?(?=\n##|\Z)'
    replacement = r'\g<1>' + analysis
    new_content = re.sub(analysis_pattern, replacement, new_content, flags=re.DOTALL)

    if dry_run:
        return True, "dry-run"

    try:
        with open(note_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True, "updated"
    except Exception as e:
        return False, f"write error: {e}"


def call_gemini_vision(image_path, api_key):
    """Call Gemini 2.5 Flash with the image and return (ai_description, analysis)."""
    ext = image_path.lower().rsplit('.', 1)[-1]
    mime_map = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png',
                'webp': 'image/webp', 'gif': 'image/gif'}
    mime_type = mime_map.get(ext, 'image/png')

    try:
        with open(image_path, 'rb') as f:
            b64_data = base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        return None, None, f"file read error: {e}"

    payload = {
        "contents": [{
            "parts": [
                {"text": VISION_PROMPT},
                {"inlineData": {"mimeType": mime_type, "data": b64_data}}
            ]
        }]
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )

    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                raw = result['candidates'][0]['content']['parts'][0]['text'].strip()
                # Strip markdown code fences if present
                raw = re.sub(r'^```(?:json)?\s*', '', raw)
                raw = re.sub(r'\s*```$', '', raw)
                parsed = json.loads(raw)
                return parsed.get('ai_description', ''), parsed.get('analysis', ''), None
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 10 * (attempt + 1)
                print(f"      Rate limited — waiting {wait}s...")
                time.sleep(wait)
            else:
                body = e.read().decode('utf-8', errors='replace')[:200]
                return None, None, f"HTTP {e.code}: {body}"
        except json.JSONDecodeError as e:
            return None, None, f"JSON parse error: {e} | raw: {raw[:100]}"
        except Exception as e:
            return None, None, f"error: {e}"

    return None, None, "max retries exceeded"


def collect_candidates(target_dir=None):
    """
    Returns list of (image_path, note_path) tuples for all images with filler notes.
    """
    candidates = []

    def scan_same_dir(folder):
        if not os.path.isdir(folder):
            return
        for fname in sorted(os.listdir(folder)):
            if not fname.lower().endswith(IMAGE_EXT):
                continue
            img_path = os.path.join(folder, fname)
            if not os.path.isfile(img_path):
                continue
            stem = os.path.splitext(fname)[0]
            note_path = os.path.join(folder, f"{stem}.md")
            if not os.path.exists(note_path):
                continue  # No note — skip (rename script handles those)
            desc = read_frontmatter_field(note_path, 'ai_description')
            if is_filler(desc):
                candidates.append((img_path, note_path))

    def scan_visual_assets():
        folder = VISUAL_ASSETS_DIR
        if not os.path.isdir(folder):
            return
        for fname in sorted(os.listdir(folder)):
            if not fname.lower().endswith(IMAGE_EXT):
                continue
            img_path = os.path.join(folder, fname)
            if not os.path.isfile(img_path):
                continue
            stem = os.path.splitext(fname)[0]
            note_path = os.path.join(ASSET_NOTES_DIR, f"{stem}.md")
            if not os.path.exists(note_path):
                continue
            desc = read_frontmatter_field(note_path, 'ai_description')
            if is_filler(desc):
                candidates.append((img_path, note_path))

    if target_dir:
        if target_dir == VISUAL_ASSETS_DIR or 'Visual_Assets' in target_dir:
            scan_visual_assets()
        else:
            scan_same_dir(target_dir)
    else:
        for folder in SAME_DIR_FOLDERS:
            scan_same_dir(folder)
        scan_visual_assets()

    return candidates


def main():
    parser = argparse.ArgumentParser(description="Update Asset Notes with real Gemini vision descriptions.")
    parser.add_argument('--dry-run', action='store_true', help="Show what would be updated without writing")
    parser.add_argument('--limit', type=int, default=0, help="Process at most N files (0 = all)")
    parser.add_argument('--dir', default='', help="Scan only this directory instead of all")
    args = parser.parse_args()

    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key and not args.dry_run:
        print("Error: GEMINI_API_KEY not set. Run: source ~/.env-secrets")
        sys.exit(1)

    target_dir = os.path.join(WORKSPACE, args.dir) if args.dir else None
    candidates = collect_candidates(target_dir)

    if args.limit:
        candidates = candidates[:args.limit]

    total = len(candidates)
    print(f"Found {total} Asset Notes with filler descriptions")
    if args.dry_run:
        print("DRY RUN — no files will be written\n")

    updated = 0
    failed = 0

    for i, (img_path, note_path) in enumerate(candidates):
        img_name = os.path.basename(img_path)
        print(f"[{i+1}/{total}] {img_name}")

        if args.dry_run:
            print(f"      would call vision on: {img_path}")
            print(f"      would update: {note_path}")
            continue

        ai_description, analysis, err = call_gemini_vision(img_path, api_key)

        if err or not ai_description:
            print(f"      FAILED: {err}")
            failed += 1
            time.sleep(0.5)
            continue

        print(f"      → {ai_description[:90]}")

        ok, msg = update_note(note_path, ai_description, analysis)
        if ok:
            updated += 1
        else:
            print(f"      NOTE UPDATE FAILED: {msg}")
            failed += 1

        time.sleep(0.5)

    print(f"\n=== Done ===")
    print(f"Updated: {updated}")
    print(f"Failed:  {failed}")
    print(f"Skipped (dry-run): {total if args.dry_run else 0}")


if __name__ == "__main__":
    main()
