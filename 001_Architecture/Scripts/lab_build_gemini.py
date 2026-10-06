#!/usr/bin/env python3
"""lab_build_gemini: /lab-build for the Gemini side (Antigravity), self-contained (Tony, 2026-10-06).

Usage:
  lab_build_gemini.py [<project>] [--into REL/PATH/Folder] [--model OPENROUTER_ID] [--cap USD]
                      [--review-model GEMINI_ID]
  lab_build_gemini.py [<project>] --dry-run      model pick + the free containment preflight only
  lab_build_gemini.py --check                    free setup check (SDK, keys, codex, review model)

<project> is a /lab-plan folder (name under 001_Architecture/Lab/ or a path). Empty = the newest
locked plan with no build yet (same rule as lab_build.py). To continue a project after a stop,
pass its folder: every run reads the project's state and carries on from there.

Why a self-contained script: same reason as lab_plan_gemini.py. Antigravity's IDE chat has no
headless mode and no subagents, so nothing can follow lab-build/SKILL.md the way Claude Code does.
The Claude Code /lab-build hands three steps to opus-standard subagents (the cited 25-point audit,
the one fix round, the one rebuild); here Gemini's top Pro model does those three through the
google-antigravity SDK (GEMINI_API_KEY from ~/.env-secrets). Everything else is lab_build.py
itself, imported and called unchanged (build, preflight, containment, check runner, scoring,
--finalize, --after-fix, --rebuild-prep, --score-rebuild): no git, sandbox or scoring logic here.

  1. Build: lab_build.py's build (picked OpenRouter model, network-off codex sandbox, git
     worktree, containment check, real acceptance checks, Build_Score.json written once).
  2. Audit: a Gemini agent with READ-ONLY tools (view/list/search, confined to Agent-OS, secret
     paths blocked) scores the 25-point rubric with quotes. It never writes: it answers, and THIS
     SCRIPT writes Build_Audit*.json and Build_Review.md, then runs --finalize. A read-only
     auditor cannot change the build before finalize, by construction.
  3. Fix round (only if the verdict says fix_round): a NEW Gemini agent whose write tools are
     allowed only for existing folders inside the build folder (absolute paths; no new
     subfolders, no commands, no network tools). It may call run_acceptance_checks, which runs
     the plan's checks in lab_build.py's own sandbox. Then --after-fix re-checks containment and
     re-scores; the auditor's 25 points carry over (no one grades their own fix).
  4. Rebuild (only if the verdict says rebuild): --rebuild-prep, a NEW Gemini agent builds the
     empty folder under the same write rules, --score-rebuild, a NEW Gemini auditor, --finalize.
     lab_build.py itself refuses a second fix round or a second rebuild.
  5. Prints a plain-words report and a last line "LAB_BUILD_GEMINI_RESULT {json}".

Spend: Gemini costs go on the Gemini API key at list price ($0 if the key is free tier) but count
against the same /lab project cap as OpenRouter, like lab_plan_gemini.py. Before each Gemini
stage, money already spent on this project (plan draft, builds, any Gemini plan review, earlier
Gemini stages) plus that stage's hard worst case must fit the cap; otherwise it stops with exit 5
and the rerun command. Each stage's record is in <project>/Build_Gemini.json.

Exit codes (lab_build.py's own, passed through): 0 finished (the verdict says lab_run or stop),
1 usage/prerequisite, 2 a key is missing, 3 refused inside a worker, 4 Codex config unreadable,
5 over the spend cap (ask Tony, rerun with --cap), 6 build failed/empty, 7 audit or score files
have problems, 8 CONTAINMENT STOP (show Tony, never fix), 124 timeout. Plus: 9 google-antigravity
SDK not installed, 10 a Gemini stage failed (log named).
"""
from __future__ import annotations

import asyncio
import contextlib
import io
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lab_build as B  # noqa: E402  (build, containment, checks, scoring, finalize: reused as-is)
import lab_plan_gemini as G  # noqa: E402  (Gemini model pick, ask/ask_valid, JSON parse, costs: reused)
from delegate import AGENT_OS, open_log  # noqa: E402
from jev_route import load_secret  # noqa: E402

L = B.L  # lab_plan_draft: cap, key name, project log
HARNESS = "antigravity"
GEMINI_META = "Build_Gemini.json"
# Hard ceilings per Gemini stage (whole session). Worst case at list price: audit $1.16, fix $1.28,
# rebuild $1.72. Real runs cost far less (the first Gemini plan review was ~$0.30).
BUDGETS = {
    "audit": {"max_input_tokens": 400_000, "max_output_tokens": 30_000, "max_tool_calls": 60},
    "fix": {"max_input_tokens": 400_000, "max_output_tokens": 40_000, "max_tool_calls": 60},
    "rebuild": {"max_input_tokens": 500_000, "max_output_tokens": 60_000, "max_tool_calls": 120},
}
TIMEOUTS = {"audit": 1200, "fix": 1500, "rebuild": 2400}  # seconds per stage
MAX_CHECK_RUNS = 4  # run_acceptance_checks calls per fix/rebuild session
MAX_STEPS = 14      # state-machine guard; a full raw->fix->rebuild->fix walk needs ~11
# Only these names are blocked inside the build folder (a build may legitimately hold e.g.
# secret_scan.py; lab_plan_gemini's wider "secret" pattern still guards the rest of Agent-OS).
SECRET_FILE = re.compile(r"(^|/)(\.env[^/]*|[^/]*\.pem|[^/]*\.key|id_rsa[^/]*)$", re.I)

