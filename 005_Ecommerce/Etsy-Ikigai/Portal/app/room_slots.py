"""Room-slot planning for the Production tab (Tony, 2026-11-08; slot map corrected 2026-11-10): which room, decor
style and print ratio each ROOM listing image shows. Pure logic, no files, no network; app/production.py calls it.

  - Listing slot map (Tony 2026-11-10, memory ikigai-listing-slot-map): 1 main, 1A video (never "slot 2"), 2 poster,
    3 ROOM, 4 Instant Download, 5 what-you-get + sizes, 6 wall diagram, 7 important notes, 8 close-up detail,
    9-19 ROOMS, 20 reviews. Rooms = slot 3 + slots 9-19 (12); every other slot is the same every listing.
  - Room slots in order (3, 9, 10, 11, 12 ...) take the rooms Tony ticked (up to 5, ONLY from Etsy's Room attribute
    list), in his order.
  - The agent fills the rest (up to slot 19) with rooms that make sense for the art: the art-to-room
    compatibility rule scores every room against the idea text, the shop-style tags and the print itself
    (value key from rooms.analyze_print), using Rules_And_Policies/Etsy_Attributes_And_Style_Crosswalk.md.
    Low scores are excluded (cyberpunk art never goes in a laundry or kitchen); a room may repeat with a
    different decor style (modern + mid-century living room); when too few rooms fit, fewer slots are planned
    rather than padding. The scores stay internal (Tony does not want to see the matrix).
  - Ratio per slot by buyer popularity (2x3 35%, 3x4 25%, 4x5 25%, ISO/5x7 10%, 11x14 5%), only ratios the design
    is sold in (all five print files) and only where the template library has a folder for that room.
Everything is deterministic: the same inputs always give the same plan. The one deliberate exception is the scene
"look" (pick_look, Tony 2026-11-17, widened 2026-11-19): light, photographer/stylist persona, camera, lens, focus, foreground,
display, composition, walls, floor, furniture and frame finish are randomised per NEW scene and saved with its seed.
"""
import re

# Etsy taxonomy 2078 Room attribute (crosswalk). The check boxes offer only these.
ETSY_ROOMS = ["Bathroom", "Bedroom", "Dorm", "Entryway", "Game room", "Kids", "Kitchen & dining", "Laundry",
              "Living room", "Nursery", "Office"]
# Mockup scenes may use rooms outside Etsy's list (crosswalk "Room pick rule"); only the agent picks these.
SCENE_ONLY_ROOMS = ["Creative space"]
SHOP_STYLES = ["Trendy", "Abstract", "Animals", "Botanical", "Food-Drink", "Game Room", "Japan Art", "Mid Century",
               "Minimalism", "Nature", "Nursery", "Retro", "Travel", "Typography", "Vintage", "Beach Ocean"]
MAX_PICKS = 5
ROOM_SLOTS = [3] + list(range(9, 20))      # the 12 room images, in fill order
FIXED_SLOTS = [1, 2, 4, 5, 6, 7, 8, 20]    # same every listing (1A video too); never a Production card


def room_slots(settings=None):
    """The room slot numbers in fill order (settings `room_slots` may override; default 3, 9-19)."""
    v = (settings or {}).get("room_slots")
    return [int(x) for x in v] if v else list(ROOM_SLOTS)

# room -> normalised name of the room folder in Room_Templates/Portrait_Templates/<NNN_Ratio>/<NNN_Room> (crosswalk:
# Living_Rooms -> Living room, Kitchen_Bar -> Kitchen & dining, GameRooms_Mancave -> Game room, Kids_Nursery ->
# Nursery and Kids). A dorm is drawn as a dorm but filed with bedrooms. None = no folder yet (Tony makes folders).
ROOM_FOLDER = {"Living room": "living_rooms", "Bedroom": "bedroom", "Dorm": "bedroom", "Bathroom": "bathroom",
               "Kitchen & dining": "kitchen_bar", "Office": "office", "Game room": "gamerooms_mancave",
               "Kids": "kids_nursery", "Nursery": "kids_nursery", "Creative space": "creative_space",
               "Entryway": "entryway", "Laundry": "laundry"}   # folders only after Tony approves them
# room folders the Templates tab may PROPOSE (Tony 2026-11-10: created only after he approves the exact path).
# Numbers follow his order: ISO already uses 007_Creative_Space and 008_Kids_Nursery, so new rooms start at 009.
PROPOSED_ROOM_FOLDERS = {"Entryway": "009_Entryway", "Laundry": "010_Laundry"}
# what the image model is asked to draw for each room
ROOM_WORDS = {"Living room": "living room", "Bedroom": "bedroom", "Dorm": "college dorm room", "Bathroom": "bathroom",
              "Kitchen & dining": "kitchen and dining nook", "Office": "home office", "Game room": "game room",
              "Kids": "kid's bedroom", "Nursery": "nursery", "Creative space": "art studio corner",
              "Entryway": "entryway", "Laundry": "laundry room"}

# ---------- compatibility rule ----------
BASE = {"Living room": 3.0, "Bedroom": 2.6, "Office": 1.8, "Entryway": 1.4, "Creative space": 1.0, "Dorm": 1.0,
        "Kitchen & dining": 0.8, "Bathroom": 0.8, "Kids": 0.4, "Nursery": 0.3, "Game room": 0.3, "Laundry": 0.2}
STYLE_ROOM = {   # shop style tag -> room bonus / malus (crosswalk + common sense)
    "Food-Drink": {"Kitchen & dining": 4, "Living room": -0.5, "Bedroom": -1.5, "Nursery": -3, "Kids": -2,
                   "Bathroom": -2, "Dorm": -0.5},
    "Game Room": {"Game room": 4, "Dorm": 2, "Bedroom": 0.5, "Office": 1, "Kitchen & dining": -3, "Laundry": -3,
                  "Nursery": -3, "Bathroom": -2, "Entryway": -1},
    "Nursery": {"Nursery": 4, "Kids": 3.5, "Bedroom": 0.5, "Office": -1.5, "Game room": -2, "Kitchen & dining": -1,
                "Dorm": -1},
    "Botanical": {"Living room": 1, "Bedroom": 1, "Bathroom": 1.5, "Kitchen & dining": 0.5, "Entryway": 0.8},
    "Nature": {"Living room": 1, "Bedroom": 0.8, "Office": 0.6, "Entryway": 0.8},
    "Beach Ocean": {"Bathroom": 2, "Bedroom": 1, "Living room": 1, "Entryway": 0.6},
    "Typography": {"Office": 1.8, "Entryway": 1.2, "Kitchen & dining": 0.6, "Dorm": 1},
    "Japan Art": {"Living room": 1, "Bedroom": 1, "Office": 0.6, "Entryway": 0.5},
    "Mid Century": {"Living room": 1.2, "Office": 0.6, "Entryway": 0.4},
    "Minimalism": {"Bedroom": 0.8, "Office": 0.8, "Bathroom": 0.6},
    "Retro": {"Living room": 0.8, "Kitchen & dining": 0.6, "Game room": 1, "Dorm": 1},
    "Vintage": {"Living room": 1, "Bedroom": 0.6, "Entryway": 0.6, "Office": 0.4},
    "Trendy": {"Bedroom": 1, "Dorm": 1.5, "Living room": 0.6},
    "Abstract": {"Living room": 1, "Office": 1, "Bedroom": 0.6, "Entryway": 0.5},
    "Animals": {"Living room": 0.8, "Bedroom": 0.6, "Kids": 1.5, "Nursery": 1},
    "Travel": {"Living room": 0.8, "Office": 1, "Entryway": 1, "Dorm": 0.6},
}
WORD_ROOM = [    # words in the idea title/description -> room bonus / malus
    (r"\b(cats?|kittens?|dogs?|pupp(y|ies)|pets?)\b", {"Living room": 0.6, "Kids": 0.6, "Nursery": 0.3}),
    (r"\b(books?|reading|library|bookish|novel)\b", {"Living room": 1, "Office": 1.2, "Bedroom": 0.6, "Dorm": 0.5}),
    (r"\b(coffee|wine|cocktails?|food|kitchen|fruits?|lemons?|drinks?|bar|tea|bakery|pasta|cheese)\b",
     {"Kitchen & dining": 3}),
    (r"\b(bath|bathroom|spa|shower|soap)\b", {"Bathroom": 3}),
    (r"\b(baby|nursery|kids?|child|children|toddler|cute|bunny|teddy)\b", {"Nursery": 2, "Kids": 2}),
    (r"\b(game|gaming|gamer|arcade|anime|cyber\w*|neon|pixel|manga)\b",
     {"Game room": 3, "Dorm": 1.5, "Kitchen & dining": -2, "Laundry": -3, "Nursery": -3, "Bathroom": -1.5}),
    (r"\b(laundry|wash|washing)\b", {"Laundry": 4}),
    (r"\b(motivational|quote|work|desk|hustle|focus)\b", {"Office": 2}),
    (r"\b(welcome|home|door|keys?|entry)\b", {"Entryway": 2}),
    (r"\b(gothic|skulls?|horror|dark|moody|witch\w*|ravens?|occult)\b",
     {"Nursery": -4, "Kids": -3, "Kitchen & dining": -1, "Laundry": -2}),
    (r"\b(plants?|botanical|flowers?|floral|leaf|leaves|ferns?)\b", {"Bathroom": 0.8, "Kitchen & dining": 0.5}),
    (r"\b(ocean|beach|sea|coastal|waves?|surf)\b", {"Bathroom": 1.5}),
]
VALUE_ROOM = {"dark": {"Nursery": -2, "Kids": -1.5, "Bathroom": -0.5, "Game room": 0.8},
              "light": {"Nursery": 0.3, "Kids": 0.2}}
