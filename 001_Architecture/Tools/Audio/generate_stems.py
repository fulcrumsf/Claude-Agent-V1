#!/usr/bin/env python3
"""
generate_stems.py — Audio stem generator for video productions.

Reads Data/stem_map.json from a production folder, generates each stem via
ElevenLabs SFX API, and saves them to Audio_Stems/.

Stems longer than 28s are automatically split into overlapping chunks and
crossfaded together with ffmpeg.

Usage:
  python3 generate_stems.py <production_folder> [--stems id1 id2] [--overwrite]

Inputs:
  <production_folder>/Data/stem_map.json

Outputs:
  <production_folder>/Audio_Stems/<stem_id>.mp3

ElevenLabs SFX limits:
  - Max 30s per call — script caps chunks at 28s for safety
  - Stems > 28s are generated in overlapping chunks and crossfaded
"""

import argparse
import json
import math
import os
import shutil
import subprocess
import sys

from pathlib import Path

import requests

MAX_ELEVENLABS_S = 28   # 2s under the 30s hard limit
CHUNK_OVERLAP_S  = 4    # overlap between chunks for crossfade seam


def load_api_key():
    result = subprocess.run(
        "source ~/.env-secrets && echo $ELEVENLABS_API_KEY",
        shell=True, executable="/bin/zsh", capture_output=True, text=True
    )
    key = result.stdout.strip()
    if key:
        os.environ["ELEVENLABS_API_KEY"] = key
    return os.environ.get("ELEVENLABS_API_KEY", "")


def generate_sfx(prompt, duration_s, api_key):
    """Call ElevenLabs sound-generation API. Returns raw audio bytes (mp3)."""
    duration_s = min(float(duration_s), 30.0)
    resp = requests.post(
        "https://api.elevenlabs.io/v1/sound-generation",
        headers={"xi-api-key": api_key, "Content-Type": "application/json"},
        json={"text": prompt, "duration_seconds": duration_s, "prompt_influence": 0.3},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.content


def crossfade_chunks(chunk_paths, overlap_s, output_path, tmp_dir):
    """Merge a list of audio chunk paths with crossfade. Saves to output_path."""
    if len(chunk_paths) == 1:
        shutil.copy(chunk_paths[0], output_path)
        return

    current = chunk_paths[0]
    for i, next_chunk in enumerate(chunk_paths[1:], 1):
        merged = tmp_dir / f"_cf_{i}.mp3"
        result = subprocess.run([
            "ffmpeg", "-y",
            "-i", str(current),
            "-i", str(next_chunk),
            "-filter_complex", f"acrossfade=d={overlap_s}:c1=tri:c2=tri",
            "-c:a", "libmp3lame", "-b:a", "192k",
            str(merged)
        ], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg crossfade failed:\n{result.stderr[-1000:]}")
        current = merged

    shutil.copy(str(current), str(output_path))


def generate_stem(stem, output_dir, api_key, overwrite, tmp_dir):
    """Generate one stem. Returns True on success, False on failure."""
    stem_id   = stem["id"]
    label     = stem["label"]
    prompt    = stem["prompt"]
    duration_s = stem["out_s"] - stem["in_s"]
    out_path  = output_dir / f"{stem_id}.mp3"

    if out_path.exists() and not overwrite:
        print(f"  SKIP {stem_id} — exists (use --overwrite to regenerate)", flush=True)
        return True

    print(f"\n  [{stem_id}] {label} — {duration_s}s", flush=True)

    try:
        if duration_s <= MAX_ELEVENLABS_S:
            print(f"    → ElevenLabs SFX ({duration_s}s): {prompt[:80]}...", flush=True)
            audio = generate_sfx(prompt, duration_s, api_key)
            out_path.write_bytes(audio)
            print(f"    ✓ Saved {out_path.name} ({len(audio)//1000} KB)", flush=True)

        else:
            # Multi-chunk: generate overlapping chunks, crossfade together
            step = MAX_ELEVENLABS_S - CHUNK_OVERLAP_S
            n_chunks = math.ceil((duration_s - CHUNK_OVERLAP_S) / step)
            print(f"    → {duration_s}s exceeds {MAX_ELEVENLABS_S}s limit — generating {n_chunks} chunks", flush=True)

            chunk_paths = []
            for i in range(n_chunks):
                chunk_start = i * step
                remaining   = duration_s - chunk_start
                chunk_dur   = min(MAX_ELEVENLABS_S, remaining)
                chunk_dur   = min(chunk_dur, 30.0)

                print(f"    → Chunk {i+1}/{n_chunks} ({chunk_dur:.0f}s): {prompt[:60]}...", flush=True)
                audio = generate_sfx(prompt, chunk_dur, api_key)
                chunk_path = tmp_dir / f"{stem_id}_chunk{i+1}.mp3"
                chunk_path.write_bytes(audio)
                chunk_paths.append(chunk_path)

            crossfade_chunks(chunk_paths, CHUNK_OVERLAP_S, out_path, tmp_dir)
            print(f"    ✓ Saved {out_path.name} ({out_path.stat().st_size//1000} KB)", flush=True)

        return True

    except Exception as e:
        print(f"    ✗ FAILED: {e}", flush=True)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate audio stems from Data/stem_map.json via ElevenLabs SFX"
    )
    parser.add_argument("production_folder", help="Path to production folder")
    parser.add_argument("--stems-file", default="Data/stem_map.json",
                        help="Stem map JSON to use (default: Data/stem_map.json)")
    parser.add_argument("--stems", nargs="+", metavar="ID",
                        help="Only generate specific stem IDs (e.g. --stems c1 c2)")
    parser.add_argument("--overwrite", action="store_true",
                        help="Regenerate stems even if output file already exists")
    args = parser.parse_args()

    production_root = Path(args.production_folder).resolve()
    if not production_root.exists():
        sys.exit(f"ERROR: Folder not found: {production_root}")

    stem_map_path = production_root / args.stems_file
    if not stem_map_path.exists():
        sys.exit(f"ERROR: stem map not found at {stem_map_path}")

    stem_map = json.loads(stem_map_path.read_text())
    stems = stem_map["stems"]

    if args.stems:
        stems = [s for s in stems if s["id"] in args.stems]
        if not stems:
            sys.exit(f"ERROR: No stems matched: {args.stems}")

    api_key = load_api_key()
    if not api_key:
        sys.exit("ERROR: ELEVENLABS_API_KEY not found in ~/.env-secrets")

    output_dir = production_root / "Audio_Stems"
    output_dir.mkdir(exist_ok=True)

    tmp_dir = output_dir / "_tmp"
    tmp_dir.mkdir(exist_ok=True)

    prod_name = production_root.name
    overwrite_label = " | --overwrite" if args.overwrite else ""
    print(f"\n=== Stem Generator — {prod_name} | {len(stems)} stems{overwrite_label} ===\n")

    success, failed = 0, []
    for stem in stems:
        ok = generate_stem(stem, output_dir, api_key, args.overwrite, tmp_dir)
        if ok:
            success += 1
        else:
            failed.append(stem["id"])

    shutil.rmtree(tmp_dir, ignore_errors=True)

    print(f"\n=== Done: {success}/{len(stems)} succeeded ===")
    if failed:
        print(f"Failed: {', '.join(failed)} — re-run to retry")


if __name__ == "__main__":
    main()
