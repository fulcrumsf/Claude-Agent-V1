"""Room mockups for the Production tab (listing slots 3 and 9-19), Tony's recipe of 2026-11-08 (replaces the computed-frame
approach): the image model draws the WHOLE room with one real frame holding a BLANK WHITE insert; the art is laid in
afterwards, so one scene works for any print and the art's pixels are never redrawn.

  1. scene: Nano Banana Pro / Nano Banana 2.1 / GPT Image 2.5 through kie_edit.generate() (app/kie_edit.py, copied
     from the archived Teak Sideboard's Scripts 2026-11-10), prompt from room_slots.scene_prompt (art never in it).
  2. sam_detect() (Tony 2026-11-10, "pixel-perfect" standard): Gemini rough box -> SAM 2.1 (largest checkpoint) ->
     material-edge alpha refinement -> sub-pixel four-corner fit -> loud failure when corners and mask disagree
     (app/sam_frames.py, run in the ikigai-sam venv), then out to the OPENING = the frame's HARD inner edge with the
     shadowed paper counted as opening (sam_frames.opening_quad, Tony 2026-11-12). True width:height from the
     perspective (rooms.true_aspect). A scene whose opening is more than 3% off the print's ratio is REJECTED
     (Regenerate), never padded with a mat. The art quad = the opening + opening_pad_px (0.5 px since 2026-11-15) under the frame.
     The old brightness/Canny find_insert() below is LEGACY (kept for reference and tests, never used by new builds).
  3. PhotoCraft (photocraft-cli, not Photoshop) layered PSD, hand-editable, named:
        GLARE > Glass Sheen (Screen 8%)
        SHADOWS > Light Shadow + Frame Edge Shadow + Frame Hard Shadow (Multiply). Tony's shadow rule
                  (Mockup_Docs/Template_Layer_Rules_And_Checker_Spec.md): plain BLACK fill, cut to shape, blurred,
                  each with a LAYER MASK cut to the art quad (select.lasso on the quad -> revealSelection). The art
                  covers the baked frame shadow, so these rebuild it from MEASUREMENTS (measure_edge_shadows):
                  Frame Hard Shadow: crisp, the frame edge's measured tone over the art's pad (the photo's dark
                  inner wall / lip line, or the frame face), so no art shows on the wood. Frame Edge Shadow: soft,
                  per side a blurred black band (strength, width, blur fitted to the paper's darkening from the
                  opening inward). Light Shadow: angle MEASURED from the photo - the wall's sun line inside the SAM
                  wall mask when there is one, else the direction + depth of the measured light falloff across the
                  blank insert. Opacity = the measured darkening. Photo pixels are never copied into a shadow.
        Place Artwork Here (smart object on the art quad, native pixels at its true ratio)
        BASE (room photo)
  3b. card_verify(): a black and a white card rendered through the finished PSD; the visible art quad (sub-pixel fit
     on the anti-aliased difference) must sit within card_tol_px (1 px) of the art quad, reach the opening on every
     side (no sliver beyond 0.5 px) and run under the frame by at most 2 px (+0.5), else the build fails.
  4. render: the print COVER-FIT to the smart object's native pixels (centred, the excess clipped, never stretched,
     never a white border; more than 3% crop is refused), replaceContents, exported as JPG into 03-Etsy Images under
     the slot number; then room_templates.guard_quad (hue + shadow cover).
  5. AUTO-SAVE: every generated scene becomes a template in Tony's tree
        Portrait_Templates/<NNN_Ratio_*>/<NNN_Room>/<NNN_Style>/<AI_...>/  (PSD, source scene, preview, template.json)
     using his existing NNN_ folders; a style folder is created only when a template first lands in that cell
     (next free number). Agents never create ratio or room folders: a room with no folder is reported instead.

Tony's own PSDs get a template.json too (`python3 -m app.scene_templates --manifests`): smart-object pixels and the
visible art quad (measured once by rendering a black and a white card and diffing), so the "+" picker can render any
of them with the same fit and guard. The Teak Sideboard (room.json, computed frames + wall-colour layers) was ARCHIVED
by Tony 2026-11-10 (002_Modern/Archive/Teak_Sideboard/); Archive folders are never scanned, so it is never offered.
"""
import json
import math
import re
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

import numpy as np

from . import room_slots as rs
from .db import ROOT

DEFAULTS = {"room_templates_dir": "../Room_Templates", "photocraft_bin": "photocraft-cli", "room_render_timeout_s": 300,
            "room_scene_engine": "nbpro", "room_scene_resolution": "2K", "room_scene_aspect": "4:3",
            "room_guard_max_cover": 0.35,
            "kie_edit_script": "app/kie_edit.py",
            # SAM 2 (Tony 2026-11-10: every new template's corners + masks): its own venv outside the workspace
            "sam_python": "~/.cache/ikigai-sam/bin/python", "sam_timeout_s": 600, "card_tol_px": 1.0,
            # Tony 2026-11-12: the art runs this far under the frame's hard inner edge (never more than
            # template_checker.PAD_MAX_PX); the Frame Hard Shadow layer darkens it to the frame edge's measured tone.
            # 0.5 since 2026-11-15 (Tony's own hand fix of the Sideboard template: art 0.4-0.6 px under the frame,
            # so the photo's own dark inner frame line shows)
            "opening_pad_px": 0.5}
LIBRARY = "Portrait_Templates"
MANIFEST = "template.json"
ART = "Place Artwork Here"
BASE_NAME = "BASE (room photo)"
# canonical folder name when a NEW style folder is needed (Tony's naming, e.g. 001_Japandi_Minimalist)
DECOR_FOLDER = {"Japandi": "Japandi_Minimalist", "Boho": "Boho_Colorful", "Neutral": "Neutral_Aesthetic"}
# kie.ai credits per scene by engine (nbpro 1K/2K = 18, engines.json 2026-11-04); others shown after the run
SCENE_CREDITS = {"nbpro": 18}
W709 = np.array([0.2126, 0.7152, 0.0722], "float32")


class TemplateError(Exception):
    """A plain reason a room image could not be made (shown on the card)."""


def _cfg(settings, key):
    return (settings or {}).get(key, DEFAULTS[key])


def _abs(p):
    p = Path(p)
    return p if p.is_absolute() else (ROOT / p).resolve()


def library(settings=None):
    return _abs(_cfg(settings, "room_templates_dir")) / LIBRARY


# ---------- the folder tree (Tony's NNN_ masters) ----------

MASTER = re.compile(r"^\d{3}_")


def _kids(d):
    return sorted(c for c in d.iterdir() if c.is_dir() and c.name != "Archive") if d.is_dir() else []


def ratio_dir(settings, ratio):
    from .template_gallery import ratio_of
    for d in _kids(library(settings)):
        if MASTER.match(d.name) and ratio_of(d.name) == ratio:
            return d
    return None


def room_dir(settings, ratio, room):
    """<NNN_Ratio>/<NNN_Room> for an Etsy/scene room, or None when Tony has no folder for it there."""
    want = rs.ROOM_FOLDER.get(room)
    rd = ratio_dir(settings, ratio)
    if not want or rd is None:
        return None
    return next((d for d in _kids(rd) if MASTER.match(d.name) and rs.norm(d.name) == want), None)


def available_rooms(settings=None):
    """{room: [ratios that have a folder for it]} (rooms with none are left out)."""
    out = {}
    for room in rs.ETSY_ROOMS + rs.SCENE_ONLY_ROOMS:
        ok = [r for r in rs.RATIOS if room_dir(settings, r, room) is not None]
        if ok:
            out[room] = ok
    return out


def _is_style_dir(d):
    return MASTER.match(d.name) and not any(d.glob("*.psd"))


def style_dir(rdir, decor, create=False):
    """The NNN_ style folder in a room folder that fits this decor (exact name first, then alias words). With
    create=True a missing one is made with the next free number - only when a template is about to land in it."""
    styles = [d for d in _kids(rdir) if _is_style_dir(d)]
    exact = [d for d in styles if rs.norm(d.name) in (rs.norm(decor), rs.norm(DECOR_FOLDER.get(decor, decor)))]
    hit = exact or [d for d in styles if rs.decor_matches(decor, d.name)]
    if hit:
        return hit[0]
    if not create:
        return None
    nums = [int(d.name[:3]) for d in _kids(rdir) if MASTER.match(d.name)]
    d = rdir / f"{(max(nums) + 1) if nums else 1:03d}_{DECOR_FOLDER.get(decor, decor)}"
    d.mkdir()
    return d


