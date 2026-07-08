# Next Session Handoff — 2026-07-03

## Current State: Pompeii Pipeline

**Production:** `002_Content-Creation/Video_Editor/002_Channels/003_Reimagined-Realms/Productions/0001_Pompeii_The_Escape/`

### What's Done
- ✅ All 21 clips generated at correct beatmap durations (C1–C7, C13–C21 via Seedance 1.5)
- ✅ C8–C12 regenerated at 12s with Seedance 1.5 (no Seedance 2.0 needed)
- ✅ Original 5s clips archived to `Video_Clips/Archive_5s_Originals/`
- ✅ Raw video stitched: `Assembly/raw_video.mp4` (232.6 MB, 152s)
- ✅ Gemini second-by-second scene analysis: `Assembly/gemini_scene_analysis.md`
- ✅ 13 audio stems generated: `Audio_Stems/*.mp3`
- ✅ Stems mixed: `Assembly/stems_mix.mp3`
- ✅ Narration concatenated: `Assembly/narration.mp3`
- ✅ Two video outputs ready to watch:
  - `Assembly/0001_Pompeii_The_Escape_raw_with_stems.mp4` (208 MB)
  - `Assembly/0001_Pompeii_The_Escape_raw_with_stems_narration.mp4` (209 MB)
- ❌ `Assembly/music.mp3` — Suno generation failing (kie.ai outage as of 2026-07-03). Retry with: `python3 assemble.py --phase 4 --stop-phase 4`
- ❌ `Assembly/0001_Pompeii_The_Escape_final.mp4` — blocked on Suno

---

## CRITICAL DESIGN DECISION — Next Audio Pass

**The current stem approach is wrong. Do NOT re-run generate_stems.py with the current design.**

### What Tony decided:

The audio pipeline needs a **vision-based audio composer** that:

1. **Watches the video like a human** — one screenshot per second extracted from `raw_video.mp4` via ffmpeg
2. **Cross-references three sources simultaneously:**
   - Screenshots (what the viewer sees each second at 720p)
   - `Assembly/gemini_scene_analysis.md` (second-by-second text description)
   - Narration script (what is being said at each second)
3. **Generates individually tailored audio clips** — not broad thematic stems. One unique audio clip per scene moment, each generated with a prompt describing THAT specific moment
4. **Labels clips by scene and timecode**: `C05_0020_eruption_gasp.mp3`, `C08_0046_hooves_cart.mp3`
5. **Outputs a Premiere-compatible XML** (FCPXML or Premiere XML) that places all audio clips on the timeline at the correct timecodes on separate named tracks — so Premiere auto-builds the audio layout on import

### Why the current approach failed:
- Broad stems (e.g., `panicked_crowd` running 25s→57s) span multiple scenes with different visual content
- ElevenLabs generates generic audio that loops and doesn't respond to scene changes
- No impact hits, no risers, no transition whooshes — only ambient layers
- The audio composer had no visual context, only text summaries

### What a real documentary audio composer does:
- **Per-scene specific sounds** — every scene has its own audio decision
- **Spot FX timed to exact frames** — sub-bass boom when eruption column appears at 0:20, not a 37s ambient rumble
- **Risers** — tension builds 2-3s BEFORE a dramatic cut, so by the time the image changes the viewer is already primed
- **Silence** — some moments (the plaster cast reveal, the desk scene) get near-silence + a single sustained string note, not ambient sound
- **Transitions** — whooshes, low frequency swells between acts
- **Scene-responsive fades** — crowd sound fades out BECAUSE the crowd disperses on screen, not on a timer

### Two audio categories (NOT just "stems"):
1. **Ambient layers** — continuous beds (wind, room tone, distant rumble) — true stems
2. **Spot FX / event hits** — discrete timed clips (impact booms, risers, whooshes, crowd hit, hooves) — individual clips placed at exact timecodes

Both categories are kept as separate files for Premiere. Nothing is pre-mixed.

---

## Next Session — Exact Steps

### Step 1: Research pass FIRST (do not skip)
Before building the new audio composer, research documentary sound design:
- How Planet Earth II, Our Planet, and similar productions design audio
- What risers, impact hits, whooshes, and room tone look like in a real timeline
- Save findings to `000_Wiki/Video-Production/Documentary-Sound-Design.md`

### Step 2: Extract frames at 1fps
```bash
mkdir -p ".../0001_Pompeii_The_Escape/Assembly/Frames"
ffmpeg -i ".../Assembly/raw_video.mp4" \
  -vf "fps=1,scale=1280:720" \
  -q:v 3 \
  ".../Assembly/Frames/frame_%04d.jpg"
```
Result: ~152 JPEGs in `Assembly/Frames/`

### Step 3: Build vision-based audio composer script
Location: `001_Architecture/Tools/Audio/compose_audio.py`
- Accepts: production_folder
- Reads: Assembly/Frames/*.jpg + gemini_scene_analysis.md + Production/Narration.md (or Script.md)
- Sends to Gemini (vision model) with documentary sound design knowledge baked into the prompt
- Gemini outputs a structured JSON audio brief: per-second/per-scene audio decisions
- Script generates each audio clip via ElevenLabs SFX
- Script generates FCPXML or Premiere XML placing clips at correct timecodes

### Step 4: Retry Suno when kie.ai recovers
```bash
cd .../0001_Pompeii_The_Escape
python3 assemble.py --phase 4 --stop-phase 4
```
Then run final render:
```bash
python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Audio/render_outputs.py \
  ".../0001_Pompeii_The_Escape"
```

---

## Tools Built This Session (all reusable)

| Script | Location | Purpose |
|--------|----------|---------|
| `batch_generate_videos.py` | `001_Architecture/Tools/Video-Generation/Channels/Reimagined_Realms/` | Generate clips from beatmap |
| `gemini_scene_analysis.py` | `001_Architecture/Tools/AI-Analysis/` | Second-by-second Gemini video analysis |
| `generate_stems.py` | `001_Architecture/Tools/Audio/` | Generate audio stems via ElevenLabs |
| `mix_stems.py` | `001_Architecture/Tools/Audio/` | Mix stems onto timeline with ffmpeg |
| `render_outputs.py` | `001_Architecture/Tools/Audio/` | Render 3 video outputs at professional levels |
| `assemble.py` | Production root | 7-phase full assembly pipeline |
| `compose_audio.py` | `001_Architecture/Tools/Audio/` | **TO BUILD** — vision-based audio composer |

## Audio Level Standards (locked in)
- Narration: loudnorm -14 LUFS / -1 dBTP (YouTube standard)
- Ambient stems: 40% in final mix
- Spot FX / event hits: variable, set per-clip in Premiere
- Music bed: 12% (heavily ducked)

## Key File Locations
| Asset | Path |
|-------|------|
| Production root | `002_Content-Creation/Video_Editor/002_Channels/003_Reimagined-Realms/Productions/0001_Pompeii_The_Escape/` |
| Raw stitch | `Assembly/raw_video.mp4` |
| Gemini analysis | `Assembly/gemini_scene_analysis.md` |
| Stem map | `Data/stem_map.json` |
| Frames (to extract) | `Assembly/Frames/` |
| Audio stems | `Audio_Stems/` |
| Video outputs | `Assembly/0001_Pompeii_The_Escape_*.mp4` |
| Beatmap | `Data/Beatmap.json` |
| Narration audio | `Narration_Audio/Scene_01.mp3` … `Scene_06.mp3` |
