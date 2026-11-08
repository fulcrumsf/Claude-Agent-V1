"""Mockup step (slots 1, 2, 7 + fixed images). PhotoCraft itself is not run here; the art-fitting, the Etsy
size cap and the missing-file refusals are. The real swap was proven on Book Club Cat (2026-11-05)."""
from pathlib import Path

import pytest
from PIL import Image

from app import mockups
from app.pipeline.base import NotConfigured


def test_fit_art_cover_crops_never_stretches(tmp_path):
    src = tmp_path / "a.jpg"
    Image.new("RGB", (700, 990), "red").save(src)          # ISO ratio 0.707
    dest = tmp_path / "o.png"
    assert mockups.fit_art(src, (3039, 3031), dest) > 0.25   # square frame: about 29% cropped off
    assert Image.open(dest).size == (3039, 3031)
    assert mockups.fit_art(src, (1931, 2732), dest) < 0.01   # same shape as the frame: nothing cropped


def test_place_always_writes_a_jpg_under_the_limit_and_keeps_the_render(tmp_path, monkeypatch):
    png = tmp_path / "r.png"
    Image.new("RGB", (50, 50), "blue").save(png)
    out = mockups._place(png, tmp_path / "01_Main_Mockup.png")
    assert out.name == "01_Main_Mockup.jpg" and out.is_file()
    monkeypatch.setattr(mockups, "ETSY_MAX_MB", 0)         # too big at every quality: still a JPG, never a PNG
    assert mockups._place(png, tmp_path / "07_Detail.png").suffix == ".jpg"
    assert png.is_file()                                    # nothing is deleted


def test_build_refuses_missing_templates_and_prints(tmp_path):
    with pytest.raises(NotConfigured, match="templates folder"):
        mockups.build(tmp_path / "00001-X", {"mockup_templates": str(tmp_path / "nope")})
    tpl = tmp_path / "tpl"
    tpl.mkdir()
    with pytest.raises(NotConfigured, match="template files missing"):
        mockups.build(tmp_path / "00001-X", {"mockup_templates": str(tpl)})
    for _, n in mockups.GENERATED + mockups.FIXED:
        (tpl / n).write_bytes(b"x")
    with pytest.raises(NotConfigured, match="print JPG is missing"):
        mockups.build(tmp_path / "00001-X", {"mockup_templates": str(tpl)})
