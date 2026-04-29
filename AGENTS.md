# Agent Instructions — Claude-Agent Workspace

> **For:** OpenAI Codex, Antigravity, and any OpenAI-compatible agent operating in this workspace.
> **Claude Code users:** See `CLAUDE.md` instead.

---

## What This Workspace Is

This is Tony's operating system — a unified workspace for all business operations, content creation, e-commerce, app development, and game development. Every subfolder is a department.

**Owner:** Tony (info@borednomad.com)

---

## Rule 1: Read the Workspace Map First

Before exploring any folder or asking Tony for context:

1. Read `001_Architecture/Install_Maps/Workspace-Map.md` — this tells you what every folder is and where everything lives
2. Read `001_Architecture/Memory/` — conventions, tag systems, workflow rules
3. Read `001_Architecture/Logs/` — what was done in recent sessions

---

## Rule 2: Check TOOLBOX Before Writing Scripts

**`TOOLBOX.md` at the workspace root** is the master list of all installed tools, CLIs, MCPs, and Python scripts. Check it before writing any new code. The tool you need probably already exists.

---

## Rule 3: Ingest Procedure

When files are in `000_Ingest/` or Tony says "ingest", follow this exact procedure:

### Step 1: Classify

Read the file. Determine:
- **Type:** `bookmark` | `api-doc` | `tool-doc` | `tutorial` | `model-doc` | `prompt` | `reference` | `doc`
- **Domain:** `ai-agents` | `rag-systems` | `app-dev` | `content-strategy` | `architecture` | `video-production`

### Step 2: Add YAML Frontmatter to Original File

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

**Tag rules:** max 5 tags, all lowercase, kebab-case (dashes not spaces), no quotes.

### Step 3: Route Original File to Resource Library

| Type | Destination |
|------|-------------|
| `bookmark` | `007_Resource_Library/Bookmarks/` |
| `api-doc` for kie.ai | `007_Resource_Library/Docs/Video_Editor/Kie.ai_API/` |
| `api-doc` for fal.ai | `007_Resource_Library/Docs/Video_Editor/Fal.ai_API/` |
| `api-doc` other | `007_Resource_Library/Docs/` |
| `tool-doc` | `007_Resource_Library/Tools/` |
| `tutorial` | `007_Resource_Library/Tutorials/` |
| `model-doc` | `007_Resource_Library/Models/` |
| `prompt` | `007_Resource_Library/Prompts/` |
| `doc` | `007_Resource_Library/Docs/` |

Move the file (don't copy). Use title-case filenames with dashes: `Kie-Ai-API-Reference.md`.

### Step 4: Create a Wiki Page

Create a NEW synthesized knowledge page in `000_Wiki/` — this is NOT a copy of the original.

**Wiki routing by domain:**

| Domain | Wiki Folder |
|--------|-------------|
| `ai-agents` | `000_Wiki/AI-Agents/` |
| `rag-systems` | `000_Wiki/RAG-Systems/` |
| `app-dev` | `000_Wiki/App-Dev/` |
| `content-strategy` | `000_Wiki/Content-Strategy/` |
| `architecture` | `000_Wiki/Architecture/` |
| `video-production` | `000_Wiki/Video-Production/` |

**Wiki page format:**

```markdown
---
title: "Concept or Tool Name"
type: wiki
category: [domain]
tags:
  - tag-one
  - tag-two
source: [path to resource library file]
created: YYYY-MM-DD
---

# Title

## What It Is
One paragraph. Plain language.

## Key Concepts
Bullet list of key ideas extracted and synthesized from the source.

## How Tony Uses This
Practical connection to Tony's workflows. Which department, which tool chain.

## Related
- [[Link to related wiki page]]
```

### Step 5: Cross-Link

Search `000_Wiki/` for existing pages that mention the same tool or concept. Add a `[[link]]` to the new page in their `## Related` section.

### Step 6: Update Log and Index

**`000_Wiki/log.md`** — append:
```
## [YYYY-MM-DD] ingest | Title
Source: [original filename] → [destination in Resource Library]
Wiki: [path to new wiki page]
```

**`000_Wiki/index.md`** — add entry under the correct category:
```
- [[Wiki Page Title]] — one-line description
```

### Step 7: Run Graphify

```bash
cd /Users/tonymacbook2025/Documents/Claude-Agent && graphify update .
```

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

---

## Session Memory

Before starting work, read:
- `001_Architecture/Logs/` — session logs
- `001_Architecture/Memory/` — conventions and preferences
- `001_Architecture/Feedback_Loop/` — corrections and validated approaches
