"""Refresh library (controls addendum A.7): new images are normalised, swept, renamed, cleaned (crop / LaMa with the
confidence check), blanked and tagged; a second click writes nothing; Tony's tags are kept; the paid Nano fill is
capped and never run by the refresh. SAM, LaMa, the vision calls, OCR and Gemini are injected stand-ins (free)."""
import hashlib
import json

import numpy as np
import pytest
from PIL import Image

from app import references as R
from test_references import fake_detector, room


class Vision:
    """claude -p stand-in: names, tags and registers."""

    def __init__(self):
        self.calls = []

    def __call__(self, prompt, images=None):
        self.calls.append(prompt)
        if "for a file name" in prompt:
            return json.dumps({str(k + 1): "Sunny Kitchen Thin Oak Frame Wide Shot" for k in range(len(images))})
        if "what kind of home" in prompt:
            ids = prompt.split("in this order: ")[1].split(")")[0].split(", ")
            return json.dumps({i: "ordinary_apartment" for i in ids})
        ids = prompt.split("in this order: ")[1].split(")")[0].split(", ")
        return json.dumps({i: {"display_group": "hung", "shot": "medium", "register": "small_rental"} for i in ids})


def no_overlays(png):
    return {"findings": [], "frame_box": [0.3, 0.18, 0.62, 0.75], "notes": []}


@pytest.fixture
def board(tmp_path):
    d = tmp_path / "Mock-Up_Inspiration"
    d.mkdir()
    (d / "Archive").mkdir()
    room(d / "0901_Test_Room_Dark_Frame.png")
    (d / "Archive" / "0905_Old.png").write_bytes(b"x")                       # an Archive id counts for the next id
    (d / "Rename_Log.md").write_text("# Mock-Up Inspiration - Rename Log\n\n| id | original_filename | new_filename |\n"
                                     "|---|---|---|\n| 0901 | a.png | 0901_Test_Room_Dark_Frame.png |\n")
    S = {"reference_dir": str(d)}
    R.prepare(S, detector=fake_detector((300, 120, 540, 440)), ocr=lambda png: [], log=lambda *_: None)
    return {"dir": d, "S": S}


def _jpg(path, size=(900, 600)):
    p = room(path.with_suffix(".png"), size=size)
    with Image.open(p) as im:
        im.convert("RGB").save(path, format="JPEG", quality=95)
    p.unlink()
    return path


def _run(board, scan=no_overlays, lama=None, vision=None):
    return R.refresh(board["S"], ask_vision=vision or Vision(), scan=scan, lama=lama,
                     detector=fake_detector((300, 120, 540, 440)), ocr=lambda png: [], tagger=None)


def test_new_jpg_is_renamed_logged_blanked_and_tagged_with_a_register(board):
    d = board["dir"]
    R.update(board["S"], lambda m: m["refs"]["0901"].update(tags={"display_group": "hung"}, tags_by="seed_2026-11-20"))
    _jpg(d / "IMG_2231.jpg")
    res = _run(board)
    new = [r for r in res["results"] if r.get("was") == "IMG_2231.jpg"]
    assert new and new[0]["id"] == "0906" and new[0]["file"] == "0906_Sunny_Kitchen_Thin_Oak_Frame_Wide_Shot.png"
    assert (d / "Archive" / "IMG_2231.jpg").is_file() and not (d / "IMG_2231.jpg").exists()     # original kept
    log = (d / "Rename_Log.md").read_text()
    assert "refresh" in log and "| 0906 | IMG_2231.jpg | 0906_Sunny_Kitchen_Thin_Oak_Frame_Wide_Shot.png |" in log
    e = R.load(d)["refs"]["0906"]
    assert e["renamed_from"] == "IMG_2231.jpg" and e["has_art"] is True and (d / e["blank"]).is_file()
    assert e["tags"]["register"] == "small_rental"
    assert R.load(d)["refs"]["0901"]["tags"]["register"] == "ordinary_apartment"      # old entry: register once


def test_a_tiny_image_is_archived_unchanged(board):
    d = board["dir"]
    p = d / "tiny.png"
    Image.new("RGB", (380, 300), (200, 190, 180)).save(p)
    h = hashlib.sha1(p.read_bytes()).hexdigest()
    res = _run(board)
    assert any(r.get("note") == "archived: too small (380 px)" for r in res["results"])
    assert hashlib.sha1((d / "Archive" / "tiny.png").read_bytes()).hexdigest() == h and not p.exists()


def test_a_corner_deal_bubble_is_cropped_and_the_original_backed_up(board):
    d = board["dir"]
    room(d / "0910_Corner_Bubble.png")
    (d / "Archive" / "0910_Corner_Bubble.png").write_bytes(b"older backup")      # name taken -> _Original

    def scan(png):
        return {"findings": [{"type": "deal", "box": [0.0, 0.0, 0.1, 0.05], "conf": 0.9}],
                "frame_box": [0.3, 0.18, 0.62, 0.75], "notes": []}
    _run(board, scan=scan)
    with Image.open(d / "0910_Corner_Bubble.png") as im:
        assert im.size == (900, 570)                                               # 5% off the top
    assert (d / "Archive" / "0910_Corner_Bubble_Original.png").is_file()
    assert (d / "Archive" / "0910_Corner_Bubble.png").read_bytes() == b"older backup"
    e = R.load(d)["refs"]["0910"]
    assert e["cleanup"]["method"] == "crop" and e["cleanup"]["confidence"] == "high"
    assert "| 0910 | deal |" in (d / "Cleanup_Log.md").read_text()


