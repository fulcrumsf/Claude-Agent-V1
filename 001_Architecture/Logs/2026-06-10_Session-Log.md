# Session Log — 2026-06-10
**Project:** I Love/Hate Everything card game promo video
**Working dir:** `000_Ingest/Love_Hate/`

---

## Actions

- **Identified credits blocker on kie.ai** — Seedance 2.0 returned "Credits insufficient" regardless of image format (URL or base64). Root cause: low account balance, not API structure.
- **Installed Cloudinary Python SDK** (`pip3 install cloudinary --break-system-packages`)
- **Uploaded start/end frames to Cloudinary:**
  - `01-Start.jpeg` → `https://res.cloudinary.com/da6zdvts2/image/upload/v1781062091/love_hate_scene001_start.jpg`
  - `02-End.jpeg` → `https://res.cloudinary.com/da6zdvts2/image/upload/v1781062093/love_hate_scene001_end.jpg`
- **Submitted Scene-001 to kie.ai Seedance 2.0** — task `fd9c35484dba7b3da2142d5f2f025fd2`, consumed 205 credits, 175s generation time
- **Downloaded result:** `Video_Assembly/Scene-001/Scene-001_Seedance2.mp4` — 5s, 1280×720, 24fps, 1.1MB
- **Result rejected by Tony** — card deck entered frame vertically (on edge) instead of flat/horizontal
- **Drafted revised orientation-locked prompt** for resubmission
- **Cut Reference2.mov into 5 scene clips** — stored in `Video_Assembly/Reference2_Scenes/Scene_001.mp4` through `Scene_005.mp4`
  - Discovered Reference2.mov is only 15s (scene_analysis.md timestamps were from Reference.mov, a different file)
  - Re-ran pixel-diff detection at threshold=0.18 → 5 scenes
- **Created Gemini Omni prompt** for Scene-001 using 3 references: Scene_001.mp4 (motion reference) + 01-Start.jpeg + 02-End.jpeg. Tony is uploading these manually to Gemini Omni interface.

## Files Created/Modified
- `Video_Assembly/Scene-001/Scene-001_Seedance2.mp4` — first video attempt (rejected, orientation wrong)
- `Video_Assembly/Reference2_Scenes/Scene_001.mp4` through `Scene_005.mp4` — scene cuts for reference use
- Cloudinary: `love_hate_scene001_start`, `love_hate_scene001_end`

## Pending
- Scene-001 resubmission with Gemini Omni (Tony uploading manually)
- Scene-001 resubmission to Seedance with revised orientation-locked prompt
- Shots 2–5: Gemini still image generation (`generate_shot.py`)
- Shot 6: Feed `ILHE BOX_4_IMG_6879.png` directly to Veo3 for box orbit

## Key Decisions
- Cloudinary = reliable image hosting bridge for AI APIs that require public URLs
- `FAL_AI_API_KEY` available but `storage.fal.ai` DNS doesn't resolve from this machine
- Gemini Omni being evaluated as alternative to Seedance for first/last frame video gen
