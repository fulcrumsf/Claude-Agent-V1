"""Offline unittest suite for ledger_hook.py (stdlib only, no network)."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import ledger_hook as lh  # noqa: E402
import quality_ledger as ql  # noqa: E402


class _TmpEnv(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old_tmp = os.environ.get("QUALITY_LEDGER_TMP")
        self.old_test = os.environ.get("QUALITY_LEDGER_TEST")
        os.environ["QUALITY_LEDGER_TMP"] = self.tmp.name
        os.environ["QUALITY_LEDGER_TEST"] = "1"

    def tearDown(self):
        if self.old_tmp is None:
            os.environ.pop("QUALITY_LEDGER_TMP", None)
        else:
            os.environ["QUALITY_LEDGER_TMP"] = self.old_tmp
        if self.old_test is None:
            os.environ.pop("QUALITY_LEDGER_TEST", None)
        else:
            os.environ["QUALITY_LEDGER_TEST"] = self.old_test
        self.tmp.cleanup()


def payload(hook_event_name, prompt=None, tool=None, session="fixture-session"):
    p = {
        "session_id": session,
        "hook_event_name": hook_event_name,
        "cwd": "/Users/tonymacbook2025/Documents/Agent-OS",
    }
    if prompt is not None:
        p["prompt"] = prompt
    if tool is not None:
        p["tool_name"] = "Skill"
        p["tool_input"] = {"skill": tool}
    return p


class HookFlowTests(_TmpEnv):
    def test_no_marker_means_no_output(self):
        out = lh.run(payload("UserPromptSubmit",
                             prompt="honestly that one is a B+"), "claude", "prompt")
        self.assertEqual(out, "")

    def test_skill_starts_a_ledger(self):
        out = lh.run(payload("PostToolUse", tool="Neon_Parcel_Longform_Compilation_v2"),
                     "claude", "skill")
        self.assertIn("Quality Ledger", out)
        for cmd in ("check", "self-correct", "grade", "edit"):
            self.assertIn(f"quality_ledger.py {cmd} --ledger", out)
        marker = lh.load_marker("fixture-session")
        self.assertIsNotNone(marker)
        self.assertEqual(marker["workflow_id"], "neon_parcel_longform")
        self.assertTrue(marker["ledger_path"].endswith("Quality_Ledger.jsonl"))

    def test_grade_shorthand_writes_director_event(self):
        lh.run(payload("PostToolUse", tool="Neon_Parcel_Longform_Compilation_v2"),
               "claude", "skill")
        lh.run(payload("UserPromptSubmit",
                       prompt="grade: B+ accept step=final attempt=1 movement reads right"),
               "claude", "prompt")
        ledger = Path(lh.load_marker("fixture-session")["ledger_path"])
        events = ql.read_events(ledger)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["source"], "director_judgment")
        self.assertEqual(events[0]["actor"], "Tony")
        self.assertEqual(events[0]["director"]["grade"], "B+")

    def test_plain_grade_creates_pending_not_event(self):
        lh.run(payload("PostToolUse", tool="Neon_Parcel_Longform_Compilation_v2"),
               "claude", "skill")
        out = lh.run(payload("UserPromptSubmit",
                             prompt="honestly that one is a B+"), "claude", "prompt")
        self.assertIn("Quality Ledger", out)
        ledger = lh.load_marker("fixture-session")["ledger_path"]
        self.assertFalse(Path(ledger).exists())
        marker = lh.load_marker("fixture-session")
        self.assertEqual(len(marker["pending"]), 1)

    def test_bare_approved_reminds_for_score(self):
        lh.run(payload("PostToolUse", tool="Neon_Parcel_Longform_Compilation_v2"),
               "claude", "skill")
        out = lh.run(payload("UserPromptSubmit", prompt="approved"),
                     "claude", "prompt")
        self.assertIn("87", out)
        ledger = lh.load_marker("fixture-session")["ledger_path"]
        self.assertFalse(Path(ledger).exists())

    def test_stop_asks_for_pending_grade(self):
        lh.run(payload("PostToolUse", tool="Neon_Parcel_Longform_Compilation_v2"),
               "claude", "skill")
        lh.run(payload("UserPromptSubmit", prompt="honestly that one is a B+"),
               "claude", "prompt")
        out = lh.run(payload("Stop"), "claude", "stop")
        self.assertIn("pending", out)

    def test_malformed_input_fails_open(self):
        self.assertEqual(lh.run({"not": "a valid payload"}, "claude", "prompt"), "")
        self.assertEqual(lh.run(None, "claude", "prompt"), "")


class HookProcessTests(_TmpEnv):
    """Run the real entry point via stdin, as a harness does."""

    def _run(self, stdin, *args):
        import subprocess
        import time
        start = time.time()
        proc = subprocess.run([sys.executable, str(HERE / "ledger_hook.py"), *args],
                              input=stdin, capture_output=True, text=True, timeout=10)
        return proc, time.time() - start

    def test_malformed_stdin_exits_0_under_1s(self):
        proc, secs = self._run("not json {", "--harness", "claude", "--event", "prompt")
        self.assertEqual((proc.returncode, proc.stdout), (0, ""))
        self.assertLess(secs, 1.0)

    def test_stop_with_pending_exits_0_and_asks_tony(self):
        lh.run(payload("PostToolUse", tool="Neon_Parcel_Longform_Compilation_v2"),
               "claude", "skill")
        lh.run(payload("UserPromptSubmit", prompt="honestly that one is a B+"),
               "claude", "prompt")
        proc, secs = self._run(json.dumps(payload("Stop")), "--event", "stop")
        self.assertEqual(proc.returncode, 0)
        self.assertLess(secs, 1.0)
        out = json.loads(proc.stdout)
        self.assertIn("What grade do you give it", out["systemMessage"])
        self.assertIn("pending", out["reason"])
        blocked, _ = self._run(json.dumps(payload("Stop")), "--event", "stop", "--block")
        self.assertEqual(blocked.returncode, 2)

    def test_recorded_grade_clears_pending(self):
        lh.run(payload("PostToolUse", tool="Neon_Parcel_Longform_Compilation_v2"),
               "claude", "skill")
        lh.run(payload("UserPromptSubmit", prompt="honestly that one is a B+"),
               "claude", "prompt")
        lh.run(payload("UserPromptSubmit", prompt="grade: B+ accept step=final ok"),
               "claude", "prompt")
        self.assertEqual(lh.run(payload("Stop"), "claude", "stop"), "")


class ShorthandMissingStepTests(_TmpEnv):
    """A grade: shorthand with no step= is never silently written as a final grade."""

    def _start(self):
        lh.run(payload("PostToolUse", tool="Neon_Parcel_Longform_Compilation_v2"),
               "claude", "skill")
        return Path(lh.load_marker("fixture-session")["ledger_path"])

    def test_missing_step_is_pending_not_written(self):
        ledger = self._start()
        out = lh.run(payload("UserPromptSubmit",
                             prompt="grade: B+ accept too stiff"), "claude", "prompt")
        self.assertIn("no `step=`", out)
        self.assertFalse(ledger.exists())  # nothing written, least of all a final
        pending = lh.load_marker("fixture-session")["pending"]
        self.assertEqual(len(pending), 1)
        self.assertTrue(pending[0]["needs_step"])
        self.assertEqual(pending[0]["grade"], "B+")
        self.assertEqual(pending[0]["verbatim"], "grade: B+ accept too stiff")
        self.assertIn("pending grade", lh.run(payload("Stop"), "claude", "stop"))

    def test_resend_with_step_writes_and_clears_pending(self):
        ledger = self._start()
        lh.run(payload("UserPromptSubmit", prompt="grade: redo too stiff"),
               "claude", "prompt")
        lh.run(payload("UserPromptSubmit", prompt=(
            "grade: B+ accept step=character_sheet.motoboy attempt=6 too stiff")),
            "claude", "prompt")
        events = ql.read_events(ledger)
        self.assertEqual(len(events), 1)
        self.assertEqual((events[0]["step"], events[0]["level"], events[0]["attempt"]),
                         ("character_sheet.motoboy", "sub_step", 6))
        self.assertEqual(lh.load_marker("fixture-session")["pending"], [])
        self.assertEqual(lh.run(payload("Stop"), "claude", "stop"), "")

    def test_step_present_path_unchanged(self):
        ledger = self._start()
        lh.run(payload("UserPromptSubmit", prompt="grade: A accept step=final great"),
               "claude", "prompt")
        lh.run(payload("UserPromptSubmit", prompt="grade: C+ redo step=environment"),
               "claude", "prompt")
        levels = [(e["step"], e["level"]) for e in ql.read_events(ledger)]
        self.assertEqual(levels, [("final", "final"), ("environment", "step")])


class ShorthandParseTests(unittest.TestCase):
    def test_parse_shorthand_no_step_is_none(self):
        self.assertIsNone(lh.parse_shorthand("grade: B+ accept too stiff")["step"])

    def test_no_false_positive_grades(self):
        self.assertIsNone(lh.parse_shorthand("grade: redo Car too big")["grade"])
        self.assertIsNone(lh.parse_shorthand("grade: redo the Dog looks off")["grade"])
        self.assertIsNone(lh.parse_shorthand("grade: accept Also nice")["grade"])
        self.assertEqual(lh.parse_shorthand("grade: A- accept")["grade"], "A-")
        self.assertIsNone(lh.detect_signal("A van drove past the harbour"))
        self.assertEqual(lh.detect_signal("that's an A, great")["grade"], "A")

    def test_codex_skill_md_read_is_a_skill(self):
        self.assertEqual(lh.extract_skill({"tool_name": "Read", "tool_input": {
            "file_path": "/x/Skills/Neon_Parcel_Longform_Compilation_v2/SKILL.md"}}),
            "Neon_Parcel_Longform_Compilation_v2")

    def test_parse_shorthand(self):
        got = lh.parse_shorthand("grade: B+ accept step=final attempt=6 nice")
        self.assertEqual(got["grade"], "B+")
        self.assertEqual(got["decision"], "accept")
        self.assertEqual(got["step"], "final")
        self.assertEqual(got["attempt"], 6)
        self.assertIsNone(lh.parse_shorthand("not a grade"))
        self.assertIsNone(lh.parse_shorthand("honestly that one is a B+"))


class BareGradeTests(_TmpEnv):
    """2026-10-06 bug hunt: a bare capital grade with no decision word was dropped
    (no event, no reminder), and "grade: A accept" kept the accept but lost the A."""

    def _start(self):
        lh.run(payload("PostToolUse", tool="Neon_Parcel_Longform_Compilation_v2"),
               "claude", "skill")
        return Path(lh.load_marker("fixture-session")["ledger_path"])

    def _say(self, text):
        return lh.run(payload("UserPromptSubmit", prompt=text), "claude", "prompt")

    def test_bare_a_is_recorded(self):
        self.assertEqual(lh.parse_shorthand("grade: A step=final")["grade"], "A")
        ledger = self._start()
        out = self._say("grade: A step=final")
        self.assertIn("recorded", out)
        director = ql.read_events(ledger)[0]["director"]
        self.assertEqual(director.get("grade"), "A")
        self.assertNotIn("decision", director)

    def test_a_with_decision_keeps_the_grade(self):
        ledger = self._start()
        self._say("grade: A accept step=final great")
        director = ql.read_events(ledger)[0]["director"]
        self.assertEqual((director.get("grade"), director.get("decision")), ("A", "accept"))

    def test_every_scale_grade_alone_and_in_any_case(self):
        for grade in ql.load_grade_scale():
            for typed in (grade, grade.lower()):
                if typed == "a":
                    continue  # lowercase bare "a" alone is covered below
                got = lh.parse_shorthand(f"grade: {typed} step=final")
                self.assertEqual((got["grade"], got["problems"]), (grade, []), typed)
        self.assertEqual(lh.parse_shorthand("grade: a step=final")["grade"], "A")
        self.assertEqual(lh.parse_shorthand("Grade: b- redo step=x")["grade"], "B-")
        self.assertEqual(lh.parse_shorthand("grade: B plus accept step=x")["grade"], "B+")
        self.assertEqual(lh.parse_shorthand("grade:A step=final")["grade"], "A")
        self.assertEqual(lh.parse_shorthand("grade: A, step=final")["grade"], "A")

    def test_article_a_is_never_a_grade(self):
        got = lh.parse_shorthand("grade: redo a bit soft step=env")
        self.assertEqual((got["grade"], got["decision"], got["problems"]),
                         (None, "redo", []))
        self.assertIsNone(lh.detect_signal("A van drove past the harbour"))

    def test_ambiguous_a_is_asked_not_guessed(self):
        ledger = self._start()
        for text in ("grade: A great job step=final",
                     "grade: redo step=final A van is too big"):
            got = lh.parse_shorthand(text)
            self.assertIsNone(got["grade"], text)
            self.assertTrue(got["problems"], text)
            out = self._say(text)
            self.assertIn("NOT recorded", out)
        self.assertFalse(ledger.exists())
        pending = lh.load_marker("fixture-session")["pending"]
        self.assertEqual(len(pending), 2)
        self.assertIn("could be the grade A", pending[0]["problem"])


class ShorthandStrictnessTests(_TmpEnv):
    """One rule set for the shorthand: anything that cannot be recorded exactly as
    Tony meant is not recorded and says why (never a silent drop or partial line)."""

    def _start(self):
        lh.run(payload("PostToolUse", tool="Neon_Parcel_Longform_Compilation_v2"),
               "claude", "skill")
        return Path(lh.load_marker("fixture-session")["ledger_path"])

    def _say(self, text):
        return lh.run(payload("UserPromptSubmit", prompt=text), "claude", "prompt")

    def test_decision_comes_from_the_header_not_his_comment(self):
        got = lh.parse_shorthand("grade: B+ accept step=final no need to redo")
        self.assertEqual(got["decision"], "accept")
        got = lh.parse_shorthand("grade: A step=final looks great, redo the audio later")
        self.assertEqual((got["grade"], got["decision"]), ("A", None))

    def test_unrecordable_notes_write_nothing_and_say_why(self):
        ledger = self._start()
        cases = {
            "grade: B+ A- step=final": "more than one grade",
            "grade: accept redo step=final": "more than one decision",
            "grade: E step=final": "not a grade on the scale",
            "grade: A step=final attempt=0": "attempt=",
            "grade: A step=final attempt=-1": "attempt=",
            "grade: A step=final attempt=1.5": "attempt=",
            "grade: C- redo step=final step=env": "two different step=",
            "grade:": "no letter grade",
            "grade: 87 accept step=final": "no letter grade",
        }
        for text, why in cases.items():
            out = self._say(text)
            self.assertIn("NOT recorded", out, text)
            self.assertIn(why, out, text)
        self.assertFalse(ledger.exists())
        self.assertEqual(len(lh.load_marker("fixture-session")["pending"]), len(cases))

    def test_step_value_punctuation_and_case(self):
        ledger = self._start()
        self._say("grade: B+ accept step=Final, great")
        ev = ql.read_events(ledger)[0]
        self.assertEqual((ev["step"], ev["level"]), ("final", "final"))

    def test_attempt_defaults_to_latest_attempt_like_the_cli(self):
        ledger = self._start()
        ql.append_event(ledger, ql.build_event(
            workflow_id="neon_parcel_longform", run_id="Agent-OS",
            step="character_sheet.motoboy", level="sub_step", attempt=6,
            source="agent_self_correction", actor="agent", reason="v6"))
        self._say("grade: B+ accept step=character_sheet.motoboy")
        self.assertEqual(ql.read_events(ledger)[-1]["attempt"], 6)

    def test_write_failure_is_a_visible_pending_item(self):
        self._start()
        marker = lh.load_marker("fixture-session")
        marker["ledger_path"] = str(Path(self.tmp.name) / "No_Such_Folder" / "L.jsonl")
        lh.save_marker("fixture-session", marker)
        out = self._say("grade: B+ accept step=final")
        self.assertIn("NOT recorded", out)
        self.assertIn("does not exist", out)
        self.assertIn("record it now by hand", out)
        self.assertFalse((Path(self.tmp.name) / "No_Such_Folder").exists())
        pending = lh.load_marker("fixture-session")["pending"]
        self.assertEqual(pending[0]["verbatim"], "grade: B+ accept step=final")

    def test_grade_without_active_ledger_is_not_silent(self):
        out = self._say("grade: B+ accept step=final")
        self.assertIn("NOT recorded", out)
        self.assertEqual(self._say("honestly that one is a B+"), "")  # plain chat stays quiet

    def test_signal_reminder_clears_on_a_step_level_grade(self):
        ledger = self._start()
        self._say("honestly the environment is a C, redo it")
        self.assertEqual(len(lh.load_marker("fixture-session")["pending"]), 1)
        # The agent asks which step and records it at step level (not final).
        ql.append_event(ledger, ql.build_event(
            workflow_id="neon_parcel_longform", run_id="Agent-OS", step="environment",
            level="step", attempt=1, source="director_judgment", actor="Tony",
            reason="", director={"grade": "C", "decision": "redo",
                                 "verbatim": "honestly the environment is a C, redo it"}))
        self.assertEqual(lh.run(payload("Stop"), "claude", "stop"), "")

    def test_lowercase_signed_grade_in_plain_chat_is_a_signal(self):
        self.assertEqual(lh.detect_signal("that was a b- honestly")["grade"], "B-")
        self.assertIsNone(lh.detect_signal("I wrote it in c++"))
        self.assertIsNone(lh.detect_signal("more B-roll please"))

    def test_skill_restart_keeps_pending(self):
        self._start()
        self._say("honestly that one is a B+")
        self._start()  # skill invoked again in the same session
        self.assertEqual(len(lh.load_marker("fixture-session")["pending"]), 1)

    def test_session_id_cannot_escape_the_marker_folder(self):
        lh.run(payload("PostToolUse", tool="Neon_Parcel_Longform_Compilation_v2",
                       session="../../evil/x"), "claude", "skill")
        made = list(Path(self.tmp.name).glob("agent_os_quality_ledger_*.json"))
        self.assertEqual(len(made), 1)
        self.assertFalse((Path(self.tmp.name).parent / "evil").exists())
        self.assertEqual(list(Path(self.tmp.name).glob("*.tmp")), [])


class StopScopeTests(_TmpEnv):
    def test_unexplained_retries_only_for_this_run(self):
        lh.run(payload("PostToolUse", tool="Neon_Parcel_Longform_Compilation_v2"),
               "claude", "skill")
        ledger = Path(lh.load_marker("fixture-session")["ledger_path"])
        for attempt in (1, 2):  # an OLD run's silent retry in the shared ledger
            ql.append_event(ledger, ql.build_event(
                workflow_id="neon_parcel_longform", run_id="old-run", step="video",
                level="step", attempt=attempt, source="mechanical_check",
                actor="mechanical_check", reason="", check={"name": "c", "result": "pass"}))
        self.assertEqual(lh.run(payload("Stop"), "claude", "stop"), "")


class RunResolutionTests(unittest.TestCase):
    """The hook never invents a run from the workspace root and never makes folders."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "Agent-OS"
        (self.root / "Productions" / "0002_Show" / "Data" / "History").mkdir(parents=True)
        (self.root / "Logs").mkdir()
        self.old_ws = lh.WORKSPACE
        lh.WORKSPACE = self.root
        self.old_test = os.environ.pop("QUALITY_LEDGER_TEST", None)
        self.entry = {"workflow_id": "neon",
                      "ledger": "Productions/{run_id}/Data/History/Quality_Ledger.jsonl"}

    def tearDown(self):
        lh.WORKSPACE = self.old_ws
        if self.old_test is not None:
            os.environ["QUALITY_LEDGER_TEST"] = self.old_test
        self.tmp.cleanup()

    def test_workspace_root_is_not_a_run(self):
        run, ledger, note = lh.resolve_target({"cwd": str(self.root)}, self.entry)
        self.assertIsNone(ledger)
        self.assertIn("not inside", note)

    def test_production_subfolder_finds_its_run(self):
        cwd = self.root / "Productions" / "0002_Show" / "Data"
        run, ledger, _ = lh.resolve_target({"cwd": str(cwd)}, self.entry)
        self.assertEqual(run, "0002_Show")
        self.assertEqual(Path(ledger).parent.resolve(),
                         (self.root / "Productions/0002_Show/Data/History").resolve())

    def test_missing_production_folder_is_never_created(self):
        cwd = self.root / "Productions" / "0003_New"
        run, ledger, _ = lh.resolve_target({"cwd": str(cwd)}, self.entry)
        self.assertIsNone(ledger)
        self.assertFalse((self.root / "Productions" / "0003_New").exists())

    def test_central_ledger_at_root_gets_a_dated_run(self):
        entry = {"workflow_id": "etsy_listing", "ledger": "Logs/Quality_Ledger.jsonl"}
        run, ledger, _ = lh.resolve_target({"cwd": str(self.root)}, entry)
        self.assertTrue(run.endswith("-etsy_listing"))
        self.assertNotEqual(run, "Agent-OS")
        self.assertTrue(ledger.endswith("Quality_Ledger.jsonl"))


