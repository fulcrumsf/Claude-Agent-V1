#!/usr/bin/env bash
# PostToolUse hook: after Write/Edit/MultiEdit creates or touches a file,
# check the file path against the workspace naming convention
# (001_Architecture/Scripts/check_naming_convention.py) and surface any
# violation back into the agent's context immediately, instead of relying on
# the agent or Tony to notice it later.
#
# Built 2026-08-16 after repeated real violations (scene_02/, scene_05b.png,
# etc. created directly from lowercase internal identifiers) went unnoticed
# until Tony caught them by hand. This makes that check mechanical.
#
# Hook input (JSON on stdin) contains tool_input.file_path for Write/Edit,
# or tool_response.filePath as a fallback.

set -euo pipefail

CHECKER="/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/check_naming_convention.py"

INPUT="$(cat)"
FILE_PATH="$(printf '%s' "$INPUT" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    ti = data.get('tool_input') or {}
    tr = data.get('tool_response') or {}
    print(ti.get('file_path') or ti.get('path') or tr.get('filePath') or '')
except Exception:
    print('')
" 2>/dev/null || echo "")"

if [ -z "$FILE_PATH" ]; then
    exit 0
fi

VIOLATIONS="$(python3 "$CHECKER" "$FILE_PATH" 2>&1 || true)"

if printf '%s' "$VIOLATIONS" | grep -q "NAMING CONVENTION VIOLATIONS"; then
    python3 -c "
import json, sys
msg = sys.argv[1]
print(json.dumps({
    'hookSpecificOutput': {
        'hookEventName': 'PostToolUse',
        'additionalContext': 'NAMING CONVENTION CHECK FAILED for the file just written — ' + msg.replace(chr(10), ' ') + ' Fix the name now (Title_Case_With_Underscores, no spaces, .py exempt) before continuing, per Agent-OS/CLAUDE.md.'
    }
}))
" "$VIOLATIONS"
fi

exit 0
