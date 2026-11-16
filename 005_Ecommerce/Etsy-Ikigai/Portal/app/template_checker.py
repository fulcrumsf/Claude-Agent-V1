"""Template checker (Tony 2026-11-10; spec Mockup_Docs/Template_Layer_Rules_And_Checker_Spec.md). Headless, READ-ONLY:
every check renders the PSD with photocraft-cli (`run <psd> ... --out <png>` into a temp folder) and measures the
renders; the PSD is never saved (its size + mtime are compared before and after, and a change is reported).

Per template, PASS / FAIL with plain reasons:
  1 opening   art area vs the frame opening, both SUB-PIXEL: the visible art quad is fitted to the anti-aliased
              black/white card difference; the opening is SAM 2's opening on a render with the art and overlays
              hidden (sam_opening; 2026-11-10). Since 2026-11-12 the opening is the frame's HARD inner edge with
              the shadowed paper counted as opening (sam_frames.opening_quad): FAIL on a gap > 0.5 px (baked
              paper/shadow shows) or art > 2.5 px under the frame (the allowed pad is 1-2 px, hidden by the Frame
              Hard Shadow layer). Falls back to the old edge search (inner frame / mat edge nearest each side,
              +-3 px) when SAM is not installed, fails, or the template has a mat.
  2 card      black card vs white card: pixels inside the opening that do not change = a gap (white sliver);
              pixels beyond the opening + the 2 px pad that change = art over the frame
  3 overlay   every shadow / glare layer's effect stays inside the art opening (rendered alone over a grey card)
  4 purity    every shadow layer is neutral (black fill: R = G = B) and smooth (not copied photo pixels)
  5 sun       the wall's sun line (light/shade edge measured on the base, ONLY on SAM's wall mask) vs the shadow
              layer's edge, within 3 deg; a straight light edge on the art with no sun line confirmed on the wall
              fails, and so does a light shadow over the art where the photo still shows a print (2026-11-15)
  6 ratio     opening ratio vs the folder's ratio within 3% (cover-fit crop limit); smart object not stretched
  7 mat       when a mat exists: uniform width on all four sides, bevel / shadow layer present
  placement   wall molding / wainscoting: the frame never hangs over molding, and inside a wall panel it sits
              centred with margin (no molding near the frame = pass; 2026-11-15)
  8 layers    `Place Artwork Here`, SHADOWS and GLARE present; no hidden "OLD ..." layers waiting for Tony

Results: config/template_checks.json ({rel: result}), shown on the Templates tab. CLI:
    python -m app.template_checker --all            check every template in the library
    python -m app.template_checker <rel> [<rel>...]  check some (rel = path under Portrait_Templates)
    python -m app.template_checker --fails          print the FAIL list from the results file
"""
import json
import math
import shutil
import subprocess
import tempfile
import threading
from datetime import datetime
from pathlib import Path

import numpy as np

from .db import ROOT

RESULTS = ROOT / "config" / "template_checks.json"
ART = "Place Artwork Here"
TOL_PX = 3              # opening vs art, per side (old integer edge search only)
# Tony 2026-11-12: the opening is the frame's HARD inner edge (shadowed paper counted as opening); the art runs
# 1-2 px under it (scene_templates opening_pad_px 1.5) and the Frame Hard Shadow layer darkens that pad. With the
# sub-pixel SAM opening: art short of the opening by more than EDGE_TOL_PX = a sliver of baked paper/shadow (FAIL);
# art under the frame by more than PAD_MAX_PX + EDGE_TOL_PX = art over the frame (FAIL).
PAD_MAX_PX = 2.0
EDGE_TOL_PX = 0.5
TOL_RATIO = 0.03        # cover-fit crop limit
TOL_DEG = 3.0           # sun angle
RATIO_TARGETS = {"2x3": [2 / 3], "3x4": [0.75], "4x5": [0.8], "11x14": [11 / 14], "iso": [1 / 2 ** 0.5, 5 / 7]}
OVERLAY_BLENDS = {"Multiply", "Screen", "Overlay", "Soft Light", "Hard Light", "Linear Burn", "Color Burn",
                  "Linear Dodge (Add)", "Linear Dodge", "Darken", "Lighten", "Color Dodge"}
OVERLAY_WORDS = ("shadow", "glare", "reflection", "glass", "sheen", "light", "shade", "highlight")
STRUCT_WORDS = ("mat", "matte", "frame", "fame", "paper", "foreground", "canvas", "border")
# layers the 2026-11-08 standardisation script built FROM PHOTO PIXELS (Room_Templates/Directory.md "Layer structure":
# "Scene Light & Shadow ... is the blank insert from the photo"; spec item 3: Frame Edge Shadow + Scene Light & Shadow
# were photo copies). Suspect until rebuilt as black fills (template.json "layers_verified" marks a rebuilt template).
PHOTO_BUILT = {"Scene Light & Shadow", "Frame Edge Shadow"}
CHECKS = ["opening", "card", "overlay", "purity", "sun", "ratio", "mat", "placement", "layers"]
LABELS = {"opening": "Opening vs art", "card": "Black/white card", "overlay": "Overlay size", "purity": "Overlay purity",
          "sun": "Sun angle", "ratio": "Ratio", "mat": "Mat", "placement": "Placement (wall molding)",
          "layers": "Layer names"}
_job = {"running": False, "done": 0, "total": 0, "current": "", "error": ""}
_job_lock = threading.Lock()


class CheckError(Exception):
    pass


# ---------- photocraft-cli ----------

def _bin(settings=None):
    return (settings or {}).get("photocraft_bin", "photocraft-cli")


def _run(settings, args, timeout=300):
    b = _bin(settings)
    if not shutil.which(b):
        raise CheckError(f"{b} is not on PATH")
    r = subprocess.run([b, *args], capture_output=True, text=True, timeout=timeout)
    if r.returncode:
        raise CheckError(f"PhotoCraft failed: {(r.stderr or r.stdout).strip()[-300:]}")
    return r.stdout


def _cmd(c, p=None):
    return ["--cmd", c, "--params", json.dumps(p or {})]


def info(psd, settings=None):
    return json.loads(_run(settings, ["info", str(psd)]))


def flatten(layers, parents=(), out=None):
    """Layer tree -> list (top of the stack first) of dicts with `parents` (names) and `shown` (layer and every
    parent visible)."""
    out = [] if out is None else out
    for l in layers or []:
        kids = l.get("children") or l.get("layers") or []
        d = {k: v for k, v in l.items() if k not in ("children", "layers")}
        d["parents"] = list(parents)
        d["shown"] = bool(l.get("visible", True)) and all(p.get("visible", True) for p in parents)
        out.append(d)
        flatten(kids, (*parents, l), out)
    for d in out:
        d["parents"] = [p.get("name", "") if isinstance(p, dict) else p for p in d["parents"]]
    return out


