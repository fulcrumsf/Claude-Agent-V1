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
DEFAULTS = {"reference_dir": "../Creative_Inspiration/Mock-Up_Inspiration", "planner_references": True,
            "reference_lowres_max": 400, "reference_max_side": 2048, "reference_nano_max_credits": 30,
            "reference_lama_model": "~/pinokio/api/comfy.git/app/models/inpaint/big-lama.pt"}
DEFAULT_CLOSENESS = 60
REGISTERS = ("grand_period", "upscale_modern", "ordinary_apartment", "ordinary_house", "small_rental", "japandi",
             "industrial_loft", "farmhouse_cottage", "boho_eclectic", "family_kids", "workspace_studio")
RING_DE = 25.0            # leftover check: a band pixel this far from the band's median colour is an art sliver
RING_MAX = 0.08          # worst side, mean over rows (calibrated on the 26: slivers / objects across a frame >= 0.088)
PORTRAIT_MAX = 0.90       # true width / height; square, landscape and round art is not a display we build
DISPLAY_GROUPS = ("hung", "surface", "shelf", "floor")
LIVED_IN = ("tidy", "lived_in", "busy")
_LOCK = threading.RLock()
LOCK = _LOCK                # the planner reads a manifest snapshot under the same lock (controls addendum A.5)

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
    """Atomic (temp file + rename); nothing is written when the text is unchanged."""
    import os
    p = Path(folder) / MANIFEST
    txt = json.dumps(man, indent=1, ensure_ascii=False) + "\n"
    if not p.is_file() or p.read_text() != txt:
        tmp = p.with_name(p.name + ".tmp")
        tmp.write_text(txt)
        os.replace(tmp, p)


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

