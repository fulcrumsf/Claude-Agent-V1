#!/usr/bin/env python3
"""Agent-OS action log -- the paper trail for every agent, every harness (Tony, 2026-10-06).

Why it exists: Tony needs to answer "what touched this file, when, from which harness and
session, and why?" The guard log (Agent-OS-Guard.jsonl) only says a deny/ask happened, with
no target, so it can't answer that. This module is purely additive: it never blocks
anything and every entry point swallows its own errors, so the guard and router behave
exactly as before.

Three kinds of lines go into ~/Library/Logs/Agent-OS-Actions.jsonl:
  event=tool      every state-changing tool call that reaches fs_guard.py (writes, edits,
                  patches, non-read-only shell commands, subagent launches, MCP calls,
                  plus every deny/ask with its target). Called from fs_guard.py.
  event=prompt    every user prompt (the "why"), excerpted and redacted. Called from
                  jev_route.py, which already runs on the prompt event in all 4 harnesses.
  event=deletion_detected / deletion_cleared
                  the deletion sentinel: on each prompt, a tracked-only `git status`
                  (~30 ms) is compared to the last check. Any git-tracked file that went
                  missing is logged with the time window it vanished in -- this catches
                  deletions that no tool call made (harness housekeeping such as Codex's
                  system-skill resync, a script's internals, or Tony himself).

Each tool/prompt line carries whatever attribution the harness hands its hooks: session id,
transcript path, subagent id/type (Claude), turn id + model (Codex), tool_use_id, and
delegate_worker=true inside delegate.py workers.

Size: one line is kept under ~3.8 KB. When the file passes 50 MB it is renamed to
Agent-OS-Actions.<timestamp>.jsonl (never deleted -- Tony prunes archives himself).
Off switch: AGENT_OS_ACTION_LOG=off. Test/redirect: AGENT_OS_ACTION_LOG=/some/other/file.jsonl

Query it:
  python3 action_log.py who <path-or-text> [--since 2026-10-01] [--limit 50]
  python3 action_log.py session <session-id>
  python3 action_log.py check          # run the deletion sentinel now
  python3 action_log.py tail [N]
Tests: python3 -m unittest test_action_log  (from 001_Architecture/Scripts)
"""
from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

AGENT_OS = Path("/Users/tonymacbook2025/Documents/Agent-OS")
DEFAULT_LOG = Path.home() / "Library" / "Logs" / "Agent-OS-Actions.jsonl"
MAX_BYTES = 50 * 1024 * 1024
MAX_LINE = 3800
MAX_PATHS = 20
MAX_DELETED_LISTED = 200

# ---------------------------------------------------------------- where to write


def log_path() -> Path | None:
    v = os.environ.get("AGENT_OS_ACTION_LOG", "").strip()
    if v.lower() in ("off", "0", "false", "no"):
        return None
    return Path(v) if v else DEFAULT_LOG


def state_path(log: Path) -> Path:
    return log.with_name(log.stem + ".state.json")


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def parse_t(s: str) -> datetime | None:
    try:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S%z")
    except (TypeError, ValueError):
        return None


def _rotate_if_big(log: Path) -> None:
    limit = int(os.environ.get("AGENT_OS_ACTION_LOG_MAX_BYTES") or MAX_BYTES)
    try:
        if log.stat().st_size < limit:
            return
    except OSError:
        return
    # Unique name (second + nanoseconds + pid): os.rename silently overwrites an existing
    # target, so a reused name would lose an archive.
    archive = log.with_name(f"{log.stem}.{time.strftime('%Y-%m-%d_%H-%M-%S')}"
                            f"-{time.time_ns() % 10**9:09d}-{os.getpid()}{log.suffix}")
    if archive.exists():
        return
    try:
        os.rename(log, archive)  # a move, never a delete; a racing hook may already have moved it
    except OSError:
        pass


