# Phase 1 Context: Storyboard Contract

## Domain Boundary

Define the structured input contract and deterministic prompt layout used to request storyboard sheets. This phase does not implement vision QA, regeneration, or Seedance submission; those are later phases.

## Decisions

### Frame-by-frame specificity
- Every frame must be specified explicitly, in order.
- Each frame description must state the visible subjects, relevant object states, spatial relationships, and the action or state transition represented by that frame.
- The contract must make continuity requirements explicit rather than relying on the model to infer them from a vague summary.

### Captions
- Each frame has an exact caption supplied by the shot specification.
- The storyboard prompt tells the image model to render that caption in the matching panel.
- Caption text is part of the later QA contract, not decorative text that can be ignored.

### Stable prompt layout
- Every storyboard prompt uses the same labeled order: overall summary, visual/camera/style locks, continuity invariants, frame sequence, caption requirements, hard constraints, and output layout.
- The model fills the content fields; it does not choose a different schema or ordering per shot.

### Cost and downstream safety
- This phase should support a maximum of three candidates, but the retry loop belongs to Phase 3.
- A storyboard must be treated as a reference plan only. It must never be silently used as a clean temporal first frame.

### Regression example
- Include a Shot 6 fixture in which frame 1 requires a closed countryside gate with the bear already behind it, frame 2 requires the grandmother approaching while the gate remains closed, and frame 3 requires the grandmother opening the gate toward the bear.
- The fixture must be capable of exposing the prior failure: absent subjects, wrong gate state, and an unexplained state change.

## Agent's Discretion

- JSON field names and serialization details, provided they preserve the decisions above.
- Whether the prompt builder accepts JSON directly or a typed Python mapping at its public boundary.
- Exact caption typography/layout language, provided captions remain exact and panel associations are unambiguous.
- Whether the contract includes optional fields for duration, shot type, or reference assets, provided required continuity fields cannot be omitted.

## Canonical References

- `001_Architecture/Skills/Storyboard-Generation/SKILL.md`
- `001_Architecture/Skills/Neon_Parcel_Longform_Compilation/SKILL.md`
- `001_Architecture/Skills/Seedance-Prompting-Guide/SKILL.md`
- `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/validate_pre_video_gate.py`
- `002_Content-Creation/Video_Editor/002_Channels/002_Neon-Parcel/Productions/0001_Grandma-And-Bear-Compilation/`

## Deferred Ideas

- Calibrating the vision checker against a larger labeled dataset belongs in v2.
- A human editing UI belongs in v2.
- Post-Seedance video QA belongs outside this phase and the current v1 roadmap.

---
*Captured: 2026-08-30 from the storyboard QA design discussion*
