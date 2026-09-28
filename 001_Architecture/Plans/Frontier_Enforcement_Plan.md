# Frontier Enforcement Plan (Option B, part 2)

> Written 2026-09-27 by the `opus-deep` worker at Tony's request, after the Sonnet controller got the "delegate this now" hint twice and ignored it both times.
> Builds on `001_Architecture/Plans/Option_B_Model_Routing_Plan.md`. Additive: `fs_guard.py`, the anti-recursion flag, `delegate.py`'s worker isolation and the working parts of `jev_route.py` all stay.

## The problem in one line

The router's frontier hint is only advice. A cheap model can ignore it, and tonight it did. Tony wants hard work to reach a strong model without him saying anything, without the cheap model grinding first, and without paying for a strong model on small jobs.

## What was verified before designing (from installed code and docs, not memory)

| Harness | Version | What a hook can really do | Source checked |
|---|---|---|---|
| Claude Code | 2.1.170 | `PreToolUse` can deny any tool. `Stop` can block the turn from ending (`decision: block` + `reason`), and it receives `stop_hook_active`, `last_assistant_message` and `background_tasks`. Every hook input carries `agent_id` when the call comes from inside a subagent. No hook can change the model. | `claude.exe` hook-input schema (`qO()`, Stop schema) |
| Codex CLI + Codex Desktop | 0.157.1 | `PreToolUse` can deny. `Stop` `decision: block` continues the turn and feeds `reason` back as a new user prompt. `SubagentStart` / `SubagentStop` report `agent_type`. Subagent hooks share the parent `session_id`. Hooks must be trusted once in `/hooks`. No hook can change the model. | `codex_hooks.md` (developers.openai.com, cached tonight) |
| Gemini CLI | 0.45.2 | `BeforeModel` can return `hookSpecificOutput.llm_request.model` and the CLI really switches the model for that call (`modifiedModel` then `resolveModel()`; the alias `pro` resolves to the best Pro model the account can use). `AfterAgent` `decision: block` forces another pass. Subagents (`~/.gemini/agents/`) are on by default. | `@google/gemini-cli` bundle, `fireBeforeModelEvent` + `fromHookLLMRequest` |
| Antigravity IDE | 2.5.5 | `PreToolUse` can `deny`. `Stop` `decision: continue` blocks the stop. `PreInvocation` can inject steps. No documented custom-subagent config and no model switch. | bundled `agy-customizations/docs/hooks.md`, real transcripts |

So the old plan's line "no harness lets a hook swap the model" is wrong for Gemini CLI. It is right for the other three.

## Jev test results (live, 2026-09-27, 25 calls)

The old decision used only `route` + `multi_task`. It cannot tell "this conversation is heavy" from "do heavy work now". I added one question, `work_now` ("is the user asking for substantial work right now, rather than chatting, asking, approving, or one small edit?"), and gave Jev the last assistant message as context so short replies like "yes, build it" make sense.

| Message | route | conf | work_now | Result |
|---|---|---|---|---|
| Design a real enforcement layer ... implement it with tests | frontier | 1.00 | 0.98 | enforce |
| Seedance scale bug resisted 3 fixes, root-cause it | frontier | 1.00 | 0.97 | enforce |
| Refactor Neon Parcel scaffold + callers | frontier | 1.00 | 0.98 | enforce |
| "yes, build it" after a proposed design | frontier | 0.99 | 0.87 | enforce |
| "yes, build it" with no context | frontier | 0.62 | 0.60 | advise only |
| "ok" after a proposed design | frontier | 0.96 | 0.35 | advise only |
| Long "let's talk through the triggers" message | frontier | 0.33 | 0.11 | nothing |
| Swap the MODEL constant in delegate.py | answer | 0.84 | 0.11 | nothing |
| What does fs_guard do with /tmp deletes? | answer | 0.91 | 0.09 | nothing |
| "no, hold off on that for now" | answer | 0.28 | 0.03 | nothing |

Rule adopted: **enforce only when route = frontier, confidence >= 0.80 and work_now >= 0.70.** Frontier with confidence >= 0.60 otherwise gets the old soft hint. On this sample that is 4/4 real frontier jobs enforced and 0/7 conversational or small jobs enforced. The `multi_task` question is now told to ignore the context (with context it jumped to 0.5-0.8 on single requests).

## Design

Three layers, strongest first. Each harness gets the strongest layer it supports.

### Layer 1: make the right model do it from the start (Gemini CLI only)

`BeforeModel` hook: when the turn is enforced, return `llm_request.model = "pro"`. The whole turn runs on Pro. No handoff, no wasted Flash tokens. This is the ideal the other harnesses can't reach.

### Layer 2: a hard gate before any work happens (Claude Code, Codex, Antigravity)

`jev_route.py` (the prompt hook) now also writes a small **turn state** per session: level (`enforce` / `advise` / none), the Jev numbers, `delegated`, a read counter, a stop-block counter. File: `~/Library/Caches/Agent-OS-Router-State.json` (existing folder, file locked with `fcntl`, stale sessions pruned).

