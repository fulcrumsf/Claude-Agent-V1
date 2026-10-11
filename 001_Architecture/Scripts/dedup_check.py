#!/usr/bin/env python3
"""Shared URL/title dedup check — used by the ingest skill and tool_catalog.py.

Mirrors the dedup pattern already proven for images in process_image_ingest.py
(exact-match first, then a softer title flag), ported to text-note frontmatter
and to Tool_Catalog.json entries. Read-only: callers decide what to do with a match.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

AGENT_OS = Path(__file__).resolve().parents[2]
RESOURCE_LIBRARY = AGENT_OS / "007_Resource_Library"

# Tracking/session params that make two otherwise-identical URLs look different.
_STRIP_QUERY_KEYS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term",
    "ref", "si", "feature", "fbclid", "gclid", "via",
}

_FRONTMATTER_URL_RE = re.compile(r"^url:\s*(\S+)\s*$", re.MULTILINE)
_FRONTMATTER_TITLE_RE = re.compile(r'^title:\s*"?([^"\n]+)"?\s*$', re.MULTILINE)


def normalize_url(url: str) -> str:
    """Lowercase scheme/host, strip trailing slash, drop tracking params and fragment."""
    if not url:
        return ""
    url = url.strip().strip('"').strip("'")
    parts = urlsplit(url)
    scheme = parts.scheme.lower() or "https"
    netloc = parts.netloc.lower()
    path = parts.path.rstrip("/")
    kept = [(k, v) for k, v in parse_qsl(parts.query) if k.lower() not in _STRIP_QUERY_KEYS]
    query = urlencode(sorted(kept))
    return urlunsplit((scheme, netloc, path, query, ""))


def _read_frontmatter_field(text: str, pattern: re.Pattern) -> str | None:
    m = pattern.search(text)
    return m.group(1).strip() if m else None


def find_duplicate_by_url(url: str, search_root: Path = RESOURCE_LIBRARY) -> Path | None:
    """Scan every .md frontmatter under search_root for a matching url: field.
    Returns the first matching file path, or None. O(n) file scan — fine at
    this corpus size (low thousands of files); revisit if it ever gets slow.
    """
    target = normalize_url(url)
    if not target:
        return None
    for path in search_root.rglob("*.md"):
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        if "url:" not in text:
            continue
        found = _read_frontmatter_field(text, _FRONTMATTER_URL_RE)
        if found and normalize_url(found) == target:
            return path
    return None


def find_duplicate_by_title(title: str, folder: Path) -> Path | None:
    """Soft check: does a note with this exact title already exist in `folder`?
    Title-only match is weaker evidence than a URL match — callers should treat
    this as a flag (e.g. tag `possible-duplicate`), not an automatic skip.
    """
    if not folder.is_dir():
        return None
    target = title.strip().lower()
    for path in folder.glob("*.md"):
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        found = _read_frontmatter_field(text, _FRONTMATTER_TITLE_RE)
        if found and found.strip().lower() == target:
            return path
    return None


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: dedup_check.py <url> [search_root]", file=sys.stderr)
        return 1
    url = sys.argv[1]
    root = Path(sys.argv[2]) if len(sys.argv) > 2 else RESOURCE_LIBRARY
    match = find_duplicate_by_url(url, root)
    if match:
        print(f"DUPLICATE: {match}")
        return 0
    print("NO MATCH")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
