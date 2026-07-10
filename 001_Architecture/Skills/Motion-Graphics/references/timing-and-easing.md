# Timing & Easing Reference

Distilled from `001_Architecture/Skills/refactoring-ui/references/animation-microinteractions.md`
(real UI-motion-design literature already in this workspace) plus this
session's production corrections. For Remotion implementation syntax
(`interpolate`, `spring`, easing functions), see
`001_Architecture/Skills/remotion-best-practices/SKILL.md` → `rules/timing.md`
— this file covers the *judgment*, that one covers the *code*.

## Why animate at all

Valid reasons: draw attention to something that changed, show relationship
between states (this became that), communicate hierarchy/order, make an
interface/graphic feel responsive and alive.

Invalid reasons: because it's easy to add, because everything else has
motion so this should too, decoration with no communicative purpose. If you
can't say what the motion is *telling the viewer*, don't add it.

## Duration guidelines

- Small, local changes (a label settling, a hover-equivalent state change):
  short and snappy — roughly 100-200ms equivalent (~3-6 frames at 30fps).
  Longer than this reads as sluggish for something small.
- Larger movements (an element entering the frame, a scene-level reveal,
  something traveling real distance): duration should scale with the
  distance/size of the change. A big move that happens too fast reads as
  glitchy; a small move that takes too long reads as sluggish. Match
  perceived effort to perceived distance.
- When in doubt, err short. Overly long animations are a more common
  mistake than overly short ones — they make the viewer wait.

## Easing curves — when to use each

- **Ease-out** (fast start, slow finish): default for anything *entering*
  the frame or appearing. Front-loads the perceived speed, settles gently.
  Feels responsive and natural.
- **Ease-in** (slow start, fast finish): default for anything *leaving* the
  frame or disappearing. Builds momentum outward, matches how exits feel.
- **Ease-in-out**: for movement that both starts and ends in place (e.g. a
  camera move that settles on both ends) — smooth acceleration and
  deceleration on both sides.
- **Linear**: avoid for anything meant to feel alive or organic. Correct
  only for genuinely mechanical/constant-rate motion (a literal clock
  hand, a progress bar tracking real elapsed time) — using it elsewhere is
  one of the two most common tells of generic/default motion graphics
  (the other is a flat opacity-only pop-in; see main SKILL.md).
- **Spring/overshoot**: for anything that should feel like it has physical
  weight or should draw the eye at the moment it settles — text pulses,
  playful UI, anything meant to feel "alive" rather than merely functional.
  Prefer a real spring simulation over hand-keyframing a bounce; a spring
  naturally produces the single overshoot-and-settle motion that a manual
  keyframe curve has to fake.

## Leader lines and draw-in animation

Don't render a leader line, arrow, or connecting stroke at full length
instantly — animate its draw progress (stroke length or SVG path progress)
over a short window (~15-25 frames at 30fps), eased out. Pair it with the
label's own reveal so the line and the text land as one coordinated gesture
rather than two separate events competing for attention.

## Accessibility note (carried from the source reference)

Not every viewer wants strong motion. This is less directly applicable to
pre-rendered video than to interactive UI, but the underlying principle
still matters for pacing: avoid motion that's purely disorienting (rapid
flashing, extreme parallax) when it's not communicating something — see
"Invalid reasons" above.
