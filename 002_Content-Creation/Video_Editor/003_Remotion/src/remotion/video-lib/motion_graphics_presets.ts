import { interpolate } from "remotion";

// ─── motion_graphics_presets ───────────────────────────────────────────────
// Reusable building blocks for the Motion-Graphics-Compositing skill
// (001_Architecture/Skills/Motion-Graphics-Compositing/SKILL.md).
//
// NOT a one-size-fits-all compositor — every production's motion graphic is
// custom (different assets, different pacing, different beat count). What's
// reusable is the keyframe math itself: each preset below is a small pure
// function a production's own composition (a hand-written .tsx file, same
// pattern as Scene02DiagramTest.tsx) imports and composes as needed, rather
// than re-deriving the same interpolate() calls from scratch every time.
//
// Extracted 2026-08-18 from Scene02DiagramTest.tsx, the first real
// production use of this pattern (Anomalous Wild, Scene 02 diagram
// animation — Tony-graded "A+" against the Seedance video-gen alternative,
// which hallucinated on the same beat).

/** Keyframe helper — pairs of [frame, value], monotonic, clamped at both ends. */
export const kf = (frame: number, points: [number, number][]): number =>
  interpolate(
    frame,
    points.map((p) => p[0]),
    points.map((p) => p[1]),
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

/** Opacity handoff between two layers — one fades out exactly as the other fades in. */
export const crossfade = (
  frame: number,
  fromFrame: number,
  toFrame: number
): { outgoing: number; incoming: number } => ({
  outgoing: kf(frame, [[fromFrame, 1], [toFrame, 0]]),
  incoming: kf(frame, [[fromFrame, 0], [toFrame, 1]]),
});

/** Continuous scale-up "camera push-in" over a frame range. */
export const pushZoom = (
  frame: number,
  startFrame: number,
  endFrame: number,
  fromScale = 1.0,
  toScale = 1.2
): number => kf(frame, [[startFrame, fromScale], [endFrame, toScale]]);

/** Scale-down + reposition to reveal surrounding context (inverse of pushZoom). */
export const pullBackReveal = (
  frame: number,
  startFrame: number,
  endFrame: number,
  fromScale = 1.2,
  toScale = 1.0
): number => kf(frame, [[startFrame, fromScale], [endFrame, toScale]]);

/** Two elements held at fixed offset positions for a side-by-side comparison beat. */
export const sideBySideHold = (
  frame: number,
  startFrame: number,
  settleFrame: number,
  leftOffsetPct: number,
  rightOffsetPct: number
): { leftTranslateXPct: number; rightTranslateXPct: number } => ({
  leftTranslateXPct: kf(frame, [[startFrame, leftOffsetPct], [settleFrame, 0]]),
  rightTranslateXPct: kf(frame, [[startFrame, rightOffsetPct], [settleFrame, 0]]),
});

/** Parts animate from a separated offset into their final assembled position. */
export const explodedAssembly = (
  frame: number,
  startFrame: number,
  endFrame: number,
  fromOffsetPct: number,
  toOffsetPct = 0
): number => kf(frame, [[startFrame, fromOffsetPct], [endFrame, toOffsetPct]]);

/**
 * STUB — not implemented. Whiteboard-style vector-trace reveal (labels/outlines
 * animate as if hand-drawn in real time). Needs its own research/reference pass
 * before real implementation — see Diagram-Generation SKILL.md's "Other animation
 * techniques" list and 2026-08-18-Motion-Graphics-Compositing-Skill-Spec.md, Section 9.
 */
export const lineTraceReveal = (
  _frame: number,
  _startFrame: number,
  _endFrame: number
): never => {
  throw new Error(
    "lineTraceReveal is not yet implemented — needs a research pass on vector-trace/whiteboard-reveal techniques before building. See Motion-Graphics-Compositing skill spec, Section 9."
  );
};
