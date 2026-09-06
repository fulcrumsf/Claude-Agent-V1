---
name: codex-agent-os-hardening
description: "Use this skill whenever Codex or any OpenAI-compatible agent starts work in Agent-OS, when Tony says Codex is missing Claude Code habits, when a task touches memory/logs/feedback/folder routing/skills, or when Tony corrects agent behavior. This skill mirrors the Claude Code operating discipline for Agent-OS: read the right manuals, use the shared memory layers, wait for approval on recommendations before acting, preserve files, update feedback/logs/memory, and close sessions cleanly."
---

# Codex Agent-OS Hardening

This skill makes Codex behave like a trained Agent-OS operator instead of a fresh assistant. Use it as the operating checklist for work inside `/Users/tonymacbook2025/Documents/Agent-OS/`.

## Why This Matters

Agent-OS is Tony's whole business operating system. Claude Code, Codex, Gemini, Antigravity, and other agents must share the same folder rules, memory habits, feedback loop, and preservation discipline. Tony should not have to reteach Codex rules that Claude already knows.

## Startup Checklist

At the start of Agent-OS work, orient from the shared manuals before exploring blindly:

1. Read `/Users/tonymacbook2025/Documents/Agent-OS/AGENTS.md`.
2. Read `001_Architecture/Memory/Core_Memory.md`.
3. Read `001_Architecture/Memory/Memory_Index.md`.
4. Read `001_Architecture/Install_Maps/Workspace-Map.md` for folder routing.
5. Read `TOOLBOX.md` before writing scripts, installing tools, or inventing a new workflow.
6. Read `001_Architecture/Skills/Skill-Index.md`, then open the relevant `SKILL.md` before using a skill.
7. Read recent logs or feedback only when relevant; do not load every memory/log file by default.

Prefer targeted retrieval over bulk context loading. The goal is the smallest sufficient context for the current task.

For broad onboarding or "understand Agent-OS" requests, prioritize the numbered top-level departments. Tony's hierarchy is:

1. `001_Architecture`
2. `002_Content-Creation`
3. `007_Resource_Library`

Usually skip `000_Ingest` unless the task is specifically about ingesting or organizing raw intake.

## Approval Boundary

When Tony asks for a recommendation, suggestion, options, or where something should go:

- Give the recommendation.
- Explain the tradeoff if useful.
- Wait for Tony's reply before creating directories, scaffolding, files, or moving anything.

Do not treat "recommend" as "recommend and implement." This is a hard operating rule because Tony uses recommendation requests to make routing decisions before work begins.

## File And Folder Discipline

Follow the existing directory maps. Do not create new top-level folders or new category folders unless Tony explicitly approves the destination.

Default routing:

- Architecture, memory, skills, logs, audits, tools: `001_Architecture/`
- Synthesized durable knowledge: `000_Wiki/`
- Raw/reference materials: `007_Resource_Library/`
- Active video/content work: `002_Content-Creation/`
- App builds: `003_Apps/`
- Games: `004_Games/`
- E-commerce: `005_Ecommerce/`
- Websites: `006_Websites/`
- Investments: `008_Investments/`
- AI job references: `009_AI_Jobs/`

Naming convention:

- Default Agent-OS docs/folders use Title_Case_With_Underscores or Title-Case-With-Dashes according to local convention.
- Preserve existing naming style in the destination folder.
- Skill directory names can remain lowercase-kebab-case when that matches the skill registry convention.
- Python scripts and config files follow the language/tool convention when renaming would break imports or tooling.

## Preservation Rules

Never delete, trash, overwrite, or destructively rename source files. If an item should be removed, report it and wait.

For generated artifacts, storyboards, prompts, renders, audio, videos, and pipeline outputs:

- Preserve prior iterations.
- Use the next version number for replacements.
- Move superseded versions only into an approved `Archived/` destination.
- Never overwrite paid or expensive artifacts.

## Memory And Feedback Writes

Capture Tony's preferences and corrections without waiting for him to say "remember this."

Use these layers:

- `001_Architecture/Feedback_Loop/YYYY-MM-DD_Feedback.md` for corrections, preferences, and validated approaches.
- `001_Architecture/Logs/YYYY-MM-DD_Session-Log.md` for significant work, decisions, files touched, and pending state.
- `001_Architecture/Memory/Global_Agent_Memory.md` for durable cross-agent rules and stable preferences.
- `001_Architecture/Memory/Codex_Memory.md` only for Codex-specific quirks that should not apply globally.
- `001_Architecture/Self_Learning_Loop/YYYY-MM-DD_Self-Review.md` after meaningful sessions to record patterns, mistakes, and improvements.

Keep memory concise and operational. Do not store transcript-like detail, secrets, noisy session chatter, or one-off implementation trivia in global memory.

## When Tony Corrects You

Treat corrections as system hardening data.

1. Acknowledge the correction directly.
2. Identify whether it is a one-off preference, recurring workflow rule, or hard rule.
3. Record it in the feedback loop.
4. If durable across agents, add a compact entry to global memory.
5. If Codex-specific, add it to Codex memory.
6. If it changes folder routing or operating procedure, update the relevant directory/manual file.
7. Log the session change.

If you repeat a previously corrected behavior, stop and acknowledge the repeat before continuing.

## Work Execution Rules

- Use existing tools and skills before writing new scripts.
- Use `rg` for searching when available.
- Use targeted file reads rather than broad dumps.
- Do not modify architecture, memory, configs, or code when the task is only an audit or recommendation.
- Verify meaningful changes before saying they are done.
- If verification is blocked, say what could not be verified and why.
- Keep user updates concise and non-technical unless Tony asks for technical detail.

## Closeout Checklist

When Tony says to wrap up, save memory, close the session, or when a meaningful Agent-OS task ends:

1. Update the session log with what changed, why, files touched, and pending state.
2. Update the feedback loop for corrections, preferences, and validated approaches.
3. Update global memory for durable cross-agent rules.
4. Update Codex memory for Codex-only lessons.
5. Add a self-review if the session included meaningful mistakes, repeated patterns, or process improvements.
6. Update directory maps, skill index, and TOOLBOX when new folders, skills, scripts, tools, or configs were created.
7. Run the appropriate verification command or file existence/search check.
8. Final response should clearly state what changed and what was not changed.

## Quick Mental Model

Codex should behave like a careful new employee who reads the manual, checks the filing rules, uses existing tools, asks before changing structure, writes down durable lessons, and leaves the next agent a clean trail. Agent-OS is the business operating system: Architecture is the brain, Content Creation is the active production engine, Resource Library and Wiki are the knowledge layers, Graphify is selective retrieval, and skills are hardened runbooks.
