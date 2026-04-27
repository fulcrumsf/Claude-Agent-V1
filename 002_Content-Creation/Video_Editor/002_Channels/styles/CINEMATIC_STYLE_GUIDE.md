# Cinematic Style Guide

## Overview

This guide defines the 6 production methodologies (cinematic styles) used in multi-channel video content production. These are **not content-based categories** (e.g., "ocean footage" or "creatures"). They are **treatment categories** — the visual technique, composition method, and aesthetic vibe used to capture or generate footage for specific narrative purposes.

Each style has:
- **Visual identity:** The look, feel, and composition approach
- **Generation method:** Which AI model to use and how to prompt it
- **Use cases:** When to apply this style in a script
- **Post-processing:** What happens after generation (color grade, overlays, effects)

---

## The 6 Cinematic Styles

### Style 01: Archival B&W Documentary

**Visual Identity:**
- Grayscale tones, high contrast, film grain
- 1960s–1990s aesthetic
- Low saturation, slightly faded appearance
- Suggests age, authenticity, historical credibility

**Real-world reference:**
- BBC nature documentaries from the 1980s
- Historical newsreel footage
- Museum archival recordings

**Generation Workflow:**
1. **Model:** Nano Banana 2 (kie.ai) with period-appropriate prompt
2. **Prompt structure:** `"[Historical subject], 1980s documentary style, black and white, grainy film texture, high contrast, authentic archival footage"`
3. **Post-process:** Optional grain filter in Remotion to enhance vintage feel
4. **Cost:** $0.04–0.09 per image (kie.ai)

**Use cases in scripts:**
- HMS Challenger discovery (1960s ship, historical context)
- Historical timeline sequences
- "How we know this is real" sequences (credibility through "vintage footage")
- Flashback narratives

**Key rule:** Generate in color → convert to grayscale in Remotion. Don't ask the model to generate grayscale (it hallucinates).

---

### Style 02: 3D Animated Synthetic

**Visual Identity:**
- Clean, geometric shapes
- Bright synthetic colors (primary blues, greens, bright accents)
- Illustration-like or 3D render quality
- High clarity, educational feel
- Often includes cross-sections, cutaways, exploded diagrams

**Real-world reference:**
- TED-Ed explainer videos
- National Geographic educational sequences
- CGI geology visualizations (plate tectonics, volcanism)
- Medical animation style

**Generation Workflow:**
1. **Model:** Nano Banana 2 (kie.ai) with "3D render" or "synthetic" style modifier
2. **Prompt structure:** `"[Subject], 3D render, cross-section, synthetic colors, clean geometry, bright blue and green palette, educational diagram style, labels optional"`
3. **Post-process:** Add Remotion overlays (arrows, labels, annotations) if needed; never embedded text
4. **Cost:** $0.04–0.09 per image (kie.ai)

**Use cases in scripts:**
- Plate tectonics visualization (subduction zones, magma flow)
- Earth's interior cross-sections
- Geological process explanation (Ring of Fire, volcanic activity)
- Physics diagrams (pressure, temperature, force visualization)
- Anatomical or biological breakdowns

**Key rule:** Generate the diagram clean and unlabeled → add text/callouts in Remotion.

---

### Style 03: Satellite/Map Visualization

**Visual Identity:**
- Overhead/bird's-eye perspective
- Flat design aesthetic (minimal perspective distortion)
- Information overlay style (labels, depth markers, distance indicators)
- Google Earth or topographic map feel
- Muted colors or natural terrain colors

**Real-world reference:**
- Google Earth / Maps zoom sequences
- NASA satellite imagery
- Topographic maps
- Military/strategic maps

**Generation Workflow:**
1. **Model:** Nano Banana 2 (kie.ai) with map-specific prompt
2. **Prompt structure:** `"[Location], satellite view, topographic map, overhead perspective, depth markers, geographic scale, information overlay, Google Earth style, flat design"`
3. **Post-process:** Remotion overlays for depth lines, distance labels, scale comparisons (e.g., "Mount Everest would fit here")
4. **Cost:** $0.04–0.09 per image (kie.ai)

