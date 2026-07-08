---
title: "Anomalous Wild Pipeline Scripts — What Exists, What's Active, What's Superseded"
type: wiki
category: video-production
tags:
  - video-production
  - orchestration
  - anomalous-wild
  - pipeline
created: 2026-07-07
source:
  - [[../../001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/pipeline_supervisor.py]]
  - [[../../001_Architecture/Tools/Video-Generation/Generic_Tools/run_new_clips_batch.py]]
  - [[../../001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/DESIGN.md]]
  - [[../../001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/PLAN.md]]
---

# Anomalous Wild Pipeline Scripts

## What It Is
Anomalous Wild was the **first video pipeline ever built in this workspace** — it predates Reimagined Realms, which was, until now, the only channel with a fully locked, single-command pipeline (`/reimagined-realms`). Because Anomalous Wild's early tooling grew organically across multiple sessions, several scripts below do overlapping jobs from different eras, rather than one clean pipeline. This page exists so a future "what does this script do" question can be answered by reading this page, not by re-deriving it from scratch.

**Update 2026-07-07/08: the unifying orchestrator skill is now built.** See `001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/SKILL.md` — invoke via `/anomalous-wild`. Built via `superpowers:subagent-driven-development` (one fresh subagent per task, task-scoped review with fix rounds where needed, then a final whole-branch review). Full task-by-task history: `DESIGN.md` (approved spec) + `PLAN.md` (11-task plan, Task 10 skipped as already done manually). See "The New Orchestrator Pipeline" section below for what it actually built.

## The Generation Scripts — Which One Is Actually Used

| Script | Location | Status | What it does |
|---|---|---|---|
| `pipeline_supervisor.py` | `Channels/Anomalous_Wild/` | ✅ **Active / preferred** | Batch clip generator with real error-code classification (FATAL/CREDITS/SKIP/RATE/WAIT/RETRY/UNKNOWN), retries, macOS notifications, auto-preloop after success. Kept as-is in the new pipeline design. |
| `run_new_clips_batch.py` | `Generic_Tools/` (despite the name, only ever used for Bioluminescence Weapon) | ⚠️ **Superseded, not deleted** | Simpler batch generator, same core job as `pipeline_supervisor.py` but without retry/error sophistication. See below for its one distinguishing feature. |
| `preloop_new_clips.py` | `Generic_Tools/` | Active, used by `pipeline_orchestrator.sh` | Post-processes freshly generated clips into looped versions matching narration duration. |
| `preloop_videos.sh` | `Channels/Anomalous_Wild/` | Active | Same preloop job, for the original 12 hero clips (hardcoded durations). Needed bash 4+ (`declare -A`); fixed 2026-07-07 via `brew install bash` (5.3.15, now first in PATH). Verified end-to-end — all 12 clips correctly reported as already looped. |
| `pipeline_orchestrator.sh` | `Channels/Anomalous_Wild/` | Active | 6-stage wrapper chaining the above four scripts in sequence. Was calling a `004_Tools/` path that stopped existing after a June reorg — fixed 2026-07-07. |
| `check_pipeline_status.py` | `Channels/Anomalous_Wild/` | Active | Read-only: reports which clips/images are done vs. pending. |

## The Diagram Safety Idea Worth Remembering

`run_new_clips_batch.py` has one feature `pipeline_supervisor.py` lacks: for any image entry marked `is_diagram: true`, it auto-appends a negative prompt — *"no text, no labels, no callout lines, no arrows, no annotation marks"* — before sending it to the image model. This was added after Tony's Video 001 Report Card caught garbled, misspelled text baked into an AI-generated anatomical diagram (see `Productions/0001_Bioluminescence_Weapon/Grading_Interview/Report_Card.md`).

**It didn't fully work** — a negative prompt alone doesn't reliably stop an image model from occasionally rendering garbled text anyway. That's a known limitation of these models, not a bug in the script. The actual fix, designed 2026-07-06 for the new pipeline, goes further:

1. Research a real reference image of the subject first (grounds anatomy in reality)
2. Generate a clean illustration guided by that reference, still with the no-text negative prompt
3. **New step:** a vision model looks at the *actual generated image* and returns real coordinates for each labeled feature — no guessing
4. Labels and callout lines get placed in Remotion at those exact detected coordinates

So the idea behind `run_new_clips_batch.py`'s negative-prompt trick carries forward into the new pipeline; the script itself doesn't need to.

## Remotion Components

