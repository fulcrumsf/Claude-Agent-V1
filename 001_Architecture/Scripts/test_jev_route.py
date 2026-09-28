import contextlib
import io
import json
import os
import time
import unittest
from unittest import mock

import jev_route


def fake_response(route="chore", conf=0.9, multi=0.1):
    body = {"answers": {
        "route": {"type": "choice", "choice": route, "confidence": conf,
                  "probabilities": {route: conf}},
        "multi_task": {"type": "noul", "noul": multi}}}
    return io.BytesIO(json.dumps(body).encode())


class DecideTests(unittest.TestCase):
    @mock.patch.object(jev_route, "load_secret", return_value="sk-test")
    @mock.patch("urllib.request.urlopen")
    def test_parses_route_and_multi_task(self, urlopen, _):
        urlopen.return_value.__enter__.return_value = fake_response("frontier", 0.8, 0.7)
        d = jev_route.decide("Re-architect the ingest pipeline across 6 scripts")
        self.assertEqual((d.route, d.confidence, d.multi_task), ("frontier", 0.8, 0.7))
        sent = json.loads(urlopen.call_args[0][0].data)
        self.assertEqual(sent["model"], "typesafe/jev-1.13")
        self.assertEqual(set(sent["questions"]), {"route", "multi_task"})

    @mock.patch.object(jev_route, "load_secret", return_value="sk-test")
    @mock.patch("urllib.request.urlopen", side_effect=TimeoutError)
    def test_fails_open_on_timeout(self, *_):
        self.assertIsNone(jev_route.decide("anything long enough to route"))

    @mock.patch.object(jev_route, "load_secret", return_value=None)
    def test_no_key_means_no_decision(self, _):
        self.assertIsNone(jev_route.decide("anything long enough to route"))

    def test_skips_slash_commands_and_tiny_prompts(self):
        self.assertIsNone(jev_route.decide("/model"))
        self.assertIsNone(jev_route.decide("yes"))

    @mock.patch.dict("os.environ", {"AGENT_OS_DELEGATE_WORKER": "1"})
    def test_skipped_inside_delegate_worker(self):
        self.assertIsNone(jev_route.decide("anything long enough to route"))


class HintTests(unittest.TestCase):
    def test_answer_gets_no_hint(self):
        self.assertIsNone(jev_route.hint_for(jev_route.Decision("answer", 0.9, 0.1), "claude"))

    def test_frontier_names_the_harness_subagents(self):
        h = jev_route.hint_for(jev_route.Decision("frontier", 0.8, 0.1), "claude")
        self.assertIn("opus-standard", h)
        h = jev_route.hint_for(jev_route.Decision("frontier", 0.8, 0.1), "codex")
        self.assertIn("sol-standard", h)

    def test_chore_points_to_delegate(self):
        h = jev_route.hint_for(jev_route.Decision("chore", 0.9, 0.1), "gemini")
        self.assertIn("delegate.py", h)

    def test_low_confidence_gets_no_hint(self):
        self.assertIsNone(jev_route.hint_for(jev_route.Decision("chore", 0.4, 0.1), "claude"))

    def test_brain_dump_hint_asks_to_split(self):
        h = jev_route.hint_for(jev_route.Decision("answer", 0.9, 0.8), "claude")
        self.assertIn("split", h.lower())


class AntigravityPromptTests(unittest.TestCase):
    def test_antigravity_reads_last_user_message(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
            f.write('{"type":"USER_INPUT","content":"first"}\n{"type":"MODEL","content":"x"}\n'
                    '{"type":"USER_INPUT","content":"tag every note in the ingest folder"}\n'
                    'not json, no marker\n["USER_INPUT"]\n')
        self.addCleanup(os.unlink, f.name)
        self.assertEqual(jev_route.antigravity_prompt({"invocationNum": 0, "transcriptPath": f.name}),
                         "tag every note in the ingest folder")
        self.assertEqual(jev_route.antigravity_prompt({"invocationNum": 2, "transcriptPath": f.name}), "")


class MainFailsOpenTests(unittest.TestCase):
    def run_main(self, argv, stdin):
        out = io.StringIO()
        with mock.patch.object(jev_route.sys, "argv", ["jev_route.py"] + argv), \
             mock.patch.object(jev_route.sys, "stdin", io.StringIO(stdin)), \
             mock.patch.object(jev_route, "log"), \
             contextlib.redirect_stdout(out):
            rc = jev_route.main()
        return rc, out.getvalue()

    def test_bad_input_returns_0_with_no_output(self):
        cases = [
            ([], "[]"),                                   # non-dict payload
            ([], "not json"),
            (["--harness"], '{"prompt": "x"}'),           # --harness with no value
            (["--harness", "antigravity"], '{"invocationNum": "abc", "transcriptPath": "/x"}'),
        ]
        for argv, stdin in cases:
            with mock.patch.object(jev_route, "decide", side_effect=AssertionError("must not be reached")):
                self.assertEqual(self.run_main(argv, stdin), (0, ""), (argv, stdin))

    def test_wall_clock_guard_stops_a_slow_run(self):
        def slow(_prompt):
            time.sleep(2)
            return jev_route.Decision("chore", 0.9, 0.1)
        with mock.patch.object(jev_route, "WALL_CLOCK", 0.1), mock.patch.object(jev_route, "decide", side_effect=slow):
            start = time.time()
            self.assertEqual(self.run_main([], '{"prompt": "tag every note in the ingest folder"}'), (0, ""))
            self.assertLess(time.time() - start, 1.0)

    def test_good_run_still_prints_hint(self):
        with mock.patch.object(jev_route, "decide", return_value=jev_route.Decision("chore", 0.9, 0.1)):
            rc, out = self.run_main([], '{"prompt": "tag every note in the ingest folder"}')
        self.assertEqual(rc, 0)
        self.assertIn("delegate.py", json.loads(out)["hookSpecificOutput"]["additionalContext"])


class SecretTests(unittest.TestCase):
    def test_reads_export_and_plain_lines(self):
        text = "export OPENROUTER_API_KEY=sk-a\nOTHER=1\nOPENROUTER_CHORES_KEY='sk-b'\n"
        with mock.patch("builtins.open", mock.mock_open(read_data=text)), \
             mock.patch.dict("os.environ", {}, clear=True):
            self.assertEqual(jev_route.load_secret("OPENROUTER_API_KEY"), "sk-a")
            self.assertEqual(jev_route.load_secret("OPENROUTER_CHORES_KEY"), "sk-b")


class RenderTests(unittest.TestCase):
    def test_claude_and_codex_shape(self):
        for h in ("claude", "codex"):
            out = json.loads(jev_route.render(h, "HINT"))
            self.assertEqual(out["hookSpecificOutput"]["additionalContext"], "HINT")
            self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "UserPromptSubmit")

    def test_gemini_shape(self):
        out = json.loads(jev_route.render("gemini", "HINT"))
        self.assertEqual(out["hookSpecificOutput"]["additionalContext"], "HINT")

    def test_no_hint_prints_nothing(self):
        self.assertEqual(jev_route.render("claude", None), "")


if __name__ == "__main__":
    unittest.main()
