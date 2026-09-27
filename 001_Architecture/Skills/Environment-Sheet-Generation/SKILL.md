---
name: environment-sheet-generation
description: Use whenever a video production has a location that appears in more than one scene and needs to look identical every time — "build an environment sheet", "location reference sheet", "make a sheet for the burrow/reef/palace", or any pipeline step generating shots set in the same recurring location across multiple scenes. Generates one people/creature-less panel per scene set there via GPT-Image-2 — never one generic room shot.
---

# Environment/Location Sheet Generation

Generates a single reference-sheet image locking a recurring location's appearance — but structured per-scene, not per-location-in-general. One sheet per location, with exactly one panel for each scene that happens there.

Production-proven origin: generalizes `environment_sheet_generation.py` from `Reimagined_Realms_POV_Shorts_Pipeline_v2` (v2 revision, built after two confirmed real failures — see below). Applies to any channel with a recurring setting, not just POV human productions — e.g. Anomalous Wild's reef burrow, palace throne room, whatever recurs across a production's scenes.

## Before using this skill

Read [`GPT-Image-2-Prompting-Guide`](../GPT-Image-2-Prompting-Guide/SKILL.md) first for the underlying model's prompting conventions.

## Architectural Plausibility Check — mandatory before generating any built/constructed location (locked 2026-09-19)

Confirmed real, repeated failure (Neon Parcel Test Shot 03): a doorbell-cam
environment plate was generated straight from a text description with no
architectural grounding, and produced a real construction-logic defect — a
staircase offset from the door with a mismatched second patio level. That
got caught and "fixed" once, but the fix itself was still ungrounded and
produced a *new* defect the exact same way: a 10+ step monumental staircase
on a normal single-story house, an implausible step count nobody checked
against the building's actual height. Two different defects, same root
cause: geometry was generated first and checked for plausibility only after
the fact, by eye, on a finished image — exactly backwards.

**The fix, mandatory for any location involving a real constructed
structure (stairs, doorways, rooms, load-bearing geometry — not open
natural landscapes):**

1. **Invoke [`Production-Research-Agent`](../Production-Research-Agent/SKILL.md)'s
   Step 2 (reference images) before writing any plan — mandatory, not
   optional (locked 2026-09-19).** This skill already exists and already
   does exactly this for every other channel (Anomalous Wild pulls real
   animal reference photos before generating a creature illustration,
   Reimagined Realms pulls real location photos) — environment sheets for a
   built/constructed location were the one place this was being skipped,
   with generation attempted straight from imagination instead. Fix: query
   for reference photos **tailored to the specific environment this
   production actually needs** — not a generic "house" search, but the
   real specific type (e.g. "single-story regional Australian house front
   porch and steps," "raised bearer-and-joist floor entry stairs"), the way
   Anomalous Wild's research is tailored to the specific creature/subject
   in that production, not "animal" in general. Save the results to
   `Research/Reference_Images/` per that skill's existing convention (capped
   at 20, grounding only, never composited into the final output). Street
   View or a sourced real-world construction fact/standard are acceptable
   fallbacks **only** when Production-Research-Agent's own image search
   doesn't surface the specific detail needed — state that explicitly when
   it happens, never silently skip straight to guessing.
