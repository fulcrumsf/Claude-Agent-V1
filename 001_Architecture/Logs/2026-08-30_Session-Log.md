## Session Summary

- Investigated the Shot 8 Neon Parcel failure: the multi-panel storyboard was
  submitted as `first_frame_url`, so Seedance rendered the storyboard as the
  video content instead of using it as visual-continuity context.
- Implemented an API-boundary fix in
  `001_Architecture/Tools/Video-Generation/Generic_Tools/kie_market_api.py`:
  `reference_image_urls` and `first_frame_url` are separate fields, and invalid
  combinations are rejected before a provider request.
- Updated the Neon Parcel batch runners, pre-video validator, Neon Parcel
  skill, and shared Seedance prompting guide.
- Added five regression tests covering correct routing, invalid combinations,
  and storyboard-as-start-frame rejection.
- Verification passed: 22 Neon Parcel tests, 5 wrapper tests, Python compile
  checks, and `git diff --check`.
- Graphify refresh was attempted but the installed `graphify` 0.4.2 CLI does
  not provide the documented `update` command; it only exposed install/query/
  hook commands, so no graph refresh was performed.

## Neon Parcel Storyboard Corrections

- Tony confirmed that the active v1 outputs for Shots 06, 08, 09, 10, 11, and
  12 visibly opened on their storyboard sheets and authorized regeneration.
- Regenerated all six with versioned prompts and corrected routing. Shots 06,
  09, 10, and 12 completed as v2 using `reference_image_urls`; Shots 08 and 11
  still rendered storyboard content despite that correct field and were
  targeted with clean-start fallbacks.
- Shot 08 completed as v3 using its existing clean single-scene start frame.
  Shot 11 required a v4 after its first crop retained storyboard fragments;
  the final v4 uses an exact text-free first-panel crop and passed visual
  opening-frame inspection.
- Every current replacement is normalized to 1920x1080 through Topaz 2x and
  FFmpeg. Each superseded prompt, raw clip, upscale, and final render was
  preserved in the matching archive folder, with exactly one current version
  left in the active `Video_Clips/` folder.
- Added resumable regeneration scripts for the v2 batch and targeted v3/v4
  fallbacks. Fixed the pre-video gate false positive that rejected explicit
  negative overlay constraints; 23 Neon Parcel tests and 8 pre-video tests
  passed.
- At the time of the initial summary, no new paid generation had been
  submitted; this was superseded later in the session by the authorized v2/v3/v4
  correction batch documented above.

## Review Scope Update

- Tony flagged Shots 06, 08, 11, and 12 for later review because their issues
  are major. Shots 09 and 10 are accepted despite minor nuance problems.
- Defer discussion, regeneration, or editorial changes to the four flagged
  shots until Tony returns to them. The later v2/v3/v4 regeneration work and
  its task IDs are recorded in the `Neon Parcel Storyboard Corrections` section
  above.

## Storyboard QA GSD Phase 1

- Bootstrapped a focused GSD planning project for Neon Parcel storyboard QA
  after mapping the brownfield workspace.
- Defined four phases: structured storyboard contract, visual QA, capped
  regeneration, and validated Seedance handoff.
- Implemented Phase 1 locally: provider-neutral storyboard schema validation,
  stable prompt rendering, Shot 6 regression fixture, QA acceptance checklist,
  and skill documentation updates.
- Verification: 28 focused Neon Parcel tests passed, Python compilation passed,
  and `git diff --check` passed. No paid generation was used.
- Git commit was unavailable because the repository index is read-only in this
  session; planning and implementation files remain present and verified.

## Storyboard QA GSD Phase 2

- Implemented the provider-neutral storyboard vision QA evaluator in
  `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/storyboard_qa.py`.
- The evaluator requires explicit evidence for every frame and adjacent-frame
  check, records candidate/contract hashes, and fails closed on missing,
  ambiguous, malformed, or low-confidence evidence.
- Added mocked Shot 6 regression coverage for missing bear, wrong gate state,
  broken transitions, implausible physics, caption ambiguity, and missing
  panels. Added a minimum-confidence rule that downgrades weak apparent
  passes to manual review. 37 focused Neon Parcel tests pass.
- No paid image/video generation was used. Phase 3 is the next planned step:
  the three-candidate regeneration/archive/blocking loop.

## Storyboard QA GSD Phase 3

- Implemented the append-only storyboard attempt controller and injectable
  generation/QA loop in `storyboard_regeneration.py`.
- Enforced the three-candidate hard cap, prior-QA sequencing, retry context from
  actual findings, non-destructive archive/promotion, and Seedance-blocking
  terminal states.
- Added mocked fail/fail/pass, fail/fail/fail, provider-failure, cap, and
  incomplete-QA coverage. 44 focused Neon Parcel tests pass.
- No paid image/video generation was used. Phase 4 validated Seedance handoff
  is next.

