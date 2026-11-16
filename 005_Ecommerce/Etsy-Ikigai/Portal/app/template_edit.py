"""Templates tab: "Edit with chat" and "Open in PhotoCraft" (Tony 2026-11-10, Ikigai_Portal_Build_Plan section 4).

Edit with chat (a large overlay: room left, chat right, before/after):
  - start: the template PSD is COPIED to a working file in the gallery cache (data/rooms/Edit_<key>_v<N>.psd); the
    template itself is untouched until Tony presses Save.
  - each chat line becomes a short list of LAYER edits, checked against an allow-list and run headless with
    photocraft-cli on the working copy (never `layer.delete`): show/hide, opacity, blend, rename, move, blur a layer,
    the art smart object's corners, retire a layer (hide + rename "OLD ... (retire)"), heal a small spot on the
    BASE layer (spot healing at the point Tony clicked). The translator is the Portal's headless Claude CLI (no
    tools) with the layer list; simple lines ("hide Glass Sheen", "Light Shadow opacity 12%") are parsed without it.
  - a real pixel change ("make the couch pink", "remove the lamp") is a generative fill, wide-crop method
    (app/wide_fill.py, proven 2026-11-15): SAM 3.1 in the local ComfyUI finds the object by its name (or the spot
    Tony clicked), a wide crop around it goes to kie.ai Nano Banana 2.1 with his line plus a fixed shadow /
    keep-everything-else suffix, and the answer is composited back through a wide soft mask (every pixel outside it
    stays the original). Cost (6 credits, about $0.03) is shown first and runs only after Tony confirms; the edited
    picture becomes a new layer above BASE, the old BASE is retired (hidden + "OLD BASE ... (retire)").
  - Save: the old PSD moves into the template folder's Archive/ (pre-approved by Tony), the edited copy takes its
    name, and the template checker runs on it. Discard: nothing changes. The X asks Save / Discard when unsaved.
Open in PhotoCraft: opens the template in "PhotoCraft with OpenFill" (~/Applications, PhotoCraft 0.23 + the OpenFill
bar, control port 7878) so Tony can use Filter > Plug-ins > Generative Fill... by hand; selects the layer he names.
It never saves the document: Tony saves in PhotoCraft himself (that writes the template PSD directly). The old
ArtCraft PhotoCraft (/Applications/ArtCraft) stays the Portal's headless layer tool (photocraft-cli); setting
photocraft_open_with = "artcraft" opens that one instead (control port 47811, `photocraft-cli mcp --bridge`).
"""
import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path

from . import template_checker as tc
from . import template_gallery as tg
from . import wide_fill as wf

APP = "/Applications/ArtCraft/PhotoCraft.app/Contents/MacOS/photocraft"
OPENFILL_LAUNCHER = Path.home() / "Applications/PhotoCraft with OpenFill.app/Contents/MacOS/openfill-photocraft"
OPENFILL_PROFILE = Path.home() / "Library/Application Support/OpenFill for PhotoCraft"
IMAGE_GEN = next((p / "001_Architecture/Tools/Image-Generation" for p in Path(__file__).resolve().parents
                  if (p / "001_Architecture").is_dir()), None)
IMAGE_EDIT_CREDITS = wf.CREDITS
BLENDS = ["Normal", "Multiply", "Screen", "Overlay", "Soft Light", "Hard Light", "Darken", "Lighten", "Linear Burn",
          "Color Burn", "Color Dodge", "Linear Dodge (Add)"]
_sessions = {}
_lock = threading.Lock()


class EditError(Exception):
    pass


def _key(rel):
    return hashlib.sha1(rel.encode()).hexdigest()[:12]


def _cache(settings):
    return tg.cache_dir(settings)


def _run(settings, args, timeout=300):
    return tc._run(settings, args, timeout)


def _cmd(c, p=None):
    return ["--cmd", c, "--params", json.dumps(p or {})]


def _template(settings, rel):
    t = next((x for x in tg.scan(settings)[0] if x["rel"] == rel), None)
    if t is None:
        raise EditError("no such template")
    if t.get("wired"):
        raise EditError("the Teak Sideboard is edited in PhotoCraft by hand (Open in PhotoCraft)")
    return t


