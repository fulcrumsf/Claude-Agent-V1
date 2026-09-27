import os
import sys
import json
import re
import base64
import argparse
import urllib.request
import urllib.error
import time
import shutil
import hashlib
from datetime import datetime

try:  # macOS framework Python frequently ships without a usable CA bundle for urllib
    import certifi
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())
except ImportError:
    pass

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_VISION_MODEL", "qwen/qwen3.5-flash-02-23")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

WORKSPACE_ROOT = "/Users/tonymacbook2025/Documents/Agent-OS"
RESOURCE_LIBRARY = os.path.join(WORKSPACE_ROOT, "007_Resource_Library")
UNDETERMINED_DIR = os.path.join(RESOURCE_LIBRARY, "Undetermined")
RENAME_LOG = os.path.join(RESOURCE_LIBRARY, "_Ingest_Rename_Log.md")
DIRECTORY_MD = os.path.join(RESOURCE_LIBRARY, "Directory.md")

_TAG_BULLET_RE = re.compile(r"^\*\s+\*\*([^:*]+):\*\*\s*(.*)$")


def _parse_bullet_section(lines, start_idx):
    """Parse '*   **Name:** description' bullets starting after start_idx,
    stopping at the next '## ' header. A bullet's description can continue
    across following lines (indented sub-bullets, wrapped text) - anything
    that isn't itself a new top-level bullet or blank gets appended, so a
    multi-line definition is never silently truncated to its first line."""
    out = {}
    current = None
    for l in lines[start_idx + 1:]:
        if l.startswith("## "):
            break
        m = _TAG_BULLET_RE.match(l.strip())
        if m:
            current = m.group(1).strip()
            out[current] = m.group(2).strip()
        elif current and l.strip():
            out[current] = (out[current] + " " + l.strip()).strip()
    return out


def load_tag_vocabulary():
    """Parse Directory.md's '## Tag Vocabulary' section - the single source
    of truth every note's tags must be drawn from (1-2 per note). Mirrors
    retag_and_retitle.py's parsing so both scripts stay in sync automatically
    if Directory.md changes - never hardcode a second copy of this list."""
    text = open(DIRECTORY_MD, encoding="utf-8").read()
    lines = text.split("\n")
    start = next((i for i, l in enumerate(lines) if l.strip() == "## Tag Vocabulary"), None)
    if start is None:
        raise RuntimeError("Directory.md '## Tag Vocabulary' section missing")
    return _parse_bullet_section(lines, start)


def _canonical_tag(t, tags):
    """Case-insensitive match against the vocabulary - the model sometimes
    returns a valid tag with the wrong casing."""
    low = str(t).strip().lower()
    for real in tags:
        if real.lower() == low:
            return real
    return None

# Filename stems that are non-descriptive — AI sometimes produces these when it can't read an image
BAD_NAME_PATTERNS = [
    # Generic/ambiguous names
    r"^screenshot",
    r"^clip-\d+$",
    r"^clip$",
    r"^image$",
    r"^image-[0-9a-z]",
    r"^photo$",
    r"^picture$",
    r"^background$",
    r"^banner$",
    r"^example$",
    r"^untitled$",
    r"^chatgpt-image",
    r"^img-",
    r"^img$",
    r"^file$",
    r"^[0-9a-f]{8,}$",
    r"^[a-z0-9]{20,}$",

    # Timestamps and dimensions
    r"[0-9]{8,}",
    r"[0-9]+x[0-9]+",

    # UUID fragments (Midjourney job IDs)
    r"[0-9a-f]{8}-[0-9a-f]{4}",

    # TikTok navigation bar OCR dumps
    r"explore-following",
    r"-live-explore",
    r"-live-stem",
    r"-stem-explore",

    # Garbled OCR prefix tokens
    r"^ive-",
    r"^itt-",
    r"^ial-",
    r"^ifk-",
    r"^i[0-9]+-",
]

# Folders the vision model should never be offered as a destination:
# Archive is manual-only ("files are manually moved"), Videos is a special
# per-video subfolder structure (not a flat image category), and Undetermined
# is the existing low-confidence fallback bucket, not something to pick.
_FOLDER_EXCLUDE = {"Archive", "Videos", "Undetermined"}


