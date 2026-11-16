"""Templates tab actions: Build this on a gap tile, proposed room folders, Edit with chat, Open in PhotoCraft.
kie.ai and PhotoCraft are faked (no credits, no app window)."""
import json
from pathlib import Path

import numpy as np
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app import scene_templates as stp, template_build as tb, template_edit as te, template_gallery as tg
from test_scene_templates import FakeCraft, fake_generator, scene


def tree(tmp_path):
    root = tmp_path / "Room_Templates"
    lib = root / "Portrait_Templates"
    for d in ("002_Ratio_2x3/002_Bedroom/001_Japandi", "002_Ratio_2x3/001_Living_Rooms", "003_Ratio_3x4/003_Bathroom"):
        (lib / d).mkdir(parents=True)
    return root


@pytest.fixture
def S(tmp_path, monkeypatch):
    monkeypatch.setattr(stp, "_run", FakeCraft())
    return {"room_templates_dir": str(tree(tmp_path)), "gallery_cache": str(tmp_path / "cache"),
            "template_checks_path": str(tmp_path / "checks.json"), "room_scene_engine": "nbpro"}


def test_gap_plan_and_build_into_the_gap_folder_then_deny_to_archive(S, tmp_path):
    gaps = {g["rel"]: g for g in tg.scan(S)[1]}
    plan = tb.gap_plan(gaps["002_Ratio_2x3/002_Bedroom/001_Japandi"], S)
    assert (plan["room"], plan["decor"], plan["ratio"], plan["credits"]) == ("Bedroom", "Japandi", "2x3", 18)
    assert plan["path"] == "Room_Templates/Portrait_Templates/002_Ratio_2x3/002_Bedroom/001_Japandi/"
    calls = []
    tb.start(plan["rel"], S)
    with pytest.raises(tb.BuildError, match="one at a time"):
        tb.start("003_Ratio_3x4/003_Bathroom", S)
    tb.run(plan["rel"], S, fake_generator(calls), check=False)
    assert not tb.job()["running"] and not tb.job()["error"], tb.job()
    folder = Path(S["room_templates_dir"]) / "Portrait_Templates" / plan["rel"]
    before = sorted(p.name for p in folder.iterdir())
    assert len(before) == 3 and not [p for p in folder.iterdir() if p.is_dir()]        # no new folder
    man = json.loads((folder / "template.json").read_text())
    assert man["approved"] is False and man["credits"] == 18 and calls[0]["prompt"].startswith("Photorealistic japandi bedroom")
    t = next(x for x in tg.scan(S)[0] if x["rel"] == tb.job()["made"])
    assert t["room"] == "Bedroom" and plan["rel"] not in {g["rel"] for g in tg.scan(S)[1]}
    tb.decide(t["rel"], "denied", S)
    assert sorted(p.name for p in (folder / "Archive").iterdir()) and not list(folder.glob("*.psd"))
    assert plan["rel"] in {g["rel"] for g in tg.scan(S)[1]}                             # a gap again


def test_room_folders_are_only_proposed_until_tony_approves_the_exact_path(S):
    props = tb.proposals(S)
    assert {p["rel"] for p in props} == {"002_Ratio_2x3/009_Entryway", "002_Ratio_2x3/010_Laundry",
                                         "003_Ratio_3x4/009_Entryway", "003_Ratio_3x4/010_Laundry"}
    lib = Path(S["room_templates_dir"]) / "Portrait_Templates"
    assert not (lib / "002_Ratio_2x3/009_Entryway").exists()                            # nothing created by looking
    with pytest.raises(tb.BuildError):
        tb.approve_folder("002_Ratio_2x3/011_Hallway", S)                               # not a proposal
    assert tb.approve_folder("002_Ratio_2x3/009_Entryway", S)["created"].endswith("009_Entryway/")
    assert (lib / "002_Ratio_2x3/009_Entryway").is_dir()
    assert "002_Ratio_2x3/009_Entryway" in {g["rel"] for g in tg.scan(S)[1]}            # now a gap to build


def test_quick_parse_validate_and_never_delete():
    layers = [{"id": 9, "name": "Glass Sheen", "kind": "Pixel", "blend": "Screen", "opacity": 0.12, "visible": True,
               "bounds": [0, 0, 10, 10], "group": "GLARE"},
              {"id": 7, "name": "Light Shadow", "kind": "Pixel", "blend": "Multiply", "opacity": 0.17, "visible": True,
               "bounds": [0, 0, 10, 10], "group": "SHADOWS"},
              {"id": 4, "name": "Place Artwork Here", "kind": "Smart Object", "blend": "Normal", "opacity": 1,
               "visible": True, "bounds": [10, 10, 50, 70], "group": ""},
              {"id": 2, "name": "BASE (room photo)", "kind": "Pixel", "blend": "Normal", "opacity": 1, "visible": True,
               "bounds": [0, 0, 200, 150], "group": ""}]
    assert te.quick_parse("hide glass sheen", layers)[1] == [{"op": "set", "layer": 9, "visible": False}]
    assert te.quick_parse("Light Shadow opacity 12%", layers)[1] == [{"op": "set", "layer": 7, "opacity": 0.12}]
    assert te.quick_parse("remove this 30px", layers, [50, 60])[1] == [{"op": "heal", "points": [[50, 60]], "size": 30}]
    with pytest.raises(te.EditError, match="never deleted"):
        te.validate([{"op": "delete", "layer": 7}], layers, (200, 150))
    with pytest.raises(te.EditError, match="unknown layer"):
        te.validate([{"op": "set", "layer": 99, "visible": False}], layers, (200, 150))
    cmds = " ".join(te.commands(te.validate([{"op": "retire", "layer": 7}, {"op": "heal", "points": [[5, 5]]}],
                                            layers, (200, 150)), layers))
    assert "OLD Light Shadow (retire)" in cmds and "paint.spotHealing" in cmds and "layer.delete" not in cmds


