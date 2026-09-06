# Concerns

## Confirmed Failure Mode
The existing storyboard workflow can generate one sheet whose panels do not satisfy the intended sequence. In the Shot 6 example, subject presence and gate state were inconsistent across frames, while the Seedance prompt still described the intended action. This creates a contradiction between reference image and text prompt.

## Main Risks
- A visual checker could approve a pretty but logically invalid storyboard unless it checks explicit frame requirements.
- A prompt-only checker cannot reliably verify what the generated image actually contains.
- Regeneration can become an unbounded cost loop without a hard three-attempt cap.
- Deriving Seedance prompts from the original idea after QA would reintroduce the same contradiction.
- Baked captions may be visually legible but semantically wrong; caption text needs its own check.
- Storyboard sheets can accidentally be passed as temporal first frames, producing visible sheet artifacts.

## Existing Fragility
- Provider calls are external and paid, so preflight and logging must remain separate from generation.
- The workspace is broad and lacks a repository-wide package manifest; tests should target stable module boundaries.
- Current scripts are intentionally conservative and mostly deterministic; vision evaluation will need a clear adapter and recorded evidence for reproducibility.

## Guardrails Required
Use a versioned structured schema, frame-level acceptance criteria, candidate cap of three, explicit archive paths, evidence records, and a hard downstream block when no candidate passes.
