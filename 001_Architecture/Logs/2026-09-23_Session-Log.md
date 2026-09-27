# Session Log — 2026-09-22 (evening) to 2026-09-23

- Session start: claude-mem outage surfaced ("inference allowance exhausted"). Added memory note `project_claude_mem_outage_2026-09.md`.
- Diagnosed claude-mem: provider=gemini but no key reached the worker (it reads keys only from `~/.claude-mem/.env` or settings.json), so it fell back to Claude via Tony's subscription OAuth. Fix: `~/.claude-mem/.env` → symlink to `~/.env-secrets`; `CLAUDE_MEM_GEMINI_MODEL` gemini-2.5-flash-lite (invalid) → gemini-flash-lite-latest; settings backup in `~/.claude-mem/backups/`. Verified Gemini sessions storing. Global_Agent_Memory corrected.
- Disk: 18 → ~46 GB free. Tony ran `npm cache clean --force` (7 GB), `docker image prune -a` (17.9 GB), `uv cache clean` (15.8 GB, after stopping the claude-mem worker that held the lock).
- Shot 07: Tony approved the fishmonger/walrus/van sheets, confirmed the subadult walrus, and specified the ice cascade; rejected env v1. Rewrote Blocking_Plan + Site_Plan v2 (harbour quay facing the bay; v1s kept as *_v1_Superseded.md); 6 Wikimedia harbour refs; Environment_Sheet_v2 (top-down v3 → reverse v3/v3b → POV v3 → landmark v3; PIL path arrow) approved.
- Two-clip plan: Clip 1 Kie Seedance 2 Mini (all refs), Clip 2 WaveSpeed Mini Video Extend (Tony accepted no sheets).
- Storyboard Clip 1 v1 (approved with notes) → video v1 FAILED (tiled grid). Storyboard v2 (scale/zoom/door fixes, controller attempt 2/3) approved → video v2 FAILED (sheet frame + garbled title) → salvaged by FFmpeg crop 746x418 (Tony option 1).
- Created `Data/Generation_Log.json` for Shot 07 (the guard blocked the first call without it; no spend).
- Clip 2 end frame v1 (zoomed, whole fish) → v2 matched. Extend v1 (with end frame, 6 s) FAILED: water appeared on the tarmac. Extend v2 (Tony's railing exit, no end frame, 8 s) PASSED; Gemini 0.95, no errors.
- Tony graded Shot 07 **B+**: beats good; scale 1.5-2x too large; the van isn't fully in its bay. Report_Card.md written; feedback + memory `feedback_neon_parcel_scale_to_environment.md`.
- Upscale: Magnific basic API failed ("1/2 chunks"). Via the Magnific MCP: Topaz Astra 2 (0.3/0.5/0.5), 5,580 credits; faces clean. Final fill-and-crop to 1920x1080 per Tony: `Shot07_Full_v2_1080p_FINAL_NoBars.mp4`. Tony: Magnific is a one-off, not in the pipeline.
- Researched upscaler prices (fal Topaz $0.02/s, Kie $0.04/s, WaveSpeed ByteDance $0.0072/s, SeedVR2 $0.04/s). Kie Topaz exposes only a scale factor.
- Tony: fal default, Kie backup. `upscale_video.py` updated (fal Topaz Proteus 2x first, audio remuxed from raw; backup at scratchpad). Tested on a 3 s clip (~$0.06): works; softer than Astra. Updated the Neon Parcel v2 skill, TOOLBOX, Global_Agent_Memory, project memory.
- Close-out: this log, self-review, handoff `Logs/Handoffs/2026-09-23_Session-Handoff_Claude.md`. Nothing committed to git.

## Codex Seedance clarification — 2026-09-23
- Updated Seedance guide with Tony-approved A–G; preserved legacy temporal-frame support and corrected conflicting Kie reference/frame instructions. Text verification and whitespace check completed. No provider calls or gate-code changes.
