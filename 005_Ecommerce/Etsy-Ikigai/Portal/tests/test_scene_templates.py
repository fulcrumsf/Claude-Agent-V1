"""Room scenes -> templates (app/scene_templates.py) and the Production tab cards (app/production.py).
PhotoCraft and kie.ai are faked: a synthetic room with a perspective frame and a blank white insert stands in for the
model's scene, and the fake photocraft-cli copies images instead of rendering. No network, no credits."""
import json
import shutil
from pathlib import Path

import cv2
import numpy as np
import pytest
from PIL import Image

from app import prints, production, scene_templates as stp
from test_prints import approved_idea, env, fake_upscayl  # noqa: F401  (fixture reuse)

QUAD = [[520, 170], [760, 190], [756, 566], [524, 574]]      # the insert (true 2:3), slight 3/4 perspective


def scene(path, quad=QUAD, size=(1200, 900)):
    """A beige plastered wall, a dark wood frame, a blank white insert with a soft shadow, a sofa below."""
    W, H = size
    rng = np.random.default_rng(1)
    a = np.full((H, W, 3), (196, 182, 160), "float32") + rng.normal(0, 3, (H, W, 1))
    a[int(H * 0.72):] = (120, 104, 88)                                   # sofa
    q = np.float32(quad)
    c = q.mean(0)
    outer = c + (q - c) * 1.13
    cv2.fillPoly(a, [np.int32(outer)], (70, 48, 30))                     # frame moulding
    cv2.fillPoly(a, [np.int32(q)], (238, 236, 231))                      # blank paper
    ys, xs = np.mgrid[0:H, 0:W]
    shade = np.clip((xs - 640) / 400, 0, 1)[..., None] * 18              # soft key light falloff to the right
    m = np.zeros((H, W), "uint8")
    cv2.fillPoly(m, [np.int32(q)], 1)
    a = np.where(m[..., None] > 0, a - shade, a)
    Image.fromarray(np.clip(a, 0, 255).astype("uint8")).save(path)
    return path


def test_find_insert_gets_the_corners_and_true_shape(tmp_path):
    p = scene(tmp_path / "s.png")
    q, info = stp.find_insert(np.asarray(Image.open(p).convert("RGB")), 2 / 3)
    assert q is not None, info
    assert np.abs(np.float32(q) - np.float32(QUAD)).max() <= 3
    assert 0.55 < info["aspect"] < 0.75


def test_no_insert_is_reported_not_guessed(tmp_path):
    Image.new("RGB", (800, 600), (150, 140, 130)).save(tmp_path / "plain.png")
    q, why = stp.find_insert(np.asarray(Image.open(tmp_path / "plain.png")), 2 / 3)
    assert q is None and "insert" in why


def test_off_ratio_scene_is_rejected_and_art_is_cover_fit_never_padded(tmp_path):
    """Tony 2026-11-10: cover-fit + centre crop, never stretched, never a white border; >35% off = rejected (was 3%; Tony 2026-11-16: ratio barely matters, only absurd mismatches)."""
    sq = [[0, 0], [100, 0], [100, 100], [0, 100]]
    with pytest.raises(stp.TemplateError, match="off the print ratio"):
        stp.art_quad(sq, 1.0, 2 / 3)                                    # square insert for a 2x3 print (+50%): regenerate
    assert stp.art_quad(sq, 0.68, 2 / 3)[1] == "full"                   # 2% off: art cover-fits the insert
    assert stp.art_quad(sq, 0.73, 2 / 3)[1] == "full"                   # 9.5% off: still believable, art cover-fits and crops
    assert stp.art_quad(sq, 0.55, 2 / 3)[1] == "full"                   # 17% off: fine too
    src = tmp_path / "a.jpg"
    Image.new("RGB", (700, 990), "red").save(src)                       # ISO art (0.707)
    with pytest.raises(stp.TemplateError, match="limit 35%"):
        stp.fit_cover(src, (300, 800), tmp_path / "f.png")               # 3:8 slot: 47% would be cut off
    crop = stp.fit_cover(src, (712, 1000), tmp_path / "g.png")          # 0.712 slot: under 1% cut, edge to edge
    im = np.asarray(Image.open(tmp_path / "g.png"))
    red = lambda px: np.abs(px.astype(int) - [255, 0, 0]).max() < 6
    assert 0 < crop < 0.01 and im.shape[:2] == (1000, 712)
    assert red(im[0, 0]) and red(im[-1, -1]) and red(im[0, 356]) and red(im[500, 0])   # no white border anywhere


