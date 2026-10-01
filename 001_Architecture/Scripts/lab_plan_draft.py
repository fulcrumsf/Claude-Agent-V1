#!/usr/bin/env python3
"""lab_plan_draft: the picked-model draft step of /lab-plan (Tony, 2026-09-30).

Usage:
  lab_plan_draft.py "<question>" [--model ID] [--name Title_Slug] [--cap USD] [--lab-root PATH] [--dry-run]
  lab_plan_draft.py --verify <project_folder>
  lab_plan_draft.py --list

What it does (draft mode):
  1. Picks a model from a small curated candidate table (task type + price), checked against
     OpenRouter's live model list when reachable. Jev is never involved in /lab.
  2. Makes one project folder: 001_Architecture/Lab/YYYY-MM-DD_Title_Slug (suffix _2, _3 on collision).
  3. Runs `codex exec -s read-only` on that model through OpenRouter (same provider, key and
     isolation flags as delegate.py). The worker can read the workspace but never write to it;
     its final message IS the draft and lands in <project>/Draft_Raw.md (made read-only).
  4. Writes <project>/Draft_Meta.json (model, why, tokens, cost, draft hash) and prints a last
     line "LAB_PLAN_RESULT {json}" for the calling session.
  The Opus review (score raw draft, write acceptance checks, lock/regenerate) is NOT done here:
  the /lab-plan command's own session spawns `opus-standard` for it, then runs --verify.

Verify mode checks the review's files mechanically: Draft_Raw.md unchanged (hash), Score.json
valid and written before Plan_Locked.md (score-then-edit), Acceptance_Checks.json well formed
(then made read-only), Review.md present. Logs the score for picker calibration.

Exit codes: 0 ok, 1 usage error, 2 no OpenRouter key, 3 refused (inside a worker),
4 Codex config unreadable, 5 over spend cap (ask Tony to raise it with --cap),
6 draft failed / empty, 7 verify found problems, 124 worker timed out.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from delegate import (AGENT_OS, PROVIDER, ConfigReadError, isolation_overrides,  # noqa: E402
                      mcp_server_names, open_log)
from jev_route import load_secret  # noqa: E402

LAB_ROOT = Path(AGENT_OS) / "001_Architecture" / "Lab"
LOG = Path.home() / "Library" / "Logs" / "Agent-OS-Lab.jsonl"
KEY_NAME = "OPENROUTER_CHORES_KEY"  # existing key (Tony: no separate lab key for now)
WORKER_TIMEOUT = 1200  # seconds; a plan draft that runs longer is stopped
EFFORT = "medium"
PROJECT_CAP_USD = 2.00  # locked default per /lab project; over it = stop and ask Tony
PLAN_BUDGET_USD = 1.00  # a single plan draft's worst-case estimate must fit under this
EST_IN_TOKENS, EST_OUT_TOKENS = 400_000, 20_000  # worst-case agent-loop totals for one draft
KEY_RESERVE_USD = 1.00  # always leave this much on the shared key so Jev routing never starves
PASS_SCORE = 80
MODELS_URL = "https://openrouter.ai/api/v1/models"
KEY_URL = "https://openrouter.ai/api/v1/key"


@dataclass(frozen=True)
class Candidate:
    id: str
    in_price: float   # USD per 1M input tokens (OpenRouter list price, checked 2026-09-30)
    out_price: float  # USD per 1M output tokens
    note: str


# Curated first pass (2026-09-30), not a scraped leaderboard. Kept inside the families Tony
# already allows for cheap work (deepseek/qwen/z-ai/moonshotai/Gemini Flash) plus MiniMax, which
# the /lab spec names. Order in PREFERENCE = preference. Refine from the scores logged in
# ~/Library/Logs/Agent-OS-Lab.jsonl once ~10-15 graded runs exist.
CANDIDATES = {c.id: c for c in (
    Candidate("deepseek/deepseek-v4-pro-0813", 0.66, 1.98, "strong reasoning, lowest price of the strong tier"),
    Candidate("z-ai/glm-5.3", 1.40, 4.40, "strong agentic coding and tool use"),
    Candidate("qwen/qwen3.8-max-0902", 2.00, 6.00, "broad knowledge, long structured writing"),
    Candidate("google/gemini-3.8-flash", 0.75, 3.75, "fast, good at creative/content planning"),
    Candidate("moonshotai/kimi-k2.7-code", 0.671, 3.35, "code-focused"),
    Candidate("minimax/minimax-m3", 0.30, 1.20, "cheap code-capable fallback"),
)}
PREFERENCE = {
    "code": ["z-ai/glm-5.3", "deepseek/deepseek-v4-pro-0813", "moonshotai/kimi-k2.7-code", "minimax/minimax-m3"],
    "content": ["google/gemini-3.8-flash", "qwen/qwen3.8-max-0902", "deepseek/deepseek-v4-pro-0813"],
    "general": ["deepseek/deepseek-v4-pro-0813", "z-ai/glm-5.3", "qwen/qwen3.8-max-0902", "google/gemini-3.8-flash"],
}
CODE_WORDS = re.compile(r"\b(build|builder|script|scripts|code|pipeline|automat\w*|api|cli|tool|tools|bug|refactor|hook|hooks|"
                        r"python|app|website|integration|mcp|n8n|workflow|database|server|command)\b", re.I)
CONTENT_WORDS = re.compile(r"\b(video|videos|shorts?|thumbnails?|story|storyline|captions?|titles?|channel|"
                           r"content|posts?|carousel|brand|marketing|copy|etsy|listing|book|design|voiceover)\b", re.I)
STOPWORDS = {"a", "an", "the", "to", "for", "of", "and", "or", "in", "on", "with", "that", "this", "how", "i",
             "we", "me", "my", "our", "can", "could", "should", "would", "want", "need", "please", "is", "are",
             "it", "its", "be", "do", "does", "what", "which", "into", "from", "by", "so", "some", "about", "lets",
             "plan"}

RULES = (
    "You are the plan drafter for Tony's Agent-OS /lab-plan command. Rules, no exceptions:\n"
    "- You are READ-ONLY. Never create, edit, move or delete any file; never run anything that changes state. "
    "Your final message is the only output, and it IS the plan.\n"
    "- Never publish, send, upload, buy, or call paid APIs. Never print secrets or read ~/.env-secrets.\n"
    "- Ground the plan in what really exists. Before planning, read "
    f"{AGENT_OS}/TOOLBOX.md and the SKILL.md files or scripts the task touches (under "
    f"{AGENT_OS}/001_Architecture/Skills/ and {AGENT_OS}/001_Architecture/Scripts/). Read at most ~15 files. "
    "Only name a path as existing if you actually opened it.\n"
    "- The plan will later be built by a sandboxed builder that can ONLY create new files inside ONE new "
    "folder. So: never plan edits to existing files. Anything that must touch existing files (TOOLBOX.md, "
    "Skill-Index.md, hook configs, other pipelines) goes under 'Wiring' as a later Tony-approved step.\n"
    "- Every paid API call must sit after a cost-estimate pause for Tony; every publish after a selection "
    "pause. API keys load from ~/.env-secrets, never hardcoded.\n"
    "- If the ask is vague, lock it to the workspace's own skills and conventions instead of guessing, and "
    "list what you assumed.\n"
    "Final message: ONLY the plan, in exactly this Markdown structure:\n"
    "# Plan: <short title>\n"
    "## Goal\n(1-3 sentences: what done looks like for Tony)\n"
    "## Existing Pieces To Reuse\n(tools, skills, scripts, with the real paths you opened)\n"
    "## New Folder And Files\n(the ONE new folder: name in Title_Case_With_Underscores and where in the "
    "workspace it will live once promoted; every new file inside it and what each does)\n"
    "## Steps\n(numbered, concrete, file-level)\n"
    "## Spend And Safety Gates\n(every paid call, its pause, rough cost; keys; nothing publishes unapproved)\n"
    "## How To Verify\n(free checks a script can run: commands and expected results; then what only Tony's "
    "first real paid run can show)\n"
    "## Wiring (Later, Tony-Approved)\n(edits to existing files, if any)\n"
    "## Open Questions For Tony\n"
    "## Assumptions\n"
)


# ---------------------------------------------------------------- picking

def task_type(question: str) -> str:
    code, content = len(CODE_WORDS.findall(question)), len(CONTENT_WORDS.findall(question))
    if code == content == 0 or code == content:
        return "general"
    return "code" if code > content else "content"


def live_prices(timeout: float = 8.0) -> dict[str, tuple[float, float]] | None:
    """{model_id: (in $/M, out $/M)} from OpenRouter's public model list; None if unreachable."""
    try:
        with urllib.request.urlopen(MODELS_URL, timeout=timeout) as resp:
            data = json.load(resp)["data"]
        out = {}
        for m in data:
            p = m.get("pricing") or {}
            try:
                out[m["id"]] = (float(p.get("prompt", 0)) * 1e6, float(p.get("completion", 0)) * 1e6)
            except (TypeError, ValueError):
                continue
        return out
    except Exception:
        return None