def layers_of(psd, settings=None):
    inf = tc.info(psd, settings)
    out = []
    for l in tc.flatten(inf.get("layers")):
        out.append({k: l.get(k) for k in ("id", "name", "kind", "blend", "opacity", "visible", "bounds", "hasMask",
                                           "clipped")} | {"group": " / ".join(l["parents"])})
    return out, [int(inf["width"]), int(inf["height"])]


def _render(psd, out_jpg, settings, card_px=None, work=None):
    """The working copy with the AMBER test card in the art (the gallery's "Show art area" card, Tony 2026-11-15:
    amber = exactly where the art shows), as a JPG <= 1800 px wide."""
    import tempfile
    from PIL import Image
    work = Path(work or _cache(settings))
    args = ["run", str(psd)]
    if card_px:
        card = work / f"Edit_tint_{card_px[0]}x{card_px[1]}.png"
        if not card.is_file():
            tg.tint_card(card_px[0], card_px[1], card)
        args += _cmd("layer.select", {"name": tc.ART}) + _cmd("layer.smartObjects.replaceContents", {"path": str(card)})
    with tempfile.TemporaryDirectory() as td:          # the full-size PNG lives in a temp folder only
        png = Path(td) / "render.png"
        _run(settings, args + ["--out", str(png)])
        with Image.open(png) as im:
            im = im.convert("RGB")
            if im.width > 1800:
                im = im.resize((1800, round(im.height * 1800 / im.width)), Image.LANCZOS)
            im.save(out_jpg, quality=88)
    return out_jpg


def _url(prefix, p):
    st = Path(p).stat()
    return f"{prefix}/api/templates/edit-file/{Path(p).name}?v={st.st_mtime_ns:x}"


def edit_file(name, settings=None):
    if not re.fullmatch(r"Edit_[0-9a-f]{12}_v\d+\.jpg", name):
        return None
    f = _cache(settings) / name
    return f if f.is_file() else None


def state(rel, settings=None, prefix="/ikigai"):
    s = _sessions.get(rel)
    if not s:
        return {"rel": rel, "open": False}
    v = s["versions"]
    return {"rel": rel, "open": True, "name": s["name"], "versions": len(v) - 1, "dirty": len(v) > 1,
            "before": _url(prefix, v[0]["jpg"]), "after": _url(prefix, v[-1]["jpg"]), "log": s["log"],
            "quad": v[-1].get("quad"), "layers": s["layers"], "canvas": s["canvas"], "busy": s.get("busy", False),
            "pending": {k: v for k, v in s["pending"].items() if k in ("credits", "box", "target", "text")}
            if s.get("pending") else None}


def start(rel, settings=None, prefix="/ikigai"):
    """Open (or reopen) an edit session: copy the PSD to the cache and render the 'before'."""
    t = _template(settings, rel)
    with _lock:
        if rel in _sessions:
            return state(rel, settings, prefix)
    k = _key(rel)
    c = _cache(settings)
    c.mkdir(parents=True, exist_ok=True)              # data/rooms already exists (the gallery cache)
    psd0 = c / f"Edit_{k}_v0.psd"
    shutil.copy2(t["psd"], psd0)
    try:
        so = tc.so_size(psd0, settings, c)
    except Exception:  # noqa: BLE001
        so = None
    jpg0 = _render(psd0, c / f"Edit_{k}_v0.jpg", settings, so)
    layers, canvas = layers_of(psd0, settings)
    quad = None                                       # the art area, for the editor's orange onion-skin tint
    try:
        man = json.loads((Path(t["psd"]).parent / "template.json").read_text())
        quad = man.get("quad_art") or None
    except Exception:  # noqa: BLE001  (no manifest: no tint)
        pass
    st = t["psd"].stat()
    with _lock:
        _sessions[rel] = {"name": t["name"], "psd": str(t["psd"]), "so": so, "key": k, "layers": layers,
                          "canvas": canvas, "orig": [st.st_size, st.st_mtime_ns],
                          "versions": [{"psd": psd0, "jpg": jpg0, "ops": [], "quad": quad}],
                          "log": [{"who": "studio", "text": "Tell me what to change: shadows, glare, mat, frame, the "
                                   "art corners, things in the room (\"make the couch pink\", \"remove the lamp\"), "
                                   "or click the picture to mark a spot."}]}
    return state(rel, settings, prefix)


# ---------- translating a chat line into layer edits ----------

