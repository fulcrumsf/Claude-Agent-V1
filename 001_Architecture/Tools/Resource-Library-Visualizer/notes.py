import os
import re
import sys
import glob
import datetime
import importlib.util
import pathlib
import yaml

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
detect = _load("detect")

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.S)
EMBED_RE = re.compile(r"!\[\[([^\]|]+?\.(?:png|jpe?g|webp|gif))", re.I)
MD_IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)]+?\.(?:png|jpe?g|webp|gif))\)", re.I)


def parse_note(path):
    text = open(path, encoding="utf-8", errors="ignore").read()
    m = FM_RE.match(text)
    if not m:
        return {}, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
        if not isinstance(fm, dict):
            return {}, text
    except yaml.YAMLError:
        return {}, text
    return fm, m.group(2)


def find_sibling_image(md_path):
    stem = os.path.splitext(md_path)[0]
    for ext in config.IMG_EXT:
        if os.path.isfile(stem + ext):
            return stem + ext
    return None


def first_embed_image(body, md_dir):
    for rx in (EMBED_RE, MD_IMG_RE):
        m = rx.search(body or "")
        if not m:
            continue
        name = os.path.basename(m.group(1).strip())
        cand = os.path.join(md_dir, name)
        if os.path.isfile(cand):
            return cand
    return None


def _ingested_at(fm, path):
    for k in ("enriched", "created"):
        v = fm.get(k)
        if v:
            return str(v)[:10]
    return datetime.date.fromtimestamp(os.path.getmtime(path)).isoformat()


def _folder(rel):
    parts = rel.split(os.sep)
    return parts[0] if len(parts) > 1 else ""


def build_index(root=None):
    root = root or config.RESOURCE_LIB
    cards = []
    for f in glob.glob(os.path.join(root, "**", "*.md"), recursive=True):
        if os.sep + ".git" + os.sep in f or "graphify-out" in f:
            continue
        fm, body = parse_note(f)
        rel = os.path.relpath(f, root)
        folder = _folder(rel)
        img = find_sibling_image(f) or first_embed_image(body, os.path.dirname(f))
        yid = detect.youtube_id(
            " ".join(str(fm.get(k, "")) for k in ("url", "source")) + " " + body)
        has_image = img is not None
        structural = detect.is_structural(os.path.basename(f))
        if has_image:
            kind = "image"
        elif yid and not structural:
            kind = "youtube"
        else:
            kind = "text"
        label, risk = detect.detect_source(fm, body, os.path.basename(f), has_image)
        fm_for_glyph = dict(fm)
        fm_for_glyph["_filename"] = os.path.basename(f)
        tags = [str(t) for t in (fm.get("tags") or []) if t]
        cards.append({
            "path": rel,
            "abspath": f,
            "title": str(fm.get("title") or os.path.splitext(os.path.basename(f))[0]),
            "summary": str(fm.get("summary") or fm.get("ai_description") or ""),
            "folder": folder,
            "tags": tags,
            "kind": kind,
            "image_abspath": img,
            "youtube_id": yid,
            "source_label": label,
            "vision_risk": risk,
            "glyph_color": detect.glyph_color(fm_for_glyph, folder),
            "ingested_at": _ingested_at(fm, f),
            "has_image": has_image,
        })
    cards.sort(key=lambda c: c["ingested_at"], reverse=True)
    return cards
