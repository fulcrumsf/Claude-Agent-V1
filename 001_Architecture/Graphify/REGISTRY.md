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
| Wiki | `000_Wiki/` | `000_Wiki/graphify-out/` | 125 | built | 2026-09-06T02:00Z |
| Architecture | `001_Architecture/` | `001_Architecture/graphify-out/` | 3843 | built | 2026-09-07T05:52Z|
| Video Editor | `002_Content-Creation/Video_Editor/` | `002_Content-Creation/Video_Editor/graphify-out/` | 2952 | built | 2026-09-05T22:55Z|
| Whop Clipping | `002_Content-Creation/Whop_Clipping/` | `002_Content-Creation/Whop_Clipping/graphify-out/` | 1 | pending build | — |
| Social Media | `002_Content-Creation/Social_Media_Marketing/` | `002_Content-Creation/Social_Media_Marketing/graphify-out/` | 1 | pending build | — |
| Apps | `003_Apps/` | `003_Apps/graphify-out/` | 8 | pending build | — |
| Games | `004_Games/` | `004_Games/graphify-out/` | 2 | pending build | — |
| Ecommerce | `005_Ecommerce/` | `005_Ecommerce/graphify-out/` | 4 | pending build | — |
| Affiliate Marketing | `005_Affiliate_Marketing/` | `005_Affiliate_Marketing/graphify-out/` | 36 | built | 2026-09-06T02:00Z |
| Resource Library | `007_Resource_Library/` | `007_Resource_Library/graphify-out/` | 2507 | built (v2.1 — see note) | 2026-09-06T01:30Z |

Total: 12 domains tracked (Wiki + Affiliate Marketing built 2026-09-06).

> **Resource Library build note — v2 (2026-09-06):** rebuilt after the stub-enrichment
> pass. **3,036 nodes / 1,182 edges / 1,897 communities (184 substantive)** — ~3x nodes,
> ~4x edges vs the weak v1 (1,066 / 293). Method: (1) enriched ~890 near-empty notes in
> place — `revision_stub_notes.py` re-visioned 300 screenshots, `enrich_url_stub_notes.py`
> ran Gemini web-grounded summaries on 525 links; (2) `apply_dead_stub_graphignore.py`
> excluded 1,046 hopeless stubs (garbled OCR / missing image / no signal) — still in the
> vault, just not graphed; (3) **per-subfolder `graphify extract --force --token-budget
> 16000` on all 13 subfolders, then `graphify merge-graphs`, `cluster-only`, `label`**
> (~$2.40 Gemini). The small token budget was the key fix — the whole-corpus run had
> Gemini silently omitting 67% of files from its chunk responses; per-subfolder dropped
> that to ~8–25% (still ~24% on the 3 big folders: Tools, Research, Prompts).
> Per-subfolder also fixed the v1 node-ID collisions. Sub-graphs kept at
> `007_Resource_Library/<subfolder>/graphify-out/`.
>
> **v2.1 (2026-09-06):** re-ran the 3 big folders at `--token-budget 8000` (halved from
> 16000). Omission dropped hard — Prompts 24%→3% (219→339 nodes), Research 20%→7%
> (523→700), Tools 24%→12% (1334→1687). Re-merged all 13 → **3,686 nodes / 1,622 edges /
> 2,146 communities (392 labeled)**. +$1.90 Gemini (project total ~$4.80). Tools still omits
> ~12% (mostly gumroad-mirror / `*-GITHUB` stub dupes) — acceptable, diminishing returns.
> **Rule learned:** for a docs-heavy folder, `--token-budget 8000` per-subfolder is the
> sweet spot; the 60000 default makes Gemini silently drop most files.
>
> **Cleanup closed (2026-09-07):** Tony reviewed the notes automation couldn't enrich
> (`note_review.py` → `~/Desktop/Resource_Library_Review/`). 3 junked + deleted; the
> remaining 13 (7 unreadable images, 5 YouTube links, fal.ai) are **kept as-is on
> purpose** — no further enrichment. Tools' ~12%% omission also parked. A richer visual
> review/edit tool is a future build.

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
