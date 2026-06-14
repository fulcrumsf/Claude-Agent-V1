import os
import sys
import re
import json
import argparse

RESOURCE_LIBRARY = "/Users/tonymacbook2025/Documents/Agent-OS/007_Resource_Library"

CATEGORY_FOLDERS = [
    "Tools", "Tutorials", "Docs", "Investments", "Models", "Prompts",
    "Research", "Workflows", "Design_Inspiration", "Personal", "Project_Ideas",
]

FILLER_PATTERNS = [
    "likely a saved reference",
    "general visual reference",
    "it can be kept as a general visual",
    "this appears to be a screenshot of",
    "can be kept as a general",
    "for later comparison or idea capture",
]

# Filename stems that are non-descriptive — must be re-visioned regardless of asset note content
BAD_FILENAME_PATTERNS = [
    # Generic/ambiguous single-word names
    r"^screenshot",
    r"^clip-\d+$",
    r"^clip$",
    r"^image$",
    r"^image-[0-9a-z]",        # Image-timestamp or Image-hash prefix
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

    # Hash/random strings
    r"^[0-9a-f]{8,}$",          # pure hex hash strings
    r"^[a-z0-9]{20,}$",         # long random alphanumeric (no dashes)

    # Timestamps and image dimensions embedded in name
    r"[0-9]{8,}",               # long number = Unix timestamp (e.g. 1762525300827)
    r"[0-9]+x[0-9]+",           # image dimensions (683x1024, 4x5, 2x3)

    # UUID / Midjourney job ID fragments
    r"[0-9a-f]{8}-[0-9a-f]{4}", # UUID-style hex fragment

    # TikTok / Instagram navigation bar OCR dumps
    r"explore-following",       # TikTok bottom nav
    r"-live-explore",           # TikTok UI
    r"-live-stem",              # TikTok STEM tab
    r"-stem-explore",           # TikTok STEM tab combo

    # Garbled OCR prefix tokens (truncated "Live", "AI", nav label fragments)
    r"^ive-",                   # garbled "Live"
    r"^itt-",                   # garbled "Live"
    r"^ial-",                   # garbled prefix
    r"^ifk-",                   # garbled prefix
    r"^i[0-9]+-",               # I238-... numeric garble
]


def find_series_files(candidates):
    """
    Detect numbered series: files ending in -N where N >= 2 AND another file
    with the same base (N-1 or N=1 or bare base) exists in the same directory.
    These are conflict-resolution duplicates that need re-vision.
    """
    all_stems = {os.path.splitext(f)[0].lower() for f in candidates}
    flagged = set()
    for f in candidates:
        stem = os.path.splitext(f)[0].lower()
        m = re.match(r'^(.+?)-(\d{1,2})$', stem)
        if not m:
            continue
        base, num = m.group(1), int(m.group(2))
        if num < 2:
            continue
        # Only flag if the series base exists (base alone, or base-1, or base-01)
        series_exists = (
            base in all_stems or
            f"{base}-1" in all_stems or
            f"{base}-01" in all_stems or
            f"{base}-{num - 1}" in all_stems
        )
        if series_exists:
            flagged.add(f)
    return flagged

IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg',
                    '.PNG', '.JPG', '.JPEG', '.WEBP', '.GIF', '.SVG')
BINARY_EXTENSIONS = ('.docx', '.doc', '.pdf')
VISION_EXTENSIONS = IMAGE_EXTENSIONS + BINARY_EXTENSIONS


def is_filler(description):
    if not description:
        return True
    d = description.lower().strip()
    if len(d) < 60:
        return True
    return any(p in d for p in FILLER_PATTERNS)


def is_bad_filename(filename):
    """Return True if the filename stem is non-descriptive and needs re-vision."""
    stem = os.path.splitext(filename)[0].lower().replace(" ", "-")
    return any(re.match(p, stem) for p in BAD_FILENAME_PATTERNS)


