"""Reference photographs for the slot-set planner (realism addendum section 1, 2026-11-20).

Tony's reference board (Creative_Inspiration/Mock-Up_Inspiration/, setting reference_dir) holds cleaned screenshots of
real framed art in rooms. Each one is prepared ONCE, headless and free:
  1. find the artwork with the existing SAM pipeline in reference mode (sam_frames.py detect --reference, run in the
     SAM venv; one Gemini flash-lite box call), canvas retry, plain-mask fallback;
  2. fill the artwork flat with the insert MARKER colour picked opposite the reference's own wall
     (slot_planner.marker_for_wall), one pixel under the frame lip, so captions, watermarks and poster lettering on the
     art are gone;
  3. measure (art height share, true aspect, camera side, light side, wall colour) and run the free checks (leftover
     ring, portrait only, one frame and no mirror / screen, upright, no room text);
  4. write NNNN_<Same_Name>_Blank.png NEXT TO its source and one Reference_Manifest.json for the folder.
Repeated runs are free and byte-stable (sha1 + prep_version); an entry Tony blanked by hand (blank_method "tony") and
tags he edited (tags_by "tony") are never touched. The planner picks ONE distinct reference per slot; the image model
gets the blank (recoloured / mirrored on demand into the run's temp dir) for camera, lens, framing and character only.

  python -m app.references --prepare [--ids 0024,0031] [--force] [--sheet out.png]
"""
import hashlib
import json
import re
import shutil
import subprocess
import threading
from datetime import datetime
from pathlib import Path

import numpy as np

PREP_VERSION = 1
MANIFEST = "Reference_Manifest.json"
SOURCE_RE = re.compile(r"^(\d{4})_[A-Za-z0-9_\-]+\.png$")
DEFAULTS = {"reference_dir": "../Creative_Inspiration/Mock-Up_Inspiration", "planner_references": True}
RING_DE = 25.0            # leftover check: a band pixel this far from the band's median colour is an art sliver
RING_MAX = 0.08          # worst side, mean over rows (calibrated on the 26: slivers / objects across a frame >= 0.088)
PORTRAIT_MAX = 0.90       # true width / height; square, landscape and round art is not a display we build
DISPLAY_GROUPS = ("hung", "surface", "shelf", "floor")
LIVED_IN = ("tidy", "lived_in", "busy")
_LOCK = threading.Lock()

# 1.6: seed tags from viewing all 26 (2026-11-20). Measured fields (camera side, light side, aspect, art share) win
# over these; camera_height / lens / window_covering added from the same viewing. seed_why = never usable as is.
_T = dict


def _seed(display, shot, setting, room, height, lens, light, lived, window, editorial=False, pres="frame", why=None):
    return _T(display_group=display, shot=shot, setting=setting, room=room, camera_height=height, lens=lens,
              light_type=light, lived_in=lived, window_covering=window, editorial=editorial, presentation=pres,
              **({"seed_why": why} if why else {}))


