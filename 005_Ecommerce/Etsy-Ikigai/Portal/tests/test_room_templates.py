"""Room-template mockups (app/room_templates.py): paint swap, white frame fix, light/frame/paint planning, guard,
and the Production tab hiding room files the step did not make."""
import json

import numpy as np
from PIL import Image

from app import room_templates as rt, walls
from test_prints import approved_idea, env  # noqa: F401  (fixture reuse)


def _rgba(rgb, a=1.0, size=(8, 8)):
    x = np.zeros((*size, 4), "float32")
    x[..., :3] = np.array(rgb, "float32") / 255
    x[..., 3] = a
    return x


def test_paint_swap_same_paint_is_identity_and_darker_paint_is_darker(tmp_path):
    ref = _rgba((150, 140, 120))
    same = np.array(Image.open(rt.paint_layer(ref, (200, 192, 176), (200, 192, 176), tmp_path / "a.png")))
    assert np.abs(same[..., :3].astype(int) - np.array([150, 140, 120])).max() <= 3
    dark = np.array(Image.open(rt.paint_layer(ref, (200, 192, 176), (74, 76, 76), tmp_path / "b.png")))
    assert dark[..., :3].mean() < same[..., :3].mean() - 40
    assert (dark[..., 3] == 255).all()                       # alpha (wall mask) is kept


def test_paint_swap_never_burns_a_lit_wall_to_white(tmp_path):
    ref = _rgba((250, 248, 244))                             # sunlit, near-clipped reference wall
    out = np.array(Image.open(rt.paint_layer(ref, (200, 192, 176), (240, 233, 220), tmp_path / "c.png")))
    luma = out[..., :3].astype(float) @ np.array([0.299, 0.587, 0.114])
    assert luma.max() < 245                                  # highlight shoulder keeps the paint's tone


def test_paint_swap_limits_cool_cast_on_warm_paint(tmp_path):
    ref = _rgba((120, 125, 145))                             # bluish shade on the golden-hour plate
    out = np.array(Image.open(rt.paint_layer(ref, (200, 192, 176), (196, 184, 168), tmp_path / "d.png")))
    r, g, b = out[0, 0, :3].astype(int)
    assert r >= b                                            # warm putty stays warm, not mauve/blue


def test_white_frame_in_shade_reads_neutral_not_taupe(tmp_path):
    taupe = _rgba((120, 105, 85))
    out = np.array(Image.open(rt.white_frame_layer(taupe, tmp_path / "w.png")))[0, 0, :3].astype(int)
    assert out.mean() > 115 and (out.max() - out.min()) < (120 - 85)


def test_rank_lights_and_room_frames():
    room = {"frames": {"oak": "Oak", "walnut": "Walnut"},
            "lights": [{"id": "gold", "rank": 1, "suits": ["food_drink"]}, {"id": "win", "rank": 2, "suits": ["cute_light"]}]}
    assert [l["id"] for l in rt.rank_lights(room, "cute_light")] == ["win", "gold"]
    assert [l["id"] for l in rt.rank_lights(room, "neon_night")] == ["gold", "win"]
    fs = rt.room_frames(room, [{"id": "gold_ornate"}, {"id": "walnut", "mat": True}, {"id": "oak"}])
    assert [(f["id"], f["layer"]) for f in fs] == [("walnut", "Walnut"), ("oak", "Oak")]


def test_walls_prefer_quiet_mid_neutral_behind_light_art():
    names = [p["name"] for p in walls.choose({"value_key": "light", "accents": [{"rgb": [203, 45, 18]}]}, "warm_wood", n=3)]
    assert names[0] in ("Warm Sand", "Greige") and "Charcoal" not in names and "Blue Grey" not in names


