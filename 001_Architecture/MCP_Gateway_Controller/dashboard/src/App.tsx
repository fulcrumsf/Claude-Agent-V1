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
                aria-current={activeTab === tab ? 'page' : undefined}
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
                    type="button"
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
                          type="button"
                          onClick={() => toggleMCP(mcp.name)}
                          className={`w-12 h-6 rounded-full transition relative ${
                            mcp.enabled
                              ? 'bg-green-600'
                              : 'bg-slate-700'
                          }`}
                          aria-label={`Toggle ${mcp.name}`}
                        >
                          <span
                            className={`absolute w-5 h-5 bg-white rounded-full transition-all ${
                              mcp.enabled ? 'right-0.5 top-0.5' : 'left-0.5 top-0.5'
                            }`}
                          />
                        </button>
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
