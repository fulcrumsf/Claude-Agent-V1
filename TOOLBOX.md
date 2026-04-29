---
title: "TOOLBOX: Complete Tool & Capability Reference"
type: guideline
domain: architecture
tags: [guideline, architecture, doc]
---

# TOOLBOX: Complete Tool & Capability Reference

**Last updated:** 2026-04-29

This is the single source of truth for all pre-installed tools, CLIs, MCPs, skills, and plugins.

**CRITICAL MAINTENANCE RULE:** Whenever you install a new skill, plugin, MCP, CLI, or Python tool anywhere in the workspace, **immediately update this file**. Add the new capability under the appropriate section below. Agents don't know tools exist unless they're documented here.

---

## System Maps (Install Maps)

Two maps live at `001_Architecture/Install_Maps/`. When Tony says **"look at the system map"** or **"look at the install map"**, read the appropriate file.

| Map | File | What it covers |
|-----|------|----------------|
| **Workspace Map** | [`001_Architecture/Install_Maps/Workspace-Map.md`](001_Architecture/Install_Maps/Workspace-Map.md) | Folder structure, departments, active projects |
| **System Map** | [`001_Architecture/Install_Maps/System-Map.md`](001_Architecture/Install_Maps/System-Map.md) | All installed apps, Homebrew, Python, Docker, MCPs, CLIs, scripts, skills, Adobe plugins |

**Auto-update script:** `001_Architecture/Scripts/generate_system_map.py`
- Runs weekly via cron (Sundays 3 AM)
- Refresh manually: `python3 001_Architecture/Scripts/generate_system_map.py`
- Output: `System-Map.md` + `system_map_data.json` (machine-readable)

---

## Web Scraping & URL Content

### Firecrawl (Multiple Interfaces)
- **Firecrawl CLI** (installed globally) — `firecrawl scrape <url> --only-main-content --format markdown`
- **Firecrawl Plugin** (enabled) — provides all skills below
- **Firecrawl Skills** — invoke via `/` prefix:
  - `/firecrawl-scrape` — Scrape a single URL with content extraction
  - `/firecrawl-search` — Web search and extract results
  - `/firecrawl-crawl` — Crawl an entire site
  - `/firecrawl-map` — Generate a site map
  - `/firecrawl-browse` — Browse and interact with pages
  - `/firecrawl-download` — Download files from URLs
  - `/firecrawl-agent` — Agent mode for complex scraping tasks
- **Python Tool:** `App Building/tools/enrich-notion-bookmarks.py` — uses Firecrawl to enrich Notion bookmarks with AI summaries
- **API Key:** `FIRECRAWL_API_KEY` in `~/.mcp-secrets.env`
- **When quota exhausted:** Falls back to Open Graph metadata extraction

---

## Browser Automation

### Playwright
- **Status:** Plugin installed but DISABLED (can be enabled quickly)
- **Skill:** `/playwright-cli` — browser automation via command line
- **Use case:** Automated testing, screenshot capture, form filling

---

## Stock Media & Open-Licensed Content

### Openverse API
- **What it does:** Search for Creative Commons and public domain images, audio, and video
- **Registration:** OAuth2 API-based (POST `/v1/auth_tokens/register/` endpoint)
- **API Key:** `OPENVERSE_API_KEY_CLIENT_ID` and `OPENVERSE_API_KEY_CLIENT_SECRET` in `~/.mcp-secrets.env`
- **Features:** Search filters for CC licensing, public domain content, usage rights
- **Use case:** Video Editor stock media sourcing — find free, legally-usable footage and images before generating AI assets
- **Status:** Registered and active (app: "Uno Mas Video Editor")
- **Tier rating:** 7/10 for images + audio (no video support yet)
- **Reference:** Full public domain source comparison in `App Building/Video Editor/references/docs/PUBLIC_DOMAIN_SOURCES_RATING.md`

### Complete Public Domain Source Ratings
- **Location:** `App Building/Video Editor/references/docs/PUBLIC_DOMAIN_SOURCES_RATING.md`
- **What it includes:** 1-10 ratings for 13 public domain sources (NASA, Pexels, Wikimedia, LOC, archive.org, etc.)
- **Tier system:** Query priority and fallback logic for each asset type (footage, photos, audio, maps, etc.)
- **Use case:** Documentary research skill uses this to decide which sources to query in which order

