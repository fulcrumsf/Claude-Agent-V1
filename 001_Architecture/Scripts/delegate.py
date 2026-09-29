#!/usr/bin/env python3
"""delegate: hand a chore to a cheap worker on Jev Router (Option B, 2026-09-27; switched
from OpenRouter's generic Auto Router to TypeSafe's Jev Router, which adapts model choice
per-request rather than per-session, still constrained by the workspace's cost-tier allowlist).

Usage: delegate.py "<task>" [--skill Skill_Name] [--cwd PATH] [--dry-run]
The worker is `codex exec` on OpenRouter (key OPENROUTER_CHORES_KEY, capped by Tony),
so the fs_guard hook and Codex rules still block deletes and new folders.
Worker restrictions (command-line -c overrides only; ~/.codex/config.toml is never edited):
no plugins, apps, browser/computer use or image generation, every MCP server from
~/.codex/config.toml disabled, low reasoning effort, stopped after 30 minutes.
Hooks stay on, so the fs_guard PreToolUse hook still fires.
Prints the worker's final report plus the files it changed; the calling model must
check that list before telling Tony the chore is done.
Exit codes: worker's own code, 1 usage error, 2 no chores key,
3 refused (already inside a delegated worker), 124 worker timed out.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jev_route import load_secret  # noqa: E402

AGENT_OS = "/Users/tonymacbook2025/Documents/Agent-OS"
MODEL = "openrouter/auto"
WORKER_TIMEOUT = 1800  # seconds; chores that run longer are stopped and reported
CODEX_CONFIG = Path.home() / ".codex" / "config.toml"
# Codex features switched off for the worker: plugins (and the MCP servers they bring),
# connectors/apps, browser and computer use, paid image generation. Hooks stay on.
DISABLED_FEATURES = ("plugins", "remote_plugin", "apps", "browser_use", "computer_use", "image_generation")
MAX_SNAPSHOT_FILES = 5000  # bound on files snapshotted before/after a run
MAX_FILES_PER_ROOT = 1000  # bound per already-dirty folder (000_Ingest included)
INGEST_DIR = "000_Ingest"
PROVIDER = ('model_providers.openrouter_chores={name="OpenRouter chores", '
            'base_url="https://openrouter.ai/api/v1", env_key="OPENROUTER_CHORES_KEY", wire_api="responses"}')
RULES = (
    "You are a chore worker in Tony's Agent-OS workspace. Rules, no exceptions:\n"
    "- Never delete files or folders. Never create a new folder. Guards block both; if blocked, stop and report.\n"
    "- Never run delegate.py yourself; you are already the delegated worker.\n"
    "- Follow the named skill exactly. Do not invent rules, tags, folder names or steps it doesn't list.\n"
    "- Never publish, send, upload, buy, or call paid generation APIs.\n"
    "- If anything is unclear, do the safe part only and list the questions for Tony.\n"
    "- Finish with a short report: what you did, every file you changed, anything skipped and why.\n"
)


def build_prompt(task: str, skill: str | None) -> str:
    parts = [RULES]
    if skill:
        parts.append(f"First read {AGENT_OS}/001_Architecture/Skills/{skill}/SKILL.md completely and follow it step by step.\n")
    parts.append(f"Task: {task}")
    return "\n".join(parts)


class ConfigReadError(Exception):
    """The Codex config exists but couldn't be read/parsed, so its MCP server names
    are unknown. Callers must fail closed (refuse to run the worker) rather than
    silently proceeding as if there were no servers to disable."""


def mcp_server_names(config_path: Path = CODEX_CONFIG) -> list[str]:
    """Names of MCP servers in the Codex config (read-only; values are never printed).
    No config file at all means no servers are configured -> []  is safe.
    A config file that exists but can't be read/parsed raises ConfigReadError:
    servers may be configured but we can't see their names to disable them."""
    if not config_path.exists():
        return []
    try:
        import tomllib
        with open(config_path, "rb") as fh:
            servers = tomllib.load(fh).get("mcp_servers")
    except Exception as exc:
        raise ConfigReadError(f"could not read/parse {config_path}: {exc}") from exc
    return sorted(servers) if isinstance(servers, dict) else []


