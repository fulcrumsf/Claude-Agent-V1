# Resume Point: Neon Parcel Storyboard QA

Date paused: 2026-08-31
Project: Neon Parcel storyboard QA and validated Seedance handoff
Production: `002_Content-Creation/Video_Editor/002_Channels/002_Neon-Parcel/Productions/0001_Grandma-And-Bear-Compilation`

## Current State

- The four-phase GSD design and local implementation are complete: structured storyboard contract, fail-closed visual QA, capped regeneration, and validated Seedance handoff.
- Verification passed: 51 focused Neon Parcel tests, 5 generic wrapper tests, Python compilation, and `git diff --check`.
- No provider call or paid storyboard/video generation was made for this QA implementation.
- The local safeguards are implemented, but the live vision-provider adapter and GPT-Image generation wiring are not yet complete. Do not describe this as live end-to-end verified.
- Git commits were not created because the repository index was read-only. Do not claim a commit exists.

## Exact Next Step

Run a no-generation dry run against the existing bad Shot 6 storyboard v1 before spending credits.

Candidate image:
`/Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/002_Channels/002_Neon-Parcel/Productions/0001_Grandma-And-Bear-Compilation/Images/Shot-06-Storyboard-v1.png`

Contract fixture:
`/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/shot_06_storyboard_spec.json`

The dry run must confirm the evaluator can identify:

- Frame 1 has the bear already present behind a closed gate.
- The gate is closed before the opening action.
- Grandma does not appear before the contract says she enters.
- The bear and grandma do not appear or disappear without a causal transition.
- The gate opening, bear gesture, walking-around action, and final positions are physically coherent.
- Caption text is exact or explicitly marked ambiguous/failing.

Do not generate a replacement storyboard or video during this first dry run.

## Work Still Required

1. Build a real vision-provider adapter using the existing OpenRouter/Qwen vision pattern. Attach the storyboard sheet, submit `build_inspection_prompt(spec)`, require JSON, and preserve the raw response for audit.
2. Add adapter tests for malformed JSON, missing panels, low confidence, and a Shot 6 failure report.
3. Decide whether the first real inspection may use a live vision call. It may incur a small provider charge even though it is not image/video generation.
4. Wire the GPT-Image storyboard generation path into `run_storyboard_loop` only after the dry-run QA result is trusted.
5. Keep the hard cap at three candidates. Attempts 2 and 3 require QA of the prior candidate. After attempt 3 fails or remains ambiguous, block Seedance and flag the shot.
6. Add explicit observed fields to the QA report, such as `observed_subjects`, `observed_object_states`, `observed_actions`, `observed_spatial_relationships`, and `observed_caption`. The Seedance handoff should use these observations, or a documented contract-plus-observation merge, so it is grounded in the accepted image rather than merely restating assumptions.
7. Run one controlled real storyboard regeneration on Shot 6 only after provider wiring is verified. Archive every failed candidate and leave only the selected current candidate active.
8. Build and validate the handoff manifest, then run the pre-video gate. Route the storyboard through `reference_image_urls`, never `first_frame_url`.

## Do Not Touch Yet

- Do not alter active outputs for Shots 6, 8, 11, or 12 until Tony requests changes.
- Do not regenerate Shots 9 or 10; Tony allowed those to pass.
- Do not reuse a storyboard sheet as a temporal first frame.
- Do not spend three generations automatically without QA between attempts.

## Resume Context

Start by reading this file, `.planning/STATE.md`, the latest session log, and the Neon Parcel tool files above. Then inspect the existing Shot 6 storyboard image before writing the provider adapter or making any paid call.