MIN_SCORE = 1.5          # below this a room does not suit the art (excluded)
REPEAT_COST = 1.2        # each extra slot of the same room costs this much (sensible beats unique, but some variety)

# ---------- decor styles (the room's look; matches Tony's style folders) ----------
# shop style tag -> decor styles to show it in, best first
STYLE_DECOR = {"Mid Century": ["Mid_Century", "Modern"], "Minimalism": ["Japandi", "Minimal", "Modern"],
               "Japan Art": ["Japandi", "Minimal"], "Botanical": ["Japandi", "Boho", "Botanical"],
               "Trendy": ["Boho", "Modern"], "Retro": ["Mid_Century", "Retro", "Boho"],
               "Vintage": ["Victorian", "Mid_Century"], "Abstract": ["Modern", "Japandi"], "Typography": ["Modern"],
               "Nature": ["Japandi", "Boho"], "Animals": ["Modern", "Boho"], "Food-Drink": ["Food_and_Drink", "Modern"],
               "Game Room": ["Gamer", "Retro_Arcade"], "Nursery": ["Kids"], "Beach Ocean": ["Coastal", "Japandi"],
               "Travel": ["Modern", "Boho"]}
DEFAULT_DECOR = ["Modern", "Japandi", "Mid_Century", "Boho"]
# decor styles each room can be drawn in (Tony's style folder names); the first fits when nothing else does
ROOM_DECOR = {"Kitchen & dining": ["Food_and_Drink", "Retro", "Rustic_Farmhouse", "Modern"],
              "Game room": ["Gamer", "Retro_Arcade", "Mancave"],
              "Bathroom": ["Minimal", "Monochrome", "Botanical", "Japandi", "Coastal"],
              "Office": ["Modern", "Neutral", "Motivational", "Mid_Century", "Japandi"],
              "Kids": ["Kids"], "Nursery": ["Kids"], "Creative space": ["Boho", "Modern"]}
DECOR_WORDS = {"Japandi": "japandi", "Minimal": "minimalist", "Scandinavian": "scandinavian", "Modern": "modern",
               "Mid_Century": "mid-century modern", "Boho": "bohemian", "Victorian": "victorian",
               "Neutral": "warm neutral", "Food_and_Drink": "cozy", "Retro": "retro", "Rustic_Farmhouse":
               "rustic farmhouse", "Gamer": "gamer", "Retro_Arcade": "retro arcade", "Mancave": "moody mancave",
               "Monochrome": "monochrome", "Botanical": "botanical", "Coastal": "coastal", "Motivational": "modern",
               "Kids": "playful", "Unstyled": "modern"}
# style-folder name words that count as the same decor (e.g. 001_Japandi_Minimalist holds Japandi and Minimal)
DECOR_ALIASES = {"Japandi": ["japandi", "wabi"], "Minimal": ["minimal", "japandi"], "Scandinavian": ["scandi"],
                 "Modern": ["modern", "moody"], "Mid_Century": ["mid_century", "midcentury", "teak"],
                 "Boho": ["boho", "colorful", "trendy"], "Victorian": ["victorian"], "Neutral": ["neutral"],
                 "Food_and_Drink": ["food", "bar_cart", "bc_"], "Retro": ["retro"], "Rustic_Farmhouse": ["rustic",
                 "farmhouse"], "Gamer": ["gamer", "game_room"], "Retro_Arcade": ["arcade"], "Mancave": ["mancave"],
                 "Monochrome": ["monochrome"], "Botanical": ["botanical"], "Coastal": ["coastal"],
                 "Motivational": ["motivational"], "Kids": ["kids", "nursery"]}

# ---------- ratios ----------
RATIOS = ["2x3", "3x4", "4x5", "iso", "11x14"]           # the five print files every design is sold in
RATIO_VALUE = {"2x3": 2 / 3, "3x4": 0.75, "4x5": 0.8, "iso": 1 / 2 ** 0.5, "11x14": 11 / 14}
RATIO_LABEL = {"2x3": "2x3", "3x4": "3x4", "4x5": "4x5", "iso": "ISO / 5x7", "11x14": "11x14"}
RATIO_PROMPT = {"2x3": "2:3 ratio", "3x4": "3:4 ratio", "4x5": "4:5 ratio", "iso": "ISO ratio", "11x14": "11:14 ratio"}
PRINT_RATIO_TAG = {"2x3": "2x3", "3x4": "3x4", "4x5": "4x5", "iso": "ISO_A1", "11x14": "11x14"}
DEFAULT_WEIGHTS = {"2x3": 35, "3x4": 25, "4x5": 25, "iso": 10, "11x14": 5}


def norm(s):
    return re.sub(r"[^a-z0-9]+", "_", re.sub(r"^\d+_", "", str(s or "")).lower()).strip("_")


def decor_matches(decor, *texts):
    """True when a template / folder text names this decor style (alias words, see DECOR_ALIASES)."""
    words = DECOR_ALIASES.get(decor, [norm(decor)])
    t = " ".join(norm(x) for x in texts if x)
    return any(w in t for w in words)


def score_rooms(text, styles, value_key=None):
    """{room: (score, [reasons])} for every Etsy room and scene-only room. Internal; never shown as a matrix."""
    low = (text or "").lower()
    out = {}
    for room in ETSY_ROOMS + SCENE_ONLY_ROOMS:
        s, why = BASE[room], []
        for st in styles or []:
            d = STYLE_ROOM.get(st, {}).get(room)
            if d:
                s += d
                why.append(f"{st} {d:+g}")
        for pat, bonus in WORD_ROOM:
            if room in bonus and re.search(pat, low):
                s += bonus[room]
                why.append(f"'{re.search(pat, low).group(0)}' {bonus[room]:+g}")
        d = VALUE_ROOM.get(value_key or "", {}).get(room)
        if d:
            s += d
            why.append(f"{value_key} art {d:+g}")
        out[room] = (round(s, 2), why)
    return out


def decor_order(styles):
    """Decor styles for this design, best first (from its shop-style tags, then the defaults)."""
    seen = []
    for st in styles or []:
        for d in STYLE_DECOR.get(st, []):
            if d not in seen:
                seen.append(d)
    for d in DEFAULT_DECOR:
        if d not in seen:
            seen.append(d)
    return seen


def decors_for(room, styles):
    """Decor styles that make sense for this room and this design, best first."""
    pref = decor_order(styles)
    allowed = ROOM_DECOR.get(room)
    if not allowed:          # living room, bedroom, dorm, entryway, laundry: any general decor the design suits
        lounge = room in ("Bedroom", "Living room", "Dorm")
        return [d for d in pref if d not in ("Food_and_Drink", "Kids", "Gamer", "Retro_Arcade", "Coastal")
                or (d in ("Gamer", "Retro_Arcade") and lounge) or (d == "Coastal" and room in ("Bedroom", "Living room"))]
    hit = [d for d in pref if d in allowed]
    return hit + [d for d in allowed if d not in hit]


def ratio_targets(n, weights=None):
    """Largest-remainder split of n slots over the ratios by weight. {ratio: count}."""
    w = {r: float((weights or DEFAULT_WEIGHTS).get(r, 0)) for r in RATIOS}
    tot = sum(w.values()) or 1
    raw = {r: n * w[r] / tot for r in RATIOS}
    cnt = {r: int(raw[r]) for r in RATIOS}
    for r in sorted(RATIOS, key=lambda r: (-(raw[r] - cnt[r]), -w[r]))[:n - sum(cnt.values())]:
        cnt[r] += 1
    return cnt


def assign_ratios(slots, available, weights=None):
    """Give each planned slot a ratio: the allowed ratio (a folder exists for the room there) with the largest
    unmet share of the popularity target, ties to the more popular ratio. Mutates and returns slots."""
    w = weights or DEFAULT_WEIGHTS
    target = ratio_targets(len(slots), w)
    used = {r: 0 for r in RATIOS}
    for s in slots:
        ok = [r for r in RATIOS if r in available.get(s["room"], RATIOS)] or RATIOS
        r = max(ok, key=lambda r: (target[r] - used[r], w.get(r, 0)))
        used[r] += 1
        s["ratio"] = r
        s["ratio_label"] = RATIO_LABEL[r]
    return slots


