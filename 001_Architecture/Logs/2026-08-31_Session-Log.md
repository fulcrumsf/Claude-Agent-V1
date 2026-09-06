# 2026-08-31 Session Log

## Full black-frame scan of GlassFrogDoc (Tony's requested pre-commit step)

Rendered the whole composition 4x at half-scale, scanned every frame with ffmpeg blackdetect.

Real bugs found + fixed:
- DiagramCamera used a raw `<img>` — Remotion doesn't block on it, so every diagram
  segment boundary flashed navy for 1–3 frames while the new illustration decoded.
  Changed to Remotion `<Img>`.
- renderDiagramChain summed seconds then rounded → 1-frame navy gaps at segment
  boundaries. Now computes spans in whole frames.
- Main composition summed AUDIO seconds then rounded for scene starts → 1-frame
  gaps at scene cuts. New SCENE_FRAMES accumulator works in whole frames.
- scene_02's 02B sub-sequence ended 1 frame short of the scene → navy frame at
  the 02→03 cut. Now runs to the exact scene frame count.

Result: `blackdetect pix_th=0.03` (near-pure-black) reports NOTHING across the
whole 232s composition.

Two items left for Tony's judgement (not bugs — legitimately dark content):
- scene_04 RangeMapAnimation: 5.2s of a thin green zigzag line on near-black.
  Renders fine but visually weak / reads close to a dark screen.
- scene_07 open: 0.47s dark cinematic shot of a glowing creature emerging from
  black — intentional mood.

## Neon Parcel Storyboard QA Pause Point

Tony asked to pause and preserve the complete next-step context for tomorrow.
The local storyboard-QA architecture is implemented and verified, but live
provider wiring is not complete. The exact resume handoff is recorded at
`.planning/RESUME-2026-08-31-STORYBOARD-QA.md`.

Next action is a no-generation dry run against the existing Shot 6 storyboard
v1. It must use the structured Shot 6 contract and confirm the evaluator can
catch missing subjects, incorrect gate state, broken chronology, and
implausible physics before any replacement generation. No provider or paid
generation call was made during this pause-point work.
