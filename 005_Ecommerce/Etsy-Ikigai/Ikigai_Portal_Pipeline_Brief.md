---
title: "Ikigai Portal + Listing Pipeline — Interview Brief"
type: plan-input
domain: ecommerce
tags: [ikigai, pipeline, portal, lab-plan-input]
status: interview complete 2026-10-21, input for /lab-plan (not yet run)
---

# Ikigai Portal + Listing Pipeline — Brief for /lab-plan

Source: Tony's brain dump + 10-question interview, 2026-10-21 (Full-Picture mode). Old workflows are reference only; copy and adapt pieces, do not reuse as-is. Old models and prompts are out of date.

## Goal
A local portal where Tony reviews ideas, approves them, reviews generated art, and presses "produce this listing". Everything after that runs automatically and ends as a DRAFT on Etsy for IkigaiDigitalStudio. Nothing is published without Tony. Tony must look at every image himself; the system never auto-curates.

## Portal behaviour
- Always shows 10 ideas (text descriptions). Approve or deny; a denied idea is replaced instantly from a pre-researched pool (30-50 candidates), so approved ones stay and the list refills.
- Pool refreshed by a scheduled/on-demand research job. A few days of staleness is fine. Pool-low warning in the UI.
- Idea mix priority: (3) gap-first, low competition with real search intent; (2) mixed; (1) proven lane. Each idea tagged proven/test and carries its evidence. Current Ikigai look (abstract, Japandi, etc.) is the anchor; straying is allowed when data supports it.
- Approval generates an image prompt, shown in a separate section. "Run prompt" with an engine dropdown (config list, not hard-coded): Nano Banana (1/2/Pro), Flux, GPT Image 2, others. Output images displayed; Tony picks.
- After art is approved: mockups, sizes, PDF, Drive, naming, listing text, keyword/tags, Etsy draft.
- Listing text shown collapsed inline per listing; click Edit to edit, or tell chat ("fix tag 7"). Template-driven; only the opening SEO paragraph of the description is unique per image. Samsung Frame TV pieces have their own variant (none built yet; research average Etsy price and spec from existing Frame TV listings).
- Chat: Tony talks to Claude in the Claude Code window while watching the portal; optional in-portal "ask Claude" box later.
- Volume: 3-5 listings/week now; bursts of 10-20 later (e.g. 5 in 30 min). Idea count can scale up.
- Tony uses it only on his Mac. Local web app (localhost) recommended, packaged in Docker so it can move to Railway/Hetzner later; storage and job steps swappable.

