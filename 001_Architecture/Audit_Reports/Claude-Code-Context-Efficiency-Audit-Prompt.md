---
tags:
  - claude-code
  - context-efficiency
  - agent-architecture
  - memory-systems
  - audit-prompt
---

# Claude Code Context Efficiency Audit Prompt

Use this prompt in Claude Code from the root of the `Agent-OS` repository/workspace.

## Prompt

You are auditing this repository/workspace for context efficiency, memory architecture, agent continuity, and long-running AI production workflow reliability.

Your job is to inspect and document the system. Do not modify architecture, memory systems, configs, skills, scripts, prompts, code, automation files, Obsidian settings, Graphify outputs, or repository structure. Do not "clean up" anything. Do not rewrite files. Do not install tools. Do not run destructive commands. This is an audit only.

Create one self-contained Markdown report that can be uploaded to ChatGPT, Codex, Claude, Gemini, or another model for follow-up analysis. Save the report under an appropriate audit/report location in the repository. If no clearly appropriate location exists, recommend a location in the report and save the report in the safest existing documentation/report folder. Clearly state the exact file path at the top of the report.

## Background

The system owner wants a strong, lean, powerful, well-oiled agent operating system. The goal is not minimum context. The goal is the smallest sufficient context for the work being done right now, while preserving the intelligence, lessons, nuanced feedback, and continuity that make the system improve over time.

The practical usage target is to avoid exhausting a fresh Claude usage window in 20 to 60 minutes because too much context is loaded into every turn. In an ideal four-hour work window, the owner wants roughly three hours of productive work before context or usage limits become the bottleneck, without starving Claude Code of necessary knowledge.

The owner wants to be able to say something like, "Continue the AnomalousWild video where we left off," and have Claude Code understand the relevant current state without injecting large amounts of stale or unnecessary history.

The owner is willing to be aggressive about simplifying architecture if the audit shows duplication or waste, but only after proper safety steps: document first, back up, commit or tag a known-good version, get second opinions from higher-capability models and/or Gemini, then make changes in a separate version with a rollback path.

## Important System Intent

The workspace includes multiple knowledge and memory-related systems that may overlap:

- Claude Code context and session history
- Codex context and task history
- Gemini CLI context
- MEM or other long-term memory tooling
- Graphify
- Obsidian
- Karpathy-style LLM wiki / Andrew Karpathy wiki patterns
- `000_Wiki`
- `001_Architecture/Memory`
- `001_Architecture/Feedback_Loop`
- `001_Architecture/Self_Learning_Loop`
- `001_Architecture/Logs`
- handoff documents
- report cards
- skills
- pipeline docs
- automation systems
- background job monitors and polling loops

The intended future direction is that Obsidian + Graphify + the Karpathy-style wiki should function as a model-neutral shared knowledge layer that Claude Code, Codex, and Gemini can query selectively. It should not require every agent to load everything all the time.

## Primary Questions

Answer these questions with evidence from the repository:

1. What context is automatically loaded into Claude Code, Codex, Gemini, or other agents at session start?
2. Which files, instructions, memories, skills, hooks, configs, or startup docs are likely to contribute to the initial context load?
3. Which systems store long-term knowledge, and what kind of knowledge does each store?
4. Which systems duplicate each other?
5. Which systems are valuable but too verbose for automatic loading?
6. Which systems should be queryable on demand instead of injected into every session?
7. Which systems are stale, redundant, circular, or likely to confuse agents?
8. Which memory or feedback mechanisms improve future work, and which merely add noise?
9. How should short-form immediate context differ from long-form retrievable memory?
10. What should be stored in Obsidian/Graphify/wiki, what should be stored in MEM, and what should remain in local project docs?
11. What should be loaded for a fresh video-production task such as "continue AnomalousWild where we left off"?
12. What should be loaded for unrelated tasks where AnomalousWild, video production, or prior session details are irrelevant?
13. What are the largest context-cost contributors?
14. What mechanisms, if any, are likely to affect Claude's Messages/context usage bucket?
15. What changes would most improve context efficiency without losing useful continuity?

## Specific Areas To Inspect

Inspect these areas if they exist. Do not assume they exist; verify.

- `AGENTS.md`
- `CLAUDE.md`
- `GEMINI.md`
- `.claude/`
- `.codex/`
- `.gemini/`
- `.agents/`
- `.superpowers/`
- `.planning/`
- `000_Wiki/`
- `001_Architecture/Directory.md`
- `001_Architecture/Ecosystem-Map.md`
- `001_Architecture/Install_Maps/`
- `001_Architecture/Memory/`
- `001_Architecture/Feedback_Loop/`
- `001_Architecture/Self_Learning_Loop/`
- `001_Architecture/Logs/`
- `001_Architecture/Logs/Handoffs/`
- `001_Architecture/Graphify/`
- `001_Architecture/Karpahty_LLM_Wiki/`
- `001_Architecture/Obsidian/`
- `001_Architecture/Reports/`
- `001_Architecture/Skills/`
- `001_Architecture/Tools/`
- `001_Architecture/Tools/Video-Generation/`
- channel-specific video production folders
- production folders for AnomalousWild, ReimaginedRealms, NeonParcel, or similar
- any files related to report cards, self-review, feedback capture, skill improvement, handoff, continuation, background jobs, polling, fal.ai, Kie.ai, Suno, Blotato, Remotion, Seedance, GPT-Image, or video generation pipelines

