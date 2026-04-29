---
title: "Prompt Best Practices — Video Editing Agent"
type: guideline
domain: video-production
tags: [guideline, video-production, kie-ai, video-generation, ai-agents]
---

# Prompt Best Practices — Video Editing Agent

> **How to use this guide:**
> When writing prompts for scene generation, first identify the model you're using (or select one using the decision matrix), then follow the model-specific guidance below. Always check the active channel's `.md` file for style requirements before writing a single prompt.

---

## 1. Model Selection Decision Matrix

Use this to choose the right model before writing any prompt.

> **Note:** This matrix reflects models with API documentation currently available in `references/docs/`. The model stack is not locked — new models will be added as documentation is gathered. If a model you want to use is not listed here, use the `kie-api-fetch` skill to pull its documentation from kie.ai before prompting.

| Scenario | Best Model | Why |
|---|---|---|
| Cinematic wide-shot wildlife footage (16:9) | **Veo 3.1 Quality** (`veo3`) | Highest fidelity, built-in audio, true 16:9 |
| Fast iteration / draft generation | **Veo 3.1 Fast** (`veo3_fast`) | Same quality profile, faster, cheaper |
| Animating a reference image (any subject) | **Kling 2.6 I2V** or **Wan 2.6 I2V** | Both handle realistic motion well from a starting image |
| Multi-shot sequence with the SAME character/subject | **Kling 3.0** (multi-shot) or **Sora 2 Pro Storyboard** | Native multi-shot; Kling has element references for consistency |
| Highly stylized / artistic / abstract scene | **Sora 2 T2V** | Responds well to narrative/cinematic descriptions |
| Portrait / vertical short-form (9:16) | **Veo 3.1** (native 9:16) or **Kling 3.0** (9:16 pro mode) | Both support native vertical output |
| Starting image for I2V workflow | **Nano Banana 2** | Generates realistic, candid-looking first frames; multiple aspect ratios, 1K–4K |
| Thumbnail or still image generation | **Nano Banana 2** | Up to 14 reference images, high resolution options |
| Transition between two known images | **Veo 3.1** (`FIRST_AND_LAST_FRAMES_2_VIDEO`) | First + last frame → generates transition video |
| Subject consistency across many clips | **Kling 3.0** with `kling_elements` | Provide 2–4 reference photos; reference via `@element_name` |

---

## 2. Universal Prompt Principles

These apply to ALL models, ALL channels, regardless of content type.

### The Payoff Principle (Action / Viral / Comedy Content)
Every clip intended to be funny, surprising, or shareable must follow:

```
SETUP → ACTION → PAYOFF
```

- **Setup:** The grounding moment — what is the situation? (1–2 seconds)
- **Action:** What does the subject start doing? (the build)
- **Payoff:** What actually happens? (the reason the clip exists)

The payoff must be written explicitly into the Kling/video prompt. It will not happen automatically. A prompt that only describes a situation without scripting what happens produces a clip with no punchline.

```
❌ "Cat holds paw mid-air, looks curious, natural lighting"
✅ "Cat slowly slides paw toward the plate one inch at a time, hooks a piece of toast, then suddenly bolts off the counter with it in its mouth"
```

> Note: The Payoff Principle applies to action and comedy content. Atmospheric, cinematic, or narrative content uses story arc structures instead — see the relevant channel bible or the story arc library when available.

### Subject Consistency (Critical for Character/Series Content)
Every scene prompt featuring the same animal or character must use the **exact same physical description**. Do not shorten or vary it between scenes.

```
❌ Scene 1: "A crow in a city park..."
❌ Scene 2: "The crow perches on a fence..."

✅ Scene 1: "A large, jet-black crow with a glossy blue-sheened wing and a thick curved beak, standing in a grey urban park..."
✅ Scene 2: "A large, jet-black crow with a glossy blue-sheened wing and a thick curved beak, perching on a weathered wooden fence..."
```

### Camera Directions
These terms are understood by all models. Use them explicitly:

| Intent | Language to Use |
|---|---|
| Open wide establishing shot | `extreme wide shot`, `aerial establishing shot`, `sweeping landscape view` |
| Focus on subject | `medium close-up`, `tight close-up on [subject]`, `cinematic close-up` |
| Eyes / detail | `extreme close-up on the eye`, `macro lens shot`, `shallow depth of field` |
| Following motion | `tracking shot`, `pan following [subject]`, `slow-motion tracking` |
| Dramatic reveal | `camera slowly pulls back to reveal`, `low-angle ground-level shot` |
| Atmospheric | `drone shot over`, `bird's eye view`, `handheld-style natural movement` |

