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

## Tooling version

- **CLI package:** `graphifyy` (double-y) — **0.9.55** as of 2026-09-05, installed on Framework Python 3.13 at `/Library/Frameworks/Python.framework/Versions/3.13/bin/graphify`. This is now the only `graphify` on PATH (a stale Homebrew 0.4.23 shadow was removed).
- **Skill copies** (`~/.claude/skills/graphify`, `~/.codex/skills/graphify`) refreshed to 0.9.55 via `graphify install --platform <claude|codex>`. Marker: `001_Architecture/Skills/graphify/.graphify_version`.
- **Resolves the prior mismatch:** the old 0.4.2 CLI had no `graphify update` / `add` / `extract` subcommands, which is why the documented refresh flow failed. 0.9.55 has the full command set — `extract`, `update`, `check-update`, `path`, `explain`, `query`, `add`, `watch`, `merge-graphs`.
- **Command model in 0.9.55:** `graphify extract <path>` = headless full extraction (AST + semantic LLM, `--force` / `--mode deep`); `graphify update <path>` = fast AST-only incremental re-extract, no LLM; `graphify check-update <path>` = cron-safe pending-work check; `/graphify . --update` (skill) = incremental semantic re-extract.
- **Node-ID scheme:** the Architecture and Video Editor graphs were built on the pre-#1504 scheme. A future `graphify extract --force` rebuild gets path-qualified node IDs (fixes same-name-file collisions). Not urgent — queries work fine as-is.

## Registry table

| Domain | Path | Graph location | MD files | Status | Last built |
|--------|------|----------------|----------|--------|------------|
| Daily | `000_Daily/` | `000_Daily/graphify-out/` | 1 | pending build | — |
| Project Ideas | `000_Project-Ideas/` | `000_Project-Ideas/graphify-out/` | 0 | pending build | — |
| Wiki | `000_Wiki/` | `000_Wiki/graphify-out/` | 75 | pending build | — |
| Architecture | `001_Architecture/` | `001_Architecture/graphify-out/` | 3726 | built | 2026-09-06T00:38Z|
| Video Editor | `002_Content-Creation/Video_Editor/` | `002_Content-Creation/Video_Editor/graphify-out/` | 2952 | built | 2026-09-05T22:55Z|
| Whop Clipping | `002_Content-Creation/Whop_Clipping/` | `002_Content-Creation/Whop_Clipping/graphify-out/` | 1 | pending build | — |
| Social Media | `002_Content-Creation/Social_Media_Marketing/` | `002_Content-Creation/Social_Media_Marketing/graphify-out/` | 1 | pending build | — |
| Apps | `003_Apps/` | `003_Apps/graphify-out/` | 8 | pending build | — |
| Games | `004_Games/` | `004_Games/graphify-out/` | 2 | pending build | — |
| Ecommerce | `005_Ecommerce/` | `005_Ecommerce/graphify-out/` | 4 | pending build | — |
| Affiliate Marketing | `005_Affiliate_Marketing/` | `005_Affiliate_Marketing/graphify-out/` | — | not yet tracked — added 2026-07-12 after the Neon Parcel TikTok Shop Creator pipeline build; needs a full domain build in its own session | — |
| Resource Library | `007_Resource_Library/` | `007_Resource_Library/graphify-out/` | 3548 | built (weak — see note) | 2026-09-05T20:54Z |

Total: 12 domains tracked (11 with graphs built or pending, 1 newly added and not yet graphed).

> **Resource Library build note (2026-09-05):** first build ran on 3,548 docs via Gemini
> ($1.46). Result is **weak**: 1,066 nodes / 293 edges / 49 real communities + 729 thin
> orphan communities. **2,653 of 3,549 files (75%) produced zero nodes** — the corpus is
> mostly thin "URL + one-line" bookmarks and old image-stub notes that have no extractable
> relationship structure. Queries on the ~900 content-rich notes work (digital products,
> Claude tooling, AI video workflows all cluster sensibly); everything else is sparse.
> **Fix path:** the deferred frontmatter enrichment pass (`form:`/`summary:` + re-vision
> the image stubs with the hardened prompt) then a `graphify extract --force` rebuild, OR
> per-subfolder `graphify extract` + `graphify merge-graphs` to fix the node-ID collisions
> (Higgsfield AI / Seedance 2.0 / Claude Code minted by multiple files, losers dropped).

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
