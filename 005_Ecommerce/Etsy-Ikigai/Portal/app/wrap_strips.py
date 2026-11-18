"""Wrap strips for gallery-wrapped CANVAS templates (Tony 2026-11-17: "mockups must look real").

On a real gallery-wrapped canvas the print wraps around the stretcher, so the side the camera sees shows the art's
colours turning the corner. The face art stays exactly as before (cover-fit, cropped, unchanged); past each
camera-facing face edge a narrow WRAP STRIP is added:

  1. band: the outer DEPTH_FRAC of the fitted art (about 1.5 in on a 30 in canvas) MIRRORED across the edge (a mirror
     wrap: the strip continues the face edge's own pixels and runs inward from there). The visible strip is only
     ~10-20 px wide at 2400 px, so exact depth fidelity is not needed.
  2. shape: measured from the scene's own pixels, independent of SAM (the same perpendicular Lab profiles as
     template_checker.edge_profile): per side, from the art edge (= the face edge, checked by the checker's edge
     check) outward, the run of canvas-side colour (the face pigment, as saturated or more, or a white side) and then
     the far edge = the hard step where the side meets the gap / wood lip (sub-pixel 50% point). A side whose run is
     narrower than MIN_W px is not camera-facing and gets no strip. The far edge is a straight line fitted over 8
     segments; each visible side's 4 corners: [face start, far start, far end, face end]. At a corner where two
     visible sides meet, both strips end on the line from the face corner to the two far lines' intersection (the
     box edge); a free end follows the neighbouring face side's line and gets a small rounded corner (the canvas
     fold). Stored in template.json "wrap_strips" when the template is built or rebuilt.
  3. light: the photo's own LUMINANCE on the side (light near the face, dark at the back), divided by the face's
     luminance next to it = the shading ratio in linear light, stored as a coarse grid (NV along x NU across) and
     multiplied over the warped band. Luminance only: the old orange / brown side colour never leaks into the art.
  4. PSD: a neutral grey placeholder layer LAYER (black/grey pixels shaded like the side, cut to the strip shapes,
     above the BASE, below the art and the SHADOWS group) so Tony sees the strip positions in PhotoCraft. The checker
     hides it on its base render; the Portal hides it in every render and composites the real strip instead.
  5. render (scene_templates.render_psd): only when the manifest has "wrap_strips" with sides; every other template
     renders exactly as before. Composite: out = render + alpha * (strip - base photo), with the strip polygon's
     anti-aliased coverage, so the seam at the face edge never lets photo pixels through.
"""
import json
import math
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

import numpy as np

SIDES = ("top", "right", "bottom", "left")
LAYER = "Wrap Strip (placeholder)"
VERSION = 1
DEPTH_FRAC = 0.05        # the wrapped band = 5% of the art's long side (1.5 in on a 30 in canvas, Tony: 1-2 in)
MIN_W = 3.0              # px: a narrower side run is not a camera-facing side
SIDE_HUE_DEG = 35.0      # canvas side = the face pigment: hue within this, chroma at least the face's
WHITE_C = 0.35           # or a white side: chroma below this share of the face's, lightness above half the face's
SHADED_C = 0.6          # the side's back in shadow: chroma at least this share of the face's (a neutral gap is not)
FAR_STEP_MIN = 8.0       # Lab dE over 1.5 px: the far edge (side -> gap / wood lip) must be a hard step
SEGMENTS = 8
MIN_SEG_SHARE = 0.6
CORNER_R = 2.0           # px: the rounded canvas fold at a strip's free outer corner
NU, NV = 12, 24          # shading grid: across x along
PLACEHOLDER_GREY = 0.42  # linear albedo of the neutral placeholder strip
W709 = np.float32([0.2126, 0.7152, 0.0722])


def lin(x):
    x = np.asarray(x, "float32")
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4).astype("float32")


def enc(x):
    x = np.clip(np.asarray(x, "float32"), 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * x ** (1 / 2.4) - 0.055).astype("float32")


# ---------- geometry ----------