def plan(picked, styles, text, value_key=None, slots=None, available=None, weights=None, locked=None):
    """The slot plan: [{slot, room, decor, ratio, by: tony|agent, reason}] over the room slots in fill order
    (`slots`, default ROOM_SLOTS = 3, 9-19). `available` = {room: [ratios with a
    room folder]} (rooms missing there can still be picked by Tony; the card then says a folder is needed).
    `locked` = {slot: {room, decor, ratio}} for slots whose image Tony approved; they keep their room."""
    picked = [r for r in (picked or []) if r in ETSY_ROOMS][:MAX_PICKS]
    available = available or {}
    locked = {int(k): v for k, v in (locked or {}).items()}
    order = list(slots or ROOM_SLOTS)
    n_max = len(order)
    scores = score_rooms(text, styles, value_key)
    slots, uses, decor_used = [], {}, {}

    def add(room, by, reason, decor=None):
        ds = decors_for(room, styles)
        k = decor_used.get(room, 0)
        decor = decor or ds[k % len(ds)]
        decor_used[room] = k + 1
        uses[room] = uses.get(room, 0) + 1
        slots.append({"room": room, "decor": decor, "by": by, "reason": reason})

    for room in picked:
        add(room, "tony", "your pick")
    # agent fill: greedy on score minus a repeat cost; rooms with no template folder are never auto-picked
    while len(slots) < n_max:
        cands = [(sc - REPEAT_COST * uses.get(r, 0), r, why) for r, (sc, why) in scores.items()
                 if ROOM_FOLDER.get(r) and (not available or available.get(r))]
        cands = [c for c in cands if c[0] >= MIN_SCORE]
        if not cands:
            break                       # fewer cards rather than padding
        val, room, why = max(cands, key=lambda c: (c[0], -ETSY_ROOMS.index(c[1]) if c[1] in ETSY_ROOMS else -99))
        if uses.get(room, 0) >= len(decors_for(room, styles)):
            scores[room] = (-99, why)    # out of distinct looks for this room
            continue
        add(room, "agent", ", ".join(why[:3]) or "a common room for wall art")
    for i, s in enumerate(slots):
        s["slot"] = order[i]
    for i, s in enumerate(slots):
        if s["slot"] in locked:
            s.update({k: locked[s["slot"]][k] for k in ("room", "decor", "ratio") if locked[s["slot"]].get(k)})
            s["locked"] = True
    free = [s for s in slots if not s.get("locked")]
    assign_ratios(free, available, weights)
    for s in slots:
        s.setdefault("ratio_label", RATIO_LABEL.get(s.get("ratio"), s.get("ratio")))
    return slots


def decor_words(decor):
    """Words for the image model: the known decor styles, else the style folder's own name in plain words."""
    return DECOR_WORDS.get(decor) or re.sub(r"[_\s]+", " ", str(decor or "modern")).strip().lower()


# ---------- how the art is shown (Tony 2026-11-16) ----------
# The printed area is drawn ONE flat onion-skin orange (SAM finds it against walls, mats and shadows; grey and white
# failed), never white. Presentations: a plain thin frame, a frame with a wide mat, or a stretched canvas in a natural
# wood floater frame. Chosen per room + decor, deterministic (same inputs -> same pick), weighted by what suits the look.
INSERT_COLOUR = "onion-skin orange (a pale peachy-orange, roughly RGB 250, 215, 170)"
PRESENTATION_WEIGHTS = {            # decor -> (frame, mat, canvas) weights
    "Victorian": (30, 70, 0), "Neutral": (40, 40, 20), "Mid_Century": (40, 35, 25), "Japandi": (40, 30, 30),
    "Minimal": (40, 30, 30), "Scandinavian": (40, 30, 30), "Modern": (40, 30, 30), "Boho": (35, 20, 45),
    "Coastal": (35, 25, 40), "Botanical": (40, 30, 30), "Kids": (60, 0, 40), "Gamer": (70, 0, 30),
    "Retro_Arcade": (70, 0, 30), "Mancave": (60, 20, 20), "Rustic_Farmhouse": (40, 20, 40)}
PRESENTATION_DEFAULT = (50, 25, 25)
PRESENTATIONS = ("frame", "mat", "canvas")


def presentation_for(room, decor, ratio):
    import hashlib
    w = PRESENTATION_WEIGHTS.get(decor, PRESENTATION_DEFAULT)
    n = int(hashlib.sha1(f"{room}|{decor}|{ratio}".encode()).hexdigest()[:8], 16) % sum(w)
    for kind, x in zip(PRESENTATIONS, w):
        if n < x:
            return kind
        n -= x
    return "frame"


# Tony 2026-11-17: the orange blank bounced orange onto the gap, the frame's inner lip and the canvas side edges (real
# art bounces its own colour, never orange). Worded in the POSITIVE direction: the orange surface is dead matte and
# evenly lit, and every surface around it keeps its own colour. The ROOM keeps its own light (direct window light with
# soft-edged, clearly visible shadows is welcome: Tony's favourite is the Bedroom Wabi vertical); only the printed
# surface is evenly lit. app/despill.py removes whatever orange bounce still gets drawn.
_PRINT_AREA = ("The artwork's printed area is a single flat, plain, empty, blank " + INSERT_COLOUR + " surface with a "
               "dead-matte, non-reflective finish like unglazed matte card: one even tone from edge to edge, evenly lit "
               "across its whole face, glare-free and free of hot spots, so it reads as one clean flat colour. The "
               "orange appears only on the front face of the printed area. Its matte surface absorbs the light, so "
               "every surface next to it keeps its own natural colour in the room's own light: the frame and its inner "
               "edge stay their wood, metal or paint colour, any gap stays a natural neutral shadow, and the wall stays "
               "the wall colour. ")
_PRESENT_TEXT = {
    "frame": ("The artwork hangs in a thin frame (natural oak, walnut or brass most of the time; black only occasionally, when it clearly suits the room). "
              "The orange printed surface fills the whole frame opening right up to the inside edge of the frame on all "
              "four sides; the frame's inner edge keeps the frame's own colour right up to the orange. Any glazing is "
              "clear, invisible museum glass. NEGATIVE: no mat, no matte border, no passe-partout, no white border, no "
              "margin, no inner rectangle, no bevel line."),
    "mat": ("The artwork hangs in a refined thin frame with a WIDE off-white mat border (passe-partout) of exactly even "
            "width on all four sides, about 10% of the frame height, with a crisp bevelled window cut. The flat orange "
            "printed surface sits inside the mat window; the mat is clearly lighter than the orange so the window edge "
            "is sharp. The mat and its bevel stay their own clean off-white right up to the orange edge. Any glazing "
            "is clear, invisible museum glass."),
    # Tony 2026-11-17: orange side edges the same orange as the face made SAM take face + side edge as one shape
    # (art ran ~14 px onto the side edge); the side edges are now plain white, a clearly different tone from the face
    "canvas": ("The artwork is a thick stretched gallery canvas, 1.5 to 2 inches (4-5 cm) deep, mounted inside a thin "
               "NATURAL LIGHT WOOD floater frame (floating frame), a warm natural wood colour, never black or dark. "
               "Only the FRONT FACE of the canvas is orange. The canvas side edges (the wrap around the stretcher "
               "bars) are plain clean WHITE, clearly a different tone from the orange face, so the front face ends in "
               "one crisp straight line where the white side edge begins; the side edges are never orange, never "
               "black: they stay clean white in the light and neutral grey where they turn into shadow. The canvas "
               "sits inset inside the frame with a narrow even visible gap of about 0.5 cm between the canvas edge and "
               "the frame's inner lip; the gap holds a natural soft shadow in the neutral tones of the wood, lighter "
               "than black, so the pale wood frame, the thin gap, the white canvas side edge and the orange face are "
               "clearly separate bands. The piece stands off the wall by the canvas depth and casts a natural shadow "
               "on the wall that follows the room's light direction. Camera: a slight 3/4 view so the depth shows."),
    # Tony 2026-11-18 test: a plain stretched gallery canvas hung straight on the wall, no floater frame (build_psd
    # treats it as "canvas": same SAM face path, wrap strips and despill)
    "canvas_bare": ("The artwork is a thick stretched gallery canvas, 1.5 to 2 inches (4-5 cm) deep, hung directly on "
                    "the wall with NO frame of any kind. Only the FRONT FACE of the canvas is orange. The canvas side "
                    "edges (the wrap around the stretcher bars) are plain clean WHITE, clearly a different tone from "
                    "the orange face, so the front face ends in one crisp straight line where the white side edge "
                    "begins; the side edges are never orange, never black: they stay clean white in the light and "
                    "neutral grey where they turn into shadow. The canvas stands off the wall by its depth and casts a "
                    "natural soft shadow on the wall that follows the room's light direction. Camera: a slight 3/4 "
                    "view so the depth shows.")}


