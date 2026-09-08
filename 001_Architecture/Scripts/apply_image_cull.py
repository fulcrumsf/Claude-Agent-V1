"""
Apply an image-cull decision list from build_image_cull.html.

Reads a list of `DELETE<tab>image_rel_path[<tab>note_rel_path]` lines and MOVES
each image (and its note, if any) out of 007_Resource_Library into
~/Desktop/Delete/RL_Image_Cull/, preserving folder structure. Reversible until
you empty that folder.

Usage:
  python3 001_Architecture/Scripts/apply_image_cull.py ~/Downloads/rl_image_cull.txt
  python3 001_Architecture/Scripts/apply_image_cull.py --dry-run <file>
"""
import os
import sys
import shutil
import argparse

WORKSPACE = "/Users/tonymacbook2025/Documents/Agent-OS"
RESOURCE_LIB = os.path.join(WORKSPACE, "007_Resource_Library")
DEST = os.path.expanduser("~/Desktop/Delete/RL_Image_Cull")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("list_file")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    lines = [l.rstrip("\n") for l in open(args.list_file) if l.strip() and l.startswith("DELETE")]
    imgs = notes = missing = bytes_moved = 0
    seen_notes = set()

    for line in lines:
        parts = line.split("\t")
        img_rel = parts[1]
        note_rel = parts[2] if len(parts) > 2 else None

        img_src = os.path.join(RESOURCE_LIB, img_rel)
        if os.path.exists(img_src):
            bytes_moved += os.path.getsize(img_src)
            if not args.dry_run:
                dst = os.path.join(DEST, img_rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.move(img_src, dst)
            imgs += 1
        else:
            missing += 1

        if note_rel and note_rel not in seen_notes:
            seen_notes.add(note_rel)
            note_src = os.path.join(RESOURCE_LIB, note_rel)
            if os.path.exists(note_src):
                if not args.dry_run:
                    dst = os.path.join(DEST, note_rel)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.move(note_src, dst)
                notes += 1

    verb = "would move" if args.dry_run else "moved"
    print(f"{verb}: {imgs} images ({bytes_moved/1e9:.2f} GB) + {notes} notes -> {DEST}")
    if missing:
        print(f"  ({missing} images already gone / not found)")


if __name__ == "__main__":
    main()
