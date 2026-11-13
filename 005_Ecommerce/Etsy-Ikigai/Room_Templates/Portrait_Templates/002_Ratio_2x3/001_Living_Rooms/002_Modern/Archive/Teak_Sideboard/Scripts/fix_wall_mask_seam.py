"""Clean wall/furniture seam for the Teak Sideboard wall mask (2026-11-10, Tony-approved fix).

python fix_wall_mask_seam.py <old_wall_mask.png> <unlit_plate.png> <out_mask.png> [--debug <dir>]

Why: the lamp-free wall mask (Wall_Mask_Plate_No_Lamp.png) had a blocky, stair-stepped edge along the sideboard top
right of the bowl (up to ~47 px too high), a square notch beside the bowl and a scoop-stick remnant cut out of the
wall. The Portal turns a wall colour on at render time, so the un-painted cream wall showed through as pale smears
and a white speck (Book Club Cat slot 3).

How (only the sideboard top and the bowl change; the rest of the old mask is kept as it was):
1. Sideboard back edge = a straight line fitted to the strongest bright-to-dark vertical step of the unlit plate's
   L channel, columns x 600-1160 and 1720-2000 (fit residual <= 1.3 px). Wall above it, anti-aliased at sub-pixel.
2. Bowl (+ scoop sticks) = pixels darker than a local threshold between the local wall brightness (from the old
   mask's wall, eroded, filled by normalised convolution) and the dark wood (L 15), holes filled, opened/closed with
   round kernels and contour-smoothed (blur + 0.5 threshold), so the outline is round with no stair-steps.
3. Applied for x 600-2008 (blended into the old mask over 40 px at the left end), then a 1.2 px feather.
White = wall, black = furniture, same as before. build_template_v2.py reads this as --wallmask unchanged.
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

X0, X1 = 600, 2008                 # sideboard top span handled here (books end ~560, sideboard right end ~2010)
BOWL = (1150, 1540, 1735)          # x0, y0, x1 of the bowl search box (bottom = the sideboard line)
FIT_COLS = list(range(600, 1160, 4)) + list(range(1720, 2000, 4))


def main():
    old = np.array(Image.open(sys.argv[1]).convert("L")).astype("float32") / 255
    rgb = np.array(Image.open(sys.argv[2]).convert("RGB")).astype("float32") / 255
    out = Path(sys.argv[3])
    dbg = Path(sys.argv[sys.argv.index("--debug") + 1]) if "--debug" in sys.argv else None
    H, W = old.shape
    L = cv2.cvtColor(rgb, cv2.COLOR_RGB2Lab)[..., 0]

    # 1. sideboard back edge line
    Ls = cv2.GaussianBlur(L, (0, 0), 1.2)
    g = Ls[1:] - Ls[:-1]
    xs, ys = [], []
    for x in FIT_COLS:
        y0 = int(1665 + (x - 1150) * 0.064)            # rough prior, then the real step within +-30 px
        i = int(np.argmin(g[y0 - 30:y0 + 30, x]))
        xs.append(x); ys.append(y0 - 30 + i + 1.0)     # +1: the step lies between row i and i+1; edge at the dark row
    xs, ys = np.array(xs, "float32"), np.array(ys, "float32")
    p = np.polyfit(xs, ys, 1)
    res = np.abs(ys - np.polyval(p, xs))
    keep = res < 2.5
    p = np.polyfit(xs[keep], ys[keep], 1)
    yy, xx = np.mgrid[0:H, 0:W].astype("float32")
    line_y = np.polyval(p, xx)
    wall_line = np.clip(line_y - yy, 0, 1)             # 1 above the edge, sub-pixel ramp on the edge row

    # 2. bowl silhouette
    bx0, by0, bx1 = BOWL
    wall_old = cv2.erode((old > 0.5).astype("uint8"), np.ones((7, 7), "uint8")).astype("float32")
    num = cv2.GaussianBlur(L * wall_old, (0, 0), 10); den = cv2.GaussianBlur(wall_old, (0, 0), 10)
    wallL = num / np.maximum(den, 1e-3)
    for s in (25, 60):                                 # fill where no wall is near (inside furniture)
        n2 = cv2.GaussianBlur(L * wall_old, (0, 0), s); d2 = cv2.GaussianBlur(wall_old, (0, 0), s)
        wallL = np.where(den < 0.05, n2 / np.maximum(d2, 1e-3), wallL); den = np.maximum(den, d2)
    thr = 0.6 * wallL + 0.4 * 15.0
    box = np.zeros((H, W), bool)
    box[by0:, bx0:bx1] = True
    obj = box & (L < thr) & (yy < line_y + 2)
    obj = obj.astype("uint8")
    obj = cv2.morphologyEx(obj, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
    obj = cv2.morphologyEx(obj, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    n, lbl, st, _ = cv2.connectedComponentsWithStats(obj, connectivity=8)
    if n > 1:                                          # the bowl = the biggest dark blob; stray specks dropped
        big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        obj = (lbl == big).astype("uint8")
    cnt, _ = cv2.findContours(obj, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    obj = cv2.drawContours(np.zeros_like(obj), cnt, -1, 1, thickness=cv2.FILLED)   # fill holes (bowl inside)
    objs = cv2.GaussianBlur(obj.astype("float32"), (0, 0), 1.6)                    # contour smoothing
    obj_soft = np.clip((objs - 0.5) * 2.5 + 0.5, 0, 1)                             # ~1 px AA ramp

    # 3. compose: new wall = above the line and not bowl, inside the span; old mask elsewhere
    new = np.minimum(wall_line, 1 - obj_soft)
    w = np.clip((xx - X0) / 40.0, 0, 1) * (xx <= X1)
    w = w * (yy > 1450)                                # only the sideboard-top band changes
    mask = old * (1 - w) + new * w
    mask = cv2.GaussianBlur(mask, (0, 0), 1.2)         # 1-2 px feather
    Image.fromarray((np.clip(mask, 0, 1) * 255).round().astype("uint8"), "L").save(out)
    print({"line": [round(float(v), 5) for v in p], "fit_max_res_px": round(float(res[keep].max()), 2),
           "bowl_px": int(obj.sum()), "changed_px": int((np.abs(mask - cv2.GaussianBlur(old, (0, 0), 1.2)) > 0.5).sum())})
    if dbg:
        crop = (slice(1500, 1800), slice(1100, 2048))
        ov = (rgb[crop] * 255).astype("uint8").copy()
        e = (np.abs(cv2.Laplacian((mask[crop] > 0.5).astype("float32"), cv2.CV_32F)) > 0)
        ov[e] = (255, 0, 255)
        Image.fromarray(ov).resize((ov.shape[1] * 2, ov.shape[0] * 2), Image.NEAREST).save(dbg / "seam_overlay.png")


if __name__ == "__main__":
    main()