# ---------- scene look variety (Tony 2026-11-17, widened 2026-11-19) ----------
# Every NEW scene gets a weighted RANDOM "look". v1 (2026-11-17) varied only the light: light style, photographer
# (2 options), time of day, season, sun direction, and hardcoded "Camera angle: 3/4 corner", so every scene looked
# shot by the same photographer. v2 (2026-11-19) adds camera, lens, focus, foreground, display, composition, walls,
# floor, furniture and frame finish, and a 12-persona photographer/stylist axis (key name "photographer" kept), from
# the research in Research/Etsy_Mockup_Look_Findings.md + Etsy_Mockup_Look_Database.json (105 top Etsy listings from
# 37 shops, 46 of Tony's templates, 5 of our scenes). REFERENCE for variety, never copies of a listing.
#
# Weight rule (v2): weight = round(10 * sqrt(p)), p = the research's blended percentage for that option (market rooms
# + Tony's templates, Findings section 4). Square-root flattening turns e.g. straight-on 48 vs 3/4 7 (a 7:1 lead)
# into 69 vs 26 (about 2.6:1), so the over-represented looks still lead but the rare ones really appear. Two
# deliberate exceptions: black frame uses the MARKET-only 11% (Tony's "black only occasionally" rule), and the 85 mm
# short telephoto is fixed at 10 (about 7%) because it was never observed anywhere: UNTESTED.
#
# Room and decor only nudge the odds (multipliers clamped to 0.5-2.0, so a nudge never reaches zero); the persona
# picked earlier nudges walls, floor, furniture and display the same way (PERSONA_NUDGE). Hard gates (_look_gate)
# remove an option only where it never belongs (a nursery persona outside kids' rooms, gold frames outside vintage
# decors ...). Picks follow LOOK_ORDER; a later axis keeps only the options that make sense with the earlier picks
# (_look_fits: physical sense of light, camera geometry, and the pipeline safety rules below).
#
# Pipeline safety (orange insert + SAM + independent edge check), hard constraints:
#   - never an orange, peach, apricot, terracotta, coral or rust wall (too close to the onion-skin orange insert);
#   - the frame stands out from the wall in tone (frame_finish fits per wall; canvas floater gets a darker wood
#     sentence on pale warm walls); blush walls only with a black or walnut frame;
#   - nothing in front of the art overlaps the frame (LOOK_GUARD_FRAME, foreground at the image edge only);
#   - the art face is flat, upright, matte, evenly lit and in sharp focus (LOOK_GUARD + _PRINT_AREA unchanged);
#   - panelling only with hung art centred inside one panel (WAINSCOT_RULE intact); low camera never close under
#     hung art (it would need a steep upward tilt that keystones the opening).
#
# The pick is saved in template.json ("look", with its seed and version). Replay: pick_look(room, decor,
# override=man["look"]) (the recorded version is read from it) or pick_look(room, decor, seed=s, version=v). A v1 look
# replays with the v1 tables and gives the exact v1 prompt (byte-identical, tested). Every phrase is positive wording.
LOOK_VERSION = 2

# ----- v1 tables (2026-11-17), frozen for replay of looks saved before 2026-11-19 -----
LOOK_V1_ORDER = ("light_style", "photographer", "time_of_day", "season", "sun_direction")
LOOK_V1_PHOTOGRAPHER = {
    "magazine": (40, "Photographer style: an architecture and interiors magazine shoot: composed, balanced "
                     "framing with straight verticals, clean and considered styling with only props that belong "
                     "in the room, carefully balanced exposure."),
    "lifestyle": (60, "Photographer style: a stylish home-decor creator who stages well and understands light "
                      "and framing, photographing a real home: natural, effortless styling with a little visible "
                      "life (a throw casually draped, a book left open, a cup on a side table), slightly casual "
                      "framing that still feels well composed, beautiful natural light that is good rather than "
                      "perfect; it reads as a genuine photograph of a real, lived-in home.")}
_LIGHT_AXES = {   # shared by v1 and v2 (unchanged since 2026-11-17)
    "light_style": {
        # Tony's favourite (his Bedroom Wabi vertical template): the healthiest weight
        "soft_direct": (35, "Light style: direct window light with soft-edged, clearly visible shadows: warm sunlit "
                            "patches with gently feathered edges on the floor and the wall, calm and inviting."),
        "crisp_direct": (15, "Light style: bright, crisp direct sun with sharper-edged shadows and lively, "
                             "confident contrast across the room."),
        "dappled": (15, "Light style: sunlight filtered through slatted blinds or the leaves of a tree outside, "
                        "casting a dappled, patterned shadow across the floor and the wall to one side of the "
                        "artwork."),
        "golden_low": (15, "Light style: low, warm golden sun with long soft shadows stretching across the room and "
                           "a warm amber glow on the wall."),
        "soft_even": (20, "Light style: soft, even daylight from a bright overcast sky, with gentle open shadows and "
                          "an airy, calm feel.")},
    "time_of_day": {
        "morning": (30, "mid-morning"),
        "midday": (15, "around midday"),
        "late_afternoon": (30, "late afternoon, around 5 pm"),
        "golden_hour": (25, "golden hour, the last hour before sunset")},
    "season": {
        "spring": (25, ("on a fresh spring day, the sun bright and clean with a light, slightly cool warmth",
                        "on a fresh spring day, with clean, slightly cool daylight")),
        "summer": (25, ("in summer, with strong, bright, clear sunlight and a fresh, airy feel",
                        "in summer, with bright, airy daylight")),
        "autumn": (30, ("in autumn, when the sun sits low and warm and reaches deep into the room",
                        "on an autumn day, with soft, warm, muted daylight")),
        "winter": (20, ("in winter, when the sun stays low even at midday, pale and clean, with long thin shadows",
                        "on a winter day, with cool, pale, quiet daylight"))},
    "sun_direction": {
        "facing_sun": (35, "The window faces the sun, so sunlight falls straight in and lands on the floor and on "
                           "the wall near the art."),
        "side_window": (45, "The window is off to one side of the art wall, so the light rakes across the wall from "
                            "that side and shows its texture."),
        "away_from_sun": (20, "The window faces away from the sun, so the room fills with soft, reflected, open "
                              "daylight.")}}
LOOK_V1_AXES = {"light_style": _LIGHT_AXES["light_style"], "photographer": LOOK_V1_PHOTOGRAPHER,
                **{a: _LIGHT_AXES[a] for a in ("time_of_day", "season", "sun_direction")}}
LOOK_V1_NUDGE_DECOR = {
    "Japandi": {"soft_direct": 1.3, "soft_even": 1.2, "magazine": 1.2},
    "Minimal": {"soft_even": 1.3, "magazine": 1.3, "crisp_direct": 1.2},
    "Scandinavian": {"soft_even": 1.2, "morning": 1.2, "winter": 1.3},
    "Modern": {"crisp_direct": 1.3, "magazine": 1.2},
    "Mid_Century": {"golden_low": 1.4, "late_afternoon": 1.2, "autumn": 1.2},
    "Boho": {"dappled": 1.6, "lifestyle": 1.3, "summer": 1.2},
    "Botanical": {"dappled": 1.8, "spring": 1.3},
    "Coastal": {"crisp_direct": 1.4, "summer": 1.5, "facing_sun": 1.2},
    "Victorian": {"magazine": 1.5, "golden_low": 1.2, "autumn": 1.2},
    "Rustic_Farmhouse": {"golden_low": 1.4, "autumn": 1.4, "lifestyle": 1.2},
    "Neutral": {"soft_direct": 1.2, "lifestyle": 1.2},
    "Gamer": {"soft_even": 1.3, "golden_low": 1.2, "lifestyle": 1.3},
    "Retro_Arcade": {"golden_low": 1.3, "lifestyle": 1.2},
    "Mancave": {"golden_low": 1.4, "autumn": 1.3, "winter": 1.2},
    "Kids": {"soft_even": 1.2, "lifestyle": 1.3, "morning": 1.3}}
LOOK_V1_NUDGE_ROOM = {
    "Bedroom": {"morning": 1.3, "soft_direct": 1.2},
    "Living room": {"late_afternoon": 1.2, "golden_hour": 1.2},
    "Office": {"morning": 1.4, "magazine": 1.2, "crisp_direct": 1.2},
    "Kitchen & dining": {"morning": 1.4, "crisp_direct": 1.2},
    "Bathroom": {"soft_even": 1.3, "morning": 1.3},
    "Entryway": {"magazine": 1.3, "side_window": 1.2},
    "Dorm": {"lifestyle": 1.5, "late_afternoon": 1.2},
    "Kids": {"lifestyle": 1.3, "soft_even": 1.2},
    "Nursery": {"soft_even": 1.4, "morning": 1.2, "lifestyle": 1.2},
    "Game room": {"golden_low": 1.2, "lifestyle": 1.2},
    "Creative space": {"lifestyle": 1.4, "side_window": 1.2}}

# ----- v2 tables (2026-11-19) -----
LOOK_ORDER = ("light_style", "photographer", "time_of_day", "season", "sun_direction", "display", "camera_height",
              "camera_angle", "distance", "lens", "foreground", "depth_of_field", "composition", "wall_palette",
              "wall_treatment", "floor", "furniture_finish", "frame_finish")