def load_folder_vocabulary():
    """Parse Directory.md's '## Folder Layout & Descriptions' section - the
    single source of truth for what real category folders exist. Mirrors
    retag_and_retitle.py's parse_directory() so both scripts stay in sync
    automatically when Directory.md changes - never hardcode a second list."""
    text = open(DIRECTORY_MD, encoding="utf-8").read()
    lines = text.split("\n")
    start = next((i for i, l in enumerate(lines)
                  if l.strip() == "## Folder Layout & Descriptions"), None)
    if start is None:
        raise RuntimeError("Directory.md '## Folder Layout & Descriptions' section missing")
    raw = _parse_bullet_section(lines, start)
    # Folder Layout also carries informational asides ("Image storage (...)",
    # "Visual review tool (...)") that aren't real folders - keep only
    # bullets that are an actual directory on disk.
    return {name: desc for name, desc in raw.items()
            if name not in _FOLDER_EXCLUDE and os.path.isdir(os.path.join(RESOURCE_LIBRARY, name))}


VALID_FOLDERS = list(load_folder_vocabulary().keys())


def is_bad_name(name):
    """Return True if the name is non-descriptive and should not become a note."""
    stem = name.lower().replace(" ", "-")
    return any(re.match(p, stem) for p in BAD_NAME_PATTERNS)


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def build_library_index():
    """Scan the Resource Library for dedup: image hashes, note URLs, taken names per folder."""
    img_hashes = {}   # sha256 -> relative note/image path
    note_urls = {}     # normalized url -> note path
    taken = set()      # (category, stem) already used
    for root, dirs, files in os.walk(RESOURCE_LIBRARY):
        dirs[:] = [d for d in dirs if d not in ("OpenAI_History", "graphify-out", ".git")]
        cat = os.path.relpath(root, RESOURCE_LIBRARY).split(os.sep)[0]
        for fn in files:
            fp = os.path.join(root, fn)
            low = fn.lower()
            if low.endswith((".png", ".jpg", ".jpeg", ".webp", ".gif")):
                try:
                    img_hashes.setdefault(_sha256(fp), os.path.relpath(fp, RESOURCE_LIBRARY))
                except OSError:
                    pass
            elif low.endswith(".md") and not fn.startswith("_"):
                taken.add((cat, os.path.splitext(fn)[0].lower()))
                try:
                    t = open(fp, encoding="utf-8", errors="ignore").read()
                except OSError:
                    continue
                m = re.search(r'^url:\s*"?([^"\n]+?)"?\s*$', t, re.M)
                if m:
                    note_urls.setdefault(m.group(1).strip().rstrip("/").lower(),
                                         os.path.relpath(fp, RESOURCE_LIBRARY))
    return img_hashes, note_urls, taken


def log_rename(original, new_name, category):
    """Append one entry to the ingest rename log."""
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    line = f"- `{original}` → `{new_name}` | category: {category} | {date_str}\n"
    with open(RENAME_LOG, "a") as f:
        f.write(line)

def build_prompt():
    # Plain .replace(), not .format() - the JSON example below is full of
    # literal { } that .format() would misparse as placeholders.
    tag_vocab = load_tag_vocabulary()
    tag_lines = "\n".join(f"- {name}: {desc}" for name, desc in tag_vocab.items())
    folder_vocab = load_folder_vocabulary()
    folder_lines = "\n".join(f"- {name}: {desc}" for name, desc in folder_vocab.items())
    return (PROMPT_TEMPLATE
            .replace("{{TAG_VOCABULARY}}", tag_lines)
            .replace("{{FOLDER_VOCABULARY}}", folder_lines))