### Lighting & Atmosphere
```
Golden hour: "warm golden sunlight filtering through forest canopy"
Dramatic: "overcast dramatic sky with diffused grey light"
Cinematic night: "moonlit, deep shadows, single ambient light source"
Underwater: "shafts of light penetrating deep blue-green water"
Documentary: "natural ambient daylight, no artificial lighting"
```

### What NOT to Include in Generation Prompts
- Do not include channel names, watermarks, or text — add in post-production
- Do not describe copyrighted footage or real named people
- Do not use platform-restricted language — see Section 3 below

---

## 3. Platform Language & Compliance Rules

All channels operate on TikTok, YouTube Shorts, Instagram Reels, and Facebook Reels. All content is PG. These rules apply to **scripts, narration, captions, titles, descriptions, and on-screen text** — not just video generation prompts.

### Word Replacement Table

| Banned / Restricted Word | Platform | Replacement |
|---|---|---|
| kill / killed | TikTok | unalived |
| death / died / dead | TikTok | unalived / passed / no longer with us |
| murder / murdered | TikTok | unalived |
| suicide | All | s-word / unalive / self-unalive |
| bomb | TikTok | explosive device / device |
| missile | TikTok | projectile / explosive projectile |
| gun / shoot / shot | TikTok | zapper / banger / fired |
| attack | TikTok | ambush / confrontation / incident |
| blood / bleeding | All | use visual description without the word |
| gore / graphic | All | avoid entirely |
| sex / sexual / mating | All | reproduce / courtship behavior / pairing |
| drug / drugs | TikTok | avoid or use "substance" |
| terrorist / terrorism | All | avoid entirely |

### General PG Rules
- No graphic predation language — use "ambushes," "hunts," "pursues" not "tears apart" or "devours"
- No descriptions of animals in visible pain or distress
- No content that depicts animal cruelty, even by implication
- Deaths described clinically only when scientifically necessary — always use replacements in narration/captions
- Humor must never punch down at the animal — the comedy is in the situation, not at the animal's expense

### TikTok-Specific Notes
- TikTok's content moderation scans captions, hashtags, voiceovers, and on-screen text — not just video content
- Even if a word is fine on YouTube, if it's restricted on TikTok, use the replacement everywhere for consistency
- When in doubt, use the softer word — TikTok suppresses without warning

---

## 3. Veo 3.1 (`veo3` / `veo3_fast`)

**API Endpoint:** `POST /api/v1/veo/generate`
**Models:** `veo3` (Quality) | `veo3_fast` (Speed + required for REFERENCE_2_VIDEO)

### Key Facts
- Audio is generated automatically with every video — describe sonic environment in prompt
- `REFERENCE_2_VIDEO` mode **only works with `veo3_fast`** — not `veo3`
- Explicitly set `aspect_ratio` — do not rely on `Auto`
- `seeds` (10000–99999): Use the same seed to regenerate consistent variations

### Generation Modes

**TEXT_2_VIDEO** — Most flexible. Use for establishing shots, b-roll, atmospheric scenes.
```
Prompt structure:
[ASPECT RATIO].[SUBJECT + PHYSICAL DESCRIPTION], [ACTION/MOTION], [ENVIRONMENT/SETTING], [LIGHTING], [CAMERA DIRECTION], [MOOD/ATMOSPHERE], [AUDIO CUE if relevant]
```
Example (Anomalous Wild):
```
9:16. A large-bodied mantis shrimp, iridescent rainbow-colored shell with vivid orange and teal stripes, striking rapidly at a crab shell in shallow tropical reef water. Crystal-clear blue-green water, dappled caustic light from the surface above. Extreme close-up on the striking appendage, slow-motion. The sound of the underwater impact resonates like a crack of thunder beneath the waves.
```

**FIRST_AND_LAST_FRAMES_2_VIDEO** — Transition between two images.
Describe the *motion and transformation* between the two states, not the end states themselves.
```
Prompt: "The animal slowly turns its head toward camera, its iridescent feathers catching the light as it shifts its weight — a smooth cinematic transition between two moments."
```