def isolation_overrides(servers: list[str], effort: str = "low") -> list[str]:
    """`effort` lets frontier.py reuse the same isolation at medium/high effort."""
    out = [f'model_reasoning_effort="{effort}"']
    out += [f"features.{f}=false" for f in DISABLED_FEATURES]
    out += [f"mcp_servers.{n}.enabled=false" for n in servers if re.fullmatch(r"[A-Za-z0-9_-]+", n)]
    return out


def build_command(prompt: str, cwd: str, last_msg_file: str, servers: list[str] | None = None) -> list[str]:
    cmd = ["codex", "exec", "--skip-git-repo-check", "-C", cwd,
           "-c", PROVIDER, "-c", "model_provider=openrouter_chores"]
    for o in isolation_overrides(mcp_server_names() if servers is None else servers):
        cmd += ["-c", o]
    return cmd + ["-m", MODEL, "--output-last-message", last_msg_file, prompt]


def open_log(stamp: str, prefix: str = "Agent-OS-Delegate"):
    """Open the worker's full-output log for writing (`prefix` lets frontier.py name its own logs). Prefers ~/Library/Logs (so Tony
    finds every run in one place); falls back to the system temp dir if that's not
    writable -- some sandboxes (Codex Desktop, seen 2026-09-27) block writes outside
    the workspace and /tmp, and this must never crash the chore over a log location.
    Returns (log_path, last_msg_path, open file handle)."""
    primary = Path.home() / "Library" / "Logs" / f"{prefix}-{stamp}.log"
    try:
        return primary, str(primary.with_suffix(".last.txt")), open(primary, "w", encoding="utf-8")
    except OSError:
        pass
    fd, path = tempfile.mkstemp(prefix=f"{prefix}-{stamp}-", suffix=".log")
    log_path = Path(path)
    return log_path, str(log_path.with_suffix(".last.txt")), os.fdopen(fd, "w", encoding="utf-8")


def git_status(cwd: str) -> set[str] | None:
    """`git status --porcelain` entries as "XY path" strings, or None if git can't run."""
    try:
        out = subprocess.run(["git", "-C", cwd, "status", "--porcelain", "-z"], capture_output=True,
                             text=True, timeout=30)
    except Exception:
        return None
    if out.returncode != 0:
        return None
    entries, toks, i = set(), out.stdout.split("\0"), 0
    while i < len(toks):
        tok = toks[i]
        i += 1
        if len(tok) < 4:
            continue
        entries.add(tok)
        if tok[0] in "RC":  # rename/copy: next token is the original path
            i += 1
    return entries


def snapshot(cwd: str, entries: set[str] | None) -> dict[str, tuple[float, int]]:
    """mtime+size of every file under 000_Ingest (gitignored, the main chore target) plus files
    already dirty in git. Bounded: hidden folders are skipped, each folder root contributes at most
    MAX_FILES_PER_ROOT files and the whole snapshot at most MAX_SNAPSHOT_FILES. The "~capped" key
    records that a bound was hit."""
    roots = [INGEST_DIR] + sorted(e[3:] for e in (entries or ()))
    snap: dict[str, tuple[float, int]] = {}
    for rel in roots:
        base = os.path.join(cwd, rel.rstrip("/"))
        if os.path.isfile(base):
            files = [base]
        elif os.path.isdir(base) and not os.path.basename(base).startswith("."):
            files = []
            for d, dirs, fs in os.walk(base):
                dirs[:] = sorted(x for x in dirs if not x.startswith("."))
                files += [os.path.join(d, f) for f in sorted(fs)]
                if len(files) > MAX_FILES_PER_ROOT:
                    snap["~capped"] = (0.0, 0)
                    files = files[:MAX_FILES_PER_ROOT]
                    break
        else:
            continue
        for path in files:
            if len(snap) >= MAX_SNAPSHOT_FILES:
                snap["~capped"] = (0.0, 0)
                return snap
            try:
                st = os.stat(path)
            except OSError:
                continue
            snap[os.path.relpath(path, cwd)] = (st.st_mtime, st.st_size)
    return snap