SEED_TAGS = {
    "0001": _seed("hung", "medium", "credenza, living", "Living room", "counter", "lens_normal", "golden_low", "tidy",
                  "bare", True),
    "0023": _seed("hung", "medium", "dining banquette", "Kitchen & dining", "eye", "lens_normal", "hard_diagonal_sun",
                  "lived_in", "no_window_in_view"),
    "0024": _seed("hung", "medium", "kitchen counter", "Kitchen & dining", "eye", "lens_normal", "dusk_lamp_mix",
                  "busy", "bare"),
    "0025": _seed("floor", "medium", "beside bed", "Bedroom", "low", "lens_normal", "morning_soft_sun", "lived_in",
                  "bare"),
    "0026": _seed("floor", "medium", "bare wall", "Living room", "low", "lens_normal", "hard_diagonal_sun", "tidy",
                  "no_window_in_view"),
    "0027": _seed("hung", "medium", "bathroom tile, over toilet", "Bathroom", "eye", "lens_normal", "north_light_even",
                  "lived_in", "no_window_in_view"),
    "0028": _seed("flat", "medium", "rug", "Living room", "eye", "lens_normal", None, None, "no_window_in_view",
                  why="frame lying flat (flat lay)"),
    "0029": _seed("hung", "tight", "plain wall", "Living room", "eye", "lens_normal", "overcast_flat", "tidy",
                  "no_window_in_view"),
    "0030": _seed("surface", "medium", "coffee bar dresser", "Kitchen & dining", "counter", "lens_normal",
                  "north_light_even", "busy", "no_window_in_view"),
    "0031": _seed("shelf", "tight", "oak niche", "Living room", "counter", "lens_normal", "blind_stripes", "tidy",
                  "no_window_in_view"),
    "0032": _seed("floor", "medium", "beside French door", "Living room", "low", "lens_normal", "morning_soft_sun",
                  "tidy", "bare"),
    "0033": _seed("shelf", "tight", "ledge", "Living room", "counter", "lens_normal", "north_light_even", "tidy",
                  "no_window_in_view", why="square frame, readable book spine"),
    "0034": _seed("hung", "medium", "sideboard", "Living room", "counter", "lens_normal", "north_light_even", "tidy",
                  "no_window_in_view", True),
    "0035": _seed("hung", "medium", "sideboard, mat", "Living room", "counter", "lens_normal", "north_light_even",
                  "tidy", "no_window_in_view", True, "mat"),
    "0036": _seed("hung", "wide", "hallway, oversized canvas", "Living room", "eye", "lens_normal", "overcast_flat",
                  "tidy", "no_window_in_view", True, "canvas_bare"),
    "0037": _seed("hung", "medium", "lounge chair", "Living room", "eye", "lens_normal", "north_light_even", "tidy",
                  "no_window_in_view", True),
    "0038": _seed("hung", "medium", "desk nook", "Office", "eye", "lens_normal", "north_light_even", "tidy", "bare",
                  pres="mat"),
    "0039": _seed("hung", "wide", "panelled living, curtains", "Living room", "seated", "lens_normal", "overcast_flat",
                  "lived_in", "linen_curtains", True),
    "0040": _seed("hung", "medium", "bathroom vanity", "Bathroom", "eye", "lens_normal", None, None,
                  "no_window_in_view", why="arched mirror beside the art"),
    "0041": _seed("hung", "wide", "industrial loft", "Living room", "eye", "lens_normal", "overcast_flat", "tidy",
                  "bare", True),
    "0042": _seed("hung", "medium", "charcoal studio desk", "Office", "eye", "lens_normal", "north_light_even",
                  "lived_in", "bare", pres="mat"),
    "0043": _seed("hung", "wide", "Parisian hallway, doorway", "Living room", "eye", "lens_normal", "north_light_even",
                  "tidy", "no_window_in_view", True, why="second frame on the left wall"),
    "0044": _seed("hung", "wide", "double-height living", "Living room", "low", "lens_normal", "overcast_flat", "tidy",
                  "linen_curtains", True),
    "0045": _seed("hung", "medium", "panelled office", "Office", "eye", "lens_normal", "north_light_even", "tidy",
                  "bare", True),
    "0046": _seed("hung", "wide", "dark salon, mantel", "Living room", "eye", "lens_wide", "dusk_lamp_mix", "tidy",
                  "heavy_drapes", True),
    "0047": _seed("hung", "wide", "taupe living, mantel", "Living room", "seated", "lens_normal", "overcast_flat",
                  "tidy", "no_window_in_view", True),
}
SEED_BY = "seed_2026-11-20"


def _cfg(settings, key):
    return (settings or {}).get(key, DEFAULTS[key])


def ref_dir(settings=None):
    from .scene_templates import _abs
    return _abs(_cfg(settings, "reference_dir"))


def sources(folder):
    """The reference sources of a folder (never Archive/, never the _Blank files), sorted."""
    folder = Path(folder)
    if not folder.is_dir():
        return []
    return sorted(p for p in folder.iterdir()
                  if p.is_file() and SOURCE_RE.match(p.name) and not p.stem.endswith("_Blank"))


