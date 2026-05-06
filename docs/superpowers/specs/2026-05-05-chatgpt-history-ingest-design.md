# ChatGPT History Ingest — Design Spec
**Date:** 2026-05-05  
**Status:** Approved  
**Cost:** $0 beyond existing Claude + Gemini subscriptions

---

## Goal

Ingest Tony's full ChatGPT export (2,011 conversations) into the Claude-Agent workspace as a **second-brain profile layer** — synthesized thematic documents that teach agents who Tony is: how he thinks, ideates, and operates. Not an archive; a distillation.

---

## Source Data

**Location:** `007_Resource_Library/OpenAI_History/`

| Content | Count | Format |
|---------|-------|--------|
| Conversations | 2,011 | 21 × `conversations-*.json` |
| DALL-E images | 161 | `dalle-generations/*.webp` |
| Conversation-attached images | ~4,900 | Hash-named PNG/JPEG in UUID subdirs + root |
| PDFs / uploaded docs | ~48 | Skip — not needed |
| User profile folder | 1 | `user-HG5CoGIU59jAcjFPgScwmHxN/` — skip |

Images inside conversations are referenced via `file-service://` asset pointers in JSON. UUID-named subdirectories (e.g. `6939fa4f.../image/`) contain conversation-specific image exports.

---

## Architecture

Three phases — two scripts + one interactive Claude Code session:

```
OpenAI_History/ (raw export)
        │
        ▼
[phase1_theme_discovery.py]  ← pure Python, no LLM
        │
        ▼
ChatGPT_Theme_Report.md  ← Tony reviews, deletes unwanted themes
        │
        ▼
[Claude Code — Phase 2 interactive distillation]
        │
        ▼
001_Architecture/Memory/ChatGPT_Profile/
    ├── Tony-POD-Design-Thinking.md
    ├── Tony-Content-Strategy-Patterns.md
    ├── Tony-Systematic-Planning-Style.md
    └── ... (20–50 files)

[phase3_image_pipeline.py]  ← runs independently, pure Python
        │
        ▼
007_Resource_Library/Obsidian_Attachments/OpenAI_Images/
    └── vision-renamed images
007_Resource_Library/Research/
    └── asset notes (one per image)
```

---

## Phase 1 — Theme Discovery Script

**File:** `001_Architecture/Scripts/phase1_theme_discovery.py`  
**Runtime:** Pure Python, no LLM calls, no API credits  
**Input:** All `conversations-*.json` in `OpenAI_History/`  
**Output:** `007_Resource_Library/OpenAI_History/ChatGPT_Theme_Report.md`

### What it does
1. Reads all 21 JSON files, extracts per conversation: `title`, `create_time`, `conversation_id`, `default_model_slug`, first user message (≤200 chars)
2. Groups conversations into themes using keyword/title pattern matching (no LLM — keyword rules are sufficient for a first-pass draft)
3. Outputs a markdown table sorted by conversation count descending

### Output format
```markdown
| Theme | Count | Sample Titles |
|-------|-------|---------------|
| POD & Print-on-Demand Design | 87 | "Fishing Pun T-Shirts", "Zodiac Signs Poster"... |
| Content Strategy & YouTube | 134 | "Budapest Nightlife Highlights", "IV League SEO"... |
| Personal Health | 23 | "Supplement Stack", "Sleep Optimization"... |
| Vegas / Gambling | 11 | "Blackjack Strategy", "Poker Odds"... |
```

### Tony's action
Review the report. Delete rows for themes to exclude (personal health, gambling, Google-replacement queries, etc.). Optionally rename or merge themes. Save file. Then trigger Phase 2.

---

## Phase 2 — Thematic Distillation (Interactive)

**Runtime:** Claude Code session — covered by Claude subscription, zero API cost  
**Input:** Approved `ChatGPT_Theme_Report.md` + full conversation JSON files  
**Output:** `001_Architecture/Memory/ChatGPT_Profile/` — one MD per approved theme

