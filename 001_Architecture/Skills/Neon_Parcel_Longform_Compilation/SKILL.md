---
name: neon-parcel-longform-compilation
description: "Use when Tony asks to create a Neon Parcel long-form animal compilation, analyze reference animal videos for Neon Parcel, or generate Shorts from a Neon Parcel long-form compilation."
trigger: User invokes /neon-parcel-longform or asks for a Neon Parcel long-form compilation
---

# Neon Parcel Long-Form Reference-Inspired Compilation

This is a dedicated pipeline for Neon Parcel YouTube animal compilations. It is
not the Neon Parcel TikTok Shop pipeline and must not route products or
affiliate content here.

## Core Output

- Master video: 16:9, target 6–8 minutes
- Content: many individually generated animal clips with natural durations
- Narrator: one consistent Neon Parcel narrator, added after the rough cut
- In-scene voices: optional and independently directed per clip
- Music: Suno by default, based on the case-study music profile
- Shorts: multiple 9:16 derivatives from the approved master
- Publishing: Blotato only after Tony approves the complete package

## Non-Negotiable Safety Rules

- Preserve all source references, raw generated clips, edits, and renders.
- Never overwrite an approved render; create a new version.
- Reference videos are inspiration unless Tony has documented usage rights.
- Do not copy source dialogue, audio, choreography, framing, or sequence
  shot-for-shot from an unlicensed reference.
- Do not publish or call Blotato without explicit approval.
- Do not activate learned humor rules automatically.

## Intake

Ask:

1. What kind of animal video are we making?
2. Should Tony provide a YouTube reference, should the pipeline search, or
   should reference analysis be skipped?
3. Should generation use the default image-first path or an explicit
   text-to-video path?

If searching, return five clickable YouTube candidates. Search only videos
published between one month and one year ago. Rank using concept fit, views,
views-per-day, engagement, freshness, and competition. Add an Opportunity
badge when a concept has meaningful demand with relatively low competition;
do not make that badge the primary ranking rule.

The initial mode is human selection. Later, a configuration setting may permit
autonomous selection.

## Reference Case Study

For an approved reference, create one folder under:

`002_Content-Creation/Video_Editor/002_Channels/002_Neon-Parcel/Case_Studies/`

Retain the downloaded reference video permanently with its analysis,
transcript, keyframes, and clip boundaries. Run the shared analyzer with:

```bash
python3 001_Architecture/Skills/Video-Analyzer/analyze_reference_video.py \
  "<youtube_url>" \
  --out "<case-study-folder>" \
  --profile production \
  --dense-interval 0.5
```

The production profile must analyze individual clip boundaries, editorial
beats, humor mechanics, music, sound effects, pattern interrupts, retention
techniques, dialogue placement, and originality boundaries. It should describe
why a moment appears to work without requiring Tony to annotate every clip.

Tony may add corrections or observations to the case study. Those corrections
are valuable training data but are optional for every scene.

## Learning Library

Case studies produce proposed reusable humor and editing patterns. Store them
as proposed patterns first. Tony must approve a pattern before it becomes an
active Neon Parcel rule. The director may use approved patterns autonomously,
but must not treat every case study as a rule.

Negative examples matter: when Tony identifies a clip as unfunny and explains
why, retain that critique as a guardrail against generating the same weak
pattern again.

## Shot-List Approval Gate

After the compilation concept and reference study, present:

- A 2–3 sentence brief
- A numbered shot list
- One sentence per clip
- Natural clip duration estimate
- In-scene dialogue, if needed
- Tentative narrator role: none, setup, reaction, context, or transition

Tony may request targeted revisions such as "rewrite shots 3, 7, and 8." Do not
generate the full paid batch until the approved shot list is accepted.

## Generation and Progressive Autonomy

1. Generate Clip 1 and wait for approval.
2. Revise Clip 1 until Tony accepts it.
3. Generate Clips 2–5 individually and wait for approval.
4. Release the remaining approved shots for batch generation only after Tony
   explicitly says to proceed.

Clip durations are emergent. A successful 5-second clip remains 5 seconds and
a successful 12-second clip remains 12 seconds. Trim only to isolate the
payoff or remove unusable material.

Maintain a diversity ledger covering animal appearance, location, camera,
lighting, action, props, sound, dialogue source, and prompt phrasing. Compare
each new prompt against prior prompts before generation to reduce repetitive
patterns while preserving the episode concept.

## Editorial Narration Pass

Assemble the approved clips into a rough cut first. Then write the narrator
script as if the narrator is the editor rewatching the completed compilation.

For each clip, decide:

- Self-explanatory: no narration
- Needs setup: narrator before the action
- Needs reaction: narrator during or after the payoff
- Needs context: short explanatory line
- Dialogue-driven: preserve or generate in-scene dialogue
- Transition: narrator bridges clips

Narration must add perspective, not describe the obvious, and must stay within
the clip it belongs to. Generate the approved narrator track with ElevenLabs
after the narration pass is approved.

## Shorts Derivatives

Create multiple Shorts from the final master. The target duration is 60
seconds, but it is not a hard duration.

- Crop the 16:9 master to 9:16 around the action.
- Use the nearest complete clip boundary.
- Never cut through a clip, action, or narration.
- A Short may end below 60 seconds.
- A Short may exceed 60 seconds when needed to preserve the final complete clip.
- Do not allow narration to cross from one clip into the next.
- Add the opening title overlay only to Shorts.
- Overlay occupies frames 1–30 at 30 FPS.
- Center horizontally, place slightly above vertical center, and respect
  TikTok/Shorts safe padding.
- Do not put the core payoff under the overlay.
- Use Part 1, Part 2, etc. only for the derived Shorts, not the long-form title.

## Final Package and Publishing

Create the long-form title, description, thumbnail, Shorts titles, and report
cards after the final edit is stable. Produce both:

- `Data/Report_Card.md`
- `Data/Report_Card.json`

Wait for Tony's approval of the complete long-form and Shorts package. Only
then use the established Blotato workflow, confirm the Neon Parcel YouTube
account live, set synthetic-media disclosure where applicable, and report the
resulting status.
