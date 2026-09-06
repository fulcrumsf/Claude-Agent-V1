import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from gemini_video_inspection import DEFAULT_FPS, DEFAULT_MODEL, REPORT_SCHEMA, inspect_video


class GeminiVideoInspectionTests(unittest.TestCase):
    def test_defaults_are_dense_static_direct_gemini(self):
        self.assertEqual(DEFAULT_MODEL, "gemini-3.7-flash")
        self.assertEqual(DEFAULT_FPS, 3.0)
        self.assertEqual(REPORT_SCHEMA["required"], ["summary", "overall_confidence", "findings"])

    def test_missing_video_fails_before_api_call(self):
        with self.assertRaises(FileNotFoundError):
            inspect_video(Path("/tmp/does-not-exist.mp4"), api_key="test")

    @patch("gemini_video_inspection.genai.Client")
    def test_builds_video_part_with_requested_fps(self, client_class):
        video = Path("/tmp/gemini-inspection-test.mp4")
        video.write_bytes(b"test")
        try:
            client = client_class.return_value
            uploaded = Mock(uri="https://example.test/video", mime_type="video/mp4", name="files/test")
            uploaded.state.name = "ACTIVE"
            client.files.upload.return_value = uploaded
            client.models.generate_content.return_value.text = '{"summary":"ok","overall_confidence":0.9,"findings":[]}'
            result = inspect_video(video, api_key="test", fps=4)
            part = client.models.generate_content.call_args.kwargs["contents"][0].parts[0]
            self.assertEqual(part.video_metadata.fps, 4)
            self.assertEqual(result["processing_mode"], "static")
        finally:
            video.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
