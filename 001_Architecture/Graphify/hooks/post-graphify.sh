#!/usr/bin/env bash
# Refresh REGISTRY.md with current node counts and last-built timestamp for
# rebuilt domains. Args: list of domain slugs that were rebuilt.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_lib.sh
source "${SCRIPT_DIR}/_lib.sh"

[ "$#" -gt 0 ] || exit 0
[ -f "$REGISTRY" ] || { log "post-graphify: REGISTRY.md missing"; exit 0; }

NOW="$(date -u +%Y-%m-%dT%H:%MZ)"

# Build the JSON payload of updates for the python rewriter
UPDATES_JSON=$(python3 -c "
import json, sys
slugs = sys.argv[1:]
print(json.dumps(slugs))
" "$@")

python3 - "$REGISTRY" "$UPDATES_JSON" "$NOW" "$WORKSPACE_ROOT" <<'PY'
import json, re, sys
from pathlib import Path

registry_path = Path(sys.argv[1])
slugs = json.loads(sys.argv[2])
now = sys.argv[3]
ws = Path(sys.argv[4])

# slug → relative path mapping (must match _lib.sh)
DOMAINS = {
  "video-editor": "002_Content-Creation/Video_Editor",
  "whop-clipping": "002_Content-Creation/Whop_Clipping",
  "social-media": "002_Content-Creation/Social_Media_Marketing",
  "architecture": "001_Architecture",
  "apps": "003_Apps",
  "games": "004_Games",
  "ecommerce": "005_Ecommerce",
  "resource-library": "007_Resource_Library",
}

text = registry_path.read_text()

for slug in slugs:
  rel = DOMAINS.get(slug)
  if not rel:
    continue
  graph_json = ws / rel / "graphify-out" / "graph.json"
  node_count = 0
  if graph_json.exists():
    try:
      node_count = len(json.loads(graph_json.read_text()).get("nodes", []))
    except Exception:
      node_count = 0
  # Match the row whose Path cell contains this rel path
  pattern = re.compile(
    r"(\| [^|]+ \| `" + re.escape(rel) + r"/?` \| [^|]+ \| )(\d+|—)( \| )([^|]+)( \| )([^|]+)(\s*\|)"
  )
  def repl(m):
    return f"{m.group(1)}{node_count}{m.group(3)}built{m.group(5)}{now}{m.group(7)}"
  text, n = pattern.subn(repl, text)
  if n == 0:
    pass  # row layout drifted; skip silently

registry_path.write_text(text)
PY

log "post-graphify: REGISTRY.md updated for $*"
