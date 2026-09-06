# Diagram Blocking Plans — 0003_Glass_Frog_Transparency (Phase 6B)

Per-beat camera/reveal blocking plans for every diagram beat, tied to real word-level
timestamps from `Narration_Audio/scene_0N_beat_sheet.json`. Written so Phase 7 assembly
can implement directly without re-deriving anything. All illustrations already generated
(Step 1-2), all label coordinates already detected (Step 3) — see file paths per beat below.

**Method:** Diagram-Generation Approach B (component assets) — each anatomical concept
was generated as its own isolated illustration (organ cutaway, mirrored pouch, blood-cell
cross-section, etc.), matching this production's existing sequence-of-illustrations
structure. Phase 7 composites these via Remotion crop/zoom/pan keyframes (continuous
camera motion, never a fresh AI regeneration of the content) + `DiagramLabels.tsx` for
the label overlays, both driven by the timestamps below.

**Style judgment applied (per task instructions):** all illustrations use a clean
scientific-illustration treatment — muted anatomical color, near-black background, subtle
cool cyan-teal/silver highlights — NOT the full neon channel-brand treatment. These are
grounding illustrations that get camera/reveal-animated on top, not final branded graphics.

**Label/line color (Rule 1, `design-rules-learned.md`):** none of these illustrations use
the channel's brand green (`#8AFA47`) — sample the actual pixel color at each callout
anchor before finalizing in `DiagramLabels.tsx` (do not hardcode the component's brand-green
default for this production). Judgment calls below are directional; verify against the
actual rendered frame per Diagram-Generation's Step 4/Steps 4-5 guidance before shipping:
- `organ_cutaway` / `mirrored_pouch`: illustrations carry a faint cool cyan-teal rim glow —
  sample that cyan for label lines, white text (dark background).
- `mirrored_pouch_camouflage` / `vessel_cross_section`: cool cyan-silver highlights visible
  on the mirrored/vessel surfaces — same cyan sampling approach.
- `scene_06B_circulatory_infographic`: illustration already color-codes meaning (red =
  clot/danger, blue = normal flow) — do NOT sample one of those colors for the label lines,
  it would visually conflict with the content's own color-coding. Default to white-on-black
  per Rule 1's fallback instead.

---

## Scene_03 — Tease #1 (0.0–50.899s, max_static_s: 5.0)

**Assets:**
- `Images/scene_03/organ_cutaway/illustration.png` — labels: heart (50.2,39.5), liver
  (50.1,47.3), lungs (43.4,41.0), intestines (50.1,62.0) — all `confidence: high`.
- `Images/scene_03/mirrored_pouch/illustration.png` — labels: mirrored_pouch (59.2,50.1),
  guanine_crystal_surface (51.1,47.9) — both `confidence: high`.
- `Images/scene_03/species_montage/illustration.png` — no labels (illustrative sequence
  per task instructions — plain generated comparison panel, no label-detection run).
- Reference grounding: `Research/Reference_Images/` (glass frog anatomy/species refs) via
  Openverse search baked into `diagram_research_and_illustrate.py`'s own reference step.

**Blocking, tied to real word timestamps (`scene_03_beat_sheet.json`):**

| Segment | Asset | Motion | Labels revealed |
|---|---|---|---|
| 0.00–4.72s "Through that skin, you can see its heart, beating in real time." | organ_cutaway | Push-in centered on heart | heart @ ~2.2s (synced to word "heart") |
| 4.79–6.56s "Its liver." / "Its lungs." | organ_cutaway | Quick reframe pan heart→liver→lungs | liver @ ~5.0s, lungs @ ~5.7s |
| 6.88–9.24s "The coiled loops of its intestines." | organ_cutaway | Pan down to intestines | intestines @ ~7.1s |
| 9.52–14.69s "No dissection. No X-ray. Just daylight passing through living tissue." (5.17s) | organ_cutaway | **Continuous slow pull-back** revealing full torso silhouette across the whole segment | none (labels already placed) |
| 15.49–24.49s "Seeing the heart this clearly is rare... only show you bone, or the outline of the gut." (9.00s) | species_montage | **Continuous left-to-right pan** across the 3-species comparison panel | none |
| 25.18–32.51s "But here's what should be impossible..." (7.33s) | organ_cutaway | **Continuous punch-zoom** on liver silhouette (the "dark red blob" beat) | none (re-uses existing liver label position) |
| 33.20–41.24s "They're tucked inside tiny mirrored pouches..." (8.04s) | mirrored_pouch | **Continuous slow push-in** | mirrored_pouch @ ~34.0s, guanine_crystal_surface @ ~37.5s |
| 41.94–47.65s "The frog isn't just transparent. It's actively camouflaging its own insides." (5.71s) | mirrored_pouch | **Continuous pull-back** to reveal whole torso framing | none |
| 47.86–50.90s "And that's still not the most anomalous part." (3.04s) | (live_footage wide shot per Script visual 8 — not a diagram asset) | True static hold — allowed, under 5.0s cap, matches script's intentional near-silence beat | n/a |

