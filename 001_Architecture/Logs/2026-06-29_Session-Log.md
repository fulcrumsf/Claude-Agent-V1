# Session Log — 2026-06-29

## Summary
Pompeii video pipeline deep-dive. Found and fixed the root cause of wrong clip durations. Updated batch generation script with permanent logic. 16 clips queued for regeneration next session.

---

## What Happened

### Airtable API Fix (catalog_refresh.py)
- Root cause of 1,518 June API calls: `catalog_refresh.py` made 2 calls per record (GET + PATCH) × ~40-45 debug runs during June 19-21 build sessions
- Fixed: switched to batch upsert (10 records per PATCH with `performUpsert`) → ~4-6 calls per monthly run
- Validated: `validate_build.py` PASS
- Status: Airtable resets July 1 — next cron fires Aug 1, will use new logic

### WaveSpeed API Key
- Confirmed `WAVESPEED_API_KEY` present and valid in `~/.env-secrets`

### Pompeii Video Pipeline — Core Discovery
- All 21 clips in `Video_Clips/` are 5.041667s on disk
- Root cause: `DURATION = 5` hardcoded in `batch_generate_videos.py` with comment "trim in post per beatmap"
- Problem: the beatmap has `target_final_duration_s` up to 12.0s — you cannot trim a 5s clip to 12s
- First proposed fix was looping — Tony immediately and correctly rejected this (looping is never acceptable for video content)

### Clips Needing Regeneration (16 total)
| Clips | Final Target | Generate | Model |
|-------|-------------|----------|-------|
| C4–C7 | 8.6s | 10s | Seedance 1.5 Pro |
| C8–C12 | 12.0s | 13s | Seedance 2.0 |
| C13–C16 | 5.5s | 7s | Seedance 1.5 Pro |
| C17–C19 | 7.0s | 8s | Seedance 1.5 Pro |

Clips C1–C3, C20–C21 are fine (5.04s source > their 3.8s/1.8s targets — just trim).

### Padding Rule Solved C13–C16
C13–C16 were only 0.46s short of their 5.5s targets. Tony asked about adjusting the beatmap or holding last frame. The 1s padding rule solved it cleanly: generate 7s → trim to 5.5s = real footage, no freeze frame, no beatmap change.

### batch_generate_videos.py — Updated
**File:** `001_Architecture/Tools/Video-Generation/Channels/Reimagined_Realms/batch_generate_videos.py`

Changes made:
- Removed `MODEL = "..."` and `DURATION = 5` hardcoded constants
- Added `MODEL_1_5`, `MODEL_2_0`, `PADDING_S = 1`, `MIN_GEN_S = 4`, `MAX_1_5_S = 12`
- `build_clip_map()` now returns `(clip_map, duration_map)` with `target_final_duration_s` per clip
- Added `generation_params(target_final_s)` → computes `(model, generate_s)` via `max(4, ceil(target + 1))`
- `generate_video()` now takes `model` and `duration` as explicit params
- Added `--overwrite` flag to force regeneration of existing clips
- Print line now shows per-clip: `[C8] → ... | Seedance-2.0 | generate=13s → trim=12.0s`
- Validated: PASS

### Hard Rules Established (all future beatmaps)
- Max 8s final duration per clip (hard rule) — viewers lose attention beyond this
- Ideal: 3–6s per clip
- Always generate with ≥1s padding: `ceil(target_final_s + 1)`, min 4s
- NEVER loop video clips — ever
- Script auto-selects model: Seedance 1.5 if generate_s ≤ 12, Seedance 2.0 if >12

### Audio Design Direction
- Approach: film composer model with stems, not per-clip or per-act sequential audio
- Layers: ambient/drone (continuous) + tension risers + impact hits (booms, brass) + scene SFX
- ElevenLabs SFX categories (bass, booms, brahms, brass, cymbal, drone, etc.) = building blocks
- Each stem fades in/out independently — no abrupt audio cuts at clip or act boundaries
- Kling Video-to-Audio considered for scene-specific SFX but rejected as primary approach (audio continuity problem across independent API calls)
- Full audio stem design system to be built next session after video is stitched

---

## Files Changed
- `001_Architecture/Tools/Video-Generation/Channels/Reimagined_Realms/batch_generate_videos.py` — updated (per-clip duration/model logic + --overwrite)
- `001_Architecture/Tools/Tool-Manager/catalog_refresh.py` — updated (batch upsert)

## Files NOT Changed (pending next session)
- `Data/Beatmap.json` — `target_generate_duration_s` fields still say 12 for all; script ignores this field now and computes dynamically. Can be updated to match new padding values but not blocking.

---

## NOT Done / Queued for Next Session
1. Run 16-clip regeneration (command ready — see handoff)
2. Stitch 21 clips → `Assembly/Pompeii_Raw_Stitch.mp4`
3. Design and build audio stem system / film-composer agent
4. Generate Suno music track
5. Final assembly: narration + stems + music + captions → `final.mp4`
6. Graphify update (Content-Creation domain)
