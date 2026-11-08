"""Templates tab: tree scan at any depth, gaps, 4:3 crop, style assignment (manual always wins over auto)."""
import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app import template_gallery as g
from app import template_styles as ts

ROW = ("| Template (path in Room_Templates) | Room type | Style | SO px | SO ratio | Visible ratio | Nearest standard | Bucket "
       "| Room / look | Status | Toggle / extra layers |\n|---|---|---|---|---|---|---|---|---|---|---|\n"
       "| `Portrait_Templates/02_Ratio_3x4/Living_Room/Plain/Plain.psd` | Living_Room | Boho | 300x400 | 0.75 | 0.75 | 3x4 "
       "| 3x4 | Sunny boho room | ready | none |\n")


@pytest.fixture
def lib(tmp_path):
    root = tmp_path / "Room_Templates"
    base = root / "Portrait_Templates"
    for d in ("01_Ratio_2x3/Living_Room/Japandi/Calm", "02_Ratio_3x4/Living_Room/Plain", "04_Ratio_5x7/Bedroom/Wabi",
              "001_Ratio_ISO/001_Living_Rooms/002_Modern", "002_Ratio_2x3/003_Bathroom", "Scripts"):
        (base / d).mkdir(parents=True)
    (base / "01_Ratio_2x3/Living_Room/Japandi/Calm/Calm_Template.psd").write_bytes(b"x")
    (base / "01_Ratio_2x3/Living_Room/Japandi/Calm/Archive").mkdir()
    (base / "01_Ratio_2x3/Living_Room/Japandi/Calm/Archive/Original_Calm_Template.psd").write_bytes(b"x")
    (base / "01_Ratio_2x3/Living_Room/Japandi/Calm/Archive/Old_v1.psd").write_bytes(b"x")
    (base / "02_Ratio_3x4/Living_Room/Plain/Plain.psd").write_bytes(b"x")
    (base / "02_Ratio_3x4/Living_Room/Plain/Plain_Preview.png").write_bytes(b"x")
    (root / "Directory.md").write_text(ROW)
    styles = tmp_path / "styles.json"
    styles.write_text(json.dumps({"vocabulary": [{"label": v, "section": "Art Prints - " + v} for v in
                                                 ("Botanical", "Japan Art", "Mid Century", "Minimalism")],
                                  "manual": {}, "auto": {}}))
    return {"settings": {"room_templates_dir": str(root), "gallery_cache": str(tmp_path / "cache")}, "styles": styles}


def test_scan_any_depth_styles_and_gaps(lib):
    t, gaps, covered = g.scan(lib["settings"])
    by = {x["folder"]: x for x in t}
    assert set(by) == {"Calm", "Plain"}                     # Archive/ (Original_ backups, old versions) is ignored
    assert g.archived_count(lib["settings"]) == 2
    assert by["Calm"]["style"] == "Japandi" and by["Calm"]["ratio"] == "2x3"   # style from the folder level
    assert by["Plain"]["style"] == "Boho" and by["Plain"]["desc"] == "Sunny boho room"  # Directory row
    assert by["Plain"]["so_px"] == "300x400"
    gap = {x["rel"]: x for x in gaps}
    assert gap["04_Ratio_5x7/Bedroom/Wabi"] == {"rel": "04_Ratio_5x7/Bedroom/Wabi", "ratio": "5x7", "room": "Bedroom",
                                                "style": "Wabi", "old_layout": False}
    assert gap["002_Ratio_2x3/003_Bathroom"]["room"] == "Bathroom" and gap["002_Ratio_2x3/003_Bathroom"]["old_layout"]
    assert "Scripts" not in str(gaps)
    assert [c["rel"] for c in covered] == []                               # 5x7 living-room Modern: nothing covers it
    assert "001_Ratio_ISO/001_Living_Rooms/002_Modern" in gap


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
    assert {i["folder"] for i in d["items"]} == {"Calm", "Plain"} and len(d["gaps"]) == 3
    assert d["vocabulary"] == ["Botanical", "Japan Art", "Mid Century", "Minimalism"]
    rel = next(i["rel"] for i in d["items"] if i["folder"] == "Calm")
    r = c.post("/ikigai/api/templates/styles", json={"rel": rel, "styles": ["Japan Art"]})
    assert r.json()["source"] == "manual"
    assert c.post("/ikigai/api/templates/styles", json={"rel": rel, "styles": ["Best Sellers"]}).status_code == 422
    assert c.post("/ikigai/api/templates/styles", json={"rel": "../x.psd", "styles": []}).status_code == 404
    assert c.post("/ikigai/api/templates/styles", json={"rel": rel, "action": "auto"}).json()["source"] == "none"
    assert c.get("/ikigai/api/templates/file/..%2Fsecret.jpg").status_code == 404
    assert c.get("/ikigai/api/templates/file/Gallery_0123456789abcdef_t.jpg").status_code == 404
