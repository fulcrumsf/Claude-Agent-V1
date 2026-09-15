"""Scans 000_Ingest/ (top-level + named drop zones only - never the ad-hoc
project folders, same rule as ingest/SKILL.md) and builds a card per file,
merging in whatever pre-tag state Tony has already saved for it."""
import os
import sys
import json
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

_RL_DIR = _here.parent / "Resource-Library-Visualizer"


def _load_rl(name):
    """Import a Resource-Library-Visualizer module so this tool reuses its
    already-built, already-tested logic (YouTube/image-embed detection, the
    og:image fallback) instead of a second copy that could drift out of sync."""
    key = f"rlv_{name}"
    if key in sys.modules:
        return sys.modules[key]
    spec = importlib.util.spec_from_file_location(key, _RL_DIR / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules[key] = m
    spec.loader.exec_module(m)
    return m


rl_notes = _load_rl("notes")
rl_detect = _load_rl("detect")
rl_thumbs = _load_rl("thumbs")
rl_url_preview = _load_rl("url_preview")


def _load_state():
    try:
        with open(config.STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state_entry(rel_path, entry):
    state = _load_state()
    state[rel_path] = entry
    os.makedirs(os.path.dirname(config.STATE_FILE), exist_ok=True)
    tmp = config.STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, config.STATE_FILE)


def get_state_entry(rel_path):
    return _load_state().get(rel_path, {})


def clear_state_entry(rel_path):
    state = _load_state()
    if rel_path in state:
        del state[rel_path]
        os.makedirs(os.path.dirname(config.STATE_FILE), exist_ok=True)
        with open(config.STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)


def _text_thumb_info(abspath):
    """For a bare bookmark .md, work out (source_label, thumb_kind, thumb_value)
    using the exact same detection cascade the RL Visualizer uses: embedded
    YouTube link -> local embedded image -> remote embedded image -> the
    note's own URL (resolved lazily via the og:image fallback)."""
    fm, body = rl_notes.parse_note(abspath)
    haystack = " ".join(str(fm.get(k, "")) for k in ("url", "source")) + " " + (body or "")
    yid = rl_detect.youtube_id(haystack)
    if yid:
        return "YouTube", "remote", rl_thumbs.youtube_poster_url(yid)

    local_img = rl_notes.find_sibling_image(abspath) or rl_notes.first_embed_image(body, os.path.dirname(abspath))
    if local_img:
        return "MD", "local", local_img

    remote_img = rl_notes.first_remote_image(body)
    if remote_img:
        return "MD", "remote", remote_img

    preview_url = rl_notes.first_note_url(fm, body)
    if preview_url:
        return "MD", "lazy", preview_url

    return "MD", None, None


def _kind(filename):
    low = filename.lower()
    if low.endswith(config.IMG_EXT):
        return "image"
    if low.endswith(config.VIDEO_EXT):
        return "video"
    if low.endswith(".md"):
        return "text"
    if low.endswith(".pdf"):
        return "pdf"
    return None


def build_index():
    state = _load_state()
    cards = []

    # Top-level files directly in 000_Ingest/
    scan_dirs = [("", config.INGEST_DIR)]
    for zone in config.DROP_ZONES:
        zone_path = os.path.join(config.INGEST_DIR, zone)
        if os.path.isdir(zone_path):
            scan_dirs.append((zone, zone_path))

    for prefix, dirpath in scan_dirs:
        try:
            filenames = os.listdir(dirpath)
        except OSError:
            continue
        for fn in filenames:
            if fn.startswith(".") or fn.startswith("_"):
                continue
            abspath = os.path.join(dirpath, fn)
            if not os.path.isfile(abspath):
                continue
            kind = _kind(fn)
            if kind is None:
                continue
            rel = f"{prefix}/{fn}" if prefix else fn
            entry = state.get(rel, {})

            source_label = {"image": "Screenshot", "video": "Video", "pdf": "PDF"}.get(kind, "MD")
            thumb_kind, thumb_value = None, None
            if kind == "text":
                try:
                    source_label, thumb_kind, thumb_value = _text_thumb_info(abspath)
                except Exception:
                    pass

            cards.append({
                "path": rel,
                "abspath": abspath,
                "filename": fn,
                "kind": kind,
                "zone": prefix or "(root)",
                "source_label": source_label,
                "thumb_kind": thumb_kind,
                "thumb_value": thumb_value,
                "title": entry.get("title", ""),
                "description": entry.get("description", ""),
                "url": entry.get("url", ""),
                "folder": entry.get("folder", ""),
                "tags": entry.get("tags", []),
                "note": entry.get("note", ""),
                "has_manual_data": bool(entry),
            })
    cards.sort(key=lambda c: (c["zone"], c["filename"].lower()))
    return cards
