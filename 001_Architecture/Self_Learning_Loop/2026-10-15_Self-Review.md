---
title: "Self-Learning Loop — 2026-10-15"
type: self-review
domain: architecture
tags: [self-review, 2026-10-15]
---

# Self-Learning Loop — 2026-10-15

## What went wrong, honestly

- Echoed a real credential value into tool output twice in one session — once via a grep pattern broad enough to catch a bash error message containing it, once via bash's own "not a valid identifier" error echoing the exact failing text. Neither was a deliberate "print the secret" action, which is exactly why a pattern-matching classifier (Claude Code's own auto-mode gate) didn't catch either one. Root cause: didn't anticipate that diagnostic commands (grep, error output) can surface a value as a side effect even when the command's intent is innocuous.
- Early tool-category research (surfaced in the prior handoff, re-confirmed this session) kept finding things "don't exist" that did exist once actually checked against the vendor's own current docs (Composio's real auth path, Digistore24's MCP server). The gap wasn't laziness — it was trusting an assumption (the user's own, or an earlier pass's) over a fresh, specific check.

## What worked well

- Treating "real data" as a standard to defend rather than a box to check — when pushed twice on citation quality, the right move both times was removing weak claims entirely rather than patching them with slightly-better-sourced claims. The user noticed and escalated exactly because a half-fix (swap one blog for a "better" blog) would have repeated the same failure one tier up.
- Building and *proving* the credential hook rather than just writing it and asserting it works — pipe-tested the logic, live-fire-tested that it actually triggers, confirmed its relationship to an existing safety layer instead of assuming redundancy or an all-clear. This is the same discipline as the real-data standard, applied to a safety mechanism instead of a data claim.

## Pattern worth automating further

A repeated safety-relevant failure should trigger a mechanical fix (hook/script/config), not a second memory note, as its own standing rule — already captured in today's feedback log. The more general version: any correction that gets repeated twice is a signal the first fix was behavioral when it needed to be structural.
