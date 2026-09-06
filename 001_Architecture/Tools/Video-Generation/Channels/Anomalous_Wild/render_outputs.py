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

# Stems/music targets are hit with loudnorm (not a static volume multiplier) —
# a fixed multiplier only lands on target for the loudness the constant was
# originally calibrated against; different stem beds / Suno tracks measure at
# very different raw LUFS, so a static gain silently drifts off the locked
# target (confirmed drifting ~5-11dB off target on the 0003 production mix).
# Lowered from -20 on 2026-09-04 (Tony, on the 0003 Glass Frog v2a ambience bed):
# SFX/ambience should sit "a hair lower in volume than the soundtrack" (-22 music).
# The video-to-audio bed (generate_stems_v2a.py) is denser than the old sparse
# ElevenLabs stems, so it also gets a gentle duck under narration now.
STEMS_FILTER = "loudnorm=I=-25:TP=-4:LRA=11"
STEMS_SIDECHAIN_FILTER = "sidechaincompress=threshold=0.06:ratio=2:attack=350:release=700"

# Music bed: -22 LUFS → ~8 dB below narration. Raised from -26 on 2026-09-03 after
# Tony judged the score too quiet and the duck too strong on 0003 Glass Frog —
# A/B confirmed by ear. See Global_Agent_Memory "Audio Mix Formula".
MUSIC_FILTER = "loudnorm=I=-22:TP=-4:LRA=11"

# Each layer above is individually peak-limited via loudnorm, but amix(normalize=0)
# sums them without any ceiling on the combined signal — independently-safe streams
# can still exceed 0 dBFS (and blow past -1 dBTP) once added together. Confirmed live
# 2026-08-29: a real mix measured +0.1 dBTP after amix despite every input being
# individually loudnorm'd under its own TP target. Fix: a brickwall limiter on the
# mixed output. Target -1.8 dBTP (not -1.0) because alimiter operates in the sample
# domain, not oversampled — plain sample-peak limiting to exactly -1 dBTP still left
# measured true peak at -0.9 dBTP (inter-sample peaks slip through), so the extra
# ~0.8dB of margin is deliberate, not arbitrary.
FINAL_LIMITER = "alimiter=limit=0.8128:attack=5:release=50:level=disabled"

# Sidechain duck: music ducks further under narration (locked mix formula,
# see Global_Agent_Memory.md "Audio Mix Formula"). Softened on 2026-09-03 (Tony,
# A/B by ear on 0003): threshold 0.015->0.045 (~-27 dBFS, so only sustained speech
# triggers a full duck, not every breath/consonant), ratio 4->2.5 (~4-5 dB duck
# instead of 10+), attack 150->300ms (eases in instead of clamping — kills the
# "ducks in abruptly" feel), release 800->600ms (breathes back between sentences).
SIDECHAIN_FILTER = "sidechaincompress=threshold=0.045:ratio=2.5:attack=300:release=600"

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
            f"[1:a]{STEMS_FILTER}[stems];"
            f"[2:a]{NARRATION_FILTER}[narr];"
            f"[stems][narr]amix=inputs=2:normalize=0[mixed];"
            f"[mixed]{FINAL_LIMITER}[mix]"
        ),
        "-map", "0:v",
        "-map", "[mix]",
        "-c:v", "libx264", "-crf", str(VIDEO_CRF), "-preset", VIDEO_PRESET,
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(output_path),
    ], label=output_path.name)


def render_final(raw_video, stems_mix, narration, music, output_path):
    """Output 3: raw video + stems (ducked) + narration (loudnorm) + music bed
    (music additionally sidechain-ducked under narration)."""
    run_ffmpeg([
        "ffmpeg", "-y",
        "-i", str(raw_video),
        "-i", str(stems_mix),
        "-i", str(narration),
        "-i", str(music),
        "-filter_complex",
        (
            f"[1:a]{STEMS_FILTER}[stems_pre];"
            f"[2:a]{NARRATION_FILTER}[narr];"
            f"[narr]asplit=3[narr_out][narr_sc][narr_sc2];"
            f"[stems_pre][narr_sc2]{STEMS_SIDECHAIN_FILTER}[stems];"
            f"[3:a]{MUSIC_FILTER}[music_pre];"
            f"[music_pre][narr_sc]{SIDECHAIN_FILTER}[music];"
            f"[stems][narr_out][music]amix=inputs=3:normalize=0[mixed];"
            f"[mixed]{FINAL_LIMITER}[mix]"
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
    print(f"  Stems     : {STEMS_FILTER} in mix ({STEMS_VOLUME_FULL:.0%} in stems-only output)")
    print(f"  Music bed : {MUSIC_FILTER} + sidechain duck under narration\n")

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
