"""Spike: build a layered room-mockup TEMPLATE PSD from a magenta-panel scene plate, headless in PhotoCraft.

python build_template.py <plate.png> <out_dir> [--light left|right] [--art <print.jpg>]

Python (numpy/cv2) prepares the layer pixels (geometry from the plate's magenta panel), photocraft-cli assembles
them into a PSD with groups, blend modes, two instances of one 'Place Artwork Here' smart object (no-mat / mat),
and clipped hue/sat wall-colour adjustment layers.
"""
import json, math, subprocess, sys, time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "Portal" / "app").is_dir()) / "Portal"))   # Etsy-Ikigai/Portal
from app import rooms  # noqa: E402

Image.MAX_IMAGE_PIXELS = None
CLI = "photocraft-cli"

FRAMES = {   # albedo (linear-ish 0..1), grain strength
    "Oak": ((0.82, 0.60, 0.36), 0.20),
    "Walnut": ((0.36, 0.23, 0.15), 0.18),
    "Black": ((0.075, 0.07, 0.068), 0.02),
    "White": ((0.93, 0.92, 0.89), 0.015),
}
RAIL = 0.032          # frame rail width, fraction of the panel height (thin ~2 cm frame on a 60-70 cm piece)
MAT = 0.085           # mat border, fraction of panel height (bottom gets a little more)
SS = 1600             # board-space raster height (px) for the layer art before warping


def luma(x):
    return x @ np.array([0.299, 0.587, 0.114], "float32")


def save_rgba(rgb, a, path):
    out = np.dstack([np.clip(rgb, 0, 1), np.clip(a, 0, 1)])
    Image.fromarray((out * 255).round().astype("uint8"), "RGBA").save(path)


def board_geometry(plate):
    rgb = np.array(Image.open(plate).convert("RGB"))
    H, W = rgb.shape[:2]
    quad, info = rooms.find_frame(rgb, min_fill=0.7)
    if quad is None:
        raise SystemExit(f"panel not found: {info}")
    asp = info["aspect"]
    BW, BH = asp * SS, SS
    src = np.array([[0, 0], [BW, 0], [BW, BH], [0, BH]], "float32")
    Hm = cv2.getPerspectiveTransform(src, quad.astype("float32"))
    return rgb, quad, info, (BW, BH), Hm