# ---------- library templates (Tony's PSDs + saved AI scenes) ----------

def load_manifest(psd):
    """The manifest of this PSD: a pending rebuild's sidecar (<stem>.json) or the folder's template.json."""
    from .template_gallery import psd_manifest
    return psd_manifest(psd)


def library_templates(settings=None):
    """Every template Production may use (template_gallery.scan) with its manifest (or None). Templates waiting for
    Tony's Approve (a gap build or a rebuild, template_gallery.is_pending) are left out: never auto-picked, never
    pickable with +, until approved."""
    from .template_gallery import scan
    out = []
    for t in scan(settings)[0]:
        if t.get("pending"):
            continue
        out.append(dict(t, manifest=None if t.get("wired") else load_manifest(t["psd"])))
    return out


def matches(t, room, decor, ratio):
    """Does a library template fit a planned slot? Same ratio bucket, same room folder, decor named by its style
    folder / Directory style / name / description. Wired rooms (Teak, computed frames) are never auto-picked."""
    if t.get("wired") or t["ratio"] != ratio or rs.norm(t["room"]) != rs.ROOM_FOLDER.get(room):
        return False
    m = t.get("manifest") or {}
    return rs.decor_matches(decor, t["style"], t["name"], t.get("desc"), m.get("decor"))


# ---------- step 2: find the blank insert ----------

def _order(pts):
    from .rooms import order_quad
    return order_quad(pts)


def _poly_mask(q, W, H):
    import cv2
    m = np.zeros((H, W), "uint8")
    cv2.fillPoly(m, [np.int32(np.round(np.float32(q) * 4))], 255, lineType=cv2.LINE_AA, shift=2)
    return m.astype("float32") / 255


def _expand(q, f):
    """Grow (f > 0) or shrink (f < 0) a quad about its centre in its own unit square."""
    import cv2
    q = np.float32(q)
    Hm = cv2.getPerspectiveTransform(np.float32([[0, 0], [1, 0], [1, 1], [0, 1]]), q)
    pts = np.float32([[-f, -f], [1 + f, -f], [1 + f, 1 + f], [-f, 1 + f]]).reshape(-1, 1, 2)
    return cv2.perspectiveTransform(pts, Hm).reshape(-1, 2)


def sub_quad(q, u0, v0, u1, v1):
    import cv2
    Hm = cv2.getPerspectiveTransform(np.float32([[0, 0], [1, 0], [1, 1], [0, 1]]), np.float32(q))
    pts = np.float32([[u0, v0], [u1, v0], [u1, v1], [u0, v1]]).reshape(-1, 1, 2)
    return cv2.perspectiveTransform(pts, Hm).reshape(-1, 2)


def _snap(gray, q, search=4):
    """Polish: move each edge to the strongest nearby dark-to-bright step going inward (frame lip -> paper; the
    frame's outer edge steps the other way and is ignored), measured near both ends of the edge, then re-intersect."""
    import cv2
    g = cv2.GaussianBlur(gray, (0, 0), 1.2)
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
    q = np.float32(q)
    c = q.mean(0)

    def best_offset(a, b, n, t0, t1):
        best = (-1.0, 0)
        s = np.linspace(t0, t1, 60)[:, None]
        for d in range(-search, search + 1):
            pts = a + (b - a) * s + n * d
            xs = np.clip(pts[:, 0], 0, g.shape[1] - 1).astype(int)
            ys = np.clip(pts[:, 1], 0, g.shape[0] - 1).astype(int)
            v = float(np.clip(gx[ys, xs] * n[0] + gy[ys, xs] * n[1], 0, None).mean())   # brighter going inward
            if v > best[0] + 1e-3 or (abs(v - best[0]) <= 1e-3 and abs(d) < abs(best[1])):
                best = (v, d)
        return best[1]
    lines = []
    for i in range(4):
        a, b = q[i], q[(i + 1) % 4]
        t = (b - a) / max(np.linalg.norm(b - a), 1e-6)
        n = np.float32([-t[1], t[0]])
        if np.dot(c - a, n) < 0:
            n = -n
        d0, d1 = best_offset(a, b, n, 0.12, 0.38), best_offset(a, b, n, 0.62, 0.88)
        p0, p1 = a + (b - a) * 0.25 + n * d0, a + (b - a) * 0.75 + n * d1
        lines.append((p0, p1))

    def inter(l1, l2):
        p, r = l1[0], l1[1] - l1[0]
        s_, u = l2[0], l2[1] - l2[0]
        cr = r[0] * u[1] - r[1] * u[0]
        if abs(cr) < 1e-9:
            return None
        t_ = ((s_ - p)[0] * u[1] - (s_ - p)[1] * u[0]) / cr
        return p + r * t_
    out = [inter(lines[3], lines[0]), inter(lines[0], lines[1]), inter(lines[1], lines[2]), inter(lines[2], lines[3])]
    if any(o is None for o in out):
        return q
    out = np.float32(out)
    return out if np.abs(out - q).max() <= search * 2.5 else q