SYSTEM = """You turn one instruction about a PhotoCraft room-mockup template into layer edits. Reply with ONLY a JSON
object: {"reply": "<one short plain sentence for Tony>", "ops": [ ... ]}. Allowed ops (use layer ids from the list):
 {"op":"set","layer":ID,"visible":bool?,"opacity":0..1?,"blend":"Multiply|Screen|Normal|..."?,"name":str?}
 {"op":"move","layer":ID,"dx":int,"dy":int}
 {"op":"blur","layer":ID,"radius":px}
 {"op":"corners","quad":[[x,y],[x,y],[x,y],[x,y]]}   (the art smart object 'Place Artwork Here', clockwise from top-left)
 {"op":"retire","layer":ID}                           (hide + rename "OLD ... (retire)"; layers are NEVER deleted)
 {"op":"heal","points":[[x,y],...],"size":px}         (small removals on the BASE layer at Tony's marked point)
 {"op":"image_edit","prompt":"<what to change in the room photo>","target":"<the one thing to change, 1-2 words, e.g. couch>"}
     (real pixel changes to things in the room photo only; costs credits; "target" is what SAM looks for)
Shadows are black fills (Multiply), glare is white (Screen). Never invent layer ids. If the instruction is unclear,
reply with a question and no ops."""


def _find_layer(layers, words):
    words = words.strip().strip("'\"").lower()
    exact = [l for l in layers if (l["name"] or "").lower() == words]
    if exact:
        return exact[0]
    part = [l for l in layers if words and words in (l["name"] or "").lower()]
    return part[0] if len(part) == 1 else None


def quick_parse(text, layers, point=None):
    """Simple lines without the model: 'hide X', 'show X', 'X opacity 20%', 'blur X 4', 'move X left 6',
    'retire X', 'remove this' (with a marked point). Returns (reply, ops) or None."""
    t = text.strip()
    m = re.fullmatch(r"(hide|show)\s+(.+)", t, re.I)
    if m and (l := _find_layer(layers, m.group(2))):
        return f"{m.group(1).title()} {l['name']}.", [{"op": "set", "layer": l["id"], "visible": m.group(1).lower() == "show"}]
    m = re.fullmatch(r"(?:set\s+)?(.+?)\s+(?:opacity\s+(?:to\s+)?)(\d{1,3})\s*%?", t, re.I)
    if m and (l := _find_layer(layers, m.group(1))):
        return f"{l['name']} opacity {m.group(2)}%.", [{"op": "set", "layer": l["id"], "opacity": int(m.group(2)) / 100}]
    m = re.fullmatch(r"blur\s+(.+?)\s+(?:by\s+)?(\d+(?:\.\d+)?)\s*(?:px)?", t, re.I)
    if m and (l := _find_layer(layers, m.group(1))):
        return f"Blurred {l['name']} by {m.group(2)} px.", [{"op": "blur", "layer": l["id"], "radius": float(m.group(2))}]
    m = re.fullmatch(r"move\s+(.+?)\s+(left|right|up|down)\s+(\d+)\s*(?:px)?", t, re.I)
    if m and (l := _find_layer(layers, m.group(1))):
        n = int(m.group(3))
        dx, dy = {"left": (-n, 0), "right": (n, 0), "up": (0, -n), "down": (0, n)}[m.group(2).lower()]
        return f"Moved {l['name']} {m.group(2)} {n} px.", [{"op": "move", "layer": l["id"], "dx": dx, "dy": dy}]
    m = re.fullmatch(r"retire\s+(.+)", t, re.I)
    if m and (l := _find_layer(layers, m.group(1))):
        return f"Retired {l['name']} (hidden, renamed OLD; Tony deletes).", [{"op": "retire", "layer": l["id"]}]
    if point and re.search(r"\b(remove|erase|heal|clean|get rid of)\b", t, re.I):
        size = 40
        m = re.search(r"(\d+)\s*px", t)
        if m:
            size = int(m.group(1))
        return f"Healed the marked spot ({size} px).", [{"op": "heal", "points": [point], "size": size}]
    return None


