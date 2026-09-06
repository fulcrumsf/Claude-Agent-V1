"""Tests for clip_durations.py — the padding + trim + short-footage guard that
prevents the 0003_Glass_Frog_Transparency loop-flash bug from recurring."""

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import clip_durations as cd


class RequestDurationTests(unittest.TestCase):
    def test_typical_beat_gets_ceil_plus_one(self):
        # 6.3s target -> ceil(6.3)=7 -> +1 -> 8, well within seedance's 12 cap
        self.assertEqual(cd.request_duration(6.3, "bytedance/seedance-1.5-pro"), 8)

    def test_integer_target_still_padded(self):
        # 6.0s target -> ceil=6 -> +1 -> 7  (a bare ceil() would have given 6,
        # which is exactly what left no trim headroom on the glass frog clips)
        self.assertEqual(cd.request_duration(6.0, "seedance-1.5-pro"), 7)

    def test_sub_floor_beat_clamped_up_to_four(self):
        # 3.855s hook beat -> ceil=4 -> +1 -> 5, still >= floor, fine
        self.assertEqual(cd.request_duration(3.855, "seedance-1.5-pro"), 5)
        # a genuinely tiny beat still never goes below the model floor
        self.assertEqual(cd.request_duration(1.2, "seedance-1.5-pro"), 4)

    def test_clamped_to_model_max(self):
        self.assertEqual(cd.request_duration(11.8, "seedance-1.5-pro"), 12)   # cap 12
        self.assertEqual(cd.request_duration(11.8, "bytedance/seedance-2.0"), 13)  # cap 15
        self.assertEqual(cd.request_duration(20.0, "kling-3.0/video"), 10)   # cap 10
        self.assertEqual(cd.request_duration(20.0, "veo3_fast"), 8)          # cap 8

    def test_unknown_model_uses_conservative_default_cap(self):
        self.assertEqual(cd.model_max_s("something-new"), 12)
        self.assertEqual(cd.model_max_s(None), 12)

    def test_result_is_always_int(self):
        for t in (3.1, 4.0, 5.5, 6.9, 8.0):
            self.assertIsInstance(cd.request_duration(t, "seedance-1.5-pro"), int)

    def test_non_positive_target_rejected(self):
        with self.assertRaises(ValueError):
            cd.request_duration(0, "seedance-1.5-pro")


class TrimGuardTests(unittest.TestCase):
    def test_short_footage_kept_and_flagged_needs_fill_never_failed(self):
        # Tony 2026-08-30: never regenerate, never loop. A short clip is kept at
        # its real length with needs_fill set so assembly freeze-fills the gap.
        with mock.patch.object(cd, "probe_duration", return_value=5.9), \
             mock.patch("clip_durations.subprocess.run") as run:
            run.return_value = subprocess.CompletedProcess([], 0)
            with tempfile.TemporaryDirectory() as d:
                res = cd.trim_to_target("src.mp4", Path(d) / "out.mp4", target_s=6.3)
        self.assertTrue(res["ok"])
        self.assertTrue(res["needs_fill"])
        self.assertAlmostEqual(res["shortfall_s"], 0.4, places=3)
        self.assertAlmostEqual(res["final_s"], 5.9, places=3)  # kept at real length
        # ffmpeg was asked to keep the real length, not the (longer) target
        keep_arg = run.call_args[0][0]
        self.assertIn("5.900", keep_arg)

    def test_tiny_shortfall_within_eps_is_not_flagged(self):
        with mock.patch.object(cd, "probe_duration", return_value=6.28), \
             mock.patch("clip_durations.subprocess.run") as run:
            run.return_value = subprocess.CompletedProcess([], 0)
            with tempfile.TemporaryDirectory() as d:
                res = cd.trim_to_target("src.mp4", Path(d) / "o.mp4", target_s=6.30)
            self.assertTrue(res["ok"])
            self.assertFalse(res["needs_fill"])
            self.assertEqual(res["trim_offset_s"], 0.0)


class TrimRealFfmpegTest(unittest.TestCase):
    """One real round-trip through ffmpeg/ffprobe so the encode args are exercised."""

    def setUp(self):
        if subprocess.run(["which", "ffmpeg"], capture_output=True).returncode != 0:
            self.skipTest("ffmpeg not available")

    def test_head_trims_to_target(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "src.mp4"
            dst = Path(d) / "dst.mp4"
            subprocess.run(
                ["ffmpeg", "-y", "-f", "lavfi", "-i", "testsrc=size=320x240:rate=30",
                 "-t", "3", "-pix_fmt", "yuv420p", str(src), "-loglevel", "error"],
                check=True,
            )
            res = cd.trim_to_target(src, dst, target_s=1.5)
            self.assertTrue(res["ok"], res)
            self.assertTrue(dst.exists())
            self.assertAlmostEqual(cd.probe_duration(dst), 1.5, delta=0.15)


if __name__ == "__main__":
    unittest.main()
