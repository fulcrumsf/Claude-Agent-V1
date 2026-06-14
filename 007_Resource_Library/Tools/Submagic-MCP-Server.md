---
title: "Submagic MCP Server"
type: tool-doc
category: ai-agents
tags:
  - mcp
  - ai-agents
  - video-editing
created: 2026-05-08
source: local
---

Submagic exposes an [MCP](https://modelcontextprotocol.io/) -compatible endpoint at `POST https://api.submagic.co/mcp`. Connect from Claude Code, Claude Desktop, Cursor, or any MCP client to drive Submagic from inside your AI assistant.

## Authentication

Pass your existing Submagic API key as a Bearer token:

```http
Authorization: Bearer sk-your-api-key-here
```

The same key and credits that work for the REST API work for MCP. If you don’t have a key yet, generate one from your [account settings](https://app.submagic.co/user).

## Connecting Clients

### Claude Code

```shellscript
claude mcp add --transport http submagic https://api.submagic.co/mcp \
  --header "Authorization: Bearer $SUBMAGIC_API_KEY"
```

### Claude Desktop

Claude Desktop’s config file doesn’t speak HTTP transport directly, so we use the [`mcp-remote`](https://www.npmjs.com/package/mcp-remote) bridge.

Requires Node.js **20.18+** installed locally so `npx` can run `mcp-remote`.

To open the config file, go to **Claude → Settings → Developer → Edit Config**. Add the following:

- macOS / Linux
- Windows

```json
{
  "mcpServers": {
    "submagic": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://api.submagic.co/mcp",
        "--header",
        "Authorization: Bearer YOUR_API_KEY_HERE"
      ]
    }
  }
}
```

Save, then fully quit and reopen Claude Desktop. Submagic tools will appear under the hammer icon at the bottom of the chat.

### Cursor / Windsurf

Configure an HTTP MCP server pointing at `https://api.submagic.co/mcp` with the header:

```http
Authorization: Bearer YOUR_API_KEY_HERE
```

### claude.ai web (Custom Connectors)

Currently unsupported — claude.ai’s Custom Connectors require OAuth, not Bearer tokens. Use Claude Code, Claude Desktop, Cursor, or Windsurf for now.

## Example Prompts

Once connected, you can ask your assistant things like:

- “Create a Submagic project from this URL.”
- “Turn this YouTube video into Submagic Magic Clips.”
- “Show me the status of my recent Submagic projects.”
- “Export Submagic project `[id]` and publish it to TikTok and Instagram.”
- “List my published Submagic projects from the last week with their views.”
- “Add background music to Submagic project `[id]`.”
- “What Submagic caption templates are available?”