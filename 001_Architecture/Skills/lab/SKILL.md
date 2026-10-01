---
name: lab
description: Background reference for Tony's /lab system (/lab-plan, /lab-build, /lab-run, /lab-promote) - a middle lane where a picked cheap OpenRouter model drafts and builds new things in a contained Lab folder, Opus reviews and scores them, and nothing reaches the real workspace until Tony promotes it. Read this when asked what /lab is, what state it is in, or where lab projects live. Not a command itself.
user-invocable: false
---

# /lab system

Canonical design (Tony-approved, 2026-09-29/30): `001_Architecture/Ongoing-Agent-OS-To-Do-List.md`,
section "Part 4: OpenRouter middle-lane picker" to the end of the file. This page only summarizes
it and tracks build state. If they disagree, the to-do list wins.

## Purpose

Non-chore, multi-step work (new tools, pipelines, scripts) gets a first draft from a deliberately
picked, cheaper OpenRouter model instead of Opus, inside hard containment. Opus still reviews and
scores every step; Tony grades the real result. Explicit trigger only: Tony types the command. Jev
never routes into `/lab`, and there is no "lab mode" left switched on across messages.

## The four commands

| Command | What it does | State |
|---------|--------------|-------|
| `/lab-plan <question>` | Picked model drafts a plan read-only. `opus-standard` scores the RAW draft 0-100, writes acceptance checks, then locks (80+) or regenerates once on Opus (below 80). | **Built 2026-09-30: Claude Code (`lab-plan` skill) + Gemini/Antigravity (`lab_plan_gemini.py`)** |
| `/lab-build` | Sandboxed, network-off build of the locked plan: new files in one new folder only, inside a git worktree under `001_Architecture/Lab/`. Runner scores it on the plan's acceptance checks; `opus-standard` audits. | Not built |
| `/lab-run` | Tony's own real (paid) runs from his harness session, iterated by the harness model until Tony grades it 80+. | Not built |
| `/lab-promote` | Copies the folder into the workspace, updates TOOLBOX.md, wiki, graphify, commits and pushes. Tony typing it is the approval. | Not built |

## Where things live

- Scripts: `001_Architecture/Scripts/lab_plan_draft.py` (+ `test_lab_plan_draft.py`), shared by every
  harness; `lab_plan_gemini.py` (+ `test_lab_plan_gemini.py`), the whole Gemini-side `/lab-plan`.
- Commands: one skill folder per command here in `001_Architecture/Skills/` (`lab-plan/` so far).
  Claude Code reads them through the `~/.claude/skills` symlink, so `/lab-plan` is that skill.
- Projects: `001_Architecture/Lab/YYYY-MM-DD_Title_Slug/` (gitignored). File contract for
  `/lab-plan` output (`Draft_Raw.md`, `Draft_Meta.json`, `Score.json`, `Plan_Locked.md`,
  `Acceptance_Checks.json`, `Review.md`) is in `lab-plan/SKILL.md`. `/lab-build` must keep
  `Acceptance_Checks.json` and `Score.json` outside the builder's writable folder.
- Logs: `~/Library/Logs/Agent-OS-Lab.jsonl` (one line per draft, review and verify, with model and
  score, for tuning the picker), `~/Library/Logs/Agent-OS-Lab-Plan-<stamp>.log` (full draft worker run)
  and `~/Library/Logs/Agent-OS-Lab-Review-Gemini-<stamp>.log` (full Gemini review, tool calls included).

## Model picker (first pass)

`lab_plan_draft.py --list` prints the table. A small curated list (DeepSeek, GLM, Qwen, Gemini
Flash, Kimi, MiniMax), ordered per task type (code / content / general, from keywords in the
question), checked against OpenRouter's live model list and prices each run. Not a scraped
leaderboard: reorder it from the logged scores once ~10-15 graded runs exist. `--model <id>`
overrides.

## Money

- Key: the existing `OPENROUTER_CHORES_KEY` (Tony declined a separate lab key for now).
- Cap: $2 per lab project. Over it, the script stops and asks Tony for a yes to raise (`--cap`),
  never a silent overspend. It also keeps $1 on the shared key so Jev routing never runs dry.
- A plan draft is about $0.10-0.50 (first real test: $0.16 on `z-ai/glm-5.3`).

## Other harnesses

- Codex: not wired yet (separate task; its reviewer path would be `frontier.py`).
- Gemini: the standalone `gemini` CLI is dead for Tony's account (`IneligibleTierError`, all modes,
  any tier; do not try to log in or route around it). Tony uses Gemini only inside the Antigravity
  IDE, whose chat has no headless mode, so there is no Gemini session to follow `lab-plan/SKILL.md`.
  Instead one self-contained script does the whole command:
  `python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/lab_plan_gemini.py "<question>"`
  (same `--model`, `--name`, `--cap` flags as the draft script, plus `--review-model`). It runs
  `lab_plan_draft.py` unchanged, then reviews with Gemini's top Pro model (picked live, 2026-09-30:
  `gemini-3.1-pro-preview`, thinking high) through the `google-antigravity` SDK and `GEMINI_API_KEY`,
  then runs `--verify`. Same rubric, same six files, same score-before-edit check. The reviewer has
  read-only tools confined to Agent-OS (secret-looking paths blocked) and never writes files: the
  script writes `Score.json` first (read-only at once) before it even asks for the plan.
  `--review <project_folder>` re-runs only the review (never re-scores an existing `Score.json`);
  `--check` is a free setup check. Review cost goes on the Gemini API key: first real run used
  ~$0.30 at list price (about $0 if the key is free tier); hard budget per review ~$1.48, and
  draft + review worst case over the project cap stops and asks Tony (`--cap`).
- How Tony runs it in Antigravity: type `/lab-plan <question>` in the IDE agent chat; the agent runs
  the script (it can run terminal commands and waits for long ones) and relays the printed report.
  This needs the trigger skill `lab-plan-antigravity` in `Agent-OS/.agents/skills/`, the only skill
  folder the IDE loads besides its plugins (checked in its live system prompt 2026-09-30: it does
  NOT read `001_Architecture/Skills/` or the `~/.gemini/skills` symlinks). That folder is not
  created yet; it needs Tony's OK. Until then, run the command above in any terminal.
- Do not run `lab-plan` (the Claude skill) from Codex or Antigravity; it needs Claude Code's Agent tool.
