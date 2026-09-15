---
title: "Self-Learning Review — 2026-09-15"
type: self-review
category: session
created: 2026-09-15
---

# Self-Learning Review — 2026-09-15

**What went well:**
- Root-causing over spot-fixing: every "it keeps putting things in the wrong folder" complaint was traced to an actual code bug (stale `VALID_FOLDERS`, a truncating parser, a `Digital_Products` definition loophole) rather than just moving the individual misplaced note each time. The fixes compounded — later test batches showed real, measurable improvement.
- Reuse discipline held up under real pressure: the Ingest Visualizer imports `process_image_ingest.py` and `retag_and_retitle.py` as modules instead of re-implementing vision/classification calls a third time, and a shared `finalize_and_write_note()` was extracted (behavior-verified unchanged) rather than duplicating the note-writing template a second time.

**What went wrong / to fix next time:**
- Introduced the tag-vocabulary and folder-vocabulary dynamic-loading fix in two separate passes tonight, and only caught on the *second* pass that the Directory.md parser was silently truncating multi-line bullets to their first line — meaning the first pass's carefully-written channel-pattern guidance never actually reached the model until this was found. Lesson: after writing a new dynamic-config-loading path, actually print/inspect what gets parsed before trusting it's complete, not just that it doesn't crash.
- A live browser-UI test triggered a real, unintended ingest of ~84 items with a wrong tag. Root cause (batch bar not auto-applying) is fixed, but the deeper lesson is procedural: destructive/confirm-gated actions should be verified via direct API calls first, never by clicking through the live UI during my own testing.
- macOS's `sed` doesn't support `\s` — a "successful" removal silently did nothing, and this wasn't caught until manually re-reading the file. Worth a standing reminder to verify shell-based text edits by re-reading the result, not by trusting a zero exit code.
- 666 files sat uncommitted for the entire session. For a session this large and multi-part, should have flagged committing as a decision point mid-session rather than only surfacing it at handoff time.

**Recurring pattern worth naming:** several tonight's bugs were "two systems that should agree silently drifted apart" (tag vocabulary duplicated in the prompt vs. Directory.md; VALID_FOLDERS hardcoded vs. the real folder list; the needs-enrichment tag existing in code but never approved by Tony). The general fix pattern each time was the same: make the second copy read live from the first source of truth instead of hardcoding it. Worth checking for this pattern proactively in other scripts, not just reactively when Tony reports a symptom.