def change_report(before_git: set[str] | None, after_git: set[str] | None,
                  before_snap: dict, after_snap: dict) -> str:
    """Only what changed during the run: git status entries added/removed, plus snapshot diffs."""
    capped = "~capped" in before_snap or "~capped" in after_snap
    before_snap = {k: v for k, v in before_snap.items() if k != "~capped"}
    after_snap = {k: v for k, v in after_snap.items() if k != "~capped"}
    lines = []
    if before_git is None or after_git is None:
        lines.append("  git status could not be read (not a git folder or git missing)")
    else:
        lines += [f"  new git entry:  {e}" for e in sorted(after_git - before_git)]
        lines += [f"  git entry gone: {e}" for e in sorted(before_git - after_git)]
    lines += [f"  added:   {p}" for p in sorted(set(after_snap) - set(before_snap))]
    lines += [f"  changed: {p}" for p in sorted(p for p in set(before_snap) & set(after_snap)
                                               if before_snap[p] != after_snap[p])]
    lines += [f"  missing: {p}" for p in sorted(set(before_snap) - set(after_snap))]
    if capped:
        lines.append("  (file snapshot hit its size bound; some big folders were only partly checked)")
    if not lines:
        return "(no changes detected)"
    return "\n".join(lines)


class UsageError(Exception):
    pass


def main(argv: list[str]) -> int:
    if os.environ.get("AGENT_OS_DELEGATE_WORKER"):
        print("delegate: refused, already inside a delegated worker", file=sys.stderr)
        return 3
    args = list(argv)

    def take(flag):
        if flag not in args:
            return None
        i = args.index(flag)
        if i + 1 >= len(args) or args[i + 1].startswith("--"):
            raise UsageError(f"{flag} needs a value")
        val = args[i + 1]
        del args[i:i + 2]
        return val
    try:
        skill, cwd = take("--skill"), take("--cwd") or AGENT_OS
    except UsageError as exc:
        print(f"delegate: {exc}\n{__doc__}", file=sys.stderr)
        return 1
    dry = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]
    if not args:
        print(__doc__); return 1
    key = load_secret("OPENROUTER_CHORES_KEY")
    if not key:
        print("delegate: OPENROUTER_CHORES_KEY missing from ~/.env-secrets (see plan Task 0).", file=sys.stderr)
        return 2
    try:
        servers = mcp_server_names()
    except ConfigReadError as exc:
        print(f"delegate: refused — {exc}. Can't confirm which MCP servers to disable for the worker, "
              "so it will not run isolated. Fix ~/.codex/config.toml and retry.", file=sys.stderr)
        return 4
    stamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    if dry:
        last_msg = str(Path.home() / "Library" / "Logs" / f"Agent-OS-Delegate-{stamp}.last.txt")
        cmd = build_command(build_prompt(" ".join(args), skill), cwd, last_msg, servers=servers)
        print(" ".join(cmd[:-1]) + " <prompt>"); return 0
    log_path, last_msg, log = open_log(stamp)
    cmd = build_command(build_prompt(" ".join(args), skill), cwd, last_msg, servers=servers)
    before_git = git_status(cwd)
    before_snap = snapshot(cwd, before_git)
    note = ""
    try:
        try:
            rc = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, timeout=WORKER_TIMEOUT,
                                env=dict(os.environ, OPENROUTER_CHORES_KEY=key,
                                         AGENT_OS_DELEGATE_WORKER="1")).returncode
        except subprocess.TimeoutExpired:
            rc = 124
            note = (f"\nWORKER TIMED OUT after {WORKER_TIMEOUT} s and was stopped. The chore may be half done; "
                    "check the changed files below.\n")
    finally:
        log.close()
    report = Path(last_msg).read_text(encoding="utf-8") if Path(last_msg).exists() else "(no final report)"
    after_git = git_status(cwd)
    changes = change_report(before_git, after_git, before_snap, snapshot(cwd, before_git))
    print(f"Worker exit code: {rc}{note}\n\n== Worker report ==\n{report}\n\n"
          f"== Files changed during the run ==\n{changes}\n\n"
          f"Full log: {log_path}\nCheck every changed file against the skill before reporting done.")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