def translate(text, layers, point=None, settings=None, ask=None):
    q = quick_parse(text, layers, point)
    if q:
        return q
    from . import assistant
    lines = "\n".join(f"{l['id']}: {l['name']} [{l['kind']}, {l['blend']}, opacity {round((l['opacity'] or 1) * 100)}%"
                      f"{', hidden' if not l['visible'] else ''}{', in ' + l['group'] if l['group'] else ''}"
                      f"{', bounds ' + str(l['bounds']) if l.get('bounds') else ''}]" for l in layers)
    prompt = f"Layers (top first):\n{lines}\n\nMarked point: {point or 'none'}\n\nInstruction: {text}"
    raw = (ask or (lambda p: assistant.run_cli(p, SYSTEM, "sonnet", "haiku", 90, settings, "The edit chat")))(prompt)
    m = re.search(r"\{.*\}", raw or "", re.S)
    try:
        obj = json.loads(m.group(0)) if m else {}
    except ValueError:
        obj = {}
    return str(obj.get("reply") or "I could not turn that into a layer edit."), list(obj.get("ops") or [])


def validate(ops, layers, canvas):
    """Allow-list check; returns the ops to run (raises EditError with a plain reason)."""
    ids = {l["id"]: l for l in layers}
    W, H = canvas
    good = []
    for o in ops:
        k = o.get("op")
        if k in ("set", "move", "blur", "retire") and o.get("layer") not in ids:
            raise EditError(f"unknown layer {o.get('layer')}")
        if k == "set":
            p = {"layer": o["layer"]}
            if "visible" in o:
                p["visible"] = bool(o["visible"])
            if "opacity" in o:
                p["opacity"] = min(1.0, max(0.0, float(o["opacity"])))
            if o.get("blend"):
                if o["blend"] not in BLENDS:
                    raise EditError(f"blend {o['blend']} is not allowed")
                p["blend"] = o["blend"]
            if o.get("name"):
                p["name"] = str(o["name"])[:80]
            good.append({"op": "set", **p})
        elif k == "move":
            good.append({"op": "move", "layer": o["layer"], "dx": int(o["dx"]), "dy": int(o["dy"])})
        elif k == "blur":
            good.append({"op": "blur", "layer": o["layer"], "radius": min(200.0, max(0.1, float(o["radius"])))})
        elif k == "retire":
            good.append({"op": "retire", "layer": o["layer"]})
        elif k == "corners":
            q = [[float(x), float(y)] for x, y in o["quad"]]
            if len(q) != 4 or any(not (-W < x < 2 * W and -H < y < 2 * H) for x, y in q):
                raise EditError("the corners are off the picture")
            good.append({"op": "corners", "quad": q})
        elif k == "heal":
            pts = [[float(x), float(y)] for x, y in o["points"]][:20]
            good.append({"op": "heal", "points": pts, "size": min(400, max(4, int(o.get("size", 40))))})
        elif k == "image_edit":
            good.append({"op": "image_edit", "prompt": str(o.get("prompt", ""))[:600],
                         "target": str(o.get("target") or "")[:40]})
        else:
            raise EditError(f"'{k}' is not an allowed edit (layers are never deleted)")
    return good


def base_layer(layers):
    """The room photo: the bottom-most visible pixel/smart-object layer that is not the art and not a retired OLD
    layer (after an image edit the old BASE is still at the bottom, hidden and renamed OLD)."""
    art = [l for l in layers if l["name"] == tc.ART]
    cand = [l for l in layers if l["kind"] in ("Pixel", "Smart Object") and l not in art]
    live = [l for l in cand if l.get("visible", True) and not (l["name"] or "").startswith("OLD ")]
    return (live or cand or [None])[-1]


def commands(ops, layers):
    ids = {l["id"]: l for l in layers}
    art = next((l for l in layers if l["name"] == tc.ART), None)
    base = base_layer(layers)
    a = []
    for o in ops:
        if o["op"] == "set":
            a += _cmd("layer.setProps", {k: v for k, v in o.items() if k != "op"})
        elif o["op"] == "move":
            a += _cmd("layer.translate", {"layer": o["layer"], "dx": o["dx"], "dy": o["dy"]})
        elif o["op"] == "blur":
            a += _cmd("select.deselect") + _cmd("layer.select", {"layer": o["layer"]})
            a += _cmd("filter.blur.gaussianBlur", {"radius": o["radius"]})
        elif o["op"] == "retire":
            nm = ids[o["layer"]]["name"]
            a += _cmd("layer.setProps", {"layer": o["layer"], "visible": False,
                                         "name": nm if nm.startswith("OLD ") else f"OLD {nm} (retire)"})
        elif o["op"] == "corners" and art:
            x, y, w, h = art["bounds"]
            a += _cmd("select.deselect") + _cmd("layer.select", {"layer": art["id"]})
            a += _cmd("edit.transform", {"layer": art["id"], "rect": [x, y, x + w, y + h], "quad": o["quad"]})
        elif o["op"] == "heal" and base:
            a += _cmd("select.deselect") + _cmd("layer.select", {"layer": base["id"]})
            a += _cmd("paint.spotHealing", {"points": [[x, y, 1.0] for x, y in o["points"]], "size": o["size"],
                                            "layer": base["id"], "type": "contentAware"})
    return a


