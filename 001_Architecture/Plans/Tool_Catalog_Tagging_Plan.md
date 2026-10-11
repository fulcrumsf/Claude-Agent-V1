# Tool Catalog Tagging Plan

> **Date:** 2026-10-08
> **Status:** Deferred. Not a current priority — Tony is sitting on this intentionally, not stuck on it. Revisit when he's ready, don't push it.
> **Owner:** Tony
> **Related:** `001_Architecture/Plans/Tool_Catalog_Maintenance_Plan.md` (the main plan this extends — see its D9)

---

## Why this file exists, and why it's parked

This came out of a live test: Tony asked the Tool Catalog (674 tools, see `001_Architecture/Audit_Reports/*Scan_2026-10-08.md`) for an end-to-end video pipeline tool. A keyword search missed **OpenMontage** because its one-line description ("open-source audiovisual production system") doesn't contain any of the words the search used. A follow-up check of Graphify confirmed OpenMontage sits in total isolation — zero semantic edges touch it, one of 2,250 isolated single-file "communities" (89% of the whole Resource Library graph). The relation Tony expected Graphify to have already built simply doesn't exist in the graph.

That exposed the real gap: **the catalog's one-line descriptions are the only thing being searched, and they weren't written to be searched** — they were written to summarize. A plain-language "what job does this do" tag per tool would have caught OpenMontage regardless of its description wording.

**Tony's call (2026-10-08): this is real and worth fixing, but not now.** He's planning to move this whole system to something accessible from any device (laptop becomes a remote controller, not the only place the system lives), and intends to run a real vector database once that happens. Building a controlled-vocabulary tagging layer now would likely get partially superseded by that migration. He can currently find most tools he needs well enough as-is. So: **written down so it doesn't get lost, not built.**

---

## The approach, for whenever this gets picked back up

**Don't make Tony invent the vocabulary.** Bottom-up, not top-down:

1. **Propose:** a cheap classifier pass reads each tool's description (and body, where the description is thin) and proposes free-form job-tags per tool — unconstrained at this stage. "script generation," "text to video," "faceless automation," whatever fits.
2. **Normalize:** a second pass clusters and merges those proposals into one controlled list, collapsing synonyms ("text-to-video" / "txt2vid" / "video generation from text" → one canonical tag).
3. **Review:** Tony skims the finished list once — accept/merge/rename a few — instead of building it from a blank page.
4. **Apply:** re-run the classifier against the now-fixed vocabulary to tag every tool with 1–4 canonical tags (the `use_for` field in `Tool_Catalog.json`, per the main plan's schema).

**Target vocabulary size: 60–100 tags.** Reasoning: too few (15–20) collapses everything into generic buckets ("video," "AI tool") that don't narrow a search; too many (300+) reintroduces the synonym-drift problem a vocabulary is supposed to solve. ~60–100 lands around one tag per 7–10 tools at the catalog's current size (674 rows) — specific enough to be useful, not so granular it's unique per tool. Vocabulary isn't frozen at that number forever — new tags can be added later the same bottom-up way, gated so one doesn't get created for a single tool.

**Mechanism for both passes:** a cheap/fast classifier model (System One / Jev, already in the workspace's model-routing stack for exactly this kind of classification work), not a full reasoning model — this is a tagging/classification job, not an analysis job.

---

## Tags vs. a real vector database — the comparison, for the record

This was discussed live and the short version is: **tags now if this gets built at all, vector DB later — not instead of.** Full reasoning, kept here so it doesn't need to be re-derived:

| | Tags (controlled vocabulary) | Vector DB (embeddings) |
|---|---|---|
| New infrastructure needed | None — just JSON fields in the catalog already being built | Yes — an embedding index (Chroma/FAISS/sqlite-vec/hosted), a new dependency |
| Browsable by category | Yes, directly | Not natively — needs its own clustering step to get category-like groups |
| Catches genuinely novel phrasing with no vocabulary match | No — this is the real gap | Yes — this is what embeddings are actually good at |
| Legible "receipt" (what was checked, what matched) | Yes — exact tag matches are easy to show plainly | Harder — similarity scores are less intuitive to skim |
| Fits current scale (674 rows) | Yes | Overkill right now |
| Graphify's failure is evidence against this approach? | No — Graphify's search never even queries its own semantic edges; that's an implementation bug in Graphify specifically, not proof embeddings don't work | No — same note applies; a plain vector DB wouldn't have Graphify's specific bug |

**Why this is genuinely deferred and not just "the cheap option avoiding the right one":** Tony's stated direction is to move this system online and run a real vector database as part of that move. Building a tagging layer now is solving the same problem a different way, on hardware/architecture that's about to change. The honest tradeoff: tags would help today, but today isn't the priority — the online migration is where the real fix lands.

---

## What actually needs to happen when this gets picked back up

Nothing yet. When Tony says go:
1. Point back at this file and `Tool_Catalog_Maintenance_Plan.md` D9.
2. Confirm whether the online-system migration already happened (if so, skip straight to the vector DB, skip the tagging layer entirely — it was only ever the bridge).
3. If the migration hasn't happened yet and he still wants an interim fix, run the 4-step bottom-up process above.

No open decisions beyond "when." This file is a parking spot, not a to-do.