def roles(flat):
    """Which layer is the art, the base, the overlays (shadow / glare above the art), mats, foreground."""
    idx = {l["id"]: i for i, l in enumerate(flat)}
    art = next((l for l in flat if l.get("name") == ART and l.get("kind") == "Smart Object"), None) \
        or next((l for l in flat if l.get("name") == ART), None)
    pix = [l for l in flat if l.get("kind") in ("Pixel", "Smart Object") and l is not art]
    base = pix[-1] if pix else None
    ai = idx[art["id"]] if art else len(flat)

    def low(l):
        return " ".join([l.get("name", "")] + l.get("parents", [])).lower()
    fg = [l for l in flat if "foreground" in low(l)]
    mats = [l for l in flat if any(w in l.get("name", "").lower().split() or l.get("name", "").lower().startswith(w)
                                   for w in ("mat", "matte", "picture matte")) or l.get("name") in ("MAT",)
            or "matte" in l.get("name", "").lower() or (l.get("name", "").lower().startswith("paper"))]
    mats = [l for l in mats if l is not art and "place artwork" not in l.get("name", "").lower()]
    overlays = []
    for l in flat[:ai]:
        if l.get("kind") not in ("Pixel", "Smart Object") or l in fg or not l["shown"]:
            continue
        nm = low(l)
        struct = any(w in l.get("name", "").lower() for w in STRUCT_WORDS) and not any(
            w in l.get("name", "").lower() for w in ("shadow", "bevel", "reflection", "glass"))
        if struct:
            continue
        if l.get("blend") in OVERLAY_BLENDS or any(w in nm for w in OVERLAY_WORDS):
            overlays.append(l)
    return {"art": art, "base": base, "overlays": overlays, "mats": mats, "foreground": fg, "art_index": ai}


def _hide(ids):
    out = []
    for i in ids:
        out += _cmd("layer.setProps", {"layer": i, "visible": False})
    return out


def render(psd, out, settings=None, hide=(), card=None, art_hidden=False, art_id=None):
    args = ["run", str(psd)]
    if card is not None:
        args += _cmd("layer.select", {"name": ART}) + _cmd("layer.smartObjects.replaceContents", {"path": str(card)})
    ids = list(hide) + ([art_id] if art_hidden and art_id is not None else [])
    args += _hide(ids) + ["--out", str(out)]
    _run(settings, args)
    from PIL import Image
    with Image.open(out) as im:
        return np.asarray(im.convert("RGB")).astype("float32")


def so_size(psd, settings=None, work=None):
    from PIL import Image
    out = Path(work or tempfile.mkdtemp()) / "so.png"
    _run(settings, ["run", str(psd), *_cmd("layer.select", {"name": ART}),
                    *_cmd("layer.smartObjects.exportContents", {"path": str(out)})])
    with Image.open(out) as im:
        return list(im.size)


# ---------- geometry ----------

def order_quad(pts):
    from .rooms import order_quad as oq
    return oq(pts)


