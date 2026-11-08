"""Soften a relit plate's shadows without a new image generation (0 credits).

python soften_light.py <relit_plate.png> <unlit_plate.png> <out.png> [--gamma 0.55] [--target 0.30]

The relit plate (kie.ai edit of the unlit plate, same geometry within a few px) differs from the unlit plate mostly
by illumination. Illumination ratio R = luma(relit) / luma(unlit) (both lightly blurred so a few px of misalignment
does not matter). Shadows are lifted by compressing R toward its lit level: R' = R_lit * (R / R_lit) ** gamma, i.e.
more ambient fill light, the same pattern everywhere (wall, panel, sideboard), so the light story stays continuous.
With --target, gamma is searched so the magenta panel's shadow cover (luma < 0.75 x its p95) is about that value
(style guide 3a: shadow on the art <= 35 %).
Tried 2026-11-07 on the leaf-dapple plates and NOT used: lifting the shade washes the wall out and barely lowers the
measured cover (it is relative to the panel's own p95). The fix was one re-roll (light_b3_dapple_across.txt) instead.
Kept as a tool for plates where a shadow is simply too deep.
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "Portal" / "app").is_dir()) / "Portal"))   # Etsy-Ikigai/Portal
from app import rooms  # noqa: E402

W8 = np.array([0.2126, 0.7152, 0.0722], "float32")


def lin(x):
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def enc(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * x ** (1 / 2.4) - 0.055)


def soften(relit, unlit, gamma):
    a, b = lin(relit), lin(unlit)
    ya = cv2.GaussianBlur(a @ W8, (0, 0), 2.5)
    yb = cv2.GaussianBlur(b @ W8, (0, 0), 2.5)
    r = ya / np.maximum(yb, 1e-3)
    r_lit = float(np.percentile(r, 92))
    r2 = r_lit * np.clip(r / r_lit, 1e-3, None) ** gamma
    gain = cv2.GaussianBlur((r2 / np.maximum(r, 1e-4)).astype("float32"), (0, 0), 1.5)
    gain = np.clip(gain, 1.0, 4.0)                       # only ever lifts shadow, never darkens the sun
    return enc(a * gain[..., None])


def panel_cover(rgb8):
    mag = rooms.loose_magenta(rgb8)
    mag = cv2.erode(mag.astype("uint8"), np.ones((15, 15), "uint8")) > 0
    y = (rgb8.astype("float32") / 255) @ np.array([0.299, 0.587, 0.114], "float32")
    p95 = np.percentile(y[mag], 95)
    return float(((y < 0.75 * p95) & mag).sum() / mag.sum())


def main():
    relit = np.array(Image.open(sys.argv[1]).convert("RGB")).astype("float32") / 255
    unlit = np.array(Image.open(sys.argv[2]).convert("RGB")).astype("float32") / 255
    out = Path(sys.argv[3])
    arg = lambda k, d: float(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d
    gamma, target = arg("--gamma", 0.55), arg("--target", -1)
    print("cover before", round(panel_cover((relit * 255).astype("uint8")), 3))
    if target > 0:
        best = None
        for g in np.arange(1.0, 0.2, -0.05):
            img = (soften(relit, unlit, g) * 255).round().astype("uint8")
            c = panel_cover(img)
            if best is None or abs(c - target) < abs(best[1] - target):
                best = (g, c, img)
        gamma, cov, img = best
    else:
        img = (soften(relit, unlit, gamma) * 255).round().astype("uint8")
        cov = panel_cover(img)
    Image.fromarray(img).save(out)
    print({"gamma": round(float(gamma), 2), "cover_after": round(cov, 3), "out": str(out)})


if __name__ == "__main__":
    main()
