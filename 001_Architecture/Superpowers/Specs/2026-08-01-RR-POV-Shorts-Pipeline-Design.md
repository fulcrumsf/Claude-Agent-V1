# Reimagined Realms — POV Shorts Pipeline — Design Spec

## Purpose

A new, separate Shorts-format pipeline for the Reimagined Realms channel: vertical (9:16), historical "day in the life" POV videos — e.g. "Waking up as a peasant in medieval England," "Waking up as a pyramid builder in ancient Egypt." No dialogue — foley, ambient sound, and a themed music bed only.

This is one of potentially several future Shorts pipelines for Reimagined Realms (a separate explainer-style Shorts pipeline may follow later, covering a different format). This pipeline covers the POV format only, and does **not** replace or modify the existing long-form `Reimagined_Realms_Video_Pipeline`.

## Reference material

Two reference videos supplied by Tony (medieval peasant POV, pyramid builder POV) are analyzed once via the `Video-Analyzer` skill (see companion spec) to produce a one-time `POV_Style_Guide.md`. This pipeline reads that guide on every run; it never re-downloads or re-analyzes the references itself.

`POV_Style_Guide.md` captures: pacing (~5s/scene), POV handheld camera convention, opening-with-waking-up story convention, no-dialogue sound design approach, and text-overlay conventions (placement, sizing, drop shadow).

## Skill name / command

`Reimagined_Realms_POV_Shorts_Pipeline`, folder `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/`, invoked via `/rr-pov-shorts`.

## Video specs

- Aspect ratio: 9:16
- Resolution: 1080p (Seedance 1.5 Pro, no-audio variant)
- Minimum total duration: 65 seconds
- Scene length: ~5 seconds each
- No dialogue anywhere in the video

## Padding logic

Padding happens at the **beat-planning stage**, before any generation:
- Target ~5s/scene. If the natural story only fills enough scenes to fall short of the 65s floor (e.g. 12 scenes = 60s), insert additional day-in-life beats (more granular daily-life moments) until total scene count × ~5s ≥ 65s.
- This is a planning-time decision, not a render-time stretch/hold-frame trick — every scene in the final video is a deliberate story beat, never a padded loop or freeze.

## Per-video phases

1. **Intake** — subject definition: era + role (e.g. "medieval peasant," "pyramid builder"). Historical-accuracy notes gathered here to seed prompt generation later.
2. **Beat planning** — day-in-life scene list, ~5s/scene, padded per the logic above until ≥65s total. Opens with a waking-up beat per the style guide's convention.
3. **Shot list** — per-scene image prompt (GPT-Image-2) + video motion prompt (Seedance), POV framing, historical-accuracy details baked into prompts (not left to the model to invent).
4. **Cost estimate pause** — single locked combo (see Cost section below), presented for approval before any spend.
5. **Image generation** — GPT-Image-2 via kie.ai, one image per scene.
6. **Video generation** — Seedance 1.5 Pro, 1080p, image-to-video, per-scene ≤8s cap (matches existing Reimagined Realms convention).
7. **Sound design** (see Sound Design section below).
8. **Assembly** — concatenate scene clips into `Video_Stitched.mp4` (silent), mix in foley + music per the locked sound design.
9. **Text overlay** — Remotion pass applies the "Waking up as a ___" caption template per the style guide's placement/sizing/drop-shadow conventions. Produces `Final_v1.mp4` (see Versioning).
10. **YouTube Shorts package** — title/description/tags generated per existing Reimagined Realms conventions, adapted for Shorts.
11. **Blotato upload** — publishes to the Reimagined Realms channel (existing Blotato account, id 30323 per prior session notes — verify live before first use).

## Sound design

No dialogue means no ducking is needed — foley and music simply need to be LUFS-consistent with each other, not balanced against narration.

**Foley/ambient — per clip.** Each generated Seedance clip is run through a video-to-audio Foley model. Two candidates identified via Tool Manager research on fal.ai/WaveSpeed:
- **Mirelo SFX** (v1/v1.6, video-to-audio) — purpose-built for video-synced Foley
- **Sonilo SFX** (`v1/video-to-sfx`, `v1.1/video-to-sound-effects`) — also video-synced Foley

MMAudio v2 was considered and rejected — it blends in its own ambient/music elements, which would create jarring tonal shifts scene-to-scene across ~13 short clips. Sonilo's *video-to-video-sfx* endpoint (as opposed to its dedicated SFX endpoints above) was also rejected for per-clip use — confirmed 15-second minimum + 200-credit minimum charge per generation, making it ~3x the sticker price for our 5s clips.

**A/B test protocol (first production only):**
1. Produce a full video with Mirelo SFX foley only (no music) → `Final_v1_mirelo_test.mp4` or equivalent test naming
2. Produce a full video with Sonilo SFX foley only (no music) → equivalent test naming
3. Tony judges both, picks a winner
4. Winner is locked in as the default Foley model for all future POV productions
5. Generate Suno music for the winning video, produce a third full video (locked foley + music) → this becomes the final locked reference and `Final_v1.mp4`

**Music — once per video.** Suno (existing, proven, already integrated in the long-form Reimagined Realms `assemble.py`) generates one cohesive themed track for the full ~65s runtime in a single pass — not per-clip — avoiding tonal whiplash across short scenes.

## Deliverables / asset packaging

Standing requirement for every production, not just the test video. Nothing is destructively baked without a separately-saved, re-editable version of every component:

```
Productions/000X_Title/
├── Final_v1.mp4                     ← baked master (versioned: v1, v2, v3... per iteration)
└── Assets/
    ├── Images/                      ← per-scene GPT-Image-2 stills
    ├── Video_Clips/                 ← individual Seedance clips, one per scene
    ├── Foley_Audio/                 ← individual per-scene Foley audio (Mirelo/Sonilo)
    ├── Video_Stitched.mp4           ← all clips concatenated, silent (pre-audio, pre-text)
    ├── SFX_Full.mp3                 ← all Foley clips stitched into one track
    └── Music_Full.mp3               ← Suno track, full length
```

`Final_vN.mp4` increments on every iteration/re-render so prior versions are never overwritten.

## Cost estimate (single locked combo)

For a 65s video, 13 scenes at ~5s each:

| Item | Model | Cost |
|---|---|---|
| Images | GPT-Image-2 (kie.ai, 1K), 13× | $0.39 |
| Video | Seedance 1.5 Pro, 1080p, no-audio, 65s | $2.44 |
| Foley | Mirelo or Sonilo SFX, ~13 clips | ~$0.10 |
| Music | Suno, 1 track | $0.06 |
| **Total** | | **~$2.96/video** |

Cost is not the deciding factor for any model choice in this pipeline — quality is.

## Explicitly out of scope

- Does not replace or modify `Reimagined_Realms_Video_Pipeline` (long-form).
- Does not cover the possible future "explainer-style" Reimagined Realms Shorts pipeline — that is a separate future project with its own spec.
- No dialogue/narration/VO anywhere in this format.
