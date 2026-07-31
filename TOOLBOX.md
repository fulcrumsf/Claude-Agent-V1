---
title: "TOOLBOX: Complete Tool & Capability Reference"
type: guideline
domain: architecture
tags: [guideline, architecture, doc]
---

# TOOLBOX: Complete Tool & Capability Reference

**Last updated:** 2026-06-19

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
- **Python Tool:** `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/kie_video_gen.py` — unified API to all kie.ai video models
  - Supports: **Veo 3.1**, **Kling 3.0**, **Wan 2.6**, **Sora 2**
  - Usage: `python3 001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/kie_video_gen.py "[PROMPT]" output.mp4 "veo3"`
- **API Key:** `KIE_API_KEY`
- **Pricing:** 30–70% cheaper than fal.ai for equivalent models
- **When to use:** Always try kie.ai first for video generation

### kie-cli (kie.ai CLI)
- **Package:** `@felores/kie-cli` (npm global)
- **Usage:** `kie-cli --help` — list all available models by category; `kie-cli [category]` to explore
- **API Key:** `KIE_API_KEY`
- **When to use:** Live model discovery on kie.ai without reading the website; pipe into scripts for programmatic model selection

### WaveSpeed CLI
- **Package:** `@wavespeed/cli` (npm global)
- **Usage:** `wavespeed models "[query]"` — keyword search across 986 models; `wavespeed models` — full list
- **API Key:** `WAVESPEED_API_KEY` (fixed from `WAVESPEED_AI_API_KEY` — old name was wrong)
- **When to use:** Find WaveSpeed-specific models (Seedance, Wan, Kling variants) and their per-video flat pricing; only platform with live CLI model search

### Autohand (OpenRouter Agent CLI)
- **Installer:** autohand.ai — OpenRouter-backed CLI automation agent
- **API Key:** `OPENROUTER_API_KEY`
- **When to use:** OpenRouter-backed agent tasks from CLI; fallback for model routing when direct APIs unavailable

