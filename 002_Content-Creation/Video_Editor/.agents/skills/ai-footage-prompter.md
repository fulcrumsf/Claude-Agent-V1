---
description: Takes a beat sheet row and generates production-ready AI video prompts (Kling/Veo via Kie.ai) and reference image prompts (Fal.ai FLUX via Nano Banana). Output feeds directly into the generation tools.
status: active
channel: 001_anomalous_wild
---

# Skill: AI Footage Prompter

## Purpose

Takes each beat sheet scene marked `ai_prompt_needed: true` and generates:
1. **Kling/Veo video prompt** — for `tools/kie_video_gen.py`
2. **Fal.ai reference image prompt** — for `tools/image_gen.py` (Nano Banana format)
3. **Generation metadata** — model, duration, aspect ratio settings

---

## Anomalous Wild Visual Language (always apply)

Every prompt must reflect the channel's hybrid aesthetic:

**Palette:** Deep teal `#2B0B5A` to forest black `#0B0F1A` backgrounds · Neon green `#8AFA47` accent glow on subject · Electric cyan for anomaly reveals · Warm gold for fact highlights

**Lighting:** Cinematic, low-key, dramatic. Bioluminescent subjects: self-lit against absolute black. Surface creatures: golden-hour natural light or overcast diffuse.

**Camera style:**
- Macro/extreme close-up: shallow depth of field, bokeh background, subject fills 60–80% of frame
- POV: first-person perspective, slight lens distortion (wide angle), motion parallax
- 3D render: photorealistic, 8K texture detail, subsurface scattering on organic tissue
- Wide establishing: anamorphic lens flare, slight grain, mist/depth haze

**Style anchors:** National Geographic · BBC Earth macro cinematography · Zack D. Films 3D hybrid

---

## Kling/Veo Video Prompt Format

```
[Subject] [specific action/motion], [setting], [lighting], [camera move], [style reference], [duration hint]

EXAMPLE:
Anglerfish bioluminescent lure pulsing slowly in the abyss, absolute darkness except for the cold blue-white glow of the lure, macro close-up on the lure tip, slight forward camera drift, photorealistic 8K, National Geographic underwater cinematography, 5 seconds
```

### Rules for video prompts:
- Always specify the motion — what is moving and how
- Always specify the lighting source
- Name the camera move: `slow push in` / `orbit around subject` / `static hold` / `slow pull back` / `POV drift forward`
- Add duration hint: `5 seconds` / `7 seconds` (Veo3 default clips)
- Never use `kill` `attack` `death` — use `hunts`, `captures`, `neutralizes`
- For bioluminescence: always specify "self-illuminated" or "bioluminescent glow" + the specific color

---

## Fal.ai / Nano Banana Reference Image Prompt Format

Reference images serve as the visual style anchor fed into Kling for image-to-video.

```
[Subject] [specific feature in focus], [exact setting], [lighting description], [color palette], [camera/lens type], [style keywords]

EXAMPLE:
Extreme macro close-up of an anglerfish esca (bioluminescent lure), hovering in absolute black deep-sea water, cold blue-white self-illuminated glow with soft corona, teal and black color palette, 8K photorealistic, National Geographic underwater photography, shallow depth of field, subsurface glow effect
```

### Nano Banana enhancement checklist:
Before finalizing, apply these modifiers:
- `8K photorealistic` or `photorealistic render`
- `cinematic lighting` or `volumetric lighting`
- `shallow depth of field`
- `Anomalous Wild color palette: deep teal, forest black, neon green accent`
- `National Geographic / BBC Earth style`
- `no text, no watermark`

---

## Generation Metadata Per Scene

```json
{
  "scene_id": "scene_01",
  "image_prompt": "...",
  "video_prompt": "...",
  "model": "veo3_fast",
  "duration_s": 5,
  "aspect_ratio": "16:9",
  "output_folder": "outputs/001_anomalous_wild/bioluminescence_weapon/scene_01/",
  "priority": "high"
}
```

---

## Scene Type → Prompt Strategy

| Shot Type | Image Prompt Focus | Video Prompt Motion |
|---|---|---|
| `extreme_closeup` | Subject anatomy detail, fill 80% frame | Slow push in 2–3cm, subject breathes/pulses |
| `macro` | Texture and surface detail | Orbit slowly around subject |
| `pov` | Wide angle, subject's environment ahead | First-person forward drift |
| `wide_establishing` | Full environment, subject small in frame | Slow pull back from subject to wide |
| `3d_render` | Cross-section or internal anatomy | Slow rotation or zoom into mechanism |
| `overhead` | Top-down, geometric patterns | Static hold or slow zoom in |
| `glitch_reveal` | Subject at edge of darkness | Quick zoom + chromatic aberration flash |

---

## Output

For each `ai_prompt_needed: true` scene, deliver:
1. Image prompt (Fal.ai/Nano Banana format)
2. Video prompt (Kling/Veo format)
3. JSON metadata block
4. Flag if scene requires special handling (e.g., 3D render software needed)
