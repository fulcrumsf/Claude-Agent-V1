---
name: diagram-generation
description: Use whenever a video production needs a labeled scientific/technical diagram — "build a diagram", "generate a scientific illustration", "animate this diagram", or any beat comparing/explaining anatomy, mechanisms, or data that needs a reference-grounded illustration plus a camera/reveal animation plan. Covers both the base illustration (reference-first, no baked text) and animating it dynamically instead of leaving it static. Channel-agnostic — built on Anomalous Wild's Scientific Diagram sub-pipeline but not specific to it.
---

# Diagram Generation

Builds a labeled scientific/technical diagram and a plan for animating it — never a static, unmoving image. Two separate jobs: (1) the base illustration, reference-grounded and text-free, and (2) how it moves/reveals over time, synced to real narration timing.

**Do not let a diagram sit static.** A locked-2026-08-16 finding from real production testing: a static diagram with only label pop-ins reads flat next to high-end science-documentary references. Every diagram beat needs a real camera/reveal plan, not just entrance animations on the labels.

## Before using this skill

Read [`GPT-Image-2-Prompting-Guide`](../GPT-Image-2-Prompting-Guide/SKILL.md) for base model conventions. Read [`Storyboard-Generation`](../Storyboard-Generation/SKILL.md) — this skill's animation-planning step reuses that skill's template and frame-count logic, applied to a diagram instead of a live-action scene.

## Step 1 — Reference-grounded base illustration (existing, reusable)

Never invent anatomy/mechanism from nothing. Search Openverse for a real reference image first, then generate a clean, label-free illustration with an explicit no-text/no-label/no-callout negative prompt. Existing implementation: `diagram_research_and_illustrate.py` (currently in Anomalous Wild's tool folder, but the technique is channel-agnostic — any channel with a diagram beat should follow this same reference-first pattern).

## Step 2 — Decide: one call, or component assets first?

**This is a judgment call per diagram, not a fixed rule — think about which approach actually gets the best output before generating anything.**

**Approach A — single-call blocking plan** (what Scene_02's test used): generate one base illustration containing everything, then plan a camera/reveal animation across it in one storyboard call. Good when the diagram is a small number of related elements that don't need independent reuse or heavy per-element control (e.g. a 4-quadrant comparison illustration).

**Approach B — component assets first, then assemble.** **The actual asset-isolation + Remotion-compositing mechanics for this approach now live in [`Motion-Graphics-Compositing`](../Motion-Graphics-Compositing/SKILL.md) — invoke that skill once Approach B is decided; this section only covers the decision of when to use it.** Generate each distinct element as its own clean, isolated reference asset first (the same way a character sheet locks a creature's identity) — e.g. a "mantis eye asset," a "human eye asset," a "receptor fan asset" — then either (a) composite them directly in Remotion with keyframed opacity/scale/position (confirmed working, Tony-graded "A+" on Scene 02 — the now-default approach for animating the diagram itself), or (b) feed them into a single storyboard/diagram generation call as labeled references (`@Image1`, `@Image2`, etc.) if a static multi-element illustration is what's actually needed, not an animated one. Use component assets when:
- The diagram has multiple genuinely distinct sub-elements that benefit from independent control
- A component will be reused across multiple scenes/diagrams in the same production (generate once, reference many times, instead of regenerating it fresh each time)
- A single-call generation is struggling to keep a specific element consistent across frames

**Why this matters for consistency:** a storyboard's frames are the actual blueprint for how the animation flows. Consistency comes from what gets fed into that generation as a locked reference — the same mechanism a character sheet uses to keep a creature's identity fixed across shots applies here to any asset (a diagram component, a labeled sub-illustration, anything). If Approach A's single call can't hold a component steady, that's the signal to switch to Approach B and lock that component down as its own asset first.

## Step 3 — Animation planning (reuses Storyboard-Generation's template)

Frame count and prompt structure come from [`Storyboard-Generation`](../Storyboard-Generation/SKILL.md) — same `compute_frame_count()` formula (scene duration ÷ 1.25, clamped 6-12), same Scene/Visual-style/Sequence/consistency-directive prompt blocks. The difference from a live-footage storyboard: **frames describe camera framing and region brightness/reveal state, not new content.** The underlying diagram content must read as the same illustration in every frame — only what's in focus/highlighted vs. dimmed changes.

**Tie reveal timing to real narration, not guesses.** Pull actual word-level timestamps from the scene's `*_beat_sheet.json` and map each frame's reveal/camera-focus window to what's actually being said at that moment — confirmed working on Scene_02 (human eye content revealed 0.0-7.0s matching "Human eyes carry three kinds of color receptor... built from those three," mantis shrimp content revealed 7.5-10.5s matching "The mantis shrimp carries up to sixteen").

**This storyboard is a planning mockup, not the final asset.** The AI-generated storyboard preview may re-render the diagram content slightly differently frame to frame (even when told not to) — real production implementation must crop/mask/zoom the one actual base illustration file in Remotion, driven by the same real timestamps, so the science stays pixel-identical and never drifts. Never let the AI-regenerated preview become the thing that actually ships.

## Other animation techniques worth considering (not exhaustive — think about what fits)

Beyond camera-push-in-with-dimming, other legitimate techniques for a given diagram:
- **Sequential fade-in, no camera movement** — whole composition stays framed the same, individual labeled elements fade in opacity 0→100% in narration order
- **Exploded-view assembly** — parts start separated and animate into their final position as narration proceeds
- **Line-draw/vector-trace reveal** — labels and outlines animate as if hand-drawn in real time (whiteboard-explainer style)
- **Side-by-side synchronized comparison** — two elements stay framed together the whole time, with a synced visual event (a pulse, a counter) animating across both at once to emphasize contrast directly

Pick per-diagram based on what the content is actually trying to communicate — comparison, structure, mechanism, or sequence each suit a different technique.

## Steps 4-5 — Label detection and placement (existing, unchanged)

Gemini vision detects real label coordinates on the actual generated illustration (never a template guess); Remotion's `DiagramLabels` component places labels/callouts on top at render time, staggered per the animation plan from Step 3. See Anomalous Wild's Phase 6B for the existing implementation — `detect_label_coordinates.py` and `DiagramLabels.tsx`.

## Composing with other skills

Don't limit this to one method. Depending on the diagram, pull in whichever of these actually helps:
- [`Character-Sheet-Generation`](../Character-Sheet-Generation/SKILL.md) — if the diagram is illustrating a specific already-sheeted creature's anatomy
- [`Environment-Sheet-Generation`](../Environment-Sheet-Generation/SKILL.md) — if the diagram needs a consistent background/setting reused across scenes
- [`Storyboard-Generation`](../Storyboard-Generation/SKILL.md) — the animation-planning template this skill builds on
- [`GPT-Image-2-Prompting-Guide`](../GPT-Image-2-Prompting-Guide/SKILL.md) — base model conventions for any of the above
