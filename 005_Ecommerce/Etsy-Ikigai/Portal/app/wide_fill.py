"""Generative fill, wide-crop method (Nano Banana 2.1 on kie.ai), for "Edit with chat" pixel edits.

Proven 2026-11-15 on the Ikigai living-room template (handoff 2026-11-15 PhotoCraft OpenFill): the model redraws a
WIDE crop around the object (with the floor and wall where a shadow falls) and is told to fix the shadow; the answer
goes back through a wide soft mask, so every pixel outside that mask stays the original.

This is the Portal's copy of the method. OpenFill keeps its own (installed app, openfill/app.py `_agentos_wide_fill`,
built on OpenFill's PhotoCraft I/O); the maths here mirrors it on plain numpy arrays so the Portal does not depend on
OpenFill's code. Pure functions, no network: the caller does SAM and the kie.ai call.

    box  = box_from_mask(mask, point)            # SAM mask -> object box (or point_box(point, W, H))
    p    = plan(rgb, box)                        # crop rect of an exact model ratio, shadow side, light words
    text = instruction("make the couch pink", p) # Tony's line + location + the fixed shadow/keep-the-rest suffix
    send = crop_for_model(rgb, p)                # PIL image, long side <= 2048
    out, alpha = composite(rgb, model_answer, p) # full picture; alpha == 0 -> original pixels, bit for bit
"""
import re

import cv2
import numpy as np
from PIL import Image

RATIOS = ((1, 1), (2, 3), (3, 2), (3, 4), (4, 3), (4, 5), (5, 4), (9, 16), (16, 9), (21, 9))
MIN_SIDE = 1024          # the crop's long side at least this (when the picture allows)
SEND_SIDE = 2048         # sent at most this big (Nano Banana answers at 2K)
GROW = 0.40              # the new object may be this much bigger than the box (of its long side)
SHADOW_REACH = 1.00      # room for the new shadow, along the light direction (of the box's long side)
CREDITS = 6              # kie.ai nano-banana-2-1 at 2K: 6 credits, about $0.03 (measured 2026-11-15)
ENGINE = "nb21"          # app/kie_edit.py MODELS key -> "nano-banana-2-1"
SUFFIX = (" Change nothing else in the picture: keep the same framing, perspective, colours, light and sharpness "
          "everywhere else.")
REMOVE_RE = re.compile(r"^\s*(please\s+)?(remove|erase|delete|get rid of|take out|take away)\b", re.I)


# ---------- where the object is ----------

def box_from_mask(mask, point=None, thr=0.5, min_part=0.05):
    """(x0, y0, x1, y1) around the object SAM found, or None. With a marked point, the part under (or nearest to)
    it; without, every part at least `min_part` of the biggest (specks dropped). Precision is not needed: the crop
    and the mask are wide."""
    m = (np.asarray(mask, np.float32) > thr).astype(np.uint8)
    n, lab, stats, cent = cv2.connectedComponentsWithStats(m, connectivity=8)
    if n <= 1:
        return None
    parts = list(range(1, n))
    if point is not None:
        x, y = int(round(point[0])), int(round(point[1]))
        if 0 <= y < lab.shape[0] and 0 <= x < lab.shape[1] and lab[y, x] > 0:
            keep = [int(lab[y, x])]
        else:
            keep = [min(parts, key=lambda i: (cent[i][0] - x) ** 2 + (cent[i][1] - y) ** 2)]
    else:
        big = max(stats[i, cv2.CC_STAT_AREA] for i in parts)
        keep = [i for i in parts if stats[i, cv2.CC_STAT_AREA] >= big * min_part]
    x0 = min(stats[i, cv2.CC_STAT_LEFT] for i in keep)
    y0 = min(stats[i, cv2.CC_STAT_TOP] for i in keep)
    x1 = max(stats[i, cv2.CC_STAT_LEFT] + stats[i, cv2.CC_STAT_WIDTH] for i in keep)
    y1 = max(stats[i, cv2.CC_STAT_TOP] + stats[i, cv2.CC_STAT_HEIGHT] for i in keep)
    return int(x0), int(y0), int(x1), int(y1)


