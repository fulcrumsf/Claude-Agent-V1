---
title: "MCP Gateway Controller Implementation Plan"
type: spec
domain: app-dev
tags: [spec, app-dev, automation, ai-agents]
---

# MCP Gateway Controller Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a unified MCP Gateway server and React dashboard that consolidates all MCP management into a single point of control.

**Architecture:** Express.js gateway server running on port 3003 that routes MCP connections and serves a React dashboard UI. Configuration lives in `~/.mcp-gateway/config.json` with state persisted in `~/.mcp-gateway/state.json`. All secrets come from `~/.env-secrets.env`.

**Tech Stack:** Node.js + TypeScript + Express (backend), React + Vite + Tailwind CSS (frontend), dark theme UI

---

## File Structure

**Backend:**
- `server/src/index.ts` — Express server entry point
- `server/src/types.ts` — TypeScript interfaces for config, MCPs, state
- `server/src/config.ts` — Config file I/O and env variable interpolation
- `server/src/routes/api.ts` — REST API endpoints for MCPs, toggles, plugins, skills
- `server/package.json` — Server dependencies
- `server/tsconfig.json` — TypeScript config for backend

**Frontend:**
- `dashboard/src/main.tsx` — Vite entry point
- `dashboard/src/App.tsx` — Main React component with tabs
- `dashboard/src/index.css` — Global styles and Tailwind setup
- `dashboard/src/hooks/useMCPs.ts` — API communication hook with polling
- `dashboard/package.json` — Dashboard dependencies
- `dashboard/vite.config.ts` — Vite configuration
- `dashboard/tailwind.config.js` — Tailwind config

**Tests & Docs:**
- `server/tests/integration.test.ts` — Integration tests
- `README.md` — Project overview
- `SETUP.md` — Installation and usage instructions

---

## Task 1: Initialize Server Project

**Files:**
- Create: `server/package.json`
- Create: `server/tsconfig.json`
- Create: `server/.env.example`
- Create: `server/.gitignore`

### Steps

- [ ] **Step 1: Create server directory and package.json**

Run:
```bash
cd /Users/tonymacbook2025/Documents/App\ Building/003_App-Development/MCP-Gateway-Controller
mkdir -p server/src/routes
```

Create `server/package.json`:
```json
{
  "name": "mcp-gateway-server",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "ts-node --esm src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js",
    "test": "node --test --loader ts-node/esm tests/**/*.test.ts"
  },
  "dependencies": {
    "express": "^4.18.2",
    "dotenv": "^16.0.3"
  },
  "devDependencies": {
    "@types/express": "^4.17.17",
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0",
    "ts-node": "^10.9.1"
  }
}
```

- [ ] **Step 2: Create tsconfig.json**

Create `server/tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ES2020",
    "lib": ["ES2020"],
    "moduleResolution": "node",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

- [ ] **Step 3: Create .env.example and .gitignore**

Create `server/.env.example`:
```
MCP_GATEWAY_PORT=3003
BLOTATO_API_KEY=
STITCH_API_KEY=
N8N_MCP_TOKEN=
ELEVENLABS_API_KEY=
NOTION_API_KEY=
PERPLEXITY_API_KEY=
CONTEXT7_API_KEY=
```

Create `server/.gitignore`:
```
node_modules/
dist/
.env
.env.local
*.log
```

- [ ] **Step 4: Verify structure**

Run:
```bash
ls -la server/
# Expected: package.json, tsconfig.json, .env.example, .gitignore, src/
```

- [ ] **Step 5: Commit**

```bash
cd /Users/tonymacbook2025/Documents/App\ Building/003_App-Development/MCP-Gateway-Controller
git add server/package.json server/tsconfig.json server/.env.example server/.gitignore
git commit -m "feat: initialize server project structure"
```

---

## Task 2: Create Gateway Configuration Management

**Files:**
- Create: `server/src/types.ts`
- Create: `server/src/config.ts`

### Steps

- [ ] **Step 1: Create types.ts with all TypeScript interfaces**

Create `server/src/types.ts`:
```typescript
export interface MCPServer {
  serverURL?: string;
  command?: string;
  args?: string[];
  headers?: Record<string, string>;
  cli?: boolean;
  installed?: boolean;
}

