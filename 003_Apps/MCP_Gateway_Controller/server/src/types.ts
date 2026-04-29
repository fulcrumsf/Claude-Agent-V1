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
