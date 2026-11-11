"""Template checker (app/template_checker.py): the measuring parts on synthetic images, plus the real known-PASS
regression on Tony's hand-verified Wabi bedroom (skipped when photocraft-cli or the PSD is not on this machine)."""
import shutil
from pathlib import Path

import cv2
import numpy as np
import pytest

from app import template_checker as tc

ROOT = Path(__file__).resolve().parents[2] / "Room_Templates" / "Portrait_Templates"
WABI = ROOT / "003_Ratio_3x4/002_Bedroom/BDRM_Wabi_Vertical/BDRM_Wabi_Vertical_Template.psd"


def framed(W=900, H=900, opening=(300, 200, 300, 400), frame=16, paper=(236, 234, 229)):
    """Greige wall, oak frame `frame` px wide around a blank paper opening (x, y, w, h)."""
    a = np.full((H, W, 3), (200, 192, 180), "float32")
    x, y, w, h = opening
    cv2.rectangle(a, (x - frame, y - frame), (x + w + frame - 1, y + h + frame - 1), (190, 150, 110), -1)
    a[y:y + h, x:x + w] = paper
    return a


def quad(x, y, w, h):
    return np.float32([[x, y], [x + w, y], [x + w, y + h], [x, y + h]])


def offsets(img, q, R=24):
    s = cv2.GaussianBlur(img, (0, 0), 0.8)
    return [tc.find_edge(s, q, i, R)[0] for i in range(4)]


def test_opening_edge_found_for_exact_fit_overlap_and_gap():
    img = framed()
    assert all(abs(o) <= 1.5 for o in offsets(img, quad(300, 200, 300, 400)))           # art = opening
    over = offsets(img, quad(284, 184, 332, 432))                                       # art 16 px over the frame
    assert all(-17.5 <= o <= -14.5 for o in over)
    gap = offsets(img, quad(310, 210, 280, 380))                                        # 10 px white sliver
    assert all(8.5 <= o <= 11.5 for o in gap)


def test_a_white_print_border_is_not_mistaken_for_the_frame():
    img = framed()
    img[230:570, 330:570] = (170, 60, 50)                     # old sample art with a 30 px white border inside
    o = offsets(img, quad(300, 200, 300, 400), R=40)
    assert all(abs(x) <= 1.5 for x in o), o                   # the opening is the frame edge, not the art edge


def test_sun_line_is_measured_on_the_wall():
    img = framed(W=1200, H=1000, opening=(500, 250, 240, 320))
    gy, gx = np.mgrid[0:1000, 0:1200].astype("float32")
    shade = (gy - (700 - 0.404 * (gx - 300))) > 0             # light above a line rising 22 deg to the right
    img = np.where(shade[..., None], img * 0.82, img)
    img = cv2.GaussianBlur(img, (0, 0), 3)
    sl = tc.sun_line(img, quad(500, 250, 240, 320))
    assert sl and abs(sl["deg"] - 22) <= 2


def test_roles_find_art_base_overlays_mats_and_old_layers():
    tree = [{"id": 10, "name": "GLARE", "kind": "Group", "visible": True, "children": [
                {"id": 9, "name": "Glass Sheen", "kind": "Pixel", "blend": "Screen", "visible": True}]},
            {"id": 8, "name": "SHADOWS", "kind": "Group", "visible": True, "children": [
                {"id": 7, "name": "Light Shadow", "kind": "Pixel", "blend": "Multiply", "visible": True},
                {"id": 6, "name": "OLD Scene Light (retire)", "kind": "Pixel", "blend": "Multiply", "visible": False}]},
            {"id": 5, "name": "Matte", "kind": "Pixel", "blend": "Normal", "visible": True},
            {"id": 4, "name": "Place Artwork Here", "kind": "Smart Object", "blend": "Normal", "visible": True},
            {"id": 2, "name": "BASE (room photo)", "kind": "Pixel", "blend": "Normal", "visible": True}]
    r = tc.roles(tc.flatten(tree))
    assert r["art"]["id"] == 4 and r["base"]["id"] == 2
    assert [l["id"] for l in r["overlays"]] == [9, 7]          # hidden OLD layer and the mat are not overlays
    assert [l["id"] for l in r["mats"]] == [5]


def test_results_file_round_trip_and_stale_detection(tmp_path):
    p = tmp_path / "checks.json"
    psd = tmp_path / "x.psd"
    psd.write_bytes(b"1234")
    st = psd.stat()
    tc.save({"results": {"a/x.psd": {"status": "FAIL", "psd_size": st.st_size, "psd_mtime": int(st.st_mtime)}}}, p)
    data = tc.load(p)
    assert tc.status_for("a/x.psd", data, psd)["status"] == "FAIL" and not tc.status_for("a/x.psd", data, psd).get("stale")
    psd.write_bytes(b"123456")
    assert tc.status_for("a/x.psd", data, psd)["stale"]


@pytest.mark.skipif(not (shutil.which("photocraft-cli") and WABI.is_file()), reason="needs photocraft-cli + Tony's PSD")
def test_known_pass_wabi_bedroom_hand_verified_2026_11_10():
    """Opening verified by hand in a live PhotoCraft session: 1058, 162, 542 x 740; sun line about 22 deg."""
    before = (WABI.stat().st_size, WABI.stat().st_mtime_ns)
    r = tc.check_psd(WABI, "3x4")
    assert (WABI.stat().st_size, WABI.stat().st_mtime_ns) == before          # read-only
    assert r["status"] == "PASS", r["reasons"]
    x, y, w, h = r["measured"]["opening_box"]
    assert abs(x - 1058) <= 3 and abs(y - 162) <= 4 and abs(w - 542) <= 4 and abs(h - 740) <= 6
    assert abs(r["measured"]["sun"]["deg"] - 22) <= 3