export interface Config {
  port: number;
  groups: Record<string, string[]>;
  mcpServers: Record<string, MCPServer>;
}

export interface MCPState {
  mcpStates: Record<string, boolean>;
  groupStates: Record<string, boolean>;
}

export interface MCPInfo {
  name: string;
  group: string;
  enabled: boolean;
  hasCliAvailable?: boolean;
  hasCliInstalled?: boolean;
}

export interface GroupInfo {
  name: string;
  enabled: boolean;
  enabledCount: number;
  totalCount: number;
  mcps: MCPInfo[];
}

export interface Skill {
  name: string;
  description: string;
  command: string;
}
```

- [ ] **Step 2: Create config.ts module**

Create `server/src/config.ts`:
```typescript
import fs from 'fs';
import path from 'path';
import os from 'os';
import { Config, MCPState } from './types.js';

const CONFIG_DIR = path.join(os.homedir(), '.mcp-gateway');
const CONFIG_FILE = path.join(CONFIG_DIR, 'config.json');
const STATE_FILE = path.join(CONFIG_DIR, 'state.json');
const SECRETS_FILE = path.join(os.homedir(), '.env-secrets.env');

function ensureConfigDir() {
  if (!fs.existsSync(CONFIG_DIR)) {
    fs.mkdirSync(CONFIG_DIR, { recursive: true });
  }
}

function loadSecrets(): Record<string, string> {
  const secrets: Record<string, string> = {};
  if (fs.existsSync(SECRETS_FILE)) {
    const content = fs.readFileSync(SECRETS_FILE, 'utf-8');
    const lines = content.split('\n');
    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed && !trimmed.startsWith('#')) {
        const [key, ...rest] = trimmed.split('=');
        secrets[key] = rest.join('=');
      }
    }
  }
  return secrets;
}

function interpolateEnvVars(value: string, secrets: Record<string, string>): string {
  return value.replace(/\$\{([^}]+)\}/g, (match, key) => {
    return secrets[key] || process.env[key] || match;
  });
}

export function loadConfig(): Config {
  ensureConfigDir();
  
  if (!fs.existsSync(CONFIG_FILE)) {
    throw new Error(`Config file not found: ${CONFIG_FILE}`);
  }
  
  const secrets = loadSecrets();
  const configData = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf-8'));
  
  // Interpolate env vars in headers
  for (const [name, server] of Object.entries(configData.mcpServers)) {
    if (server.headers) {
      for (const [key, value] of Object.entries(server.headers)) {
        server.headers[key] = interpolateEnvVars(value as string, secrets);
      }
    }
  }
  
  return configData as Config;
}

export function loadState(): MCPState {
  ensureConfigDir();
  
  if (!fs.existsSync(STATE_FILE)) {
    // Return default state with all MCPs enabled
    return {
      mcpStates: {},
      groupStates: {}
    };
  }
  
  return JSON.parse(fs.readFileSync(STATE_FILE, 'utf-8')) as MCPState;
}

export function saveState(state: MCPState): void {
  ensureConfigDir();
  fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}
