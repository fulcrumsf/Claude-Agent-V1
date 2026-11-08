"""Room mockups (listing slots 8-19) from the PhotoCraft room templates under ../Room_Templates/.

Every folder (any depth, e.g. Portrait_Templates/01_Ratio_2x3/Living_Room/Teak_Sideboard/) that holds a room.json manifest
is a wired room; one PSD per light (the image model relit the same room plate; built by <room>/Scripts/build_template_v2.py).
PSD/json paths in room.json are relative to the room folder; layer-export caches go to its `cache_dir` (default: the folder).
A look = room + light + frame + mat + wall paint + glass, rendered headless with photocraft-cli by switching layers and swapping the art into the "Place Artwork Here" smart object.
The art's own pixels are never redrawn by AI (Etsy accuracy, Mockup_Style_Guide.md 1e).

Choices are made by rules, never at random (Tony 2026-11-07):
  - frames: app/frames.py (scored on the print's style tags, value key, accents; only frames the room PSD has)
  - wall paint: app/walls.py (art-director scoring vs the art and the room's furniture tone)
  - light: the room's lights ranked by how well they suit the print's mood row (rooms.pick_profile) then rank
Any paint is possible: the PSD's reference paint layer ("Wall Greige") is exported once and recoloured as a
reflectance swap in linear light (same light, texture and shadows; only the paint's albedo changes).
Accuracy guard after every render (style guide 4c.8): art hue shift <= 8 deg and shadow cover <= the light's limit;
a failing render is reported and not placed in the listing folder.
"""
import json
import subprocess
import tempfile
from pathlib import Path

import numpy as np

from .db import ROOT

DEFAULTS = {"room_templates_dir": "../Room_Templates", "room_looks_max": 4, "room_first_slot": 8,
            "room_guard_max_hue": 8.0, "room_guard_max_cover": 0.35, "photocraft_bin": "photocraft-cli",
            "room_render_timeout_s": 300}
ART_LAYER, ART_LAYER_MAT, BASE_LAYER = "Place Artwork Here", "Place Artwork Here (Mat)", \
    "BASE (scene plate with its light, panel = lit white)"
FRAME_LAYERS = ("Oak", "Walnut", "Black", "White")
W709 = np.array([0.2126, 0.7152, 0.0722], "float32")


def _cfg(settings, key):
    return (settings or {}).get(key, DEFAULTS[key])


def _abs(p):
    p = Path(p)
    return p if p.is_absolute() else (ROOT / p).resolve()


def lin(x):
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def enc(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * x ** (1 / 2.4) - 0.055)


# ---------- templates ----------

def rooms(settings=None):
    """Every folder below room_templates_dir (any depth) with a room.json, lights resolved to existing PSD + json files."""
    root = _abs(_cfg(settings, "room_templates_dir"))
    out = []
    for man in sorted(root.rglob("room.json")) if root.is_dir() else []:
        d = man.parent
        room = json.loads(man.read_text())
        room["dir"] = d
        room["lights"] = [dict(l, meta=json.loads((d / l["json"]).read_text()))
                          for l in room.get("lights", []) if (d / l["psd"]).is_file() and (d / l["json"]).is_file()]
        if room["lights"]:
            out.append(room)
    return out


def rank_lights(room, profile_key):
    """Lights that suit the print's mood row first, then the room's own rank. Deterministic."""
    return sorted(room["lights"], key=lambda l: (profile_key not in l.get("suits", []), l.get("rank", 9), l["id"]))


def room_frames(room, frame_set):
    """frames.py set -> only frames this room's PSD has, keeping the chooser's order and mat flags."""
    have = room.get("frames", {})
    return [dict(f, layer=have[f["id"]]) for f in frame_set if f["id"] in have]


# ---------- cached layer exports (one-time per light, git-ignored PNGs next to the PSD) ----------

