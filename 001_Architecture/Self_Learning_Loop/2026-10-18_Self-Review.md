---
title: "Self-Review — 2026-10-18"
type: self-review
domain: architecture
tags: [self-review, 2026-10-18]
---

# Self-Review — 2026-10-18

## What went wrong, honestly

- **Surfaced maybes repeatedly instead of fixing and verifying.** I reported suspected listing problems and open questions instead of checking the live listing and resolving them. Tony's correction was direct: fix what needs fixing and come back only when everything is checked and done. The repeated reporting was the failure, not the individual listing issues.
- **The PIL image check hit a `DecompressionBombError`.** The verification path stopped on an oversized product image instead of completing. The right approach is to handle the limit explicitly and verify with a bounded/downsampled image, not to treat the failed check as an answer.
- **The first price script treated non-price inputs as prices.** That produced noise instead of a reliable pricing pass. The script needs to read only explicit price fields and validate that each value is an actual price before reporting or syncing anything.

## What worked well

- Rebuilt all 11 listings after the Printify publish reset their TikTok size charts and brand, and confirmed the final state rather than leaving the repair list open.
- Harmonized prices across Gildan 5000, Comfort Colors, Bella 3001, and sweatshirts; changed the Printify default margin from 40% to 60%; synced Printify prices to TikTok; and repriced the Etsy iPhone cases and totes through Printful.
- Re-created Makin Bacon #2 and Sigma Rizz through Printify **External products > Migrate product** and reactivated them.
- Completed the material sweep, including the IV League cotton/polyester blend correction and the Fishing and Christmas fixes.

## Patterns worth watching

- The verified end state is the deliverable. A list of suspected issues is not a close-out, and an unresolved maybe is not a finding.
- TikTok Shop must remain the master listing. Any workflow that publishes from Printify will silently undo TikTok-specific size charts and brand settings.
- Browser verification needs the same rigor as data verification: fresh tab per product, no tab cleanup, and an explicit check of the final visible state.
- Automated checks need their own failure handling. An image-library exception or a loose price parser should produce a clear failed check, never a confident but wrong result.

## Close-out state

Unomas Creative TikTok Shop ended the session with **15 Active, 0 Reviewing, 0 Needs attention** listings.
