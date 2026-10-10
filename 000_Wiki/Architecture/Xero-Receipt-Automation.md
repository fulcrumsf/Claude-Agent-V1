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
- `xr_state.py` — the item state machine (`fetched` → `scored` → `matched` → `attached`/`already_attached` → `archived`, plus `pending_review`, `verify_failed`, `rejected`).

## Key Design Decision: OCR Can Verify, Never Auto-Attach

`byte_evidence()` accepts both real PDF text extraction (`confidence: "text"`) and OCR'd screenshots (`confidence: "ocr"`) for hashing and archive purposes — a screenshot receipt a human has already approved can still be byte-verified and archived. But the separate `auto_eligible` gate requires `confidence == "text"` specifically, so an OCR'd screenshot can never silently auto-attach on its own: OCR can misread a digit, real PDF text extraction can't. This was a real bug fixed during the live `/lab-run` test — before the fix, every screenshot/image receipt got `sha256: null` and always failed hash verification regardless of correctness.

## Real Bugs Found And Fixed During The Live `/lab-run`

1. `auth-gmail` didn't exist in the original build — built from scratch, mirroring the existing `auth-xero` PKCE pattern.
2. `xr_xero_api.py`'s token URL was wrong (`.../oauth/token` instead of `.../connect/token`), so every real `auth-xero` attempt got Xero's login HTML page back instead of a JSON token.
3. The env-secrets parser didn't strip a leading `export` token, so it couldn't read this workspace's actual `export KEY=value` convention in `~/.env-secrets`.
4. The OCR/byte-evidence gap above.
5. **Post-grade fix:** the `already_attached` branch (item already has a Xero attachment, hash matches, so no duplicate upload) left the item stuck — `archive()` never processed it, so the local file never moved to `Archive/`, and a later run couldn't re-pick it up either. Fixed: `already_attached` now flows into `archive()`, and the state machine allows `already_attached -> archived` / `verified_not_archived`. **This is a real gap that existed in production logic too, not a sandbox artifact.**

## Safety Rollout

`config.example.json` ships with `live_enabled: false`. A real Xero write requires both that config flag and `--live` on the command line. Tony must approve the dry-run date range and the proposed auto-attach count before any live run. The auto-attach cap is locked at 10 — raising it needs `calibration-report` evidence and Tony's explicit yes, not an agent's judgment call.

## Known Open Items

- `config.example.json`'s `intake_dir`/`archive_dir` are relative paths that only resolve correctly when run from the Agent-OS root — but `Weekly_Run_Prompt.md` says to `cd` into the promoted folder first, where they won't resolve. This needs a decision from Tony before scheduled/promoted runs can work without manual `--intake-dir`/`--archive-dir` overrides every time.
- `Vendor_Aliases.example.json` has no entry for "Visible" yet (scored 0 on the vendor signal during the live test) — worth adding if it's a recurring vendor.
- Adobe doesn't send a usable monthly invoice email to the connected inbox; Tony handles that one manually via the Adobe billing portal.

## Wiring Still Needed (Tony's To-Do, Not Part Of The Build)

- Register a Xero developer app (PKCE, Starter plan) and run `auth-xero` for any tenant beyond the one already connected this session.
- Create `~/.config/agent-os-xero/` (or name another data dir) — outside the workspace, needs Tony's approval.
- Copy `SKILL_xero.md` to `001_Architecture/Skills/xero/SKILL.md` and add `/xero` to `Skill-Index.md`.
- Decide the relative-path question above.
- Create the Saturday 08:00 scheduled task from `Weekly_Run_Prompt.md`.
- Add a Gmail API row to `API_Directory.md` if a second business-account scope is needed.
- Mark the superseded 2026-10-03 plan archived per `Plans/README.md`.

## See Also

- [[Lab-System]] — the build pipeline this tool went through
- [[Quality-Ledger]] — the other tool promoted through the full `/lab` pipeline end to end
