---
title: "Resource Library — Dedup Actions (Claude's recommendations)"
type: report
created: 2026-09-05
note: "Claude read all 32 files in the 14 exact + 3 medium clusters. Merges below were already applied to the KEEP files. Deletions are for Tony to execute (never-delete rule)."
---

# Dedup Actions — 16 notes recommended for deletion

> **STATUS: DONE 2026-09-05.** All 16 deletions executed and the 4 keeper merges
> applied. Re-run of the dedup script shows only the 2 "keep both" pairs + 9 low
> index-collisions remaining — nothing actionable. This file is kept as the record.

Claude read both notes in every `exact` and `medium` cluster. The 3 content merges
needed to make deletion lossless have **already been applied** to the KEEP files
(Mixamo tags, Scade-Pro description, Gobii tag, Flowise-AI description).

## Safe to delete — content is fully preserved in the KEEP file

| Delete | Keep | Reason |
|---|---|---|
| `Prompts/Copywriting-Hooks-Prompt.md` | `Prompts/Copywrite-Hook-Prompts.md` | Identical body. Keeper has proper Agent-OS frontmatter. |
| `Prompts/Get-Better-Writing-Out-Of-Chat-GPT.md` | `Prompts/Get-Better-Writing.md` | Identical body. Keeper has proper frontmatter. |
| `Prompts/Prompt-For-Marketing.md` | `Prompts/Marketing-Prompts.md` | Identical body. Keeper has proper frontmatter. |
| `Prompts/SEO-Prompting.md` | `Prompts/Chatgpt-SEO-Plugin.md` | Same prompt text. Keeper has proper frontmatter. |
| `Prompts/Drafting-Prompts.md` | `Prompts/Get-The-Best-Out-Of-Chatgpt.md` | Identical body. Keeper has proper frontmatter. |
| `Tools/Buildthatidea.md` | `Tools/Build-That-Idea.md` | Same description (one word). Keeper has the cleaner name. |
| `Tools/Coderabbit.md` | `Tools/Code-Rabbit.md` | Same tool. Keeper uses `Category:`, dup uses legacy `Tag:`. |
| `Tools/Freepik-2.md` | `Tools/Freepik.md` | `Freepik-2` is a 91-byte stub ("AI Suite"). Keeper is the full model list. |
| `Tools/Open-Router-2.md` | `Tools/Open-Router.md` | Byte-identical. |
| `Tools/Prd-Generator-2.md` | `Tools/Prd-Generator.md` | Byte-identical. |
| `Tools/Gobii-2.md` | `Tools/Gobii.md` | Near-identical. **"API" tag merged into keeper.** |
| `Tools/Mixamo-2.md` | `Tools/Mixamo.md` | Keeper has the better description. **"3D" + "Video" tags merged into keeper.** |
| `Tools/Scade-Pro-2.md` | `Tools/Scade-Pro.md` | **Dup's "no-code app builder" description merged into keeper.** |
| `Tools/Flowise-AI-2.md` | `Tools/Flowise-AI.md` | **Dup's richer description merged into keeper** (keeper already had the API/LLM tags). |
| `Tutorials/Claude-Code-YouTube-Video-Editing/Claude-Code-Plus-YouTube-Video-Editing-20-000month-1.md` | `Tutorials/Claude-Code-YouTube-Video-Editing/Claude-Code-YouTube-Video-Editing-Transcript.md` | Same video transcript, ingested twice from two `000_Ingest/` paths. Keeper has the cleaner title + tags. |
| `Tutorials/Higgsfield_YT_Pipeline/Higgsfield-Faceless-Channel-Transcript.md` | `Tutorials/Higgsfield_YT_Pipeline/Higgsfield-AI-Faceless-Channel-Bookmark.md` | The Bookmark file contains the **full, cleaner transcript** PLUS the video description, timestamps and links. The Transcript file is a strict subset. |

## NOT duplicates — keep both

- `Tutorials/Robonuggets-Faceless-Any-Subject-N8N-Automation.md` + `Tutorials/Shorts-Workflow.md`
  — `Shorts-Workflow.md` is a curated priority list of shorts-workflow videos that
  *links to* the Robonuggets tutorial. Different purpose.
- `Tutorials/Johnny-Harris-Tutorial-Template-Files.md` + `Tutorials/VOX-Style-Documentary-Tutorial-Template.md`
  — Same creator ("Lilly's Tech Tips"), shared boilerplate text, but **different Google
  Drive template links and different Patreon posts**. Two different templates.
- All 9 `low`-confidence rows in `_Dedup_Review.md` — mostly old link-list category
  notes colliding with atomic tool notes.

## One-shot deletion (run when you've eyeballed the list)

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS/007_Resource_Library
rm "Prompts/Copywriting-Hooks-Prompt.md" \
   "Prompts/Get-Better-Writing-Out-Of-Chat-GPT.md" \
   "Prompts/Prompt-For-Marketing.md" \
   "Prompts/SEO-Prompting.md" \
   "Prompts/Drafting-Prompts.md" \
   "Tools/Buildthatidea.md" \
   "Tools/Coderabbit.md" \
   "Tools/Freepik-2.md" \
   "Tools/Open-Router-2.md" \
   "Tools/Prd-Generator-2.md" \
   "Tools/Gobii-2.md" \
   "Tools/Mixamo-2.md" \
   "Tools/Scade-Pro-2.md" \
   "Tools/Flowise-AI-2.md" \
   "Tutorials/Claude-Code-YouTube-Video-Editing/Claude-Code-Plus-YouTube-Video-Editing-20-000month-1.md" \
   "Tutorials/Higgsfield_YT_Pipeline/Higgsfield-Faceless-Channel-Transcript.md"
```

Checked 2026-09-05: **none of the 16 deletion targets have inbound `[[wikilinks]]`**
from anywhere in `007_Resource_Library/` or `000_Wiki/`, so the deletions are clean.
Re-run `python3 001_Architecture/Scripts/resource_library_dedup.py` afterward to
confirm.