def quad_from_mask(m):
    import cv2
    from .rooms import _quad_from_hull
    cs, _ = cv2.findContours(m.astype("uint8") * 255, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cs:
        return None
    c = max(cs, key=cv2.contourArea)
    if cv2.contourArea(c) < 400:
        return None
    return order_quad(_quad_from_hull(cv2.convexHull(c)))


def poly_mask(q, W, H):
    import cv2
    m = np.zeros((H, W), "uint8")
    cv2.fillPoly(m, [np.int32(np.round(np.float32(q) * 4))], 1, lineType=cv2.LINE_8, shift=2)
    return m.astype(bool)


def offset_quad(q, d):
    """Move every side of a quad outward by d[i] px (d negative = inward); sides: top, right, bottom, left."""
    q = np.float32(q)
    c = q.mean(0)
    lines = []
    for i in range(4):
        a, b = q[i], q[(i + 1) % 4]
        t = (b - a) / max(np.linalg.norm(b - a), 1e-6)
        n = np.float32([-t[1], t[0]])
        if np.dot(c - a, n) > 0:
            n = -n                       # outward normal
        k = d[i] if np.ndim(d) else d
        lines.append((a + n * k, b + n * k))
    out = []
    for i in range(4):
        (p, p2), (s, s2) = lines[(i - 1) % 4], lines[i]
        r, u = p2 - p, s2 - s
        cr = r[0] * u[1] - r[1] * u[0]
        if abs(cr) < 1e-9:
            return q
        out.append(p + r * (((s - p)[0] * u[1] - (s - p)[1] * u[0]) / cr))
    return np.float32(out)


def side_profile(img, a, b, n_out, R, t0=0.2, t1=0.8, k=60):
    """Median colour at offsets -R..R (outward positive) across the side a->b."""
    H, W = img.shape[:2]
    ts = np.linspace(t0, t1, k)[:, None]
    base = a + (b - a) * ts
    prof = []
    for d in range(-R, R + 1):
        p = base + n_out * d
        xs = np.clip(np.round(p[:, 0]).astype(int), 0, W - 1)
        ys = np.clip(np.round(p[:, 1]).astype(int), 0, H - 1)
        prof.append(np.median(img[ys, xs], axis=0))
    return np.array(prof, "float32")


def find_edge(img, q, side, R, prefer="inner", start=0, min_step=14.0):
    """Offset (px, outward positive) of a strong colour step across one side of quad q, searched over -R..R.
    prefer='inner': the first strong step met going outward from R px inside (the opening = the INNER edge of the
    frame or mat; the frame's outer edge lies further out); 'near': the strong step nearest to `start`;
    'next': the first strong step beyond `start` going outward (a mat's outer edge).
    Returns (offset or None, strength)."""
    q = np.float32(q)
    a, b = q[side], q[(side + 1) % 4]
    t = (b - a) / max(np.linalg.norm(b - a), 1e-6)
    n = np.float32([-t[1], t[0]])
    if np.dot(q.mean(0) - a, n) > 0:
        n = -n
    w = 2                                                          # a soft paper->frame edge spreads over ~4 px
    prof = side_profile(img, a, b, n, R + w)
    # total colour change across a 2w window centred between offsets d and d+1 (index i <-> offset i - R + 0.5)
    sm = np.array([np.linalg.norm(prof[i + 2 * w] - prof[i]) for i in range(len(prof) - 2 * w - 1 + 1)], "float32")
    sm = sm[:2 * R]
    if sm.size == 0:
        return None, 0.0
    top = float(sm.max())
    if top < min_step:
        return None, top
    strong = [i for i in range(len(sm)) if sm[i] >= max(0.3 * top, min_step)
              and (i == 0 or sm[i] >= sm[i - 1]) and (i == len(sm) - 1 or sm[i] > sm[i + 1])]
    pos = [i - R + 0.5 for i in strong]
    if not pos:
        return None, top
    if prefer == "inner":                    # the first strong step met going outward from inside the art
        for p in sorted(pos):
            if p < -2 and _paper_band(prof, int(p + R + w), R + w):
                continue      # the band between this edge and the art edge is paper (a sample print's white border
                              # or the blank insert), not frame wood: the opening is further out
            return p, top
        return max(pos), top
    if prefer == "next":
        beyond = [p for p in pos if p > start + 2]
        return (min(beyond), top) if beyond else (None, top)
    return min(pos, key=lambda p: (abs(p - start), -p)), top


def _paper_band(prof, i0, i1):
    """Is the profile between indexes i0..i1 bright, neutral paper (not a frame)?"""
    band = prof[max(0, i0 + 2):max(i0 + 3, i1)]
    if not len(band):
        return False
    c = np.median(band, axis=0)
    mx, mn = float(c.max()), float(c.min())
    return mx > 0.7 * 255 and (mx - mn) / max(mx, 1) < 0.07


def true_aspect(q, size):
    from .rooms import true_aspect as ta
    return ta(np.float32(q), size)


def side_lengths(q):
    q = np.float32(q)
    return [math.dist(q[i], q[(i + 1) % 4]) for i in range(4)]


# ---------- sun line ----------

def _lines(gray, mask, min_len, ref_h=None):
    """Straight edges (full-resolution coordinates). Soft light edges (a sun line's penumbra) only show as edges on
    a reduced image, so the search runs at about 200 px per art height."""
    import cv2
    f = min(1.0, 200.0 / max(ref_h or min_len * 4, 1))
    g = cv2.resize(gray.astype("float32"), None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
    m = cv2.resize(mask.astype("uint8"), None, fx=f, fy=f, interpolation=cv2.INTER_NEAREST).astype(bool)
    g = cv2.GaussianBlur(g, (0, 0), 1.2)
    e = cv2.Canny(np.clip(g, 0, 255).astype("uint8"), 6, 14)
    e[~m] = 0
    L = max(8, int(min_len * f))
    ls = cv2.HoughLinesP(e, 1, np.pi / 360, threshold=max(8, int(L * 0.35)), minLineLength=L, maxLineGap=6)
    return [] if ls is None else [[int(round(v / f)) for v in l[0]] for l in ls]


def _angle(x1, y1, x2, y2):
    """Angle of a line in degrees, rising to the right positive, folded to (-90, 90]."""
    a = math.degrees(math.atan2(-(y2 - y1), x2 - x1))
    while a <= -90:
        a += 180
    while a > 90:
        a -= 180
    return a


def _step_across(gray, x1, y1, x2, y2, w=6):
    """Mean brightness difference between the two sides of a segment (relative)."""
    n = np.float32([-(y2 - y1), x2 - x1])
    n /= max(np.linalg.norm(n), 1e-6)
    ts = np.linspace(0.15, 0.85, 30)[:, None]
    p = np.float32([x1, y1]) + (np.float32([x2, y2]) - np.float32([x1, y1])) * ts
    H, W = gray.shape

    def at(pts):
        xs = np.clip(np.round(pts[:, 0]).astype(int), 0, W - 1)
        ys = np.clip(np.round(pts[:, 1]).astype(int), 0, H - 1)
        return gray[ys, xs]
    s1, s2 = at(p + n * w), at(p - n * w)
    return float(np.median(s1 - s2)) / max(float(np.median(np.maximum(s1, s2))), 1.0)


def sun_line(rgb, opening_q, search=1.0, wall=None):
    """The wall's light/shade edge near the frame: the longest straight diagonal brightness step in a band around
    the opening (frame excluded; with `wall` (a SAM wall alpha) only on the wall itself). Returns {deg, line,
    contrast} or None."""
    H, W = rgb.shape[:2]
    gray = rgb @ np.float32([0.299, 0.587, 0.114])
    q = np.float32(opening_q)
    x0, y0 = q.min(0)
    x1, y1 = q.max(0)
    w, h = x1 - x0, y1 - y0
    box = np.zeros((H, W), bool)
    box[int(max(0, y0 - search * h)):int(min(H, y1 + 0.35 * h)), int(max(0, x0 - search * w)):int(min(W, x1 + search * w))] = True
    frame = poly_mask(offset_quad(q, [0.1 * max(w, h)] * 4), W, H)
    mask = box & ~frame
    if wall is not None:
        import cv2
        mask &= cv2.erode((wall > 0.5).astype("uint8"), np.ones((7, 7), "uint8")) > 0   # away from the wall's own edge
    best = None
    for x_1, y_1, x_2, y_2 in _lines(gray, mask, 0.22 * h, h):
        a = _angle(x_1, y_1, x_2, y_2)
        if not 8 <= abs(a) <= 75:
            continue
        L = math.dist((x_1, y_1), (x_2, y_2))
        if L < 0.3 * h:                          # a real sun line runs a good way across the wall
            continue
        st = _step_across(gray, x_1, y_1, x_2, y_2, w=max(6, int(0.012 * h)))
        if abs(st) < 0.05:
            continue
        sc = L * min(abs(st), 0.4)
        if best is None or sc > best["score"]:
            best = {"deg": round(a, 1), "line": [int(x_1), int(y_1), int(x_2), int(y_2)], "contrast": round(st, 3),
                    "score": sc}
    return best


# ---------- placement: wall molding / wainscoting around the frame (Tony 2026-11-15) ----------
# Wainscoting is optional (elegant / traditional rooms only); a template WITHOUT it is never marked down. When there
# is molding near the frame: (a) covered = a molding line seen on BOTH sides of the frame at the same position runs
# behind it (a real frame cannot hang flat over raised molding); 4+ evenly spaced lines = wall texture (brick, boards),
# not molding. (b) panel = molding borders left AND right AND above or below (each running past the frame on both
# ends): FAIL when the frame is within 3% of its size of a border (touching), off-centre left/right by more than 25%
# or up/down by more than 50%. Prototype tuned on the 44 templates of 2026-11-15 (Scripts/placement_check.py).
PLACEMENT_OK = {   # template name part -> why Tony accepted its flag by eye (the check passes with this note)
    "LVRM_Floor_ISO": "Tony 2026-11-15: the skirting board behind a frame leaning on the floor is fine"}


def frame_outer(gray, V):
    """Outer frame box (x0, y0, x1, y1, [top, right, bottom, left] widths): per side, the outermost strong brightness
    step 1-12% of the size outside the visible art."""
    import cv2
    V = np.float32(V)
    x0, y0 = V.min(0)
    x1, y1 = V.max(0)
    w, h = x1 - x0, y1 - y0
    R = int(0.12 * max(w, h))
    H, W = gray.shape
    g = cv2.GaussianBlur(gray, (0, 0), 1.5)
    out = []
    for side in range(4):
        prof = []
        for d in range(2, R):
            if side == 0:
                ys, xs = int(y0 - d), np.arange(int(x0 + 0.2 * w), int(x1 - 0.2 * w))
            elif side == 2:
                ys, xs = int(y1 + d), np.arange(int(x0 + 0.2 * w), int(x1 - 0.2 * w))
            elif side == 3:
                xs, ys = int(x0 - d), np.arange(int(y0 + 0.2 * h), int(y1 - 0.2 * h))
            else:
                xs, ys = int(x1 + d), np.arange(int(y0 + 0.2 * h), int(y1 - 0.2 * h))
            prof.append(float(np.median(g[np.clip(ys, 0, H - 1), np.clip(xs, 0, W - 1)])))
        prof = np.array(prof)
        step = np.abs(prof[3:] - prof[:-3]) if len(prof) > 3 else np.zeros(1)
        lo = max(1, int(0.01 * max(w, h)))
        cand = np.nonzero(step[lo:] >= 0.5 * step[lo:].max())[0] if len(step) > lo else []
        d = (lo + cand[-1] + 4) if len(cand) and step[lo:].max() > 6 else int(0.04 * max(w, h))
        out.append(int(d))
    return float(x0 - out[3]), float(y0 - out[0]), float(x1 + out[1]), float(y1 + out[2]), out


def _merge_lines(segs, vertical, tol=4.0):
    """Nearly collinear axis-aligned segments -> lines [pos, start, end, total length, [(start, end)...]]."""
    items = []
    for x1, y1, x2, y2 in segs:
        L = math.hypot(x2 - x1, y2 - y1)
        ang = abs(math.degrees(math.atan2(y2 - y1, x2 - x1))) % 180
        if vertical and abs(ang - 90) > 3:
            continue
        if not vertical and min(ang, 180 - ang) > 6:
            continue
        pos = (x1 + x2) / 2 if vertical else (y1 + y2) / 2
        a, b = (min(y1, y2), max(y1, y2)) if vertical else (min(x1, x2), max(x1, x2))
        items.append([pos, a, b, L, [(a, b)]])
    items.sort(key=lambda it: it[0])
    lines = []
    for it in items:
        if lines and abs(it[0] - lines[-1][0]) < tol:
            l = lines[-1]
            l[0] = (l[0] * l[3] + it[0] * it[3]) / (l[3] + it[3])
            l[1], l[2], l[3] = min(l[1], it[1]), max(l[2], it[2]), l[3] + it[3]
            l[4] += it[4]
        else:
            lines.append([it[0], it[1], it[2], it[3], list(it[4])])
    return lines


def placement(rgb, V):
    """Does the frame sit physically right among the wall's molding? rgb = the scene render (art, overlays and
    foreground hidden), V = the visible art quad. Returns {flag: [reasons], covered, gaps_px, off_centre, ...};
    an empty flag list = pass (no molding near the frame passes)."""
    import cv2
    gray = (np.asarray(rgb, "float32") @ np.float32([0.299, 0.587, 0.114])).astype("float32")
    H, W = gray.shape
    fx0, fy0, fx1, fy1, fw = frame_outer(gray, V)
    fwid, fhei = fx1 - fx0, fy1 - fy0
    S = max(fwid, fhei)
    m = np.zeros((H, W), bool)                                   # around the frame, the frame itself excluded
    m[int(max(0, fy0 - 0.6 * fhei)):int(min(H, fy1 + 0.35 * fhei)),
      int(max(0, fx0 - 0.6 * fwid)):int(min(W, fx1 + 0.6 * fwid))] = True
    m[int(max(0, fy0 - 3)):int(fy1 + 3), int(max(0, fx0 - 3)):int(fx1 + 3)] = False
    ls = cv2.createLineSegmentDetector(cv2.LSD_REFINE_STD).detect(
        cv2.GaussianBlur(gray, (0, 0), 1.0).astype("uint8"))[0]
    segs = []
    for x1, y1, x2, y2 in (np.asarray(ls).reshape(-1, 4) if ls is not None else []):
        mx, my = int((x1 + x2) / 2), int((y1 + y2) / 2)
        if 0 <= my < H and 0 <= mx < W and m[my, mx]:
            segs.append((float(x1), float(y1), float(x2), float(y2)))
    vl = [l for l in _merge_lines(segs, True) if l[3] >= 0.12 * fhei]
    hl = [l for l in _merge_lines(segs, False) if l[3] >= 0.12 * fwid]

    def both_sides(sg, lo, hi, size):
        near_lo = sum(b - a for a, b in sg if b > lo - 0.3 * size and a < lo + 4)
        near_hi = sum(b - a for a, b in sg if a < hi + 0.3 * size and b > hi - 4)
        return near_lo >= 0.06 * size and near_hi >= 0.06 * size
    covered = []
    for pos, a, b, L, sg in vl:
        if fx0 + 0.03 * fwid < pos < fx1 - 0.03 * fwid and both_sides(sg, fy0, fy1, fhei):
            covered.append({"dir": "vertical", "x": round(pos), "span": [round(a), round(b)], "len": round(L)})
    for pos, a, b, L, sg in hl:
        if fy0 + 0.03 * fhei < pos < fy1 - 0.03 * fhei and both_sides(sg, fx0, fx1, fwid):
            covered.append({"dir": "horizontal", "y": round(pos), "span": [round(a), round(b)], "len": round(L)})
    texture = []
    for d_ in ("horizontal", "vertical"):                      # 4+ evenly spaced lines = wall texture, not molding
        ps = sorted(c["y" if d_ == "horizontal" else "x"] for c in covered if c["dir"] == d_)
        cl = []
        for v_ in ps:
            if cl and v_ - cl[-1][-1] < 0.04 * S:
                cl[-1].append(v_)
            else:
                cl.append([v_])
        cen = [sum(c) / len(c) for c in cl]
        if len(cen) >= 4:
            sp = np.diff(cen)
            if (np.abs(sp / np.median(sp) - 1) < 0.25).sum() >= 3:
                covered = [c for c in covered if c["dir"] != d_]
                texture.append(d_)

    def nearest(lines, lo, hi, band_lo, band_hi, before):
        sp_ = band_hi - band_lo                 # a panel border runs past the frame on BOTH ends
        c = [l for l in lines if (l[0] < lo if before else l[0] > hi)
             and l[1] < band_lo - 0.015 * sp_ and l[2] > band_hi + 0.015 * sp_
             and (band_lo - l[1]) + (l[2] - band_hi) > 0.2 * sp_]
        if not c:
            return None
        l = max(c, key=lambda l: l[0]) if before else min(c, key=lambda l: l[0])
        return round(float(lo - l[0] if before else l[0] - hi), 1)
    gaps = {"left": nearest(vl, fx0, fx1, fy0, fy1, True), "right": nearest(vl, fx0, fx1, fy0, fy1, False),
            "top": nearest(hl, fy0, fy1, fx0, fx1, True), "bottom": nearest(hl, fy0, fy1, fx0, fx1, False)}
    off = {}
    if gaps["left"] is not None and gaps["right"] is not None:
        off["horizontal"] = round(abs(gaps["left"] - gaps["right"]) / max(gaps["left"] + gaps["right"], 1), 2)
    if gaps["top"] is not None and gaps["bottom"] is not None:
        off["vertical"] = round(abs(gaps["top"] - gaps["bottom"]) / max(gaps["top"] + gaps["bottom"], 1), 2)
    panel = gaps["left"] is not None and gaps["right"] is not None and (gaps["top"] is not None or
                                                                        gaps["bottom"] is not None)
    flag = []
    if covered:
        flag.append(f"the frame hangs over {len(covered)} wall molding line(s) (the molding continues on both sides "
                    "of it); regenerate the scene")
    if panel:
        touch = [k for k, g in gaps.items() if g is not None and g < 0.03 * S]
        if touch:
            flag.append("the frame touches the panel molding on the " + ", ".join(touch))
        if off.get("horizontal", 0) > 0.25:
            flag.append(f"off-centre in its wall panel left/right ({off['horizontal']:.0%})")
        if off.get("vertical", 0) > 0.5:
            flag.append(f"off-centre in its wall panel up/down ({off['vertical']:.0%})")
    return {"flag": flag, "frame_outer": [round(v) for v in (fx0, fy0, fx1, fy1)], "gaps_px": gaps,
            "off_centre": off, "panel": panel, "covered": covered, "texture": texture,
            "lines": {"v": len(vl), "h": len(hl)}}


def insert_texture(rgb, O):
    """Brightness spread (0..1) of the photo inside the opening around a fitted light plane: blank paper is about
    0.01, an old sample print far more (scene_templates.INSERT_TEXTURE_MAX)."""
    from . import sam_frames as sf
    from . import scene_templates as stp
    H, W = rgb.shape[:2]
    Y = (np.asarray(rgb, "float32") / 255.0) @ stp.W709
    ys, xs = np.nonzero(sf.poly_coverage(stp._expand(np.float32(O), -0.08), W, H) > 0.99)
    if len(xs) < 50:
        return 0.0
    A = np.c_[xs + 0.5, ys + 0.5, np.ones_like(xs)].astype("float64")
    coef, *_ = np.linalg.lstsq(A, Y[ys, xs].astype("float64"), rcond=None)
    return float(np.std(Y[ys, xs] - A @ coef))


def is_falloff(effect, inside):
    """A smooth light falloff (scene_templates.key_light 'falloff': a plane clipped to 0..1) has no light/shade edge,
    even where it is steep: over at least a quarter of the art the effect is one plane to within 6% of its range."""
    ys, xs = np.nonzero(inside)
    if len(xs) < 200:
        return False
    v = effect[ys, xs].astype("float64")
    rng = float(np.percentile(v, 99) - np.percentile(v, 1))
    if rng < 1e-4:
        return True
    keep = (v > np.percentile(v, 1) + 0.02 * rng) & (v < np.percentile(v, 99) - 0.02 * rng)   # unclipped part
    if keep.sum() < max(100, 0.25 * len(v)):         # a sun band ramps only in a narrow strip: not a falloff
        return False
    A = np.c_[xs[keep], ys[keep], np.ones(int(keep.sum()))].astype("float64")
    coef, *_ = np.linalg.lstsq(A, v[keep], rcond=None)
    return float(np.std(v[keep] - A @ coef)) < 0.06 * rng


def overlay_edge(effect, inside):
    """Dominant straight diagonal edge of a shadow layer's effect map inside the art (deg) or None."""
    if not inside.any() or is_falloff(effect, inside):
        return None
    e = effect.copy()
    e[~inside] = 0
    top = float(np.percentile(e[inside], 99)) or 1.0
    g = np.clip(e / top * 255, 0, 255)
    h = inside.any(1).sum()
    best = None
    for x1, y1, x2, y2 in _lines(g, inside, 0.2 * h, h):
        a = _angle(x1, y1, x2, y2)
        if not 8 <= abs(a) <= 75:
            continue
        if abs(_step_across(g, x1, y1, x2, y2, w=max(3, int(0.01 * h)))) < 0.12:
            continue                     # a smooth light falloff has no edge (only a real light/shade line counts)
        L = math.dist((x1, y1), (x2, y2))
        if best is None or L > best[1]:
            best = (round(a, 1), L, [int(x1), int(y1), int(x2), int(y2)])
    return {"deg": best[0], "line": best[2]} if best else None


def visible_quad_subpixel(D, V):
    """Sub-pixel quad of the visible art from the anti-aliased black/white card difference (app/sam_frames.fit_quad);
    the integer hull quad when the fit fails (a prop clipping a corner)."""
    from . import sam_frames as sf
    try:
        q, _ = sf.fit_quad(np.clip(D, 0, 1).astype("float32"), np.float32(V), R=3.0)
        return q if np.abs(q - np.float32(V)).max() < 6 else np.float32(V)
    except Exception:  # noqa: BLE001
        return np.float32(V)


def sam_opening(bg_png, V, settings=None, work=None, psd=None):
    """The frame opening on the BASE-only render, by SAM 2 (scene_templates.sam_detect: box = the visible art +4%,
    material-edge refinement, sub-pixel corners, loud failure) plus SAM's wall mask (for the sun-line search).
    Returns (quad, model, wall alpha or None) or (None, reason, None). A SAM quad that does not overlap the art
    (IoU < 0.8) is not trusted."""
    from . import sam_frames as sf
    from . import scene_templates as stp
    if (settings or {}).get("checker_use_sam") is False:
        return None, "switched off", None
    if psd is not None and any(n in str(psd) for n in sf.NOT_ON):
        return None, "never on this template (verified by hand)", None
    V = np.float32(V)
    x0, y0 = V.min(0)
    x1, y1 = V.max(0)
    pad = 0.04 * max(x1 - x0, y1 - y0)
    try:
        res, _, wall = stp.sam_detect(bg_png, work, settings, box=[x0 - pad, y0 - pad, x1 + pad, y1 + pad], wall=True)
    except stp.TemplateError as e:
        return None, str(e)[:160], None
    O = np.float32(res["corners"])
    from PIL import Image
    with Image.open(bg_png) as im:
        W, H = im.size
    a, b = sf.poly_coverage(O, W, H) > 0.5, sf.poly_coverage(V, W, H) > 0.5
    iou = float((a & b).sum() / max((a | b).sum(), 1))
    if iou < 0.8:
        return None, f"SAM found a different region (IoU {iou:.2f} with the art)", None
    return O, res.get("model", "sam2"), wall


def side_offsets(V, O):
    """Per side (top, right, bottom, left): how far O's side lies OUTSIDE V's side (px, along V's outward normal,
    mean of the quarter points). Positive = a gap between art and frame, negative = art over the frame."""
    V, O = np.float32(V), np.float32(O)
    c = V.mean(0)
    out = []
    for i in range(4):
        a, b = V[i], V[(i + 1) % 4]
        t = (b - a) / max(np.linalg.norm(b - a), 1e-6)
        n = np.float32([-t[1], t[0]])
        if np.dot(c - a, n) > 0:
            n = -n
        p, r = O[i], O[(i + 1) % 4] - O[i]
        ds = []
        for f in (0.25, 0.75):
            x = a + (b - a) * f
            cr = n[0] * r[1] - n[1] * r[0]
            ds.append(((p - x)[0] * r[1] - (p - x)[1] * r[0]) / cr if abs(cr) > 1e-9 else 0.0)
        out.append(float(np.mean(ds)))
    return out


def opening_verdict(offs, subpixel=True):
    """Per side offsets (top, right, bottom, left; + = the opening lies OUTSIDE the art = a gap, - = the art runs
    under the frame). Sub-pixel SAM opening (the frame's hard inner edge): a gap beyond EDGE_TOL_PX fails (a sliver
    of baked paper/shadow shows), the art may run under the frame by up to PAD_MAX_PX (+ EDGE_TOL_PX) - the pad the
    Frame Hard Shadow layer hides - and fails beyond that. The old integer edge search keeps its +-TOL_PX.
    Returns the list of reasons (empty = pass)."""
    names4 = ["top", "right", "bottom", "left"]
    bad = []
    for n, o in zip(names4, offs):
        if not subpixel:
            if abs(o) > TOL_PX:
                bad.append(f"{n} {'art covers the frame by' if o < 0 else 'gap of'} {abs(o):.1f} px")
        elif o > EDGE_TOL_PX:
            bad.append(f"{n} gap of {o:.1f} px between the frame's inner edge and the art (baked paper shows)")
        elif o < -(PAD_MAX_PX + EDGE_TOL_PX):
            bad.append(f"{n} art covers the frame by {-o:.1f} px (pad limit {PAD_MAX_PX:g} px)")
    return bad


# ---------- the checks ----------

def _res(status, reason="", **kw):
    return {"status": status, "reason": reason, **kw}


def check_psd(psd, ratio=None, settings=None, so_px=None, keep=None, manifest=None):
    """Run every check on one PSD. Returns the result dict (status PASS/FAIL, reasons, checks, measured)."""
    from PIL import Image
    psd = Path(psd)
    st0 = psd.stat()
    if manifest is None and (psd.parent / "template.json").is_file():
        try:
            manifest = json.loads((psd.parent / "template.json").read_text())
        except ValueError:
            manifest = None
    res = {"psd": psd.name, "checked": datetime.now().isoformat(timespec="seconds"), "psd_size": st0.st_size,
           "psd_mtime": int(st0.st_mtime), "checks": {}, "measured": {}}
    with tempfile.TemporaryDirectory() as td:
        td = Path(keep) if keep else Path(td)
        td.mkdir(parents=True, exist_ok=True)
        inf = info(psd, settings)
        W, H = int(inf["width"]), int(inf["height"])
        flat = flatten(inf.get("layers"))
        r = roles(flat)
        res["measured"]["canvas"] = [W, H]
        # 8 layers (no render needed)
        names = [l.get("name", "") for l in flat]
        why = []
        if r["art"] is None:
            why.append(f"no '{ART}' smart object")
        for g in ("SHADOWS", "GLARE"):
            if not any(l.get("name", "").strip().upper() == g and l.get("kind") == "Group" for l in flat):
                why.append(f"no {g} group")
        old = [l["name"] for l in flat if l.get("name", "").strip().lower().startswith("old") and not l.get("visible", True)]
        if old:
            why.append("hidden OLD layer(s) for Tony to delete: " + ", ".join(old))
        res["checks"]["layers"] = _res("fail" if why else "pass", "; ".join(why),
                                       overlays=[l["name"] for l in r["overlays"]])
        if r["art"] is None:
            for k in CHECKS[:-1]:
                res["checks"][k] = _res("skip", "no art layer")
            return _finish(res, psd, st0)
        art_id = r["art"]["id"]
        so = so_size(psd, settings, td)                  # always the smart object's NATIVE pixels (the truth)
        res["measured"]["so_px"] = so
        man_so = list(so_px or (manifest or {}).get("so_px") or [])
        if man_so and man_so != so:
            res.setdefault("notes", []).append(f"template.json so_px {man_so[0]}x{man_so[1]} is not the smart object's "
                                               f"native {so[0]}x{so[1]}; the Portal renders with the native size")
        cards = {}
        for nm, v in (("blk", 0), ("wht", 255), ("gry", 128)):
            cards[nm] = td / f"card_{nm}.png"
            Image.new("RGB", tuple(so), (v, v, v)).save(cards[nm])
        fg = [l["id"] for l in r["foreground"] if l["shown"]]
        ov = [l["id"] for l in r["overlays"]]
        bg = render(psd, td / "bg.png", settings, hide=ov + fg, art_hidden=True, art_id=art_id)
        blk = render(psd, td / "blk.png", settings, hide=fg, card=cards["blk"])
        wht = render(psd, td / "wht.png", settings, hide=fg, card=cards["wht"])
        D = (wht - blk).mean(2) > 40
        V = quad_from_mask(D)
        if V is None:
            for k in ("opening", "card", "overlay", "purity", "sun", "ratio", "mat"):
                res["checks"][k] = _res("fail" if k == "opening" else "skip", "the art is not visible in the render")
            return _finish(res, psd, st0)
        res["measured"]["visible_quad"] = np.round(V, 1).tolist()
        Vs = visible_quad_subpixel((wht - blk).mean(2) / 255.0, V)
        res["measured"]["visible_quad_subpx"] = np.round(Vs, 3).tolist()
        # 1 opening: SAM 2 on the BASE-only render (Tony 2026-11-10: SAM everywhere); the old edge search only when
        # SAM is not available, fails, or the template has a mat (art on a flat mat has no window edge to segment)
        sl = side_lengths(V)
        R = int(min(40, max(10, round(0.045 * min(sl)))))
        import cv2
        bgs = cv2.GaussianBlur(bg, (0, 0), 0.8)
        names4 = ["top", "right", "bottom", "left"]
        O_sam, sam_why, sam_wall = (None, "the template has a mat", None) if (r["mats"] or (manifest or {}).get("mode")
                                                                           == "mat") \
            else sam_opening(td / "bg.png", Vs, settings, td, psd)
        if O_sam is not None:
            offs = [round(float(x), 2) for x in side_offsets(Vs, O_sam)]
            found = 4
            res["measured"]["opening_source"] = f"SAM 2 ({sam_why})"
            res["measured"]["opening_quad_sam"] = np.round(O_sam, 3).tolist()
        else:
            res["measured"]["opening_source"] = f"edge search (SAM: {sam_why})"
            offs, found = [], 0
            for i in range(4):
                o, _ = find_edge(bgs, V, i, R)
                offs.append(o)
                found += o is not None
        res["measured"]["opening_offsets"] = {names4[i]: offs[i] for i in range(4)}
        if found < 4:
            missing = [names4[i] for i in range(4) if offs[i] is None]
            if r["mats"] or (manifest or {}).get("mode") == "mat":
                # art laid on a flat mat: the mat window is drawn by the art itself (nothing to misalign)
                res["checks"]["opening"] = _res("skip", "the art sits on a flat mat (no window edge on the " +
                                                ", ".join(missing) + " side); see the mat check")
            else:
                res["checks"]["opening"] = _res("fail", "no frame/opening edge found on the " + ", ".join(missing) +
                                                " side (frameless, or the art covers the whole frame); check by eye")
            O = V
        else:
            O = np.float32(O_sam) if O_sam is not None else offset_quad(V, offs)
            bad = opening_verdict(offs, subpixel=O_sam is not None)
            res["checks"]["opening"] = _res("fail" if bad else "pass", "; ".join(bad),
                                            offsets=[round(float(x), 2) for x in offs])
        res["measured"]["opening_quad"] = np.round(O, 1).tolist()
        x, y = O[:, 0].min(), O[:, 1].min()
        res["measured"]["opening_box"] = [int(round(x)), int(round(y)), int(round(O[:, 0].max() - x)),
                                          int(round(O[:, 1].max() - y))]
        # 2 card test (sub-pixel SAM opening: no gap past 1 px inside it; the art's 1-2 px pad under the frame is
        # allowed, anything beyond PAD_MAX_PX + 1 counts as art over the frame)
        sub = O_sam is not None
        inner = poly_mask(offset_quad(O, -1.0 if sub else -1.5), W, H)
        outer = poly_mask(offset_quad(O, PAD_MAX_PX + 1.0 if sub else 1.5), W, H)
        gap = int((inner & ~D).sum())
        over = int((~outer & D).sum())
        lim = 30 + 0.002 * inner.sum()
        why = []
        if gap > lim:
            why.append(f"{gap} px inside the opening never show art (white sliver / gap)")
        if over > lim:
            why.append(f"{over} px of art outside the opening (art over the frame)")
        res["checks"]["card"] = _res("fail" if why else "pass", "; ".join(why), gap_px=gap, over_px=over)
        # 3 + 4 overlays: each alone over a grey card
        g0 = render(psd, td / "g0.png", settings, hide=ov + fg, card=cards["gry"])
        bg_l = bg @ np.float32([0.299, 0.587, 0.114]) / 255.0
        # outside = beyond both the opening and the art pixels actually shown, plus 3 px (anti-aliasing)
        art_px = cv2.dilate(D.astype("uint8"), np.ones((7, 7), "uint8")).astype(bool)
        out_band = ~(poly_mask(offset_quad(O, 3), W, H) | art_px)
        ins = poly_mask(offset_quad(O, -2), W, H)
        spill, impure, effects = [], [], {}
        for l in r["overlays"]:
            gi = render(psd, td / f"o{l['id']}.png", settings, hide=[x for x in ov if x != l["id"]] + fg,
                        card=cards["gry"])
            diff = np.abs(gi - g0).max(2)
            n_out = int((diff[out_band] > 8).sum())          # 8 levels: below that a spill is not visible
            if n_out > max(300, 0.0005 * W * H):
                why_c = " (clipping mask: photocraft-cli renders ignore clipping; use a layer mask)" if l.get("clipped") else ""
                spill.append(f"'{l['name']}' changes {n_out} px outside the art opening{why_c}")
            dk = (g0 - gi) / np.maximum(g0, 1)                     # darkening share per channel (Multiply-like)
            br = (gi - g0) / np.maximum(255 - g0, 1)               # brightening share (Screen-like)
            tint = dk if dk[ins].mean() >= br[ins].mean() else br
            m = tint.mean(2)
            eff = ins & (m > 0.03)
            effects[l["id"]] = (m, tint, l)
            if eff.sum() < 50:
                if l.get("name") in PHOTO_BUILT and not (manifest or {}).get("layers_verified"):
                    impure.append(f"'{l['name']}' built from photo pixels by the 2026-11-08 script (Directory.md)")
                continue
            chroma = float(np.median((tint.max(2) - tint.min(2))[eff] / np.maximum(m[eff], 1e-3)))
            # copied photo pixels: the shadow's fine detail follows the photo's own fine detail at the same place
            # (grain, paper texture, leftover marks). A blurred black fill does not correlate with the photo.
            hp_m = m - cv2.GaussianBlur(m, (0, 0), 1.0)
            hp_b = bg_l - cv2.GaussianBlur(bg_l, (0, 0), 1.0)
            # away from the opening edges (the frame lip is an edge in both) and only where the photo has grain
            core = eff & poly_mask(offset_quad(O, -max(6.0, 0.02 * min(side_lengths(O)))), W, H) & (np.abs(hp_b) > 1.5 / 255)
            tex = 0.0
            if core.sum() > 200:
                a_, b_ = hp_m[core], hp_b[core]
                den = float(np.std(a_) * np.std(b_))
                tex = abs(float(np.mean((a_ - a_.mean()) * (b_ - b_.mean())) / den)) if den > 1e-9 else 0.0
            reasons = []
            if l.get("name") in PHOTO_BUILT and not (manifest or {}).get("layers_verified"):
                reasons.append("built from photo pixels by the 2026-11-08 script (Directory.md), not a black fill")
            if chroma > 0.2:
                reasons.append(f"coloured ({chroma:.2f}, not a black fill)")
            if tex > 0.35:
                reasons.append(f"copied photo pixels (detail matches the photo, {tex:.2f})")
            if reasons and tint is dk:
                impure.append(f"'{l['name']}' " + " and ".join(reasons))
            elif chroma > 0.35 and tint is br:
                impure.append(f"'{l['name']}' glare is coloured ({chroma:.2f})")
        res["checks"]["overlay"] = _res("fail" if spill else ("pass" if ov else "skip"),
                                        "; ".join(spill) if spill else ("" if ov else "no shadow/glare layers"))
        res["checks"]["purity"] = _res("fail" if impure else ("pass" if ov else "skip"),
                                       "; ".join(impure) if impure else ("" if ov else "no shadow/glare layers"))
        # 5 sun angle. Tony 2026-11-15: a sun line is trusted ONLY on SAM's wall mask (the band search took a plant
        # leaf for the sun and passed an invented diagonal shadow it had itself caused); a straight light/shade edge
        # on the art with no sun line confirmed on the wall FAILS, and no light shadow may lie over a print
        from . import sam_frames as sf
        by_hand = any(n in str(psd) for n in sf.NOT_ON)       # sun line verified by hand (Wabi bedroom, 2026-11-10)
        sun = sun_line(bg, O, wall=sam_wall) if sam_wall is not None or by_hand else None
        res["measured"]["sun"] = sun
        res["measured"]["sun_searched_on"] = ("SAM wall mask" if sam_wall is not None else
                                              "band around the frame (verified by hand)" if by_hand else
                                              "not searched (no SAM wall mask)")
        edges = []
        for lid, (m, tint, l) in effects.items():
            if l.get("blend") == "Screen":
                continue
            e = overlay_edge(m, ins)
            if e:
                edges.append((l["name"], e))
        res["measured"]["shadow_edges"] = {n: e for n, e in edges}
        tex = insert_texture(bg, O)
        res["measured"]["insert_texture"] = round(tex, 4)
        from .scene_templates import INSERT_TEXTURE_MAX
        light_over_print = []
        if tex > INSERT_TEXTURE_MAX and not sun and not r["mats"]:   # the photo still shows a print in the frame and no
            # sun line on the wall explains a light shadow there (a confirmed wall sun line is compared below)
            for lid, (m, tint, l) in effects.items():
                low_n = l.get("name", "").lower()
                if l.get("blend") == "Screen" or "frame" in low_n or "edge" in low_n or "hard" in low_n:
                    continue
                if ins.any() and float((m[ins] > 0.03).mean()) > 0.2:
                    light_over_print.append(l["name"])
        if light_over_print:
            res["checks"]["sun"] = _res("fail", "light shadow over the art where the photo shows a print (its light "
                                                "cannot be measured): " + ", ".join(f"'{n}'" for n in light_over_print))
        elif not sun:
            if edges:
                n, e = edges[0]
                res["checks"]["sun"] = _res("fail", f"'{n}' draws a straight light/shade edge ({e['deg']:.0f} deg) "
                                                    "across the art but no sun line is confirmed on the wall"
                                                    + ("" if sam_wall is not None else " (no SAM wall mask)"))
            else:
                res["checks"]["sun"] = _res("skip", "no sun line on the wall near the frame")
        else:
            if not edges:
                res["checks"]["sun"] = _res("skip", f"wall sun line {sun['deg']:.0f} deg; no shadow layer has a "
                                                    "straight light edge to compare (soft or no light-source shadow)")
            else:
                n, e = min(edges, key=lambda x: abs(x[1]["deg"] - sun["deg"]))
                d = abs(e["deg"] - sun["deg"])
                res["checks"]["sun"] = _res("fail" if d > TOL_DEG else "pass",
                                            (f"'{n}' edge {e['deg']:.0f} deg vs wall sun line {sun['deg']:.0f} deg "
                                             f"({d:.0f} deg off)") if d > TOL_DEG else "",
                                            wall_deg=sun["deg"], shadow_deg=e["deg"])
        # placement: wall molding / wainscoting around the frame (no molding = pass)
        try:
            pl = placement(bg, V)
            res["measured"]["placement"] = pl
            ok = next((why for k, why in PLACEMENT_OK.items() if k in str(psd)), None)
            if pl["flag"] and ok:
                res["checks"]["placement"] = _res("pass", "", accepted=ok, flag=pl["flag"])
            else:
                res["checks"]["placement"] = _res("fail" if pl["flag"] else "pass", "; ".join(pl["flag"]))
        except Exception as e:  # noqa: BLE001  (never blocks the other checks)
            res["checks"]["placement"] = _res("skip", f"could not measure ({str(e)[:120]})")
        # 6 ratio
        asp = true_aspect(O, (W, H))
        res["measured"]["opening_ratio"] = round(asp, 4)
        why = []
        if ratio in RATIO_TARGETS:
            tgt = min(RATIO_TARGETS[ratio], key=lambda t: abs(asp / t - 1))
            off = asp / tgt - 1
            if abs(off) > TOL_RATIO:
                why.append(f"opening ratio {asp:.3f} is {off:+.1%} off {ratio} ({tgt:.3f}); the crop limit is 3%")
        vis = true_aspect(V, (W, H))
        stretch = (so[0] / so[1]) / vis - 1
        res["measured"]["so_ratio"] = round(so[0] / so[1], 4)
        res["measured"]["visible_ratio"] = round(vis, 4)
        if abs(stretch) > TOL_RATIO and not r["mats"]:
            why.append(f"the smart object ({so[0]}x{so[1]}) is stretched {stretch:+.1%} to its frame")
        res["checks"]["ratio"] = _res("fail" if why else "pass", "; ".join(why))
        # 7 mat
        if not r["mats"] and (manifest or {}).get("mode") != "mat":
            res["checks"]["mat"] = _res("skip", "no mat")
        else:
            widths = []
            for i in range(4):
                o2, _ = find_edge(bgs, O, i, int(0.3 * min(side_lengths(O))) + 4, prefer="next", start=0)
                widths.append(o2)
            names_m = ", ".join(l["name"] for l in r["mats"])
            bevel = any(any(w in l.get("name", "").lower() for w in ("bevel", "shadow")) and
                        any(w in " ".join([l.get("name", "")] + l["parents"]).lower() for w in ("mat", "matte", "bevel"))
                        for l in flat)
            why = []
            if any(w is None for w in widths):
                why.append("mat outer edge not found on every side")
            else:
                ls = side_lengths(O)
                a = asp
                norm = [widths[0] / ls[0] * a, widths[1] / ls[1], widths[2] / ls[2] * a, widths[3] / ls[3]]
                mean = sum(norm) / 4
                spread = (max(norm) - min(norm)) / max(mean, 1e-6)
                res["measured"]["mat_widths_px"] = [round(float(w), 1) for w in widths]
                if spread > 0.2:
                    why.append("mat width not uniform (" + ", ".join(f"{n} {w:.0f}px" for n, w in zip(names4, widths)) + ")")
            if not bevel:
                why.append("no mat bevel/shadow layer")
            res["checks"]["mat"] = _res("fail" if why else "pass", "; ".join(why), layers=names_m)
    return _finish(res, psd, st0)


def _finish(res, psd, st0):
    st1 = Path(psd).stat()
    if (st1.st_size, st1.st_mtime_ns) != (st0.st_size, st0.st_mtime_ns):
        res["checks"]["layers"] = _res("fail", "THE PSD CHANGED DURING THE CHECK (it must stay read-only)")
    for k in CHECKS:
        res["checks"].setdefault(k, _res("skip", ""))
    fails = [f"{LABELS[k]}: {v['reason']}" for k, v in res["checks"].items() if v["status"] == "fail"]
    res["status"] = "FAIL" if fails else "PASS"
    res["reasons"] = fails
    return res


# ---------- library ----------

def load(path=None):
    p = Path(path or RESULTS)
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError):
        return {"results": {}}


def save(data, path=None):
    p = Path(path or RESULTS)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=1) + "\n")
    tmp.replace(p)


