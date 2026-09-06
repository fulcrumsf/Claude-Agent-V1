# 2026-08-27 Session Log

## Seedance Global Guidance And Tool Catalog

- Added global Seedance guidance for complex-shot fallback: Seedance 2 Mini
  480p/720p, storyboard prompting, Topaz upscaling, and FFmpeg normalization.
- Added active Tool Manager catalog entries for Seedance 2 Mini and Topaz Video
  Upscaler with Kie.ai pricing verified on 2026-08-26.
- No video generation or production media changes were made.
- Added strict semantic-assessment gating to the shot router so lexical
  keywords cannot auto-route a shot by themselves. Added the approved audio,
  storyboard, and camera-lock requirements to the Neon Parcel contract.
- Began the approved five-shot batch: generated Shots 1-4, reused Shot 5,
  upscaled Mini outputs 2x with Topaz, normalized all five to 1920x1080 with
  FFmpeg, and recorded provider task IDs in the production Generation_Log.
- Paused further generation at Tony's request. Renamed the production to
  `0001_Grandma-And-Bear-Compilation`, retained the five normalized active
  clips, and moved prior tests/intermediates into `Video_Clips/Archived/`.
- Updated production metadata and archived test paths; JSON validation passed.

## Approved Neon Parcel Pipeline Update

- Tony approved the review-update plan before shot revisions.
- Updated the Neon Parcel skill and pipeline contract with pre-video realism,
  camera plausibility, meaningful-beat, and humor-context gates; overlay
  separation; and explicit Seedance route rules.
- Added `validate_pre_video_gate.py` for conservative, explainable preflight
  validation and `generation_guard.py` for prompt-archive and duplicate-task
  blocking.
- Wired the Kie Market wrapper with guarded production submission support.
- Added `Working`, `Intermediate`, and `Video_Clips/Archived` to new
  production scaffolds and corrected the scaffold test for numbered roots.
- Verification: 16 Neon Parcel unit tests passed; Python compilation passed;
  `pipeline.yaml` parsed as valid YAML.
- Shot revisions remain paused for Tony's next instruction.

## Revision Batch Execution

- Archived prior unapproved Shot 1-4 renders while preserving Shot 5.
- Generated and normalized four `v2` revisions, with guarded Kie task logging.
- Final files are all 1920x1080; Shots 2 and 4 each have exactly one Topaz
  upscale task, while Shots 1 and 3 bypassed Topaz.
- Pipeline is paused for Tony's review of the four videos.

## Image Archive Cleanup

- Audited the Neon Parcel production `Images/` folder.
- Moved superseded Shot 1 end frame, Shot 3 end frame, and Shot 4 storyboard
  into `Images/Archived/`.
- Retained active start frames and Shot 2 storyboard because current `v2`
  prompts still reference them.

## Additional Safeguards Implemented

- Added the physical-action risk filter to concept development and the pipeline
  contract.
- Added the Seedance 1.5 endpoint-frame decision tool and rules for using
  start-frame-only generation when an end frame could confuse interpolation.
- Verification after these changes: 20 Neon Parcel unit tests passed and the
  pipeline YAML remained valid.
