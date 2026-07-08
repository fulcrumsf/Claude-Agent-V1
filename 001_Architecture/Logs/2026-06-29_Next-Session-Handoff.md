# Next Session Handoff — 2026-06-29

## Context
Pompeii video for Reimagined Realms. All 21 clips were generated at the wrong duration (5s instead of up to 12s). Script has been fixed. 16 clips need to be re-generated. Video has NOT been assembled yet.

---

## Step 1 — Run Regeneration (FIRST THING)

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Channels/Reimagined_Realms

python3 batch_generate_videos.py \
  "/Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/002_Channels/003_Reimagined-Realms/Productions/0001_Pompeii_The_Escape" \
  --clips C4 C5 C6 C7 C8 C9 C10 C11 C12 C13 C14 C15 C16 C17 C18 C19 \
  --overwrite
```

**What this generates:**
| Clips | Generate Duration | Model | Final Trim |
|-------|-----------------|-------|------------|
| C4–C7 | 10s | Seedance 1.5 Pro | 8.6s |
| C8–C12 | 13s | Seedance 2.0 | 12.0s |
| C13–C16 | 7s | Seedance 1.5 Pro | 5.5s |
| C17–C19 | 8s | Seedance 1.5 Pro | 7.0s |

Clips C1–C3, C20–C21 are already correct at 5.04s (will be trimmed to 3.8s/1.8s during stitch).

**Expected duration:** 16 generations × ~3-5 min each = 1–2 hours. Safe to run in background.

---

## Step 2 — Stitch Video (after regeneration completes)

Assemble all 21 clips in beatmap order into one file. Non-destructive (copies only). No transitions — hard cuts.

- **Output:** `Assembly/Pompeii_Raw_Stitch.mp4`
- **Duration:** 152.5s
- **Timing:** Must match narration exactly (narration total = 152.508s)
- **Script to update/use:** `assemble.py` OR direct ffmpeg trim + concat

Trim/loop rules:
- C1–C3: trim 5.04s → 3.8s
- C4–C7: trim 10s → 8.6s (after regen)
- C8–C12: trim 13s → 12.0s (after regen)
- C13–C16: trim 7s → 5.5s (after regen)
- C17–C19: trim 8s → 7.0s (after regen)
- C20–C21: trim 5.04s → 1.8s

**No looping ever.** Every clip must be trimmed from longer generated footage.

---

## Step 3 — Design Audio Stem System (film composer model)

Tony wants audio designed like a movie score, not background music:
- **Ambient/drone stems** — continuous atmospheric layer (fade in/out by act)
- **Tension risers** — build during Acts 2 & 3 as eruption escalates
- **Impact hits** — booms, brass stabs, cymbal crashes at key visual moments
- **Scene SFX** — crowd noise, wind, rumble, ash (timed to beatmap)

ElevenLabs SFX categories to use as building blocks:
`bass, booms, brahms, brass, cymbal, device, drone, glass, impact, nature, whoosh`

Max 30s per ElevenLabs SFX call. Plan stems as continuous layers, not per-clip audio.

**Pending decision:** Whether to build a dedicated audio stem agent/skill or handle it inline.

---

## Step 4 — Generate Suno Music Track

Deferred from this session. Tony wants a Suno music bed underneath the stems.
- Length: 152.5s (match video)
- Tone: cinematic, dramatic, building to pyroclastic surge climax

---

## Step 5 — Final Assembly

`narration + ambient stems + music + color grade + captions → final.mp4`

---

## Key File Locations

| Asset | Path |
|-------|------|
| Production root | `002_Content-Creation/Video_Editor/002_Channels/003_Reimagined-Realms/Productions/0001_Pompeii_The_Escape/` |
| Video clips | `Video_Clips/C01_0.0s-3.8s.mp4` ... `C21_150.7s-152.5s.mp4` |
| Beatmap | `Data/Beatmap.json` |
| Narration | `Narration_Audio/Scene_01.mp3` ... `Scene_06.mp3` (152.508s total) |
| Shot list | `Production/Shot_List.md` |
| Assembly output | `Assembly/` (create this folder) |
| Generation script | `001_Architecture/Tools/Video-Generation/Channels/Reimagined_Realms/batch_generate_videos.py` |

---

## Hard Rules (established this session — apply to all future productions)
- Max 8s final duration per clip in any beatmap (ideal: 3–6s)
- Always generate with ≥1s padding: `ceil(target_final_s + 1)`, min 4s
- Never loop video clips — ever
- Seedance 1.5 Pro for generate_s ≤ 12s, Seedance 2.0 for >12s
- Script reads beatmap for duration — never hardcode

---

## Also Pending (not Pompeii-specific)
- Graphify update for Content-Creation domain (changed batch_generate_videos.py)
- Update Beatmap.json `target_generate_duration_s` fields to reflect new padded values (informational only — script computes dynamically, but beatmap should be accurate)
