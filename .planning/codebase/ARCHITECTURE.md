# Architecture

## Pattern
The workspace uses skill-guided orchestration around small auditable Python tools. Human approvals and production artifacts are first-class state, rather than hidden inside a single service.

## Relevant Data Flow
1. A production shot list defines the intended action, subjects, props, and continuity.
2. Storyboard-generation guidance creates a single storyboard sheet with sequential panels.
3. A storyboard reference is supplied to Seedance as contextual guidance.
4. Generation guards reserve and log paid attempts.
5. Provider output is inspected, normalized, archived, and promoted to the active clip.

## Existing Modules
- `route_shot_complexity.py` selects a conservative video route without spending credits.
- `generation_guard.py` prevents duplicate or unreasoned paid submissions.
- `validate_pre_video_gate.py` catches prompt/reference-role errors before video generation.
- `production_state.py` records explicit production checkpoints and append-only decisions.
- `decide_end_frame.py` handles endpoint evidence for start/end-frame workflows.

## Planned Integration Point
Add a storyboard contract and QA/regeneration orchestrator before the current pre-video gate. The orchestrator should produce:
- structured storyboard instructions;
- candidate image metadata and attempt count;
- vision QA findings tied to frame-level requirements;
- a validated storyboard manifest consumed by Seedance prompt generation;
- a blocked/manual-review result after the third failed candidate.

The Seedance prompt should be derived from the validated storyboard evidence, not only from the original shot description.
