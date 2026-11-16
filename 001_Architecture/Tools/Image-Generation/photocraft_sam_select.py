#!/usr/bin/env python3
"""Type a word, get a PhotoCraft selection: "select the lamp" like Photoshop's Select Subject / Object Selection.

    python3 photocraft_sam_select.py "lamp" [--threshold 0.5] [--grow 0] [--mask-only out.png]

How it works (plan: 005_Ecommerce/Etsy-Ikigai/Research/OpenFill_PhotoCraft_Plan.md, SAM section 3a):
  1. Reads the active PhotoCraft document (a merged copy saved to OpenFill's exchange folder; the
     document itself is not changed).
  2. Runs SAM 3.1 (text prompt) in the Pinokio ComfyUI on 127.0.0.1:8188 -> a full-size mask.
  3. Softens the mask edge with a guided filter that follows the photo's own edges (anti-aliased,
     no staircase from SAM's 1008 px working size).
  4. Opens the mask as a document, loads it as the selection of the photo (select.loadSelection,
     red channel, new selection), closes the mask document.
Then press Fill or Remove in OpenFill as usual.

Needs: PhotoCraft started through "PhotoCraft with OpenFill" (control port 7878; the token file stays
unread by humans and is never printed) and ComfyUI started from Pinokio with the SAM 3.1 checkpoint
(models/checkpoints/sam3.1_multiplex_fp16.safetensors). Runs entirely on this Mac.
"""
import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

import numpy as np
from PIL import Image

PROFILE = Path.home() / "Library/Application Support/OpenFill for PhotoCraft"
sys.path.insert(0, str(PROFILE / "app"))
from openfill_photocraft.control import ControlClient  # noqa: E402

COMFY = "http://127.0.0.1:8188"
SAM_CKPT = "sam3.1_multiplex_fp16.safetensors"
EXCHANGE = PROFILE / "exchange"


def _post(path, data, ctype="application/json"):
    req = urllib.request.Request(COMFY + path, data=data, headers={"Content-Type": ctype}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def _upload(png: Path) -> str:
    b = "----sam" + uuid.uuid4().hex
    body = (f'--{b}\r\nContent-Disposition: form-data; name="image"; filename="{png.name}"\r\n'
            "Content-Type: image/png\r\n\r\n").encode() + png.read_bytes() + \
        f'\r\n--{b}\r\nContent-Disposition: form-data; name="overwrite"\r\n\r\ntrue\r\n--{b}--\r\n'.encode()
    return _post("/upload/image", body, f"multipart/form-data; boundary={b}")["name"]


def sam3_mask(png: Path, text: str, threshold: float = 0.5) -> tuple[np.ndarray, float]:
    """Full-size mask (0..1 float) of every ``text`` object SAM 3.1 finds, and the seconds it took."""
    name = _upload(png)
    g = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": SAM_CKPT}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["1", 1], "text": text}},
        "3": {"class_type": "LoadImage", "inputs": {"image": name}},
        "4": {"class_type": "SAM3_Detect", "inputs": {"model": ["1", 0], "image": ["3", 0], "conditioning": ["2", 0],
                                                       "threshold": threshold, "refine_iterations": 2,
                                                       "individual_masks": False}},
        "5": {"class_type": "MaskToImage", "inputs": {"mask": ["4", 0]}},
        "6": {"class_type": "SaveImage", "inputs": {"images": ["5", 0], "filename_prefix": "agentos_sam/mask"}},
    }
    t0 = time.time()
    pid = _post("/prompt", json.dumps({"prompt": g, "client_id": "agentos-sam"}).encode())["prompt_id"]
    while True:
        with urllib.request.urlopen(f"{COMFY}/history/{pid}", timeout=30) as r:
            h = json.loads(r.read())
        st = h.get(pid, {}).get("status", {})
        if st.get("completed") or st.get("status_str") == "error":
            break
        time.sleep(0.3)
    if st.get("status_str") == "error":
        msg = [m for m in st.get("messages", []) if m[0] == "execution_error"]
        raise RuntimeError(f"SAM 3 failed in ComfyUI: {str(msg)[:400]}")
    img = h[pid]["outputs"]["6"]["images"][0]
    q = urllib.parse.urlencode({"filename": img["filename"], "subfolder": img["subfolder"], "type": img["type"]})
    with urllib.request.urlopen(f"{COMFY}/view?{q}", timeout=60) as r:
        mask = Image.open(__import__("io").BytesIO(r.read())).convert("L")
    return np.asarray(mask, dtype=np.float32) / 255.0, time.time() - t0


