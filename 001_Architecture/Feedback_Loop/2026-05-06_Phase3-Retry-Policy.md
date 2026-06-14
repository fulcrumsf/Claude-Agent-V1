---
title: "2026-05-06 Phase 3 Retry Policy"
type: feedback
category: architecture
tags:
  - feedback
  - phase-3
  - retry-policy
  - openai-429
created: 2026-05-06
source: local
---

# 2026-05-06 Phase 3 Retry Policy

Tony wants the ChatGPT image ingest pipeline to behave like a retryable batch job:

- detect which image notes still have fallback vision text
- rerun only those failed images
- break the work into smaller batches
- back off on OpenAI `429` responses instead of crashing or spamming retries

This should keep the image pass clean and prevent unnecessary reruns of notes that already have usable analysis.
