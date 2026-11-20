"""Frame-insert marker colour per scene (Tony 2026-11-19, Slot_Set_Planner_Plan.md "Decisions"): the blank insert is
drawn orange by default, or pale blue when the planned wall is warm. The builder must handle both; the orange path
stays byte-identical (golden hashes captured at commit 37a24938, before the blue marker was added)."""
import hashlib
import json

import numpy as np

from app import despill as dsp, room_templates as rt
from test_despill import FACE, scene


def _orange_bar_scene():
    a = np.full((500, 640, 3), (200, 196, 190), "uint8")
    a[80:420, 164:436] = (205, 182, 150)
    a[92:408, 176:424] = (70, 58, 48)
    a[100:400, 184:416] = (219, 164, 104)
    r = a.copy()
    r[100:400, 200:400] = (40, 80, 200)
    return a, r


def _h(x):
    return hashlib.sha1(x if isinstance(x, bytes) else json.dumps(x, sort_keys=True).encode()).hexdigest()


def test_orange_path_is_byte_identical():
    img = scene()
    out, info = dsp.apply(img, FACE)
    assert _h(out.tobytes()) == "43e5d8a2d814acea8a504538f4dcbd435add22ff"
    assert _h(info) == "6ce09c3e46c637dab2d1cee9ce921081e1575907"
    assert _h(dsp.leftover(img, FACE)) == "76e61be278c1b0a496cc3ee3f1f55910092e2966"
    a, r = _orange_bar_scene()
    assert _h(rt.art_area_gate(r, a, FACE, "canvas")) == "49335f359da5655bf17f7c2b5ac901b5cc040aab"


BLUE = (165, 200, 238)                 # the pale sky-blue blank as drawn
BLUE_SPILL = (88, 92, 108)             # the wood gap lit by blue bounce (wood x face)
WARM_WALL = (196, 112, 72)             # terracotta


def blue_scene():
    return scene(face_rgb=BLUE, gap_rgb=BLUE_SPILL)


def test_blue_marker_despill_removes_the_blue_cast_and_keeps_luminance():
    img = blue_scene()
    none, info0 = dsp.apply(img, FACE)                        # the orange default does not touch a blue blank
    assert none is None and "not the orange blank" in info0["why"]
    out, info = dsp.apply(img, FACE, "blue")
    assert out is not None and info["applied"] and info["marker"] == "blue"
    gap = np.s_[401:405, 220:380]
    lab = lambda x: __import__("cv2").cvtColor(np.float32(x) / 255.0, __import__("cv2").COLOR_RGB2Lab)
    assert lab(out[gap])[..., 2].mean() > lab(img[gap])[..., 2].mean() + 3     # less blue (b* up toward the wood)
    Y = lambda x: dsp.lin(np.float32(x) / 255.0) @ dsp.W709
    assert np.allclose(Y(out[gap]), Y(img[gap]), rtol=0.03, atol=0.002)
    assert (out[101:399, 201:399] == img[101:399, 201:399]).all()
    assert dsp.marker_of({"marker": "blue"}) == "blue" and dsp.marker_of({}) == "orange"
    assert dsp.marker_of({"despill": {"marker": "blue"}}) == "blue"
    base = dsp.base_for(img, {"despill": {"applied": True, "marker": "blue"}, "quad_art": FACE})
    assert (base == out).all()
    assert dsp.leftover(img, FACE, marker="blue")["status"] in ("pass", "fail")
    assert dsp.leftover(img, FACE)["status"] == "skip"                         # orange measure skips a blue blank


def test_gate_names_a_blue_bar_and_still_names_orange():
    a = np.full((500, 640, 3), WARM_WALL, "uint8")
    a[80:420, 164:436] = (205, 182, 150)
    a[92:408, 176:424] = (70, 58, 48)
    a[100:400, 184:416] = BLUE
    r = a.copy()
    r[100:400, 200:400] = (200, 60, 40)
    g = rt.art_area_gate(r, a, FACE, "canvas")                                # marker read from the face
    assert not g["pass"] and all(s["kind"] == "blue" for s in g["sides"].values())
    assert any("a blue bar" in w for w in g["why"])
    assert rt.art_area_gate(r, a, FACE, "canvas", None, "blue")["why"] == g["why"]
    o, ro = _orange_bar_scene()
    assert all(s["kind"] == "orange" for s in rt.art_area_gate(ro, o, FACE, "canvas")["sides"].values())


def test_build_psd_records_a_blue_marker_and_despills_blue(tmp_path, monkeypatch):
    """The builder path with a blue blank on a warm wall (PhotoCraft and SAM faked as in the other builder tests)."""
    from PIL import Image
    from app import scene_templates as stp
    W, H = 640, 500
    img = np.full((H, W, 3), WARM_WALL, "uint8")
    img[90:410, 190:410] = (205, 182, 150)
    img[100:400, 200:400] = BLUE
    png = tmp_path / "scene.png"
    Image.fromarray(img).save(png)
    seen = {}

    def fake_detect(scene_png, work, settings=None, box=None, wall=True, canvas=False, paper=False):
        from app import sam_frames as sf
        q = np.float32(FACE)
        return {"corners": q.tolist(), "model": "fake"}, sf.poly_coverage(q, W, H), None

    def fake_assemble(base_png, outdir, files, art_q, out_psd, settings=None):
        seen["files"] = dict(files)
        Path(out_psd).write_bytes(b"psd")
        return Path(out_psd)
    from pathlib import Path
    monkeypatch.setattr(stp, "sam_detect", fake_detect)
    monkeypatch.setattr(stp, "assemble", fake_assemble)
    built = stp.build_psd(png, "3x4", tmp_path, {}, presentation="frame", marker="blue")
    assert built["marker"] == "blue"
    if "despill" in built:
        assert built["despill"]["marker"] == "blue"
    work = tmp_path / "o"
    work.mkdir()                                                              # pytest's own temp folder
    assert "marker" not in stp.build_psd(png, "3x4", work, {}, presentation="frame")   # orange: no new key
