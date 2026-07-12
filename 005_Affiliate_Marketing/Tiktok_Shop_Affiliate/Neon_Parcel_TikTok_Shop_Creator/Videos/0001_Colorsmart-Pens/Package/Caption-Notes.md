---
title: "Colorsmart Pens — Caption Notes"
type: posting-notes
created: 2026-07-12
---

# TikTok_V1/V2/V3.mp4 — Ready to Post (pending caption)

**Required before posting, all 3 videos:** Add `#ad` or `#sponsored` to the
caption/on-screen text (RULE-008 disclosure — not embedded in the video
itself, see Compliance/Ledger-Scan-Results.md — none of the 3 scripts
include a spoken disclosure).

**Also required at posting time, all 3 videos:** Attach the closed-loop
TikTok Shop product anchor link (RULE-010 — a platform posting step, not a
video-file concern).

## Compliance gate results

| Video | Audio | Phase 1 | Phase 2 | Phase 3 Transcript | Phase 3 Vision |
|---|---|---|---|---|---|
| V1 | Script1 | Pass (RULE-008 action item) | Skipped (Tony's direction) | CLEAR | FLAG → resolved false positive (own-product label) |
| V2 | Script2 | Pass (RULE-008 action item) | Skipped (Tony's direction) | CLEAR | CLEAR |
| V3 | Script3 | Pass (RULE-008 action item) | Skipped (Tony's direction) | CLEAR | FLAG → resolved false positive (own-product label) |

Full detail per video in Compliance/Ledger-Scan-Results.md and the individual
Compliance/Vision-Scan/ and Compliance/Transcript-Scan/ reports.

## Shot variation across the 3 videos

Each uses a genuinely different cut (not the same edit with swapped audio):
- **V1** (4 beats, 15.7s): rock chips (IMG_9190) → sanding (IMG_9187) → painting (IMG_9192) → mismatch/result zoom (IMG_9194 image) → CTA hero (IMG_9192)
- **V2** (3 beats, 15.0s): rock chips ×2 angles (IMG_9189 + IMG_9187) → mismatch/result zoom (IMG_9194 image, slower pace) → CTA hero (IMG_9191, different clip than V1's CTA)
- **V3** (5 beats, 14.4s): rock chips/prep (IMG_9188) → painting (IMG_9192, different window than V1) → mismatch/result zoom (IMG_9194 image, faster pace) → reflective cutaway (IMG_9186) → CTA hero (IMG_9192, different window than V1's CTA)

All 3 reuse the `IMG_9194` zoom-in for the "doesn't perfectly match" beat since
it's the only asset that actually shows the painted result — intentional per
Tony, not a duplication gap.

## Audio loudness normalization

Raw VO originally measured -34 to -35 LUFS integrated (no clipping risk, just
too quiet for TikTok's ~-14 LUFS norm). All 3 final videos re-muxed with
`normalize_loudness.py` (now a permanent pipeline step, SKILL.md Step 5a.5):

| Video | Integrated Loudness | True Peak |
|---|---|---|
| V1 | -14.15 LUFS | -1.42 dBTP |
| V2 | -13.80 LUFS | -1.37 dBTP |
| V3 | -14.24 LUFS | -1.43 dBTP |
