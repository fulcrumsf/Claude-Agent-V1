import unittest

from route_shot_complexity import route_document, route_shot


class ShotComplexityTests(unittest.TestCase):
    def test_simple_shot_uses_seedance_15(self):
        result = route_shot(
            {
                "shot_id": "shot-1",
                "description": "A bear looks through the window.",
                "semantic_assessment": {dimension: 0 for dimension in ("physics", "object_continuity", "precision")},
            }
        )
        self.assertEqual(result["route"], "seedance_1_5_start_end")
        self.assertEqual(result["status"], "auto")

    def test_physics_hard_gate_uses_mini_storyboard(self):
        result = route_shot(
            {
                "shot_id": "shot-2",
                "description": "Grandma pulls the seat belt from the shoulder anchor and buckles the bear into the car.",
                "semantic_assessment": {"physics": 2, "object_continuity": 2, "precision": 2, "action_count": 2},
            }
        )
        self.assertEqual(result["route"], "seedance_2_mini_storyboard")
        self.assertTrue(result["hard_triggered"])

    def test_borderline_shot_stops_for_review(self):
        result = route_shot(
            {
                "shot_id": "shot-3",
                "description": "A dog moves through a gate.",
                "semantic_assessment": {
                    "action_count": 1,
                    "physics": 1,
                    "object_continuity": 1,
                    "precision": 1,
                    "spatial_continuity": 1,
                    "storyboard_value": 1,
                },
            }
        )
        self.assertEqual(result["route"], "manual_review")
        self.assertEqual(result["status"], "review_required")

    def test_human_override_is_preserved(self):
        result = route_shot(
            {"shot_id": "shot-4", "description": "A bear buckles a seat belt.", "route_override": "force_simple"}
        )
        self.assertEqual(result["route"], "seedance_1_5_start_end")
        self.assertEqual(result["status"], "overridden")

    def test_document_preserves_input_and_adds_routing(self):
        result = route_document(
            {
                "shots": [
                    {
                        "shot_id": "shot-1",
                        "description": "A cat blinks.",
                        "semantic_assessment": {"action_count": 0},
                    }
                ]
            }
        )
        self.assertIn("shots", result)
        self.assertIn("routing", result)
        self.assertEqual(result["routing"][0]["shot_id"], "shot-1")


if __name__ == "__main__":
    unittest.main()
