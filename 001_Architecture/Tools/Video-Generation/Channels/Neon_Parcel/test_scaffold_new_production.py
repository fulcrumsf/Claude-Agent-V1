import json
import tempfile
import unittest
from pathlib import Path

from scaffold_new_production import FOLDERS, scaffold


class ScaffoldTests(unittest.TestCase):
    def test_creates_expected_non_destructive_scaffold(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "Dogs-At-The-Park"
            scaffold(root)

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


if __name__ == "__main__":
    unittest.main()