def chat(rel, text, point=None, settings=None, prefix="/ikigai", ask=None, sam=None):
    """One chat line: translate, validate, run on the working copy, render the new 'after'."""
    s = _sessions.get(rel)
    if not s:
        raise EditError("open the editor first")
    if s.get("busy"):
        raise EditError("still working on the last edit")
    s["log"].append({"who": "tony", "text": text})
    s["busy"] = True
    try:
        reply, ops = translate(text, s["layers"], point, settings, ask)
        ops = validate(ops, s["layers"], s["canvas"])
        paid = [o for o in ops if o["op"] == "image_edit"]
        if paid:
            ops = [o for o in ops if o["op"] != "image_edit"]
            _plan_fill(s, paid[0], text, point, reply, settings, sam)
        if ops:
            _apply(s, ops, settings)
        if not paid:
            s["log"].append({"who": "studio", "text": reply if ops else (reply or "Nothing to change.")})
    except Exception as e:  # noqa: BLE001  (shown in the chat)
        s["log"].append({"who": "studio", "text": f"That did not work: {str(e)[:200]}"})
    finally:
        s["busy"] = False
    return state(rel, settings, prefix)


def _apply(s, ops, settings, extra_args=()):
    c = Path(s["versions"][-1]["psd"]).parent
    n = len(s["versions"])
    psd = c / f"Edit_{s['key']}_v{n}.psd"
    _run(settings, ["run", str(s["versions"][-1]["psd"]), *commands(ops, s["layers"]), *extra_args, "--out", str(psd)])
    if not psd.is_file():
        raise EditError("PhotoCraft did not write the edited copy")
    jpg = _render(psd, c / f"Edit_{s['key']}_v{n}.jpg", settings, s["so"])
    s["layers"], s["canvas"] = layers_of(psd, settings)
    quad = s["versions"][-1].get("quad")
    for o in ops:                                     # moving the art corners moves the tint with them
        if o["op"] == "corners":
            quad = o["quad"]
    s["versions"].append({"psd": psd, "jpg": jpg, "ops": ops, "quad": quad})


TARGET_RE = re.compile(r"\b(?:the|that|this|a|an)\s+([a-z][a-z-]*(?:\s+[a-z][a-z-]*)?)", re.I)
STOP = {"same", "whole", "picture", "image", "photo", "room", "colour", "color", "left", "right", "top", "bottom"}


def guess_target(text):
    """'make the couch pink' -> 'couch' (the translator normally names it; this is the fallback)."""
    for m in TARGET_RE.finditer(text or ""):
        w = m.group(1).split()
        w = [x for x in w if x.lower() not in STOP and x.lower() not in ("pink", "red", "blue", "green", "white",
                                                                           "black", "grey", "gray", "with", "into")]
        if w:
            return " ".join(w[:2]).lower()
    return ""


def base_png(s, settings):
    """The BASE photo alone, full size (every other layer hidden), from the latest working copy."""
    base = base_layer(s["layers"])
    if base is None:
        raise EditError("no BASE layer")
    c = Path(s["versions"][-1]["psd"]).parent
    src = c / f"Edit_{s['key']}_base_v{len(s['versions']) - 1}.png"
    if not src.is_file():
        hide = [l["id"] for l in s["layers"] if l["id"] != base["id"] and l["kind"] != "Group"]
        _run(settings, ["run", str(s["versions"][-1]["psd"]), *tc._hide(hide), "--out", str(src)])
    return base, src


