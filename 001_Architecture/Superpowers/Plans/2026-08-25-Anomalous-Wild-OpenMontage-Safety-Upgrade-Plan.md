# Anomalous Wild Pipeline — OpenMontage-Inspired Safety Upgrade Plan

> **Handoff prompt for Claude Code:** Read this entire Markdown file first. Treat the existing Anomalous Wild pipeline as protected production infrastructure. Enter superpower planning mode, inspect the repository and current git state, interview Tony at the decision gates in this document, and produce a detailed implementation plan before changing code. Do not implement anything until Tony approves the plan. Do not delete, rename, or silently change existing production behavior.

## Objective

Add the most useful OpenMontage architecture patterns to the Anomalous Wild video pipeline without damaging the parts that already work and without forcing a wholesale rewrite.

The goal is to improve reliability, resumability, prompt consistency, visual variety, cost control, and auditability while preserving the current creative behavior:

- Per-beat Tool-Manager routing
- Scientific reference grounding
- Character/reference-sheet continuity
- Diagram safety and no-guessing behavior
- Word-level narration timestamps
- Existing batch generation and retry behavior
- Tony's explicit approval pauses
- Existing production folder structure
- Existing working scripts, even when they are later wrapped by new contracts

## Protected System

Treat these as production-critical until proven otherwise:

- `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/SKILL.md`
- `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/Pipeline_Improvements_TODO.md`
- `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/`
- `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Generic_Tools/`
- `/Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/002_Channels/001_Anomalous-Wild/Productions/`
- `/Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/003_Remotion/`

Before planning implementation, read:

- `001_Architecture/Install_Maps/Workspace-Map.md`
- `001_Architecture/Install_Maps/System-Map.md`
- `001_Architecture/Memory/Core_Memory.md`
- `001_Architecture/Memory/Memory_Index.md`
- `001_Architecture/Skills/Skill-Index.md`
- `001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/SKILL.md`
- `001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/Pipeline_Improvements_TODO.md`
- `000_Wiki/Video-Production/Anomalous-Wild-Pipeline-Scripts.md`
- The active tests under the Anomalous Wild tool directory

Also inspect `git status`, recent commits, ignored files, and any uncommitted changes before proposing edits.

## Non-Destructive Rules

1. Do not delete or overwrite existing production artifacts.
2. Do not rewrite the pipeline from scratch.
3. Do not remove existing scripts because OpenMontage uses a different philosophy.
4. Do not silently change model defaults, providers, renderers, prompts, folder paths, approval pauses, or output formats.
5. New validators must initially run in report-only or warning mode unless Tony explicitly approves enforcement.
6. Existing production folders must continue to work without migration.
7. New metadata must be additive and optional for legacy productions.
8. Every behavior-changing feature must have a feature flag, compatibility path, or explicit migration step.
9. Never automatically regenerate a paid asset because a new validator flags it.
10. Never push to a remote repository without Tony's explicit approval.
11. Never commit rendered `.mp4`, `.mov`, or other large production outputs unless the existing repository policy explicitly requires it.
12. Preserve unrelated user changes in the working tree.

## Required Interview Before Implementation

Do not ask these questions before inspecting the codebase. After inspection, ask only questions whose answers would change architecture or behavior:

1. Should the first version of all new validators be **report-only**, with enforcement turned on after approximately 15 more training videos, or should specific safety checks be enforced immediately?
2. Should the new metadata live inside each production's existing `Data/` folder, or should we introduce a new typed `Contracts/` folder inside each production?
3. Should a new pipeline manifest be documentation-first, or should it become the runtime source of truth immediately? Recommended default: documentation-first, then gradual adoption.
4. Should local commits be created after each approved phase? Recommended default: yes, one focused commit per phase, but no push without approval.
5. For existing productions, should migration be read-only and optional? Recommended default: yes. Never rewrite old productions automatically.

If Tony does not answer a question, use the recommended default and record the assumption in the plan.

## Implementation Strategy

Implement in small, independently verifiable phases. Do not combine all recommendations into one large refactor.

### Phase 0 — Baseline and rollback point

- Create a new branch using the workspace convention, for example `codex/anomalous-wild-safety-upgrades`.
- Record the starting commit and working-tree state.
- Run the existing Anomalous Wild tests without modifying behavior.
- Identify current production fixtures that must remain compatible.
- Add no feature code in this phase.