### What happens
Tony tells Claude to run Phase 2. Claude:
1. Reads the approved theme list
2. For each theme, loads the matching conversation content from JSON
3. Synthesizes a thematic profile document focused on extracting *who Tony is* — not summarizing conversations, but surfacing:
   - How Tony approaches this domain
   - Recurring frameworks, vocabulary, mental models
   - Prompt style signals (systematic, iterative, visual-first, etc.)
   - Strong preferences and opinions revealed across conversations
4. If a theme has 100+ conversations, Claude processes in sub-batches and synthesizes upward
5. If `image_map.json` exists (Phase 3 already ran), injects relevant image links

### Output document structure
```markdown
---
tags: [chatgpt-profile, <domain-tag>, tony-patterns]
source: chatgpt-export-2026
conversations: <count>
date-synthesized: 2026-05-05
---

# Tony's [Theme Name]

## How Tony Thinks About This Domain

## Recurring Frameworks & Vocabulary

## Prompt Style Signals

## Key Preferences & Opinions

## Related Images
```

### Batching strategy
Large sessions will process themes in groups across multiple Claude Code sessions if needed (token budget). Each session picks up where the last left off using a simple `phase2_progress.json` checkpoint file.

---

## Phase 3 — Image Pipeline

**File:** `001_Architecture/Scripts/phase3_image_pipeline.py`  
**Runtime:** Pure Python + existing `process_image_ingest.py` (Gemini API for vision rename)  
**Input:** `dalle-generations/` + UUID conversation subdirs in `OpenAI_History/`  
**Output:** See below  
**Runs independently** — does not depend on Phase 1 or 2 completing first

### What it does
1. Collects images from both sources (DALL-E folder + UUID subdirs)
2. **Copies** (never moves) to `007_Resource_Library/Obsidian_Attachments/OpenAI_Images/`
3. Calls existing `process_image_ingest.py` for vision rename + asset note creation
4. Asset notes land in `007_Resource_Library/Research/` per existing pipeline pattern
5. Builds `image_map.json` in `OpenAI_History/`: `{ original_filename: { renamed: "...", conversation_id: "..." } }`

### image_map.json purpose
Phase 2 reads this file to inject `![[image-name.webp]]` links into the relevant thematic MD where the image's source conversation belongs to that theme.

---

## Output Structure

```
001_Architecture/Memory/ChatGPT_Profile/       ← agent second-brain layer
007_Resource_Library/OpenAI_History/
    └── ChatGPT_Theme_Report.md                ← Tony's curation checkpoint
007_Resource_Library/Obsidian_Attachments/
    └── OpenAI_Images/                         ← vision-renamed images
007_Resource_Library/Research/
    └── [image asset notes]                    ← searchable image mini-wiki
001_Architecture/Scripts/
    ├── phase1_theme_discovery.py
    └── phase3_image_pipeline.py
```

---

## Run Order

| Step | Action | Who |
|------|--------|-----|
| 1 | Run `phase1_theme_discovery.py` | Tony / Claude |
| 2 | Review + edit `ChatGPT_Theme_Report.md` | Tony |
| 3 | Tell Claude "run Phase 2" | Tony |
| 4 | Claude distills approved themes interactively | Claude Code |
| 5 | Run `phase3_image_pipeline.py` anytime | Tony / Claude |

---

## What to Skip

- Uploaded PDFs and documents — excluded unless they directly add second-brain value (Tony's call per theme)
- `user-HG5CoGIU59jAcjFPgScwmHxN/` profile folder — skip
- Personal health conversations — Tony will remove from theme report
- Vegas/gambling/Google-replacement queries — Tony will remove from theme report

---

## Implementation Notes

- All scripts use `001_Architecture/Scripts/` as home directory
- Scripts follow existing naming conventions (snake_case `.py`)
- Phase 1 outputs a markdown file Tony can edit directly in Obsidian
- Phase 2 uses a `phase2_progress.json` checkpoint so large distillation jobs survive session limits
- Phase 3 calls `process_image_ingest.py` — requires `GEMINI_API_KEY` in `~/.env-secrets`
- Implementation handed to Codex CLI to preserve Claude subscription tokens
