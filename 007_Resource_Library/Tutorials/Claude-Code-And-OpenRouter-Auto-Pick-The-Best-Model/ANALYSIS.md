# Claude Code + OpenRouter: Auto-Pick the Best Model — Video Analysis

**Status:** Keyframe extraction was not completed in this session because the sandbox could not resolve network hosts. `yt-dlp` failed before video download; therefore no video, no extracted keyframes, and no ffmpeg-generated scene analysis are present yet. This file records the transcript-derived analysis and the intended keyframe-based sections so it can be completed after download.

## Source

- **Title:** Claude Code + OpenRouter: Auto-Pick the Best Model
- **URL:** https://www.youtube.com/watch?v=Z52I8ha35Vs
- **Duration:** approximately 16:50
- **Subject:** Claude Code skill/agent for selecting models from OpenRouter documentation, rankings, and pricing.

## Narrative Structure from Transcript

| Timestamp | Topic |
|---|---|
| 00:00 | Hook: latest expensive model was not selected; leaderboard-driven cheaper model performed comparably. |
| 00:32 | Build overview: leaderboard-driven agent that updates weekly. |
| 00:58 | Project setup: Claude Code agent and skill connected to OpenRouter. |
| 03:06 | Model-selection skill design begins. |
| 04:57 | Build references are supplied: model catalog, rankings board, AI Arena, OpenRouter API Markdown list. |
| 06:51 | Required setup: `.env` API key and comparison script. |
| 07:03 | OpenRouter API-key walkthrough. |
| 09:26 | Scheduled weekly model-data update. |
| 10:53 | Identical prompt benchmark across four models. |
| 12:30 | Cost and time results. |
| 13:20 | Qualitative output review. |
| 16:26 | Closing takeaway: use model selection for token efficiency. |

## Benchmark Data

- Kimi / Moonshot K3: $0.06, 26s
- OpenAI GPT Sole 5.6: $0.24, 92.8s
- Anthropic Claude Opus 5: $0.33, 119s
- Anthropic Claude Fable 5: $0.44, 76s
- Total: $1.09; models ran in parallel.

## Build References Named in Transcript

1. `https://openrouter.ai/models`
2. OpenRouter rankings board (exact URL not captured)
3. AI Arena leaderboard (exact URL not captured)
4. OpenRouter API v1 models list as Markdown (exact URL not captured)

See `Build-Prompts-From-Description.md` for the description-fetch result.

## Keyframes

`Keyframes/` is intentionally left empty because video download and ffmpeg scene extraction could not run. No OCR was requested or attempted. Tony may inspect keyframes directly if extraction is completed later.
