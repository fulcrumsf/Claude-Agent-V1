---
title: "Workspace System Map"
type: reference
category: architecture
tags:
  - workspace
  - system-map
  - navigation
  - architecture
created: 2026-04-28
---

# Workspace System Map

**Root:** `/Users/tonymacbook2025/Documents/Agent-OS/`

This is Tony's operating system. All agents (Claude Code, Codex, Antigravity, Warp terminal agents) share this workspace as the single source of truth. Every subfolder is a department. This map tells any agent where to look and where to put things.

---

## Top-Level Structure

| Folder | Purpose |
|--------|---------|
| `000_Daily/` | Daily notes and journal entries |
| `000_Ingest/` | **Landing zone** — files dropped here via Obsidian Web Clipper or manually. Run ingest skill to process. |
| `000_Project-Ideas/` | Raw project concepts and ideation notes |
| `000_Wiki/` | **Synthesized knowledge wiki** (Karpathy-style LLM wiki). Agent-written, cross-linked pages. |
| `001_Architecture/` | **System brain** — all meta-level docs: memory, logs, maps, skills, feedback, graphify config |
| `002_Content-Creation/` | Content production departments |
| `003_Apps/` | App development projects |
| `004_Games/` | Game development projects |
| `005_Ecommerce/` | E-commerce departments |
| `006_Websites/` | Website projects by brand |
| `007_Resource_Library/` | **Raw reference files** — source materials, bookmarks, API docs, tool docs, models, prompts |
| `008_Investments/` | Investment research and portfolio tooling |
| `009_AI_Jobs/` | AI job onboarding, contracts, and work references |

---

## 000_Wiki/ — Knowledge Wiki

Synthesized knowledge pages created by agents during ingest. Not raw sources — these are curated, cross-linked articles.

| Subfolder | Content |
|-----------|---------|
| `AI-Agents/` | Claude, GPT, agent frameworks, MCP, orchestration, LLM tools |
| `RAG-Systems/` | RAG, embeddings, memory systems, vector databases |
| `App-Dev/` | React, Next.js, APIs, SDKs, coding tools |
| `Content-Strategy/` | Content strategy, SEO, marketing, social media |
| `Architecture/` | System architecture, workflows, automation, n8n, pipelines |
| `Video-Production/` | Video production, animation, Remotion, kie.ai, fal.ai, image generation |
| `log.md` | Append-only ingest log — what was processed, when, where it landed |
| `index.md` | Master index of all wiki pages by category |

---

## 001_Architecture/ — System Brain

| Subfolder | Content |
|-----------|---------|
| `Automation/` | Automation scripts and workflow configs |
| `Audit_Reports/` | Architecture audits, reusable audit prompts, and system review reports |
| `Feedback_Loop/` | Daily feedback logs (corrections, preferences, validated approaches) |
| `Graphify/` | Graphify config, hooks, registry |
| `Install_Maps/` | **This file and other workspace maps** — always check here before exploring blind |
| `Karpahty_LLM_Wiki/` | LLM wiki methodology notes (Andrej Karpathy system) |
| `Logs/` | Session logs — what was done each session |
| `MCP/` | MCP server configs and docs |
| `Memory/` | Conventions, tag systems, user preferences, workflow rules |
| `Memory/ChatGPT_Profile/` | Second-brain profile notes distilled from the ChatGPT export |
| `Obsidian/Templates/` | Obsidian Templater templates |
| `Scripts/` | Utility scripts |
| `Self_Learning_Loop/` | Periodic self-review and pattern recognition notes |
| `Skills/` | **Authoritative skill source.** `~/.claude/skills`, `~/.codex/skills`, `~/.gemini/skills` all symlink here. Add skills here; all agents pick them up automatically. |
| `Tools/` | Tool documentation organized by type |
| `Business-Strategy.md` | Business strategy overview |
| `Ecosystem-Map.md` | Full business ecosystem map |
| `Revenue-Streams.md` | Revenue stream overview |
| `Strategic-Roadmap.md` | Strategic roadmap |

### 001_Architecture/Tools/ Subfolders

