---
title: "Slot-Set Planner: realism addendum (references, lived-in brief, repeat limits, text scan, grades)"
type: plan
domain: ecommerce
tags: [ikigai-digital-studios, portal, production, mockups, room-templates, slot-planner]
created: 2026-11-20
status: built 2026-11-21 on Tony's 'Yes, build all' (steps 1-11; one commit by the parent session; paid scenes only on Tony's click)
extends: Pipeline_Docs/Slot_Set_Planner_Plan.md
---

# Slot-Set Planner: realism addendum (2026-11-20)

Plan only. Nothing was built, edited, committed or deleted while writing it; no folder was created. Paths are relative
to `005_Ecommerce/Etsy-Ikigai/Portal/` unless they start with `Creative_Inspiration/`, `Room_Templates/` or `Designs/`.
Everything here is free except a room scene that Tony generates with his own click (18 kie.ai credits each).

## 0. Why, and what the evidence shows

Tony graded Book Club Cat slots 16-19 **C, C+, C+, C-**: cookie-cutter, staged like a big-box catalog, the same warm
golden window light, the same props (dried stems, stoneware, plants, fake books, little wood objects, rattan), bare
windows, nothing lived in. He wants "someone bought the print, hung it in their real home and took a nice photo".

What the files show (checked 2026-11-20, read-only):

| Slot | Grade | How it was made | What repeats |
|---|---|---|---|
| 16 Kids | C | **planner brief** (rev 1): A5, tight, dresser_top, standing, walnut, camera left / counter / 85 mm, dappled light from the right | wood toy block, stoneware cup, dried grass stems, sage dresser |
| 17 Bedroom | C+ (best) | **old random v2 look** (no brief; slot record has no `brief_rev`): persona "Parisian apartment, elegant and slightly undone", crisp winter sun, 3/4 corner from the right, low camera | cane headboard, cane bench, stoneware vase; **garbled book-spine text** and a **second framed picture** in the hallway |
| 18 Office | C+ | **old random v2 look** (no brief) | rattan armchair, cane chair, two plants, stoneware mug, knit throw |
| 19 Nursery | C- | **planner brief** (rev 6, chat-edited): 5x7, tight, toy_shelf, standing, walnut, camera left / counter / 85 mm, golden low light from the right | wood stacking toy, stoneware bud vase, dried stem, woven basket |

Conclusions that drive this addendum:
1. **The planner's own taste paragraph produced the catalog look.** 16 and 19 are the same photograph: tight, standing
   on a surface, walnut frame, camera left at counter height, 85 mm, light from the right, stoneware + dried stem + wood
   toy. `check_set` passed them because their setting and room differ; it has no notion of "same composition" or
   "same prop family" (section 4 adds both).
2. **The prompt drowns the scene.** 732 words for slot 16 (measured with `assemble()`, identical to the saved prompt),
   of which the planner's scene is 120; the fixed blocks are 365 (frame) to 507 (canvas). Section 5 trims them.
3. **Text slips through.** Slot 17 has garbled book spines and a second frame; nothing scanned for it. Section 6.
4. **The reference board is itself mostly staged.** Of the 26 cleaned references (section 1.6) only about 7 look lived
   in; none is at night, none is gloomy overcast. References will fix camera, lens and composition; the lived-in
   content must come from the scene text (section 3), and the board needs real-home photos (open question 1).

Decided here without asking (logic, or Tony already said it): one commit total at build time; portrait only; 4:3
photo; orange marker default, blue on warm walls (`slot_planner.marker_for_wall`); no rationale text on cards; graded
slots stay library templates; paid generation only on Tony's click.

---

## 1. Reference prep (blanked references + manifest)

### 1.1 Where the files go (existing folders only)
`Creative_Inspiration/Mock-Up_Inspiration/` has only `Archive/` inside (originals and low-res; never used). No new
folder: the prepared files sit **next to their source** in the same folder:

- `NNNN_<Same_Name>_Blank.png`: the cleaned reference with the artwork filled flat with the marker colour.
- `Reference_Manifest.json`: one manifest for the folder (tags, measured facts, fill polygon, flags).

Sources = files matching `^\d{4}_[A-Za-z0-9_\-]+\.png$` that do not end in `_Blank.png`, in this folder only (never
`Archive/`). A settings key `reference_dir` (default the folder above) lets Tony move them later without code changes.
`Cleanup_Log.md` gets a short section saying what `_Blank` files are.

### 1.2 New module `app/references.py` (existing `app/` folder)
```
PREP_VERSION = 1
MANIFEST = "Reference_Manifest.json"
sources(folder) -> [Path]
prepare(settings, ids=None, force=False, log=print) -> report      # headless, idempotent
blank_for(entry, marker, flip=False, out_dir) -> Path               # recolour / mirror on demand into a temp dir
usable(settings) -> [entry]                                         # usable entries, manifest order
contact_sheet(entries, out_png, cell=300) -> Path                   # labelled sheet of _Blank files for the planner
python -m app.references --prepare [--ids 0024,0031] [--force] [--sheet <png>]
```

`prepare` per source:
1. `sha1` of the source bytes. Skip when the manifest entry has the same `sha1`, the same `prep_version`, its
   `_Blank.png` exists, and `blank_method != "tony"` is not about to be overwritten (entries Tony blanked by hand are
   never touched). This makes repeated runs free and byte-stable.
2. **Find the art** with the existing SAM pipeline in a new reference mode (`sam_frames.py detect --reference`, run
   through the SAM venv exactly like `scene_templates.sam_detect`):
   - Gemini rough box with a reference prompt (one call, `gemini-3.5-flash-lite`, the existing `gemini_box` code with
     a second prompt string): "the printed ARTWORK inside the frame and inside any mat (not the moulding, not the
     mat)"; the same JSON reply also returns `frames` (count of framed pictures), `mirrors`, `screens` and the art's
     `shape` (portrait / landscape / square / round / irregular).
   - `insert_candidates` unchanged, but `segment_insert` in reference mode skips the "edge band looks like its core"
     paper filter (a real artwork has content, so its band always differs) and orders candidates by closeness to the
     Gemini box area instead of smallest first.
   - `fit_quad` + `verify_quad` unchanged; then `opening_quad(..., paper_fallback=True)` so the fill reaches the
     frame's hard inner edge (or the mat window). Framed canvas without lip: `--canvas` path (`canvas_face_quad`).
3. **Fill**: polygon = `offset_quad(q_open, +1.0)` (one pixel under the frame lip so no art sliver survives), flat
   `MARKER_RGB[marker]`, no texture, no shading. The marker comes from the reference's own wall: `wall_lab` ring
   (`scene_templates.wall_lab`, 12-28% outside the quad) -> hex -> `slot_planner.marker_for_wall(hex)`. This also
   removes the captions / watermarks / placeholder text printed on the art (0026, 0028, 0032, 0037, 0038, 0042, and
   also 0023, 0024, 0029, which carry poster lettering). 0008 from the handoff list is in `Archive/` (low-res) and is
   not used.
4. **Measure** (deterministic, from the quad): `art_h_frac`, `aspect` (`rooms.true_aspect`), `camera_side` (left vs
   right quad edge length, > 3% difference, same rule as `stp.shot_meta`), `light_from` (`stp.light_side`), `wall_lab`,
   `marker`, image `size`.
