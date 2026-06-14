---
title: "Codex Cross-Session Memory"
type: memory
category: architecture
tags:
  - codex
  - memory
  - workflow
created: 2026-04-30
source: local
---

# Codex Cross-Session Memory

Codex-specific notes for OpenAI Codex agents. Shared cross-agent memory now lives in `001_Architecture/Memory/Global_Agent_Memory.md`.

Use this file only for Codex-specific quirks. Put durable business-wide preferences, project decisions, recurring corrections, important tool paths, and workflow rules in the global memory file so Claude Code and other agents can use them too.

## Memory Entries

### 2026-04-30 — Global Memory File Created

Tony wants memory to act globally across agents because this workspace is the whole business operating system. Use `Global_Agent_Memory.md` first for shared memories, and keep this file for Codex-only operational notes.
