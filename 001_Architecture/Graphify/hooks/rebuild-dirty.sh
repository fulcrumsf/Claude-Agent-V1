#!/usr/bin/env bash
# Stop hook: scan dirty sentinels, run `graphify update <domain>` for each,
# refresh REGISTRY.md, then delete the sentinels.
# Uses `graphify update` (AST-only, no LLM cost) — full semantic re-extraction
# requires the user to run `/graphify <domain> --update` interactively.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_lib.sh
source "${SCRIPT_DIR}/_lib.sh"

[ -d "$DIRTY_DIR" ] || exit 0
shopt -s nullglob
sentinels=( "$DIRTY_DIR"/* )
[ ${#sentinels[@]} -gt 0 ] || exit 0

REBUILT=()
for sentinel in "${sentinels[@]}"; do
  slug="$(basename "$sentinel")"
  domain_path="$(get_path_for_domain "$slug")"
  [ -n "$domain_path" ] || { rm -f "$sentinel"; continue; }

  full_path="${WORKSPACE_ROOT}/${domain_path}"
  graph_json="${full_path}/graphify-out/graph.json"

  # Skip rebuild if no graph has been built yet — nothing to update incrementally.
  if [ ! -f "$graph_json" ]; then
    log "rebuild-dirty: ${slug} skipped — no graph yet (run /graphify ${domain_path})"
    rm -f "$sentinel"
    continue
  fi

  log "rebuild-dirty: graphify update ${domain_path}"
  if (cd "$full_path" && graphify update . >/dev/null 2>&1); then
    REBUILT+=( "$slug" )
    rm -f "$sentinel"
  else
    log "rebuild-dirty: ${slug} update failed (sentinel kept)"
  fi
done

if [ ${#REBUILT[@]} -gt 0 ]; then
  "${SCRIPT_DIR}/post-graphify.sh" "${REBUILT[@]}"
fi

exit 0
