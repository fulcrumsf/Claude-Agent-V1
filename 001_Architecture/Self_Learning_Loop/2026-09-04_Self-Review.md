---
title: "Self-Review — 2026-09-04"
type: self-review
domain: meta
tags: [self-learning, retrospective]
---

# 2026-09-04 — Self-Review

## Anomalous Wild 0003 Glass Frog — the iteration that earned the A

### What went well
- Tool-Manager consult before switching the audio approach worked exactly as
  intended: surfaced that no video-to-audio model does a 3-min pass, and that the
  non-destructive move was to feed the *existing per-scene clips*, not cut the master.
- Smoke-tested one segment before firing all 6 — caught the Mirelo response-parse
  bug on a cheap single call instead of a batch.
- When the batch stalled, I checked `ps -o etime` + file sizes and found the real
  cause (all-intra 325MB segments) rather than blaming fal or just waiting.

### What went wrong / cost time
- **The segment encoder bug was mine and avoidable.** `-force_key_frames
  expr:gte(t,0)` matches every frame. I should have tested the cut-file size before
  running the batch — I tested it *after* killing a 65-minute stall.
- **First mix followed the locked stems formula (−20) blindly.** The locked value
  was calibrated for sparse ElevenLabs stems; a dense v2a jungle bed at −20 sat
  *above* the score. Tony had to tell me. I should have predicted a denser source
  needs a lower target and A/B'd it myself first.
- **Reused the pre-baked `end_card_with_cta.mp4` without checking its level.** It
  was −6 dB low. Tony caught it on the *finished* cut — exactly the kind of thing
  the pre-review gate now forces a check for.

### The meta-lesson (already written into the AW SKILL as the PRE-REVIEW GATE)
Reaching grade A took FULL10 → FULL16 — six review rounds *after* the work was
called done. Every round was a distinct defect class:
transitions (×3), anatomy, audio-mix level, CTA level. The individual checks mostly
existed but weren't all run on every re-render, and two didn't exist at all
(per-cut transition verify, generated-clip anatomy pass). A "done" that needs six
more rounds was never done. The fix isn't "try harder" — it's a single gate that
runs the whole battery before anything reaches Tony, re-run in full after every
re-render.

### Pattern to carry forward
A locked numeric constant (audio level, duration, threshold) is only valid for the
input distribution it was tuned on. When the *source* of that input changes
(ElevenLabs stems → video-to-audio bed), re-derive the constant, don't inherit it.
Same lesson as the 2026-08-30 "a rule that's only prose isn't locked" — this is
"a constant that's only a number isn't calibrated."

## Neon Parcel closeout review

### What was reinforced
- The Shot 11 workflow follows the intended control loop: structured storyboard contract, panel-by-panel inspection, prompt built from the accepted visual result, paid generation, raw-video inspection, Tony approval, then upscale.
- Direct Gemini video inspection is the default evidence provider for short clips, with OpenRouter as fallback or second opinion. Neither provider is allowed to make the final approval decision.
- Versioning and archive protection are cost and trust controls, not housekeeping.

### Remaining risk
- Automated vision can miss or misinterpret physics, eyelines, object origins, and timing. It must produce timestamped observations and confidence, but a human decision remains required while Tony is calibrating trust.
- Documentation can drift from code. The Tool-Manager now explicitly requires propagation of validated lessons into skills, configuration, toolbox entries, and executable guards where possible.

### Resume checkpoint
- Shot 11 final v5 is awaiting Tony's manual final review. No additional processing is permitted until that review is recorded.

## Codex Agent-OS onboarding correction

### What went wrong
- Codex treated Tony's request for a save-location recommendation as permission to create the file immediately. That skipped the decision checkpoint Tony explicitly wanted.
- The first location was plausible by folder rules, but the process was still wrong: recommendation and implementation are separate modes when Tony asks for suggestions first.

### Pattern to carry forward
- When Tony asks for recommendations, options, or where something belongs, the agent should stop after the recommendation and wait. Acting early creates cleanup work and erodes trust even when the final location is later corrected.
- Codex needs a stronger Agent-OS operating checklist at startup, not just ad hoc memory entries. The new `codex-agent-os-hardening` skill exists to force the same habits Claude Code already uses: read manuals, check maps/tools/skills, preserve files, record feedback, update memory, and close sessions cleanly.
- On broad Agent-OS onboarding, do not treat every folder equally. Tony explicitly prioritizes the numbered departments, with Architecture first, Content Creation second, and Resource Library third; Ingest is usually raw intake and should only be examined deeply when the task is about ingest.
