#!/usr/bin/env python3
"""lab_plan_gemini: /lab-plan for the Gemini side (Antigravity), self-contained (Tony, 2026-09-30).

Usage:
  lab_plan_gemini.py "<question>" [--model OPENROUTER_ID] [--name Title_Slug] [--cap USD] [--review-model GEMINI_ID]
  lab_plan_gemini.py --review <project_folder> [--review-model GEMINI_ID] [--cap USD]
  lab_plan_gemini.py --check

Why a self-contained script: the standalone `gemini` CLI is dead for Tony's account
(IneligibleTierError), and the Antigravity IDE chat has no headless mode, so there is no
"Gemini session following command instructions" the way Claude Code runs /lab-plan. This script
does the whole job itself, so it works the same whether Tony runs it in a terminal or the
Antigravity agent runs it for him (via the lab-plan-antigravity skill, once wired):

  1. Draft: runs lab_plan_draft.py unchanged (picked cheap OpenRouter model, read-only,
     $2/project cap, same project folder under 001_Architecture/Lab/).
  2. Review: calls Gemini's top Pro model through the google-antigravity SDK (separate process,
     GEMINI_API_KEY from ~/.env-secrets) with READ-ONLY tools confined to the Agent-OS folder.
     Same brief and rubric as the Claude Code reviewer (lab-plan/SKILL.md Step 2). The reviewer
     never writes files: it answers one step at a time and THIS SCRIPT writes Score.json first
     (then makes it read-only), and only then asks for the plan, the checks and Review.md.
     So score-before-edit holds by construction, not by trust.
  3. Verify: runs `lab_plan_draft.py --verify` unchanged (hash + mtime + format checks).
  4. Prints a plain-words report and a last line "LAB_PLAN_GEMINI_RESULT {json}".

--review runs steps 2-4 on an existing project (e.g. after a failed review). A Score.json that
already exists is never re-scored or rewritten; only missing files are filled in.
--check is a free setup check (SDK, key, which Pro model would review). No paid calls.

Exit codes: 0 ok, 1 usage error, 2 a key is missing, 3 refused (inside a worker),
4 Codex config unreadable (draft), 5 over spend cap (ask Tony; rerun with --cap),
6 draft failed, 7 verify found problems / raw draft changed, 8 review failed,
9 google-antigravity SDK not installed, 124 timed out.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lab_plan_draft as LPD  # noqa: E402  (reused as-is, never modified from here)
from delegate import AGENT_OS, open_log  # noqa: E402
from jev_route import load_secret  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent
DRAFT_SCRIPT = SCRIPTS / "lab_plan_draft.py"
KEY_NAME = "GEMINI_API_KEY"
MODELS_URL = "https://generativelanguage.googleapis.com/v1beta/models?pageSize=200"
FALLBACK_REVIEW_MODEL = "gemini-3.1-pro-preview"  # top Pro model on Tony's key, checked 2026-09-30
PRO_NAME = re.compile(r"^gemini-(\d+(?:\.\d+)?)-pro(-preview)?$")  # skips -image/-tts/-customtools variants
# Google list price for Gemini 3.x Pro preview, prompts <= 200K tokens (approximate, USD per 1M tokens).
# Thinking tokens bill as output. If Tony's key is on the free tier the real charge is $0.
PRICE_IN, PRICE_CACHED, PRICE_OUT = 2.00, 0.20, 12.00
# Hard ceiling on one review (whole session; input = uncached tokens). Worst case at list price =
# 500K*$2 + 40K*$12 = $1.48, so a typical draft (~$0.16) + review fits the $2 project cap.
BUDGET = {"max_input_tokens": 500_000, "max_output_tokens": 40_000, "max_tool_calls": 45}
REVIEW_TIMEOUT = 1200  # seconds for the whole review
DRAFT_TIMEOUT = 1500   # the draft script stops its own worker at 1200s
SECRET_PATH = re.compile(r"(^|/)(\.env[^/]*|[^/]*secret[^/]*|[^/]*\.pem|[^/]*\.key|id_rsa[^/]*)$", re.I)
PLAN_SECTIONS = ("## Goal", "## Steps", "## How To Verify")

REVIEWER_SYSTEM = (
    "You are the independent reviewer for Tony's /lab-plan command in his Agent-OS workspace "
    f"({AGENT_OS}). A cheaper model drafted a build plan; you score it, then lock or rewrite it. "
    "You have READ-ONLY tools (view files, list folders, search) confined to the workspace. You never "
    "write files: answer each step in exactly the format asked, and a script saves your answer. "
    "Never print secrets, never read .env files or ~/.env-secrets, never plan paid calls without a "
    "cost-estimate pause. Be concrete and grounded: only call a path real if you opened it."
)

BRIEF = """Project folder: {proj}
Tony's question: {question}