LOOK_AXES = {   # axis -> {option: (weight, prompt phrase)}; option names are unique across axes (nudges key on them)
    "light_style": _LIGHT_AXES["light_style"],
    # 12 photographer / stylist personas (replaces magazine / lifestyle). Each brings its own props, so the old
    # throw + open book + mug trio stops repeating. No light, lamp, wall or floor words here: those are their own
    # axes. p = persona/mood mix of market slot 1 + Tony's templates.
    "photographer": {
        "warm_lifestyle_creator": (40, "Photographer and stylist: a home-decor creator photographing her own lived-in "
                                       "home: natural, unfussy styling with one or two things she really uses, "
                                       "slightly casual framing that still feels composed."),
        "airy_scandi_catalogue": (36, "Photographer and stylist: a bright Scandinavian interiors catalogue: pale, airy "
                                      "and uncluttered, one green plant, crisp tidy styling."),
        "midcentury_magazine": (35, "Photographer and stylist: a mid-century design magazine: balanced framing, a few "
                                    "sculptural objects such as a ceramic vase and a stack of design books, warm wood "
                                    "tones with mustard or olive accents."),
        "editorial_minimal": (32, "Photographer and stylist: a minimalist architecture magazine: calm space, very few "
                                  "objects, strong clean lines and generous empty wall."),
        "parisian_apartment": (30, "Photographer and stylist: a Parisian apartment story: elegant and slightly "
                                   "undone, one vintage chair or stool, a stack of art books, fresh stems in a simple "
                                   "vase."),
        "trendy_girl_apartment": (28, "Photographer and stylist: a stylish young renter's home: playful colour, a "
                                      "fluted or curvy side piece, dried stems in a vase, a collected, lived-with "
                                      "feel."),
        "bold_colour_eclectic": (26, "Photographer and stylist: an eclectic, colour-confident home: patterned "
                                     "cushions, a mix of vintage and modern pieces, a confident but considered "
                                     "palette."),
        "japandi_calm": (26, "Photographer and stylist: a quiet Japandi home: low wooden furniture, handmade "
                             "ceramics, a single branch in a vase, a calm, restrained palette."),
        "moody_dark_academia": (22, "Photographer and stylist: a moody, scholarly study: rich deep tones, old "
                                    "leather-bound books, a brass object or two, a hushed atmosphere, while the "
                                    "artwork itself stays softly and evenly lit."),
        "coastal_grandmillennial": (22, "Photographer and stylist: a breezy coastal cottage: white and pale blue, "
                                        "washed linen, a striped cushion, a woven basket."),
        "cottage_farmhouse": (22, "Photographer and stylist: a country farmhouse: painted wood, a woven basket, a jug "
                                  "of garden flowers, honest well-used pieces."),
        "playful_nursery": (17, "Photographer and stylist: a soft, gentle children's room: a wooden toy shelf, pale "
                                "colours, a knitted toy.")},   # gated: Kids / Nursery only
    "time_of_day": _LIGHT_AXES["time_of_day"],
    "season": _LIGHT_AXES["season"],
    "sun_direction": _LIGHT_AXES["sun_direction"],
    # market rooms: floor lean 58 / on furniture 19 / hung 22; Tony: hung 93 -> blended 38 / 27 / 22 / 13
    "display": {
        "hung_over_furniture": (62, "Display: the artwork hangs on the wall centred above the {anchor}, with clear "
                                    "wall on every side of the frame."),
        "floor_lean": (52, "Display: the artwork stands on the floor leaning against the wall, tilted back only "
                           "slightly, its bottom edge resting on the floor and its face upright and flat."),
        "lean_on_furniture": (47, "Display: the artwork rests on top of the {surface}, leaning against the wall, "
                                  "tilted back only slightly, its face upright and flat."),
        "hung_bare_wall": (36, "Display: the artwork hangs alone on a calm stretch of wall with generous space around "
                               "it.")},
    # market rooms: low 61 / eye 31; Tony: eye 96 -> blended eye 50 / low 32 / counter 10 / seated 8
    "camera_height": {
        "eye": (71, "Camera height: standing eye height, about 160 cm."),
        "low": (57, "Camera height: low, about knee to hip height, looking very slightly up, verticals kept "
                    "straight."),
        "counter": (32, "Camera height: level with the top of the furniture under the artwork, about 90 cm."),
        "seated": (28, "Camera height: seated eye height, about 110 cm, as if photographed from a chair or the "
                       "bed.")},
    # market rooms: straight 53 / slight 39 / 3/4 8; Tony 67 / 20 / 13; ours was 3/4 100 -> blended 48/13/13/7/7/12
    "camera_angle": {
        "straight_on": (69, "Camera: square-on to the art wall, the frame level and parallel to the picture edges, "
                            "verticals straight."),
        "slight_left": (36, "Camera: a slight angle from the left, about 10 degrees off square, the wall receding "
                            "gently to the right."),
        "slight_right": (36, "Camera: a slight angle from the right, about 10 degrees off square, the wall receding "
                             "gently to the left."),
        "three_quarter_left": (26, "Camera: a 3/4 corner view from the left, about 30 degrees off square, so the "
                                   "depth of the room reads clearly."),
        "three_quarter_right": (26, "Camera: a 3/4 corner view from the right, about 30 degrees off square, so the "
                                    "depth of the room reads clearly."),
        "through_doorway": (35, "Camera: standing in the next room, looking straight through an open doorway at the "
                                "art wall; the painted door frame edges the picture on one or both sides, well clear "
                                "of the artwork.")},
    # market rooms: close 50 / medium 39 / wide 11; Tony: wide 44 / medium 42 / close 13 -> blended 35 / 40 / 25
    "distance": {
        "close": (59, "Framing: a close vignette; the artwork fills about half the image height (at most about "
                      "60%), with one or two objects around it and clear wall around all four sides of the "
                      "frame."),
        "medium": (63, "Framing: a medium shot of the art wall and what sits below it, the artwork about a third of "
                       "the image height."),
        "wide": (50, "Framing: a wide view of the room for scale, the artwork about a fifth of the image height and "
                     "still the clear focal point.")},
    # market normal 100%; Tony wide 7%
    "lens": {
        "lens_normal": (87, "Lens: a natural 35-50 mm view with true proportions."),
        "lens_wide": (41, "Lens: a 24-28 mm wide view that shows more of the room, verticals kept straight."),
        # UNTESTED: telephoto was never observed in the 156 researched images; kept rare on purpose
        "lens_short_tele": (10, "Lens: an 85 mm view from further back, the room gently compressed behind the "
                                "art.")},
    # market rooms 58% / Tony 80% have something at the image edge; it never touches the frame
    "foreground": {
        "clear_foreground": (59, "Foreground: the space in front of the art wall is clear."),
        "furniture_edge": (50, "Foreground: the arm of a sofa, the back of a chair or the corner of a bed enters one "
                               "edge of the picture, well clear of the frame."),
        "plant_leaves": (37, "Foreground: a few leaves of a large houseplant enter one side of the picture, well "
                             "clear of the frame."),
        "side_table": (37, "Foreground: a small side table with one or two everyday objects stands at one edge of "
                           "the picture, well clear of the frame."),
        "throw_or_rug": (35, "Foreground: the edge of a rug or a folded throw runs along the bottom of the picture, "
                             "well below the frame.")},
    # market deep 96%; Tony soft foreground 9%. The art and frame are ALWAYS sharp.
    "depth_of_field": {
        "deep_focus": (88, "Focus: everything sharp from front to back, the artwork crisp."),
        "soft_background": (35, "Focus: the artwork and its frame are crisp; only the far end of the room softens "
                                "gently."),
        "soft_foreground": (32, "Focus: the artwork and its frame are crisp; only the nearest object at the edge of "
                                "the picture is softly out of focus.")},
    "composition": {
        "centred": (67, "Composition: the artwork near the centre of the picture."),
        "thirds_left": (39, "Composition: the artwork on the left third of the picture, the room opening to the "
                            "right."),
        "thirds_right": (39, "Composition: the artwork on the right third of the picture, the room opening to the "
                             "left."),
        "beside_window": (39, "Composition: the artwork on the wall beside a window, the window partly in the "
                              "picture and well clear of the frame."),
        "offset_furniture": (32, "Composition: the artwork offset towards one end of the furniture below it.")},
    # market rooms: white/cream 64, greige 17, grey 8, blush 6; Tony adds teal, blush, sage/forest, dark.
    # NEVER orange / peach / apricot / terracotta / coral / rust (the onion-skin orange insert colour)
    "wall_palette": {
        "warm_white": (56, "Walls: a soft warm white."),
        "ivory_cream": (36, "Walls: a calm ivory cream."),
        "greige": (36, "Walls: a light warm greige."),
        "soft_grey": (32, "Walls: a soft pale grey."),
        "sage": (30, "Walls: a muted sage green."),
        "dusty_blue_teal": (28, "Walls: a deep muted teal or dusty blue."),
        "deep_moody": (26, "Walls: a deep moody colour (charcoal, deep navy or forest green)."),
        "blush": (22, "Walls: a pale dusty pink."),                 # fits: black or walnut frame only
        "colour_block": (20, "Walls: the art wall painted a confident colour block in a cool or deep shade (olive, "
                             "navy, forest green or plum) that suits the furniture.")},
    "wall_treatment": {
        "plain_paint": (72, "The wall is smooth painted plaster."),
        "limewash": (35, "The wall has a soft limewash plaster texture."),
        "panelled": (40, "The wall has tall painted panelling in the wall colour; the artwork hangs centred inside "
                         "one large panel, with clear wall on every side of the frame."),   # fits: hung only
        "shiplap": (28, "The wall is painted vertical shiplap boards in the wall colour."),
        "brick": (22, "The wall is painted brick in the wall colour, with a fine, even texture."),
        "wallpaper": (26, "The wall has a quiet small-pattern wallpaper in soft tones close to the wall colour.")},
    "floor": {
        "light_herringbone": (50, "Floor: light oak herringbone."),
        "light_plank": (50, "Floor: wide light oak planks."),
        "honey_wood": (37, "Floor: honey-toned wood planks."),
        "dark_wood": (30, "Floor: dark walnut-toned wood."),
        "rug_floor": (39, "Floor: a large textured rug covers most of the floor."),
        "checker_tile": (24, "Floor: classic checkerboard tile."),
        "stone_concrete": (24, "Floor: pale polished concrete or stone.")},
    "furniture_finish": {
        "light_oak_wood": (49, "Furniture: light oak and ash."),
        "walnut_teak": (55, "Furniture: warm walnut and teak."),
        "painted_lacquer": (35, "Furniture: the main piece painted or lacquered (black, white or a soft colour)."),
        "rattan_cane": (32, "Furniture: rattan and cane mixed with wood."),
        "colour_upholstery": (40, "Furniture: seating upholstered in a confident colour (mustard, olive, teal, deep "
                                  "blue or blush)."),
        "white_cream": (28, "Furniture: white and cream with linen upholstery.")},
    # frame and mat presentations only (a canvas keeps its natural-wood floater). Market rooms oak 64 / walnut 14 /
    # black 11 / white 8 / gold 3; Tony oak 49 / black 27. Black uses the market 11% (Tony: black only occasionally).
    "frame_finish": {
        "oak_frame": (69, "a thin natural light oak frame"),
        "black_frame": (33, "a thin black frame with a soft satin finish"),
        "walnut_frame": (37, "a thin warm walnut frame"),
        "white_frame": (30, "a thin white painted frame"),
        "gold_frame": (26, "a thin antique gold frame")}}    # gated: vintage / classical decors only
