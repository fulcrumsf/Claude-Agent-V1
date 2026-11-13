"""SAM 2 precision masks and frame-insert corners (Tony's standard, 2026-11-10: "pixel-perfect, anti-aliased, no
jagged/stair-stepped edges, no misses from shadows or soft gradients, full resolution"; memory
feedback_pixel_perfect_masks_sam_2026-11-10). Every NEW template build gets its `Place Artwork Here` corners and every
mask it needs from here; brightness-threshold / flood-fill / Canny masks are not used for new builds.

Pipeline for the blank insert:
  1. rough box: Gemini vision (or --box)                                    gemini_box()
  2. SAM 2.1 (largest checkpoint installed: hiera_large, then b+, small) segments the insert inside the box, logits
     at FULL resolution                                                    segment_insert()
  3. edge refinement: colour-guided filter (He et al.) of the SAM mask with the photo as guide, full resolution,
     only inside a thin band around the SAM boundary -> smooth anti-aliased alpha that follows the real edge
     (catches soft shadows/gradients SAM's 256-px logits round off)       refine_alpha()
  4. sub-pixel four-corner fit: start from the SAM mask's quad, then for every side sample ~200 profiles of the
     refined alpha along the side's normal (bilinear, 1/8 px steps), take each profile's 0.5 crossing after
     normalising its inner/outer plateaus, robust (Huber + inlier) line fit, intersect neighbours; three passes so
     the normals follow perspective                                         fit_quad()
  5. verification, LOUD failure (QuadError) when the corners disagree with the mask: per-side inlier share and RMS
     residual, polygon vs mask IoU and the SAM-quad vs refined-quad corner distance        verify_quad()
  6. the OPENING (Tony 2026-11-12): from that paper edge outward to the frame's HARD inner edge, the shadowed paper
     counted as opening (a frame-lip shadow / 3/4-view inner wall left a grey strip beside the art); sub-pixel, one
     line per side, loud failure                                             opening_quad()
     detect() returns "corners" = the opening, "corners_paper" = SAM's paper edge, "opening" = per-side offsets.
     The template builder then renders a black and a white card through the finished PSD and checks the visible
     art quad against these corners (scene_templates.card_verify).
Other masks (wall around the frame) use the same SAM + refine path: segment_wall().

Pure geometry (guided filter, quad fit, coverage, edge_truth) needs only numpy + cv2, so the Portal imports it; SAM
itself (torch) lives OUTSIDE the workspace in ~/.cache/ikigai-sam and runs as a subprocess:

  PY=~/.cache/ikigai-sam/bin/python
  $PY app/sam_frames.py detect <image> [--box x0,y0,x1,y1] [--json out.json] [--alpha a.png] [--wall w.png] [--out ov.png]
  $PY app/sam_frames.py compare <image> --known x,y,x,y,x,y,x,y [--box ...]
Without --box the rough box comes from Gemini (GEMINI_API_KEY from env or ~/.env-secrets / ~/.mcp-secrets.env; the
key is never printed). Alpha PNGs are 16-bit greyscale at the image's full size.
Do NOT run it on BDRM_Wabi_Vertical (verified by hand).
"""
import argparse
import base64
import json
import math
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np

HOME = Path(os.environ.get("IKIGAI_SAM_HOME", Path.home() / ".cache" / "ikigai-sam"))
# largest first; the first checkpoint present is used (override: IKIGAI_SAM_MODEL=large|base_plus|small)
MODELS = [("large", "sam2.1_hiera_large.pt", "configs/sam2.1/sam2.1_hiera_l.yaml"),
          ("base_plus", "sam2.1_hiera_base_plus.pt", "configs/sam2.1/sam2.1_hiera_b+.yaml"),
          ("small", "sam2.1_hiera_small.pt", "configs/sam2.1/sam2.1_hiera_s.yaml")]
GEMINI_MODEL = "gemini-3.5-flash-lite"
NOT_ON = ("BDRM_Wabi_Vertical",)


class QuadError(RuntimeError):
    """The corners could not be trusted (shown to Tony; the template is not built)."""


# ---------- rough box (Gemini) ----------

def _gemini_key():
    v = os.environ.get("GEMINI_API_KEY", "")
    for f in ("~/.env-secrets", "~/.mcp-secrets.env"):
        f = Path(f).expanduser()
        if v or not f.is_file():
            continue
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


# ---------- SAM 2 (torch; only in the ikigai-sam venv) ----------

_PRED = None


def model_choice():
    want = os.environ.get("IKIGAI_SAM_MODEL")
    for name, ckpt, cfg in MODELS:
        if (want is None or want == name) and (HOME / "checkpoints" / ckpt).is_file():
            return name, HOME / "checkpoints" / ckpt, cfg
    raise RuntimeError(f"no SAM 2.1 checkpoint in {HOME / 'checkpoints'}")


def predictor(device=None):
    global _PRED
    if _PRED is None:
        import torch
        from sam2.build_sam import build_sam2
        from sam2.sam2_image_predictor import SAM2ImagePredictor
        name, ckpt, cfg = model_choice()
        dev = device or ("mps" if torch.backends.mps.is_available() else "cpu")
        try:
            model = build_sam2(cfg, str(ckpt), device=dev)
        except Exception:  # noqa: BLE001  (an op missing on MPS: CPU is fine for one image)
            dev = "cpu"
            model = build_sam2(cfg, str(ckpt), device=dev)
        _PRED = SAM2ImagePredictor(model)
        _PRED.device_name, _PRED.model_name = dev, name
    return _PRED


_IMG_KEY = None


