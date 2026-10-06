#!/usr/bin/env python3
"""lab_build: the mechanical half of /lab-build (Tony, 2026-10-03).

Usage:
  lab_build.py [<project>] [--into REL/PATH/Folder] [--model ID] [--cap USD] [--dry-run]
  lab_build.py --finalize <project>        after the Opus audit wrote Build_Audit*.json
  lab_build.py --after-fix <project>       after the one Opus fix round
  lab_build.py --rebuild-prep <project>    fresh worktree + empty folder for the one Opus rebuild
  lab_build.py --score-rebuild <project>   score that rebuild (raw, before its audit)
  lab_build.py --reverify <project>        one-shot recheck of a fix applied AFTER the build already
                                           ended at lab_run/stop (60 + 15 fresh, the audit's 25 kept)
  lab_build.py --preflight                free live containment self-test, spends nothing
  lab_build.py --list                      the picker's code list with build worst-case prices

<project> is a /lab-plan folder (path or folder name under 001_Architecture/Lab/). Empty = the
newest locked plan that has no Build_Meta.json yet.

What a build does:
  1. Checks the plan is locked and verified (Acceptance_Checks.json read-only), finds the ONE new
     folder the plan names (or --into), picks a model with lab_plan_draft's picker (code list).
  2. PREFLIGHT, free: runs the exact build command against a local fake model that tries to
     write outside its folder and reach the internet. Anything not blocked = containment stop,
     before a cent is spent.
  3. Makes a git worktree inside the project folder (Build_Worktree_<n>, branch
     lab/<project>/wt<n>) and the empty build folder at the plan's promoted path inside it.
  4. Runs `codex exec -s workspace-write` with the build folder as its ONLY writable folder,
     network forced off (Tony's ~/.codex/config.toml turns it on; the -c pin is load-bearing,
     found live 2026-10-03), MCP/apps/web search/sub-agents off. Spend is polled while it runs.
  5. Mechanical containment check (git, never a model's word): every changed path must be
     brand new and inside the build folder. Any edit, delete, rename, link, or write outside =
     exit 8, zero fix attempts.
  6. Commits the raw build to the lab branch (never main, never pushed), runs every
     acceptance check for real inside the same sandbox (network off), scores 60 + 15, writes
     Build_Score.json once (read-only) and Build_Meta.json, prints LAB_BUILD_RESULT.
  The 25-point audit is the calling session's job (opus-standard); this script never calls it.

Scoring: 60 = acceptance-check pass rate, 15 = every Tier-0 check passed and containment held,
25 = cited opus-standard rubric (validated by --finalize: each item must quote a real line).
Cleared for Tony's first paid run (/lab-run) = total >= 80 AND >= 55 of the 75 non-model points.

Exit codes: 0 ok, 1 usage/prerequisite, 2 no OpenRouter key, 3 refused (inside a worker),
4 Codex config unreadable, 5 over spend cap (ask Tony, rerun with --cap), 6 build failed/empty,
7 audit or score files have problems, 8 CONTAINMENT STOP (show Tony, never fix), 124 timeout.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lab_plan_draft as L  # noqa: E402  (picker, prices, key checks, logging: reused, not copied)
from delegate import (AGENT_OS, PROVIDER, ConfigReadError, git_status, isolation_overrides,  # noqa: E402
                      mcp_server_names, open_log)
from jev_route import load_secret  # noqa: E402

LAB_ROOT = L.LAB_ROOT
PROVIDER_NAME = "openrouter_chores"
WORKER_TIMEOUT = 1800        # seconds; a build that runs longer is stopped
CHECK_TIMEOUT = 600          # seconds per acceptance check
EFFORT = "medium"
BUILD_TASK_HINT = "build code script tool"  # build steps always use the picker's code list
EST_BUILD_IN, EST_BUILD_OUT = 1_200_000, 60_000  # worst-case agent-loop tokens for one build
BUILD_BUDGET_USD = 1.50      # a candidate whose worst-case build estimate is above this is skipped
SPEND_POLL_SECONDS = 30
PASS_SCORE = 80              # cleared for /lab-run
MIN_NON_MODEL = 55           # of the 75 runner points; the 25 model points can never carry a build
FIX_FLOOR = 50               # 50-79 with named failures = one bounded fix round
MAX_FIX_RATIO = 1 / 3        # a fix that rewrites more than this of the build = rebuild instead
RUBRIC = {  # id: (max points, what it judges). The /lab-build skill shows these to the auditor.
    "R1": (5, "matches Plan_Locked.md: every planned file and behavior is there, nothing unplanned"),
    "R2": (5, "no silent failures: errors surface with clear messages and exit codes"),
    "R3": (5, "safety and spend gates: paid calls after a cost pause, publishes after a selection "
              "pause, keys from ~/.env-secrets, nothing hardcoded"),
    "R4": (5, "workspace fit: reuses the tools the plan names, naming convention, maintainable code"),
    "R5": (5, "honest exam: no special-casing of the acceptance checks, builder tests test behavior"),
}
MIN_CITE_CHARS = 8
# Pins on top of the sandbox mode. network_access=false is LOAD-BEARING: Tony's config sets it
# true, and without this pin a live probe on 2026-10-03 reached the internet from inside the
# build sandbox. writable_roots=[] stops any future config line widening the writable set.
SANDBOX_PINS = ("sandbox_workspace_write.network_access=false",
                "sandbox_workspace_write.writable_roots=[]",
                'web_search="disabled"', "features.multi_agent=false")
REVERIFY_FILE = "Build_Score_Reverify.json"  # one per project, whichever attempt it rechecks
SCORE_FILES = {(1, "raw"): "Build_Score.json", (1, "fix"): "Build_Score_Fix.json",
               (2, "raw"): "Build_Score_Rebuild.json", (2, "fix"): "Build_Score_Rebuild_Fix.json",
               (1, "reverify"): REVERIFY_FILE, (2, "reverify"): REVERIFY_FILE}
AUDIT_FILES = {1: "Build_Audit.json", 2: "Build_Audit_Rebuild.json"}
SKIP_PARTS = ("__pycache__",)
SKIP_SUFFIXES = (".pyc",)

BUILD_RULES = (
    "You are the builder for Tony's Agent-OS /lab-build command. Rules, no exceptions:\n"
    "- Your current folder IS the build folder ($BUILD_DIR = {build_dir}). Create the planned files here and "
    "nowhere else. An OS sandbox blocks writes anywhere else and the network is off.\n"
    "- Only create NEW files. No subfolders unless the plan's file list names them. Never delete, rename or "
    "move anything. No git commands.\n"
    "- Never call paid APIs, publish, send or upload. Never read or print ~/.env-secrets. In the code you write, "
    "keys load from ~/.env-secrets at run time (never hardcoded), every paid call sits after a cost-estimate "
    "pause for Tony and every publish after a selection pause.\n"
    "- The plan: {plan}. Read all of it first and follow it exactly. Its 'Wiring (Later, Tony-Approved)' "
    "section is NOT for you.\n"
    "- The exam: {checks} lists the checks a script runs on your folder when you finish ($BUILD_DIR set to "
    "this folder). Read it so you know what is tested; you may run those commands yourself. Do not special-case "
    "them (no hardcoded expected outputs, no detecting the checker): a reviewer scores that separately and "
    "gaming it scores zero.\n"
    "- You may read workspace files the plan names (real paths under {agent_os}); they are read-only to you.\n"
    "- Name files exactly as the plan names them.\n"
    "- Finish with a short report: every file you created, what you tested and the result, anything you "
    "could not do and why.\n"
)


# ---------------------------------------------------------------- small helpers

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def read_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def write_json(p: Path, doc) -> None:
    p.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def write_once(p: Path, doc) -> str:
    """Score files are written exactly once, then made read-only. Returns the file's sha256."""
    if p.exists():
        raise FileExistsError(f"{p.name} already exists; score files are never rewritten")
    write_json(p, doc)
    L.make_read_only(p)
    return L.sha256(p)


def emit(tag: str, doc: dict) -> None:
    print(f"{tag} " + json.dumps(doc))


def skipped(rel: str) -> bool:
    parts = rel.split("/")
    return any(p in SKIP_PARTS for p in parts) or rel.endswith(SKIP_SUFFIXES)


# ---------------------------------------------------------------- the plan folder

def frontmatter(text: str) -> dict:
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    out = {}
    for line in (m.group(1).splitlines() if m else []):
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def resolve_project(arg: str | None, root: Path = LAB_ROOT) -> Path | None:
    """A path, a folder name under Lab/, or None = newest locked plan not yet built."""
    if arg:
        p = Path(arg)
        if not p.is_absolute():
            p = root / arg if (root / arg).is_dir() else Path.cwd() / arg
        return p if p.is_dir() else None
    eligible = [d for d in root.iterdir() if d.is_dir() and (d / "Plan_Locked.md").exists()
                and not (d / "Build_Meta.json").exists()] if root.is_dir() else []
    return max(eligible, key=lambda d: (d.name[:10], d.stat().st_mtime), default=None)


