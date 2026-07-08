# Session Log — 2026-06-14

## Summary
Git sync session + memory architecture hardening across all agents.

## What Happened

### Investigated Claude-agent Folder
- Found `/Users/tonymacbook2025/Documents/Claude-agent/` containing only `AGENTS.md`
- Identified as a leftover from the June 6 workspace rename (Claude-Agent → Agent-OS)
- The `AGENTS.md` was a claude-mem context dump written at the moment of rename
- Tony will delete it himself — no agent action taken

### Git Repository Sync (May 5 → Jun 14)
- Last commit was May 5, 2026 — over 5 weeks of changes pending
- Discovered and resolved several issues before committing:
  - 4 nested git repos (excalidraw, hyperframes, video-use) — stripped inner `.git` folders, now plain folders in repo
  - `graphify-out/` (18MB) — untracked from git, added to .gitignore (auto-generated, rebuilds on demand)
  - `001_Architecture/Graphify/Graphify-Out/` — was never tracked, added to .gitignore explicitly
  - `000_Ingest/` ghost deletions — committed correctly (removes from GitHub, local untouched)
  - `007_Resource_Library/OpenAI_History/Already Ingested/` — 4GB+ of raw ChatGPT export data excluded
  - `001_Architecture/MCP/gemini_mcp_config.json` — hardcoded GCP API key found and replaced with `${GOOG_API_KEY}`
- Final commit: 8,067 files — pushed to `fulcrumsf/Claude-Agent-V1`
- API key security scan run across all scripts/configs — clean after fix

### Memory Architecture Hardening
- Confirmed all agents read Core_Memory.md at startup:
  - Claude Code (Desktop + CLI): CLAUDE.md ✅
  - Codex: AGENTS.md ✅
  - Gemini CLI: GEMINI.md ✅
  - Antigravity IDE (Claude ext): CLAUDE.md ✅
  - Antigravity IDE (built-in Gemini): auto-loads Core_Memory.md, AGENTS.md, GEMINI.md, claude-mem ✅
- Added Hard Rules section to `Core_Memory.md` covering: API keys, destructive operations, git rules, Agent-OS philosophy
- Strengthened API key rule in `Global_Agent_Memory.md` — now explicit for all agents
- Clarified: `~/.env-secrets` is the ONE source of truth for all keys; `~/.mcp-secrets.env` does not exist

## Files Changed
- `/Users/tonymacbook2025/Documents/Agent-OS/.gitignore` — added graphify-out paths and ChatGPT export exclusion
- `001_Architecture/MCP/gemini_mcp_config.json` — replaced live GCP key with placeholder
- `001_Architecture/Memory/Core_Memory.md` — added Hard Rules section
- `001_Architecture/Memory/Global_Agent_Memory.md` — strengthened API key rule
- `TOOLBOX.md` — added skills-lock.json location to Vercel section
- `001_Architecture/Skills/skills-lock.json` — moved here from Documents/ by Tony

## Decisions Made
- graphify-out/ excluded from repo — rebuilds automatically, not needed for restore
- 000_Ingest/ confirmed: processing queue only, never in git
- Agent-OS is the full OS — all structure/config/scripts go in repo, only large media and 000_Ingest excluded
- Universal memory write rule: always write durable memories to Global_Agent_Memory.md first
- Hard rules now live in Core_Memory.md so every agent reads them every session

## Pending
- Rotate the GCP key that was briefly in git history (private repo, low urgency — Tony will do with next key rotation)
