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
            "planner_rounds": 3, "planner_max_tight": 2, "planner_auto": False,
            # realism addendum (2026-11-20)
            "planner_references": True, "planner_compact": ["frame", "mat"], "planner_max_night": 1,
            "planner_graded_examples": True}

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

# ---------- pv2: the lived-in brief (Pipeline_Docs/Slot_Set_Planner_Realism_Addendum.md, 2026-11-20) ----------
# A brief WITHOUT "pv" (every brief and template saved before the addendum) stays pv1: normalise, lint and assemble
# run their unchanged pv1 code, so old prompts replay byte-identically (tests/test_realism_golden.py).
PV = 2
LIGHT_TYPES = ("hard_diagonal_sun", "morning_soft_sun", "golden_low", "overcast_flat", "rainy_day", "north_light_even",
               "blind_stripes", "dusk_lamp_mix", "night_lamps")
LAMP_TYPES = ("dusk_lamp_mix", "night_lamps")
LIVED_IN = ("tidy", "lived_in", "busy")
WINDOW_COVERINGS = ("venetian_blind", "roller_blind", "roman_blind", "sheer_curtain", "linen_curtains", "heavy_drapes",
                    "shutters", "bare", "no_window_in_view")
WINDOW_VIEWS = ("street", "brick_wall", "trees", "courtyard", "city", "garden", "sky", "night", "none")
PHOTO_STYLES = ("phone_snapshot", "enthusiast_camera", "editorial")
HOUSES_V2 = HOUSES + ("victorian_terrace", "craftsman_bungalow", "condo_1970s", "student_rental", "berlin_altbau",
                      "tokyo_apartment", "texas_ranch", "old_farmhouse", "mediterranean_flat", "prewar_apartment")
HOUSE_REGION = {"london_flat": "uk", "english_cottage": "uk", "victorian_terrace": "uk", "nyc_loft": "us",
                "brownstone": "us", "suburban_colonial": "us", "midcentury_ranch": "us", "modern_farmhouse": "us",
                "southwestern_adobe": "us", "craftsman_bungalow": "us", "condo_1970s": "us", "texas_ranch": "us",
                "old_farmhouse": "us", "prewar_apartment": "us", "student_rental": "uk", "paris_apartment": "europe",
                "scandinavian_house": "europe", "berlin_altbau": "europe", "mediterranean_flat": "europe",
                "coastal_cottage": "uk", "japanese_home": "asia", "tokyo_apartment": "asia"}
FRAME_L_V2 = {**FRAME_L, "bronze_frame": 40, "silver_frame": 72}
FRAME_FOR_V2 = {"frame": FRAME_FOR["frame"] + ("bronze_frame", "silver_frame", "painted_frame"),
                "mat": FRAME_FOR["mat"] + ("bronze_frame", "silver_frame", "painted_frame"),
                "canvas": ("natural_wood_floater",), "canvas_bare": ("none",)}
FRAME_WORDS_V2 = {"oak_frame": "a thin natural light oak frame", "walnut_frame": "a thin warm walnut frame",
                  "black_frame": "a thin black frame with a soft satin finish", "white_frame": "a thin white painted frame",
                  "gold_frame": "a thin antique gold frame", "bronze_frame": "a thin dark bronze metal frame",
                  "silver_frame": "a thin brushed silver frame"}
LIGHT_TYPE_STYLE = {"hard_diagonal_sun": "crisp_direct", "blind_stripes": "dappled", "golden_low": "golden_low",
                    "morning_soft_sun": "soft_direct", "overcast_flat": "soft_even", "rainy_day": "soft_even",
                    "north_light_even": "soft_even", "dusk_lamp_mix": None, "night_lamps": None}
HARD_LIGHT = ("hard_diagonal_sun", "blind_stripes")
WARM_SUN = ("golden_low", "morning_soft_sun")
LIGHT_TYPE_TEXT = {
    "hard_diagonal_sun": "Light: hard direct sun through the window cuts a crisp diagonal band of light across the wall "
                         "and floor; sharp-edged shadows.",
    "morning_soft_sun": "Light: clear morning sun, pale and fresh, falls softly into the room; gentle, clearly "
                        "visible shadows.",
    "golden_low": rs.LOOK_AXES["light_style"]["golden_low"][1].replace("Light style:", "Light:"),
    "overcast_flat": "Light: a grey overcast day; flat, cool, even window light, soft open shadows under the "
                     "furniture, slightly muted colours.",
    "rainy_day": "Light: a rainy afternoon; dim cool daylight, a few raindrops on the window glass, a lamp on in the "
                 "room.",
    "north_light_even": "Light: steady north daylight, cool and even all day, with soft, clearly visible shadows.",
    "blind_stripes": "Light: low sun through half-open venetian blinds lays parallel stripes of light and shadow across "
                     "the wall beside the frame and the floor.",
    "dusk_lamp_mix": "Light: dusk; deep blue light in the window and a warm lamp switched on in the room, soft shadows "
                     "from the lamp.",
    "night_lamps": "Light: evening after dark; the room is lit by its own lamps in warm pools with soft shadows; the "
                   "artwork is lit evenly by a nearby lamp."}
LIGHT_FROM_C = {"left": "It comes from the left.", "right": "It comes from the right.",
                "front": "It comes from a window facing the art wall.", "behind_camera": "It comes from behind the camera."}
COVERING_TEXT = {"venetian_blind": "a venetian blind", "roller_blind": "a plain roller blind",
                 "roman_blind": "a linen roman blind", "sheer_curtain": "sheer white curtains",
                 "linen_curtains": "linen curtains", "heavy_drapes": "heavy floor-length drapes",
                 "shutters": "painted wooden shutters", "bare": "no covering"}
VIEW_TEXT = {"street": "a quiet street", "brick_wall": "the neighbour's brick wall", "trees": "trees",
             "courtyard": "a small courtyard", "city": "city rooftops", "garden": "a garden", "sky": "open sky",
             "night": "the dark night", "none": ""}
PHOTO_STYLE_TEXT = {
    "phone_snapshot": "Photo: a careful phone photo by the owner: natural exposure, true colours, slight grain, framed "
                      "by hand with level verticals, unretouched; the print area stays clean and flat.",
    "enthusiast_camera": "Photo: taken by the owner with a simple mirrorless camera: natural exposure, true colours, "
                         "framed by hand with level verticals, unretouched; the print area stays clean and flat.",
    "editorial": "Photo: a calm interiors photograph, natural and unretouched."}
# rotating true-scale cue for tight shots (cm of the object's height); a cue already in the props is preferred
SCALE_CUES = (("light switch plate", r"switch", 11.4), ("power outlet", r"outlet|socket", 11.4),
              ("paperback", r"paperback|book", 18.0), ("mug", r"mug|cup", 9.5),
              ("table lamp base", r"lamp", 20.0), ("door handle", r"handle", 12.0))
CAMERA_SIDE_C = {"left": "from slightly left, 10-15 degrees off square", "right": "from slightly right, 10-15 degrees "
                 "off square", "front": "square-on to the frame"}
CAMERA_HEIGHT_C = {"surface": "level with the surface under the piece", "low": "at knee to hip height",
                   "seated": "at seated eye height (110 cm)", "counter": "at furniture-top height (90 cm)",
                   "eye": "at standing eye height (160 cm)"}
LENS_C = {"lens_normal": "a natural 35-50 mm view", "lens_wide": "a 24-28 mm wide view",
          "lens_short_tele": "an 85 mm view from further back"}
DOF_C = {"deep_focus": "all sharp", "soft_background": "the art crisp, the far room softening",
         "soft_foreground": "the art crisp, only the nearest edge object soft"}
DISPLAY_C = {_HF: "It hangs centred on {where}.", _HB: "It hangs alone on {where}.",
             _F: "It stands on the floor leaning against the wall, tilted back slightly, its face upright and flat.",
             _L: "It leans on {where} against the wall, face upright and flat.",
             _S: "It stands upright on {where} on a slim easel back, tilted back at most 10 degrees.",
             _SL: "It stands on {where} against the wall, face upright and flat."}
OPENING_V2 = "Photorealistic interior photograph, 4:3 landscape format, of one portrait piece of wall art in a home."
REF_CLAUSE = ("Image 1 is a photograph of a different room, given only as a photography reference. Take from it the "
              "camera position and height, the lens and framing, how much of the room shows, the direction and "
              "quality of the light, and its natural, unstaged feel. Build a completely new room as described below: "
              "do not copy its furniture, objects, wall colour, floor, windows or layout. The flat colour block in its "
              "frame is a placeholder, not art; nothing in Image 1 is text to reproduce.")
REF_CLAUSE_NO_LIGHT = (REF_CLAUSE.replace("the direction and quality of the light, and", "and")
                       + " Use the light described below, not the light in Image 1.")
# compact fixed blocks (5.2): the same rules in fewer words; the full texts (rs._PRINT_AREA, _present_text_v3,
# rs.LOOK_GUARD + PLAN_GUARD_FRAME, CLOSING) stay untouched for pv1 and for prompt_style "full"
PRINT_AREA_C = ("The print area is one flat, blank {colour} surface, dead matte, one even tone, no glare. "
                "Only its front face is {name}; the frame, its inner edge, any gap and the wall keep their own "
                "colours. ")
