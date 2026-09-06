---
title: "Seedance and GPT Image 2 Reference Analysis Tracker"
type: research
category: video-production
tags:
  - seedance
  - gpt-image-2
  - video-analysis
  - neon-parcel
created: 2026-08-28
source: local ingest bookmarks
---

# Video Analysis Tracker

These selected top-level `000_Ingest` bookmarks were analyzed before ingest.
The five unique analyzed source notes are now routed to the Resource Library.
The duplicate `#3` note was explicitly deleted after confirming it pointed to
the same source as `#2`.

| Selected bookmarks | Source | Status | Evidence |
|---|---|---|---|
| #2 and #3 | [Claude Replaced Higgsfield with This FREE MCP](https://www.youtube.com/watch?v=IUV8QzwIb6g) | Complete; duplicate #3 analyzed once; #2 ingested and #3 deleted | Full video, Gemini production analysis, Whisper transcript, scene keyframes, dense 0.5-second frames |
| #4 | [Create Seamless AI Films of ANY Length](https://www.youtube.com/watch?v=KxRR8uiex_s) | Complete; ingested | Full video, Gemini production analysis, Whisper transcript, scene keyframes, dense 0.5-second frames |
| #10 | [How to Turn Images into Motion Graphics using Seedance 2.0](https://www.youtube.com/watch?v=k0gSSN2A8fQ) | Complete via three sequential analysis segments; ingested | Preserved full video plus three segment analyses, transcripts, scene keyframes, and dense 0.5-second frames |
| #11 | [How to Turn Storyboards into AI Videos with GPT Image 2 + Seedance 2.0](https://www.youtube.com/watch?v=Xi9zyPTgJL8) | Complete; ingested | Full video, Gemini production analysis, Whisper transcript, scene keyframes, dense 0.5-second frames |
| #12 | [I Can't Believe ChatGPT Work Made This Whole Video From One Image](https://www.youtube.com/watch?v=tG-96mrKh8k) | Complete; ingested | Full video, Gemini production analysis, Whisper transcript, scene keyframes, dense 0.5-second frames |

## Next Gate

The outlier findings must be reviewed and approved before any skill, tool-manager,
or standard ingest updates are made.

## Model-Version Comparison Rule

The outlier review must classify every finding before adoption:

- **Seedance 1.5 Pro:** treat as first-frame plus optional last-frame generation;
  do not assume native multi-reference image support.
- **Seedance 2.0 / 2.0 Fast:** treat as the versions demonstrated by the
  storyboard, multi-reference, storyboard-splitting, and image-to-video findings
  unless the specific source identifies another version.
- **Seedance 2.5:** treat longer-duration and higher reference-count claims as
  2.5-specific and require separate live API verification before adoption.
- **GPT Image 2:** classify still-image, character-sheet, storyboard, layout,
  and prompt-expansion techniques separately from Seedance capabilities.

No newer-version capability is a valid instruction for Seedance 1.5 merely
because it appears in a Seedance-related tutorial.
