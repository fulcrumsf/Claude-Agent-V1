---
title: "Codex Context Efficiency Audit Report"
type: audit-report
category: architecture
tags:
  - context-efficiency
  - memory-systems
  - graphify
  - wiki
  - codex
created: 2026-09-05
source: codex
---

# Codex Context Efficiency Audit Report

**Exact file path:** `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Audit_Reports/Codex-Context-Efficiency-Audit-Report-2026-09-05.md`

**Audit mode:** Read-only analysis plus creation of this report. No pipeline architecture, memory system, config, code, Graphify output, Obsidian settings, or production files were modified as part of the audit itself.

**Important limitation:** This is a first-pass Codex audit, not the final Claude Code audit. I can inspect workspace files, but I cannot directly measure Anthropic's private Messages/context usage bucket or Claude Code's exact runtime token accounting. Claims about actual usage impact are therefore classified as inference unless grounded in local files.

## 1. Executive Summary

Agent-OS already has the right strategic direction: it is moving away from "load everything" and toward a layered memory system where small bootstrap files point to targeted retrieval through memory, Graphify, wiki, skills, logs, and project state. The main risk is not lack of memory. The risk is too many overlapping memory-like systems that all contain useful truth, causing agents to over-read because they cannot easily tell which layer is authoritative for the current task.

Top likely context-bloat causes:

1. Startup instructions point agents at many high-value but potentially large files and folders: logs, feedback, self-learning, memory, Graphify registry, TOOLBOX, maps, skills, and department `CLAUDE.md` files.
2. Skills are powerful but very large. Many production skills are full runbooks with historical incident lessons, exact gates, prompt rules, and pipeline constraints.
3. Logs, feedback, self-learning, report cards, production notes, and wiki pages duplicate lessons at different levels of abstraction.

Top likely lost-continuity causes:

1. Some current-state knowledge lives in recent logs or production folders rather than a compact "current resume state" pointer.
2. Background jobs and provider task status are mostly script/session driven. If the agent session dies, polling may not continue unless a process was deliberately launched outside the interactive session.
3. Agents may read the wrong layer: too much historical context, too little current production state, or stale department docs instead of the governing skill/script.

Highest-confidence recommendations:

- Keep `Core_Memory.md` and `Memory_Index.md` small and always-read.
- Make Graphify, wiki, and Resource Library query-on-demand layers, not startup context.
- For each active production, maintain one compact `RESUME_NOTES.md` or equivalent state file that points to the minimum necessary files.
- Treat skills as executable runbooks to open only when the task triggers them.
- Consolidate repeated lessons upward into governing skills or executable checks, then keep logs as historical evidence.

## 2. System Map

Confirmed:

- `AGENTS.md` defines OpenAI/Codex-facing rules. It says Agent-OS is Tony's operating system for business operations, content creation, e-commerce, apps, and games (`AGENTS.md:8-12`).
- `CLAUDE.md` defines Claude Code-facing rules and includes context-efficiency guidance (`CLAUDE.md:10-15`).
- `GEMINI.md` defines Gemini CLI-facing rules and mirrors the same shared-brain concept (`GEMINI.md:1-6`).
- `001_Architecture/Memory/` contains bootstrap memory, shared memory, memory index, and Codex-specific memory.
- `001_Architecture/Graphify/REGISTRY.md` is a federation registry for domain-specific graphs (`REGISTRY.md:8-18`).
- `000_Wiki/` is synthesized durable knowledge.
- `007_Resource_Library/` is raw/reference material.
- `002_Content-Creation/Video_Editor/` is the active content-production engine.
- `001_Architecture/Skills/` contains hardened runbooks that agents should open only when relevant.

Inferred:

- Agent-OS is evolving toward a model-neutral second brain: Obsidian is the human-facing vault, Graphify is the query graph, wiki is distilled knowledge, Resource Library is source material, and skills are operational procedure.

## 3. Automatic Context Loading

What appears to load or be read early:

- `AGENTS.md` tells OpenAI-compatible agents to read `Workspace-Map.md`, `System-Map.md`, `Core_Memory.md`, `Memory_Index.md`, and recent logs before exploring (`AGENTS.md:35-42`).
- `GEMINI.md` gives Gemini a similar startup list and explicitly says not to load every memory/log file by default (`GEMINI.md:13-21`).
- `CLAUDE.md` tells Claude to use `claude-mem`, read memory routing files, and avoid loading every memory/log file by default (`CLAUDE.md:57-75`).
- `CLAUDE.md` also says to start every session by reading the Graphify federation registry (`CLAUDE.md:131-133`).
- `Core_Memory.md` explicitly says always read only core memory and the memory index, then use targeted reads or `claude-mem` (`Core_Memory.md:24-33`).

