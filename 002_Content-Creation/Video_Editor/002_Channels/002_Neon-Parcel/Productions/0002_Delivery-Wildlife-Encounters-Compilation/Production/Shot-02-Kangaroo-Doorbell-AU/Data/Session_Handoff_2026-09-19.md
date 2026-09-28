---
title: "Test Shot 03 — Session Handoff"
date: 2026-09-19
---

# Where things stand

Test Shot 03 (kangaroo/delivery driver, fixed doorbell camera) is mid-production.
The environment sheet's architecture was found to be wrong twice in a row
(offset staircase with a mismatched patio, then an implausibly tall 10+ step
staircase, then a hedge sealing off the driveway from the walkway with no
gap) — all three caught by Tony reviewing generated images directly, not by
any check I ran beforehand. That's the actual problem this handoff exists to
fix: environment/architecture work was being generated from imagination and
checked after the fact, backwards from how it should work.

**Two pipeline-level fixes are already locked in** (both in
`001_Architecture/Skills/Environment-Sheet-Generation/SKILL.md`), so the next
session does not need to relitigate them:
- **Architectural Plausibility Check** (locked 2026-09-19): mandatory before
  generating any built/constructed location — ground it in real reference
  first, write the site plan as text, check the plan against 5 criteria,
  only then generate (diagram first, photo derived from the diagram).
- **Photoreal panel must be 16:9** (matches video output ratio); **full
  sheet is 4+ panels, landscape**, including a labeled top-down site plan
  and a landmark/detail call-out panel.

# Checklist for next session

1. **Invoke `Production-Research-Agent`'s Step 2 (reference images)** —
   tailored search, not generic: real photos of single-story regional-
   Australian house front porches/steps/walkways (the kind Tony pasted
   examples of directly — modest 2-5 step runs, a real continuous
   concrete path from driveway to entry, garden beds as edging alongside
   that path, never a hedge wall blocking it). Save to
   `Research/Reference_Images/` per that skill's convention. This step was
   skipped entirely so far for this shot — do it first, before anything
   else below.

2. **Rewrite `Data/Architectural_Site_Plan.md`** grounded in those real
   photos (not Street View, which didn't pan out — see that file's current
   "honest limitation" note) — explicit step count, and explicit language
   that the hedge/border has a visible gap at the exact point the walkway
   crosses it. Run the 5-point Architectural Plausibility Check against the
   rewritten plan before generating anything.

3. **Redo the environment sheet from scratch**, in this specific order,
   per the now-locked skill rules:
   - Panel 1: top-down site plan (schematic/blueprint), generated first,
     grounded directly in the real reference photos and the checked plan.
   - Panel 2: photorealistic doorbell POV, **16:9**, chained from Panel 1
     (not generated first and treated as ground truth, which is the
     mistake made this round).
   - Panel 3: reverse establishing view (schematic), chained forward.
   - Panel 4: landmark/detail call-out panel (mailbox, clothesline, water
     tank), chained forward.
   - Composite all 4 into one landscape sheet via PIL (per the skill's
     "never ask the model for multiple panels in one call" rule) — each
     panel generated separately, chained references, not a single
     multi-panel generation call.
   - Show every panel to Tony for review before treating any of it as
     locked.

4. **Once the environment sheet is approved**, the rest of the shot
   pipeline resumes from where it already stands:
   - Driver character sheet: already corrected and approved (hand-carried
     bag, no backpack, car shown) — no rework needed unless the new
     environment sheet changes something it depends on.
   - Kangaroo character sheet: already approved, no rework needed.
   - Regenerate the storyboard referencing the new environment sheet
     (previous storyboard versions v1-v6 all referenced the flawed
     environment plate and should not be reused/trusted as a base).
   - Re-run the Grounding Coverage Check
     (`Data/Grounding_Coverage_Check.md`) against the new storyboard call
     before submitting it.
   - Run the Automated Body-Orientation Check on the approved storyboard.
   - Proceed to Seedance video generation.

# Tools available for the next session

- `check_subject_positions.py` (Generic_Tools, global) — YOLO bounding-box/
  pose/segmentation checks, plus `--save-panels` (full-resolution individual
  panel extraction) and `--onion-skin` (red/cyan frame-diff overlay) —
  requested by Tony specifically so panel-to-panel position checks are
  measured, not eyeballed off a shrunk thumbnail. Usage gate: only after a
  shot has already failed visual review twice on a position/collision
  defect, not on a first draft.
- `storyboard_contract.py` — `reference_images` is now a required spec
  field; `render_prompt()` auto-generates the reference-labeling block. Any
  new storyboard spec must include it.

# Real defects fixed this session (for context, not action items)

- Driver character sheet: removed courier backpack, now hand-carries the
  bag (Tony's catch — a driver doesn't wear a hands-free bike-courier bag).
- Storyboard: kangaroo timing (was appearing before frame 4), driver/
  letterbox collision, bag-vs-item-left-behind logic — all fixed and
  verified in v5/v6, but those storyboard versions are now moot since
  they reference the flawed environment plate.
