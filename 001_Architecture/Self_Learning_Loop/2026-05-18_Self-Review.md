---
title: "Self Review 2026-05-18"
type: self-review
date: 2026-05-18
---

# Self Review — 2026-05-18

## What Went Well
- Brainstorming flow led to a genuinely useful pipeline design (audio-first, modular recording)
- Correctly identified that 3 visual edits × 2 audio tracks = 6 outputs without re-cutting
- Vision analysis recommendation (Qwen-VL via OpenRouter) was practical and cost-conscious
- Caught the broken symlinks early and fixed them before installing new tools

## Mistakes Made

### API key written into .env
The most significant mistake: when setting up video-use, I sourced `~/.env-secrets` and wrote the actual ElevenLabs key value into the tool's `.env` file. This directly violates Tony's workspace security model. The correct action was to create a redirect-comment `.env` with no key values.

**Root cause:** I was following the tool's install instructions literally without checking them against workspace rules first. Should always filter install steps through Tony's workspace conventions.

## Patterns To Watch
- Always check install scripts/instructions against workspace rules before executing them
- The `.env-secrets` → redirect pattern applies to every new tool install, not just Python tools — npm packages, Docker containers, CLI tools that need env files all get the same treatment
- When fixing infrastructure (symlinks, paths), document the root cause (workspace rename) so it doesn't happen again with other tools

## What Could Be Automated
- A hook or install script that intercepts `.env` writes and replaces key values with the redirect comment template would prevent the API key mistake entirely