def _fit_sides(q, contour):
    """Straight sides from the region outline: every outline point near a side votes in a robust line fit (a hull
    corner pulled out by a shadow or a frame join is overruled), then neighbouring lines are intersected."""
    import cv2
    q = np.float32(q)
    pts = np.float32(contour).reshape(-1, 2)
    if len(pts) < 16:
        return q
    size = max(math.dist(q[0], q[2]), 1.0)
    lines = []
    for i in range(4):
        a, b = q[i], q[(i + 1) % 4]
        ab = b - a
        L = float(np.linalg.norm(ab))
        t = ((pts - a) @ ab) / max(L * L, 1e-6)
        dist = np.abs((pts[:, 0] - a[0]) * ab[1] - (pts[:, 1] - a[1]) * ab[0]) / max(L, 1e-6)
        sel = pts[(t > 0.1) & (t < 0.9) & (dist < 0.025 * size)]
        if len(sel) < 6:
            return q
        vx, vy, x0, y0 = cv2.fitLine(sel, cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
        lines.append((np.float32([x0, y0]), np.float32([x0 + vx, y0 + vy])))
    out = []
    for i in range(4):
        (p, p2), (s_, s2) = lines[(i - 1) % 4], lines[i]
        r, u = p2 - p, s2 - s_
        cr = r[0] * u[1] - r[1] * u[0]
        if abs(cr) < 1e-9:
            return q
        out.append(p + r * (((s_ - p)[0] * u[1] - (s_ - p)[1] * u[0]) / cr))
    out = np.float32(out)
    return out if np.abs(out - q).max() < 0.08 * size else q


def _inward(gray, q, frac=0.03):
    """Last step: a pale frame (or its lit lip) can be as bright as the paper and get included in the white region.
    For each side, near both ends, look up to `frac` of the size inward for dark-to-bright steps and take the
    INNERMOST strong one (at least half the strongest): the paper edge always sits inside the frame edges."""
    import cv2
    g = cv2.GaussianBlur(gray, (0, 0), 1.0)
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
    H, W = g.shape
    q = np.float32(q)
    c = q.mean(0)
    reach = max(3, int(frac * min(math.dist(q[0], q[1]), math.dist(q[0], q[3]))))
    lines = []
    for i in range(4):
        a, b = q[i], q[(i + 1) % 4]
        t = (b - a) / max(np.linalg.norm(b - a), 1e-6)
        n = np.float32([-t[1], t[0]])
        if np.dot(c - a, n) < 0:
            n = -n
        ends = []
        for t0, t1 in ((0.1, 0.35), (0.65, 0.9)):
            s = a + (b - a) * np.linspace(t0, t1, 50)[:, None]
            prof = []
            for d in range(-2, reach + 1):
                pts = s + n * d
                xs = np.clip(pts[:, 0], 0, W - 1).astype(int)
                ys = np.clip(pts[:, 1], 0, H - 1).astype(int)
                prof.append(float(np.median(gx[ys, xs] * n[0] + gy[ys, xs] * n[1])))
            prof = np.array(prof)
            top = prof.max()
            peaks = [k for k in range(len(prof)) if prof[k] >= 0.5 * top and prof[k] > 0
                     and (k == 0 or prof[k] >= prof[k - 1]) and (k == len(prof) - 1 or prof[k] >= prof[k + 1])]
            d = (max(peaks) - 2) if (peaks and top > 0) else 0
            ends.append(a + (b - a) * ((t0 + t1) / 2) + n * d)
        lines.append((ends[0], ends[1]))
    out = []
    for i in range(4):
        (p, p2), (s_, s2) = lines[(i - 1) % 4], lines[i]
        r, u = p2 - p, s2 - s_
        cr = r[0] * u[1] - r[1] * u[0]
        if abs(cr) < 1e-9:
            return q
        out.append(p + r * (((s_ - p)[0] * u[1] - (s_ - p)[1] * u[0]) / cr))
    out = np.float32(out)
    return out if np.abs(out - q).max() <= reach * 2 + 2 else q


def _edge_support(gray, q):
    """How well a quad sits on the paper edge: mean dark-to-bright step going inward, sampled just across each side
    (the weakest side counts double, so one wrong side cannot hide behind three good ones)."""
    import cv2
    g = cv2.GaussianBlur(gray, (0, 0), 1.2)
    H, W = g.shape
    q = np.float32(q)
    c = q.mean(0)
    vals = []
    for i in range(4):
        a, b = q[i], q[(i + 1) % 4]
        t = (b - a) / max(np.linalg.norm(b - a), 1e-6)
        n = np.float32([-t[1], t[0]])
        if np.dot(c - a, n) < 0:
            n = -n
        s = a + (b - a) * np.linspace(0.08, 0.92, 80)[:, None]
        pi, po = s + n * 3, s - n * 3
        ok = (po[:, 0] >= 0) & (po[:, 0] < W) & (po[:, 1] >= 0) & (po[:, 1] < H) & \
             (pi[:, 0] >= 0) & (pi[:, 0] < W) & (pi[:, 1] >= 0) & (pi[:, 1] < H)
        if not ok.any():
            return -1e9
        vi = g[pi[ok, 1].astype(int), pi[ok, 0].astype(int)]
        vo = g[po[ok, 1].astype(int), po[ok, 0].astype(int)]
        vals.append(float(np.median(vi - vo)))
    return sum(vals) + min(vals)


def _upright(q, max_deg=12):
    """Left and right edges near vertical: a level camera keeps a hung frame's sides upright (3/4 views included);
    a sun patch or a rug is not."""
    for a, b in ((q[0], q[3]), (q[1], q[2])):
        dx, dy = float(b[0] - a[0]), float(b[1] - a[1])
        if dy <= 0 or abs(math.degrees(math.atan2(dx, dy))) > max_deg:
            return False
    return True


def _candidates(a, gray):
    """Four-sided candidate shapes: bright low-saturation regions at several brightness cut-offs, plus closed
    edge contours (finds paper crossed by strong window-bar shadows). Yields (quad, region area or None, contour)."""
    import cv2
    from .rooms import _quad_from_hull
    H, W = gray.shape
    mx, mn = a.max(2), a.min(2)
    sat = (mx - mn) / np.maximum(mx, 1)
    for cut in sorted({float(np.percentile(mx, p)) for p in (99, 97, 94, 90, 85, 80, 74, 68, 60)}, reverse=True):
        m = ((mx >= cut - 1) & (sat < 0.16)).astype("uint8") * 255
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), "uint8"))
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7, 7), "uint8"))
        cs, _ = cv2.findContours(m, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for c in cs:
            area = cv2.contourArea(c)
            if 0.012 * W * H < area < 0.45 * W * H:
                yield _order(_quad_from_hull(cv2.convexHull(c))), area, c
    g8 = cv2.GaussianBlur(gray, (0, 0), 1.5).astype("uint8")
    med = float(np.median(g8))
    e = cv2.dilate(cv2.Canny(g8, 0.4 * med, 1.0 * med), np.ones((3, 3), "uint8"))
    cs, _ = cv2.findContours(e, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    for c in cs:
        if not 0.012 * W * H < cv2.contourArea(c) < 0.45 * W * H:
            continue
        ap = cv2.approxPolyDP(c, 0.02 * cv2.arcLength(c, True), True)
        if len(ap) == 4:
            yield _order(ap.reshape(-1, 2).astype("float32")), None, c


def find_insert(rgb, target=None):
    """LEGACY (brightness threshold + Canny; replaced by sam_detect for every new build, 2026-11-10). Corners (tl, tr, br, bl, float32) of the blank white insert, plus {aspect, screen_aspect, fill, score}.
    Returns (None, reason) when there is no clean one. A candidate must be a clean convex four-sided shape that does
    not touch the picture edge, with upright sides, a darker band around it (the frame), neutral (paper, not a
    coloured wall) and smooth inside (no objects); best score wins, then the edges are snapped to the paper edge."""
    import cv2
    from .rooms import true_aspect
    a = np.asarray(rgb, "float32")
    H, W = a.shape[:2]
    mx, mn = a.max(2), a.min(2)
    sat = (mx - mn) / np.maximum(mx, 1)
    gray = a @ np.float32([0.299, 0.587, 0.114])
    lap = np.abs(cv2.Laplacian(cv2.GaussianBlur(gray, (0, 0), 1.0), cv2.CV_32F))
    best, why, seen = None, "no blank white insert found", set()
    for q, area, cont in _candidates(a, gray):
        key = tuple(np.round(q / 6).astype(int).ravel())
        if key in seen or not cv2.isContourConvex(q.reshape(-1, 1, 2)):
            continue
        seen.add(key)
        qa = cv2.contourArea(q)
        fill = area / qa if (area and qa) else 1.0
        if fill < 0.86 or fill > 1.06 or qa < 0.012 * W * H:
            continue
        if q[:, 0].min() < 3 or q[:, 1].min() < 3 or q[:, 0].max() > W - 4 or q[:, 1].max() > H - 4:
            continue
        if not _upright(q):
            continue
        asp = true_aspect(q, (W, H))
        if not 0.42 < asp < 1.05:                       # a vertical (or square-ish) frame insert
            why = f"the white area found is not a vertical frame insert ({asp:.2f} wide:tall)"
            continue
        inner = _poly_mask(_expand(q, -0.06), W, H) > 0.5
        ring = (_poly_mask(_expand(q, 0.06), W, H) > 0.5) & ~(_poly_mask(_expand(q, 0.01), W, H) > 0.5)
        if inner.sum() < 50 or ring.sum() < 50:
            continue
        contrast = (float(np.median(gray[inner])) - float(np.median(gray[ring]))) / 255
        smooth = float(np.percentile(lap[inner], 90))
        neutral = float(np.median(sat[inner]))
        if contrast < 0.04 or smooth > 18 or neutral > 0.2:
            continue
        ratio_fit = 1 - min(abs(math.log(asp / target)) * 3, 1) if target else 0.5
        score = (2 * fill + 2 * min(contrast, 0.3) / 0.3 + ratio_fit + (1 - smooth / 18) + (1 - neutral / 0.2)
                 + 0.5 * (qa / (W * H)) ** 0.5)
        if best is None or score > best[1]["score"]:
            best = (q, {"aspect": round(asp, 4), "fill": round(fill, 3), "score": round(score, 3),
                        "contrast": round(contrast, 3), "smooth": round(smooth, 2)}, cont)
    if best is None:
        return None, why
    hull_q = best[0]
    fit_q = _fit_sides(hull_q, best[2])
    q = max((_order(x) for x in (hull_q, fit_q, _snap(gray, hull_q), _snap(gray, fit_q))),
            key=lambda x: _edge_support(gray, x))
    q = _order(_inward(gray, q))
    info = best[1]
    info["aspect"] = round(true_aspect(q, (W, H)), 4)
    l, r = math.dist(q[0], q[3]), math.dist(q[1], q[2])
    info["screen_aspect"] = round(((math.dist(q[0], q[1]) + math.dist(q[3], q[2])) / 2) / ((l + r) / 2), 4)
    info["skew"] = round(max(l, r) / max(min(l, r), 1), 3)
    return q, info


def art_quad(insert_q, insert_aspect, target, tol=0.15):
    """Where the art goes: the whole insert, when its true shape is within `tol` of the print ratio (the art is then
    cover-fit, at most `tol` cropped). Further off = the scene is rejected (Tony 2026-11-10: regenerate, never a mat
    by accident; mats exist only as template layers). Returns (quad, "full") or raises TemplateError."""
    off = insert_aspect / target - 1
    if abs(off) <= tol:
        return np.float32(insert_q), "full"
    raise TemplateError(f"the drawn frame insert is {insert_aspect:.3f} wide:tall, {off:+.1%} off the print ratio "
                        f"{target:.3f} (limit {tol:.0%}); Regenerate for a new scene")


def so_pixels(q, target):
    """Smart-object pixel size: the art's exact ratio, as tall as the quad's longer side on screen (no upsampling
    loss in the render)."""
    hpx = max(math.dist(q[0], q[3]), math.dist(q[1], q[2]))
    return [max(8, round(hpx * target)), max(8, round(hpx))]


# ---------- step 3: layers + PSD ----------

def light_side(gray, q):
    W, H = gray.shape[1], gray.shape[0]
    ring = (_poly_mask(_expand(q, 0.25), W, H) > 0.5) & ~(_poly_mask(_expand(q, 0.02), W, H) > 0.5)
    cx = float(np.mean(np.float32(q)[:, 0]))
    xs = np.arange(W)[None, :].repeat(H, 0)
    left, right = ring & (xs < cx), ring & (xs >= cx)
    a = gray[left].mean() if left.any() else 0
    b = gray[right].mean() if right.any() else 0
    return "left" if a >= b else "right"


def _save_rgba(rgb, alpha, path):
    from PIL import Image
    arr = np.dstack([np.clip(rgb, 0, 1), np.clip(alpha, 0, 1)])
    Image.fromarray((arr * 255 + 0.5).astype("uint8"), "RGBA").save(path)


def light_falloff(img, insert_q):
    """The blank insert's measured light falloff as a plane (no pixels copied): returns (alpha 0..1 over the canvas,
    strength = the relative brightness drop across the insert)."""
    H, W = img.shape[:2]
    q = np.float32(insert_q)
    Y = img @ W709
    m = _poly_mask(_expand(q, -0.06), W, H) > 0.5
    ys, xs = np.nonzero(m)
    if len(xs) < 50:
        return np.zeros((H, W), "float32"), 0.0
    A = np.c_[xs, ys, np.ones_like(xs)].astype("float64")
    coef, *_ = np.linalg.lstsq(A, Y[ys, xs].astype("float64"), rcond=None)
    gy, gx = np.mgrid[0:H, 0:W].astype("float32")
    plane = coef[0] * gx + coef[1] * gy + coef[2]
    vals = plane[m]
    hi, lo = float(vals.max()), float(vals.min())
    if hi <= 1e-4 or hi - lo < 1e-4:
        return np.zeros((H, W), "float32"), 0.0
    return np.clip((hi - plane) / (hi - lo), 0, 1).astype("float32"), float((hi - lo) / hi)


def edge_shadow(q, W, H, side="left", strength=(0.22, 0.06, 0.16, 0.05), width=0.006):
    """Mat bevel: a thin soft shadow along the cut edge of the mat (top and the side away from the light)."""
    import cv2
    q = np.float32(q)
    Hi = np.linalg.inv(cv2.getPerspectiveTransform(np.float32([[0, 0], [1, 0], [1, 1], [0, 1]]), q))
    Y, X = np.mgrid[0:H, 0:W].astype("float32")
    P = np.stack([X, Y, np.ones_like(X)], -1) @ Hi.T
    u, v = P[..., 0] / P[..., 2], P[..., 1] / P[..., 2]
    w_, h_ = math.dist(q[0], q[1]), math.dist(q[0], q[3])
    s = width * min(w_, h_)
    st, sb, sl, sr = strength
    if side == "right":
        sl, sr = sr * 0.6, sl * 1.2
    else:
        sl, sr = sl * 1.2, sr * 0.6
    f = lambda d, k: 1 - k * np.exp(-np.clip(d, 0, None) / max(s, 0.5))
    return f(v * h_, st) * f((1 - v) * h_, sb) * f(u * w_, sl) * f((1 - u) * w_, sr)


def glass(q, W, H):
    import cv2
    q = np.float32(q)
    Hi = np.linalg.inv(cv2.getPerspectiveTransform(np.float32([[0, 0], [1, 0], [1, 1], [0, 1]]), q))
    Y, X = np.mgrid[0:H, 0:W].astype("float32")
    P = np.stack([X, Y, np.ones_like(X)], -1) @ Hi.T
    t = P[..., 0] / P[..., 2] * 0.75 + P[..., 1] / P[..., 2] * 0.35
    return np.clip(0.55 * np.exp(-((t - 0.32) / 0.16) ** 2) + 0.25 * np.exp(-((t - 0.78) / 0.07) ** 2), 0, 1)


def placeholder(w, h, path):
    from PIL import Image
    ph = np.full((h, w, 3), 232, "uint8")
    st = max(20, w // 12)
    ph[:, ::st] = 150
    ph[::st, :] = 150
    Image.fromarray(ph).save(path)


SHADOW_OPACITY = {"Frame Hard Shadow": 0.45, "Frame Edge Shadow": 0.30, "Light Shadow": 0.17}
LAYER_PAD = 4            # shadow pixels reach this far past the art quad; the layer MASK makes the exact cut
HARD_BLUR_PX = 0.35      # the hard inner edge stays crisp (Gaussian sigma of its inner cut)


# ---------- SAM 2 (subprocess into the ikigai-sam venv) ----------

def sam_detect(scene_png, work, settings=None, box=None, wall=True, canvas=False):
    """Corners + full-resolution alpha of the blank insert (and the wall mask) from app/sam_frames.py, run with the
    SAM venv's python. Returns (result dict, insert alpha HxW 0..1, wall alpha or None). Raises TemplateError."""
    import os
    from . import sam_frames as sf
    py = Path(os.path.expanduser(_cfg(settings, "sam_python")))
    if not py.is_file():
        raise TemplateError(f"SAM 2 is not installed ({py}); see app/sam_frames.py")
    work = Path(work)
    js, al, wl = work / "sam.json", work / "sam_alpha.png", work / "sam_wall.png"
    args = [str(py), "-I", str(Path(sf.__file__).resolve()), "detect", str(scene_png), "--json", str(js),
            "--alpha", str(al)]
    if wall:
        args += ["--wall", str(wl)]
    if canvas:
        args += ["--canvas"]
    if box is not None:
        args += ["--box", ",".join(f"{float(v):.1f}" for v in box)]
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=int(_cfg(settings, "sam_timeout_s")))
    except subprocess.TimeoutExpired:
        raise TemplateError("SAM 2 took too long")
    res = json.loads(js.read_text()) if js.is_file() else None
    if r.returncode or res is None or res.get("error"):
        why = (res or {}).get("error") or (r.stderr or r.stdout).strip()[-300:]
        raise TemplateError(f"no clean blank frame insert (SAM 2: {why})")
    return res, sf.read_alpha(al), (sf.read_alpha(wl) if wall and wl.is_file() else None)


# ---------- measured shadows ----------

def _side_frame(q, side):
    a, b = q[side], q[(side + 1) % 4]
    t = (b - a) / max(float(np.linalg.norm(b - a)), 1e-6)
    n = np.float32([-t[1], t[0]])
    return a, b, (n if np.dot(q.mean(0) - a, n) > 0 else -n)


def side_distance(q, W, H):
    """Signed distance (px, inward positive) of every pixel to each side line of quad q: list of 4 HxW arrays."""
    gy, gx = np.mgrid[0:H, 0:W].astype("float32")
    gx += 0.5
    gy += 0.5
    out = []
    for side in range(4):
        a, _, n = _side_frame(np.float32(q), side)
        out.append((gx - a[0]) * n[0] + (gy - a[1]) * n[1])
    return out


def measure_lip(img, q):
    """The frame lip's shadow on the blank insert, MEASURED per side: the paper's darkening next to the edge relative
    to its own plateau a little further in, fitted as k * exp(-d / w). Returns [{side, k, w_px}] (k 0 = none)."""
    from . import sam_frames as sf
    Y = (img @ W709).astype("float32")
    q = np.float32(q)
    size = min(math.dist(q[0], q[1]), math.dist(q[0], q[3]))
    D = float(max(10.0, 0.08 * size))
    offs = np.arange(0.75, D, 0.5, dtype="float32")
    out = []
    for side in range(4):
        a, b, n = _side_frame(q, side)
        ts = np.linspace(0.15, 0.85, 80, dtype="float32")[:, None]
        P = (a + (b - a) * ts)[:, None, :] + n[None, None, :] * offs[None, :, None]
        prof = np.median(sf._bilinear(Y, P[..., 0] - 0.5, P[..., 1] - 0.5), 0)
        plateau = float(np.median(prof[offs >= 0.6 * D]))
        k = np.clip(1 - prof / max(plateau, 1e-4), 0, 1)
        use = (offs <= 0.6 * D) & (k > 0.004)
        name = ("top", "right", "bottom", "left")[side]
        if k[:3].mean() < 0.015 or use.sum() < 3:
            out.append({"side": name, "k": 0.0, "w_px": 1.0})
            continue
        slope, icpt = np.polyfit(offs[use], np.log(k[use]), 1, w=k[use])
        w = float(np.clip(-1 / slope if slope < 0 else D, 0.5, D))
        out.append({"side": name, "k": round(float(np.clip(math.exp(icpt), 0, 0.8)), 3), "w_px": round(w, 2)})
    return out


def _erfc(x):
    """Complementary error function (Abramowitz-Stegun 7.1.26, |error| < 1.5e-7), numpy, no scipy."""
    x = np.asarray(x, "float64")
    z = np.abs(x)
    t = 1.0 / (1.0 + 0.3275911 * z)
    y = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + t * (-1.453152027 + t * 1.061405429)))) * np.exp(-z * z)
    return np.where(x >= 0, y, 2.0 - y)


