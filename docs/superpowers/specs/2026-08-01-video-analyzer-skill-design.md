# Video-Analyzer Skill — Design Spec

## Purpose

A universal, reusable skill for reverse-engineering the style, pacing, editing, and narrative content of any reference video on any channel/project. Not tied to Reimagined Realms or any single pipeline — any future pipeline that needs "analyze this video's style" gets this skill, not a bespoke script.

This is a prerequisite for the Reimagined Realms POV Shorts Pipeline (see `2026-08-01-rr-pov-shorts-pipeline-design.md`), which uses it once to build a one-time style guide from 2 reference videos. It is designed to outlive that use case.

## Why a new skill (not reusing existing tools)

Two existing tools are close but don't fit:
- `gemini_video_analysis.py` (`001_Architecture/Tools/AI-Analysis/`) — whole-video Gemini analysis (style/camera/humor/prompt potential), exposed as `/analyze-video`. Good narrative reasoning, but no per-scene timestamp breakdown and not focused on historical/narrative context recognition.
- `analyze_clips.py` (TikTok Shop pipeline) — dense frame-extraction + Qwen-VL, built for matching raw product footage to narration. Granular but literal (object/action lists), with known blind spots on subtle visual context, and tuned for product footage, not narrative reasoning.

Neither is packaged as a reusable skill, and neither combines "download + per-scene breakdown + narrative/historical context reasoning" in one place.

## Command

`/video-analyzer <youtube_url> --out <folder>`

(Distinct from the existing `/analyze-video` command, which stays as-is for its current whole-video style-analysis use case.)

## Flow

1. **Download** — `yt-dlp` saves the video to `<folder>/Video.mp4`
2. **Scene segmentation** — FFmpeg scene-change detection produces scene boundary timestamps
3. **Narrative analysis** — Gemini native video analysis (whole clip, not frame-batched) reasons about:
   - Visual description per scene
   - **What's actually happening** — narrative/historical context (era, role, activity — e.g. "POV of a shackled pyramid worker eating porridge," not just "person eating")
   - Camera type/motion (handheld POV, static, etc.)
   - Sound design cues (foley, ambient, music presence)
   - On-screen text/overlay style (placement, sizing, drop shadow, timing)
4. **Merge** — scene timestamps + Gemini narrative output combined into `<folder>/ANALYSIS.md`, one section per scene

## Output

Written to the caller-specified folder — never a hardcoded path:
- `<folder>/Video.mp4` — the downloaded source
- `<folder>/ANALYSIS.md` — per-scene breakdown

## Design constraints

- Stateless: the skill has no memory of past analyses and no fixed storage location. Every invocation is independent; the caller decides where results live (e.g. under a specific production's `References/` folder).
- No channel-specific logic. This skill must not contain any Reimagined-Realms-specific or POV-specific assumptions — those live in the pipeline that calls it.

## Out of scope (for this spec)

- Batch analysis of multiple videos in one call (single URL per invocation for now)
- Automatic style-guide synthesis across multiple analyzed videos (that synthesis step belongs to the calling pipeline, e.g. Reimagined Realms POV Shorts Pipeline's one-time setup phase)
