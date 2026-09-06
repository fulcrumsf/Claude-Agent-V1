---
name: gpt-image-2-prompting-guide
description: Use whenever writing or reviewing a prompt for OpenAI's GPT-Image-2 (image generation/editing) via kie.ai or the OpenAI API directly. Triggers on "write a GPT-Image-2 prompt", "generate a character sheet", "generate an environment sheet", "generate a storyboard", "generate a reference image", "GPT Image 2 negative prompt", or any image-generation task feeding a video pipeline (Anomalous Wild, Reimagined Realms, or any future channel). Covers model identity/versioning, reference-image capacity, prompt structure, character/creature reference sheets, multi-panel storyboard generation, and known limitations. This is the living reference — update it in place as the model updates, never fork a separate per-version file.
---

# GPT-Image-2 Prompting Guide

OpenAI's current-generation image model, used across Agent-OS video pipelines for character/creature reference sheets, environment sheets, storyboard panels, and labeled scientific diagram illustrations. This guide is the single reference for prompting it correctly — update in place as the model updates, do not fork a version-specific duplicate.

Every claim below is sourced. Where research came up thin or empty, that gap is stated explicitly rather than filled with a guess — check the "Known gaps" section before assuming this guide covers something it doesn't.

## Model identity (confirmed, do not assume otherwise)

**Current model: `gpt-image-2`** (default snapshot `gpt-image-2-2026-04-21`), released April 21, 2026. Replaced both DALL-E 3 and the interim `gpt-image-1.5`. Adds a reasoning/"thinking" pass before generating, runs on a GPT-5.4 backbone, and improves instruction-following, layout accuracy, and text rendering (including multilingual text) over prior versions.

Version history, for context when reading older docs/tutorials that may reference an earlier model:
- `gpt-image-1` — Mar 25, 2025 (originally shipped as "GPT-4o image generation")
- `gpt-image-1-mini` — Oct 6, 2025 (80% cheaper variant)
- `gpt-image-1.5` — Dec 16, 2025 (faster edits, fixed cropping/color-bias issues)
- `gpt-image-2` — Apr 21, 2026 (current)

Sources: [OpenAI dev community announcement](https://community.openai.com/t/introducing-gpt-image-2-available-today-in-the-api-and-codex/1379479), [OpenAI model page](https://developers.openai.com/api/docs/models/gpt-image-2), [Wikipedia — GPT Image](https://en.wikipedia.org/wiki/GPT_Image), [Latent.Space AINews](https://www.latent.space/p/ainews-openai-launches-gpt-image)

## Access via kie.ai (confirmed live, not guessed)

Model IDs on kie.ai: `gpt-image-2-text-to-image` and `gpt-image-2-image-to-image`, called via kie.ai's generic task endpoint (`POST https://api.kie.ai/api/v1/jobs/createTask`) — not a dedicated GPT-Image-2 endpoint.

**Platform routing rule (locked 2026-08-18): use kie.ai when it's cheaper AND the job doesn't need a capability kie.ai's wrapper lacks. Use direct OpenAI when a needed capability isn't exposed by kie.ai, regardless of price.** Concrete confirmed gap: `kie-cli gpt_image_2 --help` exposes no `background`/transparency parameter at all (only `prompt`, `input_urls`, `aspect_ratio`, `resolution`, `callBackUrl`) — a job that needs true alpha-transparent output (e.g. an isolated component asset for layered Remotion compositing, see [`Motion-Graphics-Compositing`](../Motion-Graphics-Compositing/SKILL.md)) must route to direct OpenAI's `background: "transparent"` parameter instead, even though kie.ai is cheaper per image ($0.03 vs $0.04, per `model_catalog.json`'s `capabilities` block on the `gpt-image-2` entry). Check Tool-Manager's catalog `capabilities` field before defaulting to kie.ai out of habit.

- **Reference images:** up to **16** per call (`input_urls` array) on the image-to-image variant — nearly double Seedance 2.0/2.0 Fast's 9-image cap.
- **Prompt length:** up to 20,000 characters.
- **Aspect ratios:** fixed list — `1:1, 3:2, 2:3, 4:3, 3:4, 5:4, 4:5, 16:9, 9:16, 2:1, 1:2, 3:1, 1:3, 21:9, 9:21, auto`.
- **Resolution:** 1K/2K/4K — 4K is **not available at 1:1** aspect ratio.

