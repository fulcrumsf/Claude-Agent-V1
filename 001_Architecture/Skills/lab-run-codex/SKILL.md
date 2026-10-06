---
name: lab-run-codex
description: Codex only. Runs when Tony types $lab-run-codex [project] (or "/lab-run" in Codex) - Tony's own first real use of a build /lab-build cleared (80+), graded 0-100 each round, with this Codex session (or a sol-standard subagent it spawns) fixing the build folder in place between rounds until he grades it 80+. Claude Code - use lab-run. Antigravity - use lab-run-antigravity.
disable-model-invocation: true
---

# /lab-run (Codex)

`/lab-run` has no harness-only step: a small script does the bookkeeping and the session it runs in
(here, you) does the rest. So there is one set of instructions for every harness. Read
`/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/lab-run/SKILL.md` in full now and
follow its Steps 1-5 exactly, with only the differences below.

Tony's argument: whatever he typed after the command (a folder name, a full path, or nothing).

## Differences in Codex

- **Who:** wherever that file says "this Claude Code session", read "this Codex session". Where it
  says to spawn `opus-standard` for a tricky fix, call `spawn_agent` with
  `agent_type: "sol-standard"` and `fork_turns: "none"`, giving it Tony's notes, the `build_dir`,
  `Plan_Locked.md` and the same rules. Both are the harness.
- **The locked rule still holds, unchanged:** never run `lab_build.py` or `lab_build_gemini.py` in
  any mode, `lab_plan_draft.py`, `delegate.py`, `frontier.py`, Jev, OpenRouter, `codex exec`, or
  another harness to make a change. Nothing here spends from the `/lab` budget.
- **Running `lab_run_log.py`:** run it outside Codex's sandbox (request escalated permission):
  `checks` starts its own codex sandbox (macOS refuses a sandbox inside a sandbox), and every grade
  is also logged to `~/Library/Logs/Agent-OS-Lab.jsonl`, which the sandbox would silently block.
  The tool's own real run usually needs the network and real files too: run it the same way.
- **One harness per loop:** before showing Tony how to try it (its Step 2) on a project that
  already has rounds, read the last line of `<PROJECT_DIR>/Run_Log.jsonl`. If its
  `changes_before_this_try` does not start with `[Codex]` (no tag = a Claude Code round,
  `[Antigravity]` = an Antigravity round), tell Tony this loop started on another harness and ask
  whether to continue it here before you change anything.
- **Tag every round:** in its Step 3, start the `--changes` value with `[Codex]` (on round 1 just
  `'[Codex]'`; after a fix, `'[Codex] <what you changed>'`).

## Never do

Everything that file's "Never touched" list and Step 4 rules forbid: no edits outside the build
folder, no deletes, renames or new folders (tell Tony the exact command instead), no commits, never
suggest a grade or soften his notes, never publish, send or upload without his explicit yes.