---

## Video Generation

### kie.ai (Primary Platform)
- **Python Tool:** `/Users/tonymacbook2025/Documents/App Building/Obsidian-Vault/003_Tools/Video-Generation/kie_video_gen.py` — unified API to all kie.ai video models
  - Supports: **Veo 3.1**, **Kling 3.0**, **Wan 2.6**, **Sora 2**
  - Usage: `python3 /Users/tonymacbook2025/Documents/App Building/Obsidian-Vault/003_Tools/Video-Generation/kie_video_gen.py "[PROMPT]" output.mp4 "veo3"`
- **API Key:** `KIE_API_KEY`
- **Pricing:** 30–70% cheaper than fal.ai for equivalent models
- **When to use:** Always try kie.ai first for video generation

### Blotato (Publishing)
- **What it does:** Publish generated videos to YouTube and social media
- **Python integration:** `kie_upload.py` for file uploads before publishing
- **API Key:** `BLOTATO_API_KEY`

---

## Image Generation

### kie.ai (Primary Platform)
- **Python Tool:** `/Users/tonymacbook2025/Documents/App Building/Obsidian-Vault/003_Tools/Image-Generation/kie_image_gen.py` — Nano Banana 2 and Nano Banana Pro
  - Usage: `python3 /Users/tonymacbook2025/Documents/App Building/Obsidian-Vault/003_Tools/Image-Generation/kie_image_gen.py "[PROMPT]" output.jpg --model nano-banana-2`
- **Skill:** `/nano-banana-pro-prompts-recommend-skill` — AI recommendations for image prompts

### fal.ai (Fallback)
- **Python Tool:** `/Users/tonymacbook2025/Documents/App Building/Obsidian-Vault/003_Tools/Image-Generation/image_gen.py` — fallback to Google AI Studio (Gemini 2.5 Flash) or fal.ai
- **API Key:** `FAL.AI_API_KEY`
- **When to use:** Only if kie.ai doesn't have the model you need

---

## Text-to-Speech

### ElevenLabs
- **Python Tool:** `/Users/tonymacbook2025/Documents/App Building/Obsidian-Vault/003_Tools/Text-To-Speech/audio_tts.py`
  - Generates TTS with word-level timestamps
  - Outputs per-scene MP3 files and `beat_sheet.json`
  - Usage: `python3 /Users/tonymacbook2025/Documents/App Building/Obsidian-Vault/003_Tools/Text-To-Speech/audio_tts.py <script.md> <output_dir> [--voice <id>]`
- **API Key:** `ELEVENLABS_API_KEY`
- **Output:** Feeds into video beat sheet and Remotion composition

---

## YouTube & Video Research

### yt-dlp (Video Download)
- **Location:** `/Library/Frameworks/Python.framework/Versions/3.13/bin/yt-dlp`
- **What it does:** Download YouTube videos and public videos at 720p
- **Invoked by:** `download-video` skill in Video Editor

### Gemini Video Analysis
- **Python Tool:** `/Users/tonymacbook2025/Documents/App Building/Obsidian-Vault/003_Tools/AI-Analysis/gemini_video_analysis.py` — analyze video style, camera work, humor, AI-prompt potential
  - Usage: `python3 /Users/tonymacbook2025/Documents/App Building/Obsidian-Vault/003_Tools/AI-Analysis/gemini_video_analysis.py "<URL>" -o output.md`
- **Skill:** `/analyze-video` — same functionality via skill interface

### Case Study Generator
- **Python Tool:** `/Users/tonymacbook2025/Documents/App Building/Obsidian-Vault/000_Skills/case_study_generator.py` — full automated case study pipeline
  - Fetches YouTube metadata via YouTube Data API
  - Runs Gemini 10-section analysis
  - Downloads video and extracts 3 screenshots
  - Outputs to `references/channels/[channel]/case_studies/`
- **Skill:** `/case-study` — same functionality, triggered by "do a case study" or competitor URL
- **API Keys:** `YOUTUBE_DATA_API_KEY`, `YOUTUBE_ANALYTICS_API_KEY`, `GOOGLE_API_KEY`

