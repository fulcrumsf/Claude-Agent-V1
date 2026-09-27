#!/usr/bin/env python3
"""Measured depth check for generated images/panels (2026-09-21). Replaces 'looks right' with numbers.

Runs Depth Anything V2 Small (Hugging Face, cached locally) on an image and reports, per object, its relative depth
(0 = farthest, 1 = nearest). Objects come from YOLO detection (COCO classes: person, bicycle, car, dog, bear, ...) and/or --box.
Use --expect "A<B" to assert 'A is CLOSER to the camera than B' (names are detection labels or --box names).

Usage:
  python3 check_depth.py <image> [--crop x0,y0,x1,y1] [--box name:x0,y0,x1,y1 ...] [--expect "person<wall" ...] [--depth-map out.png]
Limits: relative depth from one image (not metric distance); Depth Anything is monocular, so mirrored/reflective surfaces and very
flat scenes are less reliable. A detector name only exists for COCO classes (no monkey class: use --box)."""
import argparse, sys
from pathlib import Path
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
YOLO = HERE / "Subject-Aware-Reframer" / "Models" / "yolo11s.pt"
MODEL = "depth-anything/Depth-Anything-V2-Small-hf"


def depth_map(img: Image.Image) -> np.ndarray:
    import os
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    from transformers import pipeline
    pipe = pipeline("depth-estimation", model=MODEL)
    d = np.array(pipe(img)["depth"]).astype(float)     # larger = nearer
    d = (d - d.min()) / (d.max() - d.min() + 1e-9)
    if d.shape != (img.height, img.width):
        d = np.array(Image.fromarray((d * 255).astype("uint8")).resize(img.size, Image.BILINEAR)).astype(float) / 255
    return d


def detect(img: Image.Image, min_conf=0.35):
    from ultralytics import YOLO as Y
    r = Y(str(YOLO)).predict(np.array(img), conf=min_conf, verbose=False)[0]
    names = r.names; counts = {}; out = []
    for b, c, cf in zip(r.boxes.xyxy.cpu().numpy(), r.boxes.cls.cpu().numpy(), r.boxes.conf.cpu().numpy()):
        n = names[int(c)]; counts[n] = counts.get(n, 0) + 1
        out.append((n if counts[n] == 1 else f"{n}{counts[n]}", [float(v) for v in b], float(cf)))
    return out


def box_depth(d, b):
    x0, y0, x1, y1 = [int(v) for v in b]; return float(np.median(d[max(y0, 0):y1, max(x0, 0):x1]))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image", type=Path); ap.add_argument("--crop"); ap.add_argument("--box", action="append", default=[]); ap.add_argument("--expect", action="append", default=[])
    ap.add_argument("--depth-map", type=Path); ap.add_argument("--no-detect", action="store_true")
    a = ap.parse_args(); img = Image.open(a.image).convert("RGB")
    ox = oy = 0
    if a.crop:
        x0, y0, x1, y1 = [int(v) for v in a.crop.split(",")]; img = img.crop((x0, y0, x1, y1)); ox, oy = x0, y0
    d = depth_map(img); objs = {}
    if not a.no_detect:
        for n, b, cf in detect(img):
            objs[n] = b
    for spec in a.box:
        n, r = spec.split(":"); objs[n] = [float(v) - (ox if i % 2 == 0 else oy) for i, v in enumerate(r.split(","))]
    print("Relative depth (1 = nearest, 0 = farthest):")
    vals = {n: box_depth(d, b) for n, b in objs.items()}
    for n, v in sorted(vals.items(), key=lambda kv: -kv[1]):
        print(f"  {n:14s} {v:.2f}")
    bad = 0
    for e in a.expect:
        near, far = [t.strip() for t in e.split("<")]
        if near not in vals or far not in vals:
            print(f"  EXPECT {e}: cannot check (missing object: {[t for t in (near, far) if t not in vals]})"); bad += 1; continue
        ok = vals[near] > vals[far] + 0.03
        print(f"  EXPECT {near} closer than {far}: {'PASS' if ok else 'FAIL'} ({vals[near]:.2f} vs {vals[far]:.2f})"); bad += (not ok)
    if a.depth_map:
        Image.fromarray((d * 255).astype("uint8")).save(a.depth_map)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
