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
