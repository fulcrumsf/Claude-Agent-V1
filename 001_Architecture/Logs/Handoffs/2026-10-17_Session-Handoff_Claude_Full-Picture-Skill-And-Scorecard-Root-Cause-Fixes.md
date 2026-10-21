# Session Handoff — 2026-10-17 — Claude Code — Full-Picture Skill + Scorecard Root-Cause Fixes

## What's open for Tony to act on

1. **Unomas-Creative TikTok Shop: recategorize all 14 apparel listings from Men's to Women's/Unisex.** Confirmed root cause of zero apparel sales — every checked listing (IV League Sweatshirt, Christmas Calories Sweatshirt) is filed under `Menswear & Underwear > Men's Tops > Hoodies & Sweatshirts`, a Printify bulk-sync default never corrected, despite targeting women/unisex buyers. TikTok's own system already flags this on the Christmas Calories listing ("This category may not be the best match for your product"). Fix via Seller Center > Products > each listing's editor > Category field > accept TikTok's own suggestions. Not yet done — Tony said he'll try it.
2. **Try the listing-level product video field** on a few Unomas apparel SKUs — empty on every listing checked, may be a newer TikTok Shop feature Tony hasn't used yet. Unconfirmed as a real driver, worth testing.
3. **Decide what to do with the 100+ listing catalog goal** Tony set for Unomas (replacing the earlier, unfounded 22) — no concrete plan yet for getting there, just the target number logged in the scorecard.

## What got fixed today (all live in the Revenue Stream Scorecard artifact, https://claude.ai/artifact/MtqzUXukXTVvaNdbqQ3JgL)

- **Dashboard bar-scaling bug**: goal-vs-current bars were using a shared log-scale against a fixed global max (e.g. 250,000 for all traffic rows), so a tiny current value could look visually close to its goal. Fixed — current bars now render as a direct percentage of that row's own goal (`ratioPct` helper replacing `logPct`/`linPct` in the dashboard's `files/index.html`).
- **Neon Parcel TikTok Shop traffic figure**: was blending the account's viral/meme-content views (36K/mo, 2M/year) into a claim about product-video/commission performance. Corrected to the real number — 910 lifetime views across the only 2 actual TikTok Shop product videos (Glass Guard 726, Colorsmart Pens 184, both from Jul 2025). Follower count removed from this stream's scoring entirely (it's a meme-content metric, not attributable to product videos). A stale version of the same blended claim was also still sitting in the separate "Neon Parcel real audience profile" table — fixed there too.
- **Unomas-Creative catalog count**: was recorded as "6 active listings" from a stale earlier session; actually 15 (14 apparel + 1 sticker), verified live in Seller Center.
- **Unomas-Creative catalog/traffic goal math**: the old "22 listings" goal had no real derivation anywhere (not in the Monetization Plan, not cited). Real math from the one proven data point (the sticker's $2.10 real AOV) showed the old 29,000-views/mo traffic goal capped revenue at ~$396/mo regardless of catalog size — $1,000/mo was never reachable at that traffic level. Traffic goal raised to ~73,300 views/mo accordingly. Catalog goal then overridden by Tony to 100+ listings (a testing-range figure, not derived from the AOV math) — current figure in the scorecard.
- **Unomas-Creative root cause for zero apparel sales**: found via direct comparison against a real proven competitor (Up2oureucksinfabric Nurse Week Gift Sweatshirt, 3.4K+ sold/30 days, same niche/price range, found live via Seller Center's Product Opportunities tool) — see "wrong category" above. Real search volume (100K-1.4M/mo per listing's niche) exists but almost none reaches the listings (8 shop-wide search impressions/week, 0% CTR, not ranked).

## A claim I got wrong and had to retract

Reported "only 1 of 9 allowed images used per listing" as a confirmed finding and published it to the scorecard. Tony corrected it — he uses almost all 9 image slots. I had misread the preview carousel's position counter ("1/9" = viewing image 1 of 9 total images, not an image count). Retracted from the artifact; real thumbnails for images 2-9 were visible in the editor the whole time. Saved as a standing lesson: verify what a UI counter actually counts before asserting it as fact, especially before publishing it anywhere durable.

## Full-Picture skill — built and actively refined this session

`001_Architecture/Skills/Full-Picture/SKILL.md` — a toggleable pre-plan thinking-partner mode (invoke with "Full Picture"). Built earlier this session via iterative Q&A with Tony, then used live and strengthened twice more based on real misses surfaced during that live use:

- Added a "check what's already documented about this exact subject before analyzing fresh data" step, after a miss where I analyzed Neon Parcel traffic spikes without applying the viral-vs-affiliate-video funnel strategy I'd documented myself earlier the same session.
- Added "when 'why isn't this working' can't be answered from internal data alone, find a real proven comparable in the same niche and compare every field against it" — the method that found the Unomas category bug.

Validated clean via `validate_build.py` after every edit. This skill should be considered live/working, not a draft.

## Context for whoever reads this next

- `neonparcel_content_system.md` already documents the viral-vs-affiliate split for Neon Parcel TikTok — check it before re-analyzing that account's spike/traffic data.
- The Unomas category-miscategorization finding applies to likely all 14 apparel SKUs (confirmed on 2 directly, same `category_id` on both), not just the ones checked — worth a full catalog sweep once Tony starts fixing categories, to confirm all 14 and not just the 2 spot-checked.
- Scorecard dataset version numbers as of this handoff: `goal_targets` v20, `scores` v10, `neon_parcel_audience` v4, dashboard `files/index.html` v43.
