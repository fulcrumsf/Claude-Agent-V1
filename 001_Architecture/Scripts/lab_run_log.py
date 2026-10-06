#!/usr/bin/env python3
"""lab_run_log: the small mechanical half of /lab-run (Tony, 2026-10-03).

Usage:
  lab_run_log.py status [<project>]
      Is this project cleared by /lab-build for a real run? Prints LAB_RUN_STATUS {json}: build
      folder, worktree, /lab-build score, Tony's first-run notes from the verdict, every round
      logged so far, whether the folder changed since the last graded round, and whether the
      project is cleared for /lab-promote.
  lab_run_log.py log <project> --tried TEXT --notes TEXT --grade N [--changes TEXT]
      Appends ONE round to <project>/Run_Log.jsonl: what Tony tried, his notes, his 0-100 grade,
      what the harness changed before this try, and a fingerprint of the build folder exactly as
      he graded it. Prints LAB_RUN_LOGGED {json}.
  lab_run_log.py checks <project>
      Free regression smoke test after a harness fix: re-runs the plan's acceptance checks in the
      same network-off codex sandbox /lab-build used. Writes nothing; never a new score.

<project> is a folder name under 001_Architecture/Lab/ or a path. Empty (status only) = the newest
project /lab-build cleared (verdict next = lab_run) that /lab-run has not cleared yet.

Hard rule this script backs up: /lab-run never calls OpenRouter or lab_build.py's model picker and
never spends from the /lab budget. Fixes between rounds are made by the harness session itself.

Run_Log.jsonl is append-only by convention, not locked: each line carries the sha256 of the file
as it was before that line, so `status` can say if an earlier line was edited later. It is Tony's
grade of the BUILT TOOL; it shares nothing with any tool's own logs (e.g. Quality_Ledger.jsonl).

Exit codes: 0 ok, 1 usage / bad input / no project, 2 not cleared by /lab-build (status names the
step that is still needed), 3 refused (inside a delegated worker).
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lab_build as B  # noqa: E402  (manifest, check runner, verdict files: reused, not copied)

LAB_ROOT = B.LAB_ROOT
RUN_LOG = "Run_Log.jsonl"
PASS_GRADE = 80  # same threshold as the automated /lab-build score
SCHEMA = "lab_run/v1"

NEXT_STEP_HELP = {
    "opus_audit": "/lab-build Step 2 (the opus-standard audit), then Step 3 (--finalize)",
    "fix_round": "/lab-build Step 4 (the one fix round, then --after-fix)",
    "rebuild": "/lab-build Step 5 (the one rebuild)",
    "stop": "nothing in /lab-build: it ended without clearing 80. Tony decides: adjust the plan with "
            "/lab-plan, retry /lab-build with --model, or drop it",
}


def sha256_text(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def fingerprint(man: dict) -> str:
    return sha256_text(json.dumps(man, sort_keys=True).encode())


# ---------------------------------------------------------------- reading a project

def read_rounds(proj: Path) -> tuple[list[dict], list[str]]:
    """Every logged round plus any problems (bad JSON, an earlier line edited after the fact)."""
    p = proj / RUN_LOG
    if not p.exists():
        return [], []
    raw = p.read_bytes()
    rounds, problems, offset = [], [], 0
    for i, line in enumerate(raw.splitlines(keepends=True), 1):
        before = raw[:offset]
        offset += len(line)
        if not line.strip():
            continue
        try:
            doc = json.loads(line)
        except ValueError:
            problems.append(f"{RUN_LOG} line {i} is not valid JSON")
            continue
        if doc.get("prev_log_sha256") != sha256_text(before):
            problems.append(f"{RUN_LOG} line {i}: an earlier part of the log was edited after this round "
                            "was written (append-only broken; the grades may not be the originals)")
        rounds.append(doc)
    return rounds, problems


def gate(proj: Path) -> tuple[dict | None, str | None]:
    """The /lab-build result /lab-run starts from, or why it cannot start."""
    if not (proj / "Plan_Locked.md").exists():
        return None, "no locked plan here: run /lab-plan first"
    meta_p, verdict_p = proj / "Build_Meta.json", proj / "Build_Verdict.json"
    if not meta_p.exists():
        return None, "not built yet: run /lab-build first"
    if not verdict_p.exists():
        return None, f"built but not finalized: {NEXT_STEP_HELP['opus_audit']}"
    try:
        meta, verdict = B.read_json(meta_p), B.read_json(verdict_p)
    except (OSError, ValueError) as exc:
        return None, f"Build_Meta.json or Build_Verdict.json unreadable: {exc}"
    cur = verdict.get("current") or {}
    nxt = cur.get("next")
    if nxt != "lab_run" or not cur.get("cleared") or (cur.get("total") or 0) < PASS_GRADE:
        return None, (f"/lab-build has not cleared this build (latest verdict: next={nxt!r}, "
                      f"total={cur.get('total')}). Still needed: {NEXT_STEP_HELP.get(nxt, '/lab-build')}")
    w = (meta.get("worktrees") or [None])[-1]
    if not w or not Path(w.get("build_dir", "")).is_dir():
        return None, "Build_Meta.json names no build folder that exists on disk"
    return {"project_dir": str(proj), "plan": str(proj / "Plan_Locked.md"),
            "build_dir": w["build_dir"], "worktree": w["worktree"], "branch": w.get("branch"),
            "built_by": w.get("built_by"), "build_total": cur.get("total"), "build_stage": cur.get("stage"),
            "tony_paid_run": verdict.get("tony_paid_run", [])}, None


def folder_changes(old: dict, new: dict) -> dict:
    return {"added": sorted(set(new) - set(old)), "removed": sorted(set(old) - set(new)),
            "modified": sorted(k for k in set(old) & set(new) if old[k] != new[k])}


def status_doc(proj: Path, info: dict) -> dict:
    rounds, problems = read_rounds(proj)
    man = B.manifest(Path(info["build_dir"]))
    last = rounds[-1] if rounds else None
    changed = folder_changes(last.get("manifest", {}), man) if last else None
    unchanged = bool(last) and fingerprint(man) == last.get("folder_sha256")
    return dict(info, run_log=str(proj / RUN_LOG),
                rounds=[{"round": r.get("round"), "t": r.get("t"), "grade": r.get("grade"),
                         "passed": r.get("passed")} for r in rounds],
                latest_grade=last.get("grade") if last else None,
                folder_changed_since_last_round=(not unchanged) if last else None,
                changes_since_last_round=changed,
                cleared_for_promote=bool(last and last.get("passed") and unchanged),
                log_problems=problems)


def resolve(arg: str | None, root: Path = LAB_ROOT) -> Path | None:
    """A path or folder name, or None = newest project cleared by /lab-build, not yet by /lab-run."""
    if arg:
        return B.resolve_project(arg, root)
    eligible = []
    for d in (root.iterdir() if root.is_dir() else []):
        if d.is_dir():
            info, why = gate(d)
            if info and not status_doc(d, info)["cleared_for_promote"]:
                eligible.append(d)
    return max(eligible, key=lambda d: (d.name[:10], d.stat().st_mtime), default=None)


# ---------------------------------------------------------------- commands

def status_main(arg: str | None, root: Path = LAB_ROOT) -> int:
    proj = resolve(arg, root)
    if not proj:
        print("lab_run_log: " + ("no such project folder" if arg else
                                  "no project in 001_Architecture/Lab/ is waiting for /lab-run "
                                  "(none cleared by /lab-build, or all already cleared by /lab-run)"),
              file=sys.stderr)
        return 1
    info, why = gate(proj)
    if not info:
        B.emit("LAB_RUN_STATUS", {"ok": False, "project_dir": str(proj), "why": why})
        return 2
    B.emit("LAB_RUN_STATUS", dict(status_doc(proj, info), ok=True))
    return 0


def log_main(proj: Path, tried: str, notes: str, grade_text: str, changes: str) -> int:
    info, why = gate(proj)
    if not info:
        B.emit("LAB_RUN_LOGGED", {"ok": False, "project_dir": str(proj), "why": why})
        return 2
    try:
        grade = int(str(grade_text).strip())
    except ValueError:
        grade = None
    if grade is None or not 0 <= grade <= 100:
        print(f"lab_run_log: --grade must be a whole number 0-100, got {grade_text!r}", file=sys.stderr)
        return 1
    if not tried.strip() or not notes.strip():
        print("lab_run_log: --tried and --notes are both required (Tony's own words)", file=sys.stderr)
        return 1
    rounds, problems = read_rounds(proj)
    p = proj / RUN_LOG
    before = p.read_bytes() if p.exists() else b""
    if before and not before.endswith(b"\n"):
        before += b"\n"
        with open(p, "ab") as fh:
            fh.write(b"\n")
    man = B.manifest(Path(info["build_dir"]))
    last = rounds[-1] if rounds else None
    line = {"log": SCHEMA, "round": len(rounds) + 1, "t": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "project": proj.name, "build_dir": info["build_dir"], "built_by": info["built_by"],
            "build_total": info["build_total"],
            "changes_before_this_try": changes.strip(),
            "folder_changes_since_last_round": folder_changes(last.get("manifest", {}), man) if last else None,
            "tried": tried.strip(), "notes": notes.strip(), "grade": grade, "passed": grade >= PASS_GRADE,
            "folder_sha256": fingerprint(man), "manifest": man, "prev_log_sha256": sha256_text(before)}
    with open(p, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(line) + "\n")
    B.L.log_event({"event": "lab_run_grade", "project": proj.name, "round": line["round"], "grade": grade,
                   "passed": line["passed"], "built_by": info["built_by"], "build_total": info["build_total"]})
    B.emit("LAB_RUN_LOGGED", {"ok": True, "round": line["round"], "grade": grade, "passed": line["passed"],
                              "next": "lab_promote" if line["passed"] else "harness_fix_then_retry",
                              "run_log": str(p), "log_problems": problems})
    return 0


def checks_main(proj: Path) -> int:
    info, why = gate(proj)
    if not info:
        B.emit("LAB_RUN_CHECKS", {"ok": False, "project_dir": str(proj), "why": why})
        return 2
    results = [B.run_check(c, info["build_dir"]) for c in B.load_checks(proj)]
    failed = [f"{r['id']} ({r['what']})" for r in results if not r["passed"]]
    B.emit("LAB_RUN_CHECKS", {"ok": True, "passed": len(results) - len(failed), "total": len(results),
                              "failed": failed, "note": "smoke test only: no score file written, "
                              "the /lab-build score is unchanged",
                              "tails": {r["id"]: r["output_tail"][-400:] for r in results if not r["passed"]}})
    return 0


def main(argv: list[str]) -> int:
    if os.environ.get("AGENT_OS_DELEGATE_WORKER"):
        print("lab_run_log: refused, inside a delegated worker (/lab-run is harness-only)", file=sys.stderr)
        return 3
    args = list(argv)
    if not args or args[0] not in ("status", "log", "checks"):
        print(__doc__); return 1
    cmd, rest = args[0], args[1:]
    if cmd == "status":
        if len(rest) > 1:
            print(__doc__); return 1
        return status_main(rest[0] if rest else None)
    opts, pos = {}, []
    while rest:
        a = rest.pop(0)
        if a in ("--tried", "--notes", "--grade", "--changes"):
            if not rest:
                print(f"lab_run_log: {a} needs a value", file=sys.stderr); return 1
            opts[a[2:]] = rest.pop(0)
        else:
            pos.append(a)
    if len(pos) != 1:
        print(__doc__); return 1
    proj = B.resolve_project(pos[0])
    if not proj:
        print(f"lab_run_log: no such project folder: {pos[0]}", file=sys.stderr); return 1
    if cmd == "checks":
        if opts:
            print(__doc__); return 1
        if not shutil.which("codex"):
            print("lab_run_log: the codex CLI is not on PATH; the check sandbox needs it", file=sys.stderr)
            return 1
        return checks_main(proj)
    missing = [k for k in ("tried", "notes", "grade") if k not in opts]
    if missing:
        print("lab_run_log: log needs " + ", ".join("--" + m for m in missing), file=sys.stderr); return 1
    return log_main(proj, opts["tried"], opts["notes"], opts["grade"], opts.get("changes", ""))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
