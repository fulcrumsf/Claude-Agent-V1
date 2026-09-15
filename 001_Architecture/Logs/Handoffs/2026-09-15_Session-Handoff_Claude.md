---
title: "Session Handoff — 2026-09-15 (Claude Code)"
type: handoff
category: session
created: 2026-09-15
updated: 2026-09-15
---

# Session Handoff — READ THIS FIRST next session

## ⚠️ 666 files uncommitted — nothing from this session has been committed

`git status --short` shows 666 changed files (modified/deleted notes from tag/icon cleanup, moved notes, plus new/changed scripts and a whole new tool). Nothing has been committed or pushed. Tony should decide when/how to commit — likely one big commit + rollback tag, mirroring the `resource-library-v3-neon-parcel-shorts-2026-09-11` pattern from the Sep 11 session. Do not commit unprompted.

---

## 1. Resource Library Visualizer (`001_Architecture/Tools/Resource-Library-Visualizer/`, localhost:8756)

- **Emoji glyphs replace the plain ".md" placeholder tile.** Two-layer lookup in `detect.py::glyph_emoji()`: title keyword match first (can override a wrong tag — e.g. "KDP" in the title wins even if mistagged), tag-vocabulary fallback second, `📄` default. Table of ~18 title-keyword rules + all 20 tag→emoji mappings is in that file.
- **Card thumbnails now handle remote-hosted images**, not just local co-located files. `notes.py::first_remote_image()` matches `![...](https://...)` regardless of file extension (CDN/Unsplash URLs have none) and explicitly excludes `notion.so/icons/` (decorative Notion column icons, never content).
- **Lazy og:image fallback for text-only notes with a bookmark URL but no embedded image** — new `url_preview.py` module: fetches the note's own URL, extracts `<meta property="og:image">`, caches every result (hit or miss) on disk forever so a URL is never fetched twice. Wired through a new `/url_thumb` endpoint, called only when a card is actually rendered (never during index build). Needed a `certifi` SSL-cert-bundle fix (same fix `process_image_ingest.py` already had) — macOS framework Python ships without a usable CA bundle for `urllib`.
- **Fuzzy search** — a second search mode alongside the existing instant literal-substring filter. Debounced (400ms after typing stops), shells out to `graphify query "<text>" --graph 007_Resource_Library/graphify-out/graph.json`, parses `src=<path>` lines from the output, unions those paths into the visible results with a `🔮 related` badge on anything that matched via the graph but not literally. Caveat surfaced to Tony and accepted: fuzzy results are only as fresh as the last `graphify update` run.
- **Cleaned 140 `notion.so/icons/*.svg` decorative-icon embeds** out of 30 notes (these were literally showing as the "Aa" font-sample glyph on cards before the fix).
- **`Directory.md` hardening this session** (all now dynamically read by both this tool and `process_image_ingest.py` / `retag_and_retitle.py` — no hardcoded copies):
  - **Digital_Products**: now *information-products only* (ebooks/guides/courses) — explicitly excludes prints/illustrations/wall-art (that loophole was routing physical-product screenshots there).
  - **POD_Prints**: explicitly includes Ikigai Digital's printable-art line — a digital-only print/illustration is still POD_Prints, never Digital_Products.
  - **Mockups**: corrected to the actual test Tony uses — **blank vs. finished**, not "does a frame appear in the shot." A blank frame/poster/shirt meant to have Tony's own art superimposed = Mockups; a frame already showing finished art = Design_Inspiration/Content_Ideas depending on intent.
  - **Personal**: tightened to real-world life captures only (health/food/travel-logistics screenshots — a gluten-free bread, a travel medicine, a vitamin drink, a turmeric-benefits diagram) — explicitly excludes AI-generated character/scene art even when styled like a "selfie" (that's Content_Ideas).
  - **Content_Ideas**: now has concrete, channel-sourced visual-pattern hints (read from all 12 channels' `*_Content_System.md` docs, not just skimmed) — e.g. a BBC-documentary-style animal diagram → Anomalous Wild; a whimsical AI animal video (cats, "bear with grandma") → Neon Parcel; AI-generated historical/mythic imagery → Reimagined Realms/Kingdoms and Conquerors; Polyoculis's distinctive flat "silhouette" 3D art style is a directly recognizable visual signature.
- **Found and fixed a real parser bug**: `process_image_ingest.py`'s `Directory.md` parser only captured the *first line* of each folder/tag bullet, silently truncating every multi-line definition (including the Content_Ideas hardening above) before this was caught. Fixed with a shared `_parse_bullet_section()` that follows indented continuation lines until the next bullet or `## ` header.

## 2. `ingest/SKILL.md` hardening

- Fixed a genuine self-contradiction: "Drop zones (check these subfolders first)" implied `Videos/`/`PDF/`/`Screenshots/` were always auto-scanned, directly contradicting the "never auto-recurse without being asked" rule stated one section above. Now explicitly states these follow the same rule — `Videos/` in particular is never touched without Tony naming it.
- Scope Question rewritten from a 5-option multiple-choice into the conversational flow Tony actually described: top-level vs. subfolder → (if top-level) topic/search vs. "all" → (if subfolder) route by known type (`PDF`/`Images`/`Screenshots`/`Videos` auto-route; anything else — `Pipeline_Orchestration`, `Tiktok_Shop_Video_Dump`, etc. — stops and asks, since those are often deliberately parked outside graphify/wiki for a dedicated pipeline, or are grouped multi-file bundles that per-file classification would break).

## 3. `process_image_ingest.py` hardening (behavior-preserving refactor + real bug fixes)

- **Root cause of "it keeps putting things in the wrong folder"**: `VALID_FOLDERS` was a hardcoded list frozen from before the Sep 11 taxonomy rework — missing `POD_Prints`, `Mockups`, `Content_Ideas`, `Digital_Products`, `Affiliate_Marketing`, `UGC`, `Travel`, and still listing the dead `Project_Ideas` name. Now `load_folder_vocabulary()` reads live from `Directory.md`, same pattern as the tag vocabulary fix from earlier the same night.
- Tags are now canonicalized against the real 20-value vocabulary with a safety net (`_canonical_tag`) — the model's raw tag list gets filtered to only real matches, capped at 2, `Misc` fallback if none match.
- **Removed `needs-enrichment` / `search_for` / the forced `github-repo` tag entirely** — Tony explicitly rejected this ("I never approved that tag"). Not every image needs a resolvable URL; if vision finds one it goes in `url:`, otherwise nothing extra is written, no flag, no follow-up field.
- Added `--limit N` flag for reviewing a small batch before committing to the full run.
- **Extracted `finalize_and_write_note()`** — the dedup/naming/write-the-file logic that used to be inline in the CLI loop is now its own function, callable by both the CLI (unchanged behavior, verified via a real 1-image run producing identical output) and the new Ingest Visualizer. This was an explicit ask from Tony: reuse, never a second copy of the same template.
- **~495 of ~500 screenshots in `000_Ingest/Screenshots/` are still unprocessed** — several small test batches (6, 10, 20, 6 more) were run tonight specifically to validate the folder-routing fixes above; each batch's misclassifications were traced back to a real, now-fixed root cause (stale `VALID_FOLDERS`, the Directory.md truncation bug, the Mockups blank-vs-finished confusion). The fixes are believed solid now but the full remaining batch has not been run.

## 4. New tool: Ingest Visualizer (`001_Architecture/Tools/Ingest-Visualizer/`, localhost:8757)

Built from scratch tonight per Tony's request — a Resource-Library-Visualizer-style card browser for `000_Ingest/` that lets Tony pre-tag items before they're ever processed, so manually-classified items skip the API entirely and only genuinely-unknown items go through vision/text-classification.

**Architecture (explicit design constraint from Tony: never modify the original ingest scripts' behavior — only call them, or extract shared functions with zero behavior change):**
- `config.py`, `items.py` (scans `000_Ingest/` top-level + named drop zones only — same never-touch-ad-hoc-folders rule as the skill), `video_thumb.py` (ffmpeg frame grab), `ingest_runner.py` (the bridge — imports `process_image_ingest.py` and `retag_and_retitle.py` as modules, shells out to `process_video_ingest.py` unchanged), `serve.py`, `App.html`.
- **Per-item edit panel**: title/description/URL/folder/tag-checkboxes (same live `Directory.md` vocabulary). If everything's filled in, ingest skips vision/classification entirely and just dedup-checks + writes. If partially filled, vision/classifier fills in only what's missing — manual values always win.
- **Text bookmarks (`.md` from the Obsidian web-clipper) get real auto-classification** — reuses `retag_and_retitle.py`'s existing cheap text-only model call (`google/gemini-2.5-flash-lite` via OpenRouter) rather than a third copy of that logic. Manual folder/tags still override it when Tony sets them.
- **PDF ingest** — was missing entirely (Tony hit this live: 3 PDFs got batch-tagged, "ingested," but silently errored and never moved). Fixed: PDF moves into the destination folder (default `Docs`) with a small companion `.md` note carrying title/tags, matching Obsidian's native-PDF-viewer approach from the ingest skill.
- **Zone tabs** (All / root / Screenshots / PDF / etc.), **source badges** (YouTube/Screenshot/PDF/MD, color-coded), **select-by-source shortcuts** (YouTube/MD buttons, "Select All Visible" respecting the active tab, "Uncheck All" resets cleanly).
- **Batch bar applies immediately on change** — picking a folder or clicking a tag chip saves instantly (no separate "Apply to Selected" step, which Tony correctly identified as a confusing extra click once "Ingest Selected" already auto-applies).
- **Background job + live progress bar** for `/api/ingest` — a big batch (e.g. all 456 screenshots) no longer blocks one giant request with zero feedback; returns a `job_id` immediately, frontend polls `/api/ingest_status` every 1.2s, grid updates as each item completes.
- **Confirm-before-commit** on both "Ingest Selected" and the "🎯 Auto-Ingest YouTube → Tutorials" one-click button (select all YouTube-sourced items → folder=Tutorials, tag=Guide → ingest, in one click) — added after a real incident tonight where ~84 YouTube items got ingested with the wrong tag (`Misc` instead of `Guide`) because the batch bar's picked values weren't actually being applied before Ingest was clicked. Root cause fixed (batch bar auto-applies now) and the 84 notes were retagged by hand.

**Known state:** 18 `.md` bookmarks and 456 screenshots still sit in `000_Ingest/` untouched, ready for Tony to run through the visualizer whenever he wants — either hand-tag/batch-tag first, or select-all and let vision/the classifier handle everything.

## Lessons worth remembering (process, not just this session's facts)

- **Flask dev server reads `App.html`/imports its Python modules once at startup** — every code change needs a full server restart, not just a browser refresh, across both visualizers. Hit this repeatedly tonight.
- **macOS's built-in `sed` doesn't support `\s`** in patterns (BSD sed, not GNU) — a removal that reported success silently did nothing. Use explicit `[ \t]` or `[[:space:]]`.
- **A native browser `confirm()` dialog during automated/testing clicks is a real risk** — likely contributed to the accidental 84-item ingest tonight. Test destructive actions via direct API calls, not by clicking through the live UI, when a confirm-gated action is involved.