def band(d, width, blur):
    """A black band cut along an edge (d = px inward from the edge) `width` px wide, Gaussian-blurred by `blur`: 1 at
    the edge, falling off around d = width. Tony's recipe: black fill, cut to shape, blurred."""
    return 0.5 * _erfc((np.asarray(d, "float64") - width) / (math.sqrt(2.0) * np.maximum(blur, 1e-3)))


def measure_edge_shadows(img, opening_q, pad):
    """The frame's shadows MEASURED per side on the blank insert, relative to the OPENING (the frame's hard inner
    edge; the art covers the baked shadow, so these layers must reproduce it). Darkening D(d) = 1 - Y / plateau, d px
    inward, median along the middle 70% of the side; plateau = the paper a little further in.
      hard: the frame edge's own tone where the art runs under it (d in -pad..0): the photo's dark inner wall / lip
            line, or the frame face where there is none; rebuilt crisp over the art's pad.
      soft: the shadow on the paper, fitted as a blurred black band k * band(d, width, blur) on d >= 1 px (the edge
            pixel itself is half frame); k = 0 where the paper is flat up to the edge.
    Returns [{side, hard_k, soft_k, width_px, blur_px, fit_rms, plateau}] in side order top, right, bottom, left."""
    from . import sam_frames as sf
    Y = (img @ W709).astype("float32")
    q = np.float32(opening_q)
    size = min(math.dist(q[0], q[1]), math.dist(q[0], q[3]))
    D = float(max(12.0, 0.08 * size))
    pad = float(pad)
    offs = np.arange(-max(pad, 0.5), D + 1e-6, 0.25, dtype="float32")
    widths = np.arange(-6.0, 0.5 * D + 1e-6, 0.25)
    blurs = np.geomspace(0.4, 12.0, 40)
    out = []
    for side in range(4):
        a, b, n = _side_frame(q, side)
        ts = np.linspace(0.15, 0.85, 80, dtype="float32")[:, None]
        P = (a + (b - a) * ts)[:, None, :] + n[None, None, :] * offs[None, :, None]
        prof = np.median(sf._bilinear(Y, P[..., 0] - 0.5, P[..., 1] - 0.5), 0)
        plateau = float(np.median(prof[offs >= 0.6 * D]))
        Dp = np.clip(1 - prof / max(plateau, 1e-4), 0, 1)
        under = (offs >= -max(pad, 0.5)) & (offs <= -0.25)
        hard = float(np.clip(np.median(Dp[under]), 0, 0.85))
        use = (offs >= 1.0) & (offs <= 0.6 * D)
        d, y = offs[use].astype("float64"), Dp[use].astype("float64")
        best = (float((y * y).mean()), 0.0, 0.0, 1.0)
        for wd in widths:
            phi = band(d[None, :], wd, blurs[:, None])                 # blurs x samples
            den = (phi * phi).sum(1)
            k = np.clip((phi * y).sum(1) / np.maximum(den, 1e-9), 0, 0.85)
            r = ((y[None, :] - k[:, None] * phi) ** 2).mean(1)
            i = int(r.argmin())
            if r[i] < best[0]:
                best = (float(r[i]), float(k[i]), float(wd), float(blurs[i]))
        r, k, wd, bl = best
        if k * float(band(1.0, wd, bl)) < 0.02:                         # flat paper up to the edge: no soft shadow
            k, wd, bl = 0.0, 0.0, 0.0
        out.append({"side": sf.SIDES[side], "hard_k": round(hard, 3), "soft_k": round(k, 3), "width_px": round(wd, 2),
                    "blur_px": round(bl, 2), "fit_rms": round(math.sqrt(r), 4), "plateau": round(plateau, 3)})
    return out


