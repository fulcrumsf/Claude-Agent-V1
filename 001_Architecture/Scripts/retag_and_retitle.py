#!/usr/bin/env python3
"""Retag/retitle/reclassify existing 007_Resource_Library notes from their
already-written summary text — no Vision/image re-processing.

Reads Folder + Source + Tag definitions live from Directory.md (never
hardcoded), asks a cheap text-only model to propose a cleaned title, the
correct folder, and 1-2 tags from the locked vocabulary, and either writes
the result in place (folder unchanged) or moves the note (folder changed).
Anything the model can't confidently classify is routed to Undetermined/
with a `retag_flag` reason instead of being silently left wrong.

Usage:
    python3 retag_and_retitle.py Tools                  # dry run
    python3 retag_and_retitle.py Tools,Tutorials --limit 20
    python3 retag_and_retitle.py Tools --apply           # writes + moves

Env: OPENROUTER_API_KEY (primary), OPENAI_API_KEY (fallback) from ~/.env-secrets.
"""
import os
import re
import sys
import json
import time
import glob
import argparse
import importlib.util
import pathlib
import urllib.request
import urllib.error

try:
    import certifi
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
except ImportError:
    pass

WORKSPACE = "/Users/tonymacbook2025/Documents/Agent-OS"
RESOURCE_LIB = os.path.join(WORKSPACE, "007_Resource_Library")
DIRECTORY_MD = os.path.join(RESOURCE_LIB, "Directory.md")
VISUALIZER_DIR = pathlib.Path(WORKSPACE) / "001_Architecture/Tools/Resource-Library-Visualizer"

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_TEXT_MODEL", "google/gemini-2.5-flash-lite")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4.1-nano"

NEVER_SCAN = {"OpenAI_History"}
# Archive and Undetermined are deliberately scannable (not in NEVER_SCAN): Tony
# explicitly asked Archive to be included, and Undetermined becomes a legitimate
# retry queue once cleared of the batch that landed there.
MIN_SUMMARY_LEN = 15
TAG_MIN, TAG_MAX = 1, 2


# ---------- reuse the Visualizer's modules instead of re-implementing ----------

def _load(name):
    key = f"rlv_{name}"
    if key in sys.modules:
        return sys.modules[key]
    spec = importlib.util.spec_from_file_location(key, VISUALIZER_DIR / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules[key] = m
    spec.loader.exec_module(m)
    return m


notes = _load("notes")
actions = _load("actions")
config = _load("config")


# ---------- parse Directory.md (the one source of truth) ----------

BULLET_RE = re.compile(r"^\*\s+\*\*([^:*]+):\*\*\s*(.*)$")


def _section(text, header):
    lines = text.split("\n")
    start = next((i for i, l in enumerate(lines) if l.strip() == header), None)
    if start is None:
        return []
    out = []
    for l in lines[start + 1:]:
        if l.startswith("## "):
            break
        m = BULLET_RE.match(l.strip())
        if m:
            out.append((m.group(1).strip(), m.group(2).strip()))
    return out


def parse_directory():
    text = open(DIRECTORY_MD, encoding="utf-8").read()
    all_bullets = dict(_section(text, "## Folder Layout & Descriptions"))
    # Folder Layout also carries informational asides ("Image storage (...)",
    # "Visual review tool (...)") that aren't real folders — keep only bullets
    # that are an actual directory on disk.
    folders = {name: desc for name, desc in all_bullets.items()
               if os.path.isdir(os.path.join(RESOURCE_LIB, name))}
    sources = dict(_section(text, "## Source Definitions"))
    tags = dict(_section(text, "## Tag Vocabulary"))
    if not folders or not tags:
        raise RuntimeError("Directory.md sections missing/unparseable — check headers match exactly")
    return folders, sources, tags


# ---------- model call ----------

def build_prompt(note, folders, tags):
    folder_list = "\n".join(f"- {k}: {v}" for k, v in folders.items())
    tag_list = "\n".join(f"- {k}: {v}" for k, v in tags.items())
    return f"""You are classifying an existing reference-library note. You are given only
text that was already written about it — no image. Read it like a person would.

CURRENT TITLE: {note['title']}
CURRENT FOLDER: {note['folder']}
EXISTING TAGS: {", ".join(note['tags']) or "(none)"}
SEARCH HINT (may be empty): {note['search_for']}
{"RAW BODY EXCERPT (no AI summary exists for this note - read it directly, it may be a long working doc, only judge the overall subject/type)" if note.get("used_body_fallback") else "SUMMARY"}:
{note['summary']}

VALID FOLDERS (pick exactly one, use the exact name):
{folder_list}

VALID TAGS (use exact names, nothing outside this list):
{tag_list}

Rules:
- If the current title is already clear and specific, keep it unchanged.
- If it's garbled (random characters, app-chrome OCR junk, a hash/filename), replace it
  with a short human title naming the actual subject/tool from the summary or search hint —
  just the name is fine, do not pad it with a description.
- If the current folder is already correct, return it unchanged.
- Tags: 1 minimum, 2 maximum — but a second tag is NOT expected by default. Pick exactly
  ONE tag that clearly fits. Only add a second if it is ALSO clearly, specifically supported
  by the actual content — never add a second tag just to fill the range, and never pick a
  tag based on a loose or surface-level word match. One good tag beats two where the second
  is a stretch.
- Set "confident": false only if you cannot find even ONE tag that genuinely fits, or you
  are unsure of the folder — do not force a guess either way.

Output ONLY raw JSON (no markdown fences). One tag is a completely normal, good answer:
{{"title": "...", "folder": "...", "tags": ["OneTagThatFits"], "confident": true}}
"""


def _extract_json(raw):
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)
    return json.loads(raw)


