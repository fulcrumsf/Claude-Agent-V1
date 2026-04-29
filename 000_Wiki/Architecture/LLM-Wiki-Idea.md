---
title: "LLM Wiki Idea (Summary)"
type: guideline
domain: architecture
tags: [guideline, architecture, ai-agents, knowledge-graph, obsidian]
---

# LLM Wiki — Summary

Source: [[../../001_Architecture/Karpahty_LLM_Wiki/LLM-Wiki-Idea.md]]

A pattern for building personal knowledge bases where an LLM incrementally maintains a persistent, interlinked wiki — instead of doing query-time RAG retrieval on every question. The LLM does all the writing, summarizing, cross-referencing, and bookkeeping; the human owns sourcing and exploration.

Three layers: **raw sources** (immutable inputs), **the wiki** (LLM-owned markdown files), and **the schema** (a CLAUDE.md or AGENTS.md telling the LLM how to operate). Three operations: **ingest** (a source touches many wiki pages), **query** (synthesized answers can be filed back as new pages), and **lint** (periodic contradiction/stale-link health checks).

Two index files keep the system navigable: `index.md` (content catalog by category) and `log.md` (append-only chronological record). At ~100 sources / hundreds of pages this works without embedding-based RAG infrastructure. Best paired with Obsidian as the reading IDE while the LLM writes.

Applies to personal goals, deep research, book companion wikis, internal team knowledge, competitive analysis, trip planning — anything where knowledge accumulates over time.

## Related

- [[Graphify]] — the on-device knowledge graph engine used to map this wiki's cross-links
