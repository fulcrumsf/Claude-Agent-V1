---
title: "Agent-OS Monetization Strategy Plan"
type: plan
domain: architecture
tags: [plan, monetization, revenue, analytics, affiliate, etsy, youtube]
status: living
created: 2026-10-11
updated: 2026-10-13
---

# Agent-OS Monetization Strategy Plan

**Status:** Living document. First draft 2026-10-11; second pass the same day folded in Tony's answers to the 12 open questions and a read of every department folder's own docs. Updated whenever new business info comes in. Not a build plan: nothing in here is approved for building yet.

**To-do link:** top-priority item #1 in `001_Architecture/Ongoing-Agent-OS-To-Do-List.md` ("Agent-OS monetization strategy", added 2026-10-11).

---

## 1. Purpose

This is the living map of every way Agent-OS makes money, or is meant to. It exists so Tony never has to re-explain his business to a new session: any agent picking up monetization work reads this file first. It is judged against one goal, set by Tony (section 2): **$1,000/month in income by December 2026.**

**Which source wins when docs disagree (Tony, 2026-10-11):** each department folder's own `.md` files are the real source of truth for that business's status. The one-line summary tables in the root `CLAUDE.md` and `BUSINESS_CONTEXT.md` are older and lose wherever they conflict with the folder docs. Conflicts the folder docs can't settle are flagged in section 4, not guessed.