| Subfolder | Content |
|-----------|---------|
| `AI-Analysis/` | AI analysis tools |
| `Airtable/` | Airtable docs and configs |
| `Asset-Sourcing/` | Asset sourcing tools |
| `Image-Generation/` | Image generation tool docs |
| `Remotion/` | Remotion video framework docs |
| `Text-To-Speech/` | TTS tool docs |
| `Tool-Manager/` | Cost-routing CLI (`tm`), model catalog, and monthly refresh script. Key files: `tool_manager.py` (tm CLI), `catalog_refresh.py` (monthly auto-refresh + Airtable sync), `data/model_catalog.json` (24-model cross-platform pricing matrix), `data/pricing_cache.json` (live API pricing cache) |
| `Video-Generation/` | Video generation tool docs, model catalog. Subfolders: `Channels/` (per-channel scripts — Anomalous_Wild, Reimagined_Realms), `Generic_Tools/` (reusable batch scripts), `Pipeline_Docs/` (pipeline planning), `Hyperframes/` (HTML renderer), `Video-Use/` (agent editor). Key scripts in `Channels/Reimagined_Realms/`: `assemble.py` (universal assembly — takes `production_folder` arg, reads `Production/assemble_config.json`), `batch_generate_images.py` (GPT Image 2 batch, `--clips --overwrite` flags), `batch_generate_videos.py` (Seedance batch, beatmap-driven durations) |

---

## 002_Content-Creation/ — Content Departments

| Subfolder | Content |
|-----------|---------|
| `Video_Editor/` | YouTube content production — 12 channels. AI pipeline: research → script → assets → Remotion → publish |
| `Video_Editor/001_Configuration/` | Channel configs, API keys references |
| `Video_Editor/002_Channels/` | Per-channel content, styles, case studies |
| `Video_Editor/003_Remotion/` | Remotion compositions |
| `Video_Editor/004_Tools/` | Blotato publishing tool only — all Python pipeline scripts moved to `001_Architecture/Tools/Video-Generation/` |
| `Social_Media_Marketing/` | Pinterest and Instagram static content strategy |
| `Whop_Clipping/` | Long-form → Shorts pipeline for client brands |

---

## 003_Apps/ — App Development

| Subfolder | Content |
|-----------|---------|
| `Upkeeply/` | App project (in development) |
| `AI_Character_Builder/` | AI character/avatar builder tool |
| `MCP_Gateway_Controller/` | MCP gateway controller app (dashboard + server) |

---

## 004_Games/ — Game Development

| Subfolder | Content |
|-----------|---------|
| `Roblox_Game/` | Roblox game — Luau scripting, Studio architecture |

---

## 005_Affiliate_Marketing/ — Affiliate Marketing Programs

Multi-platform affiliate marketing operations. Each subfolder is a separate affiliate program or network.

| Subfolder | Content |
|-----------|---------|
| `Amazon_Associates/` | Amazon Associates affiliate program |
| `Impact_Affiliates/` | Impact affiliate network |
| `TravelPayouts/` | TravelPayouts travel affiliate network |
| `Expedia/` | Expedia affiliate program |
| `Bookaway/` | Bookaway ground transport affiliate program |
| `GetYourGuide/` | GetYourGuide tours and activities affiliate |
| `Hostelworld/` | Hostelworld accommodation affiliate |
| `JRPass/` | JR Pass Japan rail affiliate |
| `Klooks/` | Klook travel experiences affiliate |
| `SafetyWing/` | SafetyWing travel insurance affiliate |
| `Stay22/` | Stay22 accommodation affiliate |
| `Digistore24/` | Digistore24 digital products affiliate network |
| `12Go/` | 12Go Asia transport affiliate |
| `Higgsfield/` | Higgsfield AI video tool affiliate |
| `Magnific/` | Magnific AI upscaler affiliate |
| `Opusclip/` | OpusClip video clipping tool affiliate |
| `VidIQ/` | VidIQ YouTube tool affiliate |
| `Tiktok_Shop_Affiliate/` | TikTok Shop affiliate program |

---

## 005_Ecommerce/ — E-Commerce Departments

| Subfolder | Content |
|-----------|---------|
| `POD/Board-Nomad/` | Print-on-demand Etsy store — Board-Nomad brand |
| `POD/Unamoss-Creative/` | Print-on-demand Etsy store — Unamoss-Creative brand |
| `Digital_Products/` | Digital downloadable art, guides, funnels |
| `KDP/` | Amazon Kindle Direct Publishing (books) |
| `Amazon_Merch/` | Amazon Merch on Demand (t-shirts) |
| `Etsy-Bored_Nomad/` | Bored Nomad Etsy store |
| `Etsy-Ikigai/` | Ikigai Etsy store |
| `Tiktok_Shop-Uno_Mas_Creative/` | TikTok Shop for Uno Mas Creative brand |

---

## 006_Websites/ — Brand Websites

| Subfolder | Content |
|-----------|---------|
| `Bored_Nomad/` | Bored Nomad website |
| `Ikigai_Digital_Studio/` | Ikigai Digital Studio website |
| `Uno_Mas_Creative/` | Uno Mas Creative website |

