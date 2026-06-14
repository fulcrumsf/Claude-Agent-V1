# Session Log: 2026-05-02

## Session 5 — Architecture Polish & Resource Library Routing

### Summary
Tony requested clarification on folder criteria inside `007_Resource_Library`, realizing that "Bookmarks" is a flawed concept since a bookmark is merely a medium, not a topic. We removed the Bookmarks category entirely from the ingest pipeline, enforcing that all files be routed by topic (Tools, Tutorials, Investments, Docs, etc.).

We also defined a complete workflow for "Videos," where ingested videos get their own dedicated package folder, complete with the raw video file and scaffolded Markdown files for transcripts and tutorials. Finally, we wrote a Python script to permanently move 500+ scattered image files and Asset Notes from across the various folders into `Obsidian_Attachments/Visual_Assets/` and `Asset_Notes/`, completely deleting the obsolete Bookmarks directory.

### Decisions Made
- `007_Resource_Library/Directory.md` acts as the strict glossary and mapping guide for the Resource Library. Agents must read it and get Tony's permission before creating new folders.
- "Bookmarks" as a routing category is officially deprecated.
- Tools folder remains flat to keep routing simple, but ingest agents must apply 2-to-5 descriptive YAML tags (e.g., `ai-automation`, `video-production`) to ensure items remain filterable.
- Videos are no longer loose files; they are generated as "knowledge packages" inside `007_Resource_Library/Videos/[Name]/`.

### Files Touched
- `AGENTS.md` — Updated Step 3 Routing table and Tag Rules.
- `~/.claude/skills/ingest/SKILL.md` — Synced all new folder constraints, tagging rules, and video package instructions.
- `007_Resource_Library/Directory.md` — Created as the new official routing glossary.
- `001_Architecture/Scripts/cleanup_bookmarks.py` — Created and executed to reorganize 544 files.
- `007_Resource_Library/*` — Massive internal reorganization of images and asset notes into centralized folders.

## [2026-05-02] Global Architecture Symlinking & Video Ingest Pipeline
- **Decision**: Established `001_Architecture` as the single source of truth for all agents across the workspace.
- **Action**: Consolidated over 130 skills from `~/.claude/skills` and `~/.gemini/antigravity/skills` into `001_Architecture/Skills`. Replaced original hidden folders with symlinks.
- **Action**: Consolidated duplicated python provider scripts from `002_Content-Creation/Video_Editor/004_Tools/` into `001_Architecture/Tools/` and created symlinks back to maintain local imports.
- **Action**: Consolidated MCP configurations (Claude Desktop, Claude CLI, Gemini) into `001_Architecture/MCP/` and symlinked them back.
- **Action**: Created `001_Architecture/Directory.md` as the global routing glossary.
- **Action**: Updated `007_Resource_Library/Directory.md` to make the 2-5 YAML tag requirement universal for all text and asset notes.
- **Action**: Created `001_Architecture/Scripts/process_video_ingest.py` (FFmpeg scene detection + Whisper transcription) and wired it into `ingest/SKILL.md`.

## [2026-05-02] Closeout Phase: Semantic Screenshot Extraction & Naming Conventions
- **Action**: Deprecated old generic Asset Notes paradigm for screenshots.
- **Action**: Created `process_image_ingest.py` in `001_Architecture/Scripts/` to automatically analyze screenshots using Gemini 2.5 Flash Vision. It extracts semantic value (Tool, Tutorial, etc.), writes rich markdown files in Title-Case-With-Dashes, moves the raw image to Visual Assets, and routes unreadable/mistimed frames to the Undetermined folder.
- **Action**: Modified the master `ingest` skill (`SKILL.md`) to integrate this new script.
- **Action**: Logged user feedback regarding strict Title-Case-With-Dashes enforcement on markdown files and Kebab-Case on media files.

