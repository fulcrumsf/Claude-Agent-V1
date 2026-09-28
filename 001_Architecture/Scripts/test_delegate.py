import contextlib
import io
import os
import subprocess
import tempfile
import unittest
from unittest import mock

import delegate


class PromptTests(unittest.TestCase):
    def test_skill_is_read_first_and_rules_included(self):
        p = delegate.build_prompt("Ingest the 3 new files", "ingest")
        self.assertIn("001_Architecture/Skills/ingest/SKILL.md", p)
        self.assertIn("Never delete", p)
        self.assertLess(p.index("SKILL.md"), p.index("Ingest the 3 new files"))

    def test_without_skill(self):
        self.assertNotIn("SKILL.md", delegate.build_prompt("Summarize TOOLBOX.md", None))


class CommandTests(unittest.TestCase):
    def test_command_uses_openrouter_provider_and_auto_router(self):
        cmd = delegate.build_command("PROMPT", "/Users/tonymacbook2025/Documents/Agent-OS", "/tmp/last.txt")
        joined = " ".join(cmd)
        self.assertEqual(cmd[:2], ["codex", "exec"])
        self.assertIn("model_provider=openrouter_chores", joined)
        self.assertIn('env_key="OPENROUTER_CHORES_KEY"', joined)
        self.assertIn(delegate.MODEL, cmd)
        self.assertEqual(cmd[-1], "PROMPT")

    def test_worker_is_isolated_from_plugins_and_mcp(self):
        cmd = delegate.build_command("PROMPT", "/tmp", "/tmp/last.txt", servers=["blotato", "node_repl", "bad.name"])
        overrides = [cmd[i + 1] for i, c in enumerate(cmd) if c == "-c"]
        self.assertIn('model_reasoning_effort="low"', overrides)
        for f in ("plugins", "apps", "browser_use", "computer_use"):
            self.assertIn(f"features.{f}=false", overrides)
        self.assertIn("mcp_servers.blotato.enabled=false", overrides)
        self.assertIn("mcp_servers.node_repl.enabled=false", overrides)
        self.assertFalse(any("bad.name" in o for o in overrides))
        self.assertFalse(any("hooks" in o for o in overrides))  # fs_guard hook must keep firing

    def test_mcp_server_names_read_from_config(self):
        with tempfile.NamedTemporaryFile("w", suffix=".toml", delete=False) as f:
            f.write('model = "x"\n[mcp_servers.alpha]\ncommand = "a"\n[mcp_servers.beta]\nurl = "b"\n')
        self.addCleanup(os.unlink, f.name)
        self.assertEqual(delegate.mcp_server_names(delegate.Path(f.name)), ["alpha", "beta"])

    def test_missing_config_file_is_safe_empty(self):
        # No config at all -> nothing is configured -> [] is a safe answer, not a failure.
        self.assertEqual(delegate.mcp_server_names(delegate.Path("/nonexistent/config.toml")), [])

    def test_unreadable_config_fails_closed(self):
        # A config that EXISTS but can't be parsed must not be treated as "no servers":
        # servers may be configured and we just can't see their names, so this must raise.
        with tempfile.NamedTemporaryFile("w", suffix=".toml", delete=False) as f:
            f.write("this is not valid toml [[[")
        self.addCleanup(os.unlink, f.name)
        with self.assertRaises(delegate.ConfigReadError):
            delegate.mcp_server_names(delegate.Path(f.name))

    def test_main_refuses_to_run_when_config_unreadable(self):
        with mock.patch.object(delegate, "load_secret", return_value="sk-test"), \
             mock.patch.object(delegate, "mcp_server_names", side_effect=delegate.ConfigReadError("boom")), \
             mock.patch.object(subprocess, "run") as run, \
             mock.patch.dict("os.environ", {"AGENT_OS_DELEGATE_WORKER": ""}), \
             contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(delegate.main(["Summarize TOOLBOX.md"]), 4)
        self.assertIn("refused", err.getvalue())
        run.assert_not_called()

    def test_refuses_without_chores_key(self):
        with mock.patch.object(delegate, "load_secret", return_value=None), \
             mock.patch.dict("os.environ", {"AGENT_OS_DELEGATE_WORKER": ""}), \
             contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(delegate.main(["Summarize TOOLBOX.md"]), 2)

    def test_flag_without_value_is_a_usage_error(self):
        for argv in (["task", "--skill"], ["task", "--cwd"], ["task", "--skill", "--dry-run"]):
            err = io.StringIO()
            with mock.patch.dict("os.environ", {"AGENT_OS_DELEGATE_WORKER": ""}), \
                 contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(delegate.main(argv), 1)
            self.assertIn("needs a value", err.getvalue())


