# Kie.ai Video Generation Models

## Overview
Complete list of kie.ai video generation models, capabilities, speed, and quality tiers.

## Available Models

### Veo (Primary Model)
**Capabilities:**
- Text-to-video generation
- High quality, cinema-style output
- Supports style specifications (documentary, underwater, wildlife, etc.)
- Generates 1080p at 24fps

**Speed:** 6–8 minutes per generated clip
**Cost:** $0.80–$1.20 per minute
**Best For:** Documentary, narrative, cinematic content

**Presets/Styles:**
- Archival B&W
- 3D Synthetic
- Satellite/Map
- HD Underwater
- Wildlife
- Scientific Infographic

---

### Flash Model (Fast Iteration)
**Capabilities:**
- Faster generation for drafts and previews
- Lower quality than Veo
- Good for testing prompts

**Speed:** 2–3 minutes
**Cost:** $0.40 per minute
**Best For:** Quick previews, rapid iteration, testing

---

### [Other Models]
[Document additional models as they become available]

## Prompt Engineering Best Practices

### Model-Specific Tips for Veo
- **B&W Mode:** "black and white, archival, grain, high contrast"
- **Underwater:** "underwater, crystalline, light rays, blue-green"
- **Wildlife:** "natural lighting, golden hour, shallow depth of field, animal behavior"
- **3D:** "clean 3D, rendered, geometric, no shadows"

### General Best Practices
- Descriptive but concise (under 150 words)
- Specify camera movement if needed
- Include emotion/mood descriptors
- Mention lighting and color grading

## Integration with Cinematic Styles

See `000_Skills/Cinematic-Styles.md` for detailed mapping of:
- Which model to use for each style
- Cost-quality tradeoffs
- Prompt templates by style

## Pricing Comparison

See `003_Tools/Video-Generation/Pricing-Matrix.md` for:
- Cost per minute by model
- Cost vs. fal.ai comparison
- Budget scenarios

## API Documentation
[Link to kie.ai API docs]

## Account & Authentication
[Notes on API key, rate limits, billing]

## Last Updated
[Date]
