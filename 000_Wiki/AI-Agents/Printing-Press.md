---
title: "Printing Press"
type: wiki
category: ai-agents
tags:
  - ai-agents
  - cli
  - mcp
  - automation
  - sqlite
created: 2026-05-12
source: 007_Resource_Library/Tools/CLI-Printing-Press.md
---

# Printing Press

## What It Is
The Printing Press is a system for turning APIs and websites into agent-friendly CLIs, Claude Code skills, and MCP servers. It packages the "best" interface around a tool so agents can use it with less token waste, fewer docs lookups, and more compound commands.

## Key Concepts
- Local SQLite mirrors for fast compound queries
- Agent-native flags and muscle-memory workflows
- One build can output a CLI, a skill, and an MCP server
- The companion library catalogs already-printed CLIs that are ready to install
- It is designed around the idea that the best tool for an agent is often a purpose-built CLI

## How Tony Uses This
Use this when Tony wants to expose an external service to agents in a way that is faster than raw HTTP and more reliable than ad hoc prompting. It is also useful as a reference pattern for building internal operator tools.

## Related
- [[MCP-Gateway-Controller]]
- [[Get-Started-With-Codex]]
- [[Graphify]]
- [[007_Resource_Library/Tools/CLI-Printing-Press.md]]
- [[007_Resource_Library/Tools/Printing-Press-Library.md]]

