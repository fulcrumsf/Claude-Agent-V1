
## 2026-09-05 PM — dead symlink cleanup

- The 3 dangling symlinks (Generic_Tools/new_video.py, providers/kie_video_gen.py,
  providers/video_stitcher.py) pointed at the gone pre-rename `Claude-Agent` path.
  Confirmed nothing imports them; only auto-gen System-Map.md flagged them.
- `git rm`'d all 3. Preserved real content in new folder
  `001_Architecture/Tools/Video-Generation/_Archive/Generic_Legacy_Toolkit/`
  (kie_video_gen.py + video_stitcher.py = untouched originals from AW channel copy;
  new_video.py = AW-evolved version, true generic is gone). Each file has an
  ARCHIVED header comment + `_ARCHIVE_NOTE.md`. All 3 py_compile clean.
- Not committed. Shot 11 v5 flag: Tony still editing in Codex — ignore for now.

## 2026-09-05 PM — session close

- Wrote `Logs/Handoffs/2026-09-05_PM_Session-Handoff_Claude.md` (supersedes the
  overnight one). MEMORY.md pointer repointed.
- Next-session plan agreed with Tony: graphify version check → build a de-dup script
  for 007_Resource_Library (duplicate bookmarks, esp YouTube re-watches) → re-tag
  pass → build Resource Library graph Tony's specific way → hand Wiki graph to Codex
  → THEN commit branch to GitHub as one checkpoint.
- 4 Codex questions: answer (b)(c) + record (d) after the current Neon Parcel video.
- Gemini video understanding in process_video_ingest.py: deferred until after Neon Parcel.
- Saved verbatim Codex response (Neon Parcel remaining workflow items: Seedance route
  inconsistency, end-to-end orchestrator, storyboard-gen provider wiring, fallback
  executor, review toggle, provider naming, integration tests, graphify mismatch) into
  handoff §2.D2. Tony told Codex he resumes pipeline wiring after the current video.

## 2026-09-05 PM — Resource Library frontmatter contract hardened (pre-graphify)

- Audited 007_Resource_Library: ~3,563 .md eligible. Tools 83% tagged but schema
  inconsistent (`tags:` vs `Tag:` vs `Category:` list), freeform capitalized tag
  values, github-repo detection only caught 32/94. 472 sub-400b Tools files = real
  clean bookmarks (keep), a few misfiled (Midjourney billing, Untitled-14).
- Established ONE canonical frontmatter contract in ingest/SKILL.md Step 2:
  `tags:` block-list is the only tag carrier; `type:` real value (never
  extracted-knowledge); new required `form:` field (github-repo|saas-tool|
  youtube-video|tiktok|channel-study|…) = "what the thing IS"; required `summary:`
  frontmatter field; `url:` required when visible; github mirror rule.
- Updated: ingest/SKILL.md (Step 2 + Step 4 image-note shape), Directory.md
  (GLOBAL FRONTMATTER CONTRACT block), process_image_ingest.py (vision prompt asks
  content_type/form/url; emits new schema; github guardrail; drops
  extracted-knowledge / "## AI Analysis" → "## Summary"). validate_build PASS.
- NOT done: no backlog re-tag of existing notes, no graphify (Tony wants graphify
  done a specific way, explaining later). check_vision_needed.py could later also
  flag notes missing form:/summary: for a re-tag pass.

## Graphify domain rebuilds + Conservation Mode handoff

- `.graphifyignore` / `.gitignore` fix: root `.graphifyignore` only had lowercase media
  extensions; graphify's fnmatch is case-sensitive on macOS so `.PNG` etc. slipped
  through (784 "image" files in 007_Resource_Library corpus). Rewrote both ignore
  files with case-insensitive bracket-class patterns + a broader extension list.
  `.gitignore` was already fine (core.ignorecase=true) — widened its list anyway.
  Added `OpenAI_History/` exclusion (accidental 2058-file ChatGPT export dump).
- Architecture domain graph: rebuilt clean (3253 nodes / 4354 edges / 578 communities),
  REGISTRY.md row updated to 2026-09-05T01:03Z. Flagged: 3 dangling symlinks to old
  Claude-Agent path (new_video.py, kie_video_gen.py, video_stitcher.py).
- Video Editor domain graph: hit Claude account rate limit ~4x across the night.
  Chunks 1,2,3 + AST + cache completed; chunks 0,4,5 outstanding.
