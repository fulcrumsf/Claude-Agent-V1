# Agent Instructions — Agent-OS Workspace

> **For:** OpenAI Codex, Antigravity, and any OpenAI-compatible agent operating in this workspace.
> **Claude Code users:** See `CLAUDE.md` instead.

---

## What This Workspace Is

This is Tony's operating system — a unified workspace for all business operations, content creation, e-commerce, app development, and game development. Every subfolder is a department.

**Owner:** Tony (info@borednomad.com)

> [!NOTE]
> **Legacy Workspace Rename:** The workspace was formerly called `Claude-Agent` (or jokingly `clogged-agent`). Any IDE configs, startup URIs, or CLI integrations that still advertise `/Users/tonymacbook2025/Documents/Claude-Agent` must always be translated to `/Users/tonymacbook2025/Documents/Agent-OS/` on startup.



## Preservation Rule

Do not trash or destructively delete source files during ingest or cleanup. Preserve originals unless the routing decision is explicit and points to an existing destination. If something is no longer active, move it only when Tony has approved the destination; otherwise leave it in place and ask. Nothing should be thrown in the trash as part of normal workspace operations.

### Iteration Archive Rule

This preservation rule applies to every project artifact, including images,
prompts, scripts, shot lists, storyboards, metadata, audio, video, and renders.
When an iteration is denied or superseded, move the prior version into the
matching project `Archived/` folder rather than deleting or overwriting it.
Preserve its original version number and assign the replacement the next
version number. Active folders should contain only current working or approved
artifacts.

---

## Rule 1: Read the Workspace and System Maps First

Before exploring any folder or asking Tony for context:

1. Read `001_Architecture/Install_Maps/Workspace-Map.md` — this tells you what every folder is and where everything lives
2. Read `001_Architecture/Install_Maps/System-Map.md` — this tells you installed apps, CLIs, Homebrew packages, npm globals, MCPs, scripts, skills, and local tool paths
3. Read `001_Architecture/Memory/Core_Memory.md` and `001_Architecture/Memory/Memory_Index.md` — tiny bootstrap memory and routing
4. Read `001_Architecture/Logs/` — what was done in recent sessions

---

## Rule 2: Check TOOLBOX Before Writing Scripts

**`TOOLBOX.md` at the workspace root** is the master list of all installed tools, CLIs, MCPs, and Python scripts. Check it before writing any new code. The tool you need probably already exists.

## Rule 2.5: Check the Skill Index Before Choosing a Skill

The canonical cross-agent skill registry is `001_Architecture/Skills/Skill-Index.md`. Read it first when deciding which skill to use, then open the matching `SKILL.md` file for the full instructions.

## Rule 2.6: Use the Codex Agent-OS Hardening Skill

When operating as Codex or any OpenAI-compatible agent in Agent-OS, use `001_Architecture/Skills/codex-agent-os-hardening/SKILL.md` as the operating checklist for startup orientation, folder routing, recommendation approval boundaries, preservation rules, feedback-loop writes, memory updates, session logs, and closeout behavior. This skill exists so Codex mirrors Claude Code's Agent-OS discipline instead of making Tony repeat core working rules.

For broad onboarding or "understand this system" requests, prioritize the numbered departments: `001_Architecture` first, `002_Content-Creation` second, `007_Resource_Library` third. Usually skip `000_Ingest` unless the task is specifically about ingesting or organizing raw intake.

---

## Rule 3: Ingest Procedure

When files are in `000_Ingest/` or Tony says "ingest", follow this exact procedure. **Recurse into all subfolders by default** unless told otherwise ("top-level only", "don't recurse", or a single file specified).

**Notion database exports:** When recursing into a Notion export folder structure, skip top-level database container `.md` files that contain only Notion metadata. Treat each individual record `.md` as a standalone file to classify and ingest normally.

### Step 1: Classify

