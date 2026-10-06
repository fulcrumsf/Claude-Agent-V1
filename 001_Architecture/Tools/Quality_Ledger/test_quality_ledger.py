"""Offline unittest suite for quality_ledger.py (stdlib only, no network)."""

from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import quality_ledger as ql  # noqa: E402


def make_event(source, **overrides):
    base = {
        "event_id": "ev-1", "timestamp": "2026-10-02T10:00:00+00:00",
        "workflow_id": "wf", "run_id": "r1", "step": "s1", "level": "step",
        "attempt": 1, "source": source, "actor": "tool", "reason": "because",
    }
    base.update(overrides)
    return base


class SchemaTests(unittest.TestCase):
    def test_schema_enums_match_code(self):
        schema = json.loads((ql.SCHEMA_FILE).read_text(encoding="utf-8"))
        props = schema["properties"]
        self.assertEqual(props["source"]["enum"], list(ql.SOURCES))
        self.assertEqual(props["level"]["enum"], list(ql.LEVELS))
        self.assertEqual(props["check"]["properties"]["result"]["enum"],
                         list(ql.CHECK_RESULTS))
        self.assertEqual(props["director"]["properties"]["decision"]["enum"],
                         list(ql.DECISIONS))
        self.assertEqual(props["failure_type"]["enum"], list(ql.FAILURE_TYPES))
        self.assertNotIn("failure_type", schema["required"])
        self.assertEqual(json.loads((ql.GRADE_SCALE_FILE).read_text()),
                         ql.load_grade_scale())

    def test_readiness_policy_defaults(self):
        policy = ql.load_readiness_policy()
        self.assertEqual(policy["threshold"], 87)
        self.assertEqual(policy["window"], 10)
        self.assertEqual(policy["min_runs"], 3)
        self.assertEqual(policy["max_recent_redo"], 0)


class ValidateRuleTests(unittest.TestCase):
    def test_mechanical_with_grade_rejected(self):
        ev = make_event("mechanical_check",
                        check={"name": "c", "result": "fail",
                               "measured": 1.7, "threshold": 1.0, "unit": "x_scale"},
                        director={"grade": "B+", "verbatim": "x"})
        errors, _ = ql.validate_event(ev)
        self.assertTrue(any("must not have director" in e for e in errors))

    def test_director_with_check_rejected(self):
        ev = make_event("director_judgment", actor="Tony", step="final",
                        director={"grade": "B+", "decision": "accept", "verbatim": "B+"},
                        check={"name": "c", "result": "pass"})
        errors, _ = ql.validate_event(ev)
        self.assertTrue(any("must not have check" in e for e in errors))

    def test_self_correction_no_reason_rejected(self):
        ev = make_event("agent_self_correction", reason="")
        errors, _ = ql.validate_event(ev)
        self.assertTrue(any("non-empty reason" in e for e in errors))

    def test_unknown_key_rejected(self):
        ev = make_event("mechanical_check", check={"name": "c", "result": "pass"},
                        director=None)
        ev.pop("director", None)
        ev["surprise"] = True
        errors, _ = ql.validate_event(ev)
        self.assertTrue(any("unknown top-level key" in e for e in errors))

    def test_measured_must_be_number_or_null(self):
        ev = make_event("mechanical_check", check={"name": "c", "result": "fail",
                                                   "measured": [1.7, 2.0]})
        errors, _ = ql.validate_event(ev)
        self.assertTrue(any("must be a number or null" in e for e in errors))


class OverrideTests(unittest.TestCase):
    def test_override_flags(self):
        scale = ql.load_grade_scale()
        self.assertTrue(ql.director_is_override(
            {"grade": "C+", "decision": "accept_with_flaws"}, 87, scale))
        self.assertFalse(ql.director_is_override(
            {"grade": "B+", "decision": "accept"}, 87, scale))
        self.assertFalse(ql.director_is_override(
            {"grade": "C+", "decision": "redo"}, 87, scale))
        self.assertFalse(ql.director_is_override({"grade": "C+"}, 87, scale))


class FixtureReportTests(unittest.TestCase):
    def test_report_numbers_on_fixture(self):
        events = ql.read_events((HERE / "Fixture_Ledger_Valid.jsonl"))
        report = ql.compute_report(
            events, threshold=87, window=10, min_runs=3, grade_scale=ql.load_grade_scale())
        w = report["workflows"]
        n = w["neon_parcel_longform"]
        e = w["etsy_listing"]
        self.assertEqual((n["n"], n["mean"], n["ready"]), (3, 88.0, True))
        self.assertEqual(n["overridden_passes"], 1)
        self.assertGreaterEqual(n["mech_error"], 1)
        self.assertGreaterEqual(n["mech_fail"], 1)
        self.assertGreaterEqual(n["self_corrections"], 1)
        self.assertEqual((e["n"], e["ready"], e["overridden_passes"]), (1, False, 0))
        self.assertEqual((n["director_edits"], e["director_edits"]), (0, 0))
        step = [s for s in report["steps"] if s["step"] == "character_sheet.motoboy"][0]
        self.assertEqual((step["first_grade"], step["latest_grade"], step["delta"]),
                         ("C-", "B+", 17))


class DirectorEditReportTests(unittest.TestCase):
    def test_report_json_counts_director_edits_without_touching_readiness(self):
        import contextlib
        src = (HERE / "Fixture_Ledger_Valid.jsonl").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "L.jsonl"
            ledger.write_text(src, encoding="utf-8")
            ql.append_event(ledger, make_event(
                "director_edit", event_id="ev-edit-1", actor="Tony",
                workflow_id="neon_parcel_longform", run_id="r-edit",
                step="environment.pov", attempt=2,
                reason="Tony repainted the hedge himself",
                failure_type="spatial_layout"))
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = ql.main(["report", str(ledger), "--threshold", "87", "--json"])
            self.assertEqual(rc, 0)
            w = json.loads(buf.getvalue())["workflows"]
            n, e = w["neon_parcel_longform"], w["etsy_listing"]
            self.assertEqual(n["director_edits"], 1)
            self.assertEqual(e["director_edits"], 0)
            # Visibility only: readiness math identical to the fixture without the edit.
            self.assertEqual((n["n"], n["mean"], n["ready"]), (3, 88.0, True))
            self.assertEqual(n["overridden_passes"], 1)