_SUNNY = ("soft_direct", "crisp_direct", "dappled", "golden_low")
# decor (DECOR_ALIASES key, matched with decor_matches) or room -> {option: multiplier}; clamped to 0.5-2.0 in
# look_weights, so nudging changes the odds but never removes an option.
LOOK_NUDGE_DECOR = {
    "Japandi": {"soft_direct": 1.3, "soft_even": 1.2, "japandi_calm": 1.8, "airy_scandi_catalogue": 1.3, "low": 1.3,
                "floor_lean": 1.3, "close": 1.2, "limewash": 1.4},
    "Minimal": {"soft_even": 1.3, "crisp_direct": 1.2, "editorial_minimal": 1.6, "airy_scandi_catalogue": 1.3,
                "hung_bare_wall": 1.3},
    "Scandinavian": {"soft_even": 1.2, "morning": 1.2, "winter": 1.3, "airy_scandi_catalogue": 1.8,
                     "light_plank": 1.3},
    "Modern": {"crisp_direct": 1.3, "editorial_minimal": 1.3, "warm_lifestyle_creator": 1.2, "black_frame": 1.5},
    "Mid_Century": {"golden_low": 1.4, "late_afternoon": 1.2, "autumn": 1.2, "midcentury_magazine": 2.0,
                    "walnut_teak": 1.6, "colour_upholstery": 1.4, "hung_over_furniture": 1.3},
    "Boho": {"dappled": 1.6, "summer": 1.2, "trendy_girl_apartment": 1.6, "bold_colour_eclectic": 1.4,
             "rattan_cane": 1.8, "rug_floor": 1.4, "plant_leaves": 1.4},
    "Botanical": {"dappled": 1.8, "spring": 1.3, "plant_leaves": 1.6, "sage": 1.5, "japandi_calm": 1.2},
    "Coastal": {"crisp_direct": 1.4, "summer": 1.5, "facing_sun": 1.2, "coastal_grandmillennial": 2.0,
                "warm_white": 1.3, "dusty_blue_teal": 1.4, "light_plank": 1.3},
    "Victorian": {"golden_low": 1.2, "autumn": 1.2, "parisian_apartment": 1.8, "moody_dark_academia": 1.5,
                  "gold_frame": 1.8, "panelled": 1.6, "straight_on": 1.3},
    "Rustic_Farmhouse": {"golden_low": 1.4, "autumn": 1.4, "cottage_farmhouse": 2.0, "warm_lifestyle_creator": 1.3,
                         "honey_wood": 1.5, "shiplap": 1.6, "walnut_frame": 1.4},
    "Neutral": {"soft_direct": 1.2, "warm_lifestyle_creator": 1.4, "greige": 1.4},
    "Gamer": {"soft_even": 1.3, "golden_low": 1.2, "moody_dark_academia": 1.4, "bold_colour_eclectic": 1.4,
              "deep_moody": 1.6, "black_frame": 1.6},
    "Retro_Arcade": {"golden_low": 1.3, "bold_colour_eclectic": 1.6, "colour_block": 1.5},
    "Mancave": {"golden_low": 1.4, "autumn": 1.3, "winter": 1.2, "moody_dark_academia": 1.8, "deep_moody": 1.8,
                "dark_wood": 1.5},
    "Kids": {"soft_even": 1.2, "morning": 1.3, "playful_nursery": 1.8, "wallpaper": 1.4, "eye": 1.2}}
LOOK_NUDGE_ROOM = {
    "Bedroom": {"morning": 1.3, "soft_direct": 1.2, "seated": 1.5, "hung_over_furniture": 1.3,
                "soft_foreground": 1.3, "warm_lifestyle_creator": 1.2},
    "Living room": {"late_afternoon": 1.2, "golden_hour": 1.2, "furniture_edge": 1.2},
    "Office": {"morning": 1.4, "crisp_direct": 1.2, "editorial_minimal": 1.4, "lean_on_furniture": 1.4, "close": 1.3},
    "Kitchen & dining": {"morning": 1.4, "crisp_direct": 1.2, "counter": 1.8, "lean_on_furniture": 1.5,
                         "checker_tile": 1.6, "cottage_farmhouse": 1.3},
    "Bathroom": {"soft_even": 1.3, "morning": 1.3, "close": 1.4, "hung_bare_wall": 1.4, "stone_concrete": 1.4},
    "Entryway": {"editorial_minimal": 1.3, "side_window": 1.2, "lean_on_furniture": 1.3, "through_doorway": 1.5},
    "Dorm": {"warm_lifestyle_creator": 1.5, "trendy_girl_apartment": 1.5, "late_afternoon": 1.2},
    "Kids": {"warm_lifestyle_creator": 1.3, "soft_even": 1.2, "playful_nursery": 1.8},
    "Nursery": {"soft_even": 1.4, "morning": 1.2, "playful_nursery": 2.0},
    "Game room": {"golden_low": 1.2, "moody_dark_academia": 1.3, "bold_colour_eclectic": 1.3},
    "Creative space": {"warm_lifestyle_creator": 1.4, "side_window": 1.2, "lean_on_furniture": 1.4,
                       "bold_colour_eclectic": 1.3}}
PERSONA_NUDGE = {   # photographer persona (picked 2nd) -> {later option: multiplier}, same clamp
    "warm_lifestyle_creator": {"furniture_edge": 1.3, "throw_or_rug": 1.3, "hung_over_furniture": 1.2},
    "airy_scandi_catalogue": {"warm_white": 1.5, "soft_grey": 1.3, "light_plank": 1.4, "light_oak_wood": 1.4,
                              "plant_leaves": 1.4},
    "midcentury_magazine": {"walnut_teak": 1.8, "colour_upholstery": 1.5, "hung_over_furniture": 1.3,
                            "offset_furniture": 1.4},
    "editorial_minimal": {"hung_bare_wall": 1.8, "clear_foreground": 1.5, "stone_concrete": 1.6, "centred": 1.2,
                          "lens_wide": 1.3},
    "parisian_apartment": {"panelled": 2.0, "light_herringbone": 2.0, "floor_lean": 1.4, "ivory_cream": 1.3},
    "trendy_girl_apartment": {"blush": 1.8, "sage": 1.5, "rattan_cane": 1.5, "low": 1.3, "checker_tile": 1.5},
    "bold_colour_eclectic": {"colour_block": 2.0, "dusty_blue_teal": 1.6, "colour_upholstery": 1.6,
                             "wallpaper": 1.5},
    "japandi_calm": {"limewash": 1.6, "light_oak_wood": 1.5, "low": 1.3, "floor_lean": 1.3,
                     "clear_foreground": 1.3},
    "moody_dark_academia": {"deep_moody": 2.0, "dark_wood": 1.8, "walnut_teak": 1.4, "soft_background": 1.3},
    "coastal_grandmillennial": {"dusty_blue_teal": 1.5, "shiplap": 1.8, "white_cream": 1.6, "light_plank": 1.3},
    "cottage_farmhouse": {"shiplap": 1.6, "honey_wood": 1.6, "painted_lacquer": 1.3, "lean_on_furniture": 1.4},
    "playful_nursery": {"wallpaper": 1.8, "eye": 1.2, "hung_over_furniture": 1.3, "painted_lacquer": 1.3}}
