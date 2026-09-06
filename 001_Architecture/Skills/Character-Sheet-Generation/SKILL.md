---
name: character-sheet-generation
description: Use whenever a video production has a recurring character or creature that appears in more than one scene and needs to look identical every time — "build a character sheet", "creature reference sheet", "make a character sheet for the shark/main character/background worker", or any pipeline step that identifies a recurring subject and needs a consistency reference before generating shots of it. Applies across channels — POV human characters (Reimagined Realms) and recurring animals/creatures (Anomalous Wild) both use this. Generates a 16:9 reference sheet via GPT-Image-2, with panels sized to what they need to show (not a rigid uniform grid), adapted to the subject type.
---

# Character/Creature Sheet Generation

Generates a single reference-sheet image locking a recurring subject's appearance — every angle, expression/pose, and identifying detail a later video-generation shot might need to match. One sheet per distinct recurring subject; a subject that only appears once doesn't need one.

Production-proven origin: this generalizes `character_sheet_generation.py` from `Reimagined_Realms_POV_Shorts_Pipeline_v2`, which has run across multiple real productions. The generalization adds `subject_type: creature` so the same mechanism serves Anomalous Wild's recurring animals, not just POV human characters.

## Before using this skill

Read [`GPT-Image-2-Prompting-Guide`](../GPT-Image-2-Prompting-Guide/SKILL.md) first for the underlying model's prompting conventions (no negative prompts, reference-image limits, etc.) — this skill applies those conventions to one specific job (character sheets), it doesn't re-document the model itself.

## When to build one

Identify recurring subjects by reading the finished shot list, the way a human storyboard artist would — any character or creature named in more than one scene needs a sheet. A one-off background element does not.

**Every distinct subject needs its own sheet — never share one sheet across multiple subjects.** If two different creatures/characters share a shot, the video model has nothing to draw a second identity from if only one sheet exists, and will duplicate the same face/appearance for both. (Confirmed real failure mode: Reimagined Realms 0004 Titanic Stoker — three background stokers in one shot all rendered with identical faces because only one character sheet existed for the production.)

## Usage

```bash
python3 scripts/character_sheet_generation.py "<subject_description>" \
  --out "<production_folder>/Images/Character_Sheets/<Handle>_Sheet.png" \
  --role "<what this subject is, e.g. 'the recurring shark'>" \
  --subject_type person|creature \
  --input_urls <optional real reference photo URLs> \
  --anatomy_notes "<written paragraph of countable/key anatomical facts>"
```

Depends on `kie-cli` (the `gpt_image_2` command) being available and configured — same dependency as the rest of this workspace's GPT-Image-2 usage.

**Naming convention:** name the output file for the subject, e.g. `Shark_1_Character_Sheet.png`, `Main_Pistol_Shrimp_Character_Sheet.png`. Not enforced by the script — this is a human/agent-side convention so the file system stays legible (e.g. glancing at a folder and immediately knowing "that's the shark sheet").

## Layout — 16:9, panels sized to what they show (locked 2026-08-16, real correction)

The first real test on Anomalous Wild (a mantis shrimp character sheet) used a rigid 1:1 aspect ratio with a uniform 3x3 grid — inherited as-is from the original RR script, never independently checked. Tony caught it immediately: a square grid cell clips an elongated subject's full-body panel, because a square isn't wide/tall enough to fit the whole body. **Corrected default: 16:9, and panels are explicitly NOT required to be uniform equal-sized grid cells** — a full-body panel gets more room than a tight close-up panel needs. This was not sourced from any external research (none of the GPT-Image-2 research covered character-sheet layout/aspect-ratio conventions specifically) — it's a direct correction from real output review, now the locked default for every future sheet.

## What the two subject types generate

**`person`** (default — matches the original RR wording exactly, for backward compatibility with existing POV pipelines):
- Top row: front / side / back / full body
- Middle row: neutral expression, focused/exertion expression, face close-up
- Bottom row: hands+forearms close-up, feet+footwear close-up, recurring clothing/props/jewelry close-up