---

## 007_Resource_Library/ — Raw Reference Files

Source materials, bookmarks, API docs, and references. Files land here after ingest processing.

| Subfolder | Content |
|-----------|---------|
| `Bookmarks/` | Web clips saved via Obsidian Web Clipper |
| `Docs/` | Documentation organized by department |
| `Docs/Video_Editor/Kie.ai_API/` | kie.ai API documentation |
| `Docs/Video_Editor/Fal.ai_API/` | fal.ai API documentation |
| `Docs/Video_Editor/Research_API/` | Research/data API docs |
| `Docs/Video_Editor/Storytelling_Writing/` | Writing and storytelling references |
| `Docs/Affiliate_Marketing/` | ToS, rules, and compliance docs for all affiliate programs |
| `Docs/Admin/` | Admin and business documentation |
| `Models/` | AI model specs, pricing, capabilities |
| `Tools/` | Tool reference docs |
| `Tutorials/` | Step-by-step tutorials |
| `Prompts/` | Reusable prompt templates |
| `Design_Inspiration/` | Visual inspiration references and aesthetic bookmarks |
| `Personal/` | Personal-interest references and non-business captures |
| `Project_Ideas/` | Raw project concepts and future idea seeds |
| `Research/` | Competitive analysis, channel studies, benchmarks, and market/product research |
| `Workflows/` | Process maps, flowcharts, and workflow references |
| `Obsidian_Attachments/Visual_Assets/` | Raw screenshot files extracted by image ingest |
| `Undetermined/` | Mistimed or blurry screenshots moved by image ingest |
| `Archive/` | Archived items |
| `Archive/Automation_Workflows/` | Old automation workflow files |
| `OpenAI_history/` | Readable ChatGPT conversation history in `.md` form; links out to the visual asset library |
| `OpenAI_history/Needs Ingestion/N8n-Screenshots/` | Filename-based bucket for raw N8n workflow screenshots that Tony can review or delete later |
| `OpenAI_history/Needs Ingestion/Screenshots/` | General screenshot bucket for non-N8n raw images that are easy to recognize by filename |
| `OpenAI_history/Needs Ingestion/Generated-Images/` | Raw generated image files that are clearly labeled in the filename |
| `OpenAI_history/Needs Ingestion/Typography/` | Typography-related image captures and searches grouped by filename |
| `OpenAI_history/Needs Ingestion/Framing/` | Framing example images grouped by filename |
| `OpenAI_history/Needs Ingestion/Consular-Service-Assistant/` | Repeated consular assistant screenshots grouped by filename |
| `OpenAI_history/Needs Ingestion/Pastel-Waves/` | Repeated pastel waves artwork grouped by filename |
| `OpenAI_history/Needs Ingestion/DNS-Checker/` | DNS checker / propagation tool screenshots grouped by filename |
| `OpenAI_history/Needs Ingestion/Summer-Flowers-Arrangement/` | Floral prompt/image assets grouped by filename |
| `Obsidian_Attachments/` | Canonical attachment library for images and other linked assets |
| `Obsidian_Attachments/OpenAI_Images/` | OpenAI image inputs and outputs plus their attachment indexes |
| `Obsidian_Attachments/README.md` | Folder-level explainer for the attachment library |
| `OpenAI_history/README.md` | Folder-level explainer for the conversation library |

---

## Key System Files (Root Level)

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Instructions for Claude Code agents |
| `AGENTS.md` | Instructions for Codex and other OpenAI-compatible agents |
| `GEMINI.md` | Instructions for Gemini CLI agents |
| `TOOLBOX.md` | Master list of all installed tools, CLIs, MCPs, scripts |
| `graphify-out/` | Graphify knowledge graph output |

---

## Maintenance

This map is maintained by agents. When new folders are created:
1. Add them to this map immediately
2. Run `graphify update .` to update the knowledge graph

## 008_Investments/ — Investment Department

Tony's investment research and analytics department. Used for market research, portfolio tooling, watchlists, and active investment system work.

| Subfolder | Content |
|-----------|---------|
| `CLAUDE.md` | Department playbook for investment analysis and sandboxed trading rules |

## 009_AI_Jobs/ — AI Jobs Department

Reference area for AI job onboarding, platform contracts, worker agreements, and work-specific legal/reference docs Tony may need to look up later.

| Subfolder | Content |
|-----------|---------|
| `Mercor/` | Mercor onboarding contracts and worker reference set |
| `CLAUDE.md` | Department playbook for AI job reference handling |

**Last updated:** 2026-07-04
