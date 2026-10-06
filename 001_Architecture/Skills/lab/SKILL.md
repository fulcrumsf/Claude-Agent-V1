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
| `/lab-build [plan]` | Sandboxed, network-off build of the locked plan: new files in one new folder only, inside a git worktree under `001_Architecture/Lab/`. Runner scores it on the plan's acceptance checks (60 + 15); `opus-standard` audits (25, cited); one fix round + one rebuild max; 80+ = cleared for `/lab-run`. | **Built 2026-10-03: Claude Code (`lab-build` skill). Not yet run on a real plan.** |
| `/lab-run [project]` | Tony's own real (paid if the tool needs it) use of a cleared build, no sandbox, in his normal session. Each round: his notes + 0-100 grade appended to `Run_Log.jsonl`; below 80 the harness (this session or `opus-standard`, never `/lab-build` or OpenRouter) fixes the build folder in place and he tries again; 80+ = cleared for `/lab-promote`. | **Built 2026-10-03: Claude Code (`lab-run` skill). Not yet run on a real build.** |
| `/lab-promote [project]` | Only after a `/lab-run` grade of 80+ (folder unchanged since). Commits the worktree's on-disk folder (the uncommitted `/lab-run` fixes) to its own lab branch, then `git checkout <that commit> -- <folder>` into the plan's real path; the session adds the TOOLBOX.md entry and the wiki page + cross-links (ingest convention); `graphify update` on the affected domains; one commit on main holding only those changes, pushed. Tony typing it is the approval. Cleanup commands printed, never run. | **Built 2026-10-03: Claude Code (`lab-promote` skill). Not yet run on a real build.** |

## Where things live

- Scripts: `001_Architecture/Scripts/lab_plan_draft.py` (+ `test_lab_plan_draft.py`), shared by every
  harness; `lab_plan_gemini.py` (+ `test_lab_plan_gemini.py`), the whole Gemini-side `/lab-plan`;
  `lab_build.py` (+ `test_lab_build.py`, 44 tests), the mechanical half of `/lab-build` (reuses
  `lab_plan_draft.py`'s picker, key checks and log; `--preflight` is a free live containment test);
  `lab_run_log.py` (+ `test_lab_run_log.py`, 14 tests), the bookkeeping half of `/lab-run`
  (`status` = is it cleared + rounds so far, `log` = append one graded round, `checks` = free
  re-run of the acceptance checks after a fix, writes nothing). It never calls a model or the network.
  `lab_promote.py` (+ `test_lab_promote.py`, 37 tests on throwaway git repos with a local stand-in
  remote), the git half of `/lab-promote`: `list`, `plan` (read-only gate + review), `checkout`
  (lab-branch commit of the graded folder, then the one-folder checkout), `finish` (graphify, the
  main commit from a private index so other sessions' uncommitted work is never swept in, push,
  cleanup commands printed). Its only network call is the `git push`.
- Commands: one skill folder per command here in `001_Architecture/Skills/` (`lab-plan/`,
  `lab-build/`, `lab-run/`, `lab-promote/`). Claude Code reads them through the `~/.claude/skills`
  symlink, so `/lab-plan`, `/lab-build`, `/lab-run` and `/lab-promote` are those skills.
- Projects: `001_Architecture/Lab/YYYY-MM-DD_Title_Slug/` (gitignored). File contract for
  `/lab-plan` output (`Draft_Raw.md`, `Draft_Meta.json`, `Score.json`, `Plan_Locked.md`,
  `Acceptance_Checks.json`, `Review.md`) is in `lab-plan/SKILL.md`. `/lab-build` adds, in the same
  folder: `Build_Worktree_<n>/` (git worktree, branch `lab/<project>/wt<n>`, never pushed; the built
  folder sits inside it at the plan's promoted path), `Build_Meta.json`, `Build_Score.json`
  (written once, read-only), `Build_Audit.json`, `Build_Review.md`, `Build_Verdict.json`, and the
  `_Fix` / `_Rebuild` variants; contract in `lab-build/SKILL.md`. The builder can only write inside
  its one folder, so `Acceptance_Checks.json` and every score file stay out of its reach.
  `/lab-run` adds only `Run_Log.jsonl` (one appended line per round: what Tony tried, his notes,
  his grade, what the harness changed before that try, a fingerprint of the folder as graded) and
  edits the build folder in place inside the worktree, uncommitted; contract in `lab-run/SKILL.md`.
  It is Tony's grade of the built tool, separate from any log the tool itself keeps.
  `/lab-promote` adds only `Promote_Meta.json` (stage, lab commit, destination, main commit, push
  result) and one commit on the project's lab branch when `/lab-run` left fixes uncommitted (the
  branch otherwise still holds `/lab-build`'s pre-fix version). In the real workspace it creates the
  plan's one folder, edits TOOLBOX.md and `000_Wiki/`, and makes one commit on main; contract in
  `lab-promote/SKILL.md`. The worktree and lab branch stay until Tony runs the printed cleanup.
- Containment for `/lab-build`: `codex exec -s workspace-write` with the build folder as the only
  writable folder, plus `-c sandbox_workspace_write.network_access=false`. That pin is load-bearing:
  Tony's `~/.codex/config.toml` sets `network_access = true`, and a live probe on 2026-10-03 reached
  the internet from inside the build sandbox without it (the earlier "network off by default" check
  used `codex sandbox`, a different path). Every build re-proves this for free first (preflight
  against a local fake model) and stops before spending if anything is open. Acceptance checks run
  in `codex sandbox -P :workspace` (same limits). After the build, a git check (not a model) fails
  the run on any edit, delete, rename, link or file outside the folder: exit 8, zero fixes.
- Logs: `~/Library/Logs/Agent-OS-Lab.jsonl` (one line per draft, review and verify, with model and
  score, for tuning the picker; `/lab-run` adds a `lab_run_grade` line per round with the
  `/lab-build` score beside Tony's grade, for calibration), `~/Library/Logs/Agent-OS-Lab-Plan-<stamp>.log` (full draft worker run)
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
- A build counts against the same $2 (plan spend is subtracted first). Worst case is priced at
  1.2M input + 60K output tokens; candidates over $1.50 are skipped (so `glm-5.3` is skipped for
  builds today and `deepseek-v4-pro` leads), and `lab_build.py` polls the key while the worker
  runs and stops it if the project would go over. The Opus audit, fix and rebuild run on Claude's
  plan, not OpenRouter.
- `/lab-run` spends nothing from the $2: every fix is made by the harness on Claude's plan (locked
  rule, never `/lab-build` or an OpenRouter model). A tool that makes paid calls when used for real
  spends behind its own cost pauses, like any pipeline.

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
  The trigger skill is `.agents/skills/lab-plan-antigravity/SKILL.md` — the one skill folder the IDE
  actually loads besides its plugins (checked in its live system prompt 2026-09-30: it does NOT read
  `001_Architecture/Skills/` or the `~/.gemini/skills` symlinks). **Built 2026-09-30, Tony approved.**
  Running the script directly from any terminal also still works, same as before.
- Do not run `lab-plan`, `lab-build`, `lab-run` or `lab-promote` (the Claude skills) from Codex or
  Antigravity; they need Claude Code's Agent tool (and `/lab-run`'s fixes must stay on one harness
  every round). `/lab-build`, `/lab-run` and `/lab-promote` have no Gemini or Codex trigger yet.
