# 2026-09-01 Session Log

## Neon Parcel Storyboard QA Resume

- Resumed from `.planning/RESUME-2026-08-31-STORYBOARD-QA.md`.
- Visually inspected the existing Shot 6 storyboard v1. It has four visible
  panels instead of six, blank caption bands, an open gate in the first panel,
  no bear in the first panel, and broken grandma/bear continuity across later
  panels.
- Ran a no-generation dry run through `storyboard_qa.py` using the Shot 6
  structured contract and a manually structured visual observation report.
  Result: `FAIL`, overall confidence `0.82`, with findings for missing subjects,
  incorrect gate state, blank captions, absent panels 5/6, broken chronology,
  and implausible transitions/physics. No provider or generation call occurred.
- Corrected the initial test invocation's module-path error and verified 9 QA
  tests pass.
- Implemented `storyboard_vision_provider.py` as the next pipeline layer. It
  builds an OpenRouter/Qwen request from the structured contract, attaches the
  local storyboard as a data URI, requires JSON, preserves raw responses, and
  fails on missing keys or malformed model output.
- Added 4 mocked adapter tests. Combined QA and adapter suite: 13 tests pass;
  compilation and `git diff --check` pass. The adapter's `--dry-run` was also
  verified with no network call.

## Next Action

Run the adapter against a mocked real-provider response through the complete
`inspect -> evaluate_report -> persisted QA report` path, then decide whether
Tony authorizes the first live OpenRouter inspection. GPT-Image generation is
still not wired and must remain untouched until this vision path is trusted.

## Glass Frog 0003 — Revision Round 1, block A executed (branch: glass-frog-0003-revision-round1)

Tony did a full watch-through and gave 23 notes + 8 pipeline items, all captured in
`Productions/0003_Glass_Frog_Transparency/Production/Revision_Notes_Round1.md`.
Tony said "yes please complete" → executed block A (Remotion-only, no cost, no re-watch):

- DiagramLabels.tsx: full rebuild to the reference aesthetic
  (Reference_Examples/Label_Aesthetic_Red_Blood_Cells.png) — big bold white term,
  accent parenthetical, drawing leader line + end dot, glowing target ring, black
  outline, collision avoidance, labelHoldS fade-out. Verified — matches reference.
- GlassFrogDoc.tsx: new DiagramShot model — same-image runs merged into one shot
  with one eased camera path ("remount jump" fixed); DiagramCamera per-segment
  ease-in/out; buildPath() dwell keyframes hold camera still under labels;
  DiagramScene cross-dissolves image changes; SceneVisual/SceneFade cross-dissolve
  scene boundaries (outgoing scene Freezes last frame for the tail, no loop, no
  bg bleed); NarrationTrack = hard-cut VO with 3-frame edge fades.
- SceneOverlay.tsx: callout type gets a 50%-black backing plate that fades/scales
  with the text.
- Verified: strict + generous black scans NONE, white scan NONE, tsc clean,
  full render OK.

NOT committed (working tree is messy with unrelated prior-session work; Tony
hasn't asked to commit). Left on the branch for review.

Remaining: scene 06B still on old label props (TODO); block B regenerations
(04D, 06A, 06F/G/H, map) need Tony's per-item approval + cost; block C audio pops
are a pipeline/mix fix (P6); P1-P8 pipeline changes pending.

## Neon Parcel Storyboard QA Mock Completion

- Ran the complete mocked provider-to-evaluator path: request construction,
  simulated vision response, raw-response preservation, and fail-closed QA.
- Result was `FAIL` with 50 findings and overall confidence `0.82`, matching
  the known Shot 6 v1 defects. No OpenRouter, GPT-Image, or Seedance call was
  made. The combined QA and adapter suite remains green at 13 tests.
- Next action is the first real OpenRouter/Qwen vision inspection of the
  existing Shot 6 v1 image only, pending Tony's authorization.

## Live Dual-Inspection Attempt

- Tony authorized inspection-only use of OpenRouter and requested Gemini as
  the primary inspector, Qwen as an independent second opinion, and mandatory
  manual review for Shot 6.
- Gemini completed successfully. Its report confirmed the wrong/missing
  subjects, gate-state and action errors, blank captions, and absent panels;
  after provider-alias normalization, the internal evaluator returned `FAIL`
  with 42 findings.
- Qwen returned HTTP 413 because the storyboard payload exceeded OpenRouter's
  request-size limit. The adapter now compresses oversized sheets to a 512px
  JPEG transport copy while retaining the original candidate for hashing, but
  a successful Qwen inspection still needs to be rerun.
- The combined result remains `manual_review`; no storyboard regeneration or
  Seedance call occurred. The manual-review policy currently exists as an
  explicit ensemble parameter and still needs production-config/CLI wiring for
  a user-facing on/off switch.

## Manual Review Policy Enforcement

- Added production policy file:
  `002_Content-Creation/Video_Editor/002_Channels/002_Neon-Parcel/Productions/0001_Grandma-And-Bear-Compilation/Production/Storyboard-QA-Policy.json`.
- Manual review defaults to enabled when no policy file is present. With the
  policy enabled, `storyboard_handoff.validate_handoff` refuses Seedance unless
  the manifest explicitly records `manual_review_approved: true`.
- With manual review disabled explicitly, a passing handoff may proceed only if
  provider reports agree; disagreement still forces manual review.
- Updated handoff and pre-video gate tests. Full relevant suite: 45 tests pass;
  compilation and whitespace checks pass.
