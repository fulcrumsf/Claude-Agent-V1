# Cinematic Narrative / Multi-Character — Seedance Prompting (Style 2)

Supporting reference for [`SKILL.md`](./SKILL.md)'s Style 2. Everything in the main file's Core sections still applies here — the audio parameter, dialogue-via-quotes trigger, negative-prompt conventions, camera-movement language, hand/limb laterality, and general character-consistency mechanics (`@Image1`/`@Image2` ordinal tagging, named-tag alternative, blacked-out-faces technique) are all shared and documented there. This file only covers what's *different* for third-person, multi-character storytelling: characters interacting on screen (two-shots, over-the-shoulder, wide coverage), possibly speaking to each other.

**Not currently used by any pipeline.** `Reimagined_Realms_Video_Pipeline` has a documented placeholder ("future versions may support voiced character dialogue... not in scope for the current voiceover-only pipeline") that this style would serve whenever that gets built. Example scenario this is written for: a scene like a commander ordering a lieutenant to ready troops before dawn — narration sets the scene, then two named characters interact and speak.

## The Variant template system

The richest single find across the whole Seedance case-study research pass was a page from one creator's own production "Bible" — a reference document their prompting agent reads before generating anything. It defines named, reusable prompt shapes ("Variants") keyed to what reference assets exist for a given shot, instead of reinventing prompt structure per shot. Verbatim, from **Variant C** (character sheets + storyboard grid together — the highest-fidelity case):

> **Variant C - Character sheets + storyboard grid**
> Use when: the user has both character sheets AND a storyboard grid. This is the highest-fidelity setup — characters are locked by the sheets, motion and framing are locked by the grid.
>
> Character 1: @image1
> Character 2: @image2
>
> Use the provided character sheets and cinematic storyboard grid [@image3] as visual and motion reference. Create a 15-second cinematic sequence as sequential shots, one image. Follow the storyboard panel order, camera logic, motion arrows and camera framing consistently and temporally.
> NO TEXT ON SCREEN, NO MUSIC.
>
> Storyline:
> [Fill briefly from the storyboard.]

**The renumbering rule (mechanical, not a judgment call):** if there's only one character sheet, drop "Character 2" and renumber the storyboard grid to `@image2`. If there are three character sheets, they become `@image1`/`@image2`/`@image3` and the grid becomes `@image4`. The structure stays identical — only the numbers shift with however many character sheets are actually in play for that shot.

(Source: "The Only Workflow You Need to Turn a Storyboard into an AI Video," `Universal_Case_Studies/009_Only_Workflow_Storyboard_Into_AI_Video/Keyframes/022.jpg` — full page transcription in that folder's `ANALYSIS.md`)

**Other named variants referenced in the same document (not fully captured on screen):** "Variant A" appears to be the dialogue-scene variant — see "Dialogue convention" below, which cites it directly. Treat the Variant system as extensible: if a shot's reference-asset combination doesn't match Variant C above, follow the same pattern (state what's provided, state the fixed instruction shape, state the renumbering rule) rather than freeform prompting.

## Audio-default policy for this style

Default to **no music** unless the shot explicitly calls for it or names a specific track/mood. Rationale, stated directly in the source Bible: audio baked into a generation at the point of creation can't be cleanly stripped back out afterward — so leaving it silent (or foley/ambient-only, per Core) keeps the option open to score cuts separately in the edit. Only bake in music when a shot is deliberately being generated as a finished, standalone piece with its own intended soundtrack, not as raw material for a larger edit. This is the same underlying reasoning as Style 1's "no music" rule in the main `SKILL.md` — the two styles arrived at the identical rule for the identical reason, independently.

## Dialogue-in-timeline convention

When a shot needs spoken dialogue, the source Bible bakes it directly into a TIMELINE breakdown, in quoted brackets, with the speaking character explicitly named — not just floating generic dialogue text. Combine this with `SKILL.md`'s Core "Dialogue — triggered by quotation marks" section (the quote-marks mechanism itself is unchanged; this just adds *where* and *how* to attribute the line when more than one character is in the shot).

Example shape, applied to the Kingdoms and Conquerors-style scenario this style is meant for:

> Genghis Khan turns to his lieutenant and says, "We move on the village at dawn. Ready the soldiers." The lieutenant nods once and turns to relay the order.

Attribute every line to the specific character speaking it (by name, matching however that character is tagged/named in the reference set) — never leave it ambiguous which of several characters in frame is talking.

## Real production example — inline continuity clauses inside a multi-character prompt

A working kie.ai Seedance 2.0 prompt (partially legible, transcribed verbatim) shows the Variant-style structure in actual use, combining `@Image` role-tagging with the inline continuity/anti-hallucination clauses documented in `SKILL.md`'s Core "Negative prompts" section:

> No dialogue. Face stable. No deformation. Hands anatomically correct, no extra fingers, no warping. [@Image] is the environment — washitsu interior, shoji screens glowing warm tungsten in the background, tatami floor, hearth embers casting low firelight. [@Image] is the son — samurai 20s, gray-charcoal robes, hair tied back, seated in foreground silhouette, out of focus. [@Image] is the father — samurai 50s, black robes with white family crest, graying hair tied back, gray beard, black blindfold tied firmly in every shot. Blindfold stays tied throughout — never removed, never touched, never slips... Father remains seated in seiza facing the son across the hearth. Positions never swap. 0-2s: Starting frame matches [@Image] exactly...

Notice the pattern: each `@Image` reference gets a one-line role description right where it's introduced (not just a bare tag), and scene-specific continuity rules ("positions never swap," "blindfold never slips") are stated inline as part of that character's description, not only in a closing negative-prompt line. This is the practical, working version of the Variant C template above.

(Source: `Universal_Case_Studies/002_Seedance_2.0_GPT_Image_2_Character_Environment_Consistency/Keyframes/019.jpg`)
