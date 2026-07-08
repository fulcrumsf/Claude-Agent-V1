---
title: "Hyperframes Video Rendering"
type: wiki
category: video-production
tags:
  - video-editing
  - motion-graphics
  - html
  - heygen
  - animation
  - gsap
  - short-form
  - installed
created: 2026-05-18
source: 007_Resource_Library/Tools/Hyperframes-HTML-Video.md
---

# Hyperframes — HTML-Native Video Renderer

## What It Is
Hyperframes is an open-source video rendering framework by HeyGen. Compositions are written as HTML files with data attributes — no React, no proprietary DSL. Agents already speak HTML, making this ideal for AI-driven video production. Apache 2.0 licensed, no per-render fees.

## How It Works
- Define video as HTML with `data-start`, `data-duration`, `data-track-index` attributes
- Preview instantly in browser (live reload)
- Render to MP4 via headless Chrome + FFmpeg pipeline
- Deterministic: same input = identical output, every time

## What It Does
- Text overlays, subtitle animations, floating card animations
- Motion graphics and 3D assets (via Three.js adapter)
- GSAP timeline animations — seekable and frame-accurate
- Shader transitions (WebGL)
- TTS audio sync (Kokoro — runs locally, no API cost)
- Whisper transcription for captions
- Background removal (u2net)
- 50+ ready-to-use catalog blocks: social overlays, data charts, cinematic effects
- Website-to-video: give it a URL, get a video

## Hyperframes vs Remotion
Both drive headless Chrome. Key difference is authoring surface:
- **Hyperframes** → HTML + CSS + GSAP (no build step, paste and animate)
- **Remotion** → React components/TSX (requires bundler, source-available license)

Hyperframes is fully open source. Remotion requires a paid license above small-team thresholds.

## Installation (Tony's Workspace)
- **CLI:** `hyperframes` — installed globally via npm (v0.6.25)
- **Repo:** `001_Architecture/Tools/Video-Generation/Hyperframes/` (cloned, LFS test files skipped)
- **Skills installed and symlinked:**
  - `001_Architecture/Skills/hyperframes/` — composition authoring, captions, TTS, audio-reactive animation
  - `001_Architecture/Skills/hyperframes-cli/` — dev-loop: init, lint, preview, render, doctor
  - `001_Architecture/Skills/gsap/` — GSAP timelines for frame-accurate seeking
- **Invocation:** `/hyperframes`, `/hyperframes-cli`, `/gsap` in Claude Code, Codex, or Gemini

## Common Commands
```bash
npx hyperframes init my-video     # scaffold a new composition
npx hyperframes preview           # browser preview with live reload
npx hyperframes render            # render to MP4
npx hyperframes add flash-through-white  # add catalog block
```

## When To Use
- Adding text overlays, captions, or motion graphics to already-cut footage
- Building promotional announcement videos from scratch
- Website-to-video conversions
- Adding animated card effects synced to speech (BIT framework: Build → Integrate → Tune)
- After video-use has produced a clean cut and captions/branding are needed next

## Tony's Workflow Position
Hyperframes sits after video-use in the affiliate video pipeline. video-use cuts the raw footage to audio; Hyperframes adds the overlay layer (captions, CTA cards, branding). Currently not active in the TikTok affiliate workflow — will be added when analytics justify captions.

## Related
- [[Video-Production/Video-Use-Agent-Editor]] — the cutting layer that comes before Hyperframes
- [[Video-Production/Short-Form-Video-Creation-Stack]] — stack context
- [[007_Resource_Library/Tutorials/Claude-Hyperframes-V2-Video]] — BIT framework tutorial
- `001_Architecture/Tools/Video-Generation/Hyperframes/` — installed repo
