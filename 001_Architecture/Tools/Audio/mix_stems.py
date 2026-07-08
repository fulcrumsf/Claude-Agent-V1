#!/usr/bin/env python3
"""
mix_stems.py — Mix generated audio stems onto the video timeline.

Reads Data/stem_map.json (or --stems-file) and Audio_Stems/*.mp3 from a
production folder. Positions each stem at its correct timestamp with S-curve
(hsin) fade-in/fade-out, then outputs:

  Assembly/stems_mix.mp3              — stems only (always written)
  Assembly/stems_narration_mix.mp3    — stems + narration (when --narration is passed)

The stems_narration_mix.mp3 is the complete standalone audio track for the
video, ready for import into any DAW or video editor without re-mixing.

Usage:
  python3 mix_stems.py <production_folder>
  python3 mix_stems.py <production_folder> --stems-file Data/per_scene_stem_map.json
  python3 mix_stems.py <production_folder> --stems-file Data/per_scene_stem_map.json \\
                       --narration Assembly/narration.mp3
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Mix Audio_Stems/ onto the timeline using Data/stem_map.json"
    )
    parser.add_argument("production_folder", help="Path to production folder")
    parser.add_argument("--volume", type=float, default=1.0,
                        help="Master volume multiplier for the stems mix (default: 1.0)")
    parser.add_argument("--stems-file", default="Data/stem_map.json",
                        help="Stem map JSON to use (default: Data/stem_map.json)")
    parser.add_argument("--narration", metavar="PATH",
                        help="Path to narration MP3. When provided, also outputs stems_narration_mix.mp3")
    args = parser.parse_args()

    production_root = Path(args.production_folder).resolve()
    stem_map_path   = production_root / args.stems_file
    if not stem_map_path.exists():
        sys.exit(f"ERROR: stem map not found: {stem_map_path}")

    stem_map         = json.loads(stem_map_path.read_text())
    total_duration_s = stem_map["total_duration_s"]
    stems            = stem_map["stems"]

    stems_dir   = production_root / "Audio_Stems"
    output_path = production_root / "Assembly" / "stems_mix.mp3"
    output_path.parent.mkdir(exist_ok=True)

    print(f"\n=== Stem Mixer — {production_root.name} ===\n")

    # Collect stems that have been generated
    available = []
    for stem in stems:
        stem_file = stems_dir / f"{stem['id']}.mp3"
        if stem_file.exists():
            available.append((stem, stem_file))
            print(f"  ✓ {stem['id']}.mp3")
        else:
            print(f"  ✗ {stem['id']}.mp3 — missing, skipping")

    if not available:
        sys.exit("ERROR: No stem files found in Audio_Stems/")

    # Build ffmpeg filter_complex:
    # For each stem: adelay to position it, afade in, afade out, atrim to prevent bleed
    inputs       = []
    filter_parts = []
    labels       = []

    for i, (stem, stem_file) in enumerate(available):
        in_s       = stem["in_s"]
        out_s      = stem["out_s"]
        fade_in_s  = stem.get("fade_in_s", 1)
        fade_out_s = stem.get("fade_out_s", 1)
        volume     = stem.get("volume", 1.0)
        delay_ms   = int(in_s * 1000)
        label      = f"s{i}"

        inputs += ["-i", str(stem_file)]

        # fade_curve: hsin = half-sine = S-curve (ease-in/ease-out). Falls back to hsin.
        curve = stem.get("fade_curve", "hsin")
        # out_s in per-scene maps is already extended by crossfade_s so the
        # generated audio has real content to fade from — no hard trim needed.
        # We soft-trim at out_s + crossfade_s to prevent runaway bleed.
        crossfade_s = stem.get("crossfade_s", fade_out_s)
        soft_trim   = out_s + crossfade_s

        chain = f"[{i}:a]adelay={delay_ms}|{delay_ms}"

        if volume != 1.0:
            chain += f",volume={volume}"

        if fade_in_s > 0:
            chain += f",afade=t=in:st={in_s}:d={fade_in_s}:curve={curve}"

        if fade_out_s > 0:
            fade_out_start = out_s - fade_out_s
            chain += f",afade=t=out:st={fade_out_start}:d={fade_out_s}:curve={curve}"

        # Soft trim: allow audio to bleed past out_s for the crossfade tail,
        # but cap at out_s + crossfade_s so clips don't run indefinitely.
        chain += f",atrim=end={soft_trim}"

        chain += f"[{label}]"
        filter_parts.append(chain)
        labels.append(f"[{label}]")

    n          = len(labels)
    mix_inputs = "".join(labels)

    if args.volume != 1.0:
        filter_parts.append(f"{mix_inputs}amix=inputs={n}:normalize=0[premix]")
        filter_parts.append(f"[premix]volume={args.volume}[mix]")
    else:
        filter_parts.append(f"{mix_inputs}amix=inputs={n}:normalize=0[mix]")

    filter_complex = ";".join(filter_parts)

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[mix]",
        "-t", str(total_duration_s),
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(output_path),
    ]

    print(f"\n  Mixing {n} stems into stems_mix.mp3...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr[-3000:])
        sys.exit("ERROR: ffmpeg stem mix failed")

    size_mb = output_path.stat().st_size / 1_000_000
    probe   = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(output_path)],
        capture_output=True, text=True,
    )
    dur = float(probe.stdout.strip() or 0)
    print(f"  ✓ stems_mix.mp3 saved ({size_mb:.1f} MB, {dur:.1f}s)")

    # --- Optional: mix stems + narration → stems_narration_mix.mp3 ---
    if args.narration:
        narration_path = Path(args.narration)
        if not narration_path.is_absolute():
            narration_path = production_root / args.narration
        if not narration_path.exists():
            print(f"\n  ✗ narration file not found: {narration_path}")
        else:
            narration_out = output_path.parent / "stems_narration_mix.mp3"
            print(f"\n  Mixing stems + narration → stems_narration_mix.mp3...")
            result = subprocess.run([
                "ffmpeg", "-y",
                "-i", str(output_path),       # stems_mix.mp3
                "-i", str(narration_path),     # narration.mp3
                "-filter_complex",
                # Narration sits at full level; stems already LUFS-corrected
                "[0:a][1:a]amix=inputs=2:normalize=0:duration=first[mix]",
                "-map", "[mix]",
                "-c:a", "libmp3lame", "-b:a", "192k",
                str(narration_out),
            ], capture_output=True, text=True)

            if result.returncode != 0:
                print(result.stderr[-2000:])
                print("  ✗ narration mix failed")
            else:
                nb_mb = narration_out.stat().st_size / 1_000_000
                probe2 = subprocess.run(
                    ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                     "-of", "csv=p=0", str(narration_out)],
                    capture_output=True, text=True,
                )
                dur2 = float(probe2.stdout.strip() or 0)
                print(f"  ✓ stems_narration_mix.mp3 saved ({nb_mb:.1f} MB, {dur2:.1f}s)")


if __name__ == "__main__":
    main()