def _lama_stub(fill):
    def run(inp, mask, out):
        a = np.asarray(Image.open(inp).convert("RGB")).copy()
        m = np.asarray(Image.open(mask)) > 127
        a[m] = fill(a, m)
        Image.fromarray(a).save(out)
    return run


def test_a_mid_wall_watermark_is_lama_filled_outside_pixels_identical(board):
    d = board["dir"]
    p = room(d / "0911_Watermark.png")
    before = np.asarray(Image.open(p).convert("RGB")).copy()

    def scan(png):
        return {"findings": [{"type": "watermark", "box": [0.05, 0.4, 0.2, 0.5], "conf": 0.9}],
                "frame_box": [0.3, 0.18, 0.62, 0.75], "notes": []}
    rng = np.random.default_rng(3)
    _run(board, scan=scan, lama=_lama_stub(lambda a, m: np.clip(np.float32([236, 232, 224]) +
                                                                rng.normal(0, 0, (int(m.sum()), 3)), 0, 255)))
    after = np.asarray(Image.open(p).convert("RGB"))
    m = R._mask_from_box([0.05, 0.4, 0.2, 0.5], 900, 600)
    assert (after[~m] == before[~m]).all()
    e = R.load(d)["refs"]["0911"]
    assert e["cleanup"]["method"] == "lama"


def test_a_smeared_lama_is_low_confidence_and_never_silently_usable(board):
    d = board["dir"]
    room(d / "0912_Smear.png")

    def scan(png):
        return {"findings": [{"type": "watermark", "box": [0.02, 0.3, 0.25, 0.6], "conf": 0.9}],
                "frame_box": [0.3, 0.18, 0.62, 0.75], "notes": []}
    rng = np.random.default_rng(1)
    res = _run(board, scan=scan, lama=_lama_stub(lambda a, m: rng.integers(0, 255, (int(m.sum()), 3))))
    e = R.load(d)["refs"]["0912"]
    assert e["cleanup"]["confidence"] == "low" and e["usable"] is False and "clean-up needs your eye" in e["why"]
    assert (d / e["cleanup"]["check_image"]).is_file()
    assert next(r for r in res["results"] if r.get("id") == "0912")["status"] == "needs_eye"
    R.mark_ok(board["S"], "0912")
    e = R.load(d)["refs"]["0912"]
    assert e["cleanup"]["ok_by"] == "tony" and "clean-up needs your eye" not in e["why"]


def test_a_second_click_writes_nothing(board):
    d = board["dir"]
    _jpg(d / "IMG_1.jpg")
    _run(board)
    stamp = {p.name: (p.stat().st_mtime_ns, hashlib.sha1(p.read_bytes()).hexdigest()) for p in d.rglob("*") if p.is_file()}
    v = Vision()
    res = _run(board, vision=v)
    assert res.get("nothing_new") and v.calls == []
    assert stamp == {p.name: (p.stat().st_mtime_ns, hashlib.sha1(p.read_bytes()).hexdigest()) for p in d.rglob("*")
                     if p.is_file()}


def test_tonys_tags_are_never_overwritten(board):
    d = board["dir"]
    R.update(board["S"], lambda m: m["refs"]["0901"].update(tags={"display_group": "hung"}, tags_by="tony"))
    _jpg(d / "IMG_9.jpg")
    _run(board)
    assert R.load(d)["refs"]["0901"]["tags"] == {"display_group": "hung"}


def test_a_photo_without_framed_art_gets_has_art_false(board):
    d = board["dir"]
    Image.new("RGB", (900, 600), (236, 232, 224)).save(d / "0913_No_Art.png")

    def no_art(src, work, settings, canvas):
        raise RuntimeError("no frame")
    R.refresh(board["S"], ask_vision=Vision(), scan=lambda png: {"findings": [], "frame_box": None},
              detector=no_art, ocr=lambda png: [])
    e = R.load(d)["refs"]["0913"]
    assert e["has_art"] is False and e["blank_method"] == "none" and (d / e["blank"]).is_file() and e["usable"]


def test_nano_route_refuses_above_the_cap_and_refresh_never_calls_it(board, monkeypatch):
    monkeypatch.setattr(R, "nano_fill", lambda *a, **k: pytest.fail("refresh must never spend"))
    _jpg(board["dir"] / "IMG_5.jpg")
    _run(board)
    assert R.nano_plan(board["S"], ["0901"] * 5)["ok"] and not R.nano_plan(board["S"], ["0901"] * 6)["ok"]


def test_dry_run_reports_and_writes_nothing(board):
    d = board["dir"]
    _jpg(d / "IMG_7.jpg")
    before = sorted(p.name for p in d.rglob("*"))
    res = R.refresh(board["S"], dry_run=True)
    assert res["dry_run"] and res["results"][0]["file"] == "IMG_7.jpg"
    assert sorted(p.name for p in d.rglob("*")) == before


def test_archive_it_moves_source_and_blank(board):
    d = board["dir"]
    e = R.load(d)["refs"]["0901"]
    R.archive_ref(board["S"], "0901")
    assert not (d / e["source"]).exists() and (d / "Archive" / e["blank"]).is_file()
    assert R.load(d)["refs"]["0901"]["archived"] and not R.usable(board["S"])
