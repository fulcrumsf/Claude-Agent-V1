# Self-Review — 2026-06-10

## What Went Wrong

**Scene timestamp cross-contamination.** I used `scene_analysis.md` timestamps (from Reference.mov, 26s) to try cutting Reference2.mov (15s). I should have verified the video duration against the timestamps before building the cut list — a one-line `ffprobe` check at the start would have caught this immediately.

**Missing spatial orientation constraint in initial Seedance prompt.** The first video came back with cards on-edge because the prompt described motion ("drops straight down") without locking the object's spatial orientation. For falling objects, orientation must be stated before motion, not assumed. The fix is now documented but I should build "orientation lock" into my mental template for any falling/dropping shot.

**Poll termination condition.** The kie.ai polling loop used `('succeeded', 'failed', 'error', 'completed')` but the actual success state is `'success'`. Ran 20 extra poll iterations unnecessarily. Fix: always log a raw sample of the status field before writing the condition check.

## What Worked

**Cloudinary as API bridge.** When kie.ai had no working upload endpoint and fal.ai storage DNS failed, reaching for Cloudinary (already in TOOLBOX) was the right call. Installed SDK in under a minute, got public URLs, unblocked the pipeline.

**Pixel diff scene detection on fresh video.** Re-running detection on Reference2.mov rather than trying to adapt old timestamps was cleaner and faster than debugging the mismatch.

## Patterns to Watch

- AI video models need *physical analogy* orientation constraints, not just spatial language. "Never rotates" is weaker than "like a hardcover book dropping face-down."
- Always `ffprobe` duration of target video before building a cut list from any external source of timestamps.
- When an API endpoint returns 404 for upload, check TOOLBOX for hosted storage options (Cloudinary, S3, etc.) before trying to reverse-engineer the API.
