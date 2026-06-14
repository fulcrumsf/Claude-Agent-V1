---
name: ingest
description: "Process files from the 000_Ingest/ folder into the vault. Triggers when the user says \"ingest\", \"process ingest\", \"ingest this file\", \"process the ingest folder\", \"what's in ingest\", or when starting a session and files are present in 000_Ingest/. This skill governs the full pipeline: classify → (media: analyze & rename) → format → route → create wiki page or asset note → cross-link → log → graphify. Always use this skill for any ingest-related task — do not improvise the procedure."
---

# Vault Ingest Pipeline

## What This Skill Does

When files land in `000_Ingest/` (via Obsidian Web Clipper, manual drop, or any subfolder within `000_Ingest/`), this skill processes them end-to-end:

0. **Markitdown** — convert any PDF, Word, PowerPoint, or Excel files to `.md` before processing
1. **Classify** — determine content type and topic domain
1.5. **Media Analysis** — if image or unreadable binary: use vision to describe and rename descriptively
2. **Format** — add YAML frontmatter to text files; media gets a routed note instead
3. **Route** — move original to the correct `007_Resource_Library/` subfolder
4. **Wiki page or routed note** — synthesized wiki page in `000_Wiki/` (text) or a categorized note in the correct `007_Resource_Library/` subfolder for media references
5. **Cross-link** — link to related existing wiki pages (text files only)
6. **Log** — append to `000_Wiki/log.md`
7. **Index** — update `000_Wiki/index.md` (text files only)
8. **Graphify** — run `graphify update .` from workspace root

Do every step in order. Never skip steps.

---

## Subfolder Recursion

By default, recurse into ALL subfolders within `000_Ingest/`. Process every file found, regardless of nesting depth.

**Exception:** If the user says "top-level only", "don't recurse", or specifies a single file — limit to what was specified.

**Notion database exports:** When recursing into a Notion export folder structure (deeply nested folders with individual record `.md` files), skip top-level database container `.md` files that contain only Notion metadata and no real content. Treat each individual record `.md` file as a standalone file to classify and ingest normally.

---

## Step 0: Markitdown Pre-Processing

Before classifying, scan for binary file types that need conversion to `.md`:

**Supported types:** `.pdf`, `.docx`, `.doc`, `.pptx`, `.ppt`, `.xlsx`, `.xls`

**For each matching file found:**
```bash
markitdown "/path/to/file.pdf" -o "/path/to/file.md"
```
Then delete the original binary. The resulting `.md` file proceeds through Steps 1–8 as normal.

**Skip this step for:** `.md`, `.txt`, `.json`, `.csv`, images, videos — they are handled by their own pipelines.

**Drop zones** (check these subfolders first):
- `000_Ingest/PDF/` — PDFs
- `000_Ingest/Screenshots/` — images (skip markitdown, go to Step 1.5)
- `000_Ingest/Videos/` — videos (skip markitdown, run `process_video_ingest.py`)

---

## Step 1: Classify the File

Read the file and determine:

### Content Type (`type` field)

| Type | Signals |
|------|---------|
| `bookmark` | Clipped from web, has source URL, no deep technical content |
| `api-doc` | Contains endpoints, authentication, request/response examples |
| `tool-doc` | Overview of a tool, what it does, how to use it generally |
| `tutorial` | Step-by-step instructions for accomplishing something |
| `model-doc` | AI model specs, pricing, capabilities, comparisons |
| `prompt` | A reusable prompt template |
| `reference` | Style guide, design system, visual reference |
| `case-study` | Analysis of a specific example or project |
| `script` | Code or automation script |
| `workflow` | A process map, flowchart, or operational workflow reference |
| `project-idea` | A raw project concept, seed, or future build note |
| `design-inspiration` | A visual inspiration reference or aesthetic bookmark |
| `personal` | A non-business reference or personal-interest capture |
| `research` | A benchmark, comparison, channel study, market study, or analysis capture |
| `doc` | General documentation that doesn't fit above |
| `image` | Any image file (.png, .jpg, .jpeg, .webp, .gif, .svg) |
| `pdf` | PDF document (.pdf) |
| `word-doc` | Word document (.docx, .doc) or other unreadable binary |