- [HH:MM] ⚡ CONSERVATION MODE + HANDOFF → Codex | Reason: Claude account rate-limited
  repeatedly overnight | Task: finish Video Editor graphify build (3 chunks + assembly)
  | spec at scratchpad/codex_ve_graphify.md | Result: pending | Artifact: report to
  001_Architecture/Logs/Handoffs/2026-09-05_Video-Editor-Graphify_Codex-Completion.md
- Wiki + Resource Library domain graphs: still not built. Resource Library on hold
  pending Tony's redundancy/scoping conversation (3559 files even after exclusions).

## Neon Parcel Shot 12 storyboard revision

- Reviewed Shot 12 storyboard v1 against the v2 video failure. Confirmed Grandma's
  gate entrance, yard crossing, arrival at the trampoline steps, and climb were
  collapsed into one panel.
- Saved structured prompt v2 and generated two new storyboard candidates. Attempt 1
  had Grandma drift to the trampoline's right side instead of the visible steps and
  was preserved under `Working/Analysis/Shot-12-Storyboard-v2-Attempt-1/`.
- Attempt 2 passed agent visual inspection for wide 16:9 panels, one Grandma, three
  cubs, fixed camera geometry, visible gate origin, continuous route, bottom-of-steps
  checkpoint, and physical climb. Active file:
  `Images/Shot-12-Storyboard-v2.png`.
- Await Tony's storyboard approval. No Seedance prompt revision, paid generation,
  upscale, or video replacement has been started.

- Tony approved the climbing-step depiction as the better visual direction because
  Grandma's scale is natural. The standing-on-trampoline depiction is oversized
  and should not be used as the final storyboard state without correction.

## Neon Parcel Shot 12 v3 generation

- Generated `Working/Shot-12-Seedance-2-Mini-480p-v3.mp4` from the approved
  climbing-step storyboard and v3 Seedance prompt. Existing v2 artifacts were not
  overwritten.
- Contract/unit verification passed: 74 tests. Gemini's advisory inspection found
  no reported duplicate Grandma, but only clearly described approach/lean behavior.
- Human contact-sheet review indicates the lower-left step climb is not clearly
  realized; Grandma appears to approach the trampoline edge from the right. Raw v3
  failed the six-stage storyboard continuity requirement. No upscale or final render
  was run; v3 remains preserved for audit and comparison.

## Neon Parcel Shot 12 tiled-storyboard failure and hardening

- Direct frame inspection confirmed the v3 output reproduced the six storyboard
  panels as a 3-by-2 tiled layout inside the video, rather than generating one
  continuous shot. This is a provider/reference-role failure, not merely a missed
  action beat.
- Hardened the pre-video gate to block unverified composite storyboard-sheet
  references, updated the Seedance and Neon Parcel skills, and added a regression
  test. The approved route is now clean 16:9 temporal start/end anchors, with the
  storyboard retained for planning, prompt construction, and QA only.
- Verification: 75 tests passed. No new provider request was made.

## Seedance storyboard tag convention

- An initial generic tag convention was recorded as `@image_1`/`@image_2`, then
  superseded after the Kie playground example was checked. Kie's provider-specific
  convention is `@Image 1`/`@Image 2`, matching upload order.

## Validated Kie storyboard prompt pattern

- Tony manually confirmed Shot 12 v6 correctly interpreted the storyboard as one
  continuous shot with one camera angle rather than reproducing six panels.
- Promoted the validated pattern into `storyboard_handoff.py`: duration, shot
  count, and aspect ratio header; explicit Kie `@Image 1` upload-order mapping;
  `Shot 1, panel N` chronology; concise follow-the-storyboard instruction; and
  explicit prohibition on reproducing the sheet layout.
- Updated Storyboard, Seedance, and Neon Parcel skills and the handoff regression
  test. Verification: 75 tests passed.

## Universal visual-reference role binding

- Tony clarified that every uploaded image in a Seedance call must receive an
  explicit provider tag and role based on upload order: storyboard, character
  sheet, environment sheet, prop sheet, and any additional visual references.
- Extended `storyboard_handoff.py` to render all manifest `reference_order`
  entries as Kie `@Image N` declarations and fail on invalid upload ordering.
- Updated all three applicable skills and feedback guidance. Verification:
  75 tests passed.