TAG_ENUMS = {"display_group": DISPLAY_GROUPS, "shot": ("tight", "medium", "wide"), "register": REGISTERS,
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


def prep_for(entry, marker, flip=False, closeness=DEFAULT_CLOSENESS, out_dir=None, settings=None):
    """The reference image to send at a closeness (controls addendum C.2): v >= 50 sends exactly blank_for (the same
    bytes as the realism addendum); v < 50 a smaller, blurred copy: long side L = 384 + 576 v / 50 (rounded to 32),
    Gaussian sigma = (50 - v) / 50 x 0.012 x L. A photo without framed art is sent as is (no fill to recolour)."""
    from PIL import Image, ImageFilter, ImageOps
    v = int(closeness)
    if entry.get("has_art") is False:
        src = ref_dir(settings) / entry["blank"]
        if not flip and v >= 50:
            return src
        with Image.open(src) as im:
            img = im.convert("RGB")
    else:
        src = blank_for(entry, marker, flip, out_dir, settings)
        if v >= 50:
            return src
        with Image.open(src) as im:
            img = im.convert("RGB")
        flip = False                                # blank_for already mirrored it
    if flip:
        img = ImageOps.mirror(img)
    if out_dir is None:
        raise ValueError("out_dir is needed for a prepared reference")
    if v < 50:
        L, sigma = prep_size(v)
        s = L / max(img.size)
        img = img.resize((max(1, round(img.width * s)), max(1, round(img.height * s))), Image.LANCZOS)
        if sigma > 0:
            img = img.filter(ImageFilter.GaussianBlur(sigma))
    out = Path(out_dir) / f"ref_{Path(entry['blank']).stem[:4]}_{marker}{'_flip' if flip else ''}_c{v}.png"
    img.save(out)
    return out


def prep_size(v):
    """(long side, blur sigma) for closeness v < 50."""
    v = max(0, min(49, int(v)))
    L = int(round((384 + (960 - 384) * v / 50) / 32) * 32)
    return L, round((50 - v) / 50 * 0.012 * L, 3)


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


# ---------- Refresh library (controls addendum A, 2026-11-21) ----------
SRC_EXT = (".png", ".jpg", ".jpeg", ".webp", ".heic")
LOG_FILES = ("Rename_Log.md", "Cleanup_Log.md", MANIFEST)
CROP_MAX = 0.08          # a crop removes at most 8% of a side
FRAME_GROW = 0.03        # the frame box dilated 3% (a crop or a LaMa mask never touches it)
MASK_DILATE = 6          # px around an overlay box
MASK_MAX = 0.02          # LaMa mask at most 2% of the picture
TEXTURE_BAND = (0.35, 3.0)
RING_PX = 12
NANO_CREDITS = 6         # wide_fill (nb21 at 2K), measured 2026-11-15
_refresh = {"running": False, "step": "", "done": 0, "total": 0, "current": "", "results": [], "started": None,
            "finished": None, "message": ""}
_refresh_lock = threading.Lock()


def _rcfg(settings, key):
    return (settings or {}).get(key, DEFAULTS[key])


def _expand(p):
    import os
    return Path(os.path.expanduser(str(p)))


def refresh_state():
    with _refresh_lock:
        return {**_refresh, "results": list(_refresh["results"])}


def _progress(**kw):
    with _refresh_lock:
        _refresh.update(kw)


def pending(settings=None, man=None):
    """Images not yet processed: any image in the folder (not Archive/, not a _Blank) that is not NNNN_<Words>.png,
    or is one without a manifest entry, or whose sha1 differs from its entry. [(path, reason)]."""
    folder = ref_dir(settings)
    man = man if man is not None else load(folder)
    refs = man.get("refs") or {}
    out = []
    if not folder.is_dir():
        return out
    for p in sorted(folder.iterdir()):
        if not p.is_file() or p.name.startswith(".") or p.name in LOG_FILES or p.suffix.lower() not in SRC_EXT:
            continue
        if p.stem.endswith("_Blank") or p.stem.endswith("_Cleanup_Check"):
            continue
        m = SOURCE_RE.match(p.name)
        if not m:
            out.append((p, "new"))
            continue
        e = refs.get(m.group(1))
        if e is None:
            out.append((p, "no manifest entry"))
        elif e.get("blank_method") != "tony" and e.get("sha1") and e["sha1"] != _sha1(p):
            out.append((p, "changed"))
    return out


def _arch_dest(arch, name):
    """Backup rule A.3: Archive/<name>; taken -> <stem>_Original, _Original_2, ... (never overwritten)."""
    dest = arch / name
    if not dest.exists():
        return dest
    stem, suf = Path(name).stem, Path(name).suffix
    dest = arch / f"{stem}_Original{suf}"
    k = 2
    while dest.exists():
        dest = arch / f"{stem}_Original_{k}{suf}"
        k += 1
    return dest


def backup(src, arch):
    """Copy the untouched original into Archive/ before any edit. Returns the backup path."""
    arch.mkdir(exist_ok=True)                   # Archive/ already exists (Tony's pre-approved Archive rule)
    dest = _arch_dest(arch, src.name)
    shutil.copy2(src, dest)
    return dest


def archive_move(src, arch):
    arch.mkdir(exist_ok=True)
    dest = _arch_dest(arch, src.name)
    shutil.move(str(src), str(dest))
    return dest


def normalise(path, settings=None, arch=None):
    """Step 1-2 (free): heic -> png (macOS sips), EXIF orientation applied, re-saved as PNG (EXIF / GPS dropped), the
    longest side capped at reference_max_side (Lanczos). The untouched original goes to Archive/ first. A picture whose
    longest side <= reference_lowres_max is moved to Archive/ unchanged instead. Returns (png path | None, note)."""
    from PIL import Image, ImageOps
    folder = path.parent
    arch = arch or folder / "Archive"
    src = path
    tmp = None
    if path.suffix.lower() == ".heic":
        import tempfile
        tmp = Path(tempfile.mkdtemp()) / (path.stem + ".png")
        r = subprocess.run(["sips", "-s", "format", "png", str(path), "--out", str(tmp)], capture_output=True, text=True)
        if r.returncode or not tmp.is_file():
            return None, "could not read the HEIC file"
        src = tmp
    try:
        with Image.open(src) as im:
            w, h = im.size
            exif = bool(im.getexif())
            img = ImageOps.exif_transpose(im).convert("RGB")
    except Exception:  # noqa: BLE001
        return None, "not a readable image"
    if max(w, h) <= int(_rcfg(settings, "reference_lowres_max")):
        archive_move(path, arch)
        return None, f"archived: too small ({max(w, h)} px)"
    cap = int(_rcfg(settings, "reference_max_side"))
    resized = max(img.size) > cap
    if resized:
        s = cap / max(img.size)
        img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    out = path.with_suffix(".png")
    if path.suffix.lower() == ".png" and not exif and not resized and img.size == (w, h):
        return path, ""
    backup(path, arch)
    img.save(out, format="PNG")
    if out != path:
        path.unlink()                          # the original is in Archive/ (copied above): a move, not a loss
    return out, ("resized to " + str(cap) if resized else "re-saved as PNG")


def next_id(folder):
    """1 + the max id over the folder, Archive/ and Rename_Log.md (never reuses an id)."""
    ids = [0]
    for d in (folder, folder / "Archive"):
        if d.is_dir():
            ids += [int(m.group(1)) for p in d.iterdir() if (m := re.match(r"^(\d{4})_", p.name))]
    log = folder / "Rename_Log.md"
    if log.is_file():
        ids += [int(x) for x in re.findall(r"^\|\s*(\d{4})\s*\|", log.read_text(), re.M)]
    return max(ids) + 1


def clean_words(text, n=10):
    words = [w for w in re.split(r"[^A-Za-z0-9]+", str(text or "")) if w][:n]
    return "_".join(w if w.isupper() and len(w) > 1 else w[:1].upper() + w[1:] for w in words) or "Reference"


def rename_batch(paths, ask):
    """Free (claude -p vision, Tony's plan): <= 10 Title_Case name words per image, batches of 8. {path: words}."""
    from .prod_chat import encode_image
    out = {}
    for i in range(0, len(paths), 8):
        batch = paths[i:i + 8]
        prompt = ("Name each room photograph (images in this order: " + ", ".join(str(k + 1) for k in range(len(batch)))
                  + ") for a file name: at most 10 plain words about the setting, surface, frame, scale and camera "
                  "(for example \"Floor Lean Thin Oak Frame Herringbone Floor French Door\"). Never name popups, "
                  "buttons or overlay labels. Output ONLY {\"1\": \"words\", ...}.")
        raw = str(ask(prompt, [encode_image(p, 900) for p in batch]))
        try:
            obj = json.loads(raw[raw.find("{"): raw.rfind("}") + 1])
        except ValueError:
            obj = {}
        for k, pth in enumerate(batch):
            out[pth] = clean_words(obj.get(str(k + 1)) if isinstance(obj, dict) else None)
    return out


def _log_rows(path, title, header, rows, total=None):
    """Append a dated table to a log file (existing format)."""
    if not rows:
        return
    txt = path.read_text() if path.is_file() else f"# {title}\n"
    day = datetime.now().date().isoformat()
    block = f"\n## {day} refresh\n\n{header}\n" + "\n".join(rows) + "\n"
    if total:
        block += f"\n{total}\n"
    path.write_text(txt.rstrip("\n") + "\n" + block)


def _mask_from_box(box, W, H, d=MASK_DILATE):
    m = np.zeros((H, W), bool)
    x0, y0, x1, y1 = box
    m[max(0, int(y0 * H) - d):min(H, int(np.ceil(y1 * H)) + d), max(0, int(x0 * W) - d):min(W, int(np.ceil(x1 * W)) + d)] = True
    return m


def _grow_box(b, f):
    w, h = b[2] - b[0], b[3] - b[1]
    return [b[0] - f * w, b[1] - f * h, b[2] + f * w, b[3] + f * h]


def _hits(a, b):
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])


