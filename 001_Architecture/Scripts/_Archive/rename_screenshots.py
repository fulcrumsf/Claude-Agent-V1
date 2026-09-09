# DEPRECATED — 2026-05-09
# Produces lowercase kebab-case filenames and uses Gemini API directly.
# Incompatible with current pipeline (Title-Case-With-Dashes, OpenRouter/OpenAI).
# Use process_image_ingest.py instead.

import os
import sys
import json
import base64
import argparse
import urllib.request
import urllib.error
import time
import re

API_KEY = os.environ.get("GEMINI_API_KEY")
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

DEFAULT_DIR = "/Users/tonymacbook2025/Documents/Agent-OS/000_Ingest/Process Screenshots/Rename"

PROMPT = """
You are tasked with generating a concise, descriptive filename for this screenshot.
The user takes these screenshots from their phone (TikTok, YouTube) or laptop.
It usually contains:
- A bookmark of a tool
- A physical prop or product
- A business idea (they have ideas in various industries)
- A stock or investment they want to remember

Based on what you see in the image, provide ONLY a single filename (without the extension) using lowercase kebab-case (hyphens between words, no underscores, no spaces).
Examples:
- tiktok-video-editing-tool
- youtube-prop-coffee-mug
- business-idea-real-estate-app
- stock-aapl-chart
- tool-website-name

Output ONLY the filename, nothing else. No explanation. Max 5-7 words.
"""


def to_kebab(name):
    return name.lower().replace('_', '-').replace(' ', '-').replace('/', '-').replace('\\', '-')


def clean_name(name):
    name = to_kebab(name)
    name = re.sub(r'[^a-z0-9\-]+', '-', name)
    name = re.sub(r'-+', '-', name).strip('-')
    return name


def generate_filename(image_path):
    ext = image_path.lower().split('.')[-1]
    if ext in ('jpg', 'jpeg'):
        mime_type = "image/jpeg"
    elif ext == 'png':
        mime_type = "image/png"
    else:
        return None

    try:
        with open(image_path, "rb") as f:
            b64_data = base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        print(f"Error reading {image_path}: {e}")
        return None

    if API_KEY:
        try:
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": PROMPT},
                            {"inlineData": {"mimeType": mime_type, "data": b64_data}}
                        ]
                    }
                ],
                "generationConfig": {
                    "responseMimeType": "text/plain"
                }
            }
            req = urllib.request.Request(
                API_URL,
                data=json.dumps(payload).encode('utf-8'),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                raw = result['candidates'][0]['content']['parts'][0]['text'].strip()
                name = clean_name(raw)
                if name.endswith(f".{ext}"):
                    name = name[:-(len(ext) + 1)]
                return name
        except Exception as e:
            print(f"Gemini failed for {image_path}: {e}. Falling back to OpenAI if available...")

    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        try:
            payload = {
                "model": "gpt-4o-mini",
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
            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {openai_key}"
                }
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                raw = result['choices'][0]['message']['content'].strip()
                name = clean_name(raw)
                if name.endswith(f".{ext}"):
                    name = name[:-(len(ext) + 1)]
                return name
        except Exception as e:
            print(f"OpenAI fallback failed for {image_path}: {e}")
            return None

    return None


def main():
    parser = argparse.ArgumentParser(description="Rename images using Gemini vision — outputs kebab-case filenames.")
    parser.add_argument("dir", nargs="?", default=DEFAULT_DIR, help="Directory of images to rename (default: Process Screenshots/Rename)")
    args = parser.parse_args()

    dir_path = args.dir

    if not os.path.isdir(dir_path):
        print(f"Error: '{dir_path}' is not a valid directory.")
        sys.exit(1)

    files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f)) and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    print(f"Found {len(files)} images in {dir_path}")

    for i, file in enumerate(files):
        old_path = os.path.join(dir_path, file)
        ext = file.rsplit('.', 1)[-1]

        print(f"[{i+1}/{len(files)}] Processing {file}...")

        new_name = generate_filename(old_path)

        if new_name:
            new_filename = f"{new_name}.{ext}"
            new_path = os.path.join(dir_path, new_filename)
            counter = 1
            while os.path.exists(new_path) and new_path != old_path:
                new_filename = f"{new_name}-{counter}.{ext}"
                new_path = os.path.join(dir_path, new_filename)
                counter += 1

            if new_path != old_path:
                os.rename(old_path, new_path)
                print(f"   -> {new_filename}")
            else:
                print(f"   -> Name unchanged")
        else:
            print(f"   -> Failed to generate name")

        time.sleep(0.1)


if __name__ == "__main__":
    main()
