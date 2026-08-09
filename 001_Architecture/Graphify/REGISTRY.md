---
title: "Graphify Federation Registry"
type: config
domain: architecture
tags: [config, architecture, graphify, knowledge-graph]
---

# Graphify Federation Registry

Single source of truth for Tony's federated knowledge graphs. Each domain has its own graph; this file routes queries to the right one.

`000_Ingest/` is intentionally excluded from federation. It is a temporary staging area for unsorted incoming files, not an ingested knowledge domain.

## How agents use this file

**Rule #1 in the global CLAUDE.md:** Before ANY lookup task — questions, research, "where is X", finding files, searching for concepts — read this registry, identify the relevant domain graph, then run `cd <domain> && /graphify query "your question"`. Only fall back to Grep/Read if the graph returns nothing useful.

Each graph query is ~70x cheaper than raw grep/file reads.

## Registry table

| Domain | Path | Graph location | MD files | Status | Last built |
|--------|------|----------------|----------|--------|------------|
| Daily | `000_Daily/` | `000_Daily/graphify-out/` | 1 | pending build | — |
| Project Ideas | `000_Project-Ideas/` | `000_Project-Ideas/graphify-out/` | 0 | pending build | — |
| Wiki | `000_Wiki/` | `000_Wiki/graphify-out/` | 75 | pending build | — |
| Architecture | `001_Architecture/` | `001_Architecture/graphify-out/` | 2132 | built | 2026-08-09T06:14Z|
| Video Editor | `002_Content-Creation/Video_Editor/` | `002_Content-Creation/Video_Editor/graphify-out/` | 390 | built | 2026-08-09T05:39Z|
| Whop Clipping | `002_Content-Creation/Whop_Clipping/` | `002_Content-Creation/Whop_Clipping/graphify-out/` | 1 | pending build | — |
| Social Media | `002_Content-Creation/Social_Media_Marketing/` | `002_Content-Creation/Social_Media_Marketing/graphify-out/` | 1 | pending build | — |
| Apps | `003_Apps/` | `003_Apps/graphify-out/` | 8 | pending build | — |
| Games | `004_Games/` | `004_Games/graphify-out/` | 2 | pending build | — |
| Ecommerce | `005_Ecommerce/` | `005_Ecommerce/graphify-out/` | 4 | pending build | — |
| Affiliate Marketing | `005_Affiliate_Marketing/` | `005_Affiliate_Marketing/graphify-out/` | — | not yet tracked — added 2026-07-12 after the Neon Parcel TikTok Shop Creator pipeline build; needs a full domain build in its own session | — |
| Resource Library | `007_Resource_Library/` | `007_Resource_Library/graphify-out/` | 25 | pending build | — |

Total: 12 domains tracked (11 with graphs built or pending, 1 newly added and not yet graphed).

> **Status legend:**
> - `pending build` — domain has YAML frontmatter, but graph hasn't been built yet
> - `built` — graph.json + GRAPH_REPORT.md exist; query is operational
> - `stale` — files modified since last build; run `graphify update <path>` to refresh

## Building a domain graph

The graphify skill uses parallel subagents internally to extract entities from docs. To build:

```bash
cd <domain-folder>
# In Claude Code, type the slash command:
/graphify .
```

The pipeline: detect → AST extract code → semantic extract docs (subagents) → cluster → write `graphify-out/{graph.json, GRAPH_REPORT.md, index.html}`.

To rebuild after edits (no LLM, fast):
```bash
graphify update <domain-folder>
```

## Querying

Pick the domain that covers your question, then:

```bash
cd <domain-folder>
graphify query "your question" --budget 1500
graphify path "ConceptA" "ConceptB"      # shortest connection
graphify explain "SwinTransformer"        # plain-language node summary
```

## Cross-domain query examples

| Question | Right graph |
|----------|-------------|
| "What cinematic styles do we have?" | Video Editor |
| "How does the Upkeeply data model work?" | Apps |
| "What POD brands do I run?" | Ecommerce |
| "Which Kie.ai models are cheapest?" | Resource Library |
| "What's our content strategy framework?" | Video Editor (or Architecture if business-level) |
| "How does Graphify federation work?" | Architecture |

If a question spans domains, query each relevant graph separately and merge findings — there is no single union graph by design (federation > monolith).

## Maintenance

- After substantial edits to MD files in a domain, run `graphify update <domain>` (AST-only, free)
- After major refactors or new tutorial content, rerun `/graphify . --update` (incremental semantic extract)
- Federation hooks in `001_Architecture/Graphify/hooks/` mark domains dirty on file edits and rebuild on session Stop — see `hooks/README.md`

## Files

- This registry: `001_Architecture/Graphify/REGISTRY.md`
- Federation hooks: `001_Architecture/Graphify/hooks/`
- Per-domain graphs: `<domain>/graphify-out/`
- Workspace ignore rules: `.graphifyignore` at the repo root (and any ancestor directory up to the `.git` boundary — the tool reads `.graphifyignore` files directly, not a `.graphify/` subfolder; `.graphify/.graphifyignore` is not read by the tool despite the old naming). Includes a global media exclusion (`*.mp4`, `*.png`, etc., added 2026-08-03) — graphify is scoped to text/code for the architecture "second brain," never video transcription or image vision-extraction.
