import os
import sys
import importlib.util
import pathlib
from PIL import Image, ImageOps

_here = pathlib.Path(__file__).parent


def _load(name):
    key = f"rlv_{name}"
    if key in sys.modules:
        return sys.modules[key]
    spec = importlib.util.spec_from_file_location(key, _here / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules[key] = m
    spec.loader.exec_module(m)
    return m


config = _load("config")


def youtube_poster_url(video_id):
    return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"


def thumb_path_for(image_abspath):
    try:
        rel = os.path.relpath(image_abspath, config.RESOURCE_LIB)
    except ValueError:
        rel = os.path.basename(image_abspath)
    if rel.startswith(".."):
        rel = os.path.basename(image_abspath)
    return os.path.join(config.THUMB_CACHE, rel + ".jpg")


def ensure_thumb(image_abspath):
    if not image_abspath or not os.path.isfile(image_abspath):
        return None
    dst = thumb_path_for(image_abspath)
    if os.path.isfile(dst) and os.path.getmtime(dst) >= os.path.getmtime(image_abspath):
        return dst
    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        im = ImageOps.exif_transpose(Image.open(image_abspath)).convert("RGB")
        if im.width > config.THUMB_W:
            im = im.resize((config.THUMB_W, max(1, round(im.height * config.THUMB_W / im.width))))
        im.save(dst, "JPEG", quality=60)
        return dst
    except Exception:
        return None
