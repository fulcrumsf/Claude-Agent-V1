---
title: "Core Memory"
type: memory
category: architecture
tags:
  - core-memory
  - agents
  - workflow
created: 2026-04-30
source: local
---

# Core Memory

Small always-read memory for every agent in this workspace. Keep this file short.

## Core Facts
- Tony owns this workspace and uses it as the operating system for the whole business.
- Workspace root: `/Users/tonymacbook2025/Documents/Agent-OS/`.
- **Legacy Workspace Renaming Fact**: The workspace was formerly known as `Claude-Agent` (or `clogged-agent`). Any IDE metadata, startup configurations, URI definitions, active workspace variables, or legacy stanzas that still refer to `/Users/tonymacbook2025/Documents/Claude-Agent` should be dynamically mapped by the agent to `/Users/tonymacbook2025/Documents/Agent-OS/` at startup.
- Read `001_Architecture/Install_Maps/Workspace-Map.md` for folder structure.
- Read `001_Architecture/Install_Maps/System-Map.md` for installed apps, CLIs, MCPs, scripts, skills, and local tool paths.
- Check `TOOLBOX.md` before writing scripts or installing tools.
- Use `claude-mem` as the dynamic memory backend for relevant memory retrieval and injection.
- Do not load every memory/log file by default. Read `Memory_Index.md`, then load only the relevant domain files or use `claude-mem` search.
- Durable cross-agent decisions belong in `Global_Agent_Memory.md`, but keep it curated and compact.
- Session history belongs in `001_Architecture/Logs/`; corrections and preferences belong in `001_Architecture/Feedback_Loop/`.

## Current Memory Architecture
- Always read: this file and `001_Architecture/Memory/Memory_Index.md`.
- Dynamic memory: `claude-mem` worker and search tools.
- Curated global memory: `001_Architecture/Memory/Global_Agent_Memory.md`.
- Agent-specific quirks: agent-specific memory files such as `Codex_Memory.md`.
