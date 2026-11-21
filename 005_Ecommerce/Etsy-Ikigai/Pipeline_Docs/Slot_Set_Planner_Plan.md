---
title: "Slot-Set Planner: implementation plan"
type: plan
domain: ecommerce
tags: [ikigai-digital-studios, portal, production, mockups, room-templates]
created: 2026-11-19
status: built 2026-11-19 (steps 1-10 to G1; G2 not approved, not run); uncommitted until the parent session commits; realism addendum built 2026-11-21 (see Slot_Set_Planner_Realism_Addendum.md: references, lived-in pv2 briefs, repeat limits, output scan, grades)
---

# Slot-Set Planner: implementation plan (2026-11-19)

Plan only. No code was changed while writing it. Every build step below is one small commit; nothing spends kie.ai
credits without Tony's click.

## Decisions 2026-11-19 (Tony) — these override the plan below
1. **Portrait only.** No landscape art or frames anywhere in the planner (enums, ratios, briefs). Orientation becomes a
   pre-production setting later; the code keeps one marked hook (`slot_planner.ORIENTATION`), nothing is built for it.
   The 4:3 generated scene photo IS the Etsy listing photo shape: `room_scene_aspect` stays "4:3", unchanged. Planner
   prompts describe a portrait FRAME inside a 4:3 photograph (the v2 "portrait photograph" wording stays as it is for
   replay; it is not "fixed").
2. **Warm walls ARE allowed.** Replaces "never orange/peach/terracotta/sand walls" (sections 6.3, 7.1, 15.1): the
   frame-insert MARKER colour is chosen per scene, opposite the wall. Default `orange` (today's behaviour,
   byte-identical for every existing scene and template). A planned wall on the warm side (terracotta, adobe, mustard,
   peach, sand, tan, orange-ish, warm brown or red) gets `marker: "blue"` and the prompt asks for a pale blue blank
   insert. Lint: warm wall => blue marker; cool / neutral wall => orange; never a blue marker on a blue / teal wall.
   The builder supports the blue marker (insert detection, despill of a blue cast, art-area gate names a blue or orange
   bar, no hard-coded orange left in the path). Built as its own step before the G0 gate; G0 also runs a warm-wall
   stand-in with a recoloured blue insert (free).
3. **Entry / hallway settings** are filed under Living_Rooms (there is no Entryway folder; no folders are created).
4. **No kie.ai credits, no real generation.** G2 is NOT approved. The build stops after G1 (free dry plan, `claude -p`
   planner calls only, no Fable).

## Build status (2026-11-19, Claude Opus worker)
- Steps 1-9 built in `Portal/app/slot_planner.py` (new), `production.py`, `studio.py`, `prod_chat.py`, `assistant.py`,
  `scene_templates.py` (`shot_meta`, `wall_lab`, `build_psd(marker=)`), `despill.py` (marker hue windows),
  `room_templates.py` (gate names a blue / orange bar), `template_checker.py` (leftover measure per marker),
  `templates/index.html` (facts line, Show prompt, plan line, Re-plan), `config/settings.json` (planner_* keys).
- Marker step (decision 2) built before G0. Orange path byte-identical: `tests/test_marker.py` golden hashes,
  `tests/test_room_look_v2.py` V2 hashes + live templates replay their saved prompts.
- Deviations: (a) the plan's "dE2000 < 25 to the insert" wall test is not used (every pale white wall is ~15 from the pale
  orange insert); the marker follows the wall FAMILY computed from its hex (warm families -> blue). (b) An existing
  image's scale is NOT inferred from its measured shot: the legacy library frames big wall pieces close (art ~50% of the
  picture height, G1), so a non-brief template counts as large unless the vision describe says it stands on a surface.
  (c) The fixed-slot vision describe is one call for all fixed images (not one per image). (d) Auto-planning on panel
  open needs `planner_auto: true` (on in settings.json) and never retries a failed plan by itself.
- G0 (free, SAM + PhotoCraft, 9 stand-ins incl. 2 recoloured blue on a terracotta wall): every build, guard and art-area
  gate PASSED, art at 13-59% of picture height, despill applied (blue: 10.6k and 2.8k px). The template checker FAILED 8 of
  9 on existing issues seen on the source templates too: 1.5-3.5 px edge strips (resampled crops) and the Office Mid Century
  scene's Light Shadow sun angle (fails at 18% as well, so not a tight-shot problem). No builder fix made.
- G1 dry plan for Book Club Cat: see the parent session report. G2 NOT run (no credits).

## 1. Goal

Replace "each room slot rolls its own random look at Generate time" with **one planned set**: when a design's
room slots are built, a planner (interior designer + photographer + curator) looks at the whole design and writes
one scene brief + prompt per open slot in a single pass, with full context of the art and of the slots that already
exist. A deterministic balance/similarity check then rejects sets that repeat themselves, and the planner rewrites
the weakest slots (bounded rounds). Prompts are saved with the slot at plan time, shown on the card behind a
"Show prompt" triangle, editable from the Studio chat, and Generate sends the saved prompt. Library templates are
still used first (free); only new scenes cost credits (~18 each), and the total is shown up front.

Success = the 12 room images of one listing read as one calm, believable shop, but with different settings, shot
sizes, print sizes, ratios, camera sides, light, walls, furniture and house types; small prints shown tight on a
surface, big prints shown wider on a wall.

## 2. Current state (verified 2026-11-19, file:line)

Paths are relative to `005_Ecommerce/Etsy-Ikigai/Portal/`.

**Why the 12 slots look alike**
- `app/production.py:587-588`: a NEW scene calls `rs.pick_look(room, decor)` (fresh random seed) and
  `rs.scene_prompt(...)` independently per click. No slot knows what the others look like.
- `app/room_slots.py:847-879` `pick_look`: weighted random per axis; weights are the same for every slot of the
  same room/decor, so a set of mostly Living room + Bedroom slots converges on the same leaders
  (`straight_on` 69, `eye` 71, `warm_white` 56, `plain_paint` 72, `hung_over_furniture` 62; `room_slots.py:509-597`).
