# Shot List / Tool Routing — 0003_Glass_Frog_Transparency

Per-beat routing decisions, reasoned against `motion_graphics_capabilities.json` (Remotion / video-use / Hyperframes / Manim) per Phase 5's Tool-Manager-consultation requirement. No tool assumed by default — reasoning given per beat.

> **The routing table below is as-planned. For what actually shipped in the
> approved grade-A final cut, read `## FINAL CUT — as shipped` at the bottom of
> this file.** Scene-level timings are unchanged (`Beat_Table.json` still accurate);
> the deltas are shot-level.

---

## scene_01 — Hook (0–3.85s) — live_footage

**Visual need:** Extreme macro glitch-cut push through canopy at night to the frog's translucent belly, backlit, heart visible beating. No on-screen text.

**Routing:** `pipeline_supervisor.py`-driven generation (Seedance 1.5 Pro, per Phase 6A default). No compositing tool needed — no overlay/callout in this beat, and the glitch-cut transition is a straight video edit, not a graphics composition.

---

## scene_02 — Setup (0–14.4s) — live_footage

**Visual need:** Wide establishing shot of frog on leaf (dorsal view) → hard cut to macro underside reveal → backlit organ silhouette → skin-texture comparison → POV drift toward organs. On-screen: Species Name Card (fly-in text, per style guide's locked graphics system).

**Routing:** `pipeline_supervisor.py` generation for all 5 visual segments (each ≤8s live-footage cap satisfied — longest is 7s). **+ Remotion** for the Species Name Card overlay — matches `motion_graphics_capabilities.json`'s Remotion `best_for`: "Compositing illustrated overlays on top of generated or filmed footage," which is exactly the BioluminescenceDoc.tsx precedent already cited in Phase 7.

---

## scene_03 — Tease #1 (0–50.9s) — diagram

**Visual need:** Internal 3D-render cutaways (heart, liver, lungs, intestines), species-comparison montage, mirrored guanine-crystal pouch cutaway, Fact Callout ("Mirrored organ pouches").

**Routing:** **Scientific Diagram sub-pipeline** (Phase 6B: `diagram_research_and_illustrate.py` → `detect_label_coordinates.py` → `DiagramLabels.tsx`) for the organ-cutaway and mirrored-pouch illustrations — matches Remotion's documented `best_for`: "Labeled scientific/technical diagrams with exact coordinate-based callout placement," confirmed against the PhylogeneticTree.tsx precedent in the capability profile. The species-comparison montage (visual 4) is closer to a straight generated-image sequence than a labeled diagram — route that specific shot through image generation (GPT-Image-2) directly rather than the full label-detection sub-pipeline, since it needs no anatomical callouts, just side-by-side comparison frames. Fact Callout text via Remotion (same overlay capability as scene_02).

**Note for Diagram-Generation (Phase 6B Step 5):** this beat's 50.9s runtime with `max_static_s: 5.0` needs a real camera/reveal blocking plan — flag for the mandatory static-hold check at Phase 7.

---

## scene_04 — Context Loop (0–35.5s) — live_footage

**Visual need:** Animated range map, wide cloud-forest/stream establishing shots, nocturnal ambush-hunting behavior, daytime sleeping frog, backlit near-invisible side shot. On-screen: Location Card.

**Routing:** `pipeline_supervisor.py` generation for the frog-specific shots (visuals 2, 4, 5, 6). Visual 3 (nocturnal hunting behavior) is a **Production-Asset-Planner B-roll candidate** — per Script.md's production notes, the generic Pexels rainforest-amphibian inventory may cover a generic ambush-hunting cutaway here; confirm in Phase 5B rather than assuming generation is required. **+ Remotion** for the Location Card overlay and the range-map animation — the map is a data-driven graphic (geographic outline + animated path), which fits Remotion's documented data-visualization strength better than any other tool in the profile (Hyperframes is explicitly `not_for` precise coordinate-based placement; Manim is `not_for` compositing over generated imagery — a map needs both).

---

## scene_05 — Tease #2 (0–73.0s) — diagram

**Visual need:** Awake-vs-asleep 3D internal renders (blood cell density), concentration-into-liver render, mirrored-pouch camouflage render, side-by-side comparison shot, vessel cross-section, human vascular cross-section insert, photoacoustic imaging device visualization. On-screen: two Fact Callouts + Anomaly Level Meter.

**Routing:** **Scientific Diagram sub-pipeline** for the vessel cross-sections and mirrored-pouch camouflage render (labeled, coordinate-anchored anatomy — same Remotion `best_for` fit as scene_03). The awake/asleep side-by-side comparison and the photoacoustic-imaging-device insert are closer to generated illustrative b-roll than labeled diagrams — route those through direct image/video generation, not the label-detection sub-pipeline. **+ Remotion** for both Fact Callouts and the Anomaly Level Meter (explicitly a data/stat-reveal graphic, matching Remotion's "data visualization (charts, counters, stat reveals)" strength).

**Note for Diagram-Generation (Phase 6B Step 5):** longest diagram beat in the production (73.0s, `max_static_s: 5.0`) — needs the most rigorous camera/reveal blocking plan of the three diagram scenes; do not under-plan this one.

---

## scene_06 — Reward (0–50.4s) — diagram

**Visual need:** Wide cinematic pull-back on frog, abstract human-circulatory infographic render, lab/photoacoustic insert, final push-in on transparent belly, pull-back to canopy. On-screen: Fact Callout ("Studied for human blood-clot research").

**Routing:** Mixed — visuals 1, 4, 6, 7 (frog shots, cinematic pull-back/push-in) are **live_footage-style generation** via `pipeline_supervisor.py` despite the scene's overall `diagram` coarse routing, since they're real/generated creature footage, not labeled anatomy. Visual 2 (human circulatory infographic) is the one true **Scientific Diagram sub-pipeline** candidate here — this is also the beat where the Phase 6B NotebookLM-infographic reference-grounding option (once documented per today's approved addition) would be most useful, since a clean medical-diagram reference could sharpen the illustration step beyond what a photo reference alone provides. **+ Remotion** for the Fact Callout.

**Flag:** this scene mixes live_footage and diagram beats more evenly than any other scene in the production — Production-Asset-Planner (Phase 5B) should treat scene_06's sub-beats individually rather than applying one blanket treatment.

---

## scene_07 — Hook Forward (0–4.7s) — live_footage

**Visual need:** Single quick glitch-cut flash-frame of an unnamed future-video creature. No on-screen text.

**Routing:** `pipeline_supervisor.py` generation, single short clip. No compositing tool needed.

---

## Summary

| Scene | Coarse routing | Generation | Compositing/overlay tool |
|---|---|---|---|
| 01 | live_footage | Seedance 1.5 Pro | none |
| 02 | live_footage | Seedance 1.5 Pro | Remotion (Species Name Card) |
| 03 | diagram | Scientific Diagram sub-pipeline + GPT-Image-2 (comparison montage) | Remotion (labels + Fact Callout) |
| 04 | live_footage | Seedance 1.5 Pro + possible B-roll (Phase 5B to confirm) | Remotion (Location Card + map animation) |
| 05 | diagram | Scientific Diagram sub-pipeline + generated inserts | Remotion (labels + 2 Fact Callouts + Anomaly Meter) |
| 06 | diagram (mixed) | Seedance 1.5 Pro (frog shots) + Scientific Diagram sub-pipeline (infographic insert) | Remotion (Fact Callout) |
| 07 | live_footage | Seedance 1.5 Pro | none |

No beat in this production required Hyperframes or Manim — no music-reactive visuals, karaoke-style captions, or pure equation/algorithm content anywhere in this script. Remotion covers every overlay/diagram need per its documented capability profile.

---

## FINAL CUT — as shipped (approved grade A, 2026-09-04)

Deltas from the as-planned routing above, after the 23-note revision + Round 2.
Composition = `003_Remotion/src/remotion/video-components/GlassFrogDoc.tsx`.

**Global**
- **Every cut is a 0.5s cross-dissolve** (`ChainScene` freeze-under/live-over),
  scene boundaries and internal shot changes alike. No hard cuts anywhere.
- Audio: **video-to-audio ambience** via `generate_stems_v2a.py` (fal.ai Mirelo
  SFX v1.6, 6 scene-boundary segments, crossfaded, −25 LUFS) is the SFX default;
  ElevenLabs `generate_stems.py` is the fallback. Score = Suno track 2
  ("science documentary" brief), −22 LUFS + sidechain duck. Narration −14.
  End card CTA VO normalized to −14 (matched to body VO).

**scene_01 / scene_02 / scene_07** — as planned (Seedance 1.5 Pro clips + Remotion
species card). scene_02's mid-scene 02A→02B is a freeze+dissolve (unchanged).

**scene_03** — as planned diagram pipeline, PLUS:
- `MIRRORED_POUCH_03` shot shortened to ~9.8s.
- **New `FROG_PHOTO_03` shot** cross-dissolves in at ~43s: a real public-domain
  glass-frog photograph (GPT-Image-2 v1, `Images/scene_03/glass_frog_photo/` +
  SOURCE.md), Ken-Burns move. Used where a generated illustration would strain
  credibility. `S03_SHOTS` = 4 shots.

**scene_04** — as planned, PLUS:
- `RangeMapAnimation` now draws the range path over a **real Natural Earth
  basemap** (`Images/scene_04_range_map/basemap.png` + SOURCE.md, public domain,
  no attribution), AW-styled — not the synthetic SVG-only map.
- **`Scene_04D` regenerated** (Seedance 1.5 Pro): was showing a heart (wrong
  beat) + a leg glitch; now the tongue-strike / moth-snap the VO describes.

**scene_05** — as planned diagram pipeline. Camera holds under every label
(`buildPath()` `holdS` dwell keyframes). `S05_SHOTS` = 6 shots.

**scene_06** — mixed live/diagram as planned, PLUS:
- **`Scene_06A` regenerated**: was cut internally by Seedance ~3s in; now one
  continuous pull-back, no internal cut.
- **`Scene_06F` / `06G` / `06H` reworked** (`VanishShot` / `HeldVideoShot`):
  Seedance 1.5 cannot animate "become transparent/invisible", so the vanish is
  done in Remotion — the clip plays, then the last ~1.3–2s cross-dissolve to that
  shot's pre-extracted `_End.png` still (frog dissolved into the leaf). 06G is
  held + Ken-Burns'd past its 6.07s real length to ~8.8s. No two live
  `OffthreadVideo`s ever overlap (kills the horizontal-band tear). 06F carries a
  known toe-count morph at ~3:32 — Tony let it pass.

