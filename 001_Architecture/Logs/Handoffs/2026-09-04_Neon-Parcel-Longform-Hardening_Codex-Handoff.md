---
title: "Neon Parcel Longform Hardening — Codex Handoff"
type: handoff
category: video-production
created: 2026-09-04
---

# Neon Parcel Longform Hardening — Codex Handoff

## 1. Summary

This session hardened the Neon Parcel longform-compilation pipeline around the
failure pattern seen in Shots 6, 8, 11, and 12: storyboards could be visually
ambiguous, Seedance prompts could restate assumptions instead of the accepted
image, and paid outputs could be advanced before physics/continuity review. The
pipeline now uses a structured per-frame storyboard contract, capped storyboard
retry/QA machinery, validated storyboard-to-Seedance handoff, direct Gemini
video inspection as the default evidence provider, explicit Tony approval gates,
and non-destructive version/archive protection. The purpose is to reduce wasted
generation/upscale credits while keeping every paid artifact recoverable across
Codex, Claude Code, Gemini CLI, Antigravity, and future harnesses.

## 2. Files touched

### Shared skills, configuration, and registry

- `001_Architecture/Skills/Neon_Parcel_Longform_Compilation/SKILL.md` — locked Neon Parcel route, dual-skill prompting requirement, storyboard/video review policy, fallback rules, and preservation gates.
- `001_Architecture/Skills/Neon_Parcel_Longform_Compilation/pipeline.yaml` — configured manual review, Gemini-first inspection, OpenRouter fallback, and approval policy.
- `001_Architecture/Skills/Storyboard-Generation/SKILL.md` — structured storyboard, subject-origin, spatial-geometry, realism-tone, and QA requirements.
- `001_Architecture/Skills/Storyboard-Generation/Examples/` — reusable storyboard examples for panel structure and continuity review.
- `001_Architecture/Skills/Seedance-Prompting-Guide/SKILL.md` — storyboard handoff, timestamped action, audio/camera constraints, and duration/reference guidance.
- `001_Architecture/Skills/Tool-Manager/SKILL.md` — added cross-agent learning-propagation rule so validated lessons reach governing skills/configuration/tools.
- `TOOLBOX.md` — documented Gemini video inspection and the Neon Parcel hardening checkpoint.
- `001_Architecture/Skills/Skill-Index.md` — refreshed canonical skill registry.

### Neon Parcel tools and tests

- `001_Architecture/Tools/Video-Generation/Generic_Tools/kie_market_api.py` — supports explicit Seedance first/last-frame inputs, rejects invalid reference combinations, and refuses unsafe downloads.
- `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/generation_guard.py` — blocks paid generation without an explicit version and revision reason.
- `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/artifact_preservation.py` — centralizes new-version and archive safeguards.
- `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/gemini_video_inspection.py` — uploads video directly to Gemini and emits timestamped structured findings.
- `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/storyboard_contract.py` — serializes frame-level subjects, states, relationships, actions, captions, tone, and capture style.
- `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/storyboard_qa.py` — evaluates storyboard evidence against the structured contract.
- `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/storyboard_regeneration.py` — caps storyboard attempts at three and preserves failed candidates.
- `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/storyboard_ensemble.py` — records advisory provider findings and enforces human-in-the-loop policy fields.
- `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/storyboard_handoff.py` — builds Seedance prompts from the accepted storyboard observations.
- `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/storyboard_vision_provider.py` — storyboard vision-provider adapter boundary.
- `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/validate_pre_video_gate.py` — fail-closed pre-video validation.
- `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/test_gemini_video_inspection.py` — tests Gemini inspection parsing and policy behavior.
- `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/test_artifact_preservation.py` — tests non-destructive artifact handling.
- `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/test_generation_guard.py` — tests paid-generation version guards.
- `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/test_storyboard_*.py` — tests storyboard contract, QA, retries, provider policy, and handoff behavior.
- `001_Architecture/Tools/Video-Generation/Generic_Tools/test_kie_market_api.py` — tests Kie reference routing and download safety.

### Shot 11 production records

- `002_Content-Creation/Video_Editor/002_Channels/002_Neon-Parcel/Productions/0001_Grandma-And-Bear-Compilation/Scripts/generate_shot11_v5.py` — records and submits the approved v5 Seedance generation without overwriting prior attempts.
- `002_Content-Creation/Video_Editor/002_Channels/002_Neon-Parcel/Productions/0001_Grandma-And-Bear-Compilation/Scripts/finish_shot11_v5.py` — downloads, upscales, normalizes, and verifies the separately versioned v5 output.
- `001_Architecture/Tools/Video-Generation/Channels/Neon_Parcel/shot_11_storyboard_spec_v2.json` — structured eight-frame sprinkler storyboard contract.

## 3. Key decisions and reasoning

- **Use both storyboard and Seedance skills every time.** The storyboard is a
  Seedance input, so image continuity and video-model behavior cannot be treated
  as separate concerns.
- **Storyboard generation remains one sheet, not six separate paid images.**
  The cost-saving approach is one image generation containing detailed,
  explicitly described frames; the contract and inspection compensate for the
  ambiguity risk.
- **Inspect, report, then ask Tony.** Gemini/OpenRouter findings are evidence,
  not automatic approval or rejection. This protects against false positives
  and false negatives while Tony is still calibrating trust.