Source: [docs.kie.ai/market/gpt/gpt-image-2-image-to-image](https://docs.kie.ai/market/gpt/gpt-image-2-image-to-image)

## Negative prompts — not supported, fold exclusions into the positive prompt

There is **no `negative_prompt` parameter** on this model — confirmed both by OpenAI's own API surface (only quality/size/format/compression/n-style params exist) and by a third-party CLI wrapper that explicitly drops the parameter locally because the model rejects it. There's also **no `seed` parameter**.

**The fix:** state exclusions as explicit constraints inside the positive prompt — e.g. `"no watermark, no border, no extra text"`, `"preserve identity/geometry/layout exactly"`. OpenAI's own cookbook and fal.ai's guide both treat this as functionally equivalent to a negative prompt, not a lesser workaround.

Sources: [OpenAI Cookbook — GPT Image Generation Models Prompting Guide](https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide), [fal.ai — Prompting GPT Image 2](https://fal.ai/learn/tools/prompting-gpt-image-2), [PixVerse GPT Image 2 review/guide](https://pixverse.ai/en/blog/gpt-image-2-review-and-prompt-guide)

## Prompt structure

Consistent guidance across OpenAI's own Cookbook and fal.ai's independent guide:

1. **Order matters:** background/scene → subject → key details → constraints. Use line breaks or labeled segments for a complex prompt, not one dense paragraph.
2. **Specificity beats hype words.** Concrete materials/lighting/lens language ("overcast daylight, brushed aluminum, 50mm feel") outperforms generic quality tags ("8K, ultra-detailed, masterpiece") — fal.ai reports the latter simply "don't render" as meaningful signal.
3. **The constraints section is where mediocre prompts fail silently** (fal.ai's phrasing) — always state explicitly what must NOT change, especially on any generation meant to preserve identity from a reference image.
4. **Text-in-image:** wrap literal text in quotes or ALL CAPS, specify font/size/color/placement, spell hard words letter-by-letter if accuracy matters.
5. **Format flexibility:** minimal prompts, descriptive paragraphs, JSON-like structured prompts, and tag-based prompts all reportedly work, as long as intent is unambiguous — there's no single mandated format.
6. **Iterate small.** One change per follow-up turn rather than a full rewrite; repeat the "preserve" list every iteration to fight drift.

Sources: [OpenAI Cookbook prompting guide](https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide), [fal.ai prompting guide](https://fal.ai/learn/tools/prompting-gpt-image-2)

## Character/creature reference sheets

The "character anchor" pattern, converging across OpenAI's own cookbook example and a field-tested third-party workflow:

1. **Generate one clean reference sheet first** — front view + profile, clean/neutral background, **the name written on the image itself**. The written label matters: the model pattern-matches against the visual *and* its label, rather than reconstructing appearance from a text description alone each time.
2. **Attach that sheet as an input image on every later generation**, and restate invariant traits explicitly every time: "same coloring, same proportions, same markings, do not redesign the character."
3. **For animals/creatures** (this workspace's primary use case, e.g. Anomalous Wild): the same pattern applies directly — a labeled multi-angle sheet of "the mantis shrimp" or "the shark," reused as an input image on every subsequent shot-generation call for that creature.
4. **Two-sheet technique for stronger control:** a head/face-detail sheet for identity, plus a separate full-body sheet when body markings, coloration, or proportions matter beyond the head. Default to the head sheet; add the full-body sheet only when the shot needs it.
5. **Fresh session per generation** is recommended by one field report, attaching only the reference sheet(s) actually needed for that call — this avoids context-accumulation drift and matches how this workspace's pipelines already call the API statelessly per-shot.

Sources: [OpenAI Cookbook — image-gen-1.5 prompting guide](https://developers.openai.com/cookbook/examples/multimodal/image-gen-1.5-prompting_guide) (character-anchor workflow), [How to Get Consistent Character Images in ChatGPT Images 2.0](https://aimeetsgirlboss.substack.com/p/how-to-get-consistent-character-images) (two-sheet technique, field-tested, non-official)

## Environment sheets

No dedicated official guide was found for environment sheets specifically (see gaps below), but the same character-anchor mechanism applies by extension: generate one labeled environment reference (e.g. "the mantis shrimp's reef burrow"), reuse it as an input image on every shot set in that location, and restate invariant details ("same coral formation, same lighting, same burrow entrance shape") each time. Cross-reference the Seedance skill's Environment/location reference sheets section for how this feeds into video generation once the image sheet exists.

## Multi-panel storyboards

- **Official guidance:** define the narrative as a sequence of clear visual beats, one per panel — "Panel 1: X happens… Panel 2: Y happens…" — concrete and action-focused, not abstract.
- **Field-tested grid technique** (Devtalk forum — concrete, on-point for a video pipeline, but not an official OpenAI source): generate a 3×3 grid in a single call, one panel per shot, then feed that whole grid image into the video model with per-panel motion prompts. Reported advantages: pacing locks before any video spend, and character consistency is stronger because all panels come from one unified generation rather than separate calls. Whether 4×4 grids hold up for longer sequences is an open question in that same thread — no confirmed answer found either way.
- **Real constraint:** once a multi-panel grid is generated as a single image, individual panels can't be cleanly re-edited without regenerating the whole set. Plan around this — don't design a workflow that assumes selective panel redo is possible.
- **Expect a real failure rate, not a solved problem.** One review-style source (PixVerse, moderate caliber, not official) reported 8-panel batches achieving usable continuity on roughly 5–6 of 8 panels with "Thinking mode" on, with 2–3 needing a face re-roll. Budget for reroll passes on any multi-panel storyboard generation.

Sources: [OpenAI Cookbook prompting guide](https://developers.openai.com/cookbook/examples/multimodal/image-gen-1.5-prompting_guide), [Devtalk — GPT Image 2 + Seedance 2.0 storyboard grid thread](https://devtalk.com/t/gpt-image-2-seedance-2-0-pipeline-whats-your-experience-with-the-storyboard-grid-approach/242365), [PixVerse GPT Image 2 review/guide](https://pixverse.ai/en/blog/gpt-image-2-review-and-prompt-guide)

**Scaling the storyboard to the scene, not to a fixed panel count:** a scene's storyboard should have however many panels match that scene's actual shot count — 1, 2, or 3 panels (wide / medium / close-up / reverse-angle) for a short scene, not a fixed grid size. The 3×3/8-panel grid technique above is for storyboarding an entire multi-shot sequence in one image; a single scene within a larger production typically needs far fewer panels.

## Optional workflow additions — use only when the task calls for them

These techniques came from the reviewed GPT Image 2 workflows. They are **extras**, not mandatory stages. The agent should select them based on the job's risk, complexity, and iteration needs rather than applying the entire list by default.

### 1. Short idea → expanded production prompt

When the user provides only a brief concept and the image will become a production reference, first expand the idea into a structured prompt using the normal order: scene/background → subject → key details → constraints. Preserve the user's concept and do not invent story beats that change its intent. For a simple image or a tightly specified edit, skip expansion and use the user's instructions directly.

### 2. Storyboard correction loop

When a storyboard has repeated panels, continuity errors, ambiguous object positions, or an impossible visual state, use the generated storyboard as an input reference and request a corrected storyboard. State exactly what must change and what must remain unchanged. This is a pre-video quality gate; do it before spending video-generation credits. Do not use this loop merely to make a satisfactory storyboard more elaborate.

### 3. Storyboard continuation

When a sequence is longer than one storyboard page, attach the completed page and ask for the next page while preserving the established characters, environment, camera language, lighting, and visual style. Treat the new page as a continuity draft that still requires review. Do not assume continuation guarantees exact identity or composition across calls.

### 4. Brief-to-storyboard shortcut

When the user wants rapid ideation, a one-sentence concept can be converted into a panel-by-panel storyboard draft. Use explicit visual beats rather than abstract labels. This is a planning shortcut, not a substitute for detailed prompting when the storyboard controls complex action, physical continuity, or a paid video generation.

### 5. Structured character data block

When recurring characters or creatures must remain consistent across several images, place invariant details in one reusable block: identity, age or species, proportions, coloring, markings, clothing, accessories, and behavior. Attach the appropriate reference sheet and repeat the invariant block on each generation. Use only the details relevant to the shot; an unnecessarily large block can compete with the actual scene direction.

### 6. Compare before committing

When the image is a high-cost or high-impact production anchor and more than one compatible image route is available, generate a small comparison set using the same brief and constraints before committing to a model, resolution, or platform. Compare composition, continuity, anatomy, text/layout accuracy, and style adherence separately. Skip this for routine images or when the user has already selected the model and the task is an iteration of an approved direction.

**Decision rule:** choose the smallest optional workflow that reduces the specific risk. For example, use prompt expansion for an underspecified idea, storyboard correction for a visual continuity error, character data for identity drift, continuation for a multi-page sequence, and comparison only when the model/platform choice is genuinely uncertain. Never combine optional techniques automatically just because they are available.

## Cross-session style/palette consistency — real, sourced gap

This is the weakest-sourced topic in this guide, and the gap is being stated plainly rather than papered over:

- OpenAI's own docs admit the limitation directly: "the model may occasionally struggle to maintain visual consistency for recurring characters or brand elements across multiple generations."
- The only sourced mitigation: **describe style concretely, not by reference-name.** fal.ai's guidance — "name the parts rather than saying 'same style'" (e.g. "chunky pixel forms, limited arcade palette, bright glow accents" instead of "same style as before") — because abstract style callbacks don't reliably carry information across genuinely separate API calls/sessions.
- No official documentation exists for a session/thread-persistent "style seed" mechanism on the plain Images API. (The Responses API's multi-turn image editing maintains state within one conversation thread, but that doesn't help across separate calls/sessions, which is how this workspace's pipelines call the API today.)
- **If tighter cross-scene/cross-production style guarantees are ever needed:** the two available levers are (a) always carrying forward the same locked style-description block verbatim into every prompt, and (b) attaching a previously-generated "canon" image as a reference input on every subsequent call. Neither is confirmed to fully solve drift — both are the best documented options available.

Sources: [OpenAI Image Generation guide](https://developers.openai.com/api/docs/guides/image-generation), [fal.ai prompting guide](https://fal.ai/learn/tools/prompting-gpt-image-2)

## Known limitations / failure modes

- Multi-panel grids can't be selectively re-edited (see Storyboards above).
- Multiple faces in one image, and CJK/Arabic/Hebrew text rendering, remain weak points even in the current model.
- Resolution above 2560×1440 is explicitly flagged "experimental" by OpenAI's own cookbook, with "more variable results."
- Detailed camera/lens specs "may be interpreted loosely" per official docs — treat as compositional guidance, not physical simulation.

## Known gaps — do not assume these are solved

Stated explicitly per this guide's sourcing standard — do not fill these in with a plausible-sounding guess if the question comes up:

- **Animal/creature anatomical accuracy:** no source found discussing GPT-Image-2-specific failure modes for animal/creature anatomy (extra limbs, wrong joint counts, anatomically implausible features). General AI-image anatomy-error discussion exists but isn't model-specific, so it isn't cited here as if it were. The model is only ~4 months old as of this research, which likely explains the sparse community data — reassess this section periodically as more real-world use accumulates.
- **Community discussion generally (Reddit/GitHub):** thin, for the same reason — the model is too new for much organic troubleshooting content yet.
- **Environment sheets specifically:** no dedicated official or field-tested guide found; the guidance above is extrapolated from the character-sheet mechanism, not independently sourced.
- **Single-panel storyboard + character-sheet combination in one Seedance call** (as opposed to a full multi-panel storyboard): this is a Seedance-side question, not a GPT-Image-2 one — see the Seedance-Prompting-Guide skill's "single-panel storyboard + character sheet(s) combined" section for the current state of that research.

## Related skill

[Seedance-Prompting-Guide](../Seedance-Prompting-Guide/SKILL.md) — once a character sheet, environment sheet, or storyboard panel is generated here, that image becomes an input reference for Seedance video generation. This skill only covers building the still images; Seedance's skill covers turning them into video.