def sam_mask(png, word, settings=None):
    """SAM 3.1 (text prompt) in the local ComfyUI (Pinokio, 127.0.0.1:8188): a full-size 0..1 mask. Reuses
    001_Architecture/Tools/Image-Generation/photocraft_sam_select.py (the PhotoCraft 'select the lamp' bridge)."""
    import importlib
    import sys
    if IMAGE_GEN is None or not (IMAGE_GEN / "photocraft_sam_select.py").is_file():
        raise EditError("the SAM bridge (photocraft_sam_select.py) is missing")
    if str(IMAGE_GEN) not in sys.path:
        sys.path.insert(0, str(IMAGE_GEN))
    mod = importlib.import_module("photocraft_sam_select")
    if (settings or {}).get("comfy_url"):
        mod.COMFY = settings["comfy_url"]
    mask, _secs = mod.sam3_mask(Path(png), word, float((settings or {}).get("edit_sam_threshold", 0.4)))
    return mask


def _plan_fill(s, op, text, point, reply, settings, sam=None):
    """Find the object (SAM by name, or Tony's click), plan the wide crop, show the cost. Nothing is paid here."""
    from PIL import Image
    import numpy as np
    target = (op.get("target") or guess_target(op.get("prompt")) or guess_target(text)).strip()
    _base, src = base_png(s, settings)
    with Image.open(src) as im:
        rgb = np.asarray(im.convert("RGB"))
    H, W = rgb.shape[:2]
    box, how = None, ""
    if target:
        try:
            mask = (sam or (lambda p, w: sam_mask(p, w, settings)))(src, target)
            mask = np.asarray(mask, np.float32)
            if mask.shape != (H, W):
                mask = np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR),
                                  np.float32) / 255.0
            box = wf.box_from_mask(mask, point)
            how = f"found the {target}" if box else ""
        except Exception as e:  # noqa: BLE001  (SAM / ComfyUI down: Tony can still click the thing)
            how = f"SAM could not run ({str(e)[:80]})"
            box = None
    if box is None and point:
        box, how = wf.point_box(point, W, H), "using the spot you marked"
    if box is None:
        s["log"].append({"who": "studio", "text": (f"I could not find {('the ' + target) if target else 'what to change'}"
                         f"{' (' + how + ')' if how.startswith('SAM') else ''}. Click on it in the picture and send the "
                         "line again.")})
        return
    p = wf.plan(rgb, box)
    s["pending"] = {"prompt": wf.instruction(text, p), "text": text, "target": target, "credits": IMAGE_EDIT_CREDITS,
                    "box": p["box"], "plan": p, "src": str(src)}
    s["log"].append({"who": "studio", "text": f"{reply + ' ' if reply else ''}I {how} (dashed box). That is a "
                     f"generative fill with Nano Banana 2.1 on a wide crop around it: about {IMAGE_EDIT_CREDITS} "
                     "credits (~$0.03). Press Confirm to spend them, or say something else."})


