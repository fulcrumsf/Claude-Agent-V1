"""Tests for lab_promote.py. Every repo here is a throwaway git repo in the temp folder, with a local
bare repo standing in for GitHub: nothing touches the real Agent-OS, 001_Architecture/Lab/, 000_Wiki/
or TOOLBOX.md, nothing reaches the network, graphify is a stub, and the calibration log is stubbed."""
import contextlib
import io
import json
import os
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

import lab_promote as P

R, B = P.R, P.B
REL = "001_Architecture/Tools/Word_Tool"
PROJ = "2026-10-03_Word_Tool"
FAKE_KEY = "sk-" + "or-v1-" + "q" * 48  # built at run time so no key-shaped literal sits in this file


def sh(cwd, *args) -> str:
    return subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True, text=True).stdout


def run(fn, *a, **k):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        code = fn(*a, **k)
    tagged = [ln for ln in out.getvalue().splitlines() if ln.startswith("LAB_PROMOTE_")]
    return code, (json.loads(tagged[-1].split(" ", 1)[1]) if tagged else None)


def write(p: Path, text: str) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    return p


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name).resolve()
        self.origin = base / "origin.git"
        sh(base, "init", "-q", "--bare", "-b", "main", str(self.origin))
        self.repo = base / "Agent-OS"
        self.repo.mkdir()
        sh(self.repo, "init", "-q", "-b", "main")
        for k, v in (("user.name", "Test"), ("user.email", "t@example.com"), ("commit.gpgsign", "false")):
            sh(self.repo, "config", k, v)
        write(self.repo / ".gitignore", "001_Architecture/Lab/\n__pycache__/\n*.pyc\n*.log\n")
        write(self.repo / "TOOLBOX.md", "# TOOLBOX\n\n## Tools\n\n### Old Tool\n- old\n")
        write(self.repo / "000_Wiki/index.md", "# Wiki Index\n\n## Architecture\n\n- [[Architecture/Existing]] - x\n")
        write(self.repo / "000_Wiki/log.md", "# Log\n")
        write(self.repo / "000_Wiki/Architecture/Existing.md", "# Existing\n\n## Related\n- [[Other]]\n")
        write(self.repo / "001_Architecture/Tools/README.md", "tools\n")
        write(self.repo / P.REGISTRY_REL, "| Domain | Path | Graph |\n|---|---|---|\n"
              "| Wiki | `000_Wiki/` | x |\n| Architecture | `001_Architecture/` | x |\n")
        sh(self.repo, "add", "-A")
        sh(self.repo, "commit", "-q", "-m", "init")
        sh(self.repo, "remote", "add", "origin", str(self.origin))
        sh(self.repo, "push", "-q", "-u", "origin", "main")
        self.lab = self.repo / "001_Architecture" / "Lab"
        self.proj = self.lab / PROJ
        self.proj.mkdir(parents=True)
        self.plan(f"One folder: `{REL}/`.")
        self.wt = self.proj / "Build_Worktree_1"
        self.branch = f"lab/{PROJ}/wt1"
        sh(self.repo, "worktree", "add", "-q", "-b", self.branch, str(self.wt), "HEAD")
        self.build = self.wt / REL
        write(self.build / "word_tool.py", "print('word v1')\n")
        write(self.build / "README.md", "# Word Tool\n")
        sh(self.wt, "add", "-A")
        sh(self.wt, "commit", "-q", "-m", "lab: raw build")
        self.raw_commit = sh(self.wt, "rev-parse", "HEAD").strip()
        B.write_json(self.proj / "Build_Meta.json", {"into": REL, "worktrees": [{
            "worktree": str(self.wt), "build_dir": str(self.build), "branch": self.branch,
            "built_by": "deepseek/deepseek-v4-pro", "attempt": 1}]})
        B.write_json(self.proj / "Build_Verdict.json", {
            "current": {"stage": "raw", "total": 90.0, "cleared": True, "next": "lab_run"},
            "history": [], "tony_paid_run": ["Run it once."]})
        self.secrets = write(base / "env-secrets", f"export OPENROUTER_API_KEY={FAKE_KEY}\nDEBUG=true\n")
        self.graphify_calls = []
        patcher = mock.patch.object(B.L, "log_event", lambda event: None)
        patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self):
        self.tmp.cleanup()

    # ---- helpers
    def plan(self, folder_line):
        write(self.proj / "Plan_Locked.md", "---\nstatus: locked\n---\n# Plan: Word_Tool\n\n"
              f"## New Folder And Files\n{folder_line}\n\n## How To Verify\nRun it.\n\n"
              "## Wiring (Later, Tony-Approved)\n- Register the hook.\n- Add to TOOLBOX.md.\n")

    def grade(self, g, notes="fine"):
        return run(R.log_main, self.proj, "ran it", notes, str(g), "")

    def fix_in_place(self):  # what /lab-run does: edit in place, never commit
        write(self.build / "word_tool.py", "print('word v2, fixed in /lab-run')\n")

    def fake_graphify(self, ok=True):
        def g(repo, domain):
            self.graphify_calls.append(domain)
            return {"domain": domain, "ok": ok}
        return g

    def plan_cmd(self, **k):
        return run(P.plan_main, str(self.proj), k.get("accept", False), self.lab, self.secrets)

    def checkout(self, **k):
        return run(P.checkout_main, str(self.proj), k.get("accept", False), self.lab, self.secrets)

    def session_edits(self, toolbox_line="\n### Word Tool (`001_Architecture/Tools/Word_Tool/`)\n- counts words\n"):
        with open(self.repo / "TOOLBOX.md", "a") as fh:
            fh.write(toolbox_line)
        write(self.repo / "000_Wiki/Architecture/Word-Tool.md", "---\ntitle: Word Tool\ntype: wiki\n---\n# Word Tool\n")
        with open(self.repo / "000_Wiki/index.md", "a") as fh:
            fh.write("- [[Architecture/Word-Tool]] - counts words\n")
        return ["TOOLBOX.md", "000_Wiki/Architecture/Word-Tool.md", "000_Wiki/index.md"]

    def finish(self, files, desc="the word tool we built in lab gets promoted", no_push=False, ok=True):
        return run(P.finish_main, str(self.proj), files, desc, ["Co-Authored-By: Test <t@example.com>"],
                   no_push, self.lab, self.secrets, self.fake_graphify(ok))

    def main_head(self):
        return sh(self.repo, "rev-parse", "main").strip()

    def lab_head(self):
        return sh(self.repo, "rev-parse", self.branch).strip()

    def state(self):
        return (self.main_head(), self.lab_head(), sh(self.repo, "status", "--porcelain", "--untracked-files=all"),
                sh(self.wt, "status", "--porcelain", "--untracked-files=all"),
                sorted(p.name for p in self.proj.iterdir()))


