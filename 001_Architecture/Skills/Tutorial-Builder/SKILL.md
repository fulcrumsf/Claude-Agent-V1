---
name: Tutorial-Builder
description: Turn a past multi-session build (pipeline, tool, workflow) into a replication blueprint and video-recording concept for the Roboto Gato YouTube channel and/or a sellable/free PDF. Invoke only when Tony explicitly says something like "turn X into a tutorial" or "tutorialize the [thing]".
---

> ⚠️ **WORK IN PROGRESS — ALPHA SKELETON, NOT FINALIZED.**
> This skill is a placeholder scaffold created 2026-07-05. It has not been run against a real subject yet. Treat every section below as a working draft to be tested, broken, and rewritten through actual use — not settled logic. Do not assume the steps below are complete or correct until they've survived a real invocation.

## Purpose

Tony builds tools, pipelines, and workflows across many Claude Code sessions (sometimes 10+ sessions over 2-3 weeks). He wants a repeatable way to turn that body of work into teaching material for his **Roboto Gato** YouTube channel (Claude Code / n8n / automation build-in-public channel), which may become a PDF (sell or free lead magnet), a YouTube video, a video series, or some combination — decided per invocation, not fixed.

Long-term direction (not in scope yet — see Non-Goals): the written output eventually feeds into the `notebooklm` skill to generate a slide-style PDF, with affiliate links (Higgsfield, kie.ai, fal.ai, etc.) inserted where relevant, and eventually ties into video production skills for the actual recording.

## Trigger

**Explicit only.** Tony must name the subject directly, e.g.:
- "Turn the Reimagined Realms video pipeline into a tutorial"
- "Tutorialize the graphify federation setup"

Do not proactively suggest this skill or run it in the background. Nothing automatic.

## Scope for this alpha version

**In scope:**
1. Gather source material about the named subject across the whole workspace — not just the current session. Look in:
   - `001_Architecture/Logs/` (session logs)
   - `001_Architecture/Self_Learning_Loop/` (self-reviews)
   - `001_Architecture/Feedback_Loop/` (corrections/decisions)
   - `001_Architecture/Memory/` (Global_Agent_Memory.md, Core_Memory.md, etc.)
   - Relevant `SKILL.md` files and the actual scripts/code produced
   - Use the graphify domain graph (`001_Architecture/Graphify/REGISTRY.md`) to help locate relevant material before falling back to raw grep, per the workspace's Rule #1
2. Write a **replication blueprint** (`blueprint.md`) — a PRD-style doc detailed enough that a viewer/reader could rebuild the same pipeline themselves: what was built, why, the real decisions/dead-ends that mattered, the final architecture, the tools/stack used.
3. Write a **video concept** (`video-concept.md`) — what Tony should screen-record and talk about, mapped to the blueprint steps. Assume the viewer is a beginner ("explaining to a 7th grader who's never used Claude Code") — favor plain language over jargon in the talking points.
4. Flag an **affiliate-link opportunities** section — call out places in the material where a tool with a known Tony affiliate/discount link was used (Higgsfield, kie.ai, fal.ai, etc.), so they can be inserted later. Do not invent links — only flag tools, and only fill in a link if one is already known/documented somewhere in the workspace.

**Out of scope for this alpha (explicit non-goals):**
- No PDF rendering or design — output is markdown only
- No NotebookLM invocation yet — that handoff is a manual next step, not automated by this skill
- No video editing, recording, or motion graphics generation — that stays with the existing `video-use`, `hyperframes`, and `manim-video` skills when Tony actually gets to production
- No automatic/background triggering

## Output location

Save outputs alongside the subject being tutorialized where possible (e.g. inside that channel's `Case_Studies/` or a new `Tutorials/` subfolder) — exact convention still TBD, confirm with Tony on first real invocation.

## Open questions to resolve on first real use

- Where exactly should blueprint.md / video-concept.md live per subject?
- How much of the "dead-end/what didn't work" history should make it into the blueprint vs. just the final clean path?
- What counts as "done" gathering source material — is there a point where more session history stops adding value?
- Should this become a two-way door with the `notebooklm` skill (i.e., does Tutorial-Builder eventually call it directly), or stay a manual handoff indefinitely?

Update this file after each real invocation based on what worked, what didn't, and what Tony corrects.
