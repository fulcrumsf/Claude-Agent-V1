"""Tests for action_log.py (the Agent-OS paper trail). Run from 001_Architecture/Scripts:
    python3 -m unittest test_action_log -v
No test deletes anything: temp dirs are created with mkdtemp and left for the OS to clear,
and the git-deletion test simulates a missing tracked file with `git rm --cached`
(index only, the file itself stays on disk)."""
import io
import contextlib
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import action_log
import jev_route

AO = str(action_log.AGENT_OS)


def temp_log() -> str:
    return os.path.join(tempfile.mkdtemp(prefix="action_log_test_"), "actions.jsonl")


def read(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


class ReadOnlyCommandTests(unittest.TestCase):
    def test_read_only_commands_are_skipped(self):
        for cmd in ["ls -la", "git status && git log --oneline -5", "grep -rn foo . | head -20",
                    "find . -name '*.md'", "cat a.txt 2>/dev/null", "sed -n 1,5p f.md",
                    "git -C /x status --short", "cd /tmp && pwd", "wc -l *.py", "git diff HEAD~1 -- a",
                    ["/bin/zsh", "-lc", "ls"][2:], "FOO=1 ls", "git branch -a", "ls | xargs wc -l"]:
            self.assertTrue(action_log.is_readonly_command(cmd), cmd)

    def test_anything_that_can_change_state_is_logged(self):
        for cmd in ["rm x", "echo hi > f.md", "echo hi >> f.md", "sed -i '' s/a/b/ f", "find . -delete",
                    "find . -exec rm {} +", "python3 x.py", "git commit -m x", "git checkout -- a",
                    "echo $(rm -rf x)", "cat <<EOF > f\nx\nEOF", "ls | tee out.txt", "git branch -D old",
                    "env FOO=1 python3 x.py", "ls | xargs rm", "mv a b", "codex debug prompt-input",
                    "mkdir new", "touch a", "cp a b", "sort -o out in", "unknowncmd --flag", ""]:
            self.assertFalse(action_log.is_readonly_command(cmd), cmd)

    def test_list_commands(self):
        self.assertTrue(action_log.is_readonly_command(["git", "status"]))
        self.assertFalse(action_log.is_readonly_command(["rm", "-rf", "x"]))


class DescribeToolTests(unittest.TestCase):
    def test_write_edit_paths_resolve_against_cwd(self):
        self.assertEqual(action_log.describe_tool("Write", {"file_path": "a/b.md"}, AO),
                         {"action": "write", "paths": [AO + "/a/b.md"]})
        self.assertEqual(action_log.describe_tool("Edit", {"file_path": AO + "/x.md"}, AO)["action"], "edit")
        self.assertEqual(action_log.describe_tool("replace_file_content", {"TargetFile": "/t/x.md"}, AO),
                         {"action": "edit", "paths": ["/t/x.md"]})

    def test_apply_patch_lists_every_operation(self):
        patch = ("*** Begin Patch\n*** Delete File: old.md\n*** Add File: new.md\n+x\n"
                 "*** Update File: a.md\n*** Move to: b.md\n*** End Patch")
        d = action_log.describe_tool("apply_patch", {"command": patch}, AO)
        self.assertEqual(d["paths"], [AO + "/old.md", AO + "/new.md", AO + "/a.md", AO + "/b.md"])
        self.assertIn("delete old.md", d["summary"])

    def test_subagent_launch_keeps_its_instructions(self):
        d = action_log.describe_tool("Agent", {"subagent_type": "opus-deep", "description": "Investigate",
                                               "prompt": "Find who deleted plugin-creator"}, AO)
        self.assertEqual(d["action"], "subagent")
        self.assertIn("opus-deep", d["summary"])
        self.assertIn("plugin-creator", d["prompt"])

    def test_read_tools_and_read_only_mcp_are_skipped(self):
        for tool in ["Read", "Glob", "Grep", "view_file", "mcp__obsidian-mcp-server__obsidian_get_note",
                     "mcp__obsidian-mcp-server__obsidian_list_notes"]:
            self.assertIsNone(action_log.describe_tool(tool, {"path": "a.md"}, AO), tool)

    def test_state_changing_mcp_and_unknown_tools_are_logged(self):
        for tool in ["mcp__obsidian-mcp-server__obsidian_write_note", "mcp__blotato__blotato_create_post",
                     "mcp__obsidian-mcp-server__obsidian_delete_note", "brand_new_tool"]:
            self.assertIsNotNone(action_log.describe_tool(tool, {"path": "a.md"}, AO), tool)


class RecordToolTests(unittest.TestCase):
    def setUp(self):
        self.log = temp_log()
        self.env = mock.patch.dict(os.environ, {"AGENT_OS_ACTION_LOG": self.log, "AGENT_OS_DELEGATE_WORKER": ""})
        self.env.start()

    def tearDown(self):
        self.env.stop()

    def test_attribution_fields_from_each_harness(self):
        action_log.record_tool("claude", {"session_id": "s", "transcript_path": "/t.jsonl", "agent_id": "a",
                                          "agent_type": "opus-standard", "tool_use_id": "u"},
                               {"tool_name": "Write", "tool_input": {"file_path": "/x/a.md"}, "cwd": AO}, "allow")
        action_log.record_tool("codex", {"session_id": "c", "turn_id": "t1", "model": "gpt"},
                               {"tool_name": "Bash", "tool_input": {"command": "touch a"}, "cwd": AO}, "allow")
        r1, r2 = read(self.log)
        self.assertEqual((r1["session"], r1["agent_type"], r1["agent_id"], r1["transcript"], r1["tool_use_id"]),
                         ("s", "opus-standard", "a", "/t.jsonl", "u"))
        self.assertEqual((r2["harness"], r2["turn"], r2["model"], r2["command"]), ("codex", "t1", "gpt", "touch a"))
        self.assertTrue(r1["t"].startswith("20") and r1["event"] == "tool")

    def test_read_only_allow_writes_nothing_but_deny_always_writes(self):
        p = {"tool_name": "Bash", "tool_input": {"command": "ls"}, "cwd": AO}
        action_log.record_tool("claude", {}, p, "allow")
        self.assertEqual(read(self.log), [])
        action_log.record_tool("claude", {}, p, "deny", "BLOCKED by Agent-OS guard")
        (r,) = read(self.log)
        self.assertEqual((r["decision"], r["action"]), ("deny", "blocked-call"))
        self.assertIn("BLOCKED", r["reason"])

    def test_delegate_worker_is_flagged(self):
        with mock.patch.dict(os.environ, {"AGENT_OS_DELEGATE_WORKER": "1"}):
            action_log.record_tool("codex", {}, {"tool_name": "Bash", "tool_input": {"command": "touch a"}}, "allow")
        self.assertTrue(read(self.log)[0]["delegate_worker"])

    def test_off_switch_writes_nothing(self):
        with mock.patch.dict(os.environ, {"AGENT_OS_ACTION_LOG": "off"}):
            action_log.record_tool("claude", {}, {"tool_name": "Write", "tool_input": {"file_path": "/a"}}, "allow")
            action_log.record_prompt("claude", {}, "hello there")
        self.assertFalse(os.path.exists(self.log))

    def test_garbage_never_raises(self):
        for raw, payload in [(None, None), ("x", {"tool_name": 5, "tool_input": "s"}), ({}, {"tool_input": [1]})]:
            action_log.record_tool("claude", raw, payload, "allow")
        action_log.record_prompt("claude", None, None)

    def test_huge_command_stays_one_short_valid_line(self):
        action_log.record_tool("claude", {}, {"tool_name": "Bash", "tool_input": {"command": "touch " + "a" * 20000}},
                               "allow")
        with open(self.log, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
        self.assertEqual(len(lines), 1)
        self.assertLessEqual(len(lines[0].encode()), action_log.MAX_LINE)
        self.assertTrue(json.loads(lines[0])["command"].endswith("[cut]"))

    def test_rotation_moves_never_deletes(self):
        with mock.patch.dict(os.environ, {"AGENT_OS_ACTION_LOG_MAX_BYTES": "300"}):
            for i in range(6):
                action_log.record_tool("claude", {}, {"tool_name": "Write", "tool_input": {"file_path": f"/f{i}"}},
                                       "allow")
        files = action_log._log_files(Path(self.log))
        self.assertGreater(len(files), 1)
        total = sum(len(read(str(f))) for f in files)
        self.assertEqual(total, 6)  # every record still exists somewhere


class PromptTests(unittest.TestCase):
    def setUp(self):
        self.log = temp_log()
        self.env = mock.patch.dict(os.environ, {"AGENT_OS_ACTION_LOG": self.log})
        self.env.start()

    def tearDown(self):
        self.env.stop()

    def test_prompt_is_recorded_redacted_and_capped(self):
        action_log.record_prompt("claude", {"session_id": "s9", "cwd": AO},
                                 "use sk-abcdefghijklmnopqrstuv and OPENAI_API_KEY=xyz123 <private>secret</private> "
                                 + "z" * 2000)
        (r,) = read(self.log)
        self.assertEqual((r["event"], r["session"]), ("prompt", "s9"))
        for leaked in ("sk-abcdefghijklmnopqrstuv", "xyz123", "secret"):
            self.assertNotIn(leaked, r["prompt"])
        self.assertLessEqual(len(r["prompt"]), 820)

    def test_jev_route_records_prompt_even_when_routing_returns_nothing(self):
        out = io.StringIO()
        with mock.patch.object(jev_route.sys, "argv", ["jev_route.py", "--harness", "codex"]), \
             mock.patch.object(jev_route.sys, "stdin", io.StringIO(json.dumps(
                 {"prompt": "clean up the ingest folder please", "session_id": "cx1"}))), \
             mock.patch.object(jev_route, "decide", return_value=None), \
             mock.patch.object(jev_route, "log"), \
             mock.patch.object(action_log, "check_deletions") as sentinel, \
             contextlib.redirect_stdout(out):
            self.assertEqual(jev_route.main(), 0)
        (r,) = read(self.log)
        self.assertEqual((r["harness"], r["session"], r["prompt"]), ("codex", "cx1", "clean up the ingest folder please"))
        sentinel.assert_called_once()
        self.assertEqual(out.getvalue(), "")

    def test_who_joins_tool_calls_to_the_prompt_that_caused_them(self):
        action_log.record_prompt("claude", {"session_id": "s1"}, "restore plugin-creator from git")
        action_log.record_tool("claude", {"session_id": "s1"}, {"tool_name": "Bash", "tool_input": {
            "command": "git checkout -- 001_Architecture/Skills/.system/plugin-creator/"}, "cwd": AO}, "allow")
        report = action_log.who("plugin-creator", log=Path(self.log))
        self.assertIn("git checkout", report)
        self.assertIn("why (last prompt in this session", report)
        self.assertIn("restore plugin-creator from git", report)


    def test_subagent_why_is_frozen_at_its_first_action(self):
        base = {"session_id": "p1", "transcript_path": "/x/p1.jsonl"}
        action_log.record_prompt("claude", base, "investigate the deletion")
        action_log.record_tool("claude", base, {"tool_name": "Agent", "tool_input": {
            "subagent_type": "opus-deep", "description": "Investigate", "prompt": "find who deleted it"}}, "allow")
        sub = dict(base, agent_id="ag1", agent_type="opus-deep")
        action_log.record_tool("claude", sub, {"tool_name": "Bash", "tool_input": {"command": "touch probe-a"}}, "allow")
        action_log.record_prompt("claude", base, "an unrelated later message from Tony")
        action_log.record_tool("claude", sub, {"tool_name": "Bash", "tool_input": {"command": "touch probe-b"}}, "allow")
        report = action_log.who("probe-b", log=Path(self.log))
        self.assertIn("investigate the deletion", report)
        self.assertNotIn("unrelated later message", report)
        self.assertIn("find who deleted it", report)
        self.assertIn("/x/p1/subagents/agent-ag1.jsonl", report)


class DeletionSentinelTests(unittest.TestCase):
    def setUp(self):
        self.log = temp_log()
        self.env = mock.patch.dict(os.environ, {"AGENT_OS_ACTION_LOG": self.log})
        self.env.start()

    def tearDown(self):
        self.env.stop()

    def test_logic_new_and_cleared(self):
        with mock.patch.object(action_log, "tracked_deletions", side_effect=[[], ["a/x.md", "a/y.md"], ["a/y.md"]]):
            self.assertIsNone(action_log.check_deletions("claude", {"session_id": "s"}))  # baseline, nothing missing
            new = action_log.check_deletions("codex", {})
            action_log.check_deletions("claude", {})
        self.assertEqual(new["paths"], ["a/x.md", "a/y.md"])
        events = [(r["event"], r["paths"]) for r in read(self.log)]
        self.assertEqual(events, [("deletion_detected", ["a/x.md", "a/y.md"]), ("deletion_cleared", ["a/x.md"])])
        self.assertIsNotNone(read(self.log)[0]["window_start"])

    def test_git_failure_is_silent(self):
        with mock.patch.object(action_log, "tracked_deletions", return_value=None):
            self.assertIsNone(action_log.check_deletions())
        self.assertEqual(read(self.log), [])

    def test_real_git_repo_without_deleting_any_file(self):
        repo = Path(tempfile.mkdtemp(prefix="action_log_repo_"))
        git = ["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t"]
        subprocess.run(git + ["init", "-q"], check=True)
        (repo / "keep.md").write_text("a")
        (repo / "plugin-creator.md").write_text("b")
        subprocess.run(git + ["add", "."], check=True)
        subprocess.run(git + ["commit", "-qm", "init"], check=True)
        self.assertIsNone(action_log.check_deletions("claude", {}, repo=repo))
        subprocess.run(git + ["rm", "-q", "--cached", "plugin-creator.md"], check=True)  # index only
        self.assertTrue((repo / "plugin-creator.md").exists())
        rec = action_log.check_deletions("codex", {"session_id": "z"}, repo=repo)
        self.assertEqual((rec["paths"], rec["session"]), (["plugin-creator.md"], "z"))
        report = action_log.who("plugin-creator", log=Path(self.log))
        self.assertIn("NO logged agent tool call mentioned this path", report)


if __name__ == "__main__":
    unittest.main()