```

- [ ] **Step 3: Test types and config loading**

Run:
```bash
cd /Users/tonymacbook2025/Documents/App\ Building/003_App-Development/MCP-Gateway-Controller/server
npx tsc --noEmit src/types.ts src/config.ts
# Expected: No errors
```

- [ ] **Step 4: Commit**

```bash
git add server/src/types.ts server/src/config.ts
git commit -m "feat: add configuration types and loading logic"
```

---

## Task 3: Create Express Server and REST API

**Files:**
- Create: `server/src/routes/api.ts`
- Create: `server/src/index.ts`

### Steps

- [ ] **Step 1: Create API routes module**

Create `server/src/routes/api.ts`:
```typescript
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
  for (const [groupName, mcps] of Object.entries(config.groups)) {
    if (mcps.includes(name)) {
      group = groupName;
      break;
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
```

- [ ] **Step 2: Create Express server entry point**

Create `server/src/index.ts`:
```typescript
import express from 'express';
import { loadConfig } from './config.js';
import apiRouter from './routes/api.js';

const app = express();

app.use(express.json());
app.use('/api', apiRouter);

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// Static files for dashboard (in production)
app.use(express.static('../dashboard/dist'));

// Fallback to index.html for SPA routing
app.get('/', (req, res) => {
  res.sendFile('../dashboard/dist/index.html');
});

const config = loadConfig();
const PORT = config.port || 3003;

app.listen(PORT, () => {
  console.log(`MCP Gateway Server running on http://localhost:${PORT}`);
});
```

- [ ] **Step 3: Test server setup**

Run:
```bash
cd /Users/tonymacbook2025/Documents/App\ Building/003_App-Development/MCP-Gateway-Controller/server
npm install
# Expected: Dependencies installed without errors
```

- [ ] **Step 4: Verify no type errors**

Run:
```bash
npx tsc --noEmit src/index.ts src/routes/api.ts
# Expected: No errors
```

- [ ] **Step 5: Commit**

```bash
git add server/src/index.ts server/src/routes/api.ts
git commit -m "feat: create express server with REST API endpoints"
```

---

## Task 4: Initialize Dashboard Project

**Files:**
- Create: `dashboard/package.json`
- Create: `dashboard/vite.config.ts`
- Create: `dashboard/tsconfig.json`
- Create: `dashboard/tailwind.config.js`
- Create: `dashboard/index.html`

### Steps

- [ ] **Step 1: Create dashboard directory structure**

Run:
```bash
cd /Users/tonymacbook2025/Documents/App\ Building/003_App-Development/MCP-Gateway-Controller
mkdir -p dashboard/src/hooks
```

- [ ] **Step 2: Create package.json**

Create `dashboard/package.json`:
```json
{
  "name": "mcp-gateway-dashboard",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.0.0",
    "vite": "^4.4.0",
    "typescript": "^5.0.0",
    "tailwindcss": "^3.3.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0"
  }
}
```

- [ ] **Step 3: Create vite.config.ts**

Create `dashboard/vite.config.ts`:
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:3003',
        changeOrigin: true
      }
    }
  }
});
```

- [ ] **Step 4: Create tsconfig.json**

Create `dashboard/tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "jsx": "react-jsx",
    "strict": true,
    "esModuleInterop": true,
    "resolveJsonModule": true,
    "moduleResolution": "bundler"
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

- [ ] **Step 5: Create tailwind.config.js**

Create `dashboard/tailwind.config.js`:
```javascript
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {}
  },
  plugins: []
};
```

- [ ] **Step 6: Create index.html**

Create `dashboard/index.html`:
```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>MCP Gateway Controller</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 7: Install dependencies**

Run:
```bash
cd /Users/tonymacbook2025/Documents/App\ Building/003_App-Development/MCP-Gateway-Controller/dashboard
npm install
# Expected: All dependencies installed successfully
```

- [ ] **Step 8: Commit**

```bash
git add dashboard/package.json dashboard/vite.config.ts dashboard/tsconfig.json dashboard/tailwind.config.js dashboard/index.html
git commit -m "feat: initialize dashboard project with Vite and Tailwind"
```

---

## Task 5: Build Dashboard React Components

**Files:**
- Create: `dashboard/src/main.tsx`
- Create: `dashboard/src/App.tsx`
- Create: `dashboard/src/index.css`

### Steps

- [ ] **Step 1: Create global styles**

Create `dashboard/src/index.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #020617;
  color: #e2e8f0;
}

#root {
  width: 100%;
  min-height: 100vh;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #0f172a;
}

::-webkit-scrollbar-thumb {
  background: #334155;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #475569;
}
```

- [ ] **Step 2: Create main.tsx entry point**

Create `dashboard/src/main.tsx`:
```typescript
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

- [ ] **Step 3: Create App.tsx main component**

Create `dashboard/src/App.tsx`:
```typescript
import { useState } from 'react';
import { useMCPs } from './hooks/useMCPs';

type Tab = 'mcps' | 'plugins' | 'skills';