def blank_name(src_name):
    return Path(src_name).stem + "_Blank.png"


def load(folder):
    p = Path(folder) / MANIFEST
    if p.is_file():
        try:
            m = json.loads(p.read_text())
            m.setdefault("refs", {})
            return m
        except ValueError:
            pass
    return {"version": 1, "prep_version": PREP_VERSION, "refs": {}}


def save(folder, man):
    p = Path(folder) / MANIFEST
    txt = json.dumps(man, indent=1, ensure_ascii=False) + "\n"
    if not p.is_file() or p.read_text() != txt:
        p.write_text(txt)


def update(settings, fn):
    """Read-modify-write the manifest under a lock (uses, grades, kie_refused)."""
    folder = ref_dir(settings)
    with _LOCK:
        man = load(folder)
        fn(man)
        save(folder, man)
        return man


# ---------- SAM in reference mode (subprocess into the SAM venv) ----------

def sam_reference(png, work, settings=None, canvas=False, box=None):
    """sam_frames.py detect --reference in the SAM venv. Returns the result dict; raises RuntimeError with the reason."""
    import os
    from . import sam_frames as sf
    from .scene_templates import _cfg as scfg
    py = Path(os.path.expanduser(scfg(settings, "sam_python")))
    if not py.is_file():
        raise RuntimeError(f"SAM 2 is not installed ({py})")
    js = Path(work) / "ref_sam.json"
    if js.exists():
        js.unlink()
    args = [str(py), "-I", str(Path(sf.__file__).resolve()), "detect", str(png), "--reference", "--json", str(js)]
    if canvas:
        args.append("--canvas")
    if box is not None:
        args += ["--box", ",".join(f"{float(v):.1f}" for v in box)]
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=int(scfg(settings, "sam_timeout_s")))
    except subprocess.TimeoutExpired:
        raise RuntimeError("SAM 2 took too long")
    res = json.loads(js.read_text()) if js.is_file() else None
    if r.returncode or res is None or res.get("error"):
        raise RuntimeError((res or {}).get("error") or (r.stderr or r.stdout).strip()[-300:])
    return res


# ---------- geometry + colour ----------

def quad_of_polygon(poly):
    """A four-corner quad (tl, tr, br, bl) around a fill polygon (mask mode): its minimum-area rectangle."""
    import cv2
    from .sam_frames import order_quad
    box = cv2.boxPoints(cv2.minAreaRect(np.float32(poly)))
    return order_quad(np.float32(box))


def fill_mask(poly, W, H, quad=False):
    """Anti-aliased coverage 0..1 of the fill polygon (sub-pixel for a quad)."""
    from .sam_frames import poly_coverage
    if quad and len(poly) == 4:
        return poly_coverage(np.float32(poly), W, H)
    from PIL import Image, ImageDraw
    ss = 4
    im = Image.new("L", (W * ss, H * ss), 0)
    ImageDraw.Draw(im).polygon([(x * ss, y * ss) for x, y in poly], fill=255)
    return np.asarray(im.resize((W, H), Image.BOX)).astype("float32") / 255.0


def paint(rgb, poly, marker, quad=False):
    """rgb with the polygon filled flat with the marker colour (no texture, no shading). uint8 HxWx3."""
    from .slot_planner import MARKER_RGB
    H, W = rgb.shape[:2]
    a = fill_mask(poly, W, H, quad)[..., None]
    out = rgb.astype("float32") * (1 - a) + np.float32(MARKER_RGB[marker]) * a
    return np.clip(np.round(out), 0, 255).astype("uint8")


def _grow(poly, d, quad):
    """The fill polygon moved outward by d px (offset for a quad; dilation for a mask polygon)."""
    from .sam_frames import offset_quad
    if quad and len(poly) == 4:
        return offset_quad(np.float32(poly), d).tolist()
    return None


