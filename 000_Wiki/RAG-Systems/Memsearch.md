---
title: "Memsearch"
type: wiki
category: rag-systems
tags:
  - memsearch
  - semantic-memory
  - vector-database
  - ai-agents
  - milvus
source: "[[007_Resource_Library/Tools/Memsearch-Cross-Platform-Semantic-Memory]]"
created: 2026-04-30
---

# Memsearch

## What It Is
Memsearch is an open-source cross-platform semantic memory library built by Zilliz. It gives AI coding agents (Claude Code, Codex, OpenCode, OpenClaw) persistent, searchable memory across sessions. Markdown files are the source of truth — Milvus acts as a rebuildable shadow index for hybrid vector + keyword search.

## Key Concepts
- **Markdown-first** — memories are plain `.md` files, human-readable and version-controllable; Milvus is derived and rebuildable
- **Cross-platform** — one memory backend shared across Claude Code, Codex CLI, OpenCode, and OpenClaw via platform-specific plugins
- **3-layer progressive recall** — search (ranked chunks) → expand (full section) → transcript (raw dialogue)
- **Hybrid search** — BM25 sparse + dense vector + RRF reranking for high-recall retrieval
- **Live sync** — file watcher auto-indexes on change; SHA-256 dedup skips unchanged content
- **Embedding options** — defaults to local ONNX (no API key, ~558 MB model); supports OpenAI, Ollama, and others
- **Milvus backends** — Milvus Lite (default, zero config), Zilliz Cloud (free tier), or self-hosted Docker

## How Tony Uses This
Potential fit for the cross-agent memory layer in this workspace. Currently `claude-mem` handles episodic memory injection. Memsearch could complement or replace it for semantic recall across Claude Code, Codex, and Gemini CLI sessions — especially useful if memory needs to be queryable by concept rather than just recency.

## Related

- [[007_Resource_Library/Tools/Memsearch-Cross-Platform-Semantic-Memory]]
- [[MemPalace]]
- [[Open-Brain]]
