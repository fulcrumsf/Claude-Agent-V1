# Model Selector Guide

## Quick Reference: Which Model for Which Style?

| Style | Output Type | Model | Platform | Cost per Asset | Quality Tier |
|-------|------------|-------|----------|-----------------|--------------|
| **Style 01: Archival B&W** | Static image | Nano Banana 2 | kie.ai | $0.04–0.09 | High |
| **Style 02: 3D Synthetic** | Static image | Nano Banana 2 | kie.ai | $0.04–0.09 | High |
| **Style 03: Satellite/Map** | Static image | Nano Banana 2 | kie.ai | $0.04–0.09 | High |
| **Style 04: HD Underwater** | Video (5–30 sec) | Kling 2.1 Pro | kie.ai | $0.125–0.25 per 5-sec clip | High |
| **Style 04: HD Underwater (Hero)** | Video (short) | Veo 3 Quality | kie.ai | $2.00 per 8-sec clip | Excellent |
| **Style 05: Wildlife** | Static image | Nano Banana 2 | kie.ai | $0.04–0.09 | High |
| **Style 05: Wildlife (Video)** | Video (cinematic) | Veo 3 Quality | kie.ai | $2.00 per 8-sec clip | Excellent |
| **Style 06: Infographic** | Static image | Nano Banana 2 | kie.ai | $0.04–0.09 | High |

---

## Decision Framework

### Step 1: What Type of Output Do I Need?