def library(tmp_path):
    """A tiny Room_Templates tree in Tony's NNN_ layout."""
    root = tmp_path / "Room_Templates"
    lib = root / "Portrait_Templates"
    for d in ("002_Ratio_2x3/001_Living_Rooms/001_Japandi_Minimalist", "002_Ratio_2x3/002_Bedroom",
              "003_Ratio_3x4/001_Living_Rooms/002_Modern", "003_Ratio_3x4/002_Bedroom", "004_Ratio_4x5/001_Living_Rooms",
              "001_Ratio_ISO/001_Living_Rooms", "005_Ratio_11x14/001_Living_Rooms"):
        (lib / d).mkdir(parents=True)
    return root


def test_folders_room_and_style_rules(tmp_path):
    root = library(tmp_path)
    S = {"room_templates_dir": str(root)}
    rd = stp.room_dir(S, "2x3", "Living room")
    assert rd.name == "001_Living_Rooms" and stp.room_dir(S, "2x3", "Office") is None   # never invented
    assert stp.available_rooms(S)["Bedroom"] == ["2x3", "3x4"]
    assert stp.style_dir(rd, "Japandi").name == "001_Japandi_Minimalist"              # Tony's folder reused
    assert stp.style_dir(rd, "Mid_Century") is None                                      # not created by a lookup
    made = stp.style_dir(rd, "Mid_Century", create=True)
    assert made.name == "002_Mid_Century" and made.is_dir()                              # next free number


class FakeCraft:
    """Stands in for photocraft-cli: a PSD is the base PNG's bytes, a render copies the PSD's base."""

    def __init__(self):
        self.calls = []

    def __call__(self, settings, args):
        self.calls.append(args)
        out = Path(args[args.index("--out") + 1])
        shutil.copyfile(args[1], out)
        return "{}"


def fake_generator(calls):
    def gen(engine, out, prompt, aspect, res):
        calls.append({"engine": engine, "prompt": prompt, "aspect": aspect, "res": res})
        scene(Path(out))
        return {"out": out, "model": "nano-banana-pro", "credits": 18.0, "left": 739.0}
    return gen


def test_build_psd_layers_are_named_and_hand_editable(tmp_path, monkeypatch):
    craft = FakeCraft()
    monkeypatch.setattr(stp, "_run", craft)
    (tmp_path / "w").mkdir()
    b = stp.build_psd(scene(tmp_path / "s.png"), "2x3", tmp_path / "w")
    a = " ".join(craft.calls[0])
    for name in ("BASE (room photo)", "Place Artwork Here", "Light Shadow", "Frame Edge Shadow", "Frame Hard Shadow",
                 "SHADOWS", "GLARE", "Glass Sheen", "edit.transform", '"smartObject": true'):
        assert name in a
    # Tony's shadow rule: every shadow layer is a BLACK fill (alpha = shape), limited to the art opening. This scene's
    # paper is flat up to the frame: no soft shadow is measured, so none is invented (L_edge may be empty).
    for f in ("L_hard.png", "L_edge.png", "L_light.png"):
        im = np.asarray(Image.open(tmp_path / "w" / f))
        assert im[..., :3].max() == 0 and (im[..., 3].max() > 0 or f == "L_edge.png")
        assert im[:150, :, 3].max() == 0 and im[:, :480, 3].max() == 0          # nothing outside the frame insert
    # the art runs 0.5 px under the frame's inner edge (Tony 2026-11-12, 0.5 since his own fix 2026-11-15), the
    # opening is kept separately
    from app import sam_frames as sf
    pads = sf.side_offsets(b["quad_insert"], b["quad_art"])
    assert pads == pytest.approx([0.5] * 4, abs=0.02) and b["opening_pad_px"] == 0.5
    assert b["so_ratio"] == pytest.approx(2 / 3, abs=0.01) and b["psd_tmp"].is_file()


