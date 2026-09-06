---
title: "Self-Review — 2026-09-03"
type: self-review
domain: architecture
tags: [self-learning, review]
---

# Self-Review — 2026-09-03 (Glass Frog 0003 revision, Rounds C + 9/10 + R2-1..R2-7)

## What went well
- **Verify-before-presenting held up repeatedly.** Block C: the "3 VO pops" were
  diagnosed by RESUME_NOTES as a live defect; extracting the actual PCM showed the
  render was already clean and the real bug was a dormant pipeline hard-concat.
  Saved a wasted re-mix. R2-4: the band artifact Tony saw was invisible on stills
  — only a frame-by-frame pull from the *encoded* output confirmed root cause
  (two live OffthreadVideos).
- **Turning "locked prose rules" into code chokepoints.** Block C produced
  `audio_pop_scan.py` as a real gate, not another paragraph in a SKILL. Same
  pattern as the 2026-08-30 clip_durations lesson.
- **Showing prompts before spending.** Frog photo + Suno score both went to Tony
  as a prompt first; both landed on the first generation.

## What to do better
- **The Remotion scene-content structure fought back three times.** scene_04 /
  scene_06 hard cuts (R2-5), the OffthreadVideo tear (R2-4), the 06F→06G timing
  (R2-4) — all because each scene's content was hand-wired as ad-hoc Sequences
  with no shared crossfade/duration primitive. `ChainScene` now exists but only
  covers 04 + 06 front. **The whole composition should be one chain model** — that
  refactor is overdue and would have prevented R2-4 and R2-5 both. Flag for
  whoever does the "0.5s crossfade default in assemble.py" Block D item — do it
  properly as a reusable primitive, not per-scene.
- **Pipeline gaps that only surfaced under review, not during the autonomous run:**
  (1) Suno prompt never persisted; (2) `generate_audio:true` on the Block B regen
  produced clips with no audio stream and nobody noticed until the mix; (3) no
  limb-deformation check on generated clips. All three are "the autonomous run
  reported success but a human review found the hole." → Block D should add
  post-generation assertions for each.
- **Audio was treated as an afterthought.** FULL6..FULL13 were all narration-only
  for ~4 days of review because the mix was "later." Tony judged edits without
  score/pacing context the whole time. Next production: get a rough three-layer
  mix in early so review happens against something close to final.

## Recurring
- Tony's aesthetic notes almost always = "less stylized, more real / more
  grounded" (real basemap not squiggle; real frog photo; scientific not
  mysterious score; gentler more natural duck). The pipeline defaults skew too
  "designed." Worth encoding as a channel-level bias.