def call_openrouter(prompt):
    payload = {
        "model": OPENROUTER_MODEL,
        "response_format": {"type": "json_object"},
        "messages": [{"role": "user", "content": prompt}],
    }
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "HTTP-Referer": "https://openrouter.ai/",
            "X-OpenRouter-Title": "Agent-OS Retag Pass",
        },
    )
    attempts, max_attempts = 0, 5
    while True:
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return _extract_json(result["choices"][0]["message"]["content"])
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempts >= max_attempts - 1:
                raise
            delay = 2 ** attempts
            attempts += 1
            time.sleep(delay)


def call_openai(prompt):
    payload = {
        "model": OPENAI_MODEL,
        "response_format": {"type": "json_object"},
        "messages": [{"role": "user", "content": prompt}],
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {OPENAI_KEY}"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        return _extract_json(result["choices"][0]["message"]["content"])


def classify(prompt):
    if OPENROUTER_KEY:
        try:
            return call_openrouter(prompt)
        except Exception as e:  # noqa: BLE001 - fall through to OpenAI
            print(f"   [openrouter failed: {e}] trying OpenAI fallback...", file=sys.stderr)
    if OPENAI_KEY:
        return call_openai(prompt)
    raise RuntimeError("No OPENROUTER_API_KEY or OPENAI_API_KEY set")


# ---------- validation ----------

def _canonical_tag(t, tags):
    """Case-insensitive match against the vocabulary - the model sometimes
    returns a valid tag with the wrong casing (e.g. 'guide' for 'Guide')."""
    low = str(t).strip().lower()
    for real in tags:
        if real.lower() == low:
            return real
    return None


def validate(result, folders, tags):
    """Returns (ok: bool, reason: str|None). Mutates result['tags'] in place
    to the canonical casing when a case-insensitive match is found."""
    if not isinstance(result, dict):
        return False, "non-dict-response"
    if result.get("confident") is False:
        return False, "low-confidence"
    folder = result.get("folder")
    if folder not in folders:
        return False, "bad-folder"
    rtags = result.get("tags")
    if not isinstance(rtags, list) or not (TAG_MIN <= len(rtags) <= TAG_MAX):
        return False, "bad-tag-count"
    canonical = [_canonical_tag(t, tags) for t in rtags]
    if any(c is None for c in canonical):
        return False, "bad-tag-value"
    result["tags"] = canonical
    if not result.get("title"):
        return False, "missing-title"
    return True, None


# ---------- note IO (minimal-diff writes, mirrors titles.py / fix_yaml.py pattern) ----------

BODY_EXCERPT_LEN = 1000


def _body_excerpt(body):
    """Fallback reading source for text-only notes (e.g. old Notion exports)
    that have real content in the body but no frontmatter summary field."""
    text = re.sub(r"\n{3,}", "\n\n", (body or "").strip())
    return text[:BODY_EXCERPT_LEN]


def load_note_context(path, rel, folder):
    fm, body = notes.parse_note(path)
    summary = str(fm.get("summary") or fm.get("ai_description") or "")
    used_body = False
    if len(summary.strip()) < MIN_SUMMARY_LEN:
        excerpt = _body_excerpt(body)
        if len(excerpt) >= MIN_SUMMARY_LEN:
            summary = excerpt
            used_body = True
    return {
        "path": rel,
        "abspath": path,
        "folder": folder,
        "title": str(fm.get("title") or ""),
        "summary": summary,
        "used_body_fallback": used_body,
        "search_for": str(fm.get("search_for") or ""),
        "tags": [str(t) for t in (fm.get("tags") or [])],
    }


def write_title_tags(path, new_title, new_tags, extra_flag=None):
    raw_fm, body = notes.raw_frontmatter_text(path)
    fm = raw_fm
    if new_title:
        safe_title = str(new_title).replace('"', "'")  # never emit unescaped quotes into a "..." scalar
        if re.search(r"^title:.*$", fm, re.M):
            fm = re.sub(r"^title:.*$", f'title: "{safe_title}"', fm, count=1, flags=re.M)
        else:
            fm = f'title: "{safe_title}"\n' + fm
    tag_block = "tags:\n" + "\n".join(f"  - {t}" for t in new_tags)
    # Match the whole existing list regardless of its indentation style (some
    # legacy notes use 0-indent "- x" instead of "  - x") - a partial match here
    # leaves stray dash lines dangling below the new block and breaks the YAML.
    if re.search(r"^tags:\s*\[\s*\]\s*$", fm, re.M):
        fm = re.sub(r"^tags:\s*\[\s*\]\s*$", tag_block, fm, count=1, flags=re.M)
    elif re.search(r"^tags:\n(?:\s*- .*\n?)*", fm, re.M):
        fm = re.sub(r"^tags:\n(?:\s*- .*\n?)*", tag_block + "\n", fm, count=1, flags=re.M)
    else:
        fm = fm.rstrip("\n") + "\n" + tag_block
    if extra_flag:
        fm = fm.rstrip("\n") + f'\nretag_flag: "{extra_flag}"'
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"---\n{fm.strip(chr(10))}\n---\n{body}")


