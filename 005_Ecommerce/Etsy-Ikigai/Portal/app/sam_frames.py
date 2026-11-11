"""Frame-insert detection prototype with SAM 2 (Tony 2026-11-10, build plan section 6). PROTOTYPE ONLY: not wired into
the Production / template flow yet.

Pipeline: Gemini vision gives a ROUGH box around the blank frame insert -> SAM 2 (Segment Anything 2.1, Apache 2.0,
runs on this Mac, CPU or Apple MPS) segments the insert inside that box -> four corners are fitted to the mask
(convex hull -> 4 longest sides -> robust line fit per side -> intersections) -> optional verification with the
template checker's black/white card test, and a compare mode that scores corner error against a known quad.
Target: corner error <= 2 px (the current find_insert method is 4-12 px).

SAM 2 lives OUTSIDE the workspace in its own venv: ~/.cache/ikigai-sam (torch, sam2, opencv-python-headless);
checkpoint ~/.cache/ikigai-sam/checkpoints/sam2.1_hiera_small.pt (Meta's official download). This file imports
nothing from the Portal, so it runs with that venv's python:

  PY=~/.cache/ikigai-sam/bin/python
  $PY app/sam_frames.py detect <image> [--box x0,y0,x1,y1] [--out overlay.png]      # four corners as JSON
  $PY app/sam_frames.py compare <image> --known x,y,x,y,x,y,x,y [--box ...]           # corner error in px
Without --box the rough box comes from Gemini (GEMINI_API_KEY from env or ~/.env-secrets; the key is never printed).
Do NOT run it on BDRM_Wabi_Vertical (already verified by hand); Tony will supply a template that was done wrong.
"""
import argparse
import base64
import json
import math
import os
import re
import sys
import urllib.request
from pathlib import Path

import numpy as np

HOME = Path(os.environ.get("IKIGAI_SAM_HOME", Path.home() / ".cache" / "ikigai-sam"))
CHECKPOINT = HOME / "checkpoints" / "sam2.1_hiera_small.pt"
CONFIG = "configs/sam2.1/sam2.1_hiera_s.yaml"
GEMINI_MODEL = "gemini-3.5-flash-lite"


# ---------- rough box (Gemini) ----------

def _gemini_key():
    v = os.environ.get("GEMINI_API_KEY", "")
    f = Path("~/.env-secrets").expanduser()
    if not v and f.is_file():
        for line in f.read_text().splitlines():
            m = re.match(r"\s*(?:export\s+)?GEMINI_API_KEY=(.*)", line)
            if m:
                v = m.group(1).strip().strip("'\"")
    return v


def gemini_box(image_path, model=GEMINI_MODEL, timeout=60):
    """Rough [x0, y0, x1, y1] pixel box around the blank paper inside the picture frame (Gemini's 0-1000 grid)."""
    from PIL import Image
    key = _gemini_key()
    if not key:
        raise RuntimeError("GEMINI_API_KEY is not set")
    with Image.open(image_path) as im:
        W, H = im.size
    prompt = ("This room photo has one picture frame on the wall with a blank (white or placeholder) insert. Return the "
              "bounding box of the INSERT inside the frame (not the frame moulding) as JSON "
              '{"box_2d": [ymin, xmin, ymax, xmax]} on a 0-1000 grid.')
    mime = "image/png" if str(image_path).lower().endswith(".png") else "image/jpeg"
    body = {"contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": mime, "data":
                         base64.b64encode(Path(image_path).read_bytes()).decode()}}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0}}
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                                 data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "x-goog-api-key": key})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        out = json.load(r)
    obj = json.loads(out["candidates"][0]["content"]["parts"][0]["text"])
    b = obj["box_2d"] if isinstance(obj, dict) else obj[0]["box_2d"]
    y0, x0, y1, x1 = [float(v) for v in b]
    return [x0 / 1000 * W, y0 / 1000 * H, x1 / 1000 * W, y1 / 1000 * H]


