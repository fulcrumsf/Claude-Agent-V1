import importlib.util
import pathlib

TOOL = pathlib.Path("001_Architecture/Tools/Resource-Library-Visualizer")


def load(name):
    spec = importlib.util.spec_from_file_location(name, TOOL / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


notes = load("notes")


def test_parse_note_valid(tmp_path):
    p = tmp_path / "A.md"
    p.write_text('---\ntitle: "A"\ntags:\n  - x\n---\nbody here\n')
    fm, body = notes.parse_note(str(p))
    assert fm["title"] == "A"
    assert fm["tags"] == ["x"]
    assert body.strip() == "body here"


def test_parse_note_no_frontmatter(tmp_path):
    p = tmp_path / "B.md"
    p.write_text("# just markdown\n")
    fm, body = notes.parse_note(str(p))
    assert fm == {}
    assert "just markdown" in body


def test_parse_note_broken_yaml_recovers_title_and_tags(tmp_path):
    p = tmp_path / "C.md"
    p.write_text(
        '---\n'
        'title: "React Bits Web"\n'
        'category: app-dev\n'
        'tags:\n'
        '  - web-development\n'
        '  - react\n'
        'ai_description: "a tool called "React Bits" with "quotes" that break yaml"\n'
        '---\nbody\n'
    )
    fm, body = notes.parse_note(str(p))
    assert fm["title"] == "React Bits Web"
    assert fm["category"] == "app-dev"
    assert fm["tags"] == ["web-development", "react"]
    assert body.strip() == "body"


def test_find_sibling_image(tmp_path):
    (tmp_path / "OpenCode.md").write_text("x")
    (tmp_path / "OpenCode.png").write_bytes(b"\x89PNG")
    got = notes.find_sibling_image(str(tmp_path / "OpenCode.md"))
    assert got == str(tmp_path / "OpenCode.png")


def test_find_sibling_image_missing(tmp_path):
    (tmp_path / "Lonely.md").write_text("x")
    assert notes.find_sibling_image(str(tmp_path / "Lonely.md")) is None


def test_build_index_pairs_and_sorts(tmp_path):
    d = tmp_path / "Tools"
    d.mkdir()
    (d / "New.md").write_text('---\ntitle: "New"\nsummary: "s"\nenriched: 2026-09-05\n---\nx')
    (d / "New.png").write_bytes(b"\x89PNG\r\n")
    (d / "Old.md").write_text('---\ntitle: "Old"\ncreated: 2026-01-01\n---\nhttps://youtu.be/abcdefghijk')
    idx = notes.build_index(str(tmp_path))
    assert [c["title"] for c in idx] == ["New", "Old"]        # newest first
    assert idx[0]["kind"] == "image"
    assert idx[1]["kind"] == "youtube"
    assert idx[1]["youtube_id"] == "abcdefghijk"


def test_build_index_text_only_note(tmp_path):
    d = tmp_path / "Tools"
    d.mkdir()
    (d / "Dedup-Review.md").write_text('---\ntitle: "Dedup Review"\n---\nno image no video')
    idx = notes.build_index(str(tmp_path))
    assert idx[0]["kind"] == "text"
    assert idx[0]["glyph_color"].startswith("#")
