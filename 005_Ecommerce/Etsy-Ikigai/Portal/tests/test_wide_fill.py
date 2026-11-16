"""Edit with chat, generative fill (wide crop, Nano Banana 2.1): geometry, composite, the chat -> confirm flow and
Open in PhotoCraft with OpenFill. No paid calls: SAM, kie.ai and PhotoCraft are faked."""
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from app import template_edit as te
from app import wide_fill as wf
from test_scene_templates import FakeCraft, scene


def _ratio_ok(p):
    x0, y0, x1, y1 = p["crop"]
    a, b = map(int, p["ratio"].split(":"))
    return abs((x1 - x0) / (y1 - y0) - a / b) < 0.01


def test_box_from_mask_picks_the_part_under_the_click_and_drops_specks():
    m = np.zeros((400, 600), np.float32)
    m[50:150, 40:200] = 1          # couch
    m[300:350, 400:550] = 1        # second couch
    m[10:12, 590:592] = 1          # speck
    assert wf.box_from_mask(m) == (40, 50, 550, 350)                      # both parts, speck dropped
    assert wf.box_from_mask(m, point=(450, 320)) == (400, 300, 550, 350)  # the one Tony clicked
    assert wf.box_from_mask(m, point=(250, 100)) == (40, 50, 200, 150)    # nearest part to the click
    assert wf.box_from_mask(np.zeros((40, 40))) is None
    assert wf.point_box((5, 5), 600, 400) == (0, 0, 35, 35)               # clamped at the picture corner


@pytest.mark.parametrize("box", [(0, 0, 120, 90), (1500, 1100, 1600, 1200), (700, 500, 900, 700), (10, 600, 1590, 1190)])
def test_crop_is_an_exact_model_ratio_inside_the_picture_and_holds_the_box(box):
    rgb = np.full((1200, 1600, 3), 128, np.uint8)
    p = wf.plan(rgb, box)
    x0, y0, x1, y1 = p["crop"]
    assert 0 <= x0 < x1 <= 1600 and 0 <= y0 < y1 <= 1200 and _ratio_ok(p)
    assert x0 <= box[0] and y0 <= box[1] and x1 >= min(box[2], 1600) and y1 >= min(box[3], 1200)
    assert max(x1 - x0, y1 - y0) >= min(1024, 1200)                        # wide: at least 1024 px long
    send = wf.crop_for_model(rgb, p)
    assert max(send.size) <= wf.SEND_SIDE


def test_small_picture_still_gets_a_ratio_crop():
    p = wf.plan(np.zeros((300, 500, 3), np.uint8), (200, 100, 260, 160))
    x0, y0, x1, y1 = p["crop"]
    assert 0 <= x0 and 0 <= y0 and x1 <= 500 and y1 <= 300 and _ratio_ok(p)


def test_instruction_has_tonys_line_location_and_the_fixed_suffix():
    p = wf.plan(np.full((900, 1200, 3), 100, np.uint8), (400, 500, 700, 700))
    t = wf.instruction("make the couch pink", p)
    assert t.startswith("In the area from") and "make the couch pink" in t and "cast shadow" in t
    assert t.endswith(wf.SUFFIX)
    r = wf.instruction("remove the lamp", p)
    assert r.startswith("remove the lamp.") and "Do not add anything new" in r and r.endswith(wf.SUFFIX)


def test_composite_leaves_every_pixel_outside_the_mask_identical():
    rng = np.random.default_rng(3)
    rgb = rng.integers(0, 255, (900, 1200, 3), dtype=np.uint8)
    box = (500, 400, 700, 600)
    p = wf.plan(rgb, box)
    x0, y0, x1, y1 = p["crop"]
    answer = Image.fromarray(np.full((y1 - y0, x1 - x0, 3), (240, 80, 160), np.uint8))   # the model repaints it all
    quad = [[100, 100], [300, 100], [300, 300], [100, 300]]
    out, alpha = wf.composite(rgb, answer, p, protect=quad)
    assert out.shape == rgb.shape and out.dtype == np.uint8
    outside = alpha == 0
    assert outside.sum() > 0 and np.array_equal(out[outside], rgb[outside])             # bit for bit
    assert np.array_equal(out[:y0], rgb[:y0]) and np.array_equal(out[:, :x0], rgb[:, :x0])  # outside the crop
    assert alpha[100:300, 100:300].max() == 0                                            # the art area is never touched
    core = out[box[1] + 20:box[3] - 20, box[0] + 20:box[2] - 20].reshape(-1, 3).mean(0)
    assert abs(core[0] - 240) < 3 and abs(core[1] - 80) < 3                              # inside: the model's pixels
    assert alpha[:y0].max(initial=0) == 0 and alpha[y1:].max(initial=0) == 0 and alpha[:, x1:].max(initial=0) == 0


