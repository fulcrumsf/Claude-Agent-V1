"""Gallery-wrap side strips for canvas templates (app/wrap_strips.py, Tony 2026-11-17: mockups must look real).
A synthetic canvas in a floater frame: flat orange face, a visible RIGHT side (saturated orange fading to brown, the old
pre-white-side scenes), a dark gap and a light wood lip on every side. PhotoCraft is faked; no credits."""
import json
import shutil
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from app import scene_templates as stp, template_checker as tc, wrap_strips as ws

FACE = [[200, 100], [400, 100], [400, 400], [200, 400]]       # tl, tr, br, bl (pixel-edge coordinates)
SIDE_W = 10                                                     # visible orange side
GAP_R, GAP = 4, 8                                               # right gap / gap on the other sides
FACE_RGB = (250, 215, 170)


def canvas_scene(path=None, W=640, H=500):
    a = np.full((H, W, 3), (200, 196, 190), "float32")                 # wall
    wood = (205, 182, 150)
    a[100 - GAP - 12:400 + GAP + 12, 200 - GAP - 12:400 + SIDE_W + GAP_R + 12] = wood
    a[100 - GAP:400 + GAP, 200 - GAP:400 + SIDE_W + GAP_R] = (70, 58, 48)  # the gap (dark, low chroma)
    for k in range(SIDE_W):                                             # orange side: light at the face, darker back
        t = k / (SIDE_W - 1)
        a[100:400, 400 + k] = np.float32((235, 120, 40)) * (1 - 0.6 * t)
    a[100:400, 200:400] = FACE_RGB
    img = np.uint8(np.clip(np.round(a), 0, 255))
    if path:
        Image.fromarray(img).save(path)
    return img


def test_only_the_camera_facing_side_gets_a_strip_and_its_far_edge_is_measured():
    w = ws.measure(canvas_scene(), FACE, "canvas")
    assert list(w["sides"]) == ["right"]
    assert set(w["not_shown"]) == {"top", "bottom", "left"}
    sd = w["sides"]["right"]
    assert sd["far_px"] == pytest.approx([SIDE_W, SIDE_W], abs=0.75)    # side -> gap step, not the gap -> wood one
    q = np.float32(sd["quad"])
    assert np.allclose(q[0], FACE[1]) and np.allclose(q[3], FACE[2])  # the strip starts exactly on the art edge
    assert q[1][1] == pytest.approx(100, abs=0.5) and q[2][1] == pytest.approx(400, abs=0.5)   # free ends: face lines
    g = np.float32(sd["shade"])
    assert g.shape == (ws.NV, ws.NU)
    assert g[:, 0].mean() > g[:, -1].mean() + 0.1                       # light near the face, dark at the back
    assert sd["round_corners"] == [1, 2]
    assert ws.measure(canvas_scene(), FACE, "frame") is None            # only canvas templates


def test_composite_replaces_the_orange_side_keeps_the_face_and_everything_else(tmp_path):
    scene = canvas_scene()
    H, W = scene.shape[:2]
    w = ws.measure(scene, FACE, "canvas")
    art = np.zeros((300, 200, 3), "uint8")
    art[:] = (30, 60, 230)                                              # a blue print
    render = scene.copy()
    render[100:400, 200:400] = art                                      # the face as PhotoCraft renders it
    out = ws.composite(render, scene, art, w).astype(int)
    assert (out[100:400, 200:400] == render[100:400, 200:400]).all()   # face art untouched
    cov = ws.coverage(np.float32(w["sides"]["right"]["quad"]), W, H)
    assert (out[cov == 0] == render[cov == 0]).all()                    # nothing outside the strip changes
    inner = out[110:390, 401:409]
    assert (inner[..., 2] > inner[..., 0]).all()                        # the strip is the art's blue, no orange left
    assert inner[:, 0].mean() > inner[:, -1].mean()                     # with the photo's shadow gradient
    assert (render[110:390, 401:409, 0] > render[110:390, 401:409, 2]).all()   # (it was orange before)


def test_band_is_the_mirrored_outer_edge_of_the_art_per_side():
    a = np.arange(12, dtype="float32").reshape(3, 4)                    # rows y, cols x
    assert ws.band_source(a, "right", 2).tolist() == [[3, 2], [7, 6], [11, 10]]
    assert ws.band_source(a, "left", 2).tolist() == [[8, 9], [4, 5], [0, 1]]
    assert ws.band_source(a, "top", 2).tolist() == [[0, 4], [1, 5], [2, 6], [3, 7]]
    assert ws.band_source(a, "bottom", 2).tolist() == [[11, 7], [10, 6], [9, 5], [8, 4]]


