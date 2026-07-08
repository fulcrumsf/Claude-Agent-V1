---
title: "Agent-OS Validation System"
type: wiki
category: architecture
tags:
  - validation
  - hooks
  - claude-code
  - checks-and-balances
  - automation
source: built 2026-06-19
created: 2026-06-19
---

# Agent-OS Validation System

## What It Is

A three-component system built into Claude Code that prevents agents from declaring work done without verifying it actually works. Addresses the core problem of silently incomplete builds and dropped data-fetch failures.

## Key Concepts

- **Functional artifact** — any file that is supposed to DO something when invoked: Python scripts, shell scripts, SKILL.md files, tool configs, settings.json. Not logs, memory files, or markdown documents.
- **Build manifest** — `/tmp/agent_os_build_manifest.json`. Tracks `unverified` and `verified` lists per session. Auto-created on first write, session-scoped.
- **Hard block** — Stop hook exits with code 2, which physically prevents Claude from finishing its turn until the manifest is clear.

## Components

### 1. Build Tracker Hook
**File:** `~/.claude/hooks/agent-os-build-tracker.js`
**Type:** PostToolUse (fires after Write/Edit/MultiEdit)
**What it does:**
- Detects writes to functional artifacts by file extension and path pattern
- Injects `⚠️ VERIFY REQUIRED` warning into Claude's context window immediately
- Appends the file path to the build manifest under `unverified`

**Triggers on:** `.py`, `.sh`, `.js`, `SKILL.md`, tool configs, `settings.json`, `pricing_cache.json`
**Ignores:** Feedback loop entries, session logs, memory files, planning docs, beat tables, shot lists

### 2. Stop Validator Hook
**File:** `~/.claude/hooks/agent-os-stop-validator.js`
**Type:** Stop (fires when Claude finishes a turn)
**What it does:**
- Reads the build manifest
- If `unverified` list is non-empty: outputs the list of unverified files, exits with code 2 (blocks stop)
- If empty: exits 0, Claude stops normally

### 3. Validation Script
**File:** `001_Architecture/Scripts/validate_build.py`
**Usage:**
```bash
# Validate files
python3 001_Architecture/Scripts/validate_build.py --files "path1.py,path2/SKILL.md"

# Validate data fetch completeness
python3 001_Architecture/Scripts/validate_build.py --data-fetch --sources "kie.ai,fal.ai,openai" --got "kie.ai,openai"
```

**Type-aware checks:**
| File Type | Checks |
|---|---|
| `.py` | Syntax (`py_compile`), CLI `--help` smoke test, referenced path existence |
| `SKILL.md` | Frontmatter present, `name:` field exists, name registered in Skill-Index.md |
| `.json` | Valid JSON parse |
| `.sh` | Executable bit set, bash syntax valid |
| `.js` | Exists and non-empty |

When a file passes, it moves from `unverified` → `verified` in the manifest. When manifest is empty, the Stop hook unblocks.

## Data Fetch Validation Rule

Separate from file validation. When fetching data from multiple sources (APIs, scrapers, pricing pages):

1. List all expected sources before starting
2. After fetching, report ALL results — not just successes
3. For each failure: source name + error + what Tony needs to do to fix it
4. Never present partial results as a complete result

**CLI usage:**
```bash
python3 001_Architecture/Scripts/validate_build.py \
  --data-fetch \
  --sources "kie.ai,fal.ai,openai,perplexity" \
  --got "kie.ai,openai,perplexity"
# Output: fal.ai ❌ MISSING — report to Tony with error details
```

## Hook Configuration

Wired in `~/.claude/settings.json`:
```json
"hooks": {
  "PostToolUse": [
    { "matcher": "Write|Edit|MultiEdit", "hooks": [
      { "name": "skill-index-sync", ... },
      { "name": "agent-os-build-tracker", "command": "node ~/.claude/hooks/agent-os-build-tracker.js" }
    ]},
  ],
  "Stop": [
    { "matcher": "", "hooks": [
      { "name": "agent-os-stop-validator", "command": "node ~/.claude/hooks/agent-os-stop-validator.js" }
    ]}
  ]
}
```

## How Tony Uses This

Nothing changes in Tony's workflow. The system runs invisibly. If Claude tries to say "done" without verifying, the Stop hook blocks it and forces verification first. Tony only sees the output if something failed — in which case Claude reports what broke, why, and what needs to happen.

## Related
- [[Tool-Manager]] — uses validate_build.py for pricing cache checks
- [[Reimagined_Realms_Video_Pipeline]] — first skill validated under this system
- `001_Architecture/Feedback_Loop/2026-06-19_Feedback.md` — corrections that motivated this build