def plan_fix(f, frame):
    """crop | lama for one overlay finding (A.1 step 5): crop when it touches an edge, the strip is <= 8% of that side
    and the strip does not touch the frame box (dilated 3%)."""
    b = f["box"]
    fr = _grow_box(frame, FRAME_GROW) if frame else None
    opts = []
    if b[1] <= 0.01 and b[3] <= CROP_MAX:
        opts.append(("top", b[3], [0, 0, 1, b[3]]))
    if b[3] >= 0.99 and 1 - b[1] <= CROP_MAX:
        opts.append(("bottom", 1 - b[1], [0, b[1], 1, 1]))
    if b[0] <= 0.01 and b[2] <= CROP_MAX:
        opts.append(("left", b[2], [0, 0, b[2], 1]))
    if b[2] >= 0.99 and 1 - b[0] <= CROP_MAX:
        opts.append(("right", 1 - b[0], [b[0], 0, 1, 1]))
    opts = [o for o in opts if not (fr and _hits(o[2], fr))]
    if opts:
        side, frac, _ = min(opts, key=lambda o: o[1])
        return {"method": "crop", "side": side, "frac": frac}
    return {"method": "lama"}


def _after_crop(box, fix):
    """A 0..1 box in the picture after a crop of `frac` from `side`."""
    f = fix["frac"]
    x0, y0, x1, y1 = box
    if fix["side"] == "top":
        return [x0, (y0 - f) / (1 - f), x1, (y1 - f) / (1 - f)]
    if fix["side"] == "bottom":
        return [x0, y0 / (1 - f), x1, y1 / (1 - f)]
    if fix["side"] == "left":
        return [(x0 - f) / (1 - f), y0, (x1 - f) / (1 - f), y1]
    return [x0 / (1 - f), y0, x1 / (1 - f), y1]


def apply_crop(rgb, side, frac):
    H, W = rgb.shape[:2]
    if side == "top":
        return rgb[int(np.ceil(frac * H)):]
    if side == "bottom":
        return rgb[:H - int(np.ceil(frac * H))]
    if side == "left":
        return rgb[:, int(np.ceil(frac * W)):]
    return rgb[:, :W - int(np.ceil(frac * W))]


def texture_ratio(rgb, mask, ring=RING_PX):
    """Laplacian variance inside the mask / in a ring around it (1.0 = same texture)."""
    import cv2
    g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype("float32")
    lap = cv2.Laplacian(g, cv2.CV_32F)
    k = 2 * ring + 1
    outer = cv2.dilate(mask.astype("uint8"), np.ones((k, k), "uint8")) > 0
    band = outer & ~mask
    if mask.sum() < 4 or band.sum() < 4:
        return 1.0
    vi, vo = float(lap[mask].var()), float(lap[band].var())
    if vo < 1e-6:
        return 1.0 if vi < 1e-6 else 99.0
    return vi / vo