**REFERENCE_2_VIDEO** (veo3_fast only) — Subject stays consistent from provided reference images.
Prompt should describe *what you want the subject to DO*, not what it looks like (the reference images handle that).
```
imageUrls: [1–3 reference images of the subject]
prompt: "Moving slowly through dense jungle undergrowth, branches parting, humid misty atmosphere, dramatic green-tinted ambient light filtering through the canopy."
```

### Veo 3.1 Prompt Tips
- Include audio description for richer results: `"the distant rumble of thunder"`, `"silence except for the creak of the branch"`
- Veo handles cinematic language well — use film terminology freely
- Longer, more detailed prompts generally outperform short prompts
- For wildlife: describe *behavior* specifically, not just appearance

---

## 4. Kling 2.6 — Image to Video

**API Endpoint:** `POST /api/v1/jobs/createTask`
**Model:** `kling-2.6/image-to-video`
**Duration:** `5` or `10` seconds
**Input:** 1 image URL (required) + text prompt

### Key Syntax: Bracket Notation
Kling 2.6 uses `[Subject Description, Action]` bracket syntax to track subjects across the generated video. This is **not documented in the API spec** but is visible in the official examples and significantly improves subject consistency.

```
[Physical description of subject] describes who/what the subject is.
[Physical description of subject, specific action] describes what they do.
```

Example from official docs:
```
In a bright rehearsal room, sunlight streams through the windows.
[Campus band female lead singer] stands in front of the microphone with her eyes closed.
[Campus band female lead singer, singing loudly] Lead vocal: "I will do my best..."
The camera slowly pans around the band members.
```

For wildlife use:
```
In a misty cloud forest at dawn, filtered green light falls on the forest floor.
[Large male jaguar, dark spotted coat, powerful haunches, amber eyes] crouches motionless behind a fallen log.
[Large male jaguar, dark spotted coat, slowly raising its head to scan the surroundings]
Low-angle shot, extreme close-up on the eyes. Complete silence.
```

### Kling 2.6 Prompt Tips
- The prompt animates FROM the provided reference image — describe the motion/action you want to see emerge
- Include camera movement explicitly: `"camera slowly pushes in"`, `"slow pan left"`
- `sound: false` — Kling 2.6 does not generate great audio; disable it and add audio in post

---

## 5. Kling 3.0

**API Endpoint:** `POST /api/v1/jobs/createTask`
**Model:** `kling-3.0/video`
**Duration:** 3–15 seconds
**Modes:** `std` (720p) | `pro` (1080p) — use `pro` for final output
**Aspect Ratios:** `16:9` | `9:16` | `1:1`

### Single-Shot Mode (`multi_shots: false`)
Same bracket notation as Kling 2.6. Use `image_urls` for first frame (and optionally last frame) to bracket the motion.

### Multi-Shot Mode (`multi_shots: true`)
Up to 5 shots, each with its own `prompt` and `duration`. The first frame image applies to the first shot only.

```json
"multi_prompt": [
  { "prompt": "Shot 1 description @element_animal", "duration": 4 },
  { "prompt": "Shot 2 description @element_animal", "duration": 4 },
  { "prompt": "Shot 3 description @element_animal", "duration": 4 }
]
```

### Element References (`@element_name` Syntax)
Upload 2–4 reference images of your subject to the kie.ai File Upload API. Then reference them in prompts.

```json
"kling_elements": [
  {
    "name": "element_jaguar",
    "description": "large male jaguar with dark rosette pattern",
    "element_input_urls": ["url1.jpg", "url2.jpg", "url3.jpg"]
  }
]
```

In the prompt: `"The jaguar@element_jaguar prowls through shallow river water, muscles rippling, extreme wide shot"`

### Kling 3.0 Prompt Tips
- `element_name` in `kling_elements` must exactly match the `@element_name` in the prompt (without the `@`)
- Pro mode for finals; std mode for fast iteration
- Multi-shot is best for structured storyboards where you need consistent subject across shots
- Sound effects (`sound: true`) work best for action sequences — leave off for narrated wildlife footage

---

## 6. Wan 2.6 — Text to Video & Image to Video

**API Endpoint:** `POST /api/v1/jobs/createTask`
**Models:** `wan/2-6-text-to-video` | `wan/2-6-image-to-video`
**Duration:** `5`, `10`, or `15` seconds
**Resolution:** `720p` | `1080p` (default: 1080p)
**Max prompt length:** 5,000 characters

