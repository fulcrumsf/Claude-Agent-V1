import importlib.util
import pathlib
from PIL import Image

TOOL = pathlib.Path("001_Architecture/Tools/Resource-Library-Visualizer")


def load(name):
    spec = importlib.util.spec_from_file_location(name, TOOL / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


thumbs = load("thumbs")


def test_youtube_poster_url():
    assert thumbs.youtube_poster_url("abcdefghijk") == "https://img.youtube.com/vi/abcdefghijk/hqdefault.jpg"


def test_ensure_thumb_generates(tmp_path, monkeypatch):
    monkeypatch.setattr(thumbs.config, "THUMB_CACHE", str(tmp_path / "cache"))
    monkeypatch.setattr(thumbs.config, "RESOURCE_LIB", str(tmp_path))
    src = tmp_path / "Big.png"
    Image.new("RGB", (900, 600), "red").save(src)
    out = thumbs.ensure_thumb(str(src))
    assert out and pathlib.Path(out).is_file()
    assert Image.open(out).width == thumbs.config.THUMB_W


def test_ensure_thumb_cache_hit(tmp_path, monkeypatch):
    monkeypatch.setattr(thumbs.config, "THUMB_CACHE", str(tmp_path / "cache"))
    monkeypatch.setattr(thumbs.config, "RESOURCE_LIB", str(tmp_path))
    src = tmp_path / "X.png"
    Image.new("RGB", (400, 400), "blue").save(src)
    a = thumbs.ensure_thumb(str(src))
    mtime1 = pathlib.Path(a).stat().st_mtime_ns
    b = thumbs.ensure_thumb(str(src))
    assert a == b
    assert pathlib.Path(b).stat().st_mtime_ns == mtime1   # not regenerated