def lama_fill(png, mask, out_png, settings=None, runner=None):
    """LaMa (big-lama TorchScript) in the SAM venv: python -m app.references --lama <in> <mask> <out>. The result is
    pasted back only inside the mask (outside pixels bit-identical). runner(in, mask, out) is injectable."""
    from PIL import Image
    import os
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        mpng = Path(td) / "mask.png"
        Image.fromarray((mask.astype("uint8") * 255)).save(mpng)
        raw = Path(td) / "lama.png"
        if runner is not None:
            runner(str(png), str(mpng), str(raw))
        else:
            from .scene_templates import _cfg as scfg
            py = _expand(scfg(settings, "sam_python"))
            model = _expand(_rcfg(settings, "reference_lama_model"))
            if not py.is_file() or not model.is_file():
                raise RuntimeError("LaMa is not installed (SAM venv or big-lama.pt missing)")
            root = Path(__file__).resolve().parent.parent
            r = subprocess.run([str(py), "-m", "app.references", "--lama", str(png), str(mpng), str(raw),
                                "--model", str(model)], cwd=str(root), capture_output=True, text=True, timeout=600,
                               env={**os.environ, "PYTHONNOUSERSITE": "1"})
            if r.returncode or not raw.is_file():
                raise RuntimeError("LaMa failed: " + (r.stderr or r.stdout).strip()[-200:])
        with Image.open(png) as a, Image.open(raw) as b:
            orig = np.asarray(a.convert("RGB"))
            res = np.asarray(b.convert("RGB").resize(a.size))
    out = np.where(mask[..., None], res, orig).astype("uint8")
    Image.fromarray(out).save(out_png)
    return Path(out_png)


def _lama_main(inp, mask, out, model):
    """The --lama script mode (runs inside the SAM venv, which has torch)."""
    import torch
    from PIL import Image
    m = torch.jit.load(model, map_location="cpu")
    m.eval()
    img = np.asarray(Image.open(inp).convert("RGB")).astype("float32") / 255.0
    msk = (np.asarray(Image.open(mask).convert("L")) > 127).astype("float32")
    H, W = msk.shape
    ph, pw = (8 - H % 8) % 8, (8 - W % 8) % 8
    img_p = np.pad(img, ((0, ph), (0, pw), (0, 0)), mode="reflect")
    msk_p = np.pad(msk, ((0, ph), (0, pw)), mode="reflect")
    with torch.no_grad():
        r = m(torch.from_numpy(img_p).permute(2, 0, 1)[None], torch.from_numpy(msk_p)[None, None])
    res = r[0].permute(1, 2, 0).numpy()[:H, :W]
    Image.fromarray(np.clip(res * 255, 0, 255).astype("uint8")).save(out)


def clean_overlays(png, scan_res, settings=None, lama=None, rescan=None, check_out=None):
    """Step 5: crop / LaMa each overlay finding, then the confidence check (A.1). Edits `png` in place (the caller
    backed it up first). Crops go first (the other boxes move with each crop); the rest share one LaMa mask. A low
    confidence result writes a before / after strip to check_out. Returns the cleanup record."""
    from PIL import Image
    frame = scan_res.get("frame_box")
    fs = [dict(f) for f in scan_res.get("findings") or []]
    rec = {"overlays": [{"type": f["type"], "box": [round(v, 4) for v in f["box"]]} for f in fs], "method": "none",
           "confidence": "high", "at": datetime.now().isoformat(timespec="seconds")}
    if not fs:
        return rec
    with Image.open(png) as im:
        rgb = np.asarray(im.convert("RGB"))
    methods = []
    todo = sorted(fs, key=lambda f: 0 if plan_fix(f, frame)["method"] == "crop" else 1)
    lama_fs = []
    while todo:
        f = todo.pop(0)
        fix = plan_fix(f, frame)
        if fix["method"] == "crop":
            rgb = apply_crop(rgb, fix["side"], fix["frac"])
            methods.append("crop")
            frame = _after_crop(frame, fix) if frame else None      # the other boxes move with the crop
            todo = [dict(g, box=_after_crop(g["box"], fix)) for g in todo]
            lama_fs = [dict(g, box=_after_crop(g["box"], fix)) for g in lama_fs]
        else:
            lama_fs.append(f)
    Image.fromarray(rgb).save(png)
    if lama_fs:
        H, W = rgb.shape[:2]
        mask = np.zeros((H, W), bool)
        for f in lama_fs:
            mask |= _mask_from_box(f["box"], W, H)
        lama_fill(png, mask, png, settings, lama)
        methods.append("lama")
        with Image.open(png) as im:
            after = np.asarray(im.convert("RGB"))
        area = float(mask.mean())
        tex = texture_ratio(after, mask)
        fr = _grow_box(frame, FRAME_GROW) if frame else None
        touches = bool(fr and any(_hits(f["box"], fr) for f in lama_fs))
        left = []
        if rescan is not None:
            try:
                again = rescan(png) or {}
                left = [g for g in again.get("findings") or [] if any(_hits(g["box"], f["box"]) for f in lama_fs)]
            except Exception:  # noqa: BLE001
                left = []
        rec["checks"] = {"mask_area": round(area, 4), "texture": round(tex, 3), "touches_frame": touches,
                         "left": len(left)}
        if left or not (TEXTURE_BAND[0] <= tex <= TEXTURE_BAND[1]) or area > MASK_MAX or touches:
            rec["confidence"] = "low"
            rec["mask_boxes"] = [[round(v, 4) for v in f["box"]] for f in lama_fs]
            if check_out is not None:
                _check_image(rgb, after, rec["mask_boxes"], check_out)
                rec["check_image"] = f"Archive/{Path(check_out).name}"
    rec["method"] = "lama" if "lama" in methods else ("crop" if methods else "none")
    return rec


