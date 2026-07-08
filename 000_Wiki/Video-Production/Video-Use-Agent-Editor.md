---
title: "Video Use Agent Editor"
type: wiki
category: video-production
tags:
  - video-editing
  - ai-agents
  - ffmpeg
  - elevenlabs
  - short-form
  - affiliate
  - tiktok
  - installed
created: 2026-05-18
source: 007_Resource_Library/Tools/Video-Use-Coding-Agents.md
---

# Video Use — Agent-Driven Video Editor

## What It Is
video-use is an open-source tool from browser-use that lets any coding agent (Claude Code, Codex, Gemini) edit raw video footage through natural conversation. Drop footage in a folder, describe what you want, get `final.mp4` back. No presets, no menus — the agent reasons about the video through word-level transcripts and on-demand visual composites.

## How It Works
The LLM never watches the video. It reads it through two layers:
- **Layer 1 — Audio transcript**: ElevenLabs Scribe gives word-level timestamps, speaker diarization, and audio events packed into a ~12KB `takes_packed.md`
- **Layer 2 — Visual composite (on demand)**: `timeline_view` produces a filmstrip + waveform PNG for any time range — called only at decision points, not for every frame

Pipeline: `Transcribe → Pack → LLM Reasons → EDL → Render → Self-Eval`

The self-eval loop runs `timeline_view` at every cut boundary before showing you the output. Catches visual jumps, audio pops, hidden subtitles.

## What It Does
- Cuts filler words (`umm`, `uh`, false starts) and dead air between takes
- Auto color grades segments
- 30ms audio fades at every cut
- Burns subtitles (2-word UPPERCASE chunks, customizable)
- Generates animation overlays via Hyperframes, Remotion, Manim, or PIL
- Persists session memory in `project.md`

## Installation (Tony's Workspace)
- **Repo:** `001_Architecture/Tools/Video-Generation/Video-Use/`
- **Skill:** `001_Architecture/Skills/video-use/` (symlinked)
- **Dependencies:** Installed via `uv sync`
- **API key needed:** `ELEVENLABS_API_KEY` — load via `source ~/.env-secrets` (never stored in .env)
- **Invocation skill:** `/video-use` in Claude Code, Codex, or Gemini

## When To Use
- Raw footage → clean cut (removing silences, filler, dead takes)
- Audio-first editing: drop pre-recorded VO clips, video cuts to match
- Multi-take consolidation — uses "last take rule" by default
- Any content type: talking head, product demo, montage, tutorial

## Tony's Affiliate Video Workflow
video-use is the cutting engine for the TikTok Shop / YouTube Shorts affiliate video pipeline:
1. Tony drops 8 product footage clips + 6 pre-recorded VO clips into a folder
2. Skill analyzes clips with Qwen-VL vision (see: `analyze_clips.py`)
3. video-use cuts each audio clip to matching footage
4. 6 final 9:16 MP4s come out: 3 TikTok + 3 YouTube Shorts

## Related
- [[Video-Production/Hyperframes-Video-Rendering]] — overlay and motion graphics layer
- [[Video-Production/Short-Form-Video-Creation-Stack]] — stack context
- [[Video-Production/Video-Production-Workflow]] — full production workflow
- [[007_Resource_Library/Tutorials/Claude-Code-YouTube-Video-Editing/Claude-Code-Plus-YouTube-Video-Editing-20-000month-1.md]]
- [[001_Architecture/Skills/TikTok-Shop-Affiliate-Video/SKILL.md]] — affiliate video skill
- `001_Architecture/Tools/Video-Generation/Video-Use/` — installed repo
