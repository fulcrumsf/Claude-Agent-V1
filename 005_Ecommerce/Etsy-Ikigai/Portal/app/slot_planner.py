"""Slot-set planner (Pipeline_Docs/Slot_Set_Planner_Plan.md, built 2026-11-19): ONE planned set of room scenes per
listing instead of a random look per click.

A planner (headless `claude -p` through assistant.run_cli, Tony's plan, no credits) sees the art, the slot images that
already exist and the open slots, and writes one scene brief per open slot in a single pass. Code then
  - derives what the model must not get wrong (ratio + scale from the print size, wall family + insert MARKER colour
    from the wall hex),
  - lints every brief (hard rules: scale vs shot, canvas size, camera geometry, marker vs wall, frame vs wall contrast,
    panelling, no people / pets / readable text, 60-160 words),
  - checks the whole set for balance and similarity (check_set; approved slots count but are never blamed),
  - asks the model to rewrite only the blamed slots (bounded rounds), keeps the best round,
  - swaps a "new" brief for a free library template when one fits as well (library_swap),
  - assembles the prompt actually sent (assemble: scene text + fixed pipeline-safety blocks, never left to the model).

Tony's decisions 2026-11-19 (override the plan):
  - PORTRAIT ONLY: every frame is portrait. ORIENTATION below is the one hook for a later pre-production setting;
    nothing reads another value yet. The picture itself stays the 4:3 Etsy listing photo (room_scene_aspect).
  - Warm walls are allowed: the blank insert MARKER is picked per scene opposite the wall: orange by default (today's
    path, byte-identical), pale blue when the wall is warm; never blue on a blue / teal wall.
  - Entry / hallway settings are filed under Living room (no Entryway folder exists).
  - No kie.ai credits are spent here; the planner only plans.

Briefs live in the listing record under production.set_plan (never inside production.slots, which run_slot replaces).
`python -m app.slot_planner --idea 3 --dry-run` plans Book Club Cat and prints the briefs and the check; it writes
nothing (the DB is opened read-only).
"""
import hashlib
import json
import math
import re
import threading
from datetime import datetime
from pathlib import Path

from . import room_slots as rs

# HOOK (Tony 2026-11-19): orientation becomes a pre-production setting later. Today every frame is portrait; nothing
# reads another value, and no landscape sizes, ratios or prompts exist anywhere in the planner.
ORIENTATION = "portrait"

VERSION = 1
DEFAULTS = {"planner_model": "sonnet", "planner_fallback_model": "haiku", "planner_timeout_s": 300,
            "planner_rounds": 3, "planner_max_tight": 2, "planner_auto": False}

# ---------- sizes (Tony's listing chart, Listing_Templates/Description_Template_AI.md) ----------
# ratio -> scale -> sizes (portrait: width x height in inches; ISO by name). Every design has all five ratio files;
# the render always uses that ratio's print file (5x7 -> the ISO file, 0.714 vs 0.707).
SIZE_CHART = {
    "2x3": {"small": ["4x6", "6x9", "8x12"], "medium": ["10x15", "12x18", "16x24"], "large": ["20x30", "24x36"]},
    "3x4": {"small": ["6x8", "9x12"], "medium": ["12x16", "15x20"], "large": ["18x24", "24x32"]},
    "4x5": {"small": ["4x5", "8x10"], "medium": ["12x15", "16x20"], "large": ["20x25", "24x30"]},
    "iso": {"small": ["5x7", "A6", "A5", "A4"], "medium": ["A3"], "large": ["A2", "A1"]},
    "11x14": {"small": [], "medium": ["11x14"], "large": ["22x28"]}}
ISO_IN = {"A6": (4.1, 5.8), "A5": (5.8, 8.3), "A4": (8.3, 11.7), "A3": (11.7, 16.5), "A2": (16.5, 23.4),
          "A1": (23.4, 33.1)}
SCALES = ("small", "medium", "large")
SIZE_INDEX = {size: (ratio, scale) for ratio, d in SIZE_CHART.items() for scale, sizes in d.items() for size in sizes}


def size_in(size):
    """(width, height) in inches of a chart size (portrait)."""
    if size in ISO_IN:
        return ISO_IN[size]
    w, h = (float(x) for x in size.split("x"))
    return (min(w, h), max(w, h))


# ---------- shots ----------
SHOTS = {"tight": {"scale": "small", "frac": (45, 65)}, "medium": {"scale": "medium", "frac": (30, 50)},
         "wide": {"scale": "large", "frac": (18, 35)}}
SHOT_OK = {"small": ("tight", "medium"), "medium": ("medium", "wide"), "large": ("wide",)}   # one step wider, never tighter
SHOT_ORDER = ("tight", "medium", "wide")

# ---------- settings (where the piece lives inside the filed room) ----------
# name -> (phrase, displays allowed, scales allowed)
_S = "standing_on_surface"
_L = "lean_on_surface"
_HF = "hung_over_furniture"
_HB = "hung_bare_wall"
_F = "floor_lean"
_SL = "shelf_ledge"
SETTINGS = {
    "over_sofa": ("the wall above a sofa", (_HF,), ("medium", "large")),
    "sideboard_top": ("the top of a low sideboard", (_L, _S, _HF), ("small", "medium")),
    "coffee_table": ("a low coffee table", (_S,), ("small",)),
    "bookshelf": ("a shelf of a bookcase", (_SL, _S), ("small",)),
    "mantel": ("a fireplace mantel", (_L, _HF), ("small", "medium", "large")),
    "console_behind_sofa": ("a slim console table behind a sofa", (_L, _S), ("small", "medium")),
    "side_table": ("a small side table beside an armchair", (_S,), ("small",)),
    "floor_beside_chair": ("the floor beside an armchair", (_F,), ("medium", "large")),
    "entry_console": ("an entry console table in a hallway", (_L, _S, _HF), ("small", "medium")),
    "hallway_wall": ("a calm hallway wall", (_HB,), ("medium", "large")),
    "over_bed": ("the wall above a bed headboard", (_HF,), ("medium", "large")),
    "nightstand": ("a bedside nightstand", (_S, _L), ("small",)),
    "dresser_top": ("the top of a dresser", (_L, _S, _HF), ("small", "medium")),
    "floor_beside_bed": ("the floor beside a bed", (_F,), ("medium", "large")),
    "reading_corner": ("the wall of a reading corner beside an armchair", (_HB, _HF), ("medium", "large")),
    "desk_top": ("the top of a desk", (_S, _L), ("small",)),
    "over_desk": ("the wall above a desk", (_HF,), ("medium", "large")),
    "shelf": ("a wall shelf", (_SL, _S), ("small",)),
    "credenza_top": ("the top of a low credenza", (_L, _HF), ("small", "medium", "large")),
    "floor_lean": ("the floor against the wall", (_F,), ("medium", "large")),
    "open_shelf": ("an open kitchen shelf", (_SL, _S), ("small",)),
    "counter": ("a kitchen counter against the backsplash wall", (_L, _S), ("small", "medium")),
    "over_dining_table": ("the wall above a dining table", (_HF,), ("medium", "large")),
    "sideboard": ("a dining-room sideboard", (_L, _HF), ("small", "medium", "large")),
    "bar_cart": ("the top of a bar cart", (_S,), ("small",)),
    "over_bath": ("the wall above a freestanding bathtub", (_HF,), ("medium", "large")),
    "over_vanity": ("the wall beside a bathroom vanity", (_HB, _HF), ("small", "medium")),
    "bath_ledge": ("a bathtub ledge", (_S, _L), ("small",)),
    "small_shelf": ("a small bathroom shelf", (_SL, _S), ("small",)),
    "wallpaper_wall": ("a bathroom wall with a quiet wallpaper", (_HB,), ("medium",)),
    "over_crib": ("the wall above a crib", (_HF,), ("medium",)),
    "over_kids_bed": ("the wall above a child's bed", (_HF,), ("medium", "large")),
    "toy_shelf": ("a low toy shelf", (_SL, _S, _L), ("small",)),
    "picture_ledge": ("a picture ledge on the wall", (_SL,), ("small", "medium")),
    "media_console": ("a low media console", (_L, _HF), ("medium", "large")),
    "work_table": ("a studio work table", (_L, _S), ("small", "medium")),
    "studio_wall": ("a studio wall", (_HB,), ("medium", "large")),
}
_LIVING = ["over_sofa", "sideboard_top", "coffee_table", "bookshelf", "mantel", "console_behind_sofa", "side_table",
           "floor_beside_chair", "entry_console", "hallway_wall"]       # entry / hallway: filed under Living room
ROOM_SETTINGS = {
    "Living room": _LIVING, "Entryway": _LIVING,
    "Bedroom": ["over_bed", "nightstand", "dresser_top", "floor_beside_bed", "reading_corner"],
    "Dorm": ["over_bed", "nightstand", "dresser_top", "desk_top", "shelf"],
    "Office": ["desk_top", "over_desk", "shelf", "credenza_top", "floor_lean"],
    "Kitchen & dining": ["open_shelf", "counter", "over_dining_table", "sideboard", "bar_cart"],
    "Bathroom": ["over_bath", "over_vanity", "bath_ledge", "small_shelf", "wallpaper_wall"],
    "Kids": ["over_kids_bed", "dresser_top", "toy_shelf", "picture_ledge"],
    "Nursery": ["over_crib", "dresser_top", "toy_shelf", "picture_ledge"],
    "Game room": ["over_sofa", "media_console", "shelf"],
    "Creative space": ["work_table", "picture_ledge", "studio_wall"],
    "Laundry": ["shelf", "counter"]}
DISPLAYS = (_HF, _HB, _F, _L, _S, _SL)
SURFACE_DISPLAYS = (_L, _S, _SL)
HUNG = (_HF, _HB)

# ---------- camera, light, presentation ----------
PRESENTATIONS = ("frame", "mat", "canvas", "canvas_bare")
FRAME_L = {"black_frame": 15, "walnut_frame": 35, "gold_frame": 60, "oak_frame": 65, "white_frame": 95,
           "natural_wood_floater": 65}
FRAME_FOR = {"frame": ("oak_frame", "walnut_frame", "black_frame", "white_frame", "gold_frame"),
             "mat": ("oak_frame", "walnut_frame", "black_frame", "white_frame", "gold_frame"),
             "canvas": ("natural_wood_floater",), "canvas_bare": ("none",)}
CAMERA_SIDES = ("left", "right", "front")
CAMERA_HEIGHTS = ("surface", "low", "seated", "counter", "eye")
LENSES = tuple(rs.LOOK_AXES["lens"])
LIGHT_STYLES = tuple(rs.LOOK_AXES["light_style"])
LIGHT_FROM = ("left", "right", "front", "behind_camera")
SHADOWS = ("soft", "hard")
DOFS = tuple(rs.LOOK_AXES["depth_of_field"])
WALL_TREATMENTS = ("plain_paint", "limewash", "plaster", "panelled", "wainscot_lower", "shiplap", "brick", "wallpaper",
                   "tile", "concrete", "wood_slat")
HOUSES = ("london_flat", "nyc_loft", "paris_apartment", "english_cottage", "scandinavian_house", "coastal_cottage",
          "southwestern_adobe", "midcentury_ranch", "japanese_home", "brownstone", "suburban_colonial",
          "modern_farmhouse")
BUYERS = ("big_wall_decorator", "small_space_renter", "gift_buyer", "desk_or_bookshelf_person", "parent", "cat_lover",
          "reader", "first_home_buyer")
FURNITURE_STYLES = ("japandi_low_wood", "midcentury_teak", "scandi_light_oak", "parisian_vintage", "rustic_farmhouse",
                    "modern_minimal", "boho_rattan", "industrial_metal", "classic_traditional", "coastal_painted",
                    "kids_painted", "eclectic_mix")
FURNITURE_FAMILIES = ("light_wood", "mid_wood", "dark_wood", "painted_white", "painted_colour", "black", "metal",
                      "rattan_cane", "upholstered_colour", "upholstered_neutral")