PROMPT_TEMPLATE = """
You are a semantic knowledge extractor analyzing screenshots and images for a knowledge vault.

## PRIMARY RULE: Name based on WHAT this image is ABOUT, not what text happens to be visible.

Ask yourself: "What is this image ACTUALLY about?" — not "What random text is visible?"

## IGNORE these completely when generating the filename and description:
- App navigation bars (TikTok: Live / STEM / Explore / Following / Shop / Saved / Inbox)
- Instagram/YouTube UI chrome (Home / Search / Reels / Profile tabs)
- Status bars, timestamps, notification icons, carrier info
- Browser chrome, sidebars, menu buttons, decorative text
- Watermarks, repeated interface elements, bottom nav bars
- Any text that is part of the app shell, NOT the content being saved

## FOCUS on:
- The central subject, tool name, concept, or message
- The PRIMARY VISUAL CONTENT (what fills most of the screen)
- What the user INTENDED to save — the actual topic, not the wrapper
- Named entities: tool names, brand names, concepts, techniques

## Naming examples (CRITICAL — follow this logic):
BAD: "Live-Stem-Explore-Following-Shop" (TikTok nav bar OCR dump)
GOOD: "AI-Landing-Page-Vibe-Coding-Tips" (what the TikTok video is actually about)

BAD: "Home-Search-Notifications-Messages" (Twitter nav OCR dump)
GOOD: "OpenAI-Memory-System-Thread" (what the tweet/thread is actually about)

BAD: "File-Edit-View-Help" (menu bar OCR dump)
GOOD: "YouTube-Analytics-Growth-Dashboard" (what the screenshot actually shows)

## Categories — locked list, nothing outside it

`category` must be EXACTLY one of these (never invent a folder, never use an
old/renamed name like "Project_Ideas" — it no longer exists):

{{FOLDER_VOCABULARY}}

Only use "Undetermined" (a separate fallback, not one of the categories above)
if the image is blurry, has no context, or lacks actionable content.

## DO NOT FABRICATE — hard rule

You may only state what is VISIBLE in the image or reconstructable from visible text.

- **URL**: only fill `url` if the address is actually shown — including when it is
  obfuscated to dodge a link filter (e.g. `mesh3d [.gallery]` → `https://mesh3d.gallery`,
  `github dot com slash foo` → `https://github.com/foo`). Reconstructing shown text is fine.
  **Never guess or synthesize a URL that is not in the frame.** A confident wrong URL is
  worse than none. Not every image has one — if it isn't shown, leave `url` as "" and move on;
  that is a completely normal, unremarkable outcome, not something to flag.
- **ai_description / summary**: describe only what the frame shows or verifiably states.
  If it references a tool/repo/site whose PURPOSE is not shown, say "purpose not shown in
  frame" — do NOT invent what it does.
- If unsure whether something is real vs inferred, mark it inferred in the description.

## Tag Vocabulary — locked list, nothing outside it

`tags` carries 1 minimum, 2 maximum values, every one drawn EXACTLY from this list —
never invent a tag, never use a different casing or wording:

{{TAG_VOCABULARY}}

A second tag is never required or expected by default — one good tag beats two where
the second is a stretch. Only add a second tag when it is clearly, specifically
supported by what's actually shown; if unsure it applies, leave it off.

Output ONLY a raw JSON object (no markdown ```json blocks):

{
    "category": "Tools",
    "content_type": "tool-doc",
    "form": "github-repo",
    "title_case_name": "Title-Case-With-Dashes",
    "ai_description": "2-3 sentences describing the PRIMARY SUBJECT: what tool/concept/idea is shown, what it does (only if shown), why someone would save it. Do NOT describe the app chrome or navigation. Do NOT invent capabilities that are not visible.",
    "url": "",
    "tags": ["OneOrTwoTagsFromTheVocabularyAbove"]
}

Naming rules:
- title_case_name: Title-Case-With-Dashes, semantic meaning only (e.g. Suno-AI-Music-Platform, ComfyUI-Workflow-Tutorial)
- NO nav bar text, NO UI labels, NO timestamps, NO dimension numbers in the name

Field rules:
- content_type: ONE of bookmark|api-doc|tool-doc|tutorial|model-doc|prompt|reference|case-study|script|workflow|project-idea|design-inspiration|personal|research|doc . Never "extracted-knowledge".
- form: ONE of saas-tool|desktop-app|browser-extension|github-repo|open-source-project|api-service|youtube-video|tiktok|article|social-thread|prompt|workflow-diagram|channel-study|market-research|model-spec|design-reference|project-idea|dataset|paper|other . This is WHAT THE THING IS.
- url: the source / product / repo URL ONLY if it is visible in the frame (obfuscated-but-reconstructable counts). Use "" otherwise — do NOT synthesize a plausible URL, and do not treat a missing URL as anything to flag or follow up on.
- If it is or references a GitHub repo: form MUST be "github-repo". Set `url` to the repo URL only if shown, otherwise "".
- tags: 1-2 values EXACTLY from the Tag Vocabulary list above — see that section, not this one.
"""