def _side(q, s):
    """Side s of quad q: (start corner, end corner, outward unit normal)."""
    from .template_checker import _outward
    return _outward(np.float32(q), s)


def _intersect(p, r, s, u):
    """Intersection of line p + t r and line s + k u (None when parallel)."""
    cr = r[0] * u[1] - r[1] * u[0]
    if abs(cr) < 1e-9:
        return None
    t = ((s - p)[0] * u[1] - (s - p)[1] * u[0]) / cr
    return np.float32(p + r * t)


def strip_quads(q, far):
    """Per visible side: [face start, far start, far end, face end]. `far` = {side index: (F0, F1)} = the far edge's
    outward offset (px) at the side's start and end corners."""
    q = np.float32(q)
    lines = {}
    for s in range(4):
        a, b, n = _side(q, s)
        lines[s] = (a, b, n)
    far_line = {}
    for s, (f0, f1) in far.items():
        a, b, n = lines[s]
        p0, p1 = a + n * f0, b + n * f1
        far_line[s] = (p0, p1 - p0)
    out = {}
    for s in far:
        a, b, n = lines[s]
        p, r = far_line[s]
        ends = []
        for adj, corner in (((s - 1) % 4, a), ((s + 1) % 4, b)):
            if adj in far_line:                               # two visible sides meet: the box edge
                x = _intersect(p, r, *far_line[adj])
            else:                                             # free end: the neighbouring face side, extended
                a2, b2, _ = lines[adj]
                x = _intersect(p, r, a2, b2 - a2)
            if x is None or float(np.linalg.norm(x - corner)) > 4 * max(abs(far[s][0]), abs(far[s][1]), 1.0) + 4:
                x = np.float32(corner + n * (far[s][0] if corner is a else far[s][1]))
            ends.append(x)
        out[SIDES[s]] = np.float32([a, ends[0], ends[1], b])
    return out


def rounded_polygon(quad, round_idx, r=CORNER_R, k=6):
    """The quad as a polygon with the corners in `round_idx` rounded (quadratic Bezier, radius ~r px)."""
    quad = np.float32(quad)
    pts = []
    for i in range(4):
        P = quad[i]
        if i not in round_idx:
            pts.append(P)
            continue
        A, B = quad[(i - 1) % 4], quad[(i + 1) % 4]
        la, lb = float(np.linalg.norm(A - P)), float(np.linalg.norm(B - P))
        ra = min(r, 0.45 * la, 0.45 * lb)
        if ra <= 0.05:
            pts.append(P)
            continue
        p0, p2 = P + (A - P) / la * ra, P + (B - P) / lb * ra
        for t in np.linspace(0, 1, k):
            pts.append((1 - t) ** 2 * p0 + 2 * (1 - t) * t * P + t ** 2 * p2)
    return np.float32(pts)


# ---------- measuring a template ----------

def _lch(c):
    return float(c[0]), float(np.hypot(c[1], c[2])), math.degrees(math.atan2(c[2], c[1]))


def side_colour(prof, face, shaded=False):
    """Per profile sample: is it canvas side (the face pigment at least as saturated, or a white side)? shaded: the
    looser test for the side's back in deep shadow (the pigment's hue, chroma >= SHADED_C x the face's, darker)."""
    Lf, Cf, hf = _lch(face)
    ok = np.zeros(len(prof), bool)
    for i, c in enumerate(prof):
        L, C, h = _lch(c)
        dh = abs((h - hf + 180) % 360 - 180)
        if shaded:
            ok[i] = dh < SIDE_HUE_DEG and C >= SHADED_C * Cf and L < Lf - 4
        else:
            ok[i] = (C >= Cf and dh < SIDE_HUE_DEG and L > 3) or (C < WHITE_C * max(Cf, 1.0) and L > 0.5 * Lf)
    return ok


