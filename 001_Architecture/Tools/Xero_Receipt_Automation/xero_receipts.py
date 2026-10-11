#!/usr/bin/env python3
import argparse
import hashlib
import json
import mimetypes
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import xr_config
import xr_match
import xr_notify
import xr_report
import xr_secrets
import xr_state
import xr_gmail_api
from xr_gmail_api import FakeGmailClient, FakeGmailSource
from xr_xero_api import FakeXeroClient, XeroClient


SCOPES = "offline_access accounting.banktransactions.read accounting.invoices.read accounting.contacts.read accounting.attachments"
CANDIDATE_FIELDS = ("account_label", "message_id", "thread_id", "sender", "subject", "date", "body_text", "attachments")
ALLOWED_DROPS = {".pdf", ".jpg", ".jpeg", ".png", ".heic"}
# Only receipts already attached to Xero AND hash-verified can ever have their email archived.
# Every one of these states is reachable only through a downloaded-bytes hash match.
ARCHIVE_ELIGIBLE_STATES = {"verified", "verified_not_archived", "archived", "already_attached"}
GMAIL_UNTAGGED_NOTE = (
    "Receipt attached and verified, but the email has no Gmail label. "
    "Add a Gmail filter/label for this vendor so it can be archived next time."
)


def parse_args():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--config", default="config.example.json")
    common.add_argument("--data-dir")
    common.add_argument("--intake-dir")
    common.add_argument("--archive-dir")
    common.add_argument("--dry-run", action="store_true")
    common.add_argument("--offline", action="store_true")
    common.add_argument("--fixtures-dir", default=".")
    common.add_argument("--simulate-live", action="store_true")
    common.add_argument("--fake-verify-fail", action="store_true")
    common.add_argument("--live", action="store_true")
    common.add_argument("--scheduled", action="store_true")
    common.add_argument("--now", default=None)
    common.add_argument("--run-id", default=None, help="reuse a run id so a second call ingests Run_<id>_Gmail_Candidates.json")
    common.add_argument("--json", dest="json_output", action="store_true")
    parser = argparse.ArgumentParser(prog="xero_receipts.py", parents=[common], description="Attach receipts to existing Xero expenses only.")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("config-check", "auth-xero", "auth-gmail", "xero-fetch", "plan-search", "ingest-candidates", "fetch-bytes", "scan-drops", "match", "attach", "verify", "archive", "run", "review", "approve", "reject", "correct", "confirm-removed", "vendor-trust", "notify-check", "notify", "calibration-report", "verify-state", "gmail-archive"):
        commands.add_parser(name, parents=[common])
    commands.choices["auth-gmail"].add_argument("--account", default=None, help="gmail_accounts label this token is for (defaults to the config's first entry)")
    commands.choices["auth-gmail"].add_argument("--allow-archive", action="store_true", help="request gmail.modify (needed only for the gated gmail-archive step) instead of gmail.readonly")
    for command in ("approve", "reject", "correct", "confirm-removed", "attach", "verify", "archive", "gmail-archive"):
        subparser = getattr(commands, "choices", {}).get(command)
        if subparser is not None:
            subparser.add_argument("--item", required=(command == "approve"))
    approve = commands.choices["approve"]
    approve.add_argument("--by", default="tony")
    correct = commands.choices["correct"]
    correct.add_argument("--kind", required=True)
    correct.add_argument("--note", required=True)
    vendor = commands.choices["vendor-trust"]
    vendor.add_argument("--show", action="store_true")
    vendor.add_argument("--reset")
    notify = commands.choices["notify"]
    notify.add_argument("--channel", choices=("macos",))
    notify.add_argument("--sent", choices=("push", "macos"))
    notify.add_argument("--result", default="")
    notify.add_argument("--ack", action="store_true")
    return parser.parse_args()


