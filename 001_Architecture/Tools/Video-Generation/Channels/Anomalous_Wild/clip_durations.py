"""
clip_durations.py — the single source of truth for how long a generated video
clip is *requested* at, and how it gets *trimmed* back to its real on-screen
target afterwards.

Why this exists (incident 0003_Glass_Frog_Transparency, 2026-08-30):
  - Seedance's `duration` is an integer number of seconds and the model
    undershoots the request by ~0.1-0.9s. Clips were requested at roughly the
    beat's target length with no headroom, then the Remotion timeline was built
    from the *planned* target number instead of the real file length. Where the
    declared length exceeded the real footage, Remotion's OffthreadVideo looped
    back to frame 0 — a hard flash-cut before every affected scene boundary.

The fix, enforced here so no pipeline stage has to remember it:
  1. request_duration() pads every clip: ceil(target) + 1s, clamped to the
     model's own [4, max] range, returned as an int ready for the API.
  2. trim_to_target() head-trims the generated clip to exactly the beat's target
     duration, and REFUSES (no output file) when the real footage is shorter
     than the target — that clip must be regenerated at a higher duration, it
     can never be silently stretched or looped.

Pure logic + ffmpeg/ffprobe subprocesses only. No API calls, no project paths.
"""

from __future__ import annotations

import math
import subprocess
from pathlib import Path

# Generation floor shared by every video model this pipeline uses. Seedance 1.5
# Pro / 2.0 / 2.0 Fast all reject anything under 4s (Seedance-Prompting-Guide,
# "Minimum duration is a hard floor").
MIN_FLOOR_S = 4

# Head/tail headroom added on top of ceil(target) before the request is sent.
# ceil() already contributes up to ~1s; +1 here covers Seedance's observed
# ~0.5s undershoot with margin. Bumping this trades API spend for fewer
# INSUFFICIENT_FOOTAGE regens (Seedance bills per generated second).
PAD_SECONDS = 1

# Tolerance when comparing real footage against the target — a clip that comes
# back a few hundredths of a second short of target is fine to trim; anything
# more is a real shortfall.
EPS_S = 0.05

# Per-model maximum accepted `duration` (seconds). Keys are matched as
# case-insensitive substrings of the model slug.
_MODEL_MAX_S = {
    "seedance-1.5-pro": 12,
    "seedance-1.5": 12,
    "seedance-2.0-fast": 15,
    "seedance-2.0": 15,
    "seedance-2": 15,
    "kling": 10,
    "veo": 8,
}
_DEFAULT_MAX_S = 12


def model_max_s(model: str | None) -> int:
    """Maximum `duration` the given model slug accepts. Defaults to 12 when the
    slug is unknown or missing (the most conservative common ceiling)."""
    if not model:
        return _DEFAULT_MAX_S
    m = model.lower()
    for key, cap in _MODEL_MAX_S.items():
        if key in m:
            return cap
    return _DEFAULT_MAX_S


def request_duration(target_s: float, model: str | None = None) -> int:
    """The integer `duration` value to send to the video API for a beat whose
    real on-screen target is `target_s` seconds.

    ceil(target) + PAD_SECONDS, clamped to the model's [MIN_FLOOR_S, max] range.
    Always an int — the APIs require it.
    """
    if target_s <= 0:
        raise ValueError(f"target_s must be positive, got {target_s!r}")
    padded = math.ceil(target_s) + PAD_SECONDS
    return max(MIN_FLOOR_S, min(model_max_s(model), padded))


def probe_duration(path: str | Path) -> float:
    """Real container duration of a media file, in seconds, via ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    )
    try:
        return float(result.stdout.strip())
    except ValueError as exc:
        raise RuntimeError(
            f"ffprobe could not read a duration from {path}: "
            f"{result.stderr.strip() or result.stdout.strip()!r}"
        ) from exc


def trim_to_target(src: str | Path, dst: str | Path, target_s: float) -> dict:
    """Head-trim `src` to at most `target_s` seconds → `dst`, video-only, clean
    keyframes (matches the pipeline's existing preloop encode).

    Head-trim (keep the first N seconds), not centre: the risk being eliminated
    is overrun past the *end*, the clip's first frame is the anchored
    composition worth keeping, and any audio extracted from the raw clip stays
    aligned at t=0.

    When the generated footage is shorter than `target_s`, the clip is kept at
    its real length and `needs_fill` / `shortfall_s` are set — assembly then
    holds the last frame for the gap (VideoSegFilled). It is NEVER looped and
    NEVER regenerated (Tony, 2026-08-30: padding should make it right the first
    time; paying to re-roll is not the fallback).

    Returns:
        {"ok": True, "real_s", "final_s", "trim_offset_s": 0.0,
         "needs_fill": bool, "shortfall_s": float}
    or on a genuine ffmpeg failure:
        {"ok": False, "real_s", "target_s", "reason": "FFMPEG_TRIM_FAILED ..."}
    """
    src, dst = Path(src), Path(dst)
    real_s = probe_duration(src)

    keep_s = min(real_s, target_s)
    needs_fill = real_s < target_s - EPS_S
    shortfall_s = round(max(0.0, target_s - real_s), 3)

    dst.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([
        "ffmpeg", "-y",
        "-i", str(src),
        "-t", f"{keep_s:.3f}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-an",
        str(dst), "-loglevel", "error",
    ])
    if r.returncode != 0:
        return {
            "ok": False,
            "real_s": real_s,
            "target_s": target_s,
            "reason": f"FFMPEG_TRIM_FAILED (exit {r.returncode})",
        }
    return {
        "ok": True,
        "real_s": real_s,
        "final_s": round(keep_s, 3),
        "trim_offset_s": 0.0,
        "needs_fill": needs_fill,
        "shortfall_s": shortfall_s,
    }