def point_box(point, W, H, frac=0.15):
    """No SAM result but Tony clicked the object: a square of `frac` of the short side around the click."""
    s = max(16, int(min(W, H) * frac))
    x, y = float(point[0]), float(point[1])
    return clamp_box((x - s / 2, y - s / 2, x + s / 2, y + s / 2), W, H)


def clamp_box(b, W, H):
    x0, y0, x1, y1 = b
    x0, y0 = int(max(0, min(W - 1, round(x0)))), int(max(0, min(H - 1, round(y0))))
    x1, y1 = int(max(x0 + 1, min(W, round(x1)))), int(max(y0 + 1, min(H, round(y1))))
    return x0, y0, x1, y1


# ---------- the crop ----------

def wide_box(W, H, want):
    """The smallest box of an exact model ratio around `want` (x0, y0, x1, y1), inside the W x H picture.
    Returns ((x0, y0, x1, y1), "a:b")."""
    dw, dh = max(1.0, want[2] - want[0]), max(1.0, want[3] - want[1])
    best = None
    for a, b in RATIOS:
        r = a / b
        bw = max(dw, dh * r)
        bw, bh = int(round(bw)), int(round(bw / r))
        if bw <= W and bh <= H and (best is None or bw * bh < best[0] * best[1]):
            best = (bw, bh, f"{a}:{b}")
    if best is None:                       # the picture is smaller than the wish: the biggest ratio box inside it
        for a, b in RATIOS:
            r = a / b
            bw = int(min(W, H * r))
            bh = int(bw / r)
            if best is None or bw * bh > best[0] * best[1]:
                best = (bw, bh, f"{a}:{b}")
    bw, bh, ratio = best
    cx, cy = (want[0] + want[2]) / 2, (want[1] + want[3]) / 2
    x0 = int(min(max(0, round(cx - bw / 2)), W - bw))
    y0 = int(min(max(0, round(cy - bh / 2)), H - bh))
    return (x0, y0, x0 + bw, y0 + bh), ratio


def light_dir(rgb, box):
    """Where shadows fall: the brightest large area (a window, a sunlit patch) is the light; the shadow points from
    it through the box. Unit (dx, dy), or None for an evenly lit picture."""
    a = np.asarray(rgb, np.float32)[..., :3]
    lum = a @ np.float32([0.299, 0.587, 0.114])
    f = 16
    hh, ww = lum.shape[0] // f, lum.shape[1] // f
    if hh < 2 or ww < 2:
        return None
    small = lum[: hh * f, : ww * f].reshape(hh, f, ww, f).mean((1, 3))
    top = small >= np.percentile(small, 97)
    contrast = float(small[top].mean() / max(1.0, float(np.median(small))))
    ys, xs = np.nonzero(top)
    lx, ly = (xs.mean() + 0.5) * f, (ys.mean() + 0.5) * f
    dx, dy = (box[0] + box[2]) / 2 - lx, (box[1] + box[3]) / 2 - ly
    norm = (dx * dx + dy * dy) ** 0.5
    if contrast < 1.3 or norm < 1:
        return None
    return dx / norm, dy / norm


