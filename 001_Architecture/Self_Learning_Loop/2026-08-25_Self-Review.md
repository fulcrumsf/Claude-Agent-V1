# 2026-08-25 Self-Review

## What went well

- The retrospective process worked as designed: asking Tony one question at a time and verifying every claim against live files (not memory) surfaced real, previously-undocumented gaps that a memory-only pass would have missed entirely (Seedance never wired into code, Remotion documented as mandatory but bypassed in practice, NotebookLM discussed but never integrated, a dead multi-channel question in a single-channel script).
- The subagent-driven-development process's two-tier review (per-task + final whole-branch) proved its value directly: the final review caught a real cost bug (native audio paid for on every Seedance clip, then ElevenLabs paying again for the same stem) that no single task's scoped diff review could have seen, because it was the interaction of two different tasks' edits (Task 2's model default + Task 6's `generate_seedance()` wiring).
- Caught and fixed a stale git-tag naming collision before it caused real damage (almost overwrote a meaningful July tag) by checking first rather than assuming a name was free.
- Handled a genuinely tricky merge-conflict scenario (main had uncommitted content beyond even the branch's merge base) by diagnosing precisely via direct file diffs before acting, rather than guessing or forcing something.

## What went wrong / could be tighter

- **Underestimated `main`'s actual state before starting implementation.** Should have checked `main` for uncommitted work and tag collisions *before* creating the worktree and building the plan, not discovered mid-implementation and again at merge time. Two separate "the worktree/checkout is missing something main has" surprises in one session is a pattern — next time, snapshot `main`'s exact state (git log, tag list, and a full `git status` count) as the very first step of any implementation-adjacent task, not something reacted to as it bites.
- **Spent real session budget hitting the platform's monthly spend limit twice** (once on a research subagent, once on a review subagent) — both recovered cleanly by pausing and resuming, no work lost, but a large multi-task subagent plan run in one sitting is expensive; worth being more upfront with Tony about that cost before committing to "fully autonomous, no check-ins" on plans this size.
- **The plan document itself assumed file content (SKILL.md sections) that turned out to be partially uncommitted** — the plan was authored by reading the live main checkout directly, which is correct, but the later worktree-based implementation didn't inherit that same view. Should flag this class of risk explicitly when a plan is authored outside the isolated environment it will later be implemented in.

## Recurring pattern across today and prior sessions

- The single highest-leverage lesson repeated again today, in a new form: **a plausible signal (a doc's claim, a worktree's inherited git history) was trusted as ground truth until directly verified against the actual live file/state.** This is the same root cause already logged from the Aug 22-24 diagram/audio/thumbnail arc (`feedback_verify_before_presenting`), now confirmed to apply just as much to infrastructure/process work (git state, doc-vs-code drift) as to generated creative assets. Worth treating as a general operating principle, not a domain-specific one.

## Open item for next session

- `pipeline_supervisor.py` has pre-existing hardcoded `/tmp/biolum_*` paths (cloned from the bioluminescence-weapon script), flagged by the final review as an out-of-scope `validate_build.py` failure. Tony asked to be reminded of this next session.
