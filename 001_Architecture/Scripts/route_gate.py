#!/usr/bin/env python3
"""Agent-OS route gate: turns the Jev frontier hint into enforcement (Tony, 2026-09-27).

Why this exists: on 2026-09-27 the Sonnet controller received the router's "delegate this
now" hint twice and answered inline both times. A hint is advice; this module is the
enforcement layer. Plan: 001_Architecture/Plans/Frontier_Enforcement_Plan.md

How it works:
  jev_route.py (the prompt hook) calls arm_turn() with a level per session:
    "enforce" -> frontier work, confident, and Tony asked for real work now
    "advise"  -> soft hint only, never gated
  This script then runs as more hooks in the same session:
    pretool       (Claude, Codex, Antigravity) until a frontier agent is delegated, deny
                  work tools; allow READ_BUDGET quick reads to prepare the handoff
    stop          (Claude, Codex, Antigravity) block ending an undelegated enforced turn once
    subagent-start / subagent-stop  (Codex) record sol-standard / sol-deep starting
    before-model  (Gemini CLI) switch the model to Pro for the whole enforced turn
Never gated: calls from inside a subagent, the delegated worker (AGENT_OS_DELEGATE_WORKER),
anything once the turn is delegated, stale turns, and everything when ~/.agent_os_router_off
exists. Fails open: any error means no output, exit 0, the tool call goes ahead.
Audit log: ~/Library/Logs/Agent-OS-Route-Gate.jsonl (denials, delegations, stop blocks,
stop violations, model swaps; plain allows are not logged).
Test: python3 route_gate.py --self-test
"""
from __future__ import annotations

import fcntl
import json
import os
import re
import shlex
import sys
import time
from contextlib import contextmanager
from pathlib import Path

STATE = Path.home() / "Library" / "Caches" / "Agent-OS-Router-State.json"
LOG = Path.home() / "Library" / "Logs" / "Agent-OS-Route-Gate.jsonl"
OFF_SWITCH = Path.home() / ".agent_os_router_off"
MARKER = "[Agent-OS router]"  # prefix of every message this module sends; jev_route skips prompts starting with it
TURN_TTL = 3600  # seconds; an enforced turn older than this no longer gates anything
MAX_SESSIONS = 200
READ_BUDGET = 4  # quick read-only calls allowed before delegating, to gather file paths for the handoff
STOP_BLOCKS = 1  # times an undelegated enforced turn is kept from ending; then it may stop (logged)
QUESTION_MAX = 400  # a short reply ending in "?" is a clarifying question and may end the turn
FRONTIER_PY = "/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/frontier.py"
GEMINI_FRONTIER_MODEL = "pro"  # Gemini CLI alias; resolveModel() picks the best Pro the account can use

FRONTIER_AGENTS = {"claude": {"opus-standard", "opus-deep"}, "codex": {"sol-standard", "sol-deep"}}
READONLY_AGENTS = {"Explore", "claude-code-guide"}  # cheap read-only subagents: count as one read

CLAUDE_ALWAYS = {"AskUserQuestion", "TodoWrite", "ToolSearch", "TaskList", "TaskGet", "TaskOutput",
                 "TaskStop", "EnterPlanMode", "ExitPlanMode", "Monitor", "SubagentHandback"}
CLAUDE_READ = {"Read", "Grep", "Glob", "LS", "NotebookRead", "WebFetch", "WebSearch"}
AG_READ = {"view_file", "list_dir", "grep_search", "find_by_name", "codebase_search", "view_file_outline",
           "view_code_item", "read_url_content", "search_web"}
AG_WORK = {"write_to_file", "replace_file_content", "multi_replace_file_content"}
READISH_TOOL = re.compile(r"(read|get|list|search|query|fetch|find|view|status)", re.I)
WRITEISH_TOOL = re.compile(r"(write|create|update|delete|remove|patch|append|replace|send|post|publish|"
                           r"upload|move|rename|edit|set|run|exec|generate|trash)", re.I)
READONLY_CMDS = {"ls", "cat", "head", "tail", "grep", "rg", "wc", "pwd", "file", "stat", "tree", "jq",
                 "which", "echo", "find", "sed", "awk", "cd", "du", "sort", "uniq", "cut", "less", "true"}
READONLY_GIT = {"status", "log", "diff", "show", "branch", "rev-parse", "ls-files", "blame", "grep"}

