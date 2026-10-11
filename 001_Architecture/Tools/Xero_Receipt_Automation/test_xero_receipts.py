import argparse
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import xr_config
import xr_gmail_api
import xr_match
import xr_secrets
import xr_state
from xero_receipts import Pipeline


ROOT = Path(__file__).resolve().parent
PYTHON = sys.executable

# The repo ignores *.pdf, so the synthetic fixture PDFs never reach git (they were lost at
# promotion). Rebuild them here, byte-identical every time, so the suite runs on a fresh checkout.
FIXTURE_PDF_TEXT = {
    "Fixture_Attachment_Adobe.pdf": "Adobe Creative Cloud invoice date 2026-05-12 Total $57.99",
    "Fixture_Attachment_OpenAI.pdf": "OpenAI invoice date 2026-05-01 Total $20.00",
    "Fixture_Attachment_Anthropic_A.pdf": "Anthropic invoice A date 2026-05-20 Total $20.00",
    "Fixture_Attachment_Anthropic_B.pdf": "Anthropic invoice B date 2026-05-21 Total $20.00",
    "Fixture_Manual_Jshad_Invoice.pdf": "Jshad Invoice date 2026-05-15 Total $49.00",
}


def minimal_pdf(text):
    """A one-page ASCII PDF whose text pypdf can extract."""
    stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(objects, 1):
        offsets.append(len(out))
        out += f"{number} 0 obj\n".encode() + body + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    out += b"".join(f"{offset:010d} 00000 n \n".encode() for offset in offsets)
    out += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    return bytes(out)


def ensure_fixture_pdfs():
    for name, text in FIXTURE_PDF_TEXT.items():
        path = ROOT / name
        if not path.is_file():
            path.write_bytes(minimal_pdf(text))


ensure_fixture_pdfs()


class TemporaryPaths:
    def __enter__(self):
        self.data = Path(tempfile.mkdtemp())
        self.intake = Path(tempfile.mkdtemp())
        self.archive = Path(tempfile.mkdtemp())
        return self.data, self.intake, self.archive

    def __exit__(self, *_):
        return False


