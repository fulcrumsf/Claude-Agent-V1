---
title: "Find Skills (Vercel Labs Agent Skill)"
type: tool-doc
category: ai-agents
form: github-repo
summary: "Vercel Labs' find-skills meta-skill: teaches an agent to search the open skills ecosystem (skills.sh) with `npx skills find` and install a skill with `npx skills add` mid-task. Catalog page clipped from agenticskills.io, including the full SKILL.md. Installed in Agent-OS on 2026-10-01."
url: https://github.com/vercel-labs/skills/tree/main/skills/find-skills
tags:
  - GitHub
  - Coding-Agent
created: 2026-10-01
source: https://agenticskills.io
---

Index live · v1.7.0 · SEP 26 2026

**193+** skills indexed **193** MCP servers **9** platforms tracked

\[ ⌘K \] search

Vercel Labs' meta-skill for skill discovery: it teaches the agent to reach for the Skills CLI (\`npx skills\`) on its own when you ask for something it can't already do. \`npx skills find\` searches the open agent skills ecosystem indexed at skills.sh by keyword, and \`npx skills add\` installs a skill from GitHub in one command — so the agent can extend itself mid-task instead of stopping while you go browse a directory. It is a package manager client for agent capabilities, not a catalogue of its own.

Claude CodeCodexCursorGemini CliMulti Platform

32.1Kstars

Updated 3 months ago

3contributors

## Install This Skill

```
npx skills add vercel-labs/skills@find-skills
```

Get new skills in your inbox. What we added, what we rejected, and why. [See a past issue](https://agenticskills.io/newsletter).

## When to use this skill

- →You want the agent to find and install a skill mid-task, instead of stopping to go browse a directory yourself
- →Setting up a new machine or repo and letting the agent pull the skills it needs on its own
- →You suspect a skill exists for a task but don't know what it's called — \`npx skills find\` searches by keyword
- →You want one-command installs rather than copying a SKILL.md into the right folder by hand
- →Keeping an existing set current — the CLI ships \`check\` and \`update\` for everything installed

## When not to use

- ✕You already know which skill you want — the install command on its own catalog page is faster than a search
- ✕You're authoring a skill rather than finding one — use the \`skill-creator\` skill
- ✕You're vetting a skill on security or maintenance grounds — this ranks by popularity, not review
- ✕Environments without Node, since every command runs through \`npx\` — install manually instead

## SKILL.md

## Find Skills

This skill helps you discover and install skills from the open agent skills ecosystem.

## When to Use This Skill

Use this skill when the user:

- Asks "how do I do X" where X might be a common task with an existing skill
- Says "find a skill for X" or "is there a skill for X"
- Asks "can you do X" where X is a specialized capability
- Expresses interest in extending agent capabilities
- Wants to search for tools, templates, or workflows
- Mentions they wish they had help with a specific domain (design, testing, deployment, etc.)

## What is the Skills CLI?

The Skills CLI (`npx skills`) is the package manager for the open agent skills ecosystem. Skills are modular packages that extend agent capabilities with specialized knowledge, workflows, and tools.

**Key commands:**

- `npx skills find [query]` - Search for skills interactively or by keyword
- `npx skills add <package>` - Install a skill from GitHub or other sources
- `npx skills check` - Check for skill updates
- `npx skills update` - Update all installed skills

**Browse skills at:** https://skills.sh/

## How to Help Users Find Skills

### Step 1: Understand What They Need

When a user asks for help with something, identify:

1. The domain (e.g., React, testing, design, deployment)
2. The specific task (e.g., writing tests, creating animations, reviewing PRs)
3. Whether this is a common enough task that a skill likely exists

### Step 2: Check the Leaderboard First

Before running a CLI search, check the [skills.sh leaderboard](https://github.com/vercel-labs/skills) to see if a well-known skill already exists for the domain. The leaderboard ranks skills by total installs, surfacing the most popular and battle-tested options.

For example, top skills for web development include:

- `vercel-labs/agent-skills` — React, Next.js, web design (100K+ installs each)
- `anthropics/skills` — Frontend design, document processing (100K+ installs)

### Step 3: Search for Skills

If the leaderboard doesn't cover the user's need, run the find command:

```bash
npx skills find [query]
```

For example:

- User asks "how do I make my React app faster?" → `npx skills find react performance`
- User asks "can you help me with PR reviews?" → `npx skills find pr review`
- User asks "I need to create a changelog" → `npx skills find changelog`

### Step 4: Verify Quality Before Recommending

**Do not recommend a skill based solely on search results.** Always verify:

1. **Install count** — Prefer skills with 1K+ installs. Be cautious with anything under 100.
2. **Source reputation** — Official sources (`vercel-labs`, `anthropics`, `microsoft`) are more trustworthy than unknown authors.
3. **GitHub stars** — Check the source repository. A skill from a repo with <100 stars should be treated with skepticism.

### Step 5: Present Options to the User

When you find relevant skills, present them to the user with:

1. The skill name and what it does
2. The install count and source
3. The install command they can run
4. A link to learn more at skills.sh

Example response:

```
I found a skill that might help! The "react-best-practices" skill provides
React and Next.js performance optimization guidelines from Vercel Engineering.
(185K installs)

