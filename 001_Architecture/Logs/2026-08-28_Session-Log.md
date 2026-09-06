# Session Log — 2026-08-28

## Neon Parcel Pause State

- Production: `0001_Grandma-And-Bear-Compilation`
- Shot 1: storyboard-based Seedance 2 Mini test approved and finished as active `Video_Clips/Shot-01-1080p-v3.mp4` at 1920x1080.
- Shot 2: storyboard-based Seedance 2 Mini test approved and finished as active `Video_Clips/Shot-02-1080p-v4.mp4` at 1920x1080.
- Shot 3: storyboard-based Seedance 2 Mini direction test approved despite direction mismatch and finished as active `Video_Clips/Shot-03-1080p-v3.mp4` at 1920x1080.
- Shot 4: corrected unaware-to-discovery storyboard-based Seedance 2 Mini test approved and finished as active `Video_Clips/Shot-04-1080p-v3.mp4` at 1920x1080.
- Superseded Shot 1 v2 artifacts were moved to matching archive folders.
- All unapproved tests remain archived; no source artifacts were deleted.

## Locked Decision

Tony provisionally graded the new Neon Parcel video route 89/B+ based on direct
review, versus C- for the previous mixed route. The Neon Parcel default is now:

`Storyboard -> Seedance 2 Mini 480p -> Topaz 2x -> FFmpeg 1920x1080`

Seedance 1.5 is an explicit fallback/comparison route only. This decision is
Neon Parcel-specific and does not change other channel pipelines.

## Next Step

The pipeline is paused for discussion. Do not start another generation until
Tony gives the next instruction. Likely next work is reviewing the remaining
production plan, then applying the new default to future shots rather than
rerunning already approved clips.

## Important Learning

- Storyboard references improved results substantially but did not reliably
  control vehicle travel direction; prompts must define physical orientation,
  lane relationship, front/rear, entry edge, exit edge, and continuous motion.
- Storyboards are visual-continuity references, never literal panel layouts.
- The exact Seedance prompt must be saved before every paid request using the
  Neon Parcel prompt contract.

## Cross-Project Framework Work

- Created `001_Architecture/Superpowers/Specs/2026-08-29-Iterative-AI-Production-Framework.md` as a channel-agnostic design document for Tony's build-test-observe-diagnose-revise workflow.
- The framework documents intentionality, saved inputs, one-version/one-provider-call controls, whole-result review, precise failure classification, non-destructive archiving, approval calibration, learning promotion, and staged autonomy.
- It is a working architecture specification, not yet an active global skill.