def args(**overrides):
    values = {
        "config": str(ROOT / "Fixture_Config.json"),
        "data_dir": None,
        "intake_dir": None,
        "archive_dir": None,
        "dry_run": False,
        "offline": True,
        "fixtures_dir": str(ROOT),
        "simulate_live": False,
        "fake_verify_fail": False,
        "live": False,
        "scheduled": False,
        "now": None,
        "json_output": True,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


class XeroReceiptTests(unittest.TestCase):
    def test_pdf_extraction_and_score_table(self):
        aliases = json.loads((ROOT / "Fixture_Vendor_Aliases.json").read_text())
        transaction = {"contact_name": "Adobe", "date": "2026-05-12", "total": 57.99, "attachment_count": 0}
        candidate = {
            "sender": "receipts@adobe.com",
            "subject": "Adobe Creative Cloud receipt",
            "date": "2026-05-12",
            "body_text": "Adobe invoice date 2026-05-12 Total $57.99",
            "attachments": [{"filename": "adobe.pdf"}],
            "staged_fixture": str(ROOT / "Fixture_Attachment_Adobe.pdf"),
        }
        score, signals, exact, vendor = xr_match.score_candidate(transaction, candidate, aliases)
        self.assertEqual(score, 1.00)
        self.assertEqual(signals, {"amount": 0.40, "vendor": 0.30, "date": 0.20, "receipt_evidence": 0.10})
        self.assertTrue(exact)
        self.assertEqual(vendor, "adobe")
        no_date = dict(candidate, date="")
        no_date["body_text"] = "Adobe invoice Total $57.99"
        score, signals, *_ = xr_match.score_candidate(transaction, no_date, aliases)
        self.assertEqual(score, 0.80)

    def test_classification_hard_gates_and_tie(self):
        aliases = json.loads((ROOT / "Fixture_Vendor_Aliases.json").read_text())
        config = json.loads((ROOT / "Fixture_Config.json").read_text())
        transaction = {"contact_name": "Anthropic", "date": "2026-05-20", "total": 20.00, "attachment_count": 0}
        candidates = []
        for letter in ("A", "B"):
            candidates.append({
                "sender": "invoice@anthropic.com",
                "subject": f"Anthropic invoice {letter}",
                "date": "2026-05-20",
                "body_text": "Anthropic invoice Total $20.00",
                "attachments": [{"filename": f"{letter}.pdf"}],
                "staged_fixture": str(ROOT / f"Fixture_Attachment_Anthropic_{letter}.pdf"),
            })
        classification, scored, best, lead = xr_match.classify(transaction, candidates, aliases, config)
        self.assertEqual(classification, "pending_review")
        self.assertEqual(scored[0]["score"], 1.00)
        self.assertEqual(lead, 0.00)
        connector_only = dict(candidates[0])
        connector_only.pop("staged_fixture")
        classification, _, best, _ = xr_match.classify(transaction, [connector_only], aliases, config)
        self.assertEqual(classification, "pending_review")
        self.assertIsNone(best.get("byte_evidence"))

    def test_state_rejects_invalid_transition_and_is_idempotent(self):
        with TemporaryPaths() as (data, _, _):
            state = xr_state.StateStore(data)
            transaction = {"item_id": "BankTransactions:test", "endpoint": "BankTransactions", "guid": "test"}
            state.discover("run-1", transaction)
            state.transition("BankTransactions:test", "search_planned", "run-1")
            state.transition("BankTransactions:test", "candidates_received", "run-1")
            state.transition("BankTransactions:test", "auto_eligible", "run-1")
            state.transition("BankTransactions:test", "upload_pending", "run-1")
            state.transition("BankTransactions:test", "uploaded_unverified", "run-1")
            state.transition("BankTransactions:test", "verified", "run-1")
            state.transition("BankTransactions:test", "archived", "run-1")
            with self.assertRaises(ValueError):
                state.transition("BankTransactions:test", "upload_pending", "run-2")

    def test_config_check_refuses_missing_directory_without_creating(self):
        with TemporaryPaths() as (_, intake, archive):
            missing = intake / "missing-data"
            with self.assertRaises(FileNotFoundError):
                Pipeline(args(data_dir=str(missing), intake_dir=str(intake), archive_dir=str(archive)))
            self.assertFalse(missing.exists())

    def test_dry_run_exact_counts_and_no_file_moves(self):
        with patch("xero_receipts.time.sleep", lambda _: None), TemporaryPaths() as (data, intake, archive):
            before = sorted(path.name for path in archive.iterdir())
            result = Pipeline(args(data_dir=str(data), intake_dir=str(intake), archive_dir=str(archive), dry_run=True)).run()
            self.assertEqual(result["summary"]["auto_eligible"], 2)
            self.assertEqual(result["summary"]["pending_review"], 2)
            self.assertEqual(result["summary"]["needs_manual_portal_lookup"], 1)
            self.assertEqual(result["summary"]["no_candidate"], 1)
            self.assertEqual(result["summary"]["excluded_by_bank_account"], 1)  # t7 sits on Relay Business Checking
            self.assertEqual(result["summary"]["excluded_bank_accounts"], {"Relay Business Checking": 1})
            self.assertEqual(result["summary"]["xero_write_calls"], 0)
            self.assertEqual(before, [])

    def test_simulated_live_is_post_only_hash_verified_and_idempotent(self):
        with patch("xero_receipts.time.sleep", lambda _: None), TemporaryPaths() as (data, intake, archive):
            first = Pipeline(args(data_dir=str(data), intake_dir=str(intake), archive_dir=str(archive), simulate_live=True)).run()
            second = Pipeline(args(data_dir=str(data), intake_dir=str(intake), archive_dir=str(archive), simulate_live=True)).run()
            self.assertEqual(first["summary"]["uploaded"], 2)
            self.assertEqual(first["summary"]["verified"], 2)
            self.assertEqual(first["summary"]["archived"], 2)
            self.assertEqual(first["summary"]["xero_put_calls"], 0)
            self.assertEqual(second["summary"]["uploaded"], 0)
            self.assertEqual(second["summary"]["xero_write_calls"], 0)
            self.assertTrue((archive / "05-12-2026_Adobe-Creative-Cloud_57.99.pdf").is_file())
            self.assertTrue((archive / "05-03-2026_OpenAI_20.00.pdf").is_file())

    def test_only_write_is_attachment_post(self):
        # Simulated live run: every write the pipeline makes is a POST to .../Attachments/<name>.
        with patch("xero_receipts.time.sleep", lambda _: None), TemporaryPaths() as (data, intake, archive):
            pipeline = Pipeline(args(data_dir=str(data), intake_dir=str(intake), archive_dir=str(archive), simulate_live=True))
            pipeline.run()
            methods = {method for method, _ in pipeline.client.call_log}
            self.assertEqual(methods, {"GET", "POST"})
            for method, path in pipeline.client.call_log:
                if method == "POST":
                    self.assertRegex(path, r"^(BankTransactions|Invoices)/[^/]+/Attachments/[^/]+$")
        # Real client: the HTTP method actually sent for an upload is POST.
        from xr_xero_api import XeroClient
        sent = []

        class Response:
            status = 200
            def read(self):
                return b'{"Attachments": [{"AttachmentID": "a1", "FileName": "f.pdf", "ContentLength": 3}]}'
            def __enter__(self):
                return self
            def __exit__(self, *_):
                return False

        client = XeroClient("cid", "tenant", "rt")
        client.access_token = "token"
        with patch("xr_xero_api.urllib.request.urlopen", lambda request, timeout: sent.append(request.get_method()) or Response()):
            self.assertEqual(client.post_attachment("BankTransactions", "g1", "f.pdf", b"abc", "application/pdf")["AttachmentID"], "a1")
        self.assertEqual(sent, ["POST"])

    def _matched(self, data, intake, archive):
        pipeline = Pipeline(args(data_dir=str(data), intake_dir=str(intake), archive_dir=str(archive), simulate_live=True))
        records = pipeline.fetch()
        pipeline.plan_search(records)
        pipeline.ingest_candidates(records)
        pipeline.fetch_bytes(records)
        pipeline.scan_drops(records)
        pipeline.match(records)
        return pipeline, records

    def test_same_filename_collision_suffix_or_already_attached(self):
        name = "05-12-2026_Adobe-Creative-Cloud_57.99.pdf"
        adobe_bytes = (ROOT / "Fixture_Attachment_Adobe.pdf").read_bytes()
        for existing, expected in ((b"old", "suffix"), (adobe_bytes, "already")):
            with patch("xero_receipts.time.sleep", lambda _: None), TemporaryPaths() as (data, intake, archive):
                pipeline, records = self._matched(data, intake, archive)
                pipeline.client.attachments["t1-adobe"] = [{"AttachmentID": "x", "FileName": name, "ContentLength": len(existing)}]
                pipeline.client.bytes[("t1-adobe", name)] = existing
                pipeline.attach(records)
                adobe = next(record for record in records if record["item_id"] == "BankTransactions:t1-adobe")
                if expected == "suffix":
                    self.assertEqual(adobe["state"], "uploaded_unverified")
                    self.assertEqual(adobe["filename"], name[:-4] + "_" + adobe["sha256"][:8] + ".pdf")
                else:
                    self.assertEqual(adobe["state"], "already_attached")
                self.assertNotIn(("POST", f"BankTransactions/t1-adobe/Attachments/{name}"), pipeline.client.call_log)

    def test_ocr_only_and_vendor_hold_never_auto(self):
        aliases = json.loads((ROOT / "Fixture_Vendor_Aliases.json").read_text())
        config = json.loads((ROOT / "Fixture_Config.json").read_text())
        transaction = {"contact_name": "Adobe", "date": "2026-05-12", "total": 57.99, "currency": "USD"}
        candidate = {
            "sender": "receipts@adobe.com", "subject": "Adobe receipt", "date": "2026-05-12",
            "body_text": "Adobe Total $57.99", "attachments": [{"filename": "adobe.pdf"}],
            "staged_fixture": str(ROOT / "Fixture_Attachment_Adobe.pdf"),
        }
        self.assertEqual(xr_match.classify(transaction, [candidate], aliases, config)[0], "auto_eligible")
        self.assertEqual(xr_match.classify(transaction, [candidate], aliases, config, {"adobe": {}})[0], "pending_review")
        with patch("xr_match.extract_text", lambda path: {"text": "Adobe Total $57.99", "confidence": "ocr"}):
            self.assertEqual(xr_match.classify(transaction, [candidate], aliases, config)[0], "pending_review")
        self.assertEqual(xr_match.classify(dict(transaction, currency="EUR"), [candidate], aliases, config)[0], "pending_review")

    def test_rerun_after_manual_drop_and_after_failed_verify(self):
        with patch("xero_receipts.time.sleep", lambda _: None), TemporaryPaths() as (data, intake, archive):
            Pipeline(args(data_dir=str(data), intake_dir=str(intake), archive_dir=str(archive), dry_run=True)).run()
            (intake / "jshad-Invoice.pdf").write_bytes((ROOT / "Fixture_Manual_Jshad_Invoice.pdf").read_bytes())
            pipeline = Pipeline(args(data_dir=str(data), intake_dir=str(intake), archive_dir=str(archive), dry_run=True))
            pipeline.run()
            self.assertEqual(pipeline.state.index["items"]["BankTransactions:t4-jshad"]["state"], "auto_eligible")
        with patch("xero_receipts.time.sleep", lambda _: None), TemporaryPaths() as (data, intake, archive):
            (intake / "jshad-Invoice.pdf").write_bytes((ROOT / "Fixture_Manual_Jshad_Invoice.pdf").read_bytes())
            Pipeline(args(data_dir=str(data), intake_dir=str(intake), archive_dir=str(archive), simulate_live=True, fake_verify_fail=True)).run()
            pipeline = Pipeline(args(data_dir=str(data), intake_dir=str(intake), archive_dir=str(archive), simulate_live=True))
            second = pipeline.run()
            item = pipeline.state.index["items"]["BankTransactions:t4-jshad"]
            self.assertEqual(item["state"], "pending_review")
            self.assertIn("hash-match", item["reason"])
            self.assertEqual(second["summary"]["uploaded"], 0)
            self.assertTrue((intake / "jshad-Invoice.pdf").is_file())

    def test_archive_gate_leaves_manual_drop_in_intake(self):
        with patch("xero_receipts.time.sleep", lambda _: None), TemporaryPaths() as (data, intake, archive):
            (intake / "jshad-Invoice.pdf").write_bytes((ROOT / "Fixture_Manual_Jshad_Invoice.pdf").read_bytes())
            result = Pipeline(args(data_dir=str(data), intake_dir=str(intake), archive_dir=str(archive), simulate_live=True, fake_verify_fail=True)).run()
            self.assertEqual(result["summary"]["verified"], 0)
            self.assertEqual(result["summary"]["archived"], 0)
            self.assertTrue((intake / "jshad-Invoice.pdf").is_file())
            self.assertEqual(list(archive.iterdir()), [])

    def test_manual_drop_moves_after_hash_verification(self):
        with patch("xero_receipts.time.sleep", lambda _: None), TemporaryPaths() as (data, intake, archive):
            (intake / "jshad-Invoice.pdf").write_bytes((ROOT / "Fixture_Manual_Jshad_Invoice.pdf").read_bytes())
            result = Pipeline(args(data_dir=str(data), intake_dir=str(intake), archive_dir=str(archive), simulate_live=True)).run()
            self.assertEqual(result["summary"]["archived"], 3)
            self.assertFalse((intake / "jshad-Invoice.pdf").exists())
            self.assertTrue((archive / "05-15-2026_Jshad_49.00.pdf").is_file())

    def test_notification_once_per_iso_week(self):
        common = [
            PYTHON,
            str(ROOT / "xero_receipts.py"),
            "--config", str(ROOT / "Fixture_Config.json"),
            "--offline",
            "--fixtures-dir", str(ROOT),
        ]
        with patch("xero_receipts.time.sleep", lambda _: None), TemporaryPaths() as (data, intake, archive):
            base = common + [
                "notify-check",
                "--data-dir", str(data), "--intake-dir", str(intake), "--archive-dir", str(archive),
                "--json",
            ]
            Pipeline(args(data_dir=str(data), intake_dir=str(intake), archive_dir=str(archive), dry_run=True, scheduled=True)).run()
            first = json.loads(subprocess.check_output(base + ["--now", "2026-05-23T08:00:00-04:00"]).splitlines()[-1])
            self.assertEqual(first["decision"], "SEND")
            self.assertIn("/xero", first["message"])
            subprocess.check_call(common + [
                "notify", "--config", str(ROOT / "Fixture_Config.json"), "--offline", "--fixtures-dir", str(ROOT),
                "--data-dir", str(data), "--intake-dir", str(intake), "--archive-dir", str(archive),
                "--sent", "push", "--result", "test", "--now", "2026-05-23T08:01:00-04:00",
            ])
            second = json.loads(subprocess.check_output(base + ["--now", "2026-05-24T09:00:00-04:00"]).splitlines()[-1])
            third = json.loads(subprocess.check_output(base + ["--now", "2026-05-30T08:00:00-04:00"]).splitlines()[-1])
            self.assertEqual(second["decision"], "SKIP")
            self.assertEqual(third["decision"], "SEND")

    def test_correction_is_durable_and_vendor_goes_review_only(self):
        with patch("xero_receipts.time.sleep", lambda _: None), TemporaryPaths() as (data, intake, archive):
            Pipeline(args(data_dir=str(data), intake_dir=str(intake), archive_dir=str(archive), simulate_live=True)).run()
            review = json.loads(subprocess.check_output([
                PYTHON, str(ROOT / "xero_receipts.py"), "review", "--config", str(ROOT / "Fixture_Config.json"),
                "--offline", "--fixtures-dir", str(ROOT), "--data-dir", str(data), "--intake-dir", str(intake),
                "--archive-dir", str(archive), "--json",
            ]).decode())
            adobe = next(item["item_id"] for item in review["auto_attached_this_week"] if "Adobe" in json.dumps(item))
            output = subprocess.check_output([
                PYTHON, str(ROOT / "xero_receipts.py"), "correct", "--item", adobe, "--kind", "wrong_receipt",
                "--note", "you tagged this one wrong", "--config", str(ROOT / "Fixture_Config.json"), "--offline",
                "--fixtures-dir", str(ROOT), "--data-dir", str(data), "--intake-dir", str(intake),
                "--archive-dir", str(archive), "--json",
            ]).decode()
            self.assertIn("remove", output.lower())
            correction = json.loads((data / "Corrections.jsonl").read_text().splitlines()[-1])
            self.assertEqual(correction["note"], "you tagged this one wrong")
            holds = json.loads(subprocess.check_output([
                PYTHON, str(ROOT / "xero_receipts.py"), "vendor-trust", "--show", "--config", str(ROOT / "Fixture_Config.json"),
                "--offline", "--fixtures-dir", str(ROOT), "--data-dir", str(data), "--intake-dir", str(intake),
                "--archive-dir", str(archive), "--json",
            ]).decode().splitlines()[-1])
            self.assertIn("adobe", holds)

    # ---- Bank account badges -------------------------------------------------------------

    def test_bank_account_badge_in_review_json(self):
        from xr_xero_api import XeroClient
        raw = {"BankTransactionID": "g1", "Type": "SPEND", "DateString": "2026-05-12T00:00:00", "Total": 5.0,
               "Contact": {"Name": "Adobe"}, "BankAccount": {"AccountID": "a1", "Code": "090", "Name": "Chase Ink"},
               "LineItems": [{"Description": "Creative Cloud"}, {"Description": "Tax"}]}
        normalized = XeroClient.normalize(raw)
        self.assertEqual(normalized["BankAccount"], {"AccountID": "a1", "Code": "090", "Name": "Chase Ink"})
        self.assertEqual(normalized["Description"], "Creative Cloud Tax")
        self.assertIsNone(XeroClient.normalize({"InvoiceID": "i1", "Type": "ACCPAY"})["BankAccount"])
        with patch("xero_receipts.time.sleep", lambda _: None), TemporaryPaths() as (data, intake, archive):
            Pipeline(args(data_dir=str(data), intake_dir=str(intake), archive_dir=str(archive), dry_run=True)).run()
            review = Pipeline(args(data_dir=str(data), intake_dir=str(intake), archive_dir=str(archive))).state
            from xr_report import review_json
            entries = {entry["item_id"]: entry for section in ("needs_approval", "auto_attached_this_week", "manual_portal", "other") for entry in review_json(review)[section]}
            self.assertEqual(entries["BankTransactions:t1-adobe"]["bank_account"], {"account_id": "acct-chase-ink", "code": "CHASE", "name": "Chase Ink"})
            # Xero omitted Name on this line; it is filled from another line on the same AccountID.
            self.assertEqual(entries["BankTransactions:t2-openai"]["bank_account"]["name"], "Chase Ink")
            self.assertEqual(entries["BankTransactions:t5-pge"]["bank_account"]["name"], "CapitalOne Spark Miles")
            self.assertIsNone(entries["Invoices:t3-anthropic"]["bank_account"])  # bills have no bank account

    def test_bank_account_backfills_already_finished_items(self):
        with patch("xero_receipts.time.sleep", lambda _: None), TemporaryPaths() as (data, intake, archive):
            pipeline = Pipeline(args(data_dir=str(data), intake_dir=str(intake), archive_dir=str(archive), simulate_live=True))
            pipeline.run()
            adobe = pipeline.state.index["items"]["BankTransactions:t1-adobe"]
            self.assertEqual(adobe["state"], "archived")
            adobe["transaction"].pop("bank_account")  # an item finished before badges existed
            pipeline.state.save()
            later = Pipeline(args(data_dir=str(data), intake_dir=str(intake), archive_dir=str(archive), dry_run=True))
            later.fetch()
            self.assertEqual(later.state.index["items"]["BankTransactions:t1-adobe"]["transaction"]["bank_account"]["name"], "Chase Ink")

    # ---- Eligible bank accounts (expense credit cards only) ------------------------------

    def test_bank_account_allowlist_matching(self):
        allow = [{"name": "Chase Ink", "account_id": "acct-chase-ink"}, {"name": "Capital One Spark Miles", "account_id": ""}]
        self.assertTrue(xr_match.bank_account_eligible({"account_id": "acct-chase-ink", "name": "Renamed"}, allow))
        self.assertFalse(xr_match.bank_account_eligible({"account_id": "other", "name": "Chase Ink"}, allow))  # id entry: id only
        self.assertTrue(xr_match.bank_account_eligible({"account_id": "x", "name": "CapitalOne  Spark-Miles"}, allow))
        for name in ("Relay Business Checking", "Mercury Checking", "Mercury Savings", "Wise Business", "PayPal Business", "Etsy Payment Balance", ""):
            self.assertFalse(xr_match.bank_account_eligible({"account_id": "z", "name": name}, allow))
        self.assertFalse(xr_match.bank_account_eligible(None, allow))
        self.assertFalse(xr_match.bank_account_eligible({"account_id": "acct-chase-ink"}, []))  # empty list: nothing eligible

    def test_items_found_before_allowlist_are_parked_and_never_attached(self):
        with patch("xero_receipts.time.sleep", lambda _: None), TemporaryPaths() as (data, intake, archive):
            config = json.loads((ROOT / "Fixture_Config.json").read_text())
            (data / "open.json").write_text(json.dumps(dict(config, eligible_bank_accounts=config["eligible_bank_accounts"] + [{"name": "CapitalOne Spark Miles"}, {"name": "Chase Ink"}])))
            Pipeline(args(config=str(data / "open.json"), data_dir=str(data), intake_dir=str(intake), archive_dir=str(archive), dry_run=True)).run()
            state = xr_state.StateStore(data)
            self.assertEqual(state.index["items"]["BankTransactions:t5-pge"]["state"], "pending_review")
            self.assertEqual(state.index["items"]["BankTransactions:t2-openai"]["state"], "auto_eligible")
            # Tony narrows the allowlist to Chase only: the CapitalOne PG&E line leaves "Needs your approval".
            (data / "chase.json").write_text(json.dumps(dict(config, eligible_bank_accounts=[{"name": "Chase Ink", "account_id": "acct-chase-ink"}])))
            pipeline = Pipeline(args(config=str(data / "chase.json"), data_dir=str(data), intake_dir=str(intake), archive_dir=str(archive), dry_run=True))
            pipeline.run()
            pge = pipeline.state.index["items"]["BankTransactions:t5-pge"]
            self.assertEqual(pge["state"], "no_candidate")
            self.assertTrue(pge["ineligible_bank_account"])
            # Allowlist fixed again: the parked item is matched normally and loses its flag.
            again = Pipeline(args(config=str(data / "open.json"), data_dir=str(data), intake_dir=str(intake), archive_dir=str(archive), dry_run=True))
            again.run()
            self.assertEqual(again.state.index["items"]["BankTransactions:t5-pge"]["state"], "pending_review")
            self.assertNotIn("ineligible_bank_account", again.state.index["items"]["BankTransactions:t5-pge"])
            # Attach-time guard: an item approved earlier whose line is no longer on an eligible card is refused.
            (data / "none.json").write_text(json.dumps(dict(config, eligible_bank_accounts=[{"name": "Nothing"}])))
            live = Pipeline(args(config=str(data / "none.json"), data_dir=str(data), intake_dir=str(intake), archive_dir=str(archive), simulate_live=True))
            openai = live.state.index["items"]["BankTransactions:t2-openai"]
            live.attach([openai])
            self.assertEqual(openai["state"], "no_candidate")
            self.assertFalse([call for call in live.client.call_log if call[0] == "POST"])

    # ---- Etsy-integration phantom transfers ----------------------------------------------

    def test_etsy_phantom_transfer_is_never_matched_or_attached(self):
        aliases = json.loads((ROOT / "Fixture_Vendor_Aliases.json").read_text())
        config = json.loads((ROOT / "Fixture_Config.json").read_text())
        candidates = json.loads((ROOT / "Fixture_Gmail_Candidates.json").read_text())["items"]["BankTransactions:t7-etsy-phantom"]
        phantom = {"contact_name": "Etsy", "reference": "", "description": "Bank Transfer to Etsy Payment Balance",
                   "date": "2026-05-01", "total": 10.98, "currency": "USD",
                   "bank_account": {"name": "Relay Business Checking"}}
        # Without the guard the real Etsy payment email would land in "Needs your approval".
        self.assertEqual(xr_match.classify(phantom, candidates, aliases, config)[0], "pending_review")
        self.assertIsNotNone(xr_match.phantom_transfer_reason(phantom))
        self.assertIsNone(xr_match.phantom_transfer_reason(dict(phantom, description="Etsy ads", bank_account={"name": "Chase Ink"})))
        self.assertIsNone(xr_match.phantom_transfer_reason(dict(phantom, bank_account={"name": "Etsy Payment Balance"})))
        store_named = dict(phantom, contact_name="IkigaiDigitalStudio", description="Bank Transfer to IkigaiDigitalStudio Payment Balance")
        self.assertIsNotNone(xr_match.phantom_transfer_reason(store_named))  # store name need not say Etsy
        with patch("xero_receipts.time.sleep", lambda _: None), TemporaryPaths() as (data, intake, archive):
            # Layer 1: Relay is not an eligible account, so the line is never even discovered.
            pipeline = Pipeline(args(data_dir=str(data), intake_dir=str(intake), archive_dir=str(archive), simulate_live=True))
            pipeline.run()
            self.assertNotIn("BankTransactions:t7-etsy-phantom", pipeline.state.index["items"])
        with patch("xero_receipts.time.sleep", lambda _: None), TemporaryPaths() as (data, intake, archive):
            # Layer 2: even if Relay were wrongly allowlisted, the phantom guard still refuses it.
            loose = dict(config, eligible_bank_accounts=config["eligible_bank_accounts"] + [{"name": "Relay Business Checking"}])
            (data / "loose.json").write_text(json.dumps(loose))
            pipeline = Pipeline(args(config=str(data / "loose.json"), data_dir=str(data), intake_dir=str(intake), archive_dir=str(archive), simulate_live=True))
            pipeline.run()
            item = pipeline.state.index["items"]["BankTransactions:t7-etsy-phantom"]
            self.assertEqual(item["state"], "no_candidate")
            self.assertTrue(item["phantom_transfer"])
            self.assertFalse([call for call in pipeline.client.call_log if "t7-etsy-phantom" in call[1]])
            with self.assertRaises(ValueError):  # cannot be approved into an attach either
                pipeline.state.transition("BankTransactions:t7-etsy-phantom", "approved", "run-x")
            from xr_report import review_json
            flagged = {entry["item_id"]: entry for entry in review_json(pipeline.state)["flagged"]}
            self.assertIn("phantom transfer", flagged["BankTransactions:t7-etsy-phantom"]["flags"][0])

    # ---- Gmail archive (remove INBOX only) -----------------------------------------------

    def _gmail_writes(self, pipeline):
        return [call for client in pipeline._gmail_clients.values() if client for call in client.call_log if call[0] == "POST"]

    def test_user_labels_ignore_system_labels(self):
        self.assertEqual(xr_gmail_api.user_labels(["INBOX", "UNREAD", "IMPORTANT", "STARRED", "SENT", "DRAFT", "CATEGORY_UPDATES"]), [])
        self.assertEqual(xr_gmail_api.user_labels(["INBOX", "Label_7"]), ["Label_7"])

    def test_tagged_email_is_archived_untagged_is_flagged_and_left_alone(self):
        with patch("xero_receipts.time.sleep", lambda _: None), TemporaryPaths() as (data, intake, archive):
            pipeline = Pipeline(args(data_dir=str(data), intake_dir=str(intake), archive_dir=str(archive), simulate_live=True))
            result = pipeline.run()
            fake = pipeline._gmail_clients["tony_personal"]
            self.assertEqual(result["summary"]["gmail_archived"], 1)
            self.assertEqual(result["summary"]["gmail_untagged"], 1)
            # Exactly one Gmail write, and it only removes INBOX from the tagged Adobe email.
            self.assertEqual(self._gmail_writes(pipeline), [("POST", "messages/gm-adobe/modify", {"removeLabelIds": ["INBOX"]})])
            self.assertEqual(fake.labels["gm-adobe"], ["UNREAD", "CATEGORY_UPDATES", "Label_12"])
            self.assertIn("INBOX", fake.labels["gm-openai"])  # untagged: untouched
            items = pipeline.state.index["items"]
            self.assertEqual(items["BankTransactions:t1-adobe"]["gmail_archive"]["status"], "archived")
            self.assertEqual(items["BankTransactions:t2-openai"]["gmail_archive"]["status"], "untagged")
            from xr_report import review_json
            flagged = {entry["item_id"]: entry for entry in review_json(pipeline.state)["flagged"]}
            self.assertIn("no Gmail label", flagged["BankTransactions:t2-openai"]["flags"][0])
            # Never touched: unverified items (PG&E pending review, Anthropic tie) and the phantom line.
            touched = {call[1].split("/")[1] for call in fake.call_log}
            self.assertEqual(touched, {"gm-adobe", "gm-openai"})
            # Second run: Adobe is done, OpenAI is re-checked (Tony may have labelled it) but not written.
            again = Pipeline(args(data_dir=str(data), intake_dir=str(intake), archive_dir=str(archive), simulate_live=True))
            again.run()
            self.assertEqual(self._gmail_writes(again), [])

    def test_gmail_archive_gate_off_is_read_only_preview(self):
        with patch("xero_receipts.time.sleep", lambda _: None), TemporaryPaths() as (data, intake, archive):
            first = Pipeline(args(data_dir=str(data), intake_dir=str(intake), archive_dir=str(archive), simulate_live=True))
            first.archive_write_enabled = False  # attach + verify only
            first.run()
            self.assertEqual(self._gmail_writes(first), [])
            preview = Pipeline(args(data_dir=str(data), intake_dir=str(intake), archive_dir=str(archive)))
            statuses = {row["item_id"]: row["status"] for row in preview.gmail_archive()}
            self.assertEqual(statuses, {"BankTransactions:t1-adobe": "would_archive", "BankTransactions:t2-openai": "untagged"})
            self.assertEqual(self._gmail_writes(preview), [])
            self.assertNotIn("gmail_archive", preview.state.index["items"]["BankTransactions:t1-adobe"])
            dry = Pipeline(args(data_dir=str(data), intake_dir=str(intake), archive_dir=str(archive), simulate_live=True, dry_run=True))
            dry.gmail_archive()
            self.assertEqual(self._gmail_writes(dry), [])

    def test_write_gates_need_their_own_flag_and_live(self):
        with TemporaryPaths() as (data, intake, archive):
            config = json.loads((ROOT / "Fixture_Config.json").read_text())
            def gates(live, offline, simulate, **flags):
                path = data / "gate_config.json"
                path.write_text(json.dumps(dict(config, **flags)))
                pipeline = Pipeline(args(config=str(path), data_dir=str(data), intake_dir=str(intake), archive_dir=str(archive), live=live, offline=offline, simulate_live=simulate))
                return pipeline.write_enabled, pipeline.archive_write_enabled
            self.assertEqual(gates(True, False, False), (False, False))
            self.assertEqual(gates(False, False, False, auto_archive_enabled=True, live_enabled=True), (False, False))  # no --live
            self.assertEqual(gates(True, False, False, auto_archive_enabled=True), (False, True))
            self.assertEqual(gates(True, False, False, live_enabled=True), (True, False))  # attach flag does not unlock archive
            self.assertEqual(gates(True, False, True), (False, False))  # --simulate-live can no longer bypass real flags

    def test_read_only_gmail_token_refuses_before_any_write(self):
        with patch("xero_receipts.time.sleep", lambda _: None), TemporaryPaths() as (data, intake, archive):
            pipeline = Pipeline(args(data_dir=str(data), intake_dir=str(intake), archive_dir=str(archive), simulate_live=True))
            pipeline._gmail_clients["tony_personal"] = xr_gmail_api.FakeGmailClient(ROOT, "tony_personal", True, scopes=xr_gmail_api.READONLY_SCOPE)
            pipeline.run()
            self.assertEqual(self._gmail_writes(pipeline), [])
            outcome = pipeline.state.index["items"]["BankTransactions:t1-adobe"]["gmail_archive"]
            self.assertEqual(outcome["status"], "failed")
            self.assertIn("--allow-archive", outcome["reason"])

    def test_trash_spam_and_already_archived_are_left_alone(self):
        with patch("xero_receipts.time.sleep", lambda _: None), TemporaryPaths() as (data, intake, archive):
            pipeline = Pipeline(args(data_dir=str(data), intake_dir=str(intake), archive_dir=str(archive), simulate_live=True))
            labels = {"gm-adobe": ["TRASH", "INBOX", "Label_1"], "gm-openai": ["Label_2"]}
            pipeline._gmail_clients["tony_personal"] = xr_gmail_api.FakeGmailClient(ROOT, "tony_personal", True, labels=labels)
            pipeline.run()
            self.assertEqual(self._gmail_writes(pipeline), [])
            items = pipeline.state.index["items"]
            self.assertEqual(items["BankTransactions:t1-adobe"]["gmail_archive"]["status"], "skipped")
            self.assertEqual(items["BankTransactions:t2-openai"]["gmail_archive"]["status"], "already_out_of_inbox")

    def test_real_gmail_client_archive_call_is_fixed_body_post(self):
        sent = []

        class Response:
            def read(self):
                return b'{"id": "m1", "labelIds": ["Label_1"]}'
            def __enter__(self):
                return self
            def __exit__(self, *_):
                return False

        client = xr_gmail_api.GmailClient("token", "tony_personal", xr_gmail_api.MODIFY_SCOPE)
        self.assertTrue(client.can_modify)
        self.assertFalse(xr_gmail_api.GmailClient("token", "x", xr_gmail_api.READONLY_SCOPE).can_modify)
        with patch("xr_gmail_api.urllib.request.urlopen", lambda request, timeout: sent.append((request.get_method(), request.full_url, request.data)) or Response()):
            client.remove_inbox_label("m1")
        self.assertEqual(sent, [("POST", "https://gmail.googleapis.com/gmail/v1/users/me/messages/m1/modify", b'{"removeLabelIds": ["INBOX"]}')])

    def test_config_rejects_bad_flags_and_unsupported_reconcile(self):
        with TemporaryPaths() as (data, intake, archive):
            config = json.loads((ROOT / "Fixture_Config.json").read_text())
            config.update(data_dir=str(data), intake_dir=str(intake), archive_dir=str(archive))
            path = data / "bad_config.json"
            for bad in ({"auto_archive_enabled": "yes"}, {"auto_reconcile_enabled": False}, {"max_auto_archive_per_run": -1},
                        {"eligible_bank_accounts": [{}]}, {"eligible_bank_accounts": "Chase Ink"}):
                path.write_text(json.dumps(dict(config, **bad)))
                with self.assertRaises(ValueError):
                    xr_config.load_config(path)
            missing = dict(config)
            missing.pop("eligible_bank_accounts")
            path.write_text(json.dumps(missing))
            with self.assertRaises(ValueError):  # no allowlist at all: refuse to run rather than attach anywhere
                xr_config.load_config(path)

    def test_filename_sanitizing(self):
        transaction = {"date": "2026-05-12", "archive_date_format": "%m-%d-%Y"}
        self.assertEqual(xr_state.safe_filename("bad:name?.pdf", "fallback.pdf"), "bad_name_.pdf")
        transaction["total"] = 57.99
        self.assertEqual(xr_state.archive_name(transaction, "Adobe", "pdf"), "05-12-2026_Adobe_57.99.pdf")

    def test_secret_redaction(self):
        access_value = "".join(chr(97 + index) for index in range(20))
        refresh_value = "".join(chr(122 - index) for index in range(20))
        text = json.dumps({"access_token": access_value, "refresh_token": refresh_value})
        self.assertNotIn(access_value, xr_secrets.redact(text))


if __name__ == "__main__":
    unittest.main()