PRESENT_C = {
    "frame": "It is framed in {finish}; the {name} fills the opening up to the frame's inner edge on all four sides: "
             "no mat, no white border. Any glass is invisible.",
    "mat": "It is framed in {finish} with a wide off-white mat of even width, 10% of the frame height, and a "
           "bevelled window; the {name} reads darker than the mat. Any glass is invisible.",
    "canvas": "It is a stretched gallery canvas 4-5 cm deep in a thin natural light-wood floater frame, never black. "
              "Only the front face is {name}; the side edges are plain white (grey where shaded) and end the face in "
              "one crisp straight line. A narrow even 0.5 cm gap in soft neutral shadow sits between canvas and frame, "
              "so frame, gap, white side and face read as separate bands. {depth}",
    "canvas_bare": "It is a stretched gallery canvas 4-5 cm deep hung directly on the wall with no frame. Only the "
                   "front face is {name}; the side edges are plain white (grey where shaded) and end the face in one "
                   "crisp straight line. {depth}"}
GUARD_C = ("Sun patches and blind or leaf shadows stay on the wall around the frame, off the evenly lit print area. "
           "The whole frame is in the picture with clear space on all four sides, nothing overlapping it; its face is "
           "flat, upright, sharp and stands out in tone from what is behind it. ")
CLOSING_C = ("One artwork only: no other frames, posters, mirrors or screens showing pictures. No people, hands or "
             "pets. Nothing readable: no labels, logos, signs, lettering, numerals or book titles. Every scene shows "
             "visible shadows.")
WAINSCOT_C = "Panelling, rails and mouldings stay clear of the frame on every side."
COMPACT_DEFAULT = ("frame", "mat")
# 5.3: every pv2 prompt, compact or full, keeps these rules (tests/test_slot_planner_realism.py)
RULES = [("matte", r"matte"), ("even", r"\beven"), ("front face", r"front face"), ("own colour", r"own (\w+ )?colou?rs?"),
         ("clear space", r"clear space on all four sides"), ("overlap", r"overlap"), ("sharp", r"sharp"),
         ("upright", r"upright"), ("flat", r"\bflat\b"), ("stands out", r"stands out"), ("no people", r"No people"),
         ("pets", r"pets"), ("book titles", r"book titles"), ("no other frames", r"no other (picture )?frames"),
         ("mirrors", r"mirrors"), ("shadows", r"shadows"), ("4:3", r"4:3"), ("portrait", r"portrait")]
RULES_PRESENT = {"frame": [r"inner edge", r"no mat"], "mat": [r"even width", r"bevel"],
                 "canvas": [r"white", r"gap", r"floater", r"never black"], "canvas_bare": [r"no frame", r"white"]}
CAMERA_WORDS = re.compile(r"\b(camera|lens|\d{2,3}\s?mm|close-?up|wide shot|tight shot|medium shot|angle|shot from|"
                          r"from the (left|right))\b", re.I)
TEXT_CARRIERS = re.compile(r"\b(calendar|newspaper|magazines?|cereal box|packaging|sticky notes?|whiteboard|chalkboard|"
                           r"price tags?|receipts?|posters?)\b", re.I)
QUALIFIED = (("books", r"\bbooks?\b", r"plain|spines? (turned )?away|face down|unmarked|cloth-bound|linen-covered"),
             ("envelopes", r"\b(envelopes?|letters|mail)\b", r"face down|plain"),
             ("phone", r"\bphones?\b", r"face down|screen off"), ("laptop", r"\blaptops?\b", r"closed"),
             ("clock", r"\bclocks?\b", r"no numerals|plain face"), ("drawing", r"\bdrawings?\b", r"no (letters|words)"),
             ("bottles", r"\b(bottles?|jars?)\b", r"plain|unlabell?ed"))
# pv2 asks for these everyday phrases itself; they are not people (BANNED still catches "hands", "a face", ...)
BANNED_OK = re.compile(r"\b(hand-me-downs?|second-hand|hand-?made|hand-painted|hand-?finished|by hand|face[- ]down|"
                       r"faces? (away|down)|(clock|watch) face|plain face)\b", re.I)
NIGHT_WORDS = re.compile(r"\b(night|after dark|lamplight)\b", re.I)
SUN_WORDS = re.compile(r"\b(sun|sunlit|sunbeams?|sunlight)\b", re.I)
PROP_FAMILIES = {   # family -> (regex over scene + props, max per listing) (4.1)
    "dried_stems": (r"dried (stems?|grass(es)?|flowers?|wheat|thistle|lavender)|pampas|bunny tails?|wheat stems?", 1),
    "rattan_cane": (r"rattan|cane|wicker|woven seat", 1),
    "boucle": (r"bouc?l[eé]|teddy fabric|sherpa", 1),
    "wood_toy": (r"wood(en)? (blocks?|toys?|cubes?|beads?)|stacking (toy|rings?)", 1),
    "candles": (r"candles?|candlesticks?|tealights?", 1),
    "knit_throw": (r"(chunky )?knit(ted)? (throw|blanket)", 1),
    "plants": (r"plants?|fern|monstera|fiddle[- ]leaf|pothos|ficus|olive tree|succulents?|cactus|palm", 2),
    "stoneware": (r"stoneware|ceramic (vase|cup|jug|bowl)|bud vase|clay (vase|pot)|pottery", 2),
    "book_stack": (r"stack(ed|s)? of books|books stacked|coffee[- ]table books", 2),
    "brass_object": (r"(brass|bronze) (figure|object|candlestick|tray|bowl|sculpture)", 2),
    "woven_basket": (r"woven baskets?|seagrass|jute basket", 1),
    "eucalyptus_branch": (r"eucalyptus|(olive|blossom|cherry) branch(es)?", 1)}
_PROP_RX = {k: re.compile(rf"\b({rx})\b", re.I) for k, (rx, _) in PROP_FAMILIES.items()}
COMP_KEYS = ("display", "shot", "camera_side", "camera_height", "lens", "light_from", "frame_finish")
DISPLAY_GROUP = {_HF: "hung", _HB: "hung", _L: "surface", _S: "surface", _SL: "shelf", _F: "floor"}
GRADES = ("A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D", "F")
GRADE_SCORE = {"A+": 4.3, "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7, "C+": 2.3, "C": 2.0, "C-": 1.7, "D": 1.0,
               "F": 0.0}


def prop_families(text):
    """Sorted prop-family names present in a scene + props text (4.1)."""
    return sorted(k for k, rx in _PROP_RX.items() if rx.search(text or ""))


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
    lab = lab_of_hex(hx)
    if wall_family(lab) in WARM_FAMILIES:
        return "blue"
    L, C, h = lch(lab)          # tolerance (Tony 2026-11-20): a visibly warm pale wall (sand, tan, beige, warm greige)
    return "blue" if (C >= 8.5 and 35 <= h <= 100 and L >= 55) else "orange"   # is near the insert; whites/creams stay orange


# ---------- normalise + lint one brief ----------

KEEP = ("slot", "source", "library_rel", "print_size", "shot", "setting", "display", "presentation", "frame_finish",
        "camera_side", "camera_height", "lens", "light_style", "light_from", "shadow", "depth_of_field", "wall", "floor",
        "furniture", "house", "buyer", "props", "scene")      # no "marker" (code picks it) and no rationale field


KEEP_V2 = KEEP + ("occupant", "lived_in", "light_type", "window", "photo_style", "reference", "reference_flip",
                  "frame_colour")


def is_v2(raw):
    """A pv2 brief: marked pv 2, or a planner reply in the pv2 schema (occupant / light_type)."""
    return isinstance(raw, dict) and (raw.get("pv") == PV or "light_type" in raw or "occupant" in raw)


def normalise(raw, slot_ctx):
    """A model brief -> a clean brief: unknown keys dropped (no rationale field survives), room / decor from the slot
    plan, ratio + scale from the print size, wall family + marker from the wall hex. Never raises.
    A pv2 brief (is_v2) also gets the lived-in fields; light_style + shadow derived from light_type."""
    if is_v2(raw):
        return _normalise_v2(raw, slot_ctx)
    return _normalise_v1(raw, slot_ctx)


def _normalise_v2(raw, slot_ctx):
    b = _normalise_v1(raw, slot_ctx)
    b["pv"] = PV
    b["props"] = [str(p)[:80] for p in (raw.get("props") or []) if str(p).strip()][:8]
    occ = " ".join(str(raw.get("occupant") or "").split())
    b["occupant"] = occ[:240]
    for k in ("lived_in", "light_type", "photo_style"):
        b[k] = raw.get(k)
    w = raw.get("window") if isinstance(raw.get("window"), dict) else {}
    b["window"] = {"covering": w.get("covering"), "view": w.get("view") or "none"}
    ref = raw.get("reference")
    b["reference"] = str(ref).strip().zfill(4) if ref not in (None, "", "none") else None
    b["reference_flip"] = bool(raw.get("reference_flip"))
    fc = raw.get("frame_colour") if isinstance(raw.get("frame_colour"), dict) else None
    b["frame_colour"] = None
    if fc:
        try:
            lab = lab_of_hex(fc.get("hex"))
            b["frame_colour"] = {"name": str(fc.get("name") or "")[:30],
                                 "hex": "#" + re.sub(r"[^0-9a-fA-F]", "", fc["hex"]).upper(),
                                 "lab": [round(v, 1) for v in lab]}
        except ValueError:
            b["frame_colour"] = {"name": str(fc.get("name") or "")[:30], "hex": fc.get("hex"), "lab": None}
    lt = b.get("light_type")
    if lt in LIGHT_TYPES:
        b["light_style"] = LIGHT_TYPE_STYLE[lt]
        b["shadow"] = "hard" if lt in HARD_LIGHT else "soft"
    else:
        b["light_style"] = None
    b.setdefault("depth_of_field", "deep_focus")
    if b.get("depth_of_field") not in DOFS:
        b["depth_of_field"] = "deep_focus"
    return b