Read {proj}/Draft_Raw.md (a plan drafted by a cheaper model: {drafter}). Never edit it.
Check the draft against the real workspace: open the files, skills and tools it names and confirm
they exist and do what it says; check {agent_os}/001_Architecture/Skills/ and {agent_os}/TOOLBOX.md
for anything it should reuse; if the ask is vague (e.g. "add motion graphics"), the plan must lock
it to the workspace's own skill for that job. Read at most ~15 files.

Hard constraints the plan must meet (a future sandboxed builder enforces them):
- it only creates new files inside ONE new folder; no edits to existing files except a separate
  "Wiring (Later, Tony-Approved)" list (TOOLBOX.md, Skill-Index.md, hooks, other pipelines);
- every paid API call sits after a cost-estimate pause, every publish after a selection pause;
- API keys load from ~/.env-secrets, never hardcoded; nothing publishes without Tony's approval.

This review has 4 steps; I will ask for them one at a time. Do not build or run the plan.

STEP 1 of 4 - SCORE THE RAW DRAFT FIRST, before improving anything. Rubric (100 total):
grounding in real workspace files 30, answers Tony's actual question 20, buildable under the
one-new-folder / new-files-only rule with concrete file-level steps 20, spend and safety gates 15,
verifiable with free checks 15. Investigate with your tools, then reply with ONLY this JSON object
(no code fence, no other text):
{{"score": <whole number 0-100>, "verdict": "lock" if score >= 80 else "regenerate",
 "reasons": ["one line per rubric area: points given and why"]}}
