#!/usr/bin/env bash
# PostToolUse hook: when Edit/Write/MultiEdit touches a file inside a tracked
# domain, drop a sentinel file so the Stop hook knows which domain to rebuild.
#
# Hook input (JSON on stdin) contains tool_input.file_path for Edit/Write/MultiEdit.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_lib.sh
source "${SCRIPT_DIR}/_lib.sh"

# Read JSON from stdin, extract file_path (handle both Write and Edit shapes)
INPUT="$(cat)"
FILE_PATH="$(printf '%s' "$INPUT" | python3 -c "
import json, sys
try:
  data = json.load(sys.stdin)
  ti = data.get('tool_input') or {}
  print(ti.get('file_path') or ti.get('path') or '')
except Exception:
  print('')
" 2>/dev/null || echo "")"

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

DOMAIN="$(get_domain_for_path "$FILE_PATH")"
if [ -z "$DOMAIN" ]; then
  exit 0
fi

mkdir -p "$DIRTY_DIR"
touch "${DIRTY_DIR}/${DOMAIN}"
log "mark-dirty: ${DOMAIN} (${FILE_PATH})"

exit 0