def test_composite_keeps_unchanged_zone_pixels_original():
    rgb = np.full((900, 1200, 3), 150, np.uint8)
    p = wf.plan(rgb, (500, 400, 700, 600))
    x0, y0, x1, y1 = p["crop"]
    ans = rgb[y0:y1, x0:x1].copy()
    ans[400 - y0:600 - y0, 500 - x0:700 - x0] = (20, 200, 20)                          # change only the object
    out, alpha = wf.composite(rgb, Image.fromarray(ans), p)
    far = out[y0 + 5:y0 + 40, x0 + 5:x0 + 40]
    assert np.abs(far.astype(int) - 150).max() <= 1


# ---------- the Edit with chat flow ----------

@pytest.fixture
def session(tmp_path, monkeypatch):
    from app import scene_templates as stp
    from test_template_build_edit import tree
    S = {"room_templates_dir": str(tree(tmp_path)), "gallery_cache": str(tmp_path / "cache"),
         "template_checks_path": str(tmp_path / "checks.json")}
    monkeypatch.setattr(stp, "_run", FakeCraft())
    tdir = Path(S["room_templates_dir"]) / "Portrait_Templates/002_Ratio_2x3/001_Living_Rooms/Test_Room"
    tdir.mkdir()
    psd = tdir / "Test_Room.psd"
    psd.write_bytes(scene(tmp_path / "s.png").read_bytes())
    layers = [{"id": 4, "name": "Place Artwork Here", "kind": "Smart Object", "blend": "Normal", "opacity": 1,
               "visible": True, "bounds": [500, 170, 260, 400], "group": ""},
              {"id": 2, "name": "BASE (room photo)", "kind": "Pixel", "blend": "Normal", "opacity": 1, "visible": True,
               "bounds": [0, 0, 1200, 900], "group": ""}]
    craft = FakeCraft()
    monkeypatch.setattr(te, "layers_of", lambda p, s=None: (layers, [1200, 900]))
    monkeypatch.setattr(te, "_run", lambda s, a, timeout=300: craft(s, a))
    monkeypatch.setattr(te.tc, "so_size", lambda p, s=None, w=None: [260, 400])
    monkeypatch.setattr(te, "_render", lambda p, out, s, so=None, work=None: Path(out).write_bytes(b"jpg") and out)
    rel = "002_Ratio_2x3/001_Living_Rooms/Test_Room/Test_Room.psd"
    te.start(rel, S)
    yield S, rel, craft, psd
    te.discard(rel, S)


ASK = lambda p: '{"reply":"Sure.","ops":[{"op":"image_edit","prompt":"make the couch pink","target":"couch"}]}'  # noqa: E731


def couch_mask(png, word):
    assert word == "couch"
    m = np.zeros((900, 1200), np.float32)
    m[660:860, 300:900] = 1
    return m


def test_chat_finds_the_object_with_sam_and_shows_the_cost_first(session):
    S, rel, craft, _ = session
    st = te.chat(rel, "make the couch pink", None, S, ask=ASK, sam=couch_mask)
    assert st["pending"] == {"credits": 6, "box": [300, 660, 900, 860], "target": "couch", "text": "make the couch pink"}
    assert "about 6 credits" in st["log"][-1]["text"] and "found the couch" in st["log"][-1]["text"]
    assert not st["dirty"]                                                   # nothing paid, nothing changed


def test_nothing_found_asks_for_a_click_then_uses_the_click(session):
    S, rel, _, _ = session
    empty = lambda png, word: np.zeros((900, 1200))  # noqa: E731
    st = te.chat(rel, "make the couch pink", None, S, ask=ASK, sam=empty)
    assert st["pending"] is None and "Click on it" in st["log"][-1]["text"]
    st = te.chat(rel, "make the couch pink", [600, 760], S, ask=ASK, sam=empty)
    b = st["pending"]["box"]
    assert b[0] < 600 < b[2] and b[1] < 760 < b[3] and "marked" in st["log"][-1]["text"]


