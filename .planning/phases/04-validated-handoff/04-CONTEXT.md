# Phase 4 Context: Validated Handoff

## Domain Boundary

Connect the selected passing storyboard to Neon Parcel Seedance prompt construction and the existing pre-video gate. The handoff must reject any storyboard that is missing, failed, ambiguous, or not selected by the Phase 3 controller.

## Decisions

### Source of truth
- The selected storyboard manifest is the required source for continuity and action handoff.
- Seedance prompt text must be derived from validated storyboard observations, not regenerated from the original unchecked shot description alone.
- The original shot intent may supply context only where it does not contradict the validated storyboard evidence.

### Prompt structure
- Preserve the existing mandatory five-section Seedance order: camera lock, scene continuity, action timeline, audio, hard constraints.
- Convert frame observations into chronological observable physical beats with cause and result.
- Do not tell Seedance to reproduce storyboard panels literally; the storyboard remains contextual reference input.

### Gate and routing
- Require `status == pass` and a selected active candidate before handoff.
- Keep storyboard `reference_image_urls` separate from clean temporal `first_frame_url`.
- Preserve candidate/contract/QA hashes and paths in the handoff manifest and generation log.
- The pre-video gate remains provider-free and must block before any paid request.

## Agent's Discretion

- Exact manifest field names and prompt-builder API, provided selected-pass evidence is mandatory.
- How frame descriptions are compacted into action beats, provided no chronological or causal information is dropped.
- Whether handoff validation lives in the existing gate or a dedicated helper called by it, provided every Seedance path uses it.
- Exact treatment of audio when storyboard evidence contains no audio information: use the existing native-audio defaults and never invent dialogue.

## Canonical References

- `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/storyboard_contract.py`
- `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/storyboard_qa.py`
- `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/storyboard_regeneration.py`
- `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/validate_pre_video_gate.py`
- `001_Architecture/Tools/Video-Generation/Generic_Tools/kie_market_api.py`
- `001_Architecture/Skills/Neon_Parcel_Longform_Compilation/Templates/Seedance-Prompt-Contract.json`
- `001_Architecture/Skills/Seedance-Prompting-Guide/SKILL.md`
- `.planning/phases/03-capped-regeneration/03-SUMMARY.md`

## Deferred Ideas

- Full video-output QA remains outside this project.
- Provider/model-specific prompt optimization and threshold calibration belong in v2.
