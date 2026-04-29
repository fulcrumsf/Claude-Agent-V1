import { Router } from 'express';
import { loadConfig, loadState, saveState } from '../config.js';
import { Config, MCPState, MCPInfo, GroupInfo, Skill } from '../types.js';

const router = Router();

let cachedConfig: Config | null = null;
let cachedState: MCPState | null = null;

function getConfig(): Config {
  if (!cachedConfig) {
    cachedConfig = loadConfig();
  }
  return cachedConfig;
}

function getState(): MCPState {
  if (!cachedState) {
    cachedState = loadState();
  }
  return cachedState;
}

function getMCPInfo(name: string, config: Config, state: MCPState): MCPInfo | null {
  const server = config.mcpServers[name];
  if (!server) return null;

  let group = 'Unknown';
  if (config.groups) {
    for (const [groupName, mcps] of Object.entries(config.groups)) {
      if (mcps.includes(name)) {
        group = groupName;
        break;
      }
    }
  }

  const enabled = state.mcpStates[name] !== false;

  return {
    name,
    group,
    enabled,
    hasCliAvailable: server.cli ? true : false,
    hasCliInstalled: server.installed ? true : false
  };
}

// GET /api/mcps
router.get('/mcps', (req, res) => {
  const config = getConfig();
  const state = getState();

  const groups: Record<string, GroupInfo> = {};

  for (const [groupName, mcpNames] of Object.entries(config.groups)) {
    const mcps: MCPInfo[] = [];
    for (const name of mcpNames) {
      const info = getMCPInfo(name, config, state);
      if (info) mcps.push(info);
    }

    const enabledCount = mcps.filter(m => m.enabled).length;
    groups[groupName] = {
      name: groupName,
      enabled: state.groupStates[groupName] !== false,
      enabledCount,
      totalCount: mcps.length,
      mcps
    };
  }

  res.json(groups);
});

// GET /api/plugins
router.get('/plugins', (req, res) => {
  // Return list of installed plugins
  res.json([
    { name: 'Vercel', enabled: true },
    { name: 'Figma', enabled: true },
    { name: 'GitHub', enabled: true }
  ]);
});

// GET /api/skills
router.get('/skills', (req, res) => {
  // Return list of available skills
  const skills: Skill[] = [
    {
      name: 'Brainstorming',
      description: 'Turn ideas into fully formed designs and specs',
      command: '/brainstorm'
    },
    {
      name: 'Code Review',
      description: 'Review code for quality and best practices',
      command: '/review-code'
    }
  ];

  res.json(skills);
});

// POST /api/toggle-mcp
router.post('/toggle-mcp', (req, res) => {
  const { mcp } = req.body;
  if (!mcp) {
    return res.status(400).json({ error: 'MCP name required' });
  }

  const state = getState();
  state.mcpStates[mcp] = !state.mcpStates[mcp];
  saveState(state);
  cachedState = state;

  res.json({ mcp, enabled: state.mcpStates[mcp] });
});

// POST /api/toggle-group
router.post('/toggle-group', (req, res) => {
  const { group } = req.body;
  if (!group) {
    return res.status(400).json({ error: 'Group name required' });
  }

  const config = getConfig();
  const state = getState();

  const mcpNames = config.groups[group];
  if (!mcpNames) {
    return res.status(404).json({ error: 'Group not found' });
  }

  const currentEnabled = state.groupStates[group] !== false;
  const newEnabled = !currentEnabled;

  state.groupStates[group] = newEnabled;
  for (const mcp of mcpNames) {
    state.mcpStates[mcp] = newEnabled;
  }

  saveState(state);
  cachedState = state;

  res.json({ group, enabled: newEnabled });
});

export default router;
