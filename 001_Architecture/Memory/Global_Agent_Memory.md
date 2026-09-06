---
title: "Global Agent Memory"
type: memory
category: architecture
tags:
  - global-memory
  - agents
  - workflow
created: 2026-04-30
source: local
---

# Global Agent Memory

Durable cross-agent memory for this workspace. Claude Code, Codex, Antigravity, Gemini CLI, and any OpenAI-compatible agent should treat this file as shared memory for stable preferences, project decisions, recurring corrections, important tool paths, and workflow rules that should survive across days.

This is not a transcript. Keep entries concise, reusable, and operational.

Do not load this file by default once it grows large. Agents should always read `Core_Memory.md` and `Memory_Index.md`, then use `claude-mem` or targeted file reads to retrieve relevant memory.

## Memory Entries

### 2026-09-04 — Recommendation Requests Require Approval Before Acting

When Tony asks for a recommendation, suggestion, options, or where something should be saved, agents must provide the recommendation and wait for Tony's reply before creating directories, scaffolding, files, or moving anything. Do not interpret "give me a suggestion" as permission to implement. This is a cross-agent rule for Claude Code, Codex, Gemini, and other Agent-OS agents.

### 2026-09-04 — Codex Has an Agent-OS Hardening Skill

Codex should use `001_Architecture/Skills/codex-agent-os-hardening/SKILL.md` whenever operating in Agent-OS. The skill mirrors Claude Code's Agent-OS operating discipline: read the core manuals and maps, check skills/tools first, respect recommendation approval boundaries, preserve files, update feedback/logs/memory, and close sessions cleanly.

### 2026-09-04 — Agent-OS Onboarding Priority

When getting oriented in Agent-OS, prioritize the numbered top-level folders (`NNN_...`) as the main operating departments. Tony's hierarchy is: `001_Architecture` first, `002_Content-Creation` second, `007_Resource_Library` third. `000_Ingest` can usually be skipped unless the task is specifically about ingesting or organizing raw intake.

### 2026-04-30 — This Workspace Is the Whole Business OS

Tony treats `/Users/tonymacbook2025/Documents/Agent-OS/` as one project folder for the entire business. All agents should assume this workspace contains business operations, content creation, e-commerce, app development, game development, tools, logs, memory, and resource libraries. Memory should be global across this workspace unless it is clearly department-specific.

### 2026-04-30 — Shared Memory Must Work Across Agents

Tony wants Claude Code, Codex, and other agents to share durable memory through workspace files. Agents should read `001_Architecture/Memory/`, `001_Architecture/Logs/`, `001_Architecture/Feedback_Loop/`, and `001_Architecture/Self_Learning_Loop/` before asking repeated context questions. Important durable facts belong in this global memory file.

### 2026-04-30 — Mirror Claude Memory Protocol for Codex

Tony wants Codex to maintain memory similarly to Claude Code. `AGENTS.md` now instructs Codex to read and write session logs, feedback logs, self-review notes, and workspace-local memory. Codex should treat workspace files as the durable memory layer and should update them automatically when Tony gives feedback, reveals preferences, validates an approach, or asks to close/save a session.

### 2026-04-30 — System Map Is Mandatory Context

Tony expects agents to know the System Map location: `001_Architecture/Install_Maps/System-Map.md`. Agent instructions now say to read both the Workspace Map and System Map before exploring or asking for context.

### 2026-04-30 — Use Claude-Mem for Relevant Memory Injection

Tony wants memory to be relevant-injected rather than loaded as one large markdown file. `claude-mem` 12.4.9 is installed for Claude Code and Gemini CLI, the worker runs on port `37701`, and Codex has the `thedotmack` marketplace registered from the local claude-mem checkout. Agents should use `claude-mem` for dynamic memory retrieval and keep markdown memory small, curated, and routed through `Core_Memory.md` plus `Memory_Index.md`.

### 2026-05-01 — Preserve Shift+Enter for Multiline Agent Prompts

Tony prefers `Shift+Enter` as the standard command for adding a new line when talking to terminal-based agents. When an IDE terminal collapses `Shift+Enter` into plain `Enter`, agents should look for a settings/keybinding fix rather than asking Tony to learn a different shortcut.

### 2026-05-01 — Numbered Workspace Folders Are Top-Level Departments

Tony treats folders named with a three-digit prefix and underscore, such as `001_Architecture`, as top-level workspace departments. In Antigravity Explorer, these should be visually distinct with pastel folder icons. A local Antigravity icon theme was added at `~/.antigravity/extensions/tony.numbered-folder-pastels-1.0.0/` and enabled with `workbench.iconTheme = "tony-numbered-folder-pastels"`.

### 2026-05-01 — Antigravity Local Extensions Need a Packaged VSIX

When installing a local Antigravity extension, package it as a `.vsix` with `extension/package.json` inside the archive and install it with the Antigravity CLI. Antigravity registers installed extensions in `~/.antigravity/extensions/extensions.json`; a raw copied folder is not enough for a reliable install.

### 2026-05-01 — Explorer Row Colors Need CSS Injection, Not Just an Icon Theme

If Tony wants the entire Explorer row background colored per folder in Antigravity, a file icon theme is not enough. Use a CSS injection extension such as `be5invis.vscode-custom-css` and point it at a workspace stylesheet that targets the Explorer tree rows.

### 2026-05-01 — Ingest Skill Now Handles Media and Subfolders

The vault ingest pipeline (SKILL.md, AGENTS.md, GEMINI.md) was upgraded with:
- **Subfolder recursion on by default** — recurse into all `000_Ingest/` subfolders unless told otherwise
- **Images** → `007_Resource_Library/Obsidian_Attachments/Visual_Assets/` + Asset Note in `007_Resource_Library/Asset_Notes/`
- **PDFs** → `007_Resource_Library/Docs/` — no companion file (Obsidian native PDF viewer)
- **Word docs (.docx)** → `007_Resource_Library/Docs/` + Asset Note in `007_Resource_Library/Asset_Notes/`
- **Asset Notes** named identically to the media file (same kebab-case stem, `.md` extension)
- **Notion exports** — skip top-level database container `.md` files; ingest individual record files normally

### 2026-05-01 — Lookup-First Gate for Vision Calls

Before calling any vision API (rename script, Gemini vision, Claude vision) on images or binary files during ingest, ALWAYS run:
```bash
python 001_Architecture/Scripts/check_vision_needed.py "/path/to/images"
```
This checks Asset Note quality. Files with real descriptions are skipped. Only files with filler descriptions or no note proceed to vision. Filler patterns: "likely a saved reference", "general visual reference", description < 60 chars, no Asset Note. Prevents duplicate API spend on already-cataloged files.

### 2026-05-01 — Asset Note Quality Standard

A proper Asset Note `ai_description` must be specific and observable: platform (TikTok, Instagram, GitHub), specific content visible (tool name, dates, prices, data), and business relevance. Generic descriptions are failures and will be flagged by `check_vision_needed.py` for re-processing.

### 2026-05-01 — Three-Brain Conservation Mode

When Claude usage quota is high, activate Conservation Mode: Codex becomes the primary brain, Claude only handles synthesis. Triggers: Tony says "usage limit", "conservation mode", "save tokens" etc. (reactive) OR 2+ of these in a session: 15+ tool calls, 5+ files written, 3+ major task cycles, 1 large build (proactive). Exit with "full mode" or "back to normal". Documented in `~/.claude/skills/three-brain/SKILL.md`.

### 2026-05-01 — rename_screenshots.py Is Canonical Ingest Step 1.5

`001_Architecture/Scripts/rename_screenshots.py` uses Gemini 2.5 Flash vision to rename image files to descriptive kebab-case names. Accepts a directory as CLI arg; defaults to `000_Ingest/Process Screenshots/Rename/`. The ingest skill Step 1.5 calls this script. Requires `GEMINI_API_KEY` in environment. Duplicate removed from `000_Ingest/`.

### 2026-05-03 — Screenshot Renaming Vision Order

Tony wants screenshot renaming to use Gemini vision first, then OpenAI vision as fallback. OCR is not the default path and should only be used if Tony explicitly requests OCR or a dedicated OCR workflow.

### 2026-05-03 — Single Shared Secrets File (HARD RULE — ALL AGENTS)

`~/.env-secrets` is the ONE AND ONLY place any API key ever lives. This applies to Claude Code, Codex, Gemini CLI, VS Code, and every other agent or tool operating in Agent-OS.

**Hard rules:**
- Never hardcode a live API key in any file — not `.env`, not `.json`, not `.yaml`, not `.toml`, not shell scripts, nowhere
- Never reference `~/.mcp-secrets.env` — it is stale and does not exist
- Config files always use placeholder references like `${KEY_NAME}` — never real values
- If a tool needs a key, it reads it from the environment after `source ~/.env-secrets` has been run via `~/.agent-bootstrap.sh`
- Any agent that finds a hardcoded key in a file must replace it with a placeholder immediately and flag it to Tony

### 2026-05-03 — Shared Agent Bootstrap Draft

Tony wants a single shared bootstrap for Agent-OS that can load `~/.env-secrets`, detect terminal/runtime context where possible, and preserve native subscription auth for Claude Code / Codex / Gemini CLI runs. Obsidian terminal is part of the shell detection set.

### 2026-05-03 — Zshrc Sources Shared Bootstrap

Tony’s `~/.zshrc` now sources `~/.agent-bootstrap.sh` and has a timestamped backup in `~/.zshrc-backups/`. The bootstrap change was made non-destructively.

### 2026-05-03 — Runtime Detection Rule

Terminal CLI names map directly to runtimes: `claude` → Claude Code CLI, `codex` → Codex CLI, `gemini` → Gemini CLI, and `agy` → Antigravity CLI. Only ambiguous generic fallback paths should prompt the user for the current runtime.

### 2026-05-03 — Bootstrap Symlink Required

The shared bootstrap lives canonically in `001_Architecture/Scripts/agent-bootstrap.sh` but is exposed to shells via a non-destructive home symlink at `~/.agent-bootstrap.sh` so `.zshrc` can source it reliably.

### 2026-05-03 — UGC Recruitment Ads Route to Research

Screenshots like `UGCcreator.com` that show UGC creator recruitment or agency outreach offers should route to `Research`, not `Models`, when the note is being saved as a market or offer reference.

### 2026-05-03 — Future Context Estimator Idea

Tony may want a future local utility to estimate startup/context usage from injected files, hooks, and memory across Claude Code, Codex, and Gemini sessions.

### 2026-05-11 — Skill Registry Is the Cross-Agent Discovery Layer

The canonical shared skill index is `001_Architecture/Skills/Skill-Index.md`, generated from every `SKILL.md` in the skills tree by `001_Architecture/Scripts/sync_skill_index.py`. Claude Code and Gemini hooks now regenerate it automatically after skill edits so all agents can discover the same skills from one registry.

### 2026-05-13 — Ingest Should Synthesize, Not Mirror

When Tony asks for ingest follow-up, prefer a compact synthesis pass in `000_Wiki/` over one wiki page per source file. Group related source notes into fewer durable reference pages when they share a common theme, and fold overlapping guides into the existing synthesis instead of duplicating them.

### 2026-05-03 — Image Notes Live In Category Folders

For ingested images, the raw file stays in `007_Resource_Library/Obsidian_Attachments/Visual_Assets/` and the note file is created directly in the matching category folder in `007_Resource_Library/`. Do not create a separate `Asset_Notes/` directory unless Tony explicitly asks for one.

### 2026-05-03 — Video Ingest Direct Path

Tony prefers the stock `process_video_ingest.py` to be run directly on the source clip. Wrapper-based pre-renaming can make recovery harder if a batch aborts partway through; normalize the resulting package stem afterward if needed.

### 2026-05-03 — Wrapper-Based Video Preprocessing Is Risky

An earlier wrapper-based video pass left `003_Coke-Edit.mp4` and `IMG_9650.MOV` unrecoverable from the workspace. Avoid source-mutating wrappers for ingest unless there is a strong reason to use them.

### 2026-05-03 — Never Trash Source Files

Tony does not want source files thrown in the trash during normal workspace operations. Preserve originals until the routing decision is explicit; only move into existing destinations or ask Tony before any destructive cleanup.

### 2026-05-03 — Screenshot Vision Must Stay Grounded

If a screenshot note names entities that do not visibly appear in the image, treat it as a vision hallucination or mismatch, not a routing success. Re-run or mark undetermined unless the visible text and layout actually support the title and category.

### 2026-05-01 — Antigravity Custom CSS Needed an Inline Workbench Patch

Installing `be5invis.vscode-custom-css` and adding `vscode_custom_css.imports` was not enough on its own. Antigravity loaded the Explorer row colors only after patching `/Applications/Antigravity.app/Contents/Resources/app/out/vs/code/electron-browser/workbench/workbench.html` to inline the stylesheet.

### 2026-05-01 — Suppressing Antigravity Corrupt Installation Warning

When modifying Antigravity's core files (like `workbench.html`) for UI customization, the application will show a "corrupt installation" warning on startup because the file checksums no longer match `product.json`. To fix this permanently without dismissing the notification every time, generate the SHA256 base64 hash of the modified file (minus the trailing '=') and replace the old hash in `/Applications/Antigravity.app/Contents/Resources/app/product.json` under the `checksums` object.

### 2026-05-01 — update_asset_notes_vision.py
`001_Architecture/Scripts/update_asset_notes_vision.py` scans resource library folders for images whose Asset Notes have filler descriptions. It uses Gemini vision with a text-extraction-focused prompt to rewrite the `ai_description` and `## AI Analysis` sections in place.

### 2026-05-01 — API Cost Mitigation via Multi-Agent Execution
When performing large batch operations (e.g., passing 500 images to a vision API), do not execute the loop inside Claude Code, as it quickly consumes the Anthropic API org limit. Instead, use Claude Code to author the script, but execute the script using the Gemini CLI (or directly via a standard terminal) to leverage cheaper/unlimited Gemini Flash API endpoints.

### 2026-05-02 — The "Bookmarks" Antipattern
"Bookmark" is a medium, not a category. Ingested web clippings must be categorized and routed based on their actual topic (e.g., `Tools`, `Tutorials`, `Investments`). The `Bookmarks` folder was deprecated and removed.

### 2026-05-02 — Directory.md is the Routing Glossary
Agents MUST read `007_Resource_Library/Directory.md` before routing ingested files. This file defines exactly what goes where. If a file doesn't fit existing definitions, agents must ask Tony for permission before creating a new top-level directory. Do not guess.

### 2026-05-02 — Video Knowledge Packages
When ingesting `.mp4` or `.mov` files, they do not go into flat folders. They must be placed in a dedicated package folder (e.g., `007_Resource_Library/Videos/[Name]/`). The script must place the video inside and create two empty scaffold files next to it: `[Name]-Transcript.md` and `[Name]-Tutorial.md`.

### 2026-05-02 — Image Ingest Keeps Raw Files in Visual Assets
For image ingest, the raw image stays in `007_Resource_Library/Obsidian_Attachments/Visual_Assets/`. The routed object is the corresponding note, which moves into the correct category subfolder. If no category folder exists, queue the item for the end of the batch and ask Tony before creating a new directory or assigning a new category.

### 2026-05-02 — Canonical Routing Categories for Image-Derived Notes
Use the existing Resource Library destinations as the routing categories for image-derived notes: `Tools`, `Tutorials`, `Prompts`, `Docs`, `Investments`, `Models`, `Videos`, and `Archive`. Classify by actual content first, then route the note into the matching existing folder. Ambiguous items should stay queued until the end of the batch and be reviewed with Tony rather than guessed.

### 2026-05-02 — Image Routing Tie-Break Rules
If a screenshot is primarily reusable prompt text, route it to `Prompts`. If it is primarily a walkthrough or tutorial video reference, route it to `Tutorials`. If it primarily shows a software product, SaaS, GitHub repo, or identifiable tool URL/caption, route it to `Tools`. `Docs` is primarily for PDFs and text reference, with markdown reserved only for rare API/configuration cases like curl or HTTP examples.

### 2026-05-02 — Workflows and Project Ideas Are Now First-Class Resource Library Routes
Tony added `007_Resource_Library/Workflows/` for process maps, flowcharts, and workflow references, and `007_Resource_Library/Project_Ideas/` for raw project concepts and future build seeds. `Workflow.md` should route to `Workflows/` instead of `Tools/`, and tutorial-style YouTube/TikTok search screenshots like `Videos.md` should route to `Tutorials/`.

### 2026-05-02 — Docs Is Strict, Workflows Are Visual, and Project Ideas Are Written Seeds
Tony clarified that `Workflows` means visual process diagrams only: flowcharts, mind maps, and other visual explanations of a workflow. `Project_Ideas` is for mostly `.md` notes describing future business projects across YouTube, Etsy, Printful, Printify, affiliate marketing, and similar ventures. `Docs` should remain limited to actual documentation artifacts and not become a catch-all for inspiration screenshots or bookmarks.

