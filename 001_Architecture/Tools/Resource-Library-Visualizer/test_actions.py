from conftest import load


def _mod(monkeypatch, root):
    actions = load("actions")
    monkeypatch.setattr(actions.config, "RESOURCE_LIB", str(root))
    monkeypatch.setattr(actions.config, "DELETE_DIR", str(root.parent / "delete"))
    monkeypatch.setattr(actions.queue, "log_delete", lambda *a, **k: None)
    return actions


def test_move_to_delete_takes_note_and_image(monkeypatch, rl_fixture):
    a = _mod(monkeypatch, rl_fixture)
    moved = a.move_to_delete("Tools/OpenCode.md")
    assert not (rl_fixture / "Tools" / "OpenCode.md").exists()
    assert not (rl_fixture / "Tools" / "OpenCode.png").exists()
    assert any(p.endswith("OpenCode.md") for p in moved)
    assert (rl_fixture.parent / "delete" / "Tools" / "OpenCode.png").exists()


def test_move_note_takes_note_and_image(monkeypatch, rl_fixture):
    a = _mod(monkeypatch, rl_fixture)
    monkeypatch.setattr(a.config, "CATEGORY_FOLDERS", ["Tools", "Content_Ideas"])
    new_rel = a.move_note("Tools/OpenCode.md", "Content_Ideas")
    assert new_rel == "Content_Ideas/OpenCode.md"
    assert not (rl_fixture / "Tools" / "OpenCode.md").exists()
    assert (rl_fixture / "Content_Ideas" / "OpenCode.md").exists()
    assert (rl_fixture / "Content_Ideas" / "OpenCode.png").exists()


def test_move_note_rejects_bad_dest(monkeypatch, rl_fixture):
    a = _mod(monkeypatch, rl_fixture)
    monkeypatch.setattr(a.config, "CATEGORY_FOLDERS", ["Tools"])
    import pytest
    with pytest.raises(ValueError):
        a.move_note("Tools/OpenCode.md", "../Evil")


def test_rewrite_note_fixes_fields(monkeypatch, rl_fixture):
    a = _mod(monkeypatch, rl_fixture)
    a.rewrite_note("Tools/MisLabel.md", {
        "title": "Cool GitHub Repo",
        "summary": "Actually an unrelated OSS project.",
        "url": "https://github.com/foo/bar",
        "tags": "github-repo, oss",
    })
    fm, body = load("notes").parse_note(str(rl_fixture / "Tools" / "MisLabel.md"))
    assert fm["title"] == "Cool GitHub Repo"
    assert fm["url"] == "https://github.com/foo/bar"
    assert fm["tags"] == ["github-repo", "oss"]
    assert fm["original_filename"] == "IMG_8710.PNG"   # untouched


def test_rewrite_note_replaces_body(monkeypatch, rl_fixture):
    a = _mod(monkeypatch, rl_fixture)
    a.rewrite_note("Tutorials/Vid.md", {"body": "new body\n"})
    _, body = load("notes").parse_note(str(rl_fixture / "Tutorials" / "Vid.md"))
    assert body.strip() == "new body"


def test_rewrite_note_raw_writes_verbatim_yaml(monkeypatch, rl_fixture):
    a = _mod(monkeypatch, rl_fixture)
    raw = 'title: "New Title"\ncategory: personal\ntags:\n  - one\n  - two\n'
    parsed = a.rewrite_note_raw("Tools/MisLabel.md", raw)
    assert parsed["title"] == "New Title"
    fm, _ = load("notes").parse_note(str(rl_fixture / "Tools" / "MisLabel.md"))
    assert fm["title"] == "New Title"
    assert fm["tags"] == ["one", "two"]


def test_rewrite_note_raw_rejects_invalid_yaml(monkeypatch, rl_fixture):
    a = _mod(monkeypatch, rl_fixture)
    import pytest
    with pytest.raises(ValueError):
        a.rewrite_note_raw("Tools/MisLabel.md", 'title: "unterminated')


def test_rerun_ai_returns_before_after(monkeypatch, rl_fixture):
    a = _mod(monkeypatch, rl_fixture)
    fake = lambda img: {"title": "Corrected Title", "summary": "fixed", "tags": ["github-repo"]}
    out = a.rerun_ai("Tools/MisLabel.md", vision_fn=fake)
    assert out["before"]["title"] == "Photoshop Plugin"
    assert out["after"]["title"] == "Corrected Title"
    assert out["applied"] is False


def test_estimate_rerun_cost():
    a = load("actions")
    assert a.estimate_rerun_cost(10) == 0.10
