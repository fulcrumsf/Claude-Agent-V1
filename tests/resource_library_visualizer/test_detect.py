import importlib.util
import pathlib

TOOL = pathlib.Path("001_Architecture/Tools/Resource-Library-Visualizer")


def load(name):
    spec = importlib.util.spec_from_file_location(name, TOOL / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


detect = load("detect")


def test_youtube_id_from_watch_url():
    assert detect.youtube_id("see https://www.youtube.com/watch?v=Xi9zyPTgJL8 now") == "Xi9zyPTgJL8"


def test_youtube_id_from_short_url():
    assert detect.youtube_id("https://youtu.be/G7gK8H6u7Rs?si=abc") == "G7gK8H6u7Rs"


def test_youtube_id_none():
    assert detect.youtube_id("no video here") is None


def test_source_youtube_from_body():
    label, risk = detect.detect_source({}, "watch https://youtu.be/G7gK8H6u7Rs", "App-Building.md", False)
    assert label == "YouTube"
    assert risk is False


def test_source_screenshot_iphone_is_vision_risk():
    label, risk = detect.detect_source(
        {"original_filename": "IMG_8710.PNG"}, "", "Live-Explore.md", True)
    assert label == "Screenshot"
    assert risk is True


def test_source_screenshot_from_tag():
    label, risk = detect.detect_source(
        {"tags": ["screenshot", "video"]}, "", "Foo.md", True)
    assert label == "Screenshot"


def test_source_bookmark_from_web_clip():
    fm = {"source": "https://example.com/page", "url": "https://example.com/page"}
    label, risk = detect.detect_source(fm, "# Example\nclipped article body", "Example.md", True)
    assert label == "Bookmark"


def test_source_md_for_text_only_note():
    label, risk = detect.detect_source({"tags": ["ideas"]}, "just plain text, no image, no link",
                                        "Some-Notion-Export.md", False)
    assert label == "MD"
    assert risk is False


def test_is_structural():
    assert detect.is_structural("Dedup-Review.md") is True
    assert detect.is_structural("rename_log.md") is True
    assert detect.is_structural("OpenCode.md") is False


def test_glyph_color_is_hex():
    c = detect.glyph_color({"type": "tool-doc"}, "Tools")
    assert c.startswith("#") and len(c) == 7
