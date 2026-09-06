import unittest

from decide_end_frame import decide


class EndFrameDecisionTests(unittest.TestCase):
    def test_clear_endpoint_uses_end_frame(self):
        result = decide({"route": "seedance_1_5_start_end", "endpoint_assessment": {field: True for field in ("materially_different_state", "stable_camera_geometry", "consistent_subject_count", "clear_endpoint")}})
        self.assertEqual(result["decision"], "use_end_frame")

    def test_confusing_endpoint_uses_start_only(self):
        result = decide({"route": "seedance_1_5_start_end", "endpoint_assessment": {"materially_different_state": False, "stable_camera_geometry": True, "consistent_subject_count": False, "clear_endpoint": False}})
        self.assertEqual(result["decision"], "start_frame_only")

    def test_missing_assessment_requires_review(self):
        self.assertEqual(decide({"route": "seedance_1_5_start_end"})["decision"], "manual_review")

    def test_other_route_is_not_applicable(self):
        self.assertEqual(decide({"route": "seedance_2_mini_storyboard"})["decision"], "not_applicable")


if __name__ == "__main__":
    unittest.main()
