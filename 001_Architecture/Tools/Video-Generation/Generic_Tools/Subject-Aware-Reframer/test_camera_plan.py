"""Behavioral tests for framing, timing, settings, and preservation."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from camera_plan import build_plan, observations, settings_for
from reframe import new_output, validate_plan

PROFILES = json.loads((Path(__file__).parent/"Framing-Profiles-v1.json").read_text())


def fixture(shots=1, seconds=5, moving=False):
    count = seconds*30
    frames, segments = [], []
    for s in range(shots):
        segments.append({"id": f"Scene-{s}", "start_pts": s*count, "end_pts": (s+1)*count})
        for i in range(count):
            x = 400+i*3 if moving else 400
            frames.append({"source_frame": s*count+i, "pts": s*count+i,
                "source_seconds": (s*count+i)/30, "shot": f"Scene-{s}",
                "tracks": [
                    {"id": f"Scene-{s}:person:1", "family": "person", "class_id": 0,
                     "confirmed": True, "confidence": .9, "bbox_xyxy": [x,250,x+150,850]},
                    {"id": f"Scene-{s}:animal:2", "family": "animal", "class_id": 21,
                     "confirmed": True, "confidence": .9, "bbox_xyxy": [1300,600,1600,900]}]})
    return {"config": {"family_tracking": True, "time_base": "1/30", "shots": segments,
                        "expected_source_frames": len(frames)},
            "frames": frames, "stream": {"width": 1920,"height": 1080,"time_base": "1/30"}}


def make_plan(cache, mode, overrides=None, shots=None):
    settings = settings_for(PROFILES["defaults"], PROFILES["profiles"][mode], overrides)
    result = build_plan(cache, settings, shots or {}, {"width": 1080,"height": 1920,"fps": 30})
    validate_plan({"variants": {"test": result}},cache)
    return result


class FramingTests(unittest.TestCase):
    def test_group_mode_never_discards_source_edges(self):
        plan = make_plan(fixture(), "group")
        self.assertTrue(all(f["crop_xyxy"] == [0,0,1920,1080] and f["layout"] == "fit_blur" for f in plan["frames"]))

    def test_subject_mode_follows_motion_with_bounded_speed_and_full_subject(self):
        plan = make_plan(fixture(moving=True), "subject", {"switch_policy": "priority"})
        crop = [f for f in plan["frames"] if f["layout"] == "crop"]
        self.assertEqual(len(crop), len(plan["frames"]))
        self.assertGreater(crop[-1]["crop_xyxy"][0], crop[0]["crop_xyxy"][0]+300)
        for a,b in zip(crop,crop[1:]):
            if not b["cut"]:
                self.assertLessEqual(abs(sum(b["crop_xyxy"][::2])/2-sum(a["crop_xyxy"][::2])/2),1920*.65/30+1e-4)

    def test_alternation_works_for_two_people_without_an_animal(self):
        cache = fixture(seconds=4)
        for r in cache["frames"]:
            r["tracks"][1].update(id="Scene-0:person:2",family="person",class_id=0)
        plan = make_plan(cache,"subject",{"subject_hold_seconds":1})
        selected = [plan["frames"][i*30]["focus"]["id"] for i in range(4)]
        self.assertEqual(selected,["Scene-0:person:1","Scene-0:person:2","Scene-0:person:1","Scene-0:person:2"])

    def test_hybrid_combines_views_and_keeps_the_payoff_wide(self):
        plan = make_plan(fixture(seconds=10),"hybrid")
        self.assertEqual(plan["frames"][0]["layout"],"crop")
        self.assertEqual(plan["frames"][120]["layout"],"fit_blur")
        self.assertEqual(plan["frames"][200]["layout"],"crop")
        self.assertTrue(all(f["layout"]=="fit_blur" for f in plan["frames"][-60:]))

    def test_too_wide_a_subject_falls_back_without_clipping(self):
        cache=fixture()
        for r in cache["frames"]:
            r["tracks"]=r["tracks"][:1]
            r["tracks"][0]["bbox_xyxy"]=[200,100,1600,1000]
        plan=make_plan(cache,"subject")
        self.assertTrue(all(f["layout"]=="fit_blur" for f in plan["frames"]))

    def test_one_subject_does_not_get_a_scheduled_camera_reset(self):
        cache = fixture()
        for r in cache["frames"]:
            r["tracks"] = r["tracks"][:1]
        plan = make_plan(cache,"subject")
        self.assertEqual(sum(f["cut"] for f in plan["frames"]),1)

    def test_hybrid_ending_stays_wide_when_an_animal_exits(self):
        cache = fixture(seconds=10)
        for r in cache["frames"][270:]:
            r["tracks"] = r["tracks"][:1]
        plan = make_plan(cache,"hybrid")
        self.assertTrue(all(f["layout"]=="fit_blur" for f in plan["frames"][-60:]))

    def test_brief_crop_return_between_wide_views_is_suppressed(self):
        from camera_plan import suppress_short_crop_returns
        frames = [{"output_seconds":i/30, "layout":"crop" if 50 <= i < 65 else "fit_blur",
                   "camera_segment":"a:crop" if 50 <= i < 65 else "a:wide", "shot":"a",
                   "crop_xyxy":[0,0,600,1080], "focus":{}} for i in range(90)]
        suppress_short_crop_returns(frames,1.5,1920,1080)
        self.assertTrue(all(f["layout"]=="fit_blur" for f in frames))
        self.assertEqual(sum(f["cut"] for f in frames),1)

    def test_unknown_settings_and_shot_names_fail(self):
        with self.assertRaisesRegex(ValueError,"Unknown framing"):
            make_plan(fixture(),"subject",{"typo":1})
        with self.assertRaisesRegex(ValueError,"unknown shot"):
            make_plan(fixture(),"subject",shots={"not-a-shot":{"mode":"group"}})
        with self.assertRaisesRegex(ValueError,"odd integer"):
            make_plan(fixture(),"group",{"background_blur":20})

    def test_scene_override_is_local_and_cut_resets_camera(self):
        plan=make_plan(fixture(shots=2),"subject",shots={"Scene-1":{"mode":"group"}})
        self.assertEqual(plan["frames"][0]["layout"],"crop")
        self.assertEqual(plan["frames"][150]["layout"],"fit_blur")
        self.assertTrue(plan["frames"][150]["cut"])
        self.assertEqual(plan["resolved_shot_settings"]["Scene-0"]["mode"],"subject")

    def test_gap_bridging_stops_after_the_configured_limit(self):
        cache=fixture(seconds=2)
        records=cache["frames"]
        for r in records[15:]:
            r["tracks"]=[]
        settings=settings_for(PROFILES["defaults"],{})
        candidates=observations(records,[.5,.8,1.5],settings,1920,1080)
        self.assertEqual(len(candidates[0]),2)
        self.assertEqual(candidates[1],[])
        self.assertEqual(candidates[2],[])

    def test_new_run_cannot_overwrite_or_escape_output_root(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            job={"output_root":str(root)}
            (root/"existing").mkdir()
            with self.assertRaises(FileExistsError):
                new_output(root/"existing",job)
            with self.assertRaisesRegex(ValueError,"direct new child"):
                new_output(root.parent/"escaped",job)

    def test_renderer_preserves_complete_foreground_in_group_view(self):
        import numpy as np
        from render_reframe import group_frame
        source=np.zeros((180,320,3),dtype=np.uint8)
        source[:]=[80,120,200]
        source[:, :8]=[0,0,255]
        source[:, -8:]=[255,0,0]
        frame=group_frame(source,180,320,.5,21)
        self.assertEqual(frame.shape,(320,180,3))
        self.assertGreater(int(frame[160,1,2]),240)
        self.assertGreater(int(frame[160,-2,0]),240)


if __name__=="__main__":
    unittest.main()
