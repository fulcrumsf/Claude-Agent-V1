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
