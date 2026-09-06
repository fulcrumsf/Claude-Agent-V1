import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from storyboard_handoff import build_seedance_prompt, validate_handoff


FIXTURE = Path(__file__).with_name("shot_06_storyboard_spec.json")


class StoryboardHandoffTests(unittest.TestCase):
    def setUp(self):
        self.spec = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def _files(self, root):
        storyboard = root / "selected-storyboard.png"
        contract = root / "contract.json"
        qa = root / "qa.json"
        state = root / "attempts.json"
        storyboard.write_bytes(b"selected storyboard")
        contract.write_text(json.dumps(self.spec), encoding="utf-8")
        qa.write_text(json.dumps({"status": "pass", "findings": []}), encoding="utf-8")
        state.write_text(json.dumps({"events": [{"event": "selected", "attempt": 2}]}), encoding="utf-8")
        return storyboard, contract, qa, state

    def _manifest(self, storyboard, contract, qa, state, **overrides):
        result = {
            "shot_id": "Shot-06",
            "status": "pass",
            "selected_attempt": 2,
            "active_storyboard_path": str(storyboard),
            "contract_path": str(contract),
            "qa_report_path": str(qa),
            "attempt_state_path": str(state),
            "storyboard_reference_url": "https://cdn.example/shot-06-storyboard.png",
            "reference_role": "storyboard_reference",
            "manual_review_approved": True,
            "storyboard_sha256": hashlib.sha256(storyboard.read_bytes()).hexdigest(),
            "contract_sha256": hashlib.sha256(contract.read_bytes()).hexdigest(),
            "qa_report_sha256": hashlib.sha256(qa.read_bytes()).hexdigest(),
        }
        result.update(overrides)
        return result

    def test_passing_handoff_builds_existing_five_sections_in_order(self):
        with tempfile.TemporaryDirectory() as directory:
            storyboard, contract, qa, state = self._files(Path(directory))
            manifest = self._manifest(storyboard, contract, qa, state)
            prompt = build_seedance_prompt(self.spec, {"status": "pass"}, manifest)
        positions = [prompt.index(section) for section in ("TONE:", "CAPTURE STYLE:", "CAMERA LOCK:", "SCENE CONTINUITY:", "ACTION TIMELINE:", "AUDIO:", "VISUAL REALISM:", "HARD CONSTRAINTS:")]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("Shots: 1 | Duration:", prompt)
        self.assertIn("@Image 1 = the first uploaded image", prompt)
        self.assertIn("Follow this storyboard @Image 1", prompt)
        self.assertIn("Shot 1, panel 3:", prompt)
        self.assertIn("The left-side gate is now partly open", prompt)
        self.assertIn("Unplanned real-life neighbor footage", prompt)
        self.assertIn("music", prompt)
        self.assertIn("do not reproduce its panels", prompt)

    def test_failed_or_unselected_handoff_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            storyboard, contract, qa, state = self._files(Path(directory))
            for overrides in ({"status": "manual_review"}, {"selected_attempt": None}):
                with self.assertRaises(ValueError):
                    validate_handoff(self._manifest(storyboard, contract, qa, state, **overrides))

    def test_storyboard_and_first_frame_roles_must_be_separate(self):
        with tempfile.TemporaryDirectory() as directory:
            storyboard, contract, qa, state = self._files(Path(directory))
            with self.assertRaisesRegex(ValueError, "cannot also be"):
                validate_handoff(
                    self._manifest(
                        storyboard,
                        contract,
                        qa,
                        state,
                        first_frame_url="https://cdn.example/shot-06-storyboard.png",
                    )
                )

    def test_hash_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            storyboard, contract, qa, state = self._files(Path(directory))
            with self.assertRaisesRegex(ValueError, "storyboard_sha256"):
                validate_handoff(self._manifest(storyboard, contract, qa, state, storyboard_sha256="wrong"))

    def test_nonpassing_qa_report_cannot_build_prompt(self):
        with tempfile.TemporaryDirectory() as directory:
            storyboard, contract, qa, state = self._files(Path(directory))
            with self.assertRaisesRegex(ValueError, "QA report"):
                build_seedance_prompt(self.spec, {"status": "fail"}, self._manifest(storyboard, contract, qa, state))

    def test_manual_review_policy_blocks_unapproved_handoff(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            storyboard, contract, qa, state = self._files(root)
            policy = root / "policy.json"
            policy.write_text(json.dumps({"manual_review_required": True}))
            with self.assertRaisesRegex(ValueError, "manual storyboard review approval"):
                validate_handoff(self._manifest(storyboard, contract, qa, state, review_policy_path=str(policy), manual_review_approved=False))

    def test_policy_file_can_disable_manual_approval_requirement(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            storyboard, contract, qa, state = self._files(root)
            policy = root / "policy.json"
            policy.write_text(json.dumps({"manual_review_required": False}))
            manifest = self._manifest(storyboard, contract, qa, state, review_policy_path=str(policy), manual_review_approved=False)
            self.assertEqual(validate_handoff(manifest)["status"], "pass")


if __name__ == "__main__":
    unittest.main()
