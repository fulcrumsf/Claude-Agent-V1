"""Output scan of a generated room scene (realism addendum section 6, 2026-11-20): stray text, interface buttons,
watermarks, logos, a second frame or a mirror, and the insert marker colour leaking outside the art. Free: macOS Vision
OCR through a small compiled Swift tool (app/text_scan.swift) on overlapping upscaled tiles, plus one cheap Gemini
flash-lite vision call (no kie.ai credits).

  ocr_findings(png)              6 x 4 tiles, 20% overlap, 3x Lanczos, boxes mapped back, duplicates merged
  gemini_findings(png, ask=None) [{type, box_2d, confidence}] (ask injectable for tests)
  marker_leak(rgb, quad, marker) share of the picture within dE76 < 12 of the marker colour outside the art quad
  scan(png, settings, ...)       {"pass", "severity": none | soft | hard, "findings", "overlay"}

Severity (6.3): HARD = OCR text in a corner or a wide strip in the edge band, or a Gemini ui_button / watermark / logo /
extra_frame / mirror / person / pet (conf >= 0.6), or wide signage / text; SOFT = any other OCR text (book spines,
small labels), small Gemini text, marker leak > 0.25%. A hard finding stops the build (scene kept in Archive); a soft
one builds and flags the card. Nothing here ever spends credits or repairs an image.
"""
import json
import math
import os
import re
import subprocess
import tempfile
from pathlib import Path

import numpy as np

DEFAULTS = {"scene_scan": "ocr+gemini", "text_scan_bin": "~/.cache/ikigai-sam/bin/ikigai_text_scan"}
TILES = (6, 4)
OVERLAP = 0.2
UPSCALE = 3
OCR_MIN_CONF = 0.3
OCR_MIN_ALNUM = 3
OCR_MIN_H = 0.0035          # box height >= 0.35% of the picture height
EDGE = 0.10                 # edge band: outer 10% of width / height
CORNER = 0.15               # corner boxes 15% x 15%
HARD_EDGE_W = 0.04          # an OCR strip in the edge band at least 4% of the width (captions, watermarks, buttons)
GEM_CONF = 0.6
GEM_TEXT_W = 0.06
LEAK_DE = 12.0
LEAK_MAX = 0.0025
HARD_TYPES = ("ui_button", "watermark", "logo", "extra_frame", "mirror", "person", "pet")
GEM_TYPES = HARD_TYPES + ("text", "signage")
SWIFT = Path(__file__).with_name("text_scan.swift")


def _cfg(settings, key):
    return (settings or {}).get(key, DEFAULTS[key])


# ---------- OCR (macOS Vision via the Swift tool; tesseract fallback) ----------

def scan_bin(settings=None, compile_missing=True):
    """Path of the compiled Vision OCR tool, compiled once with `swiftc -O` when missing. None when unavailable."""
    p = Path(os.path.expanduser(_cfg(settings, "text_scan_bin")))
    if p.is_file():
        return p
    if not compile_missing or not SWIFT.is_file():
        return None
    try:
        r = subprocess.run(["swiftc", "-O", str(SWIFT), "-o", str(p)], capture_output=True, text=True, timeout=300)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return p if r.returncode == 0 and p.is_file() else None


def tiles(W, H, grid=TILES, overlap=OVERLAP):
    """Overlapping tile boxes [(x0, y0, x1, y1)] covering a W x H picture (grid cols x rows, overlap share)."""
    cols, rows = grid
    tw, th = W / (cols - (cols - 1) * overlap), H / (rows - (rows - 1) * overlap)
    out = []
    for j in range(rows):
        for i in range(cols):
            x0, y0 = i * tw * (1 - overlap), j * th * (1 - overlap)
            out.append((int(round(x0)), int(round(y0)), int(round(min(W, x0 + tw))), int(round(min(H, y0 + th)))))
    return out


def _iou(a, b):
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / u if u > 0 else 0.0


def _contains(a, b):
    """b's centre lies inside a."""
    cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
    return a[0] <= cx <= a[2] and a[1] <= cy <= a[3]