AUDITOR_SYSTEM = (
    "You are the independent auditor for Tony's /lab-build command in his Agent-OS workspace "
    f"({AGENT_OS}). A cheaper model built a planned tool; a script already ran its acceptance checks. "
    "You have READ-ONLY tools (view files, list folders, search) confined to the workspace. You never "
    "write files and never run anything: answer each step in exactly the format asked, and a script saves "
    "your answer. Never print secrets, never read .env files or ~/.env-secrets. Be concrete: quote only "
    "lines you actually opened."
)
WRITER_SYSTEM = (
    "You are the {role} for Tony's /lab-build command in his Agent-OS workspace ({agent_os}). You may "
    "create and edit files ONLY inside the build folder {build_dir}, always with absolute paths, and only "
    "in folders that already exist there (no new subfolders). A tool policy refuses anything else. You "
    "cannot run commands; call run_acceptance_checks to run the plan's checks in the sandbox. Never "
    "delete or rename, never read .env files or ~/.env-secrets, never write a key into a file, never call "
    "paid APIs. Keys load from ~/.env-secrets at run time in the code you write; every paid call sits "
    "after a cost-estimate pause and every publish after a selection pause."
)

AUDIT_BRIEF = """Project folder: {proj}
Built folder: {build_dir} (built by {built_by}). Mechanical score file: {proj}/{score_file}

Read {proj}/Plan_Locked.md, {proj}/Acceptance_Checks.json, the score file (every check's real
result and output tail) and every file in the built folder. You cannot change anything; do not
try. No paid APIs, no network.

This audit has 2 steps; I will ask for them one at a time.

STEP 1 of 2 - score this 25-point rubric, 5 points each:
{rubric}
Reply with ONLY this JSON object (no code fence, no other text):
{{"items": [{{"id": "R1", "points": <0-5>, "cite_file": "<file path relative to the built folder, or {score_file}>",
   "cite_text": "one line copied exactly from that file, 8+ characters", "why": "plain words"}},
  ... the same for R2, R3, R4, R5],
 "failures_to_fix": ["specific named problems a small fix could solve, e.g. 'C11: validate exits 1, must be 2'"],
 "fix_would_exceed_third": true or false}}
Every item needs a real quoted line, even at full marks. A script checks each quote against the
file and gives 0 to any item whose quote it cannot find. fix_would_exceed_third = true if fixing
the named failures would rewrite more than about a third of the build's lines.
"""

AUDIT_REVIEW = """STEP 2 of 2 - Build_Review.md for Tony, in plain words: what was built, which checks failed
and why, what each rubric item found, and what a fix would change. Short, a blank line between
points. Do not use tools for this step. Reply with ONLY the Markdown."""

AUDIT_FIX = """lab_build.py --finalize found problems with the audit you wrote:
{problems}
Reply with ONLY the corrected audit JSON object, same format as STEP 1. Never change your view of
the build to fit a number; fix only what the problems name."""

FIX_PROMPT = """Fix round for Tony's /lab-build (the only one this project gets).
Build folder: {build_dir}
Plan: {proj}/Plan_Locked.md (its 'Wiring (Later, Tony-Approved)' section is not for you).
Exam: {proj}/Acceptance_Checks.json ($BUILD_DIR = the build folder). Audit: {proj}/Build_Review.md

Fix ONLY these named failures:
{failures}

Keep it small: well under a third of the build's lines (a script measures the change; a bigger one
is thrown out and triggers a rebuild). Edit or create files only inside the build folder, absolute
paths only. Never touch Acceptance_Checks.json, Plan_Locked.md or any Build_* file. You may call
run_acceptance_checks to confirm (at most {runs} times). When done, reply with ONLY a short Markdown
list (at most 5 lines) of what you changed, file by file."""

REBUILD_PROMPT = """Rebuild Tony's /lab project from scratch; the first build scored too low.
Build folder: {build_dir} (new; if files are already there from an interrupted attempt, finish them).
Plan: {proj}/Plan_Locked.md (build exactly this; its Wiring section is not for you).
Exam: {proj}/Acceptance_Checks.json ($BUILD_DIR = the build folder). You may read
{proj}/Build_Review.md to learn what went wrong, but write everything fresh.
Create files only inside the build folder, absolute paths only, named exactly as the plan names
them. Do not special-case the checks (no hardcoded expected outputs): a reviewer scores that
separately. Call run_acceptance_checks before finishing (at most {runs} times). Reply with ONLY a
short Markdown list (at most 8 lines): files created, which checks pass."""


