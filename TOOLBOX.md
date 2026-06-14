---
title: "TOOLBOX: Complete Tool & Capability Reference"
type: guideline
domain: architecture
tags: [guideline, architecture, doc]
---

# TOOLBOX: Complete Tool & Capability Reference

**Last updated:** 2026-04-30

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

**Vision audit script:** `001_Architecture/Scripts/check_vision_needed.py`
- Checks images against their category-folder notes to determine which files actually need vision analysis
- Searches `007_Resource_Library/{Tools,Tutorials,Research,...}/` for paired markdown notes (NOT legacy Asset_Notes/)
- Reads description from `## AI Analysis` section; detects filler ("likely a saved reference", "general visual reference", etc.)
- Run: `python 001_Architecture/Scripts/check_vision_needed.py "/path/to/images"`
- Pipe-friendly: add `--needs-vision-only` to print just filenames needing vision
- Always run this BEFORE calling the ingest script — avoids duplicate API spend
- Output: count of already-cataloged vs needs-vision, with per-file reasons

**Skill registry sync script:** `001_Architecture/Scripts/sync_skill_index.py`
- Regenerates `001_Architecture/Skills/Skill-Index.md` from every `SKILL.md` in the skills tree
- Designed to run from Claude/Gemini hooks after skill edits so Gemini can discover new or changed skills automatically
- Safe to run manually at any time if the registry needs a refresh

**Image Extraction script:** `001_Architecture/Scripts/process_image_ingest.py`
- Uses OpenRouter vision first (qwen model), then OpenAI vision fallback, to extract semantic knowledge
- OCR is not the default path for screenshot renaming
- Run: `python3 001_Architecture/Scripts/process_image_ingest.py "/path/to/images"`
- Output: `Title-Case-With-Dashes.md` note in correct category folder, raw image moved to `Visual_Assets/`, undetermined items to `Undetermined/`

**Image case fix script:** `001_Architecture/Scripts/fix_image_case.py`
- Post-process cleanup: converts any remaining lowercase kebab-case image filenames in Visual_Assets to Title-Case-With-Dashes
- Uses paired note's frontmatter `title:` field as source of truth; falls back to word-capitalizing the stem
- Updates `![[...]]` embeds in paired notes and logs to `rename_log.md`
- Run: `python3 001_Architecture/Scripts/fix_image_case.py` (dry run) or `--apply` to rename

**Notion export processor:** `001_Architecture/Scripts/process_notion_edit.py`
- Heuristic offline batch processor for large Notion exports when the export mixes md, json, csv, images, PDFs, spreadsheets, and Pages files.
- Run: `python3 001_Architecture/Scripts/process_notion_edit.py "/path/to/Notion-Edit"`
- Output: routes files into the current Resource Library categories, creates markdown notes for images/text exports, and leaves the source folder empty.

**Markitdown CLI** — converts files to Markdown
- Install: `pip install 'markitdown[all]'` (v0.1.5, already installed)
- CLI: `markitdown file.pdf -o output.md`
- Supports: PDF, Word (.docx), PowerPoint (.pptx), Excel (.xlsx), HTML, images, audio, zip
- Use case: Step 0 of ingest pipeline — converts binary files to `.md` before classify/route steps run
- Also usable standalone anywhere in the workspace

**Video Extraction script:** `001_Architecture/Scripts/process_video_ingest.py`
- Automates multi-step FFmpeg scene detection and audio Whisper transcription for incoming raw videos.
- Run: `python3 001_Architecture/Scripts/process_video_ingest.py "/path/to/video.mp4"`
- Output: Properly structured package with keyframes and transcript files in `007_Resource_Library/Videos/`.

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
- **API Key:** `FIRECRAWL_API_KEY` in `~/.env-secrets`
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
- **API Key:** `OPENVERSE_API_KEY_CLIENT_ID` and `OPENVERSE_API_KEY_CLIENT_SECRET` in `~/.env-secrets`
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