- `app/room_slots.py:294-302` `presentation_for`: frame / mat / canvas is a **sha1 hash of room|decor|ratio**, so
  every slot with the same room+decor+ratio gets the same presentation.
- `app/room_slots.py:212-224` `assign_ratios` + `production.py:332-346` `library_picks` + `scene_templates.py:1171`
  `print_for`: in the live record of Book Club Cat (listing 1 / idea 3) **7 of the 8 rendered slots used
  `Book Club Cat_2x3_24x36.jpg`**, slot 13 used the 11x14 file. Shots are all big wall pieces.
- Scale is never a variable: there is no print-size, shot-size or setting axis. "Room" today = whole-room framing
  (`ROOM_WORDS`, `room_slots.py:51-54`, `scene_prompt` "... interior featuring one vertical piece of wall art").

**Live slot state, Book Club Cat (read-only DB check, `data/portal.db`)**
- Slots 3, 9, 10, 11, 12, 13, **14 and 15 are approved** (the brief said 3, 9-13; 14 = new Office Mid_Century scene,
  15 = library Japandi, both approved since). **Slots 16-19 are empty.** First real use of the planner = slots 16-19.
- `srec["ratio"]` is the plan's ratio, not what was rendered: slot 3 says 2x3 but its template lives in
  `005_Ratio_11x14`. The balance check must read the ratio from `srec["print"]` (the file actually rendered).

**Generation path that the planner plugs into**
- `production.py:558-695` `run_slot`: library pick (free) or new scene: `pick_look` -> `scene_prompt` ->
  `stp.generate_scene` -> `stp.build_psd(scene, ratio, presentation=rs.presentation_for(...))` (596-597) ->
  `stp.save_template(meta={"prompt", "look", ...})` (604-608) -> render -> `guard_quad` + `art_gate` -> place.
  Build failure keeps the scene as `Archive/Scene_No_Insert_NN_<stamp>.png` with the reason (598-603).
- `production.py:676-680`: the slot record is **replaced** (`prod["slots"][str(slot)] = {**out, ...}`), so any
  extra key stored in the slot record (a brief) would be dropped by the next run. Briefs must live outside it or be
  carried over explicitly.
- `production.py:484-497` `start_slot`: one job at a time, global lock.
- `production.py:301-314` `_plan`: slots with an approved image are `locked` (keep room/decor/ratio).
- `scene_templates.py:79` `SCENE_CREDITS = {"nbpro": 18}`; `production.py:317-321` `_engine` gives credits + USD.
- `scene_templates.py:61-62` + `config/settings.json`: `room_scene_aspect` is **"4:3"**; every room render is
  2400x1792 landscape (slot 15: 2655x2000). But the v2 prompt says "The picture is a vertical (portrait)
  photograph" (`room_slots.py:974`). The model gets a contradiction. The planner's prompts state the real
  orientation; the v2 text stays untouched (byte-identical replay).
- `config/print_sizes.json`: **one print file per ratio at the largest size** (2x3 24x36, 3x4 18x24, 4x5 24x30,
  11x14 22x28, ISO A1). "Print size" in a scene is therefore a story/scale choice; the file used is always the
  ratio's file (5x7 -> ISO file, 0.714 vs 0.707).

**Look replay / backwards compatibility**
- `room_slots.py:817-822` `_tables` raises on any version other than 1/2; `pick_look(override=man["look"])`
  replays a saved look; `tests/test_room_look_v2.py:78-103` pins v1 prompts by sha1. No v2 golden hashes exist yet.
- Only `template_build.py:108-152` writes `look` into `template.json`; nothing outside `room_slots.py` reads
  `man["look"]` back. So planner templates can store a new `brief` key without touching any look reader.

**Template builder limits that matter for tight/small scenes**
- `sam_frames.py:177-208` candidates need a clean 4-sided mask >= 400 px containing the box centre;
  `sam_frames.py:78`/`detect` 872-922: rough box from Gemini; `segment_wall` 234-259 clicks the wall at
  +-0.62-0.68 of the frame width and needs a wall mask >= 4x the insert, else wall = None.
- `scene_templates.py:470-478` `art_quad` rejects > 35% off the print ratio; `MAX_CROP 0.35` (1152) for render.
- `room_templates.py:241-276` guard (hue shift, shadow cover <= 35%); `room_templates.py:335-394` art-area gate.
- All 46 live templates were tuned on wall pieces seen at roughly 18-40% of image height. A frame standing on a
  nightstand, shot tight, has never been through SAM, `opening_quad`, `measure_edge_shadows`, `key_light`,
  `light_pattern` or the gate.

**Studio chat (the edit channel)**
- `app/assistant.py:218-242` `run_cli`: headless `claude -p --safe-mode --tools ""`, own system prompt, model from
  settings (`chat_model` sonnet, fallback haiku), stream-json with image blocks. `app/art.py:299` already reuses it
  for the art prompt writer (`art_writer_model`, 180 s timeout). The planner reuses the same function.
- `app/assistant.py:28` ACTIONS, `:79-91` Production actions; `app/prod_chat.py:31` ACTIONS, `:153-168`
  `snapshot_lines`, `:317-365` `ProdHooks.run` (validated against the real record), `offer_regenerate` never spends.
- `app/chat.py:29-31,65-69`: the page sends `prod_idea_id` + `prod_slot` ("Ask chat").
- `app/templates/index.html:781-803` `slotCard`, `:804-819` `paintPanel` (header credit line 812-814), `:801`
  Ask chat button, `:824-832` panel repaints every 3 s while a job runs (innerHTML is rebuilt: open/closed UI state
  must be tracked in JS or it collapses on every repaint).

