import unittest
import tempfile
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from kie_market_api import _validate_seedance_input, build_seedance_mini_input, download


class SeedanceReferenceRoutingTests(unittest.TestCase):
    def test_storyboard_is_context_reference(self):
        payload = build_seedance_mini_input(
            "animate the scene",
            reference_image_urls=["https://cdn.example/Shot-08-Storyboard-v1.png"],
        )
        self.assertEqual(payload["reference_image_urls"], ["https://cdn.example/Shot-08-Storyboard-v1.png"])
        self.assertNotIn("first_frame_url", payload)

    def test_clean_start_frame_is_temporal_input(self):
        payload = build_seedance_mini_input(
            "animate the scene",
            first_frame_url="https://cdn.example/Shot-08-Start-Frame-v2.png",
        )
        self.assertEqual(payload["first_frame_url"], "https://cdn.example/Shot-08-Start-Frame-v2.png")
        self.assertNotIn("reference_image_urls", payload)

    def test_first_and_last_frames_are_temporal_pair(self):
        payload = build_seedance_mini_input(
            "animate the scene",
            first_frame_url="https://cdn.example/Shot-08-First-Frame-v3.png",
            last_frame_url="https://cdn.example/Shot-08-End-Frame-v3.png",
        )
        self.assertEqual(payload["first_frame_url"].split("/")[-1], "Shot-08-First-Frame-v3.png")
        self.assertEqual(payload["last_frame_url"].split("/")[-1], "Shot-08-End-Frame-v3.png")
        self.assertNotIn("reference_image_urls", payload)

    def test_storyboard_cannot_be_passed_as_start_frame(self):
        with self.assertRaisesRegex(ValueError, "storyboard"):
            build_seedance_mini_input(
                "animate the scene",
                first_frame_url="https://cdn.example/Shot-08-Storyboard-v1.png",
            )

    def test_frame_and_reference_are_not_combined(self):
        with self.assertRaises(ValueError):
            build_seedance_mini_input(
                "animate the scene",
                first_frame_url="https://cdn.example/Shot-08-Start-Frame-v2.png",
                reference_image_urls=["https://cdn.example/character.png"],
            )

    def test_low_level_task_guard_catches_misrouting(self):
        with self.assertRaisesRegex(ValueError, "storyboard"):
            _validate_seedance_input(
                "bytedance/seedance-2-mini",
                {"first_frame_url": "https://cdn.example/storyboard-v1.png"},
            )

    def test_provider_download_requires_versioned_new_path(self):
        with self.assertRaisesRegex(ValueError, "explicit version"):
            download("https://cdn.example/video.mp4", Path(tempfile.gettempdir()) / "video.mp4")


if __name__ == "__main__":
    unittest.main()