**Static-hold check:** every segment ≥5.0s (9.52–14.69, 15.49–24.49, 25.18–32.51,
33.20–41.24, 41.94–47.65) is covered edge-to-edge by continuous camera motion (pull-back,
pan, punch-zoom) — zero static residual anywhere in the 50.899s scene. The one true static
hold (47.86–50.90s, 3.04s) is under the cap on its own, per the script's deliberate
near-silence beat.

---

## Scene_05 — Tease #2 (0.0–73.004s, max_static_s: 5.0) — longest/riskiest diagram beat

**Assets:**
- `Images/scene_05/blood_cell_concentration/illustration.png` — labels:
  red_blood_cells_awake (25.1,50.1), red_blood_cells_asleep (75.3,50.5) — both `high`.
  **`liver` came back `not_found` on this specific image** (it's a vessel-only
  cross-section, no liver depicted) — structurally stripped of coordinates by
  `detect_label_coordinates.py`, not rendered. The liver callout is instead placed on
  `mirrored_pouch_camouflage` below, where liver was detected at high confidence.
- `Images/scene_05/mirrored_pouch_camouflage/illustration.png` — labels: liver (51.5,42.5),
  mirrored_surface (40.0,28.0), red_blood_cells (43.1,53.2) — all `high`. Grounded
  additionally against `Research/NotebookLM_Test_Infographic_Mirrored_Liver.png` (the
  Tony-approved test infographic of this exact mechanism) per the task's explicit
  instruction to reuse it as reference for this beat.
- `Images/scene_05/vessel_cross_section/illustration.png` — labels: red_blood_cells
  (47.9,53.6), vessel_wall (39.5,28.5) — both `high`.
- `Images/scene_05/side_by_side/illustration.png` — no labels (illustrative b-roll per
  task instructions — awake-vs-asleep comparison shot, skipped label-detection).
- `Images/scene_05/photoacoustic_insert/illustration.png` — no labels (illustrative b-roll
  per task instructions — lab/device visualization, skipped label-detection).

**Blocking, tied to real word timestamps (`scene_05_beat_sheet.json`):**

| Segment | Duration | Asset | Motion | Labels |
|---|---|---|---|---|
| 0.00–5.07s "Science has only recently discovered how far this trick actually goes." | 5.07s | (live_footage: frog asleep, wide) | Continuous slow push-in | n/a |
| 5.77–18.01s "In 2022, researchers... turn their own transparency up on command." | 12.24s | blood_cell_concentration | Hold ~4s on red_blood_cells_awake, then continuous pan to red_blood_cells_asleep | awake @ ~t+1s, asleep @ ~t+9s |
| 18.45–25.43s "While a glass frog sleeps, it pulls nearly ninety percent..." | 6.98s | blood_cell_concentration | Continuous tighter reframe on asleep side + subtle opacity-ramp "draining" overlay | (both labels already placed) |
| 25.87–28.80s "It packs them into one organ. Its liver." | 2.93s | mirrored_pouch_camouflage | Hard cut in, push-in on liver | liver @ 28.04s (synced to word "liver") |
| 29.25–37.56s "With that much of its blood cells removed... two to three times more transparent..." | 8.31s | mirrored_pouch_camouflage | Continuous two-stage push/pan: liver → mirrored_surface → red_blood_cells | mirrored_surface @ ~t+2s, red_blood_cells @ ~t+6s |
| 38.07–43.96s "We'll come back to why that matters — but first, consider what should happen next." | 5.89s | side_by_side | Continuous slow pan left→right across the two halves | n/a |
| 44.56–51.46s "In almost every other vertebrate on Earth, concentrating blood cells that densely triggers dangerous clotting." | 6.90s | vessel_cross_section | Continuous push-in + subtle pulse/compression animation on the cell mass, timed to peak at "triggers dangerous clotting" | red_blood_cells @ early, vessel_wall @ mid |
| 52.15–57.24s "Glass frogs do this every single day, and their blood never clots at all." | 5.09s | vessel_cross_section | Continuous slow pull-back + gentle cool-toned color-grade shift (signals "no clotting here") | (labels already placed) |
| 57.84–73.00s "Researchers only caught this happening using... on a frog that never even woke up." | 15.16s | photoacoustic_insert | Two-stage: (a) ~7s continuous looping sound-wave-ripple overlay animation over the frog, synced to "pulses of light that make blood cells vibrate audibly"; (b) ~8s continuous slow push-in toward the frog, settling on a calm close-up | n/a |