def set_image(rgb):
    global _IMG_KEY
    import torch
    p = predictor()
    key = (rgb.shape, int(rgb[::97, ::89].sum()))
    if key != _IMG_KEY:
        with torch.inference_mode():
            p.set_image(rgb)
        _IMG_KEY = key
    return p


def sam_predict(rgb, box=None, points=None, labels=None, multimask=True):
    """SAM 2 logits at FULL resolution: (logits[k, H, W] float32, scores[k])."""
    import torch
    p = set_image(rgb)
    kw = {}
    if box is not None:
        kw["box"] = np.array(box, "float32")
    if points is not None:
        kw["point_coords"] = np.array(points, "float32")
        kw["point_labels"] = np.array(labels, "int32")
    with torch.inference_mode():
        logits, scores, _ = p.predict(multimask_output=multimask, return_logits=True, **kw)
    return np.asarray(logits, "float32"), np.asarray(scores, "float32")


def _band_contrast(lab, m):
    """Colour difference (Lab dE) between the band just inside a mask's edge and its core. Paper insert: small (the
    edge is still paper); frame + insert: large (the edge band is frame moulding)."""
    import cv2
    u = m.astype("uint8")
    er = lambda k: cv2.erode(u, np.ones((k, k), "uint8")) > 0
    band, core = er(3) & ~er(9), er(41)
    if band.sum() < 50 or core.sum() < 50:
        return None
    return float(np.linalg.norm(np.median(lab[band], 0) - np.median(lab[core], 0)))