def find_note_path(image_stem):
    """Search all category folders for a markdown note matching the image stem."""
    for cat in CATEGORY_FOLDERS:
        note_path = os.path.join(RESOURCE_LIBRARY, cat, f"{image_stem}.md")
        if os.path.exists(note_path):
            return note_path
    return None


def read_ai_description(note_path):
    """Read the AI Analysis section body from a category-folder markdown note."""
    try:
        with open(note_path, 'r', encoding='utf-8') as f:
            in_section = False
            lines = []
            for line in f:
                stripped = line.rstrip()
                if stripped == "## AI Analysis":
                    in_section = True
                    continue
                if in_section:
                    if stripped.startswith("## "):
                        break
                    if stripped:
                        lines.append(stripped)
            if lines:
                return " ".join(lines)
    except Exception:
        pass
    return None


def audit_directory(dir_path):
    needs_vision = []
    already_cataloged = []

    try:
        files = os.listdir(dir_path)
    except Exception as e:
        print(f"Error reading directory '{dir_path}': {e}", file=sys.stderr)
        sys.exit(1)

    candidates = sorted(
        f for f in files
        if os.path.isfile(os.path.join(dir_path, f))
        and f.lower().endswith(VISION_EXTENSIONS)
    )

    series_bad = find_series_files(candidates)

    for filename in candidates:
        # Numbered series (conflict-resolution duplicates)
        if filename in series_bad:
            needs_vision.append({"file": filename, "reason": "numbered_series"})
            continue

        # Bad filename patterns — re-vision regardless of asset note
        if is_bad_filename(filename):
            needs_vision.append({"file": filename, "reason": "bad_filename"})
            continue

        stem = os.path.splitext(filename)[0]
        note_path = find_note_path(stem)

        if not note_path:
            needs_vision.append({"file": filename, "reason": "no_asset_note"})
            continue

        description = read_ai_description(note_path)

        if is_filler(description):
            needs_vision.append({
                "file": filename,
                "reason": "filler_description",
                "current": description or ""
            })
        else:
            already_cataloged.append({"file": filename, "description": description})

    return needs_vision, already_cataloged


def main():
    parser = argparse.ArgumentParser(
        description="Audit images/docs to find which ones need vision analysis. "
                    "Checks Asset Note quality — filler descriptions flag the file for re-processing."
    )
    parser.add_argument("dir", help="Directory of images/docs to audit")
    parser.add_argument("--json", action="store_true", help="Output full results as JSON")
    parser.add_argument(
        "--needs-vision-only",
        action="store_true",
        help="Print only filenames that need vision, one per line — pipe-friendly"
    )
    args = parser.parse_args()

    needs_vision, already_cataloged = audit_directory(args.dir)

    if args.needs_vision_only:
        for item in needs_vision:
            print(item["file"])
        return

    if args.json:
        print(json.dumps({
            "needs_vision": needs_vision,
            "already_cataloged": already_cataloged
        }, indent=2))
        return

    total = len(needs_vision) + len(already_cataloged)
    print(f"\n=== Vision Audit: {args.dir} ===")
    print(f"Scanned:           {total}")
    print(f"Already cataloged: {len(already_cataloged)}  (skip)")
    print(f"Needs vision:      {len(needs_vision)}\n")

    if needs_vision:
        print("Files needing vision:")
        for item in needs_vision:
            reason_map = {
                "no_asset_note": "no asset note",
                "filler_description": "filler description",
                "bad_filename": "bad filename",
                "numbered_series": "numbered series",
            }
            reason = reason_map.get(item["reason"], item["reason"])
            print(f"  [{reason}]  {item['file']}")

    if already_cataloged:
        sample = already_cataloged[:3]
        print(f"\nAlready cataloged (showing {len(sample)} of {len(already_cataloged)}):")
        for item in sample:
            desc = (item['description'] or '')[:70]
            print(f"  ✓ {item['file']}: {desc}...")


if __name__ == "__main__":
    main()
