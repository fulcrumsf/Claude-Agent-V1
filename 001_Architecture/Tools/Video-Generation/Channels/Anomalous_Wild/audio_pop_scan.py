#!/usr/bin/env python3
"""
audio_pop_scan.py — pre-delivery audio-discontinuity gate for Anomalous Wild.

Catches the class of bug from Glass Frog 0003: per-segment audio (narration
scenes, beat stems, native clip audio) butt-joined without a fade, producing an
audible click/pop at the splice. Hard-concat splices show up as a single-sample
step change far larger than anything speech or music produces on its own,
especially when the surrounding audio is near-silent.

Method (per feedback_audio_verification_method — raw PCM + numpy, never astats):
  * decode to mono 48k PCM
  * |first difference| per sample = instantaneous step
  * a "pop" = a step >= --hard-threshold whose ±40ms RMS floor is < --silence-floor
    (a big step out of near-silence — the signature of a spliced edit, not a
    plosive or a musical accent)
  * additionally, at every known join timestamp (--joins, or derived from a
    production's Narration_Audio/scene_*.mp3 lengths with --production), any step
    over --join-threshold fails — a join must never carry a discontinuity.

Exit status: 0 = clean, 1 = pop(s) found, 2 = usage/IO error.

Usage:
  python3 audio_pop_scan.py <media_file>
  python3 audio_pop_scan.py <render.mp4> --production <production_folder>
  python3 audio_pop_scan.py <render.mp4> --joins 92.53,99.6,223.07
  python3 audio_pop_scan.py <audio.mp3> --json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

SR = 48000
HARD_THRESHOLD = 0.45      # |Δsample| that a clean speech/music mix never reaches
VERY_HARD_THRESHOLD = 0.60 # nothing natural steps this far in one sample — always a pop
SILENCE_FLOOR = 0.05       # ±40ms RMS below this = "near silence" around the step
JOIN_THRESHOLD = 0.25      # stricter — at a known join, even a modest step is a defect
JOIN_WINDOW_S = 0.030      # search ± this around each declared join timestamp


def decode_pcm(path: Path) -> np.ndarray:
    """Decode any media file to a mono float32 array at SR."""
    proc = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path),
         "-vn", "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode()[-2000:] or "ffmpeg decode failed")
    if not proc.stdout:
        raise RuntimeError(f"no audio stream decoded from {path}")
    return np.frombuffer(proc.stdout, dtype=np.int16).astype(np.float32) / 32768.0


def audio_duration_s(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    )
    return float(out.stdout.strip())


def derive_narration_joins(production: Path) -> list[float]:
    """Cumulative scene-boundary timestamps from Narration_Audio/scene_*.mp3 lengths."""
    audio_dir = production / "Narration_Audio"
    scenes = sorted(audio_dir.glob("scene_*.mp3")) or sorted(audio_dir.glob("Scene_*.mp3"))
    joins, cursor = [], 0.0
    for p in scenes[:-1]:  # no join after the final scene
        cursor += audio_duration_s(p)
        joins.append(round(cursor, 3))
    return joins


def local_rms(a: np.ndarray, i: int, half_win: int) -> float:
    lo, hi = max(0, i - half_win), min(len(a), i + half_win)
    seg = a[lo:hi]
    return float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0


def scan(
    a: np.ndarray,
    joins: list[float] | None = None,
    hard_threshold: float = HARD_THRESHOLD,
    silence_floor: float = SILENCE_FLOOR,
    join_threshold: float = JOIN_THRESHOLD,
) -> list[dict]:
    """Return a list of pop findings. Empty list == clean."""
    d = np.abs(np.diff(a))
    half_win = int(SR * 0.040)
    findings: list[dict] = []

    # 1. global hard steps: flagged if either far beyond anything natural
    #    (VERY_HARD, any context) or merely hard but sitting in near-silence
    #    (a spliced edit between quiet segments).
    hits = np.nonzero(d >= hard_threshold)[0]
    last_t = -1.0
    for i in hits:
        t = i / SR
        if t - last_t < 0.050:      # collapse clusters to one finding
            continue
        step = float(d[i])
        floor = local_rms(a, i, half_win)
        if step >= VERY_HARD_THRESHOLD:
            kind = "hard_step"
        elif floor < silence_floor:
            kind = "silence_bounded_step"
        else:
            continue
        findings.append({
            "t": round(t, 4), "step": round(step, 4),
            "rms_floor": round(floor, 5), "kind": kind,
        })
        last_t = t

    # 2. anything at a declared join
    for jt in joins or []:
        c = int(jt * SR)
        w = int(SR * JOIN_WINDOW_S)
        lo, hi = max(0, c - w), min(len(d), c + w)
        if hi <= lo:
            continue
        seg = d[lo:hi]
        j = int(np.argmax(seg))
        if seg[j] >= join_threshold:
            gi = lo + j
            findings.append({
                "t": round(gi / SR, 4), "step": round(float(seg[j]), 4),
                "rms_floor": round(local_rms(a, gi, half_win), 5),
                "kind": "join_discontinuity", "declared_join_s": jt,
            })

    findings.sort(key=lambda f: f["t"])
    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description="Scan a render/audio file for splice pops")
    ap.add_argument("media_file")
    ap.add_argument("--production", help="production folder — derive narration scene joins")
    ap.add_argument("--joins", help="comma-separated join timestamps in seconds")
    ap.add_argument("--hard-threshold", type=float, default=HARD_THRESHOLD)
    ap.add_argument("--silence-floor", type=float, default=SILENCE_FLOOR)
    ap.add_argument("--join-threshold", type=float, default=JOIN_THRESHOLD)
    ap.add_argument("--json", action="store_true", help="emit findings as JSON")
    args = ap.parse_args()

    path = Path(args.media_file)
    if not path.exists():
        print(f"ERROR: not found: {path}", file=sys.stderr)
        return 2

    joins: list[float] = []
    if args.production:
        joins += derive_narration_joins(Path(args.production))
    if args.joins:
        joins += [float(x) for x in args.joins.split(",") if x.strip()]

    try:
        a = decode_pcm(path)
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    findings = scan(
        a, joins,
        hard_threshold=args.hard_threshold,
        silence_floor=args.silence_floor,
        join_threshold=args.join_threshold,
    )

    if args.json:
        print(json.dumps({"file": str(path), "joins_checked": joins,
                          "findings": findings, "clean": not findings}, indent=2))
    else:
        print(f"\n=== audio_pop_scan — {path.name} ===")
        print(f"  duration {len(a)/SR:.2f}s   joins checked: {len(joins)}")
        if not findings:
            print("  ✅ CLEAN — no splice pops detected\n")
        else:
            print(f"  ❌ {len(findings)} POP(S) FOUND:")
            for f in findings:
                mmss = f"{int(f['t']//60)}:{f['t']%60:06.3f}"
                extra = f"  (declared join {f['declared_join_s']}s)" if "declared_join_s" in f else ""
                print(f"    {mmss}  step={f['step']}  rms_floor={f['rms_floor']}  "
                      f"[{f['kind']}]{extra}")
            print("\n  Fix: fade every audio segment join (fade-out/fade-in pair, ~20ms) — "
                  "never a hard concat. See AW SKILL Phase 8.\n")

    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
