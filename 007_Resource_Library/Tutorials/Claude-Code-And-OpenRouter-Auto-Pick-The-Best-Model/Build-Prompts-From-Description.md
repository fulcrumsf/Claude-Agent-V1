---
title: "Build Prompts and References From Video Description"
type: tutorial
category: ai-agents
form: article
summary: "The video description links to a written build guide (Substack article by Nuno Tavares) documenting every step, setting, and gotcha for building a Claude Code + OpenRouter model-router skill/agent. This file is the full retrieved guide, kept separate from the video's own transcript/analysis."
url: https://goautomatedmarketer.substack.com/p/i-let-claude-code-pick-its-own-model
tags:
  - claude-code
  - openrouter
  - model-routing
  - build-guide
created: 2026-09-29
source: https://www.youtube.com/watch?v=Z52I8ha35Vs
---

# Build Prompts and References From Video Description

## Source

The video description reads: *"The written version of this build — every step, every setting, and what breaks: https://goautomatedmarketer.substack.com"* — that root URL is the "Automated Marketer" Substack (Nuno Tavares). The specific post matching this video, found via the publication archive, is:

**"I Let Claude Code Pick Its Own Model. The Cheapest One Did the Job for About 1/7 the Price."** — Sep 11, 2026
https://goautomatedmarketer.substack.com/p/i-let-claude-code-pick-its-own-model

Full text retrieved and reproduced below (this is the actual written build guide the video's description points to — distinct from the video's own transcript in `Claude-Code-And-OpenRouter-Auto-Pick-The-Best-Model-Transcript.md`).

## The Build, Step by Step

**Vocabulary the author uses on purpose:**
- **Skill** = a reusable set of instructions Claude loads when relevant. The "how."
- **Agent** = a worker you invoke that uses skills to get a job done. The "who."
- The router is one of each: a skill that knows how to read the model list + leaderboard, and an agent you call when you want a model picked.

### Step 1: Tell Claude Code what you want

Open a terminal, run `claude`, and describe the job. The author's dictated prompt (near-verbatim, this is the actual build prompt):

> Build a skill and an agent that act as a model selector for my projects. I'm going to give you OpenRouter's documentation for every model it has, plus a leaderboard that ranks them. Then create a scheduled task on my computer that refreshes those documents every week so we're always current. After that, run a test to make sure we're picking the best model for the task, and record the time and cost per model. Pricing is on OpenRouter. Tell me when you're ready for the documents.

Claude thinks for a minute, then asks for the links.

### Step 2: Hand it the documents

"This is the part people skip, and it's the part that makes the agent good. Don't let Claude guess what models exist. Give it the source." Paste in four links:

1. `openrouter.ai/models` — the full model list
2. OpenRouter's own rankings page — which models people actually use
3. An independent leaderboard — author used **AI Arena** ("covers a lot of models in one place")
4. OpenRouter's API model list — a machine-readable version of the catalog ("Claude eats this one up")

Claude reads all four and builds the skill + agent. The author's build produced a folder called `model-router` inside his "agent team" folder.

### Step 3: Get an OpenRouter API key

- Go to openrouter.ai, create an account
- Click **Credits**, add funds (pay-as-you-go, not covered by any Claude subscription)
- Click **Workspaces**, create one (named "laptop" in the video), then **New API key**
- Name it; optionally set expiration and a spending limit ("I skip the limit and watch the charges instead. You may want the limit.")
- Click **Create**, copy the key
- Open the `.env` file already placed in the agent's folder (Claude pre-adds a placeholder), paste the key in, save

### Step 4: Set up the weekly refresh

Keeps the router's model knowledge current (leaderboards go stale within months). Claude generates a PowerShell command (Windows) — on Mac, tell Claude you're on Mac and it gives the cron equivalent.

- Windows key → type PowerShell → right-click → Run as administrator
- Paste the first command Claude gives, hit enter (registers the scheduled task)
- Paste the second confirm command
- **Known gotcha:** the confirm step threw an error in the author's own run. Fix: copy the exact error text back into Claude Code and let it diagnose — "nine times out of ten, it's me [a typo/copy error]." Fixed in one shot.

## What the Author's Test Showed

Same prompt sent to 4 models in parallel, via the router, for a Remotion 30-second "how to install Claude Code" explainer video:

| Model | Cost | Time |
|---|---|---|
| Kimi K3 | ~$0.06 | 26s |
| GPT-5.6 Sol | ~$0.24 | ~93s |
| Opus 5 | ~$0.33 | 119s |
| Fable 5 | ~$0.44 | 76s |

