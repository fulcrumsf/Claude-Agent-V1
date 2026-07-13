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