To install it:
npx skills add vercel-labs/agent-skills@react-best-practices

Learn more: https://skills.sh/vercel-labs/agent-skills/react-best-practices
```

### Step 6: Offer to Install

If the user wants to proceed, you can install the skill for them:

```bash
npx skills add <owner/repo@skill> -g -y
```

The `-g` flag installs globally (user-level) and `-y` skips confirmation prompts.

## Common Skill Categories

When searching, consider these common categories:

| Category | Example Queries |
| --- | --- |
| Web Development | react, nextjs, typescript, css, tailwind |
| Testing | testing, jest, playwright, e2e |
| DevOps | deploy, docker, kubernetes, ci-cd |
| Documentation | docs, readme, changelog, api-docs |
| Code Quality | review, lint, refactor, best-practices |
| Design | ui, ux, design-system, accessibility |
| Productivity | workflow, automation, git |

## Tips for Effective Searches

1. **Use specific keywords**: "react testing" is better than just "testing"
2. **Try alternative terms**: If "deploy" doesn't work, try "deployment" or "ci-cd"
3. **Check popular sources**: Many skills come from `vercel-labs/agent-skills` or `ComposioHQ/awesome-claude-skills`

## When No Skills Are Found

If no relevant skills exist:

1. Acknowledge that no existing skill was found
2. Offer to help with the task directly using your general capabilities
3. Suggest the user could create their own skill with `npx skills init`

Example:

```
I searched for skills related to "xyz" but didn't find any matches.
I can still help you with this task directly! Would you like me to proceed?

If this is something you do often, you could create your own skill:
npx skills init my-xyz-skill
```

Synced from [vercel-labs/skills@114c663](https://github.com/vercel-labs/skills/blob/114c6637a18676ac99b8bd34ffc7c9da61d072cb/skills/find-skills/SKILL.md) fetched May 24, 2026

Text is reproduced unmodified. Links to competing skill directories are shown as plain text or point to the source repository instead.

## Frequently asked questions

Get new skills in your inbox. What we added, what we rejected, and why. [See a past issue](https://agenticskills.io/newsletter).

## Related Skills

### Quick Stats

Source repo · this path

Stars32,149

Forks2,739

Last commit 2026-07-06

Contributors 3

LicenseMIT

Category [Productivity](https://agenticskills.io/category/productivity)

Source [vercel-labs/skills](https://github.com/vercel-labs/skills/tree/main/skills/find-skills "https://github.com/vercel-labs/skills/tree/main/skills/find-skills")

### Tags

discoveryinstallationmeta

## Keep exploring

Find Skills is one of 193 skills in the directory.

- [
	All Productivity skills
	15 skills in this category
	](https://agenticskills.io/category/productivity)
- [
	Workflow bundles
	Skills and MCP servers combined for a whole job
	](https://agenticskills.io/workflows)
- [
	MCP servers
	Audited servers that give agents live tool access
	](https://agenticskills.io/mcp)