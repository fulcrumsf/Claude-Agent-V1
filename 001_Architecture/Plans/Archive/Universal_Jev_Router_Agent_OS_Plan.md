**Superseded by Option_B_Model_Routing_Plan.md (2026-09-27)**

# Universal Jev Router Architecture & Implementation Plan for Agent-OS

> **Status:** Pending Multi-Agent Audit (Claude Code $\rightarrow$ Codex $\rightarrow$ Opus Implementation)  
> **Target:** Seamless, cross-harness model routing and batch classification across **Claude Code**, **OpenAI Codex**, **Antigravity / Gemini CLI**, and workspace scripts.

---

## 1. Executive Vision: The Always-On Local AI Gateway

### The Core Problem
* **Token Inefficiency:** Running frontier models (Claude 3.5 Sonnet, Opus 3.5, Codex) on trivial requests (typos, docs lookups, status checks, batch folder triage) consumes massive tokens and triggers rate limits / 5-hour lockouts.
* **Harness Fragmentation:** Claude Code, OpenAI Codex, Antigravity, and bash scripts currently operate as separate runtimes with disconnected model configurations.
* **Manual Friction:** Manually typing `/model haiku` or switching models by hand interrupts flow and is rarely done consistently.

### The Solution: Universal Local Jev Gateway (`localhost:4000`)
A lightweight, zero-latency local daemon running in the background on your Mac that interfaces directly with TypeSafe AI's **Jev** via the OpenRouter API (`typesafe/jev-latest`). 

Because Jev provides **free output tokens ($0.00)** and costs only **$0.04 per 1M input tokens** with ~200ms heuristic classification, this gateway acts as an invisible, intelligent traffic cop for every AI agent operating in Agent-OS.

```
                    +---------------------------------------+
                    |           USER / HARNESSES            |
                    |  - Claude Code CLI                    |
                    |  - OpenAI Codex CLI                   |
                    |  - Antigravity IDE / Gemini CLI       |
                    |  - Workspace Python / Bash Scripts    |
                    +---------------------------------------+
                                        |
                                        v
                    +---------------------------------------+
                    |    UNIVERSAL LOCAL JEV GATEWAY        |
                    |         (localhost:4000)              |
                    |  - Health & Metrics                   |
                    |  - /route (Tier 1 / 2 / 3 Dispatch)   |
                    |  - /classify (choice, binary, score)  |
                    |  - Transparent Reverse Proxy Mode     |
                    +---------------------------------------+
                                        |
                 +----------------------+----------------------+
                 |                                             |
                 v (Snap Classification ~200ms)                v (Direct Fallback)
+------------------------------------+        +------------------------------------+
|       OPENROUTER / JEV             |        |         LOCAL HEURISTICS           |
|      (typesafe/jev-latest)         |        |   Deterministic regex / rules      |
+------------------------------------+        +------------------------------------+
                 |
                 +----------------------+----------------------+
                                        |
          +-----------------------------+-----------------------------+
          |                             |                             |
          v                             v                             v
     [ TIER 1 ]                    [ TIER 2 ]                    [ TIER 3 ]
   Rules / Local Cache          Fast Small Model              Frontier Agent
  - No AI, <1ms, $0.00         - Claude 3.5 Haiku            - Claude 3.5 Sonnet
  - Direct grep / files        - Luna / Local SLM            - Claude 3.5 Opus / Fable
  - Internal vault cmds        - "Quick summary / doc query" - OpenAI Codex
  - "Show my priorities"       - ~$0.0001 per call           - Deep multi-file coding
```

---

## 2. The 3-Tier Execution Framework

Every incoming request is categorized into one of three execution tiers:

| Tier | Category | Latency | Model / Engine | Cost per 1k Calls | Trigger Examples |
| :---: | :--- | :---: | :--- | :---: | :--- |
| **Tier 1** | **Deterministic / Rules** | `<1ms` | **Local Engine (No AI)** | **$0.00** | *"Where did we leave off?", "Show active directives", "Open terminal drawer", "Check pending ingest"* |
| **Tier 2** | **Lightweight Query** | `~300ms` | **Claude 3.5 Haiku / Luna** | **~$0.15** | *"Fix typo in line 42", "What is the syntax for ripgrep?", "Summarize today's 3 AI news items"* |
| **Tier 3** | **Deep Frontier Agent** | `3s–30s` | **Claude 3.5 Sonnet / Codex / Opus** | **~$3.00–$15.00** | *"Refactor auth middleware across 5 files", "Analyze YouTube tutorial keyframes", "Build new agent skill"* |

