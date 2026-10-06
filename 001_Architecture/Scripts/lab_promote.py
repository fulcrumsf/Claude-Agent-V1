#!/usr/bin/env python3
"""lab_promote: the mechanical half of /lab-promote (Tony, 2026-10-03).

Usage:
  lab_promote.py list
      Every /lab project /lab-build cleared, with its latest /lab-run grade and whether it is
      cleared for promotion. Prints LAB_PROMOTE_LIST {json}.
  lab_promote.py plan [<project>] [--accept-edited-log]
      Read-only. Gate + what would happen: destination path, every file, the /lab-run fixes that
      will first be committed to the lab branch, files left behind (gitignored), secret scan,
      local main commits that the push would also publish, the plan's remaining wiring items.
      Writes nothing. Prints LAB_PROMOTE_PLAN {json}.
  lab_promote.py checkout [<project>] [--accept-edited-log]
      Steps 1-3: gate (latest /lab-run grade 80+, folder unchanged since), commit the worktree's
      on-disk build folder to its OWN lab branch if anything is uncommitted (the /lab-run fixes),
      then `git checkout <that commit> -- <folder>` into the real workspace. Prints
      LAB_PROMOTE_CHECKOUT {json} and writes <project>/Promote_Meta.json.
  lab_promote.py finish [<project>] --description TEXT --file REL [--file REL ...]
                        [--trailer LINE ...] [--no-push]
      Steps 6-8, after the session wrote the TOOLBOX.md entry and the wiki page(s): graphify update
      on every affected domain, ONE commit on main holding only the promoted folder and the
      session's own edits to the listed files (other sessions' uncommitted edits in the same files
      stay uncommitted), push, then print the cleanup commands for Tony. Never runs them.
      Rerun after a failed push = push retry only. Prints LAB_PROMOTE_DONE {json}.

<project> is a folder name under 001_Architecture/Lab/ or a path. Empty = the one project that is
cleared for promotion and not promoted yet (refused if there are none or several).

Why the lab-branch commit first: /lab-build commits the RAW build to lab/<project>/wt<n>, but
/lab-run's fixes are edited in place and left uncommitted. Checking the branch out as-is would
promote stale, pre-fix code. So this script commits the folder exactly as Tony graded it (its
fingerprint must match his passing Run_Log.jsonl round) to the lab branch, never main, and only
then checks that commit's one folder out. A pathspec checkout cannot pull in anything else.

Approval: Tony typing /lab-promote with his own description IS the approval (to-do list, Part 4,
"/lab-promote scope confirmed", 2026-09-30). No extra prompt. Cleanup is never automatic.

Exit codes: 0 ok, 1 usage / no project / already promoted, 2 not cleared (names the /lab step
still needed), 3 refused inside a delegated worker, 4 workspace not ready (not on main, folder
already exists, plan does not name it, branch wrong), 5 secret found (nothing promoted or
committed), 6 promoted files do not match what Tony graded, 7 a listed file problem (merge
conflict with another session's uncommitted edit, unchanged, outside scope), 8 main moved during
the commit (nothing changed, rerun finish), 9 push failed (the commit stays local, rerun finish).
"""
from __future__ import annotations

import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lab_build as B  # noqa: E402  (git helpers, file kinds, manifest, folder checks: reused)
import lab_run_log as R  # noqa: E402  (the /lab-run gate and Run_Log.jsonl reader: reused)
from jev_route import SECRETS  # noqa: E402

LAB_ROOT = B.LAB_ROOT
PROMOTE_META = "Promote_Meta.json"
SCHEMA = "lab_promote/v1"
MAIN_BRANCH = "main"
PASS_GRADE = R.PASS_GRADE  # 80, the threshold everywhere in /lab
GRAPHIFY_TIMEOUT = 1800
REGISTRY_REL = "001_Architecture/Graphify/REGISTRY.md"
LAB_REL = "001_Architecture/Lab"

SECRET_NAME = re.compile(r"KEY|TOKEN|SECRET|PASSW|CREDENTIAL|AUTH", re.I)
MIN_SECRET_LEN = 16
SECRET_PATTERNS = (
    ("OpenRouter key", re.compile(r"sk-or-v1-[A-Za-z0-9]{20,}")),
    ("Anthropic key", re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}")),
    ("OpenAI-style key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_\-]{32,}")),
    ("GitHub token", re.compile(r"\b(?:ghp|gho|ghs|ghu)_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9\-]{10,}")),
    ("private key block", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----")),
)


class PromoteError(Exception):
    def __init__(self, code: int, why: str, **extra):
        super().__init__(why)
        self.code, self.why, self.extra = code, why, extra


# ---------------------------------------------------------------- git (every call goes through here)

def git_bytes(repo, *args, env: dict | None = None, data: bytes | None = None, check: bool = True,
              timeout: int = 300) -> tuple[int, bytes, str]:
    out = subprocess.run(["git", "-C", str(repo), *args], input=data, capture_output=True,
                         env=env, timeout=timeout)
    err = out.stderr.decode("utf-8", "replace")
    if check and out.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {err.strip()}")
    return out.returncode, out.stdout, err


def git(repo, *args, env: dict | None = None, check: bool = True, timeout: int = 300) -> str:
    return git_bytes(repo, *args, env=env, check=check, timeout=timeout)[1].decode("utf-8", "replace")


