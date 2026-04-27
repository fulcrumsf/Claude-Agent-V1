---
description: Anomalous Wild hybrid style — wildlife documentary foundation layered with AI-generated 3D renders, glitch cuts, edutainment pacing, and dark neon color grading. Distinct from generic nature documentary. Use for all Anomalous Wild productions.
status: active
channel: 001_anomalous_wild
---

# Style: Anomalous Wild Hybrid

## What Makes This Style Distinct

This is **not** a standard nature documentary style. Anomalous Wild sits at the intersection of four visual languages:

| Influence | What We Take From It |
|---|---|
| BBC / National Geographic | Cinematic framing, authoritative narration, macro photography |
| Zack D. Films | 3D AI renders for anatomy/mechanism, POV shots, hybrid real+CG |
| Kurzgesagt | Explainer animation inserts, clean data visualization, educational pacing |
| Glitch/Digital Art | Hard cuts, digital distortion, dark neon palette, anomaly reveals |

The result: **cinematic wildlife documentary with AI augmentation** — we show what a camera physically cannot capture.

---

## Color System

| Element | Hex | Usage |
|---|---|---|
| Background primary | `#612DD8` | Thumbnails, title cards, intro card |
| Background secondary | `#2B0B5A` | Gradient end, overlay backgrounds |
| Neon green accent | `#8AFA47` | Subject glow, logo symbol, arrow highlights |
| Electric cyan | varies | Glitch cuts, anomaly reveal frames |
| Warm gold | varies | Key fact callouts, species name cards |
| Text | `#FFFFFF` | All on-screen text |
| Arrow | `#FF2A2A` | Thumbnail arrows only |

**Video backgrounds:** `#2B0B5A` → `#0B0F1A` gradient. Never plain black. Never white. Never grey.

---

## Typography

| Use | Font | Weight |
|---|---|---|
| Headings / title cards | Bee Vietnam Pro | Bold |
| Subheadings / callouts | Mont Bold | Bold |
| Body text overlays | Mont Bold or Bee Vietnam Pro | Regular |
| Species name cards | Mont Bold (common) + Bee Vietnam Pro regular (Latin) | Mixed |

**Text animation:** Fly-in only. No static lower-thirds. No fade-in. Animated callouts for every key fact.

**Glitch text effect:** Apply to hooks and title cards only — not to every text element.

---

## Shot Language

### Core Shot Types (in priority order)

1. **Macro / extreme close-up** — Eyes, scales, feathers, skin texture, anatomical detail. This is the primary shot type for mobile. Use it whenever a new feature is introduced.

2. **POV shot** — The camera becomes the animal. Looking through a translucent eyelid. Seeing through compound eyes. Bioluminescence from inside the organism. This is the single highest-retention technique — use it once per video minimum.

3. **Hybrid real + 3D** — Real wildlife footage for establishing and behavioral shots. AI-generated 3D for mechanisms the camera cannot see: internal anatomy, the speed of a mantis shrimp punch, a nictitating membrane sliding across an eye.

4. **Overhead / God view** — Animal in habitat, wide frame, then rapid zoom to detail. Establishes scale before the anomaly.

5. **Slow-motion insert** — Impact moments, strikes, fluid motion. Cut from normal speed → slow-mo for effect. No extended slow-mo without narration.

### Shot Combinations That Work
- Wide establishing → hard cut to extreme macro → glitch cut to 3D render of mechanism
- POV shot → cut back to external macro → narrator explains what the viewer just saw
- Normal behavior → freeze frame → animated callout → resume action

---

## Pacing & Cut Rhythm

| Format | Cut Frequency | Narration Pace |
|---|---|---|
| Shorts (< 60s) | Every 1–2s | Brisk, no pauses |
| Medium (5–12 min) | Every 2–4s | Deliberate, let macro shots breathe |
| Long-form (15+ min) | Every 3–5s | Full Attenborough cadence |

**Rule:** Vocal pauses are edited out of narration. The story does not pause — only the music breathes.

**Micro-payoff frequency:**
- Shorts: every 5–8 seconds
- Medium: every 30–60 seconds
- Long-form: every 60–90 seconds

---

## Transition System

| Transition | When to Use |
|---|---|
| Hard cut | Default — between all standard shots |
| Glitch cut | Anomaly reveals, hook moments, surprising facts |
| Slow-mo freeze → resume | Impact moments, punch moments, fast movements |
| Zoom punch | Fact callouts that need emphasis |
| Music swell + hold | Before Tease #2 and the Reward — creates anticipation |