---

## 3. Harness Integration Blueprints

The gateway supports multiple integration modalities to ensure 100% compatibility across all tools:

### Harness A: Claude Code Integration
* **Primary Path (Pre-Flight Hook):**
  * Script: `001_Architecture/Scripts/jev_claude_hook.py` (or Node `router.mjs`).
  * Configuration: Added to workspace `.claude/settings.json` or global `~/.claude/settings.json`:
    ```json
    {
      "hooks": {
        "pre_prompt": "python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/jev_claude_hook.py"
      }
    }
    ```
  * **Behavior:** Before Claude evaluates a user turn, the hook sends the prompt to `http://localhost:4000/route`. If Tier 2, it dynamically swaps Claude's execution model to Haiku; if Tier 3, it preserves Sonnet/Opus.
  * **Interactive Controls:** Supports commands in chat:
    * `/jev on` — Activates dynamic routing (default).
    * `/jev off` — Locks Claude to the currently selected model.
    * `/jev status` — Displays routing history and estimated token savings.

* **Secondary Path (Transparent Proxy):**
  * Run Claude with `ANTHROPIC_BASE_URL=http://localhost:4000/v1`.
  * The gateway intercepts completions, calls Jev to inspect the message chain, rewrites the target `model` header to Haiku or Sonnet, and streams the response back transparently.

---

### Harness B: OpenAI Codex Integration
* **Integration Strategy:**
  * Codex uses a runner script or shell wrapper (`001_Architecture/Scripts/codex_router.py`) that proxies commands:
    ```bash
    codex-routed "prompt"
    ```
  * Or custom Codex agent instructions in `AGENTS.md` and `001_Architecture/Skills/codex-agent-os-hardening/SKILL.md` that instruct Codex to query `localhost:4000/route` when planning subagent dispatches.
  * For batch tasks, Codex offloads sub-steps to Jev via `POST http://localhost:4000/classify`.

---

### Harness C: Antigravity IDE & Gemini CLI Integration
* **Integration Strategy:**
  * Antigravity IDE and Gemini CLI share rules in `GEMINI.md` and global settings in `~/.gemini/settings.json`.
  * A custom tool or slash command helper queries `localhost:4000/classify` for high-speed categorization.
  * When performing multi-file scans or large-scale lint audits, Antigravity delegates file-filtering decisions to Jev rather than invoking frontier vision/reasoning models.

---

### Harness D: Batch Ingest Pipeline (`000_Ingest/`)
* **Dedicated Ingest Triage Script:** `001_Architecture/Scripts/jev_ingest_triage.py`.
* **Workflow:**
  1. Scans all raw documents in `000_Ingest/`.
  2. Calls `localhost:4000/classify` with:
     * `binary`: Is this document actionable content or junk/empty stub?
     * `choice`: Classify into target folder: `['Docs', 'Tools', 'Tutorials', 'Prompts', 'Investments', 'Research', 'Design_Inspiration', 'Personal']`.
     * `score`: Rate business utility from 1 to 10.
  3. Automatically drafts YAML frontmatter and routes files in seconds for pennies.

---

## 4. Technical Architecture of the Gateway Daemon

### Daemon Specifications
* **Runtime:** Lightweight Python FastAPI (`uvicorn`) or Node.js Express server.
* **Port:** `127.0.0.1:4000` (or configurable fallback `3456`).
* **Environment Variables:**
  * `OPENROUTER_API_KEY`: Read securely from `~/.zshrc` or `.env` (never hardcoded).
  * `JEV_MODEL`: `typesafe/jev-latest`.
  * `JEV_TIMEOUT_MS`: `800` (safety circuit breaker).
  * `JEV_DEFAULT_FALLBACK`: `claude-3-5-sonnet`.

### Core API Endpoints

