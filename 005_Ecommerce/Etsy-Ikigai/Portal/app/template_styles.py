"""Style assignment for the Templates tab (Tony, 2026-11-08).

Vocabulary = the style/theme sections of the Ikigai Etsy shop (config/template_styles.json "vocabulary"; fetched with
Etsy API v3 getShopSections). One JSON file holds everything, manual and auto kept apart:
  "manual": {template rel path: [labels]}   Tony's clicks; ALWAYS win, an empty list means "no style" on purpose
  "auto":   {template rel path: {"styles": [...], "key": thumbnail key, "model": ..., "tokens": n}}
Auto = one cheap vision call (Gemini flash-lite, GEMINI_API_KEY from env / ~/.env-secrets, never printed) on the cached
4:3 thumbnail, cached per thumbnail key so each image is classified once (a changed PSD gets a new key).
"""
import base64
import json
import os
import re
import threading
import urllib.request
from pathlib import Path

from .db import ROOT

FILE = ROOT / "config" / "template_styles.json"
MODEL = "gemini-3.5-flash-lite"
_lock = threading.RLock()
_job = {"running": False, "done": 0, "failed": 0, "tokens": 0}


def load(path=None):
    with _lock:
        return json.loads(Path(path or FILE).read_text())


def save(data, path=None):
    p = Path(path or FILE)
    with _lock:
        tmp = p.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
        tmp.replace(p)


def labels(data):
    return [v["label"] for v in data.get("vocabulary", [])]


def resolve(data, rel, key=None):
    """{"styles", "source": manual|auto|none, "auto": [...]}. Manual wins; an auto guess for an older thumbnail
    (different key) is still shown until the new one is classified."""
    auto = (data.get("auto") or {}).get(rel) or {}
    a = [s for s in auto.get("styles", []) if s in labels(data)]
    if rel in (data.get("manual") or {}):
        return {"styles": data["manual"][rel], "source": "manual", "auto": a}
    if a:
        return {"styles": a, "source": "auto", "auto": a}
    return {"styles": [], "source": "none", "auto": []}


def set_manual(rel, styles, path=None):
    """Tony's choice for one template (multi-select). Unknown labels are refused. Returns the resolved styles."""
    with _lock:
        data = load(path)
        bad = [s for s in styles if s not in labels(data)]
        if bad:
            raise ValueError(f"not a shop style: {', '.join(bad)}")
        ordered = [s for s in labels(data) if s in styles]
        data.setdefault("manual", {})[rel] = ordered
        save(data, path)
        return resolve(data, rel)


def clear_manual(rel, path=None):
    """Back to the auto guess."""
    with _lock:
        data = load(path)
        (data.get("manual") or {}).pop(rel, None)
        save(data, path)
        return resolve(data, rel)


def confirm_auto(rel, path=None):
    """One click: the auto guess becomes Tony's manual choice."""
    with _lock:
        data = load(path)
        return set_manual(rel, resolve(data, rel)["auto"], path)


# ---------- auto: vision guess ----------

def _gemini_key():
    v = os.environ.get("GEMINI_API_KEY", "")
    f = Path("~/.env-secrets").expanduser()
    if not v and f.is_file():
        for line in f.read_text().splitlines():
            m = re.match(r"\s*(?:export\s+)?GEMINI_API_KEY=(.*)", line)
            if m:
                v = m.group(1).strip().strip("'\"")
    return v


def gemini_classify(image_path, vocab, model=MODEL, timeout=60, prompt=None):
    """Ask a cheap vision model which shop styles suit this room (or, with `prompt`, anything else picked from the
    vocabulary). Returns (styles, tokens)."""
    key = _gemini_key()
    if not key:
        raise RuntimeError("GEMINI_API_KEY is not set")
    prompt = prompt or ("This is a room mockup with an empty grey placeholder in a picture frame; the placeholder will hold a "
              "wall-art print. Which of these Etsy shop styles would sell well shown in this room? Match the room's "
              "purpose and props first (a bar cart or kitchen suits Food-Drink, a gaming setup suits Game Room, a "
              "child's room suits Nursery), then its decor, mood and colours. Pick 1 to 3, best first, only from "
              "this list: " + "; ".join(vocab) +
              '. Answer JSON only: {"styles": ["..."]}')
    mime = "image/png" if Path(image_path).suffix.lower() == ".png" else \
        "image/webp" if Path(image_path).suffix.lower() == ".webp" else "image/jpeg"
    body = {"contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": mime, "data":
                         base64.b64encode(Path(image_path).read_bytes()).decode()}}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0}}
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": key})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        out = json.load(r)
    text = out["candidates"][0]["content"]["parts"][0]["text"]
    styles = [s for s in json.loads(text).get("styles", []) if s in vocab][:3]
    return styles, int((out.get("usageMetadata") or {}).get("totalTokenCount", 0))


ART_PROMPT = ("This is a wall-art print sold as a printable download in an Etsy shop. Which of these shop sections "
              "does it belong in? Judge the subject first (food or drink -> Food-Drink, animals -> Animals, plants or "
              "flowers -> Botanical, landscapes -> Nature, words -> Typography, gaming -> Game Room, baby-friendly -> "
              "Nursery), then the look (era, palette, technique). Pick 1 to 3, best first, only from this list: ")


def classify_art(image_path, vocab, model=MODEL, timeout=60):
    """Production tab (2026-11-08): the design's shop styles from the art itself when Tony ticks none. Same cheap
    Gemini call as the Templates tab auto-guess, art prompt instead of room prompt. Returns (styles, tokens)."""
    return gemini_classify(image_path, vocab, model, timeout,
                           ART_PROMPT + "; ".join(vocab) + '. Answer JSON only: {"styles": ["..."]}')


def classify_missing(items, classify=None, path=None):
    """items: [(rel, thumb_path, key)]. Classifies only templates with no manual choice and no auto guess for this
    key. Each result is written as soon as it arrives. Returns {"done", "failed", "tokens"}."""
    classify = classify or gemini_classify
    res = {"done": 0, "failed": 0, "tokens": 0}
    for rel, thumb, key in items:
        data = load(path)
        if rel in (data.get("manual") or {}) or ((data.get("auto") or {}).get(rel) or {}).get("key") == key:
            continue
        try:
            styles, tokens = classify(thumb, labels(data))
        except Exception:  # noqa: BLE001  (one failure must not stop the rest; retried next visit)
            res["failed"] += 1
            continue
        with _lock:
            data = load(path)
            data.setdefault("auto", {})[rel] = {"styles": styles, "key": key, "model": MODEL, "tokens": tokens}
            save(data, path)
        res["done"] += 1
        res["tokens"] += tokens
    return res


def start_auto(items, classify=None):
    with _lock:
        if _job["running"] or not items:
            return
        _job["running"] = True

    def work():
        try:
            r = classify_missing(items, classify)
            for k in ("done", "failed", "tokens"):
                _job[k] += r[k]
        finally:
            _job["running"] = False
    threading.Thread(target=work, daemon=True).start()


def job():
    return dict(_job)
