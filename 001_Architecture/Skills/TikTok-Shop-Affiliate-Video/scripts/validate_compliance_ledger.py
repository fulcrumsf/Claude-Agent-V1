#!/usr/bin/env python3
"""
validate_compliance_ledger.py — Structural validator for Compliance-Ledger.md.

Every rule block must have: an ID line ("RULE-NNN | Category | SEVERITY"),
a Rule: line, a Source: line, and a Verified: line. This does NOT validate
that the rule text is accurate — only that every entry is complete enough
to be traceable back to a source and a verification date.

Usage:
  python3 validate_compliance_ledger.py <ledger_path>
"""
import re
import sys
from pathlib import Path

HEADER_PATTERN = re.compile(r"^(RULE-\d+)\s*\|\s*([^|]+?)\s*\|\s*(.+)$")


def parse_ledger_entries(ledger_text: str) -> list:
    entries = []
    current = None
    for line in ledger_text.splitlines():
        line = line.strip()
        header_match = HEADER_PATTERN.match(line)
        if header_match:
            if current:
                entries.append(current)
            current = {
                "id": header_match.group(1),
                "category": header_match.group(2).strip(),
                "severity": header_match.group(3).strip(),
                "rule": "",
                "source": "",
                "verified": "",
            }
        elif current is not None:
            if line.startswith("Rule:"):
                current["rule"] = line[len("Rule:"):].strip()
            elif line.startswith("Source:"):
                current["source"] = line[len("Source:"):].strip()
            elif line.startswith("Verified:"):
                current["verified"] = line[len("Verified:"):].strip()
    if current:
        entries.append(current)
    return entries


def validate(ledger_text: str) -> list:
    errors = []
    for entry in parse_ledger_entries(ledger_text):
        for field in ("rule", "source", "verified"):
            if not entry[field]:
                errors.append(f"{entry['id']} is missing a {field} value")
    return errors


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: validate_compliance_ledger.py <ledger_path>")
    text = Path(sys.argv[1]).read_text()
    entries = parse_ledger_entries(text)
    errors = validate(text)
    print(f"Parsed {len(entries)} ledger entries.")
    if errors:
        print(f"{len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("All entries valid.")


if __name__ == "__main__":
    main()
