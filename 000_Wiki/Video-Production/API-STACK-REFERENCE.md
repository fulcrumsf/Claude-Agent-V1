---
title: "Anti-Gravity Agent — API Stack Reference"
type: spec
domain: video-production
tags: [spec, video-production, kie-ai, ai-agents, anomalous-wild]
---

**Source:** [[/Users/tonymacbook2025/Documents/Claude-Agent/007_Resource_Library/Docs/Video_Editor/API-STACK-REFERENCE.md]]

## Summary

Master API reference for the Anti-Gravity autonomous video production agent. Covers the full multi-channel architecture (Anomalous Wild, Board Nomad, Neon Parcel, Reimagined Realms) where each channel has a Channel Bible defining voice, style, content rules, and visual identity, and the agent loads the relevant bible per task.

The document specifies environment-variable layout (`.env`), reference-doc directory structure, and the publishing flow via Blotato (each channel maps to platform IDs). It catalogues the API integrations the agent depends on: kie.ai for video generation (Veo, Kling, Sora 2, Wan, Nano Banana, Seedream), Suno for music, plus auxiliary services for SEO/metadata and asset sourcing.

Use this reference to understand how the agent orchestrates research, scripting, asset generation, Remotion composition, and publishing across channels — and as the source of truth when wiring new APIs into the stack or onboarding a new channel.