def head(repo) -> str:
    return git(repo, "rev-parse", "HEAD").strip()


def blob(repo, rev_path: str) -> bytes | None:
    rc, out, _ = git_bytes(repo, "cat-file", "blob", rev_path, check=False)
    return out if rc == 0 else None


def inside(path: str, rel: str) -> bool:
    path = path.rstrip("/")
    return path == rel or path.startswith(rel + "/")


def z_list(text: str) -> list[str]:
    return [t for t in text.split("\0") if t]


def tree_files(repo, commit: str, rel: str) -> dict[str, tuple[str, str]]:
    """path relative to the folder -> (mode, blob sha), for every file under rel in commit."""
    out = {}
    for rec in z_list(git(repo, "ls-tree", "-r", "-z", "--full-tree", commit, "--", rel)):
        meta, path = rec.split("\t", 1)
        mode, _typ, sha = meta.split()
        if inside(path, rel) and path != rel:
            out[path[len(rel) + 1:]] = (mode, sha)
    return out


def ignored_under(root, rel: str) -> set[str]:
    out = git(root, "ls-files", "-z", "--others", "--ignored", "--exclude-standard", "--", rel)
    return {p[len(rel) + 1:] for p in z_list(out) if inside(p, rel)}


def hash_paths(root, rels: list[str]) -> dict[str, str]:
    if not rels:
        return {}
    _, out, _ = git_bytes(root, "hash-object", "--stdin-paths", data=("\n".join(rels) + "\n").encode())
    return dict(zip(rels, out.decode().split()))


def folder_vs_commit(root, rel: str, commit: str) -> dict:
    """Compare the folder on disk under <root>/<rel> with <commit>'s copy. Gitignored files and
    Python caches are listed, never compared (they are never committed)."""
    folder = Path(root) / rel
    kinds = B.file_kinds(folder)
    links = sorted(r for r, k in kinds.items() if k != "file")
    on_disk = {r for r, k in kinds.items() if k == "file" and not B.skipped(r)}
    ignored = ignored_under(root, rel) & on_disk
    tracked = tree_files(root, commit, rel)
    compare = sorted(on_disk - ignored)
    shas = hash_paths(root, [f"{rel}/{r}" for r in compare])
    return {"missing": sorted(set(tracked) - on_disk),
            "extra": sorted(r for r in compare if r not in tracked),
            "differs": sorted(r for r in compare if r in tracked and shas[f"{rel}/{r}"] != tracked[r][1]),
            "ignored": sorted(ignored), "links": links, "files": sorted(tracked)}


def mismatch(doc: dict) -> list[str]:
    return [f"{k}: {', '.join(doc[k])}" for k in ("missing", "extra", "differs", "links") if doc[k]]


# ---------------------------------------------------------------- secrets (names only, never values)

