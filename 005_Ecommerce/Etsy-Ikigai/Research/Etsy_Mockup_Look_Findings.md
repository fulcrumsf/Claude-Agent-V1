---
title: "Etsy Mockup Look Findings"
type: research
domain: ecommerce
tags: [ikigai-digital-studios, mockups, research, room-templates]
built: 2026-11-19
---

# Etsy Mockup Look Findings (2026-11-19)

Data: `Etsy_Mockup_Look_Database.json` (same folder). 156 tagged images: **105 Etsy listings from 37 shops** (Alura official MCP, est sales), **46 of Tony's own templates** (incl. FAILED-checker and Archive), **5 scenes from our generator** (`AI_*` plates). Method and limits are in the JSON header.

Reference, not copies: the shots below show the range of looks buyers respond to. Nothing here is a scene to reproduce.

**Limit (read first):** only the **primary image (slot 1)** of each Etsy listing could be seen. Etsy listing pages returned HTTP 403 to the browser, and the Etsy API call for gallery images was not permitted in this session. Slot 1 is the thumbnail that wins the click, but slots 2-20 (where most room shots live) are not in this data. The 2026-11-07 sweep in `Mockup_Docs/Mockup_Style_Guide.md` section 7 covers full galleries for 29 listings and agrees with the findings below.

Rooms-only tables use real room scenes (`kind` = room, room_minimal, set_layered). Market n=36, Tony n=45, ours n=5.

---

## 1. The cookie-cutter, in one table

| Axis | Market | Tony's own | Our generator |
|---|---|---|---|
| Camera angle | straight-on 53%, slight 39%, 3/4 8% | straight-on 67%, 3/4 13% | **3/4: 100%** |
| Camera height | **low 61%**, eye 31% | eye 96% | eye 100% |
| Distance | **close 50%**, medium 39%, wide 11% | wide 44%, medium 42% | medium 100% |
| How the art is shown | **floor lean 58%**, on furniture 19%, hung 22% | hung 93% | hung 80% |
| Wall | white/cream 64%, greige 17% | white 51%, **colour 33%** (teal, pink, sage, charcoal) | limewash white 80% |
| Floor | light herringbone, light plank | light plank, herringbone | **distressed old planks 4 of 5** |
| Props | 0-2 objects, varied | varied, colour pillows | **book 5 of 5, mug 4 of 5, draped throw 4 of 5** |
| Frame | light oak 64%, walnut 14%, black 11% | oak 49%, **black 27%** | oak floater 60% |

Why the props repeat: the `lifestyle` photographer phrase (weight 60) literally names "a throw casually draped, a book left open, a cup on a side table". Why the walls repeat: "moody and lived-in", japandi/minimal decor words and no wall axis. Why the angle repeats: `Camera angle: 3/4 corner` is hardcoded in `scene_prompt`. Lighting is already varied and is not the problem.

## 2. Top 5 findings

1. **Straight-on wins, 3/4 is rare.** 53% of market room shots and 67% of Tony's are square-on; 3/4 is 8% and 13%. Ours is 100% 3/4.
2. **The market shoots low and close.** 61% of market room shots are from knee/hip height and 50% are close vignettes (art fills about half the image). Tony and our generator are almost always eye height.
3. **Floor leans dominate the market; Tony's taste is hung over furniture.** Market rooms: 58% floor lean + 19% leaning on a sideboard/bench/mantel. Tony: 93% hung above a sofa, bed or credenza. Both are valid looks for different buyers; ours only does one.
4. **Walls: white is the market default, colour is Tony's signature.** Market 64% white/cream, 17% greige, under 10% colour. Tony uses teal, petrol blue, dusty pink, sage, forest green and chocolate in a third of his templates. Ours never leaves warm limewash white.
5. **Floors and wood are where "same photographer" shows most.** Market: light herringbone and light plank, oak or walnut furniture, painted panelling. Ours: the same distressed planks and rustic table every time.

### 1-3 lines each, supporting

