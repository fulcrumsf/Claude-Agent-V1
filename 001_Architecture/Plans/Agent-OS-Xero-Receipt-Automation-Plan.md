# Agent-OS Xero Receipt Automation Plan
**This plan was created in OpenAI Codex. **
**Status:** Implementation handoff for Claude Code to refine with Tony, then execute in phases  
**Owner:** Tony  
**Proposed workspace:** `Agent-OS/Accounting/Xero/`  
**Version:** 1.0 — 2026-10-03

## 1. Goal and operating rule

Give Tony one reliable local inbox for receipts that still need attention. For each receipt, the system should extract useful fields, find a matching **existing** Xero transaction, upload the receipt as an attachment, confirm that Xero has the attachment, and only then move the local original into `archive/YYYY/MM/`. Anything left in `receipts_to_match/` or placed in `needs_review/` must be visible in a run summary.

**Phase 1 boundary:** Match existing transactions and attach receipts only. Do **not** create transactions, auto-reconcile bank lines, change account codes or categories, change tax treatment, mark bills paid, or alter transaction amounts or dates. Never infer that an upload succeeded solely from a request being sent. A receipt enters `archive/` only after a verified successful Xero attachment and a durable local audit record.

This is a plan, not authorization to create the proposed Agent-OS folders or move existing receipts. Agent-OS rules require Tony to approve a new folder and any new archive destination before implementation makes them. Claude Code should first compare the proposal with `AGENTS.md`, `CLAUDE.md`, the workspace map, and any existing accounting directories, then obtain that structural approval.

## 2. Scope and success criteria

### In scope for Phase 1

- Manually placed PDF, JPEG, PNG, HEIC, or other explicitly supported receipt files in an intake folder.
- Deterministic local processing and Xero API calls, with a dry-run mode.
- Text extraction or OCR, candidate search, scoring, and human review for uncertain cases.
- Attachment to an eligible existing Xero transaction after duplicate checks.
- Verification, archiving by **verified upload month**, and an append-only audit trail.
- A concise run report: new, matched, attached, archived, needs review, already attached, and failed.

### Out of scope for Phase 1

- Automatic reconciliation, coding, category or tax changes, or creation of accounting records.
- Deletion of source files, Xero attachments, or audit records.
- Autonomous approval of ambiguous matches.
- Email, mobile capture, and cloud drive watchers until the local flow is proven.

**Acceptance criteria:** A known receipt can be processed twice without duplicate upload; an uncertain receipt never uploads; an interrupted upload can be recovered safely; a successful receipt leaves intake only after verification; and every action can be traced from file hash to Xero tenant, transaction ID, attachment ID or equivalent verified evidence, time, and outcome. A dry run makes no Xero writes and moves no files.

## 3. Roles and architecture

```text
Tony drops files into receipts_to_match/
                |
                v
Claude Code: operator, run control, review queue, human summary
                |
                v
Codex-built local integration: extract -> score -> decide -> upload -> verify -> journal -> archive
                |
                v
Xero Accounting API: deterministic search and attachment operations

Optional: official Xero MCP for agent-assisted read/query tasks, if its current tools,
permissions, and behavior prove useful during discovery. The local API integration
remains the authoritative execution path for upload and verification.
```

**Claude Code** owns workflow instructions, reviews exceptions, coordinates implementation, and reports results to Tony. **Codex** is the implementation engineer for the local client, matching engine, CLI, persistence, and defect fixes. **Xero API** executes transaction reads and attachment writes using explicit IDs. **Xero MCP** is optional for exploratory lookups and operator convenience; do not make production behavior depend on a capability that has not been verified in the installed MCP version. Claude Code should inspect the current official Xero documentation and MCP tool list during discovery before choosing endpoints, scopes, upload limits, or attachment verification method.

## 4. Proposed folder layout

The following is a **proposed** layout under the Agent-OS root, not folders to create yet. Reuse existing directories if the workspace already has an approved accounting location.

```text
Agent-OS/
└── Accounting/
    └── Xero/
        ├── README.md
        ├── config.example.yaml
        ├── receipts_to_match/       # original files awaiting first pass
        ├── needs_review/            # unresolved originals; sidecar review notes
        ├── archive/
        │   └── YYYY/
        │       └── MM/              # originals with verified attachment
        ├── logs/                    # append-only run and event records
        └── state/                   # local idempotency database; access restricted
```

