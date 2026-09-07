"""
Resource Library stub triage.

Classifies every near-empty ("stub") note in 007_Resource_Library into one of
three buckets so the enrichment pass knows what to do with each:

  bucket1_revision   - stub still has its source screenshot in the vault
                       -> re-run vision on the image, rewrite the note in place
  bucket2_url_enrich - stub has no usable image but carries a source URL
                       -> Gemini (web-grounded) visits the link, writes a summary
  bucket3_dead       - garbled OCR title, missing image, or no salvageable signal
                       -> add to .graphifyignore so the graph rebuild skips it
                          (files stay in the vault, untouched)

A note is a "stub" when its body (excluding frontmatter, image embeds, wiki
links and bare URLs) has fewer than STUB_WORD_THRESHOLD words.

Output:
  007_Resource_Library/_Stub_Triage.json   machine-readable bucket lists
  007_Resource_Library/_Stub_Triage.md     human summary

Usage:
  python3 resource_library_stub_triage.py
"""
import os
import re
import json
from datetime import datetime

WORKSPACE = "/Users/tonymacbook2025/Documents/Agent-OS"
RESOURCE_LIB = os.path.join(WORKSPACE, "007_Resource_Library")
JSON_OUT = os.path.join(RESOURCE_LIB, "_Stub_Triage.json")
MD_OUT = os.path.join(RESOURCE_LIB, "_Stub_Triage.md")

STUB_WORD_THRESHOLD = 40

# Folders under 007 that are already excluded from the graph or are not
# curated Resource Library prose - skip them entirely.
SKIP_DIRS = {
    "OpenAI_History", "Obsidian_Attachments", "Archive", "graphify-out",
    ".git", "__pycache__",
}

IMG_EXT = (".png", ".jpg", ".jpeg", ".webp", ".gif")


def build_image_index():
    """filename (lowercase) -> absolute path, for every image in the vault."""
    idx = {}
    for root, dirs, files in os.walk(WORKSPACE):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "__pycache__")]
        for fn in files:
            if fn.lower().endswith(IMG_EXT):
                idx.setdefault(fn.lower(), os.path.join(root, fn))
    return idx


def body_word_count(text):
    body = re.sub(r"^---.*?---", "", text, count=1, flags=re.S)
    body = re.sub(r"!\[\[.*?\]\]|!\[.*?\]\(.*?\)|\[\[.*?\]\]|\[.*?\]\(.*?\)|https?://\S+", "", body)
    return len(re.findall(r"\w+", body))


def first_image_embed(text):
    m = re.search(r"!\[\[([^\]]+?\.(?:png|jpg|jpeg|webp|gif))\s*(?:\|[^\]]*)?\]\]", text, re.I)
    if m:
        return m.group(1).strip()
    m = re.search(r"!\[[^\]]*\]\(([^)]+?\.(?:png|jpg|jpeg|webp|gif))\)", text, re.I)
    if m:
        return os.path.basename(m.group(1).strip())
    return None


ASSET_URL = re.compile(
    r"\.(svg|css|js|woff2?|ico|png|jpe?g|gif|webp|map)(\?|$)"
    r"|notion\.so/icons/|notion\.so/image/|images\.unsplash\.com"
    r"|public-files\.gumroad\.com|gstatic|googletagmanager|fonts\.googleapis",
    re.I,
)


def first_url(text):
    """First real destination URL - skips asset/CDN/icon links that carry no meaning."""
    for m in re.finditer(r"https?://[^\s)>\]\"']+", text):
        u = m.group(0).rstrip(".,);")
        if u.lower().endswith(IMG_EXT) or ASSET_URL.search(u):
            continue
        return u
    return None


GARBLED_TITLE = re.compile(r"^[a-z0-9-]+$")


def looks_garbled(path):
    stem = os.path.basename(path)[:-3]
    words = stem.replace("-", " ").split()
    if len(words) < 3:
        return False
    short = [w for w in words if len(w) <= 4]
    return len(short) / len(words) > 0.6


def main():
    img_index = build_image_index()
    buckets = {"bucket1_revision": [], "bucket2_url_enrich": [], "bucket3_dead": []}
    reasons = {}

    for root, dirs, files in os.walk(RESOURCE_LIB):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            if not fn.endswith(".md") or fn.startswith("_"):
                continue
            path = os.path.join(root, fn)
            rel = os.path.relpath(path, RESOURCE_LIB)
            try:
                text = open(path, encoding="utf-8", errors="ignore").read()
            except Exception:
                continue
            if body_word_count(text) >= STUB_WORD_THRESHOLD:
                continue
            # Already enriched (has the marker) but written terse — not a stub,
            # don't re-flag it for review.
            if re.search(r"^enriched:\s*\S", text, re.M):
                continue

            embed = first_image_embed(text)
            img_path = img_index.get(embed.lower()) if embed else None
            url = first_url(text)

            if img_path:
                buckets["bucket1_revision"].append({"note": rel, "image": img_path, "url": url})
            elif url:
                buckets["bucket2_url_enrich"].append({"note": rel, "url": url})
            else:
                why = "garbled-title" if looks_garbled(path) else (
                    "missing-image" if embed else "no-signal")
                buckets["bucket3_dead"].append({"note": rel, "reason": why})
                reasons[why] = reasons.get(why, 0) + 1

    payload = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "stub_word_threshold": STUB_WORD_THRESHOLD,
        "counts": {k: len(v) for k, v in buckets.items()},
        "dead_reasons": reasons,
        **buckets,
    }
    with open(JSON_OUT, "w") as f:
        json.dump(payload, f, indent=2)

    lines = [
        "# Resource Library — Stub Triage",
        "",
        f"Generated {payload['generated']}  ·  stub = body < {STUB_WORD_THRESHOLD} words",
        "",
        f"- **bucket1_revision** ({len(buckets['bucket1_revision'])}) — screenshot present, re-run vision in place",
        f"- **bucket2_url_enrich** ({len(buckets['bucket2_url_enrich'])}) — URL present, Gemini web-grounded summary",
        f"- **bucket3_dead** ({len(buckets['bucket3_dead'])}) — add to .graphifyignore (files untouched)",
        "",
        "## Dead breakdown",
        "",
    ]
    for k, v in sorted(reasons.items(), key=lambda x: -x[1]):
        lines.append(f"- {k}: {v}")
    lines.append("")
    with open(MD_OUT, "w") as f:
        f.write("\n".join(lines))

    print(json.dumps(payload["counts"], indent=2))
    print("dead reasons:", reasons)
    print(f"\nwrote {JSON_OUT}\nwrote {MD_OUT}")


if __name__ == "__main__":
    main()
