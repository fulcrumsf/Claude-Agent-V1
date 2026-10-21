# Agent-OS Command Center Visual Dashboard Roadmap

> **Date:** 2026-09-30  
> **Status:** Architecture Seed / Brain Dump Roadmap (Phase 3)  
> **Target:** Unified Mission Control for Tony's Business Operations  
> **Workspace Alignment:** Encapsulates `001_Architecture` through `007_Resource_Library`

---

## 1. Vision & Purpose

Tony operates a multi-faceted digital business empire inside `/Users/tonymacbook2025/Documents/Agent-OS/`, spanning:
- **12 YouTube Channels** (Neon Parcel, Reimagined Realms, Anomalous Wild, Bored Nomad, Business Origin Stories, etc.).
- **Social Media & Clipping** (TikTok, Instagram Reels, Facebook Reels, Shorts).
- **Affiliate Marketing & TikTok Shop Creator** programs.
- **Print-on-Demand (POD)** on Etsy, Printify, and Redbubble.
- **Digital Products** on Etsy, expanding to Shopify / Lemon Squeezy.
- **Brand & Niche Websites** (`006_Websites/`).

Currently, orchestrating these pipelines requires juggling separate terminal commands, scattered scripts in `001_Architecture/Tools/`, multiple chat windows (Claude Code, Codex, Antigravity IDE), and manual checks.

The **Agent-OS Command Center Dashboard** is envisioned as a single-pane-of-glass Mission Control web/desktop application that brings all operations, agent conversations, and department pipelines into a unified, visually engaging interface.

---

## 2. Core Dashboard Modules

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      AGENT-OS UNIFIED COMMAND CENTER                         │
├─────────────────────┬────────────────────────────────────────────────────────┤
│                     │  [Tab: Central War Room]                               │
│  DEPARTMENTS        │  Live streaming chat: Tony ↔ Claude ↔ Gemini ↔ Codex   │
│                     ├────────────────────────────────────────────────────────┤
│  ▶ War Room         │  [Active Goal / Dispatch Input]                        │
│  ▶ Video Pipelines  │  "Run storyboard QA on Neon Parcel Shot 02 and audit"   │
│  ▶ Social / Clips   ├────────────────────────────────────────────────────────┤
│  ▶ E-Commerce (POD) │  [Quick Stats / Metrics Bar]                           │
│  ▶ Digital Products │  Active Productions: 3 | Queued Uploads: 5 | Health: OK│
│  ▶ Websites / SEO   ├────────────────────────────────────────────────────────┤
│  ▶ Resource Library │  [Department Live Canvas]                              │
│                     │  (Kanban / Pipeline / Analytics / Listing Grid)        │
└─────────────────────┴────────────────────────────────────────────────────────┘
```

---

### Module 1: The Central War Room & Agent Chat
- **Interactive Chat Canvas:** An integrated chat interface communicating directly with the **Multi-Agent Bridge MCP** (see [`Multi_Agent_Bridge_MCP_Slack_Plan.md`](file:///Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Plans/Multi_Agent_Bridge_MCP_Slack_Plan.md)).
- **Multi-Agent Feed:** Real-time visibility into Claude Code, Antigravity (Gemini), and Codex discussing tasks, sharing code diffs, and completing audits.
- **Single-Prompt Dispatch:** A global prompt bar where Tony enters high-level instructions (e.g., *"Scaffold a new Anomalous Wild episode on Glass Frogs and generate voiceover"*), which the system routes to the appropriate agents and scripts.

---

### Module 2: Video Production Pipeline Hub (`002_Content-Creation`)
- **Channel Selector:** Quick switching between all 12 channels (Neon Parcel, Anomalous Wild, Reimagined Realms, etc.).
- **Visual Production Kanban:**
  - `Concept / Script` ➔ `TTS & Beat Sheet (ElevenLabs)` ➔ `Storyboard QA (Kie/Gemini)` ➔ `Video Gen (Seedance/Veo/Wan)` ➔ `Assembly & Foley (Mirelo/MMAudio)` ➔ `Review & Signoff`.
- **Media Player & Frame Inspector:** Built-in video player with timestamped inspection findings (`gemini_video_inspection.py` feedback).
- **One-Click Blotato Publishing:** Trigger pre-signed upload and multi-platform posting to YouTube, TikTok, Instagram, and Facebook Reels with verified tags and disclosure settings.

---

### Module 3: Social Media, Clipping & TikTok Shop Affiliate Desk
- **Hook & Trend Radar:** Scraping and cataloging top-performing affiliate product hooks and viral structures.
- **Clipping Pipeline:** Interface for taking long-form horizontal masters and processing them through `Subject-Aware-Reframer` into vertical Shorts/Reels.
- **Draft Queue:** Manage TikTok Shop Creator video drafts before pushing to the TikTok app for product link attachment.

---

### Module 4: E-Commerce & Merch Matrix (`005_Ecommerce`)
- **Print-on-Demand (POD) Operations:**
  - Catalog and mockup status across **Etsy**, **Printify**, and **Redbubble**.
  - Batch generation runner: Kick off design variants with Nano Banana 2 / GPT-Image-1, apply mockup templates, and generate SEO-optimized titles and tags.
- **Digital Products Desk:**
  - Active listings on **Etsy**.
  - Staging and deployment for **Shopify** and **Lemon Squeezy** digital product storefronts.
  - Asset bundling, PDF guide generation, and automated delivery package validation.

---

### Module 5: Brand Websites & Affiliate Marketing (`006_Websites`)
- **Site Status Dashboard:** Uptime, deployment status (Vercel / Cloudflare), and quick links to live sites.
- **SEO & Content Health:** Automated keyword rank tracking and content freshness monitor.
- **Affiliate Program Matrix:** Tracking compliance docs, approved links, and commission rates across active affiliate partner programs (`005_Affiliate_Marketing/` & `007_Resource_Library/Docs/Affiliate_Marketing/`).

---

### Module 6: Resource Library & Ingest Inspector (`007_Resource_Library`)
- An embedded view of the **Resource Library Visualizer** (`001_Architecture/Tools/Resource-Library-Visualizer/serve.py`).
- Fast visual review of incoming screenshots, YouTube tutorials, prompts, and tool documentation.
- One-click triggers for re-running vision enrichment or archiving rejected items.

---

## 3. Technology Stack & Design Direction

When Tony is ready to construct this dashboard, the recommended stack is:
- **Framework:** Next.js (App Router) or Vite + React (TypeScript).
- **Styling:** Premium dark-mode design system with curated HSL color palettes, glassmorphism cards, dynamic micro-animations, and clean typography (e.g. Outfit, Inter).
- **Backend / Integration:**
  - Local Node.js / Python API gateway connecting to the **Agent-OS Multi-Agent Bridge MCP**.
  - Server-Sent Events (SSE) or WebSockets for live streaming terminal output and agent conversations.
- **Desktop Packaging:** Can run as a local web server (`http://localhost:3000`) or wrapped with Electron / Tauri for native window management.