def secret_values(path: Path = SECRETS) -> dict[str, str]:
    vals = {}
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError:
        return vals
    for line in lines:
        m = re.match(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*['\"]?([^'\"\s]+)", line)
        if m and SECRET_NAME.search(m.group(1)) and len(m.group(2)) >= MIN_SECRET_LEN:
            vals[m.group(1)] = m.group(2)
    return vals


def scan_text(text: str, values: dict[str, str]) -> list[str]:
    found = [f"value of {name} from ~/.env-secrets" for name, v in values.items() if v in text]
    found += [label for label, rx in SECRET_PATTERNS if rx.search(text)]
    return sorted(set(found))


def scan_folder(folder: Path, files: list[str], values: dict[str, str]) -> list[dict]:
    hits = []
    for rel in files:
        try:
            data = (folder / rel).read_bytes()
        except OSError:
            continue
        if b"\0" in data[:8192] or len(data) > 5_000_000:
            continue
        found = scan_text(data.decode("utf-8", "replace"), values)
        if found:
            hits.append({"file": rel, "found": found})
    return hits


# ---------------------------------------------------------------- the project

def read_meta(proj: Path) -> dict:
    p = proj / PROMOTE_META
    return B.read_json(p) if p.exists() else {}


def plan_title(plan_text: str) -> str | None:
    m = re.search(r"^# Plan:\s*(.+)$", plan_text, re.M)
    return m.group(1).strip() if m else None


def section(plan_text: str, heading_prefix: str) -> str | None:
    m = re.search(rf"^## {re.escape(heading_prefix)}[^\n]*$(.*?)(?=^## |\Z)", plan_text, re.M | re.S)
    return m.group(1) if m else None


def plan_names_folder(plan_text: str, rel: str) -> bool:
    sec = section(plan_text, "New Folder And Files")
    return bool(sec) and (f"`{rel}/`" in sec or f"`{rel}`" in sec)


def wiring_items(plan_text: str) -> list[str]:
    sec = section(plan_text, "Wiring") or ""
    return [ln.strip()[2:].strip() for ln in sec.splitlines() if ln.strip().startswith("- ")]


def lab_target(proj: Path) -> dict:
    """Where the build sits (worktree, branch, folder) and where it goes (the plan's path)."""
    meta = B.read_json(proj / "Build_Meta.json")
    rel = (meta.get("into") or "").strip("/")
    w = (meta.get("worktrees") or [None])[-1]
    if not rel or not w:
        raise PromoteError(4, "Build_Meta.json names no promoted path or worktree")
    wt, build_dir, branch = Path(w["worktree"]), Path(w["build_dir"]), w.get("branch") or ""
    if build_dir.resolve() != (wt / rel).resolve():
        raise PromoteError(4, f"build folder {build_dir} is not at the plan's path {rel} inside {wt}")
    if not branch.startswith("lab/"):
        raise PromoteError(4, f"worktree branch {branch!r} is not a lab/ branch; refusing to commit to it")
    if git(wt, "symbolic-ref", "-q", "HEAD", check=False).strip() != f"refs/heads/{branch}":
        raise PromoteError(4, f"the worktree {wt} is not on its lab branch {branch}; nothing was changed")
    plan_text = (proj / "Plan_Locked.md").read_text(encoding="utf-8")
    if not plan_names_folder(plan_text, rel):
        raise PromoteError(4, f"Plan_Locked.md's 'New Folder And Files' section does not name `{rel}/`; "
                              "the destination must come from the locked plan")
    common = git(wt, "rev-parse", "--path-format=absolute", "--git-common-dir").strip()
    return {"rel": rel, "worktree": str(wt), "build_dir": str(build_dir), "branch": branch,
            "repo": str(Path(common).parent), "plan_text": plan_text,
            "all_worktrees": [{"worktree": x["worktree"], "branch": x.get("branch")}
                              for x in meta.get("worktrees", [])]}


def promote_gate(proj: Path, accept_edited_log: bool = False) -> tuple[dict, dict]:
    """Only a build Tony himself graded 80+ in /lab-run, unchanged since, may be promoted."""
    info, why = R.gate(proj)
    if not info:
        raise PromoteError(2, f"/lab-build has not cleared this project, so /lab-run and /lab-promote "
                              f"cannot start: {why}")
    st = R.status_doc(proj, info)
    if not st["rounds"]:
        raise PromoteError(2, f"no /lab-run round is logged yet (no {R.RUN_LOG}). Run /lab-run first: "
                              "/lab-promote only takes a build Tony used for real and graded 80+.")
    if st["log_problems"] and not accept_edited_log:
        raise PromoteError(2, f"{R.RUN_LOG} was edited after it was written ("
                              + "; ".join(st["log_problems"]) + "). Show Tony; rerun with "
                              "--accept-edited-log only if he says the grades are right.")
    last = st["rounds"][-1]
    if not last.get("passed") or (last.get("grade") or 0) < PASS_GRADE:
        raise PromoteError(2, f"the latest /lab-run grade is {last.get('grade')} (round {last.get('round')}), "
                              f"below {PASS_GRADE}. Run /lab-run again: fix, retry, re-grade until 80+.")
    if st["folder_changed_since_last_round"]:
        ch = st["changes_since_last_round"] or {}
        files = ", ".join(ch.get("added", []) + ch.get("modified", []) + ch.get("removed", []))
        raise PromoteError(2, f"the build folder changed after Tony's passing grade ({files}). Run one more "
                              "/lab-run round so the grade matches what would be promoted.")
    return info, st


def last_manifest(proj: Path) -> dict:
    rounds, _ = R.read_rounds(proj)
    return rounds[-1].get("manifest", {}) if rounds else {}


def lab_pending(t: dict) -> dict:
    wt, rel = t["worktree"], t["rel"]
    staged_outside = [p for p in z_list(git(wt, "diff", "--cached", "--name-only", "-z")) if not inside(p, rel)]
    pending = [(x[:2], x[3:]) for x in z_list(git(wt, "status", "--porcelain=v1", "-z", "--no-renames",
                                                  "--untracked-files=all", "--", rel))]
    outside = [x[3:] for x in z_list(git(wt, "status", "--porcelain=v1", "-z", "--no-renames",
                                        "--untracked-files=all")) if not inside(x[3:], rel)]
    return {"staged_outside": staged_outside, "outside_changes": outside,
            "uncommitted": [{"status": xy.strip(), "path": p[len(rel) + 1:] if inside(p, rel) else p}
                            for xy, p in pending]}


def main_state(repo: str) -> dict:
    ref = git(repo, "symbolic-ref", "-q", "HEAD", check=False).strip()
    remote = git(repo, "config", f"branch.{MAIN_BRANCH}.remote", check=False).strip()
    merge = git(repo, "config", f"branch.{MAIN_BRANCH}.merge", check=False).strip()
    unpushed = []
    if remote and merge.startswith("refs/heads/"):
        tracking = f"refs/remotes/{remote}/{merge[len('refs/heads/'):]}"
        rc, out, _ = git_bytes(repo, "rev-list", "--oneline", f"{tracking}..refs/heads/{MAIN_BRANCH}", check=False)
        unpushed = out.decode().splitlines() if rc == 0 else []
    return {"on_main": ref == f"refs/heads/{MAIN_BRANCH}", "ref": ref, "remote": remote, "merge": merge,
            "unpushed_commits": unpushed}


def resolve(arg: str | None, root: Path = LAB_ROOT) -> Path:
    if arg:
        proj = B.resolve_project(arg, root)
        if not proj:
            raise PromoteError(1, f"no such project folder: {arg}")
        return proj
    ready = [d for d in sorted(root.iterdir()) if d.is_dir() and _cleared(d)
             and read_meta(d).get("stage") != "pushed"] if root.is_dir() else []
    if len(ready) != 1:
        raise PromoteError(1, "no project is cleared for /lab-promote" if not ready else
                           "several projects are cleared for /lab-promote, name one: "
                           + ", ".join(d.name for d in ready))
    return ready[0]


def _cleared(proj: Path) -> bool:
    try:
        promote_gate(proj)
        return True
    except (PromoteError, OSError, ValueError, KeyError):
        return False


# ---------------------------------------------------------------- assess (read-only, shared by plan + checkout)

def assess(proj: Path, accept_edited_log: bool, secrets_path: Path) -> tuple[dict, dict, list[str]]:
    info, st = promote_gate(proj, accept_edited_log)
    t = lab_target(proj)
    repo, rel, wt = t["repo"], t["rel"], t["worktree"]
    pm = read_meta(proj)
    problems = []
    ms = main_state(repo)
    if not ms["on_main"]:
        problems.append(f"the real workspace is on {ms['ref'] or 'a detached HEAD'}, not {MAIN_BRANCH}; "
                        "promotion commits to main only")
    resuming = pm.get("stage") == "checked_out"
    if not resuming:
        problems += B.into_check(repo, head(repo), rel)  # brand-new folder, tracked parent, not ignored
    staged_main = z_list(git(repo, "diff", "--cached", "--name-only", "-z", "--", rel))
    if staged_main and not resuming:
        problems.append(f"the real workspace already has staged changes under {rel}")
    lp = lab_pending(t)
    if lp["staged_outside"]:
        problems.append("the worktree has staged changes outside the build folder: " + ", ".join(lp["staged_outside"]))
    kinds = B.file_kinds(Path(t["build_dir"]))
    links = sorted(r for r, k in kinds.items() if k != "file")
    if links:
        problems.append("links or special files inside the build folder (only plain files are promoted): "
                        + ", ".join(links))
    files = sorted(r for r, k in kinds.items() if k == "file" and not B.skipped(r))
    ignored = sorted(ignored_under(wt, rel) & set(files))
    hits = scan_folder(Path(t["build_dir"]), [f for f in files if f not in ignored], secret_values(secrets_path))
    doc = {"project": proj.name, "project_dir": str(proj), "title": plan_title(t["plan_text"]),
           "destination": str(Path(repo) / rel), "rel": rel, "repo": repo,
           "worktree": wt, "branch": t["branch"], "build_dir": t["build_dir"],
           "build_total": info["build_total"], "built_by": info["built_by"],
           "grades": [r["grade"] for r in st["rounds"]], "rounds": len(st["rounds"]),
           "files": [f for f in files if f not in ignored], "not_promoted_gitignored": ignored,
           "lab_run_uncommitted": lp["uncommitted"],
           "lab_branch_commit_needed": bool(lp["uncommitted"]),
           "worktree_changes_outside_folder_not_promoted": lp["outside_changes"],
           "main": ms, "secret_scan": hits, "wiring_left_for_tony": wiring_items(t["plan_text"]),
           "resuming": resuming}
    if hits:
        problems.append("secret scan found something in the build folder (names only): "
                        + "; ".join(f"{h['file']}: {', '.join(h['found'])}" for h in hits))
    return doc, t, problems


# ---------------------------------------------------------------- commands

def emit_error(tag: str, exc: PromoteError, proj: Path | None = None) -> int:
    print(f"lab_promote: {exc.why}", file=sys.stderr)
    B.emit(tag, dict({"ok": False, "exit_code": exc.code, "why": exc.why,
                      "project_dir": str(proj) if proj else None}, **exc.extra))
    return exc.code


def list_main(root: Path = LAB_ROOT) -> int:
    rows = []
    for d in (sorted(root.iterdir()) if root.is_dir() else []):
        if not d.is_dir():
            continue
        info, why = R.gate(d)
        if not info:
            continue
        st = R.status_doc(d, info)
        try:
            meta = B.read_json(d / "Build_Meta.json")
            title = plan_title((d / "Plan_Locked.md").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            meta, title = {}, None
        rows.append({"project": d.name, "title": title, "into": meta.get("into"),
                     "grades": [r["grade"] for r in st["rounds"]], "cleared_for_promote": _cleared(d),
                     "promote_stage": read_meta(d).get("stage")})
    B.emit("LAB_PROMOTE_LIST", {"ok": True, "projects": rows})
    return 0


def plan_main(arg: str | None, accept_edited_log: bool = False, root: Path = LAB_ROOT,
              secrets_path: Path = SECRETS) -> int:
    proj = None
    try:
        proj = resolve(arg, root)
        if read_meta(proj).get("stage") in ("committed", "pushed"):
            raise PromoteError(1, f"already promoted (stage {read_meta(proj)['stage']}); "
                                  "use finish to retry a failed push")
        doc, _t, problems = assess(proj, accept_edited_log, secrets_path)
    except PromoteError as exc:
        return emit_error("LAB_PROMOTE_PLAN", exc, proj)
    code = 0 if not problems else (5 if doc["secret_scan"] else 4)
    B.emit("LAB_PROMOTE_PLAN", dict(doc, ok=not problems, problems=problems, exit_code=code))
    return code


def commit_lab_branch(t: dict, proj: Path) -> tuple[str, bool]:
    """Commit the build folder exactly as it is on disk to its OWN lab branch (never main), only if
    something is uncommitted. Returns (commit, made_a_new_commit)."""
    wt, rel, branch = t["worktree"], t["rel"], t["branch"]
    if git(wt, "symbolic-ref", "-q", "HEAD", check=False).strip() != f"refs/heads/{branch}":
        raise PromoteError(4, f"worktree is not on {branch}; refusing to commit")
    before = head(wt)
    git(wt, "add", "-A", "--", rel, f":(exclude,glob){rel}/**/__pycache__/**", f":(exclude,glob){rel}/**/*.pyc")
    if not git(wt, "diff", "--cached", "--name-only", "--", rel).strip():
        return before, False
    git(wt, "-c", "commit.gpgsign=false", "commit", "--no-verify", "-q", "-m",
        f"lab: /lab-run fixes as graded, before /lab-promote ({proj.name})", "--", rel)
    after = head(wt)
    if git(wt, "rev-parse", f"{after}^").strip() != before:
        raise PromoteError(6, "the lab-branch commit did not land on top of the lab branch")
    return after, True


def check_against_grade(wt: str, rel: str, commit: str, manifest: dict, ignored: set[str]) -> list[str]:
    """What gets promoted must be what Tony graded: every committed file's content equals his passing
    round's fingerprint, and every graded file is either committed or gitignored (never committed)."""
    problems = []
    tracked = tree_files(wt, commit, rel)
    for name, (_mode, sha) in tracked.items():
        data = blob(wt, sha) or b""
        if manifest.get(name) != hashlib.sha256(data).hexdigest():
            problems.append(f"{name} differs from the graded version")
    for name in manifest:
        if name not in tracked and name not in ignored:
            problems.append(f"{name} was graded but is not in the commit")
    return problems


def checkout_main(arg: str | None, accept_edited_log: bool = False, root: Path = LAB_ROOT,
                  secrets_path: Path = SECRETS) -> int:
    proj = None
    try:
        proj = resolve(arg, root)
        pm = read_meta(proj)
        if pm.get("stage") in ("committed", "pushed"):
            raise PromoteError(1, f"already promoted (stage {pm['stage']}); run finish to retry a failed push")
        doc, t, problems = assess(proj, accept_edited_log, secrets_path)
        if problems:
            raise PromoteError(5 if doc["secret_scan"] else 4, "not promoted: " + " | ".join(problems),
                               problems=problems)
        repo, rel, wt = t["repo"], t["rel"], t["worktree"]
        if doc["resuming"]:
            same = folder_vs_commit(repo, rel, pm["lab_commit"])
            if mismatch(same):
                raise PromoteError(6, "a checkout is half done and the folder now differs from it: "
                                      + "; ".join(mismatch(same)) + ". Show Tony; nothing was changed.")
            B.emit("LAB_PROMOTE_CHECKOUT", dict(pm, ok=True, resumed=True))
            return 0
        lab_commit, made = commit_lab_branch(t, proj)
        ignored = set(doc["not_promoted_gitignored"])
        bad = check_against_grade(wt, rel, lab_commit, last_manifest(proj), ignored)
        on_disk = folder_vs_commit(wt, rel, lab_commit)
        if bad or mismatch(on_disk):
            raise PromoteError(6, "the lab commit does not match what Tony graded: "
                                  + "; ".join(bad + mismatch(on_disk)) + ". Nothing was promoted.")
        snapshot = git(repo, "stash", "create").strip() or head(repo)  # objects only: no ref, no file change
        main_head = head(repo)
        epoch = time.time()
        git(repo, "checkout", lab_commit, "--", rel)  # the locked mechanism: ONE folder, from ONE commit
        landed = folder_vs_commit(repo, rel, lab_commit)
        if mismatch(landed):
            raise PromoteError(6, "the checked-out folder does not match the lab commit: "
                                  + "; ".join(mismatch(landed)))
        pm = {"promote": SCHEMA, "stage": "checked_out", "project": proj.name, "project_dir": str(proj),
              "title": doc["title"], "rel": rel, "destination": doc["destination"], "repo": repo,
              "worktree": wt, "branch": t["branch"], "all_worktrees": t["all_worktrees"],
              "lab_commit": lab_commit, "lab_commit_made_now": made,
              "lab_run_fixes_committed": doc["lab_run_uncommitted"], "files": landed["files"],
              "not_promoted_gitignored": doc["not_promoted_gitignored"],
              "build_total": doc["build_total"], "built_by": doc["built_by"], "grades": doc["grades"],
              "snapshot": snapshot, "main_head_at_checkout": main_head, "checkout_epoch": epoch,
              "checked_out": time.strftime("%Y-%m-%dT%H:%M:%S"),
              "wiring_left_for_tony": doc["wiring_left_for_tony"]}
        B.write_json(proj / PROMOTE_META, pm)
        B.L.log_event({"event": "lab_promote_checkout", "project": proj.name, "rel": rel,
                       "lab_commit": lab_commit, "lab_commit_made_now": made, "grades": doc["grades"]})
        B.emit("LAB_PROMOTE_CHECKOUT", dict(pm, ok=True, resumed=False))
        return 0
    except PromoteError as exc:
        return emit_error("LAB_PROMOTE_CHECKOUT", exc, proj)


# ---------------------------------------------------------------- finish

def registry_domains(repo) -> list[tuple[str, str]]:
    p = Path(repo) / REGISTRY_REL
    try:
        text = p.read_text(encoding="utf-8")
    except OSError:
        return []
    return [(m.group(1).strip(), m.group(2).strip("/"))
            for m in re.finditer(r"^\|\s*([^|`]+?)\s*\|\s*`([^`]+)`\s*\|", text, re.M)]


def domains_for(paths: list[str], domains: list[tuple[str, str]]) -> list[tuple[str, str]]:
    out = []
    for p in paths:
        best = max((d for d in domains if inside(p, d[1])), key=lambda d: len(d[1]), default=None)
        if best and best not in out:
            out.append(best)
    return out


def run_graphify(repo: str, domain_rel: str) -> dict:
    """`graphify update <domain>`: AST-only refresh, no LLM, no spend. Never fatal."""
    exe = shutil.which("graphify")
    if not exe:
        return {"domain": domain_rel, "ok": False, "note": "graphify is not on PATH; skipped"}
    try:
        out = subprocess.run([exe, "update", str(Path(repo) / domain_rel)], cwd=repo, capture_output=True,
                             text=True, timeout=GRAPHIFY_TIMEOUT)
        return {"domain": domain_rel, "ok": out.returncode == 0, "exit_code": out.returncode,
                "tail": (out.stdout + out.stderr)[-600:]}
    except subprocess.TimeoutExpired:
        return {"domain": domain_rel, "ok": False, "note": f"timed out after {GRAPHIFY_TIMEOUT}s"}


def birth(p: Path) -> float:
    st = p.stat()
    return getattr(st, "st_birthtime", st.st_ctime)


def merge_one(repo: str, path: str, snapshot: str, main_now: str, checkout_epoch: float) -> dict:
    """Content to commit for one listed file: main's committed version plus ONLY this session's
    edits (snapshot -> disk). Other sessions' uncommitted edits in the same file stay out."""
    disk_p = Path(repo) / path
    disk = disk_p.read_bytes()
    base, cur = blob(repo, f"{snapshot}:{path}"), blob(repo, f"{main_now}:{path}")
    ls = git(repo, "ls-tree", main_now, "--", path).split()
    mode = ls[0] if ls else ("100755" if os.access(disk_p, os.X_OK) else "100644")
    if base is None:
        if cur is not None:
            raise PromoteError(7, f"{path} was committed by someone else after /lab-promote started")
        if birth(disk_p) < checkout_epoch:
            raise PromoteError(7, f"{path} existed (uncommitted) before /lab-promote started, so it is "
                                  "not this command's own new file; leave it out or ask Tony")
        return {"path": path, "content": disk, "mode": mode, "kind": "new", "added": disk}
    if disk == base:
        raise PromoteError(7, f"{path} was listed but /lab-promote did not change it")
    added = "".join(ln[1:] for ln in difflib.unified_diff(
        base.decode("utf-8", "replace").splitlines(True), disk.decode("utf-8", "replace").splitlines(True), n=0)
        if ln.startswith("+") and not ln.startswith("+++")).encode()
    if cur == base:
        return {"path": path, "content": disk, "mode": mode, "kind": "edit", "added": added,
                "other_uncommitted_kept_out": False}
    if cur is None:
        raise PromoteError(7, f"{path} is gone from main since /lab-promote started")
    with tempfile.TemporaryDirectory() as td:
        a, b, c = Path(td, "main"), Path(td, "before"), Path(td, "after")
        a.write_bytes(cur), b.write_bytes(base), c.write_bytes(disk)
        rc, out, _ = git_bytes(repo, "merge-file", "-p", "-L", "main", "-L", "before /lab-promote",
                               "-L", "after /lab-promote", str(a), str(b), str(c), check=False)
    if rc != 0:
        raise PromoteError(7, f"{path}: this command's edit overlaps another uncommitted edit in the same "
                              "lines, so they cannot be separated. Nothing was committed; show Tony.")
    return {"path": path, "content": out, "mode": mode, "kind": "edit", "added": added,
            "other_uncommitted_kept_out": True}


def build_commit(repo: str, base: str, lab_commit: str, rel: str, shared: list[dict], message: str) -> str:
    """One commit on top of main's tip from a private index: the promoted folder's tree from the lab
    commit plus the merged listed files. The real index and other staged work are never used."""
    with tempfile.TemporaryDirectory() as td:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(td) / "index"))
        git(repo, "read-tree", base, env=env)
        _, entries, _ = git_bytes(repo, "ls-tree", "-r", "-z", "--full-tree", lab_commit, "--", rel)
        git_bytes(repo, "update-index", "-z", "--index-info", env=env, data=entries)
        for s in shared:
            _, sha, _ = git_bytes(repo, "hash-object", "-w", "--stdin", f"--path={s['path']}", data=s["content"])
            git(repo, "update-index", "--add", "--cacheinfo", f"{s['mode']},{sha.decode().strip()},{s['path']}",
                env=env)
        tree = git(repo, "write-tree", env=env).strip()
        msg = Path(td) / "msg"
        msg.write_text(message, encoding="utf-8")
        return git(repo, "commit-tree", tree, "-p", base, "-F", str(msg)).strip()


