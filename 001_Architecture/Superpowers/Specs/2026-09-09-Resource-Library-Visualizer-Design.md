---
title: "Resource Library Visualizer — Design"
type: design-spec
category: architecture
created: 2026-09-09
tags:
  - resource-library
  - tooling
  - internal-tool
  - review-workflow
---

# Resource Library Visualizer — Design

## Purpose

A local, browser-based gallery for reviewing the `007_Resource_Library` note
collection — "Adobe Lightroom for screenshots." The Resource Library is a
fuzzy-queryable bookmarked reference library; its value depends on staying
**trustworthy**, and AI-ingested notes go stale or get mislabeled fast. Tony
does not browse the vault in Obsidian (dislikes the UI), so this tool is the
review surface.

**Primary job: culling.** Secondary jobs: catching Vision mislabels (wrong
title / wrong URL / wrong subject) and queueing fix requests for the agent.

## Scope

### In scope

- Read every `.md` in `007_Resource_Library/` (recursively).
- **Default gallery view:** notes that embed an image OR embed/link a YouTube
  video.
- **Text-only toggle (off by default):** notes with no image — rendered as a
  color-coded `.md` glyph card instead of a thumbnail.
- Gallery grid of cards (Notion-gallery style).
- Detail view: full note rendered Obsidian-style (inline image embeds,
  YouTube embeds, wikilinks, callouts).
- Filters: folder, source type, top-N tags.
- Sort: most-recently-ingested first.
- Bulk select → **Delete** (move to `~/Desktop/delete/`) and **Re-run AI**.
- Per-card: **Edit** (structured fields), **Re-run AI**, **Add Comment**.
- A persistent **Review Queue** markdown file the agent later actions.

### Out of scope (v1)

- Editing anything outside `007_Resource_Library`.
- Bulk retag / bulk move / merge (revisit only if mislabeling proves chronic).
- Any write to git / committing (Tony reviews the diff separately).
- Multi-user, auth, remote hosting.
- A real WYSIWYG markdown editor.
- An ignore list for structural `.md` files — they stay visible, distinguished
  by glyph, and Tony knows not to touch them.

## Architecture

Two pieces:

### 1. Local server — one Python file (`serve.py`, Flask or FastAPI)

Responsibilities:

- Scan `007_Resource_Library/` on startup, build an in-memory index of notes.
- Pair each note with its sibling image by the co-location rule: same folder,
  same name stem (`Tools/OpenCode.md` ↔ `Tools/OpenCode.png`). No `![[...]]`
  resolver, no index file — just a directory listing. (Fallback: if no
  same-stem sibling exists, parse the first `![[...]]` / `![](...)` embed in
  the body.)
- Generate a thumbnail cache (280px JPEG) mirroring the seed script
  (`build_image_cull.py`). Cache dir: `~/.cache/rl_visualizer/thumbs/`.
  Regenerated only when the source image mtime is newer.
- Serve full-resolution images on demand for the detail view.
- Render note markdown to HTML Obsidian-style for the detail view.
- Compute the top-8 tags across the visible corpus for the filter bar.

HTTP endpoints:

| Method + path | Purpose |
|---|---|
| `GET /` | The single-page app shell. |
| `GET /api/notes` | Index: every card's metadata (see Data Model). |
| `GET /api/note?path=…` | One note: raw frontmatter fields + rendered body HTML. |
| `GET /thumb?path=…` | Cached thumbnail JPEG. |
| `GET /img?path=…` | Full-res image (detail view). |
| `PATCH /api/note` | Save edited fields for one note (rewrites the `.md`). |
| `POST /api/delete` | Move `[paths]` (+ sibling images) to `~/Desktop/delete/`. |
| `POST /api/rerun-ai` | Re-run ingest Vision on `[paths]`; return before/after. |
| `POST /api/comment` | Append a comment for one note to the Review Queue. |
| `POST /api/queue/finalize` | Seal the current queue batch; return its text. |

Run: `python 001_Architecture/Tools/Resource-Library-Visualizer/serve.py`
then it opens `http://localhost:8756` in the browser. Docker packaging is a
possible later add, not v1.

### 2. Browser SPA — single HTML file with inline CSS/JS