@pytest.fixture
def prod(env, tmp_path, monkeypatch):
    root = library(tmp_path)
    env["S"].update({"room_templates_dir": str(root), "room_scene_engine": "nbpro", "room_slots": [3] + list(range(9, 20))})
    monkeypatch.setattr(stp, "_run", FakeCraft())
    calls = []
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from app import studio
    app = FastAPI()
    studio.mount(app, env["con"], env["S"], None, ask=lambda p, s=None: "", spawn=lambda fn, *a: fn(*a),
                 upscayl=fake_upscayl([]),
                 scene_generator=fake_generator(calls),
                 art_classify=lambda path, vocab: (["Animals", "Trendy"], 900))
    c = TestClient(app)
    iid = approved_idea(env["con"])
    c.post(f"/ikigai/api/prints/{iid}/run", json={})
    return {**env, "c": c, "iid": iid, "root": root, "gen": calls}


def test_only_upscaled_designs_are_listed(prod):
    c = prod["c"]
    other = approved_idea(prod["con"], title="Not upscaled yet: fire goat")
    ids = [d["idea_id"] for d in c.get("/ikigai/api/production").json()["items"]]
    assert ids == [prod["iid"]] and other not in ids


def test_panel_plans_slots_and_blank_styles_come_from_the_art(prod):
    c, iid = prod["c"], prod["iid"]
    p = c.get(f"/ikigai/api/production/{iid}/panel").json()
    assert p["styles"] == [] and p["styles_auto"] == ["Animals", "Trendy"] and p["styles_source"] == "auto"
    assert p["rooms_all"][0] == "Bathroom" and len(p["rooms_all"]) == 11 and p["max_rooms"] == 5
    assert p["slots"] and p["slots"][0]["slot"] == 3
    assert {s["room"] for s in p["slots"]} <= {"Living room", "Bedroom", "Dorm"}  # only rooms with folders (dorm = bedroom)
    assert p["slots"][0]["next"]["kind"] == "new" and p["slots"][0]["next"]["credits"] == 18
    assert prod["gen"] == []                                                      # nothing generated by looking


def test_ticks_are_saved_as_tags_and_validated(prod):
    c, iid = prod["c"], prod["iid"]
    p = c.post(f"/ikigai/api/production/{iid}/tags", json={"rooms": ["Office", "Living room"],
                                                           "styles": ["Trendy", "Animals"]}).json()
    assert [(s["slot"], s["room"], s["by"]) for s in p["slots"][:2]] == [(3, "Office", "tony"), (9, "Living room", "tony")]
    assert p["slots"][0]["next"]["kind"] == "none" and "Office folder" in p["slots"][0]["next"]["label"]
    rec = prints._record(prod["con"], prints.listing_for(prod["con"], iid)["id"])
    assert rec["design_tags"]["rooms"] == ["Office", "Living room"]
    assert rec["design_tags"]["styles"] == ["Trendy", "Animals"]               # shop order
    assert c.post(f"/ikigai/api/production/{iid}/tags", json={"rooms": ["Hallway"]}).status_code == 422
    six = ["Bathroom", "Bedroom", "Dorm", "Entryway", "Office", "Kids"]
    assert c.post(f"/ikigai/api/production/{iid}/tags", json={"rooms": six}).status_code == 422


def test_generate_new_scene_saves_template_places_jpg_and_never_overwrites(prod):
    c, iid, root = prod["c"], prod["iid"], prod["root"]
    c.post(f"/ikigai/api/production/{iid}/tags", json={"rooms": ["Living room"], "styles": ["Mid Century"]})
    p = c.post(f"/ikigai/api/production/{iid}/slots/3/generate", json={}).json()
    card = p["slots"][0]
    assert card["state"] == "idle" and card["image"], card["message"]
    assert card["image"]["file"].startswith("03_Room_Living_Room_") and card["source"] == "new"
    assert "onion-skin orange" in prod["gen"][0]["prompt"] and prod["gen"][0]["aspect"] == "4:3"
    folder = prod["tmp"] / "Designs" / "00121-Book Club Cat" / "03-Etsy Images"
    assert (folder / card["image"]["file"]).is_file()
    # auto-saved template: Tony's ratio + room folders, a style folder made only now, manifest beside the PSD
    tdir = (stp.library(prod["S"]) / card["template"]).parent
    assert tdir.parent.parent.name == "001_Living_Rooms" and stp.MASTER.match(tdir.parent.name)
    man = json.loads((tdir / "template.json").read_text())
    assert man["kind"] == "ai_scene" and man["made_for"]["slot"] == 3 and man["so_px"] and man["quad_art"]
    assert any(tdir.glob("*_Template.psd")) and any(tdir.glob("*_Scene.png"))
    # Regenerate: the new scene is a new file beside it; the old one goes to Archive (never overwritten)
    first = card["image"]["file"]
    p = c.post(f"/ikigai/api/production/{iid}/slots/3/generate", json={}).json()
    second = p["slots"][0]["image"]["file"]
    assert p["slots"][0]["state"] == "idle", p["slots"][0]["message"]
    assert second != first and (folder / second).is_file() and not (folder / first).exists()
    assert (folder / "Archive" / first).is_file()