def test_two_visible_sides_meet_on_the_box_edge():
    q = stp_quads = ws.strip_quads(FACE, {1: (10.0, 10.0), 2: (6.0, 6.0)})
    r, b = np.float32(q["right"]), np.float32(q["bottom"])
    assert np.allclose(r[2], [410, 406]) and np.allclose(b[1], [410, 406])   # both end at the far lines' crossing
    assert np.allclose(r[3], b[0])                                       # and share the face corner
    assert stp_quads["right"][1][1] == pytest.approx(100)                # the free top end follows the face's top line


def test_placeholder_is_neutral_grey_and_only_on_the_strip(tmp_path):
    scene = canvas_scene()
    w = ws.measure(scene, FACE, "canvas")
    p = ws.placeholder_png(w, scene.shape[1], scene.shape[0], tmp_path / "L_wrap.png")
    im = np.asarray(Image.open(p))
    on = im[..., 3] > 250
    assert on.any() and (np.ptp(im[on][:, :3].astype(int), axis=1) <= 1).all()     # grey, not a photo copy
    assert im[:, :398, 3].max() == 0 and im[:, 420:, 3].max() == 0


def _strip_manifest(tmp_path):
    scene = canvas_scene(tmp_path / "Scene.png")
    shutil.copyfile(tmp_path / "Scene.png", tmp_path / "T.psd")        # the fake PhotoCraft renders = the scene
    w = ws.measure(scene, FACE, "canvas")
    return {"psd": "T.psd", "scene": "Scene.png", "so_px": [200, 300], "quad_art": FACE, "presentation": "canvas",
            "wrap_strips": w}


class Craft:
    def __init__(self):
        self.calls = []

    def __call__(self, settings, args):
        self.calls.append(args)
        out = Path(args[args.index("--out") + 1])
        shutil.copyfile(args[1], out)
        return "{}"


def test_render_psd_draws_strips_only_for_templates_that_have_them(tmp_path, monkeypatch):
    craft = Craft()
    monkeypatch.setattr(stp, "_run", craft)
    monkeypatch.setattr(stp, "so_size", lambda *a, **k: [200, 300])
    art = tmp_path / "art.png"
    Image.new("RGB", (200, 300), (30, 60, 230)).save(art)
    man = _strip_manifest(tmp_path)
    (tmp_path / "w0").mkdir()
    # no wrap_strips: exactly the old render (no hide command, no strip)
    r0 = stp.render_psd(tmp_path / "T.psd", [200, 300], art, tmp_path / "plain.png", work=tmp_path / "w0",
                        manifest={k: v for k, v in man.items() if k != "wrap_strips"})
    assert ws.LAYER not in " ".join(craft.calls[-1]) and r0["wrap_strips"] == []
    assert (np.asarray(Image.open(tmp_path / "plain.png")) == np.asarray(Image.open(tmp_path / "Scene.png"))).all()
    # with wrap_strips: the grey placeholder is hidden and the strip is drawn over the orange side
    (tmp_path / "w1").mkdir()
    r1 = stp.render_psd(tmp_path / "T.psd", [200, 300], art, tmp_path / "wrap.png", work=tmp_path / "w1", manifest=man)
    assert ws.LAYER in " ".join(craft.calls[-1]) and r1["wrap_strips"] == ["right"]
    out = np.asarray(Image.open(tmp_path / "wrap.png")).astype(int)
    assert (out[110:390, 401:409, 2] > out[110:390, 401:409, 0]).all()
    # wrap=False (the before image): placeholder hidden, no strip
    (tmp_path / "w2").mkdir()
    r2 = stp.render_psd(tmp_path / "T.psd", [200, 300], art, tmp_path / "off.png", work=tmp_path / "w2", manifest=man,
                        wrap=False)
    assert r2["wrap_strips"] == [] and ws.LAYER in " ".join(craft.calls[-1])


def test_assemble_puts_the_placeholder_above_the_base_below_the_art(tmp_path, monkeypatch):
    craft = Craft()
    monkeypatch.setattr(stp, "_run", craft)
    Image.new("RGB", (8, 8)).save(tmp_path / "base.png")
    files = {n: f"{n}.png" for n in ("Light Shadow", "Frame Edge Shadow", "Frame Hard Shadow", "Glass Sheen")}
    files["Wrap Strip"] = "L_wrap.png"
    stp.assemble(tmp_path / "base.png", tmp_path, files, FACE, tmp_path / "t.psd")
    a = " ".join(craft.calls[0])
    i_wrap, i_art = a.index("L_wrap.png"), a.index("placeholder.png")
    assert a.index(stp.BASE_NAME) < i_wrap < a.index(ws.LAYER) < i_art < a.index("SHADOWS")
    craft.calls.clear()
    files.pop("Wrap Strip")
    stp.assemble(tmp_path / "base.png", tmp_path, files, FACE, tmp_path / "t.psd")
    assert ws.LAYER not in " ".join(craft.calls[0])                      # frames / mats: no strip layer


