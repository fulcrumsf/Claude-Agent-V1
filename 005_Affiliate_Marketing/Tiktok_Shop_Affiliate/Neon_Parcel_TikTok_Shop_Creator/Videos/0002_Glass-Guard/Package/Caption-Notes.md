---
title: "Glass Guard — Caption Notes"
type: posting-notes
created: 2026-07-31
---

# TikTok_V1.mp4 — Posting Status

**Posted to Blotato as a TikTok draft (2026-07-31), confirmed landed in
Tony's TikTok drafts inbox.** Caption used: `Glass Was So Clean The Camera
Couldn't Even See It 🚿✨ #glasscleaning #showerhacks #tiktokfinds`. Still
needs the product link attached manually in-app before publishing (Blotato
has no field for TikTok Shop product tagging).

Post settings: accountId 27763 (neonparcel — **note: this ID changed from the
25731 previously recorded in memory; always verify live via
blotato_list_accounts before posting, don't trust a cached ID**),
privacyLevel PUBLIC_TO_EVERYONE, isDraft true, isBrandedContent false
(affiliate/commission arrangement, not a brand-paid partnership — see
Compliance-Ledger.md RULE-008 addendum), isYourBrand false, isAiGenerated
false, comments/duet/stitch left enabled.

**Disclosure approach:** no #ad — relying on the auto "Creator earns
commission" tag TikTok adds once the product link is attached, per
Compliance-Ledger.md RULE-008 addendum. 3 relevant hashtags used instead.

**Single-video product** — Tony explicitly opted out of the standard 3-variant
A/B set for this product.

## Compliance gate results

| Video | Phase 1 | Phase 2 | Phase 3 Transcript | Phase 3 Vision |
|---|---|---|---|---|
| V1 (first render) | Pass (RULE-008 action item) | Could not run — Firecrawl can't reach tiktok.com; proceeded on last-verified ledger (2026-07-11) per Tony's sign-off | CLEAR | FLAG → resolved false positive (own-product label, see Vision-Scan/TikTok_V1-resolution.md) |
| V1 (final, post audio fix) | — (unchanged) | — (unchanged) | CLEAR | CLEAR |

## Audio pause-trim fix (this product's key pipeline improvement)

First render had audible clicks/pops and clipped words from a naive
hard-cut pause trim. Root cause: no crossfade at cut boundaries, and the
silence detector's threshold occasionally landed inside a word's trailing
consonant. Fixed by adding 120ms safety padding + 15ms fades at every join —
now permanent as `scripts/trim_vo_pauses.py` and SKILL.md Step 5a.4. Full
detail in memory: `feedback_vo_pause_trimming.md`.

VO went from 64.9s raw → 37.5s (naive trim, had clicks) → 40.3s (fixed trim,
clean) after re-adding the safety padding. Final loudness: -14.22 LUFS
integrated, -1.49 dBTP true peak.

## Shot plan

Single cut, 40.3s: product box hook (IMG_9100) → grime shot 1 (IMG_9103) →
grime shot 2 (IMG_9102) → applying product (IMG_9101) → clean-glass reveal
(IMG_9184, shot through the glass at the ceiling post-clean — reads as
"empty" footage unless you know that's the point) → more application
(IMG_9101, later window) → clean-glass hold into CTA (IMG_9184) → product box
close (IMG_9100).
