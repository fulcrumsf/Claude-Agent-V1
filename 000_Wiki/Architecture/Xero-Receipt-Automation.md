---
title: "Xero Receipt Automation"
type: wiki
category: architecture
tags:
  - xero
  - receipts
  - gmail
  - accounting
  - lab-system
created: 2026-10-10
source: 001_Architecture/Tools/Xero_Receipt_Automation/README.md
---
# Xero Receipt Automation

## What It Is

A deterministic Python pipeline that searches Gmail for receipts, scores and byte-verifies the matches, and attaches only the confident ones to **existing** Xero expense transactions. Built and promoted through the [[Lab-System|/lab system]] — Phase 1 of a larger receipt-matching project.

**Location:** `001_Architecture/Tools/Xero_Receipt_Automation/`
**Promoted:** 2026-10-10, two real `/lab-run` rounds against the live Uno Mas Creative LLC Xero tenant and two real Gmail accounts, both graded 90 (Tony). Built score 87 (`z-ai/glm-5.3`).

## The Hard Boundary (Locked, Never Changes)

The tool is write-restricted on purpose — it is an attachment assistant, not an accounting agent:

- Never creates a transaction, payment, contact, journal, or bill.
- Never changes account codes, categories, tax, amounts, dates, or reconciliation state.
- Never marks a bill paid.
- The only Xero write is `POST /Attachments/{Filename}`.
- A file only moves to `Archive/` after downloaded Xero bytes hash-match the local file.
- Xero has no attachment-delete endpoint — undo is manual, by design.

## Architecture

- `xero_receipts.py` — the deterministic pipeline: Xero calls, file handling, hashing, state machine, scoring, archive, and notification decisions.
- `SKILL_xero.md` — the Claude `/xero` layer for Gmail search and Tony's review step.
- `Weekly_Run_Prompt.md` — the Saturday 08:00 scheduled-task prompt.
- `xr_gmail_api.py` — read-only Gmail byte path. A connector-relayed text summary can propose a candidate, but only real byte evidence can let it auto-attach.
- `xr_xero_api.py` — the only network client with write access, and the only approved Xero write.
- `xr_match.py` — scoring and the `byte_evidence()` / `auto_eligible` gate (see below).
- `xr_state.py` — the item state machine (`fetched` → `scored` → `matched` → `attached`/`already_attached` → `archived`, plus `pending_review`, `verify_failed`, `rejected`). `rejected` is reclassifiable, not terminal (fixed 2026-10-10 — see "Real Bugs" below).

## Zero-Friction Mode (standing rule, 2026-10-10 evening)

Tony asked for zero terminal/chat friction on high-confidence matches. As of this session:

- `live_enabled` is **permanently `true`** in `config.example.json` — no longer toggled per run.
- `thresholds.auto_min_score` is **0.87**. A plain `run --live` does fetch → search → match → attach → verify → archive in one call; anything clearing that bar (and `auto_min_lead: 0.15`, unchanged) attaches for real with no chat approval and no terminal command.
- **Discovery is fully self-contained** — `Pipeline.search_gmail_live` (new, `xero_receipts.py`) searches every account in `gmail_accounts` directly using the tool's own Keychain OAuth, the same credentials already used for byte-fetching. The old "Claude layer writes `Gmail_Candidates.json` by hand" handoff — which only ever reached whichever single account a chat session's own Gmail connector happened to be bound to (personal, in practice) — is gone. `Run_<id>_Gmail_Candidates.json` is now an auto-generated audit record, not a required input.
- **Gmail archive is live.** Both `tony_personal` and `borednomad_business` re-authorized with `gmail.modify`. `auto_archive_enabled` gates the one Gmail write (removing `INBOX` on an already-verified receipt email that already carries a real user label) the same way `live_enabled` used to — flip on for an approved run, flip back off.
- **Known risk, by design, not a bug:** when multiple transactions share vendor/amount/date (same-day repeat charges, e.g. Kie.ai API credit auto-reloads), the matcher can't fully disambiguate — Xero's bank-transaction data carries no time-of-day (always midnight in `DateString`), only the receipt email does. A built-in dedup guard (same receipt hash proposed for more than one transaction) demotes any such pair out of auto-attach into `pending_review` instead of guessing or duplicating.

## Key Design Decision: OCR Can Verify, Never Auto-Attach

