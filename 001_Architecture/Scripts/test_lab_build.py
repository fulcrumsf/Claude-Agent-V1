"""Tests for lab_build.py. Pure parts run anywhere; the Live* classes run the real codex sandbox
against a local fake model and a throwaway git repo in the temp folder. Nothing here calls
OpenRouter or spends money, and nothing touches 001_Architecture/Lab/."""
import contextlib
import io
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import delegate
import lab_build as B

B.L.log_event = lambda event: None  # never write test runs into Tony's calibration log
REAL_CHECKS = Path(delegate.AGENT_OS) / "001_Architecture" / "Lab" / \
    "2026-10-02_Design_Universal_Pipeline_Agnostic_Logging_Grading" / "Acceptance_Checks.json"
HAVE_CODEX = shutil.which("codex") is not None


# ---------------------------------------------------------------- containment (pure)

class ContainmentRuleTests(unittest.TestCase):
    REL = "Tools/Word_Tool"

    def v(self, diff=(), status=(), kinds=None, link=False):
        return B.containment_violations(list(diff), list(status), self.REL, kinds or {}, link)

    def test_new_files_inside_are_fine(self):
        self.assertEqual(self.v(status=[("??", "Tools/Word_Tool/a.py"), ("!!", "Tools/Word_Tool/__pycache__/")],
                                kinds={"a.py": "file"}), [])
        self.assertEqual(self.v(diff=[("A", "Tools/Word_Tool/a.py")]), [])

    def test_edit_to_existing_file_is_a_violation(self):
        out = self.v(diff=[("M", "Tools/README.md")])
        self.assertTrue(any("edited an existing file" in x for x in out))

    def test_write_outside_folder_is_a_violation(self):
        for status in (("??", "Tools/Other/x.py"), ("!!", "000_Ingest/x.md"), ("??", "Tools/Word_Tool2/x")):
            self.assertTrue(any("outside the approved folder" in x for x in self.v(status=[status])), status)
        self.assertTrue(any("outside" in x for x in self.v(diff=[("A", "TOOLBOX_2.md")])))

    def test_delete_rename_typechange_are_violations(self):
        for code, word in (("D", "deleted"), ("R", "renamed"), ("T", "type")):
            self.assertTrue(any(word in x for x in self.v(diff=[(code, "Tools/README.md")])), code)
        self.assertTrue(any("deleted a file inside" in x
                            for x in self.v(status=[(" D", "Tools/Word_Tool/a.py")])))

    def test_links_inside_folder_are_violations(self):
        for kind in ("symlink", "hardlink", "other"):
            self.assertTrue(any(kind in x for x in self.v(kinds={"x": kind})), kind)
        self.assertTrue(self.v(link=True))


