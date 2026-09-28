---
title: "Test Shot 03 — Architectural Site Plan (text, checked before any image generation)"
locked: 2026-09-19
---

# Grounding sources

- **Real photos:** `Real_References/Sutton_NSW_Streetview.jpg`, `heading_30.jpg`,
  `heading_300.jpg`, `heading_340.jpg` — real regional-NSW bushland-fringe
  street photos (Sutton, NSW). Confirmed real: brick-veneer single-story
  construction, red corrugated-iron roofing, open sloped grassy blocks with
  minimal fencing at the front, consistent with what this shot already
  depicts. **Honest limitation:** none of these captures a clean, close
  front-porch/staircase view — Street View at this location didn't happen to
  frame one. Not used for exact step count.
- **Step count/porch height:** grounded in real Australian residential
  construction standard instead, not a photo. A single-story home on a
  raised bearer-and-joist floor (common on sloped/rural AU blocks, which
  this bushland-fringe setting plausibly is) typically has a floor height of
  roughly 450-900mm above ground, with standard domestic step rise around
  150-190mm per step — meaning a real front entry here would need
  **roughly 3-5 steps**, not the 10+ step run generated previously. Tony's
  correction ("4 to 5 steps") matches this real standard.
- **Real photo confirmation (2026-09-19, via Production-Research-Agent's
  reference-image step, Openverse search):**
  `Research/Reference_Images/Queenslander_Front_Steps_01.jpg` — a real
  historic photo of a Queenslander-style raised weatherboard house on
  stumps, with a short, modest front stair run (well under 10 steps)
  leading to a side porch landing. Directly confirms the 3-5 step estimate
  above against a real photographed structure, not construction-standard
  math alone. Two other Openverse results
  (`Queenslander_Railway_Complex_02.jpg`, `AU_House_Front_Porch_03.jpg`)
  were searched but not useful for this specific detail — see
  `Research/Reference_Images/SOURCE.md` for the honest breakdown. None of
  the three shows a clean driveway-to-entry walkway; that detail remains
  grounded in Tony's own directly pasted real-house examples described
  below.

# Site plan (text, walkable-path logic checked before any diagram exists)

- **House:** single-story, brick-veneer/weatherboard, red/dark corrugated-
  iron roof, raised bearer-and-joist floor consistent with a sloped regional
  block.
- **Front door:** centered on the house's street-facing wall.
- **Porch landing:** a small flat landing directly in front of the door, at
  floor height (~450-900mm above ground).
- **Staircase:** a single, direct, centered run of **4-5 steps**, aligned on
  the same axis as the door — straight down from the porch landing to
  ground level. No offset, no second mismatched patio level, no diagonal
  detour required.
- **Walkway:** a single continuous paved path connects the base of the
  staircase to the driveway where the car parks. **This is the actual
  route a person walks** — door → porch landing → down 4-5 steps → straight
  along the short connecting path → driveway/car. No gaps, no doubled-back
  segments, no obstacle placed directly in this line.
- **Landscaping placement, checked against the walkway (corrected
  2026-09-19 — real defect found on first diagram attempt):** the hedge
  along the driveway's edge was drawn as one unbroken border with no gap,
  fully sealing the driveway off from the walkway/lawn area — a real,
  confirmed defect, caught by checking the actual generated diagram against
  this plan, not assumed fixed by instruction alone. **The hedge/border
  must have an explicit, visible gap or opening at the exact point where
  the walkway crosses it**, the same way Tony's real reference photos show
  a real Australian house: a curved or straight concrete path cutting
  directly from the driveway across the lawn to the entry steps, with
  garden beds/low plantings running *alongside* that path as edging, never
  as an unbroken wall across it. Any hedge/border drawn as a single
  continuous unbroken line along the whole property edge — with no opening
  anywhere — fails this check by construction, regardless of where the
  walkway itself is labeled.
- **Driveway/car:** at the end of the walkway, screen-left edge of the
  doorbell frame, per already-locked facts.
