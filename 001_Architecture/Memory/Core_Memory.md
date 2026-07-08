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

## Hard Rules — All Agents Must Follow These Always

### Validation — Never Declare Work Done Without Proof
- Every build, script, skill, or automation MUST be followed by a verification step before reporting completion.
- Verification options: run the code, call the CLI, check the output file exists and has real content, grep for the key symbol.
- If you cannot verify something (no permission, auth required, needs a live run Tony must trigger), say exactly: "I could not verify [X] because [Y]. You need to manually confirm [Z]." Then stop.
- Never silently skip verification. Never assume it works. Never say "done" when you haven't checked.
- If a verification fails: diagnose before reporting. Do not just flag a failure — explain what broke and propose a fix.

### Data Fetching and Scraping — Report Everything, Not Just Successes
- When fetching data from multiple sources (APIs, scrapers, pricing pages, etc.), every source must be accounted for in the response.
- Format: show what succeeded, then explicitly flag what failed, why it failed, and what Tony needs to do to fix it.
- Never silently omit a failed source. A missing result with no explanation is the same as hiding the failure.
- Example: "Got pricing for kie.ai ✅ and OpenAI ✅. fal.ai ❌ — returned 403, requires authentication. You need to log in and re-run the scraper, or provide a session cookie."
- This applies to: API calls, web scrapes, CLI tool runs, file reads, any operation where partial results are possible.

### Incomplete Work and Dropped Instructions
- Follow every instruction in a request, not just the first one. If a message has 3 parts, all 3 must be addressed.
- If you cannot complete part of a request (blocked, no access, missing dependency), say so explicitly before moving on.
- Do not deliver partial work without clearly labeling which parts are incomplete and why.
- If something was corrected in a prior session and you find yourself doing it again, stop and acknowledge the repeat before proceeding.

### API Keys
- `~/.env-secrets` is the ONE AND ONLY place any API key ever lives. No exceptions.
- Never hardcode a live key in any file — not `.env`, `.json`, `.yaml`, `.toml`, shell scripts, nowhere.
- Config files always use placeholder references like `${KEY_NAME}` — never real values.
- `~/.mcp-secrets.env` does not exist and must never be referenced.

### Destructive Operations
- Never delete, remove, rename, or move any files or folders — not even ones that appear stale or redundant.
- Tony handles all destructive operations himself. A prior agent deletion destroyed the entire workspace and cost months of recovery.
- When something should be removed, report the finding and stop. Do not offer to run `rm`, `mv`, or any destructive command.

### Git / GitHub
- `000_Ingest/` never goes into the GitHub repo. It is a temporary processing queue — files only belong in the repo after being wikified and graphified via the ingest skill.
- Never commit video files, image files, or auto-generated output folders (graphify-out/, Graphify-Out/).
- All API keys must be replaced with `${KEY_NAME}` placeholders before any commit.

### Agent-OS Philosophy
- Agent-OS (`/Users/tonymacbook2025/Documents/Agent-OS/`) is Tony's personal operating system and the single orchestration layer for all AI work — Claude Code, Codex, Gemini CLI, VS Code, Antigravity IDE, and every other agent operates inside this folder.
- All structure, configs, scripts, wiki, and architecture belong in the repo. The only exclusions are `000_Ingest/`, large media files, and secrets.
- When saving any durable memory, always write to `001_Architecture/Memory/Global_Agent_Memory.md` first (universal), then to agent-specific memory if needed.

### SKILL.md Validation — validate_build.py Does Not Parse YAML
- `validate_build.py`'s skill check only string-searches for `'name:'` in frontmatter — it will report PASS on a SKILL.md with genuinely broken YAML.
- If a skill's trigger-matching seems off, verify frontmatter directly: `python3 -c "import yaml; yaml.safe_load(open(path).read().split('---')[1])"`.
- Known past failure mode: a dangling, unquoted second `<example>` block outside the quoted `description:` string breaks parsing and degrades the skill's real trigger description to a bare title fallback in the live skill list. Found and fixed in both Anomalous_Wild_Video_Pipeline and Reimagined_Realms_Video_Pipeline SKILL.md files 2026-07-08 — check any other multi-example SKILL.md for the same pattern before trusting validate_build.py's PASS alone.

### Multi-Task Builds — Always Run a Final Whole-Branch Review
- When executing a multi-task implementation plan (subagent-driven-development or similar), per-task review is necessary but not sufficient — later tasks consume earlier tasks' real output shapes, and two individually-approved tasks can still contradict each other when composed.
- Always run one final whole-branch review across the complete file set, on the most capable available model, even if every individual task passed its own review cleanly.
