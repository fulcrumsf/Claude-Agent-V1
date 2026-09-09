---
name: youtube-thumbnail-design
description: "YouTube thumbnail design with specific dimensions, contrast rules, and mobile preview optimization. Covers safe zones, text placement, face expression psychology, and A/B testing. Use for: YouTube thumbnails, video cover images, click-through optimization. Triggers: youtube thumbnail, thumbnail design, video thumbnail, click through rate, ctr optimization, youtube cover, video cover image, thumbnail maker, thumbnail tips, youtube design, video preview image"
allowed-tools: Bash(infsh *)
---

# YouTube Thumbnail Design

Create high-CTR YouTube thumbnails with AI image generation via [inference.sh](https://inference.sh) CLI.

## Quick Start

> Requires inference.sh CLI (`infsh`). [Install instructions](https://raw.githubusercontent.com/inference-sh/skills/refs/heads/main/cli-install.md)

```bash
infsh login

# Generate a thumbnail
infsh app run falai/flux-dev-lora --input '{
  "prompt": "YouTube thumbnail style, close-up of a person with surprised excited expression looking at a glowing laptop screen, vibrant blue and orange color scheme, dramatic studio lighting, shallow depth of field, high contrast, cinematic",
  "width": 1280,
  "height": 720
}'
```


## Specifications

| Spec | Value |
|------|-------|
| Dimensions | 1280 x 720 px (minimum) |
| Recommended | 1920 x 1080 px |
| Aspect ratio | 16:9 |
| Max file size | 2 MB |
| Formats | JPG, GIF, PNG |

## The 120px Test

Your thumbnail appears at roughly **120px wide** on mobile — that's how most viewers first see it.

**At 120px, viewers must be able to identify:**
1. The mood/emotion (from colors and expression)
2. The general subject (from composition)
3. The text (if any — only if large enough)

**Test:** view your thumbnail at 120px width. If it's a muddy blur, redesign.

## Safe Zones

```
┌─────────────────────────────────────────────┐
│                                             │
│   ✅ SAFE FOR TEXT AND KEY ELEMENTS         │
│                                             │
│                                             │
│                                             │
│                                             │
│                                       ┌───┐ │
│                                       │ ⏱ │ │ ← Timestamp overlay
│                              ┌────────┴───┘ │    (bottom-right)
│   ┌────┐                     │  DURATION    │
│   │ CH │ Chapter marker      └──────────────│
└───┴────┴────────────────────────────────────┘
     ↑ Bottom-left: chapter/progress markers
```

**Avoid placing critical elements in:**
- Bottom-right corner (video duration timestamp)
- Bottom-left corner (chapter markers, progress bar)
- Extreme edges (cropping varies by device)

## Color Strategy

### High-Contrast Pairs That Work

| Combination | Mood | Best For |
|-------------|------|----------|
| Yellow + Black | Urgency, attention | Tech, business, lists |
| Red + White | Energy, excitement | Entertainment, reactions |
| Blue + Orange | Professional contrast | Education, tutorials |
| Green + White | Growth, money | Finance, success stories |
| Purple + Yellow | Premium, creative | Design, art, creativity |
| White + Dark | Clean, minimal | Luxury, minimalist channels |

### Color Rules

- **Background** and **text/subject** should be complementary or high-contrast
- Avoid same-temperature colors touching (red on orange = mud)
- Use **3 colors maximum** per thumbnail
- Saturate more than real life — thumbnails compete with bright UI

## Text on Thumbnails

### When to Use Text

- Lists/numbers: "7 Tips", "Top 10"
- Strong opinions: "STOP Doing This"
- Results: "$10K in 30 Days"
- Comparisons: "vs" between two things

### When NOT to Use Text

- The video title already says it (redundant)
- The emotion/visual tells the story
- You can't make it large enough to read at 120px

### Text Rules

| Rule | Reason |
|------|--------|
| Max 6 words | Readability at thumbnail size |
| Min 60pt equivalent | Must be legible at 120px width |
| Bold sans-serif font | Thin fonts disappear at small sizes |
| Contrast stroke/shadow | Ensures readability on any background |
| No small text | If it's not readable small, cut it |

## Face Expression Psychology

Thumbnails with faces get **higher CTR** than faceless thumbnails. Expression matters:

| Expression | CTR Impact | Best For |
|------------|-----------|----------|
| **Surprise/shock** | Highest | Reaction, reveal, discovery content |
| **Curiosity** | High | Tutorial, how-to, tips |
| **Excitement** | High | Unboxing, reviews, announcements |
| **Concern/worry** | Medium-high | Warning, mistake, problem content |
| **Confidence** | Medium | Expert advice, authority content |
| **Neutral** | Lowest | Avoid unless your brand is minimalist |

### Face Composition Rules

- Face should fill **30-50%** of the thumbnail
- Eyes looking **toward the text or subject** (directs viewer attention)
- Eyes looking at camera = connection. Eyes looking at object = curiosity.
- Place face on one side (usually left), text or subject on the other

```bash
# Generate a face-forward thumbnail
infsh app run falai/flux-dev-lora --input '{
  "prompt": "close-up portrait of a man with genuinely surprised expression, mouth slightly open, raised eyebrows, looking at camera, left side of frame, vibrant teal background, dramatic rim lighting, YouTube thumbnail style, high contrast, cinematic",
  "width": 1280,
  "height": 720
}'

# Generate a face-looking-at-subject thumbnail
infsh app run bytedance/seedream-4-5 --input '{
  "prompt": "person looking amazed at a glowing holographic chart showing upward growth, dramatic blue and green lighting, right side profile view, dark background, tech aesthetic, high energy",
  "size": "2K"
}'
```

## Thumbnail Patterns by Content Type

### Tutorial / How-To
```bash
infsh app run falai/flux-dev-lora --input '{
  "prompt": "overhead flat lay of organized workspace with laptop showing code editor, colorful sticky notes, coffee cup, clean bright background, professional setup, tutorial style composition, warm lighting",
  "width": 1280,
  "height": 720
}'
```

### Before/After
```bash
infsh app run falai/flux-dev-lora --input '{
  "prompt": "split composition, left side dark and messy disorganized desk, right side bright clean organized minimalist workspace, dramatic contrast between chaos and order, clear dividing line in center, high contrast",
  "width": 1280,
  "height": 720
}'
```

### Product Review / Comparison
```bash
infsh app run falai/flux-dev-lora --input '{
  "prompt": "two products facing each other with dramatic lighting and sparks between them, competition battle concept, dark background with colorful rim lighting, versus comparison style, high energy, product photography",
  "width": 1280,
  "height": 720
}'
```

### Listicle / Number
```bash
infsh app run falai/flux-dev-lora --input '{
  "prompt": "dynamic arrangement of 7 different colorful objects floating in space against dark gradient background, each item distinct and clearly separated, energetic composition, vibrant saturated colors, studio lighting",
  "width": 1280,
  "height": 720
}'
```

## A/B Testing

Test one variable at a time:

| Variable | Test A vs B |
|----------|-------------|
| Face vs No face | Same composition, with/without person |
| Expression | Surprise vs curiosity |
| Color scheme | Warm vs cool palette |
| Text vs No text | With/without text overlay |
| Background | Bright vs dark |
| Composition | Left-facing vs right-facing subject |

```bash
# Generate variant A
infsh app run falai/flux-dev-lora --input '{
  "prompt": "..., bright yellow background, ...",
  "width": 1280, "height": 720
}' --no-wait

# Generate variant B (same prompt, different background)
infsh app run falai/flux-dev-lora --input '{
  "prompt": "..., dark navy background, ...",
  "width": 1280, "height": 720
}' --no-wait
```

## Thumbnail Checklist

- [ ] 1280x720 minimum (1920x1080 preferred)
- [ ] Under 2MB file size
- [ ] Passes the 120px squint test
- [ ] No critical elements in bottom-right (timestamp) or bottom-left (chapter)
- [ ] Max 3 colors, high contrast
- [ ] Text (if any) is max 6 words, bold, with contrast stroke
- [ ] Face expression matches content energy (if applicable)
- [ ] Doesn't duplicate the video title
- [ ] Stands out from surrounding thumbnails (check your niche)
- [ ] Works on both light and dark YouTube backgrounds

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Too much text | Unreadable at thumbnail size | Max 6 words or no text |
| Low contrast | Disappears in the feed | Use complementary colors |
| Cluttered composition | Eye doesn't know where to look | One focal point |
| Generic stock photo feel | No personality, gets skipped | Authentic expressions, unique angles |
| Tiny details | Lost at 120px | Bold, simple shapes |
| Same style every video | Viewer fatigue | Vary within brand guidelines |
| Misleading thumbnail | Kills trust, hurts retention | Match the actual content |

## Optional Mode: Architecture-First Thumbnail Pass

Use this additive mode when the thumbnail has multiple subjects or props, a
specific visual story, a recurring character, a complex environment, or a
high-cost image-generation workflow. It does not replace the Quick Start,
pattern prompts, checklist, or A/B-testing rules above.

Reusable field structure: `Thumbnail-Architecture-Template.json` in this skill
folder. Fill its placeholders from the actual video; do not copy its defaults
over the video evidence.

### Mandatory Visual Reference Gate

Do not design, prompt, or generate a thumbnail from text-based takeaways alone.
Before starting, visually inspect at least one approved example of a good
thumbnail relevant to the subject, channel, or intended composition. Record
the concrete visual lessons being adapted: focal hierarchy, subject scale,
expression, gaze, contrast, text-space placement, background simplicity, and
mobile readability. If no suitable visual example has been inspected, pause
thumbnail work and obtain one before proceeding. Use the example as a design
reference, never as an exact composition or protected artwork to copy.

### Step 1: Define the Visual Promise

Before generating, write one sentence answering: "What should a viewer
understand or feel in one second?" Choose one dominant story anchor. Do not
automatically turn a compilation into a crowded collage; secondary elements
must support the anchor rather than compete with it.

For a compilation, the visual hook and any text overlay must communicate the
shared collection-level payoff, not accidentally promise only the single scene
shown. Use a representative hero moment that implies the recurring pattern,
while keeping the overlay short and collection-oriented. Compare the copy with
the actual clip set and reject wording that overpromises one isolated event.

Demographics and identity must come from the actual video content. Never use a
default ethnicity, age presentation, wardrobe, or regional identity simply
because it appeared in an earlier thumbnail. Variation is welcome only after
the thumbnail has been checked against the people represented in the source
video.

### Step 2: Create a Thumbnail Architecture Brief

Fill in this brief before writing the image prompt:

```text
Title/topic promise:
Primary focal subject:
Foreground:
Midground:
Background:
Subject scale and frame position:
Eye path and gaze direction:
Lighting direction and subject/background separation:
Dominant palette and contrast relationship:
Reserved text area:
Elements to keep simple or exclude:
Mobile-size readability risk:
YouTube UI safe-zone risks:
```

The brief should deliberately specify visual hierarchy, approximate placement,
negative space, and the intended title area. Keep critical elements away from
the bottom-right timestamp area, bottom-left chapter/progress area, and extreme
edges, while still applying the existing Safe Zones section.

### Step 3: Decide Whether To Split Assets

Use one generation when the scene is visually simple. Generate complex assets
separately when they are likely to compete for prompt attention or lose their
identity, such as:

- A recurring human face or mascot
- A detailed animal, product, prop, or device
- Multiple logos or recognizable symbols
- A screen, sign, or other element requiring controlled content

Assemble separated assets in a staged composite only when doing so gives more
control. The goal is to isolate failure modes, not to add complexity for its
own sake. Never copy a reference thumbnail's exact people, logos, protected
artwork, or composition.

### Step 4: Refine One Variable At A Time

Preserve the best accepted version and make one meaningful change per
refinement pass, such as screen content, prop placement, wardrobe color,
material polish, or lighting. Do not combine unrelated changes when a working
composition or subject identity could be damaged. Keep every iteration
non-destructive and use a new version rather than overwriting a prior result.

### Step 5: Run The Existing Validation Plus These Additions

- Re-run the existing 120px test, safe-zone check, contrast check, text check,
  and content-truth check.
- Confirm the main visual promise is still understandable without reading the
  title.
- Confirm the eye lands on one dominant anchor before secondary details.
- Confirm the reserved text area remains open and readable.
- Confirm faces, animals, props, and logos have not changed identity or merged.
- Inspect at mobile size on both light and dark backgrounds.
- Treat CTR or "viral" improvement as a hypothesis to test, not a guarantee.

## Related Skills

```bash
npx skills add inference-sh/skills@ai-image-generation
npx skills add inference-sh/skills@image-upscaling
npx skills add inference-sh/skills@prompt-engineering
```

Browse all apps: `infsh app list`
