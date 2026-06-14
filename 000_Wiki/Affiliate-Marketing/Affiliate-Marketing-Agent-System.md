---
title: "Affiliate Marketing Agent System"
type: wiki
category: affiliate-marketing
tags:
  - affiliate-marketing
  - compliance
  - link-management
  - content-monetization
source: 005_Affiliate_Marketing/CLAUDE.md
created: 2026-05-29
---

# Affiliate Marketing Agent System

## What It Is

A master affiliate marketing coordinator agent that lives in `005_Affiliate_Marketing/`. It manages 18+ affiliate programs across travel, tools, and e-commerce — handling compliance, content creation with link injection, link management, and performance tracking. It orchestrates sub-agents in other departments rather than producing content directly.

## Key Concepts

- **Compliance-first** — every link placement is checked against the program's ToS before content is created or published. All ToS docs live in `007_Resource_Library/Docs/Affiliate_Marketing/`
- **Interview-driven content** — Tony initiates a topic (e.g. "Bangkok guide"); the agent interviews him, routes to the website or content agent, then auto-identifies and injects affiliate opportunities into the draft
- **API-powered tables** — for destination guides, the agent generates recommendation tables (budget / mid / premium) using program APIs where available (Expedia, Hostelworld, etc.)
- **Link management** — current state: `Links.md` per program folder; target state: Airtable as canonical link catalog with API lookup, optional link shortening via Bitly or custom domain
- **Performance tracking** — API-first, CSV export fallback for programs without APIs; ideal end state is a unified dashboard via Google Analytics or equivalent

## Active Programs (18)

Travel: TravelPayouts, Expedia, Bookaway, GetYourGuide, Hostelworld, JR Pass, Klook, SafetyWing, Stay22, 12Go
General/Tools: Amazon Associates, Impact Affiliates, Digistore24
AI Tools: Higgsfield, Magnific, OpusClip, VidIQ
Social Commerce: TikTok Shop Affiliate

## How Tony Uses This

All interactions through Agent-OS root. Typical flows:
- "Show me what's performing" → pulls commission/click data across programs
- "Write a blog post about [destination]" → interview → draft → compliance check → inject links → disclose
- "Create a PDF resource" → same as above but also checks PDF link policies per program
- New program joined → ingest ToS doc → automatically available for compliance checks

## Folder Structure

```
005_Affiliate_Marketing/          ← agent home
  Amazon_Associates/
  Impact_Affiliates/
  TravelPayouts/
  ... (one per program)
  CLAUDE.md                       ← agent instructions

007_Resource_Library/Docs/Affiliate_Marketing/   ← ToS and compliance docs (shared across all agents)
```

Content produced does NOT live in `005_Affiliate_Marketing/` — it routes to `006_Websites/` (blog posts) or `002_Content-Creation/` (video, social).

## Related

- [[Architecture/Workspace-Map]] — full folder structure reference
- [[Video-Production/OpusClip-Agent-Opus-Affiliate-Program]] — OpusClip program notes
- [[Video-Production/Submagic-Affiliate-Program]] — Submagic program notes
- [[TikTok-Shop-Affiliate-Compliance]] — TikTok Shop creator campaign and affiliate compliance reference
- [[TikTok-Shop-Affiliate-Do-Dont-Cheat-Sheet]] — Short reference for allowed and disallowed TikTok Shop affiliate content patterns