No build step, no framework required (vanilla JS is fine; the seed pages are
the pattern). Talks only to the local server. Holds transient UI state
(current filters, selection) in memory; nothing authoritative lives in
`localStorage` — the server and the `.md` files are the source of truth.

## Data Model — card metadata (`GET /api/notes`)

Per note:

```
{
  "path":        "Tools/OpenCode.md",          // relative to 007_Resource_Library
  "title":       "OpenCode",                    // frontmatter title, fallback filename stem
  "summary":     "One-sentence description.",    // frontmatter summary
  "folder":      "Tools",                        // top-level category folder
  "tags":        ["ai", "github-repo"],          // frontmatter tags
  "thumb":       "/thumb?path=Tools/OpenCode.png",
  "kind":        "image" | "youtube" | "text",
  "source_label": "Screenshot" | "YouTube" | "Bookmark" | null,
  "vision_risk": true,                            // Vision-derived → needs scrutiny
  "md_glyph_color": "#rrggbb",                    // only when kind == "text"
  "ingested_at": "2026-09-05"                     // enriched → created → mtime
}
```

## Card anatomy

Notion-gallery style. Top to bottom:

1. **Thumbnail** (image, YouTube poster frame, or colored `.md` glyph).
   - YouTube poster: `https://img.youtube.com/vi/<id>/hqdefault.jpg`, derived
     from the URL in the note.
2. **Title** (from the `.md` filename / frontmatter title).
3. **Short description** (one sentence, from `summary:`).
4. **Folder pill** — one of: Project_Ideas, Prompts, Research, Tools,
   Tutorials, Workflows, Models, Docs, Design_Inspiration, Personal,
   Investments, … (the category folders). Doubles as the color-code.
5. **1–2 supporting tag pills** (soft Notion palette — muted, aesthetically
   pleasing, e.g. the blue/pink/green of the Notion "city" tags).
6. **Colored source label**, right-aligned on its own line — `YouTube`,
   `Screenshot`, or `Bookmark`. `Screenshot` uses a warning color because
   those are the Vision-error-prone notes.

Footer lines 4, 5, 6 are **separate lines**, not one row.

## Source-label & badge detection (heuristic, ~90% accuracy — acceptable)

Read from frontmatter / filename:

| Signal | Result |
|---|---|
| `url:` / `source:` is a `youtube.com` / `youtu.be` link, or body has a YouTube embed | `YouTube` |
| `original_filename: IMG_####.PNG` (iPhone) | `Screenshot`, `vision_risk = true` |
| `screenshot` in `tags:` | `Screenshot` |
| `source:` is a web URL **and** body contains a clipped page (Obsidian Web Clipper structure) | `Bookmark` |
| no image, structural filename (`*review*.md`, `*log*.md`, `*REGISTRY*`, `Directory.md`, `AGENTS.md`, …) | `kind = text`, structural glyph color |
| none of the above, has image | `Screenshot` (default for image notes) |

`md_glyph_color` for text cards is derived from folder + `type:` / `form:`
frontmatter, mapped to ~6–8 palette colors (structural/system = one distinct
color; Tools, Models, Tutorials, Research, Prompts, Workflows each get one;
no-frontmatter = neutral gray). No hand-maintained registry — pure derivation.

## Filters & sort

Three filter rows above the grid:

1. **Folder buttons** — one toggle per category directory.
2. **Source type** — `YouTube` / `Screenshot` / `Bookmark`.
3. **Tags** — the 8 most-used tags across the corpus, as toggles.

Multiple filters within a row = OR; across rows = AND. A search box
(filename / title contains) like the seed page.

**Default sort:** `ingested_at` descending (most recent first).

## Detail view

Click a card → slide-over or full-screen panel showing the note rendered as
Obsidian would:

- `![[image.png]]` / `![](…)` → inline `<img>` (served via `/img`).
- YouTube links / embeds → inline iframe player.
- `[[wikilinks]]` → rendered as text/links (no navigation target needed in v1;
  just don't show raw `[[ ]]`).
- `> [!note]` callouts → styled callout blocks.
- Frontmatter shown as a clean key/value header block, not raw YAML.

From the detail view: **Edit**, **Re-run AI**, **Add Comment**, **Delete**.

## Actions

### Delete (bulk + per-card) — immediate

- Server moves the `.md` **and its sibling image(s)** to `~/Desktop/delete/`
  (preserving enough path to disambiguate, e.g. `~/Desktop/delete/Tools/…`).
- Card disappears from the grid immediately (visual confirmation the action
  ran).
- Also logged to the Review Queue (paper trail).
- **Not** a real delete — Tony reviews `~/Desktop/delete/` manually before
  removing anything.

### Edit (per-card) — immediate

Edit toggle in the detail view reveals structured fields:

- **Title**
- **Description / summary**
- **URL**
- **Tags** (comma-separated or chip input)
- **Body** (plain `<textarea>` — only needed when the mislabel is deeper)

Save → `PATCH /api/note` → server rewrites that one `.md` (frontmatter fields
updated in place, body replaced if edited). No markdown toolbar.

### Re-run AI (bulk + per-card)

- Re-invokes the ingest Vision step (`process_image_ingest.py` logic) on the
  selected note's image.
- Returns before/after frontmatter; Tony accepts (writes it) or rejects
  (no change).

### Add Comment (per-card)

- Free-text (Tony dictates via Wispr Flow): "should be design-inspiration not
  graphic-design," etc.
- Appended to the Review Queue against that note's path.
- No direct `.md` edit — the agent actions these later.

## Review Queue file

Path: `~/Desktop/Resource_Library_Review/Review_Queue.md`

The tool appends entries as they happen. Format:

```markdown
## Batch — open (started 2026-09-09 14:22)

- [ ] COMMENT  Tools/Some-Note.md
      "This should be tagged design-inspiration instead of graphic-design."
- [x] DELETE   Research/Old-Thing.md  (moved to ~/Desktop/delete/ 14:25)
- [ ] COMMENT  Prompts/Another.md
      "Title is wrong — the screenshot is a GitHub repo, not a Photoshop plugin."
```

**Finalize Queue** button → seals the current batch:

```markdown
## Batch — FINALIZED 2026-09-09 15:10  (12 comments, 34 deletes)
```

…and starts a fresh open batch. On finalize, the tool surfaces the batch text
(copy button + download) so Tony hands it to the agent. The agent then works
the unchecked `COMMENT` lines.

## File layout

```
001_Architecture/Tools/Resource-Library-Visualizer/
├── serve.py            # the local server (single file)
├── app.html            # the SPA (inline CSS/JS)
├── render.py           # markdown → Obsidian-style HTML
├── detect.py           # source-label / vision-risk / glyph-color heuristics
└── README.md
```

(Directory name needs Tony's OK before creation — workspace rule.)

Thumbnail cache: `~/.cache/rl_visualizer/thumbs/` (outside the repo).

## Reused / referenced code

- `001_Architecture/Scripts/build_image_cull.py` — thumbnail generation,
  grid rendering, filter-chip, localStorage pattern (seed).
- `001_Architecture/Scripts/note_review.py` — note-card review pattern (seed).
- `001_Architecture/Scripts/process_image_ingest.py` — the Vision re-run logic.
- `001_Architecture/Skills/ingest/SKILL.md` — frontmatter contract (title,
  type, form, summary, url, tags).

## Open questions / decisions deferred to build

- Flask vs FastAPI — pick during build (Flask is lighter; either is fine).
- Exact port (proposed 8756).
- Whether `Re-run AI` needs a spend guard (Vision API cost per call) — likely
  a simple "you're about to re-run N notes, ~$X" confirm.
- `~/Desktop/delete/` path collision handling when two notes share a stem
  across folders (mirror the folder into the delete dir).

## Success criteria

- Tony opens the tool and sees every image/YouTube note in
  `007_Resource_Library`, newest first, in a Notion-style grid, in one page
  load (thumbnails lazy-load).
- He can filter to a folder / source type / tag and the grid updates instantly.
- He can multi-select 50 cards, hit Delete, and they're gone from view and
  sitting in `~/Desktop/delete/` — in under a second.
- He can open a mislabeled note, fix the title/URL/tags, save, and the `.md`
  on disk is correct.
- He can dictate a comment on a card, hit Finalize Queue, and hand the agent
  a clean actionable list.
