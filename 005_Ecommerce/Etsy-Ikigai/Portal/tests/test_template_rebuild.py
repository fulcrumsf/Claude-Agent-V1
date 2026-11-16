"""Tony 2026-11-15 decisions: rebuilt templates wait for his Approve and are never used by Production until then;
SAM's paper edge may run up to 3 px onto the frame lip; the sun-line guard (sun lines only on SAM's wall mask, no
light shadow over a print); the wainscoting placement check; the wainscoting line in the scene prompt."""
import json
from pathlib import Path

import cv2
import numpy as np
import pytest

from app import production, room_slots as rs, sam_frames as sf, scene_templates as stp, template_build as tb
from app import template_checker as tc, template_gallery as tg


# ---------- pending rebuilds: shown for approval, never used by Production ----------

@pytest.fixture
def S(tmp_path):
    root = tmp_path / "Room_Templates"
    folder = root / "Portrait_Templates" / "002_Ratio_2x3" / "001_Living_Rooms" / "002_Modern" / "LVRM_Test"
    folder.mkdir(parents=True)
    (folder / "LVRM_Test.psd").write_bytes(b"old")
    (folder / "LVRM_Test_Preview.png").write_bytes(b"old preview")
    (folder / "template.json").write_text(json.dumps({"name": "LVRM_Test", "kind": "tony_psd", "psd": "LVRM_Test.psd",
                                                      "so_px": [400, 600], "quad_art": [[0, 0], [1, 0], [1, 1], [0, 1]]}))
    new = "LVRM_Test_Rebuild_2026-11-15"
    (folder / f"{new}.psd").write_bytes(b"new")
    (folder / f"{new}_Scene.png").write_bytes(b"scene")
    (folder / f"{new}.json").write_text(json.dumps({
        "name": new, "kind": "rebuild", "psd": f"{new}.psd", "scene": f"{new}_Scene.png", "replaces": "LVRM_Test.psd",
        "so_px": [398, 597], "quad_art": [[0, 0], [2, 0], [2, 2], [0, 2]], "approved": False}))
    styles = tmp_path / "styles.json"
    styles.write_text(json.dumps({"vocabulary": [{"label": "Minimalism", "section": "Art Prints - Minimalism"}],
                                  "manual": {"002_Ratio_2x3/001_Living_Rooms/002_Modern/LVRM_Test/LVRM_Test.psd":
                                             ["Minimalism"]}, "auto": {}}))
    return {"room_templates_dir": str(root), "gallery_cache": str(tmp_path / "cache"),
            "template_checks_path": str(tmp_path / "checks.json"), "template_styles_path": str(styles)}, folder


REL_OLD = "002_Ratio_2x3/001_Living_Rooms/002_Modern/LVRM_Test/LVRM_Test.psd"
REL_NEW = "002_Ratio_2x3/001_Living_Rooms/002_Modern/LVRM_Test/LVRM_Test_Rebuild_2026-11-15.psd"


def test_a_pending_rebuild_is_listed_for_approval_but_never_in_productions_library(S):
    s, folder = S
    ts = {t["rel"]: t for t in tg.scan(s)[0]}
    assert ts[REL_NEW]["pending"] is True and ts[REL_OLD]["pending"] is False
    assert ts[REL_NEW]["so_px"] == "398x597"                   # its own manifest, not the old PSD's
    lib = stp.library_templates(s)
    assert [t["rel"] for t in lib] == [REL_OLD]                # the live PSD stays in use, the rebuild never
    assert stp.load_manifest(folder / "LVRM_Test_Rebuild_2026-11-15.psd")["kind"] == "rebuild"
    assert stp.load_manifest(folder / "LVRM_Test.psd")["kind"] == "tony_psd"
    plan = [{"slot": 9, "room": "Living room", "decor": "Modern", "ratio": "2x3"},
            {"slot": 10, "room": "Living room", "decor": "Modern", "ratio": "2x3"}]
    picks = production.library_picks(plan, {}, lib)
    assert picks[9]["rel"] == REL_OLD and picks[10] is None    # never the pending one, not even as a second pick
    items = {i["rel"]: i for i in tg.overview(s, build=False, auto=False)["items"]}
    assert items[REL_NEW]["awaiting"] and items[REL_NEW]["rebuild_of"] == "LVRM_Test.psd"
    assert not items[REL_OLD]["awaiting"]