- **Yard landmarks (already locked):** letterbox/mailbox, Hills Hoist
  clothesline, rainwater tank — placed in the open lawn area, clear of the
  walkway and staircase.

# Orientation reference (locked 2026-09-19 — real error found and fixed)

**Compass ground truth, independent of any camera:** the driveway/car sits
on the **west** side of the property. The hedge and mailbox sit on the
**east** side. The house is at the **north** end (top of the top-down
diagram), the street is at the **south** end.

**Corrected 2026-09-19 (real defect, caught by Tony, not by a check I
ran):** the Hills Hoist clothesline and the rainwater tank are NOT both on
the same side — checking the actual ground-truth photoreal POV panel
directly shows they're split. **The clothesline is on the east side**
(with the lawn/hedge/mailbox). **The water tank is on the west side**
(with the driveway/car) — it sits near the driveway, not the lawn. The
top-down and reverse-view diagrams were generated with both landmarks
grouped together on the east side, which contradicts the POV panel they
were supposed to match. Root cause: I wrote the site plan's landmark list
grouping them together by assumption/habit, and never checked the actual
generated POV panel's real landmark positions before writing the diagram
prompts that were supposed to match it — the exact same category of
mistake as the earlier left/right orientation error, just on individual
landmark placement instead of the whole-scene mirror.

**Real error, confirmed and corrected:** a top-down diagram's left/right
does NOT transfer directly to a first-person camera view — it depends
entirely on which direction that camera faces. This was gotten wrong once
already (the doorbell POV panel initially matched the top-down diagram's
raw left/right, which was actually backwards) before being corrected.

**The rule, stated so it can be checked, not re-derived from scratch each
time:**
- **Doorbell POV** (camera faces south, away from the house, out toward
  the street): west (driveway) appears on **screen-RIGHT**. East (hedge/
  mailbox) appears on **screen-LEFT**.
- **Reverse establishing view** (camera faces north, back toward the
  house): west (driveway) appears on **screen-LEFT**. East (hedge/mailbox)
  appears on **screen-RIGHT**.
- These two views face opposite directions, so they are always mirror
  images of each other for the same physical object — if one is on the
  POV's right, it is on the reverse view's left, always, by construction,
  never independently guessed per panel.
- **Top-down diagram itself:** west = page-left, east = page-right
  (standard north-up map convention) — this is the one view that does NOT
  need to be derived, it's the ground-truth source both other views are
  checked against.

Any new panel generated for this environment must state which of these
three view types it is, and get its left/right from this table — not from
copying another panel's screen-left/right by habit.

# Site Plan Coordinate Spec (locked 2026-09-19 — supersedes the section below)

**SUPERSEDED METHODOLOGY, kept for the record, not for reuse:** the
previous version of this section measured the photoreal POV panel and
derived diagram coordinates from it. That entire approach was backwards
and is retired per Tony's explicit, repeated correction: **the top-down
plan view is generated first and is the single source of truth; the front
view and POV are built from it and checked against it, never the
reverse.** It also only ever specified x (left/right), never y (depth),
which is how the water tank/clothesline depth error and the hedge-extent
error both got through uncaught.

**This is the actual spec — written before any image exists, x AND y for
every point, extent for line elements, orientation for the car.**
Convention: x=0 is the west/left edge of the property, x=1 is the east/
right edge. y=0 is at the house (north), y=1 is at the street (south).

