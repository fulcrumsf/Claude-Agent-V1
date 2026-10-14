---
title: "Revenue Stream Pipeline Outlines"
type: plan
domain: architecture
tags: [plan, monetization, pipeline, ikigai, bored-nomad, unomas-creative, youtube, tiktok]
status: draft — structure only, awaiting Tony's approval
created: 2026-10-13
---

# Revenue Stream Pipeline Outlines

**Status: structure only.** Tony asked for a brief, one-sentence-per-node tree for each of the 5 revenue candidates scored in `Agent-OS-Monetization-Strategy-Plan.md` section 7c — not a built-out plan. This is for him to glance at and approve the shape before any plan gets fleshed out. **Note: Tony wrote "Alora.io" in his brain dump — this is Alura.io (`app.alura.io`), the Etsy SEO/keyword tool already on his affiliate shortlist (`005_Affiliate_Marketing/Affiliate-Program-Removal-Checklist.md`, line 57). Corrected here, flag if that's wrong.**

---

## 1. Ikigai Digital Studios — full pipeline (research → design → list → promote)

**Correction from Tony, 2026-10-13: this is NOT "reuse the existing n8n workflows."** Tony wants a new, purpose-built pipeline for Ikigai. The existing n8n workflows (`_Ikigai_Art_Creator`, `Ikigai_Wall_Art_Token_Creator`, `Ikigai_Mockup_Gen_Rooms`, `Ikigai_Image_Resize`) are reference only — a rough guide to the architecture shape, not something to wire up as-is. Some of the Python scripts (`ikigai_cropper_fixed.py`, `ikigai_thumbnail.py`, `Ikigai_mockup_launcher.py`, `Ikigai_detail_zoom_launcher.py`, `Tokenized_Image_Compressor.py`) may be reusable pieces inside the new pipeline — not confirmed which ones yet. **Tony is walking through how it all fits together before this section gets re-planned — too much detail for one session, deferred.** Relevant skills and API/agent-tool platforms found for this pipeline (Treg, Composio Universal CLI, Printing Press Library, Alura.io, Listadum, etc.) are now catalogued in `005_Ecommerce/Etsy-Ikigai/Prior-Pipeline-Research-Consolidated.md` sections 5-6 — check there before researching any of this again. Everything below this note is the PRIOR draft (treat as superseded, kept for reference until the walkthrough replaces it):

~~**Real existing infrastructure found this session — don't rebuild, point to these:**~~
- ~~n8n workflows (`/Users/tonymacbook2025/Documents/Docker/n8n-data/workflows/`): `_Ikigai_Art_Creator` (art generation), `Ikigai_Wall_Art_Token_Creator` (style-consistent tokenized variants), `Ikigai_Mockup_Gen_Rooms` (room-scene mockups), `Ikigai_Image_Resize`.~~
- ~~Local scripts (`/Users/tonymacbook2025/Documents/Automations/IkigaiDigital/`): `ikigai_cropper_fixed.py` (5 standard print-size crops), `ikigai_thumbnail.py` (72dpi thumbnails), `Ikigai_mockup_launcher.py` + `Ikigai_Batch_StaticOnly.jsx` (Photoshop static mockups → video mockups in one click), `Ikigai_detail_zoom_launcher.py` + `Ikigai_Zoom_Mockup.jsx` (zoom/detail mockups), `Tokenized_Image_Compressor.py`.~~
- Reference notes: `007_Resource_Library/Workflows/Ikigai-Digital.md` (plain-English script docs), `007_Resource_Library/OpenAI_History/POD-Print-on-Demand/n8n-Image-Crop-Workflow-FBF0.md` and sibling notes in that folder (prior ChatGPT working sessions — still useful background, just not the blueprint to copy).
- **Not found / not yet automated:** niche/keyword-gap research, Etsy listing creation itself, Pinterest posting, Pinterest/Facebook ad creation. These are the real gaps to design, not the mockup/crop/thumbnail steps.

**Tree:**
1. **Research**
   1.1. Pull real Etsy search-volume and competition data per candidate niche.
   1.2. Shortlist 5-10 keyword-gap niches (high search, low competition) via Alura.io once access clears, manually in the meantime.
2. **Ideation**
   2.1. Turn each validated niche into concrete design concepts (subject, style, color mood).
3. **Design generation**
   3.1. Generate base artwork per concept using the existing n8n Art Creator workflow.
   3.2. Run art through the existing Wall Art Token Creator for style-consistent variants.
