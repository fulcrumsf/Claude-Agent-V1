---
title: "TOOLBOX: Complete Tool & Capability Reference"
type: guideline
domain: architecture
tags: [guideline, architecture, doc]
---

# TOOLBOX: Complete Tool & Capability Reference

**Last updated:** 2026-06-19

This is the single source of truth for all pre-installed tools, CLIs, MCPs, skills, and plugins.

**CRITICAL MAINTENANCE RULE:** Whenever you install a new skill, plugin, MCP, CLI, or Python tool anywhere in the workspace, **immediately update this file**. Add the new capability under the appropriate section below. Agents don't know tools exist unless they're documented here.

---

## Agent Safety Guard (fs_guard.py, 2026-09-27)

`001_Architecture/Scripts/fs_guard.py` is a pre-tool hook shared by Claude Code (`~/.claude/settings.json`), Codex (`~/.codex/hooks.json` + `~/.codex/rules/agent_os_guard.rules`) and Gemini CLI (`~/.gemini/settings.json`). It hard-blocks every agent delete (rm, rmdir, find -delete, git clean, rsync --delete, inline Python/Node deletes, MCP delete-note tools); temp paths are exempt. It also stops new folders inside Agent-OS: Claude shows Tony a prompt, and Codex/Gemini must ask. Always-allowed new folder names: `Archived`, `Rejected`, `vN`, caches, anything under `000_Ingest/`, and item folders inside an existing `007_Resource_Library/<Folder>/`. Test: `python3 001_Architecture/Scripts/fs_guard.py --self-test`.

---

## Model Routing (Option B, 2026-09-27)

Every harness starts each prompt on its own cheap default model; a shared Jev call decides whether it stays there, escalates to a frontier subagent, or gets delegated as a chore. Built and unit-tested (uncommitted); harness hook registration is pending Tony (see below).

