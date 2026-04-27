# App Building — Warehouse Manifest

## What This Is

This is the root workspace for all of Tony's business operations and digital product development. Every subfolder is a department that builds, automates, or manages one part of the overall business.

---

## ⚡ BEFORE BUILDING ANYTHING

**Always check the TOOLBOX first.**

Tony has pre-installed tools, CLIs, MCPs, skills, and plugins. Before writing a Python script, shell script, or suggesting new code, check whether a pre-existing tool already handles it.

**TOOLBOX location:** `/Users/tonymacbook2025/Documents/Claude-Agent/TOOLBOX.md`

Common tasks and what tools exist:
- **Web scraping** → Firecrawl (CLI, plugin, 8 skills)
- **Video/image generation** → kie.ai Python tools
- **Browser automation** → Playwright
- **n8n workflows** → n8n MCP + 6 skills
- **Notion** → Notion MCP (can be enabled)
- **Figma** → Figma MCP + skills
- **GitHub** → GitHub MCP
- **Publishing/scheduling** → Blotato
- **Cloudinary** → Cloudinary MCP (5 endpoints)
- **Obsidian vault** → Obsidian MCP

**Maintenance rule:** Every time a new skill, plugin, MCP, CLI tool, or Python tool is installed anywhere in the workspace, immediately update TOOLBOX.md. It's the single source of truth.

---

## Business Overview

A multi-stream digital business spanning content creation, e-commerce, affiliate marketing, digital products, and SaaS tools. The goal is systematic automation — each department builds toward replacing manual effort with reliable systems.

**Owner:** Tony
**Knowledge vault:** `/Users/tonymacbook2025/Documents/App Building/Obsidian-Vault/` (also accessible via Obsidian MCP)
**Graphify registry:** `/Users/tonymacbook2025/Documents/App Building/000_Graphify/REGISTRY.md`

---

## Vault-First Architecture

All shared knowledge (skills, tools, brand systems, case studies) lives in a unified Obsidian vault.

### Agent Instructions

Before asking the user for context:
1. **Search the vault** for relevant knowledge
2. **If you find partial answers but need clarification**, ask a focused question
3. **When adding new knowledge** (after creating a video, researching a tool, etc.), offer to save it to the vault

### Vault Structure

- **000_Skills/** — Reusable workflows (NotebookLM protocol, case study analysis, cinematic styles, video production workflow, content strategy framework)
- **001_Administration/** — Business strategy, revenue streams, ecosystem map, roadmap
- **002_Brands/** — Brand guidelines, content systems, case studies for: Anomalous-Wild, Board-Nomad, Unamoss-Creative, Ikigai-Digital-Studios
- **003_Tools/** — Tool documentation, model catalogs, pricing matrices, TOOLBOX
- **004_Research/** — Raw web clippings (auto-ingested), reference material
- **005_Wikis/** — Compiled knowledge articles by concept (Video-Production, Content-Strategy, AI-Agents, RAG-Systems)

### Vault Navigation Examples

- User: "Create a video explainer" → Search `000_Skills/NotebookLM-Protocol.md`
- User: "NeonParcel content strategy" → Search `002_Brands/` for the relevant brand
- User: "What models are cheapest?" → Search `003_Tools/Video-Generation/Pricing-Matrix.md`
- User: "I don't understand RAG" → Search `005_Wikis/RAG-Systems/`

### Read First

Start every session by reviewing `/Users/tonymacbook2025/Documents/App Building/Obsidian-Vault/000_VAULT-INDEX.md`.

---

## Departments

| Folder | Agent Purpose | Status |
|--------|--------------|--------|
| `002_Content-Creation/Video_Editor/` | YouTube content production for 12 channels. AI-assisted pipeline: research → script → assets → Remotion composition → publish. Has case-study skill and cinematic style system (6 production methodologies with model pricing). | Active |
| `002_Content-Creation/Whop_Clipping/` | Long-form video → Shorts pipeline for client brands. Tony posts on theme pages, earns per-view. | Planned |
| `002_Content-Creation/Social_Media_Marketing/` | Static image + carousel strategy for Pinterest and Instagram. Fashion/clothing niche focus. | Planned |
| `005_Ecommerce/POD/` | Print-on-demand Etsy store. Tony designs; fulfillment via POD service. Brands: Board-Nomad, Unamoss-Creative. | Active |
| `005_Ecommerce/Digital_Products/` | Digital downloadable wall art Etsy store + guides, downloads, funnels. Distribution via Gumroad, own website (Next.js + Sanity + Lemon Squeezy), email marketing. | Planned |
| `005_Ecommerce/KDP/` | Book publishing on Amazon Kindle Direct Publishing. | Active |
| `005_Ecommerce/Amazon_Merch/` | T-shirt designs on Amazon Merch on Demand. | Planned |
| `003_Apps/Upkeeply/` | App project (purpose TBD per project CLAUDE.md). | In Development |
| `003_Apps/AI_Character_Builder/` | AI character/avatar builder tool. | In Development |
| `004_Games/Roblox_Game/` | Roblox game development. Luau scripting, Studio architecture, subagents for research/build/UI/design. | In Development |
| Blotato (inside `002_Content-Creation/Video_Editor/004_Tools/`) | Social media publishing and scheduling automation. Active MCP server. | Active |

---

## Business Context

### Revenue Streams

| Stream | Status | Notes |
|--------|--------|-------|
| **YouTube (12 channels)** | Current | Ad revenue + sponsorships |
| **Whop clipping** | Current | Per-view income from client brands via theme pages |
| **Etsy POD** | Current | Print-on-demand (Board-Nomad, Unamoss-Creative) |
| **Etsy Digital** | Current | Downloadable wall art |
| **Travel affiliate** | Current | Amazon Associates, Impact, travel programs |
| **Amazon KDP** | Current | Book royalties |
| **Amazon Merch** | Current | T-shirt royalties |
| **Digital products** | Planned | Guides, downloads via Gumroad / website / email funnels |
| **Social media marketing** | Current | Content strategy for client/growth |

### Ecosystem

Content (video + social) → audience growth → affiliate clicks + store traffic + digital product sales → email list → repeat revenue.

The video engine is the top of the funnel.

---

## Shared Principles

- Every department builds toward automation — manual first, then systematize
- No publishing without explicit owner approval
- All API keys live in `~/.mcp-secrets.env` (sourced by shell)
- Obsidian vault is the source of truth for notes, strategy, and research
- Revenue streams are interconnected

---

## Video Editor Key Systems (For Root Agent Coordination)

When Tony asks about video production, case studies, or cinematic styles:

### Case Study System
- **Skill:** `case-study` (invoke via Skill tool)
- **Trigger:** User says "create a case study", "analyze this video", or provides a URL
- **Output:** case_study.md + 3 screenshots + viral score breakdown saved to `002_Content-Creation/Video_Editor/` under the relevant channel
- **Agent coordination:** If Tony asks "compare this video to ours," request case studies from Video Editor

### Cinematic Style System (6 Production Methodologies)
- **Location:** `002_Content-Creation/Video_Editor/002_Channels/Styles/`
- **Styles:** Archival B&W Documentary, 3D Synthetic, Satellite/Map, HD Underwater (primary), Wildlife, Scientific Infographic
- **Full documentation:** `CINEMATIC_STYLE_GUIDE.md`, `MODEL_SELECTOR.md`, `MODEL_CATALOG.json`, `MODEL_SELECTOR.json`
- **Cost optimization:** kie.ai is 30–70% cheaper than fal.ai
- **Agent coordination:** If new departments need video generation, point them to Video Editor's cinematic style system
