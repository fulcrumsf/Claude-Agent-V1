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
     2026-11-18 (a PLAIN canvas hung on the wall, white sides, pale wall): the side band starts past the face end and
     ends at its first HARD step (a white side and a pale wall pass the same colour test, so the colour run alone
     ran over the wall); the far edge must be one straight line; never two opposite sides; a free end follows its
     MEASURED end edge (the side is a trapezoid in perspective) when that lies inside the neighbouring face line;
     a white side's shading keeps the photo's pattern with its brightest part = the face (white paint is not light);
     sides are detected on the uncorrected SAM quad and attached to the edge-check-corrected art edge (art_offsets);
     unseen sides whose fold catches the light get a 1-3 px fading "fold" band of the art's edge (renders only).
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
FACE_DE, FACE_L_WEIGHT = 5.0, 0.35   # the face ends where its colour changes this much (template_checker's canvas rule)
FACE_FROM = -4.0         # px: the face end is searched from this far inside the art edge
HARD_SHARE = 0.6         # a hard step: its 1.5 px change is at least this share of the change over 6 px
BAND_SHARE = 0.8        # this share of the band between the face edge and the far edge must be canvas-side colour
REACH = (0.12, 24.0, 90.0)   # profile reach: share of the art's short side, min, max px (a 2 in side at a steep angle)
END_DEPTHS = (0.2, 0.35, 0.5, 0.65, 0.8)  # free-end profiles at these shares of the side's width
END_STEP_MIN = 4.0       # Lab dE: the side's free end against the wall (a white side on a pale wall is a soft contrast)
END_FLAT_MAX = 4.0       # the side band inside the end must be this flat (90th percentile Lab distance)
END_MAX_RMS = 1.0        # px: the end points must lie on one straight line
END_MAX_V0 = 3.0         # px: ... that meets the face edge within this of the face corner
END_KEEP_PX = 1.5        # px: a measured far corner this close to the face line's keeps the face line (as before)
FOLD_MAX = 3.0           # px: a lit canvas fold (the face's rounded edge catching the light) is at most this wide
FOLD_MIN = 1.25          # px: narrower = only the anti-aliased edge pixel, no fold band
FOLD_SHADE = (1.05, 1.15)  # a fold is drawn only when brighter than the face by this; its brightness is capped here
FIT_MAX_RMS = 1.5       # px: a far edge that is not a straight line (a sun patch, a wall pattern) is not a side
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


def strip_quads(q, far, ends=None):
    """Per visible side: [near start, far start, far end, near end]. `far` = {side index: (F0, F1)} = the far edge's
    outward offset (px) at the side's start and end corners. `ends` = {side index: {1: (anchor, unit direction) or
    None, 2: ...}}: a FREE end's measured end edge (measure_end: a line through the face corner it was measured at);
    when its far corner lands more than END_KEEP_PX from the face-line one, the strip's end follows that line (far
    corner AND near corner, the line's crossing with the art edge). Otherwise the near corners are the art corners."""
    q = np.float32(q)
    ends = ends or {}
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
        corners, near = [], [a, b]
        lim = 4 * max(abs(far[s][0]), abs(far[s][1]), 1.0) + 4
        for idx, adj, corner in ((1, (s - 1) % 4, a), (2, (s + 1) % 4, b)):
            if adj in far_line:                               # two visible sides meet: the box edge
                x = _intersect(p, r, *far_line[adj])
            else:                                             # free end: the neighbouring face side, extended
                a2, b2, _ = lines[adj]
                x = _intersect(p, r, a2, b2 - a2)
                e = (ends.get(s) or {}).get(idx)
                if e is not None:                             # ... or the measured end edge (plain canvas)
                    anchor, d = np.float32(e[0]), np.float32(e[1])
                    xm = _intersect(p, r, anchor, d)
                    nm_ = _intersect(a, b - a, anchor, d)
                    # the neighbouring side is hidden, so the camera is inside its plane: the end edge recedes
                    # INTO the side, never past the neighbouring face line (a measured end out there is the gap or
                    # a frame's shading, not the side's end)
                    inner = xm is not None and float(np.dot(xm - a2, lines[adj][2])) <= 0.5
                    if inner and nm_ is not None and float(np.linalg.norm(xm - corner)) <= lim and \
                            float(np.linalg.norm(nm_ - corner)) <= 2 * END_MAX_V0 and (
                            x is None or float(np.linalg.norm(xm - x)) > END_KEEP_PX):
                        x = xm
                        near[idx - 1] = np.float32(nm_)
            if x is None or float(np.linalg.norm(x - corner)) > lim:
                x = np.float32(corner + n * (far[s][0] if corner is a else far[s][1]))
            corners.append(x)
        out[SIDES[s]] = np.float32([near[0], corners[0], corners[1], near[1]])
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


