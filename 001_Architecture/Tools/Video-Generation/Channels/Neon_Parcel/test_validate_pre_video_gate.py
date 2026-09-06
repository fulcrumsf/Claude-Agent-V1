import json
import tempfile
import unittest
from pathlib import Path

from validate_pre_video_gate import validate_shot


class PreVideoGateTests(unittest.TestCase):
    def _shot(self, root: Path, route="seedance_1_5_start_end"):
        prompt = root / "Shot-01-v1.json"
        prompt.write_text(json.dumps({"prompt": "realistic scene"}), encoding="utf-8")
        shot = {
            "shot_id": "shot-1",
            "route": route,
            "prompt_file": str(prompt),
            "visual_realism": {"status": "pass"},
            "camera_plausibility": {"status": "pass"},
            "meaningful_visual_beat": {"status": "pass"},
            "humor_context": {"status": "pass"},
            "output_resolution": "1920x1080",
            "generation_prompt": "realistic scene, fixed camera, native audio",
            "postprocess": {},
        }
        return shot

    def test_passes_native_seedance_15_without_topaz(self):
        with tempfile.TemporaryDirectory() as directory:
            result = validate_shot(self._shot(Path(directory)))
            self.assertTrue(result["ready_for_paid_generation"])

    def test_missing_gate_blocks(self):
        with tempfile.TemporaryDirectory() as directory:
            shot = self._shot(Path(directory))
            shot["humor_context"] = {"status": "review"}
            result = validate_shot(shot)
            self.assertFalse(result["ready_for_paid_generation"])

    def test_overlay_in_prompt_blocks(self):
        with tempfile.TemporaryDirectory() as directory:
            shot = self._shot(Path(directory))
            shot["generation_prompt"] = "realistic scene with a title card"
            result = validate_shot(shot)
            self.assertIn("prompt_scope:post-production overlay content detected", result["failures"])

    def test_overlay_exclusions_are_allowed(self):
        with tempfile.TemporaryDirectory() as directory:
            shot = self._shot(Path(directory))
            shot["generation_prompt"] = "realistic scene; no captions, title cards, overlays, or watermarks"
            result = validate_shot(shot)
            self.assertNotIn("prompt_scope:post-production overlay content detected", result["failures"])

    def test_mini_requires_upscale_route(self):
        with tempfile.TemporaryDirectory() as directory:
            shot = self._shot(Path(directory), "seedance_2_mini_storyboard")
            shot["generation_resolution"] = "480p"
            shot["reference_image_urls"] = ["https://cdn.example/storyboard.png"]
            shot["postprocess"] = {"topaz_factor": "2x", "final_normalization": "1920x1080"}
            root = Path(directory)
            storyboard = root / "selected-storyboard.png"
            contract = root / "contract.json"
            qa = root / "qa.json"
            state = root / "attempts.json"
            manifest = root / "handoff.json"
            storyboard.write_bytes(b"storyboard")
            contract.write_text("{}", encoding="utf-8")
            qa.write_text(json.dumps({"status": "pass", "findings": []}), encoding="utf-8")
            state.write_text(json.dumps({"events": [{"event": "selected", "attempt": 1}]}), encoding="utf-8")
            manifest.write_text(json.dumps({
                "shot_id": "shot-1",
                "status": "pass",
                "selected_attempt": 1,
                "active_storyboard_path": str(storyboard),
                "contract_path": str(contract),
                "qa_report_path": str(qa),
                "attempt_state_path": str(state),
                "storyboard_reference_url": "https://cdn.example/storyboard.png",
                "reference_role": "storyboard_reference",
                "manual_review_approved": True,
            }), encoding="utf-8")
            shot["storyboard_handoff_manifest"] = str(manifest)
            self.assertTrue(validate_shot(shot)["ready_for_paid_generation"])

    def test_mini_storyboard_requires_reference_field(self):
        with tempfile.TemporaryDirectory() as directory:
            shot = self._shot(Path(directory), "seedance_2_mini_storyboard")
            shot["generation_resolution"] = "480p"
            shot["postprocess"] = {"topaz_factor": "2x", "final_normalization": "1920x1080"}
            result = validate_shot(shot)
            self.assertIn("reference_routing:mini_storyboard_reference_missing", result["failures"])

    def test_unverified_composite_storyboard_sheet_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shot = self._shot(root, "seedance_2_mini_storyboard")
            shot["generation_resolution"] = "480p"
            shot["reference_image_urls"] = ["https://cdn.example/storyboard.png"]
            shot["reference_role"] = "storyboard_sheet"
            shot["provider_verified_storyboard_sheet"] = False
            shot["postprocess"] = {"topaz_factor": "2x", "final_normalization": "1920x1080"}
            result = validate_shot(shot)
            self.assertIn("provider_contract:composite_storyboard_sheet_not_verified_for_video", result["failures"])

    def test_storyboard_cannot_be_first_frame(self):
        with tempfile.TemporaryDirectory() as directory:
            shot = self._shot(Path(directory))
            shot["first_frame_url"] = "https://cdn.example/storyboard.png"
            result = validate_shot(shot)
            self.assertIn("reference_routing:storyboard_must_not_be_first_frame", result["failures"])

    def test_mini_storyboard_requires_selected_passing_handoff(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shot = self._shot(root, "seedance_2_mini_storyboard")
            shot["generation_resolution"] = "480p"
            shot["reference_image_urls"] = ["https://cdn.example/storyboard.png"]
            shot["postprocess"] = {"topaz_factor": "2x", "final_normalization": "1920x1080"}
            result = validate_shot(shot)
            self.assertIn("storyboard_handoff:manifest_missing", result["failures"])

    def test_mini_storyboard_blocks_manual_review_handoff(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shot = self._shot(root, "seedance_2_mini_storyboard")
            shot["generation_resolution"] = "480p"
            shot["reference_image_urls"] = ["https://cdn.example/storyboard.png"]
            shot["postprocess"] = {"topaz_factor": "2x", "final_normalization": "1920x1080"}
            manifest = root / "handoff.json"
            storyboard = root / "storyboard.png"
            contract = root / "contract.json"
            qa = root / "qa.json"
            state = root / "attempts.json"
            storyboard.write_bytes(b"storyboard")
            contract.write_text("{}", encoding="utf-8")
            qa.write_text("{}", encoding="utf-8")
            state.write_text(json.dumps({"events": [{"event": "selected", "attempt": 1}]}), encoding="utf-8")
            manifest.write_text(json.dumps({
                "shot_id": "shot-1",
                "status": "manual_review",
                "selected_attempt": 1,
                "active_storyboard_path": str(storyboard),
                "contract_path": str(contract),
                "qa_report_path": str(qa),
                "attempt_state_path": str(state),
                "storyboard_reference_url": "https://cdn.example/storyboard.png",
                "reference_role": "storyboard_reference",
            }), encoding="utf-8")
            shot["storyboard_handoff_manifest"] = str(manifest)
            result = validate_shot(shot)
            self.assertTrue(any(item.startswith("storyboard_handoff:invalid:") for item in result["failures"]))

    def test_native_1080p_topaz_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            shot = self._shot(Path(directory))
            shot["postprocess"] = {"topaz": True}
            self.assertFalse(validate_shot(shot)["ready_for_paid_generation"])

    def test_mini_first_last_requires_two_temporal_frames_and_no_upscale(self):
        with tempfile.TemporaryDirectory() as directory:
            shot = self._shot(Path(directory), "seedance_2_mini_first_last")
            shot["generation_resolution"] = "480p"
            shot["first_frame_url"] = "https://cdn.example/Shot-06-First-Frame-v2.png"
            shot["last_frame_url"] = "https://cdn.example/Shot-06-End-Frame-v2.png"
            self.assertTrue(validate_shot(shot)["ready_for_paid_generation"])
            shot["reference_image_urls"] = ["https://cdn.example/storyboard.png"]
            self.assertFalse(validate_shot(shot)["ready_for_paid_generation"])


if __name__ == "__main__":
    unittest.main()
