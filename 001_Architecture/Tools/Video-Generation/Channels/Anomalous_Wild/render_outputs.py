#!/usr/bin/env python3
"""
render_outputs.py — Sound engineer render pipeline for video productions.

Produces three video outputs from a production folder:
  1. <prod>_raw_with_stems.mp4          — raw video + stems (no narration, for stem review)
  2. <prod>_raw_with_stems_narration.mp4 — raw video + stems + narration
  3. <prod>_final.mp4                    — raw video + stems + narration + music (everything)

Professional audio levels (documentary standard):
  - Narration:  loudnorm target -14 LUFS (YouTube standard), -1 dBTP ceiling
  - SFX/Stems:  -20 LUFS in mix → volume=0.40 relative to narration
  - Music bed:  -26 LUFS in mix → volume=0.12 relative to narration (heavily ducked)
  - Stems-only: volume=0.85 (no narration competing — for monitoring/review)

Usage:
  python3 render_outputs.py <production_folder>

Inputs required (generate these first):
  Assembly/raw_video.mp4      — from assemble.py --stop-phase 2
  Assembly/stems_mix.mp3      — from mix_stems.py
  Assembly/narration.mp3      — from assemble.py --phase 3 --stop-phase 3
  Assembly/music.mp3          — from assemble.py --phase 4 --stop-phase 4

Outputs:
  Assembly/<prod>_raw_with_stems.mp4
  Assembly/<prod>_raw_with_stems_narration.mp4
  Assembly/<prod>_final.mp4
"""

import argparse
import subprocess
import sys
from pathlib import Path

# ── Professional audio levels ──────────────────────────────────────────────────

# Narration: loudnorm to -14 LUFS integrated, -1 dBTP true peak, 7 LU range
NARRATION_FILTER = "loudnorm=I=-14:TP=-1:LRA=7"

# Stems in final mix: -20 LUFS → ~6 dB below narration
STEMS_VOLUME_FULL = 0.85   # stems-only output (no narration competing)
STEMS_VOLUME_MIX  = 0.40   # stems when narration is present

# Music bed: -26 LUFS → ~12 dB below narration
MUSIC_VOLUME = 0.12

# Video encode settings
VIDEO_CRF    = 18
VIDEO_PRESET = "slow"


def run_ffmpeg(cmd, label):
    print(f"  [{label}] Encoding...", flush=True)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr[-3000:])
        sys.exit(f"ERROR: ffmpeg failed for {label}")


def check_input(path, name):
    if not path.exists():
        print(f"  ✗ MISSING: {name} → {path}")
        return False
    size_mb = path.stat().st_size / 1_000_000
    print(f"  ✓ {name} ({size_mb:.1f} MB)")
    return True


def render_stems_only(raw_video, stems_mix, output_path):
    """Output 1: raw video + stems at monitoring level (no narration)."""
    run_ffmpeg([
        "ffmpeg", "-y",
        "-i", str(raw_video),
        "-i", str(stems_mix),
        "-filter_complex",
        f"[1:a]volume={STEMS_VOLUME_FULL}[stems]",
        "-map", "0:v",
        "-map", "[stems]",
        "-c:v", "libx264", "-crf", str(VIDEO_CRF), "-preset", VIDEO_PRESET,
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(output_path),
    ], label=output_path.name)


def render_stems_and_narration(raw_video, stems_mix, narration, output_path):
    """Output 2: raw video + stems (ducked) + narration (loudnorm -14 LUFS)."""
    run_ffmpeg([
        "ffmpeg", "-y",
        "-i", str(raw_video),
        "-i", str(stems_mix),
        "-i", str(narration),
        "-filter_complex",
        (
            f"[1:a]volume={STEMS_VOLUME_MIX}[stems];"
            f"[2:a]{NARRATION_FILTER}[narr];"
            f"[stems][narr]amix=inputs=2:normalize=0[mix]"
        ),
        "-map", "0:v",
        "-map", "[mix]",
        "-c:v", "libx264", "-crf", str(VIDEO_CRF), "-preset", VIDEO_PRESET,
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(output_path),
    ], label=output_path.name)


