# Shot List — 0002 Mantis Shrimp Color Vision

Tool routing confirmed against `motion_graphics_capabilities.json` (Tool-Manager). Live-footage beats route to kie.ai video generation via `pipeline_supervisor.py` (per skill Phase 6A); diagram beats route to the Scientific Diagram sub-pipeline (Phase 6B), which itself uses Openverse (reference) + kie.ai GPT-Image-2 (illustration) + Gemini vision (label coordinates) + Remotion `DiagramLabels` (placement) — confirmed as Remotion's documented `best_for` case for labeled scientific diagrams.

Video model: **Seedance 2.0 Fast** via kie.ai (`$0.165/s`, 720p) — Tool-Manager's top-rated (8.8/10) documentary/cinematic-fast recommendation. (fal_ai lists a nominally lower "$0.0112/unit" price for the same model, but that unit is ambiguous in the catalog and kie.ai is this workspace's documented default gateway — using kie.ai for a clean, verifiable estimate.)

Beats over the 8.0s live-footage clip cap are split into multiple clips.

---

## Scene 01 — GLITCH HOOK (live_footage, 1 clip)
**C01** (0.0–7.5s): Extreme macro of a mantis shrimp compound eye, independently rotating, dark neon palette (deep teal/forest green/amber), National Geographic lighting, photorealistic 8K, no text

## Scene 02 — SETUP (diagram, 1 illustration)
**D02**: Side-by-side comparison — human eye cross-section (3 receptor types) vs. mantis shrimp compound eye cross-section (16 receptor types), labeled scientific diagram style — ✅ generated, `Images/scene_02/illustration.png` (note: no Openverse reference found for this query — not anatomically grounded against a real photo, flagged by the pipeline itself)

## Scene 03 — SETUP cont. (live_footage, 2 clips)
**C03a** (0.0–6.25s): POV shot, camera becomes one independently-moving eyestalk, rotating to track subject
**C03b** (6.25–12.5s): Second eyestalk visible at frame edge, tracking a different subject simultaneously

## Scene 04 — TEASE #1 (live_footage, 3 clips)
**C04a** (0.0–6.0s): Slow-mo freeze on the eye mid-rotation
**C04b** (6.0–12.0s): Zoom punch into individual ommatidia (compound eye facets), macro detail
**C04c** (12.0–18.0s): Hold on facet detail, Anomaly Level Meter overlay triggers (Remotion channel-chrome graphic, not part of diagram sub-pipeline)

## Scene 05 — CONTEXT LOOP (diagram, 1 illustration) — 32.8s
**D05**: 3D-style render, light waves shown twisting toward the eye (circular polarization mechanism), labeled scientific diagram style — ✅ generated, `Images/scene_05/illustration.png`

## Scene 05B — CONTEXT LOOP cont. (diagram, 1 illustration) — 9.9s
**D05b**: Two mantis shrimp facing off, glowing polarization-signal patterns visible only under "shrimp-vision" overlay — labeled/annotated diagram style — ✅ generated, `Images/scene_05b/illustration.png` (note: reads more as atmospheric artwork than a clean labeled diagram — style consistency gap vs. D02/D05)
*(Split 2026-08-16 from the original single 44s scene per Tony's 3-5s motion rule — see Anomalous-Wild-Scriptwriter.md's Mandatory Visual-Duration Check. Each half now has its own beat and its own static-hold check at 5.0s max.)*

## Scene 06 — TEASE #2 (live_footage, 1 clip)
**C06** (0.0–5.9s): Rack focus from eye to the mantis shrimp's raptorial appendage (front claw), held in ready position

## Scene 07 — REWARD (live_footage, 4 clips)
**C07a** (0.0–7.1s): Strike wind-up, raptorial appendage coiling
**C07b** (7.1–14.2s): Ultra-high-speed strike release, cavitation bubble forming
**C07c** (14.2–21.3s): Cavitation bubble collapse, flash of light
**C07d** (21.3–28.3s): Cut back to the eye tracking the entire event in real time

## Scene 08 — HOOK FORWARD (live_footage, 3 clips)
**C08a** (0.0–5.7s): Pull back from eye
**C08b** (5.7–11.3s): Full mantis shrimp visible in burrow
**C08c** (11.3–17.0s): Hold on final frame, neon green rim-light, ready for end card

---

## Totals
- Live-footage clips: 14 (≈89.3s total runtime → ≈$14.74 at kie.ai Seedance 2.0 Fast $0.165/s, 720p) — **not yet generated, stopped here per Tony's instruction**
- Diagram illustrations: 3 (scene_02, scene_05, scene_05b) — ✅ all generated
- Character sheet: 1 (mantis shrimp) — ✅ generated (approved for this test run, see Data/Generation_Log.json for corrections locked in for future sheets)
- Storyboards: 6 (one per live-footage scene) — ✅ all generated
- Music: 1 Suno track → $0.06 (kie.ai) — not yet generated
- SFX stems: small number of short ElevenLabs generations, negligible — not yet generated

**Image-phase actual spend: well under $1** (1 character sheet + 6 storyboards + 3 diagrams, all GPT-Image-2 at ~$0.03/image). Live-footage video generation (≈$14.74) is the only piece still pending — stopped here for Tony's review per instruction, resume only on explicit go-ahead.
