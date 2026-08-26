---
title: "Self-Review — 2026-08-22"
type: self-review
domain: video-production
tags: [self-review, anomalous-wild, mantis-shrimp]
---

# Self-Review — 2026-08-22

## What went well
- Catching real, reproducible defects before they compounded: the Scene_03E environment mismatch (background genuinely shifted mid-clip) and the Scene 05 chroma-green color-spill on translucent assets were both caught by *actually verifying* — frame-extraction contact sheets and checkerboard-composite checks — not by assuming a generation succeeded because no error was thrown. Both became permanent skill-file rules rather than one-off fixes.
- Treating "the storyboard doesn't match the shot list" as a real bug worth investigating root cause, not just patching the immediate scene — this generalized into a repeatable reconciliation pass applied to all 8 scenes.
- Sequential polling pattern for long-running Seedance generations (background bash + resume-on-notification) worked reliably across ~20 clips despite some tasks taking 15-20+ min in queue — didn't give up or assume failure without checking the raw task status for an actual fail code first.

## What could improve
- The final assembly step used a simplified ffmpeg-concat instead of the pipeline's documented Remotion master-composition approach (Phase 7). This was a reasonable judgment call given Tony's literal ask ("I just want to see the final video"), but it's also very likely *why* the full video graded B-/B while every individual scene graded A-range — the gap is presentation/polish, not content. Next time: ask explicitly whether a quick preview assembly or the full Remotion composition is wanted, rather than defaulting to the faster path silently.
- Video-generation polling repeatedly needed 2-4 rounds of 45s×10-attempt loops (kie.ai queue was slow this session, up to 20+ minutes on some tasks) — this worked but was verbose/repetitive in the transcript. Consider a single longer-interval polling loop (e.g. 90s×15) instead of restarting the same 10-attempt loop repeatedly when the first round comes back empty.
- Did not proactively suggest the "grade every video" convention myself — Tony had to introduce it. Once introduced, it's a good practice (built the Report_Card.md entry immediately); worth extending unprompted to other channels' productions going forward, not just Anomalous Wild.

## Pattern to watch
This is the second production (after Scene 02's original diagram-vs-Seedance failure) where the fix that mattered was "stop trusting generation success as validation — extract and actually look." Consider whether this should become an even more explicit mandatory step (not just "verify the matte") across all image/video generation in this pipeline, not only motion-graphics compositing.