### 2026-05-02 — Design Inspiration and Personal Are Now First-Class Routes
Tony created `007_Resource_Library/Design_Inspiration/` for t-shirt designs, website inspiration, aesthetic Instagram accounts, and image-only visual references. Tony created `007_Resource_Library/Personal/` for non-business references such as band tour flyers and other personal-interest captures. `Real-Life-Lore-YOUTUBE.md` should route to `Design_Inspiration/`, and `Lofi.md` should route to `Tutorials/`.
Tony also treats product-research captures like `Google-Inulin-Products.md` as `Personal/` when they are not clearly business documentation or investment research.

### 2026-05-03 — Research Is a First-Class Routing Category
Tony created `007_Resource_Library/Research/` for benchmark captures, channel studies, market/product research, comparisons, and analysis notes. `Virality-Structures-2.md`, `Meow-Toptop-Bee.md`, and `Wellness-Doctor-Health.md` all route to `Research/` because they are TikTok/channel examples being studied, not models or generic docs.

### 2026-05-03 — Video Packages Must Be Renamed Descriptively
Tony does not want opaque hash-style video package names. Video ingest should rename the MP4, folder, transcript scaffold, and tutorial scaffold to a shared descriptive stem using `Title-Case-With-Dashes`, with acronyms preserved in uppercase such as `AI-Epoxy-Time-Lapse-Claude-Code-Skill`.

### 2026-05-03 — Notion Export Processor Exists
`001_Architecture/Scripts/process_notion_edit.py` is the canonical offline batch processor for large mixed Notion exports when the folder contains md, text, JSON, CSV, images, PDFs, spreadsheets, and Pages files. It routes files into the current Resource Library categories and creates markdown notes for images and text exports without requiring live vision access.

### 2026-05-06 — ChatGPT Profile Layer Exists
Tony's ChatGPT export distillation now lives in `001_Architecture/Memory/ChatGPT_Profile/` as one note per approved theme. Treat it as a durable second-brain profile layer for Tony's recurring thinking patterns, not as a raw archive.

### 2026-05-06 — ChatGPT History Should Be Human-Readable by Theme
Tony wants the ChatGPT export reorganized into theme folders under `007_Resource_Library/OpenAI_History/`, with one readable conversation note per conversation and image references linked from those notes. The canonical image assets now live under `007_Resource_Library/Obsidian_Attachments/OpenAI_Images/Inputs` and `Outputs`, while the generated image notes stay directly in `007_Resource_Library/Research/OpenAI_Images/`. Filenames should stay descriptive with only a short ID suffix at the end.

### 2026-05-06 — Input Images Must Be Linked From Conversation Notes
User-uploaded ChatGPT images should be copied into `007_Resource_Library/Obsidian_Attachments/OpenAI_Images/Inputs/` and referenced directly from the matching conversation note so the note can lead back to the exact uploaded asset before any future renaming pass. Generated images stay in `Outputs/`.

### 2026-05-06 — ChatGPT Original Image Staging Lives in Ingested
The original copied ChatGPT image files that were staged from `OpenAI_History` now live under `007_Resource_Library/Obsidian_Attachments/OpenAI_Images/ingested/` so the raw originals remain grouped separately from the Research copies.

### 2026-05-06 — Duplicate OpenAI Outputs Are Quarantined First
When the OpenAI output image set contains true binary duplicates, move the extras into `007_Resource_Library/Obsidian_Attachments/OpenAI_Images/Outputs/quarantine-delete-later/` instead of deleting them immediately. Leave one canonical file per exact hash in `Outputs/`.

### 2026-05-06 — Duplicate OpenAI Inputs Are Quarantined First
When the OpenAI input image set contains true binary duplicates, move the extras into `007_Resource_Library/Obsidian_Attachments/OpenAI_Images/Inputs/quarantine-delete-later/` instead of deleting them immediately. Leave one canonical file per exact hash in `Inputs/`.

Tony wants raw OpenAI History images mirrored non-destructively into `007_Resource_Library/OpenAI_History/Image-Review/` as a browsable hard-link folder when he needs to inspect them in bulk. Future OpenAI History scans should ignore `Image-Review/` so the mirror folder is not treated as new source data.

Tony also wants a labeled inventory pass for raw OpenAI History images that groups files into backtrackable boxes such as confirmed ingested inputs, confirmed ingested outputs, generated outputs, user-upload-like files, documents, exact duplicates, and needs-review, with a manifest capturing the source path and classification reason. Treat that inventory as the preferred inspection layer over a raw mirror.

When checking uncategorized conversation notes against image files, treat the canonical `Obsidian_Attachments/OpenAI_Images/Inputs` and `Outputs` folders as the source of truth; filename-only matching against `OpenAI_history/Needs Ingestion` is not sufficient and may yield zero safe moves even when the notes already embed valid vault links.

Tony wants obvious N8n workflow screenshots in `OpenAI_history/Needs Ingestion` grouped automatically by filename into `N8n-Screenshots` so they can be bulk-reviewed or deleted later without spending vision on every file.

Tony also wants repeated filename words to drive automatic grouping of raw images in `OpenAI_history/Needs Ingestion` so obvious clusters like screenshots, typography, framing, and generated images can be sorted without opening each file manually.

### 2026-05-06 — OpenAI gpt-4o-mini Is the Default Vision Model for ChatGPT Image Ingest
Tony chose `gpt-4o-mini` as the default image-understanding model for the ChatGPT image ingest pipeline to keep costs down and avoid Gemini or OpenRouter unless explicitly needed later.

### 2026-05-06 — Phase 3 Image Retry Policy
When reprocessing ChatGPT image notes, only retry notes with fallback vision text, use smaller batches, and add exponential backoff for OpenAI `429` responses. Do not blindly rerun the entire image set if the existing notes already have usable vision summaries.

### 2026-05-09 — Image Ingest Pipeline Is Now Coherent (Post-Audit State)

After a full multi-agent coherence audit, the image pipeline was realigned. Current authoritative state:
- **Vision script:** `process_image_ingest.py` — uses OpenRouter (qwen model) first, OpenAI fallback. NOT Gemini.
- **Audit script:** `check_vision_needed.py` — searches category folders (`Tools/`, `Research/`, etc.) for paired notes. Reads `## AI Analysis` section body. `Asset_Notes/` dir does NOT exist and is NOT used.
- **Naming rule (absolute):** Every file in this workspace — images, notes, scripts exempt — uses Title-Case-With-Dashes. No exceptions.
- **Deprecated:** `rename_screenshots.py` — produces lowercase kebab-case, uses Gemini API directly. Do not use.
- **Embed fix tool:** `fix_embeds.py` — case-insensitive Visual_Assets lookup, fixes wrong-case `![[]]` embeds in category folder notes.
- **435 ChatGPT export images** still need ingest: `007_Resource_Library/OpenAI_History/ChatGPT_Image_Generator/`

### 2026-05-09 — Planned: Agent-OS Build

Tony plans to build Agent-OS as an Obsidian-based OS with dashboards. Before the rename was finalized, all hardcoded paths in scripts, CLAUDE.md, TOOLBOX.md, memory files, and hooks had to be updated. Content Creation Pipeline dashboard also planned — channel selector, format checkboxes (YT Short/TikTok/IG Reel/FB Reel), concept → long-form → auto-snip to vertical, Blotato publish routing per channel.

### Global Architecture Rule (2026-05-02)
- **Single Source of Truth**: All AI agent skills, generic scripts, tools, and MCP configurations must live exclusively in `001_Architecture/`. 
- **Symlink System**: Local agent folders (`~/.claude/skills`, `~/.gemini/antigravity/skills`) are physically symlinked to `001_Architecture/Skills`. Never create isolated agent-specific scripts/skills.
- **Python Providers**: Global API providers (`google.py`, `image_gen.py`, `kie_upload.py`) live in `001_Architecture/Tools/` and are symlinked into local project directories (e.g., Video_Editor) as needed.
- **Video Ingestion Pipeline**: Ingesting a video triggers `001_Architecture/Scripts/process_video_ingest.py` to extract FFmpeg keyframes (scene>0.3) and a Whisper transcript into a `007_Resource_Library/Videos/[Kebab-Name]/` package.
- **Universal Tagging**: EVERY ingested text file and Asset Note across the entire workspace MUST include 2 to 5 descriptive YAML tags for cross-agent semantic filtering.
### 2026-06-10 — AI Video Prompts: Spatial Orientation Lock for Falling Objects

When prompting any video generation model (Seedance, Veo3, Gemini Omni) for an object that drops or falls into frame, the model will default to animating the object entering on its edge unless orientation is explicitly locked.

**Pattern to use:**
1. State the object's orientation *before* describing the motion: "The deck is ALREADY ORIENTED HORIZONTALLY AND FLAT — parallel to the table surface, card backs facing camera"
2. Use a physical analogy: "like a hardcover book dropping face-down onto a table"
3. Add explicit negatives: "never rotates, never tilts, never stands on edge"
4. Lock relative to camera: "showing the wide face of the deck at all times"

Validated on Seedance 2.0 — without these constraints the deck came in vertically. Revised prompt (with these constraints) is queued for Gemini Omni.

---

### 2026-06-10 — Cloudinary SDK as Image Hosting Bridge for AI APIs

When an AI API requires hosted image URLs for parameters (e.g. `firstFrame`/`lastFrame`) but has no working upload endpoint, use Cloudinary:
```python
import cloudinary, cloudinary.uploader
cloudinary.config(cloud_name=..., api_key=..., api_secret=..., secure=True)
result = cloudinary.uploader.upload(local_path, public_id="my_id", overwrite=True)
url = result['secure_url']
```
All three Cloudinary credentials are in `~/.env-secrets`: `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_Key`, `CLOUDINARY_API_Secret`. SDK install: `pip3 install cloudinary --break-system-packages`.

`storage.fal.ai` DNS does not resolve from this machine — fal.ai SDK-based upload is not available. Use Cloudinary instead.

---

### 2026-06-10 — kie.ai Seedance 2.0 API Confirmed Working

- Model slug: `bytedance/seedance-2`
- Endpoint: `POST https://api.kie.ai/api/v1/jobs/createTask`
- Parameters: `firstFrame` (URL), `lastFrame` (URL), `aspect_ratio`, `prompt`
- Status poll: `GET https://api.kie.ai/api/v1/jobs/recordInfo?taskId=...` — success state is `"success"` (not `"succeeded"`)
- Cost: ~205 credits per generation, ~175s generation time
- Video result URL is in `data.resultJson.resultUrls[0]` — hosted on `tempfile.aiquickdraw.com`

---

### 2026-06-10 — Reference Video Scene Timestamps Must Match the Target File

`scene_analysis.md` timestamps were generated from `Reference.mov` (26s). `Reference2.mov` is only 15s. Always run `ffprobe` on the target video and verify duration matches any timestamp source before building a cut list. If they don't match, re-run pixel-diff detection on the target file directly.

---

### 2026-06-10 — Love_Hate Video Production State

Project: `000_Ingest/Love_Hate/`
- Scene-001 video generated (`Scene-001_Seedance2.mp4`) — rejected (wrong card orientation)
- Revised orientation-locked prompt ready; Gemini Omni being tested as alternative
- Reference2.mov cut into 5 scenes: `Video_Assembly/Reference2_Scenes/Scene_001–005.mp4`
- Shots 2–5: Gemini still image generation pending (`generate_shot.py`)
- Shot 6: Box hero (`ILHE BOX_4_IMG_6879.png`) → Veo3 orbit shot pending

---

## OpenAI history ingest preference
- Tony wants `007_Resource_Library/OpenAI_history` organized by move semantics into exactly two status folders: `Already Ingested` and `Needs Ingestion`.
- Tony does not want extra review buckets when the goal is simply to see what has already been processed versus what still needs ingestion.
- Tony wants raw conversation UUID folders in `OpenAI_history` grouped under a readable parent like `Already-Gone-Through-Theme-Process` rather than left as numeric strings at the root.
- Tony wants `OpenAI_history` to function as a readable `.md` conversation library, with image references linking out to files stored in `007_Resource_Library/Obsidian_Attachments/` rather than copying images into the history tree.
- Tony uses a two-part image system: `OpenAI_history` stores conversation context and links, while `Obsidian_Attachments` is the searchable visual library with image-specific notes.
- Tony wants the workspace map updated whenever new folders or structural files are created in the workspace, with a brief explanation for each new folder.
- During review-layer cleanup, if a file is already represented in the canonical ingested set, treat it as a duplicate/no-op instead of churning it again.
- Tony wants raw `conversations-*.json` shards to be treated as already ingested once the 2,011 theme notes exist, with `Multiple Conversations in One` reserved only as a fallback for future unsplittable bundles.
- Tony wants image ingestion status to be verified against canonical hashes in `007_Resource_Library/Obsidian_Attachments/OpenAI_Images`, and exact duplicate binaries should not be reprocessed.

### 2026-05-11 — Workspace Rename Strategy

- The workspace root is `Agent-OS`.
- Treat `/Users/tonymacbook2025/Documents/Agent-OS` as the canonical path in new docs, scripts, and configs.
- The rollback anchor for this migration is tag `pre-agent-os-rename-20260511` at commit `6c7c4d30f83750f92c074aa547f822a3d95e69cf`.

### 2026-05-11 — Restart Verification Plan

- After restarting, the first task is to verify that Claude Code, Gemini CLI, and Codex CLI all resolve the workspace through `/Users/tonymacbook2025/Documents/Agent-OS`.
- Confirm the canonical workspace path before making any further edits.
- Use the `pre-agent-os-rename-20260511` tag if the migration needs to be rolled back.

### 2026-05-11 — Agent-OS Canonical Root Verified

- `/Users/tonymacbook2025/Documents/Agent-OS` is the canonical workspace path.
- `~/.codex/config.toml` should keep only the `Agent-OS` project entry; the legacy stanza was removed during verification.

### 2026-05-11 — Antigravity Explorer Uses Agent-OS

- Antigravity's persisted workspace state should point at `file:///Users/tonymacbook2025/Documents/Agent-OS` so the Explorer root label matches the canonical folder name after restart.
- The live Antigravity settings import for custom CSS should also use the canonical `Agent-OS` path.
- `~/.claude/ide/63460.lock` was updated so the Claude/IDE bridge advertises `Agent-OS`.

### 2026-05-11 — Old Workspace Alias Should Not Be Used

- Tony does not want the workspace referred to by the old name anymore.
- `Agent-OS` is the only user-facing workspace name that should appear in Antigravity Explorer, logs, and future docs.
- Once the transition is complete, the legacy compatibility path should not be kept around.

### 2026-05-11 — `000_Ingest` Is Not Graphified

- `000_Ingest/` is a temporary dump area for unsorted incoming files.
- Graphify should skip `000_Ingest/` entirely and only cover files after ingest routes them into durable destination folders.

### 2026-05-11 — Graphify Rule Applies Across Claude, Codex, and Gemini

- The `000_Ingest/` exclusion must appear in the shared Graphify skill and in the bootstrap docs used by Claude Code, Codex, and Gemini CLI.
- The registry and hook helpers should treat `000_Ingest/` as non-federated staging, not a build target.

### 2026-05-29 — Affiliate Marketing Department Added

- `005_Affiliate_Marketing/` is now a full department with its own agent (`CLAUDE.md`)
- 18 affiliate programs tracked; more will be added over time
- Compliance docs for all programs live in `007_Resource_Library/Docs/Affiliate_Marketing/` — this is the shared source of truth across ALL agents
- Program subfolders hold links, performance data, notes — content routes to `006_Websites/` or `002_Content-Creation/`, not here
- Amazon Associates ToS is the first ingested compliance doc

### 2026-05-29 — Graphify Output Location Locked

- Canonical location: `001_Architecture/Graphify/Graphify-Out/`
- No symlink at root — agents always run: `graphify update . && rsync -a graphify-out/ 001_Architecture/Graphify/Graphify-Out/ && rm -rf graphify-out`
- `graphify-out/` is in `.gitignore`
- `001_Architecture/Graphify/Hooks/` (capital H) contains the federation hooks

### 2026-05-29 — Superpowers Plugin Output Paths Updated

- Specs now save to `001_Architecture/Superpowers/Specs/`
- Plans now save to `001_Architecture/Superpowers/Plans/`
- Changed in plugin cache at `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/` — may revert on plugin version update

### 2026-05-29 — Agent Runtime Audit Post-Antigravity Upgrade

- After any Antigravity upgrade, re-audit ALL skills symlinks across: `~/.claude/`, `~/.codex/`, `~/.gemini/`, `~/.gemini/antigravity/`, `~/.gemini/antigravity-ide/`
- `~/.gemini/antigravity/skills` was pointing to dead Claude-Agent path — fixed to Agent-OS
- Antigravity IDE native Gemini agent now has superpowers via `~/.gemini/antigravity-ide/GEMINI.md`
- MCP canonical config lives at `001_Architecture/MCP/gemini_mcp_config.json` → symlinked to `~/.gemini/antigravity-ide/mcp_config.json`
- claude-mem MCP added to that config (note: versioned path `13.3.0` needs update on claude-mem upgrades)

### 2026-05-29 — Three Memory Layers Confirmed

- `~/.claude-mem/` — claude-mem episodic (SQLite + Chroma, auto-watches sessions, searchable via /mem-search)
- `001_Architecture/Memory/` — shared human-readable vault memory, all agents can read
- `~/.claude/projects/.../memory/MEMORY.md` — Claude Code cross-session preferences only
- These three are complementary, not redundant. All wired up and working.

