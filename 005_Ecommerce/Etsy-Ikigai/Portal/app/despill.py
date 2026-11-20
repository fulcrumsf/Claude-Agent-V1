"""Orange despill for templates built on the orange blank insert (Tony 2026-11-17: "real art bounces its own colour,
never orange").

The AI scene is drawn with a flat onion-skin orange insert so SAM can find it. The orange also BOUNCES onto what is
next to it: the floater gap, the frame's inner lip, the canvas side edges, a mat bevel (Japandi 11x14: the bottom gap
is exactly the wood's colour lit by orange light, wood x face). Once the real art covers the insert that orange glow
no longer belongs. This is the green-screen despill idea, deterministic, no AI:

  1. geometry: a thin BAND just outside the art quad (BAND_FRAC of its short side, 8-30 px; full strength to 75% of it,
     fading to 0 at its outer edge), each pixel assigned to its nearest side by its signed distance to the quad.
  2. orange axis: the face's own colour (median of the face plateau, linear-light chromaticity rgb / Y). The
     "orange-ness" of a pixel = its chromaticity's projection on (face - neutral). This axis keeps luminance exactly
     (both ends have Y = 1), so moving along it never changes brightness.
  3. reference (per side): what the surroundings legitimately are, i.e. the most orange material that is NOT spill:
     the top REF_TOP share (by orange-ness) of the pixels in the ring just past the band (band..2.5 band, never touched
     here). Walnut, brass or an orange wall in that ring raise the reference, so they are never "despilled". In a
     corner region (outside two sides) the less orange of the two sides' references holds.
  4. edge unmix (the half-pixel orange line): pixels straddling the art edge (centre -1..+1.5 px) still hold part of the
     photo's orange face; the art covers them only partly, so a thin orange line showed along the edge. Each one is
     moved toward the clean outside colour 2.5 px further out by its measured face share (linear RGB projection), so
     what the art leaves uncovered is the gap / lip, never the face. Pixels more than COVER_TOL (0.5 px) inside
     the art edge are left alone.
  5. despill: in the band, where the orange-ness is above the reference + MARGIN of the face's, the pixel's
     chromaticity is pulled toward the reference's by just enough to bring it back to that limit; its luminance is kept
     (rgb = chromaticity x Y). Wood, wall, mat and black frames that are no more orange than their surroundings are
     not changed.

Where it lives: a pixel layer LAYER directly above the BASE (below the wrap-strip placeholder, the art and SHADOWS),
holding ONLY the corrected pixels (alpha 255 there, 0 elsewhere). It is a retouch of the photo, not a shadow, so the
black-fill shadow rule does not apply; the original BASE is untouched underneath. PhotoCraft shows the corrected scene,
every Portal render includes it (it is part of the PSD), and the checker hides it for its geometry checks (they read
the scene's own pixels) and measures leftover orange on a render with it. Written by build_psd for new builds and by
`python -m app.despill <template folder>` for existing ones (PSD + template.json backed up into the folder's Archive).

Marker colour (Tony 2026-11-19, slot-set planner): a scene planned on a WARM wall is drawn with a pale BLUE blank
insert instead of the orange one, so its bounce is blue. Everything above is colour-agnostic (the axis is the face's
own colour); only the face test's hue window depends on the marker (MARKER_HUE). marker="orange" is the default
everywhere and gives exactly the old results (golden test tests/test_marker.py). A template records a non-orange
marker as "marker" in template.json (and in its despill info); marker_of(manifest) reads it. The PSD layer keeps its
name LAYER for every marker (the checker finds it by that name).
"""
import json
import math
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

import numpy as np

LAYER = "Despill (orange bounce fix)"
VERSION = 1
BAND_FRAC = 0.025          # band width = this share of the art quad's short side ...
BAND_MIN, BAND_MAX = 8.0, 30.0   # ... clamped (px)
FADE_FROM = 0.75           # full strength up to this share of the band, then a linear fade to 0 at the band's edge
REF_OUT = 2.5              # reference ring: band .. REF_OUT x band outside the art
REF_TOP = 0.10             # reference = the most orange REF_TOP share of the candidates (protects warm wood)
MARGIN = 0.15              # allowed orange-ness above the reference, as a share of the face's own
INNER = 1.0                # px inside the art edge (pixel centres) still worked on (partly uncovered by the art)
EDGE_REACH = 1.5           # edge unmix: pixel centres -INNER .. +EDGE_REACH px from the art edge
EDGE_OUT = 2.5             # the clean outside sample, px past the art edge
EDGE_IN = 3.0              # the local face sample, px inside the art edge
COVER_TOL = 0.5            # px: pixels further than this inside the art edge are never changed
FACE_MIN_C = 15.0          # the face is the orange blank: Lab chroma at least this ...
FACE_HUE = (40.0, 100.0)   # ... with a hue in this range (onion-skin orange ~75 deg)
MARKER_HUE = {"orange": FACE_HUE, "blue": (190.0, 300.0)}   # pale sky-blue blank ~261 deg (slot planner, 2026-11-19)
FACE_FLAT = 6.0            # ... and flat (75th percentile Lab ab distance from its median; a print is not)
MIN_AXIS = 0.2             # orange axis length (chromaticity) below this: nothing to despill
LEFT_DE = 6.0              # leftover check: a pixel is visibly orange when (uncovered share x Lab dE) > this ...
LEFT_AREA = 20.0           # ... and a side FAILs at this many such pixels in display px^2 (scene fitted to ~1600 px)
DISPLAY_W = 1600.0
SIDES = ("top", "right", "bottom", "left")
W709 = np.float32([0.2126, 0.7152, 0.0722])