def estimate(in_price: float, out_price: float) -> float:
    return round(EST_IN_TOKENS / 1e6 * in_price + EST_OUT_TOKENS / 1e6 * out_price, 4)


def pick(question: str, live: dict | None, override: str | None = None) -> list[dict]:
    """Ordered list of usable picks: [{id, in_price, out_price, est_usd, why}]. First = chosen,
    second = fallback if the first fails fast. `live` (None = offline) drops retired models
    and updates prices; with --model the override is the only pick."""
    ttype = task_type(question)
    ids = [override] if override else PREFERENCE[ttype]
    picks = []
    for mid in ids:
        base = CANDIDATES.get(mid)
        if live is not None and mid not in live:
            continue  # retired or renamed on OpenRouter
        if live is not None:
            inp, outp = live[mid]
        elif base:
            inp, outp = base.in_price, base.out_price
        else:
            inp = outp = 0.0  # unknown override while offline: cost unknown
        est = estimate(inp, outp)
        if not override and est > PLAN_BUDGET_USD:
            continue
        why = (f"--model override" if override else
               f"task type '{ttype}', preference #{PREFERENCE[ttype].index(mid) + 1}: {base.note}")
        picks.append({"id": mid, "in_price": round(inp, 4), "out_price": round(outp, 4),
                      "est_usd": est, "why": why, "task_type": ttype})
    return picks