Acceptance criteria:

- Baseline test results are recorded.
- Existing uncommitted changes are documented and untouched.
- A rollback commit or tag exists locally.

### Phase 1 — Canonical artifact contracts and schemas

Borrow the OpenMontage pattern of validating stage artifacts against schemas, but adapt it to the current Anomalous Wild folder structure.

Start with schemas for:

- `Scene_Routing.json`
- `Beat_Table.json`
- `Shot_List` structured data
- `new_clips_prompts.json`
- narration beat sheets
- generation log entries
- review/report-card data
- cost records
- decision records

Requirements:

- Schemas must be additive and versioned.
- Legacy production artifacts must remain readable.
- Validation must first be report-only.
- Invalid data must produce an actionable error naming the file, field, and correction.
- Do not duplicate schema logic across scripts.

Preferred location to evaluate:

`001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/schemas/`

Do not create this folder until the directory convention and migration impact have been reviewed.

### Phase 2 — Resumable checkpoints

Add a lightweight checkpoint utility inspired by OpenMontage, without replacing `pipeline_supervisor.py`.

Support at minimum:

- `in_progress`
- `awaiting_human`
- `completed`
- `failed`

Record:

- Current phase
- Current scene or beat
- Completed scene/beat IDs
- Failed items and error categories
- Last successful action
- Cost snapshot
- Timestamp
- Relevant artifact paths

The checkpoint system must resume from partial progress and must never regenerate a paid asset merely because a checkpoint is missing. If identity is uncertain, stop and ask Tony.

### Phase 3 — Append-only decision log

Add a normalized decision log for meaningful production choices.

Each decision should include:

- `category`
- `subject`
- `selected`
- `options_considered`
- `reason`
- `confidence`
- `user_approved`
- `timestamp`
- `supersedes`, when applicable

When a choice changes, append a new decision. Do not mutate history.

At minimum cover:

- Video model family
- Provider/model override
- Tool routing
- B-roll versus generated footage
- Prompt strategy
- Diagram method
- Composition/runtime choice
- Voice
- Music
- Thumbnail treatment
- Publish/privacy choice

### Phase 4 — Visual-variety and slideshow-risk gate

Build a report-only pre-generation validator based on the OpenMontage variation and slideshow-risk ideas.

Check for:

- Repeated shot sizes
- Consecutive same-size shots
- Excessive static shots
- Repeated lighting/environment treatment
- Repeated camera movement
- Missing hero moments
- Generic visual descriptions
- Missing shot intent
- Too much dependence on one visual grammar
- Diagram or text beats that risk becoming static slides

Output a production-local report such as:

`Data/Visual_Variety_Report.json`

Do not automatically rewrite prompts or regenerate assets. The report should recommend concrete changes for the shot list or prompt plan.

This phase directly addresses the existing TODO item that visual variety needs a concrete mechanism.

### Phase 5 — Structured prompt generation

Do not discard the existing Anomalous Wild prompt quality. Wrap it in a structured internal representation before producing provider-specific prompt strings.

Evaluate a prompt object containing:

1. Camera/lens/depth of field
2. Shot size and movement
3. Subject/action/anatomical constraints
4. Environment and texture
5. Lighting/color temperature
6. Scientific/reference constraints
7. Character/prop/environment references
8. Channel style adaptation
9. Negative constraints
10. Provider-specific formatting

The generated prompt manifest must remain compatible with the current generation scripts during the migration.

Requirements:

- Preserve the existing scientific grounding language.
- Preserve diagram no-text/no-label safeguards.
- Avoid copying one identical style prefix into every scene.
- Keep prompt provenance: record which skill, style guide, reference, and builder produced each prompt.
- Add tests for prompt stability and required safety constraints.

### Phase 6 — Scored Tool-Manager recommendations

Keep Tool-Manager as the routing authority. Add structured scoring to its output rather than replacing it.

Score candidates on:

- Task fit
- Expected output quality
- Reference/style control
- Reliability
- Cost efficiency
- Latency
- Continuity with locked production decisions

Record the selected tool, rejected alternatives, score breakdown, and reasoning in the shot list or decision log.

Do not hardcode a provider fallback chain unless Tony explicitly approves one.

### Phase 7 — Cost reservation and reconciliation

Extend the current cost estimate pause into an auditable ledger:

```text
estimate -> reserve -> execute -> reconcile actual cost
```