def _run(settings, args, timeout=None):
    r = subprocess.run([_cfg(settings, "photocraft_bin"), *args], capture_output=True, text=True,
                       timeout=timeout or int(_cfg(settings, "room_render_timeout_s")))
    if r.returncode != 0:
        raise RuntimeError(f"PhotoCraft failed: {(r.stderr or r.stdout).strip()[-300:]}")
    return r.stdout


def _cmd(c, p=None):
    return ["--cmd", c, "--params", json.dumps(p or {})]


def _vis(layer, on):
    return _cmd("layer.setProps", {"layer": layer, "visible": bool(on)})


ALL_TOP = (BASE_LAYER, "WALL COLOUR", ART_LAYER, ART_LAYER_MAT, "MAT", "FRAME", "SHADOWS", "GLASS")


def export_layer(room, light, layer, settings=None, groups=()):
    """One layer alone as an RGBA PNG (everything else hidden), cached as Cache_<psd stem>_<layer>.png."""
    safe = "".join(ch if ch.isalnum() else "_" for ch in layer).strip("_")
    psd = room["dir"] / light["psd"]
    stamp = f"{psd.stat().st_size:x}"                 # keyed by PSD name + size: a rebuilt PSD never reuses a stale cache
    out = room["dir"] / room.get("cache_dir", "") / f"Cache_{psd.stem}_{stamp}_{safe}.png"
    if out.is_file():
        return out
    args = []
    for top in ALL_TOP:
        if top == "SHADOWS" and not light.get("soft_layer"):
            continue
        args += _vis(top, top in groups or top == layer)
    if layer not in ALL_TOP:
        if "FRAME" in groups:                          # the frame group also holds the other frames + lip shadow
            args += _vis("Frame lip shadow", False) + [x for f in FRAME_LAYERS for x in _vis(f"Frame {f}", False)]
            if light.get("contact_layer"):                 # v3 PSDs (2026-11-08) also hold a contact-shadow layer
                args += _vis("Frame contact shadow", False)
        args += _vis(layer, True)
    _run(settings, ["run", str(psd), *args, "--out", str(out)])
    return out


def _load(p):
    from PIL import Image
    with Image.open(p) as im:
        return np.array(im.convert("RGBA")).astype("float32") / 255


def _save_rgba(a, path):
    from PIL import Image
    Image.fromarray((np.clip(a, 0, 1) * 255).round().astype("uint8"), "RGBA").save(path)


def paint_layer(ref_rgba, ref_rgb, new_rgb, out_path):
    """Reflectance swap: new = ref x (new paint / reference paint) per channel in linear light, so the plate's light
    (sun, shade, its colour) and the plaster texture stay. Highlight shoulder (weak spot 3, 2026-11-07): on the bright
    plates a mid paint came out near-white because the sun lifted it to clipping; above 0.5 linear luma the result
    is compressed (soft shoulder, never above ~237/255) so a lit wall keeps its colour instead of burning out."""
    ref = lin(ref_rgba[..., :3])
    k = lin(np.array(new_rgb, "float32") / 255) / np.maximum(lin(np.array(ref_rgb, "float32") / 255), 1e-4)
    px = ref * k[None, None, :]
    y = px @ W709
    knee, cap = 0.5, 0.85                       # linear luma; cap 0.85 = about 237/255 on screen
    y2 = np.where(y > knee, knee + (cap - knee) * np.tanh((y - knee) / (cap - knee)), y)
    px = px * (y2 / np.maximum(y, 1e-5))[..., None]
    # cool-cast limit: in the golden-hour plate's shade the light reads blue, which turned warm paints (putty, clay)
    # grey-mauve. Where a pixel is cooler than the paint chip itself, pull its colour 70 % back to the chip's.
    c0 = lin(np.array(new_rgb, "float32") / 255)
    c0 = c0 / max(float(c0 @ W709), 1e-5)
    yy = np.maximum(px @ W709, 1e-5)
    c = px / yy[..., None]
    cool = np.clip(((c[..., 2] - c0[2]) - (c[..., 0] - c0[0])) / 0.25, 0, 1)[..., None] * 0.7
    px = (c * (1 - cool) + c0[None, None, :] * cool) * yy[..., None]
    out = np.dstack([enc(px), ref_rgba[..., 3]])
    _save_rgba(out, out_path)
    return out_path


