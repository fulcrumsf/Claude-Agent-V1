"""Grabs a single frame a couple seconds into a video (via ffmpeg) to use as
a card thumbnail for videos still sitting in 000_Ingest/ - cached so a given
video is only ever decoded once."""
import os
import sys
import hashlib
import subprocess
import pathlib
import importlib.util

_here = pathlib.Path(__file__).parent


def _load(name):
    key = f"iv_{name}"
    if key in sys.modules:
        return sys.modules[key]
    spec = importlib.util.spec_from_file_location(key, _here / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules[key] = m
    spec.loader.exec_module(m)
    return m


config = _load("config")


def _cache_path(video_abspath):
    digest = hashlib.sha256(video_abspath.encode("utf-8")).hexdigest()[:16]
    return os.path.join(config.THUMB_CACHE, digest + ".jpg")


def ensure_thumb(video_abspath, seek_seconds=2):
    if not os.path.isfile(video_abspath):
        return None
    dst = _cache_path(video_abspath)
    if os.path.isfile(dst) and os.path.getmtime(dst) >= os.path.getmtime(video_abspath):
        return dst
    os.makedirs(config.THUMB_CACHE, exist_ok=True)
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-ss", str(seek_seconds), "-i", video_abspath,
             "-frames:v", "1", "-vf", f"scale={config.THUMB_W}:-1", dst],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30,
        )
    except Exception:
        return None
    return dst if os.path.isfile(dst) else None
