# Session Handoff — Affiliate/Referral API-Connection System Built

**Date:** 2026-10-12, afternoon through night (one continuous session)
**Harness:** Claude Code
**Picks up from:** `2026-10-12_Session-Handoff_Claude_Monetization-Plan-And-TikTok-Shop-Fixes.md` (this morning's handoff — that session closed the monetization questionnaire; this one built the whole API-connection layer on top of it)

## Where things stand

Tony named this session's work his real path to the **$1,000/month net profit by December 2026** goal, and explicitly wants it treated as a persistent, cross-session, cross-harness "shared brain" — not one-off research. His words: "it needs to know everything... I want all of this to be global... a shared brain." Every durable fact from this session has been written into files, not left in chat. Read in this order:

1. `001_Architecture/Plans/Agent-OS-Monetization-Strategy-Plan.md` — master plan, section 5b for the API/content-link strategy.
2. `005_Affiliate_Marketing/CLAUDE.md` — "Direction Update — 2026-10-12" has the locked workflow/consolidation decisions, including the Impact Publisher Tag vs. Travelpayouts Drive comparison and the 12Go-vs-Stay22 evidence.
3. `001_Architecture/API_Directory.md` — "Connection potential" section, per-platform detail.
4. The two live artifacts (use the Artifact tool's `read` action, they're too detailed to re-derive from memory):
   - **Affiliate & Referral Audit** — `https://claude.ai/artifact/5CCTGiT16yFwEAiK4csjpt` — 76 items, each with two status dimensions (earnings API, content-link automation) and a removal checkbox Tony controls.
   - **Stock Portfolio Audit** — `https://claude.ai/artifact/KpJ549B9wWNMGJ6UQ2kYW1` — 14 items.

## What is done and verified

- **Full affiliate/referral inventory rebuilt** from Tony's old spreadsheet exports, restructured into exactly two categories (Affiliates, Referral Links) per his request, with non-affiliate items (ads, donations, POD side-stores) relocated into the monetization plan.
- **Monetization questionnaire fully closed** — every revenue stream (KDP, Redbubble, POD side-stores, email list, TikTok Shop affiliate, Whop, Merch, Brain Blueprint, Skool, YPP) has a real, Tony-confirmed status. Full detail in plan section 3.
- **Two real dashboards checked live** (logged in via Tony's password manager, no credentials seen by the agent):
  - Redbubble: Jul 2026 $0, Aug 2026 $13.54, Sep 2026 $8.20 (after fees).
  - Amazon KDP: 5 live paperback journals from 2020-2021, $0.00 royalties in Sep and Oct 2026 — live but dormant.
- **API/MCP connection research completed across ~90 platforms**, two dimensions per item: can earnings be pulled automatically, and can a specific product/tour/hotel page be found and tagged with Tony's affiliate ID while writing content ("content-link automation"). Full results on every item in the Affiliate & Referral Audit artifact.
- **Amazon PA-API key tested live** — one safe, read-only call confirmed the key is valid and current (not deprecated, contrary to an earlier research guess), just gated by Amazon's 10-qualifying-sales/30-day eligibility rule, exactly as Tony predicted.
- **Real API keys now in `~/.env-secrets`:**
  - Amazon Associates — tested, working, gated on eligibility.
  - Stay22 — added by Tony, **not yet live-tested**.
  - Travelpayouts — added by Tony, **not yet live-tested**.
  - Impact — connected via OAuth; Tony configured the token's scopes himself with guidance given mid-session (enabled Actions, Conversions, Reports, Catalogs, Products, Tracking Links, Programs, Media Properties, Invoices, and most others; left off Withdrawal Settings, Identity Verification, and "a couple more" he didn't specify).
- **Strategic decisions locked** (all documented in `005_Affiliate_Marketing/CLAUDE.md`):
  - Content workflow: **write first, find links after** — never pick affiliate products before or during writing.
  - Default hub order for building links into a draft: **Stay22 → Travelpayouts → Impact**, network-agnostic beyond that (Tony: "I don't care what affiliate marketing network I go through... whatever's easiest and makes the most money").
  - **Travelpayouts Drive** (a free on-site AI script) is the strongest fully-automatic match for "write first, link after" — it actually scans finished posts and inserts links on its own. Impact's Publisher Tag only upgrades links already present in text, it can't create new ones from plain mentions.
  - **Consolidation is a direction, not an action** — Tony is not cancelling anything now; new content just routes through the hub networks going forward, old one-off programs fade out only if/when he stops wanting to manage them.
  - **12Go is a deliberate keep** — research (after Tony pushed back on an initial "redundant" flag) confirmed it's the only real Southeast Asia ground-transport (bus/train/ferry) specialist; Stay22 has zero ground-transport capability. The actual redundant program is **Bookaway** (12Go's sister company, same routes).
  - **borednomad.com rebuild is fully from-scratch** — no old code, HTML, or scripts carry over, only text and images from existing posts. This resolves the earlier `emrld.cc` mystery-script question as moot.
  - Drive, Stay22, and Impact's Publisher Tag can all run on the rebuilt site without conflicting (confirmed via direct research) — only real overlap risk is Drive vs. Stay22 both claiming the same hotel/tour brand, solved by excluding the brand in one of them.
  - Stay22's **YouTube integration is already live** — Tony's channel is connected, Stay22 auto-inserts recommended tracked links into video descriptions. No setup needed, already running.