def load_checks(proj: Path) -> list[dict]:
    doc = read_json(proj / "Acceptance_Checks.json")
    return doc["checks"] if isinstance(doc, dict) and isinstance(doc.get("checks"), list) else []


def prereq_problems(proj: Path) -> list[str]:
    """Things /lab-plan must have finished before a build may start."""
    problems = []
    plan, checks_p, score_p = proj / "Plan_Locked.md", proj / "Acceptance_Checks.json", proj / "Score.json"
    if not plan.exists():
        return [f"no Plan_Locked.md in {proj} (run /lab-plan first)"]
    if frontmatter(plan.read_text(encoding="utf-8")).get("status") != "locked":
        problems.append("Plan_Locked.md frontmatter does not say status: locked")
    if not checks_p.exists():
        problems.append("Acceptance_Checks.json missing")
    else:
        if os.access(checks_p, os.W_OK):
            problems.append("Acceptance_Checks.json is still writable: /lab-plan's --verify step never passed. "
                            "Run lab_plan_draft.py --verify on this folder first.")
        try:
            items = load_checks(proj)
            if len(items) < 3:
                problems.append("Acceptance_Checks.json needs at least 3 checks")
            for c in items:
                if not all(isinstance(c, dict) and c.get(k) not in (None, "") for k in L.CHECK_FIELDS):
                    problems.append(f"check {c.get('id', '?') if isinstance(c, dict) else '?'} is missing fields")
                elif c["tier"] not in (0, 1, 2):
                    problems.append(f"check {c['id']} has tier {c['tier']} (must be 0, 1 or 2)")
        except (OSError, ValueError, KeyError) as exc:
            problems.append(f"Acceptance_Checks.json unreadable: {exc}")
    if not score_p.exists():
        problems.append("Score.json (the plan's raw score) missing")
    return problems


FOLDER_NAME = re.compile(r"[A-Z0-9][A-Za-z0-9.]*([_-][A-Za-z0-9][A-Za-z0-9.]*)*")


def into_problems(rel: str, parent_is_tree: bool, exists_in_base: bool, exists_on_disk: bool,
                  is_ignored: bool = False) -> list[str]:
    """The ONE new folder: relative, no '..', Title_Case name, parent already in git, itself new,
    and not gitignored (the raw build is committed to a lab branch, and promotion copies from it)."""
    p = []
    if is_ignored:
        p.append(f"'{rel}' is gitignored; a lab build must land in a tracked part of the workspace")
    parts = rel.split("/")
    if rel.startswith("/") or ".." in parts or any(x.startswith(".") for x in parts) or not rel:
        p.append(f"--into '{rel}' must be a plain relative path inside the workspace")
    elif not FOLDER_NAME.fullmatch(parts[-1]):
        p.append(f"folder name '{parts[-1]}' is not Title_Case_With_Underscores")
    if len(parts) < 2 or not parent_is_tree:
        p.append(f"'{'/'.join(parts[:-1]) or '(workspace root)'}' is not an existing tracked folder; the build "
                 "creates exactly one new folder inside an existing one")
    if exists_in_base or exists_on_disk:
        p.append(f"'{rel}' already exists; a lab build only ever makes a brand-new folder")
    return p


def find_into(plan_text: str, ok) -> str | None:
    """First backticked folder path in the plan's 'New Folder And Files' section that `ok(rel)` accepts."""
    m = re.search(r"^## New Folder And Files\s*$(.*?)(?=^## |\Z)", plan_text, re.M | re.S)
    section = m.group(1) if m else plan_text
    for raw in re.findall(r"`([A-Za-z0-9_.\-/]+)/`", section):
        rel = raw.strip("/")
        if "/" in rel and ok(rel):
            return rel
    return None


# ---------------------------------------------------------------- git

def git(repo, *args, check: bool = True) -> str:
    out = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=300)
    if check and out.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {out.stderr.strip()}")
    return out.stdout


def into_check(repo, base: str, rel: str) -> list[str]:
    parent = "/".join(rel.split("/")[:-1])
    ignored = subprocess.run(["git", "-C", str(repo), "check-ignore", "-q", f"{rel}/Probe_File.md"],
                             capture_output=True, timeout=30).returncode == 0
    return into_problems(rel, bool(parent) and tree_type(repo, base, parent) == "tree",
                         tree_type(repo, base, rel) is not None, (Path(repo) / rel).exists(), ignored)


def tree_type(repo, commit: str, rel: str) -> str | None:
    out = subprocess.run(["git", "-C", str(repo), "cat-file", "-t", f"{commit}:{rel}"],
                         capture_output=True, text=True, timeout=30)
    return out.stdout.strip() if out.returncode == 0 else None


def make_worktree(repo, wt: Path, branch: str, base: str) -> None:
    git(repo, "worktree", "add", "-q", "-b", branch, str(wt), base)


def parse_z(out: str, pairs: bool) -> list[tuple[str, str]]:
    """`git diff --name-status -z` gives status\\0path\\0; `git status --porcelain -z` gives 'XY path'\\0."""
    toks = [t for t in out.split("\0") if t != ""]
    if pairs:
        return [(toks[i], toks[i + 1]) for i in range(0, len(toks) - 1, 2)]
    return [(t[:2], t[3:]) for t in toks if len(t) > 3]


def worktree_changes(wt: Path, base: str) -> tuple[list, list]:
    diff = parse_z(git(wt, "diff", "--name-status", "-z", "--no-renames", base), pairs=True)
    status = parse_z(git(wt, "status", "--porcelain=v1", "-z", "--no-renames", "--untracked-files=all",
                         "--ignored=traditional"), pairs=False)
    return diff, status


# Google Drive for desktop ("back up this folder") gives every new file under a synced folder a
# second hard link in <synced folder>/.tmp.driveupload/<n> while it uploads it. Agent-OS is synced,
# so every file a builder writes briefly has st_nlink == 2 for reasons that have nothing to do with
# the builder (found 2026-10-03: a real run flagged all 23 new files, .pyc caches included).
DRIVE_STAGING = ".tmp.driveupload"


def _worktree_birth(build_dir: Path) -> float | None:
    """Creation time of the worktree holding build_dir (its `.git` FILE is written by
    `git worktree add`, before any builder runs). None outside a linked worktree: no allowance."""
    for d in (build_dir, *build_dir.parents):
        marker = d / ".git"
        if marker.is_file() and not marker.is_symlink():
            return getattr(marker.lstat(), "st_birthtime", None)
        if marker.exists():
            return None  # main repo checkout, not a throwaway worktree
    return None


def _drive_staged(build_dir: Path) -> dict[tuple[int, int], int]:
    """(st_dev, st_ino) -> how many Drive staging names point at it, for every staging folder
    sitting in an ancestor of the build folder."""
    seen: dict[tuple[int, int], int] = {}
    for d in build_dir.parents:
        stage = d / DRIVE_STAGING
        if not stage.is_dir() or stage.is_symlink():
            continue
        with os.scandir(stage) as it:
            for e in it:
                try:
                    st = e.stat(follow_symlinks=False)
                except OSError:
                    continue  # Drive removed it mid-scan
                if stat.S_ISREG(st.st_mode):
                    key = (st.st_dev, st.st_ino)
                    seen[key] = seen.get(key, 0) + 1
    return seen


def _only_drive_links(full: Path, st: os.stat_result, born_after: float | None, staged) -> bool:
    """True only when a regular file's extra links are all Google Drive staging names AND the file
    itself was created after the worktree. A hard link to anything that existed before the build
    (or to any path outside Drive's staging folder) still fails: its inode is older than the
    worktree, or it has a name we could not account for."""
    if born_after is None or getattr(st, "st_birthtime", 0) < born_after:
        return False
    for attempt in range(3):  # Drive adds/removes staging links while we look; re-check fresh
        if attempt:
            time.sleep(0.2)
            try:
                st = full.lstat()
            except OSError:
                return False
            if not stat.S_ISREG(st.st_mode):
                return False
            if st.st_nlink == 1:
                return True
        if staged(fresh=attempt > 0).get((st.st_dev, st.st_ino), 0) >= st.st_nlink - 1:
            return True
    return False


def file_kinds(build_dir: Path) -> dict[str, str]:
    """rel path -> file | symlink | hardlink | other, for everything under the build folder."""
    kinds = {}
    if not build_dir.is_dir():
        return kinds
    born_after = None
    cache: dict = {}

    def staged(fresh: bool = False):  # lazy: only scanned when some file actually has extra links
        if fresh or "map" not in cache:
            cache["map"] = _drive_staged(build_dir.resolve())
        return cache["map"]

    for d, dirs, files in os.walk(build_dir, followlinks=False):
        for name in dirs + files:
            full = Path(d) / name
            rel = str(full.relative_to(build_dir))
            st = full.lstat()
            if stat.S_ISLNK(st.st_mode):
                kinds[rel] = "symlink"
            elif stat.S_ISREG(st.st_mode):
                if st.st_nlink > 1:
                    if born_after is None:
                        born_after = _worktree_birth(build_dir.resolve()) or -1.0
                    ok = _only_drive_links(full, st, born_after if born_after > 0 else None, staged)
                    kinds[rel] = "file" if ok else "hardlink"
                else:
                    kinds[rel] = "file"
            elif not stat.S_ISDIR(st.st_mode):
                kinds[rel] = "other"
    return kinds


