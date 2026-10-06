---
name: lab-promote-antigravity
description: Antigravity only. Use when Tony types /lab-promote [project, or his own words for what is being promoted] inside the Antigravity IDE agent chat - the last /lab step for a build he graded 80+ in /lab-run. Moves the one folder into the real workspace, adds its TOOLBOX.md entry and wiki page, runs graphify, commits only those changes to main and pushes. Not for Claude Code (use the lab-promote skill there) or Codex (use lab-promote-codex).
---

# /lab-promote (Antigravity)

`/lab-promote` has no Gemini-only step: `lab_promote.py` does every git step and check, and the
session it runs in (here, you) writes the TOOLBOX.md entry and the wiki page. So there is one set
of instructions for every harness. Read
`/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/lab-promote/SKILL.md` in full now
and follow its Steps 0-6 exactly, with only the differences below.

Tony's argument: $ARGUMENTS (a folder name, a full path, his own words, or empty).

## Differences in Antigravity

- **Who:** wherever that file says "the Claude Code session" or "you", read "you, the Antigravity
  agent". Run its commands in the terminal; `finish` can take several minutes (graphify), wait for
  it. Never `delegate.py`, Jev, OpenRouter, `frontier.py`, `lab_build_gemini.py` or another harness.
- **Approval is unchanged:** Tony typing `/lab-promote` with his own description IS the approval,
  including the commit and the push. Show him the Step 1 review, then keep going without asking.
  Stop only where the script refuses (an exit code) or the project is ambiguous (its Step 0).
- **Trailers (its Step 5):** add `--trailer` only for commit trailer lines your own instructions
  require; if none, leave `--trailer` out.

## Never do

Never run the printed cleanup commands, any delete, a force-push, `reset --hard`, or a pull/rebase
on your own. Never edit the promoted folder (that is a `/lab-run` fix). No new folders except the
one the script creates; if no `000_Wiki/` category fits, ask Tony. Everything in the plan's
"Wiring (Later, Tony-Approved)" list stays out: hand Tony that list at the end.
