---
title: "Higgsfield AI Faceless YouTube Pipeline"
type: wiki
category: video-production
tags:
  - higgsfield-ai
  - faceless-youtube
  - claude-mcp
  - seedance
  - content-automation
source: "[[Higgsfield-AI-Faceless-Channel-Bookmark]]"
created: 2026-06-17
---

# Higgsfield AI Faceless YouTube Pipeline

## What It Is

A fully automated faceless YouTube channel pipeline that combines Claude Fable 5 with the Higgsfield MCP to produce complete documentary-style videos — script, voiceover, music, and cinematic visuals — from a single prompt. The reference channel (Bright Side) earns ~$39,500/month using this format.

## Key Concepts

- **Claude + Higgsfield MCP** — Claude writes research-backed scripts and orchestrates generation; Higgsfield handles video, image, and voice under one roof via Seedance 2.0
- **Single-prompt video generation** — one prompt produces a full 5-minute video with consistent characters, visual style, voiceover, music, and auto-pacing (no clip-by-clip prompting)
- **High-RPM niche targeting** — Finance, Technology, and Edutainment pay the most per 1,000 views; Edutainment (Bright Side style) is evergreen and algorithm-pushed to non-subscribers
- **Channel analysis → script** — prompt Claude to analyze a target channel's hooks and structure, then write an original script in the same format
- **Auto-packaging for YouTube** — one prompt generates thumbnails (3 variants for A/B testing), title options, SEO tags, and a timestamped description
- **Demonetization safety** — AI content is allowed by YouTube; what gets flagged is zero-value spam. Claude writes unique, fact-checked scripts; Higgsfield generates original visuals. Both rules satisfied automatically
- **Scale with one prompt** — "Make me 2 more videos for this channel" triggers independent research, unique scripts, and separate visual styles per video

## The Three Master Prompts

| Step | Prompt |
|------|--------|
| Script | `Analyze the channel, scenarios, hooks and write me a script for a similar video: [channel URL]` |
| Video | `Make a 5 minute video like on the reference account using Seedance 2.0. 1080p. It's going on a faceless youtube channel.` |
| Package | `Put together a complete YouTube video package for me: prepare the thumbnails, title, and everything else needed to upload it.` |

## Setup

1. Sign up at higgsfield.ai → MCP & CLI section → copy install command
2. Claude → Settings → Connectors → Add Custom Connector → name `Higgsfield` → paste URL → Connect
3. Switch to Claude Code terminal — all generation runs here

## How Tony Uses This

Directly applicable to Tony's 12-channel YouTube operation. This pipeline eliminates the manual steps of scripting, clip generation, voiceover recording, and thumbnail creation. Edutainment documentaries are an untapped format relative to Tony's current channel mix — this workflow could spin up a new evergreen channel with minimal ongoing effort.

## Related

- [[Higgsfield-Video-Pipeline]] — Claude skills for Higgsfield prompt optimization (separate but complementary)
- [[Pipeline-Orchestration]] — broader video pipeline orchestration architecture
- [[Video_Pipeline_PDR]] — internal video pipeline design reference