MAX_IMAGE_DIMENSION = 2000  # px, longest edge


def _prepare_image_b64(image_path, mime_type):
    """Base64-encode an image for the vision API, downscaling first if its
    longest edge exceeds MAX_IMAGE_DIMENSION. Full-resolution phone/monitor
    screenshots (multi-MB) were timing out against OpenRouter's request
    timeout and then tripping OpenAI's per-request rate limit on fallback -
    every retry sent the same oversized payload, so the file never ingested.
    Resizing keeps the request fast and small without losing anything the
    model needs to read on-screen text."""
    from PIL import Image
    import io

    with open(image_path, "rb") as f:
        raw = f.read()

    with Image.open(io.BytesIO(raw)) as img:
        if max(img.size) <= MAX_IMAGE_DIMENSION:
            return base64.b64encode(raw).decode("utf-8")
        img = img.copy()
        img.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION), Image.LANCZOS)
        buf = io.BytesIO()
        save_format = "PNG" if mime_type == "image/png" else "JPEG"
        if save_format == "JPEG" and img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.save(buf, format=save_format)
        return base64.b64encode(buf.getvalue()).decode("utf-8")


def process_image(image_path):
    ext = image_path.lower().split('.')[-1]
    if ext in ('jpg', 'jpeg'):
        mime_type = "image/jpeg"
    elif ext == 'png':
        mime_type = "image/png"
    elif ext == 'webp':
        mime_type = "image/webp"
    else:
        return None

    try:
        b64_data = _prepare_image_b64(image_path, mime_type)
    except Exception as e:
        print(f"Error reading {image_path}: {e}")
        return None

    if OPENROUTER_KEY:
        try:
            payload = {
                "model": OPENROUTER_MODEL,
                "response_format": {"type": "json_object"},
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": build_prompt()},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{b64_data}"
                                }
                            }
                        ]
                    }
                ]
            }
            api_url = "https://openrouter.ai/api/v1/chat/completions"
            req = urllib.request.Request(
                api_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {OPENROUTER_KEY}",
                    "HTTP-Referer": "https://openrouter.ai/",
                    "X-OpenRouter-Title": "Agent-OS ChatGPT Ingest",
                }
            )
            attempts = 0
            max_attempts = 5
            while True:
                try:
                    with urllib.request.urlopen(req, timeout=20) as response:
                        result = json.loads(response.read().decode('utf-8'))
                        raw = result['choices'][0]['message']['content'].strip()
                        return json.loads(raw)
                except urllib.error.HTTPError as e:
                    if e.code != 429 or attempts >= max_attempts - 1:
                        raise
                    retry_after = e.headers.get("Retry-After")
                    delay = 2 ** attempts
                    if retry_after:
                        try:
                            delay = max(delay, int(retry_after))
                        except Exception:
                            pass
                    attempts += 1
                    print(f"OpenRouter rate-limited for {image_path}; retrying in {delay}s ({attempts}/{max_attempts})...")
                    time.sleep(delay)
        except Exception as e:
            print(f"OpenRouter vision failed for {image_path}: {e}. Falling back to OpenAI if available...")

    if OPENAI_KEY:
        try:
            payload = {
                "model": "gpt-4o-mini",
                "response_format": {"type": "json_object"},
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": build_prompt()},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{b64_data}"
                                }
                            }
                        ]
                    }
                ]
            }
            api_url = "https://api.openai.com/v1/chat/completions"
            req = urllib.request.Request(
                api_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {OPENAI_KEY}"
                }
            )
            attempts = 0
            max_attempts = 5
            while True:
                try:
                    with urllib.request.urlopen(req, timeout=20) as response:
                        result = json.loads(response.read().decode('utf-8'))
                        raw = result['choices'][0]['message']['content'].strip()
                        return json.loads(raw)
                except urllib.error.HTTPError as e:
                    if e.code != 429 or attempts >= max_attempts - 1:
                        raise
                    retry_after = e.headers.get("Retry-After")
                    delay = 2 ** attempts
                    if retry_after:
                        try:
                            delay = max(delay, int(retry_after))
                        except Exception:
                            pass
                    attempts += 1
                    print(f"OpenAI rate-limited for {image_path}; retrying in {delay}s ({attempts}/{max_attempts})...")
                    time.sleep(delay)
        except Exception as e:
            print(f"OpenAI fallback failed for {image_path}: {e}")
            return None

    return None

