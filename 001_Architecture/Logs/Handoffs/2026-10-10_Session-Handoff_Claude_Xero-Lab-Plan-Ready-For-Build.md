# Session Handoff — Claude Code — 2026-10-10
## Xero Receipt Automation — /lab-plan done, ready for /lab-build

## What's done, exactly where to pick up

**The plan is locked and fully updated. Next action for the new session: run `/lab-build` on this project — nothing else needs doing first.**

Project folder: `001_Architecture/Lab/2026-10-09_Design_Phase_1_Xero_Receipt_Automation/`

Contents, all current:
- `Score.json` — raw draft scored 61/100 (regenerate verdict), immutable, do not touch.
- `Draft_Raw.md` — the original cheap-model draft (z-ai/glm-5.3, $0.21), immutable, do not touch.
- `Plan_Locked.md` — **the actual spec to build from.** Rewritten ~80% by an opus-standard reviewer after catching real errors in the raw draft (Xero attachments API has no DELETE; Xero can't see unreconciled bank-feed lines at all; the draft's own scoring could never hit its own auto-attach threshold; it had Python trying to call Claude's Gmail connector directly, which doesn't work). Then **hand-updated by this session** after a full discovery Q&A with Tony — see "Decisions already locked in" below, all already written into this file's config block, gates table, and Open Questions section (marked RESOLVED).
- `Acceptance_Checks.json` — 17 free, offline checks (4 containment, 6 structural, 7 measured against a synthetic fixture scenario). Re-locked read-only after C07 was hand-edited to match Tony's real decisions (cap 10 not 15, `archive_gmail_sourced: false`, `notify.channel: "macos"` not `"push"`).
- `Review.md` — the reviewer's plain-language explanation of what it changed and why.
- `Handover_Xero_MCP_Research.md` — **new, built this session, not part of the original /lab-plan output.** Cross-references three independent sources (the plan's own research, a fresh GitHub README fetch, and a full Video-Analyzer pass over an ingested tutorial) that all agree: the Xero MCP server (official or self-hosted) has no attachment-upload tool, confirming the plan's direct-API write path isn't a workaround, it's the only option. Also has the live Custom Connection price ($5.45/mo, for later reference only) and exact Claude Desktop MCP-connection steps for the optional read-only wiring item. Read this before /lab-build starts, it has useful context the plan doesn't repeat.

## Decisions already locked in (do not re-ask Tony these)

From a full one-question-at-a-time discovery conversation, already written into `Plan_Locked.md`:

1. **Gmail scope, Phase 1: one account only.** `fulcrumsf@gmail.com` is the only connected Gmail connector in this workspace. Tony found no way to connect `info@borednomad.com` simultaneously. Business Gmail is an explicit Phase 2 item, not Phase 1 scope.
2. **Receipt bytes: Option A, confirmed.** Build the small read-only Gmail API fetcher (`xr_gmail_api.py`, `gmail.readonly` scope, Desktop OAuth client). Tony explicitly rejected "Gmail finds become suggestions you download yourself" — "that defeats the purpose."
3. **Archive date format: MM-DD-YYYY.** `12-05-2026` = December 5. Already the plan's default.
4. **Only manual drops get archived.** Gmail-sourced receipts that get attached do NOT get a copy in `Archive/`. (`archive_gmail_sourced: false`)
5. **Schedule: Saturday 08:00 local, confirmed.** `0 8 * * 6`. If the laptop's asleep, Desktop scheduled-task's existing catch-up-on-next-launch behavior already satisfies "run as soon as it's available."
6. **No phone push, ever.** Tony explicitly does not want phone notifications even as a side effect. `PushNotification` tool is **not used at all** in this build — the notifier calls `/usr/bin/osascript` (Mac banner) directly as the one and only channel, not as a fallback. This removed the need for the original plan's N1 discovery gate entirely (deleted from the gates table — it tested something that's now a fixed decision, not an open question).
7. **`gmail_less` vendor seed list: intentionally empty.** Tony suspects OpenAI/Claude billing may not email receipts but isn't sure and didn't want to look it up mid-conversation. Do NOT pre-seed these vendors as `gmail_less` — let real "needs manual portal lookup" results from actual runs populate `Vendor_Overrides.json` instead.
8. **Auto-attach cap: 10 per run**, not the draft's original 15.
9. **Runtime data folder approved:** `~/.config/agent-os-xero/` — Tony will create this himself at wiring time (agents can't create folders outside the workspace without his say-so; this is that say-so, already given).

## What /lab-build needs to actually do

Follow `001_Architecture/Skills/lab-build/SKILL.md`'s normal process against this project folder — nothing unusual about the mechanics. The one-new-folder target is `Xero_Receipt_Automation/`, promoted later to `001_Architecture/Tools/Xero_Receipt_Automation/`. Full file list, architecture (Claude-layer-does-Gmail-search / Python-layer-does-everything-else split, and why), state machine, scoring formula, and all 22 build steps are in `Plan_Locked.md` — it's long and detailed on purpose, read it in full before building, don't skim.

Three Discovery Gates remain genuinely open and must be tested for real during/before the build, not assumed either way (all three have a free test and a safe fallback already written into the plan, so the build doesn't block on the answer):
- **G1** (expected "no" — already corroborated three ways in the handover doc, but the plan still wants it formally recorded)
- **G3** (the Gmail API fetcher's "Testing" OAuth mode may cause 7-day token expiry, same known issue already accepted for YouTube Analytics auth — worth flagging to Tony if it bites, not silently worked around)
- **G4** (confirms Tony's real transactions are reachable as SPEND/ACCPAY by run time, i.e. he reconciles before the bot runs, not after)

## Not done / explicitly out of scope for Phase 1 — don't expand into these without asking

- Business Gmail account (`info@borednomad.com`) — Phase 2.
- Stripe/Paddle portal scraping or API — Tony handles those manually via the `000_Ingest/Xero_Receipts/` drop folder (already exists, already has a flat `Archive/` subfolder inside it, also already created by Tony — do not create either, do not add subfolders under `Archive/`).
- Applying Tony's existing Xero reconciliation templates — deferred, Xero's API can't see unreconciled bank-feed lines so there's no low-effort way to touch this in Phase 1.
- Anything that writes to Xero beyond `POST .../Attachments/{Filename}` — no PUT, no other POST, no create/update/delete of any transaction, contact, or record. This is a hard constraint in the plan's safety gates, not a style preference.

## Context on why this project exists

Supersedes `001_Architecture/Plans/Agent-OS-Xero-Receipt-Automation-Plan.md` (the original Codex-drafted plan, 2026-10-03, which assumed manual file-drop-first intake). That plan isn't deleted — `Plan_Locked.md` explicitly says what it reused from it (idempotency, state machine shape, audit trail format, security handling, phased rollout gates) and what changed (Gmail-first flow instead of manual-first, confident matches auto-attach from the first live run instead of after a full human-approved pilot, Tony's exact folder structure). Once `/lab-build` → `/lab-promote` actually ships this, the old plan file should move to `Plans/Archive/` per `Plans/README.md`'s own rule — that's in the new plan's "Wiring (Later, Tony-Approved)" list, not done yet.

## One real mistake made this session, for the record

Testing `lab_plan_draft.py --help` actually ran a real (cheap, $0.0167) draft and created a throwaway project folder `001_Architecture/Lab/2026-10-09_Help/` — the script has no `--help` flag, it took the string literally as a question. Harmless but real spend and a real folder sitting there. Flagged to Tony already; he hasn't said whether to leave it or has a preference — agents can't delete it either way, only Tony can.