class AppendAndAttemptTests(unittest.TestCase):
    def test_append_only_and_auto_attempt(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "L.jsonl"
            ev1 = make_event("mechanical_check", check={"name": "c", "result": "pass"})
            ql.append_event(ledger, ev1)
            before = ledger.read_text(encoding="utf-8")
            ev2 = make_event("mechanical_check", check={"name": "c", "result": "fail"},
                             attempt=2)
            ql.append_event(ledger, ev2)
            after = ledger.read_text(encoding="utf-8")
            self.assertTrue(after.startswith(before))
            self.assertGreater(len(after.splitlines()), len(before.splitlines()))

    def test_latest_attempt_auto_number(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "L.jsonl"
            ql.append_event(ledger, make_event(
                "mechanical_check", workflow_id="workflow", run_id="run", step="step",
                attempt=3, check={"name": "c", "result": "pass"}))
            self.assertEqual(ql.latest_attempt(str(ledger), "workflow", "run", "step"), 3)
            self.assertEqual(ql.latest_attempt(str(ledger), "workflow", "run", "other"), 0)


class FromReportTests(unittest.TestCase):
    def test_from_report_mapping(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "L.jsonl"
            argv = ["check", "--ledger", str(ledger), "--workflow", "neon_parcel_longform",
                    "--run", "r1", "--step", "storyboard.scale",
                    "--from-report", str(HERE / "Fixture_Scale_Check_Report.json")]
            args = ql.build_parser().parse_args(argv)
            import contextlib as _c
            with _c.redirect_stdout(io.StringIO()):
                rc = ql.cmd_check(args)
            self.assertEqual(rc, 0)
            ev = ql.read_events(ledger)[0]
            self.assertEqual(ev["source"], "mechanical_check")
            self.assertEqual(ev["check"]["result"], "fail")
            self.assertIsNotNone(ev["check"].get("measured"))
            self.assertNotIn("director", ev)


class BackfillTests(unittest.TestCase):
    def test_backfill_dry_run(self):
        out = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = out
        try:
            argv = ["backfill-report-cards", str(HERE / "Fixture_Report_Card.md"),
                    "--workflow", "neon_parcel_longform"]
            rc = ql.main(argv)
        finally:
            sys.stdout = old_stdout
        self.assertEqual(rc, 0)
        text = out.getvalue()
        self.assertIn("B+", text)
        self.assertIn("director_judgment", text)

    def test_grade_requires_verbatim(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "L.jsonl"
            argv = ["grade", "--ledger", str(ledger), "--workflow", "wf", "--run", "r1",
                    "--step", "final", "--level", "final", "--grade", "B"]
            import contextlib as _c
            with _c.redirect_stdout(io.StringIO()), _c.redirect_stderr(io.StringIO()):
                rc = ql.main(argv)
            self.assertNotEqual(rc, 0)


def run_cli(argv):
    """Run the CLI quietly; return its exit code (argparse rejections included)."""
    import contextlib as _c
    with _c.redirect_stdout(io.StringIO()), _c.redirect_stderr(io.StringIO()):
        try:
            return ql.main(argv)
        except SystemExit as exc:  # argparse choices= rejection
            return exc.code


class FailureTypeTests(unittest.TestCase):
    def test_valid_failure_type_accepted(self):
        ev = make_event("mechanical_check", check={"name": "scale", "result": "fail"},
                        failure_type="scale")
        errors, _ = ql.validate_event(ev)
        self.assertEqual(errors, [])

    def test_invalid_failure_type_rejected(self):
        ev = make_event("mechanical_check", check={"name": "scale", "result": "fail"},
                        failure_type="van too big")
        errors, _ = ql.validate_event(ev)
        self.assertTrue(any("failure_type" in e for e in errors))
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "L.jsonl"
            with self.assertRaises(ValueError):
                ql.append_event(ledger, ev)
            self.assertFalse(ledger.exists())
            bad = Path(tmp) / "Bad.jsonl"
            bad.write_text(json.dumps(ev) + "\n", encoding="utf-8")
            self.assertEqual(run_cli(["validate", str(bad)]), 2)

    def test_failure_type_is_optional(self):
        ev = make_event("mechanical_check", check={"name": "c", "result": "fail"})
        self.assertNotIn("failure_type", ev)
        errors, _ = ql.validate_event(ev)
        self.assertEqual(errors, [])
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "L.jsonl"
            rc = run_cli(["check", "--ledger", str(ledger), "--workflow", "wf",
                          "--run", "r1", "--step", "s1", "--result", "fail"])
            self.assertEqual(rc, 0)
            self.assertNotIn("failure_type", ql.read_events(ledger)[0])

    def test_cli_check_and_self_correct_record_failure_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "L.jsonl"
            self.assertEqual(run_cli(
                ["check", "--ledger", str(ledger), "--workflow", "wf", "--run", "r1",
                 "--step", "storyboard", "--result", "fail",
                 "--failure-type", "continuity"]), 0)
            self.assertEqual(run_cli(
                ["self-correct", "--ledger", str(ledger), "--workflow", "wf",
                 "--run", "r1", "--step", "storyboard", "--reason", "kept bag in hand",
                 "--failure-type", "plausibility"]), 0)
            events = ql.read_events(ledger)
            self.assertEqual([e["failure_type"] for e in events],
                             ["continuity", "plausibility"])
            rows = [ql.flatten(e, ql.load_grade_scale()) for e in events]
            self.assertIn("failure_type", ql.EXPORT_COLUMNS)
            self.assertEqual(rows[0]["failure_type"], "continuity")

    def test_cli_rejects_unknown_failure_type_with_exit_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "L.jsonl"
            rc = run_cli(["check", "--ledger", str(ledger), "--workflow", "wf",
                          "--run", "r1", "--step", "s1", "--result", "fail",
                          "--failure-type", "wonky"])
            self.assertEqual(rc, 2)
            self.assertFalse(ledger.exists())


class DirectorEditTests(unittest.TestCase):
    def test_valid_director_edit(self):
        ev = make_event("director_edit", actor="Tony",
                        reason="repainted the hedge so it stops at the driveway",
                        artifact_path="Character_Sheets/POV_Panel_Final_Tony_Edit.png")
        errors, _ = ql.validate_event(ev)
        self.assertEqual(errors, [])

    def test_director_edit_actor_must_be_tony(self):
        ev = make_event("director_edit", actor="claude", reason="edited")
        errors, _ = ql.validate_event(ev)
        self.assertTrue(any("actor must be 'Tony'" in e for e in errors))

    def test_director_edit_needs_reason(self):
        ev = make_event("director_edit", actor="Tony", reason="  ")
        errors, _ = ql.validate_event(ev)
        self.assertTrue(any("non-empty reason" in e for e in errors))

    def test_director_edit_rejects_check_and_director(self):
        ev = make_event("director_edit", actor="Tony", reason="edited",
                        check={"name": "c", "result": "pass"},
                        director={"grade": "A", "verbatim": "A"})
        errors, _ = ql.validate_event(ev)
        self.assertTrue(any("must not have check" in e for e in errors))
        self.assertTrue(any("must not have director" in e for e in errors))

    def test_cli_edit_forces_tony_and_new_attempt(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "L.jsonl"
            ql.append_event(ledger, make_event(
                "mechanical_check", workflow_id="wf", run_id="r1", step="env.pov",
                attempt=4, check={"name": "c", "result": "fail"}))
            rc = run_cli(["edit", "--ledger", str(ledger), "--workflow", "wf",
                          "--run", "r1", "--step", "env.pov",
                          "--reason", "Tony fixed the hedge himself",
                          "--artifact", "POV_Panel_Final_Tony_Edit.png",
                          "--failure-type", "spatial_layout"])
            self.assertEqual(rc, 0)
            ev = ql.read_events(ledger)[-1]
            self.assertEqual((ev["source"], ev["actor"], ev["attempt"]),
                             ("director_edit", "Tony", 5))
            self.assertNotIn("check", ev)
            self.assertNotIn("director", ev)
            self.assertEqual(ev["artifact_path"], "POV_Panel_Final_Tony_Edit.png")
            self.assertEqual(ev["failure_type"], "spatial_layout")
            # Tony's edit explains the attempt going up: not an unexplained retry.
            events = ql.read_events(ledger)
            self.assertEqual(ql.unexplained(ql.collect_attempts(events), events), 0)

    def test_cli_edit_requires_reason(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "L.jsonl"
            rc = run_cli(["edit", "--ledger", str(ledger), "--workflow", "wf",
                          "--run", "r1", "--step", "s1"])
            self.assertNotEqual(rc, 0)
            rc = run_cli(["edit", "--ledger", str(ledger), "--workflow", "wf",
                          "--run", "r1", "--step", "s1", "--reason", "   "])
            self.assertEqual(rc, 2)
            self.assertFalse(ledger.exists())


def run_cli_capture(argv):
    """Run the CLI; return (exit code, stdout, stderr), argparse rejections included."""
    import contextlib as _c
    out, err = io.StringIO(), io.StringIO()
    with _c.redirect_stdout(out), _c.redirect_stderr(err):
        try:
            rc = ql.main(argv)
        except SystemExit as exc:
            rc = exc.code
    return rc, out.getvalue(), err.getvalue()


class StepActivityTests(unittest.TestCase):
    """Fix 1: step-level iteration pain shows up in report without touching the
    final-only readiness math."""

    def _fixture_plus_step_pain(self, tmp):
        ledger = Path(tmp) / "L.jsonl"
        ledger.write_text((HERE / "Fixture_Ledger_Valid.jsonl").read_text(encoding="utf-8"),
                          encoding="utf-8")
        common = {"workflow_id": "neon_parcel_longform", "run_id": "r-pain",
                  "step": "environment", "level": "step"}
        for attempt in (1, 2, 3):
            ql.append_event(ledger, make_event(
                "director_judgment", event_id=f"dj-{attempt}", actor="Tony",
                reason="", attempt=attempt,
                director={"decision": "redo", "verbatim": f"redo {attempt}"},
                **common))
            ql.append_event(ledger, make_event(
                "agent_self_correction", event_id=f"sc-{attempt}", actor="agent",
                attempt=attempt + 1, reason="fixed it", corrects_event_id=f"dj-{attempt}",
                **common))
        ql.append_event(ledger, make_event(
            "mechanical_check", event_id="mc-fail", attempt=4,
            check={"name": "c", "result": "fail"}, **common))
        ql.append_event(ledger, make_event(
            "mechanical_check", event_id="mc-err", attempt=4,
            check={"name": "c", "result": "error"}, **common))
        ql.append_event(ledger, make_event(
            "director_edit", event_id="ed-1", actor="Tony", attempt=5,
            reason="Tony fixed it himself", **common))
        return ledger

    def test_step_activity_counts_step_redos_without_changing_readiness(self):
        base = ql.compute_report(ql.read_events(HERE / "Fixture_Ledger_Valid.jsonl"),
                                 threshold=87, window=10, min_runs=3,
                                 grade_scale=ql.load_grade_scale())
        with tempfile.TemporaryDirectory() as tmp:
            ledger = self._fixture_plus_step_pain(tmp)
            rc, out, _ = run_cli_capture(["report", str(ledger), "--threshold", "87",
                                          "--json"])
            self.assertEqual(rc, 0)
            report = json.loads(out)
            # Existing --json shape is untouched (additive only).
            self.assertEqual(set(report), {"workflows", "steps", "step_activity"})
            n = report["workflows"]["neon_parcel_longform"]
            b = base["workflows"]["neon_parcel_longform"]
            for key in ("n", "mean", "ready", "why", "redo", "overridden_passes"):
                self.assertEqual(n[key], b[key], key)
            self.assertEqual((n["n"], n["mean"], n["ready"], n["redo"]),
                             (3, 88.0, True, 0))
            row = [r for r in report["step_activity"]
                   if (r["workflow_id"], r["step"]) == ("neon_parcel_longform",
                                                        "environment")][0]
            self.assertEqual(row, {
                "workflow_id": "neon_parcel_longform", "step": "environment",
                "max_attempt": 5, "redos": 3, "mech_fail": 1, "mech_error": 1,
                "self_corrections": 3, "director_edits": 1})
            # The fixture's own motoboy step: its C- was a sub_step "redo" that the
            # final-only workflow "redo" counter (0) never showed. Now it is visible.
            moto = [r for r in report["step_activity"]
                    if r["step"] == "character_sheet.motoboy"][0]
            self.assertEqual((moto["max_attempt"], moto["redos"], moto["mech_error"]),
                             (6, 1, 1))
            # Plain-text report shows the new section with the real numbers.
            rc, text, _ = run_cli_capture(["report", str(ledger), "--threshold", "87"])
            self.assertEqual(rc, 0)
            self.assertIn("step activity", text)
            self.assertIn("neon_parcel_longform / environment: max_attempt=5, redos=3",
                          text)
            rc, md, _ = run_cli_capture(["report", str(ledger), "--threshold", "87",
                                         "--markdown"])
            self.assertIn("### Step Activity", md)
            self.assertIn("| neon_parcel_longform | environment | 5 | 3 | 1 | 1 | 3 | 1 |",
                          md)


class GradeLevelRequiredTests(unittest.TestCase):
    """Fix 2: no silent default to final."""

    def test_grade_without_level_exits_2_with_clear_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "L.jsonl"
            rc, _, err = run_cli_capture(
                ["grade", "--ledger", str(ledger), "--workflow", "wf", "--run", "r1",
                 "--step", "environment", "--decision", "redo",
                 "--verbatim", "redo it"])
            self.assertEqual(rc, 2)
            self.assertIn("required", err)
            self.assertIn("--level", err)
            self.assertFalse(ledger.exists())

    def test_grade_with_explicit_step_level_is_not_a_final(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "L.jsonl"
            rc, _, _ = run_cli_capture(
                ["grade", "--ledger", str(ledger), "--workflow", "wf", "--run", "r1",
                 "--step", "environment", "--level", "step", "--decision", "redo",
                 "--verbatim", "redo it"])
            self.assertEqual(rc, 0)
            self.assertEqual(ql.read_events(ledger)[0]["level"], "step")


class SelfCorrectActorTests(unittest.TestCase):
    """Fix 3: a readable actor, not this script's filename."""

    def test_self_correct_actor_is_agent(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "L.jsonl"
            rc, _, _ = run_cli_capture(
                ["self-correct", "--ledger", str(ledger), "--workflow", "wf",
                 "--run", "r1", "--step", "s1", "--reason", "redid it"])
            self.assertEqual(rc, 0)
            actor = ql.read_events(ledger)[0]["actor"]
            self.assertNotEqual(actor, "quality_ledger.py")
            self.assertEqual(actor, "agent")


class CheckActorTests(unittest.TestCase):
    """A mechanical check names WHAT ran it: not this script, not "agent"."""

    def test_manual_check_actor(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "L.jsonl"
            rc, _, _ = run_cli_capture(
                ["check", "--ledger", str(ledger), "--workflow", "wf", "--run", "r1",
                 "--step", "s1", "--result", "fail"])
            self.assertEqual(rc, 0)
            actor = ql.read_events(ledger)[0]["actor"]
            self.assertNotEqual(actor, "quality_ledger.py")
            self.assertNotEqual(actor, "agent")
            self.assertEqual(actor, "mechanical_check")

    def test_from_report_actor(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "L.jsonl"
            common = ["check", "--ledger", str(ledger), "--workflow", "wf",
                      "--run", "r1", "--step", "storyboard.scale", "--from-report"]
            # the real checker's report has no tool field: its logical name is used
            self.assertEqual(run_cli_capture(
                common + [str(HERE / "Fixture_Scale_Check_Report.json")])[0], 0)
            # a report that names its own tool: that name is the actor
            named = Path(tmp) / "Named_Report.json"
            named.write_text(json.dumps({"passed": True, "tool": "check_hand_side"}))
            self.assertEqual(run_cli_capture(common + [str(named)])[0], 0)
            actors = [e["actor"] for e in ql.read_events(ledger)]
            self.assertEqual(actors, ["check_storyboard_scale", "check_hand_side"])


class BackdateTests(unittest.TestCase):
    """Fix 4: --at backdates check / grade / self-correct / edit; garbage rejected."""

    def test_at_sets_timestamp_on_all_four_writers(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "L.jsonl"
            common = ["--ledger", str(ledger), "--workflow", "wf", "--run", "r1",
                      "--step", "s1"]
            calls = [
                ["check", *common, "--result", "fail", "--at", "2026-09-19T00:47:00Z"],
                ["grade", *common, "--level", "step", "--decision", "redo",
                 "--verbatim", "redo", "--at", "2026-09-19T01:59:00+00:00"],
                ["self-correct", *common, "--reason", "fixed",
                 "--at", "2026-09-19T10:00:00-07:00"],  # converted to UTC
                ["edit", *common, "--reason", "Tony fixed it",
                 "--at", "2026-09-19T17:47:00Z"],
            ]
            for argv in calls:
                self.assertEqual(run_cli_capture(argv)[0], 0, argv[0])
            stamps = [e["timestamp"] for e in ql.read_events(ledger)]
            self.assertEqual(stamps, ["2026-09-19T00:47:00+00:00",
                                      "2026-09-19T01:59:00+00:00",
                                      "2026-09-19T17:00:00+00:00",
                                      "2026-09-19T17:47:00+00:00"])

    def test_no_at_still_uses_now(self):
        from datetime import datetime, timezone, timedelta
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "L.jsonl"
            run_cli_capture(["check", "--ledger", str(ledger), "--workflow", "wf",
                             "--run", "r1", "--step", "s1", "--result", "pass"])
            stamp = datetime.fromisoformat(ql.read_events(ledger)[0]["timestamp"])
            self.assertLess(abs(datetime.now(timezone.utc) - stamp), timedelta(minutes=1))

    def test_invalid_at_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "L.jsonl"
            for bad in ("garbage", "2026-13-45T99:00:00Z", "2026-09-19T17:47:00", ""):
                rc, _, err = run_cli_capture(
                    ["self-correct", "--ledger", str(ledger), "--workflow", "wf",
                     "--run", "r1", "--step", "s1", "--reason", "x", "--at", bad])
                self.assertEqual(rc, 2, bad)
                self.assertIn("--at", err)
            self.assertFalse(ledger.exists())


def final_judgment(event_id, run_id, ts, grade=None, decision=None, workflow="wf"):
    director = {"verbatim": f"{grade} {decision}"}
    if grade:
        director["grade"] = grade
    if decision:
        director["decision"] = decision
    return make_event("director_judgment", event_id=event_id, actor="Tony", reason="",
                      workflow_id=workflow, run_id=run_id, step="final", level="final",
                      timestamp=ts, director=director)


def write_lines(path, events):
    Path(path).write_text("".join(json.dumps(e) + "\n" for e in events), encoding="utf-8")


class CliInputHardeningTests(unittest.TestCase):
    """2026-10-06 bug hunt: CLI input that used to be written silently wrong."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ledger = Path(self.tmp.name) / "L.jsonl"
        self.common = ["--ledger", str(self.ledger), "--workflow", "wf", "--run", "r1",
                       "--step", "s1"]

    def tearDown(self):
        self.tmp.cleanup()

    def test_attempt_zero_and_negative_rejected(self):
        for bad in ("0", "-1", "1.5", "x"):
            rc, _, err = run_cli_capture(["check", *self.common, "--result", "pass",
                                          "--attempt", bad])
            self.assertEqual(rc, 2, bad)
            self.assertIn("--attempt", err)
        self.assertFalse(self.ledger.exists())

    def test_nan_and_inf_rejected(self):
        for flag, bad in (("--measured", "nan"), ("--threshold", "inf"),
                          ("--measured", "-inf")):
            rc, _, _ = run_cli_capture(["check", *self.common, "--result", "fail",
                                        flag, bad])
            self.assertEqual(rc, 2, bad)
        self.assertFalse(self.ledger.exists())
        ev = make_event("mechanical_check", check={"name": "c", "result": "fail",
                                                   "measured": float("nan")})
        self.assertTrue(any("number or null" in e for e in ql.validate_event(ev)[0]))

    def test_empty_identifiers_rejected(self):
        for flag in ("--workflow", "--run", "--step", "--ledger"):
            argv = ["check", *self.common, "--result", "pass"]
            argv[argv.index(flag) + 1] = "  "
            self.assertEqual(run_cli_capture(argv)[0], 2, flag)
        ev = make_event("mechanical_check", step="", check={"name": "c", "result": "pass"})
        self.assertTrue(any("step must be a non-empty string" in e
                            for e in ql.validate_event(ev)[0]))

    def test_grade_letter_case_is_normalized(self):
        rc, out, _ = run_cli_capture(["grade", *self.common, "--level", "step",
                                      "--grade", " b+ ", "--verbatim", "b+"])
        self.assertEqual(rc, 0)
        self.assertEqual(ql.read_events(self.ledger)[0]["director"]["grade"], "B+")
        self.assertIn("event_id", out)  # the id is printed so --corrects can use it

    def test_grade_needs_grade_or_decision(self):
        rc, _, err = run_cli_capture(["grade", *self.common, "--level", "step",
                                      "--verbatim", "hmm"])
        self.assertEqual(rc, 2)
        self.assertIn("--grade and/or --decision", err)

    def test_corrects_must_name_a_real_event(self):
        self.assertEqual(run_cli_capture(["check", *self.common, "--result", "fail",
                                          "--reason", "x"])[0], 0)
        real = ql.read_events(self.ledger)[0]["event_id"]
        for bad in ("", "no-such-id"):
            rc, _, _ = run_cli_capture(["self-correct", *self.common, "--reason", "fix",
                                        "--corrects", bad])
            self.assertEqual(rc, 2, bad)
            rc, _, _ = run_cli_capture(["edit", *self.common, "--reason", "fix",
                                        "--corrects", bad])
            self.assertEqual(rc, 2, bad)
        self.assertEqual(run_cli_capture(["self-correct", *self.common, "--reason", "fix",
                                          "--corrects", real])[0], 0)
        self.assertEqual(len(ql.read_events(self.ledger)), 2)

    def test_from_report_shapes(self):
        cases = {"list": [1, 2], "string_true": {"passed": "true"},
                 "null": {"passed": None}, "missing": {"failures": []}}
        for name, body in cases.items():
            report = Path(self.tmp.name) / f"{name}.json"
            report.write_text(json.dumps(body))
            rc, _, err = run_cli_capture(["check", *self.common, "--from-report",
                                          str(report)])
            self.assertEqual(rc, 2, name)
            self.assertNotIn("Traceback", err)
        named = Path(self.tmp.name) / "Bad_Name.json"
        named.write_text(json.dumps({"passed": True, "name": 5, "threshold": "x"}))
        self.assertEqual(run_cli_capture(["check", *self.common, "--from-report",
                                          str(named)])[0], 0)
        check = ql.read_events(self.ledger)[0]["check"]
        self.assertEqual(check["name"], "bad__name")
        self.assertNotIn("threshold", check)

    def test_from_report_refuses_conflicting_flags(self):
        report = Path(self.tmp.name) / "R.json"
        report.write_text(json.dumps({"passed": False}))
        rc, _, err = run_cli_capture(["check", *self.common, "--from-report", str(report),
                                      "--result", "pass"])
        self.assertEqual(rc, 2)
        self.assertIn("--result", err)
        self.assertFalse(self.ledger.exists())

    def test_ledger_never_creates_folders(self):
        ledger = Path(self.tmp.name) / "New_Folder" / "Sub" / "L.jsonl"
        rc, _, err = run_cli_capture(["check", "--ledger", str(ledger), "--workflow", "wf",
                                      "--run", "r", "--step", "s", "--result", "pass"])
        self.assertEqual(rc, 2)
        self.assertIn("does not exist", err)
        self.assertFalse((Path(self.tmp.name) / "New_Folder").exists())

    def test_at_out_of_range_or_future_rejected(self):
        for bad in ("0001-01-01T00:00:00+05:00", "9999-12-31T23:59:59-05:00",
                    "2999-01-01T00:00:00Z", "2026-02-30T00:00:00Z"):
            rc, _, err = run_cli_capture(["check", *self.common, "--result", "pass",
                                          "--at", bad])
            self.assertEqual(rc, 2, bad)
            self.assertNotIn("Traceback", err)
        self.assertFalse(self.ledger.exists())


class LedgerFileHardeningTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_append_after_a_line_with_no_newline(self):
        ledger = self.dir / "L.jsonl"
        first = make_event("mechanical_check", check={"name": "c", "result": "pass"})
        ledger.write_text(json.dumps(first), encoding="utf-8")  # no trailing newline
        ql.append_event(ledger, dict(first, event_id="ev-2"))
        self.assertEqual(run_cli(["validate", str(ledger)]), 0)
        self.assertEqual(len(ql.read_events(ledger)), 2)

    def test_bom_and_windows_line_endings_are_read(self):
        ev = final_judgment("e1", "r1", "2026-10-02T10:00:00+00:00", "B+", "accept")
        bom = self.dir / "Bom.jsonl"
        bom.write_bytes(b"\xef\xbb\xbf" + (json.dumps(ev) + "\r\n").encode())
        self.assertEqual(run_cli(["validate", str(bom)]), 0)
        self.assertEqual(run_cli(["report", str(bom)]), 0)

    def test_unicode_line_breaks_stay_on_one_line(self):
        ledger = self.dir / "L.jsonl"
        ql.append_event(ledger, final_judgment("e1", "r1", "2026-10-02T10:00:00+00:00",
                                               "B+", "accept") | {
            "director": {"grade": "B+", "verbatim": "line sep para\x85nel"}})
        text = ledger.read_text(encoding="utf-8")
        self.assertEqual(len(text.splitlines()), 1)
        self.assertEqual(ql.read_events(ledger)[0]["director"]["verbatim"],
                         "line sep para\x85nel")

    def test_concurrent_auto_attempts_are_unique(self):
        import subprocess
        ledger = self.dir / "L.jsonl"
        cmd = [sys.executable, str(HERE / "quality_ledger.py"), "check", "--ledger",
               str(ledger), "--workflow", "wf", "--run", "r", "--step", "s",
               "--result", "fail", "--reason", "x" * 5000]
        procs = [subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                 for _ in range(12)]
        for proc in procs:
            self.assertEqual(proc.wait(timeout=30), 0)
        attempts = sorted(e["attempt"] for e in ql.read_events(ledger))
        self.assertEqual(attempts, list(range(1, 13)))

    def test_validate_lists_every_bad_line_with_real_line_numbers(self):
        ledger = self.dir / "L.jsonl"
        good = make_event("mechanical_check", check={"name": "c", "result": "pass"})
        ledger.write_text("\n" + json.dumps(good) + "\nnot json\n\n"
                          + json.dumps(dict(good, event_id="ev-2", source="Mechanical_Check"))
                          + "\n", encoding="utf-8")
        rc, out, _ = run_cli_capture(["validate", str(ledger)])
        self.assertEqual(rc, 2)
        self.assertIn(f"{ledger}:3: not valid JSON", out)
        self.assertIn(f"{ledger}:5: source", out)

    def test_validate_type_rules(self):
        base = make_event("mechanical_check", check={"name": "c", "result": "pass"})
        bad = {
            "timestamp garbage": dict(base, timestamp="yesterday"),
            "timestamp no tz": dict(base, timestamp="2026-10-02T10:00:00"),
            "timestamp number": dict(base, timestamp=12345),
            "workflow None": dict(base, workflow_id=None),
            "cost string": dict(base, cost_usd="3.50"),
            "cost negative": dict(base, cost_usd=-1),
            "cost nan": dict(base, cost_usd=float("nan")),
            "corrects empty": dict(base, corrects_event_id=""),
            "check no name": dict(base, check={"result": "pass"}),
            "check unit number": dict(base, check={"name": "c", "result": "pass", "unit": 5}),
            "grade unhashable": make_event("director_judgment", actor="Tony",
                                           director={"grade": ["A"], "verbatim": "A"}),
            "failure_type list": dict(base, failure_type=["scale"]),
            "director empty verbatim": make_event(
                "director_judgment", actor="Tony", director={"grade": "A", "verbatim": ""}),
            "both check and director": dict(base, director={"grade": "A", "verbatim": "A"}),
            "source wrong case": dict(base, source="Mechanical_Check"),
            "edit with empty reason": make_event("director_edit", actor="Tony", reason=""),
        }
        for name, event in bad.items():
            errors, _ = ql.validate_event(event)
            self.assertTrue(errors, name)
        self.assertEqual(ql.validate_event(dict(base, cost_usd=0.42))[0], [])
        warn = ql.validate_event(make_event(
            "mechanical_check", reason="", check={"name": "c", "result": "fail"}))[1]
        self.assertTrue(any("empty reason" in w for w in warn))

    def test_duplicate_event_ids_and_same_ledger_twice(self):
        ledger = self.dir / "L.jsonl"
        write_lines(ledger, [final_judgment(f"g{i}", f"r{i}", f"2026-10-0{i + 1}T10:00:00+00:00",
                                            "A", "accept") for i in range(3)])
        rc, _, err = run_cli_capture(["report", str(ledger), str(ledger), "--json"])
        self.assertEqual(rc, 2)
        self.assertIn("listed twice", err)
        dup = self.dir / "Dup.jsonl"
        dup.write_text(ledger.read_text() * 2)
        self.assertEqual(run_cli(["validate", str(dup)]), 2)


class ReportHardeningTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_empty_ledger_says_so(self):
        empty = self.dir / "Empty.jsonl"
        empty.write_text("")
        rc, out, _ = run_cli_capture(["report", str(empty)])
        self.assertEqual(rc, 0)
        self.assertIn("no events", out)
        rc, out, _ = run_cli_capture(["report", str(empty), "--json"])
        self.assertEqual(json.loads(out), {"workflows": {}, "steps": [], "step_activity": []})

    def test_schema_invalid_lines_refused_without_traceback(self):
        bad = self.dir / "Bad.jsonl"
        write_lines(bad, [
            final_judgment("e1", "r1", "2026-10-02T10:00:00+00:00", "B+", "accept")
            | {"director": "B+"},
            final_judgment("e2", "r1", 12345, "B+", "accept") | {"workflow_id": None},
        ])
        for cmd in (["report", str(bad)], ["report", str(bad), "--json"],
                    ["export", str(bad)]):
            rc, _, err = run_cli_capture(cmd)
            self.assertEqual(rc, 2, cmd)
            self.assertNotIn("Traceback", err)
            self.assertIn("Bad.jsonl:1", err)

    def test_final_redo_without_a_grade_blocks_ready(self):
        ledger = self.dir / "L.jsonl"
        events = [final_judgment(f"g{i}", f"r{i}", f"2026-10-0{i + 1}T10:00:00+00:00",
                                 g, "accept") for i, g in enumerate(("B+", "A", "A-"))]
        write_lines(ledger, events)
        rc, out, _ = run_cli_capture(["report", str(ledger), "--json"])
        self.assertTrue(json.loads(out)["workflows"]["wf"]["ready"])
        events.append(final_judgment("redo1", "r9", "2026-10-05T10:00:00+00:00",
                                     None, "redo"))
        write_lines(ledger, events)
        rc, out, _ = run_cli_capture(["report", str(ledger), "--json"])
        w = json.loads(out)["workflows"]["wf"]
        self.assertEqual((w["ready"], w["redo"], w["n"]), (False, 1, 3))
        self.assertIn("recent redo=1", w["why"])

    def test_readiness_uses_the_exact_mean_not_the_rounded_one(self):
        scale = {"B+": 87, "Q": 86}
        events = [final_judgment(f"g{i}", f"r{i}", f"2026-10-01T10:{i:02d}:00+00:00",
                                 "B+", "accept") for i in range(29)]
        # no decision, so it is counted (an accepted below-bar grade is an override)
        events.append(final_judgment("q", "rq", "2026-10-01T11:00:00+00:00", "Q"))
        w = ql.compute_report(events, threshold=87, window=30, min_runs=3,
                              grade_scale=scale, max_recent_redo=0)["workflows"]["wf"]
        self.assertEqual(w["mean"], 87.0)  # 86.97 rounded for display
        self.assertFalse(w["ready"])
        self.assertIn("< threshold=87", w["why"])

    def test_events_sort_by_real_time_across_offsets(self):
        early = final_judgment("a", "r1", "2026-10-01T12:00:00+00:00", "B+", "accept")
        late = final_judgment("b", "r2", "2026-10-01T10:00:00-07:00", "A", "accept")  # 17:00Z
        self.assertEqual([e["event_id"] for e in ql._by_time([late, early])], ["a", "b"])

    def test_report_rejects_bad_window_and_threshold(self):
        ledger = self.dir / "L.jsonl"
        ledger.write_text("")
        for flags in (["--window", "0"], ["--window", "-3"], ["--min-runs", "-1"],
                      ["--threshold", "101"], ["--threshold", "abc"]):
            self.assertEqual(run_cli(["report", str(ledger), *flags]), 2, flags)

    def test_markdown_escapes_pipes_in_step_names(self):
        ev = make_event("mechanical_check", step="a|b", check={"name": "c", "result": "pass"})
        report = ql.compute_report([ev], 87, 10, 3, ql.load_grade_scale(), 0)
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ql.print_report_text(report, markdown=True)
        self.assertIn("| a\\|b |", buf.getvalue())


class BackfillHardeningTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.scale = ql.load_grade_scale()

    def tearDown(self):
        self.tmp.cleanup()

    def grade_of(self, text):
        return ql.read_report_card_grade(text, self.scale)

    def test_blank_grade_never_borrows_the_next_line(self):
        self.assertEqual(self.grade_of("**Grade:**\n\nA compilation of clips.\n"),
                         (None, None))
        self.assertEqual(self.grade_of("Grade:\nA compilation\n"), (None, None))

    def test_ungraded_card_never_falls_through_to_a_section_grade(self):
        text = "**Grade:** TBD\n\n## Thumbnail\n\n**Grade: A**\n"
        self.assertEqual(self.grade_of(text), (None, None))
        grade, problem = self.grade_of("**Grade:** Excellent\n\n**Grade: A**\n")
        self.assertIsNone(grade)
        self.assertIn("Excellent", problem)

    def test_label_must_start_the_line(self):
        self.assertEqual(self.grade_of("Re-Grade: A\n**Grade:** C\n"), ("C", None))
        self.assertEqual(self.grade_of("Upgrade: A plan\n"), (None, None))

    def test_real_report_card_formats(self):
        cases = {
            "**Grade:** B\n": "B",
            "**Grade: A**\n": "A",
            "**Grade: B+ (Tony, 2026-09-22). APPROVED, FINAL.**\n": "B+",
            "**Grade: C — passes.**\n": "C",
            "**Grade:** B+ (video v7, 2026-09-20).\n": "B+",
            "- **Grade:** A-\n": "A-",
            "| Field | Value |\n|---|---|\n| Grade | B+ |\n": "B+",
            "**Grade:** b+\n": "B+",
            "---\nGrade: \"B+\"\n---\n# Card\n": "B+",
            "---\nGrade: B+ (Tony)\n---\n# Card\n": "B+",
            "﻿---\nGrade: A-\n---\n": "A-",
        }
        for text, want in cases.items():
            self.assertEqual(self.grade_of(text), (want, None), text)

    def test_unclear_grades_are_refused(self):
        for text in ("**Grade:** E\n", "**Grade:** B+/A-\n", "**Grade:** D+\n",
                     "**Grade:** a work in progress\n"):
            grade, problem = self.grade_of(text)
            self.assertIsNone(grade, text)
            self.assertTrue(problem, text)

    def test_frontmatter_and_body_must_agree(self):
        grade, problem = self.grade_of("---\nGrade: B+\n---\n**Grade:** A\n")
        self.assertIsNone(grade)
        self.assertIn("disagrees", problem)
        self.assertEqual(self.grade_of("---\nGrade: B+\n---\n**Grade:** B+\n"), ("B+", None))

    def test_missing_card_does_not_stop_the_batch(self):
        card = self.dir / "P1" / "Data"
        card.mkdir(parents=True)
        (card / "Report_Card.md").write_text("**Grade:** A\n")
        rc, out, err = run_cli_capture(["backfill-report-cards", str(self.dir / "nope.md"),
                                        str(card / "Report_Card.md"), "--workflow", "wf"])
        self.assertEqual(rc, 2)
        self.assertIn("nope.md", err)
        self.assertIn('"run_id": "P1"', out)

    def test_backfill_is_idempotent(self):
        card = self.dir / "P1" / "Data"
        card.mkdir(parents=True)
        (card / "Report_Card.md").write_text("**Grade:** A\n")
        ledger = self.dir / "L.jsonl"
        argv = ["backfill-report-cards", str(card / "Report_Card.md"), "--workflow", "wf",
                "--ledger", str(ledger)]
        self.assertEqual(run_cli(argv), 0)
        rc, out, _ = run_cli_capture(argv)
        self.assertEqual(rc, 0)
        self.assertIn("already backfilled", out)
        self.assertEqual(len(ql.read_events(ledger)), 1)


class PendingClearTests(unittest.TestCase):
    def test_pending_lists_words_and_clears(self):
        import os
        with tempfile.TemporaryDirectory() as tmp:
            old = os.environ.get("QUALITY_LEDGER_TMP")
            os.environ["QUALITY_LEDGER_TMP"] = tmp
            try:
                ql.write_marker(ql.marker_path("s1"), {"run_id": "r1", "pending": [
                    {"kind": "grade", "step": "final", "verbatim": "Plan B for later",
                     "problem": "x"}]})
                rc, out, _ = run_cli_capture(["pending", "--session", "s1"])
                self.assertIn("Plan B for later", out)
                rc, out, _ = run_cli_capture(["pending", "--session", "s1", "--clear"])
                self.assertIn("cleared 1", out)
                rc, out, _ = run_cli_capture(["pending", "--session", "s1"])
                self.assertIn("no pending items", out)
                self.assertEqual(ql.marker_path("../../x").parent, Path(tmp))
            finally:
                if old is None:
                    os.environ.pop("QUALITY_LEDGER_TMP", None)
                else:
                    os.environ["QUALITY_LEDGER_TMP"] = old


class LatestFinalPerRunTests(unittest.TestCase):
    """Tony, 2026-10-06 (decision 1): only the latest final grade of a run counts
    toward readiness; the earlier ones stay in the ledger and export."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ledger = Path(self.tmp.name) / "L.jsonl"

    def tearDown(self):
        self.tmp.cleanup()

    def _report(self, events, **kw):
        write_lines(self.ledger, events)
        args = ["report", str(self.ledger), "--json"]
        for key, value in kw.items():
            args += [f"--{key.replace('_', '-')}", str(value)]
        rc, out, err = run_cli_capture(args)
        self.assertEqual(rc, 0, err)
        return json.loads(out)

    def test_redo_then_accept_counts_only_the_accept(self):
        events = [
            final_judgment("r1-c", "r1", "2026-10-01T10:00:00+00:00", "C", "redo"),
            final_judgment("r2-b", "r2", "2026-10-01T11:00:00+00:00", "B+", "accept"),
            final_judgment("r3-a", "r3", "2026-10-01T12:00:00+00:00", "A-", "accept"),
            final_judgment("r1-a", "r1", "2026-10-01T13:00:00+00:00", "A", "accept"),
        ]
        w = self._report(events)["workflows"]["wf"]
        # Before: the stale "C, redo" kept recent redo=1 -> NOT READY.
        self.assertEqual((w["n"], w["mean"], w["redo"], w["ready"]), (3, 90.0, 0, True))

    def test_earlier_plain_grade_is_not_averaged_in(self):
        events = [
            final_judgment("r1-c", "r1", "2026-10-01T10:00:00+00:00", "C"),
            final_judgment("r1-a", "r1", "2026-10-01T13:00:00+00:00", "A", "accept"),
            final_judgment("r2-b", "r2", "2026-10-01T11:00:00+00:00", "B+", "accept"),
            final_judgment("r3-a", "r3", "2026-10-01T12:00:00+00:00", "A-", "accept"),
        ]
        w = self._report(events)["workflows"]["wf"]
        # Before: n=4, mean=(73+93+87+90)/4=85.75 -> NOT READY. Now the C is superseded.
        self.assertEqual((w["n"], w["mean"], w["ready"]), (3, 90.0, True))

    def test_superseded_grade_stays_in_the_file_export_and_steps(self):
        events = [
            final_judgment("r1-c", "r1", "2026-10-01T10:00:00+00:00", "C", "redo"),
            final_judgment("r1-a", "r1", "2026-10-01T13:00:00+00:00", "A", "accept"),
        ]
        report = self._report(events)
        raw_ids = [json.loads(line)["event_id"]
                   for line in self.ledger.read_text().splitlines()]
        self.assertEqual(raw_ids, ["r1-c", "r1-a"])
        rc, out, _ = run_cli_capture(["export", str(self.ledger), "--format", "jsonl"])
        self.assertEqual(rc, 0)
        rows = [json.loads(line) for line in out.splitlines()]
        self.assertEqual([(r["event_id"], r["director_grade"], r["director_decision"])
                          for r in rows], [("r1-c", "C", "redo"), ("r1-a", "A", "accept")])
        step = report["steps"][0]
        self.assertEqual((step["first_grade"], step["latest_grade"]), ("C", "A"))
        # step_activity is step-level visibility, not final grades: the superseded
        # redo is still shown there, unchanged by this rule.
        self.assertEqual(report["step_activity"][0]["redos"], 1)

    def test_override_rule_applies_to_the_latest_final_only(self):
        base = [
            final_judgment("r2-b", "r2", "2026-10-01T11:00:00+00:00", "B+", "accept"),
            final_judgment("r3-a", "r3", "2026-10-01T12:00:00+00:00", "A-", "accept"),
        ]
        # C redo, then Tony ships it at C+ anyway: the latest is an override.
        w = self._report(base + [
            final_judgment("r1-c", "r1", "2026-10-01T10:00:00+00:00", "C", "redo"),
            final_judgment("r1-cp", "r1", "2026-10-01T13:00:00+00:00", "C+",
                           "accept_with_flaws"),
        ])["workflows"]["wf"]
        self.assertEqual((w["n"], w["mean"], w["redo"], w["overridden_passes"]),
                         (2, 88.5, 0, 1))
        # Override first, then a fixed run graded A: the earlier override is
        # superseded too, and the A counts.
        w = self._report(base + [
            final_judgment("r1-cp", "r1", "2026-10-01T10:00:00+00:00", "C+",
                           "accept_with_flaws"),
            final_judgment("r1-a", "r1", "2026-10-01T13:00:00+00:00", "A", "accept"),
        ])["workflows"]["wf"]
        self.assertEqual((w["n"], w["mean"], w["overridden_passes"], w["ready"]),
                         (3, 90.0, 0, True))
        # A later gradeless "redo" still supersedes an accepted grade.
        w = self._report(base + [
            final_judgment("r1-a", "r1", "2026-10-01T10:00:00+00:00", "A", "accept"),
            final_judgment("r1-redo", "r1", "2026-10-01T13:00:00+00:00", None, "redo"),
        ])["workflows"]["wf"]
        self.assertEqual((w["n"], w["redo"], w["ready"]), (2, 1, False))

    def test_latest_is_by_timestamp_then_file_order(self):
        # A backdated line written later loses to a newer timestamp written earlier.
        events = [
            final_judgment("new", "r1", "2026-10-01T13:00:00+00:00", "A", "accept"),
            final_judgment("old", "r1", "2026-10-01T10:00:00+00:00", "C"),
        ]
        latest = ql.latest_final_per_run(events)
        self.assertEqual([e["event_id"] for e in latest], ["new"])
        # Same timestamp: the later line in the file wins.
        same = "2026-10-01T10:00:00+00:00"
        events = [final_judgment("first", "r1", same, "C"),
                  final_judgment("second", "r1", same, "A", "accept")]
        self.assertEqual([e["event_id"] for e in ql.latest_final_per_run(events)],
                         ["second"])
        events.reverse()
        self.assertEqual([e["event_id"] for e in ql.latest_final_per_run(events)],
                         ["first"])

    def test_window_means_most_recent_runs(self):
        events = [
            final_judgment("r2", "r2", "2026-10-01T02:00:00+00:00", "B+", "accept"),
            final_judgment("r3", "r3", "2026-10-01T03:00:00+00:00", "A", "accept"),
            final_judgment("r1-am", "r1", "2026-10-01T04:00:00+00:00", "A-", "accept"),
            final_judgment("r1-ap", "r1", "2026-10-01T05:00:00+00:00", "A+", "accept"),
        ]
        w = self._report(events, window=2, min_runs=2)["workflows"]["wf"]
        # Two most recent RUNS: r3 (A 93) and r1's latest (A+ 97). Counting grade
        # lines instead would have taken r1's A- and A+ (mean 93.5).
        self.assertEqual((w["n"], w["mean"]), (2, 95.0))

    def test_gradeless_accept_does_not_supersede(self):
        # A decision-only accept is not a grade (a bare approval never is): the
        # run's latest readiness final is still the earlier graded one.
        events = [
            final_judgment("r1-a", "r1", "2026-10-01T10:00:00+00:00", "A", "accept"),
            final_judgment("r1-ok", "r1", "2026-10-01T13:00:00+00:00", None, "accept"),
        ]
        self.assertEqual([e["event_id"] for e in ql.latest_final_per_run(events)],
                         ["r1-a"])


class SameArtifactAttemptTests(unittest.TestCase):
    """Tony, 2026-10-06 (decision 2): checks on the same generated output share one
    attempt; only a regenerated output is a new attempt."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.ledger = self.dir / "L.jsonl"
        self.common = ["--ledger", str(self.ledger), "--workflow", "wf", "--run", "r1",
                       "--step", "storyboard"]

    def tearDown(self):
        self.tmp.cleanup()

    def _check(self, *extra, name="c", result="pass"):
        rc, out, err = run_cli_capture(["check", *self.common, "--name", name,
                                        "--result", result, *extra])
        return rc, err

    def _attempts(self):
        return [e["attempt"] for e in ql.read_events(self.ledger)]

    def test_same_artifact_shares_new_artifact_bumps(self):
        v1 = self.dir / "Storyboard_v1.png"
        v1.write_bytes(b"first render")
        self.assertEqual(self._check("--artifact", str(v1), name="scale",
                                     result="fail")[0], 0)
        self.assertEqual(self._check("--artifact-path", str(v1), name="hand_check",
                                     result="fail")[0], 0)
        self.assertEqual(self._attempts(), [1, 1])
        sha = ql.file_sha256(v1)
        self.assertEqual({e["artifact_sha256"] for e in ql.read_events(self.ledger)},
                         {sha})
        # A regenerated output (new file) is a real new attempt.
        v2 = self.dir / "Storyboard_v2.png"
        v2.write_bytes(b"second render")
        self.assertEqual(self._check("--artifact", str(v2), name="scale")[0], 0)
        self.assertEqual(self._check("--artifact", str(v2), name="hand_check")[0], 0)
        self.assertEqual(self._attempts(), [1, 1, 2, 2])
        # Regenerated IN PLACE (same file name, new bytes): still a new attempt.
        v2.write_bytes(b"third render")
        self.assertEqual(self._check("--artifact", str(v2), name="scale")[0], 0)
        self.assertEqual(self._attempts()[-1], 3)
        # Re-checking an OLDER output never reuses an old number: new attempt.
        self.assertEqual(self._check("--artifact", str(v1), name="scale")[0], 0)
        self.assertEqual(self._attempts()[-1], 4)
        # step_activity and unexplained retries now follow regenerations, not checks.
        events = ql.read_events(self.ledger)
        row = ql.compute_step_activity(events)[0]
        self.assertEqual((row["max_attempt"], row["mech_fail"]), (4, 2))

    def test_two_checks_on_one_image_are_not_an_unexplained_retry(self):
        image = self.dir / "Panel.png"
        image.write_bytes(b"pixels")
        self._check("--artifact", str(image), name="scale")
        self._check("--artifact", str(image), name="hand_check")
        events = ql.read_events(self.ledger)
        self.assertEqual(ql.unexplained(ql.collect_attempts(events), events), 0)
        self.assertEqual(ql.compute_step_activity(events)[0]["max_attempt"], 1)

    def test_no_artifact_is_its_own_attempt(self):
        rc, err = self._check(name="scale")
        self.assertEqual(rc, 0)
        self.assertIn("counts as its own attempt", err)
        self._check(name="hand_check")
        self.assertEqual(self._attempts(), [1, 2])
        events = ql.read_events(self.ledger)
        self.assertNotIn("artifact_sha256", events[0])
        # One check with a file after a check with none: no evidence they match.
        image = self.dir / "Panel.png"
        image.write_bytes(b"pixels")
        self._check("--artifact", str(image), name="scale")
        self.assertEqual(self._attempts(), [1, 2, 3])

    def test_unreadable_artifact_is_refused(self):
        for bad in (str(self.dir / "Missing.png"), str(self.dir)):
            rc, err = self._check("--artifact", bad)
            self.assertEqual(rc, 2, bad)
            self.assertIn("cannot read", err)
        self.assertFalse(self.ledger.exists())

    def test_explicit_attempt_still_wins(self):
        image = self.dir / "Panel.png"
        image.write_bytes(b"pixels")
        self._check("--artifact", str(image))
        self._check("--artifact", str(image), "--attempt", "7")
        self.assertEqual(self._attempts(), [1, 7])

    def test_from_report_fingerprint_matches_a_manual_check(self):
        image = self.dir / "Storyboard_Clip2_v1.png"
        image.write_bytes(b"storyboard pixels")
        sha = ql.file_sha256(image)
        report = self.dir / "Scale_Check_Storyboard_Clip2_v1.json"
        report.write_text(json.dumps({"storyboard": image.name, "storyboard_sha256": sha,
                                      "passed": False,
                                      "failures": ["van is 210px (+70% too big)"]}))
        rc, _, err = run_cli_capture(["check", *self.common, "--from-report", str(report)])
        self.assertEqual(rc, 0, err)
        self._check("--artifact", str(image), name="hand_check")
        events = ql.read_events(self.ledger)
        self.assertEqual([e["attempt"] for e in events], [1, 1])
        self.assertEqual((events[0]["artifact_path"], events[0]["artifact_sha256"]),
                         (image.name, sha))
        # --artifact that is not the file the report measured is refused.
        other = self.dir / "Other.png"
        other.write_bytes(b"something else")
        rc, _, err = run_cli_capture(["check", *self.common, "--from-report", str(report),
                                      "--artifact", str(other)])
        self.assertEqual(rc, 2)
        self.assertIn("not the file the report measured", err)
        # The placeholder all-zero hash in the fixture is not a fingerprint.
        rc, _, _ = run_cli_capture(["check", *self.common, "--from-report",
                                    str(HERE / "Fixture_Scale_Check_Report.json")])
        self.assertEqual(rc, 0)
        self.assertNotIn("artifact_sha256", ql.read_events(self.ledger)[-1])

    def test_check_on_tonys_edited_file_shares_his_attempt(self):
        self._check(name="scale", result="fail")
        edited = self.dir / "POV_Panel_Final_Tony_Edit.png"
        edited.write_bytes(b"tony's pixels")
        rc, _, err = run_cli_capture(["edit", *self.common, "--reason", "Tony fixed it",
                                      "--artifact", str(edited)])
        self.assertEqual(rc, 0, err)
        self._check("--artifact", str(edited), name="scale")
        self.assertEqual(self._attempts(), [1, 2, 2])

    def test_concurrent_checks_on_one_file_share_one_attempt(self):
        import subprocess
        image = self.dir / "Panel.png"
        image.write_bytes(b"pixels")
        cmd = [sys.executable, str(HERE / "quality_ledger.py"), "check", *self.common,
               "--result", "pass", "--artifact", str(image)]
        procs = [subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                 for _ in range(8)]
        for proc in procs:
            self.assertEqual(proc.wait(timeout=30), 0)
        self.assertEqual(self._attempts(), [1] * 8)


if __name__ == "__main__":
    unittest.main()
