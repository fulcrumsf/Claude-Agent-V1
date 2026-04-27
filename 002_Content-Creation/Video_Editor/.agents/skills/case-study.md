---
description: Generate a case study of a YouTube video — fetches metadata, extracts 3 screenshots (beginning/middle/end), runs Gemini analysis on hook structure, retention mechanics, viral score, and production notes, then saves everything into the appropriate channel's case_studies/ folder.
trigger: User says "do a case study", "case study of", "analyze this video for case study", or provides a YouTube URL and asks what makes it successful / why it went viral.
---

# Skill: Video Case Study Generator

Use this skill when the user wants to analyze an existing YouTube (or public) video to understand what makes it successful and extract lessons for their own content.

## When to Use
- User says: "do a case study of [URL]"
- User says: "why did this video go viral?" + URL
- User says: "analyze this competitor video" + URL
- User says: "I want to study this video" + URL
- User provides a URL and asks what makes it work / what to replicate

---

## Step 1: Gather Required Info

If the user hasn't provided both pieces of info, ask:

1. **The video URL** (YouTube link)
2. **Which channel folder** this case study belongs to:

```
001_anomalous_wild       — Anomalous Wild (nature/animal facts)
002_neonparcel           — Neon Parcel (AI cat videos)
003_reimaginedrealms     — Reimagined Realms (AI history POV)
004_kingdoms_and_conquerors — Kingdoms & Conquerors (AI conquests)
005_glyphary             — Glyphary (folklore, myth, mysteries)
006_polyoculis           — Polyoculis (geography, phenomena, heists)
007_robotto_gato         — Robotto Gato (AI tools, n8n, automation)
008_borednomad           — Bored Nomad (travel, digital nomad)
009_unomascreative       — Uno Mas Creative (design tutorials)
010_room_portal          — Room Portal (lo-fi Ghibli loops)
011_ikigaidigitalstudio  — Ikigai Digital Studio (wall art / Etsy)
012_business_origin_stories — Business Origin Stories
```

Ask: *"Which channel is this case study for? Pick the number or name that best fits."*

---

## Step 2: Run the Generator

```bash
cd "/Users/tonymacbook2025/Documents/App Building/Video Editor"
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 tools/case_study_generator.py "[VIDEO_URL]" [CHANNEL_FOLDER]
```

**Example:**
```bash
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 tools/case_study_generator.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" 001_anomalous_wild
```

The script will:
1. Fetch YouTube metadata (title, views, likes, duration, description, tags) via YouTube Data API v3
2. Send the video URL to Gemini 2.5 Flash for a 10-section case study analysis
3. Download the video via yt-dlp (720p max)
4. Extract 3 screenshots via FFmpeg: beginning (10%), middle (50%), end (85%)
5. Save everything to: `references/channels/[channel]/case_studies/[video-title-slug]/`

Output files:
- `case_study.md` — full metadata + Gemini analysis
- `screenshot_beginning.jpg`
- `screenshot_middle.jpg`
- `screenshot_end.jpg`

---

## Step 3: Report Results

After the script completes, tell the user:

1. Where the case study was saved (full path)
2. The **viral score** summary (Hook / Retention / Shareability / Production / Overall — all /10)
3. The **top 3 things to replicate** from the analysis
4. The **one-line lesson** from Section 10

---

## What Gemini Analyzes (10 Sections)

| Section | Focus |
|---|---|
| 1. Hook Analysis | First 15 seconds — why it works |
| 2. Content Structure | Arc, pacing, micro-payoffs |
| 3. Retention Mechanics | Psychological hooks used |
| 4. Title & Thumbnail | Click-worthiness breakdown |
| 5. Production Analysis | Style, audio, graphics, budget |
| 6. What to Replicate | Top 3 actionable takeaways |
| 7. What to Avoid | Weaknesses / AI translation limits |
| 8. AI Production Notes | Prompts, hardest elements, pipeline |
| 9. Viral Score | Hook / Retention / Shareability / Production / Overall |
| 10. One-Line Summary | Core lesson distilled |

---

## Prerequisites

- `GEMINI_API_KEY` or `GOOGLE_API_KEY` in `.env` (for Gemini analysis)
- `YOUTUBE_DATA_API_KEY` in `.env` (for metadata — already configured)
- `yt-dlp` installed: `pip install yt-dlp`
- `ffmpeg` installed: `/opt/homebrew/bin/ffmpeg` (already present)
- `google-genai` installed: `pip install google-genai` (NOT the deprecated `google-generativeai`)
- `requests` installed: `pip install requests`
- All packages must be installed under `/Library/Frameworks/Python.framework/Versions/3.13/` — use that interpreter to run all scripts

---

## Notes

- Gemini analyzes the YouTube URL directly (no download needed for AI analysis)
- Video download is only needed for frame extraction — failures here won't stop the case study
- The case study folder is named after the video title (slugified, max 80 chars)
- If the video is private or geo-blocked, Gemini will return an error — ask the user for a different URL
- Analysis takes 30–90 seconds depending on video length