class StageError(Exception):
    def __init__(self, msg: str, code: int = 10):
        super().__init__(msg)
        self.code = code


# ---------------------------------------------------------------- pure helpers (unit-tested)

def worst_case_usd(stage: str) -> float:
    b = BUDGETS[stage]
    return round(b["max_input_tokens"] / 1e6 * G.PRICE_IN + b["max_output_tokens"] / 1e6 * G.PRICE_OUT, 2)


def rubric_text() -> str:
    return "\n".join(f"   {rid} {what}" for rid, (_, what) in B.RUBRIC.items())


def audit_problems(doc: dict) -> list[str]:
    """Shape only. Whether each quote is real is lab_build.py --finalize's job (it scores 0)."""
    out = []
    items = doc.get("items") if isinstance(doc, dict) else None
    if not isinstance(items, list):
        return ["needs an 'items' list with R1-R5"]
    got = {i.get("id"): i for i in items if isinstance(i, dict)}
    for rid, (mx, _) in B.RUBRIC.items():
        it = got.get(rid)
        if it is None:
            out.append(f"rubric item {rid} missing")
            continue
        pts = it.get("points")
        if not isinstance(pts, (int, float)) or isinstance(pts, bool) or not 0 <= pts <= mx:
            out.append(f"{rid} points must be a number 0-{mx}")
        if not isinstance(it.get("cite_file"), str) or not it["cite_file"].strip():
            out.append(f"{rid} needs cite_file")
        if not isinstance(it.get("cite_text"), str) or len(it["cite_text"].strip()) < B.MIN_CITE_CHARS:
            out.append(f"{rid} cite_text must be one real line of {B.MIN_CITE_CHARS}+ characters")
        if not isinstance(it.get("why"), str) or not it["why"].strip():
            out.append(f"{rid} needs why")
    f = doc.get("failures_to_fix")
    if not isinstance(f, list) or not all(isinstance(x, str) for x in f):
        out.append("'failures_to_fix' must be a list of strings")
    if not isinstance(doc.get("fix_would_exceed_third"), bool):
        out.append("'fix_would_exceed_third' must be true or false")
    return out


def audit_doc(reply: dict, model: str, attempt: int) -> dict:
    return {"scored_by": model, "harness": f"{HARNESS} (lab_build_gemini.py)", "attempt": attempt,
            "items": [{k: i.get(k) for k in ("id", "points", "cite_file", "cite_text", "why")}
                      for i in reply["items"] if isinstance(i, dict) and i.get("id") in B.RUBRIC],
            "failures_to_fix": reply["failures_to_fix"],
            "fix_would_exceed_third": reply["fix_would_exceed_third"]}


def _wire_path(p: str) -> str:
    try:
        from google.antigravity.connections.local.local_connection_config import normalize_wire_path
        return normalize_wire_path(p)
    except ImportError:
        return p[7:] if p.startswith("file://") else p


def path_args(args) -> list[str]:
    """Every argument of a tool call that names a path (same keys lab_plan_gemini's reviewer checks)."""
    from_keys = ("path", "file_path", "directory_path", "TargetFile", "output_path")
    return [v for k, v in (args or {}).items()
            if isinstance(v, str) and (k in from_keys or k.lower().endswith(("path", "dir", "directory", "file")))]


def _inside(real: str, root: str) -> bool:
    return real.startswith(root + os.sep)


def read_ok(path: str, build_dir: str | None) -> bool:
    """lab_plan_gemini's read rule (inside Agent-OS, secret-looking names blocked), widened only so
    the build folder's own files can be read even if their name contains 'secret'."""
    if G.inside_workspace(path):
        return True
    if not build_dir:
        return False
    real = os.path.realpath(os.path.expanduser(_wire_path(str(path))))
    return _inside(real, os.path.realpath(build_dir)) and not SECRET_FILE.search(real)


def write_target_ok(path: str, build_dir: str) -> bool:
    """A write is allowed only to an absolute path strictly inside the build folder, whose folder
    already exists (no new subfolders), and that is not a link. Everything else is refused."""
    p = _wire_path(str(path))
    if not os.path.isabs(p) or os.path.islink(p):
        return False
    real, root = os.path.realpath(p), os.path.realpath(build_dir)
    return _inside(real, root) and os.path.isdir(os.path.dirname(real)) and not SECRET_FILE.search(real)


def write_args_ok(args, build_dir: str) -> bool:
    paths = path_args(args)
    return bool(paths) and all(write_target_ok(p, build_dir) for p in paths)  # no path named = refused