- **Action**: Fully integrated Codex CLI and Codex Desktop. Deleted the separate `~/.codex/skills/` folder and symlinked it to the central global `001_Architecture/Skills/` source of truth. Both applications are now permanently synchronized with Claude and Gemini.
- **Action**: Added an OpenAI GPT-4o-mini Vision fallback to `process_image_ingest.py`. If Gemini is rate-limited or exhausted, the system automatically falls back to OpenAI seamlessly.

## [2026-05-02] Ingest Routing Correction: Images Stay in Visual Assets
- **Action**: Updated the ingest skill so raw images remain in `007_Resource_Library/Obsidian_Attachments/Visual_Assets/`.
- **Action**: Clarified that the routed object is the corresponding note, which must move into the correct category subfolder.
- **Action**: Added an end-of-batch holdback rule for uncategorized items so Tony can approve any new folder or category before anything is created.

## [2026-05-02] Ingest Routing Categories Defined
- **Action**: Added an explicit routing table for image-derived notes in the ingest skill.
- **Action**: Canonical categories are `Tools`, `Tutorials`, `Prompts`, `Docs`, `Investments`, `Models`, `Videos`, and `Archive`.
- **Action**: Ambiguous items remain queued until the end of the batch so Tony can approve the category instead of the agent guessing.

## [2026-05-02] Ingest Tie-Break Rules Clarified
- **Action**: Defined a decision order for image-derived notes: prompts first, then tutorials, then tools, then docs, then investments, models, videos, and archive.
- **Action**: Clarified that `Docs` is primarily for PDFs/text reference and only rarely for markdown API/configuration notes.
- **Action**: Recorded Tony's examples: Notion prompt screenshots route to `Prompts`; YouTube/TikTok walkthroughs route to `Tutorials`; tool/product/GitHub screenshots route to `Tools`.

## [2026-05-02] Pilot Ingest Test
- **Action**: Moved a prompt screenshot note to `007_Resource_Library/Prompts/TikTok-JSON-Prompt.md` and preserved the prompt text in the note.
- **Action**: Moved a tool screenshot note to `007_Resource_Library/Tools/Vortex-Longshot-Tool.md` because the software and URL were the primary signal.
- **Action**: Moved a tutorial screenshot note to `007_Resource_Library/Tutorials/New-Fav-MCP-Tutorial.md` and kept the walkthrough context and visible node details.
- **Action**: Left the raw images in `007_Resource_Library/Obsidian_Attachments/Visual_Assets/` as instructed.

## [2026-05-02] Batch 2 Image-Derived Note Routing
- **Action**: Moved `AgentKit-OpenAI-Platform.md`, `Viewstats-YouTube-Tool.md`, `Promptly-AI-Tool.md`, `TikTok-Live-Studio-Access.md`, `YouTube-Tool-N8n-Overview.md`, `TikTok-AI-Video-Tools.md`, and `Tripod-AI-Tool.md` into their routed folders.
- **Action**: Routed prompt resources to `Prompts`, tutorial-style breakdowns to `Tutorials`, and product/tool screenshots to `Tools`.
- **Action**: Normalized the moved notes so they have proper frontmatter and short `What It Is` / `Key Details` sections where appropriate.

## [2026-05-02] Batch 3 Prompt Resource Routing
- **Action**: Moved `ChatGPT-Prompt.md`, `Cross-X-Prompt-2.md`, `Cross-X-Prompt-3.md`, `VeoVault-AI-Prompts.md`, and `God-Of-Prompt-Veo.md` into `007_Resource_Library/Prompts/`.
- **Action**: Converted the notes to prompt-resource format with prompt context or template sections.
- **Action**: Kept the raw screenshots in `Obsidian_Attachments/Visual_Assets/` unchanged.

## [2026-05-02] Batch 4 Tool and Tutorial Routing
- **Action**: Moved `Nexlev-YouTube-Tool.md`, `Web-Assets-Generator-Tool.md`, `Skilljar-Agent-Skills-URL.md`, and `TubeGenAI-YouTube-Automation.md` into their routed folders.
- **Action**: Classified `Skilljar-Agent-Skills-URL.md` as a tutorial resource and the other three as tools.
- **Action**: Normalized the YAML on `Sora-Tutorial-Breakdown.md` so its description remains parseable.

