import { useState } from 'react';
export function useMCPs() {
    const [groups, setGroups] = useState({
        'Built-in MCPs': {
            enabled: true,
            enabledCount: 2,
            totalCount: 3,
            mcps: [
                { name: 'filesystem', enabled: true, hasCliAvailable: true, hasCliInstalled: true },
                { name: 'web-browser', enabled: true, hasCliAvailable: false, hasCliInstalled: false },
                { name: 'database', enabled: false, hasCliAvailable: true, hasCliInstalled: false },
            ],
        },
        'External MCPs': {
            enabled: false,
            enabledCount: 0,
            totalCount: 2,
            mcps: [
                { name: 'github-mcp', enabled: false, hasCliAvailable: true, hasCliInstalled: false },
                { name: 'notion-mcp', enabled: false, hasCliAvailable: true, hasCliInstalled: false },
            ],
        },
    });
    const [plugins] = useState([
        { name: 'Plugin: Figma Design', enabled: true },
        { name: 'Plugin: Vercel Deploy', enabled: false },
        { name: 'Plugin: GitHub Integration', enabled: true },
    ]);
    const [skills] = useState([
        { name: 'Case Study Analysis', description: 'Analyze video case studies for viral patterns', command: '/case-study' },
        { name: 'Cinematic Styles', description: 'Apply production methodologies to video generation', command: '/cinematic' },
        { name: 'Notebooklm Protocol', description: 'Grounded research notebooks for scripts', command: '/notebooklm' },
        { name: 'Content Strategy', description: 'Framework for content planning and distribution', command: '/content-strategy' },
    ]);
    const toggleMCP = (mcpName) => {
        setGroups((prev) => {
            const newGroups = { ...prev };
            for (const group of Object.values(newGroups)) {
                const mcp = group.mcps.find((m) => m.name === mcpName);
                if (mcp) {
                    mcp.enabled = !mcp.enabled;
                    group.enabledCount = group.mcps.filter((m) => m.enabled).length;
                    break;
                }
            }
            return newGroups;
        });
    };
    const toggleGroup = (groupName) => {
        setGroups((prev) => {
            const newGroups = { ...prev };
            const group = newGroups[groupName];
            if (group) {
                const newEnabled = !group.enabled;
                group.enabled = newEnabled;
                group.mcps.forEach((mcp) => {
                    mcp.enabled = newEnabled;
                });
                group.enabledCount = newEnabled ? group.totalCount : 0;
            }
            return newGroups;
        });
    };
    return {
        groups,
        plugins,
        skills,
        toggleMCP,
        toggleGroup,
    };
}