# ---------- main pass ----------

def notes_in_folder(folder):
    pattern = os.path.join(RESOURCE_LIB, folder, "**", "*.md")
    for f in sorted(glob.glob(pattern, recursive=True)):
        if os.sep + ".git" + os.sep in f or "graphify-out" in f:
            continue
        yield f, os.path.relpath(f, RESOURCE_LIB)


def run(folder_names, apply, limit=None, force_folder=None, exclude=None, only_empty=False):
    exclude = set(exclude or [])
    folders, sources, tags = parse_directory()
    rows = []
    count = 0
    for folder in folder_names:
        if folder in NEVER_SCAN:
            print(f"skipping {folder} (never scanned)")
            continue
        if folder not in folders:
            print(f"WARNING: {folder!r} is not a defined folder in Directory.md — skipping")
            continue
        for path, rel in notes_in_folder(folder):
            if limit and count >= limit:
                break
            ctx = load_note_context(path, rel, folder)
            if only_empty and ctx["tags"]:
                continue
            if len(ctx["summary"].strip()) < MIN_SUMMARY_LEN:
                # Nothing to reason from — this still needs a Vision pass, but it
                # must land in Undetermined, not sit unflagged looking "checked".
                row = {**ctx, "status": "undetermined", "reason": "no-summary",
                       "new_title": None, "new_folder": None, "new_tags": None}
                if apply:
                    try:
                        new_rel = actions.move_note(rel, "Undetermined")
                        write_title_tags(os.path.join(RESOURCE_LIB, new_rel),
                                          None, ctx["tags"] or ["Misc"], extra_flag="no-summary")
                    except FileExistsError:
                        row["status"] = "undetermined-conflict-left-in-place"
                rows.append(row)
                continue
            count += 1
            try:
                result = classify(build_prompt(ctx, folders, tags))
                ok, reason = validate(result, folders, tags)
            except Exception as e:  # noqa: BLE001 - record and continue the batch
                result, ok, reason = {}, False, f"api-error:{e}"

            row = {**ctx, "new_title": result.get("title"), "new_folder": result.get("folder"),
                   "new_tags": result.get("tags"), "reason": reason}

            if not ok:
                row["status"] = "undetermined"
                if apply:
                    try:
                        new_rel = actions.move_note(rel, "Undetermined")
                        write_title_tags(os.path.join(RESOURCE_LIB, new_rel),
                                          None, ctx["tags"] or ["Misc"], extra_flag=reason)
                    except FileExistsError:
                        row["status"] = "undetermined-conflict-left-in-place"
            else:
                row["status"] = "ok"
                exempt = os.path.basename(path) in exclude
                target_folder = result["folder"] if exempt else (force_folder or result["folder"])
                row["new_folder"] = target_folder
                if apply:
                    target_path = path
                    try:
                        if target_folder != folder:
                            new_rel = actions.move_note(rel, target_folder)
                            target_path = os.path.join(RESOURCE_LIB, new_rel)
                        write_title_tags(target_path, result["title"], result["tags"])
                    except FileExistsError as e:
                        # A note with this name already lives in the target folder.
                        # Never crash the batch over one collision - route it to
                        # Undetermined (same as any other failure) instead of leaving
                        # it stranded in its original folder unflagged.
                        row["reason"] = f"name-conflict:{e}"
                        try:
                            new_rel = actions.move_note(rel, "Undetermined")
                            write_title_tags(os.path.join(RESOURCE_LIB, new_rel),
                                              None, ctx["tags"] or ["Misc"], extra_flag=row["reason"])
                            row["status"] = "undetermined"
                        except FileExistsError:
                            row["status"] = "undetermined-conflict-left-in-place"
            rows.append(row)
        if limit and count >= limit:
            break

    print_report(rows, apply)
    return rows


