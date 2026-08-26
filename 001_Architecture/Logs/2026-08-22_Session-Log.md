---
title: "Session Log — 2026-08-22"
type: log
domain: video-production
tags: [log, session, anomalous-wild, mantis-shrimp]
---

# Session Log — 2026-08-22 (multi-day arc, Aug 19–22)

## What happened
Full scene-by-scene production pass on Anomalous Wild's `0002_Mantis_Shrimp_Color_Vision`, ending in a complete first-cut assembled video. This was explicitly a pipeline-testing session (Tony's framing: "testing this pipeline... go individually, scene by scene... 80%→95% confidence before autonomous mode").

## Key actions, in order
1. **Storyboard-vs-shot-list reconciliation** for all 8 live-footage/diagram scenes (03, 04, 06, 07, 08 needed rewrites/refinements; 01, 02 pre-existing). Root cause: several Shot_List.md entries predated their real storyboards and drifted from them.
2. **Locked new pipeline rules** (all written into skill files, not just this session):
   - Clip-boundary decision: "can one prompt + one start frame + one end frame plausibly produce this, in ≤~8s?" — not fixed duration splits. (`Production-Asset-Planner/SKILL.md`)
   - Sequential lettering spans a whole scene's segments (generated + B-roll together), not separate tracks.
   - B-roll now saves into `Video_Clips/<Scene>/`, not a separate `B_Roll/` folder.
   - Start/end frame must be visually distinct — near-duplicate framing gives Seedance nothing to interpolate. (`Seedance-Prompting-Guide/SKILL.md`)
   - End frame generation must reference the start frame as an input image, not just the storyboard panel — prevents independently-invented environments (caught on Scene_03E, background genuinely changed mid-clip).
   - Chroma-green matting causes color-spill contamination on *translucent/glowing* components (not opaque ones) — use near-black for those specifically. (`Motion-Graphics-Compositing/SKILL.md`, caught on Scene 05's light-wave assets)
3. **Deliberate visual variety across scenes**, Tony's explicit instruction: Scene 03 = dark neutral, Scene 04 = warm shallow-tropical (turquoise/caustics), Scene 06 = cooler blue-violet dusk — creature coloration itself never changes (no real biological basis for a cold/warm color morph in *Odontodactylus scyllarus*, confirmed via web research).
4. **Diagram animation via Approach B** (component-asset + Remotion compositing, not Seedance) applied to Scenes 05 and 05B — both previously flat static images, now real keyframed reveals tied to narration timestamps.
5. **Generated all remaining live-footage video** (Scenes 03, 04, 06, 07, 08 — 17 Seedance clips total across the production).
6. **Full assembly**: upscaled all 720p clips to 1080p, concatenated all scenes in order, built narration track, generated a new Suno score, mixed per the channel's locked LUFS/sidechain formula, appended the locked end card. Output: `Assembly/0002_Mantis_Shrimp_Color_Vision_FINAL_v1.mp4` (1920×1080, 2:32).

## Real spend
Scene 03: $2.03 (one regeneration for the environment-mismatch fix). Scene 04: ~$2.53. Scenes 06/07/08: video generation completed but exact total not itemized this session — check `Data/Generation_Log.json` if a precise figure is needed later. Suno track: $0.06.

## Grade
**B- / B** on the full assembled video (see `Data/Report_Card.md`) — scene-level content graded much higher (A-/A/A+) individually; the gap is the assembly method (direct ffmpeg concat instead of a proper hand-authored Remotion master composition per Phase 7) and general polish, not the generated content itself.

## Where to pick up next session
- Tony wants an **edit pass** on the assembled video — no specific list yet, he'll give notes when he reviews it.
- Open question worth raising: does this production get a real Remotion master composition (title cards, lower-thirds) built for it, or does the ffmpeg-concat assembly stand as final?
- Scene 05B's storyboard artwork itself was never regenerated (only Scene 05/05B got the *animation* treatment) — not an issue, just noting for context.
- New standing convention as of this session: **every finished video gets graded** (like this one) for a self-learning database — see `Global_Agent_Memory.md` and Claude cross-session memory for the rule.