# ---------------------------------------------------------------- project folder

def slug(question: str, max_words: int = 6) -> str:
    words = [w for w in re.findall(r"[A-Za-z0-9]+", question) if w.lower() not in STOPWORDS]
    parts = [w if w.isupper() and len(w) > 1 else w[:1].upper() + w[1:].lower() for w in words[:max_words]]
    return "_".join(parts)[:60].rstrip("_") or "Untitled"


def project_dir(root: Path, question: str, name: str | None = None, today: str | None = None) -> Path:
    base = f"{today or time.strftime('%Y-%m-%d')}_{name or slug(question)}"
    path, n = root / base, 2
    while path.exists():
        path, n = root / f"{base}_{n}", n + 1
    return path


# ---------------------------------------------------------------- running

def build_prompt(question: str) -> str:
    return f"{RULES}\nTony's /lab-plan question:\n{question}"


def build_command(prompt: str, model: str, cwd: str, last_msg_file: str, servers: list[str]) -> list[str]:
    cmd = ["codex", "exec", "--skip-git-repo-check", "-C", cwd, "-s", "read-only", "--json",
           "-c", PROVIDER, "-c", "model_provider=openrouter_chores"]
    for o in isolation_overrides(servers, effort=EFFORT):
        cmd += ["-c", o]
    return cmd + ["-m", model, "--output-last-message", last_msg_file, prompt]


