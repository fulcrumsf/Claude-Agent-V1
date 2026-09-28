# Option B Model Routing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** In every harness Tony uses, each prompt starts on that harness's cheap model. Jev decides where the work belongs: the cheap model answers it, a frontier subagent in the same harness takes hard work, or a cheap OpenRouter Auto Router worker does chores through one shared `delegate` command.

**Architecture:** Two small shared Python scripts plus per-harness wiring. `jev_route.py` runs as each harness's "before the prompt" hook. It asks Jev (OpenRouter Decisions API) for one routing decision and adds a short hint the model sees; it never answers anything itself. `delegate.py` runs a headless Codex worker pointed at OpenRouter Auto Router (limited to approved cheap models), inside the existing `fs_guard.py` protection, and returns a short report plus the list of changed files for the main model to check. Frontier escalation uses each harness's native subagents: Claude `opus-standard` / `opus-deep` (already built) and Codex `sol-standard` / `sol-deep` (Task 5).

**Tech Stack:** Python 3.13 standard library only (`urllib`, `json`, `subprocess`, `unittest`); OpenRouter Decisions API (`typesafe/jev-1.13`); OpenRouter Auto Router; Codex CLI 0.157.1 (`codex exec`); the hook systems of Claude Code, Codex, Gemini CLI and Antigravity 2.0.

**Spec:** Replaces `001_Architecture/Plans/Universal_Jev_Router_Agent_OS_Plan.md` (Gemini draft, audited 2026-09-27: its hook doesn't exist, it used the wrong Jev endpoint and stale model IDs, and a local gateway daemon isn't needed). Tony's requirements, 2026-09-27 session:
1. Jev decides first, in every harness.
2. The default model is the harness's own lower-end model (Claude: Sonnet 5; Codex: an OpenAI model; Gemini: a Gemini model).
3. Frontier work goes to a stronger subagent in the same harness (Claude: Opus 5.5 at medium or high effort). Fable is never used.
4. Work that doesn't need a frontier model goes to OpenRouter Auto Router (DeepSeek, Qwen, GLM and similar).
5. Tony never switches models by hand.

## Global Constraints

- Jev never answers questions. It returns a decision only: model `typesafe/jev-1.13`, endpoint `POST https://openrouter.ai/api/alpha/decisions`, question types `choice`, `noul`, `score`.
- Every Jev call has a hard 1.0 s timeout and fails open: no hint, and the prompt continues untouched. (Measured 2026-09-27: 260–350 ms typical, one 18 s failure.)
- Agents never delete files or folders and never create new folders inside Agent-OS without Tony's approval. `001_Architecture/Scripts/fs_guard.py` enforces this and must keep passing `python3 001_Architecture/Scripts/fs_guard.py --self-test`.
- Secrets live only in `~/.env-secrets`. Scripts read that file directly because desktop apps don't load shell profiles. Never print or log a key.
- No new folders. Logs go to single files in the existing `~/Library/Logs/` (`Agent-OS-Router.jsonl`, `Agent-OS-Delegate-<timestamp>.log`).
- Standard library only, so each script starts in about 50 ms (hooks run on every prompt).
- Workspace file names are Title_Case_With_Underscores, except `.py` files (lowercase, like the rest of `001_Architecture/Scripts/`).
- Commit only after Tony says to commit. Media is never committed. Run the secret scan before any commit.
- Chores never publish, send, spend, or delete. Delegated workers follow the named skill exactly and invent no rules, tags or folders.

## File Map

| File | Status | Responsibility |
|---|---|---|
| `001_Architecture/Scripts/jev_route.py` | Create | Jev decision + hint text + per-harness hook I/O |
| `001_Architecture/Scripts/test_jev_route.py` | Create | Unit tests (HTTP mocked) |
| `001_Architecture/Scripts/delegate.py` | Create | `delegate` command: builds and runs the OpenRouter worker, returns report + changed files |
| `001_Architecture/Scripts/test_delegate.py` | Create | Unit tests (subprocess mocked) |
| `001_Architecture/Scripts/fs_guard.py` | Modify | Add the `antigravity` harness adapter |
| `~/.claude/settings.json` | Modify | `UserPromptSubmit` → `jev_route.py --harness claude` |
| `~/.codex/hooks.json` | Modify | `UserPromptSubmit` → `jev_route.py --harness codex` |
| `~/.codex/agents/sol-standard.toml`, `sol-deep.toml` | Create | Codex frontier subagents |
| `~/.gemini/settings.json` | Modify | `BeforeAgent` → `jev_route.py --harness gemini` |
| `~/.gemini/config/hooks.json` | Create (file only; the folder exists) | Antigravity: `PreToolUse` → fs_guard, `PreInvocation` → jev_route |
| `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` | Modify | One routing-rules block (same text in each) |
| `TOOLBOX.md`, `001_Architecture/Memory/Global_Agent_Memory.md` | Modify | Document the system |

---