def print_report(rows, applied):
    undetermined = [r for r in rows if r["status"].startswith("undetermined")]
    skipped = [r for r in rows if r["status"] == "skipped-no-summary"]
    ok = [r for r in rows if r["status"] == "ok"]

    print(f"\n{'APPLIED' if applied else 'DRY RUN'} — {len(rows)} notes considered "
          f"({len(ok)} ok, {len(undetermined)} -> Undetermined, {len(skipped)} skipped/no-summary)\n")

    if undetermined:
        print(f"--- Routed to Undetermined ({len(undetermined)}) ---")
        for r in undetermined:
            print(f"  {r['path']}  [{r['reason']}]")
        print()

    print(f"--- Reclassified ({len(ok)}) ---")
    for r in ok:
        title_change = f"{r['title']!r} -> {r['new_title']!r}" if r["title"] != r["new_title"] else "(title unchanged)"
        folder_change = f"{r['folder']} -> {r['new_folder']}" if r["folder"] != r["new_folder"] else "(folder unchanged)"
        src = "  [read from body, no summary existed]" if r.get("used_body_fallback") else ""
        print(f"  {r['path']}{src}\n    {title_change}\n    {folder_change}\n    tags: {r['tags']} -> {r['new_tags']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folders", help="comma-separated folder names, e.g. Tools,Tutorials")
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    ap.add_argument("--limit", type=int, default=None, help="cap notes processed (per run, for sampling)")
    ap.add_argument("--force-folder", default=None,
                    help="one-off override: ignore the model's folder guess and use this folder "
                         "for every note that classifies OK (not a standing rule, scope it deliberately)")
    ap.add_argument("--exclude", default=None,
                    help="comma-separated filenames (basename, e.g. Foo.md) exempt from "
                         "--force-folder — still get retitled/retagged, just keep the model's own "
                         "folder pick instead of the forced one")
    ap.add_argument("--only-empty", action="store_true",
                    help="skip any note that already has tags — targets exactly the notes that "
                         "were never classified (e.g. after a scope change like adding recursion) "
                         "without re-touching or re-spending on ones already done")
    args = ap.parse_args()
    exclude = [f.strip() for f in args.exclude.split(",")] if args.exclude else None
    run([f.strip() for f in args.folders.split(",") if f.strip()], args.apply, args.limit,
        force_folder=args.force_folder, exclude=exclude, only_empty=args.only_empty)


if __name__ == "__main__":
    main()
