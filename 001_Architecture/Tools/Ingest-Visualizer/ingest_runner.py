"""Bridges the Ingest Visualizer's pre-tagged items to the real ingest
scripts. Never duplicates their logic - imports process_image_ingest.py's
own functions directly (vision call + the shared finalize_and_write_note),
and shells out to process_video_ingest.py exactly as the CLI would. Both
scripts remain fully usable stand-alone with unchanged behavior."""
import os
import re
import sys
import shutil
import subprocess
import importlib.util
import pathlib
from datetime import datetime

_here = pathlib.Path(__file__).parent


def _load_local(name):
    key = f"iv_{name}"
    if key in sys.modules:
        return sys.modules[key]
    spec = importlib.util.spec_from_file_location(key, _here / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules[key] = m
    spec.loader.exec_module(m)
    return m


config = _load_local("config")


def _load_pii():
    """Import process_image_ingest.py as a module, without running its CLI."""
    key = "iv_process_image_ingest"
    if key in sys.modules:
        return sys.modules[key]
    path = os.path.join(config.SCRIPTS_DIR, "process_image_ingest.py")
    spec = importlib.util.spec_from_file_location(key, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[key] = m
    spec.loader.exec_module(m)
    return m


def _load_rtt():
    """Import retag_and_retitle.py to reuse its existing cheap text-only
    classification model call (OpenRouter google/gemini-2.5-flash-lite, same
    one already used to retag library notes) - never a second copy of this
    calling code for a second model choice."""
    key = "iv_retag_and_retitle"
    if key in sys.modules:
        return sys.modules[key]
    path = os.path.join(config.SCRIPTS_DIR, "retag_and_retitle.py")
    spec = importlib.util.spec_from_file_location(key, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[key] = m
    spec.loader.exec_module(m)
    return m


def classify_text_bookmark(abspath):
    """Ask the same cheap text model retag_and_retitle.py uses to read a raw
    bookmark's own content and suggest a title/folder/tags - no vision, no
    manual folder required. Returns (result_dict_or_None, error_or_None)."""
    rtt = _load_rtt()
    pii = _load_pii()
    folders = pii.load_folder_vocabulary()
    tags = pii.load_tag_vocabulary()
    stem = os.path.splitext(os.path.basename(abspath))[0]
    raw = open(abspath, encoding="utf-8", errors="ignore").read()
    body = _FM_RE.sub("", raw, count=1)[:3000]

    folder_list = "\n".join(f"- {k}: {v}" for k, v in folders.items())
    tag_list = "\n".join(f"- {k}: {v}" for k, v in tags.items())
    prompt = f"""You are classifying a bookmarked note (saved via a browser web-clipper,
text only, no image involved) into Tony's reference library. Read it like a person would.

FILENAME / WORKING TITLE: {stem}

BODY:
{body}

VALID FOLDERS (pick exactly one, use the exact name):
{folder_list}

VALID TAGS (use exact names, nothing outside this list):
{tag_list}

Rules:
- title: a short, clean human title for this bookmark - fix a garbled/URL-like filename into
  a real name if needed, otherwise keep the working title if it's already clear.
- folder: pick the single best-fitting folder from the list above.
- tags: 1 minimum, 2 maximum - one good tag beats a forced second one; only add a second if
  it is ALSO clearly, specifically supported by the content.
- Set "confident": false only if you genuinely cannot tell what this bookmark is about.

Output ONLY raw JSON (no markdown fences):
{{"title": "...", "folder": "...", "tags": ["OneTagThatFits"], "confident": true}}
"""
    try:
        result = rtt.classify(prompt)
    except Exception as e:
        return None, f"classification call failed: {e}"
    ok, reason = rtt.validate(result, folders, tags)
    if not ok:
        return None, f"classification not usable ({reason})"
    return result, None


def _titleize(text):
    """A human-typed title -> Title-Case-With-Dashes stem, preserving
    whatever capitalization Tony actually typed."""
    return "-".join(text.strip().split())


def ingest_image(abspath, manual):
    """manual: {title, description, url, folder, tags} - any subset may be
    filled in. Returns the same status dict as finalize_and_write_note,
    plus a top-level 'used_vision' bool so the caller can tell which path ran."""
    pii = _load_pii()

    have_all = bool(manual.get("title") and manual.get("description")
                     and manual.get("folder") and manual.get("tags"))

    # Same dedup-1 pre-check the CLI does - never waste a vision call (or
    # write a duplicate note) on a byte-identical image already in the library.
    img_hashes, note_urls, taken = pii.build_library_index()
    try:
        digest = pii._sha256(abspath)
    except OSError:
        digest = None
    if digest and digest in img_hashes:
        return {"status": "dup", "dup_of": img_hashes[digest], "used_vision": False}

    if have_all:
        data = {
            "category": manual["folder"],
            "title_case_name": _titleize(manual["title"]),
            "ai_description": manual["description"],
            "tags": manual["tags"],
            "content_type": "reference",
            "form": "other",
            "url": manual.get("url", ""),
        }
        used_vision = False
    else:
        vision_data = pii.process_image(abspath)
        if not vision_data:
            return {"status": "error", "message": "vision extraction failed", "used_vision": True}
        data = dict(vision_data)
        if manual.get("title"):
            data["title_case_name"] = _titleize(manual["title"])
        if manual.get("description"):
            data["ai_description"] = manual["description"]
        if manual.get("folder"):
            data["category"] = manual["folder"]
        if manual.get("tags"):
            data["tags"] = manual["tags"]
        if manual.get("url"):
            data["url"] = manual["url"]
        used_vision = True

    result = pii.finalize_and_write_note(abspath, data, img_hashes, note_urls, taken)
    result["used_vision"] = used_vision
    return result


_FM_RE = re.compile(r"^---\s*\n.*?\n---\s*\n?", re.S)


def _slugify(text):
    text = re.sub(r"[^A-Za-z0-9 -]", "", text).strip()
    return "-".join(text.split())


def ingest_pdf(abspath, entry):
    """Per ingest/SKILL.md: Obsidian has a native PDF viewer, so the PDF
    itself just moves into the destination folder (default Docs) - no
    markitdown conversion needed unless Tony asks for one separately. A
    small companion .md (same stem, same folder) carries the title/tags,
    since a PDF file has nowhere of its own to hold that. Folder/tags are
    manual-only for now - no text-extraction classifier built for PDFs yet."""
    pii = _load_pii()
    folder = entry.get("folder") or "Docs"
    if folder not in pii.VALID_FOLDERS:
        return {"status": "error", "message": f"'{folder}' isn't a valid folder"}

    vocab = pii.load_tag_vocabulary()
    tags = [c for c in (pii._canonical_tag(t, vocab) for t in (entry.get("tags") or [])) if c][:2]
    if not tags:
        tags = ["Misc"]

    filename = os.path.basename(abspath)
    stem = os.path.splitext(filename)[0]
    title = entry.get("title") or stem
    name = _slugify(title) or _slugify(stem) or "Untitled"

    dest_dir = os.path.join(pii.RESOURCE_LIBRARY, folder)
    os.makedirs(dest_dir, exist_ok=True)
    base, n = name, 1
    while (os.path.exists(os.path.join(dest_dir, f"{name}.md"))
           or os.path.exists(os.path.join(dest_dir, f"{name}.pdf"))):
        name = f"{base}-{n}"
        n += 1

    dest_pdf = os.path.join(dest_dir, f"{name}.pdf")
    shutil.move(abspath, dest_pdf)

    yaml_tags = "\n".join(f"  - {t}" for t in tags)
    url_line = f'url: "{entry["url"]}"\n' if entry.get("url") else ""
    summary_line = f'summary: "{entry["description"]}"\n' if entry.get("description") else ""
    date_str = datetime.now().strftime("%Y-%m-%d")
    md_content = f"""---
title: "{title}"
{url_line}{summary_line}tags:
{yaml_tags}
original_filename: "{filename}"
created: {date_str}
---

![[{name}.pdf]]
"""
    dest_md = os.path.join(dest_dir, f"{name}.md")
    with open(dest_md, "w", encoding="utf-8") as f:
        f.write(md_content)

    return {"status": "written", "category": folder, "name": name, "img_filename": f"{name}.pdf"}


def ingest_text(abspath, entry):
    """A bare bookmark .md (e.g. from the Obsidian web-clipper Chrome
    extension) was never vision-classified - there's no image to look at.
    But it isn't left fully manual either: if Tony hasn't set a folder/tags
    himself, this reads the note's own text via the same cheap classifier
    retag_and_retitle.py already uses and auto-suggests them. A manual
    folder/tag always wins over the classifier - this only fills in what
    Tony left blank, same override precedence as the image path."""
    pii = _load_pii()
    folder = entry.get("folder")
    tags_in = entry.get("tags") or []
    title_in = entry.get("title")
    used_classifier = False

    if not folder or not tags_in:
        result, err = classify_text_bookmark(abspath)
        if result:
            used_classifier = True
            folder = folder or result["folder"]
            tags_in = tags_in or result["tags"]
            title_in = title_in or result["title"]
        elif not folder:
            return {"status": "error",
                    "message": err or "Could not auto-classify this bookmark — pick a folder manually."}

    if folder not in pii.VALID_FOLDERS:
        return {"status": "error", "message": f"'{folder}' isn't a valid folder"}

    vocab = pii.load_tag_vocabulary()
    tags = [c for c in (pii._canonical_tag(t, vocab) for t in tags_in) if c][:2]
    if not tags:
        tags = ["Misc"]

    filename = os.path.basename(abspath)
    stem = os.path.splitext(filename)[0]
    title = title_in or stem
    name = _slugify(title) or _slugify(stem) or "Untitled"

    dest_dir = os.path.join(pii.RESOURCE_LIBRARY, folder)
    os.makedirs(dest_dir, exist_ok=True)
    base, n = name, 1
    while os.path.exists(os.path.join(dest_dir, f"{name}.md")):
        name = f"{base}-{n}"
        n += 1

    raw = open(abspath, encoding="utf-8", errors="ignore").read()
    body = _FM_RE.sub("", raw, count=1)  # drop any pre-existing frontmatter (e.g. from the web clipper)

    yaml_tags = "\n".join(f"  - {t}" for t in tags)
    url_line = f'url: "{entry["url"]}"\n' if entry.get("url") else ""
    summary_line = f'summary: "{entry["description"]}"\n' if entry.get("description") else ""
    date_str = datetime.now().strftime("%Y-%m-%d")

    frontmatter = f"""---
title: "{title}"
{url_line}{summary_line}tags:
{yaml_tags}
created: {date_str}
---

"""
    dest_path = os.path.join(dest_dir, f"{name}.md")
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(frontmatter + body)
    os.remove(abspath)
    return {"status": "written", "category": folder, "name": name, "img_filename": None,
            "used_classifier": used_classifier}


_PACKAGE_LINE_RE = re.compile(r"Knowledge Package created at:\s*\n?(.+)$")


def ingest_video(abspath, tags, note):
    """Runs process_video_ingest.py unchanged, then - as a separate
    post-processing step done by THIS tool, not the original script -
    rewrites the resulting Tutorial.md's tags to the real vocabulary and
    appends Tony's note as an analysis-instructions section."""
    script = os.path.join(config.SCRIPTS_DIR, "process_video_ingest.py")
    proc = subprocess.run(
        ["python3", script, abspath],
        capture_output=True, text=True, timeout=1800,
    )
    if proc.returncode != 0:
        return {"status": "error", "message": proc.stderr[-2000:]}

    m = _PACKAGE_LINE_RE.search(proc.stdout)
    if not m:
        return {"status": "error", "message": "could not find package path in output",
                "stdout": proc.stdout[-2000:]}
    package_dir = m.group(1).strip()
    tutorial_files = [f for f in os.listdir(package_dir) if f.endswith("-Tutorial.md")] \
        if os.path.isdir(package_dir) else []
    if not tutorial_files:
        return {"status": "written", "package_dir": package_dir, "note": "no Tutorial.md found to annotate"}

    tutorial_path = os.path.join(package_dir, tutorial_files[0])
    text = open(tutorial_path, encoding="utf-8").read()

    pii = _load_pii()
    vocab = pii.load_tag_vocabulary()
    canonical_tags = [c for c in (pii._canonical_tag(t, vocab) for t in (tags or ["Guide"])) if c][:2]
    if not canonical_tags:
        canonical_tags = ["Guide"]
    yaml_tags = "\n".join(f"  - {t}" for t in canonical_tags)
    text = re.sub(r"^tags:\n(?:  - .*\n)+", f"tags:\n{yaml_tags}\n", text, count=1, flags=re.M)

    if note and note.strip():
        text += f"\n## Analysis Notes (from Tony)\n{note.strip()}\n"

    open(tutorial_path, "w", encoding="utf-8").write(text)
    return {"status": "written", "package_dir": package_dir, "tutorial_path": tutorial_path}
