# Gemini Agent Instructions — Agent-OS Workspace

> **For:** Gemini CLI agents operating in this workspace.
> **Claude Code users:** See `CLAUDE.md`. **Codex users:** See `AGENTS.md`.

This workspace is Tony's operating system for all business operations. The same rules apply across all agents — same brain, same procedures.

> [!NOTE]
> **Legacy Workspace Rename:** The workspace was formerly called `Claude-Agent` (or jokingly `clogged-agent`). Any IDE configs, startup URIs, or CLI integrations that still advertise `/Users/tonymacbook2025/Documents/Claude-Agent` must always be translated to `/Users/tonymacbook2025/Documents/Agent-OS/` on startup.



## Start Here

**Hard-enforced file rules (2026-09-27):** agents never delete files or folders (Tony deletes) and never create a new folder on their own: place work in an existing folder per `001_Architecture/Directory.md` and the nearest `Directory.md`, or ask Tony. Enforced for Claude Code, Codex and Gemini CLI by `001_Architecture/Scripts/fs_guard.py`; a block means stop and ask Tony, never find a workaround.

1. Read `001_Architecture/Install_Maps/Workspace-Map.md` — full folder map with explanations
2. Read `001_Architecture/Install_Maps/System-Map.md` — installed apps, CLIs, Homebrew packages, npm globals, MCPs, scripts, skills, and local tool paths
3. Read `001_Architecture/Memory/Core_Memory.md` — tiny always-read memory
4. Read `001_Architecture/Memory/Memory_Index.md` — routing layer for relevant memory
5. Read `TOOLBOX.md` before writing scripts or installing tools

Do not load every memory or log file by default. Use `claude-mem` for relevant memory injection/search, then targeted file reads based on `Memory_Index.md`.

**Model routing (Option B, 2026-09-27):** start every task on this harness's cheap default model. A `[Agent-OS router, Jev]` note may appear with your prompt; follow it.
- Answer questions and small edits yourself.
- Frontier work: don't do it inline yourself — delegate it. Claude: dispatch the `opus-standard` (or `opus-deep`) subagent. Codex: spawn the custom agent named `sol-standard` (or `sol-deep`) by that exact name — Codex only delegates when told to spawn a named agent directly, not when told where work "goes."
- Chores (ingest, sorting, tagging, renaming, bulk summaries) go to `python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/delegate.py "<task>" --skill <Skill_Name>`. Chores can take minutes, so run it in the background or with the maximum shell timeout (it stops the worker after 30 minutes). Then check the changed-files list it returns before reporting done.
- Brain dumps: split them into tasks and route each one. Never use Fable.

## Skills Registry

- The canonical skill library lives in `001_Architecture/Skills/`.
- Read `001_Architecture/Skills/Skill-Index.md` first when choosing a skill.
- Then open the matching `SKILL.md` file before using that skill.
- `001_Architecture/Scripts/sync_skill_index.py` regenerates the index when skills change.

## Full-Picture Mode (toggleable, cross-harness, locked 2026-10-17)

A thinking-partner mode for the pre-plan phase of any task (research, analytics, brainstorming, writing, planning/architecture) — not execution. Manual toggle only, never silently auto-on or auto-off. Full behavior spec: `001_Architecture/Skills/Full-Picture/SKILL.md` — read and follow it in full whenever Tony says "Full Picture," "let's go into Full Picture mode," or a similarly explicit on-phrase. Applies identically across Claude Code, Codex, Gemini CLI, Antigravity, and any other agent in this workspace.

**Analytic-Skill (cross-harness, 2026-10-20).** For any analysis, research, ranking, scoring, opportunity-finding or analytics-dashboard task, read and follow `001_Architecture/Skills/Analytic-Skill/SKILL.md` in full. It is a domain-agnostic method (real sourced evidence, user examples are seeds not checklists, outlier hunting, potential scoring, plan-before-run, visual minimal-word output) and applies identically across Claude Code, Codex, Gemini CLI, Antigravity and any other agent; pair it with Full-Picture and Tool-Manager.

## Dynamic Memory — Claude-Mem

`claude-mem` is installed for Gemini CLI and injects relevant context through `~/.gemini/GEMINI.md`.

- Worker status: `npx claude-mem status`
- Start worker: `npx claude-mem start`
- Viewer: `http://localhost:37701`
- Hooks live in `~/.gemini/settings.json`
- Use `<private>...</private>` tags for sensitive material that should not be stored.

Markdown memory should stay small and curated:
- `Core_Memory.md` — always-read bootstrap facts
- `Memory_Index.md` — memory routing
- `Global_Agent_Memory.md` — stable cross-agent decisions only
- `Logs/` and `Feedback_Loop/` — historical records, read only when relevant

## Session Memory — Write Automatically

Capture knowledge without being asked when Tony gives feedback, reveals preferences, validates an approach, or asks to wrap/save a session.

- Corrections and preferences → `001_Architecture/Feedback_Loop/YYYY-MM-DD_Feedback.md`
- Significant actions and files touched → `001_Architecture/Logs/YYYY-MM-DD_Session-Log.md`
- Durable cross-agent decisions → `001_Architecture/Memory/Global_Agent_Memory.md`
- Patterns after meaningful work → `001_Architecture/Self_Learning_Loop/YYYY-MM-DD_Self-Review.md`
- ALWAYS update all Workspace Maps, System Maps, TOOLBOX.md, and directory definitions to include any new folders, scripts, skills, or configurations before closing out a session.

Let `claude-mem` handle episodic memory. Do not turn markdown memory into a transcript.

## Ingest Procedure

**Follow `001_Architecture/Skills/ingest/SKILL.md` directly — not a summary of it.** It's the one canonical procedure, shared by Claude Code, Codex, and Gemini/Antigravity via the same symlinked `Skills/` folder (`~/.gemini/antigravity/skills` points at `001_Architecture/Skills`, confirmed 2026-10-09). This section previously restated the procedure from memory and that summary had already gone stale in a couple of places (wrong graphify scoping among them) — removed to stop re-summarizing something that changes over time. Use Gemini's native multimodal vision for the Step 1.5 image-analysis call where the skill asks for vision; everything else in the file applies exactly as written, including the newer dedup-check and Tool Catalog steps.

## File Naming

No spaces. Title-Case-With-Dashes.md. Acronyms uppercase. Python scripts exempt.

## Full Instructions

See `AGENTS.md` for the complete procedure. This file is a Gemini-focused bootstrap, with memory behavior mirrored from Claude and Codex.