"""

RESUME = """Project folder: {proj}
Tony's question: {question}
Draft by {drafter}: {proj}/Draft_Raw.md. Step 1 (the score) is already done and final, do not
re-score: score {score}, verdict "{verdict}", reasons: {reasons}
Hard constraints for the plan: new files inside ONE new folder only (edits to existing files go
under "Wiring (Later, Tony-Approved)"); every paid call after a cost-estimate pause, every publish
after a selection pause; keys from ~/.env-secrets, never hardcoded. You have read-only tools; read
the draft and whatever workspace files you need (at most ~15). Do not build or run the plan.
"""

STEP_PLAN = """STEP 2 of 4 - PLAN. Your score was {score}, verdict "{verdict}".
{mode}
Use the draft's section structure exactly: # Plan: <short title>, ## Goal, ## Existing Pieces To Reuse,
## New Folder And Files, ## Steps, ## Spend And Safety Gates, ## How To Verify,
## Wiring (Later, Tony-Approved), ## Open Questions For Tony, ## Assumptions.
Reply with ONLY the plan Markdown, starting with the line "# Plan:". No frontmatter (the script
adds it), no code fence, no other text."""
MODE_LOCK = ("Verdict is lock: keep the draft and fix its minor issues (wrong paths, missing gates, "
             "vague steps).")
MODE_REGEN = ("Verdict is regenerate: this is the one allowed retry. Write a new plan yourself from "
              "scratch, using the failures in your score reasons as context.")

STEP_CHECKS = """STEP 3 of 4 - ACCEPTANCE CHECKS for a future /lab-build of the plan you just wrote, written
now, before any code exists. At least 3 checks, all free to run (no paid APIs, no network).
Tier 0 = static/containment (files exist only inside $BUILD_DIR, secret scan, no hardcoded keys).
Tier 1 = structural (scripts parse, --help runs, imports resolve, model IDs exist in the workspace
pricing files, every paid call after its cost pause, every publish after its selection pause).
Tier 2 = measured output from free local steps on fixture files (ffprobe, ebur128, preview frames).
Paid runs are not a tier; list them under tony_paid_run. Use $BUILD_DIR for the new folder.
Reply with ONLY this JSON object (no code fence, no other text):
{{"checks": [{{"id": "C01", "tier": 0, "what": "plain words",
  "run": "shell command", "pass_if": "exact expected result, e.g. exit code 0 / output contains X"}}],
 "tony_paid_run": ["what Tony should look at on his first real paid run"]}}"""

STEP_REVIEW = """STEP 4 of 4 - Review.md for Tony, in plain words: score and verdict, what you changed (or why
you regenerated), how big the change was (none / minor / major, rough % of the plan rewritten),
and anything Tony must decide. Short, a blank line between points. Do not use tools for this step.
Reply with ONLY the Markdown."""

FIX = """verify found problems in {name}:
{problems}
Rewrite {name} only (Score.json is final and is never changed). Reply with ONLY the corrected
content, in the same format as before."""


class ReviewError(Exception):
    def __init__(self, msg: str, code: int = 8):
        super().__init__(msg)
        self.code = code


# ---------------------------------------------------------------- pure helpers (unit-tested)

def pick_review_model(names: list[str] | None) -> tuple[str, str]:
    """Highest-version Gemini Pro text model on the key (GA beats preview at the same version)."""
    best = None
    for n in names or []:
        m = PRO_NAME.match(n.removeprefix("models/"))
        if not m:
            continue
        rank = (tuple(int(x) for x in m.group(1).split(".")), 0 if m.group(2) else 1)
        if best is None or rank > best[0]:
            best = (rank, n.removeprefix("models/"))
    if best:
        return best[1], "highest Gemini Pro model on the key (live list)"
    return FALLBACK_REVIEW_MODEL, "fallback (live model list unavailable)"


def extract_json(text: str) -> dict:
    """The last top-level JSON object in a reply (tolerates code fences or a sentence before it)."""
    t = re.sub(r"```(?:json)?", "", text or "")
    dec, found, i = json.JSONDecoder(), None, 0
    while True:
        i = t.find("{", i)
        if i < 0:
            break
        try:
            obj, end = dec.raw_decode(t, i)
            if isinstance(obj, dict):
                found = obj
            i = end
        except ValueError:
            i += 1
    if found is None:
        raise ValueError("no JSON object in the reply")
    return found


def score_problems(doc: dict) -> list[str]:
    s, out = doc.get("score"), []
    if not isinstance(s, int) or isinstance(s, bool) or not 0 <= s <= 100:
        out.append("'score' must be a whole number 0-100")
    elif doc.get("verdict") != ("lock" if s >= LPD.PASS_SCORE else "regenerate"):
        out.append(f"'verdict' must be '{'lock' if s >= LPD.PASS_SCORE else 'regenerate'}' for score {s}")
    if not isinstance(doc.get("reasons"), list) or not doc["reasons"] or not all(isinstance(r, str) for r in doc["reasons"]):
        out.append("'reasons' must be a non-empty list of strings")
    return out


def check_problems(doc: dict) -> list[str]:
    """Same rules lab_plan_draft.verify applies to Acceptance_Checks.json."""
    items, out = doc.get("checks"), []
    if not isinstance(items, list) or len(items) < 3:
        return ["needs a 'checks' list with at least 3 checks"]
    for c in items:
        missing = [f for f in LPD.CHECK_FIELDS if not (isinstance(c, dict) and c.get(f) not in (None, ""))]
        if missing:
            out.append(f"check {c.get('id', '?') if isinstance(c, dict) else '?'} missing {missing}")
        elif c["tier"] not in (0, 1, 2) or isinstance(c["tier"], bool):
            out.append(f"check {c['id']} tier must be 0, 1 or 2 (paid runs are Tony's, not a tier)")
    if not isinstance(doc.get("tony_paid_run", []), list):
        out.append("'tony_paid_run' must be a list")
    return out


def clean_plan(text: str) -> str:
    """Drop anything before the '# Plan:' line and any wrapping code fence."""
    t = re.sub(r"^\s*```(?:markdown|md)?\s*\n|\n```\s*$", "", (text or "").strip())
    i = t.find("# Plan:")
    return (t[i:] if i >= 0 else t).strip() + "\n"


def plan_problems(plan: str) -> list[str]:
    out = [] if plan.lstrip().startswith("# Plan:") else ["must start with '# Plan:'"]
    return out + [f"missing section '{s}'" for s in PLAN_SECTIONS if s not in plan]


def frontmatter(score: int, drafter: str, reviewer: str, regenerated: bool) -> str:
    return ("---\nstatus: locked\n"
            f"raw_draft_score: {score}\ndrafted_by: {drafter}\nlocked_by: {reviewer}\n"
            f"regenerated: {'true' if regenerated else 'false'}\n---\n\n")


def review_cost(usage) -> float:
    if usage is None:
        return 0.0
    prompt = usage.prompt_token_count or 0
    cached = usage.cached_content_token_count or 0
    out = (usage.candidates_token_count or 0) + (usage.thoughts_token_count or 0)
    # The SDK's cumulative counts can report more cached than prompt tokens (seen 2026-09-30:
    # 96K prompt, 137K cached), i.e. prompt is then already the uncached part. Never go negative.
    uncached = prompt - cached if prompt >= cached else prompt
    return round(uncached / 1e6 * PRICE_IN + cached / 1e6 * PRICE_CACHED + out / 1e6 * PRICE_OUT, 4)


def draft_cost_of(meta: dict) -> float:
    """Larger of the shared-key spend delta (lags by minutes on OpenRouter) and the token-price cost."""
    return round(max(float(meta.get("key_spend_delta_usd") or 0), float(meta.get("token_cost_usd") or 0)), 4)


def worst_case_review_usd() -> float:
    return round(BUDGET["max_input_tokens"] / 1e6 * PRICE_IN + BUDGET["max_output_tokens"] / 1e6 * PRICE_OUT, 2)


def inside_workspace(path: str | None) -> bool:
    """True only for paths inside Agent-OS that do not look like secrets."""
    if not path:
        return True  # tool call without a path argument
    from google.antigravity.connections.local.local_connection_config import normalize_wire_path
    p = os.path.realpath(os.path.expanduser(normalize_wire_path(str(path))))
    root = os.path.realpath(AGENT_OS)
    return (p == root or p.startswith(root + os.sep)) and not SECRET_PATH.search(p)


# ---------------------------------------------------------------- Gemini side

def list_gemini_models(key: str) -> list[str] | None:
    try:  # key goes in a header, never in the URL
        req = urllib.request.Request(MODELS_URL, headers={"x-goog-api-key": key})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.load(resp)
        return [m["name"] for m in data.get("models", [])
                if "generateContent" in m.get("supportedGenerationMethods", [])]
    except Exception:
        return None


def make_agent_config(key: str, model: str):
    from google.antigravity import (BuiltinTools, CapabilitiesConfig, GeminiAPIEndpoint,
                                    GeminiModelOptions, LocalAgentConfig, ModelTarget, ThinkingLevel)
    from google.antigravity.types import BudgetConfig
    from google.antigravity.connections.local.local_connection_config import WIRE_PATH_ARGUMENT_KEYS
    from google.antigravity.hooks import policy

    def safe(args) -> bool:  # the SDK passes the tool call's argument dict
        paths = [v for k, v in (args or {}).items()
                 if k in WIRE_PATH_ARGUMENT_KEYS or k.lower().endswith(("path", "dir", "directory", "file"))]
        return all(inside_workspace(p) for p in paths if isinstance(p, str))

    read_tools = [BuiltinTools.VIEW_FILE, BuiltinTools.LIST_DIR, BuiltinTools.SEARCH_DIR, BuiltinTools.FIND_FILE]
    target = ModelTarget(name=model, endpoint=GeminiAPIEndpoint(
        api_key=key, options=GeminiModelOptions(thinking_level=ThinkingLevel.HIGH)))
    return LocalAgentConfig(
        models=[target],
        api_key=key,  # also covers the SDK's default image-model slot (image tool is disabled anyway)
        system_instructions=REVIEWER_SYSTEM,
        capabilities=CapabilitiesConfig(enabled_tools=read_tools, enable_subagents=False),
        # deny by default; read tools only, and only for paths inside Agent-OS that are not secrets
        policies=[policy.deny_all()] + [policy.allow(t.value, when=safe, name="lab_review_read") for t in read_tools],
        workspaces=[AGENT_OS],
        # any Agent-OS hook the harness might run (jev_route, delegate) stands down inside a worker
        env={"AGENT_OS_DELEGATE_WORKER": "1"},
        budget_config=BudgetConfig(**BUDGET),
    )


async def ask(agent, prompt: str, log) -> str:
    """One turn. Returns only the text after the last tool activity (the actual answer)."""
    from google.antigravity.types import StopReason, Text, ToolCall, ToolResult
    log.write(f"\n===== PROMPT {time.strftime('%H:%M:%S')}\n{prompt}\n")
    resp = await agent.chat(prompt)
    buf: list[str] = []
    async for ch in resp.chunks:
        if isinstance(ch, ToolCall):
            buf = []
            log.write(f"[tool] {ch.name} {json.dumps(ch.args, default=str)[:300]}\n")
        elif isinstance(ch, ToolResult):
            buf = []
            if ch.error:
                log.write(f"[tool error] {ch.error[:300]}\n")
        elif isinstance(ch, Text):
            buf.append(ch.text)
    text = "".join(buf).strip()
    log.write(f"===== REPLY ({resp.stop_reason})\n{text}\n")
    log.flush()
    if resp.stop_reason not in (None, StopReason.UNSPECIFIED):
        code = 5 if "EXCEEDED" in str(resp.stop_reason) else 8
        raise ReviewError(f"review stopped early: {resp.stop_reason} (budget {BUDGET})", code)
    if not text:
        raise ReviewError("reviewer returned an empty answer")
    return text


async def ask_valid(agent, prompt: str, parse, problems_of, log, what: str):
    """Ask, validate, and give the reviewer exactly one chance to correct a malformed answer."""
    reply = await ask(agent, prompt, log)
    for attempt in (1, 2):
        try:
            value = parse(reply)
            problems = problems_of(value)
        except ValueError as exc:
            value, problems = None, [str(exc)]
        if not problems:
            return value
        if attempt == 2:
            raise ReviewError(f"{what} still invalid after one correction: {problems}")
        reply = await ask(agent, f"That {what} is not valid: {problems}. Reply again with ONLY the corrected {what}.", log)


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


async def run_review(proj: Path, meta: dict, model: str, key: str, log) -> dict:
    from google.antigravity import Agent
    score_p, plan_p = proj / "Score.json", proj / "Plan_Locked.md"
    checks_p, review_p = proj / "Acceptance_Checks.json", proj / "Review.md"
    drafter, question = meta.get("model") or "unknown", meta.get("question") or ""
    fmt = {"proj": proj, "question": question, "drafter": drafter, "agent_os": AGENT_OS}
    info = {"wrote": []}
    async with Agent(make_agent_config(key, model)) as agent:
        if score_p.exists():
            score = json.loads(score_p.read_text(encoding="utf-8"))
            if score_problems(score):
                raise ReviewError(f"existing Score.json is invalid {score_problems(score)}; it is never rewritten. "
                                  "Tell Tony.", 7)
            await ask(agent, RESUME.format(score=score["score"], verdict=score["verdict"],
                                           reasons=json.dumps(score["reasons"]), **fmt)
                      + "\nReply with just: READY", log)
        else:
            score = await ask_valid(agent, BRIEF.format(**fmt), extract_json, score_problems, log, "score JSON")
            score = {"score": score["score"], "verdict": score["verdict"], "reasons": score["reasons"],
                     "scored_by": model}
            write_text(score_p, json.dumps(score, indent=2) + "\n")
            LPD.make_read_only(score_p)  # final: never edited after this line
            info["wrote"].append("Score.json")
        regen = score["verdict"] == "regenerate"
        if not plan_p.exists():
            body = await ask_valid(agent, STEP_PLAN.format(score=score["score"], verdict=score["verdict"],
                                                           mode=MODE_REGEN if regen else MODE_LOCK),
                                   clean_plan, plan_problems, log, "plan")
            write_text(plan_p, frontmatter(score["score"], drafter, model, regen) + body)
            info["wrote"].append("Plan_Locked.md")
        if not checks_p.exists():
            checks = await ask_valid(agent, STEP_CHECKS, extract_json, check_problems, log, "checks JSON")
            doc = {"plan": proj.name, "written_by": model, "checks": checks["checks"],
                   "tony_paid_run": checks.get("tony_paid_run", [])}
            write_text(checks_p, json.dumps(doc, indent=2) + "\n")
            info["wrote"].append("Acceptance_Checks.json")
        if not review_p.exists():
            text = await ask_valid(agent, STEP_REVIEW, lambda t: t.strip() + "\n",
                                   lambda t: [] if len(t.strip()) > 20 else ["too short"], log, "Review.md")
            write_text(review_p, text)
            info["wrote"].append("Review.md")

        problems = run_verify(proj)[1]
        fixable = {"Plan_Locked.md": plan_p, "Acceptance_Checks.json": checks_p, "Review.md": review_p}
        if problems and not any(("Score.json" in p or "Draft_Raw.md" in p or "Draft_Meta.json" in p) for p in problems):
            for name, path in fixable.items():
                mine = [p for p in problems if name in p or (name == "Acceptance_Checks.json" and p.startswith("check "))]
                if not mine:
                    continue
                reply = await ask(agent, FIX.format(name=name, problems="\n".join(mine)), log)
                if name == "Plan_Locked.md":
                    write_text(path, frontmatter(score["score"], drafter, model, regen) + clean_plan(reply))
                elif name == "Acceptance_Checks.json":
                    fixed = extract_json(reply)
                    write_text(path, json.dumps({"plan": proj.name, "written_by": model,
                                                 "checks": fixed.get("checks"),
                                                 "tony_paid_run": fixed.get("tony_paid_run", [])}, indent=2) + "\n")
                else:
                    write_text(path, reply.strip() + "\n")
                info["wrote"].append(f"{name} (fix)")
        info["usage"] = agent.conversation.total_usage
    info["score"] = score
    return info


# ---------------------------------------------------------------- draft + verify (reused scripts)

def run_draft(argv: list[str]) -> tuple[int, dict | None]:
    """Run lab_plan_draft.py unchanged, streaming its messages, and parse LAB_PLAN_RESULT."""
    print("Step 1/3 - drafting with a picked OpenRouter model (lab_plan_draft.py, up to 20 min)...", flush=True)
    try:
        proc = subprocess.run([sys.executable, str(DRAFT_SCRIPT), *argv], capture_output=True, text=True,
                              timeout=DRAFT_TIMEOUT)
    except subprocess.TimeoutExpired:
        return 124, None
    if proc.stderr.strip():
        print(proc.stderr.strip(), file=sys.stderr)
    result = None
    for line in proc.stdout.splitlines():
        if line.startswith("LAB_PLAN_RESULT "):
            result = json.loads(line[len("LAB_PLAN_RESULT "):])
    return proc.returncode, result


def run_verify(proj: Path) -> tuple[int, list[str], dict]:
    proc = subprocess.run([sys.executable, str(DRAFT_SCRIPT), "--verify", str(proj)],
                          capture_output=True, text=True, timeout=120)
    summary = {}
    for line in proc.stdout.splitlines():
        if line.startswith("LAB_PLAN_VERIFY "):
            summary = json.loads(line[len("LAB_PLAN_VERIFY "):])
    problems = summary.get("problems") or ([] if proc.returncode == 0 else [proc.stderr.strip() or "verify failed"])
    return proc.returncode, problems, summary


# ---------------------------------------------------------------- orchestration

def sdk_ok() -> bool:
    try:
        import google.antigravity  # noqa: F401
        return True
    except ImportError:
        return False


def review_main(proj: Path, review_model: str | None, cap: float) -> int:
    if not sdk_ok():
        print("lab_plan_gemini: google-antigravity SDK not installed (pip3 install google-antigravity).", file=sys.stderr)
        return 9
    key = load_secret(KEY_NAME)
    if not key:
        print(f"lab_plan_gemini: {KEY_NAME} missing from ~/.env-secrets.", file=sys.stderr)
        return 2
    try:
        meta = json.loads((proj / "Draft_Meta.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"lab_plan_gemini: {proj} has no readable Draft_Meta.json ({exc}).", file=sys.stderr)
        return 1
    raw = proj / "Draft_Raw.md"
    if not meta.get("draft_sha256") or not raw.exists() or LPD.sha256(raw) != meta["draft_sha256"]:
        print("lab_plan_gemini: Draft_Raw.md is missing, failed, or was changed after drafting. Not reviewing; "
              "tell Tony.", file=sys.stderr)
        return 7
    if (proj / "Plan_Locked.md").exists() and run_verify(proj)[0] == 0:
        print("Already reviewed and verified; nothing to do.")
        return report(proj, meta, None, cap)
    if review_model:
        model, why = review_model, "--review-model override"
    else:
        model, why = pick_review_model(list_gemini_models(key))
    draft_cost = draft_cost_of(meta)
    worst = worst_case_review_usd()
    if draft_cost + worst > cap:
        print(f"lab_plan_gemini: STOPPED, needs Tony's OK. Draft cost ${draft_cost:.2f} + review worst case "
              f"${worst:.2f} (Gemini list price) is over this project's ${cap:.2f} cap. If Tony approves, rerun: "
              f"lab_plan_gemini.py --review \"{proj}\" --cap <higher USD>", file=sys.stderr)
        return 5
    print(f"Step 2/3 - independent review on {model} ({why}), read-only, typically 2-6 min...", flush=True)
    stamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    log_path, _, log = open_log(stamp, prefix="Agent-OS-Lab-Review-Gemini")
    t0 = time.time()
    try:
        info = asyncio.run(asyncio.wait_for(run_review(proj, meta, model, key, log), REVIEW_TIMEOUT))
    except asyncio.TimeoutError:
        log.close()
        print(f"lab_plan_gemini: review timed out after {REVIEW_TIMEOUT}s. Log: {log_path}", file=sys.stderr)
        return 124
    except ReviewError as exc:
        log.close()
        print(f"lab_plan_gemini: review FAILED: {exc}. Log: {log_path}", file=sys.stderr)
        LPD.log_event({"event": "review", "harness": "antigravity", "project": proj.name, "model": model,
                       "ok": False, "error": str(exc)[:200]})
        return exc.code
    except Exception as exc:  # SDK / network / quota errors
        log.close()
        print(f"lab_plan_gemini: review FAILED ({type(exc).__name__}: {str(exc)[:300]}). Log: {log_path}",
              file=sys.stderr)
        LPD.log_event({"event": "review", "harness": "antigravity", "project": proj.name, "model": model,
                       "ok": False, "error": f"{type(exc).__name__}"})
        return 8
    log.close()
    u = info.get("usage")
    cost = review_cost(u)
    review = {"model": model, "seconds": round(time.time() - t0, 1), "cost_usd_list_price": cost,
              "tokens": {"input": u.prompt_token_count, "cached": u.cached_content_token_count,
                         "output": u.candidates_token_count, "thinking": u.thoughts_token_count} if u else None,
              "wrote": info["wrote"], "log": str(log_path)}
    LPD.log_event({"event": "review", "harness": "antigravity", "project": proj.name, "model": model, "ok": True,
                   "score": info["score"]["score"], "verdict": info["score"]["verdict"], "cost_usd": cost})
    return report(proj, meta, review, cap)


def report(proj: Path, meta: dict, review: dict | None, cap: float) -> int:
    print("Step 3/3 - mechanical verify (lab_plan_draft.py --verify)...", flush=True)
    rc, problems, summary = run_verify(proj)
    plan_p, review_p = proj / "Plan_Locked.md", proj / "Review.md"
    score = summary.get("score")
    draft_cost = draft_cost_of(meta)
    lines = ["", "=" * 70, "/lab-plan (Gemini / Antigravity) result", "=" * 70,
             f"Drafted by: {meta.get('model')} - {meta.get('why_picked')}",
             f"Draft cost: ${float(draft_cost):.2f} (OpenRouter)"]
    if review:
        lines.append(f"Reviewed by: {review['model']} in {review['seconds']}s, about ${review['cost_usd_list_price']:.2f} "
                     "at Gemini list price (Gemini API key; $0 if the key is free tier)")
    if score is not None:
        lines.append(f"Raw draft score: {score}/100 - "
                     + ("locked with minor fixes (80+)" if score >= LPD.PASS_SCORE else "below 80, rewritten by the reviewer"))
    lines.append(f"Acceptance checks: {summary.get('checks', '?')}   Folder: {proj}")
    lines.append("Verify: " + ("PASSED (Score.json + Acceptance_Checks.json now read-only)" if rc == 0
                               else f"FAILED: {problems}"))
    if review_p.exists():
        lines += ["", "--- Review.md ---", review_p.read_text(encoding="utf-8").strip()]
    if plan_p.exists():
        body = re.sub(r"^---\n.*?\n---\n\n?", "", plan_p.read_text(encoding="utf-8"), count=1, flags=re.S)
        lines += ["", "--- Locked plan ---", body.strip()]
    lines += ["", "Plan is ready for /lab-build (not built yet)." if rc == 0 else
              "Not ready: tell Tony what verify said. If it names Score.json or Draft_Raw.md, do not fix it."]
    print("\n".join(lines))
    result = {"ok": rc == 0, "project_dir": str(proj), "draft_model": meta.get("model"),
              "draft_cost_usd": draft_cost, "score": score, "verdict": summary.get("verdict"),
              "checks": summary.get("checks"), "review": review, "problems": problems, "cap_usd": cap}
    print("LAB_PLAN_GEMINI_RESULT " + json.dumps(result, default=str))
    return 0 if rc == 0 else 7


def check_main() -> int:
    ok = sdk_ok()
    key = load_secret(KEY_NAME)
    print(f"google-antigravity SDK: {'installed' if ok else 'MISSING (pip3 install google-antigravity)'}")
    print(f"{KEY_NAME}: {'found in ~/.env-secrets' if key else 'MISSING'}")
    print(f"Draft key {LPD.KEY_NAME}: {'found' if load_secret(LPD.KEY_NAME) else 'MISSING'}")
    print(f"Lab folder: {LPD.LAB_ROOT} {'exists' if LPD.LAB_ROOT.is_dir() else 'MISSING (never auto-created)'}")
    if key:
        names = list_gemini_models(key)
        model, why = pick_review_model(names)
        print(f"Review model: {model} ({why})")
    print(f"Review worst case per project: ${worst_case_review_usd():.2f} at list price (budget {BUDGET})")
    return 0 if ok and key else 2


def main(argv: list[str]) -> int:
    if os.environ.get("AGENT_OS_DELEGATE_WORKER"):
        print("lab_plan_gemini: refused, already inside a delegated worker", file=sys.stderr)
        return 3
    args = list(argv)
    if args[:1] == ["--check"]:
        return check_main()

    def take(flag):
        if flag not in args:
            return None
        i = args.index(flag)
        if i + 1 >= len(args) or args[i + 1].startswith("--"):
            raise ValueError(f"{flag} needs a value")
        val = args[i + 1]
        del args[i:i + 2]
        return val
    try:
        review_dir, review_model, cap_s = take("--review"), take("--review-model"), take("--cap")
        cap = float(cap_s) if cap_s else LPD.PROJECT_CAP_USD
    except ValueError as exc:
        print(f"lab_plan_gemini: {exc}\n{__doc__}", file=sys.stderr)
        return 1
    if review_dir:
        if args:
            print(f"lab_plan_gemini: unexpected arguments with --review: {args}", file=sys.stderr)
            return 1
        proj = Path(review_dir).expanduser().resolve()
        if not proj.is_dir():
            print(f"lab_plan_gemini: no such project folder {proj}", file=sys.stderr)
            return 1
        return review_main(proj, review_model, cap)
    if not [a for a in args if not a.startswith("--")]:
        print(__doc__)
        return 1
    if not sdk_ok():  # fail before spending anything on a draft
        print("lab_plan_gemini: google-antigravity SDK not installed (pip3 install google-antigravity).", file=sys.stderr)
        return 9
    if not load_secret(KEY_NAME):
        print(f"lab_plan_gemini: {KEY_NAME} missing from ~/.env-secrets.", file=sys.stderr)
        return 2
    draft_args = args + (["--cap", cap_s] if cap_s else [])
    rc, result = run_draft(draft_args)
    if rc != 0 or not result or not result.get("ok"):
        hints = {5: "Over the spend cap: ask Tony for a yes, then rerun with --cap <higher USD>.",
                 6: "Draft failed: ask Tony whether to retry on another model (--model <id>, see "
                    "lab_plan_draft.py --list). Do not write the plan yourself.",
                 124: "Draft timed out: ask Tony whether to retry on another model."}
        print(f"lab_plan_gemini: draft step stopped (exit {rc}). {hints.get(rc, 'Setup problem: show Tony the message above.')}",
              file=sys.stderr)
        return rc or 6
    print(f"Draft done: {result['model']} ({result.get('why_picked')}).", flush=True)
    return review_main(Path(result["project_dir"]), review_model, cap)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
