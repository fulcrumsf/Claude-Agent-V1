# Phase 4 Summary: Validated Handoff

## Completed

- Added `storyboard_handoff.py` with a hash-checked selected storyboard manifest validator and a Seedance prompt adapter.
- Required selected attempt identity, `status == pass`, active storyboard path, contract/QA artifacts, storyboard reference URL, and explicit reference role.
- Derived the Seedance prompt from the validated frame sequence while preserving the existing five-section order: camera lock, scene continuity, action timeline, audio, hard constraints.
- Added chronological physical beats with cause and observable result, including the Shot 6 gate sequence.
- Extended the pre-video gate so the Mini storyboard route requires a valid selected-pass handoff manifest and matching reference URL.
- Preserved the existing storyboard/reference versus clean first-frame separation.
- Added regression tests for failed/manual-review/unselected handoffs, hash mismatch, prompt order, missing manifest, reference mismatch, and role confusion.
- Updated Neon Parcel and shared Seedance guidance with the complete contract -> QA -> capped retries -> validated handoff -> pre-video gate -> Seedance order.

## Verification

- Neon Parcel suite: 51 tests passed.
- Generic Kie wrapper tests: 5 passed.
- Python compilation: passed.
- `git diff --check`: passed.
- No provider or paid generation calls were made.

## Project Outcome

The four-phase storyboard-QA workflow is implemented locally. A future storyboard-route shot must now have an explicit contract, a checked candidate, a capped attempt history, and a selected passing handoff before Seedance can be submitted.

## Note

The repository Git index remains read-only in this session, so GSD commits could not be created. Files are present and locally verified.