def test_sam_down_still_works_with_a_click(session):
    S, rel, _, _ = session

    def down(png, word):
        raise ConnectionRefusedError("ComfyUI is not running")
    st = te.chat(rel, "make the couch pink", None, S, ask=ASK, sam=down)
    assert st["pending"] is None and "SAM could not run" in st["log"][-1]["text"]


def test_confirm_sends_the_wide_crop_and_adds_a_new_base_layer(session):
    S, rel, craft, _ = session
    te.chat(rel, "make the couch pink", None, S, ask=ASK, sam=couch_mask)
    sent = {}

    def editor(crop, out, prompt, ratio):
        im = Image.open(crop).convert("RGB")
        sent.update(size=im.size, prompt=prompt, ratio=ratio)
        a = np.asarray(im).copy()
        a[:] = (230, 120, 170)
        Image.fromarray(a).save(out)
        return {"credits": 6.0}
    st = te.confirm_image_edit(rel, S, editor=editor)
    assert sent["prompt"].endswith(wf.SUFFIX) and "make the couch pink" in sent["prompt"]
    a, b = map(int, sent["ratio"].split(":"))
    assert abs(sent["size"][0] / sent["size"][1] - a / b) < 0.01
    assert st["dirty"] and st["pending"] is None and "Done (6.0 credits)" in st["log"][-1]["text"]
    cmd = " ".join(c for call in craft.calls for c in call if "placeEmbedded" in " ".join(call))   # the _apply run
    assert "file.placeEmbedded" in cmd and "OLD BASE (room photo) (retire)" in cmd and "layer.delete" not in cmd
    s = te._sessions[rel]
    full = next(Path(s["versions"][-1]["psd"]).parent.glob("Edit_*_base_edit_v*.png"))
    base = np.asarray(Image.open(next(full.parent.glob("Edit_*_base_v0.png"))).convert("RGB"))
    new = np.asarray(Image.open(full).convert("RGB"))
    assert np.array_equal(new[:300], base[:300])                             # far from the couch: original
    assert new[760, 600, 0] > 200 and new[760, 600, 1] < 150                 # the couch is pink


def test_a_failed_fill_keeps_the_confirmation_waiting(session):
    S, rel, _, _ = session
    te.chat(rel, "make the couch pink", None, S, ask=ASK, sam=couch_mask)

    def broken(*a):
        raise RuntimeError("kie.ai refused the job")
    st = te.confirm_image_edit(rel, S, editor=broken)
    assert st["pending"]["credits"] == 6 and "did not work" in st["log"][-1]["text"] and not st["dirty"]


def test_base_layer_skips_the_retired_old_base():
    layers = [{"id": 9, "name": "BASE (edited 20261115_2300)", "kind": "Pixel", "visible": True},
              {"id": 4, "name": "Place Artwork Here", "kind": "Smart Object", "visible": True},
              {"id": 2, "name": "OLD BASE (room photo) (retire)", "kind": "Pixel", "visible": False}]
    assert te.base_layer(layers)["id"] == 9


def test_guess_target():
    assert te.guess_target("make the couch pink") == "couch"
    assert te.guess_target("remove the coffee table") == "coffee table"
    assert te.guess_target("brighter please") == ""


def test_open_in_photocraft_uses_the_openfill_build(session, monkeypatch):
    S, rel, _, psd = session
    launched, bridged = [], []
    up = {"v": False}
    monkeypatch.setattr(te, "_port_open", lambda port: up["v"])

    def launcher(args):
        launched.append(args)
        up["v"] = True
    r = te.open_in_photocraft(rel, "SHADOWS", dict(S, openfill_launcher="/x/openfill-photocraft"), launcher,
                              lambda port, tok, calls, s=None: bridged.append((port, calls)) or
                              [{"result": {}} for _ in calls])
    assert launched == [["/x/openfill-photocraft", str(psd)]]                 # the OpenFill launcher, not ArtCraft
    assert bridged[0][0] == 7878 and bridged[0][1] == [("await_document", {"name": "Test_Room"}),
                                                       ("layer.select", {"name": "SHADOWS"})]
    assert r["with"] == "OpenFill" and r["app"] == "launched" and r["selected"]
