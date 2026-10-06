---
name: lab-plan-codex
description: Codex only. Runs when Tony types $lab-plan-codex <question> (or "/lab-plan" in Codex) - a cheap picked OpenRouter model drafts a build plan read-only, then a sol-standard subagent scores the raw draft 0-100, writes acceptance checks, and locks (>=80) or regenerates (<80) the plan into 001_Architecture/Lab/. Claude Code - use lab-plan. Antigravity - use lab-plan-antigravity.
disable-model-invocation: true
---

# /lab-plan (Codex)

Codex has the same building blocks as Claude Code here: the same script (`lab_plan_draft.py`) and a
named frontier subagent (`sol-standard`, `gpt-6-sol`) in place of `opus-standard`. So there is one
set of instructions for both. Read
`/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/lab-plan/SKILL.md` in full now and
follow its Steps 1-4 exactly, with only the differences below.

Tony's question: whatever he typed after the command. If it is empty, ask him what he wants planned
and stop.

## Differences in Codex

- **Who:** wherever that file says "you, the Claude Code session", read "you, this Codex session".
- **The reviewer (its Step 2):** call `spawn_agent` with `agent_type: "sol-standard"` and
  `fork_turns: "none"` (a fresh context, so the reviewer is independent of this session and runs on
  sol-standard's own model) and the same prompt that file gives, with `sol-standard` wherever it
  says `opus-standard` (`"scored_by"`, `locked_by:`, `"written_by"`). Then `wait_agent` with long
  waits until it reports. This skill is your explicit instruction to spawn it. Never do the review
  yourself.
- **"SendMessage to the same reviewer"** (its Step 3): `followup_task` to that same agent.
- **Running `lab_plan_draft.py`:** run it outside Codex's sandbox (request escalated permission,
  justification: "it starts its own codex sandbox, which macOS refuses inside another sandbox, and
  it needs the network for OpenRouter"). The draft can take up to 20 minutes: give it a long timeout
  or keep polling until it exits.
- **If `spawn_agent` is not available** in this Codex window, stop after the draft and tell Tony.
- **The report (its Step 4):** say "sol-standard" wherever it says "Opus". End by saying the plan
  is ready for `/lab-build` (`$lab-build-codex` here).
