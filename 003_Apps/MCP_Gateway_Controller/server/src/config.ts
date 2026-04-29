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
        secrets[key.trim()] = rest.join('=').trim();
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
  let configData: Record<string, unknown>;
  try {
    configData = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf-8'));
  } catch (err) {
    throw new Error(`Failed to parse config file at ${CONFIG_FILE}: ${err instanceof Error ? err.message : String(err)}`);
  }

  // Interpolate env vars in headers
  const mcpServers = configData.mcpServers as Record<string, any>;
  for (const [name, server] of Object.entries(mcpServers)) {
    if (server.headers) {
      for (const [key, value] of Object.entries(server.headers)) {
        server.headers[key] = interpolateEnvVars(value as string, secrets);
      }
    }
  }

  return configData as unknown as Config;
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

  try {
    return JSON.parse(fs.readFileSync(STATE_FILE, 'utf-8')) as MCPState;
  } catch (err) {
    console.warn(`Failed to load state file, using defaults: ${err instanceof Error ? err.message : String(err)}`);
    return {
      mcpStates: {},
      groupStates: {}
    };
  }
}

export function saveState(state: MCPState): void {
  ensureConfigDir();
  fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}
