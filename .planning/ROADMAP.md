# Roadmap: Neon Parcel Storyboard QA

## Overview

We will first lock the storyboard data contract and prompt layout, then build deterministic visual-QA decisioning around a vision adapter, then add the capped regeneration/archive loop, and finally connect the validated artifact to Seedance prompt generation and the pre-video gate. Each phase ends with tests and evidence that the next layer can trust.

## Phases

- [x] **Phase 1: Storyboard Contract** - Define the stable frame-by-frame schema and generation prompt layout.
- [x] **Phase 2: Storyboard QA** - Evaluate candidate sheets for visual continuity, captions, and physics.
- [x] **Phase 3: Capped Regeneration** - Orchestrate checked retries, archiving, and manual-review blocking.
- [x] **Phase 4: Validated Handoff** - Generate Seedance prompts only from passing storyboard evidence and integrate the gate.

## Phase Details

### Phase 1: Storyboard Contract
**Goal**: Every storyboard request has a complete, machine-readable frame specification and a stable prompt template.
**Depends on**: Nothing
**Requirements**: [STORY-01, STORY-02, STORY-03]
**Success Criteria**:
  1. A shot can be serialized with explicit frame-by-frame visual requirements and captions.
  2. The prompt builder emits the same labeled sections and ordering for every shot.
  3. A Shot 6 regression fixture expresses the closed-gate, bear-present, grandmother-continuity requirements unambiguously.
**Plans**: 2 plans

### Phase 2: Storyboard QA
**Goal**: A generated storyboard sheet receives an evidence-backed pass/fail result against its frame contract.
**Depends on**: Phase 1
**Requirements**: [QA-01, QA-02, QA-03]
**Success Criteria**:
  1. The checker can identify missing subjects and incorrect gate/object states in a candidate.
  2. The checker evaluates transitions and physics across adjacent frames, not just isolated panels.
  3. Missing or ambiguous evidence fails closed with actionable findings.
**Plans**: 2 plans

### Phase 3: Capped Regeneration
**Goal**: Failed storyboard candidates are retried safely up to three times, then blocked and flagged.
**Depends on**: Phase 2
**Requirements**: [REGEN-01, REGEN-02, REGEN-03, REGEN-04]
**Success Criteria**:
  1. Candidate two is never requested before candidate one is checked.
  2. The attempt counter hard-stops at three and all artifacts remain traceable.
  3. A three-failure result prevents any Seedance task submission.
**Plans**: 2 plans

### Phase 4: Validated Handoff
**Goal**: Seedance receives only a prompt/reference package backed by a passing storyboard manifest.
**Depends on**: Phase 3
**Requirements**: [HANDOFF-01, HANDOFF-02, HANDOFF-03]
**Success Criteria**:
  1. Seedance prompt generation refuses a missing or failed storyboard manifest.
  2. The generated video prompt reflects the accepted storyboard observations.
  3. Storyboard/reference and clean temporal first-frame roles remain separated.
**Plans**: 2 plans

## Progress

**Execution Order:** Phases 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Storyboard Contract | 2/2 | Complete | 2026-08-30 |
| 2. Storyboard QA | 2/2 | Complete | 2026-08-31 |
| 3. Capped Regeneration | 2/2 | Complete | 2026-08-31 |
| 4. Validated Handoff | 2/2 | Complete | 2026-08-31 |
