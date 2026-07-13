---
title: "Self-Review — 2026-07-11"
type: rationale
domain: content-creation
tags: [self-review, anomalous-wild, blotato, quality-control]
---

# 2026-07-11 Self-Review

## What went well
- Caught the thumbnail-style conflict (locked brand JSON vs. pipeline default) before generating anything, and asked instead of guessing — Tony confirmed this was the right call and the resulting thumbnail scored "Grade A."
- Caught the broken title/description output from `generate_youtube_package.py` by actually reading the generated file before uploading, instead of trusting the script ran correctly because it exited 0.
- For the end-card redesign, rendered still-frame previews at each iteration step (layout move, then background-image shift) instead of jumping straight to a full 10s render — kept iteration cheap and let Tony give precise feedback before committing compute to the final video.
- Diagnosed the Blotato upload failure by actually inspecting the uploaded file's response headers (`curl -I`) rather than re-guessing at the API payload — found the real root cause (missing Content-Type) instead of retrying blindly.

## What went wrong / recurring pattern
- Two Blotato upload failures in a row before finding the real cause (400MB cap, then Content-Type). The first failure (400MB) should have been anticipated — file size vs. platform upload limits is a checkable precondition, not something to discover via a failed API call. Next time: check file size against known platform caps *before* attempting upload, not after.
- Initially called `generate_youtube_package.py` with a full-sentence `subject` argument instead of a short noun phrase, which produced visibly broken output on the first pass. The script's own usage docstring didn't warn about this, but a quick sanity check of the output before treating it as "done" would have caught it sooner — I did catch it, but only after killing an in-progress background generation that had already started.

## What could be automated / systematized
- The Content-Type-on-Blotato-upload gotcha and the 400MB cap are both now written to Feedback_Loop, but they'd be more durable as an explicit step in `upload_to_blotato.md` itself (the actual pipeline doc other agents will read) rather than only living in a dated feedback file. Worth updating that doc directly next time it's touched.
- `generate_youtube_package.py`'s title/description builder is a known-broken utility now bypassed by hand-writing copy. It should either be fixed properly or have its docstring updated to warn "do not use for final titles, draft-quality only" so a future agent doesn't trust it blindly.