---

## Video Editing & Composition

### FFmpeg
- **Location:** `/opt/homebrew/bin/ffmpeg`
- **What it does:** Frame extraction, audio/video stitching, encoding
- **Invoked by:** `extract-frames` skill and `video_stitcher.py`

### Remotion (React-based Video Composition)
- **Project:** `App Building/my-video/` (full Next.js + Remotion app)
- **Video Editor:** `remotion-app/src/remotion/` — components and compositions
- **MCP:** `npx @remotion/mcp@latest` (active in `~/.claude/.mcp.json`)
- **Skill:** `/remotion-best-practices` — 30+ rules covering animations, audio, assets, 3D, captions, etc.
- **Use case:** Programmatically compose videos as React components

### Video Stitching
- **Python Tool:** `/Users/tonymacbook2025/Documents/App Building/Obsidian-Vault/003_Tools/Video-Generation/video_stitcher.py` — stitch scenes (video.mp4 + audio.mp3) into final MP4
  - Usage: `python3 /Users/tonymacbook2025/Documents/App Building/Obsidian-Vault/003_Tools/Video-Generation/video_stitcher.py scene_1/ scene_2/ ... -o final.mp4`

### Final Cut Pro XML Export
- **Python Tool:** `/Users/tonymacbook2025/Documents/App Building/Obsidian-Vault/003_Tools/Remotion/export_fcpxml.py` — export timeline as FCPXML 1.9
  - Usage: `python3 /Users/tonymacbook2025/Documents/App Building/Obsidian-Vault/003_Tools/Remotion/export_fcpxml.py --video-dir outputs/<project>`
  - Allows importing into Final Cut Pro for further editing

---

## Notion

### Notion MCP Plugin
- **Status:** Installed but DISABLED (can be enabled)
- **What it does:** Full Notion workspace integration — pages, databases, properties
- **Enable:** Turn on in `~/.claude/settings.json` plugins
- **API Key:** `NOTION_API_KEY`

### Notion Bookmark Enrichment
- **Python Tool:** `/Users/tonymacbook2025/Documents/App Building/Obsidian-Vault/003_Tools/Notion/enrich-notion-bookmarks.py` — autonomous script
  - Processes all 14 bookmark databases
  - Scrapes URLs via Firecrawl
  - Generates AI summaries via Claude
  - Updates Notion descriptions
  - Runs: `source ~/.mcp-secrets.env && python3 /Users/tonymacbook2025/Documents/App Building/Obsidian-Vault/003_Tools/Notion/enrich-notion-bookmarks.py`

---

## Obsidian / Knowledge Vault

### Obsidian MCP
- **Vault Location:** `/Users/tonymacbook2025/Documents/App Building/Obsidian-Vault`
- **API Key:** `OBSIDIAN_API_KEY`
- **What it does:** Read/write access to all 1,382+ markdown notes in the vault

### Obsidian Skills
- `/obsidian` — General Obsidian integration
- `/obsidian-cli` — CLI-based access
- `/obsidian-markdown` — Markdown format in Obsidian
- `/obsidian-bases` — Obsidian Bases feature (database-like functionality)

### Future: Obsidian RAG
- Plan exists for Obsidian vault + Qdrant + search_vault MCP (separate, planned system)

---

## GitHub

### GitHub MCP Plugin
- **Status:** Enabled
- **What it does:** Full GitHub repo management — PRs, issues, commits, branches
- **Auth:** `GITHUB_PERSONAL_ACCESS_TOKEN` in `~/.mcp-secrets.env`
- **Skills** (via plugin):
  - Git workflow: `/commit`, `/commit-push-pr`, `/clean_gone`
  - PR/code review: `/review-pr`, `/code-review`

---

## Figma

### Figma MCP
- **Status:** Enabled
- **Endpoint:** `https://mcp.figma.com/mcp`
- **What it does:** Design generation, component export, design system integration

### Figma Skills
- `/frontend-design` — Guided frontend design workflows
- `/stitch-design-taste` — Design taste via Stitch design tool

---

## Cloudinary (Media Storage & CDN)

