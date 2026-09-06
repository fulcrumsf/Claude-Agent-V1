"""
Re-vision Resource Library stub notes (triage bucket 1) IN PLACE.

For every stub note that still has its source screenshot, re-run the hardened
vision prompt from process_image_ingest.py and rewrite that note's frontmatter
+ body where it already lives. The filename, path and ![[image]] embed are
preserved, so no Obsidian links or graph node IDs break.

What changes in each note:
  - form:      set from vision (saas-tool | github-repo | tiktok | ...)
  - summary:   real 2-3 sentence description (was filler / absent)
  - url:       only if actually visible in the frame (anti-fabrication rule)
  - search_for + needs-enrichment tag: when the URL is unknown but nameable
  - tags:      union of existing tags + new content tags
  - type:      normalised content_type (never "extracted-knowledge")
  - enriched:  today's date - notes carrying this are skipped on re-runs

Reads:  007_Resource_Library/_Stub_Triage.json  (run resource_library_stub_triage.py first)
Writes: each note in place + 007_Resource_Library/_Revision_Log.md

Usage:
  source ~/.env-secrets
  python3 revision_stub_notes.py --dry-run --limit 5
  python3 revision_stub_notes.py --limit 10
  python3 revision_stub_notes.py                 # all remaining
"""
import os
import re
import sys
import json
import time
import argparse
from datetime import datetime

try:  # macOS framework Python often can't find a CA bundle for urllib
    import certifi
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())
except ImportError:
    pass

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)
from process_image_ingest import process_image, is_bad_name  # reuse hardened prompt + call

WORKSPACE = "/Users/tonymacbook2025/Documents/Agent-OS"
RESOURCE_LIB = os.path.join(WORKSPACE, "007_Resource_Library")
TRIAGE = os.path.join(RESOURCE_LIB, "_Stub_Triage.json")
LOG = os.path.join(RESOURCE_LIB, "_Revision_Log.md")
TODAY = datetime.now().strftime("%Y-%m-%d")

FM_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.S)


def parse_frontmatter(text):
    m = FM_RE.match(text)
    if not m:
        return {}, text, ""
    raw, body = m.group(1), m.group(2)
    fm = {}
    key = None
    for line in raw.split("\n"):
        if re.match(r"^\s*-\s+", line) and key:
            fm.setdefault(key, []) if not isinstance(fm.get(key), list) else None
            if not isinstance(fm.get(key), list):
                fm[key] = []
            fm[key].append(line.strip()[1:].strip().strip('"\''))
            continue
        mm = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if mm:
            key = mm.group(1)
            val = mm.group(2).strip()
            if val == "":
                fm[key] = []
            else:
                fm[key] = val.strip('"\'')
    return fm, body, raw


def existing_embed(body):
    m = re.search(r"!\[\[[^\]]+\]\]", body)
    return m.group(0) if m else None


