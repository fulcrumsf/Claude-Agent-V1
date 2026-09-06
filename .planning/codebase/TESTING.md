# Testing

## Framework
Focused modules use Python `unittest` files beside the implementation, for example `test_generation_guard.py`, `test_production_state.py`, and `test_validate_pre_video_gate.py`.

## Existing Coverage
- Generation reservation and retry safety.
- Production checkpoint persistence and append-only decision history.
- Complexity routing decisions.
- End-frame decisions.
- Pre-video reference-role and prompt validation.

## Planned QA Tests
- Schema validation rejects missing frame captions, frame actions, and continuity invariants.
- Candidate attempts stop at exactly three.
- Failed candidates are archived and never reused as active output.
- Vision findings identify missing subjects, wrong object state, impossible transitions, and caption mismatch.
- A passing candidate is the only input allowed to Seedance prompt generation.
- All-failed candidates produce a manual-review flag and no paid video task.

## Verification Style
Use deterministic unit tests for orchestration and mocked vision/provider boundaries. Use a small fixture set containing the Shot 6 failure pattern as a regression case. Keep live paid generation out of automated tests.
