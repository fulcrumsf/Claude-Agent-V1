# Session Log — 2026-08-15

Continuation of a multi-day session (started 2026-08-10) covering: ingest skill scoping, the Seedance Case Study Pipeline (Phases 1-3), Video-Analyzer upgrades, and a POV Shorts pipeline bug-diagnosis-and-fix cycle.

## Ingest Skill
- Added a "Scope Question" to `001_Architecture/Skills/ingest/SKILL.md`: a generic "ingest"/"process ingest" trigger now asks a 5-option multiple-choice question (top-level only / everything incl. subfolders / a named subfolder / choose files / freeform "other") before touching anything. Default flipped from auto-recurse-everything to top-level-only.

## Seedance Case Study Pipeline (multi-phase, plan saved in Claude memory `project_seedance_case_study_pipeline.md`)
- **Phase 1 — Ingest:** 11 Seedance/consistency YouTube tutorial transcripts ingested from `000_Ingest/` (top-level). 10 routed to `007_Resource_Library/Tutorials/`, 1 tool-doc (kie.ai CLI/MCP) to `007_Resource_Library/Tools/`. 9 new wiki pages in `000_Wiki/Video-Production/`, cross-linked, logged, indexed.
- **New shared folder created:** `002_Content-Creation/Video_Editor/002_Channels/Universal_Case_Studies/` — for case studies not specific to one channel. Existing `004_Seedance_Storyboard_Character_Consistency_Tutorial` moved out of ReimagineRealms' `Case_Studies/` into this new folder as `001_`.
- **Phase 2 — Case studies:** all 10 video tutorials run through Video-Analyzer into `Universal_Case_Studies/001`-`010` (Gemini narrative + later backfilled with keyframes/transcript).
- **Video-Analyzer skill upgraded** (`001_Architecture/Skills/Video-Analyzer/`): added local FFmpeg full-resolution scene-cut keyframe extraction + local Whisper transcription (both free, no API cost) alongside the existing Gemini pass, plus a mandatory "read the keyframes yourself" step for on-screen prompts/settings/composition Gemini can't reliably read. Later added a second `--dense-interval` extraction mode (fixed-interval frames regardless of scene cuts) specifically for continuity/fault auditing, since scene-cut keyframes miss drift within one continuous shot.
- **Phase 3 — Outlier extraction → Seedance skill upgrade:** `Seedance-Prompting-Guide/SKILL.md` restructured into a Core (shared mechanics) + 5 production-style framework (POV, Cinematic Narrative/Multi-Character, Documentary, UGC/Talking Presenter, Portal/Transition), each labeled with which pipelines actually use it today (mostly none yet, outside POV). New supporting file `Cinematic-Narrative-Multi-Character.md` holds the heaviest addition — a real "AI Filmmaking Bible" Variant A/B/C prompt-template system found in the case study research, with dynamic `@image` renumbering rules, audio-default policy, and dialogue-in-timeline convention.

## POV Shorts Pipeline v2 — Bug Diagnosis and Fix
- Tony flagged unnatural POV framing on Roman Gladiator (constant hands/legs visible regardless of gaze direction) and a POV-to-third-person camera break on Pyramid Builder's opening scene.
- Investigation found `POV_LOCK_CLAUSE` (duplicated in `shot_list_builder.py` and `storyboard_generation.py`) had over-corrected: it mandated hands/forearms/chest-down body be *always* visible in every shot, instead of only banning what's physically impossible to see.
- A citation in `POV_Style_Guide.md` claiming a "confirmed 2026-08-05" face-rendering bug was checked against git history, session logs, and feedback loop — found to have no basis anywhere. Flagged and later corrected.
- Ran the newly-upgraded Video-Analyzer (dense-interval mode) on Pyramid Builder and a new Roman Gladiator case study (`Case_Studies/004_Roman_Gladiator_Continuity_Review/`) to get real visual evidence. Confirmed both bugs directly from full-resolution frames.
- **Fixes applied and tested (126/126 passing):** `POV_LOCK_CLAUSE` corrected in both files to a negative-constraint rule (never show own face/back-of-head/shoulder/back; hands/arms visibility now scene-dependent). `POV_Style_Guide.md` scene-writing checklist grown to 10 items with a new "pose-change-within-a-shot" check (split any big pose change into two generations with a last-frame handoff). False citation replaced with the real, visually-confirmed incident.

## Roadmap (Tony, 2026-08-15)
Two-phase plan for this pipeline: manual iterate → critique → publish → critique loop until output quality is consistently ~99%, then transition to scheduled/autonomous mode (auto topic discovery, script, generation, publish) gated only by a lightweight Airtable/spreadsheet yes/no on proposed ideas. Currently in phase one.

## Files changed
Ingest skill, Seedance-Prompting-Guide skill (+ new file), Video-Analyzer skill + script, Reimagined_Realms_POV_Shorts_Pipeline_v2 (`shot_list_builder.py`, `storyboard_generation.py`, both test files, `POV_Style_Guide.md`), 9 new Video-Production wiki pages + 3 cross-linked existing ones, 10 Universal_Case_Studies folders, 2 new/backfilled Reimagined-Realms case studies (Pyramid Builder backfill, new Roman Gladiator).

## Next steps
Apply the fixed pipeline to the next new POV Shorts production and keep critiquing real output against the 10-item checklist. No other open items.
