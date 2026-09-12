# Gate 3 Review — Configurable Subject-Aware Reframing

Date: 2026-09-09. Status: built and automatically verified; Tony's normal-speed
visual review is pending. The current candidate is `Gate-3-Run-002/`.

## Start with the comparison

- [Side-by-side comparison](Gate-3-Run-002/Framing-Comparison-v1.mp4)
- [Hybrid vertical candidate](Gate-3-Run-002/Part-3-Hybrid-v1.mp4)
- [Group vertical candidate](Gate-3-Run-002/Part-3-Group-v1.mp4)
- [Subject vertical candidate](Gate-3-Run-002/Part-3-Subject-v1.mp4)
- [Framing debug video](Gate-3-Run-002/Framing-Debug-v1.mp4)
- [Hybrid contact sheet](Gate-3-Run-002/Framing-Contact-Sheet-v1.jpg)
- [Crop plan](Gate-3-Run-002/Crop-Plan-v1.json)
- [Job and settings](Part-3-Framing-Job-v1.json)
- [Verification](Gate-3-Verification-v1.json)
- [Test results](Gate-3-Test-Results-v1.txt)

## What was built

One global engine, independent of Neon Parcel, now supports:

| Mode | Behavior in this comparison |
|---|---|
| Group | Retains the full 16:9 source inside 9:16 over a dimmed blurred background. |
| Subject | Tracks one selected subject and alternates subjects using the configured 3.5-second schedule. Falls back to a wide view when the subject or camera movement cannot fit safely. |
| Hybrid | Combines subject crops and group views. Uses a 3.5-second subject / 2.5-second group cycle once multiple subjects are established, and keeps the ending two seconds of each multi-subject scene wide. |

Profiles, per-video settings, and per-shot overrides are supported. The shared
JSON job interface has `plan`, `render`, and `reframe` commands. The guide is
`001_Architecture/Tools/Video-Generation/Generic_Tools/Subject-Aware-Reframer/Job-Contract-v1.md`
in Agent-OS. No new dependency or model was installed for Gate 3.

The planner uses the already-verified family-aware detection cache. It bridges
short gaps, uses limited look-ahead, suppresses small camera movements, limits
continuous pan/zoom speed, and resets at cuts. It validates source bounds and
coverage of the chosen subject. Group views preserve the full source; individual
views can intentionally exclude other subjects.

## What changed during review

The initial render included brief crop returns between wider views and a late
switch away from the hose scene's ending group view when the animal exited.
The revised planner suppresses crop returns shorter than 1.5 seconds beside a
wide view and remembers that a scene has multiple subjects. The end-group hold
therefore persists when a detection disappears.

The original first run was preserved under
`Archived/Gate-3-Run-001/`; its archive receipt verifies every original file.
Gate 2 baseline/audit material remains available for comparison.

## What to assess

- Doorway: the hybrid opens around the doorway, follows Grandma as she emerges,
  then widens for the interaction. The source begins before Grandma is visible;
  look-ahead positions the camera but does not invent an earlier appearance.
- Hose: check whether the individual bear and Grandma views reveal the action
  at the right moments. A bear that is too wide for a safe crop triggers the
  configured group fallback.
- Trampoline: compare the single-subject views with the wider ending that
  includes Grandma and the bears. Whole-scene fitting makes subjects smaller.
  This is the intended tradeoff for keeping the entire group visible.

The first hybrid crop begins before the subject enters in each relevant scene.
Some subject views can include a partially cropped bystander. The model's
imperfect identities and detections still affect visual selection. These are
review candidates, not an approved replacement for earlier Shorts.

## Verification

- 24 behavioral tests passed, covering timing, source preservation, approval/job
  checks, subject alternation (including two people), scene overrides, tracking
  gaps, safe fallback, minimum holds, and edited-plan crop validation.
- All three vertical videos are 1080×1920 at 30 fps, with 968 frames, approximately
  32.267 seconds, and AAC 48 kHz stereo audio. Audio and video start at zero and
  agree within one frame.
- All five video files passed full FFmpeg decode and codec/timing checks.
  Their fingerprints, the contact sheet, and the camera plan were independently
  rechecked after rendering.
- The plan uses the original 97.500–129.750-second source interval and excludes
  the following endcard. Source timestamp conversion adds about 16.7 ms of tail
  hold/padding at 30 fps.
- All continuous crops remain inside the source and contain their selected box.
  Pan/zoom measurements remain within configured limits. Hybrid ends all three
  scenes in group view.
- Source master and four protected prior Shorts remain unchanged. Execution was
  offline. The five-output render/verification pass took about 32.4 seconds.
- Experiment allocation was approximately 2.1 GiB, with approximately 19.8 GiB
  disk free at final verification.

Agent visual inspection covered the rendered contact sheet and per-frame
decisions. Tony's normal-speed review determines whether the framing and
switching feel right.

## Later stages

Switching currently uses visual tracks and explicit timing/preferences; it does
not interpret narration or identify story beats. The ending-group rule is a
configurable timing rule, not semantic recognition of the payoff.

Automatic selection of multiple Shorts from a long master, caption/branding
composition, a questionnaire, Airtable/MCP adapters, pipeline activation, and
publishing remain later stages. The shared job contract is the integration point
for those components. First choose and tune the framing behavior on this review.
