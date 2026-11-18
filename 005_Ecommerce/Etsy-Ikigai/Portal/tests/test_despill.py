"""Orange despill around the art (app/despill.py, Tony 2026-11-17: real art bounces its own colour, never orange).
A synthetic canvas in a light wood floater: flat onion-skin orange face, a gap whose wood is lit by orange bounce
(wood x face, exactly what the Japandi 11x14 scene shows), plain wood beyond, a grey wall. PhotoCraft is faked."""
import json
import shutil
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from app import despill as dsp, scene_templates as stp, template_checker as tc, wrap_strips as ws

FACE = [[200, 100], [400, 100], [400, 400], [200, 400]]
FACE_RGB = (240, 190, 135)
WOOD = (205, 182, 150)
GAP = 6
SPILL = (122, 81, 49)          # the gap's wood lit by the orange (measured on the Japandi bottom gap)


def scene(face_rgb=FACE_RGB, wood=WOOD, gap_rgb=SPILL, face_bottom=400, W=640, H=500):
    a = np.full((H, W, 3), (200, 196, 190), "float32")
    a[100 - GAP - 30:400 + GAP + 30, 200 - GAP - 30:400 + GAP + 30] = wood
    a[100 - GAP:400 + GAP, 200 - GAP:400 + GAP] = gap_rgb
    a[100:face_bottom, 200:400] = face_rgb
    return np.uint8(a)


def orange(img, ref):
    """Orange-ness on the despill axis (chromaticity projection) per pixel, for a given face colour."""
    L = dsp.lin(np.float32(img) / 255.0)
    c = L / np.maximum(L @ dsp.W709, 1e-5)[..., None]
    F = dsp.lin(np.float32(ref) / 255.0)
    ax = F / float(F @ dsp.W709) - 1
    return (c - 1) @ (ax / np.linalg.norm(ax))


def test_synthetic_orange_spill_in_the_gap_is_neutralised_and_its_luminance_kept():
    img = scene()
    out, info = dsp.apply(img, FACE)
    assert info["applied"] and out is not None
    gap = np.s_[401:405, 220:380]                                       # bottom gap, away from the corners
    s0, s1 = orange(img, FACE_RGB)[gap], orange(out, FACE_RGB)[gap]
    wood_s = orange(np.uint8([[WOOD]]), FACE_RGB)[0, 0]
    assert s0.mean() > wood_s + 0.5                                     # it was clearly orange
    assert s1.max() <= wood_s + dsp.MARGIN * info["orange_axis"] + 0.03  # now no more orange than the wood allows
    Y = lambda x: dsp.lin(np.float32(x) / 255.0) @ dsp.W709
    assert np.allclose(Y(out[gap]), Y(img[gap]), rtol=0.03, atol=0.002)  # luminance kept
    for nm in ("top", "left", "right"):
        assert info["sides"][nm]["s_band_after"] < info["sides"][nm]["s_band_before"] - 0.3


def test_face_art_area_and_plain_wood_are_untouched():
    img = scene()
    out, info = dsp.apply(img, FACE)
    assert (out[101:399, 201:399] == img[101:399, 201:399]).all()       # the face the art covers is untouched (only
    #                                                                     the edge pixel ring, 0.5 px tolerance)
    band = dsp.band_px(FACE)
    far = int(np.ceil(band)) + 1
    assert (out[400 + far:400 + GAP + 30, 210:390] == img[400 + far:400 + GAP + 30, 210:390]).all()   # wood beyond
    assert (out[400 + GAP:400 + far, 210:390] == img[400 + GAP:400 + far, 210:390]).all()   # wood inside the band too
    assert (out[:60] == img[:60]).all() and (out[:, :150] == img[:, :150]).all()             # wall


def test_warm_walnut_frame_without_spill_is_not_despilled():
    """Walnut is 'more orange' than the onion-skin face in chromaticity, but it is the frame's own colour: the
    reference is the most orange material in the ring past the band, so it stays."""
    walnut, walnut_shade = (110, 70, 45), (72, 46, 30)
    img = scene(wood=walnut, gap_rgb=walnut_shade)
    out, info = dsp.apply(img, FACE)
    assert out is None or int(np.any(out != img, -1).sum()) < 50
    assert info.get("version") == dsp.VERSION


def test_orange_bounce_on_a_white_mat_bevel_goes_back_to_the_mats_white():
    img = scene(wood=(240, 238, 232), gap_rgb=(240, 215, 185))           # wide white mat, bevel tinted by the orange
    out, info = dsp.apply(img, FACE)
    bevel = out[401:405, 220:380].astype(int)
    assert info["sides"]["bottom"]["s_ref"] < 0.15                       # the reference is the white mat
    assert (np.ptp(bevel, axis=-1) < np.ptp(img[401:405, 220:380].astype(int), axis=-1) - 15).all()
    assert (out[420:440, 220:380] == img[420:440, 220:380]).all()        # the mat itself is untouched


