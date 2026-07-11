---
title: "Neon Parcel TikTok Shop Creator Pipeline — Design"
type: spec
status: approved
created: 2026-07-11
---

# Neon Parcel TikTok Shop Creator Pipeline — Design

## Purpose

Tony joined the TikTok Shop Creator (affiliate) program on the existing NeonParcel TikTok account (1,000+ followers — same account used for NeonParcel's viral-animal-video content, but this is a separate content lane with no brand-aesthetic requirement). He earns commission on shoppable videos for third-party products (not his own inventory — that distinguishes this from the Uno Mas Creative / Board-Nomad POD TikTok Shop, which sells his own products and lives under `005_Ecommerce/`).

This is affiliate work, so it belongs under `005_Affiliate_Marketing/`, next to the TikTok Shop TOS compliance bundle already organized there.

First real test case: Colorsmart Pens, raw footage + 3 VO audio variants already dropped in `000_Ingest/Tiktok_Shop_Video_Dump/002-Colorsmart Pens/`.

## Scope

**In scope now:** TikTok Shop Creator pipeline only — vertical video, NeonParcel TikTok account, TikTok TOS compliance.

**Explicitly out of scope for this build:** An Amazon-affiliate YouTube sibling pipeline. Tony may eventually record separate landscape footage (raw dumps for TikTok and Amazon are never the same shoot — different orientation, different Ingest folders) and post to a not-yet-created "Amazon Finds" YouTube channel. That pipeline would live at `005_Affiliate_Marketing/Amazon_Associates/Videos/` (mirroring the structure below) and would check against the Amazon Associates Program Operating Agreement (`007_Resource_Library/Docs/Affiliate_Marketing/Amazon-Associates-Program-Operating-Agreement.md`) + YouTube ToS + FTC disclosure rules — NOT the TikTok TOS ledger. Documented here only so the TikTok-side design doesn't paint us into a corner; nothing under Amazon_Associates/ is built as part of this spec.

## Folder Structure

```
005_Affiliate_Marketing/Tiktok_Shop_Affiliate/Neon_Parcel_TikTok_Shop_Creator/
├── Compliance-Ledger.md              (shared across all products)
├── Compliance-Freshness-Log.md       (shared — tracks live-check dates + diffs)
├── Videos/
│   ├── 0001_Colorsmart-Pens/
│   │   ├── Intake.md                 (pre-production answers — see Questionnaire below)
│   │   ├── Edit/
│   │   │   ├── TikTok_V1.mp4
│   │   │   ├── TikTok_V2.mp4
│   │   │   └── TikTok_V3.mp4
│   │   ├── Compliance/
│   │   │   ├── Ledger-Scan-Results.md
│   │   │   ├── Vision-Scan/          (keyframes + findings, one set per distinct cut)
│   │   │   └── Transcript-Scan/      (per-video transcript + findings)
│   │   └── Package/                  (final ready-to-post files: video + caption + hashtags)
│   └── 0002_<Next-Product>/
```

Raw footage/audio is never duplicated into this tree — it stays in `000_Ingest/Tiktok_Shop_Video_Dump/<Product>/` as the pull source, per Tony's existing workflow (dump raw → pipeline pulls from Ingest → pipeline writes only what it creates into the folder above).

## Output Model

Not a fixed "3 cuts × 2 audio = 6 outputs" formula (the existing generic `TikTok-Shop-Affiliate-Video` skill's default assumption doesn't apply here). For this pipeline:

- **3 distinct TikTok videos**, all vertical, all from the same raw footage pool, but each with genuinely different cuts, beats, and pacing (not the same edit with swapped audio).
- **No YouTube output** as part of this pipeline. If Tony ever wants an Amazon-affiliate version of a product, that's a separate shoot (landscape footage, different Ingest folder) processed through the future Amazon Associates sibling pipeline — never the same footage reused, never posted to NeonParcel.

## Skill Approach

Extend the existing `001_Architecture/Skills/TikTok-Shop-Affiliate-Video/SKILL.md` in place rather than forking a Neon-Parcel-specific skill — it already does the right audio-first, no-branding-required editing approach. Additions needed:

1. A pre-production question at invocation start: **"Is this a TikTok Shop Creator video, or something else?"** — for now, only the TikTok Shop Creator path is implemented; anything else is out of scope and flagged back to Tony rather than guessed at.
2. Output model override for the Neon Parcel TikTok Shop Creator case: 3 distinct vertical cuts, no fixed YouTube pairing (supersedes the skill's general 6-output default for this specific invocation context).
3. The compliance gate (below) wired in as a required step before any video is marked ready-to-post.
4. Output routing to `005_Affiliate_Marketing/Tiktok_Shop_Affiliate/Neon_Parcel_TikTok_Shop_Creator/Videos/<NNNN_Product-Slug>/` per the folder structure above.

## Compliance Gate

Three phases, in order, per product:

### Phase 1 — Local Ledger Scan (every video, near-free)
A new file, `Compliance-Ledger.md`, built from the 18-file TOS bundle already in `TikTok-TOS/`. Rules are extracted **verbatim with citations** (exact quote + source filename + line reference), never paraphrased — paraphrase risks baking in errors, as already demonstrated when a grep of the actual source text contradicted an assumed-loosened rule about competitor logos. Each ledger entry:

```
RULE-014 | Visual/Branding | HARD BLOCK
Rule: Do not show any third-party brand name, logo, trademark, or service mark
without written permission — including blurred/partial logos, background logos,
or platform watermarks.
Source: CREATOR CAMPAIGN TERMS AND CONDITIONS FOR TIKTOK SHOP US.md (§2.4.1.1, line 255)
        + Best Practices for Promotional Content.md (lines 92, 138, 157)
Verified: 2026-07-11
```

Categories flagged **"always escalate to Phase 2 for this product"** regardless of how routine the script looks: Health/Supplements, Beauty/Skincare, Weight-Management. Tech gadgets (Tony's actual near-term focus) do not auto-escalate by category, but still get the universal Phase 1 checks (logos, disclosures, misleading/discount claims, guarantee language).

This scan runs against the VO script text before editing starts (catch issues early, before any production time is spent).

### Phase 2 — Live Freshness Check (cadence-gated, not every video)
A new CLI tool (Firecrawl-based, per Tony's CLI-first rule) pulls TikTok's currently-published Creator/Seller policy pages and diffs them against the ledger. The 18 local `.md` files have no captured/source-date metadata, so they cannot be assumed current — this phase is what catches real policy drift.

- Runs automatically if `Compliance-Freshness-Log.md`'s last-verified date is more than 14 days old; otherwise skipped.
- Any category flagged "always escalate" (Health/Beauty/Weight-Management) also triggers this phase regardless of cadence, the first time a product in that category is processed.
- Diffs (new rules, changed rules, contradictions with the local ledger) get appended to the ledger as new dated entries — never silently overwritten — and logged in `Compliance-Freshness-Log.md`.

### Phase 3 — Post-Build Content Verification (every video, automated)
Run once the edit exists, before it's marked ready-to-post:

- **Vision scan**: extract keyframes from each of the 3 distinct cuts (existing OpenRouter vision pipeline already used elsewhere in this workspace) checking specifically for third-party logos/watermarks/brand marks in frame.
- **Transcript scan**: transcribe (or reuse) each of the 3 videos' final VO and re-check against the ledger — catches drift between the original script and the final edit.

### Final Gate
No video is marked ready-to-post without Tony seeing a compact compliance summary first: what was checked, what passed, what got flagged and how it resolved. Never auto-publish — consistent with the existing "never publish without explicit approval" rule already in place for the Video Editor department.

## Testing Plan

Colorsmart Pens (`000_Ingest/Tiktok_Shop_Video_Dump/002-Colorsmart Pens/`) is the first real run through this pipeline end to end: 3 distinct TikTok cuts from the existing footage + 3 VO variants, full compliance gate, output landing in `Videos/0001_Colorsmart-Pens/`.

## Open Items (not blocking this build)

- Amazon Associates sibling pipeline — folder documented above, nothing built.
- "Amazon Finds" YouTube channel does not exist yet — out of scope until Tony decides to build it.
- Ledger initial build (Phase 1 extraction from the 18 TOS files) and the Firecrawl freshness-check CLI tool are both net-new work items for the implementation plan.
