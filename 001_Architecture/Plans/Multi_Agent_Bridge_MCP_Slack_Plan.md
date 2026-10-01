# Multi-Agent Bridge (MCP + Slack) Plan

> **Date:** 2026-09-30  
> **Status:** Draft / Planned  
> **Target:** Claude Code (Lead Orchestrator), Codex CLI/Desktop, Antigravity IDE / Gemini SDK  
> **Primary Goal:** Enable seamless cross-agent communication, peer review, and task delegation without manual copy-pasting, with real-time visibility in a dedicated Slack channel (`#agents-war-room`).

---

## 1. Executive Summary & Objective

Tony currently maintains active subscriptions across three primary agent platforms ($60/mo total):
1. **Claude Code (Anthropic)** — Primary orchestrator, interactive coding, complex tool execution, repo-level refactoring.
2. **Codex CLI / Desktop (OpenAI)** — Fast logic verification, deterministic code review, unit tests, `fs_guard` adherence.
3. **Antigravity IDE / Gemini SDK (Google)** — 1M–2M token context window, repository-wide architecture audits, multimodal processing, Gemini video/image analysis.

Currently, sharing findings between these agents requires manual copy-pasting. Furthermore, running tasks in Gemini CLI faces authentication barriers due to personal OAuth deprecation. 

This plan designs the **Multi-Agent Bridge**:
- A lightweight **Model Context Protocol (MCP)** server (`agent-bridge-mcp`) accessible by Claude Code, Codex, and Antigravity.
- Headless execution runners for Antigravity (`google-antigravity` Python SDK via `GEMINI_API_KEY`) and Codex (`codex exec`).
- Real-time streaming into a private **Slack Channel** (`#agents-war-room`) so Tony can observe peer discussions and audits live from desktop or mobile.

---

## 2. Multi-Phase Architectural Roadmap

### Phase 1: Core Bridge & Slack War Room (This Plan)
- **Local MCP Server (`agent-bridge-mcp`):** Exposes peer-messaging and peer-audit tools.
- **Headless Runners:**
  - Antigravity Runner (`001_Architecture/Scripts/antigravity_worker.py`) using `google-antigravity` SDK.
  - Codex Runner (`001_Architecture/Scripts/codex_worker.py` or reusing `frontier.py` / `delegate.py`).
- **Slack Gateway:** Webhook / Bot integration posting handoffs, reasoning summaries, and audits into `#agents-war-room`.
- **Peer-Review Loop:** Automated "Triple-Check" workflow where Claude drafts, Antigravity audits architecture/context, and Codex verifies logic/safety.

### Phase 2: Department Action APIs & Autonomous Tool Handlers (Future)
- Expose workspace scripts across `001_Architecture/Tools/` as standardized API actions:
  - `video_pipeline_action`: Trigger Seedance/Veo, FFmpeg cuts, or Blotato publishing.
  - `ecommerce_action`: Sync Printify mockups, Etsy digital product uploads, Redbubble metadata.
  - `ingest_action`: Batch classify and route intake files via `process_image_ingest.py`.
- Enables agents to not only talk, but dispatch operations across Tony's business units.