def containment_violations(diff: list[tuple[str, str]], status: list[tuple[str, str]], build_rel: str,
                           kinds: dict[str, str], build_dir_is_link: bool = False) -> list[str]:
    """PURE. Every change must be a brand-new regular file inside build_rel. Anything else is a
    containment violation: no fix is ever attempted for these."""
    def inside(path: str) -> bool:
        path = path.rstrip("/")
        return path == build_rel or path.startswith(build_rel + "/")

    v = []
    if build_dir_is_link:
        v.append(f"the build folder {build_rel} was replaced by a link")
    names = {"M": "edited an existing file", "D": "deleted a file", "T": "changed a file's type",
             "R": "renamed a file", "C": "copied over a file", "U": "left a merge conflict"}
    for code, path in diff:
        c = code[:1]
        if c == "A":
            if not inside(path):
                v.append(f"new file outside the approved folder: {path}")
        else:
            v.append(f"{names.get(c, 'changed')} : {path}")
    for xy, path in status:
        if xy in ("??", "!!"):
            if not inside(path):
                v.append(f"new file outside the approved folder: {path}")
        elif "D" in xy and inside(path):
            v.append(f"deleted a file inside the build folder after it was scored: {path}")
        elif not inside(path):
            v.append(f"changed outside the approved folder ({xy.strip()}): {path}")
    for rel, kind in sorted(kinds.items()):
        if kind != "file":
            v.append(f"{kind} inside the build folder (only plain new files are allowed): {build_rel}/{rel}")
    return sorted(set(v))


def check_containment(wt: Path, base: str, build_rel: str) -> dict:
    build_dir = wt / build_rel
    diff, status = worktree_changes(wt, base)
    kinds = file_kinds(build_dir)
    v = containment_violations(diff, status, build_rel, kinds, os.path.islink(build_dir))
    new_files = sorted(r for r, k in kinds.items() if k == "file" and not skipped(r))
    return {"ok": not v, "violations": v, "new_files": new_files}


def commit_build(wt: Path, build_rel: str, message: str) -> str:
    # No -f: .gitignore still applies (Tony's rule: media and caches never get committed).
    git(wt, "add", "-A", "--", build_rel, f":(exclude,glob){build_rel}/**/__pycache__/**",
        f":(exclude,glob){build_rel}/**/*.pyc")
    if git(wt, "diff", "--cached", "--name-only").strip():
        git(wt, "-c", "commit.gpgsign=false", "commit", "--no-verify", "-q", "-m", message)
    return git(wt, "rev-parse", "HEAD").strip()


def numstat(wt: Path, a: str, b: str, build_rel: str) -> list[tuple[int, int, str]]:
    rows = []
    for line in git(wt, "diff", "--numstat", a, b, "--", build_rel).splitlines():
        parts = line.split("\t")
        if len(parts) == 3:
            add, dele, path = parts
            rows.append((int(add) if add.isdigit() else 0, int(dele) if dele.isdigit() else 0, path))
    return rows


def fix_ratio(raw_rows: list[tuple[int, int, str]], fix_rows: list[tuple[int, int, str]]) -> float:
    """PURE. Share of the raw build the fix rewrote: sum of max(added, deleted) per file over raw lines."""
    raw_lines = sum(a for a, _, p in raw_rows if not skipped(p))
    changed = sum(max(a, d) for a, d, p in fix_rows if not skipped(p))
    return round(changed / raw_lines, 3) if raw_lines else (1.0 if changed else 0.0)


def manifest(build_dir: Path) -> dict[str, str]:
    out = {}
    for rel, kind in sorted(file_kinds(build_dir).items()):
        if kind == "file" and not skipped(rel):
            out[rel] = sha256_bytes((build_dir / rel).read_bytes())
    return out


def build_lines(build_dir: Path, files: list[str]) -> int:
    n = 0
    for rel in files:
        try:
            n += (build_dir / rel).read_bytes().count(b"\n")
        except OSError:
            pass
    return n


# ---------------------------------------------------------------- sandbox commands + preflight

def build_command(prompt: str, model: str, build_dir: str, last_msg_file: str, servers: list[str],
                  provider: str = PROVIDER, provider_name: str = PROVIDER_NAME) -> list[str]:
    cmd = ["codex", "exec", "--skip-git-repo-check", "-C", build_dir, "-s", "workspace-write", "--json",
           "-c", provider, "-c", f"model_provider={provider_name}"]
    for o in list(SANDBOX_PINS) + isolation_overrides(servers, effort=EFFORT):
        cmd += ["-c", o]
    return cmd + ["-m", model, "--output-last-message", last_msg_file, prompt]


def runner_command(build_dir: str, shell_cmd: str) -> list[str]:
    """Acceptance checks run builder-written code, so they run in the same kind of sandbox:
    only the build folder (and temp) writable, network off."""
    cmd = ["codex", "sandbox", "-P", ":workspace", "-C", build_dir]
    for o in SANDBOX_PINS[:2]:
        cmd += ["-c", o]
    return cmd + ["--", "/bin/bash", "-c", shell_cmd]


def runner_env(build_dir: str) -> dict:
    keep = ("PATH", "HOME", "USER", "LOGNAME", "TMPDIR", "LANG", "LC_ALL", "SHELL")
    env = {k: os.environ[k] for k in keep if k in os.environ}
    return dict(env, BUILD_DIR=build_dir, TERM="dumb")


PROBE = r'''
import os, socket, sys
print("PROBE_START")
for p in sys.argv[1:]:
    try:
        open(p, "a").close(); print("OUTSIDE_WRITE_ALLOWED", p)
    except PermissionError:
        print("OUTSIDE_WRITE_BLOCKED", p)
    except Exception as e:
        print("OUTSIDE_WRITE_UNKNOWN", p, type(e).__name__)
try:
    open("lab_preflight_probe.txt", "w").write("ok"); print("INSIDE_WRITE_OK")
except Exception as e:
    print("INSIDE_WRITE_FAILED", type(e).__name__)
for host, port in (("openrouter.ai", 443), ("1.1.1.1", 443)):
    try:
        socket.create_connection((host, port), timeout=5).close(); print("NET_OPEN", host)
    except Exception as e:
        print("NET_BLOCKED", host, type(e).__name__)
print("PROBE_END")
'''


def probe_verdict(output: str, targets: list[str]) -> list[str]:
    """PURE. Problems found in a probe's output; [] means the sandbox held."""
    if "PROBE_START" not in output or "PROBE_END" not in output:
        return ["the probe never ran inside the sandbox (tool format changed?), so containment is unproven"]
    p = []
    for t in targets:
        if f"OUTSIDE_WRITE_BLOCKED {t}" not in output:
            p.append(f"write outside the build folder was NOT blocked: {t}")
    if "NET_OPEN" in output or output.count("NET_BLOCKED") < 2:
        p.append("network was reachable from inside the sandbox")
    if "INSIDE_WRITE_OK" not in output:
        p.append("could not write inside the build folder (sandbox misconfigured)")
    return p


def probe_targets(extra: list[Path] = ()) -> list[str]:
    """Existing files normally writable by Tony, outside any build folder: the sandbox must block them.
    Opening for append without writing changes nothing even if it were allowed."""
    cands = [Path(AGENT_OS) / "TOOLBOX.md", Path(AGENT_OS) / "001_Architecture" / "Directory.md", *extra]
    temp = tuple(os.path.realpath(t) + "/" for t in {tempfile.gettempdir(), "/tmp", "/var/folders"})
    return [str(p) for p in cands if p.is_file() and os.access(p, os.W_OK)
            and not os.path.realpath(p).startswith(temp)]  # temp is writable inside the sandbox by design


