"""Templates tab: tree scan at any depth, gaps, 4:3 crop, style assignment (manual always wins over auto)."""
import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app import template_gallery as g
from app import template_styles as ts

ROW = ("| Template (path in Room_Templates) | Room type | Style | SO px | SO ratio | Visible ratio | Nearest standard | Bucket "
       "| Room / look | Status | Toggle / extra layers |\n|---|---|---|---|---|---|---|---|---|---|---|\n"
       "| `Portrait_Templates/003_Ratio_3x4/002_Bedroom/Plain/Plain.psd` | Bedroom | Wabi_Sabi | 300x400 | 0.75 | 0.75 | 3x4 "
       "| 3x4 | Sunny wabi room | ready | none |\n")


@pytest.fixture
def lib(tmp_path):
    root = tmp_path / "Room_Templates"
    base = root / "Portrait_Templates"
    for d in ("002_Ratio_2x3/001_Living_Rooms/001_Japandi_Minimalist/Calm", "002_Ratio_2x3/001_Living_Rooms/002_Modern",
              "003_Ratio_3x4/002_Bedroom/Plain", "001_Ratio_ISO/002_Bedroom/002_Scandinavian", "001_Ratio_ISO/008_Kids_Nursery",
              "005_Ratio_11x14/003_Bathroom", "01_Ratio_2x3/Living_Room", "Scripts"):
        (base / d).mkdir(parents=True)
    calm = base / "002_Ratio_2x3/001_Living_Rooms/001_Japandi_Minimalist/Calm"
    (calm / "Calm_Template.psd").write_bytes(b"x")
    (calm / "Archive").mkdir()
    (calm / "Archive/Original_Calm_Template.psd").write_bytes(b"x")
    (calm / "Archive/Old_v1.psd").write_bytes(b"x")
    (base / "003_Ratio_3x4/002_Bedroom/Plain/Plain.psd").write_bytes(b"x")
    (base / "003_Ratio_3x4/002_Bedroom/Plain/Plain_Preview.png").write_bytes(b"x")
    (root / "Directory.md").write_text(ROW)
    styles = tmp_path / "styles.json"
    styles.write_text(json.dumps({"vocabulary": [{"label": v, "section": "Art Prints - " + v} for v in
                                                 ("Botanical", "Japan Art", "Mid Century", "Minimalism")],
                                  "manual": {}, "auto": {}}))
    return {"settings": {"room_templates_dir": str(root), "gallery_cache": str(tmp_path / "cache")}, "styles": styles}


def test_numbered_folder_names():
    assert g.label("001_Living_Rooms") == "Living Rooms" and g.label("001_Japandi_Minimalist") == "Japandi Minimalist"
    assert g.label("006_GameRooms_Mancave") == "GameRooms Mancave" and g.number("004_Kitchen_Bar") == 4
    assert g.ratio_of("001_Ratio_ISO") == "iso" and g.ratio_of("005_Ratio_11x14") == "11x14"
    assert g.ratio_of("002_Ratio_2x3") == "2x3" and g.ratio_of("Scripts") is None


def test_scan_any_depth_styles_and_gaps(lib):
    t, gaps, stray = g.scan(lib["settings"])
    by = {x["folder"]: x for x in t}
    assert set(by) == {"Calm", "Plain"}                     # Archive/ (Original_ backups, old versions) is ignored
    assert g.archived_count(lib["settings"]) == 2
    assert by["Calm"]["style"] == "Japandi Minimalist" and by["Calm"]["ratio"] == "2x3"   # style from the folder level
    assert by["Calm"]["room"] == "Living Rooms" and by["Calm"]["room_n"] == 1
    assert by["Plain"]["style"] == "Wabi Sabi" and by["Plain"]["desc"] == "Sunny wabi room"  # template at room level
    assert by["Plain"]["so_px"] == "300x400" and by["Plain"]["room"] == "Bedroom"
    gap = {x["rel"]: x for x in gaps}
    assert set(gap) == {"002_Ratio_2x3/001_Living_Rooms/002_Modern", "001_Ratio_ISO/002_Bedroom/002_Scandinavian",
                        "001_Ratio_ISO/008_Kids_Nursery", "005_Ratio_11x14/003_Bathroom"}   # Tony's empty folders, real depth
    assert gap["001_Ratio_ISO/002_Bedroom/002_Scandinavian"] == {
        "rel": "001_Ratio_ISO/002_Bedroom/002_Scandinavian", "ratio": "iso", "room": "Bedroom", "room_n": 2,
        "style": "Scandinavian"}
    assert gap["005_Ratio_11x14/003_Bathroom"]["style"] == "Unstyled" and gap["005_Ratio_11x14/003_Bathroom"]["ratio"] == "11x14"
    assert "Scripts" not in str(gaps)
    assert [s["rel"] for s in stray] == ["01_Ratio_2x3", "01_Ratio_2x3/Living_Room"]   # outside NNN_: never a gap


