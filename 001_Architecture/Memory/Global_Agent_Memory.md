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

### 2026-05-03 — Single Shared Secrets File

Tony uses `~/.env-secrets` as the single shared secrets file. `~/.mcp-secrets.env` is stale and should not be referenced by active workspace instructions.

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
- Job-specific AI contracts should route into `009_AI_Jobs/[Platform]/` instead of the generic docs library.