LOOK_NUDGE_RANGE = (0.5, 2.0)
# what the art hangs over / rests on, per room (display phrases {anchor} / {surface})
ROOM_ANCHOR = {"Living room": "sofa", "Bedroom": "bed headboard", "Dorm": "bed", "Office": "desk",
               "Kitchen & dining": "dining table", "Bathroom": "freestanding bathtub", "Entryway": "console table",
               "Laundry": "folding counter", "Kids": "bed", "Nursery": "crib", "Game room": "sofa",
               "Creative space": "work table"}
ROOM_SURFACE = {"Living room": "sideboard", "Bedroom": "dresser", "Dorm": "desk", "Office": "desk",
                "Kitchen & dining": "kitchen counter", "Bathroom": "wooden bench", "Entryway": "console table",
                "Laundry": "countertop", "Kids": "low bookshelf", "Nursery": "dresser", "Game room": "low media console",
                "Creative space": "work table"}
LOOK_AT_BUILD = "at_build"          # preview only (Templates gap tile): the look is picked when Build is clicked
# Kept in EVERY variant (positive wording): strong or patterned shadows stay off the print surface, outlines stay crisp
LOOK_GUARD = ("Whatever the light, the artwork itself hangs in calm, even light: sun patches, shadows and any blind or "
              "leaf pattern land on the floor and on the wall around the frame, while the whole printed area stays "
              "one flat, evenly lit tone; the frame, the mat or canvas edge and the wall each stay clearly distinct, "
              "with crisp, unbroken outlines. ")
# v2 addition (research pipeline-safety table): four unbroken edges for SAM and the edge check, art face sharp
LOOK_GUARD_FRAME = ("The whole frame sits inside the picture with clear wall on all four sides; nothing in front of it "
                    "overlaps any part of the frame. The artwork face is flat, upright and in sharp focus, and the "
                    "frame stands out clearly from the wall in tone. ")
_HUNG = ("hung_over_furniture", "hung_bare_wall")
_LEAN = ("floor_lean", "lean_on_furniture")
_PALE_WARM_WALLS = ("ivory_cream", "greige", "blush")     # + warm_white with limewash (see _pale_warm)
_VINTAGE_DECORS = ("Victorian", "Rustic_Farmhouse", "Botanical", "Neutral")
_GAMER_PERSONAS = ("warm_lifestyle_creator", "editorial_minimal", "bold_colour_eclectic", "moody_dark_academia",
                   "trendy_girl_apartment")


def _pale_warm(look):
    w = look.get("wall_palette")
    return w in _PALE_WARM_WALLS or (w == "warm_white" and look.get("wall_treatment") == "limewash")


def _look_gate(room, decor, axis, key):
    """False where an option never belongs in this room / decor (v2). Unlike nudges, a gate removes the option."""
    dm = lambda *ds: any(decor_matches(d, decor) for d in ds)     # noqa: E731
    young = room in ("Kids", "Nursery")
    if axis == "photographer":
        if dm("Gamer", "Retro_Arcade", "Mancave") and key not in _GAMER_PERSONAS:   # a coastal gamer den reads wrong
            return False
        return {"playful_nursery": young, "trendy_girl_apartment": room not in ("Office", "Kids", "Nursery"),
                "moody_dark_academia": not young, "cottage_farmhouse": room != "Game room"}.get(key, True)
    if axis == "display":
        return not (key == "floor_lean" and room == "Bathroom")
    if axis == "camera_height":
        return not (key == "seated" and room in ("Bathroom", "Entryway", "Laundry"))
    if axis == "wall_palette":
        return not (key == "deep_moody" and young)
    if axis == "wall_treatment":
        if key == "panelled":
            return not dm("Gamer", "Retro_Arcade", "Mancave", "Kids")
        if key == "wallpaper":
            return young or room == "Bathroom" or dm("Kids", "Victorian", "Boho", "Coastal", "Botanical")
        if key == "brick":
            return room not in ("Bathroom", "Nursery")
    if axis == "floor":
        if key == "checker_tile":
            return room not in ("Bedroom", "Nursery", "Kids", "Office")
        if key == "rug_floor":
            return room not in ("Bathroom", "Laundry")
    if axis == "frame_finish" and key == "gold_frame":
        return dm(*_VINTAGE_DECORS)
    return True


def _look_fits(axis, key, picks):
    """Sense of an option given the axes picked before it (LOOK_ORDER): physical light (v1 rules, unchanged), camera
    geometry and the pipeline safety rules (v2). A missing earlier pick never rules anything out."""
    g = picks.get
    light, time = g("light_style"), g("time_of_day")
    if light is not None:
        if axis == "time_of_day":
            return key in ("late_afternoon", "golden_hour") if light == "golden_low" else key != "golden_hour"
        if axis == "season" and time == "late_afternoon":       # 5 pm: low autumn/winter sun, still high in summer
            return key in ("autumn", "winter") if light == "golden_low" else key != "winter"   # 5 pm winter = dusk
        if axis == "sun_direction":
            return key != "facing_sun" if light == "soft_even" else key != "away_from_sun"
    display, height, angle, dist = g("display"), g("camera_height"), g("camera_angle"), g("distance")
    if axis == "camera_height" and display:
        if key == "counter":                     # level with a furniture top: only when the art is on / over one
            return display in ("lean_on_furniture", "hung_over_furniture")
    if axis == "camera_angle" and key == "through_doorway" and height:
        return height in ("eye", "low")
    if axis == "distance":
        if angle == "through_doorway" and key == "close":
            return False
        if height == "low" and display in _HUNG and key == "close":    # steep upward tilt would keystone the opening
            return False
    if axis == "lens" and dist:
        if key == "lens_wide" and dist == "close":                     # wide lens up close bends the frame
            return False
        if key == "lens_short_tele" and dist == "wide":                # an 85 mm whole-room view does not fit a room
            return False
    if axis == "foreground":
        if angle == "through_doorway":                                 # the door frame is the foreground
            return key == "clear_foreground"
        if key == "throw_or_rug" and display == "floor_lean":          # would run into the frame's bottom edge
            return False
    if axis == "depth_of_field":
        if key == "soft_foreground" and g("foreground") in (None, "clear_foreground"):
            return g("foreground") is None
        if key == "soft_background" and (angle in ("straight_on", "through_doorway") or dist == "close"):
            return False                                               # the art wall IS the background there
    if axis == "composition":
        if angle == "through_doorway":
            return key == "centred"
        if key == "offset_furniture" and display:
            return display in ("hung_over_furniture", "lean_on_furniture")
        if key == "beside_window" and g("sun_direction"):              # a window in the art wall cannot face the sun
            return g("sun_direction") in ("side_window", "away_from_sun")  # and also light that wall
    if axis == "wall_treatment" and key == "panelled" and display:     # WAINSCOT_RULE: centred inside one panel
        return display in _HUNG
    if axis == "frame_finish" and g("wall_palette"):                   # the frame must stand out from the wall
        wall = g("wall_palette")
        if wall == "blush":
            return key in ("black_frame", "walnut_frame")
        if key == "oak_frame":
            return not _pale_warm(picks)
        if key == "white_frame":
            return wall not in ("warm_white", "ivory_cream", "soft_grey")
        if key in ("black_frame", "walnut_frame"):
            return wall != "deep_moody"
        if key == "gold_frame":
            return wall not in ("ivory_cream", "greige")
    return True


def _tables(version):
    if version == 1:
        return LOOK_V1_ORDER, LOOK_V1_AXES, LOOK_V1_NUDGE_DECOR, LOOK_V1_NUDGE_ROOM
    if version == 2:
        return LOOK_ORDER, LOOK_AXES, LOOK_NUDGE_DECOR, LOOK_NUDGE_ROOM
    raise ValueError(f"unknown look version {version!r}; one of 1, 2")


