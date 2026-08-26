import json
import tempfile
import unittest
from pathlib import Path

from production_state import record_state


class ProductionStateTests(unittest.TestCase):
    def test_state_is_current_and_decisions_are_append_only(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            first = record_state(root, "clip_1_pending", "Begin first clip review")
            second = record_state(root, "clips_2_5_pending", "First clip approved")

            current = json.loads(
                (root / "Data" / "Checkpoint_State.json").read_text(encoding="utf-8")
            )
            decisions = (root / "Data" / "History" / "Decision_Log.jsonl").read_text(
                encoding="utf-8"
            ).splitlines()

            self.assertEqual(first["from_state"], "scaffolded")
            self.assertEqual(second["from_state"], "clip_1_pending")
            self.assertEqual(current["state"], "clips_2_5_pending")
            self.assertEqual(len(decisions), 2)


if __name__ == "__main__":
    unittest.main()
