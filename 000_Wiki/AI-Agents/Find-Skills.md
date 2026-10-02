---
title: "Find Skills"
type: wiki
category: ai-agents
tags:
  - agent-skills
  - skills-cli
  - skill-discovery
  - vercel-labs
source: "[[007_Resource_Library/Tools/Find-Skills-Vercel-Labs-Agent-Skill]]"
created: 2026-10-01
---

# Find Skills

## What It Is
Find Skills (`vercel-labs/skills@find-skills`) is a small meta-skill from Vercel Labs. It teaches an agent to notice when a request might already be covered by a published skill, search the open skills ecosystem indexed at skills.sh, and offer to install the match. It doesn't contain any skills itself. It wraps the Skills CLI (`npx skills`), which is the package manager for SKILL.md-format skills across Claude Code, Codex, Gemini CLI, Cursor, Antigravity and dozens of other agents. The source repo has about 32K GitHub stars and an MIT license.

## Key Concepts
- **Two commands do the work.** `npx skills find <query>` searches by keyword (optionally `--owner <org>`), and `npx skills add <owner/repo@skill>` installs. `npx skills update` refreshes installed skills.
- **Leaderboard first.** The skill tells the agent to check the skills.sh install leaderboard before running a search, because heavily installed skills from known sources (`vercel-labs`, `anthropics`, `microsoft`) are the safer bet.
- **Quality bar before recommending.** Prefer 1K+ installs, be wary under 100, and treat source repos under 100 stars with skepticism. Popularity isn't a security review.
- **Present, then offer.** The agent shows the skill name, install count, source and install command, and installs only if the user agrees (`-g` for global, `-y` to skip prompts).
- **Fallback.** If nothing fits, the agent says so, does the task directly, and can suggest `npx skills init` to start a custom skill.

## How Tony Uses This
Installed 2026-10-01 into `001_Architecture/Skills/find-skills/` (Claude Code, Codex and Gemini CLI through their symlinks) and mirrored to `.agents/skills/find-skills/` for Antigravity. It's the discovery half of Agent-OS skill management. The other half is the safety gate: every candidate it finds gets scanned with `/skillspector` (NVIDIA SkillSpector, also installed 2026-10-01) before it is installed.

Two workspace-specific caveats:
- Don't run the skill's own install command (`npx skills add <pkg> -g -y`) as written. In this workspace's symlinked layout it writes the files to `~/.agents/skills/` and leaves a broken symlink in `001_Architecture/Skills/`. Follow `001_Architecture/Skills/Skill_Install_Rules.md` instead.
- SkillSpector flags the unpinned `npx skills` calls (rule RP1, MEDIUM): each run fetches whatever version of the CLI is latest on npm. Pin it (`npx -y skills@1.7.0 ...`) when running it for real.

## Related
- [[007_Resource_Library/Tools/Find-Skills-Vercel-Labs-Agent-Skill]]
- [[007_Resource_Library/Tools/Skills-Sh-Agent-Ecosystem]]
- [[Claude-Code-And-Karpathys-System-10000-Skills]]
- [[Humanizer]]