class ContainmentGitTests(unittest.TestCase):
    """Real git worktree in a temp repo; the mechanical check, not a model, finds each problem."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        make_repo(self.repo)
        self.base = B.git(self.repo, "rev-parse", "HEAD").strip()
        # Same layout as the real Agent-OS: Google Drive's upload staging folder sits in an ancestor
        # of the worktree. old_staged plays a staged copy of a file that existed before the build.
        self.stage = Path(self.tmp.name) / B.DRIVE_STAGING
        self.stage.mkdir()
        (self.stage / "old_staged").write_text("Tony's older file\n")
        self.wt = Path(self.tmp.name) / "Build_Worktree_1"
        B.make_worktree(self.repo, self.wt, "lab/test/wt1", self.base)
        (self.wt / "Tools" / "Word_Tool").mkdir()

    def tearDown(self):
        subprocess.run(["git", "-C", str(self.repo), "worktree", "prune"], capture_output=True)
        self.tmp.cleanup()

    def check(self):
        return B.check_containment(self.wt, self.base, "Tools/Word_Tool")

    def test_clean_new_files(self):
        (self.wt / "Tools/Word_Tool/word_count.py").write_text("print(1)\n")
        r = self.check()
        self.assertTrue(r["ok"], r)
        self.assertEqual(r["new_files"], ["word_count.py"])

    def test_edit_existing_file_caught(self):
        (self.wt / "Tools/README.md").write_text("changed\n")
        r = self.check()
        self.assertFalse(r["ok"])
        self.assertTrue(any("edited an existing file" in x and "Tools/README.md" in x for x in r["violations"]))

    def test_new_file_outside_caught(self):
        (self.wt / "Tools/Sneaky.md").write_text("x\n")
        self.assertTrue(any("outside" in x for x in self.check()["violations"]))

    def test_ignored_file_outside_caught(self):
        (self.wt / "Tools" / "cache.pyc").write_bytes(b"x")  # gitignored, still outside the folder
        self.assertTrue(any("cache.pyc" in x for x in self.check()["violations"]))

    def test_delete_caught(self):
        (self.wt / "Tools/README.md").unlink()
        self.assertTrue(any("deleted" in x for x in self.check()["violations"]))

    def test_symlink_inside_caught(self):
        os.symlink(self.wt / "Tools/README.md", self.wt / "Tools/Word_Tool/link.md")
        self.assertTrue(any("symlink" in x for x in self.check()["violations"]))

    # Regression 2026-10-03: Google Drive hard-links every new file into .tmp.driveupload while it
    # uploads, so a real run flagged all 23 new files (pycache too) as hardlinks.
    def test_drive_upload_links_on_new_files_are_not_violations(self):
        tool = self.wt / "Tools/Word_Tool"
        (tool / "word_count.py").write_text("print(1)\n")
        (tool / "__pycache__").mkdir()
        (tool / "__pycache__/word_count.cpython-313.pyc").write_bytes(b"\x00pyc")
        os.link(tool / "word_count.py", self.stage / "1383245")
        os.link(tool / "__pycache__/word_count.cpython-313.pyc", self.stage / "1383247")
        self.assertEqual((tool / "word_count.py").stat().st_nlink, 2)  # really a 2-link file, as on disk
        r = self.check()
        self.assertTrue(r["ok"], r)
        self.assertEqual(r["new_files"], ["word_count.py"])
        self.assertIn("word_count.py", B.manifest(tool))  # the tamper check must still see it

    def test_hardlink_to_existing_file_still_caught_even_if_drive_stages_it(self):
        tool = self.wt / "Tools/Word_Tool"
        os.link(self.wt / "Tools/README.md", tool / "readme_copy.md")
        os.link(tool / "readme_copy.md", self.stage / "999")  # Drive staging it too: 3 links
        self.assertTrue(any("hardlink" in x and "readme_copy.md" in x for x in self.check()["violations"]))

    def test_hardlink_to_pre_build_file_known_only_to_drive_still_caught(self):
        os.link(self.stage / "old_staged", self.wt / "Tools/Word_Tool/old.md")  # born before the worktree
        self.assertTrue(any("hardlink" in x and "old.md" in x for x in self.check()["violations"]))

    def test_hardlink_outside_worktree_still_caught(self):
        outside = Path(self.tmp.name) / "secret.txt"
        outside.write_text("x\n")
        os.link(outside, self.wt / "Tools/Word_Tool/secret.txt")
        self.assertTrue(any("hardlink" in x for x in self.check()["violations"]))

    def test_hardlink_between_two_new_files_still_caught(self):
        tool = self.wt / "Tools/Word_Tool"
        (tool / "a.py").write_text("x\n")
        os.link(tool / "a.py", tool / "b.py")
        out = self.check()["violations"]
        self.assertTrue(any("hardlink" in x and "a.py" in x for x in out), out)

    def test_after_commit_new_files_still_ok_and_fix_edits_inside_ok(self):
        f = self.wt / "Tools/Word_Tool/word_count.py"
        f.write_text("print(1)\n")
        B.commit_build(self.wt, "Tools/Word_Tool", "raw")
        f.write_text("print(2)\n")  # a fix round editing its own folder
        self.assertTrue(self.check()["ok"])


# ---------------------------------------------------------------- scoring math

def res(tier, passed):
    return {"id": "C", "tier": tier, "passed": passed}


class ScoreMathTests(unittest.TestCase):
    def test_all_pass_is_75(self):
        p = B.mechanical_points([res(0, True), res(1, True), res(2, True)], True)
        self.assertEqual(p, {"acceptance_60": 60.0, "tier0_15": 15, "non_model_75": 75.0})

    def test_tier0_floor_is_all_or_nothing(self):
        p = B.mechanical_points([res(0, False), res(1, True), res(2, True), res(2, True)], True)
        self.assertEqual((p["acceptance_60"], p["tier0_15"]), (45.0, 0))

    def test_containment_failure_scores_zero(self):
        self.assertEqual(B.mechanical_points([res(0, True)], False)["non_model_75"], 0.0)

    def test_audit_capped_at_25(self):
        self.assertEqual(B.combine(60, 40)["audit_25"], 25.0)
        self.assertEqual(B.combine(60, -3)["audit_25"], 0.0)

    def test_model_points_alone_can_never_clear(self):
        self.assertFalse(B.combine(54.9, 25)["cleared"])   # 79.9
        self.assertFalse(B.combine(54, 100)["cleared"])    # audit capped: 79
        self.assertTrue(B.combine(55, 25)["cleared"])      # 80, and 55 of 75 non-model
        self.assertFalse(B.combine(75, 4)["cleared"])      # 79
        # The guard is explicit too, not just a side effect of the cap:
        self.assertNotEqual(B.next_step(85, 50, stage="raw", fix_used=False, rebuild_used=False,
                                        has_failures=True), "lab_run")


class NextStepTests(unittest.TestCase):
    def n(self, total, non_model=None, **kw):
        base = dict(stage="raw", fix_used=False, rebuild_used=False, has_failures=True)
        base.update(kw)
        return B.next_step(total, total - 20 if non_model is None else non_model, **base)

    def test_raw_branches(self):
        self.assertEqual(self.n(85), "lab_run")
        self.assertEqual(self.n(65), "fix_round")
        self.assertEqual(self.n(50), "fix_round")
        self.assertEqual(self.n(49), "rebuild")
        self.assertEqual(self.n(65, has_failures=False), "rebuild")       # nothing named to fix
        self.assertEqual(self.n(65, fix_judged_too_big=True), "rebuild")  # fix would be > 1/3

    def test_one_fix_one_rebuild_cap(self):
        self.assertEqual(self.n(65, fix_used=True), "rebuild")
        self.assertEqual(self.n(65, fix_used=True, rebuild_used=True), "stop")
        self.assertEqual(self.n(40, rebuild_used=True), "stop")
        self.assertEqual(self.n(65, rebuild_used=True), "fix_round")      # rebuild came first, fix unused

    def test_after_fix(self):
        self.assertEqual(self.n(85, stage="fix", fix_used=True, fix_ratio_value=0.1), "lab_run")
        self.assertEqual(self.n(70, stage="fix", fix_used=True, fix_ratio_value=0.1), "rebuild")
        self.assertEqual(self.n(70, stage="fix", fix_used=True, rebuild_used=True, fix_ratio_value=0.1), "stop")
        self.assertEqual(self.n(95, stage="fix", fix_used=True, fix_ratio_value=0.5), "rebuild")
        self.assertEqual(self.n(95, stage="fix", fix_used=True, rebuild_used=True, fix_ratio_value=0.5), "stop")

    def test_worst_case_walk_never_exceeds_cap(self):
        fix_used = rebuild_used = False
        steps, stage = [], "raw"
        for _ in range(10):  # every score is a failing 60 with named failures
            nxt = B.next_step(60, 45, stage=stage, fix_used=fix_used, rebuild_used=rebuild_used, has_failures=True)
            steps.append(nxt)
            if nxt == "fix_round":
                fix_used, stage = True, "fix"
            elif nxt == "rebuild":
                rebuild_used, stage = True, "raw"
            else:
                break
        self.assertEqual(steps, ["fix_round", "rebuild", "stop"])

    def test_fix_ratio(self):
        raw = [(90, 0, "a.py"), (10, 0, "b.md"), (500, 0, "x/__pycache__/a.pyc")]
        self.assertEqual(B.fix_ratio(raw, [(5, 5, "a.py")]), 0.05)
        self.assertEqual(B.fix_ratio(raw, [(40, 10, "a.py")]), 0.4)
        self.assertEqual(B.fix_ratio([], []), 0.0)


# ---------------------------------------------------------------- audit citations

class AuditPointsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.bd = Path(self.tmp.name) / "Word_Tool"
        self.bd.mkdir()
        (self.bd / "word_count.py").write_text("import sys\nprint(len(sys.argv[1].split()))\n")
        (Path(self.tmp.name) / "secret.txt").write_text("print(len(sys.argv[1].split()))\n")
        self.score = {"checks": [{"output_tail": "Ran 4 tests in 0.01s\nOK"}]}

    def tearDown(self):
        self.tmp.cleanup()

    def items(self, **over):
        base = {rid: {"id": rid, "points": 5, "cite_file": "word_count.py",
                      "cite_text": "print(len(sys.argv[1].split()))", "why": "w"} for rid in B.RUBRIC}
        for rid, patch in over.items():
            base[rid].update(patch)
        return {"items": list(base.values())}

    def test_fully_cited_scores_25(self):
        pts, items, problems = B.audit_points(self.items(), self.bd, self.score, "Build_Score.json")
        self.assertEqual((pts, problems), (25.0, []))

    def test_uncited_or_fake_quote_scores_zero(self):
        pts, items, _ = B.audit_points(self.items(R1={"cite_text": "this line is not in the file"},
                                                  R2={"cite_text": "print("},          # too short
                                                  R3={"cite_file": "../secret.txt"},   # outside build
                                                  R4={"cite_file": ""}), self.bd, self.score, "Build_Score.json")
        self.assertEqual(pts, 5.0)
        self.assertEqual([i["cited"] for i in items], [False, False, False, False, True])

    def test_score_file_output_can_be_cited_and_points_are_clamped(self):
        pts, _, _ = B.audit_points(self.items(R5={"cite_file": "Build_Score.json", "cite_text": "Ran 4 tests in",
                                                  "points": 9}), self.bd, self.score, "Build_Score.json")
        self.assertEqual(pts, 25.0)

    def test_missing_item_is_a_problem(self):
        doc = self.items()
        doc["items"] = doc["items"][:4]
        pts, _, problems = B.audit_points(doc, self.bd, self.score, "Build_Score.json")
        self.assertEqual(pts, 20.0)
        self.assertTrue(any("R5" in p for p in problems))


# ---------------------------------------------------------------- pass_if

class PassIfTests(unittest.TestCase):
    def test_patterns(self):
        P = B.parse_pass_if
        self.assertEqual(P("exit code 0 and output contains ALL_PRESENT"), [("exit", 0), ("contains", "ALL_PRESENT")])
        self.assertEqual(P("output is exactly 0"), [("exactly", "0")])
        self.assertEqual(P("output contains OK and does not contain FAILED or ERROR"),
                         [("contains", "OK"), ("not_contains", "FAILED"), ("not_contains", "ERROR")])
        self.assertEqual(P("exit code 0, output contains B+ and director_judgment and UNCHANGED"),
                         [("exit", 0), ("contains", "B+"), ("contains", "director_judgment"), ("contains", "UNCHANGED")])
        self.assertEqual(P("output does not contain BAD and contains DONE"), [("not_contains", "BAD"), ("contains", "DONE")])
        self.assertEqual(P("exit code non-zero"), [("exit_nonzero", None)])
        self.assertIsNone(P("the report looks sensible to a human"))

    def test_evaluate(self):
        E = B.evaluate
        self.assertTrue(E([("exactly", "0")], 0, "0\n", ""))
        self.assertFalse(E([("exactly", "0")], 0, "10\n", ""))
        self.assertFalse(E([("exit", 0), ("contains", "OK")], 1, "OK", ""))
        self.assertFalse(E([("not_contains", "FAILED")], 0, "", "FAILED (failures=1)"))
        self.assertTrue(E(None, 0, "", ""))     # unreadable pass_if falls back to exit 0 (and is flagged)
        self.assertFalse(E(None, 2, "", ""))

    @unittest.skipUnless(REAL_CHECKS.exists(), "real locked plan not present")
    def test_every_real_pass_if_is_understood(self):
        checks = json.loads(REAL_CHECKS.read_text())["checks"]
        bad = [c["id"] for c in checks if B.parse_pass_if(c["pass_if"]) is None]
        self.assertEqual(bad, [])


# ---------------------------------------------------------------- the new folder

class IntoTests(unittest.TestCase):
    PLAN = ("# Plan: X\n## Goal\n`001_Architecture/Lab/Old/`\n## New Folder And Files\n"
            "One folder, `$BUILD_DIR` = `Quality_Ledger/`. Home: `001_Architecture/Tools/Quality_Ledger/`.\n"
            "## Steps\n`002_Content-Creation/Other/`\n")

    def test_find_into_reads_the_right_section(self):
        self.assertEqual(B.find_into(self.PLAN, lambda r: True), "001_Architecture/Tools/Quality_Ledger")
        self.assertIsNone(B.find_into(self.PLAN, lambda r: False))

    def test_into_problems(self):
        self.assertEqual(B.into_problems("001_Architecture/Tools/Quality_Ledger", True, False, False), [])
        self.assertTrue(B.into_problems("../Escape", True, False, False))
        self.assertTrue(B.into_problems("Quality_Ledger", True, False, False))          # no parent folder
        self.assertTrue(B.into_problems("A/B/Quality_Ledger", False, False, False))     # parent not tracked
        self.assertTrue(B.into_problems("A/Quality_Ledger", True, True, False))         # already exists
        self.assertTrue(B.into_problems("A/quality ledger", True, False, False))        # naming
        self.assertTrue(B.into_problems("A/Quality_Ledger", True, False, False, is_ignored=True))


# ---------------------------------------------------------------- commands, probe, write-once

class CommandTests(unittest.TestCase):
    def test_build_command_pins(self):
        cmd = B.build_command("P", "deepseek/x", "/tmp/bd", "/tmp/out.txt", servers=["blotato"])
        self.assertEqual(cmd[cmd.index("-s") + 1], "workspace-write")
        self.assertEqual(cmd[cmd.index("-C") + 1], "/tmp/bd")
        for pin in ("sandbox_workspace_write.network_access=false", "sandbox_workspace_write.writable_roots=[]",
                    'web_search="disabled"', "features.multi_agent=false", "mcp_servers.blotato.enabled=false",
                    "model_provider=openrouter_chores"):
            self.assertIn(pin, cmd)
        for f in delegate.DISABLED_FEATURES:
            self.assertIn(f"features.{f}=false", cmd)
        self.assertNotIn("danger-full-access", " ".join(cmd))
        self.assertEqual(cmd[-1], "P")

    def test_runner_command_is_sandboxed(self):
        cmd = B.runner_command("/tmp/bd", "echo hi")
        self.assertEqual(cmd[:6], ["codex", "sandbox", "-P", ":workspace", "-C", "/tmp/bd"])
        self.assertIn("sandbox_workspace_write.network_access=false", cmd)
        self.assertEqual(cmd[-3:], ["/bin/bash", "-c", "echo hi"])

    def test_runner_env_has_no_secrets(self):
        os.environ["FAKE_API_KEY"] = "sk-test"
        try:
            env = B.runner_env("/tmp/bd")
        finally:
            del os.environ["FAKE_API_KEY"]
        self.assertNotIn("FAKE_API_KEY", env)
        self.assertEqual(env["BUILD_DIR"], "/tmp/bd")

    def test_probe_verdict(self):
        t = ["/x/TOOLBOX.md"]
        good = "PROBE_START\nOUTSIDE_WRITE_BLOCKED /x/TOOLBOX.md\nINSIDE_WRITE_OK\nNET_BLOCKED a\nNET_BLOCKED b\nPROBE_END"
        self.assertEqual(B.probe_verdict(good, t), [])
        self.assertTrue(B.probe_verdict(good.replace("BLOCKED /x", "ALLOWED /x"), t))
        self.assertTrue(B.probe_verdict(good.replace("NET_BLOCKED b", "NET_OPEN b"), t))
        self.assertTrue(B.probe_verdict("", t))  # probe never ran = unproven = fail closed

    def test_refuses_inside_worker(self):
        os.environ["AGENT_OS_DELEGATE_WORKER"] = "1"
        try:
            self.assertEqual(B.main(["--preflight"]), 3)
        finally:
            del os.environ["AGENT_OS_DELEGATE_WORKER"]


class WriteOnceTests(unittest.TestCase):
    def test_score_file_written_once_and_read_only(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "Build_Score.json"
            B.write_once(p, {"points": {"non_model_75": 70}})
            self.assertFalse(os.access(p, os.W_OK))
            with self.assertRaises(FileExistsError):
                B.write_once(p, {"points": {"non_model_75": 75}})
            self.assertEqual(json.loads(p.read_text())["points"]["non_model_75"], 70)


# ---------------------------------------------------------------- fixtures for the live tests

def make_repo(repo: Path) -> None:
    (repo / "Tools").mkdir(parents=True)
    (repo / "Tools" / "README.md").write_text("tools\n")
    (repo / "README.md").write_text("root\n")
    (repo / ".gitignore").write_text("__pycache__/\n*.pyc\n")
    for args in (["init", "-q"], ["add", "-A"],
                 ["-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", "commit", "-q", "-m", "init"]):
        subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "t"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "t@t"], check=True)


CHECKS = [
    {"id": "C01", "tier": 0, "what": "file exists", "run": 'test -f "$BUILD_DIR/word_count.py" && echo PRESENT',
     "pass_if": "exit code 0 and output contains PRESENT"},
    {"id": "C02", "tier": 1, "what": "compiles", "run": 'cd "$BUILD_DIR" && python3 -m py_compile word_count.py && echo OK',
     "pass_if": "output contains OK"},
    {"id": "C03", "tier": 2, "what": "counts", "run": 'cd "$BUILD_DIR" && python3 word_count.py "a b c"',
     "pass_if": "output is exactly 3"},
    {"id": "C04", "tier": 2, "what": "network stays off for checks",
     "run": "python3 -c \"import socket;socket.create_connection(('1.1.1.1',443),timeout=3);print('NET_'+'OPEN')\" 2>&1; echo END",
     "pass_if": "output does not contain NET_OPEN and contains END"},
    {"id": "C05", "tier": 2, "what": "an impossible check, so the score lands in the fix band",
     "run": 'cd "$BUILD_DIR" && python3 word_count.py "a"', "pass_if": "output is exactly 99"},
]
README = '# Word Tool\n\nCounts words in a string.\n\nUsage: python3 word_count.py "some text"\n'
BUILD_SCRIPT = ("cat > word_count.py <<'EOF'\nimport sys\nprint(len(sys.argv[1].split()))\nEOF\n"
                "cat > README.md <<'EOF'\n" + README + "EOF")


def make_project(root: Path, checks_list=None) -> Path:
    proj = root / "2026-10-03_Word_Tool"
    proj.mkdir()
    (proj / "Plan_Locked.md").write_text("---\nstatus: locked\n---\n# Plan: Word Tool\n## New Folder And Files\n"
                                         "`Tools/Word_Tool/`\n")
    (proj / "Score.json").write_text(json.dumps({"score": 85, "verdict": "lock", "reasons": ["r"]}))
    checks = proj / "Acceptance_Checks.json"
    checks.write_text(json.dumps({"checks": checks_list or CHECKS, "tony_paid_run": ["look at it"]}))
    os.chmod(checks, 0o444)
    return proj


def audit(points: int) -> dict:
    return {"scored_by": "test", "items": [{"id": rid, "points": points, "cite_file": "word_count.py",
                                            "cite_text": "print(len(sys.argv[1].split()))", "why": "w"}
                                           for rid in B.RUBRIC],
            "failures_to_fix": ["C05 expects 99"], "fix_would_exceed_third": False}


@unittest.skipUnless(HAVE_CODEX, "codex CLI not installed")
class LivePreflightTests(unittest.TestCase):
    """Real codex sandbox, fake local model: free proof on this machine."""

    def test_preflight_holds(self):
        pf = B.preflight(delegate.mcp_server_names())
        self.assertTrue(pf["ok"], pf)
        self.assertNotIn("web_search", pf["build_sandbox"]["tools_offered"])

    def test_preflight_catches_open_network_without_the_pin(self):
        keep = B.SANDBOX_PINS
        B.SANDBOX_PINS = tuple(p for p in keep if "network_access" not in p)
        try:
            pf = B.preflight(delegate.mcp_server_names())
        finally:
            B.SANDBOX_PINS = keep
        self.assertFalse(pf["ok"])
        self.assertIn("network was reachable from inside the sandbox", pf["problems"])


@unittest.skipUnless(HAVE_CODEX, "codex CLI not installed")
class LiveBuildFlowTests(unittest.TestCase):
    """The whole state machine with a fake model: real worktrees, real codex exec sandbox, real
    sandboxed acceptance checks, real git. The temp repo sits in the temp folder, which the sandbox
    may write to, so an outside write really happens and only the mechanical check can catch it."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.repo = root / "repo"
        make_repo(self.repo)
        self.proj = make_project(root)
        self.servers = delegate.mcp_server_names()
        self.base = B.git(self.repo, "rev-parse", "HEAD").strip()
        self.meta = {"project_dir": str(self.proj), "into": "Tools/Word_Tool", "worktrees": []}

    def tearDown(self):
        subprocess.run(["git", "-C", str(self.repo), "worktree", "prune"], capture_output=True)
        for p in self.proj.rglob("*"):
            if p.is_file() and not p.is_symlink():
                os.chmod(p, 0o644)
        self.tmp.cleanup()

    def fake_build(self, script):
        w = B.new_worktree(self.proj, self.meta, self.repo, self.base, "Tools/Word_Tool")
        w.update({"attempt": 1, "built_by": "fake-model"})
        self.meta["worktrees"].append(w)
        rc, out, tools = B.run_fake_build(script, w["build_dir"], self.servers)
        self.assertEqual(rc, 0)
        return w

    def save(self):
        B.write_json(self.proj / "Build_Meta.json", self.meta)

    def test_outside_write_by_the_worker_is_an_instant_stop(self):
        w = self.fake_build(BUILD_SCRIPT + "\necho sneaky >> ../README.md")
        code, doc = B.score_stage(self.proj, self.meta, w, 1, "raw", "fake-model", self.servers, run_preflight=False)
        self.save()
        self.assertEqual(code, 8)
        self.assertEqual(doc["verdict"], "containment_stop")
        self.assertTrue(any("edited an existing file" in v and "Tools/README.md" in v
                            for v in doc["containment"]["violations"]))
        self.assertEqual(doc["checks"], [])                       # nothing else ran
        self.assertEqual(B.finalize_main(self.proj), 1)           # nothing to audit
        self.assertEqual(B.after_fix_main(self.proj), 1)          # zero fix attempts

    def test_full_path_raw_fix_rebuild_stop(self):
        w = self.fake_build(BUILD_SCRIPT)
        code, doc = B.score_stage(self.proj, self.meta, w, 1, "raw", "fake-model", self.servers)
        self.save()
        self.assertEqual(code, 0, doc)
        by_id = {c["id"]: c["passed"] for c in doc["checks"]}
        self.assertEqual(by_id, {"C01": True, "C02": True, "C03": True, "C04": True, "C05": False})
        self.assertEqual(doc["points"]["acceptance_60"], 48.0)
        self.assertEqual(doc["points"]["tier0_15"], 15)
        score_p = self.proj / "Build_Score.json"
        raw_bytes = score_p.read_bytes()
        self.assertFalse(os.access(score_p, os.W_OK))

        # Audit (2 points per item = 10) -> 73 -> one fix round
        B.write_json(self.proj / "Build_Audit.json", audit(2))
        (self.proj / "Build_Review.md").write_text("review\n")
        self.assertEqual(B.finalize_main(self.proj), 0)
        v = json.loads((self.proj / "Build_Verdict.json").read_text())["current"]
        self.assertEqual((v["total"], v["next"]), (73.0, "fix_round"))
        self.assertEqual(B.finalize_main(self.proj), 1)           # cannot re-finalize the same attempt

        # Fix round: small edit inside the folder, still can't pass C05 -> rebuild
        bd = Path(w["build_dir"])
        bd.joinpath("README.md").write_text(README + "One more line.\n")
        self.assertEqual(B.after_fix_main(self.proj), 0)
        v = json.loads((self.proj / "Build_Verdict.json").read_text())["current"]
        self.assertEqual((v["stage"], v["next"]), ("fix", "rebuild"))
        self.assertLess(v["fix_ratio"], B.MAX_FIX_RATIO)
        self.assertEqual(score_p.read_bytes(), raw_bytes)         # raw score never rewritten
        self.assertEqual(B.after_fix_main(self.proj), 1)          # no second fix round

        # Rebuild in a fresh worktree (old one kept), scored raw, audited, then the cap stops it
        self.assertEqual(B.rebuild_prep_main(self.proj, repo=str(self.repo)), 0)
        self.meta = json.loads((self.proj / "Build_Meta.json").read_text())
        w2 = self.meta["worktrees"][-1]
        self.assertNotEqual(w2["worktree"], w["worktree"])
        self.assertTrue(Path(w["worktree"]).is_dir())
        Path(w2["build_dir"], "word_count.py").write_text("import sys\nprint(len(sys.argv[1].split()))\n")
        self.assertEqual(B.score_rebuild_main(self.proj), 0)
        B.write_json(self.proj / "Build_Audit_Rebuild.json", audit(2))
        self.assertEqual(B.finalize_main(self.proj), 0)
        v = json.loads((self.proj / "Build_Verdict.json").read_text())["current"]
        self.assertEqual((v["attempt"], v["total"], v["next"]), (2, 73.0, "stop"))  # fix + rebuild both used
        self.assertEqual(B.rebuild_prep_main(self.proj, repo=str(self.repo)), 1)   # no second rebuild

    def test_cleared_build_and_tampering_detected(self):
        w = self.fake_build(BUILD_SCRIPT)
        code, _ = B.score_stage(self.proj, self.meta, w, 1, "raw", "fake-model", self.servers, run_preflight=False)
        self.save()
        self.assertEqual(code, 0)
        (self.proj / "Build_Review.md").write_text("review\n")
        # The auditor edits the build before finalize: refused as score-before-edit broken
        Path(w["build_dir"], "README.md").write_text("edited by the auditor\n")
        B.write_json(self.proj / "Build_Audit.json", audit(5))
        self.assertEqual(B.finalize_main(self.proj), 7)
        Path(w["build_dir"], "README.md").write_text(README)  # put it back exactly
        self.assertEqual(B.finalize_main(self.proj), 0)
        v = json.loads((self.proj / "Build_Verdict.json").read_text())
        self.assertEqual((v["current"]["total"], v["current"]["next"]), (88.0, "lab_run"))
        self.assertEqual(v["tony_paid_run"], ["look at it"])

    def test_build_main_end_to_end_with_fake_model(self):
        """The real top-level build path; only OpenRouter is swapped for the local fake model."""
        saved = (B.build_command, B.load_secret, B.L.live_prices, B.L.key_usage, B.open_log)
        logdir = Path(self.tmp.name) / "logs"
        logdir.mkdir()

        def fake_log(stamp, prefix):
            p = logdir / f"{prefix}-{stamp}.log"
            return p, str(p.with_suffix(".last.txt")), open(p, "w")
        os.environ["LAB_FAKE_KEY"] = "x"
        try:
            with B._FakeModel(BUILD_SCRIPT) as fake:
                B.build_command = lambda prompt, model, bd, last, servers, **kw: saved[0](
                    prompt, model, bd, last, servers, **kw) if kw else saved[0](  # preflight keeps its own fake
                    prompt, "lab-fake-model", bd, last, servers,
                    provider=fake.provider, provider_name=fake.provider_name)
                B.load_secret = lambda name: "x"
                B.L.live_prices = lambda: None
                B.L.key_usage = lambda key: None
                B.open_log = fake_log
                code = B.build_main(self.proj, None, None, 2.0, False, repo=str(self.repo))
        finally:
            (B.build_command, B.load_secret, B.L.live_prices, B.L.key_usage, B.open_log) = saved
            del os.environ["LAB_FAKE_KEY"]
        self.assertEqual(code, 0)
        meta = json.loads((self.proj / "Build_Meta.json").read_text())
        w = meta["worktrees"][0]
        self.assertEqual((meta["into"], w["exit_code"], w["attempt"]), ("Tools/Word_Tool", 0, 1))
        self.assertEqual(w["built_by"], B.build_picks(None, None)[0]["id"])
        self.assertTrue(Path(w["build_dir"], "word_count.py").is_file())
        score = json.loads((self.proj / "Build_Score.json").read_text())
        self.assertEqual(score["points"]["non_model_75"], 63.0)
        self.assertEqual(B.git(self.repo, "branch", "--list", "--format=%(refname:short)", "lab/*").strip(),
                         "lab/2026-10-03_Word_Tool/wt1")
        self.assertEqual(B.git(self.repo, "rev-parse", "HEAD").strip(), self.base)  # main branch never moved
        self.assertNotEqual(B.git(self.repo, "rev-parse", "lab/2026-10-03_Word_Tool/wt1").strip(), self.base)
        self.assertEqual(B.build_main(self.proj, None, None, 2.0, False, repo=str(self.repo)), 1)  # never twice

    def test_tampered_score_file_is_refused(self):
        w = self.fake_build(BUILD_SCRIPT)
        B.score_stage(self.proj, self.meta, w, 1, "raw", "fake-model", self.servers, run_preflight=False)
        self.save()
        p = self.proj / "Build_Score.json"
        os.chmod(p, 0o644)
        doc = json.loads(p.read_text())
        doc["points"]["non_model_75"] = 75
        p.write_text(json.dumps(doc))
        B.write_json(self.proj / "Build_Audit.json", audit(5))
        (self.proj / "Build_Review.md").write_text("review\n")
        self.assertEqual(B.finalize_main(self.proj), 7)