## Graphify CLI version upgrade (evening)

- Version check found the active `graphify` on PATH was `graphifyy` 0.4.2 (Framework
  Python 3.13) — a stripped build with no `update`/`add`/`extract` subcommands. A
  second shadowed install (`/opt/homebrew/bin/graphify`, 0.4.23) had the full command
  set but lost the PATH race. PyPI latest was 0.9.55.
- Upgraded `graphifyy` 0.4.2 → 0.9.55 on Framework Python 3.13. Uninstalled the
  Homebrew 0.4.23 package and removed its orphaned wrapper — one `graphify` on PATH now.
- Refreshed skill copies to 0.9.55: `graphify install --platform claude` and
  `--platform codex`. `.graphify_version` marker now 0.9.55. Old skills backed up as
  `SKILL.md.bak` in each skill dir; new `references/` dir added by installer.
- Functional test: `graphify query` works against the existing Architecture graph.
  Note: Architecture + Video Editor graphs use the pre-#1504 node-ID scheme; a
  `graphify extract --force` rebuild would add path-qualified IDs (not urgent).
- Docs updated: REGISTRY.md new `## Tooling version` section; PM handoff §2.A.1 +
  §2.D(a) + §2.D2 marked resolved; Neon Parcel Codex handoff graphify bullet updated.
- Closes Codex open question (a) and the Codex "Graphify tooling mismatch" bullet.

## Resource Library dedup script built (evening)

- New reusable script `001_Architecture/Scripts/resource_library_dedup.py` — scans
  007_Resource_Library for likely duplicate bookmarks, writes a side-by-side review
  table (`007_Resource_Library/_Dedup_Review.md` + `.json`). Never deletes/moves.
- Match tiers: exact (same canonical URL / YouTube ID / identical body), high (same
  real domain + fuzzy title), medium (fuzzy body), low (shares a URL but looks
  unrelated, or one side is a link-list/index note).
- CLI options for reuse: --roots, --output, --format {md,json,both}, --min-title-sim,
  --min-body-sim, --include-images. Default scans 13 roots (excludes OpenAI_History,
  Obsidian_Attachments, graphify-out, Archive).
- First full run: 3550 notes → 18 clusters (8 exact, 3 medium, 7 low). Key false-
  positive sources handled: Notion icon SVGs, your-domain.com callbacks, Unsplash CDN
  links, claude.ai/code boilerplate, /search?q= query URLs, and old Notion-era
  link-list category notes colliding with atomic per-tool notes.
- validate_build PASS. Codex review pass dispatched (codex:codex-rescue) for a second
  opinion on the matching logic.
- NEXT: Tony reviews `_Dedup_Review.md`, decides merges/removals. Then re-tag pass, then graph build.

## Resource Library dedup — Codex review folded in

- Codex (codex:codex-rescue → task task-mtozyk2k-ttwzeu) reviewed the matching logic.
  One Medium finding + 5 low/latent. No edits by Codex.
- Medium finding acted on: bare-homepage URLs were rejected outright, missing real
  Tool re-bookmarks. Fix: homepage URLs from frontmatter `URL:`/`source:` are now a
  valid exact key when both notes are non-index. Recall jumped 18 → 26 clusters —
  8 more real Tool dupes surfaced (Mixamo/Mixamo-2, Open-Router/-2, Coderabbit/
  Code-Rabbit, Flowise-AI/-2, Freepik/-2, Gobii/-2, Scade-Pro/-2, Build-That-Idea/
  Buildthatidea).
- Also applied: scheme normalized to https (http/https now match); body-URL fallback
  deprioritizes discord/patreon/gumroad/social invite links; transitive-cluster
  reason picks the strongest touching match; body-pass length cutoff now derived
  from --min-body-sim instead of hardcoded 1.35.
- Final: 3550 notes → 26 clusters (16 exact, 3 medium, 7 low), ~16s. validate_build PASS.

## Resource Library dedup — full triage done, delete list ready

- Two more index-detection bugs found + fixed while reviewing: (1) homepage-rejection
  also suppressed link-list detection (Social-Media.md, an 8-link index, showed as
  exact); (2) the YouTube-ID pass had no index/sanity guard (Shorts-Workflow.md link
  list vs the Robonuggets tutorial). Both now downgrade to `low`. Final: 26 clusters
  (14 exact, 3 medium, 9 low).