WALL_FAMILIES = ("white_cream", "greige_beige", "grey", "charcoal_black", "blush_pink", "warm_brown_red", "warm_earth",
                 "mustard_yellow", "olive_green", "sage_green", "forest_green", "teal_blue", "dusty_blue", "navy",
                 "plum_purple")
WARM_FAMILIES = ("blush_pink", "warm_brown_red", "warm_earth", "mustard_yellow")
BLUE_FAMILIES = ("teal_blue", "dusty_blue", "navy")

CAMERA_SIDE_TEXT = {
    "left": "Camera: from slightly left of the frame, about 10 to 15 degrees off square, the wall receding gently to "
            "the right, verticals straight.",
    "right": "Camera: from slightly right of the frame, about 10 to 15 degrees off square, the wall receding gently "
             "to the left, verticals straight.",
    "front": "Camera: square-on to the frame, the frame level and parallel to the picture edges, verticals straight."}
CAMERA_HEIGHT_TEXT = {
    "surface": "Camera height: level with the surface the piece stands on, looking straight at the art.",
    **{k: rs.LOOK_AXES["camera_height"][k][1] for k in ("low", "seated", "counter", "eye")}}
LIGHT_FROM_TEXT = {"left": "The daylight comes from a window to the left of the frame.",
                   "right": "The daylight comes from a window to the right of the frame.",
                   "front": "The daylight comes from a window facing the art wall.",
                   "behind_camera": "The daylight comes from a window behind the camera."}
SHADOW_TEXT = {"soft": "Shadows are soft-edged and clearly visible.",
               "hard": "Shadows are crisp-edged and clearly visible."}
DISPLAY_TEXT = {
    _HF: "Display: the piece hangs centred on {where}, with clear wall on every side of the frame.",
    _HB: "Display: the piece hangs alone on {where}, with generous space around it.",
    _F: "Display: the piece stands on the floor leaning against the wall, tilted back only slightly, its bottom edge "
        "resting on the floor and its face upright and flat.",
    _L: "Display: the piece rests on {where}, leaning against the wall behind it, tilted back only slightly, its face "
        "upright and flat.",
    _S: "Display: the piece stands upright on {where} on a slim easel back, tilted back at most 10 degrees, its face "
        "flat.",
    _SL: "Display: the piece stands on {where}, leaning against the wall behind it, its face upright and flat."}
WALL_TREATMENT_TEXT = {
    "plain_paint": "The wall is smooth painted plaster.", "limewash": "The wall has a soft limewash plaster texture.",
    "plaster": "The wall is hand-finished plaster with a gentle, even texture.",
    "panelled": "The wall has tall painted panelling in the wall colour; the artwork is centred inside one larger "
                "panel, with clear wall on every side of the frame.",
    "wainscot_lower": "The wall has painted wainscoting below waist height only, fully below the frame.",
    "shiplap": "The wall is painted vertical shiplap boards in the wall colour.",
    "brick": "The wall is painted brick in the wall colour, with a fine, even texture.",
    "wallpaper": "The wall has a quiet small-pattern wallpaper in soft tones close to the wall colour.",
    "tile": "The wall is laid with plain matte tiles in the wall colour.",
    "concrete": "The wall is smooth raw concrete.", "wood_slat": "The wall is clad in fine vertical wood slats."}

# ---------- the insert marker (Tony 2026-11-19) ----------
MARKERS = ("orange", "blue")
MARKER_RGB = {"orange": (250, 215, 170), "blue": (160, 200, 240)}
MARKER_WORDS = {"orange": rs.INSERT_COLOUR,
                "blue": "pale sky blue (a soft powder blue, roughly RGB 160, 200, 240)"}

PLAN_GUARD_FRAME = ("The whole frame sits inside the picture with clear space on all four sides of the frame; nothing "
                    "in front of it overlaps any part of the frame. The artwork face is flat, upright and in sharp "
                    "focus, and the frame stands out clearly in tone from what is behind it. ")
CLOSING = ("Only one piece of art; no other frames, posters or mirrors. No people, no faces, no hands, no pets. Nothing "
           "in the picture carries readable text: no labels, logos, signs, lettering or book titles; books have plain "
           "covers or face away. No lamps unless the setting clearly needs one.")
BANNED = re.compile(r"\b(person|people|woman|women|man|men|hands?|faces?|cats?|kittens?|dogs?|pets?|labels?|signs?|"
                    r"logos?|lettering|titles?|posters?|mirrors?|gallery wall|second frame|neon sign|why|because|"
                    r"perfect for)\b", re.I)
WORDS_MIN, WORDS_MAX = 60, 160


# ---------- colour ----------

def lab_of_hex(hx):
    """CIELAB (D65) of '#RRGGBB'. Raises ValueError on a bad hex."""
    m = re.fullmatch(r"#?([0-9a-fA-F]{6})", str(hx or "").strip())
    if not m:
        raise ValueError(f"bad colour hex {hx!r}")
    return lab_of_rgb([int(m.group(1)[i:i + 2], 16) for i in (0, 2, 4)])


def lab_of_rgb(rgb):
    def lin(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(float(c)) for c in rgb)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 216 / 24389 else (24389 / 27 * t + 16) / 116   # noqa: E731
    fx, fy, fz = f(x), f(y), f(z)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def lch(lab):
    L, a, b = lab
    return L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360


def de2000(lab1, lab2):
    """CIEDE2000 colour difference."""
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2
    C1, C2 = math.hypot(a1, b1), math.hypot(a2, b2)
    Cb = (C1 + C2) / 2
    G = 0.5 * (1 - math.sqrt(Cb ** 7 / (Cb ** 7 + 25 ** 7)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360
    h2p = math.degrees(math.atan2(b2, a2p)) % 360
    dLp, dCp = L2 - L1, C2p - C1p
    dh = 0.0 if C1p * C2p == 0 else (h2p - h1p if abs(h2p - h1p) <= 180 else
                                      h2p - h1p - 360 if h2p - h1p > 180 else h2p - h1p + 360)
    dHp = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dh / 2))
    Lbp, Cbp = (L1 + L2) / 2, (C1p + C2p) / 2
    if C1p * C2p == 0:
        hbp = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        hbp = (h1p + h2p) / 2
    else:
        hbp = (h1p + h2p + 360) / 2 if h1p + h2p < 360 else (h1p + h2p - 360) / 2
    T = (1 - 0.17 * math.cos(math.radians(hbp - 30)) + 0.24 * math.cos(math.radians(2 * hbp))
         + 0.32 * math.cos(math.radians(3 * hbp + 6)) - 0.20 * math.cos(math.radians(4 * hbp - 63)))
    dth = 30 * math.exp(-(((hbp - 275) / 25) ** 2))
    Rc = 2 * math.sqrt(Cbp ** 7 / (Cbp ** 7 + 25 ** 7))
    Sl = 1 + 0.015 * (Lbp - 50) ** 2 / math.sqrt(20 + (Lbp - 50) ** 2)
    Sc, Sh = 1 + 0.045 * Cbp, 1 + 0.015 * Cbp * T
    Rt = -math.sin(math.radians(2 * dth)) * Rc
    return math.sqrt((dLp / Sl) ** 2 + (dCp / Sc) ** 2 + (dHp / Sh) ** 2 + Rt * (dCp / Sc) * (dHp / Sh))


def wall_family(lab):
    """The wall's colour family, from its CIELAB (deterministic; the model's own family word is not trusted)."""
    L, C, h = lch(lab)
    if C < 12:
        if L >= 82:
            return "white_cream"
        if L < 35:
            return "charcoal_black"
        return "greige_beige" if lab[2] > 3 and L >= 55 else "grey"
    if h < 20 or h >= 345 or (h < 32 and C < 30 and L > 60):      # pinks, incl. pale dusty blush
        return "blush_pink" if L > 60 else "warm_brown_red"
    if h < 55:
        return "warm_brown_red" if L < 50 else "warm_earth"
    if h < 80:
        return "warm_earth"
    if h < 105:
        return "mustard_yellow" if C >= 35 else "warm_earth"
    if h < 120:
        return "olive_green"
    if h < 180:
        return "sage_green" if L > 55 else "forest_green"
    if h < 230:
        return "teal_blue"
    if h < 290:
        return "dusty_blue" if L > 50 else "navy"
    return "blush_pink" if L > 70 else "plum_purple"


def is_loud(lab):
    L, C, _ = lch(lab)
    return C > 35 or L < 35


def marker_for_wall(hx):
    """The insert marker for a wall: blue opposite a warm wall (terracotta, adobe, peach, sand, tan, mustard, warm
    brown / red, warm pink: WARM_FAMILIES), orange otherwise (default, today's path: whites, creams, greiges, greys,
    greens, blues, plums). A colour-difference test is not used: dE2000 puts every pale white within ~15 of the pale
    orange insert, and white walls with the orange insert are what all live templates are."""
    return "blue" if wall_family(lab_of_hex(hx)) in WARM_FAMILIES else "orange"


# ---------- normalise + lint one brief ----------

KEEP = ("slot", "source", "library_rel", "print_size", "shot", "setting", "display", "presentation", "frame_finish",
        "camera_side", "camera_height", "lens", "light_style", "light_from", "shadow", "depth_of_field", "wall", "floor",
        "furniture", "house", "buyer", "props", "scene")      # no "marker" (code picks it) and no rationale field


def normalise(raw, slot_ctx):
    """A model brief -> a clean brief: unknown keys dropped (no rationale field survives), room / decor from the slot
    plan, ratio + scale from the print size, wall family + marker from the wall hex. Never raises."""
    b = {k: raw.get(k) for k in KEEP if k in raw}
    b["slot"] = int(slot_ctx["slot"])
    b["room"], b["decor"] = slot_ctx["room"], slot_ctx["decor"]
    b["source"] = "library" if b.get("source") == "library" and b.get("library_rel") else "new"
    if b["source"] != "library":
        b["library_rel"] = None
    size = str(b.get("print_size") or "").strip().replace(" ", "")
    size = size.upper() if re.fullmatch(r"[aA]\d", size) else size.lower()
    b["print_size"] = size
    b["ratio"], b["scale"] = SIZE_INDEX.get(size, (None, None))
    w = dict(b.get("wall") or {}) if isinstance(b.get("wall"), dict) else {}
    w = {k: w.get(k) for k in ("name", "hex", "treatment")}
    try:
        lab = lab_of_hex(w.get("hex"))
        w["hex"] = "#" + re.sub(r"[^0-9a-fA-F]", "", w["hex"]).upper()
        w["family"] = wall_family(lab)
        w["lab"] = [round(v, 1) for v in lab]
        b["marker"] = marker_for_wall(w["hex"])          # opposite the wall, never the model's choice
    except ValueError:
        w["family"] = None
    b["wall"] = w
    f = b.get("furniture") if isinstance(b.get("furniture"), dict) else {}
    b["furniture"] = {k: f.get(k) for k in ("style", "colour", "family")}
    b["props"] = [str(p)[:80] for p in (b.get("props") or []) if str(p).strip()][:8]
    b["scene"] = " ".join(str(b.get("scene") or "").split())
    if b.get("presentation") == "canvas":
        b["frame_finish"] = "natural_wood_floater"
    elif b.get("presentation") == "canvas_bare":
        b["frame_finish"] = "none"
    b.setdefault("marker", "orange")
    return b


