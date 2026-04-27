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