def merge(hits):
    """Duplicates across overlapping tiles -> one finding (highest confidence kept, box = union)."""
    out = []
    for h in sorted(hits, key=lambda h: -h["conf"]):
        for o in out:
            if _iou(o["box"], h["box"]) > 0.3 or _contains(o["box"], h["box"]) or _contains(h["box"], o["box"]):
                o["box"] = [min(o["box"][0], h["box"][0]), min(o["box"][1], h["box"][1]),
                            max(o["box"][2], h["box"][2]), max(o["box"][3], h["box"][3])]
                break
        else:
            out.append(dict(h))
    return out


def map_hits(raw, boxes, W, H):
    """Vision hits ({tile, conf, box 0..1 of the tile, text}) -> picture-space boxes in 0..1 of the picture."""
    out = []
    for r in raw:
        x0, y0, x1, y1 = boxes[int(r["tile"])]
        tw, th = x1 - x0, y1 - y0
        b = r["box"]
        out.append({"conf": float(r["conf"]), "text": str(r.get("text") or ""),
                    "box": [(x0 + b[0] * tw) / W, (y0 + b[1] * th) / H, (x0 + b[2] * tw) / W, (y0 + b[3] * th) / H]})
    return out


def keep_ocr(h):
    """An OCR hit worth reporting: confidence, >= 3 letters / digits, not a hair-thin box."""
    return (h["conf"] >= OCR_MIN_CONF and len(re.findall(r"[A-Za-z0-9]", h["text"])) >= OCR_MIN_ALNUM
            and (h["box"][3] - h["box"][1]) >= OCR_MIN_H)


def _tesseract(png):
    """Weaker fallback (textures read as glyphs): psm 11 TSV, conf >= 70, >= 4 alphanumerics."""
    from PIL import Image
    with Image.open(png) as im:
        W, H = im.size
    try:
        r = subprocess.run(["tesseract", str(png), "-", "--psm", "11", "tsv"], capture_output=True, text=True,
                           timeout=120)
    except (OSError, subprocess.TimeoutExpired):
        return []
    out = []
    for line in r.stdout.splitlines()[1:]:
        f = line.split("\t")
        if len(f) < 12:
            continue
        try:
            conf = float(f[10])
        except ValueError:
            continue
        txt = f[11].strip()
        if conf >= 70 and len(re.findall(r"[A-Za-z0-9]", txt)) >= 4:
            x, y, w, h = (int(v) for v in f[6:10])
            out.append({"conf": conf / 100, "text": txt, "box": [x / W, y / H, (x + w) / W, (y + h) / H],
                        "engine": "tesseract"})
    return out


def ocr_findings(png, settings=None, runner=None):
    """OCR text in the picture: [{conf, text, box (0..1 of the picture), engine}]. runner(tile_paths) -> raw Vision
    hits is injectable for tests."""
    from PIL import Image
    with Image.open(png) as im:
        im = im.convert("RGB")
        W, H = im.size
        boxes = tiles(W, H)
        with tempfile.TemporaryDirectory() as td:
            paths = []
            for k, b in enumerate(boxes):
                t = im.crop(b)
                t = t.resize((t.width * UPSCALE, t.height * UPSCALE), Image.LANCZOS)
                p = Path(td) / f"t{k:02d}.png"
                t.save(p)
                paths.append(str(p))
            if runner is None:
                exe = scan_bin(settings)
                if exe is None:
                    return [h for h in _tesseract(png) if keep_ocr(h)]
                try:
                    r = subprocess.run([str(exe)] + paths, capture_output=True, text=True, timeout=300)
                    raw = json.loads(r.stdout or "[]")
                except (OSError, subprocess.TimeoutExpired, ValueError):
                    return [h for h in _tesseract(png) if keep_ocr(h)]
            else:
                raw = runner(paths)
    hits = [dict(h, engine="vision") for h in map_hits(raw, boxes, W, H)]
    return [h for h in merge(hits) if keep_ocr(h)]


# ---------- Gemini (one flash-lite call) ----------