def _shrink(rec: dict) -> str:
    line = json.dumps(rec, ensure_ascii=False)
    for key, keep in (("command", 600), ("prompt", 600), ("args", 300), ("summary", 300),
                      ("command", 200), ("prompt", 200), ("args", 100), ("summary", 100)):
        if len(line.encode()) <= MAX_LINE:
            break
        if isinstance(rec.get(key), str) and len(rec[key]) > keep:
            rec[key] = rec[key][:keep] + " ...[cut]"
            line = json.dumps(rec, ensure_ascii=False)
    if len(line.encode()) > MAX_LINE and isinstance(rec.get("paths"), list):
        rec["paths"] = rec["paths"][:5] + [f"... +{len(rec['paths']) - 5} more"]
        line = json.dumps(rec, ensure_ascii=False)
    return line


def append(rec: dict) -> None:
    """Append one record. Never raises."""
    log = log_path()
    if log is None:
        return
    try:
        _rotate_if_big(log)
        line = _shrink({k: v for k, v in rec.items() if v not in (None, "", [], {})})
        with open(log, "a", encoding="utf-8") as fh:  # O_APPEND: whole-line writes stay atomic
            fh.write(line + "\n")
    except Exception:
        pass


# ---------------------------------------------------------------- attribution

ID_KEYS = {
    "session": ("session_id", "sessionId", "conversation_id", "conversationId", "cascadeId",
                "trajectoryId"),
    "transcript": ("transcript_path", "transcriptPath"),
    "agent_id": ("agent_id", "agentId"),
    "agent_type": ("agent_type", "agentType"),
    "turn": ("turn_id", "turnId"),
    "tool_use_id": ("tool_use_id", "toolUseId", "tool_call_id", "toolCallId"),
    "model": ("model",),
    "mode": ("permission_mode",),
}


def context(raw: object, harness: str) -> dict:
    """Who is acting: pulled from the raw hook payload of any harness."""
    ctx: dict = {"harness": harness}
    if isinstance(raw, dict):
        for out_key, keys in ID_KEYS.items():
            for k in keys:
                v = raw.get(k)
                if isinstance(v, (str, int)) and str(v):
                    ctx[out_key] = str(v)[:300]
                    break
        # Claude subagents share the parent's session id; their own instructions live here.
        if ctx.get("agent_id") and str(ctx.get("transcript", "")).endswith(".jsonl"):
            ctx["subagent_transcript"] = (ctx["transcript"][:-len(".jsonl")]
                                          + f"/subagents/agent-{ctx['agent_id']}.jsonl")
    if os.environ.get("AGENT_OS_DELEGATE_WORKER"):
        ctx["delegate_worker"] = True
    return ctx


# ---------------------------------------------------------------- what the tool call does

WRITE_TOOLS = {"Write", "write_file", "write_to_file", "create_file"}
EDIT_TOOLS = {"Edit", "MultiEdit", "NotebookEdit", "replace", "edit", "edit_file", "str_replace",
              "replace_file_content", "multi_replace_file_content", "str_replace_based_edit_tool"}
SHELL_TOOLS = {"Bash", "run_shell_command", "shell", "exec_command", "local_shell", "run_command",
               "unified_exec", "container.exec"}
AGENT_TOOLS = {"Agent", "Task", "spawn_agent"}
READ_TOOLS = {"Read", "Glob", "Grep", "LS", "WebFetch", "WebSearch", "TodoWrite", "ToolSearch",
              "read_file", "read_many_files", "glob", "search_file_content", "list_directory",
              "google_web_search", "web_fetch", "view_file", "list_dir", "grep_search",
              "find_by_name", "codebase_search", "view_image", "update_plan", "Skill"}
PATH_KEYS = ("file_path", "notebook_path", "path", "absolute_path", "TargetFile", "AbsolutePath",
             "filePath", "target_file")
READ_VERBS = re.compile(r"(^|_|__)(get|list|search|read|query|fetch|find|view|show|status|describe|"
                        r"inspect|lookup|count|check|download_url|preview)", re.I)
WRITE_VERBS = re.compile(r"(create|write|update|delete|remove|trash|patch|append|replace|move|rename|"
                         r"upload|post|send|publish|set|add|edit|manage|run|exec|deliver|schedule|"
                         r"generate|assign|share|pin)", re.I)


def _abs(p: str, cwd: str) -> str:
    p = os.path.expanduser(str(p))
    return os.path.normpath(p if os.path.isabs(p) else os.path.join(cwd or str(AGENT_OS), p))


