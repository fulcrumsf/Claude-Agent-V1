#!/usr/bin/env python3
"""Agent-OS filesystem guard — one pre-tool hook shared by Claude Code, Codex and Gemini CLI.

Rules (Tony, 2026-09-27):
  1. No agent deletes files or folders. Tony deletes. Hard block, no override.
     Only exception: scratch/temp locations (/tmp, /private/tmp, /var/folders).
  2. No agent creates a new folder inside Agent-OS on its own. It must place work in
     an existing folder per the directory guides, or ask Tony. Claude Code shows Tony
     a permission prompt; Codex and Gemini are blocked and must ask in chat.

Wired in:
  Claude Code  ~/.claude/settings.json   PreToolUse   python3 fs_guard.py --harness claude
  Codex        ~/.codex/hooks.json       PreToolUse   python3 fs_guard.py --harness codex
  Gemini CLI   ~/.gemini/settings.json   BeforeTool   python3 fs_guard.py --harness gemini

Protocol: reads the hook JSON on stdin. Block = reason on stderr + exit 2 (all three
harnesses honor this). Claude "ask" = permissionDecision JSON on stdout + exit 0.
Known gaps: scripts run from files (python3 foo.py) are not inspected; Codex apply_patch
file deletions are not hookable. Test: python3 fs_guard.py --self-test

Paper trail (2026-10-06): every call is also handed to action_log.record_tool(), which
writes state-changing calls and every deny/ask (with target, session, subagent) to
~/Library/Logs/Agent-OS-Actions.jsonl. Purely additive: it cannot change a verdict, and if
action_log.py is missing or fails, the guard behaves exactly as before.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import sys
import time
from pathlib import Path

try:  # paper-trail logger; optional, the guard never depends on it
    import action_log
except Exception:  # pragma: no cover
    action_log = None

AGENT_OS = Path("/Users/tonymacbook2025/Documents/Agent-OS")
TEMP_PREFIXES = ("/tmp/", "/private/tmp/", "/var/folders/", "/private/var/folders/")
LOG = Path.home() / "Library" / "Logs" / "Agent-OS-Guard.jsonl"

# Folder names any agent may create without asking (backup/version conventions + tooling caches).
ALLOWED_NEW_DIR_NAMES = re.compile(
    r"^(Archived|Rejected|__pycache__|node_modules|graphify-out|v\d+(\.\d+)*[a-z]?)$"
)

DELETE_CMDS = {"rm", "rmdir", "unlink", "trash", "rmtrash", "srm", "shred"}
SHELLS = {"bash", "sh", "zsh", "dash", "fish"}
INTERPRETERS = {"python", "python3", "node", "perl", "ruby", "bun", "deno"}
PREFIX_CMDS = {"sudo", "command", "builtin", "exec", "nohup", "time", "nice", "caffeinate"}
CODE_DELETE = re.compile(
    r"(shutil\.rmtree|os\.(remove|unlink|rmdir|removedirs)|\.unlink|\.rmdir|"
    r"\bfs(\.promises)?\.(rm|rmSync|unlink|unlinkSync|rmdir|rmdirSync)|\.(rm|rmSync|unlinkSync|rmdirSync)|"
    r"rimraf|\bunlink|send2trash)\s*\("
)
MCP_DELETE_TOOL = re.compile(r"(delete|remove|trash)_?(note|file|files|dir|directory|folder|path)", re.I)

DELETE_MSG = (
    "BLOCKED by Agent-OS guard: agents may not delete files or folders (Tony's rule, all harnesses). "
    "Tony does all deleting himself. Do not retry another way. Tell Tony exactly what you wanted to delete "
    "and why, and let him do it. To retire a file, move it into a sibling Archived/ or Rejected/ folder instead."
)


def folder_msg(path: str) -> str:
    return (
        f"Agent-OS guard: '{path}' would be a NEW folder. Agents do not create folders on their own. "
        "Read 001_Architecture/Directory.md and the nearest Directory.md, and put the work in an existing "
        "folder. If none fits, ask Tony where it goes or whether he approves a new folder."
    )


class Verdict(Exception):
    def __init__(self, kind: str, reason: str):
        self.kind, self.reason = kind, reason  # kind: "deny" | "ask"


def resolve(p: str, cwd: str) -> str:
    p = os.path.expanduser(os.path.expandvars(p))
    return os.path.normpath(p if os.path.isabs(p) else os.path.join(cwd, p))


def is_temp(path: str) -> bool:
    return (path.rstrip("/") + "/").startswith(TEMP_PREFIXES) and "$" not in path


def new_dir_verdict(path: str) -> Verdict | None:
    """Return a verdict if creating `path` (a directory) would add an unapproved folder in Agent-OS."""
    p = Path(path)
    try:
        rel = p.relative_to(AGENT_OS)
    except ValueError:
        return None
    parts = rel.parts
    # First component that does not exist yet = the folder actually being created.
    for i in range(1, len(parts) + 1):
        candidate = AGENT_OS.joinpath(*parts[:i])
        if candidate.exists():
            continue
        name = parts[i - 1]
        if name.startswith(".") or ALLOWED_NEW_DIR_NAMES.match(name):
            continue
        if parts[0] == "000_Ingest":
            continue
        if parts[0] == "007_Resource_Library" and i == 3:  # new item folder inside an existing library folder
            continue
        return Verdict("ask", folder_msg(str(candidate)))
    return None


def split_segments(command: str) -> list[list[str]]:
    text = command.replace("`", " ; ").replace("\n", " ; ")
    try:
        lex = shlex.shlex(text, posix=True, punctuation_chars=";&|()")
        lex.whitespace_split = True
        tokens = list(lex)
    except ValueError:
        tokens = text.split()
    segments, cur = [], []
    for t in tokens:
        if t and set(t) <= set(";&|()"):
            if cur:
                segments.append(cur)
            cur = []
        else:
            cur.append(t)
    if cur:
        segments.append(cur)
    return segments


def strip_prefix(argv: list[str]) -> list[str]:
    i = 0
    while i < len(argv):
        tok = argv[i]
        base = os.path.basename(tok)
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tok):
            i += 1
        elif base in PREFIX_CMDS:
            i += 1
        elif base == "env":
            i += 1
            while i < len(argv) and (argv[i].startswith("-") or "=" in argv[i]):
                i += 1
        elif base == "xargs":
            i += 1
            while i < len(argv) and argv[i].startswith("-"):
                i += 1
        else:
            break
    return argv[i:]


HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")


def split_heredocs(command: str) -> tuple[str, list[tuple[str, str]]]:
    """Separate heredoc bodies from the command. Returns (command without bodies, [(consumer, body)])."""
    lines, out, bodies, i = command.split("\n"), [], [], 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        m = HEREDOC.search(line)
        i += 1
        if m:
            delim, body = m.group(2), []
            while i < len(lines) and lines[i].strip() != delim:
                body.append(lines[i])
                i += 1
            i += 1  # skip the delimiter line
            argv = strip_prefix(line[: m.start()].split())
            bodies.append((os.path.basename(argv[0]) if argv else "", "\n".join(body)))
    return "\n".join(out), bodies


def check_command(command: str, cwd: str, depth: int = 0) -> None:
    if depth > 3:
        return
    command, bodies = split_heredocs(command)
    for consumer, body in bodies:
        if consumer in SHELLS:
            check_command(body, cwd, depth + 1)
        elif re.sub(r"[\d.]+$", "", consumer) in INTERPRETERS and CODE_DELETE.search(body):
            raise Verdict("deny", DELETE_MSG)
        # Anything else (cat, tee, >> file) is data being written, not run.
    for seg in split_segments(command):
        argv = strip_prefix(seg)
        if not argv:
            continue
        cmd = os.path.basename(argv[0])
        args = argv[1:]
        operands = [a for a in args if not a.startswith("-")]

        if cmd in DELETE_CMDS:
            targets = [resolve(a, cwd) for a in operands] or ["?"]
            if not all(is_temp(t) for t in targets):
                raise Verdict("deny", DELETE_MSG)
        elif cmd == "find" and ("-delete" in args or any(
                a in ("-exec", "-execdir", "-ok") and i + 1 < len(args)
                and os.path.basename(args[i + 1]) in DELETE_CMDS for i, a in enumerate(args))):
            roots = [resolve(a, cwd) for a in args[: next((i for i, a in enumerate(args) if a.startswith("-")), len(args))]]
            if not roots or not all(is_temp(r) for r in roots):
                raise Verdict("deny", DELETE_MSG)
        elif cmd == "git" and operands[:1] == ["clean"]:
            raise Verdict("deny", DELETE_MSG)
        elif cmd == "git" and operands[:1] == ["rm"] and "--cached" not in args:
            raise Verdict("deny", DELETE_MSG)
        elif cmd == "rsync" and any(a.startswith(("--delete", "--remove-source-files")) for a in args):
            raise Verdict("deny", DELETE_MSG)
        elif cmd == "osascript" and re.search(r"\bdelete\b", " ".join(args), re.I):
            raise Verdict("deny", DELETE_MSG)
        elif cmd in ("mv", "cp") and any(".Trash" in a for a in args):
            raise Verdict("deny", DELETE_MSG)
        elif cmd in SHELLS:
            for i, a in enumerate(args):
                if re.fullmatch(r"-[a-z]*c[a-z]*", a) and i + 1 < len(args):
                    check_command(args[i + 1], cwd, depth + 1)
                    break
        elif re.sub(r"[\d.]+$", "", cmd) in INTERPRETERS:
            if CODE_DELETE.search(" ".join(args)):
                raise Verdict("deny", DELETE_MSG)

        if cmd == "mkdir":
            for a in operands:
                v = new_dir_verdict(resolve(a, cwd))
                if v:
                    raise v
        elif cmd in ("mv", "cp") and len(operands) >= 2:
            srcs, dest = operands[:-1], resolve(operands[-1], cwd)
            if not os.path.exists(dest) and any(os.path.isdir(resolve(s, cwd)) for s in srcs):
                v = new_dir_verdict(dest)
                if v:
                    raise v


def check_patch(patch: str, cwd: str) -> None:
    """Codex apply_patch: block file deletions, check folders that added/moved files would create."""
    for line in patch.splitlines():
        m = re.match(r"^\*\*\* (Delete File|Add File|Move to): (.+?)\s*$", line)
        if not m:
            continue
        if m.group(1) == "Delete File":
            raise Verdict("deny", DELETE_MSG)
        v = new_dir_verdict(os.path.dirname(resolve(m.group(2), cwd)))
        if v:
            raise v


def normalize_antigravity(payload) -> dict:
    """Map an Antigravity PreToolUse payload onto the shape evaluate() expects.
    A malformed payload (payload, toolCall or args not an object) means nothing to check."""
    if not isinstance(payload, dict):
        return {}
    call = payload.get("toolCall")
    if not isinstance(call, dict):
        return {}
    name, args = str(call.get("name") or ""), call.get("args")
    if not isinstance(args, dict):
        return {}
    ws = payload.get("workspacePaths")
    cwd = str(args.get("Cwd") or (ws[0] if isinstance(ws, list) and ws else str(AGENT_OS)))
    if name == "run_command":
        return {"tool_name": "Bash", "tool_input": {"command": args.get("CommandLine", "")}, "cwd": cwd}
    if name == "write_to_file":
        return {"tool_name": "Write", "tool_input": {"file_path": args.get("TargetFile", "")}, "cwd": cwd}
    return {"tool_name": name, "tool_input": args, "cwd": cwd}


def evaluate(payload: dict) -> Verdict | None:
    tool = str(payload.get("tool_name") or "")
    tin = payload.get("tool_input") or {}
    cwd = str(payload.get("cwd") or os.getcwd())
    try:
        if MCP_DELETE_TOOL.search(tool):
            raise Verdict("deny", DELETE_MSG)
        if tool == "apply_patch":
            check_patch(str(tin.get("command") or tin.get("input") or "") if isinstance(tin, dict) else str(tin), cwd)
            return None
        cmd = tin.get("command") if isinstance(tin, dict) else None
        if isinstance(cmd, list):
            cmd = shlex.join(str(c) for c in cmd)
        if cmd:
            check_command(str(cmd), str(tin.get("workdir") or tin.get("dir_path") or cwd))
        path = None
        if isinstance(tin, dict) and tool in ("Write", "write_file", "NotebookEdit"):
            path = tin.get("file_path") or tin.get("absolute_path") or tin.get("path")
        if path:
            v = new_dir_verdict(os.path.dirname(resolve(str(path), cwd)))
            if v:
                raise v
    except Verdict as v:
        return v
    return None


def log(harness: str, tool_name: object, decision: str) -> None:
    """Append one line per hook call. Deny/ask are always logged (rare, worth a
    permanent audit trail). Plain allows are logged only for antigravity, whose
    real hook wiring hadn't been verified yet (2026-09-27) -- Claude Code fires
    this hook on nearly every Bash/Write, so logging every allow there would
    flood the file during normal use."""
    if decision == "allow" and harness != "antigravity":
        return
    try:
        with open(LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"t": time.strftime("%Y-%m-%dT%H:%M:%S"), "harness": harness,
                                 "tool": tool_name if isinstance(tool_name, str) else None,
                                 "decision": decision}) + "\n")
    except OSError:
        pass


def trail(harness: str, raw: object, payload: dict, v: Verdict | None) -> None:
    """Hand the call to the paper-trail logger. Can never raise or change the verdict."""
    if action_log is None:
        return
    try:
        action_log.record_tool(harness, raw, payload, v.kind if v else "allow", v.reason if v else "")
    except Exception:
        pass


def main() -> int:
    harness =sys.argv[sys.argv.index("--harness") + 1] if "--harness" in sys.argv else "claude"
    try:
        payload = json.load(sys.stdin)
    except Exception:
        log(harness, None, "parse_error")
        return 0
    raw = payload
    if harness == "antigravity":
        payload = normalize_antigravity(payload)
    if not isinstance(payload, dict):
        log(harness, None, "malformed_payload")
        return 0
    tool_name = payload.get("tool_name")
    v = evaluate(payload)
    trail(harness, raw, payload, v)
    if v is None:
        log(harness, tool_name, "allow")
        return 0
    if harness == "antigravity":
        log(harness, tool_name, v.kind)
        print(json.dumps({"decision": v.kind, "reason": v.reason}))
        return 0
    if v.kind == "ask" and harness == "claude":
        log(harness, tool_name, "ask")
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse", "permissionDecision": "ask",
            "permissionDecisionReason": v.reason}}))
        return 0
    log(harness, tool_name, "deny")
    print(v.reason, file=sys.stderr)
    return 2


def self_test() -> int:
    AO = str(AGENT_OS)
    cases = [
        # (tool, input, cwd, expected)
        ("Bash", {"command": "rm -rf 000_Wiki"}, AO, "deny"),
        ("Bash", {"command": "rm notes.md"}, AO, "deny"),
        ("Bash", {"command": "cd x && rm -rf ../y"}, AO, "deny"),
        ("Bash", {"command": "sudo rm -r /Users/tonymacbook2025/Desktop/a"}, AO, "deny"),
        ("Bash", {"command": "rmdir Empty"}, AO, "deny"),
        ("Bash", {"command": "find . -name '*.png' -delete"}, AO, "deny"),
        ("Bash", {"command": "find . -type d -exec rm -rf {} +"}, AO, "deny"),
        ("Bash", {"command": "ls | xargs rm"}, AO, "deny"),
        ("Bash", {"command": "git clean -fd"}, AO, "deny"),
        ("Bash", {"command": "git rm old.md"}, AO, "deny"),
        ("Bash", {"command": "rsync -a --delete a/ b/"}, AO, "deny"),
        ("Bash", {"command": "bash -c 'rm -rf Scene_01'"}, AO, "deny"),
        ("Bash", {"command": ["/bin/zsh", "-lc", "rm -rf graphify-out"]}, AO, "deny"),
        ("Bash", {"command": "python3 -c 'import shutil; shutil.rmtree(\"x\")'"}, AO, "deny"),
        ("Bash", {"command": "python3 - <<'EOF'\nimport os\nos.remove('a.txt')\nEOF"}, AO, "deny"),
        ("Bash", {"command": "node -e \"require('fs').rmSync('x',{recursive:true})\""}, AO, "deny"),
        ("Bash", {"command": "echo hi\nrm -rf Video_Clips"}, AO, "deny"),
        ("Bash", {"command": "mv Old ~/.Trash/"}, AO, "deny"),
        ("Bash", {"command": "echo $(rm -rf x)"}, AO, "deny"),
        ("mcp__obsidian-mcp-server__obsidian_delete_note", {"path": "a.md"}, AO, "deny"),
        ("run_shell_command", {"command": "rm -rf 002_Content-Creation"}, AO, "deny"),
        ("Bash", {"command": "bash <<'EOF'\nrm -rf Scene_02\nEOF"}, AO, "deny"),
        ("Bash", {"command": "cat >> log.md <<'EOF'\nretired the `rm -rf graphify-out` step\nEOF"}, AO, None),
        ("Bash", {"command": "python3 - <<'EOF'\nprint('shutil.rmtree is banned')\nEOF"}, AO, None),
        ("apply_patch", {"command": "*** Begin Patch\n*** Delete File: 000_Wiki/log.md\n*** End Patch"}, AO, "deny"),
        ("apply_patch", {"command": "*** Begin Patch\n*** Add File: 001_Architecture/New_Place/a.md\n+hi\n*** End Patch"}, AO, "ask"),
        ("apply_patch", {"command": "*** Begin Patch\n*** Update File: TOOLBOX.md\n@@\n-old\n+rm -rf x is banned\n*** End Patch"}, AO, None),
        ("apply_patch", {"command": "*** Begin Patch\n*** Add File: 001_Architecture/Scripts/new_tool.py\n+import shutil\n+shutil.rmtree('x')\n*** End Patch"}, AO, None),
        ("Bash", {"command": "rm -rf /tmp/claude-501/scratch/x"}, AO, None),
        ("Bash", {"command": "rm /private/tmp/a.json /tmp/b.json"}, AO, None),
        ("Bash", {"command": "ls -la && git status && grep -rn 'rm -rf' ."}, AO, None),
        ("Bash", {"command": "git rm --cached big.mp4"}, AO, None),
        ("Bash", {"command": "grep -rn 'shutil.rmtree' 001_Architecture"}, AO, None),
        ("Bash", {"command": "mkdir 001_Architecture/Handoffs_New"}, AO, "ask"),
        ("Bash", {"command": "mkdir -p 002_Content-Creation/New_Dept/Sub"}, AO, "ask"),
        ("Bash", {"command": "mkdir -p 001_Architecture/Scripts/Archived"}, AO, None),
        ("Bash", {"command": "mkdir -p 001_Architecture/Scripts/v3"}, AO, None),
        ("Bash", {"command": "mkdir -p 000_Ingest/batch_7"}, AO, None),
        ("Bash", {"command": "mkdir -p 007_Resource_Library/Tutorials/New-Tutorial"}, AO, None),
        ("Bash", {"command": "mkdir /tmp/claude-501/work"}, AO, None),
        ("Bash", {"command": "mv 001_Architecture/Plans 001_Architecture/Plans_Renamed"}, AO, "ask"),
        ("Write", {"file_path": AO + "/001_Architecture/Brand_New/Note.md", "content": ""}, AO, "ask"),
        ("Write", {"file_path": AO + "/001_Architecture/Directory.md", "content": ""}, AO, None),
        ("Write", {"file_path": "/tmp/claude-501/x/y.md", "content": ""}, AO, None),
        ("write_file", {"file_path": AO + "/Brand_New_Top/x.md"}, AO, "ask"),
        ("antigravity", {"toolCall": {"name": "run_command", "args": {"CommandLine": "rm -rf 000_Wiki", "Cwd": AO}}}, AO, "deny"),
        ("antigravity", {"toolCall": {"name": "write_to_file", "args": {"TargetFile": AO + "/Brand_New_Ag/x.md"}}}, AO, "ask"),
        ("antigravity", {"toolCall": {"name": "run_command", "args": {"CommandLine": "ls -la", "Cwd": AO}}}, AO, None),
        ("antigravity", {"toolCall": "not-an-object"}, AO, None),
    ]
    failures = 0
    for tool, tin, cwd, expected in cases:
        payload = {"tool_name": tool, "tool_input": tin, "cwd": cwd}
        if tool == "antigravity":
            payload = normalize_antigravity(dict(tin, workspacePaths=[cwd]))
        v = evaluate(payload)
        got = v.kind if v else None
        ok = got == expected
        failures += not ok
        print(f"{'PASS' if ok else 'FAIL'}  expected={expected!s:5} got={got!s:5}  {tool}: {str(tin)[:90]}")
    print(f"\n{len(cases) - failures}/{len(cases)} passed")
    return 1 if failures + trail_self_test() else 0


def trail_self_test() -> int:
    """Paper-trail cases: what fs_guard hands action_log ends up in the log (synthetic payloads,
    written to a temp file, never the real log). Returns the failure count."""
    import tempfile
    if action_log is None:
        print("FAIL  paper trail: action_log.py could not be imported")
        return 1
    AO = str(AGENT_OS)
    cases = [
        # (harness, raw payload, expect a line?, expected fields)
        ("claude", {"tool_name": "Write", "tool_input": {"file_path": AO + "/TOOLBOX.md"}, "cwd": AO,
                    "session_id": "s1", "agent_id": "a1", "agent_type": "opus-standard"},
         True, {"action": "write", "decision": "allow", "session": "s1", "agent_type": "opus-standard"}),
        ("claude", {"tool_name": "Bash", "tool_input": {"command": "rm -rf 000_Wiki"}, "cwd": AO,
                    "session_id": "s2"}, True, {"action": "shell", "decision": "deny", "command": "rm -rf 000_Wiki"}),
        ("claude", {"tool_name": "Bash", "tool_input": {"command": "git status && ls -la"}, "cwd": AO},
         False, {}),
        ("codex", {"tool_name": "apply_patch", "tool_input": {"command": "*** Begin Patch\n*** Update File: "
                   "TOOLBOX.md\n@@\n-a\n+b\n*** End Patch"}, "cwd": AO, "session_id": "c1", "turn_id": "t9",
                   "model": "gpt-x"}, True, {"action": "patch", "paths": [AO + "/TOOLBOX.md"], "turn": "t9"}),
        ("antigravity", {"toolCall": {"name": "write_to_file", "args": {"TargetFile": AO + "/Brand_New_Ag/x.md"}},
                         "workspacePaths": [AO], "conversationId": "g1"}, True,
         {"action": "write", "decision": "ask", "session": "g1"}),
        ("claude", {"tool_name": "Read", "tool_input": {"file_path": AO + "/TOOLBOX.md"}, "cwd": AO}, False, {}),
    ]
    failures = 0
    td = tempfile.mkdtemp(prefix="fs_guard_trail_")  # left for the OS to clear: no deletes, even in tests
    logf = os.path.join(td, "actions.jsonl")
    old = os.environ.get("AGENT_OS_ACTION_LOG")
    os.environ["AGENT_OS_ACTION_LOG"] = logf
    try:
        for harness, raw, expect_line, fields in cases:
            before = open(logf).read().count("\n") if os.path.exists(logf) else 0
            payload = normalize_antigravity(raw) if harness == "antigravity" else raw
            trail(harness, raw, payload, evaluate(payload))
            lines = open(logf).read().splitlines() if os.path.exists(logf) else []
            got_line = len(lines) > before
            rec = json.loads(lines[-1]) if got_line else {}
            ok = got_line == expect_line and all(rec.get(k) == v for k, v in fields.items())
            failures += not ok
            print(f"{'PASS' if ok else 'FAIL'}  trail {harness}:{payload.get('tool_name')} "
                  f"logged={got_line} {({k: rec.get(k) for k in fields} if fields else '')}")
    finally:
        if old is None:
            os.environ.pop("AGENT_OS_ACTION_LOG", None)
        else:
            os.environ["AGENT_OS_ACTION_LOG"] = old
    print(f"\npaper trail: {len(cases) - failures}/{len(cases)} passed")
    return failures


if __name__ == "__main__":
    sys.exit(self_test() if "--self-test" in sys.argv else main())
