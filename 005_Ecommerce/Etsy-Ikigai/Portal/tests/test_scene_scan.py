"""Output scan (realism addendum 6, tests 8.1.3): thresholds, tiling maths, severity and Pillow stand-ins. The Vision
OCR and Gemini are injected; the real OCR on Tony's slot 17 runs only on macOS with the compiled tool."""
import os
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image, ImageDraw

from app import scene_scan as ss


def test_tiles_cover_the_picture_with_overlap():
    b = ss.tiles(2400, 1800)
    assert len(b) == 24
    assert b[0][:2] == (0, 0) and max(x[2] for x in b) == 2400 and max(x[3] for x in b) == 1800
    assert b[1][0] < b[0][2]                                               # neighbours overlap


def test_hits_map_back_and_duplicates_merge():
    boxes = [(0, 0, 100, 100), (80, 0, 180, 100)]
    raw = [{"tile": 0, "conf": 0.9, "box": [0.85, 0.5, 0.95, 0.6], "text": "ABCD"},
           {"tile": 1, "conf": 0.6, "box": [0.05, 0.5, 0.15, 0.6], "text": "ABCD"}]
    hits = ss.merge(ss.map_hits(raw, boxes, 200, 100))
    assert len(hits) == 1 and hits[0]["conf"] == 0.9 and abs(hits[0]["box"][0] - 0.425) < 1e-6


def test_keep_needs_confidence_letters_and_height():
    ok = {"conf": 0.5, "text": "ABC", "box": [0.4, 0.4, 0.5, 0.41]}
    assert ss.keep_ocr(ok)
    assert not ss.keep_ocr(dict(ok, conf=0.2)) and not ss.keep_ocr(dict(ok, text="A-1"))
    assert not ss.keep_ocr(dict(ok, box=[0.4, 0.4, 0.5, 0.402]))


@pytest.mark.parametrize("box,sev", [
    ([0.02, 0.02, 0.10, 0.05], "hard"),            # corner
    ([0.40, 0.92, 0.50, 0.95], "hard"),            # bottom edge band, 10% wide
    ([0.40, 0.92, 0.42, 0.95], "soft"),            # edge band but narrow
    ([0.48, 0.62, 0.56, 0.66], "soft")])           # book spines mid-picture
def test_ocr_severity(box, sev):
    f, s = ss.classify([{"conf": 0.8, "text": "TEXT", "box": box}])
    assert s == sev and f[0]["severity"] == sev


def test_gemini_severity_and_marker_leak():
    f, s = ss.classify(gem=[{"type": "extra_frame", "box": [0.1, 0.1, 0.2, 0.3], "conf": 0.8}])
    assert s == "hard" and "second frame" in f[0]["why"]
    assert ss.classify(gem=[{"type": "logo", "box": [0.1, 0.1, 0.2, 0.3], "conf": 0.4}])[1] == "none"
    assert ss.classify(gem=[{"type": "text", "box": [0.4, 0.4, 0.43, 0.45], "conf": 0.9}])[1] == "soft"
    assert ss.classify(leak=0.004)[1] == "soft" and ss.classify(leak=0.001)[1] == "none"


def _room(path, draw=None):
    im = Image.new("RGB", (1200, 900), (232, 228, 220))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 700, 1200, 900], fill=(140, 100, 70))
    d.rectangle([480, 180, 720, 520], fill=(60, 40, 30))
    d.rectangle([492, 192, 708, 508], fill=(250, 215, 170))
    if draw:
        draw(d)
    im.save(path)
    return path


def _ocr_from_drawn(texts):
    """A Vision stand-in that 'reads' the strings drawn at known picture boxes: reports them for every tile they
    fall in (in tile coordinates), like the real tool."""
    def run(paths):
        boxes = ss.tiles(1200, 900)
        out = []
        for k, (x0, y0, x1, y1) in enumerate(boxes):
            for txt, (a, b, c, d) in texts:
                if a >= x0 and c <= x1 and b >= y0 and d <= y1:
                    w, h = x1 - x0, y1 - y0
                    out.append({"tile": k, "conf": 0.9, "text": txt,
                                "box": [(a - x0) / w, (b - y0) / h, (c - x0) / w, (d - y0) / h]})
        return out
    return run


@pytest.mark.parametrize("case,sev", [("sale", "hard"), ("spine", "soft"), ("pill", "hard"), ("clean", "none")])
def test_stand_ins(tmp_path, case, sev):
    texts = {"sale": [("SALE 20%", (20, 20, 160, 50))], "spine": [("ABCD", (300, 560, 330, 600))],
             "pill": [("Visit site", (30, 820, 180, 860))], "clean": []}[case]

    def draw(d):
        for t, (a, b, c, e) in texts:
            if case == "pill":
                d.rounded_rectangle([a - 8, b - 6, c + 8, e + 6], radius=18, fill=(255, 255, 255))
            d.text((a, b), t, fill=(0, 0, 0))
    png = _room(tmp_path / "s.png", draw)
    gem = (lambda png, prompt: '{"findings": [{"type": "ui_button", "box_2d": [900, 20, 960, 160], '
           '"confidence": 0.9}]}') if case == "pill" else (lambda png, prompt: '{"findings": []}')
    r = ss.scan(png, {}, art_quad=[[492, 192], [708, 192], [708, 508], [492, 508]], ocr_runner=_ocr_from_drawn(texts),
                gemini_ask=gem, overlay=str(tmp_path / "ov.png"))
    assert r["severity"] == sev, r["findings"]
    assert r["pass"] == (sev == "none")
    if sev != "none":
        assert Path(r["overlay"]).is_file() and ss.summary(r)


def test_marker_leak_counts_orange_outside_the_art(tmp_path):
    png = _room(tmp_path / "s.png", lambda d: d.rectangle([40, 40, 140, 140], fill=(250, 215, 170)))
    rgb = np.asarray(Image.open(png).convert("RGB"))
    leak = ss.marker_leak(rgb, [[492, 192], [708, 192], [708, 508], [492, 508]], "orange")
    assert abs(leak - 101 * 101 / (1200 * 900)) < 0.002


def test_scan_off_and_gemini_failure_are_not_fatal(tmp_path):
    png = _room(tmp_path / "s.png")
    assert ss.scan(png, {"scene_scan": "off"})["severity"] == "none"

    def boom(png, prompt):
        raise RuntimeError("no key")
    r = ss.scan(png, {}, ocr_runner=lambda paths: [], gemini_ask=boom)
    assert r["severity"] == "none" and "gemini scan skipped" in r["notes"][0]


SLOT17 = (Path(__file__).resolve().parents[2] / "Designs" / "00121-Book Club Cat" / "03-Etsy Images" /
          "17_Room_Bedroom_Mid_Century.jpg")


@pytest.mark.skipif(sys.platform != "darwin" or not SLOT17.is_file() or not os.environ.get("IKIGAI_VISION_TESTS"),
                    reason="real Vision OCR on Tony's slot 17: set IKIGAI_VISION_TESTS=1 (macOS)")
def test_real_vision_finds_the_garbled_spines_on_slot_17():
    hits = ss.ocr_findings(SLOT17, {})
    assert hits and ss.classify(hits)[1] == "soft"
