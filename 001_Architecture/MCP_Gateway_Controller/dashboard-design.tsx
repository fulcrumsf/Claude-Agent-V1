'use client';

import React, { useState } from 'react';
import { ChevronDown, Terminal, Zap, BookOpen, CheckCircle, AlertCircle } from 'lucide-react';

interface MCPServer {
  id: string;
  name: string;
  enabled: boolean;
  hasCliAvailable: boolean;
  cliInstalled: boolean;
  group: string;
}

interface Plugin {
  id: string;
  name: string;
  enabled: boolean;
}

interface Skill {
  id: string;
  name: string;
  description: string;
  command: string;
}

// Mock data
const mcpServers: MCPServer[] = [
  { id: 'blotato', name: 'Blotato', enabled: true, hasCliAvailable: false, cliInstalled: false, group: 'Publishing' },
  { id: 'stitch', name: 'Stitch (Design)', enabled: true, hasCliAvailable: false, cliInstalled: false, group: 'Design' },
  { id: 'remotion', name: 'Remotion', enabled: true, hasCliAvailable: true, cliInstalled: true, group: 'Video' },
  { id: 'elevenlabs', name: 'ElevenLabs', enabled: true, hasCliAvailable: false, cliInstalled: false, group: 'Audio' },
  { id: 'notion', name: 'Notion', enabled: true, hasCliAvailable: false, cliInstalled: false, group: 'Data' },
  { id: 'perplexity', name: 'Perplexity', enabled: true, hasCliAvailable: false, cliInstalled: false, group: 'Research' },
  { id: 'context7', name: 'Context7', enabled: true, hasCliAvailable: false, cliInstalled: false, group: 'Documentation' },
  { id: 'playwright', name: 'Playwright', enabled: false, hasCliAvailable: true, cliInstalled: true, group: 'Browser' },
  { id: 'n8n', name: 'n8n', enabled: true, hasCliAvailable: false, cliInstalled: false, group: 'Automation' },
];

const plugins = [
  { id: 'vercel', name: 'Vercel Plugin', enabled: true },
  { id: 'figma', name: 'Figma Plugin', enabled: true },
  { id: 'github', name: 'GitHub Plugin', enabled: true },
];

const skills = [
  { id: 'brainstorm', name: 'Brainstorming', description: 'Turn ideas into fully formed designs and specs', command: '/brainstorm' },
  { id: 'frontend-design', name: 'Frontend Design', description: 'Create distinctive, production-grade UIs', command: '/frontend-design' },
  { id: 'code-review', name: 'Code Review', description: 'Review code for quality and best practices', command: '/code-review' },
  { id: 'commit', name: 'Git Commit', description: 'Create well-formed git commits', command: '/commit' },
];

