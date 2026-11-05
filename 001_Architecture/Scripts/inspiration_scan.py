#!/usr/bin/env python3
"""Creative Inspiration scan (Ikigai Etsy, built 2026-11-04).

Scans new images in 005_Ecommerce/Etsy-Ikigai/Creative_Inspiration/, asks a
vision model what each one is (artwork, mockup, screenshot, photo, other),
analyzes ONLY the artwork inside it, renames the file to
`NNNN_Descriptive_Name.ext`, writes a STYLE PROFILE .md to Style_Profiles/
(style kept separate from subject) and appends a row to Rename_Log.md.

Usage:
  python3 inspiration_scan.py              # normal run (idempotent, safe any time)
  python3 inspiration_scan.py --dry-run    # print the plan, write nothing, no API calls
  python3 inspiration_scan.py --limit 3    # process at most 3 new images
  python3 inspiration_scan.py --undo 0004  # rename image 0004 back to its original name

Scheduled daily 03:00 by ~/Library/LaunchAgents/com.agent-os.inspiration-scan.plist.
Vision call pattern and key handling reused from process_image_ingest.py.
Never prints or logs API key values. Never deletes anything.
"""
import os
import sys
import re
import io
import json
import time
import base64
import fcntl
import argparse
import urllib.request
import urllib.error
from datetime import date

try:  # macOS framework Python frequently ships without a usable CA bundle for urllib
    import certifi
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())
except ImportError:
    pass

# ---------------------------------------------------------------- config ----
VISION_MODEL = "google/gemini-3.7-flash"            # primary, via OpenRouter (strong fine detail, cheap)
FALLBACK_OPENROUTER_MODEL = "qwen/qwen3.5-flash-02-23"  # neighbour scripts' default
OPENAI_FALLBACK_MODEL = "gpt-4o-mini"                # last resort, direct OpenAI
REQUEST_TIMEOUT = 120                                 # seconds per vision call
MAX_IMAGE_DIMENSION = 1600                            # px longest edge of the temp analysis copy

WORKSPACE_ROOT = "/Users/tonymacbook2025/Documents/Agent-OS"
INSPIRATION_DIR = os.path.join(WORKSPACE_ROOT, "005_Ecommerce/Etsy-Ikigai/Creative_Inspiration")
PROFILES_DIRNAME = "Style_Profiles"
PROFILES_DIR = os.path.join(INSPIRATION_DIR, PROFILES_DIRNAME)
LOG_PATH = os.path.join(INSPIRATION_DIR, "Rename_Log.md")
SECRETS_FILE = os.path.expanduser("~/.env-secrets")
NEEDED_KEYS = ("OPENROUTER_API_KEY", "OPENAI_API_KEY")

SUPPORTED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".avif"}
SKIP_NAMES = {".gitkeep", ".DS_Store", "Rename_Log.md"}
SOURCE_TYPES = ("artwork", "mockup", "screenshot", "photo", "other")
ID_PREFIX_RE = re.compile(r"^(\d{4})_")

LOG_HEADER = (
    "# Creative Inspiration - Rename Log\n\n"
    "Append-only. Written by `001_Architecture/Scripts/inspiration_scan.py`. "
    "A file listed here with status `ok` is never renamed again. "
    "`error` rows are retried next run. Undo: `python3 inspiration_scan.py --undo <id>`.\n\n"
    "| id | date_scanned | original_filename | new_filename | source_type | profile_file | status |\n"
    "|---|---|---|---|---|---|---|\n"
)


# --------------------------------------------------------------- secrets ----
def load_secrets():
    """launchd does not inherit the shell, so read ~/.env-secrets ourselves.
    Only the keys we need; values are never printed."""
    if not os.path.isfile(SECRETS_FILE):
        return
    with open(SECRETS_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:].strip()
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            if k not in NEEDED_KEYS or os.environ.get(k):
                continue
            v = v.strip()
            if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
                v = v[1:-1]
            os.environ[k] = v


def redact(text):
    text = str(text)
    for k in NEEDED_KEYS:
        v = os.environ.get(k)
        if v and len(v) > 6:
            text = text.replace(v, "[REDACTED]")
    return text