def test_checker_knows_the_strip_layer_and_never_calls_it_an_overlay_or_the_base():
    flat = tc.flatten([{"id": 1, "name": "SHADOWS", "kind": "Group", "children": [
                           {"id": 2, "name": "Light Shadow", "kind": "Pixel", "blend": "Multiply"}]},
                       {"id": 3, "name": tc.ART, "kind": "Smart Object"},
                       {"id": 4, "name": ws.LAYER, "kind": "Pixel", "blend": "Normal"},
                       {"id": 5, "name": stp.BASE_NAME, "kind": "Pixel"}])
    r = tc.roles(flat)
    assert [l["id"] for l in tc.wrap_layers(flat)] == [4]
    assert r["base"]["id"] == 5 and 4 not in [l["id"] for l in r["overlays"] + r["mats"] + r["foreground"]]


def test_add_to_template_backs_up_bakes_the_layer_and_records_the_strips(tmp_path, monkeypatch):
    t = tmp_path / "AI_Test"
    (t / "Archive").mkdir(parents=True)
    canvas_scene(t / "AI_Test_Scene.png")
    (t / "AI_Test_Template.psd").write_bytes(b"psd v1")
    man = {"psd": "AI_Test_Template.psd", "scene": "AI_Test_Scene.png", "so_px": [200, 300], "quad_art": FACE,
           "presentation": "canvas"}
    (t / "template.json").write_text(json.dumps(man))
    monkeypatch.setattr(tc, "info", lambda *a, **k: {"layers": [{"id": 1, "name": stp.BASE_NAME, "kind": "Pixel"}]})
    calls = []

    def run(settings, args):
        calls.append(args)
        Path(args[args.index("--out") + 1]).write_bytes(b"psd v2")
    w = ws.add_to_template(t, run=run, log=lambda *_: None)
    assert list(w["sides"]) == ["right"]
    a = " ".join(calls[0])
    assert ws.LAYER in a and a.index(stp.BASE_NAME) < a.index("file.placeEmbedded")
    assert (t / "AI_Test_Template.psd").read_bytes() == b"psd v2"
    arch = sorted(p.name for p in (t / "Archive").iterdir())
    assert any(n.endswith(".psd") and "before_wrap_strips" in n for n in arch)
    assert (t / "Archive" / next(n for n in arch if n.endswith(".psd"))).read_bytes() == b"psd v1"
    new = json.loads((t / "template.json").read_text())
    assert new["wrap_strips"]["sides"]["right"] and new["so_px"] == [200, 300]
    (t2 := tmp_path / "No_Archive").mkdir()
    shutil.copy(t / "template.json", t2 / "template.json")
    shutil.copy(t / "AI_Test_Scene.png", t2 / "AI_Test_Scene.png")
    with pytest.raises(stp.TemplateError, match="Archive"):           # agents never create the Archive folder
        ws.add_to_template(t2, run=run, log=lambda *_: None)


def test_seam_pixel_is_art_plus_strip_never_a_dark_line():
    """A face edge half way through a pixel: that pixel is half art, half strip (the strip's alpha is capped at the
    art's leftover coverage; an overlap subtracted the photo twice and drew a dark 1 px line)."""
    scene = canvas_scene()
    w = ws.measure(scene, FACE, "canvas")
    face_half = [[200, 100], [399.5, 100], [399.5, 400], [200, 400]]         # the art covers half of column 399
    art = np.full((300, 200, 3), (30, 60, 230), "uint8")
    render = scene.astype("float32")
    render[100:400, 200:399] = art[:, :199]
    render[100:400, 399] = 0.5 * np.float32(art[:, 199]) + 0.5 * render[100:400, 399]
    w["sides"]["right"]["quad"] = [[399.5, 100], *w["sides"]["right"]["quad"][1:3], [399.5, 400]]
    out = ws.composite(np.uint8(np.round(render)), scene, art, w, face_half).astype(int)
    seam, strip = out[150:350, 399], out[150:350, 400]
    assert (np.abs(seam - (0.5 * art[0, 0] + 0.5 * strip)) <= 3).all()


# ---------- a PLAIN canvas hung on the wall, no frame (Tony 2026-11-18) ----------
# White side edges next to an orange face, a pale wall that is as light as the side, the side seen as a trapezoid
# (its free ends recede in perspective), a soft shadow beyond it, and the face's fold catching the light on top/left.
PLAIN_SIDE = [(400, 100), (412, 104), (412, 394), (400, 400)]       # right side: top end slants down, bottom end up
PLAIN_FACE_RGB = (195, 118, 67)


