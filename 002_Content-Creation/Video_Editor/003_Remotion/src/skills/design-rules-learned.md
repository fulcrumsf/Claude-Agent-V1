# Design Rules Learned

This file is a **growing, additive** record of design judgment corrected or
confirmed by Tony during real production work. It exists because "match the
channel brand sheet" and "match the existing component" are not always
sufficient to produce good styling — some calls require judgment that wasn't
written down anywhere until Tony corrected or confirmed it in a session.

**Rules of this file:**
- Only add an entry after a real, specific correction or confirmation from
  Tony — never speculative "best practices."
- Never delete or rewrite a prior entry to make room for a new one. If a new
  entry narrows or overrides an old one, say so explicitly in the new entry
  and leave the old one in place with a note, rather than silently replacing it.
- Each entry: the general rule, then the concrete example that taught it, so
  future agents can judge edge cases instead of blindly pattern-matching.

---

## Rule 1 — Brand accent colors are for channel chrome, not in-scene content

Documented channel brand colors (logo, thumbnail, lower-thirds, channel UI)
are **not automatically correct** for in-scene diagram/callout graphics layered
over generated illustrations or footage. That illustration/footage isn't
"branded" — it's content. Its own palette should drive callout/label color
choices, not the channel sheet.

**Default when a diagram/callout needs a color and there's no reference to
match:**
1. Sample the actual image (e.g. via PIL) near the callout target and use a
   color pulled from what's actually glowing/highlighted there — don't guess
   a hex value from memory.
2. If the background is black/near-black, default label text to white for
   contrast, unless a supplied reference image shows otherwise.
3. Only reach for a documented brand accent when the graphic *is* channel
   chrome (logo marks, lower-third channel identity, thumbnail overlays).

**Taught by:** Anomalous Wild, Bioluminescence Weapon, esca/bacteria callout
(2026-07-10). First pass defaulted to the channel's neon green `#8AFA47`
(documented as "subject glow, arrow, logo symbol" in
`Anomalos_Wild_Content_system.md`) purely because it was the one accent color
found in existing code (`SceneOverlay.tsx`'s `AnnotationOverlay`). Tony
corrected: that green is for logo/channel chrome, not this image. The image's
own glow, sampled directly from `Fish-01.png`, came back as electric cyan
(`rgb(19,245,251)` / `#13F5FB`) — which also happens to match the *other*
documented brand accent ("Accent Cyan — glitch cuts and anomaly reveals"), so
the fix wasn't "ignore the brand system," it was "pick the right accent for
the right job, and verify against the actual pixels rather than assuming."

**Known open gap, not yet fixed (flagging, not touching without approval):**
`video-components/DiagramLabels.tsx` — the generalized diagram-labeling
component built for the Scientific Diagram sub-pipeline — hardcodes
`LINE_COLOR = "#8AFA47"` (brand green) as a blanket default for every future
labeled diagram across the whole pipeline. Per this rule, that default should
probably become "sample from the source image" rather than a fixed brand
color. Left as-is for now since it's already a locked, shipped part of the
`/anomalous-wild` pipeline — don't change it without asking first.

---

## Rule 2 — Label/text reveals should resolve, not pop; lines should draw, not appear

Any callout label, kinetic text, or diagram annotation that reveals itself
mid-video should combine a **blur-to-sharp resolve with an opacity fade-in**
— not a flat opacity-only pop. The effect should read as the word
materializing/glowing into focus, which is what pulls the eye to it. Leader
lines or arrows pointing to a target should animate their draw progress over
roughly 15–25 frames rather than appearing instantly.

**Taught by:** Anomalous Wild, Bioluminescence Weapon, esca/bacteria callout
(2026-07-10). Tony confirmed this explicitly and unprompted: *"words should
phase in and glow so your eyes are drawn to the words rather than just pop up
and be static."* Implemented as: opacity ramp over frames [4,18], paired with
a `blur()` filter ramp from ~10px to 0px over frames [4,22], plus a
`text-shadow` glow whose opacity settles after the blur resolves. Leader
lines draw over ~20 frames with an eased-out interpolation before the
endpoint glow-pulse triggers.

**How to apply:** treat "pop-in opacity only" as the anti-pattern for any
future callout/label/lower-third work in this pipeline, not just this scene.

**Amendment (2026-07-10):** on top of the blur/opacity resolve above, label
text should also carry a small scale-and-brightness pulse as it settles —
scale springs up past 1.0 (reads momentarily larger/brighter), then eases
back down to resting size/brightness. This is a spring overshoot
(`spring({ from: 0.82, to: 1, config: { damping: 9, stiffness: 140 } })`),
not a manual keyframe bounce — let the spring produce the single
overshoot-and-settle naturally. Implementation note: don't drive a
correlated glow boost by feeding the spring's own output value into
`interpolate()` as the input range — a spring overshoots and returns through
the same values, which breaks `interpolate()`'s strictly-monotonic input
requirement. Drive the glow boost off `frame` instead, timed to land on the
spring's peak, since frame is always monotonic.

---

## Rule 3 — Diagram labels belong in open space off the subject, never on it

For anatomical/scientific diagram callouts: the label text itself should sit
fully off the subject, in open background space — never overlapping the
subject or the highlighted feature it's pointing to. Only a small dot marker
touches the subject; a line runs from that dot out to the label. When there
are multiple labels, anchor them from different directions (e.g. one from
above, one from below) so their lines never cross or bunch into the same
region.

**Taught by:** Anomalous Wild esca/bacteria callout (2026-07-10), directly
corrected against Tony's own reference image (`Fish-02.png`). First pass
computed each label's position as a small fixed pixel offset *from* its
target dot (~200px away), which kept both labels crowded on top of the
glowing subject itself, with their leader lines crossing each other. Fish-02
does the opposite: labels are distributed around the subject's perimeter in
open black space, each line traveling a real distance from dot to label, and
no two lines cross. Fix was to make label position an independent, explicit
anchor point (not a derived offset from the target) chosen for open space,
verified by sampling the actual pixel color at the anchor point to confirm
it's empty background before placing text there.

**How to apply:** when placing 2+ labels on one diagram, do not derive label
position purely from "near its target." Pick anchor points around the
subject's open perimeter first (sample pixels to confirm they're empty
background), distribute multiple labels from different sides/directions of
the subject, then draw each line from anchor to target — matching how a real
printed scientific diagram lays out callouts.

