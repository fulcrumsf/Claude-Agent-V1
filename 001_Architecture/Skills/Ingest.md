---
name: ingest
description: Process files from the 000_Ingest/ folder into the vault. Triggers when the user says "ingest", "process ingest", "ingest this file", "process the ingest folder", "what's in ingest", or when starting a session and files are present in 000_Ingest/. This skill governs the full pipeline: classify → format → route source file to 007_Resource_Library → create wiki page in 000_Wiki → cross-link → log → graphify. Always use this skill for any ingest-related task — do not improvise the procedure.
---

# Vault Ingest Pipeline

## What This Skill Does

When a file lands in `000_Ingest/` (typically via Obsidian Web Clipper or manual drop), this skill processes it end-to-end:

1. **Classify** — determine content type and topic domain
2. **Format** — add YAML frontmatter + tags to the original file
3. **Route** — move original to the correct `007_Resource_Library/` subfolder
4. **Wiki page** — create a synthesized knowledge page in `000_Wiki/`
5. **Cross-link** — link to related existing wiki pages and resource files
6. **Log** — append to `000_Wiki/log.md`
7. **Index** — update `000_Wiki/index.md`
8. **Graphify** — run `graphify update .` from workspace root

Do every step in order. Never skip steps.

---

## Step 1: Classify the File

Read the file and determine:

### Content Type (`type` field)

| Type | Signals |
|------|---------|
| `bookmark` | Clipped from web (Obsidian Web Clipper), has source URL, no deep technical content |
| `api-doc` | Contains endpoints, authentication, request/response examples |
| `tool-doc` | Overview of a tool, what it does, how to use it generally |
| `tutorial` | Step-by-step instructions for accomplishing something |
| `model-doc` | AI model specs, pricing, capabilities, comparisons |
| `prompt` | A reusable prompt template |
| `reference` | Style guide, design system, visual reference |
| `case-study` | Analysis of a specific example or project |
| `script` | Code or automation script |
| `doc` | General documentation that doesn't fit above |

### Topic Domain (determines Wiki category)

| Domain | Wiki Folder | Signals |
|--------|-------------|---------|
| AI agents, Claude, LLMs, agent frameworks | `000_Wiki/AI-Agents/` | Claude, GPT, agents, MCP, LangChain, orchestration |
| RAG, memory, vector databases, embeddings | `000_Wiki/RAG-Systems/` | RAG, embeddings, Pinecone, Chroma, memory systems |
| App development, APIs, coding tools | `000_Wiki/App-Dev/` | React, Next.js, Supabase, APIs, SDKs, coding |
| Content strategy, marketing, copywriting | `000_Wiki/Content-Strategy/` | content, SEO, marketing, social media, email |
| System architecture, workflows, automation | `000_Wiki/Architecture/` | workflows, automation, n8n, pipelines, systems design |
| Video production, animation, image generation | `000_Wiki/Video-Production/` | video, animation, Remotion, kie.ai, fal.ai, Midjourney, image gen |

If a file spans multiple domains, pick the primary one.

---

## Step 2: Add YAML Frontmatter to Original File

Every file gets YAML frontmatter before it is moved. Follow this exact format:

```yaml
---
title: "Human-Readable Title"
type: bookmark|api-doc|tool-doc|tutorial|model-doc|prompt|reference|case-study|script|doc
category: ai-agents|rag-systems|app-dev|content-strategy|architecture|video-production|ecommerce|general
tags:
  - tag-one
  - tag-two
  - tag-three
created: YYYY-MM-DD
source: https://... or local
---
```

### Tag Rules (non-negotiable)
- Maximum 5 tags
- All lowercase, kebab-case (dashes not spaces): `video-generation` not `Video Generation`
- No camelCase, no PascalCase, no spaces, no quotes around tags
- Tags describe: what tool/system it relates to + what it's about
- Example: `kie-ai`, `video-generation`, `api-reference`, `pricing`

---

## Step 3: Route the Original File to Resource Library

Move (not copy) the formatted original file to the correct subfolder:

| Content Type | Destination |
|-------------|-------------|
| `bookmark` | `007_Resource_Library/Bookmarks/` |
| `api-doc` for kie.ai | `007_Resource_Library/Docs/Video_Editor/Kie.ai_API/` |
| `api-doc` for fal.ai | `007_Resource_Library/Docs/Video_Editor/Fal.ai_API/` |
| `api-doc` other video/research | `007_Resource_Library/Docs/Video_Editor/Research_API/` |
| `api-doc` other | `007_Resource_Library/Docs/` |
| `tool-doc` | `007_Resource_Library/Tools/` |
| `tutorial` | `007_Resource_Library/Tutorials/` |
| `model-doc` | `007_Resource_Library/Models/` |
| `prompt` | `007_Resource_Library/Prompts/` |
| `doc` | `007_Resource_Library/Docs/` |

Use the file naming convention: `Title-Case-With-Dashes.md` (no spaces, capitalize each word, acronyms stay uppercase).

---

## Step 4: Create a Wiki Page

Create a NEW file in the appropriate `000_Wiki/` subfolder. This is NOT a copy of the original — it is a synthesized knowledge page.

### Wiki Page Format

```markdown
---
title: "Concept or Tool Name"
type: wiki
category: [same domain as above]
tags:
  - tag-one
  - tag-two
source: [link to the resource library file this came from]
created: YYYY-MM-DD
---

# Title

## What It Is
One paragraph. Plain language. What is this, why does it exist, who uses it.

## Key Concepts
Bullet list of the most important ideas, capabilities, or features. Extract from source — don't copy verbatim, synthesize.

## How Tony Uses This
Practical note connecting this to Tony's actual workflows. Which department, which tool chain, what problem it solves. Leave blank if not applicable.

## Related
- [[Link to related wiki page]]
- [[Link to relevant resource file]]
```

The wiki page title should be the concept or tool name, not the article title. For example, a bookmarked article "10 Ways to Use Graphify" → wiki page titled "Graphify".

---

## Step 5: Cross-Link

After creating the wiki page:

1. Search `000_Wiki/` for any existing pages that mention the same tool/concept
2. Add a `[[link]]` to the new wiki page in those related pages (under their `## Related` section)
3. If no related pages exist, skip — don't force links

This keeps the wiki graph connected so Graphify can map relationships.

---

## Step 6: Update Log and Index

### log.md (`000_Wiki/log.md`)
Append one line per ingested file:
```
## [YYYY-MM-DD] ingest | Title
Source: [original filename] → [destination in Resource Library]
Wiki: [path to new wiki page created]
```

Create `log.md` if it doesn't exist.

### index.md (`000_Wiki/index.md`)
Add or update the entry for the new wiki page under the correct category section:
```
- [[Wiki Page Title]] — one-line description
```

Create `index.md` with category headers if it doesn't exist.

---

## Step 7: Run Graphify

After all files are processed, run from the workspace root:

```bash
cd /Users/tonymacbook2025/Documents/Claude-Agent && graphify update .
```

This updates the knowledge graph with all new cross-links and pages.

---

## Batch Ingest

When processing the entire `000_Ingest/` folder:
- Process files one at a time
- Run graphify ONCE at the end, not after each file
- Report a summary: how many files processed, where each one landed

## Single File Ingest

When the user says "ingest [filename]" or "process this file":
- Process that one file through all 7 steps
- Run graphify at the end

---

## File Naming

All files in this workspace follow:
- No spaces — use `_` or `-`
- Capitalize first letter of every word: `Kie-Ai-API-Reference.md`
- Acronyms stay uppercase: `MCP`, `API`, `RAG`
- Python scripts (.py) are exempt from renaming
