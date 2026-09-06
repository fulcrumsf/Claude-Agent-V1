---
title: "Agent-OS Context Architecture Hardening Plan Prompt"
type: prompt
category: architecture
tags:
  - context-efficiency
  - memory-systems
  - implementation-plan
  - source-of-truth
  - resume-notes
created: 2026-09-05
source: codex
---

# Agent-OS Context Architecture Hardening Plan Prompt

Use this prompt after reviewing the context-efficiency audit reports. Its purpose is to generate a risk-controlled plan, double-check that plan for safety, and then implement only low-risk approved improvements.

## Prompt

You are working inside `/Users/tonymacbook2025/Documents/Agent-OS/`.

Your job is to create a risk-controlled plan to harden Agent-OS context efficiency, memory routing, source-of-truth hierarchy, and project resume behavior, then double-check that plan for safety before implementing only the approved, low-risk changes.

Do not delete files. Do not remove memory systems. Do not rewrite pipeline architecture. Do not simplify video-production skills aggressively. Do not change Graphify/wiki behavior unless the plan explicitly proves the change is low-risk and reversible. Preserve all existing files.

## Goal

Improve Agent-OS so Claude Code, Codex, Gemini, and future agents can work with the smallest sufficient context for the current task while preserving continuity, hard-earned production lessons, feedback, and rollback safety.

The target architecture is:

1. `Core_Memory.md` stays tiny and always-read.
2. `Memory_Index.md` becomes the main memory-routing layer.
3. `Global_Agent_Memory.md` stores durable cross-agent rules only.
4. Logs, feedback, and self-review remain as historical evidence, not default context.
5. Graphify remains the main selective retrieval layer.
6. Wiki remains distilled knowledge.
7. Resource Library remains source/reference material.
8. Skills remain the operational source of truth for repeatable workflows.
9. Active projects and productions get compact resume-state files.
10. Agents get a clear source-of-truth hierarchy so duplicated lessons do not confuse them.

## First: Inspect Before Planning

Read these first:

- `AGENTS.md`
- `CLAUDE.md`
- `GEMINI.md`
- `TOOLBOX.md`
- `BUSINESS_CONTEXT.md`
- `001_Architecture/Memory/Core_Memory.md`
- `001_Architecture/Memory/Memory_Index.md`
- `001_Architecture/Memory/Global_Agent_Memory.md`
- `001_Architecture/Memory/Codex_Memory.md`
- `001_Architecture/Install_Maps/Workspace-Map.md`
- `001_Architecture/Graphify/REGISTRY.md`
- `001_Architecture/Audit_Reports/Claude-Code-Context-Efficiency-Audit-Prompt.md`
- `001_Architecture/Audit_Reports/Codex-Context-Efficiency-Audit-Report-2026-09-05.md`
- relevant recent files in `001_Architecture/Feedback_Loop/`
- relevant recent files in `001_Architecture/Logs/`
- relevant recent files in `001_Architecture/Self_Learning_Loop/`

If the task touches skills, also read:

- `001_Architecture/Skills/Skill-Index.md`
- `001_Architecture/Skills/codex-agent-os-hardening/SKILL.md`
- any directly relevant `SKILL.md` files

Use targeted reads. Do not bulk-load every log, feedback file, skill, wiki page, or resource-library document.

## Recommended Architecture To Implement

Define and document this source-of-truth hierarchy:

1. Executable scripts, tests, guards, and validated automation
2. Active skill instructions
3. Current project or production resume-state files
4. Global cross-agent memory
5. Wiki and Graphify retrieval
6. Logs, feedback, self-review, and report cards as supporting evidence

Clarify that when the same rule appears in multiple places, the higher layer wins unless a newer lower-layer entry is clearly a correction that has not yet been promoted.

## Required Improvements

Create a plan for these improvements:

1. Make `Memory_Index.md` the clear routing layer for memory and context loading.
2. Keep `Core_Memory.md` short and always-read.
3. Clarify that logs, feedback, and self-review should be read only when relevant.
4. Add a concise source-of-truth hierarchy to the appropriate architecture/memory docs.
5. Add or standardize a compact `RESUME_NOTES.md` pattern for active productions/projects.
6. Clarify how agents should continue work from a phrase like "continue AnomalousWild where we left off."
7. Clarify what should not be loaded by default for unrelated tasks.
8. Preserve Graphify as query-on-demand, not bulk context.
9. Preserve Wiki as distilled knowledge and Resource Library as source material.
10. Preserve skills as operational runbooks, but avoid loading unrelated skills.
11. Document a background-job contract pattern:
    - task id location
    - state file location
    - polling owner
    - whether it survives agent shutdown
    - resume command
    - completion signal
