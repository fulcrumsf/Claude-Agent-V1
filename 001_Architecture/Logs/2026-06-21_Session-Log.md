---
title: "Session Log 2026-06-21"
type: log
date: 2026-06-21
tags: [session-log, tool-manager, airtable, pricing, model-catalog]
---

# Session Log — 2026-06-21

## Work Completed

### fal.ai Billing Unit — Resolved
- Investigated `"units"` ambiguity in fal.ai pricing API for Seedance 2.0
- **Answer:** Token-based billing, not per-second or per-video
- Formula: `tokens = (height × width × duration × 24) / 1024` at $0.014/1K tokens
- Resolves to: Standard 720p = $0.302/s, Standard 1080p = $0.682/s, Fast 720p = $0.242/s
- fal.ai API returns `"billing_unit": "1000 tokens"` — the old `"units"` label in the Platform API was misleading

### Airtable Model Catalog — Full Table Restructure
- **Before:** 24 rows, one per model, prices normalized to per-5s-clip equivalent
- **After:** 34 rows, one per resolution/audio variant, all prices in genuine $/s or $/img
- New Airtable fields created: `Row ID`, `Resolution`, `Audio`, `Variant`, `Price Unit`
- `Row ID` is now the upsert key (e.g., `seedance-2.0_1080p`) — replaces `Model ID`
- Name column shows `Model (Resolution · Audio)` format (e.g., `Seedance 2.0 (1080p · Audio)`)
- Deleted 24 stale pre-restructure records from Airtable

### model_catalog.json
- Added `variants` arrays to all 25 models with pre-computed per-second/per-image prices
- Added **ElevenLabs Video-to-Music** as a new model (elevenlabs-video-to-music)
- Set **Topaz Upscale** to `status: inactive` (excluded from Airtable sync)
- Removed unit columns that Tony deleted from Airtable (`kie.ai Unit`, `WaveSpeed Unit`, `fal.ai Unit`)

### catalog_refresh.py
- Rewrote `sync_to_airtable()` to iterate variants instead of models
- Added `_fmt_price()` helper — outputs `$0.31/s`, `$0.02/img`, `$0.06/gen` etc.
- Display name includes variant: `f"{model['name']} ({variant_label})"`
- All 34/34 variant records synced successfully

### WaveSpeed Pricing Formula (locked in from previous session)
- Resolution multipliers: 480p×1, 720p×2, 1080p×5
- Formula: `base_price × resolution_mult × duration / 5`
- Seedance 2.0: 720p=$0.24/s, 1080p=$0.60/s; Fast: 720p=$0.20/s, 1080p=$0.50/s

## Files Changed
- `001_Architecture/Tools/Tool-Manager/data/model_catalog.json`
- `001_Architecture/Tools/Tool-Manager/catalog_refresh.py`

## Next Session
- Pompeii video (Reimagined Realms pipeline) — video editing