### Task 0: Tony's prerequisites (manual, about 10 minutes)

Only Tony can do these. Nothing else starts until all four are checked.

- [x] **Step 1: Spending cap (done 2026-09-27).** Tony uses his existing OpenRouter key, with a $20/month credit limit. The cap covers everything on that key (Jev, chores, any other tool using it). Add the line `OPENROUTER_CHORES_KEY=<same value as OPENROUTER_API_KEY>` to `~/.env-secrets`; the plan's code reads that name.
- [x] **Step 2: Auto Router limits (done 2026-09-27, workspace-wide at openrouter.ai → Default Workspace → Routing).** Cost Tier Low; allowed models `deepseek/*`, `qwen/*`, `z-ai/*`, `moonshotai/*`, `google/gemini-3.8-flash`, `google/gemini-3.1-flash-lite`, `google/gemini-2.5-flash`, `google/gemini-2.5-flash-lite`; excluded `moonshotai/kimi-k3`; Prevent overrides on. No preset is needed: the worker uses `openrouter/auto` and these limits apply to it automatically.
- [ ] **Step 3: Set the cheap defaults. (pending Tony)** Claude Code: `"model": "sonnet"` in `~/.claude/settings.json` (Tony is doing this himself). Codex: DONE 2026-09-27, `gpt-6-luna` at `high` in `~/.codex/config.toml` (verified with `codex exec`). Gemini CLI and Antigravity: pick the Flash model in each app's model menu.
- [x] **Step 4: Confirm with the executing agent** that all three are done. The agent checks only that the key names exist, never their values:

```bash
grep -cE '^(export )?OPENROUTER_CHORES_KEY=' ~/.env-secrets
```

Expected: `1`

---

### Task 1: `jev_route.py` core (decision + hint)

**Files:**
- Create: `001_Architecture/Scripts/jev_route.py`
- Test: `001_Architecture/Scripts/test_jev_route.py`

**Interfaces:**
- Produces: `load_secret(name: str) -> str | None`, `decide(prompt: str, timeout: float = 1.0) -> Decision | None`, `hint_for(decision: Decision, harness: str) -> str | None`, and dataclass `Decision(route: str, confidence: float, multi_task: float)`, where `route` is one of `"answer"`, `"frontier"`, `"chore"`.

- [x] **Step 1: Write the failing tests**

```python
# 001_Architecture/Scripts/test_jev_route.py
import io
import json
import unittest
from unittest import mock

import jev_route


def fake_response(route="chore", conf=0.9, multi=0.1):
    body = {"answers": {
        "route": {"type": "choice", "choice": route, "confidence": conf,
                  "probabilities": {route: conf}},
        "multi_task": {"type": "noul", "noul": multi}}}
    return io.BytesIO(json.dumps(body).encode())


class DecideTests(unittest.TestCase):
    @mock.patch.object(jev_route, "load_secret", return_value="sk-test")
    @mock.patch("urllib.request.urlopen")
    def test_parses_route_and_multi_task(self, urlopen, _):
        urlopen.return_value.__enter__.return_value = fake_response("frontier", 0.8, 0.7)
        d = jev_route.decide("Re-architect the ingest pipeline across 6 scripts")
        self.assertEqual((d.route, d.confidence, d.multi_task), ("frontier", 0.8, 0.7))
        sent = json.loads(urlopen.call_args[0][0].data)
        self.assertEqual(sent["model"], "typesafe/jev-1.13")
        self.assertEqual(set(sent["questions"]), {"route", "multi_task"})

    @mock.patch.object(jev_route, "load_secret", return_value="sk-test")
    @mock.patch("urllib.request.urlopen", side_effect=TimeoutError)
    def test_fails_open_on_timeout(self, *_):
        self.assertIsNone(jev_route.decide("anything long enough to route"))

    @mock.patch.object(jev_route, "load_secret", return_value=None)
    def test_no_key_means_no_decision(self, _):
        self.assertIsNone(jev_route.decide("anything long enough to route"))

    def test_skips_slash_commands_and_tiny_prompts(self):
        self.assertIsNone(jev_route.decide("/model"))
        self.assertIsNone(jev_route.decide("yes"))


class HintTests(unittest.TestCase):
    def test_answer_gets_no_hint(self):
        self.assertIsNone(jev_route.hint_for(jev_route.Decision("answer", 0.9, 0.1), "claude"))

    def test_frontier_names_the_harness_subagents(self):
        h = jev_route.hint_for(jev_route.Decision("frontier", 0.8, 0.1), "claude")
        self.assertIn("opus-standard", h)
        h = jev_route.hint_for(jev_route.Decision("frontier", 0.8, 0.1), "codex")
        self.assertIn("sol-standard", h)

    def test_chore_points_to_delegate(self):
        h = jev_route.hint_for(jev_route.Decision("chore", 0.9, 0.1), "gemini")
        self.assertIn("delegate.py", h)

    def test_low_confidence_gets_no_hint(self):
        self.assertIsNone(jev_route.hint_for(jev_route.Decision("chore", 0.4, 0.1), "claude"))

    def test_brain_dump_hint_asks_to_split(self):
        h = jev_route.hint_for(jev_route.Decision("answer", 0.9, 0.8), "claude")
        self.assertIn("split", h.lower())


class SecretTests(unittest.TestCase):
    def test_reads_export_and_plain_lines(self):
        text = "export OPENROUTER_API_KEY=sk-a\nOTHER=1\nOPENROUTER_CHORES_KEY='sk-b'\n"
        with mock.patch("builtins.open", mock.mock_open(read_data=text)), \
             mock.patch.dict("os.environ", {}, clear=True):
            self.assertEqual(jev_route.load_secret("OPENROUTER_API_KEY"), "sk-a")
            self.assertEqual(jev_route.load_secret("OPENROUTER_CHORES_KEY"), "sk-b")


if __name__ == "__main__":
    unittest.main()
```

