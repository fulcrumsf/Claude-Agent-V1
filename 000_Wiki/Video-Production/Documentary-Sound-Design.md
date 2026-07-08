# Documentary Sound Design
*Reference for Reimagined Realms and all documentary-style productions*

---

## Overview

Professional nature documentaries (Planet Earth II, BBC Our Planet, Blue Planet II) treat sound as a narrative layer equal to visuals. Very little audio is actually captured on location — the majority of the final soundtrack is constructed in post-production from layered elements designed to guide emotional responses.

---

## The Three-Layer Audio Stack

Every professional documentary sequence is built from three simultaneous layers:

### 1. Ambience (Bed)
- Continuous environmental texture: wind, rain, room tone, distant wildlife
- Never silence — even "quiet" scenes have a low-level ambient bed
- Multiple micro-layers underneath (e.g., distant birds + leaf rustle + faint breeze)
- Shifts tonally between scenes to signal location or mood change

### 2. Sound Design (Foreground Events)
- Impact hits, foley, specific sound events tied to on-screen action
- Foley re-creates sounds impossible to capture in field (animal footsteps, movement textures)
- Telephoto lens problem: cameras can zoom in 50m but mics cannot isolate at that distance — everything is re-created
- Planet Earth II used ~30 individual audio tracks per shot

### 3. Music + Score
- Hans Zimmer / Jacob Shea / Jasha Klebe philosophy for Planet Earth II: *"All the music is trying to do is shine an additional light onto things"*
- Score blends orchestra with electronics and sounds from nature (locust swarms, thunder claps processed into score elements)
- Music **loses interest and holds still** during narration-heavy moments — uncluttered soundscape lets narrator guide
- Music only gets "epic harmonic / fist-pumping" when the visual story resolves

---

## Tension Architecture — The Standard Pattern

Used in virtually every high-stakes nature documentary sequence:

```
[Silence / minimal ambience]
→ Low riser begins (bowed metal, sub-bass texture)
→ Narration explains the situation
→ Percussion enters (percussive, staccato, rhythmic)
→ Intensity builds with each cut
→ IMPACT HIT at the moment of peak action or revelation
→ Emotional resolution music (harmonic, sweeping)
```

**Key rule:** Impact hits and tension risers should arrive **2–3 seconds before** major cuts — not on the cut itself. This pre-shadows the edit and makes the transition feel inevitable rather than abrupt.

---

## Key Techniques

### Risers
- Begin quietly, ramp up in volume and intensity
- Land at the loudest point just before a major cut or revelation
- Cinematic risers = sub-frequency + harmonic overtone + white noise sweep
- Duration: typically 3–8 seconds

### Impact Hits
- Release accumulated tension after a riser
- Define structure: punctuate cuts, emphasize title cards, anchor key visual moments
- Used sparingly — overuse kills dramatic effect
- One impact per major scene beat is the professional standard

### Whooshes / Transitions
- Short, directional sounds that signal movement between shots
- Maintain continuity and momentum during fast cuts
- Nature docs use organic whooshes (wind rushes, wing flaps) not electronic sweeps

### Wild Tracks
- Dedicated ambient recordings made on location specifically for post-production
- Planet Earth II sent sound recordists back to filming locations after cameras left
- Recorded herd sounds, animal calls, atmospheric textures separately from picture

---

## Documentary vs. Trailer Audio

| Element | Documentary | Trailer |
|---------|-------------|---------|
| Risers | Organic, slower builds | Electronic, faster |
| Impacts | 1 per major beat | Every few seconds |
| Ambience | Always present | Often stripped out |
| Music | Sits under narration | Often dominates |
| Silence | Used for dramatic contrast | Avoided |

---

## Narration Integration Rules (Attenborough Model)

- Music drops to near-silence or holds a single texture note during narration
- Ambient bed stays active (never cut ambience under VO)
- No competing melodic lines while narrator is speaking
- Resume musical momentum immediately after narration ends
- The narrator's voice IS the primary storytelling instrument — everything else supports it

---

## Application to Reimagined Realms

For Pompeii and all RR productions, the per-scene audio approach replaces the broad-stem approach:

1. **Each scene clip gets its own audio brief** based on visual analysis (Gemini frames)
2. **Classify each scene** into one of: Establishing, Rising Action, Peak Tension, Resolution, Transition
3. **Select sound type by scene class:**
   - Establishing → ambience bed + soft melodic underscore
   - Rising Action → low riser + percussive texture
   - Peak Tension → high riser landing to impact hit
   - Resolution → harmonic swell, emotional score
   - Transition → whoosh or silence cut
4. **Narration scenes** → drop music to single-note texture, keep ambience
5. **Never loop** — each clip's audio is unique and matches its visual duration

---

## Tools Available for RR Productions

| Task | Tool |
|------|------|
| Per-scene SFX (ambience, impacts, risers) | ElevenLabs SFX API |
| Music generation | Suno via kie.ai |
| Visual scene analysis | Gemini Vision (1fps frames) |
| Final mix placement | FCPXML → Premiere |

---

## Source References

- [How Planet Earth II Sound Conveys Realism — Hollywood Reporter](https://www.hollywoodreporter.com/lists/how-planet-earth-ii-sound-conveys-realism-a-sense-danger-1010977/)
- [The Sound of Planet Earth II — Resurface Audio](https://resurface.audio/planet-earth-ii-sound/)
- [Planet Earth II Composers on the Iguana Scene — SPIN](https://www.spin.com/2017/02/planet-earth-ii-composers-talk-music-david-attenboroughs-voice-interview/)
- [Planet Earth II Music Score — Variety](https://variety.com/2017/artisans/news/planet-earth-ii-music-score-1202014486/)
- [Sound Design and Foley in Documentaries — Nicolas Titeux](https://www.nicolastiteux.com/en/blog/sound-design-foley-documentaries/)
- [How to Create Tension with Sound Design — Bluezone Corporation](https://www.bluezone-corporation.com/blog/how-to-create-tension-with-sound-design)
- [What Are Cinematic Riser Sound Effects — Soundstripe](https://www.soundstripe.com/blogs/what-are-cinematic-riser-sound-effects)
- [Do Nature Documentaries Use Authentic Sounds — SoundCy](https://soundcy.com/article/do-nature-documentaries-have-sound)
