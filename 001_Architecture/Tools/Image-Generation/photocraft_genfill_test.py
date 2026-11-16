#!/usr/bin/env python3
"""End-to-end test of PhotoCraft Generative Fill (OpenFill + Agent-OS patch), as Tony would use it.

Drives the running "PhotoCraft with OpenFill" exactly like the panel's Generate button: opens a COPY of an
image, draws a rectangular selection, starts the Fill job on the chosen engine, waits, then saves the
flattened result and checks it against the original (what changed, and where).

usage:
  photocraft_genfill_test.py <image copy> <x> <y> <w> <h> "<instruction>" [--engine nano|qwen|<engine id>]
                             [--remove] [--tag NAME]
  - the image must be a copy inside ~/Library/Application Support/OpenFill for PhotoCraft/exchange/
  - nano = cloud:kie:nano-banana-2-1 (default, about $0.03 a call), qwen = local Qwen Edit 2511 Lightning
Writes GenFill_<tag>_After.png, GenFill_<tag>_Compare.png (before | after | changed pixels in red,
selection in green) into that exchange folder and prints a JSON line with seconds, changed pixels and
kie.ai credits used. Keys (KIE_API_KEY in ~/.env-secrets, the panel key, the control token) are read
from files and never printed.
"""
import argparse
import json
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

PROFILE = Path.home() / "Library/Application Support/OpenFill for PhotoCraft"
EX = PROFILE / "exchange"
sys.path.insert(0, str(PROFILE / "app"))
from openfill_photocraft.control import ControlClient  # noqa: E402

ENGINES = {"nano": "cloud:kie:nano-banana-2-1", "qwen": "qwen-image-edit-2511-lightning"}


def secret(name):
    for line in (Path.home() / ".env-secrets").read_text().splitlines():
        line = line.strip()
        line = line[7:] if line.startswith("export ") else line
        if line.startswith(name + "="):
            return line.split("=", 1)[1].strip().strip("'\"")
    return ""


def kie_credits():
    req = urllib.request.Request("https://api.kie.ai/api/v1/chat/credit",
                                 headers={"Authorization": "Bearer " + secret("KIE_API_KEY")})
    with urllib.request.urlopen(req, timeout=30) as r:
        return float(json.loads(r.read())["data"])


def api(path, body=None):
    url = (PROFILE / "page-url.txt").read_text().strip()
    base, key = url.split("/?key=")
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(base + path, data=data, method="POST" if data else "GET",
                                 headers={"X-OpenFill-Key": key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read() or b"{}")


def doc_index(c, name):
    for d in (c.call("ui.inspect").get("session") or {}).get("documents") or []:
        if d.get("name") == name:
            return int(d["index"])
    return None


def save_flat(c, index, rel):
    """Duplicate the document merged, save it as PNG at ``rel`` (relative to the exchange folder, PhotoCraft's
    automation write root), close the copy."""
    c.run("document.activate", document=index)
    name = f"GenFill check {int(time.time())}"
    c.run("image.duplicate", name=name, mergedOnly=True)
    copy = doc_index(c, name)
    c.run("document.activate", document=copy)
    c.call("app.save", path=rel)
    c.run("file.close", document=copy)
    c.run("document.activate", document=index)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("x", type=int)
    ap.add_argument("y", type=int)
    ap.add_argument("w", type=int)
    ap.add_argument("h", type=int)
    ap.add_argument("prompt")
    ap.add_argument("--engine", default="nano")
    ap.add_argument("--remove", action="store_true")
    ap.add_argument("--tag", default="")
    ap.add_argument("--check-only", action="store_true", help="no new job: only save and compare what is there")
    a = ap.parse_args()
    src = Path(a.image).resolve()
    if src.parent != EX.resolve():
        sys.exit(f"put the test copy in {EX} first (never the original template)")
    tag = a.tag or time.strftime("%H%M%S")
    engine = ENGINES.get(a.engine, a.engine)
    c = ControlClient(7878, PROFILE / "control.token")
    index = doc_index(c, src.name)
    if index is None:
        c.call("app.open", path=str(src.relative_to(Path.home())))
        for _ in range(40):
            time.sleep(0.5)
            index = doc_index(c, src.name)
            if index is not None:
                break
    c.run("document.activate", document=index)
    if not a.check_only:
        c.run("select.rect", x=a.x, y=a.y, width=a.w, height=a.h)
        time.sleep(1.5)  # the watcher sees the selection
    cloud = engine.startswith("cloud:kie:") and not a.check_only
    before = kie_credits() if cloud else None
    t0 = time.time()
    a.check_only or api("/api/fill", {"prompt": "" if a.remove else a.prompt, "remove": a.remove, "variations": 1, "seed": -1,
                      "model": engine, "removal": engine, "strength": 1.0, "negative": ""})
    state = {}
    while not a.check_only and time.time() - t0 < 900:
        time.sleep(2)
        state = api("/api/state")
        if not state.get("busy") and state["job"]["state"] not in ("running", "starting", ""):
            break
    secs = time.time() - t0
    job = state.get("job") or {}
    if job.get("variations"):
        api("/api/keep", {"which": "selected"})
        time.sleep(2)
    after = kie_credits() if cloud else None
    out = EX / f"GenFill_{tag}_After.png"
    save_flat(c, index, out.name)
    o = np.asarray(Image.open(src).convert("RGB"), np.int16)
    r = np.asarray(Image.open(out).convert("RGB"), np.int16)
    changed = np.abs(o - r).max(2) > 3
    ys, xs = np.nonzero(changed)
    bbox = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())] if len(xs) else None
    # compare picture: a crop around everything that changed
    pad = 120
    bx = (max(0, min(a.x, bbox[0] if bbox else a.x) - pad), max(0, min(a.y, bbox[1] if bbox else a.y) - pad),
          min(o.shape[1], max(a.x + a.w, bbox[2] if bbox else 0) + pad),
          min(o.shape[0], max(a.y + a.h, bbox[3] if bbox else 0) + pad))
    b_im, a_im = Image.open(src).convert("RGB").crop(bx), Image.open(out).convert("RGB").crop(bx)
    heat = a_im.copy()
    red = Image.new("RGB", heat.size, (255, 0, 0))
    m = Image.fromarray((changed[bx[1]:bx[3], bx[0]:bx[2]] * 160).astype(np.uint8), "L")
    heat.paste(red, (0, 0), m)
    ImageDraw.Draw(heat).rectangle([a.x - bx[0], a.y - bx[1], a.x + a.w - bx[0], a.y + a.h - bx[1]],
                                   outline=(0, 255, 0), width=4)
    cmp = Image.new("RGB", (b_im.width * 3 + 40, b_im.height), (30, 30, 30))
    for i, im in enumerate((b_im, a_im, heat)):
        cmp.paste(im, (i * (b_im.width + 20), 0))
    cmp.save(EX / f"GenFill_{tag}_Compare.png")
    print(json.dumps({"tag": tag, "engine": engine, "state": job.get("state"), "message": job.get("message"),
                      "seconds": round(secs, 1), "changed_px": int(changed.sum()), "changed_bbox": bbox,
                      "kie_credits_used": round(before - after, 2) if cloud else None}))


if __name__ == "__main__":
    main()