def lint(b, slot_ctx=None, settings=None):
    """Hard per-brief rules (plan 7.1 + Tony 2026-11-19). {"pass", "why": [plain reasons]}. A failing brief can not
    be generated."""
    why = []
    ctx = slot_ctx or {}

    def need(key, allowed, label=None):
        if b.get(key) not in allowed:
            why.append(f"{label or key} {b.get(key)!r} is not one of {', '.join(map(str, allowed))}")
            return False
        return True
    if b.get("source") == "library":
        return {"pass": bool(b.get("library_rel")), "why": [] if b.get("library_rel") else ["library brief without a template"]}
    if not b.get("ratio"):
        why.append(f"print size {b.get('print_size')!r} is not in the size chart")
    elif ctx.get("ratios") is not None and b["ratio"] not in ctx["ratios"]:
        why.append(f"{b['ratio']} has no {b.get('room')} folder in Room_Templates (have {', '.join(ctx['ratios'])})")
    room_settings = ROOM_SETTINGS.get(b.get("room"), list(SETTINGS))
    if need("setting", room_settings, f"setting for {b.get('room')}"):
        phrase, displays, scales = SETTINGS[b["setting"]]
        need("display", displays, f"display on {b['setting']}")
        if b.get("scale") and b["scale"] not in scales:
            why.append(f"a {b['scale']} print does not fit {b['setting']} (only {', '.join(scales)})")
    need("shot", SHOT_ORDER)
    if b.get("scale") and b.get("shot") in SHOT_ORDER and b["shot"] not in SHOT_OK[b["scale"]]:
        why.append(f"a {b['print_size']} ({b['scale']}) print is never shown as a {b['shot']} shot "
                   f"(allowed: {', '.join(SHOT_OK[b['scale']])})")
    if need("presentation", PRESENTATIONS):
        if b["presentation"] in ("canvas", "canvas_bare") and b.get("scale") == "small":
            why.append("canvas only for medium and large prints; small prints get a frame or a mat")
        need("frame_finish", FRAME_FOR[b["presentation"]], f"frame finish for {b['presentation']}")
    for key, allowed in (("camera_side", CAMERA_SIDES), ("camera_height", CAMERA_HEIGHTS), ("lens", LENSES),
                         ("light_style", LIGHT_STYLES), ("light_from", LIGHT_FROM), ("shadow", SHADOWS),
                         ("depth_of_field", DOFS), ("house", HOUSES), ("buyer", BUYERS), ("marker", MARKERS)):
        need(key, allowed)
    fu = b.get("furniture") or {}
    if fu.get("style") not in FURNITURE_STYLES:
        why.append(f"furniture style {fu.get('style')!r} is not one of the listed styles")
    if fu.get("family") not in FURNITURE_FAMILIES:
        why.append(f"furniture colour family {fu.get('family')!r} is not one of the listed families")
    disp, shot, height = b.get("display"), b.get("shot"), b.get("camera_height")
    if height == "low" and disp in HUNG and shot == "tight":
        why.append("a low camera close under hung art keystones the opening")
    if b.get("lens") == "lens_wide" and shot == "tight":
        why.append("a wide lens up close bends the frame")
    if b.get("lens") == "lens_short_tele" and shot == "wide":
        why.append("an 85 mm lens does not fit a wide room view")
    if height == "surface" and disp not in SURFACE_DISPLAYS:
        why.append("surface camera height only when the piece stands on a surface")
    if height == "counter" and disp not in SURFACE_DISPLAYS + (_HF,):
        why.append("counter camera height only with the piece on or over furniture")
    props = b.get("props") or []
    if shot == "tight" and not 1 <= len(props) <= 3:
        why.append(f"a tight shot has 1 to 3 small props ({len(props)} given)")
    if len(props) > 5:
        why.append(f"at most 5 props ({len(props)} given)")
    w = b.get("wall") or {}
    if not w.get("family"):
        why.append(f"wall colour {w.get('hex')!r} is not a #RRGGBB hex")
    else:
        lab = w["lab"]
        want = marker_for_wall(w["hex"])
        if b.get("marker") == "blue" and w["family"] in BLUE_FAMILIES:
            why.append(f"a blue insert marker on a {w['family'].replace('_', ' ')} wall: the marker must be opposite "
                       "the wall")
        elif b.get("marker") != want:
            why.append(f"the {w['family'].replace('_', ' ')} wall needs the {want} insert marker, not {b.get('marker')}")
        fin = b.get("frame_finish")
        if fin in FRAME_L and abs(FRAME_L[fin] - lab[0]) < 15:
            why.append(f"the {fin.replace('_', ' ')} does not stand out from the wall in tone (wall L* {lab[0]:.0f})")
        if w["family"] == "blush_pink" and b.get("presentation") in ("frame", "mat") and \
                fin not in ("black_frame", "walnut_frame"):
            why.append("blush walls only with a black or walnut frame")
        if w.get("treatment") not in WALL_TREATMENTS:
            why.append(f"wall treatment {w.get('treatment')!r} is not one of the listed treatments")
        text = (b.get("scene") or "").lower()
        if w.get("treatment") == "panelled" and (disp not in HUNG or not re.search(r"cent(re|er)d? inside one "
                                                                                    r"(larger )?panel", text)):
            why.append("panelling only behind hung art, with the art centred inside one larger panel (say so)")
        if w.get("treatment") == "wainscot_lower" and "below waist height" not in text:
            why.append("wainscoting only below waist height (say so in the scene)")
    scene = b.get("scene") or ""
    n = len(scene.split())
    if not WORDS_MIN <= n <= WORDS_MAX:
        why.append(f"the scene text has {n} words (60 to 160)")
    for txt, label in ((scene, "scene"), (" ".join(props), "props"), (str(b.get("floor") or ""), "floor")):
        hit = sorted({m.group(0).lower() for m in BANNED.finditer(txt)})
        if hit:
            why.append(f"the {label} names {', '.join(hit)} (no people, pets, readable text, other frames or reasons)")
    low = scene.lower()
    for side in ("left", "right"):
        if re.search(rf"\bfrom the {side}\b", low) and b.get("light_from") != side and b.get("camera_side") != side:
            why.append(f"the scene says 'from the {side}' but neither the light nor the camera is on the {side}")
    return {"pass": not why, "why": why}


# ---------- the prompt actually sent (code, not the model) ----------

def print_area_text(marker="orange"):
    """rs._PRINT_AREA for the orange marker (unchanged, byte-identical); the same sentences in blue otherwise."""
    if marker == "orange":
        return rs._PRINT_AREA
    return rs._PRINT_AREA.replace(rs.INSERT_COLOUR, MARKER_WORDS[marker]).replace("orange", marker)


def _present_text_v3(b):
    """The presentation sentences for a brief: the v2 sentences (room_slots._present_text_v2, not edited) fed with a
    look built from the brief, then the standing-on-a-surface sentence and the marker colour."""
    kind = b["presentation"]
    lean = b.get("display") in SURFACE_DISPLAYS + (_F,)
    look = {"display": "lean_on_furniture" if lean else "hung_over_furniture",
            "frame_finish": b.get("frame_finish") if b.get("frame_finish") in rs.LOOK_AXES["frame_finish"] else None,
            "camera_angle": "straight_on" if b.get("camera_side") == "front" else "slight_left"}
    w = b.get("wall") or {}
    if w.get("lab") and w["lab"][0] > 75 and w.get("family") in ("white_cream", "greige_beige", "blush_pink"):
        look["wall_palette"] = "ivory_cream"          # pale warm wall: the floater wood is named darker (v2 rule)
    t = rs._present_text_v2(kind, look)
    if b.get("display") == _S:
        t += " It stands upright on a slim easel back, tilted back at most 10 degrees."
    if b.get("marker", "orange") != "orange":
        t = t.replace("orange", b["marker"])
    return t


def _outer(b):
    """Outer size in inches (w, h) of the whole piece: print + mat border + frame moulding (or the floater)."""
    w, h = size_in(b["print_size"])
    mat = {"small": 1.5, "medium": 2.0, "large": 3.0}.get(b.get("scale"), 2.0) if b.get("presentation") == "mat" else 0
    rim = {"frame": 0.75, "mat": 0.75, "canvas": 1.0, "canvas_bare": 0.0}.get(b.get("presentation"), 0.75)
    return w + 2 * (mat + rim), h + 2 * (mat + rim)


def _fmt(x):
    return f"{x:.1f}".rstrip("0").rstrip(".")


def hung_where(phrase):
    """'the wall above a sofa' stays; 'the top of a low credenza' / 'a fireplace mantel' -> 'the wall above ...'."""
    if phrase.startswith("the wall"):
        return phrase
    return "the wall above " + re.sub(r"^the (top|wall) of ", "", phrase)


def shot_text(b):
    w, h = size_in(b["print_size"])
    ow, oh = _outer(b)
    lo, hi = SHOTS[b["shot"]]["frac"]
    t = (f"Framing: a {b['shot']} shot. The piece is a {b['scale']} {b['print_size']} print ({_fmt(w)} x {_fmt(h)} in, "
         f"{_fmt(w * 2.54)} x {_fmt(h * 2.54)} cm); as shown, the whole piece measures about {_fmt(ow)} x {_fmt(oh)} in "
         f"({_fmt(ow * 2.54)} x {_fmt(oh * 2.54)} cm) and fills about {lo} to {hi}% of the picture height.")
    if b["shot"] == "tight":
        t += (f" Everything around it is at true everyday scale: an ordinary coffee cup beside it would stand about "
              f"{round(100 * 3.8 / oh)}% as tall as the piece.")
    elif b["shot"] == "medium":
        t += " The furniture is at true everyday scale: a sideboard, desk or dresser top is about 75 cm from the floor."
    else:
        t += " The room is at true everyday scale: a sofa back is about 85 cm high and a door about 200 cm."
    return t


def assemble(b):
    """The full prompt for a NEW brief: the planner's scene + fixed blocks (portrait frame in a 4:3 photograph, shot
    and scale, camera, light, wall, the marker print area + presentation, guards). Deterministic."""
    phrase = SETTINGS[b["setting"]][0]
    parts = [
        "Photorealistic interior photograph in a 4:3 landscape picture format, showing one portrait (vertical) piece "
        "of wall art as the clear subject.",
        b["scene"],
        shot_text(b),
        DISPLAY_TEXT[b["display"]].format(where=hung_where(phrase) if b["display"] == _HF else phrase),
        CAMERA_SIDE_TEXT[b["camera_side"]], CAMERA_HEIGHT_TEXT[b["camera_height"]],
        rs.LOOK_AXES["lens"][b["lens"]][1], rs.LOOK_AXES["depth_of_field"][b["depth_of_field"]][1],
        rs.LOOK_AXES["light_style"][b["light_style"]][1], LIGHT_FROM_TEXT[b["light_from"]], SHADOW_TEXT[b["shadow"]],
        "Every scene shows visible shadows.",
        f"Walls: {b['wall']['name'] or 'a calm wall colour'}. "
        + WALL_TREATMENT_TEXT[b["wall"]["treatment"]],
    ]
    t = " ".join(p.strip() for p in parts if p) + " "
    if b["wall"]["treatment"] in ("panelled", "wainscot_lower"):
        t += rs.WAINSCOT_RULE + " "
    t += print_area_text(b.get("marker", "orange")) + _present_text_v3(b) + " "
    t += rs.LOOK_GUARD + PLAN_GUARD_FRAME + CLOSING
    return t


# ---------- the set check ----------

SIM_W = {"setting": 2, "shot": 2, "camera_side": 1.5, "wall_family": 1.5, "display": 1, "presentation": 1,
         "furniture": 1, "house": 1, "light_style": 1, "wall_treatment": 1, "camera_height": 0.5, "lens": 0.5,
         "depth_of_field": 0.5}
SIM_MAX = 0.6
JACCARD_MAX = 0.5
STOP = set("with that this from into onto over under their there where which while about around behind beside "
           "between above below very only just some soft warm light room wall walls piece frame print a an the and "
           "of in on to is its it at as by".split())