DELEGATE_HOW = {
    "claude": ("Your next action must be the Agent tool with subagent_type \"opus-standard\" (or \"opus-deep\" for "
               "architecture, multi-file builds, or bugs that resisted earlier attempts)"),
    "codex": ("Spawn the custom agent named `sol-standard` now (or `sol-deep` for architecture, multi-file builds, or "
              "stubborn bugs)"),
    "antigravity": (f"Run this with run_command: python3 {FRONTIER_PY} \"<task>\" (add --deep for architecture, "
                    "multi-file builds, or stubborn bugs). It runs a frontier model and can take several minutes"),
}
HANDOFF = ("Hand over Tony's full request, the file paths you know, what was already tried, and the exact output you "
           "need back. After it reports, check its work and summarize it for Tony.")


# ---------------------------------------------------------------- turn state

@contextmanager
def _locked_state():
    """Read-modify-write the shared state file under an exclusive lock. Parallel tool calls
    (Codex runs hooks concurrently) would otherwise lose read-counter updates."""
    fh = open(STATE, "a+", encoding="utf-8")
    try:
        fcntl.flock(fh, fcntl.LOCK_EX)
        fh.seek(0)
        try:
            data = json.loads(fh.read() or "{}")
        except ValueError:
            data = {}
        if not isinstance(data, dict):
            data = {}
        yield data
        if len(data) > MAX_SESSIONS:
            for key in sorted(data, key=lambda k: data[k].get("t", 0) if isinstance(data[k], dict) else 0)[
                    : len(data) - MAX_SESSIONS]:
                del data[key]
        fh.seek(0)
        fh.truncate()
        fh.write(json.dumps(data))
    finally:
        fcntl.flock(fh, fcntl.LOCK_UN)
        fh.close()


def _key(harness: str, session: str) -> str:
    return f"{harness}:{session}"


def arm_turn(harness: str, session: str, level: str | None, info: dict | None = None) -> None:
    """Start a new turn for this session (called by jev_route on every real user prompt).
    A turn with level None clears any earlier enforcement. Running frontier subagents are kept."""
    if not session:
        return
    try:
        with _locked_state() as data:
            old = data.get(_key(harness, session))
            active = old.get("active", 0) if isinstance(old, dict) else 0
            data[_key(harness, session)] = dict(info or {}, t=time.time(), level=level, delegated=False,
                                                reads=0, stop_blocks=0, active=active)
    except OSError:
        pass


def load_turn(harness: str, session: str) -> dict | None:
    try:
        raw = STATE.read_text(encoding="utf-8")
        turn = json.loads(raw or "{}").get(_key(harness, session))
    except (OSError, ValueError, AttributeError):
        return None
    return turn if isinstance(turn, dict) else None


def update_turn(harness: str, session: str, **changes) -> None:
    try:
        with _locked_state() as data:
            turn = data.get(_key(harness, session))
            if isinstance(turn, dict):
                turn.update(changes)
    except OSError:
        pass


def gating(turn: dict | None) -> bool:
    """True while this turn is enforced frontier work that has not been delegated yet."""
    if not turn or turn.get("level") != "enforce" or turn.get("delegated") or turn.get("active", 0) > 0:
        return False
    if time.time() - float(turn.get("t", 0)) > TURN_TTL:
        return False
    return not OFF_SWITCH.exists()


def log(harness: str, event: str, action: str, detail: str = "") -> None:
    try:
        with open(LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"t": time.strftime("%Y-%m-%dT%H:%M:%S"), "harness": harness, "event": event,
                                 "action": action, "detail": detail[:120]}) + "\n")
    except OSError:
        pass


# ---------------------------------------------------------------- classifying tool calls

def readonly_command(cmd: str) -> bool:
    """True if every segment of a shell command only reads. Conservative: anything unknown is work."""
    text = re.sub(r"\d?>\s*/dev/null|2>&1|&>\s*/dev/null", " ", str(cmd))
    if ">" in text or "<<" in text:
        return False
    for seg in re.split(r"&&|\|\||[;|\n]", text):
        try:
            toks = shlex.split(seg)
        except ValueError:
            toks = seg.split()
        while toks and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", toks[0]):
            toks = toks[1:]
        if not toks:
            continue
        name = os.path.basename(toks[0])
        if name in ("bash", "sh", "zsh") and len(toks) > 2 and re.fullmatch(r"-[a-z]*c[a-z]*", toks[1]):
            if not readonly_command(toks[2]):  # Codex runs reads as `bash -lc "<cmd>"`
                return False
        elif name == "git":
            sub = next((t for t in toks[1:] if not t.startswith("-")), "")
            if sub not in READONLY_GIT:
                return False
        elif name == "sed" and any(t.startswith("-i") or t == "--in-place" for t in toks[1:]):
            return False
        elif name == "find" and any(t in ("-delete", "-exec", "-execdir", "-ok", "-okdir") for t in toks[1:]):
            return False
        elif name == "awk" and "system(" in seg:
            return False
        elif name not in READONLY_CMDS:
            return False
    return True