def lin(x):
    x = np.asarray(x, "float32")
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4).astype("float32")


def enc(x):
    x = np.clip(np.asarray(x, "float32"), 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * x ** (1 / 2.4) - 0.055).astype("float32")


def _lab(rgb01):
    import cv2
    return cv2.cvtColor(np.clip(np.float32(rgb01), 0, 1), cv2.COLOR_RGB2Lab)


def band_px(q):
    q = np.float32(q)
    short = min(float(np.linalg.norm(q[(i + 1) % 4] - q[i])) for i in range(4))
    return float(np.clip(BAND_FRAC * short, BAND_MIN, BAND_MAX))


def _sides(q):
    from .template_checker import _outward
    return [_outward(np.float32(q), s) for s in range(4)]


def _geom(q, W, H, reach):
    """Box around the quad (+reach) and per pixel: signed distance to the quad (outside +, the max over the four
    side half-planes), nearest side, position t along it."""
    q = np.float32(q)
    x0, y0 = max(0, int(math.floor(q[:, 0].min() - reach)) - 2), max(0, int(math.floor(q[:, 1].min() - reach)) - 2)
    x1, y1 = min(W, int(math.ceil(q[:, 0].max() + reach)) + 3), min(H, int(math.ceil(q[:, 1].max() + reach)) + 3)
    ys, xs = np.mgrid[y0:y1, x0:x1].astype("float32")
    P = np.stack([xs + 0.5, ys + 0.5], -1)
    sd = _sides(q)
    dist = np.stack([(P - a) @ n for a, b, n in sd], 0)
    side = dist.argmax(0)
    d = dist.max(0)
    t = np.zeros_like(d)
    for s, (a, b, n) in enumerate(sd):
        v = b - a
        m = side == s
        t[m] = ((P[m] - a) @ v) / max(float(v @ v), 1e-6)
    return (x0, y0, x1, y1), P, d, side, t, sd, dist


def marker_of(manifest):
    """The blank insert's marker colour of a template: "orange" unless its template.json says otherwise."""
    m = manifest or {}
    return m.get("marker") or (m.get("despill") or {}).get("marker") or "orange"


def face_colour(L, q, marker="orange"):
    """The face's linear colour (median of its plateau) when it is the flat blank of this marker colour (orange by
    default), else (None, why)."""
    from .template_checker import offset_quad, poly_mask
    q = np.float32(q)
    H, W = L.shape[:2]
    short = min(float(np.linalg.norm(q[(i + 1) % 4] - q[i])) for i in range(4))
    m = poly_mask(offset_quad(q, -max(6.0, 0.04 * short)), W, H)
    px = L[m]
    if len(px) < 200:
        return None, "the face is too small to measure"
    if len(px) > 60000:
        px = px[np.linspace(0, len(px) - 1, 60000).astype(int)]
    F = np.median(px, 0)
    lab = _lab(enc(px[None])[0][None])[0]
    lf = _lab(enc(F)[None, None])[0, 0]
    C, h = float(np.hypot(lf[1], lf[2])), math.degrees(math.atan2(lf[2], lf[1])) % 360
    flat = float(np.percentile(np.hypot(lab[:, 1] - lf[1], lab[:, 2] - lf[2]), 75))
    if flat > FACE_FLAT:
        return None, f"the face is not flat ({flat:.1f}): a print, not the orange blank"
    lo, hi = MARKER_HUE[marker]
    if C < FACE_MIN_C or not lo <= h <= hi:
        return None, f"the face is not the {marker} blank (Lab chroma {C:.0f}, hue {h:.0f} deg)"
    return F, ""


