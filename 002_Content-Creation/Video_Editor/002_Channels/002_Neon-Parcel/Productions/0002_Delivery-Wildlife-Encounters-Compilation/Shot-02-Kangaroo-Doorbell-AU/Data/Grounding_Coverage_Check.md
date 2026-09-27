---
title: "Test Shot 03 — Grounding Coverage Check"
---

# Call: Delivery_Driver_Character_Sheet.png (v3, corrected 2026-09-18)

Checklist built from `Research/Plausibility_Facts.md` (Delivery driver +
Delivery car rows/Phase 1 items) — every line accounted for before writing
the prompt.

| Fact (source) | In this prompt? |
|---|---|
| Local takeaway shop's own driver, not a gig-app courier (Phase 1 Q1) | Included — stated explicitly |
| Carries a plain insulated delivery bag or stack of takeaway containers, held/carried, NOT a hands-free backpack (Phase 1 Q2) | Included — backpack explicitly excluded by name |
| Drives an ordinary older-model sedan/hatchback, not rideshare-branded, not new/luxury (Phase 1 Q3 / Delivery car row) | Included — in the environment/movement panel description |
| Generic unbranded clothing, ordinary regional-AU casual streetwear, era ~2019 (Phase 2 Era/region-appropriate form) | Included |
| Ordinary adult human scale (Phase 2 Scale reference) | Included — default person-sheet scale, no oversizing language needed |
| Arrival/mobility: drives and parks a car (Phase 2) | Included — environment panel shows him beside the parked car |
| Motion/behavior nuance: "notice kangaroo" physical tell (Phase 2) | **Excluded, intentionally** — this is a storyboard/video motion beat, not applicable to a static character reference sheet |
| Plausible presence: local takeaway delivery ordinary for regional AU towns in 2019 (Phase 2) | Context only, not a visual requirement — no sheet content needed |

No unaccounted facts. Prompt cleared to submit.

# Call: Storyboard_v2.png (corrected 2026-09-18)

| Fact/finding (source) | In this spec? |
|---|---|
| Driver: local takeaway driver, no backpack, hand-carried bag/containers (Phase 1) | Included — reused directly from the corrected character sheet as a bound reference |
| Driver's car visible at driveway/screen-left edge, stationary throughout (Tony correction, Blocking Plan) | Included — added to every frame's visible_subjects/object_states, not just some, since it's a static background element |
| Grey kangaroo species, chest/shoulder-height scale vs. driver (Phase 1/2) | Included — reused from character sheet, unchanged continuity invariant |
| House/yard set dressing: Hills Hoist, water tank, corrugated-iron house, native garden (Phase 1) | Included — reused from the corrected environment plate as a bound reference |
| Clear/dry midday weather (Phase 1 / Matrix weather axis) | Included — unchanged continuity invariant |
| No dog/other animals (Blocking Plan) | Included — unchanged continuity invariant |
| **v1 review finding (not a Grounding Audit fact, but a confirmed defect):** kangaroo was missing entirely from frame 5 | Fixed — new hard constraint requires the kangaroo visible in every frame from 4 through 6, no exceptions |
| **v1 review finding:** kangaroo's frame-4 entry position read as already mid-exit near the letterbox, not freshly entering | Fixed — frame 4 description tightened to specify it's still close to the garden-bed entry point, not yet advanced across the lawn |

No unaccounted facts or unresolved v1 defects. Spec cleared to submit.

# Call: Storyboard_v3.png (corrected 2026-09-18, Tony's review of v2)

| Finding (source) | In this spec? |
|---|---|
| Kangaroo's body visually merged with the letterbox post in v2 frame 4 (Tony, direct image review) | Fixed — every frame's kangaroo description now explicitly states clear separation from the letterbox; added as a standalone hard constraint |
| Driver would keep his insulated bag, not leave the whole thing on the porch (Tony correction) — a real Grounding Audit gap never asked in Phase 1, logged retroactively as Phase 1 item 7b | Fixed — frames 1-3 rewritten around "take item out, keep bag," frames 3-6 explicitly show the bag still in hand, added as two standalone hard constraints |

Both are genuine defects found by direct visual review of the generated
image, not something the existing Grounding Audit columns would have caught
on their own (object-collision and "what exactly gets left behind" aren't
covered by scale/mobility/motion/era/presence). Logged here so the fix is
traceable, and the "what gets left behind" question is now recorded in
`Research/Plausibility_Facts.md` for any future shot with a similar
hand-off action.

# Call: Environment_Plate_1.png (v2, corrected 2026-09-18)

| Fact (source) | In this prompt? |
|---|---|
| Driveway/car must be visible in-frame, not off-frame (Tony correction 2026-09-18, Blocking Plan) | Included — car at screen-left edge, stationary |
| Driver's car: ordinary older-model sedan/hatchback, not rideshare-branded (Phase 1 Q3) | Included |
| House: single-story brick-veneer/weatherboard, corrugated-iron roof (Phase 1 Q5) | Included — was previously generic "suburban house exterior," now specific |
| Yard: Hills Hoist clothesline, rainwater tank, native/bushland garden plantings (Phase 1 Q4) | Included |
| Second vehicle/ute in driveway (Phase 1 Q4, listed as optional set dressing) | **Excluded, intentionally** — only the driver's own car should be present; an extra vehicle risks an unaccounted-for object in a plate meant to stay static across every frame |
| No dog, no other animals (Blocking Plan explicit exclusion) | Included — explicitly stated in prompt |
| Doorbell hardware era specifics: fisheye, motion-triggered, 2018/2019 Ring-generation, modest dynamic range (Phase 1 Q8) | Included |
| Clear, dry, midday weather, hard shadows (Phase 1 Q6) | Included — was previously just "midday sun," now specific |
| Doormat/steps/letterbox as fixed scale references (Phase 2 Scale reference) | Included (unchanged from v1) |

No unaccounted facts. Prompt cleared to submit.

# Call: Storyboard_v4.png (corrected 2026-09-18, Tony's precise review of v3)

Built `check_subject_positions.py` (new tool, YOLO/Ultralytics-based) per
Tony's direct request for a deterministic check instead of eyeballed visual
review. It measures person/car bounding-box positions per panel -- real
capability, but its first run (whole-person centroid distance) was too
coarse to catch the actual defect Tony found by zooming in himself: exact
foot position relative to the steps vs. the driveway. Documenting both the
tool's real value and its real limitation honestly rather than overclaiming.

| Finding (source) | In this spec? |
|---|---|
| Kangaroo present in frame 1 (should not exist until frame 4) | Fixed — frame 1 explicitly states it must not be drawn; added as a standalone hard constraint covering frames 1-3 |
| Driver retreats from driveway (frame 4) back onto the steps (frame 5), then back to the driveway (frame 6) -- confirmed by Tony via close visual inspection, reproduced by zooming into the steps region myself | Fixed — frame 5's object_states now explicitly states his feet remain on the driveway, not the steps; added as a standalone hard constraint covering frames 4-6 |

Note: `check_subject_positions.py`'s COCO-based YOLO detector cannot detect
"steps," "driveway," or "sidewalk" -- these aren't trained object classes,
only discrete objects (person, car, animal, etc.) are. Confirmed directly
with Tony. Fine-grained relational judgments like "which step is he
standing on" still require direct visual inspection (zoomed crops), not
object-detection bounding boxes.
