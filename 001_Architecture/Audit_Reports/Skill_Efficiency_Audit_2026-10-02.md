---
title: "Skill Efficiency Audit"
type: audit-report
domain: architecture
tags: [audit, skills, context-efficiency, graphify]
created: 2026-10-02
---

# Skill Efficiency Audit — 2026-10-02

**Live sortable table (view, sort, search):** https://claude.ai/artifact/NTPGURVhJE13RwBk7Ye7CT

Raw data backing the table: `Skill_Efficiency_Audit_2026-10-02_Data.json` (this folder) — one row per skill with `name`, `words`, `score`, `trigger`, `desc`. If the artifact link ever stops working, this JSON is the full dataset and can be re-rendered or read directly.

## Question asked

Tony asked whether Agent-OS's ~235 skills are bloating the context window, and whether a better tool exists for auto-selecting skills than the current name+description matching.

## Method

- Counted words in every `SKILL.md` under `001_Architecture/Skills/` (235 skills, median ≈1,312 words, range 29–13,009 words).
- Scored each skill 1–10 on `10 − 9×percentile(word_count)` — 10 = cheapest to load if triggered, 1 = most expensive. This measures **context cost if the skill fires**, not quality. The 4 video-pipeline skills at the bottom (Neon Parcel, Anomalous Wild, Reimagined Realms) score low *on purpose* — they're meant to load fully only when that specific pipeline runs.
- Pulled a "biggest trigger" phrase from each skill's frontmatter description (first quoted phrase, or the `Use when...` clause).
- Queried the Resource Library graphify domain + grepped `007_Resource_Library` and `000_Ingest` for any existing tool/note about skill auto-routing or context-window mitigation.

## Finding 1 — Skills are not the context problem

Claude Code already uses progressive disclosure: only a one-line name+description per skill sits in context for the whole session (the fixed, small cost). The full `SKILL.md` body only loads into context the moment a skill actually fires. Having 235 skills costs little as long as descriptions stay narrow — the lever is **trigger specificity per skill**, not skill count.

## Finding 2 — MCP servers are the real risk, not skills

Found in the vault: [`007_Resource_Library/Tools/Why-I-Stopped-Using-Mcps-In-Claude-Code-And-What-I-Use-Instead.md`](../../007_Resource_Library/Tools/Why-I-Stopped-Using-Mcps-In-Claude-Code-And-What-I-Use-Instead.md). Unlike skills, MCP tool schemas load in full for every connected server, all the time — 7 MCP servers ate 50% of a 200k context window before a single prompt. The fix described there is **MCP Launchpad** (`mcpl`, github.com/kenneth-liao/mcp-launchpad): one CLI gateway that caches all MCP tool schemas and exposes BM25 semantic search, so only 1–2 relevant tool definitions load per task instead of every schema from every server.

No equivalent dedicated "skill router" tool was found anywhere in the Resource Library or Ingest — because skills don't need one; they already work the progressive-disclosure way MCP Launchpad is trying to retrofit onto MCP.

## Open item

Evaluate whether MCP Launchpad is worth adopting for Tony's connected MCP servers specifically (not for skills). Not yet installed or tested.