class GateTests(Fixture):
    def assert_refused(self, words, code=2):
        before = self.state()
        for fn in (self.plan_cmd, self.checkout):
            c, doc = fn()
            self.assertEqual(c, code, doc)
            self.assertIn(words, doc["why"])
        self.assertEqual(self.state(), before)
        self.assertFalse((self.repo / REL).exists())

    def test_no_run_log_points_back_to_lab_run(self):
        self.assert_refused("Run /lab-run first")

    def test_latest_grade_under_80_is_refused(self):
        self.grade(79)
        self.assert_refused("below 80")

    def test_only_the_latest_round_counts(self):
        self.grade(92)
        self.grade(70, "worse after the change")
        self.assert_refused("below 80")

    def test_folder_changed_after_the_passing_grade(self):
        self.grade(88)
        self.fix_in_place()
        self.assert_refused("changed after Tony's passing grade")

    def test_edited_run_log_needs_tonys_say_so(self):
        self.grade(60)
        self.grade(85)
        p = self.proj / R.RUN_LOG
        p.write_text(p.read_text().replace('"grade": 60', '"grade": 99', 1))
        self.assert_refused("--accept-edited-log")
        self.assertEqual(self.plan_cmd(accept=True)[0], 0)

    def test_uncleared_build_names_the_lab_build_step(self):
        self.grade(90)
        B.write_json(self.proj / "Build_Verdict.json", {"current": {"total": 70, "cleared": False,
                                                                     "next": "fix_round"}, "history": []})
        self.assert_refused("Step 4")


