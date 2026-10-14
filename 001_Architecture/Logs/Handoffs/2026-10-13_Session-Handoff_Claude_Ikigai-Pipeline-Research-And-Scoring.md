# Session Handoff — Ikigai Pipeline Research + Revenue Scoring

**Date:** 2026-10-13
**Harness:** Claude Code
**Picks up from:** `2026-10-12_Session-Handoff_Claude_Affiliate-API-System-Built.md`

## Where things stand

This session closed out the open items from 2026-10-12 (API key live-tests) and then went deep on two things Tony pushed toward: a real-data revenue-stream scoring (not LLM opinion), and the start of a from-scratch Ikigai production pipeline.

## What is done and verified

1. **All 3 pending API keys live-tested, all working:**
   - Impact.com: `GET /Mediapartners/{AccountSID}/Campaigns` → 11 campaigns.
   - Stay22: `GET /v1/reporting/transactions` → authenticated, `partnerId: borednomad`.
   - Travelpayouts: `GET /finance/v2/get_user_balance` → real balance, $7.68 USD pending.
   - Logged in `001_Architecture/API_Directory.md`.

2. **Revenue-stream scoring, real-data version, done and published.** `001_Architecture/Plans/Agent-OS-Monetization-Strategy-Plan.md` sections 7b and 7c. Two dashboard artifacts:
   - `https://claude.ai/artifact/MtqzUXukXTVvaNdbqQ3JgL` — the general Tier 1/2/3 scoring.
   - A second artifact (link in section 7c of the plan) — deep-dive 0-100 scoring on Tony's 5 named candidates (Ikigai ad-platform test: 80, Bored Nomad Aurora Borealis: 76, Unomas-Creative TikTok fix: 64, Bored Nomad YouTube→Amazon: 56, monk-persona channel: 34), every claim cited to a real source.

3. **Ikigai pipeline — first structural pass, then explicitly deferred by Tony.** `001_Architecture/Plans/Revenue-Stream-Pipeline-Outlines.md` has 5 one-sentence-per-node trees (Ikigai full pipeline, Bored Nomad Aurora Borealis expansion, Unomas-Creative fix, YouTube/Amazon affiliate, monk-persona channel). **Tony corrected the Ikigai tree:** the existing n8n workflows found in the workspace are reference architecture only, not the build target — he wants a new, purpose-built pipeline. He said walking through how it all fits together is "too much detail for one session" and deferred it. **Do not re-push on this until Tony opens it himself.**

4. **New consolidated reference file built:** `005_Ecommerce/Etsy-Ikigai/Prior-Pipeline-Research-Consolidated.md` — this is now the one place for everything Ikigai-pipeline-related found outside the main plan:
   - Section 1: real October 2025 Etsy niche/keyword-research instructions (written for the now-discontinued Rube/Composio tool, methodology still reusable).
   - Section 2: the 120-style design-token taxonomy (`TS-293` through `TS-419`) that feeds the existing n8n Wall Art Token Creator.
   - Section 3: pointer to existing production scripts (already catalogued in the pipeline-outline file).
   - Section 4: genuine gaps — listing automation, Pinterest posting, ad creation, Alura.io integration. Still open.
   - Section 5: skills found via `find-skills` — honest caveat that almost none clear the 1K-install trust bar; workspace's own Tool-Manager/firecrawl/ai-seo are more trustworthy starting points.
   - Section 6: agent-tool platforms — **Treg** (confirmed: this is the "OpenRouter for agent tools" Tony was trying to remember), Composio Universal CLI (Canva automation), Printing Press Library (58 CLIs, several directly relevant — tiktok-shop, shopify, amazon-seller, google-ads, scrape-creators).
   - Section 7: **Etsy listing mockup photo pattern, confirmed directly against 2 live listings** — position 2 is always a fixed video mockup, position 3 is always a fixed flat "poster" mockup, position 4+ varies by art style/room staging. Matches Tony's description exactly.
   - Section 8: **PhotoCraft researched** — open-source, AI-rebuilt Photoshop alternative (Rust, MIT/Apache-2.0), opens real PSD files, has CLI/batch/native-MCP automation (better agent-automation fit than Photoshop). **Gap: no ExtendScript/`.jsx`/`.atn` support** — Tony's existing `Ikigai_Batch_StaticOnly.jsx` and `Ikigai_Zoom_Mockup.jsx` scripts need rebuilding (same logic, different scripting surface), not porting. **Tony confirmed this tradeoff is fine** — not a blocker.

5. **Antigravity local-storage search technique established and documented.** Real chat data lives in `~/.gemini/antigravity/conversations/*.pb` (encrypted, not searchable) and `~/.gemini/antigravity/brain/<session>/` (readable `task.md`/`walkthrough.md`/`implementation_plan.md`). Binary-safe grep (`grep -qai`) across both found zero mentions of Ikigai/Etsy/POD anywhere — that specific "new full system" conversation Tony remembered is not in Antigravity's local storage on this Mac. Worth reusing this method for future "I talked to an LLM about X" searches.

6. **`TOOLBOX.md` updated** with the agent-tool-aggregator findings (Treg, Composio Universal CLI, Printing Press Library, Pipedream "string alpha" flagged unverified) and PhotoCraft — all marked not-yet-installed/connected, research only.

## Genuinely open items for next session

1. **Tony's own Ikigai pipeline walkthrough** — the real next step on this whole thread. He said it's too much to give in one session; wait for him to bring it, don't chase it.
2. **Which existing Python scripts are reusable** inside the new pipeline (cropper, thumbnailer, mockup launcher, zoom launcher) vs. rebuilt from scratch — explicitly unresolved, Tony said "I need to show you how it all fits together."
3. **PhotoCraft is research-only** — not installed, not tested on this Mac. If Tony wants to actually try it, that's a fresh task (download, test PSD compatibility with his real mockup templates, test CLI/batch against a real mockup task).
4. **Listing-automation, Pinterest-posting, and ad-creation gaps** (section 4 of the consolidated file) — still nothing found for these. Alura.io status (waitlist/applied) not confirmed.
5. **Section 7b/7c's carried-forward open items** (unchanged from 2026-10-12): live-balance follow-ups on Stay22/Travelpayouts beyond the basic auth test, Impact's "Deals" scope for brand sponsorships, Beacons/Pensight email-account-to-channel mapping, stock portfolio current income untracked.

## Read next

1. This file.
2. `001_Architecture/Plans/Agent-OS-Monetization-Strategy-Plan.md` sections 7b-7c.
3. `001_Architecture/Plans/Revenue-Stream-Pipeline-Outlines.md` — note section 1 (Ikigai) is marked superseded/pending Tony's walkthrough.
4. `005_Ecommerce/Etsy-Ikigai/Prior-Pipeline-Research-Consolidated.md` — the new master reference for anything Ikigai-pipeline-related; check here before re-researching tools, skills, or the mockup pattern.
