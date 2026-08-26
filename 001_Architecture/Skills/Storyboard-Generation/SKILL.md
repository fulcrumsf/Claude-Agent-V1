---
name: storyboard-generation
description: Use whenever a video production needs a per-scene storyboard — a single image showing 6-12 sequential frames of a shot's progression, used to plan shot composition and camera movement before spending on real video generation. Triggers on "build a storyboard", "storyboard this scene", "generate a storyboard sheet", or any pipeline step converting a scene's beat/shot list into a visual planning reference. Channel-agnostic — works for Anomalous Wild, Reimagined Realms, or any future channel; only the visual style and scene content change per channel, never the template structure.
---

# Storyboard Generation

Generates one storyboard sheet per scene: a grid of 6-12 sequential frames showing how that scene's shot progresses from start to finish, each frame labeled and captioned, used to plan composition/camera before any real video generation runs.

**Locked 2026-08-16 after two real production tests** on `0002_Mantis_Shrimp_Color_Vision` (Anomalous Wild) — see "Why this structure" below for what was tried and rejected first.

## Before using this skill

Read [`GPT-Image-2-Prompting-Guide`](../GPT-Image-2-Prompting-Guide/SKILL.md) first for the underlying model's prompting conventions. Read [`Character-Sheet-Generation`](../Character-Sheet-Generation/SKILL.md) if the scene has a recurring subject — that sheet gets passed as a reference image here.

## What's locked vs. what's always caller-supplied

**Locked (the template structure — never changes per channel):**
- Frame count formula: `compute_frame_count(duration_s)` — roughly 1 frame per 1.25s, clamped to [6, 12]
- Prompt structure: four blocks in this order — `Scene:` → `Visual style:` → `Storyboard sequence:` (one line per frame) → closing consistency directive
- Panel convention: thin black borders between panels, bold sans-serif frame-number badge top-left of each panel, one-line caption in a plain white strip beneath each panel
- Text is baked into the image by the model itself in this skill — not composited separately. See "Why baked text, not composited" below for why this differs from the diagram sub-pipeline's rule.

**Always caller-supplied (per production, per channel — never hardcode):**
- `scene_description` — who/what/setting for this specific scene
- `visual_style` — the channel's own aesthetic (Anomalous Wild's dark neon nature-doc palette, Reimagined Realms' cinematic historical look, or any future channel's own style)
- `frames` — the actual per-frame action list, sized to match `compute_frame_count()`'s output for that scene's real duration (pulled from `Beat_Table.json` or equivalent)

## Usage

```python
from storyboard_generation import build_spec, generate_storyboard

spec = build_spec(
    scene_id="Scene_07",
    duration_s=28.329,                    # from Beat_Table.json
    scene_description="...",              # per-scene, per-channel
    visual_style="...",                   # per-channel — this is the only channel-specific knob
    frame_actions=["...", "...", ...],    # length MUST match compute_frame_count(duration_s)
)
generate_storyboard(spec, output_path, reference_image_urls=[character_sheet_url])
```

Or via CLI: `python3 scripts/storyboard_generation.py <spec.json> --out <path> --reference_image_urls <url>`

`build_spec()` raises if `frame_actions` doesn't match the computed frame count — this is intentional. Getting the beat breakdown right per scene is the caller's job (derived from the real shot list), not something this script silently pads or truncates.

## Writing `frame_actions` — shot variety and anatomical precision (locked 2026-08-17, real production findings)

Two real, confirmed problems found on a real production's storyboard set, both caused by how `frame_actions` gets written, not by the model:

**1. Visual coverage does not need to literally illustrate every narration topic — and shot composition must change dramatically at least every ~3 seconds of scene duration (locked 2026-08-17, sharpened after a first pass at this rule wasn't concrete enough).** Roughly every 2 frames at this skill's ~1.25s-per-frame rate. "Change dramatically" means varying BOTH framing (wide/medium/close/extreme-close) AND subject/content — not just a progressively tighter zoom on the same fixed thing. A true wide establishing shot, a b-roll cutaway of movement or environment, a different anatomical feature or body part — real alternatives, not camera-distance variations on one subject. No single feature or subject should dominate more than roughly half of a scene's total frames, even if the narration talks about that feature the whole time — bookend a detail-heavy sequence with establishing/context shots rather than filling the whole scene with it. (Example only, not a rule to copy literally: a scene narrating a creature's eyes could open on a wide shot of it moving through its environment, cut to a medium shot, then push into the eye only for the back portion of the scene — not eye close-ups start to finish.) The first version of this rule ("just vary the shots sometimes") produced replacement frames that were still too similar to what they replaced — a same-subject close-up swapped for another same-subject close-up. The fix has to be a genuinely different shot concept, verified against a real reference (a professional storyboard/shot-list example, not just a mental checklist) before locking in a scene's frame list.