def test_deny_moves_image_and_its_new_template_to_archive_and_undo_restores(prod):
    c, iid = prod["c"], prod["iid"]
    c.post(f"/ikigai/api/production/{iid}/tags", json={"rooms": ["Living room"]})
    card = c.post(f"/ikigai/api/production/{iid}/slots/3/generate", json={}).json()["slots"][0]
    name, tdir = card["image"]["file"], (stp.library(prod["S"]) / card["template"]).parent
    folder = prod["tmp"] / "Designs" / "00121-Book Club Cat" / "03-Etsy Images"
    c.post(f"/ikigai/api/production/{iid}/images/{name}", json={"decision": "denied"})
    assert not (folder / name).exists() and (folder / "Archive" / name).is_file()
    assert not tdir.exists() and (tdir.parent / "Archive" / tdir.name).is_dir()
    assert c.get(f"/ikigai/api/production/{iid}/file/{name}").status_code == 200   # still viewable on the card
    c.post(f"/ikigai/api/production/{iid}/images/{name}", json={"decision": "pending"})
    assert (folder / name).is_file() and tdir.is_dir()
    c.post(f"/ikigai/api/production/{iid}/images/{name}", json={"decision": "approved"})
    p = c.get(f"/ikigai/api/production/{iid}/panel").json()
    assert p["slots"][0]["image"]["status"] == "approved" and p["slots"][0]["locked"]


def test_one_job_at_a_time(prod):
    c, iid = prod["c"], prod["iid"]
    production.start_slot(prod["con"], prod["S"], iid, 9)                 # a job is running
    try:
        r = c.post(f"/ikigai/api/production/{iid}/slots/3/generate", json={})
        assert r.status_code == 422 and "one at a time" in r.json()["detail"]
    finally:
        production._job.update(running=False, idea_id=None, slot=None, stage="")
    for fixed in (4, 8, 20):                                                 # fixed images, never a room card
        assert c.post(f"/ikigai/api/production/{iid}/slots/{fixed}/generate", json={}).status_code == 422


def test_plus_picker_renders_a_library_template_for_free(prod):
    c, iid, root = prod["c"], prod["iid"], prod["root"]
    tdir = root / "Portrait_Templates/002_Ratio_2x3/002_Bedroom/BDRM_Test"
    tdir.mkdir()
    scene(tdir / "BDRM_Test.png").rename(tdir / "BDRM_Test.psd")          # fake PSD (the fake craft copies it)
    (tdir / "template.json").write_text(json.dumps({"psd": "BDRM_Test.psd", "so_px": [240, 360],
                                                    "quad_art": QUAD, "kind": "tony_psd"}))
    rel = "002_Ratio_2x3/002_Bedroom/BDRM_Test/BDRM_Test.psd"
    assert c.post(f"/ikigai/api/production/{iid}/slots/10/generate", json={"template": "nope.psd"}).status_code == 422
    p = c.post(f"/ikigai/api/production/{iid}/slots/10/generate", json={"template": rel}).json()
    card = next(s for s in p["slots"] if s["slot"] == 10)
    assert card["image"] and card["template"] == rel and card["source"] == "picked" and prod["gen"] == []


def test_a_failed_scene_is_shown_on_the_card_and_releases_the_job(prod, monkeypatch):
    c, iid = prod["c"], prod["iid"]

    def broke(engine, out, prompt, aspect, res):
        Image.new("RGB", (800, 600), (150, 140, 130)).save(out)          # no frame drawn
        return {"credits": 18.0}
    monkeypatch.setattr(stp, "kie_module", lambda s=None: type("K", (), {"generate": staticmethod(broke)}))
    production.run_slot(prod["con"], prod["S"], iid, 3)
    p = c.get(f"/ikigai/api/production/{iid}/panel").json()
    card = p["slots"][0]
    assert card["state"] == "failed" and "no clean blank frame insert" in card["message"]
    assert not p["job"]["running"]
    kept = list((prod["tmp"] / "Designs" / "00121-Book Club Cat" / "03-Etsy Images" / "Archive").glob("Scene_No_Insert_03_*"))
    assert kept                                                            # the paid-for scene is kept, not lost


