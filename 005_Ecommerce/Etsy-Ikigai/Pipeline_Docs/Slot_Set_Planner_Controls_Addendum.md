---
title: "Slot-Set Planner: controls addendum (reference refresh, reference share + closeness sliders, engine pickers, Generate all)"
type: plan
domain: ecommerce
tags: [ikigai-digital-studios, portal, production, mockups, room-templates, slot-planner, art-engines]
created: 2026-11-20
status: built 2026-11-21 on Tony's 'Yes, build all' (sections A-F + A/B, see Build status); one commit by the parent session; paid steps only on Tony's click
extends: Pipeline_Docs/Slot_Set_Planner_Plan.md, Pipeline_Docs/Slot_Set_Planner_Realism_Addendum.md
---

# Slot-Set Planner: controls addendum (2026-11-20)

**Build status (2026-11-21).** Built: A Refresh library (normalise, low-res sweep, `claude -p` rename, overlay scan
`scene_scan.scan_reference`, crop / LaMa with the confidence check, has_art, register tags, Looks fine / Archive it /
capped Nano fill route, job + routes + UI); B share slider (`n_image`, `enforce_share`, tag sentence, `reference_mode`);
C closeness slider (four bands, `prep_for`, band clauses, `ref_takeaways`, A/B variants on the batch runner); D engines
v2 (`engines.json` v2, kie / fal / WaveSpeed adapters, price labels, `--test` CLI, `data/engine_status.json`); E room
engine per panel and per card, upscale of small scenes, per-engine room check (gate), template.json engine fields,
grades per engine; F Generate all (estimate, key, cap, hard-stop rules, cancel, recover, end report); G `app/prefs.py`.
Golden locks in `tests/test_controls_golden.py`. Flux 3 fal id checked in fal's OpenAPI. Run for real on the board
2026-11-21 (free): 0048-0050 added (0050 usable), registers on all 29. Not run (paid, Tony's click): the engine test
round (`python -m app.engines --test ... --yes`, about 61 cr-eq), the first room scene per new engine, A/B generation,
Nano fill.

Plan only. Paths are relative to `005_Ecommerce/Etsy-Ikigai/Portal/` unless they start with `Creative_Inspiration/`,
`Room_Templates/` or `Designs/`. Nothing here spends kie.ai credits or fal / WaveSpeed dollars without Tony's click.

**Dependency.** The realism addendum is NOT built yet (checked 2026-11-20: no `app/references.py`, no
`app/scene_scan.py`; `scene_templates.generate_scene` has no `ref_imgs`). This addendum builds on top of it: its build
starts after realism-addendum steps 1-9 (8.2) and both go into the one final commit if built in the same session.

Decided here without asking (logic or Tony already said it): one commit at the end; no new folders (all new files sit
in existing folders: `app/`, `config/`, `data/`, `tests/`, `Mock-Up_Inspiration/`, its `Archive/`); never delete;
never auto-approve; paid work only on a click that showed the cost first; no "why it fits" text on cards; portrait
art, 4:3 room photo.

---

## 0. Live facts this plan rests on (verified 2026-11-20)

| Fact | Source |
|---|---|
| Art engines: `config/engines.json` lists `gpt-image-2` (default, 6 cr), `nano-banana-2` (8), `nano-banana-pro` (18); `engines.KieAdapter` = createTask + poll recordInfo; `adapter_for` raises for any provider other than `kie` | `app/engines.py:155-162` |
| Build art cost check is in kie credits: `need = credits_per_image * n`, refused when `ad.credits() < need` | `app/art.py:520-531` |
| Art pull-down label = `engineLabel()`; select `data-art="engine"` | `templates/index.html:647-675` |
| Room scenes: `generate_scene` calls `kie_edit.generate(eng, out, prompt, aspect, res)`; engine = setting `room_scene_engine` (`"nbpro"`); `SCENE_CREDITS = {"nbpro": 18}` | `scene_templates.py:79,1104-1115`, `production.py:318-322` |
| `kie_edit.MODELS` short ids: nbpro, nb21, gpt25, gpt25s, nb2, gpt; `TEXT_TO_IMAGE = {nbpro, nb21, nb2}` | `app/kie_edit.py` |
| One job at a time: `_job` + `_job_lock`, `start_slot` claims, `run_slot` always releases; `run_slot` swallows errors into the slot record and returns nothing | `production.py:43,546-560,639-822` |
| `queue_of(cards)` = Generate-all hook, library first then slot order, credits per slot, exposed as `pan.queue` | `production.py:469-481` |
| Plan line + "Re-plan open slots" button, header credit box `pcred`; panel repaints only when data changed | `index.html:835-842,861-868` |
| Settings: `config/settings.json` loaded once at startup (`main.py:19`), never written by code; DB has a `meta` key/value table with `get_meta` / `set_meta` | `app/db.py:52,139-147` |
| Key NAMES present in `~/.env-secrets`: `KIE_API_KEY`, `FAL_AI_API_KEY`, `WAVESPEED_API_KEY` (values never read or printed) | name-only grep |
| Reference folder: 26 `NNNN_*.png` in `Creative_Inspiration/Mock-Up_Inspiration/`, `Archive/` holds originals + low-res; `Rename_Log.md` (id, original, new) and `Cleanup_Log.md` (crop / LaMa / Nano rules) | folder listing |
| LaMa model: `~/pinokio/api/comfy.git/app/models/inpaint/big-lama.pt`; SAM venv `~/.cache/ikigai-sam/bin/python` (has torch) | `find` |
| Nano fill for clean-up already exists as `app/wide_fill.py` (nb21 wide crop, 6 credits at 2K, measured 2026-11-15) | `app/wide_fill.py:1-35` |

---

## A. Reference library Refresh button

### A.1 What one click does (in order, per new or changed image)
"Not yet processed" = any image in `reference_dir` (not in `Archive/`) that is not `NNNN_<Words>.png`, or is one but
has no manifest entry, or whose sha1 differs from its manifest entry. Accepted inputs: png, jpg, jpeg, webp, heic
(heic converted with macOS `sips -s format png`, free).

1. **Normalise** (free): apply EXIF orientation, re-save as PNG (drops EXIF, including GPS on Tony's real-home photos
   before anything is uploaded anywhere). Longest side > `reference_max_side` (2048): the untouched original goes to
   `Archive/` first (backup rule A.3), the working PNG is resized to 2048 (Lanczos).
2. **Low-res sweep** (free): longest side <= `reference_lowres_max` (400) -> moved to `Archive/` unchanged, no
   rename, listed "archived: too small (320 px)". Same as Tony's 2026-11-20 sweep.
3. **Rename** (free, `claude -p` vision through `assistant.run_cli`, Tony's plan): batches of 8 images, enum-free name
   words only (setting, surface, frame, scale, camera; never popups or overlay labels; <= 10 Title_Case words, ASCII,
   `_` separators). Next id = 1 + max id over the folder, `Archive/` and `Rename_Log.md` (never reuses an id).
   Appends rows to `Rename_Log.md` under a dated heading `## YYYY-MM-DD refresh` (id | original_filename |
   new_filename). Name collision -> `_2`.
4. **Overlay detection** (free except Gemini flash-lite, well under a cent per image): `scene_scan.scan(png,
   mode="reference")` from the realism addendum (OCR tiles + one Gemini call) with a reference prompt that lists the
   overlays seen so far: Pinterest "Visit site" / lens buttons, "Deal" bubbles, video timers, carousel arrows, shop
   names, tiled mock-up-store watermarks, "insert your own design" circles, captions. The same Gemini reply returns
   the frame box, so the next steps know where the frame is. Findings inside the artwork are ignored (the blank covers
   them).
5. **Overlay removal**, choosing like `Cleanup_Log.md` did:
   - **crop** (Pillow) when the finding touches an edge, the strip to remove is <= 8% of that side, and the strip does
     not touch the frame box (dilated 3%);
   - else **LaMa** (big-lama TorchScript, run in the SAM venv via a small script mode `python -m app.references
     --lama <in> <mask> <out>`), mask = OCR text pixels or the finding's box, dilated 6 px; result pasted back only
     inside the mask (outside pixels bit-identical);
   - **confidence check** after LaMa (free): (a) re-scan the region: no finding left; (b) texture match: Laplacian
     variance inside the mask / in a 12 px ring around it within 0.35-3.0; (c) mask area <= 2% of the picture and does
     not touch the frame box. Any miss -> `cleanup.confidence: "low"`, the image is `usable: false, why: "clean-up
     needs your eye"` and goes in the result list with a before/after crop. It is never silently accepted.
6. **Blank + measure + manifest** (realism addendum 1.2 steps 2-5, unchanged): SAM art quad, fill with the wall's
   marker colour, `_Blank.png`, measured fields, usable checks. New: a photo with no framed art (real-home photos often
   have none) gets `has_art: false`, `blank_method: "none"`, `_Blank.png` = the cleaned photo itself; usable for
   tag-only text and, as an image, only at closeness < 50 (section C), never for the "close" band.
7. **Tags + register** (free, `claude -p` vision, batches of 8): the realism addendum's enum tags plus a new
   `register` tag (A.4). Runs for every new entry and once for every existing entry missing `register` (the 26 today).
   `tags_by: "tony"` entries are never overwritten.

Idempotent: a second click with nothing new does no work and writes nothing (sha1 + `prep_version` check, realism 1.2
step 1). Never deletes: files only move into `Archive/` or get a backup copy there.

### A.2 Nano fill (the only paid part, always a separate click)
The background run never spends. When LaMa is low-confidence on a wall, window or view (LaMa smeared 0024's garden
view before), the result list shows one button: **"Nano fill N images · about 6 x N credits"**, capped by
`reference_nano_max_credits` (30; the button refuses more and says so). It runs `wide_fill` (nb21, 6 credits each,
measured) on the same mask, backs up first, re-runs the confidence check, logs to `Cleanup_Log.md`. A kie refusal
("flagged as sensitive", 0028) costs nothing and is listed. Rows also get **"Looks fine"** (sets `cleanup.ok_by:
"tony"`, `usable` re-evaluated) and **"Archive it"** (moves source + `_Blank` to `Archive/`).

### A.3 Backups and logs
- Before any edit (resize, crop, LaMa, Nano): untouched original copied to `Archive/<same filename>`; if that name is
  taken, `Archive/<stem>_Original.png`, then `_Original_2`, ... Never overwritten.
- `Cleanup_Log.md` gets a dated `## YYYY-MM-DD refresh` table in its existing format (id | overlay found | where | fix
  used | result) and a totals line with kie credits spent (0 unless Nano ran).

### A.4 Register tag (fit between art and home)
`REGISTERS = ("grand_period", "upscale_modern", "ordinary_apartment", "ordinary_house", "small_rental", "japandi",
"industrial_loft", "farmhouse_cottage", "boho_eclectic", "family_kids", "workspace_studio")`.
- Planner schema gains a top-level `registers_ok` (2-6 values) chosen once per plan for the artwork ("a cozy cat
  print fits ordinary_apartment, ordinary_house, small_rental, family_kids, farmhouse_cottage; not grand_period").
- `validate_references` (realism 2.1) adds: the reference's `register` must be in `registers_ok`; otherwise it is
  reassigned by code (score + 3 for a register match). Missing `registers_ok` -> all allowed (logged).
- No reference fits -> that slot is planned text-only without a reference and counts against the share (section B).

### A.5 Code
- `app/references.py` (realism addendum module) gains `refresh(settings, ask_vision, scan, lama, log, progress)`,
  `lama_fill(...)`, `rename_batch(...)`, `register_batch(...)`, `nano_fill(ids, settings, generator)`.
- Manifest entry additions: `register`, `has_art`, `cleanup {overlays: [{type, box}], method: crop|lama|nano|none,
  confidence: high|low, ok_by?, original: "Archive/...", at}`, `renamed_from`, `kie_refused?`.
- Writes are atomic (temp + rename) under `references.LOCK`; the planner reads a snapshot under the same lock.
- Job: module state `_refresh = {running, step, done, total, current, results[], started, finished}`; worker via
  the Portal's `spawn`; `recover()` marks an interrupted run "stopped by a restart" (no files half-written thanks to
  atomic writes).
- Routes (`studio.py`): `POST /api/references/refresh` (start; 422 if running), `GET /api/references/refresh`
  (progress + results + counts), `POST /api/references/{id}/ok`, `POST /api/references/{id}/archive`,
  `POST /api/references/nano {ids}` (paid, cap enforced server-side).

### A.6 UI (Production tab, under the plan line)
`References: 22 usable · 2 need your eye · last refresh 21:14  [Refresh library]`. While running:
`Refreshing references 7/15: 0049 finding the artwork…` (panel poll already runs every 3 s; `waiting` gains
`refresh.running`). Result list in a `<details>` (open state kept in a JS Set like Show prompt), one line per image:
`0048 · was IMG_2231.HEIC · cleaned (LaMa, 1 spot) · ordinary_apartment · ready` /
`0049 · archived: too small (380 px)` / `0050 · needs your eye: LaMa on the window [before/after] [Looks fine] [Archive it]`.

### A.7 Tests (`tests/test_references.py`, synthetic Pillow images; SAM, LaMa, vision, scan injected)
New jpg + heic-named stub -> renamed `NNNN_...png`, Rename_Log row, id continues after `Archive/` max; 380 px image ->
moved to Archive unchanged; corner "Deal" bubble -> crop, original backed up with same name, `_Original` when taken;
mid-wall watermark -> LaMa stub, pixels outside mask identical; smeared stub -> `confidence: low`, `usable: false`;
second run writes nothing (mtimes + sha1 unchanged); `tags_by: tony` untouched; no-art photo -> `has_art: false`;
register missing on old entries -> one vision batch; Nano route refuses above the cap, never called by `refresh`.

---

## B. "Share of slots that get a reference" slider

### B.1 Meaning and maths
Share of the OPEN slots being planned (never approved / fixed ones) whose reference is SENT AS AN IMAGE. Every open
slot still gets a distinct reference id (realism 2.1); the others use it in `reference_mode: "tags"`: only its tags
(display, shot, camera height, lens, light type, lived-in, photo style) become words; no image is sent.

`n_image = floor(share * n_open / 100 + 0.5)` (round half up), then clamped to `<= number of open slots whose engine
takes references` and `<= usable image-capable references not used by fixed slots`.
Examples at 80%: 1 open -> 1, 2 -> 2, 3 -> 2, 4 -> 3, 5 -> 4, 8 -> 6. 0% -> 0, 100% -> all.

### B.2 Who gets one (planner proposes, code enforces)
- Planner prompt line: "Send the reference photograph as an image for exactly {n_image} of the open slots: the ones
  where a photograph says what words cannot (an unusual light such as blind stripes, dusk with a lamp or hard
  diagonal sun; a tight shot on a surface where scale and composition matter; depth through a doorway). For the
  others set `reference_mode` to `tags`." Schema: `reference_mode: "image" | "tags"`.
- `slot_planner.enforce_share(briefs, n_image)` (deterministic): need score = tight +2, light in {blind_stripes,
  dusk_lamp_mix, night_lamps, hard_diagonal_sun, rainy_day} +2, wide +1, floor/surface display +1, ties by slot.
  Too many images -> lowest scores become `tags`; too few -> highest-scoring `tags` slots become `image`. Slots on a
  text-only engine are always `tags`. Logged in the round's failures like other code fixes, never sent back to the
  planner.
- Tag text (new constant `REF_TAG_TEXT`, one sentence, positive wording, inserted where the image clause would go):
  e.g. "Photographed like a careful phone photo from counter height with a normal lens, the piece hung over furniture
  in a medium shot, in steady north light, in a lived-in room." Camera fields are still derived from the reference
  (realism 2.1), so text and fields agree.

### B.3 Persistence and UI
- Default from `config/settings.json` `planner_reference_share: 80`; Tony's slider value saved in `meta` as
  `ui.reference_share` (section G) and used by every later plan of every design.
- UI: `Reference photos for [====|--] 80% of open slots · 3 of 4` beside "Re-plan open slots" (range input, step 10,
  value shown live; saved on `change`, not on every drag tick). The "3 of 4" preview uses B.1 in JS with `pan.queue`.
- A slider change does NOT re-plan by itself (Tony controls spend and time). The plan stores
  `set_plan.controls = {share, closeness, scene_engine}`; when the current values differ the plan line says
  `made at 80% / 60; Re-plan to apply` and Generate all still uses the saved briefs Tony saw.

### B.4 Tests
Rounding table above; clamp by engine capability and by usable references; enforce_share swaps by need score;
`tags` brief prompt has no "Image 1" and contains the tag sentence; share stored in `set_plan.controls`.

---

## C. "How closely the reference influences the result" slider (loose to close)

### C.1 Honest scope
No engine offers a numeric reference weight. Nano Banana Pro / 2 take `image_input` as plain context; kie's
Midjourney (which has style/omni weights) has no API there; Flux 3 edit-image has numbered "reference roles", no
weight. So closeness is approximate and works through three levers that ARE controllable: (1) the planner's
instruction, (2) what image is sent (size and blur), (3) the exact reference-clause wording. Text-only engines
(section E) get only lever (1) through the tag text. The A/B test (C.5) is how Tony calibrates it.

### C.2 Bands (value 0-100, default `planner_reference_closeness: 60`, saved as `ui.reference_closeness`)
| Band | Values | Planner instruction (added to the planner prompt with the number) | Image sent | Derived from the reference |
|---|---|---|---|---|
| essence | 0-24 | "Study the reference and decide what is distinctive about it that suits THIS artwork (a quality of light, a type of room, a mood, a camera habit); use only that, and invent the rest freely." Returns `ref_takeaways` (1-2 of light, room_type, mood, camera, composition, materials) | long side 384-672 px, Gaussian blur | only the fields named in `ref_takeaways` (camera fields only if "camera") |
| loose | 25-49 | "Keep its camera position and overall light; choose your own composition, furniture and objects for this artwork." | long side 672-960 px, lighter blur | camera side / height / lens |
| balanced | 50-79 | "Keep its camera, composition, overall light and mood; choose your own furniture and objects to suit this artwork." | as is (the cleaned `_Blank.png`, long side <= 1568) | camera + composition (display, shot band) |
| close | 80-100 | "The scene should feel like the reference: the same kind of furniture in the same places, the same composition, camera, light and mood, built as a new room in that style. Describe the furniture types it shows; never copy individual objects, patterns or details exactly." | as is | camera + composition + light type when its tag matches |

Image prep `references.prep_for(entry, marker, flip, closeness, out_dir)` (extends realism `blank_for`): for v < 50,
long side `L = 384 + (960 - 384) * v / 50` rounded to 32, blur sigma `= (50 - v) / 50 * 0.012 * L` px; v >= 50 sends
the file as is. So **the default 60 sends exactly what the realism addendum sends** (byte-identical upload).
A no-art reference (`has_art: false`) is image-eligible only for v < 50.

### C.3 Reference clause per band (extends realism 2.2; assembled by code, placed after the opening line)
- **essence**: "Image 1 is a loose mood reference from a different room, not a picture to rebuild. Take from it only
  {takeaway words}. The camera, furniture, objects, colours and layout follow the description below. The flat colour
  block in its frame is a placeholder, not art; nothing in Image 1 is text to reproduce."
- **loose**: "Image 1 is a photograph of a different room, given only as a photography reference. Take from it the
  camera position and height, the lens and the overall light. Choose a new composition and build a completely new
  room as described below: do not copy its furniture, objects, wall colour, floor, windows or layout. The flat colour
  block in its frame is a placeholder, not art; nothing in Image 1 is text to reproduce."
- **balanced** (default 60): the realism addendum 2.2 clause, **verbatim** (with-light and without-light variants).
- **close**: "Image 1 is a photograph of a different room. Recreate its look and feel closely: the same camera
  position, height and lens, the same framing and composition, the same kind of furniture in the same places, the
  same light and mood. Build it as a new room in that style: do not copy individual objects, patterns or details
  exactly; the wall colour, the artwork's frame and the life in the room follow the description below. The flat
  colour block in its frame is a placeholder, not art; nothing in Image 1 is text to reproduce."

Lint unchanged (scene text never names camera, lens, angle, shot size or light direction). At "close" the system
prompt allows the scene to name furniture TYPES seen in the reference ("a low cane-front sideboard"); the realism
prop-family limits still apply (a close copy of a rattan-heavy reference still counts as rattan).

### C.4 Storage
Brief gains `ref_closeness` (int) and `ref_band`; `assemble_v2(b, ref)` picks the clause from `ref_band`; the prompt
in Show prompt is therefore exactly what is sent. `template.json` `brief` keeps both, so grades can be read against
closeness later. pv1 briefs never get these keys (byte-identical replay).

### C.5 A/B test (calibration; paid only on Tony's click)
- Card button (only on open slots whose engine takes references): **"A/B closeness"**. Free step: the planner
  re-plans that one slot three times with the SAME reference and engine and closeness 20 / 60 / 100 (three `claude -p`
  calls), saved in `set_plan.abtest[slot] = {reference, engine, variants: {"20": brief, "60": brief, "100": brief}}`.
- A strip under the card shows the three prompts (Show prompt panes) and one button **"Generate 3 variants · about
  54 credits"** (3 x the slot engine's price; Nano Banana Pro = 18 each). It runs through the Generate-all batch runner
  (section F) with `place: false`: each variant is generated, built, rendered, scanned; the render goes to
  `03-Etsy Images/Archive/AB_<slot>_<value>_<stamp>.jpg`; each template is saved as usual with `brief.ab = {slot,
  value}`.
- Per variant: grade select (realism 7), **"Put in slot 16"** (free: copies the render into the slot as pending) and
  **"Make 60 the default"** (sets `ui.reference_closeness`). Nothing is approved automatically.
- Proposed first run: Book Club Cat slot 16 on Nano Banana Pro (it was graded C; it is a library template now, so
  the test re-plans it as an open slot through the realism addendum's `--replan` route).

### C.6 Tests
Band edges (24/25, 49/50, 79/80); prep sizes and blur sigma; v >= 50 returns the source bytes unchanged; essence
derives only takeaway fields; balanced clause == realism clause (sha1); close clause contains "do not copy individual
objects"; A/B route plans 3 variants with the same reference and spends nothing; Generate 3 variants uses the batch
runner with `place: false`.

---

## D. Build art: six-engine pull-down (Ideas > idea bank > Build art)

### D.1 Engines, Tony's order (verified 2026-11-20 against live catalogs; "verified" = id + params + price read from
the provider; "tested" = a real generation succeeded, set only by D.5)

| # | Label | Provider / model id | Art params (2:3) | Price per art image | Refs (for rooms, E) | Flags |
|---|---|---|---|---|---|---|
| 1 | GPT Image 2.6 (default) | kie `gpt-image-2-6/flare-text-to-image` | `aspect_ratio: "2:3"`, `resolution: "1K"`, `quality: "high"`, `output_format: "png"` | **token-billed**: 900 cr / 1M text-in tokens, 5,400 cr / 1M image-out tokens (kie page; "10% below official"). Estimate 9 cr (medium) to 34 cr (high) per 2:3 1K, assuming 1,584 / 6,240 output tokens as for earlier GPT image models | text-to-image takes none; `flare-image-to-image` takes `input_urls` (up to 16) but EDITS them -> rooms text-only | id + params verified (kie.ai/gpt-image-2-6); **price per image UNVERIFIED** until measured |
| 2 | Ideogram 3 | kie `ideogram/v3-text-to-image` | no 2:3 offered: `image_size: "portrait_4_3"` (3:4), `rendering_speed: "QUALITY"`, `style: "AUTO"`, `expand_prompt: false`; output WebP | 10 cr ($0.05) QUALITY (BALANCED 7, TURBO 3.5) | none on kie (fal's Ideogram v3 takes style-only `image_urls`; not used) | verified (docs.kie.ai + kie pricing API); 3:4 master is cover-cropped for the 2x3 file by `prints` (`subject_cut` warning already exists) |
| 3 | Recraft V4.1 | fal `fal-ai/recraft/v4.1/text-to-image`; fallback WaveSpeed `recraft-ai/recraft-v4.1/text-to-image` | fal: `image_size: {"width": 1024, "height": 1536}` (custom size is in the OpenAPI schema); WaveSpeed: `image_size: "3:4"` (no 2:3) | fal $0.035 (~7 cr-eq); WaveSpeed $0.04 | none | ids + price verified (fal OpenAPI + `tm fal-search`, `wavespeed schema`); custom-size limits UNVERIFIED. Flash ($0.007) and Pro ($0.21) exist; not listed |
| 4 | Flux 3 | fal `blackforestlabs/flux-3/text-to-image`; fallback WaveSpeed `black-forest-labs/flux-3/text-to-image` | `aspect_ratio: "2:3"`, `resolution: "1k"`, `output_format: "png"`, `enable_prompt_expansion: false` | fal $0.048 / megapixel (~$0.05, ~10 cr-eq at 1k); WaveSpeed $0.048 at 1k, $0.10 at 2k, $0.607 at 4k | fal `blackforestlabs/flux-3/edit-image`: `image_urls` up to 10, numbered "reference roles" (guide behaviour UNVERIFIED) | verified (fal OpenAPI, WaveSpeed docs). Newest Flux offered: kie has only Flux 3 Klein (small model) and Flux 2 Pro (5 cr 1K); Flux 3 is the pick |
| 5 | Nano Banana 2 | kie `nano-banana-2` | unchanged | 8 cr 1K ($0.04); 12 at 2K | `image_input` (count UNVERIFIED) | verified price (kie pricing API) |
| 6 | Nano Banana Pro | kie `nano-banana-pro` | unchanged | 18 cr ($0.09) | `image_input` up to 8 (realism 2.3) | verified; in daily room use |

The old `gpt-image-2` entry stays in the file with `"hidden": true` so old rounds (`art_rounds.engine`, iterate rounds
that reuse `parent["engine"]`) still resolve their label; it is not shown in the pull-down.

### D.2 `config/engines.json` v2 (schema)
```json
{"version": 2, "default": "gpt-image-2-6", "usd_per_credit": 0.005, "aspect_ratio": "2:3", "resolution": "1K",
 "engines": [
  {"id": "gpt-image-2-6", "label": "GPT Image 2.6", "provider": "kie", "env_key": "KIE_API_KEY", "order": 1,
   "price": {"unit": "tokens", "credits_per_m_text_in": 900, "credits_per_m_image_out": 5400,
             "estimate_credits": {"art": 34, "room": 17}, "upper_credits": {"art": 34, "room": 67}},
   "uses": {"art":  {"model": "gpt-image-2-6/flare-text-to-image", "params": {"quality": "high", "output_format": "png"},
                     "aspect_param": "aspect_ratio", "res_param": "resolution"},
            "room": {"model": "gpt-image-2-6/flare-text-to-image", "params": {"quality": "medium", "output_format": "png"},
                     "resolution": "2K", "ref_kind": null}},
   "verified": "2026-11-20", "tested": null},
  {"id": "flux-3", "label": "Flux 3", "provider": "fal", "env_key": "FAL_AI_API_KEY", "order": 4,
   "price": {"unit": "megapixel", "usd_per_mp": 0.048},
   "uses": {"art":  {"model": "blackforestlabs/flux-3/text-to-image", "params": {"resolution": "1k", "output_format": "png",
                     "enable_prompt_expansion": false}},
            "room": {"provider": "wavespeed", "env_key": "WAVESPEED_API_KEY", "model": "black-forest-labs/flux-3/text-to-image",
                     "params": {"resolution": "2k", "output_format": "png"}, "price": {"unit": "image", "usd": 0.10},
                     "ref_model": {"provider": "fal", "model": "blackforestlabs/flux-3/edit-image", "ref_param": "image_urls", "max_refs": 10},
                     "ref_kind": "guide_unverified"}},
   "fallback": {"provider": "wavespeed", "env_key": "WAVESPEED_API_KEY", "model": "black-forest-labs/flux-3/text-to-image"},
   "verified": "2026-11-20", "tested": null},
  {"id": "nano-banana-pro", "scene_id": "nbpro", "...": "unchanged fields + uses.room.ref_kind = guide"},
  {"id": "gpt-image-2", "hidden": true, "...": "unchanged"}
 ]}
```
`aspect_map` per engine where the provider has no ratio string (Ideogram `{"2:3": "portrait_4_3", "4:3":
"landscape_4_3"}`, Recraft fal `{"2:3": {"width": 1024, "height": 1536}, "4:3": {"width": 2048, "height": 1536}}`,
Recraft WaveSpeed `{"2:3": "3:4", "4:3": "4:3"}`). `scene_id` links an engines.json id to a `kie_edit.MODELS` short id.

### D.3 Adapters (`app/engines.py`, existing file; one class per provider, same interface)
```
class Adapter:                           # KieAdapter (existing, extended), FalAdapter, WaveSpeedAdapter
    balance() -> {"amount": float | None, "unit": "credits" | "usd"}   # kie: /api/v1/chat/credit; WaveSpeed: GET
                                         # /api/v3/balance (endpoint UNVERIFIED -> None on error); fal: None (no balance API)
    credits() -> float                   # kie only, kept for old callers
    submit(prompt, aspect_ratio, resolution, refs=(), use="art") -> task id
    wait(task_id) -> result url          # poll; plain EngineError reasons
    download(url, path) -> Path          # always saved as PNG (WebP / JPEG converted with Pillow, lossless)
    generate(prompt, out_path, aspect_ratio="2:3", resolution="1K", on_task=None, refs=(), use="art")
        -> {"task_id", "path", "provider", "model", "credits": float | None, "usd": float | None, "measured": bool}
```
- **kie**: unchanged createTask / recordInfo; `submit` builds `input` from `uses[use].params` + mapped aspect; for
  the three existing ids the JSON body is byte-identical to today (golden test). Cost = balance difference (measured).
- **fal** (queue API): `POST https://queue.fal.run/{model}` header `Authorization: Key <FAL_AI_API_KEY>` -> `request_id`,
  `status_url`, `response_url`; poll `status_url` (IN_QUEUE / IN_PROGRESS / COMPLETED); `GET response_url` ->
  `images[0].url`. Refs as data URIs (Flux 3 accepts them; no upload). Cost = price table (fal has no balance API),
  `measured: false`.
- **WaveSpeed**: `POST https://api.wavespeed.ai/api/v3/{model}` header `Authorization: Bearer <WAVESPEED_API_KEY>` ->
  `data.id`; poll `GET /api/v3/predictions/{id}/result` until `data.status` is `completed` (`outputs[0]`) or one of
  `failed / cancelled / timeout / deleted`. Cost = price table.
- **No blind resubmit** (WaveSpeed's docs warn a retry after an unclear failure can bill twice): a submit is retried
  only when the provider clearly refused it with no task id. Fallback provider (Recraft, Flux 3) only when the primary
  refused at submit (nothing billed) and the fallback price <= the shown price.
- Keys: `engines.secret()` as today; values never logged. `ready` = key present.
- `adapter_for(engine_id, settings, use="art")` returns the class by `provider` (per-use override for Flux 3 rooms).

### D.4 Price label and cost checks
- `list_engines()` adds `price_label`: kie fixed `"10 cr ($0.05)"`; token engines `"≈34 cr est. ($0.17)"` until
  `data/engine_status.json` has measured values, then `"31 cr measured ($0.16)"` (mean of the last 5);
  fal / WaveSpeed `"$0.035 (≈7 cr) · fal"`. The pull-down (`index.html:673`) shows label + price + tested date or
  "not tested yet"; the cost line under it multiplies by images per round (4).
- `art._run`: the up-front check uses the engine's estimate (upper bound for token engines) and compares only when
  `balance()` returns a number in the same unit; fal skips the check (no balance API) and says so on the round.
  Round `credits_spent` = measured kie difference, else price-table credits-equivalent ($ / 0.005), marked "est.".

### D.5 One cheap test per engine (only on Tony's go)
`python -m app.engines --test gpt-image-2-6,ideogram-3,recraft-4-1,flux-3 --use art` prints the planned cost and does
nothing without `--yes` (a Portal button is not needed for a one-off). One 2:3 1K image each with a neutral prompt
(no design), saved in the scratchpad, result written to `data/engine_status.json` (`art.tested`, measured cost,
seconds, output size). Upper-bound cost: 34 + 10 + 7 + 10 = **about 61 credits-equivalent (~$0.31)**, of which kie
44 credits, fal ~$0.085. Nano Banana 2 / Pro are not re-tested (in use).

### D.6 Tests
Mocked HTTP for each provider: request JSON per engine and use (golden for the 3 existing kie ids), aspect mapping,
poll states incl. every WaveSpeed terminal failure, fal COMPLETED path, WebP -> PNG, no resubmit after an unclear
failure, fallback only on clear refusal; hidden engine resolves but is not listed; default is `gpt-image-2-6`; price
labels; art round with a fal engine skips the balance check and records est. cost.

---

## E. Engine picker for room scenes (Production tab)

### E.1 Where it lives
- **Panel default**: `Scene engine [Nano Banana Pro · 18 cr ($0.09) · takes reference photos ▾]` in the plan line,
  beside the share slider and Re-plan. Saved as `ui.scene_engine` (section G); replaces reading
  `room_scene_engine` directly (the setting stays as the fallback default; `"nbpro"` and engines.json ids both accepted,
  normalised by `scene_templates.scene_engine_id()`).
- **Per-card override**: a small select in each open card's footer next to the cost line, first option `Panel default
  (Nano Banana Pro)`. Saved in the listing record at `production.slot_engines[<slot>]` (outside `production.slots`,
  which `run_slot` replaces). Route `POST /api/production/{id}/slots/{slot}/engine {engine | null}`.
- Repaint safety: `paintPanel` defers while a `<select>` inside the panel has focus (repaint on `blur`).

### E.2 Cost per scene per engine (4:3, ~2K)
| Engine | Room request | Est. per scene | Reference photo |
|---|---|---|---|
| Nano Banana Pro | kie `nano-banana-pro`, 2K (today's call, unchanged) | 18 cr (verified) | yes (`image_input`) |
| Nano Banana 2 | kie `nano-banana-2`, 2K | 12 cr (verified) | yes (`image_input`) |
| GPT Image 2.6 | kie flare t2i, 2K, quality medium | ≈17 cr est., upper 67 (UNVERIFIED, token-billed) | no: image-to-image would edit the reference |
| Ideogram 3 | kie, `landscape_4_3`, QUALITY, `negative_prompt` "text, lettering, logo, watermark, people, pets" | 10 cr | no |
| Recraft V4.1 | fal, 2048x1536 custom (fallback `landscape_4_3` + upscale) | $0.035 (≈7 cr) | no |
| Flux 3 | WaveSpeed 2k text-only; fal `edit-image` 2k when a reference is sent | $0.10 (≈20 cr) text-only; ≈$0.15 (≈30 cr) with reference | only after its gate sets `ref_ok` (E.4) |

- Capability comes from engines.json `uses.room.ref_kind` (`guide` / `guide_unverified` / null). This replaces the
  realism addendum's hard-coded `REF_ENGINES`. A slot on a text-only engine is planned `reference_mode: "tags"`
  (counted by B.1) and its card note says "reference used as words (engine takes no photo)".
- The prompt is the same text for every engine (so Tony's grades compare engines, not prompts); only API parameters
  differ (Ideogram `negative_prompt`, prompt expansion off for Ideogram and Flux). The prompt is assembled at
  generation for the slot's current engine (`assemble(brief, ref=engine_takes_ref and mode == "image")`, free,
  deterministic) and Show prompt shows that same text.
- Scenes narrower than `scene_min_width` (2000 px; Ideogram and Recraft fallbacks are about 1 MP) are upscaled 2x
  with the existing local Upscayl (`upscayl_bin`, free) before `build_psd`, because every builder threshold was tuned on
  2400 px scenes.

### E.3 Plumbing
- `scene_templates.generate_scene(prompt, out_png, settings, generator, ref_imgs=(), engine=None)`: engine resolved
  per slot by the caller; if the engine has a `scene_id` in `kie_edit.MODELS` the call is exactly today's
  `gen(scene_id, out, prompt, aspect, res[, ref_imgs])` (byte-identical for nbpro); otherwise
  `engines.adapter_for(engine, settings, use="room").generate(..., refs=ref_imgs)` and the result is mapped to
  kie_edit's dict shape (`out, model, task, s, credits, left`) plus `usd`, `provider`, `measured`.
- `production._engine(settings)` becomes `scene_engine(con, settings, rec, slot)` -> `{id, label, credits_per_scene,
  usd_per_scene, takes_ref, gate}`; `_next_source` and `queue_of` use the slot's engine; `SCENE_CREDITS` is derived
  from engines.json (`nbpro` still 18).
- `run_slot(..., engine=None)` takes the slot's engine; `template.json` keeps `"engine"` (the scene_id for kie Nano,
  e.g. `"nbpro"`, so old and new templates match) and adds `"engine_id"`, `"engine_provider"`, `"engine_model"`,
  `"usd"`, `"cost_measured"`; the brief in template.json gets `engine` too.
- Grades per engine: `grades` (realism 7) aggregated by `engine_id`; the engine select labels show
  `mean grade B (4 graded)` once there are grades.

### E.4 Per-engine gate (the big risk: the builder was tuned on Nano output)
SAM insert detection, the orange / blue flat marker, despill, `art_area_gate`, guard and the output scan all assume a
flat, evenly lit, marker-coloured insert inside a crisp frame. Other engines may paint the insert as a picture or
textured paper, tint it, ignore "orange", or draw soft frames. State per engine in `data/engine_status.json`:
`room.gate = untested | passed_1 | trusted | suspect | failed`, `room.ref_ok` (bool), `room.scenes[]`.

- **Free pre-check (stand-in, before any paid scene)**: request-shape test with mocked HTTP, plus the existing G0
  stand-in run on 3 Nano scenes downscaled to the engine's native size and upscaled back (proves the upscale path does
  not break SAM or the checker at 1 MP). No model output can be faked for free, so the real check is the first scene.
- **First-real-scene check** (runs inside `run_slot` after `build_psd`, free): insert found; insert colour within dE76
  < 20 of `MARKER_RGB[marker]` and texture std below `INSERT_TEXTURE_MAX`; aspect 4:3 within 2%; guard + art-area
  gate + output scan pass. All pass -> `passed_1`; two real scenes pass -> `trusted`.
- **Fail**: existing behaviour (scene kept in `03-Etsy Images/Archive/` with the reason; attempt logged) plus a plain
  card reason ("Flux 3 painted the blank insert as a picture; the insert is not flat") and a button **"Try on Nano
  Banana Pro · 18 credits"** (paid, Tony's click; never automatic). One fail -> `suspect`; two -> `failed` (engine
  stays selectable, label says "failed the room check twice").
- **Generate all** (F) only uses engines at `passed_1` or `trusted`; an untested / failed engine on a slot is listed
  as "generate one by hand first" and skipped. Single-card Generate is always allowed (one click, shown cost).
- **References on Flux 3** are sent only after `ref_ok` is set: Tony grades one A/B variant set on Flux 3 and says it
  used the reference as a guide (did not edit it); until then Flux 3 rooms are text-only.

### E.5 Tests
Engine resolution order (card override > `ui.scene_engine` > setting); `"nbpro"` and `"nano-banana-pro"` equivalent;
nbpro path calls the stub generator with exactly today's arguments; non-kie engine goes through the adapter with
mapped aspect and resolution; text-only engine forces `tags` mode and no `ref_imgs`; small scene upscaled before build;
gate state transitions; Generate-all skips untested engines; template.json engine fields.

---

## F. "Generate all open slots" button

### F.1 Flow
1. Button in the plan line: **`Generate all open slots · ≈56 credits`** (disabled while a job, a batch, planning or a
   reference refresh runs, when no slot is open, or when the plan status is `failed` / `planning` / stale).
2. Click -> `GET /api/production/{id}/generate-all` returns the estimate; a confirm box lists, in run order (library
   first, then slot order, from `queue_of`):
   `16 · library template X · free` / `17 · new · Nano Banana Pro · reference 0031 (image) · 18 cr` /
   `18 · new · Flux 3 · reference 0024 (words) · ≈20 cr ($0.10, fal/WaveSpeed)` / skipped rows with reasons
   (lint failed, engine not through its room check, no room folder).
   Totals per engine and overall in credits-equivalent ($ / 0.005) and dollars, the kie balance, and the cap
   (`ui.generate_all_cap`, default `generate_all_cap_credits: 120`, editable in the box). One **Confirm** button.
3. `POST /api/production/{id}/generate-all {key, cap}`: `key` = sha1 of the estimate rows; a different key (the plan,
   engines or slots changed since Tony looked) -> 422 "the plan changed; check the new total". Never more than shown.
4. Worker `production.run_batch(con, settings, idea_id, rows, cap, generator)` runs one slot at a time through the
   same single job lock (`start_slot(..., by_batch=True)` then `run_slot` in the same thread).

### F.2 Rules
- **Skips**: approved / pending-decision slots (not open), fixed slots, a slot whose brief fails lint, a slot whose
  engine is not `passed_1` / `trusted`, a slot already running.
- **Budget**: before each paid slot, stop if `spent + row.upper > min(cap, shown_total)` (token engines use their
  upper bound until measured) or if the kie balance < the row's estimate. Spent = measured kie difference, else the
  price table. This is how it never spends beyond the shown estimate.
- **Hard failure stops the run** (the rest would fail the same way): key missing, auth refused, balance too low, the
  provider refusing jobs for non-content reasons, two network timeouts in a row. Remaining rows -> `skipped: stopped
  after slot 17 (kie.ai balance too low)`.
- **Slot failure does not stop it**: no clean insert, gate / guard fail, hard output-scan finding, content refusal
  (with the realism addendum's one free text-only retry when the refusal cost nothing). Listed at the end.
- **Cancel**: `POST /api/production/generate-all/cancel` sets a flag checked between slots; the running slot finishes
  (a submitted kie / fal / WaveSpeed job cannot be un-billed); header says "Stopping after slot 17…".
- **Never auto-approves**: images land as pending exactly like a card click; flagged ones go to Archive with reasons.
- **Interactions**: uses the saved briefs Tony saw (Show prompt), the slot engines (E), the reference mode and
  closeness stored in each brief (B, C); slider changes after the plan apply only after Re-plan (B.3); output scan
  per slot (realism 6); the planner's library-first swap already decided which slots are free.

### F.3 State, progress, end report
- Module state `_batch = {running, idea_id, rows[{slot, status: waiting|running|done|flagged|failed|skipped, engine,
  est, spent, why}], spent, cap, total, cancel, started, finished, stop_reason}`; `start_slot` refuses card clicks while
  `_batch["running"]` ("Generate all is running").
- `run_slot` is refactored to RETURN an outcome `{kind: done|flagged|failed, hard: bool, credits, usd, why}` (it still
  writes the slot record exactly as today; single-card callers ignore the return value).
- Panel: `pan.batch`; each card shows `queued 3 of 4` / `making…` / `done` / `failed: <reason>`; header line
  `Generating all: 2 of 4 done · 36 of ≈56 credits used [Cancel]`. Poll `waiting` includes `batch.running`.
- End report stored in the listing record `production.batches` (last 5) and shown on the plan line:
  `Generate all finished: 3 made (1 flagged), 1 failed (slot 18: no clean blank insert, scene kept in Archive). Spent
  36 credits.` `recover()` marks a batch cut by a restart "interrupted" (no auto-resume).
- `queue_of` / `generate_queue` stay the source of the order (rows add engine, reference mode and upper cost).

### F.4 Tests
Estimate rows, order and totals per engine; key mismatch refused; cap stops before a slot that would exceed it;
token engine uses its upper bound; hard failure stops and marks the rest skipped; slot failure continues and is
listed; cancel stops after the current slot; card clicks refused during a batch; approved slots never touched
(deep-equal); no auto-approval; recover marks interrupted; A/B (`place: false`) runs through the same runner and
places nothing in slots.

---

## G. How the settings persist

| Value | Default (file, Tony edits) | Tony's live value | Scope |
|---|---|---|---|
| reference share | `planner_reference_share: 80` | `meta ui.reference_share` | all designs |
| reference closeness | `planner_reference_closeness: 60` | `meta ui.reference_closeness` | all designs |
| room engine default | `room_scene_engine: "nbpro"` | `meta ui.scene_engine` | all designs |
| room engine per slot | none | listing record `production.slot_engines` | one design |
| Generate-all cap | `generate_all_cap_credits: 120` | `meta ui.generate_all_cap` | all designs |
| art engine default | engines.json `default: "gpt-image-2-6"` | the pull-down choice per round (unchanged) | per round |
| reference refresh | `reference_dir`, `reference_lowres_max: 400`, `reference_max_side: 2048`, `reference_nano_max_credits: 30`, `reference_lama_model: "~/pinokio/api/comfy.git/app/models/inpaint/big-lama.pt"` | none | global |
| scene upscale | `scene_min_width: 2000` | none | global |
| engine state | none | `data/engine_status.json` (tests, measured costs, room gates) | global, written by code |

New small module `app/prefs.py`: `get(con, settings, key)` / `put(con, key, value)` over `meta` (`ui.` prefix, JSON
values, validated ranges: share 0-100 step 10, closeness 0-100, cap 0-1000, engine must exist). Route
`POST /api/prefs {key, value}`; `panel` returns the live values. `config/settings.json` is never written by code.

## H. Reuse of the planner's saved briefs
Nothing re-plans unless Tony clicks Re-plan, changes ticks (existing auto re-plan) or runs an A/B. New brief keys
(`reference_mode`, `ref_closeness`, `ref_band`, `ref_takeaways`, `engine`) are pv2-only; `normalise` drops them from
pv1. Generate all, single-card Generate and the A/B runner all read `brief_for(rec, slot)`; the engine and the prompt
for that engine are resolved at run time (free); `set_plan.controls` records the slider values used for the plan.

---

## I. Tests overall and golden locks
1. **Golden first** (before any change): sha1 of the kie request bodies for the three existing art engines and for
   `kie_edit.generate("nbpro", ...)`; realism goldens (pv1 slot 16 / 19 prompts, V1/V2 look hashes, marker hashes)
   stay green; pv2 at closeness 60 and `reference_mode: image` == the realism addendum's `assemble` output.
2. Unit tests per section (A.7, B.4, C.6, D.6, E.5, F.4) with injected HTTP, vision, SAM, LaMa, OCR and generators.
3. Free dry runs: `python -m app.references --refresh --dry-run` on the real folder (reports, writes nothing);
   `python -m app.slot_planner --idea 3 --dry-run --replan 16,17,18,19` with share 80 / closeness 60; Generate-all
   estimate for Book Club Cat (GET only).
4. Browser smoke on 8800: share and closeness sliders save and survive reload; engine selects survive a repaint; the
   Refresh progress and result list; Generate-all confirm box numbers equal the estimate; Cancel; A/B strip.
5. Paid steps, each only on Tony's go: D.5 engine tests (~61 cr-eq), first room scene per new engine (its listed
   price), A/B closeness (~54 cr on Nano Banana Pro), Nano fill in the refresh (6 cr each, cap 30).

## J. Ordered build steps (one final commit)
1. Golden locks (I.1).
2. engines.json v2 + `engines.py` adapters (kie extended, fal, WaveSpeed), price labels, `data/engine_status.json`,
   `--test` CLI (no `--yes` run). Tests D.6.
3. Build art pull-down: `art.options`, `art._run` cost check, `index.html` label; default GPT Image 2.6. Tests.
4. `app/prefs.py` + `/api/prefs`; panel returns live values.
5. Room engine plumbing (E.3), per-slot override, upscale step, gate state, template.json fields. Tests E.5.
6. Reference Refresh (A): normalise, low-res, rename, overlays, LaMa script mode, blank, register, job, routes, UI.
   Tests A.7. Run it for real on the folder (free: SAM, Gemini flash-lite, `claude -p`), report the result list.
7. Planner: `registers_ok`, `reference_mode`, `enforce_share`, closeness bands, `prep_for`, clauses, tag text,
   `set_plan.controls`. Tests B.4, C.6.
8. Generate all (F): estimate, key, batch runner, `run_slot` outcome, cancel, recover, UI. Tests F.4.
9. A/B closeness (C.5) on the batch runner.
10. Browser smoke; restart the Portal (`uv run --no-project --with-requirements requirements.txt uvicorn app.main:app
    --port 8800`).
11. Free dry runs (I.3) and a build report for Tony.
12. Docs: status lines in both earlier plan files, `Cleanup_Log.md` refresh section, `TOOLBOX.md` (fal + WaveSpeed
    adapters in the Portal, reference Refresh, LaMa script mode), `Directory.md` if it lists Portal modules.
13. One commit (code, tests, docs, manifest and `_Blank` files from step 6).
14. Paid steps only on Tony's go (I.5).

## K. Risks
| Risk | Mitigation |
|---|---|
| GPT Image 2.6 is token-billed; a 2K room could cost far more than the estimate | upper bound used for caps until measured; measured mean replaces the label after the first image; rooms use quality medium; the economy model (5 cr flat 1K) exists if it is too dear |
| Non-Nano engines break the template builder (insert painted, tinted, soft frame) | per-engine gate (E.4), Generate all only on passed engines, scenes kept in Archive with reasons, one-click Nano retry only on Tony's click |
| Ideogram is strong at lettering and may put text in rooms | `negative_prompt` for rooms; output scan (realism 6) catches it |
| Recraft / Ideogram scenes are ~1 MP | local Upscayl to >= 2000 px before the build; checker thresholds watched on the first scenes |
| Closeness is approximate (no weights anywhere) | three real levers (instruction, image prep, clause); A/B test to calibrate; stated on the slider tooltip "approximate" |
| Close band copies objects from the reference | clause forbids copying individual objects; prop-family limits; distinct references per slot; grades per reference push bad ones down |
| LaMa smears a view or window during refresh | confidence check, never silently accepted, Tony's eye or a 6-credit Nano fill on his click |
| A batch spends while Tony is away | confirm with the exact total, key check, cap, hard-failure stop, cancel; one slot at a time |
| fal has no balance API | price-table cost, shown as "est."; Generate-all cap still applies |
| WaveSpeed retry could bill twice | no blind resubmit; fallback only on a clear refusal at submit |
| Old art rounds reference `gpt-image-2` | kept as a hidden engine entry |
| Real-home photos carry GPS EXIF | PNG re-save drops EXIF before any upload |

## L. Open questions for Tony
1. **Go for the engine test round?** One art image each on GPT Image 2.6, Ideogram 3, Recraft V4.1 and Flux 3: about
   61 credits-equivalent at most (~$0.31: 44 kie credits + ~$0.085 on fal). Room checks per engine come later, one
   card click each, price shown on the card.
2. **Generate-all cap**: default 120 credits per run (about 6 Nano Banana Pro scenes). Keep it, or another number? (It
   stays editable in the confirm box either way.)

Sources checked 2026-11-20: kie.ai pricing API (`/client/v1/model-pricing/page`), kie.ai/gpt-image-2-6,
docs.kie.ai/market/ideogram/v3-text-to-image, kie.ai/flux-2, fal OpenAPI schemas
(`fal.ai/api/openapi/queue/openapi.json?endpoint_id=...`) and `tm fal-search --pricing`, `wavespeed models` /
`wavespeed schema`, wavespeed.ai docs for `black-forest-labs/flux-3/text-to-image`.