- Read all 32 files in the 14 exact + 3 medium clusters. Verdict: 16 real dupes to
  delete, 2 "keep both" (Johnny-Harris vs VOX templates = different Drive links;
  Robonuggets vs Shorts-Workflow = tutorial vs link-list).
- Applied 4 lossless merges to KEEP files before deletion: Mixamo tags (3D, Video),
  Gobii tag (API), Scade-Pro description (no-code builder line), Flowise-AI description.
- Verified: none of the 16 deletion targets have inbound [[wikilinks]].
- Wrote `007_Resource_Library/_Dedup_Actions.md` — full keep/delete table + one-shot
  `rm` block for Tony to run (never-delete rule). `.graphifyignore` updated.
- PENDING: Tony runs the deletions, then re-run dedup to confirm, then re-tag pass.
## Shot 12 storyboard v3

- Created `Images/Shot-12-Storyboard-v3.png` with eight panels so the action now
  ends after Grandma reaches the trampoline and begins a small first bounce.
- Preserved the fixed camera, gate-to-steps route, three cubs, and natural scale;
  no video generation was run.

## Resource Library dedup — deletions executed

- Tony explicitly authorized + Claude ran the 16-file `rm` block (2026-09-05 PM).
- Re-ran dedup: 3534 notes, 10 clusters left = the 1 "keep-both" medium
  (Johnny-Harris/VOX templates) + 9 low (index-note collisions). Nothing actionable
  remains. Dedup pass COMPLETE.
- Git: 16 deletions + 4 keeper merges staged as working-tree changes on the branch.

## process_image_ingest.py hardened — anti-fabrication

- Live-tested Claude's own vision on 3 real TikTok screenshots with Tony. Lesson: the
  pass must RESEARCH (resolve repo/site → visit → pull context), and must NEVER
  fabricate a URL. Claude invented github.com/tundealao/claude-watch (wrong) + guessed
  wrong purpose; mesh3d.gallery worked because the domain was actually in-frame (just
  obfuscated as "mesh3d [.gallery]").
- Hardened `process_image_ingest.py` PROMPT + parse path: new `search_for:` field
  (web-search string when url unknown), `needs-enrichment` auto-tag, "## Enrichment
  needed" body section, code guardrail demoting malformed URLs to search hints.
  Rule: reconstruct visible/obfuscated URLs; never synthesize an unseen one; never
  state an unshown tool's purpose.
- Contract propagated: `001_Architecture/Skills/ingest/SKILL.md` (Step 2 fields +
  rules) and `007_Resource_Library/Directory.md`. validate_build PASS.

## Shot 12 v8 submitted

- Tony approved storyboard v4 and added a frame-5 continuity note: Grandma
  follows the visible curve toward the steps while still facing the camera,
  with only a slight counterclockwise turn.
- Updated `shot_12_storyboard_spec_v4.json`, created the v8 Seedance prompt and
  submission script, and verified 75 Neon Parcel tests pass.
- Submitted a new Kie/Seedance 2 Mini raw generation as v8, task
  `598a54640b1872a89e542efa537f8aa2`. It is awaiting provider completion;
  no upscale or overwrite is permitted before Tony's manual approval.

## Shot 12 v8 approved and upscale submitted

- Tony approved the raw Shot 12 v8 video.
- Recovered the already-submitted raw file without creating another Seedance
  task, then submitted its authorized 2x Topaz upscale as task
  `db84fab20ad9d9514aea10cf5fb762af`.
- Final 1080p output is not available yet; the recovery script now reuses the
  existing Topaz task ID if resumed, preventing duplicate upscale charges.

## Neon Parcel narration review cut

- Created `Scripts/Narration-v1.md` with 13 short Herbie narration beats and
  preserved the rule that original in-clip speech remains audible.
- Generated separate ElevenLabs MP3s with word-level timing in
  `Narration_Audio/v1`; total narration is 52.9 seconds.
- Added the missing shared TTS `config.py` loader so the existing utility reads
  `~/.env-secrets` without embedding credentials.
- Assembled all 12 selected final clips with original audio plus VO. The first
  render exposed a short audio-stream issue; corrected v3 pads the original
  audio and verifies video/audio both reach 129.7 seconds.
