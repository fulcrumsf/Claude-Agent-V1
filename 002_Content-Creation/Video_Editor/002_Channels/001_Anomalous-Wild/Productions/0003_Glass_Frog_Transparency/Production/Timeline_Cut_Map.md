# 0003 Glass Frog — Timeline / Cut Map

Frame map of every scene boundary, cut, transition, freeze-fill and overlay in
`GlassFrogDoc.tsx` (composition `GlassFrogDoc`, 30fps, 6986 frames = 3:52.9).
In Remotion Studio, type a frame number in the frame field to jump to any row.

> **⚠️ 2026-09-04: the internal per-scene tables below were generated 2026-08-31,
> BEFORE Revision Round 1. Scene-start frames are still correct. The internal rows
> are stale in these ways — corrected here, not yet re-tabulated row by row:**
>
> - **There are no hard cuts anymore.** Every `**` row below is now a **0.5s
>   cross-dissolve** (`ChainScene` freeze-under/live-over). This is the single
>   biggest change. The old summary line "every scene boundary is a HARD CUT" is void.
> - **scene_03** gained a real glass-frog **photo** shot (`FROG_PHOTO_03`,
>   Ken-Burns) cross-dissolving in at ~43s; `MIRRORED_POUCH_03` shortened to ~9.8s.
> - **scene_04** frame 2075: `RangeMapAnimation` now draws over a **real Natural
>   Earth basemap**, not the synthetic SVG. `Scene_04D` regenerated (tongue strike).
> - **scene_06** `Scene_06A` regenerated (no internal cut). `06F/06G/06H` rebuilt
>   as `VanishShot`/`HeldVideoShot`: frames roughly 06F 6268→6510, 06G 6510→6692
>   (held+KenBurns to ~8.8s on screen), 06H 6692→6844, each boundary a ~1.3s
>   crossfade, 06F/06H dissolve into their `_End.png` stills.
> - Audio (appended/mixed post-composition): v2a Mirelo ambience −25 LUFS
>   (default; ElevenLabs stems = fallback) + Suno track-2 score −22 + narration −14
>   + end card with CTA VO at −14.

Legend: `**` = shot change (now a 0.5s cross-dissolve) · `+` = overlay graphic on top.
The end card is appended after this composition by ffmpeg (Phase 7), not in Remotion.

---

## Scene starts — ALL HARD CUTS between scenes

| Time | Frame | Scene |
|---|---|---|
| 0:00.0 | 0 | **SCENE 01** — single clip `Scene_01A_looped.mp4`, no transitions |
| 0:03.9 | 116 | **SCENE 02** |
| 0:18.3 | 548 | **SCENE 03** |
| 1:09.2 | 2075 | **SCENE 04** |
| 1:44.7 | 3141 | **SCENE 05** |
| 2:57.7 | 5331 | **SCENE 06** |
| 3:48.1 | 6844 | **SCENE 07** |
| 3:52.9 | 6986 | END of Remotion composition |

---

## SCENE 02 (116–548) — the ONLY real transition in the whole video

| Time | Frame | Event |
|---|---|---|
| 0:04.9 | 146 | + species card "Glass Frog / Centrolenidae" fades IN |
| 0:08.9 | 266 | + species card fades OUT |
| 0:10.5 | 316 | 02A live clip begins easing out; **KenBurns** slow zoom/drift starts |
| 0:10.9 | 328 | 02A real footage ends → **FREEZE-HOLD** of its last frame begins |
| 0:11.4 | 343 | 02B enters, **0.5s opacity crossfade** over the frozen 02A |
| 0:11.9 | 358 | crossfade complete — fully on 02B (Ken Burns still drifting to scene end) |
| 0:18.3 | 548 | hard cut to SCENE 03 |

`Scene_02A_looped.mp4` real length 7.083s; `Scene_02B_looped.mp4` 7.083s (windowed to 205 frames).

---

## SCENE 03 (548–2075) — diagrams, HARD CUTS between illustrations, camera never stops

| Time | Frame | Event |
|---|---|---|
| 0:18.3 | 548 | organ cutaway (labels: heart) |
| 0:23.1 | 692 | same image — no visible cut, camera moves (labels: liver, lungs) |
| 0:25.1 | 754 | same image (label: intestines) |
| 0:27.8 | 834 | same image |
| 0:33.8 | 1013 | **CUT → species montage** |
| 0:43.4 | 1303 | **CUT → organ cutaway** |
| 0:51.5 | 1544 | **CUT → mirrored pouch** · + callout "Mirrored organ pouches" (6s) (labels: mirrored_pouch, guanine_crystal_surface) |
| 1:00.2 | 1806 | same image, camera continues |
| 1:06.1 | 1984 | same image — near-silence hold beat |
| 1:09.2 | 2075 | hard cut to SCENE 04 |

