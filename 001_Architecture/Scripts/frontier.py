#!/usr/bin/env python3
"""frontier: hand hard work to a frontier model from any shell (Tony, 2026-09-27).

Usage: frontier.py "<task>" [--deep] [--cwd PATH] [--dry-run]

Why this exists: Claude Code has opus-standard/opus-deep and Codex has sol-standard/sol-deep,
but Antigravity has no custom-subagent config, so it had no way to reach a frontier model at
all. This is its frontier subagent, and any harness can use it. When route_gate.py enforces a
frontier turn in Antigravity, running this command is what opens the gate.
(Gemini CLI doesn't need it: route_gate switches enforced Gemini turns to Pro directly.)

Engine: `codex exec` on Tony's ChatGPT login with gpt-6-sol (the sol-standard model) at
medium effort; --deep means high effort (sol-deep). Same isolation as delegate.py: no plugins,
apps, browser/computer use or image generation, every MCP server disabled, and
AGENT_OS_DELEGATE_WORKER=1 so the worker never routes, gates or delegates itself.
Stopped after 45 minutes. Prints the worker's report plus the files it changed; the caller
checks that list before telling Tony the work is done.
Exit codes: worker's own code, 1 usage error, 3 refused (already inside a worker),
4 Codex config unreadable, 124 worker timed out.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from delegate import (AGENT_OS, ConfigReadError, change_report, git_status,  # noqa: E402
                      isolation_overrides, mcp_server_names, open_log, snapshot)

MODEL = "gpt-6-sol"  # same model as ~/.codex/agents/sol-standard.toml and sol-deep.toml
EFFORT, DEEP_EFFORT = "medium", "high"
WORKER_TIMEOUT = 2700  # seconds; frontier work runs longer than chores
RULES = (
    "You are the frontier worker for Tony's Agent-OS workspace, called because this task needs deeper "
    "reasoning than the calling model. Rules, no exceptions:\n"
    "- Follow AGENTS.md and any skill the task names exactly. Do not invent rules, tags, folders or steps.\n"
    "- Never delete files or folders. Never create a new folder. Guards block both; if blocked, stop and report.\n"
    "- Never run frontier.py or delegate.py yourself; you are already the worker.\n"
    "- Never publish, send, upload, buy, or call paid generation APIs.\n"
    "- Think the problem through first, do the task fully, and verify the real result (run it, test it).\n"
    "- Finish with a short report: what you did, what you verified, every file you changed, anything left open.\n"
)


def build_prompt(task: str) -> str:
    return f"{RULES}\nTask: {task}"


def build_command(prompt: str, cwd: str, last_msg_file: str, deep: bool = False,
                  servers: list[str] | None = None) -> list[str]:
    """Uses Codex's default provider (Tony's ChatGPT login), not delegate.py's OpenRouter provider."""
    cmd = ["codex", "exec", "--skip-git-repo-check", "-C", cwd]
    effort = DEEP_EFFORT if deep else EFFORT
    for o in isolation_overrides(mcp_server_names() if servers is None else servers, effort=effort):
        cmd += ["-c", o]
    return cmd + ["-m", MODEL, "--output-last-message", last_msg_file, prompt]


def main(argv: list[str]) -> int:
    if os.environ.get("AGENT_OS_DELEGATE_WORKER"):
        print("frontier: refused, already inside a delegated worker", file=sys.stderr)
        return 3
    args = list(argv)
    cwd = AGENT_OS
    if "--cwd" in args:
        i = args.index("--cwd")
        if i + 1 >= len(args) or args[i + 1].startswith("--"):
            print(f"frontier: --cwd needs a value\n{__doc__}", file=sys.stderr)
            return 1
        cwd = args[i + 1]
        del args[i:i + 2]
    deep, dry = "--deep" in args, "--dry-run" in args
    args = [a for a in args if a not in ("--deep", "--dry-run")]
    if not args:
        print(__doc__)
        return 1
    try:
        servers = mcp_server_names()
    except ConfigReadError as exc:
        print(f"frontier: refused — {exc}. Can't confirm which MCP servers to disable for the worker, "
              "so it will not run isolated. Fix ~/.codex/config.toml and retry.", file=sys.stderr)
        return 4
    stamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    prompt = build_prompt(" ".join(args))
    if dry:
        cmd = build_command(prompt, cwd, "<last-message-file>", deep=deep, servers=servers)
        print(" ".join(cmd[:-1]) + " <prompt>")
        return 0
    log_path, last_msg, log = open_log(stamp, prefix="Agent-OS-Frontier")
    cmd = build_command(prompt, cwd, last_msg, deep=deep, servers=servers)
    before_git = git_status(cwd)
    before_snap = snapshot(cwd, before_git)
    note = ""
    try:
        try:
            rc = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, timeout=WORKER_TIMEOUT,
                                env=dict(os.environ, AGENT_OS_DELEGATE_WORKER="1")).returncode
        except subprocess.TimeoutExpired:
            rc = 124
            note = (f"\nWORKER TIMED OUT after {WORKER_TIMEOUT} s and was stopped. The work may be half done; "
                    "check the changed files below.\n")
    finally:
        log.close()
    report = Path(last_msg).read_text(encoding="utf-8") if Path(last_msg).exists() else "(no final report)"
    changes = change_report(before_git, git_status(cwd), before_snap, snapshot(cwd, before_git))
    print(f"Frontier worker ({MODEL}, {DEEP_EFFORT if deep else EFFORT} effort) exit code: {rc}{note}\n\n"
          f"== Worker report ==\n{report}\n\n== Files changed during the run ==\n{changes}\n\n"
          f"Full log: {log_path}\nCheck the changed files and the report before telling Tony it is done.")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
