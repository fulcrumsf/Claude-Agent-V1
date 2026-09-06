---
title: "Neon Parcel Compilation Review Updates Plan"
type: implementation-plan
category: video-production
tags:
  - neon-parcel
  - video-pipeline
  - humor-calibration
  - review-process
status: approved-implementation
created: 2026-08-27
---

# Neon Parcel Compilation Review Updates

Tony approved implementation of this update set before revising the current
shot concepts. Shot revisions remain a later phase.

## Confirmed Rules To Preserve

- Seedance 1.5 Pro at native 1080p bypasses Topaz.
- Seedance 2 Mini at 480p uses Topaz 2x, then FFmpeg normalization to
  1920x1080.
- A provider prompt is submitted only once per shot/version unless the
  provider fails, the output is corrupt, or Tony explicitly requests a
  revision.
- Exact prompts are saved before submission and linked to provider task IDs.
- Text overlays, captions, labels, emojis, watermarks, and title graphics are
  added in post-production, never inside image or video prompts.

## Review Findings To Convert Into Rules

1. Add pre-video visual-realism review after reference-image/storyboard
   creation. Reject synthetic-looking anatomy, fur, lighting, shadows, or
   obvious 3D-render appearance.
2. Add pre-video camera-plausibility review. Validate the claimed capture
   source, physical camera placement, framing, lens character, and whether the
   footage looks like a real recording rather than a commercial shot.
3. Require a meaningful visual beat: readable setup, development, and outcome;
   repeated actions need escalation or a clear contextual reason.
4. Strengthen humor-context review after Tony completes the current humor
   discussion. The review should favor believable absurdity, causal dialogue,
   sincere human logic, and visible outcomes over invented punchlines.
5. Use the Benny case study's recurring-premise structure and recording style
   as inspiration without copying its exact characters, dialogue, overlays,
   sequence, or distinctive framing.

## Implementation Sequence

### Phase 1: Finish Calibration

- Complete Tony's review of the Benny reference and the paused five-shot batch.
- Record approved positive and negative examples with the reason for each.
- Resolve the humor-context rubric before coding it.

### Phase 2: Pre-Video Gates

- Add realism, camera plausibility, and meaningful-beat checks after image or
  storyboard generation and before any paid video request.
- Require manual review when any gate is uncertain.
- Keep failed reference assets and explanations for later calibration.

### Phase 3: Cost And Audit Controls

- Add an enforced generation-log preflight lock.
- Block duplicate shot/version submissions unless a permitted retry or explicit
  revision is recorded.
- Add source-resolution validation that blocks Topaz for native 1080p inputs.
- Store exact prompts, references, parameters, provider task IDs, and retry
  reasons in immutable versioned files.
- Keep raw and processing intermediates outside the active `Video_Clips`
  directory.

### Phase 4: Post-Production Separation

- Keep all titles, captions, ranking graphics, emojis, and watermarks in a
  post-production overlay specification and render layer.
- Ensure generation prompts describe only the scene, camera, action, and native
  audio.

### Phase 5: Shot 4 Revisit

- Rewrite Shot 4 only after the humor-context rubric is approved.
- Require a new prompt archive entry and pre-video gate results.
- Generate one paid revision only, then wait for Tony's review.

### Phase 6: Verification And Re-Entry

- Run automated tests for routing, resolution, prompt archival, duplicate-task
  blocking, and overlay separation.
- Perform one end-to-end dry run without provider submission.
- Resume the production workflow only after Tony approves the update set.

## Current Status

- Phase 1: approved and recorded
- Phase 2: implemented
- Phase 3: implemented
- Phase 4: implemented
- Phase 5: waiting for humor-context decision
- Phase 6: verified by automated tests and config checks; end-to-end provider dry run remains intentionally unsubmitted