def descriptor(b):
    """The flat facts check_set compares (None = unknown, never counted as equal)."""
    w, f = b.get("wall") or {}, b.get("furniture") or {}
    lab = w.get("lab")
    return {"slot": b.get("slot"), "scale": b.get("scale"), "ratio": b.get("ratio"), "print_size": b.get("print_size"),
            "shot": b.get("shot"), "setting": b.get("setting"), "display": b.get("display"),
            "presentation": b.get("presentation"), "camera_side": b.get("camera_side"),
            "camera_height": b.get("camera_height"), "lens": b.get("lens"), "light_style": b.get("light_style"),
            "light_from": b.get("light_from"), "shadow": b.get("shadow"), "depth_of_field": b.get("depth_of_field"),
            "wall_family": w.get("family"), "wall_treatment": w.get("treatment"),
            "wall_loud": is_loud(lab) if lab else None,
            "furniture": f"{f.get('style')}|{f.get('colour') or '-'}" if f.get("style") else None,
            "furniture_family": f.get("family"), "house": b.get("house"), "buyer": b.get("buyer"),
            "scene": b.get("scene") or ""}


def _tokens(t):
    return {w for w in re.findall(r"[a-z]{4,}", (t or "").lower()) if w not in STOP}


def similarity(a, b):
    tot = sum(SIM_W.values())
    s = sum(w for k, w in SIM_W.items() if a.get(k) is not None and a.get(k) == b.get(k))
    return s / tot


def _split(n, weights):
    """Largest-remainder split of n over buckets by weight. {bucket: count}."""
    tot = sum(weights.values())
    if tot <= 0:
        return {k: 0 for k in weights}
    raw = {k: n * v / tot for k, v in weights.items()}
    out = {k: int(v) for k, v in raw.items()}
    for k in sorted(weights, key=lambda k: -(raw[k] - out[k]))[:n - sum(out.values())]:
        out[k] += 1
    return out


def check_set(briefs, fixed, order=None, ratio_avail=None, max_tight=None):
    """Balance + similarity over the whole listing (plan 7.2). briefs = {slot: brief} (open slots), fixed = {slot:
    descriptor} (approved / pending images: counted, never blamed). ratio_avail = {slot: [ratios with a folder]}.
    Returns {"pass", "failures": [{"rule", "text", "slots"}], "blame": {slot: points}, "scores": {...}}."""
    opens = {int(s): descriptor(b) for s, b in briefs.items()}
    fix = {int(s): dict(d) for s, d in (fixed or {}).items()}
    allv = {**fix, **opens}
    order = [int(s) for s in (order or sorted(allv))]
    n, m = len(allv), len(opens)
    fails, blame = [], {s: 0.0 for s in opens}

    def fail(rule, text, slots, pts=1.0):
        slots = [s for s in slots if s in opens]
        if not slots:
            return
        fails.append({"rule": rule, "text": text, "slots": sorted(slots)})
        for s in slots:
            blame[s] += pts

    def count(key, pool=None):
        c = {}
        for s, d in (pool or allv).items():
            if d.get(key) is not None:
                c.setdefault(d[key], []).append(s)
        return c
    # scale mix: fill the deficit of thirds
    if m:
        tgt = _split(n, {k: 1 for k in SCALES})
        fx = {k: sum(1 for d in fix.values() if d.get("scale") == k) for k in SCALES}
        deficit = {k: max(0, tgt[k] - fx[k]) for k in SCALES}
        if sum(deficit.values()) >= m:
            want = _split(m, deficit)
        else:
            extra = _split(m - sum(deficit.values()), {k: 1 for k in SCALES})
            want = {k: deficit[k] + extra[k] for k in SCALES}
        got = {k: [s for s, d in opens.items() if d["scale"] == k] for k in SCALES}
        heavy = [s for x in SCALES if len(got[x]) > want[x] for s in got[x]]
        for k in SCALES:
            if abs(len(got[k]) - want[k]) > 1:
                over = len(got[k]) > want[k]
                fail("scale", f"{len(got[k])} open slots are {k} prints; the set needs about {want[k]} "
                              f"(target {', '.join(f'{x} {want[x]}' for x in SCALES)})",
                     got[k] if over else (heavy or list(opens)), 1.0)
    # ratio mix
    rc = count("ratio")
    for s, d in opens.items():
        r = d["ratio"]
        if r and len(fix) and sum(1 for x in fix.values() if x.get("ratio") == r) >= 0.4 * n:
            fail("ratio", f"slot {s} adds another {r} to a set that is already {r} for 40% or more", [s])
    for r in rs.RATIOS:
        if r in rc:
            continue
        could = [s for s, d in opens.items() if r in ((ratio_avail or {}).get(s) or rs.RATIOS)
                 and len(rc.get(d["ratio"], [])) >= 2]
        if could:
            fail("ratio", f"no {r} print in the set while open slots could show one", could, 0.5)
    # sizes
    known = [d["print_size"] for d in allv.values() if d.get("print_size")]
    sizes_open = [d["print_size"] for d in opens.values() if d.get("print_size")]
    for sz in {x for x in sizes_open if sizes_open.count(x) > 1}:
        fail("sizes", f"print size {sz} is used twice", [s for s, d in opens.items() if d["print_size"] == sz][1:])
    if len(set(known)) < min(6, len(known)):
        fail("sizes", f"only {len(set(known))} different print sizes", list(opens), 0.5)
    # camera side
    cs = count("camera_side")
    nk = sum(len(v) for v in cs.values())
    for side, ss in cs.items():
        if nk >= 4 and len(ss) > 0.5 * nk:
            fail("camera", f"{len(ss)} of {nk} slots are shot from the {side}", ss, 0.7)
    if n >= 6:
        for side in ("left", "right"):
            if side not in cs:
                fail("camera", f"no slot is shot from the {side}", list(opens), 0.4)
    seq = [s for s in order if s in allv]
    for a, b in zip(seq, seq[1:]):
        da, db = allv[a], allv[b]
        if da.get("camera_side") and da.get("camera_side") == db.get("camera_side") and da.get("shot") and \
                da.get("shot") == db.get("shot"):
            fail("neighbours", f"slots {a} and {b} sit next to each other with the same camera side and shot",
                 [b] if b in opens else [a])
    # light
    ls = count("light_style")
    nl = sum(len(v) for v in ls.values())
    for k, ss in ls.items():
        if nl >= 4 and len(ss) > 0.4 * nl:
            fail("light", f"{len(ss)} of {nl} slots use {k.replace('_', ' ')} light", ss, 0.7)
    lf = {k for k in count("light_from") if k in ("left", "right")}
    if sum(len(v) for v in count("light_from").values()) >= 4 and len(lf) < 2:
        fail("light", "the light always comes from the same side", list(opens), 0.4)
    sh = count("shadow")
    if m >= 2 and sum(len(v) for v in sh.values()) >= 3 and len(sh) < 2:
        fail("light", "every slot has the same shadow softness (the set needs soft and crisp)",
             [x for v in sh.values() for x in v], 0.4)
    # walls
    wf = count("wall_family")
    for k, ss in wf.items():
        lim = 0.4 * n if k == "white_cream" else 3
        if len(ss) > lim:
            fail("walls", f"{len(ss)} slots have {k.replace('_', ' ')} walls", ss, 0.8)
    loud = [s for s, d in allv.items() if d.get("wall_loud")]
    if len(loud) > 2:
        fail("walls", f"{len(loud)} slots have loud or very deep walls (at most 2)", loud[2:] if len(loud) > 2 else [])
    wt = count("wall_treatment")
    ntr = sum(len(v) for v in wt.values())
    for k, ss in wt.items():
        if ntr >= 4 and len(ss) > 0.5 * ntr:
            fail("walls", f"{len(ss)} of {ntr} walls are {k.replace('_', ' ')}", ss, 0.5)
    if len(wt.get("wallpaper", [])) > 1:
        fail("walls", "more than one patterned wallpaper", wt["wallpaper"][1:])
    # furniture
    for k, ss in count("furniture").items():
        if len(ss) > 1:
            fail("furniture", f"the same furniture ({k.replace('_', ' ').replace('|', ', ')}) twice", ss[1:])
    for k, ss in count("furniture_family").items():
        if len(ss) > 3:
            fail("furniture", f"{len(ss)} slots have {k.replace('_', ' ')} furniture", ss, 0.5)
    # setting / house / buyer
    for k, ss in count("setting").items():
        if len(ss) > 1:
            fail("setting", f"setting {k.replace('_', ' ')} is used twice", ss[1:] if ss[0] in opens else ss)
    for k, ss in count("house").items():
        if len(ss) > 2:
            fail("house", f"{len(ss)} slots are in a {k.replace('_', ' ')}", ss, 0.5)
    bc = count("buyer")
    nb = sum(len(v) for v in bc.values())
    if len(bc) < min(4, nb):
        fail("buyer", f"only {len(bc)} buyer types across the set (at least 4)", list(opens), 0.4)
    # presentation
    pc = count("presentation")
    npres = sum(len(v) for v in pc.values())
    for k, ss in pc.items():
        if npres >= 4 and len(ss) > 0.6 * npres:
            fail("presentation", f"{len(ss)} of {npres} slots are {k.replace('_', ' ')}", ss, 0.5)
    small = [s for s, d in allv.items() if d.get("scale") == "small"]
    if len(small) >= 2 and "mat" not in pc:
        fail("presentation", "two or more small prints and no mat", small)
    # tight cap until the first tight scene passed its real test (plan section 12, setting planner_max_tight)
    tight = [s for s, d in opens.items() if d.get("shot") == "tight"]
    if max_tight is not None and len(tight) > max_tight:
        fail("tight", f"{len(tight)} tight shots; at most {max_tight} until the first tight scene is proven",
             tight[max_tight:])
    # pairwise
    pairs = {}
    keys = sorted(allv)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            if a not in opens and b not in opens:
                continue
            sim = similarity(allv[a], allv[b])
            pairs[f"{a}-{b}"] = round(sim, 2)
            if sim >= SIM_MAX:
                later = b if b in opens else a
                fail("similar", f"slots {a} and {b} are too alike ({sim:.2f})", [later])
            if a in opens and b in opens:
                ta, tb = _tokens(allv[a]["scene"]), _tokens(allv[b]["scene"])
                jac = len(ta & tb) / max(len(ta | tb), 1)
                if jac >= JACCARD_MAX:
                    fail("similar", f"slots {a} and {b} have near-identical scene text ({jac:.2f})", [b])
    return {"pass": not fails, "failures": fails, "blame": {s: round(v, 2) for s, v in blame.items()},
            "scores": {"pairs_max": max(pairs.values()) if pairs else 0.0, "n": n, "open": m}}


def total_blame(chk):
    return round(sum(chk["blame"].values()), 2)


# ---------- library candidates + swap ----------

def library_brief(t, slot_ctx, used_sizes=()):
    """A brief for a library template (free): its measured descriptor, a story size in its ratio + measured scale."""
    meta = t.get("meta") or {}
    shot = meta.get("shot") or "wide"
    scale = SHOTS[shot]["scale"]
    ratio = t["ratio"]
    sizes = [s for sc in (scale,) + tuple(x for x in SCALES if x != scale) for s in SIZE_CHART[ratio].get(sc, [])]
    size = next((s for s in sizes if s not in used_sizes), sizes[0] if sizes else None)
    wall = {"name": None, "hex": None, "treatment": None, "family": None}
    if meta.get("wall_lab"):
        wall.update(family=wall_family(meta["wall_lab"]), lab=meta["wall_lab"])
    saved = t.get("brief") or {}
    b = {"slot": slot_ctx["slot"], "room": slot_ctx["room"], "decor": slot_ctx["decor"], "source": "library",
         "library_rel": t["rel"], "print_size": size, "ratio": ratio, "scale": SIZE_INDEX.get(size, (ratio, scale))[1],
         "shot": shot, "camera_side": meta.get("camera_side"), "light_from": meta.get("light_from"),
         "presentation": meta.get("presentation"), "wall": wall, "marker": t.get("marker") or "orange",
         "setting": saved.get("setting"), "display": saved.get("display"), "furniture": saved.get("furniture") or {},
         "house": saved.get("house"), "buyer": saved.get("buyer"), "light_style": saved.get("light_style"),
         "scene": "", "prompt": None, "library_name": t.get("name"), "library_desc": t.get("desc")}
    return b