def _cmd_text(cmd: object) -> str:
    if isinstance(cmd, list):
        return shlex.join(str(c) for c in cmd)
    return str(cmd or "")


def patch_ops(patch: str, cwd: str) -> list[str]:
    ops = []
    for line in patch.splitlines():
        m = re.match(r"^\*\*\* (Delete File|Add File|Update File|Move to): (.+?)\s*$", line)
        if m:
            verb = {"Delete File": "delete", "Add File": "add", "Update File": "update",
                    "Move to": "move-to"}[m.group(1)]
            ops.append(f"{verb} {_abs(m.group(2), cwd)}")
    return ops


READONLY_CMDS = {
    "ls", "cat", "head", "tail", "wc", "grep", "rg", "egrep", "fgrep", "find", "pwd", "echo",
    "printf", "which", "type", "whereis", "stat", "file", "du", "df", "date", "cal", "true",
    "false", "test", "[", "basename", "dirname", "realpath", "readlink", "sed", "sort", "uniq",
    "cut", "tr", "column", "jq", "diff", "cmp", "comm", "tree", "less", "more", "od", "xxd",
    "hexdump", "strings", "md5", "shasum", "sha256sum", "cd", "pushd", "popd", "printenv",
    "whoami", "id", "uname", "hostname", "ps", "lsof", "sw_vers", "sleep", "nl", "fold", "paste",
    "git", "mdfind", "mdls", "ffprobe", "env", "export", "set", "unset", "source", ".", "command",
}
GIT_READONLY = {"status", "log", "diff", "show", "rev-parse", "reflog", "ls-files", "ls-tree",
                "blame", "grep", "describe", "shortlog", "cat-file", "rev-list", "merge-base",
                "whatchanged", "--version", "version", "help"}
HARMLESS_REDIRECT = re.compile(r"(\d?>>?|&>)\s*/dev/null|\d>&\d")


def is_readonly_command(cmd: object) -> bool:
    """Conservative: True only when every segment is a known read-only command.
    Anything unknown, any output redirect, substitution or heredoc counts as state-changing."""
    text = _cmd_text(cmd)
    if not text.strip() or "$(" in text or "`" in text or "<<" in text or "<(" in text:
        return False
    text = HARMLESS_REDIRECT.sub(" ", text)
    if ">" in text:
        return False
    for seg in re.split(r"\|\||&&|[;|\n&]", text):
        try:
            toks = shlex.split(seg)
        except ValueError:
            return False
        while toks and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", toks[0]):
            toks = toks[1:]
        if toks and os.path.basename(toks[0]) == "xargs":
            toks = toks[1:]
            while toks and toks[0].startswith("-"):
                toks = toks[1:]
        if not toks:
            continue
        base, args = os.path.basename(toks[0]), toks[1:]
        if base not in READONLY_CMDS:
            return False
        if base == "find" and any(a in ("-delete", "-exec", "-execdir", "-ok", "-okdir", "-fprint",
                                        "-fprintf", "-fls") for a in args):
            return False
        if base == "sed" and any(a.startswith("-i") or a.startswith("--in-place") for a in args):
            return False
        if base == "sort" and any(a == "-o" or a.startswith("--output") for a in args):
            return False
        if base in ("env", "command") and [a for a in args if not a.startswith("-") and "=" not in a]:
            return False  # env/command running another program: not provably read-only
        if base == "git":
            rest = [a for a in args if not a.startswith("-")]
            opts = [a for a in args if a.startswith("-")]
            if "-C" in args:  # git -C <dir> <sub> ...
                i = args.index("-C")
                rest = [a for a in args[i + 2:] if not a.startswith("-")]
            sub = rest[0] if rest else ("--version" if "--version" in opts else "")
            if sub == "branch" and all(a in ("-a", "-v", "-vv", "-r", "--list", "--show-current")
                                       for a in args[1:]):
                continue
            if sub == "remote" and rest[1:2] in ([], ["-v"], ["show"]):
                continue
            if sub not in GIT_READONLY:
                return False
    return True