def sun_shade(img, insert_q, wall=None):
    """The wall's sun line measured from the photo (template_checker.sun_line, searched only on the SAM wall mask
    when one is given), continued across the opening: alpha 1 on the shade side, softened like the photo's penumbra.
    Returns (alpha, info) or (None, None)."""
    import cv2
    from .template_checker import sun_line
    H, W = img.shape[:2]
    sl = sun_line(img * 255.0, insert_q, wall=wall)
    if not sl:
        return None, None
    x1, y1, x2, y2 = sl["line"]
    gy, gx = np.mgrid[0:H, 0:W].astype("float32")
    n = np.float32([-(y2 - y1), x2 - x1])
    n /= max(float(np.linalg.norm(n)), 1e-6)
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    sd = (gx - mx) * n[0] + (gy - my) * n[1]
    Y = img @ W709
    d = max(6, int(0.02 * H))

    def at(px, py):
        return float(Y[int(np.clip(py, 0, H - 1)), int(np.clip(px, 0, W - 1))])
    lit, shade = at(mx - n[0] * d, my - n[1] * d), at(mx + n[0] * d, my + n[1] * d)
    shade_pos = shade < lit
    alpha = ((sd > 0) if shade_pos else (sd < 0)).astype("float32")
    q = np.float32(insert_q)
    soft = max(1.5, 0.012 * max(math.dist(q[0], q[3]), math.dist(q[1], q[2])))
    alpha = cv2.GaussianBlur(alpha, (0, 0), soft)
    sl["depth"] = round(float(np.clip(1 - min(lit, shade) / max(lit, shade, 1e-4), 0, 1)), 3)
    return alpha, sl


INSERT_TEXTURE_MAX = 0.03   # brightness spread (std) of a blank insert around its fitted light plane; above = a print