def commit_message(pm: dict, description: str, files: list[str], trailers: list[str]) -> str:
    folder = pm["rel"].split("/")[-1]
    lines = [f"feat(lab-promote): promote {folder} into {pm['rel']}", "", description.strip(), "",
             f"From /lab project {pm['project']} (branch {pm['branch']}, commit {pm['lab_commit'][:10]}).",
             f"/lab-build score {pm.get('build_total')}; /lab-run grades "
             + ", ".join(str(g) for g in pm.get("grades", [])) + ".",
             "Also updated: " + ", ".join(files) + "."]
    if trailers:
        lines += [""] + [t.strip() for t in trailers if t.strip()]
    return "\n".join(lines) + "\n"


def cleanup_commands(pm: dict) -> list[str]:
    repo, cmds = pm["repo"], []
    for w in pm.get("all_worktrees") or [{"worktree": pm["worktree"], "branch": pm["branch"]}]:
        if Path(w["worktree"]).exists():
            cmds.append(f'git -C "{repo}" worktree remove "{w["worktree"]}"')
        if w.get("branch") and git(repo, "rev-parse", "--verify", "-q", f"refs/heads/{w['branch']}", check=False).strip():
            cmds.append(f'git -C "{repo}" branch -D "{w["branch"]}"')
    return cmds


