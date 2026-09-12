# 2026-09-09 Session Log

## Deferred channel-integration handoff

- Tony requested a durable handoff so a future “plug this Shorts workflow into
  [channel]” request can resume without repeating the history. No integration
  should happen today.
- Wrote `Future-Channel-Integration-Handoff-v1.md` in the shared reframer directory,
  covering current capability, remaining automatic clipping/controller work,
  per-channel profiles, pilot/approval steps, technical limits, and artifact links.
- Added discovery pointers to README, TOOLBOX, Memory Index, and shared memory.
  Only handoff/documentation records changed; no rendering, installation,
  channel activation, automation, or Airtable changes were performed.

## Part Three framing selection

- Tony preferred Hybrid (third comparison variant) for this video specifically.
  Saved `Gate-3-Review-Decision-v1.json` beside the production review, and recorded
  the scoped preference in feedback/shared memory. No rerender, global default
  change, connector activation, or later-stage execution was performed.

## Subject-aware reframer — Gate 3 implementation

- Tony approved the expanded Gate 3 scope: a global engine with programmable group,
  subject, and hybrid modes, saved profiles, per-video settings, and shot overrides.
  Future automatic clipping, optional intake questions, and Airtable control are
  architectural context; they are not implemented or activated in this gate.
- Added `camera_plan.py`, `reframe.py`, `render_reframe.py`,
  `Framing-Profiles-v1.json`, `test_camera_plan.py`, and `Job-Contract-v1.md` under
  the existing shared tool. Extended the offline launcher. No dependencies added.
- Created `Part-3-Framing-Job-v1.json` and two versioned render runs under the
  production's `Shorts/Versions/v3/Auto-Reframe/`. Current candidate:
  `Gate-3-Run-002/`, containing three 1080x1920 videos, comparison/debug videos,
  contact sheet, crop-plan JSON, and verified report.
- Initial review found brief crop returns and an ending-group interruption.
  Fixed hold behavior and added regression tests. First run preserved under the
  experiment's `Archived/Gate-3-Run-001/`, with an archive hash receipt.
- All 24 behavioral tests passed. All five current videos passed full decode,
  codec/timing checks and matching hashes; independent crop coverage, bounds,
  pan/zoom limit, source integrity and resource checks passed. Render plus media
  verification took 32.4 seconds. About 2.1 GiB allocated, 19.8 GiB free.
- Saved `Gate-3-Review-v1.md`, `Gate-3-Test-Results-v1.txt`, and
  `Gate-3-Verification-v1.json`. Updated shared memory, feedback, TOOLBOX, Workspace
  Map, Architecture Directory, and tool documentation. Tony's playback review
  remains pending. Master and prior Shorts are untouched.
- Final Agent-OS build validation passed for all 15 selected code, configuration,
  and handoff artifacts; saved `Gate-3-Build-Validation-v1.txt`.

## Neon Parcel subject-aware reframer — resumed Gate 2

- Session began September 8 and resumed September 9. Tony requested interview →
  plan → explicit approval → execution. Planning and Gate 1 changed no workspace
  files or installed dependencies. Tony explicitly approved Gate 2 and 42 package pins.
- Confirmed M3 Max, 36 GB RAM, Python 3.11.12, FFmpeg 8.1.1. Part Three source is
  97.500–129.750 s: 771 actual frames with irregular timestamps; cuts at 107.583333
  and 117.666667 s. The prior v2 Short starts video about 33 ms after its audio.
- Created `001_Architecture/Tools/Video-Generation/Generic_Tools/Subject-Aware-Reframer/`
  with isolated `.venv`, `.cache`, hash-locked requirements, dependency provenance,
  official YOLO11s weights/receipt, offline launcher, diagnostic CLI, and tests.
  No global package changes. Installed environment and caches total about 1.9 GiB.
- Dependency consistency and six unit tests passed. CPU and MPS each loaded the
  model with restricted loading under OS network denial and ran one-frame inference.
- Full CPU baseline produced `Shorts/Versions/v3/Auto-Reframe/Run-001/` with raw
  detections/tracks, debug video, contact sheet, timing map, and run report. It took
  60.8 seconds for detection and 71.7 seconds including diagnostics; peak process
  RSS was 678 MB. Debug video is 1280x800, 968 frames at 30 fps, about 32.266 seconds,
  with 48 kHz stereo audio. Both streams start at zero; full decode passed.