class CheckoutTests(Fixture):
    def test_the_gap_uncommitted_lab_run_fix_is_committed_then_promoted(self):
        self.fix_in_place()
        self.grade(86)
        self.assertEqual(sh(self.wt, "status", "--porcelain", "--", REL).strip(), f"M {REL}/word_tool.py")
        code, doc = self.checkout()
        self.assertEqual(code, 0, doc)
        self.assertTrue(doc["lab_commit_made_now"])
        # exactly one new commit, on the lab branch, on top of the raw build; main untouched by it
        self.assertEqual(sh(self.repo, "rev-parse", f"{self.branch}^").strip(), self.raw_commit)
        self.assertEqual(doc["lab_commit"], self.lab_head())
        self.assertNotEqual(self.main_head(), self.lab_head())
        on_main = subprocess.run(["git", "-C", str(self.repo), "merge-base", "--is-ancestor", self.lab_head(), "main"])
        self.assertEqual(on_main.returncode, 1)  # the lab commit is NOT on main
        # the promoted copy is the FIXED one, not the stale branch version
        self.assertIn("fixed in /lab-run", (self.repo / REL / "word_tool.py").read_text())
        self.assertEqual(sorted(doc["files"]), ["README.md", "word_tool.py"])
        self.assertEqual(sh(self.wt, "status", "--porcelain", "--", REL).strip(), "")
        self.assertEqual(B.read_json(self.proj / P.PROMOTE_META)["stage"], "checked_out")

    def test_no_empty_or_duplicate_lab_commit_when_nothing_changed(self):
        self.grade(90)
        before = self.lab_head()
        code, doc = self.checkout()
        self.assertEqual(code, 0, doc)
        self.assertFalse(doc["lab_commit_made_now"])
        self.assertEqual(self.lab_head(), before)
        self.assertEqual(doc["lab_commit"], self.raw_commit)

    def test_plan_writes_nothing_and_shows_the_review(self):
        self.fix_in_place()
        self.grade(85)
        before = self.state()
        code, doc = self.plan_cmd()
        self.assertEqual(code, 0, doc)
        self.assertEqual(self.state(), before)
        self.assertEqual(doc["destination"], str(self.repo / REL))
        self.assertTrue(doc["lab_branch_commit_needed"])
        self.assertEqual(doc["lab_run_uncommitted"], [{"status": "M", "path": "word_tool.py"}])
        self.assertEqual(doc["wiring_left_for_tony"], ["Register the hook.", "Add to TOOLBOX.md."])
        self.assertEqual(doc["grades"], [85])

    def test_only_the_one_folder_is_promoted(self):
        write(self.wt / "001_Architecture/Tools/Other/sneaky.py", "x = 1\n")  # committed on the lab branch
        sh(self.wt, "add", "-A")
        sh(self.wt, "commit", "-q", "-m", "outside")
        write(self.wt / "TOOLBOX.md", "rewritten inside the worktree\n")  # uncommitted, outside the folder
        self.grade(90)
        code, doc = self.checkout()
        self.assertEqual(code, 0, doc)
        self.assertFalse((self.repo / "001_Architecture/Tools/Other").exists())
        self.assertIn("### Old Tool", (self.repo / "TOOLBOX.md").read_text())
        status = sh(self.repo, "status", "--porcelain", "--untracked-files=all").splitlines()
        self.assertEqual(sorted(s[3:] for s in status), [f"{REL}/README.md", f"{REL}/word_tool.py"])
        code, plan = self.plan_cmd()
        self.assertEqual(code, 0, plan)
        self.assertEqual(plan["worktree_changes_outside_folder_not_promoted"], ["TOOLBOX.md"])

    def test_gitignored_files_are_listed_and_left_behind(self):
        write(self.build / "run.log", "real-run output\n")
        self.grade(90)
        code, doc = self.checkout()
        self.assertEqual(code, 0, doc)
        self.assertEqual(doc["not_promoted_gitignored"], ["run.log"])
        self.assertFalse((self.repo / REL / "run.log").exists())

    def test_destination_already_exists(self):
        write(self.repo / REL / "x.md", "already here\n")
        sh(self.repo, "add", "-A")
        sh(self.repo, "commit", "-q", "-m", "someone made it")
        self.grade(90)
        code, doc = self.checkout()
        self.assertEqual(code, 4)
        self.assertIn("already exists", doc["why"])

    def test_refuses_off_main(self):
        self.grade(90)
        sh(self.repo, "checkout", "-q", "-b", "side")
        code, doc = self.checkout()
        self.assertEqual(code, 4)
        self.assertIn("not main", doc["why"])

    def test_destination_must_come_from_the_locked_plan(self):
        self.grade(90)
        self.plan("One folder: `001_Architecture/Tools/Something_Else/`.")
        code, doc = self.checkout()
        self.assertEqual(code, 4)
        self.assertIn("does not name", doc["why"])

    def test_symlink_in_the_folder_is_refused(self):
        os.symlink(str(self.secrets), self.build / "keys")
        self.grade(90)
        code, doc = self.checkout()
        self.assertEqual(code, 4)
        self.assertIn("links", doc["why"])
        self.assertFalse((self.repo / REL).exists())

    def test_secret_value_or_pattern_stops_everything(self):
        for i, leak in enumerate((FAKE_KEY, "ghp_" + "a" * 36)):
            with self.subTest(i=i):
                write(self.build / "word_tool.py", f"KEY = '{leak}'\n")
                self.grade(90)
                before = self.lab_head()
                code, doc = self.checkout()
                self.assertEqual(code, 5, doc)
                self.assertNotIn(leak, json.dumps(doc))  # names only, never the value
                self.assertEqual(self.lab_head(), before)
                self.assertFalse((self.repo / REL).exists())

    def test_rerunning_checkout_resumes_without_a_second_commit(self):
        self.fix_in_place()
        self.grade(90)
        first = self.checkout()[1]
        code, doc = self.checkout()
        self.assertEqual(code, 0, doc)
        self.assertTrue(doc["resumed"])
        self.assertEqual(doc["lab_commit"], first["lab_commit"])