Keep originals byte-for-byte. Proposed archive subfolders are based on the local date of **verified upload**, not the receipt date, so the archive location reflects when the system completed its job. Store the receipt date separately in metadata. Never delete from `needs_review/` or `archive/` automatically. If Tony's preservation rules prohibit an operational move until he approves the destination, the implementation must stop before the move and report `verified_not_archived`.

Suggested eventual repository code location: an existing approved app or tools directory selected during discovery. Keep scripts separate from live receipt data and credentials. Do not put receipts, tokens, or the state database into Git.

## 5. Receipt intake and extraction

1. Accept only files with allowed extensions and validated MIME/content; reject or review corrupt, password-protected, empty, and oversized files. Check current Xero attachment limits during discovery.
2. Wait until a copied file is stable (size and modification time unchanged across checks) before processing.
3. Compute SHA-256 on the original bytes. Record original path, filename, size, MIME, hash, and intake time. Keep the original unchanged.
4. Extract native text from text-based PDFs first. For scans and images, use a local OCR option where quality is adequate; consider a managed OCR/document service only if accuracy warrants it and Tony approves sending financial documents to that service.
5. Parse merchant, total, currency, transaction date, tax if present, payment hint/last four if present, and invoice/receipt number. Keep raw extracted text and field confidence separate from match confidence. Redact or avoid logging sensitive full text.
6. Detect multi-receipt files, unsupported currencies, missing totals, implausible dates, and low OCR quality; route them to review rather than guessing.

**OCR options to evaluate:** native PDF extraction; on-device OCR such as Apple Vision or Tesseract; a document OCR provider for hard scans. Compare on Tony's sample receipts for field accuracy, latency, privacy, and cost. The extraction component should return a common structured record regardless of provider.

## 6. Matching policy

Search only Xero transaction types that Tony explicitly approves during discovery. Determine the exact type and status eligibility for bank transactions, spend money transactions, bills, or other records by inspecting the live tenant and current API. An existing transaction may already be reconciled or unreconciled; the matching flow must **never change** that state.

### Candidate generation

- Hard gates: same tenant, supported transaction type, same currency, exact or policy-approved total, eligible transaction status, and a date within the configured window. Compare signed amounts using a documented expense/refund convention.
- Fetch candidate transactions within the date window and account scope. Use pagination, rate limit handling, and only the minimum required fields.
- Compare merchant/contact name after conservative normalization and an explicit alias table; use receipt number or reference as supporting evidence where available.
- Exclude candidates already linked in local state to the same receipt hash. Check Xero attachments for a pre-existing matching attachment before any upload.

### Suggested initial score and thresholds

The score is a **ranking heuristic, not a calibrated probability**. Hard gates always override the score.

| Signal | Suggested weight | Notes |
|---|---:|---|
| Exact amount | 0.35 | Required by default; tolerances require a documented rule |
| Merchant/contact match | 0.30 | Alias match below exact normalized match |
| Date proximity | 0.20 | Same day highest; decline through the window |
| Receipt/reference evidence | 0.10 | Only if present and trustworthy |
| Account/payment hint | 0.05 | Supporting signal only |

Use a configurable ±3-day posting window to start. `>= 0.90` and a lead of `>= 0.15` over the next candidate may qualify for **proposed automatic attachment** after calibration on real samples. `0.70–0.89`, ties, small leads, OCR uncertainty, refund ambiguity, or mismatched metadata go to `needs_review/`. `< 0.70` or no candidate also goes to review. During the first live pilot, require Tony's approval for **every** upload even if the score exceeds 0.90; widen automation only after measuring false matches. A high score must never override conflicting hard facts.

Store top candidate IDs and the contributing signals in the review record. Do not include secrets or full card numbers. Calibrate thresholds against labeled sample receipts before unattended operation.

## 7. State machine and attachment verification

Use an explicit persisted state machine, ideally a small SQLite database with unique constraints on `(tenant_id, sha256)` and an event journal. Every transition should be recoverable after a crash.

```text
discovered -> extracted -> candidate_selected -> upload_pending
           -> uploaded_unverified -> verified -> archived
           \-> needs_review
           \-> failed_retryable / failed_permanent
```

**Upload sequence:**