def test_edit_session_save_archives_the_old_psd_and_discard_changes_nothing(S, tmp_path, monkeypatch):
    lib = Path(S["room_templates_dir"]) / "Portrait_Templates"
    tdir = lib / "002_Ratio_2x3/001_Living_Rooms/Test_Room"
    tdir.mkdir()
    psd = tdir / "Test_Room.psd"
    psd.write_bytes(scene(tmp_path / "s.png").read_bytes())   # the fake PhotoCraft treats a PSD as its base PNG
    layers = [{"id": 4, "name": "Place Artwork Here", "kind": "Smart Object", "blend": "Normal", "opacity": 1,
               "visible": True, "bounds": [500, 170, 260, 400], "group": ""},
              {"id": 2, "name": "BASE (room photo)", "kind": "Pixel", "blend": "Normal", "opacity": 1, "visible": True,
               "bounds": [0, 0, 1200, 900], "group": ""}]
    monkeypatch.setattr(te, "layers_of", lambda p, s=None: (layers, [1200, 900]))
    monkeypatch.setattr(te, "_run", lambda s, a, timeout=300: FakeCraft()(s, a))
    monkeypatch.setattr(te.tc, "so_size", lambda p, s=None, w=None: [260, 400])
    monkeypatch.setattr(te, "_render", lambda p, out, s, so=None, work=None: Path(out).write_bytes(b"jpg") and out)
    rel = "002_Ratio_2x3/001_Living_Rooms/Test_Room/Test_Room.psd"
    st = te.start(rel, S)
    assert st["open"] and not st["dirty"] and "Place Artwork Here" in [l["name"] for l in st["layers"]]
    st = te.chat(rel, "hide BASE (room photo)", None, S)
    assert st["dirty"] and st["log"][-1]["who"] == "studio"
    st = te.chat(rel, "make the wall green", None, S, ask=lambda p: '{"reply":"Repaint.","ops":[{"op":"image_edit",'
                                                                   '"prompt":"paint the wall sage green","target":"wall"}]}',
                 sam=lambda png, word: np.pad(np.ones((200, 300)), ((100, 600), (200, 700))))
    assert st["pending"]["credits"] == 6 and "Confirm" in st["log"][-1]["text"]           # cost shown, nothing run
    assert st["pending"]["box"] == [200, 100, 500, 300] and st["pending"]["target"] == "wall"
    original = psd.read_bytes()
    te.discard(rel, S)
    assert psd.read_bytes() == original and not (tdir / "Archive").exists()
    te.start(rel, S)
    te.chat(rel, "hide BASE (room photo)", None, S)
    out = te.save(rel, S, recheck=False)
    assert (tdir / "Archive" / out["archived"]).is_file() and psd.is_file()            # old version kept


def test_open_in_photocraft_launches_with_control_port_and_selects_the_layer(S, tmp_path, monkeypatch):
    lib = Path(S["room_templates_dir"]) / "Portrait_Templates"
    tdir = lib / "002_Ratio_2x3/001_Living_Rooms/Test_Room"
    tdir.mkdir()
    (tdir / "Test_Room.psd").write_bytes(b"x")
    launched, bridged = [], []
    up = {"v": False}

    def launcher(args):
        launched.append(args)
        up["v"] = True
        Path(args[args.index("--control-token-file") + 1]).parent.mkdir(parents=True, exist_ok=True)
        Path(args[args.index("--control-token-file") + 1]).write_text("t")
    monkeypatch.setattr(te, "_port_open", lambda port: up["v"])
    r = te.open_in_photocraft("002_Ratio_2x3/001_Living_Rooms/Test_Room/Test_Room.psd", "SHADOWS",
                              dict(S, photocraft_app="/x/photocraft", photocraft_open_with="artcraft"), launcher,
                              lambda port, tok, calls, s=None: bridged.append(calls) or [{"result": {}}])
    a = launched[0]
    assert a[1:3] == ["--control", "47811"] and "--control-token-file" in a and a[-1].endswith("Test_Room.psd")
    assert bridged[0] == [("command_run", {"command": "layer.select", "params": {"name": "SHADOWS"}})]
    assert r["selected"] and r["app"] == "launched"


def test_templates_api_shows_checks_gaps_with_build_cost_and_proposals(S, tmp_path):
    (tmp_path / "checks.json").write_text(json.dumps({"results": {}}))
    import shutil
    shutil.copy(Path(__file__).resolve().parents[1] / "config" / "template_styles.json", tmp_path / "styles.json")
    app = FastAPI()
    tg.mount(app, S, auto=False, spawn=lambda fn, *a: None, styles_path=tmp_path / "styles.json")
    c = TestClient(app)
    j = c.get("/ikigai/api/templates").json()
    g = next(x for x in j["gaps"] if x["rel"] == "002_Ratio_2x3/002_Bedroom/001_Japandi")
    assert g["build"]["credits"] == 18 and g["build"]["path"].endswith("001_Japandi/")
    assert {p["room"] for p in j["proposals"]} == {"Entryway", "Laundry"} and "check_job" in j
    assert c.post("/ikigai/api/templates/folders", json={"rel": "002_Ratio_2x3/099_Nope"}).status_code == 422
    assert c.post("/ikigai/api/templates/build", json={"rel": "not/a/gap"}).status_code == 422