- **Build the Seedance prompt from what the accepted storyboard visibly shows.**
  This prevents the original idea from reintroducing actions, origins, or
  geometry that the generated storyboard did not actually establish.
- **Cap storyboard retries at three.** This limits spend; after three failed or
  unresolved candidates the shot is flagged rather than burning credits.
- **Use direct Gemini first for short-video inspection.** Static sampling at 3
  FPS is appropriate when every frame, origin, eyeline, route, and physics issue
  matters; OpenRouter remains fallback/second opinion.
- **Never overwrite.** Every paid generation, fallback, upscale, and normalized
  derivative gets a new version; superseded artifacts move to `Archived/`.
  This preserves recovery if inspection is wrong.
- **Shot 11 used the storyboard route and passed raw review before Topaz.**
  Tony approved the raw v5 clip, allowing the v5 upscale; the final remains
  pending Tony’s manual review.
- **Graphify was not refreshed.** The installed CLI reports package/skill
  mismatch and does not support the documented `graphify update` command. Do
  not assume the graph reflects this handoff until the CLI contract is resolved.
  — **UPDATE 2026-09-05 PM: CLI contract resolved.** `graphifyy` upgraded
  `0.4.2 → 0.9.55`, stale Homebrew shadow removed, skill copies refreshed.
  `graphify update` / `extract` / `check-update` now available. The graph
  still needs an actual refresh run, but the tooling blocker is gone.
  See `001_Architecture/Graphify/REGISTRY.md` `## Tooling version`.

## 4. Current state

### Done / working

- Structured storyboard contract, QA, three-attempt controller, and Seedance
  handoff code are present.
- Manual-review policy is represented in pipeline configuration and ensemble
  outputs; providers do not auto-clear or auto-reject.
- Direct Gemini video inspection ran successfully on Shot 11 using static 3 FPS
  sampling and produced timestamped findings.
- Shot 11 raw v5 was approved by Tony, upscaled with Topaz 2x, and normalized to
  1920x1080 as `Shot-11-1080p-v5.mp4`.
- Global feedback, session log, self-review, and durable memory were updated.

### Partially done

- Shot 11 final v5 still needs Tony’s manual final review.
- The actual GPT-Image storyboard generation adapter and full live storyboard
  vision-provider loop remain less thoroughly exercised than the dry-run and
  Shot 11 handoff logic.
- The manual-review on/off policy is represented in configuration, but a
  user-facing control surface has not been verified.

### Broken or untested

- `graphify update .` is documented but unavailable in the installed Graphify
  CLI; graph refresh is therefore unverified.
- A full repository test suite was not run during this closeout.
- Automated vision remains inherently fallible for subtle physics, eyelines,
  object origins, and timing; no provider result should be treated as proof.
- The working tree contains broad pre-existing/uncommitted changes from other
  pipeline work. Do not reset, discard, or blindly commit them.

## 5. Open questions / ambiguities

- Should Graphify be upgraded to the skill’s expected version, or should the
  documented graph-refresh command be updated to the installed CLI’s workflow?
- Where should the manual storyboard/video review toggle live for Tony: only in
  `pipeline.yaml`, or also in a UI/CLI command and production manifest?
- Should Gemini and a second provider be run routinely in parallel, or should
  Gemini remain primary with OpenRouter invoked only for disagreement/uncertainty?
- What exact approval label should be recorded for Shot 11 final v5 after Tony
  reviews it: pass, pass-with-minor-defect, or revision?

## 6. Next steps, in priority order

1. Present and obtain Tony’s manual approval or revision decision for Shot 11
   final v5. Do not generate, upscale, or advance Shot 12 before that decision.
2. If Shot 11 passes, record the approval in the daily feedback and session log,
   then begin Shot 12 with storyboard review only; preserve its existing v2.
3. Run the targeted Neon Parcel tests and any available full test suite before
   relying on the new adapters for more paid generations.
4. Resolve the Graphify CLI mismatch and refresh the graph after the final docs
   and skill changes are accepted.
5. Verify and, if needed, expose the manual-review policy toggle in the normal
   operator workflow.
6. Keep propagating validated lessons into skills/configuration/executable
   guards, not only episodic memory.

## 7. Source pointers

- `001_Architecture/Feedback_Loop/2026-09-04_Feedback.md` — Tony’s current
  approvals, corrections, and closeout persistence rules.
- `001_Architecture/Logs/2026-09-04_Session-Log.md` — chronological Shot 11
  generation, Gemini inspection, raw approval, Topaz completion, and resume gate.
- `001_Architecture/Memory/Global_Agent_Memory.md` — durable cross-agent rules
  for storyboard QA, Seedance references, preservation, and learning propagation.
- `001_Architecture/Self_Learning_Loop/2026-09-04_Self-Review.md` — honest review
  of what worked, residual vision risk, and the Shot 11 resume checkpoint.
- `001_Architecture/Skills/Neon_Parcel_Longform_Compilation/SKILL.md` — governing
  Neon Parcel workflow and hard gates.
- `001_Architecture/Skills/Storyboard-Generation/SKILL.md` — shared storyboard
  contract and visual-continuity guidance.
- `001_Architecture/Skills/Seedance-Prompting-Guide/SKILL.md` — shared Seedance
  reference-role, timeline, audio, and handoff guidance.
- `TOOLBOX.md` — cross-agent inventory and Neon Parcel tool-routing notes.