def key_light(img, insert_q, wall=None):
    """ONE key-light shadow with its angle MEASURED from the photo: the wall's sun line when SAM's wall mask is there,
    else the direction and depth of the light falloff across the blank insert (a plane fitted to the paper's
    brightness away from the lip shadow). Returns (alpha HxW, meta).
    Guards (Tony 2026-11-15): a sun line is trusted ONLY on SAM's wall mask (without it, a prop edge such as a plant
    leaf passed for the sun and an invented diagonal shadow was painted across the art); and when the insert is not
    blank paper (an old photo still showing a sample print) its light cannot be measured: no Light Shadow at all."""
    from . import sam_frames as sf
    H, W = img.shape[:2]
    q = np.float32(insert_q)
    Y = img @ W709
    m = sf.poly_coverage(_expand(q, -0.08), W, H) > 0.99
    ys, xs = np.nonzero(m)
    if len(xs) < 50:
        return np.zeros((H, W), "float32"), {"kind": "none", "opacity": 0.0}
    A = np.c_[xs + 0.5, ys + 0.5, np.ones_like(xs)].astype("float64")
    coef, *_ = np.linalg.lstsq(A, Y[ys, xs].astype("float64"), rcond=None)
    texture = float(np.std(Y[ys, xs] - A @ coef))
    alpha, sl, tex_sun = None, None, None
    if wall is not None:
        alpha, sl = sun_shade(img, insert_q, wall)
        if alpha is not None:                     # blank paper crossed by the sun band: plane + band explain it
            A2 = np.c_[A, alpha[ys, xs]]
            c2, *_ = np.linalg.lstsq(A2, Y[ys, xs].astype("float64"), rcond=None)
            tex_sun = float(np.std(Y[ys, xs] - A2 @ c2))
    if min(texture, tex_sun if tex_sun is not None else texture) > INSERT_TEXTURE_MAX:
        return np.zeros((H, W), "float32"), {
            "kind": "none", "opacity": 0.0, "insert_texture": round(texture, 4),
            "why": "the insert is not blank paper (a print in the photo): its light cannot be measured"}
    if alpha is not None and tex_sun <= INSERT_TEXTURE_MAX:
        return alpha, {"kind": "sun line", "deg": sl["deg"], "line": sl["line"], "measured_depth": sl["depth"],
                       "opacity": round(float(np.clip(sl["depth"], 0.06, 0.35)), 3),
                       "searched_on": "SAM wall mask", "insert_texture": round(tex_sun, 4)}
    if texture > INSERT_TEXTURE_MAX:
        return np.zeros((H, W), "float32"), {"kind": "none", "opacity": 0.0, "insert_texture": round(texture, 4),
                                             "why": "the insert's light is neither a plane nor the wall's sun band"}
    gy, gx = np.mgrid[0:H, 0:W].astype("float32")
    plane = coef[0] * (gx + 0.5) + coef[1] * (gy + 0.5) + coef[2]
    vals = plane[sf.poly_coverage(q, W, H) > 0.5]
    hi, lo = float(vals.max()), float(vals.min())
    if hi <= 1e-4 or hi - lo < 1e-4:
        return np.zeros((H, W), "float32"), {"kind": "flat", "opacity": 0.0}
    deg = math.degrees(math.atan2(-float(coef[1]), -float(coef[0])))     # direction the light falls off towards
    drop = (hi - lo) / hi
    return np.clip((hi - plane) / (hi - lo), 0, 1).astype("float32"), {
        "kind": "falloff", "deg": round(deg, 1), "measured_drop": round(drop, 3),
        "opacity": round(float(np.clip(drop, 0.02, 0.35)), 3), "insert_texture": round(texture, 4),
        "sun_line": "searched on SAM's wall mask: none" if wall is not None else "not searched (no SAM wall mask)"}


def make_layers(img, insert_q, art_q, so_px, mode, outdir, wall=None, pad=None):
    """Full-canvas RGBA layer PNGs into outdir (Tony's shadow rule: black fill only, cut to shape, blurred; the shadow
    reaches LAYER_PAD px past the art quad and the PSD layer MASK makes the exact cut). insert_q = the OPENING (frame's
    hard inner edge), art_q = the opening + `pad` px under the frame. Since the art covers the baked shadow, two frame
    layers rebuild it from measurements (measure_edge_shadows):
      Frame Hard Shadow: crisp, the frame edge's measured tone over the art's pad (d < 0), so no art shows on the wood
      Frame Edge Shadow: soft, the per-side blurred band fitted to the paper's darkening (d >= 0)
    Returns {name: file} plus "_meta" (measurements)."""
    from . import sam_frames as sf
    from .template_checker import offset_quad
    H, W = img.shape[:2]
    outdir = Path(outdir)
    q = np.float32(art_q)
    q_open = np.float32(insert_q)
    if pad is None:
        pad = max(0.0, float(np.mean(sf.side_offsets(q_open, q))))
    region = sf.poly_coverage(offset_quad(q, LAYER_PAD), W, H)
    black = np.zeros((H, W, 3), "float32")
    files, meta = {}, {}
    sides = measure_edge_shadows(img, q_open, pad)
    keep_h = np.ones((H, W), "float32")
    keep_s = np.ones((H, W), "float32")
    for s, d in zip(sides, side_distance(q_open, W, H)):
        inside = band(-d, 0.0, HARD_BLUR_PX)                    # 0 under the frame, 1 inside the opening (crisp)
        if s["hard_k"] > 0:
            keep_h *= (1 - s["hard_k"] * (1 - inside)).astype("float32")
        if s["soft_k"] > 0:
            keep_s *= (1 - s["soft_k"] * band(np.clip(d, 0, None), s["width_px"], s["blur_px"]) * inside).astype("float32")
    hard = (1 - keep_h) * region
    soft = (1 - keep_s) * region
    for name, f, a, kind in (
            ("Frame Hard Shadow", "L_hard.png", hard,
             f"the frame's hard inner edge over the art's {pad:g} px pad (measured frame-edge tone vs the paper)"),
            ("Frame Edge Shadow", "L_edge.png", soft,
             "soft shadow on the paper (per side: black band, width + blur + strength fitted to the blank insert)")):
        top = float(a.max())
        _save_rgba(black, a / max(top, 1e-6), outdir / f)
        files[name] = f
        meta[name] = {"kind": kind, "opacity": round(float(np.clip(top, 0.02, 0.9)), 3),
                      "sides": [({k: s[k] for k in ("side", "hard_k")} if name == "Frame Hard Shadow" else
                                 {k: s[k] for k in ("side", "soft_k", "width_px", "blur_px", "fit_rms")}) for s in sides]}
    meta["Frame Hard Shadow"]["pad_px"] = pad
    # key light, angle measured
    alpha, km = key_light(img, insert_q, wall)
    _save_rgba(black, alpha * region, outdir / "L_light.png")
    files["Light Shadow"] = "L_light.png"
    meta["Light Shadow"] = km
    _save_rgba(np.ones((H, W, 3), "float32"), glass(q, W, H) * region, outdir / "L_glass.png")
    files["Glass Sheen"] = "L_glass.png"
    placeholder(so_px[0], so_px[1], outdir / "placeholder.png")
    files["_meta"] = meta
    return files


def _cmd(c, p=None):
    return ["--cmd", c, "--params", json.dumps(p or {})]


def _run(settings, args):
    """photocraft-cli (tests replace this)."""
    bin_ = _cfg(settings, "photocraft_bin")
    if not shutil.which(bin_):
        raise TemplateError(f"{bin_} is not on PATH")
    try:
        r = subprocess.run([bin_, *args], capture_output=True, text=True,
                           timeout=int(_cfg(settings, "room_render_timeout_s")))
    except subprocess.TimeoutExpired:
        raise TemplateError("PhotoCraft took too long")
    errs = [ln for ln in (r.stdout + r.stderr).splitlines() if "error" in ln.lower()]
    if r.returncode or errs:
        raise TemplateError(f"PhotoCraft failed: {((r.stderr or r.stdout).strip() or '; '.join(errs))[-300:]}")
    return r.stdout


def _pts(q):
    return [[round(float(x), 3), round(float(y), 3)] for x, y in q]


def assemble(base_png, outdir, files, art_q, out_psd, settings=None):
    """The layered, hand-editable PSD (layer stack in the module docstring). Every shadow / glare layer gets a layer
    MASK cut to the art opening (anti-aliased lasso on the SAM quad -> Reveal Selection)."""
    P = lambda n: str((Path(outdir) / n).resolve())

    meta = files.get("_meta") or {}

    def place(f, name, blend="Normal", op=1.0):
        return (_cmd("file.placeEmbedded", {"path": P(f), "smartObject": False, "scale": 100})
                + _cmd("layer.setProps", {"name": name, "blend": blend, "opacity": op, "visible": True})
                + _cmd("select.lasso", {"points": _pts(art_q), "antiAlias": True})
                + _cmd("layer.layerMask.revealSelection", {}))         # (it consumes the selection)
    a = ["run", str(base_png), *_cmd("layer.setProps", {"name": BASE_NAME})]
    a += _cmd("layer.select", {"name": BASE_NAME})
    a += _cmd("file.placeEmbedded", {"path": P("placeholder.png"), "smartObject": True, "scale": 100})
    a += _cmd("layer.setProps", {"name": ART, "blend": "Normal"})
    a += _cmd("edit.transform", {"quad": _pts(art_q)})            # no selection is active here (deselect would fail)
    shadows = [n for n in ("Light Shadow", "Frame Edge Shadow", "Frame Hard Shadow") if n in files]
    for n in shadows:
        a += place(files[n], n, "Multiply", (meta.get(n) or {}).get("opacity", SHADOW_OPACITY.get(n, 0.2)))
    a += _cmd("layer.new.group", {"name": "SHADOWS"})
    for n in shadows:
        a += _cmd("layer.moveTo", {"layer": n, "target": "SHADOWS", "position": "into"})
    a += _cmd("layer.select", {"name": "SHADOWS"}) + place(files["Glass Sheen"], "Glass Sheen", "Screen", 0.08)
    a += _cmd("layer.new.group", {"name": "GLARE"})
    a += _cmd("layer.moveTo", {"layer": "Glass Sheen", "target": "GLARE", "position": "into"})
    a += ["--out", str(out_psd)]
    _run(settings, a)
    if not Path(out_psd).is_file():
        raise TemplateError("the PSD was not written")
    return Path(out_psd)