### 2026-05-29 — Plugin Sharing Clarification

- Plugins are runtime-specific by design — Claude Code plugins don't transfer to Codex/Gemini
- The SHARED layer across all runtimes is: skills (symlinked), memory (vault), instruction files (CLAUDE.md/AGENTS.md/GEMINI.md)
- Codex and Gemini CLI do not have native MCP support — MCPs are an IDE/extension feature

### 2026-06-06 — Obsidian New File Folder Uses Canonical Attachments Path

- Obsidian's default new-note folder should point at `007_Resource_Library/Obsidian_Attachments` rather than the dead `Obsidian_AttachmentsArchive` path.
- Keep the attachment library rooted in the canonical `Obsidian_Attachments` folder so new workspace metadata does not drift back to a nonexistent folder.

### 2026-06-06 — CLI Versions After Full Update

Current global npm CLI versions (post-update):
- Claude Code: 2.1.167
- Gemini CLI: 0.45.2
- Codex CLI: 0.137.0
- firecrawl-cli: 1.19.0
- hyperframes: 0.6.76 (must install with --ignore-scripts — sharp native build fails)
- playwright: 0.1.13
- pyright: 1.1.410
- typescript-language-server: 5.3.0
- vercel: 54.9.1
- npm: 11.12.1
- typescript: 5.9.3 (held — v6 is major, upgrade intentionally)

### 2026-06-06 — hyperframes Install Rule

Always install hyperframes with `--ignore-scripts`:
`npm install -g hyperframes@latest --ignore-scripts`
The sharp native module SIGKILL's the install without this flag.

### 2026-06-06 — Tutorial Skill Bundles Stay Together

- When a tutorial note ships with reusable skills and supporting upload instructions, keep the whole package together in `007_Resource_Library/Tutorials/` if Tony may tweak the skills later.
- Do not split the companion skills into `Tools/` just because they are reusable; preserve the source tutorial context and package relationship first.

### 2026-06-06 — Shared Skills Source of Truth

- Keep skills in `001_Architecture/Skills/` as the canonical source of truth so Codex, Claude Code, Antigravity, VS Code, Hermes, and other runtimes can reuse the same library through symlinks and shared workspace conventions.
- If a skill is channel-specific, keep it in the shared skills library when cross-runtime reuse matters, and use wiki or graph links to associate it with the relevant channel instead of relocating it out of the authoritative skills store.

### 2026-06-06 — New Department Routing

- `008_Investments/` is the active investment research and portfolio tooling department.
- `009_AI_Jobs/` is the department for AI job onboarding contracts, worker agreements, and platform-specific work references such as Mercor.

### 2026-06-14 — Git Repository Rules Hardened

- `000_Ingest/` is a temporary processing queue — never commit it. Files only belong in the repo after being wikified and graphified via the ingest skill.
- `graphify-out/` and `001_Architecture/Graphify/Graphify-Out/` are auto-generated output — never commit. Rebuilds automatically on `graphify update`.
- Raw ChatGPT export files (`007_Resource_Library/OpenAI_History/Already Ingested/`) are excluded — too large, redownloadable.
- All nested git repos inside Agent-OS must have their inner `.git` folders removed so GitHub sees them as plain folders in one unified repo.
- Run an API key scan before every git commit. GitHub's secret scanner will block pushes with live keys.

### 2026-06-14 — Universal Memory Write Rule (All Agents)

When saving any durable memory, always write to `001_Architecture/Memory/Global_Agent_Memory.md` first. Agent-specific memory (`~/.claude/.../memory/`, `Codex_Memory.md`, etc.) is secondary. Hard rules that apply to all agents also go in `Core_Memory.md` so they are read every session by every agent.

### 2026-06-14 — Agent Coverage Confirmed

All active coding agents read `Core_Memory.md` at session start:
- Claude Code Desktop + CLI → `CLAUDE.md`
- Codex CLI → `AGENTS.md`
- Gemini CLI → `GEMINI.md`
- Antigravity IDE (Claude Code ext) → `CLAUDE.md`
- Antigravity IDE (built-in Gemini agent) → auto-loads `Core_Memory.md`, `AGENTS.md`, `GEMINI.md`, and `claude-mem` context

Warp is not used as a coding agent — no config needed.
- Job-specific AI contracts should route into `009_AI_Jobs/[Platform]/` instead of the generic docs library.

### 2026-06-17 — Tool Manager Agent Is Mandatory — Never Answer Tool Questions From Memory

A dedicated Tool Manager skill exists at `001_Architecture/Skills/Tool-Manager/SKILL.md`. **All agents in all harnesses must invoke it automatically** whenever:
- Starting any task that requires knowing what tools, APIs, scripts, or skills are available
- Asked "do we have X?", "what can I use for Y?", "is there a skill for Z?"
- About to claim a tool is unavailable or suspended
- Building a pipeline that depends on specific APIs or models

**Never answer tool availability questions from memory, stale CLAUDE.md notes, or internal catalogs.** These go stale within days. Tony confirmed this is a hard rule after repeated failures.

**Invocation:** `Skill("Tool-Manager")` in Claude Code / Antigravity. Direct file read of `001_Architecture/Skills/Tool-Manager/SKILL.md` in Codex / Gemini CLI.

**Update protocol:** Tool Manager is read-only. When it finds something new or stale, it flags it and delegates the write to the calling agent. The calling agent updates TOOLBOX.md.

### 2026-06-17 — kie.ai Is The Full Media Stack (Not Just Video)

kie.ai provides: video gen (Kling, Veo, Seedance 2.0, Seedance 2.0 Fast, Wan, Sora), image gen (Nano Banana 2, GPT-Image-1), AND Suno music generation API. It is the single gateway for all AI media generation. fal.ai is secondary — use only for models not on kie.ai.

**Confirmed available on kie.ai as of Jun 2026:** Seedance 2.0, Seedance 2.0 Fast (NOT suspended — prior catalog entry was wrong), Suno API at https://kie.ai/suno-api.

### 2026-06-19 — Validation Hook System Is Live in Claude Code

Two hooks are now active in `~/.claude/settings.json`:
- **PostToolUse (`agent-os-build-tracker.js`):** After every Write/Edit on a functional artifact (.py, .sh, SKILL.md, .json configs), injects `⚠️ VERIFY REQUIRED` into Claude's context and appends to `/tmp/agent_os_build_manifest.json`.
- **Stop (`agent-os-stop-validator.js`):** Blocks Claude from finishing a turn (exit 2) if unverified artifacts remain in the manifest.
- **Validation script:** `001_Architecture/Scripts/validate_build.py` — run it, it clears the manifest. Type-aware: Python syntax+help, SKILL frontmatter+index, JSON parse, shell syntax, data-fetch completeness.

All agents should know: **Claude Code now enforces verification before task completion. This is not optional.**

### 2026-06-19 — Reimagined Realms Video Pipeline Skill

Full 10-phase faceless YouTube pipeline skill at `001_Architecture/Skills/Reimagined_Realms_Video_Pipeline/SKILL.md`. Invoke with `/reimagined-realms`. Replaces Higgsfield MCP — no subscription needed. Uses: Firecrawl (channel analysis), DAIPBR + 7-part Story Ideation (script), Tool Manager pricing cache (cost estimate), ElevenLabs `audio_tts.py` (voiceover + timestamps), beatmap from VO timing, per-clip shot list. ElevenLabs voice ID for this channel: `raMcNf2S8wCmuaBcyI6E`.

### 2026-06-19 — Skills Directory Is a Symlink — Always Use 001_Architecture/Skills/

`~/.claude/skills/` is a symlink to `001_Architecture/Skills/`. All skills created in `001_Architecture/Skills/[Skill_Name]/SKILL.md` are automatically available to Claude Code, Codex, and Gemini CLI. Never create skills anywhere else.

### 2026-06-21 — Airtable Model Catalog Restructured — 34 Variant Rows

The Model Catalog Airtable table (`Model Catalog` in base `appTQPmV4oWJHSfLX`, table `tblONvSjUufdAjZx3`) was rebuilt from 24 model rows to 34 variant rows (one per resolution/audio combination).

**Key facts for all agents:**
- Upsert key is now `Row ID` (e.g., `seedance-2.0_1080p`), NOT `Model ID`
- All price columns show genuine $/s (video) or $/img (image) — never normalized per-clip values
- Name field format: `Model (Resolution · Audio)` — e.g., `Seedance 2.0 (1080p · Audio)`
- New Airtable fields: Row ID, Resolution, Audio, Variant, Price Unit
- `catalog_refresh.py` generates rows from `model["variants"]` arrays in `model_catalog.json`
- 25 models total (24 active, Topaz Upscale inactive); 34 variant rows

**fal.ai Seedance 2.0 billing (confirmed):** Token-based at $0.014/1K tokens. Formula: `tokens = (height × width × duration × 24) / 1024`. Per-second rates: 720p=$0.302/s, 1080p=$0.682/s.

**WaveSpeed resolution pricing formula:** `base_price × multiplier × duration / 5`. Multipliers: 480p×1, 720p×2, 1080p×5. Seedance 2.0: 720p=$0.24/s, 1080p=$0.60/s.

**ElevenLabs Video-to-Music** added to catalog (id: `elevenlabs-video-to-music`). Topaz Upscale set to `inactive`.

### 2026-06-21 — Hard Rules: Validation, Reporting, and Completion

Three non-negotiable rules added to `Core_Memory.md` (all agents must follow):
1. **Never declare done without proof** — run `validate_build.py` or equivalent before reporting completion on any functional artifact.
2. **Multi-source fetches report everything** — list expected sources first, then report each as ✅ resolved or ❌ failed (with error + what Tony needs to do to fix it). Never present partial results as complete.
3. **Multi-part instructions: address all parts** — enumerate them before starting. Flag any part you cannot complete before moving on. Never silently drop an instruction.

### 2026-06-29 — Video Clip Generation Hard Rules (ALL Reimagined Realms Productions)

These rules are permanent and apply to every future video production:

1. **Never loop video clips** — looping is always visible to viewers and is never acceptable. If a clip is too short, re-generate it at the correct duration.
2. **Always generate with padding** — `generate_s = max(4, ceil(target_final_s + 1))`. Min 4s (Seedance minimum). This ensures real footage exists at every frame.
3. **Model selection by generated duration** — Seedance 1.5 Pro if `generate_s ≤ 12`, Seedance 2.0 if `generate_s > 12`.
4. **Script reads beatmap — never hardcode duration** — `batch_generate_videos.py` reads `target_final_duration_s` per clip from `Beatmap.json`. No `DURATION = N` constant ever.
5. **Max 8s final duration per clip** (hard rule) — viewers disengage beyond 8s. Ideal: 3–6s per clip.
6. **Use `--overwrite` flag for reruns** — `batch_generate_videos.py` skips existing clips by default; add `--overwrite` to force regeneration.

### 2026-06-29 — Pompeii Video Status (Reimagined Realms, Production 0001)

- 21 clips generated but 16 are wrong duration (5s instead of 8–13s)
- `batch_generate_videos.py` has been fixed with per-clip duration logic
- **Next session: run regeneration command** (see `001_Architecture/Logs/2026-06-29_Next-Session-Handoff.md`)
- After regen: stitch → audio stems → Suno music → final assembly
- Audio approach: film composer model — stems (ambient drone + tension risers + impact hits + scene SFX) layered independently, not per-clip sequential audio

### 2026-07-03 — Video Pipeline: Audio Stem Design Rules (ALL Productions)

**Hard rule: Never design audio stems without Gemini second-by-second video analysis first.**

The beatmap gives clip timing but not visual content. Stems timed from beatmap descriptions alone will be wrong — crowd sizes, animal presence, camera movement, and emotional intensity vary clip-by-clip in ways the beatmap cannot describe. The correct pipeline order is:

1. Generate all clips at correct durations
2. Stitch raw assembly (no audio)
3. Run Gemini on the stitched video → get second-by-second scene description
4. Build stem timing map from Gemini output (not from beatmap)
5. Generate stems with precise fade-in/fade-out derived from actual visual content
6. Suno music bed generated last, after stems are placed

**Why Gemini, not image analysis:** Still images miss motion, pacing, and the cumulative feel of a scene. Video analysis gives the composer context needed for tonality, impact placement, and riser timing.

**Stem categories (Reimagined Realms cinematic model):**
- Continuous layers: atmospheric drone, wind/ambient environment
- Act-timed layers: crowd presence, tension risers, seismic rumble
- Scene-specific SFX: footsteps, hooves, cart wheels, harness — timed to actual visual content per Gemini analysis
- Hit-point events: eruption booms, impact hits, silence drops — placed on exact frame
- Late-video: emotional/mournful tones timed to specific visual moments
- Music bed (Suno): generated last, underlies everything

### 2026-07-03 — Seedance API Fixes and Clip Generation Updates

1. **Seedance 2.0 correct kie.ai model slug** is `bytedance/seedance-2` (NOT `bytedance/seedance-2.0/image-to-video` — that returns 500 "model format incorrect")
2. **Seedance 1.5 Pro can generate exactly 12s** — clips with 12s final target can use 1.5 at 12s with no padding buffer; this is acceptable and saves significant cost vs Seedance 2.0 ($0.0375/s vs $0.31/s at 1080p)
3. **Always ffprobe-verify output duration** after generation — `batch_generate_videos.py` now checks actual clip duration vs target and flags any clip under target for Seedance 2.0 retry
4. **Archive originals before overwriting** — before running `--overwrite` on clips that were generated at wrong durations, move originals to `Video_Clips/Archive_<reason>/` folder
5. **Rule 3 update** (supersedes 2026-06-29 entry): Model selection is `Seedance 1.5 if generate_s ≤ 12, Seedance 2.0 if generate_s > 12`. Clips that need exactly 12s final duration should generate at 12s with 1.5 (no padding), not be forced to 2.0.

### 2026-07-03 — Pompeii Video Status Update

- C1–C7, C13–C19: regenerated at correct beatmap durations ✅
- C8–C12: regenerated at 12s with Seedance 1.5 (in progress as of this writing)
- Original 5s clips archived to `Video_Clips/Archive_5s_Originals/`
- **Next steps**: stitch all 21 clips → Gemini video analysis → stem map → audio generation → Suno music → final assembly

### 2026-06-29 — Airtable API Budget Fixed

- `catalog_refresh.py` now uses batch upsert (10 records per PATCH) instead of per-record GET+PATCH
- Monthly cron will use ~4–6 API calls instead of ~68

### 2026-07-03 — Pompeii Video Fully Assembled (Session 2 Close)

Full status of `0001_Pompeii_The_Escape` (Reimagined Realms):
- All 21 clips at correct beatmap durations ✅
- Raw stitch: `Assembly/raw_video.mp4` (152s, 232.6 MB) ✅
- Gemini second-by-second scene analysis: `Assembly/gemini_scene_analysis.md` ✅
- 13 audio stems generated (ElevenLabs SFX): `Audio_Stems/*.mp3` ✅
- Two review videos delivered: `raw_with_stems.mp4`, `raw_with_stems_narration.mp4` ✅
- `music.mp3` (Suno) blocked by kie.ai outage — retry next session with `python3 assemble.py --phase 4 --stop-phase 4`
- `final.mp4` blocked on Suno — once music generates, run `render_outputs.py`
- **Full handoff:** `001_Architecture/Logs/2026-07-03_Next-Session-Handoff.md`

### 2026-07-03 — Audio Composer Architecture: Vision-First Per-Scene Clips

**Current approach (stem map) is 65% quality. The correct architecture for all future Reimagined Realms productions:**

1. **Extract 1fps screenshots** from raw_video.mp4 → `Assembly/Frames/frame_XXXX.jpg` (ffmpeg, 720p)
2. **Gemini vision pass** — send all frames + `gemini_scene_analysis.md` + narration script simultaneously
3. **Output: per-scene audio brief** (JSON) — one audio decision per scene, not broad thematic stems:
   - Ambient layers (continuous beds: wind, room tone, rumble)
   - Spot FX / event clips (discrete: impact hits, risers, whooshes, crowd burst, hooves)
   - Timecode, duration, volume, fade-in/fade-out per clip
   - Clip name that indicates scene and time: `C05_0020_eruption_boom.mp3`
4. **Generate each clip individually** via ElevenLabs SFX (not one big generic stem)
5. **Export FCPXML** placing all clips on Premiere timeline at exact timecodes on separate named tracks

**Why this beats broad stems:**
- Crowd audio can fade out exactly when crowd disperses ON SCREEN (not on a timer)
- Impact hits land on the exact frame, not somewhere in a 30s stem window
- No looping, no generic behavior — each clip is composed for that specific visual moment
- Premiere import gives Tony full manual override on any clip

**Key distinction:** Some audio IS true stems (continuous ambient wind) and some IS discrete spot FX (eruption boom at 0:20). Both are individual files kept separate — nothing pre-mixed.

**Research requirement:** Before building `compose_audio.py`, run a documentary sound design research pass (Planet Earth II, Our Planet) and bake that knowledge into the Gemini composer prompt. The composer needs to know what risers, impact hits, transitions, and silence decisions look like in a real production.

