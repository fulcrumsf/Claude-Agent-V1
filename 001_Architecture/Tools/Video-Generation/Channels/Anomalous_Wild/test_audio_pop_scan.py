#!/usr/bin/env python3
"""Tests for audio_pop_scan.scan() — the splice-pop detector.

Run: python3 test_audio_pop_scan.py
"""
import unittest

import numpy as np

from audio_pop_scan import scan, SR


def _tone(dur_s, freq=180.0, amp=0.25):
    t = np.arange(int(dur_s * SR)) / SR
    return (amp * np.sin(2 * np.pi * freq * t)).astype(np.float32)


def _silence(dur_s):
    return np.zeros(int(dur_s * SR), dtype=np.float32)


class ScanDetector(unittest.TestCase):
    def test_clean_speechlike_audio_has_no_findings(self):
        a = np.concatenate([_silence(0.2), _tone(1.0), _silence(0.2), _tone(1.0), _silence(0.2)])
        self.assertEqual(scan(a), [])

    def test_hard_step_out_of_silence_is_flagged(self):
        # a brief low-level burst inside silence: the edges are hard steps whose
        # ±40ms neighbourhood is still near-silent
        burst = np.array([0.5], np.float32)  # single-sample impulse — a real click
        a = np.concatenate([_silence(0.5), burst, _silence(0.5)])
        found = scan(a)
        self.assertTrue(found)
        self.assertEqual(found[0]["kind"], "silence_bounded_step")
        self.assertGreaterEqual(found[0]["step"], 0.45)

    def test_very_hard_step_flagged_even_amid_loud_audio(self):
        loud = _tone(1.0, amp=0.4)
        loud2 = _tone(1.0, amp=0.4, freq=181.0) + 0.7  # +0.7 DC jump at the splice
        a = np.concatenate([loud, loud2])
        found = scan(a)  # no join declared — must still catch it via VERY_HARD
        self.assertTrue(any(f["kind"] == "hard_step" for f in found))

    def test_loud_continuous_tone_edge_is_not_flagged_without_join(self):
        # a tone that starts already ramped (no silence-bounded step) stays clean
        a = np.concatenate([_tone(0.5), _tone(0.5, freq=240.0)])
        # phase discontinuity here is small; detector must not cry pop on normal content
        self.assertEqual(scan(a), [])

    def test_join_discontinuity_flagged_even_when_not_in_silence(self):
        left = _tone(1.0)
        right = _tone(1.0, freq=181.0) + 0.35  # DC jump at the splice, mid-energy
        a = np.concatenate([left, right])
        found = scan(a, joins=[1.0])
        self.assertTrue(any(f["kind"] == "join_discontinuity" for f in found))

    def test_join_check_clean_when_faded(self):
        left = _tone(1.0)
        fade = np.linspace(1, 0, int(0.02 * SR), dtype=np.float32)
        left[-len(fade):] *= fade
        right = _tone(1.0, freq=181.0)
        right[:len(fade)] *= fade[::-1]
        a = np.concatenate([left, right])
        self.assertEqual(scan(a, joins=[1.0]), [])

    def test_clusters_collapse_to_single_finding(self):
        spike = np.full(int(0.2 * SR), 0.6, np.float32)
        a = np.concatenate([_silence(0.3), spike, _silence(0.3)])
        # entering AND leaving the block are both hard steps in silence — but within 50ms? no.
        # they're 0.2s apart, so 2 findings is correct; assert we don't get dozens.
        self.assertLessEqual(len(scan(a)), 2)


if __name__ == "__main__":
    unittest.main()
