---
title: "Self-Review — 2026-04-28"
type: report
domain: architecture
tags: [report, architecture, knowledge-graph]
---

# 2026-04-28 — Self-Review

## Patterns

### Subagent budget is a real constraint, not a soft one
Hit the org's monthly subagent usage limit during Phase 3 (wikify). Two of three parallel agents were cut off mid-work but had finished ~90% of their assigned files before the limit hit. Direct tool calls (Bash/Edit/Read) continued working — only the Agent dispatch was blocked.

**Lesson:** Before dispatching multi-agent batches, weigh whether the work can be done sequentially with direct tool calls. Wikify (read → classify → prepend frontmatter) didn't strictly need subagents — it was chosen for parallelism. With hindsight, sequential bash + Edit would have been cheaper and not run into the limit.

**Trigger condition for the limit:** Multiple parallel general-purpose agents each making 80+ tool calls over file-iteration loops. Budget exhausted in ~5 minutes of wall time.

### Always verify what an agent actually did vs what it reported
The Resource_Library agent reported clean completion. The Content-Creation and Architecture agents reported "limit hit" but had silently completed most of their work. Inspecting the filesystem (counting files with `head -1 | grep "^---"`) gave the actual progress, not the agents' reports.

### Plan assumptions can break at execution time
The plan said "Phase 4: run `graphify .` per domain". At execution, discovered that the build pipeline is the `/graphify` slash command, which itself dispatches parallel subagents for semantic doc extraction. Phase 4 was always going to be subagent-heavy — that should have surfaced during planning, not after Phase 3 already exhausted the budget.

**Rule:** When a plan involves a tool I haven't run before in this workspace, do a `--help` or skill-file read during planning, not execution.

## What worked well

- Splitting wikify into 3 parallel agents by file count (Resource_Library, Content-Creation, everything else) was the right shape — Resource_Library finished cleanly, the other two were salvageable
- Sentinel-based dirty tracking for the federation hooks is robust to interruption (sentinel survives a crashed session, recover-stale picks it up)
- Inline functional smoke test of `mark-dirty.sh` + `rebuild-dirty.sh` after install caught nothing broken but proves the wiring works

## What to improve

- Pre-flight check at start of any plan that involves subagents: estimate total subagent dispatches and decide whether to batch into smaller waves
- When a tool's CLI shape differs from the skill/slash-command shape, read the skill file early so the plan reflects reality

---

# 2026-04-28 (Session 2) — Ingest System Build

## What Went Well

- Brainstorming skill kept the design conversation structured before building anything
- Reading folder structures before asking Tony questions — he explicitly called out that asking questions he could answer by looking is a failure mode
- The skill-creator → test → deploy flow produced a working skill that passed across Claude Code and Codex
- AGENTS.md + GEMINI.md as portability layer is the right architecture — same brain, different entry points

## What Was Wrong (Yesterday's Session)

- Told Tony "just say ingest and I'll know what to do" — no skill was created, no procedure encoded. This breaks across context resets and environments. Fix: always encode in a skill.
- Didn't suggest AGENTS.md or GEMINI.md — Tony had to raise cross-environment portability himself.

## Rules for Next Session

- Ingest = invoke ingest skill. Never improvise the pipeline.
- Read `001_Architecture/Install_Maps/Workspace-Map.md` before exploring any folder.
- `000_Ingest/Notion-Edit/` — off limits until Tony manually curates it.
- Full workspace graphify deferred until bulk ingest is complete.