def library_swap(briefs, fixed, cands, order=None, ratio_avail=None, max_tight=None):
    """After the set passes: each NEW brief tries its slot's library candidates (same shot, unused); a swap is kept when
    the set still passes and no pair gets more alike than SIM_MAX. Returns (briefs, swapped slots)."""
    out = dict(briefs)
    used = {b.get("library_rel") for b in out.values() if b.get("library_rel")}
    swapped = []
    for s in sorted(out):
        b = out[s]
        if b.get("source") != "new":
            continue
        for t in cands.get(s) or []:
            if t["rel"] in used or (t.get("meta") or {}).get("shot") != b.get("shot"):
                continue
            nb = library_brief(t, {"slot": s, "room": b["room"], "decor": b["decor"]},
                               [x.get("print_size") for k, x in out.items() if k != s])
            nb["lint"] = {"pass": True, "why": []}
            trial = {**out, s: nb}
            if check_set(trial, fixed, order, ratio_avail, max_tight)["pass"]:
                out = trial
                used.add(t["rel"])
                swapped.append(s)
                break
    return out, swapped


# ---------- the planner (claude -p) ----------

SYSTEM_PROMPT = """You plan the room photographs for one Etsy listing of a printable wall-art design, as three people \
at once: an interior designer who furnishes believable homes, an interiors photographer who frames and lights them, \
and a curator who decides how a buyer should first meet this artwork. You see the artwork, the photographs that \
already exist for this listing, and the open slots you must plan.

Write one scene per open slot in a single pass. The set must feel like one calm, clean, believable shop: real homes, \
few objects, good natural light, nothing staged or cluttered. Variety comes from WHERE the piece lives and HOW it is \
photographed, never from noise.

Every artwork is a PORTRAIT (vertical) piece. Every photograph is a 4:3 landscape listing photo.

What a slot is: the room name is where it is filed. The setting is the surface or wall inside that room (a \
nightstand, a desk, a mantel, an entry console or hallway wall, which are filed under Living room, the wall over a \
bed, a bathroom wall with wallpaper). Setting and shot are separate choices.

Scale drives framing. Pick a real print size from the chart for each slot. Small prints are shown TIGHT: the piece \
stands or leans on a surface and fills about half to two thirds of the picture height, with one to three small \
everyday objects at true scale beside it. Medium prints are medium shots with the furniture below. Large prints are \
wider shots on a wall or leaning on the floor. Across the whole listing aim for roughly a third small, a third \
medium, a third large, all five ratios, and several different sizes; the photographs that already exist count, so \
fill what they lack.

The art ties in with the scene, which does NOT mean matching its colours. Do not take the wall or furniture colours \
from the artwork. Contrast and complement are welcome; quiet neutrals are the default; one or two slots may use a \
loud wall or a bold furniture piece when it flatters this piece. Warm walls (terracotta, adobe, mustard, sand, \
warm brown) are allowed: the pipeline picks the colour of the blank print area itself. Think of the buyer each scene \
speaks to.

Photography taste (from the shop owner's reference board): mostly straight-on or a gentle angle, low to middle \
camera height, close framing with the art as the clear subject, furniture often cut by the bottom edge, warm low sun \
or soft window daylight with soft visible shadows, plaster or limewash walls, walnut and oak, a few sculptural \
objects (stoneware, dried stems, a small brass or bronze piece, one plant at the edge). Vary across the set: camera \
side, height, lens, light direction and quality, shadow softness, depth of field, how much room shows, wall colour \
and texture, furniture style AND colour, house type and region.

Hard rules, never broken:
- No people, faces, hands or pets. One piece of art only. No other frames, posters or mirrors.
- Nothing readable: no labels, logos, signs, lettering, book titles (books have plain covers or face away).
- Every scene shows visible shadows (soft or crisp). The art face is flat, upright, in sharp focus, evenly lit.
- The whole frame is inside the picture with clear space around it; nothing overlaps the frame.
- The frame contrasts with the wall in tone (frame lightness: black 15, walnut 35, gold 60, oak 65, white 95, canvas \
floater = natural wood 65; wall lightness at least 15 away). Canvas only for medium and large prints.
- Wainscoting only below waist height (say "below waist height"), or panelling with the art "centred inside one \
larger panel" (say so).
- Do not describe the artwork itself; the print area is replaced later. Do not describe the camera, lens or light \
direction in the scene text either: those come from the fields.
- The scene text is 60 to 160 words of plain, positive description of the room and the setting. Never explain why.
- Prefer a listed library template for a slot when one fits the set (it is free); otherwise plan a new scene.

Output ONLY one JSON object, no prose, no reasons, no explanations."""

SCHEMA = {"briefs": [{
    "slot": "int", "source": "new | library", "library_rel": "rel of a listed library template, only for library",
    "print_size": "a size from the chart", "shot": "tight | medium | wide", "setting": "one of the slot's settings",
    "display": "one of that setting's displays", "presentation": "frame | mat | canvas | canvas_bare",
    "frame_finish": "oak_frame | walnut_frame | black_frame | white_frame | gold_frame (canvas: natural_wood_floater)",
    "camera_side": "left | right | front", "camera_height": "surface | low | seated | counter | eye",
    "lens": "|".join(LENSES), "light_style": "|".join(LIGHT_STYLES), "light_from": "|".join(LIGHT_FROM),
    "shadow": "soft | hard", "depth_of_field": "|".join(DOFS),
    "wall": {"name": "plain colour name", "hex": "#RRGGBB", "treatment": "|".join(WALL_TREATMENTS)},
    "floor": "short phrase", "furniture": {"style": "|".join(FURNITURE_STYLES), "colour": "one word",
                                           "family": "|".join(FURNITURE_FAMILIES)},
    "house": "|".join(HOUSES), "buyer": "|".join(BUYERS), "props": ["1-3 small objects for tight, at most 5"],
    "scene": "60-160 words"}]}


def cfg(settings, key):
    return (settings or {}).get(key, DEFAULTS[key])


def parse(raw):
    """The JSON object in a model reply (fences and stray text around it allowed). Raises ValueError."""
    t = str(raw or "")
    m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", t, re.S)
    t = m.group(1) if m else t[t.find("{"): t.rfind("}") + 1]
    obj = json.loads(t)
    if not isinstance(obj, dict):
        raise ValueError("not a JSON object")
    items = obj.get("briefs")
    if isinstance(items, dict):
        items = [dict(v, slot=v.get("slot", k)) for k, v in items.items()]
    if not isinstance(items, list):
        raise ValueError("no briefs list")
    out = {}
    for it in items:
        if isinstance(it, dict):
            try:
                out[int(it.get("slot"))] = it
            except (TypeError, ValueError):
                continue
    return out


def _compact(b):
    return {k: b.get(k) for k in ("slot", "source", "library_rel", "print_size", "shot", "setting", "display",
                                  "presentation", "frame_finish", "camera_side", "camera_height", "lens", "light_style",
                                  "light_from", "shadow", "depth_of_field", "floor", "house", "buyer", "props", "scene")} \
        | {"wall": {k: (b.get("wall") or {}).get(k) for k in ("name", "hex", "treatment")},
           "furniture": b.get("furniture")}


def planner_prompt(ctx, current=None, failures=None, rewrite=None, wider=()):
    data = {
        "design": ctx["design"],
        "size_chart": {r: {k: v for k, v in d.items() if v} for r, d in SIZE_CHART.items()},
        "shots": {k: {"scale": v["scale"], "frame_height_share_percent": list(v["frac"])} for k, v in SHOTS.items()},
        "shot_allowed_by_scale": {k: list(v) for k, v in SHOT_OK.items()},
        "credits_per_new_scene": ctx.get("credits_per_scene"),
        "max_tight_shots": ctx.get("max_tight"),
        "existing_photographs": list(ctx["fixed"].values()),
        "open_slots": [{"slot": o["slot"], "room": o["room"], "decor": o["decor"], "ratios_with_a_folder": o["ratios"],
                        "settings": {s: {"displays": list(SETTINGS[s][1]), "scales": list(SETTINGS[s][2])}
                                     for s in ROOM_SETTINGS.get(o["room"], [])},
                        "library": [{k: t.get(k) for k in ("rel", "ratio", "decor", "desc")} | (t.get("meta") or {})
                                    for t in o.get("library") or []][:8]}
                       for o in ctx["open"] if rewrite is None or o["slot"] in rewrite],
        "lists": {"house": HOUSES, "buyer": BUYERS, "furniture.style": FURNITURE_STYLES,
                  "furniture.family": FURNITURE_FAMILIES, "wall.treatment": WALL_TREATMENTS},
        "output_schema": SCHEMA}
    head = ("Image 1 is the artwork. Image 2 (when present) is a contact sheet of the photographs that already exist, "
            "each labelled with its slot number.\n\n")
    if current is None:
        task = f"Plan every open slot ({', '.join(str(o['slot']) for o in ctx['open'])})."
    else:
        task = ("This is your current plan:\n" + json.dumps([_compact(b) for b in current.values()], ensure_ascii=False)
                + "\n\nThese rules are broken:\n" + "\n".join(f"- {f}" for f in failures or [])
                + f"\n\nRewrite ONLY slots {', '.join(map(str, rewrite))}; keep every other slot as it is and return "
                  "only the rewritten slots.")
    if wider:
        task += (f"\nSlot(s) {', '.join(map(str, wider))}: plan one step WIDER than before (a medium shot of a small "
                 "or medium print), because the tight scene could not be built.")
    return head + "Inputs:\n" + json.dumps(data, ensure_ascii=False) + "\n\n" + task + "\nReturn only the JSON object."


def default_ask(settings, system=None):
    """ask(prompt, images) -> raw reply, through the same headless claude -p route as the Studio chat (Tony's plan,
    no credits). system: the planner's system prompt by default, VISION_SYSTEM for the fixed-slot describe."""
    from .assistant import run_cli

    def ask(prompt, images=None):
        return run_cli(prompt, system or SYSTEM_PROMPT, cfg(settings, "planner_model"),
                       cfg(settings, "planner_fallback_model"), int(cfg(settings, "planner_timeout_s")), settings,
                       who="The scene planner", images=images)
    return ask


def _call(ask, prompt, images, log):
    """One planner call with one retry on unusable JSON."""
    raw = ask(prompt, images)
    try:
        return parse(raw)
    except (ValueError, TypeError) as e:
        log(f"planner reply was not usable JSON ({e}); asking once more")
        return parse(ask(prompt + "\n\nYour last answer was not valid JSON. Return valid JSON only.", images))


def finish(briefs, ctx):
    """normalise + lint + prompt for every brief of the open slots."""
    out = {}
    for o in ctx["open"]:
        raw = briefs.get(o["slot"])
        if raw is None:
            continue
        if raw.get("_done"):
            out[o["slot"]] = raw
            continue
        if raw.get("source") == "library":
            t = next((x for x in o.get("library") or [] if x["rel"] == raw.get("library_rel")), None)
            if t is not None:
                b = library_brief(t, o, [x.get("print_size") for x in out.values()])
                b["lint"], b["_done"] = {"pass": True, "why": []}, True
                out[o["slot"]] = b
                continue
            raw = dict(raw, source="new", library_rel=None)
        b = normalise(raw, o)
        b["lint"] = lint(b, o)
        b["prompt"] = assemble(b) if b["lint"]["pass"] else None
        b["_done"] = True
        out[o["slot"]] = b
    return out


