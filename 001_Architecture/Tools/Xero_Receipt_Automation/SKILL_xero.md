---
name: xero
---

# /xero

Run `python3 xero_receipts.py review --config config.example.json --json`, then show exactly four sections:

1. **Needs your approval**
2. **Already auto-attached this week**
3. **Manual portal lookups**
4. **No candidate / failures / verified-not-archived**

For a fresh weekly pass, run `python3 xero_receipts.py run --scheduled --live`, then execute the Gmail search plan from `Run_<id>_Search_Plan.json` using the connected Gmail connector. Use `PLAIN_TEXT` metadata, never `RAW`, and never ask a model to retype receipt bytes or amounts.

Tony's chat words are the only approval:

- `approve 3` → confirm the item, then run `approve --item 3 --by tony`, followed by attach/verify/archive with `--live`.
- `reject 3` → reject that item.
- `run now` → run the full dry-run/live pipeline as appropriate.
- `you tagged this one wrong`, `wrong receipt`, or `personal expense` → confirm the item number, then run `correct` with Tony's words verbatim.
- `snooze` → run `notify-check --ack`.

Never use any Xero or Gmail create/update/delete tool. Never call a Gmail label, trash, send, draft, forward, or reply tool. Never attach anything Tony has not approved except the pipeline's own `auto_eligible` item that passed every locked gate.
