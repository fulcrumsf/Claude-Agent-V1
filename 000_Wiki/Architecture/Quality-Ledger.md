---
title: "Quality Ledger"
type: wiki
category: architecture
tags:
  - quality-ledger
  - logging
  - grading
  - lab-system
  - pipeline-agnostic
created: 2026-10-06
source: 001_Architecture/Tools/Quality_Ledger/README.md, 001_Architecture/Tools/Quality_Ledger/Agent_Instructions.md
---
# Quality Ledger

## What It Is
A channel-agnostic, append-only quality log for Agent-OS production pipelines (Neon Parcel, Anomalous Wild, Reimagined Realms, TikTok Shop, and future channels), plus a fail-open hook adapter (`ledger_hook.py`) that fills it without anyone having to remember to call it. Built and promoted through the [[Lab-System|/lab system]] — the first real project to go through all four `/lab` commands end to end.

**Location:** `001_Architecture/Tools/Quality_Ledger/`
**Promoted:** 2026-10-06, graded 87 in `/lab-run` (Tony).

## The Four Event Types
Every line in a ledger is one event with exactly one source:

| Type | Source | Notes |
|---|---|---|
| `mechanical_check` | A script or automated gate | `pass`/`fail`/`error` + measured value. `error` = the tool broke (Kie 500, upscaler timeout); `fail` = the tool ran but the output failed the check (wrong hand, van at 1.7x). This split is what plain Report Cards blur together. |
| `director_judgment` | Tony's own chat text, verbatim | Grade and/or decision (`accept` / `accept_with_flaws` / `redo`). Only Tony's own words can produce one — never a script, check, or agent inference. |
| `agent_self_correction` | The agent, before Tony saw the result | Requires a `reason` and a `corrects_event_id` link to the event it fixed. |
| `director_edit` | Tony, with his own hands | `actor` is always Tony; `reason` required; no `check` or `director` object. Counts as an explained retry, like a self-correction. |

Grades attach to any level Tony comments on (`sub_step`, `step`, `final`) — `--level` has no default, so a forgotten level is a hard error, never a silent misattribution.

## Failure Types (Closed List)
A fixed, closed vocabulary (free text rejected) covering the real recurring defect categories found across Neon Parcel and other channels: `spatial_layout`, `scale`, `continuity`, `subject_count`, `plausibility`, `camera`, `motion`, `render_artifact`, `story`, `other`. Full table with real examples in the tool's own README.

## Design Decisions (Locked, Don't Re-Litigate)
- **Readiness = latest final grade per run only.** A run's readiness contribution is its most recent final-level grade, not every grade ever logged for it.
- **Check attempts share by artifact fingerprint.** Multiple `mechanical_check` calls against the same artifact (same sha256) collapse into one attempt instead of inflating the attempt count.
- Confirmed by Tony, 2026-10-06, after the artifact-sharing and readiness-filter implementation round.

## Status (as of promotion)
Hardened through 7 real rounds, 124 passing tests, 34+ real bugs found and fixed in one deliberate adversarial pass. Validated against real production history (Neon Parcel's kangaroo-doorbell shot) as a mechanical check that the ledger/hook/grading flow works end to end — that was a dry run of the mechanism, not a real grading session, and did not re-grade or re-review that already-approved video.

**The real first test** is the next new Neon Parcel video run through the pipeline after wiring is complete: Quality_Ledger should fill automatically as the production runs, and that live grading is the actual validation, not a replay of old footage.

## Wiring Still Needed (Tony's To-Do, Not Part Of The Build)
- Register `ledger_hook.py` in each harness's hook config (Claude `~/.claude/settings.json`, Codex `~/.codex/hooks.json`, Gemini `~/.gemini/settings.json`) — harness config edits are blocked in auto mode, so these commands have to be run by Tony himself.
- Copy `Workflow_Registry_Example.json` to a live `Workflow_Registry.json` and add each workflow to cover.
- Paste `Agent_Instructions.md` into each workflow's own skill (Neon Parcel v2, Anomalous Wild, Reimagined Realms, TikTok Shop, social-content, future channels).
- Add `quality_ledger.py check` calls to shared checkers (`check_storyboard_scale.py`, the character-sheet hand-check, `seedance2_call.py` error paths) and to `scaffold_new_production.py`.
- A central ledger for runs with no production folder: `001_Architecture/Logs/Quality_Ledger.jsonl`.
- Backfill the 17 existing Report Cards into the ledger (confirmed by Tony, 2026-10-02) — a wiring step, not part of the build, since it writes real production data.

## See Also
- [[Lab-System]] — the build pipeline this tool went through