`byte_evidence()` accepts both real PDF text extraction (`confidence: "text"`) and OCR'd screenshots (`confidence: "ocr"`) for hashing and archive purposes — a screenshot receipt a human has already approved can still be byte-verified and archived. But the separate `auto_eligible` gate requires `confidence == "text"` specifically, so an OCR'd screenshot can never silently auto-attach on its own: OCR can misread a digit, real PDF text extraction can't. This was a real bug fixed during the live `/lab-run` test — before the fix, every screenshot/image receipt got `sha256: null` and always failed hash verification regardless of correctness.

## Real Bugs Found And Fixed During The Live `/lab-run`

1. `auth-gmail` didn't exist in the original build — built from scratch, mirroring the existing `auth-xero` PKCE pattern.
2. `xr_xero_api.py`'s token URL was wrong (`.../oauth/token` instead of `.../connect/token`), so every real `auth-xero` attempt got Xero's login HTML page back instead of a JSON token.
3. The env-secrets parser didn't strip a leading `export` token, so it couldn't read this workspace's actual `export KEY=value` convention in `~/.env-secrets`.
4. The OCR/byte-evidence gap above.
5. **Post-grade fix:** the `already_attached` branch (item already has a Xero attachment, hash matches, so no duplicate upload) left the item stuck — `archive()` never processed it, so the local file never moved to `Archive/`, and a later run couldn't re-pick it up either. Fixed: `already_attached` now flows into `archive()`, and the state machine allows `already_attached -> archived` / `verified_not_archived`. **This is a real gap that existed in production logic too, not a sandbox artifact.**

### Found and fixed during the first real-use session, 2026-10-10 evening

6. `attach()` uploaded the right bytes but never recomputed `record["sha256"]` from them — it trusted an upstream `byte_evidence.sha256` that `match()` doesn't always populate for manual-drop candidates, so `verify()` falsely reported a hash mismatch (`None` never equals a real hash) even when the upload was byte-perfect. Hit twice (Adobe, Spectrum), both independently confirmed correct by re-downloading the real Xero attachment and hash-comparing to the local file. Fixed: `attach()` now always computes the hash from the exact bytes it's about to upload, right before uploading. Covered by a regression test.
7. `rejected` was a genuinely terminal state (no outgoing transition in `xr_state.py`) — using `reject` to clear a wrongly-matched candidate permanently stranded the item even when it later turned out to have a real receipt waiting. Hit this incident directly: 7 items rejected, 4 of them had real receipts. Fixed: `rejected` is now reclassifiable like `no_candidate`/`pending_review`, so a later run with a different candidate can pick it back up.
8. The matcher picked the same local file for two different same-vendor/same-amount Printful transactions (Oct 6 and Oct 7, both $77.33) instead of each getting its own order-specific receipt. The correct Oct 7 file was still sitting unused in intake; attached directly via the Xero API and hash-verified. Not a systemic code fix — a one-off correction, documented in case the pattern recurs.

## Safety Rollout

`config.example.json` ships with `live_enabled: false`. A real Xero write requires both that config flag and `--live` on the command line. Tony must approve the dry-run date range and the proposed auto-attach count before any live run. The auto-attach cap is locked at 10 — raising it needs `calibration-report` evidence and Tony's explicit yes, not an agent's judgment call.

## Known Open Items (as of 2026-10-10 evening)

- The Saturday 08:00 scheduled task (`xero-receipts-weekly`) has never gotten its first manual "Run now" click.
- A handful of real transactions still have no receipt found (Adobe doesn't send a usable invoice email — Tony downloads it from the billing portal; a few vendors are "manual download only" per `Vendor_Aliases.example.json`'s `portal_hint` fields).
- Add a Gmail API row to `API_Directory.md`; mark the superseded 2026-10-03 plan archived per `Plans/README.md`.
- The matching-confidence threshold (87%) and the same-amount-collision guard are based on one night's real evidence, not weeks of production data — worth watching the first several real auto-attach runs before fully trusting it unattended.

## Resolved Since Promotion (was "Wiring Still Needed")

All of the original post-promotion wiring is done: Xero/Gmail auth connected for both the business tenant and both Gmail accounts (including `gmail.modify` for archiving); `/xero` skill registered in `Skill-Index.md`; `intake_dir`/`archive_dir` are absolute paths so the relative-path question is moot; the scheduled task exists (just needs its first run). See "Zero-Friction Mode" above for what changed on top of the original promotion.

## See Also

- [[Lab-System]] — the build pipeline this tool went through
- [[Quality-Ledger]] — the other tool promoted through the full `/lab` pipeline end to end
