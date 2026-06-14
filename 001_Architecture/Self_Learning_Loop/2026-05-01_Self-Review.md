---
title: "Self-Review - 2026-05-01"
type: self-review
tags:
  - self-review
created: 2026-05-01
---

# Self-Review - 2026-05-01

## What Worked Well

**Back-and-forth design before implementation.** Tony explicitly asked to discuss the plan before building anything. Asking one focused question per turn (voice dictation constraint) kept the conversation clean and resulted in clear decisions before a single file was touched. This is the right pattern for any skill/system redesign.

**Reading the existing skill before designing.** Loading the full ingest SKILL.md early meant every design decision was grounded in the actual current state, not assumptions. The media plan integrated cleanly because I understood what was already there.

**Surfacing the Notion database nuance.** Tony hadn't thought through the scaffolding-vs-content distinction before I raised it. Proactively asking about it prevented a bad default (ingesting hundreds of meaningless container MDs) from being baked into the skill.

## What to Watch

**The "same answer across all three files" problem.** AGENTS.md, GEMINI.md, and SKILL.md now have overlapping ingest logic. If the procedure changes again, all three need updating. Worth noting if the skill gets extended again — consider whether AGENTS.md should just point to SKILL.md as the canonical source rather than restating the steps.

**Asset Note naming is an untested assumption.** The decision to name Asset Notes identically to media files (same stem, `.md`) seemed clear in the conversation, but hasn't been tested in practice. If Obsidian or the file system has any issue with two files sharing the same stem in different folders, this will surface during the first actual ingest.

## Patterns

- Tony consistently prefers to think out loud before committing to implementation. Let him drive the exploration phase.
- When Tony says "I need to think about that," surface the tradeoffs and let him land the decision rather than proposing a default.
