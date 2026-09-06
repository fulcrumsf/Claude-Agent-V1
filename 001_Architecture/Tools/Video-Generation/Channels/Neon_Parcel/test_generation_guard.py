import json
import tempfile
import unittest
from pathlib import Path

from generation_guard import check_allowed, reserve


class GenerationGuardTests(unittest.TestCase):
    def test_missing_prompt_blocks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            log = root / "Generation_Log.json"
            log.write_text(json.dumps({"assets": []}), encoding="utf-8")
            with self.assertRaises(ValueError):
                check_allowed(log, "shot-1", "v1", root / "missing.json")

    def test_successful_existing_task_blocks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            log = root / "Generation_Log.json"
            prompt = root / "prompt.json"
            prompt.write_text("{}", encoding="utf-8")
            log.write_text(json.dumps({"assets": [{"shot_id": "shot-1", "version": "v1", "status": "success", "task_id": "task-1"}]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                check_allowed(log, "shot-1", "v1", prompt)

    def test_reserve_records_prompt_hash_and_blocks_second_attempt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            log = root / "Generation_Log.json"
            prompt = root / "prompt.json"
            prompt.write_text('{"prompt":"x"}', encoding="utf-8")
            log.write_text(json.dumps({"assets": []}), encoding="utf-8")
            record = reserve(log, "shot-1", "v1", prompt, "seedance")
            self.assertEqual(record["status"], "reserved")
            self.assertTrue(record["prompt_sha256"])
            with self.assertRaises(ValueError):
                check_allowed(log, "shot-1", "v1", prompt)

    def test_failed_attempt_can_be_retried_with_reason(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            log = root / "Generation_Log.json"
            prompt = root / "prompt.json"
            prompt.write_text("{}", encoding="utf-8")
            log.write_text(json.dumps({"assets": [{"shot_id": "shot-1", "version": "v1", "status": "failed"}]}), encoding="utf-8")
            self.assertEqual(check_allowed(log, "shot-1", "v1", prompt, "provider_failed")["prior_attempts"], 1)

    def test_unversioned_paid_attempt_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            log = root / "Generation_Log.json"
            prompt = root / "prompt.json"
            prompt.write_text("{}", encoding="utf-8")
            log.write_text(json.dumps({"assets": []}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "version must be explicit"):
                check_allowed(log, "shot-1", "latest", prompt)


if __name__ == "__main__":
    unittest.main()