**Use cases in scripts:**
- Mariana Trench geography (showing scale, curve, location relative to Japan)
- Ocean basin topography
- Planetary geographic scale comparisons
- Route maps or journey visualization
- Earthquake/volcanic zone mapping (Ring of Fire)

**Key rule:** Generated image provides the base map; Remotion adds all text, scale bars, and interactive elements.

---

### Style 04: HD Underwater Camera (Primary Workhorse)

**Visual Identity:**
- Cinematic underwater footage with submersible POV
- Depth-dependent color shift: bright blues at surface → fading to black at depth
- Water particles, light scatter, natural light physics
- Bioluminescence glow (blue accent lights in deep sections)
- Immersive, observational camera movement

**Real-world reference:**
- BBC Blue Planet II underwater sequences
- NatGeo Deep Sea documentation
- James Nestor's ocean exploration footage
- Submersible discovery footage (Alvin, etc.)

**Generation Workflow:**
1. **Model:** Kling 2.1 Pro (kie.ai) for standard sequences, Veo 3 Quality for hero moments
2. **Prompt structure:** 
   - **Standard:** `"Underwater cinema descent, water particles, natural depth color transition, submersible POV, [depth zone atmosphere], cinematic composition"`
   - **With creatures:** `"Underwater cinematic footage, [creature name], bioluminescence, depth zone appropriate, submersible lighting, natural behavior"`
   - **Hero moment:** `"[Subject], underwater cinematic masterpiece, bioluminescence glow, cinematic lighting, emotional reveal, professional documentary"`
3. **Duration:** Generate as 5-second clips (max 30 seconds per clip)
4. **Post-process:** 
   - Add SFX layer (Suno-generated ambient underwater sounds)
   - Color grade for zone transition (bright blue → dark blue → black with bioluminescence)
   - Crossfade between clips (never hard cuts)
4. **Cost:** $0.125 (Kling Standard) → $0.25 (Kling Pro) → $2.00 (Veo 3 Quality) per clip

**Use cases in scripts:**
- Main narrative "descent journey" (16–30 minutes of video)
- Creature encounters (in natural habitat)
- Zone transitions (Epipelagic → Twilight → Midnight → Hadal)
- Environmental exploration
- 90% of the video runtime in deep-sea documentaries