def plan(rgb, box, grow=GROW, reach=SHADOW_REACH, min_side=MIN_SIDE):
    """The wide crop around `box`: the box grown, swept along the shadow side, plus a margin, at least `min_side`
    long, then fitted to an exact model ratio inside the picture."""
    H, W = np.asarray(rgb).shape[:2]
    box = clamp_box(box, W, H)
    side = max(box[2] - box[0], box[3] - box[1])
    g, r = round(side * grow), round(side * reach)
    light = light_dir(rgb, box) if r > 0 else None
    sdx, sdy = (light[0] * r, light[1] * r) if light else (0.0, r * 0.5)   # even light: down and a little sideways
    zx0, zy0 = min(box[0], box[0] + sdx) - g, min(box[1], box[1] + sdy) - g
    zx1, zy1 = max(box[2], box[2] + sdx) + g, max(box[3], box[3] + sdy) + g
    m = max(64.0, side * 0.25)
    want = [zx0 - m, zy0 - m, zx1 + m, zy1 + m]
    long_side = max(want[2] - want[0], want[3] - want[1])
    if long_side < min_side:
        extra = (min_side - long_side) / 2
        if want[2] - want[0] >= want[3] - want[1]:
            want[0], want[2] = want[0] - extra, want[2] + extra
        else:
            want[1], want[3] = want[1] - extra, want[3] + extra
    crop, ratio = wide_box(W, H, want)
    words = []
    if light:
        if abs(light[0]) > 0.35:
            words.append("left" if light[0] < 0 else "right")
        if abs(light[1]) > 0.35:
            words.append("down" if light[1] > 0 else "up")
    return {"box": list(box), "crop": list(crop), "ratio": ratio, "grow": int(g), "shadow": [float(sdx), float(sdy)],
            "toward": words, "size": [W, H]}


def instruction(text, p):
    """Tony's own line, where the object sits in the crop (in words), and the fixed shadow / keep-the-rest suffix."""
    x0, y0, x1, y1 = p["crop"]
    w, h = x1 - x0, y1 - y0
    b = p["box"]

    def pct(v, n):
        return int(round(100.0 * min(max(v, 0), n) / n))
    loc = (f"the area from {pct(b[0] - x0, w)}% to {pct(b[2] - x0, w)}% across and {pct(b[1] - y0, h)}% to "
           f"{pct(b[3] - y0, h)}% down")
    what = text.strip().rstrip(".")
    if REMOVE_RE.match(what):
        out = (f"{what}. It is in {loc} of this picture. Remove it together with its cast shadow and any reflection "
               "of it, and rebuild what is behind it (floor, wall, skirting, lines, texture and light) exactly as it "
               "would look without it. Do not add anything new.")
    else:
        toward = f", falling toward the {' and '.join(p['toward'])}" if p.get("toward") else ""
        out = (f"In {loc} of this picture: {what}. Remove the old shadow of anything that was there before, and give "
               f"the new or changed object a natural cast shadow that matches the existing light direction{toward} "
               "and the other shadows in the picture.")
    return out + SUFFIX


def crop_for_model(rgb, p, send_side=SEND_SIDE):
    x0, y0, x1, y1 = p["crop"]
    im = Image.fromarray(np.asarray(rgb, np.uint8)[y0:y1, x0:x1, :3])
    if max(im.size) > send_side:
        f = send_side / max(im.size)
        im = im.resize((max(1, round(im.width * f)), max(1, round(im.height * f))), Image.LANCZOS)
    return im


# ---------- the composite ----------

def _blur(a, r):
    r = max(1, int(r))
    return cv2.GaussianBlur(a, (0, 0), r / 1.7 + 0.5)


def _dil(m, r):
    r = max(1, int(r))
    return cv2.dilate(m.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))) > 0


