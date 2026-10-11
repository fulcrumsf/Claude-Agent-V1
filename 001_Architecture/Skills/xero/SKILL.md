---
name: xero
description: Weekly Xero receipt review for Tony. Invoke when Tony says /xero, "xero review", "what receipts need approval", "approve N", "reject N", or asks about receipts attached to Xero expenses. Front end for the promoted Xero_Receipt_Automation tool; the only Xero write it ever causes is an attachment upload — either Tony-approved, or auto-attached at ≥87% match confidence per his 2026-10-10 standing instruction — and the only Gmail write is a flag-gated archive (INBOX label removal) of already-verified receipt emails.
---

# /xero

Tool folder: `/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Xero_Receipt_Automation/` (source copy: `SKILL_xero.md` there).

Run every command from the Agent-OS root with these flags (Vendor_Aliases loads from `--fixtures-dir`, also in live mode):

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
XR=001_Architecture/Tools/Xero_Receipt_Automation
python3 $XR/xero_receipts.py review --config $XR/config.example.json --fixtures-dir $XR --json
```

Run `review --json`, then show exactly four sections:

1. **Needs your approval**
2. **Already auto-attached this week**
3. **Manual portal lookups**
4. **No candidate / failures / verified-not-archived**

Under any item whose `flags` list is non-empty, show each flag as a sub-bullet in plain words (`flagged` in the JSON lists them all). Show `bank_account.name` next to each item when present.

For a fresh weekly pass, run `python3 xero_receipts.py run --scheduled --live`. **Discovery is fully self-contained as of 2026-10-10** — the pipeline searches Gmail itself (`Pipeline.search_gmail_live`, in `xero_receipts.py`) across every account in `config.gmail_accounts` (`tony_personal` **and** `borednomad_business`) using the tool's own Keychain-stored OAuth, the same credentials `fetch_gmail_bytes` already used. It no longer needs — and no longer waits for — the chat session's own Gmail connector to write `Run_<id>_Gmail_Candidates.json` by hand; that file is now auto-generated as an audit record. The old limitation ("my chat Gmail connector only reaches `fulcrumsf@gmail.com`, never the business inbox") no longer applies to anything the *pipeline* does — it still applies to anything *you* search ad hoc in chat with the Gmail connector tool, which is a separate, narrower credential.

**Fully automatic above 87% (standing rule, 2026-10-10):** Tony wants zero terminal/chat friction for high-confidence matches. `live_enabled` is now permanently `true` (not a per-run toggle) and `thresholds.auto_min_score` is `0.87`. A plain `python3 xero_receipts.py run --live --config config.example.json` does fetch → match → attach → verify → archive in one call — any item that clears `auto_min_score` (0.87) **and** `auto_min_lead` (0.15, unchanged — guards against two same-amount items scoring close together) attaches for real with **no chat approval needed**, not just no terminal command. Show Tony what happened afterward via `review --json` / the widget; don't ask first for anything that already cleared the bar.

Tony's chat words are still the only approval for anything below that bar:

- `approve 3` → confirm the item, then run `approve --item 3 --by tony`, followed by `run --live` (or `attach --item 3 --live` + verify + archive).
- `reject 3` → reject that item. **Warning:** `rejected` is a terminal state in `xr_state.py` (no outgoing transition) — if the real receipt turns up later, don't use `reject`; just leave it `pending_review`/`no_candidate`, or an item already wrongly `rejected` needs a direct state-file fix, not a retry.
- `run now` → run the full live pipeline.
- `you tagged this one wrong`, `wrong receipt`, or `personal expense` → confirm the item number, then run `correct` with Tony's words verbatim.
- `snooze` → run `notify-check --ack`.

Never use any Xero create/update/delete tool, and never use the chat Gmail connector's write tools (label, unlabel, trash, send, draft, forward, reply, spam). Never attach anything Tony has not approved except the pipeline's own `auto_eligible` item that passed every locked gate.

**The one Gmail write (narrow exception, 2026-10-10):** the pipeline itself, never the chat connector, may **archive** a receipt email. Archiving means removing the `INBOX` label and nothing else. All of these must hold:

- The email's receipt is already attached **and** hash-verified in Xero (item state `verified`, `verified_not_archived`, `archived`, or `already_attached`). No other email in the inbox is ever touched.
- The message carries at least one real user label. Gmail system labels (`INBOX`, `UNREAD`, `IMPORTANT`, `STARRED`, `SENT`, `DRAFT`, `SPAM`, `TRASH`, `CHAT`, `CATEGORY_*`) do not count. The label does not have to match the vendor name, so don't second-guess it.
- If there is no real label, leave the email in the inbox. Review shows the flag "add a Gmail filter/label for this vendor"; pass that on to Tony.
- `auto_archive_enabled: true` in config **and** `--live`, run through `run` or `gmail-archive`. The token must carry the `gmail.modify` scope (`auth-gmail --account <label> --allow-archive`).

Still never: trash, delete, send, draft, forward, reply, mark spam, add any label, remove any label other than `INBOX`, or create, rename or delete labels.

**Auto-reconcile does not exist.** Xero's public API cannot read the Reconcile queue or Bank Rules, and cannot press "OK" on a statement line; Xero says it never will. If Tony asks the tool to reconcile, say so plainly and point to `README.md` > "Auto-reconcile". Never improvise by creating a Spend Money transaction or setting `IsReconciled`.

**Bank accounts:** receipts attach only to lines on the accounts in `eligible_bank_accounts` (Tony's two expense credit cards). An item flagged "Not on an eligible expense credit card" or "Likely a known Etsy-integration phantom transfer" is never attached. Tell Tony; he deletes phantom transfers himself in Xero.

## Operating notes (learned on the first real run, 2026-10-10)

- `--item` takes the full item id (e.g. `BankTransactions:<guid>`), not a list number. Map Tony's number to the id from `review --json`, matching vendor + amount + date.
- `approve` only works on `pending_review` items. An `auto_eligible` item (score ≥0.87, lead ≥0.15) attaches on the next `run --live` with no approval step at all — see "Fully automatic above 87%" above.
- A Xero write needs both `--live` and `live_enabled: true` in `config.example.json`; `live_enabled` is permanently `true` as of 2026-10-10 (Tony's standing instruction — zero terminal friction). The old "flip it on, flip it back off" pattern is retired for ordinary runs. If `live_enabled` is ever manually editing by anyone outside this standing rule, that's one of the few genuinely gated actions Claude Code's own permission classifier blocks a model from doing itself (tagged `[Security Weaken]`) — only Tony can flip it via his own terminal.
- A Gmail archive needs both `--live` and `auto_archive_enabled: true`; `live_enabled` does not unlock it, and it does not unlock `live_enabled`. Same discipline: preview first with `gmail-archive --live --dry-run --json`, show Tony the `would_archive` and `untagged` lists, flip the flag to `true` only for the run he approved, then back to `false` immediately. Never leave it on for scheduled runs.
- `--simulate-live` only works with `--offline` fakes; it can no longer bypass either flag on a real run.
- Items whose email has no PDF/image attachment (Google Play, Apple) can never be auto-attached. Tell Tony to download the receipt from the vendor portal and drop it in `000_Ingest/Xero_Receipts/`.
- Gmail-sourced receipts end at `verified_not_archived` because `archive_gmail_sourced` is `false` (the file stays in Gmail; `Archive/` is for manual drops). The Xero hash check is the proof.
- **`attach()` does not always populate `record["sha256"]` for manual-drop matches**, which makes `verify()` falsely fail (`None` never equals a real hash) even when the uploaded bytes are byte-perfect. Seen twice, 2026-10-10 (Adobe, Spectrum). Before assuming a real corruption: re-download the attachment via `list_attachments`/`get_attachment` and hash-compare to the local file yourself. If they match, the upload was fine — only the state record's `sha256`/`state` fields are wrong and need a direct fix. This is a real bug in `attach()`, not yet patched in code.
