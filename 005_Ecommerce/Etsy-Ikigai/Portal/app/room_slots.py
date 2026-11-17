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
Everything is deterministic: the same inputs always give the same plan.
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


_PRINT_AREA = ("The artwork's printed area is a single flat, plain, matte, empty " + INSERT_COLOUR + " surface, completely "
               "uniform: no artwork, no text, no logo, no gradient, no glare, no reflection and no heavy shadow on it. ")
_PRESENT_TEXT = {
    "frame": ("The artwork hangs in a thin frame (natural oak, walnut or brass most of the time; black only occasionally, when it clearly suits the room). "
              "The orange printed surface fills the whole frame opening right up to the inside edge of the frame on all "
              "four sides. NEGATIVE: no mat, no matte border, no passe-partout, no white border, no margin, no inner "
              "rectangle, no bevel line."),
    "mat": ("The artwork hangs in a refined thin frame with a WIDE off-white mat border (passe-partout) of exactly even "
            "width on all four sides, about 10% of the frame height, with a crisp bevelled window cut. The flat orange "
            "printed surface sits inside the mat window; the mat is clearly lighter than the orange so the window edge "
            "is sharp."),
    "canvas": ("The artwork is a thick stretched gallery canvas, 1.5 to 2 inches (4-5 cm) deep, with the orange face and "
               "clearly visible orange side edges, mounted inside a thin NATURAL LIGHT WOOD floater frame (floating "
               "frame), a warm natural wood colour, never black or dark. The canvas sits inset inside the frame with a "
               "narrow even visible gap of about 0.5 cm between the canvas edge and the frame's inner lip; the gap shows "
               "only a soft light shadow (never black), so the pale wood frame, the thin gap and the orange canvas edge "
               "are three clearly separate bands. The piece stands off the wall by the canvas depth and casts only a "
               "soft, light, diffuse shadow on the wall. Camera: a slight 3/4 view so the depth shows.")}


def scene_prompt(room, decor, ratio, presentation=None):
    """Tony's recipe (memory feedback_room_template_recipe_ai_frame_in_scene, 2026-11-08, updated 2026-11-16): one
    piece of wall art whose printed area is flat onion-skin orange, shown as a frame, a matted frame or a stretched
    canvas in a floater frame. The art is never in the prompt (it is composited later). Standing rules: no people, no
    random lamps, props only when lived-in."""
    kind = presentation or presentation_for(room, decor, ratio)
    return (f"Photorealistic {decor_words(decor)} {ROOM_WORDS.get(room, room.lower())} interior "
            f"featuring one vertical piece of wall art ({RATIO_PROMPT[ratio]}). Realistic "
            "textures, subtle decor, moody and lived-in detail that feels authentic. Lighting is soft warm daylight, "
            "naturally diffused, never harsh. Camera angle: 3/4 corner. Composition should be vertical, focused on "
            "the artwork and wall area. Only one piece of wall art, no other frames. " + _PRINT_AREA
            + _PRESENT_TEXT[kind] + " No people, no faces, no hands, no pets. No lamps unless the room clearly "
            "needs one; only props a real person would leave there, nothing staged. " + WAINSCOT_RULE)


# Tony 2026-11-15 (Mockup_Docs/Mockup_Style_Guide.md "Wainscoting and wall molding rule"): optional, elegant /
# traditional rooms only, and it never touches the art.
WAINSCOT_RULE = ("Wall paneling or wainscoting only if the room style calls for it (elegant or traditional rooms); if "
                 "used, either keep it below waist height and fully below the frame, or make the panels larger than "
                 "the frame with the frame hanging centred inside one panel, with clear wall space on every side; the "
                 "frame never touches or overlaps any molding, rail or panel edge.")