def run_main_mocked(run_side_effect=None, returncode=0):
    """Run delegate.main with the worker, git, snapshots and log file mocked; returns (rc, stdout, mock_run)."""
    out = io.StringIO()
    with mock.patch.object(delegate, "load_secret", return_value="fake-key"), \
         mock.patch.dict("os.environ", {"AGENT_OS_DELEGATE_WORKER": ""}), \
         mock.patch.object(delegate, "git_status", return_value=set()), \
         mock.patch.object(delegate, "snapshot", return_value={}), \
         mock.patch.object(delegate.subprocess, "run") as mock_run, \
         mock.patch("builtins.open", mock.mock_open()), \
         mock.patch.object(delegate.Path, "exists", return_value=False), \
         contextlib.redirect_stdout(out):
        if run_side_effect is not None:
            mock_run.side_effect = run_side_effect
        else:
            mock_run.return_value = mock.Mock(returncode=returncode)
        rc = delegate.main(["Summarize TOOLBOX.md"])
    return rc, out.getvalue(), mock_run


class AntiRecursionTests(unittest.TestCase):
    def test_refuses_inside_a_delegated_worker(self):
        err = io.StringIO()
        with mock.patch.dict("os.environ", {"AGENT_OS_DELEGATE_WORKER": "1"}), \
             mock.patch.object(delegate, "load_secret") as ls, \
             mock.patch.object(delegate.subprocess, "run") as run, \
             contextlib.redirect_stderr(err):
            self.assertEqual(delegate.main(["Summarize TOOLBOX.md"]), 3)
        self.assertIn("refused, already inside a delegated worker", err.getvalue())
        ls.assert_not_called()
        run.assert_not_called()

    def test_worker_env_sets_delegate_flag_and_timeout(self):
        rc, _, mock_run = run_main_mocked()
        self.assertEqual(rc, 0)
        _, kwargs = mock_run.call_args
        self.assertEqual(kwargs["env"].get("AGENT_OS_DELEGATE_WORKER"), "1")
        self.assertEqual(kwargs["env"].get("OPENROUTER_CHORES_KEY"), "fake-key")
        self.assertEqual(kwargs["timeout"], delegate.WORKER_TIMEOUT)

    def test_timeout_still_reports_and_returns_124(self):
        rc, out, _ = run_main_mocked(run_side_effect=subprocess.TimeoutExpired("codex", delegate.WORKER_TIMEOUT))
        self.assertEqual(rc, 124)
        self.assertIn("TIMED OUT", out)
        self.assertIn("== Worker report ==", out)
        self.assertIn("== Files changed during the run ==", out)


class ChangedFilesTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()  # system temp dir, not inside Agent-OS
        self.addCleanup(tmp.cleanup)
        self.root = tmp.name
        os.makedirs(os.path.join(self.root, "000_Ingest"))
        os.makedirs(os.path.join(self.root, "Notes"))
        for rel in ("000_Ingest/a.md", "000_Ingest/b.md", "Notes/dirty.md", "Notes/untracked_file.md"):
            with open(os.path.join(self.root, rel), "w") as fh:
                fh.write("x")

    def touch(self, rel, text):
        path = os.path.join(self.root, rel)
        with open(path, "w") as fh:
            fh.write(text)
        st = os.stat(path)
        os.utime(path, (st.st_atime, st.st_mtime + 5))

    def test_snapshot_diff_reports_added_changed_missing(self):
        entries = {" M Notes/dirty.md", "?? Notes/untracked_file.md"}
        before = delegate.snapshot(self.root, entries)
        self.assertEqual(set(before), {"000_Ingest/a.md", "000_Ingest/b.md", "Notes/dirty.md", "Notes/untracked_file.md"})
        self.touch("Notes/dirty.md", "changed again")
        self.touch("000_Ingest/c.md", "new")
        os.rename(os.path.join(self.root, "000_Ingest/b.md"), os.path.join(self.root, "Notes/b_moved.md"))
        after = delegate.snapshot(self.root, entries)
        report = delegate.change_report(entries, entries | {"?? Notes/b_moved.md"}, before, after)
        self.assertIn("changed: Notes/dirty.md", report)
        self.assertIn("added:   000_Ingest/c.md", report)
        self.assertIn("missing: 000_Ingest/b.md", report)
        self.assertIn("new git entry:  ?? Notes/b_moved.md", report)
        self.assertNotIn("a.md", report)
        self.assertNotIn("untracked_file", report)

    def test_no_changes(self):
        snap = delegate.snapshot(self.root, set())
        self.assertEqual(delegate.change_report(set(), set(), snap, delegate.snapshot(self.root, set())),
                         "(no changes detected)")

    def test_snapshot_is_bounded(self):
        with mock.patch.object(delegate, "MAX_FILES_PER_ROOT", 1):
            snap = delegate.snapshot(self.root, set())
        self.assertIn("~capped", snap)
        self.assertEqual(len([k for k in snap if k.startswith("000_Ingest/")]), 1)
        report = delegate.change_report(set(), set(), snap, snap)
        self.assertIn("size bound", report)

    def test_git_status_parses_porcelain_z(self):
        fake = mock.Mock(returncode=0, stdout=" M a.md\0?? new dir/\0R  new.md\0old.md\0")
        with mock.patch.object(delegate.subprocess, "run", return_value=fake):
            self.assertEqual(delegate.git_status("/x"), {" M a.md", "?? new dir/", "R  new.md"})
        with mock.patch.object(delegate.subprocess, "run", return_value=mock.Mock(returncode=128, stdout="")):
            self.assertIsNone(delegate.git_status("/x"))


if __name__ == "__main__":
    unittest.main()