def face_end_1d(prof, offs, face):
    """Where the colour leaves the face colour along one profile (Lab, lightness weighted down so shading on the face
    stays face; the independent edge check's canvas rule). Searched from FACE_FROM px inside the art edge, so a SAM
    quad a few px inside or outside the true face edge still finds it. Returns the offset or None."""
    dE = np.linalg.norm((prof - face) * np.float32([FACE_L_WEIGHT, 1, 1]), axis=1)
    hit = np.nonzero((offs >= FACE_FROM) & (dE >= FACE_DE))[0]
    if not len(hit):
        return None
    i = int(hit[0])
    if i == 0:
        return float(offs[0])
    f = (FACE_DE - dE[i - 1]) / max(float(dE[i] - dE[i - 1]), 1e-6)
    return float(offs[i - 1] + f * (offs[i] - offs[i - 1]))


def _steps(prof, offs, half=0.75):
    """Lab colour change over 2 x half px centred on every offset."""
    at = lambda o: np.stack([np.interp(o, offs, prof[:, k]) for k in range(3)], -1)
    return np.linalg.norm(at(offs + half) - at(offs - half), axis=1)


def far_edge_1d(prof, offs, face):
    """One profile (outward offsets, 0 = the art edge). Returns (far edge offset or None, side width px from the face
    edge). Tony 2026-11-18 (a plain canvas on a white wall): the side is a band that starts right at the face edge in
    canvas-side colour (the face pigment, or a white side) and ENDS AT A HARD STEP (the side's back edge against the
    wall, its shadow, a gap or a wood lip). The side-colour test alone cannot end it: a white side and a white or grey
    wall pass the same test, so the band would run on over the wall. No hard step within reach = no measurable side."""
    from .template_checker import _half_cross
    fe = face_end_1d(prof, offs, face)
    if fe is None:
        return None, 0.0
    ok = side_colour(prof, face)
    sh = side_colour(prof, face, shaded=True)
    # the side starts right past the face end (never on the face itself: an orange side and the face share a colour;
    # the canvas fold can be a 2-3 px shaded roll first)
    start = np.nonzero((offs > fe) & (offs <= fe + 4.0) & ok)[0]
    if not len(start):                     # a dark gap, a shadow or the wall right at the face edge: no side here
        return None, 0.0
    i = int(start[0])
    o_s = float(offs[i])
    while i + 1 < len(offs) and ok[i + 1]:
        i += 1
    if float(offs[i]) - fe < MIN_W:        # the lit side colour must run at least MIN_W (a dark gap is not a side)
        return None, float(offs[i]) - fe
    st = _steps(prof, offs)
    wide = _steps(prof, offs, 3.0)
    lo = max(o_s + 1.5, fe + MIN_W)        # past the face -> side transition
    # the FIRST hard step past that: a real edge (most of the change within 1.5 px), never the steep middle of a
    # shading gradient across the side (an orange side darkening to brown at its back)
    peaks = [k for k in np.nonzero((offs >= lo) & (offs <= offs[-1] - 3.0) & (st >= FAR_STEP_MIN)
                                   & (st >= HARD_SHARE * wide))[0]
             if st[k] >= st[k - 1] and st[k] >= st[min(k + 1, len(st) - 1)]]
    if not peaks:
        return None, 0.0
    F = _half_cross(prof, offs, float(offs[peaks[0]]))
    band = (offs >= o_s) & (offs <= F - 0.75)
    if not band.any() or float(np.mean(ok[band] | sh[band])) < BAND_SHARE:
        return None, F - fe                # the band is not canvas-side colour throughout (a prop, a print)
    return F, F - fe