def test_a_face_that_is_not_the_orange_blank_is_skipped():
    out, info = dsp.apply(scene(face_rgb=(238, 236, 231)), FACE)       # white insert
    assert out is None and not info["applied"] and "orange" in info["why"]
    rng = np.random.default_rng(3)
    printed = scene()
    printed[100:400, 200:400] = rng.integers(0, 255, (300, 200, 3))      # a print in the frame
    out, info = dsp.apply(printed, FACE)
    assert out is None and "not flat" in info["why"]


def test_half_pixel_orange_line_on_the_art_edge_is_gone():
    """The face runs half a pixel past the art's bottom edge: the art covers half of that pixel row, the other half
    showed the photo's orange face (a thin orange line). After the edge unmix it shows the gap."""
    img = scene()                                                       # face to y=400
    q = [[200, 100], [400, 100], [400, 399.5], [200, 399.5]]            # art ends half way through row 399
    out, _ = dsp.apply(img, q)
    art = np.float32([30, 60, 230])
    row = np.s_[399, 220:380]
    before = 0.5 * art + 0.5 * np.float32(img[row])
    after = 0.5 * art + 0.5 * np.float32(out[row])
    assert (before[:, 0] > 130).all()                                   # orange showed through (red 30 -> 135)
    assert (after[:, 0] < 90).all() and (after[:, 0] > 50).all()        # now the dark gap shows instead
    assert (np.abs(out[399, 220:380].astype(int) - out[402, 220:380].astype(int)) <= 3).all()   # = the despilled gap


def test_wrap_strip_pixels_and_face_art_are_identical_with_or_without_despill():
    from test_wrap_strips import canvas_scene
    sc = canvas_scene()
    q = [[200, 100], [400, 100], [400, 400], [200, 400]]
    w = ws.measure(sc, q, "canvas")
    ds, info = dsp.apply(sc, q)
    assert ds is not None
    art = np.full((300, 200, 3), (30, 60, 230), "uint8")
    outs = []
    for base in (sc, ds):
        r = base.copy()
        r[100:400, 200:400] = art
        outs.append(ws.composite(r, base, art, w).astype(int))
    H, W = sc.shape[:2]
    cov = ws.coverage(np.float32(w["sides"]["right"]["quad"]), W, H)
    full = cov >= 0.999
    assert full.sum() > 1000 and (outs[0][full] == outs[1][full]).all()   # the strip's own shading is untouched
    assert (outs[0][100:400, 200:400] == outs[1][100:400, 200:400]).all()


def test_leftover_check_flags_raw_spill_and_passes_after_despill_wrap_strips_excluded():
    img = scene()
    raw = dsp.leftover(img, FACE)
    assert raw["status"] == "fail" and raw["sides"]["bottom"]["orange_px"] > 100 and "display px^2" in raw["reason"]
    out, _ = dsp.apply(img, FACE)
    assert dsp.leftover(out, FACE)["status"] == "pass"
    assert dsp.leftover(scene(face_rgb=(238, 236, 231)), FACE)["status"] == "skip"
    # the area a wrap strip draws over is never counted
    strip = [[400, 100], [400 + GAP, 100], [400 + GAP, 400], [400, 400]]
    only_right = scene()
    only_right[100 - GAP:100, 200 - GAP:400 + GAP] = (130, 117, 101)     # neutral gap on top, bottom, left
    only_right[400:400 + GAP, 200 - GAP:400 + GAP] = (130, 117, 101)
    only_right[100:400, 200 - GAP:200] = (130, 117, 101)
    assert dsp.leftover(only_right, FACE)["sides"]["right"]["status"] == "fail"
    assert dsp.leftover(only_right, FACE, [strip])["sides"]["right"]["status"] == "pass"
    # the checker's wrapper reads the strips from the manifest and never raises
    man = {"wrap_strips": {"sides": {"right": {"quad": strip}}}}
    assert tc.spill_check(np.float32(only_right), FACE, man)["sides"]["right"]["status"] == "pass"
    assert tc.spill_check(None, FACE)["status"] == "skip"


