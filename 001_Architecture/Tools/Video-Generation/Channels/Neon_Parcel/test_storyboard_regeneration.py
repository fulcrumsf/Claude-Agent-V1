import json
import tempfile
import unittest
from pathlib import Path

from storyboard_regeneration import StoryboardAttemptController, run_storyboard_loop


FIXTURE = Path(__file__).with_name("shot_06_storyboard_spec.json")


class StoryboardRegenerationTests(unittest.TestCase):
    def setUp(self):
        self.spec = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def _controller(self, root):
        return StoryboardAttemptController(
            root / "attempts.json",
            "Shot-06",
            archive_dir=root / "archived",
            active_dir=root / "active",
        )

    def _run(self, results):
        root = Path(tempfile.mkdtemp())
        controller = self._controller(root)
        spec_path = root / "spec.json"
        spec_path.write_text(json.dumps(self.spec), encoding="utf-8")
        generated = []
        evaluated = []

        def prompt_path_factory(attempt):
            path = root / f"prompt-{attempt}.txt"
            path.write_text(f"prompt {attempt}", encoding="utf-8")
            return path

        def generate(spec, attempt, retry_findings):
            generated.append((attempt, retry_findings))
            path = root / f"candidate-{attempt}.png"
            path.write_bytes(f"candidate {attempt}".encode())
            return path

        def evaluate(spec, image):
            evaluated.append(image.name)
            return results[len(evaluated) - 1]

        outcome = run_storyboard_loop(
            self.spec,
            controller,
            generate,
            evaluate,
            prompt_path_factory=prompt_path_factory,
            spec_path=spec_path,
        )
        return root, controller, generated, evaluated, outcome

    @staticmethod
    def qa(status, evidence="test evidence"):
        return {"status": status, "findings": [{"frame": "1", "category": "object_state", "evidence": evidence}]}

    def test_fail_fail_pass_stops_at_third_and_selects_only_passing_candidate(self):
        root, controller, generated, evaluated, outcome = self._run([self.qa("fail"), self.qa("fail"), self.qa("pass")])
        self.assertEqual(outcome["status"], "pass")
        self.assertEqual([item[0] for item in generated], [1, 2, 3])
        self.assertEqual(evaluated, ["candidate-1.png", "candidate-2.png", "candidate-3.png"])
        self.assertEqual(len(list((root / "archived").glob("*"))), 2)
        self.assertEqual(len(list((root / "active").glob("*"))), 1)
        self.assertEqual(controller.selected_attempt(), 3)

    def test_fail_fail_fail_blocks_and_never_selects(self):
        root, controller, generated, evaluated, outcome = self._run([self.qa("fail"), self.qa("fail"), self.qa("fail")])
        self.assertEqual(outcome["status"], "blocked")
        self.assertEqual(len(generated), 3)
        self.assertEqual(len(evaluated), 3)
        self.assertIsNone(controller.selected_attempt())
        self.assertTrue(controller.blocked())
        self.assertEqual(len(list((root / "archived").glob("*"))), 3)
        self.assertFalse((root / "candidate-3.png").exists())

    def test_first_pass_skips_unnecessary_retries(self):
        root, controller, generated, evaluated, outcome = self._run([self.qa("pass")])
        self.assertEqual(outcome["status"], "pass")
        self.assertEqual(len(generated), 1)
        self.assertEqual(len(evaluated), 1)

    def test_retry_receives_only_prior_findings(self):
        root, controller, generated, evaluated, outcome = self._run([self.qa("fail", "gate open too early"), self.qa("pass")])
        self.assertEqual(generated[1][1][0]["evidence"], "gate open too early")

    def test_provider_failure_is_distinct_and_retries(self):
        root = Path(tempfile.mkdtemp())
        controller = self._controller(root)
        spec_path = root / "spec.json"
        spec_path.write_text(json.dumps(self.spec), encoding="utf-8")
        calls = []

        def prompt(attempt):
            path = root / f"prompt-{attempt}.txt"
            path.write_text("prompt", encoding="utf-8")
            return path

        def generate(spec, attempt, findings):
            calls.append(attempt)
            if attempt == 1:
                raise RuntimeError("provider timeout")
            path = root / f"candidate-{attempt}.png"
            path.write_bytes(b"candidate")
            return path

        outcome = run_storyboard_loop(
            self.spec,
            controller,
            generate,
            lambda spec, image: self.qa("pass"),
            prompt_path_factory=prompt,
            spec_path=spec_path,
        )
        self.assertEqual(outcome["status"], "pass")
        self.assertEqual(calls, [1, 2])
        self.assertEqual(controller.attempts()[1]["status"], "provider_failed")

    def test_fourth_attempt_is_refused_before_provider_call(self):
        root = Path(tempfile.mkdtemp())
        controller = self._controller(root)
        prompt = root / "prompt.txt"
        spec = root / "spec.json"
        prompt.write_text("prompt", encoding="utf-8")
        spec.write_text("{}", encoding="utf-8")
        for attempt in range(1, 4):
            number = controller.reserve_attempt(prompt, spec, retry_reason="retry" if attempt > 1 else None)
            image = root / f"candidate-{attempt}.png"
            image.write_bytes(b"candidate")
            controller.record_generated(number, image)
            controller.record_qa(number, self.qa("fail"))
        with self.assertRaisesRegex(ValueError, "attempt cap reached"):
            controller.reserve_attempt(prompt, spec, retry_reason="retry")

    def test_next_attempt_requires_completed_prior_qa(self):
        root = Path(tempfile.mkdtemp())
        controller = self._controller(root)
        prompt = root / "prompt.txt"
        spec = root / "spec.json"
        image = root / "candidate.png"
        prompt.write_text("prompt", encoding="utf-8")
        spec.write_text("{}", encoding="utf-8")
        number = controller.reserve_attempt(prompt, spec)
        controller.record_generated(number, image) if image.exists() else None
        with self.assertRaisesRegex(ValueError, "previous storyboard candidate"):
            controller.reserve_attempt(prompt, spec, retry_reason="retry")


if __name__ == "__main__":
    unittest.main()
