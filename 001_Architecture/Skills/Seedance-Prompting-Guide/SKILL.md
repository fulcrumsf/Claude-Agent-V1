---
name: seedance-prompting-guide
description: Use whenever writing or reviewing a prompt for ByteDance Seedance (any version — 1.5 Pro, 2.0, 2.0 Fast, and future releases) — image-to-video or text-to-video generation via kie.ai, WaveSpeed, or fal.ai. Triggers on "write a Seedance prompt", "generate a video with Seedance", "how do I prompt Seedance for dialogue/audio/camera movement", "Seedance negative prompt", or any video-generation task using a Seedance model. Covers native audio control (dialogue vs. ambient/foley-only), camera movement/cinematic shot language, and negative-prompt conventions. This is the living reference — update it in place as new Seedance versions ship, never fork a separate per-version file.
---

# Seedance Prompting Guide (All Versions)

ByteDance Seedance generates video and — since 1.5 Pro — synchronized native audio in the same pass. This guide is the single reference for prompting any Seedance version correctly. Update this file in place when a new version ships; do not create version-specific duplicate skills.

## Core philosophy

Seedance wants **cinematic direction, not image-generation keywords**. Write the prompt like a shot list handed to a director of photography, not a mood-board caption. The model responds to narrative structure across four layers, in this order:

1. **Subject definition** — who/what, framing, setting
2. **Action / key sound events** — what happens, what makes sound (dialogue if any, footsteps, specific foley events)
3. **Environmental audio cues** — the ambient bed (wind, birds, crowd murmur, distant traffic)
4. **Visual style / camera / lighting** — grade, lens feel, camera movement

