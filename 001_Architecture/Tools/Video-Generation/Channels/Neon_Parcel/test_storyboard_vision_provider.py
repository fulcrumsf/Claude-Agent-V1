import base64
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from storyboard_vision_provider import build_request, inspect_storyboard


FIXTURE = Path(__file__).with_name("shot_06_storyboard_spec.json")


def _provider_report(spec):
    check = {"status": "pass", "confidence": 0.95, "evidence": "Visible and coherent."}
    return {
        "overall_confidence": 0.95,
        "frame_checks": [
            {"frame": frame["frame"], **{name: check for name in ("subject_presence", "object_state", "spatial_relationship", "action_state", "caption")}}
            for frame in spec["frames"]
        ],
        "transition_checks": [
            {"from_frame": number, "to_frame": number + 1, **{name: check for name in ("causal_transition", "chronology", "camera_geometry", "physics")}}
            for number in range(1, len(spec["frames"]))
        ],
    }


class StoryboardVisionProviderTests(unittest.TestCase):
    def setUp(self):
        self.spec = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_request_contains_contract_prompt_and_data_uri(self):
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "candidate.png"
            image.write_bytes(b"png bytes")
            request = build_request(self.spec, image, model="test/model")
        self.assertEqual(request["model"], "test/model")
        content = request["messages"][0]["content"]
        self.assertIn("Return JSON only", content[0]["text"])
        self.assertTrue(content[1]["image_url"]["url"].startswith("data:image/png;base64,"))
        self.assertEqual(base64.b64decode(content[1]["image_url"]["url"].split(",", 1)[1]), b"png bytes")

    def test_live_call_returns_parsed_report_and_raw_response(self):
        response_body = {"choices": [{"message": {"content": json.dumps(_provider_report(self.spec))}}]}

        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return json.dumps(response_body).encode("utf-8")

        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "candidate.png"
            image.write_bytes(b"png bytes")
            with patch("storyboard_vision_provider.urllib.request.urlopen", return_value=Response()):
                report, raw = inspect_storyboard(self.spec, image, api_key="test-key")
        self.assertEqual(report["overall_confidence"], 0.95)
        self.assertEqual(raw, response_body)

    def test_invalid_provider_json_is_rejected(self):
        response_body = {"choices": [{"message": {"content": "not json"}}]}

        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return json.dumps(response_body).encode("utf-8")

        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "candidate.png"
            image.write_bytes(b"png bytes")
            with patch("storyboard_vision_provider.urllib.request.urlopen", return_value=Response()):
                with self.assertRaises(ValueError):
                    inspect_storyboard(self.spec, image, api_key="test-key")

    def test_openrouter_text_block_content_is_supported(self):
        response_body = {"choices": [{"message": {"content": [{"type": "text", "text": json.dumps(_provider_report(self.spec))}]}}]}

        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self): return json.dumps(response_body).encode("utf-8")

        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "candidate.png"
            image.write_bytes(b"png bytes")
            with patch("storyboard_vision_provider.urllib.request.urlopen", return_value=Response()):
                report, _ = inspect_storyboard(self.spec, image, api_key="test-key")
        self.assertEqual(report["overall_confidence"], 0.95)

    def test_missing_api_key_is_rejected_before_network(self):
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "candidate.png"
            image.write_bytes(b"png bytes")
            with self.assertRaises(RuntimeError):
                inspect_storyboard(self.spec, image, api_key="")


if __name__ == "__main__":
    unittest.main()