export default function App() {
  const [activeTab, setActiveTab] = useState<Tab>('mcps');
  const { groups, plugins, skills, toggleMCP, toggleGroup } = useMCPs();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <h1 className="text-2xl font-bold">MCP Gateway Controller</h1>
          <p className="text-sm text-slate-400 mt-1">
            Unified MCP management for all your tools
          </p>
        </div>
      </header>

      {/* Tabs */}
      <div className="border-b border-slate-800 bg-slate-900/30 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6">
          <nav className="flex gap-8">
            {(['mcps', 'plugins', 'skills'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 px-1 border-b-2 font-medium transition ${
                  activeTab === tab
                    ? 'border-blue-500 text-blue-400'
                    : 'border-transparent text-slate-400 hover:text-slate-300'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {activeTab === 'mcps' && (
          <div className="space-y-6">
            {Object.entries(groups).map(([groupName, group]) => (
              <div
                key={groupName}
                className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden"
              >
                {/* Group Header */}
                <div className="bg-slate-800/50 px-6 py-4 flex items-center justify-between">
                  <div>
                    <h2 className="font-semibold text-lg">{groupName}</h2>
                    <p className="text-sm text-slate-400 mt-1">
                      {group.enabledCount} of {group.totalCount} enabled
                    </p>
                  </div>
                  <button
                    onClick={() => toggleGroup(groupName)}
                    className={`px-4 py-2 rounded font-medium transition ${
                      group.enabled
                        ? 'bg-blue-600 hover:bg-blue-700 text-white'
                        : 'bg-slate-700 hover:bg-slate-600 text-slate-300'
                    }`}
                  >
                    {group.enabled ? 'Disable All' : 'Enable All'}
                  </button>
                </div>

                {/* MCPs List */}
                <div className="divide-y divide-slate-800">
                  {group.mcps.map((mcp) => (
                    <div
                      key={mcp.name}
                      className="px-6 py-4 flex items-center justify-between hover:bg-slate-800/50 transition"
                    >
                      <div>
                        <h3 className="font-medium">{mcp.name}</h3>
                        {mcp.hasCliAvailable && (
                          <p className="text-xs text-green-400 mt-1">
                            ✓ CLI available
                            {mcp.hasCliInstalled && ' • CLI installed'}
                          </p>
                        )}
                      </div>
                      <div className="flex items-center gap-3">
                        <span
                          className={`text-xs font-medium px-2 py-1 rounded ${
                            mcp.enabled
                              ? 'bg-green-900/30 text-green-400'
                              : 'bg-slate-800 text-slate-400'
                          }`}
                        >
                          {mcp.enabled ? 'Active' : 'Inactive'}
                        </span>
                        <button
                          onClick={() => toggleMCP(mcp.name)}
                          className={`w-12 h-6 rounded-full transition ${
                            mcp.enabled
                              ? 'bg-green-600'
                              : 'bg-slate-700'
                          }`}
                          aria-label={`Toggle ${mcp.name}`}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'plugins' && (
          <div className="grid gap-4">
            {plugins.map((plugin) => (
              <div
                key={plugin.name}
                className="bg-slate-900 border border-slate-800 rounded-lg px-6 py-4 flex items-center justify-between"
              >
                <h3 className="font-medium">{plugin.name}</h3>
                <span
                  className={`text-xs font-medium px-2 py-1 rounded ${
                    plugin.enabled
                      ? 'bg-green-900/30 text-green-400'
                      : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  {plugin.enabled ? 'Enabled' : 'Disabled'}
                </span>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'skills' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {skills.map((skill) => (
              <div
                key={skill.name}
                className="bg-slate-900 border border-slate-800 rounded-lg px-6 py-6"
              >
                <h3 className="font-semibold text-lg">{skill.name}</h3>
                <p className="text-slate-400 text-sm mt-2">{skill.description}</p>
                <p className="text-blue-400 text-xs font-mono mt-4 bg-slate-800 px-3 py-2 rounded">
                  {skill.command}
                </p>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
```

- [ ] **Step 4: Verify components structure**

Run:
```bash
cd /Users/tonymacbook2025/Documents/App\ Building/003_App-Development/MCP-Gateway-Controller/dashboard
npx tsc --noEmit src/App.tsx src/main.tsx
# Expected: No type errors
```

- [ ] **Step 5: Commit**

```bash
git add dashboard/src/main.tsx dashboard/src/App.tsx dashboard/src/index.css
git commit -m "feat: build dashboard React components with Tailwind styling"
```

---

## Task 6: Create useMCPs Hook for API Communication

**Files:**
- Create: `dashboard/src/hooks/useMCPs.ts`

### Steps

- [ ] **Step 1: Create useMCPs hook**

Create `dashboard/src/hooks/useMCPs.ts`:
```typescript
import { useState, useEffect } from 'react';

export interface MCPInfo {
  name: string;
  group: string;
  enabled: boolean;
  hasCliAvailable?: boolean;
  hasCliInstalled?: boolean;
}

export interface GroupInfo {
  name: string;
  enabled: boolean;
  enabledCount: number;
  totalCount: number;
  mcps: MCPInfo[];
}

export interface Plugin {
  name: string;
  enabled: boolean;
}

export interface Skill {
  name: string;
  description: string;
  command: string;
}

const API_BASE = '/api';
const POLL_INTERVAL = 5000; // 5 seconds

export function useMCPs() {
  const [groups, setGroups] = useState<Record<string, GroupInfo>>({});
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch MCPs
  const fetchMCPs = async () => {
    try {
      const response = await fetch(`${API_BASE}/mcps`);
      if (!response.ok) throw new Error('Failed to fetch MCPs');
      const data = await response.json();
      setGroups(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    }
  };

  // Fetch plugins
  const fetchPlugins = async () => {
    try {
      const response = await fetch(`${API_BASE}/plugins`);
      if (!response.ok) throw new Error('Failed to fetch plugins');
      const data = await response.json();
      setPlugins(data);
    } catch (err) {
      console.error('Failed to fetch plugins:', err);
    }
  };

  // Fetch skills
  const fetchSkills = async () => {
    try {
      const response = await fetch(`${API_BASE}/skills`);
      if (!response.ok) throw new Error('Failed to fetch skills');
      const data = await response.json();
      setSkills(data);
    } catch (err) {
      console.error('Failed to fetch skills:', err);
    }
  };

  // Toggle individual MCP
  const toggleMCP = async (mcpName: string) => {
    try {
      const response = await fetch(`${API_BASE}/toggle-mcp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mcp: mcpName })
      });
      if (!response.ok) throw new Error('Failed to toggle MCP');
      await fetchMCPs();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to toggle MCP');
    }
  };

  // Toggle entire group
  const toggleGroup = async (groupName: string) => {
    try {
      const response = await fetch(`${API_BASE}/toggle-group`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ group: groupName })
      });
      if (!response.ok) throw new Error('Failed to toggle group');
      await fetchMCPs();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to toggle group');
    }
  };

  // Initial load
  useEffect(() => {
    const initialize = async () => {
      setLoading(true);
      await Promise.all([fetchMCPs(), fetchPlugins(), fetchSkills()]);
      setLoading(false);
    };

    initialize();
  }, []);

  // Poll for updates
  useEffect(() => {
    const interval = setInterval(fetchMCPs, POLL_INTERVAL);
    return () => clearInterval(interval);
  }, []);

  return {
    groups,
    plugins,
    skills,
    loading,
    error,
    toggleMCP,
    toggleGroup
  };
}
```

- [ ] **Step 2: Verify hook type checking**

Run:
```bash
cd /Users/tonymacbook2025/Documents/App\ Building/003_App-Development/MCP-Gateway-Controller/dashboard
npx tsc --noEmit src/hooks/useMCPs.ts
# Expected: No type errors
```

- [ ] **Step 3: Commit**

```bash
git add dashboard/src/hooks/useMCPs.ts
git commit -m "feat: create useMCPs hook for server API communication"
```

---

## Task 7: Create Integration Tests

**Files:**
- Create: `server/tests/integration.test.ts`
- Modify: `server/package.json` (add test script)

### Steps

- [ ] **Step 1: Create test directory**

Run:
```bash
mkdir -p /Users/tonymacbook2025/Documents/App\ Building/003_App-Development/MCP-Gateway-Controller/server/tests
```

- [ ] **Step 2: Create integration tests**

Create `server/tests/integration.test.ts`:
```typescript
import assert from 'assert';
import { loadConfig, loadState, saveState } from '../src/config.js';
import { MCPState } from '../src/types.js';

console.log('Running integration tests...\n');

// Test 1: loadConfig returns valid configuration
console.log('Test 1: loadConfig returns valid configuration');
try {
  const config = loadConfig();
  assert(config.port, 'Config should have port');
  assert(config.groups, 'Config should have groups');
  assert(config.mcpServers, 'Config should have mcpServers');
  console.log('✓ PASS\n');
} catch (err) {
  console.log('✗ FAIL:', err instanceof Error ? err.message : String(err));
  process.exit(1);
}

// Test 2: loadState returns valid state
console.log('Test 2: loadState returns valid state');
try {
  const state = loadState();
  assert(typeof state === 'object', 'State should be an object');
  assert('mcpStates' in state, 'State should have mcpStates');
  assert('groupStates' in state, 'State should have groupStates');
  console.log('✓ PASS\n');
} catch (err) {
  console.log('✗ FAIL:', err instanceof Error ? err.message : String(err));
  process.exit(1);
}

// Test 3: saveState persists state changes
console.log('Test 3: saveState persists state changes');
try {
  let state = loadState();
  const originalState = JSON.parse(JSON.stringify(state));
  
  state.mcpStates['test-mcp'] = true;
  saveState(state);
  
  const reloadedState = loadState();
  assert(
    reloadedState.mcpStates['test-mcp'] === true,
    'State should persist changes'
  );
  
  // Restore original state
  originalState.mcpStates['test-mcp'] = undefined;
  delete originalState.mcpStates['test-mcp'];
  saveState(originalState);
  
  console.log('✓ PASS\n');
} catch (err) {
  console.log('✗ FAIL:', err instanceof Error ? err.message : String(err));
  process.exit(1);
}

// Test 4: Config contains expected MCP servers
console.log('Test 4: Config contains expected MCP servers');
try {
  const config = loadConfig();
  const expectedMCPs = ['blotato', 'stitch', 'n8n-mcp', 'remotion', 'elevenlabs'];
  
  for (const mcp of expectedMCPs) {
    assert(config.mcpServers[mcp], `Config should contain ${mcp}`);
  }
  console.log('✓ PASS\n');
} catch (err) {
  console.log('✗ FAIL:', err instanceof Error ? err.message : String(err));
  process.exit(1);
}

// Test 5: Config groups are properly organized
console.log('Test 5: Config groups are properly organized');
try {
  const config = loadConfig();
  const expectedGroups = ['Publishing', 'Design', 'Video', 'Audio', 'Data', 'Research'];
  
  for (const group of expectedGroups) {
    assert(config.groups[group], `Config should contain ${group} group`);
    assert(Array.isArray(config.groups[group]), `${group} should be an array`);
  }
  console.log('✓ PASS\n');
} catch (err) {
  console.log('✗ FAIL:', err instanceof Error ? err.message : String(err));
  process.exit(1);
}

console.log('All integration tests passed! ✓');
```

- [ ] **Step 2: Verify tests can be run**

Run:
```bash
cd /Users/tonymacbook2025/Documents/App\ Building/003_App-Development/MCP-Gateway-Controller/server
npm test
# Expected: All tests pass (or expected failures if config.json not yet created)
```

- [ ] **Step 3: Commit**

```bash
git add server/tests/integration.test.ts
git commit -m "test: add integration tests for config management"
```

---

## Task 8: Create Documentation

**Files:**
- Create: `README.md`
- Create: `SETUP.md`

### Steps

- [ ] **Step 1: Create README.md**

Create `README.md`:
```markdown
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
```

- [ ] **Step 2: Create SETUP.md**

Create `SETUP.md`:
```markdown
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
```

- [ ] **Step 3: Verify files exist**

Run:
```bash
ls -la /Users/tonymacbook2025/Documents/App\ Building/003_App-Development/MCP-Gateway-Controller/*.md
# Expected: README.md and SETUP.md listed
```

- [ ] **Step 4: Commit**

```bash
git add README.md SETUP.md
git commit -m "docs: add README and SETUP documentation"
```

---

## Summary

All 8 tasks are now ready for execution by subagents:

1. ✓ Server project initialization (package.json, tsconfig.json)
2. ✓ Configuration management (types.ts, config.ts with env interpolation)
3. ✓ Express server and API (routes, endpoints for MCPs/plugins/skills, toggles)
4. ✓ Dashboard initialization (Vite, Tailwind, tsconfig)
5. ✓ React dashboard components (dark theme, tabs, group toggles)
6. ✓ useMCPs hook (API communication, polling)
7. ✓ Integration tests (config loading, state persistence)
8. ✓ Documentation (README, SETUP guide)

Each task is independent, completable in 15-25 minutes, and includes self-review + two-stage approval.
