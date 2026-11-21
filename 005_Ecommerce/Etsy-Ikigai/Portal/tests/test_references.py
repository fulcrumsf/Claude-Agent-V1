"""Reference prep (realism addendum 1, tests 8.1.2): blanking the artwork of a reference photo with the insert marker,
the manifest, idempotency, Tony's hand-blanked entries, the usability checks and recolour / mirror on demand. SAM, Gemini
and the OCR are injected stand-ins; the real-SAM checks at the bottom run only with the SAM venv (local, free)."""
import json
import os
from pathlib import Path

import numpy as np
import pytest
from PIL import Image, ImageDraw

from app import references as R, slot_planner as sp

WALL = (236, 232, 224)
FRAME = (70, 48, 30)


def room(path, art_box=(300, 120, 540, 440), frame=12, text=True, second=False, size=(900, 600)):
    """A synthetic reference: plain wall, a dark wood frame, a patterned artwork with lettering, a floor."""
    im = Image.new("RGB", size, WALL)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 500, size[0], size[1]], fill=(150, 110, 80))
    x0, y0, x1, y1 = art_box
    d.rectangle([x0 - frame, y0 - frame, x1 + frame - 1, y1 + frame - 1], fill=FRAME)
    for i in range(x0, x1, 20):                                      # a busy pattern = "art"
        d.rectangle([i, y0, min(i + 10, x1 - 1), y1 - 1], fill=(200, 40 + (i % 120), 60))
        d.rectangle([i + 10, y0, min(i + 19, x1 - 1), y1 - 1], fill=(30, 90, 170))
    if text:
        d.text((x0 + 20, y0 + 20), "ART EXPLORE", fill=(255, 255, 255))
    if second:
        d.rectangle([40, 120, 160, 300], fill=FRAME)
    im.save(path)
    return path