def test_checker_knows_the_despill_layer_and_never_calls_it_an_overlay_or_the_base():
    flat = tc.flatten([{"id": 1, "name": "SHADOWS", "kind": "Group", "children": [
                           {"id": 2, "name": "Light Shadow", "kind": "Pixel", "blend": "Multiply"}]},
                       {"id": 3, "name": tc.ART, "kind": "Smart Object"},
                       {"id": 4, "name": ws.LAYER, "kind": "Pixel", "blend": "Normal"},
                       {"id": 6, "name": dsp.LAYER, "kind": "Pixel", "blend": "Normal"},
                       {"id": 5, "name": stp.BASE_NAME, "kind": "Pixel"}])
    r = tc.roles(flat)
    assert [l["id"] for l in tc.despill_layers(flat)] == [6]
    assert r["base"]["id"] == 5 and 6 not in [l["id"] for l in r["overlays"] + r["mats"] + r["foreground"]]


def test_layer_png_holds_only_the_corrected_pixels(tmp_path):
    img = scene()
    out, _ = dsp.apply(img, FACE)
    im = np.asarray(Image.open(dsp.layer_png(img, out, tmp_path / "L.png")))
    on = im[..., 3] == 255
    assert on.sum() == int(np.any(out != img, -1).sum()) and set(np.unique(im[..., 3])) <= {0, 255}
    assert (im[on][:, :3] == out[on]).all() and not on[102:398, 202:398].any()


class Craft:
    def __init__(self):
        self.calls = []

    def __call__(self, settings, args):
        self.calls.append(args)
        out = Path(args[args.index("--out") + 1])
        shutil.copyfile(args[1], out)
        return "{}"


def test_assemble_puts_despill_directly_above_the_base_below_the_strip_and_art(tmp_path, monkeypatch):
    craft = Craft()
    monkeypatch.setattr(stp, "_run", craft)
    Image.new("RGB", (8, 8)).save(tmp_path / "base.png")
    files = {n: f"{n}.png" for n in ("Light Shadow", "Frame Edge Shadow", "Frame Hard Shadow", "Glass Sheen")}
    files.update({"Wrap Strip": "L_wrap.png", "Despill": "L_despill.png"})
    stp.assemble(tmp_path / "base.png", tmp_path, files, FACE, tmp_path / "t.psd")
    a = " ".join(craft.calls[0])
    assert a.index(stp.BASE_NAME) < a.index("L_despill.png") < a.index(dsp.LAYER) < a.index("L_wrap.png") \
        < a.index("placeholder.png")


def test_base_for_matches_the_layer_only_when_the_template_has_it():
    img = scene()
    assert dsp.base_for(img, {"quad_art": FACE}) is img
    out, _ = dsp.apply(img, FACE)
    assert (dsp.base_for(img, {"quad_art": FACE, "despill": {"applied": True}}) == out).all()


def test_add_to_template_backs_up_bakes_the_layer_above_the_base_and_records_it(tmp_path, monkeypatch):
    t = tmp_path / "AI_Test"
    (t / "Archive").mkdir(parents=True)
    Image.fromarray(scene()).save(t / "AI_Test_Scene.png")
    (t / "AI_Test_Template.psd").write_bytes(b"psd v1")
    man = {"psd": "AI_Test_Template.psd", "scene": "AI_Test_Scene.png", "so_px": [200, 300], "quad_art": FACE}
    (t / "template.json").write_text(json.dumps(man))
    monkeypatch.setattr(tc, "info", lambda *a, **k: {"layers": [{"id": 1, "name": stp.BASE_NAME, "kind": "Pixel"}]})
    calls = []

    def run(settings, args):
        calls.append(args)
        Path(args[args.index("--out") + 1]).write_bytes(b"psd v2")
    inf = dsp.add_to_template(t, run=run, log=lambda *_: None)
    assert inf["applied"] and inf["layer"] == dsp.LAYER
    a = " ".join(calls[0])
    assert a.index(stp.BASE_NAME) < a.index("file.placeEmbedded") < a.index(dsp.LAYER)
    assert (t / "AI_Test_Template.psd").read_bytes() == b"psd v2"
    arch = sorted(p.name for p in (t / "Archive").iterdir())
    assert any(n.endswith(".psd") and "before_despill" in n for n in arch)
    assert any(n.endswith(".json") and "before_despill" in n for n in arch)
    new = json.loads((t / "template.json").read_text())
    assert new["despill"]["changed_px"] > 0 and new["so_px"] == [200, 300]
    (t2 := tmp_path / "No_Archive").mkdir()
    shutil.copy(t / "template.json", t2 / "template.json")
    shutil.copy(t / "AI_Test_Scene.png", t2 / "AI_Test_Scene.png")
    with pytest.raises(stp.TemplateError, match="Archive"):            # agents never create the Archive folder
        dsp.add_to_template(t2, run=run, log=lambda *_: None)