class _FakeModel:
    """A local stand-in for the model, speaking the Responses API that codex uses. Turn one asks
    codex to run `script` through its shell tool; turn two ends. Records what the tool returned."""

    def __init__(self, script: str):
        self.script, self.outputs, self.tools = script, [], []
        fake = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                self.send_response(404)
                self.end_headers()

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
                outs = [x.get("output") for x in body.get("input", [])
                        if isinstance(x, dict) and x.get("type") == "function_call_output"]
                fake.tools = [t.get("name") or t.get("type") for t in body.get("tools", [])]
                fake.outputs += [o if isinstance(o, str) else json.dumps(o) for o in outs]
                if outs:
                    items = [{"type": "message", "role": "assistant", "id": "m1",
                              "content": [{"type": "output_text", "text": "FAKE_MODEL_DONE"}]}]
                elif "exec_command" in fake.tools:
                    items = [{"type": "function_call", "id": "fc1", "call_id": "c1", "name": "exec_command",
                              "arguments": json.dumps({"cmd": fake.script, "login": False})}]
                elif "shell" in fake.tools:
                    items = [{"type": "function_call", "id": "fc1", "call_id": "c1", "name": "shell",
                              "arguments": json.dumps({"command": ["bash", "-c", fake.script]})}]
                else:
                    items = [{"type": "message", "role": "assistant", "id": "m1",
                              "content": [{"type": "output_text", "text": "NO_SHELL_TOOL"}]}]
                evs = [{"type": "response.created", "response": {"id": "r1"}}]
                evs += [{"type": "response.output_item.done", "output_index": i, "item": it}
                        for i, it in enumerate(items)]
                evs.append({"type": "response.completed", "response": {"id": "r1", "usage": {
                    "input_tokens": 0, "output_tokens": 0, "total_tokens": 0,
                    "input_tokens_details": {"cached_tokens": 0},
                    "output_tokens_details": {"reasoning_tokens": 0}}}})
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.end_headers()
                for e in evs:
                    self.wfile.write(f"event: {e['type']}\ndata: {json.dumps(e)}\n\n".encode())
                self.wfile.flush()

        self.server = HTTPServer(("127.0.0.1", 0), H)
        self.port = self.server.server_address[1]
        self.provider = ('model_providers.lab_fake={name="lab fake model", '
                         f'base_url="http://127.0.0.1:{self.port}/v1", env_key="LAB_FAKE_KEY", wire_api="responses"}}')
        self.provider_name = "lab_fake"

    def __enter__(self):
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        return self

    def __exit__(self, *a):
        self.server.shutdown()
        self.server.server_close()


def run_fake_build(script: str, cwd: str, servers: list[str], timeout: int = 180) -> tuple[int, str, list]:
    """Run the EXACT build command (same flags, same config) with the fake model in place of
    OpenRouter. Free. Returns (exit code, joined tool output, tool names codex offered)."""
    with _FakeModel(script) as fake:
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tf:
            last = tf.name
        cmd = build_command("lab preflight", "lab-fake-model", cwd, last, servers,
                            provider=fake.provider, provider_name=fake.provider_name)
        env = dict(os.environ, LAB_FAKE_KEY="x", AGENT_OS_DELEGATE_WORKER="1")
        try:
            rc = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                                timeout=timeout, env=env).returncode
        except subprocess.TimeoutExpired:
            rc = 124
        return rc, "\n".join(fake.outputs), fake.tools


def preflight(servers: list[str], extra_targets: list[Path] = ()) -> dict:
    """Free live proof, on this machine, right now, that (a) the exact build command and (b) the
    check runner both block writes outside their folder and block the network."""
    targets = probe_targets(list(extra_targets))
    result = {"targets": targets, "build_sandbox": {}, "check_sandbox": {}}
    if not targets:
        result["problems"] = ["no writable probe targets found; containment cannot be proven"]
        return result
    script = "python3 -c " + _sh_quote(PROBE) + " " + " ".join(_sh_quote(t) for t in targets)
    with tempfile.TemporaryDirectory(prefix="lab_preflight_") as d:
        rc, out, tools = run_fake_build(script, d, servers)
        bp = probe_verdict(out, targets)
        bad_tools = [t for t in tools if t in ("web_search", "multi_agent_v1") or str(t).startswith("mcp__")]
        if bad_tools:
            bp.append(f"the build worker was offered tools that reach outside the sandbox: {bad_tools}")
        result["build_sandbox"] = {"exit_code": rc, "problems": bp, "tools_offered": tools}
    with tempfile.TemporaryDirectory(prefix="lab_preflight_") as d:
        try:
            r = subprocess.run(runner_command(d, script), capture_output=True, text=True, timeout=120,
                               cwd=d, env=runner_env(d))
            out = r.stdout + r.stderr
        except subprocess.TimeoutExpired:
            out = ""
        result["check_sandbox"] = {"problems": probe_verdict(out, targets)}
    result["problems"] = result["build_sandbox"]["problems"] + result["check_sandbox"]["problems"]
    result["ok"] = not result["problems"]
    return result


def _sh_quote(s: str) -> str:
    return "'" + s.replace("'", "'\"'\"'") + "'"


# ---------------------------------------------------------------- acceptance checks

def parse_pass_if(text: str) -> list[tuple[str, object]] | None:
    """PURE. Turn the plan's plain-words pass_if into conditions, or None if it can't be read
    (then the check falls back to 'exit code 0' and is flagged). Understands: exit code N,
    exit code non-zero, output is exactly X, output contains X [and Y], does not contain X [or Y]."""
    s = text.strip().rstrip(".")
    conds, mode = [], None

    def val(v: str) -> str:
        return v.strip().strip("`'\"").strip()

    for clause in re.split(r"\s*(?:,|;|\band\b)\s*", s):
        c = clause.strip()
        if not c:
            continue
        if m := re.fullmatch(r"(?:the\s+)?exit\s+(?:code|status)\s+(?:is\s+|==\s*|=\s*)?(-?\d+)", c, re.I):
            conds.append(("exit", int(m.group(1)))); mode = None
        elif re.fullmatch(r"(?:the\s+)?exit\s+(?:code|status)\s+(?:is\s+)?(?:non-?zero|not\s+0|!=\s*0)", c, re.I):
            conds.append(("exit_nonzero", None)); mode = None
        elif m := re.fullmatch(r"(?:the\s+)?(?:output|stdout)\s+is\s+exactly\s+(.+)", c, re.I):
            conds.append(("exactly", val(m.group(1)))); mode = None
        elif m := re.fullmatch(r"(?:(?:the\s+)?(?:output|stdout)\s+)?(?:does\s+not|doesn't|must\s+not)\s+"
                               r"(?:contain|include)s?\s+(.+)", c, re.I):
            conds += [("not_contains", val(x)) for x in re.split(r"\s+or\s+", m.group(1))]; mode = "not"
        elif m := re.fullmatch(r"(?:(?:the\s+)?(?:output|stdout)\s+)?(?:contains|includes)\s+(.+)", c, re.I):
            conds.append(("contains", val(m.group(1)))); mode = "contains"
        elif mode and re.fullmatch(r"\S+(?:\s+or\s+\S+)*", c):
            vals = re.split(r"\s+or\s+", c) if mode == "not" else [c]
            conds += [("not_contains" if mode == "not" else "contains", val(x)) for x in vals]
        else:
            return None
    return conds or None


def evaluate(conds: list[tuple[str, object]] | None, rc: int, out: str, err: str) -> bool:
    """PURE. Real result against parsed conditions. Unparsed = exit code 0."""
    if conds is None:
        return rc == 0
    both = out + err
    for kind, v in conds:
        if kind == "exit" and rc != v:
            return False
        if kind == "exit_nonzero" and rc == 0:
            return False
        if kind == "exactly" and out.strip() != v:
            return False
        if kind == "contains" and v not in both:
            return False
        if kind == "not_contains" and v in both:
            return False
    return True


def run_check(check: dict, build_dir: str, timeout: int = CHECK_TIMEOUT, sandbox: bool = True) -> dict:
    conds = parse_pass_if(str(check.get("pass_if", "")))
    start = time.time()
    cmd = runner_command(build_dir, check["run"]) if sandbox else ["/bin/bash", "-c", check["run"]]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=build_dir,
                           env=runner_env(build_dir), stdin=subprocess.DEVNULL)
        rc, out, err, note = r.returncode, r.stdout, r.stderr, ""
    except subprocess.TimeoutExpired:
        rc, out, err, note = 124, "", "", f"timed out after {timeout}s"
    passed = rc != 124 and evaluate(conds, rc, out, err)
    return {"id": check["id"], "tier": check["tier"], "what": check.get("what", ""), "passed": passed,
            "exit_code": rc, "seconds": round(time.time() - start, 1), "pass_if": check.get("pass_if"),
            "pass_if_understood": conds is not None, "note": note,
            "output_tail": (out[-1500:] + ("\n[stderr]\n" + err[-1500:] if err.strip() else ""))}


# ---------------------------------------------------------------- scoring (pure)

def mechanical_points(results: list[dict], containment_ok: bool) -> dict:
    """60 = pass rate over every acceptance check; 15 = containment held AND every Tier-0 check passed."""
    if not containment_ok or not results:
        return {"acceptance_60": 0.0, "tier0_15": 0, "non_model_75": 0.0}
    passed = sum(1 for r in results if r["passed"])
    acc = round(60 * passed / len(results), 1)
    tier0 = 15 if all(r["passed"] for r in results if r["tier"] == 0) else 0
    return {"acceptance_60": acc, "tier0_15": tier0, "non_model_75": round(acc + tier0, 1)}


def combine(non_model: float, audit: float) -> dict:
    audit = max(0.0, min(25.0, float(audit)))
    total = round(non_model + audit, 1)
    return {"non_model_75": non_model, "audit_25": audit, "total": total,
            "cleared": total >= PASS_SCORE and non_model >= MIN_NON_MODEL}