def far_edge_1d(prof, offs, face):
    """One profile (outward offsets, 0 = the face/art edge). Returns (far edge offset or None, side-colour run px)."""
    from .template_checker import _half_cross
    ok = side_colour(prof, face)
    start = np.nonzero((offs >= 0) & (offs <= 2.0) & ok)[0]
    if not len(start):
        return None, 0.0
    i = start[0]
    while i + 1 < len(offs) and ok[i + 1]:
        i += 1
    run = float(offs[i])
    if run < MIN_W:
        return None, run
    # the side's back in deep shadow (pre-white-side scenes: orange fading to brown) is still the side: extend
    # through it, by at most the run's own width (never into a warm wood lip)
    sh = side_colour(prof, face, shaded=True)
    while i + 1 < len(offs) and sh[i + 1] and offs[i + 1] <= 2 * run:
        i += 1
    run_end = float(offs[i])
    reach = max(6.0, 0.75 * run)
    win = np.nonzero((offs >= run_end - 1.0) & (offs <= run_end + reach))[0]
    at = lambda o: np.array([np.interp(o, offs, prof[:, k]) for k in range(3)])
    st = np.float32([np.linalg.norm(at(offs[j] + 0.75) - at(offs[j] - 0.75)) for j in win])
    # the FIRST hard step past the side colour (a local peak): the side's back edge (a neutral gap behind it is not
    # part of the side; a shaded side running straight into the wood lip ends at the lip)
    peaks = [k for k in range(len(st)) if st[k] >= FAR_STEP_MIN and st[k] >= st[max(k - 1, 0)]
             and st[k] >= st[min(k + 1, len(st) - 1)]]
    if not peaks:
        return run_end, run
    return _half_cross(prof, offs, float(offs[win[peaks[0]]])), run


def measure_sides(rgb, art_q):
    """Which sides show the canvas side, and where each one's far edge runs. Returns ({side index: (F0, F1)},
    {side name: info})."""
    from .template_checker import _lab, edge_profile
    q = np.float32(art_q)
    lab = _lab(np.float32(rgb))
    size = min(float(np.linalg.norm(q[1] - q[0])), float(np.linalg.norm(q[3] - q[0])))
    R = float(np.clip(0.06 * size, 24.0, 60.0))
    offs = np.arange(-8.0, R + 1e-6, 0.25, dtype="float32")
    plateau = (offs >= -8.0) & (offs <= -3.0)
    edges = np.linspace(0.08, 0.92, SEGMENTS + 1)
    far, info = {}, {}
    for s in range(4):
        ts, Fs, runs, skipped = [], [], [], 0
        for t0, t1 in zip(edges[:-1], edges[1:]):
            prof = edge_profile(lab, q, s, offs, float(t0), float(t1), n=40)
            face = np.median(prof[plateau], 0)
            if float(np.percentile(np.linalg.norm(prof[plateau] - face, axis=1), 90)) > 4.0:
                skipped += 1                                  # a prop or a print in front: not the plain face
                continue
            F, run = far_edge_1d(prof, offs, face)
            runs.append(run)
            if F is not None:
                ts.append(0.5 * (t0 + t1))
                Fs.append(F)
        st = {"segments": len(Fs), "side_run_px": round(float(np.median(runs)), 2) if runs else 0.0}
        if len(Fs) < MIN_SEG_SHARE * SEGMENTS or st["side_run_px"] < MIN_W:
            st["visible"] = False
            info[SIDES[s]] = st
            continue
        ts, Fs = np.float32(ts), np.float32(Fs)
        keep = np.ones(len(Fs), bool)
        for _ in range(2):
            c = np.polyfit(ts[keep], Fs[keep], 1)
            res = np.abs(np.polyval(c, ts) - Fs)
            new = res <= max(1.5, 2.5 * float(np.median(res[keep])))
            if new.sum() < 3 or (new == keep).all():
                break
            keep = new
        F0, F1 = float(np.polyval(c, 0.0)), float(np.polyval(c, 1.0))
        st.update(visible=True, far_px=[round(F0, 2), round(F1, 2)], segments_px=[round(float(f), 2) for f in Fs],
                  fit_rms_px=round(float(np.sqrt(np.mean((np.polyval(c, ts[keep]) - Fs[keep]) ** 2))), 3))
        far[s] = (F0, F1)
        info[SIDES[s]] = st
    return far, info