def white_frame_layer(ref_rgba, out_path):
    """Weak spot 2 (2026-11-07): the white frame read taupe in shade (warm light x grey = beige-brown). A painted
    white frame in shade reads as a light neutral grey: keep 35 % of the light's colour, lift shade (gamma 0.8)."""
    rgb = lin(ref_rgba[..., :3])
    y = np.maximum(rgb @ W709, 1e-5)
    chroma = rgb / y[..., None]
    chroma = 1 + 0.35 * (chroma - 1)
    y2 = np.clip(y, 0, 1) ** 0.8
    _save_rgba(np.dstack([enc(chroma * y2[..., None]), ref_rgba[..., 3]]), out_path)
    return out_path


# ---------- render one look ----------

def look_args(room, light, look, paint_png=None, white_png=None):
    """photocraft-cli command list for one look (art already swapped in)."""
    a = []
    for f in FRAME_LAYERS:
        a += _vis(f"Frame {f}", look["frame_layer"] == f and not (f == "White" and white_png))
    a += _vis("MAT", look["mat"]) + _vis(ART_LAYER_MAT, look["mat"]) + _vis(ART_LAYER, not look["mat"])
    for p in light["meta"].get("paints", []):
        a += _vis(f"Wall {p}", False)
    if paint_png:
        a += _cmd("layer.select", {"name": f"Wall {light['meta']['paints'][0]}"})
        a += _cmd("file.placeEmbedded", {"path": str(paint_png), "smartObject": False, "scale": 100})
        a += _cmd("layer.setProps", {"name": f"Wall {look['paint']['name']} (chosen)", "blend": "Normal", "visible": True})
        a += _cmd("layer.moveTo", {"layer": f"Wall {look['paint']['name']} (chosen)", "target": "WALL COLOUR",
                                   "position": "into"})
    if white_png:
        a += _cmd("layer.select", {"name": "Frame Oak"})
        a += _cmd("file.placeEmbedded", {"path": str(white_png), "smartObject": False, "scale": 100})
        a += _cmd("layer.setProps", {"name": "Frame White (neutral)", "blend": "Normal", "visible": True})
        a += _cmd("layer.moveTo", {"layer": "Frame White (neutral)", "target": "FRAME", "position": "into"})
    if light.get("soft_layer"):
        a += _vis("Soft cast shadow", True)          # shadow on every image (Tony decision 2)
    a += _vis("GLASS", look.get("glass", True))
    return a


def render_look(room, light, art, look, out_png, settings=None, work=None):
    """Render one look to out_png (PNG). Returns {"png", "fitted"}."""
    from .mockups import fit_art
    work = Path(work or tempfile.mkdtemp())
    meta = light["meta"]
    fitted = work / f"art_{light['id']}.png"
    fit_art(art, tuple(meta["smart_object_px"]), fitted)
    paint_png = white_png = None
    if look.get("paint"):
        ref = room.get("reference_paint", {"layer": "Wall Greige", "rgb": [200, 192, 176]})
        src = _load(export_layer(room, light, ref["layer"], settings, groups=("WALL COLOUR",)))
        paint_png = paint_layer(src, ref["rgb"], look["paint"]["rgb"], work / f"paint_{light['id']}.png")
    if look["frame_layer"] == "White":
        src = _load(export_layer(room, light, "Frame White", settings, groups=("FRAME",)))
        white_png = white_frame_layer(src, work / f"white_{light['id']}.png")
    args = (_cmd("layer.select", {"name": ART_LAYER})
            + _cmd("layer.smartObjects.replaceContents", {"path": str(fitted.resolve())})
            + _cmd("layer.select", {"name": ART_LAYER_MAT})
            + _cmd("layer.smartObjects.replaceContents", {"path": str(fitted.resolve())})
            + look_args(room, light, look, paint_png, white_png))
    _run(settings, ["run", str(room["dir"] / light["psd"]), *args, "--out", str(out_png)])
    if not Path(out_png).is_file():
        raise RuntimeError(f"{Path(out_png).name} was not written")
    return {"png": Path(out_png), "fitted": fitted}