def _fake_room(tmp_path, monkeypatch):
    room = tmp_path / "Room_Templates" / "01_Test_Room"
    room.mkdir(parents=True)
    meta = {"art_aspect": 0.667, "smart_object_px": [200, 300], "paints": ["Greige"],
            "quad_nomat": [[10, 10], [110, 10], [110, 160], [10, 160]], "quad_mat": [[20, 20], [100, 20], [100, 150], [20, 150]]}
    for lid in ("a", "b"):
        (room / f"t_{lid}.json").write_text(json.dumps(meta))
        (room / f"R_{lid}.psd").write_bytes(b"x")
    (room / "room.json").write_text(json.dumps({
        "name": "Test Room", "furniture": "warm_wood", "value_keys": ["light"], "frames": {"oak": "Oak", "walnut": "Walnut"},
        "lights": [{"id": "a", "label": "Light_A", "kind": "a", "psd": "R_a.psd", "json": "t_a.json", "rank": 1, "suits": []},
                   {"id": "b", "label": "Light_B", "kind": "b", "psd": "R_b.psd", "json": "t_b.json", "rank": 2,
                    "suits": ["cute_light"]},
                   {"id": "gone", "label": "X", "kind": "x", "psd": "missing.psd", "json": "t_a.json", "rank": 0}]}))
    art = tmp_path / "Cat_2x3_24x36.jpg"
    Image.new("RGB", (200, 300), (230, 225, 215)).save(art)
    return {"room_templates_dir": str(tmp_path / "Room_Templates")}, art


def test_plan_is_deterministic_and_skips_missing_psds(tmp_path, monkeypatch):
    settings, art = _fake_room(tmp_path, monkeypatch)
    rooms_found = rt.rooms(settings)
    assert [l["id"] for l in rooms_found[0]["lights"]] == ["a", "b"]
    looks = rt.plan([art], {"title": "Book Club Cat", "description": "a cat asleep on a book, mid-century gouache"}, settings)
    assert [lk["light"]["id"] for lk in looks] == ["b", "a"]            # cute_light suits light b first
    assert len({(lk["frame_id"], lk["paint"]["name"]) for lk in looks}) == len(looks)
    again = rt.plan([art], {"title": "Book Club Cat", "description": "a cat asleep on a book, mid-century gouache"}, settings)
    assert [(l["frame_id"], l["paint"]["name"]) for l in again] == [(l["frame_id"], l["paint"]["name"]) for l in looks]
    assert rt.file_name(8, looks[0]) == "08_Room_Test_Room_Light_B.jpg"


def test_build_rooms_skips_flagged_looks_and_writes_jpgs(tmp_path, monkeypatch):
    settings, art = _fake_room(tmp_path, monkeypatch)
    out = tmp_path / "out"
    out.mkdir()

    def fake_render(room, light, art_, look, png, settings=None, work=None):
        Image.new("RGB", (64, 64), (200, 190, 180)).save(png)
        return {"png": png, "fitted": png}
    monkeypatch.setattr(rt, "render_look", fake_render)
    monkeypatch.setattr(rt, "guard", lambda room, light, *a, **k: {"pass": light["id"] == "b", "why": ["shadow covers 70%"]})
    made, notes, failed = rt.build_rooms(out, [art], settings, {"title": "Book Club Cat"})
    assert [m["file"] for m in made] == ["08_Room_Test_Room_Light_B.jpg"]
    assert failed == [9] and "flagged for Tony" in notes[0]
    assert (out / "08_Room_Test_Room_Light_B.jpg").is_file() and not list(out.glob("*.png"))


def test_production_hides_old_room_files_once_room_step_made_rooms(env):
    from app import prints
    from test_production import _make
    c, iid = env["c"], approved_idea(env["con"])
    folder = _make(env, iid)                                  # 08_Living_Room.jpg + 09_Bedroom.jpg (old v1 rooms)
    assert [i["file"] for i in c.get("/ikigai/api/production").json()["items"][0]["images"]] == \
        ["08_Living_Room.jpg", "09_Bedroom.jpg"]              # no room-step record yet: everything shows
    Image.new("RGB", (40, 40)).save(folder / "08_Room_Teak_Sideboard_Window_Light.jpg")
    con = env["con"]
    lst = prints.listing_for(con, iid)
    rec = prints._record(con, lst["id"])
    rec["mockups"] = {"files": [{"file": "08_Room_Teak_Sideboard_Window_Light.jpg", "slot": 8, "room": "Teak Sideboard",
                                 "light": "window_soft", "frame": "walnut", "mat": False, "paint": "Warm Sand"}]}
    prints._save_record(con, lst["id"], rec)
    imgs = c.get("/ikigai/api/production").json()["items"][0]["images"]
    assert [i["file"] for i in imgs] == ["08_Room_Teak_Sideboard_Window_Light.jpg"]
    assert imgs[0]["look"]["paint"] == "Warm Sand"
    assert (folder / "08_Living_Room.jpg").is_file()          # hidden, never deleted