class FinishTests(Fixture):
    def promote_ready(self):
        self.fix_in_place()
        self.grade(88)
        code, doc = self.checkout()
        self.assertEqual(code, 0, doc)
        return doc

    def test_full_promotion_commits_only_its_own_changes_and_pushes(self):
        # another session's uncommitted edit already sits in TOOLBOX.md before /lab-promote starts
        tb = self.repo / "TOOLBOX.md"
        tb.write_text(tb.read_text().replace("# TOOLBOX\n", "# TOOLBOX (half-done edit by another session)\n"))
        start = self.main_head()
        self.promote_ready()
        files = self.session_edits()
        code, doc = self.finish(files)
        self.assertEqual(code, 0, doc)
        commit = doc["main_commit"]
        self.assertEqual(self.main_head(), commit)
        self.assertEqual(sh(self.repo, "rev-parse", f"{commit}^").strip(), start)
        changed = sorted(sh(self.repo, "show", "--name-only", "--format=", commit).split())
        self.assertEqual(changed, sorted(files + [f"{REL}/README.md", f"{REL}/word_tool.py"]))
        self.assertIn("fixed in /lab-run", sh(self.repo, "show", f"{commit}:{REL}/word_tool.py"))
        committed_tb = sh(self.repo, "show", f"{commit}:TOOLBOX.md")
        self.assertIn("### Word Tool", committed_tb)
        self.assertNotIn("another session", committed_tb)  # kept out of the commit...
        self.assertIn("another session", tb.read_text())  # ...and still on disk, uncommitted
        self.assertEqual(sh(self.repo, "diff", "--cached", "--name-only").strip(), "")
        self.assertEqual(sh(self.repo, "diff", "--name-only").split(), ["TOOLBOX.md"])
        self.assertTrue(any("other uncommitted edits" in w for w in doc["warnings"]))
        msg = sh(self.repo, "log", "-1", "--format=%B", commit)
        self.assertIn("the word tool we built in lab gets promoted", msg)
        self.assertIn(PROJ, msg)
        self.assertIn("Co-Authored-By: Test", msg)
        # pushed to the stand-in remote
        self.assertTrue(doc["pushed"])
        self.assertEqual(sh(self.origin, "rev-parse", "main").strip(), commit)
        # graphify ran on the affected domains only (the promoted folder's and the wiki's)
        self.assertEqual(sorted(self.graphify_calls), ["000_Wiki", "001_Architecture"])
        # cleanup is printed for Tony, never run
        self.assertTrue(self.wt.exists())
        self.assertEqual(self.lab_head(), doc["lab_commit"])
        cmds = " ".join(doc["cleanup_commands_for_tony"])
        self.assertIn(f'worktree remove "{self.wt}"', cmds)
        self.assertIn(f'branch -D "{self.branch}"', cmds)
        self.assertEqual(doc["wiring_left_for_tony"], ["Register the hook.", "Add to TOOLBOX.md."])
        self.assertEqual(B.read_json(self.proj / P.PROMOTE_META)["stage"], "pushed")

    def test_never_runs_a_destructive_git_command(self):
        calls, real = [], subprocess.run

        def spy(cmd, *a, **k):
            calls.append([str(x) for x in cmd])
            return real(cmd, *a, **k)
        with mock.patch("subprocess.run", spy):
            self.promote_ready()
            self.finish(self.session_edits())
        joined = [" ".join(c) for c in calls]
        for bad in ("worktree remove", "worktree prune", "branch -D", "branch -d", "reset --hard", " clean",
                    "--force", "push -f", " rm ", "stash drop", "stash clear", "checkout -f"):
            self.assertFalse([j for j in joined if bad in j], bad)
        self.assertTrue(any("checkout" in j and f"-- {REL}" in j for j in joined))

    def test_main_moved_after_checkout_still_lands_on_top(self):
        self.promote_ready()
        write(self.repo / "000_Wiki/Architecture/Existing.md", "# Existing\n\nedited and committed elsewhere\n")
        sh(self.repo, "commit", "-q", "-m", "other session", "--", "000_Wiki/Architecture/Existing.md")
        other = self.main_head()
        code, doc = self.finish(self.session_edits())
        self.assertEqual(code, 0, doc)
        self.assertEqual(sh(self.repo, "rev-parse", f"{doc['main_commit']}^").strip(), other)
        self.assertIn("edited and committed elsewhere", sh(self.repo, "show", "main:000_Wiki/Architecture/Existing.md"))

    def test_main_moving_during_the_commit_changes_nothing(self):
        self.promote_ready()
        files = self.session_edits()
        real = P.build_commit

        def racing(*a, **k):
            c = real(*a, **k)
            write(self.repo / "race.md", "x\n")
            sh(self.repo, "add", "race.md")
            sh(self.repo, "commit", "-q", "-m", "race", "--", "race.md")
            return c
        with mock.patch.object(P, "build_commit", racing):
            code, doc = self.finish(files)
        self.assertEqual(code, 8, doc)
        self.assertEqual(B.read_json(self.proj / P.PROMOTE_META)["stage"], "checked_out")
        self.assertEqual(sh(self.repo, "log", "-1", "--format=%s", "main").strip(), "race")
        code, doc = self.finish(files)
        self.assertEqual(code, 0, doc)

    def test_overlapping_edit_with_another_session_stops_before_committing(self):
        tb = self.repo / "TOOLBOX.md"
        tb.write_text(tb.read_text().replace("- old\n", "- old X\n"))
        self.promote_ready()
        files = self.session_edits()
        tb.write_text(tb.read_text().replace("- old X\n", "- old Y\n"))
        before = self.main_head()
        code, doc = self.finish(files)
        self.assertEqual(code, 7, doc)
        self.assertIn("overlaps", doc["why"])
        self.assertEqual(self.main_head(), before)

    def test_promoted_folder_edited_after_checkout_is_refused(self):
        self.promote_ready()
        write(self.repo / REL / "word_tool.py", "print('sneaked in')\n")
        code, doc = self.finish(self.session_edits())
        self.assertEqual(code, 6)
        self.assertIn("/lab-run", doc["why"])

    def test_toolbox_and_wiki_are_required(self):
        self.promote_ready()
        files = self.session_edits()
        for subset in (["000_Wiki/index.md"], ["TOOLBOX.md"]):
            self.assertEqual(self.finish(subset)[0], 7, subset)

    def test_bad_file_paths_are_refused(self):
        self.promote_ready()
        files = self.session_edits()
        for bad in (f"{REL}/word_tool.py", f"001_Architecture/Lab/{PROJ}/Plan_Locked.md", "../x.md", "missing.md"):
            code, doc = self.finish(files + [bad])
            self.assertEqual(code, 7, bad)

    def test_a_file_that_predates_the_promotion_is_not_swept_in(self):
        write(self.repo / "000_Wiki/Architecture/Someone_Elses_Draft.md", "draft\n")
        time.sleep(0.05)
        self.promote_ready()
        files = self.session_edits() + ["000_Wiki/Architecture/Someone_Elses_Draft.md"]
        code, doc = self.finish(files)
        self.assertEqual(code, 7)
        self.assertIn("before /lab-promote started", doc["why"])

    def test_unlisted_changes_are_warned_not_committed(self):
        self.promote_ready()
        files = self.session_edits()
        write(self.repo / "000_Wiki/Architecture/Existing.md", "# Existing\n\n## Related\n- [[Word-Tool]]\n")
        code, doc = self.finish(files)
        self.assertEqual(code, 0, doc)
        self.assertTrue(any("Existing.md" in w for w in doc["warnings"]))
        self.assertNotIn("Word-Tool", sh(self.repo, "show", "main:000_Wiki/Architecture/Existing.md"))

    def test_secret_in_the_sessions_own_edit_is_refused(self):
        self.promote_ready()
        files = self.session_edits(toolbox_line=f"\n### Word Tool\n- key {FAKE_KEY}\n")
        before = self.main_head()
        code, doc = self.finish(files)
        self.assertEqual(code, 5)
        self.assertNotIn(FAKE_KEY, json.dumps(doc))
        self.assertEqual(self.main_head(), before)

    def test_graphify_failure_does_not_block(self):
        self.promote_ready()
        code, doc = self.finish(self.session_edits(), ok=False)
        self.assertEqual(code, 0, doc)
        self.assertFalse(doc["graphify"][0]["ok"])

    def test_failed_push_keeps_the_commit_and_rerun_only_pushes(self):
        self.promote_ready()
        files = self.session_edits()
        sh(self.repo, "remote", "set-url", "origin", str(Path(self.tmp.name) / "missing.git"))
        code, doc = self.finish(files)
        self.assertEqual(code, 9, doc)
        commit = doc["main_commit"]
        self.assertEqual(self.main_head(), commit)
        self.assertEqual(B.read_json(self.proj / P.PROMOTE_META)["stage"], "committed")
        sh(self.repo, "remote", "set-url", "origin", str(self.origin))
        code, doc = self.finish([], desc="")
        self.assertEqual(code, 0, doc)
        self.assertEqual(self.main_head(), commit)  # no second commit
        self.assertEqual(sh(self.origin, "rev-parse", "main").strip(), commit)

    def test_no_push_then_push(self):
        self.promote_ready()
        start_remote = sh(self.origin, "rev-parse", "main").strip()
        code, doc = self.finish(self.session_edits(), no_push=True)
        self.assertEqual(code, 0, doc)
        self.assertTrue(doc["push_skipped"])
        self.assertEqual(sh(self.origin, "rev-parse", "main").strip(), start_remote)
        self.assertEqual(self.finish([], desc="")[0], 0)
        self.assertEqual(sh(self.origin, "rev-parse", "main").strip(), self.main_head())

    def test_after_pushing_everything_refuses_to_run_again(self):
        self.promote_ready()
        self.assertEqual(self.finish(self.session_edits())[0], 0)
        self.assertEqual(self.finish([], desc="again")[0], 1)
        self.assertEqual(self.checkout()[0], 1)
        self.assertEqual(self.plan_cmd()[0], 1)

    def test_finish_before_checkout(self):
        self.grade(90)
        code, doc = self.finish(["TOOLBOX.md"])
        self.assertEqual(code, 1)
        self.assertIn("checkout", doc["why"])