# ---------- accuracy guard (style guide 4c.8) ----------

def guard(room, light, render_png, fitted_png, mat, settings=None, max_cover=None):
    """Unwarp the art from the render, compare hue of coloured pixels with the fitted source, and measure how much
    of the art lies in shadow (lit-white panel luma < 0.75 x its p95, from the PSD's BASE layer)."""
    import cv2
    from PIL import Image
    meta = light["meta"]
    q = np.array(meta["quad_mat" if mat else "quad_nomat"], "float32")
    src = np.array(Image.open(fitted_png).convert("RGB"))
    h, w = src.shape[:2]
    Hm = cv2.getPerspectiveTransform(q, np.array([[0, 0], [w, 0], [w, h], [0, h]], "float32"))
    ren = cv2.warpPerspective(np.array(Image.open(render_png).convert("RGB")), Hm, (w, h))
    base_png = export_layer(room, light, BASE_LAYER, settings)
    base = cv2.warpPerspective(np.array(Image.open(base_png).convert("RGB")), Hm, (w, h)).astype("float32")
    m = np.zeros((h, w), bool)
    mg = int(0.03 * h)
    m[mg:-mg, mg:-mg] = True                        # skip the frame-lip shadow margin
    hs = cv2.cvtColor(src, cv2.COLOR_RGB2HSV_FULL).astype("float32")
    hr = cv2.cvtColor(ren, cv2.COLOR_RGB2HSV_FULL).astype("float32")
    col = m & (hs[..., 1] > 90) & (hs[..., 2] > 60)
    d = (hr[..., 0] - hs[..., 0]) * 360 / 256
    d = (d + 180) % 360 - 180
    hue = float(np.degrees(np.angle(np.mean(np.exp(1j * np.radians(d[col])))))) if col.any() else 0.0
    lum = base @ np.array([0.299, 0.587, 0.114], "float32")
    cover = float(((lum < 0.75 * np.percentile(lum[m], 95)) & m).sum() / m.sum())
    lim_c = float(max_cover if max_cover is not None else light.get("max_cover", _cfg(settings, "room_guard_max_cover")))
    lim_h = float(_cfg(settings, "room_guard_max_hue"))
    why = []
    if abs(hue) > lim_h:
        why.append(f"art hue moved {hue:+.1f} deg (limit {lim_h:g})")
    if cover > lim_c:
        why.append(f"shadow covers {cover:.0%} of the art (limit {lim_c:.0%})")
    return {"hue_shift_deg": round(hue, 1), "shadow_cover": round(cover, 2), "cover_limit": lim_c,
            "pass": not why, "why": why}


# ---------- choose the looks for one print ----------

def pick_art(arts, aspect):
    """The print file whose shape is closest to the template's art window (least cropping)."""
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None

    def ratio(p):
        with Image.open(p) as im:
            return im.size[0] / im.size[1]
    return min(arts, key=lambda p: abs(ratio(p) - aspect))