def _check_image(before, after, boxes, out):
    """Before / after crop of the cleaned region (uint8 arrays of one size), side by side, saved in Archive/."""
    from PIL import Image
    if True:
        a, b = Image.fromarray(before), Image.fromarray(after)
        W, H = a.size
        x0 = max(0, int(min(bx[0] for bx in boxes) * W) - 60)
        y0 = max(0, int(min(bx[1] for bx in boxes) * H) - 60)
        x1 = min(W, int(max(bx[2] for bx in boxes) * W) + 60)
        y1 = min(H, int(max(bx[3] for bx in boxes) * H) + 60)
        ca, cb = a.crop((x0, y0, x1, y1)), b.crop((x0, y0, x1, y1))
        sheet = Image.new("RGB", (ca.width * 2 + 8, ca.height), (255, 255, 255))
        sheet.paste(ca, (0, 0))
        sheet.paste(cb, (ca.width + 8, 0))
        sheet.save(out)
    return out


def default_vision_ask(settings=None, system="You look at interior photographs and answer with JSON only."):
    from .slot_planner import default_ask
    return default_ask(settings, system)


def register_batch(entries, ask, settings=None):
    """The register tag (A.4) for entries that miss it: claude -p vision, batches of 8. {id: register}."""
    from .prod_chat import encode_image
    folder = ref_dir(settings)
    out = {}
    for i in range(0, len(entries), 8):
        batch = entries[i:i + 8]
        ids = [e["id"] for e in batch]
        prompt = ("For each room photograph (images in this order: " + ", ".join(ids) + ") say what kind of home it "
                  f"is. Output ONLY {{\"<id>\": one of {list(REGISTERS)}}}.")
        raw = str(ask(prompt, [encode_image(folder / (e.get("blank") or e["source"]), 900) for e in batch]))
        try:
            obj = json.loads(raw[raw.find("{"): raw.rfind("}") + 1])
        except ValueError:
            obj = {}
        for rid in ids:
            v = obj.get(rid) if isinstance(obj, dict) else None
            if v in REGISTERS:
                out[rid] = v
    return out