- [x] **Step 2: Run the tests and confirm they fail**

Run: `cd 001_Architecture/Scripts && python3 -m unittest test_jev_route -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'jev_route'`

- [x] **Step 3: Write the implementation**

```python
#!/usr/bin/env python3
"""Jev router hint for every harness (Tony, Option B, 2026-09-27).

Runs as the before-the-prompt hook. It asks Jev (a decision model; it never answers)
where the work belongs and adds one short hint the model sees:
  answer   -> no hint (the harness's cheap default model just answers)
  frontier -> hand it to this harness's frontier subagent
  chore    -> run the shared delegate command (OpenRouter Auto Router worker)
Fails open: no key, timeout, or any error means no hint and the prompt continues.
Off switch: create the file ~/.agent_os_router_off
"""
from __future__ import annotations

import json
import os
import re
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
        parts.append(f"This needs frontier-level reasoning. Hand it to {FRONTIER.get(harness, FRONTIER['gemini'])} "
                     "with the full goal, file paths, prior attempts and the output you need back.")
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
```

- [x] **Step 4: Run the tests and confirm they pass**

Run: `cd 001_Architecture/Scripts && python3 -m unittest test_jev_route -v`
Expected: all 10 tests PASS

- [x] **Step 5: One live call** (costs about $0.00002)

Run: `cd 001_Architecture/Scripts && python3 -c "import jev_route as j; print(j.decide('Ingest everything in 000_Ingest and tag it with the Resource Library tags'))"`
Expected: `Decision(route='chore', ...)`. If the route is wrong, adjust only the `criteria` wording in `QUESTIONS` and rerun. Record the final wording in the Task 7 notes.

---

### Task 2: Hook wiring for Claude Code, Codex and Gemini CLI

**Files:**
- Modify: `001_Architecture/Scripts/jev_route.py` (add `main()`)
- Modify: `001_Architecture/Scripts/test_jev_route.py`
- Modify: `~/.claude/settings.json`, `~/.codex/hooks.json`, `~/.gemini/settings.json`

**Interfaces:**
- Consumes: `decide`, `hint_for`, `log` from Task 1.
- Produces: `render(harness: str, hint: str | None) -> str` (the exact stdout for that harness) and the CLI `jev_route.py --harness claude|codex|gemini|antigravity`.