def _side_rows(lab, poly, offs=(0.75, 1.75, 2.75), n=160):
    """Per side (top, right, bottom, left) of a fill quad: Lab samples along rows `offs` px outside it."""
    from .sam_frames import _bilinear, offset_quad
    out = []
    for i in range(4):
        rows = []
        for d in offs:
            q = offset_quad(np.float32(poly), d)
            a, b = q[i], q[(i + 1) % 4]
            t = np.linspace(0.08, 0.92, n)
            xs, ys = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            rows.append(np.stack([_bilinear(lab[..., c], xs, ys) for c in range(3)], -1))
        out.append(rows)
    return out


def leftover_ring(rgb, poly, quad=False, width=3.0):
    """Art sliver check (1.2 step 5), the share 0..1 of the worst side. A quad: per side, rows 0.75 / 1.75 / 2.75 px
    outside the fill; frame wood, a mat or a lip shadow run evenly ALONG a side, an art sliver does not, so a row's
    share of samples more than dE 25 from that row's median is the measure (mean over rows, worst side). A mask
    polygon: the share of a 3 px band outside it far from the band median."""
    import cv2
    H, W = rgb.shape[:2]
    lab = cv2.cvtColor(np.float32(rgb) / 255.0, cv2.COLOR_RGB2Lab)
    if quad and len(poly) == 4:
        worst = 0.0
        for rows in _side_rows(lab, poly):
            share = np.mean([float((np.linalg.norm(r - np.median(r, 0), axis=1) > RING_DE).mean()) for r in rows])
            worst = max(worst, float(share))
        return worst
    inner = fill_mask(poly, W, H, quad) > 0.5
    k = int(2 * width + 1)
    outer = cv2.dilate(inner.astype("uint8"), np.ones((k, k), "uint8")) > 0
    band = outer & ~inner
    if band.sum() < 20:
        return 0.0
    v = lab[band]
    return float((np.linalg.norm(v - np.median(v, 0), axis=1) > RING_DE).mean())


def frame_eaten(rgb, poly, wall_lab, quad=True):
    """Number of sides with NO frame or mat line outside the fill: every row from 1.5 px out to 40% of the art's size
    looks like the wall (median dE76 < 12). A white mat or print margin on a white wall still has its frame further
    out, so it is not counted; a fill that took the whole frame in finds only wall."""
    import cv2
    if not (quad and len(poly) == 4) or wall_lab is None:
        return 0
    q = np.float32(poly)
    size = min(float(np.linalg.norm(q[1] - q[0])), float(np.linalg.norm(q[3] - q[0])))
    offs = tuple(np.linspace(1.5, max(4.0, 0.4 * size), 32))
    lab = cv2.cvtColor(np.float32(rgb) / 255.0, cv2.COLOR_RGB2Lab)
    n = 0
    for rows in _side_rows(lab, poly, offs=offs):
        if all(float(np.linalg.norm(np.median(r, 0) - np.float32(wall_lab))) < 12 for r in rows):
            n += 1
    return n


def wall_rgb_hex(rgb, quad, ring=(0.12, 0.28)):
    """Median sRGB hex of the wall ring around the art (same ring as scene_templates.wall_lab). None when off-picture."""
    from .template_checker import offset_quad, poly_mask
    q = np.float32(quad)
    H, W = rgb.shape[:2]
    side = float(np.mean([np.linalg.norm(q[(i + 1) % 4] - q[i]) for i in range(4)]))
    m = (poly_mask(offset_quad(q, ring[1] * side), W, H) > 0.5) & ~(poly_mask(offset_quad(q, ring[0] * side), W, H) > 0.5)
    if m.sum() < 200:
        return None
    med = np.median(rgb[m].astype("float32"), 0)
    return "#" + "".join(f"{int(round(v)):02X}" for v in med)