class Pipeline:
    def __init__(self, args):
        self.args = args
        self.config = xr_config.load_config(args.config, args.data_dir, args.intake_dir, args.archive_dir)
        self.paths = xr_config.config_paths(self.config)
        self.fixtures_dir = Path(args.fixtures_dir).expanduser()
        self.now = args.now or xr_state.iso_utc()
        self.run_id = getattr(args, "run_id", None) or "run_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.state = xr_state.StateStore(self.paths["data"])
        self.aliases = json.loads((self.fixtures_dir / ("Fixture_Vendor_Aliases.json" if args.offline else "Vendor_Aliases.example.json")).read_text(encoding="utf-8"))
        self._client = None
        self._gmail_clients = {}
        self.excluded_bank_accounts = {}
        # --simulate-live only means something against the offline fakes; with --live it must never bypass the flag.
        simulated = bool(args.offline and args.simulate_live)
        self.write_enabled = simulated or bool(args.live and self.config["live_enabled"])
        # Separate gate for the one Gmail write (archive = remove INBOX label). Independent of live_enabled.
        self.archive_write_enabled = simulated or bool(args.live and self.config.get("auto_archive_enabled", False))
        self.already_attached_this_call = []
        self.summary = {
            "auto_eligible": 0,
            "pending_review": 0,
            "needs_manual_portal_lookup": 0,
            "no_candidate": 0,
            "uploaded": 0,
            "verified": 0,
            "archived": 0,
            "already_attached": 0,
            "xero_write_calls": 0,
            "xero_put_calls": 0,
            "gmail_archived": 0,
            "gmail_untagged": 0,
            "gmail_write_calls": 0,
            "phantom_transfers": 0,
            "excluded_by_bank_account": 0,
            "excluded_bank_accounts": {},
        }

    @property
    def client(self):
        """Created on first use, so review/notify commands never need Xero access."""
        if self._client is None:
            if self.args.offline:
                self._client = FakeXeroClient(self.fixtures_dir, self.args.simulate_live)
            elif self.args.live:
                self._client = self._live_client()
            else:
                raise RuntimeError("Xero access needs --offline (synthetic fixtures) or --live (real Xero; add --dry-run for read-only)")
        return self._client

    def _live_client(self):
        client_id = xr_secrets.required_secret("XERO_CLIENT_ID")
        tenant_id = self.config["tenant_id"]
        stored = xr_secrets.read_refresh_token(tenant_id) if tenant_id else ""
        if not stored:
            raise RuntimeError("no Xero sign-in found (tenant_id empty or no Keychain token); run auth-xero")
        client = XeroClient(client_id, tenant_id, stored, xr_secrets)
        client.refresh()
        return client

    def fetch(self):
        active = []
        raw_items = []
        targets = self.config["xero_targets"]
        start = datetime.fromisoformat(self.now.replace("Z", "+00:00")).date() - timedelta(days=self.config["weekly_lookback_days"])
        cutoff = f"DateTime({start.year},{start.month},{start.day})"
        raw_items.extend(self.client.list_bank_transactions(where=f'Type=="{targets["bank_transactions"]["type"]}" AND Date>={cutoff}'))
        raw_items.extend(self.client.list_invoices(where=f'Type=="{targets["invoices"]["type"]}" AND Date>={cutoff}'))
        statuses_bank = set(self.config["xero_targets"]["bank_transactions"]["statuses"])
        statuses_invoice = set(self.config["xero_targets"]["invoices"]["statuses"])
        bank_names = self._known_bank_names(raw_items)
        for raw in raw_items:
            endpoint = "BankTransactions" if raw.get("Type") == "SPEND" else "Invoices"
            bank_account = self._bank_account(raw, endpoint, bank_names)
            existing = self.state.index["items"].get(f"{endpoint}:{raw['ID']}")
            if existing is not None and bank_account and existing["transaction"].get("bank_account") != bank_account:
                existing["transaction"]["bank_account"] = bank_account  # backfill badges on already-known items, incl. finished ones
            if endpoint == "BankTransactions" and not xr_match.bank_account_eligible(bank_account, self.config["eligible_bank_accounts"]):
                # Revenue / transfer accounts (Relay, Mercury, Wise, PayPal, Etsy Payment Balance...) never get receipts.
                name = (bank_account or {}).get("name") or (bank_account or {}).get("account_id") or "unknown account"
                self.excluded_bank_accounts[name] = self.excluded_bank_accounts.get(name, 0) + 1
                if existing is not None and existing["state"] in xr_state.CLASSES:
                    self._mark_ineligible(existing, name)
                continue
            if existing is not None and existing.pop("ineligible_bank_account", None):
                if str(existing.get("reason", "")).startswith("Not on an eligible expense credit card"):
                    existing.pop("reason")  # allowlist fixed: the item is matched normally again
            status = raw.get("Status", "AUTHORISED")
            allowed = statuses_bank if endpoint == "BankTransactions" else statuses_invoice
            if status not in allowed or raw.get("HasAttachments"):
                continue
            transaction = {
                "item_id": f"{endpoint}:{raw['ID']}",
                "endpoint": endpoint,
                "guid": raw["ID"],
                "type": raw.get("Type", ""),
                "date": raw.get("Date", ""),
                "total": raw.get("Total", raw.get("Amount", 0)),
                "currency": raw.get("CurrencyCode", "USD"),
                "contact_name": raw.get("ContactName", raw.get("Contact", {}).get("Name", "")),
                "reference": raw.get("Reference", ""),
                "description": raw.get("Description", ""),
                "is_reconciled": raw.get("IsReconciled", False),
                "bank_account": bank_account,
                "archive_date_format": self.config["archive_date_format"],
            }
            record = self.state.discover(self.run_id, transaction, self.args.dry_run)
            if record is not None:
                active.append(record)
        return active

    def _mark_ineligible(self, record, account_name):
        """An item found before the allowlist existed: park it where it can never be approved or uploaded."""
        reason = f"Not on an eligible expense credit card ({account_name}); receipts are never attached on this account."
        if record["state"] != "no_candidate":
            self.state.transition(record["item_id"], "no_candidate", self.run_id, self.args.dry_run, auto=False, reason=reason, ineligible_bank_account=True)
        else:
            record.update(auto=False, reason=reason, ineligible_bank_account=True)

    def _known_bank_names(self, raw_items):
        """AccountID -> Name, from this fetch and from earlier runs, for lines where Xero omits Name."""
        names = {}
        for item in self.state.index["items"].values():
            bank = (item.get("transaction") or {}).get("bank_account") or {}
            if bank.get("account_id") and bank.get("name"):
                names[bank["account_id"]] = bank["name"]
        for raw in raw_items:
            bank = raw.get("BankAccount") or {}
            if bank.get("AccountID") and bank.get("Name"):
                names[bank["AccountID"]] = bank["Name"]
        return names

    @staticmethod
    def _bank_account(raw, endpoint, bank_names):
        """Which Xero bank account a Spend Money line sits on. Bills (Invoices) have none: null."""
        bank = raw.get("BankAccount") or {}
        if endpoint != "BankTransactions" or not bank:
            return None
        account_id = bank.get("AccountID", "")
        return {"account_id": account_id, "code": bank.get("Code", ""), "name": bank.get("Name") or bank_names.get(account_id, "")}

    def plan_search(self, records):
        plan = {"run_id": self.run_id, "items": {}}
        for record in records:
            transaction = record["transaction"]
            vendor = xr_match.vendor_for(transaction["contact_name"], self.aliases)
            date = datetime.fromisoformat(transaction["date"])
            start = date.fromordinal(date.toordinal() - self.config["gmail_window_days"])
            end = date.fromordinal(date.toordinal() + self.config["gmail_window_days"])
            queries = []
            if vendor:
                domains = " OR ".join(self.aliases[vendor].get("sender_domains", []))
                queries.append(f"(from:({domains}) OR \"{self.aliases[vendor]['display_name']}\") after:{start:%Y/%m/%d} before:{end:%Y/%m/%d}")
            queries.append(f"\"{transaction['total']:.2f}\"")
            plan["items"][record["item_id"]] = {"queries": queries, "transaction": transaction}
            if record["state"] == "discovered":
                self.state.transition(record["item_id"], "search_planned", self.run_id, self.args.dry_run)
        path = self.paths["data"] / f"Run_{self.run_id}_Search_Plan.json"
        path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        self._last_plan = plan
        return plan

    def search_gmail_live(self, records, plan):
        """Real, in-process Gmail search across every account in config.gmail_accounts —
        read-only (search/message/attachment GET, same Keychain token as fetch_gmail_bytes).
        Replaces the old 'Claude layer writes Gmail_Candidates.json' handoff, which only ever
        reached whichever single Gmail account a chat session's own connector was bound to."""
        items = {}
        for record in records:
            if record["state"] != "search_planned":
                continue
            item_id = record["item_id"]
            queries = plan["items"].get(item_id, {}).get("queries", [])
            candidates = []
            seen_message_ids = set()
            for label in self.config["gmail_accounts"]:
                client = self.gmail_client(label)
                if client is None:
                    continue
                for query in queries:
                    try:
                        result = client.search(query, page_size=5)
                    except Exception as error:
                        print(f"warning: Gmail search failed for {item_id} ({label}): {error}", file=sys.stderr)
                        continue
                    for thread in result.get("threads", [])[:3]:
                        message_id = thread["id"]
                        if message_id in seen_message_ids:
                            continue
                        seen_message_ids.add(message_id)
                        try:
                            message = client.message(message_id, "full")
                        except Exception as error:
                            print(f"warning: Gmail fetch failed for {message_id} ({label}): {error}", file=sys.stderr)
                            continue
                        headers = {h["name"]: h["value"] for h in message.get("payload", {}).get("headers", [])}
                        date_header = headers.get("Date", "")
                        try:
                            date = parsedate_to_datetime(date_header).date().isoformat()
                        except (TypeError, ValueError):
                            date = record["transaction"]["date"]
                        attachments = [
                            {"filename": filename, "mime": mime}
                            for filename, mime, _ in xr_gmail_api.attachment_parts(message.get("payload"))
                        ]
                        candidates.append({
                            "account_label": label,
                            "message_id": message_id,
                            "thread_id": thread.get("threadId", message_id),
                            "sender": headers.get("From", ""),
                            "subject": headers.get("Subject", ""),
                            "date": date,
                            "body_text": xr_gmail_api.message_text(message.get("payload")),
                            "attachments": attachments,
                        })
                    if len(candidates) >= 5:
                        break
                if len(candidates) >= 5:
                    break
            if candidates:
                items[item_id] = candidates
        return items

    def load_candidates(self, records, plan=None):
        """Offline: fixtures. Otherwise a real, in-process Gmail search across both accounts
        (search_gmail_live), written to Run_<id>_Gmail_Candidates.json as an audit record.
        A pre-existing, already-valid candidates file for this run_id is used as-is (manual
        override path kept for debugging/edge cases) rather than searched again."""
        if self.args.offline:
            return FakeGmailSource(self.fixtures_dir).candidates()
        path = self.paths["data"] / f"Run_{self.run_id}_Gmail_Candidates.json"
        if not path.exists():
            items = self.search_gmail_live(records, plan or {"items": {}})
            path.write_text(json.dumps({"run_id": self.run_id, "items": items}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or data.get("run_id") != self.run_id or not isinstance(data.get("items"), dict):
            raise ValueError(f"{path.name}: needs run_id {self.run_id} and an items object")
        unknown = sorted(set(data["items"]) - {record["item_id"] for record in records})
        if unknown:
            raise ValueError(f"{path.name}: unknown item ids {unknown}")
        for item_id, candidates in data["items"].items():
            for candidate in candidates if isinstance(candidates, list) else [None]:
                missing = [field for field in CANDIDATE_FIELDS if not isinstance(candidate, dict) or field not in candidate]
                if missing or not isinstance(candidate["attachments"], list) or len(candidate["body_text"]) > 20000:
                    raise ValueError(f"{path.name}: bad candidate for {item_id} (missing {missing} or body over 20000 chars)")
                for field in ("staged_fixture", "staged_path", "path"):
                    candidate.pop(field, None)  # connector text can never supply file bytes
        return data["items"]

    def ingest_candidates(self, records):
        fixture_candidates = self.load_candidates(records, getattr(self, "_last_plan", None))
        for record in records:
            candidates = fixture_candidates.get(record["item_id"], [])
            record["candidates"] = candidates
            if record["state"] == "search_planned":
                self.state.transition(record["item_id"], "candidates_received", self.run_id, self.args.dry_run)
        return fixture_candidates

    def fetch_bytes(self, records):
        if not self.args.offline and self.config["gmail_byte_source"] == "gmail_api":
            self.fetch_gmail_bytes(records)
        for record in records:
            for candidate in record.get("candidates", []):
                path = candidate.get("staged_fixture") or candidate.get("staged_path")
                if not path:
                    continue
                source = Path(path).expanduser()
                if not source.is_file():
                    candidate["staged_path"] = None
        return records

    def fetch_gmail_bytes(self, records):
        """Byte-exact Gmail attachments (read-only API) staged as data_dir/staged_<sha12>.<ext>."""
        for record in records:
            for candidate in record.get("candidates", []):
                label = candidate.get("account_label")
                client = self.gmail_client(label)
                if client is None or not candidate.get("attachments"):
                    continue
                fetched = xr_gmail_api.fetch_candidate_bytes(client, candidate)
                if not fetched or len(fetched[1]) > self.config["max_file_mb"] * 1024 * 1024:
                    continue
                digest = hashlib.sha256(fetched[1]).hexdigest()
                staged = self.paths["data"] / f"staged_{digest[:12]}{Path(fetched[0]).suffix.lower()}"
                if not staged.exists():
                    staged.write_bytes(fetched[1])
                candidate["staged_path"] = str(staged)

    def gmail_client(self, label):
        """One client per Gmail account label (offline: fixture fake). None when no Keychain token exists."""
        if label not in self._gmail_clients:
            if self.args.offline:
                self._gmail_clients[label] = FakeGmailClient(self.fixtures_dir, label, self.args.simulate_live)
            else:
                token = xr_secrets.read_refresh_token(label, xr_gmail_api.GMAIL_KEYCHAIN_SERVICE) if label else ""
                if not token:
                    print(f"warning: no Gmail token in Keychain ({xr_gmail_api.GMAIL_KEYCHAIN_SERVICE}/{label}); its candidates can only go to review", file=sys.stderr)
                    self._gmail_clients[label] = None
                else:
                    access, scopes = xr_gmail_api.access_token_info(xr_secrets.required_secret("GMAIL_CLIENT_ID"), xr_secrets.required_secret("GMAIL_CLIENT_SECRET"), token)
                    self._gmail_clients[label] = xr_gmail_api.GmailClient(access, label, scopes)
        return self._gmail_clients[label]

    def scan_drops(self, records):
        drops = []
        for path in self.paths["intake"].iterdir():
            if path.is_dir() or path.name.startswith(".") or path.suffix.lower() not in ALLOWED_DROPS:
                continue
            first = path.stat()
            time.sleep(5)
            second = path.stat()
            if (first.st_size, first.st_mtime_ns) != (second.st_size, second.st_mtime_ns):
                continue
            drops.append(path)
        for record in records:
            for path in drops:
                extraction = xr_match.extract_text(path)
                candidate = {
                    "account_label": "manual drop",
                    "sender": "",
                    "subject": f"Manual drop {path.name}",
                    "date": record["transaction"]["date"],
                    "view_url": "",
                    "body_text": extraction["text"][:20000],
                    "attachments": [{"filename": path.name, "mime": mimetypes.guess_type(path)[0] or "application/octet-stream", "size": path.stat().st_size}],
                    "path": str(path),
                    "source_kind": "manual",
                }
                record.setdefault("candidates", []).append(candidate)
            if record["state"] == "search_planned":
                self.state.transition(record["item_id"], "candidates_received", self.run_id, self.args.dry_run)
        return drops

    def match(self, records):
        holds = self.state.vendor_holds()
        results = []
        for record in records:
            if record["state"] not in xr_state.RECLASSIFIABLE or record.get("verify_failed"):
                continue
            transaction = record["transaction"]
            candidates = record.get("candidates", [])
            phantom = xr_match.phantom_transfer_reason(transaction)
            if phantom:
                # Never score, never attach: no_candidate cannot be approved or uploaded. Tony deletes these in Xero.
                results.append([record, "no_candidate", {"auto": False, "phantom_transfer": True, "reason": phantom, "top_candidates": [], "lead": 0.0}])
                continue
            classification, scored, best, lead = xr_match.classify(
                transaction,
                candidates,
                self.aliases,
                self.config,
                holds,
                self.config["max_attachments_per_doc"],
            )
            details = {
                "top_candidates": scored[:3],
                "runner_up_score": scored[1]["score"] if len(scored) > 1 else 0.0,
                "lead": lead,
                "auto": classification == "auto_eligible",
            }
            if best:
                details.update({
                    "score": best["score"],
                    "signals": best["signals"],
                    "source": best.get("account_label"),
                    "source_path": best.get("staged_fixture") or best.get("staged_path") or best.get("path"),
                    "source_kind": "fixture" if best.get("staged_fixture") else ("manual" if best.get("path") else "gmail"),
                    "sha256": (best.get("byte_evidence") or {}).get("sha256"),
                    "gmail_message_id": best.get("message_id"),
                })
            results.append([record, classification, details])
        # One receipt file may back only one transaction: a hash proposed twice, or already used elsewhere, goes to review.
        used = {item.get("sha256") for item in self.state.index["items"].values() if item.get("attachment_id")}
        proposed = [details.get("sha256") for _, classification, details in results if classification == "auto_eligible"]
        for result in results:
            record, classification, details = result
            sha = details.get("sha256")
            if classification == "auto_eligible" and (proposed.count(sha) > 1 or sha in used):
                result[1] = "pending_review"
                details.update(auto=False, reason="same receipt hash proposed for another transaction")
        for record, classification, details in results:
            if record["state"] != classification:
                self.state.transition(record["item_id"], classification, self.run_id, self.args.dry_run, **details)
            record["state"] = classification
            record.update(details)
        return records

    def attach(self, records):
        if not self.write_enabled or self.args.dry_run:
            return []
        uploaded = []
        for record in records:
            if record["state"] not in {"auto_eligible", "approved"} or len(uploaded) >= self.config["max_auto_attach_per_run"]:
                continue
            transaction = record["transaction"]
            current = self.client.get_transaction(transaction["endpoint"], transaction["guid"])
            if transaction["endpoint"] == "BankTransactions":
                bank = current.get("BankAccount") or {}
                current_bank = {"account_id": bank.get("AccountID", ""), "name": bank.get("Name") or (transaction.get("bank_account") or {}).get("name", "")}
                if not xr_match.bank_account_eligible(current_bank, self.config["eligible_bank_accounts"]):
                    reason = f"Not on an eligible expense credit card ({current_bank['name'] or current_bank['account_id'] or 'unknown account'}); not attached."
                    next_state = "pending_review" if record["state"] == "approved" else "no_candidate"
                    self.state.transition(record["item_id"], next_state, self.run_id, self.args.dry_run, auto=False, reason=reason, ineligible_bank_account=True)
                    record["state"] = next_state
                    continue
            if (
                current.get("Total", current.get("Amount")) != transaction["total"]
                or current.get("Date") != transaction["date"]
                or current.get("ContactName", current.get("Contact", {}).get("Name")) != transaction["contact_name"]
            ):
                self.state.transition(record["item_id"], "pending_review", self.run_id, self.args.dry_run)
                continue
            attachments = self.client.list_attachments(transaction["endpoint"], transaction["guid"])
            if len(attachments) >= self.config["max_attachments_per_doc"]:
                self.state.transition(record["item_id"], "pending_review", self.run_id, self.args.dry_run, reason="attachment limit")
                continue
            source = Path(record["source_path"]).expanduser()
            extension = source.suffix.lower().lstrip(".")
            vendor = xr_match.vendor_for(transaction["contact_name"], self.aliases)
            display = self.aliases[vendor]["display_name"] if vendor else transaction["contact_name"]
            filename = xr_state.safe_filename(xr_state.archive_name(transaction, display, extension), f"{transaction['guid']}.{extension}")
            existing = {item["FileName"]: item for item in attachments}
            if filename in existing:
                content = self.client.get_attachment(transaction["endpoint"], transaction["guid"], filename)
                if hashlib.sha256(content).hexdigest() == record["sha256"]:
                    self.state.transition(record["item_id"], "already_attached", self.run_id, self.args.dry_run, filename=filename, attachment_id=existing[filename]["AttachmentID"])
                    record["state"] = "already_attached"
                    self.summary["already_attached"] += 1
                    self.already_attached_this_call.append(record)
                    continue
                filename = xr_state.safe_filename(f"{Path(filename).stem}_{record['sha256'][:8]}.{extension}", filename)
            self.state.transition(record["item_id"], "upload_pending", self.run_id, self.args.dry_run, filename=filename)
            content = source.read_bytes()
            mime = mimetypes.guess_type(filename)[0] or "application/pdf"
            # Always the real hash of what's actually being uploaded — never trust an upstream
            # byte_evidence.sha256 that may be missing or stale (manual-drop matches don't always
            # get one populated during match()). verify() compares against this value, so it must
            # reflect these exact bytes or a correct upload can falsely fail hash verification.
            sha256 = hashlib.sha256(content).hexdigest()
            attachment = self.client.post_attachment(transaction["endpoint"], transaction["guid"], filename, content, mime)
            self.state.transition(record["item_id"], "uploaded_unverified", self.run_id, self.args.dry_run, filename=filename, attachment_id=attachment["AttachmentID"], sha256=sha256)
            record["state"] = "uploaded_unverified"
            record["sha256"] = sha256
            uploaded.append(record)
        return uploaded

    def verify(self, records):
        verified = []
        for record in records:
            if record["state"] != "uploaded_unverified":
                continue
            transaction = record["transaction"]
            attachments = self.client.list_attachments(transaction["endpoint"], transaction["guid"])
            attachment = next((item for item in attachments if item["FileName"] == record["filename"]), None)
            same = False
            if attachment is not None:
                content = self.client.get_attachment(transaction["endpoint"], transaction["guid"], record["filename"])
                same = len(content) == attachment["ContentLength"] and hashlib.sha256(content).hexdigest() == record["sha256"]
            if self.args.fake_verify_fail or not same:
                reason = "attachment not found in Xero after upload" if attachment is None else "downloaded bytes do not hash-match the local file"
                self.state.transition(record["item_id"], "pending_review", self.run_id, self.args.dry_run, reason=reason, verify_failed=True, auto=False)
                print(f"verify failed for {record['item_id']}: {reason}; file kept in intake, item sent to review", file=sys.stderr)
                continue
            self.state.transition(record["item_id"], "verified", self.run_id, self.args.dry_run, evidence="downloaded bytes hash-match", filename=record["filename"], attachment_id=attachment["AttachmentID"])
            record["state"] = "verified"
            verified.append(record)
        return verified

    def archive(self, records):
        archived = []
        for record in records:
            if record["state"] not in {"verified", "already_attached"}:
                continue
            source = Path(record["source_path"]).expanduser()
            destination = self.paths["archive"] / record["filename"]
            if destination.exists():
                self.state.transition(record["item_id"], "verified_not_archived", self.run_id, self.args.dry_run, reason="archive name collision")
                record["state"] = "verified_not_archived"
                continue
            if record["source_kind"] == "manual":
                if not source.is_file():
                    self.state.transition(record["item_id"], "verified_not_archived", self.run_id, self.args.dry_run, reason="source missing")
                    continue
                os.rename(source, destination)
            elif record["source_kind"] == "fixture" or (self.config["archive_gmail_sourced"] and record["source_kind"] == "gmail"):
                destination.write_bytes(source.read_bytes())
            else:
                self.state.transition(record["item_id"], "verified_not_archived", self.run_id, self.args.dry_run, reason="gmail archive disabled")
                record["state"] = "verified_not_archived"
                continue
            self.state.transition(record["item_id"], "archived", self.run_id, self.args.dry_run, filename=record["filename"])
            record["state"] = "archived"
            archived.append(record)
        return archived

    def gmail_archive_candidates(self, item_id=None):
        """Items whose receipt came from a Gmail message and is already attached + hash-verified in Xero."""
        items = [self.state.index["items"][item_id]] if item_id else list(self.state.index["items"].values())
        eligible = []
        for item in items:
            if item.get("state") not in ARCHIVE_ELIGIBLE_STATES or item.get("verify_failed"):
                continue
            if item.get("source_kind") not in {"gmail", "fixture"}:  # manual drops have no email to archive
                continue
            if not (item.get("gmail_message_id") and item.get("source") and item.get("attachment_id") and item.get("sha256")):
                continue
            if (item.get("gmail_archive") or {}).get("status") in {"archived", "already_out_of_inbox"}:
                continue
            eligible.append(item)
        return eligible

    def gmail_archive(self, item_id=None):
        """Archive (remove INBOX, nothing else) the email behind each hash-verified receipt, only if the
        email carries a real user label. Writes only with auto_archive_enabled + --live and not --dry-run;
        otherwise it is a read-only preview that is not saved."""
        writes = self.archive_write_enabled and not self.args.dry_run
        cap = self.config.get("max_auto_archive_per_run", 10)
        results = []
        archived_count = 0
        for item in self.gmail_archive_candidates(item_id):
            label, message_id = item["source"], item["gmail_message_id"]
            outcome = {"account": label, "message_id": message_id, "run_id": self.run_id, "at": self.now}
            client = self.gmail_client(label)
            labels = client.message_labels(message_id) if client is not None else None
            if client is None:
                outcome.update(status="failed", reason=f"no Gmail token in Keychain for account label {label}")
            elif labels is None:
                outcome.update(status="failed", reason="Gmail message not found (deleted or moved account)")
            elif "TRASH" in labels or "SPAM" in labels:
                outcome.update(status="skipped", reason="message is in Trash or Spam; left alone")
            elif "INBOX" not in labels:
                outcome.update(status="already_out_of_inbox")
            elif not xr_gmail_api.user_labels(labels):
                outcome.update(status="untagged", note=GMAIL_UNTAGGED_NOTE)
            elif not writes:
                outcome.update(status="would_archive")
            elif not client.can_modify:
                outcome.update(status="failed", reason=f"Gmail token for {label} is read-only; run auth-gmail --account {label} --allow-archive")
            elif archived_count >= cap:
                outcome.update(status="would_archive", reason=f"max_auto_archive_per_run ({cap}) reached; next run")
            else:
                client.remove_inbox_label(message_id)
                self.summary["gmail_write_calls"] += 1
                after = client.message_labels(message_id) or []
                if "INBOX" in after:
                    outcome.update(status="failed", reason="INBOX label still present after the archive call")
                else:
                    outcome.update(status="archived")
                    archived_count += 1
            if labels is not None:
                outcome["user_labels"] = xr_gmail_api.user_labels(labels)
            if writes and outcome["status"] != "would_archive":
                item["gmail_archive"] = outcome
                self.state.append({"event": "gmail_archive", "item_id": item["item_id"], **outcome})
            results.append({"item_id": item["item_id"], **outcome})
        self.summary["gmail_archived"] = sum(1 for row in results if row["status"] == "archived")
        self.summary["gmail_untagged"] = sum(1 for row in results if row["status"] == "untagged")
        return results

    def run(self):
        records = self.fetch()
        self.plan_search(records)
        self.ingest_candidates(records)
        self.fetch_bytes(records)
        self.scan_drops(records)
        self.match(records)
        if not self.args.dry_run:
            uploaded = self.attach(records)
            verified = self.verify(uploaded)
            archived = self.archive(verified + self.already_attached_this_call)
            self.summary.update({
                "uploaded": len(uploaded),
                "verified": len(verified),
                "archived": len(archived),
            })
            if self.archive_write_enabled:
                self.gmail_archive()
        active_states = {record["state"] for record in records}
        self.state.index["last_run"] = self.run_id
        self.state.index["last_run_time"] = self.now
        for record in records:
            record["last_run_id"] = self.run_id
            record["last_run_scheduled"] = self.args.scheduled
        self.state.save()
        counts = {}
        for record in records:
            counts[record["state"]] = counts.get(record["state"], 0) + 1
        self.summary.update({
            "auto_eligible": counts.get("auto_eligible", 0) + counts.get("approved", 0),
            "pending_review": counts.get("pending_review", 0),
            "needs_manual_portal_lookup": counts.get("needs_manual_portal_lookup", 0),
            "no_candidate": counts.get("no_candidate", 0),
            "already_attached": counts.get("already_attached", 0),
            "xero_write_calls": sum(1 for method, _ in (self._client.call_log if self._client else []) if method == "POST"),
            "xero_put_calls": 0,
            "phantom_transfers": sum(1 for record in records if record.get("phantom_transfer")),
            "excluded_by_bank_account": sum(self.excluded_bank_accounts.values()),
            "excluded_bank_accounts": dict(sorted(self.excluded_bank_accounts.items())),
        })
        review = xr_report.review_json(self.state)
        report_path = xr_report.write_report(self.paths["data"], self.run_id, review)
        if self.args.scheduled:
            self.state.index["scheduled_summary"] = {
                "review_items": review["needs_approval"],
                "manual_items": review["manual_portal"],
                "failure_items": review["other"],
            }
            self.state.save()
        return {"run_id": self.run_id, "summary": self.summary, "report": str(report_path)}


def emit(args, value):
    if args.json_output and isinstance(value, dict):
        print(json.dumps(value, sort_keys=True))
    else:
        if isinstance(value, dict):
            value = json.dumps(value, indent=2, sort_keys=True)
        print(value)


def main():
    args = parse_args()
    try:
        return dispatch(args)
    except Exception as error:  # one plain line, never a traceback
        print(f"error: {type(error).__name__}: {xr_secrets.redact(str(error))}", file=sys.stderr)
        return 1


def dispatch(args):
    if args.command == "config-check":
        pipeline = Pipeline(args)
        emit(args, {"ok": True, "tenant_alias": pipeline.config["tenant_alias"], "live_enabled": pipeline.config["live_enabled"], "auto_archive_enabled": pipeline.config.get("auto_archive_enabled", False)})
        return 0
    if args.command == "auth-xero":
        if args.offline:
            print("auth-xero is disabled in offline mode")
            return 0
        client_id = xr_secrets.required_secret("XERO_CLIENT_ID")
        tenant_id = args.data_dir and "pending" or ""
        client = XeroClient(client_id, tenant_id, "", xr_secrets)
        code, verifier = client.authorize(SCOPES)
        token = client.exchange_code(code, verifier)
        connections = client.list_connections()
        connection = connections[0]
        client.tenant_id = connection["tenantId"]
        xr_secrets.save_refresh_token(client.tenant_id, token["refresh_token"])
        print(f"Connected tenant: {connection.get('tenantName')} ({client.tenant_id})")
        return 0
    if args.command == "auth-gmail":
        if args.offline:
            print("auth-gmail is disabled in offline mode")
            return 0
        client_id = xr_secrets.required_secret("GMAIL_CLIENT_ID")
        gmail_secret = xr_secrets.required_secret("GMAIL_CLIENT_SECRET")
        account_label = args.account
        if not account_label:
            config = json.loads(Path(args.config).read_text(encoding="utf-8"))
            accounts = config.get("gmail_accounts") or []
            if not accounts:
                raise RuntimeError("no gmail_accounts in config and no --account given")
            account_label = accounts[0]
        scope = xr_gmail_api.MODIFY_SCOPE if args.allow_archive else xr_gmail_api.READONLY_SCOPE
        gmail_token = xr_gmail_api.authorize(client_id, gmail_secret, scope=scope)
        xr_secrets.save_refresh_token(account_label, gmail_token, service=xr_gmail_api.GMAIL_KEYCHAIN_SERVICE)
        print(f"Connected Gmail account label: {account_label} (scope: {scope.rsplit('/', 1)[-1]})")
        return 0
    pipeline = Pipeline(args)
    if args.command == "xero-fetch":
        records = pipeline.fetch()
        if pipeline.excluded_bank_accounts:
            print(f"notice: skipped lines on non-eligible bank accounts: {dict(sorted(pipeline.excluded_bank_accounts.items()))}", file=sys.stderr)
        emit(args, [record["transaction"] for record in records])
        return 0
    if args.command in {"plan-search", "ingest-candidates", "fetch-bytes", "scan-drops", "match"}:
        records = pipeline.fetch()
        pipeline.plan_search(records)
        pipeline.ingest_candidates(records)
        pipeline.fetch_bytes(records)
        pipeline.scan_drops(records)
        pipeline.match(records)
        pipeline.state.save()
        emit(args, {"run_id": pipeline.run_id, "items": len(records)})
        return 0
    if args.command == "run":
        result = pipeline.run()
        if args.json_output:
            print(json.dumps({"run_id": result["run_id"], "summary": result["summary"]}, sort_keys=True))
        else:
            print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    if args.command == "review":
        emit(args, xr_report.review_json(pipeline.state))
        return 0
    if args.command == "approve":
        pipeline.state.transition(args.item, "approved", pipeline.run_id, False, by=args.by)
        pipeline.state.save()
        emit(args, {"item_id": args.item, "state": "approved"})
        return 0
    if args.command == "reject":
        pipeline.state.transition(args.item, "rejected", pipeline.run_id, False)
        pipeline.state.save()
        emit(args, {"item_id": args.item, "state": "rejected"})
        return 0
    if args.command == "attach":
        records = [pipeline.state.index["items"][args.item]] if args.item else pipeline.state.items_in({"auto_eligible", "approved"})
        uploaded = pipeline.attach(records)
        pipeline.state.save()
        emit(args, {"uploaded": len(uploaded)})
        return 0
    if args.command == "verify":
        records = [pipeline.state.index["items"][args.item]] if args.item else pipeline.state.items_in({"uploaded_unverified"})
        verified = pipeline.verify(records)
        pipeline.state.save()
        emit(args, {"verified": len(verified)})
        return 0
    if args.command == "archive":
        records = [pipeline.state.index["items"][args.item]] if args.item else pipeline.state.items_in({"verified", "already_attached"})
        archived = pipeline.archive(records)
        pipeline.state.save()
        emit(args, {"archived": len(archived)})
        return 0
    if args.command == "gmail-archive":
        results = pipeline.gmail_archive(args.item)
        pipeline.state.save()
        mode = "live" if pipeline.archive_write_enabled and not args.dry_run else "preview (no Gmail writes: needs auto_archive_enabled true and --live, without --dry-run)"
        emit(args, {"mode": mode, "results": results, "gmail_write_calls": pipeline.summary["gmail_write_calls"]})
        return 0
    if args.command == "correct":
        item = pipeline.state.index["items"][args.item]
        row = {
            "item_id": args.item,
            "kind": args.kind,
            "note": args.note,
            "transaction": item.get("transaction"),
            "filename": item.get("filename"),
            "attachment_id": item.get("attachment_id"),
            "sha256": item.get("sha256"),
            "gmail_message_id": item.get("gmail_message_id"),
            "score": item.get("score"),
            "signals": item.get("signals"),
            "auto": item.get("auto", False),
        }
        pipeline.state.append_jsonl(pipeline.state.corrections_path, row)
        pipeline.state.transition(args.item, "correction_logged", pipeline.run_id, False, correction_kind=args.kind)
        vendor = xr_match.vendor_for(item["transaction"]["contact_name"], pipeline.aliases)
        if vendor:
            pipeline.state.set_vendor_hold(vendor, pipeline.config["correction_hold_days"], args.note)
        pipeline.state.save()
        transaction = item["transaction"]
        print(
            f"Xero cannot remove attachments through its API. Open {transaction['contact_name']} {transaction['date']} "
            f"${transaction['total']} ({transaction['type']}), open its files, remove {item.get('filename')}, "
            "then tell me 'removed'."
        )
        return 0
    if args.command == "confirm-removed":
        item = pipeline.state.index["items"][args.item]
        transaction = item["transaction"]
        attachments = pipeline.client.list_attachments(transaction["endpoint"], transaction["guid"])
        if item.get("filename") in {entry["FileName"] for entry in attachments}:
            print("Attachment is still present in Xero")
            return 1
        pipeline.state.transition(args.item, "removed_confirmed", pipeline.run_id, False)
        next_state = "excluded" if item.get("correction_kind") == "personal_expense" else "pending_review"
        pipeline.state.transition(args.item, next_state, pipeline.run_id, False)
        pipeline.state.save()
        emit(args, {"item_id": args.item, "state": next_state})
        return 0
    if args.command == "vendor-trust":
        if args.reset:
            pipeline.state.clear_vendor_hold(args.reset)
            pipeline.state.save()
            emit(args, {"reset": args.reset})
        else:
            emit(args, pipeline.state.vendor_holds())
        return 0
    if args.command == "notify-check":
        notify = xr_notify.NotifyStore(pipeline.paths["data"])
        emit(args, notify.decision(pipeline.state, args.now or xr_state.iso_utc()))
        return 0
    if args.command == "notify":
        notify = xr_notify.NotifyStore(pipeline.paths["data"])
        if args.ack:
            notify.record_sent("ack", "acknowledged", args.now or xr_state.iso_utc())
            emit(args, {"decision": "SKIP", "reason": "acknowledged"})
            return 0
        if args.sent:
            notify.record_sent(args.sent, args.result, args.now or xr_state.iso_utc())
            emit(args, {"recorded": args.sent})
            return 0
        if args.channel == "macos":
            decision = notify.decision(pipeline.state, args.now or xr_state.iso_utc())
            if decision["decision"] == "SEND":
                result = xr_notify.send_macos(decision["message"])
                notify.record_sent("macos", result, args.now or xr_state.iso_utc())
            emit(args, decision)
            return 0
    if args.command == "calibration-report":
        emit(args, xr_report.calibration(pipeline.state))
        return 0
    if args.command == "verify-state":
        invalid = []
        for item_id, item in pipeline.state.index["items"].items():
            try:
                previous = None
                with pipeline.state.audit_path.open(encoding="utf-8") as stream:
                    for line in stream:
                        row = json.loads(line)
                        if row.get("item_id") != item_id or row.get("event") != "transition":
                            continue
                        if previous and row["to_state"] not in xr_state.TRANSITIONS.get(previous, set()):
                            invalid.append({"item_id": item_id, "from": previous, "to": row["to_state"]})
                        previous = row["to_state"]
                if previous != item["state"]:
                    invalid.append({"item_id": item_id, "index_state": item["state"], "audit_state": previous})
            except FileNotFoundError:
                invalid.append({"item_id": item_id, "reason": "audit log missing"})
        if invalid:
            emit(args, {"ok": False, "invalid": invalid})
            return 1
        print("STATE_OK")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