class SmallPieces(Fixture):
    def test_registry_longest_prefix(self):
        doms = P.registry_domains(self.repo) + [("Tools", "001_Architecture/Tools")]
        self.assertEqual(P.domains_for([REL, "TOOLBOX.md", "000_Wiki/x.md"], doms),
                         [("Tools", "001_Architecture/Tools"), ("Wiki", "000_Wiki")])

    def test_secret_values_only_take_key_like_names(self):
        vals = P.secret_values(self.secrets)
        self.assertEqual(list(vals), ["OPENROUTER_API_KEY"])
        self.assertEqual(P.scan_text("nothing here", vals), [])

    def test_list_and_empty_argument(self):
        self.grade(90)
        code, doc = run(P.list_main, self.lab)
        self.assertEqual(code, 0)
        self.assertEqual([(r["project"], r["cleared_for_promote"]) for r in doc["projects"]], [(PROJ, True)])
        self.assertEqual(P.resolve(None, self.lab), self.proj)

    def test_cli(self):
        self.assertEqual(run(P.main, ["finish", str(self.proj)])[0], 1)
        self.assertEqual(run(P.main, ["bogus"])[0], 1)
        os.environ["AGENT_OS_DELEGATE_WORKER"] = "1"
        try:
            self.assertEqual(run(P.main, ["list"])[0], 3)
        finally:
            del os.environ["AGENT_OS_DELEGATE_WORKER"]


if __name__ == "__main__":
    unittest.main()