# ---------- SAM 2 ----------

_PRED = None


def predictor(device=None):
    global _PRED
    if _PRED is None:
        import torch
        from sam2.build_sam import build_sam2
        from sam2.sam2_image_predictor import SAM2ImagePredictor
        dev = device or ("mps" if torch.backends.mps.is_available() else "cpu")
        try:
            model = build_sam2(CONFIG, str(CHECKPOINT), device=dev)
        except Exception:  # noqa: BLE001  (some ops are missing on MPS: CPU is fine for one image)
            dev = "cpu"
            model = build_sam2(CONFIG, str(CHECKPOINT), device=dev)
        _PRED = SAM2ImagePredictor(model)
        _PRED.device_name = dev
    return _PRED


def segment(rgb, box):
    """Best SAM 2 mask for the insert inside `box` (a positive click at the box centre helps it pick the paper,
    not the whole frame). Returns (bool mask, score)."""
    import torch
    p = predictor()
    with torch.inference_mode():
        p.set_image(rgb)
        x0, y0, x1, y1 = box
        masks, scores, _ = p.predict(box=np.array([x0, y0, x1, y1], "float32"),
                                     point_coords=np.array([[(x0 + x1) / 2, (y0 + y1) / 2]], "float32"),
                                     point_labels=np.array([1]), multimask_output=True)
    # prefer the mask that fills the box best without leaking outside it (the insert, not frame + insert)
    bw, bh = max(x1 - x0, 1), max(y1 - y0, 1)
    best, best_s = None, -1e9
    for m, s in zip(masks, scores):
        m = m.astype(bool)
        ys, xs = np.nonzero(m)
        if len(xs) < 100:
            continue
        inside = ((xs >= x0 - 0.05 * bw) & (xs <= x1 + 0.05 * bw) & (ys >= y0 - 0.05 * bh) & (ys <= y1 + 0.05 * bh)).mean()
        fill = m.sum() / (bw * bh)
        sc = float(s) + inside - abs(1 - min(fill, 1.5))
        if sc > best_s:
            best, best_s = m, sc
    if best is None:
        raise RuntimeError("SAM 2 found no mask in the box")
    return best, best_s


# ---------- four corners from a mask ----------

def order_quad(pts):
    pts = np.asarray(pts, "float32")
    s, d = pts.sum(1), pts[:, 0] - pts[:, 1]
    return np.array([pts[s.argmin()], pts[d.argmax()], pts[s.argmax()], pts[d.argmin()]], "float32")