def key_usage(key: str) -> dict | None:
    req = urllib.request.Request(KEY_URL, headers={"Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            d = json.load(resp)["data"]
        return {"usage": float(d.get("usage") or 0), "limit_remaining": d.get("limit_remaining")}
    except Exception:
        return None


def usage_from_log(log_path: Path) -> dict:
    """Sum token usage over every `turn.completed` event in the codex --json log."""
    tot = {"input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0}
    try:
        for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
            if '"turn.completed"' not in line:
                continue
            try:
                u = json.loads(line).get("usage") or {}
            except ValueError:
                continue
            for k in tot:
                tot[k] += int(u.get(k) or 0)
    except OSError:
        pass
    return tot


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_read_only(path: Path) -> None:
    path.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)


def log_event(event: dict) -> None:
    try:
        with open(LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"t": time.strftime("%Y-%m-%dT%H:%M:%S"), **event}) + "\n")
    except OSError:
        pass


def run_worker(cmd: list[str], key: str, log) -> tuple[int, float]:
    start = time.time()
    try:
        rc = subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                            timeout=WORKER_TIMEOUT,
                            env=dict(os.environ, **{KEY_NAME: key}, AGENT_OS_DELEGATE_WORKER="1")).returncode
    except subprocess.TimeoutExpired:
        rc = 124
    return rc, round(time.time() - start, 1)