def card_verify(psd, quad, settings=None, work=None, opening=None):
    """The black / white card test on the finished PSD (shadow + glare groups hidden): the anti-aliased difference of
    the two renders is the visible art; its sub-pixel quad must match `quad` (the art quad) within card_tol_px, and no
    pixel more than 1 px inside the opening may stay uncovered (a sliver) or show art outside it. With `opening`
    (the frame's hard inner edge; Tony 2026-11-12) the art must reach the opening on every side (a gap of more than
    template_checker.EDGE_TOL_PX = a sliver of baked paper) and run under the frame by at most PAD_MAX_PX (+ the same
    tolerance); art beyond that is art over the frame. Raises TemplateError."""
    from PIL import Image
    from . import sam_frames as sf
    from .template_checker import EDGE_TOL_PX, PAD_MAX_PX
    work = Path(work or tempfile.mkdtemp())
    so = so_size(psd, settings, work)
    outs = []
    for name, v in (("blk", 0), ("wht", 255)):
        card = work / f"card_{name}.png"
        Image.new("RGB", tuple(so), (v, v, v)).save(card)
        out = work / f"cv_{name}.png"
        hide = []
        for g in ("SHADOWS", "GLARE"):
            hide += _cmd("layer.select", {"name": g}) + _cmd("layer.setProps", {"visible": False})
        _run(settings, ["run", str(psd), *_cmd("layer.select", {"name": ART}),
                        *_cmd("layer.smartObjects.replaceContents", {"path": str(card.resolve())}), *hide,
                        "--out", str(out)])
        with Image.open(out) as im:
            outs.append(np.asarray(im.convert("RGB")).astype("float32"))
    D = np.clip((outs[1] - outs[0]).mean(2) / 255.0, 0, 1)
    try:
        vq, _ = sf.fit_quad(D, np.float32(quad), R=3.0)
    except sf.QuadError as e:
        raise TemplateError(f"card test: the art edge could not be measured ({e})")
    err = sf.corner_error(vq, quad)
    H, W = D.shape
    from .template_checker import offset_quad
    op = np.float32(quad if opening is None else opening)
    inner = sf.poly_coverage(offset_quad(op, -1.0), W, H) > 0.999
    lim_out = 1.0 if opening is None else PAD_MAX_PX + 1.0
    outer = sf.poly_coverage(offset_quad(op, lim_out), W, H) < 0.001
    gap, over = int((inner & (D < 0.5)).sum()), int((outer & (D > 0.5)).sum())
    res = {"visible_quad": np.round(vq, 3).tolist(), "corner_err_px": err["per_corner_px"], "max_px": err["max_px"],
           "gap_px": gap, "over_px": over}
    why = []
    if opening is not None:
        pads = [round(x, 2) for x in sf.side_offsets(op, vq)]      # + = art runs under the frame by that much
        res["pad_px"] = dict(zip(sf.SIDES, pads))
        for s, p in zip(sf.SIDES, pads):
            if p < -EDGE_TOL_PX:
                why.append(f"{s}: a {-p:.2f} px sliver between the frame's inner edge and the art")
            elif p > PAD_MAX_PX + EDGE_TOL_PX:
                why.append(f"{s}: art runs {p:.2f} px over the frame (pad limit {PAD_MAX_PX:g} px)")
    tol = float(_cfg(settings, "card_tol_px"))
    if err["max_px"] > tol or gap or over or why:
        raise TemplateError(f"card test failed: visible art is {err['max_px']:.2f} px off the art corners "
                            f"(limit {tol:g}); {gap} px sliver, {over} px over the frame" +
                            ("; " + "; ".join(why) if why else ""))
    return res


def build_psd(scene_png, ratio, work, settings=None, box=None, presentation=None):
    """Scene image -> layered PSD in `work` (SAM corners, measured shadows, card test). Returns the manifest fields."""
    from PIL import Image
    from .rooms import true_aspect
    work = Path(work)
    with Image.open(scene_png) as im:
        rgb = np.asarray(im.convert("RGB"))
    H, W = rgb.shape[:2]
    target = rs.RATIO_VALUE[ratio]
    from .template_checker import PAD_MAX_PX, offset_quad
    canvas = presentation == "canvas"
    res, _alpha, wall = sam_detect(scene_png, work, settings, box=box, canvas=canvas)
    q = np.float32(res["corners"])               # the OPENING: the frame's hard inner edge, shadowed paper included
    asp = true_aspect(q, (W, H))
    l, r = math.dist(q[0], q[3]), math.dist(q[1], q[2])
    info = {"aspect": round(asp, 4),
            "screen_aspect": round(((math.dist(q[0], q[1]) + math.dist(q[3], q[2])) / 2) / ((l + r) / 2), 4),
            "skew": round(max(l, r) / max(min(l, r), 1), 3), "method": "sam2 + hard inner edge",
            "sam": {k: res.get(k) for k in ("model", "device", "box", "box_source", "sam", "verify", "wall_px")},
            "opening": res.get("opening"), "quad_paper": res.get("corners_paper")}
    q_open, mode = art_quad(q, asp, target)                    # >3% off the print ratio: rejected (regenerate)
    pad = 0.0 if canvas else float(_cfg(settings, "opening_pad_px"))   # canvas: no frame lip to run the art under
    if not 0 <= pad <= PAD_MAX_PX:
        raise TemplateError(f"opening_pad_px {pad:g} is outside 0..{PAD_MAX_PX:g} px")
    aq = offset_quad(q_open, pad)                              # the art runs `pad` px under the frame's inner edge
    so = so_pixels(aq, true_aspect(aq, (W, H)))                # the art quad's own true ratio: no stretch
    base = work / "base.png"
    Image.fromarray(rgb).save(base)                   # flat RGB PNG (PhotoCraft opens it as the base layer)
    files = make_layers(rgb.astype("float32") / 255, q, aq, so, mode, work, wall, pad=pad)
    psd = assemble(base, work, files, aq, work / "template.psd", settings)
    (work / "cards").mkdir(exist_ok=True)
    card = card_verify(psd, aq, settings, work / "cards", opening=q)
    return {"psd_tmp": psd, "quad_insert": np.round(q, 3).tolist(), "quad_art": np.round(aq, 3).tolist(),
            "quad_paper": res.get("corners_paper"), "opening_pad_px": pad,
            "mode": mode, "so_px": so, "so_ratio": round(so[0] / so[1], 4), "insert": info,
            "shadows": files.get("_meta"), "card_test": card,
            "canvas": [W, H], "light_from": light_side(rgb.astype("float32") @ W709, q)}


# ---------- step 1: the scene ----------