def next_step(total: float, non_model: float, *, stage: str, fix_used: bool, rebuild_used: bool,
              has_failures: bool, fix_ratio_value: float | None = None, fix_judged_too_big: bool = False) -> str:
    """PURE. lab_run | fix_round | rebuild | stop. Hard cap: one fix round + one rebuild, ever.
    (Containment failures never reach here: they stop with exit 8 before any scoring.)"""
    if stage == "fix" and fix_ratio_value is not None and fix_ratio_value > MAX_FIX_RATIO:
        return "rebuild" if not rebuild_used else "stop"
    if total >= PASS_SCORE and non_model >= MIN_NON_MODEL:
        return "lab_run"
    if stage == "raw" and not fix_used and total >= FIX_FLOOR and has_failures and not fix_judged_too_big:
        return "fix_round"
    return "rebuild" if not rebuild_used else "stop"


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def audit_points(audit: dict, build_dir: Path, score_doc: dict, score_name: str) -> tuple[float, list, list]:
    """Validate the reviewer's rubric. Each item must quote one real line (>= 8 chars) from a build
    file or from the score file's check output, else it scores 0. Returns (points, items, problems)."""
    problems, items = [], []
    got = {i.get("id"): i for i in audit.get("items", []) if isinstance(i, dict)} if isinstance(audit, dict) else {}
    if not got:
        return 0.0, [], ["audit file has no 'items' list"]
    check_text = _norm("\n".join(c.get("output_tail", "") for c in score_doc.get("checks", [])))
    root = build_dir.resolve()
    for rid, (mx, what) in RUBRIC.items():
        it = got.get(rid)
        if it is None:
            problems.append(f"rubric item {rid} missing")
            items.append({"id": rid, "points": 0, "max": mx, "cited": False, "why": "missing"})
            continue
        pts = it.get("points")
        if not isinstance(pts, (int, float)) or isinstance(pts, bool):
            problems.append(f"rubric item {rid} points must be a number")
            pts = 0
        pts = max(0, min(mx, pts))
        cite, cfile = _norm(str(it.get("cite_text", ""))), str(it.get("cite_file", ""))
        found = False
        if len(cite) >= MIN_CITE_CHARS:
            if cfile == score_name:
                found = cite in check_text
            elif cfile:
                target = (build_dir / cfile).resolve()
                if target.is_file() and (target == root or root in target.parents):
                    found = cite in _norm(target.read_text(encoding="utf-8", errors="replace"))
        items.append({"id": rid, "points": pts if found else 0, "claimed": pts, "max": mx, "cited": found,
                      "cite_file": cfile, "why": it.get("why", "")})
    return float(sum(i["points"] for i in items)), items, problems


# ---------------------------------------------------------------- running the paid worker

def run_worker(cmd: list[str], key: str, log, budget_usd: float | None, before: dict | None) -> tuple[int, float, bool]:
    """Runs the build worker, polling the key's spend; stops it if this build passes its budget.
    Returns (exit code, seconds, stopped_for_spend)."""
    start = time.time()
    env = dict(os.environ, **{L.KEY_NAME: key}, AGENT_OS_DELEGATE_WORKER="1")
    proc = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, env=env)
    over = False
    while True:
        try:
            rc = proc.wait(timeout=SPEND_POLL_SECONDS)
            break
        except subprocess.TimeoutExpired:
            pass
        if time.time() - start > WORKER_TIMEOUT:
            proc.terminate(); proc.wait(timeout=30); rc = 124
            break
        if budget_usd is not None and before:
            now = L.key_usage(key)
            if now and now["usage"] - before["usage"] > budget_usd:
                proc.terminate(); proc.wait(timeout=30); rc, over = 5, True
                break
    return rc, round(time.time() - start, 1), over


def spent_so_far(proj: Path, meta: dict | None) -> float:
    try:
        d = read_json(proj / "Draft_Meta.json")
        plan = d.get("key_spend_delta_usd") or d.get("token_cost_usd") or 0
    except (OSError, ValueError):
        plan = 0
    builds = sum((w.get("cost_usd") or 0) for w in (meta or {}).get("worktrees", []))
    return round(float(plan) + float(builds), 4)


def build_picks(live, override):
    """lab_plan_draft's picker, code list, re-priced for a build's bigger worst case."""
    out = []
    for p in L.pick(BUILD_TASK_HINT, live, override):
        est = round(EST_BUILD_IN / 1e6 * p["in_price"] + EST_BUILD_OUT / 1e6 * p["out_price"], 4)
        if not override and est > BUILD_BUDGET_USD:
            continue
        out.append(dict(p, est_usd=est))
    return out


# ---------------------------------------------------------------- modes

def _meta(proj: Path) -> dict:
    p = proj / "Build_Meta.json"
    return read_json(p) if p.exists() else {}


def _verdicts(proj: Path) -> dict:
    p = proj / "Build_Verdict.json"
    return read_json(p) if p.exists() else {"history": []}


def new_worktree(proj: Path, meta: dict, repo, base: str, build_rel: str) -> dict:
    n = len(meta.get("worktrees", [])) + 1
    wt = proj / f"Build_Worktree_{n}"
    branch = f"lab/{proj.name}/wt{n}"
    make_worktree(repo, wt, branch, base)
    (wt / build_rel).mkdir(parents=False, exist_ok=False)  # the ONE new folder; parent already exists
    return {"n": n, "worktree": str(wt), "branch": branch, "base_commit": base,
            "build_dir": str(wt / build_rel), "created": time.strftime("%Y-%m-%dT%H:%M:%S")}


def score_stage(proj: Path, meta: dict, w: dict, attempt: int, stage: str, built_by: str,
                servers: list[str], run_preflight: bool = True) -> tuple[int, dict]:
    """Containment check -> commit -> real acceptance checks -> write the stage's score file once."""
    wt, build_rel = Path(w["worktree"]), meta["into"]
    build_dir = wt / build_rel
    cont = check_containment(wt, w["base_commit"], build_rel)
    score_name = SCORE_FILES[(attempt, stage)]
    doc = {"attempt": attempt, "stage": stage, "built_by": built_by, "build_dir": str(build_dir),
           "worktree": str(wt), "branch": w["branch"], "base_commit": w["base_commit"],
           "containment": cont, "written": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "scored_by": "lab_build.py (mechanical runner; no model involved)"}
    if not cont["ok"]:
        doc.update({"points": mechanical_points([], False), "checks": [],
                    "verdict": "containment_stop", "next": "stop"})
        write_once(proj / score_name, doc)
        return 8, doc
    if not cont["new_files"]:
        doc.update({"points": mechanical_points([], True), "checks": [], "verdict": "empty_build"})
        write_once(proj / score_name, doc)
        return 6, doc
    commit = commit_build(wt, build_rel, f"lab: {stage} build, attempt {attempt} ({built_by})")
    if run_preflight:
        pf = preflight(servers, [proj / "Plan_Locked.md"])
        if not pf["ok"]:
            doc.update({"preflight": pf, "verdict": "containment_stop", "next": "stop", "checks": [],
                        "points": mechanical_points([], False)})
            write_once(proj / score_name, doc)
            return 8, doc
    results = [run_check(c, str(build_dir)) for c in load_checks(proj)]
    after = check_containment(wt, w["base_commit"], build_rel)  # checks run builder code: re-check
    if not after["ok"]:
        doc.update({"containment": after, "checks": results, "verdict": "containment_stop", "next": "stop",
                    "points": mechanical_points([], False)})
        write_once(proj / score_name, doc)
        return 8, doc
    pts = mechanical_points(results, True)
    files = after["new_files"]
    doc.update({"commit": commit, "checks": results, "points": dict(pts, audit_25=None),
                "max_possible_total": round(pts["non_model_75"] + 25, 1),
                "failed_checks": [r["id"] for r in results if not r["passed"]],
                "unparsed_pass_if": [r["id"] for r in results if not r["pass_if_understood"]],
                "file_manifest": manifest(build_dir), "build_lines": build_lines(build_dir, files)})
    sha = write_once(proj / score_name, doc)
    w.setdefault("scores", {})[stage] = {"file": score_name, "sha256": sha, "commit": commit}
    L.log_event({"event": "build_score", "project": proj.name, "attempt": attempt, "stage": stage,
                 "built_by": built_by, "non_model_75": pts["non_model_75"],
                 "failed": doc["failed_checks"]})
    return 0, doc


