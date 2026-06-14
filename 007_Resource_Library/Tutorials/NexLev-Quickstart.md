---
title: "NexLev-Quickstart"
type: tutorial
category: video-production
tags:
  - tutorial
  - how-to
  - youtube-analytics
  - setup
  - video-production
created: 2026-06-06
source: 000_Ingest/Nexlev Docs.md
---
## Quickstart

Connect NexLev MCP to your preferred AI assistant and start analyzing YouTube channels in under 5 minutes. Choose the platform you use below.

## Prerequisites

Before you begin, make sure you have:

- **Active NexLev account** — Free for all users. [Upgrade to Pro](https://dashboard.nexlev.io/docs/mcp/quickstart?required_nexlev_lite_pro_access=true) for higher quota limits.

### Via Claude's custom connector

**Step 1 — Active NexLev account**

Make sure your NexLev account is active before proceeding.

**Step 2 — Open Claude Connectors**

Go to **claude.ai → Settings → Connectors → Add custom connector**. You can also open the connectors page directly:

[Connect on Claude →](https://claude.ai/customize/connectors)

![Claude Settings → Connectors → Add custom connector](https://dashboard.nexlev.io/_next/image?url=%2Fimages%2Fdocumentation%2Fmcp%2Fclaude-add-custom-connector.png&w=1920&q=75)

**Step 3 — Enter the connector details**

Fill in the following information exactly as shown:

FieldValue

Name `NexLev`

Server URL `https://prod.dashboard.nexlev.io/api/claude-mcp`

Authentication `OAuth`

![Enter NexLev connector details in Claude](https://dashboard.nexlev.io/_next/image?url=%2Fimages%2Fdocumentation%2Fmcp%2Fclaude-step-3-connector-details.png&w=1920&q=75)

**Step 4 — Approve the connection**

After adding the connector, please click the **Connect** button and Claude will redirect you to sign in with your NexLev account.

**Step 5 — Set tool permissions**

Go to **claude.ai → Settings → Connectors**, find NexLev, and click **Configure**. Then set **Tool permissions** to **Always allow** — this lets Claude use your NexLev tools automatically without asking you every time.

![Set NexLev tool permissions to Always allow in Claude](https://dashboard.nexlev.io/_next/image?url=%2Fimages%2Fdocumentation%2Fmcp%2Fclaude-step-5-permissions.png&w=1920&q=75)

**No API key needed.** Claude.ai uses OAuth to connect directly to your NexLev account. Works on web and mobile — your tools sync across all devices.

[Connect on Claude →](https://claude.ai/customize/connectors)

## What You Can Do Next

Once connected, start using NexLev tools directly inside your AI chat:

### Long Form Channel Search

```
Find 20 long-form channels related to the minecraft niche
```

### Short Form Channel Analysis

```
Show me 15 viral YouTube Shorts channels in the comedy niche
```

### Keyword Research

```
Find high-volume, low-competition keywords for cooking content
```

### Content Strategy

```
What content strategy should I use for a tech review channel with 10K subscribers?
```

### Competitive Research

```
Compare successful channels in the fitness niche and identify common patterns
```

## Understanding NexLev Responses

When you use NexLev through Claude, ChatGPT, or Claude Code CLI, you'll receive interactive widgets displaying:

- **Channel data** — Comprehensive metrics, performance indicators, and growth analytics
- **Sortable results** — Click column headers to sort by different metrics
- **Expandable details** — View in-depth information for each result
- **Filtering options** — Refine results by various criteria
- **Pagination** — Navigate through large result sets

**Pro Tip:** Results are interactive! You can sort, filter, and expand channels directly within the chat interface for deeper analysis.

## Rate Limits

All limits are **per user, per tool, and reset every 24 hours**.

Lite and Premium share identical rate limits across all tools. If you're on the Premium plan, the numbers in the Lite column apply to you.

### Channel Discovery

| Tool & Description | Free | Lite | Pro |
| --- | --- | --- | --- |
| Long-form channel search | 10 | 150 | 300 |
| Short-form channel search | 10 | 150 | 300 |
| Similar channels | 5 | 20 | 30 |
| Faceless outlier finder | 10 | 100 | 200 |
| Faceless channel check | 5 | 100 | 300 |
| Channel resolver | 10 | 100 | 500 |
| Niche channel search | 10 | 100 | 200 |

Per user · resets every 24 hours

[Upgrade to Pro →](https://dashboard.nexlev.io/docs/mcp/quickstart?required_nexlev_lite_pro_access=true)

### Video Intelligence

| Tool & Description | Free | Lite | Pro |
| --- | --- | --- | --- |
| Similar videos | 5 | 20 | 30 |
| Video search | 10 | 150 | 300 |
| YouTube search | 50 | 100 | 500 |
| Video details | 10 | 100 | 300 |
| Video comments | 10 | 150 | 300 |
| Video transcript | 5 | 150 | 300 |
| Bulk video transcripts | 5 | 50 | 100 |
| Video subtitle | 5 | 150 | 300 |
| Bulk video subtitles | 5 | 50 | 100 |
| Channel outlier videos | 10 | 50 | 100 |

Per user · resets every 24 hours

[Upgrade to Pro →](https://dashboard.nexlev.io/docs/mcp/quickstart?required_nexlev_lite_pro_access=true)

### Visual Search

| Tool & Description | Free | Lite | Pro |
| --- | --- | --- | --- |
| Similar thumbnails | 5 | 20 | 30 |

Per user · resets every 24 hours

[Upgrade to Pro →](https://dashboard.nexlev.io/docs/mcp/quickstart?required_nexlev_lite_pro_access=true)

### Visual Video Analysis

| Tool & Description | Free | Lite | Pro |
| --- | --- | --- | --- |
| Watch YouTube video and ask | 1 | 5 | 15 |
| Watch Instagram video and ask | 1 | 5 | 15 |
| Watch TikTok video and ask | 1 | 5 | 15 |

Per user · resets every 24 hours

[Upgrade to Pro →](https://dashboard.nexlev.io/docs/mcp/quickstart?required_nexlev_lite_pro_access=true)

### Channel Analytics

| Tool & Description | Free | Lite | Pro |
| --- | --- | --- | --- |
| Channel analytics | 5 | 20 | 30 |
| Daily analytics | 5 | 20 | 30 |
| Short vs long views | 5 | 20 | 30 |
| Geography & revenue | 5 | 20 | 30 |
| Batch channel metrics | 5 | 20 | 30 |
| Channel categories | 10 | 100 | 500 |
| Channel formats | 10 | 100 | 500 |
| Channel videos | 50 | 100 | 300 |
| Channel shorts | 50 | 100 | 300 |
| Channel playlists | 50 | 100 | 300 |
| Channel about | 50 | 100 | 300 |

Per user · resets every 24 hours

[Upgrade to Pro →](https://dashboard.nexlev.io/docs/mcp/quickstart?required_nexlev_lite_pro_access=true)

### Monetization

| Tool & Description | Free | Lite | Pro |
| --- | --- | --- | --- |
| Channel monetization check | 5 | 100 | 300 |
| Video monetization check | 5 | 100 | 300 |
| Video RPM | 5 | 150 | 300 |

Per user · resets every 24 hours

[Upgrade to Pro →](https://dashboard.nexlev.io/docs/mcp/quickstart?required_nexlev_lite_pro_access=true)

### Niche Intelligence

| Tool & Description | Free | Lite | Pro |
| --- | --- | --- | --- |
| Niche overview | 5 | 20 | 30 |
| Niche categories | 10 | 100 | 500 |
| Niche formats | 10 | 100 | 500 |
| Niche tags | 5 | 100 | 500 |

Per user · resets every 24 hours

[Upgrade to Pro →](https://dashboard.nexlev.io/docs/mcp/quickstart?required_nexlev_lite_pro_access=true)

### Swipefile

Swipefile is available on **Lite, Pro, and Premium** plans only — Free plan users do not have access.

| Tool & Description | Free | Lite | Pro |
| --- | --- | --- | --- |
| List swipefile folders | 0 | 200 | 500 |
| List swipefile items | 0 | 200 | 500 |
| Get folder insights | 0 | 100 | 300 |
| Save to swipefile | 0 | 100 | 300 |
| Update swipefile item | 0 | 50 | 200 |
| Move swipefile item | 0 | 30 | 100 |
| Delete swipefile item | 0 | 30 | 100 |
| Create swipefile folder | 0 | 20 | 50 |

Per user · resets every 24 hours

[Upgrade to Pro →](https://dashboard.nexlev.io/docs/mcp/quickstart?required_nexlev_lite_pro_access=true)

### Personal Channel Analytics

Personal Channel Analytics tools is available on **Lite, Pro, and Premium** plans only — Free plan users do not have access.

| Tool & Description | Free | Lite | Pro |
| --- | --- | --- | --- |
| List my YouTube channels | 0 | 100 | 200 |
| Channel overview | 0 | 20 | 50 |
| Channel analytics | 0 | 20 | 50 |
| Revenue report | 0 | 15 | 40 |
| Top videos | 0 | 15 | 40 |
| Audience demographics | 0 | 15 | 40 |
| Traffic sources | 0 | 15 | 40 |
| Device & OS report | 0 | 15 | 40 |
| Geography report | 0 | 15 | 40 |
| Playback locations | 0 | 15 | 40 |
| Content sharing | 0 | 15 | 40 |
| Subscriber status | 0 | 15 | 40 |
| Video analytics | 0 | 20 | 50 |
| Audience retention | 0 | 15 | 40 |

Per user · resets every 24 hours

[Upgrade to Pro →](https://dashboard.nexlev.io/docs/mcp/quickstart?required_nexlev_lite_pro_access=true)