| Finding | Data note |
|---|---|
| Slot 1 is often not a room | Of 105 slot-1 images: sets 30%, plain studio wall 28%, room 18%, art + 1-2 objects 15%, flat-lay 3% |
| Parisian panelled walls are a big renderer look | 14 market images + 7 of Tony's use white or cream panelling, mostly with a floor lean |
| Vintage sellers use plain walls + era frames | NorthPrints, Legacy, Ranfurly, RenArt: plain wall, gold/rustic/carved wood frame, soft drop shadow |
| Fast risers use sunlit plain walls and flat-lays | ExaFrameStudio (2026, trend +640%), Legacy: leaf-dapple sun on a cream wall; WellAndWest, PaperMuse: frame lying on rumpled linen, from above |
| Foreground elements are normal | Market 58%, Tony 80% have a sofa arm, chair, plant or door frame at the image edge |
| Lens and depth of field barely vary | Market: normal lens 100%, deep focus 96%. Tony: wide-angle 7%, soft foreground 9%. Telephoto was not observed anywhere |
| Black frames: market 11%, Tony 27% | Our current text says "black only occasionally" |

## 3. Mood spread by style (Etsy, all 105)

| Style | Moods seen (count) |
|---|---|
| Japandi (16) | warm cosy 7, airy bright 5, editorial minimal 3, eclectic layered 1 |
| Coastal (16) | airy bright 5, coastal airy 5, grandmillennial 2, editorial, moody, preppy, playful 1 each |
| Rustic Farmhouse (14) | classic vintage 9, cosy, airy, editorial, festive 1 each |
| Victorian / Vintage (10) | classic vintage 5, moody dark 3, romantic soft 1, airy 1 |
| Kids / Nursery (10) | playful soft 6, airy 2, playful bright 1, preppy traditional 1 |
| Modern (8) | warm cosy 5, airy, classic, editorial moody 1 each |
| Botanical (7) | editorial minimal 4, cosy, airy, moody dark 1 each |
| Mid-Century (6) | warm cosy 3, editorial minimal 3 |
| Boho (6) | editorial minimal 6 (all gallery-wall sets) |
| Scandinavian (4) | airy 2, moody warm 1, cottage cosy 1 |

Tony's own (46): warm cosy 20%, playful trendy 17%, airy 15%, calm neutral 11%, bold colour 9%, editorial 7%, moody 6%. Each buyer type gets its own mood; one default mood serves only one of them.

---

## 4. Proposed new axes (proposal only, no Portal code changed)

Same shape as `LOOK_AXES` in `Portal/app/room_slots.py`: `{option: (base weight, prompt phrase)}`. Weights blend market (rooms) and Tony's templates. Positive wording only. **Replace** the hardcoded `"Camera angle: 3/4 corner."` with the `camera_angle` pick. The canvas presentations' own "slight 3/4 view so the depth shows" stays (it only applies to canvas).

### Pipeline safety (orange insert + SAM + edge check)

| Rule | Why |
|---|---|
| The art face is always in sharp focus, flat and evenly lit (`LOOK_GUARD` stays) | SAM + despill |
| The whole frame sits inside the image with clear wall on all four sides; foreground objects stay at the image edge, **never overlapping the frame** | edge check needs four unbroken edges |
| **No orange, peach, apricot or terracotta walls**; blush walls only with a wide white mat or a black/walnut frame | too close to the onion-skin orange insert |
| Frame colour must contrast with the wall: light oak needs a wall darker or cooler than oak (white, grey, sage, blue, charcoal) or a white mat; on warm beige/greige use black, walnut or white frames | frame/wall edge must be distinct |
| Close vignettes: art fills at most about 60% of the image height | keeps margin for the frame and shadow |
| Low camera: at most a gentle upward tilt, verticals kept straight | keeps the opening a near-rectangle |
| Through-doorway: the door frame stays well clear of the art frame | edge check |
| Unsafe, leave out: frames cut off by the image edge, props overlapping a frame corner, gallery walls (scene rule "one piece of art"), people | SAM / standing rules |

### Ready-to-paste axes