- Review cut:
  `Assembly/Versions/v3/Neon-Parcel-Grandma-And-Bear-Compilation-VO-Review-v3.mp4`.
  No music, branding, captions, or publishing steps were added.

## Neon Parcel narration sync correction

- Tony reported inaudible narration and original-audio sync drift in the first
  review cut.
- Root cause confirmed: selected clips mix missing audio streams with 32 kHz
  AAC streams of different durations; stream-copy concatenation was unsafe.
- Created a timestamp-safe v4 assembly that filter-concats every clip, inserts
  silence for clips without audio, resamples original audio to 48 kHz, and
  mixes the 13 VO lines directly without the faulty sidechain path.
- Verified v4 picture and audio both run 129.768 seconds at 1920x1080/48 kHz.

## Neon Parcel audio workflow hardened

- Hardened the successful narration approach into the Neon Parcel skill,
  Toolbox, report card, feedback loop, and Global Agent Memory.
- Locked Herbie (`Kz0DA4tCctbPjLay2QT1`), separate shot-aligned VO lines,
  original audio preservation, 48 kHz timestamp-safe assembly, review mix
  defaults of `0.55` source audio and `1.6` narration, and no music/branding
  before narration review.
- Added the shared TTS `config.py` secret loader and verified it loads from
  `~/.env-secrets` without exposing credentials.
- Verification: Neon Parcel suite remains 75/75 passing and `git diff --check`
  is clean. Remaining production work is final music/branding/package review,
  not pipeline hardening.

## Neon Parcel music and end-screen review master

- Tony selected CTA option 2: “Subscribe to Neon Parcel. You never know what
  is next.” Generated with Herbie at 3.6 seconds, inside the seven-second end
  screen.
- Generated and preserved both Suno instrumental variants using the approved
  quirky, whimsical, family-friendly home-video prompt; the longest variant
  was used for the review master.
- Appended the verified horizontal end screen and mixed music under the
  narration/original audio using the hardened 48 kHz workflow.
- Review master:
  `Assembly/Versions/v5/Neon-Parcel-Grandma-And-Bear-Compilation-Music-Endscreen-Review-v1.mp4`.
  Duration is 136.775 seconds; video and audio endpoints match.
- Status: awaiting Tony's review of music, CTA, and end-screen presentation;
  no publishing or Shorts generation performed.

## Neon Parcel compilation status and package phase

- Tony approved the music/end-screen review master and graded the compilation
  **B**.
- Tony set the Neon Parcel Compilation pipeline at **65% autonomy-ready**, with
  a **95%** threshold for mostly autonomous scheduled operation.
- Updated the production manifest, checkpoint state, report card, Neon Parcel
  skill, feedback loop, and shared memory. Current status is
  `package_creation_pending`; publishing remains blocked.
- Confirmed the existing skills: `title-hook-generator` covers title options
  and descriptions; `youtube-thumbnail-design` covers thumbnail creation and
  validation. Both should be used with the Neon Parcel pipeline skill.

## Resource Library graph build — Option A ran, result weak

- `graphify extract .` via Gemini: 3,548 docs, $1.46, ~15 min. OpenAI_History + media
  correctly excluded.
- Result: 1,066 nodes / 293 edges / 778 communities (49 real + 729 thin orphans).
- **75% of files (2,653/3,549) produced zero nodes** — thin bookmark notes + image
  stubs have no extractable structure. Confirms the corpus, not the tool, is the
  ceiling. The ~900 content-rich notes cluster fine (queried digital-products and
  Claude-tooling — both returned coherent results w/ real edges).
- Node-ID collisions logged (Higgsfield AI, Seedance 2.0, Claude Code minted by
  multiple files → losers dropped). graphify recommends per-subfolder extract + merge.
- REGISTRY.md updated with the honest build note. graphify-out/ gitignored (not committed).
- DECISION PENDING: keep as v1 + enrich later, or invest now in per-subfolder rebuild /
  frontmatter enrichment pass.

## Neon Parcel thumbnail tutorial case study

- Ingested only `How To Make Viral Thumbnails (99% Do This Wrong).md` from
  `000_Ingest/`, routing it to `007_Resource_Library/Tutorials/` with the
  visible YouTube URL `https://www.youtube.com/watch?v=jOcztYdF0fc`.
- YouTube media downloads returned 403s for available streams, so the public URL
  was analyzed directly through Gemini's supported YouTube input path rather
  than using cookies or repeated failed downloads.