def _rect_h(quad, w, h):
    """Homography from a w x h rectangle (pixel-edge coordinates) onto `quad` (pixel-edge coordinates), in the
    pixel-centre convention cv2 uses."""
    import cv2
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]]) - 0.5
    return cv2.getPerspectiveTransform(src, np.float32(quad) - 0.5)


def shading(rgb, quad, art_q, s):
    """The photo's own shading on one side strip: its linear luminance / the face's next to it (luminance only, never
    the photo's colour), median per along-bin. Returns an NV x NU grid (rows = along the side, cols = face -> back)."""
    import cv2
    Y = lin(np.float32(rgb) / 255.0) @ W709
    quad = np.float32(quad)
    width = max(float(np.linalg.norm(quad[1] - quad[0])), float(np.linalg.norm(quad[2] - quad[3])))
    length = float(np.linalg.norm(quad[3] - quad[0]))
    su = 4                                                     # 4 samples per px across
    nu, nv = max(8, int(math.ceil(width * su))), max(NV * 4, int(math.ceil(length)))
    Hm = _rect_h(quad, nu, nv)
    rect = cv2.warpPerspective(Y, np.linalg.inv(Hm), (nu, nv), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    # the face next to the strip: 3..6 px inside the face edge, at the same place along the side
    a, b, n = _side(np.float32(art_q), s)
    tv = (np.arange(nv, dtype="float32") + 0.5) / nv
    P = (a + (b - a) * tv[:, None])[:, None, :] - n[None, None, :] * np.float32([3, 4, 5, 6])[None, :, None]
    fy = cv2.remap(Y, (P[..., 0] - 0.5).astype("float32"), (P[..., 1] - 0.5).astype("float32"), cv2.INTER_LINEAR,
                   borderMode=cv2.BORDER_REPLICATE)
    face = np.median(fy, 1)
    face = cv2.GaussianBlur(face[:, None], (0, 0), max(2.0, nv / 60))[:, 0]
    ratio = rect / np.maximum(face[:, None], 1e-4)
    # drop the samples within 0.5 px of the face edge and 0.9 px of the far edge (mixed pixels), stretch the rest
    lo, hi = int(round(0.5 * su)), nu - int(round(0.9 * su))
    if hi - lo >= 2:
        ratio = ratio[:, lo:hi]
    cols = cv2.resize(ratio, (NU, ratio.shape[0]), interpolation=cv2.INTER_AREA)
    rows = np.array_split(np.arange(cols.shape[0]), NV)
    grid = np.stack([np.median(cols[r], 0) for r in rows])
    return np.clip(grid, 0.0, 1.5).astype("float32")


def measure(rgb, art_q, presentation="canvas", depth_frac=DEPTH_FRAC):
    """The template.json 'wrap_strips' entry for a scene (RGB uint8/float 0..255) and its art quad, or None when the
    template is not a canvas or no side is camera-facing."""
    if presentation != "canvas":
        return None
    q = np.float32(art_q)
    far, info = measure_sides(rgb, q)
    if not far:
        return None
    quads = strip_quads(q, far)
    sides = {}
    for s, (F0, F1) in far.items():
        nm = SIDES[s]
        quad = quads[nm]
        g = shading(rgb, quad, q, s)
        free = [i for i, adj in ((1, (s - 1) % 4), (2, (s + 1) % 4)) if adj not in far]
        sides[nm] = {"quad": np.round(quad, 3).tolist(), "far_px": info[nm]["far_px"],
                     "width_px": [round(float(np.linalg.norm(quad[1] - quad[0])), 2),
                                  round(float(np.linalg.norm(quad[2] - quad[3])), 2)],
                     "round_corners": free, "segments_px": info[nm]["segments_px"],
                     "fit_rms_px": info[nm]["fit_rms_px"], "shade": np.round(g, 3).tolist(),
                     "shade_face_to_back": [round(float(g[:, 0].mean()), 3), round(float(g[:, -1].mean()), 3)]}
    return {"version": VERSION, "depth_frac": depth_frac, "corner_radius_px": CORNER_R, "layer": LAYER,
            "art_quad": np.round(q, 3).tolist(), "sides": sides,
            "not_shown": {k: v for k, v in info.items() if not v.get("visible")},
            "method": "art edge -> canvas-side colour run -> hard step to the gap / wood lip (scene Lab profiles, 8 "
                      "segments, straight line); shading = photo luminance / face luminance (linear, no colour)",
            "measured": datetime.now().isoformat(timespec="seconds")}


# ---------- rendering ----------

def band_source(art, side, d):
    """The outer d px of the art at `side`, mirrored across the edge: rows = along the side (start -> end corner of
    the art quad side), cols = from the edge inward (col 0 = the edge's own pixels)."""
    a = np.asarray(art)
    if side == "right":
        return a[:, ::-1][:, :d]
    if side == "left":
        return a[::-1, :d]
    if side == "top":
        return a[:d, :].transpose(1, 0, *range(2, a.ndim))
    if side == "bottom":
        return a[::-1, ::-1][:d, :].transpose(1, 0, *range(2, a.ndim))
    raise ValueError(side)


def coverage(poly, W, H, box=None, ss=8):
    """Anti-aliased area coverage (0..1) of a CONVEX polygon: ss x ss sample centres per pixel tested against every
    side's half-plane. Unlike a fillPoly raster (which counts a boundary sub-sample on some edges) two polygons that
    share an edge get complementary coverage there, so a strip and the art meet without a gap or an overlap. `box`
    (x0, y0, x1, y1) limits the work; zero elsewhere."""
    poly = np.float64(poly)
    out = np.zeros((H, W), "float32")
    x0, y0 = max(0, int(math.floor(poly[:, 0].min())) - 1), max(0, int(math.floor(poly[:, 1].min())) - 1)
    x1, y1 = min(W, int(math.ceil(poly[:, 0].max())) + 2), min(H, int(math.ceil(poly[:, 1].max())) + 2)
    if box is not None:
        x0, y0, x1, y1 = max(x0, box[0]), max(y0, box[1]), min(x1, box[2]), min(y1, box[3])
    if x1 <= x0 or y1 <= y0:
        return out
    sub = (np.arange(ss) + 0.5) / ss
    xs = (np.arange(x0, x1)[:, None] + sub[None, :]).ravel()
    ys = (np.arange(y0, y1)[:, None] + sub[None, :]).ravel()
    X, Y = np.meshgrid(xs, ys)
    area = float(np.sum(poly[:, 0] * np.roll(poly[:, 1], -1) - np.roll(poly[:, 0], -1) * poly[:, 1]))
    sgn = 1.0 if area > 0 else -1.0
    inside = np.ones(X.shape, bool)
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        if np.allclose(a, b):
            continue
        inside &= sgn * ((b[0] - a[0]) * (Y - a[1]) - (b[1] - a[1]) * (X - a[0])) > 0
    out[y0:y1, x0:x1] = inside.reshape(y1 - y0, ss, x1 - x0, ss).mean((1, 3))
    return out


def strip_layer(ws, W, H, art=None):
    """Full-canvas linear RGB + alpha of every strip: the mirrored band of `art` (fitted to the smart object, RGB
    0..255) times the measured shading; with art None the neutral grey placeholder. Returns (rgb_lin, alpha)."""
    import cv2
    rgb = np.zeros((H, W, 3), "float32")
    alpha = np.zeros((H, W), "float32")
    if art is not None:
        art_l = lin(np.asarray(art, "float32")[..., :3] / 255.0)
        d = max(2, int(round(float(ws.get("depth_frac", DEPTH_FRAC)) * max(art_l.shape[:2]))))
    for nm, sd in (ws.get("sides") or {}).items():
        quad = np.float32(sd["quad"])
        wmax = max(sd["width_px"]) if sd.get("width_px") else 8.0
        L = int(math.ceil(max(float(np.linalg.norm(quad[3] - quad[0])), 4)))
        tw = max(4, int(math.ceil(wmax * 3)))
        if art is not None:
            band = band_source(art_l, nm, min(d, art_l.shape[1] if nm in ("right", "left") else art_l.shape[0]))
            band = cv2.resize(np.ascontiguousarray(band), (tw, band.shape[0]), interpolation=cv2.INTER_AREA)
            band = cv2.resize(band, (tw, L), interpolation=cv2.INTER_AREA if band.shape[0] > L else cv2.INTER_LINEAR)
        else:
            band = np.full((L, tw, 3), PLACEHOLDER_GREY, "float32")
        g = np.float32(sd["shade"])
        sh = cv2.resize(g, (tw, L), interpolation=cv2.INTER_LINEAR)
        img = band * sh[..., None]
        x0, y0 = max(0, int(math.floor(quad[:, 0].min())) - 2), max(0, int(math.floor(quad[:, 1].min())) - 2)
        x1, y1 = min(W, int(math.ceil(quad[:, 0].max())) + 3), min(H, int(math.ceil(quad[:, 1].max())) + 3)
        if x1 <= x0 or y1 <= y0:
            continue
        Hm = _rect_h(quad - np.float32([x0, y0]), tw, L)
        warped = cv2.warpPerspective(img, Hm, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR,
                                     borderMode=cv2.BORDER_REPLICATE)
        poly = rounded_polygon(quad, sd.get("round_corners", []), float(ws.get("corner_radius_px", CORNER_R)))
        a = coverage(poly, W, H)[y0:y1, x0:x1]
        # strips tile (two visible sides share the box edge): accumulate coverage-weighted
        rgb[y0:y1, x0:x1] += warped * a[..., None]
        alpha[y0:y1, x0:x1] += a
    a = np.clip(alpha, 0, 1)
    rgb = np.where(alpha[..., None] > 1e-6, rgb / np.maximum(alpha[..., None], 1e-6), 0) * a[..., None]
    return rgb, a


def has_strips(manifest):
    return bool(((manifest or {}).get("wrap_strips") or {}).get("sides"))


def composite(render_rgb, base_rgb, fitted_art, ws, art_q=None):
    """The render (uint8 / float 0..255, the PSD rendered with the placeholder strip layer HIDDEN) with the wrap
    strips laid over the side edges. out = render + alpha * (strip - base photo): the strip replaces exactly the
    photo's share of each pixel, so the face art is untouched and the seam lets no photo through. On the seam pixels
    alpha is capped at 1 - the art quad's own coverage (`art_q`, else ws["art_quad"]), so the two never overlap (an
    overlap darkened the seam into a 1 px line). Returns uint8."""
    R = np.asarray(render_rgb, "float32")[..., :3] / 255.0
    B = np.asarray(base_rgb, "float32")[..., :3] / 255.0
    H, W = R.shape[:2]
    s_lin, a = strip_layer(ws, W, H, fitted_art)
    S = enc(np.where(a[..., None] > 1e-6, s_lin / np.maximum(a[..., None], 1e-6), 0))
    aq = art_q if art_q is not None else ws.get("art_quad")
    if aq is not None:
        ys_, xs_ = np.nonzero(a > 0)
        if len(xs_):
            box = (int(xs_.min()), int(ys_.min()), int(xs_.max()) + 1, int(ys_.max()) + 1)
            a = np.minimum(a, 1.0 - coverage(aq, W, H, box))
    out = R + a[..., None] * (S - B)
    return np.uint8(np.clip(np.round(out * 255), 0, 255))


def placeholder_png(ws, W, H, path):
    """The neutral grey placeholder layer for the PSD (RGBA, full canvas)."""
    from PIL import Image
    s_lin, a = strip_layer(ws, W, H, None)
    rgb = enc(np.where(a[..., None] > 1e-6, s_lin / np.maximum(a[..., None], 1e-6), 0))
    rgba = np.dstack([np.round(rgb * 255), np.round(a * 255)]).astype("uint8")
    Image.fromarray(rgba, "RGBA").save(path)
    return Path(path)


# ---------- adding strips to an existing template ----------

def _free_name(folder, name):
    p = Path(folder) / name
    k = 2
    while p.exists():
        p = Path(folder) / f"{Path(name).stem}_{k}{Path(name).suffix}"
        k += 1
    return p


def add_to_template(tdir, settings=None, run=None, log=print):
    """Measure the wrap strips of a canvas template (from its scene PNG), back the PSD and template.json up into the
    folder's existing Archive, bake the placeholder layer into the PSD (above the BASE) and write "wrap_strips" to
    template.json. The smart object is not touched (so_px unchanged). Returns the wrap_strips entry (None when the
    template is not a canvas or shows no side)."""
    from PIL import Image
    from . import scene_templates as stp
    from . import template_checker as tc
    tdir = Path(tdir)
    mf = tdir / stp.MANIFEST
    man = json.loads(mf.read_text())
    psd = tdir / man["psd"]
    rgb = np.asarray(Image.open(tdir / man["scene"]).convert("RGB"))
    pres = tc.presentation_of(man)
    ws = measure(rgb, man["quad_art"], pres)
    if not ws:
        log(f"no wrap strips: {pres} template or no camera-facing canvas side")
        return None
    arch = tdir / "Archive"
    if not arch.is_dir():
        raise stp.TemplateError(f"{arch} is missing (agents never create folders; Tony makes Archive folders)")
    stamp = datetime.now().strftime("%Y%m%d")
    names = [l.get("name") for l in tc.flatten(tc.info(psd, settings).get("layers"))]
    backups = []
    if LAYER not in names:
        b_psd = _free_name(arch, f"{psd.stem}_before_wrap_strips_{stamp}.psd")
        shutil.copy2(psd, b_psd)
        backups.append(f"Archive/{b_psd.name}")
    b_js = _free_name(arch, f"template_before_wrap_strips_{stamp}.json")
    shutil.copy2(mf, b_js)
    backups.append(f"Archive/{b_js.name}")
    if LAYER not in names:
        H, W = rgb.shape[:2]
        run = run or stp._run
        with tempfile.TemporaryDirectory() as td:
            png = placeholder_png(ws, W, H, Path(td) / "L_wrap.png")
            out = Path(td) / "with_strips.psd"
            run(settings, ["run", str(psd), *stp._cmd("layer.select", {"name": stp.BASE_NAME}),
                           *stp._cmd("file.placeEmbedded", {"path": str(png.resolve()), "smartObject": False,
                                                            "scale": 100}),
                           *stp._cmd("layer.setProps", {"name": LAYER, "blend": "Normal", "opacity": 1.0,
                                                        "visible": True}),
                           "--out", str(out)])
            if not out.is_file():
                raise stp.TemplateError("the PSD with the wrap strip layer was not written")
            shutil.copyfile(out, psd)
        psd.touch()                                   # new mtime: the gallery's thumbnail cache refreshes
    else:                   # re-measured: the PSD keeps its placeholder layer (a guide only; renders hide it)
        log("the PSD already has the wrap strip layer: only template.json is refreshed")
    backups = list((man.get("wrap_strips_added") or {}).get("backups") or []) + backups
    man["wrap_strips"] = ws
    man["wrap_strips_added"] = {"when": datetime.now().isoformat(timespec="seconds"), "backups": backups,
                                "why": "gallery-wrap side strips (Tony 2026-11-17: mockups must look real)",
                                "credits": 0}
    mf.write_text(json.dumps(man, indent=1) + "\n")
    log(f"wrap strips: {', '.join(ws['sides'])}; backups {', '.join(backups)}")
    return ws


if __name__ == "__main__":
    import sys
    from .db import load_config
    for t in sys.argv[1:]:
        add_to_template(t, load_config("settings"))
