"""Placement detector (prototype, read-only): does the frame sit physically right on the wall?
Looks for long straight wall-molding / panel lines around the frame in the scene render and reports:
  covered  : molding lines that run INTO the frame (a vertical line above/below the frame whose x lies inside the
             frame, or a horizontal line left/right of it whose y lies inside) = the frame hangs over molding
  panel    : the nearest molding line on each side (gap in px from the frame's OUTER edge), whether the frame is
             fully inside one panel, and how far off-centre it is
Frame outer edge: the art quad pushed outward until the frame's outer edge (strongest step within 10% of the size).
Usage: python placement.py scenes_dir out_dir [key ...]"""
import json
import math
import sys
from pathlib import Path

import cv2
import numpy as np

SC = Path(sys.argv[1])
OUT = Path(sys.argv[2])
OUT.mkdir(exist_ok=True)
idx = json.loads((SC / "index.json").read_text())
keys = sys.argv[3:] or sorted(k for k in idx if idx[k].get("V"))


def frame_outer(gray, V):
    """Outer frame box (x0, y0, x1, y1): per side, the strongest brightness step 1-10% of the size outside the art."""
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
            ys = np.clip(ys, 0, H - 1)
            xs = np.clip(xs, 0, W - 1)
            prof.append(float(np.median(g[ys, xs])))
        prof = np.array(prof)
        step = np.abs(prof[3:] - prof[:-3])
        # the outermost strong step (frame -> wall), searching from 1% out
        lo = max(1, int(0.01 * max(w, h)))
        cand = np.nonzero(step[lo:] >= 0.5 * step[lo:].max())[0]
        d = (lo + cand[-1] + 2 + 2) if len(cand) and step[lo:].max() > 6 else int(0.04 * max(w, h))
        out.append(d)
    return x0 - out[3], y0 - out[0], x1 + out[1], y1 + out[2], out


def segments(gray, mask):
    lsd = cv2.createLineSegmentDetector(cv2.LSD_REFINE_STD)
    ls = lsd.detect(cv2.GaussianBlur(gray, (0, 0), 1.0).astype("uint8"))[0]
    out = []
    if ls is None:
        return out
    for x1, y1, x2, y2 in np.asarray(ls).reshape(-1, 4):
        mx, my = int((x1 + x2) / 2), int((y1 + y2) / 2)
        if not (0 <= my < mask.shape[0] and 0 <= mx < mask.shape[1]) or not mask[my, mx]:
            continue
        out.append((float(x1), float(y1), float(x2), float(y2)))
    return out


def merge(segs, vertical, tol=4.0):
    """Group nearly collinear axis-aligned segments into lines: (pos, start, end, total length)."""
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
    items.sort()
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