def plan_set(ctx, ask, settings=None, log=print, wider=()):
    """The planning loop (plan 7.4). ctx from context(); ask(prompt, images) -> raw text. Returns a set_plan dict
    (status ready | needs_attention | failed, briefs, check, rounds, cost) without saving anything."""
    import time
    t0 = time.time()
    rounds = int(cfg(settings, "planner_rounds"))
    max_tight = ctx.get("max_tight")
    order = ctx["order"]
    avail = {o["slot"]: o["ratios"] for o in ctx["open"]}
    images = ctx.get("images") or []
    out = {"version": VERSION, "status": "planning", "model": cfg(settings, "planner_model"), "rounds": 0,
           "created": datetime.now().isoformat(timespec="seconds")}
    try:
        got = _call(ask, planner_prompt(ctx, wider=wider), images, log)
    except Exception as e:  # noqa: BLE001  (ChatUnavailable, bad JSON twice)
        return {**out, "status": "failed", "message": f"the scene planner could not answer: {str(e)[:160]}",
                "briefs": {}, "seconds": round(time.time() - t0)}
    cur = finish(got, ctx)
    best = None
    for rnd in range(rounds + 1):
        out["rounds"] = rnd + 1
        missing = [o["slot"] for o in ctx["open"] if o["slot"] not in cur]
        chk = check_set(cur, ctx["fixed_desc"], order, avail, max_tight)
        lint_bad = [s for s, b in cur.items() if not b["lint"]["pass"]]
        score = total_blame(chk) + 3 * len(lint_bad) + 5 * len(missing)
        if best is None or score < best[0]:
            best = (score, dict(cur), chk)
        if chk["pass"] and not lint_bad and not missing:
            break
        if rnd == rounds:
            break
        top = sorted(chk["blame"], key=lambda s: -chk["blame"][s])
        redo = sorted(set([s for s in top if chk["blame"][s] > 0][:4] + lint_bad + missing))
        words = [f["text"] for f in chk["failures"]] + [f"slot {s}: {w}" for s in lint_bad for w in cur[s]["lint"]["why"]]
        words += [f"slot {s} has no brief" for s in missing]
        log(f"round {rnd + 1}: {len(chk['failures'])} set failures, {len(lint_bad)} lint failures; rewriting {redo}")
        try:
            got = _call(ask, planner_prompt(ctx, cur, words, redo), images, log)
        except Exception as e:  # noqa: BLE001
            log(f"rewrite call failed: {e}")
            break
        cur = {**cur, **{s: b for s, b in finish({s: got[s] for s in redo if s in got}, ctx).items()}}
    _, cur, chk = best
    lint_bad = [s for s, b in cur.items() if not b["lint"]["pass"]]
    if chk["pass"] and not lint_bad:
        cands = {o["slot"]: o.get("library") or [] for o in ctx["open"]}
        cur, swapped = library_swap(cur, ctx["fixed_desc"], cands, order, avail, max_tight)
        chk = check_set(cur, ctx["fixed_desc"], order, avail, max_tight)
        if swapped:
            log(f"library templates (free) used for slots {swapped}")
    status = "ready" if chk["pass"] and not lint_bad and len(cur) == len(ctx["open"]) else "needs_attention"
    msg = "" if status == "ready" else "; ".join([f["text"] for f in chk["failures"][:3]]
                                                 + [f"slot {s}: {cur[s]['lint']['why'][0]}" for s in lint_bad[:2]])
    briefs = {}
    for s, b in cur.items():
        b = {k: v for k, v in b.items() if k != "_done"}
        b.update(rev=1, edited_by="planner", history=[], stale=False, attempts=[])
        briefs[str(s)] = b
    cps = ctx.get("credits_per_scene") or 0
    new = sum(1 for b in briefs.values() if b["source"] == "new")
    out.update(status=status, message=msg, briefs=briefs,
               check={"pass": chk["pass"], "failures": chk["failures"], "blame": chk["blame"], "scores": chk["scores"]},
               cost={"library": len(briefs) - new, "new": new, "credits_per_scene": cps, "credits": new * cps,
                     "usd": round(new * cps * 0.005, 2)},
               seconds=round(time.time() - t0), updated=datetime.now().isoformat(timespec="seconds"))
    return out


# ---------- context (the real listing) ----------

def _ratio_of_print(name):
    for r, tag in rs.PRINT_RATIO_TAG.items():
        if f"_{tag}_" in str(name or ""):
            return r
    return None


def fixed_descriptor(con, settings, srec, image_path, vision=None):
    """Measured facts of one existing slot image (template manifest + the image), plus the categorical guesses of
    the vision describe (`vision`: dict or None). Measured fields win; unknown stays None."""
    from . import scene_templates as stp
    d = {k: None for k in descriptor({})}
    d.update(slot=None, ratio=_ratio_of_print(srec.get("print")) or srec.get("ratio"), scene="")
    rel = srec.get("template")
    man = None
    if rel:
        psd = stp.library(settings) / rel
        if not psd.is_file():                       # moved to its style folder's Archive (denied) or renamed
            psd = None
        man = stp.load_manifest(psd) if psd else None
    meta = stp.shot_meta(man, image_path) if man else {}
    if meta:
        d.update(shot=meta["shot"], camera_side=meta["camera_side"], light_from=meta.get("light_from"),
                 presentation=meta.get("presentation"), art_h_frac=meta["art_h_frac"])
        if meta.get("wall_lab"):
            d.update(wall_family=wall_family(meta["wall_lab"]), wall_loud=is_loud(meta["wall_lab"]),
                     wall_lab=meta["wall_lab"])
    look = (man or {}).get("look") or {}
    if look.get("version") == 2:
        d.update(camera_height=look.get("camera_height"), lens=look.get("lens"),
                 depth_of_field=look.get("depth_of_field"), wall_treatment=look.get("wall_treatment"),
                 light_style=look.get("light_style"))
    elif look.get("light_style"):
        d["light_style"] = look["light_style"]
    if (man or {}).get("brief"):
        bd = descriptor(man["brief"])
        d.update({k: v for k, v in bd.items() if d.get(k) is None and v is not None and k != "scene"})
    for k, v in (vision or {}).items():
        if k in d and d.get(k) is None and v not in (None, "", "unknown"):
            d[k] = v
    if vision and vision.get("furniture_style"):
        d["furniture"] = f"{vision['furniture_style']}|{vision.get('furniture_colour') or '-'}"
    # Scale of an existing image (G1 finding, 2026-11-19): the legacy library frames BIG wall pieces close (art ~50%
    # of the picture height), so the measured shot can not tell the print's scale. A template made from a brief keeps
    # its brief's scale; otherwise a piece standing on a surface is small, everything else a large wall piece.
    if (man or {}).get("brief", {}).get("scale"):
        d["scale"] = man["brief"]["scale"]
    elif d.get("display") in SURFACE_DISPLAYS:
        d["scale"] = "small"
    else:
        d["scale"] = "large"
    return d


VISION_SYSTEM = ("You describe interior photographs with categorical facts for a planning tool. You answer with one JSON "
                 "object only, no prose.")
VISION_PROMPT = ("These are existing room photographs of one Etsy wall-art listing, in the order given by the slot "
                 "numbers listed below. For each, answer with categorical facts only, choosing from the lists. Output "
                 "ONLY a JSON object {\"<slot>\": {\"setting\", \"display\", \"furniture_style\", \"furniture_colour\", "
                 "\"furniture_family\", \"house\", \"buyer\", \"camera_height\", \"wall_treatment\", \"light_style\", "
                 "\"shadow\"}}; use null when unsure. No prose.")


def describe_fixed(items, ask_vision):
    """ONE vision call for all uncached existing slot images: [(slot, path)] -> {slot: {...}}. Failures -> {}."""
    if not items:
        return {}
    from .prod_chat import encode_image
    lists = {"setting": sorted(SETTINGS), "display": DISPLAYS, "furniture_style": FURNITURE_STYLES,
             "furniture_family": FURNITURE_FAMILIES, "house": HOUSES, "buyer": BUYERS,
             "camera_height": CAMERA_HEIGHTS, "wall_treatment": WALL_TREATMENTS, "light_style": LIGHT_STYLES,
             "shadow": SHADOWS}
    prompt = (VISION_PROMPT + "\nSlots in image order: " + ", ".join(str(s) for s, _ in items) + "\nLists: "
              + json.dumps(lists))
    try:
        raw = ask_vision(prompt, [encode_image(p, 900) for _, p in items])
        t = str(raw)
        obj = json.loads(t[t.find("{"): t.rfind("}") + 1])
    except Exception:  # noqa: BLE001  (unknown is fine: the check never treats it as a duplicate)
        return {}
    out = {}
    for s, _ in items:
        v = obj.get(str(s)) if isinstance(obj, dict) else None
        if isinstance(v, dict):
            out[s] = {k: v.get(k) for k in lists if v.get(k) in lists[k]} | (
                {"furniture_colour": str(v.get("furniture_colour"))[:20]} if v.get("furniture_colour") else {})
    return out


