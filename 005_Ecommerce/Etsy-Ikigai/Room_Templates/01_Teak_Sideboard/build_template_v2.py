"""v2 room template: one PSD per LIGHT PLATE (the image model relit the same room), real paint colours, moulded frames.

python build_template_v2.py <plate.png> <out_dir> --wallmask <wall_mask_from_unlit_plate.png> [--light left] [--soft]

Changes vs ../build_template.py (whose PSD mechanism is reused unchanged: smart object x2, groups, Multiply/Screen):
- no procedural window/dapple layers. The light is in the plate itself (kie.ai edit of the base room), and the panel's
  own shading (read from the magenta) carries it onto paper, mat and art; frames are lit by the same light map.
- --soft adds the soft cast-shadow option (the v3/v5 look) for the unlit base plate.
- WALL COLOUR = reflectance swap: solid colour new_paint/old_paint (in linear light; sRGB-gamma multiply is the same
  product) as a Multiply layer masked to the wall. Texture, shadows and sun stay; dark paints go dark, sun stays warm.
- FRAMES: Normal-blend layers computed per pixel: albedo x moulding profile shading (rounded outer arris, flat face,
  inner bevel, mitred corners, satin specular) x wood grain x the plate's own light (luma map + light colour vs. luma).
"""
import json, math, sys, time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))      # build_template.py (v1 helpers) sits next to this file
import build_template as bt  # noqa: E402  (spike v1: geometry, warp, masks, assemble helpers)
from build_template import rooms, luma, save_rgba, warp, rect_edge_dist, rect_mask  # noqa: E402

CLI = "photocraft-cli"
# albedo (sRGB-ish 0..1), grain strength, specular strength, specular tightness
FRAMES = {
    "Oak": ((0.80, 0.60, 0.40), 0.16, 0.05, 18),
    "Walnut": ((0.34, 0.215, 0.145), 0.20, 0.07, 22),
    "Black": ((0.045, 0.043, 0.042), 0.015, 0.10, 30),
    "White": ((0.955, 0.950, 0.935), 0.008, 0.05, 26),
}
PAINTS = {   # muted real paint chips (approx. sRGB), applied as reflectance swaps from the plate's cream wall
    "Greige": (200, 192, 176), "Sage": (168, 175, 150), "Soft Clay": (194, 152, 130),
    "Dusty Blue": (158, 172, 181), "Charcoal": (84, 84, 82),
}
OLD_PAINT = np.array([236, 228, 212], "float32") / 255
RAIL, MAT = 0.040, 0.085   # rail 0.032 -> 0.040 (2026-11-08: frames read flat; a wider moulding shows its profile)


def lin(x):
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def enc(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * x ** (1 / 2.4) - 0.055)


def refine_wall(mask_u8, img, panel):
    """Wall mask from the unlit plate, grown up to object edges (fixes the halo the v1 mask left round the frame,
    its cast shadow and the lamp): grow only into pixels whose CHROMA (Lab a,b) matches the local wall and that are
    not near-black, so shadowed wall is included but furniture/lamp are not. The panel (front + side) is cut out."""
    sc = img.astype("float32") / 255
    m = (mask_u8 > 127).astype("float32")
    lab = cv2.cvtColor(sc, cv2.COLOR_RGB2Lab)
    wl = cv2.GaussianBlur(lab * m[..., None], (0, 0), 25) / np.maximum(cv2.GaussianBlur(m, (0, 0), 25)[..., None], 1e-3)
    dab = np.linalg.norm(lab[..., 1:] - wl[..., 1:], axis=2)
    zone = (cv2.dilate(m, np.ones((11, 11), "uint8")) > 0) | (cv2.dilate(panel, np.ones((91, 91), "uint8")) > 0)  # edge barrier: never grow far (cream book pages match the wall chroma)
    grow = zone & (dab < 6) & (lab[..., 0] > 28)
    band = cv2.dilate(panel, np.ones((121, 121), "uint8")) > 0          # the panel's own cast-shadow strip is wall
    full = ((m > 0) | grow | (band & (lab[..., 0] > 15))) & ~(panel > 0)
    full = cv2.morphologyEx(full.astype("uint8"), cv2.MORPH_OPEN, np.ones((3, 3), "uint8"))
    full = cv2.morphologyEx(full, cv2.MORPH_CLOSE, np.ones((5, 5), "uint8"))
    n, lbl, st, _ = cv2.connectedComponentsWithStats((full == 0).astype("uint8"), connectivity=4)
    small = np.isin(lbl, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] < 1500])
    full = (full > 0) | small
    full = full & ~(panel > 0)
    return np.clip(cv2.GaussianBlur(full.astype("float32"), (0, 0), 0.9), 0, 1)


