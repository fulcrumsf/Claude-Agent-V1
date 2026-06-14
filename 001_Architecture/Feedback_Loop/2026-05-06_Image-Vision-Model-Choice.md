---
title: "2026-05-06 Image Vision Model Choice"
type: feedback
category: architecture
tags:
  - feedback
  - vision-model
  - gpt-4o-mini
  - image-ingest
created: 2026-05-06
source: local
---

# 2026-05-06 Image Vision Model Choice

Tony prefers the ChatGPT image ingest pipeline to use OpenAI `gpt-4o-mini` as the default vision model.

Reasoning:

- lower cost than the higher-capability options
- stays inside OpenAI instead of routing through Gemini or OpenRouter
- sufficient for naming images and writing asset notes for the vault

This should remain the default unless Tony explicitly asks for a different model or a quality comparison run.
