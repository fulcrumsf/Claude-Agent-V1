---
title: "Neon Parcel Production Report Card"
type: report
tags: [report, neon-parcel, seedance-2.0-mini, storyboard, autonomous-run]
---

# Shot 06 — Capybara at the Condo Gate (Sao Paulo suburb, Brazil)

**Grade: B+ (Tony, 2026-09-22). APPROVED, FINAL — no further spend on this shot.**
Tony's own words: look and correctness of movement earned the B+; the storyline itself is a minus, but it passes and is approved. This shot was run pipeline-to-completion autonomously per Tony's explicit instruction on 2026-09-21/22 ("test to see if the pipeline works on its own until it completes a video") — no per-step approval was requested after the storyboard.

## What ran, in order
1. Diversity Matrix (cell #8, capybara/motoboy/condo gate) + duplicate check vs. Shots 01-05 — no exact duplicate.
2. Concept filters — adapted the picked gag: capybara can't reach the motorcycle seat (0.55 m shoulder height vs ~0.78 m seat), and Brazilian condo delivery practice keeps the courier at the guardhouse, not riding in. New gag: capybara claims the dry spot under the awning; courier steps into the drizzle.
3. Grounding Audit (Phase 1 + Phase 2), Wikimedia Commons reference images (capybara, Brazilian portaria, Honda CG-class motorcycle).
4. Blocking Plan + Site Plan (revised once before any image, to put the camera facing the courier instead of behind him).
5. Environment sheet (5 panels: camera POV, top-down v1+v2, eye-level, reverse, landmark detail — top-down regenerated once to fix the motorcycle model).
6. Character sheet (Motoboy) — v1 failed the automated hand-check gate (a confident wrong-hand result on a close-up); v2 regenerated and passed 8/8.
7. Creature sheet (Capybara) — passed on the first generation.
8. Prop sheet (Motorcycle) — v1 invented ungrounded "held" panels with a generic hand (a real gap in the shared prop-sheet script, now fixed globally); v2 regenerated clean.
9. Storyboard (Storyboard_v1.png) — one retry needed (first Kie image task failed server-side, 0 credits; resubmission succeeded). Passed the automated body-orientation check (consistent turn, no flip) and a full frame-by-frame read.
10. Video: Seedance 2 Mini, winning-formula template, all 5 references sent and tagged, via `seedance2_call.py` (passed the tag/format gate on the first attempt). One paid generation, no retries needed.
11. Gemini evidence pass on the raw clip: confidence 0.95, no error-severity findings.
12. Upscale: Kie Topaz failed twice (server-side 500, 0 credits both times) → Magnific fallback succeeded (took ~50 min, unusually slow) → FFmpeg normalized to 1920x1080.

## My own review of the raw clip (frame-by-frame, not just the generation log)
- Subject count and identity held: exactly one motoboy, one capybara, one motorcycle throughout; motorcycle never moved.
- Story beats landed in order: capybara enters from off-frame on the verge, crosses, lies down on the dry slab, courier notices, steps into the drizzle and puts his helmet on.
- Scale read correctly (capybara knee-to-thigh height on the courier).
- **Flag:** the camera appears to push in slightly / reframe tighter starting around 8s, a soft violation of the "no camera movement" hard constraint. This matches the winning formula's known weak spot from Shot 05 (v7's "brief camera reframe ~2.5-4.5s"). Not corrected in this run since no approval checkpoint was requested — flagged here for Tony's grading.

## Files
- Storyboard: `Storyboard_v1.png`
- Raw video: `Data/Seedance_Mini_v1_Winning_Formula.mp4` (480p, as generated)
- Final: `Video_Clips/Shot-06-1080p-v1.mp4` (1920x1080)
- Full asset trail: `Data/Generation_Log.json`


## Grading detail (2026-09-22)
| Aspect | Verdict |
|---|---|
| Visual look | Pass (part of B+) |
| Movement correctness | Pass (part of B+) |
| Storyline | Weak (Tony's stated minus) |
| Overall | B+, approved, passes |

**Lesson for future Diversity Matrix cells (same category as the Shot 04 tanuki finding):** a technically clean, well-grounded shot can still have a weak storyline on its own terms, separately from execution quality. The comedic-hook requirement (added after Shot 04) evidently didn't fully close this gap for Shot 06's adapted gag (capybara claims the dry spot, courier steps into the rain) — worth a stronger hook check on the NEXT cell, not a redo of this approved one.
