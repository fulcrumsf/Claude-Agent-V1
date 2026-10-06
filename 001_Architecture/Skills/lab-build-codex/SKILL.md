---
name: lab-build-codex
description: Codex only. Runs when Tony types $lab-build-codex [plan folder] (or "/lab-build" in Codex) - a cheap picked OpenRouter model builds a locked /lab-plan inside a network-off sandbox and a git worktree under 001_Architecture/Lab/, a script scores it for real on the plan's acceptance checks, then a sol-standard subagent audits it, with at most one fix round and one rebuild. Claude Code - use lab-build. Antigravity - use lab-build-antigravity.
disable-model-invocation: true
---

# /lab-build (Codex)

Codex has the same building blocks as Claude Code here: the same script (`lab_build.py`) and a
named frontier subagent (`sol-standard`, `gpt-6-sol`, in `~/.codex/agents/sol-standard.toml`) in
place of `opus-standard`. So there is one set of instructions for both. Read
`/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/lab-build/SKILL.md` in full now and
follow its Steps 1-6 exactly, with only the differences below.

Tony's argument: whatever he typed after the command (a folder name under `001_Architecture/Lab/`,
a full path, or nothing = the newest locked plan with no build yet).

## Differences in Codex

- **Who:** wherever that file says "you, the Claude Code session", read "you, this Codex session".
- **Spawning the auditor (its Step 2) and the rebuilder (its Step 5):** call `spawn_agent` with
  `agent_type: "sol-standard"` and `fork_turns: "none"` (a fresh context, so the auditor is
  independent of this session and runs on sol-standard's own model), and the same prompt that file
  gives, with `"scored_by": "sol-standard"` in the audit JSON. Then `wait_agent` with long waits
  (minutes) until it reports. This skill is your explicit instruction to spawn these subagents.
- **"SendMessage to the same auditor"** (its Steps 3 and 4): `followup_task` to that same agent.
- **New agent rules are unchanged:** the rebuild gets a NEW `sol-standard`, and the rebuild's
  audit gets another NEW one (never the rebuilder). Never audit, fix or rebuild anything yourself.
- **Running `lab_build.py`:** run every call outside Codex's sandbox (request escalated permission,
  justification: "lab_build.py starts its own codex sandbox, which macOS refuses inside another
  sandbox, and it needs the network for OpenRouter"). The build can run 30+ minutes: give it a long
  timeout or keep polling until it exits; never cancel it early.
- **If `spawn_agent` is not available** in this Codex window (multi-agent off), stop after the
  build is scored and tell Tony. Do not do the audit yourself and do not substitute another tool.

## Known limit

`lab_build.py` labels the fix round and the rebuild "opus-standard" in `Build_Meta.json` and the
score files. In Codex they were done by `sol-standard`; the auditor's `Build_Review.md` sections
and `Build_Audit*.json` (`scored_by`) say who really did the work.