- **`BioluminescenceDoc.tsx`** — the actual composition that renders Bioluminescence Weapon. Hardcoded to that video's specific scenes and durations; not a reusable template. A reference copy lives at `Productions/0001_Bioluminescence_Weapon/Remotion/BioluminescenceDoc.tsx`; the live, working version stays in `003_Remotion/src/remotion/video-components/` untouched.
- **`AnomalousWildEndCard.tsx`** — the channel's end card composition. In practice, the pipeline doesn't re-render this per video — it just appends the pre-rendered `end_card_v3.mp4` via ffmpeg (locked rule, see DESIGN.md). A reference copy lives at `Brand_Assets/End_Card/AnomalousWildEndCard.tsx` next to the actual mp4 files; still registered live in `Root.tsx` too.

## Folder Structure (as of 2026-07-07)

Anomalous Wild's channel and production folder structure was reorganized to match Reimagined Realms' pattern:
- Channel level: `Brand_Assets/` (End_Card, Branding), `Case_Studies/`, `Productions/`
- Production level (`Productions/0001_Bioluminescence_Weapon/`): `Scripts/`, `Production/`, `Images/`, `Video_Clips/`, `Narration_Audio/`, `Audio_Stems/`, `Assembly/` (with versions nested inside as `Assembly/Versions/`), `Package/`, plus `Grading_Interview/`, `Motion-Graphics/`, `Remotion/`, `_tests/` for things that don't fit the typed categories.

## The New Orchestrator Pipeline (built 2026-07-07/08)

### Why it was built
The Bioluminescence Weapon video's anatomical diagram (anglerfish) shipped with garbled, misspelled text baked into the AI-generated image — an "AI slop" defect. Root cause: the image model was asked to draw both the illustration AND the labels in one shot. The fix required a real multi-step sub-pipeline (research → clean illustration → vision-verified coordinates → separately-placed labels), plus the channel needed the same start-to-finish automation Reimagined Realms already had (word-level timestamps, YouTube package, Blotato upload).

### What it built (11 tasks, Task 10 skipped as already done)
1. **Tool-Manager Motion Graphics Capability Profile** — `motion_graphics_capabilities.json`, every tool entry (Remotion/video-use/Hyperframes/Manim) cites a real source. Lets the orchestrator route each beat's visual need live, instead of hardcoding "diagrams always go to Remotion."
2. **Word-level narration timestamps** — `generate_narration_with_timestamps.py`, thin wrapper around the existing proven `audio_tts.py` function.
3. **Beat table builder** — `build_beat_table.py`, encodes the two hard rules: 8s max clip for live-footage beats, 3-5s max static frame for diagram beats.
4-6. **Scientific Diagram sub-pipeline** — the actual fix for the garbled-text problem:
   - `diagram_research_and_illustrate.py` — real Openverse reference image + clean no-text kie.ai illustration
   - `detect_label_coordinates.py` — Gemini vision detects real per-image coordinates, structurally strips any coordinate from a `not_found` entry (code-enforced "never guess," not just a prompt instruction)
   - `DiagramLabels.tsx` — Remotion component that places labels/callouts at those exact coordinates
7. **YouTube package generator** — `generate_youtube_package.py`, adapted from RR's formulas, and actually generates 3 real thumbnail images (not just prompts)
8. **Blotato upload procedure** — `upload_to_blotato.md`, with a real-verified account ID
9. **End card lock-in + scaffolder** — `scaffold_new_production.py`
11. **Orchestrator SKILL.md** — `/anomalous-wild`, wires all of the above into 10 phases mirroring RR's structure

### Bugs caught during the build (worth remembering the *pattern*, not just the fix)
- **Per-task reviews caught:** a fabricated-capability risk in Task 5's vision coordinates (fixed with code-level stripping, not just a prompt instruction), a type-erasure cast in Task 6 instead of the codebase's existing Zod-schema pattern, a silently-missing thumbnail-generation step in Task 7, and — most consequential — a malformed YAML frontmatter bug in Task 11's SKILL.md (a dangling unquoted second `<example>` block outside the `description:` string) that was **actively degrading the skill's own trigger-matching in the live system** — confirmed by comparing this session's own skill list before/after the fix. The exact same defect existed in Reimagined Realms' `SKILL.md` (same pattern, presumably introduced the same way) and was fixed too once flagged.
- **Only the final whole-branch review caught:** two cross-cutting integration bugs invisible to any single task's review — (1) Task 5's `not_found` coordinate-stripping was rejected by Task 6's *original* required-field Zod schema, which would have crashed diagram assembly in exactly the safety-path scenario the design was built to handle; (2) the 3-5s static-frame rule was recorded as data (`max_static_s`) but nothing in the pipeline actually read or enforced it anywhere. Both fixed and re-verified. **Lesson:** per-task review is necessary but not sufficient for a multi-task build with real interfaces between tasks — the final whole-branch pass is where cross-task contradictions surface.

## Related
- [[Pipeline-Orchestration]]
- [[Video-Production-Workflow]]