def test_upscale_and_resize_also_make_the_listing_images_when_switched_on(env):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from app import studio
    made = []

    def fake_build(folder, settings, design=None):
        made.append(folder.name)
        return {"files": [{"file": "01_Main_Mockup.jpg", "slot": 1}, {"file": "03_Instant_Download.png", "slot": 3}],
                "pending": "rooms in Production", "notes": []}
    S = {**env["S"], "prints_make_listing_images": True}
    app = FastAPI()
    studio.mount(app, env["con"], S, None, ask=lambda p, s=None: "", spawn=lambda fn, *a: fn(*a),
                 upscayl=fake_upscayl([]), mockup_build=fake_build)
    c = TestClient(app)
    iid = approved_idea(env["con"])
    st = c.post(f"/ikigai/api/prints/{iid}/run", json={}).json()
    assert st["done"] and st["steps"]["mockups"]["status"] == "done" and st["listing_images"] and made == ["00121-Book Club Cat"]
    st = c.post(f"/ikigai/api/prints/{iid}/run", json={"redo": True}).json()
    assert st["steps"]["mockups"]["status"] == "done" and len(made) == 2  # re-run remakes 1, 2, 7 too


def test_two_cards_never_preview_the_same_library_template():
    lib = [{"rel": f"002_Ratio_2x3/001_Living_Rooms/002_Modern/T{i}/T{i}.psd", "name": f"T{i}", "ratio": "2x3",
            "room": "Living Rooms", "style": "Modern", "desc": "", "wired": False, "manifest": None} for i in (1, 2)]
    plan = [{"slot": 8, "room": "Living room", "decor": "Modern", "ratio": "2x3"},
            {"slot": 9, "room": "Living room", "decor": "Modern", "ratio": "2x3"},
            {"slot": 10, "room": "Living room", "decor": "Modern", "ratio": "2x3"}]
    picks = production.library_picks(plan, {}, lib)
    assert [p and p["name"] for p in (picks[8], picks[9], picks[10])] == ["T1", "T2", None]   # third: new scene
    picks = production.library_picks(plan, {"8": {"template": lib[0]["rel"], "tried": [lib[0]["rel"]]}}, lib)
    assert picks[8]["name"] == "T2" and picks[9] is None      # regenerate moves on; T1 stays with slot 8


# ---------- Tony 2026-11-12: opening = the frame's hard inner edge, art pad, hard + soft shadow layers ----------

from app.scene_templates import card_verify as real_card_verify      # bound before conftest replaces it


def wall_scene(path=None, size=(900, 800)):
    """The measured LVRM_Midcentury case in miniature: the frame's dark inner wall left of the opening and a warm,
    near-flat shadow strip on the paper that blurs out (test_sam_frames.render_wall_frame)."""
    from test_sam_frames import Q, render_wall_frame
    rgb = render_wall_frame(Q, size)
    if path:
        Image.fromarray(rgb).save(path)
    return rgb, Q


def test_edge_shadows_are_measured_hard_on_the_wall_soft_on_the_paper():
    from app import sam_frames as sf
    rgb, q = wall_scene()
    img = rgb.astype("float32") / 255
    sides = {s["side"]: s for s in stp.measure_edge_shadows(img, q, 1.5)}
    L = sides["left"]
    # the art's pad on the left lies on the dark inner wall: its tone vs the paper (100,72,48 vs 236,234,228)
    wall = 1 - float(np.float32([100, 72, 48]) @ stp.W709) / float(np.float32([236, 234, 228]) @ stp.W709)
    assert L["hard_k"] == pytest.approx(wall, abs=0.06)
    # the drawn strip: 0.5 darkening, band 4 px, blur 1.8 px -> fitted back
    assert L["soft_k"] == pytest.approx(0.5, abs=0.06) and L["width_px"] == pytest.approx(4.0, abs=0.75)
    assert L["blur_px"] == pytest.approx(1.8, abs=0.6) and L["fit_rms"] < 0.03
    for s in ("top", "right", "bottom"):                     # crisp paper up to the frame: no soft shadow invented
        assert sides[s]["soft_k"] == 0.0 and 0.15 < sides[s]["hard_k"] < 0.45   # the pad lies on the oak face


