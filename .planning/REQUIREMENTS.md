# Requirements: Neon Parcel Storyboard QA

**Defined:** 2026-08-30
**Core Value:** Seedance must receive a storyboard that is visually and logically consistent with the intended shot.

## v1 Requirements

### Storyboard Contract

- [x] **STORY-01**: The pipeline can represent each shot with an overall summary, camera/style locks, continuity invariants, and an ordered list of explicit frame specifications.
- [x] **STORY-02**: Each frame specification includes visible subjects, object states, spatial relationships, action transition, and the exact caption text to render.
- [x] **STORY-03**: The pipeline produces the same stable prompt layout for every storyboard candidate instead of inventing a new structure per shot.

### Visual QA

- [x] **QA-01**: The checker compares the generated storyboard image against the structured frame requirements.
- [x] **QA-02**: The checker reports missing/unexpected subjects, incorrect object states, broken action continuity, caption mismatch, and physically implausible transitions.
- [x] **QA-03**: Ambiguous visual evidence fails closed and routes to review rather than being treated as a pass.

### Controlled Regeneration

- [x] **REGEN-01**: The pipeline checks candidate one before requesting candidate two.
- [x] **REGEN-02**: The pipeline permits no more than three storyboard candidates for a shot and records each attempt.
- [x] **REGEN-03**: After three failed candidates, the shot is flagged and Seedance submission is blocked.
- [x] **REGEN-04**: A failed candidate and its prompt/QA evidence are preserved in the production archive.

### Downstream Handoff

- [x] **HANDOFF-01**: Seedance prompt generation requires a passing storyboard manifest.
- [x] **HANDOFF-02**: The Seedance prompt is derived from the validated storyboard observations and preserves the original shot intent only where it does not contradict the accepted visual evidence.
- [x] **HANDOFF-03**: Storyboard references remain distinct from clean first-frame assets.

## v2 Requirements

### Quality Improvements

- **QUAL-01**: Calibrate the checker against a larger labeled set of accepted and rejected storyboard sheets.
- **QUAL-02**: Add a human correction interface for editing frame requirements before retrying.
- **QUAL-03**: Add provider/model-specific QA thresholds and cost telemetry.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Fully automatic approval of borderline images | Ambiguity is a safety signal and should be reviewed by a human |
| New image/video providers | Existing wrappers and routing are sufficient for v1 |
| Video QA after Seedance generation | Valuable later, but this project first prevents bad storyboard inputs |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| STORY-01 | Phase 1 | Pending |
| STORY-02 | Phase 1 | Pending |
| STORY-03 | Phase 1 | Pending |
| QA-01 | Phase 2 | Pending |
| QA-02 | Phase 2 | Pending |
| QA-03 | Phase 2 | Pending |
| REGEN-01 | Phase 3 | Pending |
| REGEN-02 | Phase 3 | Pending |
| REGEN-03 | Phase 3 | Pending |
| REGEN-04 | Phase 3 | Pending |
| HANDOFF-01 | Phase 4 | Pending |
| HANDOFF-02 | Phase 4 | Pending |
| HANDOFF-03 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 13 total
- Mapped to phases: 13
- Unmapped: 0

---
*Requirements defined: 2026-08-30*
*Last updated: 2026-08-31 after Phase 4 completion*
