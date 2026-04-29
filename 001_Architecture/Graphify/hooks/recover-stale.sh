#!/usr/bin/env bash
# SessionStart hook: if dirty sentinels survived a previous session (crash,
# session killed, etc.), trigger rebuild now so the graphs are fresh before
# any work begins.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_lib.sh
source "${SCRIPT_DIR}/_lib.sh"

[ -d "$DIRTY_DIR" ] || exit 0
shopt -s nullglob
sentinels=( "$DIRTY_DIR"/* )
[ ${#sentinels[@]} -gt 0 ] || exit 0

log "recover-stale: ${#sentinels[@]} stale sentinel(s) found, rebuilding"
exec "${SCRIPT_DIR}/rebuild-dirty.sh"
