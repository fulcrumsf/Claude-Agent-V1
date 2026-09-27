"""Tests for the Seedance model routing in pipeline_supervisor.py (2026-09-27).

Bug fixed: a beat switched to Seedance 2.0 used to be sent silently as Seedance 1.5 Pro.
The supervisor does module-level path setup from sys.argv[1], so point it at a temp dir first."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_TMP = tempfile.mkdtemp()
(Path(_TMP) / "Production").mkdir(parents=True, exist_ok=True)
sys.argv = ["pipeline_supervisor.py", _TMP]

import pipeline_supervisor as ps  # noqa: E402

BASE = {"video_prompt": "A mantis shrimp strikes a snail shell.", "target_duration_s": 6.3,
        "first_frame_url": "https://x/first.png", "last_frame_url": "https://x/last.png"}
REF_PROMPT = """@Image 1 = creature sheet titled "MANTIS SHRIMP".
@Image 2 = environment sheet, the reef.
The scene takes place at @Image 2.
[00:00-00:04] @Image 1 strikes the shell.
"""


class SeedancePayloadTests(unittest.TestCase):
    def test_default_is_still_15_pro_with_input_urls(self):
        p = ps.seedance_payload(dict(BASE))
        self.assertEqual(p["model"], "bytedance/seedance-1.5-pro")
        self.assertEqual(p["input"]["input_urls"], ["https://x/first.png", "https://x/last.png"])
        self.assertEqual(p["input"]["duration"], "8")

    def test_seedance_2_override_is_really_sent_as_2(self):
        p = ps.seedance_payload({**BASE, "model": "bytedance/seedance-2"})
        self.assertEqual(p["model"], "bytedance/seedance-2")
        self.assertEqual(p["input"]["first_frame_url"], "https://x/first.png")
        self.assertEqual(p["input"]["last_frame_url"], "https://x/last.png")
        self.assertNotIn("input_urls", p["input"])
        self.assertEqual(p["input"]["duration"], 8)

    def test_seedance_2_reference_mode_with_tagged_prompt(self):
        e = {"video_prompt": REF_PROMPT, "target_duration_s": 4, "model": "bytedance/seedance-2-fast",
             "reference_image_urls": ["https://x/shrimp_sheet.png", "https://x/reef_env.png"]}
        p = ps.seedance_payload(e)
        self.assertEqual(p["input"]["reference_image_urls"], e["reference_image_urls"])
        self.assertNotIn("first_frame_url", p["input"])

    def test_mixing_frames_and_references_is_refused(self):
        with self.assertRaises(ValueError):
            ps.seedance_payload({**BASE, "model": "bytedance/seedance-2", "reference_image_urls": ["https://x/a.png"]})

    def test_reference_prompt_without_tags_is_refused(self):
        with self.assertRaises(ValueError):
            ps.seedance_payload({"video_prompt": "A shrimp strikes.", "target_duration_s": 4,
                                 "model": "bytedance/seedance-2", "reference_image_urls": ["https://x/a.png"]})

    def test_unknown_seedance_model_is_refused_not_downgraded(self):
        with self.assertRaises(ValueError):
            ps.seedance_payload({**BASE, "model": "bytedance/seedance-2.0"})

    def test_config_error_makes_no_api_call(self):
        with mock.patch.object(ps.requests, "post") as post:
            r = ps.generate_seedance({**BASE, "model": "bytedance/seedance-9"})
        post.assert_not_called()
        self.assertEqual(r["error_category"], "CONFIG")

    def test_seedance_2_submits_the_2_payload(self):
        resp = mock.Mock(status_code=200); resp.json.return_value = {"code": 200, "data": {"taskId": "t1"}}
        with mock.patch.object(ps.requests, "post", return_value=resp) as post, \
             mock.patch.object(ps, "kie_poll", return_value={"ok": True, "data": {}}), \
             mock.patch.object(ps, "extract_video_url", return_value="https://x/out.mp4"):
            r = ps.generate_seedance({**BASE, "model": "bytedance/seedance-2"})
        self.assertTrue(r["ok"])
        self.assertEqual(post.call_args.kwargs["json"]["model"], "bytedance/seedance-2")


if __name__ == "__main__":
    unittest.main()