**Related files (read these, don't duplicate them):**

- Department folder docs (listed per stream in section 3): the real per-business status.
- `001_Architecture/API_Directory.md`: the source of truth for what is actually connected. Section 5 summarizes it.
- `001_Architecture/Revenue-Streams.md`: **re-checked 2026-10-11, still an unfilled template** (every figure is a `$[X]` placeholder). It is the intended home for raw per-stream numbers once they exist. This plan is the strategy map; that file is the numbers ledger. Fill it, don't fork it.
- `001_Architecture/Business-Strategy.md` and `001_Architecture/Strategic-Roadmap.md`: **re-checked, still pure placeholder templates.** `001_Architecture/Ecosystem-Map.md`: a generic diagram template with no real numbers or stream specifics.
- `005_Affiliate_Marketing/Affiliate-Program-Removal-Checklist.md` and its live artifact (the **Affiliate & Referral Audit**, link in section 3's affiliate marketing entry): the working inventory of every affiliate program and referral code, post-cleanup 2026-10-12.
- `005_Affiliate_Marketing/Stock-Portfolio-Checklist.md` and its live artifact (the **Stock Portfolio Audit**): historical stock photo/footage portfolios, reference only (section 3b).

**What this plan is for, operationally (Tony, 2026-10-12):** this file (plus the department docs and trackers it points to) is meant to be complete enough that Tony can ask a status question — "how's my Fine Art America store doing?", "do we have an ad campaign running on TikTok?" — and get a real answer: either the tracked status/numbers, or an honest "that's not connected/tracked yet, here's what it'd take to set up." Every stream below should end in one of three states: **tracked** (real numbers, a live source), **known but unconnected** (it exists, no analytics/data pulled yet), or **not set up** (planned/doesn't exist). When a stream is in the second or third state, say so plainly rather than guessing or inventing a number.

---

## 2. Success criteria (Tony, 2026-10-11)

**The goal: reach $1,000/month in income by December 2026, through whichever combination of streams gets there fastest and easiest.**

- **Optimize for speed-to-goal and ease.** Not long-term scale, not elegance, and not picking one single "best" stream. A mix of three small streams that adds up to $1,000 counts just as much as one big one.
- **Anything is on the table.** Tony named digital products/ebooks and pushing harder on Ikigai Digital Studios as examples, "or anything else."
- **The clock:** from 2026-10-11 that is about 7 weeks to the start of December and about 11.5 weeks to the end of it. Anything that needs months to ramp (new SEO sites, new YouTube channels, a Roblox game) is unlikely to contribute meaningfully by December, however good it is long-term.
- **This is the lens for the whole plan.** Every stream in section 3 now ends with "what's missing to move it toward $1,000/mo by December."

**The next real step, once every stream is mapped:** score each stream on one question: "How fast, and how easily, can this realistically add $X/month by December?" Inputs per stream: today's real monthly income, the effort to add more, how long until new effort turns into money, and running costs (e.g. Etsy ad spend). Section 7 has a first, evidence-only read that fed the scoring. **The scoring itself is done — section 7b, completed 2026-10-13.**

**Resolved, 2026-10-11:**

1. **Gross or net? RESOLVED: net — $1,000/month in profit**, confirmed directly by Tony. Income after direct platform costs (e.g. Etsy sales minus Etsy ads and fees) is what counts. Etsy ad spend has exceeded sales in at least one recent period (section 3), so this matters — a stream showing revenue can still be a net loser.
2. **What month counts?** Still assumed: the December 2026 calendar month totals $1,000+ profit across all streams, measured from one place (Xero is the likely candidate, section 5). Not yet explicitly confirmed by Tony.

---

## 3. Revenue streams map (folder-verified, 2026-10-11)

Every department folder was read on 2026-10-11. "Docs" says whether the folder actually describes the business or is empty scaffolding. "Revenue today" only says what the workspace can prove; no stream has real income figures recorded anywhere in the workspace yet.

### 3a. Summary table

| Stream | Real status (folder docs) | Docs in workspace | Revenue today (evidence) | Analytics |
|---|---|---|---|---|
| **YouTube, 12 launched channels** | Live, but in "trial phase" per `Video_Editor/CLAUDE.md` | Strong (channel bibles for 11 of 13 channel folders) | Not documented. Likely small (see detail) | 🟢 Views/subs live; no revenue data |
| **Etsy POD: Bored Nomad** | Live store, verified directly 2026-10-11 (https://www.etsy.com/shop/BoredNomad): 157 sales, 97 listings, 4.9★/31 reviews, on Etsy since 2020, Printful/Printify fulfillment | Now strong — canonical doc at `005_Ecommerce/Etsy-Bored_Nomad/CLAUDE.md` (merged, 2026-10-11) | Real sales confirmed via Xero P&L (section 5): Etsy Sales $467.00 domestic + $19.50 intl YTD, after a -$69.42 coupon line | 🔴 Route decided, not built (section 5) |
| **Etsy Digital: Ikigai Digital Studios** | Live store, verified directly 2026-10-11 (https://www.etsy.com/shop/IkigaiDigitalStudio): 63 sales, 18 listings, 5.0★/4 reviews, on Etsy since 2023, 100% digital downloads $6.50-$8.50 each, zero production/shipping cost | Now strong — new `Etsy-Ikigai/CLAUDE.md` written, resolves the "empty folder" gap flagged in section 4 | Store is live and running Etsy ads; at least one recent period where ad spend/fees exceeded sales (unconfirmed which LLC's Xero books this — section 5 open item) | 🔴 Same Etsy route |
| **Unomas-Creative POD** (TikTok Shop + Printify pop-up store) | Verified directly in TikTok Seller Central, 2026-10-11: 15 active listings (mostly, not all, match the Bored Nomad Etsy catalog), fulfilled via Printify. Low views traced to missing product images/size charts, not titles/keywords | Now documented — `005_Ecommerce/Tiktok_Shop-Uno_Mas_Creative/CLAUDE.md`, full product/order/diagnostic data | **Lifetime: 3 orders, ~$7.14 revenue, ~$6.09 earned, all one product** (Skeleton Skater Sticker) — the only listing of 15 with any sales | 🔴 None |
| **Redbubble: Bored Nomad** | **Active, verified live 2026-10-12** — 60 designs, logged into the actual seller dashboard (not just the public shop) | **None.** No folder yet; only a link on borednomad.com's resources page. Shop URL: `https://www.redbubble.com/people/borednomad/shop` — saved here, don't ask Tony for it again | **Real monthly earnings pulled directly, 2026-10-12:** Jul 2026 $0, Aug 2026 $13.54 (after fees), Sep 2026 $8.20 (after fees). Matches Tony's own "$10-20/month, depends" estimate | 🟢 Redbubble's own Earnings Details page — real, dated, pullable by month; no public API |
| **Amazon KDP** | **Active but dormant — verified live in the KDP dashboard 2026-10-12.** 5 paperback journals live (all from 2020-2021), no eBook/hardcover editions. Tony wants to expand into coloring/activity books now that AI can help produce them | **None.** `005_Ecommerce/KDP/` is empty (no CLAUDE.md, though `DEPARTMENTS.md` points to one). Niche-research tools already bookmarked: `007_Resource_Library/Tools/Kdp.md` (Book Bolt, Helium 10, Publisher Rocket) | **$0.00 in both September and October 2026** (real, pulled from Prior Months' Royalties, all 17 marketplaces) — no recent sales despite being live | 🔴 None — KDP has no seller-facing analytics API; Amazon KDP Reports are manual-export only, now a known repeatable login path |
| **Amazon Merch on Demand** | **Planned, deliberately paused (Tony, 2026-10-12).** No account set up yet — Tony is intentionally waiting until Bored Nomad POD and Ikigai Digital Studios are making more consistent money before adding a fourth POD-style stream, to avoid spreading effort too thin | Thin (CLAUDE.md only) | None (not started per folder) | n/a |
| **Affiliate marketing** (travel + AI tools, 18 programs) | Live program memberships; Bored Nomad site carries real affiliate links | Strong department brief (`005_Affiliate_Marketing/CLAUDE.md`); all 17 per-program folders empty | Not documented | 🟡 GA4 site traffic only; no commission data |
| **TikTok Shop affiliate** (Neon Parcel TikTok) | **Confirmed live by Tony, 2026-10-12** — Colorsmart Pens and Glass Guard both went live with product links. Videos: `https://www.tiktok.com/@neonparcel` (saved here, don't ask again) | Strong (compliance ledger, 18 TOS docs, per-video scans) | **No commissions earned yet**, confirmed by Tony — live but not yet converting | 🔴 None |
| **Whop clipping** | **Paused (Tony, 2026-10-12).** Was in a couple of clipping campaigns (unnamed, no longer active), earned roughly $30-40 total. Didn't get good at it before stopping. Plan is to come back later with a more automated version — not scoped, not now | Thin (CLAUDE.md only) | ~$30-40 lifetime, informal, not current | n/a |
| **Social media marketing** (Pinterest/IG, fashion) | **Planned** (folder: "no active posting pipelines yet") | Thin, plus a detailed adjacent brief (`Plans/AI-Fashion-Affiliate-Implementation-Brief.md`) | None | 🟡 Blotato analytics tools, untested |
| **Digital products** (guides, ebooks, Gumroad / own site / email funnels) | **Planned** (folder: "setup and product design stage") | Thin (CLAUDE.md only) | None | n/a |
| **Email list** | **Exists, confirmed by Tony 2026-10-12** — ConvertKit (Kit), roughly 1-2 subscribers. Possibly also a small list via Beacons and/or Pensight, platform-to-channel mapping unconfirmed | **None.** No folder or doc | Effectively $0 — no offer/lead magnet is live, and Tony says the signup isn't prominent on a website he describes as currently broken | 🔴 None |
| **Bored Nomad website rebuild** | Not started; a full redesign case study already exists (section 6) | Strong (case study) | n/a (new path) | GA4 property carries over |
| **Apps: Upkeeply, AI Character Builder** | Upkeeply: PRD + scaffold, "not in active development," Tony likely deleting. AI Character Builder: internal production tool | Medium | None | n/a |
| **Roblox game** | Strategy only, no game built | Medium (`Strategy.md`) | None | n/a |
| **Stock photo/video portfolios** | **Still active, low priority (Tony, 2026-10-12, corrected).** Real, ongoing (if small) income across 14 remaining platforms; Tony isn't actively uploading new work because it's unlikely to meaningfully move the $1,000/mo goal, but existing uploads keep earning | Tracked in the **Stock Portfolio Audit** artifact + `005_Affiliate_Marketing/Stock-Portfolio-Checklist.md` | Figures on file are **stale lifetime totals, not current** — Tony doesn't keep them updated. Historical: Getty $91.34, Shutterstock $32.10, Adobe Stock $29.64, Pond5 $15.00, Pixta $7.17, Dreamstime $5.75, Bigstock $4.50, 123RF $4.79, Depositphotos $3.90, Alamy $3.00; $197.19 lifetime total across all 14. Current monthly income unknown | 🔴 None |
| **Ad campaigns** (planned, not yet run) | **Planned only — none has ever launched (Tony, 2026-10-12).** All entries here are *campaigns to possibly run*, not ad revenue (the old spreadsheet's "Ads" tab name was misleading — nothing in it is income) | None | $0 — no campaign has run | n/a — nothing to connect until a campaign exists |
| **Donations** (Buy Me A Coffee) | Passive "tip jar" link, not actively promoted | None | Unknown, likely $0 | 🔴 None |
| **POD side-stores** (Fine Art America, Threadless) + **Gumroad** (digital, not POD) | **All active but nearly empty, confirmed by Tony 2026-10-12.** Fine Art America and Threadless have a couple of Bored Nomad designs each; Gumroad has zero products listed | None | Negligible — not actively used, intentionally deprioritized while Etsy is the main store | 🔴 None |
| **AI contract work (Mercor)** (newly relevant) | Contracts on file in `009_AI_Jobs/Mercor/` | Reference docs only | Unknown; it is income, but not a business stream | n/a |

### 3b. Per-stream detail and what's missing for the December goal

**YouTube (12 launched channels; `002_Content-Creation/Video_Editor/`)**
- *Real state:* `Video_Editor/CLAUDE.md` says production is still in a manual "trial phase" until "video quality meets monetization standards." Channel bibles (content systems) exist for Anomalous Wild, Neon Parcel, Reimagined Realms, Kingdoms & Conquerors, Glyphary, Polyoculis, Robotto Gato (not launched), Bored Nomad, Uno Mas Creative, Room Portal, Ikigai Digital Studios and Business Origin Stories. **The Brain Blueprint has no channel bible at all** (its folder only holds an empty-looking `Autonomy_Report_Card/`). Production folders exist only for Anomalous Wild (3), Neon Parcel (2 compilations) and Reimagined Realms (5).
- *Business model:* AdSense plus sponsorships; several bibles add affiliate links (Bored Nomad: Amazon, SafetyWing, Airalo; Room Portal: projectors and lighting) or store traffic (Ikigai, Uno Mas).
- *Revenue today:* not recorded anywhere. The 2026-10-06 pull shows **about 7,300 views across all 12 channels in the last 30 days** (Neon Parcel 3,962, Bored Nomad 2,585, Reimagined Realms 564, the rest under 150 each). Neon Parcel's 2.7M lifetime views are mostly in the past.
- **YouTube Partner Program — resolved, 2026-10-12. No channel is monetized (in YPP) yet.** Neon Parcel is closest (highest subscriber count of the twelve) but hasn't cleared YPP's thresholds (1,000 subscribers + 4,000 public watch hours in the past 12 months, or 10M Shorts views in 90 days — Tony's own description of the bar blended the numbers slightly; these are YouTube's actual published thresholds). No channel is close enough on both metrics yet.
- *Missing for December:* real AdSense numbers once/if a channel clears YPP. At ~7,300 monthly views and no channel in YPP yet, ad revenue is not a realistic lever for December. YouTube's faster value toward the goal is still as a traffic driver to stores and affiliate links, not ads.

**The Brain Blueprint (no channel bible — why, clarified by Tony 2026-10-12)**
- *Why there's no bible:* the channel originally ran on an AI-video tool covering psychology/brain-science topics. Tony describes the output as "AI slop" — low engagement, videos that didn't hook viewers — and stopped paying for that service. The channel folder was never fleshed out because the original concept was abandoned.
- *New direction, not yet built:* Tony's plan is to pivot the channel to a recurring-persona format — "an Asian monk" character discussing health topics (gut health, etc.) in videos similar in spirit to a template/A-B-test approach (very similar videos, different enough per-video that the algorithm doesn't flag it as spam/duplicate content). End goal: sell a product, most likely a subscription supplement (e.g. a gut-health pill) — either as a **Digistore24** offer or a found product with a high-enough affiliate commission to justify the production effort. Commission rate is the gating factor: Tony wants a meaningfully high rate before committing real effort here.
- *Status:* concept only, not scoped or built. Not a December lever — flagged for a future phase.

**Skool community**
- *Real state, confirmed by Tony 2026-10-12:* **does not exist yet.** No tutorials have been built to put into a community, so this is downstream of actually producing teaching content first (see Tutorial-Builder reference above). Not a near-term item.

**Etsy POD: Bored Nomad (`005_Ecommerce/POD/`, canonical shop doc now `005_Ecommerce/Etsy-Bored_Nomad/CLAUDE.md`)**
- *Real state:* POD CLAUDE.md: "Active. Publishing new designs and optimizing listings." Store URL `etsy.com/shop/BoredNomad`, fulfilled by Printful (borednomad.com resources page) and Printify + Printful (Etsy CLAUDE.md). Real Printful receipts show up in Xero (receipt automation, 2026-10-10).
- *Business model:* per-product margin on travel-themed wall art, apparel and home decor.
- *Revenue today, quantified, 2026-10-11:* shop verified directly — **157 total sales, 97 active listings, 4.9★ (31 reviews), live since 2020.** Categories: Art Prints, Accessories, Bags/Totes, Coffee Mugs, Home Decor, Hoodies, Leggings, Shirts, Skirts, Stickers, Sweaters. Recurring design themes: Aurora Borealis/Northern Lights, Banff National Park, Tokyo/cyberpunk-anime, Japanese art, plus general humor tees. Fulfilled by two production partners (Chatsworth CA + a second US partner), original designs by Tony (Adobe Fresco/Illustrator, AI-assisted). Xero YTD 2026: $467.00 domestic + $19.50 international Etsy sales, net of a -$69.42 coupon line (section 5) — note this is 2026-only, not lifetime.
- *Docs fixed and merged, 2026-10-11:* real shop data written, the dead `App Building/Obsidian-Vault` path removed from `POD/CLAUDE.md` (pointed to a folder that no longer exists post-rename), and the "Board-Nomad" typo fixed to "Bored Nomad." **Canonical, sole location is now `005_Ecommerce/Etsy-Bored_Nomad/CLAUDE.md`** — Tony's explicit call, 2026-10-11: there should be no `POD/Board-Nomad/` subfolder at all going forward, matching the flat `Etsy-Ikigai/` pattern. The old `POD/Board-Nomad/Etsy/CLAUDE.md` holds nothing unique anymore (its full content is now in the canonical file) and was left in place only because agents can't delete folders — Tony can delete the whole `POD/Board-Nomad/` folder whenever convenient.
- *Etsy route (locked, section 5):* Etsy Open API v3 plus a third-party tool like Listadum, in parallel. This is also to-do #2 (Bored Nomad Etsy store automation).

**Etsy Digital: Ikigai Digital Studios (`002_Channels/011_Ikigai-Digital-Studios/`, shop doc now at `005_Ecommerce/Etsy-Ikigai/CLAUDE.md`)**
- *Real state:* the Ikigai channel bible says "Etsy Store: Active (Ikigai Digital Studio)." Business model is spelled out: digital downloadable wall art, no inventory or shipping, future own-website store "likely LemonSqueezy" to avoid Etsy fees. Tony confirmed 2026-10-11 it is Etsy-only for now.
- *Revenue today, quantified, 2026-10-11:* shop verified directly — **63 total sales, 18 active listings, 5.0★ (4 reviews), live since 2023 (~2.5 years), based Raleigh NC.** Every listing is a $6.50-$8.50 digital download (Art Prints — Trendy, Reimagined, Abstract, Botanical, Food & Drink, Japan Art, Mid Century, Minimalism) — **zero marginal production/shipping cost per sale**, the defining advantage of this stream. Process: mixed media (digital art, photography, collage, hand drawing/painting, gouache, linocut), curated/reimagined vintage and public-domain art, some disclosed generative-AI-assisted designs. Same owner as Bored Nomad (shops cross-link each other's bios).
- *Revenue today, costs:* the store runs Etsy ads. Etsy billing emails for IkigaiDigitalStudio show Tony's card being charged, which per the Etsy/Xero mechanism Tony described only happens when ad spend and fees exceed that period's sales. So in at least one recent period, Ikigai cost more than it earned. Not enough to judge the trend. Open item: unconfirmed whether Ikigai runs through the same Uno Mas Creative LLC Xero org pulled in section 5, or a separate one.
- *Resolves the old "Current vs Planned" conflict:* Etsy Digital is **live** (Ikigai on Etsy). The `Digital_Products` department's "Planned" refers to everything beyond Etsy (Gumroad, own site, guides, email funnels), which really hasn't started.
- *Docs fixed, 2026-10-11:* the previously-empty `005_Ecommerce/Etsy-Ikigai/` folder now has a real `CLAUDE.md` with the data above. `006_Websites/Ikigai_Digital_Studio/` is still an empty placeholder for the future own-site build. Tony named Ikigai as a candidate to push harder; it already has a live storefront and a zero-marginal-cost product, which is exactly the "fast and easy" profile, as long as ad spend is under control. This is also to-do #3.

**Uno Mas Creative POD (TikTok store + Printify pop-up store)**
- *Real state, verified directly 2026-10-11:* TikTok Shop live, fulfilled via Printify. **15 active listings — most titles match the Bored Nomad Etsy catalog, but not all** (Tony corrected an earlier overgeneralization here; at least "Sigma Rizz Retro T-Shirt" doesn't appear on Bored Nomad's Etsy and is likely an Unomas-Creative original — not every listing individually audited). **Only ONE product has ever sold: "Skeleton Skater Sticker for Skateboard and Laptops."** 3 lifetime orders ($2.75, $1.82, $2.57 — ~$7.14 total, ~$6.09 earned after fees). The other 14 listings have zero sales. Fully documented at `005_Ecommerce/Tiktok_Shop-Uno_Mas_Creative/CLAUDE.md`. `005_Ecommerce/POD/Unamoss-Creative/` folder still exists but Tony is renaming it himself (spelling fix, see section 4) — not touched by this plan. The YouTube channel bible frames the brand as a design-tutorial channel for the LLC.
- *Root cause of low views, diagnosed 2026-10-11, corrected after Tony's pushback:* first pass misread an optimizer side-panel as "1 of 9 images, no size chart" — wrong. Checked the actual listing editor directly instead: "Caffeine & Chaos" has **8 of 9 images uploaded, including a real size chart image.** Category search volume is huge (1.4M+ searches for "caffeine chaos shirt") but views are tiny (12). The real, confirmed cause: TikTok's own page shows *"We couldn't detect any size information. Please try another image"* — their automatic text recognition fails to read the uploaded size chart because its "Size Chart" heading is in a decorative cursive font with small measurement text, which breaks OCR. Not a title/keyword problem as Tony suspected — and not a missing-images problem either, as this session first wrongly concluded.

**Fix attempted, then RESOLVED differently by Tony, 2026-10-11 night.** This session tried TikTok's structured "Create size chart" tool (enter measurements as data) and hit two dead ends: a platform-wide Bust-field minimum of 18.9" rejected the real 18.25" S-size measurement, and the UI for adding a custom "Width" column kept breaking. Tony found the actual right tool: TikTok's **"Convert Image to Size Chart"** function, run directly on the existing uploaded image — confirmed working on "Caffeine & Chaos." Full detail and next-day action items: `005_Ecommerce/Tiktok_Shop-Uno_Mas_Creative/CLAUDE.md`. Per-listing audit of the other 14 listings still needed — same fix likely applies to each, not yet confirmed.
- *Signal worth testing:* the one product that sold is a cheap ($2-5), low-friction impulse buy — not full-price apparel like the other 14 listings. Possibly indicates TikTok Shop converts better on low-price/low-consideration items than higher-price apparel, worth more stickers/small items as a test before investing more in the apparel listings there.
- **No documentation of the store business yet. Needs a Tony questionnaire.**

**Redbubble: Bored Nomad**
- *Real state, verified live in the seller dashboard 2026-10-12 (Tony gave standing permission to log in and check his real sales/analytics whenever needed — no need to ask each time):* **active**, 60 designs listed, North Carolina-based account. Shop: `https://www.redbubble.com/people/borednomad/shop` (saved — don't ask Tony for this again).
- *Real earnings, pulled directly from Redbubble's own Earnings Details page (Artist Tools → Earnings details, selectable by month):* **Jul 2026 $0, Aug 2026 $13.54 after fees, Sep 2026 $8.20 after fees.** Matches Tony's own estimate ("$10-20/month, depends") closely. Oct 2026 hadn't posted yet at check time (current month, in progress). No public API; this has to be pulled by logging into the dashboard and reading the Earnings Details page per month — now a known, repeatable path, not a one-time check.
- *Tony's framing:* "makes sales every now and then" — small but real and already monetizing with zero extra effort, unlike several other streams in this plan.
- **Still no workspace folder/doc** — the real numbers above live only in this plan for now. A dedicated `005_Ecommerce/Redbubble/CLAUDE.md` would need a new folder (agents can't create one unasked); flag to Tony if he wants one set up.

**Amazon KDP (`005_Ecommerce/KDP/`)**
- *Real state, confirmed live in the KDP dashboard, 2026-10-12 (signed in with Tony's permission):* **5 titles live**, all paperback journals/notebooks, all submitted 2020-2021 and untouched since: "Notebook Journal: Japanese Edo Style Cover Floral Theme" ($5.99, ASIN B09KDRCYHG), "Journal Paperback: Vintage Japanese Manchurian Crane" ($5.89, ASIN B09KNGCGC5), "The Great Wave off Kanagawa Journal Notebook" ($5.79, ASIN B09KN2LP2L), "Composition Notebook: Japanese Floral Art Cover" ($6.99, ASIN B09K21CC4Y), "Butterfly and Botanical Journal College Ruled Lined Notebook" ($5.89, ASIN B08KPX4P5V, published under "Bored Nomad LLC" rather than "Bored Nomad" like the others). No eBook or hardcover editions linked to any title — paperback only.
- *Real recent royalties, pulled directly from Prior Months' Royalties:* **September 2026: $0.00. October 2026 (partial): $0.00.** Across every marketplace (US, UK, Germany, France, Japan, Canada, and 11 more), 0 KENP reads. The account is **currently dormant** — Tony's "some sales" is real but historical, not recent; nothing has sold in at least the last two reported months. Folder itself is still empty; `DEPARTMENTS.md` points to a `KDP/CLAUDE.md` that doesn't exist.
- *Tony's plan going forward:* expand into other low-content formats — coloring books, activity books — now that AI tooling can help produce interiors faster. Wants help identifying niches with "good search volume, not oversaturated." Explicitly said: lock the tools for this into the plan.
- *Tool suggestions, pulled from what's already bookmarked in the vault (`007_Resource_Library/Tools/Kdp.md` — no need to re-research from scratch):* **Book Bolt** (interior/cover design + keyword and niche research, boltdesigner.io), **Publisher Rocket** (Amazon keyword/category research, one-time purchase model, publisherrocket.com), **Helium 10** (broader Amazon seller toolkit — keyword research, rank tracking — helium10.com). Of the three, Publisher Rocket and Book Bolt are the KDP-specific niche/keyword tools; Helium 10 is the more general (and more expensive, subscription) Amazon toolkit. **Recommendation: start with Publisher Rocket or Book Bolt** for niche/keyword validation before committing to Helium 10's subscription cost — neither is connected or purchased yet, this is a recommendation, not a locked decision.
- *December fit:* Tony flagged this himself as **not a December push** — KDP grows organically on Amazon search rather than through social promotion, and takes longer to compound than a stream he can actively drive traffic to. Keep it as a background/long-term stream, not a $1,000/mo lever.
- *Analytics:* no seller-facing API for KDP; Amazon's own KDP Reports dashboard is manual-export only. Not connected.
- **Still needs a real workspace doc** (`005_Ecommerce/KDP/CLAUDE.md` is empty) — book titles, niches, and sales-to-date aren't recorded anywhere yet beyond this plan.

**Amazon Merch on Demand (`005_Ecommerce/Amazon_Merch/`)**
- *Real state, confirmed by Tony 2026-10-12:* **planned, deliberately not started.** No approved Merch on Demand account exists yet. Tony is intentionally waiting on this one — he wants Bored Nomad POD and Ikigai Digital Studios producing more consistent income first, rather than spreading effort across a fourth POD-style stream before the first few are solid.
- *December fit:* explicitly not a near-term lever — this is a "later, once other streams are proven" stream by Tony's own sequencing logic, not a documentation gap.

**Affiliate marketing (`005_Affiliate_Marketing/`)**
- *Real state:* the department brief is the most complete business doc in the workspace: an agent role, compliance-first workflow, and a list of **18 active programs**: Amazon Associates, Impact, TravelPayouts, Expedia, Bookaway, GetYourGuide, Hostelworld, JR Pass, Klook, SafetyWing, Stay22, Digistore24, 12Go, Higgsfield, Magnific, OpusClip, VidIQ, TikTok Shop Affiliate. Note it covers AI/creator tools too, not only travel.
- *But:* all 17 per-program folders are empty. No `Links.md` link catalogs, no `Performance/` exports. The brief's target state (Airtable link catalog) isn't built.
- *Revenue today:* borednomad.com has "genuine affiliate integration" (March 2026 site audit) and its resources page carries affiliate links (Astra theme, Cloudways, ConvertKit, Merch Titans, travel programs). GA4 shows ~222 active users per 28 days on the site. Commissions are not recorded anywhere.
- *Missing for December:* per-program earnings (one manual check of each dashboard would do for a baseline). At ~222 users/month, travel affiliate income from the site is likely small today; the rebuild (section 6) won't move it much before December because search rankings take months. AI-tool affiliates (Higgsfield, OpusClip, VidIQ, Magnific) could fit Robotto Gato or Neon Parcel audiences faster; unexplored.

**TikTok Shop affiliate (`005_Affiliate_Marketing/Tiktok_Shop_Affiliate/`)**
- *Real state:* the Neon Parcel TikTok Shop Creator pipeline was built and validated 2026-07-12. Two products produced: Colorsmart Pens (3 cuts) and Glass Guard (1 cut). Full compliance system (ledger, freshness log, 18 TikTok policy docs, per-video transcript and vision scans).
- **Resolved, 2026-10-12 — confirmed by Tony: both went live with product links attached.** Videos are up on `https://www.tiktok.com/@neonparcel`. **No commissions have been earned yet** — live, but not converting so far. The production system already exists, so this stays a candidate for "fast if it starts converting" rather than something that needs to be rebuilt.
- *Next real step, not yet done:* check per-video performance (views, clicks) on the actual TikTok account to see whether the lack of commissions is a traffic problem or a conversion problem — different fixes for each.

**Whop clipping (`002_Content-Creation/Whop_Clipping/`)**
- *Real state, confirmed by Tony 2026-10-12:* **was active, now paused.** Participated in a couple of clipping campaigns (unnamed — not currently active in them), earned roughly **$30-40 total**. Put in real time but hadn't gotten good at it yet when he stopped.
- *Plan going forward:* wants to come back later with a more automated clipping workflow, not the manual approach he tried. Explicitly not scoped or scheduled — "currently on pause," not a December lever.

**Social media marketing (`002_Content-Creation/Social_Media_Marketing/`)**
- *Real state:* **Planned**, "no active posting pipelines yet." Fashion/clothing niche on Pinterest and Instagram.
- *Adjacent:* `001_Architecture/Plans/AI-Fashion-Affiliate-Implementation-Brief.md` (2026-10-07) is a detailed brief for an AI-character fashion carousel workflow monetized through Amazon Associates. It is effectively this department's business model, but not adopted or built. Its compliance cautions (no fake "I tried this" claims, human review before publishing) are worth keeping if it's ever picked up.

**Digital products (`005_Ecommerce/Digital_Products/`)**
- *Real state:* **Planned**, "setup and product design stage." Distribution plan: Gumroad, own site (Next.js + Sanity + Lemon Squeezy), email funnels. Nothing built.
- *Clarified by Tony 2026-10-12:* Gumroad was conceived as a fallback distribution channel for something like a digital course or PDF, meant to be sold through Beacons or a Stand Store page. **Tony now believes Beacons and Stand Store can sell directly themselves**, which would make the separate Gumroad step unnecessary — Gumroad is "there in case I need it," not the current plan. Worth confirming Beacons/Stand Store's direct-sale capability before building anything on Gumroad.
- *Related ideas in the to-do list:* Tutorial-Builder tiered packaging (free PDF, a lead magnet "gated behind joining his Skool community," paid Skool tier) and Agent-OS as a sellable deploy template. Both unscoped.
- *For December:* Tony named digital products and ebooks as a candidate. The fastest version probably reuses an existing storefront (Ikigai's Etsy shop, Beacons, or a Stand Store page) rather than building the planned Next.js site or Gumroad catalog first. That's an observation for the scoring step, not a decision.

**POD side-stores (Fine Art America, Threadless, Gumroad)**
- *Real state, confirmed by Tony 2026-10-12:* **all active accounts, but nearly empty.** Fine Art America and Threadless each have "a couple" Bored Nomad designs; **Gumroad has zero products listed today** (see Digital products above — it's held as a future fallback channel, not in use). The original intent for Fine Art America/Threadless/Redbubble was to cross-post Bored Nomad's existing art to more sales channels.
- *Why they've stayed empty:* Tony says it's purely bandwidth — Etsy is the main store, and manually re-listing the same designs across multiple platforms is tedious. He'd like this automated eventually (one upload → pushed to every POD channel), but confirmed this is **not a near-term priority** — he's not building that automation before the December goal.
- **Needs a workspace doc eventually** (none exists); low priority given Tony's own sequencing.

**Email list**
- *Real state, confirmed by Tony 2026-10-12:* **does exist.** Platform: **ConvertKit (Kit)**, roughly **1-2 subscribers**. There may also be a separate list through **Beacons**, and a **Pensight** page — Tony isn't sure which brand/channel each is tied to (possibly Neon Parcel on Beacons, Reimagined Realms on Pensight, unconfirmed). Needs a follow-up pass to map Beacons/Pensight accounts to channels before this can be tracked properly.
- *Why it's near-zero:* no lead magnet or offer exists yet to drive signups, and Tony says the signup form isn't prominent on borednomad.com, which he describes as currently broken/non-functional — reinforces the website rebuild (section 6) as a prerequisite for this stream mattering.
- **Still needs a real workspace doc** — platform, account ownership per channel, and subscriber counts aren't recorded anywhere but this plan yet.

**Apps and games (`003_Apps/`, `004_Games/`)**
- *Upkeeply:* real PRD (home-maintenance chatbot, revenue via Amazon/Walmart affiliate links on replacement parts) plus a Vite scaffold; "not yet in active development." Tony has said he's likely deleting it. Not a December path.
- *AI Character Builder:* an internal tool for making character sheets for video production. No monetization model in its docs. Note: its CLAUDE.md describes Docker/React source files, but the folder only holds that CLAUDE.md and an `.rtf`; the code isn't there (may live elsewhere).
- *Roblox:* `Strategy.md` sets out a clear model (simulator/tycoon game, Robux via game passes/developer products, cash-out via DevEx at roughly 100,000 Robux ≈ $350, 30,000 Robux minimum). No game exists yet. At that rate $1,000/month needs roughly 285,000 Robux a month. Not a December path.

**Stock photo/video portfolios**
- *Real state, clarified by Tony 2026-10-12, corrected same day:* **still an active, earning stream** — not reference-only as this plan first said. Came from an old Numbers (Excel-equivalent) spreadsheet with separate tabs per income category; stock photography was its own tab. Tony has mostly stopped uploading new work because it's unlikely to meaningfully move the $1,000/mo December goal, but existing uploads keep earning passively.
- *Current state, 2026-10-12:* started as a 19-portfolio list pulled from the old spreadsheet; Tony removed 5 that never earned anything and were never really started (Canstock, EyeEm, Pexels, Photocase, Pixabay — Envato is in the remaining 14, also flagged as never actually started). **14 remain**, tracked in the **Stock Portfolio Audit** artifact and `005_Affiliate_Marketing/Stock-Portfolio-Checklist.md`.
- *Numbers caveat:* every dollar figure on file is a **stale lifetime total** — Tony doesn't keep it updated, so don't quote these as current monthly income. Current monthly income from stock is unknown and untracked; low priority to connect given it's a small, low-effort-ceiling stream.
- *Historically strongest:* Getty Images ($91.34 lifetime) and Shutterstock ($32.10).

**Ad campaigns (planned, not yet run)**
- *Real state, clarified by Tony 2026-10-12, corrected same day:* **none of these are ad revenue — they're all planned campaigns, not yet launched.** Carried over from the old Numbers spreadsheet's "Ads" tab (a misleading tab name; nothing in it was ever income). Candidates: **Facebook Ads, Microsoft Ads, TikTok Ads, Pinterest Ads** (Pinterest added 2026-10-12 — Tony's likely use case: advertising POD products and/or digital ebooks). No accounts set up, no IDs assigned, no budget, no campaign has ever run.
- **Resolved, 2026-10-12:** the old "Paypal (Ad Revenue)" entry was removed — confirmed a duplicate of the "Paypal.me" donation link (`https://paypal.me/borednomad`), not ad revenue at all, just mis-tabbed in the old spreadsheet.
- *Missing to actually use this stream:* if/when a campaign is built, this plan needs the ad account IDs, pixel/conversion tracking setup, and a budget per platform — none of that exists yet. Not a December lever until a campaign is deliberately started.

**Donations (Buy Me A Coffee)**
- *Real state:* a passive tip-jar link, not actively promoted anywhere documented. Likely near-zero income. Not pursued further unless Tony wants to promote it.

**AI contract work (Mercor; `009_AI_Jobs/`)**
- **RESOLVED, 2026-10-11 — excluded from the $1,000/month goal.** Tony is actively trying to phase Mercor out (new restrictions: no VPN use, must be physically in the US) — he does not want it counted or treated as part of this plan's strategy.

`008_Investments/` is personal investing, not business income, and is left out of this plan.

**Ecosystem (root CLAUDE.md):** content (video + social) → audience → affiliate clicks + store traffic + digital product sales → email list → repeat revenue. The video engine is the top of the funnel.

### 3c. Documentation coverage at a glance

**Real documentation describing the business:**
- YouTube channels (11 channel bibles), Video_Editor department
- Affiliate marketing department brief, TikTok Shop affiliate system
- Ikigai Digital Studios business model (inside its channel bible)
- Bored Nomad website (March 2026 redesign case study)
- Roblox strategy, Upkeeply PRD, AI Character Builder

**Thin: a stub CLAUDE.md that states intent, with no real business detail (status, products, numbers):**
- Etsy POD Bored Nomad, Amazon Merch, Whop clipping, Social media marketing, Digital products

**No folder/doc yet, but now answered — real info lives in this plan only (section 3b), folders still need to catch up:**
- Amazon KDP (empty folder; real state: active, 4-5 books live)
- Redbubble (no folder; real state: active, real monthly earnings pulled 2026-10-12)
- Email list (no folder; real state: ConvertKit, ~1-2 subscribers)
- Stock photo/video portfolios (tracked in a separate artifact/checklist, not a department folder; real state: active, low priority)
- The Brain Blueprint YouTube channel (no channel bible; real state: old concept abandoned, pivot concept not yet built)
- Fine Art America, Threadless, Gumroad (no folder; real state: active accounts, nearly empty, deprioritized)

**Still genuinely undocumented (not answered yet):**
- Per-program affiliate details (17 empty program folders under `005_Affiliate_Marketing/`)
- Beacons/Pensight account-to-channel mapping (which list belongs to which brand)

---

## 4. Known doc inconsistencies (flagged, not fixed)

None of these were edited in this pass. Fix them when the file is next edited for another reason, or ask Tony if he wants them fixed now.

1. **"Board-Nomad" is a typo. The correct spelling is "Bored Nomad"** (Tony, 2026-10-11: someone is *bored*, the monotony is getting to them). Root `CLAUDE.md`'s Departments table, Revenue Streams table and Vault Structure line say "Board-Nomad." The typo also appears in folder names (`005_Ecommerce/POD/Board-Nomad/`, `002_Content-Creation/Video_Editor/002_Channels/008_Board-Nomad/`), in `005_Ecommerce/POD/CLAUDE.md`, in front-matter tags (`board-nomad`) and in to-do #2's title. Doc text can be corrected freely. **Folder renames need Tony's approval and a reference check first** (scripts, the Seedance gate config, YouTube token labels and graphify outputs may reference the current paths).
2. **Brand spelling — FULLY RESOLVED, 2026-10-11.** Two distinct, intentionally different names, confirmed by Tony: **"Unomas-Creative"** is the brand/store name (POD, TikTok Shop, Etsy-adjacent work); **"Uno Mas Creative LLC"** is the separate legal entity name (Xero, section 5) — not a typo, not meant to match. Brand spelling fixed in root `CLAUDE.md`, `POD/CLAUDE.md`, `Etsy-Bored_Nomad/CLAUDE.md`, and `Tiktok_Shop-Uno_Mas_Creative/CLAUDE.md`. Tony is renaming the `005_Ecommerce/POD/Unamoss-Creative/` folder himself. A wider spelling cleanup remains outside this plan's scope: several files under `007_Resource_Library/POD_Prints/` and the YouTube channel's own content docs (folder already correctly named `009_Unomas-Creative/`) still use "Unamoss-Creative" in filenames and text — not touched here, flagged for a dedicated pass if Tony wants it.
3. **Root `CLAUDE.md` and `BUSINESS_CONTEXT.md` mark Whop clipping, Amazon Merch and Social media marketing as "Current" revenue streams.** Their own folders say Planned/not started. Per Tony's rule, the folders win; the summary tables are out of date.
4. **Amazon KDP is marked "Active"/"Current" with nothing in its folder** (and `DEPARTMENTS.md` points to a `KDP/CLAUDE.md` that doesn't exist). Can't be resolved from docs; in the questionnaire.
5. **Duplicate Etsy folders — RESOLVED, 2026-10-11.** `005_Ecommerce/Etsy-Ikigai/CLAUDE.md` and `005_Ecommerce/Etsy-Bored_Nomad/CLAUDE.md` are the sole canonical homes for their respective shops (Tony's explicit call — no `POD/Board-Nomad/` subfolder should exist going forward). The old `005_Ecommerce/POD/Board-Nomad/Etsy/CLAUDE.md` still physically exists with a pointer note (agents can't delete folders), holding nothing unique — safe for Tony to delete the whole `POD/Board-Nomad/` folder whenever convenient. Future store-automation work for either shop goes in the `Etsy-<Brand>/` folder.
6. **Stale paths in every department CLAUDE.md:** they tell agents to read `/Users/tonymacbook2025/Documents/App Building/Obsidian-Vault/...`, which no longer exists (the workspace was renamed to Agent-OS). `DEPARTMENTS.md` (last updated 2026-04-04) has the same stale "App Building" paths.
7. **Root CLAUDE.md's Vault Structure section** points to `002_Brands/`, which doesn't exist at the workspace root.

---

## 5. Analytics connection status (as of 2026-10-11)

Verified live in a Google Chrome session on 2026-10-11 unless noted.

**YouTube: live.** Data + Analytics API working for all 12 launched channels (Robotto Gato excluded, not launched). Script: `001_Architecture/Scripts/youtube_analytics_pull.py`. Gap: it pulls views, subs, watch time and engagement, not revenue. Adding estimated revenue/RPM would need the `yt-analytics-monetary.readonly` scope (not granted today) and a re-login per channel. Still an open question for Tony (section 8).

**Google Analytics (GA4): live for one property only.** "Bored Nomad - GA4" (borednomad.com), under info@borednomad.com, ~222 active users per 28 days at check time. Not pulled into the workspace by any script. Still an open question for Tony (section 8).

**Etsy: route decided (Tony, 2026-10-11). Locked plan, not an open question:**

- **Pursue both in parallel:** (1) apply for the **Etsy Developer API (Open API v3)**, and (2) use a **third-party tool like Listadum** (to-do shortlist #24) for listing automation, e.g. auto-uploading listings.
- Same wording as `001_Architecture/API_Directory.md` (Google Analytics and Etsy Open API v3 rows, updated 2026-10-11).
- The Open API v3 registration (to-do shortlist #19, score 82) serves both analytics and the store automation items (to-do #2 Bored Nomad, #3 Ikigai Digital Studios).
- GA4 can never track Etsy shop pages: Etsy doesn't let sellers install tracking scripts, and its old Universal Analytics setting was removed and never replaced for GA4. Tony confirmed it isn't in Shop Manager. Locked, don't revisit.

**Xero (Uno Mas Creative LLC): real baseline pulled, 2026-10-11 — the most important number in this plan.** Via browser (`reporting.xero.com`, logged in as Tony). Report: Income Statement (Profit and Loss), year to date, Jan 1 – Oct 11, 2026:

| Line | Amount |
|---|---|
| Total Income (Etsy Sales Domestic/International, Media Licensing, Product Revenue, net of Etsy Coupon) | $509.09 |
| Cost of Goods Sold (POD Production Cost) | $273.92 |
| **Gross Profit** | **$235.17** |
| Total Operating Expenses (Advertising & Marketing $391.07, Bank Fees $247.92, Etsy Advertising $52.88, Etsy Fees $67.93, Mailbox & Business Address $149.95, **Software & AI Tools $1,470.38**, Telephone and Internet $196.00, Website & Hosting $196.68) | $2,772.81 |
| **Net Income (YTD, ~9.3 months)** | **-$2,537.64** |

**This changes the $1,000/month goal's starting point.** Uno Mas Creative LLC is running a net loss, not break-even — roughly -$273/month average YTD. "Software & AI Tools" at $1,470.38 is more than half of all operating expenses and the single biggest lever for cutting the loss, independent of growing revenue. **Before scoring streams on "fastest path to $1,000/mo profit," the plan needs to account for this existing burn rate** — $1,000/mo net profit by December means closing an approximately $1,273+/month gap (current average monthly loss + the $1,000 target), not just adding $1,000 of new revenue on top of zero.

**Monthly breakdown, pulled 2026-10-11 (same report, "Current fiscal year by month"):**

| Month | Income | Total Expenses | Net Income |
|---|---|---|---|
| Jan–May 2026 | $0 (dormant — no activity) | $0 | $0 |
| Jun 2026 | $16.24 | $491.74 | -$502.38 |
| Jul 2026 | $31.04 | $681.54 | -$650.50 |
| Aug 2026 | $6.50 | $769.54 | -$763.04 |
| Sep 2026 | $20.04 | $499.68 | -$479.64 |
| Oct 2026 (partial, through Oct 11) | $435.27 | $330.31 | **-$142.08** |

**The trend is improving, not flat or worsening.** The loss peaked in August (-$763.04) then dropped sharply in September and especially October. Two things are driving October's improvement: (1) real income jumped to $435.27 — mostly $441.00 in Etsy Sales (Domestic) — vs. $6-31/month in prior months; (2) "Software & AI Tools" expense dropped from $568.37 (Aug) to just $72.86 (Oct), suggesting a subscription cut already happened. If October's pace (-$142.08 over 11 days) held for a full 31-day month, the loss would be roughly -$400 — a meaningfully smaller gap to close than the YTD average suggested.

**Revised framing for the $1,000/mo goal:** the gap to close is shrinking on its own, likely from recent cuts plus the Etsy sales uptick — worth identifying what specifically changed in October (which subscriptions were cut, what drove the Etsy sales jump) since repeating/extending those changes could be the single fastest lever toward December, before even considering new revenue streams.

Open items from this pull: (1) this P&L is for Uno Mas Creative LLC only — confirm whether Ikigai Digital Studios, Board-/Bored-Nomad, and other brands run through the same LLC/Xero org or separate ones; (2) a line-item breakdown of "Software & AI Tools" would show which specific subscriptions are still active and which were just cut — worth a full audit; (3) what specifically drove the October Etsy sales jump ($441 domestic vs. ~$0-20/month prior) — worth understanding and repeating if possible.

**Xero MCP server (official, Xero-published) — considered and deferred, 2026-10-11.** Tony recalled a saved tutorial on Xero's own `xero-mcp-server` (full read/write API access via Claude Desktop, ~$5.45/month Xero-billed fee). Confirmed never actually installed in this workspace. Decision: not worth it yet for occasional P&L pulls — browser login works fine. Logged with pros/cons on the to-do list (`001_Architecture/Ongoing-Agent-OS-To-Do-List.md`, new "Flagged, not prioritized" section) for a future revisit, e.g. if monthly/scheduled Xero pulls become a real need.

**Xero: an existing income ledger the plan didn't use before (new finding, 2026-10-11).** Tony's Uno Mas Creative LLC Xero is live (the receipt automation runs against it daily) and has an **Etsy integration that already books Etsy sales, ad spend, listing and service fees automatically**. Payouts land in Relay or Mercury, which are bank-fed into Xero. That means Xero likely already holds real monthly income for every stream that pays into those accounts (Etsy, and possibly AdSense, KDP, affiliate and Redbubble payouts), without connecting each platform one by one. Two ways to read it, neither built:

- By hand: Tony runs a Profit and Loss report in Xero for the last few months. Fastest possible baseline.
- Scripted: the existing Xero tool already requests `accounting.banktransactions.read` and `accounting.invoices.read`; a P&L report would also need `accounting.reports.read`, a new scope that needs Tony's approval.

Either way this could give a real "where am I today vs $1,000" baseline within a day, before the Etsy API or any affiliate dashboards are connected. It would also suit the "what month counts" measurement in section 2.

**Google Analytics cleanup log, 2026-10-11** (all under info@borednomad.com, all moved to trash by Tony):

| Trashed GA account | Why it was dead |
|---|---|
| Bored Nomad Redbubble | GA4 property with zero data streams ever configured. Moot anyway: Redbubble only accepts the old Universal Analytics ID format, which Google stopped processing in July 2023. |
| Bored Nomad Youtube | Same empty shell. Also moot: that YouTube channel's ownership moved to the Fulcrum SF account, and YouTube is covered by the YouTube Analytics API. |
| borednomad.etsy.com | Had a real data stream pointed at https://www.etsy.com/shop/borednomad but received zero data, because Etsy blocks seller tracking scripts. |

**Locked conclusion:** GA4 cannot track Etsy or Redbubble marketplace shop pages, now or later. Don't revisit.

**Everything else** (KDP, Merch, Whop, Redbubble, Pinterest, email, each affiliate dashboard): not connected, mostly not investigated. The Xero route above may make most of them unnecessary for the December baseline.

**Housekeeping, resolved:** the first draft noted that `API_Directory.md` was out of date on Google Analytics and Etsy. It has since been updated (GA row 🟡 with the cleanup and the Etsy finding; Etsy Open API v3 row records Tony's both-routes decision). The two files now agree.

### 5b. Connection potential per stream (researched 2026-10-12)

Tony asked (2026-10-12) to know, for every platform, whether an API or MCP could feed real numbers to Claude instead of browser checks. Research pass done: vendor docs, npm, and the claude.ai connector directory. **Nothing new was connected.** Full detail, with the exact setup step for each, is in `001_Architecture/API_Directory.md` ("Connection potential" section). Per-item tags now show in the **Affiliate & Referral Audit** and **Stock Portfolio Audit** artifacts. Locked decisions (Etsy route, Xero route, GA4 scope question) are unchanged and only cross-referenced here.

**Two different things an affiliate API can do (deliberate distinction, added 2026-10-12).** Every affiliate program gets two separate ratings, because they're often different APIs on the same platform:

1. **Earnings (analytics):** can Claude pull clicks, bookings and commissions automatically? That's the table below.
2. **Content links (automation):** once an article is written, can Claude find the *specific* thing the article mentions and attach Tony's tracked link to that exact page? Tony's target workflow: write the post (e.g. "things to do in Cambodia" for borednomad.com) → spot each product or service it mentions → query the platform's search or link API → get the specific item → insert the right affiliate link. A static link (SafetyWing, a referral code) can't do this; it's the same link in every article.

Concrete examples from the research: **GetYourGuide** — its Partner API searches individual tours ("Angkor Wat") and returns each tour's page, but only issues keys above 100,000 monthly visits, so for now a tool finds the tour page by web search and tags it with Tony's partner ID (works today). **Amazon** — the Creators API's product search returns specific products with tagged links; ready once Tony adds his key, with the credential-format and 10-sales-per-marketplace caveats in `API_Directory.md`. **Hotels** — Stay22's Allez links turn a hotel name or address into a tracked Booking.com/Expedia/Hotels.com/Vrbo/Agoda link with no key at all, and Travelpayouts' partner links API turns a specific Booking.com hotel page into a tracked link (TP's own hotel search, Hotellook, shut down October 2025). Full per-platform table: `API_Directory.md` → "Content-link automation"; per-item ratings: the Affiliate & Referral Audit artifact (second "Links" badge on every row).

This is the design target for a future affiliate-link injection tool. `005_Affiliate_Marketing/CLAUDE.md` already describes the workflow ("Content Creation with Affiliate Injection", step 4 "Inject links", and "Dynamic Content Blocks") but assumed links come from static `Links.md` files and only gestured at "if an API key exists (Expedia, Hostelworld, etc.)". This research fills that gap: which platforms can actually return a specific item (Stay22, Travelpayouts, Impact, Amazon), which only take a deep-link formula (GetYourGuide, Klook, 12Go, Hostelworld, Bookaway), and that the brief's two named examples turned out weaker than assumed (Expedia's creator API is undocumented; Hostelworld's property API needs approval). Nothing is built.

**Tony's decisions on content links (2026-10-12, sixth pass).**

- **Write first, link after (locked).** Tony doesn't write around affiliate links. Content is written normally; a separate pass afterwards (Stay22's own tooling on the page, or Claude scanning the finished draft) finds mentions worth turning into links. Links are never chosen before or during writing.
- **Stay22 and Travelpayouts are the default systems**, with Impact as the third hub. Tony is network-agnostic: "whatever's easiest and whatever's going to make me the most money."
- **Consolidation direction: 2-3 hub networks, not 50 one-off programs.** Tony is open to dropping one-off programs a hub already covers. Flagged as redundant: **Klook, Hostelworld, GetYourGuide** (all Travelpayouts brands), **Bookaway** (same parent company as 12Go, Travelier, with near-identical SE Asia routes; not a TP brand) and **Expedia** (Stay22 routes to it). **12Go is kept deliberately** (researched 2026-10-12): Stay22 has no bus/train/ferry booking at all, GetYourGuide/Klook only sell headline routes, and Omio/Busbud inside TP are thinner backups (Busbud partly resells 12Go). 12Go is itself a TP brand, so keeping it doesn't conflict with consolidation. Not cancelled; Tony decides when. Check hub approval, commission rate and live links before closing any. Full table and caveats: `005_Affiliate_Marketing/CLAUDE.md` → "Direction Update — 2026-10-12".
- **Impact Publisher Tag checked:** it rewrites plain brand hyperlinks already on a page into Impact tracking links. It does not create links from text, and it only covers Impact brands. Useful as a safety net on the rebuilt site, not as the linking pass. Detail is in the same section.
- **Travelpayouts Drive checked, and it's the real candidate for write-first-link-after.** It's a free script that scans finished English travel posts and turns phrases into affiliate links by itself. It also adds hotel/tour recommendation blocks and rewrites existing direct/Partnerize/plain brand links into Travelpayouts links for brands approved inside TP. **Targeted Offers (the lower-commission pop-under) and all of Drive's algorithmic brand recommendations stay at default, on purpose — confirmed by Tony, 2026-10-12: he doesn't care about the commission difference or which specific brand (Trip.com vs Agoda, etc.) gets recommended.** Not a setting to revisit. Detail and a side-by-side with Impact's tag: `005_Affiliate_Marketing/CLAUDE.md`, section (c2).
- **Script compatibility confirmed, 2026-10-12:** Drive, Stay22, and Impact's Publisher Tag can all run on the same rebuilt site without conflicting — browsers isolate third-party scripts, and Impact's brands (NordVPN, M1, Tenba, Envato) don't overlap with what Drive/Stay22 cover (hotels, tours, flights) anyway. Only real overlap risk is Drive vs. Stay22 claiming the same hotel/tour brand — exclude the brand in one of them if it happens. Load Drive's script first in the page, per Travelpayouts' own guidance.
- **Consolidation: not happening now.** Tony confirmed 2026-10-12 he's keeping every existing affiliate program active; new content just routes through Stay22/Travelpayouts/Drive instead of one-off logins, and old programs get dropped gradually, only if/when he stops wanting to manage them — not on any schedule. **12Go is a deliberate keep**, confirmed by research 2026-10-12: it covers Vietnam/Cambodia small-town bus, ferry and van routes (e.g. Kratie→Stung Treng, Ha Tien→Phu Quoc) that Stay22 can't reach at all and other hubs only partly cover. Full detail: `005_Affiliate_Marketing/CLAUDE.md`, section (d).
- **The `emrld.cc` script question is moot.** Tony confirmed 2026-10-12 the website rebuild carries over **no old code, HTML, or scripts** — only text and images from existing posts, rebuilt into new markup. Whatever `emrld.cc` turns out to be, it doesn't survive the rebuild; Drive (and Impact's tag, if used) get installed fresh and deliberately on the new site. The "check before deleting" caution below only matters if the *current* live site gets touched before the rebuild ships.

**Fallback revenue signal when a platform has no sales API at all.** For streams with no earnings API (SafetyWing, most referral codes, Amazon Associates earnings), bank and payment data can still show whether money is actually arriving, an indirect "is this stream making anything" check. Xero already covers this for Relay and Mercury (both bank-fed into Xero). Mercury also has a read-only API and official MCP, PayPal has Transaction Search and an official MCP, Wise has balance statements by token (US business accounts), and Relay has no public API. Detail: `API_Directory.md` → "Bank & payment data".

**Can be connected, ranked by value for the December goal:**

| Stream | Path | What Tony has to do |
|---|---|---|
| Affiliate (Impact network: Envato, M1, Tenba, NordVPN, Going, Skyscanner) | **Official Impact MCP** (`mcp.impact.com`, works in Claude Code) | Enable MCP access on the Impact account, approve OAuth |
| Affiliate (Travelpayouts: Airalo, Booking.com, Omio) | Travelpayouts API (token) | Copy API token from TP profile |
| Affiliate (Stay22, Hostelworld/Expedia via Partnerize, Kit via PartnerStack) | Each has a reporting API with a self-serve key | Generate a key in each dashboard |
| Etsy (Bored Nomad, Ikigai) | **Route already locked** (Open API v3 + Listadum). New info only: Etsy's Seller App tier approves own-shop apps within minutes | Register one Seller App per shop (already on to-do #2/#3) |
| TikTok Shop seller (Unomas-Creative) | TikTok Shop Open API, Custom app in Partner Center (US) | Register as seller in-house developer, authorize the shop |
| Printful, Printify | API tokens, instant | Generate tokens (mostly duplicates what Xero already books) |
| Email (Kit) | **Official Kit MCP**, one-click in claude.ai connectors | Add connector; tools need a paid Kit plan. Low priority at ~1–2 subscribers |
| GA4 | Google's official GA4 MCP (local, read-only) | Only if Tony answers open question #9 with "yes, script it" |

**Ready the day a campaign exists (nothing to read today):** Meta Ads (official MCP, `mcp.facebook.com/ads`), TikTok Ads (official MCP in claude.ai connectors), Microsoft Ads (official read-only MCP pilot), Pinterest (API v5 Trial access covers analytics and ads; official Pinterest MCP announced but not launched yet).

**Permanently browser-only (no public API exists):** Amazon KDP (confirmed: no reporting API, Selling Partner API excludes KDP), Redbubble (confirmed), Amazon Associates earnings (the new Creators API is product data only and needs 10 sales/month), Fine Art America and Threadless seller stats, 13 of 14 stock portfolios (only Envato has an author API, and it was never really used), and essentially all 39 personal referral codes. For these, a browser login on Claude in Chrome (as done for Redbubble) or Xero's bank-fed income lines stay the real data source.

**Housekeeping found during the research:** `TOOLBOX.md` lists a `META_GRAPH_API_KEY`, but that variable doesn't exist in `~/.env-secrets`. Treat Meta Graph as not connected until Tony confirms.

---

## 6. Bored Nomad website rebuild

**What:** move borednomad.com (WordPress + Elementor on Cloudways hosting, carrying the live "Bored Nomad - GA4" property) off WordPress.

**Why (Tony, 2026-10-11):** he dislikes WordPress: bloat, plus the security and update burden.

**Target stack:** Cloudflare (Cloudflare Pages) plus a lightweight framework. Tony's requirements: fast, lightweight, not bloated, easy to keep secure, easy to update.

**Existing groundwork (found 2026-10-11):** a full redesign case study already exists: `002_Content-Creation/Video_Editor/002_Channels/008_Board-Nomad/Bored_Nomad_Case_Study/CASE-STUDY.md` (prepared 2026-03-31). It audits the current site (no hero, buried calls to action, a broken link to an old Cloudways staging URL, unconfigured GTM, an unknown `emrld.cc` script throwing errors) and proposes a component structure, author bio/trust blocks for affiliate clicks, and a newsletter component. Start the rebuild scoping from this file.

**Framework name: RESOLVED, 2026-10-11 — Tony confirmed he meant Astro.** Tony's description ("a website programming language... I believe Cloudflare bought into it or something like that") matches real, verified news: **Cloudflare acquired The Astro Technology Company on 2026-01-16**, and Astro continues as open source under MIT license. Astra (the WordPress theme the current site uses) was a coincidental naming overlap, not what Tony meant. Target framework for the rebuild is **Astro + Cloudflare Pages**, matching the March 2026 case study's proposal and the workspace's existing `astro-cloudflared-website-builder` skill — use that skill when the rebuild is actually scoped/built.

**Scope confirmed, 2026-10-12: this is a from-scratch rebuild, not a migration.** Tony: no old code, HTML, or scripts carry over — only text and images from existing posts, and even those get rebuilt into new markup. Affiliate-automation scripts (Travelpayouts Drive, Impact's Publisher Tag if used) get installed fresh and deliberately on the new site, not inherited.

Other build items to plan when this gets scoped (listed, not decided):

- Keep the "Bored Nomad - GA4" property and its history by putting the same measurement ID on the new site.
- URL redirects so existing search rankings survive, even though the content/markup itself is rebuilt from scratch, not migrated as-is.
- Carry over the newsletter signup and whatever email platform sits behind it (unconfirmed, section 3).
- Cloudflare MCP connector exists but isn't authenticated yet (API_Directory).
- A "BoredNomad WooCommerce Website" Google Cloud project exists with no credentials (API_Directory delete candidate). The current site's old staging URL also contains "woocommerce." Confirm whether any store features on the current site need replacing.
- `006_Websites/Bored_Nomad/` exists (empty) as the obvious home for the rebuild.

**Business model: a travel affiliate website.** All content funnels toward travel affiliate links. Programs Tony named on 2026-10-11:

| Program / network | Note |
|---|---|
| Impact | Affiliate network (in the affiliate department's program list) |
| Stay22 | Accommodation/travel affiliate (in the program list) |
| TravelPayouts | Travel affiliate network (in the program list) |
| Hostelworld | **RESOLVED, 2026-10-11 — confirmed by Tony.** A travel affiliate site that recommends hostels, exactly matching Hostelworld. Already in `005_Affiliate_Marketing/CLAUDE.md`'s active program list, has its own folder there, and appears on borednomad.com's resources page. |
| Amazon Associates | In the program list |
| "And many more" | The affiliate department lists 18 programs (section 3); add rows as Tony names them |

**Revenue status and the December goal:** the rebuilt site is a new revenue path that isn't live. The current site has real affiliate links but small traffic (~222 users/28 days). A rebuild's payoff comes through search, which takes months, so it is a long-term play that likely contributes little by December. That doesn't make it wrong; it just isn't the fast lever.

---

## 7. First read against the December goal (evidence only, not the scoring)

This is not the stream-by-stream scoring from section 2. It's what the folder evidence already suggests, to make that scoring faster. Every line is a hypothesis to check against real numbers.

- **Already live with a storefront and real sales (fastest to grow, if margins are positive):** Ikigai Digital Studios Etsy, Bored Nomad Etsy POD, Redbubble. Watch Etsy ad spend; Ikigai has had at least one period where it cost more than it earned.
- **Built but possibly never switched on:** TikTok Shop affiliate. The production pipeline exists and two products were produced; the open question is whether they were ever published with product links and what they earned.
- **Likely small by December:** YouTube ads (~7,300 views/month across all channels), Bored Nomad site affiliate income (~222 users/month), Roblox, Upkeeply, the website rebuild.
- **Unknown, could matter:** KDP (if books are live), email list (if a list exists), stock portfolios, AI contract work (if it counts).
- **New-build options Tony named:** digital products/ebooks. Fastest form probably reuses an existing storefront (Ikigai Etsy, Gumroad) rather than the planned Next.js site.
- **Fastest way to get real numbers for all of the above at once:** a Xero Profit and Loss report (section 5).

---

## 7b. Revenue stream scoring (completed 2026-10-13)

The question per stream: **"How fast, and how easily, can this realistically add $X/month by December 2026?"** Scored on today's real net income, effort to grow it, lag between new effort and money landing, and confidence in the evidence. Ranked by December priority, not by size — a $10/mo stream that's already running beats a $500/mo stream that needs a rebuild first.

**New finding this pass, not in section 7:** the `emrld.cc` script already on borednomad.com (found in the March 2026 site audit) is almost certainly Travelpayouts **Drive** — meaning Drive may already be live on the *current* site, independent of the rebuild. If so, it's been auto-linking travel mentions and switching other-network links to TP since before this plan existed, for zero ongoing effort. This wasn't checked in section 7's first read because the TP API wasn't live-tested yet; it is now (see API key test log, same date). Worth confirming before assuming this lever needs the rebuild to work.

### Tier 1 — already running, keep feeding it (fastest, lowest-risk path to real dollars)

| Stream | Net today | Effort to grow | Lag | Confidence | Next action |
|---|---|---|---|---|---|
| **Ikigai Digital Studios (Etsy)** | ~$15/mo gross (63 sales/2.5yr × ~$7.50), **net uncertain** — ad spend has exceeded sales in at least one period | Low — zero marginal cost per listing, just list more designs | Fast (digital, instant delivery) | High (real storefront, real sales, real ad-spend problem confirmed) | **Pull Ikigai's actual ad spend vs. sales for the last 2-3 months** (same Xero/Etsy method as Bored Nomad) before adding more listings — if ads are net-negative, fix that first; it's pure profit otherwise. |
| **Bored Nomad Etsy POD** | ~$51/mo revenue YTD average ($486.50 ÷ ~9.5 months), before Printful/Printify COGS | Low-Med — has per-unit fulfillment cost, but store, audience and design pipeline all exist | Fast | High (real shop, 157 sales, Xero-confirmed) | Identify best-selling designs/categories from the 157 sales and add 3-5 more in that vein; check net margin after COGS to confirm this is actually profitable per unit, not just revenue-positive. |
| **Redbubble: Bored Nomad** | $8-14/mo, already net of fees | Zero — passive, no action needed to keep earning | N/A, already running | High (pulled directly from seller dashboard) | Nothing required. If there's spare design time, reuse existing Bored Nomad art here — zero new creative cost, it's just upload. |
| **Stay22 YouTube auto-linking** | Unknown — live and running on Tony's channel already, revenue never pulled | Zero — already set up and running | N/A, already running | High it's active; unknown what it's earned | **Use the now-live Stay22 API** (confirmed working today) to pull actual earnings attributed to the YouTube integration — this is free money already in motion that's never been measured. |
| **Travelpayouts Drive on the current site (possible, not confirmed)** | Unknown — `emrld.cc` suggests it may already be live since before March 2026 | Zero if already installed — just needs confirming and tuning | Fast, acts on already-published posts, no rebuild needed | Medium — plausible, not confirmed | **Log into the TP dashboard and check whether Drive is actually enabled for borednomad.com, and whether it's generated any revenue to date.** If live, this is a free lever that was running unmeasured; if not installed, it's a 10-minute setup with no rebuild dependency. |

### Tier 2 — cheap to unlock, already diagnosed, worth the next hour of work

| Stream | Net today | Effort to grow | Lag | Confidence | Next action |
|---|---|---|---|---|---|
| **Unomas-Creative TikTok Shop (14 dormant listings)** | ~$0 (1 lifetime sale of 15 listings) | Very low — the blocking bug (size-chart OCR failure) is already diagnosed and the fix (TikTok's "Convert Image to Size Chart" tool) is already confirmed working on one listing | Fast if traffic materializes | Medium — fix confirmed on 1/15, not yet applied to the rest | Apply the same fix to the other 14 listings; low-price impulse items (like the one sticker that sold) are the signal to lean into over full-price apparel. |
| **TikTok Shop affiliate (Neon Parcel)** | $0 (live videos, no commissions) | Low — just needs per-video view/click data pulled to diagnose traffic vs. conversion | Fast once diagnosed | Low — root cause not yet known | Pull per-video analytics on `@neonparcel`; that alone tells you whether to push more views or fix the product page/offer. |
| **Impact.com catalog search for existing content** | $0 tracked, but the API is now live-tested and can search product catalogs by keyword | Low — this is a tool for tagging links in content Tony's *already written*, not new production | Fast | Medium (API confirmed working; catalog coverage for Envato/Tenba unconfirmed) | Run one `Catalogs/ItemSearch` test against an existing Bored Nomad post's topic to see if it returns usable product links — if yes, this is free incremental revenue on old content. |

### Tier 3 — real but slow, or blocked on something bigger than December

| Stream | Why it's not a near-term lever |
|---|---|
| **Broader travel affiliate (Stay22 Allez / Travelpayouts links / Impact tags on new content)** | The tooling is now proven live, but converting it into dollars means writing or re-tagging content at ~222 site-users/month — SEO-dependent growth takes months, not weeks. |
| **Digital products/ebooks (new build)** | Tony named it as a candidate, and the fastest version reuses Ikigai's existing Etsy storefront rather than a new site — but a real product still has to be designed and listed. Worth scoping small (one PDF/guide) if Tier 1/2 don't fill the gap alone. |
| **Email list growth** | Near-zero subscribers, no lead magnet, and the site it would convert off of is described by Tony as currently broken. Blocked on the website rebuild or a standalone landing page. |
| **Amazon KDP, Amazon Merch, Whop clipping, Roblox, Upkeeply, website rebuild, ad campaigns, donations, social media marketing, POD side-stores (FAA/Threadless/Gumroad), YouTube AdSense, stock portfolios** | Already flagged by Tony or by evidence as explicitly paused, deliberately sequenced for later, or too slow to ramp (SEO, new channel growth, new account approval, or new accounts/campaigns) to move the needle by December. No change to that read. |

### Reading this table

The honest total from Tier 1 alone, at today's measured numbers, is roughly **$75-90/mo already running** (Ikigai + Bored Nomad + Redbubble, before confirming Ikigai's and Bored Nomad's true net margins) — real but well short of $1,000. Tier 1 and 2 together are the highest-confidence, lowest-effort moves available right now: confirm/measure what's already running (Stay22 YouTube, possible Drive), fix what's already diagnosed (Unomas size charts, TikTok Shop diagnosis), and scale what's already profitable (Ikigai, Bored Nomad listings). None of that alone reaches $1,000/month — closing that gap by December most likely needs either a genuinely new, fast-to-launch product (the digital-product idea, built small and shipped through an existing storefront) or accepting that December lands short and the real target becomes "biggest sustainable jump possible," not a guaranteed $1,000.

---

## 7c. Deep-dive scoring on Tony's 5 named candidates, 2026-10-13

Tony pushed back on section 7b's first-pass scoring as LLM opinion, not real data. This pass used real pulled numbers (Etsy/Xero/TikTok/API-test figures already on file in this plan and `API_Directory.md`) plus cited market research — every claim below has a named source, not a guess. **Published as a dashboard artifact:** `https://claude.ai/artifact/MtqzUXukXTVvaNdbqQ3JgL` (scored bar chart, breakdown table, and a sources table — click through for the citation behind every claim).

**Methodology:** each of Tony's 5 named candidates scored 0-100, weighted: speed to money 40%, confidence in the evidence 20%, effort required 20%, size of realistic monthly upside 20%.

| Stream | Score | Tier | Real $ today |
|---|---|---|---|
| Ikigai Etsy — test Pinterest/FB ads vs Etsy Ads | **80** | Fast | ~$15/mo gross, net uncertain (ad spend has exceeded sales in at least one period) |
| Bored Nomad Etsy — more Aurora Borealis designs | **76** | Fast | ~$51/mo revenue YTD average, before COGS |
| Unomas-Creative TikTok Shop — fix + re-shoot videos | **64** | Cheap test | ~$0.50/mo average (lifetime $7.14 over ~13 months) |
| Bored Nomad YouTube → Amazon affiliate (travel gear) | **56** | Medium build | $0 today; channel already gets ~2,585 views/30 days |
| Monk-persona digital guides channel (Brain Blueprint pivot) | **34** | Slow/speculative | $0; channel doesn't exist, a prior attempt on it already failed |

**Key cited findings, each sourced in the dashboard's Sources table:**
- Etsy's own digital-product break-even ROAS (1.5-2.0) is well below the typical 2.8-4 benchmark — digital downloads are an easy bar to clear on ad spend, which is why Ikigai scores highest despite its ad-spend problem (InsightAgent, 2026 Etsy Ads ROAS Benchmarks).
- Pinterest is documented as the strongest platform fit for wall art/home decor, both organically and as an ads amplifier of already-working content, not a fix for weak listings (Printify; Pinterest Business's own Etsy case study: $12.47 incremental sales per $1 of Pinterest ad spend).
- Aurora Borealis/Northern Lights is a *validated* niche, not a guess — comparable Etsy listings carry 12,900-23,500 lifetime sales each, confirmed by direct marketplace search.
- TikTok Shop's own case studies show demo/educational video styles converting 3-4x higher than hard-sell style (9.2-9.9% vs 2-3%) — directly supports Tony's instinct that his Unomas-Creative videos may be too ad-like.
- Real search-intent evidence exists for a travel-gear-review YouTube format (66% of travelers watch pre-trip videos; a sample keyword carries 19,200 monthly searches), and Bored Nomad's channel already has a real, non-zero view base (~2,585/30 days) to build from — but travel/lifestyle content runs a lower median engagement (2.42%) than tech reviews (3.94%), and conversion-to-dollars is untested.
- Gut-health/supplement affiliate commissions are genuinely high (Digistore24 40-90%, ClickBank 50-75%), which is the only thing keeping the monk-persona concept's score above the floor — everything else about it (no channel, no content, a prior failed attempt) argues against it as a December lever.

**Not pulled live this pass (flagged, not guessed):** Ikigai's actual month-by-month Etsy ad spend vs. sales (would need an Etsy Shop Manager Stats login), and Unomas-Creative's per-video TikTok view/click analytics (would need the TikTok Seller Central Analytics tab). Both are fast follow-ups if Tony wants the next layer of real numbers before committing budget.

---

## 8. Open questions for Tony

### Resolved on 2026-10-11

| # | Question | Tony's answer |
|---|---|---|
| 1 | Etsy analytics route | **Both in parallel:** Etsy Developer API (Open API v3) and a third-party tool like Listadum (shortlist #24) for listing automation. Locked (section 5). |
| 5 | "Current" vs "Planned" mismatches | Don't adjudicate one by one: read each department folder and treat the folder docs as the truth. Done in section 3: Whop, Amazon Merch and Social media marketing are Planned (not earning); Etsy Digital is live (Ikigai); Digital products beyond Etsy are Planned. **KDP couldn't be resolved** (empty folder), flagged in section 4. |
| 6 | Is Redbubble still active? | **Yes, active.** |
| 7 | "Board-Nomad" vs "Bored Nomad" | **"Bored Nomad" is correct.** "Board-Nomad" is a typo; flagged in section 4, not silently fixed. |
| 12 | What counts as "best path"? | **$1,000/month in income by December 2026, via whichever mix of streams is fastest and easiest.** Now section 2, the lens for the whole plan. |

### Resolved, 2026-10-11

2. ~~**Website framework.**~~ RESOLVED — Astro + Cloudflare Pages (Tony confirmed; Cloudflare's real acquisition of Astro on 2026-01-16 matches his description exactly). See section 6.
3. ~~**Hostelworld.**~~ RESOLVED — confirmed, it's a hostel-booking travel affiliate program.
14. ~~**Does Mercor count toward the $1,000?**~~ RESOLVED — no, excluded. Tony is phasing Mercor out.
13. **Gross or net, and which month?** Gross/net RESOLVED — net (profit), confirmed by Tony. Which calendar month still assumed (December 2026), not explicitly confirmed yet.

### Still open

4. **Affiliate database / auto-linking.** Tony: "we'll discuss that more later." Future-phase placeholder, not scheduled (section 9).
8. **YouTube revenue numbers.** Extend the pull to real revenue/RPM (extra Google scope, re-login on all 12 channels), or are AdSense dashboard numbers enough?
9. **GA4 into the workspace.** Script a pull of "Bored Nomad - GA4"? (Different Google account from the YouTube pull.)
10. **Affiliate dashboards.** Which affiliate earnings get pulled automatically versus checked by hand?
11. **Other unconnected streams.** Which are worth connecting before the scoring, and which can be judged from a one-time manual export? (The Xero route in section 5 may answer most of this at once.)
15. **Xero as the baseline.** Tony approved pulling a Xero Profit and Loss report, 2026-10-11 (in progress). Still open: whether to script it later (needs a new read-only reports scope).
16. ~~**Uno Mas Creative spelling.**~~ RESOLVED, 2026-10-11 — "Unomas-Creative." See section 4.
17. ~~**Duplicate Etsy folders.**~~ RESOLVED, 2026-10-11 — see section 4.
18. **"Board-Nomad" folder names.** Tony approved fixing the typo, 2026-10-11 — done in root `CLAUDE.md` and the to-do list (now "Bored-Nomad"/"Bored Nomad"). **`005_Ecommerce/POD/Board-Nomad/` is now fully orphaned** (its content moved to `Etsy-Bored_Nomad/`, section 4) — Tony can delete it himself whenever. `002_Content-Creation/Video_Editor/002_Channels/008_Board-Nomad/` still carries the typo and is still in active use (channel production folder) — a rename there needs a separate, explicit go-ahead and reference check (scripts, YouTube token labels, graphify outputs may point at it). Not done yet.

### Questionnaire — CLOSED, 2026-10-12

Every item below was answered by Tony in one pass on 2026-10-12 (plus a live Redbubble login to pull real earnings). All real answers are folded into section 3's per-stream details. Keeping this list only as a record that the questionnaire ran and when:

- ~~Amazon KDP~~ RESOLVED — active, 4-5 low-content books live, expansion planned, tools identified. Not a December lever (grows organically, too slow). Section 3b.
- ~~Redbubble~~ RESOLVED — active, real monthly earnings pulled directly from the seller dashboard (Jul $0 / Aug $13.54 / Sep $8.20). Section 3b.
- ~~Fine Art America, Threadless, Gumroad~~ RESOLVED — all active accounts, nearly empty, deliberately deprioritized while Etsy is the main store. Section 3b.
- ~~Email list~~ RESOLVED — ConvertKit, ~1-2 subscribers; Beacons/Pensight accounts need a follow-up mapping pass. Section 3b.
- ~~TikTok Shop affiliate (Neon Parcel)~~ RESOLVED — both products went live with product links; no commissions yet. Section 3b.
- ~~Whop clipping~~ RESOLVED — paused, ~$30-40 lifetime earned, plans to automate later. Section 3b.
- ~~Amazon Merch~~ RESOLVED — no account yet, deliberately waiting on POD/Ikigai to mature first. Section 3b.
- ~~The Brain Blueprint~~ RESOLVED — old AI-video concept abandoned; pivot concept (recurring-persona health content, high-commission affiliate or Digistore24 product) not yet built. Section 3b.
- ~~Skool community~~ RESOLVED — doesn't exist yet, downstream of having tutorial content to put in it. Section 3b.
- ~~YouTube Partner Program~~ RESOLVED — no channel monetized yet; Neon Parcel closest but hasn't cleared subscriber/watch-hour thresholds. Section 3b.
- ~~Uno Mas Creative POD (TikTok seller store + Printify pop-up store)~~ RESOLVED 2026-10-11 — see section 3, verified live with real order/revenue data.
- ~~Stock photo/video portfolios~~ RESOLVED 2026-10-12 — still active, low priority, see section 3b. Only remaining open sub-item: current monthly income is untracked (figures on file are stale lifetime totals).

---

## 9. Future phase (NOT YET SCOPED): cross-brand affiliate database + auto-linking

> **NOT YET SCOPED. FUTURE DISCUSSION ONLY.** Tony: "we'll discuss that more later." No design decisions have been made. Don't build, prototype, or pick tools for this until Tony opens the discussion.

Tony's concept, as he described it on 2026-10-11:

1. **A central database of all his affiliate program relationships**, across all brands (not just Bored Nomad).
2. **An agent that scans his blog posts and content** and converts plain product/service mentions into the correct affiliate links automatically.

Context for when the discussion happens (not a decision): `005_Affiliate_Marketing/CLAUDE.md` already describes a target state close to this (an Airtable link catalog tagged by program, topic, content type and platform, plus a link-injection workflow with per-program compliance checks). The per-program folders it expects are still empty.

---

## 10. Status

- **Living document.** Updated as new information comes in. Not a one-shot plan, and not a build spec.
- **First draft:** 2026-10-11. **Second pass:** 2026-10-11 (Tony's answers, folder-by-folder research, success criteria). **Third pass:** 2026-10-12 (affiliate/referral cleanup — see `005_Affiliate_Marketing/`, the Xero P&L baseline, and the full questionnaire closed — section 8 — including a live Redbubble earnings pull). **Fourth pass:** 2026-10-12 (API/MCP connection potential for every platform, section 5b). **Fifth pass:** 2026-10-12 (second API dimension, content-link automation, plus bank/payment data as a fallback revenue signal, section 5b). **Sixth pass:** 2026-10-12 (Tony's write-first-link-after workflow, Stay22/Travelpayouts as default, hub consolidation direction, Impact Publisher Tag and Travelpayouts Drive findings, section 5b).
- **Next steps, in order:**
  1. ~~Get a real income baseline~~ Done, section 5 (Xero P&L, net goal confirmed, December confirmed as the target month).
  2. ~~Run the questionnaire for the undocumented streams~~ Done, section 8 — every stream now has a real, Tony-confirmed status.
  3. **Score every stream against "how fast and how easily can this add $X/month by December" (section 2) and pick the mix that reaches $1,000.** This is the next real step — every stream now has enough information to be scored.
  4. Fill `001_Architecture/Revenue-Streams.md` with the real numbers.
  5. In parallel, the locked Etsy route (Open API v3 + Listadum) proceeds under to-do #2 and #3.
- **Plans-folder rule:** this file stays in `001_Architecture/Plans/` while the monetization decision is pending. Per `Plans/README.md`, move it to `Archive/` only once the strategy is decided and finalized.