def measure_sides(rgb, art_q):
    """Which sides show the canvas side, and where each one's far edge runs. Returns ({side index: (F0, F1)},
    {side name: info})."""
    from .template_checker import _lab, edge_profile
    q = np.float32(art_q)
    lab = _lab(np.float32(rgb))
    size = min(float(np.linalg.norm(q[1] - q[0])), float(np.linalg.norm(q[3] - q[0])))
    R = float(np.clip(REACH[0] * size, REACH[1], REACH[2]))
    offs = np.arange(-10.0, R + 1e-6, 0.25, dtype="float32")
    plateau = (offs >= -10.0) & (offs <= -5.0)
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
        rms = float(np.sqrt(np.mean((np.polyval(c, ts[keep]) - Fs[keep]) ** 2)))
        F0, F1 = float(np.polyval(c, 0.0)), float(np.polyval(c, 1.0))
        st.update(segments_px=[round(float(f), 2) for f in Fs], fit_rms_px=round(rms, 3))
        if keep.sum() < MIN_SEG_SHARE * SEGMENTS or rms > FIT_MAX_RMS or min(F0, F1) < MIN_W - 1.0:
            st.update(visible=False, why="the far edge is not one straight line along the side (a wall pattern or a "
                                         "shadow, not a canvas side)")
            info[SIDES[s]] = st
            continue
        st.update(visible=True, far_px=[round(F0, 2), round(F1, 2)])
        far[s] = (F0, F1)
        info[SIDES[s]] = st
    # a box never shows two opposite sides at once: keep the one on the nearer (longer) face edge
    for s in (0, 1):
        o = s + 2
        if s in far and o in far:
            ls, lo_ = (float(np.linalg.norm(q[(k + 1) % 4] - q[k])) for k in (s, o))
            drop = o if ls >= lo_ else s
            far.pop(drop)
            info[SIDES[drop]].update(visible=False, why="the opposite side is the camera-facing one (a box never shows "
                                                        "both)")
    return far, info


def _sample(lab, P):
    """Lab colours at the points P (N x 2, pixel-edge coordinates), bilinear."""
    import cv2
    xs, ys = (P[None, :, 0] - 0.5).astype("float32"), (P[None, :, 1] - 0.5).astype("float32")
    return np.stack([cv2.remap(np.ascontiguousarray(lab[..., k]), xs, ys, cv2.INTER_LINEAR,
                               borderMode=cv2.BORDER_REPLICATE)[0] for k in range(3)], -1)


