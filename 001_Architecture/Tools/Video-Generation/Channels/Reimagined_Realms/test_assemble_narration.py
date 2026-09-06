#!/usr/bin/env python3
"""Tests for assemble.py's edge-faded narration concat (Glass Frog 0003 Block C / P6).

Run: python3 test_assemble_narration.py
"""
import unittest

from assemble import build_narration_concat_filter, NARRATION_JOIN_FADE_S


class BuildNarrationConcatFilter(unittest.TestCase):
    def test_one_stage_per_input_plus_concat(self):
        f = build_narration_concat_filter([3.0, 4.0, 5.0])
        stages = f.split(";")
        self.assertEqual(len(stages), 4)  # 3 fade stages + 1 concat
        self.assertIn("concat=n=3:v=0:a=1[out]", stages[-1])
        self.assertTrue(stages[-1].startswith("[a0][a1][a2]"))

    def test_every_input_gets_both_fades(self):
        f = build_narration_concat_filter([2.5, 6.0])
        self.assertEqual(f.count("afade=t=in:st=0:d="), 2)
        self.assertEqual(f.count("afade=t=out:st="), 2)

    def test_fade_out_starts_fade_len_before_each_clip_end(self):
        f = build_narration_concat_filter([10.0], fade_s=0.02)
        self.assertIn("afade=t=out:st=9.9800:d=0.02", f)

    def test_short_clip_clamps_fade_out_start_to_zero(self):
        f = build_narration_concat_filter([0.01], fade_s=0.02)
        self.assertIn("afade=t=out:st=0.0000:d=0.02", f)

    def test_default_fade_is_20ms(self):
        self.assertEqual(NARRATION_JOIN_FADE_S, 0.02)
        f = build_narration_concat_filter([1.0])
        self.assertIn("d=0.02", f)

    def test_resamples_every_input_to_44100_mono(self):
        f = build_narration_concat_filter([1.0, 2.0, 3.0])
        self.assertEqual(f.count("aresample=44100,aformat=channel_layouts=mono"), 3)


if __name__ == "__main__":
    unittest.main()
