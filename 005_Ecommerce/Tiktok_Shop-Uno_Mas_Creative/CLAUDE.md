---
title: "CLAUDE.md — Unomas-Creative TikTok Shop"
type: config
domain: ecommerce
tags: [config, ecommerce, unomas-creative, tiktok-shop]
---

# CLAUDE.md — Unomas-Creative TikTok Shop

Tony's TikTok Shop under the **Unomas-Creative** brand (canonical spelling confirmed by Tony, 2026-10-11 — see the known-spelling-inconsistency note in `001_Architecture/Plans/Agent-OS-Monetization-Strategy-Plan.md`, section 4).

## Status (verified live in TikTok Seller Central, 2026-10-11)

- **Fulfillment:** Printify (see `005_Ecommerce/POD/Printify/CLAUDE.md`) — every order routes through "Printify Warehouse."
- **Products:** 15 active listings. **Correction, 2026-10-11 — not all are repurposed Bored Nomad designs, per Tony.** Most titles match the Bored Nomad Etsy catalog (Makin Bacon Pancakes, Christmas Calories, IV League Sweatshirt, Fishing Graphic, Butterfly and Moth, Vintage Amalfi Coast, Spiteful Tee, Caffeine & Chaos, Keepin' It Reel Fishing, Skeleton Skater Sticker), but at least one — "Sigma Rizz Retro T-Shirt | 90s Y2K Vintage Meme Rizzler Tee" — does not appear on the Bored Nomad Etsy shop and is likely Unomas-Creative-original. Not every listing individually verified against the Etsy catalog; don't assume the full list is a 1:1 repost without checking. 0 Needs Attention, 0 Draft, 0 Reviewing.
- **Lifetime orders: 3 total, all "Skeleton Skater Sticker for Skateboard and Laptops"** (the only product that's actually sold):
  - 02/26/2026 — 4"×4" size, $2.75 total, **$2.38 earned** after fees
  - 02/21/2026 — 2"×2" size, $1.82 total, **$1.71 earned** after fees
  - 10/17/2025 — $2.57 total (order detail page errored on load; amount confirmed from the order list, product presumed the same sticker given the pattern)
  - **Lifetime revenue: ~$7.14 total, ~$6.09+ earned after TikTok/Printify fees** — this is the real number, not "a couple of sales" in the abstract.
- All 15 other listings show 0 items sold, low view counts (single digits to ~70s) — the sticker is the only product with any traction so far.
- This is distinct from the general `002_Content-Creation/Whop_Clipping/` / `TikTok-Shop-Affiliate-Video` skill work (that's affiliate promotion of other people's products; this is Tony's own Printify-fulfilled product storefront on TikTok Shop).

## Relevance to the $1,000/month goal

See `001_Architecture/Plans/Agent-OS-Monetization-Strategy-Plan.md` for the full comparison — at ~$6/lifetime net earnings after a year+ of listings, this stream is not currently a meaningful contributor, but the one product that *did* sell (a cheap, low-friction sticker) may be a signal worth testing — lower price point, lower consideration purchase converts better on TikTok Shop than full-price apparel.

## Why views/search volume are low — diagnosed 2026-10-11, corrected after Tony's pushback

First pass misread the optimizer side-panel as "1 of 9 images, no size chart" — **wrong, Tony caught it.** Opened the actual listing editor directly (`product/edit/<id>`) to re-check properly:

- **Category search volume is huge, listing views are tiny — a real gap.** E.g. "Caffeine & Chaos" sits in a keyword category with 1,481,473 searches but has only 12 views; "Makin Bacon Pancakes" is in a 1,459,351-search category with 17 views. This pattern repeats across most listings. The demand exists; these specific listings aren't surfacing for it.
- **Confirmed on the real listing editor: 8 of 9 images ARE uploaded, including one clearly labeled "Size Chart."** Images are not the problem on this listing.
- **The real, confirmed cause: TikTok's automatic size-chart text recognition fails to read the uploaded size chart image.** The page shows the exact error: *"We couldn't detect any size information. Please try another image."* Zoomed into the actual uploaded image — the "Size Chart" heading is in a **decorative cursive/script font**, with a fairly small measurement table below it (SIZE/WIDTH/LENGTH columns, S/M/etc. rows). Stylized fonts and small text are exactly what breaks OCR/text-recognition systems like this one.
- **Fix, recommended to Tony, not yet done:** use TikTok's **"Create size chart"** structured tool instead of uploading an image — enter S/M/L/XL/XXL/3XL measurements as actual data fields, removing the OCR failure point entirely. Alternative: keep an image but make a plain, high-contrast, standard-font version just for TikTok (the decorative cursive version can stay on Etsy/elsewhere where it's just visual branding, not something a system needs to parse).
- **Per-listing image completeness not yet audited** — only "Caffeine & Chaos" was checked directly (8/9 images, real size chart that fails parsing). The "Parts to improve" column flagging "Images" and/or "Size information" on other listings needs the same direct-editor check before assuming the same cause applies — don't generalize from one listing again.
- TikTok's own optimizer already ran ("13 listings automatically optimized") but 7-day search impressions are still 0 — consistent with a size-chart-parsing failure blocking full listing quality, since auto-optimization can't fix a human-readability/OCR problem in an uploaded image.

## Open items

- Not yet connected to any analytics/API (see `001_Architecture/API_Directory.md`).
- `Products > Search optimization` page loaded blank during this check — possibly needs more account sales/traffic history to populate; worth revisiting once there's more activity.
- Full per-listing audit (which of the 15 are Bored Nomad reposts vs. original Unomas-Creative designs) not yet done — only spot-checked.
- **RESOLVED by Tony, 2026-10-11 night — found the right tool.** The session's attempt to use TikTok's "Create size chart" structured-data tool hit a dead end (a platform-wide Bust-field minimum of 18.9" rejected the real 18.25" S-size measurement, and the multi-select tag UI for adding a custom "Width" column kept breaking/resetting). Tony instead used TikTok's **"Convert Image to Size Chart"** function directly on the existing uploaded chart image — this is a different, better path than the manual structured-entry route this session was stuck on. Confirmed working by Tony on the "Caffeine & Chaos" listing.
- **Next action (2026-10-12):** apply the same "Convert Image to Size Chart" fix to the other 14 listings flagged with the same "Images"/"Size information" warning in `Products > Improve listing quality`. Each listing needs its own existing size chart image run through that conversion tool — not re-done from scratch. Re-check the "Needs attention" panel per listing after conversion to confirm it clears, same as it did for Caffeine & Chaos.