def push(pm: dict) -> dict:
    repo, ms = pm["repo"], main_state(pm["repo"])
    if not ms["remote"] or not ms["merge"]:
        return {"ok": False, "why": f"{MAIN_BRANCH} has no upstream remote configured",
                "retry": f'git -C "{repo}" push'}
    publishing = ms["unpushed_commits"]
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    rc, out, err = git_bytes(repo, "push", ms["remote"], f"refs/heads/{MAIN_BRANCH}:{ms['merge']}",
                             env=env, check=False, timeout=300)
    return {"ok": rc == 0, "remote": ms["remote"], "published_commits": publishing,
            "output_tail": (out.decode("utf-8", "replace") + err)[-600:],
            "retry": f'git -C "{repo}" push {ms["remote"]} {MAIN_BRANCH}'}


def done_doc(pm: dict) -> dict:
    return {"ok": True, "project": pm["project"], "destination": pm["destination"], "rel": pm["rel"],
            "main_commit": pm.get("main_commit"), "pushed": pm.get("pushed", False), "push": pm.get("push"),
            "files_committed": pm.get("files_committed"), "graphify": pm.get("graphify"),
            "lab_commit": pm["lab_commit"], "lab_commit_made_now": pm.get("lab_commit_made_now"),
            "not_promoted_gitignored": pm.get("not_promoted_gitignored"),
            "warnings": pm.get("warnings", []), "wiring_left_for_tony": pm.get("wiring_left_for_tony", []),
            "cleanup_commands_for_tony": cleanup_commands(pm),
            "cleanup_note": "Tony runs these himself when he is happy with the promoted copy. "
                            "/lab-promote never runs them."}


