import contextlib
import io
import json
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

import route_gate

INFO = {"route": "frontier", "confidence": 0.97, "work_now": 0.9}


class GateTestCase(unittest.TestCase):
    """Every test gets its own state file, log and off-switch path."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        for name, value in (("STATE", self.dir / "state.json"), ("LOG", self.dir / "log.jsonl"),
                            ("OFF_SWITCH", self.dir / "off")):
            p = mock.patch.object(route_gate, name, value)
            p.start()
            self.addCleanup(p.stop)

    def pretool(self, tool, tin, harness="claude", session="s", **extra):
        out, code = route_gate.handle(harness, "pretool", dict({"session_id": session, "tool_name": tool,
                                                                 "tool_input": tin}, **extra))
        self.assertEqual(code, 0)
        if not out:
            return "allow"
        return json.loads(out)["hookSpecificOutput"]["permissionDecision"]

    def stop(self, harness="claude", session="s", **extra):
        out, _ = route_gate.handle(harness, "stop", dict({"session_id": session}, **extra))
        return json.loads(out)["decision"] if out else "allow"

    def logged(self):
        if not route_gate.LOG.exists():
            return []
        return [json.loads(l)["action"] for l in route_gate.LOG.read_text().splitlines()]


class ReadonlyCommandTests(unittest.TestCase):
    def test_reads(self):
        for cmd in ("ls -la", "git status && git log --oneline -5", "cat a.md | head -20", "rg foo 2>/dev/null",
                    "cd 001_Architecture && sed -n 1,40p x.py", "find . -name '*.md'", "wc -l a b 2>&1"):
            self.assertTrue(route_gate.readonly_command(cmd), cmd)

    def test_work(self):
        for cmd in ("echo hi > a.txt", "python3 build.py", "git commit -m x", "sed -i '' s/a/b/ f",
                    "find . -exec touch {} +", "cat <<EOF > f\nx\nEOF", "npm test", "mv a b", "ls; rm x"):
            self.assertFalse(route_gate.readonly_command(cmd), cmd)


class ClassifyTests(unittest.TestCase):
    def test_claude(self):
        c = lambda tool, tin=None: route_gate.classify("claude", tool, tin or {})
        self.assertEqual(c("Agent", {"subagent_type": "opus-deep"}), "delegate")
        self.assertEqual(c("Agent", {"subagent_type": "general-purpose", "model": "opus"}), "delegate")
        self.assertEqual(c("Task", {"subagent_type": "opus-standard"}), "delegate")
        self.assertEqual(c("Agent", {"subagent_type": "Explore"}), "read")
        self.assertEqual(c("Agent", {"subagent_type": "general-purpose"}), "work")
        self.assertEqual(c("SendMessage"), "delegate")
        self.assertEqual(c("AskUserQuestion"), "allow")
        self.assertEqual(c("Skill", {"skill": "superpowers:brainstorming"}), "work")
        self.assertEqual(c("Write", {"file_path": "x"}), "work")
        self.assertEqual(c("mcp__obsidian-mcp-server__obsidian_get_note"), "read")
        self.assertEqual(c("mcp__obsidian-mcp-server__obsidian_write_note"), "work")
        self.assertEqual(c("Bash", {"command": f"python3 {route_gate.FRONTIER_PY} 'x'"}), "delegate")

    def test_codex(self):
        c = lambda tool, tin=None: route_gate.classify("codex", tool, tin or {})
        self.assertEqual(c("apply_patch", {"command": "*** Begin Patch"}), "work")
        self.assertEqual(c("Bash", {"command": ["bash", "-lc", "rg foo"]}), "read")  # list form, shell wrapper unwrapped
        self.assertEqual(c("Bash", {"command": ["bash", "-lc", "rg foo > out.txt"]}), "work")
        self.assertEqual(c("Bash", {"command": "rg foo"}), "read")
        self.assertEqual(c("spawn_agent", {"agent_type": "worker"}), "allow")
        self.assertEqual(c("update_plan"), "allow")

    def test_antigravity(self):
        c = lambda tool, tin=None: route_gate.classify("antigravity", tool, tin or {})
        self.assertEqual(c("replace_file_content"), "work")
        self.assertEqual(c("grep_search"), "read")
        self.assertEqual(c("manage_task"), "allow")
        self.assertEqual(c("run_command", {"CommandLine": "npm run build"}), "work")
        self.assertEqual(c("run_command", {"CommandLine": "git diff"}), "read")


class ClaudeGateTests(GateTestCase):
    def test_nothing_armed_means_nothing_gated(self):
        self.assertEqual(self.pretool("Edit", {"file_path": "x"}), "allow")
        self.assertEqual(self.stop(), "allow")

    def test_enforced_turn_full_cycle(self):
        route_gate.arm_turn("claude", "s", "enforce", INFO)
        self.assertEqual(self.pretool("Write", {"file_path": "x"}), "deny")
        self.assertEqual(self.stop(stop_hook_active=False), "block")
        self.assertEqual(self.stop(stop_hook_active=True), "allow")
        self.assertEqual(self.logged(), ["deny", "stop_block", "stop_violation"])
        self.assertEqual(self.pretool("Write", {"file_path": "x"}), "allow")  # violated turns stop gating

    def test_deny_reason_tells_it_exactly_what_to_do(self):
        route_gate.arm_turn("claude", "s", "enforce", INFO)
        out, _ = route_gate.handle("claude", "pretool", {"session_id": "s", "tool_name": "Edit", "tool_input": {}})
        reason = json.loads(out)["hookSpecificOutput"]["permissionDecisionReason"]
        self.assertTrue(reason.startswith(route_gate.MARKER))
        self.assertIn('subagent_type "opus-standard"', reason)
        self.assertIn("0.97", reason)

    def test_short_clarifying_question_may_end_the_turn(self):
        route_gate.arm_turn("claude", "s", "enforce", INFO)
        self.assertEqual(self.stop(last_assistant_message="Which channel folder should this go in?"), "allow")
        self.assertEqual(self.stop(last_assistant_message="Here is the full design. " * 30 + "Sound good?"), "block")

    def test_running_background_opus_counts_as_delegated(self):
        route_gate.arm_turn("claude", "s", "enforce", INFO)
        tasks = [{"id": "1", "type": "subagent", "status": "running", "description": "x", "agent_type": "opus-deep"}]
        self.assertEqual(self.stop(background_tasks=tasks), "allow")

    def test_stale_turn_and_off_switch_release_the_gate(self):
        route_gate.arm_turn("claude", "s", "enforce", INFO)
        route_gate.update_turn("claude", "s", t=time.time() - route_gate.TURN_TTL - 5)
        self.assertEqual(self.pretool("Edit", {}), "allow")
        route_gate.arm_turn("claude", "s", "enforce", INFO)
        route_gate.OFF_SWITCH.write_text("")
        self.assertEqual(self.pretool("Edit", {}), "allow")

    def test_delegated_worker_is_never_gated(self):
        route_gate.arm_turn("claude", "s", "enforce", INFO)
        with mock.patch.dict("os.environ", {"AGENT_OS_DELEGATE_WORKER": "1"}):
            self.assertEqual(self.pretool("Edit", {}), "allow")

    def test_sessions_are_independent(self):
        route_gate.arm_turn("claude", "a", "enforce", INFO)
        self.assertEqual(self.pretool("Edit", {}, session="b"), "allow")
        self.assertEqual(self.pretool("Edit", {}, session="a"), "deny")

    def test_new_turn_resets_budget_and_delegation(self):
        route_gate.arm_turn("claude", "s", "enforce", INFO)
        self.assertEqual(self.pretool("Agent", {"subagent_type": "opus-standard"}), "allow")
        route_gate.arm_turn("claude", "s", "enforce", INFO)
        self.assertEqual(self.pretool("Edit", {}), "deny")


class CodexTests(GateTestCase):
    def test_only_frontier_subagents_open_the_gate(self):
        route_gate.arm_turn("codex", "c", "enforce", INFO)
        route_gate.handle("codex", "subagent-start", {"session_id": "c", "agent_type": "default"})
        self.assertEqual(self.pretool("apply_patch", {"command": "x"}, harness="codex", session="c"), "deny")
        route_gate.handle("codex", "subagent-start", {"session_id": "c", "agent_type": "sol-deep"})
        self.assertEqual(self.pretool("apply_patch", {"command": "x"}, harness="codex", session="c"), "allow")

    def test_stop_block_shape(self):
        route_gate.arm_turn("codex", "c", "enforce", INFO)
        out, _ = route_gate.handle("codex", "stop", {"session_id": "c", "stop_hook_active": False})
        d = json.loads(out)
        self.assertEqual(d["decision"], "block")
        self.assertIn("sol-standard", d["reason"])


class AntigravityTests(GateTestCase):
    def ag(self, name, args):
        out, _ = route_gate.handle("antigravity", "pretool", {"conversationId": "g", "toolCall": {"name": name, "args": args}})
        return json.loads(out)["decision"] if out else "allow"

    def test_deny_shape_and_frontier_py(self):
        route_gate.arm_turn("antigravity", "g", "enforce", INFO)
        self.assertEqual(self.ag("write_to_file", {"TargetFile": "x"}), "deny")
        self.assertEqual(self.ag("run_command", {"CommandLine": f"python3 {route_gate.FRONTIER_PY} 'task' --deep"}), "allow")
        self.assertEqual(self.ag("write_to_file", {"TargetFile": "x"}), "allow")

    def test_stop_only_on_model_stop(self):
        route_gate.arm_turn("antigravity", "g", "enforce", INFO)
        out, _ = route_gate.handle("antigravity", "stop", {"conversationId": "g", "terminationReason": "error"})
        self.assertEqual(out, "")
        out, _ = route_gate.handle("antigravity", "stop", {"conversationId": "g", "terminationReason": "model_stop"})
        self.assertEqual(json.loads(out)["decision"], "continue")

    def test_malformed_payload_is_ignored(self):
        route_gate.arm_turn("antigravity", "g", "enforce", INFO)
        for payload in ({"conversationId": "g", "toolCall": "nope"}, {"conversationId": "g"}, [], "x"):
            self.assertEqual(route_gate.handle("antigravity", "pretool", payload), ("", 0), payload)


class GeminiTests(GateTestCase):
    def test_model_swap_shape_and_single_log_line(self):
        route_gate.arm_turn("gemini", "m", "enforce", INFO)
        for _ in range(3):  # BeforeModel fires on every model call in the turn
            out, _ = route_gate.handle("gemini", "before-model", {"session_id": "m"})
            self.assertEqual(json.loads(out)["hookSpecificOutput"]["llm_request"], {"model": "pro"})
        self.assertEqual(self.logged(), ["model_swap"])

    def test_advise_turn_keeps_flash(self):
        route_gate.arm_turn("gemini", "m", "advise", INFO)
        self.assertEqual(route_gate.handle("gemini", "before-model", {"session_id": "m"})[0], "")


class RobustnessTests(GateTestCase):
    def test_corrupt_state_file_fails_open_and_recovers(self):
        route_gate.STATE.write_text("{not json")
        self.assertEqual(self.pretool("Edit", {}), "allow")
        route_gate.arm_turn("claude", "s", "enforce", INFO)
        self.assertEqual(self.pretool("Edit", {}), "deny")

    def test_state_is_pruned(self):
        with mock.patch.object(route_gate, "MAX_SESSIONS", 3):
            for i in range(6):
                route_gate.arm_turn("claude", f"s{i}", "enforce", INFO)
        self.assertEqual(len(json.loads(route_gate.STATE.read_text())), 3)

    def test_unknown_event_and_bad_stdin(self):
        self.assertEqual(route_gate.handle("claude", "nope", {}), ("", 0))
        out = io.StringIO()
        with mock.patch.object(route_gate.sys, "stdin", io.StringIO("not json")), contextlib.redirect_stdout(out):
            self.assertEqual(route_gate.main(), 0)
        self.assertEqual(out.getvalue(), "")

    def test_self_test_passes(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(route_gate.self_test(), 0, out.getvalue())


if __name__ == "__main__":
    unittest.main()
