# Session Handoff — 2026-10-18 — Claude Code — Unomas-Creative TikTok Shop size chart templates + listing optimization

## Read first
All work is in Tony's TikTok Shop (Uno Mas Creative, Seller Center US). Every edit was submitted via **Update** and shows "Product submitted — changes submitted for review; live info won't be affected before changes are approved." **Nothing is approved yet.** First job next session: open Seller Center > Products and check review status of all 14 apparel listings (rejections/flags, especially search terms).

## What was done
Created 4 TikTok size chart templates (Seller Center > Products > size chart "Manage templates", URL `/product/batch/size-chart`), named after the Printify blank. Measurements come from Printify catalog size guides (not from the old TikTok charts):

| Template | Blank | Columns | Chest/Bust | Listings |
|---|---|---|---|---|
| Gildan 5000 | tee | Length, Chest, Sleeve length | circumference (flat width x 2) | Makin Bacon #1, Keepin' It Reel, World Is Your Oyster |
| Comfort Colors 1717 | tee | Length, Bust, Sleeve length | circumference | Motivational, Caffeine & Chaos, Skater Skeleton, Vintage Amalfi Coast, Butterfly and Moth, Makin Bacon #2 |
| Bella+Canvas 3001 | tee | Length, Chest, Sleeve length | circumference | Fishing Graphic, Spiteful Tee, Sigma Rizz |
| Gildan 18000 | sweatshirt | Length, Bust, Sleeve length | circumference | Christmas Calories, IV League |

All 14 apparel listings use the template; the sticker (Skeleton Skater, SPOKE) was not touched. Rows were trimmed per listing so the chart shows only sizes actually sold (several listings do not sell 4XL/5XL). Size labels use "XXL" (TikTok's option name), not "2XL".

## Other listing changes (same Update as the chart)
- **Category changed to Women's** (rule from Tony: images mostly women or ladylike copy = Women's; mens-like = Men's): Spiteful Tee, Christmas Calories (Women's Pullover Sweatshirts), IV League (Women's Pullover Sweatshirts), Makin Bacon #2 (Women's T-shirts). Changing category wipes attributes and size chart; chart was rebuilt after. All other listings kept their existing category.
- **Brand fixed from "No brand"**: Skater Skeleton, Butterfly and Moth (Comfort Colors); Fishing Graphic, Spiteful, Sigma Rizz (Bella+Canvas); Christmas Calories, Oyster (Gildan).
- **Search terms rewritten** (were generic category words, or junk like "blackhead extraction, black panther" on Makin Bacon #2) on: Skater Skeleton, Fishing Graphic, Spiteful, Christmas Calories, IV League, Makin Bacon #2, Sigma Rizz, Oyster, Keepin' It Reel.

## Lessons / gotchas
- **Do not put blank model names ("bella canvas 3001", "comfort colors 1717") in Search terms.** TikTok flags them "non-compliant" as a critical issue. Fixed on Fishing Graphic and Skater Skeleton before final save. Brand field handles it.
- TikTok's Bust/Chest field rejects flat-width values (min 18.9 in for Bust). Use full circumference.
- Drawer column labels follow the listing category (Women's = "Bust", Men's = "Chest"). Templates apply to either; column name stays as the template's.
- Template dropdown on a listing page is cached at page load; reload after creating/editing a template.
- Edit page URL pattern that works: `/product/edit/<product_id>?shop_region=US&tab=2`. A wrong id opens a blank new-product form (do not save it).
- A first scripted attempt accidentally clicked Add Row in a listing's own chart on Makin Bacon #1 (unsaved); discarded via "Discard", never submitted.

## Open for Tony / next agent
1. Check review results on all 14 listings in a day or two.
2. **Sigma Rizz and Makin Bacon #2 do not appear in Printify's My Products list** (Printify shows 14 products incl. the sticker, with Caffeine & Chaos repeated on page 2). Sigma Rizz chart was verified from its own uploaded size-chart image (Bella Canvas 3001, XS-4XL). Makin Bacon #2's blank (Comfort Colors) is inferred from its brand tag and garment-dyed images, unverified. Worth confirming both are still fulfillable from Printify.
3. Two Makin Bacon listings exist on TikTok (#1 Gildan 5000 id ...642329, #2 Comfort Colors id ...066969). Possible duplicate; decide whether to keep both.
4. Oyster kept in Men's (no clear women's signal); Fishing/Keepin' It Reel/Makin Bacon #1/Skater/Sigma stayed Men's by the rule. Revisit if sales stay at zero.
5. Not done: titles, images, product video field, attributes, the 100+ listing catalog goal. The earlier handoff (2026-10-17) recategorization item is partly addressed here (4 moved to Women's); others were judged correct as Men's.
6. Keepin' It Reel search terms were replaced with a shorter set; the old set used more of the 250 characters. Low risk, mention if rankings drop.

## Browser state
Tabs were left open on request (TikTok editor, template manager, product list, optimizer, Printify).

## Product IDs
Makin Bacon #1 1730055677584642329, Makin Bacon #2 1730109189694066969, Keepin' It Reel 1730683822105661721, Oyster 1729952783726776601, Motivational 1729916618683617561, Caffeine & Chaos 1729820758210220313, Skater Skeleton 1730256002367721753, Amalfi 1729757632960565529, Butterfly and Moth 1730780084769886489, Fishing Graphic 1730608842800337177, Spiteful 1730236629342064921, Sigma Rizz 1729690965680951577, Christmas Calories 1729893954609451289, IV League 1730717431954837785.

## Addendum — Seller Center tour (same day, Full-Picture mode)
Details in memory `project_unomas_tiktok_seller_center_tour.md`. Headlines: 0 visitors/orders in 7 days (traffic, not listing quality, is now the bottleneck); probation limits 0/50 orders, 15/100 listings; FBT not usable with Printify POD; "Review" in listing quality = AI optimizer change log, "Optimize" = image suggestions (IV League's main image was judged fine, not cropped; Tony reordered images by hand); 2 brand suggestions pending and safe to accept; all 16 products at 20% Open Collaboration commission with 0 creators, check margin; Makin Bacon #2 priced about double Makin Bacon #1; "Optimize 1 product to Good" mission has Mark complete available.
