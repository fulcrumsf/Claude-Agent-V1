import json
import tempfile
import unittest
from pathlib import Path

from storyboard_contract import validate_spec
from storyboard_qa import build_inspection_prompt, evaluate_report, normalize_vision_report, render_report


FIXTURE = Path(__file__).with_name("shot_06_storyboard_spec.json")


def _check(status="pass", evidence="The image visibly matches the contract.", confidence=0.95):
    return {"status": status, "confidence": confidence, "evidence": evidence}


def complete_passing_report(spec):
    return {
        "overall_confidence": 0.95,
        "frame_checks": [
            {
                "frame": frame["frame"],
                **{name: _check() for name in ("subject_presence", "object_state", "spatial_relationship", "action_state", "caption")},
            }
            for frame in spec["frames"]
        ],
        "transition_checks": [
            {
                "from_frame": number,
                "to_frame": number + 1,
                **{name: _check() for name in ("causal_transition", "chronology", "camera_geometry", "physics")},
            }
            for number in range(1, len(spec["frames"]))
        ],
    }


class StoryboardQATests(unittest.TestCase):
    def setUp(self):
        self.spec = json.loads(FIXTURE.read_text(encoding="utf-8"))
        validate_spec(self.spec)

    def test_inspection_prompt_contains_every_frame_and_fail_closed_rule(self):
        prompt = build_inspection_prompt(self.spec)
        self.assertIn("Return JSON only", prompt)
        self.assertIn('"frame": 1', prompt)
        self.assertIn('"caption": "Opening shot.', prompt)
        self.assertIn("do not mark ambiguity as pass", prompt)

    def test_complete_passing_report_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "storyboard.png"
            candidate.write_bytes(b"mock storyboard")
            result = evaluate_report(self.spec, complete_passing_report(self.spec), candidate)
            self.assertEqual(result["status"], "pass")
            self.assertEqual(result["findings"], [])
            self.assertEqual(len(result["checked_frames"]), 6)
            self.assertEqual(len(result["checked_transitions"]), 5)

    def test_shot_six_wrong_gate_and_missing_bear_are_frame_specific_failures(self):
        report = complete_passing_report(self.spec)
        report["frame_checks"][0]["subject_presence"] = _check(
            "fail", "The bear is not visible in panel 1."
        )
        report["frame_checks"][0]["object_state"] = _check(
            "fail", "The gate is visibly open in panel 1."
        )
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "shot-06.png"
            candidate.write_bytes(b"mock storyboard")
            result = evaluate_report(self.spec, report, candidate)
        self.assertEqual(result["status"], "fail")
        self.assertEqual(
            {(item["frame"], item["category"]) for item in result["findings"]},
            {("1", "subject_presence"), ("1", "object_state")},
        )

    def test_transition_physics_failure_is_not_ignored(self):
        report = complete_passing_report(self.spec)
        report["transition_checks"][1]["physics"] = _check(
            "fail", "The bear changes sides without a visible movement path."
        )
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "storyboard.png"
            candidate.write_bytes(b"mock storyboard")
            result = evaluate_report(self.spec, report, candidate)
        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["findings"][0]["frame"], "2->3")
        self.assertEqual(result["findings"][0]["category"], "physics")

    def test_ambiguous_or_missing_evidence_fails_closed(self):
        report = complete_passing_report(self.spec)
        report["frame_checks"][2]["caption"] = _check(
            "ambiguous", "Caption band is too blurred to read.", confidence=0.3
        )
        del report["transition_checks"][0]["camera_geometry"]
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "storyboard.png"
            candidate.write_bytes(b"mock storyboard")
            result = evaluate_report(self.spec, report, candidate)
        self.assertEqual(result["status"], "manual_review")
        self.assertTrue(any(item["category"] == "caption" for item in result["findings"]))
        self.assertTrue(any(item["category"] == "camera_geometry" for item in result["findings"]))

    def test_low_confidence_pass_is_downgraded_to_manual_review(self):
        report = complete_passing_report(self.spec)
        report["frame_checks"][0]["caption"] = _check(
            "pass", "Caption appears to match, but it is barely legible.", confidence=0.4
        )
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "storyboard.png"
            candidate.write_bytes(b"mock storyboard")
            result = evaluate_report(self.spec, report, candidate)
        self.assertEqual(result["status"], "manual_review")
        self.assertEqual(result["findings"][0]["status"], "ambiguous")

    def test_missing_candidate_is_manual_review(self):
        with tempfile.TemporaryDirectory() as directory:
            result = evaluate_report(
                self.spec,
                complete_passing_report(self.spec),
                Path(directory) / "missing.png",
            )
        self.assertEqual(result["status"], "manual_review")
        self.assertEqual(result["findings"][0]["category"], "candidate_image")

    def test_malformed_report_is_manual_review(self):
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "storyboard.png"
            candidate.write_bytes(b"mock storyboard")
            result = evaluate_report(self.spec, {"frame_checks": []}, candidate)
        self.assertEqual(result["status"], "manual_review")
        self.assertEqual(result["findings"][0]["category"], "report_schema")

    def test_provider_aliases_are_normalized_without_relaxing_checks(self):
        report = complete_passing_report(self.spec)
        aliased = {
            "overall_confidence": report["overall_confidence"],
            "frame_analysis": report["frame_checks"],
            "transition_analysis": [
                {"frames": f"{item['from_frame']}-{item['to_frame']}", **{k: v for k, v in item.items() if k not in {"from_frame", "to_frame"}}}
                for item in report["transition_checks"]
            ],
        }
        normalized = normalize_vision_report(aliased)
        self.assertEqual(normalized["frame_checks"], report["frame_checks"])
        self.assertEqual(normalized["transition_checks"][0]["from_frame"], 1)
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "storyboard.png"
            candidate.write_bytes(b"mock storyboard")
            result = evaluate_report(self.spec, aliased, candidate)
        self.assertEqual(result["status"], "pass")

    def test_report_renderer_exposes_status_and_actionable_finding(self):
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "storyboard.png"
            candidate.write_bytes(b"mock storyboard")
            report = complete_passing_report(self.spec)
            report["frame_checks"][0]["object_state"] = _check(
                "fail", "The gate is open too early."
            )
            result = evaluate_report(self.spec, report, candidate)
        rendered = render_report(result)
        self.assertIn("Storyboard QA: FAIL", rendered)
        self.assertIn("1 / object_state", rendered)
        self.assertIn("gate is open too early", rendered)


if __name__ == "__main__":
    unittest.main()
