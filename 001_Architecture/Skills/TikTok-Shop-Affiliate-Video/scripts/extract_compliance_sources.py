#!/usr/bin/env python3
"""
extract_compliance_sources.py — Pulls official TikTok Seller University source
URLs embedded inside the ingested TOS bundle, deduped by knowledge_id, so the
freshness checker (check_tos_freshness.py) has a grounded, non-guessed URL list.

Usage:
  python3 extract_compliance_sources.py <tos_folder> <out_json_path>
"""
import json
import re
import sys
from pathlib import Path

KNOWLEDGE_ID_PATTERN = re.compile(r"knowledge_id=(\d+)")
BASE_URL = "https://seller-us.tiktok.com/university/essay?knowledge_id={}"


def extract_knowledge_ids(tos_folder: Path) -> dict:
    ids = {}
    for md_file in sorted(Path(tos_folder).glob("*.md")):
        text = md_file.read_text(errors="ignore")
        for match in KNOWLEDGE_ID_PATTERN.finditer(text):
            kid = match.group(1)
            ids.setdefault(kid, BASE_URL.format(kid))
    return ids


def write_sources_json(sources: dict, out_path: Path) -> None:
    Path(out_path).write_text(json.dumps(sources, indent=2, sort_keys=True))


def main():
    if len(sys.argv) < 3:
        sys.exit("Usage: extract_compliance_sources.py <tos_folder> <out_json_path>")
    sources = extract_knowledge_ids(Path(sys.argv[1]))
    write_sources_json(sources, Path(sys.argv[2]))
    print(f"Extracted {len(sources)} unique source URLs -> {sys.argv[2]}")


if __name__ == "__main__":
    main()