## Pipeline steps (from Tony)
1. Ideate (keyword research, gap analysis, what sells, low competition + decent search).
2. Generate art (selectable engine), upscale. Largest size at 300 DPI.
3. Upscale: Upscayl (installed at /Applications/Upscayl.app; check headless CLI) as default; Magnific MCP backup; open-source (ComfyUI weights) alternatives. Minimise cost.
4. Mockups: hero image, product video, hand/poster flat mockup, one fixed zoomed detail shot (~20x), plus several room-scene lifestyle mockups (style of house + count chosen in portal). Etsy allows 10 images. Listing image order confirmed in Prior-Pipeline-Research-Consolidated.md section on listings: pos 1 hero, 2 video, 3 poster, 4+ style-matched rooms/details/size graphics.
5. Static mockups via PhotoCraft (open-source Photoshop clone, headless CLI, batch, MCP, opens PSD). Goal: drop Adobe Creative Cloud. PhotoCraft does NOT run .jsx/.atn; scripts must be rebuilt. photocraft-cli is NOT currently installed/on PATH (checked 2026-10-21); first task is to prove it opens Tony's mockup PSDs headless.
6. Resize/center-crop to the 5 print sizes (read sizes from a live listing; old scripts: ikigai_cropper_fixed.py).
7. Package: Google Drive folder per listing, sequential folder naming, share link embedded in a templated PDF (Tony will supply the template) which is the Etsy download file. Later storage/delivery may move off Drive to a database/other store.
8. Listing text, 13 tags (keyword research), price: template price, mostly $6.50 (an $8.50 listing includes an extra 1:1 ratio image). Frame TV price: research.
9. Upload as Etsy draft via Etsy Open API v3 (Tony applies for a developer/Seller App; approval may be minutes). Listadum (shortlist #24, SEO/audit/bulk edit via Etsy API; unverified) as parallel/fallback. Until API approved: pipeline produces a finished folder Tony uploads manually.

## Out of scope for v1
Bundles. But every finished single is logged as a record (ID, style, sizes, files, listing link) so a later bundle pipeline or storage move is a lookup.

## Time sinks (build these first)
Mockups, room scenes, resizing, PDF creation, Drive upload + sequential naming, description, tag/keyword research. Etsy draft review after upload is only a few clicks.

## Research data sources
Start: Alura Pro through logged-in Chrome (volume, competition, per-listing lifetime sales), Pinterest Trends, Etsy trend report, Google Trends via Composio, EverBee. eRank free is 5 searches/day. Chrome extensions installed (Profile 2): Keywords Everywhere, EHunt, Alura, EverBee - manual spot-check only. Upgrade to paid tools only after pipeline listings show sales; vet by real reviews from digital-print sellers first. Alura volumes run far above EverBee; use for ranking only. Alura /listings endpoint has a daily quota (~150 calls).

## Creative Inspiration folder
Tony wants `005_Ecommerce/Etsy-Ikigai/Creative_Inspiration/` for Pinterest style dumps (idea engine reads it). PENDING Tony's yes on the path; not created.

## Full-Picture findings to build in
- Real problem is traffic/competition, not production speed: Ikigai 30d = 64 visits, 0 orders; lifetime 4,145 visits, 62 orders, 1.5% conversion, $356. Abstract = 53 of 63 sold items (Colorful Abstract 43 orders). Pipeline value depends on new listings getting seen, so measure per-listing performance and feed it back into idea scoring (the "data decides" loop Tony wants).
- AI room mockups: old V4 n8n flow (ChatGPT-4o prompts -> Flux Schnell empty room -> fal nano-banana/edit inserts art) lets the model re-render Tony's art. Add a fidelity check per mockup (compare art region vs original) or composite the exact art by code. Flag failures to Tony.
- Upscale: 300 DPI at the largest size exceeds native model output; plan generate -> upscale as two stages with a quality check.
- Etsy AI-disclosure: shop discloses AI per listing; keep that in the template.
- Cloud move: PhotoCraft has a Linux build; Upscayl needs GPU/Vulkan (slow on cheap servers) - plan a cloud-friendly upscaler later.
- Existing n8n/script files on this Mac: /Users/tonymacbook2025/Documents/Docker/n8n-data/workflows/ (Ikigai_Mockup_Gen_Rooms _V4.json, _Ikigai_Art_Creator-Nano-Pro_V5.json, Ikigai_Image_Resize.json, Ikigai_Tokenizer) and /Users/tonymacbook2025/Documents/Automations/IkigaiDigital/ (cropper, thumbnail, mockup launcher, zoom launcher, .jsx scripts). Reference only.
- Related docs: 005_Ecommerce/Etsy-Ikigai/Prior-Pipeline-Research-Consolidated.md, 007_Resource_Library/Design_Inspiration/Ikigai-Art-Styles-Tokens.md (120-style token table), 007_Resource_Library/Workflows/Ikigai-Digital.md, 001_Architecture/Plans/Revenue-Stream-Pipeline-Outlines.md.

## Open items for Tony
- Apply for Etsy developer app (day-one task).
- Confirm Creative_Inspiration folder path.
- Supply the Etsy-delivery PDF template and the listing description template.
- Install/locate PhotoCraft CLI; confirm which PSD mockup templates are licensed to reuse.
