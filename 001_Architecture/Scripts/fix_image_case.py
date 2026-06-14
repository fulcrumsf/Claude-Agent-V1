#!/usr/bin/env python3
"""
fix_image_case.py — Convert lowercase kebab-case image filenames in Visual_Assets
to Title-Case-With-Dashes, using the paired markdown note's title as the source of truth.

Usage:
    python3 fix_image_case.py                   # dry run — shows what would change
    python3 fix_image_case.py --apply            # rename files and update notes
    python3 fix_image_case.py --apply --since "2026-05-09"   # limit to files after date
"""

import os
import re
import sys
import argparse
from datetime import datetime

WORKSPACE = "/Users/tonymacbook2025/Documents/Agent-OS"
VISUAL_ASSETS = os.path.join(WORKSPACE, "007_Resource_Library", "Obsidian_Attachments", "Visual_Assets")
RESOURCE_LIBRARY = os.path.join(WORKSPACE, "007_Resource_Library")
RENAME_LOG = os.path.join(VISUAL_ASSETS, "rename_log.md")

CATEGORY_FOLDERS = [
    "Tools", "Tutorials", "Docs", "Investments", "Models", "Prompts",
    "Research", "Workflows", "Design_Inspiration", "Personal", "Project_Ideas",
]

IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.webp', '.gif', '.PNG', '.JPG', '.JPEG')


def is_lowercase_kebab(stem):
    """Return True if the stem is all-lowercase (needs Title-Case conversion)."""
    return stem == stem.lower() and '-' in stem


def stem_from_title(title_str):
    """Convert a frontmatter title string to Title-Case-With-Dashes."""
    # title_str is like: "Google Cloud Vision Warehouse Documentation"
    return '-'.join(w for w in title_str.replace('"', '').replace("'", '').split())


def read_note_title(note_path):
    """Extract the title field from a markdown note's YAML frontmatter."""
    try:
        with open(note_path, 'r', encoding='utf-8') as f:
            in_frontmatter = False
            for line in f:
                line = line.rstrip()
                if line == '---':
                    in_frontmatter = not in_frontmatter
                    continue
                if in_frontmatter and line.startswith('title:'):
                    val = line.split(':', 1)[1].strip().strip('"').strip("'")
                    return val
    except Exception:
        pass
    return None


def find_paired_note(img_stem):
    """Find the markdown note that embeds this image (by searching category folders)."""
    for cat in CATEGORY_FOLDERS:
        cat_dir = os.path.join(RESOURCE_LIBRARY, cat)
        if not os.path.isdir(cat_dir):
            continue
        for fname in os.listdir(cat_dir):
            if not fname.endswith('.md'):
                continue
            note_path = os.path.join(cat_dir, fname)
            try:
                with open(note_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                # Check if this note embeds the image
                if f'[[{img_stem}.' in content or f'[[{img_stem.lower()}.' in content:
                    return note_path, cat
            except Exception:
                pass
    return None, None


def update_note_embed(note_path, old_filename, new_filename):
    """Replace the ![[old]] embed with ![[new]] in the note."""
    try:
        with open(note_path, 'r', encoding='utf-8') as f:
            content = f.read()
        new_content = content.replace(f'[[{old_filename}]]', f'[[{new_filename}]]')
        if new_content != content:
            with open(note_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
    except Exception as e:
        print(f"  ERROR updating note {note_path}: {e}")
    return False


def log_fix(original, new_name):
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    line = f"- `{original}` → `{new_name}` | case-fix | {date_str}\n"
    try:
        with open(RENAME_LOG, 'a') as f:
            f.write(line)
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(description="Convert lowercase Visual_Assets filenames to Title-Case")
    parser.add_argument('--apply', action='store_true', help='Apply renames (default: dry run)')
    args = parser.parse_args()

    dry_run = not args.apply

    if dry_run:
        print("DRY RUN — pass --apply to rename files\n")

    candidates = []
    for fname in os.listdir(VISUAL_ASSETS):
        if not fname.endswith(IMAGE_EXTENSIONS):
            continue
        stem = os.path.splitext(fname)[0]
        if not is_lowercase_kebab(stem):
            continue
        candidates.append(fname)

    print(f"Found {len(candidates)} lowercase-kebab image files in Visual_Assets\n")

    renamed = 0
    skipped = 0

    for fname in sorted(candidates):
        stem, ext = os.path.splitext(fname)
        img_path = os.path.join(VISUAL_ASSETS, fname)

        # Find paired note
        note_path, category = find_paired_note(stem)

        if note_path:
            title = read_note_title(note_path)
            if title:
                new_stem = stem_from_title(title)
            else:
                # Fall back to capitalizing each word
                new_stem = '-'.join(w.capitalize() for w in stem.split('-'))
        else:
            # No note found — capitalize each word as fallback
            new_stem = '-'.join(w.capitalize() for w in stem.split('-'))

        new_fname = f"{new_stem}{ext}"
        new_path = os.path.join(VISUAL_ASSETS, new_fname)

        if new_fname == fname:
            skipped += 1
            continue

        print(f"  {fname}")
        print(f"  → {new_fname}")
        if note_path:
            print(f"     note: {os.path.relpath(note_path, WORKSPACE)}")
        else:
            print(f"     note: NOT FOUND")
        print()

        if not dry_run:
            # Rename image
            if os.path.exists(new_path) and new_path != img_path:
                print(f"  SKIP (conflict): {new_fname} already exists")
                skipped += 1
                continue
            os.rename(img_path, new_path)
            # Update note embed
            if note_path:
                update_note_embed(note_path, fname, new_fname)
            log_fix(fname, new_fname)
            renamed += 1
        else:
            renamed += 1

    action = "Would rename" if dry_run else "Renamed"
    print(f"\n{action}: {renamed} | Skipped: {skipped}")


if __name__ == '__main__':
    main()
