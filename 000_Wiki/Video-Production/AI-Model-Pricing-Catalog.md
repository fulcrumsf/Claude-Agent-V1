---
title: "AI Model Pricing Catalog"
type: wiki
category: video-production
tags:
  - pricing
  - model-catalog
  - tool-manager
  - airtable
  - video-generation
  - image-generation
created: 2026-06-21
source:
  - [[../../001_Architecture/Tools/Tool-Manager/data/model_catalog.json]]
  - [[../../001_Architecture/Tools/Tool-Manager/catalog_refresh.py]]
---

# AI Model Pricing Catalog

## What It Is

A live Airtable table (`Model Catalog`, base `Agent-OS`) showing cross-platform pricing for every AI model in active use — one row per resolution/audio variant. All prices are in genuine cost-per-second (video) or cost-per-image (image). Updated monthly via `catalog_refresh.py`.

**Airtable:** Base `appTQPmV4oWJHSfLX` → Table `tblONvSjUufdAjZx3`

## Table Structure

| Field | Description |
|-------|-------------|
| Name | `Model (Resolution · Audio)` — e.g., `Seedance 2.0 (1080p · Audio)` |
| Row ID | Unique upsert key: `{model-id}_{resolution}` |
| Resolution | `720p`, `1080p`, `2K`, `4K` (video) or `1K`, `2K`, `4K` (image) |
| Audio | `Yes` / `No` / `N/A` |
| Price Unit | `$/s`, `$/img`, `$/gen`, `$/req`, etc. |
| kie.ai | Cost per unit via kie.ai |
| WaveSpeed | Cost per unit via WaveSpeed |
| fal.ai | Cost per unit via fal.ai |
| Google Direct | Cost per unit via Google Cloud AI |
| Cheapest Platform | Winner + price, e.g., `kie.ai ($0.31/s)` |
| `X` in any cell | Platform unavailable at that resolution, or pricing unknown |

## Platform Notes

### kie.ai
Single gateway for Seedance, Kling, Veo, Wan, Suno, and image models. Generally cheapest for video. Prices are already in $/s for most video models.

### WaveSpeed
Resolution-tiered pricing for models like Seedance. Formula: `base_price × multiplier × duration / 5`
- 480p: ×1 (skip — below minimum quality)
- 720p: ×2
- 1080p: ×5

Seedance 2.0 example: base=$0.60, so 720p→$0.24/s, 1080p→$0.60/s.

### fal.ai — Seedance 2.0 Token Billing
Seedance 2.0 on fal.ai uses **token-based billing**, not flat per-second:
```
tokens = (height × width × duration × 24) / 1024
cost   = tokens / 1000 × $0.014
```
Results: 720p≈$0.302/s, 1080p≈$0.682/s. fal.ai API returns `"unit": "units"` — this means 1000-token units.

### Google Direct
Veo 3.1 Quality: $0.35/s, Veo 3.1 Fast: $0.15/s — billed per output second via Google Cloud.

## Key Pricing Benchmarks (Jun 2026)

| Model | Resolution | Cheapest | $/s |
|-------|-----------|---------|-----|
| Seedance 2.0 | 1080p | kie.ai | $0.31 |
| Seedance 2.0 | 720p | WaveSpeed | $0.24 |
| Seedance 2.0 Fast | 720p | kie.ai | $0.165 |
| Kling 3.0 Pro | 1080p | kie.ai | $0.1125 |
| Veo 3.1 Quality | 1080p | kie.ai | $0.159 (est) |
| LTX-2 Pro | 1080p | WaveSpeed | $0.012 |
| GPT Image 2 | 1K | kie.ai | $0.03/img |
| Midjourney | 1K | WaveSpeed | $0.10/img |

## How to Refresh

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Tool-Manager
source ~/.env-secrets && python3 catalog_refresh.py --skip-ratings
```

Runs automatically on the 1st of each month at 3am via cron. Syncs 34 variant records to Airtable.

## Model Files

- **Catalog JSON:** `001_Architecture/Tools/Tool-Manager/data/model_catalog.json`
- **Refresh script:** `001_Architecture/Tools/Tool-Manager/catalog_refresh.py`
- **Pricing cache:** `001_Architecture/Tools/Tool-Manager/data/pricing_cache.json` (kie.ai prices)
- **Tool-Manager CLI:** `tm` — `tm fal-search <query>`, `tm cheapest <type>`
