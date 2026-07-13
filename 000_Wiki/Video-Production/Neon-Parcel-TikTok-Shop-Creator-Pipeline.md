---
title: "Neon Parcel TikTok Shop Creator Pipeline"
type: wiki
category: video-production
tags:
  - tiktok-shop
  - affiliate-marketing
  - video-production
  - compliance
  - neon-parcel
created: 2026-07-12
source: 001_Architecture/Skills/TikTok-Shop-Affiliate-Video
---

# Neon Parcel TikTok Shop Creator Pipeline

## What It Is
A compliance-gated video production pipeline for TikTok Shop Creator affiliate videos, posted on the NeonParcel TikTok account (same account as NeonParcel's viral-animal-video YouTube/Instagram/Facebook brand, but this is a distinct content lane — no brand aesthetic requirement, since TikTok Shop Creator commission videos are unrelated to NeonParcel's animal-content identity). Tony earns commission when a shoppable video drives a sale of a third-party product — this is affiliate work, not e-commerce (he doesn't sell his own products here, unlike the Uno Mas Creative/Board-Nomad POD shops).

Built via `superpowers:subagent-driven-development` (8-task plan, fresh implementer subagent per task, per-task review with fix rounds, final whole-branch review). Design spec: `001_Architecture/Superpowers/Specs/2026-07-11-Neon-Parcel-Tiktok-Shop-Creator-Pipeline-Design.md`. Skill: `001_Architecture/Skills/TikTok-Shop-Affiliate-Video/SKILL.md` (extended in place, not forked — same skill also handles the generic 6-output audio-first workflow for other invocation contexts).

## Key Concepts

**Output model:** not the skill's generic "3 cuts × 2 audio = 6 outputs" — for this pipeline it's 3 genuinely distinct TikTok videos (different beats/pacing per video from the same footage pool), no YouTube pairing. An Amazon-affiliate YouTube sibling pipeline is documented in the spec but intentionally not built (would live at `005_Affiliate_Marketing/Amazon_Associates/Videos/`, different compliance regime entirely — Amazon Associates + FTC, not TikTok TOS).

**Folder structure:** `005_Affiliate_Marketing/Tiktok_Shop_Affiliate/Neon_Parcel_TikTok_Shop_Creator/Videos/NNNN_Product-Slug/{Edit,Compliance/{Vision-Scan,Transcript-Scan,Ledger-Scan-Results.md},Package}/`.

**Three-phase compliance gate** (account-ban risk is real — TikTok can suspend/deactivate e-commerce access):
1. **Phase 1 — local ledger scan** (`Compliance-Ledger.md`, 10 citation-backed rules extracted verbatim from the real 18-file TOS bundle, never paraphrased) — read against the VO script before editing starts.
2. **Phase 2 — live freshness check** (`check_tos_freshness.py`, Firecrawl-based, 14-day/always-escalate cadence) — catches real policy drift the local snapshot missed. **Known limitation:** Firecrawl currently refuses to scrape `seller-us.tiktok.com` entirely ("we do not support this site") — the wiring is correct end-to-end but provides zero real drift-detection value until this vendor limitation is resolved.
3. **Phase 3 — post-build scans** (`compliance_vision_scan.py`, `compliance_transcript_scan.py`) — both fail safe to FLAG on any ambiguous result (never silently CLEAR). The vision scan reliably flags the product's own label/logo text — this is correct behavior, not a bug; it always needs a human to distinguish "the product being promoted" (fine) from genuine unrelated third-party branding (the actual violation).

**RULE-008 (disclosure) real-world addendum:** the TOS text says `#ad`/`#sponsored` should be prominent, but Tony's direct platform observation (2026-07-12) is that attaching a TikTok Shop product link auto-adds a "Creator earns commission" tag, which functions as the disclosure for this content type — other TikTok Shop affiliate creators don't use `#ad` either. Not something the local TOS bundle documents; flagged in the ledger as observation-based, revisit if it's ever contradicted by a bundle refresh.

**Loudness normalization** (`normalize_loudness.py`, SKILL.md Step 5a.5): raw VO measured -34 to -35 LUFS with no clipping risk (just too quiet vs. TikTok's ~-14 LUFS norm) before this was added — now a mandatory step, two-pass EBU R128 targeting -14 LUFS / -1.5 dBTP.

**Shot-matching workflow** (validated on Colorsmart Pens, Tony's explicit approval): transcribe the VO with word-level timestamps (ElevenLabs Scribe) → build an exact narration beat map → run dense keyframe vision analysis (every ~4s, not just scene-change detection, since long continuous handheld clips often produce only 1 scene-change frame) → match real footage moments to what's being narrated → when no clip actually shows the narrated outcome, a still image with a slow Ken Burns zoom on the relevant detail is an acceptable, Tony-endorsed substitute (reusing the same static asset across all product variants for that one beat is fine, not a duplication problem, as long as overall beat count/pacing/shot selection differs per video).

## How Tony Uses This
Invoke the `TikTok-Shop-Affiliate-Video` skill for any new TikTok Shop Creator product. First real production: Colorsmart Pens (3 videos, V1 posted to Blotato as a TikTok draft 2026-07-12 — Blotato has no TikTok Shop product-tagging field, confirmed via live tool schema, so the product link must be attached manually in the TikTok app after the draft lands).

## Related
- [[../Affiliate-Marketing/TikTok-Shop-Affiliate-Compliance]]
- [[../Affiliate-Marketing/TikTok-Shop-Affiliate-Do-Dont-Cheat-Sheet]]
