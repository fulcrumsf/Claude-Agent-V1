---
title: "Motion Graphics Design Principles — Composition, Reveal Craft, and the Self-Improving Design Ledger"
type: wiki
category: video-production
tags:
  - video-production
  - motion-graphics
  - remotion
  - design
  - anomalous-wild
created: 2026-07-10
source:
  - [[../../001_Architecture/Skills/Motion-Graphics/SKILL.md]]
  - [[../../002_Content-Creation/Video_Editor/003_Remotion/src/skills/design-rules-learned.md]]
  - [[../../002_Content-Creation/Video_Editor/003_Remotion/src/remotion/video-components/EscaBacteriaCallout.tsx]]
---

# Motion Graphics Design Principles

## What this is

Before 2026-07-10, motion-graphics *composition/taste* (as opposed to
Remotion *API* knowledge, which `remotion-best-practices` already covered
well) didn't really exist anywhere in Agent-OS as durable, checkable
knowledge. The channel style docs
(`002_Content-Creation/Video_Editor/.agents/styles/{Kinetic-Typography,
Vox-Documentary,Kurzgesagt-Animated}.md`) were — and still are — literally
marked `status: placeholder`. Design judgment lived only in whatever an
agent happened to infer in the moment, which meant Tony had to re-explain
the same corrections repeatedly.

Two things now exist to fix that:

1. **`design-rules-learned.md`** (`002_Content-Creation/Video_Editor/003_Remotion/src/skills/`)
   — a growing, additive, dated ledger of rules actually corrected or
   confirmed by Tony on real production work. This is the ground-truth
   layer. It's also wired directly into the Remotion app's own AI
   skill-detection system (`003_Remotion/src/skills/index.ts`), so
   prompt-driven motion-graphics generation picks it up automatically.
2. **`Motion-Graphics` skill** (`001_Architecture/Skills/Motion-Graphics/`)
   — the general-principles companion skill, triggered on any
   motion-graphics/callout/kinetic-typography/title-card task. It
   explicitly defers to `design-rules-learned.md` as higher-authority than
   its own general content, and separates proven rules from general craft
   knowledge from unvalidated aesthetic direction (its own
   `references/treatment-styles.md`) rather than presenting all three with
   equal confidence.

## How the ledger got built (case study)

Source production: Anomalous Wild, Bioluminescence Weapon, esca/bacteria
callout insert clip (~2:32 in the finished video) — see
`EscaBacteriaCallout.tsx` and rendered output at
`002_Content-Creation/Video_Editor/002_Channels/001_Anomalous-Wild/Productions/0001_Bioluminescence_Weapon/Motion-Graphics/esca-bacteria-callout/`.
The original version of this beat used an image model to bake labels
directly into the image — the documented "gibberish diagram text" failure
mode already known from the Anomalous Wild pipeline build (see
[[Anomalous-Wild-Pipeline-Scripts]]). Rebuilding it correctly as a Remotion
overlay surfaced four real, generalizable corrections in one session:

1. **Color belongs to content, not the brand sheet by default.** First pass
   reused the channel's brand-green accent purely because it was the one
   color already present in nearby code. Corrected: sample the actual
   image for color; reserve brand accents for real channel chrome (logo,
   thumbnail, lower-thirds).
2. **Diagram labels belong in open space off the subject**, connected by a
   line to a small dot marker — never overlapping the subject itself.
   First pass computed label position as a fixed offset from the target,
   which kept labels crowded on the glowing subject.
3. **Leader lines radiating from one area must not be parallel to each
   other**, even if they don't cross. Confirmed against real leader-line
   placement literature (radial contour labeling research), not just
   inferred — see citations in `design-rules-learned.md` Rule 4.
4. **Label reveals should materialize** — blur-to-sharp resolve plus a
   spring-overshoot scale/brightness pulse — never a flat opacity pop.

Each correction was applied, re-rendered, and verified with an actual frame
grab before being written into `design-rules-learned.md` — the ledger only
grows from real corrections, not speculative best practices.

## Known open gap (flagged, not fixed)

`DiagramLabels.tsx` — the shared component from the Scientific Diagram
sub-pipeline used by the live `/anomalous-wild` orchestrator — still
hardcodes brand green as its default line/label color, which is exactly
the anti-pattern Rule 1 above corrects. Left alone intentionally (it's
shipped, locked pipeline code); flagged in both `design-rules-learned.md`
and `Anomalous_Wild_Video_Pipeline/SKILL.md` for a future session to fix
with explicit sign-off.

## Where to look next

- Full rule ledger with citations: `design-rules-learned.md`
- Composition/terminology/timing principles: `Motion-Graphics/SKILL.md`
- Treatment-style craft notes (Kinetic Typography, Vox, Kurzgesagt):
  `Motion-Graphics/references/treatment-styles.md`
- Timing/easing judgment: `Motion-Graphics/references/timing-and-easing.md`