def _robust_line(pts):
    """Huber line fit, then refit on the points within 2 px of it (a missing corner chunk is outvoted)."""
    import cv2
    pts = np.float32(pts)
    for _ in range(3):
        vx, vy, x0, y0 = cv2.fitLine(pts, cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
        d = np.abs((pts[:, 0] - x0) * vy - (pts[:, 1] - y0) * vx)
        keep = d < max(2.0, float(np.percentile(d, 60)))
        if keep.sum() < 8 or keep.all():
            break
        pts = pts[keep]
    return np.float32([x0, y0]), np.float32([x0 + vx, y0 + vy])


def quad_from_mask(mask, box=None):
    """Four corners (tl, tr, br, bl), sub-pixel. Each side is a robust line through the mask's OUTERMOST pixels on
    that side (leftmost per row for the left side, topmost per column for the top ...), over the middle 80% of the
    side, so a chunk the mask missed or a prop over a corner does not bend the side; neighbouring lines are
    intersected and moved out by half a pixel (mask cells -> paper edge)."""
    import cv2
    m = cv2.morphologyEx(mask.astype("uint8"), cv2.MORPH_OPEN, np.ones((3, 3), "uint8")).astype(bool)
    ys, xs = np.nonzero(m)
    if len(xs) < 100:
        raise RuntimeError("empty mask")
    x0, y0, x1, y1 = box if box is not None else (xs.min(), ys.min(), xs.max(), ys.max())
    rows = np.arange(int(y0 + 0.1 * (y1 - y0)), int(y1 - 0.1 * (y1 - y0)))
    cols = np.arange(int(x0 + 0.1 * (x1 - x0)), int(x1 - 0.1 * (x1 - x0)))
    left, right, top, bottom = [], [], [], []
    for y in rows:
        r = np.nonzero(m[y])[0] if 0 <= y < m.shape[0] else []
        if len(r):
            left.append((r.min() - 0.5, y))
            right.append((r.max() + 0.5, y))
    for x in cols:
        c = np.nonzero(m[:, x])[0] if 0 <= x < m.shape[1] else []
        if len(c):
            top.append((x, c.min() - 0.5))
            bottom.append((x, c.max() + 0.5))
    if min(len(left), len(top)) < 8:
        raise RuntimeError("the mask is too small for a quad")
    L = [_robust_line(top), _robust_line(right), _robust_line(bottom), _robust_line(left)]
    out = []
    for i in range(4):                                  # corner i = side (i-1) x side i: tl = left x top ...
        (p, p2), (s_, s2) = L[(i - 1) % 4], L[i]
        r, u = p2 - p, s2 - s_
        cr = r[0] * u[1] - r[1] * u[0]
        if abs(cr) < 1e-9:
            raise RuntimeError("parallel sides")
        out.append(p + r * (((s_ - p)[0] * u[1] - (s_ - p)[1] * u[0]) / cr))
    return order_quad(np.float32(out))


def detect(image_path, box=None):
    from PIL import Image
    with Image.open(image_path) as im:
        rgb = np.asarray(im.convert("RGB"))
    src = "given"
    if box is None:
        box, src = gemini_box(image_path), "gemini"
    mask, score = segment(rgb, box)
    q = quad_from_mask(mask, box)
    return {"image": str(image_path), "box": [round(float(v), 1) for v in box], "box_source": src,
            "corners": np.round(q, 2).tolist(), "mask_px": int(mask.sum()), "score": round(float(score), 3),
            "device": getattr(predictor(), "device_name", "?")}, mask


def corner_error(q, known):
    q, k = np.float32(q), order_quad(np.float32(known).reshape(4, 2))
    d = [math.dist(a, b) for a, b in zip(order_quad(q), k)]
    return {"per_corner_px": [round(x, 2) for x in d], "max_px": round(max(d), 2), "mean_px": round(sum(d) / 4, 2),
            "pass_2px": max(d) <= 2.0}


def overlay(image_path, mask, q, out):
    import cv2
    from PIL import Image
    a = np.asarray(Image.open(image_path).convert("RGB")).copy()
    a[mask] = (a[mask] * 0.6 + np.array([255, 60, 40]) * 0.4).astype("uint8")
    cv2.polylines(a, [np.int32(np.round(np.float32(q)))], True, (0, 255, 255), 2)
    Image.fromarray(a).save(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="SAM 2 frame-insert corners (prototype)")
    ap.add_argument("mode", choices=["detect", "compare"])
    ap.add_argument("image")
    ap.add_argument("--box", help="x0,y0,x1,y1 rough box (skips Gemini)")
    ap.add_argument("--known", help="x,y x 4 known corners (compare mode)")
    ap.add_argument("--out", help="write an overlay PNG here")
    a = ap.parse_args(argv)
    if "BDRM_Wabi_Vertical" in a.image:
        sys.exit("Not on the Wabi bedroom (already verified by hand); use the template Tony supplies.")
    box = [float(v) for v in a.box.split(",")] if a.box else None
    res, mask = detect(a.image, box)
    if a.mode == "compare":
        if not a.known:
            sys.exit("--known x,y,x,y,x,y,x,y is required for compare")
        res["error"] = corner_error(res["corners"], [float(v) for v in a.known.split(",")])
    if a.out:
        overlay(a.image, mask, res["corners"], a.out)
        res["overlay"] = a.out
    print(json.dumps(res, indent=1))
    return res


if __name__ == "__main__":
    main()
