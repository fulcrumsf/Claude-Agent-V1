---
title: "Neon Parcel Production Report Card"
type: report
domain: video-production
tags: [report, neon-parcel, video-production, seedance-2.0-mini, environment-sheet]
---

# Neon Parcel Production Report Card

**Production:** Shot 03 — Moose Dash-Cam (Northern Ontario, CA)
**Grade:** C
**Review date:** 2026-09-19

## Critique Notes

### Full action clip (`Seedance_Mini_v1_Full_Action_Test.mp4`)

**Grade: C — passes.**

First full multi-reference action shot run on Seedance-2-Mini for this
pipeline, using the same recipe confirmed on the standard tier for Shot 02
(environment + character sheet references, ordinal `@ImageN` tagging,
timestamped action beats, inline continuity constraints). Verified
frame-by-frame: moose calf enters from the left treeline gap, crosses in
front of the stopped van, exits right into the opposite treeline, road
clear at the end. Calf stayed antler-free and correctly proportioned
(gangly build, ~4-5 ft shoulder height relative to the van) throughout, no
duplicate animals, no stray subjects, van never visibly rendered (matches
the locked no-exit safety constraint).

**Honest framing of the grade:** C reflects Mini's real quality tier
relative to standard Seedance-2's A-grade result on Shot 02 — a genuine,
accepted step down in visual fidelity, not a list of specific defects.
Tony's own words: *"I'll grade that a C. It passes."* No itemized critique
beyond the grade was given.

**This result locked in a real pipeline default change:** given the
roughly 80-90% cost reduction per second versus standard Seedance-2 at
matching resolution, Tony directed that Seedance-2-Mini (via
`kie_market_api.py`, not `kie-cli`) becomes the **default** model for every
new Neon Parcel shot going forward — see `Video_Editor/CLAUDE.md`'s Video
preference order and `Seedance-Prompting-Guide/SKILL.md`'s "Mini confirmed
and now the locked default" section. Standard Seedance-2 remains available
as a deliberate, stated upgrade for a specific shot that needs it, not a
silent fallback.

## Pipeline Readiness Status

**Current readiness:** Environment-sheet generation order, the road/
natural-landscape adaptation of the 3-panel process, the Grounding Audit
(including a real mid-audit terminology correction — "yearling" fixed to
"calf, ~6 months" — caught before the character sheet was generated), and
the Mini-tier multi-reference recipe are all now confirmed and locked.

**Next phase:** Diversity Matrix cell selection for the next shot in this
compilation.