```python
SCENE_VERSION = 1
SCENE_ORDER = ("persona", "display", "camera_angle", "camera_height", "distance", "lens", "depth_of_field",
               "foreground", "composition", "wall_palette", "wall_treatment", "floor", "furniture_finish", "frame_finish")
SCENE_AXES = {
    # market rooms: straight 53 / slight 39 / 3q 8; Tony: 67 / 20 / 13; ours: 3q 100
    "camera_angle": {
        "straight_on": (48, "Camera: square-on to the art wall, the frame level and parallel to the picture edges, verticals straight."),
        "slight_left": (13, "Camera: a slight angle from the left, about 10 degrees off square, the wall receding gently to the right."),
        "slight_right": (13, "Camera: a slight angle from the right, about 10 degrees off square, the wall receding gently to the left."),
        "three_quarter_left": (7, "Camera: a three-quarter view from the left, about 30 degrees off square, so the depth of the room reads clearly."),
        "three_quarter_right": (7, "Camera: a three-quarter view from the right, about 30 degrees off square, so the depth of the room reads clearly."),
        "through_doorway": (12, "Camera: standing in the next room, looking straight through an open doorway at the art wall; the painted door frame edges the picture on one or both sides, well clear of the artwork.")},
    # market rooms: low 61 / eye 31 / counter 6 / seat 3; Tony: eye 96
    "camera_height": {
        "eye": (50, "Camera height: standing eye height, about 160 cm."),
        "low": (32, "Camera height: low, about knee to hip height, looking very slightly up, verticals kept straight."),
        "counter": (10, "Camera height: level with the top of the sideboard or counter, about 90 cm."),
        "seated": (8, "Camera height: seated eye height, about 110 cm, as if photographed from the sofa or bed.")},
    # market rooms: close 50 / medium 39 / wide 11; Tony: wide 44 / medium 42 / close 13
    "distance": {
        "close": (35, "Framing: a close vignette; the artwork fills about half the image height, with the furniture top or floor and one or two objects around it, and clear wall around all four sides of the frame."),
        "medium": (40, "Framing: a medium shot of the art wall and the furniture beneath it, the artwork about a third of the image height."),
        "wide": (25, "Framing: a wide view of the whole room for scale, the artwork about a fifth of the image height, still the clear focal point.")},
    # market 100% normal; Tony: wide 7%; telephoto not observed (kept small, untested)
    "lens": {
        "normal": (75, "Lens: a natural 35-50 mm view with true proportions."),
        "wide": (17, "Lens: a 24-28 mm wide view that shows more of the room, verticals kept straight."),
        "short_tele": (8, "Lens: an 85 mm view from further back, the room gently compressed and the background close behind the art.")},
    # market deep 96%; Tony soft foreground 9%. The art and frame are always sharp.
    "depth_of_field": {
        "deep": (78, "Focus: everything sharp from front to back."),
        "soft_background": (12, "Focus: the artwork and its frame are crisp; the far background softens gently."),
        "soft_foreground": (10, "Focus: the artwork and its frame are crisp; the nearest object at the edge of the picture is softly out of focus.")},
    # market rooms 58% / Tony 80% have something at the image edge; it never touches the frame
    "foreground": {
        "none": (35, "The space in front of the art wall is clear."),
        "furniture_edge": (25, "The arm of a sofa, the back of a chair or the corner of a bed enters one edge of the picture, well clear of the frame."),
        "plant_leaves": (14, "A few leaves of a large houseplant enter one side of the picture, well clear of the frame."),
        "side_table": (14, "A small side table with one or two everyday objects stands at one edge of the picture, well clear of the frame."),
        "throw_or_rug": (12, "The edge of a rug or a folded throw fills the bottom of the picture.")},
    # market rooms: floor 58 / on furniture 19 / hung 22; Tony: hung 93
    "display": {
        "hung_over_furniture": (38, "The artwork hangs on the wall centred above the {anchor}."),
        "floor_lean": (27, "The artwork stands on the floor leaning against the wall, its bottom edge resting on the floor."),
        "lean_on_furniture": (22, "The artwork rests on top of the {surface}, leaning against the wall."),
        "hung_bare_wall": (13, "The artwork hangs alone on a calm stretch of wall with space around it.")},
    "composition": {
        "centred": (45, "Composition: the artwork near the centre of the picture."),
        "thirds_left": (15, "Composition: the artwork on the left third of the picture, the room opening to the right."),
        "thirds_right": (15, "Composition: the artwork on the right third of the picture, the room opening to the left."),
        "beside_window": (15, "Composition: the artwork on the wall beside a window, the window partly in the picture."),
        "offset_furniture": (10, "Composition: the artwork offset above one end of a long piece of furniture.")},
    # market rooms: white/cream 64, greige 17, grey 8, blush 6; Tony adds teal 11, blush 9, sage/forest 4, dark 4
    # never orange / peach / apricot / terracotta (insert colour)
    "wall_palette": {
        "warm_white": (31, "The walls are a soft warm white."),
        "ivory_cream": (13, "The walls are a calm ivory cream."),
        "greige": (13, "The walls are a light warm greige."),
        "soft_grey": (10, "The walls are a soft pale grey."),
        "sage": (9, "The walls are a muted sage green."),
        "dusty_blue_teal": (8, "The walls are a deep muted teal or dusty blue."),
        "deep_moody": (7, "The walls are a deep moody colour (charcoal, chocolate brown or forest green), lit softly."),
        "blush": (5, "The walls are a pale dusty pink."),           # only with mat or dark frame
        "colour_block": (4, "The wall is painted a confident colour block that suits the furniture.")},
    "wall_treatment": {
        "plain_paint": (52, "The wall is smooth painted plaster."),
        "limewash": (12, "The wall has a soft limewash plaster texture."),
        "panelled": (16, "The wall has tall painted Parisian panelling; the artwork sits centred inside one large panel or leans on the floor in front of it."),
        "shiplap": (8, "The wall is painted vertical shiplap boards."),
        "brick": (5, "One wall is painted or exposed brick."),
        "wallpaper": (7, "The wall has a quiet small-pattern wallpaper.")},   # kids / nursery / grandmillennial
    "floor": {
        "light_herringbone": (25, "The floor is light oak herringbone."),
        "light_plank": (25, "The floor is wide light oak planks."),
        "honey_wood": (14, "The floor is honey-toned wood planks."),
        "dark_wood": (9, "The floor is dark walnut-toned wood."),
        "rug": (15, "A large textured rug covers most of the floor."),
        "checker_tile": (6, "The floor is classic checkerboard tile."),
        "stone_concrete": (6, "The floor is pale polished concrete or stone.")},
    "furniture_finish": {
        "light_oak": (24, "The furniture is light oak and ash."),
        "walnut_teak": (30, "The furniture is warm walnut and teak."),
        "painted_lacquer": (12, "The main piece of furniture is painted or lacquered (black, white or a soft colour)."),
        "rattan_cane": (10, "The furniture mixes rattan and cane with wood."),
        "colour_upholstery": (16, "The seating is upholstered in a confident colour (mustard, rust, olive, teal or blush)."),
        "white_cream": (8, "The furniture is white and cream with linen upholstery.")},
    # frame and mat presentations only (canvas keeps its natural-wood floater rule)
    # market rooms: oak 64 / walnut 14 / black 11 / white 8 / gold 3; Tony: oak 49 / black 27 / white 11 / walnut 11
    "frame_finish": {
        "light_oak": (48, "a thin natural light oak frame"),
        "black": (22, "a thin matte black frame"),
        "walnut": (14, "a thin warm walnut frame"),
        "white": (9, "a thin white painted frame"),
        "thin_gold": (7, "a thin antique gold frame")},   # vintage / classical / botanical-antique art only
}
```

