# Phase 3 Context: Capped Regeneration

## Domain Boundary

Orchestrate storyboard candidate generation, QA sequencing, archival, and blocking. A candidate must be generated, checked by Phase 2, and only then can the next candidate be requested. This phase does not redesign the vision evaluator or generate the final Seedance prompt.

## Decisions

### Hard attempt cap
- Maximum of three storyboard candidates per shot.
- Candidate two cannot be requested until candidate one has a recorded QA result; the same rule applies to candidate three.
- After the third candidate fails or requires manual review, the shot is flagged and downstream Seedance generation is blocked.

### Versioning and preservation
- Every candidate prompt, image, QA result, and attempt state is preserved.
- Failed/superseded candidates move to the matching archive location; active output contains only the selected passing candidate.
- Regeneration must never overwrite a prior candidate or silently reuse a failed candidate as the accepted reference.

### Retry prompting
- Retry prompts retain the same Phase 1 schema and frame order.
- A retry may add targeted corrections derived from the prior QA findings, but it must not rewrite the original shot intent invisibly.
- A passing candidate becomes the only storyboard artifact eligible for Phase 4 handoff.

### Cost and safety boundary
- The orchestrator owns the counter and refuses attempts above three before calling the image provider.
- Provider failures and QA failures remain distinct in the audit record.
- No Seedance task may be submitted from a failed/manual-review storyboard state.

## Agent's Discretion

- Exact state-file format and status names, provided transitions are explicit and append-only.
- Whether the image-generation adapter is synchronous or poll-based, provided the attempt is recorded before submission and finalized after the image exists.
- Exact archive subfolders, provided they preserve shot ID, candidate number, and version.
- Retry correction wording, provided it is derived from actionable QA findings and remains within the stable contract.

## Canonical References

- `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/storyboard_contract.py`
- `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/storyboard_qa.py`
- `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/generation_guard.py`
- `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/production_state.py`
- `002_Content-Creation/Video_Editor/002_Channels/002_Neon-Parcel/Productions/0001_Grandma-And-Bear-Compilation/Scripts/regenerate_storyboard_shots_v2.py`
- `.planning/phases/02-storyboard-qa/02-SUMMARY.md`

## Deferred Ideas

- Automatic provider cost optimization and threshold calibration belong in v2.
- Human editing UI for retry corrections belongs in v2.
