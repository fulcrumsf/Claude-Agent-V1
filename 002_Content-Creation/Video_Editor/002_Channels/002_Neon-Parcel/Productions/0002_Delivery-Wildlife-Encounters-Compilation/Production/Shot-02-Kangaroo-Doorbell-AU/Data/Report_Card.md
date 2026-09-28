---
title: "Neon Parcel Production Report Card"
type: report
domain: video-production
tags: [report, neon-parcel, video-production, seedance-2.0, environment-sheet]
---

# Neon Parcel Production Report Card

**Production:** Test Shot 03 — Kangaroo Doorbell (AU)
**Grade:** A
**Review date:** 2026-09-19

## Critique Notes

### Full 6-beat action clip (`Seedance_v1_Full_Action_Test.mp4`)

**Grade: A**

First-attempt success on the hardest shot type this pipeline has run so far
— fixed-camera doorbell POV, two distinct subjects (one human, one animal),
six sequential action beats, strict continuity constraints (bag never set
down, kangaroo never touches the letterbox, driver's feet on the correct one
of three named ground surfaces, exactly one of each subject throughout).
Verified frame-by-frame (not just from the generation log): subject count
correct in every checked frame, food item correctly separated from the bag,
car stationary and correctly oriented the entire clip, hedge line intact on
both sides, kangaroo enters screen-left clear of the letterbox, both subjects
visible together during the watch beat, driver exits screen-right at the end.

**One soft note, not a regeneration blocker:** the kangaroo holds its mid-hop
pose fairly static for ~2s during the watch beat (00:08–00:11) — reads
slightly staged rather than a natural weight-settling motion. Flagged for
awareness; did not affect the A grade because every hard constraint held and
the overall result reads as genuine found footage.

**This result is the first confirmed end-to-end success of the full
"environment sheet + multi-character-sheet, single Seedance 2.0 call"
recipe** — see `Seedance-Prompting-Guide/SKILL.md`'s "Confirmed recipe"
section (added 2026-09-19) for the exact reusable process. Everything in
that recipe should be the default starting point for the next shot of this
type, not re-derived from scratch.

## Pipeline Readiness Status

**Current readiness:** Environment-sheet generation order, depth/extent/
orientation checking, and the full Seedance multi-reference action-sequence
recipe are now all confirmed and locked into their respective skills. Next
gap: the kangaroo's staged-pause motion quality — worth a targeted note in
the Grounding Audit's motion-naturalness check if it recurs on a future
shot.

**Next phase:** Tony's call on whether to proceed to the full production
render of this shot, or treat Test Shot 03 as complete and move to the next
Diversity Matrix test.