def stage_done(gm: dict, stage: str, attempt: int) -> bool:
    return any(s.get("stage") == stage and s.get("attempt") == attempt and s.get("ok") for s in gm.get("stages", []))


def gemini_spent(gm: dict) -> float:
    return round(sum(float(s.get("cost_usd_list_price") or 0) for s in gm.get("stages", [])), 4)


def plan_review_spent(project: str, log_path: Path | None = None) -> float:
    """Gemini /lab-plan review spend for this project, from the shared /lab log (lab_plan_gemini
    logs it there; it is not stored in the project folder)."""
    total = 0.0
    try:
        with open(log_path or L.LOG, encoding="utf-8") as fh:
            for line in fh:
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                if (e.get("event") == "review" and e.get("harness") == HARNESS and e.get("project") == project
                        and e.get("ok")):
                    total += float(e.get("cost_usd") or 0)
    except OSError:
        pass
    return round(total, 4)


def next_action(proj: Path, meta: dict, verdicts: dict, gm: dict) -> tuple[str, str]:
    """PURE-ish (reads file existence only). Where this project stands and what runs next."""
    w = B._current(meta)
    if not w:
        return "build", ""
    attempt, scores = w.get("attempt", 1), w.get("scores", {})
    if "raw" not in scores:
        sf = proj / B.SCORE_FILES[(attempt, "raw")]
        if sf.exists():
            try:
                verdict = B.read_json(sf).get("verdict")
            except (OSError, ValueError):
                verdict = "unreadable"
            return ("containment_stop" if verdict == "containment_stop" else "build_failed"), \
                f"{sf.name} says {verdict}"
        if attempt == 1:
            return "build_failed", ("the build worker did not finish (see Build_Meta.json). Retry only if Tony "
                                    "says so, with --model <id> (see lab_build.py --list).")
        return ("score_rebuild", "") if stage_done(gm, "rebuild", 2) else ("rebuild", "")
    hist = verdicts.get("history", [])
    if not any(h.get("attempt") == attempt and h.get("stage") == "raw" for h in hist):
        return ("finalize", "") if (proj / B.AUDIT_FILES[attempt]).exists() else ("audit", "")
    nxt = (verdicts.get("current") or {}).get("next")
    if nxt == "fix_round":
        return ("after_fix", "") if stage_done(gm, "fix", attempt) else ("fix", "")
    if nxt == "rebuild":
        return "rebuild_prep", ""
    if nxt in ("lab_run", "stop"):
        return "done", nxt
    return "unknown", f"Build_Verdict.json says next={nxt!r}"


# ---------------------------------------------------------------- project files

def load_gm(proj: Path) -> dict:
    p = proj / GEMINI_META
    try:
        return B.read_json(p) if p.exists() else {"stages": []}
    except (OSError, ValueError):
        return {"stages": []}


def record(proj: Path, entry: dict) -> None:
    gm = load_gm(proj)
    gm.setdefault("stages", []).append(dict(entry, t=time.strftime("%Y-%m-%dT%H:%M:%S")))
    B.write_json(proj / GEMINI_META, gm)


def project_spent(proj: Path, meta: dict, gm: dict) -> float:
    return round(B.spent_so_far(proj, meta) + gemini_spent(gm) + plan_review_spent(proj.name), 4)


def append_review(proj: Path, heading: str | None, text: str) -> None:
    p = proj / "Build_Review.md"
    old = p.read_text(encoding="utf-8") if p.exists() else ""
    body = text.strip() + "\n"
    if heading:
        body = f"## {heading}\n\n{body}"
    p.write_text((old.rstrip() + "\n\n" if old.strip() else "") + body, encoding="utf-8")