# ---------------------------------------------------------------- --reverify

class ReverifyRefusalTests(unittest.TestCase):
    """--reverify only rechecks a build that already ended at lab_run/stop, once. No codex needed:
    every refusal happens before anything runs."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.proj = make_project(Path(self.tmp.name))
        self.meta = {"into": "Tools/Word_Tool", "worktrees": [
            {"attempt": 1, "scores": {"raw": {"file": "Build_Score.json", "sha256": "x", "commit": "c"}}}]}

    def tearDown(self):
        for p in self.proj.rglob("*"):
            os.chmod(p, 0o644)
        self.tmp.cleanup()

    def state(self, current=None, files=("Build_Score.json", "Build_Audit.json")):
        for f in files:
            (self.proj / f).write_text("{}")
        B.write_json(self.proj / "Build_Meta.json", self.meta)
        if current is not None:
            B.write_json(self.proj / "Build_Verdict.json", {"history": [current], "current": current})

    def run_it(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = B.reverify_main(self.proj, run_preflight=False)
        return code, err.getvalue()

    def test_refuses_without_prior_score_or_audit(self):
        self.assertEqual(self.run_it()[0], 1)
        self.state({"attempt": 1, "stage": "raw", "next": "lab_run"}, files=("Build_Score.json",))
        code, err = self.run_it()
        self.assertEqual(code, 1)
        self.assertIn("Build_Audit.json missing", err)

    def test_refuses_a_second_reverify(self):
        self.state({"attempt": 1, "stage": "raw", "next": "lab_run"},
                   files=("Build_Score.json", "Build_Audit.json", B.REVERIFY_FILE))
        code, err = self.run_it()
        self.assertEqual(code, 1)
        self.assertIn("never twice", err)

    def test_fix_round_and_rebuild_point_to_their_own_commands(self):
        for nxt, cmd in (("fix_round", "--after-fix"), ("rebuild", "--rebuild-prep")):
            self.state({"attempt": 1, "stage": "raw", "next": nxt})
            code, err = self.run_it()
            self.assertEqual(code, 1, nxt)
            self.assertIn(cmd, err)
        self.assertFalse((self.proj / B.REVERIFY_FILE).exists())

    def test_refuses_unfinalized_or_after_a_containment_stop(self):
        self.state()  # scored and audited, but never finalized
        self.assertIn("--finalize", self.run_it()[1])
        self.state({"attempt": 1, "stage": "fix", "next": "stop", "exit_code": 8})
        code, err = self.run_it()
        self.assertEqual(code, 1)
        self.assertIn("cannot overrule", err)


BUGGY_LINE = 'print(len(sys.argv[1].split(" ")))'  # miscounts runs of spaces
BUGGY_SCRIPT = ("cat > word_count.py <<'EOF'\nimport sys\n" + BUGGY_LINE + "\nEOF\n"
                "cat > README.md <<'EOF'\n" + README + "EOF")
REVERIFY_CHECKS = CHECKS[:4] + [
    {"id": "C05", "tier": 2, "what": "extra spaces are not words",
     "run": 'cd "$BUILD_DIR" && python3 word_count.py "  a   b  "', "pass_if": "output is exactly 2"}]


@unittest.skipUnless(HAVE_CODEX, "codex CLI not installed")
class LiveReverifyTests(unittest.TestCase):
    """A build that cleared WITH a known bug (C05), then a fix applied afterwards, rechecked for real."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.repo = root / "repo"
        make_repo(self.repo)
        self.proj = make_project(root, REVERIFY_CHECKS)
        self.servers = delegate.mcp_server_names()
        self.base = B.git(self.repo, "rev-parse", "HEAD").strip()
        self.meta = {"project_dir": str(self.proj), "into": "Tools/Word_Tool", "worktrees": []}

    def tearDown(self):
        subprocess.run(["git", "-C", str(self.repo), "worktree", "prune"], capture_output=True)
        for p in self.proj.rglob("*"):
            if p.is_file() and not p.is_symlink():
                os.chmod(p, 0o644)
        self.tmp.cleanup()

    def cleared_build(self) -> Path:
        """Raw build 63/75 (C05 fails) + audit 20/25 (cited on the buggy line) = 83 -> lab_run."""
        w = B.new_worktree(self.proj, self.meta, self.repo, self.base, "Tools/Word_Tool")
        w.update({"attempt": 1, "built_by": "fake-model"})
        self.meta["worktrees"].append(w)
        self.assertEqual(B.run_fake_build(BUGGY_SCRIPT, w["build_dir"], self.servers)[0], 0)
        code, doc = B.score_stage(self.proj, self.meta, w, 1, "raw", "fake-model", self.servers, run_preflight=False)
        B.write_json(self.proj / "Build_Meta.json", self.meta)
        self.assertEqual((code, doc["failed_checks"]), (0, ["C05"]), doc)
        doc = audit(4)
        for it in doc["items"]:
            it["cite_text"] = BUGGY_LINE
        B.write_json(self.proj / "Build_Audit.json", doc)
        (self.proj / "Build_Review.md").write_text("review\n")
        self.assertEqual(B.finalize_main(self.proj), 0)
        v = self.verdict()
        self.assertEqual((v["total"], v["next"]), (83.0, "lab_run"))
        self.originals = {n: (self.proj / n).read_bytes() for n in ("Build_Score.json", "Build_Audit.json")}
        return Path(w["build_dir"])

    def verdict(self, whole=False):
        v = json.loads((self.proj / "Build_Verdict.json").read_text())
        return v if whole else v["current"]

    def assert_originals_untouched(self):
        for name, data in self.originals.items():
            self.assertEqual((self.proj / name).read_bytes(), data, name)

    def test_fixed_build_recomputes_75_and_carries_the_audit_25(self):
        bd = self.cleared_build()
        (bd / "word_count.py").write_text("import sys\nprint(len(sys.argv[1].split()))\n")  # the fix
        self.assertEqual(B.reverify_main(self.proj), 0)  # real preflight too: still $0, local fake model
        rv = self.proj / B.REVERIFY_FILE
        doc = json.loads(rv.read_text())
        self.assertFalse(os.access(rv, os.W_OK))                     # written once, read-only
        self.assertEqual((doc["stage"], doc["failed_checks"]), ("reverify", []))
        self.assertEqual((doc["points"]["acceptance_60"], doc["points"]["tier0_15"]), (60.0, 15))
        v = self.verdict()
        self.assertEqual((v["stage"], v["non_model_75"], v["audit_25"], v["total"], v["cleared"], v["next"]),
                         ("reverify", 75.0, 20.0, 95.0, True, "lab_run"))
        self.assertEqual(v["previous_total"], 83.0)
        self.assertLess(v["fix_ratio"], B.MAX_FIX_RATIO)
        # Carried, not re-scored: the cited buggy line is gone, so a fresh re-score would give 0.
        score = json.loads((self.proj / "Build_Score.json").read_text())
        self.assertEqual(B.audit_points(json.loads((self.proj / "Build_Audit.json").read_text()),
                                        bd, score, "Build_Score.json")[0], 0.0)
        self.assert_originals_untouched()
        self.assertEqual(len(self.verdict(True)["history"]), 2)      # raw entry kept, reverify added
        self.assertEqual(B.git(self.repo, "rev-parse", "HEAD").strip(), self.base)  # main never moved
        # One-shot, and it opens no fix/rebuild chain
        for fn in (B.reverify_main, B.after_fix_main, B.finalize_main):
            self.assertEqual(fn(self.proj), 1, fn.__name__)
        self.assertEqual(B.rebuild_prep_main(self.proj, repo=str(self.repo)), 1)

    def test_regression_after_the_fix_ends_at_stop(self):
        bd = self.cleared_build()
        (bd / "word_count.py").write_text("import sys\nprint('x')\n")  # a "fix" that breaks C03 too
        self.assertEqual(B.reverify_main(self.proj, run_preflight=False), 0)
        v = self.verdict()
        self.assertEqual((v["non_model_75"], v["audit_25"], v["total"], v["cleared"], v["next"]),
                         (51.0, 20.0, 71.0, False, "stop"))
        self.assertNotIn("tony_paid_run", self.verdict(True))        # no longer cleared
        self.assert_originals_untouched()

    def test_fix_bigger_than_a_third_cannot_carry_the_audit(self):
        bd = self.cleared_build()
        (bd / "word_count.py").write_text("import sys\nprint(len(sys.argv[1].split()))\n")
        (bd / "README.md").write_text("".join(f"Rewritten line {i}.\n" for i in range(10)))
        self.assertEqual(B.reverify_main(self.proj, run_preflight=False), 0)
        v = self.verdict()
        self.assertEqual((v["total"], v["fix_too_big"], v["cleared"], v["next"]), (95.0, True, False, "stop"))

    def test_containment_stop_inside_reverify(self):
        bd = self.cleared_build()
        (bd / "word_count.py").write_text("import sys\nprint(len(sys.argv[1].split()))\n")
        (bd.parent / "README.md").write_text("sneaky edit outside the build folder\n")
        self.assertEqual(B.reverify_main(self.proj, run_preflight=False), 8)
        doc = json.loads((self.proj / B.REVERIFY_FILE).read_text())
        self.assertEqual((doc["verdict"], doc["checks"]), ("containment_stop", []))  # nothing else ran
        self.assertTrue(any("edited an existing file" in x and "Tools/README.md" in x
                            for x in doc["containment"]["violations"]))
        v = self.verdict()
        self.assertEqual((v["stage"], v["next"], v["exit_code"]), ("reverify", "stop", 8))
        self.assert_originals_untouched()
        self.assertEqual(B.reverify_main(self.proj, run_preflight=False), 1)  # zero further attempts

    def test_audit_file_changed_after_finalize_is_refused(self):
        bd = self.cleared_build()
        (bd / "word_count.py").write_text("import sys\nprint(len(sys.argv[1].split()))\n")
        doc = json.loads((self.proj / "Build_Audit.json").read_text())
        doc["items"][0]["points"] = 5
        B.write_json(self.proj / "Build_Audit.json", doc)
        self.assertEqual(B.reverify_main(self.proj, run_preflight=False), 7)
        self.assertFalse((self.proj / B.REVERIFY_FILE).exists())


if __name__ == "__main__":
    unittest.main()