- Hash checks confirm the master, approved Parts One/Two, and both prior Part Three
  candidates are unchanged. No camera planner or vertical render was built.
- Initial visual review: Grandma tracking generally works; doorway bear missed
  throughout Shot 10. Hose interaction is substantially detected. Trampoline
  tracks exhibit four person/bear class transitions and late missed bears.
- All-class audit on 15 source frames identified species confusion: the porch
  animal is consistently classified as dog; some trampoline bears as dog/cat.
  Ran a second diagnostic using all COCO animal classes and separate person/animal
  trackers, retaining original species labels and the baseline for comparison.
- `Run-002/` completed in 71.2 seconds, peak RSS 661 MB. The porch animal appears
  in all 241 raw frames and 238 confirmed tracks; trampoline animals in all 289
  raw frames and 286 confirmed tracks. These are presence counts, not accuracy.
  Three-animal tracking covers 243 trampoline frames; brief duplicates, missed
  detections, ID fragmentation, and occlusion remain.
- Eight unit tests and independent Run-002 timing, full decode, family separation,
  source preservation, and resource checks passed. Created
  `Gate-2-Verification-v1.json`, review handoff, and updated tool README.
  Resource check: 1.96 GiB allocated, 20.48 GiB free. Tony's playback review is
  pending; no Gate 3 approval or vertical reframe is implied by these diagnostics.
- Experimental inventory entries added to TOOLBOX, Workspace Map, and Architecture
  Directory. Full auto-generated System Map refresh/pipeline adoption remains
  deferred to the global-adoption gate; it was not manually rewritten.
- Agent-OS build validation passed for all 16 selected functional/configuration
  artifacts; report retained as `Auto-Reframe/Build-Validation-v1.txt`. Gate 2
  handoff is ready, with camera planning and the vertical candidate awaiting
  Tony's explicit Gate 3 approval.

---

## Resource Library overhaul (Claude, Sep 8–9, separate thread from the reframer above)

### claude-mem → Gemini
- Observer was on `claude` (sonnet-4-6, CLI subscription auth) — burning the same Claude
  usage allowance as interactive sessions; it hit its cap. Switched
  `CLAUDE_MEM_PROVIDER=gemini` (`gemini-2.5-flash-lite`), tier-routing off. Key stays ONLY
  in `~/.env-secrets` (alias `export CLAUDE_MEM_GEMINI_API_KEY="$GEMINI_API_KEY"` at line 225);
  settings.json key field left "". Confirmed live: worker log `using Gemini`.

### Graphs built
- Resource Library v1 (weak, 1066n) → **v2.1: 3,686 nodes / 1,622 edges**. Method: enriched
  ~890 thin notes in place, excluded ~1,046 dead ones, per-subfolder `graphify extract
  --force --token-budget 8000` + merge-graphs (small budget was the fix — 60k default makes
  Gemini drop 2/3 of files). ~$4.80 Gemini total.
- Built: **000_Wiki** (345n), **005_Affiliate_Marketing** (202n), **003_Apps** (263n),
  004_Games/005_Ecommerce/000_Daily/Whop/Social (stubs). Only 000_Project-Ideas unbuilt (empty).

### Autonomy report cards
- `Autonomy_Report_Card/Autonomy_Report_Card.md` in all 13 channel folders. Anomalous Wild
  ~90%, Neon Parcel ~65%, Reimagined Realms 10% (provisional — needs real assessment), rest placeholder.

### Resource Library cull (all moved to ~/Desktop/Delete/, NOT deleted — Tony holding)
- ~590 stray/broken/dead notes + 1,044 graph-excluded notes + 8,109 images + 12 video clips
  + 928 MB ChatGPT export backup. RL went **8.2 GB → ~2 GB**. ~11 GB staged in ~/Desktop/Delete/.
- New review tools: `resource_library_stub_triage.py`, `revision_stub_notes.py`,
  `enrich_url_stub_notes.py`, `apply_dead_stub_graphignore.py`, `note_review.py`,
  `note_review_excluded.py`, `build_broken_image_review.py`, `build_image_cull.py` + `apply_image_cull.py`.