### Cloudinary MCP Plugin
- **Status:** Enabled
- **API Key:** (Cloudinary credentials in plugin settings)
- **5 MCP Endpoints:**
  1. Asset Management — upload, organize, manage media files
  2. Environment Configuration — manage Cloudinary account settings
  3. Structured Metadata — apply metadata to assets
  4. Analysis — analyze media, get stats
  5. MediaFlows — automated media transformation workflows

---

## n8n Workflow Automation

### n8n MCP
- **Connected to:** `unomas.app.n8n.cloud`
- **What it does:** Create, run, inspect n8n workflows from Claude
- **Auth:** `N8N_MCP_TOKEN` in `~/.mcp-secrets.env`

### n8n Skills (6 available)
- `/n8n-workflow-patterns` — Design patterns for workflows
- `/n8n-node-configuration` — Configure n8n nodes
- `/n8n-code-javascript` — Write JavaScript code nodes
- `/n8n-expression-syntax` — n8n expression language
- `/n8n-validation-expert` — Validation patterns
- `/n8n-mcp-tools-expert` — MCP tools integration

---

## Publishing & Social Scheduling

### Blotato
- **What it does:** YouTube + social media (Instagram, TikTok, Facebook) publishing
- **Invoked by:** `kie_upload.py` for file uploads
- **API Key:** `BLOTATO_API_KEY`
- **Integration:** Final step in Video Editor production pipeline

### Meta Graph API
- **What it does:** Facebook/Instagram publishing and analytics
- **API Key:** `META_GRAPH_API_KEY`

---

## Vercel (Deployment)

### Vercel Plugin
- **Status:** Enabled
- **What it does:** Deploy Next.js/full-stack apps, manage environments, domains, analytics
- **Commands:**
  - `/vercel:deploy` — Deploy to Vercel
  - `/vercel:env` — Manage environment variables
  - `/vercel:status` — Check deployment status
  - Plus 15+ more Vercel-specific commands

---

## Airtable (Content Tracking)

### Airtable Integration
- **Python Module:** `tools/airtable.py` — CRUD operations in Video Editor
- **Use case:** Track video content, performance scores, publishing status
- **API Key:** `AIRTABLE_API_KEY`
- **Status:** Planned — structure TBD, not yet fully operational

---

## AI Research

### Perplexity
- **What it does:** AI-powered web search for viral topics, trends, research
- **Skill:** Referenced in Video Editor workflows for topic research
- **API Key:** `PERPLEXITY_API_KEY`

### NotebookLM
- **What it does:** Grounded research notebooks — answers only from sources you provide
- **Skill:** `/notebooklm` — create research notebooks, query them fact-checked
- **Use case:** Video research that can't hallucinate beyond uploaded sources

### YouTube Transcript
- **Skill:** `/youtube-transcript` — extract and analyze YouTube video transcripts

---

## Code Development Workflow

### Git Commands
- `/commit` — Interactive git commit with staging
- `/commit-push-pr` — Commit + push + create PR (full workflow)
- `/clean_gone` — Clean up deleted branches locally

### Code Review & Quality
- `/code-review` — Structured code review process
- `/review-pr` — Pull request review with detailed analysis
- `/feature-dev` — Guided feature development workflow

### Plugins (Language Servers)
- **pyright-lsp** (enabled) — Python type checking via Pyright
- **typescript-lsp** (enabled) — TypeScript type checking via TypeScript LS

---

## Project Management

### GSD (Get Shit Done) System
- **49 commands** — `/gsd:<command>` — full project lifecycle management
- **Core commands:**
  - `/gsd:new-project` — Start a new project with roadmap
  - `/gsd:plan-phase` — Plan a phase with research + task breakdown
  - `/gsd:execute-phase` — Execute phase with atomic commits
  - `/gsd:verify-work` — Verify phase goal achievement
  - `/gsd:progress` — Check overall progress
  - `/gsd:ship` — Ship completed work
- **Plus:** 44 more commands for backlog, milestones, debugging, auditing, etc.

### Ralph Loop
- **Command:** `/ralph-loop` — autonomous recurring task agent
- **Cancel:** `/cancel-ralph` — stop the loop
- **Use case:** Automated, repeating workflows without manual triggering