def display_group(display):
    return DISPLAY_GROUP.get(display)


def ref_fits(entry, b):
    """Does a reference fit a brief: same display group, reference shot within one step of the brief's shot."""
    t = entry.get("tags") or {}
    if t.get("display_group") != display_group(b.get("display")):
        return False
    if t.get("shot") in SHOT_ORDER and b.get("shot") in SHOT_ORDER:
        return abs(SHOT_ORDER.index(t["shot"]) - SHOT_ORDER.index(b["shot"])) <= 1
    return True


def apply_reference(b, entry):
    """Derive camera_side (flip swaps left / right), camera_height and lens from the reference (2.1), fixed up so the
    pv1 camera rules still hold; ref_use = camera, lens, composition, character (+ light when the brief's light_type
    equals the reference's tag). Without a reference the model's camera fields stay."""
    if not entry:
        b["ref_use"] = []
        return b
    t = entry.get("tags") or {}
    side = entry.get("camera_side") or "front"
    if b.get("reference_flip") and side in ("left", "right"):
        side = "right" if side == "left" else "left"
    b["camera_side"] = side
    h = t.get("camera_height") if t.get("camera_height") in CAMERA_HEIGHTS else b.get("camera_height")
    disp = b.get("display")
    if h == "surface" and disp not in SURFACE_DISPLAYS:
        h = "counter" if disp == _HF else "eye"
    if h == "counter" and disp not in SURFACE_DISPLAYS + (_HF,):
        h = "eye"
    if h == "low" and disp in HUNG and b.get("shot") == "tight":
        h = "eye"
    b["camera_height"] = h or "eye"
    lens = t.get("lens") if t.get("lens") in LENSES else (b.get("lens") or "lens_normal")
    if lens == "lens_wide" and b.get("shot") == "tight":
        lens = "lens_normal"
    if lens == "lens_short_tele" and b.get("shot") == "wide":
        lens = "lens_normal"
    b["lens"] = lens
    use = ["camera", "lens", "composition", "character"]
    if b.get("light_type") and b.get("light_type") == t.get("light_type"):
        use.append("light")
    b["ref_use"] = use
    return b


def _normalise_v1(raw, slot_ctx):
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
    be generated. pv2 briefs get the realism rules on top (_lint_v2); pv1 briefs exactly the old rules."""
    if b.get("pv") == PV:
        return _lint_v2(b, slot_ctx, settings)
    return _lint_v1(b, slot_ctx, settings)


def _lint_v2(b, slot_ctx=None, settings=None):
    """pv2 (realism addendum 3.4): the pv1 rules with the pv2 lists (houses, frame finishes, props per shot, light_type
    instead of light_style) + occupant, lived-in, window, photo style, camera words, text carriers, qualified objects,
    light words vs light type, reference fit, painted frames."""
    why = []
    ctx = slot_ctx or {}
    if b.get("source") == "library":
        return {"pass": bool(b.get("library_rel")), "why": [] if b.get("library_rel") else ["library brief without a template"]}

    def need(key, allowed, label=None):
        if b.get(key) not in allowed:
            why.append(f"{label or key} {b.get(key)!r} is not one of {', '.join(map(str, allowed))}")
            return False
        return True
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
    shot, disp, height = b.get("shot"), b.get("display"), b.get("camera_height")
    if b.get("scale") and shot in SHOT_ORDER and shot not in SHOT_OK[b["scale"]]:
        why.append(f"a {b['print_size']} ({b['scale']}) print is never shown as a {shot} shot "
                   f"(allowed: {', '.join(SHOT_OK[b['scale']])})")
    w = b.get("wall") or {}
    if need("presentation", PRESENTATIONS):
        if b["presentation"] in ("canvas", "canvas_bare") and b.get("scale") == "small":
            why.append("canvas only for medium and large prints; small prints get a frame or a mat")
        need("frame_finish", FRAME_FOR_V2[b["presentation"]], f"frame finish for {b['presentation']}")
    for key, allowed in (("camera_side", CAMERA_SIDES), ("camera_height", CAMERA_HEIGHTS), ("lens", LENSES),
                         ("light_type", LIGHT_TYPES), ("light_from", LIGHT_FROM), ("depth_of_field", DOFS),
                         ("house", HOUSES_V2), ("buyer", BUYERS), ("marker", MARKERS), ("lived_in", LIVED_IN),
                         ("photo_style", PHOTO_STYLES)):
        need(key, allowed)
    win = b.get("window") or {}
    if win.get("covering") not in WINDOW_COVERINGS:
        why.append(f"window covering {win.get('covering')!r} is not one of {', '.join(WINDOW_COVERINGS)}")
    if win.get("view") not in WINDOW_VIEWS:
        why.append(f"window view {win.get('view')!r} is not one of {', '.join(WINDOW_VIEWS)}")
    lt = b.get("light_type")
    if lt == "night_lamps" and win.get("covering") != "no_window_in_view" and win.get("view") != "night":
        why.append("an evening lamp-lit scene shows a night view or no window")
    if lt == "blind_stripes" and win.get("covering") != "venetian_blind":
        why.append("blind stripes only with a venetian blind window covering")
    occ = b.get("occupant") or ""
    if not occ:
        why.append("no occupant line (who lives there, for planning only)")
    elif len(occ.split()) > 25:
        why.append(f"the occupant line has {len(occ.split())} words (at most 25)")
    fu = b.get("furniture") or {}
    if fu.get("style") not in FURNITURE_STYLES:
        why.append(f"furniture style {fu.get('style')!r} is not one of the listed styles")
    if fu.get("family") not in FURNITURE_FAMILIES:
        why.append(f"furniture colour family {fu.get('family')!r} is not one of the listed families")
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
    cap = {"tight": 3, "medium": 6, "wide": 8}.get(shot, 6)
    if shot == "tight" and not 1 <= len(props) <= 3:
        why.append(f"a tight shot has 1 to 3 small props ({len(props)} given)")
    elif len(props) > cap:
        why.append(f"a {shot} shot has at most {cap} props ({len(props)} given)")
    if b.get("lived_in") == "busy":
        if shot == "tight":
            why.append("a busy, lived-in scene needs a medium or wide shot")
        elif len(props) < 4:
            why.append(f"a busy scene names at least 4 everyday things ({len(props)} given)")
    fin = b.get("frame_finish")
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
        fl = FRAME_L_V2.get(fin)
        if fin == "painted_frame":
            fc = b.get("frame_colour") or {}
            if not fc.get("lab"):
                why.append("a painted frame needs frame_colour {name, hex}")
            else:
                fl = fc["lab"][0]
                mk = lab_of_rgb(MARKER_RGB.get(b.get("marker") or "orange"))
                hue_d = abs((lch(fc["lab"])[2] - lch(mk)[2] + 180) % 360 - 180)
                if de2000(fc["lab"], mk) < 25 or (lch(fc["lab"])[1] > 15 and hue_d < 30):
                    why.append(f"a {fc.get('name') or 'painted'} frame is too close to the {b.get('marker')} insert "
                               "colour")
        if fl is not None and abs(fl - lab[0]) < 15:
            why.append(f"the {str(fin).replace('_', ' ')} does not stand out from the wall in tone (wall L* {lab[0]:.0f})")
        if w["family"] == "blush_pink" and b.get("presentation") in ("frame", "mat") and \
                fin not in ("black_frame", "walnut_frame", "bronze_frame"):
            why.append("blush walls only with a black, walnut or bronze frame")
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
        hit = sorted({m.group(0).lower() for m in BANNED.finditer(BANNED_OK.sub(" ", txt))})
        if hit:
            why.append(f"the {label} names {', '.join(hit)} (no people, pets, readable text, other frames or reasons)")
    alltxt = scene + " " + " ".join(props)
    cam = sorted({m.group(0).lower() for m in CAMERA_WORDS.finditer(scene)})
    if cam:
        why.append(f"the scene names the camera or light direction ({', '.join(cam)}); those come from the fields")
    car = sorted({m.group(0).lower() for m in TEXT_CARRIERS.finditer(alltxt)})
    if car:
        why.append(f"the scene names things that carry text ({', '.join(car)})")
    for sent in re.split(r"(?<=[.;!?])\s+", alltxt):
        for label, obj, qual in QUALIFIED:
            if re.search(obj, sent, re.I) and not re.search(qual, sent, re.I):
                why.append(f"{label} must be described as unreadable in the same sentence ({qual.replace('|', ' / ')})")
    if NIGHT_WORDS.search(scene) and lt not in LAMP_TYPES:
        why.append("night or lamplight words with a daylight light type")
    if SUN_WORDS.search(scene) and lt in ("overcast_flat", "rainy_day", "night_lamps"):
        why.append(f"sun words with the {str(lt).replace('_', ' ')} light type")
    ref = b.get("reference")
    refs = ctx.get("refs")
    if ref and refs is not None:
        e = next((r for r in refs if r.get("id") == ref), None)
        if e is None:
            why.append(f"reference {ref} is not a usable reference")
        elif not ref_fits(e, b):
            t = e.get("tags") or {}
            why.append(f"reference {ref} ({t.get('display_group')}, {t.get('shot')}) does not fit a "
                       f"{display_group(disp)} {shot} slot")
    return {"pass": not why, "why": list(dict.fromkeys(why))}


def _lint_v1(b, slot_ctx=None, settings=None):
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


def assemble(b, ref=True):
    """The full prompt for a NEW brief: the planner's scene + fixed blocks (portrait frame in a 4:3 photograph, shot
    and scale, camera, light, wall, the marker print area + presentation, guards). Deterministic.
    A brief without "pv" (every brief saved before 2026-11-20) -> _assemble_v1, byte-identical. pv2 -> _assemble_v2;
    ref=False gives the text-only prompt (no reference clause) for when the reference image is not sent."""
    if b.get("pv") == PV:
        return _assemble_v2(b, ref)
    return _assemble_v1(b)


def prompt_style(b):
    """compact | full for a pv2 brief (saved on the brief by finish; compact for frame / mat by default)."""
    return b.get("prompt_style") or ("compact" if b.get("presentation") in COMPACT_DEFAULT else "full")


def scale_cue(b):
    """(name, height cm) of the true-scale cue for a tight shot: one already in the props, else rotated by slot."""
    txt = " ".join(b.get("props") or []) + " " + (b.get("scene") or "")
    for name, rx, cm in SCALE_CUES:
        if re.search(rf"\b({rx})", txt, re.I):
            return name, cm
    name, _, cm = SCALE_CUES[int(b.get("slot") or 0) % len(SCALE_CUES)]
    return name, cm


def shot_text_c(b):
    w, h = size_in(b["print_size"])
    ow, oh = _outer(b)
    lo, hi = SHOTS[b["shot"]]["frac"]
    phrase = SETTINGS[b["setting"]][0]
    t = (f"Framing: a {b['shot']} shot; a {_fmt(w)} x {_fmt(h)} in print, about {round(ow * 2.54)} x "
         f"{round(oh * 2.54)} cm as shown, filling {lo}-{hi}% of the picture height. "
         + DISPLAY_C[b["display"]].format(where=hung_where(phrase) if b["display"] == _HF else phrase))
    if b["shot"] == "tight":
        name, cm = scale_cue(b)
        t += f" A {name} nearby is about {round(100 * cm / (oh * 2.54))}% as tall as the piece (true scale)."
    elif b["shot"] == "medium":
        t += " A desk or dresser top stands about 75 cm high."
    else:
        t += " A sofa back stands about 85 cm high, a door 200 cm."
    return t


def camera_text_c(b):
    return (f"Camera: {CAMERA_SIDE_C[b['camera_side']]}, {CAMERA_HEIGHT_C[b['camera_height']]}, "
            f"{LENS_C[b['lens']]}, {DOF_C[b['depth_of_field']]}, verticals level.")


def window_text(b):
    w = b.get("window") or {}
    cov = w.get("covering")
    if not cov or cov == "no_window_in_view":
        return ""
    view = VIEW_TEXT.get(w.get("view") or "none", "")
    return (f"The window has {COVERING_TEXT[cov]}" + (f"; outside, {view}." if view else "."))


def ref_clause(b):
    """The reference clause (2.2) for a brief whose reference image is sent: with or without the reference's light."""
    return REF_CLAUSE if "light" in (b.get("ref_use") or []) else REF_CLAUSE_NO_LIGHT