def _box(a: np.ndarray, r: int) -> np.ndarray:
    """Mean over a (2r+1)^2 window (integral image)."""
    c = np.pad(a, ((r + 1, r), (r + 1, r)), mode="edge").cumsum(0).cumsum(1)
    k = 2 * r + 1
    return (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / (k * k)


def guided_soften(mask: np.ndarray, photo: Image.Image, r: int = 3, eps: float = 1e-3) -> np.ndarray:
    """Guided filter (He et al.) with the photo's luminance as guide: the edge lands on the object's
    real edge and is anti-aliased. Only a band around the hard edge changes."""
    g = np.asarray(photo.convert("L"), dtype=np.float32) / 255.0
    mg, mp = _box(g, r), _box(mask, r)
    cov = _box(g * mask, r) - mg * mp
    var = _box(g * g, r) - mg * mg
    a = cov / (var + eps)
    b = mp - a * mg
    out = _box(a, r) * g + _box(b, r)
    band = (_box(mask, r + 2) > 0.001) & (_box(mask, r + 2) < 0.999)
    return np.clip(np.where(band, out, mask), 0.0, 1.0)


def grow(mask: np.ndarray, px: int) -> np.ndarray:
    if px <= 0:
        return mask
    return (_box((mask > 0.5).astype(np.float32), px) > 0.0).astype(np.float32).clip(mask, 1.0)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("text")
    ap.add_argument("--threshold", type=float, default=0.5)
    ap.add_argument("--grow", type=int, default=0, help="expand the selection by N px (Photoshop: Select > Modify > Expand)")
    ap.add_argument("--mask-only", help="write the mask PNG here and do not touch the selection")
    ap.add_argument("--port", type=int, default=7878)
    args = ap.parse_args()

    pc = ControlClient(args.port, PROFILE / "control.token")
    session = pc.call("ui.inspect")["session"]
    docs = session.get("documents") or []
    if not docs:
        print("Open an image in PhotoCraft first.")
        return 1
    active = session.get("active")
    photo_doc = next(d for d in docs if d.get("index") == active)
    stamp = uuid.uuid4().hex[:8]
    # 1. the visible image, merged, without touching the document
    pc.run("image.duplicate", name=f"sam-{stamp}", mergedOnly=True)
    pc.call("app.save", path=f"sam-{stamp}.png")
    pc.run("file.close")
    pc.run("document.activate", document=active)
    src = EXCHANGE / f"sam-{stamp}.png"
    photo = Image.open(src).convert("RGB")
    # 2. SAM 3.1
    mask, secs = sam3_mask(src, args.text, args.threshold)
    if mask.shape != (photo.height, photo.width):
        mask = np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).resize(photo.size, Image.BILINEAR),
                          dtype=np.float32) / 255.0
    found = float((mask > 0.5).mean())
    if found == 0.0:
        print(f"SAM 3 found no '{args.text}' ({secs:.1f} s). Try another word or a lower --threshold.")
        return 2
    # 3. edges
    soft = guided_soften(grow(mask, args.grow), photo)
    out = Image.fromarray((soft * 255 + 0.5).astype(np.uint8), "L")
    mask_path = EXCHANGE / f"sam-{stamp}-mask.png"
    out.convert("RGB").save(mask_path)
    if args.mask_only:
        out.save(args.mask_only)
        print(f"mask written: {args.mask_only} ({found:.1%} of the image, SAM {secs:.1f} s)")
        return 0
    # 4. load it as the selection
    pc.call("app.open", path=os.path.relpath(mask_path, Path.home()))
    session = pc.call("ui.inspect")["session"]
    mask_doc = next(d for d in session["documents"] if d.get("name", "").startswith(f"sam-{stamp}-mask"))
    photo_idx = next(d["index"] for d in session["documents"] if d.get("name") == photo_doc.get("name"))
    pc.run("document.activate", document=photo_idx)
    pc.run("select.loadSelection", document=mask_doc["index"], channel="red", operation="new")
    pc.run("file.close", document=mask_doc["index"])
    session = pc.call("ui.inspect")["session"]
    photo_idx = next(d["index"] for d in session["documents"] if d.get("name") == photo_doc.get("name"))
    pc.run("document.activate", document=photo_idx)
    bounds = pc.run("document.inspect").get("selectionBounds")
    print(f"selected '{args.text}' in {photo_doc.get('name')}: bounds {bounds}, SAM {secs:.1f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