def draft(question: str, override: str | None, name: str | None, cap: float, root: Path, dry: bool) -> int:
    key = load_secret(KEY_NAME)
    if not key:
        print(f"lab_plan_draft: {KEY_NAME} missing from ~/.env-secrets.", file=sys.stderr)
        return 2
    try:
        servers = mcp_server_names()
    except ConfigReadError as exc:
        print(f"lab_plan_draft: refused — {exc}. Can't confirm which MCP servers to disable, so the "
              "worker will not run isolated. Fix ~/.codex/config.toml and retry.", file=sys.stderr)
        return 4
    live = live_prices()
    picks = pick(question, live, override)
    if not picks:
        print(f"lab_plan_draft: no usable model ({'override not on OpenRouter' if override else 'every candidate retired or over budget'}). "
              "Run --list to see the table.", file=sys.stderr)
        return 6
    first = picks[0]
    if first["est_usd"] > cap:
        print(f"lab_plan_draft: STOPPED, needs Tony's OK. {first['id']} worst-case estimate ${first['est_usd']:.2f} "
              f"is over this project's ${cap:.2f} cap. If Tony approves, rerun with --cap <higher USD>.", file=sys.stderr)
        return 5
    before = key_usage(key)
    remaining = before.get("limit_remaining") if before else None
    if remaining is not None and float(remaining) < first["est_usd"] + KEY_RESERVE_USD:
        print(f"lab_plan_draft: STOPPED, needs Tony's OK. The shared OpenRouter key has ${float(remaining):.2f} left "
              f"this month; this draft could use ${first['est_usd']:.2f} and ${KEY_RESERVE_USD:.2f} is kept for Jev "
              "routing. Tony can raise the key's limit on openrouter.ai.", file=sys.stderr)
        return 5
    prompt = build_prompt(question)
    if dry:
        cmd = build_command(prompt, first["id"], AGENT_OS, "<project>/Draft_Raw.md", servers)
        print(" ".join(cmd[:-1]) + " <prompt>")
        print("LAB_PLAN_PICK " + json.dumps({"picks": picks, "live_list": live is not None,
                                              "project_dir": str(project_dir(root, question, name))}))
        return 0

    proj = project_dir(root, question, name)
    proj.mkdir(parents=False, exist_ok=False)  # Lab/ itself must already exist (never auto-created)
    raw = proj / "Draft_Raw.md"
    stamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    attempts, rc, secs, used = [], 6, 0.0, None
    for i, p in enumerate(picks[:2]):
        log_path, _, log = open_log(f"{stamp}-{i + 1}", prefix="Agent-OS-Lab-Plan")
        try:
            rc, secs = run_worker(build_command(prompt, p["id"], AGENT_OS, str(raw), servers), key, log)
        finally:
            log.close()
        ok = rc == 0 and raw.exists() and raw.read_text(encoding="utf-8").strip() != ""
        attempts.append({"model": p["id"], "exit_code": rc, "seconds": secs, "log": str(log_path),
                         "tokens": usage_from_log(log_path)})
        if ok:
            used = p
            break
        # Only a fast failure (model/provider error before real work) earns one retry on the next pick.
        if secs > 90 or rc == 124:
            break
    after = key_usage(key)
    meta = {"question": question, "project_dir": str(proj), "created": stamp, "attempts": attempts,
            "live_model_list": live is not None, "cap_usd": cap,
            "key_spend_delta_usd": round(after["usage"] - before["usage"], 4) if before and after else None,
            "key_spend_note": "delta on the shared key; Jev/chore calls in the same minutes are included"}
    if used:
        tok = attempts[-1]["tokens"]
        meta.update({"model": used["id"], "task_type": used["task_type"], "why_picked": used["why"],
                     "price_per_m_tokens": {"input": used["in_price"], "output": used["out_price"]},
                     "est_worst_case_usd": used["est_usd"],
                     "token_cost_usd": round(tok["input_tokens"] / 1e6 * used["in_price"]
                                             + tok["output_tokens"] / 1e6 * used["out_price"], 4),
                     "draft_sha256": sha256(raw)})
        make_read_only(raw)
    (proj / "Draft_Meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    spent = meta.get("key_spend_delta_usd") or meta.get("token_cost_usd") or 0
    log_event({"event": "draft", "project": proj.name, "model": meta.get("model"), "task_type": meta.get("task_type"),
               "ok": bool(used), "exit_code": rc, "cost_usd": spent})
    result = {"ok": bool(used), "exit_code": rc, "project_dir": str(proj), "draft": str(raw) if used else None,
              "model": meta.get("model"), "why_picked": meta.get("why_picked"),
              "cost_usd": spent, "over_cap": bool(spent and spent > cap)}
    if not used:
        print(f"lab_plan_draft: draft FAILED (exit {rc}). Logs: {', '.join(a['log'] for a in attempts)}",
              file=sys.stderr)
    elif result["over_cap"]:
        print(f"lab_plan_draft: WARNING, this draft cost ${spent:.2f}, over the ${cap:.2f} project cap. "
              "Tell Tony before spending more on this project.", file=sys.stderr)
    print("LAB_PLAN_RESULT " + json.dumps(result))
    return 0 if used else (124 if rc == 124 else 6)


# ---------------------------------------------------------------- verify

CHECK_FIELDS = ("id", "tier", "what", "run", "pass_if")


def verify(proj: Path) -> tuple[list[str], dict]:
    """Mechanical checks on the Opus review's output. Returns (problems, summary)."""
    problems, summary = [], {"project_dir": str(proj)}
    meta_p, raw = proj / "Draft_Meta.json", proj / "Draft_Raw.md"
    score_p, plan_p = proj / "Score.json", proj / "Plan_Locked.md"
    checks_p, review_p = proj / "Acceptance_Checks.json", proj / "Review.md"
    try:
        meta = json.loads(meta_p.read_text(encoding="utf-8"))
        summary["model"] = meta.get("model")
        if not raw.exists() or sha256(raw) != meta.get("draft_sha256"):
            problems.append("Draft_Raw.md was changed or removed after drafting (the raw draft must stay untouched)")
    except (OSError, ValueError) as exc:
        problems.append(f"Draft_Meta.json unreadable: {exc}")
    try:
        score = json.loads(score_p.read_text(encoding="utf-8"))
        s = score.get("score")
        if not isinstance(s, int) or not 0 <= s <= 100:
            problems.append("Score.json 'score' must be a whole number 0-100")
        else:
            summary["score"] = s
            want = "lock" if s >= PASS_SCORE else "regenerate"
            if score.get("verdict") != want:
                problems.append(f"Score.json verdict must be '{want}' for score {s} (threshold {PASS_SCORE})")
            summary["verdict"] = score.get("verdict")
        if not isinstance(score.get("reasons"), list) or not score.get("reasons"):
            problems.append("Score.json needs a non-empty 'reasons' list")
    except (OSError, ValueError) as exc:
        problems.append(f"Score.json missing or not valid JSON: {exc}")
    if not plan_p.exists() or not plan_p.read_text(encoding="utf-8").strip():
        problems.append("Plan_Locked.md missing or empty")
    elif score_p.exists() and score_p.stat().st_mtime > plan_p.stat().st_mtime:
        problems.append("Score.json was written after Plan_Locked.md (must score the raw draft BEFORE editing)")
    try:
        checks = json.loads(checks_p.read_text(encoding="utf-8"))
        items = checks.get("checks") if isinstance(checks, dict) else None
        if not isinstance(items, list) or len(items) < 3:
            problems.append("Acceptance_Checks.json needs a 'checks' list with at least 3 checks")
        else:
            for c in items:
                missing = [f for f in CHECK_FIELDS if not (isinstance(c, dict) and c.get(f) not in (None, ""))]
                if missing:
                    problems.append(f"check {c.get('id', '?') if isinstance(c, dict) else '?'} missing {missing}")
                elif c["tier"] not in (0, 1, 2):
                    problems.append(f"check {c['id']} tier must be 0, 1 or 2 (paid runs are Tony's, not a tier)")
            summary["checks"] = len(items)
    except (OSError, ValueError) as exc:
        problems.append(f"Acceptance_Checks.json missing or not valid JSON: {exc}")
    if not review_p.exists() or not review_p.read_text(encoding="utf-8").strip():
        problems.append("Review.md missing or empty")
    return problems, summary


def verify_main(proj: Path) -> int:
    if not proj.is_dir():
        print(f"lab_plan_draft: no such project folder {proj}", file=sys.stderr)
        return 1
    problems, summary = verify(proj)
    if not problems:
        make_read_only(proj / "Acceptance_Checks.json")  # the future builder must not edit its own exam
        make_read_only(proj / "Score.json")
    summary["ok"] = not problems
    summary["problems"] = problems
    log_event({"event": "verify", "project": proj.name, "model": summary.get("model"),
               "score": summary.get("score"), "verdict": summary.get("verdict"), "ok": not problems})
    print("LAB_PLAN_VERIFY " + json.dumps(summary))
    return 0 if not problems else 7


def list_main() -> int:
    live = live_prices()
    print(f"Live OpenRouter list: {'reachable' if live is not None else 'UNREACHABLE (static prices shown)'}")
    for ttype, ids in PREFERENCE.items():
        print(f"\n{ttype}:")
        for mid in ids:
            c = CANDIDATES[mid]
            inp, outp = live[mid] if live and mid in live else (c.in_price, c.out_price)
            flag = "" if live is None or mid in live else "  [NOT ON OPENROUTER NOW]"
            print(f"  {mid:32s} ${inp:.3f}/${outp:.3f} per M  worst-case ${estimate(inp, outp):.2f}  {c.note}{flag}")
    return 0


# ---------------------------------------------------------------- CLI

def main(argv: list[str]) -> int:
    if os.environ.get("AGENT_OS_DELEGATE_WORKER"):
        print("lab_plan_draft: refused, already inside a delegated worker", file=sys.stderr)
        return 3
    args = list(argv)
    if args[:1] == ["--list"]:
        return list_main()
    if args[:1] == ["--verify"]:
        if len(args) != 2:
            print(__doc__); return 1
        return verify_main(Path(args[1]))

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
        override, name, cap, root = take("--model"), take("--name"), take("--cap"), take("--lab-root")
        cap = float(cap) if cap else PROJECT_CAP_USD
    except ValueError as exc:
        print(f"lab_plan_draft: {exc}\n{__doc__}", file=sys.stderr)
        return 1
    dry = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]
    question = " ".join(args).strip()
    if not question:
        print(__doc__); return 1
    if name and not re.fullmatch(r"[A-Z0-9][A-Za-z0-9]*(_[A-Z0-9][A-Za-z0-9]*)*", name):
        print("lab_plan_draft: --name must be Title_Case_With_Underscores (e.g. Caption_Tool)", file=sys.stderr)
        return 1
    root_p = Path(root) if root else LAB_ROOT
    if not root_p.is_dir():
        print(f"lab_plan_draft: lab folder {root_p} does not exist; it is never auto-created. Ask Tony.",
              file=sys.stderr)
        return 1
    return draft(question, override, name, cap, root_p, dry)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