### Topic Domain (determines Wiki/Asset routing)

| Domain | Destination | Signals |
|--------|-------------|---------|
| AI agents, Claude, LLMs, agent frameworks | `000_Wiki/AI-Agents/` | Claude, GPT, agents, MCP, LangChain, orchestration |
| RAG, memory, vector databases, embeddings | `000_Wiki/RAG-Systems/` | RAG, embeddings, Pinecone, Chroma, memory systems |
| App development, APIs, coding tools | `000_Wiki/App-Dev/` | React, Next.js, Supabase, APIs, SDKs, coding |
| Content strategy, marketing, copywriting | `000_Wiki/Content-Strategy/` | content, SEO, marketing, social media, email |
| System architecture, workflows, automation | `000_Wiki/Architecture/` | workflows, automation, n8n, pipelines, systems design |
| Video production, animation, image generation | `000_Wiki/Video-Production/` | video, animation, Remotion, kie.ai, fal.ai, Midjourney, image gen |
| Visual assets, images, design files | `007_Resource_Library/[category-based subfolder]/` | images, mockups, screenshots, design assets |

If a file spans multiple domains, pick the primary one.

---

## Step 1.5: Media Analysis & Renaming (Images and Binary Files Only)

**Skip this step for `.md`, `.txt`, `.json`, `.csv`, and other text-readable files.**
**PDFs:** Skip renaming — proceed directly to Step 3 (route to `Docs/`).

### Lookup-First Gate — Run Before Any Vision Call

Before calling vision or the rename script, check whether each file is already properly cataloged. This avoids wasting API calls on files that have already been described.

**Run the audit script:**
```bash
python /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/check_vision_needed.py "/path/to/images"

# Pipe-friendly list of only files that need vision:
python /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/check_vision_needed.py "/path/to/images" --needs-vision-only
```

The script checks each file's Asset Note for filler descriptions. A file is flagged as **needs vision** if any of:
- No Asset Note exists
- `ai_description` contains: "likely a saved reference", "general visual reference", "This appears to be a screenshot of…", "for later comparison or idea capture"
- Description is under 60 characters

**Decision:**
- Already cataloged (real description found) → skip vision, proceed to Step 3
- Needs vision → continue to rename step below

### Semantic Image Extraction (Vision Required)

Run the image ingestion script on files the audit flagged (or just pass the whole folder):
```bash
python /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/process_image_ingest.py "/path/to/images"
```

The script uses OpenRouter vision first (qwen model), then OpenAI vision as the fallback if OpenRouter is unavailable or fails. It semantically extracts the content (Tools, Tutorials, Workflows, Research, Ideas), generates `Title-Case-With-Dashes.md` files in the appropriate folders, and leaves the raw image in `Visual_Assets/`.

**Important:** Do not use OCR as the default screenshot path. OCR is not the primary ingest strategy here and should only be used if Tony explicitly asks for it or a separate OCR workflow is being implemented.

**CRITICAL:** Once an image is processed by this script, the raw image stays in `Visual_Assets/`. Only the paired note is routed. **Skip Steps 2 and 3 for image files.**

---

## Step 2: Add YAML Frontmatter (Text Files Only)

For `.md`, `.txt`, `.json`, `.csv`, and other text-readable files — add YAML frontmatter before moving:

```yaml
---
title: "Human-Readable Title"
type: bookmark|api-doc|tool-doc|tutorial|model-doc|prompt|reference|case-study|script|workflow|project-idea|design-inspiration|personal|research|doc
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
- Minimum 2 tags, maximum 5 tags.
- All lowercase, kebab-case (dashes not spaces): `video-generation` not `Video Generation`
- No camelCase, no PascalCase, no spaces, no quotes around tags
- Use rich semantic tags (e.g., `ai-automation`, `agentic-ai`, `video-editing`) so flat folders can be easily filtered.

**Skip this step for image files and binary files** — they get an Asset Note in Step 4 instead.

---

## Step 3: Route the Original File to Resource Library

> **DIRECTORY REFERENCE:** Before routing, you MUST read `007_Resource_Library/Directory.md` to understand the exact definitions and constraints of each destination folder.

Move (not copy) the file to the correct subfolder based on the definitions in `Directory.md`:

| Content Type | Destination |
|-------------|-------------|
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
| `image` | Automatically routed by `process_image_ingest.py` (Skip manual routing) |
| `video` (Requires package creation) | `007_Resource_Library/Videos/[Kebab-Case-Name]/` |

**Special Video Handling Rule:**
For `video` types (`.mp4`, `.mov`, `.avi`, etc.), execute the automated ingestion pipeline script instead of moving it manually:
```bash
python /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/process_video_ingest.py "/path/to/the/video.mp4"
```
This script will automatically generate a descriptive `Title-Case-With-Dashes` package name, rename the video file itself, extract scene-detected keyframes via FFmpeg, transcribe the audio via Whisper, and generate the proper scaffold markdown files in `007_Resource_Library/Videos/`.

**Naming rule:** the video folder, MP4, transcript scaffold, and tutorial scaffold must all share the same descriptive stem. Acronyms stay uppercase (`AI`, `API`, `MCP`), and the first letter of every other word is capitalized.

All files: use `Title-Case-With-Dashes` naming. No exceptions — images, notes, and text files all follow this rule.

---

## Step 4: Create a Wiki Page or Asset Note

### Text Files → Wiki Page

Create a NEW file in the appropriate `000_Wiki/` subfolder. This is NOT a copy of the original — it is a synthesized knowledge page.

If the ingested text file is itself a routed reference note for `Prompts`, `Design_Inspiration`, `Personal`, `Research`, `Tools`, `Tutorials`, `Workflows`, or `Project_Ideas`, move it into the matching `007_Resource_Library/` folder instead of synthesizing a wiki page.

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

The wiki page title should be the concept or tool name, not the article title.

### PDFs → No Asset Note Needed

Obsidian has a native PDF viewer. PDFs routed to `007_Resource_Library/Docs/` are readable directly in Obsidian — no companion file needed. Only create a wiki page if the PDF contains content worth synthesizing (e.g., a technical reference or research paper).

### Images

Images no longer use generic "Asset Notes." They are processed automatically by the `process_image_ingest.py` script in Step 1.5, which creates rich semantic markdown notes and leaves the image in `Visual_Assets/`. If you are processing an image, you should have already skipped this step.

### Media Notes

Media notes are the routed objects, not the raw images. Move the note into the correct category folder under `007_Resource_Library/` based on the image's topic. If the proper category folder does not already exist, skip that item and queue it for the end of the batch. Do **not** create new directories without Tony's explicit approval. When the batch is finished, ask Tony how to name or create any missing category folders before moving those remaining notes.

### Routing Categories for Media Notes

Use these routing categories when classifying image-derived notes:

| Category | Route | Use When |
|----------|-------|----------|
| `tools` | `007_Resource_Library/Tools/` | The image shows a SaaS, app, plugin, workflow tool, website, or software product. |
| `tutorials` | `007_Resource_Library/Tutorials/` | The image is teaching a process, walkthrough, lesson, or how-to workflow. |
| `workflows` | `007_Resource_Library/Workflows/` | The image is primarily a process map, flowchart, or operational workflow reference. |
| `prompts` | `007_Resource_Library/Prompts/` | The image contains a reusable prompt, prompt formula, prompt library, or prompt example. |
| `design-inspiration` | `007_Resource_Library/Design_Inspiration/` | The image is mainly aesthetic inspiration, a design reference, or a channel/profile/style bookmark. |
| `personal` | `007_Resource_Library/Personal/` | The image is a personal-interest capture, tour flyer, or other non-business bookmark. |
| `research` | `007_Resource_Library/Research/` | The image is a benchmark, comparison, channel study, market study, or analysis capture. |
| `docs` | `007_Resource_Library/Docs/` | The image is reference material, documentation, API/spec material, forms, manuals, or general written reference. |
| `investments` | `007_Resource_Library/Investments/` | The image is market-related, stock/crypto research, portfolio screenshots, or finance/investing analysis. |
| `models` | `007_Resource_Library/Models/` | The image is about AI models, model comparisons, pricing, benchmarks, or model deployment. |
| `videos` | `007_Resource_Library/Videos/[Descriptive-Name]/` | The image belongs to a video knowledge package, clip, or video-specific reference set. |
| `archive` | `007_Resource_Library/Archive/` | The image note is obsolete, low-value, or intentionally archived after review. |
| `project-ideas` | `007_Resource_Library/Project_Ideas/` | The image or note captures a raw project concept, future build seed, or idea note. |

If a note does not clearly fit one of the existing routes above, leave it queued until the end of the batch and ask Tony before assigning a category or creating a folder.

### Image Routing Decision Order

When an image could fit more than one route, use this order:

1. **Prompts** if the screenshot is primarily reusable prompt text that Tony wants converted into text.
2. **Tutorials** if the screenshot is primarily a walkthrough, lesson, or how-to video reference.
3. **Workflows** if the screenshot is primarily a process map, flowchart, or operational workflow reference.
4. **Design Inspiration** if the screenshot is mainly an aesthetic reference, visual inspiration, or profile/channel style bookmark.
5. **Personal** if the screenshot is a personal-interest capture or non-business bookmark, like a concert or tour flyer.
6. **Research** if the screenshot is primarily a benchmark, comparison, channel study, market study, or analysis capture.
7. **Tools** if the screenshot is primarily a software product, SaaS, plugin, app, or GitHub repo. A visible URL, repo name, or captions identifying the product are strong signals for Tools.
8. **Docs** only if the screenshot is primarily reference material, API/configuration info, or curl/HTTP request examples.
9. **Investments** if the image is finance or market related.
10. **Models** if the image is about AI models, pricing, benchmarks, or deployment.
11. **Videos** if it is part of a video knowledge package.
12. **Archive** only if the item is intentionally retired or low-value.

If the screenshot is ambiguous and the winning category is not obvious, queue it for the end of the batch and ask Tony rather than guessing or creating anything new.

**Preservation rule:** Do not trash or destructively delete source files during ingest or cleanup. Preserve originals unless the routing decision is explicit and points to an existing destination. If something is no longer active, move it only when Tony has approved the destination; otherwise leave it in place and ask.

### Word Docs

Create a companion `.md` file in `007_Resource_Library/Docs/` summarizing the content and purpose. **Do NOT create a wiki page for word docs.**

---

## Step 5: Cross-Link

After creating the wiki page (text files only):

1. Search `000_Wiki/` for any existing pages that mention the same tool/concept
2. Add a `[[link]]` to the new wiki page in those related pages (under their `## Related` section)
3. If no related pages exist, skip — don't force links