def as_list(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def build_note(fm_old, body_old, data):
    title = fm_old.get("title") or data.get("title_case_name", "Untitled").replace("-", " ")
    category = (fm_old.get("category") or data.get("category", "")).strip()
    created = fm_old.get("created") or TODAY
    orig = fm_old.get("original_filename", "")

    content_type = (data.get("content_type") or fm_old.get("type") or "reference") or "reference"
    if content_type in ("extracted-knowledge", "", None):
        content_type = "reference"
    form = (data.get("form") or "other") or "other"
    summary = (data.get("ai_description") or "").strip()
    url = (data.get("url", "") or "").strip()
    search_for = (data.get("search_for", "") or "").strip()

    if url and not re.match(r"^https?://[^\s]+\.[^\s]+", url):
        search_for = search_for or url
        url = ""

    tags = as_list(fm_old.get("tags")) + [t for t in data.get("tags", []) if t]
    if ("github.com" in url) or form == "github-repo":
        form = "github-repo"
        if "github-repo" not in tags:
            tags = ["github-repo"] + tags
        if not url and not search_for:
            search_for = f"{title} github repo"
    if search_for and not url and "needs-enrichment" not in tags:
        tags.append("needs-enrichment")
    # de-dup, keep order
    seen = set()
    tags = [t for t in tags if not (t in seen or seen.add(t))]

    embed = existing_embed(body_old) or (f"![[{data.get('title_case_name','')}]]" if False else "")

    q = '"'
    lines = ["---", f"title: {q}{title}{q}", f"type: {content_type}"]
    if category:
        lines.append(f"category: {category.lower()}")
    lines.append(f"form: {form}")
    lines.append(f"summary: {q}{summary.replace(q, chr(39))}{q}")
    if url:
        lines.append(f"url: {q}{url}{q}")
    elif search_for:
        lines.append(f"search_for: {q}{search_for.replace(q, chr(39))}{q}")
    lines.append("tags:")
    lines += [f"  - {t}" for t in tags]
    if orig:
        lines.append(f"original_filename: {q}{orig}{q}")
    lines.append(f"created: {created}")
    lines.append(f"enriched: {TODAY}")
    lines.append("---")
    lines.append("")
    if embed:
        lines.append(embed)
        lines.append("")
    lines.append("## Summary")
    lines.append(summary or "_vision returned no description_")
    if search_for and not url:
        lines.append("")
        lines.append("## Enrichment needed")
        lines.append(f"URL/context not shown in the image. Resolve by web-searching: `{search_for}`")
    return "\n".join(lines) + "\n"


def log(entries):
    header = not os.path.exists(LOG)
    with open(LOG, "a") as f:
        if header:
            f.write(f"# Resource Library — Re-vision Log\n\nStarted {datetime.now().isoformat(timespec='seconds')}\n\n")
        for e in entries:
            f.write(e + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--throttle", type=float, default=1.0)
    ap.add_argument("--shard", default="0/1", help="I/N - process items where index %% N == I")
    args = ap.parse_args()

    shard_i, shard_n = (int(x) for x in args.shard.split("/"))
    items = json.load(open(TRIAGE))["bucket1_revision"]
    items = [it for idx, it in enumerate(items) if idx % shard_n == shard_i]
    done = failed = skipped = 0
    entries = []

    for it in items:
        if args.limit and (done + failed) >= args.limit:
            break
        note_path = os.path.join(RESOURCE_LIB, it["note"])
        if not os.path.exists(note_path):
            continue
        text = open(note_path, encoding="utf-8", errors="ignore").read()
        fm, body, _ = parse_frontmatter(text)
        if fm.get("enriched"):
            skipped += 1
            continue
        img = it["image"]
        if not os.path.exists(img):
            failed += 1
            entries.append(f"- FAIL (image gone) `{it['note']}`")
            continue

        old_summary = (fm.get("summary") or fm.get("ai_description") or "")[:80]
        if args.dry_run:
            print(f"[dry] would re-vision {it['note']}  (img: {os.path.basename(img)})")
            done += 1
            continue

        print(f"[{done + failed + 1}] {it['note']}", flush=True)
        data = process_image(img)
        if not data:
            failed += 1
            entries.append(f"- FAIL (vision) `{it['note']}`")
            time.sleep(args.throttle)
            continue

        new_text = build_note(fm, body, data)
        with open(note_path, "w") as f:
            f.write(new_text)
        done += 1
        new_summary = (data.get("ai_description") or "")[:80]
        flag = " [BAD-NAME→check]" if is_bad_name(data.get("title_case_name", "")) else ""
        entries.append(f"- ok `{it['note']}`{flag}\n    - was: {old_summary!r}\n    - now: {new_summary!r}")
        if done % 20 == 0:
            log(entries)
            entries = []
            print(f"  ...{done} done, {failed} failed, {skipped} skipped")
        time.sleep(args.throttle)

    if entries:
        log(entries)
    print(f"\nre-vision complete: {done} rewritten, {failed} failed, {skipped} already-enriched")
    if not args.dry_run:
        print(f"log: {LOG}")


if __name__ == "__main__":
    main()
