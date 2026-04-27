---
description: Writes Anomalous Wild video scripts following the Anomalous Arc™. Produces narration-ready scripts with scene cues, text overlays, and music notes. Always reads the channel bible before writing.
status: active
channel: 001_anomalous_wild
---

# Skill: Anomalous Wild Script Writer

## Reference Files (read before writing)
- Channel bible: `references/channels/001_anomalous_wild/anomalos_wild_content_system.md`
- Style guide: `.agents/styles/anomalous-wild-hybrid.md`
- Case studies: `references/channels/001_anomalous_wild/case_studies/`

---

## Script Structure — The Anomalous Arc™

Every script follows this exact structure regardless of length:

```
[GLITCH HOOK]     0–3s
[SETUP]           3–30s
[TEASE #1]        30–90s
[CONTEXT LOOP]    90s–midpoint
[TEASE #2]        midpoint–near end
[REWARD]          final 15–20%
[HOOK FORWARD]    last 5s
```

---

## Script Format

Use this block format for every scene:

```
---
SCENE [N] — [SECTION NAME] — [TIMESTAMP RANGE]
---
NARRATION:
"[Exact spoken text. Every sentence on its own line for TTS pacing.]"

VISUAL: [Shot type + what the camera sees]
SOUND: [Ambient audio / music cue / stingers]
ON-SCREEN TEXT: [Animated callout text if any]
TRANSITION: [Hard cut / glitch cut / slow-mo freeze / none]
---
```

---

## Voice Rules

**Narrator persona:** David Attenborough-inspired — calm authority, genuine wonder, never panicked, never shouting. The facts are the drama.

**ElevenLabs settings:**
- Primary: Higsley Bishonship — ID: `KYhuk3Y57IlkV1ZjtDAt`
- Model: `eleven_multilingual_v2`
- Stability: 0.55 · Similarity: 0.80 · Style: 0.30 · Speaker Boost: ON

**Words to NEVER write in narration:**
`guys` · `literally` · `insane` · `crazy` · `OMG` · `kill` · `blood` · `die` · `dead` · `death` · `attack` · `brutally` · `graphic` · `shocking` · `violent` · `sex` · `mate` · `disgusting`

**Words and phrases to USE:**
`remarkably` · `what's extraordinary is` · `science has only recently discovered` · `of all the creatures on Earth` · `what we now know` · `the question that baffled researchers`

---

## Hook Rules

- First sentence must be a fact so strange it sounds impossible
- No introductions, no welcome, no channel name — start IN the story
- The visual that opens the video must be the most arresting frame in the entire piece
- Short sentences during hook. Longer sentences during context.

Example hook format:
> "This creature evolved its own light source. Not once — forty separate times. Across animals that have never shared a single ancestor."

---

## Retention Techniques to Embed

1. **Double Reveal** — after each fact, escalate: "But there's a stranger version..." or "And that's still not the most anomalous part."
2. **Curiosity gap** — withhold the most surprising implication until the Reward section
3. **POV cue** — write at least one scene from the animal's perspective ("What the anglerfish sees...")
4. **Micro-teasers** — plant one tease line every 60–90 seconds: "We'll come back to why this matters — but first..."

---

## Output

Deliver:
1. Full script in scene-block format (all sections labeled)
2. Estimated total runtime
3. Scene count
4. List of visual shots that need AI generation vs CC0 footage
