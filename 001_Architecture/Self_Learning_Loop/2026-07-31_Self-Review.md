---
title: "Self-Review — 2026-07-31"
type: self-review
created: 2026-07-31
---

# Self-Review — 2026-07-31

**What went wrong:**
- Shipped the first Glass Guard render with audible audio defects (clicks + clipped words) without catching it myself — I normalized loudness and QC'd the visual frame-by-frame, but never actually analyzed the audio waveform for edit artifacts before presenting it as done. The bug was fully mechanical and I had every tool needed to catch it (raw-PCM sample-diff scan) — I just didn't run it until Tony reported the symptom. **Lesson: after any hard audio edit (cuts, concats, trims), run a discontinuity scan before calling it done — don't rely on QC that only checks video frames and loudness numbers.**
- Told Tony "9184 has no usable content" based on vision analysis + my own frame checks, without considering that a cleaning product's own success (invisible, transparent glass) would produce exactly that "empty-looking" footage. Should have asked "what would this footage look like if the product worked perfectly" before concluding a clip was a misfire.
- Briefly mixed up NeonParcel's YouTube and TikTok Blotato account IDs while drafting a memory note — caught it before posting by re-checking TOOLBOX.md and the live API, but the initial memory-writing pass wasn't careful enough about which platform an ID belonged to.

**What worked well:**
- Independent verification before accepting Tony's grime-timestamp claim: pulled full-resolution frames myself rather than trusting the vision-model summary, which surfaced a real (if ultimately resolved-in-his-favor) discrepancy worth surfacing rather than silently complying.
- The audio bug diagnosis was fast and precise once prompted: astats → found an anomalous max-difference value → wrote a targeted sample-jump scanner → pinpointed exact click timestamps → correlated them to known edit boundaries → root-caused correctly on the first pass, no guessing.
- Immediately promoted the fix into the permanent skill (script + SKILL.md step) in the same session, before being asked to, once Tony signaled he didn't want to repeat the correction — matches the standing instruction to write fixes back into durable pipeline assets, not just this session's output.

**Recurring pattern worth automating:** this is the second product (after Colorsmart Pens) where `analyze_clips.py`'s scene-change detection undercovers handheld footage (1 frame per clip). The dense fixed-interval sampler I hand-rolled this session should probably become a real flag/mode on `analyze_clips.py` itself instead of a one-off scratchpad script recreated per session — worth doing next time this comes up a third time.

**Still open:** `compliance_vision_scan.py` false-positives on the promoted product's own branding every single time (2/2 products so far) — this is now a predictable, guaranteed flag, not an edge case. Worth fixing the prompt directly rather than continuing to manually resolve it on every product.
