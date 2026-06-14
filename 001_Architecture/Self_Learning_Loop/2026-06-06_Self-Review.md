# Self-Review — 2026-06-06

## What Went Well
- **Batch npm install failure caught quickly** — when hyperframes killed the install batch, I identified the problem immediately and re-ran packages individually rather than debugging the giant command
- **--ignore-scripts fix for hyperframes** — clean workaround; sharp native build is a known fragile dependency
- **MCP canonical source found correctly** — checked `realpath` before editing, caught the symlink to `001_Architecture/MCP/gemini_mcp_config.json`
- **Brew already current** — Antigravity upgrade had already pulled brew updates; didn't waste time re-running

## What to Improve
- **Don't batch unrelated packages in one npm install** — when one fails (SIGKILL), the whole command dies and nothing else updates. Install in logical groups or individually for packages with native dependencies
- **Should have checked hyperframes for native deps first** — sharp is a known problematic native module; could have anticipated the `--ignore-scripts` requirement upfront

## Rules to Carry Forward
- `hyperframes` always requires `npm install -g hyperframes --ignore-scripts`
- `typescript` major version upgrades are intentional decisions — never auto-update across majors
- After any app upgrade (Antigravity, Claude Desktop, etc.), re-audit ALL skills symlinks
- When updating npm packages with native deps, install them separately last