def confirm_image_edit(rel, settings=None, prefix="/ikigai", editor=None):
    """Tony confirmed the paid fill: the wide crop goes to kie.ai Nano Banana 2.1 (6 credits), the answer is
    composited back through the wide soft mask (pixels outside it stay the original), and the result goes in as a
    new layer right above the old BASE, which is retired (hidden + renamed OLD). `editor(crop_png, out_png,
    prompt, ratio)` is for tests."""
    s = _sessions.get(rel)
    if not s or not s.get("pending"):
        raise EditError("nothing waiting for confirmation")
    if s.get("busy"):
        raise EditError("still working on the last edit")
    from PIL import Image
    import numpy as np
    pend = s.pop("pending")
    s["busy"] = True
    try:
        base = base_layer(s["layers"])
        if base is None:
            raise EditError("no BASE layer")
        c = Path(s["versions"][-1]["psd"]).parent
        n = len(s["versions"])
        p = pend["plan"]
        with Image.open(pend["src"]) as im:
            rgb = np.asarray(im.convert("RGB"))
        crop = c / f"Edit_{s['key']}_fill_v{n}_crop.png"
        wf.crop_for_model(rgb, p).save(crop)
        answer = c / f"Edit_{s['key']}_fill_v{n}_answer.png"
        if editor is None:
            from .scene_templates import kie_module
            mod = kie_module(settings)
            eng = (settings or {}).get("edit_fill_engine", wf.ENGINE)
            editor = lambda a, b, pr, ratio: mod.generate(eng, str(b), pr, aspect_ratio=ratio, res="2K", ref_imgs=[str(a)])
        info = editor(crop, answer, pend["prompt"], p["ratio"]) or {}
        with Image.open(answer) as im:
            out, alpha = wf.composite(rgb, im.convert("RGB"), p, s["versions"][-1].get("quad"))
        full = c / f"Edit_{s['key']}_base_edit_v{n}.png"
        Image.fromarray(out).save(full)
        stamp = datetime.now().strftime("%Y%m%d_%H%M")
        extra = _cmd("layer.select", {"layer": base["id"]})
        extra += _cmd("file.placeEmbedded", {"path": str(full), "smartObject": False, "scale": 100})
        extra += _cmd("layer.setProps", {"name": f"BASE (edited {stamp})", "visible": True})
        extra += _cmd("layer.setProps", {"layer": base["id"], "visible": False,
                                         "name": f"OLD {base['name']} (retire)"})
        _apply(s, [], settings, extra)
        spent = info.get("credits") if isinstance(info, dict) else None
        s["log"].append({"who": "studio", "text": f"Done ({spent if spent is not None else pend['credits']} credits): "
                         "new BASE layer with the change; the old one is hidden and renamed OLD for you to delete. "
                         "Everything outside the edited area is the original photo."})
    except Exception as e:  # noqa: BLE001  (kept waiting: Tony can press Confirm again or say something else)
        s["pending"] = pend
        s["log"].append({"who": "studio", "text": f"The fill did not work: {str(e)[:200]}"})
    finally:
        s["busy"] = False
    return state(rel, settings, prefix)


def undo(rel, settings=None, prefix="/ikigai"):
    s = _sessions.get(rel)
    if s and len(s["versions"]) > 1:
        s["versions"].pop()                     # the working file stays in the cache (nothing deleted)
        s["layers"], s["canvas"] = layers_of(s["versions"][-1]["psd"], settings)
        s["log"].append({"who": "studio", "text": "Undone."})
    return state(rel, settings, prefix)


def save(rel, settings=None, prefix="/ikigai", recheck=True):
    """The old PSD -> <template folder>/Archive/<name>_before_edit_<stamp>.psd; the edited copy takes its place;
    the checker runs again. Nothing is deleted."""
    s = _sessions.get(rel)
    if not s or len(s["versions"]) < 2:
        raise EditError("nothing to save")
    psd = Path(s["psd"])
    st = psd.stat()
    if [st.st_size, st.st_mtime_ns] != s["orig"]:
        raise EditError("the template changed on disk since the editor opened (PhotoCraft?); Discard and reopen")
    arch = psd.parent / "Archive"
    arch.mkdir(exist_ok=True)                   # Archive folders are pre-approved (Tony 2026-11-08)
    dest = arch / f"{psd.stem}_before_edit_{datetime.now():%Y%m%d_%H%M%S}.psd"
    shutil.move(str(psd), str(dest))
    shutil.copy2(s["versions"][-1]["psd"], psd)
    with _lock:
        _sessions.pop(rel, None)
    if recheck:
        tc.start(settings, [rel])
    return {"rel": rel, "open": False, "saved": True, "archived": dest.name}


def discard(rel, settings=None, prefix="/ikigai"):
    with _lock:
        _sessions.pop(rel, None)
    return {"rel": rel, "open": False, "discarded": True}


# ---------- Open in PhotoCraft ----------

def _port_open(port):
    with socket.socket() as so:
        so.settimeout(0.3)
        return so.connect_ex(("127.0.0.1", port)) == 0


def _bridge(port, token_file, calls, settings=None, timeout=20):
    """JSON-RPC over `photocraft-cli mcp --bridge` (initialize + tools/call ...). Returns the responses."""
    msgs = [{"jsonrpc": "2.0", "id": 0, "method": "initialize",
             "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "portal", "version": "1"}}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"}]
    for i, (tool, args) in enumerate(calls, 1):
        msgs.append({"jsonrpc": "2.0", "id": i, "method": "tools/call", "params": {"name": tool, "arguments": args}})
    p = subprocess.run([tc._bin(settings), "mcp", "--bridge", f"127.0.0.1:{port}", "--control-token-file",
                        str(token_file)], input="\n".join(json.dumps(m) for m in msgs) + "\n", capture_output=True,
                       text=True, timeout=timeout)
    out = []
    for ln in p.stdout.splitlines():
        try:
            out.append(json.loads(ln))
        except ValueError:
            pass
    return out


