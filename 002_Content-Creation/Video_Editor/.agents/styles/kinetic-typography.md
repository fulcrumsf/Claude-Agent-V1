---
description: Kinetic typography style. Text is the primary visual — words animate in sync with audio (narration, music, or speech). Bold, expressive, rhythm-driven. Used for lyric videos, quote reels, short-form hooks, and high-energy intro sequences. Primary tool: Remotion.
status: placeholder — needs interview to flesh out implementation details
---

# Style: Kinetic Typography

## Overview
Kinetic typography makes text the star. Words, phrases, and letters animate in direct sync with audio — appearing, transforming, and exiting in rhythm with what's being said or sung. Used for lyric videos, motivational quote reels, short-form hooks, and punchy intro sequences. Remotion is ideal for this because frame-accurate timing is built in.

---

## Known Techniques (to be detailed via interview)

- **Word-by-word reveal** — each word animates in as it's spoken in the audio
- **Scale pop** — words scale up or bounce on stressed syllables
- **Color shift** — words change color to match emotional tone or emphasis
- **Typeface mixing** — combining display fonts and body fonts for hierarchy and contrast
- **Stagger animation** — letters or words cascade in with offset delays
- **Background motion** — subtle animated gradient, particle field, or texture behind text
- **Push / wipe transitions** — text slides out as next phrase slides in
- **3D rotation** — words flip or rotate into position (CSS perspective transform)
- **Split text effects** — words split apart and reform for dramatic emphasis
- **Rhythm sync** — animation timing locked to BPM of the music track

---

## Remotion Implementation Notes
*(To be completed — interview required)*

- Word timing data source (transcript JSON? manual?): TBD
- Animation primitives (spring, interpolate, useAudioData?): TBD
- Font choices per mood: TBD
- Background treatment: TBD
- Color palette approach: TBD
- Short-form vs long-form variations: TBD
- useAudioData for beat sync: TBD (Remotion has built-in audio visualization)

---

## Reference Channels
- Lyric video productions (general)
- Gary Vaynerchuk quote reels
- MrBeast intro sequences
- Film title sequences (general reference)