1. Acquire a per-receipt lock; create or load the state record by tenant and hash.
2. Re-read the selected Xero transaction by ID and confirm key facts still match. Re-check its current attachments and the API's limit before writing.
3. Record `upload_pending` with transaction ID and intended filename. Upload the original bytes with the correct content type and a stable, collision-safe attachment name.
4. Record the response identifiers and status. A successful HTTP response alone means `uploaded_unverified`.
5. Query the transaction's attachments again. Verify that the intended attachment is present with the strongest evidence the current API exposes: returned attachment ID, exact filename, expected size, and, if download is supported, byte hash. Document which checks were actually possible. If verification is uncertain, keep the original in place and mark `uploaded_unverified` for manual investigation.
6. Persist `verified` and a durable event **before** moving the local file. Move the original atomically where the filesystem permits into `archive/YYYY/MM/`; if cross-volume, copy, verify hash, then retain the source until an approved cleanup procedure exists. Record final path and hash. If the move fails, leave `verified_not_archived` for a safe retry without re-uploading.

On restart, inspect `upload_pending` and `uploaded_unverified` records in Xero before retrying an upload. A timeout could mean Xero accepted it. Never blindly resend after an ambiguous response. If Xero does not expose enough attachment metadata to establish identity, require manual verification before archiving.

## 8. Review queue and operator flow

`needs_review/` holds originals with a machine-readable sidecar or state record and a short human summary. Review reasons include no candidate, several candidates, low OCR confidence, amount/currency mismatch, possible duplicate, unsupported type, or Xero/API failure requiring a human decision.

Claude Code should present: filename, extracted merchant/date/amount, reason, top candidate transactions with IDs and evidence, and proposed action. Tony can approve a specific transaction ID, correct extracted fields, mark a duplicate already handled, or leave it pending. A reviewed approval should be stored with approver and timestamp. The execution layer must recheck the transaction and attachments before upload, because the review may be stale. Do not silently return a reviewed file to automatic processing without preserving the review decision.

Do not treat `needs_review/` as an archive. A receipt there is unresolved. A periodic report should show items aging in both `receipts_to_match/` and `needs_review/`.

## 9. Idempotency and audit trail

Use both **content identity** and **Xero identity**. SHA-256 catches byte-for-byte duplicate receipts even when renamed. A separate fingerprint (merchant, date, amount, receipt number) can flag likely scans of the same receipt but must not automatically discard them. Unique keys should prevent the same hash from attaching twice to the same tenant. Xero attachment lookup protects against replays after a crash or manual upload outside the tool.

Write JSON Lines events to `logs/YYYY-MM-DD.jsonl` and keep structured state in SQLite. Each event should include UTC timestamp, run ID, receipt ID/hash prefix, source path, tenant ID or safe alias, transaction ID, state transition, score/evidence, attachment ID when available, archive path, and error code. Avoid tokens, full OCR text, account numbers, and other sensitive data in logs. Rotate or retain logs according to Tony's accounting retention policy; never silently delete them.

Example events (illustrative IDs):

```jsonl
{"ts":"2026-10-03T14:20:11Z","run_id":"run-20261003-01","event":"match_proposed","receipt_id":"sha256:8b6f…","tenant":"primary","transaction_id":"txn-123","score":0.94,"runner_up":0.62,"dry_run":true}
{"ts":"2026-10-03T14:25:44Z","run_id":"run-20261003-02","event":"attachment_verified","receipt_id":"sha256:8b6f…","tenant":"primary","transaction_id":"txn-123","attachment_id":"att-456","evidence":["attachment_id","filename","size"]}
{"ts":"2026-10-03T14:25:45Z","run_id":"run-20261003-02","event":"archived","receipt_id":"sha256:8b6f…","from":"receipts_to_match/store-47.18.pdf","to":"archive/2026/10/store-47.18.pdf","sha256_verified":true}
```

If the Xero API lacks an attachment ID or size in a particular response, log the evidence actually available rather than fabricating fields.

## 10. Security and credentials