| Element | x (west↔east) | y (house↔street, depth) | Notes |
|---|---|---|---|
| House / front door | x≈0.5 (centered) | y≈0.0 (north edge) | — |
| Porch landing + staircase | x≈0.5 (centered, same axis as door) | y≈0.05–0.15 | 4-5 steps |
| Walkway | x≈0.5 | spans y≈0.15 → y≈0.85 | connects staircase to driveway; hedge has a gap here |
| Driveway | x≈0.05–0.25 (west) | spans y≈0.15 → y≈0.95 (house to street) | — |
| Car | x≈0.1–0.2 (west, on driveway) | y≈0.5–0.7 (mid-to-rear of driveway) | **Orientation: backed in — rear/trunk faces the house (north, y=0 direction), front/nose faces the street (south, y=1 direction), ready to drive out forward. This is an independent fact from position and must be checked separately.** |
| Water tank | x≈0.05–0.15 (west, near driveway) | **y≈0.75–0.85 (near the street — corrected 2026-09-19, was wrongly placed near the house)** | — |
| Hedge (east side) | x≈0.85–1.0 (east) | **spans y≈0.1 → y≈0.95 — must reach the full east property edge (corrected 2026-09-19, was cut off short of the boundary)** | gap at walkway crossing (y≈0.15–0.2) |
| Hedge (west side, driveway edge) | x≈0.25–0.3 | spans y≈0.15 → y≈0.95 | gap at walkway crossing |
| Clothesline / Hills Hoist | x≈0.7–0.85 (east, with lawn) | **y≈0.75–0.85 (near the street — corrected 2026-09-19, was wrongly placed mid-yard near the house)** | — |
| Mailbox | x≈0.85–0.95 (east, at property edge) | y≈0.9–0.95 (at the street) | **A low bush/shrub belongs beside the mailbox (added 2026-09-19, per Tony's markup) — currently missing from every generated panel** |
| Front lawn | x≈0.35–0.85 (east of walkway) | y≈0.15–0.85 | open, no obstructions |

**Verification procedure, once panels exist:** for the top-down panel,
crop each element's exact expected (x, y) region and confirm it's
actually there — same discipline as before, now covering both axes. For
the front view and POV (perspective panels), check x the same way; check
y only by cross-referencing the stated house↔street depth qualitatively
(near house / mid-yard / near street) against what the panel shows, since
depth doesn't convert to vertical pixel position by a fixed rule in a
perspective shot — `check_landmark_positions.py` now reports y_center_frac
for exactly this cross-reference, without claiming to auto-validate it.
Check car orientation (front vs. rear direction) as its own explicit item
in every panel, never inferred from its position.

# Expected Layout Coordinates (SUPERSEDED 2026-09-19 — kept for the record only, do not reuse this methodology)

Schematic/line-art panels (top-down diagram, reverse establishing view)
cannot be checked with `check_landmark_positions.py`'s open-vocabulary
detector (OWL-ViT) — confirmed by direct test: it found all 5 landmarks
cleanly in the photoreal POV panel but found nothing reliable in the
schematic diagram (near-zero-threshold results were garbage, e.g. a
"clothesline" box spanning nearly the whole image). **Fix: measure the
ground-truth POV panel once with the tool, derive the expected mirrored
x-position for every landmark in the schematic panels mathematically, and
check the exact expected pixel region directly — not scan the whole image
and describe it.**

**Ground truth, measured via `check_landmark_positions.py` on the
approved photoreal POV panel** (x_center_frac, 0=left edge, 1=right edge):

| Landmark | POV (measured) | Expected in top-down/reverse (mirrored: 1 − POV) |
|---|---|---|
| Water tank | 0.944 (far right) | **0.056 (far left)** |
| Rotary clothesline | 0.156 (far left) | **0.845 (far right)** |
| Mailbox | 0.445 (center-left) | 0.555 (center-right) |
| Car | 0.833 (right) | 0.167 (left) |
| Hedge (nearest visible segment) | 0.583 (center-right) | 0.417 (center-left) |

**Why this was wrong, not just incomplete:** this table treated the
photoreal POV as ground truth to be measured and matched, when the
top-down plan should have been the ground truth all along. It also has no
y/depth column and no orientation field, which is exactly how the
depth and car-orientation defects got through.

# Measured Ground Truth (locked 2026-09-19 — Tony's call: the existing top-down IS the source of truth, as-is)

Tony's explicit direction: stop trying to perfect the top-down further —
accept `Data/Env_v3_Panel_1_TopDown.png` exactly as it stands as the fixed
source of truth, and make every other panel match **it**, not an idealized
spec. These values are measured directly off that actual image (visual
estimate, both axes), superseding the idealized coordinate table above for
generation/checking purposes:

| Element | x (west↔east) | y (house↔street, depth) |
|---|---|---|
| Front door | 0.48 | 0.27 |
| Porch landing / staircase | 0.44–0.51 | 0.27–0.42 |
| Walkway | 0.46–0.51 | spans 0.32 → 0.88 |
| Driveway | 0.17–0.32 | spans 0.20 → 0.95 |
| Car | 0.24–0.30 | 0.52 (mid-driveway) — **orientation: backed in, rear toward house (y→0), front toward street (y→1)** |
| Water tank | 0.18–0.26 | 0.14 (near house — matches Tony's markup, this is where it actually is in the accepted top-down) |
| Clothesline | 0.65–0.75 | 0.43 (mid-yard — matches Tony's markup) |
| Mailbox | 0.54 | 0.78 (near street) |
| Hedge, east side | spans 0.75 → 0.95 (does not reach the x=1.0 edge) | 0.82–0.87 |
| Hedge, west/driveway side | 0.32–0.34 | spans 0.42 → 0.86 |

**Every subsequent panel (front view, POV) must match these exact
positions on both axes** — mirrored on x per the Orientation reference
above, and matched on y directly (depth doesn't mirror, only left/right
does). If a landmark is measured near the house here, it must read as near
the house in every other panel too, not "somewhere in the yard."

# Architectural Plausibility Check (run against this plan, before any image exists)

| Check | Result |
|---|---|
| Does step count match a real single-story building's floor height? | Yes — 4-5 steps matches a ~450-900mm raised floor at standard step rise. The previous 10+ step version would imply an implausibly tall structure inconsistent with a normal single-story roofline. |
| Is there one continuous walkable path from car to door, with no gaps or illogical jumps? | Yes — car → driveway → connecting path → base of stairs → 4-5 steps → porch landing → door, one unbroken line. |
| Does any landscaping element block the actual walking path? | **Failed on attempt 1** — hedge drawn as one unbroken line, fully sealing the driveway off from the walkway, no gap anywhere. Corrected: hedge/border must have an explicit visible gap at the exact point the walkway crosses it, matching real reference photos of actual Australian houses (curved/straight concrete path cutting directly from driveway to entry, garden beds as edging alongside the path, never as an unbroken wall). |
| Is the staircase centered on the same axis as the door (no offset, no second mismatched patio level)? | Yes — single direct run, same axis as door and porch landing. |
| Is this consistent with already-locked facts (car position, door position, yard landmarks)? | Yes — no contradictions with the existing Blocking Plan or Grounding Audit. |
| Does every point landmark have an explicit depth (house↔street), not just a side? | Yes — see the Site Plan Coordinate Spec above, y-column added 2026-09-19. |
| Does every line/area element (hedges) have an explicit extent reaching the real property boundary, not just a position? | Yes — both hedge rows now specify a start/end span reaching the full edge. |
| Does the car have an explicit, independently-checked orientation (front/rear facing direction)? | Yes — backed in, rear toward the house, front toward the street; stated as its own fact, not inferred from position. |
| Does the plan include every element Tony has directly confirmed should exist (e.g. the mailbox bush)? | Yes — bush added to the Mailbox row. |

**POV panel locked 2026-09-19: Tony edited the image directly himself
after repeated AI-generation/inpaint attempts failed to get it right.**
Final file: `Character_Sheets/POV_Panel_Final_Tony_Edit.png`. This is now
the fixed ground truth for the POV — do not regenerate it.

All nine checks pass. **Generation order, locked and non-negotiable:
(1) top-down plan view first — the source of truth; (2) front/reverse
elevation view second, chained from and checked against the top-down;
(3) photorealistic POV panel last, chained from and checked against both.
No panel is ever generated before the panel(s) it depends on.**