## Storyboard QA GSD Phase 4

- Implemented `storyboard_handoff.py`, requiring a selected passing storyboard
  manifest and converting validated frame sequences into the existing five-layer
  Seedance prompt contract.
- Extended the Neon Parcel pre-video gate to reject missing, failed, or
  manual-review storyboard handoffs and to verify the storyboard reference URL.
- Preserved the separate storyboard `reference_image_urls` and clean temporal
  `first_frame_url` roles. 51 Neon Parcel tests and 5 generic wrapper tests pass.
- The complete four-phase storyboard-QA workflow is implemented locally; no
  provider or paid generation calls were made.

## Session 2 — Glass Frog edit review continued + AW clip-duration pipeline fix

- Glass Frog 0003 Remotion edit review: fixed the remaining systemic VideoSeg
  duration mismatch (Tony chose "fix all 12"). scene_04 + scene_06 clips now laid
  out in whole frames at floor(real ffprobe) via new `F()` helper in
  GlassFrogDoc.tsx; synthetic segs absorb slack; scene totals still locked to
  audio. Verified frame-by-frame at the two worst cuts (04D→04E, 06D→06E). No
  re-render of the final MP4 (Tony: pipeline-only this session).
- Root-caused why the "generate at floor, then trim" rule wasn't followed: it was
  prose-only, no code enforced it; AW has no dedicated clip-gen script, clips are
  generated freehand per beat; planners set generation_duration_s = target.
- Built the enforcement:
  - NEW `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/clip_durations.py`
    — `request_duration(target, model)` = ceil(target)+1 clamped to model [4,max];
    `trim_to_target()` head-trims to target and refuses (no output,
    INSUFFICIENT_FOOTAGE) when real footage < target. + `test_clip_durations.py`.
  - `pipeline_supervisor.py`: sends `gen_request_duration(entry)` to Kling/Seedance
    instead of raw `duration_s`; `preloop()` is target-aware (trims to
    target_duration_s, hard-fails short footage); `run()` aborts if any video
    entry lacks `target_duration_s`; clip_manifest.json records
    target/real_generated/final_trimmed per clip. + `test_pipeline_supervisor_durations.py`.
  - Docs: AW SKILL Phase 6A + Phase 7 rule, Production-Asset-Planner Step 6,
    Seedance-Prompting-Guide floor section — planners now record target only.
  - 17 new tests pass; validate_build passes on all 7 touched files; pre-existing
    AW tests unaffected (test_generate_youtube_package's cloudinary import error
    is pre-existing, unrelated).

### Session 2 cont. — freeze-fill fallback + diagram black-frame fix (2nd pass)

- Tony's design call: NEVER regenerate a short clip (cost), NEVER loop. Padding
  should get it right first time; freeze-frame-with-slow-dissolve is the only
  fallback, and hand the shortfall to an adjacent synthetic segment when possible.
- Also flagged: "lots of black frames in the current video." Found the cause —
  scenes 03 & 05 had ~8 inter-DiagramSeg gaps each (0.2-0.8s) rendering only the
  #0B0F1A fill. Was in the original assembly, not the loop fix.
- Built:
  - `clip_durations.trim_to_target`: short footage → keep clip at real length,
    set needs_fill + shortfall_s, never fail/refuse. `pipeline_supervisor.py`:
    short clip → manifest status `ok_short`, notify once, continue (no retry,
    no regen).
  - GlassFrogDoc.tsx: `renderDiagramChain(segs, sceneEndS)` makes every DiagramSeg
    contiguous (holds final camera position, no gap) — applied to scenes 03 & 05,
    refactored their seg lists into S03_SEGS/S05_SEGS arrays. Verified: former
    navy gap frames now hold the diagram.
  - GlassFrogDoc.tsx: `VideoSegFilled` — plays clip for real length then
    `<Freeze>`-holds last frame with eased FadeOutTail dissolve. Replaced scene_02's
    manual PNG FreezeFrame/FreezeSeg (removed, + unused Img import). Verified
    frames 305-350: clean, no flash, no black.
  - SKILL Phase 6A + Phase 7: no-regen/no-loop freeze-fill rule; "no background/
    black frames — segments contiguous 0→audio-length" mandatory rule + pre-Phase-8
    black-frame scan.
- 17 pipeline tests pass; Remotion tsc clean; validate_build passes.

- Ken Burns on held frames (Tony: "slow zoom and slow pan, nicer than frozen, no
  black"): new `KenBurns` wrapper in VideoSegFilled applies a shared very-slow
  push+drift to both the fading clip and the <Freeze>, ramping in from the
  dissolve point; pan clamped to what the zoom covers so no edge/black shows.
  `renderDiagramChain` appends a gentle continuation keyframe so held diagram
  cameras keep breathing too. tsc clean; rendered frames 305-360 — full frame,
  no black edges, motion continuous through the freeze.