def refresh(settings=None, ask_vision=None, scan=None, lama=None, detector=None, ocr=None, tagger=None, log=None,
            dry_run=False):
    """One click of Refresh library (A.1): normalise, low-res sweep, rename, overlay scan + clean-up (crop / LaMa +
    confidence check), blank + measure + manifest, tags + register. Free (SAM, LaMa, OCR local; Gemini flash-lite;
    claude -p). Never spends credits, never deletes (files only move into Archive/ or get a backup copy there).
    Idempotent: nothing new -> no work, nothing written. Returns {"results": [...], "counts": {...}}.
    dry_run: report what would happen, write nothing."""
    from . import scene_scan
    log = log or (lambda *_: None)
    folder = ref_dir(settings)
    arch = folder / "Archive"
    ask = ask_vision
    scan = scan or (lambda png: scene_scan.scan_reference(png, settings))
    with _LOCK:
        man = load(folder)
    todo = pending(settings, man)
    refs = man.get("refs") or {}
    miss_reg = [dict(e, id=rid) for rid, e in refs.items()
                if not (e.get("tags") or {}).get("register") and e.get("tags_by") != "tony" and not e.get("archived")
                and e.get("blank") and (folder / e["blank"]).is_file()]
    results = []
    if dry_run:
        for p, why in todo:
            results.append({"file": p.name, "plan": why})
        return {"results": results, "pending": len(todo), "register_missing": len(miss_reg), "dry_run": True}
    if not todo and not miss_reg:
        return {"results": [], "pending": 0, "register_missing": 0, "nothing_new": True}
    _progress(total=len(todo) + (1 if miss_reg else 0), done=0)
    if ask is None:
        ask = default_vision_ask(settings)
    # 1-2: normalise + low-res sweep
    work = []
    for p, why in todo:
        _progress(step="normalising", current=p.name)
        png, note = normalise(p, settings, arch)
        if png is None:
            results.append({"file": p.name, "status": "archived" if note.startswith("archived") else "skipped",
                            "note": note})
            _progress(done=_refresh["done"] + 1)
            continue
        work.append({"path": png, "was": p.name, "why": why, "note": note})
    # 3: rename (only names that are not NNNN_Words.png)
    to_name = [w for w in work if not SOURCE_RE.match(w["path"].name)]
    if to_name:
        _progress(step="naming", current=", ".join(w["path"].name[:20] for w in to_name[:3]))
        names = rename_batch([w["path"] for w in to_name], ask)
        nid = next_id(folder)
        rows = []
        for w in to_name:
            words = names.get(w["path"]) or "Reference"
            new = folder / f"{nid:04d}_{words}.png"
            k = 2
            while new.exists() or (arch / new.name).exists():
                new = folder / f"{nid:04d}_{words}_{k}.png"
                k += 1
            shutil.move(str(w["path"]), str(new))
            rows.append(f"| {nid:04d} | {w['was']} | {new.name} |")
            w.update(path=new, renamed_from=w["was"])
            nid += 1
        _log_rows(folder / "Rename_Log.md", "Mock-Up Inspiration - Rename Log", "| id | original_filename | new_filename |"
                  "\n|---|---|---|", rows)
    # 4-5: overlays + clean-up
    clog = []
    cleanups = {}
    for w in work:
        p = w["path"]
        rid = SOURCE_RE.match(p.name).group(1)
        _progress(step="looking for overlays", current=f"{rid}")
        try:
            sres = scan(p)
        except Exception as e:  # noqa: BLE001
            sres = {"findings": [], "frame_box": None, "notes": [str(e)[:80]]}
        w["frame_box"] = sres.get("frame_box")
        if sres.get("findings"):
            orig = backup(p, arch)
            try:
                rec = clean_overlays(p, sres, settings, lama, rescan=scan,
                                     check_out=_arch_dest(arch, f"{p.stem}_Cleanup_Check.png"))
            except Exception as e:  # noqa: BLE001
                shutil.copy2(orig, p)                 # LaMa broke: the untouched picture goes back
                rec = {"overlays": [{"type": f["type"], "box": f["box"]} for f in sres["findings"]], "method": "none",
                       "confidence": "low", "error": str(e)[:160], "at": datetime.now().isoformat(timespec="seconds")}
            rec["original"] = f"Archive/{orig.name}"
            cleanups[rid] = rec
            where = ", ".join(scene_scan._where(f["box"]) for f in sres["findings"])
            clog.append(f"| {rid} | {', '.join(sorted({f['type'] for f in sres['findings']}))} | {where} | "
                        f"{rec['method']} | {'ok' if rec['confidence'] == 'high' else 'needs your eye'} |")
        else:
            cleanups[rid] = {"overlays": [], "method": "none", "confidence": "high",
                             "at": datetime.now().isoformat(timespec="seconds")}
    # 6-7: blank + measure + manifest, tags + register (prepare() keeps uses, grades and Tony's tags)
    ids = [SOURCE_RE.match(w["path"].name).group(1) for w in work]
    tagger = tagger or vision_tagger(settings, ask)
    if ids:
        _progress(step="finding the artwork (SAM)", current=", ".join(ids))
        prepare(settings, ids, True, log, detector, ocr, tagger)
    with _LOCK:
        man = load(folder)
        refs = man.setdefault("refs", {})
        for w in work:
            rid = SOURCE_RE.match(w["path"].name).group(1)
            e = refs.get(rid)
            if e is None:
                continue
            if w.get("renamed_from"):
                e["renamed_from"] = w["renamed_from"]
            cu = cleanups.get(rid)
            if cu:
                e["cleanup"] = cu
            no_art = (not e.get("blank_method") and any(str(x).startswith("artwork not found") for x in e.get("why") or [])
                      and not w.get("frame_box"))
            if no_art:                                # a real-home photo without framed art: tags / loose use only
                blank = folder / blank_name(w["path"].name)
                shutil.copy2(w["path"], blank)
                e.update(has_art=False, blank_method="none", blank=blank.name,
                         why=[x for x in e.get("why") or [] if not str(x).startswith("artwork not found")])
            else:
                e.setdefault("has_art", True)
            if cu and cu.get("confidence") == "low" and cu.get("ok_by") != "tony":
                e["why"] = list(dict.fromkeys(list(e.get("why") or []) + ["clean-up needs your eye"]))
            e["usable"] = not e.get("why")
        man["refs"] = dict(sorted(refs.items()))
        save(folder, man)
    # register for every entry missing it (the 26 old ones once)
    with _LOCK:
        man = load(folder)
    miss = [dict(e, id=rid) for rid, e in (man.get("refs") or {}).items()
            if not (e.get("tags") or {}).get("register") and e.get("tags_by") != "tony" and not e.get("archived")
            and e.get("blank") and (folder / e["blank"]).is_file()]
    if miss:
        _progress(step="tagging the kind of home", current=f"{len(miss)} references")
        try:
            got = register_batch(miss, ask, settings)
        except Exception as e:  # noqa: BLE001
            got = {}
            log(f"register tagging skipped: {e}")

        def fn(m):
            for rid, reg in got.items():
                e = (m.get("refs") or {}).get(rid)
                if e is not None and e.get("tags_by") != "tony":
                    e.setdefault("tags", {})["register"] = reg
        update(settings, fn)
    if clog:
        _log_rows(folder / "Cleanup_Log.md", "Mock-Up Inspiration - Cleanup Log",
                  "| id | overlay found | where | fix used | result |\n|---|---|---|---|---|", clog,
                  "Totals: kie.ai credits spent 0 (LaMa and crops are local and free).")
    with _LOCK:
        man = load(folder)
    for w in work:
        rid = SOURCE_RE.match(w["path"].name).group(1)
        e = (man.get("refs") or {}).get(rid) or {}
        cu = e.get("cleanup") or {}
        results.append({"id": rid, "file": w["path"].name, "was": w.get("renamed_from"), "status":
                        "needs_eye" if cu.get("confidence") == "low" and cu.get("ok_by") != "tony" else
                        ("ready" if e.get("usable") else "unusable"),
                        "cleanup": cu.get("method"), "spots": len(cu.get("overlays") or []),
                        "register": (e.get("tags") or {}).get("register"), "has_art": e.get("has_art", True),
                        "why": e.get("why"), "check_image": cu.get("check_image")})
    return {"results": results, "pending": len(todo), "register_missing": len(miss)}