2. **Write the site plan as text before any image is generated** — explicit
   dimensions/counts where they matter (step count, not just "some
   steps"), and the actual walkable path a person would use, described as
   a real route (door → landing → stairs → path → driveway, or whatever
   the location's real equivalent is) — not just a list of disconnected
   set-dressing elements.
3. **Run an explicit plausibility check against that written plan, not
   against a generated image** — does the step count match the building's
   real height, is there one continuous walkable path with no gaps or
   illogical jumps, does any set-dressing element block that path, is the
   layout centered/aligned the way a real structure would actually be
   built. Record this check in the production's `Data/` folder before
   generating anything.
4. **Only after the plan passes that check, generate images in this exact
   order — mandatory, no exceptions (locked 2026-09-19, restated after
   repeated real violations of this same rule):**

   1. **Top-down / bird's-eye plan view — generated first, always.** This
      is the **single source of truth** for the location's entire
      geometry. Every position, depth, and orientation fact gets fixed
      here first.
   2. **Front/reverse elevation view — generated second, chained from and
      checked against the top-down.** Never generated independently of
      it, never generated before it.
   3. **Photorealistic camera-reference panel (the POV) — generated
      last, chained from and checked against both prior panels.**

   **Real, repeated failure this restates, explicitly, to close it for
   good:** on this exact production, the photoreal POV panel was
   generated *first*, then treated as "ground truth" to measure and
   derive the top-down and reverse-view diagrams from — the precise
   inverse of this rule. It felt reasonable in the moment ("the POV has
   real pixels I can measure, the diagrams don't exist yet") and was
   still wrong: a photograph never encodes depth, object extent, or
   facing/orientation as checkable facts, only left/right position by
   rough visual impression — which is exactly why water tank/clothesline
   depth, hedge extent, and car orientation all drifted wrong across
   multiple attempts before this was caught. **The top-down plan view is
   the only panel allowed to be generated without another panel to check
   against. Every other panel is generated FROM it, never the reverse,
   with no exception for "I'll generate the photo first since it's more
   grounded."**

## Depth, not just left/right — every position check needs two axes (locked 2026-09-19)

Real, repeated failure: every spatial check built on this production
before this point (including a purpose-built detection tool) only ever
compared **which side of frame** something was on (left vs. right/x-axis).
Real defects that check never could have caught, because they live on the
other axis entirely: the water tank and clothesline were on the *correct*
side but positioned too close to the house instead of near the street
(a **depth/y-axis** error — how far from the camera/house toward the
road), and a hedge that reached the correct side of frame but stopped
short of the property's actual edge (an **extent** error, not a point
position at all).

**Every spatial fact about a location must specify a full 2D position, not
just a side:**
- **x (left/right):** which side of frame, as already established.
- **y (depth):** how far from the house/camera toward the street/road —
  stated explicitly (e.g. "near the house," "mid-yard," "near the street/
  road edge"), never left implicit.
- **Extent, for line/area elements (hedges, fences, the lawn itself):** a
  start point AND an end point, or an explicit "reaches the property edge"
  statement — never just one position with an assumed length.
- **Orientation, for any directional object (a parked car, a person, an
  animal facing a direction):** which way it faces, stated explicitly and
  checked as its own fact, completely separate from where its center
  point is. A car's position can be perfectly correct while its facing
  direction is backwards — these are independent facts and must be
  checked independently.

When using `check_landmark_positions.py` (or any manual coordinate check),
compare **both** `x_center_frac` and `y_center_frac` between images, not
x alone — and check extent/orientation facts by their own explicit
statement in the site plan, since a center-point coordinate check cannot
represent either one.

This check is about the location's *built structure*, not its dressing —
open landscape, foliage placement style, or lighting mood don't need this
level of rigor, but anything a real person would need to physically walk
through, climb, or pass through does.

## Techniques confirmed working, locked 2026-09-19 (Neon Parcel Test Shot 03 environment sheet)

After multiple failed attempts on the same shot (wrong orientation twice,
landmark depth wrong twice, lawn geometry distorted, car direction flipped
back and forth), these specific fixes are what actually closed each gap —
lock them in as standard practice, not shot-specific workarounds:

1. **Describe orientation by literal visible parts, never by shorthand
   jargon.** "Backed in" got misread/miscommunicated repeatedly across
   both directions. "The car's FRONT BUMPER, HEADLIGHTS, AND WINDSHIELD
   face X; the REAR BUMPER AND TAIL LIGHTS face Y" is unambiguous because
   it names concrete, unmistakable features instead of a compressed term
   that depends on shared assumptions about what it means.

2. **Annotate the orientation directly onto the top-down source-of-truth
   image** — a deterministic PIL overlay (arrow + label, e.g. "CAR FRONT
   (faces house)" / "CAR REAR (faces street)"), not another AI generation
   call. This turns orientation into a fixed, visible fact on the one
   panel every other panel is checked against, instead of something
   re-derived from prose each time a new panel gets prompted — which is
   exactly how it kept drifting.

3. **State relative proximity between landmarks as an explicit fact when
   they're supposed to be near each other** (e.g. "the water tank is
   positioned immediately next to the car, close together on the same
   side") — a landmark can have the "correct" side and still end up too
   far from where it actually needs to be relative to its neighbor if
   proximity isn't stated as its own requirement.

4. **Name the lens/perspective explicitly to prevent geometry distortion**
   ("shot on a standard 50mm-equivalent lens, not wide-angle, to keep
   perspective distortion minimal") plus an explicit negative constraint
   on the specific failure mode observed ("lawn strips must NOT narrow
   into a triangle/wedge shape at either end — clean rectangles of
   consistent width, matching the top-down"). Generic "match the
   reference exactly" was not enough; naming the actual defect shape by
   name in the prompt is what fixed it.

5. **Generate photorealistic panels without baked-in labels, chained from
   the top-down as a real image reference with "interpret positions from
   the attached diagram" framing** — add labels afterward as a separate
   deterministic step (PIL text + leader lines), not in the same
   generation call. Asking one call to nail real-world photographic
   geometry *and* correct text placement simultaneously is asking for two
   hard problems at once; splitting them made the geometry noticeably
   more reliable.

## Why one panel per scene, never a single generic shot (the failures this fixes)

The original v1 approach — one shared reference image per location — failed twice on a real production:

1. **Merging two scenes into one shared panel silently dropped an action.** A door-push scene got skipped entirely when merged with the "already inside" scene next to it — the panel showed the aftermath, not the actual physical moment.
2. **A panel meant to be an empty room reference had crowd figures and hands creep in**, even though nothing in the prompt asked for people.

Both are fixed by structuring the sheet as **one panel per scene**, never merged or reused, with people/creatures explicitly excluded by default.

## "One panel per scene" means per distinct camera setup, not per storyboard frame (real failure, logged 2026-09-17)

Confirmed real failure (Neon Parcel): a 6-frame storyboard was one continuous
handheld take (a single camera reacting mid-shot, not six different camera
setups), but the environment sheet was built with one panel per storyboard
frame anyway — producing a fabricated walking-POV progression that got
steadily closer to the truck, frame by frame. Nothing in the actual shot
corresponds to that progression; it doesn't exist. "One panel per scene"
means one panel per genuinely distinct camera position/setup the production
actually uses — for a single continuous shot, that's often just 1-3 wide
establishing angles covering the real spatial layout, never a mechanical
1:1 mapping to however many frames the storyboard happens to have.

**Also ground the environment sheet in whatever's already been approved.**
The same failure also produced a location that looked nothing like the
already-approved storyboard, because the sheet was generated from text alone
with no reference to what had already been established. If a storyboard or
prior sheet already exists for this location, pass it via `--input_urls` so
the environment sheet matches the real, already-locked appearance instead of
inventing a fresh one.

## Never ask the model to draw multiple angles in one generation call (real failure, logged 2026-09-18)

Confirmed real failure, tried three times before it stuck: asking GPT-Image-2
to generate several panels of the "same" location in a single call — even
with explicit per-panel descriptions, a "strict consistency" clause, and real
reference photos attached — produced mismatched geometry between panels every
time (a wall/gate post in a different position, a truck half on the
sidewalk, inconsistent lighting). GPT-Image-2 has no ControlNet-style
structural/layout conditioning — text and reference images are the only
inputs it has, and drawing multiple "panels" in one image is still one
continuous improvised canvas, not truly independent, geometrically-locked
views. **This is a real model-capability ceiling, not a prompting failure —
no amount of stricter wording fixes it.**

**What actually works:** generate each camera angle as its own separate
single-image call, and chain the references — each new angle's `--input_urls`
should be the *immediately prior generated plate*, not the original disparate
sources (a real photo, an old storyboard, etc.) re-supplied every time.
Referencing one already-correct single image is a far more tractable task for
the model than reconciling several loose references into new panels from
scratch. Composite the separately-generated, individually-consistent plates
into one sheet afterward with a deterministic layout tool (Pillow/PIL grid
compositing, matching this workspace's white-caption-band convention) — never
another AI generation call for the layout step itself.

**Also: derive which angles are actually needed from the shot's real camera
behavior, not generic photography convention.** Defaulting to "wide shot +
reverse angle" produced a reverse angle from inside the truck bed that the
real camera (a bystander's handheld phone) would never actually be
positioned at — nothing in the shot ever cuts there. Check the production's
own blocking plan for what camera position(s) the shot actually uses, and
only generate the angles that correspond to real camera setups in that shot.

**If a generated plate has a geometry defect, drop it rather than forcing
it.** Don't keep re-prompting the same failure hoping the next attempt fixes
it blindly — if one clean plate is usable and a second attempt produced a
real defect (e.g. an object in an impossible position), proceed with what's
correct and revisit the missing angle later rather than compounding wasted
generations chasing it in the moment.

## Usage

```bash
python3 scripts/environment_sheet_generation.py <location.json> \
  --out "<production_folder>/Images/Environment_Sheets/<Location>_Sheet.png"
```

`location.json`:
```json
{
  "location": "the mantis shrimp's reef burrow",
  "scenes": [
    {"scene": 1, "description": "wide establishing shot, burrow entrance at dusk"},
    {"scene": 6, "description": "close angle at the burrow mouth, raptorial claw visible in frame"}
  ]
}
```

- One entry per scene set in this location — **never merge two scenes into one panel, even if they're similar.** A real camera never holds the exact same framing twice; each panel must show a visibly different angle, zoom, or height.
- Each panel shows the scene's actual physical action moment, not its aftermath (a door mid-push, not the already-open room beyond it).

## Rules enforced by the prompt itself

- **No people, no hands, no arms, no held objects, no animals/creatures in any panel by default** — these are pure empty-location camera references. The one exception: a location reference that's deliberately meant to include a stationary environmental creature (e.g. background reef life for an underwater establishing shot) — state that explicitly per-panel in the scene description if needed, otherwise assume none. Practice dummies/mannequins are fine, they're not people.
- Panel labels (scene number only) sit in a reserved blank margin strip beneath each panel — never overlapping the image content.
- Consistent style/lighting across every panel, as if genuinely the same physical location.
- No watermark.

## The photorealistic camera-reference panel must be rendered at the production's video aspect ratio (locked 2026-09-19)

Confirmed real requirement, Tony: the one panel meant to represent the
actual camera's real output (e.g. a doorbell-cam POV) must be generated at
**16:9** specifically — the aspect ratio the video itself will be produced
in — never a square or off-ratio crop of a larger composite sheet. This
matters because that panel is the one downstream storyboard/video prompts
treat as "what the camera actually sees" — if its own aspect ratio doesn't
match the eventual video frame, composition and framing decisions made
against it won't hold once the real video is generated at 16:9. Schematic/
diagram panels (top-down plans, reverse establishing views, labelled detail
call-outs) are not bound by this — they're spatial references, not stand-ins
for camera output, and can use whatever aspect ratio best fits their content.

## Full sheet structure: at least 4 panels, landscape overall sheet, one spatial diagram minimum (locked 2026-09-19)

Confirmed real correction, Tony: a bare 2-panel sheet (one photo, one
schematic) is not enough — it reads as thin next to a real production
environment-design page, and doesn't give a generation model or a human
reviewer enough grounding to catch geometry problems before they propagate.
**Every environment sheet needs at minimum four panels**, assembled into one
landscape-oriented sheet matching this workspace's other reference-sheet
conventions (a labeled margin strip beneath each panel, consistent overall
layout with Character/Creature sheets):

1. **The photorealistic camera-reference panel** (16:9, per the rule above).
2. **A top-down/bird's-eye site plan** — schematic, labeled with leader
   lines calling out every fixed landmark that matters for blocking: the
   door, the camera mount, the staircase, the driveway, the car, and any
   named yard set-dressing (mailbox, clothesline, water tank, hedge line,
   lawn boundary, etc.) — not just the two or three elements a first pass
   happens to think of.
3. **A reverse/alternate establishing angle** — schematic, explicitly
   labeled as a spatial reference only, not real camera output, if it
   depicts a viewpoint the actual shot's camera never uses.
4. **A landmark/detail call-out panel** — labels and isolates the specific
   recurring yard/set objects (mailbox, clothesline, water tank, etc.) that
   later prompts will need to reference by name, so their appearance is
   locked the same way a character sheet locks a recurring subject's look.

Add more panels when the location genuinely needs them (more landmarks, more
real camera setups) — four is the floor, not a ceiling.

**Build this the way the "never ask the model to draw multiple angles in one
call" section above already establishes** — each panel is its own separate
generation call, chaining the previous panel forward as the `--input_urls`
reference for the next one, never one call asked to produce all four panels
at once. Composite the finished, individually-consistent panels into one
landscape sheet afterward with a deterministic PIL/Pillow grid layout, not
another AI generation call.

## Sheet presentation template — required for every environment sheet (locked 2026-09-20, GLOBAL, Tony)

Every environment sheet is assembled from a JSON spec by `scripts/build_environment_sheet.py` (never hand-laid-out), so all sheets look the same. Worked example: `Examples/Shot_05_Vervet_Shopfront_Spec.json` (re-renders the approved Shot 05 sheet pixel-for-pixel).

```bash
python3 scripts/build_environment_sheet.py <spec.json> --base <production_folder> --out <production_folder>/Character_Sheets/Environment_Sheet_vN.png
```

Required, on every sheet:
- **Dark presentation-board look:** header bar with sheet title + headline, one bordered card per panel, numbered badge, panel title + one-line subtitle, legend strip beneath each panel.
- **Panel 1 is always the camera's view, titled `CAMERA POV` with subtitle stating it is exactly what the video frame shows** (16:9).
- **Panel titles are mandatory:** `TOP-DOWN VIEW`, `REVERSE VIEW` (subtitled "Spatial reference ONLY - NOT camera output"), `LANDMARK DETAIL`, plus any extra views the location needs (four is the floor).
- **Labels live in the side margins with leader lines to a dot on the image; they never cover an image.** Labels are added by the renderer (deterministic), never baked in by the image model; generate panels unlabeled. Leader lines must not cross (the renderer orders labels by anchor height).
- **Color coding:** orange = the shot's action points, teal = fixed set structure.
- **Optional bottom rows** (included by default on every sheet unless Tony says otherwise): MATERIALS & COLORS swatches (cropped from the panels), COLOR PALETTE (auto-sampled from the camera POV), DETAILS crops.
- Mark positions (`fx`,`fy`) are set by hand and must be checked by eye on the rendered sheet.

The generation order above (top-down first, everything chained from it) is GLOBAL, confirmed by Tony 2026-09-20. This template covers only the human-facing sheet; which images are sent to a video model is decided by each channel's own pipeline.

## Feeding the sheet forward

Pass the relevant panel (or the full sheet, cropped to the needed scene) as an input reference on any shot-generation call set in that location — see [`Seedance-Prompting-Guide`](../Seedance-Prompting-Guide/SKILL.md)'s environment reference section for both the pre-compositing approach (environment + character composited into one starting frame before Seedance runs) and the direct tagged-reference approach (environment passed as its own `@ImageN` alongside character sheets in one Seedance call).