def measure_end(lab, q, s, corner_idx, F):
    """Where a visible side's FREE end runs (Tony 2026-11-18: a plain canvas on the wall shows its side as a
    trapezoid; its end edges recede in perspective from the face corners, they do not continue the face's top and
    bottom lines). At END_DEPTHS of the side's width, a profile ALONG the side from inside the side out past the
    corner; the end = the first hard step out of the side colour. The end edge is the straight line through those
    points (it must meet the face edge within END_MAX_V0 of the corner). Returns (where it meets the face edge line,
    its unit direction) or None when the end cannot be
    measured cleanly (then the face line is used, as before)."""
    from .template_checker import _half_cross
    a, b, n = _side(q, s)
    t = (b - a) / max(float(np.linalg.norm(b - a)), 1e-6)
    c, e = (a, -t) if corner_idx == 1 else (b, t)          # e points from the side's middle out past this corner
    span = min(1.5 * F + 6.0, 0.4 * float(np.linalg.norm(b - a)))
    v = np.arange(-span, 0.6 * F + 6.0 + 1e-6, 0.25, dtype="float32")
    pts = []
    for u in END_DEPTHS:
        d = u * F
        prof = np.median(np.stack([_sample(lab, c[None] + n[None] * (d + du) + e[None] * v[:, None])
                                   for du in (-0.15 * F, 0.0, 0.15 * F)]), 0)
        inside = v <= -0.35 * span
        band = np.median(prof[inside], 0)
        if float(np.percentile(np.linalg.norm(prof[inside] - band, axis=1), 90)) > END_FLAT_MAX:
            continue                                        # not a clean side band here
        dev = np.linalg.norm(prof - band, axis=1)
        st, wide = _steps(prof, v), _steps(prof, v, 3.0)
        cand = [k for k in np.nonzero((v > -0.35 * span) & (st >= END_STEP_MIN) & (st >= HARD_SHARE * wide))[0]
                if st[k] >= st[k - 1] and st[k] >= st[min(k + 1, len(st) - 1)]
                and float(np.median(dev[(v >= v[k] + 1.0) & (v <= v[k] + 2.5)])) >= END_STEP_MIN]
        if not cand:
            continue
        pts.append((d, _half_cross(prof, v, float(v[cand[0]]))))
    if len(pts) < 3:
        return None
    D, V = np.float32([p[0] for p in pts]), np.float32([p[1] for p in pts])
    k, v0 = (float(x) for x in np.polyfit(D, V, 1))       # the end edge: v = k d + v0 (v0 = where it meets the
    if abs(v0) > END_MAX_V0:                                # face edge line: at the face corner, give or take the fold)
        return None
    if float(np.sqrt(np.mean((V - (k * D + v0)) ** 2))) > END_MAX_RMS:
        return None
    c = c + e * v0
    dirv = n + e * k
    return np.float32(c), np.float32(dirv / np.linalg.norm(dirv))


def _rect_h(quad, w, h):
    """Homography from a w x h rectangle (pixel-edge coordinates) onto `quad` (pixel-edge coordinates), in the
    pixel-centre convention cv2 uses."""
    import cv2
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]]) - 0.5
    return cv2.getPerspectiveTransform(src, np.float32(quad) - 0.5)


def shading(rgb, quad, art_q, s, cap=1.5):
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
    return np.clip(grid, 0.0, cap).astype("float32")


def measure_folds(rgb, art_q, skip=()):
    """Tony 2026-11-18 ("the top and left edges feel very harsh and cut out"): on the sides the camera does NOT see,
    a plain canvas still shows its rounded FOLD as a 1-3 px light rim where the face turns away towards the light.
    Left alone, that rim stays the blank's peach next to the art: a hard outline. Per side not in `skip`: the rim =
    from the art edge out to where the colour reaches the wall next to it (Lab, 8 segments, median); its brightness
    = rim luminance / face luminance. Only a LIT rim (brighter than the face) gets a fold band (a dark gap or a
    shadow line stays the photo's own). Returns {side name: {"width_px", "shade"}}."""
    from .template_checker import _lab, edge_profile
    q = np.float32(art_q)
    rgbf = np.float32(rgb)
    lab = _lab(rgbf)
    Y = lin(rgbf / 255.0) @ W709
    offs = np.arange(-6.0, 8.0 + 1e-6, 0.25, dtype="float32")
    face_m, out_m = (offs >= -6.0) & (offs <= -3.0), (offs >= 5.0) & (offs <= 8.0)
    edges = np.linspace(0.08, 0.92, SEGMENTS + 1)
    folds = {}
    for s in range(4):
        if s in skip:
            continue
        ws_, gs = [], []
        for t0, t1 in zip(edges[:-1], edges[1:]):
            prof = edge_profile(lab, q, s, offs, float(t0), float(t1), n=40)
            yp = edge_profile(np.dstack([Y, Y, Y]), q, s, offs, float(t0), float(t1), n=40)[:, 0]
            out = np.median(prof[out_m], 0)
            far = np.nonzero((offs >= 0) & (offs <= 4.0) & (np.linalg.norm(prof - out, axis=1) >= 6.0))[0]
            if not len(far):
                continue
            w = float(offs[far[-1]]) + 0.25
            rim = (offs > 0) & (offs <= w)
            if not rim.any():
                continue
            ws_.append(w)
            gs.append(float(np.median(yp[rim])) / max(float(np.median(yp[face_m])), 1e-4))
        if len(ws_) < MIN_SEG_SHARE * SEGMENTS:
            continue
        w, g = float(np.median(ws_)), float(np.median(gs))
        if w < FOLD_MIN or g < FOLD_SHADE[0]:
            continue
        folds[SIDES[s]] = {"width_px": round(min(w, FOLD_MAX), 2), "shade": round(min(g, FOLD_SHADE[1]), 3)}
    return folds


