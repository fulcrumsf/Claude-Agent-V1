---
title: "Skill Install Rules"
type: doc
category: architecture
tags:
  - agents
  - skills
created: 2026-10-01
source: local
---

# Skill Install Rules

How to install a third-party skill in Agent-OS so every harness sees it. Written 2026-10-01 while installing `find-skills`, `humanizer` and `skillspector`.

## Where skills live

- **Canonical folder:** `001_Architecture/Skills/<skill-name>/` (a real folder, lowercase-kebab-case name). `~/.claude/skills`, `~/.codex/skills` and `~/.gemini/skills` are all symlinks to this folder, so one install covers Claude Code, Codex and Gemini CLI.
- **Antigravity mirror:** Antigravity IDE only reads `.agents/skills/` at the workspace root. That folder is real, not a symlink, because symlinks into Antigravity's sandbox don't resolve reliably. Every skill installed into the canonical folder must also be **copied** (not symlinked) to `.agents/skills/<skill-name>/`. When a skill is updated, copy it again so the two stay identical (`diff -r` should print nothing).

## Install procedure

1. Get the skill's files into the scratchpad: `git clone --depth 1` the repo, or download the folder.
2. Scan the folder you are about to install (not the whole clone, since `.git/` hooks and CI files inflate the score):
   `skillspector scan <folder> --no-llm` (or use the `/skillspector` skill for the full static plus semantic review).
3. Read every HIGH or CRITICAL finding in context. Stop and ask Tony if any is real.
4. Copy the exact scanned files into `001_Architecture/Skills/<skill-name>/`.
5. Copy the same files into `.agents/skills/<skill-name>/`.
6. Run `python3 001_Architecture/Scripts/sync_skill_index.py` to refresh `Skill-Index.md`.
7. Add the skill to `TOOLBOX.md` (workspace root).

## Don't use bare `skills add -g` here

Checked 2026-10-01 against Vercel's skills CLI v1.7.0 in a sandboxed HOME that copies this workspace's symlink layout:

- `npx skills add <pkg> -g -y` with no `--agent` writes the real files to `~/.agents/skills/<name>/` (outside the repo) and puts a relative symlink in `~/.claude/skills/`. Because `~/.claude/skills` is itself a symlink, the relative path resolves from the wrong folder and the link is **broken**. 16 links already in `001_Architecture/Skills/` (the `firecrawl-*` family, `cloudflare`, and several design skills) are broken this way, which is why those skills don't load.
- `npx -y skills@1.7.0 add <pkg> -g -y --agent claude-code` copies a real folder into `001_Architecture/Skills/<name>/` and records it in `~/.agents/.skill-lock.json`. Use this form when you want the CLI's update tracking, and still do steps 2, 3, 5, 6 and 7 above.
- The CLI sends install telemetry unless `DISABLE_TELEMETRY=1` is set.
