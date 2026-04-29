---
title: "MCP Gateway Controller — Setup Guide"
type: tutorial
domain: app-dev
tags: [tutorial, app-dev, automation]
---

# MCP Gateway Controller — Setup Guide

## Prerequisites

- Node.js 18+ installed
- `~/.env-secrets.env` file with your API keys
- Existing MCP server URLs or CLI tools available

## Installation

### 1. Create Configuration Directory

```bash
mkdir -p ~/.mcp-gateway
```

### 2. Create ~/.mcp-gateway/config.json

```json
{
  "port": 3003,
  "groups": {
    "Publishing": ["blotato"],
    "Design": ["stitch"],
    "Video": ["remotion"],
    "Audio": ["elevenlabs"],
    "Data": ["notion"],
    "Research": ["perplexity"],
    "Documentation": ["context7"],
    "Automation": ["n8n-mcp"],
    "Browser": ["playwright"]
  },
  "mcpServers": {
    "blotato": {
      "serverURL": "https://mcp.blotato.com/mcp",
      "headers": {
        "blotato-api-key": "${BLOTATO_API_KEY}"
      }
    },
    "stitch": {
      "serverURL": "https://stitch.googleapis.com/mcp",
      "headers": {
        "X-Goog-Api-Key": "${STITCH_API_KEY}"
      }
    },
    "n8n-mcp": {
      "serverURL": "https://n8n.robottogato.com/mcp-server/http",
      "headers": {
        "Authorization": "Bearer ${N8N_MCP_TOKEN}"
      }
    },
    "remotion": {
      "command": "npx",
      "args": ["-y", "@remotion/mcp@latest"]
    },
    "elevenlabs": {
      "command": "uvx",
      "args": ["elevenlabs-mcp"]
    },
    "notion": {
      "command": "uvx",
      "args": ["notion-mcp"]
    },
    "perplexity": {
      "command": "uvx",
      "args": ["perplexity-mcp"]
    },
    "context7": {
      "command": "uvx",
      "args": ["context7-mcp"]
    },
    "playwright": {
      "cli": true,
      "installed": true,
      "command": "playwright"
    }
  }
}
```

### 3. Create ~/.env-secrets.env

```bash
BLOTATO_API_KEY=your_key_here
STITCH_API_KEY=your_key_here
N8N_MCP_TOKEN=your_token_here
ELEVENLABS_API_KEY=your_key_here
NOTION_API_KEY=your_key_here
PERPLEXITY_API_KEY=your_key_here
CONTEXT7_API_KEY=your_key_here
```

### 4. Install and Start Server

```bash
cd server
npm install
npm run dev
# Server runs on http://localhost:3003
```

### 5. Install and Start Dashboard

```bash
cd dashboard
npm install
npm run dev
# Dashboard runs on http://localhost:5173
```

### 6. Access Dashboard

Visit `http://localhost:5173` in your browser.

## Integration with Anti-Gravity

Add to your Anti-Gravity configuration (`~/.gemini/antigravity/mcp_config.json`):

```json
{
  "mcpServers": {
    "gateway": {
      "serverURL": "http://localhost:3003"
    }
  }
}
```

## Integration with Claude Code

Add to your Claude Code configuration (`~/.claude/.mcp.json`):

```json
{
  "mcpServers": {
    "gateway": {
      "serverURL": "http://localhost:3003"
    }
  }
}
```

## Troubleshooting

### Config file not found error
- Ensure `~/.mcp-gateway/config.json` exists and is valid JSON
- Check file permissions: `ls -la ~/.mcp-gateway/`

### API endpoints return empty
- Verify config.json has proper MCP definitions
- Check that secrets in `~/.env-secrets.env` are correct
- Ensure server is running on port 3003

### Dashboard won't connect to server
- Check that server is running: `curl http://localhost:3003/health`
- Verify dashboard is running on port 5173
- Check browser console for CORS or network errors

### API key interpolation not working
- Verify key names in config.json match `~/.env-secrets.env`
- Use format: `${KEY_NAME}` in config headers
- Restart server after changing secrets

## Next Steps

1. Configure your Anti-Gravity or Claude Code to use the gateway
2. Toggle MCPs on/off in the dashboard
3. Monitor logs for any connection issues
4. Phase 2: Add health checks and usage analytics
