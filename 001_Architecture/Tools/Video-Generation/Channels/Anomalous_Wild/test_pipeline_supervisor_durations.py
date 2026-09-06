"""Integration tests for the duration-padding / trim-guard wiring added to
pipeline_supervisor.py (2026-08-30, 0003_Glass_Frog_Transparency fix).

The supervisor does module-level path setup from sys.argv[1], so we point it at
a throwaway temp dir before importing it."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_TMP = tempfile.mkdtemp()
(Path(_TMP) / "Production").mkdir(parents=True, exist_ok=True)
sys.argv = ["pipeline_supervisor.py", _TMP]

import pipeline_supervisor as ps  # noqa: E402


class GenRequestDurationTests(unittest.TestCase):
    def test_uses_target_duration_padded(self):
        self.assertEqual(ps.gen_request_duration(
            {"target_duration_s": 6.3, "model": "bytedance/seedance-1.5-pro"}), 8)

    def test_sub_floor_target_clamped(self):
        self.assertEqual(ps.gen_request_duration(
            {"target_duration_s": 3.855, "model": "bytedance/seedance-1.5-pro"}), 5)

    def test_legacy_duration_s_still_padded(self):
        self.assertEqual(ps.gen_request_duration(
            {"duration_s": 6, "model": "kling-3.0/video"}), 7)

    def test_missing_everything_falls_back_to_eight(self):
        self.assertEqual(ps.gen_request_duration({"model": "veo3_fast"}), 8)


class StartupGuardTests(unittest.TestCase):
    def _write_manifest(self, entries):
        ps.PROMPTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        ps.PROMPTS_FILE.write_text(json.dumps(entries))

    def test_run_aborts_when_a_video_entry_lacks_target_duration_s(self):
        self._write_manifest([
            {"scene_id": "scene_01a", "generation_type": "video",
             "output_folder": _TMP, "target_duration_s": 5.0},
            {"scene_id": "scene_02a", "generation_type": "video",
             "output_folder": _TMP},  # <-- missing
        ])
        with mock.patch.object(ps, "notify"), mock.patch.object(ps, "check_audio_layers"):
            with self.assertRaises(SystemExit) as cm:
                ps.run()
        self.assertEqual(cm.exception.code, 1)


class PreloopTrimTests(unittest.TestCase):
    def setUp(self):
        if subprocess.run(["which", "ffmpeg"], capture_output=True).returncode != 0:
            self.skipTest("ffmpeg not available")

    def test_target_aware_preloop_trims_and_flags_short(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "raw.mp4"
            subprocess.run(
                ["ffmpeg", "-y", "-f", "lavfi", "-i", "testsrc=size=320x240:rate=30",
                 "-t", "6.1", "-pix_fmt", "yuv420p", str(src), "-loglevel", "error"],
                check=True,
            )
            # target within footage -> trims to target, not flagged
            ok = ps.preloop(src, Path(d) / "a.mp4", target_s=5.9)
            self.assertTrue(ok["ok"])
            self.assertFalse(ok["needs_fill"])
            self.assertAlmostEqual(ok["final_s"], 5.9, places=3)

            # target beyond footage -> keep the clip at real length, flag needs_fill,
            # never fail and never loop (assembly freeze-fills)
            short = ps.preloop(src, Path(d) / "b.mp4", target_s=7.5)
            self.assertTrue(short["ok"])
            self.assertTrue(short["needs_fill"])
            self.assertGreater(short["shortfall_s"], 1.0)
            self.assertTrue((Path(d) / "b.mp4").exists())
            self.assertLess(short["final_s"], 7.5)

    def test_legacy_preloop_without_target_keeps_natural_length(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "raw.mp4"
            subprocess.run(
                ["ffmpeg", "-y", "-f", "lavfi", "-i", "testsrc=size=320x240:rate=30",
                 "-t", "4", "-pix_fmt", "yuv420p", str(src), "-loglevel", "error"],
                check=True,
            )
            res = ps.preloop(src, Path(d) / "out.mp4")
            self.assertTrue(res["ok"])
            self.assertTrue((Path(d) / "out.mp4").exists())


if __name__ == "__main__":
    unittest.main()