**Script to build:** `001_Architecture/Tools/Audio/compose_audio.py`

### 2026-07-03 — Audio Level Standards (Locked In)

- Narration: loudnorm -14 LUFS / -1 dBTP (YouTube standard, via ffmpeg loudnorm filter)
- Ambient stems in final mix: 40% volume
- Ambient stems in stems-only review: 85% volume
- Spot FX event clips: set individually per clip in Premiere (no pre-set)
- Music bed (Suno): 12% (heavily ducked under narration)
- Per-stem volume override supported in `stem_map.json` via `"volume"` key

### 2026-07-03 — Reusable Audio Pipeline Scripts (All Accept production_folder Arg)

All scripts in `001_Architecture/Tools/Audio/` are production-agnostic:
- `generate_stems.py` — reads `Data/stem_map.json`, generates each stem via ElevenLabs SFX, handles chunking for stems > 28s
- `mix_stems.py` — reads stem_map.json, builds ffmpeg filter_complex with per-stem adelay + volume + fade + atrim
- `render_outputs.py` — renders 3 outputs: stems-only review, stems+narration, final with Suno music
- `compose_audio.py` — **TO BUILD** — vision-based composer (see entry above)
- Airtable free tier: 1,000 calls/month; resets July 1

### 2026-07-04 — Reimagined Realms Pipeline Fully Validated (Pompeii Test #1)

Production 0001_Pompeii_The_Escape completed end-to-end. V8 is the final render (C20 fixed, Suno music, locked audio formula). Tony rated it 100%.

**Locked pipeline rules (all agents must follow):**
- Clip hard max: **8s** `target_final_duration_s` — never exceed, Seedance 1.5 max is 12s (4s buffer)
- Script formula: `ceil(target_min × 163 × 1.15)` words — voice raMcNf2S8wCmuaBcyI6E at 163 WPM + 15% padding
- TTS gate: after ElevenLabs generates narration.mp3, ffprobe duration — if >5% short of target, STOP and flag
- Audio mix (locked): stems vol=0.88 → -23 LUFS; narration vol=3.09 → -14 LUFS; music vol=0.12 → -28 LUFS; sidechain duck threshold=0.015 ratio=4 attack=150ms release=800ms
- Suno API: endpoint `https://api.kie.ai/api/v1/generate` — `callBackUrl` field required (use placeholder); response is array of URLs, pick longest by ffprobe duration
- assemble.py is now universal: lives in `001_Architecture/Tools/Video-Generation/Channels/Reimagined_Realms/assemble.py`; reads `Production/assemble_config.json` per production

**Thumbnail formula (composition-based, not palette-based):**
Single human figure back-to-camera, lower third, deep vanishing point, human dwarfed by environment. Palette matches story emotion. No text. Generate 3 concepts per video, Tony picks one.

**Title formula (3 options per video):**
1. Primary: "[Number] [Subject] [Vanished/Did X]. [Unresolved tension statement]." — curiosity gap
2. Secondary: "What Really Happened to the [Number] [People] Who [Survived/Escaped] [Event]" — discovery frame
3. Tertiary: "[Place] Wasn't a [Expected]. It Was a [Reframe]." — pattern interrupt

**Description formula:** First sentence = the exact question someone types into YouTube search. Description optimizes for search intent; title optimizes for curiosity hook. Never swap these roles.

### 2026-07-04 — Blotato Upload Live + Full Pipeline Locked Through Phase 12

First real Blotato YouTube upload completed: Pompeii ("18,000 People Lived in Pompeii...") published private to ReimaginedRealms channel (account id `30323`). Video: `https://www.youtube.com/watch?v=3Y8e8hOs7Ks`.

**Newly locked rules (all agents must follow):**
- **CTA / end-screen system**: every video ends with a fixed, non-negotiable 8-second hold on one continuous clip (no video cuts). Audio inside that hold = 1.5s silence gap (`CTA_GAP_SECONDS`) → static pre-rendered CTA audio (`Brand_Assets/CTA/cta_follow_reimagined_realms.mp3`, 3.76s, voice `raMcNf2S8wCmuaBcyI6E`, line: "Follow Reimagined Realms. History gets stranger every episode."). Story narration must never spill into this window — it is a dedicated final beat, not derived from VO timing. This is now coded into the universal `assemble.py`'s `phase_concat_narration()` (auto-appends gap+CTA every run) — never regenerate the CTA line/audio per production.
- **Beatmap rule**: the last sub-beat of the final act is always a "CTA Hold" beat — single clip, `target_final_duration_s = 8.0` fixed (only beat in the pipeline with a hardcoded, non-derived duration), topically relevant to that episode, visually clean (YouTube end screen overlays on top of it).
- **Script rule**: scripts no longer include a spoken CTA line (Phase 4) — CTA is 100% a post-production asset now.
- **YouTube upload defaults via Blotato (locked, all RR videos)**: `isMadeForKids: false`, `containsSyntheticMedia: true`, `privacyStatus: private` on upload (manual review before going public), playlists NOT automated (Tony adds manually during scheduling for now).
- **Blotato mechanics**: custom thumbnails must be ≤2MB (compress PNG→JPEG via ffmpeg if over); large local files need `blotato_create_presigned_upload_url` → `curl -X PUT --data-binary` → use the returned `publicUrl` in `create_post`. If Blotato errors "reconnect your YouTube account" for thumbnails, that's an OAuth scope issue fixed in the Blotato dashboard, not a script bug — already-uploaded media URLs don't need re-uploading after reconnect.
- **Reimagined_Realms_Video_Pipeline skill is now a true 12-phase, start-to-finish orchestrator** (`001_Architecture/Skills/Reimagined_Realms_Video_Pipeline/SKILL.md`) — Phase 11 (media generation + assembly, one quality pause after test clip C1) and Phase 12 (Blotato upload, pause for title/thumbnail/privacy) replace the old "next steps — manual" list. Running `/reimagined-realms` now goes all the way to a live private YouTube upload, not just a package of files.

### 2026-07-06 — Motion Graphics "Slop" Definition + Orchestrator Architecture Preference (Vox-Style Explainers)

Reviewed Anomalous Wild's Bioluminescence Weapon video (phylogenetic tree scene, 1:38–2:14) with `gemini_scene_analysis.py` (now duplicated per-channel at `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/gemini_scene_analysis.py` — original at `Tools/AI-Analysis/gemini_scene_analysis.py` stays Reimagined-Realms-flavored/untouched; duplicate, never edit the original when a new channel needs its own copy).

**"Slop" defined precisely (applies to all future Vox/Kurzgesagt-style explainer motion graphics):** abstract data-viz (dots, lines, charts, tree diagrams) is NOT itself the problem. The problem is when narration names a concrete subject (an animal, object, person) and the visual stays abstract instead of showing an illustrated overlay of that concrete subject tied to the data shape. Every named subject in narration needs a corresponding illustrated asset on screen, not just an abstract shape standing in for it.

**Root cause pattern to watch for:** the failure traced back to the script's own VISUAL direction line under-specifying the treatment (it explicitly asked for "glowing dots on a tree," never asked for illustrated creature overlays) — not a model execution failure. When diagnosing a "slop" complaint, check the script's VISUAL line before assuming the generation/build step is at fault.

**Standing architecture preference — orchestrator, not monolithic skill:** Tony does not want one skill responsible for directing a motion graphic AND generating its illustrated assets AND animating them ("I don't want the one skill to have too many tasks that it does shortcuts on"). Preferred shape for any future motion-graphics work: a director/orchestrator skill that identifies needed assets per scene and delegates actual asset creation to dedicated specialized agents, then handles composition/animation itself. This is the same discipline as the existing Reference-First Pipeline in `002_Content-Creation/Video_Editor/CLAUDE.md` (Nano Banana illustration → Figma/SVG labels → Remotion static asset) — apply it to Vox-style explainer scenes too, don't invent a separate pattern.

**Case-Study-Analysis skill ≠ visual taste transfer:** confirmed the existing case-study skill (`001_Architecture/Skills/Case-Study-Analysis.md`) is a performance/growth framework (viral score, hooks, retention) with only a shallow "Visual Elements" checklist line — it was never wired to actually re-inject reference screenshots into context at generation time. Do not assume curated case-study screenshots alone will improve visual output; a real reference needs to be handed in-context at the moment of asset generation, not just cited in a written analysis doc.

**DEFERRED — do not build yet:** one-off test proved illustrated motion-graphic opens beat bare abstract data-viz opens for scene intros, not just for the mid-scene creature-overlay fix above. Test: GPT Image 2 (kie.ai model id `gpt-image-2-text-to-image`) generated a static "tree of life" (bioluminescent tree, bacteria at roots, jellyfish/anglerfish/squid in branches), then Seedance 1.5 Pro (kie.ai model id `bytedance/seedance-1.5-pro`, image-to-video via `input_urls`, Cloudinary as the URL bridge) animated it into a 10s clip for scene_06's opening line ("What makes this more remarkable is..."). Tony confirmed this reads as far less boring than the original bare tree-draws-itself open. No script was created and no existing script (Reimagined Realms or otherwise) was touched — this was run as inline one-off Python, intentionally not formalized. When the Vox-style asset pipeline eventually gets locked in (see orchestrator note above), the storyboard/VISUAL-direction generator (compare Anomalous Wild's vs. Reimagined Realms' storyboard generation to see which already handles this better) should default to illustrated/narrative opens over abstract-only ones for scene/video openers. Artifacts kept at `002_Content-Creation/Video_Editor/002_Channels/001_Anomalous-Wild/001_Bioluminescence-Weapon/_tests/intro_tree_of_life/` for reference.

### 2026-07-04 — Future Pipeline Plans (Context Only — Do Not Build Yet)

- **Airtable-driven automation**: after 10 validated videos, intake questions become Airtable columns; agent reads row, generates video autonomously
- **Idea generation cron**: daily job checks queue, generates 3–5 ideas if fewer than ~10 ungenerated ideas in Airtable; Tony approves/ignores each; never auto-generates without approval
- **Short-form pipeline**: separate 9:16 mode, built after long-form is validated through 10 tests
- ~~Blotato upload skill~~ — DONE 2026-07-04, see Phase 12 of Reimagined_Realms_Video_Pipeline skill
- **Description chapter auto-generator**: still built manually (transcribed from Beatmap.json by hand each time) — a small script to auto-format chapters would remove this manual step, but is not blocking since Phase 12 works today
- **Playlist automation**: Blotato's `playlistIds` field is available and account has 18 playlists mapped, but Tony wants this to stay manual for now

### 2026-07-08 — Anomalous Wild Video Pipeline Built (11-task plan, Task 10 skipped) — `/anomalous-wild` now live

Built via `superpowers:subagent-driven-development` (fresh implementer subagent per task, task-scoped reviewer with fix-and-re-review loops, final whole-branch review). Full write-up: `000_Wiki/Video-Production/Anomalous-Wild-Pipeline-Scripts.md`. Registry of new scripts: `001_Architecture/Tools/Tool-Manager/data/pipeline_scripts_registry.json` (`channels.anomalous_wild.new_pipeline_scripts`).

**What it is:** Anomalous Wild's own start-to-finish orchestrator (`001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/SKILL.md`, invoke via `/anomalous-wild`), mirroring Reimagined Realms' automation level: word-level narration timestamps, per-beat Tool-Manager tool routing (never hardcoded), a full Scientific Diagram sub-pipeline (fixes the garbled-diagram-text "AI slop" bug from Bioluminescence Weapon), YouTube package generation (incl. real thumbnail generation), and Blotato upload.

**Locked facts all agents should know:**
- Blotato YouTube accountId for Anomalous Wild is `42514` — displayed in Blotato's own dashboard as "Anomalos Wild" (a typo from account setup, confirmed by Tony 2026-07-08 — do not "fix" this by assuming it's the wrong account). Do not confuse with Reimagined Realms' `30323`.
- Scientific Diagram sub-pipeline pattern (the actual fix for garbled AI-generated diagram text): (1) research a real reference image via Openverse, (2) generate a clean illustration via kie.ai GPT-Image-2 with an explicit no-text/no-label negative prompt, (3) Gemini vision detects real per-image label coordinates — never guesses, structurally strips coordinates from any `not_found` entry, (4) Remotion (`DiagramLabels.tsx`) places labels at those exact detected coordinates. Apply this same 4-step pattern to any future channel that needs labeled scientific/technical diagrams — do not go back to asking an image model to draw labels directly.
- `end_card_v3.mp4` (`Brand_Assets/End_Card/`) is a fixed, hardcoded asset for every Anomalous Wild video — `scaffold_new_production.py` hard-fails if it's missing, and it's always appended via ffmpeg concat, never regenerated or routed through Remotion.
- **`validate_build.py`'s `check_skill()` does NOT parse YAML** — it only naively string-searches for `'name:'`. A SKILL.md can have genuinely broken frontmatter and still show `✅ PASS`. If a skill's own trigger-matching seems off, verify frontmatter with `python3 -c "import yaml; yaml.safe_load(open(path).read().split('---')[1])"` directly — this caught a real bug (a dangling unquoted second `<example>` block) that was degrading both `Anomalous_Wild_Video_Pipeline/SKILL.md` and `Reimagined_Realms_Video_Pipeline/SKILL.md`'s real trigger descriptions in the live skill list (both now fixed).
- **Final whole-branch review is not optional for multi-task builds**, even when every individual task passed its own review — it caught 2 real integration bugs (a schema/data-shape contradiction between two separately-approved tasks, and a hard constraint recorded as data but never mechanically enforced anywhere) that no single task's review could see. Always run one after a multi-task subagent-driven-development build, on the most capable available model.

**Pre-existing gaps flagged, not yet resolved:** no locked ElevenLabs voice ID for Anomalous Wild (orchestrator asks at runtime); `pipeline_supervisor.py` expects a `Production/new_clips_prompts.json` manifest with no script yet auto-building it from the new `Shot_List.md` format.

### 2026-07-10 — Design-Rules-Learned System: Self-Accumulating Styling Judgment for Video Pipelines

Tony wants motion-graphics design judgment to accumulate across iterations, not be re-explained every session. New durable, additive file: `002_Content-Creation/Video_Editor/003_Remotion/src/skills/design-rules-learned.md` — rule = general principle + the concrete correction/confirmation that taught it. Never delete or silently overwrite an entry; a narrowing/override gets a new dated entry that says so explicitly. Wired into the Remotion app's own AI skill-detection system (`003_Remotion/src/skills/index.ts` — added as a new `GUIDANCE_SKILLS` category) so the in-app prompt-driven motion-graphics tool (`DynamicComp`) picks it up automatically, not just human/agent readers. Pointed to from `Video_Editor/CLAUDE.md` and `Anomalous_Wild_Video_Pipeline/SKILL.md`.

**Rule 1 locked in:** documented channel brand accent colors (logo/thumbnail/lower-third chrome) are not automatically correct for in-scene diagram/callout graphics over generated illustration content — that content isn't "branded." Default: sample the actual image for color (PIL or similar) rather than assume a brand hex; default to white label text on black backgrounds for contrast unless a reference shows otherwise. Taught by the Anomalous Wild esca/bacteria callout: first pass wrongly reused neon green `#8AFA47` (documented as logo/arrow accent) just because it was the one color already in code; corrected to a cyan sampled directly from `Fish-01.png` (`rgb(19,245,251)`), which separately validated the channel's own "Accent Cyan" entry — so the lesson is "verify against real pixels," not "brand colors are wrong."

**Rule 2 locked in:** label/text reveals should blur-resolve + fade in (not flat opacity pop); leader lines should draw progressively over ~15-25 frames, not appear instantly. Confirmed explicitly by Tony as a liked pattern, not a correction.