5. **Free checks** (all must pass for `usable: true`):
   - leftover ring: in a 3 px band just outside the fill polygon, share of pixels more than dE 25 from the band's
     median colour < 5% (an art sliver is high-contrast against frame wood or mat);
   - portrait only: true aspect <= 0.90 (square / landscape / round art -> `usable: false`, our builder only makes
     portrait rectangles);
   - Gemini `frames == 1`, `mirrors == 0`, `screens == 0` (a second artwork or a mirror in the reference invites one
     in the output);
   - display is upright (a frame lying flat, like 0028, is not a display we build);
   - text scan (section 6) on the `_Blank.png`: any finding -> `room_text: [boxes]`, `usable: false` until cleaned
     (0033's "STONE DESIGN" spine is found today; see 6.6).
6. **Tags** (categorical): the seed table in 1.6 is written once as `tags` with `tags_by: "seed_2026-11-20"`.
   References added later get one `claude -p` vision call (the planner's `run_cli` route, Tony's plan, no credits),
   enum-only JSON, batches of 8 images, `tags_by: "vision"`. Measured fields always win over tags. Tony can edit any
   tag in the manifest (`tags_by: "tony"` is never overwritten).

### 1.3 When SAM fails or the art is not a rectangle
In order: (a) retry with `--canvas`; (b) **mask mode**: fill the refined SAM alpha (`refine_alpha`) dilated by 2 px
when the mask lies inside the Gemini box and covers >= 60% of it, store its simplified contour (<= 64 points) as the
fill polygon, `blank_method: "mask"`; (c) otherwise `usable: false, why: "artwork not found"`. The CLI report lists
every unusable reference with its reason; Tony can blank one by hand in any editor, save it as `_Blank.png` and set
`blank_method: "tony"` in the manifest. Round or irregular art is unusable by the shape rule anyway.

### 1.4 Manifest entry (shape)
```json
{"version": 1, "prep_version": 1, "refs": {
  "0024": {"source": "0024_Kitchen_Corner_Sink_Subway_Tile_Thin_Black_Frame_Evening_Light.png",
           "blank": "0024_Kitchen_Corner_Sink_Subway_Tile_Thin_Black_Frame_Evening_Light_Blank.png",
           "sha1": "...", "size": [1353, 1219], "usable": true, "why": [],
           "blank_method": "sam_quad | sam_canvas | mask | tony", "fill_polygon": [[x, y], ...],
           "marker": "orange", "wall_lab": [L, a, b], "aspect": 0.74, "art_h_frac": 0.36, "camera_side": "left",
           "light_from": "left", "frames": 1, "mirrors": 0, "room_text": [],
           "tags": {"display_group": "hung", "shot": "medium", "setting": "kitchen counter", "room": "Kitchen & dining",
                    "camera_height": "counter", "lens": "lens_normal", "light_type": "dusk_lamp_mix",
                    "light_quality": "soft", "window_covering": "bare", "wall_texture": "tile",
                    "house": "older family kitchen", "lived_in": "busy", "editorial": false},
           "tags_by": "seed_2026-11-20", "uses": [], "grades": []}}}
```
`uses` (listing, slot, template) and `grades` are appended at generation and grading time (sections 2.6, 7).

### 1.5 Recolour and mirror on demand
`blank_for(entry, marker, flip)` re-fills `fill_polygon` on the cleaned source with the other marker when the brief's
marker differs from the reference's, and mirrors the image when the brief asks for `reference_flip`; output goes to
the run's temp dir only (nothing extra is stored).

### 1.6 Seed tags from viewing all 26 (2026-11-20)
Display group: hung / surface (standing or leaning on furniture) / shelf / floor. Lived-in: tidy / lived_in / busy.

| id | display | shot | setting | light | lived-in | flags | usable |
|---|---|---|---|---|---|---|---|
| 0001 | hung | medium | credenza, living | golden_low, from left | tidy (styled) | dried wheat, brass figure: the old recipe | yes |
| 0023 | hung | medium | dining banquette | hard_diagonal_sun, from right | lived_in | poster lettering (blanked) | yes |
| 0024 | hung | medium | kitchen counter | dusk_lamp_mix | busy | lettering (blanked) | yes |
| 0025 | floor | medium | beside bed | morning_soft_sun, from right | lived_in | old wood door | yes |
| 0026 | floor | medium | bare wall | hard_diagonal_sun, from left | tidy | watermarks on art (blanked) | yes |
| 0027 | hung | medium | bathroom tile, over toilet | north_light_even | lived_in | | yes |
| 0028 | flat lay | - | rug | - | - | frame lying flat | no |
| 0029 | hung | tight | plain wall | overcast_flat | tidy | heavy lettering (blanked) | yes (tight only) |
| 0030 | surface | medium | coffee bar dresser | north_light_even | busy | | yes |
| 0031 | shelf | tight | oak niche | blind_stripes | tidy | | yes |
| 0032 | floor | medium | beside French door | morning_soft_sun | tidy | watermarks on art (blanked) | yes |
| 0033 | shelf | tight | ledge | north_light_even | tidy | square frame, readable book spine | no |
| 0034 | hung | medium | sideboard | north_light_even | tidy | catalog | yes |
| 0035 | hung | medium | sideboard, mat | north_light_even | tidy | dried thistle, catalog | yes |
| 0036 | hung | wide | hallway, oversized canvas | overcast_flat | tidy | large / canvas only | yes |
| 0037 | hung | medium | lounge chair | north_light_even | tidy | caption on art (blanked) | yes |
| 0038 | hung | medium | desk nook | north_light_even, from left | tidy | "ROOTED" on art (blanked) | yes |
| 0039 | hung | wide | panelled living, curtains | overcast_flat | lived_in | AI render, luxe | yes |
| 0040 | hung | medium | bathroom vanity | - | - | arched mirror | no |
| 0041 | hung | wide | industrial loft | overcast_flat | tidy | luxe | yes |
| 0042 | hung | medium | charcoal studio desk | north_light_even, from right | lived_in | "Your artwork Here" (blanked) | yes |
| 0043 | hung | wide | Parisian hallway, doorway | north_light_even | tidy | second frame on the left wall | no (until cleaned) |
| 0044 | hung | wide | double-height living | overcast_flat | tidy | luxe | yes |
| 0045 | hung | medium | panelled office | north_light_even, from left | tidy | | yes |
| 0046 | hung | wide | dark salon, mantel | dusk_lamp_mix (dim) | tidy | moody | yes |
| 0047 | hung | wide | taupe living, mantel | overcast_flat | tidy | | yes |

22 usable (more than the 12 room slots). Thin spots: floor leans 3, surface/shelf 3, night 0, hard sun 2, busy 2.

---

## 2. One distinct reference per slot, sent to the image model

### 2.1 Choice (planner proposes, code validates)
- The planner sees the reference list (id, compact tags, measured shot / side / light, past grades) plus **one contact
  sheet image** of the usable `_Blank.png` files labelled by id (`references.contact_sheet`, 1568 px long side, added
  as image 3 after the art and the existing-slots sheet).
- Each brief returns `reference` (id) and `reference_flip` (bool).
- `slot_planner.validate_references(briefs, fixed, refs)` (deterministic):
  - the id exists and is `usable`;
  - **distinct in the set**: no two open slots share a reference, and none reuses a reference recorded in a fixed
    slot's template brief; reuse only when usable references < open slots (then least-used first);
  - display group of the reference == display group of the brief (hung / surface / shelf / floor);
  - reference shot within one step of the brief's shot (tight <-> tight/medium, wide <-> medium/wide);
  - an invalid or duplicate pick is **reassigned by code**: best score = display match 3 + shot match 2 + lived-in
    match 1 + unused across listings 1 + mean past grade (0-1), ties by id; logged in the round's failures.
- The reference supplies the look, so code **derives** (like ratio and marker today): `camera_side` (flip swaps
  left/right), `camera_height`, `lens` from the reference; the model's own values for these fields are overwritten.
  Diversity of camera across the set therefore comes from choosing different references, which `check_set` still
  measures.
- `ref_use` = `["camera", "lens", "composition", "character"]`, plus `"light"` only when the brief's `light_type`
  equals the reference's tag. Stored on the brief.

### 2.2 The reference clause (exact wording, assembled by code, placed right after the opening line)
With light (`"light" in ref_use`):
> Image 1 is a photograph of a different room, given only as a photography reference. Take from it the camera
> position and height, the lens and framing, how much of the room shows, the direction and quality of the light, and
> its natural, unstaged feel. Build a completely new room as described below: do not copy its furniture, objects,
> wall colour, floor, windows or layout. The flat colour block in its frame is a placeholder, not art; nothing in
> Image 1 is text to reproduce.

Without light: the same, with "the direction and quality of the light, and" replaced by "and" and one added sentence:
"Use the light described below, not the light in Image 1."

Never in the clause: the occupant line, the art, any interface or text. Word count: 72 / 78.

### 2.3 How the image is attached (verified in code and on kie.ai docs, 2026-11-20)
- `app/kie_edit.py generate(engine, out, prompt, aspect_ratio, res, ref_imgs=())` already uploads `ref_imgs` and sends
  them as `image_input` for Nano Banana (`input_urls` for GPT). `nano-banana-pro` accepts up to 8 `image_input` URLs,
  jpeg/png/webp up to 30 MB; `aspect_ratio` (incl. "4:3") is part of the same schema with or without images
  (docs.kie.ai/market/google/pro-image-to-image). Uploads are free.
- `scene_templates.generate_scene(prompt, out_png, settings=None, generator=None, ref_imgs=())`: when `ref_imgs` is
  empty it calls `gen(eng, out, prompt, aspect, res)` exactly as today (every test stub keeps working); otherwise
  `gen(..., ref_imgs=ref_imgs)`. The test stub `fake_generator` gets an optional `ref_imgs=()` argument.
- `REF_ENGINES = {"nbpro", "nb21", "nb2"}` in `scene_templates`. Any other `room_scene_engine` (GPT image-to-image
  would EDIT the reference instead of using it as a guide) -> text-only prompt (`assemble(b, ref=False)`), card note
  "reference not sent (engine)". Also text-only when the `_Blank.png` is missing or `planner_references` is false.
- **Cost**: kie.ai prices Nano Banana Pro per output, "18 credits for 1K/2K, 24 for 4K" (kie.ai/nano-banana-pro);
  neither page mentions input images changing it. Expected extra: **0 credits**. `generate()` already returns the
  measured balance difference; the first reference scene's `credits` value confirms it, and the card cost line uses
  the measured number from then on.
- **Refusal** ("flagged as sensitive", seen on 0028 in the cleanup): when kie refuses the job and the balance did not
  move, `run_slot` retries **once text-only** inside the same click (so one click still costs at most 18 credits),
  marks the reference `kie_refused: <date>` in the manifest so it is not picked again, and notes it on the card. If
  the balance moved, no retry.

### 2.4 Scene text vs reference (keeping them consistent)
- The scene text describes the room, its furniture, its life and imperfections, and the setting; the reference gives
  camera, lens, composition and character. The system prompt says so (section 3.2) and lint enforces it:
  - scene text may not name camera, lens, focal length, angle, shot size or light direction (`CAMERA_WORDS`, 3.4);
  - the reference's display group must match the brief's display (2.1);
  - the scene's light words must not contradict `light_type` (e.g. "night" words with a daylight type) (3.4).
- The Show prompt panel shows `Reference 0024 (mirrored)` and a 96 px thumbnail of the blank above the prompt text.

### 2.5 Where it plugs into `run_slot` (`production.py:679-700`)
For a `new` brief with `reference`: `ref = references.blank_for(entry, brief["marker"], brief["reference_flip"],
td)`; `prompt = brief["prompt"]` when sent, else `slot_planner.assemble(brief, ref=False)`; `stp.generate_scene(
prompt, scene, settings, generator, ref_imgs=[ref])`. Nothing changes for briefs without `reference` (old briefs) or
the random-look fallback.

### 2.6 Bookkeeping
`template.json` `brief` keeps `reference`, `reference_flip`, `ref_use`, `reference_sent`; the manifest entry gets a
`uses` row. Fixed slots made from a reference therefore block its reuse in that listing.

---

## 3. Planner taste rewrite (lived-in brief)

### 3.1 What goes away
The "Photography taste" paragraph (`slot_planner.py:854-859`) and its recipe: walnut and oak, plaster or limewash,
stoneware, dried stems, a small brass piece, one plant at the edge, warm low sun. The "calm, clean ... few objects,
nothing staged or cluttered" sentence (`:831-833`) is replaced too (it pushed toward catalog vignettes).

### 3.2 New `SYSTEM_PROMPT` (draft, replaces the constant for new plans; the old text stays as `SYSTEM_PROMPT_V1`)
```
You plan the room photographs for one Etsy listing of a printable wall-art design. You are three people at once: an
interior designer who knows how real people furnish the homes they actually live in, a photographer, and a curator
who decides how a buyer first meets this artwork. You see the artwork, the photographs that already exist for this
listing, a sheet of reference photographs labelled with their ids, and the open slots you must plan.

The story of every photograph: someone bought this print, had it printed and framed, put it up in their own home and
took a nice photo of it. The home is real and lived in. It is not a showroom, a catalogue or a styled vignette.

Every artwork is a PORTRAIT (vertical) piece. Every photograph is a 4:3 landscape listing photo.

For each open slot, first decide who lives there and write it as "occupant": one short sentence for your own
planning. It is never shown and never sent to the image model, so the scene text never mentions a person. Then write
the scene from that life:
- Everyday things in use, left where people leave them: a jacket over a chair back, a half-finished mug, a few plain
  envelopes face down, a phone charger cable, shoes by a door, a child's crayon drawing with no letters, folded
  laundry, keys in a bowl, a lamp left on. Pick what this occupant would have; never all of them.
- Real imperfections: uneven bedding, a scuffed skirting board, a rug slightly askew, worn paint on a door frame, a
  radiator under the window, light switches, power outlets, a plain round thermostat, door frames and hinges.
- Real windows: venetian or roller blinds, linen curtains, sheers or shutters, and a real view (a street, the
  neighbour's brick wall, trees, a courtyard, a city). A bare window at most once in the whole listing.
- Furniture of different ages that was not bought as a set: a hand-me-down dresser beside a flat-pack shelf, a
  vintage chair at a modern desk, a painted chest with worn edges.
- Different houses and regions: a 1920s brick terrace, a 1970s condo, a rented student flat, a craftsman bungalow, a
  converted loft, an old farmhouse kitchen, a Tokyo apartment, a Berlin Altbau, a Texas ranch house. The region shows
  in windows, radiators, floors, outlets and light.
- How lived-in each slot is ("tidy", "lived_in", "busy") varies across the set: a nursery may be tidy, a study or a
  kitchen clearly used. "busy" only for medium and wide shots. Everything stays clear of the frame: clutter sits below
  its bottom edge or toward the picture edges.

The light varies across the set and is never a default warm golden glow: hard diagonal sun with crisp shadows, a grey
overcast day, a rainy afternoon, blue dusk with a warm lamp on, evening lit only by lamps, sun striped by venetian
blinds, steady north light. Warm golden low sun at most once in the whole listing.

The photograph looks taken by the owner with a good phone or a simple camera: natural auto exposure, true colours, a
little grain in the room, framed by hand (slightly off-centre is fine, verticals level), not retouched. At most two
slots in the listing look editorial.

Avoid the catalogue recipe. Each of these at most once in the whole listing, counting the photographs that already
exist: dried stems or pampas, rattan or cane, boucle, a wooden toy block or stacking toy, candles, a chunky knit
throw. Plants at most twice; stoneware or ceramic vases at most twice; stacks of books at most twice. Do not default
to walnut, oak, limewash and stoneware.

References: pick ONE reference photograph for each open slot, a different one for every slot, never one already used
by an existing photograph. The reference gives the camera position, lens, framing and the photograph's character
(and its light when your light type matches it); your scene gives the room and the life in it. Choose a reference
whose display (hung on a wall, on a surface, on a shelf, leaning on the floor) and framing fit the slot's print size.
"reference_flip": true uses it mirrored. Never describe the reference's furniture or objects: build a new room.

What a slot is: the room name is where it is filed. The setting is the surface or wall inside that room (a
nightstand, a desk, a mantel, an entry console or hallway wall, which are filed under Living room, the wall over a
bed, a bathroom wall). Setting and shot are separate choices.

Scale drives framing. Pick a real print size from the chart for each slot. Small prints are shown TIGHT: the piece
stands or leans on a surface and fills about half to two thirds of the picture height, with one to three everyday
objects at true scale beside it. Medium prints are medium shots with the furniture below. Large prints are wider
shots on a wall or leaning on the floor. Across the listing aim for roughly a third small, a third medium, a third
large, all five ratios, several sizes; the existing photographs count, so fill what they lack.

The art ties in with the room by contrast or harmony, never by matching its colours. Do not take wall or furniture
colours from the artwork. One or two slots may use a loud wall, a bold furniture piece or a painted frame (yellow,
red, deep green, bronze) when it flatters this piece. Warm walls are allowed: the pipeline picks the colour of the
blank print area itself.

Hard rules, never broken:
- No people, faces, hands or pets, not even mentioned in passing. One piece of art only: no other frames, posters,
  mirrors, or screens showing pictures.
- Nothing readable: books show plain spines or face away, envelopes face down, phones face down, laptops closed, clocks
  without numerals; no calendars, magazines, packaging, signs, labels or logos.
- Every scene shows visible shadows. The art face is flat, upright, in sharp focus and evenly lit.
- The whole frame is inside the picture with clear space around it; nothing overlaps the frame.
- The frame contrasts with the wall in tone (frame lightness: black 15, walnut 35, bronze 40, gold 60, oak 65,
  silver 72, white 95; a painted frame by its colour; wall lightness at least 15 away). Canvas floaters are natural
  wood, never black. Canvas only for medium and large prints.
- Wainscoting only below waist height (say "below waist height"), or panelling with the art "centred inside one
  larger panel" (say so).
- Do not describe the artwork. The scene text never names the camera, lens, angle, shot size or light direction:
  those come from the fields and the reference.
- The scene text is 60 to 160 words of plain description of the room, its things and its life. Never explain why.
- Prefer a listed library template when one fits the set (it is free); otherwise plan a new scene.

Output ONLY one JSON object, no prose, no reasons, no explanations.
```

### 3.3 Schema and enums (brief `pv: 2`)
New / changed fields in `SCHEMA` and `KEEP` (all others unchanged):

| Field | Values | Notes |
|---|---|---|
| `occupant` | <= 25 words | internal: never in the prompt, never on the card; shown in the chat snapshot for the pointed slot only; not BANNED-linted (it names a person by design) |
| `lived_in` | `tidy`, `lived_in`, `busy` | `busy` needs >= 4 props and medium/wide |
| `light_type` | `hard_diagonal_sun`, `morning_soft_sun`, `golden_low`, `overcast_flat`, `rainy_day`, `north_light_even`, `blind_stripes`, `dusk_lamp_mix`, `night_lamps` | replaces `light_style` in pv2; code derives `light_style` for the old descriptor (`hard_diagonal_sun`->crisp_direct, `blind_stripes`->dappled, `golden_low`->golden_low, `morning_soft_sun`->soft_direct, the three soft daylight types -> soft_even, lamp types -> None) and `shadow` (hard for sun/blinds, soft otherwise) |
| `window` | `{"covering": venetian_blind / roller_blind / roman_blind / sheer_curtain / linen_curtains / heavy_drapes / shutters / bare / no_window_in_view, "view": street / brick_wall / trees / courtyard / city / garden / sky / night / none}` | `night_lamps` -> view `night` or `no_window_in_view` |
| `photo_style` | `phone_snapshot`, `enthusiast_camera`, `editorial` | editorial <= 2 per set |
| `reference`, `reference_flip` | manifest id, bool | 2.1 |
| `frame_finish` | adds `bronze_frame` (L 40), `silver_frame` (L 72), `painted_frame` | `painted_frame` needs `frame_colour {name, hex}`; contrast uses its L*; lint: dE2000 to the marker >= 25 and not in the marker's hue family (no orange frame on the orange marker, no blue frame on the blue one); canvas stays `natural_wood_floater` |
| `house` | adds `victorian_terrace`, `craftsman_bungalow`, `condo_1970s`, `student_rental`, `berlin_altbau`, `tokyo_apartment`, `texas_ranch`, `old_farmhouse`, `mediterranean_flat`, `prewar_apartment` | `HOUSE_REGION` map (uk, us, europe, asia, other) |
| `props` | free text (<= 3 tight, <= 6 medium, <= 8 wide) | families counted by code (section 4) |

Phrases (positive wording, in `slot_planner`, new constants, nothing in `room_slots` edited):
- `LIGHT_TYPE_TEXT`: e.g. `hard_diagonal_sun` "Light: hard direct sun through the window cuts a crisp diagonal band of
  light across the wall and floor; sharp-edged shadows."; `blind_stripes` "Light: low sun through half-open venetian
  blinds lays parallel stripes of light and shadow across the wall beside the frame and the floor."; `overcast_flat`
  "Light: a grey overcast day; flat, cool, even window light, soft open shadows under the furniture, slightly muted
  colours."; `rainy_day` "... dim cool daylight, a few raindrops on the window glass, a lamp on in the room.";
  `dusk_lamp_mix` "Light: dusk; deep blue light in the window and a warm lamp switched on in the room, soft shadows
  from the lamp."; `night_lamps` "Light: evening after dark; the room is lit by its own lamps in warm pools with soft
  shadows; the artwork is lit evenly by a nearby lamp."; `north_light_even`, `morning_soft_sun`; `golden_low` reuses
  the LOOK_AXES phrase.
- `WINDOW_TEXT`: "The window has {covering phrase}; outside, {view phrase}." (`no_window_in_view`: nothing).
- `PHOTO_STYLE_TEXT`: `phone_snapshot` "Photo: a careful phone photo by the owner: natural auto exposure, true colours,
  a little grain in the room, framed by hand slightly off-centre with level verticals, not retouched; the print area
  stays clean and flat." `enthusiast_camera`: same idea, a simple mirrorless camera. `editorial`: "a calm interiors
  photograph, natural and unretouched."
- Scale cue: the tight-shot sentence no longer always says "an ordinary coffee cup" (it seeded a cup in every tight
  scene). `SCALE_CUES` rotates by slot over a light switch plate (11.4 cm), a power outlet, a paperback, a mug, a table
  lamp base, a door handle; a cue already in the props is preferred.

### 3.4 Lint additions (pv2 only; pv1 lint unchanged)
- `occupant` present, <= 25 words; `lived_in`, `light_type`, `window`, `photo_style` valid; `busy` + tight -> fail.
- `CAMERA_WORDS = r"\b(camera|lens|\d{2,3}\s?mm|close-?up|wide shot|tight shot|medium shot|angle|shot from|from the (left|right))\b"`
  in `scene` -> fail.
- `TEXT_CARRIERS = r"\b(calendar|newspaper|magazines?|cereal box|packaging|sticky notes?|whiteboard|chalkboard|price tags?|receipts?|posters?)\b"` -> fail.
- Qualified objects (same sentence must carry a qualifier, else fail):
  books -> `plain|spines? (turned )?away|face down|unmarked|cloth-bound|linen-covered`;
  envelopes / letters / mail -> `face down|plain`; phone -> `face down|screen off`; laptop -> `closed`;
  clock -> `no numerals|plain face`; drawing -> `no (letters|words)`; bottles / jars -> `plain|unlabell?ed`.
- Light words vs `light_type`: `night|after dark|lamplight` only with lamp types; `sun|sunlit|sunbeam` not with
  `overcast_flat` / `rainy_day` / `night_lamps`.
- Reference fit (2.1) and painted-frame rules (3.3).
- Unchanged: BANNED words, wall/marker, frame contrast, panelling, 60-160 words, scale vs shot.

### 3.5 `assemble()` and byte-identical old briefs
- `assemble(b, ref=True)` dispatches: a brief without `pv` (every saved brief and template today) goes to
  `_assemble_v1(b)`, which is today's function body moved unchanged. Golden test: `sha1(assemble(brief))` equals the
  saved `prompt` of slot 16 (`AI_Kids_Kids_20261120_122955`) and slot 19 (`AI_Nursery_Kids_20261120_134709`)
  `template.json` (verified equal today for slot 16).
- `pv: 2` -> `_assemble_v2(b, ref)` in this order: opening (14 words) -> reference clause (2.2, when sent) -> scene ->
  framing/scale (compact, with the rotating scale cue) -> camera (one merged sentence from the derived side, height,
  lens, depth of field) -> light type -> window -> photo style -> wall -> print area + presentation -> guards ->
  closing (section 5 decides full or compact text for the last three).
- `normalise` keeps pv1 behaviour for pv1 input; pv2 adds derivation of `light_style`, `shadow`, camera fields from
  the reference, `frame_colour` L*, and drops unknown keys as today.
- `descriptor()` gains `light_type`, `warm_sun`, `window_covering`, `lived_in`, `photo_style`, `reference`, `region`,
  `frame_finish`, `prop_families` (set) and `comp_sig`. `SIM_W` and `similarity()` are NOT changed (old check tests
  keep their numbers); the new facts feed the new rules in section 4.
- `chat_lines` / `edit_brief`: `EDIT_FIELDS` adds `lived_in`, `light_type`, `window`, `photo_style`, `reference`,
  `reference_flip`, `occupant`, `frame_colour`; edits of a pv1 brief stay pv1.
- `card_brief` adds `reference` and `ref_thumb_url`; never `occupant`.

---

## 4. Set-wide repeat limits in `check_set` (deterministic)

### 4.1 Prop families (`PROP_FAMILIES`, regex over `scene` + `props`, presence per slot)
| Family | Regex (case-insensitive, word bounded) | Max per listing |
|---|---|---|
| `dried_stems` | `dried (stems?\|grass(es)?\|flowers?\|wheat\|thistle\|lavender)\|pampas\|bunny tails?\|wheat stems?` | 1 |
| `rattan_cane` | `rattan\|cane\|wicker\|woven seat` | 1 |
| `boucle` | `bouc?l[eé]\|teddy fabric\|sherpa` | 1 |
| `wood_toy` | `wood(en)? (blocks?\|toys?\|cubes?\|beads?)\|stacking (toy\|rings?)` | 1 |
| `candles` | `candles?\|candlesticks?\|tealights?` | 1 |
| `knit_throw` | `(chunky )?knit(ted)? (throw\|blanket)` | 1 |
| `plants` | `plants?\|fern\|monstera\|fiddle[- ]leaf\|pothos\|ficus\|olive tree\|succulents?\|cactus\|palm` | 2 |
| `stoneware` | `stoneware\|ceramic (vase\|cup\|jug\|bowl)\|bud vase\|clay (vase\|pot)\|pottery` | 2 |
| `book_stack` | `stack(ed\|s)? of books\|books stacked\|coffee[- ]table books` | 2 |
| `brass_object` | `(brass\|bronze) (figure\|object\|candlestick\|tray\|bowl\|sculpture)` | 2 |
| `woven_basket` | `woven baskets?\|seagrass\|jute basket` | 1 |
| `eucalyptus_branch` | `eucalyptus\|(olive\|blossom\|cherry) branch(es)?` | 1 |

### 4.2 Other repeat rules
| Rule | Fails when | Blame |
|---|---|---|
| warm sun | `golden_low` > 1, or warm-sun family (`golden_low`, `morning_soft_sun`, old `soft_direct`/`golden_low` looks) > 2 | later open slots in listing order beyond the limit |
| light recipe | same (`light_type` or old `light_style`, `light_from`, `shadow`) > 2 | same |
| composition signature | two slots agree on >= 5 of (display, shot, camera_side, camera_height, lens, light_from, frame_finish) | the later open slot (16 vs 19 matched 7 of 7) |
| camera recipe | same (camera_side, camera_height, lens) > 2 | later open slots |
| reference | same reference twice (fixed included) | the later open slot |
| windows | `bare` > 1; one covering > 2 | later open slots |
| lived-in mix (pv2 open slots >= 3) | no `tidy`, or fewer than half `lived_in`/`busy`, or `busy` > 2 | open slots of the over-full or missing bucket |
| photo style | `editorial` > 2 | later open slots |
| frame finish | one finish > 40% of known, or `walnut_frame` > 3 | later open slots |
| region | fewer than 3 regions when n >= 6 | all open slots, 0.4 |
| night | `night_lamps` > 1 (until one night scene passes the builder; setting `planner_max_night: 1`) | later open slots |

Counting: the listing = fixed + open. A limit that the **fixed slots alone already exceed** is never a failure; it
only forbids open slots from adding more ("rattan already appears in slots 17 and 18: no rattan in open slots").
Blame points 1.0 (prop family, reference, composition signature), 0.7 (light, camera), 0.5 (others). Failure text is
plain and actionable, e.g. "dried stems appear in fixed slot 13 and open slot 19; at most 1 in the listing: remove
them from slot 19". These failures go into the rewrite round exactly like today's (`plan_set`, top 4 by blame).

### 4.3 Props of fixed (approved) slots
- Slot made from a brief: the regexes run on its saved `scene` + `props` (template.json `brief`).
- Otherwise: the existing one-call fixed-slot vision describe (`describe_fixed`) gets new keys: `prop_families`
  (choose from `PROP_FAMILIES` names), `light_type`, `window_covering`, `lived_in`, `warm_sun` (bool). The cache entry
  gets `vision_version: 2`; v1 entries are re-described once (one `claude -p` call for all uncached images, free).
  Unknown stays None and never counts as a repeat.

---

## 5. Shorter fixed boilerplate (without weakening the rules)

### 5.1 Measured today (slot 16 brief, frame)
| Block | Words |
|---|---|
| opening | 21 |
| scene (the planner's) | 120 |
| shot/scale | 67 |
| display + camera side + height + lens + focus | 91 |
| light + direction + shadow + "every scene shows shadows" | 54 |
| wall | 6 |
| print area (`rs._PRINT_AREA`) | 119 |
| presentation (frame 86, mat 98, canvas 228, canvas_bare 126) | 86 |
| `LOOK_GUARD` + `PLAN_GUARD_FRAME` | 111 |
| `CLOSING` | 49 |
| **total** | **732** (mat 744, canvas 864, canvas_bare 762) |

### 5.2 Keep / trim / merge (pv2 "compact" texts, new constants; `rs._PRINT_AREA`, `_PRESENT_TEXT`, `LOOK_GUARD`,
`PLAN_GUARD_FRAME`, `CLOSING` stay untouched for pv1 and for "full")
- Opening: "Photorealistic interior photograph, 4:3 landscape format, of one portrait piece of wall art in a home." (14)
- Shot/scale (about 35): size in inches + cm, outer size, height share, one rotating scale cue.
- Camera (about 30, one sentence): side + degrees, height, lens, focus, "verticals level".
- `PRINT_AREA_C` (about 50): "The print area is one flat, blank {colour words} surface, dead matte like unglazed card,
  one even tone from edge to edge, no glare. Only the front face of the print is {name}; the frame, its inner edge,
  any gap and the wall keep their own colours with no {name} glow."
- `PRESENT_C`: frame (about 33) "It is framed in {finish}. The {name} fills the opening right up to the frame's inner
  edge on all four sides: no mat, no white border, no inner line. Any glass is invisible."; mat (about 40) wide
  off-white mat of even width (about 10% of the frame height), crisp bevelled window, the {name} clearly darker than
  the mat; canvas (about 75) 4-5 cm stretched canvas in a thin natural light-wood floater, never black, only the front
  face {name}, side edges plain white (grey where shaded) ending the face in one crisp straight line, a narrow even
  0.5 cm gap in soft neutral shadow so frame, gap, white side and face read as separate bands, plus the existing
  depth/lean sentence; canvas_bare (about 45).
- `GUARD_C` (about 65, merges both guards): "Sun patches and blind or leaf shadows fall on the wall and surfaces around
  the frame, never across the print area, which stays one evenly lit tone. The whole frame is inside the picture with
  clear space on all four sides and nothing overlapping it; its face is flat, upright and in sharp focus, it stands
  out in tone from what is behind it, and its outlines stay crisp."
- `CLOSING_C` (about 38): "One artwork only: no other frames, posters, mirrors or screens showing pictures. No
  people, hands or pets. Nothing readable anywhere: no labels, logos, signs, lettering, numerals or book titles; books
  show plain spines or face away. Every scene shows visible shadows."
- Dropped on purpose: "No lamps unless the setting clearly needs one" (lamps are now wanted: dusk / night types).

Targets (checked by a test): fixed blocks (print area + presentation + guards + closing) 365 -> <= 190 words for
frame/mat, 507 -> <= 270 for canvas; whole pv2 compact prompt <= 560 words with the reference clause (<= 490 without)
for a 160-word scene.

### 5.3 Same rules, proven by a test
`RULES` = list of (id, regex) that every pv2 prompt must contain, for every presentation x marker, in both styles:
marker colour words + its RGB triple; `matte`; `even`; `front face`; `own colou?rs?`; frame: `inner edge`, `no mat`;
mat: `even width`, `bevel`; canvas: `white`, `gap`, `floater`, `never black`; canvas_bare: `no frame`, `white`;
`clear space on all four sides`; `overlap`; `sharp`; `upright`; `flat`; `stands out`; `No people`; `pets`;
`book titles`; `no other frames`; `mirrors`; `shadows`; `4:3`; `portrait`. `test_compact_keeps_every_rule` asserts
each regex in both styles and the word targets above.

### 5.4 Staged rollout (easy revert)
Setting `planner_compact: ["frame", "mat"]` (default). Presentations listed use the compact blocks; canvas and
canvas_bare (the fragile SAM / wrap-strip path) keep the full blocks until two compact canvas scenes have built
cleanly, then Tony (or the agent on his word) adds them. Revert = remove an entry, no code change. Every template
records `prompt_style` in its `brief`; `attempts` already log `no_insert` / `gate_fail`, so a worse failure rate for
compact is visible per style on the card history.

---

## 6. Output scan (stray text, UI, watermarks, logos, extra frames, marker leak)

### 6.1 What exists and what was measured (2026-11-20)
- `tesseract` is installed (`/opt/homebrew/bin/tesseract`); `pytesseract`, `easyocr` and PyObjC `Vision` are not.
  `swiftc` is available, so macOS Vision OCR works through a small compiled Swift tool.
- Test on slot 17 (garbled book spines): Vision on the whole 2400 px picture finds **nothing** (letters too small);
  Vision on a **6 x 4 grid of overlapping tiles, each upscaled 3x** finds the spine text (strings like "TRRNOSIC RIGA",
  confidence 0.3-1.0, at x 0.45-0.6, y 0.62-0.66 of the picture) in **about 3.5 s per picture**, and finds nothing on
  slots 16 and 18 (which have no text). Tesseract on the same picture returns mostly noise glyphs from textures.
- On the references Vision reads 0033's "STONE DESIGN" spine (confidence 1.0).
- Gemini vision is already called per build (`sam_frames.gemini_box`, `gemini-3.5-flash-lite`), so one more call per
  scene is the cheapest way to catch UI buttons, logos and extra frames (well under a cent; no kie.ai credits).

### 6.2 New module `app/scene_scan.py` + `app/text_scan.swift`
- `text_scan.swift`: `VNRecognizeTextRequest`, accurate, no language correction, `minimumTextHeight = 0`; takes a list
  of tile PNGs, prints JSON (conf, box, string). Compiled once with `swiftc -O` to `~/.cache/ikigai-sam/bin/
  ikigai_text_scan` (existing folder outside the workspace; settings `text_scan_bin`). If the binary is missing and
  cannot be compiled: tesseract fallback (`--psm 11` TSV, conf >= 70, >= 4 alphanumerics), noted as weaker.
- `ocr_findings(png)`: 6 x 4 tiles, 20% overlap, 3x Lanczos; boxes mapped back; duplicates across tiles merged.
- `gemini_findings(png, ask=None)`: one call, JSON list of `{type: text | ui_button | watermark | logo | signage |
  extra_frame | mirror | person | pet, box_2d, confidence}`, temperature 0; `ask` injectable for tests.
- `marker_leak(scene_rgb, art_quad, marker)`: after `build_psd`, share of pixels within dE76 < 12 of the marker colour
  outside the art quad grown by 1.5% of the width.
- `scan(png, settings)` -> `{"pass", "severity": "none|soft|hard", "findings": [...], "overlay": path}`; settings
  `scene_scan: "ocr+gemini" | "ocr" | "off"` (default `ocr+gemini`).

### 6.3 Thresholds
- OCR finding: confidence >= 0.3, >= 3 alphanumeric characters, box height >= 0.35% of the picture height.
- Edge band = outer 10% of width / height; corners = 15% x 15% boxes.
- **hard**: an OCR finding in a corner, or in the edge band with width >= 4% of the picture (captions, watermarks,
  buttons); any Gemini `ui_button`, `watermark`, `logo`, `extra_frame`, `mirror`, `person`, `pet` with confidence
  >= 0.6; signage / text with confidence >= 0.6 and width >= 6%.
- **soft**: any other OCR finding (book spines, small labels on objects); Gemini `text` 0.6+ that is small; marker
  leak > 0.25% of the picture.

### 6.4 What happens (never spends by itself)
In `run_slot`, right after `generate_scene` and before `build_psd`:
- **hard** -> no build. Scene kept as `03-Etsy Images/Archive/Scene_Stray_Text_NN_<stamp>.png` plus
  `..._Scan.png` (boxes drawn); `TemplateError("stray text / a button / a second frame at the top-left corner (scene
  kept as ...); Regenerate for a new scene")`; brief `attempts` gets `result: "stray_text"`.
- **soft** -> build continues (free, so the 18 credits are not wasted); `template.json` gets `text_scan: {pass: false,
  findings}`; the render is placed **flagged** (Archive, like a guard failure) with the plain reason ("garbled text on
  book spines, centre-right"); the card offers Regenerate as a button only. Tony may still approve it.
- `library_candidates` and `production.library_picks` skip templates with `text_scan.pass == false`.
- No automatic repair. (A free local text removal is possible later; see open question 2.)

### 6.5 Free checks before any paid scene
- Unit tests with injected OCR / Gemini results (thresholds, tiling maths, severity, flow): no binary needed.
- Stand-in images drawn with Pillow: "SALE 20%" in the top-left corner -> hard; "ABCD" on a small book-spine
  rectangle mid-picture -> soft; a rounded "Visit site" pill bottom-left -> hard; a clean synthetic room -> pass.
- Real files (marked `vision`, skipped off macOS): slot 17 -> soft (spines) and Gemini `extra_frame`; slots 16, 18,
  19 -> no OCR finding; references 0033 -> text found.

### 6.6 Applied to references
`references.prepare` runs the same scan on every `_Blank.png` (1.2 step 5). A reference with room text is unusable
until cleaned (0033 today; it is also square, so it stays out).

---

## 7. Grade learning (small)

- **Scale**: `GRADES = ("A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D", "F")`, scores 4.3 ... 0.
- **Storage** (whitelisted keys only, no credentials, no prompts copied):
  - listing record: `production.grades[<image file>] = {"grade", "note"?, "at", "slot", "template", "brief_rev",
    "reference"}` (outside `production.slots`, which `run_slot` replaces);
  - template: `template.json` `grades: [{"idea_id", "design", "slot", "grade", "note"?, "at"}]` via a small writer
    `stp.add_grade(psd, entry)` that keeps only those keys (strings <= 40 chars, note <= 200);
  - reference manifest: `grades` per reference id.
- **UI**: a compact `<select class="pgrade">` (blank, A+ ... F) on every card that has an image, next to Approve /
  Deny; change -> `POST /api/production/{idea_id}/grade {name, grade}` (null clears). Approval flow unchanged. The
  panel's 3 s repaint keeps the chosen value from the panel data.
- **Chat**: action `slot_grade {idea_id, slot, grade, note?}`, only when Tony states a grade himself (system prompt
  line in `assistant.py` beside `slot_prompt_edit`).
- **Backfill** (part of the build, Tony's own grades from the handoff): 16 C, 17 C+, 18 C+, 19 C-, with the note
  "catalog look: golden window light, dried stems, stoneware, rattan, bare windows" (17: "closest: depth, character").
- **Planner use** `graded_examples(settings, good=3, bad=3)`: from all template.json files with grades; mean grade;
  good = mean >= B+ (best first, newest on ties), bad = mean <= C (worst first). Each example: grade, note, scene
  text (or, for a v2-look template, its persona / light / camera / display / wall keys), setting, shot, light type,
  lived-in, props, reference. Capped at about 1,400 words; added to `planner_prompt` as "Tony's past grades: learn what
  he rewards and what he marks down; never copy a scene". Until good examples exist, only the bad ones show.
- **Library**: templates whose mean grade is below B- are skipped by `library_candidates` / `library_picks` (so the
  four C scenes stay in the library, as Tony wants, but are not auto-picked for other designs; Tony can still pick
  them with "+").
- Per reference, the mean grade shows in the planner's reference list and counts in the reassignment score (2.1).

---

## 8. Tests and ordered build steps

### 8.1 Tests (pytest, `tests/`; generator, `ask`, Gemini and OCR injected as today)
1. **Golden locks first**: existing `test_room_look_v2.py` V1/V2 hashes and `test_marker.py` stay green; new: `assemble`
   of the saved slot 16 and slot 19 briefs equals their `template.json` prompts (sha1); a pv1 brief fixture hash.
2. `test_references.py`: synthetic room with a patterned "artwork" + Pillow text "ART EXPLORE" in a frame; fake
   `sam_detect` (conftest pattern) -> blank covers the quad, ring leftover < 5%, text gone (scan stub), manifest entry
   written; second run rewrites nothing (mtimes and sha1 unchanged); changed source -> re-prepared; `tony` entry never
   touched; square / two-frame / mirror stand-ins -> `usable: false` with reasons; recolour + flip via `blank_for`.
   Real SAM on 0024 (frame), 0035 (mat), 0036 (canvas) marked `sam`, skipped without the venv.
3. `test_scene_scan.py`: 6.5.
4. `test_slot_planner.py` additions: pv2 normalise/lint (each new rule passes and fails once: CAMERA_WORDS, text
   carriers, book without qualifier, busy + tight, painted orange frame on orange marker, night words in daylight,
   reference display mismatch); derived camera fields from the reference; `occupant` absent from `assemble` output;
   `test_compact_keeps_every_rule` + word targets (5.2-5.3); `assemble(ref=False)` has no "Image 1".
5. `check_set` additions: a set reproducing 16 + 19 fails the composition signature with blame on the later slot;
   dried stems twice fails, once passes; fixed slots already over a limit never fail, open slots adding more do;
   reference reuse fails; lived-in mix; warm-sun limit; old check tests unchanged.
6. Planner loop with canned replies: invalid / duplicate reference -> reassigned by code and listed; few-shot block
   present and capped; vision describe v2 cache upgrade happens once.
7. Flow (`test_slot_planner_flow.py`): a pv2 brief with a reference -> the stub generator receives `ref_imgs` with one
   PNG (mirrored when flipped, recoloured when markers differ) and the with-reference prompt; engine not in
   `REF_ENGINES` -> text-only prompt, no `ref_imgs`; refusal with unchanged balance -> exactly one text-only retry;
   hard scan -> no build, scene in Archive, attempt `stray_text`; soft scan -> template built, `text_scan.pass` false,
   render flagged, excluded from library picks; pv1 brief and no-plan fallback send exactly today's prompts.
8. Grades: route + record + template.json writer whitelist (unknown keys dropped); select survives a repaint; chat
   action refused without a grade word; library skip below B-.
9. Browser smoke (Portal on 8800): grade picker, Show prompt with reference id + thumbnail, no occupant anywhere on
   the card.

### 8.2 Ordered build steps (Tony's rule: ONE commit at the end; steps are for order and review only)
1. Golden locks (8.1.1). No behaviour change.
2. `app/references.py` + `sam_frames.py --reference` + Gemini reference prompt + manifest + CLI; tests 8.1.2.
   Run `python -m app.references --prepare` on the 26 (free: local SAM, about 26 Gemini flash-lite box calls); write
   the 1.6 seed tags; open the contact sheet for a look (not blocking).
3. `app/scene_scan.py` + `app/text_scan.swift` (+ compile) + tests 8.1.3; run on the references and on slots 16-19
   (free) and record the results in the build report.
4. `slot_planner` pv2: enums, normalise, lint, `_assemble_v1` move, `_assemble_v2`, compact texts, `RULES`; tests
   8.1.1 + 8.1.4.
5. `check_set` repeat limits + descriptor keys + vision describe v2; tests 8.1.5.
6. `SYSTEM_PROMPT` v2, `SCHEMA`, `planner_prompt` (reference list + sheet + graded examples), reference validation
   and reassignment, `dry_run --replan 16,17,18,19` (treats those decided slots as open, read-only DB as today);
   tests 8.1.6.
7. Generation: `generate_scene(ref_imgs)`, `REF_ENGINES`, `run_slot` wiring (reference, scan, marker leak, refusal
   retry, `template.json` fields, library exclusions); tests 8.1.7.
8. Grades: storage, route, UI select, chat action, backfill of 16-19; tests 8.1.8.
9. UI: Show prompt reference line + thumbnail; smoke 8.1.9; restart the Portal.
10. **Free dry run**: `python -m app.slot_planner --idea 3 --dry-run --replan 16,17,18,19` (all twelve Book Club Cat
    room slots have images today, so a plain dry run has no open slots). Print the four briefs, chosen references,
    word counts and the check. **Free stand-in scan test** (8.1.3). Show Tony the four prompts + reference thumbnails.
11. Docs: `Slot_Set_Planner_Plan.md` status line pointing here, `Cleanup_Log.md` `_Blank` section, `TOOLBOX.md` entry
    for the text-scan tool, `Directory.md` if it lists Portal modules.
12. One commit (code, tests, docs, `_Blank.png` files, `Reference_Manifest.json`).
13. **Paid generation only on Tony's click**: 18 credits per scene (expected +0 for the reference). Redoing slots
    16-19 = 72 credits.

### 8.3 Credits summary
| Item | kie.ai credits | Other cost |
|---|---|---|
| reference prep (26) | 0 | about 26 Gemini flash-lite calls (< $0.02); `claude -p` only for future untagged refs (Tony's plan) |
| planner, dry run, scans of existing images | 0 | `claude -p` (Tony's plan); Gemini scan per image (well under a cent) |
| one new scene with a reference | 18 (expected +0 for the reference; measured on the first run) | upload free; one Gemini scan |
| refusal + text-only retry | 18 in total for the click (retry only when the refusal cost nothing) | |

---

## 9. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Model copies the reference too literally (same room, same sofa), or treats it as an image to edit | Clause says "a different room ... do not copy its furniture, objects, wall colour, floor, windows or layout"; the scene describes a different room with its own furniture; references are distinct per slot; per-reference grades push bad ones down. Lever if it still copies: setting `scene_ref_soften` (pass a downscaled, slightly blurred reference, long side 512 px) so it carries composition and light but not details; tested on one scene before using it widely. |
| The blank colour shows up as an orange (or blue) patch on a wall or object | Reference blank uses the brief's own marker (recoloured on demand); the clause calls it a placeholder; `marker_leak` check after build flags > 0.25% of the picture; guard + art-area gate already catch a coloured bar beside the art. |
| Lens / scale confusion from small, square or tall references (600-1300 px, aspect 0.6-1.2) | Camera fields derived from the reference keep text and image in agreement; shot band must match within one step; tall references (0034-0038, 0042) fit tight/medium only (seed tags); measured-shot drift flag stays on the card. |
| Over-cluttered scenes break SAM, the art-area gate or the guard (objects near the frame) | `busy` only medium/wide; clutter "below the frame's bottom edge or toward the picture edges"; tight shots keep 1-3 props; `PLAN_GUARD_FRAME` / `GUARD_C` keep clear space on all four sides; attempts log `no_insert` / `gate_fail`; "Plan this slot one step wider" exists. |
| "A little grain" lifts the blank insert's texture above `INSERT_TEXTURE_MAX = 0.03`, so `key_light` drops the Light Shadow (no shadow over the art) | Photo-style sentence keeps "the print area stays clean and flat"; the first pv2 scenes' `shadows.light.insert_texture` is checked in the build report; if it rises, the grain words are dropped from `PHOTO_STYLE_TEXT` (one constant). |
| New light types meet builder paths never tested: night lamp gradients, rain, overcast with almost no shadow | `planner_max_night: 1` until one night scene passes; the shadow rule ("Every scene shows visible shadows") stays in the closing; blind stripes already work in `light_pattern._slats` (Boho 002116) but the slat fit can misfire on non-blind walls (Wall-Art-Shadows open item), so `blind_stripes` is only planned when the window covering is a venetian blind. |
| kie.ai refuses a reference as "sensitive" | One free-refusal text-only retry; reference marked `kie_refused` and not picked again. |
| Reference board is mostly catalog / AI-luxe, so references pull back toward staging | Lived-in content comes from the scene text; `lived_in` tags steer tidy references to tidy slots; per-reference grades; open question 1 (add real-home photos). |
| Compact boilerplate loosens detection | Rule-equivalence test; compact only for frame/mat first; one-setting revert; per-style failure history. |
| Text scan false positives on textures (wood grain, wallpaper) | Vision rather than tesseract; >= 3 alphanumerics and confidence 0.3; soft findings never block a build; Tony decides on the flagged card. |
| More planner tokens (reference sheet + few-shot) slow the plan | One extra image and <= 1,400 words; background job as today; `planner_timeout_s` 300 unchanged. |

---

## 10. Open questions for Tony (only what cannot be decided by logic)

1. **More real-home references?** Only about 7 of the 22 usable references look lived in; none is at night or on a
   grey day. May I collect 15-20 more (for example buyers' review photos of framed prints on Etsy, and real house-tour
   photos) into `Mock-Up_Inspiration/`, cleaned and renamed the same way? They are used only as private camera/light
   references, never published.
2. **Garbled book spines and other small stray text** (soft findings): flag and let you decide / Regenerate (the plan
   above), or also add a free local clean-up that paints them out (LaMa, the tool the reference cleanup used) before
   the card is shown?