def fake_detector(art_box, info=None, method="sam_quad"):
    calls = []

    def det(src, work, settings, canvas):
        calls.append({"src": Path(src).name, "canvas": canvas})
        x0, y0, x1, y1 = art_box
        q = [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
        return {"blank_method": method, "corners": q, "corners_paper": q, "opening": {"mode": "test"},
                "reference": info or {"frames": 1, "mirrors": 0, "screens": 0, "shape": "portrait", "upright": True}}
    det.calls = calls
    return det


@pytest.fixture
def board(tmp_path):
    d = tmp_path / "Mock-Up_Inspiration"
    d.mkdir()
    (d / "Archive").mkdir()
    room(d / "0901_Test_Room_Dark_Frame.png")
    room(d / "Archive" / "0902_Old_Low_Res.png")                    # never a source
    return {"dir": d, "S": {"reference_dir": str(d)}}


def test_sources_skip_archive_and_blank_files(board):
    d = board["dir"]
    (d / "0901_Test_Room_Dark_Frame_Blank.png").write_bytes(b"x")
    (d / "notes.png").write_bytes(b"x")
    assert [p.name for p in R.sources(d)] == ["0901_Test_Room_Dark_Frame.png"]


def test_prepare_blanks_the_art_writes_the_manifest_and_removes_the_text(board):
    d, S = board["dir"], board["S"]
    det = fake_detector((300, 120, 540, 440))
    rep = R.prepare(S, detector=det, ocr=lambda png: [], log=lambda *_: None)
    assert rep["prepared"] == ["0901"] and not rep["unusable"]
    man = json.loads((d / R.MANIFEST).read_text())
    e = man["refs"]["0901"]
    assert e["usable"] and e["blank"] == "0901_Test_Room_Dark_Frame_Blank.png" and e["blank_method"] == "sam_quad"
    assert e["marker"] == "orange" and e["camera_side"] == "front" and abs(e["aspect"] - 0.75) < 0.02
    assert e["leftover_ring"] < R.RING_MAX and e["frame_eaten_sides"] == 0 and e["room_text"] == []
    blank = np.asarray(Image.open(d / e["blank"]).convert("RGB")).astype(int)
    core = blank[130:430, 310:530]                                   # the art (and its lettering) is one flat marker
    assert (np.abs(core - np.array(sp.MARKER_RGB["orange"])).max()) <= 1
    assert tuple(blank[110, 420]) == FRAME and tuple(blank[50, 50]) == WALL      # frame + wall untouched
    src = np.asarray(Image.open(d / e["source"]).convert("RGB")).astype(int)
    assert (src[130:430, 310:530] != core).any()                    # the source itself is never changed


def test_second_run_rewrites_nothing_and_a_changed_source_is_prepared_again(board):
    d, S = board["dir"], board["S"]
    R.prepare(S, detector=fake_detector((300, 120, 540, 440)), ocr=lambda png: [], log=lambda *_: None)
    blank = d / "0901_Test_Room_Dark_Frame_Blank.png"
    t0, m0 = blank.stat().st_mtime_ns, (d / R.MANIFEST).stat().st_mtime_ns
    det = fake_detector((300, 120, 540, 440))
    rep = R.prepare(S, detector=det, ocr=lambda png: [], log=lambda *_: None)
    assert rep["skipped"] == ["0901"] and det.calls == []
    assert blank.stat().st_mtime_ns == t0 and (d / R.MANIFEST).stat().st_mtime_ns == m0
    room(d / "0901_Test_Room_Dark_Frame.png", art_box=(310, 120, 550, 440))     # Tony replaced the screenshot
    rep = R.prepare(S, detector=fake_detector((310, 120, 550, 440)), ocr=lambda png: [], log=lambda *_: None)
    assert rep["prepared"] == ["0901"]


def test_tony_entries_and_tony_tags_are_never_touched(board):
    d, S = board["dir"], board["S"]
    R.prepare(S, detector=fake_detector((300, 120, 540, 440)), ocr=lambda png: [], log=lambda *_: None)
    man = json.loads((d / R.MANIFEST).read_text())
    man["refs"]["0901"].update(blank_method="tony", note="blanked by hand")
    (d / R.MANIFEST).write_text(json.dumps(man))
    det = fake_detector((300, 120, 540, 440))
    R.prepare(S, force=True, detector=det, ocr=lambda png: [], log=lambda *_: None)
    assert det.calls == [] and json.loads((d / R.MANIFEST).read_text())["refs"]["0901"]["note"] == "blanked by hand"
    man["refs"]["0901"].update(blank_method="sam_quad", tags={"display_group": "floor"}, tags_by="tony")
    (d / R.MANIFEST).write_text(json.dumps(man))
    R.prepare(S, force=True, detector=fake_detector((300, 120, 540, 440)), ocr=lambda png: [], log=lambda *_: None)
    e = json.loads((d / R.MANIFEST).read_text())["refs"]["0901"]
    assert e["tags"] == {"display_group": "floor"} and e["tags_by"] == "tony"


@pytest.mark.parametrize("case,why", [
    ("square", "not a portrait artwork"), ("two_frames", "2 framed pictures"), ("mirror", "a mirror"),
    ("flat", "lies flat"), ("text", "readable text"), ("sliver", "art sliver")])
def test_unusable_references_say_why(board, case, why):
    d, S = board["dir"], board["S"]
    box = (300, 120, 540, 440)
    info = {"frames": 1, "mirrors": 0, "screens": 0, "shape": "portrait", "upright": True}
    ocr = lambda png: []                                              # noqa: E731
    if case == "square":
        room(d / "0901_Test_Room_Dark_Frame.png", art_box=(300, 120, 620, 440))
        box = (300, 120, 620, 440)
    elif case == "two_frames":
        info["frames"] = 2
    elif case == "mirror":
        info["mirrors"] = 1
    elif case == "flat":
        info["upright"] = False
    elif case == "text":
        ocr = lambda png: [{"conf": 0.9, "text": "STONE DESIGN", "box": [0.1, 0.8, 0.2, 0.85]}]   # noqa: E731
    elif case == "sliver":
        box = (310, 130, 530, 430)                                    # the fill stops 10 px inside the art
    rep = R.prepare(S, detector=fake_detector(box, info), ocr=ocr, log=lambda *_: None)
    e = json.loads((d / R.MANIFEST).read_text())["refs"]["0901"]
    assert not e["usable"] and any(why in w for w in e["why"]), e["why"]
    assert "0901" in rep["unusable"] and R.usable(S) == []


def test_frame_eaten_is_unusable(board):
    d, S = board["dir"], board["S"]
    R.prepare(S, detector=fake_detector((288, 108, 552, 452)), ocr=lambda png: [], log=lambda *_: None)
    e = json.loads((d / R.MANIFEST).read_text())["refs"]["0901"]
    assert not e["usable"] and any("took the frame" in w for w in e["why"])


def test_blank_for_recolours_and_mirrors_into_the_temp_dir_only(board, tmp_path):
    d, S = board["dir"], board["S"]
    R.prepare(S, detector=fake_detector((300, 120, 540, 440)), ocr=lambda png: [], log=lambda *_: None)
    e = R.usable(S)[0]
    assert R.blank_for(e, "orange", False, None, S) == d / e["blank"]           # same marker, no flip: the file itself
    out = tmp_path / "run"
    out.mkdir()
    before = sorted(p.name for p in d.iterdir())
    p = R.blank_for(e, "blue", True, out, S)
    assert p.parent == out and sorted(x.name for x in d.iterdir()) == before
    a = np.asarray(Image.open(p).convert("RGB")).astype(int)
    W = a.shape[1]
    assert (np.abs(a[280, W - 1 - 420] - np.array(sp.MARKER_RGB["blue"])).max()) <= 1     # mirrored blue fill
    assert tuple(a[50, W - 1 - 50]) == WALL


def test_contact_sheet_is_labelled_and_capped(board, tmp_path):
    S = board["S"]
    R.prepare(S, detector=fake_detector((300, 120, 540, 440)), ocr=lambda png: [], log=lambda *_: None)
    p = R.contact_sheet(R.usable(S), tmp_path / "sheet.png", settings=S)
    with Image.open(p) as im:
        assert max(im.size) <= 1568


def test_grades_and_uses_are_recorded_per_reference(board):
    S = board["S"]
    R.prepare(S, detector=fake_detector((300, 120, 540, 440)), ocr=lambda png: [], log=lambda *_: None)
    R.record_use(S, "0901", {"idea_id": 3, "listing": "Book Club Cat", "slot": 16, "template": "a/b.psd"})
    R.record_grade(S, "0901", {"idea_id": 3, "slot": 16, "grade": "B+", "at": "x"})
    R.record_grade(S, "0901", {"idea_id": 3, "slot": 16, "grade": "A-", "at": "y"})    # replaces, never doubles
    e = R.usable(S)[0]
    assert len(e["uses"]) == 1 and [g["grade"] for g in e["grades"]] == ["A-"] and R.mean_grade(e) == round(3.7 / 4.3, 3)
    R.mark_refused(S, "0901")
    assert R.usable(S) == []                                         # refused by kie.ai: never picked again


# ---------- real SAM (local venv, free): only when the venv is installed ----------

SAM_PY = Path(os.path.expanduser("~/.cache/ikigai-sam/bin/python"))
BOARD = Path(__file__).resolve().parents[2] / "Creative_Inspiration" / "Mock-Up_Inspiration"
needs_sam = pytest.mark.skipif(not (SAM_PY.is_file() and (BOARD / R.MANIFEST).is_file()
                                    and os.environ.get("IKIGAI_SAM_TESTS")),
                               reason="real SAM run: set IKIGAI_SAM_TESTS=1 (needs the SAM venv + Tony's board)")


@needs_sam
@pytest.mark.parametrize("rid,canvas", [("0024", False), ("0035", False), ("0036", True)])
def test_real_sam_finds_the_artwork(tmp_path, rid, canvas):
    e = json.loads((BOARD / R.MANIFEST).read_text())["refs"][rid]
    q = np.float32(e["quad"])
    box = [float(q[:, 0].min()) - 4, float(q[:, 1].min()) - 4, float(q[:, 0].max()) + 4, float(q[:, 1].max()) + 4]
    res = R.sam_reference(BOARD / e["source"], tmp_path, {}, canvas=canvas, box=box)
    got = np.float32(res["corners"])
    assert np.abs(got - q).max() < 12, (got.tolist(), q.tolist())
