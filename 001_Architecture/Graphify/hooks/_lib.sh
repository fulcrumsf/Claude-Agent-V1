#!/usr/bin/env bash
# Shared helpers for Graphify federation hooks.
# Sourced by mark-dirty.sh, rebuild-dirty.sh, recover-stale.sh, post-graphify.sh

set -euo pipefail

# Workspace root (resolves regardless of where the hook is invoked from)
WORKSPACE_ROOT="/Users/tonymacbook2025/Documents/Claude-Agent"

# Where dirty sentinels live (one empty file per domain that needs rebuild)
DIRTY_DIR="${WORKSPACE_ROOT}/.graphify/dirty"

# Federation registry
REGISTRY="${WORKSPACE_ROOT}/001_Architecture/Graphify/REGISTRY.md"

# Hook log (append-only)
HOOK_LOG="${WORKSPACE_ROOT}/.graphify/hooks.log"

# Domains that have their own graph. Each entry: "<sentinel-slug>:<relative-path>"
# Order matters — longer paths first so prefix matching is unambiguous.
DOMAINS=(
  "video-editor:002_Content-Creation/Video_Editor"
  "whop-clipping:002_Content-Creation/Whop_Clipping"
  "social-media:002_Content-Creation/Social_Media_Marketing"
  "architecture:001_Architecture"
  "apps:003_Apps"
  "games:004_Games"
  "ecommerce:005_Ecommerce"
  "resource-library:007_Resource_Library"
)

log() {
  mkdir -p "$(dirname "$HOOK_LOG")"
  printf '[%s] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >> "$HOOK_LOG"
}

# Map an absolute or workspace-relative file path to a domain slug.
# Echoes "" if the path doesn't fall inside a tracked domain.
get_domain_for_path() {
  local path="$1"
  # Strip workspace root prefix if absolute
  case "$path" in
    "$WORKSPACE_ROOT"/*) path="${path#$WORKSPACE_ROOT/}" ;;
  esac
  for entry in "${DOMAINS[@]}"; do
    local slug="${entry%%:*}"
    local prefix="${entry#*:}"
    case "$path" in
      "$prefix"/*|"$prefix") echo "$slug"; return 0 ;;
    esac
  done
  echo ""
}

# Get the workspace-relative folder for a domain slug.
get_path_for_domain() {
  local slug="$1"
  for entry in "${DOMAINS[@]}"; do
    if [ "${entry%%:*}" = "$slug" ]; then
      echo "${entry#*:}"
      return 0
    fi
  done
  echo ""
}

# Count nodes in a domain's graph.json (returns 0 if missing/invalid)
read_node_count() {
  local domain_path="$1"
  local graph="${WORKSPACE_ROOT}/${domain_path}/graphify-out/graph.json"
  if [ ! -f "$graph" ]; then echo 0; return; fi
  python3 -c "import json,sys
try:
  d=json.load(open('$graph'))
  print(len(d.get('nodes', [])))
except Exception:
  print(0)" 2>/dev/null || echo 0
}
