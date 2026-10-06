"""Tests for lab_build_gemini.py. Pure parts and the real SDK policy hook run offline; the Live*
class drives the whole state machine on a throwaway git repo with the real codex sandbox and a
local fake model (via lab_build.py's own fakes) and a scripted stand-in for the Gemini agent.
Nothing here calls Gemini or OpenRouter, spends money, or touches 001_Architecture/Lab/."""
import asyncio
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import delegate
import lab_build as B
import lab_build_gemini as X
import test_lab_build as TB  # its repo/project fixtures, reused

B.L.log_event = lambda event: None  # never write test runs into Tony's calibration log
HAVE_CODEX = shutil.which("codex") is not None
try:
    from google.antigravity.hooks import policy as P
    from google.antigravity.types import Text, ToolCall, UsageMetadata
    HAVE_SDK = True
except ImportError:
    HAVE_SDK = False


def good_audit(points=5, cite="print(len(sys.argv[1].split()))"):
    return {"items": [{"id": r, "points": points, "cite_file": "word_count.py", "cite_text": cite, "why": "w"}
                      for r in B.RUBRIC],
            "failures_to_fix": ["C05 expects 99"], "fix_would_exceed_third": False}


class PureTests(unittest.TestCase):
    def test_worst_cases_and_each_stage_alone_fits_the_cap(self):
        self.assertEqual(X.worst_case_usd("audit"), 1.16)
        for s in X.BUDGETS:
            self.assertLess(X.worst_case_usd(s), B.L.PROJECT_CAP_USD)

    def test_audit_shape(self):
        self.assertEqual(X.audit_problems(good_audit()), [])
        bad = good_audit()
        bad["items"] = bad["items"][:4]
        self.assertIn("rubric item R5 missing", X.audit_problems(bad))
        for field, val in (("points", 6), ("points", True), ("cite_text", "short"), ("cite_file", ""), ("why", "")):
            doc = good_audit()
            doc["items"][0][field] = val
            self.assertTrue(X.audit_problems(doc), (field, val))
        self.assertTrue(X.audit_problems(dict(good_audit(), fix_would_exceed_third="no")))
        self.assertTrue(X.audit_problems(dict(good_audit(), failures_to_fix="x")))
        self.assertTrue(X.audit_problems({"score": 3}))

    def test_audit_doc_keeps_only_rubric_items_and_records_the_reviewer(self):
        reply = good_audit()
        reply["items"].append({"id": "R9", "points": 5})
        doc = X.audit_doc(reply, "gemini-x", 2)
        self.assertEqual([i["id"] for i in doc["items"]], list(B.RUBRIC))
        self.assertEqual((doc["scored_by"], doc["attempt"]), ("gemini-x", 2))
        self.assertIn("antigravity", doc["harness"])

    def test_write_targets(self):
        with tempfile.TemporaryDirectory() as d:
            bd = Path(d) / "Build"
            (bd / "sub").mkdir(parents=True)
            (bd / "a.py").write_text("x\n")
            os.symlink(Path(d) / "elsewhere.txt", bd / "link.txt")
            ok = X.write_target_ok
            self.assertTrue(ok(str(bd / "new.py"), str(bd)))
            self.assertTrue(ok(str(bd / "a.py"), str(bd)))
            self.assertTrue(ok(str(bd / "sub" / "b.py"), str(bd)))               # existing subfolder
            self.assertTrue(ok(f"file://{bd}/c.py", str(bd)))
            self.assertTrue(ok(str(bd / "secret_scan.py"), str(bd)))             # a real build file name
            self.assertFalse(ok(str(bd / "newdir" / "x.py"), str(bd)))           # no new subfolders
            self.assertFalse(ok("new.py", str(bd)))                              # relative
            self.assertFalse(ok(str(bd), str(bd)))                               # the folder itself
            self.assertFalse(ok(str(bd / ".." / "out.py"), str(bd)))
            self.assertFalse(ok(str(Path(d) / "Build2" / "x.py"), str(bd)))      # sibling with a shared prefix
            self.assertFalse(ok(str(bd / "link.txt"), str(bd)))                  # a link
            self.assertFalse(ok(str(bd / ".env"), str(bd)))
            self.assertFalse(X.write_args_ok({"Content": "x"}, str(bd)))         # no path named = refused
            self.assertFalse(X.write_args_ok({"TargetFile": str(bd / "a.py"), "other_path": "/etc/x"}, str(bd)))

    def test_reads(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertTrue(X.read_ok(f"{X.AGENT_OS}/TOOLBOX.md", None))
            self.assertFalse(X.read_ok(os.path.expanduser("~/.env-secrets"), None))
            self.assertFalse(X.read_ok("/etc/hosts", d))
            inside = f"{X.AGENT_OS}/001_Architecture/Lab/P/Build_Worktree_1/Tools/T"
            self.assertFalse(X.read_ok(f"{inside}/secret_scan.py", None))       # lab_plan_gemini's wide rule
            self.assertTrue(X.read_ok(f"{inside}/secret_scan.py", inside))      # widened for the build only
            self.assertFalse(X.read_ok(f"{inside}/.env", inside))

    def test_spend_records(self):
        gm = {"stages": [{"stage": "audit", "attempt": 1, "ok": True, "cost_usd_list_price": 0.3},
                         {"stage": "fix", "attempt": 1, "ok": False}]}
        self.assertEqual(X.gemini_spent(gm), 0.3)
        self.assertTrue(X.stage_done(gm, "audit", 1))
        self.assertFalse(X.stage_done(gm, "fix", 1))
        with tempfile.TemporaryDirectory() as d:
            log = Path(d) / "lab.jsonl"
            log.write_text("\n".join(json.dumps(e) for e in (
                {"event": "review", "harness": "antigravity", "project": "P", "ok": True, "cost_usd": 0.31},
                {"event": "review", "harness": "antigravity", "project": "Q", "ok": True, "cost_usd": 9},
                {"event": "review", "harness": "antigravity", "project": "P", "ok": False},
                {"event": "draft", "project": "P", "cost_usd": 5})) + "\nnot json\n")
            self.assertEqual(X.plan_review_spent("P", log), 0.31)
            self.assertEqual(X.plan_review_spent("P", Path(d) / "missing"), 0.0)


class NextActionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.proj = Path(self.tmp.name)

    def tearDown(self):
        for p in self.proj.rglob("*"):
            os.chmod(p, 0o755 if p.is_dir() else 0o644)
        self.tmp.cleanup()

    def na(self, meta, verdicts=None, gm=None):
        return X.next_action(self.proj, meta, verdicts or {"history": []}, gm or {"stages": []})[0]

    def test_walk(self):
        w1 = {"attempt": 1, "scores": {}}
        self.assertEqual(self.na({}), "build")
        self.assertEqual(self.na({"worktrees": [w1]}), "build_failed")
        (self.proj / "Build_Score.json").write_text(json.dumps({"verdict": "containment_stop"}))
        self.assertEqual(self.na({"worktrees": [w1]}), "containment_stop")
        w1["scores"] = {"raw": {"file": "Build_Score.json"}}
        self.assertEqual(self.na({"worktrees": [w1]}), "audit")
        (self.proj / "Build_Audit.json").write_text("{}")
        self.assertEqual(self.na({"worktrees": [w1]}), "finalize")
        raw = {"attempt": 1, "stage": "raw", "next": "fix_round"}
        v = {"history": [raw], "current": raw}
        self.assertEqual(self.na({"worktrees": [w1]}, v), "fix")
        self.assertEqual(self.na({"worktrees": [w1]}, v, {"stages": [{"stage": "fix", "attempt": 1, "ok": True}]}),
                         "after_fix")
        fix = {"attempt": 1, "stage": "fix", "next": "rebuild"}
        v = {"history": [raw, fix], "current": fix}
        self.assertEqual(self.na({"worktrees": [w1]}, v), "rebuild_prep")
        w2 = {"attempt": 2, "scores": {}}
        self.assertEqual(self.na({"worktrees": [w1, w2]}, v), "rebuild")
        self.assertEqual(self.na({"worktrees": [w1, w2]}, v, {"stages": [{"stage": "rebuild", "attempt": 2, "ok": True}]}),
                         "score_rebuild")
        w2["scores"] = {"raw": {"file": "Build_Score_Rebuild.json"}}
        self.assertEqual(self.na({"worktrees": [w1, w2]}, v), "audit")
        for nxt in ("lab_run", "stop"):
            end = {"attempt": 2, "stage": "raw", "next": nxt}
            self.assertEqual(self.na({"worktrees": [w1, w2]}, {"history": [raw, fix, end], "current": end}), "done")


@unittest.skipUnless(HAVE_SDK, "google-antigravity SDK not installed")
class PolicyTests(unittest.TestCase):
    """The REAL SDK policy hook, built from the real config: free, no model involved."""

    def decide(self, cfg, name, args):
        hook = P.enforce(cfg.policies)
        res = asyncio.run(hook.run(None, ToolCall(name=name, args=args, id="1")))
        return res.allow

    def test_writer_policy(self):
        with tempfile.TemporaryDirectory() as d:
            bd = str(Path(d) / "Build")
            os.mkdir(bd)
            tool = X.make_check_tool(Path(d), bd, {"n": 0})
            cfg = X.make_config("k", "m", "s", X.BUDGETS["fix"], write_root=bd, read_root=bd, tools=(tool,))
            self.assertTrue(self.decide(cfg, "create_file", {"TargetFile": f"{bd}/a.py", "CodeContent": "x"}))
            self.assertTrue(self.decide(cfg, "edit_file", {"TargetFile": f"{bd}/a.py"}))
            self.assertFalse(self.decide(cfg, "create_file", {"TargetFile": f"{X.AGENT_OS}/TOOLBOX.md"}))
            self.assertFalse(self.decide(cfg, "create_file", {"TargetFile": f"{bd}/new_dir/a.py"}))
            self.assertFalse(self.decide(cfg, "create_file", {"CodeContent": "no path"}))
            self.assertFalse(self.decide(cfg, "run_command", {"CommandLine": "ls"}))
            self.assertFalse(self.decide(cfg, "search_web", {"query": "x"}))
            self.assertFalse(self.decide(cfg, "view_file", {"path": os.path.expanduser("~/.env-secrets")}))
            self.assertTrue(self.decide(cfg, "view_file", {"path": f"{X.AGENT_OS}/TOOLBOX.md"}))
            self.assertTrue(self.decide(cfg, "run_acceptance_checks", {}))

    def test_auditor_cannot_write_at_all(self):
        with tempfile.TemporaryDirectory() as d:
            cfg = X.make_config("k", "m", "s", X.BUDGETS["audit"], read_root=d)
            self.assertFalse(self.decide(cfg, "create_file", {"TargetFile": f"{d}/a.py"}))
            self.assertFalse(self.decide(cfg, "edit_file", {"TargetFile": f"{d}/a.py"}))
            self.assertEqual([t.value for t in cfg.capabilities.enabled_tools],
                             ["view_file", "list_directory", "search_directory", "find_file"])

    def test_check_tool_has_a_call_limit(self):
        with tempfile.TemporaryDirectory() as d:
            tool = X.make_check_tool(Path(d), d, {"n": X.MAX_CHECK_RUNS})
            self.assertIn("refused", asyncio.run(tool()))


class CliTests(unittest.TestCase):
    def test_refuses_inside_worker(self):
        os.environ["AGENT_OS_DELEGATE_WORKER"] = "1"
        try:
            self.assertEqual(X.main(["anything"]), 3)
        finally:
            del os.environ["AGENT_OS_DELEGATE_WORKER"]

    def test_bad_flags(self):
        self.assertEqual(X.main(["--cap"]), 1)
        self.assertEqual(X.main(["a", "b"]), 1)


# ---------------------------------------------------------------- the whole state machine

class FakeAgent:
    """Stands in for google.antigravity.Agent: same chat()/chunks/conversation shape, so the real
    lab_plan_gemini.ask/ask_valid run unchanged. Each reply is text or fn(prompt) -> text."""

    def __init__(self, cfg, replies):
        self.cfg, self.replies, self.prompts = cfg, list(replies), []
        self.conversation = SimpleNamespace(total_usage=UsageMetadata(
            prompt_token_count=1000, cached_content_token_count=0, candidates_token_count=100,
            thoughts_token_count=0, total_token_count=1100))

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    async def chat(self, prompt):
        self.prompts.append(prompt)
        r = self.replies.pop(0)
        text = r(prompt) if callable(r) else r

        async def gen():
            yield Text(step_index=0, text=text)
        return SimpleNamespace(chunks=gen(), stop_reason=None)


@unittest.skipUnless(HAVE_CODEX and HAVE_SDK, "codex CLI or google-antigravity SDK not installed")
class LiveDriveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.repo = root / "repo"
        TB.make_repo(self.repo)
        self.proj = TB.make_project(root)
        self.servers = delegate.mcp_server_names()
        base = B.git(self.repo, "rev-parse", "HEAD").strip()
        meta = {"project_dir": str(self.proj), "into": "Tools/Word_Tool", "worktrees": []}
        w = B.new_worktree(self.proj, meta, self.repo, base, "Tools/Word_Tool")
        w.update({"attempt": 1, "built_by": "fake-model", "cost_usd": 0.25})
        meta["worktrees"].append(w)
        rc, _, _ = B.run_fake_build(TB.BUILD_SCRIPT, w["build_dir"], self.servers)
        self.assertEqual(rc, 0)
        code, _ = B.score_stage(self.proj, meta, w, 1, "raw", "fake-model", self.servers, run_preflight=False)
        self.assertEqual(code, 0)
        B.write_json(self.proj / "Build_Meta.json", meta)
        logs = root / "logs"
        logs.mkdir()
        self.saved = (X.open_log, X.plan_review_spent)
        X.open_log = lambda stamp, prefix: (logs / f"{prefix}-{stamp}.log", "", open(logs / f"{prefix}-{stamp}.log", "w"))
        X.plan_review_spent = lambda project, log_path=None: 0.0
        self.agents = []

    def tearDown(self):
        X.open_log, X.plan_review_spent = self.saved
        subprocess.run(["git", "-C", str(self.repo), "worktree", "prune"], capture_output=True)
        for p in self.proj.rglob("*"):
            if p.is_file() and not p.is_symlink():
                os.chmod(p, 0o644)
        self.tmp.cleanup()

    def factory(self, scripts):
        def make(cfg):
            a = FakeAgent(cfg, scripts.pop(0))
            self.agents.append(a)
            return a
        return make

    def build_dir(self):
        return Path(B._current(B._meta(self.proj))["build_dir"])

    def test_cleared_on_first_audit(self):
        scripts = [[json.dumps(good_audit(5)), "The build does what the plan says; C05 is impossible."]]
        rc = X.drive(self.proj, None, None, 100.0, "gemini-test", "k", factory=self.factory(scripts),
                     repo=str(self.repo))
        self.assertEqual(rc, 0)
        v = json.loads((self.proj / "Build_Verdict.json").read_text())["current"]
        self.assertEqual((v["total"], v["next"]), (88.0, "lab_run"))
        audit = json.loads((self.proj / "Build_Audit.json").read_text())
        self.assertEqual(audit["scored_by"], "gemini-test")
        gm = json.loads((self.proj / X.GEMINI_META).read_text())
        self.assertEqual([(s["stage"], s["attempt"], s["ok"]) for s in gm["stages"]], [("audit", 1, True)])
        self.assertGreater(gm["stages"][0]["cost_usd_list_price"], 0)
        # the auditor got a config with no write tools at all
        self.assertNotIn("create_file", [t.value for t in self.agents[0].cfg.capabilities.enabled_tools])
        self.assertEqual(X.drive(self.proj, None, None, 100.0, "gemini-test", "k", factory=self.factory([]),
                                 repo=str(self.repo)), 0)  # rerun = nothing left to do, no new agent

    def test_full_walk_audit_fix_rebuild_audit_stop(self):
        def fix(prompt):
            self.assertIn("C05 expects 99", prompt)
            (self.build_dir() / "README.md").write_text(TB.README + "One more line.\n")
            return "- README.md: one line added"

        def rebuild(prompt):
            bd = self.build_dir()
            self.assertIn(str(bd), prompt)
            (bd / "word_count.py").write_text("import sys\nprint(len(sys.argv[1].split()))\n")
            return "- word_count.py"
        scripts = [[json.dumps(good_audit(2)), "Review text, attempt one, long enough."],
                   [fix],
                   [rebuild],
                   [json.dumps(good_audit(2)), "Rebuild review text, long enough to keep."]]
        rc = X.drive(self.proj, None, None, 100.0, "gemini-test", "k", factory=self.factory(scripts),
                     repo=str(self.repo))
        self.assertEqual(rc, 0)
        verdicts = json.loads((self.proj / "Build_Verdict.json").read_text())
        self.assertEqual([(h["attempt"], h["stage"], h["next"]) for h in verdicts["history"]],
                         [(1, "raw", "fix_round"), (1, "fix", "rebuild"), (2, "raw", "stop")])
        gm = json.loads((self.proj / X.GEMINI_META).read_text())
        self.assertEqual([(s["stage"], s["attempt"]) for s in gm["stages"]],
                         [("audit", 1), ("fix", 1), ("rebuild", 2), ("audit", 2)])
        review = (self.proj / "Build_Review.md").read_text()
        for heading in ("## Fix Round (Gemini, gemini-test)", "## Rebuild (Gemini, gemini-test)",
                        "## Rebuild Audit (Gemini, gemini-test)"):
            self.assertIn(heading, review)
        meta = json.loads((self.proj / "Build_Meta.json").read_text())
        self.assertIn("gemini-test (rebuild", meta["worktrees"][-1]["built_by"])
        self.assertTrue(Path(meta["worktrees"][0]["worktree"]).is_dir())         # old worktree kept
        self.assertEqual(len(self.agents), 4)                                    # a NEW agent per stage
        self.assertTrue(all(not a.replies for a in self.agents))

    def test_spend_gate_stops_before_any_gemini_call(self):
        B.write_json(self.proj / "Draft_Meta.json", {"token_cost_usd": 0.5})
        rc = X.drive(self.proj, None, None, 1.5, "gemini-test", "k", factory=self.factory([]), repo=str(self.repo))
        self.assertEqual(rc, 5)                                   # 0.5 plan + 0.25 build + 1.16 audit > 1.5
        self.assertEqual(self.agents, [])
        self.assertFalse((self.proj / "Build_Audit.json").exists())

    def test_malformed_audit_gets_one_correction_then_fails_cleanly(self):
        scripts = [["not json", "still not json"]]
        rc = X.drive(self.proj, None, None, 100.0, "gemini-test", "k", factory=self.factory(scripts),
                     repo=str(self.repo))
        self.assertEqual(rc, 10)
        self.assertFalse((self.proj / "Build_Audit.json").exists())
        gm = json.loads((self.proj / X.GEMINI_META).read_text())
        self.assertFalse(gm["stages"][0]["ok"])
        self.assertTrue(re.search(r"still invalid", gm["stages"][0]["error"]))


if __name__ == "__main__":
    unittest.main()