def measure(rgb, quad):
    """Deterministic facts of the art quad: art_h_frac, aspect (true w/h), camera_side, light_from, wall_lab, marker."""
    from . import rooms, scene_templates as stp, slot_planner as sp
    q = np.float32(quad)
    H, W = rgb.shape[:2]
    left, right = float(np.linalg.norm(q[3] - q[0])), float(np.linalg.norm(q[2] - q[1]))
    side = "left" if left > 1.03 * right else "right" if right > 1.03 * left else "front"
    gray = rgb.astype("float32") @ np.float32([0.299, 0.587, 0.114])
    hx = wall_rgb_hex(rgb, q)
    return {"art_h_frac": round(((left + right) / 2) / H, 3), "aspect": round(float(rooms.true_aspect(q, (W, H))), 3),
            "camera_side": side, "light_from": stp.light_side(gray, q), "wall_lab": stp.wall_lab(rgb, q),
            "wall_hex": hx, "marker": sp.marker_for_wall(hx) if hx else "orange"}


# ---------- prepare ----------

def _sha1(p):
    return hashlib.sha1(Path(p).read_bytes()).hexdigest()


def _ocr_room_text(png, settings, ocr):
    """OCR findings on a blanked reference (any = room text the model might copy)."""
    from . import scene_scan
    hits = ocr(png) if ocr is not None else scene_scan.ocr_findings(png, settings)
    return [{"text": h.get("text", "")[:40], "conf": round(float(h["conf"]), 2), "box": [round(v, 4) for v in h["box"]]}
            for h in hits]


def prepare_one(src, settings=None, detector=None, ocr=None, log=print, work=None):
    """Blank one reference source and return its manifest entry (without uses / grades / tony tags). The _Blank.png is
    written next to the source. detector(src, work, settings, canvas) -> sam_frames reference result (injectable)."""
    import tempfile
    from PIL import Image
    src = Path(src)
    rid = SOURCE_RE.match(src.name).group(1)
    seed = SEED_TAGS.get(rid) or {}
    detector = detector or sam_reference
    with Image.open(src) as im:
        rgb = np.asarray(im.convert("RGB"))
    H, W = rgb.shape[:2]
    ent = {"source": src.name, "blank": blank_name(src.name), "sha1": _sha1(src), "size": [W, H],
           "prep_version": PREP_VERSION, "usable": False, "why": []}
    td_ctx = tempfile.TemporaryDirectory() if work is None else None
    wd = Path(td_ctx.name if td_ctx else work)
    try:
        res, err = None, []
        order = (True, False) if str(seed.get("presentation", "")).startswith("canvas") else (False, True)
        for canvas in order:
            try:
                res = detector(src, wd, settings, canvas)
                break
            except Exception as e:  # noqa: BLE001
                err.append(str(e)[:200])
        if res is None:
            ent["why"] = ["artwork not found: " + (err[-1] if err else "no result")]
            ent["blank_method"] = None
            return ent
        info = res.get("reference") or {}
        if res.get("blank_method") == "mask":
            poly, is_quad = [list(map(float, p)) for p in res["mask_polygon"]], False
            quad = quad_of_polygon(poly)
        else:
            from .sam_frames import offset_quad
            quad = np.float32(res["corners"])
            poly, is_quad = offset_quad(quad, 1.0).tolist(), True       # one pixel under the frame lip
        m = measure(rgb, quad)
        blank = paint(rgb, poly, m["marker"], is_quad)
        ring = leftover_ring(rgb, poly, is_quad)
        eaten = 0 if seed.get("presentation") == "canvas_bare" else frame_eaten(rgb, poly, m["wall_lab"], is_quad)
        out_png = src.with_name(blank_name(src.name))
        Image.fromarray(blank).save(out_png, optimize=False)
        ent.update(blank_method=res.get("blank_method", "sam_quad"),
                   fill_polygon=[[round(float(x), 2), round(float(y), 2)] for x, y in poly],
                   quad=[[round(float(x), 2), round(float(y), 2)] for x, y in np.float32(quad)],
                   marker=m["marker"], wall_hex=m["wall_hex"], wall_lab=m["wall_lab"], aspect=m["aspect"],
                   art_h_frac=m["art_h_frac"], camera_side=m["camera_side"], light_from=m["light_from"],
                   frames=info.get("frames"), mirrors=info.get("mirrors"), screens=info.get("screens"),
                   shape=info.get("shape"), upright=info.get("upright"), leftover_ring=round(ring, 4),
                   frame_eaten_sides=eaten, opening=(res.get("opening") or {}).get("mode"))
        why = []
        if not is_quad:
            why.append("ragged fill (mask mode): blank it by hand and set blank_method tony")
        if ring >= RING_MAX:
            why.append(f"art sliver left beside the fill ({ring:.1%} of the worst side)")
        if eaten >= 2:
            why.append(f"the fill took the frame or mat in too ({eaten} sides)")
        if m["aspect"] > PORTRAIT_MAX:
            why.append(f"not a portrait artwork (true aspect {m['aspect']:.2f})")
        if info.get("frames") not in (None, 1):
            why.append(f"{info.get('frames')} framed pictures in the photo")
        if info.get("mirrors"):
            why.append("a mirror in the photo")
        if info.get("screens"):
            why.append("a screen showing a picture")
        if info.get("upright") is False:
            why.append("the artwork lies flat")
        ent["room_text"] = _ocr_room_text(out_png, settings, ocr)
        if ent["room_text"]:
            why.append("readable text in the room: " + ", ".join(t["text"] for t in ent["room_text"][:3]))
        if seed.get("seed_why"):
            why.append(seed["seed_why"])
        ent["why"] = why
        ent["usable"] = not why
        return ent
    finally:
        if td_ctx:
            td_ctx.cleanup()


