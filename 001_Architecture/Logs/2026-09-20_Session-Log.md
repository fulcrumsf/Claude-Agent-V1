---
title: "Session Log 2026-09-20/21 (Neon Parcel monkey shot, global Seedance 2 process, sheet templates, checker, Shorts 2+3)"
type: session-log
created: 2026-09-21
---
# Session Log 2026-09-20 to 2026-09-21

## Video (Neon Parcel, monkey / African messenger shot, compilation 0002)
- Sheets rebuilt through the skills (one prompt each): courier + monkey character sheets, title bars via `title_sheet.py`; environment sheet v2 kept. Prop routing rule: separate prop sheet only when it adds something (hidden side, not on a character sheet, recurs, must match).
- Storyboard v3 (contract spec) approved; videos v1-v7. **v7 = winning formula, graded B+** (storyboard + full labeled env sheet + labeled character sheets, every action beat tagged `@Image N`, CAMERA POV panel pinned). Template: `Neon_Parcel_Longform_Compilation_v2/Templates/Seedance_Winning_Prompt_Template_v7.md`.
- Upscale: Kie Topaz failed 5x (500, no credits; 4 s diagnostic too), so Magnific one-off worked -> `Data/Seedance_Mini_v7_1080p_FINAL.mp4`. New rule: Kie Topaz x2, then Magnific, then FFmpeg (`Generic_Tools/upscale_video.py`).

## Global rules / tools built (all in TOOLBOX.md)
- Seedance 2 / Mini gate: `Generic_Tools/seedance2_call.py` + `check_seedance_prompt_refs.py` + per-channel switch `seedance2_gate_config.json` (only Neon_Parcel on). Rules in Seedance-Prompting-Guide + Video_Editor/CLAUDE.md. Below Seedance 2 = start/end frame only, never references (table added to guide).
- Sheet templates: `title_sheet.py`, JSON `sheet_spec.py` (locked minimum panels + action extras, holder reference required for held panels).
- Checker: `check_sheet_hands.py` (pose-seeded wrist crops, foot filter, 80% gate, review flags), `check_depth.py`. Gaps left: finger count/deformity (model always draws 5), animals (deferred; MMPose if needed).
- Reimagined Realms: 9:16 mismatch in `batch_generate_videos.py` fixed; POV v2 documented 9:16-only + start-image mode, exempt; storyboards for long-form deferred.
- AI-disclosure line moved to the END of descriptions (Neon v2 skill).

## Publishing
- Neon Parcel Shorts Part 2 (2026-09-20) and Part 3 (2026-09-21) published to YouTube/TikTok/Instagram/Facebook. Links in `~/.claude/.../memory/project_neon_parcel_shorts_pipeline.md`.

## Pending
- Next: next Neon Parcel matrix/shot. Earlier approved shots are FINAL (no redo). Nothing committed to git (Tony decides). Session close: self-review + Global_Agent_Memory still to write on close.
