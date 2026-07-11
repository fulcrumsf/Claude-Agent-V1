from compliance_vision_scan import parse_verdict


def test_parse_verdict_flag_when_logo_mentioned():
    response = "Frame 2 shows a visible Nike swoosh logo on a shoe in the background.\n\nVERDICT: FLAG"
    assert parse_verdict(response) == "FLAG"


def test_parse_verdict_clear_when_no_issues():
    response = "No third-party logos, watermarks, or brand marks visible in any frame.\n\nVERDICT: CLEAR"
    assert parse_verdict(response) == "CLEAR"


def test_parse_verdict_defaults_to_flag_when_ambiguous():
    # Fail safe: if the model doesn't emit a clear VERDICT line, treat as FLAG
    # so nothing slips through on a malformed response.
    response = "The frames look fine I guess."
    assert parse_verdict(response) == "FLAG"
