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
from datetime import datetime

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_VISION_MODEL", "qwen/qwen3.5-flash-02-23")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

WORKSPACE_ROOT = "/Users/tonymacbook2025/Documents/Agent-OS"
RESOURCE_LIBRARY = os.path.join(WORKSPACE_ROOT, "007_Resource_Library")
VISUAL_ASSETS_DIR = os.path.join(RESOURCE_LIBRARY, "Obsidian_Attachments", "Visual_Assets")
UNDETERMINED_DIR = os.path.join(RESOURCE_LIBRARY, "Undetermined")
RENAME_LOG = os.path.join(VISUAL_ASSETS_DIR, "rename_log.md")

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

VALID_FOLDERS = [
    "Tools",
    "Tutorials",
    "Docs",
    "Investments",
    "Models",
    "Prompts",
    "Research",
    "Workflows",
    "Design_Inspiration",
    "Personal",
    "Project_Ideas",
]


def is_bad_name(name):
    """Return True if the name is non-descriptive and should not land in Visual_Assets."""
    stem = name.lower().replace(" ", "-")
    return any(re.match(p, stem) for p in BAD_NAME_PATTERNS)


def log_rename(original, new_name, category):
    """Append one entry to the rename log in Visual_Assets."""
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    line = f"- `{original}` → `{new_name}` | category: {category} | {date_str}\n"
    with open(RENAME_LOG, "a") as f:
        f.write(line)

PROMPT = """
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

## Categories:
- Tools: A SaaS product, app, plugin, GitHub repo, or software interface
- Tutorials: A walkthrough, how-to, lesson, or step-by-step process
- Research: A channel study, benchmark, comparison, market analysis
- Design_Inspiration: Visual inspiration, aesthetic reference, style bookmark
- Prompts: A reusable AI prompt, prompt template, or prompt formula
- Workflows: A process map, flowchart, or operational system
- Personal: Non-business capture (travel, food, personal interest)
- Project_Ideas: A raw project concept or future build idea
- Investments: Finance, market, crypto, stock content
- Models: AI model comparisons, pricing, benchmarks
- Docs: Reference material, documentation, API examples
- Undetermined: Image is blurry, has no context, or lacks actionable content

Output ONLY a raw JSON object (no markdown ```json blocks):

{
    "category": "Tools",
    "title_case_name": "Title-Case-With-Dashes",
    "ai_description": "2-3 sentences describing the PRIMARY SUBJECT: what tool/concept/idea is shown, what it does, why someone would save it. Do NOT describe the app chrome or navigation.",
    "tags": ["tag-one", "tag-two", "tag-three"]
}

Naming rules:
- title_case_name: Title-Case-With-Dashes, semantic meaning only (e.g. Suno-AI-Music-Platform, ComfyUI-Workflow-Tutorial)
- NO nav bar text, NO UI labels, NO timestamps, NO dimension numbers in the name
- tags: 2-5 lowercase kebab-case strings describing the CONTENT, not the UI
"""

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
        with open(image_path, "rb") as f:
            b64_data = base64.b64encode(f.read()).decode("utf-8")
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
                            {"type": "text", "text": PROMPT},
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
                            {"type": "text", "text": PROMPT},
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

def main():
    parser = argparse.ArgumentParser(description="Semantically ingest images (Tools, Tutorials, etc.) using OpenRouter or OpenAI Vision.")
    parser.add_argument("path", help="Path to a single image or a directory of images.")
    args = parser.parse_args()

    target_path = args.path

    if not OPENROUTER_KEY and not OPENAI_KEY:
        print("Error: OPENROUTER_API_KEY and OPENAI_API_KEY are both missing.")
        sys.exit(1)

    os.makedirs(VISUAL_ASSETS_DIR, exist_ok=True)
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

    print(f"Found {len(files_to_process)} images to process.")

    for i, file_path in enumerate(files_to_process):
        print(f"[{i+1}/{len(files_to_process)}] Processing {os.path.basename(file_path)}...")
        
        data = process_image(file_path)
        if not data:
            print("   -> Failed to extract semantic data.")
            continue
            
        category = data.get("category", "Undetermined")
        title_case_name = data.get("title_case_name", "Untitled")
        ai_description = data.get("ai_description", "No description available.")
        tags = data.get("tags", [])

        # Validate that the AI returned a descriptive name — reject generic/hash names
        if is_bad_name(title_case_name):
            print(f"   -> [BAD NAME] '{title_case_name}' is non-descriptive — routing to Undetermined/")
            category = "Undetermined"

        ext = file_path.lower().split('.')[-1]
        new_img_filename = f"{title_case_name}.{ext}"

        if category == "Undetermined" or category not in VALID_FOLDERS:
            # Move directly to Undetermined, no markdown
            dest_img_path = os.path.join(UNDETERMINED_DIR, new_img_filename)
            shutil.move(file_path, dest_img_path)
            print(f"   -> [UNDETERMINED] Moved to {dest_img_path}")
            time.sleep(1)
            continue

        # Move image to Visual Assets
        dest_img_path = os.path.join(VISUAL_ASSETS_DIR, new_img_filename)
        # Handle conflicts
        counter = 1
        while os.path.exists(dest_img_path):
            new_img_filename = f"{title_case_name}-{counter}.{ext}"
            dest_img_path = os.path.join(VISUAL_ASSETS_DIR, new_img_filename)
            counter += 1
            
        shutil.move(file_path, dest_img_path)
        log_rename(os.path.basename(file_path), new_img_filename, category)

        # Create Markdown file
        md_filename = f"{title_case_name}.md"
        md_path = os.path.join(RESOURCE_LIBRARY, category, md_filename)

        # Avoid overwriting an existing note — append counter to filename
        md_counter = 1
        while os.path.exists(md_path):
            md_filename = f"{title_case_name}-{md_counter}.md"
            md_path = os.path.join(RESOURCE_LIBRARY, category, md_filename)
            md_counter += 1

        # Resolve human title
        human_title = title_case_name.replace("-", " ")
        
        yaml_tags = "\n".join([f"  - {t}" for t in tags])
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        md_content = f"""---
title: "{human_title}"
type: extracted-knowledge
category: {category.lower()}
tags:
{yaml_tags}
original_filename: "{os.path.basename(file_path)}"
created: {date_str}
---

![[{new_img_filename}]]

## AI Analysis
{ai_description}
"""
        with open(md_path, "w") as f:
            f.write(md_content)
            
        print(f"   -> [EXTRACTED] Created {category}/{md_filename}")
        time.sleep(1)

if __name__ == "__main__":
    main()