---

## 3b. Build-path research, 2026-10-16 (not built — documented only)

Tony restated this vision independently this session (hadn't connected it back to this file), prompting a fresh architecture pass. Findings:

- **Claude Artifacts ruled out as the main interface.** Explored at length: no localhost/self-hosting, can't embed in Obsidian (claude.ai blocks iframing), and the `sample` capability (in-page Claude chat) has no memory between calls and no real tool access — nothing like a persistent agent session. Artifacts remain the right tool for narrower review dashboards (the Revenue Stream Scorecard, a future video-review-with-timestamped-comments tool), just not for "my actual Claude Code session running inside a tab."
- **The real build for "chat exactly like my Claude Code session, inside a tab" is the Claude Agent SDK** (TypeScript/Python, the same engine Claude Code itself runs on) with a custom Next.js/Vite frontend — not shelling out to `claude -p` and parsing output. Setting `cwd` to a department folder + `settingSources: ['user','project']` loads that department's own CLAUDE.md, skills, hooks (`fs_guard` included) and MCP servers automatically, so each tab = one persistent SDK session scoped to that department's folder, no separate router agent needed.
- **Billing risk, confirmed real (2026-10-16):** the Claude Agent SDK requires API-key billing and explicitly cannot run on a claude.ai subscription (Pro/Max) — it's pay-per-token, separate from Tony's plan. Must be sized/budgeted before any SDK build, not treated as a footnote.
- **A free existing alternative exists and should be tried first:** [`siteboon/claudecodeui`](https://github.com/siteboon/claudecodeui) (14.1k stars, actively maintained, AGPL-3.0) — a web/mobile UI that wraps the existing Claude Code CLI session (no SDK rewrite, no separate API billing, no per-token cost). Install via `npx @siteboon/claude-code-ui`, no setup. Worth testing against this exact use case before building anything custom.
- **Where it runs:** localhost only, not deployed — the agent needs Tony's real filesystem, ffmpeg, Python scripts and `~/.env-secrets`; Vercel/Cloudflare can't host that. If remote/phone access is wanted later, a Cloudflare Tunnel + Access in front of the local server is the right shape, not a cloud deploy.
- **Effort reality check:** a working first version (chat, tabs, session resume, approvals) is roughly 1–2 weekends with Claude building it; matching Claude Code's actual polish (tool-call display, diffs, interrupts, media previews) is several weeks; after that it's ongoing solo-maintained upkeep as the SDK changes.
- **Recommendation, not yet acted on:** before building anything, set up one pinned Claude Code session per department in named sidebar groups (zero build, available today) and try `claudecodeui` against that for about a week. Only build the SDK version — starting with one department, e.g. Video Editor, never all at once — if a real, written-down gap remains after that trial.

---

## 4. Phased Rollout Plan

- [ ] **Phase 1 (Active Pre-requisite):** Build the Multi-Agent Bridge MCP + Slack Channel (`Multi_Agent_Bridge_MCP_Slack_Plan.md`) so agents can execute tasks and communicate headlessly.
- [ ] **Phase 2 (Tool Standardization):** Standardize outputs of existing video, ecommerce, and ingest scripts into clean JSON schemas for UI consumption.
- [ ] **Phase 3 (Dashboard MVP):** Scaffold the web application with the Central War Room chat and the Video Production Pipeline Kanban.
- [ ] **Phase 4 (Full Expansion):** Integrate E-Commerce, Digital Products, Website monitors, and the Resource Library Visualizer.