def warp(img, Hm, W, H, interp=cv2.INTER_LINEAR, ss=2):
    """Perspective warp, supersampled ss x and area-downscaled so slanted edges are anti-aliased."""
    S = np.diag([ss, ss, 1.0]) @ Hm
    big = cv2.warpPerspective(img, S, (W * ss, H * ss), flags=interp, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    return cv2.resize(big, (W, H), interpolation=cv2.INTER_AREA)


def rect_edge_dist(xx, yy, x0, y0, x1, y1):
    """Distance to the boundary of an axis-aligned rectangle (not to its infinite edge lines)."""
    inside = (xx >= x0) & (xx <= x1) & (yy >= y0) & (yy <= y1)
    din = np.minimum.reduce([xx - x0, x1 - xx, yy - y0, y1 - yy])
    dx = np.maximum.reduce([x0 - xx, np.zeros_like(xx), xx - x1])
    dy = np.maximum.reduce([y0 - yy, np.zeros_like(yy), yy - y1])
    return np.where(inside, din, np.sqrt(dx ** 2 + dy ** 2))


def rect_mask(BW, BH, x0, y0, x1, y1):
    m = np.zeros((int(math.ceil(BH)), int(math.ceil(BW))), "float32")
    cv2.rectangle(m, (int(round(x0)), int(round(y0))), (int(round(x1)) - 1, int(round(y1)) - 1), 1.0, -1)
    return m


def wall_mask(rgb, obj, wallring, small=1024, tol=1.6):
    """Wall pixels: floating-range flood fill on a smoothed, downscaled copy (copes with the light gradient across
    a wall), seeded from the wall ring around the panel; the panel is a barrier. Smoothed back up to full size."""
    H, W = rgb.shape[:2]
    sm = cv2.resize(cv2.bilateralFilter(rgb, 9, 30, 9), (small, small), interpolation=cv2.INTER_AREA)
    sm = cv2.GaussianBlur(sm, (0, 0), 1.0)
    bar = cv2.resize(cv2.dilate(obj, np.ones((9, 9), "uint8")), (small, small), interpolation=cv2.INTER_NEAREST) > 0
    sm[bar] = (0, 255, 0)
    edges = cv2.Canny(cv2.cvtColor(sm, cv2.COLOR_RGB2GRAY), 18, 45)          # baseboard / furniture outlines
    sm[cv2.dilate(edges, np.ones((2, 2), "uint8")) > 0] = (0, 255, 0)
    seeds = np.argwhere(cv2.resize(wallring.astype("uint8"), (small, small), interpolation=cv2.INTER_NEAREST) > 0)
    rng = np.random.default_rng(0)
    acc = np.zeros((small, small), "uint8")
    for y, x in seeds[rng.choice(len(seeds), min(40, len(seeds)), replace=False)]:
        if acc[y, x]:
            continue
        m = np.zeros((small + 2, small + 2), "uint8")
        cv2.floodFill(sm.copy(), m, (int(x), int(y)), 0, (tol,) * 3, (tol,) * 3,
                      4 | cv2.FLOODFILL_MASK_ONLY | (255 << 8))
        got = m[1:-1, 1:-1]
        if got.sum() / 255 > 0.01 * small * small:
            acc |= got
    acc = cv2.morphologyEx(acc, cv2.MORPH_CLOSE, np.ones((5, 5), "uint8"))
    # fill enclosed specks (texture) but not real holes: holes smaller than 0.2 % of the image
    n, lbl, st, _ = cv2.connectedComponentsWithStats((acc == 0).astype("uint8"), connectivity=4)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] < 0.002 * small * small:
            acc[lbl == i] = 255
    up = cv2.resize(acc.astype("float32") / 255, (W, H), interpolation=cv2.INTER_CUBIC)
    up = cv2.GaussianBlur(up, (0, 0), 4.0)
    wall = ((up > 0.5) * 255).astype("uint8")
    wall[obj > 0] = 0
    return wall