**Known flagged gap, intentionally not touched:** `DiagramLabels.tsx` (the Scientific Diagram sub-pipeline's shared component) hardcodes brand green `#8AFA47` as its line/label color default — contradicts Rule 1 above. Left alone since it's already a locked, shipped part of `/anomalous-wild` — don't change without asking first. Surface this if a future diagram beat's styling looks off-brand for its content.

### 2026-07-10 — Motion-Graphics Skill Built (Companion to design-rules-learned.md)

Same session as the design-rules-learned entry above, extended: after 3 more correction rounds on the same esca/bacteria callout clip (label placement off the subject into open space, non-parallel radial leader-line angles, spring-overshoot pulse reveal with a monotonic-`interpolate()` gotcha), Tony ran a short interview (was a subagent used? was `Anomalous_Wild_Video_Pipeline` invoked? — no to both, everything done ad hoc in-conversation) that concluded with him asking to build a dedicated `Motion-Graphics` skill via `skill-creator`.

**New skill:** `001_Architecture/Skills/Motion-Graphics/SKILL.md` — general composition/timing/color/terminology principles for any motion-graphics work (diagrams, kinetic typography, chart reveals, title cards). Explicitly authority-ordered: `design-rules-learned.md` (production-corrected, ground truth) > this skill's own principles (cited/generalized) > `references/treatment-styles.md` (Kinetic Typography/Vox/Kurzgesagt craft notes, flagged as unvalidated general knowledge, not locked rules). Scope chosen broad (not diagram-only) and validated via vibe-check only, no formal eval loop — both per Tony's explicit answers when asked to scope.

**Vault research finding, worth knowing:** the pre-existing channel style docs (`002_Content-Creation/Video_Editor/.agents/styles/{Kinetic-Typography,Vox-Documentary,Kurzgesagt-Animated}.md`) are all literally marked `status: placeholder — needs interview to flesh out implementation details` — there was no real, tested motion-graphics composition knowledge anywhere in the vault before this session. Don't cite those files as validated technique; they're aesthetic-direction stubs only.

**Deferred, not yet applied:** Tony gave one more critique (bigger spring overshoot amplitude, stronger label glow at the pulse peak) but explicitly said not to act on it this session — logged in `Feedback_Loop/2026-07-10_Feedback.md`, to be applied in the next Motion-Graphics test session.

**Also flagged, not run:** `graphify update 001_Architecture` (fast/no-LLM) ran clean but did NOT pick up the new doc content (node count unchanged, 1620/1829/364) — the new SKILL.md/wiki files need the full interactive `/graphify --update` semantic pass to actually enter the graph. Video Editor's own domain graph is still unbuilt entirely (`pending build` in the registry) — pre-existing gap, not created this session.

### 2026-07-11 — Anomalous Wild: New Locked End Card + Blotato Upload Gotchas (400MB cap, Content-Type header)

**Locked end card asset changed.** `end_card_v3.mp4` is retired — the new locked end card for every future Anomalous Wild production is `Brand_Assets/End_Card/Anomalos_Wild_End-Card_Hero.mp4` (10s, 300 frames @ 30fps, rendered from the updated `AnomalousWildEndCard.tsx`). Tony redesigned the layout: red subscribe button removed entirely (component deleted from the .tsx, not just hidden), "THANK YOU / FOR WATCHING" title shrunk 110px→64px, and all content (title + background animal imagery) shifted to the bottom ~78% of frame via `justifyContent: "flex-end"` on the CTA stack and `top: "22%"` on the background `Img` — leaving the top of frame clear/dark for YouTube Studio's end-screen recommended-video overlay to sit on top of without visual clash. Tony confirmed the final layout as correct after two iterative still-frame previews (not full renders) before committing to the real 10s render. Old end cards (`end_card.mp4`, `end_card_v2.mp4`, `end_card_v3.mp4`) are now in `Brand_Assets/End_Card/Archive/` (Tony moved them himself). Updated to reference the new filename: `scaffold_new_production.py`, `test_scaffold_new_production.py`, `Anomalous_Wild_Video_Pipeline/SKILL.md`, `000_Wiki/Video-Production/Anomalous-Wild-Pipeline-Scripts.md`. The already-published Bioluminescence Weapon V6 video keeps its old end card — Tony explicitly said not to re-render/re-upload it just for this.

**Anomalous Wild's brand thumbnail template lives at `Anomalos_Wild__Thumbnail_Style.json`** (channel root folder) — a locked design spec (purple gradient bg, bold white lowercase headline top-left, single realistic animal cutout right with neon-green glow, one red arrow to the "weird" feature). This is NOT what `generate_youtube_package.py`'s built-in thumbnail generator produces (that script defaults to no-text photorealistic mood-variation concepts, which is off-brand for this channel). Tony confirmed the brand-template output as "Grade A" — treat the JSON template's `prompt_template.base_prompt` as the default thumbnail generation path for Anomalous Wild going forward, not the pipeline script's built-in generator.

**`generate_youtube_package.py`'s title/description builder (`build_titles`/`build_description`) is broken** — `.title()` mangles apostrophes ("Anglerfish'S"), long titles truncate mid-word, hashtags concatenate with no delimiter. Bypass it and hand-write YouTube copy directly into `Package/YouTube_Package.md` until someone fixes the script itself.

**Blotato upload — two real gotchas, both now known:**
1. **400MB video upload cap** on the current plan. A 944MB source render failed with an explicit error; two-pass ffmpeg re-encode targeting ~6.3Mbps (1080p30) brought it to ~330MB with acceptable quality. Check file size against this cap *before* attempting upload on any future Blotato video post.
2. **Presigned-upload PUTs need an explicit `Content-Type` header.** `curl -X PUT --data-binary` with no `-H "Content-Type: ..."` uploads as `application/x-www-form-urlencoded` regardless of real file type, and `blotato_create_post` then fails with a misleading, unrelated-looking error: `"Failed to fetch media URL: char 'e' is not expected.:1:1"`. This is NOT a reachability problem — verify with `curl -I <publicUrl> | grep -i content-type` and always pass `-H "Content-Type: video/mp4"` / `image/png` explicitly on every Blotato local-file upload, for any channel.

### 2026-07-12 — Neon Parcel TikTok Shop Creator Pipeline Built + Validated on Colorsmart Pens

Built via `superpowers:subagent-driven-development` (8-task plan, per-task review with 2 fix rounds, final whole-branch review that caught 2 real cross-cutting fail-safe bugs no single task's review could see). Full write-up: `000_Wiki/Video-Production/Neon-Parcel-TikTok-Shop-Creator-Pipeline.md`. Spec/plan: `001_Architecture/Superpowers/Specs|Plans/2026-07-1[12]-Neon-Parcel-Tiktok-Shop-Creator-Pipeline*`.

**What it is:** A distinct invocation context within the existing `TikTok-Shop-Affiliate-Video` skill (extended in place, not forked) for TikTok Shop Creator affiliate videos on the NeonParcel TikTok account. Not e-commerce (Tony doesn't sell his own products here) — this is commission/GMV-based affiliate work, distinct from the Uno Mas Creative/Board-Nomad POD shops. Output model: 3 genuinely distinct vertical cuts per product (different beats/pacing, not shared-cut-swapped-audio), no YouTube pairing — supersedes the skill's generic "3 cuts × 2 audio = 6 outputs" default for this context.

**Locked facts all agents should know:**
- Compliance is 3-phase: local ledger scan (Phase 1, `Compliance-Ledger.md` — 10 citation-backed rules extracted verbatim from the real TOS bundle, never paraphrased), live Firecrawl freshness check (Phase 2, cadence-gated), post-build vision/transcript scans (Phase 3, both fail-safe-to-FLAG on ambiguity, never silently CLEAR).
- **Firecrawl cannot scrape `seller-us.tiktok.com`** at all ("we do not support this site") — confirmed not an auth/rate-limit issue by independently reproducing against a real URL. Phase 2 is correctly wired end-to-end but currently provides zero real policy-drift detection until this vendor limitation is resolved. Don't re-diagnose this as a bug in future sessions.
- **RULE-008 (disclosure) has a real-world addendum, not from the TOS bundle text:** Tony confirmed via direct platform observation that attaching a TikTok Shop product link auto-adds a "Creator earns commission" tag, which serves as the disclosure for this content type — other TikTok Shop affiliate creators don't use `#ad` either. For Neon Parcel TikTok Shop Creator videos with a product link, use ~3 relevant hashtags instead of `#ad`/`#sponsored`. This is flagged as observation-based in the ledger, not a document citation — revisit if a future TOS refresh or platform behavior change contradicts it.
- **`isBrandedContent` (Blotato TikTok field) ≠ affiliate/commission content.** That flag is for direct brand-paid partnerships with brand-dictated guidelines specifically — always `false` for TikTok Shop Creator/affiliate videos.
- **Blotato has no TikTok Shop product-tagging field anywhere** (checked the live `blotato_create_post` schema directly, every TikTok-specific field enumerated) — product links must be attached manually in the TikTok app after posting/drafting via Blotato. `isDraft: true` does work for saving to the TikTok drafts inbox, confirmed working 2026-07-12, but Blotato's post-status API has no distinct "draft" state (only `in-progress → published | scheduled | failed`) — always have Tony confirm in-app, don't trust the API status alone.
- **Loudness normalization is now a mandatory pipeline step** (`normalize_loudness.py`, SKILL.md Step 5a.5) — raw VO previously measured -34 to -35 LUFS (no clipping risk, just far too quiet vs. TikTok's ~-14 LUFS norm) with zero normalization step before this. Two-pass EBU R128, default target -14 LUFS / -1.5 dBTP.
- **Validated shot-matching workflow** (Tony's explicit approval on Colorsmart Pens, now the standard for this pipeline): transcribe VO with word-level timestamps (ElevenLabs Scribe) → dense keyframe vision sampling (~every 4s, not just scene-change detection — long continuous handheld clips often yield only 1 scene-change frame) → match real footage moments to narrated beats → when no clip shows a narrated outcome, a still image + slow Ken Burns zoom is an acceptable, endorsed substitute (reusing the same static asset across all product variants for that one beat is fine, not a duplication problem).
- **Never commit rendered video `.mp4` output to GitHub from any pipeline** — only pipeline code/scripts/architecture + markdown compliance/caption docs. `*.mp4` is already globally gitignored. See `[[feedback_video_git_commit_policy]]` in Claude's cross-session memory for the full rule.

**First real production:** Colorsmart Pens (3 videos). V1 posted to Blotato as a TikTok draft (`accountId: 27763`, username `neonparcel`) — confirmed landed in Tony's TikTok drafts inbox. V2/V3 captions prepared, Tony posting those manually.

### 2026-07-31 — Neon Parcel TikTok Shop Creator: Product #0002 (Glass Guard), VO Pause-Trim Fix Made Permanent

Second real production on this pipeline, single-video mode (Tony explicitly opted out of the standard 3-variant set for this product — confirm per-product, don't default to 3). Full write-up: `000_Wiki/Video-Production/Neon-Parcel-TikTok-Shop-Creator-Pipeline.md`.

**New permanent pipeline step — VO pause trimming (SKILL.md Step 5a.4, `scripts/trim_vo_pauses.py`), always run before loudness normalization (5a.5).** A naive hard-cut trim at silence boundaries (plain `atrim`+`concat` at `silencedetect` start/end timestamps) causes two audible defects: clicks/pops (no crossfade across the edit discontinuity — confirmed via a raw-PCM sample-to-sample jump scan, 20 click events at threshold 8000/16-bit) and clipped words (the -30dB detector threshold can trigger a few ms inside a trailing/leading consonant). Fix: keep a 120ms safety-padding margin of real audio on both sides of every cut, plus a 15ms fade at every join. Verify any new source with (1) a raw-PCM sample-jump scan — should be zero — and (2) a re-transcription diff against the original script — no words should go missing. This generalizes beyond this pipeline: apply the same padding+fade approach if pause-trimming is ever needed for Reimagined Realms or Anomalous Wild VO too, don't reinvent a naive version there.

**`analyze_clips.py`'s Qwen-VL vision calls have hard caps, confirmed by hitting both:** max 16 images per OpenRouter call, and a ~128K context-length ceiling that triggers around 10 full-resolution frames in one call. Batch at ≤8 frames per call and downscale each frame to ~640px width to stay safely under both.

**Vision analysis has a real blind spot: it cannot tell "nothing here" from "this surface is now perfectly clean/transparent."** A product that makes glass genuinely spotless will produce footage that reads as an empty/misfired shot (camera pointed at background through invisible glass) to both a vision model and a quick human glance at frames — there's nothing left to see specifically because the product worked. Confirmed on Glass Guard's IMG_9184 (shot through cleaned shower glass at the ceiling) — Tony corrected this directly after the vision scan and an independent full-resolution frame check both misread it as ceiling-only footage. Don't drop a "content-free" clip from an edit without confirming with whoever shot it, especially for any cleaning/clarity/polish product category.

**`compliance_vision_scan.py` reliably false-flags the promoted product's own packaging/logo as a third-party trademark — now confirmed 2/2 products.** This is expected, not a bug, per the existing script design (fail-safe to FLAG), but it is a *guaranteed* flag on every product going forward, not an edge case — worth tightening the prompt directly next time this pipeline gets touched, to exclude the specific product being promoted in that listing while still catching real unrelated branding.

**Account ID discipline:** NeonParcel has *different* Blotato account IDs per platform — YouTube is `25731`, TikTok is `27763` (confirmed live 2026-07-31). Don't assume one ID carries across platforms for the same brand; always verify live and match to the specific platform before posting.

### 2026-08-03 — Reimagined Realms POV Shorts: First Real Production (Pyramid Builder I. Deep) Published Across 4 Platforms; Graphify Locked to Text/Code Only

Full end-to-end run of the Reimagined Realms POV Shorts pipeline (sibling to the long-form Reimagined Realms pipeline — vertical 9:16 historical "day in the life" no-dialogue Shorts, min 65s), built across 6 SDD plans over prior sessions (Video-Analyzer, Foley-Generator+Seedance-Guide, Beat-Planning/Shot-List, Image/Video-Generation, Assembly, Text-Overlay). This was the first real subject run: "Pyramid Builder I. Deep" (ancient Egyptian pyramid builder, Giza, c. 2560 BC), research-guided (WebSearch on Giza Workers' Village archaeology) but treated as creative guidance not a script, per Tony's explicit framing. Skill: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/SKILL.md`. Registered in Tool-Manager: `001_Architecture/Tools/Tool-Manager/data/pipeline_scripts_registry.json` → `reimagined_realms_pov_shorts`.

**Full pipeline ran with zero failures:** 13-shot beat plan (65s floor) → 13 images (GPT-Image-2) → 13 Seedance 1.5 Pro clips with native audio → concat/assembly → Suno music → -14 LUFS mix → versioned `Final_v1.mp4` → Remotion text-overlay captioning. Real cost ~$5-6, confirmed with Tony before spending.

**POV Shorts caption conventions locked in from Tony's critique (now in `POV_Style_Guide.md` and `POVCaption.tsx`, commits `54ae664`/`0dc8874`):**
1. Opening title caption states the actual subject from frame 0 ("POV: You Wake Up As An Egyptian Pyramid Builder"), never a literal blank — YouTube Shorts auto-grabs an early frame as the thumbnail.
2. All captions (title + per-vignette label) sit in the top ~18% of frame, not mid-screen/bottom — clear of platform UI, matches where the eye is drawn first on Shorts/Reels/TikTok.
3. Frame-0 captions render at full opacity immediately (no fade-in) — same root cause as #1. `POVCaption.tsx`'s `useCaptionVisibility` now branches: captions starting at frame 0 skip the fade-in entirely; every other caption keeps it.

**Distribution locked in as the new default:** every finished POV Short now posts to YouTube, TikTok, Instagram, AND Facebook via Blotato — Tony's explicit instruction, not a per-video decision to re-ask about. Account IDs: YouTube `30323`, TikTok `33717`, Instagram `35548`, Facebook `18651`/pageId `407939555731086`. **Only YouTube (`containsSyntheticMedia`) and TikTok (`isAiGenerated`) expose an AI-disclosure field in `blotato_create_post`** — Instagram and Facebook have none, checked directly against the live schema. Caption/hashtag research done live (2026-08-03): TikTok sweet spot 150-300 chars/3-5 hashtags; **Instagram hard-capped hashtags at 5 per post starting Dec 18, 2025** — the old "30 hashtags" guidance is stale everywhere it might still appear.

**Graphify workspace policy, now hard-locked:** graphify must never process video or image files — text/code architecture graph only ("second brain" of how things connect), per Tony's explicit instruction after the Video Editor domain build attempt hit 979 files/7.8M words (mostly binary production media) and tripped graphify's own size gate. Enforced via a new repo-root `.graphifyignore` (media extensions: mp4/mov/mp3/wav/png/jpg/jpeg/webp/gif). **Also fixed a real pre-existing documentation bug:** `REGISTRY.md` claimed the ignore file lives at `.graphify/.graphifyignore` — the tool actually reads `.graphifyignore` directly at the repo root and ancestor directories (confirmed by reading the installed package's `detect.py`). Both the registry doc and the actual ignore file are now correct. The Video Editor domain graph was then built for the first time (previously "pending build" since project inception): 391 nodes, 359 edges, 117 communities, 63.5x query token-reduction.

### 2026-08-08/09 — POV Shorts Pipeline v2 Locked In; Roman Gladiator + Titanic Stoker Published; Real Third-Party API Limits Discovered

v2 (`001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline_v2/`) went from "proof-of-concept, do not treat as locked" to a fully hardened, test-covered pipeline this session (126/126 tests), validated end-to-end on two real productions from image generation through publish: Roman Gladiator (0005) and Titanic Stoker (0004, shots 2/9/13 regenerated).

**Sheet-driven architecture, now locked:** Main/Featured-Extra/Background Character Sheets, Prop Sheet (front/back/held-from-POV, split into `held_left`/`held_right` — a generic single `held` panel let the model guess grip laterality and got it wrong), and per-location/per-scene Environment Sheets (strictly people-less, never merged across scenes) all get attached WHOLE as `input_urls` at the image-generation stage, referenced by label in prompt text — never cropped out of a sheet. This is the only proven-working reference pattern across two full test productions.

**Confirmed live, corrects a prior wrong assumption: kie.ai's `bytedance_seedance_video` endpoint rejects `first_frame_url` and `reference_image_urls` together** ("The reference image and the first and last frames are mutually exclusive, and only one scene can be selected"). A 2026-08-06 architecture note assumed both could combine (first_frame_url anchoring composition, reference_image_urls carrying character consistency) and was never tested end-to-end until a real 13-shot batch failed on it. Fixed in `video_generation.py` — `submit_video_task`/`generate_video` now raise `ValueError` if both are passed. **The correct mental model, per Tony's direct correction: once the sheet-driven image stage has produced a scene's correct starting image, that image alone is the video-generation reference — don't re-attach the original sheets "for consistency," it's redundant and, on this endpoint, rejected outright.**

**Video-prompt content rule, backed by real image-to-video prompting research:** describe motion/camera/sound only in the video-generation prompt — never re-describe pose or hand laterality already established in `first_frame_url`. Re-describing static details risks diluting the motion instruction or conflicting with what the frame already shows.

**Hand/limb laterality is a real, distinct, confirmed failure mode** for any first-person or multi-character prompt (image or video generation) — screen/camera-relative language ("left of frame") is unreliable; anchor to the character's own anatomy (which shoulder/arm) instead. Attaching reference images can make laterality *worse*, not better — a known, cross-platform model limitation, not a one-off bug. Full research and the fix pattern: `Seedance-Prompting-Guide/SKILL.md` → "Hand/limb laterality in POV and multi-character shots."

**Fixed a real Remotion truncation bug:** the `POVShort` composition in `003_Remotion/src/remotion/Root.tsx` hardcoded `durationInFrames={1560}` (65.0s @ 24fps) — any production whose actual assembled video ran longer got silently truncated (the final caption and true ending cut off). Fixed with `calculateMetadata` reading `props.durationInFrames`, now always supplied by `text_overlay.py`'s `measure_video_duration_seconds()` against the real `Final_vN.mp4`, never assumed.

**Third-party API limits worth remembering, all discovered by a real call failing (not documented anywhere until hit):** Suno's `--customMode false` prompt field caps at 500 characters (vs. up to 5000 in custom mode) — keep music-mood prompts concise. Instagram caps at 5 hashtags per post (already noted 2026-08-03, reconfirmed). Before relying on a third-party API's parameter combination, sort order, or limit for the first time, check `--help`/schema output for explicit constraints or make one cheap real call to confirm — several of this session's real bugs trace to trusting what an interface merely *allows you to pass* rather than what it actually *supports in combination*.

**New standing workspace rule:** before overwriting any existing generated asset (image or video) with a corrected regeneration, move the old file into a sibling `Rejected/` folder first — never silently replace in place. Applies workspace-wide, not just Reimagined Realms.

**YouTube Data API gotcha:** `search.list?order=viewCount` is an approximate/algorithmic ranking, not an exact sort — it silently dropped a real top-10 video by view count. For an accurate ranked list, pull the full channel's uploads playlist (`channels.list` → `contentDetails.relatedPlaylists.uploads` → paginated `playlistItems.list` → batched `videos.list` for `statistics.viewCount`) and sort exactly, rather than trusting the search endpoint's ordering.

### 2026-08-10/15 — Seedance Case Study Pipeline, Video-Analyzer Upgrade, POV Pipeline Bug Diagnosis/Fix

**Ingest skill now asks a scope question before a generic "ingest" trigger** (`001_Architecture/Skills/ingest/SKILL.md`): top-level only (new default) / everything incl. subfolders / a named subfolder / choose files / freeform description. Previously defaulted to recursing into every subfolder automatically, which Tony didn't want for plain "ingest the files in ingest" requests.

**New shared case-study location:** `002_Content-Creation/Video_Editor/002_Channels/Universal_Case_Studies/` — for case studies not specific to one channel (as opposed to a channel's own `Case_Studies/` folder). Holds 10 Seedance/AI-video tutorial case studies from the Seedance Case Study Pipeline (full plan in Claude memory `project_seedance_case_study_pipeline.md`).

**Video-Analyzer skill (`001_Architecture/Skills/Video-Analyzer/`) substantially upgraded, twice this session:**
1. Added local FFmpeg full-resolution scene-cut keyframe extraction + local Whisper transcription (both free, no API cost) alongside the existing Gemini native-video pass — Gemini alone reads on-screen text/prompts/settings unreliably at its default video-sampling resolution. New mandatory step: the invoking agent must read the extracted keyframes itself, not just rely on Gemini's description of them.
2. Added a second, denser `--dense-interval` extraction mode (fixed-interval frames, e.g. every 0.5-1s, regardless of scene cuts) specifically for continuity/fault auditing. The default scene-cut keyframes have a real blind spot: a defect that drifts gradually within one continuous shot (no hard cut) falls through the gap between two scene-cut keyframes entirely — this is exactly how a real POV-to-third-person camera break on the Pyramid Builder production went undetected until dense-interval frames were pulled.

**Seedance-Prompting-Guide skill restructured into Core + 5 production-style framework** (POV, Cinematic Narrative/Multi-Character, Documentary, UGC/Talking Presenter, Portal/Transition), each section stating plainly which pipelines actually use it today (only POV currently does). Heaviest new content — a real, verbatim "AI Filmmaking Bible" Variant A/B/C prompt-template system (dynamic `@image` renumbering rules, audio-default policy, dialogue-in-timeline convention) — lives in a new supporting file, `Cinematic-Narrative-Multi-Character.md`, kept separate from the main `SKILL.md` to stay token-lean per superpowers:writing-skills guidance (heavy reference material belongs in a linked sibling file, not the main skill).

**POV Shorts Pipeline v2 — real bug found and fixed, `POV_LOCK_CLAUSE` (duplicated in `shot_list_builder.py` AND `storyboard_generation.py` — the latter is the consequential copy since this pipeline locks visibility at the first-frame image stage):** the clause had over-corrected into mandating hands/forearms/chest-down body be *always* visible in every single shot, instead of only banning what's physically impossible to see. Confirmed on Roman Gladiator (near-constant limbs regardless of gaze direction). Fixed to a negative-constraint rule: never show own face/back-of-head/shoulder/back; everything else depends on the scene's actual action. `POV_Style_Guide.md` checklist grown to 10 items with a new "pose-change-within-a-shot" check (split any big pose change into two generations with a last-frame handoff — Pyramid Builder's opening lying→sitting shot drifted into third-person mid-generation, visually confirmed via the new dense-interval keyframes). 126/126 tests still passing after both fixes.

**Process lesson, logged in Feedback_Loop/2026-08-15:** a "confirmed as a real failure mode" citation in `POV_Style_Guide.md` had no basis anywhere in git history/session logs/feedback loop — caught by Tony, corrected. Verify any "confirmed failure" claim against actual logs before citing it as fact, whether the source is a web search or an internal skill/doc file.

**Tony's stated long-term roadmap for the POV Shorts pipeline:** manual iterate → critique → publish → critique loop until output quality is consistently ~99%, then transition to scheduled/autonomous mode (auto topic discovery, script, generation, publish) gated only by a lightweight Airtable/spreadsheet yes/no on proposed ideas — not full manual production. Currently in phase one.

### 2026-08-17/18 — Anomalous Wild (Mantis Shrimp Color Vision): Seedance Reference-Image Behavior Confirmed Live, kie.ai Market API Gap-Fill Wrapper Built

**Seedance 1.5 Pro has no style/consistency reference slot — its second image parameter IS the last frame.** On kie.ai, `bytedance/seedance-1.5-pro`'s `input_urls` array maps directly to `image`/`last_image`: element 0 = first frame, element 1 = last frame (interpolation target), full stop. Passed a character sheet as a second image expecting it to act as an anatomy/identity reference; instead the video literally morphed into and ended on a static shot of the character sheet grid — reproduced identically on a second attempt with different prompt wording, proving this is parameter behavior, not something prompt text can fix. Full detail and the corrected version-parameter tables now live in `Seedance-Prompting-Guide/SKILL.md` (new top-of-section warning callout) — **this was already partially documented there** (the "Character consistency across shots" table already stated 1.5 Pro's single-reference limitation from an 2026-08-04 finding) but wasn't checked before repeating the mistake; the skill is now updated to make this unmissable, cross-referenced from the version-parameters table directly instead of only the consistency-specific subsection.

**Seedance 2.0 (standard, not just Fast) confirmed to genuinely support both a starting-composition reference AND multi-reference identity/anatomy sheets in one call**, via `reference_image_urls` (up to 9 images, separate array, distinct from `first_frame_url`/`last_frame_url` — already known-mutually-exclusive with those per the 2026-08-08 finding above) plus `@Image1`/`@Image2` ordinal tagging in the prompt. **Practical implication for any pipeline: which Seedance version a pipeline targets is not a drop-in swap — it changes how many reference images to build at the image-generation stage and what each one should contain**, not just which API parameter name to use. 1.5 Pro needs identity solved earlier (single composited starting image, or reuse one anchor image per call); 2.0 can carry a real character sheet + environment sheet + storyboard panel all the way into the video call itself.

**Root cause of a second, separate defect (unprompted narration) on the same 1.5 Pro calls:** a documentary-style prompt (e.g. "National Geographic documentary lighting") can bias `generate_audio` toward generating a spoken narrator voiceover even with explicit "no dialogue/no narration" negative-prompt language present — confirmed reproduced twice with different negative-prompt phrasing before it actually resolved. Fix that worked: strip genre-signaling style language from the sound-brief portion of the prompt, use only concrete named foley/ambient events, and close with this guide's exact dash-led negative-prompt line. Both fixes (single reference image + corrected audio-prompt structure) confirmed working together in one call before this was written down.

**New workspace tool: `kie_market_api.py`** (`001_Architecture/Tools/Video-Generation/Generic_Tools/`) — a thin wrapper around kie.ai's unified Market API (`/api/v1/jobs/createTask` + `/api/v1/jobs/recordInfo`) for models the third-party `@felores/kie-cli` npm package doesn't wrap yet (confirmed gaps as of 2026-08-17: `bytedance/seedance-2-mini`, `topaz/video-upscale`; NOT a full CLI replacement — kie-cli stays the default, this only exists for gap models, extend it one function at a time as new gaps appear, per Tony's explicit direction). Also fixed a real bug in its own `create_task()`: kie.ai returns HTTP 200 even for API-level failures (insufficient credits, bad params) — the real status is in a `code` field in the JSON body, not the HTTP status; checking only `resp.ok` produces a confusing `NoneType has no attribute 'get'` crash instead of the actual error message.

**kie-cli version regression found and reverted:** upgrading `@felores/kie-cli` from 0.2.0 → 0.4.0 (attempting to pick up Seedance Mini support) did not add Mini or a working video-upscale tool, and silently dropped the `--mode standard/fast` selector on `bytedance_seedance_video`, defaulting instead to Seedance 2.5 only — a real risk of silently changing pricing/model tier for every existing pipeline using that flag. Reverted to 0.2.0. Lesson: verify a dependency upgrade actually delivers the capability gap it was meant to close before keeping it, and check for regressions in existing flags, not just new features.

**Confirmed dead end, do not retry: Grok Imagine's `grok-imagine/upscale` endpoint only accepts a `task_id` from Grok's own video generations** — despite doc prose implying "any Kie AI video generation model," a real test against a Seedance-generated `task_id` was rejected with `{"code":422,"msg":"record result error"}`. `topaz/video-upscale` is the correct tool for upscaling non-Grok video — it takes a direct `video_url`, not a scoped task_id, confirmed working. (Per-second Topaz pricing still makes it more expensive than generating natively at a higher resolution in most cases — check `tm cost`-style math before defaulting to the upscale-from-cheap-tier path.)

### 2026-08-18 — Diagram-Animation Beats: Seedance Confirmed Wrong Tool, Component-Asset + Remotion Compositing Is the Fix (Tony-graded "A+")

**Seedance 1.5 Pro fails harder on abstract/diagram content than on organic creature content — confirmed via a real side-by-side test on the same production.** Given a correctly-built start frame + end frame (both grounded on the real diagram illustration, matching the storyboard's actual panel 1 and panel 8 compositions), Seedance 1.5 Pro still morphed the mantis shrimp's photoreceptor-fan diagram into an unrelated metallic/mechanical structure within ~2 seconds and never converged back onto the real end frame by the clip's end — a worse failure than the creature-drift case documented 2026-08-17/18 above. Root cause read: diagram/data-viz content gives a video-generation model far less to anchor identity on than a recognizable creature does, so it drifts faster and further.

**The fix: stop trying to get Seedance to animate diagram content at all.** Generate each distinct visual element as its own clean, isolated static image asset (`Diagram-Generation` skill's already-documented "Approach B" — component assets first, then assemble), then composite/animate them in Remotion with keyframed opacity/scale/position tied to the beat's real narration timestamps (crossfades, push-ins, pull-backs — matching the storyboard's own reveal sequence). Result: zero drift by construction, since no frame content is ever regenerated — verified by extracting frames across the full render and confirming pixel-exact matches against the original storyboard panels at every beat boundary. **This should now be the default assumption for any diagram/motion-graphics-style beat, not a fallback reached for only after a failed Seedance attempt.**

**Compositing detail worth keeping: true alpha mattes, not mix-blend-mode tricks.** Isolated assets generated with a prompt like "on a solid near-black background" are NOT truly transparent — crossfading them with plain opacity shows a visible seam, and even `mixBlendMode: "screen"` (which hides the *hard* seam) still leaves a faint residual line because the baked background isn't literally pure black. The real fix: run each asset through `kie-cli recraft_remove_background` (Recraft's AI matting model, confirmed to produce true `RGBA` output), then composite with plain alpha (no blend-mode hack — screen mode would incorrectly wash out any moment where two subjects legitimately overlap on screen at once).

**Update — 2026-08-18, later same day: built and shipped.** Full spec: `001_Architecture/Superpowers/Specs/2026-08-18-Motion-Graphics-Compositing-Skill-Spec.md`. New skill: `001_Architecture/Skills/Motion-Graphics-Compositing/SKILL.md` — channel-agnostic, living reference (grows via case-study ingestion, same pattern as Seedance-Prompting-Guide). `Diagram-Generation`'s Approach B now delegates its asset-isolation + compositing mechanics to it; Anomalous Wild's Phase 6B Step 5 now defaults to Approach B over Approach A for diagram beats.

**Key additions beyond the original test:**
- **Asset generation method order** (try in sequence): (1) native transparent background via direct OpenAI GPT-Image-2 API (`background: "transparent"` — NOT exposed by kie.ai's CLI wrapper; not yet live-tested, Tony will test on the next real diagram beat, do not test speculatively), (2) green/blue chroma-screen background + Recraft AI matting (robust default), (3) near-black background + Recraft matting (last resort, what Scene 02 actually used).
- **Style-lock rule is conditional, not universal:** required when components are pieces of one unified illustrated subject (share one reference image + style block); does NOT apply to collage/mixed-media motion graphics (e.g. Vox-style pieces with genuinely heterogeneous materials — newsprint, torn paper, halftone type) where style variety is intentional.
- **Reusable building blocks, not a rigid compositor:** `kf()` keyframe helper + named animation-preset functions (`crossfade`, `pushZoom`, `pullBackReveal`, `sideBySideHold`, `explodedAssembly`; `lineTraceReveal` stubbed) in `002_Content-Creation/Video_Editor/003_Remotion/src/remotion/video-lib/motion_graphics_presets.ts`. Every production still hand-assembles its own composition from these — no one-size-fits-all data-driven template, since assets/timing/pacing genuinely differ every time.
- **Audio: reused the existing mechanism, no new tool built** — `generate_foley.py`/`foley_config.py` (Mirelo/Sonilo video-to-SFX, already built for Reimagined Realms POV Shorts). Confirmed working on Scene 02's render after compressing the source clip first (wavespeed's upload aborted on the full 17.5MB/1080p file, succeeded at 687KB/960px — exact size threshold not identified, compress first if a video-to-X API call fails with "operation was aborted"). **Found: Mirelo capped its output at 5.0s against an 11.05s input, no error/warning** — check documented max duration, or try the `sonilo` alternative, before relying on it for beats longer than ~5s.
- **Asset library:** per-production `Production/Motion_Graphics_Asset_Library.json` + cross-production master wiki index at `000_Wiki/Video-Production/Motion-Graphics-Asset-Library.md` (graphified for retrieval — auto-updates via the Stop hook, no manual graphify run needed).

**Separate, important fix triggered by this build: Tool-Manager capability-parity gap.** Tool-Manager's `model_catalog.json` only tracked price parity across platforms, not feature/capability parity — this is exactly how the kie.ai-vs-direct-OpenAI transparency gap got missed in the first place (kie.ai is cheaper for GPT-Image-2, $0.03 vs $0.04/image, so it "won" on the only axis being checked). Added a `capabilities` block to the catalog schema (start: `gpt-image-2` entry, `transparent_background_output` per platform) and updated Tool-Manager's own routing rule to check capabilities before price. **Standing process correction, direct from Tony:** consult Tool-Manager before defaulting to any platform/endpoint, unprompted — and when Tool-Manager's own data doesn't cover the actual question, tell Tool-Manager to research and update itself via its Update Protocol, don't surface an unresearched question back to Tony.

### 2026-08-19/22 — Mantis Shrimp Production: Full Scene-by-Scene Pipeline Test, First Complete Assembled Video, New Grading Convention

Multi-day session (Aug 19–22) running Anomalous Wild's `0002_Mantis_Shrimp_Color_Vision` scene-by-scene as an explicit pipeline validation pass (Tony's framing: work one scene at a time, review each, build toward ~95% confidence before more autonomous batch generation). Ended with the production's first fully assembled video.

**New standing rule — grade every finished video.** Every completed production gets a letter grade logged in that production's `Data/Report_Card.md` (already has the right frontmatter fields — use them) to build a self-learning database over time. First graded video: `0002_Mantis_Shrimp_Color_Vision` FINAL_v1 = **B-/B** — individual scenes graded much higher (A- to A+) during production; the gap was the final assembly method, not the generated content. Do this automatically at the end of every production going forward, on any channel, not just when asked.

**Storyboard-vs-shot-list reconciliation is now a standing pre-check.** Found repeatedly this session: `Shot_List.md` entries that predated their real storyboard (or predated a rule like Approach B being locked) drift out of sync with the actual storyboard content. Standing rule: the storyboard is the source of truth — check it against the shot list before generating anything for a scene, rewrite the shot list to match if they disagree, never the reverse.

**New locked rules, all written into the relevant skill files (not just noted here):**
- **Clip-boundary heuristic** (`Production-Asset-Planner/SKILL.md`): a clip's boundary is decided by "can one prompt + one start frame + one end frame plausibly produce this, in ≤~8s?" — not a fixed duration split. Sequential lettering (A/B/C/D...) spans a whole scene's segments, generated and B-roll together, not separate tracks. B-roll now saves into `Video_Clips/<Scene>/`, not a separate `B_Roll/` folder.
- **Start/end frame distinctiveness + reference chaining** (`Seedance-Prompting-Guide/SKILL.md`, `Production-Asset-Planner/SKILL.md`): a clip's start and end frame must be visually distinct (near-duplicate framing gives Seedance nothing to interpolate motion from), and an end frame must be generated using the start frame as an input reference, not just the storyboard panel alone — otherwise the two frames can independently invent different environments. Caught live on Scene_03E: a close-up start frame (near-empty dark background) and an independently-generated wide end frame (invented dense boulder field) produced a clip where the background visibly changed mid-motion. Fixed by regenerating the end frame with the start frame as a reference image.
- **Chroma-green matting fails on translucent/glowing assets** (`Motion-Graphics-Compositing/SKILL.md`): works cleanly on opaque subjects, but visibly color-contaminates translucent/glowing ones (confirmed on Scene 05's light-wave diagram assets — an amber wave read back yellow-green after chroma-green + Recraft matting). Fix: use near-black background for translucent/glowing components specifically, chroma-green for opaque ones, within the same style-locked asset set. Caught by compositing the matted result over an actual checkerboard test pattern — not by eyeballing the RGBA file, which looked fine.
- **Diagram beats without real animation get the Approach B treatment retroactively.** Scenes 05 and 05B had flat static illustrations sitting unanimated since an earlier session (before Approach B was locked as default). Both got the full component-asset + Remotion-compositing treatment this session, choreographed to real narration timestamps, same pattern as Scene 02.

**Deliberate visual variety across scenes, without changing the creature itself.** Tony wanted scenes to feel visually distinct (not repetitive) and initially floated varying the mantis shrimp's own skin color by "water temperature" — checked the biology first (confirmed via web research: *Odontodactylus scyllarus* is exclusively a shallow tropical reef species, no documented cold/warm-water color morph) and recommended varying water atmosphere/lighting instead, creature coloration held constant for character-sheet continuity. Result: Scene 03 = dark neutral, Scene 04 = warm shallow-tropical (turquoise, visible caustics), Scene 06 = cooler blue-violet dusk. **General principle:** check facts before a creative call that could read as a claim about the real world, and default to varying atmosphere/environment over the documented subject when visual variety is wanted.

**Final assembly used direct ffmpeg concat + audio mix, not the documented Remotion master-composition (Phase 7).** Tony's ask was literally "I just want to see the final video" — built: upscale all 720p clips to 1080p, concat all scenes in narrative order, build narration track from all scene audio files, generate a new Suno score sized to runtime, mix per the channel's locked LUFS/sidechain formula (narration -14 LUFS, music -26 LUFS sidechain-ducked under narration, ambient/native clip audio -20 LUFS), append the locked end card. This is very likely why the full video graded B-/B while every scene graded A-range individually — gap is presentation/polish (title cards, lower-thirds, proper Remotion authoring), not content. **Open question for next session:** does this channel's standard going forward use a real Remotion composition per production, or is a direct assembly acceptable when Tony just wants a quick look? Ask explicitly rather than assuming.

### 2026-08-23 — Mantis Shrimp: Retroactive Research Pass + Video Review + B-Roll Removal Plan (session paused mid-edit)

Follow-on session to 2026-08-19/22 above. Tony asked to run the Production-Research-Agent skill retroactively on `0002_Mantis_Shrimp_Color_Vision` (it was never run originally — this production was built by manual scene-by-scene iteration) purely to see what it surfaces, no editing yet. Full research now sits in the production's `Research/` folder: `Topic_Facts.md` (color-vision + punch-mechanic facts, sourced), 6 new reference images (5 real photos + 1 CC BY-SA scientific eye-anatomy diagram from Wikimedia), 6 new Pexels video clips added to `Pexels_Inventory.json` alongside the 2 already there.

**Real finding worth remembering: Pexels has almost no distinct "mantis shrimp" B-roll — nearly all landscape 1080p results are one contributor (JUN HO LEE) shooting the same single dive/individual/brain-coral landmark, just split into multiple listings at different trim points.** Only 2 of 6 downloaded clips are genuinely distinct footage (a close chase-POV over algae rock, and a 15s wide establishing shot with open water — the strongest one). Logged plainly in the inventory rather than presented as 6 unique sources — check this before assuming Pexels B-roll variety exists for a species this narrow.

**Video-Analyzer skill was run against a local file, not a YouTube URL — the skill's script only supports `yt-dlp` download.** Worked around it by copying the local MP4 to `Video.mp4` in the output folder and calling the script's own internal functions (`detect_scenes`, `analyze_video_narrative`, `extract_keyframes`, `transcribe_with_whisper`) directly via a Python one-liner, skipping only `download_video()`. This is a real gap in the skill for analyzing in-house-produced videos, not just external references — worth fixing in the skill itself if this need recurs.

**Analysis found a real biology/continuity error in the finished video, confirmed by pulling the exact frames**: at 1:32–1:37 the mantis shrimp has a single, centrally-fused giant raptorial appendage (biologically wrong — they have a bilateral pair), and at 1:43–1:46 that appendage morphs mid-strike into a toothed lobster/crab-style pincer, a completely different mechanism. Scene 16 (1:59) shows the same animal with the correct paired appendages 13 seconds later, so the contradiction is visible to any attentive viewer. **Tony's call: not worth fixing** — this channel's mantis shrimp video is entertainment-first, not strict science, so he explicitly declined the fix despite the confirmed error. Record this as a real preference, not an oversight: don't push scientific-accuracy fixes on this channel once Tony has reviewed and accepted a cut.

**Tony does want the two stock B-roll cutaways removed** (a generic reef fish at ~22.5s, a cleaner shrimp at ~26.2s, both inserted into the "each eye moves independently" narration beat, `Production/Beat_Table.json`'s `scene_03`, 12.492s total) — he doesn't like that they're visually different creatures breaking continuity. Confirmed via `ffprobe` that this is fully recoverable: the beat's three generated clips (`Scene_03A/03C/03E`) were rendered at ~4.06s each by Seedance but trimmed down for the original cut (to 3.75s/2.50s/3.75s) — restoring them to full raw length recovers 2.20s of the 2.49s the B-roll inserts occupy, leaving only a ~0.3s gap (closeable with a freeze-hold on the last frame or a longer crossfade). Visually verified Scene_03C's full raw clip holds up clean to the end — no artifacts, and it shows more of the actual eye-stalk movement the beat is about, so extending it is safe. **This is the concrete next step, not yet executed** — Tony ended the session before confirming to proceed with the rebuild.

**Next session should pick up exactly here:** rebuild `scene_03` in the assembly — drop `Scene_03B_BRoll_ReefFish.mp4` and `Scene_03D_BRoll_SmallShrimp.mp4`, re-cut `Scene_03A/03C/03E` from their `Video_Clips/Scene_03/Raw/` originals at full ~4.06s length, close the remaining ~0.3s gap with a hold/crossfade, and re-render the affected portion of `Assembly/0002_Mantis_Shrimp_Color_Vision_FINAL_v1.mp4`. No other scenes are affected — the B-roll problem is confined to `scene_03` only.

### 2026-08-23/24 — Mantis Shrimp: B-Roll Rebuild → Scene 05/05B Overlay Build → Grade A (full arc, five candidate versions)

Direct continuation of the entry above. B-roll rebuild executed as planned (freeze-hold pattern confirmed correct, graded B+/A-). Then a much larger arc: added grounded labels/arrows to the wave-polarization diagram, replaced a factually-wrong human-eyeball asset with a live-action mantis-shrimp clip, replaced a static signal-code inset with a full-bleed animated version, fixed an abrupt audio cutoff, and added an end-card CTA voiceover. Landed at grade A after five candidate versions (`FINAL_v2` through `FINAL_v5`) — full iteration-by-iteration table (what was liked, what wasn't, why) is in `Data/Report_Card.md` for this production; don't duplicate it here.

**The durable, cross-production lessons from this arc (all written directly into governing skill files, not just logged):**

- **Grounded ≠ well-laid-out.** `detect_label_coordinates.py`-detected coordinates were factually correct but still produced off-screen and overlapping labels — coordinate accuracy and on-screen layout quality are separate checks. `Diagram-Generation` SKILL.md now has a label-layout-safety checklist (edge margin, negative-space text placement, real-render verification) as a direct result.
- **Static mockups before a Remotion re-render** — Tony's own suggested fix when the first label pass missed — is now standard practice in `Diagram-Generation` SKILL.md: draw the proposed layout on a real extracted frame, get sign-off, only then touch the actual component.
- **Use the real existing asset as the generation reference, never a verbal description of it.** A "make this full-bleed" request against an existing glyph-grid asset got regenerated from a literal reading of Tony's casual description ("zeros and ones") instead of using the actual file — produced a visually wrong result. Now called out explicitly in `Diagram-Generation` SKILL.md.
- **Audio QC method fixed:** `ffmpeg -af astats` parsed via shell grep gave silently wrong (identical) readings across different timestamps — switched to raw-PCM WAV extraction + numpy RMS, which is now the locked method in `Anomalous_Wild_Video_Pipeline` SKILL.md's new mandatory pre-delivery audio-continuity scan.
- **"The very end of the audio" can mean a different timestamp than "the very end of the video"** when a silent card/tail follows real content — verify where audio content actually stops before assuming it's the file's last frame.
- **Anomalous Wild end cards now get a spoken CTA VO by default** (ElevenLabs, same voice_id as the production's narration), mixed in with its own fade — was previously silent-by-default under the visual "Like, Comment" text. Standard step now in `Anomalous_Wild_Video_Pipeline` SKILL.md Phase 7.
- **Seedance default corrected to 1.5 Pro, even on kie.ai** — a substitution to 2.0 (justified at the time by the workspace's general "always use latest" rule) was explicitly overridden by Tony; 1.5 Pro isn't exposed by kie.ai's `bytedance_seedance_video` CLI command (that's 2.0-only) and needs a direct `POST /jobs/createTask` call with `model: "bytedance/seedance-1.5-pro"`.

**Tony's explicit ask behind capturing all this:** every video, on every channel, should need progressively fewer correction rounds over time, working toward pipelines that run with minimal/no intervention. His estimate: this video needed roughly 50% human-driven iteration to reach an A. The mechanism for actually reducing that on future productions is writing the lesson into the *skill file that governs the step*, not just a memory note — skills get followed automatically on the next run, memory only gets consulted contextually.

### 2026-08-24 — Mantis Shrimp: Thumbnail Template v2 Locked (darkened-bg + glow + auto-headlines), Pipeline Wired

Same-day follow-on, after the Report Card/close-out entry above. Tony asked for the YouTube thumbnail/title/description package, revealing that Phase 9's `generate_youtube_package.py` had never actually produced a finished (text+arrow) thumbnail — it only generates textless base concepts (`build_thumbnail_prompt()` explicitly says "no text, no captions"). First attempt to add text/arrow used PIL with hand-guessed pixel coordinates for the subject's eyes — arrow landed on the neck joint instead of the eyes, and one arrowhead clipped into the headline text. Tony's correction pointed at the real root cause: check `0001_Bioluminescence_Weapon`'s actual finished thumbnail as a reference before inventing an approach. That thumbnail turned out to have been hand-built in a past session too (never through the script) — but it revealed the right method: composite text/arrow via `gpt-image-2-image-to-image` (image-to-image edit on the base concept), letting the model reason about actual subject edges instead of PIL math against guessed coordinates.

**Iterating from there landed on a locked v2 template** (`002_Content-Creation/Video_Editor/002_Channels/001_Anomalous-Wild/Anomalos_Wild__Thumbnail_Style.json`, replaces the old flat-purple-gradient v1):
- Darken the base concept's **real** background ~50% (not replaced with a solid gradient — a first full image-to-image pass over-corrected and flattened it, which lost per-concept mood variety; Tony's fix was "darken by 50%, don't flatten it")
- Add a neon glow rim-light around the subject, color varied per concept (cyan-teal / amber-orange / magenta-violet for Mantis Shrimp) — Tony's stated goal is brand recognition through *consistent structure* with varied color, not one fixed palette: "when somebody comes to my YouTube page... it's kind of like on brand identity"
- Bold lowercase white headline top-left with ≥8% edge padding, one red curved arrow pointing precisely at the specific anatomy tied to the hook fact (never a generic target)
- **Headline copy is now auto-generated by Claude every production, no Tony review required by default** — he explicitly approved this after seeing the quality of this session's headlines ("colors we can't see," "these eyes shouldn't work," "it sees 16 colors"). Python string templates are explicitly not trusted for this (produced weak copy earlier this same session, needed manual rewrite) — the orchestrating Claude session must draft the 3 headlines + arrow-target itself and pass them to the script.

**Pipeline is now actually wired, not just documented:** `generate_youtube_package.py` rewritten to run both stages automatically per call (base concept generation → Cloudinary upload → image-to-image treatment edit), taking `--headlines` (3, pipe-separated) and `--arrow-target` as required-quality CLI inputs. `Anomalous_Wild_Video_Pipeline` SKILL.md Phase 9 updated to instruct drafting those inputs before calling the script, and to visually inspect corners for stray watermark artifacts (kie.ai's image-to-image occasionally adds one — happened once this session, fixed by regenerating with an explicit "no logo/watermark" instruction appended).

**Meta-note reinforcing the standing pattern above:** Tony framed this explicitly as a self-learning-loop test case — "this is the kind of thing I'm hoping your self-learning abilities are able to do for me in the future... if everything could be executed as well as this process, that would be great." The mechanism that made this actually stick: locked the finding into the JSON template *and* the generator script *and* the SKILL.md, not just this memory file — so the next Anomalous Wild production gets the treatment automatically rather than needing this same conversation to happen again.

### 2026-08-25 — Anomalous Wild Pipeline v3: Full Retrospective → Plan → Implementation → Live Merge (0002 Mantis Shrimp arc closes out)

Tony ran a structured, question-by-question retrospective (brainstorming skill, retrospective-only mode) on the whole 0002_Mantis_Shrimp_Color_Vision production, working through the 36-item iteration/manual-override log built earlier this session (`Anomalous_Wild_Video_Pipeline/Mantis_Shrimp_Iteration_Log.md`) to decide, per item, what should become a locked pipeline standard vs. stay a one-off. This is the closing chapter of the Mantis Shrimp arc documented in the entries above.

**Decisions locked (now live in `Anomalous_Wild_Video_Pipeline/SKILL.md` and code, tagged `anomalous-wild-pipeline-v3-2026-08-25` on `main`):**
- **Intake questionnaire reduced from 8 questions to 2** (Format, Duration only). Channel selection, narration on/off, voiceover tone, music mood, Suno toggle, and CTA text are all now locked defaults in `new_video.py`, never asked.
- **ElevenLabs voice `KYhuk3Y57IlkV1ZjtDAt` formally locked** as the permanent Anomalous Wild voice (was being reused across productions but never actually declared locked in docs — same treatment as Reimagined Realms' hardcoded voice now).
- **CTA reduced to 3 fixed rotating lines**, picked at random per production, never typed fresh: "Subscribe for more wild animal facts." / "Follow along for more strange creatures like this one." / "Hit subscribe — nature gets weirder from here."
- **Seedance 1.5 Pro (1080p, kie.ai) is the real locked default** — was documented as default but `pipeline_supervisor.py` had zero Seedance code path (silently fell through to Kling for any Seedance-labeled beat). `generate_seedance()` now added, mirroring `generate_veo3`/`generate_kling`'s structure exactly. No fixed backup chain — switch models per-beat as needed, not via a pre-set fallback order.
- **No single assembly tool is mandatory.** Remotion, ffmpeg, video-use, HyperFrames — whichever suits a given job does that job; diagram scenes can be built independently (component assets + Motion-Graphics-Compositing) and stitched in regardless of what assembled the rest. This directly resolves the "final assembly used direct ffmpeg, not documented Remotion" gap noted in the 2026-08-22 entry above — Tony's answer was to formally drop the Remotion-mandatory rule rather than force every production through it.
- **Visual variety mechanism added**, addressing the "AI slop" repetitive-shot feeling Tony flagged: fixed universal pool (camera angle: wide/close-up/medium/low/high/macro; framing: centered/rule-of-thirds/negative-space/tight/depth-layered) rotates every shot; environment/lighting/subject-variation is NOT a fixed list, decided per-production by the director from real research (Production-Research-Agent), explicitly wired to Case Studies + the Cinematic Style Guide as craft inspiration (not a template to copy). The director persona (BBC-style nature-documentary) is meant to make these calls autonomously — Tony reviews finished videos to refine the "eye," not per-shot choices.
- **NotebookLM added as an optional research-phase step** (briefing-doc report, not diagram generation — that capability doesn't exist in NotebookLM, was a misremembering) — skip-and-proceed if unavailable, never blocks the pipeline.
- **Continuity/anatomy-flag cost control:** when a review flags a possible issue, do NOT auto-regenerate via Seedance/Veo (real cost risk on possibly-nonexistent issues — flagging itself proved unreliable this session, a flagged claw-continuity error turned out not to be visible on review). Log to `Production/Continuity_Flags.md`, defer to Tony. Explicit training-phase framing: expect to review flags like this for roughly the next 15 productions, then relax as the pipeline proves reliable — same "review now, earn autonomy later" principle as the mockup-review step logged in the 2026-08-23/24 entry above.

**Process notes worth remembering for future large implementation passes:**
- Isolated worktree + subagent-driven-development (11 tasks, each independently reviewed) + a final whole-branch review on the most capable model caught real cross-task issues no single task's scoped review could see — most notably a real cost bug (native audio generated and paid for on every Seedance clip, but the doc still gated the extraction step on "Seedance 2.0+" so it never actually got used, while ElevenLabs ran redundantly for the same stem).
- `main` had 312 uncommitted files (spanning the whole workspace) and a pre-existing `anomalous-wild-pipeline-v1` git tag from 2026-07-08 (original pipeline build) that was nearly overwritten. Resolved: committed everything on `main` as its own checkpoint first (Tony's call — preserve, don't discard), tagged pre/post-update state as `v2-2026-08-25`/`v3-2026-08-25` to avoid the collision, merged, pushed both commits and tags to GitHub. One real merge conflict (the CTA paragraph) resolved by keeping the fully-reviewed branch version.
- **Open/deferred, not part of this update:** `pipeline_supervisor.py` has pre-existing hardcoded `/tmp/biolum_*` paths (cloned from the bioluminescence-weapon script), flagged by `validate_build.py`, out of scope for this plan. Tony asked to be reminded of this at the start of the next session.

### 2026-08-26 — Cross-Iteration Learning Rule

Tony expects repeated positive and corrective feedback to be generalized
proactively into reusable skills, contracts, prompts, checks, or routing logic.
Do not leave detailed lessons isolated in a case study or reduce them to
generic guidance. Connect iteration results to the governing reusable artifact
without waiting for an additional reminder.
## Iteration Archive Convention

- Tony wants all superseded or denied project artifacts preserved, not deleted.
- This applies to images, prompts, scripts, shot lists, storyboards, metadata,
  audio, video, and renders. Move the old version into the matching project
  `Archived/` folder, preserve its original version number, and assign the
  replacement the next version number. Active folders contain current working
  or approved artifacts only.
### Neon Parcel Default Video Route (2026-08-28)

Tony approved the Neon Parcel default route after direct comparison testing:
use a Neon Parcel storyboard as the visual-continuity reference, generate with
Seedance 2 Mini at 480p, upscale with Topaz 2x, and normalize with FFmpeg to
1920x1080. Tony provisionally graded this route 89 (B+) and the previous mixed
route C-. This applies to Neon Parcel only; Seedance 1.5 remains an explicit
fallback/comparison route, not an automatic choice.
### Active Production Output Audit

Before reporting status on any video production, agents must inspect the
active output folder. Keep only the current version of each shot active;
archive older, superseded, rejected, and test artifacts in the matching
`Archived/` folder, preserving files and version numbers. This audit is
mandatory after generation, revisions, and batch completion.

### Seedance Reference-Role Contract (2026-08-30)

A storyboard/contact sheet is contextual visual-continuity input, not a
temporal start frame. On Seedance Mini calls, send it through
`reference_image_urls`; reserve `first_frame_url` for a clean single-scene
starting state. The shared Kie wrapper and Neon Parcel pre-video gate reject a
storyboard in the frame field or a combined frame/reference payload before a
paid request. Shot 8's bad v1 was caused by this exact routing error and must
not be reused as a valid test.

## 2026-08-28/29/30 — Anomalous Wild 0003 (Glass Frog) full autonomous pipeline run + Remotion edit review (in progress)

Tony ran the Anomalous_Wild_Video_Pipeline fully autonomously end-to-end (his explicit instruction, a deliberate capability test — no per-phase approval). Video is live **private** on YouTube: https://www.youtube.com/watch?v=LiJcg5aUu6I. Full technical detail, current status, and next steps: `002_Content-Creation/Video_Editor/002_Channels/001_Anomalous-Wild/Productions/0003_Glass_Frog_Transparency/Production/RESUME_NOTES.md` — **read that file before touching this production further.**

Durable outputs from this run, relevant workspace-wide:
- New channel-level cost-tracking file: `002_Content-Creation/Video_Editor/002_Channels/001_Anomalous-Wild/Production_Cost_Log.md`. kie.ai credit-to-USD rate confirmed live: **1 credit = $0.005**. Methodology (window-matching real file timestamps against kie.ai usage-export CSVs) documented inside — reusable for any future channel/production cost reconciliation.
- Real bugs found and fixed at the source (not just patched for this one production): `render_outputs.py` was missing a final limiter after `amix()`, letting individually-safe audio layers sum to clipping (+0.1 dBTP against a -1 dBTP target) — fixed for all future AW renders. Seedance's real 4s minimum duration floor is now a documented standing rule in `Seedance-Prompting-Guide` and `Production-Asset-Planner` skills (generate at floor, trim to real target downstream). `pipeline_supervisor.py`'s hardcoded paths were fixed (now takes production folder as CLI arg 1). NotebookLM CLI upgraded 0.3.4→0.8.1 (old version had a session-cookie-recovery bug, `teng-lin/notebooklm-py#865`).
- Systemic finding **now resolved (2026-08-30)**: Remotion's `OffthreadVideo` loops back to a source video's frame 0 (not a frozen last frame) when a Sequence's `durationInFrames` exceeds the source's real length — jarring flash-cuts. Root cause: Phase 7 used planned clip durations instead of real ffprobe-measured ones. Fixed in two layers: (1) GlassFrogDoc.tsx — all scene_04/scene_06 clips relaid in whole frames at `floor(real ffprobe)` via an `F()` helper, synthetic segs absorb slack, scene totals stay locked to audio; verified frame-by-frame. (2) Pipeline enforcement so it can't recur: NEW `.../Channels/Anomalous_Wild/clip_durations.py` — `request_duration(target,model)` = `ceil(target)+1` clamped to model `[4,max]`, `trim_to_target()` head-trims each generated clip to its real beat target and refuses (INSUFFICIENT_FOOTAGE, no output) when the clip is physically shorter than the beat. Wired into `pipeline_supervisor.py`: it now derives the API `duration` itself, trims every clip post-download, records target/real/final per clip in `clip_manifest.json`, and **aborts if any `new_clips_prompts.json` video entry lacks `target_duration_s`**. Planners (Production-Asset-Planner Step 6) now record `target_duration_s` only — no hand-set `generation_duration_s`. 17 tests. Lesson (also in Feedback_Loop 2026-08-30): a "locked" rule that lives only as prose for an agent to follow is not actually locked — move it into a code chokepoint with tests and a hard refuse-to-run.
- Verification discipline reinforced hard this run: caught a subagent silently exceeding its approved scope (generated 9 clips instead of an approved 1-clip pilot), a mislabeled "audio bug" that was actually correct-by-design, and the Remotion loop-back root cause above — all found by extracting and inspecting real frames/files directly rather than trusting agent self-reports. See [[feedback_verify_before_presenting]] in Claude cross-session memory.

### Neon Parcel Storyboard QA Resume Boundary (2026-08-31)

The structured storyboard contract, fail-closed QA evaluator, three-attempt
controller, and validated Seedance handoff are implemented locally and tested,
but the real vision-provider adapter and GPT-Image generation wiring are still
pending. When resuming, first run a no-generation dry run against Shot 6's
existing storyboard v1 and verify that it catches missing subjects, incorrect
gate state, broken chronology, and implausible physics. Do not touch the active
flagged shot outputs or spend generation credits before that check. The eventual
Seedance handoff must preserve verified visual observations from the accepted
 storyboard, not merely restate the original contract.

- Permanent video preservation rule: never overwrite a paid generation or any derivative, even after automated inspection. Assign every new generation, upscale, and normalized output a new version (`v3`, `v4`, etc.) and archive superseded assets in the matching `Archived/` folder so false-positive inspections never destroy recoverable work.
- Storyboard generation must be routed through the structured per-frame contract and QA controller; direct ad hoc image prompts are not valid because they bypass subject-origin, spatial-geometry, chronology, and physics checks. Do not present or hand off a storyboard until its generated image has been checked against the original contract.

### Cross-agent closeout and learning propagation (2026-09-04)

- Feedback files and session logs capture episodic decisions, but durable workflow lessons must also be propagated into the governing skill, pipeline configuration, `TOOLBOX.md`, and executable guards/tests when applicable.
- For Neon Parcel, vision inspection is advisory evidence only. The agent must report concrete storyboard/video findings and ask Tony for the decision; it must never auto-clear or auto-reject, spend the next paid-generation step, or upscale based only on provider output.
- Shot 11 v5 is the current resume boundary: final 1080p output exists and awaits Tony's manual review. Do not advance or process it further until approved.

### 2026-09-03 — Anomalous Wild audio mix + Suno: locked-value changes (Tony, A/B by ear on 0003)

- **AW audio mix formula updated** in `render_outputs.py` (the loudnorm-per-layer approach — NOT static volume multipliers, which drift 5-11 dB). New locked values: narration `loudnorm I=-14` (unchanged, YouTube standard); **music `loudnorm I=-22`** (was -26 — score was too quiet); **sidechain duck `threshold=0.045:ratio=2.5:attack=300:release=600`** (was `0.015:4:150:800` — ducked in too hard/abrupt on every syllable). Also see Claude memory `feedback-audio-mix-formula`.
- **Suno generations: always save BOTH tracks + the prompt.** `generate_suno_music.py` rewritten — the API returns ~2 tracks; it now saves every one as `<stem>_v1.mp3`/`_v2.mp3`, copies the longest to the requested path, and writes a `<stem>_suno.json` sidecar with the prompt/style/taskId/per-track metadata. (Previously it discarded the 2nd track and the prompt was never persisted — a real gap, the 0003 score prompt was lost.)
- **Anomalous Wild score direction:** "modern science documentary" — curious/clear-headed, gentle forward rhythmic pulse (arpeggiated synth + marimba/mallets), warm strings pad, hopeful resolution. NOT solo-piano, NOT dark/mysterious/"mystery-trailer". Restrained enough to sit under VO.

### 2026-09-04 — Anomalous Wild 0003 Glass Frog: final approved (grade A), milestone reference + audio-pipeline changes

- **0003 Glass Frog is the Anomalous Wild GEMSTONE / MILESTONE reference video** — first AW video graded A. Worked example: `Productions/0003_Glass_Frog_Transparency/Production/Milestone_Reference.md`. Published private (Blotato acct 42514): https://www.youtube.com/watch?v=JMn32MmAzWw (replaces the old private `LiJcg5aUu6I`, which Tony deletes manually). Canonical file: `Renders/0003_Glass_Frog_Transparency_FINAL_v2a.mp4`.
- **Video-to-audio SFX is now the AW DEFAULT.** NEW `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/generate_stems_v2a.py` — segments a picture-locked render on scene boundaries (`Data/v2a_segment_map.json`, ≤60s each), runs each through **fal.ai Mirelo SFX v1.6** (`mirelo-ai/sfx1.6/video-to-video`, motion-conditioned, cheap GPU-compute-seconds), crossfade-concats to one bed. `generate_stems.py` (ElevenLabs text-to-SFX) is the **fallback**. Gotcha: the internal segment cut MUST be downscaled/bitrate-capped (`scale=1280:-2 -maxrate 4M`) — a full-res/all-intra segment is ~50× bigger and stalls the fal upload (cost ~1h on 0003).
- **AW audio mix — SFX/ambience level lowered.** `render_outputs.py`: `STEMS_FILTER` `loudnorm I=-25` (was -20) + NEW `STEMS_SIDECHAIN_FILTER` (`threshold=0.06:ratio=2:attack=350:release=700`), wired into `render_final`. Rule: **SFX sits a hair below the music bed** (music -22). Tony, A/B by ear on the 0003 v2a bed. Narration -14 and music -22 + its duck unchanged from the 2026-09-03 values.
- **CTA voiceover level rule (locked).** The end-card CTA VO is ALWAYS normalized to the SAME filter the mix applies to the body narration (`loudnorm=I=-14:TP=-1:LRA=7`) and verified within ~1 dB via `ebur128` — never eyeballed, never a pre-baked `end_card_with_cta.mp4` reused without re-checking. 0003's first CTA render was ~6 dB under the body VO; Tony caught it on the finished cut.
- **NEW consolidated PRE-REVIEW GATE in the AW SKILL** (9 checks: black/white scan, audio-pop gate, audio-continuity scan, per-cut transition verify, clip-vs-VO beat check, generated-clip anatomy pass, CTA-VO level, duration frame-floor, ambience-vs-score balance). Run the whole battery before ANY cut goes to Tony, re-run in full after every re-render. Reason: 0003 took 6 review rounds *past* "it's done", each a defect class an existing-or-missing check would have caught.
- When a video is finished + graded, sync its Shot_List / Timeline_Cut_Map / Report_Card to what actually shipped and mark it the channel reference (done for 0003).

### 2026-09-05 — Graphify: Codex offload is the default for heavy domain builds

- Claude's session rate limit trips on graphify's many-parallel-subagent semantic
  extraction. Hand whole domain builds to **Codex** (`Skill("codex:rescue")` +
  a written spec file) — separate quota, works cleanly, follows the graphify
  SKILL.md fine. Done this way for the Video Editor domain 2026-09-05.
- **`.graphifyignore` case bug (fixed 2026-09-05):** graphify's `_is_ignored()`
  uses Python `fnmatch`, which is case-SENSITIVE on macOS/Linux. Lowercase-only
  patterns (`*.png`) silently pass every `.PNG`. Root `.graphifyignore` now uses
  case-insensitive bracket-class patterns (`*.[pP][nN][gG]`) + a broad image/video/
  audio extension list. Images & video are NEVER graphified — any ext, any case.
  (`.gitignore` was already case-safe via `core.ignorecase=true`.)
- `OpenAI_History/` (accidental 2058-file ChatGPT export in 007_Resource_Library)
  is excluded from graphify until it's properly routed.
- Graph state: Architecture ✅ (2026-09-05), Video Editor ✅ (2026-09-05, via Codex).
  Wiki + Resource Library still pending — Resource Library needs a scoping decision
  from Tony first (3559 files even after exclusions).
- A Claude Agent-tool subagent can't receive async task-completion notifications
  like the primary session — don't nest a "dispatch + wait for notification"
  pattern inside a subagent; it hangs in a re-poll loop.

### 2026-09-05 (evening) — Graphify CLI upgraded to 0.9.55
- The `graphify` CLI package is `graphifyy` (double-y). Upgraded 0.4.2 → 0.9.55 on
  Framework Python 3.13 (`/Library/Frameworks/Python.framework/Versions/3.13/bin/graphify`).
  A stale Homebrew 0.4.23 install was removed — one `graphify` on PATH now.
- The old 0.4.2 CLI lacked `update`/`add`/`extract` subcommands — that was the
  long-standing "skill vs package mismatch". 0.9.55 has the full set:
  `extract` (headless full AST+LLM), `update` (fast AST-only incremental),
  `check-update` (cron-safe), plus `path`/`explain`/`query`/`add`/`watch`/`merge-graphs`.
- Skill copies for claude + codex refreshed via `graphify install --platform <x>`;
  `.graphify_version` marker = 0.9.55. Old skills saved as `SKILL.md.bak` per dir.
- Existing Architecture + Video Editor graphs are on the pre-#1504 node-ID scheme;
  a `graphify extract --force` rebuild adds path-qualified IDs (fixes same-name-file
  collisions). Not urgent — queries work as-is.
- REGISTRY.md now has a `## Tooling version` section as the source of truth for this.