- Register a dedicated Xero app for this integration if appropriate. During discovery, confirm current OAuth flow, minimum scopes, tenant selection, redirect URI, token lifetimes, and rate limits from official Xero documentation. Use least privilege consistent with reading transactions and uploading attachments.
- Store client secret and refresh token in the OS keychain or an approved secret manager, never in YAML, Markdown, source files, logs, or Git. Restrict local file permissions on state and logs. Keep `config.example.yaml` free of credentials.
- Refresh tokens through the approved OAuth flow; account for token rotation and concurrent runs. Do not print token values on error.
- Pin the target tenant explicitly and display its safe name at run start. Prevent cross-tenant matches by including tenant ID in every state key and API operation.
- Keep OCR local initially unless Tony approves an external processor; define retention and data handling if a hosted service is added.
- Use read-only dry runs for initial analysis. Treat any live upload as an explicit write operation with an audit record.

## 11. Example configuration

Values below are **proposed defaults**, subject to discovery and sample-based calibration. Keep only nonsecret settings here.

```yaml
version: 1
xero:
  tenant_alias: primary
  eligible_transaction_types: [BANK_TRANSACTION]  # confirm exact API values
  eligible_statuses: [AUTHORISED]              # confirm tenant workflow
  credential_ref: keychain:xero-receipts-primary # reference only; no secret
paths:
  intake: receipts_to_match
  review: needs_review
  archive: archive
  logs: logs
  state_db: state/receipts.sqlite3
intake:
  allowed_extensions: [.pdf, .jpg, .jpeg, .png, .heic]
  stable_file_seconds: 5
  max_file_mb: 10                         # confirm Xero attachment limit
extraction:
  primary: native_pdf_text
  image_ocr: local                       # select implementation after trial
  min_field_confidence: 0.80
matching:
  date_window_days: 3
  exact_amount_required: true
  automatic_score_min: 0.90
  minimum_lead_over_runner_up: 0.15
  aliases: {}                            # curated merchant aliases only
workflow:
  dry_run: true
  require_human_approval_for_upload: true
  verify_attachment_before_archive: true
  archive_month_basis: verified_upload_local_date
  timezone: America/New_York
```

The sample status/type strings and size cap are placeholders, not assertions about current Xero API behavior. Claude Code must replace them with verified values before a live run.

## 12. Failure modes and recovery

| Failure | Required behavior |
|---|---|
| OCR cannot read total/date | Review; no upload |
| Multiple plausible transactions | Review with ranked candidates; no upload |
| Currency, amount, or tenant mismatch | Hard stop for that receipt; review |
| Duplicate hash already archived | Report `already_processed`; do not upload again |
| Similar receipt with different bytes | Flag possible duplicate; human decision |
| Xero rate limit or transient outage | Bounded retry with backoff; retain original and state |
| OAuth expired/revoked | Stop writes, surface reconnect instruction, retain files |
| Upload timeout or ambiguous response | Query Xero attachments before any retry |
| Upload accepted but verification incomplete | Keep original in intake/review, mark `uploaded_unverified` |
| Verified upload, archive move fails | Mark `verified_not_archived`; retry move only |
| Archive name collision | Use deterministic suffix from hash; preserve both originals |
| Process crash | Resume from persisted state; recheck remote state before writes |
| Attachment limit reached | Review; no upload or replacement without Tony's decision |

## 13. Dry run and testing strategy

Dry run must read local files and, if credentials are configured, read Xero candidates and attachments; it must **never** upload, alter Xero transactions, or move files. Its report should show intended match, score, evidence, and whether the attachment/archiving gates would pass. A `--offline` option can exercise extraction and scoring with saved, redacted transaction fixtures without Xero access.

Before live use, Codex should implement meaningful checks for parsing, amount/currency hard gates, score ties, duplicate hash handling, safe resumption after timeout, verification failure, and archive move failure. Use mock Xero responses for error paths and a small set of Tony-approved sample receipts for extraction accuracy. Verify that read-only/dry-run mode emits no write API calls and does not move files. For the live pilot, use a dedicated test set and inspect results in Xero plus the local archive and event log. Do not use real receipt data in committed test fixtures.

## 14. Phased rollout and gates