def present_text_c(b):
    """Compact presentation sentences (5.2), marker-coloured."""
    kind, name = b["presentation"], b.get("marker") or "orange"
    fin = b.get("frame_finish")
    if fin == "painted_frame":
        finish = f"a thin {(b.get('frame_colour') or {}).get('name') or 'painted'} painted frame"
    else:
        finish = FRAME_WORDS_V2.get(fin, "a thin frame")
    lean = b.get("display") in SURFACE_DISPLAYS + (_F,)
    if kind == "canvas":
        depth = ("It leans against the wall and casts a natural shadow on the wall and the surface below." if lean
                 else "It stands off the wall by its depth and casts a natural shadow on the wall.")
    else:
        depth = ("It leans against the wall and casts a soft natural shadow." if lean else
                 "It stands off the wall by its depth and casts a soft natural shadow on the wall.")
    return PRESENT_C[kind].format(finish=finish, name=name, depth=depth)


def _assemble_v2(b, ref=True):
    """pv2 (realism addendum 3.5): opening -> reference clause (when sent) -> scene -> framing / scale -> camera ->
    light type -> window -> photo style -> wall -> print area + presentation -> guards -> closing. The last three are
    the compact texts or the untouched full ones (prompt_style)."""
    style = prompt_style(b)
    marker = b.get("marker", "orange")
    lt = b["light_type"]
    light = LIGHT_TYPE_TEXT[lt]
    if lt not in LAMP_TYPES and b.get("light_from") in LIGHT_FROM_C:
        light += " " + LIGHT_FROM_C[b["light_from"]]
    wall = f"Walls: {b['wall']['name'] or 'a calm wall colour'}. " + WALL_TREATMENT_TEXT[b["wall"]["treatment"]]
    parts = [OPENING_V2, ref_clause(b) if ref and b.get("reference") else "", b["scene"]]
    if style == "compact":
        parts += [shot_text_c(b), camera_text_c(b), light, window_text(b), PHOTO_STYLE_TEXT[b["photo_style"]], wall]
        if b["wall"]["treatment"] in ("panelled", "wainscot_lower"):
            parts.append(WAINSCOT_C)
        t = " ".join(p.strip() for p in parts if p) + " "
        colour = rs.INSERT_COLOUR if marker == "orange" else MARKER_WORDS[marker]
        t += PRINT_AREA_C.format(colour=colour, name=marker) + present_text_c(b) + " " + GUARD_C + CLOSING_C
        return t
    phrase = SETTINGS[b["setting"]][0]
    parts += [shot_text(b), DISPLAY_TEXT[b["display"]].format(where=hung_where(phrase) if b["display"] == _HF else phrase),
              camera_text_c(b), light, window_text(b), PHOTO_STYLE_TEXT[b["photo_style"]], wall]
    t = " ".join(p.strip() for p in parts if p) + " "
    if b["wall"]["treatment"] in ("panelled", "wainscot_lower"):
        t += rs.WAINSCOT_RULE + " "
    closing = CLOSING
    if lt in LAMP_TYPES + ("rainy_day",):          # the lamp is part of this light; the old lamp sentence would fight it
        closing = CLOSING.replace(" No lamps unless the setting clearly needs one.", "")
    t += print_area_text(marker) + _present_text_v3_pv2(b) + " " + rs.LOOK_GUARD + PLAN_GUARD_FRAME + closing
    return t


def _present_text_v3_pv2(b):
    """The full presentation text for a pv2 brief: _present_text_v3 with the pv2 frame finishes worded."""
    fin = b.get("frame_finish")
    if fin in rs.LOOK_AXES["frame_finish"] or b["presentation"] in ("canvas", "canvas_bare"):
        return _present_text_v3(b)
    t = _present_text_v3(dict(b, frame_finish=None))
    words = (f"a thin {(b.get('frame_colour') or {}).get('name') or 'painted'} painted frame"
             if fin == "painted_frame" else FRAME_WORDS_V2.get(fin, "a thin frame"))
    return t.replace("The artwork is framed in a thin frame (natural oak, walnut or brass most of the time; black only "
                     "occasionally, when it clearly suits the room).", f"The artwork is framed in {words}.") \
            .replace("The artwork is framed in a refined thin frame with", f"The artwork is framed in {words} with")


def _assemble_v1(b):
    """pv1 prompt (the 2026-11-19 function body, unchanged)."""
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
            "scene": b.get("scene") or "",
            # realism addendum 3.5 / 4 (new rules only; SIM_W and similarity() are unchanged)
            "pv": b.get("pv"), "light_type": b.get("light_type"), "warm_sun": _warm_sun(b),
            "window_covering": (b.get("window") or {}).get("covering"), "lived_in": b.get("lived_in"),
            "photo_style": b.get("photo_style"), "reference": b.get("reference"),
            "reference_reused": b.get("reference_reused"), "region": HOUSE_REGION.get(b.get("house")),
            "frame_finish": b.get("frame_finish"),
            "prop_families": prop_families((b.get("scene") or "") + " " + " ".join(b.get("props") or []))
            if (b.get("scene") or b.get("props")) else None}


def _warm_sun(b):
    if b.get("light_type"):
        return b["light_type"] in WARM_SUN
    if b.get("light_style"):
        return b["light_style"] in ("soft_direct", "golden_low")
    return None


def comp_sig(d):
    return [d.get(k) for k in COMP_KEYS]


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


def _limit(fail, order, opens, rule, label, with_it, lim, pts, fixed_note=True):
    """A set-wide repeat limit (realism addendum 4.2): `with_it` = slots (fixed + open) that have the thing. More than
    `lim` -> the later OPEN slots in listing order beyond the limit are blamed; when the fixed slots alone already
    reach the limit, every open slot adding more is blamed (never a failure on fixed slots alone)."""
    if len(with_it) <= lim:
        return
    rank = {s: i for i, s in enumerate(order)}
    fixed_with = sorted((s for s in with_it if s not in opens), key=lambda s: rank.get(s, 99))
    open_with = sorted((s for s in with_it if s in opens), key=lambda s: rank.get(s, 99))
    if not open_with:
        return
    if len(fixed_with) >= lim:
        blamed = open_with
        text = (f"{label} already appears in fixed slot{'s' if len(fixed_with) > 1 else ''} "
                f"{', '.join(map(str, fixed_with))}: none in open slots (remove it from slot"
                f"{'s' if len(blamed) > 1 else ''} {', '.join(map(str, blamed))})")
    else:
        blamed = open_with[lim - len(fixed_with):]
        where = ", ".join(map(str, sorted(with_it, key=lambda s: rank.get(s, 99))))
        text = (f"{label} appears in slots {where}; at most {lim} in the listing: remove it from slot"
                f"{'s' if len(blamed) > 1 else ''} {', '.join(map(str, blamed))}")
    fail(rule, text, blamed, pts)


