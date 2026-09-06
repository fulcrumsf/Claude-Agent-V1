import json
import tempfile
import unittest
from pathlib import Path

from storyboard_ensemble import combine_reports, combine_with_policy, load_policy


def report(status):
    return {"status": status, "findings": []}


class StoryboardEnsembleTests(unittest.TestCase):
    def test_manual_review_policy_overrides_agreement(self):
        result = combine_reports(report("fail"), report("fail"), manual_review_required=True)
        self.assertEqual(result["status"], "manual_review")
        self.assertFalse(result["provider_disagreement"])

    def test_disagreement_requires_manual_review(self):
        result = combine_reports(report("pass"), report("fail"), manual_review_required=False)
        self.assertEqual(result["status"], "manual_review")
        self.assertTrue(result["provider_disagreement"])

    def test_agreement_can_pass_when_policy_is_off(self):
        result = combine_reports(report("pass"), report("pass"), manual_review_required=False)
        self.assertEqual(result["status"], "pass")

    def test_missing_policy_defaults_to_manual_review(self):
        self.assertTrue(load_policy()["manual_review_required"])

    def test_policy_file_can_turn_manual_review_off(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "policy.json"
            path.write_text(json.dumps({"manual_review_required": False}))
            policy = load_policy(path)
        result = combine_with_policy(report("pass"), report("pass"), policy)
        self.assertEqual(result["status"], "pass")
        self.assertFalse(result["policy"]["manual_review_required"])

    def test_policy_off_still_blocks_provider_disagreement(self):
        result = combine_with_policy(
            report("pass"), report("fail"), {"manual_review_required": False, "require_provider_agreement": True}
        )
        self.assertEqual(result["status"], "manual_review")


if __name__ == "__main__":
    unittest.main()
