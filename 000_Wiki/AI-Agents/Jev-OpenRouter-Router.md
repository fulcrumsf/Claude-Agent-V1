---
title: "Jev OpenRouter Router"
type: wiki
category: ai-agents
tags:
  - jev
  - typesafe-ai
  - openrouter
  - claude-code
  - model-routing
created: 2026-09-28
source: 007_Resource_Library/Tutorials/How-To-Use-Jev-Instantly-In-Claude-Code-With-OpenRouter/
---
# Jev OpenRouter Router

## What It Is
Jev is TypeSafe AI's "System 1" decision model. It does not generate text; it answers typed questions about an input (boolean/noul, choice, score) and returns probabilities, which makes it a near-instant, near-free classifier for routing prompts, triaging files, and gating automations. It is reachable through OpenRouter (`typesafe/jev-latest` or a pinned version such as `typesafe/jev-1.13`) with a normal OpenRouter API key, so no TypeSafe waitlist or SDK is needed.

This page synthesizes three video tutorials ingested on 2026-09-27 and connects them to how Agent-OS already uses Jev for Option B model routing.

## Key Concepts
- **System 1 vs System 2**: standard LLMs (Sonnet, Opus, GPT) reason in free-form text and are slow/expensive; Jev makes snap typed decisions. Pricing quoted in the tutorials: $0.04 per 1M input tokens, output free.
- **Three output shapes**: `bool`/`noul` (yes/no), `choice` (pick one option), `score` (position on a fixed scale). Each comes back with a probability, so code can branch on it directly.
- **OpenRouter access**: export `OPENROUTER_API_KEY`, find the model at `openrouter.ai/typesafe`, and call it with curl or an SDK. The philippacsany tutorial adapts the official TypeSafe Claude Code plugin into a user-level skill (`open-router-jev-calls`) that talks to OpenRouter instead of the TypeSafe SDK, then uninstalls the official plugin to avoid collisions.
- **Level 1: pre-flight model router**: a hook (`tools/jev-router/router.mjs` in `.claude/settings.json`) classifies each incoming prompt and routes it to a cheap, standard, or frontier model; `/jev on` and `/jev off` toggle it. RoboNuggets reports roughly 45% lower session cost on a benchmark.
- **Level 2: business automation**: high-volume classification jobs (invoice fraud, email triage, content moderation, refund gating, churn scoring) run through Jev in bulk; benchmark of 150 decisions in about 1.2 s for under a cent.
- **Level 3: micro-decisions in apps**: Jev embedded client-side, e.g. Kitze's Unclutter Chrome extension classifying DOM elements to strip ads and popups.
- **3-tier Agentic OS routing (Chase AI)**: Jev sits behind a local voice bridge (Whisper STT, Kokoro TTS) and sorts requests into Tier 1 (rules/local vault lookups, no AI), Tier 2 (small fast model), Tier 3 (full Claude Code / Codex session). The memory layer follows Karpathy's `raw/ -> wiki/ -> output/` Obsidian pattern governed by `CLAUDE.md`/`AGENTS.md`, and the skill backbone turns repeated tasks into skills and then automations.

## How Tony Uses This
- Agent-OS already implements the Level 1 pattern as Option B model routing: `001_Architecture/Scripts/jev_route.py` runs as each harness's prompt hook, asks Jev (`typesafe/jev-1.13`, OpenRouter Decisions API `POST /api/alpha/decisions`, 1 s fail-open timeout) for one routing decision, and adds a hint so the cheap default model answers, a `sol-standard`/`opus-standard` subagent takes frontier work, or `delegate.py` runs chores on OpenRouter Auto Router. See `001_Architecture/Plans/Option_B_Model_Routing_Plan.md` and `001_Architecture/Tools/Jev/Jev_Guide.md`.
- The `openrouter-jev-calls` skill in `001_Architecture/Skills/openrouter-jev-calls/` is the Agent-OS version of the customized skill from the philippacsany tutorial.
- Level 2 ideas map onto ingest: a Jev first pass could tag, assign a domain, and check relevance for batches of files before a heavier model synthesizes wiki pages.
- Chase AI's three-layer OS mirrors this workspace: `raw/` is `000_Ingest/` and `007_Resource_Library/`, `wiki/` is `000_Wiki/`, `output/` is logs and content folders. Its rules of thumb (done by hand twice -> skill; works five times -> automation; anything that sends/spends/publishes keeps a human checkpoint) match the chore-worker constraints already in `AGENTS.md`.
- Note the version drift: the tutorials use the chat-completions endpoint with `typesafe/jev-latest`; Agent-OS scripts use the Decisions endpoint with `typesafe/jev-1.13`. Follow `Jev_Guide.md` for workspace code.

## Source Tutorials
- [[../../007_Resource_Library/Tutorials/How-To-Use-Jev-Instantly-In-Claude-Code-With-OpenRouter/How-To-Use-Jev-Instantly-In-Claude-Code-With-OpenRouter-Tutorial]] (philippacsany, setup via OpenRouter and a customized Claude Code skill)
- [[../../007_Resource_Library/Tutorials/Jev-Will-10x-Your-Claude-Code/Jev-Will-10x-Your-Claude-Code-Tutorial]] (RoboNuggets, three levels of Jev implementation)
- [[../../007_Resource_Library/Tutorials/This-NEW-Jev-Claude-OS-Just-Changed-Every-AI-Workflow/This-NEW-Jev-Claude-OS-Just-Changed-Every-AI-Workflow-Tutorial]] (Chase AI, three-layer Agentic OS with Jev tiered routing)
- [[../../007_Resource_Library/Tutorials/Claude-Code-And-OpenRouter-Auto-Pick-The-Best-Model/Claude-Code-And-OpenRouter-Auto-Pick-The-Best-Model-Tutorial]] (OpenRouter leaderboard-driven model router with scheduled rankings/pricing updates and a four-model benchmark)

## Related
- [[Claude-Code-Router]]
- [[Claude-Code-Self-Improving-OS]]
- [[Claude-Code-And-Karpathys-System-10000-Skills]]
- [[Claude-And-Obsidian-Full-AI-Operating-System]]
- [[PI-Harness-Pack]]
- [[Graphify]]
