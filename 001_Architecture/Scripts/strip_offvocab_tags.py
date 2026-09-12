#!/usr/bin/env python3
"""Strip any tag not in the locked Tag Vocabulary (Directory.md) from every
note's `tags:` YAML block. A tag that case-insensitively matches a vocab
entry is kept (canonicalized to the correct casing); everything else is
removed outright - not hidden, not filtered client-side, gone from the file.

Excludes OpenAI_History by default (frozen one-off import).

Usage:
    python3 strip_offvocab_tags.py            # dry run, prints a report
    python3 strip_offvocab_tags.py --apply     # writes changes
"""
import os
import re
import sys
import glob
import argparse
import importlib.util
import pathlib

WORKSPACE = "/Users/tonymacbook2025/Documents/Agent-OS"
RESOURCE_LIB = os.path.join(WORKSPACE, "007_Resource_Library")
VISUALIZER_DIR = pathlib.Path(WORKSPACE) / "001_Architecture/Tools/Resource-Library-Visualizer"
EXCLUDE_DIRS = {"OpenAI_History"}


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
config = _load("config")


def canonical(tag, vocab):
    low = str(tag).strip().lower()
    for real in vocab:
        if real.lower() == low:
            return real
    return None


def strip_tags_block(raw_fm, kept_tags):
    block = "tags:\n" + "\n".join(f"  - {t}" for t in kept_tags) if kept_tags else "tags: []"
    # Match the whole existing list regardless of indentation style - a partial
    # match leaves stray dash lines dangling below and breaks the YAML.
    if re.search(r"^tags:\n(?:\s*- .*\n?)*", raw_fm, re.M):
        return re.sub(r"^tags:\n(?:\s*- .*\n?)*", block + "\n", raw_fm, count=1, flags=re.M)
    if re.search(r"^tags:\s*\[\s*\]\s*$", raw_fm, re.M):
        return re.sub(r"^tags:\s*\[\s*\]\s*$", block, raw_fm, count=1, flags=re.M)
    return raw_fm.rstrip("\n") + "\n" + block


def run(apply):
    vocab = config.tag_vocabulary()
    changed, unchanged, now_empty, errors = [], 0, [], []

    for path in sorted(glob.glob(os.path.join(RESOURCE_LIB, "**", "*.md"), recursive=True)):
        rel = os.path.relpath(path, RESOURCE_LIB)
        if rel.split(os.sep)[0] in EXCLUDE_DIRS:
            continue
        try:
            fm, _ = notes.parse_note(path)
        except Exception as e:  # noqa: BLE001 - keep the batch moving
            errors.append((rel, str(e)))
            continue
        if not isinstance(fm, dict) or "tags" not in fm:
            continue
        original = [str(t) for t in (fm.get("tags") or [])]
        kept = []
        for t in original:
            c = canonical(t, vocab)
            if c and c not in kept:
                kept.append(c)
        if kept == original:
            unchanged += 1
            continue

        changed.append((rel, original, kept))
        if not kept:
            now_empty.append(rel)

        if apply:
            raw_fm, body = notes.raw_frontmatter_text(path)
            new_fm = strip_tags_block(raw_fm, kept)
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"---\n{new_fm.strip(chr(10))}\n---\n{body}")

    print(f"{'APPLIED' if apply else 'DRY RUN'} - {len(changed)} notes changed, "
          f"{unchanged} already clean, {len(errors)} errors, "
          f"{len(now_empty)} left with zero tags\n")
    for rel, orig, kept in changed[:40]:
        print(f"  {rel}\n    {orig} -> {kept}")
    if len(changed) > 40:
        print(f"  ... and {len(changed) - 40} more")
    if now_empty:
        print(f"\n--- Left with zero tags ({len(now_empty)}) ---")
        for rel in now_empty[:40]:
            print(f"  {rel}")
        if len(now_empty) > 40:
            print(f"  ... and {len(now_empty) - 40} more")
    if errors:
        print(f"\n--- Errors ({len(errors)}) ---")
        for rel, e in errors:
            print(f"  {rel}: {e}")
    return changed


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    run(args.apply)