### Image co-location (architectural change — brainstormed then built)
- **Decision:** images live BESIDE their note in the category folder, same name stem
  (`Tools/OpenCode.md` + `Tools/OpenCode.png`). Flat, no subfolders. Root cause of years of
  link drift = two files linked by a fragile filename string edited by different processes.
- `migrate_images_to_notes.py` (one-time): moved 1,028 images out of `Visual_Assets/` into
  category folders, renamed to match, normalized ext case, updated 1,029 embeds. Verified 0 broken.
  14 notes tagged `shared-image-review` (dedup candidates).
- `process_image_ingest.py` rewritten: writes note + image together; dedup on ingest —
  (1) skip byte-identical image, (2) skip if `url:` already in another note, (3) title clash
  → `-N` + `possible-duplicate` tag. Rename log → `_Ingest_Rename_Log.md`. Tested OK.
- **Deleted by Tony:** `007_Resource_Library/Obsidian_Attachments/` (whole folder — Visual_Assets retired).
- Docs updated: AGENTS.md, ingest SKILL.md, Directory.md, Global_Agent_Memory.md, Workspace-Map, TOOLBOX.
- **5 scripts archived** to `001_Architecture/Scripts/_Archive/` (README there): reroute_visual_assets,
  fix_image_case, update_asset_notes_vision, fix_embeds, rename_screenshots. AGENTS.md ingest
  step repointed to process_image_ingest.py. `process_notion_edit.py` stays (deprecated, 60%).

### Commits pushed this thread
9affa3d, 2b6763c, 687d426, bb27e13, b204193, e47c560, f8d3914 (+ earlier RL-enrichment tag session).

---

## Resource Library Visualizer — designed + built + shipped (Claude, Sep 9 evening)

Full brainstorm → spec → plan → build → merge in one session. Tony's "Lightroom for
screenshots" for reviewing/culling `007_Resource_Library`.

- **Brainstormed** free-form (per his stated preference) — landed on: browser gallery,
  Notion-style cards (image + title + summary + folder pill + 2 tag pills + colored source
  label), default view = image/YouTube notes newest-first, text-only notes behind a toggle as
  color-coded `.md` glyphs. Filters: folder / source-type / top-8 tags / search. Detail view =
  note rendered Obsidian-style. Actions: bulk Delete (→ `~/Desktop/delete/`, card vanishes) +
  Re-run AI; per-card Edit (rewrites the `.md`), Re-run AI, Add Comment. Comments +
  edit-requests → `~/Desktop/Resource_Library_Review/Review_Queue.md`, "Finalize Queue" seals
  a batch for the agent.
- **Spec:** `001_Architecture/Superpowers/Specs/2026-09-09-Resource-Library-Visualizer-Design.md`
- **Plan:** `...-Implementation-Plan.md` (11 tasks, TDD, executed inline)
- **Tool:** `001_Architecture/Tools/Resource-Library-Visualizer/` — `config/detect/notes/thumbs/render/queue/actions/serve.py` + `App.html` + README. Flask, PyYAML, Pillow, markdown-it-py. 39 pytest tests (`tests/resource_library_visualizer/`).
- **Run:** `python3 001_Architecture/Tools/Resource-Library-Visualizer/serve.py` → `localhost:8756` (cold start ~12s, indexes ~4,000 notes; 1,160 gallery cards).
- **Bug caught mid-build:** modules were loading as separate instances → an early test run
  wrote junk to the REAL `~/Desktop/Resource_Library_Review/Review_Queue.md`. Fixed with a
  `sys.modules`-cached loader; deleted the junk file; confirmed no real notes were ever moved.
- **Tony approved** the running version ("exactly what I want"), did not review code.
- **Merged to main + pushed:** `dfb5ed8` (squash-free `--no-ff` merge of 12 commits). Branch deleted.
- TOOLBOX.md + `007_Resource_Library/Directory.md` updated.

### Deferred (in handoff)
- No on-disk index cache → ~12s cold start. Fine for now; cache keyed by dir mtime is the fix.
- Source-type labels heuristic (~90%): `Bookmark` detection is weak (needs `http` `source:` +
  image); most image notes fall back to `Screenshot`. Refine after Tony uses it.
- `Re-run AI` calls `process_image_ingest.process_image()` — needs `OPENROUTER_API_KEY`. Untested live (costs money).
