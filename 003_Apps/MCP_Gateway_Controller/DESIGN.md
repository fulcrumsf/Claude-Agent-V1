---
title: "MCP Gateway Controller — Design Specification"
type: spec
domain: app-dev
tags: [spec, app-dev, automation, design]
---

# MCP Gateway Controller — Design Specification

**Date:** 2026-04-07  
**Status:** Design Phase  
**Owner:** Tony

---

## Overview

The **MCP Gateway Controller** is a unified system for managing all MCP servers, plugins, and skills across your development environment (Anti-Gravity, Claude Code, VS Code, etc.). Instead of scattered configurations, you'll have:

- **One local gateway server** that routes all MCP connections
- **Beautiful web dashboard** (localhost) for toggling MCPs on/off by group
- **Consolidated inventory** of all available tools (MCPs, plugins, skills)
- **Centralized secrets** via `~/.env-secrets.env`

---

## Architecture

### Core Components

1. **Gateway Server** (Node.js + Express)
   - Runs on port **3003** (3000 = Docker, 3002 = Remotion)
   - Routes all MCP requests through single endpoint
   - Reads configuration from `~/.mcp-gateway/config.json`
   - Loads secrets from `~/.env-secrets.env`
   - Manages on/off state for each MCP group and individual MCPs

2. **Dashboard UI** (React + Tailwind + shadcn/ui)
   - Web interface at `http://localhost:[PORT]`
   - Three main tabs: MCPs, Plugins, Skills
   - Real-time toggle controls
   - Group-based organization with collapse/expand

3. **Configuration Files**
   - `~/.mcp-gateway/config.json` — Master MCP configuration
   - `~/.env-secrets.env` — All API keys and secrets (single source of truth)
   - `~/.mcp-gateway/state.json` — Persistent on/off state for MCPs

---

## MCP Consolidation Strategy

### MCPs to Include in Gateway

| MCP | Status | Group | Notes |
|-----|--------|-------|-------|
| **blotato** | Important | Publishing | Social media automation |
| **stitch** | Needed | Design | Google Stitch design tool |
| **remotion** | Needed | Video | Video framework docs |
| **n8n-mcp** | Needed (unreliable) | Automation | Workflow tool — address reliability issues |
| **elevenlabs** | Needed | Audio | Text-to-speech, voice tools |
| **notion** | Needed | Data | Database access |
| **perplexity** | Needed | Research | AI research/search |
| **context7** | Needed | Documentation | Documentation access |
| **playwright** | Lower priority | Browser | CLI available and installed — prefer CLI for token efficiency |
| **docker** | Keep separate | System | Keep as fallback; not routing through gateway initially |

### CLI vs MCP Decision

**Playwright:** Has CLI installed locally.
- **Decision:** Keep as CLI for token efficiency
- **MCP fallback:** Available through docker-mcp-toolkit if CLI insufficient
- **UI indicator:** Shows "CLI available ✓ Installed" with toggle preference

**Other tools:** Evaluate once gateway is running
- CLI preferred for token-light operations
- MCP used for complex interactions requiring full tool access

### Docker MCP Toolkit

**Current status:** Disabled in Anti-Gravity, contains ~100 tools

**Decision:** Do not disable entirely
- Extract specific tools (ElevenLabs, Notion, Perplexity, Context7, Playwright) into gateway
- Keep docker-mcp-toolkit as fallback for other tools not explicitly consolidated
- Prevents 100-tool limit from constraining you

---

## Dashboard Design

### Visual Aesthetic
- **Theme:** Dark mode (slate-950/slate-900 background)
- **Typography:** Clean, modern sans-serif with generous spacing
- **Interaction:** Smooth toggles, collapse/expand animations
- **Clarity:** High contrast, clear visual hierarchy

### Tab 1: MCP Servers