def _mcp_kind(tool: str) -> str:
    short = tool.split("__")[-1]
    return "read" if READISH_TOOL.search(short) and not WRITEISH_TOOL.search(short) else "work"


def _command_text(cmd) -> str:
    if isinstance(cmd, list):
        return shlex.join(str(c) for c in cmd)
    return str(cmd or "")


def classify(harness: str, tool: str, tin) -> str:
    """One of: "delegate" (frontier handoff, opens the gate), "allow", "read" (uses the budget), "work"."""
    tin = tin if isinstance(tin, dict) else {}
    if harness == "antigravity":
        if tool == "run_command":
            cmd = _command_text(tin.get("CommandLine"))
            return "delegate" if "frontier.py" in cmd else ("read" if readonly_command(cmd) else "work")
        if tool in AG_WORK:
            return "work"
        if tool in AG_READ:
            return "read"
        return "work" if WRITEISH_TOOL.search(tool) and not READISH_TOOL.search(tool) else "allow"
    if tool in ("Bash", "run_shell_command", "exec_command"):
        cmd = _command_text(tin.get("command"))
        if "frontier.py" in cmd:
            return "delegate"
        return "read" if readonly_command(cmd) else "work"
    if tool.startswith("mcp__"):
        return _mcp_kind(tool)
    if harness == "codex":
        # spawn_agent is never gated; SubagentStart decides whether it was a frontier agent.
        return "work" if tool == "apply_patch" else "allow"
    if tool in ("Agent", "Task"):
        kind = str(tin.get("subagent_type") or "")
        if kind in FRONTIER_AGENTS["claude"] or str(tin.get("model") or "").lower() == "opus":
            return "delegate"
        return "read" if kind in READONLY_AGENTS else "work"
    if tool == "SendMessage":
        return "delegate"  # continuing an existing subagent: the main model is handing work off, not doing it
    if tool in CLAUDE_ALWAYS:
        return "allow"
    if tool in CLAUDE_READ:
        return "read"
    return "work"


def deny_reason(harness: str, turn: dict, budget_used: bool) -> str:
    conf = turn.get("confidence")
    why = f"Jev frontier {conf:.2f}" if isinstance(conf, (int, float)) else "Tony asked for a frontier model"
    head = (f"{MARKER} Blocked: this turn is enforced frontier work ({why}). Do not do it on this model. ")
    if budget_used:
        head += f"You have used the {READ_BUDGET} quick reads allowed for preparing the handoff. "
    return head + f"{DELEGATE_HOW.get(harness, DELEGATE_HOW['antigravity'])}. {HANDOFF}"


def stop_reason(harness: str) -> str:
    return (f"{MARKER} You are about to end an enforced frontier turn without delegating it. Do not answer it "
            f"yourself. {DELEGATE_HOW.get(harness, DELEGATE_HOW['antigravity'])}. {HANDOFF} If you already "
            "answered, delegate anyway so the frontier model checks and completes the work.")


# ---------------------------------------------------------------- per-harness payload fields

def session_of(harness: str, payload: dict) -> str:
    return str(payload.get("conversationId") if harness == "antigravity" else payload.get("session_id") or "")


def tool_call(harness: str, payload: dict) -> tuple[str, dict]:
    if harness == "antigravity":
        call = payload.get("toolCall")
        call = call if isinstance(call, dict) else {}
        args = call.get("args")
        return str(call.get("name") or ""), args if isinstance(args, dict) else {}
    tin = payload.get("tool_input")
    return str(payload.get("tool_name") or ""), tin if isinstance(tin, dict) else {}


# ---------------------------------------------------------------- events

def on_pretool(harness: str, payload: dict) -> tuple[str, int]:
    if payload.get("agent_id"):  # Claude: a call made inside a subagent is never gated
        return "", 0
    session = session_of(harness, payload)
    turn = load_turn(harness, session)
    if not gating(turn):
        return "", 0
    tool, tin = tool_call(harness, payload)
    kind = classify(harness, tool, tin)
    if kind == "allow":
        return "", 0
    if kind == "delegate":
        update_turn(harness, session, delegated=True)
        log(harness, "pretool", "delegated", tool)
        return "", 0
    if kind == "read" and int(turn.get("reads", 0)) < READ_BUDGET:
        update_turn(harness, session, reads=int(turn.get("reads", 0)) + 1)
        return "", 0
    reason = deny_reason(harness, turn, budget_used=(kind == "read"))
    log(harness, "pretool", "deny", tool)
    if harness == "antigravity":
        return json.dumps({"decision": "deny", "reason": reason}), 0
    return json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                              "permissionDecisionReason": reason}}), 0