def main():
    plate = Path(sys.argv[1]); out = Path(sys.argv[2]); out.mkdir(exist_ok=True)
    light = sys.argv[sys.argv.index("--light") + 1] if "--light" in sys.argv else "left"
    art_src = Path(sys.argv[sys.argv.index("--art") + 1]) if "--art" in sys.argv else None
    t0 = time.time()
    rgb, quad, info, (BW, BH), Hm = board_geometry(plate)
    H, W = rgb.shape[:2]
    sc = rgb.astype("float32") / 255
    bw, bh = int(math.ceil(BW)), int(math.ceil(BH))

    # ---------- panel masks: front face (quad) and the whole magenta object (front + visible side edge) ----------
    front = cv2.fillConvexPoly(np.zeros((H, W), "uint8"), quad.round().astype("int32"), 255)
    loose = rooms.loose_magenta(rgb).astype("uint8") * 255
    near = cv2.dilate(front, np.ones((41, 41), "uint8"))
    side = ((loose > 0) & (near > 0) & (front == 0)).astype("uint8") * 255
    side = cv2.morphologyEx(side, cv2.MORPH_OPEN, np.ones((3, 3), "uint8"))
    obj = cv2.dilate(np.maximum(front, side), np.ones((5, 5), "uint8"))        # 2 px over the pink AA fringe
    objf = obj > 0

    # ---------- BASE: plate with the panel turned into neutral 'lit white paper' (the shading the layers multiply)
    V = (sc[..., 0] + sc[..., 2]) / 2
    mag = (cv2.erode(front, np.ones((9, 9), "uint8")) > 0) & rooms.magenta_mask(rgb)
    p95 = float(np.percentile(V[mag], 95))
    L = np.clip(V / p95, 0.25, 1.05)
    m = mag.astype("float32")
    fillL = cv2.GaussianBlur(L * m, (0, 0), 9) / np.maximum(cv2.GaussianBlur(m, (0, 0), 9), 1e-4)
    L = np.where(mag, L, fillL)
    L = np.where(side > 0, np.clip(V / p95, 0.25, 1.0), L)                       # the side edge keeps its own shade
    L = cv2.GaussianBlur(L, (0, 0), 1.2)
    # wall sample just outside the panel -> exposure (paper white = 0.92 x lit wall) and white balance
    c = quad.mean(axis=0)
    ring = cv2.fillConvexPoly(np.zeros((H, W), "uint8"), (c + (quad - c) * 1.35).round().astype("int32"), 255)
    ring = (ring > 0) & ~(cv2.dilate(obj, np.ones((15, 15), "uint8")) > 0)
    satv = (sc.max(2) - sc.min(2)) / np.maximum(sc.max(2), 1e-3)
    wallring = ring & (satv < 0.35)
    wl = luma(sc)[wallring]
    wall95 = float(np.percentile(wl, 95))
    lit = wallring & (luma(sc) >= np.percentile(wl, 75))
    wrgb = sc[lit].mean(0)
    tint = wrgb / max(float(luma(wrgb)), 1e-3)
    tint = 1 + 0.6 * (tint - 1); tint = tint / float(luma(tint))
    white = 0.92 * wall95 * tint
    base = sc.copy()
    # magenta bounce light on the floor/wall next to the panel: keep each pixel's brightness, take the chroma
    # of the surroundings a little farther out
    band = (cv2.dilate(obj, np.ones((71, 71), "uint8")) > 0) & ~objf
    farr = (cv2.dilate(obj, np.ones((161, 161), "uint8")) > 0) & ~band & ~objf
    rg = (sc[..., 0] + 0.02) / (sc[..., 1] + 0.02); bg = (sc[..., 2] + 0.02) / (sc[..., 1] + 0.02)
    ref_rg = np.median(rg[farr]); ref_bg = np.median(bg[farr])
    spill = band & ((rg - ref_rg > 0.06) | (bg - ref_bg > 0.06))
    if spill.any():
        g = sc[..., 1]
        fix = np.stack([g * ref_rg, g, g * ref_bg], -1)
        fix = fix * (luma(sc) / np.maximum(luma(fix), 1e-4))[..., None]
        sm_sp = cv2.GaussianBlur(spill.astype("float32"), (0, 0), 3)[..., None]
        base = base * (1 - sm_sp) + fix * sm_sp
    lit_white = L[..., None] * white[None, None, :]

    # ---------- board-space geometry ----------
    r = RAIL * BH
    inner = (r, r, BW - r, BH - r)                                              # no-mat art = whole inner opening
    iw, ih = inner[2] - inner[0], inner[3] - inner[1]
    art_aspect = iw / ih
    mb = MAT * BH
    ow, oh = iw - 2 * mb, ih - 2 * mb * 1.1                                     # mat opening (bottom-weighted)
    if ow / oh > art_aspect:
        ow = oh * art_aspect
    else:
        oh = ow / art_aspect
    ox0 = (BW - ow) / 2
    oy0 = inner[1] + (ih - oh) / 2 - mb * 0.1
    mat_open = (ox0, oy0, ox0 + ow, oy0 + oh)

    def to_img(pts):
        p = cv2.perspectiveTransform(np.asarray(pts, "float32").reshape(-1, 1, 2), Hm).reshape(-1, 2)
        return [[round(float(x), 2), round(float(y), 2)] for x, y in p]

    q_nomat = to_img([[inner[0], inner[1]], [inner[2], inner[1]], [inner[2], inner[3]], [inner[0], inner[3]]])
    q_mat = to_img([[mat_open[0], mat_open[1]], [mat_open[2], mat_open[1]], [mat_open[2], mat_open[3]],
                    [mat_open[0], mat_open[3]]])
    so_h = 2400
    so_size = (round(so_h * art_aspect), so_h)

    # light direction sign: +1 light from the left
    sgn = 1 if light == "left" else -1
    yy, xx = np.mgrid[0:bh, 0:bw].astype("float32")

    # ---------- FRAME albedo layers (multiply over the lit-white panel) ----------
    rails = np.ones((bh, bw), "float32"); rails[int(r):int(BH - r), int(r):int(BW - r)] = 0
    # rail facing: top lit, light-side rail lit, the others a touch darker (moulding catches the window)
    face = np.ones((bh, bw), "float32")
    face[(yy > BH - r)] = 0.86
    face[(xx > BW - r) if sgn > 0 else (xx < r)] = 0.9
    face[(xx < r) if sgn > 0 else (xx > BW - r)] = 1.04
    # inner lip line and outer arris
    d_in = rect_edge_dist(xx, yy, r, r, BW - r, BH - r)
    d_out = np.minimum.reduce([xx, BW - xx, yy, BH - yy])
    face *= 1 - 0.35 * np.exp(-(d_in / (0.0025 * BH)) ** 2)
    face *= 1 + 0.10 * np.exp(-(d_out / (0.002 * BH)) ** 2)
    rng = np.random.default_rng(3)
    noise = rng.normal(0, 1, (bh // 4 + 1, bw // 4 + 1)).astype("float32")
    gh = cv2.resize(cv2.GaussianBlur(cv2.resize(noise, (bw, bh)), (0, 0), sigmaX=40, sigmaY=1.2), (bw, bh))  # horiz grain
    gv = cv2.resize(cv2.GaussianBlur(cv2.resize(noise.T.copy(), (bw, bh)), (0, 0), sigmaX=1.2, sigmaY=40), (bw, bh))
    horiz = (yy < r) | (yy > BH - r)
    grain = np.where(horiz, gh, gv); grain = grain / (np.abs(grain).max() + 1e-6)
    rails_img = warp(rails, Hm, W, H)
    sidef = (side > 0).astype("float32")
    sidef = cv2.GaussianBlur(sidef, (0, 0), 0.8)
    # frame alpha = rails (front) + side edge + the fringe ring outside the quad
    # outer lip: the quad grown 2 px, drawn anti-aliased (covers the pink edge pixels without stair steps)
    cq = quad.mean(axis=0)
    grown = quad + (quad - cq) / np.linalg.norm(quad - cq, axis=1, keepdims=True) * 2.5
    ga = cv2.fillConvexPoly(np.zeros((H, W), "uint8"), (grown * 16).round().astype("int32"), 255,
                            lineType=cv2.LINE_AA, shift=4).astype("float32") / 255
    fringe = np.clip(ga - rails_img - warp(np.ones((bh, bw), "float32"), Hm, W, H), 0, 1)
    frame_a = np.clip(rails_img + sidef + fringe, 0, 1)
    objA = np.clip(ga + sidef, 0, 1)[..., None]                              # soft panel coverage
    base = base * (1 - objA) + lit_white * objA
    Image.fromarray((np.clip(base, 0, 1) * 255).round().astype("uint8")).save(out / "L_base.png")
    for name, (alb, gs) in FRAMES.items():
        a = np.array(alb, "float32")
        col = a[None, None, :] * (face * (1 + gs * grain))[..., None]
        col_img = warp(col, Hm, W, H)
        side_col = a * 0.62
        full = np.where((sidef > 0.5)[..., None] | (fringe > 0)[..., None], side_col[None, None, :], col_img)
        save_rgba(full, frame_a, out / f"L_frame_{name.lower()}.png")
    # lip shadow: the frame's inner edge shades what is inside it (light side rails cast it)
    lipd = np.where(True, 0, 0)
    dl = (xx - r) if sgn > 0 else ((BW - r) - xx)
    dt = yy - r
    lip = np.ones((bh, bw), "float32")
    inside = (xx > r) & (xx < BW - r) & (yy > r) & (yy < BH - r)
    lip = np.where(inside, (0.80 + 0.20 * np.clip(dl / (0.022 * BH), 0, 1) ** 0.7) *
                   (0.88 + 0.12 * np.clip(dt / (0.014 * BH), 0, 1) ** 0.7), 1.0)
    lip_img = warp(lip, Hm, W, H); inside_img = warp(inside.astype("float32"), Hm, W, H)
    save_rgba(np.repeat(lip_img[..., None], 3, 2), inside_img, out / "L_lip.png")

    # ---------- MAT ----------
    matm = rect_mask(BW, BH, *inner) - rect_mask(BW, BH, *mat_open)
    matm = np.clip(matm, 0, 1)
    matcol = np.ones((bh, bw, 3), "float32") * np.array([0.965, 0.955, 0.925], "float32")
    # bevel: the cut edge of the mat shows a thin bright (light side) / dark (far side) line
    dbev = rect_edge_dist(xx, yy, *mat_open)
    bev = np.exp(-(dbev / (0.0018 * BH)) ** 2)
    far = (np.abs(xx - mat_open[2]) < np.abs(xx - mat_open[0])) if sgn > 0 else (np.abs(xx - mat_open[0]) < np.abs(xx - mat_open[2]))
    matcol *= (1 - 0.18 * bev * far + 0.05 * bev * ~far)[..., None]
    matm_b = np.clip(matm + 0.999 * (bev > 0.3) * (matm == 0) * 0, 0, 1)
    save_rgba(warp(matcol, Hm, W, H), warp(matm_b, Hm, W, H), out / "L_mat.png")
    # mat opening shadow on the art (a 4-ply mat is thick): light-side edge
    inopen = (xx > mat_open[0]) & (xx < mat_open[2]) & (yy > mat_open[1]) & (yy < mat_open[3])
    dlm = (xx - mat_open[0]) if sgn > 0 else (mat_open[2] - xx)
    mlip = np.where(inopen, (0.86 + 0.14 * np.clip(dlm / (0.008 * BH), 0, 1)) *
                    (0.92 + 0.08 * np.clip((yy - mat_open[1]) / (0.006 * BH), 0, 1)), 1.0)
    save_rgba(np.repeat(warp(mlip, Hm, W, H)[..., None], 3, 2), warp(inopen.astype("float32"), Hm, W, H),
              out / "L_mat_lip.png")

    # ---------- GLASS: faint diagonal sheen + soft window reflection, Screen ----------
    glass_in = inside.astype("float32")
    u, v = xx / BW, yy / BH
    band = np.exp(-(((u * 0.9 + v * 0.55) - 0.55) / 0.10) ** 2) * 0.9 + np.exp(-(((u * 0.9 + v * 0.55) - 0.78) / 0.035) ** 2) * 0.5
    refl = cv2.GaussianBlur(((np.abs(((u - 0.15) * 3) % 1 - 0.5) < 0.42) & (v < 0.55) & (u < 0.6)).astype("float32"),
                            (0, 0), 0.03 * BH) * 0.35
    sheen = np.clip(band + refl, 0, 1)
    warm = np.array([1.0, 0.97, 0.92], "float32")
    save_rgba(warp(sheen[..., None] * warm[None, None, :], Hm, W, H), warp(glass_in, Hm, W, H), out / "L_glass.png")

    # ---------- WALL mask (pixels that are wall: colour close to the wall sample, connected, not the panel) ----------
    wall = wall_mask(rgb, obj, wallring)
    wallf = cv2.GaussianBlur(wall, (0, 0), 1.5).astype("float32") / 255
    save_rgba(sc, wallf, out / "L_wall_cutout.png")
    Image.fromarray(wall).save(out / "wall_mask.png")

    # ---------- SHADOW overlays: computed in the panel's plane (= the wall plane), so they line up across both ----
    # 'lit' = sun reaches it (wall + panel only); everything else sits at shade level d (one consistent light story)
    # shadow receivers: wall + panel, closed so thin dark strips next to the panel (contact shade) are included
    rc = cv2.morphologyEx(np.maximum(wall, obj), cv2.MORPH_CLOSE, np.ones((45, 45), "uint8"))
    recv = np.clip(cv2.GaussianBlur(rc, (0, 0), 3).astype("float32") / 255 + (obj > 0) + frame_a, 0, 1)
    ext = 2.2                                                                     # cover wall beyond the panel
    def plane_pattern(fn, blur):
        # rasterise fn(x,y) over an extended board-space canvas, then warp to the image with an offset homography
        ow_, oh_ = int(bw * (1 + 2 * ext * BH / BW * 0.5)), int(bh * (1 + ext))
        offx, offy = (ow_ - bw) / 2, (oh_ - bh) / 2
        Y, X = np.mgrid[0:oh_, 0:ow_].astype("float32")
        pat = fn((X - offx) / BH, (Y - offy) / BH).astype("float32")
        pat = cv2.GaussianBlur(pat, (0, 0), blur * BH)
        T = np.array([[1, 0, -offx], [0, 1, -offy], [0, 0, 1]], "float64")
        return cv2.warpPerspective(pat, Hm @ T, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)

    def frame_cast(dx, dy, blur):
        # the panel's own sun shadow on the wall, offset away from the light
        def f(x, y):
            return (((x - dx * sgn) > 0) & ((x - dx * sgn) < BW / BH) & ((y - dy) > 0) & ((y - dy) < 1)).astype("float32")
        return plane_pattern(f, blur)

    shear = 0.45 * sgn                                                            # sun from upper side: skewed grid
    def panes(x, y):
        xs = x - shear * (y - 0.2)
        px0, px1, py0, py1 = -0.55, 0.62, -0.25, 0.78
        inwin = (xs > px0) & (xs < px1) & (y > py0) & (y < py1)
        bar = 0.028
        cols = np.abs(((xs - px0) / ((px1 - px0) / 2)) % 1 - 0.5) > 0.5 - bar / ((px1 - px0) / 2)
        rows = np.abs(((y - py0) / ((py1 - py0) / 3)) % 1 - 0.5) > 0.5 - bar / ((py1 - py0) / 3)
        return inwin & ~cols & ~rows

    def dapple(x, y):
        rr = np.random.default_rng(11)
        img = np.zeros_like(x)
        h_, w_ = x.shape
        x0, x1, y0, y1 = float(x.min()), float(x.max()), float(y.min()), float(y.max())
        leaves = np.zeros((h_, w_), "uint8")
        for _ in range(900):
            cx, cy = rr.uniform(-0.6, 1.3), rr.uniform(-0.4, 0.9)
            a, b = rr.uniform(0.02, 0.06), rr.uniform(0.008, 0.022)
            ang = rr.uniform(0, 180)
            px = (cx - x0) / (x1 - x0) * (w_ - 1); py = (cy - y0) / (y1 - y0) * (h_ - 1)
            sx = (w_ - 1) / (x1 - x0)
            cv2.ellipse(leaves, (int(px), int(py)), (max(1, int(a * sx)), max(1, int(b * sx))), ang, 0, 360, 255, -1)
        # sun only through the gaps, inside a soft window-shaped patch
        xs = x - 0.3 * sgn * (y - 0.2)
        patch = (xs > -0.5) & (xs < 0.95) & (y > -0.3) & (y < 0.85)
        return patch & (leaves == 0)

    def soft(x, y):
        # a broad soft-edged sun wedge (window reveal edge), no bars
        xs = x - 0.6 * sgn * (y - 0.3)
        return (xs > -0.9) & (xs < 0.45) & (y > -0.6) & (y < 1.2)

    variants = {
        "panes": dict(fn=panes, blur=0.006, d=0.80, cast=(0.035, 0.03, 0.006), shade=(0.80, 0.80, 0.85)),
        "dapple": dict(fn=dapple, blur=0.010, d=0.82, cast=(0.035, 0.03, 0.010), shade=(0.82, 0.83, 0.86)),
        "soft": dict(fn=soft, blur=0.07, d=0.80, cast=(0.04, 0.03, 0.02), shade=(0.79, 0.80, 0.85)),
    }
    for name, vv in variants.items():
        sun = plane_pattern(lambda x, y: vv["fn"](x, y).astype("float32"), vv["blur"])
        cast = frame_cast(*vv["cast"])
        wall_only = np.clip(wallf - (obj > 0), 0, 1)
        sun = sun * recv * (1 - cast * wall_only * 0.9)                         # panel shadow on the wall
        shade = np.array(vv["shade"], "float32")
        mult = shade[None, None, :] + (1 - shade)[None, None, :] * sun[..., None]
        save_rgba(mult, np.ones((H, W), "float32"), out / f"L_shadow_{name}.png")
        warm_lift = np.array([1.0, 0.86, 0.66], "float32") * 0.55
        save_rgba(np.broadcast_to(warm_lift, (H, W, 3)), sun * 0.9, out / f"L_sun_{name}.png")

    # ---------- smart-object placeholder (a numbered grid, so the perspective can be checked) ----------
    ph = np.full((so_size[1], so_size[0], 3), 235, "uint8")
    for k in range(0, so_size[0], 100):
        ph[:, k:k + 3] = 120
    for k in range(0, so_size[1], 100):
        ph[k:k + 3, :] = 120
    Image.fromarray(ph).save(out / "placeholder_art.png")

    meta = {"plate": str(plate), "panel_quad": quad.round(2).tolist(), "panel_aspect": round(float(info["aspect"]), 4),
            "art_aspect": round(art_aspect, 4), "smart_object_px": list(so_size), "quad_nomat": q_nomat,
            "quad_mat": q_mat, "wall95": round(wall95, 3), "light_from": light, "prep_s": round(time.time() - t0, 1)}
    (out / "template.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps(meta, indent=1))
    assemble(out, meta)


def cmd(c, p=None):
    return ["--cmd", c, "--params", json.dumps(p or {})]


def assemble(out, meta):
    """photocraft-cli: one run that builds the whole layered PSD."""
    P = lambda n: str((out / n).resolve())
    a = [CLI, "run", P("L_base.png")]
    a += cmd("layer.setProps", {"name": "BASE (scene plate, panel = lit white)"})

    def place(fname, name, blend="Normal", opacity=1.0, visible=True):
        return (cmd("file.placeEmbedded", {"path": P(fname), "smartObject": False, "scale": 100})
                + cmd("layer.setProps", {"name": name, "blend": blend, "opacity": opacity, "visible": visible}))

    # WALL COLOUR: cutout of the wall + hue/sat layers clipped to it (hidden by default)
    a += place("L_wall_cutout.png", "Wall Mask (wall pixels)")
    walls = [("Wall Sage", {"hue": 95, "saturation": 18, "lightness": -6, "colorize": True}),
             ("Wall Terracotta", {"hue": 18, "saturation": 30, "lightness": -10, "colorize": True}),
             ("Wall Dusty Blue", {"hue": 210, "saturation": 16, "lightness": -6, "colorize": True}),
             ("Wall Warm Greige", {"hue": 35, "saturation": 12, "lightness": -12, "colorize": True})]
    a += cmd("layer.new.group", {"name": "WALL COLOUR"})
    a += cmd("layer.moveTo", {"layer": "Wall Mask (wall pixels)", "target": "WALL COLOUR", "position": "into"})
    a += cmd("layer.select", {"name": "Wall Mask (wall pixels)"})
    for nm, prm in walls:                      # created inside the group above the cutout, then clipped to it
        a += cmd("layer.newAdjustmentLayer.hueSaturation", prm)
        a += cmd("layer.setProps", {"name": nm, "visible": False})
        a += cmd("layer.createClippingMask", {"layer": nm})

    # ART: one smart object, two instances (no mat / mat); duplicate BEFORE transforming so both start square
    a += cmd("layer.select", {"name": "WALL COLOUR"})
    a += cmd("file.placeEmbedded", {"path": P("placeholder_art.png"), "smartObject": True, "scale": 100})
    a += cmd("layer.setProps", {"name": "Place Artwork Here", "blend": "Multiply"})
    a += cmd("layer.duplicate", {"name": "Place Artwork Here (Mat)"})
    a += cmd("layer.select", {"name": "Place Artwork Here"})
    a += cmd("edit.transform", {"quad": meta["quad_nomat"]})
    a += cmd("layer.select", {"name": "Place Artwork Here (Mat)"})
    a += cmd("edit.transform", {"quad": meta["quad_mat"]})
    a += cmd("layer.setProps", {"name": "Place Artwork Here (Mat)", "visible": False})

    a += cmd("layer.select", {"name": "Place Artwork Here (Mat)"})
    a += place("L_mat.png", "Mat (white, 4-ply)", "Multiply")
    a += place("L_mat_lip.png", "Mat bevel shadow", "Multiply")
    a += cmd("layer.new.group", {"name": "MAT"})
    for nm in ("Mat (white, 4-ply)", "Mat bevel shadow"):
        a += cmd("layer.moveTo", {"layer": nm, "target": "MAT", "position": "into"})
    a += cmd("layer.setProps", {"layer": "MAT", "visible": False})

    a += cmd("layer.select", {"name": "MAT"})
    for nm in ("white", "black", "walnut", "oak"):
        a += place(f"L_frame_{nm}.png", f"Frame {nm.capitalize()}", "Multiply", visible=(nm == "oak"))
    a += place("L_lip.png", "Frame lip shadow", "Multiply")
    a += cmd("layer.new.group", {"name": "FRAME"})
    for nm in ("Frame White", "Frame Black", "Frame Walnut", "Frame Oak", "Frame lip shadow"):
        a += cmd("layer.moveTo", {"layer": nm, "target": "FRAME", "position": "into"})

    a += cmd("layer.select", {"name": "FRAME"})
    order = [("soft", "Soft cast"), ("dapple", "Leaf dapple"), ("panes", "Window panes")]
    for key, label in order:
        a += place(f"L_shadow_{key}.png", f"{label} shadow", "Multiply", visible=(key == "panes"))
        a += place(f"L_sun_{key}.png", f"{label} sun warmth", "Soft Light", 0.6, visible=(key == "panes"))
    a += cmd("layer.new.group", {"name": "SHADOWS"})
    for key, label in order:
        for nm in (f"{label} shadow", f"{label} sun warmth"):
            a += cmd("layer.moveTo", {"layer": nm, "target": "SHADOWS", "position": "into"})

    a += cmd("layer.select", {"name": "SHADOWS"})
    a += place("L_glass.png", "Glass sheen", "Screen", 0.22)
    a += cmd("layer.new.group", {"name": "GLASS"})
    a += cmd("layer.moveTo", {"layer": "Glass sheen", "target": "GLASS", "position": "into"})
    a += ["--out", P("Room_Template.psd")]
    t = time.time()
    r = subprocess.run(a, capture_output=True, text=True)
    errs = [l for l in (r.stdout + r.stderr).splitlines() if "error" in l.lower() or "warning" in l.lower()]
    print("assemble rc", r.returncode, "s", round(time.time() - t, 1), *errs[:10], sep="\n")
    if r.returncode:
        print(r.stderr[-2000:])


if __name__ == "__main__":
    main()
