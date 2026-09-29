---
title: "Claude Code + OpenRouter: Auto-Pick the Best Model"
type: tutorial
category: ai-agents
form: youtube-video
summary: "Step-by-step guide from a 16:50 YouTube tutorial for building a Claude Code OpenRouter model-selector skill that reads model documentation and leaderboards, schedules periodic updates, and runs cost/time comparisons across four frontier models."
url: https://www.youtube.com/watch?v=Z52I8ha35Vs
tags:
  - claude-code
  - openrouter
  - model-routing
  - agentic-ai
  - benchmarking
created: 2026-09-29
source: https://www.youtube.com/watch?v=Z52I8ha35Vs
---

# Claude Code + OpenRouter: Auto-Pick the Best Model

The tutorial shows how to stop hard-coding expensive models and instead build a Claude Code "model router" that evaluates OpenRouter documentation, rankings, and pricing before choosing a model for a task. The creator builds the skill and agent first, connects OpenRouter, schedules model-data refreshes, then compares four models against an identical Remotion video-generation prompt.

## 1. Define the Agent

Use Claude Code in VS Code and describe the target behavior:

- Create an agent and skill that acts as a model selector.
- Connect it to OpenRouter so it can use available models.
- Give it OpenRouter model documentation and leaderboard/ranking data.
- For each task, identify the best and most cost-effective model.
- Track time and cost for every model invocation.
- Optionally run multiple models in parallel for comparison.

## 2. Feed the Model Knowledge Base

The creator supplies three classes of references:

1. **OpenRouter model catalog** — `https://openrouter.ai/models`
2. **Rankings board** — both the OpenRouter rankings UI and a comprehensive external leaderboard he calls "AI Arena"
3. **Machine-readable model list** — an OpenRouter API v1 endpoint that exposes models in Markdown

Paste those links when Claude Code asks for documents. Let it read and structure the material before connecting the API.

## 3. Build Before Connecting

Build the skill and agent before adding credentials. Claude Code then leaves two setup tasks:

1. Put the OpenRouter API key in `.env`.
2. Run the generated comparison script.

## 4. Connect OpenRouter

1. Open OpenRouter.
2. Create or sign into the account.
3. Create an API key.
4. Add the key to `.env`.
5. Verify connectivity using Claude Code's generated verification steps.

OpenRouter's pricing UI also exposes model prices and rankings, but the API key is the required runtime connection.

## 5. Schedule Model Updates

The generated setup includes a scheduled task/cron job that refreshes model and ranking data weekly. The video demonstrates Windows PowerShell as administrator; the creator notes the equivalent macOS instructions can be requested from Claude Code. The point is not the exact OS command, but the refresh loop: model rankings and pricing must stay current.

## 6. Run a Controlled Benchmark

The creator opens the generated `model router` folder in his "AI agent team" and asks Claude Code to:

1. Use a Remotion or Hyperframes skill to make a 30-second video explaining how to install Claude Code.
2. Run the same task with Kimi 3.0, GPT "Sole" 5.6 Ultra, Claude Opus 5, and Claude Fable 5.
3. Record generation time.
4. Record cost using OpenRouter model pricing.

All four models receive the same prompt, so differences are attributable to model behavior rather than prompt variation.

## 7. Benchmark Results Shown in the Video

| Model | Cost | Time |
|---|---:|---:|
| Kimi / Moonshot K3 | $0.06 | 26s |
| OpenAI GPT Sole 5.6 | $0.24 | 92.8s |
| Anthropic Claude Opus 5 | $0.33 | 119s |
| Anthropic Claude Fable 5 | $0.44 | 76s |
| **Total** | **$1.09** | **parallel run** |

Qualitative review in the video:

- **Fable 5**: best-looking output, accurate, strong graphics; most expensive.
- **Opus 5**: solid and competitive; slower and $0.11 cheaper than Fable.
- **GPT Sole 5.6**: high quality with a different but appealing screen treatment.
- **Kimi 3**: best price and speed; good quality, but uses an older install command.

## 8. Practical Takeaways

- Frontier models are not always the correct default.
- A model router should select by task, quality, cost, and speed rather than brand preference.
- Machine-readable docs and leaderboards make the selection skill significantly stronger.
- A weekly refresh keeps model choices aligned with the current market.
- For validation or second opinions, run the same task through multiple models and compare time, cost, and output.

## Related Resources

- [[../../000_Wiki/AI-Agents/Jev-OpenRouter-Router]]
- `ANALYSIS.md` in this folder
- `Claude-Code-And-OpenRouter-Auto-Pick-The-Best-Model-Transcript.md`
- `Build-Prompts-From-Description.md`
- `Original-Ingest-Note.md`
