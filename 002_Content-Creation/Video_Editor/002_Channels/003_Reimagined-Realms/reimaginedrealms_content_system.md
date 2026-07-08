---
title: "Reimagined Realms — Channel Content System"
type: doc
domain: content-creation
tags: [doc, content-creation, video-production, history, educational]
last-updated: 2026-06-18
---

# REIMAGINED REALMS — CHANNEL CONTENT SYSTEM

> ⚠️ **PIVOT NOTE (June 2026):** Previous identity (comedy POV/vlog — "What if history had a camera?") has been deprecated. The channel is now a historical/scientific explainer. All old content pillars, thumbnail rules, and prompt templates below reflect the new direction.

---

## CORE IDENTITY

- **Brand:** Reimagined Realms
- **Tagline:** History is stranger than fiction. We're here to prove it.
- **Tone:** Intelligent, curious, calm — like a professor you actually want to listen to
- **Model channel:** Brightside — jaw-dropping hook, visual hook + audio hook + on-screen text hook in first 2 seconds, scientific explainer style
- **Audience:** Curious adults who like learning surprising things — history buffs, science-adjacent viewers, ages 18–45
- **Concept:** Historical and history-adjacent explainer videos. The jaw-drop comes from the FACT being surprising, not from comedy or reimagining. Topics range from major historical events to forgotten crafts, techniques, artifacts, and discoveries — anything where the real story is more interesting than most people realize.
- **Disclaimer:** *This channel is for entertainment purposes. While we strive for accuracy, content may be simplified or condensed for storytelling.*

---

## WHAT THIS CHANNEL IS NOT

- ❌ Not comedy or satire
- ❌ Not "what if history was different"
- ❌ Not POV vlogging or modern-framing-meets-ancient-world
- ❌ Not reaction content or tier lists
- ✅ Real history, real facts, presented in a way that feels surprising and cinematic

---

## CONTENT PILLARS

1. **Hidden engineering & lost techniques** — the real science behind how something was built, forged, or made
   - "The Hidden Engineering Secret Inside the Great Pyramids"
   - "Why the Samurai Sword Was the Most Advanced Blade Ever Made"
   - "The Blacksmith Technique That Died With One Man"

2. **Discoveries that rewrite what we thought we knew** — archaeology, science, newly uncovered evidence
   - "Scientists Just Found Something Beneath the Sphinx"
   - "This Viking Burial Changed Everything We Knew About Norse Women"

3. **The real story behind iconic moments** — what actually happened vs. the popular version
   - "What Really Happened the Night Rome Fell"
   - "The Battle of Thermopylae — What Movies Left Out"

4. **History-adjacent: craft, skill, and mastery** — deep dives into techniques, tools, and trades from history
   - "The Japanese Art That Took 10 Years to Master"
   - "How Medieval Castles Were Actually Built (It's Not What You Think)"

5. **Forgotten people and stories** — individuals or groups history largely ignored
   - "The Mathematician Who Calculated the Earth's Circumference in 240 BCE"
   - "The Army That Was Never Defeated"

---

## HOOK SYSTEM (Brightside Formula)

### First 2 Seconds — Triple Hook
Every video must land all three simultaneously:
- **Visual hook** — striking, unexpected, or cinematic opening image
- **Audio hook** — first line of narration is the most surprising fact or question
- **On-screen text hook** — mirrors or amplifies the audio hook

### Opening Line Formula
Lead with the most jaw-dropping version of the fact. Examples:
- "It turns out scientists have discovered the Great Pyramids can survive a 9.0 earthquake — and they did it on purpose."
- "The sword this blacksmith made 800 years ago still can't be replicated today."
- "For 500 years, historians got this completely wrong."

### First 30 Seconds
- Establish why this is more surprising than the viewer expected
- Create a curiosity loop — answer one question, open another
- The viewer should feel: "I had no idea. I need to see where this goes."

---

## VIDEO FORMAT

- **Length:** 3–10 minutes (flexible, topic-dependent)
- **Aspect ratio:** 16:9 (standard YouTube) or 9:16 (Shorts) — confirm per video
- **Narration:** Calm, intelligent, curious — no hype, no clickbait energy in the voice itself
- **Pacing:** Measured but never slow — every sentence earns its place

---

## THUMBNAIL SYSTEM

### Style
- Dark or cinematic background
- Central image: the most visually surprising element of the topic (artifact, structure, discovery)
- Text: states the surprising claim — not vague, not cute
- Color palette: TBD (previous cyan/charcoal palette may carry over or be refreshed)

### Rules
**DO:**
- Make the claim in the thumbnail feel credible, not clickbait
- Show the actual subject — the pyramid, the sword, the artifact
- Use contrast to make text instantly readable
- The thumbnail and title together should answer "why should I care?" in under 2 seconds

