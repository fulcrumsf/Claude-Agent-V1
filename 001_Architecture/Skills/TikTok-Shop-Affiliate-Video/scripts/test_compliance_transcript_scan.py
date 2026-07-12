from compliance_transcript_scan import banned_phrase_patterns, scan_transcript_for_violations


def test_banned_phrase_patterns_includes_guarantee_and_cure():
    patterns = banned_phrase_patterns()
    assert any("guarantee" in p.lower() for p in patterns)
    assert any("cure" in p.lower() for p in patterns)


def test_scan_detects_banned_phrase_case_insensitive():
    transcript = "This pen will absolutely CURE your handwriting problems forever."
    violations = scan_transcript_for_violations(transcript, banned_phrase_patterns())
    assert any("cure" in v.lower() for v in violations)


def test_scan_returns_empty_for_clean_transcript():
    transcript = "This pen writes smoothly and comes in six colors, in my experience."
    violations = scan_transcript_for_violations(transcript, banned_phrase_patterns())
    assert violations == []


def test_scan_detects_multiple_distinct_violations():
    transcript = "Guaranteed to work, clinically proven, and it will cure your problems."
    violations = scan_transcript_for_violations(transcript, banned_phrase_patterns())
    assert len(violations) >= 3


def test_scan_returns_empty_list_for_empty_transcript():
    # An empty transcript has no violations by pure substring matching —
    # scan_video's caller is responsible for treating "no transcript" as FLAG,
    # not scan_transcript_for_violations itself (which correctly reports
    # "no banned phrases found" for empty input, a different question than
    # "was there content to check at all").
    assert scan_transcript_for_violations("", banned_phrase_patterns()) == []
    assert scan_transcript_for_violations("   ", banned_phrase_patterns()) == []