def contact_sheet(items, out_path, cell=420):
    """One labelled image of the existing slot photographs: [(slot, path)] -> PNG path (None when empty)."""
    if not items:
        return None
    from PIL import Image, ImageDraw
    cols = min(4, len(items))
    rows = math.ceil(len(items) / cols)
    ch = int(cell * 0.75)
    sheet = Image.new("RGB", (cols * cell, rows * (ch + 22)), (245, 243, 238))
    dr = ImageDraw.Draw(sheet)
    for i, (s, p) in enumerate(items):
        try:
            with Image.open(p) as im:
                im = im.convert("RGB")
                im.thumbnail((cell - 8, ch))
                x, y = (i % cols) * cell + 4, (i // cols) * (ch + 22) + 20
                sheet.paste(im, (x, y))
        except OSError:
            continue
        dr.text(((i % cols) * cell + 6, (i // cols) * (ch + 22) + 4), f"slot {s}", fill=(20, 20, 20))
    sheet.save(out_path)
    return out_path


def library_candidates(settings, room, used, fails, limit=8):
    """Unused, checker-not-failed library templates of this room (any ratio with a folder), with shot_meta."""
    from . import scene_templates as stp
    out = []
    want = rs.ROOM_FOLDER.get(room)
    for t in stp.library_templates(settings):
        if t.get("wired") or t["rel"] in used or t["rel"] in fails or rs.norm(t["room"]) != want:
            continue
        man = t.get("manifest") or {}
        scene = t["psd"].parent / str(man.get("scene") or "") if man.get("scene") else None
        meta = stp.shot_meta(man, scene if scene is not None and scene.is_file() else None) if man else {}
        if not meta:
            continue
        out.append({"rel": t["rel"], "name": t["name"], "ratio": t["ratio"], "decor": t["style"],
                    "desc": t.get("desc"), "brief": man.get("brief"),
                    "marker": (man.get("brief") or {}).get("marker"),
                    "meta": {k: meta.get(k) for k in ("shot", "art_h_frac", "camera_side", "light_from",
                                                      "presentation", "wall_lab")}})
        if len(out) >= limit:
            break
    return out


def context(con, settings, idea_id, ask_vision=None, cached_fixed=None, work=None):
    """Everything the planner needs for one design: design facts, fixed slot descriptors (measured + one cached
    vision describe), ALL open slots (room + decor from rs.plan; Tony's picks honoured), library candidates, images."""
    from . import production as prod
    idea, lst, rec, folder, arts = prod._ctx(con, settings, idea_id)
    plan, avail = prod._plan(con, settings, idea, rec, folder, arts)
    p = prod._prod(rec)
    fixed_items, open_slots = _split_slots(idea_id, rec, folder, plan)
    cache = dict(cached_fixed or {})
    todo = [(s, pth) for s, pth, _, name in fixed_items if name and name not in cache and pth]
    vis = describe_fixed(todo, ask_vision) if ask_vision else {}
    fixed, fixed_desc = {}, {}
    for s, pth, srec, name in fixed_items:
        ent = cache.get(name)
        if ent is None:
            d = fixed_descriptor(con, settings, srec, pth, vis.get(s))
            ent = {"descriptor": d, "file": name, "from": "measured+vision" if vis.get(s) else "measured"}
        d = dict(ent["descriptor"], slot=s)
        fixed[name] = ent
        fixed_desc[s] = d
    fails = prod.checker_fails(settings)
    used = {s.get("template") for s in p["slots"].values() if s.get("template")}
    tags = rec.get("design_tags") or {}
    styles, _ = prod.effective_styles(tags)
    an = prod._analysis(rec, arts)
    opens = [{"slot": c["slot"], "room": c["room"], "decor": c["decor"], "by": c.get("by"),
              "ratios": list(avail.get(c["room"]) or []),
              "library": library_candidates(settings, c["room"], used, fails)} for c in open_slots]
    images = []
    iso = next((a for a in arts if "_ISO_" in a.name), arts[0] if arts else None)
    from .prod_chat import encode_image
    if iso is not None:
        images.append(encode_image(iso, 1568))
    if work is not None and fixed_items:
        sheet = contact_sheet([(s, pth) for s, pth, _, _ in fixed_items if pth], Path(work) / "contact_sheet.png")
        if sheet:
            images.append(encode_image(sheet, 1568))
    eng = prod._engine(settings)
    fx_view = {str(s): {k: v for k, v in d.items() if v is not None and k not in ("scene", "wall_lab")}
               for s, d in fixed_desc.items()}
    return {"idea_id": idea_id, "listing_id": lst["id"], "order": rs.room_slots(settings),
            "design": {"title": idea["title"], "name": lst["title"], "description": idea["description"],
                       "styles": styles, "value_key": an.get("value_key"),
                       "accents": [a.get("name") for a in an.get("accents") or []]},
            "fixed": fx_view, "fixed_desc": fixed_desc, "fixed_cache": fixed, "open": opens, "images": images,
            "credits_per_scene": eng.get("credits_per_scene"), "max_tight": int(cfg(settings, "planner_max_tight")),
            "inputs_key": _key(tags, styles, open_slots, fixed_items, p)}


# ---------- storage + background jobs ----------

_running = set()
_run_lock = threading.Lock()


def get_plan(rec):
    return ((rec or {}).get("production") or {}).get("set_plan")


def brief_for(rec, slot):
    """The brief run_slot may use for this slot: it exists, is not stale, its lint passed and the plan did not fail."""
    sp = get_plan(rec) or {}
    if sp.get("status") not in ("ready", "needs_attention"):
        return None
    b = (sp.get("briefs") or {}).get(str(slot))
    if not b or b.get("stale") or not (b.get("lint") or {}).get("pass"):
        return None
    if b.get("source") == "new" and not b.get("prompt"):
        return None
    return b


def is_running(idea_id):
    with _run_lock:
        return int(idea_id) in _running


def start(con, settings, idea_id, spawn, slots=None, ask=None, wider=()):
    """Mark the plan 'planning' and run it in a worker. Returns False when one is already running for this design."""
    with _run_lock:
        if int(idea_id) in _running:
            return False
        _running.add(int(idea_id))
    _save(con, idea_id, lambda sp: sp.update(status="planning", message="", updated=_now()))
    spawn(run, con, settings, idea_id, slots, ask, wider)
    return True


def _now():
    return datetime.now().isoformat(timespec="seconds")


def _save(con, idea_id, fn):
    from . import prints
    from .db import DB_LOCK as LOCK
    with LOCK:
        lst = prints.listing_for(con, idea_id)
        rec = prints._record(con, lst["id"])
        p = rec.setdefault("production", {})
        sp = p.setdefault("set_plan", {"version": VERSION, "briefs": {}})
        fn(sp)
        prints._save_record(con, lst["id"], rec)
        return sp


def run(con, settings, idea_id, slots=None, ask=None, wider=(), log=None, ask_vision=None):
    """Worker: plan the open slots (or only `slots`) and save production.set_plan. Never touches production.slots,
    approved / pending slots, a running slot or briefs Tony edited in the chat (unless named in `slots`). Open slots
    that are not re-planned keep their briefs and count as fixed for the set check."""
    import tempfile
    log = log or (lambda *_: None)
    try:
        sp = get_plan(_record(con, idea_id)) or {}
        ask = ask or default_ask(settings)
        if ask_vision is None:
            ask_vision = ask if ask is not None and not getattr(ask, "_default", False) else \
                default_ask(settings, VISION_SYSTEM)
        with tempfile.TemporaryDirectory() as td:
            ctx = context(con, settings, idea_id, ask_vision, sp.get("fixed"), td)
            want = {int(x) for x in slots} if slots else None
            old = sp.get("briefs") or {}
            plan_now, hold = [], {}
            for o in ctx["open"]:
                b = old.get(str(o["slot"]))
                named = want is not None and o["slot"] in want
                if named or (want is None and not (b and b.get("edited_by") == "chat")):
                    plan_now.append(o)
                elif b and not b.get("stale"):
                    hold[o["slot"]] = b
            ctx["open"] = plan_now
            for s, b in hold.items():                    # kept briefs (chat edits, other slots) count as fixed
                ctx["fixed_desc"][s] = dict(descriptor(b), slot=s)
            res = plan_set(ctx, ask, settings, log, wider) if plan_now else \
                {"status": "ready", "briefs": {}, "message": "", "rounds": 0, "check": {"pass": True, "failures": []}}
        planned = {str(o["slot"]) for o in plan_now}
        open_now = {str(o["slot"]) for o in plan_now} | {str(s) for s in hold}

        def put(sp):
            prev_all = sp.get("briefs") or {}
            new = {s: b for s, b in prev_all.items() if s in open_now and s not in planned}
            for s, b in (res.get("briefs") or {}).items():
                prev = prev_all.get(s)
                if prev:
                    b["rev"] = int(prev.get("rev") or 1) + 1
                    b["history"] = (prev.get("history") or [])[-4:] + [history_entry(prev)]
                    b["attempts"] = prev.get("attempts") or []
                b["updated"] = _now()
                new[s] = b
            # briefs of slots that are no longer open (approved / pending images) stay for the record, untouched
            new.update({s: b for s, b in prev_all.items() if s not in open_now and s not in new})
            sp.update({k: v for k, v in res.items() if k != "briefs"})
            sp["briefs"] = new
            sp["cost"] = cost(new, ctx.get("credits_per_scene"), open_now)
            sp["fixed"] = ctx["fixed_cache"]
            sp["inputs_key"] = ctx["inputs_key"]
            sp["updated"] = _now()
        _save(con, idea_id, put)
    except Exception as e:  # noqa: BLE001  (shown on the panel; Generate falls back to the random look)
        _save(con, idea_id, lambda sp: sp.update(status="failed", message=f"planning failed: {str(e)[:200]}",
                                                 updated=_now()))
    finally:
        with _run_lock:
            _running.discard(int(idea_id))


def cost(briefs, credits_per_scene, open_slots=None):
    """{library, new, credits_per_scene, credits, usd} over the briefs of open slots."""
    bs = [b for s, b in (briefs or {}).items() if open_slots is None or s in open_slots]
    new = sum(1 for b in bs if b.get("source") == "new")
    cps = credits_per_scene or 0
    return {"library": len(bs) - new, "new": new, "credits_per_scene": cps, "credits": new * cps,
            "usd": round(new * cps * 0.005, 2)}


def _record(con, idea_id):
    """The listing record, read under the DB lock (read only)."""
    from . import prints
    from .db import DB_LOCK as LOCK
    with LOCK:
        lst = prints.listing_for(con, idea_id)
        return prints._record(con, lst["id"]) if lst else {}


def recover(con):
    """On startup: a plan left 'planning' by a restart is marked failed (its thread is gone)."""
    from . import prints
    from .db import DB_LOCK as LOCK
    with LOCK:
        for r in con.execute("SELECT id, record FROM listings").fetchall():
            rec = json.loads(r["record"] or "{}")
            sp = get_plan(rec)
            if sp and sp.get("status") == "planning":
                sp.update(status="failed", message="stopped by a Portal restart; Re-plan open slots")
                prints._save_record(con, r["id"], rec)


def inputs_key(con, settings, idea_id):
    """sha1 of what a plan depends on: Tony's room / style ticks, the open slots' room + decor, and the fixed slot
    files (slots whose image was made from their own brief are part of the plan, so they do not change the key).
    Cheap: no images, no vision, no library scan. Returns (key, open slot numbers)."""
    from . import production as prod
    idea, lst, rec, folder, arts = prod._ctx(con, settings, idea_id)
    plan, _ = prod._plan(con, settings, idea, rec, folder, arts)
    fixed_items, open_slots = _split_slots(idea_id, rec, folder, plan)
    tags = rec.get("design_tags") or {}
    styles, _ = prod.effective_styles(tags)
    return _key(tags, styles, open_slots, fixed_items, prod._prod(rec)), [c["slot"] for c in open_slots]


def _key(tags, styles, open_slots, fixed_items, p):
    fx = sorted((s, name) for s, _, _, name in fixed_items if not (p["slots"].get(str(s)) or {}).get("brief_rev"))
    src = json.dumps({"rooms": tags.get("rooms"), "styles": styles,
                      "open": [(c["slot"], c["room"], c["decor"]) for c in open_slots], "fixed": fx}, sort_keys=True)
    return hashlib.sha1(src.encode()).hexdigest()


def _split_slots(idea_id, rec, folder, plan):
    """(fixed items [(slot, image path, slot record, file)], open cards) of a design's slot plan."""
    from . import production as prod
    p = prod._prod(rec)
    approvals = rec.get("mockup_approvals") or {}
    job = prod.job_state()
    fixed_items, open_slots = [], []
    for c in plan:
        srec = p["slots"].get(str(c["slot"])) or {}
        name, path, where = prod._current_image(folder, c["slot"], srec, rec)
        running = job["running"] and job["idea_id"] == idea_id and job["slot"] == c["slot"]
        # an image that is approved or waiting for Tony's decision (also a flagged one) is fixed; denied = open
        decided = bool(name) and approvals.get(name) != "denied" and where in ("folder", "flagged")
        if decided or running:
            fixed_items.append((c["slot"], path, srec, name))
        else:
            open_slots.append(c)
    return fixed_items, open_slots


def mark_stale(con, idea_id, key):
    """Open briefs become stale when the design's inputs changed. Returns True when the plan was marked (the caller
    then starts a background re-plan). Chat-edited briefs never go stale on their own."""
    changed = []

    def fn(sp):
        if sp.get("inputs_key") != key and sp.get("status") != "planning":
            for b in (sp.get("briefs") or {}).values():
                if b.get("edited_by") != "chat":
                    b["stale"] = True
            sp["inputs_key"] = key
            changed.append(True)
    _save(con, idea_id, fn)
    return bool(changed)


def auto(con, settings, idea_id, spawn, ask=None):
    """Panel open / tag change (setting planner_auto): start a background plan when the design has open slots and no
    plan yet, when its inputs changed (open briefs go stale first), or when an open slot has no brief. A failed plan
    is NOT retried on its own (no loop while the CLI is down): Tony clicks Re-plan. Never blocks; never raises."""
    if not cfg(settings, "planner_auto") or is_running(idea_id):
        return False
    try:
        key, open_slots = inputs_key(con, settings, idea_id)
        if not open_slots:
            return False
        sp = get_plan(_record(con, idea_id))
        if sp and sp.get("status") == "planning":
            return False
        if not sp or sp.get("inputs_key") != key:
            mark_stale(con, idea_id, key)               # also records the key, so a failed run is not retried
            return start(con, settings, idea_id, spawn, ask=ask)
        if sp.get("status") == "failed" or sp.get("auto_missing_key") == key:
            return False
        have = {s for s, b in (sp.get("briefs") or {}).items() if not b.get("stale")}
        missing = [s for s in open_slots if str(s) not in have]
        if not missing:
            return False
        _save(con, idea_id, lambda x: x.update(auto_missing_key=key))      # once per input state
        return start(con, settings, idea_id, spawn, slots=missing, ask=ask)
    except Exception:  # noqa: BLE001
        return False


# ---------- Studio chat: edit a slot's prompt before any credits (plan section 10) ----------

EDIT_FIELDS = ("print_size", "shot", "setting", "display", "presentation", "frame_finish", "camera_side",
               "camera_height", "lens", "light_style", "light_from", "shadow", "depth_of_field", "wall", "floor",
               "furniture", "house", "buyer", "props")


class EditRefused(Exception):
    """A chat edit that was not saved (plain reason for the chat reply)."""


def history_entry(b):
    return {"rev": b.get("rev"), "at": b.get("updated"), "edited_by": b.get("edited_by"), "scene": b.get("scene"),
            "brief": {k: v for k, v in b.items() if k not in ("history", "attempts")}}


def _editable(con, settings, idea_id, slot):
    """(record, brief) of an open slot's brief, or EditRefused (no plan, no brief, approved image, running)."""
    from . import production as prod
    idea, lst, rec, folder, arts = prod._ctx(con, settings, idea_id)
    sp = get_plan(rec) or {}
    b = (sp.get("briefs") or {}).get(str(slot))
    if b is None:
        raise EditRefused(f"slot {slot:02d} has no planned scene yet (Re-plan open slots first)")
    srec = (prod._prod(rec)["slots"].get(str(slot)) or {})
    name, _, _ = prod._current_image(folder, slot, srec, rec)
    if name and (rec.get("mockup_approvals") or {}).get(name) == "approved":
        raise EditRefused(f"slot {slot:02d} already has an approved image; its scene is final")
    job = prod.job_state()
    if job["running"] and job["idea_id"] == idea_id and job["slot"] == slot:
        raise EditRefused(f"slot {slot:02d} is being made right now")
    return rec, sp, b


def _others(sp, slot):
    """The set around one slot for check_set: the other briefs (open) + the fixed descriptors (cached)."""
    fixed = {}
    for ent in (sp.get("fixed") or {}).values():
        d = dict(ent.get("descriptor") or {})
        if d.get("slot") is not None:
            fixed[int(d["slot"])] = d
    briefs = {int(s): b for s, b in (sp.get("briefs") or {}).items() if int(s) != slot and s not in
              {str(k) for k in fixed}}
    return briefs, fixed


def edit_brief(con, settings, idea_id, slot, scene=None, fields=None, order=None):
    """The chat's slot_prompt_edit: new scene text and / or field changes for one open slot. Lint failure = refused
    (EditRefused with the reasons); a balance-only failure is saved and returned as a warning. Saves rev+1,
    edited_by chat, the old version into history, and the re-assembled prompt. Returns (brief, warnings)."""
    from . import scene_templates as stp
    rec, sp, old = _editable(con, settings, idea_id, slot)
    raw = {k: old.get(k) for k in KEEP if k in old}
    raw["source"], raw["library_rel"] = "new", None
    for k, v in (fields or {}).items():
        if k not in EDIT_FIELDS:
            raise EditRefused(f"{k} can not be changed from the chat (fields: {', '.join(EDIT_FIELDS)})")
        if k == "wall" and isinstance(v, dict):
            v = {**(old.get("wall") or {}), **v}
            v = {x: v.get(x) for x in ("name", "hex", "treatment")}
        if k == "furniture" and isinstance(v, dict):
            v = {**(old.get("furniture") or {}), **v}
        raw[k] = v
    if scene:
        raw["scene"] = " ".join(str(scene).split())
    ctx = {"slot": slot, "room": old["room"], "decor": old["decor"],
           "ratios": stp.available_rooms(settings).get(old["room"]) or list(rs.RATIOS)}
    b = normalise(raw, ctx)
    b["lint"] = lint(b, ctx)
    if not b["lint"]["pass"]:
        raise EditRefused("; ".join(b["lint"]["why"]))
    b["prompt"] = assemble(b)
    others, fixed = _others(sp, slot)
    chk = check_set({**others, slot: b}, fixed, order or rs.ROOM_SLOTS, max_tight=int(cfg(settings, "planner_max_tight")))
    warn = [f["text"] for f in chk["failures"] if slot in f["slots"]]
    b.update(rev=int(old.get("rev") or 1) + 1, edited_by="chat", stale=False, attempts=old.get("attempts") or [],
             history=(old.get("history") or [])[-4:] + [history_entry(old)], updated=_now())

    def put(x):
        x.setdefault("briefs", {})[str(slot)] = b
        x["cost"] = cost(x["briefs"], (x.get("cost") or {}).get("credits_per_scene"),
                         {s for s, bb in x["briefs"].items() if not bb.get("stale")})
    _save(con, idea_id, put)
    return b, warn


def revert_brief(con, settings, idea_id, slot):
    """The chat's slot_prompt_revert: back to the previous version (saved as a new rev, so nothing is lost)."""
    rec, sp, old = _editable(con, settings, idea_id, slot)
    hist = old.get("history") or []
    if not hist or not hist[-1].get("brief"):
        raise EditRefused(f"slot {slot:02d} has no earlier version")
    prev = dict(hist[-1]["brief"])
    prev.update(rev=int(old.get("rev") or 1) + 1, edited_by="chat", stale=False, reverted_to=hist[-1].get("rev"),
                attempts=old.get("attempts") or [], history=hist[:-1] + [history_entry(old)], updated=_now())
    _save(con, idea_id, lambda x: x.setdefault("briefs", {}).__setitem__(str(slot), prev))
    return prev


def chat_lines(rec, open_slot=None, named=()):
    """Snapshot lines for the Studio chat: one short line per planned slot; the full scene + main fields for the slot
    Tony points at and slots he names."""
    sp = get_plan(rec) or {}
    briefs = sp.get("briefs") or {}
    if not briefs:
        return []
    out = ["", f"Scene plan ({sp.get('status')}; edit a slot's scene before Generate with slot_prompt_edit):"]
    full = {int(open_slot)} if open_slot else set()
    full |= {int(x) for x in named or ()}
    for s in sorted(briefs, key=int):
        b = briefs[s]
        out.append(f"- slot {int(s):02d}: {facts_line(b)} · {b.get('source')} · rev {b.get('rev')}"
                   + (" · edited in chat" if b.get("edited_by") == "chat" else "") + (" · STALE" if b.get("stale") else "")
                   + ("" if (b.get("lint") or {}).get("pass", True) else " · lint FAIL: " + "; ".join(b["lint"]["why"])[:160]))
        if int(s) in full and b.get("source") == "new":
            w = b.get("wall") or {}
            out.append(f"  fields: setting {b.get('setting')}, display {b.get('display')}, {b.get('presentation')} "
                       f"{b.get('frame_finish')}, camera {b.get('camera_side')}/{b.get('camera_height')}/{b.get('lens')}, "
                       f"light {b.get('light_style')} from {b.get('light_from')} ({b.get('shadow')}), wall {w.get('name')} "
                       f"{w.get('hex')} {w.get('treatment')}, insert {b.get('marker')}, furniture {b.get('furniture')}, "
                       f"house {b.get('house')}, buyer {b.get('buyer')}, props {b.get('props')}")
            out.append(f"  scene: {b.get('scene')}")
    return out


# ---------- panel + chat views ----------

def facts_line(b):
    if not b:
        return ""
    if b.get("source") == "library":
        return f"{b.get('print_size') or '-'} · {b.get('shot') or '-'} · library · {rs.RATIO_LABEL.get(b.get('ratio'), b.get('ratio') or '-')}"
    return (f"{b.get('print_size')} · {b.get('shot')} · {(b.get('setting') or '-').replace('_', ' ')} · "
            f"{rs.RATIO_LABEL.get(b.get('ratio'), b.get('ratio'))}")


def card_brief(b):
    if not b:
        return None
    return {"print_size": b.get("print_size"), "shot": b.get("shot"), "setting": b.get("setting"),
            "source": b.get("source"), "library_rel": b.get("library_rel"), "library_name": b.get("library_name"),
            "prompt": b.get("prompt"), "scene": b.get("scene"), "rev": b.get("rev"), "edited_by": b.get("edited_by"),
            "lint": b.get("lint"), "marker": b.get("marker"), "ratio": b.get("ratio"), "stale": b.get("stale"),
            "facts": facts_line(b), "attempts": len(b.get("attempts") or []),
            "drift": (b.get("attempts") or [{}])[-1].get("drift") if b.get("attempts") else None}


def panel_view(sp, running=False):
    if not sp:
        return {"status": "none", "message": "", "running": running}
    chk = sp.get("check") or {}
    return {"status": "planning" if running else sp.get("status"), "message": sp.get("message") or "",
            "rounds": sp.get("rounds"), "failures": [f["text"] for f in chk.get("failures") or []][:6],
            "cost": sp.get("cost"), "stale": any(b.get("stale") for b in (sp.get("briefs") or {}).values()),
            "updated": sp.get("updated"), "running": running}


# ---------- CLI: the free dry run ----------

def dry_run(idea_id, settings=None, ask=None, out=print):
    """Plan one design against a READ-ONLY view of the real DB and print the briefs + the check. Writes nothing."""
    import sqlite3
    import tempfile
    from .db import DB_PATH, load_config
    settings = settings or load_config("settings")
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True, check_same_thread=False)
    con.row_factory = sqlite3.Row
    ask = ask or default_ask(settings)
    with tempfile.TemporaryDirectory() as td:
        ctx = context(con, settings, idea_id, ask_vision=ask, work=td)
        out(f"Design #{idea_id} {ctx['design']['name']}: fixed slots {sorted(ctx['fixed_desc'])}, open slots "
            f"{[o['slot'] for o in ctx['open']]}")
        for s, d in sorted(ctx["fixed_desc"].items()):
            out(f"  fixed {s:02d}: ratio {d.get('ratio')} · {d.get('shot')} ({d.get('art_h_frac')}) · side "
                f"{d.get('camera_side')} · light {d.get('light_from')} · {d.get('presentation')} · wall "
                f"{d.get('wall_family')} · setting {d.get('setting')} · {d.get('house')} · {d.get('buyer')}")
        res = plan_set(ctx, ask, settings, log=lambda m: out("  .. " + m))
    out(f"\nStatus: {res['status']} after {res.get('rounds')} round(s), {res.get('seconds')} s"
        + (f" ({res['message']})" if res.get("message") else ""))
    for s, b in sorted(res.get("briefs", {}).items(), key=lambda x: int(x[0])):
        w = b.get("wall") or {}
        out(f"\n--- slot {s} · {b['room']} · {b['decor']} · {b['source']}"
            + (f" {b.get('library_rel')}" if b.get("library_rel") else ""))
        out(f"    {facts_line(b)} · display {b.get('display')} · {b.get('presentation')} {b.get('frame_finish')}")
        out(f"    camera {b.get('camera_side')} / {b.get('camera_height')} / {b.get('lens')} / {b.get('depth_of_field')}"
            f" · light {b.get('light_style')} from {b.get('light_from')}, {b.get('shadow')} shadows")
        out(f"    wall {w.get('name')} {w.get('hex')} ({w.get('family')}, {w.get('treatment')}) · marker "
            f"{b.get('marker')} · furniture {b.get('furniture')} · {b.get('house')} · buyer {b.get('buyer')}")
        out(f"    lint: {'pass' if b['lint']['pass'] else 'FAIL ' + '; '.join(b['lint']['why'])}")
        if b.get("scene"):
            out(f"    scene: {b['scene']}")
        if b.get("prompt"):
            out(f"    prompt ({len(b['prompt'].split())} words): {b['prompt']}")
    chk = res.get("check") or {}
    out(f"\nBalance check: {'PASS' if chk.get('pass') else 'FAIL'}"
        + "".join(f"\n  - {f['text']} (slots {f['slots']})" for f in chk.get("failures") or []))
    out(f"Cost if generated: {res.get('cost')}")
    return res


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Slot-set planner")
    ap.add_argument("--idea", type=int, required=True)
    ap.add_argument("--dry-run", action="store_true", help="plan and print only; writes nothing")
    a = ap.parse_args()
    if not a.dry_run:
        raise SystemExit("only --dry-run is available from the command line (the Portal saves plans)")
    dry_run(a.idea)
