from check_tos_freshness import should_refresh, diff_snapshots


def test_should_refresh_false_when_recent():
    from datetime import date, timedelta
    recent = (date.today() - timedelta(days=3)).isoformat()
    assert should_refresh(recent, category=None) is False


def test_should_refresh_true_when_older_than_threshold():
    from datetime import date, timedelta
    old = (date.today() - timedelta(days=20)).isoformat()
    assert should_refresh(old, category=None) is True


def test_should_refresh_true_for_always_escalate_category_even_if_recent():
    from datetime import date, timedelta
    recent = (date.today() - timedelta(days=1)).isoformat()
    assert should_refresh(recent, category="Health") is True
    assert should_refresh(recent, category="weight-management") is True


def test_should_refresh_true_for_category_substring_match():
    from datetime import date, timedelta
    recent = (date.today() - timedelta(days=1)).isoformat()
    assert should_refresh(recent, category="Health & Wellness Supplements") is True
    assert should_refresh(recent, category="Weight-Management Add-Ons") is True


def test_should_refresh_true_when_no_prior_date():
    assert should_refresh(None, category=None) is True


def test_diff_snapshots_detects_changed_line():
    old = "Rule: Comparing to a specific competitor is not allowed.\n"
    new = "Rule: Comparing to a specific competitor is allowed with permission.\n"
    diffs = diff_snapshots(old, new)
    assert any("allowed with permission" in d for d in diffs)


def test_diff_snapshots_empty_when_identical():
    text = "Rule: same text\n"
    assert diff_snapshots(text, text) == []


def test_load_last_verified_ignores_all_failed_run(tmp_path):
    from check_tos_freshness import load_last_verified
    log = tmp_path / "log.md"
    log.write_text("\n## 2026-07-12 — ALL FETCHES FAILED\nChecked 61 source URL(s) (0 succeeded, 61 failed).\n")
    assert load_last_verified(log) is None


def test_load_last_verified_recognizes_verified_run(tmp_path):
    from check_tos_freshness import load_last_verified
    log = tmp_path / "log.md"
    log.write_text("\n## 2026-07-12 — VERIFIED\nChecked 61 source URL(s) (61 succeeded, 0 failed).\n")
    assert load_last_verified(log) == "2026-07-12"
