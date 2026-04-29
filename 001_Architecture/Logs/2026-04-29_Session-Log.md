---
title: Session Log — 2026-04-29
type: session-log
tags: [session-log, system-map, install-map]
---

# Session Log — 2026-04-29

## Summary
Created a comprehensive System Map of all tools, apps, and assets on Tony's Mac. Companion to the existing Workspace-Map.md.

## Actions Taken

- **Created** `001_Architecture/Scripts/generate_system_map.py` — Python scanner (stdlib only) that discovers and documents all system assets
- **Ran** the script; generated `System-Map.md` + `system_map_data.json` in `001_Architecture/Install_Maps/`
- **Scheduled** local crontab: `0 3 * * 0` (Sundays 3 AM) — runs the script automatically, logs to `system_map_update.log`
- **Updated** `TOOLBOX.md` — added System Maps section at the top with both map files documented
- **Created** `~/.claude/projects/.../memory/reference_system_map.md` — persistent pointer so Claude never asks where the map is
- **Updated** `MEMORY.md` — added entry: "look at the system map" → read Install_Maps/System-Map.md

## What the System Map Captures (current snapshot)
| Category | Count |
|----------|-------|
| Installed apps | 582 |
| Homebrew formulae | 144 |
| Homebrew casks | 6 |
| Docker containers | 16 |
| Docker images | 21 |
| Docker compose files | 6 |
| CLIs with versions | 26 |
| Python scripts (authored) | 268 |
| Claude Code skills | 17 |
| Python installs | 4 |
| VENVs | 2 |
| Adobe plugin groups | 2 |

## Key Decisions
- Excluded Google Drive Backup, ComfyUI library trees, docker data volumes from Python script scan to avoid picking up 1,900+ library files
- Used local crontab (not remote scheduled agent) — the script needs local filesystem access; remote cloud agents cannot reach the Mac
- Docker MCP gateway (`MCP_DOCKER`) proxies all MCP tools; individual servers (obsidian, wikidata, cloudflare, Google Drive) are configured via Docker Desktop UI, not a discoverable file

## Files Touched
- `001_Architecture/Scripts/generate_system_map.py` — created
- `001_Architecture/Install_Maps/System-Map.md` — created
- `001_Architecture/Install_Maps/system_map_data.json` — created
- `TOOLBOX.md` — updated (added System Maps section)
- `~/.claude/.../memory/reference_system_map.md` — created
- `~/.claude/.../memory/MEMORY.md` — updated

## Pending / Notes
- MCP server list will be more complete once Tony connects MCP servers via Docker Desktop UI and we re-run the scanner
- Script can be extended to scan Figma plugins (cloud-based, would need Figma API)
