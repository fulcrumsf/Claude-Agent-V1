"""Templates tab: "Edit with chat" and "Open in PhotoCraft" (Tony 2026-11-10, Ikigai_Portal_Build_Plan section 4).

Edit with chat (a large overlay: room left, chat right, before/after):
  - start: the template PSD is COPIED to a working file in the gallery cache (data/rooms/Edit_<key>_v<N>.psd); the
    template itself is untouched until Tony presses Save.
  - each chat line becomes a short list of LAYER edits, checked against an allow-list and run headless with
    photocraft-cli on the working copy (never `layer.delete`): show/hide, opacity, blend, rename, move, blur a layer,
    the art smart object's corners, retire a layer (hide + rename "OLD ... (retire)"), heal a small spot on the
    BASE layer (spot healing at the point Tony clicked). The translator is the Portal's headless Claude CLI (no
    tools) with the layer list; simple lines ("hide Glass Sheen", "Light Shadow opacity 12%") are parsed without it.
  - a real pixel change (remove a lamp, change the wall) is an image-edit model call: about 18 kie.ai credits, shown
    first and run only after Tony confirms; the edited picture becomes a new layer above BASE, the old BASE is
    retired (hidden + "OLD BASE ... (retire)").
  - Save: the old PSD moves into the template folder's Archive/ (pre-approved by Tony), the edited copy takes its
    name, and the template checker runs on it. Discard: nothing changes. The X asks Save / Discard when unsaved.
Open in PhotoCraft: launches the app with a control port + token file and selects the layer Tony names via
`photocraft-cli mcp --bridge` (verified 2026-11-10). It never saves the document.
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

APP = "/Applications/ArtCraft/PhotoCraft.app/Contents/MacOS/photocraft"
IMAGE_EDIT_CREDITS = 18
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
    """The working copy with a neutral test card in the art (same card as the gallery), as a JPG <= 1800 px wide."""
    import tempfile
    from PIL import Image
    work = Path(work or _cache(settings))
    args = ["run", str(psd)]
    if card_px:
        card = work / f"Edit_card_{card_px[0]}x{card_px[1]}.png"
        if not card.is_file():
            tg.test_card(card_px[0], card_px[1], card)
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
            "quad": v[-1].get("quad"), "layers": s["layers"], "canvas": s["canvas"], "pending": s.get("pending"), "busy": s.get("busy", False)}


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
                                   "art corners, or click the picture to mark a small spot to remove."}]}
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
 {"op":"image_edit","prompt":"<what to change in the room photo>"}   (real pixel changes only; costs credits)
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
            good.append({"op": "image_edit", "prompt": str(o.get("prompt", ""))[:600]})
        else:
            raise EditError(f"'{k}' is not an allowed edit (layers are never deleted)")
    return good


def commands(ops, layers):
    ids = {l["id"]: l for l in layers}
    art = next((l for l in layers if l["name"] == tc.ART), None)
    base = next((l for l in reversed(layers) if l["kind"] in ("Pixel", "Smart Object") and l is not art), None)
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


def chat(rel, text, point=None, settings=None, prefix="/ikigai", ask=None):
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
            s["pending"] = {"prompt": paid[0]["prompt"], "credits": IMAGE_EDIT_CREDITS}
            s["log"].append({"who": "studio", "text": f"{reply} That needs the image-edit model on the room photo: "
                             f"about {IMAGE_EDIT_CREDITS} credits. Press Confirm to spend them, or say something else."})
            ops = [o for o in ops if o["op"] != "image_edit"]
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


def confirm_image_edit(rel, settings=None, prefix="/ikigai", editor=None):
    """Tony confirmed the paid image edit: the BASE photo is edited by the image model (kie.ai, ~18 credits); the
    result goes in as a new layer right above the old BASE, which is retired (hidden + renamed OLD)."""
    s = _sessions.get(rel)
    if not s or not s.get("pending"):
        raise EditError("nothing waiting for confirmation")
    pend = s.pop("pending")
    c = Path(s["versions"][-1]["psd"]).parent
    art = next((l for l in s["layers"] if l["name"] == tc.ART), None)
    base = next((l for l in reversed(s["layers"]) if l["kind"] in ("Pixel", "Smart Object") and l is not art), None)
    if base is None:
        raise EditError("no BASE layer")
    src = c / f"Edit_{s['key']}_base.png"
    hide = [l["id"] for l in s["layers"] if l["id"] != base["id"] and l["kind"] != "Group"]
    _run(settings, ["run", str(s["versions"][-1]["psd"]), *tc._hide(hide), "--out", str(src)])
    out = c / f"Edit_{s['key']}_base_edit.png"
    if editor is None:
        from .scene_templates import kie_module
        mod = kie_module(settings)
        editor = lambda a, b, p: mod.edit((settings or {}).get("room_scene_engine", "nbpro"), str(a), str(b), p)
    editor(src, out, pend["prompt"])
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    extra = _cmd("layer.select", {"layer": base["id"]})
    extra += _cmd("file.placeEmbedded", {"path": str(out), "smartObject": False, "scale": 100})
    extra += _cmd("layer.setProps", {"name": f"BASE (edited {stamp})", "visible": True})
    extra += _cmd("layer.setProps", {"layer": base["id"], "visible": False,
                                     "name": f"OLD {base['name']} (retire)"})
    _apply(s, [], settings, extra)
    s["log"].append({"who": "studio", "text": f"Image edit done ({pend['credits']} credits): new BASE layer, the old "
                                              "one is hidden and renamed OLD for you to delete."})
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


def open_in_photocraft(rel, layer=None, settings=None, launcher=None, bridge=None):
    """Launch PhotoCraft on the template with a control port + token file, then select `layer` (if named)."""
    t = next((x for x in tg.scan(settings)[0] if x["rel"] == rel), None)
    if t is None:
        raise EditError("no such template")
    psd = t["psd"]
    port = int((settings or {}).get("photocraft_control_port", 47811))
    token = _cache(settings) / f"PhotoCraft_Control_Token_{port}"
    app = (settings or {}).get("photocraft_app", APP)
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
    return {"rel": rel, "port": port, "app": opened, "layer": layer, "selected": bool(sel and "error" not in sel)}
