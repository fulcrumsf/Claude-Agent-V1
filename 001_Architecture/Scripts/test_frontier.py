import contextlib
import io
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import delegate
import frontier


class CommandTests(unittest.TestCase):
    def overrides(self, cmd):
        return [cmd[i + 1] for i, c in enumerate(cmd) if c == "-c"]

    def test_uses_chatgpt_login_and_sol_model(self):
        cmd = frontier.build_command("PROMPT", "/tmp", "/tmp/last.txt", servers=[])
        joined = " ".join(cmd)
        self.assertEqual(cmd[:2], ["codex", "exec"])
        self.assertNotIn("openrouter", joined)  # default provider = Tony's ChatGPT login, not the chores key
        self.assertEqual(cmd[cmd.index("-m") + 1], "gpt-6-sol")
        self.assertEqual(cmd[-1], "PROMPT")

    def test_effort_standard_and_deep(self):
        self.assertIn('model_reasoning_effort="medium"',
                      self.overrides(frontier.build_command("P", "/tmp", "/tmp/l", servers=[])))
        self.assertIn('model_reasoning_effort="high"',
                      self.overrides(frontier.build_command("P", "/tmp", "/tmp/l", deep=True, servers=[])))

    def test_same_isolation_as_delegate(self):
        o = self.overrides(frontier.build_command("P", "/tmp", "/tmp/l", servers=["blotato"]))
        for f in delegate.DISABLED_FEATURES:
            self.assertIn(f"features.{f}=false", o)
        self.assertIn("mcp_servers.blotato.enabled=false", o)
        self.assertFalse(any("hooks" in x for x in o))  # fs_guard must keep firing

    def test_prompt_carries_rules_then_task(self):
        p = frontier.build_prompt("Root-cause the scale bug")
        self.assertIn("Never delete", p)
        self.assertIn("Never run frontier.py", p)
        self.assertLess(p.index("Never delete"), p.index("Root-cause the scale bug"))

    def test_delegate_defaults_unchanged(self):
        # frontier.py added optional params to delegate.py; the chore worker must keep low effort.
        self.assertEqual(delegate.isolation_overrides([])[0], 'model_reasoning_effort="low"')


class MainTests(unittest.TestCase):
    def run_main(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = frontier.main(argv)
        return rc, out.getvalue(), err.getvalue()

    @mock.patch.dict("os.environ", {"AGENT_OS_DELEGATE_WORKER": "1"})
    def test_refuses_inside_a_worker(self):
        self.assertEqual(self.run_main(["x"])[0], 3)

    @mock.patch.object(frontier, "mcp_server_names", return_value=[])
    def test_usage_errors(self, _):
        self.assertEqual(self.run_main([])[0], 1)
        self.assertEqual(self.run_main(["task", "--cwd"])[0], 1)

    @mock.patch.object(frontier, "mcp_server_names", side_effect=delegate.ConfigReadError("bad toml"))
    def test_unreadable_codex_config_fails_closed(self, _):
        self.assertEqual(self.run_main(["task"])[0], 4)

    @mock.patch.object(frontier, "mcp_server_names", return_value=[])
    def test_dry_run_prints_command_only(self, _):
        rc, out, _ = self.run_main(["Design", "the", "thing", "--deep", "--dry-run"])
        self.assertEqual(rc, 0)
        self.assertIn("gpt-6-sol", out)
        self.assertIn('model_reasoning_effort="high"', out)
        self.assertTrue(out.strip().endswith("<prompt>"))

    @mock.patch.object(frontier, "mcp_server_names", return_value=[])
    def test_run_sets_worker_flag_and_reports(self, _):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        log_path = Path(tmp.name) / "f.log"
        last = str(log_path.with_suffix(".last.txt"))
        Path(last).write_text("did the thing")

        def fake_run(cmd, stdout, stderr, timeout, env):
            self.assertEqual(env["AGENT_OS_DELEGATE_WORKER"], "1")
            self.assertEqual(timeout, frontier.WORKER_TIMEOUT)
            return subprocess.CompletedProcess(cmd, 0)

        with mock.patch.object(frontier, "open_log", return_value=(log_path, last, open(log_path, "w"))), \
             mock.patch.object(frontier, "git_status", return_value=set()), \
             mock.patch.object(frontier, "snapshot", return_value={}), \
             mock.patch.object(frontier.subprocess, "run", side_effect=fake_run):
            rc, out, _ = self.run_main(["Fix", "it", "--cwd", tmp.name])
        self.assertEqual(rc, 0)
        self.assertIn("did the thing", out)
        self.assertIn("(no changes detected)", out)

    @mock.patch.object(frontier, "mcp_server_names", return_value=[])
    def test_timeout_is_reported(self, _):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        log_path = Path(tmp.name) / "f.log"
        with mock.patch.object(frontier, "open_log", return_value=(log_path, str(log_path) + ".last", open(log_path, "w"))), \
             mock.patch.object(frontier, "git_status", return_value=set()), \
             mock.patch.object(frontier, "snapshot", return_value={}), \
             mock.patch.object(frontier.subprocess, "run", side_effect=subprocess.TimeoutExpired("codex", 1)):
            rc, out, _ = self.run_main(["Fix", "it"])
        self.assertEqual(rc, 124)
        self.assertIn("TIMED OUT", out)


class OpenLogPrefixTests(unittest.TestCase):
    def test_prefix_falls_back_to_temp(self):
        with mock.patch.object(delegate.Path, "home", return_value=Path("/nonexistent-home")):
            path, last, fh = delegate.open_log("stamp", prefix="Agent-OS-Frontier")
        fh.close()
        self.addCleanup(os.unlink, path)
        self.assertTrue(path.name.startswith("Agent-OS-Frontier-stamp-"))


if __name__ == "__main__":
    unittest.main()