Main tension:

- Some files say "read recent logs" while others say "do not load every memory/log file by default." This is not a contradiction if interpreted as targeted recent-log retrieval, but agents can easily over-interpret it as permission to load too much history.

Unknown:

- Exact Claude Code auto-injection behavior from `~/.claude/...` was not measured in this audit.
- Exact Codex Desktop app prompt composition was not measured.
- Exact `claude-mem` injected payload size was not measured.

## 4. Memory And Knowledge Systems

| System | Purpose | Value | Context Cost | Duplication Risk |
|---|---|---:|---:|---:|
| `Core_Memory.md` | Tiny bootstrap rules | High | Low | Low |
| `Memory_Index.md` | Routing layer for memory | High | Low | Low |
| `Global_Agent_Memory.md` | Durable cross-agent rules | High | Medium if it grows | Medium |
| `Codex_Memory.md` | Codex-specific lessons | Medium | Low | Medium with global memory |
| `Feedback_Loop/` | Corrections/preferences/validated approaches | High | High if bulk-read | Medium |
| `Logs/` | Session summaries and touched files | High for resume | High if bulk-read | High |
| `Self_Learning_Loop/` | Retrospectives and recurring patterns | High | Medium | Medium |
| `000_Wiki/` | Synthesized durable knowledge | High | High if bulk-read | Medium |
| `007_Resource_Library/` | Source/reference material | High | Very high if bulk-read | Low if indexed |
| Graphify | Selective relationship/query layer | Very high | Low per query | Low |
| Skills | Operating runbooks | Very high | Medium/high per skill | Medium |
| Report cards / production notes | Quality and current state | High for production | Medium/high | Medium |

Conclusion: the system should keep all these layers, but each layer needs a clear loading policy. The goal is not deletion; it is routing.

## 5. Graphify, Obsidian, And Wiki Layer

Graphify is already positioned correctly as a selective retrieval layer. The registry says each domain has its own graph and that `000_Ingest/` is excluded because it is temporary staging (`REGISTRY.md:10-12`). It also says graph queries are much cheaper than raw grep/file reads (`REGISTRY.md:16-18`).

The federation design is a good context-efficiency choice. The registry explicitly prefers per-domain graphs over a single union graph (`REGISTRY.md:83`). That supports Tony's goal: ask a concept question, query the relevant domain, then load only the files that matter.

Current risk:

- Some graphs are built while many are pending. Architecture and Video Editor are built; Wiki, Apps, Games, Ecommerce, Resource Library, and others are pending in the registry snapshot (`REGISTRY.md:22-37`).
- If an agent sees Graphify as unreliable because many domains are pending, it may fall back to broad file reads.

Recommendation:

- Keep Graphify as query-on-demand.
- Make `REGISTRY.md` the routing table.
- Maintain a compact "domain graph freshness" status.
- Do not load wiki/resource-library folders wholesale.

## 6. Feedback, Logs, Self-Learning, And Report Cards

These systems are valuable but should not all be loaded into active context.

Best use:

- Feedback loop: load when Tony's preference or a recurring correction is relevant.
- Session logs: load only the latest relevant task log or specific handoff.
- Self-learning loop: use to improve process after mistakes or major sessions.
- Report cards: load only for the active production or channel reference.

Duplication pattern:

- A production mistake may appear in a report card, session log, feedback file, self-review, skill update, and memory entry.
- This is not automatically bad. The problem is when future agents cannot tell which copy is current or authoritative.

Recommended authority order:

1. Executable guard/test/script when the lesson can be enforced.
2. Governing skill when it is procedural.
3. Current project state file when it is production-specific.
4. Global memory when it is durable and cross-agent.
5. Logs/feedback/self-review as evidence, not primary instructions.

## 7. Video Pipeline Continuity

For a request like "continue AnomalousWild where we left off," the smallest sufficient context should be:

- Root bootstrap: `AGENTS.md` or `CLAUDE.md`, `Core_Memory.md`, `Memory_Index.md`.
- Graphify registry, then Video Editor graph query.
- Video Editor `CLAUDE.md` because it contains department rules and graph-first routing (`Video_Editor/CLAUDE.md:12-30`).
- The specific channel/production folder's current `RESUME_NOTES.md`, `Generation_Log.json`, `Report_Card.md`, `Shot_List.md`, and relevant `Data/` files.
- The exact triggered pipeline skill, such as Anomalous Wild, Neon Parcel, or Reimagined Realms.
- Tool Manager only when choosing a model/tool or verifying current provider capability.