def kie_module(settings=None):
    import importlib.util
    p = _abs(_cfg(settings, "kie_edit_script"))
    if not p.is_file():
        raise TemplateError(f"kie_edit.py is missing ({p})")
    spec = importlib.util.spec_from_file_location("kie_edit_portal", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def generate_scene(prompt, out_png, settings=None, generator=None):
    """One kie.ai scene (the only call that costs credits). `generator(engine, out, prompt, aspect, res)` is
    injectable for tests. Returns kie_edit.generate's dict."""
    eng = _cfg(settings, "room_scene_engine")
    gen = generator or kie_module(settings).generate
    try:
        return gen(eng, str(out_png), prompt, _cfg(settings, "room_scene_aspect"), _cfg(settings, "room_scene_resolution"))
    except TemplateError:
        raise
    except Exception as e:  # noqa: BLE001  (kie errors are plain RuntimeErrors with a readable reason)
        raise TemplateError(str(e)[:300])


ROOM_SHORT = {"Living room": "Living_Room", "Kitchen & dining": "Kitchen_Dining", "Game room": "Game_Room",
              "Creative space": "Creative_Space"}


def save_template(settings, room, decor, ratio, scene_png, built, meta):
    """AUTO-SAVE a new scene as a template in Tony's tree (no asking). Returns (template dir, psd path)."""
    rdir = room_dir(settings, ratio, room)
    if rdir is None:
        raise TemplateError(f"no {room} folder in Room_Templates for {rs.RATIO_LABEL[ratio]}; Tony makes room folders")
    sdir = style_dir(rdir, decor, create=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = f"AI_{ROOM_SHORT.get(room, room.title().replace(' ', '_'))}_{decor}_{stamp}"
    name, k = base, 2
    while (sdir / name).exists() or (sdir / "Archive" / name).exists():
        name = f"{base}_{k}"
        k += 1
    tdir = sdir / name
    tdir.mkdir()
    psd = tdir / f"{name}_Template.psd"
    shutil.copy2(built["psd_tmp"], psd)
    shutil.copy2(scene_png, tdir / f"{name}_Scene.png")
    man = {"name": name, "kind": "ai_scene", "psd": psd.name, "scene": f"{name}_Scene.png",
           "smart_object_layer": ART, "room": room, "etsy_room": room if room in rs.ETSY_ROOMS else None,
           "decor": decor, "ratio": ratio, "print_ratio": rs.PRINT_RATIO_TAG[ratio],
           **{k: built[k] for k in ("so_px", "so_ratio", "quad_insert", "quad_art", "mode", "canvas", "light_from")},
           **{k: built[k] for k in ("quad_paper", "opening_pad_px") if k in built},
           "insert": built["insert"], "shadows": built.get("shadows"), "card_test": built.get("card_test"),
           "layers_verified": "black-fill shadows built by scene_templates.make_layers (measured, masked)",
           "base_layer": BASE_NAME, "guard_max_cover": _cfg(settings, "room_guard_max_cover"),
           "desc": f"AI scene: {rs.DECOR_WORDS.get(decor, decor)} {rs.ROOM_WORDS.get(room, room)}, blank-insert frame "
                   f"(art cover-fits the insert)",
           "created": datetime.now().isoformat(timespec="seconds"), **meta}
    (tdir / MANIFEST).write_text(json.dumps(man, indent=1) + "\n")
    return tdir, psd


# ---------- step 4: render a template with the art ----------

MAX_CROP = 0.15     # Tony 2026-11-16: a drawn frame a bit off the print ratio is fine (buyers resize); cover-fit crops up to 15%, never letterbox


def fit_cover(src, size, dest, max_crop=MAX_CROP):
    """Tony's fit rule (2026-11-10): scale the art up to COVER the whole opening, centre it, clip the excess
    left/right or top/bottom. Never stretched, never a white border. Returns the share of the art cropped off;
    raises TemplateError when that is more than `max_crop` (the frame ratio is too far from the art)."""
    from .mockups import fit_art
    from PIL import Image
    with Image.open(src) as im:
        ra = im.width / im.height
    rt = size[0] / size[1]
    crop = 1 - min(ra / rt, rt / ra)
    if max_crop is not None and crop > max_crop + 1e-9:
        raise TemplateError(f"the frame ratio {rt:.3f} is {crop:.1%} off the print ratio {ra:.3f} (limit "
                            f"{max_crop:.0%}); pick a template in the print's ratio")
    return fit_art(src, tuple(size), dest)


def print_for(arts, ratio_value, tag=None):
    """The print file for this slot: the one named for the ratio, else the nearest shape (least padding)."""
    if tag:
        hit = [a for a in arts if f"_{tag}_" in Path(a).name]
        if hit:
            return hit[0]
    from .room_templates import pick_art
    return pick_art(arts, ratio_value)


def render_psd(psd, so_px, art, out_png, settings=None, work=None, max_crop=MAX_CROP):
    """Swap the art into 'Place Artwork Here' and render. The art is cover-fit to the smart object's NATIVE pixels
    (read from the PSD; a template.json so_px can be wrong, e.g. the Wabi bedroom's 542x740 vs native 562x750).
    Returns {"fitted", "cropped", "so_px"}."""
    work = Path(work or tempfile.mkdtemp())
    fitted = work / "fitted_art.png"
    try:
        native = so_size(psd, settings, work)
    except Exception:  # noqa: BLE001  (fall back to the manifest)
        native = list(so_px)
    cropped = fit_cover(art, tuple(native), fitted, max_crop)
    _run(settings, ["run", str(psd), *_cmd("layer.select", {"name": ART}),
                    *_cmd("layer.smartObjects.replaceContents", {"path": str(fitted.resolve())}), "--out", str(out_png)])
    if not Path(out_png).is_file():
        raise TemplateError(f"{Path(out_png).name} was not written")
    return {"fitted": fitted, "cropped": cropped, "so_px": list(native)}


# ---------- manifests for Tony's own PSDs ----------

def so_size(psd, settings=None, work=None):
    from PIL import Image
    out = Path(work or tempfile.mkdtemp()) / "so.png"
    _run(settings, ["run", str(psd), *_cmd("layer.select", {"name": ART}),
                    *_cmd("layer.smartObjects.exportContents", {"path": str(out)})])
    with Image.open(out) as im:
        return list(im.size)


def measure_quad(psd, so_px, settings=None, work=None):
    """Where the art is visible in the render: render a black and a white card, diff, four corners (a prop in
    front clipping a corner is rebuilt from the long sides)."""
    import cv2
    from PIL import Image
    from .rooms import _quad_from_hull
    work = Path(work or tempfile.mkdtemp())
    outs = []
    for name, v in (("blk", 0), ("wht", 255)):
        card = work / f"card_{name}.png"
        Image.new("RGB", tuple(so_px), (v, v, v)).save(card)
        out = work / f"r_{name}.png"
        _run(settings, ["run", str(psd), *_cmd("layer.select", {"name": ART}),
                        *_cmd("layer.smartObjects.replaceContents", {"path": str(card)}), "--out", str(out)])
        with Image.open(out) as im:
            outs.append(np.asarray(im.convert("L")).astype("int16"))
    m = ((outs[1] - outs[0]) > 40).astype("uint8") * 255
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cs:
        raise TemplateError("the art area could not be measured")
    c = max(cs, key=cv2.contourArea)
    q = _order(_quad_from_hull(cv2.convexHull(c)))
    return np.round(q, 1).tolist(), [int(outs[0].shape[1]), int(outs[0].shape[0])]


def ensure_manifests(settings=None, force=False, log=print):
    """template.json for every template folder that has none (Tony's PSDs). Never touches the PSDs."""
    from .template_gallery import _col, directory_rows
    rows = directory_rows(settings)
    done, failed = 0, {}
    for t in library_templates(settings):
        if t.get("wired"):
            continue
        f = t["psd"].parent / MANIFEST
        if f.is_file() and not force:
            continue
        try:
            with tempfile.TemporaryDirectory() as td:
                row = rows.get(t["psd"].name, {})
                mm = re.match(r"(\d+)x(\d+)", _col(row, "so px") or "")
                so = [int(mm.group(1)), int(mm.group(2))] if mm else so_size(t["psd"], settings, td)
                quad, canvas = measure_quad(t["psd"], so, settings, td)
            man = {"name": t["psd"].stem, "kind": "tony_psd", "psd": t["psd"].name, "smart_object_layer": ART,
                   "room": t["room"], "decor": t["style"], "ratio": t["ratio"], "so_px": so,
                   "so_ratio": round(so[0] / so[1], 4), "quad_art": quad, "canvas": canvas, "desc": t["desc"],
                   "guard": "hue only (the template's own shadows are designed)",
                   "measured": f"{datetime.now():%Y-%m-%d}: art quad from a black vs white card render"}
            f.write_text(json.dumps(man, indent=1) + "\n")
            done += 1
            log(f"manifest: {t['rel']}")
        except Exception as e:  # noqa: BLE001
            failed[t["rel"]] = str(e)[:200]
            log(f"FAILED {t['rel']}: {e}")
    return {"written": done, "failed": failed}


def manifest_for_render(t, settings=None):
    """The manifest a library template renders with (made on the fly and saved when missing)."""
    m = t.get("manifest") or load_manifest(t["psd"])
    if m and m.get("so_px") and m.get("quad_art"):
        return m
    ensure_manifests(settings, log=lambda *_: None)
    m = load_manifest(t["psd"])
    if not m:
        raise TemplateError(f"no manifest for {t['rel']}")
    return m


if __name__ == "__main__":
    import sys
    from .db import load_config
    s = load_config("settings")
    if "--manifests" in sys.argv:
        r = ensure_manifests(s, force="--force" in sys.argv)
        print(json.dumps(r, indent=1))
    if "--available" in sys.argv:
        print(json.dumps(available_rooms(s), indent=1))