### Photographer and stylist personas (replaces the 2-option `photographer` axis)

Weights from the observed persona/mood mix (market slot 1 + Tony). Each persona carries its own props so the throw + mug + book trio stops repeating.

```python
SCENE_AXES["persona"] = {
    "warm_lifestyle_creator": (16, "Photographer: a home-decor creator photographing her own lived-in home in warm afternoon light; natural styling with one or two things she uses every day."),
    "airy_scandi_catalogue": (13, "Photographer: a bright Scandinavian interiors catalogue; airy, pale, uncluttered, soft daylight, one green plant."),
    "midcentury_magazine": (12, "Photographer: a mid-century interiors magazine; warm walnut and teak, rust and mustard accents, a sculptural lamp, balanced framing."),
    "editorial_minimal": (10, "Photographer: a minimalist architecture magazine; calm space, few objects, strong clean lines, generous empty wall."),
    "parisian_apartment": (9, "Photographer: a Parisian apartment story; tall panelled walls, herringbone floor, one vintage chair, light from tall windows."),
    "trendy_girl_apartment": (8, "Photographer: a stylish young renter's bedroom or living room; playful colour, a fluted nightstand, a mushroom lamp, dried stems, soft sun on the wall."),
    "bold_colour_eclectic": (7, "Photographer: an eclectic, colour-confident home; a painted feature wall, patterned cushions, a mix of vintage and modern furniture."),
    "japandi_calm": (7, "Photographer: a quiet Japandi home; low oak furniture, ceramics, a single branch in a vase, soft even daylight."),
    "moody_dark_academia": (5, "Photographer: a moody evening study; deep wall colour, old books, a warm lamp glow in the background, the artwork itself softly and evenly lit."),
    "coastal_grandmillennial": (5, "Photographer: a breezy coastal cottage; white and pale blue, linen, a striped cushion, sea light."),
    "cottage_farmhouse": (5, "Photographer: a country farmhouse kitchen or hallway; painted wood, a woven basket, a jug of garden flowers."),
    "playful_nursery": (3, "Photographer: a soft, gentle nursery or kids' room; a wooden crib or toy shelf, pale colours, a knitted toy."),   # room-gated
}
```

