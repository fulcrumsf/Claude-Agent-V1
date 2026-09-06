
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
