---
description: Converts a finished Anomalous Wild script into a production beat sheet — a row-per-scene spreadsheet with timestamp, narration, shot type, action, on-screen text, music cue, sound design, and AI generation flags. Output is the master production document.
status: active
channel: 001_anomalous_wild
---

# Skill: Video Beat Sheet Generator

## Purpose

Takes a completed script and produces the **master production document** — a scene-by-scene breakdown used by:
- AI footage prompter (for Kling/Veo prompts)
- CC0 footage researcher (to find substitute real footage)
- ElevenLabs TTS runner (for narration audio)
- Remotion compositor (for text overlays and timing)
- Video stitcher (for final assembly order)

---

## Beat Sheet Row Format

Each row = one scene (typically 3–8 seconds of screen time).

| Field | Description |
|---|---|
| `scene_id` | `scene_01`, `scene_02`, etc. — matches folder names for stitcher |
| `arc_section` | GLITCH_HOOK / SETUP / TEASE_1 / CONTEXT_LOOP / TEASE_2 / REWARD / HOOK_FORWARD |
| `timestamp_start` | Estimated start time (MM:SS) |
| `timestamp_end` | Estimated end time (MM:SS) |
| `narration` | Exact spoken text for this scene |
| `narration_duration_s` | Estimated seconds at narrator pace (~2.5 words/sec) |
| `shot_type` | macro / extreme_closeup / wide_establishing / overhead / pov / 3d_render / animation / talking_head |
| `subject` | What the camera is focused on |
| `action` | What is happening in the frame |
| `on_screen_text` | Any animated text callout (or `none`) |
| `on_screen_text_position` | top-left / center / bottom-center |
| `music_cue` | full / duck_to_15pct / swell / silence / stinger |
| `sound_design` | Specific ambient sound or effect |
| `transition_out` | hard_cut / glitch_cut / slow_mo_freeze / none |
| `asset_source` | ai_generate / cc0_search / ai_fallback / existing_library |
| `ai_prompt_needed` | YES / NO |
| `cc0_search_query` | Search string for CC0 footage if `asset_source = cc0_search` |
| `notes` | Any special production note |

---

## Output Formats

Produce the beat sheet in **two formats**:

### 1. Markdown table (for review)
Human-readable table with all fields.

### 2. JSON array (for tools)
```json
[
  {
    "scene_id": "scene_01",
    "arc_section": "GLITCH_HOOK",
    "timestamp_start": "0:00",
    "timestamp_end": "0:03",
    "narration": "This creature evolved its own light source.",
    "narration_duration_s": 3,
    "shot_type": "extreme_closeup",
    "subject": "anglerfish bioluminescent lure",
    "action": "lure pulses with blue-white light in absolute darkness",
    "on_screen_text": "none",
    "music_cue": "silence",
    "sound_design": "deep ocean ambience, distant water pressure hum",
    "transition_out": "glitch_cut",
    "asset_source": "ai_generate",
    "ai_prompt_needed": true,
    "cc0_search_query": "",
    "notes": "Use extreme macro lens simulation"
  }
]
```

---

## Timing Rules

- Narration pace: ~2.5 words per second (Higsley voice, deliberate Attenborough cadence)
- Each scene should have enough footage duration to cover the narration + 0.5s breathing room
- Music swell scenes: add 2–3s of silence before the reward fact
- Glitch cuts: 1–2 frames only — do not linger

---

## Asset Source Decision Tree

```
Is there good CC0/MBARI/Wikimedia footage of this exact shot?
  YES → asset_source: cc0_search
  NO → Can a Kling/Veo AI prompt capture this accurately?
    YES → asset_source: ai_generate
    NO (e.g., specific anatomy cross-section) → asset_source: ai_generate + notes: "3D render required"
```