def test_rebuilt_layers_reproduce_the_baked_shadow_over_white_art(tmp_path):
    """The art covers the baked shadow, so the rebuilt layers must put it back: a white card under the hard + soft
    layers (Multiply) must match the photo's own paper + wall brightness across the left edge."""
    from app import sam_frames as sf
    rgb, q = wall_scene()
    img = rgb.astype("float32") / 255
    aq = sf.offset_quad(q, 1.5)
    files = stp.make_layers(img, q, aq, [400, 600], "full", tmp_path, None, pad=1.5)
    meta = files["_meta"]
    a = lambda f: np.asarray(Image.open(tmp_path / f)).astype("float32")[..., 3] / 255
    mult = (1 - a("L_hard.png") * meta["Frame Hard Shadow"]["opacity"]) * \
           (1 - a("L_edge.png") * meta["Frame Edge Shadow"]["opacity"])
    Y = img @ stp.W709
    paper = float(np.median(Y[sf.poly_coverage(sf.offset_quad(q, -40), 900, 800) > 0.99]))
    y = 400
    xl = float(sf.offset_quad(q, 0)[0][0] + (y - q[0][1]) / (q[3][1] - q[0][1]) * (q[3][0] - q[0][0]))
    for d in (-1.0, 0.5, 1.5, 2.5, 4.0, 6.0, 9.0):              # px inward from the opening (negative = the pad)
        x = int(round(xl + d - 0.5))
        assert mult[y, x] * paper == pytest.approx(float(Y[y, x]), abs=0.07), d
    assert meta["Frame Hard Shadow"]["pad_px"] == 1.5


class CardCraft:
    """Fake photocraft for the card test: the art card shows inside `visible` (anti-aliased) on a grey room."""

    def __init__(self, visible, size=(900, 800)):
        self.visible, self.size = np.float32(visible), size

    def __call__(self, settings, args):
        from app import sam_frames as sf
        if "--out" not in args:                                   # exportContents: the smart object's pixels
            p = json.loads(args[args.index("layer.smartObjects.exportContents") + 2])["path"]
            Image.new("RGB", (400, 600), "white").save(p)
            return "{}"
        card = json.loads(args[args.index("layer.smartObjects.replaceContents") + 2])["path"]
        v = np.asarray(Image.open(card).convert("RGB"))[0, 0].astype("float32")
        W, H = self.size
        cov = sf.poly_coverage(self.visible, W, H)[..., None]
        out = np.full((H, W, 3), 120, "float32") * (1 - cov) + v * cov
        Image.fromarray(np.round(out).astype("uint8")).save(args[args.index("--out") + 1])
        return "{}"


def test_card_test_accepts_the_pad_and_fails_a_sliver_or_more_overlap(tmp_path, monkeypatch):
    from app import sam_frames as sf
    from test_sam_frames import Q
    aq = sf.offset_quad(Q, 1.5)
    monkeypatch.setattr(stp, "_run", CardCraft(aq))
    r = real_card_verify(tmp_path / "t.psd", aq, None, tmp_path, opening=Q)
    assert all(p == pytest.approx(1.5, abs=0.15) for p in r["pad_px"].values()) and r["max_px"] <= 0.3
    short = sf.offset_quad(Q, [1.5, 1.5, 1.5, -3.0])
    monkeypatch.setattr(stp, "_run", CardCraft(short))            # left side 3 px short of the frame's inner edge
    with pytest.raises(stp.TemplateError, match=r"left: a (2\.9|3\.0)\d px sliver"):
        real_card_verify(tmp_path / "t.psd", short, None, tmp_path, opening=Q)
    wide = sf.offset_quad(Q, 3.5)
    monkeypatch.setattr(stp, "_run", CardCraft(wide))             # 3.5 px over the frame on every side
    with pytest.raises(stp.TemplateError, match="over the frame"):
        real_card_verify(tmp_path / "t.psd", wide, None, tmp_path, opening=Q)