Read the file. Determine the content's topic. "Bookmark" is no longer a valid category—route based on what the content is actually about.
- **Type:** `api-doc` | `tool-doc` | `tutorial` | `model-doc` | `prompt` | `workflow` | `project-idea` | `design-inspiration` | `personal` | `research` | `doc` | `image` | `pdf` | `word-doc` | `video` | `investment`
- **Domain/Tag:** Determine a descriptive tag (e.g., `video-production`, `social-media`, `image-editing`) to add to the YAML frontmatter.

### Step 1.5: Media Analysis & Renaming (Images and Binary Files Only)

Skip for `.md`, `.txt`, `.pdf`, `.json`, `.csv`, and other text-readable files.
PDFs: skip renaming — route directly to `007_Resource_Library/Docs/`.

**Lookup-First Gate — run before any vision call:**

```bash
python /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/check_vision_needed.py "/path/to/images"
```

This audits each file's Asset Note for filler descriptions. Filler = "likely a saved reference", "general visual reference", "This appears to be a screenshot of…", description under 60 chars, or no Asset Note at all.

- **Already cataloged** (real description found) → skip vision, go to Step 3
- **Needs vision** → continue below

For files flagged as needing vision, use the rename script:
```bash
python /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/rename_screenshots.py "/path/to/images"
```
Uses Gemini vision first and OpenAI vision as fallback. Requires the relevant API keys for whichever provider is used. Do not use OCR as the default path; only use it if Tony explicitly asks for OCR or a dedicated OCR workflow.

### Step 2: Add YAML Frontmatter (Text Files Only)

Skip for image and binary files — they get an Asset Note in Step 4.

```yaml
---
title: "Human-Readable Title"
type: [type from above]
category: [domain from above]
tags:
  - tag-one
  - tag-two
  - tag-three
created: YYYY-MM-DD
source: https://... or local
---
```

**Tag rules:** minimum 2 tags, maximum 5 tags. All lowercase, kebab-case (dashes not spaces), no quotes. Use rich semantic tags (e.g., `ai-automation`, `agentic-ai`, `video-editing`).

### Step 3: Route Original File to Resource Library