Never: wipes, dissolves, star transitions, or any "generic" transition.

---

## On-Screen Graphics System

### Species Name Card
```
[Common Name] — Bee Vietnam Pro Bold, white, 18–22px
[Genus species] — Bee Vietnam Pro regular, warm gold, 13–15px
Animated: fly in from left, hold 3s, fly out left
```

### Location Card
```
[Region/Country] — Mont Bold, white
Subtle animated map pin or geographic outline
Hold 2–3s then fade
```

### Anomaly Level Meter (optional — use for high-anomaly facts)
```
ANOMALY LEVEL: [1–10 bar, neon green fill]
Animated fill from 0 → value over 1.5s
```

### Fact Callout
```
Bold key phrase, white or warm gold
Fly in from off-screen, sync to narrator hitting the fact
Hold through end of sentence, then exit
```

---

## Audio Stack

### Narration
- **Primary voice:** Higsley Bishonship (ElevenLabs ID: `KYhuk3Y57IlkV1ZjtDAt`)
- **Backup / dramatic intros:** David — Deep Documentary (`jvcMcno3QtjOzGtfpjoI`)
- Model: `eleven_multilingual_v2` or `eleven_turbo_v2_5`
- Settings: Stability 0.55 · Similarity 0.80 · Style 0.30 · Speaker Boost ON

### Music
- Style: cinematic, mysterious, atmospheric — not upbeat, not lo-fi
- Source: Kie.ai Suno API (V4.5 or V5, instrumental)
- **Volume envelope:** Full under B-roll → duck to ~15% under narration → 0 at end
- Music swell before Tease #2 and The Reward

### Sound Design
- Ambient sound matched to habitat (wind, water, forest, ocean) — always on, low level
- Stinger sounds on glitch cuts and anomaly reveals
- Subtle "whoosh" on text fly-ins
- **Deliberate silence** for 0.5–1s before the payoff fact — the silence creates tension

---

## AI Generation Pipeline

### For mechanisms the camera can't see
Use AI-generated 3D / video for:
- Internal anatomy (organs, cellular processes)
- Ultra-high-speed events (mantis shrimp punch, dragonfly wing mechanics)
- POV perspectives (through an eyelid, through compound eyes, inside bioluminescence)
- Microscopic biology (toxin release, chromatic cells firing)

**Prompt structure:**
```
Macro [animal] [specific anatomical feature], [mechanism in motion],
cinematic 8K, [Anomalous Wild palette: deep teal / forest dark green / amber],
[camera: slow push / extreme close-up / POV], National Geographic lighting,
photorealistic, no text
```

### For establishing shots
Use real CC0/licensed wildlife footage where possible. AI video (Kling/Veo 3) for rare animals with no available footage.

### Thumbnail subjects
Midjourney v6 or Fal.ai FLUX for hyper-realistic single-animal hero shots. Rule: the animal must look slightly "wrong" — a color that shouldn't exist, an anatomy that looks impossible. Apply neon green glow in post.

---

## Long-Form Specific Rules (15+ min)

- **Chapter structure required** — add timestamps to description
- **Meme insert** (1-second reaction cut) every 4–6 minutes to reset attention — Steve Harvey "no", Michael Scott reaction, etc. Keep it subtle, never the focus
- **Double Reveal** in every chapter — never stop at one surprising fact, always escalate
- **Map animation** when introducing a new species' habitat — 2–3 second animated range map, then cut to footage
- Recurrence of Anomalous Arc within each chapter — each animal gets its own mini-Hook → Context → Reward
- **Anti-pattern to avoid:** BRIGHT SIDE's mosaic strategy (random fact compilation, no narrative coherence) performs ~94% worse than structured listicle with Double Reveal at same runtime

---

## Reference Channels (ranked by relevance)

1. **Zack D. Films** — POV shots, 3D hybrid, macro dominance
2. **Be Amazed** — Double Reveal listicle structure, Visual Lie thumbnails
3. **Ze Frank (True Facts)** — Edutainment voice, fact-to-humor ratio, format branding
4. **Kurzgesagt** — Animated explainer inserts, data visualization style
5. **ReYOUniverse** — Grand Perspective Shift hook, long-form chapter structure
6. **BBC Earth / National Geographic** — Cinematic shot language foundation
