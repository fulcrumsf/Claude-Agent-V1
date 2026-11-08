"""Remove an object (2026-11-08: the desk lamp) from EVERY light plate of a room with ONE paid image edit.

python remove_object.py <unlit_plate.png> <unlit_edited.png> <box x0,y0,x1,y1> <out_dir> [relit_plate.png ...] [--thresh 0.06]
(--thresh: raise it, e.g. 0.15, when the edit drifted in brightness so the mask would grow past the object)

1. The edit (kie.ai Nano Banana 2 on the unlit plate, prompt Light_Prompts/edit_remove_lamp.txt, 12 credits) is used
   ONLY inside the object mask: mask = where the edit differs from the original inside <box>, closed, hole-filled,
   grown and feathered. Everything else stays the original pixels (panel, books, shadows, frame position).
   The edit's small global colour drift is corrected by the original/edit ratio measured just outside the mask.
2. Each relit plate (same room, another light) gets the same patch, relit: its light ratio to the unlit plate is
   measured outside the mask and filled smoothly into it (normalised convolution), then multiplied onto the clean
   unlit patch. So no extra image edits per light.
Writes <out_dir>/<name>_nolamp.png for the unlit plate and each relit plate, plus object_mask.png.

3. Where step 2's smooth light fill cannot rebuild a hard light edge (golden-hour sun patch crossing the lamp head) or a
   detailed pattern (leaf dapple), that light gets its own edit, composited with step 1 (--thresh 0.15). To keep the
   derived pixels on the sideboard (the per-light edit moved the sideboard edge) use:
   python remove_object.py combine <derived.png> <edit_composite.png> <edit_mask.png> <x_max> <out.png>
   = edit composite only inside its mask left of x_max, the derived plate elsewhere.
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def load(p):
    return np.array(Image.open(p).convert("RGB")).astype("float32") / 255


def save(a, p):
    Image.fromarray((np.clip(a, 0, 1) * 255).round().astype("uint8")).save(p)


def fill(field, known, sigmas=(6, 16, 40, 100)):
    """Fill field where known==0 from its surroundings (normalised convolution, coarse scales only where needed)."""
    out = field.copy()
    have = known.astype("float32")
    for s in sigmas:
        num = cv2.GaussianBlur(out * have[..., None], (0, 0), s)
        den = cv2.GaussianBlur(have, (0, 0), s)[..., None]
        est = num / np.maximum(den, 1e-6)
        take = (have < 0.5) & (den[..., 0] > 0.02)
        out[take] = est[take]
        have = np.maximum(have, take.astype("float32"))
    return out


def object_mask(orig, edit, box, thresh=0.06):
    x0, y0, x1, y1 = box
    y = lambda a: a @ np.array([0.299, 0.587, 0.114], "float32")
    d = np.abs(cv2.GaussianBlur(y(edit), (0, 0), 1.5) - cv2.GaussianBlur(y(orig), (0, 0), 1.5))
    m = np.zeros(d.shape, "uint8")
    m[y0:y1, x0:x1] = (d[y0:y1, x0:x1] > thresh).astype("uint8")
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((25, 25), "uint8"))
    cnt, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    big = [c for c in cnt if cv2.contourArea(c) > 400]
    m = cv2.drawContours(np.zeros_like(m), big, -1, 1, thickness=cv2.FILLED)
    m = cv2.dilate(m, np.ones((15, 15), "uint8"))
    return np.clip(cv2.GaussianBlur(m.astype("float32"), (0, 0), 4) * 1.3, 0, 1)


def combine(derived, comp, mask, x_max, out):
    d, c = load(derived), load(comp)
    w = load(mask)[..., :1]
    w[:, x_max:] = 0
    w = cv2.GaussianBlur(w[..., 0], (0, 0), 3)[..., None]
    save(d * (1 - w) + c * w, out)


def main():
    if sys.argv[1] == "combine":
        return combine(sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]), sys.argv[6])
    orig, edit = load(sys.argv[1]), load(sys.argv[2])
    box = [int(v) for v in sys.argv[3].split(",")]
    out = Path(sys.argv[4])
    th = float(sys.argv[sys.argv.index("--thresh") + 1]) if "--thresh" in sys.argv else 0.06
    m = object_mask(orig, edit, box, th)
    save(np.repeat(m[..., None], 3, 2), out / "object_mask.png")
    known = m < 0.01
    ratio = fill(cv2.GaussianBlur(orig, (0, 0), 3) / np.maximum(cv2.GaussianBlur(edit, (0, 0), 3), 1e-3), known)
    clean = edit * np.clip(ratio, 0.7, 1.4)                 # the edit, colour-matched to the original around it
    mm = m[..., None]
    unlit = orig * (1 - mm) + clean * mm
    save(unlit, out / (Path(sys.argv[1]).stem + "_nolamp.png"))
    print({"mask_px": int((m > 0.5).sum()), "unlit": Path(sys.argv[1]).stem + "_nolamp.png"})
    for p in [a for i, a in enumerate(sys.argv[5:], 5) if a != "--thresh" and sys.argv[i - 1] != "--thresh"]:
        relit = load(p)
        light = fill(cv2.GaussianBlur(relit, (0, 0), 2) / np.maximum(cv2.GaussianBlur(orig, (0, 0), 2), 1e-3), known)
        res = relit * (1 - mm) + np.clip(unlit * light, 0, 1) * mm
        save(res, out / (Path(p).stem + "_nolamp.png"))
        print({"relit": Path(p).stem + "_nolamp.png"})


if __name__ == "__main__":
    main()
