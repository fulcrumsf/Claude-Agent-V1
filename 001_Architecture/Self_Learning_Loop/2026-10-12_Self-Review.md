---
title: "Self-Review — 2026-10-12"
type: self-review
created: 2026-10-12
---

# Self-Review — 2026-10-12

## What went well

- **Background subagent delegation scaled well for this kind of work.** Five research passes ran concurrently with the main session doing direct, bounded tasks (dark-mode fix, API key test, doc edits) in between. Each subagent got a self-contained prompt with exact file paths, exact prior context, and an explicit "don't touch X" list — none of them collided or duplicated work, even when two were touching the same files in sequence.
- **Catching the subcategory-count-collision bug** by actually opening the artifact in a browser rather than trusting the read-back JSON. The bug was invisible in raw data inspection (each item's data was correct) and only showed up as a wrong number on screen. Reinforces: a UI artifact needs a real visual check, not just a data-correctness check.
- **Re-verifying instead of defending** when Tony pushed back on the 12Go "redundant" flag and on the dismissed Impact scopes. Both times the honest answer was "the first pass was incomplete," not "let me explain why I was right." Tony noticed and engaged more once he saw pushback actually changed the answer.

## What could be better

- **The original 12Go "redundant" flag shouldn't have been asserted as confidently as it was** — it conflated "12Go is technically inside the Travelpayouts brand list" with "Travelpayouts/Stay22 can actually replace what 12Go does," which are different claims. The first research pass answered the easier question and implicitly treated it as answering the harder one. Worth being more careful about this exact failure mode: technical connectivity (is X reachable through hub Y) is not the same claim as functional equivalence (does hub Y do what X does).
- **Dismissing Media Properties/Jobs Management/Invoices scopes with "no use case" without first explaining what they were** was presumptuous — Tony correctly called this out ("you're just not telling me"). Should default to explaining unfamiliar things fully before recommending for/against them, especially when the user is about to make a real configuration choice (enabling API scopes) based on the explanation.
- **This session ran very long and covered an enormous amount of ground in one continuous thread** (affiliate inventory → removal passes → API research → multiple live-data pulls → strategic decisions → scope configuration). In hindsight, a few natural break points (end of the questionnaire close-out, end of the first API audit) might have been good moments to checkpoint with a handoff, in case the session had been interrupted. Nothing was lost this time, but it's a pattern worth watching — Tony's own context window ran out before mine did.

## Pattern to watch

Tony is increasingly treating this affiliate/monetization system as a long-lived, cross-session "shared brain," not a one-off research project. That raises the bar on documentation discipline going forward: every new fact needs to land in the right durable file (not just be answered in chat) because a future session — possibly a different harness entirely — is expected to pick it up cold and know it as well as this session does.
