# Session Handoff — Xero Receipt Automation: /lab-run complete, ready for /lab-promote

**Date:** 2026-10-10
**Harness:** Claude Code
**Picks up from:** `2026-10-10_Session-Handoff_Claude_Xero-Lab-Plan-Ready-For-Build.md`

## Where things stand

`/lab-build` cleared at 87/100 (see that project folder's own files). This session ran `/lab-build`
→ `/lab-run` end to end with **real** credentials and **real** data (not fixtures). Round 1 was
graded by Tony at **90/100, passed, cleared for `/lab-promote`** — logged in `Run_Log.jsonl`.

**Project folder:** `001_Architecture/Lab/2026-10-09_Design_Phase_1_Xero_Receipt_Automation/`
**Build folder (in the worktree):** `Build_Worktree_1/001_Architecture/Tools/Xero_Receipt_Automation/`

## Immediate next step

Tony is about to run `/lab-promote` right after this handoff is written. **One thing the promote
step needs to know:** after Tony's grade-90 log entry, I made one more fix to the build folder at
his explicit request (see "Post-grade fix" below). If `/lab-promote` checks the folder against the
round-1 fingerprint and refuses or flags a mismatch, that's expected — explain this to Tony and
either do a fast re-confirmation/re-grade, or whatever `/lab-promote`'s own instructions say to do
in that case (I had not yet read `/lab-promote`'s skill text as of writing this).

## Credentials — all live and working

- **Xero**: PKCE app "Agent-OS Receipt Automation" (Mobile/desktop type, no client secret), redirect
  `http://localhost:5035/callback`. `XERO_CLIENT_ID` in `~/.env-secrets`. Connected tenant: **Uno Mas
  Creative LLC** (`a8b7ec28-0f11-48d2-bfd1-378033872daa`), saved in `config.example.json`'s
  `tenant_id`.
- **Gmail**: OAuth client "Agent-OS Receipt Automation Gmail" (Web application type — used only for
  its client_secret; redirect `http://localhost:5036/callback`), under the pre-existing
  `antigravity-claude-491002` Google Cloud project (NOT a new project). `GMAIL_CLIENT_ID` /
  `GMAIL_CLIENT_SECRET` in `~/.env-secrets`. Two Gmail accounts connected (both refresh tokens in
  macOS Keychain, service `agent-os-xero-gmail`):
  - `tony_personal` → `fulcrumsf@gmail.com`
  - `borednomad_business` → `info@borednomad.com` (added as a second OAuth test user 2026-10-10;
    Tony's Claude plan is under this address)
  - Both labels are in `config.example.json`'s `gmail_accounts` list.
- Gmail API scope `gmail.readonly` added to the OAuth consent screen's Data Access.
- **Important standing instruction from Tony (2026-10-10, stated firmly):** never create a new API
  key/secret/OAuth client without his explicit, specific approval for that one credential — don't
  infer blanket permission from a broader "set this up" request. Ask per-credential going forward.

## Real bugs found and fixed during `/lab-build` fix-round and `/lab-run` (all in the build folder)

1. `auth-gmail` CLI command didn't exist at all in the original build — built from scratch
   (mirrors the existing `auth-xero` PKCE flow pattern).
2. `xr_xero_api.py`'s `TOKEN_URL` was wrong (`.../oauth/token` instead of `.../connect/token`) —
   caused every real `auth-xero` attempt to get Xero's login HTML page back instead of a JSON token.
3. `xr_secrets.py`'s env-secrets parser didn't strip a leading `export ` token, so it couldn't read
   this workspace's actual `export KEY=value` convention in `~/.env-secrets` (every existing entry
   in that file uses `export`).
4. `xr_match.py`'s `byte_evidence()` only accepted extraction `confidence == "text"` (true PDF text),
   silently rejecting `"ocr"` — meaning **every screenshot/image receipt got `sha256: null`** and
   would always fail hash verification, no matter how correct. Fixed to accept both "text" and "ocr"
   confidence for byte_evidence/hashing, but added an explicit `confidence == "text"` requirement to
   the separate `auto_eligible` gate, so OCR'd screenshots can be hash-verified and archived once a
   **human approves them**, but can never silently auto-attach on their own (OCR can misread a
   digit; real PDF text extraction can't). This was validated with a real screenshot workflow test.
5. **Post-grade fix (done after Tony's 90 grade, at his explicit request):** `attach()`'s
   "already attached in Xero, hash matches" branch correctly avoided a duplicate upload, but left
   the item in the terminal `already_attached` state, which `archive()` never processed (only
   looked at `verified`). So the local file never got moved to `Archive/`, and a later run couldn't
   pick it back up either, since `fetch()` already excludes transactions Xero reports as having an
   attachment. **This is a real gap that exists in production too — not a sandbox artifact.** Fixed:
   `already_attached` now flows into `archive()` (both in `run()` and the standalone `archive`
   command), and `xr_state.py`'s transition table now allows `already_attached -> archived` /
   `verified_not_archived`. Verified: compiles clean, all 16 unit tests pass, 16/17 regression
   checks pass (the 17th, C01, only fails because of a leftover `.pytest_cache` dir from testing —
   harmless, not a real defect, Tony can delete it himself: agents can't delete files).

## Real-world validation done this session (not just fixtures)

- Pulled real Xero transactions (73 unreconciled items needing receipts) via `xero-fetch --live --dry-run`.
- Ran real Gmail searches for Adobe, Anthropic, OpenAI, Visible against the real inbox. Found one
  real match (Visible, $19.00) with no PDF attachment (HTML-only confirmation email) — correctly
  routed to `pending_review`, not auto-attached. Adobe/Anthropic/OpenAI genuinely have no matching
  receipt emails in this inbox (legitimate `no_candidate`, not a bug).
- Tested the manual-drop/screenshot workflow for real: rendered the real Visible email's exact text
  into a real PNG (OCR-verified against `tesseract`, confirmed installed at
  `/opt/homebrew/bin/tesseract`), dropped it in `000_Ingest/Xero_Receipts/`, and ran it through
  scoring. Correctly matched only the Visible transaction (not any of the other 72).
- With Tony's explicit approval, did one real live write: approved the item, flipped
  `live_enabled` to `true` temporarily (restored to `false` immediately after — it's a locked
  default pinned by acceptance check C07), and actually attached the screenshot to the real Xero
  transaction. Independently verified the downloaded bytes hash-match the local file. The file is
  now archived at `000_Ingest/Xero_Receipts/Archive/09-20-2026_Visible_19.00.png` (Tony moved it
  manually after we found bug #4 above; the post-grade fix #5 means this would now happen
  automatically on a normal run).

## Known limits / open items (honest, for whoever picks this up)

- `Vendor_Aliases.example.json` has no entry for "Visible" — it scored 0 on the vendor signal.
  Worth adding if Visible is a recurring vendor.
- Adobe doesn't send a usable monthly invoice email to this inbox — Tony says he'll handle that one
  manually (download from the Adobe billing portal himself).
- `config.example.json`'s `intake_dir`/`archive_dir` are **relative paths**
  (`000_Ingest/Xero_Receipts`), which only resolve correctly when the command is run with the
  Agent-OS root as the working directory. But `Weekly_Run_Prompt.md` says to `cd` into the tool's
  own promoted folder first — from there those same relative paths won't resolve. This is pinned by
  a **locked** acceptance check (C07) that was never touched. Every real run during this session
  used explicit absolute `--intake-dir`/`--archive-dir` overrides to work around it. **This needs a
  decision from Tony** (via `/lab-plan` revision, or some other explicit override) before the
  promoted/scheduled version can run without manual flags every time.
- Unrelated, pre-existing, NOT something I touched: the "Antigravity-ClaudeCode" (YouTube) OAuth
  client in the same Google Cloud project has two active client secrets (one from March 21, 2026
  that `~/.env-secrets`'s `YOUTUBE_CLIENT_SECRET` currently uses, one from September 17, 2026 that
  nothing in `~/.env-secrets` references). Google flags this as a standard rotation-hygiene warning.
  I did not create either secret — both predate this session. Tony's own cleanup decision.
- `~/Downloads` briefly had a Google-downloaded `client_secret_*.json` plaintext file from the OAuth
  client creation flow; Tony deleted it himself during the session (agents can't delete files).

## Read next

1. `Discovery_Gates.md` in the project folder — the fullest, most current account of all the above.
2. `Run_Log.jsonl` in the project folder — the formal round-1 grade record.
3. Whatever `/lab-promote` itself instructs once Tony runs it.
