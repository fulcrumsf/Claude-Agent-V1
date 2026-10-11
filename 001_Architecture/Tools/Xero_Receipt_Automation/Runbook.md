# Xero Receipt Automation Runbook

## First setup

1. Confirm all Discovery Gates in `Discovery_Gates.md` have live results.
2. Confirm the Xero app uses the free Starter plan. Do **not** buy a Custom Connection; that is a paid pause Tony handles himself.
3. Create `~/.config/agent-os-xero/` yourself. The tool refuses to create directories.
4. Put `XERO_CLIENT_ID` in `~/.env-secrets`; never hardcode or print it.
5. Run `auth-xero`. Sign in yourself in the browser.
6. Run `xero-fetch --dry-run --live`, then `run --dry-run --live`.
7. After approving the date range and auto-attach count in chat, set `live_enabled: true`.
8. Confirm `eligible_bank_accounts` in `config.example.json` matches the real Xero account names for the two expense credit cards. Run `run --dry-run --live`. If `excluded_bank_accounts` in the summary lists Chase or Capital One, the spelling is off: copy the exact name from that list (or put the Xero `AccountID` in `account_id`). Names match ignoring case, spaces and punctuation.

## Weekly flow

1. Reconcile expenses first, in Xero. Xero's API cannot see, or reconcile, unreconciled bank-feed lines; this tool cannot auto-reconcile (see README).
2. Run `run --scheduled --live`.
3. Run `notify-check`; when it says `SEND`, run `notify --channel macos`.
4. Record delivery with `notify --sent macos`.

## Gmail archive (optional, flag-gated)

1. One time per Gmail account: `auth-gmail --account tony_personal --allow-archive` (and `borednomad_business`). Tony signs in and approves the `gmail.modify` scope. The token replaces the read-only one in the same Keychain slot.
2. Preview: `gmail-archive --live --dry-run --json`. It reads labels only. `would_archive` emails would be archived; `untagged` emails stay in the inbox until Tony adds a label or filter.
3. After Tony approves the preview in chat: set `auto_archive_enabled: true`, run `gmail-archive --live --json` (or let the approved `run --live` do it), then set it back to `false` immediately.
4. An outcome of `failed: ... read-only` means step 1 hasn't been done for that account. Nothing was written.

## Review

Run `review --json` and use `/xero`:

1. **Needs your approval** — say `approve N` to attach one item.
2. **Already auto-attached this week** — spot-check every item in Xero.
3. **Manual portal lookups** — download the receipt and drop it in `000_Ingest/Xero_Receipts/`.
4. **No candidate / failures / verified-not-archived** — inspect and retry only the failed step.
5. Any item with `flags` (no Gmail label, phantom Etsy transfer, not on an eligible card) — read the flag; none of these get attached or archived automatically.

## Corrections and undo

1. Say `correct N wrong_receipt` (or another kind) and keep your wording exact.
2. The tool writes `Corrections.jsonl` and puts that vendor on review-only for 90 days.
3. Xero cannot remove attachments through its API. Open the transaction in Xero and remove the file manually.
4. Say `removed`; `confirm-removed --item N` re-lists attachments to prove it is gone.

## Recovery

- Run `verify-state` before any manual repair.
- Dry-run is always safe: it stops after matching and performs zero Xero writes.
- A timeout after upload requires re-listing attachments before any retry.
- Keep the raw file in intake until `verify` succeeds; archive happens only after hash verification.
