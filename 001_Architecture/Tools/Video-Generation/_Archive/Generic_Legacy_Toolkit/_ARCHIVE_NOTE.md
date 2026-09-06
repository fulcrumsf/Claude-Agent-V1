---
title: "Generic Legacy Video-Generation Toolkit (Archived)"
type: archive-note
created: 2026-09-05
status: not-in-use
---

# Generic Legacy Toolkit — ARCHIVED, NOT IN USE

These three files are the pre-channel-split "generic" video-generation tools.
They are kept here **only for possible future reuse**. Nothing in the current
pipelines imports or runs them.

## What happened

- Original layout: the tools lived flat in
  `.../Video-Generation/` and were shared by every channel.
- When the toolkit was reorganized into `Generic_Tools/` + `Channels/`, each
  active channel got its own copy of these tools.
- Three symlinks in `Generic_Tools/` (`new_video.py`,
  `providers/kie_video_gen.py`, `providers/video_stitcher.py`) were left
  pointing at the **pre-rename** workspace path
  `/Users/tonymacbook2025/Documents/Claude-Agent/...`, which no longer exists —
  so they were dead links. They were removed on 2026-09-05; this folder replaces
  them.

## Provenance of the copies here

| File | Source | Notes |
|---|---|---|
| `kie_video_gen.py` | copied from `Channels/Anomalous_Wild/` | unchanged since initial commit (Apr 7) — this *is* the original generic version |
| `video_stitcher.py` | copied from `Channels/Anomalous_Wild/` | unchanged since initial commit (Apr 7) — this *is* the original generic version |
| `new_video.py` | copied from `Channels/Anomalous_Wild/` | ⚠ the true generic version is gone; this is the Anomalous-Wild-evolved 21KB version (locked voice/CTA/narration defaults, format+duration-only intake). Keep as a starting point, not a drop-in generic. |

## Current live equivalents

- Video gen: `Generic_Tools/kie_market_api.py`, per-channel `kie_video_gen.py`
- Stitching/assembly: `Channels/Reimagined_Realms/assemble.py`, per-channel `video_stitcher.py`
- Intake: per-channel `new_video.py` (e.g. `Channels/Anomalous_Wild/new_video.py`)