## [2026-05-02] Batch 5 Prompt Library Routing
- **Action**: Moved `ChatGPT-Prompt-Engineering.md`, `Cross-X-Prompt.md`, `Gemini-Prompt-Trend.md`, `Nano-Banana-Prompt-Library.md`, `Public-Prompt-Library.md`, and `Viral-Sora-Prompts.md` into `007_Resource_Library/Prompts/`.
- **Action**: Kept prompt context and template sections explicit so the notes preserve the reusable text value.
- **Action**: Left the raw images in `Obsidian_Attachments/Visual_Assets/` unchanged.

## [2026-05-02] Batch 6 Claude Tool and Tutorial Routing
- **Action**: Normalized `Awesome-Claude-MCP-Builder-Github.md`, `Awesome-Claude-Skills-Github.md`, `Claude-Mem-Plugin.md`, and `Claude-Skills-Jobs-List.md` into `007_Resource_Library/Tools/`.
- **Action**: Kept `Anthropic-Agent-Skills-Course.md` and `Claude-Must-Install-Skills.md` in `007_Resource_Library/Tutorials/` as learning resources.
- **Action**: Added explicit `What It Is` and `Key Details` sections to the tool notes so the Claude references are easy to scan later.

## [2026-05-02] Batch 7 Claude Tutorial Cleanup
- **Action**: Normalized `Claude-Must-Install-Skills.md` into tutorial format with explicit learning context and marketing AI agent details.
- **Action**: Preserved the raw screenshot in `Obsidian_Attachments/Visual_Assets/`.

## [2026-05-02] Full Remaining Asset Note Sweep
- **Action**: Processed the entire remaining `007_Resource_Library/Asset_Notes/` backlog in two automated passes.
- **Action**: Routed all 547 remaining notes out of `Asset_Notes/`, leaving the folder empty.
- **Action**: Final category totals for the sweep: 470 tools, 28 prompts, 11 tutorials, 18 docs, 11 investments, and 9 models.
- **Action**: Kept raw images in `007_Resource_Library/Obsidian_Attachments/Visual_Assets/` unchanged while moving only the notes.

## [2026-05-02] Routing Correction: Workflows and Project Ideas
- **Action**: Added `007_Resource_Library/Workflows/` as a first-class destination for process maps and workflow references.
- **Action**: Added `007_Resource_Library/Project_Ideas/` to the Resource Library map for raw project concepts and future build seeds.
- **Action**: Corrected the routing decision for `Workflow.md`; it should route to `Workflows/`, not `Tools/`.
- **Action**: Confirmed that tutorial search screenshots like `Videos.md` route to `Tutorials/` because the primary value is the tutorial list, not the search page itself.

## [2026-05-02] Routing Clarification: Docs, Inspiration, and Personal References
- **Action**: Clarified that `Workflows` means visual flowcharts/mind maps only, not written tutorials.
- **Action**: Clarified that `Docs` is not a catch-all folder and should stay limited to actual documentation artifacts.
- **Action**: Captured the need for likely new folders for design inspiration and personal references, pending Tony's naming approval.

## [2026-05-02] Routing Clarification: Design Inspiration and Personal
- **Action**: Tony confirmed `007_Resource_Library/Design_Inspiration/` for t-shirt designs, website inspiration, aesthetic Instagram accounts, and image-only visual references.
- **Action**: Tony confirmed `007_Resource_Library/Personal/` for non-business references such as band tour flyers and other personal-interest captures.
- **Action**: Corrected `Real-Life-Lore-YOUTUBE.md` out of `Models/` and identified `Lofi.md` as a tutorial resource instead of a docs note.

## [2026-05-02] Routing Clarification: Product Research Captures
- **Action**: Routed `Google-Inulin-Products.md` out of `Docs/` into `Personal/` as a non-business product-research capture.
- **Action**: Reconfirmed that `Docs` is not a catch-all folder and should only hold true documentation/reference artifacts.
