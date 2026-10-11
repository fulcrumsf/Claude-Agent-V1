#!/usr/bin/env python3
"""Regenerate the Tool Catalog HTML page's DATA array from Tool_Catalog.json.

The published artifact's page chrome (CSS, filter buttons, footer, search JS)
stays untouched — this only replaces the `const DATA = [...]` block, so the
JSON file is the real source of truth and the HTML is a generated view of it.

Usage: python3 render_catalog_html.py <path-to-catalog.html> [--write]
Without --write, prints what would change and exits 0 without touching the file.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CATALOG_JSON = SCRIPT_DIR / "data" / "Tool_Catalog.json"

CATEGORY_ORDER = [
    "YouTube / Content",
    "SEO / Analytics",
    "Social / Affiliate / Commerce",
    "AI Video / Image / Audio Gen",
    "Dev / Agent Tooling",
    "Design / Inspiration / Reference",
    "Platform / Infrastructure / Other",
]


def js_string(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def build_data_js(catalog: dict) -> str:
    by_category: dict[str, list[dict]] = {c: [] for c in CATEGORY_ORDER}
    for tool in catalog["tools"]:
        by_category.setdefault(tool["category"], []).append(tool)

    lines = ["const DATA = ["]
    for category in CATEGORY_ORDER:
        tools = by_category.get(category, [])
        lines.append(f"[{js_string(category)},[")
        for t in tools:
            source = ", ".join(t.get("sources") or [])
            row = [t["name"], t.get("does") or "", source, t.get("source_tag") or "library"]
            lines.append("[" + ",".join(js_string(v) for v in row) + "],")
        lines.append("]],")
    # Any category present in the JSON but not in CATEGORY_ORDER — append so nothing's silently dropped.
    extra = set(by_category) - set(CATEGORY_ORDER)
    for category in sorted(extra):
        tools = by_category[category]
        if not tools:
            continue
        lines.append(f"[{js_string(category)},[")
        for t in tools:
            source = ", ".join(t.get("sources") or [])
            row = [t["name"], t.get("does") or "", source, t.get("source_tag") or "library"]
            lines.append("[" + ",".join(js_string(v) for v in row) + "],")
        lines.append("]],")
    lines.append("];")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html_path", type=Path)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    catalog = json.loads(CATALOG_JSON.read_text())
    html = args.html_path.read_text()

    m = re.search(r"const DATA = \[[\s\S]*?\];", html)
    if not m:
        print("Could not find `const DATA = [...]` block in the HTML file.")
        return 1

    new_data_js = build_data_js(catalog)
    new_html = html[: m.start()] + new_data_js + html[m.end():]

    # Keep the subtitle's tool count in sync too, if it states one.
    new_html = re.sub(
        r"(\d[\d,]*)\s+tools total",
        f"{catalog['meta']['count']} tools total",
        new_html,
    )

    if args.write:
        args.html_path.write_text(new_html)
        print(f"Wrote {catalog['meta']['count']} tools into {args.html_path}")
    else:
        print(f"Would write {catalog['meta']['count']} tools into {args.html_path} (dry run, pass --write to apply)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
