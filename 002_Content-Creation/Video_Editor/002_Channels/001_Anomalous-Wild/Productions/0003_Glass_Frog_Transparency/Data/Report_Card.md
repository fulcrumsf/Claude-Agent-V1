---
title: "Video Report Card"
type: report
domain: video-production
tags: [report, video-production, content-creation]
---

# Video Report Card
**Channel:** Anomalous Wild
**Video:** 0003 — Glass Frog Transparency ("The Frog That Hides Its Own Blood to Disappear")
**Grade:** **A** (Tony, 2026-09-04 — "an A, almost an A+, just not quite")
**Previous Grade:** — (original autonomous cut never formally graded; superseded)
**Review Date:** 2026-09-04 (Block E)
**Approved cut:** `Renders/FULL16_v2a_cta-matched.mp4` → published private as
`https://www.youtube.com/watch?v=JMn32MmAzWw` (replaces the earlier private
`LiJcg5aUu6I`, which Tony deletes manually). Canonical copy:
`Renders/0003_Glass_Frog_Transparency_FINAL_v2a.mp4`.

**This is the Anomalous Wild gemstone / milestone reference video** — see
`Production/Milestone_Reference.md`. Use it as the worked example of how an AW
video should be made.

---

## Block E — final grade (2026-09-04)

**A, just short of A+.** Full 23-note revision + Round 2 (R2-1…R2-7) all landed and
were approved shot by shot. What earned the grade:

- **Edit: "perfect"** (Tony's word). 0.5s cross-dissolve on every cut, camera holds
  under every diagram label, the 06F→06G→06H vanish reworked to be tear-free,
  scene-03 real glass-frog photo cutaway, real Natural Earth range-map basemap.
- **Audio: A-grade.** New pipeline: **video-to-audio ambience** (fal.ai Mirelo SFX
  v1.6, motion-conditioned, 6 segments crossfaded) at −25 LUFS sitting just under
  the Suno track-2 science-doc score (−22 LUFS + sidechain duck), narration −14.
  CTA VO re-normalized to −14 to match the body VO exactly.

### What kept it from A+ (not defects — headroom for next time)
- Scene 06F ~3:32 toe-count morph (below) — let pass, but an A+ cut wouldn't have it.
- Diagram sections (scene 3, scene 5) still lean long; ambience there is very thin
  by necessity.

### Iteration cost (the lesson — see hardening list below)
Reaching A took ~6 review rounds (FULL10→FULL16) after the "done" call, over
transition timing (×3), an anatomy artifact, audio-mix tuning, and a CTA-level
miss. Each was a class of check that should run *before* a cut goes to Tony.

### Known issues Tony flagged but chose to let pass (do NOT re-open without him asking)

### Known issues Tony flagged but chose to let pass (do NOT re-open without him asking)

- **Scene 06F (~3:32), frog crawling on the leaf** — as the frog moves, its front
  foot morphs from ~3–4 toes down to a single toe for part of the shot. Real
  Seedance generation artifact. Tony (2026-09-03): "I'll let it pass," but noted
  it because he expected a limb/deformation checker to have caught it.
  → **Gap:** there is no per-frame limb/deformation check on *generated video
  clips*. The existing checks are: the character-sheet count-check on
  *storyboards* (Storyboard-Generation), and P8's shot-boundary detector (internal
  cuts only). A generated-clip anatomy/limb sanity pass is not built. Candidate
  for a future pipeline item (relates to P2/P7/P8). Logged here per Tony.