def look_weights(room, decor, axis, picks=None, version=LOOK_VERSION):
    """{option: probability} for one axis: base weight x room/decor (and, v2, persona) nudges (clamped, never zero),
    minus gated options (v2), then only the options that fit the earlier picks. Tests compare sampled frequencies
    with this."""
    _, axes, nd, nr = _tables(version)
    picks = picks or {}
    lo, hi = LOOK_NUDGE_RANGE
    pn = PERSONA_NUDGE.get(picks.get("photographer"), {}) if version >= 2 else {}
    w = {}
    for key, (base, _) in axes[axis].items():
        if version >= 2 and not _look_gate(room, decor, axis, key):
            continue
        m = nr.get(room, {}).get(key, 1.0) * pn.get(key, 1.0)
        for d, nudge in nd.items():
            if key in nudge and decor_matches(d, decor):
                m *= nudge[key]
        w[key] = base * min(hi, max(lo, m))
    fit = {k: v for k, v in w.items() if _look_fits(axis, k, picks)} or w
    tot = sum(fit.values())
    return {k: v / tot for k, v in fit.items()}


def pick_look(room, decor, seed=None, override=None, version=None):
    """One weighted random look. seed=None -> a fresh random seed (normal builds are genuinely random); the seed is
    returned so the same look can be replayed. override = {axis: option} (e.g. a recorded look) forces those axes;
    a recorded look's "version" is honoured, so a v1 look saved before 2026-11-19 replays with the v1 tables.
    version: force a table version for a seed-only replay (default LOOK_VERSION)."""
    import random
    version = version or (override or {}).get("version") or LOOK_VERSION
    order, axes, _, _ = _tables(version)
    if seed is None:
        seed = random.SystemRandom().randrange(2 ** 32)
    rng = random.Random(seed)
    forced = {a: v for a, v in (override or {}).items() if a in axes}
    for a, v in forced.items():
        if v not in axes[a]:
            raise ValueError(f"unknown {a} option {v!r}; one of {sorted(axes[a])}")
    picks = {}
    for axis in order:
        w = look_weights(room, decor, axis, picks, version)
        r = rng.random()                        # always drawn, so a forced axis never shifts the other draws
        if axis in forced:
            picks[axis] = forced[axis]
            continue
        acc, keys = 0.0, list(w)
        picks[axis] = keys[-1]
        for k in keys:
            acc += w[k]
            if r < acc:
                picks[axis] = k
                break
    out = {"version": version, "seed": seed, **picks}
    if forced:
        out["overridden"] = sorted(forced)
    return out


def look_text(look, room=None):
    """The prompt sentences for a look (positive wording) + LOOK_GUARD (v2 also LOOK_GUARD_FRAME). LOOK_AT_BUILD =
    preview wording. room fills the display's {anchor} / {surface} (default sideboard)."""
    if look == LOOK_AT_BUILD:
        return ("Scene look: picked at random when Build this is clicked (light, photographer and stylist, time of "
                "day, season, sun direction, display, camera angle, height, distance, lens, focus, foreground, "
                "composition, wall colour and finish, floor, furniture, frame finish) and saved in template.json. "
                + LOOK_GUARD + LOOK_GUARD_FRAME)
    v = look.get("version", 1)
    axes = LOOK_V1_AXES if v == 1 else LOOK_AXES
    sunny = look["light_style"] in _SUNNY
    season = axes["season"][look["season"]][1][0 if sunny else 1]
    time = axes["time_of_day"][look["time_of_day"]][1]
    head = (f"Time and season: {time}, {season}. {axes['sun_direction'][look['sun_direction']][1]} "
            f"{axes['light_style'][look['light_style']][1]} {axes['photographer'][look['photographer']][1]} ")
    if v == 1:
        return head + LOOK_GUARD
    fill = {"anchor": ROOM_ANCHOR.get(room, "sideboard"), "surface": ROOM_SURFACE.get(room, "sideboard")}
    scene = " ".join(axes[a][look[a]][1].format(**fill) for a in
                     ("display", "camera_angle", "camera_height", "distance", "lens", "foreground", "depth_of_field",
                      "composition", "wall_palette", "wall_treatment", "floor", "furniture_finish"))
    return head + scene + " " + LOOK_GUARD + LOOK_GUARD_FRAME


def _swap(text, old, new):
    assert old in text, old          # the v1 wording moved: fail loudly rather than send a half-edited prompt
    return text.replace(old, new)


def _present_text_v2(kind, look):
    """The presentation sentences for a v2 look (or a LOOK_AT_BUILD preview, look={}): no "hangs" when the art
    leans, no fixed camera angle, the picked frame finish, a darker floater wood on pale warm walls."""
    t = _PRESENT_TEXT[kind]
    lean = look.get("display") in _LEAN
    finish = LOOK_AXES["frame_finish"].get(look.get("frame_finish"), (0, None))[1]
    if kind == "frame":
        t = _swap(t, "The artwork hangs in a thin frame (natural oak, walnut or brass most of the time; black only "
                     "occasionally, when it clearly suits the room).",
                  f"The artwork is framed in {finish}." if finish else
                  "The artwork is framed in a thin frame (natural oak, walnut or brass most of the time; black only "
                  "occasionally, when it clearly suits the room).")
    elif kind == "mat":
        t = _swap(t, "The artwork hangs in a refined thin frame with",
                  f"The artwork is framed in {finish} with" if finish else
                  "The artwork is framed in a refined thin frame with")
    else:
        t = _swap(t, " Camera: a slight 3/4 view so the depth shows.", "")
        if kind == "canvas":
            stand = ("The piece stands off the wall by the canvas depth and casts a natural shadow on the wall that "
                     "follows the room's light direction.")
            if lean:
                t = _swap(t, stand, "The piece leans against the wall and casts a natural shadow on the wall and the "
                                    "surface below that follows the room's light direction.")
            if _pale_warm(look):
                t += (" The floater frame's natural wood is a mid-tone honey oak, clearly darker than the wall, so "
                      "its outer edge stands out crisply against the wall.")
        else:   # canvas_bare
            if lean:
                t = _swap(t, "hung directly on the wall with NO frame", "with NO frame")
                t = _swap(t, "The canvas stands off the wall by its depth and casts a natural soft shadow on the wall "
                             "that follows", "The canvas leans against the wall and casts a natural soft shadow on the "
                                             "wall and the surface below that follows")
        angle = look.get("camera_angle")
        t += (" Its depth reads in the shadow it casts." if angle in ("straight_on", "through_doorway") else
              " The side edge facing the camera shows the canvas depth." if angle else
              " The canvas depth shows in its side edge or its shadow.")
    return t


def scene_prompt(room, decor, ratio, presentation=None, look=None):
    """Tony's recipe (memory feedback_room_template_recipe_ai_frame_in_scene, 2026-11-08, updated 2026-11-16): one
    piece of wall art whose printed area is flat onion-skin orange, shown as a frame, a matted frame or a stretched
    canvas in a floater frame. The art is never in the prompt (it is composited later). Standing rules: no people, no
    random lamps, props only when lived-in. look: a pick_look() dict (callers that generate pick it first so they can
    save it in template.json), LOOK_AT_BUILD for a preview, or None for a fresh random look. A v1 look (saved before
    2026-11-19) gives the exact v1 prompt, including its fixed "Camera angle: 3/4 corner"."""
    kind = presentation or presentation_for(room, decor, ratio)
    look = look or pick_look(room, decor)
    if look != LOOK_AT_BUILD and look.get("version", 1) == 1:
        return (f"Photorealistic {decor_words(decor)} {ROOM_WORDS.get(room, room.lower())} interior "
                f"featuring one vertical piece of wall art ({RATIO_PROMPT[ratio]}). Realistic "
                "textures, subtle decor, moody and lived-in detail that feels authentic. Lighting is natural daylight "
                "from a window, falling in one consistent direction. " + look_text(look)
                + "Camera angle: 3/4 corner. Composition should be vertical, focused on "
                "the artwork and wall area. Only one piece of wall art, no other frames. " + _PRINT_AREA
                + _PRESENT_TEXT[kind] + " No people, no faces, no hands, no pets. No lamps unless the room clearly "
                "needs one; only props a real person would leave there. " + WAINSCOT_RULE)
    present = _present_text_v2(kind, {} if look == LOOK_AT_BUILD else look)
    return (f"Photorealistic {decor_words(decor)} {ROOM_WORDS.get(room, room.lower())} interior "
            f"featuring one vertical piece of wall art ({RATIO_PROMPT[ratio]}). Realistic textures, subtle decor and "
            "authentic lived-in detail. Lighting is natural daylight from a window, falling in one consistent "
            "direction. " + look_text(look, room)
            + "The picture is a vertical (portrait) photograph with the artwork as its clear focal point. Only one "
            "piece of wall art, no other picture frames, posters or mirrors. " + _PRINT_AREA
            + present + " No people, no faces, no hands, no pets. No lamps unless the room clearly needs one; only "
            "props a real person would leave there. " + WAINSCOT_RULE)


# Tony 2026-11-15 (Mockup_Docs/Mockup_Style_Guide.md "Wainscoting and wall molding rule"): optional, elegant /
# traditional rooms only, and it never touches the art.
WAINSCOT_RULE = ("Wall paneling or wainscoting only if the room style calls for it (elegant or traditional rooms); if "
                 "used, either keep it below waist height and fully below the frame, or make the panels larger than "
                 "the frame with the frame hanging centred inside one panel, with clear wall space on every side; the "
                 "frame never touches or overlaps any molding, rail or panel edge.")