New `route_gate.py` runs as a `PreToolUse` hook. While the turn is enforced and nothing has been delegated yet:

- Frontier delegation is allowed and opens the gate: Claude `Agent` with `opus-standard` / `opus-deep` (or `model: opus`), or `SendMessage` to an existing agent; Codex `SubagentStart` of `sol-standard` / `sol-deep`; any harness running `frontier.py`.
- Up to 4 quick read-only calls are allowed so the model can gather file paths for a good handoff (Read, Grep, Glob, `cat`, `git status`, read-only MCP calls, the `Explore` subagent).
- Everything else that does work is denied with an exact instruction: edits, writes, non-read shell, `Skill`, non-frontier subagents, write-type MCP tools.
- Always allowed: `AskUserQuestion`, `TodoWrite`, `ToolSearch`, task/plan tools.
- Never gated: calls from inside a subagent (Claude `agent_id`), anything while a frontier subagent is running (Codex), the delegated worker itself (`AGENT_OS_DELEGATE_WORKER`), and everything when `~/.agent_os_router_off` exists.

This is real enforcement for work that needs tools: the cheap model cannot edit, build or run anything on an enforced turn until it delegates. Waste before delegation is capped at about 4 small reads.

### Layer 3: a stop backstop (Claude Code, Codex, Antigravity)

The gate can't stop a model that answers a frontier question in plain text without calling any tool. The `Stop` hook catches that: an enforced turn that is about to end with no delegation is blocked **once** and told to delegate. A short clarifying question (under 400 characters, ends in "?") is let through so the model can still ask Tony something. If the model still stops without delegating after that one block, it is allowed to stop (no infinite loops) and a `stop_violation` line is logged.

### Filling the two gaps

- **Gemini CLI:** Layer 1 replaces the need for a subagent. The strongest Gemini model does the turn itself.
- **Antigravity:** no custom-subagent config exists, so the frontier worker is a shell command: new `frontier.py`, a sibling of `delegate.py`. It runs `codex exec` on Tony's ChatGPT login with `gpt-6-sol` (the same model as `sol-standard`; `--deep` = high effort), with `delegate.py`'s isolation (no plugins, apps, browser, computer use, image generation or MCP servers) and `AGENT_OS_DELEGATE_WORKER=1` so it never routes or gates itself. It prints the report plus the files changed. Any harness can use it.

### Keeping cost down (the overkill guard)

1. The `work_now` question and the 0.80 / 0.70 thresholds (table above).
2. Tony's words win. "do it yourself", "don't delegate", "no subagent", "stay on sonnet" or "no opus" in the prompt means nothing is enforced. "use opus", "use sol", "go deep", "frontier model" or "ultrathink" enforces even if Jev is down.
3. If the session is already on a frontier model (Claude transcript model, the Claude `model` setting, Codex `model`, Antigravity `modelName` naming opus / sol / pro), nothing is enforced.
4. Chores stay advisory, as before. Enforcing chores is a possible later step.

### Honest limits