def counts(settings=None):
    man = load(ref_dir(settings))
    refs = man.get("refs") or {}
    eye = [rid for rid, e in refs.items() if (e.get("cleanup") or {}).get("confidence") == "low"
           and (e.get("cleanup") or {}).get("ok_by") != "tony" and not e.get("archived")]
    return {"usable": len(usable(settings, man)), "need_eye": len(eye), "refs_total": len(refs)}


def refresh_view(settings=None):
    st = refresh_state()
    try:
        c = counts(settings)
    except Exception:  # noqa: BLE001
        c = {}
    return {"running": st["running"], "step": st["step"], "done": st["done"], "total": st["total"],
            "current": st["current"], "results": st["results"], "finished": st["finished"], "message": st["message"],
            **c, "pending": len(pending(settings))}


def start_refresh(settings, spawn, **kw):
    with _refresh_lock:
        if _refresh["running"]:
            return False
        _refresh.update(running=True, step="starting", done=0, total=0, current="", results=[], message="",
                        started=datetime.now().isoformat(timespec="seconds"), finished=None)
    spawn(_run_refresh, settings, kw)
    return True


def _run_refresh(settings, kw):
    try:
        res = refresh(settings, **kw)
        msg = "nothing new" if res.get("nothing_new") else f"{len(res['results'])} processed"
        _progress(results=res["results"], message=msg)
    except Exception as e:  # noqa: BLE001
        _progress(message=f"refresh stopped: {str(e)[:200]}")
    finally:
        _progress(running=False, step="", current="", finished=datetime.now().isoformat(timespec="seconds"))


def recover():
    """A refresh cut by a restart: the module state is fresh; files are never half-written (atomic writes)."""
    with _refresh_lock:
        if _refresh["running"]:
            _refresh.update(running=False, message="stopped by a restart")


def mark_ok(settings, rid):
    """Tony's "Looks fine": cleanup.ok_by tony, usable re-evaluated."""
    def fn(man):
        e = (man.get("refs") or {}).get(rid)
        if e is None:
            raise KeyError(rid)
        e.setdefault("cleanup", {})["ok_by"] = "tony"
        e["why"] = [x for x in e.get("why") or [] if x != "clean-up needs your eye"]
        e["usable"] = not e["why"]
    return update(settings, fn)


def archive_ref(settings, rid):
    """Tony's "Archive it": source + _Blank move to Archive/ (never deleted); the entry is kept, marked archived."""
    folder = ref_dir(settings)
    arch = folder / "Archive"

    def fn(man):
        e = (man.get("refs") or {}).get(rid)
        if e is None:
            raise KeyError(rid)
        for k in ("source", "blank"):
            f = folder / str(e.get(k) or "")
            if e.get(k) and f.is_file():
                archive_move(f, arch)
        e.update(archived=datetime.now().date().isoformat(), usable=False)
    return update(settings, fn)


def nano_plan(settings, ids):
    """The paid Nano fill (A.2): cost and refusal above the cap. Never called by refresh()."""
    n = len(ids)
    cost = NANO_CREDITS * n
    cap = int(_rcfg(settings, "reference_nano_max_credits"))
    return {"n": n, "credits": cost, "cap": cap, "ok": cost <= cap}


