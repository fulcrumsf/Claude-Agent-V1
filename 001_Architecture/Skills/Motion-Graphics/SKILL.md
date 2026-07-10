---
name: Motion-Graphics
description: Use whenever building, reviewing, or planning ANY motion graphic — animated diagram/callout labels, kinetic typography, chart/data reveals, title cards, lower-thirds, or any Remotion-based animated visual sequence. Trigger this even when the user doesn't say "motion graphics" explicitly — phrases like "add labels to this image," "animate this text," "make this diagram," "build a title card," "the callouts feel flat/cluttered/crossing," or "make it pop" all mean this skill applies. Encodes composition principles, reveal/timing craft, color judgment, and channel treatment styles so animation reads as intentional and professional instead of generic AI-default motion. This is the "why/what good looks like" companion to remotion-best-practices (which covers "how to code it").
metadata:
  tags: motion-graphics, composition, animation, remotion, design, callouts, kinetic-typography
---

# Motion Graphics

This skill exists so design judgment doesn't have to be re-explained every
session. It was built from a real production correction cycle (Anomalous
Wild, Bioluminescence Weapon, esca/bacteria callout, 2026-07-10) plus
external design literature — not from guessing at what "good" means.

## How to use this skill — authority order matters

Not everything below carries the same weight. When sources conflict, higher
wins:

1. **`002_Content-Creation/Video_Editor/003_Remotion/src/skills/design-rules-learned.md`**
   — the living, growing ledger of rules actually corrected or confirmed by
   Tony on real production work. This is ground truth. Read it before any
   diagram/callout/label work specifically. It's also wired into the
   Remotion app's own AI skill-detection system, so it's checked
   automatically for prompt-driven graphics too. **Add to it, in that file,
   whenever you get a new correction or confirmation — don't let new
   lessons pile up only in this skill.**
2. **Composition Principles and Reveal & Timing Craft below** — general
   motion-design principles, either cited from real external sources or
   generalized from the design-rules-learned corrections. Solid defaults
   when no specific correction exists yet.
3. **`references/treatment-styles.md`** (Kinetic Typography / Vox
   Documentary / Kurzgesagt Animated) — aesthetic direction for named
   channel styles. This is craft knowledge about what these treatments
   generally look like, not yet validated against Tony's own corrections
   the way design-rules-learned.md is. Treat it as a strong starting point,
   not a locked rule — flag it as such if you're not sure it fits.

If you build something and get corrected, the fix belongs in
design-rules-learned.md (or this skill, for a principle general enough to
outlive one project) — not just in your own memory of the conversation.

---

## Composition Principles

**One focal read at a time.** A viewer's eye can follow one thing per beat.
If two labels/callouts/elements compete for attention simultaneously, stagger
their entrances rather than revealing them together — unless the whole point
is a simultaneous group reveal (e.g. a stat grid).

**Diagram labels live in open space, on the subject only as a dot.** Never
let label text overlap the subject or the feature it's describing — only a
small marker touches the subject, the label itself sits in open background.
Verify "open" by sampling the actual pixel color at the intended anchor
point rather than eyeballing it — confirms there's nothing there before
committing to the layout.
*(Full case: design-rules-learned.md Rule 3.)*

**Leader lines radiating from one area must not be parallel to each other.**
Two lines that don't cross but both run straight up/straight down (mirrored
verticals) still read as a flat, boring composition. Real radial-labeling
design varies the slope of each leader — give each line a genuinely
different angle so the layout reads as a burst, not a stack.
*(Full case + external citations: design-rules-learned.md Rule 4.)*

**Color belongs to content, not just to the brand sheet.** A documented
brand accent color is correct for actual channel chrome — logo, thumbnail,
lower-third identity. It is not automatically correct for a diagram or
callout laid over generated illustration/footage content, because that
content isn't "branded." Default: sample the actual image near the target
point and derive color from what's really there; default label text to
white on black/dark backgrounds for contrast when no reference exists.
*(Full case: design-rules-learned.md Rule 1.)*

