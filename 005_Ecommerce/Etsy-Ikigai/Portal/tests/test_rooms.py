import math

import numpy as np
import pytest
from PIL import Image

from app import rooms
from app.pipeline.base import NotConfigured


def _scene(tmp_path, quad, size=(600, 600)):
    import cv2
    img = np.full((size[1], size[0], 3), 200, "uint8")
    cv2.fillConvexPoly(img, np.array(quad, "int32"), (255, 0, 255))
    p = tmp_path / "scene.png"
    Image.fromarray(img).save(p)
    return p


def test_find_frame_reads_corners_and_aspect(tmp_path):
    p = _scene(tmp_path, [(200, 100), (400, 100), (400, 400), (200, 400)])
    quad, info = rooms.find_frame(np.array(Image.open(p).convert("RGB")))
    assert quad is not None and abs(info["aspect"] - 200 / 300) < 0.02


def test_find_frame_rejects_missing_and_tiny(tmp_path):
    p = tmp_path / "plain.png"
    Image.new("RGB", (400, 400), (200, 200, 200)).save(p)
    quad, why = rooms.find_frame(np.array(Image.open(p)))
    assert quad is None and "no magenta" in why
    q = _scene(tmp_path, [(10, 10), (30, 10), (30, 40), (10, 40)])
    assert rooms.find_frame(np.array(Image.open(q).convert("RGB")))[0] is None


def test_pick_print_keeps_planned_shape_or_nearest(tmp_path):
    arts = [tmp_path / f"X_{t}_1.jpg" for t in ("2x3", "3x4", "4x5")]
    p, tag, note = rooms.pick_print(arts, "3x4", 0.74, 0.12)
    assert tag == "3x4" and not note
    p, tag, note = rooms.pick_print(arts, "3x4", 0.63, 0.12)     # frame came out taller than planned
    assert tag == "2x3" and "instead" in note
    with pytest.raises(NotConfigured):
        rooms.pick_print([], "2x3", 0.67, 0.12)


def test_composite_puts_the_art_in_the_frame(tmp_path):
    scene = _scene(tmp_path, [(200, 100), (400, 100), (400, 400), (200, 400)])
    art = tmp_path / "art.jpg"
    Image.new("RGB", (400, 600), (10, 120, 30)).save(art)
    quad, _ = rooms.find_frame(np.array(Image.open(scene).convert("RGB")))
    out = tmp_path / "out.jpg"
    rooms.composite(scene, quad, art, out)
    im = Image.open(out)
    r, g, b = im.getpixel((300, 250))
    assert g > r and g > b and im.size == (600, 600)
    assert im.getpixel((50, 50))[0] > 150                         # wall untouched


def test_cached_scene_needs_no_engine(tmp_path):
    settings = {"rooms_cache": str(tmp_path)}
    scene = rooms.SCENES[0]
    import shutil
    src = _scene(tmp_path, [(200, 100), (400, 100), (400, 400), (200, 400)])
    shutil.copyfile(src, rooms.scene_file(settings, scene))
    path, quad, info, calls = rooms.ensure_scene(settings, scene, None)
    assert path is not None and calls == 0
    other = rooms.SCENES[1]
    assert rooms.ensure_scene(settings, other, None)[0] is None


# ---------- v2 recipe (Mockup_Docs/Mockup_Style_Guide.md 3b, 4a-4c) ----------
def _persp_quad(deg=30, w=200, h=300, f=1200, size=1000):
    X = np.array([[-w, -h, 0], [w, -h, 0], [w, h, 0], [-w, h, 0]], float)
    t = math.radians(deg)
    R = np.array([[math.cos(t), 0, math.sin(t)], [0, 1, 0], [-math.sin(t), 0, math.cos(t)]])
    P = (R @ X.T).T + [0, 0, 2000]
    return np.stack([f * P[:, 0] / P[:, 2] + size / 2, f * P[:, 1] / P[:, 2] + size / 2], 1)


def _shadowed_scene(tmp_path, quad, size=1000, name="scene.png"):
    """Wall + magenta paper with a dark window-bar band across both (the band is ~30 % brightness)."""
    import cv2
    img = np.full((size, size, 3), (225, 210, 190), "uint8")
    cv2.fillConvexPoly(img, np.array(quad).round().astype("int32"), (250, 30, 220))
    band = np.zeros((size, size), bool)
    band[430:470, :] = True
    img[band] = (img[band] * 0.3).astype("uint8")
    p = tmp_path / name
    Image.fromarray(img).save(p)
    return p


def test_true_aspect_undoes_perspective():
    q = _persp_quad(30)
    assert abs(rooms.true_aspect(q.astype("float32"), (1000, 1000)) - 2 / 3) < 0.02
    flat = np.array([[400, 300], [600, 300], [600, 600], [400, 600]], "float32")
    assert abs(rooms.true_aspect(flat, (1000, 1000)) - 2 / 3) < 0.01


def test_find_frame_off_axis_shadowed_and_prop_on_corner(tmp_path):
    import cv2
    q = _persp_quad(30)
    p = _shadowed_scene(tmp_path, q)
    img = np.array(Image.open(p).convert("RGB"))
    cv2.circle(img, tuple(int(v) for v in q[2]), 22, (120, 90, 60), -1)      # a prop over the bottom-right corner
    quad, info = rooms.find_frame(img)
    assert quad is not None, info
    assert np.abs(quad - q).max() < 4                                           # corner rebuilt under the prop
    assert abs(info["aspect"] - 2 / 3) < 0.04 and info["screen_aspect"] < 0.62


