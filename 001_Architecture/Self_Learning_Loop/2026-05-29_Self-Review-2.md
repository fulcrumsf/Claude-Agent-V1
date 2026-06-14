# Self-Review — 2026-05-29 (Session 2)

## What Went Well
- **Audit was thorough** — checked all 6 runtimes systematically rather than spot-checking
- **Found the dead symlink immediately** — the antigravity main app skills pointed to Claude-Agent which no longer exists. Would have silently broken any agent run in that context.
- **Identified the MCP canonical source** — `001_Architecture/MCP/gemini_mcp_config.json` is symlinked rather than the config living directly in `~/.gemini/`. Good architecture that I almost missed by editing the symlink path directly.
- **Didn't overclaim on plugins** — correctly explained that plugins are runtime-specific by design, not a gap to fix.

## What to Improve
- **PATH awareness in IDE context** — the first `which` check gave false negatives because the IDE PATH differs from terminal PATH. Should always verify with manual path checks when inside an IDE session before reporting CLIs as missing.
- **Versioned paths are fragile** — the claude-mem MCP entry uses a hardcoded version path. Should have flagged this more prominently and noted it needs a maintenance rule.

## Rules to Carry Forward
- After any Antigravity/app upgrade, always re-audit skills symlinks across ALL runtime config dirs
- When editing MCP configs, always check if the file is a symlink first (`realpath`) to find the canonical source
- IDE PATH ≠ terminal PATH — use manual directory checks, not `which`, when validating CLIs from inside an IDE