**Structure:**
- Collapsible groups: Publishing, Design, Video, Audio, Data, Research, Documentation, Automation, Browser
- Each group shows: `[X of Y enabled]` status
- Group-level toggle: "Enable All" / "Disable All"
- Individual MCP toggles with status badge (Active/Inactive)

**Status Indicators:**
```
┌─ Playwright
├─ CLI available ✓
├─ CLI installed ✓
└─ [Toggle] [Active/Inactive]

┌─ ElevenLabs
├─ [No CLI available]
└─ [Toggle] [Active/Inactive]
```

**Behavior:**
- Toggling an MCP immediately updates `~/.mcp-gateway/state.json`
- Gateway server refreshes MCP availability in real-time
- Connected tools (Anti-Gravity, Claude Code) see the change on next request

### Tab 2: Plugins

- List of installed plugins (Vercel, Figma, GitHub, etc.)
- Simple on/off indicators
- No granular tool control

### Tab 3: Skills

- Grid layout showing all available skills
- Skill name, description, slash command
- **Example:**
  ```
  Brainstorming
  "Turn ideas into fully formed designs and specs"
  Command: /brainstorm
  ```

---

## Configuration Format

### `~/.mcp-gateway/config.json`

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

### `~/.mcp-gateway/state.json`

```json
{
  "mcpStates": {
    "blotato": true,
    "stitch": true,
    "remotion": true,
    "elevenlabs": true,
    "notion": true,
    "perplexity": true,
    "context7": true,
    "n8n-mcp": true,
    "playwright": false
  },
  "groupStates": {
    "Publishing": true,
    "Design": true,
    "Video": true,
    "Audio": true,
    "Data": true,
    "Research": true,
    "Documentation": true,
    "Automation": true,
    "Browser": false
  }
}
```

---

## Integration with Existing Tools

### Anti-Gravity Setup
```json
{
  "mcpServers": {
    "gateway": {
      "serverURL": "http://localhost:3003"
    }
  }
}
```

### Claude Code Setup
```json
{
  "mcpServers": {
    "gateway": {
      "serverURL": "http://localhost:3003"
    }
  }
}
```

### Fallback (Manual Override)
- If needed, keep individual tool configs for one-off usage
- Gateway is primary; individual configs are secondary
- No sync required — tools read from gateway on startup

---

## Feature Set

### Phase 1 (MVP)
- [ ] Gateway server with MCP routing
- [ ] Web dashboard with three tabs
- [ ] Group-based toggle system
- [ ] Persistent state management
- [ ] CLI vs MCP indicators

### Phase 2 (Enhancement)
- [ ] Search/filter MCPs in dashboard
- [ ] CLI tool availability detection
- [ ] Auto-sync config to Anti-Gravity and Claude Code
- [ ] Health checks (MCP connection status)
- [ ] Usage analytics

### Phase 3 (Advanced)
- [ ] MCP marketplace for adding new servers
- [ ] Custom group creation
- [ ] Per-tool granular toggles (if needed later)
- [ ] Backup/restore configuration

---

## Success Criteria

✓ Single dashboard shows all MCPs, plugins, skills  
✓ Toggle MCPs on/off by group and individually  
✓ No need to manually edit Anti-Gravity/Claude Code configs  
✓ CLI tools clearly distinguished from MCPs  
✓ All secrets centralized in `~/.env-secrets.env`  
✓ Works seamlessly across Anti-Gravity + Claude Code  
✓ Reliable (no "once in a blue moon" failures like n8n-mcp)  
✓ Minimal token overhead compared to direct MCP calls  

---

## Open Questions / Decisions Pending

1. ~~**Port selection:** Use 3001, 3002, 5173, or 8000?~~ **DECIDED:** 3003
2. **Auto-start:** Should gateway auto-start on system boot or run manually?
3. **N8N reliability:** Should we investigate why n8n-mcp fails intermittently before routing through gateway?
4. **Docker MCP toolkit:** Keep as fallback, or eventually phase out?

