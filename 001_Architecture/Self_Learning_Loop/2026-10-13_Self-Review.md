---
title: "Self-Review — 2026-10-13"
type: self-review
domain: architecture
tags: [self-review, 2026-10-13]
---

# Self-Review — 2026-10-13

## What went wrong

- **First revenue-scoring pass was LLM-opinion dressed as data.** Built a plausible-looking 0-100 scoring table before actually pulling any new numbers or citing sources. Tony caught it immediately and correctly. The fix (real pulls + cited web research) wasn't hard — it should have been the default approach from the start, not a correction-triggered redo.
- **Assumed "found existing automation" meant "reuse it."** The Ikigai pipeline draft pointed straight at n8n workflows as the build target without confirming that was the plan. Should have asked, or at minimum framed it as a proposal rather than a conclusion.
- **One wasted Agent tool call.** Tried to spawn `opus-deep` for the big multi-source research task per the router's instruction, got denied by a harness-level classifier unrelated to content, and that call is now dead weight in the transcript. Should flag this kind of denial faster and move to direct execution without re-litigating.

## What worked well

- **Binary-safe search of Antigravity's local storage** was a genuinely useful technique — treating `~/.gemini/antigravity/conversations/*.pb` and `brain/` as a real filesystem to search (rather than assuming "it's an app, I can't check its history") turned up both a real finding (the conversations are encrypted) and the actual relevant research the user half-remembered, one layer removed (the October 2025 Rube session).
- **Direct observation over inference for the mockup pattern.** Instead of describing what Tony's listings "probably" look like, actually opened two listings and read the accessibility tree for image alt-text, which gave a clean, falsifiable answer (fixed video at position 2, fixed poster at position 3) rather than a guess.
- **Researching PhotoCraft's automation surface, not just its feature list.** The useful finding wasn't "it's open source" — it was the specific gap (no ExtendScript/plugins) that determines whether Tony's existing scripts port or need rebuilding. Found that by searching specifically for "scripting automation API CLI" rather than stopping at the first general overview article.

## Patterns worth watching

- Tony is increasingly explicit that "found it" and "cited it" are not the same bar, and that bar is rising across sessions (see the `feedback_verify_before_presenting` lineage). Default to citation-first on anything resembling a comparison, score, or recommendation.
- Multiple sessions now involve digging through local app storage (Antigravity, before that various dashboard logins) to find real data the user half-remembers. This is becoming a recurring capability worth being fluent in rather than treating as a one-off.
