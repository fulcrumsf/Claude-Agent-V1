#!/usr/bin/env python3
"""
analyze_stems.py — LUFS loudness analysis and gain correction for generated audio stems.

The problem with static volume multipliers: ElevenLabs generates clips at wildly
different loudness levels. A volcanic roar at volume=0.9 will still blow out the
narration. This script measures each clip's actual LUFS (Loudness Units Full Scale)
and calculates the exact dB gain correction needed to normalize every clip to a
consistent loudness target. Results are written back into the stem map so mix_stems.py
applies real measured values, not guesses.

How it works (same as a sound engineer at the board):
  1. Play each clip through an ebur128 loudness meter (via ffmpeg loudnorm)
  2. Read integrated LUFS — the perceptual loudness your ears actually hear
  3. Calculate: gain_db = target_lufs - measured_lufs
  4. Apply scene-class creative offset on top (PeakTension clips sit higher than Resolution)
  5. Clamp gain to safe range, convert to linear volume multiplier
  6. Write corrected values back to stem map JSON

Usage:
  python3 analyze_stems.py <production_folder>
  python3 analyze_stems.py <production_folder> --stems-file Data/per_scene_stem_map.json
  python3 analyze_stems.py <production_folder> --target-lufs -20 --dry-run

Target LUFS reference:
  SFX bed base:   -20 LUFS  (leaves headroom for narration)
  Narration:      -14 LUFS  (YouTube standard — sits clearly on top)
  Music bed:      -28 LUFS  (ambient, never competes)
"""

import argparse
import json
import math
import re
import subprocess
import sys
from pathlib import Path


# Scene-class creative offset applied on top of normalization (dB)
# Positive = louder than base, negative = quieter
SCENE_CLASS_OFFSET_DB = {
    "PeakTension":  0.0,   # eruption, pyroclastic — full level, they're meant to hit hard
    "RisingAction": -2.0,  # building tension — slightly under narration
    "Climax":       -3.0,  # survivor scenes — emotional, not overwhelming
    "Establishing": -4.0,  # ambient city/ruin beds — background texture
    "Resolution":   -6.0,  # quiet reflective scenes — barely there
    "Outro":        -9.0,  # fade to silence territory
}

MAX_BOOST_DB  =  10.0   # never boost more than 10 dB (avoids noise amplification)
MAX_CUT_DB    = -24.0   # never cut more than 24 dB


def measure_lufs(audio_path: Path) -> float | None:
    """
    Measure integrated LUFS of an audio file using ffmpeg loudnorm.
    Returns LUFS as a negative float (e.g. -18.3), or None on failure.
    """
    result = subprocess.run(
        [
            "ffmpeg", "-i", str(audio_path),
            "-af", "loudnorm=I=-16:LRA=11:TP=-1.5:print_format=json",
            "-f", "null", "-",
        ],
        capture_output=True,
        text=True,
    )
    # ffmpeg writes loudnorm JSON to stderr
    stderr = result.stderr
    # Find the JSON block
    match = re.search(r'\{[^{}]+\}', stderr, re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group())
        return float(data["input_i"])
    except (KeyError, ValueError, json.JSONDecodeError):
        return None


def gain_db_for_clip(measured_lufs: float, target_lufs: float, scene_class: str) -> float:
    """Calculate total gain in dB: normalization delta + scene-class creative offset."""
    normalization_db = target_lufs - measured_lufs
    creative_offset  = SCENE_CLASS_OFFSET_DB.get(scene_class, -3.0)
    total_db = normalization_db + creative_offset
    return max(MAX_CUT_DB, min(MAX_BOOST_DB, total_db))


def db_to_linear(db: float) -> float:
    return 10 ** (db / 20.0)


def main():
    parser = argparse.ArgumentParser(
        description="Measure LUFS per stem and write corrected gain values to stem map"
    )
    parser.add_argument("production_folder", help="Path to production folder")
    parser.add_argument("--stems-file", default="Data/per_scene_stem_map.json",
                        help="Stem map JSON to analyze (default: Data/per_scene_stem_map.json)")
    parser.add_argument("--target-lufs", type=float, default=-20.0,
                        help="Target integrated LUFS for SFX bed (default: -20)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print corrections without writing to stem map")
    args = parser.parse_args()

    production_root = Path(args.production_folder).resolve()
    stem_map_path   = production_root / args.stems_file
    stems_dir       = production_root / "Audio_Stems"

    if not stem_map_path.exists():
        sys.exit(f"ERROR: stem map not found: {stem_map_path}")
    if not stems_dir.exists():
        sys.exit(f"ERROR: Audio_Stems/ not found: {stems_dir}")

    stem_map = json.loads(stem_map_path.read_text())
    stems    = stem_map["stems"]

    print(f"\n=== LUFS Analyzer — {stem_map.get('production', production_root.name)} ===")
    print(f"    Target: {args.target_lufs} LUFS base + scene-class offset")
    print(f"    Gain clamp: {MAX_CUT_DB} dB to +{MAX_BOOST_DB} dB\n")
    print(f"  {'ID':<6} {'Measured':>10} {'Gain':>8} {'Final vol':>10}  Scene class")
    print(f"  {'──':<6} {'────────':>10} {'────':>8} {'─────────':>10}  ───────────")

    changed = 0
    failed  = []

    for stem in stems:
        clip_id    = stem["id"]
        scene_cls  = stem.get("scene_class", "Establishing")
        audio_file = stems_dir / f"{clip_id}.mp3"

        if not audio_file.exists():
            print(f"  {clip_id:<6} {'MISSING':>10}")
            failed.append(clip_id)
            continue

        lufs = measure_lufs(audio_file)
        if lufs is None:
            print(f"  {clip_id:<6} {'MEASURE FAILED':>10}")
            failed.append(clip_id)
            continue

        gain_db      = gain_db_for_clip(lufs, args.target_lufs, scene_cls)
        volume_linear = db_to_linear(gain_db)
        old_volume   = stem.get("volume", 1.0)

        print(f"  {clip_id:<6} {lufs:>9.1f}L {gain_db:>+7.1f}dB {volume_linear:>10.3f}  "
              f"{scene_cls}  (was {old_volume:.3f})")

        if not args.dry_run:
            stem["volume"]        = round(volume_linear, 4)
            stem["measured_lufs"] = round(lufs, 2)
            stem["gain_db"]       = round(gain_db, 2)
            changed += 1

    print()
    if args.dry_run:
        print("=== Dry run — stem map not modified ===")
    else:
        stem_map_path.write_text(json.dumps(stem_map, indent=2))
        print(f"=== Updated {changed}/{len(stems)} stems in {stem_map_path.name} ===")

    if failed:
        print(f"Failed / missing: {', '.join(failed)}")


if __name__ == "__main__":
    main()
