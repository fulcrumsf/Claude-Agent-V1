---
title: "Session Handoff — 2026-09-11 (Claude Code)"
type: handoff
category: session
created: 2026-09-11
updated: 2026-09-11
---

# Session Handoff — READ THIS FIRST next session

## Shipped and pushed (main, tag `resource-library-v3-neon-parcel-shorts-2026-09-11`)

- **Resource Library taxonomy locked:** every note = Folder + Source (auto) + Tags (1-2 from a fixed 20-value list). No more Intent/Project/Form fields — rejected. Full definitions live in `007_Resource_Library/Directory.md` (Folder Layout, Source Definitions, Tag Vocabulary sections) — **that file is the single source of truth**, scripts parse it live.
- New folders: `Mockups`, `POD_Prints`, `Digital_Products`, `Content_Ideas`, `Affiliate_Marketing`, `UGC`, `Travel`; `Project_Ideas` renamed to `Clipping`.
- New scripts in `001_Architecture/Scripts/`: `retag_and_retitle.py` (reclassifies notes from existing text via a cheap text-only LLM, no Vision; flags to `Undetermined/` what it can't confidently do; `--force-folder`/`--exclude`/`--only-empty` flags) and `strip_offvocab_tags.py`.
- ~1,800+ notes reclassified. Visualizer (`001_Architecture/Tools/Resource-Library-Visualizer/`, `python3 serve.py` → localhost:8756) got: Move action, full YAML editor + tag-checkbox picker, Prev/Next nav, MD source detection, off-vocab tag audit row.
- Full memory of the design decisions: see Claude memory `project_resource_library_taxonomy_v2.md`, `project_resource_library_workflow.md`, `feedback_harden_dictated_specs.md`, `feedback_capitalize_vocab_values.md`.

## In progress — Tony reviewing tag accuracy (not done)

Tony is manually spot-checking tagged notes over the next couple of days and reporting bad tags one at a time. Pattern so far: most errors are **the tag definition's wording being ambiguous** (a word in the definition collides with unrelated content) rather than the model being careless. Fixed this session: `Art-Reference` (dropped "viral audio" clause), `Product` (now physical-goods-only, excludes software/games), `Research-List` (now requires an actual visible list layout), `Platforms` (now requires the platform itself be the subject, not just mentioned), and the "don't force a second tag" rule (both in `Directory.md` and the model prompt in `retag_and_retitle.py`).

**Next session: wait for Tony to bring more bad-tag examples.** For each: read the actual note, determine if it's a definition-wording collision (tighten `Directory.md`) or a genuine ungrounded model error (different problem — no fix yet, open question whether a verification pass is worth building). Do NOT re-run the bulk retag script or build a verifier until Tony says so — he's explicitly still iterating/gathering examples.

## Known residual (low priority)

- 24 notes still in `Undetermined/`, 17 notes anywhere have empty tags (`tags: []`) — genuinely-empty stubs, fine to leave.
- Ingest-triage visualizer for `000_Ingest/` (batch-assign folder/tags before vision runs) was discussed at length but never built — still on the table if Tony wants it later.
