---
title: "Lab System"
type: wiki
category: ai-agents
tags:
  - lab
  - claude-code
  - openrouter
  - model-routing
  - sandboxing
created: 2026-10-06
source: 001_Architecture/Ongoing-Agent-OS-To-Do-List.md (Part 4), 001_Architecture/Skills/lab/SKILL.md
---
# Lab System

## What It Is
`/lab` is Agent-OS's middle lane for non-chore, multi-step builds: a deliberately-picked, cheaper OpenRouter model drafts and builds inside hard containment, a stronger model (`opus-standard`/`opus-deep`) reviews and scores every step, and nothing reaches the real workspace until Tony explicitly promotes it. Explicit-trigger only — Jev never routes into `/lab`, and there is no standing "lab mode."

## The Four Commands (all built as of 2026-10-06)

| Command | Does | Sandboxed? |
|---|---|---|
| `/lab-plan <question>` | Picked model drafts a plan read-only; `opus-standard` scores it 0-100, writes acceptance checks, locks (80+) or regenerates (below 80). | Read-only |
| `/lab-build` | Picked model builds the plan's one new folder inside a git worktree, network forced off, containment checked (git-based, never a model's word). Scored 60 (acceptance checks) + 15 (containment/Tier-0) + 25 (Opus audit). 80+ clears for `/lab-run`. | Yes — real sandbox |
| `/lab-run` | Tony's own real, unsandboxed use of the build — tries it for real, grades it 0-100. Below 80: the harness model (never the OpenRouter picker) fixes it in place and tries again. Repeats until 80+. | No — intentionally the opposite of `/lab-build` |
| `/lab-promote` | Commits the build's final on-disk state to its own lab branch (never `main` directly, fingerprint-checked against what Tony actually graded), checks out the one approved folder into the real workspace, updates TOOLBOX/wiki/graphify, commits, pushes. Tony typing the command is the approval. | No |

Scripts: `001_Architecture/Scripts/lab_plan_draft.py`, `lab_build.py`, `lab_run_log.py`, `lab_promote.py` (+ test files for each). Skills (the commands themselves): `001_Architecture/Skills/lab-plan/`, `lab-build/`, `lab-run/`, `lab-promote/`. Projects live at `001_Architecture/Lab/<date>_<slug>/` (gitignored — nothing there is real until promoted).

## Real Bugs This System Already Caught In Itself

- **A false "network is off" assumption.** `/lab-build`'s containment design assumed Tony's Codex sandbox config already disabled network access. It didn't — confirmed live, now force-disabled every run.
- **A false containment-escape positive.** macOS Google Drive's background sync briefly gives a new file a second hardlink while uploading it, which an early version of the containment checker misread as a sandbox-escape attempt. Fixed to recognize Drive's own staging folder specifically; real escapes are still caught at 100%.
- **A promotion gap.** `/lab-run`'s fixes are made directly by the harness model, in place, and never committed to the build's own git branch (by design — revision never touches the OpenRouter picker or its spend cap). A naive `/lab-promote` reading that branch would ship the pre-fix code. Fixed by committing the worktree's real final state, fingerprint-checked against the grade Tony actually gave, before the real promotion.

## First Real Project Through The Whole Pipeline

**Quality_Ledger** — a universal, pipeline-agnostic logging/grading tool distinguishing `mechanical_check` / `director_judgment` / `agent_self_correction` / `director_edit` events, meant to replace the empty/inconsistent per-production logs found across Neon Parcel. Went through 7 real hardening rounds (124 tests, 34+ bugs found-and-fixed in one adversarial pass), graded 87 in `/lab-run`, and **promoted** to `001_Architecture/Tools/Quality_Ledger/` on 2026-10-06. See [[Quality-Ledger]] for the tool itself; wiring into live pipelines is still Tony's to-do.

## Key Decisions, Don't Re-Litigate

- Revision during `/lab-run` never goes back to `/lab-build` or any OpenRouter model, ever — the harness model (or an `opus-standard` subagent it spawns) makes every fix directly. This keeps the $2/project OpenRouter cap scoped to the one initial plan+build pass only.
- `/lab-build`'s fix-round and rebuild each get used at most once per project; a containment-gate failure gets zero fix attempts, full stop, shown to Tony immediately.
- Old worktrees and stale branches from a rebuild are never auto-deleted — `/lab-build`/`/lab-promote` print the exact cleanup commands for Tony to run himself.
