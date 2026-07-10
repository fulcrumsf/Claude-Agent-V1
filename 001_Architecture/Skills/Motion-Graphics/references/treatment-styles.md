# Treatment Styles — Craft Notes

**Confidence flag, read this first:** everything in this file is general
motion-design craft knowledge about how these treatments are typically
built — it has not been corrected or confirmed by Tony against real
production work the way `design-rules-learned.md`'s rules have. Use it as a
strong starting point when a beat calls for one of these styles, but if
Tony corrects something here, the fix belongs in `design-rules-learned.md`
(cross-reference it from here too), not a silent edit to this file.

The canonical style description, mood, and reference-channel list for each
of these lives in `002_Content-Creation/Video_Editor/.agents/styles/` —
those files are marked `status: placeholder — needs interview to flesh out
implementation details`. This file adds the "how do I actually animate
this well" layer; it doesn't replace those files' ownership of channel
assignment and aesthetic direction.

---

## Kinetic Typography

Text is the only visual — so every choice in *how* the text moves carries
the full communicative weight that footage or illustration would otherwise
carry.

- **Sync to the actual audio, not an estimate.** Word-level timestamps
  (already the pattern in this workspace's TTS pipeline — see
  `ElevenLabs_TTS` word-level output) should drive when each word/phrase
  enters, not a guessed cadence. Kinetic type that's even slightly off
  the spoken rhythm reads as broken immediately, more than almost any other
  motion-graphics mistake.
- **One idea on screen at a time.** Resist the urge to keep multiple past
  phrases lingering — kinetic typography works because the current word IS
  the whole frame. Exit the previous phrase before or as the new one enters.
- **Emphasis through scale/weight/color, not just position.** A stressed
  word can be larger, bolder, or shift color/brightness — matching Rule 2's
  pulse-beat pattern from the main skill (scale springs up, settles down)
  works well here too, timed to the stressed syllable.
- **Vary the entrance, not just the exit.** If every word slides in from
  the same direction, it reads as templated fast. Mix scale-pops, stagger
  reveals, and directional slides across a sequence rather than locking one
  entrance style for the whole piece.
- **Background should support, not compete.** Subtle gradient motion or a
  particle field is fine; anything with hard edges or bright detail behind
  fast-moving text fights for attention it shouldn't win.

## Vox Documentary (2D essay/collage style)

Blends real archival assets (photos, maps, documents) with flat graphic
design — dense, layered, essay-like.

- **The zoom-in is doing narrative work, not just filling time.** A push
  into a document/photo should land on the specific detail the narration
  is currently naming — treat it like a callout target, not a generic
  Ken Burns effect. If the narration doesn't name a specific detail in that
  moment, the zoom doesn't need to happen.
- **Paper-cutout/collage elements should have real depth cues** — subtle
  drop shadows, slight parallax between layers as the camera moves — even
  though everything is flat 2D. Depth is what separates "collage" from
  "flat sticker slapped on a background."
   - **Map reveals draw progressively**, same principle as leader lines in
  the main skill: borders/regions fill in over a real duration, not
  instantly, and directional arrows should animate their own draw-in.
- **Split-screen/before-after comparisons need a clear sync point** — both
  sides should change state at the same narrated beat, not staggered
  arbitrarily, or the comparison itself becomes unclear.

## Kurzgesagt Animated (flat vector explainer)

Fully illustrated, no real footage — flat vector characters, bold
iconography, information-dense but approachable.

- **Icons animate with purpose tied to the concept, not just for polish.**
  An icon representing a process should move the way that process actually
  works (e.g. a cycle icon rotates continuously if the concept is cyclical,
  a growth icon scales upward if the concept is growth) — motion as another
  channel of meaning, not decoration.
- **Scale reveals (zooming from human scale to cosmic scale or back) need
  intermediate anchors**, not one continuous zoom — pause briefly at a
  recognizable intermediate scale (e.g. Earth, solar system) so the viewer's
  sense of scale doesn't get lost between the start and end points.
- **Character rigs stay simple and readable at small size** — this style's
  whole visual language depends on characters reading instantly even when
  small in frame; avoid fine detail that only resolves at full-screen size.
- **Consistent, limited palette per scene** — matches the main skill's
  color-judgment rule: don't reach for a brand accent by default, build the
  palette from the scene's own established warm/cool base + one or two
  accent pops, consistent across the whole explainer, not per-element.
- **Particle/spark effects mark transitions, not steady-state.** Use them
  at cuts, emphasis beats, or reveals — a screen with constant particle
  motion in the background stops reading as emphasis at all.