### video-use (Agent-Driven Video Editor)
- **Repo:** `001_Architecture/Tools/Video-Generation/video-use/`
- **Skill:** `/video-use` — symlinked into `001_Architecture/Skills/video-use/`
- **What it does:** Drop raw footage + pre-recorded VO clips in a folder, agent cuts, trims silences, self-evaluates, outputs `final.mp4`. Audio-first: transcript drives cut decisions.
- **Pipeline:** Transcribe (ElevenLabs Scribe) → Pack → LLM Reasons → EDL → Render → Self-Eval
- **API key:** `ELEVENLABS_API_KEY` via `source ~/.env-secrets` (never stored in .env)
- **When to use:** Raw footage → clean cut. Primary engine for the TikTok Shop affiliate video workflow.
- **Wiki:** `000_Wiki/Video-Production/Video-Use-Agent-Editor.md`

### Hyperframes (HTML-Native Video Renderer)
- **CLI:** `hyperframes` — globally installed via npm (v0.6.25)
- **Repo:** `001_Architecture/Tools/Video-Generation/hyperframes/`
- **Skills (all symlinked into `001_Architecture/Skills/`):**
  - `/hyperframes` — composition authoring, captions, TTS, audio-reactive animation
  - `/hyperframes-cli` — dev-loop: init, lint, preview, render, doctor
  - `/gsap` — GSAP timeline animations, frame-accurate seeking
- **What it does:** Write HTML → render MP4. Motion graphics, text overlays, subtitle animations, 3D assets, shader transitions. 50+ catalog blocks. Website-to-video.
- **No API key needed** for core rendering. TTS uses Kokoro (local).
- **When to use:** After video-use produces a clean cut, when captions/overlays/motion graphics are needed. Not yet active in affiliate workflow — add when analytics justify it.
- **Wiki:** `000_Wiki/Video-Production/Hyperframes-Video-Rendering.md`

### FFmpeg
- **Location:** `/opt/homebrew/bin/ffmpeg`
- **What it does:** Frame extraction, audio/video stitching, encoding
- **Invoked by:** `extract-frames` skill, `video_stitcher.py`, video-use, and Hyperframes

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
  - Runs: `source ~/.env-secrets && python3 /Users/tonymacbook2025/Documents/App Building/Obsidian-Vault/003_Tools/Notion/enrich-notion-bookmarks.py`

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

## Cross-Agent Memory

### claude-mem
- **Version:** 12.4.9
- **What it does:** Captures coding-session activity, compresses it into searchable observations, and injects relevant context into future sessions.
- **Installed for:** Claude Code and Gemini CLI
- **Codex:** Local `thedotmack` marketplace registered from `/Users/tonymacbook2025/.claude/plugins/marketplaces/thedotmack`; use worker/search route if plugin tools are not loaded in the active session.
- **Worker:** `http://localhost:37701`
- **Status:** `npx claude-mem status`
- **Start:** `npx claude-mem start`
- **Data:** `/Users/tonymacbook2025/.claude-mem/`
- **Gemini hooks:** `/Users/tonymacbook2025/.gemini/settings.json`
- **Gemini context injection:** `/Users/tonymacbook2025/.gemini/GEMINI.md`
- **Claude search:** `/mem-search`
- **Privacy:** Wrap sensitive text in `<private>...</private>` to exclude it from memory.

---

## GitHub

### GitHub MCP Plugin
- **Status:** Enabled
- **What it does:** Full GitHub repo management — PRs, issues, commits, branches
- **Auth:** `GITHUB_PERSONAL_ACCESS_TOKEN` in `~/.env-secrets`
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