**DON'T:**
- No comedy or absurdist visuals
- No anachronism
- No generic "history documentary" stock imagery
- Don't be vague — the specific surprising thing should be implied

---

## TITLE SYSTEM

### Patterns That Work (Brightside-style)
- `Scientists Discover [Surprising Thing] About [Iconic Subject]`
- `The [X] That [Surprising Outcome Nobody Expected]`
- `Why [Famous Thing] Was More [Adjective] Than You Think`
- `What Really Happened [Famous Historical Event]`
- `The [Person/Object] History Forgot — And Why It Matters`

### Examples
- "Scientists Discover the Great Pyramid's Hidden Engineering Secret"
- "Why the Samurai Sword Is Still Impossible to Replicate"
- "The Battle Rome Never Talks About"
- "What Medieval Blacksmiths Knew That We've Forgotten"

---

## CHANNEL STATS (as of June 2026)
- Subscribers: 193
- Videos: 240
- Total Views: 127,000
- Avg views/video: ~529
- Status: Pivoting — new direction as of June 2026. Historical/scientific explainer replacing comedy POV format.

---

## CHANNEL DESCRIPTION (YouTube)

> History is stranger than fiction. We're here to prove it.
>
> Reimagined Realms digs into the real stories behind history's greatest moments — the forgotten techniques, hidden discoveries, and surprising science that never made it into the textbook.
>
> 🔔 Subscribe and learn something you'll actually want to repeat.
>
> *This channel is for entertainment purposes. While we strive for accuracy, content may be simplified or condensed for storytelling.*

---

## NARRATOR VOICE (ElevenLabs)

- **Tone:** Intelligent, curious, calm
- **Energy:** Measured — never rushed, never hype
- **Model:** ElevenLabs multilingual v2 (higher quality TTS)
- Voice selection: TBD — choose a voice that sounds like someone who has done real research and finds it genuinely interesting, not someone performing excitement

---

## AI PRODUCTION PIPELINE

See the Reimagined Realms video pipeline skill for the full production workflow. Summary:

1. **Topic research** — Perplexity (`sonar-pro`) surfaces the jaw-dropping angle
2. **Script** — GPT-4o writes the 3-min narration script with hook in first 15 seconds
3. **Voiceover** — ElevenLabs TTS (multilingual v2, calm/intelligent)
4. **Beat map** — built from ElevenLabs word-level timestamps
5. **Image prompts** — 15 images keyed to narrator's beats
6. **Images** — GPT-Image-2 via OpenAI API direct (photorealistic, cinematic)
7. **Video clips** — Seedance 2.0 Fast via kie.ai
8. **Music** — Suno via kie.ai (calm cinematic underscore)
9. **Assembly** — ffmpeg

**Estimated cost per episode:** ~$1.45–$2.17

---

## END SCREEN / CTA RULE (locked 2026-07-04)

Every finished video ends with a fixed 8-second hold, structured as:

1. **Story narration ends** (e.g. "...and that's the story of the missing people of Pompeii.")
2. **Silence gap: 1–2 seconds** — no narration, no CTA yet. This is audio-only; the video clip does NOT cut here.
3. **CTA narration plays**, using the pre-rendered static asset:
   `002_Content-Creation/Video_Editor/002_Channels/003_Reimagined-Realms/Brand_Assets/CTA/cta_follow_reimagined_realms.mp3`
   - Duration: 3.76s
   - Locked voice ID: `raMcNf2S8wCmuaBcyI6E`
   - Line: *"Follow Reimagined Realms. History gets stranger every episode."*
   - This is a reusable, channel-wide asset — generated once, never regenerated per-production. Do not create a new CTA line/audio per video.
4. **Video clip is held on one continuous shot** for the full 8 seconds — no visual cuts anywhere in this window, even though the audio has a gap followed by the CTA. The clip must be topically relevant to that episode's story (not generic), and visually clean since the YouTube end screen template overlays on top of it (avoid busy compositions in this shot).

**Hard rules:**
- Never let story narration spill into the final 8 seconds.
- Never cut between video clips inside the 8-second hold — audio gap is fine, video gap/cut is not.
- Total 8s = gap (~1–2s) + CTA audio (3.76s) + remaining trailing silence before cutoff.
- This is a pipeline-enforced constant in `assemble.py`'s end-of-timeline logic, not something the beatmap or per-video script decides.

## YOUTUBE UPLOAD DEFAULTS (via Blotato, locked 2026-07-04)

- `isMadeForKids`: **false**
- `containsSyntheticMedia`: **true** (channel uses AI-generated imagery)
- `privacyStatus`: private on upload (manual review before going public/unlisted)
- `playlistIds`: **not automated** — added manually per video during scheduling (may automate later)
- YouTube account must have "custom thumbnail" permission — if `create_post` errors with a thumbnail permission message, the account needs reconnecting in the Blotato dashboard (OAuth scope issue, not a code bug)