### Nudges (multipliers, clamped 0.5-2.0 like `LOOK_NUDGE_*`)

| Decor / room | Nudge up | Evidence |
|---|---|---|
| Japandi, Minimal | japandi_calm, airy_scandi, low height, floor_lean, close | Japandi rooms: warm cosy + airy, 5 of 16 leans |
| Mid_Century | midcentury_magazine, walnut_teak, colour_upholstery, hung_over_furniture | Tony's 13 mid-century templates |
| Boho, Trendy | trendy_girl, bold_colour, blush/sage walls, rattan | Tony's Girl/Trendy templates |
| Victorian, Vintage | parisian_apartment, moody_dark_academia, thin_gold, panelled, straight_on | vintage sellers: plain wall + gold, classic mood 14 of 24 |
| Coastal | coastal_grandmillennial, airy_scandi, white walls, light plank | coastal: airy 10 of 16 |
| Rustic_Farmhouse | cottage_farmhouse, honey/dark wood, shiplap, walnut frame | farmhouse rows |
| Kids, Nursery | playful_nursery, wallpaper, hung_over_furniture (crib), eye height | kids: playful soft 6 of 10 |
| Office, Creative space | editorial_minimal, lean_on_furniture (desk), close | |
| Bedroom | seated height, hung_over_furniture (bed), soft_foreground (bed corner) | Tony's bedrooms |
| Kitchen & dining | counter height, lean_on_furniture (counter), checker_tile | NoirPixel kitchen lean, KIKIANDNIM (Nov-07 sweep) |
| Mancave, Gamer | moody_dark_academia, dark walls | Tony's Game_Room |

Gate: `playful_nursery` only for Kids/Nursery; `trendy_girl` never for Office; `thin_gold` only when the art reads vintage/classical.

### Physical-sense rules (like `_look_fits`)

- `floor_lean` pairs with `low` or `eye` height, never `counter`; its anchor is the floor, so `{anchor}` is not used.
- `lean_on_furniture` pairs with `counter` or `eye`; `{surface}` comes from the room (sideboard, bench, mantel, desk, picture ledge, kitchen counter, dresser).
- `hung_over_furniture` `{anchor}` comes from the room (sofa, bed headboard, credenza, console, crib, desk).
- `through_doorway` forces `distance` medium or wide and `composition` centred.
- `wide` distance never with `close`-only rooms (bathroom) unless the room is drawn large.
- `blush` wall forces `frame_finish` black or walnut, or the `mat` presentation.
- `light_oak` frame on `greige`/`ivory_cream`/`warm_white`+`limewash` walls switches to the `mat` presentation or to black/walnut (frame/wall contrast).

---

## 5. What this does not cover

- Slots 2-20 of competitor galleries (not accessible this session; see the Nov-07 sweep).
- Set/gallery-wall scenes (30% of market slot 1s): out of scope while the scene rule is one piece of art.
- Plain-wall and flat-lay shots (28% + 3% of market slot 1s): they belong to the fixed template slots, not the room generator.