**Key rules:**
1. Always schedule against beat_sheet.json timestamps (narrator timing)
2. Generate multiple short clips → seamless composition in Remotion
3. Add creature narration description → visual should match narrator's description precisely
4. Color grade in Remotion for zone transitions (don't rely on model to change colors mid-sequence)

**Creature accuracy requirement:** Each creature visual must match narrator's description of size, movement, behavior, and environment. Reference images are critical.

---

### Style 05: National Geographic Wildlife

**Visual Identity:**
- Professional broadcast cinematography
- Shallow depth of field (bokeh background, sharp subject focus)
- Warm color grading (golden-hour feeling, even in controlled settings)
- Subject-centered composition
- Emotional, intimate lens on animals
- Cinematic elegance and beauty

**Real-world reference:**
- National Geographic nature photography
- Planet Earth series creature close-ups
- David Attenborough-style wildlife cinematography
- Professional wildlife portrait photography

**Generation Workflow (Static Images):**
1. **Model:** Nano Banana 2 (kie.ai) for standard, Nano Banana Pro for hero shots
2. **Prompt structure:** `"[Creature name], National Geographic wildlife cinematography, shallow depth of field, bokeh background, warm color grading, professional documentary, intimate animal portrait, studio lighting quality"`
3. **Post-process:** Optional bokeh blur enhancement in Remotion if needed
4. **Cost:** $0.04–0.09 (Nano Banana 2) or $0.09–0.12 (Nano Banana Pro) per image

**Generation Workflow (Cinematic Video):**
1. **Model:** Veo 3 Quality (kie.ai) for creature behavior/movement
2. **Prompt structure:** `"[Creature] moving/hunting/interacting, underwater/terrestrial habitat, National Geographic wildlife cinematography, cinematic moment, emotional behavior, professional documentary, warm color grading"`
3. **Duration:** 6–10 seconds max
4. **Cost:** $2.00 per 8-second video (Veo 3 Quality)

**Use cases in scripts:**
- Creature reveals and introductions
- Specimen showcase (beauty of form)
- Behavior demonstration (hunting, feeding, mating)
- Close-up focus sequences that demand viewer attention
- Emotional payoff moments (after narrator setup, creature delivers visual surprise)

**Key rule:** This is the "beauty shot" style. Every creature gets a 15–30 second wildlife moment. Narration sets expectations; video delivers emotional impact.

---

### Style 06: Scientific Infographic

**Visual Identity:**
- High contrast, clean graphic design
- Information-dense but uncluttered
- Educational, data visualization feel
- Often includes diagrams, measurements, comparisons, scale indicators
- Numerical data presented visually
- Professional scientific poster aesthetic

**Real-world reference:**
- Infographics.com style graphics
- Scientific journal figures
- Educational explainer diagrams
- Data visualization dashboards
- MIT/Stanford science communication posters

**Generation Workflow:**
1. **Model:** Nano Banana 2 (kie.ai) with infographic-specific prompt
2. **Prompt structure:** `"Scientific infographic, [data/comparison/measurement], high contrast, clean graphic design, information visualization, educational diagram, measurement scale, [specific data to show]"`
3. **Post-process:** 
   - **NEVER ask model to add text**
   - Generate clean diagram → add all text/numbers in Remotion
   - Remotion controls: label placement, font, animation timing against beat_sheet
4. **Cost:** $0.04–0.09 per image (kie.ai)

**Use cases in scripts:**
- Depth markers ("11 km down," "Challenger Deep")
- Pressure comparisons ("1000× surface pressure")
- Scale comparisons ("Mount Everest would fit here, 2 km below surface")
- Temperature/salinity/oxygen measurements
- Species counts ("27 people have visited")
- Distance/size comparisons ("5 Grand Canyons fit in Challenger Deep")
- Timeline graphics

**Data accuracy requirement:** Every number on screen must come from beat_sheet.json timestamp. Infographic appears precisely when narrator mentions the data point.

**Key rules:**
1. Generate diagram clean and unlabeled
2. Add all text in Remotion (via SVG, image overlays, or animated callouts)
3. Animate numbers/labels to appear/change on beat_sheet timestamps
4. Never embed text in the image model (hallucination risk)

---

## Cinematic vs. Infographic: The Distinction

**Cinematic styles** (01–05):
- Focus on **immersion and emotional experience**
- Viewer is "present" in the moment (B&W film, underwater descent, wildlife encounter)
- Tell a story through visual composition and subject behavior
- Higher production cost justified by narrative impact

**Scientific/Infographic style** (06):
- Focus on **information clarity and education**
- Viewer is "reading" the data (measuring, comparing, understanding)
- Text and numbers are essential (but added in Remotion, never in model)
- Lower production cost, highest information density

---

## Image-First Workflow (Critical)

**For ALL styles, always follow this sequence:**

```
1. Generate static image (Nano Banana 2)
   ↓
2. Review and approve image quality
   ↓
3. If iteration needed → regenerate image
   ↓
4. Once approved, extend to video IF narrative requires motion
   ↓
5. Add audio, color grade, overlays in Remotion
   ↓
6. Schedule against beat_sheet.json timestamps
```

**Why image-first?**
- Images are 10–100× cheaper than video
- Faster iteration and approval cycles
- Images stay consistent across video composition
- Video generation is a final "hero moment" decision, not a default

**Never:**
- Start with video and extract frames
- Generate video without image reference
- Generate both image and video for same scene (wasteful)

---

## Post-Processing Pipeline

### Universal Rules (All Styles)

1. **Audio layers (three-layer system):**
   - Narration: Always top layer, clearest
   - Music/score: Underscore, ducked below narration
   - Ambient/SFX: Scene-specific (underwater sounds, creature sounds, environmental tone)
   - All transitions are crossfades (never hard cuts into silence)

2. **Timing alignment:**
   - Every visual cut, creature reveal, infographic appearance → scheduled on beat_sheet.json
   - Narrator is the master clock
   - No silent gaps in final output

3. **Text (CRITICAL):**
   - Text NEVER generated in image model
   - Text ALWAYS added in Remotion
   - Ensures accuracy, placement control, animation timing

4. **Color grading:**
   - Style 01 (B&W): Enhance grain/contrast
   - Style 02 (3D): Maintain bright synthetic palette
   - Style 03 (Maps): Maintain clarity, enhance label readability
   - Style 04 (Underwater): Grade for zone transitions (bright blue → black → bioluminescence)
   - Style 05 (Wildlife): Warm color, enhanced bokeh
   - Style 06 (Infographic): High contrast, legibility

### Style-Specific Post-Processing

**Style 01 (Archival):**
- Add 1.5–2% film grain
- Boost contrast slightly
- Desaturate if not already grayscale
- Add subtle flicker (optional, for authenticity)

**Style 02 (3D Synthetic):**
- Ensure colors are saturated and clear
- No blur or grain (unless depth-of-field intentional)
- Keep geometric lines sharp

**Style 03 (Maps):**
- Ensure readability of overlaid text
- Add depth lines/distance indicators in Remotion
- Animate zoom/pan if showing journey

**Style 04 (Underwater):**
- Color grade for zone transition: surface (bright blue) → twilight (deep blue) → midnight (black) → hadal (black + bioluminescence)
- Add water particle effects in Remotion if needed
- Ensure creature descriptions match visuals exactly
- Crossfade between clips (no hard cuts)

**Style 05 (Wildlife):**
- Enhance warm color tones
- Boost saturation slightly
- Add subtle bokeh blur if model didn't deliver enough DOF
- No heavy effects (keep focus on subject)

**Style 06 (Infographic):**
- Ensure high contrast for data readability
- Add text labels in Remotion (animated to appear on beat)
- Highlight key numbers with color accent
- No unnecessary decoration

---

## Model Selection by Style

See **MODEL_SELECTOR.md** for detailed pricing and decision trees.

| Style | Primary Model | Platform | Cost per Asset |
|-------|---------------|----------|-----------------|
| 01 Archival | Nano Banana 2 | kie.ai | $0.04–0.09 |
| 02 3D Synthetic | Nano Banana 2 | kie.ai | $0.04–0.09 |
| 03 Satellite/Map | Nano Banana 2 | kie.ai | $0.04–0.09 |
| 04 Underwater | Kling 2.1 Pro | kie.ai | $0.125–0.25 per 5sec |
| 04 Underwater (Hero) | Veo 3 Quality | kie.ai | $2.00 per 8sec |
| 05 Wildlife | Nano Banana 2 | kie.ai | $0.04–0.09 |
| 05 Wildlife (Video) | Veo 3 Quality | kie.ai | $2.00 per 8sec |
| 06 Infographic | Nano Banana 2 | kie.ai | $0.04–0.09 |

**Default rule:** Use kie.ai. It's 30–70% cheaper than fal.ai on all models.

---

## Case Study: What They Found in the Deepest Place on Earth

*Astrum Earth, 34-minute deep-sea documentary*

### Style Distribution Throughout the Video

| Timecode | Style | Purpose | Duration |
|----------|-------|---------|----------|
| 0:00–2:09 | Archival B&W | Hook/mystery | 2 min |
| 2:09–5:30 | Archival B&W | HMS Challenger history | 3 min |
| 5:30–14:00 | 3D Synthetic | Plate tectonics explanation | 8.5 min |
| 2:16–5:04 | Satellite/Map | Geographic scale | Within narrative |
| 18:13–31:29 | **HD Underwater** | Main descent journey | **13 min** |
| 20:29–26:30 | Wildlife | Creature reveals | Within descent |
| Throughout | Infographic | Depth markers, pressure, scale data | Throughout |

### Key Insights

1. **Style 04 (Underwater) is the workhorse** — consumes 40% of runtime
2. **Multiple styles overlap** — underwater sequences include wildlife moments and infographic overlays
3. **Pacing rhythm** — narrator at 140–160 WPM; cuts every 30–90 seconds
4. **Color progression** — visual transition mirrors journey (bright → dark → bioluminescence)
5. **Data integration** — infographics appear exactly when narrator mentions numbers

See `references/channels/001_anomalous_wild/case_studies/what_they_found_in_the_deepest_place_on_earth/case_study.md` for full breakdown.

---

## Style Naming Convention

All style templates use consistent naming:

```
style_NN_[descriptive-name]/
├── style_NN_[descriptive-name].json    (template configuration)
├── STYLE_NN_README.md                  (style guide)
├── images/                             (representative frames / examples)
│   ├── style_NN_example_01.png
│   ├── style_NN_example_02.png
│   └── style_NN_example_03.png
├── prompts/                            (example generation prompts)
│   └── style_NN_sample_prompts.txt
└── frames/                             (extracted frames from reference videos)
    ├── frame_001.png
    ├── frame_002.png
    └── [...]
```

---

## Quick Prompt Templates

Use these as starting points. Customize for specific narrative needs.

### Style 01: Archival B&W
```
[Historical subject/event], 1960s–1980s documentary style, 
black and white, grainy film texture, high contrast, 
authentic archival footage, historical authenticity
```

### Style 02: 3D Synthetic
```
[Subject/process/anatomy], 3D render style, 
cross-section view, synthetic bright colors, 
clean geometry, educational diagram, labeled components optional
```

### Style 03: Satellite/Map
```
[Geographic location/feature], satellite view, 
topographic map style, overhead perspective, 
depth markers, geographic scale, information overlay
```

### Style 04: HD Underwater
```
[Creature/feature], underwater cinematic footage, 
submersible POV, depth color gradient, water particles, 
[depth zone] atmosphere, bioluminescence [if applicable], 
natural light and behavior
```

### Style 05: Wildlife
```
[Creature name], National Geographic wildlife cinematography, 
shallow depth of field, bokeh background, warm color grading, 
professional documentary, intimate animal portrait
```

### Style 06: Scientific Infographic
```
[Data/comparison/measurement], scientific infographic, 
high contrast, clean graphic design, information visualization, 
educational diagram, measurement scale, [specific data to display]
```

---

## Common Mistakes to Avoid

❌ **Mistake 1: Asking model to generate text**
- Problem: Models hallucinate and misspell
- Solution: Generate diagram clean → add text in Remotion

❌ **Mistake 2: Generating video first, extracting frames**
- Problem: Wasteful, blurry frames, expensive
- Solution: Generate image first → extend to video if needed

❌ **Mistake 3: Not scheduling against beat_sheet.json**
- Problem: Misaligned visuals, pacing issues, silences
- Solution: Every cut is triggered by narrator timestamp

❌ **Mistake 4: Hard cuts between scenes**
- Problem: Jarring, unprofessional
- Solution: Always use crossfades; add ambient audio layer

❌ **Mistake 5: Assuming Seedance 2.0 is available**
- Problem: API suspended March 15, 2026
- Solution: Use Veo 3 Quality or Kling 2.1 Pro instead

❌ **Mistake 6: Using fal.ai when kie.ai is 50% cheaper**
- Problem: Budget waste
- Solution: Default to kie.ai; use fal.ai only for unavailable models

---

## Related Documents

- **MODEL_CATALOG.json** — Full pricing and model specifications (agent-readable)
- **MODEL_SELECTOR.json** — Decision rules for model selection (agent-readable)
- **MODEL_SELECTOR.md** — Human-readable model selection guide
- **Style templates** — `style_01_*/ through style_06_*/` folders with JSON configs and examples
- **Case studies** — `references/channels/[channel]/case_studies/` for real-world style usage
- **CLAUDE.md** — Overall production workflow and quality standards
