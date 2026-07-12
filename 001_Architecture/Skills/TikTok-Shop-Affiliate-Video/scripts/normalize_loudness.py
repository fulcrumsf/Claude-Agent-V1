#!/usr/bin/env python3
"""
normalize_loudness.py — Two-pass EBU R128 loudness normalization for VO audio.

TikTok Shop Creator videos in this pipeline previously muxed raw VO straight
into the final render with no loudness check. Measuring real output (2026-07-12)
showed integrated loudness around -34 to -35 LUFS — well below the ~-14 LUFS
most social platforms target, with no clipping risk at all (true peak nowhere
near 0 dBFS). This script normalizes VO to a target loudness before it gets
muxed into the video, using ffmpeg's two-pass loudnorm (measure, then apply
with the measured values) for accuracy — a single-pass loudnorm is far less
precise.

Usage:
  python3 normalize_loudness.py <input_audio> <output_audio> [--target-i -14.0] [--target-tp -1.5] [--target-lra 7.0]
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

DEFAULT_TARGET_I = -14.0
DEFAULT_TARGET_TP = -1.5
DEFAULT_TARGET_LRA = 7.0


def measure_loudness(audio_path: Path) -> dict:
    """First pass: measure the input's integrated loudness, true peak, and LRA."""
    result = subprocess.run(
        ["ffmpeg", "-i", str(audio_path),
         "-af", f"loudnorm=I={DEFAULT_TARGET_I}:TP={DEFAULT_TARGET_TP}:LRA={DEFAULT_TARGET_LRA}:print_format=json",
         "-f", "null", "-"],
        capture_output=True, text=True,
    )
    stderr = result.stderr
    json_start = stderr.rfind("{")
    json_end = stderr.rfind("}") + 1
    if json_start == -1 or json_end == 0:
        raise RuntimeError(f"Could not find loudnorm measurement JSON in ffmpeg output: {stderr[-500:]}")
    return json.loads(stderr[json_start:json_end])


def build_normalize_filter(measured: dict, target_i: float, target_tp: float, target_lra: float) -> str:
    """Second-pass filter string: apply loudnorm using the first pass's measured values (linear mode)."""
    return (
        f"loudnorm=I={target_i}:TP={target_tp}:LRA={target_lra}:"
        f"measured_I={measured['input_i']}:measured_TP={measured['input_tp']}:"
        f"measured_LRA={measured['input_lra']}:measured_thresh={measured['input_thresh']}:"
        f"offset={measured['target_offset']}:linear=true:print_format=summary"
    )


def normalize_audio(
    input_path: Path,
    output_path: Path,
    target_i: float = DEFAULT_TARGET_I,
    target_tp: float = DEFAULT_TARGET_TP,
    target_lra: float = DEFAULT_TARGET_LRA,
) -> Path:
    measured = measure_loudness(input_path)
    filt = build_normalize_filter(measured, target_i, target_tp, target_lra)
    result = subprocess.run(
        ["ffmpeg", "-i", str(input_path), "-af", filt, "-ar", "44100", str(output_path), "-y"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg normalization failed: {result.stderr[-500:]}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Two-pass loudness normalization for VO audio")
    parser.add_argument("input_audio")
    parser.add_argument("output_audio")
    parser.add_argument("--target-i", type=float, default=DEFAULT_TARGET_I)
    parser.add_argument("--target-tp", type=float, default=DEFAULT_TARGET_TP)
    parser.add_argument("--target-lra", type=float, default=DEFAULT_TARGET_LRA)
    args = parser.parse_args()

    out = normalize_audio(
        Path(args.input_audio), Path(args.output_audio),
        args.target_i, args.target_tp, args.target_lra,
    )
    after = measure_loudness(out)
    print(f"Normalized {args.input_audio} -> {out}")
    print(f"Result: {after['input_i']} LUFS integrated, {after['input_tp']} dBTP true peak")


if __name__ == "__main__":
    main()