def build_main(proj: Path, into: str | None, override: str | None, cap: float, dry: bool,
               repo: str = AGENT_OS) -> int:
    problems = prereq_problems(proj)
    if (proj / "Build_Score.json").exists():
        problems.append("this plan already has Build_Score.json; use --finalize / --after-fix / --rebuild-prep")
    if problems:
        print("lab_build: not ready to build:\n  - " + "\n  - ".join(problems), file=sys.stderr)
        return 1
    base = git(repo, "rev-parse", "HEAD").strip()
    rel = into or find_into((proj / "Plan_Locked.md").read_text(encoding="utf-8"),
                            lambda r: not into_check(repo, base, r))
    if not rel:
        print("lab_build: could not find the plan's new folder path (an existing parent folder plus a new "
              "Title_Case folder, in backticks, in 'New Folder And Files'). Rerun with --into <path>.",
              file=sys.stderr)
        return 1
    bad = into_check(repo, base, rel)
    if bad:
        print("lab_build: " + "; ".join(bad), file=sys.stderr)
        return 1
    key = load_secret(L.KEY_NAME)
    if not key:
        print(f"lab_build: {L.KEY_NAME} missing from ~/.env-secrets.", file=sys.stderr)
        return 2
    try:
        servers = mcp_server_names()
    except ConfigReadError as exc:
        print(f"lab_build: refused, {exc}. Can't confirm which MCP servers to switch off.", file=sys.stderr)
        return 4
    meta = _meta(proj)
    live = L.live_prices()
    picks = build_picks(live, override)
    if not picks:
        print("lab_build: no usable model (retired, or every worst-case estimate is over the build budget). "
              "See --list, or pass --model.", file=sys.stderr)
        return 6
    first, spent = picks[0], spent_so_far(proj, meta)
    remaining = round(cap - spent, 4)
    if first["est_usd"] > remaining:
        print(f"lab_build: STOPPED, needs Tony's OK. {first['id']} worst-case build ${first['est_usd']:.2f}; this "
              f"project has spent ${spent:.2f} of its ${cap:.2f} cap (${remaining:.2f} left). If Tony approves, "
              "rerun with --cap <higher USD>.", file=sys.stderr)
        return 5
    before = L.key_usage(key)
    left = before.get("limit_remaining") if before else None
    if left is not None and float(left) < first["est_usd"] + L.KEY_RESERVE_USD:
        print(f"lab_build: STOPPED, needs Tony's OK. The shared OpenRouter key has ${float(left):.2f} left; this "
              f"build could use ${first['est_usd']:.2f} and ${L.KEY_RESERVE_USD:.2f} stays reserved for Jev.",
              file=sys.stderr)
        return 5
    pf = preflight(servers, [proj / "Plan_Locked.md"])
    if not pf["ok"]:
        print("lab_build: CONTAINMENT STOP before spending anything. The free preflight found:\n  - "
              + "\n  - ".join(pf["problems"]), file=sys.stderr)
        emit("LAB_BUILD_RESULT", {"ok": False, "exit_code": 8, "stage": "preflight", "preflight": pf})
        return 8
    if dry:
        emit("LAB_BUILD_PICK", {"picks": picks, "into": rel, "base_commit": base, "remaining_cap_usd": remaining,
                                "worktree": str(proj / f"Build_Worktree_{len(meta.get('worktrees', [])) + 1}"),
                                "preflight": pf, "live_list": live is not None})
        return 0

    meta.update({"project_dir": str(proj), "plan": proj.name, "into": rel, "cap_usd": cap,
                 "plan_spend_usd": spent_so_far(proj, None), "preflight": {"ok": True, "targets": pf["targets"]}})
    w = new_worktree(proj, meta, repo, base, rel)
    w.update({"attempt": 1, "built_by": first["id"], "why_picked": first["why"],
              "price_per_m_tokens": {"input": first["in_price"], "output": first["out_price"]},
              "est_worst_case_usd": first["est_usd"]})
    meta.setdefault("worktrees", []).append(w)
    write_json(proj / "Build_Meta.json", meta)
    main_before = git_status(repo)
    prompt = BUILD_RULES.format(build_dir=w["build_dir"], plan=proj / "Plan_Locked.md",
                                checks=proj / "Acceptance_Checks.json", agent_os=AGENT_OS)
    stamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    log_path, last_msg, log = open_log(stamp, prefix="Agent-OS-Lab-Build")
    try:
        rc, secs, over = run_worker(build_command(prompt, first["id"], w["build_dir"], last_msg, servers),
                                    key, log, remaining, before)
    finally:
        log.close()
    after = L.key_usage(key)
    tok = L.usage_from_log(log_path)
    w.update({"exit_code": rc, "seconds": secs, "log": str(log_path), "tokens": tok,
              "token_cost_usd": round(tok["input_tokens"] / 1e6 * first["in_price"]
                                      + tok["output_tokens"] / 1e6 * first["out_price"], 4),
              "key_spend_delta_usd": round(after["usage"] - before["usage"], 4) if before and after else None,
              "stopped_for_spend": over})
    w["cost_usd"] = w["key_spend_delta_usd"] if w["key_spend_delta_usd"] is not None else w["token_cost_usd"]
    try:
        w["builder_report"] = Path(last_msg).read_text(encoding="utf-8")[-4000:]
    except OSError:
        w["builder_report"] = None
    main_after = git_status(repo)
    if main_before is not None and main_after is not None:
        w["main_workspace_new_git_entries"] = sorted(main_after - main_before)  # info: other sessions too
    write_json(proj / "Build_Meta.json", meta)
    L.log_event({"event": "build", "project": proj.name, "model": first["id"], "exit_code": rc,
                 "cost_usd": w["cost_usd"], "seconds": secs})

    cont = check_containment(Path(w["worktree"]), base, rel)  # always, whatever the worker's exit code
    if not cont["ok"] or rc != 0:
        if not cont["ok"]:
            code, doc = score_stage(proj, meta, w, 1, "raw", first["id"], servers, run_preflight=False)
        else:
            code, doc = (5 if over else 124 if rc == 124 else 6), {"containment": cont}
        write_json(proj / "Build_Meta.json", meta)
        result = {"ok": False, "exit_code": code, "project_dir": str(proj), "worktree": w["worktree"],
                  "build_dir": w["build_dir"], "model": first["id"], "cost_usd": w["cost_usd"],
                  "log": str(log_path), "containment": doc.get("containment")}
        msg = {8: "CONTAINMENT STOP: the build touched something outside its folder. No fix will be tried.",
               5: f"stopped: this build passed the project's remaining ${remaining:.2f}. Ask Tony before more.",
               124: "build worker timed out.", 6: f"build worker failed (exit {rc})."}[code]
        print(f"lab_build: {msg} Log: {log_path}", file=sys.stderr)
        emit("LAB_BUILD_RESULT", result)
        return code
    code, doc = score_stage(proj, meta, w, 1, "raw", first["id"], servers)
    write_json(proj / "Build_Meta.json", meta)
    result = {"ok": code == 0, "exit_code": code, "project_dir": str(proj), "worktree": w["worktree"],
              "build_dir": w["build_dir"], "model": first["id"], "why_picked": first["why"],
              "cost_usd": w["cost_usd"], "score_file": SCORE_FILES[(1, "raw")],
              "points": doc.get("points"), "failed_checks": doc.get("failed_checks"),
              "max_possible_total": doc.get("max_possible_total"),
              "next": "opus_audit" if code == 0 else "stop", "log": str(log_path)}
    if code == 0:
        print("lab_build: raw build scored. READY FOR OPUS AUDIT (Build_Audit.json, then --finalize).")
    emit("LAB_BUILD_RESULT", result)
    return code


def _current(meta: dict) -> dict | None:
    return meta.get("worktrees", [])[-1] if meta.get("worktrees") else None


