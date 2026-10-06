"""Tests for lab_run_log.py. Every project here is a fake one in the temp folder: nothing touches
001_Architecture/Lab/, nothing calls OpenRouter or any paid API, and the calibration log is stubbed."""
import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import lab_run_log as R



def boom(*a, **k):
    raise AssertionError("/lab-run must never reach the OpenRouter picker or a /lab-build build")


def run(fn, *a, **k):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        code = fn(*a, **k)
    tagged = [ln for ln in out.getvalue().splitlines() if ln.startswith("LAB_RUN_")]
    doc = json.loads(tagged[-1].split(" ", 1)[1]) if tagged else None
    return code, doc


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        # never write test runs into Tony's calibration log; any picker or build call fails the test
        for target, name, value in ((R.B.L, "log_event", lambda event: None), (R.B.L, "pick", boom),
                                    (R.B.L, "live_prices", boom), (R.B.L, "run_worker", boom),
                                    (R.B, "build_main", boom), (R.B, "run_worker", boom)):
            patcher = mock.patch.object(target, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def tearDown(self):
        self.tmp.cleanup()

    def project(self, name="2026-10-03_Word_Tool", nxt="lab_run", total=90.0, cleared=True,
                plan=True, meta=True, verdict=True):
        proj = self.root / name
        build = proj / "Build_Worktree_1" / "Tools" / "Word_Tool"
        build.mkdir(parents=True)
        (build / "word_tool.py").write_text("print('word')\n")
        if plan:
            (proj / "Plan_Locked.md").write_text("# Plan\n## How To Verify\nRun it.\n")
        if meta:
            R.B.write_json(proj / "Build_Meta.json", {"worktrees": [{
                "worktree": str(proj / "Build_Worktree_1"), "build_dir": str(build),
                "branch": "lab/x/wt1", "built_by": "deepseek/deepseek-v4-pro", "attempt": 1}]})
        if verdict:
            R.B.write_json(proj / "Build_Verdict.json", {
                "current": {"stage": "raw", "total": total, "cleared": cleared, "next": nxt},
                "history": [], "tony_paid_run": ["Run it once on real input."]})
        return proj, build

    def log(self, proj, grade, notes="liked it", tried="ran it", changes=""):
        return run(R.log_main, proj, tried, notes, str(grade), changes)


class GateTests(Fixture):
    def test_cleared_build_passes_gate(self):
        proj, build = self.project()
        info, why = R.gate(proj)
        self.assertIsNone(why)
        self.assertEqual(info["build_dir"], str(build))
        self.assertEqual(info["build_total"], 90.0)
        self.assertEqual(info["tony_paid_run"], ["Run it once on real input."])

    def test_each_unfinished_step_is_named(self):
        cases = [(dict(plan=False), "/lab-plan"), (dict(meta=False), "run /lab-build first"),
                 (dict(verdict=False), "Step 2"), (dict(nxt="fix_round", total=70, cleared=False), "Step 4"),
                 (dict(nxt="rebuild", total=40, cleared=False), "Step 5"),
                 (dict(nxt="stop", total=60, cleared=False), "without clearing 80")]
        for i, (kw, words) in enumerate(cases):
            proj, _ = self.project(name=f"2026-10-03_P{i}", **kw)
            info, why = R.gate(proj)
            self.assertIsNone(info, kw)
            self.assertIn(words, why, kw)

    def test_lab_run_with_score_under_80_is_refused(self):
        proj, _ = self.project(total=79.0)
        self.assertIsNone(R.gate(proj)[0])

    def test_status_on_uncleared_project_exits_2_and_writes_nothing(self):
        proj, _ = self.project(nxt="fix_round", total=70, cleared=False)
        code, doc = run(R.status_main, str(proj), self.root)
        self.assertEqual(code, 2)
        self.assertIn("Step 4", doc["why"])
        self.assertFalse((proj / R.RUN_LOG).exists())


class LogTests(Fixture):
    def test_rounds_append_and_track_changes(self):
        proj, build = self.project()
        code, doc = self.log(proj, 72, notes="too slow")
        self.assertEqual((code, doc["round"], doc["passed"], doc["next"]), (0, 1, False, "harness_fix_then_retry"))
        (build / "word_tool.py").write_text("print('word, faster')\n")
        (build / "helper.py").write_text("x = 1\n")
        code, doc = self.log(proj, 85, changes="cached the lookup")
        self.assertEqual((code, doc["round"], doc["passed"], doc["next"]), (0, 2, True, "lab_promote"))
        lines = [json.loads(x) for x in (proj / R.RUN_LOG).read_text().splitlines()]
        self.assertEqual([x["grade"] for x in lines], [72, 85])
        self.assertEqual(lines[0]["notes"], "too slow")
        self.assertIsNone(lines[0]["folder_changes_since_last_round"])
        self.assertEqual(lines[1]["folder_changes_since_last_round"],
                         {"added": ["helper.py"], "removed": [], "modified": ["word_tool.py"]})
        self.assertEqual(lines[1]["changes_before_this_try"], "cached the lookup")
        self.assertEqual(lines[0]["log"], "lab_run/v1")
        self.assertEqual(lines[1]["build_total"], 90.0)

    def test_bad_input_is_rejected_and_nothing_written(self):
        proj, _ = self.project()
        for grade in ("101", "-1", "abc", "85.5", ""):
            self.assertEqual(self.log(proj, grade)[0], 1, grade)
        self.assertEqual(run(R.log_main, proj, "ran it", "  ", "85", "")[0], 1)
        self.assertEqual(run(R.log_main, proj, "", "notes", "85", "")[0], 1)
        self.assertFalse((proj / R.RUN_LOG).exists())

    def test_log_refuses_an_uncleared_build(self):
        proj, _ = self.project(nxt="rebuild", total=40, cleared=False)
        code, doc = self.log(proj, 90)
        self.assertEqual(code, 2)
        self.assertFalse((proj / R.RUN_LOG).exists())

    def test_log_writes_only_its_own_file(self):
        proj, build = self.project()
        before = sorted(p.relative_to(self.root) for p in self.root.rglob("*"))
        self.log(proj, 90)
        after = sorted(p.relative_to(self.root) for p in self.root.rglob("*"))
        self.assertEqual(set(after) - set(before), {proj.relative_to(self.root) / R.RUN_LOG})
        self.assertEqual(R.B.read_json(proj / "Build_Verdict.json")["current"]["next"], "lab_run")


class StatusTests(Fixture):
    def test_cleared_for_promote_needs_pass_and_unchanged_folder(self):
        proj, build = self.project()
        self.log(proj, 60)
        self.assertFalse(run(R.status_main, str(proj), self.root)[1]["cleared_for_promote"])
        self.log(proj, 88)
        code, doc = run(R.status_main, str(proj), self.root)
        self.assertTrue(doc["cleared_for_promote"])
        self.assertFalse(doc["folder_changed_since_last_round"])
        self.assertEqual([r["grade"] for r in doc["rounds"]], [60, 88])
        (build / "word_tool.py").write_text("print('edited after the passing grade')\n")
        code, doc = run(R.status_main, str(proj), self.root)
        self.assertFalse(doc["cleared_for_promote"])
        self.assertEqual(doc["changes_since_last_round"]["modified"], ["word_tool.py"])

    def test_edited_earlier_line_is_reported_not_blocked(self):
        proj, _ = self.project()
        self.log(proj, 60)
        self.log(proj, 70)
        p = proj / R.RUN_LOG
        p.write_text(p.read_text().replace('"grade": 60', '"grade": 95', 1))
        code, doc = run(R.status_main, str(proj), self.root)
        self.assertEqual(code, 0)
        self.assertTrue(any("line 2" in x and "edited" in x for x in doc["log_problems"]), doc["log_problems"])
        self.assertEqual(self.log(proj, 81)[0], 0)  # append-only by convention, not a lock

    def test_newest_eligible_skips_runs_already_cleared(self):
        old, _ = self.project(name="2026-10-01_Old")
        new, _ = self.project(name="2026-10-03_New")
        self.project(name="2026-10-04_Unbuilt", meta=False, verdict=False)
        self.assertEqual(R.resolve(None, self.root), new)
        self.log(new, 90)
        self.assertEqual(R.resolve(None, self.root), old)
        self.log(old, 85)
        self.assertIsNone(R.resolve(None, self.root))
        self.assertEqual(run(R.status_main, None, self.root)[0], 1)


class CommandTests(Fixture):
    def test_refused_inside_delegated_worker(self):
        os.environ["AGENT_OS_DELEGATE_WORKER"] = "1"
        try:
            self.assertEqual(run(R.main, ["status"])[0], 3)
        finally:
            del os.environ["AGENT_OS_DELEGATE_WORKER"]

    def test_cli_log_round_trip(self):
        proj, _ = self.project()
        code, doc = run(R.main, ["log", str(proj), "--tried", "ran it", "--notes", "good", "--grade", "83"])
        self.assertEqual((code, doc["passed"]), (0, True))
        self.assertEqual(run(R.main, ["log", str(proj), "--grade", "83"])[0], 1)
        self.assertEqual(run(R.main, ["bogus"])[0], 1)

    def test_checks_is_a_smoke_test_that_writes_nothing(self):
        proj, build = self.project()
        R.B.write_json(proj / "Acceptance_Checks.json", {"checks": [
            {"id": "C1", "tier": 0, "what": "a", "run": "true", "pass_if": "exit code 0"},
            {"id": "C2", "tier": 2, "what": "b", "run": "false", "pass_if": "exit code 0"}]})
        before = sorted(self.root.rglob("*"))
        real = R.B.run_check
        R.B.run_check = lambda c, d: real(c, d, sandbox=False)  # the live sandbox path is covered in test_lab_build
        try:
            code, doc = run(R.checks_main, proj)
        finally:
            R.B.run_check = real
        self.assertEqual((code, doc["passed"], doc["total"]), (0, 1, 2))
        self.assertEqual(doc["failed"], ["C2 (b)"])
        self.assertEqual(sorted(self.root.rglob("*")), before)


if __name__ == "__main__":
    unittest.main()