- **`001_Architecture/Scripts/jev_route.py`** — the "before the prompt" hook. Calls Jev (OpenRouter Decisions API, model `typesafe/jev-1.13`) with a 1.0 s request timeout, plus a 1.5 s wall-clock guard on the whole hook run (which also bounds the Antigravity transcript read); fails open (exit 0, no hint, prompt continues) on timeout, missing key, malformed input, or any error. Adds a `[Agent-OS router, Jev]` hint telling the model to answer it directly, hand it to a frontier subagent, or run `delegate.py`. Also flags brain dumps (multiple tasks in one message) and asks the model to split and route each one separately. Logs every decision to `~/Library/Logs/Agent-OS-Router.jsonl`. 18 unit tests in `test_jev_route.py`, all passing.
- **`001_Architecture/Scripts/delegate.py`** — the shared chore command: `python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/delegate.py "<task>" --skill <Skill_Name>` (run it in the background or with the maximum shell timeout; chores take minutes). Runs a headless `codex exec` worker on OpenRouter Auto Router (`openrouter/auto`, key `OPENROUTER_CHORES_KEY`, capped at $20/month, workspace-limited to `deepseek/*`, `qwen/*`, `z-ai/*`, `moonshotai/*` and a few Gemini Flash models), inside the existing `fs_guard.py` + Codex-rules protection so a cheap worker still can't delete files or make folders. Returns the worker's report plus only what changed during the run: `git status` entries added/removed, and a bounded before/after mtime+size snapshot of every file under `000_Ingest/` (gitignored) and of files already dirty before the run (added / changed / missing) — the calling model must check that list before telling Tony a chore is done. Worker restrictions (all via `codex exec -c` overrides; `~/.codex/config.toml` is never edited): Codex plugins, remote plugins, apps, browser use, computer use and image generation off; every MCP server in `~/.codex/config.toml` disabled; `model_reasoning_effort="low"`; stopped after 30 minutes (`WORKER_TIMEOUT`); refuses to run inside another delegated worker. Hooks stay on, so the `fs_guard.py` PreToolUse hook still blocks deletes (verified live 2026-09-27). Exit codes: the worker's own code, `1` usage error, `2` no `OPENROUTER_CHORES_KEY`, `3` refused (already inside a delegated worker), `124` worker timed out (report + changed files still printed). 14 unit tests in `test_delegate.py`, all passing.
- **`fs_guard.py` Antigravity adapter** — `normalize_antigravity()` maps Antigravity's `PreToolUse` payload (`run_command` / `write_to_file`) onto the same shape the Claude/Codex/Gemini guard already evaluates, so the same delete/new-folder blocks apply there too. Malformed payloads are treated as nothing to check. Self-test now covers 49 cases (`python3 001_Architecture/Scripts/fs_guard.py --self-test`).
- **`opus-standard` / `opus-deep`** (Claude Code, global subagents in `~/.claude/agents/`) — Opus at medium/high effort respectively, for work too hard for Sonnet but never for chores.
- **`sol-standard` / `sol-deep`** (Codex, planned) — the Codex-side equivalent of the Opus subagents; not yet created (`~/.codex/agents/` is outside Agent-OS, needs Tony's go-ahead to create the folder).
- **Anti-recursion:** `delegate.py` sets `AGENT_OS_DELEGATE_WORKER=1` in its worker's environment; `jev_route.decide()` skips routing entirely when that variable is set, so the delegated worker's own prompts never get re-routed, and `delegate.py` itself refuses to start (exit 3) when that variable is set.
- **Off switch:** `touch ~/.agent_os_router_off` disables Jev routing everywhere (delete the file to re-enable). Routing is a hint only — no harness lets a hook force a model switch mid-session.
- **Pending Tony:**
  - Register the `jev_route.py` hook in `~/.claude/settings.json`, `~/.codex/hooks.json`, `~/.gemini/settings.json` (blocked on Claude Code's auto-mode safety check).
  - Create `~/.gemini/config/hooks.json` (Antigravity `PreToolUse`/`PreInvocation` wiring).
  - Create `~/.codex/agents/sol-standard.toml` + `sol-deep.toml` (needs the `~/.codex/agents/` folder approved).
  - Run the live brain-dump tests in fresh Claude Code, Codex, and Antigravity sessions.
  - Set `"model": "sonnet"` as the Claude Code default in `~/.claude/settings.json`.
  - Fix the Python 3.13 CA bundle if not already done (`Install Certificates.command`) — without it Jev fails open silently.

---

## System Maps (Install Maps)

Two maps live at `001_Architecture/Install_Maps/`. When Tony says **"look at the system map"** or **"look at the install map"**, read the appropriate file.

| Map | File | What it covers |
|-----|------|----------------|
| **Workspace Map** | [`001_Architecture/Install_Maps/Workspace-Map.md`](001_Architecture/Install_Maps/Workspace-Map.md) | Folder structure, departments, active projects |
| **System Map** | [`001_Architecture/Install_Maps/System-Map.md`](001_Architecture/Install_Maps/System-Map.md) | All installed apps, Homebrew, Python, Docker, MCPs, CLIs, scripts, skills, Adobe plugins |

**Auto-update script:** `001_Architecture/Scripts/generate_system_map.py`
- Runs weekly via cron (Sundays 3 AM)
- Refresh manually: `python3 001_Architecture/Scripts/generate_system_map.py`
- Output: `System-Map.md` + `system_map_data.json` (machine-readable)

**Vision audit script:** `001_Architecture/Scripts/check_vision_needed.py`
- Checks images against their category-folder notes to determine which files actually need vision analysis
- Searches `007_Resource_Library/{Tools,Tutorials,Research,...}/` for paired markdown notes (NOT legacy Asset_Notes/)
- Reads description from `## AI Analysis` section; detects filler ("likely a saved reference", "general visual reference", etc.)
- Run: `python 001_Architecture/Scripts/check_vision_needed.py "/path/to/images"`
- Pipe-friendly: add `--needs-vision-only` to print just filenames needing vision
- Always run this BEFORE calling the ingest script — avoids duplicate API spend
- Output: count of already-cataloged vs needs-vision, with per-file reasons

**Resource Library dedup script:** `001_Architecture/Scripts/resource_library_dedup.py`
- Scans `007_Resource_Library/` for likely duplicate bookmarks (same source re-saved months apart — esp. YouTube tutorials)
- Match tiers: exact (same canonical URL / YouTube ID / identical body), high (same domain + fuzzy title), medium (fuzzy body), low (shares a link but looks unrelated)
- Writes a side-by-side review table: `007_Resource_Library/_Dedup_Review.md` + `.json`. **Never deletes or moves anything** — Tony reviews and decides.
- Options: `--roots`, `--output`, `--format {md,json,both}`, `--min-title-sim`, `--min-body-sim`, `--include-images`
- Run: `python3 001_Architecture/Scripts/resource_library_dedup.py` — safe to re-run any time (e.g. after an ingest batch)
- Run this BEFORE any Resource Library graphify build — don't graph the same source twice

**Resource Library stub enrichment (3 scripts):** run in order before a graphify rebuild
- `001_Architecture/Scripts/resource_library_stub_triage.py` — classifies every near-empty note into `bucket1_revision` (has screenshot), `bucket2_url_enrich` (has URL), `bucket3_dead` (garbled / missing image / no signal). Writes `007_Resource_Library/_Stub_Triage.json` + `.md`. Safe to re-run.
- `001_Architecture/Scripts/revision_stub_notes.py` — re-runs the hardened vision prompt on bucket-1 images and rewrites each note IN PLACE (filename + `![[embed]]` preserved). Adds `form:`/`summary:`/`url:`/`search_for:`/`enriched:`. `--shard I/N` for parallelism, `--dry-run`, `--limit`. Resumable (skips notes with `enriched:`). Needs `OPENROUTER_API_KEY`.
- `001_Architecture/Scripts/enrich_url_stub_notes.py` — Gemini (Google Search grounding) visits bucket-2 URLs and writes `summary:`/`form:`/`verified:`. Same flags. Needs `GEMINI_API_KEY`.
- `001_Architecture/Scripts/apply_dead_stub_graphignore.py` — writes bucket-3 paths into root `.graphifyignore` between `AUTO` markers (idempotent). Files stay in the vault; only excluded from the graph.
- `001_Architecture/Scripts/note_review.py` — for the stubs automation couldn't enrich: copies the notes (+ full images) to `~/Desktop/Resource_Library_Review/` and builds `review.html` — one page, each note shown with its image or link + text, Keep/Junk buttons per card (saved in browser), "Copy decisions" button hands back a `KEEP`/`JUNK` + path list. Read-only on the vault. Run `resource_library_stub_triage.py` first.
- `001_Architecture/Scripts/note_review_excluded.py` — bulk review page for the ~1,044 notes auto-excluded from the graph (bucket 3: garbled-title / missing-image / no-signal). `~/Desktop/Resource_Library_Review/review_excluded.html` — faceted filters (reason, folder, decision, text search), "Junk/Keep/Clear all shown" bulk buttons scoped to the current filter, per-card override, browser-saved, "Copy decisions" export. Read-only. No images (none resolve).
- `001_Architecture/Scripts/build_image_cull.py` + `apply_image_cull.py` — visual culling page for all ~9k images in 007_Resource_Library (`~/Desktop/Resource_Library_Review/image_cull.html`). Area filters (OpenAI_History / Visual_Assets / OpenAI_Images / Videos_Keyframes / Undetermined), note/no-note tag + filter, "mark all shown for delete", live GB-to-reclaim counter, copy/download delete list. apply script moves each marked image + its note to ~/Desktop/Delete/RL_Image_Cull/.
- First run 2026-09-05: ~890 notes enriched, 1046 dead notes graph-ignored.

**Resource Library Visualizer:** `001_Architecture/Tools/Resource-Library-Visualizer/serve.py`
- Local browser gallery ("Lightroom for screenshots") for reviewing / culling `007_Resource_Library`. Run `python3 001_Architecture/Tools/Resource-Library-Visualizer/serve.py` → opens `localhost:8756` (cold start ~10-15s while it indexes ~4k notes).
- Default view: notes with an embedded image or a YouTube video, newest-ingested first. Toggle shows text-only `.md` notes as color-coded glyph cards. Filters: folder / source-type (YouTube·Screenshot·Bookmark) / top-8 tags / search.
- Click a card → note rendered Obsidian-style (inline images, playable YouTube embeds, callouts, wikilinks). Per-card: **Edit** (title/summary/url/tags/body → rewrites the `.md` in place), **Re-run AI** (re-runs `process_image_ingest` vision, shows before/after, apply or discard), **Add Comment** (queued for the agent).
- Bulk select → **Delete** (moves note + sibling image to `~/Desktop/delete/`, card vanishes — never a hard delete) or **Re-run AI**.
- Comments + edit requests append to `~/Desktop/Resource_Library_Review/Review_Queue.md`; **Finalize Queue** seals a batch (copy/download) to hand to the agent.
- Nothing is committed to git. Source-type labels are heuristic (~90%). Tests: `tests/resource_library_visualizer/` (39, pytest).

**Skill registry sync script:** `001_Architecture/Scripts/sync_skill_index.py`
- Regenerates `001_Architecture/Skills/Skill-Index.md` from every `SKILL.md` in the skills tree
- Designed to run from Claude/Gemini hooks after skill edits so Gemini can discover new or changed skills automatically
- Safe to run manually at any time if the registry needs a refresh

**Codex Agent-OS Hardening skill:** `001_Architecture/Skills/codex-agent-os-hardening/SKILL.md`
- Operating checklist for Codex/OpenAI-compatible agents in Agent-OS
- Covers startup orientation, folder routing, recommendation approval boundaries, preservation rules, feedback-loop writes, memory updates, session logs, and closeout behavior
- Use whenever Codex starts work in Agent-OS or Tony corrects Codex workflow/process behavior

**Image Extraction script:** `001_Architecture/Scripts/process_image_ingest.py`
- Uses OpenRouter vision first (qwen model), then OpenAI vision fallback, to extract semantic knowledge
- OCR is not the default path for screenshot renaming
- Run: `python3 001_Architecture/Scripts/process_image_ingest.py "/path/to/images"`
- Output (as of 2026-09-09): note **and** its renamed image written **side by side** in the category folder, same name stem (`Tools/OpenCode.md` + `Tools/OpenCode.png`). `Visual_Assets/` retired.
- Dedup, automatic: (1) skip byte-identical image, (2) skip if `url:` already in another note, (3) title clash → `-N` + `possible-duplicate` tag.

**Image co-location migration (one-time, done 2026-09-09):** `001_Architecture/Scripts/migrate_images_to_notes.py`
- Moved all 1,028 images out of `Visual_Assets/` into their notes' category folders, renamed to match, normalized extensions, updated every embed. `--dry-run` / `--limit` / `--verify`. Backup + `_Image_Migration_Manifest.json`.

**Broken-image / text-only note review:** `001_Architecture/Scripts/build_broken_image_review.py <notes.json> [--title T] [--outfile F]`
- Generic full-text Keep/Strip/Junk review page for any list of notes. Folder + decision filters, bulk actions, copy/download decisions.

**ARCHIVED 2026-09-09 — do not run.** Five image scripts that operated on the retired
`Visual_Assets/` folder now live in `001_Architecture/Scripts/_Archive/` (with a README):
`reroute_visual_assets.py`, `fix_image_case.py`, `update_asset_notes_vision.py`,
`fix_embeds.py`, `rename_screenshots.py`. Current image ingest = `process_image_ingest.py`.

**Notion export processor:** `001_Architecture/Scripts/process_notion_edit.py`
- Heuristic offline batch processor for large Notion exports when the export mixes md, json, csv, images, PDFs, spreadsheets, and Pages files.
- Run: `python3 001_Architecture/Scripts/process_notion_edit.py "/path/to/Notion-Edit"`
- Output: routes files into the current Resource Library categories, creates markdown notes for images/text exports, and leaves the source folder empty.

**Markitdown CLI** — converts files to Markdown
- Install: `pip install 'markitdown[all]'` (v0.1.5, already installed)
- CLI: `markitdown file.pdf -o output.md`
- Supports: PDF, Word (.docx), PowerPoint (.pptx), Excel (.xlsx), HTML, images, audio, zip
- Use case: Step 0 of ingest pipeline — converts binary files to `.md` before classify/route steps run
- Also usable standalone anywhere in the workspace

**Video Extraction script:** `001_Architecture/Scripts/process_video_ingest.py`
- Automates multi-step FFmpeg scene detection and audio Whisper transcription for incoming raw videos.
- Run: `python3 001_Architecture/Scripts/process_video_ingest.py "/path/to/video.mp4"`
- Output: Properly structured package with keyframes and transcript files in `007_Resource_Library/Videos/`.

**Neon Parcel storyboard QA adapter:** `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/storyboard_vision_provider.py`
- Builds the structured storyboard inspection request for OpenRouter/Qwen vision, preserves raw provider responses, and rejects missing keys or malformed JSON.
- Use `--dry-run` to verify request construction without a network call or provider spend.
- Pair with `storyboard_qa.py`; the adapter does not itself approve a storyboard and must feed the fail-closed evaluator.

**Neon Parcel storyboard review policy:** `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/storyboard_ensemble.py`
- Loads a production-level manual-review policy with a safe default of `manual_review_required: true`.
- Manual review can be turned off explicitly, but provider disagreement still forces manual review when `require_provider_agreement` is true.

**Neon Parcel storyboard control loop — remaining pieces** (hardened 2026-09-04, see `Neon_Parcel_Longform_Compilation/SKILL.md` and `Logs/Handoffs/2026-09-04_Neon-Parcel-Longform-Hardening_Codex-Handoff.md`), all in `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/`:
- `storyboard_contract.py` — serializes a frame-level contract (subjects, states, relationships, actions, captions, tone, capture style) that the storyboard image must satisfy.
- `storyboard_qa.py` — evaluates storyboard vision-provider evidence against that contract; fail-closed (no evidence = no pass).
- `storyboard_regeneration.py` — caps storyboard retries at 3 attempts, preserves every failed candidate (never overwrites).
- `storyboard_handoff.py` — builds the Seedance prompt from what the *accepted* storyboard actually shows, not the original idea/assumptions (prevents reintroducing unverified actions/geometry).
- `generation_guard.py` — blocks any paid generation call that lacks an explicit version number + revision reason.
- `check_storyboard_scale.py` (2026-09-26) — measured scale check on a storyboard with local YOLOE text-prompt detection (`yoloe-11l-seg.pt` + `mobileclip_blt.ts` in `Generic_Tools/Subject-Aware-Reframer/Models/`, gitignored). Reads `Data/Scale_Spec.json` (real heights, detector words, anchors, exaggeration rules); flags size changes, parked things moving, subjects oversized vs environment anchors, side-by-side ratio errors. Writes `Data/Scale_Check_<storyboard>.json/.png`. `seedance2_call.py` hard-stops Neon Parcel calls without a passing check on the exact storyboard.
- `extract_storyboard_keyframes.py` (2026-09-26) — cuts an approved storyboard sheet into clean keyframe images (each panel at its own border, native ratio, no caption text; handles sheets with or without divider lines). Free keyframe fallback when a storyboard-reference video tiles: feed the result to `seedance2_call.py --keyframes`. Never overwrites; storyboard untouched.
- `artifact_preservation.py` — centralizes the non-destructive version/archive rule (new version on every regen, superseded moves to `Archived/`) so every tool enforces it the same way.
- `validate_pre_video_gate.py` — fail-closed pre-video validation gate before a Seedance call is allowed to fire.
- `decide_end_frame.py` — decides the storyboard's end-frame selection for image-to-video continuity.
- `gemini_video_inspection.py` — uploads a generated clip directly to Gemini (not OpenRouter) for timestamped structured findings; static 3 FPS sampling for short clips. This is the **default** evidence provider for Neon Parcel clip review — OpenRouter/Qwen (`storyboard_vision_provider.py`) is the fallback/second opinion, not primary. Neither provider auto-approves or auto-rejects; findings go to Tony.

---

## Web Scraping & URL Content

### Firecrawl (Multiple Interfaces)
- **Firecrawl CLI** (installed globally) — `firecrawl scrape <url> --only-main-content --format markdown`
- **Firecrawl Plugin** (enabled) — provides all skills below
- **Firecrawl Skills** — invoke via `/` prefix:
  - `/firecrawl-scrape` — Scrape a single URL with content extraction
  - `/firecrawl-search` — Web search and extract results
  - `/firecrawl-crawl` — Crawl an entire site
  - `/firecrawl-map` — Generate a site map
  - `/firecrawl-browse` — Browse and interact with pages
  - `/firecrawl-download` — Download files from URLs
  - `/firecrawl-agent` — Agent mode for complex scraping tasks
- **Python Tool:** `App Building/tools/enrich-notion-bookmarks.py` — uses Firecrawl to enrich Notion bookmarks with AI summaries
- **API Key:** `FIRECRAWL_API_KEY` in `~/.env-secrets`
- **When quota exhausted:** Falls back to Open Graph metadata extraction

---

## Browser Automation

### Playwright
- **Status:** Plugin installed but DISABLED (can be enabled quickly)
- **Skill:** `/playwright-cli` — browser automation via command line
- **Use case:** Automated testing, screenshot capture, form filling

---

## Stock Media & Open-Licensed Content

### Openverse API
- **What it does:** Search for Creative Commons and public domain images, audio, and video
- **Registration:** OAuth2 API-based (POST `/v1/auth_tokens/register/` endpoint)
- **API Key:** `OPENVERSE_API_KEY_CLIENT_ID` and `OPENVERSE_API_KEY_CLIENT_SECRET` in `~/.env-secrets`
- **Features:** Search filters for CC licensing, public domain content, usage rights
- **Use case:** Video Editor stock media sourcing — find free, legally-usable footage and images before generating AI assets
- **Status:** Registered and active (app: "Uno Mas Video Editor")
- **Tier rating:** 7/10 for images + audio (no video support yet)
- **Reference:** Full public domain source comparison in `App Building/Video Editor/references/docs/PUBLIC_DOMAIN_SOURCES_RATING.md`

### Complete Public Domain Source Ratings
- **Location:** `App Building/Video Editor/references/docs/PUBLIC_DOMAIN_SOURCES_RATING.md`
- **What it includes:** 1-10 ratings for 13 public domain sources (NASA, Pexels, Wikimedia, LOC, archive.org, etc.)
- **Tier system:** Query priority and fallback logic for each asset type (footage, photos, audio, maps, etc.)
- **Use case:** Documentary research skill uses this to decide which sources to query in which order

### Pexels API (Creative Commons Photos/Videos — wired up 2026-08-18)
- **What it does:** Search/download real Creative Commons photos and video footage — this workspace uses it for real B-roll to reduce AI generation cost, and for grounding reference images
- **API Key:** `PEXELS_API_KEY` in `~/.env-secrets` (fixed 2026-08-18 — was previously invalid shell syntax)
- **Full reference (auth, endpoints, rate limits, attribution rules):** `001_Architecture/Tools/Tool-Manager/data/Pexels_API_Reference.md`
- **Attribution:** legally optional per Pexels' own license, but this workspace attributes anyway — YouTube description only (Markdown, hyperlinked to contributor's Pexels profile), no on-screen burn-in
- **Download filter:** 1080p resolution, 16:9 aspect ratio only
- **Used by:** `Production-Research-Agent` skill (search/download/analyze/inventory), `Production-Asset-Planner` skill (per-beat B-roll-vs-generation decision, max 5s B-roll per clip)

---

## Video Generation

### kie.ai (Primary Platform)
- **Python Tool:** `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/kie_video_gen.py` — unified API to all kie.ai video models
  - Supports: **Veo 3.1**, **Kling 3.0**, **Wan 2.6**, **Sora 2**
  - Usage: `python3 001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/kie_video_gen.py "[PROMPT]" output.mp4 "veo3"`
- **API Key:** `KIE_API_KEY`
- **Pricing:** 30–70% cheaper than fal.ai for equivalent models
- **When to use:** Always try kie.ai first for video generation

### kie-cli (kie.ai CLI)
- **Package:** `@felores/kie-cli` (npm global) — **pinned at 0.2.0**, do not upgrade without checking first. 0.4.0 was tried 2026-08-17 and silently dropped the `bytedance_seedance_video` `--mode standard/fast` selector (defaults to Seedance 2.5 only) without adding the Mini/upscale support it was tried for — reverted.
- **Usage:** `kie-cli --help` — list all available models by category; `kie-cli [category]` to explore
- **API Key:** the CLI binary itself reads `KIE_AI_API_KEY` (not `KIE_API_KEY`, despite the rest of the workspace using that name) — an alias `export KIE_AI_API_KEY=$KIE_API_KEY` was added to `~/.env-secrets` 2026-09-17 after this silently failed with "KIE_AI_API_KEY environment variable is required." Any script that shells out to `kie-cli` (e.g. `Storyboard-Generation/scripts/image_generation.py`) needs this alias present.
- **When to use:** Live model discovery on kie.ai without reading the website; pipe into scripts for programmatic model selection

### kie_market_api.py — gap-fill wrapper for models kie-cli doesn't cover
- **Python Tool:** `001_Architecture/Tools/Video-Generation/Generic_Tools/kie_market_api.py`
- **What it's for:** kie.ai has ~441 models on its Market API; kie-cli only wraps a subset. This is a thin wrapper around the unified `/api/v1/jobs/createTask` + `/api/v1/jobs/recordInfo` endpoints for models kie-cli doesn't expose (confirmed gaps as of 2026-08-17: `bytedance/seedance-2-mini`, `topaz/video-upscale`).
- **Not a kie-cli replacement** — kie-cli stays the default for anything it already covers. Extend this file one function at a time as new gaps are found, per Tony's explicit direction (2026-08-17) — do not build a full custom CLI.
- **Usage:** `python3 kie_market_api.py seedance_mini "<prompt>" output.mp4 --resolution 480p` or `python3 kie_market_api.py grok_upscale <task_id> output.mp4`
- **Reference routing:** `--reference-image-url <url>` sends contextual storyboard/reference assets through `reference_image_urls`; `--first_frame_url <url>` is reserved for a clean temporal start frame. The wrapper rejects storyboard/frame role confusion before submission.
- **API Key:** `KIE_API_KEY`

### WaveSpeed CLI
- **Package:** `@wavespeed/cli` (npm global)
- **Usage:** `wavespeed models "[query]"` — keyword search across 986 models; `wavespeed models` — full list
- **API Key:** `WAVESPEED_API_KEY` (fixed from `WAVESPEED_AI_API_KEY` — old name was wrong)
- **When to use:** Find WaveSpeed-specific models (Seedance, Wan, Kling variants) and their per-video flat pricing; only platform with live CLI model search

### Autohand (OpenRouter Agent CLI)
- **Installer:** autohand.ai — OpenRouter-backed CLI automation agent
- **API Key:** `OPENROUTER_API_KEY`
- **When to use:** OpenRouter-backed agent tasks from CLI; fallback for model routing when direct APIs unavailable

### Blotato (Publishing) — MCP server, registered and active
- **What it does:** Publish generated videos to YouTube and social media (Instagram, TikTok, Facebook, LinkedIn, Twitter, Pinterest, Threads, Bluesky)
- **Access:** MCP server (HTTP transport, `https://mcp.blotato.com/mcp`), registered project-scoped for Agent-OS in `~/.claude.json` as of 2026-07-04. Tools available directly as `mcp__blotato__*` in Claude Code — prefer these over any manual API calls.
- **Key tools:** `blotato_list_accounts` (get accountId + platform requirements), `blotato_create_presigned_upload_url` (local file → public URL, required before `create_post` for any local video/image), `blotato_create_post` (publish/schedule), `blotato_get_post_status` (poll after create_post for large media)
- **Known connected YouTube accounts:** NeonParcel (id `25731`), ReimaginedRealms (id `30323`, 18 playlists mapped), Anomalous Wild (id `42514`, displayed as "Anomalos Wild" — a spelling variant, confirmed correct 2026-07-08)
- **Known connected TikTok accounts:** neonparcel (id `27763`), reimaginedrealms (id `33717`). TikTok posts require `privacyLevel` + `disabledComments`/`disabledDuet`/`disabledStitch`/`isBrandedContent`/`isYourBrand`/`isAiGenerated` all present, or `create_post` 400s.
- **Known connected Instagram accounts:** neonparcel (id `29334`), reimagined.realms (id `35548`). No AI-disclosure field exists for Instagram in the `blotato_create_post` schema (checked directly, 2026-08-03) — unlike YouTube/TikTok below, Instagram AI-generated content can't be flagged programmatically through this integration.
- **Known connected Facebook accounts:** Tony Cam (id `18651`) with subaccounts (pages) NeonParcel (`888301901041580`) and Reimagined Realms (`407939555731086`) — pass the page's id as `pageId`. `mediaType: "reel"` is the right choice for short vertical video.
- **AI-disclosure fields, confirmed per-platform (2026-08-03):** YouTube `containsSyntheticMedia` (bool), TikTok `isAiGenerated` (bool). Set both true for AI-generated video. No equivalent exists for Instagram or Facebook.
- **Caption/hashtag length practice (researched 2026-08-03, for SEO/discoverability posts):** TikTok — hook-first in the visible first 100-150 chars, sweet spot 150-300 chars total, 3-5 hashtags (more reads as spam to the algorithm, doesn't help reach). Instagram — hook in the first ~125 chars before "See more" truncation, **hard cap of 5 hashtags per post since Dec 18, 2025** (the old "30 hashtags" guidance is stale, don't use it).
- **TikTok `isDraft: true`** saves to the TikTok app's drafts inbox (confirmed working 2026-07-12) — useful for TikTok Shop Creator videos since Blotato has **no field to attach/tag a TikTok Shop product** (checked the live `blotato_create_post` schema directly — no such field exists on any platform). Product tagging must be done manually in the TikTok app after the draft lands. Blotato's post-status API also has no distinct "draft" status value (only `in-progress → published | scheduled | failed`) — a draft submission still reports back as `"published"`; always have Tony confirm in-app that it actually landed in drafts, don't trust the API status alone for draft posts.
- **`isBrandedContent` ≠ affiliate/commission content.** This flag is specifically for direct brand-paid partnerships with brand-dictated content guidelines — set `false` for TikTok Shop Creator/affiliate videos (commission-based, GMV-tied fees, no brand paying for that specific video/no brand creative direction).
- **Thumbnail constraint:** custom YouTube thumbnails must be ≤2MB JPEG/PNG — compress with ffmpeg first if over (`ffmpeg -i in.png -vf "scale=1920:-1" -q:v 5 out.jpg`)
- **Gotcha:** if `create_post` errors "reconnect your YouTube account" for a custom thumbnail, that's an OAuth scope issue fixed in the Blotato dashboard (not a script/MCP bug) — already-uploaded media URLs don't need re-uploading after reconnect
- **Python integration:** `kie_upload.py` for file uploads before publishing (legacy path — MCP's own presigned-upload flow is now preferred)
- **Neon Parcel Shorts, 4-platform publish (locked 2026-09-15):** one presigned upload, then `blotato_create_post` to all four Neon Parcel accounts (YouTube `25731`, TikTok `27763`, Instagram `29334`, Facebook `18651`/pageId `888301901041580`) from the same media URL. Full field-by-field settings in `Neon_Parcel_Longform_Compilation/SKILL.md` under "Validated Blotato Shorts Upload." Still requires Tony's per-Short approval of title/caption/hashtags before every publish — not a standing authorization.
- **API Key:** `BLOTATO_API_KEY` (used by the MCP server itself, not needed for direct calls from Claude Code)

---

## Image Generation

### kie.ai (Primary Platform)
- **Python Tool:** `001_Architecture/Tools/Image-Generation/kie_image_gen.py` — Nano Banana 2 and Nano Banana Pro
  - Usage: `python3 001_Architecture/Tools/Image-Generation/kie_image_gen.py "[PROMPT]" output.jpg --model nano-banana-2`
- **Skill:** `/nano-banana-pro-prompts-recommend-skill` — AI recommendations for image prompts

### fal.ai (Fallback)
- **Python Tool:** `001_Architecture/Tools/Image-Generation/image_gen.py` — fallback to Google AI Studio (Gemini 2.5 Flash) or fal.ai
- **API Key:** `FAL.AI_API_KEY`
- **When to use:** Only if kie.ai doesn't have the model you need

---

## Text-to-Speech

### ElevenLabs
- **Python Tool:** `001_Architecture/Tools/Text-To-Speech/audio_tts.py`
  - Generates TTS with word-level timestamps
  - Outputs per-scene MP3 files and `beat_sheet.json`
  - Usage: `python3 001_Architecture/Tools/Text-To-Speech/audio_tts.py <script.md> <output_dir> [--voice <id>]`
- **Runtime config:** `001_Architecture/Tools/Text-To-Speech/config.py` loads `ELEVENLABS_API_KEY` from `~/.env-secrets`; credentials are never stored in the tool folder.
- **API Key:** `ELEVENLABS_API_KEY`
- **Output:** Feeds into video beat sheet and Remotion composition

---

## Sound Effects / Ambience (video audio)

### Video-to-audio (motion-conditioned Foley) — DEFAULT for Anomalous Wild
- **Python Tool:** `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/generate_stems_v2a.py`
  - Feeds picture-locked video segments through **fal.ai Mirelo SFX v1.6**
    (`mirelo-ai/sfx1.6/video-to-video`) so ambience/Foley is conditioned on real
    on-screen motion. Segments a render on scene boundaries (`Data/v2a_segment_map.json`,
    ≤60s each), crossfade-concats to one bed (`Assembly/V2A/v2a_bed.mp3`).
  - Usage: `python3 generate_stems_v2a.py <production_folder> --source <picture_locked_render>`
  - Requires `fal-client` (`pip install fal-client`) + `FAL.AI_API_KEY`. Cheap (GPU compute-seconds).
  - No model does a 3-min single pass — Mirelo ≤60s, MMAudio v2 ≤30s, Kling v2a 3-20s.
  - Locked 2026-09-04 (Glass Frog 0003, graded A). See Global_Agent_Memory 2026-09-04.
- **Fallback:** `.../Anomalous_Wild/generate_stems.py` — ElevenLabs text-to-SFX
  (`v1/sound-generation`, 28s chunk cap) from `Data/stem_map.json`. Use only if
  video-to-audio is unavailable or a segment repeatedly fails.

### Neon Parcel End Screen
- **Horizontal asset:** `002_Content-Creation/Video_Editor/002_Channels/002_Neon-Parcel/Assets/Neon_Parcel_Endscreen_Horizontal_1080.mp4`
- **Rule:** Append to every approved Neon Parcel long-form master as a dedicated seven-second final segment; keep CTA audio inside that window.

---

## YouTube & Video Research

### YouTube Analytics OAuth (own-channel private data)
- **What it does:** OAuth (not just an API key) access to YouTube Analytics + Data API v3 for Tony's own channels — average view duration, retention, traffic source, private stats. The plain `YOUTUBE_DATA_API_KEY` below only covers public metadata (view/like counts on any channel); this covers private analytics on channels Tony owns/manages.
- **GCP project:** `Antigravity-Claude` (`antigravity-claude-491002`) — reused existing project, enabled `YouTube Data API v3` + `YouTube Analytics API`, added scopes `youtube.readonly` + `yt-analytics.readonly` to the existing `Antigravity-ClaudeCode` Desktop OAuth client (consent screen: External/Testing, test user `fulcrumsf@gmail.com`).
- **Setup script:** `001_Architecture/Scripts/youtube_analytics_auth.py <label>` — one-time per channel (Google ties the "acting as" Brand Account identity to each individual grant, so a single Google login still needs one grant per channel). Produces `~/.config/agent-os-youtube/token_<label>.json`.
- **Client secret:** `~/.config/agent-os-youtube/client_secret.json` (chmod 600, not in the repo).
- **Channels authorized (2026-09-17):** `neon_parcel` (NeonParcel, 2,100 subs), `reimagined_realms` (ReimaginedRealms, 203 subs), `anomalous_wild` (Anomalos Wild — returned only 1 sub, worth re-verifying this landed on the right brand identity), `board_nomad` (Bored Nomad, 289 subs), `business_origin_stories` (Business Origin Stories, 46 subs).
- **Usage:** load the relevant `token_<label>.json` with `google.oauth2.credentials.Credentials.from_authorized_user_info()`, build `youtube` (`v3`) for Data API or `youtubeAnalytics` (`v2`) for the Analytics API (retention curves, watch time, traffic source) via `googleapiclient.discovery.build`.

### yt-dlp (Video Download)
- **Location:** `/Library/Frameworks/Python.framework/Versions/3.13/bin/yt-dlp`
- **What it does:** Download YouTube videos and public videos at 720p
- **Invoked by:** `download-video` skill in Video Editor
- **Maintenance gotcha (found 2026-09-17):** YouTube periodically changes its signature/cipher scheme; a stale yt-dlp install (pip doesn't auto-update it) then fails every download with `HTTP Error 403: Forbidden`. Not a cookies/auth issue — fix is `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 -m pip install --upgrade yt-dlp`. If any yt-dlp-based tool (this, `Video-Analyzer`, `download-video`) suddenly 403s on a URL that should work, update yt-dlp first before troubleshooting anything else.

### Street View Static API (real location reference photos)
- **What it does:** Real street-level photos for grounding environment sheets/generation in an actual place, instead of AI-inventing a location from text alone — same principle as `Production-Research-Agent`'s real reference images. Confirmed real failure this fixes: an AI-generated environment sheet for a UK street produced a different-looking house/street than the already-approved storyboard, since nothing anchored it to reality.
- **GCP project:** `Antigravity-Claude` (`antigravity-claude-491002`) — same project as the YouTube Analytics OAuth setup. Street View Static API enabled 2026-09-18. Billing already active on this project (Pay-as-you-go), so no new billing setup was needed.
- **API key:** reuses the existing `YOUTUBE_DATA_API_KEY` value — one key can be restricted to multiple APIs in the same project rather than needing a new key per API. That key's restriction list now covers YouTube Analytics API, YouTube Data API v3, and Street View Static API.
- **Usage:** `https://maps.googleapis.com/maps/api/streetview?size=<W>x<H>&location=<address or lat,lng>&key=$YOUTUBE_DATA_API_KEY` — returns a JPEG directly. Also see the Street View Metadata endpoint (same key) to check panorama availability before requesting the image.

### Body Orientation Checker (YOLO-pose)
- **What it does:** Deterministic, non-LLM check of a detected person's body-facing direction in an image — built specifically because Gemini's holistic vision QA missed a real defect (a character's orientation silently flipped between storyboard panels) that a human review pass then had to catch by eye. Real, automated signal instead of another AI judgment call.
- **Script:** `001_Architecture/Tools/Video-Generation/Generic_Tools/check_body_orientation.py` — `python3 check_body_orientation.py <image_path>`.
- **Uses Ultralytics YOLO-pose (PyTorch), not MediaPipe.** MediaPipe's pip-packaged pose models hard-crash on macOS (`DrishtiMetalHelper... Service is unavailable`) — confirmed 2026-09-18 on both a sandboxed shell and a real M3 Max MacBook Pro, on both the full and lite model variants. This is a real MediaPipe/macOS packaging issue, not fixable via delegate/model-size flags — do not reintroduce MediaPipe for pose/orientation work on macOS.
- **Dependency note:** installing `ultralytics` upgraded `torch` 2.6.0 → 2.14.0, which broke `torchaudio`'s version pin (`torchaudio==2.6.0` required, now incompatible). Nothing in this workspace imports `torchaudio` directly, so `torchaudio` was uninstalled cleanly rather than left broken. If any future tool needs `torchaudio`, it will need reinstalling compatible with the current `torch` version.
- **Current limitation:** measures facing-toward-vs-away-from-camera (and rough left/right profile), not orientation relative to another named character in frame (e.g. "is Mover 1 still facing Mover 2") — that needs per-panel detection pairing against character sheets, not yet built. Use output as a flag for human review, not a fully automatic pass/fail gate.

### Gemini Video Analysis
- **Python Tool:** `001_Architecture/Tools/AI-Analysis/gemini_video_analysis.py` — analyze video style, camera work, humor, AI-prompt potential
  - Usage: `python3 001_Architecture/Tools/AI-Analysis/gemini_video_analysis.py "<URL>" -o output.md`
- **Neon Parcel production inspection:** `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/gemini_video_inspection.py` — direct Gemini video upload with timestamped structured findings; defaults to static 3 FPS for short clips. OpenRouter is the fallback, not the primary route.
- **Skill:** `/analyze-video` — same functionality via skill interface

### Case Study Generator
- **Python Tool:** `001_Architecture/Tools/AI-Analysis/case_study_generator.py` — full automated case study pipeline
  - Fetches YouTube metadata via YouTube Data API
  - Runs Gemini 10-section analysis
  - Downloads video and extracts 3 screenshots
  - Outputs to `references/channels/[channel]/case_studies/`
- **Skill:** `/case-study` — same functionality, triggered by "do a case study" or competitor URL
- **API Keys:** `YOUTUBE_DATA_API_KEY`, `YOUTUBE_ANALYTICS_API_KEY`, `GOOGLE_API_KEY`

---

## Video Editing & Composition

### Subject-Aware Reframer — Experimental Gate 3
- **Tool:** `001_Architecture/Tools/Video-Generation/Generic_Tools/Subject-Aware-Reframer/`
- **Status:** Channel-independent framing prototype with configurable group, subject, and hybrid modes. **Locked in 2026-09-15 as Neon Parcel's standard Shorts reframe step, Hybrid mode fixed default** (no more per-video Group/Subject comparison for Neon Parcel) — see `Neon_Parcel_Longform_Compilation/SKILL.md` "Locked Reframe Method". Other channels should still evaluate their own footage before assuming Hybrid; automatic clip selection and channel integration are still deferred.
- **Resume / handoff:** For “plug the Shorts workflow into [channel]” or “connect the short-form clipping workflow,” read `001_Architecture/Tools/Video-Generation/Generic_Tools/Subject-Aware-Reframer/Future-Channel-Integration-Handoff-v1.md`. It records the built component, remaining work, examples, and channel-by-channel approval process.
- **Runtime:** Isolated Python 3.11 environment, 42 approved hash-locked packages, official YOLO11s weights, explicit ByteTrack, FFmpeg/OpenCV diagnostics.
- **Launcher:** `run_offline.py` dispatches detection and `plan/render/reframe` commands with OS network denial, automatic installs disabled, and tool-local caches. Detection uses restricted model loading.
- **Configuration:** `Framing-Profiles-v1.json` and `Job-Contract-v1.md`; shared defaults, saved profiles, per-video settings, and shot overrides. No channel-specific camera code.
- **Outputs:** New production-local runs contain vertical MP4 variants, crop-plan JSON, comparison/debug videos, contact sheet, and verified run report. Sources and approved Shorts are never overwritten.
- **Scope:** Tony's local Agent-OS workflow. Gate 3 reuses the approved dependencies and detection cache. Automatic clip selection, narration analysis, Airtable/MCP connections, and publishing are not implemented.

### Video-Use (Agent-Driven Video Editor)
- **Repo:** `001_Architecture/Tools/Video-Generation/Video-Use/`
- **Skill:** `/video-use` — symlinked into `001_Architecture/Skills/Video-Use/`
- **What it does:** Drop raw footage + pre-recorded VO clips in a folder, agent cuts, trims silences, self-evaluates, outputs `final.mp4`. Audio-first: transcript drives cut decisions.
- **Pipeline:** Transcribe (ElevenLabs Scribe) → Pack → LLM Reasons → EDL → Render → Self-Eval
- **API key:** `ELEVENLABS_API_KEY` via `source ~/.env-secrets` (never stored in .env)
- **When to use:** Raw footage → clean cut. Primary engine for the TikTok Shop affiliate video workflow.
- **Wiki:** `000_Wiki/Video-Production/Video-Use-Agent-Editor.md`

### Hyperframes (HTML-Native Video Renderer)
- **CLI:** `hyperframes` — globally installed via npm (v0.6.25)
- **Repo:** `001_Architecture/Tools/Video-Generation/Hyperframes/`
- **Skills (all symlinked into `001_Architecture/Skills/`):**
  - `/hyperframes` — composition authoring, captions, TTS, audio-reactive animation
  - `/hyperframes-cli` — dev-loop: init, lint, preview, render, doctor
  - `/gsap` — GSAP timeline animations, frame-accurate seeking
- **What it does:** Write HTML → render MP4. Motion graphics, text overlays, subtitle animations, 3D assets, shader transitions. 50+ catalog blocks. Website-to-video.
- **No API key needed** for core rendering. TTS uses Kokoro (local).
- **When to use:** After video-use produces a clean cut, when captions/overlays/motion graphics are needed. Not yet active in affiliate workflow — add when analytics justify it.
- **Wiki:** `000_Wiki/Video-Production/Hyperframes-Video-Rendering.md`

### FFmpeg
- **Location:** `/opt/homebrew/bin/ffmpeg`
- **What it does:** Frame extraction, audio/video stitching, encoding
- **Invoked by:** `extract-frames` skill, `video_stitcher.py`, video-use, and Hyperframes

### Remotion (React-based Video Composition)
- **Project:** `App Building/my-video/` (full Next.js + Remotion app)
- **Video Editor:** `remotion-app/src/remotion/` — components and compositions
- **MCP:** `npx @remotion/mcp@latest` (active in `~/.claude/.mcp.json`)
- **Skill:** `/remotion-best-practices` — 30+ rules covering animations, audio, assets, 3D, captions, etc. (the "how to code it" reference)
- **Skill:** `/Motion-Graphics` (`001_Architecture/Skills/Motion-Graphics/SKILL.md`, built 2026-07-10) — composition/design-taste companion to remotion-best-practices (the "what good looks like" reference): diagram/callout label placement, non-parallel radial leader lines, materialize-not-pop reveals, spring-overshoot pulse beats, color judgment (content vs. brand chrome), timing/easing guidance, and treatment-style craft notes (Kinetic Typography, Vox Documentary, Kurzgesagt Animated). Defers to the living, production-corrected rule ledger at `002_Content-Creation/Video_Editor/003_Remotion/src/skills/design-rules-learned.md` as ground truth over its own general principles.
- **Use case:** Programmatically compose videos as React components

### Video Stitching
- **Python Tool:** `001_Architecture/Tools/Video-Generation/Generic_Tools/video_stitcher.py` — stitch scenes (video.mp4 + audio.mp3) into final MP4
  - Usage: `python3 001_Architecture/Tools/Video-Generation/Generic_Tools/video_stitcher.py scene_1/ scene_2/ ... -o final.mp4`

### Final Cut Pro XML Export
- **Python Tool:** `001_Architecture/Tools/Remotion/export_fcpxml.py` — export timeline as FCPXML 1.9
  - Usage: `python3 001_Architecture/Tools/Remotion/export_fcpxml.py --video-dir outputs/<project>`
  - Allows importing into Final Cut Pro for further editing

---

## Notion

### Notion MCP Plugin
- **Status:** Installed but DISABLED (can be enabled)
- **What it does:** Full Notion workspace integration — pages, databases, properties
- **Enable:** Turn on in `~/.claude/settings.json` plugins
- **API Key:** `NOTION_API_KEY`

### Notion Bookmark Enrichment
- **Python Tool:** `001_Architecture/Tools/Notion/enrich-notion-bookmarks.py` — autonomous script
  - Processes all 14 bookmark databases
  - Scrapes URLs via Firecrawl
  - Generates AI summaries via Claude
  - Updates Notion descriptions
  - Runs: `source ~/.env-secrets && python3 001_Architecture/Tools/Notion/enrich-notion-bookmarks.py`

---

## Obsidian / Knowledge Vault

### Obsidian MCP
- **Vault Location:** `/Users/tonymacbook2025/Documents/Agent-OS`
- **API Key:** `OBSIDIAN_API_KEY`
- **What it does:** Read/write access to all 1,382+ markdown notes in the vault

### Obsidian Skills
- `/obsidian` — General Obsidian integration
- `/obsidian-cli` — CLI-based access
- `/obsidian-markdown` — Markdown format in Obsidian
- `/obsidian-bases` — Obsidian Bases feature (database-like functionality)

### Future: Obsidian RAG
- Plan exists for Obsidian vault + Qdrant + search_vault MCP (separate, planned system)

---

## Cross-Agent Memory

### claude-mem
- **Version:** 12.4.9
- **What it does:** Captures coding-session activity, compresses it into searchable observations, and injects relevant context into future sessions.
- **Installed for:** Claude Code and Gemini CLI
- **Codex:** Local `thedotmack` marketplace registered from `/Users/tonymacbook2025/.claude/plugins/marketplaces/thedotmack`; use worker/search route if plugin tools are not loaded in the active session.
- **Worker:** `http://localhost:37701`
- **Status:** `npx claude-mem status`
- **Start:** `npx claude-mem start`
- **Data:** `/Users/tonymacbook2025/.claude-mem/`
- **Gemini hooks:** `/Users/tonymacbook2025/.gemini/settings.json`
- **Gemini context injection:** `/Users/tonymacbook2025/.gemini/GEMINI.md`
- **Claude search:** `/mem-search`
- **Privacy:** Wrap sensitive text in `<private>...</private>` to exclude it from memory.

---

## GitHub

### GitHub MCP Plugin
- **Status:** Enabled
- **What it does:** Full GitHub repo management — PRs, issues, commits, branches
- **Auth:** `GITHUB_PERSONAL_ACCESS_TOKEN` in `~/.env-secrets`
- **Skills** (via plugin):
  - Git workflow: `/commit`, `/commit-push-pr`, `/clean_gone`
  - PR/code review: `/review-pr`, `/code-review`

---

## Figma

### Figma MCP
- **Status:** Enabled
- **Endpoint:** `https://mcp.figma.com/mcp`
- **What it does:** Design generation, component export, design system integration

### Figma Skills
- `/frontend-design` — Guided frontend design workflows
- `/stitch-design-taste` — Design taste via Stitch design tool

---

## Cloudinary (Media Storage & CDN)

### Cloudinary MCP Plugin
- **Status:** Enabled
- **API Key:** (Cloudinary credentials in plugin settings)
- **5 MCP Endpoints:**
  1. Asset Management — upload, organize, manage media files
  2. Environment Configuration — manage Cloudinary account settings
  3. Structured Metadata — apply metadata to assets
  4. Analysis — analyze media, get stats
  5. MediaFlows — automated media transformation workflows

### Cloudinary Python SDK
- **Status:** Installed (`pip3 install cloudinary --break-system-packages`)
- **Version:** 1.44.2 — `/opt/homebrew/lib/python3.14/site-packages`
- **Credentials:** `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_Key`, `CLOUDINARY_API_Secret` in `~/.env-secrets`
- **Primary use:** Upload local images to get public HTTPS URLs for AI APIs that require hosted image URLs (e.g. `firstFrame`/`lastFrame` in kie.ai Seedance, Veo3, etc.)
- **Pattern:**
  ```python
  import cloudinary, cloudinary.uploader
  cloudinary.config(cloud_name=os.environ['CLOUDINARY_CLOUD_NAME'],
                    api_key=os.environ['CLOUDINARY_API_Key'],
                    api_secret=os.environ['CLOUDINARY_API_Secret'], secure=True)
  result = cloudinary.uploader.upload(local_path, public_id="my_id", overwrite=True)
  url = result['secure_url']  # public HTTPS URL
  ```

---

## n8n Workflow Automation

### n8n MCP
- **Connected to:** `unomas.app.n8n.cloud`
- **What it does:** Create, run, inspect n8n workflows from Claude
- **Auth:** `N8N_MCP_TOKEN` in `~/.env-secrets`

### n8n Skills (6 available)
- `/n8n-workflow-patterns` — Design patterns for workflows
- `/n8n-node-configuration` — Configure n8n nodes
- `/n8n-code-javascript` — Write JavaScript code nodes
- `/n8n-expression-syntax` — n8n expression language
- `/n8n-validation-expert` — Validation patterns
- `/n8n-mcp-tools-expert` — MCP tools integration

---

## Publishing & Social Scheduling

### Blotato — MCP server, registered and active (see full entry above under Publishing)
- **What it does:** YouTube + social media (Instagram, TikTok, Facebook) publishing
- **Access:** MCP tools (`mcp__blotato__*`) — see "Blotato (Publishing)" entry above for tool list, connected accounts, and gotchas
- **Integration:** Final step in Video Editor production pipeline — Phase 12 of the Reimagined Realms Video Pipeline skill automates this end-to-end

### Meta Graph API
- **What it does:** Facebook/Instagram publishing and analytics
- **API Key:** `META_GRAPH_API_KEY`

---

## Vercel (Deployment)

### Vercel Plugin
- **Status:** Enabled
- **What it does:** Deploy Next.js/full-stack apps, manage environments, domains, analytics
- **Skills lock:** `001_Architecture/Skills/skills-lock.json` (tracks installed Claude Code skills, including `vercel-cli` from `vercel/vercel`)
- **Commands:**
  - `/vercel:deploy` — Deploy to Vercel
  - `/vercel:env` — Manage environment variables
  - `/vercel:status` — Check deployment status
  - Plus 15+ more Vercel-specific commands

---

## Airtable (Content Tracking)

### Airtable Integration
- **Python Module:** `tools/airtable.py` — CRUD operations in Video Editor
- **Use case:** Track video content, performance scores, publishing status
- **API Key:** `AIRTABLE_API_KEY`
- **Status:** Planned — structure TBD, not yet fully operational

---

## Tool Manager (Cost Routing & Model Intelligence)

### tm CLI
- **What it does:** Live cost routing and model recommendation for all pipelines. Knows pricing for every API in the toolbox, researches model capabilities via Perplexity, and recommends the cheapest/best option before any pipeline runs.
- **CLI:** `001_Architecture/Tools/Tool-Manager/tm [command]`
- **Commands:**
  - `tm status` — check if pricing cache and model DB are current
  - `tm cost --pipeline "images:15,video:15,tts:3min,music:1track"` — estimate full pipeline cost
  - `tm recommend --type image|video` — best model + backup for a task
  - `tm research-models` — populate model capabilities DB via Perplexity
  - `tm refresh` — scrape all pricing pages (auto-runs monthly via cron)
  - `tm fal-search "<query>" [--pricing] [--limit N]` — search fal.ai model catalog via authenticated Platform API (`https://api.fal.ai/v1/models?q=`); add `--pricing` to fetch per-model pricing inline
- **Data files:**
  - `data/pricing_cache.json` — live pricing for all APIs (OpenAI, kie.ai, ElevenLabs, fal.ai, Firecrawl, etc.)
  - `data/model_capabilities.json` — pros/cons/benchmarks/rankings for all image and video models
- **Skill:** `tool-manager` — MANDATORY AUTO-INVOKE before any pipeline or tool decision
- **Cron:** Monthly refresh on the 1st at 3am
- **Note:** kie.ai pricing page is auth-gated — prices populated via Perplexity research. Run `tm refresh` after logging in manually if needed.

---

## AI Research

### Perplexity
- **What it does:** AI-powered web search for viral topics, trends, research
- **Skill:** Referenced in Video Editor workflows for topic research
- **API Key:** `PERPLEXITY_API_KEY`

### NotebookLM
- **What it does:** Grounded research notebooks — answers only from sources you provide
- **Skill:** `/notebooklm` — create research notebooks, query them fact-checked
- **Use case:** Video research that can't hallucinate beyond uploaded sources

### YouTube Transcript
- **Skill:** `/youtube-transcript` — extract and analyze YouTube video transcripts

---

## Agent-OS Validation System (Checks & Balances)

Built 2026-06-19. Ensures Claude never declares work done without proof.

### Claude Code Hooks (`~/.claude/hooks/`)
- **`agent-os-build-tracker.js`** — PostToolUse hook. Fires after every Write/Edit/MultiEdit. Detects functional artifacts (.py, .sh, .js, SKILL.md, tool configs, settings.json). Injects `⚠️ VERIFY REQUIRED` into Claude's context immediately. Appends file to build manifest.
- **`agent-os-stop-validator.js`** — Stop hook. REMOVED (Jun 19, 2026) — fired after every turn and banner couldn't be suppressed. Tool-Manager workflow is the replacement guardrail.

### Build Manifest
- Location: `/tmp/agent_os_build_manifest.json` (session-scoped, auto-created)
- Tracks: `unverified` (written, not yet checked) and `verified` (passed validation)
- Stop hook clears block once all items move to verified

### Validation Script
- **File:** `001_Architecture/Scripts/validate_build.py`
- **Usage:** `python3 001_Architecture/Scripts/validate_build.py --files "path1.py,path2/SKILL.md"`
- **Type-aware checks:**
  - `.py` → syntax (`py_compile`) + CLI `--help` smoke test + referenced path existence
  - `SKILL.md` → frontmatter present, `name:` field, name registered in Skill-Index.md
  - `.json` → valid JSON parse
  - `.sh` → executable bit + bash syntax check
  - `.js` → exists and non-empty
- **Data fetch completeness:** `python3 validate_build.py --data-fetch --sources "kie.ai,fal.ai,openai" --got "kie.ai,openai"` — diffs expected vs. resolved, flags missing sources
- When a file passes, it's moved from `unverified` → `verified` in the manifest, unblocking the Stop hook

### Rules This System Enforces
- Never declare a build done without running `validate_build.py` on it
- Multi-source data fetches must report ALL sources (pass + fail with error + fix instructions)
- Stop hook is a hard gate — Claude cannot finish a turn if functional artifacts are unverified

---

## Code Development Workflow

### Git Commands
- `/commit` — Interactive git commit with staging
- `/commit-push-pr` — Commit + push + create PR (full workflow)
- `/clean_gone` — Clean up deleted branches locally

### Code Review & Quality
- `/code-review` — Structured code review process
- `/review-pr` — Pull request review with detailed analysis
- `/feature-dev` — Guided feature development workflow

### Plugins (Language Servers)
- **pyright-lsp** (enabled) — Python type checking via Pyright
- **typescript-lsp** (enabled) — TypeScript type checking via TypeScript LS

---

## Project Management

### GSD (Get Shit Done) System
- **49 commands** — `/gsd:<command>` — full project lifecycle management
- **Core commands:**
  - `/gsd:new-project` — Start a new project with roadmap
  - `/gsd:plan-phase` — Plan a phase with research + task breakdown
  - `/gsd:execute-phase` — Execute phase with atomic commits
  - `/gsd:verify-work` — Verify phase goal achievement
  - `/gsd:progress` — Check overall progress
  - `/gsd:ship` — Ship completed work
- **Plus:** 44 more commands for backlog, milestones, debugging, auditing, etc.

### Ralph Loop
- **Command:** `/ralph-loop` — autonomous recurring task agent
- **Cancel:** `/cancel-ralph` — stop the loop
- **Use case:** Automated, repeating workflows without manual triggering

---

## Affiliate Marketing (005_Affiliate_Marketing/)

Multi-platform affiliate marketing operations. 18 programs tracked across travel, digital tools, and e-commerce.

### Programs Active
| Program | Network | Niche |
|---------|---------|-------|
| Amazon Associates | Direct | General / travel gear |
| Impact Affiliates | Impact | Multi-brand network |
| TravelPayouts | TravelPayouts | Flights, hotels, travel |
| Expedia | Direct | Hotels / travel |
| Bookaway | Direct | Ground transport |
| GetYourGuide | Direct | Tours & activities |
| Hostelworld | Direct | Accommodation |
| JR Pass | Direct | Japan rail |
| Klook | Direct | Travel experiences |
| SafetyWing | Direct | Travel insurance |
| Stay22 | Direct | Accommodation |
| Digistore24 | Digistore24 | Digital products |
| 12Go | Direct | Asia transport |
| Higgsfield | Direct | AI video tool |
| Magnific | Direct | AI upscaler |
| OpusClip | Direct | Video clipping |
| VidIQ | Direct | YouTube tools |
| TikTok Shop Affiliate | TikTok | Product affiliate |

### Key Docs
- Affiliate compliance docs → `007_Resource_Library/Docs/Affiliate_Marketing/` (ToS, allowed/prohibited rules for all programs)

---

## Video Editor Specific Tools

### TikTok Shop Affiliate Video
- **Skill:** `/tiktok-shop-affiliate-video` — `001_Architecture/Skills/TikTok-Shop-Affiliate-Video/`
- **General mode:** raw footage + pre-recorded VO clips → 3 visual edits × 2 audio tracks (TikTok + YouTube Shorts) = 6 outputs. Audio-first: VO drives the cut.
- **Neon Parcel TikTok Shop Creator mode** (locked in 2026-07-12, validated on Colorsmart Pens): a distinct invocation context within the same skill — 3 genuinely different vertical cuts (different beats/pacing per video, not shared-cut-swapped-audio), no YouTube pairing, output routed to `005_Affiliate_Marketing/Tiktok_Shop_Affiliate/Neon_Parcel_TikTok_Shop_Creator/Videos/NNNN_Product-Slug/`. Full design spec: `001_Architecture/Superpowers/Specs/2026-07-11-Neon-Parcel-Tiktok-Shop-Creator-Pipeline-Design.md`.
- **Scripts** (all in `scripts/`):
  - `analyze_clips.py` — FFmpeg scene-change keyframes → Qwen-VL (OpenRouter) → `clip_analysis.md`. For narration-driven shot matching (validated workflow), also transcribe the VO with ElevenLabs Scribe word-level timestamps first, then run denser frame sampling (every ~4s, not just scene-change) across raw clips to match real footage moments to what's being said — scene-change detection alone is often only 1 frame for long continuous handheld shots. **Qwen-VL hard caps:** max 16 images per OpenRouter call (batch at ≤8 to also stay under the 128K context limit at full frame resolution — downscale frames to ~640px width before sending). **Blind spot confirmed 2026-07-31:** the model cannot reliably detect subtle grime/residue described narratively, and will misread footage of a *now-transparent* cleaned surface as "empty/no subject" — trust the creator's own description of their footage over automated vision when they conflict, after one verification pass.
  - `trim_vo_pauses.py` — shrinks overlong VO pauses to a natural ~0.35s. Always keeps 120ms of real audio on both sides of a cut (no word clipping) and applies a 15ms fade at every join (no clicks/pops) — a naive hard-cut trim produces both failure modes. Run before `normalize_loudness.py` (SKILL.md Step 5a.4, new 2026-07-31).
  - `scaffold_product_folder.py` — per-product folder scaffolder (Edit/, Compliance/{Vision-Scan,Transcript-Scan,Ledger-Scan-Results.md}, Package/)
  - `extract_compliance_sources.py` — pulls real TikTok Seller University URLs embedded in the TOS bundle (never invents URLs)
  - `validate_compliance_ledger.py` — structural validator for `Compliance-Ledger.md`
  - `check_tos_freshness.py` — Firecrawl-based live policy freshness check (14-day/always-escalate cadence). **Known limitation:** Firecrawl currently refuses to scrape `seller-us.tiktok.com` entirely ("we do not support this site") — confirmed not an auth/rate-limit issue. This phase is correctly wired but provides zero real drift-detection value until resolved.
  - `compliance_vision_scan.py` — post-build logo/watermark scan, fails safe to FLAG on ambiguous response. Reliably flags the product's own label/logo (correct behavior — always needs human resolution to distinguish "own product" from real third-party branding).
  - `compliance_transcript_scan.py` — post-build banned-phrase scan (guarantee/cure/medical-outcome language), fails safe to FLAG on empty/failed transcription
  - `normalize_loudness.py` — two-pass EBU R128 loudness normalization (default target -14 LUFS / -1.5 dBTP), run on VO before muxing (SKILL.md Step 5a.5). Added because raw VO measured -34 to -35 LUFS with no normalization step previously.
- **Compliance ledger:** `005_Affiliate_Marketing/Tiktok_Shop_Affiliate/Neon_Parcel_TikTok_Shop_Creator/Compliance-Ledger.md` — 10 citation-backed rules. RULE-008 (disclosure) has a real-world addendum (2026-07-12): TikTok auto-adds a "Creator earns commission" tag when a Shop product link is attached, which serves as the disclosure for affiliate content — do not add `#ad`/`#sponsored` for Neon Parcel TikTok Shop Creator videos with a product link; use ~3 relevant hashtags instead.
- **API keys:** `OPENROUTER_API_KEY` (vision), `ELEVENLABS_API_KEY` (transcription/TTS), `FIRECRAWL_API_KEY` (freshness check) via `source ~/.env-secrets`
- **Trigger:** "create affiliate video", "edit product footage for TikTok", "make shop video"
- **Video output policy:** never commit rendered `.mp4` files from this (or any) pipeline to GitHub — only commit scripts/skill/compliance-doc changes (`.gitignore` already excludes `*.mp4`)

### Video Editor Skills (in Video-Editor `.agents/skills/` and Obsidian Vault)
- `/download-video` — Download YouTube videos at 720p
- `/extract-frames` — Extract frames from video at 0.5s intervals
- `/kie-api-fetch` — Fetch and document kie.ai model APIs
- `/fal-api-fetch` — Fetch and document fal.ai model APIs
- `/analyze-video` — Gemini analysis of video style
- `/case-study` — Full automated case study generation (located in `/Obsidian-Vault/000_Skills/`)
- `/documentary-research` — CC0 footage research (archive.org, Openverse, NASA, etc.)
- `/storytelling` — Comprehensive scriptwriting framework (Curiosity Loop, 3-Act, Hero's Journey, etc.)
- `/anomalous-wild-scriptwriter` — Channel-specific script writing (Anomalous Arc™)
- `/video-beat-sheet` — Convert script to production beat sheet
- `/ai-footage-prompter` — Generate video/image prompts for AI generation
- `/title-hook-generator` — Generate titles, hooks, descriptions for CTR

### Neon Parcel Long-Form Compilation Pipeline (Global — `001_Architecture/Skills/Neon_Parcel_Longform_Compilation/`)
- **Invoke:** `/neon-parcel-longform`
- **Purpose:** Reference-inspired 16:9 animal compilations for Neon Parcel, with variable-duration generated clips, post-assembly editorial narration, Suno music, Shorts derivatives, report cards, and explicit Blotato approval gates.
- **Scaffold:** `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/scaffold_new_production.py`
- **Checkpoint ledger:** `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/production_state.py` records the current state plus append-only decision history.
- **Shot complexity router:** `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/route_shot_complexity.py` scores each shot before generation and routes simple shots to Seedance 1.5 at 1080p, complex shots to Seedance 2 Mini at 480p with storyboard guidance followed by Topaz 2x and FFmpeg normalization to 1920x1080, and borderline shots to human review. It only writes an auditable JSON decision; it never calls a provider or spends credits.
- **Contract:** `001_Architecture/Skills/Neon_Parcel_Longform_Compilation/pipeline.yaml`
- **Scope boundary:** This is separate from the Neon Parcel TikTok Shop affiliate pipeline. Preserve reference media and all production versions; never auto-publish or activate learned humor patterns.
- **2026-09-04 hardening checkpoint:** Storyboard and Seedance lessons are propagated into the governing skills and executable Neon Parcel tools, not stored only as session memory. Vision inspection is advisory evidence; Tony makes the storyboard/video decision. Paid retries, fallbacks, upscales, and normalized derivatives always use new versions and preserve prior artifacts.

### Reimagined Realms Video Pipeline Skill (Global — `001_Architecture/Skills/Reimagined_Realms_Video_Pipeline/`)
- **Invoke:** `/reimagined-realms`
- **Purpose:** Full 10-phase faceless YouTube video pipeline. Replaces Higgsfield MCP — no subscription needed.
- **Workflow:** Channel analysis (Firecrawl) → Story ideation (DAIPBR + 7-part template) → Script → Beat table → Cost estimate (3 combos: GPT Image+Seedance, Nano Banana+Kling, Nano Banana+Veo 3.1) → ElevenLabs voiceover → Beatmap from VO timestamps → Shot list (per-clip image+video prompts) → YouTube package
- **Output:** `Productions/[topic-slug]/` — 8 files: script, beat table, cost estimate, voiceover, timestamps, beatmap, shot list, YouTube package
- **Tools used:** Firecrawl CLI, Tool Manager pricing cache, `001_Architecture/Tools/Text-To-Speech/audio_tts.py`, kie.ai (KIE_API_KEY), ElevenLabs (ELEVENLABS_API_KEY)
- **Voice ID (Reimagined Realms):** `raMcNf2S8wCmuaBcyI6E` (ElevenLabs multilingual v2)
- **Note:** `~/.claude/skills/` is a symlink to `001_Architecture/Skills/` — skill is global across Claude, Codex, and Gemini

### Production-Research-Agent (Global, channel-agnostic — `001_Architecture/Skills/Production-Research-Agent/`, added 2026-08-18)
- **Purpose:** Invoked right after any production's topic is chosen — deep topic research, real reference images (capped 20, grounding only, never used directly in final video), and Pexels B-roll video search/download (capped 10 clips, 1080p 16:9 only), then analyzes each clip and writes `Research/Pexels_Inventory.json` with full attribution fields captured at download time.
- **Used by:** Anomalous Wild (Phase 1, Step A3); designed to be reusable by any channel — Reimagined Realms, Kingdom and Conquerors, Glifry, Polyoculus.
- **Depends on:** `001_Architecture/Tools/Tool-Manager/data/Pexels_API_Reference.md` for the Pexels integration details.

### Production-Asset-Planner (Global, channel-agnostic — `001_Architecture/Skills/Production-Asset-Planner/`, added 2026-08-18)
- **Purpose:** Invoked once a production's shot list exists — one combined pass that decides which conditional sheets (prop/environment/background-character) are needed, generates storyboards + per-split-clip start/end frames, and decides per beat whether real Pexels B-roll (from Production-Asset-Planner's Research Agent inventory) already covers it vs. needs AI generation. Max 5s of B-roll per clip; non-destructive trimming into `B_Roll/<Scene_ID>.mp4`.
- **Used by:** Anomalous Wild (Phase 5B, replacing the previous inline logic); channel-agnostic by design.
- **Depends on:** `Production-Research-Agent` having already run for that production.

### Motion-Graphics-Compositing (Global, channel-agnostic — `001_Architecture/Skills/Motion-Graphics-Compositing/`, added 2026-08-18)
- **Purpose:** How to build animated diagrams, infographics, data-viz, and collage-style motion graphics — generate isolated component assets (transparent bg or chroma-screen + AI matting), composite/animate them in Remotion via reusable keyframe presets, instead of asking Seedance to animate the content (confirmed to hallucinate hard on abstract/diagram material — worse than its known creature-drift issue).
- **Origin:** Anomalous Wild Scene 02 (photoreceptor diagram) — Tony-graded "A+" against the failed Seedance alternative.
- **Reusable Remotion lib:** `002_Content-Creation/Video_Editor/003_Remotion/src/remotion/video-lib/motion_graphics_presets.ts` — `kf()` keyframe helper + named presets (`crossfade`, `pushZoom`, `pullBackReveal`, `sideBySideHold`, `explodedAssembly`; `lineTraceReveal` stubbed, not yet implemented).
- **Asset matting:** `kie-cli recraft_remove_background` (Recraft AI background removal, confirmed true RGBA output) — see also Pexels-style note below on the platform routing rule for GPT-Image-2.
- **Asset library:** per-production `Production/Motion_Graphics_Asset_Library.json` + cross-production master index at `000_Wiki/Video-Production/Motion-Graphics-Asset-Library.md` (graphified for retrieval).
- **Audio:** reuses `generate_foley.py`/`foley_config.py` (Mirelo/Sonilo video-to-SFX) — no new audio tool built.
- **`Diagram-Generation` skill's Approach B now delegates its asset-isolation + compositing mechanics here.**

### Tool-Manager capability-parity field (added 2026-08-18)
- **What changed:** `model_catalog.json` model entries can now carry a `capabilities` block (feature/platform parity, not just price) — populated so far on the `gpt-image-2` entry: kie.ai's wrapper exposes no transparent-background parameter; direct OpenAI does (`background: "transparent"`, not yet live-confirmed against our account).
- **New routing rule:** check `capabilities` BEFORE applying the cheapest-price rule — price only decides among platforms that already support the required capability. kie.ai is cheaper for GPT-Image-2 ($0.03 vs $0.04/image) but that's irrelevant if the job needs transparency output it doesn't expose.
- **Standing process rule:** consult Tool-Manager before defaulting to any platform/endpoint, unprompted. If Tool-Manager's data doesn't cover the actual question, tell Tool-Manager to research and update its own data via its Update Protocol — don't surface an unresearched question back to Tony.

### Seedance Prompting Guide (Global — `001_Architecture/Skills/Seedance-Prompting-Guide/`)
- **Purpose:** Living reference for prompting any ByteDance Seedance version (1.5 Pro, 2.0, 2.0 Fast, future) — dialogue vs. ambient/foley-only audio control, camera movement/cinematic shot language, negative-prompt conventions. Update in place as new versions ship; never fork a per-version copy.
- **Key facts:** quoted speech in the prompt triggers lip-synced dialogue (omit quotes for no-dialogue); `generate_audio` boolean controls native audio generation; negative prompts are a single dash-led closing line naming forbidden elements (e.g. `- No dialogue, no music, no text on screen.`).
- **When to use:** Any time a prompt is being written for Seedance video generation, for any pipeline/channel.

### Reimagined Realms — POV Shorts Pipeline (`001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/`)
- **Purpose:** Vertical (9:16), historical "day in the life" POV Shorts for Reimagined Realms — no dialogue, Seedance native audio (foley/ambient) + Suno music. Separate from the long-form Reimagined Realms pipeline above.
- **Status:** `POV_Style_Guide.md` (distilled from 2 analyzed reference videos) and a standalone Foley/SFX generator (`generate_foley.py`, swappable Mirelo/Sonilo via `foley_config.py`) are built. Beat planning, image/video generation, assembly, and publishing are separate, later plans — see `001_Architecture/Superpowers/Specs/2026-08-01-RR-POV-Shorts-Pipeline-Design.md`.
- **Design note:** initial plan used a dedicated Foley model per clip; a live A/B test (Mirelo/Sonilo Foley vs. Seedance's own native `generate_audio`) showed Seedance's native audio was the better match — see the design spec for the full decision trail. The Foley generator is still built and available as a fallback/alternative.

### Reimagined Realms — Batch Generation + Assembly Scripts (`001_Architecture/Tools/Video-Generation/Channels/Reimagined_Realms/`)
- **batch_generate_images.py** — Generate all clip images via GPT Image 2 on kie.ai
  - Usage: `python3 batch_generate_images.py <production_folder> [--clips C20 C21] [--overwrite]`
  - Reads: `Data/Beatmap.json` + `Production/Shot_List.md` (Image prompts)
  - Saves: `Images/C01_0.0s-3.8s.png ...`; skips existing — safe to re-run
  - `--clips`: generate subset only; `--overwrite`: regenerate even if file exists
- **batch_generate_videos.py** — Generate all clip videos via Seedance 1.5/2.0 on kie.ai (image-to-video)
  - Usage: `python3 batch_generate_videos.py <production_folder> [--clips C20] [--overwrite] [--audio]`
  - Reads: `Images/*.png` + `Production/Shot_List.md` (Video prompts) + `Data/Beatmap.json`
  - Uploads images to Cloudinary → submits to kie.ai → polls → saves `Video_Clips/C01_0.0s-3.8s.mp4 ...`
  - Model routing: Seedance 1.5 Pro (≤12s generate) / Seedance 2.0 (>12s); hard cap 8s final per clip
  - Keys required: `KIE_API_KEY`, `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_Key`, `CLOUDINARY_API_Secret`
- **assemble.py** — Universal assembly pipeline (trim → concat → narration → Suno → grade → caption)
  - Usage: `python3 assemble.py <production_folder> [--phase N] [--stop-phase N] [--overwrite] [--clips C20,C21] [--skip-suno]`
  - Reads: `Production/assemble_config.json` (suno_prompt, suno_tags, caption_line1, caption_line2)
  - Reads: `Data/Beatmap.json`, `Video_Clips/`, `Narration_Audio/`
  - Hard cap: 8s max final clip duration (enforced at trim phase regardless of beatmap value)
  - Suno endpoint: `https://api.kie.ai/api/v1/generate` — requires `callBackUrl` field
  - Output: `Assembly/raw_video.mp4`, `Assembly/narration.mp3`, `Assembly/music.mp3`, `Assembly/final.mp4`

### Reimagined Realms — Audio Pipeline (`001_Architecture/Tools/Audio/`)
- **compose_audio.py** — Vision-based per-scene audio composer
  - Usage: `python3 compose_audio.py <production_folder> [--reanalyze] [--dry-run]`
  - Reads: `Assembly/Frames/` (1fps frames) + `gemini_scene_analysis.md` + `Data/Beatmap.json`
  - Outputs: `Data/audio_briefs.json`, `Data/per_scene_stem_map.json`
- **generate_stems.py** — Generate per-scene SFX clips via ElevenLabs
  - Usage: `python3 generate_stems.py <production_folder> [--stems-file Data/per_scene_stem_map.json] [--stems c20 c21] [--overwrite]`
- **analyze_stems.py** — LUFS measurement and gain correction per stem
  - Usage: `python3 analyze_stems.py <production_folder> [--stems-file Data/per_scene_stem_map.json]`
  - Writes corrected `volume`, `measured_lufs`, `gain_db` back to stem map JSON
- **mix_stems.py** — Mix all stems onto video timeline with S-curve (hsin) crossfades
  - Usage: `python3 mix_stems.py <production_folder> [--stems-file Data/per_scene_stem_map.json] [--narration Assembly/narration.mp3]`
  - Output: `Assembly/stems_mix.mp3`; optionally `Assembly/stems_narration_mix.mp3`
- **audio_pop_scan.py** — Pre-review splice-pop gate (raw PCM + numpy; catches un-faded audio joins)
  - Usage: `python3 audio_pop_scan.py <render.mp4> --production <production_folder> [--joins t1,t2,...] [--json]`
  - Exit 1 on any silence-bounded hard step / very-hard step / narration-join discontinuity; run before every AW review (SKILL Phase 8)
- **render_video.py** — Versioned renderer — keeps all audio tracks separate, bakes into MP4
  - Usage: `python3 render_video.py <production_folder> --stems Assembly/stems_mix.mp3 --narration Assembly/narration.mp3 [--music Assembly/music.mp3] --stems-vol 0.88 --narration-vol 3.09 --music-vol 0.12 --duck --note "description"`
  - Locked formula: stems vol=0.88 (-23 LUFS), narration vol=3.09 (-14 LUFS), sidechain duck threshold=0.015 ratio=4 attack=150 release=800
  - Each version saved to `Assembly/V1/`, `Assembly/V2/` ... with independent track copies + render_notes.md
  - Updates `Assembly/RENDER_LOG.md`

### Anomalous Wild — Batch Generation Scripts (`001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/` + `Generic_Tools/`)

Full history/status write-up: [[000_Wiki/Video-Production/Anomalous-Wild-Pipeline-Scripts]]. Anomalous Wild is the *first* video pipeline ever built in this workspace (predates Reimagined Realms), so its early tooling is more fragmented — several scripts do overlapping jobs from different eras. **A unifying orchestrator skill is now built** (2026-07-07/08): `001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/SKILL.md` (invoke via `/anomalous-wild`), designed at `DESIGN.md` + `PLAN.md`. See the next section for the new pipeline's own scripts.

- **pipeline_supervisor.py** (`Channels/Anomalous_Wild/`) — ✅ **ACTIVE / preferred generation script.** Batch clip generator with real error-code classification (FATAL/CREDITS/SKIP/RATE/WAIT/RETRY/UNKNOWN), automatic retries, macOS notifications, auto-preloops after each successful clip. Seedance: 1.5 Pro by default; a beat with `model: bytedance/seedance-2` (or `-2-fast`) is sent as a real Seedance 2 call, frames mode or reference mode (reference prompts must pass the @Image tag lint). Mixed modes or an unknown model = CONFIG error, nothing submitted, no retries (2026-09-27).
  - Usage: `python3 pipeline_supervisor.py` (run from `002_Content-Creation/Video_Editor/`) or `--status`
  - Reads: `Production/new_clips_prompts.json` (per-clip `output_folder`, now `Video_Clips/` — files keyed by `{scene_id}.mp4`, not a fixed `video.mp4` name)
  - Kept in the new pipeline design as-is (Task list: "✅ Reused as-is")
- **run_new_clips_batch.py** (`Generic_Tools/`) — ⚠️ **SUPERSEDED, not deleted.** Simpler batch generator, only ever used for Bioluminescence Weapon despite living in "Generic_Tools." Does the same job as `pipeline_supervisor.py` but without the retry/error-handling sophistication. Its one distinguishing feature — auto-appending a scientific no-text negative prompt for `is_diagram: true` image entries (added after the Video 001 Report Card caught garbled diagram text) — didn't reliably work, since negative prompts alone don't stop image models from occasionally rendering text anyway. That idea carries forward into the new pipeline's Scientific Diagram sub-pipeline (research reference → generate clean illustration → vision-verify → label in Remotion), which is the actual fix. Left in place, unused going forward once the new sub-pipeline is built.
- **preloop_new_clips.py** (`Generic_Tools/`) — post-processes freshly generated clips into looped versions matching narration duration. Called by `pipeline_orchestrator.sh`.
- **preloop_videos.sh** (`Channels/Anomalous_Wild/`) — same job as above but for the original 12 hand-picked hero clips (hardcoded durations). Needs bash 4+ for `declare -A`; the system bash 3.2 couldn't run it. Fixed 2026-07-07 via `brew install bash` (now 5.3.15, ahead of system bash in PATH — plain `bash` picks it up automatically, no script changes needed). Verified working end-to-end.
- **pipeline_orchestrator.sh** (`Channels/Anomalous_Wild/`) — 6-stage wrapper chaining `run_new_clips_batch.py` → `preloop_new_clips.py` → `preloop_videos.sh` → `check_pipeline_status.py`. Fixed 2026-07-07 (was calling a `004_Tools/` path that stopped existing after a June reorg — pre-existing breakage, not caused by that day's folder retrofit).
- **check_pipeline_status.py** (`Channels/Anomalous_Wild/`) — read-only progress report: which clips/images are done vs. pending.
- **BioluminescenceDoc.tsx** (Remotion, `003_Remotion/src/remotion/video-components/`) — the actual Remotion composition that assembles Bioluminescence Weapon. One-off, hardcoded to that video's scenes/durations — not a reusable template. A reference copy lives at `Productions/0001_Bioluminescence_Weapon/Remotion/` for archival purposes; the live version stays in `003_Remotion` untouched.
- **AnomalousWildEndCard.tsx** (Remotion) — channel-wide end card. In practice, the pipeline just appends the pre-rendered `end_card_v3.mp4` via ffmpeg (locked per DESIGN.md) rather than re-rendering this per video. A reference copy lives at `Brand_Assets/End_Card/` alongside the mp4 files; still registered live in `Root.tsx` too.

### Anomalous Wild Pipeline — New Orchestrator (built 2026-07-07/08, `/anomalous-wild`)

Built via the `superpowers:subagent-driven-development` workflow, one task per script, each with an independent code-review pass (several fix rounds), plus a final whole-branch review that caught 2 cross-cutting integration bugs the per-task reviews couldn't see. Full task history and every review finding: `.superpowers/sdd/progress.md` (session-scoped scratch ledger, not durable — see wiki for the durable write-up).

- **build_motion_graphics_profile.py** + **data/motion_graphics_capabilities.json** (`001_Architecture/Tools/Tool-Manager/`) — Research-backed capability profile for Remotion / video-use / Hyperframes / Manim, every entry cites a real source (skill doc path or dated session precedent). Consulted by Tool-Manager when the Anomalous Wild orchestrator needs to route a beat's visual need to a tool — never a hardcoded lookup.
- **generate_narration_with_timestamps.py** (`Channels/Anomalous_Wild/`) — thin wrapper around the existing `generate_voiceover_with_timestamps()` (`Tools/Text-To-Speech/audio_tts.py`). Reads `Scripts/Narration.md` (`## scene_id` sections), writes `Narration_Audio/<scene_id>.mp3` + `_beat_sheet.json` (word-level timestamps) per scene.
- **build_beat_table.py** (`Channels/Anomalous_Wild/`) — reads `Narration_Audio/*_beat_sheet.json` + `Production/Scene_Routing.json`, writes `Production/Beat_Table.json`. Locks in `max_clip_s: 8.0` for `live_footage` beats, `max_static_s: 5.0` for diagram beats (no static frame >3-5s rule).
- **diagram_research_and_illustrate.py** (`Channels/Anomalous_Wild/`) — Scientific Diagram sub-pipeline steps 1-2: searches Openverse for a real reference image, then generates a clean no-text illustration via kie.ai GPT-Image-2 (`gpt-image-2-text-to-image`) with an explicit no-text/no-label negative prompt. This is the actual fix for the garbled-diagram-text problem from the Bioluminescence Weapon video's anglerfish diagram.
- **detect_label_coordinates.py** (`Channels/Anomalous_Wild/`) — Scientific Diagram sub-pipeline step 3: Gemini vision pass over the *actual* generated illustration, returns real `{feature, x_pct, y_pct, confidence}` coordinates. Structurally strips any coordinate attached to a `not_found` entry (never trusts the model to have omitted it) — the "never guess a label position" rule is code-enforced, not just a prompt instruction.
- **DiagramLabels.tsx** (Remotion, `003_Remotion/src/remotion/video-components/`) — Scientific Diagram sub-pipeline step 4: places labels/callout lines at the detected coordinates, staggered fade-in. Registered in `Root.tsx` via a Zod `schema=` prop (`diagramLabelsSchema`, matching the existing `AIVideo`/`aiVideoSchema` pattern in the same file — not a type-erasure cast). `x_pct`/`y_pct` are optional in the schema specifically so a `not_found` label (no coordinates) doesn't crash the composition.
- **generate_youtube_package.py** (`Channels/Anomalous_Wild/`) — adapts Reimagined Realms' title/description formulas to Anomalous Wild's science/nature framing. Thumbnail generation follows locked **template v2** (`Anomalos_Wild__Thumbnail_Style.json`, locked 2026-08-24) as a mandatory 2-stage pipeline run automatically per call: stage 1 generates 3 textless photoreal base concepts via kie.ai `gpt-image-2-text-to-image` (mood/palette variations); stage 2 uploads each to Cloudinary and edits it via `gpt-image-2-image-to-image` — darkens the real background ~50% (never flattened to a gradient), adds a per-concept neon glow rim-light, bakes in headline text + a red arrow pointing at the specific hook-fact anatomy. Takes `--headlines` (3, pipe-separated) and `--arrow-target` as required Claude-authored CLI inputs — Python string templates alone produce weak curiosity copy, don't rely on the fallback. Outputs `concept_N.png` (stage-1 base, intermediate only) and `concept_N_text.png` (finished, present this to Tony).
- **upload_to_blotato.md** (`Channels/Anomalous_Wild/`) — Blotato upload procedure doc mirroring RR's Phase 12 locked defaults. Confirmed Blotato YouTube `accountId: 42514` (displayed there as "Anomalos Wild," a spelling variant — confirmed correct by Tony 2026-07-08, not just inferred).
- **scaffold_new_production.py** (`Channels/Anomalous_Wild/`) — going-forward folder scaffolder: creates the 8 typed folders (matching Reimagined Realms' pattern) and hard-fails if the locked `end_card_v3.mp4` (`Brand_Assets/End_Card/`) is missing.
- **Anomalous_Wild_Video_Pipeline/SKILL.md** (`001_Architecture/Skills/`) — the orchestrator itself. Invoke via `/anomalous-wild`. 10 phases, mirrors Reimagined Realms' structure, explicit pause points (topic selection, live-footage cost estimate, first-clip quality check, title/thumbnail/privacy). Core principle: every beat's visual tool is chosen live via Tool-Manager, never hardcoded.

**Known cross-cutting bugs caught only by the final whole-branch review (both fixed):** (1) `detect_label_coordinates.py`'s `not_found` coordinate-stripping was rejected by `DiagramLabels.tsx`'s original required-field Zod schema — would have crashed diagram assembly exactly when the "never guess" safety path triggered; fixed by making `x_pct`/`y_pct` optional + a `hasCoordinates()` type guard. (2) The 3-5s no-static-frame rule was recorded in `Beat_Table.json` but nothing actually enforced it; fixed by adding a mandatory per-beat static-hold check to the orchestrator's Phase 7 (Assembly).

**Known pre-existing gaps flagged during this build, not yet resolved:** no locked ElevenLabs voice ID for Anomalous Wild (RR has one hardcoded, AW doesn't — orchestrator asks Tony/Tool-Manager at runtime); `pipeline_supervisor.py` expects a `Production/new_clips_prompts.json` manifest that no script yet auto-builds from the new `Shot_List.md` format (orchestrator treats this as an inline glue step).

---

## API Keys Reference

All keys stored in `~/.env-secrets`. When a tool requires a key, it's listed in `TOOLBOX.md` under that tool's section.

| Service | Key Variable | Used By |
|---------|--------------|---------|
| Firecrawl | `FIRECRAWL_API_KEY` | Firecrawl CLI, skills, enrich-notion-bookmarks.py |
| kie.ai | `KIE_API_KEY` | kie_video_gen.py, kie_image_gen.py |
| fal.ai | `FAL.AI_API_KEY` | image_gen.py fallback |
| ElevenLabs | `ELEVENLABS_API_KEY` | audio_tts.py |
| Notion | `NOTION_API_KEY` | Notion MCP, enrich-notion-bookmarks.py |
| Obsidian | `OBSIDIAN_API_KEY` | Obsidian MCP |
| YouTube Data | `YOUTUBE_DATA_API_KEY` | case_study_generator.py, Video Editor |
| YouTube Analytics | `YOUTUBE_ANALYTICS_API_KEY` | Video analytics tracking |
| Google / Gemini | `GOOGLE_API_KEY` | Gemini image/video analysis |
| OpenAI | `OPENAI_API_KEY` | General AI tasks |
| OpenRouter | `OPENROUTER_API_KEY` | Multi-model routing |
| Perplexity | `PERPLEXITY_API_KEY` | Topic research |
| Blotato | `BLOTATO_API_KEY` | YouTube/social publishing |
| Airtable | `AIRTABLE_API_KEY` | Content tracking |
| Cloudinary | (plugin settings) | Media storage/CDN |
| n8n | `N8N_MCP_TOKEN` | n8n MCP |
| GitHub | `GITHUB_PERSONAL_ACCESS_TOKEN` | GitHub MCP |
| Meta (Facebook/Instagram) | `META_GRAPH_API_KEY` | Social publishing |
| PubMed | `PUBMED_API_KEY` | Scientific research |

---

## System CLIs (OS Level)

| CLI | Location | What It Does |
|-----|----------|-------------|
| `ffmpeg` | `/opt/homebrew/bin/ffmpeg` | Video frame extraction, stitching, encoding |
| `bun` | `/Users/tonymacbook2025/.bun/bin/bun` | JavaScript runtime used by claude-mem worker and hooks |
| `gemini` | `/opt/homebrew/bin/gemini` | Google Gemini CLI for terminal-based AI agent workflows |
| `yt-dlp` | `/Library/Frameworks/Python.framework/Versions/3.13/bin/yt-dlp` | Download videos from YouTube and public sources |
| `python3` | `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3` | Python interpreter for all .py tools |
| `kie-cli` | npm global (`@felores/kie-cli`) | Live kie.ai model discovery by category — needs `KIE_API_KEY` |
| `wavespeed` | npm global (`@wavespeed/cli`) | Search 986 WaveSpeed models by keyword; per-video pricing — needs `WAVESPEED_API_KEY` |

---

## Python Packages (System-Wide, pip3)

| Package | Version | What It Does |
|---------|---------|-------------|
| `cloudinary` | 1.44.2 | Upload images/video to Cloudinary CDN; returns public HTTPS URLs for AI API parameters |
| `Pillow` | 12.2.0 | Image processing — resize, pixel diff, frame comparison; used by scene detection scripts |

---

## How to Update This File

Whenever you:
1. Install a new skill (via `/skill-creator` or manually)
2. Enable a disabled plugin
3. Add a new MCP server to `.mcp.json` or `settings.json`
4. Install a global CLI tool
5. Create a new Python tool in `tools/`

**Immediately add it to the appropriate section above.** Keep sections organized by capability (what the tool does), not by tool type. Example structure:

```
## [Capability Name]

### [Tool/Service Name]
- **[Details]:** Description
- **API Key:** `KEY_NAME` (if applicable)
- **Usage:** Command or invocation pattern
- **When to use:** Guidance on when to prefer this tool
```

This is the single source of truth. If it's not here, agents won't know it exists.

- **`Character-Sheet-Generation/scripts/title_sheet.py`** (global, 2026-09-20) — adds the standard dark title bar (subject name) to a finished character/creature/prop sheet; wraps `build_reference_sheet.py`. Usage in `Character-Sheet-Generation/SKILL.md` → 'Sheet presentation template'.
- **`001_Architecture/Tools/Video-Generation/Generic_Tools/check_sheet_hands.py`** (global, 2026-09-20, v1) — deterministic left/right hand checker for generated sheets/storyboards. Finds each human hand (scans in overlapping tiles), reports LEFT/RIGHT + confidence + annotated overlay; `--mirror-test` flips the image and labels must swap. Runs MediaPipe's palm+hand ONNX models through OpenCV DNN (`Generic_Tools/models/`), NOT the mediapipe package (crashes on macOS). Foot filter (YOLO-pose ankles) drops toes read as hands. Scope + gate in `Generic_Tools/sheet_checker_config.json` (`global_for_human_characters` false = Neon_Parcel only; true = every pipeline; `pass_threshold` 0.8). `--expect HAND:x0,y0,x1,y1` runs the pass/fail gate. Since 2026-09-21: pose-seeded wrist crops raise recall (6->9 hands on the courier sheet) and `review_flags` mark low landmark confidence / extreme proportions (weak signals). Known limits: can still miss a hand, cannot count fingers or detect deformity, human hands only. Also downloaded for upcoming checks: `models/yolo11n-pose.pt`, Depth-Anything-V2-Small (HF cache).
- **`Generic_Tools/check_seedance_prompt_refs.py`** (global, 2026-09-20) — hard gate: every Seedance reference image must have an `@Image N = ...` mapping AND be used by tag as the subject of every timestamped action beat; storyboard/env tags referred to again in the body. Runs automatically inside `kie_market_api.generate_seedance_mini()` before any paid call (raises, no spend). Rule text: Seedance-Prompting-Guide → 'Use the tag as the subject in the action text'.
- **`001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/neon_seedance_call.py`** (Neon Parcel, 2026-09-20) — the only sanctioned way to make a Neon Parcel Seedance call: builds the reference list from the shot's `Data/Video_Reference_Set.json` (final labeled assets, fixed order), enforces the winning-formula prompt rules + `@Image` tag check, supports `--dry-run`. Template: `Neon_Parcel_Longform_Compilation_v2/Templates/Seedance_Winning_Prompt_Template_v7.md`.
- **`001_Architecture/Tools/Video-Generation/Generic_Tools/seedance2_call.py`** (GLOBAL, 2026-09-20) — gate + runner for EVERY Seedance 2 / 2 Fast / 2 Mini call in any channel: builds the reference list from the clip's `Data/Video_Reference_Set.json` (final labeled storyboard, environment sheet, character/prop sheets, fixed order), blocks the paid call if a sheet built for the clip is neither sent nor listed in `not_sent` with a reason, if the winning-template sections or `@Image` tagging are broken. Tested for Mini; standard/fast untested. `Channels/Neon_Parcel/neon_seedance_call.py` delegates to it. **Scale hard stop** (2026-09-26, Neon_Parcel): blocks unless `Data/Scale_Check_<storyboard>.json` passed on the same storyboard sha256. **`--keyframes`** (2026-09-26): keyframe fallback — sends the manifest's `keyframes` instead of the storyboard, filling slots keyframes > character sheets > environment sheet > props up to `--ref-limit` (default 9, Kie Mini).
- **`Generic_Tools/seedance2_gate_config.json`** (2026-09-20) — per-channel on/off switch for the Seedance 2 reference-image process (`seedance2_call.py --channel X`). Only Neon_Parcel is true now. Flip a channel to true to enforce it there.
- **`001_Architecture/Tools/Video-Generation/Generic_Tools/upscale_video.py`** (2026-09-21) — upscale to 1920x1080 with fallback: **fal Topaz (Proteus, 2x, `FAL_AI_API_KEY`, $0.02/s) default since 2026-09-23**, then Kie Topaz 2x up to 2 attempts (backup), then Magnific video upscaler (API, `MAGNIFIC_API_KEY`, 1k/natural/creativity 0, ~$0.007 per output frame), then FFmpeg normalize. Logs attempts, never overwrites, refuses Magnific if estimated cost > $5. Neon Parcel rule in the v2 skill ('Upscale fallback rule'). **Upscaler prices (Tool-Manager catalog, verified live 2026-09-26):** fal Topaz $0.01/s ≤720p, $0.02/s 720p–1080p, $0.08/s >1080p (pinned in catalog; fal's pricing API only reports the first tier); Kie Topaz $0.04/s 1x/2x, $0.07/s 4x; WaveSpeed ByteDance Video Upscaler $0.0072/s at 1080p (cheapest, untested on our footage); WaveSpeed SeedVR2 $0.04/s at 1080p (generative, 3 s minimum, untested). `tm recommend --type upscale` (2026-09-26) ranks upscalers: locked route default first, then models tested on our footage, then price; a task mentioning faces/Proteus/model choice keeps only routes that let you pick the Topaz model (fal). Magnific connector tools (`video_upscale`, etc.) also exist in the Claude connector; scripts use the API.
- **`001_Architecture/Tools/Video-Generation/Generic_Tools/check_depth.py`** (GLOBAL, 2026-09-21) — measured depth check with Depth Anything V2 Small (cached locally): relative depth per detected object (YOLO COCO classes) or `--box`, `--expect "A<B"` asserts A is closer than B, exit code 1 on failure. Tested on Storyboard_v3 frame 1: person 0.48 > bicycle 0.45 > counter 0.41 > wall 0.40, and a wrong expectation fails. Limits: relative depth from one image; no COCO class for monkeys (use --box).
- **`Character-Sheet-Generation/scripts/sheet_spec.py`** (GLOBAL, 2026-09-21) — JSON-spec-driven character/creature/prop sheet builder: fixed approved wording + per-subject fields, locked minimum panels + action extras, labeled references, holder reference required for held panels, saves prompt first, then title bar. Examples `Sheet_Spec_Example_*.json` in the skill folder.
- **`Environment-Sheet-Generation/scripts/build_environment_sheet.py`** (GLOBAL) — renders an environment sheet (dark presentation-board style) from a JSON spec: `python3 build_environment_sheet.py <spec.json> --base <production_folder> --out <sheet.png>`. Full example spec in the skill's `Examples/`.
- **`001_Architecture/Tools/Video-Generation/Generic_Tools/check_subject_positions.py`** (GLOBAL, 2026-09-18) — deterministic subject-position check across a storyboard grid (YOLO + pose); built after Neon Parcel Test Shot 03 position failures.
- **`001_Architecture/Tools/Video-Generation/Generic_Tools/check_landmark_positions.py`** (GLOBAL) — open-vocabulary landmark-position check across two images (does a landmark sit in the same place in both).
- **`001_Architecture/Tools/Video-Generation/Generic_Tools/inpaint_image_region.py`** (GLOBAL) — masked inpainting of one image region via OpenAI's direct `images.edit` (gpt-image-2); fixes a local defect without regenerating the whole image.
- **Model weights** for these checkers live once in `001_Architecture/Tools/Video-Generation/Generic_Tools/models/` (yolo11n, yolo11n-pose, mediapipe hand/pose) and `001_Architecture/Tools/Video-Generation/Generic_Tools/Subject-Aware-Reframer/Models/` (yolo11s, YOLOE + its text encoder). Scripts load them by full path; weights are gitignored (2026-09-27).
- **sheet_spec.py update (2026-09-21):** a prop spec with no held panel now appends 'no hand/arm/held-from-POV panels, object-only' to the prompt (the base prop prompt otherwise makes the model invent generic-hand panels). Found on Shot 06 motorcycle sheet v1.

## 21st.dev (UI components) — added 2026-09-27

- **CLI (preferred):** `npx @21st-dev/cli <command>` (search, get, add, theme, logo). Auth: `TWENTYFIRST_TOKEN` in `~/.env-secrets` (points at `TWENTY_FIRST_API_KEY`). Free tier: unlimited search, **2 component-code retrievals/day**, no 21st AI generation.
- **Skills** (`001_Architecture/Skills/`): `21st-cli-use` (search/pull components via CLI), `21st-ui-build`, `21st-ui-explore`, `21st-ui-review`. Not installed: `21st-ai` (not on free plan), `21st-registry`, `21st-design-sync` (publishing). The installer refuses the symlinked `~/.claude/skills`, so install into a scratch dir and copy.
- **MCP backup:** `magic` MCP (user scope) launches via zsh, sourcing `~/.env-secrets`; no key stored in `~/.claude.json`.
