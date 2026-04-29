---
title: Self-Review — 2026-04-29
type: self-review
tags: [self-review]
---

# Self-Review — 2026-04-29

## What Went Well

**Build → verify → fix loop worked.** Ran the script, checked counts immediately, spotted anomalies (1,995 scripts, 1,663 skills, 1 compose file), and fixed before writing the final map. This is the right workflow for data-gathering scripts — always sample the output before committing.

**Clarifying questions up front.** Tony gave detailed, useful answers that shaped every design decision. Skipping those questions would have resulted in a workspace-only map and no Adobe plugins section.

**Correctly declined the remote agent for cron.** The schedule skill loaded and I immediately recognized the mismatch — a remote cloud agent cannot scan a local Mac. Redirected to `crontab` without making the user figure it out.

## What Could Be Improved

**MCP server detection is incomplete.** Docker Desktop manages MCP servers through its UI, not a file I could read. The final map only shows `docker-mcp (catalog)` and `container:cloudflared`. The real MCP tools (obsidian, wikidata, cloudflare, Google Drive) aren't documented in the map. A future improvement: add a static `known_mcps` list in the script seeded from TOOLBOX.md, or prompt Tony to update TOOLBOX.md with the full MCP list after each Docker Desktop change.

**Compose file filter was too aggressive on first pass.** The initial skip patterns removed `backups` and `docker_config` from compose file scan — those dirs contain real compose files. Should have used separate skip lists for Python scripts vs. compose files from the start. Fixed it, but it took an extra iteration.

**Should have checked Docker MCP gateway subcommands before coding the scanner.** Assumed `docker mcp gateway list` existed. It doesn't — the only subcommand is `run`. Always check `--help` before scripting against a CLI.

## Patterns to Remember

- Large glob scans (`**/*.py`) need immediate distribution analysis before use
- Local vs. remote execution is the first question for any scheduled/automated task
- Docker Desktop's MCP configuration is not file-accessible — it lives in the GUI
- Plugin directories contain many .md files that aren't skills; only scan `skills/` subdirs