Skip cross-linking for media files and asset notes.

---

## Step 6: Update Log and Index

### log.md (`000_Wiki/log.md`)
Append one line per ingested file:
```
## [YYYY-MM-DD] ingest | Title
Source: [original filename] → [destination in Resource Library]
Wiki/Asset Note: [path to new file created]
```

Create `log.md` if it doesn't exist.

### index.md (`000_Wiki/index.md`)
For text wiki pages only — add or update the entry under the correct category section:
```
- [[Wiki Page Title]] — one-line description
```

Create `index.md` with category headers if it doesn't exist. Skip for media/asset notes.

---

## Step 7: Run Graphify

After all files are processed, run from the workspace root:

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS && graphify update .
```

---

## Batch Ingest

When processing the entire `000_Ingest/` folder:
- Recurse into all subfolders by default
- Process files one at a time
- Run graphify ONCE at the end, not after each file
- Report a summary: how many files processed, where each one landed, how many asset notes created

## Single File Ingest

When the user says "ingest [filename]" or "process this file":
- Process that one file through all steps
- Run graphify at the end

---

## File Naming

All files in this workspace follow:
- No spaces — use `_` or `-`
- Capitalize first letter of every word: `Kie-Ai-API-Reference.md`
- Acronyms stay uppercase: `MCP`, `API`, `RAG`
- Python scripts (.py) are exempt from renaming
- Media files use Title-Case-With-Dashes generated during Step 1.5 vision analysis (same rule as all other files)
