---
title: "App Building — Warehouse Manifest"
type: config
domain: architecture
tags: [config, architecture, doc]
---

# App Building — Warehouse Manifest

## Token Efficiency

**Minimize tokens on every interaction.** When you have a choice between asking a clarifying question vs. making a reasonable assumption — make the assumption. When you can just do the work vs. asking for confirmation — do the work. When you can reference a skill by name vs. loading its full content into context — reference by name.

**Skills directory:** Skills live in `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.0.7/skills/` and project-local skill directories. If Tony asks about a domain (design, marketing, video production, etc.), check if a relevant skill exists in the cached skills directory and invoke it via the Skill tool rather than pre-loading knowledge. Only use skills when they're actually needed for the current task.

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
**Knowledge vault:** workspace root is the Obsidian vault (`/Users/tonymacbook2025/Documents/Claude-Agent/`) — accessible via Obsidian MCP
**Graphify registry:** `/Users/tonymacbook2025/Documents/Claude-Agent/001_Architecture/Graphify/REGISTRY.md`

## Session Memory — Read First

Before starting work, scan these folders for logs and past decisions so Tony never has to repeat himself:
- **Logs:** `001_Architecture/Logs/` — session summaries, what was done, what changed
- **Memory:** `001_Architecture/Memory/` — conventions, tag systems, user preferences, workflow rules
- **Feedback Loop:** `001_Architecture/Feedback_Loop/` — captured corrections, preferences, and validated approaches
- **Self-Learning Loop:** `001_Architecture/Self_Learning_Loop/` — periodic insights and patterns from past work
- **Claude memory:** `~/.claude/projects/-Users-tonymacbook2025-Documents-Claude-Agent/memory/MEMORY.md` — persistent cross-session memory (auto-written by Claude)

If a file in Logs, Memory, Feedback, or Self-Learning covers the current topic, read it before asking Tony for clarification.

## Session Memory — Write Automatically

Capture knowledge without being asked. These four layers update continuously:

### Feedback Loop (`001_Architecture/Feedback_Loop/`)
Save automatically when Tony gives feedback. Don't wait for him to say "record this." Detect it from the conversation:
- **Corrections:** "stop doing X", "that's wrong", "don't do it that way" → what should have been done, why it matters
- **Preferences revealed:** "I prefer X", "I don't like Y", "this is overkill" → capture the preference with context
- **Validated approaches:** Tony accepts or affirms an unusual choice ("perfect", "yes that's what I meant", no pushback on a non-obvious decision) → capture what worked and why
- Write to: `YYYY-MM-DD_Feedback.md` — one per day, append entries

### Session Logs (`001_Architecture/Logs/`)
Compact record of what happened, not a transcript. One line per significant action: what changed, why, what files were touched, what decisions were made, what's pending. Write to: `YYYY-MM-DD_Session-Log.md`

### Self-Learning Loop (`001_Architecture/Self_Learning_Loop/`)
At session close, review the day's work and identify patterns: what went wrong, what worked well, what keeps recurring, what could be automated. Be honest about mistakes. Write to: `YYYY-MM-DD_Self-Review.md`

### Cross-Session Memory
Also update `~/.claude/.../memory/MEMORY.md` with the system — user preferences go to user feedback entries, project decisions go to project entries, external references go to reference entries.

**Trigger:** When Tony says "I'm about to close this session" or similar, write all four. Also write incrementally throughout the session — don't batch everything at the end.

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

Start every session by reading the federation registry at `/Users/tonymacbook2025/Documents/Claude-Agent/001_Architecture/Graphify/REGISTRY.md` — it routes any lookup question to the correct domain graph.

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

## File Naming Convention

**Apply this rule to every new file or directory created in this workspace.**

- **No spaces** — use `_` or `-` as word separators
- **Capitalize the first letter of every word**: `Video_Pipeline_PDR.md` (not `video_pipeline_pdr.md`)
- **Acronyms stay fully uppercase**: `MCP_Gateway_Controller`, `Video_Pipeline_PDR`, `AI_Footage_Prompter`
- **Python scripts (`.py`) are exempt** — do not rename them, as other scripts may reference them by their current name

**Examples:**

| Bad | Good |
|-----|------|
| `video_pipeline_pdr.md` | `Video_Pipeline_PDR.md` |
| `Kling 2.6_Image_to_Video.md` | `Kling_2.6_Image_to_Video.md` |
| `anomalous-wild-hybrid.md` | `Anomalous-Wild-Hybrid.md` |
| `case-study.md` | `Case-Study.md` |

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

## graphify

This project has a graphify knowledge graph at graphify-out/.

Rules:
- Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- After modifying code files in this session, run `graphify update .` to keep the graph current (AST-only, no API cost)