def _repeat_limits(allv, opens, fix, order, fail, max_night=None):
    """The realism repeat limits (4.1 + 4.2) over the listing (fixed + open). Unknown (None) never counts."""
    order = list(order) + [s for s in sorted(allv) if s not in order]
    for fam, (_, lim) in PROP_FAMILIES.items():
        _limit(fail, order, opens, "props", fam.replace("_", " "),
               [s for s, d in allv.items() if fam in (d.get("prop_families") or [])], lim, 1.0)
    gold = [s for s, d in allv.items() if d.get("light_type") == "golden_low" or
            (d.get("light_type") is None and d.get("light_style") == "golden_low")]
    _limit(fail, order, opens, "light", "warm golden low sun", gold, 1, 0.7)
    _limit(fail, order, opens, "light", "warm sun (golden or soft morning sun)",
           [s for s, d in allv.items() if d.get("warm_sun")], 2, 0.7)
    recipes = {}
    for s, d in allv.items():
        k = (d.get("light_type") or d.get("light_style"), d.get("light_from"), d.get("shadow"))
        if all(k):
            recipes.setdefault(k, []).append(s)
    for k, ss in recipes.items():
        _limit(fail, order, opens, "light", f"the same light ({k[0].replace('_', ' ')} from the {k[1]}, {k[2]} "
                                            "shadows)", ss, 2, 0.7)
    cams = {}
    for s, d in allv.items():
        k = (d.get("camera_side"), d.get("camera_height"), d.get("lens"))
        if all(k):
            cams.setdefault(k, []).append(s)
    for k, ss in cams.items():
        _limit(fail, order, opens, "camera", f"the same camera ({k[0]}, {k[1]} height, {k[2].replace('_', ' ')})",
               ss, 2, 0.7)
    rank = {s: i for i, s in enumerate(order)}
    keys = sorted(allv, key=lambda s: rank.get(s, 99))
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            if a not in opens and b not in opens:
                continue
            sa, sb = comp_sig(allv[a]), comp_sig(allv[b])
            same = sum(1 for x, y in zip(sa, sb) if x is not None and x == y)
            if same >= 5:
                later = b if b in opens else a
                fail("composition", f"slots {a} and {b} are the same photograph ({same} of 7: display, shot, camera "
                                    f"side, height, lens, light side, frame finish); change slot {later}", [later], 1.0)
    refs = {}
    for s in keys:
        d = allv[s]
        if d.get("reference") and not d.get("reference_reused"):
            refs.setdefault(d["reference"], []).append(s)
    for r, ss in refs.items():
        _limit(fail, order, opens, "reference", f"reference {r}", ss, 1, 1.0)
    _limit(fail, order, opens, "windows", "a bare window",
           [s for s, d in allv.items() if d.get("window_covering") == "bare"], 1, 0.5)
    covs = {}
    for s, d in allv.items():
        c = d.get("window_covering")
        if c and c not in ("bare", "no_window_in_view"):
            covs.setdefault(c, []).append(s)
    for c, ss in covs.items():
        _limit(fail, order, opens, "windows", f"{c.replace('_', ' ')} windows", ss, 2, 0.5)
    pv2_open = {s: d for s, d in opens.items() if d.get("pv") == PV and d.get("lived_in")}
    if len(pv2_open) >= 3:
        tidy = [s for s, d in pv2_open.items() if d["lived_in"] == "tidy"]
        used = [s for s, d in pv2_open.items() if d["lived_in"] in ("lived_in", "busy")]
        busy = sorted((s for s, d in pv2_open.items() if d["lived_in"] == "busy"), key=lambda s: rank.get(s, 99))
        if not tidy:
            fail("lived_in", "no open slot is tidy (the set needs a mix)", used, 0.5)
        if len(used) * 2 < len(pv2_open):
            fail("lived_in", f"only {len(used)} of {len(pv2_open)} open slots look lived in or busy (at least half)",
                 tidy, 0.5)
        if len(busy) > 2:
            fail("lived_in", f"{len(busy)} busy slots (at most 2)", busy[2:], 0.5)
    _limit(fail, order, opens, "photo", "an editorial photo style",
           [s for s, d in allv.items() if d.get("photo_style") == "editorial"], 2, 0.5)
    fins = {}
    for s, d in allv.items():
        f = d.get("frame_finish")
        if f and f != "none":
            fins.setdefault(f, []).append(s)
    nf = sum(len(v) for v in fins.values())
    for f, ss in fins.items():
        lim = 3 if f == "walnut_frame" else len(allv)
        if nf >= 5:
            lim = min(lim, max(1, int(0.4 * nf)))
        _limit(fail, order, opens, "frames", f"the {f.replace('_', ' ')}", ss, lim, 0.5)
    regions = {d.get("region") for d in allv.values() if d.get("region")}
    if len(allv) >= 6 and sum(1 for d in allv.values() if d.get("region")) >= 6 and len(regions) < 3:
        fail("region", f"only {len(regions)} house region{'s' if len(regions) != 1 else ''} across the listing "
                       "(at least 3: UK, US, Europe, Asia)", list(opens), 0.4)
    _limit(fail, order, opens, "night", "an evening lamp-lit scene",
           [s for s, d in allv.items() if d.get("light_type") == "night_lamps"], 1 if max_night is None else max_night,
           0.5)


def check_set(briefs, fixed, order=None, ratio_avail=None, max_tight=None, max_night=None):
    """Balance + similarity over the whole listing (plan 7.2). briefs = {slot: brief} (open slots), fixed = {slot:
    descriptor} (approved / pending images: counted, never blamed). ratio_avail = {slot: [ratios with a folder]}.
    When an open brief is pv2 the realism repeat limits run too (_repeat_limits).
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
    if any(d.get("pv") == PV for d in opens.values()):
        _repeat_limits(allv, opens, fix, order, fail, max_night)
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

SYSTEM_PROMPT_V1 = """You plan the room photographs for one Etsy listing of a printable wall-art design, as three people \
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


# realism addendum 3.2 (2026-11-20): the lived-in brief replaces the catalogue recipe for every new plan
SYSTEM_PROMPT = """You plan the room photographs for one Etsy listing of a printable wall-art design. You are three \
people at once: an interior designer who knows how real people furnish the homes they actually live in, a \
photographer, and a curator who decides how a buyer first meets this artwork. You see the artwork, the photographs \
that already exist for this listing, a sheet of reference photographs labelled with their ids, and the open slots you \
must plan.

The story of every photograph: someone bought this print, had it printed and framed, put it up in their own home and \
took a nice photo of it. The home is real and lived in. It is not a showroom, a catalogue or a styled vignette.

Every artwork is a PORTRAIT (vertical) piece. Every photograph is a 4:3 landscape listing photo.

For each open slot, first decide who lives there and write it as "occupant": one short sentence for your own \
planning. It is never shown and never sent to the image model, so the scene text never mentions a person. Then write \
the scene from that life:
- Everyday things in use, left where people leave them: a jacket over a chair back, a half-finished mug, a few plain \
envelopes face down, a phone charger cable, shoes by a door, a child's crayon drawing with no letters, folded \
laundry, keys in a bowl, a lamp left on. Pick what this occupant would have; never all of them.
- Real imperfections: uneven bedding, a scuffed skirting board, a rug slightly askew, worn paint on a door frame, a \
radiator under the window, light switches, power outlets, a plain round thermostat, door frames and hinges.
- Real windows: venetian or roller blinds, linen curtains, sheers or shutters, and a real view (a street, the \
neighbour's brick wall, trees, a courtyard, a city). A bare window at most once in the whole listing.
- Furniture of different ages that was not bought as a set: a hand-me-down dresser beside a flat-pack shelf, a \
vintage chair at a modern desk, a painted chest with worn edges.
- Different houses and regions: a 1920s brick terrace, a 1970s condo, a rented student flat, a craftsman bungalow, a \
converted loft, an old farmhouse kitchen, a Tokyo apartment, a Berlin Altbau, a Texas ranch house. The region shows \
in windows, radiators, floors, outlets and light.
- How lived-in each slot is ("tidy", "lived_in", "busy") varies across the set: a nursery may be tidy, a study or a \
kitchen clearly used. "busy" only for medium and wide shots. Everything stays clear of the frame: clutter sits below \
its bottom edge or toward the picture edges.

The light varies across the set and is never a default warm golden glow: hard diagonal sun with crisp shadows, a grey \
overcast day, a rainy afternoon, blue dusk with a warm lamp on, evening lit only by lamps, sun striped by venetian \
blinds, steady north light. Warm golden low sun at most once in the whole listing.

The photograph looks taken by the owner with a good phone or a simple camera: natural auto exposure, true colours, a \
little grain in the room, framed by hand (slightly off-centre is fine, verticals level), not retouched. At most two \
slots in the listing look editorial.

Avoid the catalogue recipe. Each of these at most once in the whole listing, counting the photographs that already \
exist: dried stems or pampas, rattan or cane, boucle, a wooden toy block or stacking toy, candles, a chunky knit \
throw. Plants at most twice; stoneware or ceramic vases at most twice; stacks of books at most twice. Do not default \
to walnut, oak, limewash and stoneware.

References: pick ONE reference photograph for each open slot, a different one for every slot, never one already used \
by an existing photograph. The reference gives the camera position, lens, framing and the photograph's character \
(and its light when your light type matches it); your scene gives the room and the life in it. Choose a reference \
whose display (hung on a wall, on a surface, on a shelf, leaning on the floor) and framing fit the slot's print size. \
"reference_flip": true uses it mirrored. Never describe the reference's furniture or objects: build a new room.

What a slot is: the room name is where it is filed. The setting is the surface or wall inside that room (a \
nightstand, a desk, a mantel, an entry console or hallway wall, which are filed under Living room, the wall over a \
bed, a bathroom wall). Setting and shot are separate choices.

Scale drives framing. Pick a real print size from the chart for each slot. Small prints are shown TIGHT: the piece \
stands or leans on a surface and fills about half to two thirds of the picture height, with one to three everyday \
objects at true scale beside it. Medium prints are medium shots with the furniture below. Large prints are wider \
shots on a wall or leaning on the floor. Across the listing aim for roughly a third small, a third medium, a third \
large, all five ratios, several sizes; the existing photographs count, so fill what they lack.

The art ties in with the room by contrast or harmony, never by matching its colours. Do not take wall or furniture \
colours from the artwork. One or two slots may use a loud wall, a bold furniture piece or a painted frame (yellow, \
red, deep green, bronze) when it flatters this piece. Warm walls are allowed: the pipeline picks the colour of the \
blank print area itself.

Hard rules, never broken:
- No people, faces, hands or pets, not even mentioned in passing. One piece of art only: no other frames, posters, \
mirrors, or screens showing pictures.
- Nothing readable: books show plain spines or face away, envelopes face down, phones face down, laptops closed, clocks \
without numerals; no calendars, magazines, packaging, signs, labels or logos.
- Every scene shows visible shadows. The art face is flat, upright, in sharp focus and evenly lit.
- The whole frame is inside the picture with clear space around it; nothing overlaps the frame.
- The frame contrasts with the wall in tone (frame lightness: black 15, walnut 35, bronze 40, gold 60, oak 65, \
silver 72, white 95; a painted frame by its colour; wall lightness at least 15 away). Canvas floaters are natural \
wood, never black. Canvas only for medium and large prints.
- Wainscoting only below waist height (say "below waist height"), or panelling with the art "centred inside one \
larger panel" (say so).
- Do not describe the artwork. The scene text never names the camera, lens, angle, shot size or light direction: \
those come from the fields and the reference.
- The scene text is 60 to 160 words of plain description of the room, its things and its life. Never explain why.
- Prefer a listed library template when one fits the set (it is free); otherwise plan a new scene.

Output ONLY one JSON object, no prose, no reasons, no explanations."""

