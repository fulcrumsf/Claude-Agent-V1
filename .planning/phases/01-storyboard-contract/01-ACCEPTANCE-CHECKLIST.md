# Storyboard QA Acceptance Checklist

Phase 2 uses this checklist against each generated storyboard candidate.

## Per-Frame Checks

- [ ] Frame number and panel order match the structured specification.
- [ ] Required subjects are visible in the declared count.
- [ ] No undeclared subject appears.
- [ ] Required object states match the declared state.
- [ ] Spatial relationships match the declared arrangement.
- [ ] The panel shows the declared action/state, not a later or earlier state.
- [ ] The caption text matches the exact frame caption.

## Adjacent-Frame Checks

- [ ] Any subject entering or leaving has a declared causal transition.
- [ ] Object state changes occur only in the frame where the action causes them.
- [ ] Camera viewpoint and fixed geometry remain consistent.
- [ ] Movement is physically plausible and does not teleport, duplicate, or morph.
- [ ] The sequence remains chronological and does not reverse an established state without an action.

## Decision Rules

- Schema validation is deterministic and runs before image generation.
- Image presence, state, action, caption, and physics checks require vision evidence.
- Missing or ambiguous visual evidence is a failure/manual-review result, never an automatic pass.
- A candidate passes only when all required checks pass; later phases enforce the three-candidate cap.
