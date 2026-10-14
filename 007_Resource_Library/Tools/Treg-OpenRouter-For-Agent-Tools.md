---
title: "Treg — OpenRouter for Agent Tools"
type: tool-doc
category: ai-agents
form: github-repo
summary: "treg is an open-source proxy/registry that lets an AI agent call thousands of priced-per-call API endpoints (SEO, social, enrichment, scraping, ads) plus a team's own keys/skills/CLIs through one token and one base URL — credentials never leave the server. Self-hostable; hosted version live at treg.to, with a Claude Code plugin, an MCP surface, and a Grok Bot plugin."
url: https://github.com/superdesigndev/treg
tags:
  - github-repo
  - agent-tools
  - api-aggregator
  - mcp
  - treg
created: 2026-10-08
source: 000_Ingest/superdesigndevtreg OpenRouter for agent tools. Join community here httpsdiscord.gg6mQYYfFMAn.md
---

## Treg (OpenRouter for Tools)

**OpenRouter, but for agent tools instead of models.** Point an agent at one base URL with one token and it can do the job: a curated catalog of thousands of endpoints across many providers — SEO and backlinks, social and trends, people and company enrichment, ads, scraping, image and video generation — priced per call, from a cent, with no provider signup. Plus your own team's keys, skills and CLIs, callable by every teammate's agent without the credential ever leaving the server.

**Ask for the task, not the tool.** You don't need to know which vendor sells backlink data, or hold an account with them. Search for what you want to do, read the price, call it.

Built for the Superdesign team, live at [treg.to](https://treg.to/) — anyone can self-host (Apache 2.0 + additional terms: free to use commercially and self-host; don't redistribute as a competing hosted registry service without permission).

### Why it exists

The tools an agent needs for real work sit behind subscriptions nobody buys for a single run — Semrush $139/mo, Moz $99/mo, Crunchbase $99/mo, Apollo $59/seat — behind signup walls, or behind no public API at all. treg carries those accounts and bills fractions of a cent per call instead.

### How a call gets served (credential ladder, in order)
1. your team registered its own tool for that provider → that tool, that key
2. your team stored a secret for the provider → injected through a virtual tool
3. neither, and the endpoint has a verified public route → no provider key, free
4. otherwise → treg's own key, billed to the team's prepaid balance

Your own credential always beats treg's, so connecting a key you already pay for makes those calls free of the balance rather than duplicating cost.

### Three ways in
- **Claude Code plugin:** `/plugin marketplace add superdesigndev/treg` then `/plugin install treg@treg` — no token/config needed, walks you through CLI + sign-in + `treg mcp install` on first run.
- **CLI:** `curl -fsSL https://treg.to/install.sh | sh` → `treg login` → `treg catalog search "backlinks for a domain"` → `treg call <endpoint>` → `treg balance`.
- **Grok Bot plugin:** installed directly from x.ai's plugin marketplace, toggled on a per-capability basis (catalog:search, catalog:expand, call, call:media, etc.).

### Scale (as of this video/README, 2026-10)
3,600+ catalog endpoints, 86-94 providers (SEMrush, Moz, Majestic, SERP API, TikTok, Instagram, YouTube, Reddit, LinkedIn, Hunter, Apollo, Bright Data, Meta Ads, DataForSEO, and more), open source.

### Workflow skills (ready-made recipes)
| Skill | What it does |
|---|---|
| `treg` | Find and call any catalog tool, plus your own registered tools |
| `lead-signals` | Find in-market buyers from public signals (complaints, job changes, hiring, funding) |
| `make-ugc` | AI UGC videos: trending hooks, presenter, talking-head clips, captions |
| `jev-memory` | A Claude Code mod where Jev judges each prompt and keeps lasting preferences |

### Also relevant to this workspace
- `jev-memory` skill is a Jev-based Claude Code memory mod — worth comparing against this workspace's own claude-mem/memory system if revisited.
- Telemetry: the CLI sends anonymous usage to PostHog by default when using treg.to; disable with `TREG_TELEMETRY=0` or `DO_NOT_TRACK=1` (same env var this workspace already uses for `media-use`'s telemetry opt-out, per `001_Architecture/Memory/Global_Agent_Memory.md`).
- Roadmap includes deeper MCP support, finer permission tiers, at-rest key-management hardening.

## Related
- [[Treg-Inside-Grok-Bot-Is-A-Game-Changer]] — tutorial walkthrough of this exact tool, installed into Grok Bot, building a live SEO/backlink automation
