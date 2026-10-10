import argparse
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import xr_match
import xr_secrets
import xr_state
from xero_receipts import Pipeline


ROOT = Path(__file__).resolve().parent
PYTHON = sys.executable


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
