---
title: "MCP Gateway Controller"
type: doc
domain: app-dev
tags: [doc, app-dev, automation, ai-agents]
---

# MCP Gateway Controller

A unified system for managing all MCP servers, plugins, and skills across your development environment (Anti-Gravity, Claude Code, VS Code, etc.).

## Features

- **Single Gateway Server** — One local MCP router on port 3003
- **Web Dashboard** — Beautiful dark-themed interface for toggling MCPs
- **Group Management** — Organize MCPs by category (Design, Video, Audio, etc.)
- **Centralized Secrets** — All API keys in `~/.env-secrets.env`
- **CLI vs MCP Strategy** — Identifies when to use CLI tools vs MCPs for token efficiency
- **Real-time Toggles** — Instantly enable/disable MCPs and groups

## Architecture

- **Backend:** Node.js + Express + TypeScript on port 3003
- **Frontend:** React + Vite + Tailwind CSS
- **Configuration:** `~/.mcp-gateway/config.json` (MCP definitions)
- **State:** `~/.mcp-gateway/state.json` (toggle state)
- **Secrets:** `~/.env-secrets.env` (all API keys)

## Supported MCPs

- **Publishing:** blotato
- **Design:** stitch
- **Video:** remotion
- **Audio:** elevenlabs
- **Data:** notion
- **Research:** perplexity
- **Documentation:** context7
- **Automation:** n8n-mcp
- **Browser:** playwright (CLI preferred)

## Quick Start

See [SETUP.md](./SETUP.md) for installation instructions.

## Project Structure

```
MCP-Gateway-Controller/
├── server/                    # Express backend
│   ├── src/
│   │   ├── index.ts          # Server entry point
│   │   ├── config.ts         # Config loading
│   │   ├── types.ts          # TypeScript interfaces
│   │   └── routes/api.ts     # API endpoints
│   ├── tests/
│   │   └── integration.test.ts
│   ├── package.json
│   └── tsconfig.json
├── dashboard/                 # React frontend
│   ├── src/
│   │   ├── main.tsx          # Vite entry point
│   │   ├── App.tsx           # Main component
│   │   ├── index.css         # Global styles
│   │   └── hooks/useMCPs.ts  # API hook
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── DESIGN.md                  # Architecture spec
└── PLAN.md                    # Implementation plan
```

## Development

```bash
# Start server
cd server
npm install
npm run dev

# Start dashboard (in another terminal)
cd dashboard
npm install
npm run dev

# Visit http://localhost:5173 (dashboard proxies /api to server)
```

## Configuration

See [SETUP.md](./SETUP.md) for detailed configuration instructions.
