import json
import os
import tempfile
import time
import unittest
from pathlib import Path

import delegate
import lab_plan_draft as L


class PickTests(unittest.TestCase):
    def test_task_types(self):
        self.assertEqual(L.task_type("build a python script for the ingest pipeline"), "code")
        self.assertEqual(L.task_type("thumbnail and title ideas for the channel"), "content")
        self.assertEqual(L.task_type("what should I do next quarter"), "general")

    def test_offline_uses_static_table_in_preference_order(self):
        picks = L.pick("write a python script", live=None)
        self.assertEqual([p["id"] for p in picks], L.PREFERENCE["code"])
        self.assertTrue(all(p["est_usd"] <= L.PLAN_BUDGET_USD for p in picks))

    def test_live_list_drops_retired_models_and_uses_live_prices(self):
        live = {"deepseek/deepseek-v4-pro-0813": (1.0, 2.0)}
        picks = L.pick("general question here", live=live)
        self.assertEqual([p["id"] for p in picks], ["deepseek/deepseek-v4-pro-0813"])
        self.assertEqual(picks[0]["in_price"], 1.0)

    def test_over_budget_candidates_are_skipped(self):
        live = {mid: (50.0, 50.0) for mid in L.CANDIDATES}
        self.assertEqual(L.pick("anything", live=live), [])

    def test_override_is_the_only_pick(self):
        picks = L.pick("anything", live={"x/y": (1.0, 1.0)}, override="x/y")
        self.assertEqual([p["id"] for p in picks], ["x/y"])
        self.assertEqual(L.pick("anything", live={}, override="x/y"), [])  # not on OpenRouter


class FolderTests(unittest.TestCase):
    def test_slug_is_title_case_and_skips_stopwords(self):
        self.assertEqual(L.slug("Plan a caption tool for the Neon Parcel shorts"), "Caption_Tool_Neon_Parcel_Shorts")
        self.assertEqual(L.slug("add MCP gateway"), "Add_MCP_Gateway")
        self.assertEqual(L.slug("???"), "Untitled")

    def test_collision_gets_suffix(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            first = L.project_dir(root, "caption tool", today="2026-09-30")
            self.assertEqual(first.name, "2026-09-30_Caption_Tool")
            first.mkdir()
            self.assertEqual(L.project_dir(root, "caption tool", today="2026-09-30").name, "2026-09-30_Caption_Tool_2")


class CommandTests(unittest.TestCase):
    def test_read_only_sandbox_openrouter_and_isolation(self):
        cmd = L.build_command("P", "z-ai/glm-5.3", "/tmp", "/tmp/out.md", servers=["blotato"])
        joined = " ".join(cmd)
        self.assertEqual(cmd[cmd.index("-s") + 1], "read-only")
        self.assertNotIn("workspace-write", joined)
        self.assertIn(delegate.PROVIDER, cmd)
        self.assertIn("model_provider=openrouter_chores", cmd)
        self.assertEqual(cmd[cmd.index("-m") + 1], "z-ai/glm-5.3")
        self.assertEqual(cmd[cmd.index("--output-last-message") + 1], "/tmp/out.md")
        for f in delegate.DISABLED_FEATURES:
            self.assertIn(f"features.{f}=false", cmd)
        self.assertIn("mcp_servers.blotato.enabled=false", cmd)
        self.assertEqual(cmd[-1], "P")

    def test_prompt_has_rules_then_question(self):
        p = L.build_prompt("caption tool")
        self.assertTrue(p.startswith(L.RULES))
        self.assertTrue(p.rstrip().endswith("caption tool"))
        self.assertIn("READ-ONLY", p)

    def test_refuses_inside_worker(self):
        os.environ["AGENT_OS_DELEGATE_WORKER"] = "1"
        try:
            self.assertEqual(L.main(["anything"]), 3)
        finally:
            del os.environ["AGENT_OS_DELEGATE_WORKER"]


class VerifyTests(unittest.TestCase):
    def make(self, d: Path, score=85, verdict="lock", score_first=True, checks=3):
        raw = d / "Draft_Raw.md"
        raw.write_text("# Plan: x\n", encoding="utf-8")
        (d / "Draft_Meta.json").write_text(json.dumps({"model": "m", "draft_sha256": L.sha256(raw)}))
        score_p, plan_p = d / "Score.json", d / "Plan_Locked.md"
        score_doc = json.dumps({"score": score, "verdict": verdict, "reasons": ["r"]})
        if score_first:
            score_p.write_text(score_doc)
            plan_p.write_text("plan")
        else:
            plan_p.write_text("plan")
            score_p.write_text(score_doc)
            t = time.time()
            os.utime(plan_p, (t - 10, t - 10))
        items = [{"id": f"C{i}", "tier": 0, "what": "w", "run": "true", "pass_if": "exit 0"} for i in range(checks)]
        (d / "Acceptance_Checks.json").write_text(json.dumps({"checks": items}))
        (d / "Review.md").write_text("review")

    def test_good_review_passes(self):
        with tempfile.TemporaryDirectory() as d:
            self.make(Path(d))
            problems, summary = L.verify(Path(d))
            self.assertEqual(problems, [])
            self.assertEqual(summary["score"], 85)

    def test_verdict_must_match_threshold(self):
        with tempfile.TemporaryDirectory() as d:
            self.make(Path(d), score=70, verdict="lock")
            self.assertTrue(any("verdict" in p for p in L.verify(Path(d))[0]))

    def test_score_written_after_plan_fails(self):
        with tempfile.TemporaryDirectory() as d:
            self.make(Path(d), score_first=False)
            self.assertTrue(any("after Plan_Locked" in p for p in L.verify(Path(d))[0]))

    def test_edited_raw_draft_fails(self):
        with tempfile.TemporaryDirectory() as d:
            self.make(Path(d))
            (Path(d) / "Draft_Raw.md").write_text("edited")
            self.assertTrue(any("Draft_Raw.md was changed" in p for p in L.verify(Path(d))[0]))

    def test_too_few_checks_fails(self):
        with tempfile.TemporaryDirectory() as d:
            self.make(Path(d), checks=2)
            self.assertTrue(any("at least 3" in p for p in L.verify(Path(d))[0]))


class UsageTests(unittest.TestCase):
    def test_sums_turn_usage(self):
        with tempfile.TemporaryDirectory() as d:
            log = Path(d) / "x.log"
            log.write_text('{"type":"turn.completed","usage":{"input_tokens":10,"output_tokens":2}}\n'
                           'noise\n{"type":"turn.completed","usage":{"input_tokens":5,"cached_input_tokens":1}}\n')
            self.assertEqual(L.usage_from_log(log), {"input_tokens": 15, "cached_input_tokens": 1, "output_tokens": 2})


if __name__ == "__main__":
    unittest.main()