### Cloudinary Python SDK
- **Status:** Installed (`pip3 install cloudinary --break-system-packages`)
- **Version:** 1.44.2 — `/opt/homebrew/lib/python3.14/site-packages`
- **Credentials:** `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_Key`, `CLOUDINARY_API_Secret` in `~/.env-secrets`
- **Primary use:** Upload local images to get public HTTPS URLs for AI APIs that require hosted image URLs (e.g. `firstFrame`/`lastFrame` in kie.ai Seedance, Veo3, etc.)
- **Pattern:**
  ```python
  import cloudinary, cloudinary.uploader
  cloudinary.config(cloud_name=os.environ['CLOUDINARY_CLOUD_NAME'],
                    api_key=os.environ['CLOUDINARY_API_Key'],
                    api_secret=os.environ['CLOUDINARY_API_Secret'], secure=True)
  result = cloudinary.uploader.upload(local_path, public_id="my_id", overwrite=True)
  url = result['secure_url']  # public HTTPS URL
  ```

---

## n8n Workflow Automation

### n8n MCP
- **Connected to:** `unomas.app.n8n.cloud`
- **What it does:** Create, run, inspect n8n workflows from Claude
- **Auth:** `N8N_MCP_TOKEN` in `~/.env-secrets`

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

## Affiliate Marketing (005_Affiliate_Marketing/)

Multi-platform affiliate marketing operations. 18 programs tracked across travel, digital tools, and e-commerce.

### Programs Active
| Program | Network | Niche |
|---------|---------|-------|
| Amazon Associates | Direct | General / travel gear |
| Impact Affiliates | Impact | Multi-brand network |
| TravelPayouts | TravelPayouts | Flights, hotels, travel |
| Expedia | Direct | Hotels / travel |
| Bookaway | Direct | Ground transport |
| GetYourGuide | Direct | Tours & activities |
| Hostelworld | Direct | Accommodation |
| JR Pass | Direct | Japan rail |
| Klook | Direct | Travel experiences |
| SafetyWing | Direct | Travel insurance |
| Stay22 | Direct | Accommodation |
| Digistore24 | Digistore24 | Digital products |
| 12Go | Direct | Asia transport |
| Higgsfield | Direct | AI video tool |
| Magnific | Direct | AI upscaler |
| OpusClip | Direct | Video clipping |
| VidIQ | Direct | YouTube tools |
| TikTok Shop Affiliate | TikTok | Product affiliate |

### Key Docs
- Affiliate compliance docs → `007_Resource_Library/Docs/Affiliate_Marketing/` (ToS, allowed/prohibited rules for all programs)

---

## Video Editor Specific Tools

### TikTok Shop Affiliate Video
- **Skill:** `/tiktok-shop-affiliate-video` — `001_Architecture/Skills/TikTok-Shop-Affiliate-Video/`
- **Script:** `scripts/analyze_clips.py` — FFmpeg scene detection → Qwen-VL (OpenRouter) → `clip_analysis.md`
- **What it does:** Produces 6 TikTok/YouTube Shorts affiliate videos (9:16) from raw product footage + pre-recorded VO clips. Audio-first: VO drives the cut. 3 visual edits × 2 audio tracks = 6 outputs.
- **API keys:** `OPENROUTER_API_KEY` (vision analysis) + `ELEVENLABS_API_KEY` (transcription) via `source ~/.env-secrets`
- **Trigger:** "create affiliate video", "edit product footage for TikTok", "make shop video"

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

All keys stored in `~/.env-secrets`. When a tool requires a key, it's listed in `TOOLBOX.md` under that tool's section.

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
| `bun` | `/Users/tonymacbook2025/.bun/bin/bun` | JavaScript runtime used by claude-mem worker and hooks |
| `gemini` | `/opt/homebrew/bin/gemini` | Google Gemini CLI for terminal-based AI agent workflows |
| `yt-dlp` | `/Library/Frameworks/Python.framework/Versions/3.13/bin/yt-dlp` | Download videos from YouTube and public sources |
| `python3` | `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3` | Python interpreter for all .py tools |

---

## Python Packages (System-Wide, pip3)

| Package | Version | What It Does |
|---------|---------|-------------|
| `cloudinary` | 1.44.2 | Upload images/video to Cloudinary CDN; returns public HTTPS URLs for AI API parameters |
| `Pillow` | 12.2.0 | Image processing — resize, pixel diff, frame comparison; used by scene detection scripts |

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