SCHEMA_V1 = {"briefs": [{
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


SCHEMA = {"briefs": [{
    "pv": 2, "slot": "int", "source": "new | library", "library_rel": "rel of a listed library template, only for library",
    "occupant": "who lives there, one short sentence (planning only, never shown, never in the scene)",
    "reference": "id of ONE listed reference photograph (a different one per slot)", "reference_flip": "true | false",
    "print_size": "a size from the chart", "shot": "tight | medium | wide", "setting": "one of the slot's settings",
    "display": "one of that setting's displays", "presentation": "frame | mat | canvas | canvas_bare",
    "frame_finish": "oak_frame | walnut_frame | black_frame | white_frame | gold_frame | bronze_frame | silver_frame | "
                    "painted_frame (canvas: natural_wood_floater; canvas_bare: none)",
    "frame_colour": {"name": "only for painted_frame", "hex": "#RRGGBB"},
    "camera_side": "left | right | front (taken from the reference when one is used)",
    "camera_height": "surface | low | seated | counter | eye", "lens": "|".join(LENSES),
    "light_type": "|".join(LIGHT_TYPES), "light_from": "|".join(LIGHT_FROM), "depth_of_field": "|".join(DOFS),
    "window": {"covering": "|".join(WINDOW_COVERINGS), "view": "|".join(WINDOW_VIEWS)},
    "photo_style": "|".join(PHOTO_STYLES), "lived_in": "|".join(LIVED_IN),
    "wall": {"name": "plain colour name", "hex": "#RRGGBB", "treatment": "|".join(WALL_TREATMENTS)},
    "floor": "short phrase", "furniture": {"style": "|".join(FURNITURE_STYLES), "colour": "one word",
                                           "family": "|".join(FURNITURE_FAMILIES)},
    "house": "|".join(HOUSES_V2), "buyer": "|".join(BUYERS),
    "props": ["everyday things: 1-3 for tight, at most 6 medium, 8 wide; busy needs 4+"],
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
    out = {k: b.get(k) for k in ("slot", "source", "library_rel", "print_size", "shot", "setting", "display",
                                 "presentation", "frame_finish", "camera_side", "camera_height", "lens", "light_style",
                                 "light_from", "shadow", "depth_of_field", "floor", "house", "buyer", "props", "scene")} \
        | {"wall": {k: (b.get("wall") or {}).get(k) for k in ("name", "hex", "treatment")},
           "furniture": b.get("furniture")}
    if b.get("pv") == PV:
        out.update({k: b.get(k) for k in ("pv", "occupant", "reference", "reference_flip", "light_type", "window",
                                          "photo_style", "lived_in", "frame_colour")})
        out.pop("light_style", None)
        out.pop("shadow", None)
    return out


def ref_view(e):
    """One reference as the planner sees it: id, compact tags, measured facts, past grade."""
    t = e.get("tags") or {}
    g = [x.get("grade") for x in e.get("grades") or [] if x.get("grade")]
    return {"id": e["id"], "display": t.get("display_group"), "shot": t.get("shot"), "setting": t.get("setting"),
            "light_type": t.get("light_type"), "lived_in": t.get("lived_in"), "window": t.get("window_covering"),
            "camera_side": e.get("camera_side"), "camera_height": t.get("camera_height"), "lens": t.get("lens"),
            "editorial": t.get("editorial"), "times_used": len(e.get("uses") or []),
            **({"grades": g} if g else {})}


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
        "lists": {"house": HOUSES_V2, "buyer": BUYERS, "furniture.style": FURNITURE_STYLES,
                  "furniture.family": FURNITURE_FAMILIES, "wall.treatment": WALL_TREATMENTS},
        "output_schema": SCHEMA}
    refs = ctx.get("refs")
    if refs:
        data["references"] = [ref_view(e) for e in refs]
        data["references_used_by_existing_photographs"] = sorted(ctx.get("fixed_refs") or [])
        data["display_of_each_setting_display"] = {k: v for k, v in DISPLAY_GROUP.items()}
    if ctx.get("graded"):
        data["tonys_past_grades"] = ctx["graded"]
    n = 1
    head = "Image 1 is the artwork."
    if ctx.get("has_sheet"):
        n += 1
        head += f" Image {n} is a contact sheet of the photographs that already exist, each labelled with its slot number."
    if ctx.get("has_ref_sheet"):
        n += 1
        head += f" Image {n} is the sheet of reference photographs, each labelled with its id."
    if not ctx.get("has_sheet") and not ctx.get("has_ref_sheet"):
        head = ("Image 1 is the artwork. Image 2 (when present) is a contact sheet of the photographs that already "
                "exist, each labelled with its slot number.")
    head += "\n\n"
    if ctx.get("graded"):
        head += ("tonys_past_grades: Tony's past grades of room photographs: learn what he rewards and what he marks "
                 "down; never copy a scene.\n\n")
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


def _ref_score(e, b, use_count=0):
    """Reassignment score (2.1): display match 3 + shot match 2 + lived-in match 1 + unused across listings 1 + mean
    past grade 0-1 (ungraded 0.5); a reference already used in this set loses 1 per use (shortage reuse only)."""
    from .references import mean_grade
    t = e.get("tags") or {}
    sc = 3.0 if t.get("display_group") == display_group(b.get("display")) else 0.0
    sc += 2.0 if t.get("shot") == b.get("shot") else 0.0
    sc += 1.0 if t.get("lived_in") and t.get("lived_in") == b.get("lived_in") else 0.0
    sc += 1.0 if not e.get("uses") else 0.0
    g = mean_grade(e)
    return sc + (0.5 if g is None else g) - use_count


def validate_references(briefs, taken, refs, order=None):
    """One distinct usable reference per new pv2 brief (2.1), decided in listing order. A pick that is unknown,
    unusable, already taken (another open slot or a fixed slot's template) or does not fit (display group, shot within
    one step) is REASSIGNED by code to the best-scoring fitting free reference. When no fitting free one is left
    (fewer usable references than open slots), the least-used fitting one is reused (reference_reused); with none at all
    the brief goes text-only (reference None). Returns notes (plain lines) and edits the briefs in place."""
    if refs is None:
        return []
    by_id = {e["id"]: e for e in refs}
    taken = set(taken or ())
    count = {}
    notes = []
    rank = {s: i for i, s in enumerate(order or [])}
    for s in sorted(briefs, key=lambda s: (rank.get(s, 99), s)):
        b = briefs[s]
        if b.get("source") != "new" or b.get("pv") != PV:
            continue
        pick = b.get("reference")
        e = by_id.get(pick)
        b["reference_reused"] = False
        if e is not None and pick not in taken and ref_fits(e, b):
            taken.add(pick)
            count[pick] = 1
            continue
        free = [x for x in refs if x["id"] not in taken and ref_fits(x, b)]
        reused = False
        if not free:
            free = [x for x in refs if ref_fits(x, b)]
            reused = bool(free)
        if not free:
            if pick:
                notes.append(f"slot {s}: no usable reference fits a {display_group(b.get('display'))} "
                             f"{b.get('shot')} slot; text-only prompt")
            b["reference"], b["reference_flip"] = None, False
            continue
        best = sorted(free, key=lambda x: (-_ref_score(x, b, count.get(x["id"], 0)), x["id"]))[0]
        why = ("unknown or unusable" if e is None else "already used" if pick in taken else "does not fit the slot")
        notes.append(f"slot {s}: reference {pick or '(none)'} {why}; code picked {best['id']}"
                     + (" (reused: fewer usable references than open slots)" if reused else ""))
        b["reference"], b["reference_reused"] = best["id"], reused
        taken.add(best["id"])
        count[best["id"]] = count.get(best["id"], 0) + 1
    return notes


def finish(briefs, ctx, current=None):
    """normalise + lint + prompt for every brief of the open slots. pv2 briefs also get one distinct reference each
    (validate_references; `current` = the other briefs of the set whose references stay taken) and their camera fields
    derived from it."""
    out = {}
    v2 = {}
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
        if is_v2(raw):
            v2[o["slot"]] = (normalise(dict(raw, pv=PV), o), o)
            continue
        b = normalise(raw, o)
        b["lint"] = lint(b, o)
        b["prompt"] = assemble(b) if b["lint"]["pass"] else None
        b["_done"] = True
        out[o["slot"]] = b
    if v2:
        refs = ctx.get("refs")
        taken = set(ctx.get("fixed_refs") or ())
        taken |= {b.get("reference") for s, b in (current or {}).items()
                  if s not in v2 and b.get("reference") and not b.get("reference_reused")}
        notes = validate_references({s: b for s, (b, _) in v2.items()}, taken, refs, ctx.get("order"))
        ctx.setdefault("ref_notes", []).extend(notes)
        by_id = {e["id"]: e for e in refs or []}
        compact = ctx.get("compact", COMPACT_DEFAULT)
        for s, (b, o) in v2.items():
            apply_reference(b, by_id.get(b.get("reference")))
            b["prompt_style"] = "compact" if b.get("presentation") in compact else "full"
            b["lint"] = lint(b, dict(o, refs=refs))
            b["prompt"] = assemble(b) if b["lint"]["pass"] else None
            b["_done"] = True
            out[s] = b
    return out


def flip_fix(cur, ctx, chk, log=print):
    """Free fix after the rounds: a slot blamed for the camera side whose reference can be mirrored gets
    reference_flip toggled (camera side swaps) when that lowers the set's blame and the brief still lints."""
    by_id = {e["id"]: e for e in ctx.get("refs") or []}
    avail = {o["slot"]: o["ratios"] for o in ctx["open"]}
    octx = {o["slot"]: o for o in ctx["open"]}
    for f in [x for x in chk["failures"] if x["rule"] in ("camera", "neighbours", "composition")]:
        for s in f["slots"]:
            b = cur.get(s)
            e = by_id.get((b or {}).get("reference"))
            if not b or b.get("pv") != PV or not e or e.get("camera_side") not in ("left", "right"):
                continue
            nb = dict(b, reference_flip=not b.get("reference_flip"))
            apply_reference(nb, e)
            nb["lint"] = lint(nb, dict(octx[s], refs=ctx.get("refs")))
            if not nb["lint"]["pass"]:
                continue
            nb["prompt"] = assemble(nb)
            trial = {**cur, s: nb}
            c2 = check_set(trial, ctx["fixed_desc"], ctx["order"], avail, ctx.get("max_tight"), ctx.get("max_night"))
            if total_blame(c2) < total_blame(chk):
                log(f"slot {s}: reference {nb['reference']} {'mirrored' if nb['reference_flip'] else 'unmirrored'} "
                    f"for the camera balance (free)")
                cur, chk = trial, c2
    return cur, chk


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
        chk = check_set(cur, ctx["fixed_desc"], order, avail, max_tight, ctx.get("max_night"))
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
        cur = {**cur, **{s: b for s, b in finish({s: got[s] for s in redo if s in got}, ctx, cur).items()}}
    _, cur, chk = best
    cur, chk = flip_fix(cur, ctx, chk, log)
    lint_bad = [s for s, b in cur.items() if not b["lint"]["pass"]]
    if chk["pass"] and not lint_bad:
        cands = {o["slot"]: o.get("library") or [] for o in ctx["open"]}
        cur, swapped = library_swap(cur, ctx["fixed_desc"], cands, order, avail, max_tight)
        chk = check_set(cur, ctx["fixed_desc"], order, avail, max_tight, ctx.get("max_night"))
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
    if ctx.get("ref_notes"):
        log("references reassigned by code: " + "; ".join(ctx["ref_notes"]))
    out.update(status=status, message=msg, briefs=briefs, ref_notes=list(ctx.get("ref_notes") or []),
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
                 "\"shadow\", \"prop_families\" (a list), \"light_type\", \"window_covering\", \"lived_in\", "
                 "\"warm_sun\" (true / false)}}; use null when unsure. No prose.")
VISION_VERSION = 2


def describe_fixed(items, ask_vision):
    """ONE vision call for all uncached existing slot images: [(slot, path)] -> {slot: {...}}. Failures -> {}."""
    if not items:
        return {}
    from .prod_chat import encode_image
    lists = {"setting": sorted(SETTINGS), "display": DISPLAYS, "furniture_style": FURNITURE_STYLES,
             "furniture_family": FURNITURE_FAMILIES, "house": HOUSES, "buyer": BUYERS,
             "camera_height": CAMERA_HEIGHTS, "wall_treatment": WALL_TREATMENTS, "light_style": LIGHT_STYLES,
             "shadow": SHADOWS, "light_type": LIGHT_TYPES, "window_covering": WINDOW_COVERINGS,
             "lived_in": LIVED_IN}
    prompt = (VISION_PROMPT + "\nSlots in image order: " + ", ".join(str(s) for s, _ in items) + "\nLists: "
              + json.dumps(dict(lists, prop_families=sorted(PROP_FAMILIES))))
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
            fams = v.get("prop_families")
            if isinstance(fams, list):
                out[s]["prop_families"] = sorted({f for f in fams if f in PROP_FAMILIES})
            if isinstance(v.get("warm_sun"), bool):
                out[s]["warm_sun"] = v["warm_sun"]
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


def library_candidates(settings, room, used, fails, limit=8, decor=None):
    """Unused, checker-not-failed library templates of this room (any ratio with a folder), with shot_meta. With decor
    (Tony 2026-11-20) a template must also match the slot's decor, like production.library_picks does."""
    from . import scene_templates as stp
    out = []
    want = rs.ROOM_FOLDER.get(room)
    for t in stp.library_templates(settings):
        if t.get("wired") or t["rel"] in used or t["rel"] in fails or rs.norm(t["room"]) != want:
            continue
        if not stp.auto_pick_ok(t):          # graded below B- or flagged by the text scan (realism addendum 6.4, 7)
            continue
        man = t.get("manifest") or {}
        if decor and not rs.decor_matches(decor, t["style"], t["name"], t.get("desc"), man.get("decor")):
            continue
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


def context(con, settings, idea_id, ask_vision=None, cached_fixed=None, work=None, replan=()):
    """Everything the planner needs for one design: design facts, fixed slot descriptors (measured + one cached
    vision describe), ALL open slots (room + decor from rs.plan; Tony's picks honoured), library candidates, images,
    and (realism addendum) the usable references + their sheet and Tony's graded examples. replan: decided slots
    treated as open (the free dry run only)."""
    from . import production as prod
    idea, lst, rec, folder, arts = prod._ctx(con, settings, idea_id)
    plan, avail = prod._plan(con, settings, idea, rec, folder, arts)
    p = prod._prod(rec)
    fixed_items, open_slots = _split_slots(idea_id, rec, folder, plan, replan)
    cache = dict(cached_fixed or {})
    stale = lambda ent: (ent or {}).get("vision_version") != VISION_VERSION     # noqa: E731  (v1 cache: describe once more)
    todo = [(s, pth) for s, pth, _, name in fixed_items if name and pth and (name not in cache or stale(cache[name]))]
    vis = describe_fixed(todo, ask_vision) if ask_vision and todo else {}
    fixed, fixed_desc = {}, {}
    for s, pth, srec, name in fixed_items:
        ent = cache.get(name)
        if ent is None or (s, pth) in todo:
            d = fixed_descriptor(con, settings, srec, pth, vis.get(s))
            ent = {"descriptor": d, "file": name, "from": "measured+vision" if vis.get(s) else "measured",
                   "vision_version": VISION_VERSION}
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
              "library": library_candidates(settings, c["room"], used, fails, decor=c["decor"])} for c in open_slots]
    images = []
    iso = next((a for a in arts if "_ISO_" in a.name), arts[0] if arts else None)
    from .prod_chat import encode_image
    if iso is not None:
        images.append(encode_image(iso, 1568))
    has_sheet = has_ref_sheet = False
    if work is not None and fixed_items:
        sheet = contact_sheet([(s, pth) for s, pth, _, _ in fixed_items if pth], Path(work) / "contact_sheet.png")
        if sheet:
            images.append(encode_image(sheet, 1568))
            has_sheet = True
    refs = None
    if cfg(settings, "planner_references"):
        from . import references
        refs = references.usable(settings)
        if work is not None and refs:
            rs_png = references.contact_sheet(refs, Path(work) / "reference_sheet.png", settings=settings)
            if rs_png:
                images.append(encode_image(rs_png, 1568))
                has_ref_sheet = True
    fixed_refs = sorted({d.get("reference") for d in fixed_desc.values() if d.get("reference")})
    graded = graded_examples(settings) if cfg(settings, "planner_graded_examples") else []
    eng = prod._engine(settings)
    fx_view = {str(s): {k: v for k, v in d.items() if v is not None and k not in ("scene", "wall_lab")}
               for s, d in fixed_desc.items()}
    return {"idea_id": idea_id, "listing_id": lst["id"], "order": rs.room_slots(settings),
            "design": {"title": idea["title"], "name": lst["title"], "description": idea["description"],
                       "styles": styles, "value_key": an.get("value_key"),
                       "accents": [a.get("name") for a in an.get("accents") or []]},
            "fixed": fx_view, "fixed_desc": fixed_desc, "fixed_cache": fixed, "open": opens, "images": images,
            "credits_per_scene": eng.get("credits_per_scene"), "max_tight": int(cfg(settings, "planner_max_tight")),
            "inputs_key": _key(tags, styles, open_slots, fixed_items, p),
            "refs": refs, "fixed_refs": fixed_refs, "graded": graded, "has_sheet": has_sheet,
            "has_ref_sheet": has_ref_sheet, "compact": tuple(cfg(settings, "planner_compact") or ()),
            "max_night": int(cfg(settings, "planner_max_night")), "ref_notes": []}


def graded_examples(settings=None, good=3, bad=3, cap_words=1400):
    """Tony's graded room templates as few-shot examples (realism addendum 7): good = mean >= B+ (best first, newest on
    ties), bad = mean <= C (worst first). Until good examples exist only the bad ones show. About 1,400 words max."""
    from . import scene_templates as stp
    items = []
    for t in stp.library_templates(settings):
        if t.get("wired") or not t.get("psd"):
            continue
        gs = stp.template_grades(t["psd"])
        if not gs:
            continue
        mean = sum(stp.GRADE_SCORE[g["grade"]] for g in gs) / len(gs)
        man = t.get("manifest") or {}
        b = man.get("brief") or {}
        ex = {"grade": "/".join(g["grade"] for g in gs), "note": next((g["note"] for g in reversed(gs)
                                                                        if g.get("note")), None)}
        if b:
            ex.update(scene=b.get("scene"), setting=b.get("setting"), shot=b.get("shot"),
                      light=b.get("light_type") or b.get("light_style"), lived_in=b.get("lived_in"),
                      props=b.get("props"), reference=b.get("reference"))
        else:
            lk = man.get("look") or {}
            ex.update(persona=lk.get("photographer"), light=lk.get("light_style"), camera=lk.get("camera_angle"),
                      display=lk.get("display"), wall=lk.get("wall_palette"), room=man.get("room"))
        ex = {k: v for k, v in ex.items() if v not in (None, "", [])}
        items.append((mean, str(man.get("created") or ""), ex))
    newest = sorted(items, key=lambda i: i[1], reverse=True)              # stable sorts: newest first on ties
    good_l = sorted((i for i in newest if i[0] >= stp.GRADE_SCORE["B+"]), key=lambda i: -i[0])[:good]
    bad_l = sorted((i for i in newest if i[0] <= stp.GRADE_SCORE["C"]), key=lambda i: i[0])
    out, words = [], 0
    for kind, lst in (("good", good_l), ("bad", bad_l[:bad])):
        for _, _, ex in lst:
            n = len(json.dumps(ex).split())
            if words + n > cap_words:
                break
            out.append(dict(ex, kind=kind))
            words += n
    return out


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
            ctx["fixed_refs"] = sorted(set(ctx.get("fixed_refs") or [])
                                       | {b.get("reference") for b in hold.values() if b.get("reference")})
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


def _split_slots(idea_id, rec, folder, plan, replan=()):
    """(fixed items [(slot, image path, slot record, file)], open cards) of a design's slot plan. replan: decided slots
    treated as open (the free dry run)."""
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
        if (decided or running) and c["slot"] not in replan:
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
            "reference": b.get("reference"), "reference_flip": bool(b.get("reference_flip")),
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

def dry_run(idea_id, settings=None, ask=None, out=print, replan=()):
    """Plan one design against a READ-ONLY view of the real DB and print the briefs + the check. Writes nothing.
    replan: decided slots treated as open (e.g. 16,17,18,19 of Book Club Cat, whose twelve room slots all have images)."""
    import sqlite3
    import tempfile
    from .db import DB_PATH, load_config
    settings = settings or load_config("settings")
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True, check_same_thread=False)
    con.row_factory = sqlite3.Row
    vision = ask or default_ask(settings, VISION_SYSTEM)
    ask = ask or default_ask(settings)
    replan = tuple(int(x) for x in replan or ())
    with tempfile.TemporaryDirectory() as td:
        ctx = context(con, settings, idea_id, ask_vision=vision, work=td, replan=replan)
        out(f"Design #{idea_id} {ctx['design']['name']}: fixed slots {sorted(ctx['fixed_desc'])}, open slots "
            f"{[o['slot'] for o in ctx['open']]}" + (f" (re-planned: {list(replan)})" if replan else ""))
        out(f"References: {len(ctx.get('refs') or [])} usable ({', '.join(e['id'] for e in ctx.get('refs') or [])}); "
            f"used by fixed slots: {ctx.get('fixed_refs') or 'none'}; graded examples: {len(ctx.get('graded') or [])}")
        for s, d in sorted(ctx["fixed_desc"].items()):
            out(f"  fixed {s:02d}: ratio {d.get('ratio')} · {d.get('shot')} ({d.get('art_h_frac')}) · side "
                f"{d.get('camera_side')} · light {d.get('light_type') or d.get('light_style')} from "
                f"{d.get('light_from')} · {d.get('presentation')} · wall {d.get('wall_family')} · setting "
                f"{d.get('setting')} · props {d.get('prop_families')} · {d.get('house')}")
        res = plan_set(ctx, ask, settings, log=lambda m: out("  .. " + m))
    out(f"\nStatus: {res['status']} after {res.get('rounds')} round(s), {res.get('seconds')} s"
        + (f" ({res['message']})" if res.get("message") else ""))
    for s, b in sorted(res.get("briefs", {}).items(), key=lambda x: int(x[0])):
        w = b.get("wall") or {}
        out(f"\n--- slot {s} · {b['room']} · {b['decor']} · {b['source']}"
            + (f" {b.get('library_rel')}" if b.get("library_rel") else ""))
        out(f"    {facts_line(b)} · display {b.get('display')} · {b.get('presentation')} {b.get('frame_finish')}")
        if b.get("pv") == PV:
            band = ("realism clause with the reference's light" if "light" in (b.get("ref_use") or [])
                    else "realism clause, own light")
            out(f"    reference {b.get('reference') or 'none'}{' (mirrored)' if b.get('reference_flip') else ''}"
                f"{' (reused)' if b.get('reference_reused') else ''} · wording: {band if b.get('reference') else 'text only'}"
                f" · occupant: {b.get('occupant')}")
            out(f"    lived-in {b.get('lived_in')} · light {b.get('light_type')} from {b.get('light_from')} · window "
                f"{(b.get('window') or {}).get('covering')}/{(b.get('window') or {}).get('view')} · photo "
                f"{b.get('photo_style')} · prompt style {b.get('prompt_style')}")
        out(f"    camera {b.get('camera_side')} / {b.get('camera_height')} / {b.get('lens')} / {b.get('depth_of_field')}"
            f" · light style {b.get('light_style')}, {b.get('shadow')} shadows")
        out(f"    wall {w.get('name')} {w.get('hex')} ({w.get('family')}, {w.get('treatment')}) · marker "
            f"{b.get('marker')} · furniture {b.get('furniture')} · {b.get('house')} · buyer {b.get('buyer')}")
        out(f"    props {b.get('props')} · families {descriptor(b).get('prop_families')}")
        out(f"    lint: {'pass' if b['lint']['pass'] else 'FAIL ' + '; '.join(b['lint']['why'])}")
        if b.get("scene"):
            out(f"    scene ({len(b['scene'].split())} words): {b['scene']}")
        if b.get("prompt"):
            out(f"    prompt ({len(b['prompt'].split())} words with the reference, "
                f"{len(assemble(b, ref=False).split())} text-only): {b['prompt']}")
    chk = res.get("check") or {}
    out(f"\nBalance + repeat-limit check: {'PASS' if chk.get('pass') else 'FAIL'}"
        + "".join(f"\n  - [{f['rule']}] {f['text']} (slots {f['slots']})" for f in chk.get("failures") or []))
    if res.get("ref_notes"):
        out("Reference notes: " + "; ".join(res["ref_notes"]))
    out(f"Cost if generated: {res.get('cost')}")
    return res


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Slot-set planner")
    ap.add_argument("--idea", type=int, required=True)
    ap.add_argument("--dry-run", action="store_true", help="plan and print only; writes nothing")
    ap.add_argument("--replan", help="decided slots to plan as if open, e.g. 16,17,18,19 (dry run only)")
    a = ap.parse_args()
    if not a.dry_run:
        raise SystemExit("only --dry-run is available from the command line (the Portal saves plans)")
    dry_run(a.idea, replan=[int(x) for x in a.replan.split(",")] if a.replan else ())