def plain_canvas_scene(W=640, H=500, ss=4):
    from PIL import ImageDraw
    big = Image.new("RGB", (W * ss, H * ss), (214, 211, 207))         # pale wall, as light as the white side
    d = ImageDraw.Draw(big)
    S = lambda pts: [(x * ss, y * ss) for x, y in pts]
    d.polygon(S([(412, 104), (440, 112), (440, 404), (412, 394)]), fill=(150, 142, 136))   # the canvas's shadow
    d.polygon(S([(198, 98), (400, 98), (400, 100), (200, 100), (200, 400), (198, 400)]), fill=(250, 236, 222))  # lit fold
    d.polygon(S(PLAIN_SIDE), fill=(232, 232, 235))                    # white side edge
    d.polygon(S(FACE), fill=PLAIN_FACE_RGB)
    return np.asarray(big.resize((W, H), Image.BOX))


def test_plain_canvas_strip_is_the_white_side_only_and_its_true_trapezoid():
    w = ws.measure(plain_canvas_scene(), FACE, "canvas")
    assert list(w["sides"]) == ["right"]                                # the pale wall is never read as a side
    assert set(w["not_shown"]) == {"top", "bottom", "left"}
    sd = w["sides"]["right"]
    assert sd["far_px"] == pytest.approx([12, 12], abs=0.6)             # ends on the side -> shadow step
    q = np.float32(sd["quad"])
    assert q[1] == pytest.approx([412, 104], abs=0.8)                   # free ends: the measured end edges,
    assert q[2] == pytest.approx([412, 394], abs=0.8)                   # not the face's top / bottom lines
    g = np.float32(sd["shade"])
    assert sd["shade_basis"].startswith("white side") and g.max() <= 1.0  # white paint is not light: never glows
    p = ws.placeholder_png(w, 640, 500, Path(__import__("tempfile").mkdtemp()) / "L.png")
    a = np.asarray(Image.open(p))[..., 3] / 255.0
    side = ws.coverage(np.float32(PLAIN_SIDE), 640, 500)
    assert np.abs(a - side).sum() / side.sum() < 0.08                   # the PSD placeholder = the real side shape


def test_corrected_art_edge_keeps_the_strips_on_the_measured_sides():
    """Detection runs on the uncorrected quad; the strip's far edge stays where the photo shows it and attaches to the
    corrected art edge (detecting on a corrected edge drew strips on the wrong sides, 2026-11-18)."""
    scene = plain_canvas_scene()
    q_sam = tc.offset_quad(np.float32(FACE), [-2.0, 2.0, 1.5, -2.0])  # SAM: 2 px inside top/left, onto the side right
    offs = [2.0, -2.0, -1.5, 2.0]
    w = ws.measure(scene, q_sam, "canvas", art_offsets=offs)
    assert list(w["sides"]) == ["right"]
    assert np.allclose(w["art_quad"], tc.offset_quad(q_sam, offs), atol=1e-3)
    sd = w["sides"]["right"]
    assert sd["far_px"] == pytest.approx([sd["far_px_detected"][0] + 2.0, sd["far_px_detected"][1] + 2.0], abs=1e-6)
    assert np.float32(sd["quad"])[1][0] == pytest.approx(412, abs=0.8)


def test_a_box_never_shows_two_opposite_sides():
    far, info = ws.measure_sides(plain_canvas_scene(), FACE)
    assert not (0 in far and 2 in far) and not (1 in far and 3 in far)


def test_lit_fold_softens_the_unseen_edges_and_a_dark_gap_gets_none():
    w = ws.measure(plain_canvas_scene(), FACE, "canvas")
    assert set(w["folds"]) == {"top", "left"}                           # the lit rim, never the strip side
    assert all(ws.FOLD_MIN <= f["width_px"] <= ws.FOLD_MAX and f["shade"] <= ws.FOLD_SHADE[1]
               for f in w["folds"].values())
    assert ws.measure(canvas_scene(), FACE, "canvas")["folds"] == {}    # floater: face -> dark gap, no fold
    art = np.full((300, 200, 3), (30, 60, 230), "uint8")
    rgb, a = ws.strip_layer(w, 640, 500, art)
    assert a[99, 250] > 0.2 and a[97, 250] == 0                         # over the rim, fading out before the wall
    rgb0, a0 = ws.strip_layer(w, 640, 500, None)
    assert a0[99, 250] == 0                                             # the PSD placeholder shows strips only
