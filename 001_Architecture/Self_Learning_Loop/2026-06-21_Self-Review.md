---
title: "Self-Review 2026-06-21"
type: self-review
date: 2026-06-21
tags: [self-review, pricing, airtable, tool-manager]
---

# Self-Review — 2026-06-21

## What Went Wrong

### Normalized prices shipped instead of actual prices
I rewrote the sync function to use "variants" with pre-computed $/s values — which was the right architecture — but the first sync used the OLD `_norm_price_str()` function (which multiplied per-second prices by 5 for 5s-clip normalization) via stale Airtable records that were still visible. The real sync had created 34 new records but the old 24 were still showing at the top of the table.

**Pattern:** I created new records correctly but didn't clean up the old ones first. Tony saw the old broken data, not the new correct data. Always DELETE stale records before or during a structural table rebuild, not after.

### Resolution not in the Name field
I added a `Resolution` column but didn't surface it in the primary Name field. This is a UI context failure — I know Tony reads the Name column first. Should have added `(resolution)` to Name from the start without being asked.

## What Went Right

### fal.ai billing unit investigation
Persisted through multiple dead-ends (API returning vague "units", no clear docs) and eventually found the answer by scraping the actual model page: token-based billing with a published formula. The per-second equivalents match exactly what's shown on fal.ai's pricing table. Good outcome.

### Structured the variant data cleanly
The `pricing_variants` design is solid — keeps raw `pricing` intact for the refresh loop, adds computed `variants` for Airtable display. This separation will survive future pricing changes cleanly.

## Patterns to Remember

1. **Airtable restructures:** When changing the upsert key (e.g., from Model ID to Row ID), delete old records FIRST or the table will show both old and new simultaneously.

2. **Price display:** Tony always wants the literal unit price. If I'm converting, show the conversion assumption inline (e.g., "kie.ai: $0.159/s (est. 8s clip)") rather than hiding it.

3. **Column visibility:** For any table Tony reads, put the most important differentiator in the Name/primary field. Don't assume the right column will be visible.
