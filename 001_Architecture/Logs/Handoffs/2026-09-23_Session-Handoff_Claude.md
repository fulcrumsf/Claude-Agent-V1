---
title: "Session Handoff — 2026-09-23 (Claude Code)"
type: handoff
category: session
created: 2026-09-23
updated: 2026-09-23
---

# Session Handoff — READ THIS FIRST next session

**Next session's agenda (Tony):** probably NOT another Neon Parcel video. Topic TBD, but it will be about the **video pipeline, saving money, or optimizing the system**. Ask Tony which; the ready-made candidates are in §4 below.

This session covered 2026-09-22 evening to 2026-09-23. Session log: `001_Architecture/Logs/2026-09-23_Session-Log.md`. Feedback: `001_Architecture/Feedback_Loop/2026-09-23_Feedback.md`. Self-review: `001_Architecture/Self_Learning_Loop/2026-09-23_Self-Review.md`.

---

## 1. Done this session (no action needed)

- **Neon Parcel Shot 07 (walrus in the fishmonger's van, Scottish harbour) is FINISHED. Grade B+, final, no more spend.** Final file: `002_Content-Creation/Video_Editor/002_Channels/002_Neon-Parcel/Productions/0002_Delivery-Wildlife-Encounters-Compilation/Shot-07-Walrus-Fishmonger-Truck-GB/Data/Shot07_Full_v2_1080p_FINAL_NoBars.mp4` (1920x1080, 23 s). The full story is in that shot's `Data/Report_Card.md`. The gap to an A is **scale**: the van, characters and walrus render 1.5-2x too large vs the environment, and the van didn't fully enter its bay.
- **claude-mem fixed:** it had been silently billing Tony's **Claude plan** (the Gemini key never reached it). Fix: `~/.claude-mem/.env` is a **symlink to `~/.env-secrets`**; model set to `gemini-flash-lite-latest`. Verified running on Gemini. **Never put an `ANTHROPIC_API_KEY` in `~/.env-secrets`**, or claude-mem will bill it. Details: memory `project_claude_mem_outage_2026-09.md`.
- **Disk cleanup:** 18 GB → about 46 GB free (npm cache 7 GB, Docker images 18 GB, uv cache 16 GB). Tony ran the deletions himself. Still available if needed: iCloud Drive keeps 289 GB locally ("Optimize Mac Storage" would free most of it). Don't touch Exodus (a crypto wallet, 33 GB).
- **Upscale default changed (Tony):** `Generic_Tools/upscale_video.py` now runs **fal Topaz (model Proteus, 2x, `FAL_AI_API_KEY`) first, then Kie Topaz (backup), then Magnific basic (last resort), then FFmpeg 1920x1080**, and remuxes the audio from the raw clip. Tested on a 3 s clip: works, no face morphing, but softer than Magnific's Topaz Astra 2. The Neon Parcel skill, TOOLBOX and Global_Agent_Memory are updated.
- **Magnific stays a one-off.** Shot 07 was upscaled via the Magnific MCP (Topaz Astra 2, creativity 0.3 / realism 0.5 / sharp 0.5, 5,580 credits) by Tony's choice. **Do NOT write Magnific or Astra into any pipeline** (Tony: saving Magnific credits; he'll decide later).

## 2. ⚠️ Nothing committed to git

About 66 changed paths are uncommitted (`git status --short`), covering the last several sessions: Shots 06 + 07 production folders, the new global tools (`sheet_spec.py`, `check_depth.py`, `upscale_video.py`, `seedance2_call.py`, `title_sheet.py`, `check_sheet_hands.py` changes), and skill/doc edits. **Tony decides when to commit.** Don't commit unprompted. Never commit video/media (gitignored, per the standing rule).

## 3. Open items carried forward (lower priority)

- **Anomalous Wild bug (unfixed):** `pipeline_supervisor.py`'s `generate_seedance()` is hard-coded to Seedance 1.5 Pro and silently ignores the documented "Seedance 2.0 manual override".
- **Global Character-Sheet-Generation skill** still says "prop sheet first" for shared wardrobe; Neon Parcel's Prop Routing rule is narrower. Don't align without Tony's OK.
- **Reimagined Realms:** the storyboard/reference-image process for long-form is deferred until tested (channel disabled in `seedance2_gate_config.json`).
- **`000_Ingest/` backlog:** 456 screenshots + 18 bookmarks untouched.
- **magic MCP** (21st.dev) failed to connect: API key missing/reset. **cloudflare-api MCP** needs auth. Both are Tony's to fix.

## 4. Ready-made agenda candidates for "video pipeline / saving money / optimizing"

1. **Upscaler shoot-out (cheap, under $1):** run a 3 s face clip through fal Topaz on other models (Starlight Fast 2, Starlight Precise 2.5; generative, closer to Astra but more morph risk), WaveSpeed ByteDance Video Upscaler ($0.0072/s, the cheapest found), WaveSpeed SeedVR2 ($0.04/s). Tony picks by eye → maybe a new default. Prices checked 2026-09-23: fal Topaz $0.02/s (≤1080p), Kie Topaz $0.04/s (catalog, 2026-09-01; not re-confirmed live), Magnific ≈ credits.
2. **Storyboard → Seedance layout reproduction:** 2 of 2 Clip 1 runs on Shot 07 copied layouts (a tiled grid, then a sheet frame with a garbled title bar) even though Shots 05/06 passed. Worth diagnosing to cut wasted video spend: prompt drift from the v7 template, 15 s vs 14 s, or the look of the sheets themselves. A cheap mitigation is already proven: **crop salvage** when the scene sits inside a clean 16:9 area.
3. **Scale-control for Neon Parcel:** the B+ → A gap. Anchor sizes to fixed objects in frame and check scale on the storyboard before video spend (memory: `feedback_neon_parcel_scale_to_environment.md`).
4. **WaveSpeed Seedance 2.0 Mini Video Extend** is now a proven tool for >15 s shots (Clip 1 + extend, clean join). Lessons: **no end frame** worked; an end frame showing a distant state got pulled onto the foreground (water appeared on the tarmac). The WaveSpeed CLI upload aborts at ~10 s for multi-MB files, so host the inputs on Cloudinary instead. Not yet written into the Neon Parcel skill as a formal step; ask Tony before doing so.
5. **Kie Topaz has no settings** (only 1x/2x/4x): that's why its faces go soft/warped. That's now moot for the default route, but worth knowing.
6. **Tool-Manager catalog refresh:** add fal Topaz and the WaveSpeed upscalers with prices (the catalog's `topaz-video-upscale` entry has `fal_ai: null`).

## 5. Rules reaffirmed this session (see Feedback 2026-09-23)
- Tony's one-off overrides (Magnific upscale, sheets left out of the extend call) are NOT rule changes.
- For dictated concepts, restate the camera direction and what's behind the subject before building a site plan (the Shot 07 env v1 misread).
- Keep the v7 Seedance template's `@Image 1` line and "every panel of @Image 1" wording verbatim.
