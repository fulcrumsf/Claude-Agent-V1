# Neon Parcel Storyboard QA

## What This Is

This project adds a controlled storyboard-generation and validation layer to the Neon Parcel long-form video pipeline. It turns each shot into a structured frame specification, checks generated storyboard sheets against that specification for visual continuity and physical plausibility, and prevents Seedance generation when no valid storyboard survives review.

## Core Value

Seedance must receive a storyboard that is visually and logically consistent with the intended shot, rather than being forced to reconcile contradictory references and prompts.

## Requirements

### Validated

- Existing Neon Parcel generation guard records paid attempts and prevents duplicate shot/version submissions.
- Existing production folders preserve active and superseded media non-destructively.
- Existing storyboard and Seedance skills provide the downstream prompting conventions.
- [x] Structured storyboard contract, visual QA, capped regeneration, and validated Seedance handoff implemented and tested — Phases 1-4.

### Active

- [x] Define a stable storyboard schema with an overall summary, continuity invariants, explicit frame descriptions, and exact captions.
- [x] Validate each generated storyboard candidate against frame-level subject, object-state, action, caption, continuity, and physics requirements.
- [x] Limit storyboard regeneration to three checked candidates and flag the shot if all fail.
- [x] Generate the Seedance prompt from the validated storyboard evidence, not from unchecked assumptions.
- [x] Preserve candidate images, prompts, QA findings, and attempt history for audit and review.

### Out of Scope

- Replacing GPT-Image-2, Seedance, or the existing provider wrappers — the feature must fit the current toolchain.
- Automatically approving a visually ambiguous candidate — ambiguity must remain a manual-review outcome.
- Solving all video-generation hallucinations — the scope is to remove storyboard/prompt contradictions before video generation.
- Adding a new paid provider — cost control requires using the existing routing and generation guard.

## Context

- Shot 6 exposed the failure mode: the intended story required a closed gate, bear already present, and grandmother approaching/opening it, while the storyboard showed incompatible subject presence and gate state across frames.
- The current workflow generates a whole storyboard sheet in one image call, then supplies that sheet to Seedance. The missing control is a formal contract and post-generation visual QA gate.
- Tony wants a cost-conscious process: at most three storyboard generations, each checked before the next, with a hard flag after the third failure.
- The current active production is `002_Content-Creation/Video_Editor/002_Channels/002_Neon-Parcel/Productions/0001_Grandma-And-Bear-Compilation/`.

## Constraints

- **Cost**: Maximum three storyboard candidates per shot before manual review — avoid open-ended paid regeneration.
- **Continuity**: Frame requirements must be explicit enough to detect characters or object states appearing/disappearing without a causal transition.
- **Evidence**: Every pass/fail decision must retain the candidate, the checker result, and the requirements checked.
- **Safety**: A failed or ambiguous storyboard must block Seedance submission.
- **Compatibility**: Integrate with the existing Python tools, JSON artifacts, skills, and archive conventions.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use a structured frame-by-frame storyboard schema | Filling explicit fields is more reliable than asking the model to invent prompt structure | — Pending |
| Check the generated image, not only the source prompt | The model can produce a visually incorrect sheet even when the prompt is correct | — Pending |
| Cap storyboard attempts at three | Controls cost while allowing two corrective regenerations | — Pending |
| Derive Seedance text from the validated storyboard | Prevents unchecked original assumptions from contradicting the accepted visual reference | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? Move to Out of Scope with reason.
2. Requirements validated? Move to Validated with phase reference.
3. New requirements emerged? Add to Active.
4. Decisions to log? Add to Key Decisions.
5. "What This Is" still accurate? Update if drifted.

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections.
2. Core Value check.
3. Audit Out of Scope.
4. Update Context with current state.

---
*Last updated: 2026-08-31 after Phase 4 completion*