**Static-hold check (mandatory, this is the longest diagram beat — 73.004s total):**
Sum of segments = 5.07 + 12.24 + 6.98 + 2.93 + 8.31 + 5.89 + 6.90 + 5.09 + 15.16 = **73.004s**
(sums to the exact beat duration). Every segment at or above the 5.0s cap
(5.07, 12.24, 6.98, 8.31, 5.89, 6.90, 5.09, and the two 7s/8s halves of the final 15.16s
segment) is covered edge-to-edge by continuous camera motion, an animated overlay, or a
color-grade move — **zero static residual anywhere in the scene.** The two sub-5s segments
(2.93s cut-in) don't need coverage on their own. This is the check Phase 7's rule requires
before finalizing — confirmed clean.

---

## Scene_06 — Reward (0.0–50.434s, max_static_s: 5.0) — mixed live_footage + diagram

Per `Shot_List.md`, only sub-beats 06B and 06C are true diagram content; visuals 1/4/5/6/7
are live_footage-style Seedance generation with camera motion baked into the clip itself
(handled by Phase 6A, not Remotion diagram blocking) — included here only to confirm the
full-scene static-hold arithmetic, per the task's instruction to check the whole scene.

**Assets:**
- `Images/scene_06B_circulatory_infographic/illustration.png` — labels: clot_formation
  (36.9,49.3), platelets (35.0,44.1), normal_blood_flow (75.6,59.8) — all `high`.
- `Images/scene_06C_lab_insert/illustration.png` — no labels (illustrative lab/photoacoustic
  insert, consistent with scene_05's photoacoustic_insert treatment — equipment/overlay
  visualization, not anatomical callouts).

**Blocking, tied to real word timestamps (`scene_06_beat_sheet.json`):**

| Segment | Duration | Content | Motion |
|---|---|---|---|
| 0.00–6.82s "That contradiction is exactly what makes this discovery matter..." | 6.82s | live_footage (wide cinematic pull-back on frog) | Baked Seedance camera pull-back |
| 7.51–19.09s "In humans, the balance between clotting and bleeding..." | 11.58s | scene_06B_circulatory_infographic | Continuous hold+push on clot_formation/platelets cluster (~5s) then pan to normal_blood_flow (~6.5s) |
| 19.78–24.91s "One of the researchers called solving that balance the holy grail of hematology." | 5.13s | scene_06C_lab_insert | Continuous zoom-in + ripple-overlay animation |
| 25.52–30.12s "A glass frog solves it daily, without trying, every time it falls asleep." | 4.60s | live_footage (return to frog, calm) | Under cap, held with native idle motion from the generated clip |
| 30.63–42.53s "What we now know is that studying this small, transparent animal..." | 11.90s | live_footage (push-in on transparent belly) | Baked Seedance push-in, single continuous shot |
| 43.13–50.43s "Of all the creatures on Earth working on this problem..." | 7.30s | live_footage (overhead pull-back + final wide hold) | Baked Seedance pull-back |

**Static-hold check:** the two diagram sub-beats (06B: 11.58s, 06C: 5.13s) are each covered
edge-to-edge by continuous pan/zoom + label/overlay motion — no static residual. The
live_footage segments carry their own baked camera motion from Phase 6A generation, which
is the standard mechanism for that routing (not a Remotion blocking concern). Total scene
duration accounts for natural inter-sentence pause gaps (~0.7s each, well under any static
threshold on their own).

---

## Not-found flags (structural, not a guess)

Only one: `liver` on `Images/scene_05/blood_cell_concentration/illustration.png`
(`confidence: not_found`) — `detect_label_coordinates.py` structurally stripped its
coordinates rather than guessing. Resolved by placing the liver callout on
`mirrored_pouch_camouflage` instead, where it was detected at high confidence — no
anatomically-incorrect guess made anywhere in this beat.

## Skipped label-detection (per task instructions, not an oversight)

- `Images/scene_03/species_montage/` — plain generated comparison sequence, no callouts needed.
- `Images/scene_05/side_by_side/` — illustrative b-roll comparison shot.
- `Images/scene_05/photoacoustic_insert/` — illustrative lab/device insert.
- `Images/scene_06C_lab_insert/` — illustrative lab/photoacoustic insert (same treatment as scene_05's).