### Blotato (Publishing) — MCP server, registered and active
- **What it does:** Publish generated videos to YouTube and social media (Instagram, TikTok, Facebook, LinkedIn, Twitter, Pinterest, Threads, Bluesky)
- **Access:** MCP server (HTTP transport, `https://mcp.blotato.com/mcp`), registered project-scoped for Agent-OS in `~/.claude.json` as of 2026-07-04. Tools available directly as `mcp__blotato__*` in Claude Code — prefer these over any manual API calls.
- **Key tools:** `blotato_list_accounts` (get accountId + platform requirements), `blotato_create_presigned_upload_url` (local file → public URL, required before `create_post` for any local video/image), `blotato_create_post` (publish/schedule), `blotato_get_post_status` (poll after create_post for large media)
- **Known connected YouTube accounts:** NeonParcel (id `25731`), ReimaginedRealms (id `30323`, 18 playlists mapped), Anomalous Wild (id `42514`, displayed as "Anomalos Wild" — a spelling variant, confirmed correct 2026-07-08)
- **Known connected TikTok accounts:** neonparcel (id `27763`), reimaginedrealms (id `33717`). TikTok posts require `privacyLevel` + `disabledComments`/`disabledDuet`/`disabledStitch`/`isBrandedContent`/`isYourBrand`/`isAiGenerated` all present, or `create_post` 400s.
- **TikTok `isDraft: true`** saves to the TikTok app's drafts inbox (confirmed working 2026-07-12) — useful for TikTok Shop Creator videos since Blotato has **no field to attach/tag a TikTok Shop product** (checked the live `blotato_create_post` schema directly — no such field exists on any platform). Product tagging must be done manually in the TikTok app after the draft lands. Blotato's post-status API also has no distinct "draft" status value (only `in-progress → published | scheduled | failed`) — a draft submission still reports back as `"published"`; always have Tony confirm in-app that it actually landed in drafts, don't trust the API status alone for draft posts.
- **`isBrandedContent` ≠ affiliate/commission content.** This flag is specifically for direct brand-paid partnerships with brand-dictated content guidelines — set `false` for TikTok Shop Creator/affiliate videos (commission-based, GMV-tied fees, no brand paying for that specific video/no brand creative direction).
- **Thumbnail constraint:** custom YouTube thumbnails must be ≤2MB JPEG/PNG — compress with ffmpeg first if over (`ffmpeg -i in.png -vf "scale=1920:-1" -q:v 5 out.jpg`)
- **Gotcha:** if `create_post` errors "reconnect your YouTube account" for a custom thumbnail, that's an OAuth scope issue fixed in the Blotato dashboard (not a script/MCP bug) — already-uploaded media URLs don't need re-uploading after reconnect
- **Python integration:** `kie_upload.py` for file uploads before publishing (legacy path — MCP's own presigned-upload flow is now preferred)
- **API Key:** `BLOTATO_API_KEY` (used by the MCP server itself, not needed for direct calls from Claude Code)

---

## Image Generation

### kie.ai (Primary Platform)
- **Python Tool:** `001_Architecture/Tools/Image-Generation/kie_image_gen.py` — Nano Banana 2 and Nano Banana Pro
  - Usage: `python3 001_Architecture/Tools/Image-Generation/kie_image_gen.py "[PROMPT]" output.jpg --model nano-banana-2`
- **Skill:** `/nano-banana-pro-prompts-recommend-skill` — AI recommendations for image prompts

### fal.ai (Fallback)
- **Python Tool:** `001_Architecture/Tools/Image-Generation/image_gen.py` — fallback to Google AI Studio (Gemini 2.5 Flash) or fal.ai
- **API Key:** `FAL.AI_API_KEY`
- **When to use:** Only if kie.ai doesn't have the model you need

---

## Text-to-Speech

### ElevenLabs
- **Python Tool:** `001_Architecture/Tools/Text-To-Speech/audio_tts.py`
  - Generates TTS with word-level timestamps
  - Outputs per-scene MP3 files and `beat_sheet.json`
  - Usage: `python3 001_Architecture/Tools/Text-To-Speech/audio_tts.py <script.md> <output_dir> [--voice <id>]`
- **API Key:** `ELEVENLABS_API_KEY`
- **Output:** Feeds into video beat sheet and Remotion composition

---

## YouTube & Video Research

### yt-dlp (Video Download)
- **Location:** `/Library/Frameworks/Python.framework/Versions/3.13/bin/yt-dlp`
- **What it does:** Download YouTube videos and public videos at 720p
- **Invoked by:** `download-video` skill in Video Editor

### Gemini Video Analysis
- **Python Tool:** `001_Architecture/Tools/AI-Analysis/gemini_video_analysis.py` — analyze video style, camera work, humor, AI-prompt potential
  - Usage: `python3 001_Architecture/Tools/AI-Analysis/gemini_video_analysis.py "<URL>" -o output.md`
- **Skill:** `/analyze-video` — same functionality via skill interface

### Case Study Generator
- **Python Tool:** `001_Architecture/Tools/AI-Analysis/case_study_generator.py` — full automated case study pipeline
  - Fetches YouTube metadata via YouTube Data API
  - Runs Gemini 10-section analysis
  - Downloads video and extracts 3 screenshots
  - Outputs to `references/channels/[channel]/case_studies/`
- **Skill:** `/case-study` — same functionality, triggered by "do a case study" or competitor URL
- **API Keys:** `YOUTUBE_DATA_API_KEY`, `YOUTUBE_ANALYTICS_API_KEY`, `GOOGLE_API_KEY`

---

## Video Editing & Composition

### Video-Use (Agent-Driven Video Editor)
- **Repo:** `001_Architecture/Tools/Video-Generation/Video-Use/`
- **Skill:** `/video-use` — symlinked into `001_Architecture/Skills/Video-Use/`
- **What it does:** Drop raw footage + pre-recorded VO clips in a folder, agent cuts, trims silences, self-evaluates, outputs `final.mp4`. Audio-first: transcript drives cut decisions.
- **Pipeline:** Transcribe (ElevenLabs Scribe) → Pack → LLM Reasons → EDL → Render → Self-Eval
- **API key:** `ELEVENLABS_API_KEY` via `source ~/.env-secrets` (never stored in .env)
- **When to use:** Raw footage → clean cut. Primary engine for the TikTok Shop affiliate video workflow.
- **Wiki:** `000_Wiki/Video-Production/Video-Use-Agent-Editor.md`

### Hyperframes (HTML-Native Video Renderer)
- **CLI:** `hyperframes` — globally installed via npm (v0.6.25)
- **Repo:** `001_Architecture/Tools/Video-Generation/Hyperframes/`
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
- **Skill:** `/remotion-best-practices` — 30+ rules covering animations, audio, assets, 3D, captions, etc. (the "how to code it" reference)
- **Skill:** `/Motion-Graphics` (`001_Architecture/Skills/Motion-Graphics/SKILL.md`, built 2026-07-10) — composition/design-taste companion to remotion-best-practices (the "what good looks like" reference): diagram/callout label placement, non-parallel radial leader lines, materialize-not-pop reveals, spring-overshoot pulse beats, color judgment (content vs. brand chrome), timing/easing guidance, and treatment-style craft notes (Kinetic Typography, Vox Documentary, Kurzgesagt Animated). Defers to the living, production-corrected rule ledger at `002_Content-Creation/Video_Editor/003_Remotion/src/skills/design-rules-learned.md` as ground truth over its own general principles.
- **Use case:** Programmatically compose videos as React components

### Video Stitching
- **Python Tool:** `001_Architecture/Tools/Video-Generation/Generic_Tools/video_stitcher.py` — stitch scenes (video.mp4 + audio.mp3) into final MP4
  - Usage: `python3 001_Architecture/Tools/Video-Generation/Generic_Tools/video_stitcher.py scene_1/ scene_2/ ... -o final.mp4`

### Final Cut Pro XML Export
- **Python Tool:** `001_Architecture/Tools/Remotion/export_fcpxml.py` — export timeline as FCPXML 1.9
  - Usage: `python3 001_Architecture/Tools/Remotion/export_fcpxml.py --video-dir outputs/<project>`
  - Allows importing into Final Cut Pro for further editing

---

## Notion

### Notion MCP Plugin
- **Status:** Installed but DISABLED (can be enabled)
- **What it does:** Full Notion workspace integration — pages, databases, properties
- **Enable:** Turn on in `~/.claude/settings.json` plugins
- **API Key:** `NOTION_API_KEY`

### Notion Bookmark Enrichment
- **Python Tool:** `001_Architecture/Tools/Notion/enrich-notion-bookmarks.py` — autonomous script
  - Processes all 14 bookmark databases
  - Scrapes URLs via Firecrawl
  - Generates AI summaries via Claude
  - Updates Notion descriptions
  - Runs: `source ~/.env-secrets && python3 001_Architecture/Tools/Notion/enrich-notion-bookmarks.py`

---

## Obsidian / Knowledge Vault

### Obsidian MCP
- **Vault Location:** `/Users/tonymacbook2025/Documents/Agent-OS`
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

### Blotato — MCP server, registered and active (see full entry above under Publishing)
- **What it does:** YouTube + social media (Instagram, TikTok, Facebook) publishing
- **Access:** MCP tools (`mcp__blotato__*`) — see "Blotato (Publishing)" entry above for tool list, connected accounts, and gotchas
- **Integration:** Final step in Video Editor production pipeline — Phase 12 of the Reimagined Realms Video Pipeline skill automates this end-to-end

### Meta Graph API
- **What it does:** Facebook/Instagram publishing and analytics
- **API Key:** `META_GRAPH_API_KEY`

---

## Vercel (Deployment)

### Vercel Plugin
- **Status:** Enabled
- **What it does:** Deploy Next.js/full-stack apps, manage environments, domains, analytics
- **Skills lock:** `001_Architecture/Skills/skills-lock.json` (tracks installed Claude Code skills, including `vercel-cli` from `vercel/vercel`)
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

## Tool Manager (Cost Routing & Model Intelligence)

### tm CLI
- **What it does:** Live cost routing and model recommendation for all pipelines. Knows pricing for every API in the toolbox, researches model capabilities via Perplexity, and recommends the cheapest/best option before any pipeline runs.
- **CLI:** `001_Architecture/Tools/Tool-Manager/tm [command]`
- **Commands:**
  - `tm status` — check if pricing cache and model DB are current
  - `tm cost --pipeline "images:15,video:15,tts:3min,music:1track"` — estimate full pipeline cost
  - `tm recommend --type image|video` — best model + backup for a task
  - `tm research-models` — populate model capabilities DB via Perplexity
  - `tm refresh` — scrape all pricing pages (auto-runs monthly via cron)
  - `tm fal-search "<query>" [--pricing] [--limit N]` — search fal.ai model catalog via authenticated Platform API (`https://api.fal.ai/v1/models?q=`); add `--pricing` to fetch per-model pricing inline
- **Data files:**
  - `data/pricing_cache.json` — live pricing for all APIs (OpenAI, kie.ai, ElevenLabs, fal.ai, Firecrawl, etc.)
  - `data/model_capabilities.json` — pros/cons/benchmarks/rankings for all image and video models
- **Skill:** `tool-manager` — MANDATORY AUTO-INVOKE before any pipeline or tool decision
- **Cron:** Monthly refresh on the 1st at 3am
- **Note:** kie.ai pricing page is auth-gated — prices populated via Perplexity research. Run `tm refresh` after logging in manually if needed.

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

## Agent-OS Validation System (Checks & Balances)

Built 2026-06-19. Ensures Claude never declares work done without proof.

### Claude Code Hooks (`~/.claude/hooks/`)
- **`agent-os-build-tracker.js`** — PostToolUse hook. Fires after every Write/Edit/MultiEdit. Detects functional artifacts (.py, .sh, .js, SKILL.md, tool configs, settings.json). Injects `⚠️ VERIFY REQUIRED` into Claude's context immediately. Appends file to build manifest.
- **`agent-os-stop-validator.js`** — Stop hook. REMOVED (Jun 19, 2026) — fired after every turn and banner couldn't be suppressed. Tool-Manager workflow is the replacement guardrail.

### Build Manifest
- Location: `/tmp/agent_os_build_manifest.json` (session-scoped, auto-created)
- Tracks: `unverified` (written, not yet checked) and `verified` (passed validation)
- Stop hook clears block once all items move to verified

### Validation Script
- **File:** `001_Architecture/Scripts/validate_build.py`
- **Usage:** `python3 001_Architecture/Scripts/validate_build.py --files "path1.py,path2/SKILL.md"`
- **Type-aware checks:**
  - `.py` → syntax (`py_compile`) + CLI `--help` smoke test + referenced path existence
  - `SKILL.md` → frontmatter present, `name:` field, name registered in Skill-Index.md
  - `.json` → valid JSON parse
  - `.sh` → executable bit + bash syntax check
  - `.js` → exists and non-empty
- **Data fetch completeness:** `python3 validate_build.py --data-fetch --sources "kie.ai,fal.ai,openai" --got "kie.ai,openai"` — diffs expected vs. resolved, flags missing sources
- When a file passes, it's moved from `unverified` → `verified` in the manifest, unblocking the Stop hook

### Rules This System Enforces
- Never declare a build done without running `validate_build.py` on it
- Multi-source data fetches must report ALL sources (pass + fail with error + fix instructions)
- Stop hook is a hard gate — Claude cannot finish a turn if functional artifacts are unverified

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
- **General mode:** raw footage + pre-recorded VO clips → 3 visual edits × 2 audio tracks (TikTok + YouTube Shorts) = 6 outputs. Audio-first: VO drives the cut.
- **Neon Parcel TikTok Shop Creator mode** (locked in 2026-07-12, validated on Colorsmart Pens): a distinct invocation context within the same skill — 3 genuinely different vertical cuts (different beats/pacing per video, not shared-cut-swapped-audio), no YouTube pairing, output routed to `005_Affiliate_Marketing/Tiktok_Shop_Affiliate/Neon_Parcel_TikTok_Shop_Creator/Videos/NNNN_Product-Slug/`. Full design spec: `001_Architecture/Superpowers/Specs/2026-07-11-Neon-Parcel-Tiktok-Shop-Creator-Pipeline-Design.md`.
- **Scripts** (all in `scripts/`):
  - `analyze_clips.py` — FFmpeg scene-change keyframes → Qwen-VL (OpenRouter) → `clip_analysis.md`. For narration-driven shot matching (validated workflow), also transcribe the VO with ElevenLabs Scribe word-level timestamps first, then run denser frame sampling (every ~4s, not just scene-change) across raw clips to match real footage moments to what's being said — scene-change detection alone is often only 1 frame for long continuous handheld shots. **Qwen-VL hard caps:** max 16 images per OpenRouter call (batch at ≤8 to also stay under the 128K context limit at full frame resolution — downscale frames to ~640px width before sending). **Blind spot confirmed 2026-07-31:** the model cannot reliably detect subtle grime/residue described narratively, and will misread footage of a *now-transparent* cleaned surface as "empty/no subject" — trust the creator's own description of their footage over automated vision when they conflict, after one verification pass.
  - `trim_vo_pauses.py` — shrinks overlong VO pauses to a natural ~0.35s. Always keeps 120ms of real audio on both sides of a cut (no word clipping) and applies a 15ms fade at every join (no clicks/pops) — a naive hard-cut trim produces both failure modes. Run before `normalize_loudness.py` (SKILL.md Step 5a.4, new 2026-07-31).
  - `scaffold_product_folder.py` — per-product folder scaffolder (Edit/, Compliance/{Vision-Scan,Transcript-Scan,Ledger-Scan-Results.md}, Package/)
  - `extract_compliance_sources.py` — pulls real TikTok Seller University URLs embedded in the TOS bundle (never invents URLs)
  - `validate_compliance_ledger.py` — structural validator for `Compliance-Ledger.md`
  - `check_tos_freshness.py` — Firecrawl-based live policy freshness check (14-day/always-escalate cadence). **Known limitation:** Firecrawl currently refuses to scrape `seller-us.tiktok.com` entirely ("we do not support this site") — confirmed not an auth/rate-limit issue. This phase is correctly wired but provides zero real drift-detection value until resolved.
  - `compliance_vision_scan.py` — post-build logo/watermark scan, fails safe to FLAG on ambiguous response. Reliably flags the product's own label/logo (correct behavior — always needs human resolution to distinguish "own product" from real third-party branding).
  - `compliance_transcript_scan.py` — post-build banned-phrase scan (guarantee/cure/medical-outcome language), fails safe to FLAG on empty/failed transcription
  - `normalize_loudness.py` — two-pass EBU R128 loudness normalization (default target -14 LUFS / -1.5 dBTP), run on VO before muxing (SKILL.md Step 5a.5). Added because raw VO measured -34 to -35 LUFS with no normalization step previously.
- **Compliance ledger:** `005_Affiliate_Marketing/Tiktok_Shop_Affiliate/Neon_Parcel_TikTok_Shop_Creator/Compliance-Ledger.md` — 10 citation-backed rules. RULE-008 (disclosure) has a real-world addendum (2026-07-12): TikTok auto-adds a "Creator earns commission" tag when a Shop product link is attached, which serves as the disclosure for affiliate content — do not add `#ad`/`#sponsored` for Neon Parcel TikTok Shop Creator videos with a product link; use ~3 relevant hashtags instead.
- **API keys:** `OPENROUTER_API_KEY` (vision), `ELEVENLABS_API_KEY` (transcription/TTS), `FIRECRAWL_API_KEY` (freshness check) via `source ~/.env-secrets`
- **Trigger:** "create affiliate video", "edit product footage for TikTok", "make shop video"
- **Video output policy:** never commit rendered `.mp4` files from this (or any) pipeline to GitHub — only commit scripts/skill/compliance-doc changes (`.gitignore` already excludes `*.mp4`)

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

### Reimagined Realms Video Pipeline Skill (Global — `001_Architecture/Skills/Reimagined_Realms_Video_Pipeline/`)
- **Invoke:** `/reimagined-realms`
- **Purpose:** Full 10-phase faceless YouTube video pipeline. Replaces Higgsfield MCP — no subscription needed.
- **Workflow:** Channel analysis (Firecrawl) → Story ideation (DAIPBR + 7-part template) → Script → Beat table → Cost estimate (3 combos: GPT Image+Seedance, Nano Banana+Kling, Nano Banana+Veo 3.1) → ElevenLabs voiceover → Beatmap from VO timestamps → Shot list (per-clip image+video prompts) → YouTube package
- **Output:** `Productions/[topic-slug]/` — 8 files: script, beat table, cost estimate, voiceover, timestamps, beatmap, shot list, YouTube package
- **Tools used:** Firecrawl CLI, Tool Manager pricing cache, `001_Architecture/Tools/Text-To-Speech/audio_tts.py`, kie.ai (KIE_API_KEY), ElevenLabs (ELEVENLABS_API_KEY)
- **Voice ID (Reimagined Realms):** `raMcNf2S8wCmuaBcyI6E` (ElevenLabs multilingual v2)
- **Note:** `~/.claude/skills/` is a symlink to `001_Architecture/Skills/` — skill is global across Claude, Codex, and Gemini

### Reimagined Realms — Batch Generation + Assembly Scripts (`001_Architecture/Tools/Video-Generation/Channels/Reimagined_Realms/`)
- **batch_generate_images.py** — Generate all clip images via GPT Image 2 on kie.ai
  - Usage: `python3 batch_generate_images.py <production_folder> [--clips C20 C21] [--overwrite]`
  - Reads: `Data/Beatmap.json` + `Production/Shot_List.md` (Image prompts)
  - Saves: `Images/C01_0.0s-3.8s.png ...`; skips existing — safe to re-run
  - `--clips`: generate subset only; `--overwrite`: regenerate even if file exists
- **batch_generate_videos.py** — Generate all clip videos via Seedance 1.5/2.0 on kie.ai (image-to-video)
  - Usage: `python3 batch_generate_videos.py <production_folder> [--clips C20] [--overwrite] [--audio]`
  - Reads: `Images/*.png` + `Production/Shot_List.md` (Video prompts) + `Data/Beatmap.json`
  - Uploads images to Cloudinary → submits to kie.ai → polls → saves `Video_Clips/C01_0.0s-3.8s.mp4 ...`
  - Model routing: Seedance 1.5 Pro (≤12s generate) / Seedance 2.0 (>12s); hard cap 8s final per clip
  - Keys required: `KIE_API_KEY`, `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_Key`, `CLOUDINARY_API_Secret`
- **assemble.py** — Universal assembly pipeline (trim → concat → narration → Suno → grade → caption)
  - Usage: `python3 assemble.py <production_folder> [--phase N] [--stop-phase N] [--overwrite] [--clips C20,C21] [--skip-suno]`
  - Reads: `Production/assemble_config.json` (suno_prompt, suno_tags, caption_line1, caption_line2)
  - Reads: `Data/Beatmap.json`, `Video_Clips/`, `Narration_Audio/`
  - Hard cap: 8s max final clip duration (enforced at trim phase regardless of beatmap value)
  - Suno endpoint: `https://api.kie.ai/api/v1/generate` — requires `callBackUrl` field
  - Output: `Assembly/raw_video.mp4`, `Assembly/narration.mp3`, `Assembly/music.mp3`, `Assembly/final.mp4`

### Reimagined Realms — Audio Pipeline (`001_Architecture/Tools/Audio/`)
- **compose_audio.py** — Vision-based per-scene audio composer
  - Usage: `python3 compose_audio.py <production_folder> [--reanalyze] [--dry-run]`
  - Reads: `Assembly/Frames/` (1fps frames) + `gemini_scene_analysis.md` + `Data/Beatmap.json`
  - Outputs: `Data/audio_briefs.json`, `Data/per_scene_stem_map.json`
- **generate_stems.py** — Generate per-scene SFX clips via ElevenLabs
  - Usage: `python3 generate_stems.py <production_folder> [--stems-file Data/per_scene_stem_map.json] [--stems c20 c21] [--overwrite]`
- **analyze_stems.py** — LUFS measurement and gain correction per stem
  - Usage: `python3 analyze_stems.py <production_folder> [--stems-file Data/per_scene_stem_map.json]`
  - Writes corrected `volume`, `measured_lufs`, `gain_db` back to stem map JSON
- **mix_stems.py** — Mix all stems onto video timeline with S-curve (hsin) crossfades
  - Usage: `python3 mix_stems.py <production_folder> [--stems-file Data/per_scene_stem_map.json] [--narration Assembly/narration.mp3]`
  - Output: `Assembly/stems_mix.mp3`; optionally `Assembly/stems_narration_mix.mp3`
- **render_video.py** — Versioned renderer — keeps all audio tracks separate, bakes into MP4
  - Usage: `python3 render_video.py <production_folder> --stems Assembly/stems_mix.mp3 --narration Assembly/narration.mp3 [--music Assembly/music.mp3] --stems-vol 0.88 --narration-vol 3.09 --music-vol 0.12 --duck --note "description"`
  - Locked formula: stems vol=0.88 (-23 LUFS), narration vol=3.09 (-14 LUFS), sidechain duck threshold=0.015 ratio=4 attack=150 release=800
  - Each version saved to `Assembly/V1/`, `Assembly/V2/` ... with independent track copies + render_notes.md
  - Updates `Assembly/RENDER_LOG.md`

### Anomalous Wild — Batch Generation Scripts (`001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/` + `Generic_Tools/`)

Full history/status write-up: [[000_Wiki/Video-Production/Anomalous-Wild-Pipeline-Scripts]]. Anomalous Wild is the *first* video pipeline ever built in this workspace (predates Reimagined Realms), so its early tooling is more fragmented — several scripts do overlapping jobs from different eras. **A unifying orchestrator skill is now built** (2026-07-07/08): `001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/SKILL.md` (invoke via `/anomalous-wild`), designed at `DESIGN.md` + `PLAN.md`. See the next section for the new pipeline's own scripts.

- **pipeline_supervisor.py** (`Channels/Anomalous_Wild/`) — ✅ **ACTIVE / preferred generation script.** Batch clip generator with real error-code classification (FATAL/CREDITS/SKIP/RATE/WAIT/RETRY/UNKNOWN), automatic retries, macOS notifications, auto-preloops after each successful clip.
  - Usage: `python3 pipeline_supervisor.py` (run from `002_Content-Creation/Video_Editor/`) or `--status`
  - Reads: `Production/new_clips_prompts.json` (per-clip `output_folder`, now `Video_Clips/` — files keyed by `{scene_id}.mp4`, not a fixed `video.mp4` name)
  - Kept in the new pipeline design as-is (Task list: "✅ Reused as-is")
- **run_new_clips_batch.py** (`Generic_Tools/`) — ⚠️ **SUPERSEDED, not deleted.** Simpler batch generator, only ever used for Bioluminescence Weapon despite living in "Generic_Tools." Does the same job as `pipeline_supervisor.py` but without the retry/error-handling sophistication. Its one distinguishing feature — auto-appending a scientific no-text negative prompt for `is_diagram: true` image entries (added after the Video 001 Report Card caught garbled diagram text) — didn't reliably work, since negative prompts alone don't stop image models from occasionally rendering text anyway. That idea carries forward into the new pipeline's Scientific Diagram sub-pipeline (research reference → generate clean illustration → vision-verify → label in Remotion), which is the actual fix. Left in place, unused going forward once the new sub-pipeline is built.
- **preloop_new_clips.py** (`Generic_Tools/`) — post-processes freshly generated clips into looped versions matching narration duration. Called by `pipeline_orchestrator.sh`.
- **preloop_videos.sh** (`Channels/Anomalous_Wild/`) — same job as above but for the original 12 hand-picked hero clips (hardcoded durations). Needs bash 4+ for `declare -A`; the system bash 3.2 couldn't run it. Fixed 2026-07-07 via `brew install bash` (now 5.3.15, ahead of system bash in PATH — plain `bash` picks it up automatically, no script changes needed). Verified working end-to-end.
- **pipeline_orchestrator.sh** (`Channels/Anomalous_Wild/`) — 6-stage wrapper chaining `run_new_clips_batch.py` → `preloop_new_clips.py` → `preloop_videos.sh` → `check_pipeline_status.py`. Fixed 2026-07-07 (was calling a `004_Tools/` path that stopped existing after a June reorg — pre-existing breakage, not caused by that day's folder retrofit).
- **check_pipeline_status.py** (`Channels/Anomalous_Wild/`) — read-only progress report: which clips/images are done vs. pending.
- **BioluminescenceDoc.tsx** (Remotion, `003_Remotion/src/remotion/video-components/`) — the actual Remotion composition that assembles Bioluminescence Weapon. One-off, hardcoded to that video's scenes/durations — not a reusable template. A reference copy lives at `Productions/0001_Bioluminescence_Weapon/Remotion/` for archival purposes; the live version stays in `003_Remotion` untouched.
- **AnomalousWildEndCard.tsx** (Remotion) — channel-wide end card. In practice, the pipeline just appends the pre-rendered `end_card_v3.mp4` via ffmpeg (locked per DESIGN.md) rather than re-rendering this per video. A reference copy lives at `Brand_Assets/End_Card/` alongside the mp4 files; still registered live in `Root.tsx` too.

### Anomalous Wild Pipeline — New Orchestrator (built 2026-07-07/08, `/anomalous-wild`)

Built via the `superpowers:subagent-driven-development` workflow, one task per script, each with an independent code-review pass (several fix rounds), plus a final whole-branch review that caught 2 cross-cutting integration bugs the per-task reviews couldn't see. Full task history and every review finding: `.superpowers/sdd/progress.md` (session-scoped scratch ledger, not durable — see wiki for the durable write-up).

- **build_motion_graphics_profile.py** + **data/motion_graphics_capabilities.json** (`001_Architecture/Tools/Tool-Manager/`) — Research-backed capability profile for Remotion / video-use / Hyperframes / Manim, every entry cites a real source (skill doc path or dated session precedent). Consulted by Tool-Manager when the Anomalous Wild orchestrator needs to route a beat's visual need to a tool — never a hardcoded lookup.
- **generate_narration_with_timestamps.py** (`Channels/Anomalous_Wild/`) — thin wrapper around the existing `generate_voiceover_with_timestamps()` (`Tools/Text-To-Speech/audio_tts.py`). Reads `Scripts/Narration.md` (`## scene_id` sections), writes `Narration_Audio/<scene_id>.mp3` + `_beat_sheet.json` (word-level timestamps) per scene.
- **build_beat_table.py** (`Channels/Anomalous_Wild/`) — reads `Narration_Audio/*_beat_sheet.json` + `Production/Scene_Routing.json`, writes `Production/Beat_Table.json`. Locks in `max_clip_s: 8.0` for `live_footage` beats, `max_static_s: 5.0` for diagram beats (no static frame >3-5s rule).
- **diagram_research_and_illustrate.py** (`Channels/Anomalous_Wild/`) — Scientific Diagram sub-pipeline steps 1-2: searches Openverse for a real reference image, then generates a clean no-text illustration via kie.ai GPT-Image-2 (`gpt-image-2-text-to-image`) with an explicit no-text/no-label negative prompt. This is the actual fix for the garbled-diagram-text problem from the Bioluminescence Weapon video's anglerfish diagram.
- **detect_label_coordinates.py** (`Channels/Anomalous_Wild/`) — Scientific Diagram sub-pipeline step 3: Gemini vision pass over the *actual* generated illustration, returns real `{feature, x_pct, y_pct, confidence}` coordinates. Structurally strips any coordinate attached to a `not_found` entry (never trusts the model to have omitted it) — the "never guess a label position" rule is code-enforced, not just a prompt instruction.
- **DiagramLabels.tsx** (Remotion, `003_Remotion/src/remotion/video-components/`) — Scientific Diagram sub-pipeline step 4: places labels/callout lines at the detected coordinates, staggered fade-in. Registered in `Root.tsx` via a Zod `schema=` prop (`diagramLabelsSchema`, matching the existing `AIVideo`/`aiVideoSchema` pattern in the same file — not a type-erasure cast). `x_pct`/`y_pct` are optional in the schema specifically so a `not_found` label (no coordinates) doesn't crash the composition.
- **generate_youtube_package.py** (`Channels/Anomalous_Wild/`) — adapts Reimagined Realms' title/description/thumbnail formulas to Anomalous Wild's science/nature framing. Generates 3 curiosity-gap titles (length-clamped), a search-intent description, and **actually generates and downloads 3 real thumbnail PNGs** via kie.ai (mood/palette variations), not just prompts.
- **upload_to_blotato.md** (`Channels/Anomalous_Wild/`) — Blotato upload procedure doc mirroring RR's Phase 12 locked defaults. Confirmed Blotato YouTube `accountId: 42514` (displayed there as "Anomalos Wild," a spelling variant — confirmed correct by Tony 2026-07-08, not just inferred).
- **scaffold_new_production.py** (`Channels/Anomalous_Wild/`) — going-forward folder scaffolder: creates the 8 typed folders (matching Reimagined Realms' pattern) and hard-fails if the locked `end_card_v3.mp4` (`Brand_Assets/End_Card/`) is missing.
- **Anomalous_Wild_Video_Pipeline/SKILL.md** (`001_Architecture/Skills/`) — the orchestrator itself. Invoke via `/anomalous-wild`. 10 phases, mirrors Reimagined Realms' structure, explicit pause points (topic selection, live-footage cost estimate, first-clip quality check, title/thumbnail/privacy). Core principle: every beat's visual tool is chosen live via Tool-Manager, never hardcoded.

**Known cross-cutting bugs caught only by the final whole-branch review (both fixed):** (1) `detect_label_coordinates.py`'s `not_found` coordinate-stripping was rejected by `DiagramLabels.tsx`'s original required-field Zod schema — would have crashed diagram assembly exactly when the "never guess" safety path triggered; fixed by making `x_pct`/`y_pct` optional + a `hasCoordinates()` type guard. (2) The 3-5s no-static-frame rule was recorded in `Beat_Table.json` but nothing actually enforced it; fixed by adding a mandatory per-beat static-hold check to the orchestrator's Phase 7 (Assembly).

**Known pre-existing gaps flagged during this build, not yet resolved:** no locked ElevenLabs voice ID for Anomalous Wild (RR has one hardcoded, AW doesn't — orchestrator asks Tony/Tool-Manager at runtime); `pipeline_supervisor.py` expects a `Production/new_clips_prompts.json` manifest that no script yet auto-builds from the new `Shot_List.md` format (orchestrator treats this as an inline glue step).

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
| `kie-cli` | npm global (`@felores/kie-cli`) | Live kie.ai model discovery by category — needs `KIE_API_KEY` |
| `wavespeed` | npm global (`@wavespeed/cli`) | Search 986 WaveSpeed models by keyword; per-video pricing — needs `WAVESPEED_API_KEY` |

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