def finalize_and_write_note(file_path, data, img_hashes, note_urls, taken):
    """Given a source image still sitting at `file_path` and a fully-populated
    `data` dict (category/title_case_name/ai_description/tags/content_type/
    form/url - whether that came straight from process_image()'s vision call,
    or from a caller like Ingest-Visualizer that pre-filled some/all fields
    itself), apply every shared finalization rule - tag canonicalization,
    URL validation, bad-name/Undetermined routing, dedup-safe naming - then
    move the image and write the note. This is the ONE place that behavior
    lives; both this script's own CLI loop and any other tool ingesting
    images must call this rather than keep a second copy of the template.

    Mutates img_hashes/note_urls/taken in place (same dicts/sets threaded
    through a whole batch, so later files in the same run see earlier ones).

    Returns a dict: {"status": "written"|"undetermined"|"dup",
    plus status-specific keys: "dup_of" (dup), "path" (undetermined/written),
    "category"/"name"/"img_filename" (written)}."""
    category = data.get("category", "Undetermined")
    title_case_name = data.get("title_case_name", "Untitled")
    ai_description = data.get("ai_description", "No description available.")
    raw_tags = data.get("tags", [])
    vocab = load_tag_vocabulary()
    tags = [c for c in (_canonical_tag(t, vocab) for t in raw_tags) if c][:2]
    if not tags:
        tags = ["Misc"]
    content_type = data.get("content_type", "reference") or "reference"
    form = data.get("form", "other") or "other"
    url = (data.get("url", "") or "").strip()

    # Guardrail: never emit the deprecated placeholder type
    if content_type in ("extracted-knowledge", "", None):
        content_type = "reference"

    # Anti-fabrication guardrail: only keep a URL that looks real AND was returned
    # as an actual address. If the model slipped a guessed non-URL string in,
    # drop it rather than presenting it as a verified link.
    if url and not re.match(r"^https?://[^\s]+\.[^\s]+", url):
        url = ""

    # GitHub mirror rule: classification only (form), never an injected tag -
    # "GitHub" is already in the tag vocabulary if the model judges it topically relevant.
    if "github.com" in url or form == "github-repo":
        form = "github-repo"

    # --- dedup 2: same source URL already saved ---
    if url:
        key = url.strip().rstrip("/").lower()
        if key in note_urls:
            return {"status": "dup", "dup_of": note_urls[key]}

    # Validate that the AI returned a descriptive name — reject generic/hash names
    if is_bad_name(title_case_name):
        category = "Undetermined"

    ext = file_path.lower().split('.')[-1]
    if ext == "jpeg":
        ext = "jpg"

    if category == "Undetermined" or category not in VALID_FOLDERS:
        # Move image to Undetermined/, no markdown
        dest_img_path = os.path.join(UNDETERMINED_DIR, f"{title_case_name}.{ext}")
        c = 1
        while os.path.exists(dest_img_path):
            dest_img_path = os.path.join(UNDETERMINED_DIR, f"{title_case_name}-{c}.{ext}")
            c += 1
        shutil.move(file_path, dest_img_path)
        return {"status": "undetermined", "path": dest_img_path}

    # --- dedup 3: one free name for BOTH the note and its co-located image ---
    base = title_case_name
    name = base
    n = 1
    soft_dup = False
    while (os.path.exists(os.path.join(RESOURCE_LIBRARY, category, f"{name}.md"))
           or os.path.exists(os.path.join(RESOURCE_LIBRARY, category, f"{name}.{ext}"))
           or (category, name.lower()) in taken):
        soft_dup = True
        name = f"{base}-{n}"
        n += 1
    taken.add((category, name.lower()))
    if soft_dup and "possible-duplicate" not in tags:
        tags = tags + ["possible-duplicate"]

    new_img_filename = f"{name}.{ext}"
    dest_img_path = os.path.join(RESOURCE_LIBRARY, category, new_img_filename)
    shutil.move(file_path, dest_img_path)
    try:
        digest = _sha256(dest_img_path)
        img_hashes[digest] = os.path.relpath(dest_img_path, RESOURCE_LIBRARY)
    except OSError:
        pass
    log_rename(os.path.basename(file_path), f"{category}/{new_img_filename}", category)

    md_path = os.path.join(RESOURCE_LIBRARY, category, f"{name}.md")

    # Resolve human title
    human_title = name.replace("-", " ")

    yaml_tags = "\n".join([f"  - {t}" for t in tags])
    date_str = datetime.now().strftime("%Y-%m-%d")
    url_line = f'url: "{url}"\n' if url else ""

    md_content = f"""---
title: "{human_title}"
type: {content_type}
category: {category.lower()}
form: {form}
summary: "{ai_description.replace('"', "'")}"
{url_line}tags:
{yaml_tags}
original_filename: "{os.path.basename(file_path)}"
created: {date_str}
---

![[{new_img_filename}]]

## Summary
{ai_description}
"""
    with open(md_path, "w") as f:
        f.write(md_content)

    return {"status": "written", "category": category, "name": name, "img_filename": new_img_filename}


