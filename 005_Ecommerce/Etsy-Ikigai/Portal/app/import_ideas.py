"""Import a research batch into the idea pool (the research job runs outside the Portal).

    python -m app.import_ideas batch.json          # add, cap enforced, duplicates skipped
    python -m app.import_ideas --room              # how many ideas fit right now (ask before researching)
    python -m app.import_ideas batch.json --db path/to/portal.db

batch.json is a list (or {"items": [...]}) of:
  {"title": "...", "description": "...", "lane": "rising|steady|test", "score": 0-100,
   "source": "research",
   "evidence": {"why_buyer": "...", "why_now": "...", "competitors": "...", "warning": "...",
                "sources": ["Alura keyword ...", "Google Trends ..."]}}

The same thing over HTTP: POST /ikigai/api/ideas/import with the JSON body.
Before researching, read data/Taste_Profile.md (Tony's approvals, denials and reasons).
"""
import argparse
import json
import sys

from . import ideas
from .db import connect, load_config


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m app.import_ideas")
    ap.add_argument("batch", nargs="?")
    ap.add_argument("--db")
    ap.add_argument("--room", action="store_true")
    a = ap.parse_args(argv)
    con = connect(a.db)
    settings = load_config("settings")
    if a.room or not a.batch:
        print(json.dumps({"room": ideas.room(con, settings), "suggested_batch":
                          min(ideas.room(con, settings), ideas.cfg(settings, "refresh_batch"))}))
        return 0
    data = json.loads(open(a.batch).read())
    items = data.get("items") if isinstance(data, dict) else data
    try:
        res = ideas.add_to_pool(con, items, settings)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    print(json.dumps({**res, "added": len(res["added"])}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