def light_colour_model(sc, wallring):
    """Light colour vs brightness from the wall around the panel: the colour of the lit wall (top quarter of luma)
    and of the shaded wall (bottom third), the paint's own cream divided out; in between it blends by brightness.
    (A log-linear fit was tried first: it averaged the golden sun away and the sun patch on the art read pale.)"""
    y = luma(sc[wallring]); rgbw = sc[wallring]
    lo, hi = np.percentile(y, 33), np.percentile(y, 75)
    oldtint = OLD_PAINT / float(luma(OLD_PAINT))
    def col(sel):
        c = rgbw[sel].mean(0); c = c / float(luma(c)) / oldtint
        c = 1 + 0.85 * (c - 1)
        return c / float(luma(c))
    c_lit, c_sh = col(y >= hi), col(y <= lo)
    y_lit, y_sh = float(y[y >= hi].mean()), float(y[y <= lo].mean())

    def tint(lum):
        w = np.clip((lum - y_sh) / max(y_lit - y_sh, 1e-3), 0, 1)[..., None]
        return c_sh * (1 - w) + c_lit * w
    return tint


def main():
    plate = Path(sys.argv[1]); out = Path(sys.argv[2]); out.mkdir(exist_ok=True)
    arg = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
    light = arg("--light", "left"); soft = "--soft" in sys.argv
    wm_path = Path(arg("--wallmask")); ref_plate = Path(arg("--refplate", str(plate)))
    t0 = time.time()
    rgb, quad, info, (BW, BH), Hm = bt.board_geometry(plate)
    H, W = rgb.shape[:2]
    sc = rgb.astype("float32") / 255
    bw, bh = int(math.ceil(BW)), int(math.ceil(BH))
    sgn = 1 if light == "left" else -1

    front = cv2.fillConvexPoly(np.zeros((H, W), "uint8"), quad.round().astype("int32"), 255)
    loose = rooms.loose_magenta(rgb).astype("uint8") * 255
    near = cv2.dilate(front, np.ones((41, 41), "uint8"))
    side = ((loose > 0) & (near > 0) & (front == 0)).astype("uint8") * 255
    side = cv2.morphologyEx(side, cv2.MORPH_OPEN, np.ones((3, 3), "uint8"))
    obj = cv2.dilate(np.maximum(front, side), np.ones((5, 5), "uint8"))
    objf = obj > 0

    # ---- panel light map from the magenta (R+B; G is ~0 on magenta), as in v1, but no clamp at 0.25 for deep shade
    # luma, not (R+B)/2: where sun clips the magenta's R and B, only G still rises, so luma keeps the real contrast
    # (checked: panel p95/p10 luma 2.17 vs wall 2.3 on the golden plate; (R+B)/2 gave 1.87)
    V = luma(sc)
    mag = (cv2.erode(front, np.ones((9, 9), "uint8")) > 0) & rooms.loose_magenta(rgb)
    p95 = float(np.percentile(V[mag], 95))
    L = np.clip(V / p95, 0.15, 1.08)
    m = mag.astype("float32")
    fillL = cv2.GaussianBlur(L * m, (0, 0), 9) / np.maximum(cv2.GaussianBlur(m, (0, 0), 9), 1e-4)
    L = np.where(mag, L, fillL)
    L = np.where(side > 0, np.clip(V / p95, 0.15, 1.0), L)
    L = cv2.GaussianBlur(L, (0, 0), 1.2)
    c = quad.mean(axis=0)
    ring = cv2.fillConvexPoly(np.zeros((H, W), "uint8"), (c + (quad - c) * 1.35).round().astype("int32"), 255)
    ring = (ring > 0) & ~(cv2.dilate(obj, np.ones((15, 15), "uint8")) > 0)
    satv = (sc.max(2) - sc.min(2)) / np.maximum(sc.max(2), 1e-3)
    wallring = ring & (satv < 0.45)
    wl = luma(sc)[wallring]
    wall95 = float(np.percentile(wl, 95))
    tint = light_colour_model(sc, wallring)
    # the magenta's p95 is the panel's brightest lit level; the lit wall's p95 is the matching wall level
    illum = (L * wall95)[..., None] * tint(np.clip(L * wall95, 0.02, 1))   # light reaching the panel (RGB)
    lit_white = illum * 0.94                    # paper white = 0.94 x the lit wall next to it (style guide 3a)

    base = sc.copy()
    band = (cv2.dilate(obj, np.ones((71, 71), "uint8")) > 0) & ~objf
    farr = (cv2.dilate(obj, np.ones((161, 161), "uint8")) > 0) & ~band & ~objf
    rg = (sc[..., 0] + 0.02) / (sc[..., 1] + 0.02); bg = (sc[..., 2] + 0.02) / (sc[..., 1] + 0.02)
    ref_rg, ref_bg = np.median(rg[farr]), np.median(bg[farr])
    spill = band & ((rg - ref_rg > 0.06) | (bg - ref_bg > 0.06))
    if spill.any():
        g = sc[..., 1]
        fix = np.stack([g * ref_rg, g, g * ref_bg], -1)
        fix = fix * (luma(sc) / np.maximum(luma(fix), 1e-4))[..., None]
        sm_sp = cv2.GaussianBlur(spill.astype("float32"), (0, 0), 3)[..., None]
        base = base * (1 - sm_sp) + fix * sm_sp

    # ---- board geometry (same as v1)
    r = RAIL * BH
    inner = (r, r, BW - r, BH - r)
    iw, ih = inner[2] - inner[0], inner[3] - inner[1]
    art_aspect = iw / ih
    mb = MAT * BH
    ow, oh = iw - 2 * mb, ih - 2 * mb * 1.1
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
    q_mat = to_img([[mat_open[0], mat_open[1]], [mat_open[2], mat_open[1]], [mat_open[2], mat_open[3]], [mat_open[0], mat_open[3]]])
    so_size = (round(2400 * art_aspect), 2400)
    yy, xx = np.mgrid[0:bh, 0:bw].astype("float32")

    # ---- FRAME moulding: which rail (nearest outer edge => mitred corners), position across the rail t in [0,1]
    d_l, d_r, d_t, d_b = xx, BW - xx, yy, BH - yy
    dmin = np.minimum.reduce([d_l, d_r, d_t, d_b])
    rail_id = np.argmin(np.stack([d_l, d_r, d_t, d_b]), 0)          # 0 L, 1 R, 2 T, 3 B
    t = np.clip(dmin / r, 0, 1)
    outn = np.array([[-1, 0], [1, 0], [0, -1], [0, 1]], "float32")[rail_id]   # outward direction in board xy
    # profile slope (dz/d-outward): rounded outer arris, flat face, inner bevel facing the opening
    # stepped moulding (2026-11-08, Tony: frames looked flat): rounded outer arris, raised flat face, a small step
    # down (cove) at 45-55 %, a second lower flat, then the inner bevel down to the glazing
    slope = (np.where(t < 0.18, 1.8 * np.clip(1 - t / 0.18, 0, 1) ** 1.4, 0.0)
             + np.where((t > 0.44) & (t < 0.50), -2.2, 0.0) + np.where((t >= 0.50) & (t < 0.56), 0.9, 0.0)
             + np.where(t > 0.74, -1.1 * ((t - 0.74) / 0.26), 0.0))
    cove = 1 - 0.35 * np.exp(-((t - 0.50) / 0.03) ** 2)              # occlusion at the bottom of the step
    nrm = np.dstack([outn[..., 0] * slope, outn[..., 1] * slope, np.ones_like(t)])
    nrm /= np.linalg.norm(nrm, axis=2, keepdims=True)
    ldir = np.array([-0.55 * sgn, -0.45, 0.70], "float32"); ldir /= np.linalg.norm(ldir)
    lam = np.clip(nrm @ ldir, 0, 1) / float(ldir[2])                 # flat face == 1.0
    shade = (0.28 + 0.72 * lam) * cove                            # stronger profile contrast
    view = np.array([0.0, 0.0, 1.0], "float32"); hv = (ldir + view) / np.linalg.norm(ldir + view)
    spec_base = np.clip(nrm @ hv, 0, 1)
    # mitre seam: thin dark line where rails meet (|dx| == |dy| distance to the corner diagonal)
    big = np.float32(1e6)
    pair = lambda a, b: np.where((a < r * 1.05) & (b < r * 1.05), np.abs(a - b), big)   # only inside that corner
    diag = np.minimum.reduce([pair(d_l, d_t), pair(d_r, d_t), pair(d_l, d_b), pair(d_r, d_b)])
    mitre = 1 - 0.35 * np.exp(-(diag / (0.0012 * BH)) ** 2) * (dmin < r)
    gap = 1 - 0.55 * np.exp(-(((r - dmin)) / (0.0016 * BH)) ** 2)      # dark gap where the frame meets the glazing
    # wood grain: long streaks along the rail + a few annual-ring lines, warped by low-frequency noise
    rng = np.random.default_rng(3)
    def streaks(sx, sy):
        n = rng.normal(0, 1, (bh, bw)).astype("float32")
        n = cv2.GaussianBlur(n, (0, 0), sigmaX=sx, sigmaY=sy)
        return n / (np.abs(n).std() * 3 + 1e-6)
    gh = streaks(70, 1.0) + 0.5 * streaks(15, 0.6); gv = streaks(1.0, 70) + 0.5 * streaks(0.6, 15)
    warpn = cv2.GaussianBlur(rng.normal(0, 1, (bh, bw)).astype("float32"), (0, 0), 25) * 60
    horiz = rail_id >= 2
    across = np.where(horiz, yy, xx) + warpn
    rings = np.sin(across / (0.0045 * BH) * 2 * np.pi) ** 8
    grain = np.where(horiz, gh, gv) * 0.8 - 0.6 * rings

    rails = (dmin < r).astype("float32")
    rails_img = warp(rails, Hm, W, H)
    sidef = cv2.GaussianBlur((side > 0).astype("float32"), (0, 0), 0.8)
    cq = quad.mean(axis=0)
    grown = quad + (quad - cq) / np.linalg.norm(quad - cq, axis=1, keepdims=True) * 2.5
    ga = cv2.fillConvexPoly(np.zeros((H, W), "uint8"), (grown * 16).round().astype("int32"), 255,
                            lineType=cv2.LINE_AA, shift=4).astype("float32") / 255
    fringe = np.clip(ga - rails_img - warp(np.ones((bh, bw), "float32"), Hm, W, H), 0, 1)
    frame_a = np.clip(rails_img + sidef + fringe, 0, 1)
    objA = np.clip(ga + sidef, 0, 1)[..., None]
    base = base * (1 - objA) + lit_white * objA
    Image.fromarray((np.clip(base, 0, 1) * 255).round().astype("uint8")).save(out / "L_base.png")

    illum_n = illum / float(luma(OLD_PAINT))     # light normalised so a 1.0-albedo surface = white at wall95/paint
    for name, (alb, gs, ks, kp) in FRAMES.items():
        a = np.array(alb, "float32")
        board = np.array([1.0, 0.95, 1.04, 0.97], "float32")[rail_id]      # each rail is its own piece of wood
        tex = np.clip(1 + gs * grain, 0.4, 1.6) * (1 + (board - 1) * min(1.0, gs * 6))
        bshade = shade * mitre * gap
        col = a[None, None, :] * (bshade * tex)[..., None] + (ks * spec_base ** kp)[..., None]
        col_img = warp(col, Hm, W, H)
        side_col = (a * 0.55)[None, None, :] * np.ones((H, W, 1), "float32")   # the side (depth) face: in its own shade
        full = np.where(((sidef > 0.5) | (fringe > 0))[..., None], side_col, col_img)
        lit = full * illum_n
        save_rgba(lit, frame_a, out / f"L_frame_{name.lower()}.png")

    # lip shadow (the moulding shades the glazing on the light side) - as v1
    dl = (xx - r) if sgn > 0 else ((BW - r) - xx)
    dt = yy - r
    inside = (xx > r) & (xx < BW - r) & (yy > r) & (yy < BH - r)
    dr = ((BW - r) - xx) if sgn > 0 else (xx - r)
    db = (BH - r) - yy
    lip = np.where(inside, (0.62 + 0.38 * np.clip(dl / (0.035 * BH), 0, 1) ** 0.7) *       # moulding shades the art
                   (0.74 + 0.26 * np.clip(dt / (0.025 * BH), 0, 1) ** 0.7) *               # on the light side + top
                   (0.93 + 0.07 * np.clip(dr / (0.008 * BH), 0, 1)) *
                   (0.94 + 0.06 * np.clip(db / (0.008 * BH), 0, 1)), 1.0)
    save_rgba(np.repeat(warp(lip, Hm, W, H)[..., None], 3, 2), warp(inside.astype("float32"), Hm, W, H), out / "L_lip.png")

    # contact shadow on the wall (2026-11-08): soft drop shadow away from the light + tight occlusion at the frame edge,
    # drawn on an extended wall plane and warped with the panel's own perspective; never over the frame itself
    ext = 0.25
    ow_, oh_ = int(bw + 2 * ext * BH), int(bh + 2 * ext * BH)
    off = ext * BH
    Y, X = np.mgrid[0:oh_, 0:ow_].astype("float32")
    def rect(dx, dy, blur):
        m = ((X - off - dx >= 0) & (X - off - dx <= BW) & (Y - off - dy >= 0) & (Y - off - dy <= BH)).astype("float32")
        return cv2.GaussianBlur(m, (0, 0), blur * BH)
    cs = 0.30 * rect(0.012 * BH * sgn, 0.018 * BH, 0.014) + 0.22 * rect(0, 0, 0.004)
    T = np.array([[1, 0, -off], [0, 1, -off], [0, 0, 1]], "float64")
    csw = cv2.warpPerspective(np.clip(cs, 0, 0.45).astype("float32"), Hm @ T, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)
    csw = csw * (1 - np.clip(ga + sidef, 0, 1))
    save_rgba(np.repeat((1 - csw)[..., None], 3, 2), np.ones((H, W), "float32"), out / "L_contact.png")

    # ---- MAT (multiplies over lit white) - as v1, with a slightly stronger bevel
    matm = np.clip(rect_mask(BW, BH, *inner) - rect_mask(BW, BH, *mat_open), 0, 1)
    matcol = np.ones((bh, bw, 3), "float32") * np.array([0.975, 0.965, 0.94], "float32")
    dbev = rect_edge_dist(xx, yy, *mat_open)
    bev = np.exp(-(dbev / (0.002 * BH)) ** 2)
    far = (np.abs(xx - mat_open[2]) < np.abs(xx - mat_open[0])) if sgn > 0 else (np.abs(xx - mat_open[0]) < np.abs(xx - mat_open[2]))
    matcol *= (1 - 0.20 * bev * far + 0.04 * bev * ~far)[..., None]
    save_rgba(warp(matcol, Hm, W, H), warp(matm, Hm, W, H), out / "L_mat.png")
    inopen = (xx > mat_open[0]) & (xx < mat_open[2]) & (yy > mat_open[1]) & (yy < mat_open[3])
    dlm = (xx - mat_open[0]) if sgn > 0 else (mat_open[2] - xx)
    mlip = np.where(inopen, (0.86 + 0.14 * np.clip(dlm / (0.008 * BH), 0, 1)) *
                    (0.92 + 0.08 * np.clip((yy - mat_open[1]) / (0.006 * BH), 0, 1)), 1.0)
    save_rgba(np.repeat(warp(mlip, Hm, W, H)[..., None], 3, 2), warp(inopen.astype("float32"), Hm, W, H), out / "L_mat_lip.png")

    # ---- GLASS (Screen): faint broad sheen + reflection of the bright room side, as v1
    u, v = xx / BW, yy / BH
    bandg = np.exp(-(((u * 0.9 + v * 0.55) - 0.55) / 0.10) ** 2) * 0.9 + np.exp(-(((u * 0.9 + v * 0.55) - 0.78) / 0.035) ** 2) * 0.5
    refl = cv2.GaussianBlur(((np.abs(((u - 0.15) * 3) % 1 - 0.5) < 0.42) & (v < 0.55) & (u < 0.6)).astype("float32"), (0, 0), 0.03 * BH) * 0.35
    sheen = np.clip(bandg + refl, 0, 1)
    save_rgba(warp(sheen[..., None] * np.array([1.0, 0.97, 0.92], "float32")[None, None, :], Hm, W, H),
              warp(inside.astype("float32"), Hm, W, H), out / "L_glass.png")

    # ---- WALL COLOUR (reflectance swap, Multiply)
    panel = ((ga + sidef) > 0.02).astype("uint8")
    wall = refine_wall(np.array(Image.open(wm_path).convert("L")), (np.clip(base, 0, 1) * 255).astype("uint8"), panel)
    Image.fromarray((wall * 255).astype("uint8")).save(out / "wall_mask.png")
    # appearance-calibrated: the plate's median wall colour becomes the paint chip, every other wall pixel keeps its
    # ratio to it (texture, sun, shade, light colour). Calibrating to the assumed cream paint instead gave olive
    # 'sage' under warm light (wall_route_cmp.jpg).
    # Paint = a NORMAL layer of real paint pixels over the wall mask (physically: irradiance x new albedo).
    # the wall median x this pixel's light colour relative to the median (damped to 60 %: where the plate clipped the
    # sun to white the light colour reads cool, which made blue sun spots on charcoal). A plain solid Multiply could not
    # make a wall warmer than the plate (clay on the cool golden-hour wall came out lavender) - tried and dropped.
    wsel = wall > 0.9
    bl = lin(np.clip(base, 0, 1))
    Yp = luma(bl)
    old = lin(OLD_PAINT); Yo = float(luma(old))
    # light colour at each pixel = its chroma / the cream paint's chroma (keeps the scene's own cast: cool shade, warm sun)
    rel = (bl / np.maximum(Yp, 1e-4)[..., None]) / (old / Yo)[None, None, :]
    # where the plate clipped the sun to white the chroma is lost (reads cool): borrow the sun colour of the brightest
    # unclipped wall pixels instead
    mx = np.clip(base, 0, 1).max(2)
    ok = wsel & (mx < 0.93)
    if ok.sum() > 500:
        yv = Yp[ok]; hi = (yv >= np.percentile(yv, 85))
        rel_sun = np.median(rel[ok][hi], axis=0)
        wclip = np.clip((mx - 0.90) / 0.08, 0, 1)[..., None]
        rel = rel * (1 - wclip) + rel_sun[None, None, :] * wclip
    rel = np.clip(rel, 0.5, 2.0) ** 0.7
    rel = rel / np.maximum(luma(rel), 1e-4)[..., None]
    for pn, pc in PAINTS.items():
        chip = lin(np.array(pc, "float32") / 255)
        # same light as the plate: brightness = this pixel's irradiance (Yp / cream albedo) x the new paint's albedo
        px = chip[None, None, :] * (Yp / Yo)[..., None] * rel
        save_rgba(enc(px).astype("float32"), wall, out / f"L_paint_{pn.lower().replace(' ', '_')}.png")

    # ---- optional SOFT CAST (v1 'soft': the look Tony called most natural) for the unlit plate
    if soft:
        recv = np.clip(cv2.GaussianBlur(cv2.morphologyEx(np.maximum((wall > 0.5).astype("uint8") * 255, obj), cv2.MORPH_CLOSE,
                       np.ones((45, 45), "uint8")), (0, 0), 3).astype("float32") / 255 + objf + frame_a, 0, 1)
        ext = 2.2
        def plane_pattern(fn, blur):
            ow_, oh_ = int(bw * (1 + 2 * ext * BH / BW * 0.5)), int(bh * (1 + ext))
            offx, offy = (ow_ - bw) / 2, (oh_ - bh) / 2
            Y, X = np.mgrid[0:oh_, 0:ow_].astype("float32")
            pat = cv2.GaussianBlur(fn((X - offx) / BH, (Y - offy) / BH).astype("float32"), (0, 0), blur * BH)
            T = np.array([[1, 0, -offx], [0, 1, -offy], [0, 0, 1]], "float64")
            return cv2.warpPerspective(pat, Hm @ T, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)
        sun = plane_pattern(lambda x, y: ((x - 0.6 * sgn * (y - 0.3)) > -0.9) & ((x - 0.6 * sgn * (y - 0.3)) < 0.45)
                            & (y > -0.6) & (y < 1.2), 0.07)
        cast = plane_pattern(lambda x, y: ((x - 0.04 * sgn) > 0) & ((x - 0.04 * sgn) < BW / BH) & ((y - 0.03) > 0) & ((y - 0.03) < 1), 0.02)
        sun = sun * recv * (1 - cast * np.clip(wall - objf, 0, 1) * 0.9)
        sh = np.array((0.80, 0.81, 0.86), "float32")
        save_rgba(sh[None, None, :] + (1 - sh)[None, None, :] * sun[..., None], np.ones((H, W), "float32"), out / "L_shadow_soft.png")

    ph = np.full((so_size[1], so_size[0], 3), 235, "uint8")
    ph[:, ::100] = 120; ph[::100, :] = 120
    Image.fromarray(ph).save(out / "placeholder_art.png")

    meta = {"plate": str(plate), "panel_quad": quad.round(2).tolist(), "panel_aspect": round(float(info["aspect"]), 4),
            "art_aspect": round(art_aspect, 4), "smart_object_px": list(so_size), "quad_nomat": q_nomat, "quad_mat": q_mat,
            "wall95": round(wall95, 3), "light_from": light, "soft": soft, "paints": list(PAINTS),
            "prep_s": round(time.time() - t0, 1)}
    (out / "template.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps({k: meta[k] for k in ("panel_quad", "wall95", "prep_s")}))
    assemble(out, meta)


def cmd(c, p=None):
    return ["--cmd", c, "--params", json.dumps(p or {})]


def assemble(out, meta):
    P = lambda n: str((out / n).resolve())
    a = [CLI, "run", P("L_base.png")] + cmd("layer.setProps", {"name": "BASE (scene plate with its light, panel = lit white)"})

    def place(fname, name, blend="Normal", opacity=1.0, visible=True):
        return (cmd("file.placeEmbedded", {"path": P(fname), "smartObject": False, "scale": 100})
                + cmd("layer.setProps", {"name": name, "blend": blend, "opacity": opacity, "visible": visible}))

    names = []
    for pn in meta["paints"]:
        nm = f"Wall {pn}"; names.append(nm)
        a += place(f"L_paint_{pn.lower().replace(' ', '_')}.png", nm, "Normal", visible=False)
    a += cmd("layer.new.group", {"name": "WALL COLOUR"})
    for nm in names:
        a += cmd("layer.moveTo", {"layer": nm, "target": "WALL COLOUR", "position": "into"})

    a += cmd("layer.select", {"name": "WALL COLOUR"})
    a += cmd("file.placeEmbedded", {"path": P("placeholder_art.png"), "smartObject": True, "scale": 100})
    a += cmd("layer.setProps", {"name": "Place Artwork Here", "blend": "Multiply"})
    a += cmd("layer.duplicate", {"name": "Place Artwork Here (Mat)"})
    a += cmd("layer.select", {"name": "Place Artwork Here"}) + cmd("edit.transform", {"quad": meta["quad_nomat"]})
    a += cmd("layer.select", {"name": "Place Artwork Here (Mat)"}) + cmd("edit.transform", {"quad": meta["quad_mat"]})
    a += cmd("layer.setProps", {"name": "Place Artwork Here (Mat)", "visible": False})

    a += cmd("layer.select", {"name": "Place Artwork Here (Mat)"})
    a += place("L_mat.png", "Mat (white, 4-ply)", "Multiply") + place("L_mat_lip.png", "Mat bevel shadow", "Multiply")
    a += cmd("layer.new.group", {"name": "MAT"})
    for nm in ("Mat (white, 4-ply)", "Mat bevel shadow"):
        a += cmd("layer.moveTo", {"layer": nm, "target": "MAT", "position": "into"})
    a += cmd("layer.setProps", {"layer": "MAT", "visible": False})

    a += cmd("layer.select", {"name": "MAT"})
    a += place("L_contact.png", "Frame contact shadow", "Multiply")
    a += place("L_lip.png", "Frame lip shadow", "Multiply")
    for nm in ("white", "black", "walnut", "oak"):
        a += place(f"L_frame_{nm}.png", f"Frame {nm.capitalize()}", "Normal", visible=(nm == "oak"))
    a += cmd("layer.new.group", {"name": "FRAME"})
    for nm in ("Frame contact shadow", "Frame lip shadow", "Frame White", "Frame Black", "Frame Walnut", "Frame Oak"):
        a += cmd("layer.moveTo", {"layer": nm, "target": "FRAME", "position": "into"})

    last = "FRAME"
    if meta.get("soft"):
        a += cmd("layer.select", {"name": "FRAME"}) + place("L_shadow_soft.png", "Soft cast shadow", "Multiply", visible=False)
        a += cmd("layer.new.group", {"name": "SHADOWS"})
        a += cmd("layer.moveTo", {"layer": "Soft cast shadow", "target": "SHADOWS", "position": "into"})
        last = "SHADOWS"
    a += cmd("layer.select", {"name": last}) + place("L_glass.png", "Glass sheen", "Screen", 0.22)
    a += cmd("layer.new.group", {"name": "GLASS"})
    a += cmd("layer.moveTo", {"layer": "Glass sheen", "target": "GLASS", "position": "into"})
    a += ["--out", P("Room_Template.psd")]
    import subprocess
    t = time.time()
    rr = subprocess.run(a, capture_output=True, text=True)
    errs = [l for l in (rr.stdout + rr.stderr).splitlines() if "error" in l.lower() or "warning" in l.lower()]
    print("assemble rc", rr.returncode, "s", round(time.time() - t, 1), *errs[:10], sep="\n")
    if rr.returncode:
        print(rr.stderr[-2000:])


if __name__ == "__main__":
    main()