def test_a_gap_build_waiting_for_approval_is_not_used_either(tmp_path):
    root = tmp_path / "Room_Templates"
    d = root / "Portrait_Templates" / "002_Ratio_2x3" / "001_Living_Rooms" / "002_Modern"
    d.mkdir(parents=True)
    (d / "AI_Living_Room_Modern_1_Template.psd").write_bytes(b"x")
    (d / "template.json").write_text(json.dumps({"kind": "ai_scene", "psd": "AI_Living_Room_Modern_1_Template.psd",
                                                 "approved": False}))
    s = {"room_templates_dir": str(root)}
    assert [t["pending"] for t in tg.scan(s)[0]] == [True] and stp.library_templates(s) == []
    (d / "template.json").write_text(json.dumps({"kind": "ai_scene", "psd": "AI_Living_Room_Modern_1_Template.psd",
                                                 "approved": True}))
    assert len(stp.library_templates(s)) == 1


def test_approve_archives_the_old_version_and_the_rebuild_takes_over(S):
    s, folder = S
    out = tb.decide(REL_NEW, "approved", s)
    arch = folder / "Archive"
    names = sorted(p.name for p in arch.iterdir())
    assert any(n.startswith("LVRM_Test_before_rebuild_") and n.endswith(".psd") for n in names)
    assert any(n.startswith("LVRM_Test_template_before_rebuild_") for n in names)
    assert any(n.startswith("LVRM_Test_Preview_before_rebuild_") for n in names)
    assert not (folder / "LVRM_Test.psd").exists() and (folder / "LVRM_Test_Rebuild_2026-11-15.psd").read_bytes() == b"new"
    man = json.loads((folder / "template.json").read_text())
    assert man["approved"] is True and man["psd"] == "LVRM_Test_Rebuild_2026-11-15.psd"
    assert not (folder / "LVRM_Test_Rebuild_2026-11-15.json").exists()      # the sidecar became template.json
    lib = stp.library_templates(s)
    assert [t["rel"] for t in lib] == [REL_NEW] and lib[0]["manifest"]["so_px"] == [398, 597]
    st = json.loads(Path(s["template_styles_path"]).read_text())
    assert st["manual"][REL_NEW] == ["Minimalism"]                          # Tony's style choice follows it
    assert out["approved"] == REL_NEW
    assert sum(1 for p in folder.rglob("*") if p.is_file()) == 7               # nothing deleted (6 files + styles moved)


def test_deny_moves_the_rebuild_to_archive_and_keeps_the_old_one_live(S):
    s, folder = S
    tb.decide(REL_NEW, "denied", s)
    assert (folder / "LVRM_Test.psd").read_bytes() == b"old" and (folder / "template.json").is_file()
    names = sorted(p.name for p in (folder / "Archive").iterdir())
    assert names == ["LVRM_Test_Rebuild_2026-11-15.json", "LVRM_Test_Rebuild_2026-11-15.psd",
                     "LVRM_Test_Rebuild_2026-11-15_Scene.png"]
    assert [t["rel"] for t in tg.scan(s)[0]] == [REL_OLD]


# ---------- SAM's paper edge may run up to 3 px onto the frame lip ----------

def test_opening_accepts_sam_up_to_3px_over_the_lip_and_refuses_more():
    from test_sam_frames import Q, render_wall_frame
    rgb = render_wall_frame(strip=0.0)
    qo, info = sf.opening_quad(rgb, sf.offset_quad(Q, [2.5, 0, 0, 0]))   # SAM ran 2.5 px onto the top lip
    assert sf.corner_error(qo, Q)["max_px"] <= 0.4, info
    assert info["offset_px"]["top"] == pytest.approx(-2.5, abs=0.4)
    assert sf.OPENING_INSIDE_MAX_PX == 3.0


# ---------- sun-line guard ----------

def _paper_scene(print_in_frame=False, sun=True):
    W, H = 1000, 900
    img = np.full((H, W, 3), 0.80, "float32")
    gy, gx = np.mgrid[0:H, 0:W].astype("float32")
    if sun:                                                    # a hard diagonal light/shade edge on the wall
        img[(gy - (650 - 0.4 * (gx - 200))) > 0] *= 0.7
    q = np.float32([[400, 200], [640, 200], [640, 560], [400, 560]])
    m = sf.poly_coverage(q, W, H) > 0.5
    img[m] = (0.95 - 0.0002 * gx[m])[:, None]                  # blank paper, a soft light falloff
    if print_in_frame:
        rng = np.random.default_rng(1)
        img[m] = rng.uniform(0.2, 0.9, (int(m.sum()), 1))
    return img, q