GEMINI_PROMPT = ("You check an interior photograph that will be sold as a wall-art mockup. List every one of these "
                 "you can see: readable or garbled text anywhere (book spines, labels, signs), interface buttons or "
                 "pills, watermarks, logos, signage, a framed picture or poster OTHER than the one main framed "
                 "artwork, mirrors, people or parts of people, pets. Return JSON {\"findings\": [{\"type\": \"text|"
                 "ui_button|watermark|logo|signage|extra_frame|mirror|person|pet\", \"box_2d\": [ymin, xmin, ymax, "
                 "xmax], \"confidence\": 0..1}]} on a 0-1000 grid; an empty list when there is none. The main artwork's "
                 "own blank coloured print area is not a finding.")


def _gemini_ask(png, prompt, timeout=60):
    import base64
    import urllib.request
    from .sam_frames import GEMINI_MODEL, _gemini_key
    key = _gemini_key()
    if not key:
        raise RuntimeError("GEMINI_API_KEY is not set")
    mime = "image/png" if str(png).lower().endswith(".png") else "image/jpeg"
    body = {"contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": mime, "data":
                         base64.b64encode(Path(png).read_bytes()).decode()}}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0}}
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:"
                                 "generateContent", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "x-goog-api-key": key})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        out = json.load(r)
    return out["candidates"][0]["content"]["parts"][0]["text"]


def gemini_findings(png, ask=None):
    """[{type, box (0..1 of the picture), confidence, engine}]; ask(png, prompt) -> raw JSON text (injectable)."""
    raw = (ask or _gemini_ask)(png, GEMINI_PROMPT)
    obj = json.loads(raw) if isinstance(raw, str) else raw
    items = obj.get("findings") if isinstance(obj, dict) else obj
    out = []
    for it in items or []:
        if not isinstance(it, dict) or it.get("type") not in GEM_TYPES:
            continue
        try:
            y0, x0, y1, x1 = [float(v) / 1000 for v in it.get("box_2d") or []]
        except (TypeError, ValueError):
            continue
        out.append({"type": it["type"], "box": [x0, y0, x1, y1], "conf": float(it.get("confidence") or 0),
                    "engine": "gemini"})
    return out


# ---------- the marker colour outside the art ----------

def marker_leak(rgb, art_quad, marker="orange", grow=0.015):
    """Share of the picture's pixels within dE76 < 12 of the marker colour OUTSIDE the art quad grown by 1.5% of the
    width (the built PSD's art quad, in the scene's pixel space)."""
    import cv2
    from .slot_planner import MARKER_RGB
    from .template_checker import offset_quad, poly_mask
    H, W = rgb.shape[:2]
    lab = cv2.cvtColor(np.float32(rgb[..., :3]) / 255.0, cv2.COLOR_RGB2Lab)
    ref = cv2.cvtColor(np.float32([[MARKER_RGB[marker]]]) / 255.0, cv2.COLOR_RGB2Lab)[0, 0]
    near = np.linalg.norm(lab - ref, axis=-1) < LEAK_DE
    inside = poly_mask(offset_quad(np.float32(art_quad), grow * W), W, H) > 0.5
    return float((near & ~inside).sum()) / float(W * H)


# ---------- severity ----------

def _where(b):
    """Plain position words for a box (0..1)."""
    cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
    v = "top" if cy < 0.33 else "bottom" if cy > 0.67 else "centre"
    h = "left" if cx < 0.33 else "right" if cx > 0.67 else ""
    return (f"{v}-{h}" if h and v != "centre" else (f"centre-{h}" if h else v))


def in_corner(b):
    cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
    return (cx < CORNER or cx > 1 - CORNER) and (cy < CORNER or cy > 1 - CORNER)


def in_edge(b):
    cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
    return cx < EDGE or cx > 1 - EDGE or cy < EDGE or cy > 1 - EDGE