### Wan's Strengths
- Responds exceptionally well to **sensory and tactile descriptions** — describe texture, weight, temperature, sound
- Handles abstract/surreal concepts better than most models
- Supports very long, detailed prompts — use the full character budget for best results
- Strong at motion physics (water, fabric, fur, particle effects)

### Prompt Structure for Wan
Unlike Veo (which prefers cinematic language), Wan responds to **richly descriptive prose**:

```
[Visual framing + scale] + [Subject with full sensory description] + [Motion with physics detail] + [Environment textures] + [Lighting quality] + [Cinematic style note]
```

Example (wildlife):
```
In a hyperrealistic close-up documentary shot, a star-nosed mole — a small, velvety dark-brown creature with a ring of 22 fleshy pink star-shaped appendages surrounding its nose, tiny clawed hands, and fine dense fur — pushes through moist dark soil. Each tentacle-like nasal appendage moves independently in a rapid quivering motion as it senses the ground. The texture of the wet earth crumbles around its movement. Shallow depth of field, cool ambient underground light filtering through cracks in the soil above. National Geographic documentary aesthetic.
```

### Image-to-Video Specific
- The prompt describes what you want the image to *do* — the motion, behavior, or transformation
- Only 1 image supported (unlike Veo which supports 2)
- Image must be at least 256×256px

