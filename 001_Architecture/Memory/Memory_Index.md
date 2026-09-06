---
title: "Memory Index"
type: memory-index
category: architecture
tags:
  - memory-index
  - agents
  - workflow
created: 2026-04-30
source: local
---

# Memory Index

Use this as the routing layer. Do not load every memory file unless Tony explicitly asks for a full memory audit.

## Always Read
- `001_Architecture/Memory/Core_Memory.md` — tiny bootstrap memory
- `001_Architecture/Memory/Memory_Index.md` — this routing file

## Dynamic Retrieval
- `claude-mem` — relevant-memory injection and search across sessions
- Worker status: `npx claude-mem status`
- Start worker: `npx claude-mem start`
- Viewer: `http://localhost:37701`
- Claude Code search command: `/mem-search`

## Curated Shared Memory
- `001_Architecture/Memory/Global_Agent_Memory.md` — stable cross-agent memories only
- `001_Architecture/Memory/ChatGPT_Profile/` — distilled second-brain profile notes from Tony's ChatGPT export
- `001_Architecture/Feedback_Loop/` — corrections, preferences, and validated approaches
- `001_Architecture/Logs/` — session summaries and changed files
- `001_Architecture/Self_Learning_Loop/` — periodic patterns and retrospectives

## Agent-Specific Memory
- `001_Architecture/Memory/Codex_Memory.md` — Codex-specific quirks only
- Claude Code also has `~/.claude/projects/-Users-tonymacbook2025-Documents-Agent-OS/memory/MEMORY.md`
- Gemini CLI uses `~/.gemini/GEMINI.md` for claude-mem context injection

## Task Routing
- Broad Agent-OS orientation: read root manuals first, then prioritize numbered departments in this order: `001_Architecture`, `002_Content-Creation`, `007_Resource_Library`. Usually skip `000_Ingest` unless the task is about ingest.
- Installed tools, CLIs, local apps, MCPs, scripts: read `System-Map.md`, `TOOLBOX.md`, then search `claude-mem`.
- Workspace structure, departments, where files live: read `Workspace-Map.md`, then search `claude-mem`.
- Ingest, wiki, Graphify: read `AGENTS.md` ingest procedure, `000_Wiki/log.md`, and relevant feedback/log entries.
- Video production: search `000_Wiki/Video-Production/`, `002_Content-Creation/Video_Editor/`, and `claude-mem`.
- App development: search relevant folder under `003_Apps/` and `claude-mem`.
- E-commerce: search relevant folder under `005_Ecommerce/` and `claude-mem`.
- Agent behavior or recurring corrections: read latest `Feedback_Loop/` entries and search `claude-mem`.