def classify(ocr=(), gem=(), leak=None):
    """Findings + severity from OCR hits, Gemini findings and the marker leak share (6.3)."""
    out = []
    for h in ocr:
        b = h["box"]
        hard = in_corner(b) or (in_edge(b) and b[2] - b[0] >= HARD_EDGE_W)
        out.append({"kind": "text", "engine": h.get("engine", "vision"), "text": h.get("text", "")[:60],
                    "conf": round(h["conf"], 2), "box": [round(v, 4) for v in b],
                    "severity": "hard" if hard else "soft",
                    "why": (f"stray text at the {_where(b)} edge" if hard else f"garbled text, {_where(b)}")})
    for g in gem:
        if g["conf"] < GEM_CONF:
            continue
        b = g["box"]
        if g["type"] in HARD_TYPES:
            sev = "hard"
        elif g["type"] in ("signage", "text"):
            sev = "hard" if b[2] - b[0] >= GEM_TEXT_W else "soft"
        else:
            continue
        words = {"ui_button": "a button", "watermark": "a watermark", "logo": "a logo", "extra_frame": "a second frame",
                 "mirror": "a mirror", "person": "a person", "pet": "a pet", "signage": "a sign", "text": "text"}
        out.append({"kind": g["type"], "engine": "gemini", "conf": round(g["conf"], 2), "box": [round(v, 4) for v in b],
                    "severity": sev, "why": f"{words[g['type']]} at the {_where(b)}"})
    if leak is not None and leak > LEAK_MAX:
        out.append({"kind": "marker_leak", "engine": "pixels", "share": round(leak, 5), "severity": "soft",
                    "why": f"the insert colour shows outside the art ({leak:.2%} of the picture)"})
    sev = "hard" if any(f["severity"] == "hard" for f in out) else "soft" if out else "none"
    return out, sev


def draw_overlay(png, findings, out_png):
    from PIL import Image, ImageDraw
    with Image.open(png) as im:
        im = im.convert("RGB")
        W, H = im.size
        d = ImageDraw.Draw(im)
        for f in findings:
            if "box" not in f:
                continue
            b = f["box"]
            col = (230, 30, 30) if f["severity"] == "hard" else (240, 170, 0)
            d.rectangle([b[0] * W - 3, b[1] * H - 3, b[2] * W + 3, b[3] * H + 3], outline=col, width=max(2, W // 600))
        im.save(out_png)
    return out_png


def scan(png, settings=None, art_quad=None, marker="orange", ocr_runner=None, gemini_ask=None, overlay=None):
    """The whole scan of one scene. Mode from setting scene_scan (ocr+gemini | ocr | off). A Gemini failure is
    noted, never fatal (the OCR still runs). Returns {"pass", "severity", "findings", "overlay", "mode", "notes"}."""
    mode = _cfg(settings, "scene_scan")
    if mode == "off":
        return {"pass": True, "severity": "none", "findings": [], "overlay": None, "mode": mode, "notes": []}
    notes = []
    ocr = ocr_findings(png, settings, ocr_runner)
    if ocr and all(h.get("engine") == "tesseract" for h in ocr):
        notes.append("OCR fell back to tesseract (weaker)")
    gem = []
    if mode == "ocr+gemini":
        try:
            gem = gemini_findings(png, gemini_ask)
        except Exception as e:  # noqa: BLE001
            notes.append(f"gemini scan skipped: {str(e)[:80]}")
    leak = None
    if art_quad is not None:
        from PIL import Image
        with Image.open(png) as im:
            leak = marker_leak(np.asarray(im.convert("RGB")), art_quad, marker)
    findings, sev = classify(ocr, gem, leak)
    ov = None
    if findings and overlay:
        ov = str(draw_overlay(png, findings, overlay))
    return {"pass": sev == "none", "severity": sev, "findings": findings, "overlay": ov, "mode": mode, "notes": notes}


# ---------- reference board overlays (controls addendum A.1 step 4) ----------

REFERENCE_PROMPT = ("This is a screenshot of a room photograph saved from Pinterest, Etsy or a shop. Find every overlay "
                    "that is NOT part of the photographed room: Pinterest \"Visit site\" or lens (visual search) "
                    "buttons, \"Deal\" bubbles, video timers, carousel arrows or dots, shop names, tiled mock-up store "
                    "watermarks, \"insert your own design\" circles, captions or price labels. Also give the box of the "
                    "main framed artwork (frame included), or null when the photo has no framed art. Return JSON "
                    "{\"overlays\": [{\"type\": \"ui_button|deal|timer|carousel|shop_name|watermark|insert_circle|"
                    "caption\", \"box_2d\": [ymin, xmin, ymax, xmax], \"confidence\": 0..1}], \"frame_box\": "
                    "[ymin, xmin, ymax, xmax] or null} on a 0-1000 grid. Text printed on the artwork itself is not an "
                    "overlay. Real objects in the room (books, signs on a wall) are not overlays.")
REF_OVERLAY_TYPES = ("ui_button", "deal", "timer", "carousel", "shop_name", "watermark", "insert_circle", "caption")


def _box(v):
    y0, x0, y1, x1 = [float(x) / 1000 for x in v]
    return [x0, y0, x1, y1]


def _hit(a, b):
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])


