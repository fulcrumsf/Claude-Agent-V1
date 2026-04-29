---
title: "Video Production Workflow (Summary)"
type: skill
domain: video-production
tags: [skill, video-production, remotion, workflow-automation, content-creation]
---

# Video Production Workflow — Summary

Source: [[../../001_Architecture/Skills/Video-Production-Workflow.md]]

End-to-end pipeline from research to publishing across all 12 YouTube channels and social platforms. Six stages:

1. **Research & Ideation** — topic selection driven by content calendar, audience demand, affiliate opportunity, and cinematic style fit. NotebookLM is invoked for factual content; sources stored in `004_Research/reference-material/[topic]/`.
2. **Scriptwriting** — full shot-listed scripts with VO timing, text callouts, and audio cues. Channel-specific length targets (e.g. 8–12 min main channel). Fact-check pass before locking.
3. **Asset Creation** — visuals split between generated (kie.ai/fal.ai per `Cinematic-Styles.md` model selection), stock, and custom. Audio (VO + music + SFX) and graphics (lower-thirds, thumbnails, transitions) created in parallel.
4. **Composition & Editing** — assembled in Remotion, with cinematic-style-driven color grading and brand-specific cut pacing.
5. **Review & Polish** — self-review and pacing pass before export.
6. **Publishing** — handoff to Blotato/scheduling layer; thumbnails A/B-tested across 3–5 variants.

The workflow is the canonical reference any new channel or department should follow before deviating.