**Avoid symmetry unless the content is genuinely symmetric.** Mirrored,
centered, evenly-spaced layouts read as templated. Real designed
compositions favor deliberate asymmetry — off-center focal points, varied
spacing, elements that don't line up on a grid just because it's easier to
code that way.

---

## Reveal & Timing Craft

**Materialize, don't pop.** A flat `opacity: 0 → 1` cut is the single most
common tell of generic/lazy motion graphics. Every meaningful reveal
(label, callout, title, stat) should combine at least two of: opacity
fade, blur-to-sharp resolve, scale, or position drift. The element should
look like it's *arriving*, not switching on.

**The pulse beat.** For text/labels that need to draw the eye at the exact
moment they appear: scale springs up past 1.0 (briefly reads larger and
brighter), then eases back down to resting size/brightness. This is a
spring overshoot, not a manual keyframe bounce — e.g. in Remotion,
`spring({ from: 0.82, to: 1, config: { damping: 9, stiffness: 140 } })` and
let the spring produce the single overshoot-and-settle naturally.
Implementation gotcha: don't feed a spring's own output back into
`interpolate()` as an input range for a correlated effect (like a glow
boost) — a spring overshoots and passes back through the same values on
the way down, which breaks `interpolate()`'s strictly-monotonic input
requirement. Drive correlated effects off `frame` instead, timed to land on
the spring's peak.
*(Full case: design-rules-learned.md Rule 2 + amendment.)*

**Duration and easing are not arbitrary.** Distilled from real UI-motion
literature (full detail: `references/timing-and-easing.md`):
- Small/local changes (hover states, small reveals): ~100-200ms equivalent
  (~3-6 frames at 30fps) — fast enough to feel responsive, not sluggish.
- Larger movements (element entrances, scene-level reveals): longer
  duration scales with distance/size traveled — a bigger move earns more
  time, a small move should stay snappy.
- Ease-out (fast start, slow finish) is the default for anything entering
  the frame — it front-loads perceived speed and lets it settle gently,
  which reads as more natural than linear or ease-in.
- Ease-in is for things *leaving* the frame — starts slow, accelerates out,
  matching how things build momentum as they exit.
- Avoid linear timing for anything meant to feel alive — it's the other
  major tell of default/generic motion, alongside flat opacity pops.

**Leader lines draw, they don't appear.** Animate the line's draw progress
(e.g. over ~15-25 frames, eased out) rather than rendering it instantly at
full length. Combine with the pulse/materialize beat on the label so the
line and the word land as one coordinated gesture, not two disconnected
events.

---

## Terminology (so you can plan and discuss precisely)

- **Leader line** — the line connecting a callout label to the feature it describes.
- **Radial layout** — multiple labels/leader lines arranged around a central subject, each at a distinct angle, like spokes.
- **Ease-out / ease-in / ease-in-out** — easing curve families; see `references/timing-and-easing.md` for when to use each.
- **Spring overshoot** — a physics-based animation that passes its target value before settling back, producing a natural "bounce" or "pulse" feel (as opposed to a manually keyframed bounce).
- **Stagger** — offsetting the start time of multiple similar elements (e.g. words, list items) so they enter in sequence rather than simultaneously.
- **Kinetic typography** — text itself as the primary animated visual, timed to speech/music rather than illustrating something else.
- **Whip pan** — a fast, blurred camera-style pan used as a transition, common in Vox/Kurzgesagt-style explainers.
- **Parallax** — foreground and background elements moving at different rates to imply depth.
- **Materialize vs. pop** — see Reveal & Timing Craft above; "pop" (flat opacity cut) is the anti-pattern, "materialize" (blur/scale/position combined with opacity) is the target.

---

## Treatment Styles (channel aesthetics)

For Kinetic Typography, Vox Documentary, and Kurzgesagt Animated treatment
craft — technique notes beyond the placeholder stubs in
`002_Content-Creation/Video_Editor/.agents/styles/` — see
`references/treatment-styles.md`. Those channel-style files still own the
canonical description/reference-channel list; this skill's reference file
adds the "how do I actually animate this well" layer on top and is flagged
by confidence level throughout.
