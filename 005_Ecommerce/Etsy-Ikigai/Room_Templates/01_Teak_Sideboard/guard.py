"""Accuracy guard (style guide 4c.8): unwarp the art from a render, compare hue of coloured pixels with the source file,
and measure shadow coverage of the art (panel light < 0.75 of its lit level).
python guard.py <tpl_dir> <render.png> <mat 0|1>"""
import json, sys
import cv2
import numpy as np
from PIL import Image


def run(tpl, render, mat):
    meta = json.loads(open(f"{tpl}/template.json").read())
    q = np.array(meta["quad_mat" if mat else "quad_nomat"], "float32")
    src = np.array(Image.open(f"{tpl}/art_fitted.png").convert("RGB"))
    h, w = src.shape[:2]
    Hm = cv2.getPerspectiveTransform(q, np.array([[0, 0], [w, 0], [w, h], [0, h]], "float32"))
    ren = cv2.warpPerspective(np.array(Image.open(render).convert("RGB")), Hm, (w, h))
    base = cv2.warpPerspective(np.array(Image.open(f"{tpl}/L_base.png").convert("RGB")), Hm, (w, h)).astype("float32")
    m = np.zeros((h, w), bool); mg = int(0.03 * h); m[mg:-mg, mg:-mg] = True        # skip the lip-shadow margin
    hs = cv2.cvtColor(src, cv2.COLOR_RGB2HSV_FULL).astype("float32"); hr = cv2.cvtColor(ren, cv2.COLOR_RGB2HSV_FULL).astype("float32")
    col = m & (hs[..., 1] > 90) & (hs[..., 2] > 60)
    d = (hr[..., 0] - hs[..., 0]) * 360 / 256
    d = (d + 180) % 360 - 180
    hue_shift = float(np.degrees(np.angle(np.mean(np.exp(1j * np.radians(d[col])))))) if col.any() else 0.0
    lum = base @ np.array([0.299, 0.587, 0.114], "float32")
    lit = np.percentile(lum[m], 95)
    cover = float(((lum < 0.75 * lit) & m).sum() / m.sum())
    return {"hue_shift_deg": round(hue_shift, 1), "hue_p90_abs": round(float(np.percentile(np.abs(d[col]), 90)), 1) if col.any() else 0,
            "shadow_cover": round(cover, 2), "pass": abs(hue_shift) <= 8 and cover <= 0.35}


if __name__ == "__main__":
    print(json.dumps(run(sys.argv[1], sys.argv[2], sys.argv[3] == "1")))
