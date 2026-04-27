# Prompt Best Practices

> 📋 **This is a placeholder.**
>
> The full Prompt Best Practices guide — covering model-specific guidelines, prompt structure, aspect ratio optimization, reference image techniques, and content-specific tips — is proprietary.
>
> We use these guides internally and refine them continuously with real campaign data. They're shared exclusively with RoboNuggets community members — the people who make these free lessons possible.
>
> **Get the full guide →** [RoboNuggets.com](https://robonuggets.com)

---

## Quick Tips (Starter)

Here are a few basics to get you going:

- **Always start with aspect ratio** — prefix your prompt with the ratio: `9:16.` (vertical), `4:5.` (LinkedIn/square-ish), `16:9.` (landscape)
- **Describe realistic scenes** — natural lighting and authentic settings perform better than polished studio
- **Reference your input images** — include "Using input image 1 for product reference" so the model knows to match product appearance
- **Keep it authentic** — UGC/selfie-style prompts consistently outperform over-produced studio aesthetics
- **Be specific about the person** — age range, clothing style, body language, and camera angle all matter
- **Describe the energy** — "excited", "calm confidence", "casual surprise" give the model emotional direction

### Example Prompt
```
9:16. A young woman in casual streetwear naturally holding [product], selfie-style angle,
warm natural lighting, authentic social media aesthetic. Using input image 1 for product identity.
```