def main():
    parser = argparse.ArgumentParser(description="Semantically ingest images (Tools, Tutorials, etc.) using OpenRouter or OpenAI Vision.")
    parser.add_argument("path", help="Path to a single image or a directory of images.")
    parser.add_argument("--limit", type=int, default=None,
                        help="Process only the first N images found (for reviewing a small batch before running the rest).")
    args = parser.parse_args()

    target_path = args.path

    if not OPENROUTER_KEY and not OPENAI_KEY:
        print("Error: OPENROUTER_API_KEY and OPENAI_API_KEY are both missing.")
        sys.exit(1)

    os.makedirs(UNDETERMINED_DIR, exist_ok=True)
    for folder in VALID_FOLDERS:
        os.makedirs(os.path.join(RESOURCE_LIBRARY, folder), exist_ok=True)

    files_to_process = []
    if os.path.isfile(target_path):
        files_to_process.append(target_path)
    elif os.path.isdir(target_path):
        for f in os.listdir(target_path):
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                files_to_process.append(os.path.join(target_path, f))
    else:
        print(f"Error: {target_path} is not a valid file or directory.")
        sys.exit(1)

    if args.limit is not None:
        files_to_process = files_to_process[:args.limit]

    print(f"Found {len(files_to_process)} images to process.")
    print("Indexing library for dedup...")
    img_hashes, note_urls, taken = build_library_index()

    for i, file_path in enumerate(files_to_process):
        print(f"[{i+1}/{len(files_to_process)}] Processing {os.path.basename(file_path)}...")

        # --- dedup 1: byte-identical image already in the library ---
        try:
            digest = _sha256(file_path)
        except OSError:
            digest = None
        if digest and digest in img_hashes:
            print(f"   -> [DUP] exact-duplicate image of {img_hashes[digest]} — skipped")
            continue

        data = process_image(file_path)
        if not data:
            print("   -> Failed to extract semantic data.")
            continue

        result = finalize_and_write_note(file_path, data, img_hashes, note_urls, taken)
        if result["status"] == "dup":
            print(f"   -> [DUP] same URL as {result['dup_of']} — skipped")
            continue
        elif result["status"] == "undetermined":
            print(f"   -> [UNDETERMINED] Moved to {result['path']}")
        else:
            print(f"   -> [EXTRACTED] Created {result['category']}/{result['name']}.md (+ {result['img_filename']} beside it)")
        time.sleep(1)

if __name__ == "__main__":
    main()