- **Two real bugs fixed on the Affiliate & Referral Audit artifact:** added a light/dark theme toggle defaulting to light (Tony found dark mode hard to read); fixed a count-collision bug where same-named subcategories in different groups (e.g. "Creative" under both Affiliates and Referral Links) showed the wrong item count.
- **Stay22 referral link corrected** to the real URL Tony gave (`hub.stay22.com/referral/borednomad/travel`), replacing a stale one.
- `TOOLBOX.md`'s `META_GRAPH_API_KEY` reference confirmed as **planned, not stale** — Tony intends to get this key, hasn't yet.

## Genuinely open items for next session

1. **Live-test the Stay22 and Travelpayouts API keys.** Same pattern as the Amazon test: one safe, minimal, read-only call each, confirm they authenticate, log the result. Offered to Tony at session close, not yet done.
2. **Score every revenue stream against "how fast and how easily can this add $X/month by December."** This is the monetization plan's own stated "next real step" (section 2) and still hasn't been done — every stream now has enough real data to actually run this scoring, it just hasn't happened yet.
3. **Impact's "Deals" scope** — Tony asked about brand-deal/sponsorship functionality (separate from commission-based affiliate links); a scope called "Deals" exists on the token screen but was never researched. Worth a look if Tony wants to pursue direct brand sponsorships through Impact.
4. **Beacons/Pensight email-list account-to-channel mapping.** Tony confirmed he has lists on ConvertKit (~1-2 subscribers), and possibly separate Beacons/Pensight accounts tied to different channels (Neon Parcel? Reimagined Realms?) but isn't sure which is which. Needs a direct look at those accounts.
5. **Fine Art America / Gumroad / Threadless / Redbubble automation** — Tony wants an eventual way to auto-push the same POD designs across all these channels instead of manually re-listing; explicitly said this is not a near-term priority, but it's a named future want.
6. **Stock portfolio current monthly income is still untracked** — all figures on file are stale lifetime totals; Tony confirmed the stream is active but doesn't say how much it currently makes.
7. **12Go vs. direct-account-vs-Travelpayouts-account tracking** — confirmed 12Go is a Travelpayouts brand, but unconfirmed whether Tony's existing 12Go links should route through his direct 12Go account or through Travelpayouts (commission rates may differ) — flagged for Tony to check both dashboards himself.
8. **The cross-brand affiliate database + auto-linking concept** (section 9 of the monetization plan) is still explicitly future-phase, not scoped — don't start building it without Tony opening that discussion.

## Read next

1. This file.
2. `001_Architecture/Plans/Agent-OS-Monetization-Strategy-Plan.md` in full — it's grown substantially this session.
3. `005_Affiliate_Marketing/CLAUDE.md` "Direction Update — 2026-10-12" section.
4. The two live artifacts, if working on anything affiliate-specific — they have far more per-item detail than any summary captures.
