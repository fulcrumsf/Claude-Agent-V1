---
title: "Graphify"
type: wiki
category: architecture
tags:
  - graphify
  - knowledge-graph
  - codebase-analysis
  - on-device
source: 007_Resource_Library/Bookmarks/Graphify-On-Device-Knowledge-Graph-Engine.md
created: 2026-04-28
---

# Graphify

## What It Is

Graphify is an on-device knowledge graph engine that turns any directory of files into a queryable, traversable graph — no cloud, no LLM required for indexing. It parses codebases, documents, PDFs, images, and meeting transcripts at the AST level, extracts entities and relationships, and builds a persistent graph that grows incrementally as files change. Unlike RAG pipelines that re-embed everything on each change, Graphify only patches the affected nodes — making it fast and practical at enterprise scale.

## Key Concepts

- **AST-level extraction** — parses 20+ languages (Python, TypeScript, Go, Rust, Java, C/C++, Swift, Kotlin, and more) plus docs, PDFs, HTML, images, and meetings into a unified graph
- **Incremental graph** — only re-processes changed files; the rest of the graph stays intact. No full rebuilds.
- **Leiden clustering** — automatically groups related nodes into communities (god-nodes) for navigating large corpora
- **On-device only** — all processing happens locally; no data leaves the machine
- **Query syntax** — `graphify query "your question"` returns traversal paths with sources and confidence scores
- **Live watcher** — `graphify watch` monitors a directory and patches the graph in real time on file changes
- **Open source** — MIT license, 31k+ GitHub stars, 230k+ downloads. Enterprise tier (multi-user, cloud/on-prem) on waitlist.

## How Tony Uses This

Graphify is the knowledge layer of the entire Claude-Agent workspace. It runs on the root directory after every ingest session, mapping relationships between wiki pages, resource files, skill docs, and department folders. Any agent (Claude Code, Codex, Antigravity) can query the graph to find related content without grepping through files. The `graphify update .` command is the final step of every ingest pipeline. The graph lives in `graphify-out/` and the `GRAPH_REPORT.md` gives agents a fast summary of god-nodes and community structure.

## Related

- [[LLM-Wiki-Idea]] — the wiki methodology Graphify supports
- [[007_Resource_Library/Bookmarks/Graphify-On-Device-Knowledge-Graph-Engine.md]] — source bookmark
- [[001_Architecture/Graphify/]] — workspace Graphify config and hooks