def _chroma(L):
    Y = L @ W709
    return L / np.maximum(Y, 1e-5)[..., None], Y


def _remap(img, X, Y):
    import cv2
    return np.stack([cv2.remap(np.ascontiguousarray(img[..., k]), (X - 0.5).astype("float32"),
                               (Y - 0.5).astype("float32"), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
                     for k in range(img.shape[-1])], -1)


def apply(rgb, art_q, marker="orange"):
    """Despill a scene (RGB uint8 / float 0..255) around the art quad. Returns (despilled uint8 RGB or None when there
    is nothing to do, info dict). marker: the blank's colour ("orange" default, "blue" on warm-wall scenes)."""
    rgb = np.asarray(rgb)[..., :3]
    H, W = rgb.shape[:2]
    q = np.float32(art_q)
    Lfull = lin(np.float32(rgb) / 255.0)
    F, why = face_colour(Lfull, q, marker)
    if F is None:
        return None, {"applied": False, "why": why}
    cF = F / max(float(F @ W709), 1e-5)
    axis = cF - 1.0                                   # face - neutral, in the Y = 1 plane (axis . W709 = 0)
    alen = float(np.linalg.norm(axis))
    if alen < MIN_AXIS:
        return None, {"applied": False, "why": f"the face is nearly neutral (orange axis {alen:.2f})"}
    u = axis / alen
    s_face = alen
    band = band_px(q)
    (x0, y0, x1, y1), P, d, side, t, sd, dist = _geom(q, W, H, REF_OUT * band + 2)
    L = Lfull[y0:y1, x0:x1]
    c, Y = _chroma(L)
    s = (c - 1.0) @ u
    # 3 reference per side: the ring just past the band (never changed here)
    cand = (d >= band) & (d <= REF_OUT * band) & (Y > 0.004)
    refs, info_sides = {}, {}

    def pick(m):
        sv = s[m]
        if len(sv) < 30:
            return None
        top = m & (s >= np.quantile(sv, 1 - REF_TOP))
        cr = np.median(c[top], 0)
        return cr / max(float(cr @ W709), 1e-5)
    pooled = pick(cand)
    if pooled is None:
        return None, {"applied": False, "why": "no surroundings to take a reference from"}
    for k in range(4):
        cr = pick(cand & (side == k))
        refs[k] = pooled if cr is None else cr
    # per pixel: its side's reference; in a corner region (outside two sides) the less orange of the two, so the
    # corner of a gap is held to the same limit as the gap next to it (Japandi: below the right strip's end)
    s_side = np.float32([(refs[k] - 1.0) @ u for k in range(4)])
    masked = np.where(dist > 0, s_side[:, None, None], np.inf)
    ref_side = np.where(np.isfinite(masked.min(0)), masked.argmin(0), side)
    c_ref = np.stack([refs[k] for k in range(4)])[ref_side]
    s_ref = (c_ref - 1.0) @ u
    s_lim = s_ref + MARGIN * s_face
    out = L.copy()
    # 4 edge unmix: the straddling pixels lose the photo's face share
    from .template_checker import offset_quad
    from .wrap_strips import coverage
    # pixels the art covers completely (more than COVER_TOL px inside its edge) stay as they are; the tolerance is
    # for PhotoCraft's own rasterising of the smart object (Japandi: its art edge sits ~0.1 px inside the quad)
    open_ = coverage(offset_quad(q, -COVER_TOL), W, H, (x0, y0, x1, y1))[y0:y1, x0:x1] < 0.999
    U = (d >= -INNER) & (d <= EDGE_REACH) & (t > -0.01) & (t < 1.01) & open_
    n_unmix = 0
    if U.any():
        nrm = np.stack([sd[k][2] for k in range(4)])[side[U]]
        dd = d[U][:, None]
        Po = P[U] + nrm * (EDGE_OUT - dd)
        Pi = P[U] + nrm * (-EDGE_IN - dd)
        o = _remap(Lfull, Po[:, 0][None], Po[:, 1][None])[0]
        fi = _remap(Lfull, Pi[:, 0][None], Pi[:, 1][None])[0]
        v = fi - o
        vv = np.sum(v * v, 1)
        f = np.clip(np.sum((L[U] - o) * v, 1) / np.maximum(vv, 1e-8), 0, 1)
        f = np.where(vv > 0.03 ** 2, f, 0.0)
        g = np.clip((s[U] - s_lim[U]) / (0.1 * s_face), 0, 1)            # only where the pixel is orange-ish
        k_ = (f * g)[:, None]
        out[U] = L[U] + k_ * (o - L[U])
        n_unmix = int((k_[:, 0] > 0.02).sum())
    # 5 despill: keep luminance, pull chromaticity toward the reference down to the limit
    w = np.clip((band - d) / ((1 - FADE_FROM) * band), 0, 1) * (d >= -INNER) * open_
    c1, Y1 = _chroma(out)
    s1 = (c1 - 1.0) @ u
    k = w * np.clip((s1 - s_lim) / np.maximum(s1 - s_ref, 1e-6), 0, 1) * (s1 > s_lim)
    c2 = c1 + k[..., None] * (c_ref - c1)
    out = np.where((k > 0)[..., None], c2 * Y1[..., None], out)
    res = np.asarray(rgb).astype("float32").copy()
    new = np.round(enc(out) * 255.0)
    region = (d >= -INNER) & (d <= band)
    res[y0:y1, x0:x1] = np.where(region[..., None], new, res[y0:y1, x0:x1])
    res = np.uint8(np.clip(res, 0, 255))
    changed = np.any(res != np.uint8(np.clip(np.round(np.float32(rgb)), 0, 255)), -1)
    s_after = ((_chroma(out)[0] - 1.0) @ u)
    for kk, nm in enumerate(SIDES):
        m = (side == kk) & (d >= 0.5) & (d <= FADE_FROM * band) & (t > 0.05) & (t < 0.95)
        info_sides[nm] = {"ref_chroma": np.round(refs[kk], 3).tolist(),
                          "s_ref": round(float((refs[kk] - 1.0) @ u), 3),
                          "s_band_before": round(float(np.median(s[m])), 3) if m.any() else None,
                          "s_band_after": round(float(np.median(s_after[m])), 3) if m.any() else None,
                          "changed_px": int(changed[y0:y1, x0:x1][side == kk].sum())}
    info = {"applied": bool(changed.any()), "version": VERSION, "band_px": round(band, 2),
            "face_rgb": [int(round(float(x))) for x in enc(F) * 255], "orange_axis": round(s_face, 3),
            "margin": MARGIN, "changed_px": int(changed.sum()), "unmixed_px": n_unmix, "sides": info_sides}
    if marker != "orange":
        info["marker"] = marker
    return (res if changed.any() else None), info


def layer_png(rgb, despilled, path):
    """The PSD layer: the corrected pixels only (alpha 255 where they differ from the scene, 0 elsewhere)."""
    from PIL import Image
    a = np.asarray(rgb)[..., :3]
    m = np.any(despilled != a, -1)
    rgba = np.dstack([np.where(m[..., None], despilled, 0), np.where(m, 255, 0)]).astype("uint8")
    Image.fromarray(rgba, "RGBA").save(path)
    return Path(path)


def leftover(rgb, art_q, exclude=(), marker="orange"):
    """The checker's leftover-orange measure on a render of the base (art hidden): what the despill above would still
    change there, as Lab dE x the share of each pixel the art leaves uncovered. `exclude` = polygons drawn over in
    every render (the canvas wrap strips). Per side FAIL when the visibly orange pixels (> LEFT_DE) cover LEFT_AREA
    display px^2 or more (the scene fitted to ~1600 px wide). Returns {status, reason, sides, ...}."""
    from .wrap_strips import coverage
    rgb = np.asarray(rgb)[..., :3]
    H, W = rgb.shape[:2]
    ds, info = apply(rgb, art_q, marker)
    if not info.get("version"):
        return {"status": "skip", "reason": info.get("why", ""), "sides": {}}
    if ds is None:
        return {"status": "pass", "reason": "", "sides": {}, "orange_px": 0}
    q = np.float32(art_q)
    band = band_px(q)
    (x0, y0, x1, y1), P, d, side, t, sd, _ = _geom(q, W, H, band + 2)
    box = (x0, y0, x1, y1)
    vis = 1.0 - coverage(q, W, H, box)[y0:y1, x0:x1]
    for poly in exclude or ():
        vis = vis * (coverage(np.float32(poly), W, H, box)[y0:y1, x0:x1] < 0.5)
    a = _lab(np.float32(rgb[y0:y1, x0:x1]) / 255.0)
    b = _lab(np.float32(ds[y0:y1, x0:x1]) / 255.0)
    dE = np.linalg.norm(a - b, axis=-1) * vis
    hit = dE > LEFT_DE
    scale = (DISPLAY_W / W) ** 2
    sides, why = {}, []
    for k, nm in enumerate(SIDES):
        n = int((hit & (side == k)).sum())
        area = round(n * scale, 1)
        st = {"orange_px": n, "display_px2": area,
              "max_dE": round(float(dE[side == k].max()), 1) if (side == k).any() else 0.0}
        if area >= LEFT_AREA:
            st["status"] = "fail"
            why.append(f"{nm}: {n} px of orange spill still visible outside the art ({area:g} display px^2, up to "
                       f"dE {st['max_dE']:g}; limit {LEFT_AREA:g})")
        else:
            st["status"] = "pass"
        sides[nm] = st
    return {"status": "fail" if why else "pass", "reason": "; ".join(why), "sides": sides,
            "orange_px": int(hit.sum()), "limit_display_px2": LEFT_AREA, "limit_dE": LEFT_DE}


def base_for(scene_rgb, manifest):
    """The base the Portal renders on: the scene, despilled when the template has the despill layer."""
    if not (manifest or {}).get("despill", {}).get("applied"):
        return scene_rgb
    ds, _ = apply(scene_rgb, manifest["quad_art"], marker_of(manifest))
    return scene_rgb if ds is None else ds


# ---------- adding the layer to an existing template ----------

def add_to_template(tdir, settings=None, run=None, log=print):
    """Despill an existing template: back the PSD and template.json up into the folder's existing Archive, bake the
    corrected pixels as LAYER directly above the BASE and record "despill" in template.json. The smart object is not
    touched (so_px unchanged). Returns the despill info (applied False when there is nothing to do)."""
    from PIL import Image
    from . import scene_templates as stp
    from . import template_checker as tc
    from .wrap_strips import _free_name
    tdir = Path(tdir)
    mf = tdir / stp.MANIFEST
    man = json.loads(mf.read_text())
    psd = tdir / man["psd"]
    rgb = np.asarray(Image.open(tdir / man["scene"]).convert("RGB"))
    ds, inf = apply(rgb, man["quad_art"], marker_of(man))
    if ds is None:
        log(f"no despill: {inf.get('why') or 'no orange spill around the art'}")
        return inf
    arch = tdir / "Archive"
    if not arch.is_dir():
        raise stp.TemplateError(f"{arch} is missing (agents never create folders; Tony makes Archive folders)")
    stamp = datetime.now().strftime("%Y%m%d")
    names = [l.get("name") for l in tc.flatten(tc.info(psd, settings).get("layers"))]
    backups = []
    if LAYER not in names:
        import filecmp
        same = [p for p in sorted(arch.glob(f"{psd.stem}_before_despill_*.psd")) if filecmp.cmp(p, psd, shallow=False)]
        if same:                                      # this exact PSD is already backed up: no second copy
            b_psd = same[0]
        else:
            b_psd = _free_name(arch, f"{psd.stem}_before_despill_{stamp}.psd")
            shutil.copy2(psd, b_psd)
        backups.append(f"Archive/{b_psd.name}")
    b_js = _free_name(arch, f"template_before_despill_{stamp}.json")
    shutil.copy2(mf, b_js)
    backups.append(f"Archive/{b_js.name}")
    if LAYER not in names:
        run = run or stp._run
        with tempfile.TemporaryDirectory() as td:
            png = layer_png(rgb, ds, Path(td) / "L_despill.png")
            out = Path(td) / "with_despill.psd"
            run(settings, ["run", str(psd), *stp._cmd("layer.select", {"name": stp.BASE_NAME}),
                           *stp._cmd("file.placeEmbedded", {"path": str(png.resolve()), "smartObject": False,
                                                            "scale": 100}),
                           *stp._cmd("layer.setProps", {"name": LAYER, "blend": "Normal", "opacity": 1.0,
                                                        "visible": True}),
                           "--out", str(out)])
            if not out.is_file():
                raise stp.TemplateError("the PSD with the despill layer was not written")
            shutil.copyfile(out, psd)
        psd.touch()                                   # new mtime: the gallery's thumbnail cache refreshes
    else:      # re-measured: the PSD keeps its layer (same code + same scene = the same pixels)
        log("the PSD already has the despill layer: only template.json is refreshed")
    inf["layer"] = LAYER
    inf["added"] = {"when": datetime.now().isoformat(timespec="seconds"),
                    "backups": list(dict.fromkeys(list((man.get("despill") or {}).get("added", {}).get("backups")
                                                       or []) + backups)),
                    "why": "orange bounce from the blank insert removed (Tony 2026-11-17)", "credits": 0}
    man["despill"] = inf
    mf.write_text(json.dumps(man, indent=1) + "\n")
    log(f"despill: {inf['changed_px']} px corrected ({inf['unmixed_px']} on the art edge); backups {', '.join(backups)}")
    return inf


if __name__ == "__main__":
    import sys
    from .db import load_config
    for t_ in sys.argv[1:]:
        add_to_template(t_, load_config("settings"))