def nano_fill(ids, settings=None, generator=None):
    """Nano Banana 2.1 wide-crop fill (app/wide_fill.py, ~6 credits each) on the low-confidence LaMa regions, only on
    Tony's click; refuses above reference_nano_max_credits. Backs up first, re-runs the confidence check, logs to
    Cleanup_Log.md. A kie refusal costs nothing and is listed. generator(engine, src, out, prompt) is injectable."""
    from PIL import Image
    from . import wide_fill as wf
    plan = nano_plan(settings, ids)
    if not plan["ok"]:
        raise ValueError(f"{plan['credits']} credits is over the cap of {plan['cap']}; pick fewer images")
    folder = ref_dir(settings)
    arch = folder / "Archive"
    man = load(folder)
    out, rows = [], []
    for rid in ids:
        e = (man.get("refs") or {}).get(rid) or {}
        cu = e.get("cleanup") or {}
        boxes = cu.get("mask_boxes") or [o["box"] for o in cu.get("overlays") or []]
        src = folder / str(e.get("source") or "")
        if not boxes or not src.is_file():
            out.append({"id": rid, "status": "skipped", "why": "nothing to fill"})
            continue
        backup(src, arch)
        with Image.open(src) as im:
            rgb = np.asarray(im.convert("RGB"))
        H, W = rgb.shape[:2]
        box = [min(b[0] for b in boxes) * W, min(b[1] for b in boxes) * H, max(b[2] for b in boxes) * W,
               max(b[3] for b in boxes) * H]
        p = wf.plan(rgb, box)
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            send = Path(td) / "send.png"
            wf.crop_for_model(rgb, p).save(send)
            ans = Path(td) / "ans.png"
            try:
                if generator is not None:
                    generator(wf.ENGINE, send, ans, wf.instruction("remove the overlay and continue the room", p))
                else:
                    from .scene_templates import kie_module
                    kie_module(settings).edit(wf.ENGINE, send, ans, wf.instruction(
                        "remove the overlay and continue the room", p), "2K")
            except (Exception, SystemExit) as ex:  # noqa: BLE001
                out.append({"id": rid, "status": "refused", "why": str(ex)[:160]})
                rows.append(f"| {rid} | {', '.join(o['type'] for o in cu.get('overlays') or [])} | - | nano | "
                            f"kie refused ({str(ex)[:60]}), 0 credits |")
                continue
            with Image.open(ans) as a:
                res, _ = wf.composite(rgb, np.asarray(a.convert("RGB")), p)
        Image.fromarray(res).save(src)
        mask = np.zeros((H, W), bool)
        for b in boxes:
            mask |= _mask_from_box(b, W, H)
        tex = texture_ratio(res, mask)
        ok = TEXTURE_BAND[0] <= tex <= TEXTURE_BAND[1]

        def fn(m, rid=rid, ok=ok, tex=tex):
            en = (m.get("refs") or {}).get(rid)
            if en is not None:
                en.setdefault("cleanup", {}).update(method="nano", confidence="high" if ok else "low",
                                                    checks={"texture": round(tex, 3)})
                if ok:
                    en["why"] = [x for x in en.get("why") or [] if x != "clean-up needs your eye"]
                    en["usable"] = not en["why"]
                    en["sha1"] = _sha1(src)
        update(settings, fn)
        out.append({"id": rid, "status": "filled" if ok else "needs_eye"})
        rows.append(f"| {rid} | {', '.join(o['type'] for o in cu.get('overlays') or [])} | - | nano | "
                    f"{'ok' if ok else 'needs your eye'} |")
    _log_rows(folder / "Cleanup_Log.md", "Mock-Up Inspiration - Cleanup Log",
              "| id | overlay found | where | fix used | result |\n|---|---|---|---|---|", rows,
              f"Totals: kie.ai credits about {NANO_CREDITS * sum(1 for o in out if o['status'] in ('filled', 'needs_eye'))}"
              " (Nano Banana 2.1 wide-crop fill).")
    return out


if __name__ == "__main__":
    import sys as _sys
    if "--lama" in _sys.argv:                    # LaMa script mode (SAM venv): before any Portal import
        k = _sys.argv.index("--lama")
        model = _sys.argv[_sys.argv.index("--model") + 1] if "--model" in _sys.argv else DEFAULTS["reference_lama_model"]
        _lama_main(_sys.argv[k + 1], _sys.argv[k + 2], _sys.argv[k + 3], str(_expand(model)))
        raise SystemExit(0)
    import argparse
    from .db import load_config
    ap = argparse.ArgumentParser(description="Prepare the reference board (blank the art, manifest)")
    ap.add_argument("--prepare", action="store_true")
    ap.add_argument("--refresh", action="store_true", help="Refresh library: new images in, cleaned, named, blanked")
    ap.add_argument("--dry-run", action="store_true", help="with --refresh: report only, write nothing")
    ap.add_argument("--ids", help="comma-separated ids, e.g. 0024,0031")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--sheet", help="write a contact sheet of the usable blanks here")
    a = ap.parse_args()
    s = load_config("settings")
    if a.refresh:
        print(json.dumps(refresh(s, dry_run=a.dry_run, log=print), indent=1, ensure_ascii=False, default=str))
    if a.prepare:
        rep = prepare(s, a.ids.split(",") if a.ids else None, a.force, tagger=vision_tagger(s))
        print(json.dumps(rep, indent=1, ensure_ascii=False))
    if a.sheet:
        print(contact_sheet(usable(s), a.sheet, settings=s))
