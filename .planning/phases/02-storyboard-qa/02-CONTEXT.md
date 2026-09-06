# Phase 2 Context: Storyboard QA

## Domain Boundary

Evaluate one generated storyboard sheet against the Phase 1 structured storyboard contract and return an evidence-backed pass/fail/manual-review result. This phase does not request retries, archive candidates, or submit Seedance tasks; those behaviors belong to Phase 3 and Phase 4.

## Decisions

### What the checker must compare
- Inspect the actual generated storyboard image, not only the source prompt.
- Check each panel against its declared frame number, visible subject count, object state, spatial relationship, action/state, and exact caption.
- Check adjacent panels for causal transitions, chronological ordering, camera/geometry continuity, and plausible physical movement.

### Failure behavior
- Missing, unreadable, contradictory, or low-confidence vision evidence must fail closed.
- The result must distinguish `pass`, `fail`, and `manual_review` internally, with only `pass` eligible for later downstream use.
- Findings must identify the frame/panel and the violated requirement so a later regeneration prompt can target the defect.

### Cost and provider boundary
- The checker may use the existing vision-analysis provider pattern, but the provider call must be behind an injectable adapter so tests never call the network.
- One QA evaluation is performed per candidate; retry orchestration is explicitly deferred to Phase 3.
- The checker must not alter or overwrite the candidate image.

## Agent's Discretion

- Exact vision provider/model and request format, provided the adapter can be replaced and the raw response is archived or hash-linked.
- Whether panel crops are computed by fixed layout metadata or supplied by the caller, provided the checker never assumes a panel exists without evidence.
- Exact confidence thresholds, provided low confidence fails closed and thresholds are recorded in the QA result.
- Whether the language-model response is parsed directly or normalized through a schema validator.

## Canonical References

- `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/storyboard_contract.py`
- `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/shot_06_storyboard_spec.json`
- `001_Architecture/Skills/Storyboard-Generation/SKILL.md`
- `001_Architecture/Skills/Neon_Parcel_Longform_Compilation/SKILL.md`
- `001_Architecture/Tools/AI-Analysis/gemini_scene_analysis.py`
- `001_Architecture/Tools/AI-Analysis/gemini_video_analysis.py`
- `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/validate_pre_video_gate.py`
- `.planning/phases/01-storyboard-contract/01-ACCEPTANCE-CHECKLIST.md`

## Deferred Ideas

- Calibrating thresholds against a larger labeled storyboard dataset belongs in v2.
- Human editing of failed frame requirements belongs in v2.
- Automatic video-output QA is not part of this phase.