Quality notes: Fable 5 "set the bar" (smooth, correct install command, wrote ~40% less code than Opus 5 to get there). Opus 5 close behind. GPT-5.6 Sol skipped one visual but added one the author liked. Kimi K3 fastest/cheapest but used an *older* version of the install command — "needs a check before it ships."

## What the Video/Article Don't Mention (found in keyframes, not in the polished text)

Two of the extracted keyframes show the author's own raw working notes (a `COMPARISON.md` open in VS Code, mid-project) that undercut the clean "$0.06 wins" headline:

- **Kimi's actual run wasn't clean.** Its first attempt burned 32k reasoning tokens, returned empty output, and cost $0.48 — before a bounded-effort retry succeeded in 26s for the ~$0.06 shown in the video. Real total spend for Kimi including the failed attempt was **$0.50–1.00 on top of** the $1.09 total the video reports. The "cheapest model" headline number is the successful retry only, not the true all-in cost.
- **The author's own caveat, verbatim from his notes:** *"my quality read comes from two sampled frames per model plus reading the source, not from watching all four end to end. Watch the MP4s before treating the ranking as settled."* — the quality comparison in the video is a first-pass impression, not a rigorous review.
- Two real bugs got fixed in `run.py` mid-test: a UTF-8 encoding crash on a `✓` character that killed stdout, and a race condition where one model's crash destroyed another model's already-generated (already-paid-for) output before it could be saved.

**Takeaway for Tony's own build:** budget for retries/failures in any real cost comparison — don't take a single-run headline number (from this video or from our own future tests) as the true cost without accounting for failed attempts.

## Confirmed Project Structure (from a file-explorer keyframe)

A keyframe of the author's actual project folder (`model-router/`) shows the real skeleton, matching the Substack article's steps concretely:

```
model-router/
├── .claude/              # agent definitions
├── logs/
├── .gitignore
├── catalog.json          # model list data
├── CLAUDE.md
├── config.json
├── core.md               # skill's core instructions
├── MODELS-CHANGELOG.md
├── MODELS.md              # the leaderboard/model reference doc
├── refresh.py             # the weekly cron/scheduled-task refresh script
└── run.py                 # the test runner (sends the same prompt to N models)
```

Also visible: `openrouter.ai/api/v1/models` is a **JSON** endpoint (not literally Markdown as the transcript describes it — "MD file" appears to be the author's shorthand for "machine-readable," not the actual format). And OpenRouter's own `/models` page surfaces several *other* purpose-built routers worth knowing about beyond plain `openrouter/auto`, seen open in a browser tab during the walkthrough: **OpenRouter Fusion** (sends a prompt to a panel of models in parallel plus web search, then a judge model synthesizes one answer — relevant to the earlier brainstorm idea of "ask two models and compare"), and **Pareto Code Router** (a tiered coding-specific router with a `min_coding_score` parameter to control how strong/expensive a coding model it picks).

Author's verdict: not literally as good as the top model, but "close enough for most sub-tasks, drafts, and first passes."

## Gotchas (author's own list)

1. **It costs real money** — OpenRouter is pay-as-you-go, separate from any Claude subscription. Set a spend limit if needed, watch the charges page.
2. **Keep Claude as the boss** — the author still runs Fable 5/Opus 5 as the orchestrator that plans work and checks results. The router is only for sub-tasks handed off, not a replacement for the orchestrator.
3. **Expect one PowerShell error** — paste it back to Claude rather than debugging by hand.

## Relevance Note for Tony's Own Build

This session's brainstorm (see `000_Wiki/AI-Agents/Jev-OpenRouter-Router.md` and `001_Architecture/Ongoing-Agent-OS-To-Do-List.md` Part 2) already reached a different conclusion than this article on one point worth flagging explicitly: **Tony's orchestrator is Sonnet 5 (cheaper baseline), not Fable 5/Opus 5 (this article's expensive baseline)** — so the cost-savings math and "worth it" threshold from this guide do not transfer directly; the delta between "the router's pick" and "just asking the orchestrator directly" is smaller in Tony's setup than in the author's. Also, the author's router genuinely lets subagents run on non-Anthropic models — mechanically that only works because his whole flow is dictated through Claude Code prompting a general-purpose build, not through the Claude Code Task-tool subagent system specifically; today's earlier design review in this workspace already established that Task-tool subagents are Anthropic-only, and an OpenRouter-model worker has to be shaped like `delegate.py`, not a Task-tool agent.