def render_final(raw_video, stems_mix, narration, music, output_path):
    """Output 3: raw video + stems (ducked) + narration (loudnorm) + music bed."""
    run_ffmpeg([
        "ffmpeg", "-y",
        "-i", str(raw_video),
        "-i", str(stems_mix),
        "-i", str(narration),
        "-i", str(music),
        "-filter_complex",
        (
            f"[1:a]volume={STEMS_VOLUME_MIX}[stems];"
            f"[2:a]{NARRATION_FILTER}[narr];"
            f"[3:a]volume={MUSIC_VOLUME}[music];"
            f"[stems][narr][music]amix=inputs=3:normalize=0[mix]"
        ),
        "-map", "0:v",
        "-map", "[mix]",
        "-c:v", "libx264", "-crf", str(VIDEO_CRF), "-preset", VIDEO_PRESET,
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(output_path),
    ], label=output_path.name)


def probe_duration(path):
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    )
    return float(result.stdout.strip() or 0)


def main():
    parser = argparse.ArgumentParser(
        description="Render 3 video outputs with professional audio mixing"
    )
    parser.add_argument("production_folder", help="Path to production folder")
    args = parser.parse_args()

    production_root = Path(args.production_folder).resolve()
    if not production_root.exists():
        sys.exit(f"ERROR: Folder not found: {production_root}")

    assembly = production_root / "Assembly"
    prod_name = production_root.name

    raw_video  = assembly / "raw_video.mp4"
    stems_mix  = assembly / "stems_mix.mp3"
    narration  = assembly / "narration.mp3"
    music      = assembly / "music.mp3"

    out_stems_only = assembly / f"{prod_name}_raw_with_stems.mp4"
    out_stems_narr = assembly / f"{prod_name}_raw_with_stems_narration.mp4"
    out_final      = assembly / f"{prod_name}_final.mp4"

    print(f"\n=== Render Outputs — {prod_name} ===\n")
    print("Checking inputs:")
    ok_video    = check_input(raw_video,  "raw_video.mp4")
    ok_stems    = check_input(stems_mix,  "stems_mix.mp3")
    ok_narr     = check_input(narration,  "narration.mp3")
    ok_music    = check_input(music,      "music.mp3")

    if not ok_video or not ok_stems:
        sys.exit("\nERROR: raw_video.mp4 and stems_mix.mp3 are required. Generate them first.")

    print(f"\nAudio levels:")
    print(f"  Narration : loudnorm -14 LUFS / -1 dBTP (YouTube standard)")
    print(f"  Stems     : {STEMS_VOLUME_MIX:.0%} in mix ({STEMS_VOLUME_FULL:.0%} in stems-only output)")
    print(f"  Music bed : {MUSIC_VOLUME:.0%} (heavily ducked under narration)\n")

    # Output 1: video + stems
    print("── Output 1: Raw video + stems ──")
    render_stems_only(raw_video, stems_mix, out_stems_only)
    dur = probe_duration(out_stems_only)
    print(f"  ✓ {out_stems_only.name} ({out_stems_only.stat().st_size/1_000_000:.0f} MB, {dur:.1f}s)\n")

    # Output 2: video + stems + narration
    if ok_narr:
        print("── Output 2: Raw video + stems + narration ──")
        render_stems_and_narration(raw_video, stems_mix, narration, out_stems_narr)
        dur = probe_duration(out_stems_narr)
        print(f"  ✓ {out_stems_narr.name} ({out_stems_narr.stat().st_size/1_000_000:.0f} MB, {dur:.1f}s)\n")
    else:
        print("── Output 2: SKIPPED (narration.mp3 missing) ──\n")

    # Output 3: video + stems + narration + music
    if ok_narr and ok_music:
        print("── Output 3: Final (video + stems + narration + music) ──")
        render_final(raw_video, stems_mix, narration, music, out_final)
        dur = probe_duration(out_final)
        print(f"  ✓ {out_final.name} ({out_final.stat().st_size/1_000_000:.0f} MB, {dur:.1f}s)\n")
    else:
        missing = []
        if not ok_narr:  missing.append("narration.mp3")
        if not ok_music: missing.append("music.mp3")
        print(f"── Output 3: SKIPPED ({', '.join(missing)} missing) ──\n")

    print("=== Render complete ===")
    print(f"  Assembly/{prod_name}_raw_with_stems.mp4")
    if ok_narr:
        print(f"  Assembly/{prod_name}_raw_with_stems_narration.mp4")
    if ok_narr and ok_music:
        print(f"  Assembly/{prod_name}_final.mp4")


if __name__ == "__main__":
    main()