def insert_candidates(rgb, box):
    """Every SAM 2 mask from three prompts (box + centre click, centre click, box) x 3 multimask outputs that is a
    clean filled four-sided shape around the centre. Returns [{mask, logits, score, prompt, area, dE}]."""
    import cv2
    x0, y0, x1, y1 = box
    c = [(x0 + x1) / 2, (y0 + y1) / 2]
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype("float32")
    out = []
    for name, kw in (("box+click", {"box": box, "points": [c], "labels": [1]}),
                     ("click", {"points": [c], "labels": [1]}), ("box", {"box": box})):
        logits, scores = sam_predict(rgb, **kw)
        for lg, s in zip(logits, scores):
            m = lg > 0
            area = int(m.sum())
            if area < 400 or not m[int(c[1]), int(c[0])]:
                continue
            cs, _ = cv2.findContours(m.astype("uint8"), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            big = max(cs, key=cv2.contourArea)
            hull = cv2.contourArea(cv2.convexHull(big))
            if hull <= 0 or area / hull < 0.97 or cv2.contourArea(big) < 0.98 * area:
                continue                                          # a ring, a blob with holes or several pieces
            try:
                qa = cv2.contourArea(quad_from_mask(m).reshape(-1, 1, 2))
            except QuadError:
                continue
            if not 0.97 <= area / max(qa, 1) <= 1.02:
                continue                                          # not four straight sides
            dE = _band_contrast(lab, m)
            if dE is None:
                continue
            out.append({"mask": m, "logits": lg, "score": float(s), "prompt": name, "area": area, "dE": round(dE, 1)})
    return out


def segment_insert(rgb, box):
    """The blank-insert candidates in the order to try: of the clean four-sided SAM 2 masks, those whose edge band looks
    like their core (paper up to its edge, not frame moulding: dE <= max(12, 1.5 x the best)) and at least 20% of the
    largest, SMALLEST first (the innermost opening: a mat window inside a mat is the art opening; when its edge cannot
    be fitted the next larger one is tried). Returns [(bool mask, logits, info)]."""
    cands = insert_candidates(rgb, box)
    if not cands:
        raise QuadError("SAM 2 found no clean four-sided insert in the box")
    lim = max(12.0, 1.5 * min(c["dE"] for c in cands))
    ok = [c for c in cands if c["dE"] <= lim]
    big = max(c["area"] for c in ok)
    ok = sorted((c for c in ok if c["area"] >= 0.2 * big), key=lambda c: (c["area"], -c["score"]))
    seen, out = [], []
    for c in ok:                                  # near-identical masks from different prompts: try once
        if any(abs(c["area"] - a) < 0.01 * a for a in seen):
            continue
        seen.append(c["area"])
        info = {k: c[k] for k in ("prompt", "score", "area", "dE")}
        info["candidates"] = [{k: x[k] for k in ("prompt", "score", "area", "dE")} for x in cands]
        out.append((c["mask"], c["logits"], info))
    return out


def segment_wall(rgb, insert_q):
    """SAM 2 mask of the wall around the frame: positive clicks on the wall just outside the frame (above, left,
    right), negative click on the insert. Returns (bool mask) or None when no plausible wall mask comes back."""
    H, W = rgb.shape[:2]
    q = np.float32(insert_q)
    c = q.mean(0)
    w, h = q[:, 0].max() - q[:, 0].min(), q[:, 1].max() - q[:, 1].min()
    pts = []
    for dx, dy in ((0, -0.5), (-0.62, -0.42), (0.62, -0.42), (-0.68, 0), (0.68, 0)):
        x, y = c[0] + dx * w * 1.0, c[1] + dy * h * 1.0
        if 4 <= x < W - 4 and 4 <= y < H - 4:
            pts.append([x, y])
    if len(pts) < 2:
        return None
    logits, scores = sam_predict(rgb, points=pts + [list(map(float, c))], labels=[1] * len(pts) + [0])
    ins = poly_coverage(q, W, H) > 0.5
    best = None
    for lg, s in zip(logits, scores):
        m = lg > 0
        if (m & ins).sum() > 0.02 * ins.sum() or m.sum() < 4 * ins.sum():
            continue
        if best is None or s > best[1]:
            best = (m, float(s))
    return None if best is None else best[0]


# ---------- edge refinement (numpy + cv2) ----------

def _box(a, r):
    import cv2
    return cv2.boxFilter(a, -1, (2 * r + 1, 2 * r + 1), normalize=True, borderType=cv2.BORDER_REFLECT)


def guided_filter(I, p, r, eps):
    """He, Sun, Tang colour guided filter. I: HxWx3 float32 0..1 (guide), p: HxW float32. Returns HxW float32."""
    I = I.astype("float32")
    p = p.astype("float32")
    mI = [_box(I[..., k], r) for k in range(3)]
    mp = _box(p, r)
    cov_Ip = [_box(I[..., k] * p, r) - mI[k] * mp for k in range(3)]
    var = {}
    for i in range(3):
        for j in range(i, 3):
            var[i, j] = _box(I[..., i] * I[..., j], r) - mI[i] * mI[j] + (eps if i == j else 0)
    S = np.empty(p.shape + (3, 3), "float32")
    for (i, j), v in var.items():
        S[..., i, j] = v
        S[..., j, i] = v
    C = np.stack(cov_Ip, -1)[..., None]
    a = np.linalg.solve(S, C)[..., 0]                       # HxWx3
    b = mp - (a * np.stack(mI, -1)).sum(-1)
    ma = np.stack([_box(a[..., k], r) for k in range(3)], -1)
    mb = _box(b, r)
    return (ma * I).sum(-1) + mb


def lab_image(rgb):
    """CIE Lab as float32 (L 0..100, a/b about -128..127)."""
    import cv2
    return cv2.cvtColor(rgb.astype("float32") / 255.0, cv2.COLOR_RGB2LAB)


def material_axis(lab, mask, ring=(2, 8), core=(6, 18)):
    """How the insert differs from what surrounds it, made SHADOW-INVARIANT: the Lab difference between a ring just
    outside the mask (frame moulding) and a band just inside it (paper). A frame-lip shadow darkens the paper but keeps
    its colour, so when the colours differ (dE_ab >= 6) lightness counts only 25%; a white frame on white paper has no
    colour difference and lightness carries the edge. Returns (weights[3], inner Lab, outer Lab, dE_ab)."""
    import cv2
    u = mask.astype("uint8")
    k = lambda n: np.ones((2 * n + 1, 2 * n + 1), "uint8")
    outer = (cv2.dilate(u, k(ring[1])) > 0) & ~(cv2.dilate(u, k(ring[0])) > 0)
    inner = (cv2.erode(u, k(core[0])) > 0) & ~(cv2.erode(u, k(core[1])) > 0)
    if outer.sum() < 50 or inner.sum() < 50:
        return np.float32([1, 1, 1]), None, None, 0.0
    mi, mo = np.median(lab[inner], 0), np.median(lab[outer], 0)
    d_ab = float(np.hypot(*(mo[1:] - mi[1:])))
    w = np.float32([0.25, 1, 1]) if d_ab >= 6 else np.float32([1, 0.5, 0.5])
    return w, mi, mo, d_ab


def _masked_mean(img, w, k):
    """Local mean of img over the pixels where w is set (box window k x k)."""
    import cv2
    num = cv2.boxFilter(img * w[..., None], -1, (k, k), normalize=False)
    den = cv2.boxFilter(w, -1, (k, k), normalize=False)
    return num / np.maximum(den, 1e-6)[..., None], den


def _darker_than_both(L, Li, Lo, start=4.0, full=8.0):
    """A pixel clearly darker than both the paper and the frame (a mat-window line, the shadow in the frame lip) is
    not frame material: it belongs to the opening (art slightly under the lip beats a dark sliver)."""
    return np.clip((np.minimum(Li, Lo) - L - start) / (full - start), 0, 1)


def refine_alpha(rgb, mask, band=None, material=True):
    """SAM mask -> smooth anti-aliased alpha at FULL resolution on the photo's real MATERIAL edge (paper vs frame),
    not on a shadow edge. Inside a thin band around the SAM boundary every pixel is solved with the compositing
    equation against LOCAL colours: inside colour = mean of the mask's pixels 1-2 band widths in, outside colour = the
    same outside, in Lab weighted by material_axis (lightness only 25% when the colours differ, so a frame-lip shadow
    stays paper); alpha = the pixel's projection between the two, clipped 0..1; when paper and frame have the same
    colour (lightness mode) a pixel clearly darker than both (a mat-window line) counts as opening; then a radius-1
    guided filter
    (He et al.) with the photo as guide removes noise. Where the two local colours do not differ the SAM edge is kept
    (guided-filter smoothed). Outside the band the alpha is the SAM mask. Returns float32 HxW in 0..1."""
    import cv2
    H, W = mask.shape
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return mask.astype("float32")
    diag = math.hypot(xs.max() - xs.min(), ys.max() - ys.min())
    band = band or int(np.clip(round(0.008 * diag), 5, 14))
    pad = 3 * band + 8
    x0, y0 = max(0, xs.min() - pad), max(0, ys.min() - pad)
    x1, y1 = min(W, xs.max() + pad + 1), min(H, ys.max() + pad + 1)
    m = mask[y0:y1, x0:x1].astype("uint8")
    lab = lab_image(rgb[y0:y1, x0:x1])
    w, *_ = material_axis(lab, m.astype(bool)) if material else (np.float32([1, 1, 1]),)
    F = (lab * w).astype("float32")
    din = cv2.distanceTransform(m, cv2.DIST_L2, 5)
    dout = cv2.distanceTransform(1 - m, cv2.DIST_L2, 5)
    win = 4 * band + 1
    Fi, ni = _masked_mean(F, ((din > band) & (din <= 2 * band)).astype("float32"), win)
    Fo, no = _masked_mean(F, ((dout > band) & (dout <= 2 * band)).astype("float32"), win)
    Fb = cv2.GaussianBlur(F, (0, 0), 0.6)
    d = Fi - Fo
    dd = (d * d).sum(-1)
    a = ((Fb - Fo) * d).sum(-1) / np.maximum(dd, 1e-6)          # 0 = frame colour, 1 = paper colour
    if w[0] >= 1:                    # lightness mode (paper and frame of the same colour): a dark line is opening
        a = np.maximum(a, _darker_than_both(Fb[..., 0], Fi[..., 0], Fo[..., 0]))
    I = rgb[y0:y1, x0:x1].astype("float32") / 255.0
    smooth_sam = np.clip(guided_filter(I, m.astype("float32"), 2, 1e-3), 0, 1)
    ok = (dd > 4.0 ** 2) & (ni > 4) & (no > 4)          # local colours differ by >= 4 (weighted Lab units)
    a = np.where(ok, np.clip(a, 0, 1), smooth_sam)
    a = np.clip(guided_filter(I, a.astype("float32"), 1, 1e-4), 0, 1)
    near = (din <= band) & (m > 0) | (dout <= band) & (m == 0)
    out = mask.astype("float32").copy()
    sub = out[y0:y1, x0:x1]
    sub[near] = a[near]
    return out


def poly_coverage(q, W, H, ss=8):
    """Anti-aliased coverage (0..1) of a quad at full resolution: 8x8 supersampling inside the quad's bounding box
    (exact to 1/64 px area), zero elsewhere."""
    import cv2
    q = np.float32(q)
    out = np.zeros((H, W), "float32")
    x0, y0 = max(0, int(math.floor(q[:, 0].min())) - 1), max(0, int(math.floor(q[:, 1].min())) - 1)
    x1, y1 = min(W, int(math.ceil(q[:, 0].max())) + 2), min(H, int(math.ceil(q[:, 1].max())) + 2)
    if x1 <= x0 or y1 <= y0:
        return out
    big = np.zeros(((y1 - y0) * ss, (x1 - x0) * ss), "uint8")
    # pixel (i, j) covers [j, j+1) x [i, i+1); sample centres at (j + (k + 0.5)/ss)
    pts = (q - np.float32([x0, y0])) * ss - 0.5
    cv2.fillPoly(big, [np.int32(np.round(pts * 16))], 255, lineType=cv2.LINE_8, shift=4)
    out[y0:y1, x0:x1] = cv2.resize(big.astype("float32") / 255, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
    return out


# ---------- four corners ----------

def order_quad(pts):
    pts = np.asarray(pts, "float32")
    s, d = pts.sum(1), pts[:, 0] - pts[:, 1]
    return np.array([pts[s.argmin()], pts[d.argmax()], pts[s.argmax()], pts[d.argmin()]], "float32")


def _intersect(l1, l2):
    (p, p2), (s_, s2) = l1, l2
    r, u = p2 - p, s2 - s_
    cr = r[0] * u[1] - r[1] * u[0]
    if abs(cr) < 1e-9:
        raise QuadError("parallel sides")
    return p + r * (((s_ - p)[0] * u[1] - (s_ - p)[1] * u[0]) / cr)


def _corners(lines):
    """lines in side order top, right, bottom, left -> corners tl, tr, br, bl."""
    return np.float32([_intersect(lines[(i - 1) % 4], lines[i]) for i in range(4)])


def _robust_line(pts, tol=1.0):
    """Huber line fit, then refits on the points within `tol` px (a missing chunk / prop is outvoted).
    Returns (p0, p1, inlier mask, rms of inliers)."""
    import cv2
    pts = np.float32(pts)
    keep = np.ones(len(pts), bool)
    for _ in range(4):
        vx, vy, x0, y0 = cv2.fitLine(pts[keep], cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
        d = np.abs((pts[:, 0] - x0) * vy - (pts[:, 1] - y0) * vx)
        new = d < max(tol, float(np.percentile(d, 50)) * 2.5 if keep.sum() > 8 else tol)
        new = d < tol if new.sum() >= 0.5 * len(d) else new
        if new.sum() < 8 or (new == keep).all():
            keep = new if new.sum() >= 8 else keep
            break
        keep = new
    vx, vy, x0, y0 = cv2.fitLine(pts[keep], cv2.DIST_L2, 0, 0.01, 0.01).ravel()
    d = np.abs((pts[:, 0] - x0) * vy - (pts[:, 1] - y0) * vx)
    rms = float(np.sqrt(np.mean(d[keep] ** 2))) if keep.any() else 99.0
    return np.float32([x0, y0]), np.float32([x0 + vx, y0 + vy]), keep, rms


def quad_from_mask(mask, box=None):
    """Coarse four corners from a binary mask: robust lines through the outermost mask pixels on each side (middle
    80% of the side), intersected. Integer-cell accuracy; fit_quad() refines it."""
    import cv2
    m = cv2.morphologyEx(mask.astype("uint8"), cv2.MORPH_OPEN, np.ones((3, 3), "uint8")).astype(bool)
    ys, xs = np.nonzero(m)
    if len(xs) < 100:
        raise QuadError("empty mask")
    x0, y0, x1, y1 = box if box is not None else (xs.min(), ys.min(), xs.max(), ys.max())
    rows = np.arange(int(y0 + 0.1 * (y1 - y0)), int(y1 - 0.1 * (y1 - y0)))
    cols = np.arange(int(x0 + 0.1 * (x1 - x0)), int(x1 - 0.1 * (x1 - x0)))
    left, right, top, bottom = [], [], [], []
    for y in rows:
        r = np.nonzero(m[y])[0] if 0 <= y < m.shape[0] else []
        if len(r):
            left.append((r.min(), y + 0.5))
            right.append((r.max() + 1.0, y + 0.5))
    for x in cols:
        c = np.nonzero(m[:, x])[0] if 0 <= x < m.shape[1] else []
        if len(c):
            top.append((x + 0.5, c.min()))
            bottom.append((x + 0.5, c.max() + 1.0))
    if min(len(left), len(top)) < 8:
        raise QuadError("the mask is too small for a quad")
    L = [_robust_line(s, 1.5)[:2] for s in (top, right, bottom, left)]
    return order_quad(_corners(L))


def _bilinear(img, xs, ys):
    import cv2
    return cv2.remap(img, xs.astype("float32"), ys.astype("float32"), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


def side_points(field, q, side, R=6.0, n=200, step=0.125, t0=0.06, t1=0.94, min_contrast=0.35, normalise=True):
    """Sub-pixel edge points of one side of quad q on a 0..1 field (alpha / coverage; inside high): profiles along
    the outward normal at n places, each normalised between its inner and outer plateau, 0.5 crossing nearest the
    current side (normalise=False: the field is already 1 inside / 0 outside, e.g. a linear colour projection, and
    is used as is). Returns float32 [k, 2] points (pixel-centre coordinates are +0.5 of the index)."""
    q = np.float32(q)
    a, b = q[side], q[(side + 1) % 4]
    t = (b - a) / max(float(np.linalg.norm(b - a)), 1e-6)
    nrm = np.float32([t[1], -t[0]])
    if np.dot(q.mean(0) - a, nrm) > 0:
        nrm = -nrm                                            # outward
    ts = np.linspace(t0, t1, n)[:, None]
    base = a + (b - a) * ts
    offs = np.arange(-R, R + 1e-6, step, dtype="float32")
    P = base[:, None, :] + nrm[None, None, :] * offs[None, :, None]       # n x k x 2
    # field index (row, col) samples the pixel centre at (col + 0.5, row + 0.5)
    prof = _bilinear(field, P[..., 0] - 0.5, P[..., 1] - 0.5)
    k = max(3, int(1.0 / step))
    inner = np.median(prof[:, :k], 1) if normalise else np.ones(len(prof), "float32")
    outer = np.median(prof[:, -k:], 1) if normalise else np.zeros(len(prof), "float32")
    span = inner - outer
    ok = span > min_contrast
    pts = []
    for i in np.nonzero(ok)[0]:
        v = (prof[i] - outer[i]) / span[i]
        s = np.nonzero((v[:-1] >= 0.5) & (v[1:] < 0.5))[0]       # inside -> outside crossings
        if not len(s):
            continue
        j = s[np.argmin(np.abs(offs[s]))]                       # the one nearest the current side
        f = (v[j] - 0.5) / max(v[j] - v[j + 1], 1e-6)
        o = offs[j] + f * step
        pts.append(base[i] + nrm * o)
    return np.float32(pts).reshape(-1, 2)


def fit_quad(field, q0, iters=3, R=None, tol=0.75):
    """Sub-pixel quad on a 0..1 field starting from q0. Returns (quad, stats per side)."""
    q = order_quad(q0)
    size = min(math.dist(q[0], q[1]), math.dist(q[0], q[3]))
    R = R or float(np.clip(0.02 * size, 4, 10))
    stats = []
    for it in range(iters):
        lines, stats = [], []
        for side in range(4):
            pts = side_points(field, q, side, R=R if it == 0 else min(R, 4.0))
            if len(pts) < 20:
                raise QuadError(f"side {('top', 'right', 'bottom', 'left')[side]}: no clear edge in the mask")
            p0, p1, keep, rms = _robust_line(pts, tol)
            lines.append((p0, p1))
            stats.append({"points": int(len(pts)), "inliers": round(float(keep.mean()), 3), "rms_px": round(rms, 3)})
        q = order_quad(_corners(lines))
    return q, stats


SIDES = ("top", "right", "bottom", "left")


def verify_quad(q, alpha, q_mask, stats, max_rms=0.6, min_inliers=0.6, max_shift=None):
    """Loud failure when the corners disagree with the mask. Returns a dict of the measurements."""
    H, W = alpha.shape
    size = min(math.dist(q[0], q[1]), math.dist(q[0], q[3]))
    max_shift = max_shift or max(8.0, 0.03 * size)          # SAM's own edge is only good to a few px
    cov = poly_coverage(q, W, H)
    a = alpha > 0.5
    c = cov > 0.5
    iou = float((a & c).sum() / max((a | c).sum(), 1))
    shift = [round(math.dist(x, y), 2) for x, y in zip(order_quad(q), order_quad(q_mask))]
    why = []
    for s, st in zip(SIDES, stats):
        if st["inliers"] < min_inliers:
            why.append(f"{s} side: only {st['inliers']:.0%} of the mask edge lies on one straight line")
        if st["rms_px"] > max_rms:
            why.append(f"{s} side: mask edge wobbles {st['rms_px']:.2f} px around the fitted line")
    if iou < 0.985:
        why.append(f"quad vs mask overlap {iou:.3f} (< 0.985)")
    if max(shift) > max_shift:
        why.append(f"refined corners moved {max(shift):.1f} px from the SAM mask's corners (limit {max_shift:.1f})")
    out = {"iou": round(iou, 4), "corner_shift_px": shift, "sides": dict(zip(SIDES, stats))}
    if why:
        raise QuadError("corners disagree with the mask: " + "; ".join(why))
    return out


# ---------- the OPENING: the frame's hard inner edge (Tony 2026-11-12) ----------
#
# SAM + refine_alpha find where the PAPER looks like paper. Where the frame casts a shadow on the blank insert (a 3/4
# view shows the frame's dark inner wall, light from the side darkens the paper next to it, often with a warm bounce
# from the wood), that edge lands a few px INSIDE the real opening: measured on LVRM_Midcentury_Sideboard_2x3 the left
# side was 4.9 px short, so the art left a strip of baked grey shadow between the frame's hard dark wall and the art.
# The opening is the frame's HARD inner edge, the shadowed paper counted as opening: going outward from SAM's paper
# edge, the first HARD step in a shading-invariant material feature (chromaticity distance from the paper's own
# colour; a shadow or a warm bounce changes it slowly, the frame starts with a jump within ~1 px). Neutral frames
# (white / grey / black on white paper) use the log-brightness step instead. Sub-pixel per profile, one straight line
# per side, LOUD failure (QuadError) when a side has no hard edge, is not one straight line, or the band it adds
# between paper and frame does not look like shadowed paper.

OPENING_STEP_MIN = 0.2       # a hard edge: >= 20% of the paper->frame contrast within 1.5 px (shadow ramps: <= ~12%)
OPENING_CHROMA_MIN = 0.03    # paper->frame chromaticity contrast below this: neutral frame, brightness mode
OPENING_LUM_MIN = 0.1        # neutral frame: at least ~10% brighter / darker than the paper


def offset_quad(q, d):
    """Move every side of a quad outward by d (scalar or per side top, right, bottom, left; negative = inward)."""
    q = np.float32(q)
    c = q.mean(0)
    lines = []
    for i in range(4):
        a, b = q[i], q[(i + 1) % 4]
        t = (b - a) / max(float(np.linalg.norm(b - a)), 1e-6)
        n = np.float32([-t[1], t[0]])
        if np.dot(c - a, n) > 0:
            n = -n
        k = float(d[i] if np.ndim(d) else d)
        lines.append((a + n * k, b + n * k))
    return order_quad(_corners(lines))


def side_offsets(q_from, q_to):
    """Per side (top, right, bottom, left): how far q_to's side lies OUTSIDE q_from's (px along q_from's outward
    normal, mean of the 1/4 and 3/4 points)."""
    q_from, q_to = order_quad(q_from), order_quad(q_to)
    c = q_from.mean(0)
    out = []
    for i in range(4):
        a, b = q_from[i], q_from[(i + 1) % 4]
        t = (b - a) / max(float(np.linalg.norm(b - a)), 1e-6)
        n = np.float32([-t[1], t[0]])
        if np.dot(c - a, n) > 0:
            n = -n
        p, r = q_to[i], q_to[(i + 1) % 4] - q_to[i]
        ds = []
        for f in (0.25, 0.75):
            x = a + (b - a) * f
            cr = n[0] * r[1] - n[1] * r[0]
            ds.append(float(((p - x)[0] * r[1] - (p - x)[1] * r[0]) / cr) if abs(cr) > 1e-9 else 0.0)
        out.append(float(np.mean(ds)))
    return out


def _median_profile(img, q, side, offs, t0=0.12, t1=0.88, n=120):
    a, b = q[side], q[(side + 1) % 4]
    t = (b - a) / max(float(np.linalg.norm(b - a)), 1e-6)
    nrm = np.float32([t[1], -t[0]])
    if np.dot(q.mean(0) - a, nrm) > 0:
        nrm = -nrm                                            # outward
    ts = np.linspace(t0, t1, n, dtype="float32")[:, None]
    P = (a + (b - a) * ts)[:, None, :] + nrm[None, None, :] * np.float32(offs)[None, :, None]
    return np.median(_bilinear(img, P[..., 0] - 0.5, P[..., 1] - 0.5), 0)


def opening_quad(rgb, q_paper, reach=None):
    """The frame opening = the frame's HARD inner edge, shadowed paper included (see the block comment above), from
    SAM's refined paper quad. Returns (quad tl,tr,br,bl float32, info). Raises QuadError (loud) when it cannot be
    trusted."""
    import cv2
    q = order_quad(q_paper)
    H, W = rgb.shape[:2]
    size = min(math.dist(q[0], q[1]), math.dist(q[0], q[3]))
    reach = float(reach or np.clip(0.025 * size, 8.0, 16.0))
    pad = int(reach) + 8
    x0, y0 = max(0, int(q[:, 0].min()) - pad), max(0, int(q[:, 1].min()) - pad)
    x1, y1 = min(W, int(q[:, 0].max()) + pad + 1), min(H, int(q[:, 1].max()) + pad + 1)
    img = rgb[y0:y1, x0:x1].astype("float32")
    qc = q - np.float32([x0, y0])
    h, w = img.shape[:2]
    chrom = img / (img.sum(2, keepdims=True) + 0.5)                  # shading-invariant chromaticity
    lum = np.log(img @ np.float32([0.2126, 0.7152, 0.0722]) + 1.0)
    core = poly_coverage(offset_quad(qc, -max(12.0, 0.06 * size)), w, h) > 0.99
    if core.sum() < 200:
        raise QuadError("opening: the paper is too small")
    c_paper, l_paper = np.median(chrom[core], 0), float(np.median(lum[core]))
    feats = {"chroma": cv2.GaussianBlur(np.linalg.norm(chrom - c_paper, axis=2).astype("float32"), (0, 0), 0.6),
             "lum": cv2.GaussianBlur((l_paper - lum).astype("float32"), (0, 0), 0.6)}
    offs = np.arange(-3.0, reach + 3.0 + 1e-6, 0.25, dtype="float32")
    lines, info = [], {"sides": {}}
    for side in range(4):
        name = SIDES[side]
        pc = _median_profile(feats["chroma"], qc, side, offs)
        far = offs >= -2.0
        if float(pc[far].max()) >= OPENING_CHROMA_MIN:
            mode, f, prof = "chroma", feats["chroma"], pc
            lo, hi = 0.0, float(pc[far].max())
        else:                                                         # neutral frame: brightness
            pl = _median_profile(feats["lum"], qc, side, offs)
            outer = float(np.median(pl[offs >= reach]))
            if abs(outer) < OPENING_LUM_MIN:
                raise QuadError(f"opening: {name} side: the frame has neither a colour nor a brightness difference "
                                "from the paper")
            sgn = 1.0 if outer > 0 else -1.0                          # + = the frame is darker than the paper
            mode, f, prof = ("lum dark" if sgn > 0 else "lum bright"), feats["lum"] * sgn, pl * sgn
            lo, hi = 0.0, float((pl * sgn)[far].max())
        fn = (prof - lo) / max(hi - lo, 1e-6)
        step = np.interp(offs + 0.75, offs, fn) - np.interp(offs - 0.75, offs, fn)
        ok = (offs >= -2.0) & (offs <= reach) & (step >= OPENING_STEP_MIN)
        peaks = [i for i in np.nonzero(ok)[0] if step[i] >= step[max(i - 1, 0)] and step[i] >= step[min(i + 1, len(step) - 1)]]
        if not peaks:
            raise QuadError(f"opening: {name} side: no hard frame edge within {reach:.0f} px outside the paper "
                            f"(strongest step {float(step[(offs >= -2) & (offs <= reach)].max()):.2f})")
        d0 = float(offs[peaks[0]])                                    # the innermost hard step going outward
        band = (offs >= 0.75) & (offs <= d0 - 0.75)
        if band.any() and float(np.median(fn[band])) > 0.7:
            raise QuadError(f"opening: {name} side: the {d0:.1f} px between the paper and the hard edge look like "
                            "frame, not shadowed paper")
        # sub-pixel placement on a LINEAR field (an edge pixel is a linear mix of its two sides; log / chromaticity
        # crossings are biased): the RGB projection between the colours just inside and just outside the step
        rgbp = np.stack([_median_profile(img[..., k].copy(), qc, side, offs) for k in range(3)], 1)
        c_in = np.median(rgbp[(offs >= d0 - 1.75) & (offs <= d0 - 1.0)], 0)
        c_out = np.median(rgbp[(offs >= d0 + 1.0) & (offs <= d0 + 1.75)], 0)
        v = (c_in - c_out).astype("float32")
        if float(np.linalg.norm(v)) < 8.0:
            raise QuadError(f"opening: {name} side: the hard edge at {d0:+.1f} px has too little contrast")
        field = (cv2.GaussianBlur(img, (0, 0), 0.6) - c_out.astype("float32")) @ (v / float(v @ v))   # inside ~1
        # sub-pixel per profile around the side-level edge, two passes (the side may tilt against SAM's)
        qs = offset_quad(qc, [d0 if i == side else 0.0 for i in range(4)])
        for R in (2.5, 2.0):                      # plateaus 1.5-2.5 px out: clear of the edge pixel's blur
            pts = side_points(field, qs, side, R=R, min_contrast=0.3)
            if len(pts) < 40:
                raise QuadError(f"opening: {name} side: the hard edge is not visible along the side ({len(pts)} points)")
            p0, p1, keep, rms = _robust_line(pts, 0.75)
            lines_s = [None] * 4
            for i in range(4):
                lines_s[i] = (p0, p1) if i == side else (qs[i], qs[(i + 1) % 4])
            qs = order_quad(_corners(lines_s))
        st = {"mode": mode, "edge_px": round(d0, 2), "points": int(len(pts)), "inliers": round(float(keep.mean()), 3),
              "rms_px": round(rms, 3)}
        if st["inliers"] < 0.6 or rms > 0.6:
            raise QuadError(f"opening: {name} side: the hard edge is not one straight line ({st['inliers']:.0%} "
                            f"inliers, {rms:.2f} px rms)")
        lines.append((p0, p1))
        info["sides"][name] = st
    qo = order_quad(_corners(lines))
    offs_side = side_offsets(qc, qo)
    for name, o in zip(SIDES, offs_side):
        info["sides"][name]["offset_px"] = round(o, 2)
        if o < -1.0 or o > reach + 1.0:
            raise QuadError(f"opening: {name} side: the hard edge is {o:+.1f} px from SAM's paper edge (allowed "
                            f"-1 .. +{reach:.0f})")
    info["offset_px"] = {n: round(o, 2) for n, o in zip(SIDES, offs_side)}
    info["reach_px"] = round(reach, 1)
    return qo + np.float32([x0, y0]), info


def edge_truth(rgb, q0, mask=None, R=8.0):
    """INDEPENDENT reference corners for the precision test (no SAM logits, no guided filter): along each side, the
    raw photo's Lab projected on the paper -> frame axis (one global colour each, material_axis weights: colour first,
    lightness at 25% when the colours differ; in lightness mode pixels darker than both count as paper), profiled across the edge and
    normalised between its plateaus; the 0.5 crossing nearest the side is where the frame/mat material starts.
    Robust line per side, intersections, two passes."""
    import cv2
    lab = lab_image(rgb)
    H, W = rgb.shape[:2]
    q = order_quad(q0)
    m = poly_coverage(q, W, H) > 0.5 if mask is None else mask
    w, mi, mo, _ = material_axis(lab, m)
    if mi is None:
        raise QuadError("edge_truth: no ring")
    v = (mo - mi) * w
    labb = cv2.GaussianBlur(lab.astype("float32"), (0, 0), 0.6)
    # 0 = paper colour, 1 = frame/mat colour (global plateaus, raw pixels); darker than both = opening
    feat = np.clip(((labb - mi) * w) @ (v / max(float(v @ v), 1e-9)), 0, 1)
    if w[0] >= 1:
        feat = np.minimum(feat, 1 - _darker_than_both(labb[..., 0], mi[0], mo[0]))
    for _ in range(2):
        lines = []
        for side in range(4):
            pts = side_points(1.0 - feat, q, side, R=R, step=0.125, t0=0.08, t1=0.92, min_contrast=0.5)
            if len(pts) < 20:
                raise QuadError("edge_truth: no edge")
            lines.append(_robust_line(pts, 0.75)[:2])
        q = order_quad(_corners(lines))
    return q


def corner_error(q, known):
    q, k = order_quad(np.float32(q)), order_quad(np.float32(known).reshape(4, 2))
    d = [math.dist(a, b) for a, b in zip(q, k)]
    return {"per_corner_px": [round(x, 2) for x in d], "max_px": round(max(d), 2), "mean_px": round(sum(d) / 4, 2),
            "pass_1px": max(d) <= 1.0}


# ---------- detect ----------

def load_rgb(path):
    from PIL import Image
    with Image.open(path) as im:
        return np.asarray(im.convert("RGB"))


def detect(image_path, box=None, wall=False):
    """Full pipeline on one photo. Returns (result dict, refined alpha, wall alpha or None)."""
    if any(n in str(image_path) for n in NOT_ON):
        raise SystemExit("Not on the Wabi bedroom (verified by hand).")
    rgb = load_rgb(image_path)
    t0 = time.time()
    src = "given"
    if box is None:
        box, src = gemini_box(image_path), "gemini"
    errors = []
    for mask, logits, sel in segment_insert(rgb, box):
        try:
            q_mask = quad_from_mask(mask)
            alpha = refine_alpha(rgb, mask)
            q, stats = fit_quad(alpha, q_mask)
            ver = verify_quad(q, alpha, q_mask, stats)
            q_open, open_info = opening_quad(rgb, q)          # the frame's hard inner edge (Tony 2026-11-12)
            break
        except QuadError as e:
            errors.append(f"candidate {sel['area']} px: {e}")
    else:
        raise QuadError("; ".join(errors))
    if errors:
        sel["skipped"] = errors
    wall_a = None
    res = {"image": str(image_path), "box": [round(float(v), 1) for v in box], "box_source": src,
           "corners": np.round(q_open, 3).tolist(), "corners_paper": np.round(q, 3).tolist(), "opening": open_info,
           "corners_sam_mask": np.round(q_mask, 2).tolist(),
           "mask_px": int(mask.sum()), "sam": sel, "verify": ver,
           "model": f"sam2.1_hiera_{predictor().model_name}", "device": predictor().device_name}
    if wall:
        wm = segment_wall(rgb, q)
        if wm is not None:
            wall_a = refine_alpha(rgb, wm)
            res["wall_px"] = int((wall_a > 0.5).sum())
        else:
            res["wall_px"] = 0
    res["seconds"] = round(time.time() - t0, 1)
    return res, alpha, wall_a


def save_alpha(a, path):
    from PIL import Image
    Image.fromarray(np.round(np.clip(a, 0, 1) * 65535).astype("uint16")).save(path)


def read_alpha(path):
    from PIL import Image
    with Image.open(path) as im:
        a = np.asarray(im).astype("float32")
    return a / (65535.0 if a.max() > 255 else 255.0)


def overlay(image_path, alpha, q, out, q2=None):
    import cv2
    a = load_rgb(image_path).astype("float32")
    a = a * (1 - 0.35 * alpha[..., None]) + np.float32([255, 60, 40]) * 0.35 * alpha[..., None]
    a = np.clip(a, 0, 255).astype("uint8").copy()
    cv2.polylines(a, [np.int32(np.round(np.float32(q) * 16))], True, (0, 255, 255), 1, cv2.LINE_AA, shift=4)
    if q2 is not None:
        cv2.polylines(a, [np.int32(np.round(np.float32(q2) * 16))], True, (255, 0, 255), 1, cv2.LINE_AA, shift=4)
    from PIL import Image
    Image.fromarray(a).save(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="SAM 2 frame-insert corners + precision masks")
    ap.add_argument("mode", choices=["detect", "compare"])
    ap.add_argument("image")
    ap.add_argument("--box", help="x0,y0,x1,y1 rough box (skips Gemini)")
    ap.add_argument("--known", help="x,y x 4 known corners (compare mode)")
    ap.add_argument("--out", help="overlay PNG")
    ap.add_argument("--json", help="write the result JSON here")
    ap.add_argument("--alpha", help="16-bit PNG of the refined insert alpha")
    ap.add_argument("--wall", help="16-bit PNG of the refined wall alpha (SAM wall segmentation)")
    a = ap.parse_args(argv)
    box = [float(v) for v in a.box.split(",")] if a.box else None
    try:
        res, alpha, wall_a = detect(a.image, box, wall=bool(a.wall))
    except QuadError as e:
        res = {"image": a.image, "error": str(e)}
        if a.json:
            Path(a.json).write_text(json.dumps(res, indent=1))
        print(json.dumps(res, indent=1))
        sys.exit(2)
    if a.mode == "compare":
        if not a.known:
            sys.exit("--known x,y,x,y,x,y,x,y is required for compare")
        res["error_vs_known"] = corner_error(res["corners"], [float(v) for v in a.known.split(",")])
    if a.alpha:
        save_alpha(alpha, a.alpha)
    if a.wall and wall_a is not None:
        save_alpha(wall_a, a.wall)
    if a.out:
        overlay(a.image, alpha, res["corners"], a.out, res["corners_paper"])
        res["overlay"] = a.out
    if a.json:
        Path(a.json).write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))
    return res


if __name__ == "__main__":
    main()
