"""Tony 2026-11-19 (slot 12): never a white border. The builder extends the art over flat blank bands beside the face
(wrap_strips.paper_bands / extend_quad) and the art-area gate (room_templates.art_area_gate) fails any render that
still shows a blank bar beside the art or the blank inside it. Synthetic scenes, no PhotoCraft."""
import numpy as np
import pytest

from app import room_templates as rt, wrap_strips as ws

FACE = [[200, 100], [400, 100], [400, 400], [200, 400]]       # tl, tr, br, bl
ORANGE = (219, 164, 104)
BAND = 16                                                       # the AI's white band down both long sides


def banded_scene(W=640, H=500):
    """A floater frame: wood lip, dark gap, a canvas whose orange face has a flat WHITE band down both long sides
    (slot 12's scene, symmetric, so not a perspective side)."""
    a = np.full((H, W, 3), (200, 196, 190), "uint8")
    a[100 - 20:400 + 20, 200 - BAND - 20:400 + BAND + 20] = (205, 182, 150)       # wood
    a[100 - 8:400 + 8, 200 - BAND - 8:400 + BAND + 8] = (70, 58, 48)              # gap
    a[100:400, 200 - BAND:400 + BAND] = (240, 240, 238)                           # white bands
    a[100:400, 200:400] = ORANGE                                                  # orange face (what SAM finds)
    return a


def art_render(scene, quad_x0, quad_x1, art=(40, 80, 200)):
    r = scene.copy()
    r[100:400, quad_x0:quad_x1] = art
    return r


def test_gate_fails_white_bars_left_beside_the_art():
    scene = banded_scene()
    g = rt.art_area_gate(art_render(scene, 200, 400), scene, FACE, "canvas")
    assert not g["pass"]
    assert set(g["sides"]) == {"left", "right"} and all(s["kind"] == "white" for s in g["sides"].values())
    assert g["sides"]["right"]["width_px"] == pytest.approx(BAND, abs=1.5)
    assert any("white bar" in w and "right edge" in w for w in g["why"])


def test_gate_passes_when_the_art_covers_the_bands():
    scene = banded_scene()
    wide = [[200 - BAND, 100], [400 + BAND, 100], [400 + BAND, 400], [200 - BAND, 400]]
    g = rt.art_area_gate(art_render(scene, 200 - BAND, 400 + BAND), scene, wide, "canvas")
    assert g["pass"], g["why"]


def test_gate_fails_the_blank_still_showing_inside_the_art():
    scene = banded_scene()
    wide = [[200 - BAND, 100], [400 + BAND, 100], [400 + BAND, 400], [200 - BAND, 400]]
    r = art_render(scene, 200 - BAND, 400 + BAND)
    r[100:400, 300:340] = scene[100:400, 300:340]                     # a strip of the art missing
    g = rt.art_area_gate(r, scene, wide, "canvas")
    assert not g["pass"] and g["inside_unchanged"] > 0.1 and "blank" in g["why"][0]


def test_gate_ignores_a_mat_and_the_wall():
    """A white mat is meant to show; a canvas hung on a pale wall has wall (no band) beside it."""
    scene = banded_scene()
    assert rt.art_area_gate(art_render(scene, 200, 400), scene, FACE, "mat")["pass"]
    wall = np.full((500, 640, 3), (214, 211, 207), "uint8")
    wall[100:400, 200:400] = ORANGE
    assert rt.art_area_gate(art_render(wall, 200, 400), wall, FACE, "canvas")["pass"]


def test_builder_finds_both_bands_and_extends_the_art_over_them():
    b = ws.paper_bands(banded_scene(), FACE)
    assert set(b) == {1, 3}                                           # right and left, not top / bottom (the gap)
    for e0, e1 in b.values():
        assert e0 == pytest.approx(BAND, abs=1.0) and e1 == pytest.approx(BAND, abs=1.0)
    q = ws.extend_quad(FACE, b)
    assert q[0] == pytest.approx([200 - BAND, 100], abs=1.0) and q[2] == pytest.approx([400 + BAND, 400], abs=1.0)


def test_extend_quad_follows_a_slanted_band_end():
    q = ws.extend_quad(FACE, {1: (10.0, 20.0)})                       # right side: 10 px out at the top, 20 at the bottom
    assert q[1] == pytest.approx([410, 100]) and q[2] == pytest.approx([420, 400])
    assert q[0] == pytest.approx([200, 100]) and q[3] == pytest.approx([200, 400])
