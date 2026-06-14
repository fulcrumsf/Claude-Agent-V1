---
title: "DeerFlow 2 Enhanced"
type: tool-doc
category: ai-agents
tags:
  - ai-agents
  - deerflow
  - open-source
created: 2026-05-08
source: local
---

## 🦌 DeerFlow - 2.0

English | [中文](https://github.com/stophobia/deerflow2.0-enhanced/blob/main/README_zh.md) | [日本語](https://github.com/stophobia/deerflow2.0-enhanced/blob/main/README_ja.md)

[![bytedance%2Fdeer-flow | Trendshift](https://camo.githubusercontent.com/835ea254dc5caba36e1d1893d42771368fc1019fccb4cc1b927fc61eaaccc47a/68747470733a2f2f7472656e6473686966742e696f2f6170692f62616467652f7265706f7369746f726965732f3134363939)](https://trendshift.io/repositories/14699)

> On February 28th, 2026, DeerFlow claimed the 🏆 #1 spot on GitHub Trending following the launch of version 2. Thanks a million to our incredible community — you made this happen! 💪🔥

DeerFlow (**D** eep **E** xploration and **E** fficient **R** esearch **Flow**) is an open-source **super agent harness** that orchestrates **sub-agents**, **memory**, and **sandboxes** to do almost anything — powered by **extensible skills**.

deer-flow-720p.mp4<video src="https://private-user-images.githubusercontent.com/1003147/549895495-a8bcadc4-e040-4cf2-8fda-dd768b999c18.mp4?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzgxMTg0MDUsIm5iZiI6MTc3ODExODEwNSwicGF0aCI6Ii8xMDAzMTQ3LzU0OTg5NTQ5NS1hOGJjYWRjNC1lMDQwLTRjZjItOGZkYS1kZDc2OGI5OTljMTgubXA0P1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI2MDUwNyUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNjA1MDdUMDE0MTQ1WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9YjAyZDMwZGFjOWQ3ODA0NWY0YzkxMDE3MzZmYzI0MjdmOWJmMGNkOWJhYjlkM2RlZjI1OTdlZDM0ODY2M2EyZCZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmcmVzcG9uc2UtY29udGVudC10eXBlPXZpZGVvJTJGbXA0In0.T3qVnmTI-4BE2QBaRCvhELbYRtM6pyJaKiqN-S8FCFU" controls="controls"></video>

> [!note] Note
> **DeerFlow 2.0 is a ground-up rewrite.** It shares no code with v1. If you're looking for the original Deep Research framework, it's maintained on the [`1.x` branch](https://github.com/bytedance/deer-flow/tree/main-1.x) — contributions there are still welcome. Active development has moved to 2.0.

## Official Website

[![image](https://private-user-images.githubusercontent.com/1003147/564580564-a598c49f-3b2f-41ea-a052-05e21349188a.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzgxMTg0MDUsIm5iZiI6MTc3ODExODEwNSwicGF0aCI6Ii8xMDAzMTQ3LzU2NDU4MDU2NC1hNTk4YzQ5Zi0zYjJmLTQxZWEtYTA1Mi0wNWUyMTM0OTE4OGEucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI2MDUwNyUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNjA1MDdUMDE0MTQ1WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9YzlmMWYyYjVkMzk4YWIzN2U2ZmY2MDAyMGM3ZDdhOWJhYjgwNjUxYTJmODI4ZGU4OGFlN2UzNTBkYWRmYWQ5YyZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmcmVzcG9uc2UtY29udGVudC10eXBlPWltYWdlJTJGcG5nIn0.Vvy8JACPLF3hUTq7lFkrlxay0r7yNa4cJYPd8sVeG7w)](https://deerflow.tech/)

Learn more and see **real demos** on our [**official website**](https://deerflow.tech/).

## Coding Plan from ByteDance Volcengine

[![英文方舟](https://private-user-images.githubusercontent.com/1003147/564581194-2ecc7b9d-50be-4185-b1f7-5542d222fb2d.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzgxMTg0MDUsIm5iZiI6MTc3ODExODEwNSwicGF0aCI6Ii8xMDAzMTQ3LzU2NDU4MTE5NC0yZWNjN2I5ZC01MGJlLTQxODUtYjFmNy01NTQyZDIyMmZiMmQucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI2MDUwNyUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNjA1MDdUMDE0MTQ1WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9ZjlkNTBmYmQ5NTZhYWEzNjVjYzE4ZGQ3MGRhY2RiYTQ3MjlhODZhNWIwM2U4YTYzNDdlZTUwYmYyMTI1YjgyOCZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmcmVzcG9uc2UtY29udGVudC10eXBlPWltYWdlJTJGcG5nIn0.-PRGTMuivGVPGH4Jx2R-o1_TDLtYV7P9vat0qicgdE4)](https://private-user-images.githubusercontent.com/1003147/564581194-2ecc7b9d-50be-4185-b1f7-5542d222fb2d.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzgxMTg0MDUsIm5iZiI6MTc3ODExODEwNSwicGF0aCI6Ii8xMDAzMTQ3LzU2NDU4MTE5NC0yZWNjN2I5ZC01MGJlLTQxODUtYjFmNy01NTQyZDIyMmZiMmQucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI2MDUwNyUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNjA1MDdUMDE0MTQ1WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9ZjlkNTBmYmQ5NTZhYWEzNjVjYzE4ZGQ3MGRhY2RiYTQ3MjlhODZhNWIwM2U4YTYzNDdlZTUwYmYyMTI1YjgyOCZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmcmVzcG9uc2UtY29udGVudC10eXBlPWltYWdlJTJGcG5nIn0.-PRGTMuivGVPGH4Jx2R-o1_TDLtYV7P9vat0qicgdE4)
- We strongly recommend using Doubao-Seed-2.0-Code, DeepSeek v3.2 and Kimi 2.5 to run DeerFlow
- [Learn more](https://www.byteplus.com/en/activity/codingplan?utm_campaign=deer_flow&utm_content=deer_flow&utm_medium=devrel&utm_source=OWO&utm_term=deer_flow)
- [中国大陆地区的开发者请点击这里](https://www.volcengine.com/activity/codingplan?utm_campaign=deer_flow&utm_content=deer_flow&utm_medium=devrel&utm_source=OWO&utm_term=deer_flow)

## InfoQuest

DeerFlow has newly integrated the intelligent search and crawling toolset independently developed by BytePlus-- [InfoQuest (supports free online experience)](https://docs.byteplus.com/en/docs/InfoQuest/What_is_Info_Quest)

[![InfoQuest_banner](https://camo.githubusercontent.com/cbeffc44223167814246ed9f291065763889c0e67a1708d7c0844ab855a2a14d/68747470733a2f2f736631362d73672e74696b746f6b63646e2e636f6d2f6f626a2f6564656e2d73672f6875627365683762736270732f32303235313230382d3136303130382e706e67)](https://docs.byteplus.com/en/docs/InfoQuest/What_is_Info_Quest)

---

## Table of Contents

## Quick Start

### Configuration

1. **Clone the DeerFlow repository**
	```
	git clone https://github.com/bytedance/deer-flow.git
	cd deer-flow
	```
2. **Generate local configuration files**
	From the project root directory (`deer-flow/`), run:
	```
	make config
	```
	This command creates local configuration files based on the provided example templates.
3. **Configure your preferred model(s)**
	Edit `config.yaml` and define at least one model:
	```
	models:
	  - name: gpt-4                       # Internal identifier
	    display_name: GPT-4               # Human-readable name
	    use: langchain_openai:ChatOpenAI  # LangChain class path
	    model: gpt-4                      # Model identifier for API
	    api_key: $OPENAI_API_KEY          # API key (recommended: use env var)
	    max_tokens: 4096                  # Maximum tokens per request
	    temperature: 0.7                  # Sampling temperature
	  - name: openrouter-gemini-2.5-flash
	    display_name: Gemini 2.5 Flash (OpenRouter)
	    use: langchain_openai:ChatOpenAI
	    model: google/gemini-2.5-flash-preview
	    api_key: $OPENAI_API_KEY          # OpenRouter still uses the OpenAI-compatible field name here
	    base_url: https://openrouter.ai/api/v1
	  - name: gpt-5-responses
	    display_name: GPT-5 (Responses API)
	    use: langchain_openai:ChatOpenAI
	    model: gpt-5
	    api_key: $OPENAI_API_KEY
	    use_responses_api: true
	    output_version: responses/v1
	```
	OpenRouter and similar OpenAI-compatible gateways should be configured with `langchain_openai:ChatOpenAI` plus `base_url`. If you prefer a provider-specific environment variable name, point `api_key` at that variable explicitly (for example `api_key: $OPENROUTER_API_KEY`).
	To route OpenAI models through `/v1/responses`, keep using `langchain_openai:ChatOpenAI` and set `use_responses_api: true` with `output_version: responses/v1`.
	CLI-backed provider examples:
	```
	models:
	  - name: gpt-5.4
	    display_name: GPT-5.4 (Codex CLI)
	    use: deerflow.models.openai_codex_provider:CodexChatModel
	    model: gpt-5.4
	    supports_thinking: true
	    supports_reasoning_effort: true
	  - name: claude-sonnet-4.6
	    display_name: Claude Sonnet 4.6 (Claude Code OAuth)
	    use: deerflow.models.claude_provider:ClaudeChatModel
	    model: claude-sonnet-4-6
	    max_tokens: 4096
	    supports_thinking: true
	```
	- Codex CLI reads `~/.codex/auth.json`
		- The Codex Responses endpoint currently rejects `max_tokens` and `max_output_tokens`, so `CodexChatModel` does not expose a request-level token cap
		- Claude Code accepts `CLAUDE_CODE_OAUTH_TOKEN`, `ANTHROPIC_AUTH_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN_FILE_DESCRIPTOR`, `CLAUDE_CODE_CREDENTIALS_PATH`, or plaintext `~/.claude/.credentials.json`
		- On macOS, DeerFlow does not probe Keychain automatically. Export Claude Code auth explicitly if needed:
	```
	eval "$(python3 scripts/export_claude_code_oauth.py --print-export)"
	```
4. **Set API keys for your configured model(s)**
	Choose one of the following methods:
- Option A: Edit the `.env` file in the project root (Recommended)
	```
	TAVILY_API_KEY=your-tavily-api-key
	OPENAI_API_KEY=your-openai-api-key
	# OpenRouter also uses OPENAI_API_KEY when your config uses langchain_openai:ChatOpenAI + base_url.
	# Add other provider keys as needed
	INFOQUEST_API_KEY=your-infoquest-api-key
	```
- Option B: Export environment variables in your shell
	```
	export OPENAI_API_KEY=your-openai-api-key
	```
	For CLI-backed providers:
	- Codex CLI: `~/.codex/auth.json`
		- Claude Code OAuth: explicit env/file handoff or `~/.claude/.credentials.json`
- Option C: Edit `config.yaml` directly (Not recommended for production)
	```
	models:
	  - name: gpt-4
	    api_key: your-actual-api-key-here  # Replace placeholder
	```

### Running the Application

**Development** (hot-reload, source mounts):

```
make docker-init    # Pull sandbox image (only once or when image updates)
make docker-start   # Start services (auto-detects sandbox mode from config.yaml)
```

`make docker-start` starts `provisioner` only when `config.yaml` uses provisioner mode (`sandbox.use: deerflow.community.aio_sandbox:AioSandboxProvider` with `provisioner_url`). Backend processes automatically pick up `config.yaml` changes on the next config access, so model metadata updates do not require a manual restart during development.

**Production** (builds images locally, mounts runtime config and data):

```
make up     # Build images and start all production services
make down   # Stop and remove containers
```

> [!note] Note
> The LangGraph agent server currently runs via `langgraph dev` (the open-source CLI server).

Access: [http://localhost:2026](http://localhost:2026/)

See [CONTRIBUTING.md](https://github.com/stophobia/deerflow2.0-enhanced/blob/main/CONTRIBUTING.md) for detailed Docker development guide.

#### Option 2: Local Development

If you prefer running services locally:

Prerequisite: complete the "Configuration" steps above first (`make config` and model API keys). `make dev` requires a valid configuration file (defaults to `config.yaml` in the project root; can be overridden via `DEER_FLOW_CONFIG_PATH`).

1. **Check prerequisites**:
	```
	make check  # Verifies Node.js 22+, pnpm, uv, nginx
	```
2. **Install dependencies**:
	```
	make install  # Install backend + frontend dependencies
	```
3. **(Optional) Pre-pull sandbox image**:
	```
	# Recommended if using Docker/Container-based sandbox
	make setup-sandbox
	```
4. **Start services**:
	```
	make dev
	```
5. **Access**: [http://localhost:2026](http://localhost:2026/)

### Advanced

#### Sandbox Mode

DeerFlow supports multiple sandbox execution modes:

- **Local Execution** (runs sandbox code directly on the host machine)
- **Docker Execution** (runs sandbox code in isolated Docker containers)
- **Docker Execution with Kubernetes** (runs sandbox code in Kubernetes pods via provisioner service)

For Docker development, service startup follows `config.yaml` sandbox mode. In Local/Docker modes, `provisioner` is not started.

See the [Sandbox Configuration Guide](https://github.com/stophobia/deerflow2.0-enhanced/blob/main/backend/docs/CONFIGURATION.md#sandbox) to configure your preferred mode.

#### MCP Server

DeerFlow supports configurable MCP servers and skills to extend its capabilities. For HTTP/SSE MCP servers, OAuth token flows are supported (`client_credentials`, `refresh_token`). See the [MCP Server Guide](https://github.com/stophobia/deerflow2.0-enhanced/blob/main/backend/docs/MCP_SERVER.md) for detailed instructions.

#### IM Channels

DeerFlow supports receiving tasks from messaging apps. Channels auto-start when configured — no public IP required for any of them.

| Channel | Transport | Difficulty |
| --- | --- | --- |
| Telegram | Bot API (long-polling) | Easy |
| Slack | Socket Mode | Moderate |
| Feishu / Lark | WebSocket | Moderate |

**Configuration in `config.yaml`:**

```
channels:
  # LangGraph Server URL (default: http://localhost:2024)
  langgraph_url: http://localhost:2024
  # Gateway API URL (default: http://localhost:8001)
  gateway_url: http://localhost:8001

  # Optional: global session defaults for all mobile channels
  session:
    assistant_id: lead_agent
    config:
      recursion_limit: 100
    context:
      thinking_enabled: true
      is_plan_mode: false
      subagent_enabled: false

  feishu:
    enabled: true
    app_id: $FEISHU_APP_ID
    app_secret: $FEISHU_APP_SECRET

  slack:
    enabled: true
    bot_token: $SLACK_BOT_TOKEN     # xoxb-...
    app_token: $SLACK_APP_TOKEN     # xapp-... (Socket Mode)
    allowed_users: []               # empty = allow all

  telegram:
    enabled: true
    bot_token: $TELEGRAM_BOT_TOKEN
    allowed_users: []               # empty = allow all

    # Optional: per-channel / per-user session settings
    session:
      assistant_id: mobile_agent
      context:
        thinking_enabled: false
      users:
        "123456789":
          assistant_id: vip_agent
          config:
            recursion_limit: 150
          context:
            thinking_enabled: true
            subagent_enabled: true
```

Set the corresponding API keys in your `.env` file:

```
# Telegram
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ

# Slack
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...

# Feishu / Lark
FEISHU_APP_ID=cli_xxxx
FEISHU_APP_SECRET=your_app_secret
```

**Telegram Setup**

1. Chat with [@BotFather](https://t.me/BotFather), send `/newbot`, and copy the HTTP API token.
2. Set `TELEGRAM_BOT_TOKEN` in `.env` and enable the channel in `config.yaml`.

**Slack Setup**

1. Create a Slack App at [api.slack.com/apps](https://api.slack.com/apps) → Create New App → From scratch.
2. Under **OAuth & Permissions**, add Bot Token Scopes: `app_mentions:read`, `chat:write`, `im:history`, `im:read`, `im:write`, `files:write`.
3. Enable **Socket Mode** → generate an App-Level Token (`xapp-…`) with `connections:write` scope.
4. Under **Event Subscriptions**, subscribe to bot events: `app_mention`, `message.im`.
5. Set `SLACK_BOT_TOKEN` and `SLACK_APP_TOKEN` in `.env` and enable the channel in `config.yaml`.

**Feishu / Lark Setup**

1. Create an app on [Feishu Open Platform](https://open.feishu.cn/) → enable **Bot** capability.
2. Add permissions: `im:message`, `im:message.p2p_msg:readonly`, `im:resource`.
3. Under **Events**, subscribe to `im.message.receive_v1` and select **Long Connection** mode.
4. Copy the App ID and App Secret. Set `FEISHU_APP_ID` and `FEISHU_APP_SECRET` in `.env` and enable the channel in `config.yaml`.

**Commands**

Once a channel is connected, you can interact with DeerFlow directly from the chat:

| Command | Description |
| --- | --- |
| `/new` | Start a new conversation |
| `/status` | Show current thread info |
| `/models` | List available models |
| `/memory` | View memory |
| `/help` | Show help |

> Messages without a command prefix are treated as regular chat — DeerFlow creates a thread and responds conversationally.

## From Deep Research to Super Agent Harness

DeerFlow started as a Deep Research framework — and the community ran with it. Since launch, developers have pushed it far beyond research: building data pipelines, generating slide decks, spinning up dashboards, automating content workflows. Things we never anticipated.

That told us something important: DeerFlow wasn't just a research tool. It was a **harness** — a runtime that gives agents the infrastructure to actually get work done.

So we rebuilt it from scratch.

DeerFlow 2.0 is no longer a framework you wire together. It's a super agent harness — batteries included, fully extensible. Built on LangGraph and LangChain, it ships with everything an agent needs out of the box: a filesystem, memory, skills, sandboxed execution, and the ability to plan and spawn sub-agents for complex, multi-step tasks.

Use it as-is. Or tear it apart and make it yours.

## Core Features

### Skills & Tools

Skills are what make DeerFlow do *almost anything*.

A standard Agent Skill is a structured capability module — a Markdown file that defines a workflow, best practices, and references to supporting resources. DeerFlow ships with built-in skills for research, report generation, slide creation, web pages, image and video generation, and more. But the real power is extensibility: add your own skills, replace the built-in ones, or combine them into compound workflows.

Skills are loaded progressively — only when the task needs them, not all at once. This keeps the context window lean and makes DeerFlow work well even with token-sensitive models.

When you install `.skill` archives through the Gateway, DeerFlow accepts standard optional frontmatter metadata such as `version`, `author`, and `compatibility` instead of rejecting otherwise valid external skills.

Tools follow the same philosophy. DeerFlow comes with a core toolset — web search, web fetch, file operations, bash execution — and supports custom tools via MCP servers and Python functions. Swap anything. Add anything.

Gateway-generated follow-up suggestions now normalize both plain-string model output and block/list-style rich content before parsing the JSON array response, so provider-specific content wrappers do not silently drop suggestions.

```
# Paths inside the sandbox container
/mnt/skills/public
├── research/SKILL.md
├── report-generation/SKILL.md
├── slide-creation/SKILL.md
├── web-page/SKILL.md
└── image-generation/SKILL.md

/mnt/skills/custom
└── your-custom-skill/SKILL.md      ← yours
```

#### Claude Code Integration

The `claude-to-deerflow` skill lets you interact with a running DeerFlow instance directly from [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Send research tasks, check status, manage threads — all without leaving the terminal.

**Install the skill**:

```
npx skills add https://github.com/bytedance/deer-flow --skill claude-to-deerflow
```

Then make sure DeerFlow is running (default at `http://localhost:2026`) and use the `/claude-to-deerflow` command in Claude Code.

**What you can do**:

- Send messages to DeerFlow and get streaming responses
- Choose execution modes: flash (fast), standard, pro (planning), ultra (sub-agents)
- Check DeerFlow health, list models/skills/agents
- Manage threads and conversation history
- Upload files for analysis

**Environment variables** (optional, for custom endpoints):

```
DEERFLOW_URL=http://localhost:2026            # Unified proxy base URL
DEERFLOW_GATEWAY_URL=http://localhost:2026    # Gateway API
DEERFLOW_LANGGRAPH_URL=http://localhost:2026/api/langgraph  # LangGraph API
```

See [`skills/public/claude-to-deerflow/SKILL.md`](https://github.com/stophobia/deerflow2.0-enhanced/blob/main/skills/public/claude-to-deerflow/SKILL.md) for the full API reference.

### Sub-Agents

Complex tasks rarely fit in a single pass. DeerFlow decomposes them.

The lead agent can spawn sub-agents on the fly — each with its own scoped context, tools, and termination conditions. Sub-agents run in parallel when possible, report back structured results, and the lead agent synthesizes everything into a coherent output.

This is how DeerFlow handles tasks that take minutes to hours: a research task might fan out into a dozen sub-agents, each exploring a different angle, then converge into a single report — or a website — or a slide deck with generated visuals. One harness, many hands.

### Sandbox & File System

DeerFlow doesn't just *talk* about doing things. It has its own computer.

Each task runs inside an isolated Docker container with a full filesystem — skills, workspace, uploads, outputs. The agent reads, writes, and edits files. It executes bash commands and codes. It views images. All sandboxed, all auditable, zero contamination between sessions.

This is the difference between a chatbot with tool access and an agent with an actual execution environment.

```
# Paths inside the sandbox container
/mnt/user-data/
├── uploads/          ← your files
├── workspace/        ← agents' working directory
└── outputs/          ← final deliverables
```

### Context Engineering

**Isolated Sub-Agent Context**: Each sub-agent runs in its own isolated context. This means that the sub-agent will not be able to see the context of the main agent or other sub-agents. This is important to ensure that the sub-agent is able to focus on the task at hand and not be distracted by the context of the main agent or other sub-agents.

**Summarization**: Within a session, DeerFlow manages context aggressively — summarizing completed sub-tasks, offloading intermediate results to the filesystem, compressing what's no longer immediately relevant. This lets it stay sharp across long, multi-step tasks without blowing the context window.

### Long-Term Memory

Most agents forget everything the moment a conversation ends. DeerFlow remembers.

Across sessions, DeerFlow builds a persistent memory of your profile, preferences, and accumulated knowledge. The more you use it, the better it knows you — your writing style, your technical stack, your recurring workflows. Memory is stored locally and stays under your control.

Memory updates now skip duplicate fact entries at apply time, so repeated preferences and context do not accumulate endlessly across sessions.

## Recommended Models

DeerFlow is model-agnostic — it works with any LLM that implements the OpenAI-compatible API. That said, it performs best with models that support:

- **Long context windows** (100k+ tokens) for deep research and multi-step tasks
- **Reasoning capabilities** for adaptive planning and complex decomposition
- **Multimodal inputs** for image understanding and video comprehension
- **Strong tool-use** for reliable function calling and structured outputs

## Embedded Python Client

DeerFlow can be used as an embedded Python library without running the full HTTP services. The `DeerFlowClient` provides direct in-process access to all agent and Gateway capabilities, returning the same response schemas as the HTTP Gateway API:

```
from deerflow.client import DeerFlowClient

client = DeerFlowClient()

# Chat
response = client.chat("Analyze this paper for me", thread_id="my-thread")

# Streaming (LangGraph SSE protocol: values, messages-tuple, end)
for event in client.stream("hello"):
    if event.type == "messages-tuple" and event.data.get("type") == "ai":
        print(event.data["content"])

# Configuration & management — returns Gateway-aligned dicts
models = client.list_models()        # {"models": [...]}
skills = client.list_skills()        # {"skills": [...]}
client.update_skill("web-search", enabled=True)
client.upload_files("thread-1", ["./report.pdf"])  # {"success": True, "files": [...]}
```

All dict-returning methods are validated against Gateway Pydantic response models in CI (`TestGatewayConformance`), ensuring the embedded client stays in sync with the HTTP API schemas. See `backend/packages/harness/deerflow/client.py` for full API documentation.

## Documentation

- [Contributing Guide](https://github.com/stophobia/deerflow2.0-enhanced/blob/main/CONTRIBUTING.md) - Development environment setup and workflow
- [Configuration Guide](https://github.com/stophobia/deerflow2.0-enhanced/blob/main/backend/docs/CONFIGURATION.md) - Setup and configuration instructions
- [Architecture Overview](https://github.com/stophobia/deerflow2.0-enhanced/blob/main/backend/CLAUDE.md) - Technical architecture details
- [Backend Architecture](https://github.com/stophobia/deerflow2.0-enhanced/blob/main/backend/README.md) - Backend architecture and API reference

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](https://github.com/stophobia/deerflow2.0-enhanced/blob/main/CONTRIBUTING.md) for development setup, workflow, and guidelines.

Regression coverage includes Docker sandbox mode detection and provisioner kubeconfig-path handling tests in `backend/tests/`.

## License

This project is open source and available under the [MIT License](https://github.com/stophobia/deerflow2.0-enhanced/blob/main/LICENSE).

## Acknowledgments

DeerFlow is built upon the incredible work of the open-source community. We are deeply grateful to all the projects and contributors whose efforts have made DeerFlow possible. Truly, we stand on the shoulders of giants.

We would like to extend our sincere appreciation to the following projects for their invaluable contributions:

- **[LangChain](https://github.com/langchain-ai/langchain)**: Their exceptional framework powers our LLM interactions and chains, enabling seamless integration and functionality.
- **[LangGraph](https://github.com/langchain-ai/langgraph)**: Their innovative approach to multi-agent orchestration has been instrumental in enabling DeerFlow's sophisticated workflows.

These projects exemplify the transformative power of open-source collaboration, and we are proud to build upon their foundations.

### Key Contributors

A heartfelt thank you goes out to the core authors of `DeerFlow`, whose vision, passion, and dedication have brought this project to life:

- **[Daniel Walnut](https://github.com/hetaoBackend/)**
- **[Henry Li](https://github.com/magiccube/)**

Your unwavering commitment and expertise have been the driving force behind DeerFlow's success. We are honored to have you at the helm of this journey.

[![Star History Chart](https://camo.githubusercontent.com/18c9e9fbfb3d3e4a7308b73d8c35580eee189b9bec2f140257ff68be672d206f/68747470733a2f2f6170692e737461722d686973746f72792e636f6d2f7376673f7265706f733d6279746564616e63652f646565722d666c6f7726747970653d44617465)](https://star-history.com/#bytedance/deer-flow&Date)