def status_for(rel, data=None, psd=None):
    """The stored result for a template (None when never checked or the PSD changed since)."""
    r = (data or load()).get("results", {}).get(rel)
    if not r:
        return None
    if psd is not None:
        st = Path(psd).stat()
        if st.st_size != r.get("psd_size") or int(st.st_mtime) != r.get("psd_mtime"):
            return dict(r, stale=True)
    return r


def templates(settings=None, wired=False):
    from .scene_templates import load_manifest
    from .template_gallery import scan
    return [dict(t, manifest=load_manifest(t["psd"])) for t in scan(settings)[0] if wired or not t.get("wired")]


def check_template(t, settings=None):
    m = t.get("manifest") or {}
    return check_psd(t["psd"], t["ratio"], settings, so_px=m.get("so_px"), manifest=m)


def run_all(settings=None, rels=None, path=None, log=print):
    data = load(path)
    data.setdefault("results", {})
    ts = [t for t in templates(settings) if not rels or t["rel"] in rels]
    with _job_lock:
        _job.update(running=True, done=0, total=len(ts), current="", error="")
    try:
        for t in ts:
            with _job_lock:
                _job["current"] = t["rel"]
            try:
                r = check_template(t, settings)
            except Exception as e:  # noqa: BLE001  (one bad PSD never stops the rest)
                r = {"psd": t["psd"].name, "status": "FAIL", "reasons": [f"checker error: {str(e)[:200]}"],
                     "checks": {}, "checked": datetime.now().isoformat(timespec="seconds")}
            r["rel"] = t["rel"]
            data["results"][t["rel"]] = r
            data["updated"] = datetime.now().isoformat(timespec="seconds")
            save(data, path)
            log(f"{r['status']}  {t['rel']}" + ("" if r["status"] == "PASS" else "\n      " + "\n      ".join(r["reasons"])))
            with _job_lock:
                _job["done"] += 1
    finally:
        with _job_lock:
            _job.update(running=False, current="")
    return data


def job():
    with _job_lock:
        return dict(_job)


def start(settings=None, rels=None):
    with _job_lock:
        if _job["running"]:
            return False
        _job["running"] = True
    threading.Thread(target=run_all, args=(settings, rels, None, lambda *_: None), daemon=True).start()
    return True


if __name__ == "__main__":
    import sys
    from .db import load_config
    s = load_config("settings")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--fails" in sys.argv:
        d = load()
        fails = {k: v for k, v in d.get("results", {}).items() if v.get("status") != "PASS"}
        print(f"{len(fails)} FAIL of {len(d.get('results', {}))}")
        for k, v in sorted(fails.items()):
            print(k)
            for x in v.get("reasons", []):
                print("   ", x)
    elif "--all" in sys.argv or args:
        d = run_all(s, args or None)
        res = d["results"]
        n = sum(1 for v in res.values() if v.get("status") == "PASS")
        print(f"{n} PASS, {len(res) - n} FAIL")
    else:
        print(__doc__)