export default function MCPDashboard() {
  const [activeTab, setActiveTab] = useState('mcps');
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set(['Publishing', 'Design', 'Video', 'Audio']));
  const [servers, setServers] = useState(mcpServers);

  const toggleGroup = (group: string) => {
    const newExpanded = new Set(expandedGroups);
    if (newExpanded.has(group)) {
      newExpanded.delete(group);
    } else {
      newExpanded.add(group);
    }
    setExpandedGroups(newExpanded);
  };

  const toggleServer = (id: string) => {
    setServers(servers.map(s => s.id === id ? { ...s, enabled: !s.enabled } : s));
  };

  const toggleGroupServers = (group: string, enabled: boolean) => {
    setServers(servers.map(s => s.group === group ? { ...s, enabled } : s));
  };

  const groupedServers = servers.reduce((acc, server) => {
    if (!acc[server.group]) acc[server.group] = [];
    acc[server.group].push(server);
    return acc;
  }, {} as Record<string, MCPServer[]>);

  const groups = Object.keys(groupedServers).sort();
  const enabledCount = servers.filter(s => s.enabled).length;
  const skillCount = skills.length;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 font-['Geist']">
      {/* Header */}
      <div className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-light tracking-tight">MCP Control Center</h1>
              <p className="text-slate-400 text-sm mt-1">Manage your MCPs, plugins, and skills</p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-light text-blue-400">{enabledCount}</div>
              <div className="text-slate-400 text-xs uppercase tracking-wider">Active MCPs</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex gap-8">
            <button
              onClick={() => setActiveTab('mcps')}
              className={`py-4 text-sm font-medium transition-all border-b-2 flex items-center gap-2 ${
                activeTab === 'mcps'
                  ? 'border-blue-500 text-slate-50'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <Zap className="w-4 h-4" />
              MCP Servers
              <span className="ml-2 px-2 py-0.5 bg-slate-800 rounded text-xs text-slate-300">{servers.length}</span>
            </button>
            <button
              onClick={() => setActiveTab('plugins')}
              className={`py-4 text-sm font-medium transition-all border-b-2 flex items-center gap-2 ${
                activeTab === 'plugins'
                  ? 'border-blue-500 text-slate-50'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <Terminal className="w-4 h-4" />
              Plugins
              <span className="ml-2 px-2 py-0.5 bg-slate-800 rounded text-xs text-slate-300">{plugins.length}</span>
            </button>
            <button
              onClick={() => setActiveTab('skills')}
              className={`py-4 text-sm font-medium transition-all border-b-2 flex items-center gap-2 ${
                activeTab === 'skills'
                  ? 'border-blue-500 text-slate-50'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <BookOpen className="w-4 h-4" />
              Skills
              <span className="ml-2 px-2 py-0.5 bg-slate-800 rounded text-xs text-slate-300">{skillCount}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* MCP Servers Tab */}
        {activeTab === 'mcps' && (
          <div className="space-y-4">
            {groups.map((group) => (
              <div key={group} className="bg-slate-900/50 border border-slate-800 rounded-lg overflow-hidden hover:border-slate-700 transition-colors">
                {/* Group Header */}
                <button
                  onClick={() => toggleGroup(group)}
                  className="w-full px-6 py-4 flex items-center justify-between hover:bg-slate-800/50 transition-colors group"
                >
                  <div className="flex items-center gap-3">
                    <ChevronDown
                      className={`w-5 h-5 text-slate-400 transition-transform ${
                        expandedGroups.has(group) ? 'rotate-0' : '-rotate-90'
                      }`}
                    />
                    <h3 className="text-lg font-medium text-slate-50">{group}</h3>
                    <span className="text-slate-500 text-sm">
                      {groupedServers[group].filter(s => s.enabled).length}/{groupedServers[group].length}
                    </span>
                  </div>

                  {/* Group Toggle */}
                  <div className="flex items-center gap-3">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleGroupServers(group, groupedServers[group].some(s => !s.enabled));
                      }}
                      className="px-3 py-1.5 text-xs font-medium rounded bg-slate-800 hover:bg-slate-700 transition-colors text-slate-200"
                    >
                      {groupedServers[group].every(s => s.enabled) ? 'Disable All' : 'Enable All'}
                    </button>
                  </div>
                </button>

                {/* Group Content */}
                {expandedGroups.has(group) && (
                  <div className="border-t border-slate-800 bg-slate-950/50 divide-y divide-slate-800">
                    {groupedServers[group].map((server) => (
                      <div key={server.id} className="px-6 py-4 flex items-center justify-between hover:bg-slate-800/30 transition-colors">
                        <div className="flex items-center gap-4 flex-1">
                          <label className="flex items-center gap-3 cursor-pointer flex-1">
                            <input
                              type="checkbox"
                              checked={server.enabled}
                              onChange={() => toggleServer(server.id)}
                              className="w-5 h-5 rounded border border-slate-600 bg-slate-800 checked:bg-blue-500 checked:border-blue-500 cursor-pointer"
                            />
                            <span className={`font-medium ${server.enabled ? 'text-slate-50' : 'text-slate-500'}`}>
                              {server.name}
                            </span>
                          </label>

                          {/* Status Indicators */}
                          <div className="flex items-center gap-2">
                            {server.hasCliAvailable && (
                              <div className="flex items-center gap-1.5 px-2.5 py-1 bg-slate-800/50 rounded text-xs">
                                <Terminal className="w-3.5 h-3.5 text-amber-400" />
                                <span className="text-slate-300">CLI available</span>
                                {server.cliInstalled && (
                                  <>
                                    <span className="text-slate-600">•</span>
                                    <CheckCircle className="w-3.5 h-3.5 text-green-400" />
                                    <span className="text-slate-300">installed</span>
                                  </>
                                )}
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Status Badge */}
                        <div className={`px-3 py-1.5 rounded text-xs font-medium ml-4 ${
                          server.enabled
                            ? 'bg-green-500/20 text-green-300'
                            : 'bg-slate-700 text-slate-400'
                        }`}>
                          {server.enabled ? 'Active' : 'Inactive'}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Plugins Tab */}
        {activeTab === 'plugins' && (
          <div className="space-y-4">
            {plugins.map((plugin) => (
              <div key={plugin.id} className="bg-slate-900/50 border border-slate-800 rounded-lg px-6 py-4 flex items-center justify-between hover:border-slate-700 transition-colors">
                <label className="flex items-center gap-3 cursor-pointer flex-1">
                  <input
                    type="checkbox"
                    checked={plugin.enabled}
                    readOnly
                    className="w-5 h-5 rounded border border-slate-600 bg-slate-800 checked:bg-blue-500 checked:border-blue-500 cursor-pointer"
                  />
                  <span className="font-medium text-slate-50">{plugin.name}</span>
                </label>
                <div className={`px-3 py-1.5 rounded text-xs font-medium ${
                  plugin.enabled
                    ? 'bg-green-500/20 text-green-300'
                    : 'bg-slate-700 text-slate-400'
                }`}>
                  {plugin.enabled ? 'Active' : 'Inactive'}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Skills Tab */}
        {activeTab === 'skills' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {skills.map((skill) => (
              <div key={skill.id} className="bg-slate-900/50 border border-slate-800 rounded-lg p-6 hover:border-slate-700 transition-colors group">
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-lg font-medium text-slate-50">{skill.name}</h3>
                  <span className="px-2.5 py-1.5 bg-blue-500/20 text-blue-300 text-xs font-mono rounded border border-blue-500/30 group-hover:bg-blue-500/30 transition-colors">
                    {skill.command}
                  </span>
                </div>
                <p className="text-slate-400 text-sm leading-relaxed">{skill.description}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