def _frontier_running(harness: str, payload: dict) -> bool:
    """Claude's Stop input lists in-flight background work; a running opus agent counts as delegated."""
    tasks = payload.get("background_tasks")
    if not isinstance(tasks, list):
        return False
    return any(isinstance(t, dict) and t.get("agent_type") in FRONTIER_AGENTS.get(harness, ()) for t in tasks)


def on_stop(harness: str, payload: dict) -> tuple[str, int]:
    if harness == "antigravity" and payload.get("terminationReason") not in (None, "", "model_stop"):
        return "", 0  # errors and step limits are not the model choosing to stop
    session = session_of(harness, payload)
    turn = load_turn(harness, session)
    if not gating(turn) or _frontier_running(harness, payload):
        return "", 0
    last = str(payload.get("last_assistant_message") or "").strip()
    if last.endswith("?") and len(last) <= QUESTION_MAX:
        log(harness, "stop", "allow_question")
        return "", 0
    if payload.get("stop_hook_active") or int(turn.get("stop_blocks", 0)) >= STOP_BLOCKS:
        log(harness, "stop", "stop_violation", f"conf={turn.get('confidence')}")
        update_turn(harness, session, level="violated")  # stop gating this turn; the log keeps the record
        return "", 0
    update_turn(harness, session, stop_blocks=int(turn.get("stop_blocks", 0)) + 1)
    log(harness, "stop", "stop_block")
    reason = stop_reason(harness)
    if harness == "antigravity":
        return json.dumps({"decision": "continue", "reason": reason}), 0
    return json.dumps({"decision": "block", "reason": reason}), 0


def on_subagent(harness: str, payload: dict, started: bool) -> tuple[str, int]:
    """Codex SubagentStart/SubagentStop. Only frontier agents count; they open the gate and
    keep it open while they run, including across Tony's next prompts."""
    if payload.get("agent_type") not in FRONTIER_AGENTS.get(harness, ()):
        return "", 0
    session = session_of(harness, payload)
    turn = load_turn(harness, session)
    if turn is None:
        return "", 0
    active = max(0, int(turn.get("active", 0)) + (1 if started else -1))
    if started:
        update_turn(harness, session, active=active, delegated=True)
        log(harness, "subagent-start", "delegated", str(payload.get("agent_type")))
    else:
        update_turn(harness, session, active=active)
    return "", 0


def on_before_model(harness: str, payload: dict) -> tuple[str, int]:
    """Gemini CLI: BeforeModel may override llm_request.model, so the enforced turn runs on Pro."""
    session = session_of(harness, payload)
    turn = load_turn(harness, session)
    if not gating(turn):
        return "", 0
    if not turn.get("swapped"):
        update_turn(harness, session, swapped=True)
        log(harness, "before-model", "model_swap", GEMINI_FRONTIER_MODEL)
    return json.dumps({"hookSpecificOutput": {"hookEventName": "BeforeModel",
                                              "llm_request": {"model": GEMINI_FRONTIER_MODEL}}}), 0


EVENTS = {
    "pretool": on_pretool,
    "stop": on_stop,
    "subagent-start": lambda h, p: on_subagent(h, p, True),
    "subagent-stop": lambda h, p: on_subagent(h, p, False),
    "before-model": on_before_model,
}


def handle(harness: str, event: str, payload) -> tuple[str, int]:
    if os.environ.get("AGENT_OS_DELEGATE_WORKER") or not isinstance(payload, dict) or event not in EVENTS:
        return "", 0
    try:
        return EVENTS[event](harness, payload)
    except Exception:
        return "", 0


def _arg(name: str, default: str) -> str:
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv[:-1] else default


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    out, code = handle(_arg("--harness", "claude"), _arg("--event", ""), payload)
    if out:
        print(out)
    return code


# ---------------------------------------------------------------- self-test