def test_magenta_mask_keeps_shadowed_paper():
    px = np.array([[[250, 30, 220], [75, 9, 66], [40, 3, 30], [225, 210, 190], [200, 40, 30]]], "uint8")
    assert rooms.magenta_mask(px)[0].tolist() == [True, True, True, False, False]


def test_brief_puts_a_light_cat_print_in_a_sunny_reading_nook(tmp_path):
    art = tmp_path / "Cat_2x3_24x36.jpg"
    a = np.full((300, 200, 3), (239, 216, 182), "uint8")
    a[200:, :] = (20, 20, 20)
    a[20:60, 60:120] = (204, 46, 19)
    Image.fromarray(a).save(art)
    an = rooms.analyze_print(art)
    assert an["value_key"] == "light" and an["accents"][0]["name"].endswith("red")
    b = rooms.brief_v2("Book Club Cat: a cat asleep on an open book", an, "2x3")
    assert b["profile"] == "cute_light" and b["frame"] == "oak"
    assert b["persona"] in {p["key"] for p in rooms.PERSONAS["cute_light"]}
    assert b["persona"] == "bookish_renter"                     # 'red' accent matches her 'tomato red' palette
    prompt = rooms.scene_prompt_v2(b)
    for must in ("three-quarter", "mullions", "#FF00FF", "darker where the window-bar shadow", "No other artwork",
                 "straight-on catalogue look", "candid photo", "where she actually left them", "teak sideboard"):
        assert must in prompt
    assert "faces the wall straight on" not in prompt
    assert "home-decor magazine, " not in prompt                 # only ever named in the 'not a ...' line
    plate = rooms.scene_prompt_v2(b, plate=True)
    assert "no window-bar shadows" in plate and "no frame moulding" in plate and "candid photo" in plate
    assert rooms.pick_profile("gothic raven", "dark")["key"] == "dark_moody"     # value key + subject decide


def test_composite_v2_carries_the_shadow_and_never_outshines_the_wall(tmp_path):
    q = np.array([[300, 200], [700, 200], [700, 800], [300, 800]], "float32")
    scene = _shadowed_scene(tmp_path, q)
    art = tmp_path / "X_2x3_1.jpg"
    Image.new("RGB", (400, 600), (255, 255, 255)).save(art)
    quad, info = rooms.find_frame(np.array(Image.open(scene).convert("RGB")))
    out = tmp_path / "out.jpg"
    rep = rooms.composite_v2(scene, quad, art, out, 2 / 3, "oak")
    im = np.array(Image.open(out)).astype(float)
    lit, shade = im[300, 500].mean(), im[450, 500].mean()
    wall = np.array([225, 210, 190]).mean()
    assert lit <= wall * 1.0 and lit > wall * 0.8                     # white paper ~0.92 x the lit wall
    assert shade < lit * 0.45                                          # the window bar crosses the art
    assert rep["flags"] == [] and rep["hue_drift_deg"] < 8
    assert im[50, 50][0] > 200                                         # wall untouched


def test_composite_v2_flags_heavy_shadow(tmp_path):
    import cv2
    q = np.array([[300, 200], [700, 200], [700, 800], [300, 800]], "float32")
    img = np.full((1000, 1000, 3), (225, 210, 190), "uint8")
    cv2.fillConvexPoly(img, q.astype("int32"), (250, 30, 220))
    img[200:700, 300:700] = (img[200:700, 300:700] * 0.3).astype("uint8")     # 80 % of the paper in deep shadow
    img[690:800, 300:700] = (250, 30, 220)
    scene = tmp_path / "s.png"
    Image.fromarray(img).save(scene)
    art = tmp_path / "X_2x3_1.jpg"
    Image.new("RGB", (400, 600), (200, 60, 60)).save(art)
    rep = rooms.composite_v2(scene, q, art, tmp_path / "o.jpg", 2 / 3, "black")
    assert any("shadow covers" in f for f in rep["flags"])


def test_pick_print_v2_keeps_planned_shape_for_foreshortened_frame(tmp_path):
    arts = [tmp_path / f"X_{t}_1.jpg" for t in ("2x3", "3x4", "4x5")]
    p, tag, fit, note = rooms.pick_print_v2(arts, "2x3", {"aspect": 0.70, "screen_aspect": 0.58}, 0.12)
    assert tag == "2x3" and fit == pytest.approx(2 / 3) and not note
    p, tag, fit, note = rooms.pick_print_v2(arts, "2x3", {"aspect": 0.50, "screen_aspect": 0.48}, 0.12)
    assert fit == pytest.approx(0.50) and "cropped" in note                    # squeezed never, cropped instead


def test_v2_scene_cache_needs_no_engine(tmp_path):
    import shutil
    settings = {"rooms_cache": str(tmp_path / "rooms")}
    b = rooms.brief_v2("cat book", {"value_key": "light", "accents": []}, "2x3")
    assert rooms.scene_file_v2(settings, b).name.startswith("v2_08_cute_light_")
    q = np.array([[300, 200], [700, 200], [700, 800], [300, 800]], "float32")
    shutil.copyfile(_shadowed_scene(tmp_path, q), rooms.scene_file_v2(settings, b))
    path, quad, info, calls = rooms.ensure_scene_v2(settings, b, None)
    assert path is not None and calls == 0
    other = dict(b, profile="dark_moody", room="a study")
    assert rooms.ensure_scene_v2(settings, other, None)[0] is None
