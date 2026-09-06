import tempfile
import unittest
from pathlib import Path

from artifact_preservation import archive_existing, require_versioned_path


class ArtifactPreservationTests(unittest.TestCase):
    def test_existing_versioned_output_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "Shot-08-480p-v3.mp4"
            path.write_bytes(b"original")
            with self.assertRaises(FileExistsError):
                require_versioned_path(path)
            self.assertEqual(path.read_bytes(), b"original")

    def test_unversioned_output_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                require_versioned_path(Path(directory) / "Shot-08-480p.mp4")

    def test_archive_refuses_collision(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "Shot-08-v3.mp4"
            archive = root / "Archived"
            source.write_bytes(b"source")
            archive.mkdir()
            (archive / source.name).write_bytes(b"older archive")
            with self.assertRaises(FileExistsError):
                archive_existing(source, archive)
            self.assertTrue(source.exists())
            self.assertEqual((archive / source.name).read_bytes(), b"older archive")

    def test_archive_moves_existing_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "Shot-08-v3.mp4"
            source.write_bytes(b"source")
            destination = archive_existing(source, root / "Archived")
            self.assertEqual(destination, root / "Archived" / source.name)
            self.assertFalse(source.exists())
            self.assertEqual(destination.read_bytes(), b"source")


if __name__ == "__main__":
    unittest.main()
