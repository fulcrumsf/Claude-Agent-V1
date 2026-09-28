#!/usr/bin/env python3
"""Jev router hint for every harness (Tony, Option B, 2026-09-27).

Runs as the before-the-prompt hook. It asks Jev (a decision model; it never answers)
where the work belongs and adds one short hint the model sees:
  answer   -> no hint (the harness's cheap default model just answers)
  frontier -> hand it to this harness's frontier subagent
  chore    -> run the shared delegate command (OpenRouter Auto Router worker)
Fails open: no key, timeout, or any error means no hint and the prompt continues.
Timeouts: 1.0 s per Jev request, plus a 1.5 s wall-clock guard on the whole hook run
(which also bounds the Antigravity transcript read).
Off switch: create the file ~/.agent_os_router_off
Also skipped when the environment variable AGENT_OS_DELEGATE_WORKER is set (non-empty) —
this stops a delegate.py worker (Task 4) from recursively triggering its own routing.
"""
from __future__ import annotations

import json
import os
import re
import signal
import sys
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path

JEV_URL = "https://openrouter.ai/api/alpha/decisions"
JEV_MODEL = "typesafe/jev-1.13"
SECRETS = Path.home() / ".env-secrets"
LOG = Path.home() / "Library" / "Logs" / "Agent-OS-Router.jsonl"
OFF_SWITCH = Path.home() / ".agent_os_router_off"
MIN_CONFIDENCE = 0.6
WALL_CLOCK = 1.5  # seconds for the whole hook run; past this the hook exits silently
DELEGATE = "python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/delegate.py"

FRONTIER = {
    "claude": "the `opus-standard` subagent (or `opus-deep` for architecture, big builds, or bugs that resisted earlier attempts)",
    "codex": "the `sol-standard` custom agent (or `sol-deep` for architecture, big builds, or stubborn bugs)",
    "gemini": "the strongest model available here, or tell Tony it needs a frontier session",
    "antigravity": "the strongest model available here, or tell Tony it needs a frontier session",
}

QUESTIONS = {
    "route": {
        "type": "choice",
        "instructions": "Where should this request to a coding agent be handled?",
        "criteria": {
            "answer": "A question, explanation, lookup, or small edit that a mid-tier model handles well in one short turn.",
            "frontier": "Hard work needing deep reasoning: system or pipeline design, multi-file refactors, debugging a stubborn problem, high-stakes decisions.",
            "chore": "Mechanical or high-volume work with clear instructions: ingesting or sorting files, tagging, renaming, reformatting, summarizing many documents, filling templates.",
        },
    },
    "multi_task": {
        "type": "noul",
        "instructions": "Does this message contain several separate tasks that could be handled independently?",
        "criteria": {
            "true": "It lists or mixes two or more distinct jobs, like a brain dump or to-do list.",
            "false": "It is one request, even if that request has steps.",
        },
    },
}


@dataclass
class Decision:
    route: str
    confidence: float
    multi_task: float


def load_secret(name: str) -> str | None:
    if os.environ.get(name):
        return os.environ[name]
    try:
        with open(SECRETS, encoding="utf-8") as fh:
            for line in fh:
                m = re.match(rf"^\s*(?:export\s+)?{name}\s*=\s*['\"]?([^'\"\s]+)", line)
                if m:
                    return m.group(1)
    except OSError:
        pass
    return None