def prepare(settings=None, ids=None, force=False, log=print, detector=None, ocr=None, tagger=None):
    """Prepare every reference source of the folder (or only `ids`). Idempotent: a source with the same sha1 and
    prep_version and an existing _Blank.png is skipped; blank_method "tony" entries are never touched; tags_by
    "tony" tags are kept. tagger(entries) -> {id: tags} tags references without seed tags (claude -p vision, free).
    Returns {"prepared": [...], "skipped": [...], "unusable": {id: why}}."""
    folder = ref_dir(settings)
    want = {str(i).zfill(4) for i in ids} if ids else None
    report = {"prepared": [], "skipped": [], "unusable": {}}
    with _LOCK:
        man = load(folder)
    man["prep_version"] = PREP_VERSION
    refs = man.setdefault("refs", {})
    for src in sources(folder):
        rid = SOURCE_RE.match(src.name).group(1)
        if want is not None and rid not in want:
            continue
        old = refs.get(rid) or {}
        if old.get("blank_method") == "tony":
            report["skipped"].append(rid)
            continue
        if (not force and old.get("sha1") == _sha1(src) and old.get("prep_version") == PREP_VERSION
                and (folder / blank_name(src.name)).is_file()):
            report["skipped"].append(rid)
            continue
        log(f"preparing {rid} ({src.name})")
        ent = prepare_one(src, settings, detector, ocr, log)
        for k in ("uses", "grades", "kie_refused"):
            if k in old:
                ent[k] = old[k]
        ent.setdefault("uses", [])
        ent.setdefault("grades", [])
        if old.get("tags_by") == "tony":
            ent["tags"], ent["tags_by"] = old["tags"], "tony"
        elif rid in SEED_TAGS:
            ent["tags"] = {k: v for k, v in SEED_TAGS[rid].items() if k != "seed_why"}
            ent["tags_by"] = SEED_BY
        elif old.get("tags"):
            ent["tags"], ent["tags_by"] = old["tags"], old.get("tags_by")
        refs[rid] = ent
        report["prepared"].append(rid)
        if not ent["usable"]:
            report["unusable"][rid] = ent["why"]
    untagged = [rid for rid, e in refs.items() if not e.get("tags")]
    if untagged and tagger is not None:
        try:
            got = tagger([refs[r] for r in untagged])
            for rid, tags in (got or {}).items():
                if rid in refs and isinstance(tags, dict):
                    refs[rid]["tags"], refs[rid]["tags_by"] = tags, "vision"
        except Exception as e:  # noqa: BLE001
            log(f"vision tagging skipped: {e}")
    for rid, e in refs.items():
        if not e.get("usable") and rid not in report["unusable"]:
            report["unusable"][rid] = e.get("why")
    man["refs"] = dict(sorted(refs.items()))
    with _LOCK:
        save(folder, man)
    return report