def describe_tool(tool: str, tin: object, cwd: str) -> dict | None:
    """What a tool call changes. None means read-only (not worth a paper-trail line)."""
    tin = tin if isinstance(tin, dict) else {"input": tin}
    paths = [_abs(tin[k], cwd) for k in PATH_KEYS if isinstance(tin.get(k), str) and tin.get(k)]
    if tool in WRITE_TOOLS:
        return {"action": "write", "paths": paths[:MAX_PATHS]}
    if tool in EDIT_TOOLS:
        return {"action": "edit", "paths": paths[:MAX_PATHS]}
    if tool == "apply_patch":
        patch = str(tin.get("command") or tin.get("input") or tin.get("patch") or "")
        ops = patch_ops(patch, cwd)
        return {"action": "patch", "paths": [o.split(" ", 1)[1] for o in ops][:MAX_PATHS],
                "summary": "; ".join(o.split(" ", 1)[0] + " " + os.path.basename(o.split(" ", 1)[1])
                                     for o in ops)[:600]}
    if tool in SHELL_TOOLS:
        cmd = tin.get("command") if "command" in tin else tin.get("cmd")
        if is_readonly_command(cmd):
            return None
        wd = tin.get("workdir") or tin.get("dir_path") or tin.get("cwd")
        rec = {"action": "shell", "command": _cmd_text(cmd)}
        if wd:
            rec["workdir"] = _abs(str(wd), cwd)
        return rec
    if tool in AGENT_TOOLS:
        desc = " | ".join(str(tin.get(k)) for k in ("subagent_type", "description") if tin.get(k))
        return {"action": "subagent", "summary": desc[:200],
                "prompt": str(tin.get("prompt") or tin.get("message") or "")[:600]}
    if tool in READ_TOOLS:
        return None
    is_mcp = tool.startswith("mcp") or "__" in tool
    if is_mcp and READ_VERBS.search(tool) and not WRITE_VERBS.search(tool.split("__")[-1]):
        return None
    try:
        args = json.dumps(tin, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        args = str(tin)
    return {"action": "mcp" if is_mcp else "other", "paths": paths[:MAX_PATHS], "args": args[:600]}


def record_tool(harness: str, raw: object, payload: dict, decision: str, reason: str = "") -> None:
    """Called by fs_guard.py for every hook call. Logs state-changing calls and every deny/ask.
    Never raises."""
    try:
        if log_path() is None or not isinstance(payload, dict):
            return
        tool = str(payload.get("tool_name") or "")
        cwd = str(payload.get("cwd") or os.getcwd())
        what = describe_tool(tool, payload.get("tool_input") or {}, cwd)
        if what is None and decision == "allow":
            return
        if what is None:  # a read-only-looking call that was still denied/asked: keep the detail
            what = describe_tool("other", payload.get("tool_input") or {}, cwd) or {}
            what["action"] = "blocked-call"
        rec = {"t": now_iso(), "event": "tool", **context(raw, harness), "cwd": cwd, "tool": tool,
               "decision": decision}
        rec.update(what)
        if reason:
            rec["reason"] = reason[:160]
        append(rec)
    except Exception:
        pass


# ---------------------------------------------------------------- the why: prompts

SECRET_PATTERNS = [
    re.compile(r"<private>.*?</private>", re.S | re.I),
    re.compile(r"\b(sk|pk|rk)-[A-Za-z0-9_\-]{16,}"),
    re.compile(r"\b(ghp|gho|ghs|github_pat|xox[abprs]|AKIA|AIza)[A-Za-z0-9_\-]{12,}"),
    re.compile(r"(?i)\b(bearer)\s+[A-Za-z0-9._\-]{16,}"),
    re.compile(r"(?i)\b([A-Z0-9_]*(KEY|TOKEN|SECRET|PASSWORD|PASS)[A-Z0-9_]*)\s*[=:]\s*\S+"),
]


def redact(text: str) -> str:
    for pat in SECRET_PATTERNS:
        text = pat.sub("[redacted]", text)
    return text


def record_prompt(harness: str, raw: object, prompt: str) -> None:
    """Called by jev_route.py on every prompt. Never raises."""
    try:
        text = (prompt or "").strip()
        if log_path() is None or not text:
            return
        rec = {"t": now_iso(), "event": "prompt", **context(raw, harness),
               "cwd": str(raw.get("cwd") or "") if isinstance(raw, dict) else "",
               "prompt": redact(text)[:800]}
        append(rec)
    except Exception:
        pass


# ---------------------------------------------------------------- deletion sentinel


def tracked_deletions(repo: Path = AGENT_OS, timeout: float = 3.0) -> list[str] | None:
    """Git-tracked paths currently missing (worktree or staged deletion). None if git failed."""
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), "status", "--porcelain", "-z", "-uno", "--no-renames"],
            capture_output=True, timeout=timeout,
            env=dict(os.environ, GIT_OPTIONAL_LOCKS="0"),  # never take index.lock from a hook
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    deleted = []
    for entry in out.stdout.decode("utf-8", "replace").split("\0"):
        if len(entry) > 3 and "D" in entry[:2]:
            deleted.append(entry[3:])
    return sorted(deleted)


