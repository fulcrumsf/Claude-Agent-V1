from generate_youtube_package import build_titles, build_description

def test_build_titles_returns_three_formulas():
    titles = build_titles(subject="the anglerfish", hook_fact="uses bacteria to glow")
    assert len(titles) == 3
    assert all(isinstance(t, str) and len(t) <= 100 for t in titles)

def test_description_first_line_is_a_question():
    desc = build_description(subject="anglerfish bioluminescence", chapters=[("0:00", "Hook")])
    first_line = desc.strip().split("\n")[0]
    assert first_line.strip().endswith("?")
