---
title: "Nano Banana Image Generation Guide"
type: tutorial
domain: design
tags: [tutorial, design, video-production, pricing]
---

# Nano Banana Image Generation Guide

## Overview
Comprehensive guide to Nano Banana image generation API, prompt patterns, and cost optimization.

## API Basics

**Provider:** [Provider info]
**Endpoint:** [API endpoint]
**Rate Limit:** [X requests per minute]
**Authentication:** [API key location and setup]

---

## Getting Started

### 1. Authentication
```
export NANO_BANANA_API_KEY="your_api_key_here"
```

### 2. Basic Request
[Code example for basic image generation]

### 3. Rate Limits
- [Tier 1]: [limit] requests/minute
- [Tier 2]: [limit] requests/minute

---

## Image Generation Parameters

### Required Parameters
- **Prompt:** [Description of image to generate]
- **Model:** [Which Nano Banana model to use]

### Optional Parameters
- **Size:** [Available dimensions, e.g., 512x512, 1024x1024]
- **Steps:** [Number of generation steps, quality vs. speed]
- **Seed:** [For reproducible results]
- **Guidance Scale:** [How strictly to follow prompt]
- **Negative Prompt:** [What to avoid in image]

---

## Prompt Engineering

### Effective Prompt Structure
```
[Subject] [Art Style/Medium] [Mood/Lighting] [Quality Modifiers]
```

**Example:**
"A crystal clear underwater reef scene, cinematic photography, volumetric light rays, 8K ultra-detailed, shot on 35mm lens, golden hour lighting"

### Style Keywords
- Photography: "cinematic photography", "professional photo", "35mm"
- Painting: "oil painting", "watercolor", "digital art"
- 3D: "3D render", "CGI", "Unreal Engine"
- Quality: "ultra-detailed", "8K", "high resolution"
- Mood: "dramatic", "serene", "ethereal"

### Common Pitfalls
- [Pitfall 1]: [How to avoid it]
- [Pitfall 2]: [How to avoid it]
- Avoid overly long prompts (diminishing returns after 150 words)

---

## Quality Tiers

| Setting | Speed | Quality | Use Case |
|---------|-------|---------|----------|
| Low (20 steps) | Fast | Basic | Previews, brainstorming |
| Medium (50 steps) | Standard | Good | Standard content |
| High (75+ steps) | Slow | Excellent | Portfolio, hero imagery |

---

## Cost Optimization

### Cost per Image (Estimated)
- Low quality: $[X]
- Medium quality: $[X]
- High quality: $[X]

### Batch Generation
[Guidelines for batch requests and volume discounts]

### When to Use High Quality
- Portfolio/showcase images
- Thumbnail imagery (visible in search)
- Product images (e-commerce)

### When to Use Low Quality
- Research/brainstorming
- Internal references
- Draft compositions

---

## Common Use Cases

### 1. Thumbnail Images
**Goal:** Eye-catching, clickable thumbnails for YouTube

**Prompt Formula:**
"Bold [subject], bright colors, high contrast, dramatic lighting, professional photography, 8K quality"

**Recommended Settings:**
- Size: 1280x720 (YouTube aspect ratio)
- Steps: 50 (good quality without overspending)
- Guidance: 7.5 (medium adherence to prompt)

---

### 2. Video Poster/Cover Art
**Goal:** Full HD cover image for video series

**Prompt Formula:**
"[Subject], cinematic composition, [Art style], professional 8K photography, [Mood]"

**Recommended Settings:**
- Size: 1920x1080
- Steps: 75 (high quality for prominent placement)

---

### 3. Social Media Graphics
**Goal:** Instagram, Twitter, Pinterest graphics

**Prompt Formula:**
"[Subject], modern design, bold colors, balanced composition, [platform] optimal"

**Recommended Settings:**
- Size: [Platform-specific, e.g., 1080x1350 for Instagram]
- Steps: 50

---

## API Code Examples

### Python Example
[Code snippet for Python request]

### JavaScript Example
[Code snippet for JS request]

### CLI Usage (if available)
[Command line examples]

---

## Troubleshooting

### Common Issues

**Issue:** Image quality is poor
- Solution: Increase steps, add quality descriptors to prompt

**Issue:** Prompt not being followed
- Solution: Increase guidance scale (0–20), simplify prompt

**Issue:** Rate limit errors
- Solution: Implement request queuing, reduce simultaneous requests

**Issue:** Generation takes too long
- Solution: Reduce steps, use lower quality tier

---

## Integration with Video Production

### Thumbnail Generation Workflow
1. Video editing complete
2. Generate 5–10 thumbnail variations using Nano Banana
3. A/B test thumbnails in YouTube studio
4. Use winning thumbnail
5. Document in case study

### Cost Estimate
- 10 thumbnails per month × [cost per image] = [monthly budget]

---

## Account Management

**API Key Location:** [Where to find/manage API key]
**Billing Dashboard:** [Link to usage/billing]
**Support:** [How to get help]

---

## Batch Processing

If generating multiple images:
- [Best practices for batch requests]
- [How to handle errors/retries]
- [Cost tracking for batches]

---

## Performance Benchmarks

| Model | Quality | Speed | Cost |
|-------|---------|-------|------|
| [Model A] | [Rating] | [Time] | $[X] |
| [Model B] | [Rating] | [Time] | $[X] |

---

## Advanced Tips

### For Specific Cinematic Styles
See `000_Skills/Cinematic-Styles.md` for style-specific prompt templates that work well with Nano Banana.

### Reproducible Results
Use seed parameter to regenerate similar images:
```
seed: 12345  (use same seed for variations)
```

### Color Grading Integration
Nano Banana output can be color-graded to match video cinematic style in post-production.

---

## Resource Links

- Nano Banana Documentation: [Link]
- API Status: [Link]
- Community Examples: [Link]

---

## Last Updated
[Date]
