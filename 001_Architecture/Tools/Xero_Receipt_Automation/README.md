# Xero Receipt Automation

This tool searches Gmail for receipts, scores them, and attaches the confident byte-verified matches to **existing** Xero expenses. The hard boundary never changes:

- Never create a transaction, payment, contact, journal, or bill.
- Never change account codes, categories, tax, amounts, dates, or reconciliation state.
- Never mark a bill paid.
- The only Xero write is `POST /Attachments/{Filename}`.
- Receipts attach only to Spend Money lines on the bank accounts listed in `eligible_bank_accounts` (Tony's two expense credit cards). Revenue and transfer accounts (Relay, Mercury, Wise, PayPal, Etsy Payment Balance) never get a receipt, whatever the score.
- Move a file into `Archive/` only after downloaded Xero bytes hash-match the local file.
- Xero has no attachment delete endpoint. Undo is manual in Xero.

### The one Gmail write (added 2026-10-10)

- The only Gmail write is **archiving**: removing the `INBOX` label from one message. Nothing else about the message changes. The tool never trashes, deletes, sends, drafts, forwards, replies, marks spam, adds labels, removes other labels, or creates or edits labels.
- It applies only to an email whose receipt is already attached **and** hash-verified in Xero (states `verified`, `verified_not_archived`, `archived`, `already_attached`). Each of these states can only be reached through a downloaded-bytes hash match. The tool never touches any other email in the inbox.
- It archives only if the message has at least one real user label (Gmail system labels such as `INBOX`, `UNREAD`, `IMPORTANT`, `STARRED`, `SENT`, `DRAFT`, `SPAM`, `TRASH`, `CHAT` and `CATEGORY_*` do not count). The label does not have to match the vendor name.
- When there is no real label, the tool leaves the email in the inbox and flags it in review: "add a Gmail filter/label for this vendor so it can be archived next time".
- Labels are re-read from the Gmail API right before the decision, and again after the write to prove `INBOX` is gone. Labels the chat connector relays are never trusted.
- Gate: `auto_archive_enabled: true` in config **and** `--live`, without `--dry-run`. This is separate from `live_enabled`, and neither flag unlocks the other.
- It needs a Gmail token with the `gmail.modify` scope (`auth-gmail --account <label> --allow-archive`). A read-only token is refused before any write.

### Etsy-integration phantom transfers

The Etsy-Xero plugin sometimes books a fake "Bank Transfer to <Store> Payment Balance" line on a bank account where nothing happened. The real charge lands on a credit card. Any line that reads "Payment Balance" or "Transfer to Etsy", on an account that is not the Etsy Payment Balance account itself, is classified `no_candidate` with a flag. It is never scored, attached, approved, or categorized; Tony deletes these lines himself in Xero. The bank-account allowlist already filters these out first; this rule is a second layer.

### Auto-reconcile: not available (checked 2026-10-10)

Tony asked for the tool to create and reconcile ("Create" + "OK") lines in Xero's Reconcile queue. Xero's public API cannot do this, and Xero says it never will. Xero's developer docs (Accounting API, "Bank Statements" page, https://developer.xero.com/documentation/api/accounting/bankstatements) state that reconciling statement lines through the API is not supported and will not be added. The same page says unreconciled statement data is not exposed by any public API. The Accounting API also has no Bank Rules endpoint. Setting `IsReconciled` on a new BankTransaction is documented only for conversion apps when no matching statement line exists. On a bank-fed account it would leave the real feed line unreconciled and double-count. The tool therefore has no reconcile code. Config refuses an `auto_reconcile_enabled` key so nobody flips a switch that cannot work. Options are listed in `Discovery_Gates.md` (G5).

## Architecture

- `xero_receipts.py` is the deterministic Python pipeline. It handles Xero, files, hashes, state, scoring, archive, the gated Gmail archive step, and notification decisions.
- `SKILL_xero.md` is the Claude `/xero` layer for Gmail search and Tony review.
- `Weekly_Run_Prompt.md` is the Saturday 08:00 Desktop scheduled-task prompt.
- `xr_gmail_api.py` is the Gmail byte path (read-only), plus the single label-removal write `remove_inbox_label`. Connector-relayed text can propose a match but can never trigger an auto-attach.
- `xr_xero_api.py` contains the Xero network client and the only approved Xero write. It also captures each Spend Money line's `BankAccount` (`review --json` shows it as `bank_account: {account_id, code, name}`; it is null for bills).

## Commands

Run `python3 xero_receipts.py --help` for the full list. The important commands are:

```bash
python3 xero_receipts.py config-check --config config.example.json
python3 xero_receipts.py auth-xero --config config.example.json
python3 xero_receipts.py run --dry-run --live --config config.example.json
python3 xero_receipts.py run --scheduled --live --config config.example.json
python3 xero_receipts.py review --config config.example.json --json
python3 xero_receipts.py gmail-archive --live --dry-run --config config.example.json --json   # preview, no writes
python3 xero_receipts.py notify-check --config config.example.json --json
```

Offline fixtures are synthetic. Use `--fixtures-dir . --offline` with the provided `Fixture_Config.json`. The fixture PDFs are rebuilt by `test_xero_receipts.py` because the repo ignores `*.pdf`.

## Safety rollout

`config.example.json` starts with `live_enabled: false` and `auto_archive_enabled: false`. A Xero write requires both `live_enabled` and `--live`. A Gmail archive requires both `auto_archive_enabled` and `--live`. `--simulate-live` only works against the offline fakes and can never bypass either flag. Flip a flag to `true` only for one approved run, then back to `false` immediately; neither is a "stays on" setting. Tony must approve the dry-run range and the proposed auto-attach count first. The attach cap is 10 and the archive cap (`max_auto_archive_per_run`) is 10. No later threshold or cap change may happen without `calibration-report` evidence and Tony's explicit yes.