def check_deletions(harness: str = "manual", raw: object = None, repo: Path = AGENT_OS) -> dict | None:
    """Compare tracked deletions with the last check; log what changed. Never raises.
    Returns the record written for new deletions (or None)."""
    try:
        log = log_path()
        if log is None:
            return None
        current = tracked_deletions(repo)
        if current is None:
            return None
        sp = state_path(log)
        try:
            prev = json.loads(sp.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            prev = None
        t = now_iso()
        written = None
        ctx = context(raw, harness)
        if prev is None:
            if current:
                written = {"t": t, "event": "deletion_detected", **ctx, "window_start": None,
                           "count": len(current), "paths": current[:MAX_DELETED_LISTED],
                           "note": "baseline: already missing at the first sentinel check; when they "
                                   "went missing is unknown"}
                append(written)
        else:
            before = set(prev.get("deleted") or [])
            new = sorted(set(current) - before)
            gone = sorted(before - set(current))
            if new:
                written = {"t": t, "event": "deletion_detected", **ctx,
                           "window_start": prev.get("t"), "count": len(new),
                           "paths": new[:MAX_DELETED_LISTED],
                           "note": "git-tracked file(s) went missing between window_start and t; "
                                   "match against event=tool lines in that window to find who"}
                append(written)
            if gone:
                append({"t": t, "event": "deletion_cleared", **ctx, "window_start": prev.get("t"),
                        "count": len(gone), "paths": gone[:MAX_DELETED_LISTED],
                        "note": "back on disk, or the deletion was committed"})
        tmp = sp.with_name(sp.name + ".tmp")
        tmp.write_text(json.dumps({"t": t, "deleted": current}), encoding="utf-8")
        os.replace(tmp, sp)
        return written
    except Exception:
        return None


# ---------------------------------------------------------------- query CLI


def _log_files(log: Path) -> list[Path]:
    archives = sorted(log.parent.glob(f"{log.stem}.20*{log.suffix}"))
    return archives + ([log] if log.exists() else [])


def _records(log: Path):
    for f in _log_files(log):
        try:
            with open(f, encoding="utf-8") as fh:
                for line in fh:
                    try:
                        r = json.loads(line)
                    except ValueError:
                        continue
                    if isinstance(r, dict):
                        yield r
        except OSError:
            continue


def _mentions(r: dict, needle: str) -> bool:
    if any(needle in str(p) for p in r.get("paths") or []):
        return True
    return any(needle in str(r.get(k) or "") for k in ("command", "args", "summary", "workdir"))


def _fmt(r: dict) -> str:
    who = " ".join(f"{k}={r[k]}" for k in ("session", "agent_type", "agent_id", "turn", "model")
                   if r.get(k))
    head = f"{r.get('t')}  {r.get('harness', '?'):<11} {r.get('event')}"
    if r.get("event") == "tool":
        head += f"  {r.get('tool')} [{r.get('action')}] {str(r.get('decision', '')).upper()}"
    if r.get("delegate_worker"):
        head += "  (delegate.py worker)"
    lines = [head]
    if who:
        lines.append(f"    who: {who}")
    for k in ("paths", "command", "summary", "args", "reason", "note", "window_start"):
        if r.get(k):
            v = r[k]
            if isinstance(v, list):
                v = ", ".join(map(str, v[:8])) + (f" ... +{len(v) - 8}" if len(v) > 8 else "")
            lines.append(f"    {k}: {str(v)[:400]}")
    return "\n".join(lines)


def who(needle: str, since: str | None = None, limit: int = 50, log: Path | None = None) -> str:
    log = log or log_path() or DEFAULT_LOG
    since_dt = datetime.fromisoformat(since).astimezone() if since else None
    last_prompt: dict[str, dict] = {}
    last_launch: dict[tuple[str, str], dict] = {}  # (session, agent_type) -> latest subagent launch
    agent_why: dict[str, tuple[dict | None, dict | None]] = {}  # frozen at the subagent's first action
    tool_lines: list[dict] = []
    hits: list[tuple[dict, dict | None, dict | None]] = []
    for r in _records(log):
        rt = parse_t(r.get("t", ""))
        sess = r.get("session", "")
        if r.get("event") == "prompt" and sess:
            last_prompt[sess] = r
            continue
        if r.get("event") == "tool" and r.get("action") == "subagent":
            last_launch[(sess, str(r.get("summary", "")).split(" | ")[0])] = r
        aid = r.get("agent_id")
        if aid and aid not in agent_why:
            # A subagent shares its parent's session; the parent may get newer prompts while it runs,
            # so its "why" is the parent prompt (and launch) in force when it first acted.
            agent_why[aid] = (last_prompt.get(sess), last_launch.get((sess, r.get("agent_type", ""))))
        if since_dt and rt and rt < since_dt:
            continue
        if r.get("event") == "tool":
            tool_lines.append(r)
        if _mentions(r, needle):
            if r.get("event") != "tool":
                hits.append((r, None, None))
            elif aid:
                hits.append((r, *agent_why[aid]))
            else:
                hits.append((r, last_prompt.get(sess), None))
    out = []
    for r, why, launch in hits[-limit:]:
        out.append(_fmt(r))
        if launch:
            out.append(f"    launched as subagent ({launch.get('t')}): {launch.get('summary', '')} -- "
                       f"{launch.get('prompt', '')[:300]}")
        if r.get("agent_id"):
            out.append(f"    subagent's own instructions: {r.get('subagent_transcript') or 'see its transcript'}")
        if why:
            label = "parent prompt when this subagent started" if r.get("agent_id") else "last prompt in this session"
            out.append(f"    why ({label}, {why.get('t')}): {why.get('prompt', '')[:300]}")
        if r.get("event") == "deletion_detected":
            start, end = parse_t(r.get("window_start") or ""), parse_t(r.get("t", ""))
            suspects = [x for x in tool_lines
                        if (pt := parse_t(x.get("t", ""))) and end and pt <= end
                        and (start is None or pt >= start) and _mentions(x, needle)]
            if suspects:
                out.append(f"    tool calls in that window mentioning '{needle}': {len(suspects)} (listed above)")
            else:
                out.append("    NO logged agent tool call mentioned this path in that window -> it was removed "
                           "outside any agent tool call (harness housekeeping, a script's internals, or Tony)")
        out.append("")
    if not out:
        return f"No action-log entries mention '{needle}' (log: {log})."
    return "\n".join(out)


def session_trail(session: str, log: Path | None = None) -> str:
    log = log or log_path() or DEFAULT_LOG
    rows = [_fmt(r) + (f"\n    prompt: {r.get('prompt', '')[:400]}" if r.get("event") == "prompt" else "")
            for r in _records(log) if r.get("session") == session]
    return "\n".join(rows) or f"No entries for session {session}."


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd, rest = argv[0], argv[1:]
    if cmd == "who" and rest:
        since = rest[rest.index("--since") + 1] if "--since" in rest else None
        limit = int(rest[rest.index("--limit") + 1]) if "--limit" in rest else 50
        print(who(rest[0], since, limit))
        return 0
    if cmd == "session" and rest:
        print(session_trail(rest[0]))
        return 0
    if cmd == "check":
        r = check_deletions("manual")
        print(json.dumps(r, indent=1) if r else "No new tracked-file deletions since the last check.")
        return 0
    if cmd == "tail":
        n = int(rest[0]) if rest else 20
        log = log_path() or DEFAULT_LOG
        recs = list(_records(log))[-n:]
        print("\n".join(_fmt(r) for r in recs) or "(empty)")
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
