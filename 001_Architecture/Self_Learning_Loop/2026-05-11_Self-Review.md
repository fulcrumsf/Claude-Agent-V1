---
title: "2026-05-11 Self Review"
type: self-review
category: architecture
tags:
  - self-review
  - graphify
  - workspace-rename
  - workflow
created: 2026-05-11
source: local
---

# 2026-05-11 Self Review

## What Worked

- Verified the rename against live config instead of assuming the workspace was fine.
- Caught the Graphify coverage mismatch: `graphify update .` rebuilt the code graph but did not cover docs-only folders.
- Pushed the `000_Ingest` exclusion into the skill, registry, hooks, and all three CLI bootstrap docs so the rule is consistent across Claude Code, Codex, and Gemini.

## What Needed Correction

- The first Graphify audit treated the root update as if it covered the whole vault. It did not.
- The docs had been telling agents to use a single graphify flow for everything, which was wrong for docs-only and wiki-heavy domains.

## Pattern To Keep

- Separate staging areas from durable knowledge domains.
- Put workflow exclusions in the automation entry points, not only in memory notes.
- Verify graph output by domain coverage, not by success exit code alone.