12. Update only documentation, memory routing, templates, or indexes unless Tony explicitly approves deeper architecture/code changes.

## Plan Requirements

Before implementing anything, produce a Markdown plan with:

- Executive summary
- Files proposed for change
- Exact reason each file needs changing
- Risk level for each change
- Rollback approach
- What will not be changed
- Verification steps
- Open questions for Tony

Classify every proposed change:

- `Low risk / safe to implement`
- `Medium risk / ask Tony before implementing`
- `High risk / do not implement yet`
- `Needs measurement first`

## Safety Review Before Implementation

After writing the plan, perform a second-pass review of your own plan.

Check for:

- Any accidental architecture rewrite
- Any deletion, move, rename, or cleanup
- Any change to production pipeline behavior
- Any change to Graphify outputs
- Any change to Obsidian settings
- Any change to scripts/config/code
- Any change that could break Claude Code, Codex, or Gemini startup
- Any duplicated rule that might create contradiction
- Any overly broad instruction that could cause future context bloat

Write a `Plan Safety Review` section.

If any change is medium/high risk, stop and ask Tony before implementing it.

## Implementation Rules

Only implement changes that are clearly low-risk documentation/routing/template improvements.

Allowed examples:

- Adding a concise source-of-truth hierarchy to memory docs
- Clarifying startup/context-loading policy
- Adding a `RESUME_NOTES.md` template
- Adding a background-job contract template
- Updating directory maps to reference new templates
- Updating session logs/feedback/self-review to record what changed

Not allowed without Tony approval:

- Deleting or archiving files
- Moving folders
- Removing memory systems
- Rewriting skills heavily
- Changing scripts
- Changing Graphify outputs
- Changing Obsidian settings
- Changing automation hooks
- Changing active production files beyond adding an approved resume template

## Suggested Deliverables

Prefer creating these, if the plan confirms they fit the existing architecture:

1. `001_Architecture/Memory/Context_Loading_Policy.md`
   - Defines smallest-sufficient-context rules.
   - Explains what loads automatically vs. what is queried on demand.
   - Gives examples for video production, app work, skill editing, debugging, ingest, and strategy.

2. `001_Architecture/Memory/Source_Of_Truth_Hierarchy.md`
   - Defines authority order.
   - Explains how to resolve duplicated rules.
   - Explains when logs/feedback should be promoted into skills or guards.

3. `001_Architecture/Templates/RESUME_NOTES_Template.md`
   - Reusable template for active projects and productions.
   - Includes current status, next authorized step, blocked items, files that matter, files not to touch, latest approved version, approval gates, and resume command.

4. `001_Architecture/Templates/Background_Job_Contract_Template.md`
   - Reusable template for async generation jobs and polling workflows.
   - Includes provider, task id, state file, polling owner, survives shutdown yes/no, resume command, completion signal, and failure handling.

5. Updates to:
   - `Memory_Index.md`
   - `Core_Memory.md` only if truly needed and kept short
   - `AGENTS.md`
   - `CLAUDE.md`
   - `GEMINI.md`
   - `TOOLBOX.md` only if new templates/docs are created
   - `001_Architecture/Directory.md` only if new files/folders are created

Before creating new folders, check whether an appropriate folder already exists. If a new folder is needed, ask Tony first unless he has already approved it.

## Verification

After implementation:

1. Show a changed-files list.
2. Verify every new file exists and has content.
3. Verify every referenced path is correct.
4. Search for the key phrases:
   - `smallest sufficient context`
   - `source of truth hierarchy`
   - `resume notes`
   - `background job contract`
5. Confirm no code, scripts, pipeline configs, Graphify outputs, or Obsidian settings were modified.
6. Write a short session-log entry.
7. If the changes created a durable preference or rule, update global memory compactly.

## Final Response

Return:

- What was planned
- What was implemented
- What was intentionally not changed
- Files changed
- Verification performed
- Any remaining decisions Tony should make