1. **Discovery and approval:** Claude Code inspects existing Agent-OS accounting structure, current Xero API/MCP capabilities, transaction types, OAuth scopes, attachment metadata, and Tony's sample receipts. Confirm proposed folder destination and archive move policy with Tony before creating folders. Agree on eligible transactions and whether Phase 1 includes reconciled records.
2. **Local prototype:** Codex builds intake, extraction, hashing, candidate scoring, SQLite state, JSONL events, and a CLI. Use offline fixtures and dry runs only. Claude Code reviews output with Tony and adjusts aliases/thresholds.
3. **Read-only Xero integration:** Connect OAuth and tenant selection. Fetch candidates and current attachments in dry run. Reconcile local predictions against known Xero transactions. No uploads.
4. **Human-approved live pilot:** For each receipt, Tony approves the proposed transaction ID. Upload one at a time, verify in Xero, then archive. Inspect every result and failure path. Keep this mode until the observed false-match rate is acceptable to Tony.
5. **Controlled automation:** Enable automatic attachment only for clear, unique high-score matches after approval of measured thresholds. Continue sending exceptions to review. Add a run schedule only after manual runs are stable and Tony approves it.

Do not proceed to a later phase simply because code exists. Each gate requires a run report, inspected examples, and an explicit decision on the next level of automation.

## 15. Suggested implementation files and commands

These are names to refine after inspecting existing Agent-OS tools and folder conventions; they are **not** an instruction to create folders immediately.

```text
README.md                   operator setup, runbook, recovery
config.example.yaml         nonsecret defaults and policy
src/xero_auth.py             OAuth and token refresh via secret store
src/xero_client.py           typed API reads, upload, attachment lookup
src/extract.py               PDF text/OCR adapter and parsed fields
src/match.py                 candidate hard gates, scoring, evidence
src/state.py                 SQLite state machine and locks
src/pipeline.py              safe orchestration and resume logic
src/cli.py                   scan, dry-run, review, attach, resume, report
tests/                       focused unit/integration tests with synthetic fixtures
```

Potential operator commands, subject to CLI design:

```text
xero-receipts scan --dry-run
xero-receipts review
xero-receipts attach --receipt-id <id> --transaction-id <id> --approved-by tony
xero-receipts resume
xero-receipts report --since 2026-10-01
```

The CLI should display tenant and mode prominently and reject a live write unless the configuration and command agree on live mode. Keep implementation simple enough for Claude Code to operate and audit.

## 16. Claude Code execution checklist

- [ ] Read Agent-OS `AGENTS.md`, `CLAUDE.md`, workspace/directory maps, relevant accounting instructions, and `TOOLBOX.md`; identify existing approved paths and tools.
- [ ] Confirm Tony's Xero tenant, transaction types, receipt sample set, allowed account scope, and definition of an eligible existing transaction.
- [ ] Verify current official Xero API/OAuth/attachment documentation and installed official MCP tools; record endpoints, scopes, limits, rate limits, and verification evidence.
- [ ] Obtain Tony's approval for any new `Accounting/Xero` folders and operational archive destination before creating or moving anything in Agent-OS.
- [ ] Ask Codex to implement the local pipeline in an approved code location, with clear file ownership and a reviewed interface.
- [ ] Set up secret storage and OAuth without copying token values into workspace files.
- [ ] Label sample receipts and calibrate extraction and matching thresholds.
- [ ] Complete offline and read-only dry runs; inspect no-write evidence.
- [ ] Run a one-receipt live pilot with Tony's transaction approval; verify attachment in Xero, archived original, matching hash, and audit event.
- [ ] Repeat on a small batch with uncertain cases; validate review and recovery behavior.
- [ ] Approve any move to unattended high-confidence attachment separately; retain manual review for ambiguity.
- [ ] Write a short operating runbook and final Phase 1 acceptance report listing verified behavior and unresolved limits.

## 17. Decisions to settle during discovery

1. Which Xero record types are valid attachment targets in Tony's books, and how should refunds be handled?
2. Should receipts for already reconciled existing transactions be eligible? Attachment alone must not alter reconciliation state.
3. Which existing Agent-OS location should hold accounting data and code, and which proposed folders does Tony approve?
4. What retention policy applies to originals, state, and logs? Is moving originals into the approved archive acceptable under Agent-OS preservation rules?
5. Which OCR route meets Tony's quality and privacy expectations on a representative sample?
6. What observed precision is required before removing human approval for high-score matches?
7. Which Xero attachment fields can be re-read to establish verification, and how should uncertain verification be handled in this tenant?

**Definition of done for Phase 1:** Tony can inspect the inbox and review queue and know exactly what remains unresolved. Each archived receipt has an auditable, verified attachment to the intended existing Xero transaction. No Phase 1 run changes reconciliation or categories.
