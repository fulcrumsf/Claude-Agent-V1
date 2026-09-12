import re
import sys
import importlib.util
import pathlib

YT_RE = re.compile(
    r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([A-Za-z0-9_-]{11})")


def _markers():
    if "rlv_config" in sys.modules:
        return sys.modules["rlv_config"].STRUCTURAL_MARKERS
    p = pathlib.Path(__file__).with_name("config.py")
    spec = importlib.util.spec_from_file_location("rlv_config", p)
    m = importlib.util.module_from_spec(spec)
    sys.modules["rlv_config"] = m
    spec.loader.exec_module(m)
    return m.STRUCTURAL_MARKERS


STRUCTURAL_MARKERS = _markers()

GLYPH_PALETTE = {
    "structural": "#6b7280",   # gray-blue
    "tools":      "#2563eb",   # blue
    "models":     "#7c3aed",   # violet
    "tutorials":  "#059669",   # green
    "research":   "#d97706",   # amber
    "prompts":    "#db2777",   # pink
    "workflows":  "#0891b2",   # cyan
    "default":    "#9ca3af",   # neutral
}


def youtube_id(text):
    if not text:
        return None
    m = YT_RE.search(text)
    return m.group(1) if m else None


def is_structural(filename):
    stem = filename.lower().rsplit(".", 1)[0]
    return any(mk in stem for mk in STRUCTURAL_MARKERS)


def detect_source(fm, body, filename, has_image):
    fm = fm or {}
    tags = [str(t).lower() for t in (fm.get("tags") or [])]
    haystack = " ".join(str(fm.get(k, "")) for k in ("url", "source")) + " " + (body or "")

    if youtube_id(haystack):
        return "YouTube", False

    orig = str(fm.get("original_filename", ""))
    if re.match(r"IMG_\d+\.(png|jpe?g)$", orig, re.I):
        return "Screenshot", True

    src = str(fm.get("source", ""))
    if src.startswith("http") and has_image:
        return "Bookmark", False

    if "screenshot" in tags or has_image:
        return "Screenshot", bool(orig)

    return "MD", False


def glyph_color(fm, folder):
    if is_structural(str(fm.get("_filename", ""))):
        return GLYPH_PALETTE["structural"]
    key = (folder or "").lower()
    for name in ("tools", "models", "tutorials", "research", "prompts", "workflows"):
        if name in key:
            return GLYPH_PALETTE[name]
    t = str(fm.get("type", "")).lower()
    if "system" in t or "architecture" in t or "config" in t:
        return GLYPH_PALETTE["structural"]
    return GLYPH_PALETTE["default"]