def self_test() -> int:
    """Replays one enforced turn per harness against a throwaway state file."""
    import tempfile
    global STATE, LOG
    tmp = tempfile.mkdtemp(prefix="route-gate-selftest-")
    STATE, LOG = Path(tmp) / "state.json", Path(tmp) / "log.jsonl"
    results = []

    def check(label, got, want):
        results.append(got == want)
        print(f"{'PASS' if got == want else 'FAIL'}  {label}: got={got!r} want={want!r}")

    def verdict(out):
        if not out:
            return "allow"
        d = json.loads(out)
        return d.get("decision") or d.get("hookSpecificOutput", {}).get("permissionDecision") or "model_swap"

    info = {"route": "frontier", "confidence": 0.97, "work_now": 0.9}
    # Claude
    arm_turn("claude", "s1", "enforce", info)
    pre = lambda tool, tin, **kw: verdict(handle("claude", "pretool", dict({"session_id": "s1", "tool_name": tool, "tool_input": tin}, **kw))[0])
    check("claude edit denied", pre("Edit", {"file_path": "x"}), "deny")
    check("claude read allowed", pre("Read", {"file_path": "x"}), "allow")
    check("claude read-only bash allowed", pre("Bash", {"command": "git status && ls -la"}), "allow")
    check("claude writing bash denied", pre("Bash", {"command": "echo hi > a.txt"}), "deny")
    check("claude subagent's own call allowed", pre("Edit", {}, agent_id="a1"), "allow")
    check("claude general-purpose agent denied", pre("Agent", {"subagent_type": "general-purpose"}), "deny")
    for _ in range(3):
        pre("Grep", {"pattern": "x"})
    check("claude read budget exhausted", pre("Read", {"file_path": "y"}), "deny")
    check("claude stop blocked once", verdict(handle("claude", "stop", {"session_id": "s1", "stop_hook_active": False})[0]), "block")
    check("claude stop then allowed (violation)", verdict(handle("claude", "stop", {"session_id": "s1", "stop_hook_active": True})[0]), "allow")
    arm_turn("claude", "s1", "enforce", info)
    check("claude opus spawn opens gate", pre("Agent", {"subagent_type": "opus-standard"}), "allow")
    check("claude edit after delegation allowed", pre("Edit", {"file_path": "x"}), "allow")
    check("claude stop after delegation allowed", verdict(handle("claude", "stop", {"session_id": "s1"})[0]), "allow")
    arm_turn("claude", "s1", "advise", info)
    check("claude advise never gates", pre("Edit", {"file_path": "x"}), "allow")
    # Codex
    arm_turn("codex", "c1", "enforce", info)
    cpre = lambda tool, tin: verdict(handle("codex", "pretool", {"session_id": "c1", "tool_name": tool, "tool_input": tin})[0])
    check("codex apply_patch denied", cpre("apply_patch", {"command": "*** Begin Patch"}), "deny")
    check("codex spawn allowed", cpre("spawn_agent", {"agent": "sol-standard"}), "allow")
    check("codex stop blocked", verdict(handle("codex", "stop", {"session_id": "c1", "stop_hook_active": False})[0]), "block")
    handle("codex", "subagent-start", {"session_id": "c1", "agent_type": "sol-standard"})
    check("codex patch allowed after sol starts", cpre("apply_patch", {"command": "x"}), "allow")
    arm_turn("codex", "c1", "enforce", info)
    check("codex new turn stays open while sol runs", cpre("apply_patch", {"command": "x"}), "allow")
    handle("codex", "subagent-stop", {"session_id": "c1", "agent_type": "sol-standard"})
    arm_turn("codex", "c1", "enforce", info)
    check("codex gate closes after sol stops", cpre("apply_patch", {"command": "x"}), "deny")
    # Antigravity
    arm_turn("antigravity", "g1", "enforce", info)
    apre = lambda name, args: verdict(handle("antigravity", "pretool", {"conversationId": "g1", "toolCall": {"name": name, "args": args}})[0])
    check("antigravity write denied", apre("write_to_file", {"TargetFile": "x"}), "deny")
    check("antigravity view allowed", apre("view_file", {"AbsolutePath": "x"}), "allow")
    check("antigravity stop continues", verdict(handle("antigravity", "stop", {"conversationId": "g1", "terminationReason": "model_stop"})[0]), "continue")
    check("antigravity frontier.py opens gate", apre("run_command", {"CommandLine": f"python3 {FRONTIER_PY} \"do it\""}), "allow")
    check("antigravity write after delegation", apre("write_to_file", {"TargetFile": "x"}), "allow")
    # Gemini
    arm_turn("gemini", "m1", "enforce", info)
    check("gemini enforced turn swaps model", verdict(handle("gemini", "before-model", {"session_id": "m1"})[0]), "model_swap")
    arm_turn("gemini", "m1", None, None)
    check("gemini normal turn untouched", verdict(handle("gemini", "before-model", {"session_id": "m1"})[0]), "allow")
    print(f"\n{sum(results)}/{len(results)} passed")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(self_test() if "--self-test" in sys.argv else main())
