"""Tests for the timing, preservation, and offline boundaries used by Gate 2."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from diagnose import load_config, offline_check, output_indices, save_json, sha256, shot_for_pts, suppress_duplicate_animals, validate_shots


class DiagnosticBoundaryTests(unittest.TestCase):
    def test_irregular_pts_are_held_until_next_real_frame(self):
        records = [{"pts": p} for p in [100, 101, 103]]
        self.assertEqual(output_indices(records, 100, 104, "1/24", 48), [0, 0, 1, 1, 1, 1, 2, 2])

    def test_real_part_three_duration_rounds_up_without_exposing_next_shot(self):
        records = [{"pts": p} for p in [1198080, 1593344]]
        indices = output_indices(records, 1198080, 1594368, "1/12288")
        self.assertEqual(len(indices), 968)
        self.assertEqual(indices[-1], 1)
        self.assertTrue(all(i in (0, 1) for i in indices))

    def test_cut_frame_belongs_to_new_shot(self):
        shots = [{"id": "a", "start_pts": 0, "end_pts": 10}, {"id": "b", "start_pts": 10, "end_pts": 20}]
        validate_shots(shots)
        self.assertEqual(shot_for_pts(shots, 10)["id"], "b")
        with self.assertRaises(ValueError):
            shot_for_pts(shots, 20)
        with self.assertRaises(ValueError):
            validate_shots([shots[0], {"id": "b", "start_pts": 11, "end_pts": 20}])

    def test_existing_json_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "record.json"
            save_json(path, {"original": True})
            with self.assertRaises(FileExistsError):
                save_json(path, {"original": False})
            self.assertEqual(json.loads(path.read_text()), {"original": True})

    def test_changed_source_is_rejected_before_loading_model(self):
        with tempfile.TemporaryDirectory() as d:
            source = Path(d) / "source.mp4"
            source.write_bytes(b"original fixture")
            cfg = {"source": str(source), "source_sha256": sha256(source),
                   "shots": [{"id": "a", "start_pts": 0, "end_pts": 1}],
                   "classes": [0, 21], "inference_size": 960, "confidence": 0.1}
            path = Path(d) / "config.json"
            save_json(path, cfg)
            source.write_bytes(b"changed fixture")
            with self.assertRaisesRegex(ValueError, "fingerprint changed"):
                load_config(path)

    def test_unprotected_launch_is_rejected(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "run_offline"):
                offline_check()

    def test_duplicate_species_labels_do_not_hide_a_distinct_nearby_animal(self):
        import numpy as np
        # Bear/dog labels cover one animal; the touching third box is another animal.
        data = np.array([[0, 0, 100, 100, 0.6, 21],
                         [2, 2, 98, 98, 0.9, 16],
                         [90, 0, 190, 100, 0.8, 21]], dtype=float)
        original = data.copy()
        self.assertEqual(suppress_duplicate_animals(data), [1, 2])
        np.testing.assert_array_equal(data, original)

    def test_no_animals_is_a_valid_detection_result(self):
        import numpy as np
        self.assertEqual(suppress_duplicate_animals(np.empty((0, 6))), [])


if __name__ == "__main__":
    unittest.main()
