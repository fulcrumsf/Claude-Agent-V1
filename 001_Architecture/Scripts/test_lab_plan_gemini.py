import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import lab_plan_draft as L
import lab_plan_gemini as G


class PickModelTests(unittest.TestCase):
    def test_highest_pro_version_wins_and_variants_are_skipped(self):
        names = ["models/gemini-2.5-pro", "models/gemini-3.1-pro-preview", "models/gemini-3.1-pro-preview-customtools",
                 "models/gemini-3-pro-image-preview", "models/gemini-3.8-flash", "models/gemini-pro-latest"]
        self.assertEqual(G.pick_review_model(names)[0], "gemini-3.1-pro-preview")

    def test_ga_beats_preview_at_same_version(self):
        self.assertEqual(G.pick_review_model(["gemini-3.1-pro-preview", "gemini-3.1-pro"])[0], "gemini-3.1-pro")

    def test_offline_falls_back(self):
        self.assertEqual(G.pick_review_model(None)[0], G.FALLBACK_REVIEW_MODEL)
        self.assertEqual(G.pick_review_model(["gemini-3.8-flash"])[0], G.FALLBACK_REVIEW_MODEL)


class ParseTests(unittest.TestCase):
    def test_json_with_fence_and_preamble(self):
        reply = 'Here it is:\n```json\n{"score": 82, "verdict": "lock", "reasons": ["a {x}"]}\n```'
        self.assertEqual(G.extract_json(reply)["score"], 82)

    def test_last_object_wins(self):
        self.assertEqual(G.extract_json('{"a": 1} then {"a": 2}')["a"], 2)

    def test_no_json_raises(self):
        with self.assertRaises(ValueError):
            G.extract_json("no json here")

    def test_score_rules_match_verify(self):
        self.assertEqual(G.score_problems({"score": 80, "verdict": "lock", "reasons": ["r"]}), [])
        self.assertEqual(G.score_problems({"score": 79, "verdict": "regenerate", "reasons": ["r"]}), [])
        self.assertTrue(G.score_problems({"score": 79, "verdict": "lock", "reasons": ["r"]}))
        self.assertTrue(G.score_problems({"score": 85.5, "verdict": "lock", "reasons": ["r"]}))
        self.assertTrue(G.score_problems({"score": True, "verdict": "regenerate", "reasons": ["r"]}))
        self.assertTrue(G.score_problems({"score": 90, "verdict": "lock", "reasons": []}))

    def test_check_rules(self):
        good = [{"id": f"C{i}", "tier": i % 3, "what": "w", "run": "true", "pass_if": "exit 0"} for i in range(3)]
        self.assertEqual(G.check_problems({"checks": good}), [])
        self.assertTrue(G.check_problems({"checks": good[:2]}))
        self.assertTrue(G.check_problems({"checks": good[:2] + [dict(good[2], tier=3)]}))
        self.assertTrue(G.check_problems({"checks": good[:2] + [dict(good[2], run="")]}))

    def test_plan_cleanup_and_sections(self):
        plan = G.clean_plan("Sure, here:\n```markdown\n# Plan: X\n## Goal\ng\n## Steps\ns\n## How To Verify\nv\n```")
        self.assertTrue(plan.startswith("# Plan: X"))
        self.assertNotIn("```", plan)
        self.assertEqual(G.plan_problems(plan), [])
        self.assertTrue(G.plan_problems("# Plan: X\n## Goal\n"))

    def test_frontmatter_shape_matches_claude_version(self):
        fm = G.frontmatter(72, "z-ai/glm-5.3", "gemini-3.1-pro-preview", True)
        self.assertEqual(fm, "---\nstatus: locked\nraw_draft_score: 72\ndrafted_by: z-ai/glm-5.3\n"
                             "locked_by: gemini-3.1-pro-preview\nregenerated: true\n---\n\n")


class SafetyTests(unittest.TestCase):
    def test_paths_confined_to_agent_os_and_secrets_blocked(self):
        self.assertTrue(G.inside_workspace(f"{G.AGENT_OS}/TOOLBOX.md"))
        self.assertTrue(G.inside_workspace(f"file://{G.AGENT_OS}/001_Architecture/Skills/lab/SKILL.md"))
        self.assertFalse(G.inside_workspace("/etc/hosts"))
        self.assertFalse(G.inside_workspace(os.path.expanduser("~/.env-secrets")))
        self.assertFalse(G.inside_workspace(f"{G.AGENT_OS}/.env"))
        self.assertFalse(G.inside_workspace(f"{G.AGENT_OS}/001_Architecture/../../../.ssh/id_rsa"))
        self.assertFalse(G.inside_workspace(f"{G.AGENT_OS}-evil/x.md"))

    def test_budget_fits_cap_with_typical_draft(self):
        self.assertLess(G.worst_case_review_usd() + 0.20, L.PROJECT_CAP_USD)

    def test_cost_math(self):
        u = SimpleNamespace(prompt_token_count=1_000_000, cached_content_token_count=500_000,
                            candidates_token_count=10_000, thoughts_token_count=10_000)
        self.assertAlmostEqual(G.review_cost(u), 0.5 * 2.0 + 0.5 * 0.2 + 0.02 * 12.0, places=4)

    def test_cost_never_negative_when_cached_exceeds_prompt(self):
        u = SimpleNamespace(prompt_token_count=96_441, cached_content_token_count=137_407,
                            candidates_token_count=2_247, thoughts_token_count=4_904)
        self.assertAlmostEqual(G.review_cost(u), 96_441 / 1e6 * 2.0 + 137_407 / 1e6 * 0.2 + 7_151 / 1e6 * 12.0, places=4)

    def test_draft_cost_takes_larger_number(self):
        self.assertEqual(G.draft_cost_of({"key_spend_delta_usd": 0.0001, "token_cost_usd": 0.0396}), 0.0396)
        self.assertEqual(G.draft_cost_of({}), 0.0)

    def test_refuses_inside_worker(self):
        os.environ["AGENT_OS_DELEGATE_WORKER"] = "1"
        try:
            self.assertEqual(G.main(["anything"]), 3)
        finally:
            del os.environ["AGENT_OS_DELEGATE_WORKER"]

    def test_review_refuses_changed_raw_draft(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            raw = p / "Draft_Raw.md"
            raw.write_text("# Plan: x\n")
            (p / "Draft_Meta.json").write_text(json.dumps({"model": "m", "draft_sha256": "0" * 64, "question": "q"}))
            self.assertEqual(G.main(["--review", d]), 7)


if __name__ == "__main__":
    unittest.main()