def scan_reference(png, settings=None, ocr_runner=None, gemini_ask=None):
    """Overlays on a reference screenshot (OCR tiles + one Gemini flash-lite call with the reference prompt). Returns
    {"findings": [{type, box (0..1), conf, source}], "frame_box": [x0, y0, x1, y1] | None, "notes"}. Findings inside
    the frame box are dropped (the blanking step covers the art). OCR text counts only in a corner or inside a Gemini
    overlay box (room text such as book spines is not an overlay)."""
    notes = []
    gem, frame = [], None
    try:
        raw = (gemini_ask or _gemini_ask)(png, REFERENCE_PROMPT)
        obj = json.loads(raw) if isinstance(raw, str) else raw
        for it in (obj or {}).get("overlays") or []:
            if isinstance(it, dict) and it.get("type") in REF_OVERLAY_TYPES:
                try:
                    gem.append({"type": it["type"], "box": _box(it["box_2d"]), "conf": float(it.get("confidence") or 0),
                                "source": "gemini"})
                except (TypeError, ValueError, KeyError):
                    continue
        if (obj or {}).get("frame_box"):
            try:
                frame = _box(obj["frame_box"])
            except (TypeError, ValueError):
                frame = None
    except Exception as e:  # noqa: BLE001
        notes.append(f"gemini scan skipped: {str(e)[:80]}")
    try:
        ocr = ocr_findings(png, settings, ocr_runner)
    except Exception as e:  # noqa: BLE001
        ocr = []
        notes.append(f"OCR skipped: {str(e)[:80]}")
    found = [g for g in gem if g["conf"] >= 0.4]
    for h in ocr:
        if in_corner(h["box"]) or any(_hit(h["box"], g["box"]) for g in found):
            found.append({"type": "text", "box": [float(v) for v in h["box"]], "conf": float(h.get("conf") or 0),
                          "source": "ocr", "text": str(h.get("text", ""))[:40]})
    if frame is not None:
        found = [f for f in found if not (f["box"][0] >= frame[0] and f["box"][1] >= frame[1]
                                          and f["box"][2] <= frame[2] and f["box"][3] <= frame[3])]
    return {"findings": found, "frame_box": frame, "notes": notes}


def summary(res):
    """One plain line for a card / an error (the first two reasons)."""
    fs = [f for f in res.get("findings") or [] if f["severity"] == res.get("severity")] or res.get("findings") or []
    return "; ".join(dict.fromkeys(f["why"] for f in fs[:3]))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Stray-text / overlay scan of a scene image (free)")
    ap.add_argument("images", nargs="+")
    ap.add_argument("--ocr-only", action="store_true")
    a = ap.parse_args()
    for p in a.images:
        r = scan(p, {"scene_scan": "ocr" if a.ocr_only else "ocr+gemini"})
        print(json.dumps({"image": Path(p).name, "severity": r["severity"], "findings": r["findings"],
                          "notes": r["notes"]}, ensure_ascii=False))
