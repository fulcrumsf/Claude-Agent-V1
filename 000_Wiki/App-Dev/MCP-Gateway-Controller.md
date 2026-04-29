---
title: "MCP Gateway Controller (Summary)"
type: spec
domain: app-dev
tags: [spec, app-dev, automation, ai-agents]
---

# MCP Gateway Controller — Summary

Source: [[../../003_Apps/MCP_Gateway_Controller/DESIGN.md]]

A local unified system for managing all MCP servers, plugins, and skills across Anti-Gravity, Claude Code, VS Code, and similar IDEs. Replaces scattered per-IDE config with a single gateway, web dashboard, and centralized secrets file.

**Components:**
- **Gateway server** (Node + Express, port 3003) — routes all MCP requests through one endpoint, loads `~/.mcp-gateway/config.json` and `~/.env-secrets.env`, persists on/off state in `state.json`.
- **Dashboard** (React + Tailwind + shadcn/ui) — three tabs (MCPs, Plugins, Skills) with real-time toggles and group-based collapse/expand.
- **Config files** — master config, secrets file (single source of truth), and persistent state.

**Initial MCPs in scope:** blotato, stitch, remotion, n8n-mcp, elevenlabs, notion, perplexity, context7, playwright (lower priority — CLI preferred), and docker (kept separate as fallback). MCPs are organized by group (Publishing / Design / Video / Automation / Audio / Data / Research / Documentation / Browser / System) so users can toggle entire categories at once.

Goal: stop hand-editing per-app MCP configs every time a new tool is added.
