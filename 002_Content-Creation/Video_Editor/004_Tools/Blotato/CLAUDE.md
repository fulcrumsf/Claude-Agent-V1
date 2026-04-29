---
title: "CLAUDE.md — Blotato"
type: config
domain: social-media
tags: [config, social-media, blotato, automation]
---

# CLAUDE.md — Blotato

## What This Is
Blotato is a social media posting API and platform. This folder contains the integration layer that lets Claude Code post content directly to multiple social platforms simultaneously using the Blotato API — no N8n required.

**Primary use case:** Post the same video/image to YouTube, TikTok, Instagram, Twitter/X, Bluesky, and more in a single command.

---

## How Blotato Is Used Here

### Direct API via Claude Code (primary)
Call the Blotato API directly from this workspace. No intermediary needed. Best for:
- Publishing a finished video to 4+ platforms at once
- Scheduling posts programmatically
- One-off posts during production workflows

### Via N8n (secondary / optional)
Blotato can also be triggered through N8n workflows if scheduling automation is needed. Not the primary approach here.

### Templates / Campaigns (back-pocket)
The folder includes a 30-day campaign workflow and carousel-style post templates. Tony doesn't have an active use case for these yet but they're available.

---

## Supported Platforms
YouTube, TikTok, Instagram, Twitter/X, Bluesky, LinkedIn, and more (connect accounts at my.blotato.com)

---

## MCP Server Setup
Blotato connects as an MCP server in Claude Code:

```json
"blotato": {
  "serverUrl": "https://mcp.blotato.com/mcp",
  "headers": {
    "blotato-api-key": "YOUR_BLOTATO_API_KEY_HERE"
  }
}
```

API key lives in `references/.env` as `BLOTATO_API_KEY`.

---

## Tech Stack
- **Social Posting:** Blotato API / MCP server
- **Image Generation:** Google AI Studio (Nano Banana Pro) via `tools/image_gen.py`
- **Asset Hosting:** Kie.ai (temporary file hosting, links expire after 3 days)
- **Content Management:** Airtable (`tools/airtable.py`) — optional, for campaigns
- **Cloud Automation:** Modal.com — optional, for serverless pipelines
- **Language:** Python (`tools/`)

---

## File Structure
```
Blotato/
├── CLAUDE.md                          ← This file
├── README.md                          ← Setup guide
├── .agent/
│   ├── AGENT_BASIC.md                 ← Agent instructions
│   ├── skills/
│   │   ├── blotato_best_practices/    ← Platform-specific posting rules
│   │   └── modal_deployment/          ← Serverless deployment skill
│   └── workflows/
│       └── 30-day-campaign.md         ← Full campaign workflow (back-pocket)
├── references/
│   ├── .env                           ← API keys (never commit)
│   ├── docs/prompt-best-practices.md
│   ├── inputs/                        ← Drop media files here
│   └── outputs/                       ← Generated assets land here
└── tools/
    ├── config.py
    ├── airtable.py
    ├── kie_upload.py
    ├── image_gen.py
    ├── utils.py
    └── providers/
        └── google.py
```

---

## API Keys Required
All stored in `references/.env`:
- `BLOTATO_API_KEY` — from my.blotato.com → API settings
- `GOOGLE_API_KEY` — from aistudio.google.com (for image gen)
- `KIE_API_KEY` — from kie.ai (for file hosting)
- `AIRTABLE_API_KEY` + `AIRTABLE_BASE_ID` — only needed for campaign workflows

---

## Agent Priorities
1. **Multi-platform posting is the main job** — same video, 4+ platforms, one command
2. **Never post without Tony's approval** — no autonomous publishing
3. **Never run generation endpoints without showing cost first** — image gen costs money per call
4. **Don't create throwaway scripts** — use existing `tools/` modules via inline Python
5. **Kie.ai links expire in 3 days** — don't store them as permanent URLs

---

## Cost Reference
| Model | Cost |
|---|---|
| Nano Banana | ~$0.04/image |
| Nano Banana Pro | ~$0.13/image |

Always confirm cost + item count with Tony before any batch generation.