# ---------- vision tags for references added later (claude -p, Tony's plan, no credits) ----------

TAG_ENUMS = {"display_group": DISPLAY_GROUPS, "shot": ("tight", "medium", "wide"),
             "camera_height": ("surface", "low", "seated", "counter", "eye"),
             "lens": ("lens_normal", "lens_wide", "lens_short_tele"),
             "light_type": ("hard_diagonal_sun", "morning_soft_sun", "golden_low", "overcast_flat", "rainy_day",
                            "north_light_even", "blind_stripes", "dusk_lamp_mix", "night_lamps"),
             "lived_in": LIVED_IN,
             "window_covering": ("venetian_blind", "roller_blind", "roman_blind", "sheer_curtain", "linen_curtains",
                                 "heavy_drapes", "shutters", "bare", "no_window_in_view")}


def vision_tagger(settings=None, ask=None):
    """tagger(entries) for prepare(): batches of 8 blanks, enum-only JSON. ask(prompt, images) -> raw text."""
    from .prod_chat import encode_image

    def tag(entries):
        a = ask
        if a is None:
            from .slot_planner import default_ask
            a = default_ask(settings, "You tag interior reference photographs with categorical facts. JSON only.")
        folder = ref_dir(settings)
        out = {}
        for i in range(0, len(entries), 8):
            batch = entries[i:i + 8]
            ids = [SOURCE_RE.match(e["source"]).group(1) for e in batch]
            prompt = ("Tag each reference photograph (images in this order: " + ", ".join(ids) + "). The flat colour "
                      "block is a placeholder for the art. Output ONLY {\"<id>\": {" + ", ".join(
                          f'"{k}": one of {list(v)}' for k, v in TAG_ENUMS.items()) + ", \"editorial\": true|false}}.")
            raw = a(prompt, [encode_image(folder / e["blank"], 900) for e in batch])
            t = str(raw)
            obj = json.loads(t[t.find("{"): t.rfind("}") + 1])
            for rid in ids:
                v = obj.get(rid) if isinstance(obj, dict) else None
                if isinstance(v, dict):
                    out[rid] = {k: v.get(k) for k in TAG_ENUMS if v.get(k) in TAG_ENUMS[k]} | {
                        "editorial": bool(v.get("editorial"))}
        return out
    return tag


# ---------- use by the planner and the generator ----------

GRADE_SCORE = {"A+": 4.3, "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7, "C+": 2.3, "C": 2.0, "C-": 1.7, "D": 1.0,
               "F": 0.0}


def mean_grade(entry):
    """Mean past grade 0..1 (None when never graded)."""
    gs = [GRADE_SCORE[g["grade"]] for g in entry.get("grades") or [] if g.get("grade") in GRADE_SCORE]
    return round(sum(gs) / len(gs) / 4.3, 3) if gs else None


def usable(settings=None, man=None):
    """Usable entries in manifest order, each with "id": usable, blank on disk, not refused by kie."""
    folder = ref_dir(settings)
    man = man if man is not None else load(folder)
    out = []
    for rid, e in (man.get("refs") or {}).items():
        if e.get("usable") and not e.get("kie_refused") and e.get("blank") and (folder / e["blank"]).is_file():
            out.append(dict(e, id=rid))
    return out