def finish_main(arg: str | None, files: list[str], description: str, trailers: list[str] | None = None,
                no_push: bool = False, root: Path = LAB_ROOT, secrets_path: Path = SECRETS,
                graphify=None) -> int:
    graphify = graphify or run_graphify
    proj = None
    try:
        proj = B.resolve_project(arg, root) if arg else resolve(None, root)
        if not proj:
            raise PromoteError(1, f"no such project folder: {arg}")
        pm = read_meta(proj)
        stage = pm.get("stage")
        if stage == "pushed":
            raise PromoteError(1, f"already promoted and pushed (commit {pm.get('main_commit')})")
        if stage == "committed":  # the commit exists; only the push is left
            return _push_and_report(proj, pm, no_push)
        if stage != "checked_out":
            raise PromoteError(1, "run `checkout` first (no promotion in progress for this project)")
        if not description.strip():
            raise PromoteError(1, "--description is required: Tony's own words for what is being promoted")
        repo, rel = pm["repo"], pm["rel"]
        if not main_state(repo)["on_main"]:
            raise PromoteError(4, f"the real workspace is no longer on {MAIN_BRANCH}")
        files = sorted(set(f.strip().strip("/") for f in files if f.strip()))
        bad = [f for f in files if f.startswith("/") or ".." in f.split("/") or inside(f, rel) or inside(f, LAB_REL)
               or not (Path(repo) / f).is_file()]
        if bad:
            raise PromoteError(7, "these --file paths are not plain files this command may commit (relative, "
                                  "existing, outside the promoted folder and the Lab): " + ", ".join(bad))
        if "TOOLBOX.md" not in files or not any(inside(f, "000_Wiki") for f in files):
            raise PromoteError(7, "the TOOLBOX.md entry and the 000_Wiki page are locked steps: list TOOLBOX.md "
                                  "and every 000_Wiki file you wrote with --file")
        ignored = [f for f in files if git_bytes(repo, "check-ignore", "-q", f, check=False)[0] == 0]
        if ignored:
            raise PromoteError(7, "gitignored, never committed: " + ", ".join(ignored))
        landed = folder_vs_commit(repo, rel, pm["lab_commit"])
        if mismatch(landed):
            raise PromoteError(6, f"the promoted folder changed after checkout ({'; '.join(mismatch(landed))}). "
                                  "Edits to it go through /lab-run, not /lab-promote. Nothing was committed.")
        main_now = head(repo)
        if tree_files(repo, main_now, rel) and tree_files(repo, main_now, rel) != tree_files(repo, pm["lab_commit"], rel):
            raise PromoteError(4, f"main now has a different {rel} committed; show Tony")
        shared = [merge_one(repo, f, pm["snapshot"], main_now, pm["checkout_epoch"]) for f in files]
        values = secret_values(secrets_path)
        hits = [{"file": s["path"], "found": scan_text(s["added"].decode("utf-8", "replace"), values)}
                for s in shared]
        hits = [h for h in hits if h["found"]]
        if hits:
            raise PromoteError(5, "secret scan found something in this command's edits (names only): "
                                  + "; ".join(f"{h['file']}: {', '.join(h['found'])}" for h in hits))
        warnings = []
        changed = [p for p in z_list(git(repo, "diff", "--name-only", "-z", pm["snapshot"]))
                   if not inside(p, rel) and p not in files]
        if changed:
            warnings.append("tracked files changed since checkout but not listed, so NOT committed (another "
                            "session, or a forgotten --file): " + ", ".join(changed[:30]))
        wiki_new = [p for p in z_list(git(repo, "ls-files", "-z", "--others", "--exclude-standard", "--", "000_Wiki"))
                    if p not in files and birth(Path(repo) / p) >= pm["checkout_epoch"]]
        if wiki_new:
            warnings.append("new 000_Wiki files made since checkout but not listed, so NOT committed: "
                            + ", ".join(wiki_new))
        warnings += [f"{s['path']}: other uncommitted edits already in this file were left uncommitted; only "
                     "this command's lines went into the commit" for s in shared if s.get("other_uncommitted_kept_out")]
        doms = domains_for([rel] + files, registry_domains(repo))
        graph = [graphify(repo, d[1]) for d in doms]
        message = commit_message(pm, description, files, trailers or [])
        commit = build_commit(repo, main_now, pm["lab_commit"], rel, shared, message)
        rc, _, err = git_bytes(repo, "update-ref", "-m", f"lab-promote: {pm['project']}",
                               f"refs/heads/{MAIN_BRANCH}", commit, main_now, check=False)
        if rc != 0:
            raise PromoteError(8, f"main moved while committing ({err.strip()}); nothing changed, rerun finish")
        git(repo, "reset", "-q", "--", rel, *files, check=False)  # index only: match the new commit for these paths
        pm.update({"stage": "committed", "main_commit": commit, "committed": time.strftime("%Y-%m-%dT%H:%M:%S"),
                   "files_committed": files, "description": description.strip(), "graphify": graph,
                   "graphify_domains": [d[0] for d in doms], "warnings": warnings})
        B.write_json(proj / PROMOTE_META, pm)
        B.L.log_event({"event": "lab_promote_commit", "project": pm["project"], "rel": rel,
                       "main_commit": commit, "files": files})
        return _push_and_report(proj, pm, no_push)
    except PromoteError as exc:
        return emit_error("LAB_PROMOTE_DONE", exc, proj)