def finalize_main(proj: Path) -> int:
    """Validate the audit for the current attempt, combine 75 + 25, decide the next step."""
    meta, verdicts = _meta(proj), _verdicts(proj)
    w = _current(meta)
    if not w or "raw" not in w.get("scores", {}):
        print("lab_build: nothing scored yet for this project", file=sys.stderr)
        return 1
    attempt = w["attempt"]
    if any(h["attempt"] == attempt and h["stage"] == "raw" for h in verdicts["history"]):
        print("lab_build: this attempt is already finalized; use --after-fix or --rebuild-prep", file=sys.stderr)
        return 1
    sc = w["scores"]["raw"]
    score_p, audit_p = proj / sc["file"], proj / AUDIT_FILES[attempt]
    problems, tamper = [], False
    if not score_p.exists() or L.sha256(score_p) != sc["sha256"]:
        problems.append(f"{sc['file']} was changed or removed after it was written (score-before-edit broken)")
        tamper = True
    score = read_json(score_p) if score_p.exists() else {}
    build_dir = Path(w["build_dir"])
    if score and manifest(build_dir) != score.get("file_manifest"):
        problems.append("the build folder changed after it was scored and before this finalize "
                        "(the audit must not edit the build; that is the fix round's job, after finalize)")
        tamper = True
    try:
        audit = read_json(audit_p)
    except (OSError, ValueError) as exc:
        audit = {}
        problems.append(f"{audit_p.name} missing or not valid JSON: {exc}")
    if audit_p.exists() and score_p.exists() and audit_p.stat().st_mtime < score_p.stat().st_mtime:
        problems.append(f"{audit_p.name} is older than {sc['file']} (the audit must come after the raw score)")
    review = proj / "Build_Review.md"
    if not review.exists() or not review.read_text(encoding="utf-8").strip():
        problems.append("Build_Review.md missing or empty")
    pts, items, ap = audit_points(audit, build_dir, score, sc["file"]) if audit else (0.0, [], [])
    problems += ap
    if problems:
        emit("LAB_BUILD_VERDICT", {"ok": False, "problems": problems, "score_tampered": tamper})
        return 7
    non_model = score["points"]["non_model_75"]
    c = combine(non_model, pts)
    fix_used = any(h["stage"] == "fix" for h in verdicts["history"])
    rebuild_used = len(meta.get("worktrees", [])) > 1 and any(x.get("attempt") == 2 for x in meta["worktrees"])
    failures = [f"{r['id']} ({r['what']}): failed" for r in score.get("checks", []) if not r["passed"]]
    failures += [f"{i['id']}: {i['why']}" for i in items if i["points"] < i["max"] and i.get("why")]
    failures += [str(x) for x in audit.get("failures_to_fix", [])]
    nxt = next_step(c["total"], non_model, stage="raw", fix_used=fix_used, rebuild_used=rebuild_used,
                    has_failures=bool(failures), fix_judged_too_big=bool(audit.get("fix_would_exceed_third")))
    entry = {"attempt": attempt, "stage": "raw", "built_by": w["built_by"], **c, "audit_items": items,
             "named_failures": failures, "next": nxt, "decided": time.strftime("%Y-%m-%dT%H:%M:%S")}
    verdicts["history"].append(entry)
    verdicts["current"] = entry
    if nxt == "lab_run":
        verdicts["tony_paid_run"] = read_json(proj / "Acceptance_Checks.json").get("tony_paid_run", [])
    write_json(proj / "Build_Verdict.json", verdicts)
    L.log_event({"event": "build_verdict", "project": proj.name, "attempt": attempt, "stage": "raw",
                 "built_by": w["built_by"], "total": c["total"], "non_model_75": non_model, "audit_25": pts,
                 "next": nxt})
    emit("LAB_BUILD_VERDICT", {"ok": True, **{k: entry[k] for k in ("attempt", "stage", "non_model_75",
                                                                       "audit_25", "total", "cleared", "next")},
                               "named_failures": failures, "build_dir": w["build_dir"],
                               "tony_paid_run": verdicts.get("tony_paid_run")})
    return 0


def after_fix_main(proj: Path) -> int:
    meta, verdicts = _meta(proj), _verdicts(proj)
    w, cur = _current(meta), verdicts.get("current") or {}
    if not w or cur.get("next") != "fix_round" or cur.get("attempt") != w["attempt"]:
        print("lab_build: no fix round is due (the latest verdict did not say fix_round)", file=sys.stderr)
        return 1
    attempt = w["attempt"]
    try:
        servers = mcp_server_names()
    except ConfigReadError as exc:
        print(f"lab_build: refused, {exc}", file=sys.stderr)
        return 4
    raw_commit = w["scores"]["raw"]["commit"]
    code, doc = score_stage(proj, meta, w, attempt, "fix", "opus-standard (fix round)", servers)
    write_json(proj / "Build_Meta.json", meta)
    if code != 0:
        entry = {"attempt": attempt, "stage": "fix", "next": "stop", "exit_code": code,
                 "containment": doc.get("containment")}
        verdicts["history"].append(entry); verdicts["current"] = entry
        write_json(proj / "Build_Verdict.json", verdicts)
        emit("LAB_BUILD_VERDICT", {"ok": False, **entry})
        return code
    wt, rel = Path(w["worktree"]), meta["into"]
    ratio = fix_ratio(numstat(wt, w["base_commit"], raw_commit, rel), numstat(wt, raw_commit, doc["commit"], rel))
    non_model = doc["points"]["non_model_75"]
    c = combine(non_model, cur["audit_25"])  # the reviewer's raw-build points; it never grades its own fix
    rebuild_used = any(x.get("attempt") == 2 for x in meta["worktrees"])
    nxt = next_step(c["total"], non_model, stage="fix", fix_used=True, rebuild_used=rebuild_used,
                    has_failures=bool(doc["failed_checks"]), fix_ratio_value=ratio)
    entry = {"attempt": attempt, "stage": "fix", **c, "fix_ratio": ratio,
             "fix_too_big": ratio > MAX_FIX_RATIO, "failed_checks": doc["failed_checks"], "next": nxt,
             "decided": time.strftime("%Y-%m-%dT%H:%M:%S")}
    verdicts["history"].append(entry); verdicts["current"] = entry
    if nxt == "lab_run":
        verdicts["tony_paid_run"] = read_json(proj / "Acceptance_Checks.json").get("tony_paid_run", [])
    write_json(proj / "Build_Verdict.json", verdicts)
    L.log_event({"event": "build_verdict", "project": proj.name, "attempt": attempt, "stage": "fix",
                 "total": c["total"], "fix_ratio": ratio, "next": nxt})
    emit("LAB_BUILD_VERDICT", {"ok": True, **{k: entry[k] for k in ("attempt", "stage", "non_model_75",
                                                                       "audit_25", "total", "cleared",
                                                                       "fix_ratio", "next")},
                               "failed_checks": doc["failed_checks"], "build_dir": w["build_dir"],
                               "tony_paid_run": verdicts.get("tony_paid_run")})
    return 0


def rebuild_prep_main(proj: Path, repo: str = AGENT_OS) -> int:
    meta, verdicts = _meta(proj), _verdicts(proj)
    if (verdicts.get("current") or {}).get("next") != "rebuild":
        print("lab_build: no rebuild is due (the latest verdict did not say rebuild)", file=sys.stderr)
        return 1
    if any(x.get("attempt") == 2 for x in meta.get("worktrees", [])):
        print("lab_build: the one rebuild was already used", file=sys.stderr)
        return 1
    base = git(repo, "rev-parse", "HEAD").strip()
    rel = meta["into"]
    bad = into_check(repo, base, rel)
    if bad:
        print("lab_build: " + "; ".join(bad), file=sys.stderr)
        return 1
    w = new_worktree(proj, meta, repo, base, rel)
    w.update({"attempt": 2, "built_by": "opus-standard (rebuild)"})
    meta["worktrees"].append(w)
    write_json(proj / "Build_Meta.json", meta)
    emit("LAB_BUILD_RESULT", {"ok": True, "stage": "rebuild_prep", "build_dir": w["build_dir"],
                              "worktree": w["worktree"], "old_worktree": meta["worktrees"][-2]["worktree"],
                              "plan": str(proj / "Plan_Locked.md"),
                              "checks": str(proj / "Acceptance_Checks.json")})
    return 0


def score_rebuild_main(proj: Path) -> int:
    meta = _meta(proj)
    w = _current(meta)
    if not w or w.get("attempt") != 2 or "raw" in w.get("scores", {}):
        print("lab_build: no unscored rebuild found (run --rebuild-prep first)", file=sys.stderr)
        return 1
    try:
        servers = mcp_server_names()
    except ConfigReadError as exc:
        print(f"lab_build: refused, {exc}", file=sys.stderr)
        return 4
    code, doc = score_stage(proj, meta, w, 2, "raw", w["built_by"], servers)
    write_json(proj / "Build_Meta.json", meta)
    emit("LAB_BUILD_RESULT", {"ok": code == 0, "exit_code": code, "stage": "rebuild_raw",
                              "build_dir": w["build_dir"], "score_file": SCORE_FILES[(2, "raw")],
                              "points": doc.get("points"), "failed_checks": doc.get("failed_checks"),
                              "containment": doc.get("containment"),
                              "next": "opus_audit" if code == 0 else "stop"})
    return code


def _claimed(audit: dict) -> dict:
    """Each rubric item's points as audit_points() recorded them ('claimed'), for a change check."""
    out = {}
    for it in (audit.get("items", []) if isinstance(audit, dict) else []):
        if isinstance(it, dict) and it.get("id") in RUBRIC:
            pts = it.get("points")
            pts = pts if isinstance(pts, (int, float)) and not isinstance(pts, bool) else 0
            out[it["id"]] = max(0, min(RUBRIC[it["id"]][0], pts))
    return out


def reverify_refusal(proj: Path, meta: dict, verdicts: dict) -> str | None:
    """Why --reverify may not run now, or None. Only a build that already reached lab_run or stop
    through the normal path qualifies, once per project; fix_round/rebuild keep their own commands."""
    for name in (SCORE_FILES[(1, "raw")], AUDIT_FILES[1]):
        if not (proj / name).exists():
            return f"{name} missing: --reverify only rechecks a build that was already scored and audited"
    if (proj / REVERIFY_FILE).exists():
        return f"{REVERIFY_FILE} already exists: --reverify runs once per project, never twice"
    cur, w = verdicts.get("current") or {}, _current(meta)
    nxt = cur.get("next")
    if nxt == "fix_round":
        return "the latest verdict says fix_round: use --after-fix for that, not --reverify"
    if nxt == "rebuild":
        return ("the latest verdict says rebuild: use --rebuild-prep (then --score-rebuild and --finalize), "
                "not --reverify")
    if nxt not in ("lab_run", "stop"):
        return "no finished verdict yet: run --finalize first"
    if cur.get("exit_code"):
        return (f"the latest stage ended in a stop with exit {cur['exit_code']} (containment stop or failed "
                "build); that is final and --reverify cannot overrule it")
    if not w or cur.get("attempt") != w.get("attempt") or "raw" not in w.get("scores", {}):
        return "Build_Meta.json and Build_Verdict.json disagree about the current attempt"
    return None