---

## Video Editor Specific Tools

### Video Editor Skills (in Video-Editor `.agents/skills/` and Obsidian Vault)
- `/download-video` — Download YouTube videos at 720p
- `/extract-frames` — Extract frames from video at 0.5s intervals
- `/kie-api-fetch` — Fetch and document kie.ai model APIs
- `/fal-api-fetch` — Fetch and document fal.ai model APIs
- `/analyze-video` — Gemini analysis of video style
- `/case-study` — Full automated case study generation (located in `/Obsidian-Vault/000_Skills/`)
- `/documentary-research` — CC0 footage research (archive.org, Openverse, NASA, etc.)
- `/storytelling` — Comprehensive scriptwriting framework (Curiosity Loop, 3-Act, Hero's Journey, etc.)
- `/anomalous-wild-scriptwriter` — Channel-specific script writing (Anomalous Arc™)
- `/video-beat-sheet` — Convert script to production beat sheet
- `/ai-footage-prompter` — Generate video/image prompts for AI generation
- `/title-hook-generator` — Generate titles, hooks, descriptions for CTR

---

## API Keys Reference

All keys stored in `~/.mcp-secrets.env`. When a tool requires a key, it's listed in `TOOLBOX.md` under that tool's section.

| Service | Key Variable | Used By |
|---------|--------------|---------|
| Firecrawl | `FIRECRAWL_API_KEY` | Firecrawl CLI, skills, enrich-notion-bookmarks.py |
| kie.ai | `KIE_API_KEY` | kie_video_gen.py, kie_image_gen.py |
| fal.ai | `FAL.AI_API_KEY` | image_gen.py fallback |
| ElevenLabs | `ELEVENLABS_API_KEY` | audio_tts.py |
| Notion | `NOTION_API_KEY` | Notion MCP, enrich-notion-bookmarks.py |
| Obsidian | `OBSIDIAN_API_KEY` | Obsidian MCP |
| YouTube Data | `YOUTUBE_DATA_API_KEY` | case_study_generator.py, Video Editor |
| YouTube Analytics | `YOUTUBE_ANALYTICS_API_KEY` | Video analytics tracking |
| Google / Gemini | `GOOGLE_API_KEY` | Gemini image/video analysis |
| OpenAI | `OPENAI_API_KEY` | General AI tasks |
| OpenRouter | `OPENROUTER_API_KEY` | Multi-model routing |
| Perplexity | `PERPLEXITY_API_KEY` | Topic research |
| Blotato | `BLOTATO_API_KEY` | YouTube/social publishing |
| Airtable | `AIRTABLE_API_KEY` | Content tracking |
| Cloudinary | (plugin settings) | Media storage/CDN |
| n8n | `N8N_MCP_TOKEN` | n8n MCP |
| GitHub | `GITHUB_PERSONAL_ACCESS_TOKEN` | GitHub MCP |
| Meta (Facebook/Instagram) | `META_GRAPH_API_KEY` | Social publishing |
| PubMed | `PUBMED_API_KEY` | Scientific research |

---

## System CLIs (OS Level)

| CLI | Location | What It Does |
|-----|----------|-------------|
| `ffmpeg` | `/opt/homebrew/bin/ffmpeg` | Video frame extraction, stitching, encoding |
| `yt-dlp` | `/Library/Frameworks/Python.framework/Versions/3.13/bin/yt-dlp` | Download videos from YouTube and public sources |
| `python3` | `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3` | Python interpreter for all .py tools |

---

## How to Update This File

Whenever you:
1. Install a new skill (via `/skill-creator` or manually)
2. Enable a disabled plugin
3. Add a new MCP server to `.mcp.json` or `settings.json`
4. Install a global CLI tool
5. Create a new Python tool in `tools/`

**Immediately add it to the appropriate section above.** Keep sections organized by capability (what the tool does), not by tool type. Example structure:

```
## [Capability Name]

### [Tool/Service Name]
- **[Details]:** Description
- **API Key:** `KEY_NAME` (if applicable)
- **Usage:** Command or invocation pattern
- **When to use:** Guidance on when to prefer this tool
```

This is the single source of truth. If it's not here, agents won't know it exists.
