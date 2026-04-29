#!/bin/bash
# MCP Gateway Server — Production startup script
# Called by macOS LaunchAgent on login

export PATH="/opt/homebrew/bin:$PATH"
export HOME="/Users/tonymacbook2025"

# Load environment secrets (API keys, tokens)
if [ -f "$HOME/.env-secrets" ]; then
  set -a
  source "$HOME/.env-secrets"
  set +a
fi

PROJECT_DIR="$HOME/Documents/App Building/003_App-Development/MCP-Gateway-Controller"
cd "$PROJECT_DIR/server" || exit 1

# Run the server using ts-node ESM loader
exec node --loader ts-node/esm src/index.ts