def say(msg):
    print(redact(msg), flush=True)


# ------------------------------------------------------------------- log ----
def read_log():
    """Return list of row dicts from Rename_Log.md (empty if no log)."""
    rows = []
    if not os.path.isfile(LOG_PATH):
        return rows
    cols = ["id", "date_scanned", "original_filename", "new_filename",
            "source_type", "profile_file", "status"]
    with open(LOG_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("|") or line.startswith("|---") or line.startswith("| id "):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < len(cols):
                continue
            rows.append(dict(zip(cols, cells[:len(cols)])))
    return rows


def append_log(row):
    new_file = not os.path.isfile(LOG_PATH)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        if new_file:
            f.write(LOG_HEADER)
        safe = {k: str(v).replace("|", "/").replace("\n", " ") for k, v in row.items()}
        f.write("| {id} | {date_scanned} | {original_filename} | {new_filename} | "
                "{source_type} | {profile_file} | {status} |\n".format(**safe))


def latest_status_by_id(rows):
    """id -> last row for that id (ok / undone)."""
    out = {}
    for r in rows:
        if re.fullmatch(r"\d{4}", r["id"]):
            out[r["id"]] = r
    return out


# ------------------------------------------------------------- numbering ----
def next_id(rows, reserved):
    nums = [int(r["id"]) for r in rows if re.fullmatch(r"\d{4}", r["id"])]
    for d in (INSPIRATION_DIR, PROFILES_DIR):
        if os.path.isdir(d):
            for n in os.listdir(d):
                m = ID_PREFIX_RE.match(n)
                if m:
                    nums.append(int(m.group(1)))
    nums.extend(reserved)
    return (max(nums) if nums else 0) + 1


# ------------------------------------------------------------ candidates ----
def find_candidates(rows):
    """Images in the folder that still need scanning."""
    by_id = latest_status_by_id(rows)
    done_names = {r["new_filename"] for r in by_id.values() if r["status"] == "ok"}
    undone_names = {r["original_filename"] for r in by_id.values() if r["status"] == "undone"}
    out, skipped = [], []
    for name in sorted(os.listdir(INSPIRATION_DIR)):
        path = os.path.join(INSPIRATION_DIR, name)
        if name in SKIP_NAMES or name.startswith(".") or os.path.isdir(path):
            continue
        ext = os.path.splitext(name)[1].lower()
        if ext not in SUPPORTED_EXT:
            skipped.append((name, "not a supported image"))
            continue
        if name in done_names:
            continue
        if name in undone_names:
            skipped.append((name, "undone by Tony, left as is"))
            continue
        out.append(name)
    return out, skipped


# ---------------------------------------------------------------- vision ----
def build_prompt():
    return """You are an expert painter and art director building a reusable STYLE library for an Etsy wall-art shop. Study this image closely, at the level of individual brush marks.

STEP 1 - classify the image as exactly one source_type:
- "artwork": the artwork itself, filling (nearly) the whole image.
- "mockup": an artwork shown in a room, in a frame, on a wall, on an easel, or as a product preview.
- "screenshot": a capture of a webpage or app (UI, text, buttons) containing an artwork.
- "photo": a camera photo of a physical artwork (angle, glare, surroundings).
- "other": anything else.

STEP 2 - if it is a mockup, screenshot or photo, analyze ONLY the artwork inside it. Ignore the room, furniture, frame, wall, UI, text, and lighting of the scene completely. Never describe them in the style fields.

STEP 3 - separate STYLE from SUBJECT. The style will be reused with completely different subjects (a cat with a wine glass, a dog, a new palette), so the style fields must contain NO subject words (no people, animals, objects, places from this picture). Describe HOW it is painted, not WHAT is painted.

Be concrete and specific to THIS image (sizes, directions, edge quality, where texture shows), not generic art words. Hex values are your best approximation of the dominant colours of the artwork only.

Return ONLY a JSON object with exactly these keys:
{
  "source_type": "artwork|mockup|screenshot|photo|other",
  "artwork_location": "if not artwork: one short sentence on where the artwork sits in the image; else empty string",
  "descriptive_name": "3 to 6 words naming what the artwork IS: medium/style + subject, e.g. 'Gouache Abstract Female Portrait' (no file extension, no numbers)",
  "title": "short human title for the style, e.g. 'Loose Impasto Botanical Still Life'",
  "subject": "one or two sentences: what is depicted (this is the ONLY place subject words go)",
  "subject_keywords": ["the main subject nouns, lowercase, e.g. woman, flowers, vase"],
  "medium": "apparent medium, e.g. acrylic on canvas, gouache on paper, oil, digital painting imitating oil",
  "era_feel": "art movement / era / mood it evokes, e.g. mid-century modern, contemporary expressionist",
  "brushwork": {
    "stroke_size": "...",
    "stroke_direction": "...",
    "visibility": "how visible the individual marks are and where",
    "edge_quality": "hard/soft/lost edges, where each occurs"
  },
  "paint_behaviour": {
    "thickness": "thin washes / opaque / impasto, and where",
    "technique": "wet-on-wet, dry brush, scumbling, glazing, gouache flatness, palette knife, etc.",
    "texture": "canvas weave, paper tooth, ridges, drips, grain",
    "variation": "the subtle paint variation inside colour areas (streaks, uneven coverage, broken colour) that makes it feel hand-made"
  },
  "composition": {
    "balance": "...",
    "focal_point": "describe as a position/shape, not as the subject",
    "negative_space": "...",
    "scale_and_cropping": "..."
  },
  "palette": {
    "dominant_colors": [{"name": "warm ochre", "hex": "#C8913A"}],
    "contrast": "...",
    "saturation": "...",
    "temperature": "..."
  },
  "what_to_preserve": ["3-6 specific traits that keep this from looking generic, vector or AI-made"],
  "style_prompt": "2-4 sentences written for an image model (Nano Banana / GPT Image) describing ONLY the painting style: medium, brushwork, paint behaviour, texture, composition approach, palette. NO subject words at all.",
  "avoid": ["4-8 short negatives suited to this style, e.g. flat vector look, smooth digital gradients, plastic AI sheen"],
  "tags": ["5-10 lowercase style tags, e.g. impasto, abstract, earthy-palette, mid-century"]
}"""


def prepare_image_b64(path):
    """Temp in-memory JPEG copy for analysis (handles webp/avif/png/huge files).
    The original file is only read, never altered."""
    from PIL import Image
    with Image.open(path) as img:
        img.load()
        img = img.copy()
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1])
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")
    if max(img.size) > MAX_IMAGE_DIMENSION:
        img.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def _parse_json(raw):
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", raw, re.S)
        if m:
            return json.loads(m.group(0))
        raise