def blank_for(entry, marker, flip=False, out_dir=None, settings=None):
    """The reference image to send: the _Blank.png itself when its marker matches and no mirror is asked, else a
    re-filled (other marker) and / or mirrored copy in out_dir (the run's temp dir; nothing extra is stored)."""
    from PIL import Image, ImageOps
    folder = ref_dir(settings)
    blank = folder / entry["blank"]
    if entry.get("marker", "orange") == marker and not flip:
        return blank
    if out_dir is None:
        raise ValueError("out_dir is needed for a recoloured or mirrored reference")
    with Image.open(folder / entry["source"] if entry.get("marker") != marker else blank) as im:
        rgb = np.asarray(im.convert("RGB"))
    if entry.get("marker") != marker:
        poly = entry["fill_polygon"]
        rgb = paint(rgb, poly, marker, quad=len(poly) == 4)
    img = Image.fromarray(rgb)
    if flip:
        img = ImageOps.mirror(img)
    out = Path(out_dir) / f"ref_{Path(entry['blank']).stem[:4]}_{marker}{'_flip' if flip else ''}.png"
    img.save(out)
    return out


def contact_sheet(entries, out_png, cell=300, long_side=1568, settings=None):
    """One labelled image of the usable _Blank files for the planner (labels = reference ids)."""
    import math
    from PIL import Image, ImageDraw
    if not entries:
        return None
    folder = ref_dir(settings)
    cols = min(6, max(1, math.ceil(math.sqrt(len(entries) * 1.3))))
    rows = math.ceil(len(entries) / cols)
    lab = 22
    sheet = Image.new("RGB", (cols * cell, rows * (cell + lab)), (245, 243, 238))
    dr = ImageDraw.Draw(sheet)
    for i, e in enumerate(entries):
        x, y = (i % cols) * cell, (i // cols) * (cell + lab)
        try:
            with Image.open(folder / e["blank"]) as im:
                im = im.convert("RGB")
                im.thumbnail((cell - 8, cell - 8))
                sheet.paste(im, (x + 4, y + lab))
        except OSError:
            continue
        dr.text((x + 6, y + 5), str(e.get("id") or e["source"][:4]), fill=(20, 20, 20))
    s = long_side / max(sheet.size)
    if s < 1:
        sheet = sheet.resize((round(sheet.width * s), round(sheet.height * s)), Image.LANCZOS)
    sheet.save(out_png)
    return Path(out_png)


def record_use(settings, rid, use):
    """Append a use row {listing, slot, template, at} to a reference."""
    def fn(man):
        e = (man.get("refs") or {}).get(rid)
        if e is not None:
            e.setdefault("uses", []).append({k: use.get(k) for k in ("idea_id", "listing", "slot", "template")}
                                            | {"at": datetime.now().isoformat(timespec="seconds")})
    try:
        update(settings, fn)
    except Exception:  # noqa: BLE001  (bookkeeping never breaks a build)
        pass


def record_grade(settings, rid, entry):
    """Tony's grade of a slot made from this reference: one entry per (idea, slot), replaced; grade None removes."""
    def fn(man):
        e = (man.get("refs") or {}).get(rid)
        if e is not None:
            gs = [g for g in e.get("grades") or [] if not (g.get("idea_id") == entry.get("idea_id")
                                                          and g.get("slot") == entry.get("slot"))]
            if entry.get("grade"):
                gs.append({k: v for k, v in entry.items() if v is not None})
            e["grades"] = gs
    try:
        update(settings, fn)
    except Exception:  # noqa: BLE001
        pass


def mark_refused(settings, rid):
    def fn(man):
        e = (man.get("refs") or {}).get(rid)
        if e is not None:
            e["kie_refused"] = datetime.now().date().isoformat()
    try:
        update(settings, fn)
    except Exception:  # noqa: BLE001
        pass


if __name__ == "__main__":
    import argparse
    from .db import load_config
    ap = argparse.ArgumentParser(description="Prepare the reference board (blank the art, manifest)")
    ap.add_argument("--prepare", action="store_true")
    ap.add_argument("--ids", help="comma-separated ids, e.g. 0024,0031")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--sheet", help="write a contact sheet of the usable blanks here")
    a = ap.parse_args()
    s = load_config("settings")
    if a.prepare:
        rep = prepare(s, a.ids.split(",") if a.ids else None, a.force, tagger=vision_tagger(s))
        print(json.dumps(rep, indent=1, ensure_ascii=False))
    if a.sheet:
        print(contact_sheet(usable(s), a.sheet, settings=s))
