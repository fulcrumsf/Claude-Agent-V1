# Video Report Card — Bioluminescence Weapon
**Channel:** Anomalous Wild
**Video:** 001_anomalous_wild — Bioluminescence (The Deep-Sea Animal That Makes Its Own Light)
**Grade:** B+
**Previous Grade:** C-
**Review Date:** 2026-03-29

---

## Naming Convention
- All video output folders must be prefixed with a zero-padded sequence number
- Format: `001_`, `002_`, `003_` etc.
- First video for this channel = `001_anomalous_wild`
- Apply to all channels going forward

---

## Critique Notes

### 001 — Title Card (0:00)
- **Issue:** Generic 3D star field animation. Looks like a 1995 PowerPoint title. Could belong to any video.
- **Standard:** George Lucas / Pixar cinematic title card. World-specific atmosphere — put the viewer underwater before the story starts.
- **Reference:** Example 001A (Motion Array underwater template) — this is the mood and vibe required.
- **Fix:** Rebuild title card with specific underwater atmosphere. Scrap current 3D star field entirely.

### 001B — Title Card Audio
- **Issue:** Dead silence during title card. Narration stops, nothing fills the space. Kills momentum.
- **Fix:** Add ambient audio bed during title — ocean pressure, deep water hum, or subtle impact/boom when title hits. Must feel like being pulled underwater.

### 002 — Text Overlay Timing (approx. 0:36–0:37 and general)
- **Issue:** "200m" overlay appears several seconds after narrator says "200 meters." Same delay on "1km." Overlays are manually estimated, not locked to speech.
- **Root cause:** Overlays are placed by guesswork, not by word-level timestamps.
- **Fix:** Use ElevenLabs word-level transcript timestamps (or generate our own transcription with timestamps if ElevenLabs doesn't provide them). Every text overlay must be locked to the exact frame the word is spoken. The narration audio is the master clock — all visuals trigger from it.

### 002B — Workflow Change: Beat Map Must Come From Audio
- **Current workflow (wrong):** Generate audio → manually estimate timecodes → place visuals
- **Correct workflow:** Generate audio → extract word-level timestamps → build beat map → all visuals scheduled against beat map
- This is a fundamental workflow change that applies to every video going forward.

### 003 — Sound Design (general)
- **Issue:** No ambient sound mixing. Clips feel sterile and disconnected. No immersion.
- **Standard:** BBC Earth documentary sound design.
- **Fix:** Three-layer audio system:
  1. **Narration** — always on top, always clearest
  2. **Music/Score** — underneath, responds to story emotional beats
  3. **Ambient/SFX** — scene-specific natural sound (ocean, creature movement, environment)
- All audio transitions must crossfade — no hard cuts between scenes
- Music transitions must be blended like a sound engineer would mix them
- Kling clips should be generated with `sound: true` for ambient layer
- Suno generates one long instrumental score from a high-level mood description of the video (e.g. "nature documentary, deep ocean, mysterious and tense with moments of wonder, orchestral strings, low brass, no lyrics")
- That score plays under the whole video, ducked below narration

### 004 — Phylogenetic Tree Animation (approx. 1:39)
- **Issue:** Abstract dots-and-lines animation for ~40 seconds. No visual representation of jellyfish, squid, beetles, fungi, or bacteria. Viewer has nothing to connect to.
- **Fix:** Replace with a dynamic scientific illustration system. When narrator says "jellyfish" → glowing anatomical jellyfish illustration appears. When narrator says "beetle" → beetle appears. Each connects visually as he draws the evolutionary parallel.
- Style reference: BBC Earth meets scientific textbook — glowing blueprint aesthetic (see jellyfish NSF diagram reference).
- Timing: triggered by word-level timestamps from beat map.

### 005 — Scientific Diagrams with Hallucinated Text (approx. 2:33 and 3:34)
- **Issue (critical):** AI-generated diagrams contain gibberish, misspelled, and nonsensical text labels. Examples:
  - "light bulbs," random non-language characters (Example 003, ~2:33)
  - "Aluprymna scolopes" (should be Euprymna scolopes), "SXster syctum" (Example 004, ~3:34)
- **Root cause:** Image generation models cannot reliably render accurate text. They hallucinate letters. They must never be used for anything requiring readable labels.
- **Rule going forward:** The image model draws the picture only. It never writes the words.

**Correct scientific diagram pipeline:**
1. Researcher finds real accurate reference image of the subject (Google Images, scientific journals, etc.) — saved to project reference folder
2. Nano Banana recreates the visual illustration style WITHOUT any text, lines, arrows, or callouts (negative prompt: "no text, no labels, no callout lines, no arrows, no annotation marks")
3. All text labels and callout arrows added separately in Figma (MCP access available) or SVG
4. Export as PNG or SVG and drop into Remotion as a static asset

### 006 — Anatomical Accuracy of Animals
- **Issue:** Some video clips show animals with anatomically incorrect features. Example: anglerfish bioluminescent lure shown coming from wrong location (tongue vs. dorsal fin on head).
- **Root cause:** Text-to-video generators hallucinate anatomy when given no visual reference.
- **Fix:** For any scientifically specific animal or organism, researcher must:
  1. Find real reference images of what the animal actually looks like
  2. Save references to project folder
  3. Nano Banana builds an anatomically correct reference image using those references
  4. That image becomes the starting frame for Kling or Veo3
- This applies to all animals, organisms, and scientific subjects going forward.

---

## Workflow Changes Required (Summary)

| # | Change | Priority |
|---|--------|----------|
| 1 | Naming convention: all video folders prefixed with zero-padded number | High |
| 2 | Beat map built from ElevenLabs word-level timestamps, not manual estimation | Critical |
| 3 | Three-layer audio system (narration / score / ambient) with crossfades | High |
| 4 | Kling clips generated with `sound: true` | Medium |
| 5 | Suno generates full-length background score per video | High |
| 6 | Reference image step required before any video generation for scientific subjects | Critical |
| 7 | Nano Banana reference images: always negative-prompt out text and callout lines | Critical |
| 8 | Scientific diagram labels added in Figma or SVG — never by image model | Critical |
| 9 | Clip manifest generated for every video (clip ID, reference image ✓/✗, source, model used) | High |
| 10 | Title card rebuilt with cinematic world-specific atmosphere + ambient audio | High |
| 11 | FCPXML export generated for every video using relative paths | Medium |
| 12 | Dynamic infographic system: illustrations triggered by narration beat map | High |

---

## Research Tasks Before Next Video

- [ ] Research best pipeline for accurate scientific infographics (OpenAI image model, Figma, SVG-in-Remotion)
- [ ] Test ElevenLabs word-level timestamp output format
- [ ] Research Suno API for long-form background score generation
- [ ] Evaluate Kling `sound: true` quality for ambient scene audio
- [ ] Build FCPXML export script using relative paths
- [ ] Build clip manifest generator
