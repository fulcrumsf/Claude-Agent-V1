---
title: "Seedance Character & Environment Consistency Workflows"
type: wiki
category: video-production
tags:
  - seedance
  - character-consistency
  - reference-sheets
  - prompt-engineering
source: "[[Seedance-2.0-GPT-Image-2-Character-Environment-Consistency-Tutorial]], [[Seedance-2.5-Character-Environment-Consistency-Tutorial]]"
created: 2026-08-10
---

# Seedance Character & Environment Consistency Workflows

## What It Is

A pair of step-by-step tutorials on locking character and environment identity across Seedance video generations (2.0 and 2.5), using GPT Image 2 / Nano Banana as the reference-sheet generator and Claude to write the structured prompt templates.

## Key Concepts

- **Context-reset trick** — GPT Image 2 accumulates noise/artifacts the longer a single chat runs; always regenerate reference images in a brand-new chat, not by iterating in place.
- **Two-stage reference sheet pipeline** — generate one base character/environment image → feed it to Claude with a reference-sheet prompt template → Claude fills in a detailed multi-angle grid prompt → paste that into GPT Image 2 along with the original base image as an attached reference.
- **Fixing hallucinations without regenerating** — screenshot the broken frame (e.g. hallucinated hands), fix it in ChatGPT's image editor, remove any AI watermark, then feed the corrected frame back into Seedance as the starting frame ("starting frame matches image four").
- **Face-block filter golden rule** — a single starting-frame image with a clearly visible face is a gamble for Seedance's content filter; objects/environments as the starting image are always safe, and a full multi-angle character sheet is usually enough to bypass the face block even with a visible face.
- **Seedance 2.5 upgrade facts** — 30-second generations (up from 15s), up to 50 reference images, "Omni reference" mode. Reference images should be named descriptively and tagged by that exact name in the prompt (never "image one" placeholders) — this is what lets the model resolve which reference maps to which subject.
- **Fixing a broken scene without a full regenerate** — cut a ~5-second window around the broken shot in an editor, export it, re-upload with a targeted "keep video exactly as is, in shot two add X" prompt plus the character reference. 5 seconds (not 2-3) gives the model enough context to correctly place the character in the environment.
- **Iteration model, not one-shot** — expect 3+ full generations per scene; go back to Claude with exact shot/timestamp references ("shot 3", "shot 6 to 8 seconds") to request rewritten prompt segments, don't restart from scratch.
- **Claude Skill shortcut** — one creator built a custom Claude "concept sheet builder" skill that auto-detects whether an uploaded reference is a character, environment, or prop and applies the matching template automatically, replacing manual copy-paste of the right prompt template per asset type.

## How Tony Uses This

Directly extends the same reference-sheet architecture already locked into `Reimagined_Realms_POV_Shorts_Pipeline_v2` (character-sheet + environment-sheet conditioning via kie.ai). The context-reset trick, the "fix don't regenerate" hallucination-repair workflow, and the face-block golden rule are all concrete gaps to check against the current [[Seedance-Prompting-Guide]] skill in Phase 3 of the Seedance Case Study Pipeline (see Claude memory `project_seedance_case_study_pipeline.md`).

## Related

- [[Seedance-Prompting-Guide]] — the living universal Seedance skill this knowledge feeds into
- [[Storyboards-To-Consistent-Videos-Using-Seedance-2.0]] — companion tutorial on storyboard-driven consistency
- [[The-Secret-To-AI-Character-Sheets]] — head-to-head test of different character-sheet methods