def test_crop_is_4x3_centred_on_art_and_clamped():
    assert g.crop_box(2048, 2048, (800, 300, 700, 1030)) == (0, 47, 2048, 1583)
    l, t, r, b = g.crop_box(4000, 2000, (3600, 500, 300, 600))
    assert (r - l, b - t) == (2667, 2000) and r == 4000                    # clamped at the right edge
    l, t, r, b = g.crop_box(1000, 1500, None)
    assert (r - l) * 3 == (b - t) * 4


def test_manual_always_wins_over_auto(lib):
    p, rel = lib["styles"], "x.psd"
    ts.classify_missing([(rel, "thumb.jpg", "k1")], classify=lambda img, vocab: (["Japan Art", "Nope"], 7), path=p)
    assert ts.resolve(ts.load(p), rel) == {"styles": ["Japan Art"], "source": "auto", "auto": ["Japan Art"]}
    calls = []
    ts.classify_missing([(rel, "thumb.jpg", "k1")], classify=lambda *a: calls.append(1), path=p)
    assert calls == []                                                      # classified once per thumbnail key
    r = ts.set_manual(rel, ["Minimalism", "Botanical"], p)
    assert r["source"] == "manual" and r["styles"] == ["Botanical", "Minimalism"]   # vocabulary order
    ts.classify_missing([(rel, "thumb.jpg", "k2")], classify=lambda *a: calls.append(1), path=p)
    assert calls == []                                                      # never re-guessed once Tony chose
    assert ts.set_manual(rel, [], p) == {"styles": [], "source": "manual", "auto": ["Japan Art"]}   # "no style" on purpose
    assert ts.clear_manual(rel, p)["source"] == "auto"
    assert ts.confirm_auto(rel, p) == {"styles": ["Japan Art"], "source": "manual", "auto": ["Japan Art"]}
    with pytest.raises(ValueError):
        ts.set_manual(rel, ["Best Sellers"], p)
    data = ts.load(p)
    assert data["manual"][rel] == ["Japan Art"] and data["auto"][rel]["key"] == "k1"   # kept apart in one file


def test_failed_guess_is_skipped_and_retried(lib):
    def boom(*a):
        raise RuntimeError("down")
    assert ts.classify_missing([("y.psd", "t.jpg", "k")], classify=boom, path=lib["styles"])["failed"] == 1
    assert "y.psd" not in ts.load(lib["styles"])["auto"]


def test_api_assign_confirm_and_refusals(lib):
    app = FastAPI()
    g.mount(app, lib["settings"], styles_path=lib["styles"], auto=False)
    c = TestClient(app)
    d = c.get("/ikigai/api/templates").json()
    assert {i["folder"] for i in d["items"]} == {"Calm", "Plain"} and len(d["gaps"]) == 4
    assert len(d["stray_empty"]) == 2 and d["buckets"]["iso"] == "ISO / 5x7"
    assert d["vocabulary"] == ["Botanical", "Japan Art", "Mid Century", "Minimalism"]
    rel = next(i["rel"] for i in d["items"] if i["folder"] == "Calm")
    r = c.post("/ikigai/api/templates/styles", json={"rel": rel, "styles": ["Japan Art"]})
    assert r.json()["source"] == "manual"
    assert c.post("/ikigai/api/templates/styles", json={"rel": rel, "styles": ["Best Sellers"]}).status_code == 422
    assert c.post("/ikigai/api/templates/styles", json={"rel": "../x.psd", "styles": []}).status_code == 404
    assert c.post("/ikigai/api/templates/styles", json={"rel": rel, "action": "auto"}).json()["source"] == "none"
    assert c.get("/ikigai/api/templates/file/..%2Fsecret.jpg").status_code == 404
    assert c.get("/ikigai/api/templates/file/Gallery_0123456789abcdef_t.jpg").status_code == 404
