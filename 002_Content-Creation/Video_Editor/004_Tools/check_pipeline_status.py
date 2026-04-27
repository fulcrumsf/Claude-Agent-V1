"""
Quick status check — shows which clips are done, pending, or missing video_looped.mp4.
Run any time to see where the pipeline is at.

Usage:
  python3 004_Tools/check_pipeline_status.py
"""

import json
from pathlib import Path

BASE         = Path("002_Channels/001_Anomalous-Wild/001_Bioluminescence-Weapon")
PROMPTS_FILE = BASE / "new_clips_prompts.json"

ORIGINAL_CLIPS = [
    "scene_01", "scene_03", "scene_04", "scene_05", "scene_06",
    "scene_07", "scene_08", "scene_09",
    "scene_10a", "scene_10b", "scene_10c",
    "scene_11",
]


def check():
    if not PROMPTS_FILE.exists():
        print(f"ERROR: {PROMPTS_FILE} not found")
        return

    entries    = json.loads(PROMPTS_FILE.read_text())
    vid_entries = [e for e in entries if e.get("generation_type") == "video"]
    img_entries = [e for e in entries if e.get("generation_type") == "image"]

    print("=" * 52)
    print(" PIPELINE STATUS")
    print("=" * 52)

    # ── Original clips ────────────────────────────────
    print("\n── ORIGINAL CLIPS (video_looped.mp4) ──")
    for sid in ORIGINAL_CLIPS:
        folder  = BASE / sid
        looped  = folder / "video_looped.mp4"
        raw     = folder / "video.mp4"
        if looped.exists():
            mb = looped.stat().st_size / (1024*1024)
            print(f"  ✓ {sid:<14} {mb:5.1f} MB")
        elif raw.exists():
            print(f"  ⚠ {sid:<14} video.mp4 exists but NOT looped yet")
        else:
            print(f"  ✗ {sid:<14} missing")

    # ── New video clips ───────────────────────────────
    by_priority = {"critical": [], "high": [], "medium": []}
    for e in vid_entries:
        by_priority.setdefault(e.get("priority", "medium"), []).append(e)

    for pri in ("critical", "high", "medium"):
        group = by_priority.get(pri, [])
        if not group:
            continue
        done_v: int = 0
        done_l: int = 0
        n_total: int = 0
        pending: list[str] = []
        for e in group:
            n_total += 1
            folder = Path(e["output_folder"])
            raw    = folder / "video.mp4"
            looped = folder / "video_looped.mp4"
            if looped.exists():
                done_l += 1
            elif raw.exists():
                done_v += 1
                pending.append(f"{e['scene_id']} (needs loop)")
            else:
                pending.append(e["scene_id"])

        label = f"NEW VIDEO — {pri.upper()}"
        print(f"\n── {label} ({done_l}/{n_total} fully ready) ──")
        for e in group:
            folder = Path(e["output_folder"])
            looped = folder / "video_looped.mp4"
            raw    = folder / "video.mp4"
            if looped.exists():
                mb = looped.stat().st_size / (1024*1024)
                print(f"  ✓ {e['scene_id']:<14} looped  {mb:5.1f} MB  [{e['model']}]")
            elif raw.exists():
                mb = raw.stat().st_size / (1024*1024)
                print(f"  ⚠ {e['scene_id']:<14} raw     {mb:5.1f} MB  — needs preloop")
            else:
                print(f"  ✗ {e['scene_id']:<14} NOT YET GENERATED  [{e['model']}]")

    # ── Images ────────────────────────────────────────
    print(f"\n── FLUX PRO IMAGES ({sum(1 for e in img_entries if (Path(e['output_folder'])/'image.png').exists())}/{len(img_entries)} done) ──")
    for e in img_entries:
        img_path = Path(e["output_folder"]) / "image.png"
        if img_path.exists():
            kb = img_path.stat().st_size / 1024
            print(f"  ✓ {e['scene_id']:<14} {kb:5.0f} KB")
        else:
            print(f"  ✗ {e['scene_id']:<14} missing")

    # ── Summary ───────────────────────────────────────
    orig_ready  = sum(1 for s in ORIGINAL_CLIPS if (BASE/s/"video_looped.mp4").exists())
    new_looped  = sum(1 for e in vid_entries if (Path(e["output_folder"])/"video_looped.mp4").exists())
    new_raw     = sum(1 for e in vid_entries if (Path(e["output_folder"])/"video.mp4").exists()
                      and not (Path(e["output_folder"])/"video_looped.mp4").exists())
    new_missing = len(vid_entries) - new_looped - new_raw
    imgs_done   = sum(1 for e in img_entries if (Path(e["output_folder"])/"image.png").exists())

    done_file = Path("/tmp/biolum_pipeline_done.txt")
    pipeline_status = done_file.read_text().strip() if done_file.exists() else "RUNNING / NOT STARTED"

    print("\n" + "=" * 52)
    print(f" SUMMARY")
    print(f"  Original clips ready : {orig_ready}/{len(ORIGINAL_CLIPS)}")
    print(f"  New clips looped     : {new_looped}/{len(vid_entries)}")
    print(f"  New clips raw only   : {new_raw}  (need preloop)")
    print(f"  New clips pending    : {new_missing}  (not generated yet)")
    print(f"  Images done          : {imgs_done}/{len(img_entries)}")
    print(f"  Pipeline signal      : {pipeline_status}")
    print("=" * 52)


if __name__ == "__main__":
    check()
