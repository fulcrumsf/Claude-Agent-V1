# Mantis Shrimp Color Vision (0002) — Iteration & Manual Override Log

Compiled 2026-08-24 from Report_Card.md, Generation_Log.json, session logs, feedback logs, and self-reviews (08-22 through 08-24). For each item, decide: **LOCK IN** (make this the new pipeline default), **ONE-OFF** (was just for this video, don't generalize), or **NEEDS MORE THOUGHT**.

Legend: **ITERATION** = took multiple attempts before the automated/documented pipeline succeeded. **MANUAL OVERRIDE** = Tony directly intervened/decided differently than what the pipeline did or was documented to do.

## Research / Pre-Production

1. ITERATION — Voiceover failed first attempt (deprecated ElevenLabs model `eleven_monolingual_v1`); fixed to `eleven_multilingual_v2`. *(bug fix, already correct)*
2. ITERATION — Character sheet gen appeared to time out; actually a polling bug (`status=='completed'` vs real `status=='success'`). *(bug fix, already correct)*
3. MANUAL OVERRIDE — Character sheet generated with no reference photo, breaking channel's own reference-first rule; approved as one-time test only.
4. MANUAL OVERRIDE — Character sheet used rigid 1:1 3×3 grid, clipped panels; approved as one-time test, permanent fix (16:9, non-uniform panels) already applied to the skill.
5. ITERATION — Storyboard `--input_urls` failed (needs public HTTPS, not local path); fixed via Cloudinary auto-upload. *(bug fix, already correct)*
6. Logged but not re-generated: scene_04 inconsistent eye detail; scene_06 storyboard produced 2 panels instead of 1 (flagged for future redo, not acted on).

## Scene Production

7. MANUAL OVERRIDE / ITERATION — Several shot lists (scenes 03,04,06,07,08) drifted from their storyboards; standing rule applied: always trust storyboard, rewrite shot list, never the reverse.
8. ITERATION — Scene_03E end-frame invented a different background; fixed by requiring end-frame gen to reference the start frame image, not just the storyboard panel. ($2.03 re-spend)
9. ITERATION — Scene 05 glowing assets had color-spill on standard chroma-green key; fixed by switching to near-black key for translucent/glowing assets specifically.
10. MANUAL OVERRIDE — Rejected varying the creature's own skin color across scenes (no biological basis); used water clarity/lighting/color-grade instead.
11. **MANUAL OVERRIDE — Full assembly done via direct ffmpeg concat + audio mix, not the documented Phase 7 Remotion master composition.** Tony's literal ask at the time ("I just want to see the final video"). This is the one still flagged open in feedback logs, and matches what you said earlier this session about diagrams being generated as assets then stitched with ffmpeg.

## Post-Assembly Review

12. MANUAL OVERRIDE (workaround) — Video-Analyzer only supports YouTube URLs; called internal Python functions directly to analyze the local file instead.
13. MANUAL OVERRIDE — Confirmed biology/continuity error (claw morphing) found but explicitly left unfixed — channel ruled entertainment-first, not documentary-grade.
14. ITERATION — Dropped two stock B-roll cutaways, restored original clip lengths; graded up B-/B → B+/A- on first rebuild.
15. MANUAL OVERRIDE (process error, self-corrected) — Feedback log got overwritten instead of appended once; fixed going forward to always Read-then-Edit append-only logs.

## Scene 05/05B Overlay Build (highest-iteration segment)

16. ITERATION (1/2) — Signal-code diagram regenerated via Seedance 2.0 from a literal text-to-image read of a verbal description; disliked, misunderstood the ask.
17. ITERATION (2/2, succeeded) — Regenerated via GPT-Image-2 image-to-image using the real existing asset as reference, animated via Seedance 1.5 Pro.
18. MANUAL OVERRIDE (preference, not a fix) — Two live-action clips generated (Seedance 2.0 vs 1.5 Pro) for comparison; picked the 2.0 version.
19. ITERATION (1st) — Label/arrow overlay used Gemini-vision grounded coordinates; disliked — labels ran off-screen / overlapped art despite factually correct anchors.
20. **MANUAL OVERRIDE — Tony's own suggested fix adopted as new standard: static PIL mockups on real extracted frames, shown for approval BEFORE any Remotion re-render** (replacing default render-and-review loop). This is the "diagram labeling method changed" item flagged earlier — already effectively locked in practice.
21. ITERATION — Within mockup stage: crest anchor + filter label corrected twice before any real render, per pixel-level feedback.
22. ITERATION — Real render round 1 confirmed 2/3 labels correct, self-caught one more gap (leader line vs text) before finalizing.
23. ITERATION (self-caught) — Wrong assumption about "fade at the very end" (literal last frame vs. real end-card boundary ~10s earlier); corrected before presenting.
24. ITERATION (method fix) — `ffmpeg -af astats` + grep gave silently wrong readings; switched to raw-PCM + numpy RMS, now the locked verification method.
25. ITERATION (bug fix) — Filter-ordering bug (`afade` after `adelay` targeting wrong timeline point) during CTA VO mix.
26. MANUAL OVERRIDE (one-off, confirmed) — Crossfade into signal grid slowed from ~2s to ~3.7s. Actual cause: removing a b-roll clip left a ~1s black gap between two fade-to-black diagram scenes; slowing the crossfade was the fix for that specific gap, not a general pacing preference. Not a pipeline-wide change.

*5 candidate versions (FINAL_v2 → v5) across two sessions to go from grade B-/B to A. Tony's own estimate: ~50% human-driven iteration to reach an A.*

## YouTube Package / Thumbnail

27. MANUAL OVERRIDE — Auto-generated title/description judged weak on sight, rewritten by hand before ever showing you.
28. ITERATION (1st) — Thumbnail overlay via PIL with hand-guessed coordinates; arrow landed on neck joint, clipped into headline text.
29. MANUAL OVERRIDE — You asked why the one existing finished thumbnail wasn't used as reference; turned out it was hand-built off-script in a past session, never actually produced by the pipeline script — exposed a latent gap.
30. ITERATION (2nd, succeeded) — Regenerated via GPT-Image-2 image-to-image edit instead of PIL — clean text/arrow.
31. ITERATION — One concept had a stray watermark; fixed with explicit no-logo instruction.
32. ITERATION (1st background pass) — Full image-to-image replaced entire background, made all 3 concepts look too similar, lost distinctiveness.
33. **MANUAL OVERRIDE — Correction: darken the real photo background ~50% instead of replacing it, keep per-concept glow variation, auto-headlines approved with no manual review needed going forward.** All 3 regenerated concepts approved and locked as Thumbnail Template v2.
34. MANUAL OVERRIDE — Confirmed (by reading live tool schema) Blotato has no A/B-test API path; you'll set up YouTube's native Test & Compare manually.
35. MANUAL OVERRIDE — Published as private (not public), only 1 of 3 concepts live; you'll add B/C variants and flip to public later.
36. Open/unresolved — Chapter timestamps not re-verified against the final v5 render's actual cut points before publish. **Still needs to happen before the video goes public.**

## Cross-cutting root cause (from Report_Card.md / Self-Review)

Nearly every iteration item above traces to the same root cause: **a plausible internal signal was trusted as the verified outcome instead of checking the actual rendered/measured artifact** — grounded coordinates ≠ correct layout, a verbal description ≠ the real asset, an `astats` reading ≠ real audio state, "the very end" ≠ the actual end-card boundary. This is already captured as a standing memory rule (`feedback_verify_before_presenting`).