def test_without_sams_wall_mask_a_sun_line_is_never_trusted():
    img, q = _paper_scene()
    alpha, meta = stp.key_light(img, q, wall=None)
    assert meta["kind"] != "sun line" and "no SAM wall mask" in meta.get("sun_line", "")


def test_with_the_wall_mask_the_measured_sun_line_is_used():
    img, q = _paper_scene()
    wall = np.ones(img.shape[:2], "float32")
    alpha, meta = stp.key_light(img, q, wall=wall)
    assert meta["kind"] == "sun line" and abs(meta["deg"] - 22) <= 3


def test_no_light_shadow_over_a_print():
    img, q = _paper_scene(print_in_frame=True)
    for wall in (None, np.ones(img.shape[:2], "float32")):
        alpha, meta = stp.key_light(img, q, wall=wall)
        assert meta["kind"] == "none" and alpha.max() == 0 and meta["insert_texture"] > stp.INSERT_TEXTURE_MAX


# ---------- placement: wainscoting / wall molding ----------

def _room(lines=(), W=1400, H=1200, frame=(560, 300, 840, 700)):
    img = np.full((H, W, 3), 205, "uint8")
    for kind, pos, a, b in lines:                               # raised molding: a dark line with a light edge
        if kind == "v":
            cv2.line(img, (pos, a), (pos, b), (150, 150, 150), 3)
            cv2.line(img, (pos + 3, a), (pos + 3, b), (235, 235, 235), 2)
        else:
            cv2.line(img, (a, pos), (b, pos), (150, 150, 150), 3)
            cv2.line(img, (a, pos + 3), (b, pos + 3), (235, 235, 235), 2)
    x0, y0, x1, y1 = frame
    cv2.rectangle(img, (x0 - 30, y0 - 30), (x1 + 30, y1 + 30), (60, 40, 25), -1)    # the frame
    cv2.rectangle(img, (x0, y0), (x1, y1), (240, 240, 236), -1)                     # the art / insert
    V = np.float32([[x0, y0], [x1, y0], [x1, y1], [x0, y1]])
    return img, V


def test_no_molding_passes():
    img, V = _room()
    assert tc.placement(img, V)["flag"] == []


def test_a_frame_over_molding_fails():
    # a panel border runs from above the frame to below it, right through the frame
    img, V = _room([("v", 700, 60, 850)])
    r = tc.placement(img, V)
    assert r["covered"] and "molding" in r["flag"][0]


def test_a_frame_off_centre_in_its_panel_fails_and_centred_passes():
    panel = [("v", 420, 150, 860), ("v", 980, 150, 860), ("h", 150, 420, 980), ("h", 860, 420, 980)]
    img, V = _room(panel, frame=(490, 300, 770, 700))          # 37 px from the left border, 177 from the right
    assert any("off-centre" in f for f in tc.placement(img, V)["flag"])
    img, V = _room(panel)                                      # centred in the 420-980 panel
    r = tc.placement(img, V)
    assert r["panel"] and r["flag"] == [], r


def test_floor_iso_flag_is_accepted_by_tony():
    assert "LVRM_Floor_ISO" in tc.PLACEMENT_OK


# ---------- scene prompt ----------

def test_scene_prompt_carries_the_wainscoting_rule():
    p = rs.scene_prompt("Living room", "Modern", "2x3")
    assert "wainscoting only if the room style calls for it" in p and "centred inside one panel" in p
    assert "never touches or overlaps any molding" in p


def test_a_smooth_falloff_has_no_light_edge_but_a_sun_band_does():
    H, W = 400, 300
    gy, gx = np.mgrid[0:H, 0:W].astype("float32")
    inside = np.zeros((H, W), bool)
    inside[20:380, 20:280] = True
    ramp = np.clip((gx + 2 * gy) / 900.0, 0, 1)                 # a steep but smooth light falloff (clipped plane)
    assert tc.is_falloff(ramp, inside) and tc.overlay_edge(ramp, inside) is None
    band = cv2.GaussianBlur(((gy - 0.5 * gx) > 150).astype("float32"), (0, 0), 2) * 0.3
    assert not tc.is_falloff(band, inside)