---

## Rule 4 — Leader lines radiating from one cluster must not be parallel to each other

When multiple leader lines originate near the same feature/cluster, each line
needs a distinct angle/slope — not just non-crossing, genuinely non-parallel.
Two lines that both run straight up and straight down (mirrored verticals)
are still a weak composition even though they don't cross; the fix is
radiating angles, e.g. one line up-and-to-the-right, another down-and-to-the-
far-left, so the whole layout reads as a burst rather than a stack.

**Taught by:** Anomalous Wild esca/bacteria callout (2026-07-10), second
correction in the same session after Rule 3 fixed the crossing-lines problem
but produced two near-vertical parallel lines (one straight up, one straight
down) — technically clean but visually flat. Tony's fix: "ESCA line should go
up and to the right... bacteria line should go down into the far left."

**Externally grounded, not just inferred:** confirmed against real
leader-line/label-placement literature — "leaders running close together
should not be parallel," and leader slope should vary with radial ordering
around the cluster (Radial Contour Labeling with Straight Leaders,
[arxiv.org/pdf/1702.01799](https://arxiv.org/pdf/1702.01799); labeling-taxonomy
survey, [arxiv.org/pdf/1902.01454](https://arxiv.org/pdf/1902.01454)). Note:
an earlier search surfaced patent/technical-drawing convention (uniform
parallel callout lines) which is the *wrong* genre for this channel's
Vox/Kurzgesagt-style explainer diagrams — don't apply that convention here;
it directly contradicts Tony's reference image and this rule.

**How to apply:** whenever 2+ leader lines originate from one feature/area,
give each a clearly different angle (radiate outward like spokes), not
mirrored/parallel directions, even if they don't technically cross.

## Rule 5 — Diagram label / callout aesthetic (locked 2026-09-01, Tony-approved on 0003 Glass Frog)

Reference + anti-examples live in
`001_Architecture/Skills/Diagram-Generation/Reference_Examples/`
(`Label_Aesthetic_Red_Blood_Cells.png` is the target; two `Anti_Example_*` sheets
show what to avoid — tiny cramped labels, coloured text with no plate over busy
imagery).

**The label look:**
- Term: large, clean, **bold white** sans-serif. On 0003 the old 20px labels were
  ~1.5–2x too small; the working size is a ~40px base with a `scale` prop.
- A parenthetical qualifier ("(Asleep)", "(awake)") auto-splits onto its own line
  in a **subject-derived accent colour** (e.g. red for blood) — not the channel
  brand green.
- Thin **white** leader line that **draws on** from the feature outward, one
  right-angle bend, small dot at the label end.
- A soft **glowing target ring** at the feature end (bloom, not a hard dot).
- Contrast comes from **size + weight + a black outline/glow** — no backing box on
  the label itself.
- **Collision avoidance:** stacked labels keep a minimum vertical gap; offset the
  text block, never the leader-line target.
- Optional 2–3 line white description under the term.
- `labelHoldS` — each label fades out after its window so the camera can move on.

**Camera under labels (Rule 5b):** the diagram camera holds **completely still**
whenever a label is on screen. Blocking pattern per feature beat:
**ease to feature → settle → label fades in → DEAD STILL for the label window →
label fades out → ease to next feature.** All camera moves ease in and out.
A run of shots on the *same illustration* is ONE shot with ONE continuous eased
path — never separate hard-cut segments of the same image ("remount jump").

**Coloured callout / lower-third over busy imagery (Rule 5c):** gets a
**50%-black backing plate** (`rgba(0,0,0,0.5)`), small even padding, easing
in/out with the text.

**Taught by:** the 0003 Glass Frog edit review (2026-08-31 / 09-01). Full note
trail: `Productions/0003_Glass_Frog_Transparency/Production/Revision_Notes_Round1.md`.

## Rule 6 — Default transition is a ~0.5s cross-dissolve, not a hard cut (locked 2026-09-01, Tony — global)

Every cut (scene boundary AND internal shot change) is a ~0.5s cross-dissolve
unless a hard cut is deliberate (shock cut, match cut, the anomaly-reveal glitch
cut). Mechanics: incoming shot fades in on top; outgoing shot stays fully opaque
underneath (a video clip's tail FREEZES its last frame — extending playback loops
past real footage); never fade both toward the background (it darkens the
dissolve). Narration/VO joins **hard** with a ~3-frame edge fade only. Applies to
every channel — also lock into `Reimagined_Realms_Video_Pipeline` + `assemble.py`.

**Taught by:** 0003 Glass Frog block-A review — Tony: "rather than doing hard cuts
by default the 0.5 cross dissolve works really well ... this should be like a
global thing."
