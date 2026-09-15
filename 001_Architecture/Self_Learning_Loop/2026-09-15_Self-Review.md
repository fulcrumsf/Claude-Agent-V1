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

---

## Self-Learning Review — 2026-09-15 (session 2: Neon Parcel Shorts + graphify/commit close-out)

**What went well:**
- Derived exact shot-boundary pts for Subject-Aware Reframer detection configs from real ffprobe scene-detection rather than trusting hand-computed frame math — a manual "frames = seconds × fps" calculation was off by 3 frames on the first attempt (confirmed by the tool's own `expected_source_frames` validation error), and cross-checking against `lavfi scene` detection resolved it cleanly and repeatably for both Part 1 and Part 2.
- Caught a real cost/value mismatch before spending on it: graphify's incremental detect flagged 2,477 "changed" Resource Library docs, but sampling the diffs showed ~1,866 were a cosmetic Notion-icon strip with zero semantic content change. Scoped the actual semantic re-extraction to the 608 genuinely new files instead of blindly re-extracting all 2,477 (~113 wasted subagent dispatches avoided).
- Caught a 154MB PDF about to enter git history permanently before committing, and asked rather than silently committing or silently excluding it — Tony's answer (exclude all PDFs, make it a standing rule) turned into a durable `.gitignore` rule instead of a one-off skip.

**What went wrong / to fix next time:**
- Hit the session's Claude usage rate limit mid-way through a 28-subagent parallel dispatch; had to resume in a later turn. No data was lost (subagents had already written their chunk files to disk before being cut off), but the batch size (28 parallel subagent calls in one message) was large enough to be worth reconsidering — a future similar-scale extraction should check remaining chunk count against expected agent-minutes before firing all of them in one shot, or dispatch in two waves.
- `build_merge`'s cross-repo dedup guard rejected the Resource Library merge outright because the existing graph.json already carried per-subfolder `repo` tags from the original v2/v2.1 multi-repo-merge build — this wasn't discoverable without hitting the actual error, and cost a retry cycle (tried `root=absolute path` first, which didn't fix it, before finding the real cause was `dedup=True` itself). Now documented in REGISTRY.md so the next `--update` on this domain doesn't rediscover it the hard way.
- Did not do a full manual community-labeling pass on the Resource Library graph after this update (2,095 communities — the existing curated ~392 labels from v2.1 don't survive a fresh cluster() call since community IDs aren't stable across runs). Labels are currently generic `Community N` placeholders. Flagged honestly in REGISTRY.md rather than leaving it undocumented, but a future session should decide whether a labeling pass is worth doing given the scale.

**Recurring pattern worth naming:** twice this session, the responsible move was to computationally verify a plan against the real artifact before committing resources to it — sampling actual file diffs before choosing extraction scope, and checking actual git-staged file sizes before committing. Cheap verification steps (a `git diff`, a `du -sh`, a scene-detection ffprobe call) caught real problems that pure reasoning from the task description would have missed.