- Upgraded the installed `google-genai` SDK from 1.68.0 to 2.22.0 because the
  current Interactions API rejected the legacy schema. Gemini 3.8 Flash agentic
  analysis completed with processing trace confirmation.
- Saved the raw analysis and a Neon Parcel case study under
  `002_Content-Creation/Video_Editor/002_Channels/002_Neon-Parcel/Case_Studies/How-To-Make-Viral-Thumbnails-99-Do-This-Wrong/`.
- The report recommends additive thumbnail-architecture planning, modular asset
  decisions, one-change refinements, text/safe-zone planning, and mobile-size
  validation. The existing thumbnail skill was not changed pending Tony's
  approval of these recommendations.

## YouTube thumbnail skill optional add-on

- Added an optional `Architecture-First Thumbnail Pass` to
  `001_Architecture/Skills/youtube-thumbnail-design/SKILL.md` without changing
  existing Quick Start, pattern, checklist, safe-zone, or A/B-test logic.
- The add-on requires a one-sentence visual promise, focal hierarchy brief,
  modular-asset decision, one-variable refinement passes, non-destructive
  versioning, and mobile/safe-zone validation.
- It explicitly treats CTR/virality as a testable hypothesis, not a guarantee.

## Compilation thumbnail architecture examples

- Applied the optional Architecture-First Thumbnail Pass to the approved
  `0001_Grandma-And-Bear-Compilation` production.
- Saved three non-paid, non-destructive thumbnail architecture examples and
  complete image prompts in the production `Package/` folder: Direct Faceoff,
  Unexpected Pattern, and Caught-On-Camera Reaction.
- No image-generation credits were spent. Next decision is Tony's selection of
  an option for an actual thumbnail generation pass.

## Thumbnail candidates and metadata

- Generated three separate GPT Image 2 candidates through the established
  `kie.ai` route after correcting the live model ID mismatch.
- Preserved the 3840x2160 PNG source renders and created separate 1280x720 JPEG
  delivery files for YouTube; no existing asset was overwritten.
- Saved three title options and one shared description in the production
  package. Metadata remains draft pending Tony's selection and final review.

## Video-Analyzer agentic routing hardening

- Updated `001_Architecture/Skills/Video-Analyzer/` to default to Gemini 3.8
  Flash and explicitly select agentic or static processing by analysis category.
- Added routing categories: case-study, tutorial, continuity, physics,
  screen-text, and hybrid. Continuity/physics routes automatically request
  dense 0.5-second keyframes for frame-sensitive QA, including limb deformation,
  morphing, duplicate subjects, broken connections, and impossible causality.
- Agentic calls now use the Gemini Interactions API and record whether the
  response contains processing trace steps. Updated tests and documentation.
- Verification: Python compilation and route assertions pass; full pytest could
  not run because `pytest` is not installed in the active Python environment.

## Evening 2 — claude-mem → Gemini + Resource Library stub enrichment