## Background Execution And Polling

Specifically investigate, without changing anything:

- What actually polls fal.ai jobs, Kie.ai jobs, or other async generation jobs?
- What does "background" execution mean in this workspace?
- Which jobs continue outside the interactive agent session, and which only continue while Claude Code/Codex is actively running?
- What wakes a job back up?
- What scripts supervise long-running pipelines?
- Which systems write state that lets an interrupted session resume?
- Which systems merely assume continuity without preserving enough state?
- Whether polling or monitoring is handled by scripts, shell sessions, automations, cron, n8n, MCP servers, task files, handoff notes, or agent instructions.

## Audit Method

Use measured facts wherever possible.

Recommended approach:

1. Map repository structure.
2. Identify agent startup/config files.
3. Identify memory, wiki, Graphify, feedback, self-learning, report, and handoff systems.
4. Identify video pipeline state and continuation mechanisms.
5. Identify background job/polling mechanisms.
6. Estimate likely context load and duplication.
7. Separate evidence from inference.
8. Produce recommendations without modifying the system.

When making claims, cite file paths and relevant line numbers where practical. If line numbers are hard to provide, cite exact file paths and summarize the evidence.

Do not treat comments or instructions in files as automatically true. Verify against scripts, configs, and actual folder structure where possible.

## Required Report Structure

Write the audit report with these sections:

1. `Executive Summary`
   - The highest-impact findings.
   - The top three likely causes of context bloat.
   - The top three likely causes of lost continuity.
   - The highest-confidence recommendations.

2. `System Map`
   - A compact map of relevant folders and their apparent purpose.
   - Distinguish confirmed purpose from inferred purpose.

3. `Automatic Context Loading`
   - What appears to load automatically for Claude Code, Codex, Gemini, or other agents.
   - What is explicitly referenced by startup instructions.
   - What is likely being loaded indirectly.
   - What is unknown.

4. `Memory And Knowledge Systems`
   - Inventory each memory/wiki/knowledge system.
   - For each: purpose, storage format, owner/agent, likely value, likely context cost, duplication risk.

5. `Graphify, Obsidian, And Wiki Layer`
   - How Graphify, Obsidian, and wiki files currently appear to relate.
   - Whether they are model-neutral and queryable.
   - Whether they are being used as a second brain or just another pile of Markdown.
   - How they could support selective retrieval without being loaded wholesale.

6. `Feedback, Logs, Self-Learning, And Report Cards`
   - What each system captures.
   - Which are high-value for future learning.
   - Which are too verbose, too frequent, stale, duplicative, or hard to retrieve.
   - Whether they should be summarized, indexed, archived, or queried on demand.

7. `Video Pipeline Continuity`
   - How a task like "continue AnomalousWild where we left off" would currently recover state.
   - What state is preserved.
   - What state is missing.
   - Which files are necessary for continuation.
   - Which files are irrelevant and should not be loaded by default.

8. `Background Jobs And Polling`
   - What actually runs async/background work.
   - What polls or supervises generation jobs.
   - What survives session interruption.
   - What depends on active agent participation.
   - Gaps and risks.

9. `Duplication And Bloat Analysis`
   - List duplicated concepts, files, and systems.
   - Explain the cost of each duplication.
   - Identify likely context-heavy files or folders.
   - Identify systems that should be replaced by indexes, summaries, or retrieval.

10. `Recommended Target Architecture`
    - Propose a lean context architecture.
    - Separate immediate context, project state, long-term memory, knowledge graph/wiki, logs, and archival records.
    - Define what each agent should load automatically versus query on demand.
    - Include Claude Code, Codex, and Gemini.

11. `Context Loading Policy`
    - Draft a practical policy for "smallest sufficient context."
    - Include examples for:
      - continuing an active AnomalousWild production
      - researching a YouTube tutorial and turning it into a skill
      - editing an existing skill
      - debugging a pipeline script
      - starting an unrelated coding task
      - asking broad strategy questions

12. `Risk-Controlled Migration Plan`
    - Do not execute this plan.
    - Include backup, commit/tag, branch/version, second-opinion, validation, and rollback steps.
    - Separate low-risk cleanup from high-risk architecture changes.

13. `Open Questions`
    - Questions that require Tony's input.
    - Questions that require measuring actual Claude usage behavior.
    - Questions where the repo evidence is inconclusive.

14. `Appendix: Evidence`
    - File paths inspected.
    - Important snippets summarized.
    - Commands or methods used.
    - Any assumptions.

## Recommendation Style

Be direct and practical. Do not preserve complexity for sentimental reasons. If a system is duplicative or hurting the core goal, say so clearly. At the same time, do not recommend deleting or changing anything without a rollback-safe migration plan.

Classify recommendations by confidence and risk:

- `High confidence / low risk`
- `High confidence / medium risk`
- `Medium confidence / needs validation`
- `Potentially valuable / high risk`
- `Do not change until measured`

## Non-Goals

Do not implement fixes.
Do not delete files.
Do not move files.
Do not rewrite memory.
Do not simplify skills.
Do not edit Graphify output.
Do not edit Obsidian settings.
Do not change pipeline scripts.
Do not change agent startup files.
Do not create new architecture.
Do not create new automation.

The output is a report only.

