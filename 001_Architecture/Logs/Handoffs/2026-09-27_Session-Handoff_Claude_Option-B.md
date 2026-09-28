# Session Handoff — 2026-09-27 (afternoon): Option B Model Routing

**Next session:** start Claude Code on **Sonnet** (set `"model": "sonnet"` or pick it in the model menu), then say:
**"Execute the Option B plan, subagent-driven."**

## To-do (real items only)

1. **Execute the plan:** [`001_Architecture/Plans/Option_B_Model_Routing_Plan.md`](../../Plans/Option_B_Model_Routing_Plan.md). Task 0 is done except Tony's Sonnet default. Start at Task 1. Use the `superpowers:subagent-driven-development` skill; hand hard tasks to `opus-standard` (or `opus-deep` for Task 3's transcript work if it gets tricky).
2. **Tony, during execution:** trust the new Codex `UserPromptSubmit` hook (`codex` → `/hooks`) at Task 2 Step 7, and approve creating `~/.codex/agents/` at Task 5.
3. **Tony, whenever convenient:** delete the empty folder `002_Content-Creation/Video_Editor/002_Channels/002_Neon-Parcel/Productions/0002_Delivery-Wildlife-Encounters-Compilation/Production/Shot-02-Kangaroo-Doorbell-AU/Real_References`.

## Already done and verified this session (don't redo)

- **File guard** `001_Architecture/Scripts/fs_guard.py` (45/45 self-test): blocks all agent deletes and asks before new folders. Live in Claude Code (global settings) and Codex (hook trusted and live-tested, plus `~/.codex/rules/agent_os_guard.rules`). Installed in Gemini CLI but only pipe-tested, since headless Gemini isn't signed in. It covers Codex file patches. Antigravity is Task 3 of the plan.
- **Opus helpers:** `~/.claude/agents/opus-standard.md` (Opus, medium effort) and `opus-deep.md` (Opus, high effort).
- **Defaults:** Codex `gpt-6-luna` at high (in `~/.codex/config.toml`); Gemini 3.8 Flash at medium. Codex CLI is updated to 0.157.1.
- **OpenRouter:** one key, $20/month cap, only this system uses it. `OPENROUTER_CHORES_KEY` equals `OPENROUTER_API_KEY` in `~/.env-secrets`. Auto Router limits are set workspace-wide: Low tier; deepseek, qwen, z-ai and moonshotai families plus 4 Gemini Flash models; Kimi K3 excluded; Prevent overrides on.
- **Neon Parcel 0002** re-scaffolded (Option A). Shots now live in `Production/Shot-NN-*/`. Build new shots with `scaffold_new_production.py <production> --shot Shot-NN-Name`.
- **Graphify:** the unused root `graphify-out/` and `001_Architecture/Graphify/Graphify-Out/` were deleted by Tony. AGENTS.md and REGISTRY no longer build a graph at the root.

## Facts the executor needs (checked against docs today)

- **Jev only decides; it never answers.** It uses `POST https://openrouter.ai/api/alpha/decisions` with model `typesafe/jev-1.13`. Typical latency 260–350 ms; one 18 s failure was seen, so the 1.0 s timeout fails open.
- **Antigravity 2.0 has hooks** at `~/.gemini/config/hooks.json`. Its pre-model-call hook has no prompt field, so the prompt is read from `transcriptPath`, with an inspection step first.
- **Hermes was ruled out as the main harness:** it can't use Claude Pro (the login needs Max plus paid extra usage) or the Gemini consumer plan.