#### 1. `GET /health`
* Returns status, uptime, OpenRouter connectivity, and token savings metrics:
  ```json
  {
    "status": "healthy",
    "gateway": "agent-os-jev-router",
    "port": 4000,
    "uptime_seconds": 14200,
    "total_routed_calls": 342,
    "tokens_saved_estimate": 485000,
    "cost_savings_usd": 7.28
  }
  ```

#### 2. `POST /route`
* Evaluates incoming user prompt and classifies target tier:
  * **Input:**
    ```json
    {
      "prompt": "fix the typo in line 12 of styles.css",
      "harness": "claude-code",
      "current_model": "claude-3-5-sonnet"
    }
    ```
  * **Output:**
    ```json
    {
      "tier": 2,
      "recommended_model": "claude-3-5-haiku",
      "latency_ms": 210,
      "reason": "Single-line syntax/typo fix; does not require frontier reasoning."
    }
    ```

#### 3. `POST /classify`
* Generic structured decision evaluation (the foundation of Jev):
  * **Input:**
    ```json
    {
      "text": "Full text or summary of an article...",
      "shape": "choice",
      "choices": ["Docs", "Tools", "Tutorials", "Prompts", "Investments"]
    }
    ```
  * **Output:**
    ```json
    {
      "result": "Tools",
      "confidence": 0.94,
      "probabilities": {
        "Tools": 0.94,
        "Tutorials": 0.04,
        "Docs": 0.02
      },
      "cost_usd": 0.000012
    }
    ```

---

## 5. macOS Service Management (`launchd`)

To make the router truly **always-on** without needing manual terminal commands every time Tony restarts his Mac:
* Create a macOS user launch agent:
  `~/Library/LaunchAgents/com.agentos.jevrouter.plist`
* Managed via standard CLI:
  ```bash
  launchctl load ~/Library/LaunchAgents/com.agentos.jevrouter.plist
  launchctl start com.agentos.jevrouter
  ```
* Automatically restarts on system boot, runs silently in the background, logs to `001_Architecture/Logs/jev_router.log`, and consumes minimal memory (~35MB RAM).

---

## 6. Safety, Fallbacks & Circuit Breakers

1. **Strict 800ms Timeout Gate:**
   * If OpenRouter does not respond within 800ms (due to network lag or API issues), the gateway instantly returns the default model (`claude-3-5-sonnet`). The user experience is never blocked.
2. **Context Window Safety:**
   * Jev only needs the last user message and lightweight system directives. The router strips massive diffs or images from the routing payload to keep latency sub-250ms and token costs near zero.
3. **Hard Override:**
   * If the user prompt explicitly specifies a model (e.g. *"Use Opus for this"* or *"Think deeply"*), the router bypasses Jev and immediately returns Tier 3 / Opus.

---

## 7. Multi-Agent Audit & Implementation Checklist

This checklist must be executed sequentially:

### Phase 1: Claude Code Audit
- [ ] Verify Claude Code hook execution compatibility in current version (`pre_prompt` vs. pre-flight wrapper).
- [ ] Test latency overhead of local HTTP call (`localhost:4000/route`) during interactive chat.
- [ ] Confirm `/jev on` and `/jev off` toggle states persist across conversation turns.

### Phase 2: OpenAI Codex Audit
- [ ] Audit Codex environment variable propagation and wrapper script behavior.
- [ ] Verify Codex can query `localhost:4000/classify` during subagent autonomous loops.
- [ ] Test fallbacks when gateway daemon is offline (fail-open to default model).

### Phase 3: Opus 5.5 / Frontier Implementation
- [ ] Build `001_Architecture/Scripts/jev_gateway.py` with FastAPI and OpenRouter connector.
- [ ] Build `001_Architecture/Scripts/jev_claude_hook.py` and test pre-flight routing.
- [ ] Build `001_Architecture/Scripts/jev_ingest_triage.py` for batch `000_Ingest/` classification.
- [ ] Install `com.agentos.jevrouter.plist` into `~/Library/LaunchAgents/`.
- [ ] Benchmark token spend and latency across 10 sample tasks.
- [ ] Update `TOOLBOX.md`, `System-Map.md`, and `001_Architecture/Memory/Global_Agent_Memory.md`.