**2. State anatomical counts explicitly — never rely on implied plurality.** For any subject with more than one instance of the same feature (two eyes, multiple limbs, etc.), a frame description must say how many are visible and what each one is doing. Writing "the eye rotating" or "the eyestalk" (singular) does not mean "focus on one of the two eyes while the other stays present" — the model follows the words literally and generates exactly one eye, with the second nowhere in frame at all. Confirmed on a real production: writing singular anatomical language produced storyboard frames where a two-eyed subject appeared to have only one eye, across multiple scenes, because the prompts said "the eye" instead of "both eyes, one of them rotating." Use singular language only when a single-feature shot is genuinely intended, and know that doing so will produce exactly that — not "mostly one, with the other implied."

## Mandatory anatomy check against the character sheet (locked 2026-08-17)

After generating any storyboard for a subject that has a [`Character-Sheet-Generation`](../Character-Sheet-Generation/SKILL.md) reference, check every frame against that sheet's documented canonical anatomy **before presenting the result** — not a general "does this look plausible" glance, but a specific count-check against what the sheet documents (e.g., if the sheet shows a two-eyed subject, count eyes in every frame). A real production review initially passed several scenes as "fine" on a general look-over, then found on a targeted re-check that multiple frames across multiple scenes were missing an eye entirely — the general review had missed what a specific, deliberate count-check caught immediately. Do the specific check every time, not just when something looks off.

## Why this structure (what was tried and rejected)

**Rejected: repeating style+content+camera in every frame line.** The first real test (Scene_01, a near-static macro-eye shot) used a prompt that repeated the full style/subject description inside each frame's instruction, plus a separate rigid "camera: static" field. Result: all 6 frames looked nearly identical, camera framing itself drifted between frames despite being told not to, and only one part of the subject weakly animated.

**Adopted: three labeled blocks + natural-language shot type, informed by a real published tutorial.** Restructuring into `Scene:` / `Visual style:` / `Storyboard sequence:` (written once each, not repeated per frame), with shot type embedded naturally in each action sentence ("Close-up as...", "Extreme close-up, the...") instead of a separate rigid camera field, and a closing "keep this consistent" directive — confirmed via direct comparison against a real tutorial's prompt for a similar storyboard-to-video workflow. Re-tested on Scene_07 (12 frames, a genuinely dynamic strike sequence): real per-frame visual progression, correct shot-type variety, clean consistent character throughout. Tony approved this as the locked template.

**Frame count must come from real scene duration, not a guess.** A near-static 7.5s scene and a dynamic 28s scene need different frame counts to actually show their content — hardcoding "always 6" or "always 12" would either pad a short scene with redundant frames or under-cover a long one. `compute_frame_count()` exists specifically so this is computed the same way every time, not eyeballed.

## Why baked text, not composited (a deliberate exception to this pipeline's usual rule)

Everywhere else in this pipeline (scientific diagrams, character sheets), text/labels are composited separately in Remotion or Pillow, never generated by the AI model — because an older model generation produced garbled, unreliable text. This skill is a **confirmed exception**: real testing on 2026-08-16 with the current GPT-Image-2 showed completely clean, legible baked-in frame numbers and captions across two separate tests (6 frames and 12 frames), with zero garbling. Do not assume this generalizes to other models or contexts — if a future test on this same skill shows garbled text, fall back to generating the same frame layout with the caption/label instructions removed, leaving reserved white margin space (already part of the panel convention) for compositing real text in afterward. That fallback path was designed in from the start; it just hasn't been needed yet.

## Feeding the storyboard forward

Pass the finished storyboard sheet as a reference image alongside the character sheet on the actual shot-generation call — see [`Seedance-Prompting-Guide`](../Seedance-Prompting-Guide/SKILL.md)'s "Storyboard + subject reference" section for how a storyboard and character sheet combine in one Seedance call via `@Image1`/`@Image2` ordinal tags.