def reverify_main(proj: Path, run_preflight: bool = True) -> int:
    """Voluntary one-shot recheck when a fix was applied AFTER the build already ended at lab_run or
    stop. Re-runs containment and every acceptance check (60 + 15 fresh), carries the original audit's
    25 unchanged (validated at --finalize; never re-scored, no new audit), writes REVERIFY_FILE once.
    No model, no paid API. Build_Score*.json and Build_Audit*.json are only read, never written."""
    meta, verdicts = _meta(proj), _verdicts(proj)
    why = reverify_refusal(proj, meta, verdicts)
    if why:
        print(f"lab_build: --reverify refused: {why}", file=sys.stderr)
        return 1
    cur, w = verdicts["current"], _current(meta)
    attempt = w["attempt"]
    raw_entry = next((h for h in verdicts["history"] if h.get("attempt") == attempt and h.get("stage") == "raw"), None)
    problems = []
    for stage, sc in w.get("scores", {}).items():
        p = proj / sc["file"]
        if not p.exists() or L.sha256(p) != sc["sha256"]:
            problems.append(f"{sc['file']} was changed or removed after it was written (score-before-edit broken)")
    audit_p = proj / AUDIT_FILES[attempt]
    try:
        audit = read_json(audit_p)
    except (OSError, ValueError) as exc:
        audit = None
        problems.append(f"{audit_p.name} missing or not valid JSON: {exc}")
    if raw_entry is None or not isinstance(raw_entry.get("audit_25"), (int, float)):
        problems.append(f"no finalized audit for attempt {attempt} in Build_Verdict.json")
    elif audit is not None and _claimed(audit) != {i["id"]: i.get("claimed") for i in raw_entry.get("audit_items", [])}:
        problems.append(f"{audit_p.name} no longer matches the audit --finalize validated (its points changed)")
    if problems:
        emit("LAB_BUILD_VERDICT", {"ok": False, "stage": "reverify", "problems": problems, "score_tampered": True})
        return 7
    try:
        servers = mcp_server_names()
    except ConfigReadError as exc:
        print(f"lab_build: refused, {exc}", file=sys.stderr)
        return 4
    raw_commit = w["scores"]["raw"]["commit"]
    code, doc = score_stage(proj, meta, w, attempt, "reverify", "voluntary fix after the verdict (reverify)",
                            servers, run_preflight=run_preflight)
    write_json(proj / "Build_Meta.json", meta)
    base_entry = {"attempt": attempt, "stage": "reverify", "score_file": REVERIFY_FILE,
                  "previous_total": cur.get("total"), "previous_next": cur.get("next")}
    if code != 0:
        entry = dict(base_entry, next="stop", exit_code=code, containment=doc.get("containment"),
                     decided=time.strftime("%Y-%m-%dT%H:%M:%S"))
        verdicts["history"].append(entry); verdicts["current"] = entry
        verdicts.pop("tony_paid_run", None)
        write_json(proj / "Build_Verdict.json", verdicts)
        L.log_event({"event": "build_verdict", "project": proj.name, "attempt": attempt, "stage": "reverify",
                     "exit_code": code, "next": "stop"})
        print("lab_build: " + ("CONTAINMENT STOP during --reverify. No fix will be tried." if code == 8
                               else f"--reverify could not score the build (exit {code})."), file=sys.stderr)
        emit("LAB_BUILD_VERDICT", {"ok": False, **entry, "build_dir": w["build_dir"]})
        return code
    wt, rel = Path(w["worktree"]), meta["into"]
    ratio = fix_ratio(numstat(wt, w["base_commit"], raw_commit, rel), numstat(wt, raw_commit, doc["commit"], rel))
    non_model = doc["points"]["non_model_75"]
    c = combine(non_model, raw_entry["audit_25"])  # the original audit's points, carried, never re-scored
    too_big = ratio > MAX_FIX_RATIO  # same rule as --after-fix: the audit only carries over a small fix
    cleared = c["cleared"] and not too_big
    nxt = "lab_run" if cleared else "stop"  # one-shot: no fix round or rebuild chain from here
    entry = dict(base_entry, **dict(c, cleared=cleared), audit_25_source=f"{audit_p.name} (validated at --finalize)",
                 fix_ratio=ratio, fix_too_big=too_big, failed_checks=doc["failed_checks"], next=nxt,
                 decided=time.strftime("%Y-%m-%dT%H:%M:%S"))
    verdicts["history"].append(entry); verdicts["current"] = entry
    if nxt == "lab_run":
        verdicts["tony_paid_run"] = read_json(proj / "Acceptance_Checks.json").get("tony_paid_run", [])
    else:
        verdicts.pop("tony_paid_run", None)
    write_json(proj / "Build_Verdict.json", verdicts)
    L.log_event({"event": "build_verdict", "project": proj.name, "attempt": attempt, "stage": "reverify",
                 "total": c["total"], "fix_ratio": ratio, "next": nxt})
    emit("LAB_BUILD_VERDICT", {"ok": True, **{k: entry[k] for k in ("attempt", "stage", "non_model_75",
                                                                       "audit_25", "total", "cleared",
                                                                       "fix_ratio", "next")},
                               "previous_total": entry["previous_total"], "fix_too_big": too_big,
                               "failed_checks": doc["failed_checks"], "score_file": REVERIFY_FILE,
                               "build_dir": w["build_dir"], "tony_paid_run": verdicts.get("tony_paid_run")})
    return 0


def preflight_main() -> int:
    try:
        servers = mcp_server_names()
    except ConfigReadError as exc:
        print(f"lab_build: refused, {exc}", file=sys.stderr)
        return 4
    pf = preflight(servers)
    emit("LAB_BUILD_PREFLIGHT", pf)
    return 0 if pf["ok"] else 8


def list_main() -> int:
    live = L.live_prices()
    print(f"Live OpenRouter list: {'reachable' if live is not None else 'UNREACHABLE (static prices shown)'}")
    print(f"Build worst case = {EST_BUILD_IN:,} in + {EST_BUILD_OUT:,} out tokens; over "
          f"${BUILD_BUDGET_USD:.2f} is skipped unless --model.\n\ncode (build order):")
    for mid in L.PREFERENCE["code"]:
        c = L.CANDIDATES[mid]
        inp, outp = live[mid] if live and mid in live else (c.in_price, c.out_price)
        est = EST_BUILD_IN / 1e6 * inp + EST_BUILD_OUT / 1e6 * outp
        flag = "" if live is None or mid in live else "  [NOT ON OPENROUTER NOW]"
        skip = "  [skipped: over build budget]" if est > BUILD_BUDGET_USD else ""
        print(f"  {mid:32s} ${inp:.3f}/${outp:.3f} per M  build worst-case ${est:.2f}{skip}{flag}")
    return 0


# ---------------------------------------------------------------- CLI

def main(argv: list[str]) -> int:
    if os.environ.get("AGENT_OS_DELEGATE_WORKER"):
        print("lab_build: refused, already inside a delegated worker", file=sys.stderr)
        return 3
    args = list(argv)
    if args[:1] == ["--list"]:
        return list_main()
    if not shutil.which("codex"):
        print("lab_build: the codex CLI is not on PATH; the sandbox needs it", file=sys.stderr)
        return 1
    if args[:1] == ["--preflight"]:
        return preflight_main()
    modes = {"--finalize": finalize_main, "--after-fix": after_fix_main,
             "--rebuild-prep": rebuild_prep_main, "--score-rebuild": score_rebuild_main,
             "--reverify": reverify_main}
    if args[:1] and args[0] in modes:
        proj = resolve_project(args[1] if len(args) > 1 else None)
        if len(args) != 2 or not proj:
            print(__doc__); return 1
        return modes[args[0]](proj)

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
        into, override, cap = take("--into"), take("--model"), take("--cap")
        cap = float(cap) if cap else L.PROJECT_CAP_USD
    except ValueError as exc:
        print(f"lab_build: {exc}\n{__doc__}", file=sys.stderr)
        return 1
    dry = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]
    if len(args) > 1 or any(a.startswith("--") for a in args):
        print(__doc__); return 1
    proj = resolve_project(args[0] if args else None)
    if not proj:
        print("lab_build: no such project folder, and no locked unbuilt plan found in 001_Architecture/Lab/",
              file=sys.stderr)
        return 1
    return build_main(proj, into.strip("/") if into else None, override, cap, dry)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