Move (don't copy). Text files use `Title-Case-With-Dashes.md`. Media files use the kebab-case name from Step 1.5.

> **DIRECTORY REFERENCE:** Before routing, you MUST read `007_Resource_Library/Directory.md` to understand the exact definitions and constraints of each destination folder. If an ingested file does not clearly fit into one of the established folders, you MUST ask Tony for approval before creating a new folder. Do not guess.

| Type | Destination |
|------|-------------|
| `api-doc` / `doc` / `pdf` / `word-doc` | `007_Resource_Library/Docs/` |
| `investment` | `007_Resource_Library/Investments/` |
| `model-doc` | `007_Resource_Library/Models/` |
| `prompt` | `007_Resource_Library/Prompts/` |
| `design-inspiration` | `007_Resource_Library/Design_Inspiration/` |
| `personal` | `007_Resource_Library/Personal/` |
| `research` | `007_Resource_Library/Research/` |
| `tool-doc` / SaaS / Plugins | `007_Resource_Library/Tools/` |
| `tutorial` / How-to guides | `007_Resource_Library/Tutorials/` |
| `workflow` | `007_Resource_Library/Workflows/` |
| `project-idea` | `007_Resource_Library/Project_Ideas/` |
| `image` (ALL raw images) | `007_Resource_Library/Obsidian_Attachments/Visual_Assets/` |
| `video` (Requires package creation) | `007_Resource_Library/Videos/[Kebab-Case-Name]/` |

**AI jobs / contract reference exception:** If a file is a job-specific onboarding contract, work agreement, invention assignment, or platform reference for Tony's AI-testing work, route it to `009_AI_Jobs/[Platform]/` instead of the generic docs folder. Keep all related files for the same platform together.

**Special Video Handling Rule:**
For `video` types (`.mp4`, `.mov`, etc.):
1. Rename the video descriptively using `Title-Case-With-Dashes` and preserve uppercase acronyms like `AI` and `API`.
2. Create a new folder: `007_Resource_Library/Videos/[Descriptive-Stem]/`.
3. Move the renamed video into this folder.
4. Create empty scaffold files `[Descriptive-Stem]-Transcript.md` and `[Descriptive-Stem]-Tutorial.md` next to the video.
5. Keep the folder, MP4, transcript, and tutorial scaffold on the same stem.

### Step 4: Create a Wiki Page or Asset Note

**Text files → Wiki page** in the appropriate `000_Wiki/` subfolder (synthesized knowledge, not a copy):

If the ingested text file is itself a routed reference note for `Prompts`, `Design_Inspiration`, `Personal`, `Research`, `Tools`, `Tutorials`, `Workflows`, or `Project_Ideas`, move it into the matching `007_Resource_Library/` folder instead of synthesizing a wiki page.

| Domain | Wiki Folder |
|--------|-------------|
| `ai-agents` | `000_Wiki/AI-Agents/` |
| `rag-systems` | `000_Wiki/RAG-Systems/` |
| `app-dev` | `000_Wiki/App-Dev/` |
| `content-strategy` | `000_Wiki/Content-Strategy/` |
| `architecture` | `000_Wiki/Architecture/` |
| `video-production` | `000_Wiki/Video-Production/` |

Wiki page format: title, type, category, tags, source YAML + `## What It Is`, `## Key Concepts`, `## How Tony Uses This`, `## Related` sections.

**PDFs → No companion file needed.** Obsidian has a native PDF viewer. Only create a wiki page if the content warrants synthesis.

**Images and word docs → Note file** in the matching `007_Resource_Library/` destination folder, named with the same stem as the media file and a `.md` extension. The raw image stays in `007_Resource_Library/Obsidian_Attachments/Visual_Assets/`:

```markdown
---
title: "Descriptive Title"
type: asset-note
category: visual-assets
tags:
  - tag-one
ai_description: "One-sentence summary."
original_filename: "IMG_1234.png"
created: YYYY-MM-DD
---

![[descriptive-kebab-name.png]]

## AI Analysis
[Detailed description from vision analysis.]
```

Do NOT create a wiki page for images or word docs.

### Step 5: Cross-Link

Text files only. Search `000_Wiki/` for existing pages mentioning the same tool or concept. Add a `[[link]]` to the new page in their `## Related` section. Skip for media/asset notes.

### Step 6: Update Log and Index

**`000_Wiki/log.md`** — append:
```
## [YYYY-MM-DD] ingest | Title
Source: [original filename] → [destination in Resource Library]
Wiki/Asset Note: [path to new file created]
```

**`000_Wiki/index.md`** — add entry for text wiki pages only:
```
- [[Wiki Page Title]] — one-line description
```

### Step 7: Run Graphify

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS && graphify update .
```

`graphify update .` is the fast AST-only path for code-bearing domains. For docs-only or wiki-heavy domains, use the interactive `/graphify <domain> --update` flow so semantic extraction runs too.
Do not graphify `000_Ingest/`; it is a temporary staging area and only becomes graph targets after ingest routes files into durable folders.

---

## File Naming Convention

- No spaces — use `_` or `-`
- Capitalize first letter of every word: `Video-Production-Workflow.md`
- Acronyms stay uppercase: `MCP`, `API`, `RAG`
- Python scripts (.py) are exempt

---

## Workspace Structure Quick Reference

See `001_Architecture/Install_Maps/Workspace-Map.md` for the full map.

| Folder | What It Is |
|--------|-----------|
| `000_Ingest/` | Landing zone — process with ingest procedure |
| `000_Wiki/` | Synthesized knowledge wiki |
| `001_Architecture/` | System brain: memory, logs, skills, maps |
| `002_Content-Creation/` | YouTube (12 channels), social media, clipping |
| `003_Apps/` | App development projects |
| `004_Games/` | Roblox game |
| `005_Ecommerce/` | POD, KDP, Digital Products, Merch |
| `006_Websites/` | Brand websites |
| `007_Resource_Library/` | Raw reference materials |
| `008_Investments/` | Investment research, analytics, and active portfolio tooling |
| `009_AI_Jobs/` | AI job onboarding, contracts, work references, and platform-specific job docs |

---

## Session Memory

Before starting work, read:
- `001_Architecture/Memory/Core_Memory.md` — always-read bootstrap memory
- `001_Architecture/Memory/Memory_Index.md` — memory routing, what to load next
- `001_Architecture/Logs/` — recent session logs only when relevant
- `001_Architecture/Feedback_Loop/` — recent corrections/preferences only when relevant

Do not load every memory/log file by default. Use `claude-mem` for relevant memory retrieval first, then targeted file reads based on `Memory_Index.md`.

## Dynamic Memory — Claude-Mem

`claude-mem` is the shared relevant-memory backend for Claude Code, Codex-compatible sessions, Gemini CLI, and other agents.

- Worker status: `npx claude-mem status`
- Start worker: `npx claude-mem start`
- Viewer: `http://localhost:37701`
- Claude Code command: `/mem-search`
- Gemini CLI receives injected context through `~/.gemini/GEMINI.md`
- Codex has the local `thedotmack` plugin marketplace registered; if plugin tools are not available in the active session, use the worker commands and targeted workspace memory files.

Use `claude-mem` or its search tools for past-session context. Keep markdown memory compact and curated.

## Session Memory — Write Automatically

Capture knowledge without being asked. These layers update continuously so future Codex sessions can resume without Tony repeating context.

### Feedback Loop (`001_Architecture/Feedback_Loop/`)

Save automatically when Tony gives feedback. Don't wait for him to say "record this." Detect it from the conversation:
- **Corrections:** "stop doing X", "that's wrong", "don't do it that way" → what should have been done, why it matters
- **Preferences revealed:** "I prefer X", "I don't like Y", "this is overkill" → capture the preference with context
- **Validated approaches:** Tony accepts or affirms a non-obvious choice ("perfect", "yes that's what I meant", no pushback on a deliberate decision) → capture what worked and why
- Write to: `YYYY-MM-DD_Feedback.md` — one per day, append entries

### Session Logs (`001_Architecture/Logs/`)

Keep a compact record of what happened, not a transcript. Record significant actions: what changed, why, what files were touched, what decisions were made, what's pending.

- Write to: `YYYY-MM-DD_Session-Log.md`
- Append during the session when meaningful work happens
- At session close, make sure the day log reflects the current state

### Self-Learning Loop (`001_Architecture/Self_Learning_Loop/`)

At session close, review the day's work and identify patterns: what went wrong, what worked well, what keeps recurring, what could be automated. Be honest about mistakes.

- Write to: `YYYY-MM-DD_Self-Review.md`

### Global Cross-Agent Memory (`001_Architecture/Memory/Global_Agent_Memory.md`)

Codex does not have Claude Code's built-in auto-written `~/.claude/.../memory/MEMORY.md`. Use workspace-local memory files instead, with `Global_Agent_Memory.md` as the shared source of truth across Claude Code, Codex, Antigravity, Gemini CLI, and other agents.

Update `001_Architecture/Memory/Global_Agent_Memory.md` only with durable facts that should survive across days and should be visible to all agents:
- Tony's stable preferences
- project-level decisions
- recurring corrections
- important tool paths or workflow rules
- external references that should be easy to find again

Use `001_Architecture/Memory/Codex_Memory.md` only for Codex-specific quirks that should not apply globally.

Do not store secrets, API keys, private credential values, noisy transcripts, or session-by-session detail in markdown memory. Store concise, reusable memory entries. Let `claude-mem` handle episodic session memory and relevant injection.

### Closeout Trigger

When Tony says "I'm about to close this session", "wrap this up", "save memory", or similar:
1. Update today's session log
2. Update today's feedback log if any corrections/preferences/validated approaches appeared
3. Add or update durable entries in `001_Architecture/Memory/Global_Agent_Memory.md`
4. Add a self-review entry if the session included meaningful work
5. Update all Workspace Maps, System Maps, TOOLBOX.md, and directory definitions to include any new folders, scripts, skills, or configurations.
6. If code or docs changed, run the appropriate verification or graph update before final response

Also write incrementally throughout the session when an important preference or decision appears — don't batch everything only at the end.


<claude-mem-context>
# Memory Context

# [Agent-OS] recent context, 2026-06-06 3:53pm EDT

Legend: 🎯session 🔴bugfix 🟣feature 🔄refactor ✅change 🔵discovery ⚖️decision 🚨security_alert 🔐security_note
Format: ID TIME TYPE TITLE
Fetch details: get_observations([IDs]) | Search: mem-search skill

Stats: 50 obs (22,351t read) | 296,762t work | 92% savings

### May 29, 2026
S165 User asked "where did we leave off last time?" — session orientation and continuity check (May 29 at 12:11 AM)
S166 Multi-agent skills symlink audit and repair — ensuring all AI agent runtimes connect to the shared Agent-OS Skills library (May 29 at 12:35 AM)
S167 Full multi-agent environment health check — CLI tools, plugins, and shared infrastructure audit across all runtimes (May 29 at 12:39 AM)
S168 Full multi-agent environment audit and integration — MCPs, plugins, CLIs, and Antigravity IDE capability gaps closed (May 29 at 12:41 AM)
S169 User confirmed acceptance of multi-agent memory architecture — three-layer memory system explained and validated (May 29 at 12:47 AM)
S170 Session 2 close-out: agent runtime audit after Antigravity upgrade — all artifacts written and memory updated (May 29 at 12:50 AM)
S171 Update Codex CLI to latest version (May 29 at 12:52 AM)
### Jun 6, 2026
S172 Full developer CLI toolchain audit and update across npm, Homebrew, and uv (Jun 6 at 1:16 PM)
S173 List all MCPs across all runtimes (Antigravity IDE, Claude Desktop, Claude Code plugin layer) (Jun 6 at 1:20 PM)
S174 Session wrap-up — all memory artifacts written, session log finalized, MCP inventory listed (Jun 6 at 1:27 PM)
753 2:02p 🔵 markitdown Confirmed Installed with Azure Document Intelligence Support
755 " 🔵 Pre-Classification Routing Map Generated for 75 Ingest Files
756 2:03p 🔵 Social1.md Identified as TikTok Shop Ad Performance Data Dump
757 " 🔵 Two Arcads + Claude Code UGC Ad Workflow Tools Found in Ingest Queue
758 " 🔵 TikTok Spotlight Creator Program Documentation Ingested
759 2:04p 🔵 DESIGN.md Format Spec Found — Google Labs Standard for Agent-Readable Design Systems
760 " 🔵 NexLev MCP Connector Docs Found — YouTube Channel Research Tool for Claude
761 2:06p 🟣 Batch Ingest of 75 Root-Level Files Completed Successfully
762 " 🔵 Ingest Verification Confirms 75 Files Routed With Source Attribution — But 18+ Files Have Generic Names
763 2:07p 🔴 Second Pass Corrected All 75 Filenames Using Source-Based Title Derivation
764 2:08p 🔵 Final Ingest Verification Confirms All 75 Files Properly Named and Traceable
765 " 🔴 Manual Routing Corrections Applied to 12 Misclassified Ingest Files
766 2:09p 🔵 000_Ingest Root Cleared; Subfolders Still Pending Including Two Mercor PDFs
767 " 🟣 graphify Knowledge Graph Updated After Ingest Batch
768 2:14p ⚖️ Ingest Folder Review: Higgs Field Video Pipeline Organization
769 " 🔵 Higgsfield Video Pipeline Folder Structure Mapped
770 2:15p 🔵 Banana-Pro-Director Skill: Higgsfield Image Prompt Builder
771 " 🔵 Cinema-Worldbuilder Skill: Seedance Video Prompt Director
772 " 🔵 Skill Upload Instructions: Claude.ai Skills Installation Process
773 2:16p 🔵 Higgsfield Video Pipeline Skills Are Completely Unlinked in Agent-OS
774 2:17p 🔵 Related Tutorial Files Found in Resource Library for Higgsfield Pipeline Linking
775 " 🔵 Higgsfield Video Pipeline Has No Processed Entry; Workflow Cross-Links Identified
776 2:19p 🔵 Agent-OS Has No Existing Skills Architecture Path for Ingest
777 " 🔵 Agent-OS Skills Architecture: Skills Stored at 001_Architecture/Skills/[name]/SKILL.md
778 2:20p 🔵 Tutorials Folder Is Completely Flat; Character-Consistency Tutorial Identified as Cross-Link Target
779 " 🔵 Seedance Wiki Page and Nano Banana Ingest History Confirm Migration Cross-Link Targets
780 " 🔵 Higgsfield Tool Entry Is a Minimal Stub With No Cross-Links
781 " ✅ Higgsfield Video Pipeline Folder Moved from Ingest to Resource Library Tutorials
782 2:21p ✅ Higgsfield Pipeline Files Renamed to Follow Agent-OS Naming Convention
783 " ✅ Higgsfield-Video-Pipeline.md Formatted with YAML Frontmatter and Cross-Links
784 " ✅ Higgsfield Pipeline Fully Integrated: Wiki Cross-Link, Ingest Log, and Session Log Updated
785 " 🔵 Log Update Patch Failed: Placeholder Text Not Found in wiki/log.md
786 2:22p ✅ All Three Log/Wiki Files Successfully Updated on Second Patch Attempt
787 " ✅ Graphify Knowledge Graph Updated with Higgsfield Pipeline Files
788 2:23p 🔵 Remaining 000_Ingest Subfolders Identified for Next Review Pass
789 " 🔵 Graphify Watch Reverted Node/Edge Count Below the Manual Update Result
790 " 🔵 Higgsfield Migration Verified Complete; Global Memory Checked for Pattern Recording
791 2:24p ✅ Global Agent Memory Updated: Tutorial Skill Bundles Stay Together Rule
792 2:25p 🔵 Second Ingest Subfolder Found: Higgsfield-Claude-Prompt Contains Tutorial and Prompt Pair
793 " 🔵 Higgsfield-Claude-Prompt Folder: Tutorial Is Near-Duplicate; Timestamp-Prompt Is New Standalone Reusable Prompt
794 " 🔵 Higgsfield-Claude-Prompt: Tutorial Confirmed Duplicate; Timestamp-Prompt Confirmed New and Unprocessed
795 2:26p 🔵 Tutorial Duplicate Confirmed by Diff: Only Difference Is YAML Frontmatter
796 " 🔵 Video Production PDR Exists as Architecture Spec in Wiki
797 2:27p ✅ Claude Code YouTube Video Editing Bundle Consolidated Into Tutorials Subfolder
798 " ✅ Claude Code YouTube Video Editing Bundle Fully Formatted and Cross-Linked
799 2:28p ✅ Claude Code YouTube Video Editing Bundle Logged and Graphify Update Triggered
800 " 🔵 Graphify Update Complete; Higgsfield-Claude-prompt Folder Remains With Only .DS_Store
801 2:29p 🔵 Third Ingest Subfolder: AIOS_Installation_Guide Contains MD + PDF Pair
802 " 🔵 Claude Code YouTube Video Editing Bundle Fully Verified; Ingest Folder Completely Empty
804 2:33p 🔵 009_AI_JOBS/ — New Top-Level Folder Created for Mercor Legal Docs

Access 297k tokens of past work via get_observations([IDs]) or mem-search skill.
</claude-mem-context>