Verified hook formats (checked against each tool's docs, 2026-09-27):
- **Claude Code** `UserPromptSubmit`: stdin has `prompt`. To add context, stdout is `{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"..."}}`.
- **Codex** `UserPromptSubmit`: stdin has `prompt`. Same stdout shape as Claude Code. Any `matcher` is ignored.
- **Gemini CLI** `BeforeAgent`: stdin has `prompt`. Stdout `{"hookSpecificOutput":{"additionalContext":"..."}}` appends the text to the prompt for that turn.

- [x] **Step 1: Add the failing tests**

```python
class RenderTests(unittest.TestCase):
    def test_claude_and_codex_shape(self):
        for h in ("claude", "codex"):
            out = json.loads(jev_route.render(h, "HINT"))
            self.assertEqual(out["hookSpecificOutput"]["additionalContext"], "HINT")
            self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "UserPromptSubmit")

    def test_gemini_shape(self):
        out = json.loads(jev_route.render("gemini", "HINT"))
        self.assertEqual(out["hookSpecificOutput"]["additionalContext"], "HINT")

    def test_no_hint_prints_nothing(self):
        self.assertEqual(jev_route.render("claude", None), "")
```

- [x] **Step 2: Run the tests and confirm they fail**

Run: `cd 001_Architecture/Scripts && python3 -m unittest test_jev_route -v`
Expected: FAIL with `AttributeError: module 'jev_route' has no attribute 'render'`

- [x] **Step 3: Implement `render` and `main`** (append to `jev_route.py`)

```python
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


def prompt_from(payload: dict, harness: str) -> str:
    if harness == "antigravity":
        return antigravity_prompt(payload)  # defined in Task 3
    return str(payload.get("prompt") or "")


def main() -> int:
    harness = sys.argv[sys.argv.index("--harness") + 1] if "--harness" in sys.argv else "claude"
    try:
        payload = json.load(sys.stdin)
    except Exception:
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
```

Also add this stub now, so imports don't break before Task 3 replaces it:

```python
def antigravity_prompt(payload: dict) -> str:
    return ""
```

- [x] **Step 4: Run the tests and confirm they pass**

Run: `cd 001_Architecture/Scripts && python3 -m unittest test_jev_route -v`
Expected: all 13 tests PASS

- [ ] **Step 5: Register the hook in all three harnesses. (pending Tony)** Back up each file first as `<file>.bak-<date>-pre-jev-route`. Merge; never replace existing hooks.

```bash
cp ~/.claude/settings.json ~/.claude/settings.json.bak-$(date +%F)-pre-jev-route
cp ~/.codex/hooks.json ~/.codex/hooks.json.bak-$(date +%F)-pre-jev-route
cp ~/.gemini/settings.json ~/.gemini/settings.json.bak-$(date +%F)-pre-jev-route
python3 - <<'EOF'
import json, os
S = '/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/jev_route.py'
def add(path, event, harness, extra=None):
    p = os.path.expanduser(path); d = json.load(open(p))
    groups = d.setdefault("hooks", {}).setdefault(event, [])
    if any("jev_route.py" in h.get("command", "") for g in groups for h in g.get("hooks", [])):
        return print("already present:", path)
    hook = {"type": "command", "command": f'python3 "{S}" --harness {harness}', "timeout": 5}
    hook.update(extra or {})
    groups.append({"hooks": [hook]})
    json.dump(d, open(p, "w"), indent=2); print("added:", path)
add("~/.claude/settings.json", "UserPromptSubmit", "claude", {"statusMessage": "Jev routing"})
add("~/.codex/hooks.json", "UserPromptSubmit", "codex", {"statusMessage": "Jev routing"})
add("~/.gemini/settings.json", "BeforeAgent", "gemini", {"name": "agent-os-jev-route", "timeout": 5000})
EOF
```

Expected: three `added:` lines. (Gemini CLI timeouts are in milliseconds; the other two use seconds.)

- [x] **Step 6: Pipe-test each harness**

```bash
S=001_Architecture/Scripts/jev_route.py
echo '{"prompt":"Ingest everything in 000_Ingest and tag it"}' | python3 $S --harness claude
echo '{"prompt":"Ingest everything in 000_Ingest and tag it"}' | python3 $S --harness gemini
tail -2 ~/Library/Logs/Agent-OS-Router.jsonl
```

Expected: JSON containing `delegate.py`, and log lines with `"route": "chore"` and `ms` under 1000.

- [ ] **Step 7: Live test (pending Tony)**
  - **Claude Code:** start a new session, send "Rename every note in 000_Ingest to Title_Case and tag them", and confirm the reply mentions delegating.
  - **Codex:** run `codex`, open `/hooks`, trust the new `UserPromptSubmit` hook (Tony does this), then send the same prompt.
  - **Gemini CLI:** only if Tony has signed it in.

---

### Task 3: Antigravity adapters (file guard + Jev hint)

**Files:**
- Modify: `001_Architecture/Scripts/fs_guard.py` (payload adapter + `antigravity` output)
- Modify: `001_Architecture/Scripts/jev_route.py` (replace the `antigravity_prompt` stub)
- Modify: `001_Architecture/Scripts/test_jev_route.py`
- Create: `~/.gemini/config/hooks.json` (file only; `~/.gemini/config/` already exists)

**Interfaces:**
- Consumes: `evaluate(payload) -> Verdict | None` in fs_guard; `render("antigravity", hint)` from Task 2.
- Produces: `normalize_antigravity(payload: dict) -> dict` in fs_guard, and `antigravity_prompt(payload: dict) -> str` in jev_route.

Verified Antigravity 2.0 format (antigravity.google/docs/hooks, 2026-09-27):
- **Config:** global `~/.gemini/config/hooks.json`, shaped `{"<hook-set-name>": {"PreToolUse": [{"matcher": ..., "hooks": [{"type": "command", "command": ..., "timeout": 10}]}]}}`.
- **PreToolUse stdin:** `toolCall.name` and `toolCall.args`. Shell commands are `run_command` with `CommandLine`; file writes are `write_to_file` with `TargetFile`.
- **PreToolUse stdout:** `{"decision": "allow"|"deny"|"ask", "reason": "..."}`.
- **PreInvocation stdin:** has `invocationNum` and `transcriptPath` but **no prompt text**, so the prompt is read from the transcript file.
- **PreInvocation stdout:** `{"injectSteps":[{"ephemeralMessage":"..."}]}`.

- [x] **Step 1: Look at a real transcript first.** Open any Antigravity conversation, send one message, then find the transcript file:

```bash
ls -t ~/.gemini/antigravity/brain/*/ 2>/dev/null | head; find ~/.gemini/antigravity -newer ~/.gemini/settings.json -type f -name "*.json*" | head
```

Open the newest match. Write down the JSON path to the latest user message text; for example, each line is `{"type":"USER_INPUT","content":"..."}`. Step 4 uses exactly that shape. If `transcriptPath` points to a format that can't be read, skip Steps 4–5, keep the stub (no hint in Antigravity), and note it in Task 7.

- [x] **Step 2: Add the failing fs_guard tests.** Add these cases to the `cases` list in `self_test()`:

```python
("antigravity", {"toolCall": {"name": "run_command", "args": {"CommandLine": "rm -rf 000_Wiki", "Cwd": AO}}}, AO, "deny"),
("antigravity", {"toolCall": {"name": "write_to_file", "args": {"TargetFile": AO + "/Brand_New_Ag/x.md"}}}, AO, "ask"),
("antigravity", {"toolCall": {"name": "run_command", "args": {"CommandLine": "ls -la", "Cwd": AO}}}, AO, None),
```

Also change the loop so it builds the payload with `normalize_antigravity` when `tool == "antigravity"`:

```python
payload = {"tool_name": tool, "tool_input": tin, "cwd": cwd}
if tool == "antigravity":
    payload = normalize_antigravity(dict(tin, workspacePaths=[cwd]))
v = evaluate(payload)
```

Run: `python3 001_Architecture/Scripts/fs_guard.py --self-test`
Expected: FAIL, `NameError: name 'normalize_antigravity' is not defined`

- [x] **Step 3: Implement the fs_guard adapter.** Add this above `evaluate`:

```python
def normalize_antigravity(payload: dict) -> dict:
    """Map an Antigravity PreToolUse payload onto the shape evaluate() expects."""
    call = payload.get("toolCall") or {}
    name, args = str(call.get("name") or ""), call.get("args") or {}
    cwd = str(args.get("Cwd") or (payload.get("workspacePaths") or [str(AGENT_OS)])[0])
    if name == "run_command":
        return {"tool_name": "Bash", "tool_input": {"command": args.get("CommandLine", "")}, "cwd": cwd}
    if name == "write_to_file":
        return {"tool_name": "Write", "tool_input": {"file_path": args.get("TargetFile", "")}, "cwd": cwd}
    return {"tool_name": name, "tool_input": args, "cwd": cwd}
```

In `main()`, after `payload = json.load(sys.stdin)`, add:

```python
    if harness == "antigravity":
        payload = normalize_antigravity(payload)
```

Before the existing Claude `ask` branch, add:

```python
    if harness == "antigravity":
        print(json.dumps({"decision": v.kind, "reason": v.reason}))
        return 0
```

Run: `python3 001_Architecture/Scripts/fs_guard.py --self-test`
Expected: `48/48 passed`

- [x] **Step 4: Replace the jev_route stub.** Adjust the field names to match what Step 1 found; this example assumes JSON lines shaped like `{"type":"USER_INPUT","content":"..."}`.

```python
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
                try:
                    step = json.loads(line)
                except ValueError:
                    continue
                if step.get("type") == "USER_INPUT":
                    last = str(step.get("content") or "")
    except OSError:
        return ""
    return last
```

Add the test:

```python
    def test_antigravity_reads_last_user_message(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
            f.write('{"type":"USER_INPUT","content":"first"}\n{"type":"MODEL","content":"x"}\n'
                    '{"type":"USER_INPUT","content":"tag every note in the ingest folder"}\n')
        self.assertEqual(jev_route.antigravity_prompt({"invocationNum": 0, "transcriptPath": f.name}),
                         "tag every note in the ingest folder")
        self.assertEqual(jev_route.antigravity_prompt({"invocationNum": 2, "transcriptPath": f.name}), "")
```

Run: `cd 001_Architecture/Scripts && python3 -m unittest test_jev_route -v`
Expected: all 14 tests PASS

- [ ] **Step 5: Create `~/.gemini/config/hooks.json` (pending Tony)**

```bash
test -e ~/.gemini/config/hooks.json && echo "EXISTS - merge by hand, do not overwrite" || cat > ~/.gemini/config/hooks.json <<'EOF'
{
  "agent-os": {
    "PreToolUse": [
      {
        "hooks": [
          {"type": "command", "command": "python3 \"/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/fs_guard.py\" --harness antigravity", "timeout": 10}
        ]
      }
    ],
    "PreInvocation": [
      {
        "hooks": [
          {"type": "command", "command": "python3 \"/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/jev_route.py\" --harness antigravity", "timeout": 5}
        ]
      }
    ]
  }
}
EOF
```

- [ ] **Step 6: Live test in Antigravity. (pending Tony)** Restart Antigravity. Ask its agent to "run: rm 000_Ingest/fs_guard_nonexistent_test.txt"; the file doesn't exist, so nothing can be lost. Expected: refused with the Agent-OS guard message. Then send the chore prompt from Task 2 Step 7 and confirm the reply mentions delegating.

---

### Task 4: `delegate.py` (the OpenRouter Auto Router worker)

**Files:**
- Create: `001_Architecture/Scripts/delegate.py`
- Test: `001_Architecture/Scripts/test_delegate.py`

**Interfaces:**
- Consumes: `load_secret` from `jev_route.py`.
- Produces: the CLI `delegate.py "<task>" [--skill Skill_Name] [--cwd PATH] [--dry-run]`, plus `build_prompt(task: str, skill: str | None) -> str` and `build_command(prompt: str, cwd: str, last_msg_file: str) -> list[str]`.

Why Codex is the worker: `codex exec` is headless. It can use OpenRouter as a model provider (documented in OpenRouter's Codex CLI guide), and it already runs the trusted `fs_guard` hook plus `agent_os_guard.rules`, so a cheap worker can't delete anything. The worker's key is `OPENROUTER_CHORES_KEY`, which has the spending cap from Task 0.

- [x] **Step 1: Spike first: check that Codex + OpenRouter + Auto Router work.** Run this in a scratch folder, not in Agent-OS:

```bash
set -a; source ~/.env-secrets; set +a
cd /tmp && codex exec --skip-git-repo-check \
  -c 'model_providers.openrouter_chores={name="OpenRouter chores", base_url="https://openrouter.ai/api/v1", env_key="OPENROUTER_CHORES_KEY", wire_api="responses"}' \
  -c model_provider=openrouter_chores -m openrouter/auto \
  "Run 'ls /tmp | head -3' and tell me which model you are." 2>&1 | tail -15
```

Expected: a listing plus a model name. Then check openrouter.ai → Activity and confirm the model that answered is on the allowed list from Task 0 Step 2.
  - **If tool calls fail with the chosen model:** tell Tony. Workers need tool calling, so the allowed list must drop that model family.

- [x] **Step 2: Write the failing tests**

```python
# 001_Architecture/Scripts/test_delegate.py
import unittest
from unittest import mock

import delegate


class PromptTests(unittest.TestCase):
    def test_skill_is_read_first_and_rules_included(self):
        p = delegate.build_prompt("Ingest the 3 new files", "ingest")
        self.assertIn("001_Architecture/Skills/ingest/SKILL.md", p)
        self.assertIn("Never delete", p)
        self.assertLess(p.index("SKILL.md"), p.index("Ingest the 3 new files"))

    def test_without_skill(self):
        self.assertNotIn("SKILL.md", delegate.build_prompt("Summarize TOOLBOX.md", None))


class CommandTests(unittest.TestCase):
    def test_command_uses_openrouter_provider_and_auto_router(self):
        cmd = delegate.build_command("PROMPT", "/Users/tonymacbook2025/Documents/Agent-OS", "/tmp/last.txt")
        joined = " ".join(cmd)
        self.assertEqual(cmd[:2], ["codex", "exec"])
        self.assertIn("model_provider=openrouter_chores", joined)
        self.assertIn('env_key="OPENROUTER_CHORES_KEY"', joined)
        self.assertIn(delegate.MODEL, cmd)
        self.assertEqual(cmd[-1], "PROMPT")

    def test_refuses_without_chores_key(self):
        with mock.patch.object(delegate, "load_secret", return_value=None):
            self.assertEqual(delegate.main(["Summarize TOOLBOX.md"]), 2)


if __name__ == "__main__":
    unittest.main()
```

Run: `cd 001_Architecture/Scripts && python3 -m unittest test_delegate -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'delegate'`

- [x] **Step 3: Write the implementation**

```python
#!/usr/bin/env python3
"""delegate: hand a chore to a cheap OpenRouter Auto Router worker (Option B, 2026-09-27).

Usage: delegate.py "<task>" [--skill Skill_Name] [--cwd PATH] [--dry-run]
The worker is `codex exec` on OpenRouter (key OPENROUTER_CHORES_KEY, capped by Tony),
so the fs_guard hook and Codex rules still block deletes and new folders.
Prints the worker's final report plus the files it changed; the calling model must
check that list before telling Tony the chore is done.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jev_route import load_secret  # noqa: E402

AGENT_OS = "/Users/tonymacbook2025/Documents/Agent-OS"
MODEL = "openrouter/auto"
PROVIDER = ('model_providers.openrouter_chores={name="OpenRouter chores", '
            'base_url="https://openrouter.ai/api/v1", env_key="OPENROUTER_CHORES_KEY", wire_api="responses"}')
RULES = (
    "You are a chore worker in Tony's Agent-OS workspace. Rules, no exceptions:\n"
    "- Never delete files or folders. Never create a new folder. Guards block both; if blocked, stop and report.\n"
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


def build_command(prompt: str, cwd: str, last_msg_file: str) -> list[str]:
    return ["codex", "exec", "--skip-git-repo-check", "-C", cwd,
            "-c", PROVIDER, "-c", "model_provider=openrouter_chores",
            "-m", MODEL, "--output-last-message", last_msg_file, prompt]


def changed_files(cwd: str) -> str:
    try:
        return subprocess.run(["git", "-C", cwd, "status", "--porcelain"], capture_output=True,
                              text=True, timeout=30).stdout.strip() or "(no changes)"
    except Exception as exc:  # not a git folder, git missing
        return f"(could not list changes: {exc})"


def main(argv: list[str]) -> int:
    args = list(argv)
    def take(flag):
        if flag in args:
            i = args.index(flag); val = args[i + 1]; del args[i:i + 2]; return val
        return None
    skill, cwd = take("--skill"), take("--cwd") or AGENT_OS
    dry = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]
    if not args:
        print(__doc__); return 1
    key = load_secret("OPENROUTER_CHORES_KEY")
    if not key:
        print("delegate: OPENROUTER_CHORES_KEY missing from ~/.env-secrets (see plan Task 0).", file=sys.stderr)
        return 2
    stamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    log_path = Path.home() / "Library" / "Logs" / f"Agent-OS-Delegate-{stamp}.log"
    last_msg = str(log_path.with_suffix(".last.txt"))
    cmd = build_command(build_prompt(" ".join(args), skill), cwd, last_msg)
    if dry:
        print(" ".join(cmd[:-1]) + " <prompt>"); return 0
    before = changed_files(cwd)
    with open(log_path, "w", encoding="utf-8") as log:
        rc = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT,
                            env=dict(os.environ, OPENROUTER_CHORES_KEY=key)).returncode
    report = Path(last_msg).read_text(encoding="utf-8") if Path(last_msg).exists() else "(no final report)"
    print(f"Worker exit code: {rc}\n\n== Worker report ==\n{report}\n\n"
          f"== Git changes before ==\n{before}\n\n== Git changes after ==\n{changed_files(cwd)}\n\n"
          f"Full log: {log_path}\nCheck every changed file against the skill before reporting done.")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [x] **Step 4: Run the tests and confirm they pass**

Run: `cd 001_Architecture/Scripts && python3 -m unittest test_delegate -v`
Expected: all 4 tests PASS. Then run `python3 delegate.py "Summarize TOOLBOX.md" --dry-run`; expected output is the codex command line with `<prompt>` at the end.

- [x] **Step 5: Live chore test (read-only, safe)**

```bash
python3 001_Architecture/Scripts/delegate.py "Read TOOLBOX.md and list its top-level section headings. Do not change any file."
```

Expected: a report listing the headings, and "Git changes after" identical to "before". Check the cost at openrouter.ai → Activity; it should be a fraction of a cent.

- [x] **Step 6: Live guard test through the worker**

```bash
python3 001_Architecture/Scripts/delegate.py "Run exactly: rm 000_Ingest/fs_guard_nonexistent_test.txt  and report the result."
```

Expected: the report says the command was blocked by the Agent-OS guard.

---

### Task 5: Codex frontier subagents

**Files:**
- Create: `~/.codex/agents/sol-standard.toml`, `~/.codex/agents/sol-deep.toml` (`~/.codex/agents/` may not exist. It sits outside Agent-OS, so fs_guard allows it, but confirm the folder with Tony before creating it.)

Format (developers.openai.com/codex/subagents): standalone TOML with `name`, `description`, `developer_instructions`, and optional `model` and `model_reasoning_effort`. Cheap default: `gpt-6-luna`. Frontier: `gpt-6-sol`.

- [ ] **Step 1: Create both files (pending Tony)**

```toml
# ~/.codex/agents/sol-standard.toml
name = "sol-standard"
description = "Frontier escalation at medium effort for tasks too hard for the cheap default model: tricky multi-file bugs, non-obvious refactors, careful reviews, or anything the main model already failed once. Never for chores."
model = "gpt-6-sol"
model_reasoning_effort = "medium"
developer_instructions = """
You are the frontier worker for Tony's Agent-OS workspace. Follow AGENTS.md and any named skill exactly.
Never delete files or folders and never create folders without Tony's approval (guards enforce this; if blocked, report it).
Do the task fully, verify the real result, then report what you did, what you verified, and which files changed.
"""
```

```toml
# ~/.codex/agents/sol-deep.toml
name = "sol-deep"
description = "Frontier escalation at high effort for the hardest work only: system or pipeline design, multi-step builds across many files, bugs that resisted earlier attempts, high-stakes decisions. Prefer sol-standard otherwise. Never for chores."
model = "gpt-6-sol"
model_reasoning_effort = "high"
developer_instructions = """
You are the deep-reasoning worker for Tony's Agent-OS workspace. Follow AGENTS.md and any named skill exactly.
Never delete files or folders and never create folders without Tony's approval (guards enforce this; if blocked, report it).
Think the problem through first, do the task fully, verify the real result, then report what you did, what you verified, and which files changed.
"""
```

- [ ] **Step 2: Verify that Codex loads them (pending Tony)**

Run: `codex exec -m gpt-6-luna --skip-git-repo-check "List the custom agents you can spawn, names only."`
Expected: the output includes `sol-standard` and `sol-deep`.

---

### Task 6: Routing rules in every instruction file

**Files:**
- Modify: `CLAUDE.md` (under `## Shared Principles`), `AGENTS.md` (under `## Preservation Rule`), `GEMINI.md` (under `## Start Here`)

- [x] **Step 1: Insert the same block in all three files** (use a Python replace that asserts the anchor appears exactly once):

```markdown
**Model routing (Option B, 2026-09-27):** start every task on this harness's cheap default model. A `[Agent-OS router, Jev]` note may appear with your prompt; follow it.
- Answer questions and small edits yourself.
- Frontier work goes to this harness's frontier subagent (Claude: `opus-standard` / `opus-deep`; Codex: `sol-standard` / `sol-deep`).
- Chores (ingest, sorting, tagging, renaming, bulk summaries) go to `python3 001_Architecture/Scripts/delegate.py "<task>" --skill <Skill_Name>`. Then check the changed-files list it returns before reporting done.
- Brain dumps: split them into tasks and route each one. Never use Fable.
```

- [x] **Step 2: Verify**

Run: `grep -c "Model routing (Option B" CLAUDE.md AGENTS.md GEMINI.md`
Expected: `1` for each file.

---

### Task 7: End-to-end acceptance, docs, handoff

**Files:**
- Modify: `TOOLBOX.md` (extend the "Opus Escalation Subagents" section into "Model Routing (Option B)"), `001_Architecture/Memory/Global_Agent_Memory.md`, and today's `001_Architecture/Logs/<date>_Session-Log.md`
- Modify: `001_Architecture/Plans/Universal_Jev_Router_Agent_OS_Plan.md` (add a one-line "Superseded by Option_B_Model_Routing_Plan.md" banner at the top; delete nothing)

- [ ] **Step 1: Brain-dump test in Claude Code. (pending Tony)** Paste this into a fresh session on Sonnet:

> "Three things: 1) what's the difference between Seedance Mini and Seedance 2, 2) tag the notes in 000_Ingest with our Resource Library tags, 3) redesign how the Neon Parcel storyboard QA works so it catches scale errors earlier."

Expected: the router note asks to split. Item 1 is answered directly. Item 2 goes through `delegate.py --skill ingest` and comes back with a changed-files list. Item 3 goes to `opus-deep` (or `opus-standard`).

- [ ] **Step 2: Repeat the same brain dump in Codex and in Antigravity. (pending Tony)** Expected: the same three routes, with Codex using `sol-*`.

- [x] **Step 3: Review the router log**

Run: `python3 -c "import json,collections; rows=[json.loads(l) for l in open('/Users/tonymacbook2025/Library/Logs/Agent-OS-Router.jsonl')]; print(collections.Counter((r['harness'], r['route']) for r in rows)); print('max ms', max(r['ms'] for r in rows))"`
Expected: routes spread across harnesses, and max ms under 1000 (anything higher means the timeout fired and failed open).

- [x] **Step 4: Update docs.** TOOLBOX gets what each piece is and where it's configured, plus the off switch `touch ~/.agent_os_router_off`. Global memory gets one line. The session log gets the results, including any criteria rewording from Task 1 Step 5 and the Auto Router result from Task 4 Step 1.

- [x] **Step 5: Final checks**

```bash
python3 001_Architecture/Scripts/fs_guard.py --self-test | tail -1
cd 001_Architecture/Scripts && python3 -m unittest test_jev_route test_delegate 2>&1 | tail -3
```

Expected: `48/48 passed` and `OK`. Then ask Tony whether to commit (after running the secret scan).

---

## Open Items for Tony (decide before or during execution)

1. ~~Monthly cap~~ Done: $20/month on the shared OpenRouter key.
2. ~~Allowed worker models~~ Done: set workspace-wide on OpenRouter (Task 0 Step 2). Add Sonnet via OpenRouter only if chores turn out to need it; it bills per token, not against the Claude plan.
3. ~~Codex cheap default~~ Done: `gpt-6-luna`, high effort.
4. **Creating `~/.codex/agents/`** (outside Agent-OS) in Task 5.
5. **Gemini CLI sign-in:** needed for its live test only.

## Limits to know

- **A hint is not a hard switch.** No harness lets a hook change the main model mid-session; Jev's note plus the instruction-file rules make routing reliable, not guaranteed.
- **Every prompt gets about 0.3–0.5 s slower** in each harness (one Jev call). The off switch is `~/.agent_os_router_off`.
- **Delegated chores cost OpenRouter credits, not plan usage.** That's the point: plan limits last longer.
- **Opus and Sol subagents still use the $20 plans.** They just run only when needed.