Track per paid action:

- Estimated cost
- Reserved cost
- Actual cost
- Success/failure
- Refund or unused reservation
- Remaining production budget

This must integrate with, not bypass, the existing Tool-Manager pricing sources and approval pauses.

No paid call may be blocked solely because a new ledger is unavailable during the compatibility period. Fail safely by stopping before the paid call and explaining why.

### Phase 8 — Narration-to-visual pacing validation

Use the existing word-level timestamps to validate editorial coverage.

Check:

- Every important narration cue has a visual landmark.
- Visual events do not begin materially before or after their narration beat.
- No beat is underfilled.
- No visual asset continues past its intended narration role without a deliberate reason.
- Diagram camera/reveal motion and label timing are included in the calculation.

Begin in report-only mode. This must not replace the existing static-hold check; it complements it.

### Phase 9 — Declarative pipeline manifest and stage contracts

After the previous phases are stable, create a machine-readable Anomalous Wild pipeline manifest inspired by OpenMontage.

The manifest should declare:

- Stages
- Required input artifacts
- Produced artifacts
- Tools available
- Review focus
- Approval gates
- Revision limits
- Cost policy
- Compatibility/version information

Recommended first stage names:

`intake`, `research`, `script`, `narration`, `beat_plan`, `asset_plan`, `generation`, `assembly`, `audio`, `package`, `publish`

The manifest should initially document and validate the current pipeline. Do not make it the sole runtime orchestrator until parity with the existing skill and scripts is proven.

## Deliberately Do Not Copy From OpenMontage

Do not adopt these ideas blindly:

- Do not remove the existing Anomalous Wild batch supervisor.
- Do not eliminate per-beat Tool-Manager routing.
- Do not force a single renderer or composition engine.
- Do not replace scientific diagram safeguards with generic style/playbook logic.
- Do not force all production decisions into Python.
- Do not require a new board/UI before the file-based pipeline is stable.
- Do not migrate old productions automatically.
- Do not turn every warning into a blocking gate.

## Required Testing

For every phase:

- Add or update unit tests for the new contract.
- Test legacy artifact compatibility.
- Test malformed input and failure behavior.
- Test that paid generation is not triggered by validation alone.
- Test resume behavior with an interrupted mock production.
- Test that existing prompt safety constraints remain present.
- Run the full existing Anomalous Wild test suite.

For any change touching generation, assembly, or publishing, also perform a dry-run against a copied fixture production. Never use a real production folder as a test sandbox.

## Git and Review Workflow

Use this workflow unless Tony explicitly changes it:

1. Inspect and plan only.
2. Ask the required interview questions.
3. Get Tony's approval of the implementation plan.
4. Implement one phase at a time.
5. Run tests and dry-runs after each phase.
6. Create one focused local commit per approved phase.
7. Show the changed files, tests, compatibility notes, and rollback instructions.
8. Wait for Tony's approval before pushing.

Suggested commit subjects:

- `feat(anomalous-wild): add versioned artifact schemas`
- `feat(anomalous-wild): add resumable checkpoints`
- `feat(anomalous-wild): add append-only decision log`
- `feat(anomalous-wild): add report-only visual variety gate`
- `feat(anomalous-wild): add structured prompt contracts`

Do not squash unrelated existing work. Do not amend commits unless Tony explicitly requests it.

## Definition of Safe Completion

This work is not complete merely because the new files exist. It is complete only when:

- Existing Anomalous Wild tests still pass.
- Existing production artifacts remain readable.
- The current pipeline can still run using its existing path.
- New validators are report-only unless explicitly approved as blocking.
- The pipeline can explain what it is doing and why.
- Interrupted work can resume without guessing or unnecessary paid regeneration.
- Prompt construction is inspectable and preserves scientific safeguards.
- Visual variety problems are detected before expensive generation.
- Costs are traceable from estimate through actual spend.
- Every changed behavior has a rollback path.
- Tony has reviewed the final diff before any remote push.

## Final Deliverables Claude Code Must Produce

Before implementation:

- Repository audit summary
- Current architecture map
- Compatibility/risk matrix
- Interview answers and recorded assumptions
- Phased implementation plan
- Test plan
- Rollback plan

After each implementation phase:

- Changed-file summary
- Test results
- Dry-run results
- New behavior and non-behavior statement
- Migration notes
- Rollback instructions
- Proposed commit

