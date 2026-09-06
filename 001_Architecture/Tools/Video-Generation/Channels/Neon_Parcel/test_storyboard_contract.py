import json
import unittest
from pathlib import Path

from storyboard_contract import render_prompt, validate_spec


FIXTURE = Path(__file__).with_name("shot_06_storyboard_spec.json")


class StoryboardContractTests(unittest.TestCase):
    def setUp(self):
        self.spec = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_shot_six_fixture_validates_continuity_requirements(self):
        result = validate_spec(self.spec)
        self.assertEqual(result["frames"][0]["frame"], 1)
        frame_one_subjects = " ".join(result["frames"][0]["visible_subjects"]).lower()
        self.assertIn("bear", frame_one_subjects)
        self.assertIn("closed", result["frames"][0]["object_states"][0].lower())
        self.assertIn("open", result["frames"][2]["object_states"][0].lower())
        self.assertEqual(
            result["frames"][0]["caption"],
            "Opening shot. Closed driveway gate. Bear already behind it.",
        )

    def test_render_order_and_exact_captions_are_stable(self):
        prompt = render_prompt(self.spec)
        self.assertLess(prompt.index("OVERALL SUMMARY:"), prompt.index("CAMERA LOCK:"))
        self.assertLess(prompt.index("TONE:"), prompt.index("FRAME-BY-FRAME STORYBOARD SEQUENCE:"))
        self.assertIn("Unplanned real-life neighbor footage", prompt)
        self.assertIn("Audio exclusions:", prompt)
        self.assertLess(prompt.index("CAMERA LOCK:"), prompt.index("FRAME-BY-FRAME STORYBOARD SEQUENCE:"))
        self.assertLess(prompt.index("FRAME 1:"), prompt.index("FRAME 2:"))
        self.assertLess(prompt.index("FRAME 2:"), prompt.index("FRAME 3:"))
        self.assertIn("Caption (render this exact text in the caption band): Opening shot.", prompt)

    def test_missing_frame_field_fails_before_generation(self):
        broken = json.loads(json.dumps(self.spec))
        del broken["frames"][1]["object_states"]
        with self.assertRaisesRegex(ValueError, "frame 2 missing required fields"):
            validate_spec(broken)

    def test_nonconsecutive_frames_fail(self):
        broken = json.loads(json.dumps(self.spec))
        broken["frames"][2]["frame"] = 4
        with self.assertRaisesRegex(ValueError, "consecutively numbered"):
            validate_spec(broken)

    def test_frame_one_cannot_start_with_unexplained_transition(self):
        broken = json.loads(json.dumps(self.spec))
        broken["frames"][0]["transition_from_previous"] = "The bear appears."
        with self.assertRaisesRegex(ValueError, "frame 1 cannot"):
            validate_spec(broken)


if __name__ == "__main__":
    unittest.main()
