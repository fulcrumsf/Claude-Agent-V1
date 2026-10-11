#!/usr/bin/env python3
"""Tool Catalog — local source-of-truth companion to the published Tool Catalog
artifact (https://claude.ai/artifact/3D9QHYnL7EZ8eunDsHRz4R).

Why this exists: the artifact's data lived only as a hardcoded array inside a
Claude-hosted HTML page, which no script can read or write. This JSON file is
the real source of truth now; the artifact gets regenerated from it when a
live Claude session republishes it.

Every write path dedup-checks by URL first (via dedup_check.py) — never add a
duplicate row for the same product, and never duplicate-ingest the same
bookmark. Catalog entries are per-PRODUCT (one row per tool), not per-file —
a tool bookmarked from 3 different sources is 1 row with 3 sources, not 3 rows.

Usage:
    python3 tool_catalog.py add --name "X" --url "https://..." --category "..." \\
        --does "one-line description" --source "path/to/note.md" [--kind github-repo]
    python3 tool_catalog.py find "turn long videos into shorts"
    python3 tool_catalog.py status
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
AGENT_OS = SCRIPT_DIR.parents[2]
CATALOG_PATH = SCRIPT_DIR / "data" / "Tool_Catalog.json"

sys.path.insert(0, str(AGENT_OS / "001_Architecture" / "Scripts"))
from dedup_check import normalize_url, find_duplicate_by_url  # noqa: E402


def load_catalog() -> dict:
    if not CATALOG_PATH.exists():
        return {"meta": {"count": 0}, "tools": []}
    return json.loads(CATALOG_PATH.read_text())


def save_catalog(catalog: dict) -> None:
    catalog["meta"]["count"] = len(catalog["tools"])
    CATALOG_PATH.write_text(json.dumps(catalog, indent=2))


def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s or "unnamed"


def find_by_url_in_catalog(catalog: dict, url: str) -> dict | None:
    """Dedup check #1: does this exact product URL already have a row?"""
    if not url:
        return None
    target = normalize_url(url)
    for tool in catalog["tools"]:
        if tool.get("url") and normalize_url(tool["url"]) == target:
            return tool
    return None


def cmd_add(args: argparse.Namespace) -> int:
    catalog = load_catalog()

    # Dedup gate #1: already a row in the catalog for this exact URL?
    existing = find_by_url_in_catalog(catalog, args.url) if args.url else None
    if existing:
        if args.source and args.source not in existing["sources"]:
            existing["sources"].append(args.source)
            save_catalog(catalog)
            print(f"DUPLICATE — already catalogued as '{existing['name']}' ({existing['id']}). "
                  f"Added '{args.source}' as a new source, no new row created.")
        else:
            print(f"DUPLICATE — already catalogued as '{existing['name']}' ({existing['id']}). "
                  f"No change (source already recorded).")
        return 0

    # Dedup gate #2: a Resource Library note already exists for this URL,
    # even if it never made it into the catalog (e.g. ingested before this
    # tool existed). Still worth flagging rather than silently duplicating.
    if args.url:
        rl_match = find_duplicate_by_url(args.url)
        if rl_match and not args.force:
            print(f"NOTE ALREADY EXISTS at {rl_match} but has no catalog row yet. "
                  f"Re-run with --force to catalog it anyway, or check why it wasn't caught earlier.")
            return 1

    record_id = slugify(args.name)
    existing_ids = {t["id"] for t in catalog["tools"]}
    base_id, n = record_id, 2
    while record_id in existing_ids:
        record_id = f"{base_id}-{n}"
        n += 1

    catalog["tools"].append({
        "id": record_id,
        "name": args.name,
        "url": args.url,
        "kind": args.kind,
        "category": args.category or "Uncategorized",
        "does": args.does or "",
        "use_for": [],
        "pricing": None,
        "status": "bookmarked",
        "sources": [args.source] if args.source else [],
        "source_tag": "ingest",
        "first_seen": args.first_seen or "unknown",
        "notes": "",
    })
    save_catalog(catalog)
    print(f"Added '{args.name}' as new row ({record_id}).")
    return 0


def cmd_find(args: argparse.Namespace) -> int:
    catalog = load_catalog()
    q = args.query.lower()
    hits = [
        t for t in catalog["tools"]
        if q in t["name"].lower() or q in (t.get("does") or "").lower()
        or any(q in u.lower() for u in t.get("use_for", []))
    ]
    if not hits:
        print(f'No matches for "{args.query}" ({len(catalog["tools"])} tools in catalog).')
        return 0
    print(f'{len(hits)} match(es) for "{args.query}":')
    for t in hits:
        print(f"  - {t['name']} — {t['does']}")
        print(f"    category: {t['category']} | status: {t['status']} | url: {t.get('url') or '(none)'}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    catalog = load_catalog()
    tools = catalog["tools"]
    with_url = sum(1 for t in tools if t.get("url"))
    print(f"{len(tools)} tools total, {with_url} with a known URL ({len(tools) - with_url} cannot be "
          f"URL-deduped yet).")
    by_status: dict[str, int] = {}
    for t in tools:
        by_status[t["status"]] = by_status.get(t["status"], 0) + 1
    for status, n in sorted(by_status.items()):
        print(f"  {status}: {n}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Add a tool, dedup-checked by URL first")
    p_add.add_argument("--name", required=True)
    p_add.add_argument("--url", default=None)
    p_add.add_argument("--category", default=None)
    p_add.add_argument("--does", default=None)
    p_add.add_argument("--kind", default=None)
    p_add.add_argument("--source", default=None, help="Resource Library path this was found in")
    p_add.add_argument("--first-seen", dest="first_seen", default=None)
    p_add.add_argument("--force", action="store_true",
                        help="Add even if a Resource Library note already exists for this URL")
    p_add.set_defaults(func=cmd_add)

    p_find = sub.add_parser("find", help="Keyword search by name/description/use_for")
    p_find.add_argument("query")
    p_find.set_defaults(func=cmd_find)

    p_status = sub.add_parser("status", help="Summary counts")
    p_status.set_defaults(func=cmd_status)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