def capture(fn, *args, **kw) -> tuple[int, dict, str]:
    """Run a lab_build.py mode in-process, echo what it printed, and parse its LAB_BUILD_* line."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = fn(*args, **kw)
    text = buf.getvalue()
    if text.strip():
        print(text.rstrip(), flush=True)
    doc = {}
    for line in text.splitlines():
        for tag in ("LAB_BUILD_VERDICT ", "LAB_BUILD_RESULT ", "LAB_BUILD_PICK "):
            if line.startswith(tag):
                try:
                    doc = json.loads(line[len(tag):])
                except ValueError:
                    pass
    return rc, doc, text


# ---------------------------------------------------------------- Gemini side

def make_config(key: str, model: str, system: str, budget: dict, write_root: str | None = None,
                read_root: str | None = None, tools: tuple = ()):
    from google.antigravity import (BuiltinTools, CapabilitiesConfig, GeminiAPIEndpoint,
                                    GeminiModelOptions, LocalAgentConfig, ModelTarget, ThinkingLevel)
    from google.antigravity.types import BudgetConfig
    from google.antigravity.hooks import policy

    def reads(args) -> bool:
        return all(read_ok(p, read_root) for p in path_args(args))

    def writes(args) -> bool:
        return write_args_ok(args, write_root)

    read_tools = [BuiltinTools.VIEW_FILE, BuiltinTools.LIST_DIR, BuiltinTools.SEARCH_DIR, BuiltinTools.FIND_FILE]
    write_tools = [BuiltinTools.CREATE_FILE, BuiltinTools.EDIT_FILE] if write_root else []
    # deny by default: read tools inside Agent-OS only, write tools inside the build folder only,
    # plus the check runner. No run_command, web, URL, image or subagent tools at all.
    pol = [policy.deny_all()] + [policy.allow(t.value, when=reads, name="lab_build_read") for t in read_tools]
    pol += [policy.allow(t.value, when=writes, name="lab_build_write") for t in write_tools]
    pol += [policy.allow(fn.__name__, name="lab_build_checks") for fn in tools]
    target = ModelTarget(name=model, endpoint=GeminiAPIEndpoint(
        api_key=key, options=GeminiModelOptions(thinking_level=ThinkingLevel.HIGH)))
    return LocalAgentConfig(
        models=[target], api_key=key, system_instructions=system,
        capabilities=CapabilitiesConfig(enabled_tools=read_tools + write_tools, enable_subagents=False),
        tools=list(tools), policies=pol, workspaces=[AGENT_OS],
        env={"AGENT_OS_DELEGATE_WORKER": "1"},  # Agent-OS hooks stand down inside a worker
        budget_config=BudgetConfig(**budget))


def make_check_tool(proj: Path, build_dir: str, counter: dict):
    async def run_acceptance_checks() -> str:
        """Run every acceptance check of this /lab project against the build folder, inside the same
        network-off sandbox the scorer uses. Returns each check's id, whether it passed, its exit
        code and the end of its output. Can take a few minutes. Limited number of calls."""
        if counter["n"] >= MAX_CHECK_RUNS:
            return f"refused: run_acceptance_checks may be called at most {MAX_CHECK_RUNS} times per session"
        counter["n"] += 1
        results = await asyncio.to_thread(lambda: [B.run_check(c, build_dir) for c in B.load_checks(proj)])
        return json.dumps([{"id": r["id"], "passed": r["passed"], "exit_code": r["exit_code"], "what": r["what"],
                            "pass_if": r["pass_if"], "output_tail": r["output_tail"][-600:]} for r in results])
    return run_acceptance_checks


def default_factory(cfg):
    from google.antigravity import Agent
    return Agent(cfg)


def finalize(proj: Path) -> tuple[int, dict]:
    rc, doc, _ = capture(B.finalize_main, proj)
    return rc, doc


async def audit_stage(proj: Path, meta: dict, model: str, key: str, log, factory) -> dict:
    w = B._current(meta)
    attempt, score_name = w["attempt"], w["scores"]["raw"]["file"]
    audit_p = proj / B.AUDIT_FILES[attempt]
    fmt = {"proj": proj, "build_dir": w["build_dir"], "built_by": w.get("built_by"), "score_file": score_name,
           "rubric": rubric_text()}
    cfg = make_config(key, model, AUDITOR_SYSTEM, BUDGETS["audit"], read_root=w["build_dir"])
    wrote = []
    async with factory(cfg) as agent:
        reply = await G.ask_valid(agent, AUDIT_BRIEF.format(**fmt), G.extract_json, audit_problems, log, "audit JSON")
        B.write_json(audit_p, audit_doc(reply, model, attempt))
        wrote.append(audit_p.name)
        text = await G.ask_valid(agent, AUDIT_REVIEW, lambda t: t.strip() + "\n",
                                 lambda t: [] if len(t.strip()) > 20 else ["too short"], log, "Build_Review.md")
        append_review(proj, f"Rebuild Audit (Gemini, {model})" if attempt == 2 else None, text)
        wrote.append("Build_Review.md")
        rc, verdict = finalize(proj)
        if rc == 7 and not verdict.get("score_tampered"):  # one correction, audit file only (as in Claude's Step 3)
            reply = await G.ask_valid(agent, AUDIT_FIX.format(problems="\n".join(verdict.get("problems", []))),
                                      G.extract_json, audit_problems, log, "audit JSON")
            B.write_json(audit_p, audit_doc(reply, model, attempt))
            wrote.append(f"{audit_p.name} (fix)")
            rc, verdict = finalize(proj)
        usage = agent.conversation.total_usage
    return {"wrote": wrote, "usage": usage, "finalize_rc": rc, "verdict": verdict}


async def writer_stage(stage: str, proj: Path, meta: dict, verdicts: dict, model: str, key: str, log,
                       factory) -> dict:
    w = B._current(meta)
    counter = {"n": 0}
    tool = make_check_tool(proj, w["build_dir"], counter)
    role = "fixer (one fix round)" if stage == "fix" else "rebuilder (one rebuild)"
    system = WRITER_SYSTEM.format(role=role, agent_os=AGENT_OS, build_dir=w["build_dir"])
    if stage == "fix":
        failures = (verdicts.get("current") or {}).get("named_failures") or []
        prompt = FIX_PROMPT.format(build_dir=w["build_dir"], proj=proj, runs=MAX_CHECK_RUNS,
                                   failures="\n".join(f"- {f}" for f in failures) or "- (none named)")
    else:
        prompt = REBUILD_PROMPT.format(build_dir=w["build_dir"], proj=proj, runs=MAX_CHECK_RUNS)
    cfg = make_config(key, model, system, BUDGETS[stage], write_root=w["build_dir"], read_root=w["build_dir"],
                      tools=(tool,))
    async with factory(cfg) as agent:
        summary = await G.ask(agent, prompt, log)
        usage = agent.conversation.total_usage
    append_review(proj, f"{'Fix Round' if stage == 'fix' else 'Rebuild'} (Gemini, {model})", summary)
    return {"wrote": ["build folder", "Build_Review.md"], "usage": usage, "summary": summary[-2000:],
            "check_runs": counter["n"]}


def run_stage(stage: str, proj: Path, model: str, key: str, cap: float, factory, why: str = "") -> int:
    meta, verdicts, gm = B._meta(proj), B._verdicts(proj), load_gm(proj)
    w = B._current(meta)
    spent, worst = project_spent(proj, meta, gm), worst_case_usd(stage)
    if spent + worst > cap:
        print(f"lab_build_gemini: STOPPED, needs Tony's OK. This project has spent ${spent:.2f}; the Gemini "
              f"{stage} step could use up to ${worst:.2f} at list price, over the ${cap:.2f} cap. If Tony "
              f"approves, rerun: lab_build_gemini.py \"{proj}\" --cap <higher USD>", file=sys.stderr)
        return 5
    print(f"Gemini {stage} (attempt {w['attempt']}) on {model}{' (' + why + ')' if why else ''}, "
          f"worst case ${worst:.2f}...", flush=True)
    stamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    log_path, _, log = open_log(stamp, prefix=f"Agent-OS-Lab-Build-Gemini-{stage}")
    t0 = time.time()
    entry = {"stage": stage, "attempt": w["attempt"], "model": model, "log": str(log_path)}
    try:
        if stage == "audit":
            coro = audit_stage(proj, meta, model, key, log, factory)
        else:
            coro = writer_stage(stage, proj, meta, verdicts, model, key, log, factory)
        info = asyncio.run(asyncio.wait_for(coro, TIMEOUTS[stage]))
    except asyncio.TimeoutError:
        info, err, code = None, f"timed out after {TIMEOUTS[stage]}s", 124
    except G.ReviewError as exc:  # 5 = the stage's own token budget ran out
        info, err, code = None, str(exc), 5 if exc.code == 5 else 10
    except Exception as exc:  # SDK / network / quota errors
        info, err, code = None, f"{type(exc).__name__}: {str(exc)[:300]}", 10
    finally:
        log.close()
    secs = round(time.time() - t0, 1)
    if info is None:
        record(proj, dict(entry, ok=False, seconds=secs, error=err[:300]))
        L.log_event({"event": f"build_{stage}", "harness": HARNESS, "project": proj.name, "model": model,
                     "ok": False, "error": err[:200]})
        print(f"lab_build_gemini: Gemini {stage} FAILED: {err}. Log: {log_path}", file=sys.stderr)
        return code
    u = info.pop("usage", None)
    cost = G.review_cost(u)
    record(proj, dict(entry, ok=True, seconds=secs, cost_usd_list_price=cost,
                      tokens={"input": u.prompt_token_count, "cached": u.cached_content_token_count,
                              "output": u.candidates_token_count, "thinking": u.thoughts_token_count} if u else None,
                      **{k: v for k, v in info.items() if k in ("wrote", "summary", "check_runs", "finalize_rc")}))
    L.log_event({"event": f"build_{stage}", "harness": HARNESS, "project": proj.name, "model": model, "ok": True,
                 "attempt": w["attempt"], "cost_usd": cost})
    if stage == "audit" and info.get("finalize_rc"):
        v = info.get("verdict") or {}
        print("lab_build_gemini: --finalize refused the audit"
              + (" (score-before-edit broken; repair nothing, tell Tony)" if v.get("score_tampered") else "")
              + f": {v.get('problems')}", file=sys.stderr)
        return info["finalize_rc"]
    return 0


# ---------------------------------------------------------------- orchestration

def pick_model(key: str, override: str | None) -> tuple[str, str]:
    if override:
        return override, "--review-model override"
    return G.pick_review_model(G.list_gemini_models(key))


def drive(proj: Path, into: str | None, override: str | None, cap: float, review_model: str | None,
          key: str, factory=default_factory, repo: str = AGENT_OS) -> int:
    model, why = None, ""
    for _ in range(MAX_STEPS):
        meta, verdicts, gm = B._meta(proj), B._verdicts(proj), load_gm(proj)
        act, note = next_action(proj, meta, verdicts, gm)
        if act == "build_failed" and override and "raw" not in (B._current(meta) or {}).get("scores", {}) \
                and not (proj / B.SCORE_FILES[(1, "raw")]).exists():
            act = "build"  # Tony chose to retry the build on another model
        if act == "build":
            gem = gemini_spent(gm) + plan_review_spent(proj.name)
            if gem:
                print(f"(${gem:.2f} of the ${cap:.2f} cap already went to Gemini review; the build gets the rest)")
            print("Build - picked OpenRouter model in the network-off sandbox (lab_build.py, up to 30 min)...",
                  flush=True)
            rc, _, _ = capture(B.build_main, proj, into, override, round(cap - gem, 4), False, repo=repo)
            if rc:
                return rc
            continue
        if act in ("audit", "fix", "rebuild"):
            if model is None:
                model, why = pick_model(key, review_model)
            rc = run_stage(act, proj, model, key, cap, factory, why)
            if rc:
                return report(proj, rc)
            if act == "rebuild":  # say who really rebuilt it (lab_build.py's default label names opus-standard)
                meta = B._meta(proj)
                meta["worktrees"][-1]["built_by"] = f"{model} (rebuild, Gemini via lab_build_gemini.py)"
                B.write_json(proj / "Build_Meta.json", meta)
            continue
        if act == "finalize":
            rc, _ = finalize(proj)
        elif act == "after_fix":
            rc, _, _ = capture(B.after_fix_main, proj)
        elif act == "rebuild_prep":
            rc, _, _ = capture(B.rebuild_prep_main, proj, repo=repo)
        elif act == "score_rebuild":
            rc, _, _ = capture(B.score_rebuild_main, proj)
        elif act == "done":
            return report(proj, 0)
        elif act == "containment_stop":
            print(f"lab_build_gemini: CONTAINMENT STOP ({note}). No fix will be attempted; the worktree is left "
                  "as-is for Tony.", file=sys.stderr)
            return report(proj, 8)
        elif act == "build_failed":
            print(f"lab_build_gemini: {note}", file=sys.stderr)
            return report(proj, 6)
        else:
            print(f"lab_build_gemini: cannot continue: {note}", file=sys.stderr)
            return report(proj, 7)
        if rc:
            return report(proj, rc)
    print("lab_build_gemini: stopped after too many steps (state did not settle); tell Tony.", file=sys.stderr)
    return report(proj, 7)


def report(proj: Path, rc: int) -> int:
    meta, verdicts, gm = B._meta(proj), B._verdicts(proj), load_gm(proj)
    ws = meta.get("worktrees", [])
    first, cur = (ws[0] if ws else {}), verdicts.get("current") or {}
    hist = verdicts.get("history", [])
    raw = next((h for h in hist if h.get("stage") == "raw" and h.get("attempt") == 1), None)
    lines = ["", "=" * 70, "/lab-build (Gemini / Antigravity) result", "=" * 70]
    if first:
        lines.append(f"Built by: {first.get('built_by')} - {first.get('why_picked')}")
        lines.append(f"Build cost: ${float(first.get('cost_usd') or 0):.2f} (OpenRouter)")
    for s in gm.get("stages", []):
        lines.append(f"Gemini {s['stage']} (attempt {s['attempt']}): {s['model']}, "
                     + (f"about ${float(s.get('cost_usd_list_price') or 0):.2f} at list price" if s.get("ok")
                        else f"FAILED ({s.get('error')})"))
    if raw:
        sc = proj / B.SCORE_FILES[(1, "raw")]
        pts = B.read_json(sc).get("points", {}) if sc.exists() else {}
        lines.append(f"RAW score: {raw['total']}/100 = checks {pts.get('acceptance_60')}/60 + safety floor "
                     f"{pts.get('tier0_15')}/15 + Gemini audit {raw.get('audit_25')}/25")
    for h in hist:
        if h is raw:
            continue
        lines.append(f"Then {h.get('stage')} (attempt {h.get('attempt')}): total {h.get('total')}"
                     + (f", fix rewrote {round(100 * h['fix_ratio'])}% of the build" if h.get("fix_ratio") is not None else "")
                     + (f", exit {h['exit_code']}" if h.get("exit_code") else "") + f", next {h.get('next')}")
    if cur.get("named_failures"):
        lines.append("Named failures: " + "; ".join(cur["named_failures"][:8]))
    if ws:
        lines.append(f"Built folder: {ws[-1].get('build_dir')}")
        lines.append(f"Worktree: {ws[-1].get('worktree')}" + (" (older worktrees left for Tony)" if len(ws) > 1 else ""))
    review = proj / "Build_Review.md"
    if review.exists():
        lines += ["", "--- Build_Review.md ---", review.read_text(encoding="utf-8").strip()]
    nxt = cur.get("next")
    if rc == 0 and nxt == "lab_run":
        lines += ["", "CLEARED for Tony's first real paid run: /lab-run (Tony types it when ready). Look at:"]
        lines += [f"  - {x}" for x in verdicts.get("tony_paid_run", [])]
    elif rc == 0 and nxt == "stop":
        lines += ["", "Did not clear 80 after one fix round and one rebuild. Tony decides: adjust the plan with "
                      "/lab-plan, retry with --model, or drop it."]
    elif rc == 8:
        lines += ["", "CONTAINMENT STOP: the build touched something outside its folder. No fix is tried."]
    elif rc:
        hint = {5: "Over the spend cap (or a Gemini step's own token budget): ask Tony for a yes, then rerun "
                   "with --cap <higher USD>; it carries on from here.",
                6: "The build failed: ask Tony whether to retry on another model (--model <id>, see "
                   "lab_build.py --list). Never build it yourself.",
                10: "A Gemini step failed (log named above). Ask Tony whether to rerun (it carries on from "
                    "here) or try --review-model <id>.",
                124: "A step timed out. Ask Tony whether to rerun; it carries on from here."}
        lines += ["", f"Stopped with exit {rc}. " + hint.get(rc, "Show Tony the message above; do not fix or "
                                                                 "rewrite any score or audit file.")]
    print("\n".join(lines))
    result = {"ok": rc == 0, "exit_code": rc, "project_dir": str(proj), "next": nxt, "total": cur.get("total"),
              "cleared": cur.get("cleared"), "build_dir": ws[-1].get("build_dir") if ws else None,
              "worktree": ws[-1].get("worktree") if ws else None,
              "gemini_stages": [{k: s.get(k) for k in ("stage", "attempt", "model", "ok", "cost_usd_list_price")}
                                for s in gm.get("stages", [])],
              "tony_paid_run": verdicts.get("tony_paid_run")}
    print("LAB_BUILD_GEMINI_RESULT " + json.dumps(result, default=str))
    return rc


def check_main() -> int:
    ok, key = G.sdk_ok(), load_secret(G.KEY_NAME)
    print(f"google-antigravity SDK: {'installed' if ok else 'MISSING (pip3 install google-antigravity)'}")
    print(f"{G.KEY_NAME}: {'found in ~/.env-secrets' if key else 'MISSING'}")
    print(f"Build key {L.KEY_NAME}: {'found' if load_secret(L.KEY_NAME) else 'MISSING'}")
    print(f"codex CLI (build + check sandbox): {'found' if shutil.which('codex') else 'MISSING'}")
    print(f"Lab folder: {L.LAB_ROOT} {'exists' if L.LAB_ROOT.is_dir() else 'MISSING (never auto-created)'}")
    if key:
        model, why = G.pick_review_model(G.list_gemini_models(key))
        print(f"Review model: {model} ({why})")
    print("Gemini worst case per stage at list price: "
          + ", ".join(f"{s} ${worst_case_usd(s):.2f}" for s in BUDGETS) + f"; project cap ${L.PROJECT_CAP_USD:.2f}")
    return 0 if ok and key and shutil.which("codex") else 2


def main(argv: list[str]) -> int:
    if os.environ.get("AGENT_OS_DELEGATE_WORKER"):
        print("lab_build_gemini: refused, already inside a delegated worker", file=sys.stderr)
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
        into, override, cap_s, review_model = take("--into"), take("--model"), take("--cap"), take("--review-model")
        cap = float(cap_s) if cap_s else L.PROJECT_CAP_USD
    except ValueError as exc:
        print(f"lab_build_gemini: {exc}\n{__doc__}", file=sys.stderr)
        return 1
    dry = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]
    if len(args) > 1 or any(a.startswith("--") for a in args):
        print(__doc__)
        return 1
    if not shutil.which("codex"):
        print("lab_build_gemini: the codex CLI is not on PATH; the build sandbox needs it", file=sys.stderr)
        return 1
    proj = B.resolve_project(args[0] if args else None)
    if not proj:
        print("lab_build_gemini: no such project folder, and no locked unbuilt plan in 001_Architecture/Lab/. "
              "To continue a started build, pass its folder.", file=sys.stderr)
        return 1
    if dry:
        rc, _, _ = capture(B.build_main, proj, into.strip("/") if into else None, override, cap, True)
        return rc
    if not G.sdk_ok():  # fail before spending anything on a build
        print("lab_build_gemini: google-antigravity SDK not installed (pip3 install google-antigravity).",
              file=sys.stderr)
        return 9
    key = load_secret(G.KEY_NAME)
    if not key:
        print(f"lab_build_gemini: {G.KEY_NAME} missing from ~/.env-secrets.", file=sys.stderr)
        return 2
    print(f"Project: {proj}", flush=True)
    return drive(proj, into.strip("/") if into else None, override, cap, review_model, key)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