### Wan 2.6 Prompt Tips
- Words that trigger strong results: `hyperrealistic`, `cinematic`, `documentary`, `tactile`, `slow-motion`, `macro lens`
- Wan handles water, fog, fur, and particle effects (pollen, dust, spores) exceptionally well — use these in wildlife content
- Do not use Wan for text-in-video — it handles embedded text poorly
- Wan is ideal for abstract/scientific visualization sequences (e.g., showing an animal's sensory field, internal biology, particle-level phenomena)

---

## 7. Sora 2 — Text to Video & Image to Video

**API Endpoint:** `POST /api/v1/jobs/createTask`
**Models:** `sora-2-text-to-video` | `sora-2-image-to-video`
**`n_frames`:** `10` (10 seconds) or `15` (15 seconds) — **this is seconds, not frame count**
**Aspect Ratio:** `portrait` (9:16) | `landscape` (16:9) — note: NOT pixel values
**Max prompt length:** 10,000 characters

### Sora 2 Prompt Strengths
- Exceptional at **narrative, scene-building prompts** — describe what's happening like a film director's notes
- Strong on environmental storytelling and atmosphere
- Handles unusual/surreal stylization well (claymation, animation styles, etc.)
- `character_id_list` allows pre-built character animations (max 5) — must create characters via Sora-2-characters endpoint first

### Prompt Structure for Sora 2
Sora 2 responds best to **scene description + action + emotional/atmospheric context**:

```
[Scene setup] + [Subject description + behavior] + [Camera work] + [Atmosphere + mood] + [Optional: dialogue or sound]
```

Example (Anomalous Wild):
```
A documentary-style deep ocean scene, 900 meters below the surface. Complete darkness except for a single source of bioluminescent light — an anglerfish, grotesque and ancient-looking, its lure swaying gently in the abyssal current. The lure pulses with cold blue-white light. Camera slowly pushes in, handheld-style slight drift, as small curious fish approach the glow. The moment is hypnotic and slightly terrifying. Silence except for deep water pressure sounds.
```

### Important Notes
- Always set `remove_watermark: true` to clean output
- `character_id_list` is optional — leave empty if not using pre-built characters
- `portrait`/`landscape` are the only options — no numeric ratio

---

## 8. Sora 2 — Pro Storyboard

**API Endpoint:** `POST /api/v1/jobs/createTask`
**Model:** `sora-2-pro-storyboard`
**Structure:** Array of `shots[]`, each with `Scene` (description) and `duration` (seconds)
**Total video:** `n_frames` = `10`, `15`, or `25` seconds (sum of shot durations cannot exceed this)
**Aspect Ratio:** `portrait` | `landscape`

> **CRITICAL:** The prompt field is called `Scene` (capital S), NOT `prompt`. This is unique to this model.

### When to Use Pro Storyboard
Use this when you need **narrative continuity** across multiple cuts within a single generation — it produces more coherent scene-to-scene transitions than calling the T2V endpoint multiple times.

### Shot Writing for Pro Storyboard
Each `Scene` should:
1. Briefly re-establish the subject (for continuity)
2. Describe the specific action/motion for this shot
3. Include camera direction
4. Note any key atmospheric change from the previous shot

```json
"shots": [
  {
    "Scene": "Extreme wide establishing shot of the Serengeti at golden hour. The vast golden grass plain stretches to the horizon. A lone cheetah, lean and spotted with distinctive black tear-stripe markings under its eyes, stands motionless on a rocky outcrop surveying the landscape. Silence.",
    "duration": 5
  },
  {
    "Scene": "The same cheetah with black tear-stripe markings and golden spotted coat locks onto something in the distance. Medium close-up on its face. Its eyes narrow. Ears flatten slightly. The camera holds still as tension builds.",
    "duration": 5
  },
  {
    "Scene": "The cheetah explodes into a sprint from the same rocky outcrop, low-angle tracking shot from the side. Its body stretches full extension and recoils with each stride. Slow-motion. Dust kicks up from the dry earth.",
    "duration": 5
  }
]
```

### Pro Storyboard Tips
- Repeat subject physical description in each shot for consistency
- Keep shot durations between 3–8 seconds for best pacing
- The optional `image_urls` (1 image) sets the visual style/tone reference for the whole sequence
- Total duration of all shots must equal `n_frames` exactly

---

## 9. Google Nano Banana 2 (Image Generation)

**API Endpoint:** `POST /api/v1/jobs/createTask`
**Model:** `nano-banana-2`
**Use case:** Starting frames for I2V workflows, thumbnail art, concept images, illustrated frames
**Reference images:** Up to 14 input images
**Aspect ratios:** 1:1, 2:3, 3:2, 9:16, 16:9, 4:5, and more
**Resolution:** `1K`, `2K`, `4K`

### When to Use Nano Banana 2
- **Generating the starting image for any image-to-video pipeline** — the primary use case. Generate a realistic, candid-looking first frame, then immediately feed the URL into Kling, Wan, or any I2V model.
- Generating thumbnail hero images for YouTube long-form
- Creating stylized illustrations or concept art that matches a channel's visual identity
- Producing concept art before committing to video generation
- Using reference images to generate consistent-style frames

> **URL Expiry Warning:** Nano Banana 2 generated image URLs expire within approximately 2 minutes. If using the output as an I2V starting frame, submit it to the video model immediately — in the same pipeline step. Do not generate images in batch and submit later.

### Prompt Structure for Nano Banana 2
Nano Banana 2 handles multi-panel and complex scene descriptions well. Be explicit about style:

```
[Art style/medium] + [Subject with detailed physical description] + [Pose/action] + [Environment] + [Lighting] + [Color palette/mood] + [Output format guidance]
```

Example (Anomalous Wild thumbnail):
```
Photorealistic wildlife photography style. A mantis shrimp in extreme close-up, impossibly vivid iridescent colors — deep teal, electric orange, and cobalt blue — its compound eyes looking directly at camera with alien intensity. Set against a dark underwater background with a single shaft of light from above illuminating the subject. The image feels like a scientific discovery moment. High contrast. Channel color palette: deep teal, amber, electric cyan. Cinematic and slightly ominous.
```

### Reference Image Usage
When providing `image_input` URLs, describe what relationship the references should have to the output:
- "Use the provided reference images to match the visual style and color grade"
- "The animal in the reference images should appear in this new scene"
- "Match the artistic style of the reference images"

### Nano Banana 2 Tips
- Use `4K` resolution for thumbnails intended for YouTube
- `16:9` aspect ratio for YouTube thumbnail dimensions
- For Anomalous Wild: include color palette in prompt — `"deep teal, amber, electric cyan"` — to maintain brand consistency
- The model supports very long prompts (20,000 chars) — use this for detailed scene composition

---

## 10. Scientific Diagram Pipeline

> **Rule:** AI image models draw the picture. Figma/SVG draws the words.
> Never use an image model to generate text labels, callout lines, annotations, or arrows — they hallucinate characters. All labeling happens in post.

### The Four-Step Pipeline

```
1. REFERENCE   Find a real scientific reference image (photo, illustration, journal figure)
               → Save to: references/[video_id]/[subject]_reference.jpg
               → Required for: any anatomical diagram, organism close-up, biological process

2. ILLUSTRATION  Generate a clean, unlabeled illustration with Nano Banana 2
               → Use the reference image as input
               → Mandatory negative prompt (append to all diagram prompts):
                 "no text, no labels, no callout lines, no arrows, no annotation marks,
                  no letters, no numbers, no words, no captions"
               → Target: photorealistic or clean scientific illustration style
               → Output: save to outputs/[video_id]/[scene_id]/image.png

3. LABELS      Add all labels, callout lines, annotations, and titles in Figma or as SVG
               → Import the PNG from step 2 as the base layer
               → Add text and lines as vector objects on top
               → Font: match the channel's typography system (see channel bible)
               → Export at 1920×1080 (or 1080×1920 for vertical)

4. EXPORT      Export the labeled composition to Remotion
               → As static PNG for still diagrams
               → As image sequence or Lottie for animated diagrams
```

### Nano Banana 2 Prompt Template (Scientific Illustration)

```
[Art style] + [Subject with exact anatomical description] + [Pose/orientation for labeling] +
[Clean background — white/dark/neutral] + [Negative prompt block]

Negative prompt block (always append):
"no text, no labels, no callout lines, no arrows, no annotation marks,
 no letters, no numbers, no words, no captions"
```

Example (bioluminescence weapon):
```
Clean scientific illustration style, photorealistic. A honeybee, dorsal view, wings fully
extended and slightly spread, on a pure white background with soft diffused lighting.
Show full anatomical detail — compound eyes, three body segments (head, thorax, abdomen),
six legs with visible pollen baskets, venation pattern on both wing pairs.
Centered in frame with margins on all sides for labeling. No text, no labels, no callout
lines, no arrows, no annotation marks, no letters, no numbers, no words, no captions.
```

### When `requires_reference: true` Is Mandatory

Any `new_clips_prompts.json` entry with `"is_diagram": true` **must** also have:
```json
{
  "is_diagram": true,
  "requires_reference": true,
  "reference_image": "references/[video_id]/[subject]_reference.jpg"
}
```

The `run_new_clips_batch.py` tool will block generation and print a warning if the
reference file does not exist. Use `--force-no-ref` only in development/test runs.

### Common Mistakes to Avoid

| Mistake | What Happens | Fix |
|---------|-------------|-----|
| No negative prompt on diagram | Model adds fake text, numbers, or arrow-like marks | Always append the mandatory negative prompt block |
| Generating labels in the image model | Text is garbled or wrong characters | Move all labels to Figma/SVG — always |
| Wrong orientation for labeling | Labels don't fit around the subject | Specify `dorsal view`, `lateral view`, `frontal view` explicitly |
| No reference image | Subject anatomy is hallucinated | Find a real reference first — saves multiple regeneration cycles |
| Prompt describes a "labeled diagram" | Model tries to add labels | Never use the word "diagram" or "labeled" — describe a clean illustration |

---

## 12. Channel-Specific Prompt Templates

Channel-specific prompt templates live in each channel's bible, not in this document. Refer to the relevant channel bible for templates tailored to that channel's visual style, humor type, and aesthetic.

- **Anomalous Wild:** `references/docs/ANOMALOUS WILD — CHANNEL BIBLE.md`
- **Neon Parcel:** `references/docs/NEON PARCEL — CHANNEL BIBLE.md`

---

## 13. What Is NOT Documented (Known Unknowns)

These gaps exist in the current API documentation. Use with caution:

| Gap | Notes |
|---|---|
| Kling bracket syntax `[Description, Action]` | Works based on official examples but not formally documented — test per use case |
| Veo 3.1 audio quality control | Cannot directly specify audio mix or suppress specific sounds beyond describing the scene |
| Sora 2 character consistency without `character_id_list` | Relies entirely on repeating the physical description in each prompt |
| Wan 2.6 aspect ratio | No explicit aspect ratio parameter — the model infers from the input image shape (I2V) or generates at a default ratio (T2V). Test outputs. |
| Kling 2.6 resolution | Always outputs at its internal default — no resolution parameter available for this model version |
| Nano Banana 2 image editing vs. generation | When `image_input` is provided, behavior varies between style-matching, inpainting, and reference-guided generation — test per use case |

---

*Last updated: March 21, 2026. Update this file when new models are added, new platform language rules are confirmed, or universal prompting patterns are validated through testing. Channel-specific rules belong in the channel bible, not here.*