**`creature`** (new — for animals in a nature-documentary context):
- Top row: front / side / back / full body (unchanged — orientation still matters for any subject)
- Middle row: resting/neutral pose, active/alert pose, eyes+face close-up
- Bottom row: distinguishing markings/coloration close-up, the production's key anatomical feature close-up (e.g. claw, fin, lure — whatever this specific story is about), skin/scale/fur texture close-up
- **Additional row (locked 2026-08-17):** a movement/environment pose — the subject in motion within its natural setting (swimming, walking, crawling). Added after a real production's storyboard set kept collapsing into near-identical close-ups: the sheet had no wide/establishing/context material at all for later storyboard generations to draw on, only static studio-style turnaround and close-up panels. This row exists specifically to give Storyboard-Generation's shot-variety rule something real to reference.

Both variants: identical lighting/build/coloration enforced across every panel, no watermark/panel borders. Text is now conditional, not always forbidden — see `anatomy_notes` below. (Note: the "no panel borders" instruction was not fully honored on the first real test — thin grid lines appeared anyway. Cosmetic, not yet independently fixed — treat as a known soft constraint, not a guarantee.)

## Record countable anatomical features explicitly — in both the description AND baked onto the sheet (locked 2026-08-17)

When calling this skill, note in `subject_description` how many of each repeated feature the subject has (e.g. "two independently-moving eyestalks," "four limbs," "one dorsal fin") whenever that count matters to the story. This sheet is the ground-truth reference other skills check generated output against — [`Storyboard-Generation`](../Storyboard-Generation/SKILL.md) requires a specific count-check against this sheet before presenting any storyboard.

**Also pass `anatomy_notes` — a short written paragraph baked directly into the sheet image itself, not just the metadata description that disappears after this one call.** Inspired directly by professional game-style character reference sheets, which pair visual turnarounds with a written attributes/stat block. Confirmed on a real production that GPT-Image-2 renders baked-in text cleanly (see the Storyboard-Generation skill's own text findings), so putting countable-anatomy facts as real text on the reference image gives every later generation that uses this sheet textual grounding, not just a visual one — directly targeting the exact failure this was built to prevent (a later generation dropping an eye, miscounting limbs, etc. because the visual reference alone wasn't specific enough). Example only, not a template to copy verbatim: `"Two independently-rotating compound eyestalks, each mounted on its own movable joint, capable of tracking separate objects simultaneously. One pair of raptorial claws (dactyl clubs) folded beneath the body at rest, extended forward when striking."` Strongly recommended for any `creature` sheet with paired/repeated features; optional but still useful for `person` sheets with anything a later generation could get wrong.

## Feeding the sheet forward

Once generated, this sheet becomes an input reference (`reference_image_urls` / `@ImageN` ordinal tag) on every subsequent shot-generation call involving that subject — see [`Seedance-Prompting-Guide`](../Seedance-Prompting-Guide/SKILL.md)'s character consistency section for how it gets consumed downstream, and its "Storyboard + subject reference" section for combining a character sheet with a storyboard panel in one call.

## Known limitation (carried over from GPT-Image-2-Prompting-Guide)

No source found specifically discussing GPT-Image-2's animal/creature anatomy failure modes (extra limbs, wrong proportions, etc.) — the `creature` mode above is a reasoned adaptation of the well-documented `person` pattern, not independently validated against animal-specific failure data. Run Video-Analyzer's continuity check on any real output using this mode, same as any other new technique in this pipeline.

Two ingested-but-not-yet-case-studied tutorials touch character-reference-sheet
workflows (`007_Resource_Library/Tutorials/Create-Seamless-AI-Films-of-ANY-Length-GPT-Image-2-Seedance-2.0.md`,
`I-Can't-Believe-ChatGPT-Work-Made-This-Whole-Video-From-One-Image.md`) — see
[`Seedance-Prompting-Guide`](../Seedance-Prompting-Guide/SKILL.md)'s "Un-reviewed
reference material" section before treating either as validated technique.