def composite(rgb, answer, p, protect=None):
    """Put the model's answer back. `answer` = PIL image (any size: resized to the crop). Returns (full uint8 RGB
    picture, full float alpha). Inside the box: the model's pixels. In the wide zone (box grown, swept along the
    shadow side): the model's pixels only where it changed something (and only its change of light on textured
    things such as wood grain, marble or a frame). Everywhere alpha is 0 the original pixels stay, bit for bit.
    `protect` = a polygon [[x, y], ...] in full-picture pixels (the art opening) that is never changed."""
    orig_full = np.asarray(rgb, np.uint8)[..., :3]
    H, W = orig_full.shape[:2]
    x0, y0, x1, y1 = p["crop"]
    w, h = x1 - x0, y1 - y0
    orig = orig_full[y0:y1, x0:x1].astype(np.float32)
    arr = np.asarray(answer.convert("RGB").resize((w, h), Image.LANCZOS), np.float32)
    b = p["box"]
    side = max(b[2] - b[0], b[3] - b[1])
    grow = max(2, int(p.get("grow") or round(side * GROW)))
    sel = np.zeros((h, w), bool)
    sel[max(0, b[1] - y0):max(0, b[3] - y0), max(0, b[0] - x0):max(0, b[2] - x0)] = True
    zone = _dil(sel, grow)
    sdx, sdy = p.get("shadow") or (0.0, 0.0)
    swept = np.zeros_like(sel)
    for i in range(1, 17):                      # the box slid along the shadow direction: the new shadow's room
        dx, dy = int(round(sdx * i / 16)), int(round(sdy * i / 16))
        sh = np.zeros_like(sel)
        ys, yd = (slice(0, max(0, h - dy)), slice(dy, h)) if dy >= 0 else (slice(-dy, h), slice(0, h + dy))
        xs, xd = (slice(0, max(0, w - dx)), slice(dx, w)) if dx >= 0 else (slice(-dx, w), slice(0, w + dx))
        if abs(dx) < w and abs(dy) < h:
            sh[yd, xd] = sel[ys, xs]
        swept |= sh
    zone |= _dil(swept, max(2, grow))
    feather = max(8, round(side * 0.06))
    zone_soft = np.clip(_blur(zone.astype(np.float32), feather) * 2.0, 0.0, 1.0)
    # a crop edge inside the picture fades out (a picture edge needs no fade)
    ramp = float(feather * 2)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    edge = np.ones((h, w), np.float32)
    if x0 > 0:
        edge = np.minimum(edge, xx / ramp)
    if x1 < W:
        edge = np.minimum(edge, (w - 1 - xx) / ramp)
    if y0 > 0:
        edge = np.minimum(edge, yy / ramp)
    if y1 < H:
        edge = np.minimum(edge, (h - 1 - yy) / ramp)
    edge = np.clip(edge, 0.0, 1.0)
    core_r = max(4, round(side * 0.03))
    core = np.clip(_blur(_dil(sel, core_r).astype(np.float32), core_r) * 2.0, 0.0, 1.0) * edge
    ring = np.clip(_blur(_dil(sel, grow).astype(np.float32), max(4, grow // 4)) * 2.0 - 0.5, 0.0, 1.0)
    gray = orig.mean(axis=2)
    density = _blur((np.abs(gray - _blur(gray, 2)) > 2.0).astype(np.float32), 14)
    smooth = np.clip((0.6 - density) / 0.2, 0.0, 1.0)
    diff = cv2.blur(np.abs(arr - orig).max(axis=2), (5, 5))
    change = np.clip((diff - 6.0) / 14.0, 0.0, 1.0)
    change = np.clip(_blur(change, max(3, feather // 3)) * 1.6, 0.0, 1.0)
    alpha = np.maximum(core, change * zone_soft * edge)
    if protect is not None and len(protect) >= 3:
        keep = np.zeros((H, W), np.uint8)
        cv2.fillPoly(keep, [np.round(np.asarray(protect, np.float32)).astype(np.int32)], 1)
        alpha = alpha * (1.0 - keep[y0:y1, x0:x1].astype(np.float32))
    alpha[alpha < 1.0 / 255] = 0.0
    ratio = np.clip((_blur(arr, 6) + 2.0) / (_blur(orig, 6) + 2.0), 0.2, 4.0)
    k = np.maximum(np.maximum(core, ring * change), change * smooth)[..., None]
    layer = arr * k + np.clip(orig * ratio, 0, 255) * (1.0 - k)
    a3 = alpha[..., None]
    mixed = np.clip(layer * a3 + orig * (1.0 - a3) + 0.5, 0, 255).astype(np.uint8)
    out = orig_full.copy()
    out[y0:y1, x0:x1] = np.where(a3 > 0, mixed, orig_full[y0:y1, x0:x1])
    full_alpha = np.zeros((H, W), np.float32)
    full_alpha[y0:y1, x0:x1] = alpha
    return out, full_alpha