def _push_and_report(proj: Path, pm: dict, no_push: bool) -> int:
    if no_push:
        B.emit("LAB_PROMOTE_DONE", dict(done_doc(pm), push_skipped=True,
                                        push_command=f'git -C "{pm["repo"]}" push'))
        return 0
    result = push(pm)
    pm["push"] = result
    if result["ok"]:
        pm.update({"stage": "pushed", "pushed": True, "pushed_at": time.strftime("%Y-%m-%dT%H:%M:%S")})
    B.write_json(proj / PROMOTE_META, pm)
    B.L.log_event({"event": "lab_promote_push", "project": pm["project"], "ok": result["ok"],
                   "main_commit": pm.get("main_commit")})
    if not result["ok"]:
        doc = dict(done_doc(pm), ok=False, exit_code=9,
                   why="push failed; the commit is safe on local main. Fix the cause, then rerun finish "
                       "(it only retries the push), or Tony runs the retry command.")
        print("lab_promote: push failed: " + result.get("output_tail", result.get("why", "")), file=sys.stderr)
        B.emit("LAB_PROMOTE_DONE", doc)
        return 9
    B.emit("LAB_PROMOTE_DONE", done_doc(pm))
    return 0


# ---------------------------------------------------------------- cli

def main(argv: list[str]) -> int:
    if os.environ.get("AGENT_OS_DELEGATE_WORKER"):
        print("lab_promote: refused, inside a delegated worker (/lab-promote is harness-only)", file=sys.stderr)
        return 3
    args = list(argv)
    if not args or args[0] not in ("list", "plan", "checkout", "finish"):
        print(__doc__)
        return 1
    cmd, rest = args[0], args[1:]
    multi, single, flags, pos = {"--file": [], "--trailer": []}, {}, set(), []
    while rest:
        a = rest.pop(0)
        if a in multi or a == "--description":
            if not rest:
                print(f"lab_promote: {a} needs a value", file=sys.stderr)
                return 1
            if a in multi:
                multi[a].append(rest.pop(0))
            else:
                single[a] = rest.pop(0)
        elif a in ("--no-push", "--accept-edited-log"):
            flags.add(a)
        else:
            pos.append(a)
    if len(pos) > 1 or (cmd == "list" and (pos or flags or single or any(multi.values()))):
        print(__doc__)
        return 1
    arg = pos[0] if pos else None
    if cmd == "list":
        return list_main()
    if cmd == "plan":
        return plan_main(arg, "--accept-edited-log" in flags)
    if cmd == "checkout":
        return checkout_main(arg, "--accept-edited-log" in flags)
    if not multi["--file"] or "--description" not in single:
        print("lab_promote: finish needs --description and at least one --file", file=sys.stderr)
        return 1
    return finish_main(arg, multi["--file"], single["--description"], multi["--trailer"], "--no-push" in flags)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
