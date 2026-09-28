import json
import tempfile
import unittest
from pathlib import Path

from scaffold_new_production import FOLDERS, SHOT_FOLDERS, scaffold, scaffold_shot


class ScaffoldTests(unittest.TestCase):
    def test_creates_expected_non_destructive_scaffold(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "Dogs-At-The-Park"
            root = scaffold(root)

            for relative_folder in FOLDERS:
                self.assertTrue((root / relative_folder).is_dir())

            manifest_path = root / "Data" / "Production_Manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["long_form"]["aspect_ratio"], "16:9")
            self.assertTrue(manifest["shorts"]["target_is_soft"])
            self.assertEqual(manifest["shorts"]["overlay_frames"], [1, 30])

            manifest_path.write_text("user-approved-manifest\n", encoding="utf-8")
            scaffold(root)
            self.assertEqual(
                manifest_path.read_text(encoding="utf-8"), "user-approved-manifest\n"
            )

    def test_shot_scaffold_is_standard_and_non_destructive(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = scaffold(Path(temporary_directory) / "0003_Test-Compilation")
            shot = scaffold_shot(root, "Shot-08-Otter-Doorstep-NZ")
            self.assertEqual(shot, root / "Production" / "Shot-08-Otter-Doorstep-NZ")
            for relative_folder in SHOT_FOLDERS:
                self.assertTrue((shot / relative_folder).is_dir())

            kept = shot / "Data" / "Generation_Log.json"
            kept.write_text("keep-me\n", encoding="utf-8")
            scaffold_shot(root, "Shot-08-Otter-Doorstep-NZ")
            self.assertEqual(kept.read_text(encoding="utf-8"), "keep-me\n")

            with self.assertRaises(ValueError):
                scaffold_shot(root, "otter shot")


if __name__ == "__main__":
    unittest.main()
