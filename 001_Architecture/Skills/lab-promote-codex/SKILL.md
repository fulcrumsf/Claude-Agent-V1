---
name: lab-promote-codex
description: Codex only. Runs when Tony types $lab-promote-codex [project, or his own words for what is being promoted] (or "/lab-promote" in Codex) - the last /lab step for a build he graded 80+ in /lab-run. Moves the one folder into the real workspace, adds its TOOLBOX.md entry and wiki page, runs graphify, commits only those changes to main and pushes. Claude Code - use lab-promote. Antigravity - use lab-promote-antigravity.
disable-model-invocation: true
---

# /lab-promote (Codex)

`/lab-promote` has no harness-only step: `lab_promote.py` does every git step and check, and the
session it runs in (here, you) writes the TOOLBOX.md entry and the wiki page. So there is one set
of instructions for every harness. Read
`/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/lab-promote/SKILL.md` in full now
and follow its Steps 0-6 exactly, with only the differences below.

Tony's argument: whatever he typed after the command (a folder name, a full path, his own words, or
nothing).

## Differences in Codex

- **Who:** wherever that file says "the Claude Code session" or "you", read "this Codex session".
  Never `delegate.py`, Jev, OpenRouter, `frontier.py`, a subagent, or another harness.
- **Approval is unchanged:** Tony typing the command with his own description IS the approval,
  including the commit and the push. Show him the Step 1 review, then keep going without asking.
  Stop only where the script refuses (an exit code) or the project is ambiguous (its Step 0).
- **Running `lab_promote.py`:** run `checkout` and `finish` outside Codex's sandbox (request
  escalated permission, justification: "git worktree commit, graphify, and the push to GitHub").
  `finish` can take several minutes (graphify): give it a long timeout.
- **Trailers (its Step 5):** add `--trailer` only for commit trailer lines your own instructions
  require; if none, leave `--trailer` out.

## Never do

Never run the printed cleanup commands, any delete, a force-push, `reset --hard`, or a pull/rebase
on your own. Never edit the promoted folder (that is a `/lab-run` fix). No new folders except the
one the script creates; if no `000_Wiki/` category fits, ask Tony. Everything in the plan's
"Wiring (Later, Tony-Approved)" list stays out: hand Tony that list at the end.