**Jev / OpenRouter**: `001_Architecture/Skills/openrouter-jev-calls` is for short typed judgments under a token
cap; a 12-brief creative JSON is the wrong job for it. The deterministic check replaces any "judge" model, so the
planner uses only `claude -p` (Tony's plan, no credits). No Fable.

## 3. Taste reference: what Tony's 22 inspiration screenshots show

`Creative_Inspiration/Mock-Up_Inspiration/` (Pinterest crops, 1:1 or near; popup bubbles ignored). Use for lens,
framing, composition, light, scale and setting variety only; never their ratio, never copy a room.

- **Framing is close.** In about 15 of 22 the artwork (frame) fills 55-85% of the picture height; only #05, #12,
  #16, #22 show a real room. Even the "room" ones keep the art as the clear subject with the furniture cut by the
  bottom edge (#01, #02, #19).
- **Straight-on dominates** (#01, #02, #04, #06, #07, #10, #11, #12, #13, #14, #20, #21). Angled shots are a
  minority and gentle: #03 and #18 lean at about 30 degrees, #05/#09 a slight 3/4 from the right, #08 slight left.
- **Camera height is low-to-middle**: floor leans shot from knee height (#06, #07, #15, #18), hung pieces from
  about the height of the furniture top (#01, #02, #17).
- **Display mix**: hung over a sideboard/desk/sofa (#01, #02, #04, #05, #12, #16, #17, #19, #20, #22), floor lean
  against wall (#03, #06, #07, #15, #18), lean on a bench (#08 hung over slatted bench, #14 over low bench),
  hung on raw concrete/brick with nothing below (#13, #21).
- **Light**: warm low sun with one soft-edged diagonal patch across wall and art edge (#01, #14, #21), bright
  soft daylight from a window at the image edge (#05, #10, #16), evening lamp/candle glow with the art evenly lit
  (#11 brass sconces, #18 candles + city window). Shadows always present, mostly soft.
- **Walls are calm and do NOT match the art.** Warm white / limewash / plaster in most; the colour comes from the
  art against a neutral (#02, #04, #07). Contrast pairings Tony saved: yellow art on grey distressed brick (#21),
  warm art on a cool blue-grey bedroom wall (#20), colourful portrait in a dark moody dining room with brass (#11),
  ochre art on raw concrete (#13), Japanese shoji screen + dark vase with red branch (#14), Parisian panelling
  behind a floor lean (#06, #15).
- **Furniture/wood**: walnut credenza (#01), oak desk + rush chair (#02, #17), slatted oak bench (#08), boucle
  curved sofa (#16), green velvet sofa (#19), cognac leather bench (#12), boucle armchair + floating shelves (#22).
  One confident furniture colour per scene at most.
- **Props are few and sculptural**: dried wheat in a stoneware jug, a small bronze figure, a brass candlestick
  (#01); ceramic vases, one plant at the image edge (#04, #13 cactus, #16, #18, #20); a red mushroom lamp on a
  nightstand (#20). #01 shows a book with a readable spine title: exactly what our "no readable text" rule forbids.
- **Frames**: thin walnut/oak floaters and thin oak frames most; black thin frames (#03, #04, #18); thin gold
  (#11, #21, #19 bronze). Big canvases lean or hang without a mat; no mats seen.
- **House types implied**: Paris apartment with balcony window (#16), NYC loft at night (#18), Japanese/Japandi
  (#14), luxe dining (#11), beamed rustic-modern (#22), suburban American colonial window (#01), white entry (#08).
- **What is NOT in them**: small prints shown tight on a nightstand/desk/shelf. That is Tony's new idea; the
  inspiration only tells us how tight, low and straight he likes framing.

## 4. Size, scale and shot mapping

Print sizes = Tony's listing chart (`Listing_Templates/Description_Template_AI.md:27-50`). Every design has all
five ratio files. The scene shows the frame at the chosen real size; the render uses that ratio's print file,
cover-fit (never letterbox, `scene_templates.py:1155` `fit_cover`).

| Ratio (file) | Small (tight) | Medium (medium shot) | Large (wider shot) |
|---|---|---|---|
| 2x3 | 4x6, 6x9, 8x12 | 10x15, 12x18, 16x24 | 20x30, 24x36 |
| 3x4 | 6x8, 9x12 | 12x16, 15x20 | 18x24, 24x32 |
| 4x5 | 4x5, 8x10 | 12x15, 16x20 | 20x25, 24x30 |
| ISO | 5x7, A6, A5, A4 | A3 | A2, A1 |
| 11x14 | (none) | 11x14 | 22x28 |

| Shot | Used for | Frame outer height in the 4:3 picture | What is visible | Typical display |
|---|---|---|---|---|
| tight | small | 45-65% | the frame + the surface it stands on + 1-3 small props at true scale (a cup, a small vase, a few books with plain covers or spines away), wall behind | standing on / leaning on a nightstand, desk, shelf, mantel, console, bath ledge, coffee table |
| medium | medium | 30-50% | art + the furniture piece below/beside it, a slice of floor or wall | hung over a desk, dresser, bench, sideboard; lean on a sideboard |
| wide | large | 18-35% | the wall + main furniture + some room depth | hung over sofa/bed/credenza, floor lean, through a doorway |

Rules (hard, checked in code):
- Shot must match the size's scale band (one step "wider" allowed for medium, never "tighter" than the band for
  large: a 24x36 is never on a nightstand).
- The whole frame stays inside the picture with clear space on all four sides (>= 3% of the picture width/height).
- Minimum art opening height 18% of the picture (SAM/edge-fit floor seen in today's templates).
- Canvas / bare canvas only for medium and large. Small prints: thin frame or a frame with a mat (classic 5x7 in an
  8x10 with mat).
- Scale cues in the prompt: real size in inches and cm, the outer frame size, and one true-scale neighbour
  ("about as tall as the table lamp base", "the cup beside it is a third of its height"). Image models draw "a
  small frame" as a poster otherwise.
- Set balance target over all 12 slots: small/medium/large about a third each (4/4/4, +-1), all five ratios at
  least once, at least 6 distinct sizes.

## 5. Data model

### 5.1 Where it is stored

In the listing record (JSON in `listings.record`, same as everything else in Production), under
`production.set_plan`, **not** inside `production.slots[...]` (that dict is replaced on every run,
`production.py:676`). Nothing new on disk except what `save_template` already writes.

```json
"production": {
  "slots": { "...": "unchanged; a run adds brief_rev + brief_source" },
  "set_plan": {
    "version": 1,
    "status": "planning | ready | needs_attention | failed",
    "message": "plain reason when not ready",
    "created": "2026-11-20T10:02:11", "updated": "...",
    "model": "sonnet", "rounds": 2, "seconds": 143,
    "inputs_key": "sha1 of design tags + rs.plan rooms/decor of open slots + fixed slot files",
    "fixed": { "3": {"descriptor": {...}, "file": "03_Room_...jpg", "from": "measured+look|measured+vision"} },
    "briefs": { "16": { ...brief, see 5.2... } },
    "check": { "pass": true, "failures": [], "scores": {...} },
    "cost": { "library": 1, "new": 3, "credits_per_scene": 18, "credits": 54, "usd": 0.27 }
  }
}
```

### 5.2 One brief

```json
{
  "slot": 16, "rev": 3, "edited_by": "planner | chat", "history": [{"rev": 2, "scene": "...", "at": "..."}],
  "room": "Bedroom", "decor": "Japandi",          // from rs.plan (Tony's ticks honoured), used for filing + library
  "source": "new | library", "library_rel": null,
  "print_size": "5x7", "ratio": "iso", "scale": "small", "shot": "tight",
  "setting": "nightstand", "display": "standing_on_surface",
  "presentation": "mat", "frame_finish": "walnut_frame",
  "camera_side": "left | right | front", "camera_height": "surface | low | seated | counter | eye",
  "lens": "lens_normal | lens_wide | lens_short_tele",
  "light_style": "soft_direct | crisp_direct | dappled | golden_low | soft_even",   // LOOK_AXES keys reused
  "light_from": "left | right | front | behind_camera", "shadow": "soft | hard",
  "depth_of_field": "deep_focus | soft_background | soft_foreground",
  "wall": {"name": "deep teal", "hex": "#2F5D62", "family": "teal_blue", "treatment": "plain_paint"},
  "floor": "pale oak planks",
  "furniture": {"style": "japandi_low_wood", "colour": "walnut", "family": "dark_wood"},
  "house": "london_flat", "buyer": "gift_buyer",
  "props": ["small stoneware cup", "two cloth-bound books, spines facing away"],
  "scene": "60-160 words of plain, positive scene description written by the planner",
  "prompt": "the full assembled prompt actually sent (scene + fixed pipeline blocks), 5.3",
  "lint": {"pass": true, "why": []},
  "stale": false,
  "attempts": [{"at": "...", "result": "built | no_insert | gate_fail", "why": "..."}]
}
```
No rationale field exists anywhere (no "why this fits"); the parser drops unknown keys.

### 5.3 Prompt assembly (code, not the LLM)

`slot_planner.assemble(brief)` = planner's `scene` text + fixed blocks, so the pipeline-safety wording is always
present verbatim and the LLM never has to remember it:
1. `"Photorealistic interior photograph, a 4:3 landscape picture."` (orientation from `room_scene_aspect`).
2. `brief.scene`.
3. Shot + scale sentence from the table in section 4 (size in inches + cm, outer frame size, frame height share).
4. Camera side / height / lens / focus sentences (new v3 phrase table; LOOK_AXES phrases reused where they fit).
5. Light sentence (LOOK_AXES `light_style` phrase + direction + "every scene shows soft visible shadows").
6. Wall sentence: colour name + treatment phrase (wainscoting only "below waist height" or "art centred inside one
   larger panel", `WAINSCOT_RULE` appended unchanged).
7. `_PRINT_AREA` (unchanged) + presentation text (new `_present_text_v3`: frame / mat / canvas / canvas_bare,
   standing-on-surface variant: "stands upright on a slim easel back, tilted back at most 10 degrees").
8. `LOOK_GUARD` (unchanged) + new `PLAN_GUARD_FRAME` ("clear space on all four sides of the frame; nothing overlaps
   any part of it"; the v2 `LOOK_GUARD_FRAME` says "clear wall on all four sides", which is wrong for a frame
   standing on a nightstand, so it is not reused, and not edited).
9. `"Only one piece of art; no other frames, posters or mirrors. No people, no faces, no hands, no pets. Nothing in
   the picture carries readable text: no labels, logos, signs, lettering or book titles; books have plain covers or
   face away. No lamps unless the setting clearly needs one."`

v1 and v2 constants and functions are not edited.

### 5.4 Template metadata

- New-scene templates made from a brief: `template.json` gets `"brief": {...brief without history...}` and the
  existing `"prompt"`; **no `"look"` key** (so no look reader ever sees a v3 dict). Replay of such a template =
  its saved prompt (and its saved scene for free rebuilds, `production.py:533-555`, unchanged).
- Library matching needs shot/scale. **No files are rewritten**: `stp.shot_meta(manifest)` computes on the fly
  from `quad_art` + `canvas` (already in every manifest; Tony's PSDs get them via `manifest_for_render`):
  `art_h_frac` (art quad height / picture height), `shot` (bands of section 4), `camera_side` (left edge vs right
  edge length of the quad, > 3% difference), `light_from` (manifest), `wall_lab` (median Lab of a ring 8-20% outside
  the quad in the scene PNG), cached in memory by PSD mtime. A brief-made template also carries its brief.

## 6. The planner

New module `app/slot_planner.py` (existing `app/` folder; no new folders). Engine: `assistant.run_cli` with its own
system prompt; settings keys with defaults `planner_model: "sonnet"`, `planner_fallback_model: "haiku"`,
`planner_timeout_s: 300`, `planner_rounds: 3`. Runs in a background worker (`spawn`), never in a request.

### 6.1 When it runs
- Automatically, once, when the Production panel opens for a design with open room slots and no `set_plan`
  (same pattern as `auto_styles` via `start_auto`, `production.py:364`).
- Automatically after Tony changes room/style ticks (`save_tags`): only open slots are re-planned.
- Button "Re-plan open slots" on the panel (free).
- Never touches: slots with an image that is approved or pending decision, the running slot, briefs Tony edited
  through the chat (`edited_by: chat`) unless he asks for that slot by name.
- `inputs_key` changes (tags, rooms from `rs.plan`, fixed set) -> open briefs get `stale: true` and a background
  re-plan starts.

### 6.2 Inputs (one prompt, full context)
- Design: title, description, shop styles in use (`effective_styles`, Tony's ticks or the Gemini read), value key
  + accents (`_analysis`), and **the art itself** as an image block (ISO printable, long side 1568 px).
- A contact sheet (one image) of the fixed slots' current images, each labelled with its slot number.
- Fixed slots as JSON descriptors (6.4).
- Open slots: slot number, room + decor from `rs.plan` (Tony's picks are fixed to their slots), which ratios have a
  room folder (`stp.available_rooms`), allowed settings per room (6.5).
- Library candidates per open slot: unused, checker-not-failed templates in that room (any ratio with a folder),
  each with `shot_meta` + decor + presentation + wall family. Max 8 per slot.
- The size chart and section-4 tables; credits per new scene.

### 6.3 System prompt (draft, to be tuned in step 3)

```
You plan the room photographs for one Etsy listing of a printable wall-art design, as three people at once:
an interior designer who furnishes believable homes, an interiors photographer who frames and lights them, and a
curator who decides how a buyer should first meet this artwork. You see the artwork, the photographs that already
exist for this listing, and the open slots you must plan.

Write one scene per open slot in a single pass. The set must feel like one calm, clean, believable shop: real
homes, few objects, good natural light, nothing staged or cluttered. Variety comes from WHERE the piece lives and
HOW it is photographed, never from noise.

What a slot is: the room name is where it is filed. The setting is the surface or wall inside that room (a
nightstand, a desk, a mantel, an entry console, the wall over a bed, a bathroom wall with wallpaper). Setting and
shot are separate choices.

Scale drives framing. Pick a real print size from the chart for each slot. Small prints (4x6 to 8x10, 5x7, A6-A4)
are shown TIGHT: the frame stands or leans on a surface and fills about half to two thirds of the picture height,
with one to three small everyday objects at true scale beside it. Medium prints (11x14, 12x16 to 16x24, A3) are
medium shots with the furniture below. Large prints (18x24 and up, A2, A1, 22x28) are wider shots on a wall or
leaning on the floor. Across the whole listing use roughly a third small, a third medium, a third large, all five
ratios, and several different sizes.

The art ties in with the scene, which does NOT mean matching its colours. Do not take the wall or furniture
colours from the artwork. Contrast and complement are welcome; quiet neutrals are the default; one or two slots may
use a loud wall or a bold furniture piece when it flatters this piece (a bold desert-feeling piece in a pale Japandi
room, a colourful piece against deep teal). Think of the buyer each scene speaks to: big-wall decorator, small-space
renter, gift buyer, desk or bookshelf person, parent, cat lover, reader.

Photography taste (from the shop owner's reference board): mostly straight-on or a gentle angle, low to middle
camera height, close framing with the art as the clear subject, furniture often cut by the bottom edge, warm low
sun or soft window daylight with soft visible shadows, plaster or limewash walls, walnut and oak, a few sculptural
objects (stoneware, dried stems, a small brass or bronze piece, one plant at the edge). Vary across the set: camera
side (left looking right, right looking left, dead-on), height, lens, light direction and quality, shadow softness,
depth of field, how much room shows, wall colour and texture (paint, plaster, limewash, wallpaper, panelling, brick,
tile, concrete), furniture style AND colour, house type and region (London flat, NYC loft, Paris apartment, English
cottage, Scandinavian house, coastal cottage, southwestern adobe, mid-century ranch, Japanese-style home,
brownstone).

Hard rules, never broken:
- No people, faces, hands or pets. One piece of art only. No other frames, posters or mirrors.
- Nothing readable: no labels, logos, signs, lettering, book titles (books have plain covers or face away).
- Every scene shows visible shadows (soft or crisp). The art face is flat, upright, in sharp focus, evenly lit.
- The whole frame is inside the picture with clear space around it; nothing overlaps the frame.
- The frame contrasts with the wall in tone. Canvas floater frames are natural wood, never black.
- Walls are never orange, peach, apricot, terracotta, coral, rust, salmon, sand or tan (that family is reserved for
  the blank print area the pipeline replaces). Southwestern / adobe homes use white, bone, turquoise, cobalt or
  sage plaster; terracotta may appear only in floor tiles or pots away from the frame.
- Wainscoting or panelling only below waist height, or with the art centred inside one larger panel.
- Do not describe the artwork; the print area is replaced later.
- Prefer a listed library template for a slot when one fits the set (it is free); otherwise plan a new scene.

Output ONLY one JSON object, no prose, no reasons, no explanations, matching this schema: {schema}
```

### 6.4 Fixed-slot descriptors (measured first, guessed never)
For each slot with an approved or pending image, built once and cached in `set_plan.fixed` keyed by file name:
- Measured from the template manifest (deterministic): `shot` + `art_h_frac`, `camera_side`, `light_from`,
  `presentation`, `wall_lab` -> `wall.family`, ratio from `srec["print"]` (e.g. `_2x3_` / `_11x14_`); scale
  inferred from shot (tight -> small, medium -> medium, wide -> large).
- From a v2 `look` when the template has one: display, camera_height, lens, depth_of_field, wall_treatment,
  furniture family, light_style.
- The rest (setting, furniture style, house type, buyer) from ONE vision call (`run_cli` with the slot image,
  enum-only JSON, Sonnet), cached per file. Unknown values are ignored by the check, never treated as duplicates.

### 6.5 Enums (the planner must pick from these; free text only in `scene`, `floor`, `props`, `wall.name`)
- `setting` per room: Living room {over_sofa, sideboard_top, coffee_table, bookshelf, mantel, console_behind_sofa,
  side_table, floor_beside_chair, entry_console*}; Bedroom {over_bed, nightstand, dresser_top, floor_beside_bed,
  reading_corner}; Office {desk_top, over_desk, shelf, credenza_top, floor_lean}; Kitchen & dining {open_shelf,
  counter, over_dining_table, sideboard, bar_cart}; Bathroom {over_bath, over_vanity, bath_ledge, small_shelf,
  wallpaper_wall}; Kids/Nursery {over_crib, dresser_top, toy_shelf, picture_ledge}; Game room {over_sofa,
  media_console, shelf}; Creative space {work_table, picture_ledge, studio_wall}. (*see open question 2)
- `display`: hung_over_furniture, hung_bare_wall, floor_lean, lean_on_surface, standing_on_surface, shelf_ledge.
- `house`, `buyer`, `furniture.style`, `wall.family`, `wall.treatment`: fixed lists in the module (about 10-12 each).

## 7. Deterministic checks

### 7.1 Per-brief lint (hard; a failing brief cannot be generated)
- Enums valid; `print_size` in the chart for its `ratio`; ratio has a room folder for the slot's room.
- Shot within the size's scale band (section 4); canvas only medium/large; tight -> 1-3 props, others <= 5.
- `camera_height` low + `display` hung + shot tight is rejected (keystoning, same rule as `room_slots.py:776`);
  lens_wide + tight rejected; lens_short_tele + wide rejected (mirrors `_look_fits`, `room_slots.py:778-782`).
- **Wall colour vs the orange insert** (reconciles "no orange walls" with "loud walls allowed"): `wall.hex` ->
  CIELAB. Insert = RGB 250,215,170 (`room_slots.py:284`). Reject when deltaE2000 < 25 to the insert, or when the
  hue angle h is 25-80 degrees with chroma C* > 14 and L* > 40 (orange / peach / apricot / terracotta / sand / tan
  family). Deep warm darks (L* < 40: oxblood, chocolate) and every cool or yellow (h > 82: mustard, saffron) loud
  colour pass. `scene` text is also scanned for those colour words next to "wall".
- Frame vs wall contrast: frame finish L* table (black 15, walnut 35, oak 65, gold 60, white 95) vs wall L*,
  difference >= 15; blush walls only black/walnut (same as `room_slots.py:802-813`). Canvas -> natural wood.
- Panelling/wainscoting treatment only with hung display and the words "centred inside one larger panel" or
  "below waist height" present.
- Text lint on `scene` + `props`: banned words (person, woman, man, hand, face, cat, dog, pet, label, sign, logo,
  lettering, title, poster, mirror, gallery wall, second frame, neon sign, "why", "because", "perfect for"); length
  60-160 words.

### 7.2 Set balance + similarity (`check_set(briefs, fixed) -> {pass, failures, blame}`)
Fixed slots count in every tally but are never blamed or rewritten. Targets for open slots are "fill the
deficit": target_total[bucket] - fixed[bucket], clipped at 0, then spread over the open slots.

| Rule | Fails when |
|---|---|
| scale mix | any of small/medium/large is more than 1 away from its achievable target |
| ratio mix | a ratio missing while open slots could add it; open slots add to a ratio already at >= 40% of the set |
| sizes | fewer than min(6, n) distinct sizes; a size used twice among open slots |
| camera side | one side > 50% of the set; left or right absent (n >= 6); two neighbouring slots (listing order) share side AND shot |
| light | one `light_style` > 40%; `light_from` only one side; no `hard` or no `soft` shadow in the set |
| wall | one wall family > 40% (white/cream) or > 3 slots (others); loud/deep walls (C* > 35 or L* < 35) > 2; one treatment > 50%; patterned wallpaper > 1 |
| furniture | same (style, colour) twice; one colour family > 3 |
| setting / house / buyer | same setting twice (fixed included); one house type > 2; fewer than 4 buyer types |
| presentation | one presentation > 60%; mat absent when >= 2 small slots |
| pairwise | weighted similarity >= 0.6 for any pair (weights: setting 2, shot 2, camera_side 1.5, wall family 1.5, display 1, presentation 1, furniture 1, house 1, light_style 1, wall treatment 1, height 0.5, lens 0.5, dof 0.5; equal = 1, unknown = 0), or scene-text token Jaccard >= 0.5 |

`blame`: each failure adds points to the open slots that cause it (the later slot of a similar pair, the slots in
the over-full bucket). Sorted descending = the slots to rewrite.

### 7.3 Library-first swap (deterministic)
After the check passes, for every `new` brief try each library candidate of that slot (room match, any ratio with a
folder, `shot_meta.shot` equal to the brief's shot, checker not failed, unused in this listing). Accept the swap
(`source: library`, brief rewritten from the template's measured descriptor + its saved brief/look) when the set
still passes and no pair gets more similar than 0.6. Credits fall accordingly.

### 7.4 Rewrite loop
1. Call 1: full plan. Parse (FENCE-less JSON; one retry on parse failure with "return valid JSON only").
2. Lint each brief; derive `ratio`/`scale` from `print_size` in code (the LLM cannot get them wrong).
3. `check_set`. Pass -> 7.3 -> save `ready`.
4. Fail -> call 2..`planner_rounds+1`: the current set + the failure list in plain words + "rewrite only slots
   [top 4 by blame and every lint failure]; return those slots only". Merge, go to 2.
5. After the last round: keep the round with the lowest total blame; status `needs_attention` with the failures
   listed on the panel. Briefs with lint failures cannot be generated (card says "Re-plan this slot"); balance-only
   failures can still be generated.
6. Planner unavailable (`ChatUnavailable`): status `failed`, message shown; Generate falls back (8.3).

## 8. Generate consumes the saved prompt

### 8.1 `run_slot` (`production.py:558`)
- At start, read `set_plan.briefs[str(slot)]`. Use it when it exists, is not stale, and its lint passed.
- `source: library` -> the existing library path with `t = brief.library_rel` (if still in the library and not
  failed; else fall through to `library_picks` as today).
- `source: new` -> skip `pick_look`/`scene_prompt`; `prompt = brief.prompt`;
  `build_psd(scene, brief.ratio, ..., presentation=brief.presentation)` (canvas_bare -> "canvas", as today);
  `save_template(room, decor, brief.ratio, ..., meta={"prompt", "brief", engine...})`;
  `print_for(arts, RATIO_VALUE[brief.ratio], PRINT_RATIO_TAG[brief.ratio])`.
- Slot record gets `brief_rev`, `brief_source`; the brief is appended to with `attempts`.
- After a successful build: measure the new template's `shot_meta`; if the measured shot is outside the brief's
  band, flag it on the card ("drawn wider/tighter than planned") but keep the image (Tony judges).

### 8.2 Card `next` source
`library_picks` (`production.py:332`) gets the briefs: a slot with `source: library` returns its template; a slot
with `source: new` returns None (new scene) even if an old-style match exists. Slots without a brief: unchanged.

### 8.3 Fallback (unchanged behaviour)
No `set_plan`, no brief for the slot, stale brief while the planner is down, or `failed` plan -> exactly today's
path: `rs.pick_look(room, decor)` + `rs.scene_prompt(...)` + `presentation_for`. The card says "random look (no
plan)" so Tony knows.

### 8.4 Failures of a brief scene
- `stp.TemplateError` in `build_psd` -> existing behaviour (scene kept in `03-Etsy Images/Archive/` with the
  reason, `production.py:598-603`) + `attempts` entry `no_insert`.
- Gate/guard fail -> existing flagged-in-Archive behaviour + `attempts` entry `gate_fail`.
- Two failed attempts on a `tight` brief -> the card offers "Plan this slot one step wider" (free re-plan of that
  slot, medium shot); never automatic regeneration (credits only on Tony's click).

## 9. UI (index.html, studio.py, production.py)

- `production.panel` adds `set_plan` {status, message, rounds, check.failures (plain words), cost, stale} and per
  card `brief` {print_size, shot, setting, source, prompt, scene, rev, edited_by, lint}.
- Card head (`index.html:783`): second line becomes `5x7 · tight · nightstand · ISO` (facts only).
- Card body: `<details class="pprompt" data-pprompt="16"><summary>Show prompt</summary><pre>…</pre></details>`
  under the picture; collapsed by default; native triangle; the card grows when opened. Open state kept in a JS
  `Set` keyed by idea+slot and re-applied in `paintPanel`, because the panel repaints every 3 s during a job
  (`index.html:831`). Inside: the full assembled prompt, the planner part first; "edited in chat" tag when
  `edited_by: chat`; library briefs show "Library template X (free); no prompt sent".
- Panel header (`index.html:812-814`): one line under the credit box:
  `Scene plan: ready · 4 open slots · 1 library (free) · 3 new ≈ 54 credits ($0.27)`, or `Planning scenes…`,
  or `Needs attention: <first failure>`; a `Re-plan open slots` ghost button. No rationale text anywhere.
- Routes in `studio.py`: `POST /api/production/{id}/plan {slots?: [int]}` (spawn planner, return panel);
  `planner.recover(con)` at mount marks a `planning` status left by a restart as `failed`.
- Generate-all hook only: `production.generate_queue(con, settings, idea_id)` returns the ordered open slots with
  source and credits (library first), exposed as `pan.queue`. No button (future feature; credit cap to ask first).

## 10. Studio chat: edit a slot's prompt before credits

- `prod_chat.snapshot_lines` (`prod_chat.py:153`): per slot one short brief line (size · shot · setting · source ·
  rev); for the pointed slot (`open_slot`) and slots named in the message, the full `scene` text + main fields.
- New actions (`prod_chat.ACTIONS`, `assistant.ACTIONS`, system prompt lines after `assistant.py:91`):
  - `slot_prompt_edit {idea_id, slot, scene?, fields?}`: the chat rewrites the scene text from Tony's words
    and/or changes enum fields (`print_size`, `shot`, `setting`, `camera_side`, `wall`, ...). The Portal runs the
    lint (7.1) and `check_set` (7.2) with the edit; lint failure = refused with the reason; balance-only failure =
    saved, and the reply line says which balance rule it now breaks. Saves `rev+1`, `edited_by: chat`, old version
    into `history`, re-assembles `prompt`. Only for slots without an approved image.
  - `slot_prompt_revert {idea_id, slot}`: back to the previous rev.
  - Generating stays a button (`offer_regenerate` already exists; label shows "new AI scene, about 18 credits").
- The chat never writes a rationale; its system prompt line says "describe the scene, never explain why".

## 11. Tests (pytest, `tests/`; generator, `ask` and `art_gate` are injected as today)

1. **Byte-identical replay (step 0, before any change):** capture sha1 of `scene_prompt` for 4 v2 looks x 4
   presentations at the current commit into `tests/test_room_look_v2.py` (new `V2` table, like `V1` at :78);
   keep the V1 test. After every later step both pass unchanged.
2. **Old templates untouched:** sha1 of every live `template.json` before/after a planner run on a scratch DB
   copy -> identical; `pick_look(override=man["look"])` on the 5 live v2 looks reproduces each saved `prompt`.
3. **Approved slots untouched:** planner run on a scratch copy of Book Club Cat's record: `production.slots` for
   3, 9-15 deep-equal before/after, their JPG mtimes unchanged, no brief written for them.
4. **Fallback:** no `set_plan` -> `run_slot` sends exactly `rs.scene_prompt(...)` of a seeded `pick_look`
   (monkeypatched seed); `set_plan.status == "failed"` -> same.
5. **Lint unit tests:** each forbidden wall (terracotta #C8643C, peach #FFCBA4, sand #D8C3A0, coral) rejected;
   loud allowed walls (deep teal, cobalt, emerald, oxblood, mustard #D4A017, plum) pass; oak frame on ivory
   rejected; 24x36 + tight rejected; 5x7 + canvas rejected; size not in ratio chart rejected; banned words rejected.
6. **check_set unit tests (deterministic):** 12 identical briefs -> fails scale, side, setting, pairwise with blame
   on the open slots only; a hand-built good set of 12 passes; Book Club Cat case (8 fixed large 2x3 + 4 open):
   open slots must be small/medium and add 3x4, 4x5, ISO; a set that does so passes, one that adds a 2x3 fails;
   neighbour rule; unknown fixed fields never count as equal.
7. **Planner loop with canned replies:** reply 1 fails (2 close pairs) -> reply 2 rewrites only the blamed slots ->
   passes in round 2; malformed JSON -> one retry; never-passing replies -> stops at `planner_rounds`, keeps the
   lowest-blame set, status `needs_attention`; extra keys (a "why") are dropped.
8. **Library-first swap:** a candidate with matching shot and no similarity clash replaces a `new` brief; cost drops
   by 18; a clashing candidate is not used.
9. **run_slot with a brief:** stub generator records the prompt == `brief.prompt`; `build_psd` gets
   `brief.presentation`; `template.json` has `brief`, no `look`; slot record keeps `brief_rev` after the run.
10. **Chat:** `slot_prompt_edit` refused on an approved slot, refused on a lint failure, saved with rev+1 and
    history on success; `revert` restores; snapshot shows the open slot's scene text.
11. **UI smoke (browser, Portal on 8800):** Show prompt opens/closes and stays open across a repaint; cost line
    numbers match `set_plan.cost`.
12. **Small-scene gate (section 12):** stand-in tests in pytest marked `sam` (skipped without the SAM venv).

## 12. Gate: one small scene end to end before relying on tight shots

- **G0 stand-ins (free):** take 3 existing scenes (Office 225742 canvas, Bedroom 002116 canvas, Office Mid Century
  174105 mat), crop around the frame so it fills 55% and 65% of a 4:3 picture, resample to 2400x1792, and run
  `build_psd` -> `render_psd` -> `guard_quad` -> `art_gate` -> template checker on each. Also one "small in wide"
  stand-in (frame at 18% height). Record per stage pass/fail. Fix only what fails (likely: `segment_wall` click
  points outside the picture, `gemini_box` on a crowded tabletop, `key_light` with little wall).
- **G1 dry plan (free):** run the planner on Book Club Cat (slots 16-19) with `--dry-run` (prints briefs + check
  report, writes nothing). Tony reads the four prompts.
- **G2 real scene (about 18 credits, ONLY after Tony says go):** generate one tight small brief (e.g. 5x7 ISO with a
  mat on a nightstand) into slot 16 through the normal card button. Pass = built, gate + guard pass, measured shot
  tight, Tony approves the look.
- **If G2 fails:** the scene is kept in `03-Etsy Images/Archive/` with the reason (existing), the attempt is logged
  on the brief, the slot offers "Plan this slot one step wider"; a builder fix for the specific failure is a
  separate commit tested on the archived scene for free (`rebuild_from_scene` style), then Tony decides on a second
  paid try. Until G2 passes, the planner caps tight shots at 2 per set (setting `planner_max_tight: 2`).

## 13. Ordered build steps (one commit each)

1. Tests: add v2 golden hashes (11.1) and the template.json/approved-slot snapshot helpers. No behaviour change.
2. `app/slot_planner.py` part 1: enums, size chart, shot table, wall Lab check, frame contrast, text lint,
   `assemble()` + `_present_text_v3` + `PLAN_GUARD_FRAME`. Tests 11.5.
3. `check_set` + `blame` + fixed-slot measurement from manifests (`stp.shot_meta`, `wall_lab`). Tests 11.6.
4. Planner prompt, `plan_set()` with injected `ask`, parse, rewrite loop, library-first swap, `--dry-run`
   entry point (`python -m app.slot_planner --idea 3 --dry-run`). Tests 11.7, 11.8.
5. Storage + jobs: `set_plan` in the record, background run on panel open / tag change / button, `recover`,
   `inputs_key` staleness, fixed-slot vision describe (cached). Tests 11.2, 11.3.
6. `run_slot` + `library_picks` consume briefs; fallback path; attempts log; measured-shot flag. Tests 11.4, 11.9.
7. **G0 stand-in gate** (section 12); builder fixes if needed, each its own commit.
8. UI: card facts line, Show prompt details, plan/cost header line, Re-plan button, `pan.queue`. Smoke 11.11.
9. Studio chat: snapshot brief lines, `slot_prompt_edit` / `slot_prompt_revert`, system prompt lines. Tests 11.10.
10. G1 dry plan on Book Club Cat, show Tony; then G2 only on his go.
11. Docs: this file's status, `Pipeline_Docs/Ikigai_Portal_Build_Plan_2026-11-10.md` pointer, `Directory.md` if
    it lists Portal modules; memory note after Tony approves.

## 14. Risks

- **Image model ignores scale:** a "5x7 on a nightstand" drawn as a poster. Mitigation: inches + cm + outer frame
  size + a true-scale neighbour in the prompt; measured shot after build flags drift; Tony judges realism.
- **Tight shots break the builder** (wall mask, Gemini box in clutter, little wall for `key_light`, frame near the
  picture edge). Mitigation: G0 stand-ins, 3% margin rule, `planner_max_tight` cap until G2 passes.
- **Prompt and enums disagree** (scene text says "from the right", enum says left). Mitigation: assembled
  sentences come from the enums and follow the scene text; lint scans scene text for side/size words that
  contradict the enums.
- **Fixed slots dominate** (Book Club Cat: 8 large wall pieces): thirds are not reachable; the check uses
  achievable deficit targets, so open slots go small/medium instead of failing forever.
- **Vision describe of fixed slots is a guess.** Only categorical fields come from it; measured fields win; unknown
  never counts as a duplicate.
- **Planner latency** (1-4 calls, 1-3 minutes each): background only; card buttons work meanwhile (fallback path).
- **Loud colours vs despill:** `despill.py` removes orange cast near the art; a mustard or oxblood wall right
  beside the frame may get partly neutralised. Check on the first loud-wall scene; the gate does not catch it.
- **v2 prompt says portrait, kie returns 4:3 landscape** (2.0): planner prompts fix it for new scenes only; old
  path unchanged by design.
- **Library candidates are mostly large wall pieces:** small/tight slots will be new scenes at first (cost); the
  library fills up with tight templates over time.

## 15. Open questions for Tony (few)

1. **Adobe / warm walls vs the orange marker.** Proposed rule: never orange/peach/terracotta/sand/tan walls;
   southwestern adobe is shown with white, bone, turquoise or cobalt plaster and terracotta only in floor tiles or
   pots away from the frame. OK? (Alternative, later and separate: a cool-coloured marker insert for warm-wall
   scenes, which needs SAM, despill and gate changes and its own test.)
2. **Entry console / hallway settings:** there is no Entryway room folder (`room_slots.py:49` proposes
   `009_Entryway`). File those scenes under Living_Rooms until you make the folder, or skip entry settings for now?
3. **G2 go:** after the free dry plan, may I spend about 18 credits on one tight 5x7 scene in Book Club Cat slot 16?