def plan(arts, design, settings=None, n=None):
    """Looks for one print, best first: [{room, light, frame, mat, paint, art, reasons}]. Deterministic.
    design = {"title", "description", "cards"}. One look per light of the best room (more rooms: round-robin)."""
    from . import frames, rooms as rooms_v2, walls
    n = int(n or _cfg(settings, "room_looks_max"))
    title = (design or {}).get("title") or ""
    desc = (design or {}).get("description") or ""
    all_rooms = rooms(settings)
    if not all_rooms:
        return []
    first = pick_art(arts, all_rooms[0]["lights"][0]["meta"]["art_aspect"])
    analysis = rooms_v2.analyze_print(first)
    profile = rooms_v2.pick_profile(f"{title} {desc}", analysis["value_key"])["key"]
    fr = frames.frames_for_print(title, desc, analysis, (design or {}).get("cards"), settings)
    ranked_rooms = sorted(all_rooms, key=lambda r: (analysis["value_key"] not in r.get("value_keys", []), r["dir"].name))
    looks = []
    for room in ranked_rooms:
        fset = room_frames(room, fr["frames"]) or [{"id": "oak", "layer": "Oak", "mat": False, "reasons": ["fallback"]}]
        paints = walls.choose(analysis, room.get("furniture", "warm_wood"), n=3)
        for i, light in enumerate(rank_lights(room, profile)):
            # frames and paints cycle at different steps so no two looks share both (3 frames x 3 paints)
            f, p = fset[i % len(fset)], paints[(i + i // len(fset)) % len(paints)]
            art = pick_art(arts, light["meta"]["art_aspect"])
            looks.append({"room": room, "light": light, "frame_id": f["id"], "frame_layer": f["layer"],
                          "mat": bool(f.get("mat")), "paint": {"name": p["name"], "rgb": p["rgb"]}, "glass": True,
                          "art": art, "profile": profile, "analysis": analysis,
                          "reasons": {"frame": f.get("reasons", []), "paint": p["reasons"],
                                      "light": f"{light['kind']}; suits {profile}" if profile in light.get("suits", [])
                                      else f"{light['kind']}; room rank {light.get('rank')}"}})
    # interleave rooms so a listing does not repeat one room back to back
    by_room = {}
    for lk in looks:
        by_room.setdefault(lk["room"]["dir"].name, []).append(lk)
    order, k = [], 0
    while len(order) < len(looks):
        for lst in by_room.values():
            if k < len(lst):
                order.append(lst[k])
        k += 1
    return order[:n]


def file_name(slot, look):
    return f"{slot:02d}_Room_{look['room']['name'].replace(' ', '_')}_{look['light']['label']}.jpg"


def build_rooms(out_dir, arts, settings, design):
    """Render the planned looks into out_dir as JPG (slots 8..). Returns (made, notes, failed_slots)."""
    from .mockups import _place
    made, notes, failed = [], [], []
    looks = plan(arts, design, settings)
    if not looks:
        return made, ["room mockups: no room templates found"], failed
    slot0 = int(_cfg(settings, "room_first_slot"))
    with tempfile.TemporaryDirectory() as td:
        for i, lk in enumerate(looks):
            slot = slot0 + i
            png = Path(td) / f"room_{slot}.png"
            try:
                r = render_look(lk["room"], lk["light"], lk["art"], lk, png, settings, td)
                g = guard(lk["room"], lk["light"], png, r["fitted"], lk["mat"], settings)
            except Exception as e:                      # one bad look must not stop the others
                failed.append(slot)
                notes.append(f"room slot {slot} not built: {e}")
                continue
            if not g["pass"]:
                failed.append(slot)
                notes.append(f"room slot {slot} ({lk['light']['label']}) flagged for Tony, not used: "
                             + "; ".join(g["why"]))
                continue
            out = _place(png, out_dir / file_name(slot, lk))
            made.append({"file": out.name, "slot": slot, "room": lk["room"]["name"], "light": lk["light"]["id"],
                         "frame": lk["frame_id"], "mat": lk["mat"], "paint": lk["paint"]["name"],
                         "print": lk["art"].name, "guard": g, "reasons": lk["reasons"],
                         "mb": round(out.stat().st_size / 1e6, 1)})
    return made, notes, failed
