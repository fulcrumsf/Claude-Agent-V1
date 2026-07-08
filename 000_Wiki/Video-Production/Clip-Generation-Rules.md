# Clip Generation Rules — Reimagined Realms

Established: 2026-06-29
Applies to: All Reimagined Realms video productions using `batch_generate_videos.py`

---

## Hard Rules

### 1. Never Loop Video Clips
A looped clip visibly resets — the viewer sees the motion restart. This is never acceptable.  
If a clip is too short for its beatmap slot, **re-generate it at the correct duration**. There is no other valid option.

### 2. Always Generate With Padding
```
generate_s = max(4, ceil(target_final_duration_s + 1))
```
- Minimum 4 seconds (Seedance API minimum)
- At least 1 full second of padding beyond the final target
- This ensures real generated footage exists at every frame to be trimmed from

**Example:** C4 needs 8.6s final → `ceil(8.6 + 1) = 10s` generated → trim to 8.6s

### 3. Model Selection by Generated Duration
| Condition | Model |
|-----------|-------|
| `generate_s ≤ 12` | Seedance 1.5 Pro (`bytedance/seedance-1.5-pro`) |
| `generate_s > 12` | Seedance 2.0 (`bytedance/seedance-2.0/image-to-video`) |

Seedance 1.5 Pro max: 12s  
Seedance 2.0 max: 15s

### 4. Script Reads Beatmap — No Hardcoded Duration
`batch_generate_videos.py` computes `generate_s` per clip from `Beatmap.json → target_final_duration_s`.  
Never hardcode a `DURATION = N` constant. The beatmap is the source of truth.

### 5. Clip Duration Limits (Beatmap Design Rule)
- **Hard max:** 8 seconds `target_final_duration_s` per clip
- **Ideal range:** 3–6 seconds per clip
- Viewers disengage beyond 8 seconds of a single shot
- This Pompeii video (Act 3 = 12s clips) violates this rule and is the exception

---

## Script Reference

**Location:** `001_Architecture/Tools/Video-Generation/Channels/Reimagined_Realms/batch_generate_videos.py`

**Key flags:**
```bash
# Normal run (skips existing clips)
python3 batch_generate_videos.py <production_folder> --clips C4 C5 C6

# Force regeneration of existing clips
python3 batch_generate_videos.py <production_folder> --clips C4 C5 C6 --overwrite

# With ambient audio (doubles cost)
python3 batch_generate_videos.py <production_folder> --audio
```

**Per-clip output line:**
```
[C8] → C08_45.7s-57.7s.mp4 | Seedance-2.0 | generate=13s → trim=12.0s
```

---

## Regeneration Decision Tree

```
Is target_final_duration_s > raw clip duration on disk?
  YES → Regenerate (never loop)
  NO  → Trim in post

compute generate_s = max(4, ceil(target_final_s + 1))
generate_s ≤ 12? → Seedance 1.5 Pro
generate_s > 12? → Seedance 2.0
```

---

## Why This Matters

The Pompeii video (Production 0001) was generated with `DURATION = 5` hardcoded, producing 5s clips for slots needing up to 12s. This required regenerating 16 of 21 clips. This wiki page exists to prevent the same mistake in future productions.