def _call(api_url, key, model, b64, extra_headers=None):
    payload = {
        "model": model,
        "response_format": {"type": "json_object"},
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": build_prompt()},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
            ],
        }],
    }
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {key}"}
    headers.update(extra_headers or {})
    req = urllib.request.Request(api_url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    attempts, max_attempts = 0, 4
    while True:
        try:
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return _parse_json(result["choices"][0]["message"]["content"])
        except urllib.error.HTTPError as e:
            if e.code not in (429, 502, 503) or attempts >= max_attempts - 1:
                raise
            delay = 2 ** attempts
            ra = e.headers.get("Retry-After")
            if ra and ra.isdigit():
                delay = max(delay, int(ra))
            attempts += 1
            say(f"  rate-limited/busy ({e.code}); retrying in {delay}s")
            time.sleep(delay)


def analyze(path):
    """Returns (data, model_used). Raises RuntimeError with reasons on total failure."""
    b64 = prepare_image_b64(path)
    errors = []
    or_key = os.environ.get("OPENROUTER_API_KEY")
    if or_key:
        for model in (VISION_MODEL, FALLBACK_OPENROUTER_MODEL):
            try:
                data = _call("https://openrouter.ai/api/v1/chat/completions", or_key, model, b64,
                             {"HTTP-Referer": "https://openrouter.ai/",
                              "X-OpenRouter-Title": "Agent-OS Inspiration Scan"})
                validate(data)
                return data, model
            except Exception as e:
                errors.append(f"{model}: {e}")
                say(f"  {model} failed: {e}")
    oa_key = os.environ.get("OPENAI_API_KEY")
    if oa_key:
        try:
            data = _call("https://api.openai.com/v1/chat/completions", oa_key, OPENAI_FALLBACK_MODEL, b64)
            validate(data)
            return data, OPENAI_FALLBACK_MODEL
        except Exception as e:
            errors.append(f"{OPENAI_FALLBACK_MODEL}: {e}")
    if not errors:
        errors.append("no OPENROUTER_API_KEY or OPENAI_API_KEY found")
    raise RuntimeError("; ".join(errors))


REQUIRED = ("source_type", "descriptive_name", "subject", "brushwork", "paint_behaviour",
            "composition", "palette", "style_prompt", "avoid", "tags")


def validate(data):
    if not isinstance(data, dict):
        raise ValueError("response is not a JSON object")
    missing = [k for k in REQUIRED if not data.get(k)]
    if missing:
        raise ValueError(f"missing fields: {', '.join(missing)}")
    st = str(data["source_type"]).strip().lower()
    data["source_type"] = st if st in SOURCE_TYPES else "other"


# ---------------------------------------------------------------- naming ----
SMALL = {"and", "of", "with", "in", "on", "the", "a", "an", "at", "to", "for", "by"}
ACRONYMS = {"ai", "3d", "2d", "uk", "usa", "nyc"}


def title_case_name(text):
    words = re.findall(r"[A-Za-z0-9]+", str(text))
    words = [w for w in words if not re.fullmatch(r"\d{3,}", w)]
    out = []
    for w in words:
        lw = w.lower()
        if lw in ACRONYMS:
            out.append(w.upper())
        elif lw in SMALL and out:
            continue  # keep names short; drop filler words mid-name
        else:
            out.append(w[:1].upper() + w[1:].lower())
    if len(out) > 6:
        out = out[:6]
    if len(out) < 3:
        out = (out + ["Style", "Reference"])[:max(3, len(out))]
    return "_".join(out) or "Untitled_Style_Reference"


def unique_name(stem, ext, taken):
    name = f"{stem}{ext}"
    n = 2
    while name in taken or os.path.exists(os.path.join(INSPIRATION_DIR, name)) \
            or os.path.exists(os.path.join(PROFILES_DIR, f"{os.path.splitext(name)[0]}.md")):
        name = f"{stem}_{n}{ext}"
        n += 1
    return name


# --------------------------------------------------------------- profile ----
def _y(v):
    """YAML-safe scalar/flow value (JSON is valid YAML flow syntax)."""
    return json.dumps(v, ensure_ascii=False)


def quality_flags(data):
    flags = []
    sp = data.get("style_prompt", "").lower()
    for kw in data.get("subject_keywords", []) or []:
        kw = str(kw).strip().lower()
        if len(kw) > 2 and re.search(rf"\b{re.escape(kw)}s?\b", sp):
            flags.append(f"subject word in style_prompt: {kw}")
    return flags


def write_profile(img_id, new_name, original, data, model, today):
    stem = os.path.splitext(new_name)[0]
    profile_name = f"{stem}.md"
    pal = data.get("palette", {}) or {}
    colors = pal.get("dominant_colors", []) or []
    hexes = [c.get("hex", "") for c in colors if isinstance(c, dict)]
    style_json = {
        "medium": data.get("medium", ""),
        "era_feel": data.get("era_feel", ""),
        "brushwork": data.get("brushwork", {}),
        "paint_behaviour": data.get("paint_behaviour", {}),
        "composition": data.get("composition", {}),
        "palette": pal,
        "what_to_preserve": data.get("what_to_preserve", []),
        "style_prompt": data.get("style_prompt", ""),
        "avoid": data.get("avoid", []),
    }
    flags = quality_flags(data)
    fm = [
        "---",
        f"id: {_y(img_id)}",
        f"title: {_y(data.get('title', stem.replace('_', ' ')))}",
        f"new_filename: {_y(new_name)}",
        f"original_filename: {_y(original)}",
        f"image_path: {_y('../' + new_name)}",
        f"scanned: {_y(today)}",
        f"source_type: {_y(data['source_type'])}",
        f"status: {_y('active')}",
        f"medium: {_y(data.get('medium', ''))}",
        f"era_feel: {_y(data.get('era_feel', ''))}",
        f"subject: {_y(data.get('subject', ''))}",
        f"style_prompt: {_y(data.get('style_prompt', ''))}",
        f"avoid: {_y(data.get('avoid', []))}",
        f"palette_hex: {_y(hexes)}",
        f"tags: {_y(data.get('tags', []))}",
        f"vision_model: {_y(model)}",
        f"quality_flags: {_y(flags)}",
        f"style_json: {_y(style_json)}",
        "---",
        "",
    ]

    def section(title, d):
        lines = [f"## {title}", ""]
        if isinstance(d, dict):
            for k, v in d.items():
                lines.append(f"- **{k.replace('_', ' ').capitalize()}:** {v}")
        elif isinstance(d, list):
            lines += [f"- {x}" for x in d]
        else:
            lines.append(str(d))
        return lines + [""]

    body = [f"# {img_id} - {data.get('title', stem.replace('_', ' '))}", "",
            f"![{stem}](../{new_name})", "",
            f"Source type: **{data['source_type']}**"
            + (f" ({data['artwork_location']})" if data.get("artwork_location") else "")
            + f". Original file: `{original}`. Scanned {today} with `{model}`.", ""]
    body += ["## Style prompt fragment (no subject)", "", f"> {data.get('style_prompt', '')}", ""]
    body += section("Avoid", data.get("avoid", []))
    body += section("Brushwork", data.get("brushwork", {}))
    body += section("Paint behaviour", data.get("paint_behaviour", {}))
    body += section("Composition", data.get("composition", {}))
    body += ["## Palette", "", "| colour | hex |", "|---|---|"]
    body += [f"| {c.get('name', '')} | `{c.get('hex', '')}` |" for c in colors if isinstance(c, dict)]
    body += ["", f"- **Contrast:** {pal.get('contrast', '')}",
             f"- **Saturation:** {pal.get('saturation', '')}",
             f"- **Temperature:** {pal.get('temperature', '')}", ""]
    body += [f"## Medium and era feel", "", f"{data.get('medium', '')}. {data.get('era_feel', '')}", ""]
    body += section("What makes it not generic (preserve)", data.get("what_to_preserve", []))
    body += ["## Subject (recorded separately, NOT part of the style)", "", data.get("subject", ""), ""]
    body += ["## Tags", "", " ".join(f"`{t}`" for t in data.get("tags", [])), ""]
    if flags:
        body += section("Quality flags", flags)

    with open(os.path.join(PROFILES_DIR, profile_name), "w", encoding="utf-8") as f:
        f.write("\n".join(fm + body))
    return profile_name, flags


# ------------------------------------------------------------------ undo ----
def undo(img_id):
    img_id = img_id.zfill(4)
    rows = read_log()
    last = latest_status_by_id(rows).get(img_id)
    if not last:
        say(f"No log entry for id {img_id}.")
        return 1
    if last["status"] != "ok":
        say(f"id {img_id} is '{last['status']}', nothing to undo.")
        return 1
    cur = os.path.join(INSPIRATION_DIR, last["new_filename"])
    dst = os.path.join(INSPIRATION_DIR, last["original_filename"])
    if not os.path.exists(cur):
        say(f"{last['new_filename']} is not in the folder; cannot undo.")
        return 1
    if os.path.exists(dst):
        say(f"{last['original_filename']} already exists; refusing to overwrite.")
        return 1
    os.rename(cur, dst)
    prof = os.path.join(PROFILES_DIR, last["profile_file"])
    if os.path.isfile(prof):  # profile kept (never deleted), just marked undone
        with open(prof, encoding="utf-8") as f:
            txt = f.read()
        with open(prof, "w", encoding="utf-8") as f:
            f.write(txt.replace('status: "active"', 'status: "undone"', 1))
    append_log({**last, "date_scanned": date.today().isoformat(), "status": "undone"})
    say(f"Undid {img_id}: {last['new_filename']} -> {last['original_filename']} (profile kept, marked undone).")
    return 0


# ------------------------------------------------------------------ main ----
def main():
    ap = argparse.ArgumentParser(description="Creative Inspiration style scan")
    ap.add_argument("--dry-run", action="store_true", help="print the plan, write nothing")
    ap.add_argument("--limit", type=int, default=0, help="process at most N new images")
    ap.add_argument("--undo", metavar="ID", help="rename image ID back to its original filename")
    args = ap.parse_args()

    # One run at a time (launchd + dashboard "scan now"): lock this script file itself.
    lock_fh = open(os.path.abspath(__file__), "r")
    try:
        fcntl.flock(lock_fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        say("Another inspiration scan is running; exiting.")
        return 0

    today = date.today().isoformat()
    say(f"=== inspiration_scan {today} {'(dry run)' if args.dry_run else ''} ===")
    if not os.path.isdir(INSPIRATION_DIR):
        say(f"Missing folder: {INSPIRATION_DIR}")
        return 1
    if not args.dry_run and not os.path.isdir(PROFILES_DIR):
        say(f"Missing folder: {PROFILES_DIR} (create it first; this script never creates folders)")
        return 1

    if args.undo:
        if args.dry_run:
            say(f"Would undo id {args.undo}.")
            return 0
        return undo(args.undo)

    load_secrets()
    rows = read_log()
    candidates, skipped = find_candidates(rows)
    for name, why in skipped:
        say(f"skip  {name}: {why}")
    if args.limit > 0:
        candidates = candidates[:args.limit]
    if not candidates:
        say("Nothing new to scan.")
        return 0

    reserved, taken = [], set()
    used_ids = {r["id"] for r in rows if re.fullmatch(r"\d{4}", r["id"])}
    ok = err = 0
    for name in candidates:
        path = os.path.join(INSPIRATION_DIR, name)
        ext = os.path.splitext(name)[1]
        m = ID_PREFIX_RE.match(name)
        adopt = bool(m) and m.group(1) not in used_ids and m.group(1) not in [f"{r:04d}" for r in reserved]
        img_id = m.group(1) if adopt else f"{next_id(rows, reserved):04d}"
        reserved.append(int(img_id))

        if args.dry_run:
            how = "keep existing name" if adopt else f"rename to {img_id}_<Descriptive_Name>{ext}"
            say(f"plan  {name} -> id {img_id}, analyze with {VISION_MODEL}, {how}, "
                f"write {PROFILES_DIRNAME}/<stem>.md, log row")
            continue

        say(f"scan  {name} (id {img_id})")
        try:
            data, model = analyze(path)
            if adopt:
                new_name = name
            else:
                new_name = unique_name(f"{img_id}_{title_case_name(data['descriptive_name'])}", ext, taken)
                os.rename(path, os.path.join(INSPIRATION_DIR, new_name))
            taken.add(new_name)
            try:
                profile_name, flags = write_profile(img_id, new_name, name, data, model, today)
            except Exception:
                if not adopt:  # keep file and log consistent: put the name back
                    os.rename(os.path.join(INSPIRATION_DIR, new_name), path)
                raise
            row = {"id": img_id, "date_scanned": today, "original_filename": name,
                   "new_filename": new_name, "source_type": data["source_type"],
                   "profile_file": profile_name, "status": "ok"}
            append_log(row)
            rows.append(row)
            used_ids.add(img_id)
            ok += 1
            say(f"  ok    -> {new_name} [{data['source_type']}] via {model}"
                + (f"  FLAGS: {'; '.join(flags)}" if flags else ""))
        except Exception as e:
            reserved.remove(int(img_id))
            reason = redact(str(e))[:300]
            append_log({"id": "-", "date_scanned": today, "original_filename": name,
                        "new_filename": "-", "source_type": "-", "profile_file": "-",
                        "status": f"error: {reason}"})
            err += 1
            say(f"  error {name}: {reason} (left unrenamed, retried next run)")

    if not args.dry_run:
        say(f"Done: {ok} scanned, {err} errors.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