### claude-mem observer moved off Claude
- Was `CLAUDE_MEM_PROVIDER=claude` (model claude-sonnet-4-6, CLI subscription auth) —
  the memory worker was burning the same Claude usage allowance as interactive
  sessions; that allowance hit its cap 2026-09-05T17:47Z ("inference allowance
  exhausted").
- Switched to `gemini` (`gemini-2.5-flash-lite`), tier-routing disabled so nothing
  falls back to haiku. Confirmed live: worker log `Generator auto-starting ... using Gemini`.
- Key handling: Gemini key NOT copied into settings.json. Added alias
  `export CLAUDE_MEM_GEMINI_API_KEY="$GEMINI_API_KEY"` at `~/.env-secrets:225`;
  settings.json field left "". (Correction logged — Claude first wrote the literal
  key into settings.json, Tony flagged it as a security risk, remediated.)
- `npx claude-mem install --provider gemini` non-interactively opens a cmem.ai
  login page — don't use it; plain `worker restart` picks up settings.json fine.

### Resource Library stub enrichment (graph-day batch A, part 1)
- Goal: fatten the ~2,000 near-empty notes that made the RL graph weak, before rebuild.
- New scripts in `001_Architecture/Scripts/`:
  - `resource_library_stub_triage.py` — classifies stubs → `_Stub_Triage.json`/`.md`.
    Buckets: bucket1_revision (has screenshot), bucket2_url_enrich (has URL),
    bucket3_dead (garbled/missing-image/no-signal).
  - `revision_stub_notes.py` — re-runs hardened vision prompt on bucket-1 images,
    rewrites the note IN PLACE (filename/embed preserved), sets form/summary/url/
    search_for/tags + `enriched:` marker (resumable). `--shard I/N` for parallelism.
  - `enrich_url_stub_notes.py` — Gemini (google_search grounding) visits bucket-2
    URLs, writes summary/form/verified. `--shard I/N`.
  - `apply_dead_stub_graphignore.py` — writes bucket-3 paths into root
    `.graphifyignore` between AUTO markers (idempotent). NOT YET APPLIED.
- Triage counts (2026-09-05): 362 revision / 558 url-enrich / 1028 dead.
- `process_image_ingest.py` — added certifi SSL_CERT_FILE guard (macOS framework
  Python had no CA bundle → urllib SSL failures).
- Backup of all 939 mutated notes: scratchpad `stub_notes_backup_pre_enrich.tar.gz`.
  007_Resource_Library is git-tracked (5571 files) so git is the other safety net.
- Runs launched in parallel (12 revision shards + 5 enrich shards). PENDING at
  handoff: wait for completion → re-run triage → apply_dead_stub_graphignore →
  `graphify extract --force` rebuild → spot-check.

### RL graph rebuild — v2 (crossed into 2026-09-06)
- Whole-corpus `graphify extract --force` after enrichment: STILL 1684/2507 files
  produced zero nodes (67%) — Gemini omits files from large chunk responses. New graph
  978 < old 1066 → graphify shrink-guard refused the overwrite (v1 preserved).
- Diagnosis: the omission is a chunk-size problem, not (only) a corpus problem.
  Docs test folder with `--token-budget 18000`: 67% → 8% omitted.
- Fix applied: `scratchpad/rl_per_subfolder.sh` — per-subfolder
  `graphify extract --force --token-budget 16000` on all 13 subfolders →
  `graphify merge-graphs` → `cluster-only` → `label`.
- Result: **3036 nodes / 1182 edges / 1897 communities**, ~$2.40 Gemini. v1 was 1066/293.
  Sub-graphs live at `007_Resource_Library/<subfolder>/graphify-out/`.
- Big folders still lose ~24% (Tools 275/1143, Research 111/554, Prompts 54/227) — a
  `--token-budget 8000` re-run on just those 3 would recover most. Logged in REGISTRY note.
- Test queries ("AI video generation tools", "n8n automation") return relevant,
  well-clustered results.
- REGISTRY.md row + build note updated to v2.

### RL graph v2.1 — big-folder re-extract at token-budget 8000
- Prompts test: budget 16000→8000 cut omission 24%→3%, nodes 219→339. Applied to Research + Tools.
- Research: 523→700 nodes (omit 20%→7%). Tools: 1334→1687 (omit 24%→12%). +$1.90 Gemini.
- Re-merged 13 subgraphs → cluster → label: **3686 nodes / 1622 edges / 2146 communities (392 labeled)**.
- `scratchpad/rl_bigfolders.sh`. REGISTRY v2.1 note added with the token-budget rule.
- Queries verified (POD/etsy, AI video, n8n) — relevant + well-clustered.

### Wiki + Affiliate Marketing graphs built (2026-09-06)
- 000_Wiki: 125 docs → 345 nodes / 89 edges / 261 communities (3 omitted, all README). $0.24.
- 005_Affiliate_Marketing: 36 docs → 202 nodes / 162 edges / 50 communities (0 omitted). $0.34.
  Content = TikTok Shop TOS/compliance corpus + Neon Parcel TikTok Shop Creator pipeline.
- Both via `graphify extract --force --token-budget 8000` + cluster + label. REGISTRY rows updated.
- Queries verified.

### Note review pass — closed (2026-09-07)
- Built note_review.py (renamed from build_stub_review): copies un-enriched notes +
  images to ~/Desktop/Resource_Library_Review/ with a Keep/Junk HTML page.
- Triage bug fixed: notes with `enriched:` marker no longer re-flagged (108→13 real).
- Tony reviewed: 3 junked (deleted via ~/Desktop/Delete), 13 kept as-is — enrichment
  on these is CLOSED, not revisiting. Future: richer visual review/edit tool (deferred).