def _openfill_bridge(port, token_file, calls, settings=None, timeout=60):
    """Commands to the OpenFill PhotoCraft through OpenFill's own control client (token file never read aloud).
    calls = [(command, params), ...]; ("await_document", {"name": stem}) waits until that document is open and
    makes it active. Returns one reply per call."""
    import sys
    app_dir = str(OPENFILL_PROFILE / "app")
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)
    from openfill_photocraft.control import ControlClient
    pc = ControlClient(port, Path(token_file))
    out = []
    for cmd, params in calls:
        if cmd == "await_document":
            doc = None
            for _ in range(int(timeout * 2)):
                try:
                    docs = (pc.call("ui.inspect").get("session") or {}).get("documents") or []
                    doc = next((d for d in docs if str(d.get("name", "")).startswith(params["name"])), None)
                except Exception:  # noqa: BLE001  (still starting)
                    doc = None
                if doc:
                    break
                time.sleep(0.5)
            if doc:
                pc.run("document.activate", document=doc["index"])
            out.append({"result": doc} if doc else {"error": "document not open"})
        else:
            try:
                out.append({"result": pc.run(cmd, **params)})
            except Exception as e:  # noqa: BLE001
                out.append({"error": str(e)[:200]})
    return out


def open_in_photocraft(rel, layer=None, settings=None, launcher=None, bridge=None):
    """Open the template in PhotoCraft for hand work and select `layer` (if named). Default: "PhotoCraft with
    OpenFill" (Generative Fill in Filter > Plug-ins); photocraft_open_with = "artcraft": the old ArtCraft build."""
    t = next((x for x in tg.scan(settings)[0] if x["rel"] == rel), None)
    if t is None:
        raise EditError("no such template")
    psd = t["psd"]
    sett = settings or {}
    if sett.get("photocraft_open_with", "openfill") == "openfill":
        exe = Path(sett.get("openfill_launcher", OPENFILL_LAUNCHER))
        if not exe.exists() and launcher is None:
            raise EditError("PhotoCraft with OpenFill is not installed (" + str(exe) + ")")
        port = int(sett.get("openfill_control_port", 7878))
        token = OPENFILL_PROFILE / "control.token"
        was_up = _port_open(port)
        # the launcher starts PhotoCraft + the OpenFill bar, or hands the file to the running one
        (launcher or (lambda a: subprocess.Popen(a, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                                 start_new_session=True)))([str(exe), str(psd)])
        for _ in range(120):
            if _port_open(port):
                break
            time.sleep(0.5)
        calls = [("await_document", {"name": Path(psd).stem})]
        if layer:
            calls.append(("layer.select", {"name": layer}))
        r = (bridge or _openfill_bridge)(port, token, calls, settings)
        sel = r[-1] if layer and r else None
        return {"rel": rel, "port": port, "app": "reused" if was_up else "launched", "with": "OpenFill",
                "layer": layer, "selected": bool(sel and "error" not in sel)}
    port = int(sett.get("photocraft_control_port", 47811))
    token = _cache(settings) / f"PhotoCraft_Control_Token_{port}"
    app = sett.get("photocraft_app", APP)
    if not _port_open(port):
        if not Path(app).exists() and launcher is None:
            raise EditError("PhotoCraft is not installed at " + app)
        (launcher or (lambda a: subprocess.Popen(a, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                                 start_new_session=True)))(
            [app, "--control", str(port), "--control-token-file", str(token), str(psd)])
        for _ in range(60):
            if _port_open(port) and token.is_file():
                break
            time.sleep(0.5)
        opened = "launched"
    else:
        opened = "reused"
        (bridge or _bridge)(port, token, [("command_run", {"command": "file.open", "params": {"path": str(psd)}})],
                            settings)
    sel = None
    if layer:
        r = (bridge or _bridge)(port, token, [("command_run", {"command": "layer.select", "params": {"name": layer}})],
                                settings)
        sel = r[-1] if r else None
    return {"rel": rel, "port": port, "app": opened, "with": "ArtCraft", "layer": layer,
            "selected": bool(sel and "error" not in sel)}