---

## SCENE 04 (2075–3141) — range map + b-roll, ALL HARD CUTS

| Time | Frame | Event |
|---|---|---|
| 1:09.2 | 2075 | RangeMapAnimation (SVG line draws on) — **the weak one, needs a real map background: Mexico → Amazon** |
| 1:14.4 | 2231 | **CUT → clip 04B** |
| 1:15.7 | 2270 | + LocationCard "Cloud Forests, Central & South America" (3s) |
| 1:20.4 | 2413 | **CUT → 04C** |
| 1:26.5 | 2595 | **CUT → 04D** |
| 1:32.6 | 2777 | **CUT → 04E** |
| 1:39.6 | 2989 | **CUT → 04F** |
| 1:44.7 | 3141 | hard cut to SCENE 05 |

---

## SCENE 05 (3141–5331) — diagrams, HARD CUTS between illustrations, camera never stops

| Time | Frame | Event |
|---|---|---|
| 1:44.7 | 3141 | side-by-side |
| 1:50.5 | 3314 | **CUT → blood cell concentration** (labels: red_blood_cells awake/asleep) |
| 2:03.2 | 3695 | same image · + callout "90% of red blood cells hidden" (6s, ~2:03.3) |
| 2:10.6 | 3917 | **CUT → mirrored pouch camouflage** (label: liver) |
| 2:14.0 | 4019 | same image · + callout "2–3x more transparent" (6s, ~2:14.7) (labels: mirrored_surface, red_blood_cells) |
| 2:22.8 | 4283 | **CUT → side-by-side** |
| 2:29.3 | 4478 | **CUT → vessel cross-section** · + AnomalyMeter 9/10 (6s, ~2:29.5) (labels: red_blood_cells, vessel_wall) |
| 2:36.8 | 4705 | same image |
| 2:42.5 | 4876 | **CUT → photoacoustic insert** |
| 2:57.7 | 5331 | hard cut to SCENE 06 |

---

## SCENE 06 (5331–6844) — video + infographics mixed, ALL HARD CUTS

| Time | Frame | Event |
|---|---|---|
| 2:57.7 | 5331 | clip 06A (live footage) |
| 3:03.8 | 5513 | **CUT → 06B circulatory infographic** (labels: clot_formation, platelets, normal_blood_flow) |
| 3:10.1 | 5702 | **CUT → 06C lab insert diagram** |
| 3:14.8 | 5844 | **CUT → 06D (live footage)** |
| 3:20.9 | 6026 | **CUT → 06E** |
| 3:28.9 | 6268 | **CUT → 06F** |
| 3:37.0 | 6510 | **CUT → 06G** |
| 3:43.1 | 6692 | **CUT → 06H** |
| 3:39.7 | 6591 | + callout "Studied for human blood-clot research" (8.4s) |
| 3:48.1 | 6844 | hard cut to SCENE 07 |

---

## SCENE 07 (6844–6986) — single clip, dark cinematic open, no transition

| Time | Frame | Event |
|---|---|---|
| 3:48.1 | 6844 | clip 07A (Hook Forward) — opens dark by design |
| 3:52.9 | 6986 | END |

---

## Summary (as of the approved final cut, 2026-09-04)

- **Every scene boundary and every internal shot change is a 0.5s cross-dissolve**
  (`ChainScene` freeze-under/live-over). No hard cuts anywhere in the video.
- 06F/06H additionally dissolve into a static end-frame PNG (the "vanish"); 06G is
  a held + Ken-Burns'd still past its real clip length.
- Diagram scenes (03, 05, 06B/C) keep the camera moving across every dissolve, and
  hold it still under every label (move → settle → label in → hold → label out → move).
- All infographics/labels/cards/maps are **Remotion components** (`DiagramLabels.tsx`,
  `SceneOverlay.tsx`, `LocationCard`, `AnomalyMeter`, `RangeMapAnimation`) — nothing
  is baked into the illustration PNGs. The scene-03 photo shot and scene-04 basemap
  are the only photographic assets; both are public domain with SOURCE.md.
- Automated scans (final cut, 2026-09-04): audio-pop scan clean; no true-black
  frames except the end card's own designed fade-out; no white-flash frames.