def white_side(rgb, quad, art_q, s):
    """Is the side painted white / neutral while the face is a colour (the plain-canvas prompt: orange face, white
    sides)? Median Lab chroma of the strip's middle vs the face's next to it."""
    from .template_checker import _lab
    quad, q = np.float32(quad), np.float32(art_q)
    lab = _lab(np.float32(rgb))
    u = np.float32([0.3, 0.5, 0.7])[:, None, None]
    t = np.linspace(0.1, 0.9, 30, dtype="float32")[None, :, None]
    near = quad[0] + (quad[3] - quad[0]) * t
    farl = quad[1] + (quad[2] - quad[1]) * t
    side = _sample(lab, (near + (farl - near) * u).reshape(-1, 2))
    a, b, n = _side(q, s)
    face = _sample(lab, (a + (b - a) * t[0] - n * 8.0).reshape(-1, 2))
    Cs = float(np.median(np.hypot(side[:, 1], side[:, 2])))
    Cf = float(np.median(np.hypot(face[:, 1], face[:, 2])))
    return Cf >= 10.0 and Cs < WHITE_C * Cf


def measure(rgb, art_q, presentation="canvas", depth_frac=DEPTH_FRAC, art_offsets=None):
    """The template.json 'wrap_strips' entry for a scene (RGB uint8/float 0..255) and its art quad, or None when the
    template is not a canvas or no side is camera-facing.
    art_offsets (top, right, bottom, left px, + = outward; Tony 2026-11-18): the art quad of the template is art_q
    moved by these per-side corrections (the independent edge check's face-edge measurement). The sides are still
    DETECTED on art_q (the SAM quad the profiles were designed on: a corrected edge sits on the face's last pixel and
    confused the side test into strips on the wrong sides); each visible side's far edge then stays where it was
    measured in the photo (far_new = far_old - offset) and the strips attach to the corrected art edge."""
    if presentation != "canvas":
        return None
    from .template_checker import _lab, offset_quad
    q0 = np.float32(art_q)
    far0, info = measure_sides(rgb, q0)
    if not far0:
        return None
    offs = [0.0] * 4 if art_offsets is None else [float(x) for x in art_offsets]
    q = np.float32(offset_quad(q0, offs)) if any(offs) else q0
    far = {s: (F0 - offs[s], F1 - offs[s]) for s, (F0, F1) in far0.items()}
    lab = _lab(np.float32(rgb))
    ends = {}
    for s, (F0, F1) in far0.items():
        for idx, adj, F in ((1, (s - 1) % 4, F0), (2, (s + 1) % 4, F1)):
            if adj not in far0:
                ends.setdefault(s, {})[idx] = measure_end(lab, q0, s, idx, F)
    quads = strip_quads(q, far, ends)
    sides = {}
    for s, (F0, F1) in far.items():
        nm = SIDES[s]
        quad = quads[nm]
        g = shading(rgb, quad, q, s)
        white = white_side(rgb, quad, q, s)
        if white:      # Tony 2026-11-18, plain canvas: a WHITE side next to the orange face. Their luminance ratio is
            # mostly paint (white vs orange), not light: it clipped at 1.5 everywhere and the strip glowed. Keep the
            # photo's shading pattern across and along the side, its brightest part = the face's brightness.
            g = shading(rgb, quad, q, s, cap=np.inf)
            g = np.clip(g / max(float(np.percentile(g, 95)), 1e-4), 0.0, 1.0).astype("float32")
        free = [i for i, adj in ((1, (s - 1) % 4), (2, (s + 1) % 4)) if adj not in far]
        info[nm]["far_px"] = [round(F0, 2), round(F1, 2)]
        if any(offs):
            info[nm]["far_px_detected"] = [round(far0[s][0], 2), round(far0[s][1], 2)]
        sides[nm] = {"quad": np.round(quad, 3).tolist(), "far_px": info[nm]["far_px"],
                     **({"far_px_detected": info[nm]["far_px_detected"]} if any(offs) else {}),
                     "ends": {str(i): (None if (ends.get(s) or {}).get(i) is None else
                                       {"anchor": np.round(ends[s][i][0], 3).tolist(),
                                        "dir": np.round(ends[s][i][1], 4).tolist()}) for i in free},
                     "width_px": [round(float(np.linalg.norm(quad[1] - quad[0])), 2),
                                  round(float(np.linalg.norm(quad[2] - quad[3])), 2)],
                     "round_corners": free, "segments_px": info[nm]["segments_px"],
                     "fit_rms_px": info[nm]["fit_rms_px"], "shade": np.round(g, 3).tolist(),
                     "shade_basis": "white side: the photo's shading pattern, brightest = the face" if white
                     else "side luminance / face luminance",
                     "shade_face_to_back": [round(float(g[:, 0].mean()), 3), round(float(g[:, -1].mean()), 3)]}
    return {"version": VERSION, "depth_frac": depth_frac, "corner_radius_px": CORNER_R, "layer": LAYER,
            "art_quad": np.round(q, 3).tolist(), "sides": sides,
            "folds": measure_folds(rgb, q, skip=tuple(far)),
            **({"art_offsets_px": [round(x, 2) for x in offs], "detected_on_quad": np.round(q0, 3).tolist()}
               if any(offs) else {}),
            "not_shown": {k: v for k, v in info.items() if not v.get("visible")},
            "method": "face edge -> canvas-side colour band -> first HARD step to the wall / gap / wood lip (scene Lab "
                      "profiles, 8 segments, one straight line, never both opposite sides); free ends = the measured "
                      "end edge through the face corner; shading = photo luminance / face luminance (linear, no "
                      "colour)",
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
    if art is not None and ws.get("art_quad") is not None:
        aq = np.float32(ws["art_quad"])
        for nm, fd in (ws.get("folds") or {}).items():
            # the lit fold: the art's own edge pixels carried 1-3 px over the rim, brightened like the rim, fading
            # out across it (a rounded edge, not a cut). Renders only: the PSD placeholder shows the strips alone.
            s = SIDES.index(nm)
            a0, b0, n = _side(aq, s)
            w = float(fd["width_px"])
            quad = np.float32([a0, a0 + n * w, b0 + n * w, b0])
            L = int(math.ceil(max(float(np.linalg.norm(b0 - a0)), 4)))
            band = band_source(art_l, nm, 2)
            band = cv2.resize(np.ascontiguousarray(band), (4, L), interpolation=cv2.INTER_AREA)
            x0, y0 = max(0, int(math.floor(quad[:, 0].min())) - 2), max(0, int(math.floor(quad[:, 1].min())) - 2)
            x1, y1 = min(W, int(math.ceil(quad[:, 0].max())) + 3), min(H, int(math.ceil(quad[:, 1].max())) + 3)
            if x1 <= x0 or y1 <= y0:
                continue
            Hm = _rect_h(quad - np.float32([x0, y0]), 4, L)
            warped = cv2.warpPerspective(band * float(fd["shade"]), Hm, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR,
                                         borderMode=cv2.BORDER_REPLICATE)
            yy, xx = np.mgrid[y0:y1, x0:x1].astype("float32") + 0.5
            d = ((xx - a0[0]) * n[0] + (yy - a0[1]) * n[1]) / max(w, 1e-3)
            ramp = np.clip(1.0 - d, 0.0, 1.0)
            cov = coverage(quad, W, H)[y0:y1, x0:x1] * ramp
            rgb[y0:y1, x0:x1] += warped * cov[..., None]
            alpha[y0:y1, x0:x1] += cov
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