res = {}
for k in keys:
    rgb = cv2.cvtColor(cv2.imread(str(SC / f"{k}.png")), cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype("float32")
    H, W = gray.shape
    V = np.float32(idx[k]["V"])
    fx0, fy0, fx1, fy1, fw = frame_outer(gray, V)
    fwid, fhei = fx1 - fx0, fy1 - fy0
    S = max(fwid, fhei)
    m = np.zeros((H, W), bool)                                   # search zone: around the frame, frame excluded
    m[int(max(0, fy0 - 0.6 * fhei)):int(min(H, fy1 + 0.35 * fhei)), int(max(0, fx0 - 0.6 * fwid)):int(min(W, fx1 + 0.6 * fwid))] = True
    m[int(fy0 - 3):int(fy1 + 3), int(fx0 - 3):int(fx1 + 3)] = False
    segs = segments(gray, m)
    vl = [l for l in merge(segs, True) if l[3] >= 0.12 * fhei]
    hl = [l for l in merge(segs, False) if l[3] >= 0.12 * fwid]
    covered = []

    def both_sides(segs_, lo, hi, size):
        """molding seen on BOTH sides of the frame at the same position = it runs behind the frame"""
        near_lo = sum(b - a for a, b in segs_ if b > lo - 0.3 * size and a < lo + 4)
        near_hi = sum(b - a for a, b in segs_ if a < hi + 0.3 * size and b > hi - 4)
        return near_lo >= 0.06 * size and near_hi >= 0.06 * size
    for pos, a, b, L, sg in vl:
        if fx0 + 0.03 * fwid < pos < fx1 - 0.03 * fwid and both_sides(sg, fy0, fy1, fhei):
            covered.append({"dir": "vertical", "x": round(pos), "span": [round(a), round(b)], "len": round(L)})
    for pos, a, b, L, sg in hl:
        if fy0 + 0.03 * fhei < pos < fy1 - 0.03 * fhei and both_sides(sg, fx0, fx1, fwid):
            covered.append({"dir": "horizontal", "y": round(pos), "span": [round(a), round(b)], "len": round(L)})

    def nearest(lines, lo, hi, band_lo, band_hi, before):
        sp_ = band_hi - band_lo                 # a panel border runs past the frame on BOTH ends (a frame's own
        c = [l for l in lines if (l[0] < lo if before else l[0] > hi)  # side / shadow line does not)
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
    # regular wall texture (brick courses, boards: 4+ evenly spaced lines behind the frame) is a real wall, not molding
    for d_ in ("horizontal", "vertical"):
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
                res.setdefault("_texture", []).append(k)
    # a wainscot PANEL around the frame = borders left AND right AND above or below (a closed molding rectangle)
    panel = gaps["left"] is not None and gaps["right"] is not None and (gaps["top"] is not None or gaps["bottom"] is not None)
    flag = []
    if covered:
        flag.append(f"frame hangs over {len(covered)} molding line(s) (molding continues on both sides of it)")
    if panel:
        touch = [s for s, g in gaps.items() if g is not None and g < 0.03 * S]
        if touch:
            flag.append("frame touches the panel molding on " + ", ".join(touch))
        if off.get("horizontal", 0) > 0.25:
            flag.append(f"off-centre in its panel, left/right ({off['horizontal']:.0%})")
        if off.get("vertical", 0) > 0.5:
            flag.append(f"off-centre in its panel, up/down ({off['vertical']:.0%})")
    res[k] = {"frame_outer": [round(float(v)) for v in (fx0, fy0, fx1, fy1)], "frame_width_px": fw, "gaps_px": gaps,
              "off_centre": off, "panel_both_sides": panel, "covered": covered, "flag": flag, "lines": {"v": len(vl), "h": len(hl)}}
    # overlay
    vis = rgb.copy()
    cv2.rectangle(vis, (int(fx0), int(fy0)), (int(fx1), int(fy1)), (0, 200, 255), 3)
    for pos, a, b, L, _ in vl:
        cv2.line(vis, (int(pos), int(a)), (int(pos), int(b)), (0, 255, 0), 2)
    for pos, a, b, L, _ in hl:
        cv2.line(vis, (int(a), int(pos)), (int(b), int(pos)), (0, 255, 0), 2)
    for c in covered:
        if c["dir"] == "vertical":
            cv2.line(vis, (c["x"], c["span"][0]), (c["x"], c["span"][1]), (255, 0, 0), 5)
        else:
            cv2.line(vis, (c["span"][0], c["y"]), (c["span"][1], c["y"]), (255, 0, 0), 5)
    x0c, y0c = int(max(0, fx0 - 0.7 * fwid)), int(max(0, fy0 - 0.6 * fhei))
    crop = vis[y0c:int(min(H, fy1 + 0.45 * fhei)), x0c:int(min(W, fx1 + 0.7 * fwid))]
    sc = 900 / max(crop.shape[:2])
    cv2.imwrite(str(OUT / f"{k}_placement.jpg"), cv2.cvtColor(cv2.resize(crop, None, fx=sc, fy=sc), cv2.COLOR_RGB2BGR))
    print(f"{'FLAG' if flag else 'ok  '} {k}: {'; '.join(flag)} gaps={gaps} off={off}")
(OUT / "placement.json").write_text(json.dumps(res, indent=1, default=float))
