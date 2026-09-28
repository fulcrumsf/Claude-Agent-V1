# Self-Review — 2026-09-28 (Option B execution session, started 2026-09-27)

## What went well

- The `subagent-driven-development` process (fresh implementer per task, dedicated task review, final whole-branch review) worked exactly as designed for the core 7-task Option B build: caught the `mcp_server_names` fail-closed gap before it shipped, and the final review found nothing further needing a second fix wave.
- Once problems moved from "build" to "live debugging," reading a product's own bundled documentation (Antigravity's `hooks.md`, Codex's subagent docs) settled two real, otherwise-unresolvable disputes about hook structure and delegation semantics, faster and more reliably than guessing from prior assumptions or from a plan written in an earlier session.
- Independently verifying claims before repeating them as fact — checking OpenRouter's real settings page instead of trusting the plan doc, checking the real router log instead of trusting "it should be routing by now," running a scoped review against a real diff instead of trusting a builder's self-report — caught every real bug found tonight. None of them would have surfaced from just reading a report.

## What went wrong, stated honestly

- **The frontier-enforcement build was a real miss, not just an "interesting failed experiment."** Dispatching `opus-deep` with a large, ambitious brief produced a genuinely clever design, but it shipped code that force-enforced on ordinary conversation (any mention of "opus"/"frontier"/"sol") and bypassed its own off-switch — live across four harnesses before anyone checked it. The controller (this session) should have insisted on a narrower first slice (one harness, one mechanism) rather than approving a brief that touched all four hooks, a new worker script, and a Gemini model-swap in one pass.
- **`frontier.py --self-test` running a real paid call was a preventable, mechanical gap** — `delegate.py` had the identical class of bug fixed hours earlier in the same session (unknown-flag handling), and the fix wasn't generalized to the new sibling script before it was trusted.
- **Repeated pattern: build first, verify second, most of the night.** The controller session did not escalate to a stronger model for the harder debugging (Antigravity's hook-location investigation, in particular) until directly told to, despite several wrong-hypothesis rounds that a fresh, stronger pass likely would have resolved faster. This was Tony's own observation, not something caught internally.
- **The OpenRouter allowlist had been reported "done" in an earlier session and was actually never saved** — a claim in a plan/log was trusted without a live check, for what turned out to be an entire session's worth of time.

## Recurring pattern across sessions (not just tonight)

Every real bug found tonight was found by *checking the actual state of something* (a settings page, a log file, a diff, a live product doc) rather than by trusting a written claim about that state — the plan's own claim, a builder's self-report, an assumption carried from an earlier session. This is the same shape of lesson as `feedback_verify_before_presenting.md` (grounded is not verified) from earlier work, applied here to infrastructure and automation rather than creative/production output. Worth treating as a standing default for any session, not a lesson specific to Option B: before repeating a claim about system state, check the system, not the note about the system.

## What to do differently next time

1. When dispatching a subagent for hook/gate/enforcement-shaped work, scope the first dispatch to one harness and one mechanism, not the full cross-harness build, so a review gate exists before the blast radius is large.
2. When a fix pattern is found in one script (e.g. `delegate.py`'s missing self-test), immediately check for the same pattern in any sibling script created in the same session, rather than assuming it's isolated.
3. Escalate to a stronger model proactively after 2 failed hypotheses on a technical investigation, rather than waiting to be told.
