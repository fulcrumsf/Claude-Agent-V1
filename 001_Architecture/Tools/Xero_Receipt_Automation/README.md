# Xero Receipt Automation

This tool searches Gmail for receipts, scores them, and attaches the confident byte-verified matches to **existing** Xero expenses. The hard boundary never changes:

- Never create a transaction, payment, contact, journal, or bill.
- Never change account codes, categories, tax, amounts, dates, or reconciliation state.
- Never mark a bill paid.
- The only Xero write is `POST /Attachments/{Filename}`.
- Move a file into `Archive/` only after downloaded Xero bytes hash-match the local file.
- Xero has no attachment delete endpoint. Undo is manual in Xero.

## Architecture

- `xero_receipts.py` is the deterministic Python pipeline. It handles Xero, files, hashes, state, scoring, archive, and notification decisions.
- `SKILL_xero.md` is the Claude `/xero` layer for Gmail search and Tony review.
- `Weekly_Run_Prompt.md` is the Saturday 08:00 Desktop scheduled-task prompt.
- `xr_gmail_api.py` is the read-only Gmail byte path. Connector-relayed text can propose, but never auto-attach.
- `xr_xero_api.py` contains the only network clients and the only approved Xero write.

## Commands

Run `python3 xero_receipts.py --help` for the full list. The important commands are:

```bash
python3 xero_receipts.py config-check --config config.example.json
python3 xero_receipts.py auth-xero --config config.example.json
python3 xero_receipts.py run --dry-run --live --config config.example.json
python3 xero_receipts.py run --scheduled --live --config config.example.json
python3 xero_receipts.py review --config config.example.json --json
python3 xero_receipts.py notify-check --config config.example.json --json
```

Offline fixtures are synthetic. Use `--fixtures-dir . --offline` with the provided `Fixture_Config.json`.

## Safety rollout

`config.example.json` starts with `live_enabled: false`. A Xero write requires both the config flag and `--live`. Tony must approve the dry-run range and proposed auto-attach count first. The cap is 10. No later threshold or cap change may happen without `calibration-report` evidence and Tony's explicit yes.
