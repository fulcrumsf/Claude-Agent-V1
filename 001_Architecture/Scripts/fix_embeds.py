#!/usr/bin/env python3
"""
fix_embeds.py — Fix wrong-case ![[image]] embeds in 007_Resource_Library markdown notes.

Scans all .md notes, finds ![[...]] embeds whose filenames don't exactly match
a file in Visual_Assets but DO match case-insensitively, and rewrites them to
use the exact on-disk filename.

Usage:
    python3 fix_embeds.py                # dry run — shows what would change
    python3 fix_embeds.py --apply        # apply all fixes in place
"""

import os
import re
import argparse
from datetime import datetime

WORKSPACE = "/Users/tonymacbook2025/Documents/Agent-OS"
RESOURCE_LIBRARY = os.path.join(WORKSPACE, "007_Resource_Library")
VISUAL_ASSETS = os.path.join(RESOURCE_LIBRARY, "Obsidian_Attachments", "Visual_Assets")

CATEGORY_FOLDERS = [
    "Tools", "Tutorials", "Docs", "Investments", "Models", "Prompts",
    "Research", "Workflows", "Design_Inspiration", "Personal", "Project_Ideas",
]

EMBED_RE = re.compile(r'!\[\[([^\]]+)\]\]')


def build_case_map(visual_assets_dir):
    """Build a dict: lowercase_filename -> exact_on_disk_filename."""
    case_map = {}
    try:
        for fname in os.listdir(visual_assets_dir):
            case_map[fname.lower()] = fname
    except Exception as e:
        print(f"ERROR reading Visual_Assets: {e}")
    return case_map


def fix_note(note_path, case_map, apply):
    try:
        with open(note_path, 'r', encoding='utf-8') as f:
            original = f.read()
    except Exception as e:
        print(f"  ERROR reading {note_path}: {e}")
        return 0

    fixes = []

    def replace_embed(m):
        embed_name = m.group(1)
        lower = embed_name.lower()
        correct = case_map.get(lower)
        if correct and correct != embed_name:
            fixes.append((embed_name, correct))
            return f'![[{correct}]]'
        return m.group(0)

    new_content = EMBED_RE.sub(replace_embed, original)

    if fixes:
        rel = os.path.relpath(note_path, WORKSPACE)
        for bad, good in fixes:
            print(f"  {rel}: ![[{bad}]] → ![[{good}]]")
        if apply:
            with open(note_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

    return len(fixes)


def main():
    parser = argparse.ArgumentParser(description="Fix wrong-case image embeds in markdown notes")
    parser.add_argument('--apply', action='store_true', help='Apply fixes (default: dry run)')
    args = parser.parse_args()

    dry_run = not args.apply
    if dry_run:
        print("DRY RUN — pass --apply to write changes\n")

    case_map = build_case_map(VISUAL_ASSETS)
    print(f"Visual_Assets: {len(case_map)} files indexed\n")

    total_fixes = 0
    notes_fixed = 0

    for cat in CATEGORY_FOLDERS:
        cat_dir = os.path.join(RESOURCE_LIBRARY, cat)
        if not os.path.isdir(cat_dir):
            continue
        for fname in sorted(os.listdir(cat_dir)):
            if not fname.endswith('.md'):
                continue
            note_path = os.path.join(cat_dir, fname)
            n = fix_note(note_path, case_map, apply=args.apply)
            if n:
                total_fixes += n
                notes_fixed += 1

    action = "Would fix" if dry_run else "Fixed"
    print(f"\n{action}: {total_fixes} embeds across {notes_fixed} notes")


if __name__ == '__main__':
    main()