- **Static image?** → Go to [Image Generation Models](#image-generation-models)
- **Video clip?** → Go to [Video Generation Models](#video-generation-models)

### Step 2: What is My Quality Requirement?

- **Rough cut / iteration** → Budget tier
- **Broadcast standard** → Mid tier
- **Hero shot / final sequence** → Premium tier

### Step 3: What is My Budget?

- **Minimal** → Use cheapest option
- **Moderate** → Use standard tier
- **Generous** → Use premium tier

### Step 4: Select Platform

**Default: Always use kie.ai first.** It's 30–70% cheaper than fal.ai on virtually all models.

Only use fal.ai if:
- Model not available on kie.ai
- Specific technical reason (document in ticket)

---

## Image Generation Models

### Nano Banana 2 (Google Gemini 3.1 Flash 4K)

**When to use:** Primary choice for styles 01–03 and 06. Also for style 05 (wildlife).

**Pricing on kie.ai:**
- 1K resolution: **$0.04/image**
- 2K resolution: **$0.06/image**
- 4K resolution: **$0.09/image**

**Pricing on fal.ai:**
- 512×512: $0.06/image
- 1K: $0.08/image
- 2K: $0.12/image
- 4K: $0.16/image

**Recommendation:** Use kie.ai (30–40% cheaper).

**Speed:** Fast
**Quality:** High
**Best for:** High-volume production, standard sequences, most use cases

**Post-processing:**
- Style 01 (B&W): Add grayscale + grain in Remotion
- Style 02 (3D): Use as-is or cleanup in Figma
- Style 03 (Maps): Add Remotion overlays (depth markers, labels)
- Style 05 (Wildlife): Use as-is or add bokeh blur in Remotion
- Style 06 (Infographic): Add text labels in Remotion ONLY

---

### Nano Banana Pro (Google Gemini 3.0 Pro)

**When to use:** When highest image quality is required (hero shots, title cards, premium sequences).

**Pricing on kie.ai:**
- 1K–2K: **$0.09–0.12/image**

**Pricing on fal.ai:**
- Commercial: **$0.15/image**

**Recommendation:** Use kie.ai (20–40% cheaper).

**Speed:** Standard (slower than Nano Banana 2)
**Quality:** Very High
**Best for:** Final hero shots, key visual moments, high-visibility content

---

## Video Generation Models

### Kling 2.1 Standard (720p)

**When to use:** Rough cuts, iterations, speed-focused production, budget constraints.

**Pricing on kie.ai:** **$0.125 per 5-second clip** = $0.025/second

**Speed:** Standard
**Quality:** Good
**Resolution:** 720p
**Best for:** Early edits, brainstorming, proof-of-concept

**Maximum duration:** 30 seconds per clip (generate as multiple 5-second segments)

---

### Kling 2.1 Pro (1080p)

**When to use:** Final renders for broadcast, published content, standard video sequences.

**Pricing on kie.ai:** **$0.25 per 5-second clip** = $0.05/second

**Speed:** Standard
**Quality:** High
**Resolution:** 1080p
**Best for:** Final video production, YouTube publishing, broadcast-quality sequences

**Maximum duration:** 30 seconds per clip (generate as multiple 5-second segments)

---

### Veo 3 Fast (1080p)

**When to use:** When Veo 3 quality is desired but cost must be moderate. Better visual coherence than Kling.

**Pricing on kie.ai:** **$0.40 per 8-second video** = $0.05/second

**Speed:** Standard
**Quality:** Good–High
**Resolution:** Up to 1080p
**Best for:** Standard sequences, balanced cost/quality, most underwater footage

**Fal.ai comparison:** Fal.ai charges $0.40/second ($3.20 for 8 seconds), making kie.ai equivalent in cost but better workflow.

---

### Veo 3 Quality (1080p)

**When to use:** Hero shots, key narrative moments, cinematic reveals, final video sequences.

**Pricing on kie.ai:** **$2.00 per 8-second video** = $0.25/second

**Speed:** Standard
**Quality:** Excellent
**Resolution:** Up to 1080p
**Best for:** Title sequences, creature reveals, emotional peaks, premium content

**Comparison:**
- Kling 2.1 Pro: $0.05/second (5× cheaper, good quality)
- Veo 3 Quality: $0.25/second (5× more expensive, excellent quality)

**Use this when:**
- Narrative moment is critically important
- Viewer attention should peak
- Final render, not iteration
- Budget allows

---

### Seedance 1.5 Pro

**Status:** Available on kie.ai
**Status:** Veo 3 Quality often preferred

**Pricing on kie.ai:** **$0.052 per second** (~$0.26 for 5-second video with audio)

**Features:**
- Native audio synchronization
- Multi-shot sequence support
- Character consistency

**When to use:** If multi-shot narrative generation is required and Veo 3 is too expensive.

---

### Seedance 2.0

⚠️ **SUSPENDED as of March 15, 2026** — Hollywood copyright suspension

**Fallback options:**
1. Use Veo 3 Quality (best visual quality)
2. Use Seedance 1.5 Pro (if audio sync critical)
3. Use Kling 2.1 Pro (if budget constrained)

---

## Platform Comparison: Kie.ai vs Fal.ai

### Image Generation

| Model | Kie.ai | Fal.ai | Winner |
|-------|--------|--------|--------|
| Nano Banana 2 (1K) | $0.04 | $0.08 | **kie.ai (50% cheaper)** |
| Nano Banana Pro | $0.09 | $0.15 | **kie.ai (40% cheaper)** |
| Seedream V4 | N/A | $0.03 | fal.ai (if budget critical) |

**Recommendation:** Use kie.ai for all Nano Banana models. Use fal.ai only for budget-tier alternatives.

### Video Generation

| Model | Kie.ai | Fal.ai | Winner |
|--------|--------|--------|--------|
| Veo 3 | $0.05–0.25/sec | $0.40/sec | **kie.ai (4–8× cheaper)** |
| Kling 2.1 | $0.025–0.05/sec | $0.07/sec (Turbo only) | **kie.ai (cheaper, more options)** |
| Seedance 1.5 | $0.052/sec | N/A | kie.ai |
| Seedance 2.0 | Suspended | Coming soon | TBD |
| Wan 2.5 | N/A | $0.05/sec | fal.ai (only option) |

**Recommendation:** Use kie.ai as default platform for all video work. Use fal.ai only for Wan 2.5 if ultra-budget is required.

---

## Cost Scenarios

### Scenario 1: 30-Second Underwater Descent (Style 04)

**Parameters:**
- Style: HD Underwater Camera
- Duration: 30 seconds
- Quality: Broadcast standard
- Budget: Moderate

**Solution:**
1. Break into 6 × 5-second clips
2. Generate each with Kling 2.1 Pro on kie.ai
3. **Total cost:** 6 × $0.125 = **$0.75**
4. Add SFX layer (Suno), color grade in Remotion

**Alternative (budget-conscious):**
1. Use Kling 2.1 Standard instead
2. **Total cost:** 6 × $0.063 = **$0.38**
3. Quality acceptable for rough cuts and B-roll

---

### Scenario 2: Title Sequence with Creature Close-up (Style 05)

**Parameters:**
- Style: Wildlife cinematography
- Output: Static image (title card) + short video (creature reveal)
- Quality: Hero shot
- Budget: Premium

**Solution:**
1. **Title image:** Nano Banana Pro (4K) on kie.ai = **$0.12**
2. **Creature video:** Veo 3 Quality (8 sec) on kie.ai = **$2.00**
3. **Total cost:** **$2.12**
4. Post-process: Add color grading, bokeh to image; sync audio to creature video

---

### Scenario 3: Full Educational Sequence (All Styles)

**Parameters:**
- Content: 5-minute video using all 6 styles
- Quality: Broadcast standard
- Budget: Moderate

**Asset breakdown:**
- Style 01 (B&W intro): 3 images @ $0.04 = **$0.12**
- Style 02 (3D expl.): 5 images @ $0.06 = **$0.30**
- Style 03 (Maps): 4 images @ $0.04 = **$0.16**
- Style 04 (Video): 60 sec ÷ 5 sec clips = 12 clips @ $0.125 = **$1.50**
- Style 05 (Wildlife): 6 images @ $0.06 = **$0.36**
- Style 06 (Infographics): 8 images @ $0.04 = **$0.32**

**Total asset cost: $2.76**

*(Plus ElevenLabs TTS for narration, Suno for music/SFX, Remotion composition labor)*

---

## Rules for Video Agents

### Rule 1: Use Kie.ai by Default

Every model selector should default to kie.ai unless:
1. Model is unavailable on kie.ai
2. Specific technical requirement exists (document it)
3. Cost analysis shows fal.ai is cheaper for this specific case

### Rule 2: Image-First Workflow

**Always:**
1. Generate base image
2. Extend to video if needed
3. Never video-first

**Why:** Images are 10–100× cheaper and faster for iteration.

### Rule 3: Text in Remotion, Never in Model

**NEVER ask the model to generate text.** Models hallucinate text and make errors.

**ALWAYS:**
1. Generate clean graphic design (no text)
2. Add text labels, callouts, overlays in Remotion
3. Animate text timing against beat_sheet.json

### Rule 4: Schedule Against Narration Timestamps

**Narrator is the master clock.**

**Workflow:**
1. Extract narration from ElevenLabs TTS
2. Get word-level timestamps from ElevenLabs API
3. Build beat_sheet.json from timestamps
4. Schedule all visual cuts, creature reveals, infographic appearances against beat_sheet

**Never estimate timecodes manually.**

### Rule 5: Avoid Seedance 2.0

Seedance 2.0 is suspended (March 15, 2026).

**Fallback priority:**
1. Veo 3 Quality (best quality, short clips)
2. Seedance 1.5 Pro (if audio sync critical)
3. Kling 2.1 Pro (if budget constrained)

---

## Quality Tier Decision Tree

```
Need a new asset?
│
├─ What's the purpose?
│  ├─ Internal review / brainstorming?
│  │  └─ Use BUDGET tier
│  │     • Nano Banana 2 (1K) @ $0.04
│  │     • Kling 2.1 Standard @ $0.125/5sec
│  │     • Result: Fast iteration, lowest cost
│  │
│  ├─ YouTube / public release?
│  │  └─ Use BROADCAST tier
│  │     • Nano Banana 2 (2K) @ $0.06
│  │     • Kling 2.1 Pro @ $0.25/5sec
│  │     • Result: Meets monetization standards
│  │
│  └─ Premium / hero moment / paid distribution?
│     └─ Use PREMIUM tier
│        • Nano Banana Pro (4K) @ $0.12
│        • Veo 3 Quality @ $2.00/8sec
│        • Result: Best quality, command attention
```

---

## FAQ

**Q: Should I always use the most expensive model?**
A: No. Match quality tier to narrative importance. Reserve hero budgets for key moments (title cards, creature reveals, emotional peaks).

**Q: Can I use fal.ai to save money?**
A: fal.ai is 30–70% more expensive than kie.ai on most models. Only use fal.ai if kie.ai doesn't have the model you need.

**Q: Why not use Seedance 2.0?**
A: Suspended March 15, 2026 due to Hollywood copyright concerns. Use Veo 3 Quality or Kling 2.1 Pro instead.

**Q: How do I minimize production costs?**
A: 1) Use Nano Banana 2 (1K) on kie.ai for all images; 2) Use Kling 2.1 Standard for rough cuts; 3) Reserve Veo 3 Quality for hero sequences only.

**Q: What if I need text in my infographic?**
A: Generate the clean graphic in Nano Banana 2, then add all text labels in Remotion. Never ask the model to generate text.

**Q: How long does each model take?**
A: All listed models complete in 30–90 seconds. Speed is similar across kie.ai and fal.ai; cost difference is the driver.

---

## Related Documents

- **MODEL_CATALOG.json** — Full pricing table and model details (JSON format for agent consumption)
- **MODEL_SELECTOR.json** — Decision rules and decision tree (JSON format for agent automation)
- **CINEMATIC_STYLE_GUIDE.md** — Visual style definitions and prompt templates
- **CLAUDE.md** — Production workflow and quality standards
