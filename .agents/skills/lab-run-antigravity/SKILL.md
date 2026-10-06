---
name: lab-run-antigravity
description: Antigravity only. Use when Tony types /lab-run [project] (or asks to lab-run a cleared build) inside the Antigravity IDE agent chat - his own first real use of a build /lab-build cleared (80+), graded 0-100 each round, with you fixing the build folder in place between rounds until he grades it 80+. Not for Claude Code (use the lab-run skill there) or Codex (use lab-run-codex).
---

# /lab-run (Antigravity)

`/lab-run` has no Gemini-only step: a small script does the bookkeeping and the session it runs in
(here, you) does the rest. So there is one set of instructions for every harness. Read
`/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/lab-run/SKILL.md` in full now and
follow its Steps 1-5 exactly, with only the differences below.

Tony's argument: $ARGUMENTS (a folder name under `001_Architecture/Lab/`, a full path, or empty).

## Differences in Antigravity

- **Who:** wherever that file says "this Claude Code session", read "you, the Antigravity agent".
  Run its commands in the terminal. Antigravity has no subagents, so the `opus-standard` option in
  its Step 4 does not exist here: you make every fix yourself.
- **The locked rule still holds, unchanged:** every fix is made by the harness (you). Never run
  `lab_build.py` or `lab_build_gemini.py` in any mode, `lab_plan_draft.py`, `delegate.py`,
  `frontier.py`, Jev, OpenRouter, `codex exec`, or another harness to make a change. Nothing here
  spends from the `/lab` budget.
- **One harness per loop:** before showing Tony how to try it (its Step 2) on a project that
  already has rounds, read the last line of `<PROJECT_DIR>/Run_Log.jsonl`. If its
  `changes_before_this_try` does not start with `[Antigravity]` (no tag = a Claude Code round,
  `[Codex]` = a Codex round), tell Tony this loop started on another harness and ask whether to
  continue it here before you change anything.
- **Tag every round:** in its Step 3, start the `--changes` value with `[Antigravity]` (on round 1
  just `'[Antigravity]'`; after a fix, `'[Antigravity] <what you changed>'`).

## Never do

Everything that file's "Never touched" list and Step 4 rules forbid: no edits outside the build
folder, no deletes, renames or new folders (tell Tony the exact command instead), no commits, never
suggest a grade or soften his notes, never publish, send or upload without his explicit yes.