def decide(prompt: str, timeout: float = 1.0) -> Decision | None:
    if os.environ.get("AGENT_OS_DELEGATE_WORKER"):
        return None
    text = (prompt or "").strip()
    if len(text) < 20 or text.startswith("/") or OFF_SWITCH.exists():
        return None
    key = load_secret("OPENROUTER_API_KEY")
    if not key:
        return None
    body = json.dumps({"model": JEV_MODEL, "state": {"request": text[:12000]},
                       "questions": QUESTIONS}).encode()
    req = urllib.request.Request(JEV_URL, data=body, method="POST", headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            answers = json.load(resp)["answers"]
        route = answers["route"]
        return Decision(route["choice"], float(route.get("confidence", 0)),
                        float(answers["multi_task"]["noul"]))
    except Exception:
        return None


def hint_for(d: Decision, harness: str) -> str | None:
    parts = []
    if d.multi_task >= 0.6:
        parts.append("This message holds several tasks. Split it into separate tasks and route each one on its own "
                     "(answer it yourself / frontier subagent / delegate chore).")
    if d.confidence >= MIN_CONFIDENCE and d.route == "frontier":
        parts.append(f"This needs frontier-level reasoning. Do not do it yourself: delegate it now by spawning "
                     f"{FRONTIER.get(harness, FRONTIER['gemini'])}, handing it the full goal, file paths, prior "
                     "attempts and the output you need back.")
    elif d.confidence >= MIN_CONFIDENCE and d.route == "chore":
        parts.append(f"This is a chore. Do not do it yourself: run `{DELEGATE} \"<task>\" --skill <Skill_Name>`, "
                     "then check the changed-files list it returns before telling Tony it is done.")
    if not parts:
        return None
    return "[Agent-OS router, Jev] " + " ".join(parts)


def log(harness: str, d: Decision | None, ms: int) -> None:
    try:
        with open(LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"t": time.strftime("%Y-%m-%dT%H:%M:%S"), "harness": harness, "ms": ms,
                                 "route": d.route if d else None,
                                 "confidence": d.confidence if d else None,
                                 "multi_task": d.multi_task if d else None}) + "\n")
    except OSError:
        pass


def render(harness: str, hint: str | None) -> str:
    if not hint:
        return ""
    if harness in ("claude", "codex"):
        return json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                                                  "additionalContext": hint}})
    if harness == "gemini":
        return json.dumps({"hookSpecificOutput": {"additionalContext": hint}})
    if harness == "antigravity":
        return json.dumps({"injectSteps": [{"ephemeralMessage": hint}]})
    return ""


def antigravity_prompt(payload: dict) -> str:
    """PreInvocation has no prompt field; read the last user message from the transcript.
    Only route on the first model call of a turn."""
    if int(payload.get("invocationNum") or 0) != 0:
        return ""
    path = payload.get("transcriptPath")
    if not path:
        return ""
    last = ""
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                if "USER_INPUT" not in line:
                    continue
                try:
                    step = json.loads(line)
                except ValueError:
                    continue
                if isinstance(step, dict) and step.get("type") == "USER_INPUT":
                    last = str(step.get("content") or "")
    except OSError:
        return ""
    return last


def prompt_from(payload: dict, harness: str) -> str:
    if harness == "antigravity":
        return antigravity_prompt(payload)  # defined in Task 3
    return str(payload.get("prompt") or "")


class _Deadline(Exception):
    pass


def _on_deadline(signum, frame):
    raise _Deadline()


def main() -> int:
    """Never fails the prompt: any error or the wall-clock deadline means exit 0, no output."""
    old = None
    try:
        old = signal.signal(signal.SIGALRM, _on_deadline)
        signal.setitimer(signal.ITIMER_REAL, WALL_CLOCK)
    except (ValueError, AttributeError, OSError):  # no SIGALRM here or not the main thread
        old = None
    try:
        try:
            return _run()
        except Exception:
            return 0
    except _Deadline:  # the one-shot timer fired inside the handler above
        return 0
    finally:
        if old is not None:
            try:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, old)
            except _Deadline:
                pass


def _run() -> int:
    harness = sys.argv[sys.argv.index("--harness") + 1] if "--harness" in sys.argv else "claude"
    payload = json.load(sys.stdin)
    if not isinstance(payload, dict):
        return 0
    start = time.time()
    d = decide(prompt_from(payload, harness))
    log(harness, d, int((time.time() - start) * 1000))
    out = render(harness, hint_for(d, harness) if d else None)
    if out:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