Source: [Seedance 2.0 Prompting Guide (fal.ai)](https://fal.ai/learn/tools/seedance-2-0-prompting-guide), [How to Use Seedance 2.0 Like a Pro (fal.ai)](https://fal.ai/learn/tools/how-to-use-seedance-2-0)

## Audio control

Seedance's audio generation is driven entirely by prompt content plus one boolean parameter — there is no separate "audio prompt" field.

### The `generate_audio` parameter

- Boolean, defaults to `true` on 1.5 Pro (confirmed live via `wavespeed schema bytedance/seedance-v1.5-pro/image-to-video`).
- Set explicitly per call — never assume the platform default matches what you want.
- When `false`, no audio track is generated at all (silent output) — useful if the pipeline plans to add all audio in post (e.g. a dedicated Foley/music pipeline stage) instead of relying on native generation.

### Dialogue — triggered by quotation marks

**Putting a spoken line in double quotes inside the prompt is the trigger for lip-synced dialogue.** Example:

> A barista leans over the counter and says, "Your usual, right?" with a warm smile.

The model lip-syncs the quoted line to the character's mouth. This works for both 1.5 and 2.0.

**To avoid dialogue entirely: never include quoted spoken lines in the prompt.** There is no separate toggle to "turn off" the lip-sync mechanism other than simply not writing quoted speech — the presence of quotes IS the mechanism.

Source: [Seedance 1.5 Prompt Guide (fal.ai)](https://fal.ai/learn/devs/seedance-1-5-prompt-guide)

### Ambient / foley-only sound (no dialogue)

Treat the prompt like **a sound brief**, not a vague mood description — name the specific sounds you want in the mix as concrete nouns/events (footsteps on packed dirt, water sloshing, distant birds, crowd murmur), not abstract adjectives (avoid "atmospheric sound"). An open-ended prompt tends to default toward whatever was most common in training data (often music-forward, "ad-like" scoring) rather than a clean ambient/foley mix.

### Negative prompts — explicitly excluding unwanted audio/visual elements

Seedance defaults toward elements common in its training distribution unless told otherwise — background music, on-screen captions, logos/watermarks, and even incidental extra people/objects can "sneak in" even when not requested, because the model has seen so many clips containing them.

**Convention:** a single closing line, beginning with a dash, listing every forbidden element by name. Their own universal example (documented as "the universal nine word closer"):

> `- No music, No logo, no text on screen.`

Adapt per-project. For a no-dialogue, foley-only, no-baked-music POV Short (our own convention — see "Our locked convention" below):

> `- No dialogue, no spoken words, no voiceover, no lip sync, no music, no on-screen text.`

Source: [Seedance 2.0 Negative Prompts Guide (videoai.me)](https://videoai.me/blog/seedance-2-0-negative-prompts)

## Camera movement / cinematic shot language

- Describe **how** the camera moves, not just what's in frame — this is the single biggest gap between amateur-looking and cinematic-looking output.
- Universal template: **Subject + Camera movement + Modifier + Lighting + Style**
- Modifiers like "smooth," "aggressive," or "handheld" set the emotional register of the movement (calm/controlled vs. urgent/chaotic).
- **Never stack more than 2-3 camera instructions in one prompt** — more than that and the model's motion output degrades/conflicts.
- `camera_fixed` boolean parameter (1.5 Pro, confirmed via WaveSpeed schema) locks the camera to a static position — set `true` for POV static shots (e.g. sitting, eating, watching), `false` (default) when you want camera motion (walking POV, tracking shots).

Example (from fal.ai's own guide):

> A flamenco dancer in a deep red dress drops into a low spin on a worn wooden stage, the skirt flaring wide before she snaps upright and stamps twice, dust lifting in the single hard spotlight above her. Shot from a low front angle on a long lens, the background falling into black, a warm amber grade with hard-edged shadows.

Source: [Seedance 2.0 Prompting Guide (fal.ai)](https://fal.ai/learn/tools/seedance-2-0-prompting-guide)

## Version-specific API parameters

**Seedance 1.5 Pro** (confirmed live via `wavespeed schema bytedance/seedance-v1.5-pro/image-to-video`, 2026-08-01):

| Field | Type | Notes |
|---|---|---|
| `prompt` | string | required |
| `image` | string | required — first-frame reference (image-to-video mode) |
| `last_image` | string | optional — last-frame reference for interpolation |
| `aspect_ratio` | enum | `21:9`, `16:9`, `4:3`, `1:1`, `3:4`, `9:16` |
| `duration` | integer | default 5, range 4-12 (seconds) |
| `resolution` | enum | `480p`, `720p` (default), `1080p` |
| `generate_audio` | boolean | default `true` |
| `camera_fixed` | boolean | default `false` |
| `seed` | integer | `-1` = random |

**Seedance 2.0 / 2.0 Fast:** same core prompting philosophy (4-layer structure, quote-triggered dialogue, dash-led negative-prompt closer) — check the live schema (`wavespeed schema <model-id>`, or `kie-cli --help` / the platform's own docs) for exact parameter names/ranges before each new integration, since ByteDance has been shipping frequent version updates and defaults can shift. **Never hardcode assumed parameter values from this table into new code without a live schema check first** — this table is a snapshot, not a guarantee.

## Related but distinct tool: Seed Audio 1.0

ByteDance also ships **Seed Audio 1.0** (`bytedance/seed-audio-1.0` on fal.ai) — a standalone audio-only generation model, not part of Seedance video generation. It produces multi-character dialogue, sound effects, ambience, and music from a single text prompt, independent of any video. Two modes: text-to-speech (dialogue only) and text-to-audio (full cinematic mix with dialogue + sound design). Useful as a future option for post-hoc full audio-scene generation decoupled from video generation, but **not currently used in any Agent-OS pipeline** — Seedance's own `generate_audio` (synced to the video it's generating) is what we use today. Source: [How to Use Seed Audio 1.0 (fal.ai)](https://fal.ai/learn/tools/how-to-use-seed-audio), [What Is Seed Audio 1.0? (MindStudio)](https://www.mindstudio.ai/blog/what-is-seed-audio-1-0-bytedance)

## Our locked convention (Reimagined Realms POV Shorts)

For the POV Shorts pipeline (`001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/`), every Seedance prompt must:

1. Never include quoted spoken dialogue — these videos have no dialogue by design.
2. Name specific foley/ambient events concretely (footsteps, sloshing, birds, wind, crowd murmur) rather than vague mood words.
3. End with a negative-prompt closing line: `- No dialogue, no spoken words, no voiceover, no lip sync, no music, no on-screen text.` (the "no music" clause matters specifically for us — Suno generates the separate music layer, so Seedance's native audio should stay foley/ambient-only, not compete with its own score).
4. Use `generate_audio=true` (this pipeline uses Seedance's native audio instead of a separate Foley-model step — see `001_Architecture/Superpowers/Specs/2026-08-01-RR-POV-Shorts-Pipeline-Design.md` for the decision history).
5. Set `camera_fixed` per the shot: `true` for static POV vignettes (eating, sitting, watching), `false` for walking/handheld/tracking shots — per `POV_Style_Guide.md`'s camera conventions.