- **Claude Code, Codex, Antigravity:** a cheap model can still write one plain-text answer before the stop backstop catches it, and it can ignore the one stop block. That text answer is the only unenforceable leak, it is bounded to one reply, and every case is logged as `stop_violation`. Tool-using work cannot leak.
- **Codex:** `PreToolUse` doesn't say whether a call came from a subagent. The gate opens as soon as a `sol-*` subagent starts, so their calls pass. A non-frontier Codex subagent spawned on an enforced turn has its work tools blocked too, which is intended.
- **Codex headless (`codex exec`):** corrected tonight. `exec` does fire hooks: the `frontier.py` smoke run logged `hook: UserPromptSubmit` and wrote a router log line (skipped because of `AGENT_OS_DELEGATE_WORKER`). The earlier "zero log entries" were those same skipped `route: null` lines. TOOLBOX already records `fs_guard` blocking a delete inside a `delegate.py` worker, so workers are protected.
- **Codex trust:** the project hooks in `.codex/hooks.json` do nothing until Tony trusts them in `/hooks`, but the enforced hint already says "a hook blocks edits" for Codex because the file mentions `route_gate.py`. That sentence is only true once they're trusted.
- **Gemini CLI:** verified from source, not live (the CLI isn't signed in headlessly). Short follow-ups ("yes, do it") get no context in Gemini, because its transcript is a whole-session JSON file, not JSONL.
- **Antigravity:** tool names come from real transcripts (`view_file`, `run_command`, `grep_search`, `replace_file_content`, `write_to_file`, `list_dir`, `read_url_content`, `manage_task`). Unknown tools are allowed rather than blocked, so a new write tool would slip through until it's added.

## Files

| File | Change |
|---|---|
| `001_Architecture/Scripts/route_gate.py` | New. Turn state, PreToolUse gate, Stop backstop, Codex subagent tracking, Gemini model swap, audit log `~/Library/Logs/Agent-OS-Route-Gate.jsonl` |
| `001_Architecture/Scripts/test_route_gate.py` | New tests |
| `001_Architecture/Scripts/jev_route.py` | `work_now` question, last-assistant context, enforce/advise levels, Tony overrides, frontier-model check, writes turn state, ignores its own stop-continuation prompts |
| `001_Architecture/Scripts/test_jev_route.py` | Updated + new tests |
| `001_Architecture/Scripts/frontier.py` | New shell frontier worker |
| `001_Architecture/Scripts/test_frontier.py` | New tests |
| `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` | One new routing bullet (same text in each): `ENFORCED` means delegate first; Antigravity uses `frontier.py`; Gemini switches itself |
| `TOOLBOX.md` | `route_gate.py` and `frontier.py` entries; corrected the "hint only" line |
| `001_Architecture/Scripts/delegate.py` | Two backward-compatible parameters (`effort` for `isolation_overrides`, `prefix` for `open_log`) so `frontier.py` reuses them |
| `.agents/hooks.json` | Antigravity: gate on `PreToolUse`, backstop on `Stop` |
| `.codex/hooks.json` (project) | Codex: gate on `PreToolUse`, `SubagentStart`, `SubagentStop`, `Stop` (inert until Tony trusts them in `/hooks`) |
| `~/.claude/settings.json`, `~/.gemini/settings.json` | Tony adds the snippets below (agents are blocked from editing these) |

## Wiring Tony adds himself

**Claude Code** (`~/.claude/settings.json`, inside `"hooks"`): add one `PreToolUse` group and one `Stop` group.

```json
"PreToolUse": [
  { "matcher": "*", "hooks": [ { "type": "command", "command": "python3 \"/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/route_gate.py\" --harness claude --event pretool", "timeout": 5 } ] }
],
"Stop": [
  { "hooks": [ { "type": "command", "command": "python3 \"/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/route_gate.py\" --harness claude --event stop", "timeout": 5 } ] }
]
```

(Append these groups next to the existing `fs_guard` `PreToolUse` group; don't replace it.)

**Gemini CLI** (`~/.gemini/settings.json`, inside `"hooks"`): add

```json
"BeforeModel": [
  { "hooks": [ { "type": "command", "name": "agent-os-route-gate", "command": "python3 \"/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/route_gate.py\" --harness gemini --event before-model", "timeout": 5000 } ] }
]
```

**Codex:** open an interactive `codex` session in Agent-OS, run `/hooks`, and trust the four new project hooks from `.codex/hooks.json`.

**Antigravity:** nothing. `.agents/hooks.json` is read automatically.

## Verification

- Unit tests: `cd 001_Architecture/Scripts && python3 -m unittest` and `python3 fs_guard.py --self-test`.
- Pipe tests: `route_gate.py --self-test` replays a full enforced turn per harness (arm, denied edit, allowed reads, budget exhausted, delegation opens the gate, stop blocked once, then allowed).
- Live checks for Tony (one message each, after wiring): in Claude Code send "Design and build X across these 5 files" and confirm the first action is an `opus-standard` spawn; then `tail ~/Library/Logs/Agent-OS-Route-Gate.jsonl`.

## Status (2026-09-27, end of session)

Built and tested: everything in the Files table. 92 unit tests pass (`python3 -m unittest` in `001_Architecture/Scripts`), `fs_guard.py --self-test` 49/49, `route_gate.py --self-test` 26/26.

Live checks run tonight:
- Real hook entry points piped with live Jev: a Claude frontier prompt was enforced (edit denied, stop blocked once, `opus-standard` spawn opened the gate); a small-edit prompt and a "do it yourself" prompt were not enforced; a Gemini frontier prompt produced the `llm_request.model = "pro"` override.
- Antigravity: "yes, build it" after a proposed design was read against the transcript context and enforced (Jev 0.98, work_now 0.82); `replace_file_content` was denied; `frontier.py` opened the gate; a later invocation in the same turn kept the state.
- `frontier.py` live run: `gpt-6-sol` on the `openai` provider answered, exit 0.

Live in Antigravity now (`.agents/hooks.json` is read automatically). Codex needs `/hooks` trust. Claude Code and Gemini CLI need Tony's snippets above.

## Open items

1. Live-test Gemini CLI `BeforeModel` swap once the CLI is signed in.
2. First real Claude Code session after wiring: confirm the `PreToolUse` gate sees `agent_id` on subagent calls (the schema says it does) by checking that the `opus-standard` subagent's own edits are never denied.
3. Watch `stop_violation` counts for a week. If they are common in one harness, raise its stop-block limit from 1 to 2.
4. Antigravity `PreInvocation` can inject a `toolCall` step, which could run `frontier.py` without the model choosing to. Its semantics for long commands are undocumented, so it's parked as an experiment.
5. Chores are still advisory. The same gate could enforce `delegate.py` later if chores keep getting done inline.
