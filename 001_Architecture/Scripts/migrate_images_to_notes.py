# MIGRATION COMPLETE 2026-09-09 (1,028 images). Kept for reference / re-verify only.
"""
One-time migration: co-locate every Resource Library image with its note.

Before:  note in  007_Resource_Library/Tools/OpenCode.md
         image in 007_Resource_Library/Obsidian_Attachments/Visual_Assets/whatever.PNG
After:   both in  007_Resource_Library/Tools/  as  OpenCode.md + OpenCode.png

For each image-note:
  1. find its ![[embed]] and the real image file
  2. move the image into the note's own folder, renamed to <note-stem>.<lower-ext>
  3. rewrite the note's embed to match
  4. record old -> new in a manifest

Special cases:
  - image shared by >1 note  -> copy so each note gets its own; tag both 'shared-image-review'
  - note with >1 embed        -> repoint each embed to its moved sibling
  - .svg                      -> moved as-is

Usage:
  python3 migrate_images_to_notes.py --dry-run
  python3 migrate_images_to_notes.py --limit 20
  python3 migrate_images_to_notes.py
  python3 migrate_images_to_notes.py --verify
"""
import os
import re
import json
import shutil
import hashlib
import argparse
from collections import defaultdict
from datetime import datetime

RL = "/Users/tonymacbook2025/Documents/Agent-OS/007_Resource_Library"
VA = os.path.join(RL, "Obsidian_Attachments", "Visual_Assets")
MANIFEST = os.path.join(RL, "_Image_Migration_Manifest.json")
BACKUP = os.path.expanduser(
    "~/Desktop/Delete/RL_Image_Migration_Backup_" + datetime.now().strftime("%Y%m%d_%H%M"))

IMG_EXT = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg")
EMBED_RE = re.compile(r'!\[\[([^\]|]+?\.(?:png|jpg|jpeg|webp|gif|svg))\]\]', re.I)
SKIP_DIRS = {"OpenAI_History", "Obsidian_Attachments", "graphify-out", ".git"}


def all_images():
    """lowercase basename -> full path, across the whole vault."""
    idx = {}
    for root, dirs, files in os.walk(os.path.dirname(RL)):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules")]
        for f in files:
            if f.lower().endswith(IMG_EXT):
                idx.setdefault(f.lower(), os.path.join(root, f))
    return idx


def note_files():
    out = []
    for root, dirs, files in os.walk(RL):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith(".md") and not f.startswith("_"):
                out.append(os.path.join(root, f))
    return out


def add_tag(text, tag):
    if re.search(rf'^\s*-\s*{re.escape(tag)}\s*$', text, re.M):
        return text
    m = re.search(r'^(tags:\s*\n)((?:\s*-\s*.*\n)*)', text, re.M)
    if m:
        return text[:m.end()] + f"  - {tag}\n" + text[m.end():]
    # no tags block: add one after first frontmatter line
    return re.sub(r'^(---\n)', rf'\1tags:\n  - {tag}\n', text, count=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()

    if args.verify:
        return verify()

    imgs = all_images()
    notes = note_files()

    # map image basename -> list of notes embedding it
    img2notes = defaultdict(list)
    note_embeds = {}
    for nf in notes:
        t = open(nf, encoding="utf-8", errors="ignore").read()
        es = EMBED_RE.findall(t)
        if es:
            note_embeds[nf] = es
            for e in es:
                img2notes[e.strip().lower()].append(nf)

    if not args.dry_run:
        os.makedirs(BACKUP, exist_ok=True)
        shutil.copytree(VA, os.path.join(BACKUP, "Visual_Assets"), dirs_exist_ok=True)
        for nf in note_embeds:
            rel = os.path.relpath(nf, RL)
            dst = os.path.join(BACKUP, "notes", rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(nf, dst)
        print(f"backup -> {BACKUP}")

    manifest = []
    moved = copied = repointed = missing = flagged = 0
    done_notes = 0

    for nf in sorted(note_embeds):
        if args.limit and done_notes >= args.limit:
            break
        folder = os.path.dirname(nf)
        stem = os.path.splitext(os.path.basename(nf))[0]
        text = open(nf, encoding="utf-8", errors="ignore").read()
        embeds = note_embeds[nf]
        changed = False

        for i, emb in enumerate(embeds):
            src = imgs.get(emb.strip().lower())
            if not src or not os.path.exists(src):
                missing += 1
                continue
            ext = os.path.splitext(emb)[1].lower()
            new_name = f"{stem}{ext}" if i == 0 else f"{stem}-{i + 1}{ext}"
            dst = os.path.join(folder, new_name)

            shared = len(img2notes[emb.strip().lower()]) > 1
            # avoid clobbering a different image already at dst
            n = 1
            while os.path.exists(dst) and os.path.abspath(dst) != os.path.abspath(src):
                new_name = f"{stem}-{i + 1 + n}{ext}"
                dst = os.path.join(folder, new_name)
                n += 1

            action = "copy" if shared else "move"
            manifest.append({"note": os.path.relpath(nf, RL), "from": os.path.relpath(src, RL),
                             "to": os.path.relpath(dst, RL), "action": action})
            if args.dry_run:
                print(f"[{action}] {os.path.relpath(src, RL)}  ->  {os.path.relpath(dst, RL)}")
            else:
                if shared:
                    shutil.copy2(src, dst); copied += 1
                else:
                    shutil.move(src, dst); moved += 1
                    imgs[os.path.basename(dst).lower()] = dst
            text = text.replace(f"![[{emb}]]", f"![[{new_name}]]")
            changed = changed or (new_name != emb)
            if i > 0:
                repointed += 1
            if shared:
                text = add_tag(text, "shared-image-review")
                flagged += 1

        if changed and not args.dry_run:
            open(nf, "w").write(text)
        done_notes += 1

    if not args.dry_run:
        json.dump(manifest, open(MANIFEST, "w"), indent=2)
        print(f"\nmoved {moved}, copied {copied} (shared), repointed {repointed} extra embeds")
        print(f"flagged {flagged} shared-image notes, {missing} embeds had no file")
        print(f"manifest -> {MANIFEST}")
        # leftover images in Visual_Assets
        left = [f for f in os.listdir(VA) if f.lower().endswith(IMG_EXT)]
        print(f"images still in Visual_Assets: {len(left)}")
        if left:
            print("  " + ", ".join(left[:15]))
    else:
        print(f"\n[dry-run] {len(manifest)} image moves across {done_notes} notes")


def verify():
    imgs = all_images()
    notes = note_files()
    broken = beside = elsewhere = 0
    for nf in notes:
        t = open(nf, encoding="utf-8", errors="ignore").read()
        for emb in EMBED_RE.findall(t):
            p = imgs.get(emb.strip().lower())
            if not p:
                broken += 1
            elif os.path.dirname(p) == os.path.dirname(nf):
                beside += 1
            else:
                elsewhere += 1
    left = [f for f in os.listdir(VA) if f.lower().endswith(IMG_EXT)] if os.path.isdir(VA) else []
    print(f"embeds: {beside} beside their note, {elsewhere} elsewhere, {broken} broken")
    print(f"images still in Visual_Assets: {len(left)}")


if __name__ == "__main__":
    main()