4. **Asset production** *(already automated — wire together, don't rebuild)*
   4.1. Crop to the 5 standard print sizes (`ikigai_cropper_fixed.py`).
   4.2. Generate room-mockups (n8n Mockup Gen Rooms).
   4.3. Generate zoom/detail mockups (`Ikigai_detail_zoom_launcher.py`).
   4.4. Generate thumbnails (`ikigai_thumbnail.py`).
5. **Listing**
   5.1. Draft SEO title/tags/description per listing (Alura.io once available, manual meanwhile).
   5.2. Publish to Etsy (manual today; Etsy Open API v3 is the already-locked automation route per the monetization plan).
6. **Promotion**
   6.1. Pin each new listing to Pinterest organically as the first promotion step.
   6.2. Layer in a small paid-ad test (Pinterest first, per this session's research) once a listing has organic traction.
7. **Feedback loop**
   7.1. Track which niches/designs actually sell and feed that back into step 1's research.

---

## 2. Bored Nomad Etsy — Aurora Borealis expansion

**Pointer:** reuses Bored Nomad's existing POD/Printful/Printify pipeline (`005_Ecommerce/Etsy-Bored_Nomad/CLAUDE.md`) — no new production infrastructure needed, only new designs feeding the existing flow.

**Tree:**
1. **Research**
   1.1. Pull Etsy's own search/competition data for Aurora Borealis sub-niches (Iceland, Norway, Alaska, color variants, formats).
2. **Design**
   2.1. Brief 3-5 new designs in formats/styles already proven in the niche (per the 12.9k-23.5k-sale competitor evidence from this session).
3. **Production**
   3.1. Run designs through the existing POD mockup/listing flow (same Printful/Printify process already in use).
4. **Listing**
   4.1. Publish via the already-locked Etsy Open API v3 + Listadum automation route.
5. **Promotion**
   5.1. Cross-post to Pinterest, reusing whatever Pinterest step gets built for Ikigai (item 1, step 6).
6. **Review**
   6.1. Compare new listings' performance against the proven competitor benchmarks.

---

## 3. Unomas-Creative TikTok Shop — fix + re-shoot

**Pointer:** the size-chart fix is already diagnosed and confirmed working on one listing (`005_Ecommerce/Tiktok_Shop-Uno_Mas_Creative/CLAUDE.md`) — step 1 below is pure execution, not new research.

**Tree:**
1. **Fix existing listings**
   1.1. Apply the already-confirmed "Convert Image to Size Chart" fix to the other 14 listings.
2. **Content audit**
   2.1. Pull real view/click analytics per existing video from TikTok Seller Central.
3. **Content redesign**
   3.1. Re-script videos toward product-education/benefit style instead of hard-sell (per this session's TikTok Shop conversion research).
4. **Test**
   4.1. Publish 2-3 re-shot videos and compare conversion against the old style.
5. **Scale**
   5.1. Double down on whichever style/price-point converts best (low-cost impulse items are the current signal, per the one sticker sale).

---

## 4. Bored Nomad YouTube → Amazon affiliate (travel gear)

**Pointer:** production-process template exists at `005_Affiliate_Marketing/Tiktok_Shop_Affiliate/` (Neon Parcel's compliance/production pipeline) — adapt the process, not the platform or product type.

**Tree:**
1. **Scope**
   1.1. Decide: pilot on the existing Bored Nomad channel, or spin up a dedicated channel — **needs Tony's decision.**
2. **Research**
   2.1. Identify 10-15 high-search, buy-intent travel-gear keywords/products to target first.
3. **Production**
   3.1. Adapt the existing Neon Parcel TikTok Shop pipeline to a YouTube format pointed at Amazon products.
4. **Monetization**
   4.1. Tag each featured product with an Amazon Associates link once the account clears the PA-API eligibility bar.
5. **Publish & measure**
   5.1. Publish a small batch (3-5 videos) and track views/clicks/conversions before committing further production time.

---

## 5. Monk-persona digital guides channel (Brain Blueprint pivot)

**Pointer:** this channel has no existing infrastructure — a prior AI-video attempt here was abandoned as "AI slop." Treat as a from-scratch build, lowest-confidence of the five (see monetization plan section 7c).

**Tree:**
1. **Concept lock**
   1.1. Tony defines the persona, topic focus (e.g. gut health), and monetization target (Digistore24 offer vs. direct digital guide) before any production starts — **needs Tony's decision.**
2. **Offer research**
   2.1. Shortlist 3-5 high-commission Digistore24/ClickBank offers in the chosen health niche.
3. **Content format**
   3.1. Design a repeatable template (same character, same structure, enough variation to avoid duplicate-content flags).
4. **Pilot**
   4.1. Produce 2-3 pilot videos before committing to a full channel build.
5. **Decision gate**
   5.1. Tony reviews pilot performance before deciding whether this becomes a real production line.

---

## Open questions for Tony

1. Item 1 (Ikigai) and item 2 (Bored Nomad) both end in a Pinterest-promotion step — build that once and share it, or build it per-brand? Recommend building once.
2. Item 4 (YouTube/Amazon) step 1.1 needs a real decision: existing Bored Nomad channel or a new one.
3. Item 5 (monk persona) step 1.1 needs the persona/topic/monetization decision locked before anything else can start.
4. Confirm the Alora.io → Alura.io read is correct.