class HookGuardTests(_TmpEnv):
    def _run(self, stdin, *args, keep_open=False):
        import subprocess
        import time
        start = time.time()
        if keep_open:  # a harness that never closes stdin
            proc = subprocess.Popen([sys.executable, str(HERE / "ledger_hook.py"), *args],
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, text=True)
            try:
                proc.wait(timeout=5)
            finally:
                proc.stdin.close()
            return proc.returncode, time.time() - start
        proc = subprocess.run([sys.executable, str(HERE / "ledger_hook.py"), *args],
                              input=stdin, capture_output=True, text=True, timeout=10)
        return proc.returncode, time.time() - start

    def test_mistyped_hook_command_still_exits_0(self):
        # exit 2 on UserPromptSubmit would block Tony's prompt.
        self.assertEqual(self._run("{}", "--harness", "claude-code", "--event", "prompt")[0], 0)
        self.assertEqual(self._run("{}")[0], 0)

    def test_wall_clock_guard_really_stops_a_hung_stdin(self):
        rc, secs = self._run("", "--event", "prompt", keep_open=True)
        self.assertEqual(rc, 0)
        self.assertLess(secs, 2.0)

    def test_truncated_and_binary_stdin_fail_open(self):
        for junk in ('{"session_id": "x", "prompt": "gra', "\x00\xff garbage", "[1, 2]"):
            self.assertEqual(self._run(junk, "--event", "prompt")[0], 0)

    def test_locked_ledger_is_reported_within_budget(self):
        import fcntl
        import time
        lh.run(payload("PostToolUse", tool="Neon_Parcel_Longform_Compilation_v2"),
               "claude", "skill")
        ledger = Path(lh.load_marker("fixture-session")["ledger_path"])
        with open(ledger, "a") as holder:
            fcntl.flock(holder.fileno(), fcntl.LOCK_EX)
            start = time.time()
            out = lh.run(payload("UserPromptSubmit", prompt="grade: B+ accept step=final"),
                         "claude", "prompt")
            self.assertLess(time.time() - start, 1.0)
        self.assertIn("locked", out)
        self.assertEqual(ledger.read_text(), "")
        self.assertEqual(len(lh.load_marker("fixture-session")["pending"]), 1)


if __name__ == "__main__":
    unittest.main()