What should not be loaded by default:

- All prior production logs.
- All wiki pages.
- All Resource Library docs.
- Full skill library.
- Unrelated channels or revenue streams.
- Historical case studies unless the active task requires them.

Continuity gap:

- Resume state appears to exist, but it is distributed. A single current-state pointer per active production would reduce both context load and lost continuity.

## 8. Background Jobs And Polling

Confirmed mechanisms:

- `pipeline_supervisor.py` is a blocking supervisor for Anomalous Wild; its header says it does not stop until clips are done and should be run with `nohup &` for background behavior (`pipeline_supervisor.py:1-32`).
- It writes `_supervisor_state` files including `pipeline_done.txt`, `supervisor.log`, and `failures.json` (`pipeline_supervisor.py:60-65`).
- It polls Kie.ai task endpoints with increasing intervals until success/failure/timeout (`pipeline_supervisor.py:139-166`).
- `kie_market_api.py` submits tasks, records task IDs into generation logs, polls `recordInfo`, and refuses to overwrite provider outputs (`kie_market_api.py:47-66`, `kie_market_api.py:69-121`, `kie_market_api.py:124-129`).
- Generic utilities include Kie and WaveSpeed polling functions and parallel polling helpers.
- Graphify federation hooks mark domains dirty and rebuild on session stop (`REGISTRY.md:85-89`).

Risk:

- "Background" can mean several different things: a blocking script, a shell process launched with `nohup`, a hook that fires on session stop, or an agent actively waiting.
- If a task is not launched outside the interactive agent session, it likely does not survive the session ending.

Recommendation:

- Define a single "background job contract" for each provider workflow:
  - task id location
  - state file location
  - polling owner
  - whether it survives agent shutdown
  - resume command
  - completion signal

## 9. Duplication And Bloat Analysis

Likely duplicated concepts:

- "Read maps/toolbox/memory first" appears in root instructions, Claude/Gemini files, hardening skill, and memory files.
- "Do not load everything" appears in Claude, Gemini, Core Memory, Memory Index, and the hardening skill.
- "Preserve iterations / never overwrite" appears in root instructions, memory, production skills, and tool guards.
- Video model/provider rules appear in Tool Manager, TOOLBOX, pipeline skills, wrappers, and production logs.
- Tony preference/correction records appear in feedback, global memory, Codex memory, logs, and self-review.

Highest context-cost contributors:

- Full production skills.
- `TOOLBOX.md`, which is useful but broad.
- Recent logs if read wholesale.
- Video production folders with renders, report cards, manifests, data, prompts, and case studies.
- Resource Library and Wiki if loaded as files rather than queried.

Recommendation:

- Keep the duplication only where it serves a different job.
- Collapse durable recurring lessons upward into skills or executable guards.
- Keep logs as searchable evidence.
- Keep global memory compact.

## 10. Recommended Target Architecture

Proposed context layers:

1. Immediate bootstrap: tiny always-read files.
   - `Core_Memory.md`
   - `Memory_Index.md`
   - Agent entry file: `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md`

2. Routing layer: small index files.
   - `Workspace-Map.md`
   - `System-Map.md`
   - `Graphify/REGISTRY.md`
   - `Skill-Index.md`

3. Current task state: one compact state pointer.
   - For each production: `RESUME_NOTES.md` or equivalent.
   - For each active app/game: one active project status file.

4. Procedural layer: open only triggered skills.
   - Pipeline skill.
   - Tool Manager skill when tool/model/provider choice is involved.
   - Ingest skill only for ingest work.

5. Long-form knowledge: query on demand.
   - Graphify domain queries.
   - Wiki pages.
   - Resource Library source docs.
   - Case studies.

6. Historical evidence: query only when needed.
   - Logs.
   - Feedback loop.
   - Self-review.
   - Report cards.

## 11. Context Loading Policy

Continuing an active Anomalous Wild production:

- Load root bootstrap, memory index, Graphify registry, Video Editor `CLAUDE.md`, current production resume/state files, and Anomalous Wild skill.
- Query Video Editor graph for specific questions.
- Do not load unrelated channels or all prior logs.

Researching a YouTube tutorial and turning it into a skill:

- Load root bootstrap, Tool Manager if tools are involved, Video Analyzer skill, ingest/wiki rules, and skill-creator if creating a skill.
- Store source tutorial in Resource Library, distilled lesson in Wiki or skill.

Editing an existing skill:

- Load root bootstrap, Skill Index, exact `SKILL.md`, relevant referenced files only, and recent feedback if the edit responds to Tony's correction.
- Validate skill frontmatter directly.

Debugging a pipeline script:

- Load root bootstrap, TOOLBOX, exact script, tests, current production state, and governing skill.
- Avoid reading full production history unless bug context requires it.

Starting an unrelated coding task:

- Load root bootstrap, Workspace/System maps, relevant app/game/project folder only.
- Do not load video production memory.

Broad strategy question:

- Load `BUSINESS_CONTEXT.md`, `Ecosystem-Map.md`, `Revenue-Streams.md`, and relevant business/department docs.
- Query wiki/Graphify rather than loading every strategy file.

## 12. Risk-Controlled Migration Plan

Do not execute this plan during the audit.

Low risk:

- Add or update concise indexes.
- Add current-state pointers for active projects.
- Clarify in startup docs that recent logs are targeted reads, not bulk loads.
- Add "authority order" to memory docs.

Medium risk:

- Consolidate duplicated instructions across `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, and the hardening skill.
- Split very large skills into small frontdoor skill files plus references.
- Add background-job contracts for provider scripts.

High risk:

- Removing memory systems.
- Changing Graphify federation structure.
- Reworking Claude/Codex/Gemini startup behavior.
- Replacing logs/feedback/self-learning architecture.

Safety sequence:

1. Commit/tag current Agent-OS state.
2. Save this report and Claude's future report.
3. Get second opinion from Claude/Gemini.
4. Create a branch/version for changes.
5. Start with one low-risk domain.
6. Verify retrieval quality and context reduction.
7. Roll back if continuity gets worse.

## 13. Open Questions

- What exact files does Claude Code inject automatically at session start?
- How large is the `claude-mem` injected payload in practice?
- Does Claude Code load full `CLAUDE.md` plus nested `CLAUDE.md` files, and when?
- Which Graphify hooks are currently installed in Claude Code settings versus merely present in the repo?
- Which background scripts survive when Claude Code hits usage limits or the terminal process exits?
- Which active productions already have reliable `RESUME_NOTES.md` files?
- Which lessons in logs/feedback have already been promoted into governing skills or code guards?

## 14. Appendix: Evidence

Files inspected or sampled during this audit/session:

- `/Users/tonymacbook2025/Documents/Agent-OS/AGENTS.md`
- `/Users/tonymacbook2025/Documents/Agent-OS/CLAUDE.md`
- `/Users/tonymacbook2025/Documents/Agent-OS/GEMINI.md`
- `/Users/tonymacbook2025/Documents/Agent-OS/TOOLBOX.md`
- `/Users/tonymacbook2025/Documents/Agent-OS/BUSINESS_CONTEXT.md`
- `/Users/tonymacbook2025/Documents/Agent-OS/DEPARTMENTS.md`
- `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Directory.md`
- `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Ecosystem-Map.md`
- `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Revenue-Streams.md`
- `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Strategic-Roadmap.md`
- `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Memory/Core_Memory.md`
- `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Memory/Memory_Index.md`
- `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Memory/Global_Agent_Memory.md`
- `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Memory/Codex_Memory.md`
- `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Graphify/REGISTRY.md`
- `/Users/tonymacbook2025/Documents/Agent-OS/000_Wiki/index.md`
- `/Users/tonymacbook2025/Documents/Agent-OS/000_Wiki/log.md`
- `/Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/CLAUDE.md`
- `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/codex-agent-os-hardening/SKILL.md`
- `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/graphify/SKILL.md`
- `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/ingest/SKILL.md`
- `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/three-brain/SKILL.md`
- `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/Tool-Manager/SKILL.md`
- `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/SKILL.md`
- `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/Neon_Parcel_Longform_Compilation/SKILL.md`
- `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/Reimagined_Realms_Video_Pipeline/SKILL.md`
- `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/Production-Research-Agent/SKILL.md`
- `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/Production-Asset-Planner/SKILL.md`
- `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/Storyboard-Generation/SKILL.md`
- `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/Video-Analyzer/SKILL.md`
- `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools/kie_market_api.py`
- `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools/utils.py`
- `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/pipeline_supervisor.py`

Methods used:

- Targeted file reads.
- Directory/file listings.
- Search for memory, Graphify, polling, task, and background-job terms.
- Line-numbered evidence extraction for core files.

Assumptions:

- `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` are intended as agent startup manuals.
- Graphify query cost is accepted as documented by the local registry.
- Context-cost estimates are qualitative unless measured by a provider/token tool.
