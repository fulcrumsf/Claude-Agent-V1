# test_validate_compliance_ledger.py
from validate_compliance_ledger import parse_ledger_entries, validate

VALID_FIXTURE = """
RULE-001 | Visual/Branding | HARD BLOCK
Rule: Do not show any third-party logo without permission.
Source: Best Practices for Promotional Content.md (line 138)
Verified: 2026-07-11

RULE-002 | Claims/Discounts | HARD BLOCK
Rule: The discounted price shown must exactly match the product detail page.
Source: Misleading Discount Content Guide.md (line 10)
Verified: 2026-07-11
"""

INVALID_FIXTURE = """
RULE-001 | Visual/Branding | HARD BLOCK
Rule: Do not show any third-party logo without permission.
Verified: 2026-07-11
"""


def test_parses_two_entries():
    entries = parse_ledger_entries(VALID_FIXTURE)
    assert len(entries) == 2
    assert entries[0]["id"] == "RULE-001"
    assert entries[0]["category"] == "Visual/Branding"
    assert entries[0]["severity"] == "HARD BLOCK"
    assert "third-party logo" in entries[0]["rule"]
    assert "Best Practices" in entries[0]["source"]
    assert entries[0]["verified"] == "2026-07-11"


def test_validate_passes_on_complete_entries():
    assert validate(VALID_FIXTURE) == []


def test_validate_flags_missing_source():
    errors = validate(INVALID_FIXTURE)
    assert len(errors) == 1
    assert "RULE-001" in errors[0]
    assert "source" in errors[0].lower()