### Phase 3: Unified Agent-OS Command Center Visual Dashboard (Future)
- A local web / desktop application providing a high-level operational GUI.
- Connects to the same event bus / MCP backend as Slack.
- Full details specified in [`001_Architecture/Plans/Agent_OS_Command_Center_Dashboard_Roadmap.md`](file:///Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Plans/Agent_OS_Command_Center_Dashboard_Roadmap.md).

---

## 3. Phase 1 Detailed Design

### 3.1 Architecture Diagram

```
                 ┌──────────────────────────────────────────────────┐
                 │                Tony (User Observer)              │
                 │         Monitors Slack / Guides Direction        │
                 └─────────────────────────┬────────────────────────┘
                                           │
                                           ▼
┌──────────────────────┐        ┌──────────────────────┐        ┌──────────────────────┐
│  Claude Code (Lead)  │◄──────►│   agent-bridge-mcp   │◄──────►│  Slack #agents-room  │
│  Orchestrates Build  │        │   (Local MCP Server) │        │  (Real-Time Stream)  │
└──────────────────────┘        └──────────┬───────────┘        └──────────────────────┘
                                           │
                 ┌─────────────────────────┴─────────────────────────┐
                 ▼                                                   ▼
┌──────────────────────────────────┐               ┌──────────────────────────────────┐
│   Headless Antigravity Worker    │               │      Headless Codex Worker       │
│  google-antigravity Python SDK   │               │            codex exec            │
│  (Gemini 3.5 Pro / Flash)        │               │         (GPT-5 / Sol / Luna)     │
└──────────────────────────────────┘               └──────────────────────────────────┘
```

---

### 3.2 MCP Server Tool Specification (`agent-bridge-mcp`)

The MCP server will register in `~/.claude.json` (Claude Code), `~/.codex/config.toml` (Codex), and `001_Architecture/MCP/gemini_mcp_config.json` (Antigravity).

It exposes 3 primary tools:

1. `delegate_to_agent(target_agent: str, task_prompt: str, context_files: list[str], model_tier: str)`
   - **`target_agent`**: `"antigravity"` | `"codex"`
   - **`task_prompt`**: The objective or review request.
   - **`context_files`**: Relative paths to relevant source files or plans.
   - **`model_tier`**: `"pro"` (deep reasoning/architecture) or `"flash"`/`"fast"` (quick lookup/minor check).
   - **Behavior**:
     - Posts initiation notice to Slack `#agents-war-room`.
     - Spawns the headless worker with file preservation rules (`fs_guard` compatible).
     - Streams reasoning/thoughts to Slack.
     - Returns final report and changed files list back to caller.

2. `request_peer_audit(artifact_path: str, audit_focus: str)`
   - Dispatches a parallel review to both Antigravity (macro-architecture & cross-repo coherence) and Codex (micro-logic, typing, syntax, safety).
   - Streams both reviews side-by-side into Slack.
   - Synthesizes findings into an actionable markdown report.

3. `post_agent_update(message: str, category: str)`
   - Allows any agent to post milestone updates, blockers, or completed tasks to Slack without blocking execution.

---

### 3.3 Worker Implementations

#### A. Antigravity Worker (`001_Architecture/Scripts/antigravity_worker.py`)
- Uses official `google-antigravity` Python SDK.
- Auth: Reads `GEMINI_API_KEY` from `~/.env-secrets` (no OAuth fragility).
- Model selection: Configured dynamically:
  - `model="gemini-3.5-pro"` for architectural reviews.
  - `model="gemini-3.5-flash"` for quick checks and chores.
- Capabilities: Runs with read-only or read/write sandboxed tools per task.

#### B. Codex Worker (`001_Architecture/Scripts/codex_worker.py`)
- Uses `codex exec` with `--skip-git-repo-check`.
- Runs with isolated environment overrides (similar to `delegate.py` and `frontier.py`).
- Hooks into `fs_guard.py` to enforce zero unauthorized deletes or folder creations.

---

### 3.4 Slack Integration Specs

- **Channel:** `#agents-war-room` (or private workspace channel).
- **Credentials:** `SLACK_BOT_TOKEN` and `SLACK_SIGNING_SECRET` stored strictly in `~/.env-secrets`.
- **Bot Persona Formats:**
  - `🤖 [Claude Code]`: Purple badge, reports orchestration and build diffs.
  - `🔷 [Antigravity/Gemini]`: Blue badge, reports architectural analysis, visual review, and 1M-context scans.
  - `🟢 [Codex]`: Green badge, reports logic audits, test execution results, and security checks.
  - `👤 [Tony Override]`: Tony can post in-thread; agents listen or poll when waiting on input.

---

## 4. Implementation Steps (Phase 1)

1. **Task 1: Slack App Setup**
   - Create Slack app with `chat:write`, `channels:history`, `channels:read` scopes.
   - Save tokens to `~/.env-secrets`.
2. **Task 2: Build `antigravity_worker.py`**
   - Headless script using `google-antigravity` SDK.
   - CLI flags: `--task`, `--model [flash|pro]`, `--files`, `--stream-slack`.
   - Unit tests covering prompt formatting and SDK error handling.
3. **Task 3: Build `codex_worker.py`**
   - Clean headless wrapper around `codex exec` with proper isolation overrides.
4. **Task 4: Build `agent_bridge_mcp.py`**
   - Lightweight Python FastMCP / MCP stdio server.
   - Wire tools: `delegate_to_agent`, `request_peer_audit`, `post_agent_update`.
5. **Task 5: Registration & Config**
   - Add to `~/.claude.json`.
   - Add to `~/.gemini/antigravity-ide/mcp_config.json`.
   - Add to `001_Architecture/Install_Maps/System-Map.md` and `TOOLBOX.md`.
6. **Task 6: Live Smoke Test**
   - From Claude Code, trigger a peer audit on a plan file.
   - Verify Slack channel receives formatted outputs from all three agents.

---

## 5. Security & Safety Guards

- **File Preservation Rule:** All workers inherit `fs_guard.py` rules—no agent may delete files or create arbitrary root directories.
- **Recursion Lock:** Workers pass `AGENT_OS_DELEGATE_WORKER=1` in environment to prevent recursive re-delegation loops.
- **Cost Ceilings:** Max tokens and timeout caps (e.g. 600s) on all delegated sub-processes.
