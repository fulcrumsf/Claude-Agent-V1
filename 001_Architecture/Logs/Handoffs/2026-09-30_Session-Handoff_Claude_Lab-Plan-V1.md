# Session Handoff — 2026-09-30 — Claude Code — `/lab` system, `/lab-plan` v1

**Read this first, before anything else, per the new standing rule in `CLAUDE.md`.**

## What shipped tonight

The `/lab` system: a new, explicit-trigger-only lane for non-chore, multi-step builds (new tools/pipelines), separate from Option B's answer/chore/frontier routing. A deliberately-picked, cheap OpenRouter model drafts first, inside hard containment; a strong model reviews and scores every step before anything reaches the real workspace.

**`/lab-plan` (the first of four commands) is built, tested, and live in two harnesses:**
- **Claude Code:** `001_Architecture/Skills/lab-plan/SKILL.md`. Reviewer is `opus-standard`, spawned via the Agent tool.
- **Gemini / Antigravity:** `001_Architecture/Scripts/lab_plan_gemini.py`, a self-contained script (no interactive "Gemini session follows instructions" exists — see below). Reviewer is Gemini's top Pro model via the `google-antigravity` SDK. Trigger for typing `/lab-plan` inside Antigravity's own chat: `.agents/skills/lab-plan-antigravity/SKILL.md`.
- Both share the same draft script (`001_Architecture/Scripts/lab_plan_draft.py`) and the same six-file output contract per project (`Draft_Raw.md`, `Draft_Meta.json`, `Score.json`, `Plan_Locked.md`, `Acceptance_Checks.json`, `Review.md`), saved under `001_Architecture/Lab/YYYY-MM-DD_Title_Slug/` (gitignored).

**Full design history, all four commands' specs (even the unbuilt ones):** `001_Architecture/Ongoing-Agent-OS-To-Do-List.md`, "Part 4: OpenRouter middle-lane picker" — read this before touching `/lab` further, it's the canonical source, not this handoff.

**Separately this session:** `delegate.py` reverted from `typesafe/jev-router` back to `openrouter/auto` (Tony's cost-control call) with a curated allow-list; a previously-unlimited OpenRouter key got a live $20/month cap set on openrouter.ai; the OpenRouter tutorial video fully ingested.

## What's NOT built yet — the actual next steps, in order

1. **Codex's `/lab-plan`.** Not started. Its reviewer path should be `frontier.py` (already exists, already proven elsewhere in this workspace) — same shape as the Gemini build (self-contained script, since Codex likely has the same "no session follows a skill file" limitation Gemini turned out to have — check this assumption, don't just copy it blindly).
2. **`/lab-build`.** The locked plan gets built for real, sandboxed (`codex exec -s workspace-write`, confined to one new folder inside a git worktree under `001_Architecture/Lab/`, network OFF during the build — verified genuinely off by default this session, don't re-verify unless something changed). Full containment-layer spec is in the to-do list Part 4.
3. **`/lab-run`.** Tony's own real, paid, network-on run — harness-side only, iterative (he gives notes, harness makes fixes directly, never back to the picked model), graded 0-100 by Tony himself, ≥80 required to proceed.
4. **`/lab-promote`.** Copies the new folder into the real workspace, updates `TOOLBOX.md`, wikifies, runs graphify, commits, pushes. Tony typing the command with his own description of what's being promoted IS the approval — no second confirmation gate.

## Known risks, named and not yet resolved — read before trusting `/lab-plan`'s output

- **The Gemini reviewer may be too lenient.** Its only live test gave 100/100 to a draft that had a real flaw (confused the gitignored `Lab/` staging folder for a real promoted destination) and included one acceptance check that can never fail. Needs calibration across more real runs before trusting an 80+ score from it.
- **Claude Code's `/lab-plan` has never been run live end-to-end.** The draft-script half was tested for real; the review half (spawning `opus-standard`, scoring, locking) has only been traced through. Tony explicitly said not to worry about this — he's going to use it for real himself. If something breaks on his first real run, that's expected-possible, not a sign something was missed.
- **Gemini pricing used in `lab_plan_gemini.py` is an estimate**, not confirmed against a current source. Tony confirmed his `GEMINI_API_KEY` is billed (Google Cloud Console, card on file), not free tier — so real charges are happening, just at an unverified rate.
- **Counting the Gemini review's cost against the same $2/project cap as the OpenRouter draft cost was this build's own judgment call**, not something explicitly specified before building — Tony has not been asked to confirm or reject this specifically (he did confirm the $2 cap + ask-to-raise behavior in general, just not this specific accounting choice).

## Real technical facts discovered this session, don't re-derive them

- **The standalone `gemini` CLI (`gemini -p`, interactive `gemini`, any flag combination) is permanently dead for personal Google accounts** — `IneligibleTierError`, confirmed live, unaffected by Google AI Pro or any other subscription tier. Google's own message says migrate to Antigravity. Do not try to fix this with login/auth — it's not an auth problem.
- **Antigravity's IDE chat has no headless/scriptable mode.** `antigravity-ide chat "<prompt>"` runs silently against the already-open GUI window and returns nothing capturable. This is why Gemini's `/lab-plan` is a self-contained script rather than a command-file the way Claude Code's is.
- **Antigravity's IDE only reads skills from `.agents/skills/`** (not `001_Architecture/Skills/`, not the `~/.gemini/skills` symlink) — confirmed by reading its own live system prompt during this session. Any future Antigravity-facing trigger goes there.
- **`codex exec -s workspace-write`'s sandbox has no network access by default** — tested live this session (`curl` inside it fails to resolve any host). This is load-bearing for `/lab-build`'s safety design — don't re-assume it without re-checking if Codex itself gets updated.
- **`claude -p` was broken** (expired OAuth on the programmatic flag specifically, despite normal interactive login working fine) — Tony fixed it live tonight via `claude auth login`. If it breaks again, that's the fix.
- **The `google-antigravity` Python SDK is real**, not a hallucinated package (PyPI, Google LLC, alpha, v0.1.20 at time of writing) — genuinely installed and verified working this session. Installing it bumped `protobuf` to a newer version that pip flagged as conflicting with `google-api-core`/`google-ai-generativelanguage`/etc. — checked, confirmed not actually breaking `google.generativeai` (used by Anomalous Wild's audio pipeline), but worth a second look if anything Google-API-related misbehaves later.

## One thing outside this session's own work, flagged not reviewed

A separate, parallel Antigravity session wrote its own architecture plans tonight (`001_Architecture/Plans/Multi_Agent_Bridge_MCP_Slack_Plan.md`, `001_Architecture/Plans/Agent_OS_Command_Center_Dashboard_Roadmap.md`, and its own entry in `Global_Agent_Memory.md` and in today's session log) — a "Multi-Agent Bridge" + "Command Center Dashboard" concept, unrelated to `/lab`. This Claude Code session did not write, review, or vet that work. If asked about it, say so plainly rather than treating it as reviewed.

## Housekeeping still sitting untouched (older, not from tonight)

Still on `001_Architecture/Ongoing-Agent-OS-To-Do-List.md`'s Part 3: the `Youtube_Studio_Ask_AI` case study (untracked), a stale `Character-Sheet-Generation/SKILL.md` diff, a stale `Graphify/REGISTRY.md` diff, `.tmp.driveupload/` (likely safe to delete, Tony's call). None of this blocks `/lab` work.
