"""Realism addendum inside Production (tests 8.1.7 + 8.1.8): a pv2 brief sends its reference photograph (recoloured /
mirrored on demand), engines that would edit the reference get the text-only prompt, a free refusal is retried once
text-only, the output scan stops or flags a scene, and Tony's grades are stored with the listing, the template and the
reference. kie.ai, PhotoCraft, SAM, OCR and Gemini are faked (no credits)."""
import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from app import prints, production, references as R, room_slots as rs, scene_templates as stp, slot_planner as splan
from test_prints import approved_idea, env, fake_upscayl  # noqa: F401
from test_references import fake_detector, room
from test_scene_templates import prod, scene  # noqa: F401
from test_slot_planner_realism import SCENE2


def _rec(prod):
    return prints._record(prod["con"], prints.listing_for(prod["con"], prod["iid"])["id"])


def _put_plan(prod, set_plan):
    con = prod["con"]
    lid = prints.listing_for(con, prod["iid"])["id"]
    rec = prints._record(con, lid)
    rec.setdefault("production", {})["set_plan"] = set_plan
    prints._save_record(con, lid, rec)


@pytest.fixture
def board(prod, tmp_path):
    d = Path(prod["S"]["reference_dir"])
    d.mkdir(exist_ok=True)
    room(d / "0901_Test_Room_Dark_Frame.png")
    R.prepare(prod["S"], detector=fake_detector((300, 120, 540, 440)), ocr=lambda png: [], log=lambda *_: None)
    R.update(prod["S"], lambda m: m["refs"]["0901"].update(tags={"display_group": "hung", "shot": "medium",
                                                                 "camera_height": "eye", "lens": "lens_normal",
                                                                 "light_type": "overcast_flat"}))
    return d


def pv2_brief(slot=3, **kw):
    raw = {"pv": 2, "slot": slot, "source": "new", "print_size": "12x16", "shot": "medium", "setting": "over_sofa",
           "display": "hung_over_furniture", "presentation": "frame", "frame_finish": "walnut_frame",
           "camera_side": "left", "camera_height": "eye", "lens": "lens_normal", "light_type": "overcast_flat",
           "light_from": "left", "depth_of_field": "deep_focus",
           "wall": {"name": "warm white", "hex": "#F2EEE6", "treatment": "plaster"}, "floor": "oak",
           "furniture": {"style": "eclectic_mix", "colour": "pine", "family": "light_wood"}, "house": "condo_1970s",
           "buyer": "reader", "props": ["a denim jacket", "a mug", "keys in a bowl", "folded laundry"],
           "scene": SCENE2.replace("bedroom", "living room"), "occupant": "a nurse on night shifts",
           "lived_in": "lived_in", "window": {"covering": "venetian_blind", "view": "street"},
           "photo_style": "phone_snapshot", "reference": "0901"}
    raw.update(kw)
    ctx = {"slot": slot, "room": "Living room", "decor": "Modern", "ratios": list(rs.RATIOS)}
    b = splan.normalise(raw, ctx)
    splan.apply_reference(b, {"camera_side": "left", "tags": {"camera_height": "eye", "lens": "lens_normal",
                                                               "light_type": "overcast_flat"}})
    b["prompt_style"] = "compact"
    b["lint"] = splan.lint(b, ctx)
    assert b["lint"]["pass"], b["lint"]["why"]
    b.update(prompt=splan.assemble(b), rev=1, edited_by="planner", history=[], stale=False, attempts=[])
    return b


def recorder(calls, fail_with_ref=None):
    """A generator stub that records what it got (and the reference's pixels at the art centre / a wall corner)."""
    def gen(engine, out, prompt, aspect, res, ref_imgs=()):
        entry = {"prompt": prompt, "ref_imgs": list(ref_imgs)}
        if ref_imgs:
            a = np.asarray(Image.open(ref_imgs[0]).convert("RGB"))
            entry.update(centre=tuple(int(v) for v in a[280, 420]), mirrored_centre=tuple(int(v) for v in
                                                                                         a[280, a.shape[1] - 1 - 420]))
            if fail_with_ref:
                calls.append(entry)
                raise RuntimeError(fail_with_ref)
        calls.append(entry)
        scene(Path(out))
        return {"out": out, "model": "nano-banana-pro", "credits": 18.0, "left": 700.0}
    return gen


def _run(prod, gen, slot=3):
    production.start_slot(prod["con"], prod["S"], prod["iid"], slot)
    production.run_slot(prod["con"], prod["S"], prod["iid"], slot, None, gen)
    return _rec(prod)["production"]["slots"][str(slot)]


def _tags(prod):
    prod["c"].post(f"/ikigai/api/production/{prod['iid']}/tags", json={"rooms": ["Living room"], "styles": ["Modern"]})


def test_a_pv2_brief_sends_its_reference_and_records_it(prod, board):
    _tags(prod)
    b = pv2_brief()
    _put_plan(prod, {"version": 1, "status": "ready", "briefs": {"3": b}})
    calls = []
    srec = _run(prod, recorder(calls))
    assert srec["state"] == "done", srec.get("message")
    assert len(calls) == 1 and len(calls[0]["ref_imgs"]) == 1 and calls[0]["prompt"] == b["prompt"]
    assert "Image 1 is a photograph of a different room" in calls[0]["prompt"] and "nurse" not in calls[0]["prompt"]
    assert calls[0]["centre"] == splan.MARKER_RGB["orange"]                                   # the blank as is
    man = json.loads(((stp.library(prod["S"]) / srec["template"]).parent / "template.json").read_text())
    assert man["brief"]["reference"] == "0901" and man["brief"]["reference_sent"] is True
    assert man["text_scan"]["pass"] is True
    e = R.load(board)["refs"]["0901"]
    assert e["uses"][-1]["slot"] == 3 and e["uses"][-1]["template"] == srec["template"]
    pan = prod["c"].get(f"/ikigai/api/production/{prod['iid']}/panel").json()
    card = pan["slots"][0]
    assert card["brief"]["reference"] == "0901" and card["brief"]["ref_thumb_url"].endswith("/api/references/0901/blank")
    assert "occupant" not in json.dumps(card) and "nurse" not in json.dumps(card["brief"])
    assert prod["c"].get(card["brief"]["ref_thumb_url"]).status_code == 200


def test_a_blue_brief_gets_a_recoloured_mirrored_reference(prod, board):
    _tags(prod)
    b = pv2_brief(wall={"name": "terracotta", "hex": "#C8643C", "treatment": "plaster"}, frame_finish="black_frame",
                  reference_flip=True)
    assert b["marker"] == "blue"
    _put_plan(prod, {"version": 1, "status": "ready", "briefs": {"3": b}})
    calls = []
    _run(prod, recorder(calls))
    assert calls[0]["mirrored_centre"] == splan.MARKER_RGB["blue"]
    assert sorted(p.name for p in board.iterdir() if p.suffix == ".png") == [
        "0901_Test_Room_Dark_Frame.png", "0901_Test_Room_Dark_Frame_Blank.png"]          # nothing extra stored


def test_an_engine_that_edits_images_gets_the_text_only_prompt(prod, board):
    _tags(prod)
    prod["S"]["room_scene_engine"] = "gpt25"
    b = pv2_brief()
    _put_plan(prod, {"version": 1, "status": "ready", "briefs": {"3": b}})
    calls = []
    srec = _run(prod, recorder(calls))
    assert calls[0]["ref_imgs"] == [] and calls[0]["prompt"] == splan.assemble(b, ref=False)
    assert srec["reference"]["note"] == "reference not sent (engine)"
    man = json.loads(((stp.library(prod["S"]) / srec["template"]).parent / "template.json").read_text())
    assert man["prompt"] == splan.assemble(b, ref=False) and man["brief"]["reference_sent"] is False


def test_a_free_refusal_is_retried_once_text_only(prod, board, monkeypatch):
    _tags(prod)
    monkeypatch.setattr(stp, "kie_balance", lambda settings=None: 500.0)        # the refusal cost nothing
    b = pv2_brief()
    _put_plan(prod, {"version": 1, "status": "ready", "briefs": {"3": b}})
    calls = []
    srec = _run(prod, recorder(calls, fail_with_ref="kie.ai refused the job: flagged as sensitive"))
    assert len(calls) == 2 and calls[0]["ref_imgs"] and calls[1]["ref_imgs"] == []
    assert calls[1]["prompt"] == splan.assemble(b, ref=False) and srec["state"] == "done"
    assert R.load(board)["refs"]["0901"]["kie_refused"] and R.usable(prod["S"]) == []


def test_a_refusal_with_an_unknown_balance_is_not_retried(prod, board):
    _tags(prod)
    _put_plan(prod, {"version": 1, "status": "ready", "briefs": {"3": pv2_brief()}})
    calls = []
    srec = _run(prod, recorder(calls, fail_with_ref="kie.ai could not make it: flagged as sensitive"))
    assert len(calls) == 1 and srec["state"] == "failed" and "no retry" in srec["message"]


def test_a_hard_scan_stops_the_build_and_keeps_the_scene(prod, board, monkeypatch):
    _tags(prod)
    _put_plan(prod, {"version": 1, "status": "ready", "briefs": {"3": pv2_brief()}})
    monkeypatch.setattr(production, "scan_scene", lambda png, settings=None, overlay=None: {
        "pass": False, "severity": "hard", "overlay": None, "mode": "test", "notes": [],
        "findings": [{"severity": "hard", "why": "stray text at the top-left edge"}]})
    calls = []
    srec = _run(prod, recorder(calls))
    assert srec["state"] == "failed" and "stray text at the top-left edge" in srec["message"]
    arch = prod["tmp"] / "Designs" / "00121-Book Club Cat" / "03-Etsy Images" / "Archive"
    assert list(arch.glob("Scene_Stray_Text_03_*.png"))
    att = _rec(prod)["production"]["set_plan"]["briefs"]["3"]["attempts"]
    assert att[-1]["result"] == "stray_text"


def test_a_soft_scan_builds_flags_and_keeps_it_out_of_library_picks(prod, board, monkeypatch):
    _tags(prod)
    _put_plan(prod, {"version": 1, "status": "ready", "briefs": {"3": pv2_brief()}})
    monkeypatch.setattr(production, "scan_scene", lambda png, settings=None, overlay=None: {
        "pass": False, "severity": "soft", "overlay": None, "mode": "test", "notes": [],
        "findings": [{"severity": "soft", "why": "garbled text, centre-right"}]})
    srec = _run(prod, recorder([]))
    assert srec["state"] == "done" and not srec["guard"]["pass"] and "garbled text" in srec["message"]
    pan = prod["c"].get(f"/ikigai/api/production/{prod['iid']}/panel").json()
    assert pan["slots"][0]["image"]["flagged"]
    t = next(x for x in stp.library_templates(prod["S"]) if x["rel"] == srec["template"])
    assert t["manifest"]["text_scan"]["pass"] is False and not stp.auto_pick_ok(t)
    att = _rec(prod)["production"]["set_plan"]["briefs"]["3"]["attempts"]
    assert att[-1]["result"] == "text_flag"


def test_pv1_brief_sends_exactly_its_saved_prompt_and_no_reference(prod, board):
    from test_slot_planner_flow import _brief
    _tags(prod)
    b = _brief(3)
    _put_plan(prod, {"version": 1, "status": "ready", "briefs": {"3": b}})
    calls = []
    srec = _run(prod, recorder(calls))
    assert calls[0] == {"prompt": b["prompt"], "ref_imgs": []} and "reference" not in srec


# ---------- grades (8.1.8) ----------

def test_grade_route_stores_listing_template_and_survives_the_repaint(prod, board):
    _tags(prod)
    _put_plan(prod, {"version": 1, "status": "ready", "briefs": {"3": pv2_brief()}})
    srec = _run(prod, recorder([]))
    name = srec["file"]
    c, iid = prod["c"], prod["iid"]
    p = c.post(f"/ikigai/api/production/{iid}/grade", json={"name": name, "grade": "B-", "note": "too tidy"}).json()
    assert p["slots"][0]["image"]["grade"] == "B-"
    assert c.get(f"/ikigai/api/production/{iid}/panel").json()["slots"][0]["image"]["grade"] == "B-"
    g = _rec(prod)["production"]["grades"][name]
    assert g["grade"] == "B-" and g["slot"] == 3 and g["template"] == srec["template"] and g["reference"] == "0901"
    psd = stp.library(prod["S"]) / srec["template"]
    assert [x["grade"] for x in stp.template_grades(psd)] == ["B-"]
    assert R.load(board)["refs"]["0901"]["grades"][-1]["grade"] == "B-"
    assert c.post(f"/ikigai/api/production/{iid}/grade", json={"name": name, "grade": "Z"}).status_code == 422
    c.post(f"/ikigai/api/production/{iid}/grade", json={"name": name, "grade": None})
    assert name not in _rec(prod)["production"]["grades"] and stp.template_grades(psd) == []


def test_template_grade_writer_whitelists_keys(tmp_path):
    psd = tmp_path / "T.psd"
    stp.add_grade(psd, {"idea_id": 3, "slot": 16, "grade": "C", "note": "n" * 500, "prompt": "secret", "key": "x"})
    g = stp.template_grades(psd)[0]
    assert set(g) <= set(stp.GRADE_KEYS) and len(g["note"]) == 200 and "prompt" not in g
    with pytest.raises(ValueError):
        stp.add_grade(psd, {"grade": "Q"})


def test_chat_grade_needs_tonys_own_grade_word(prod, board):
    from app import prod_chat
    _tags(prod)
    _put_plan(prod, {"version": 1, "status": "ready", "briefs": {"3": pv2_brief()}})
    _run(prod, recorder([]))
    h = prod_chat.ProdHooks(prod["con"], prod["S"], lambda fn, *a: None)
    with pytest.raises(production.ProductionError, match="state yourself"):
        h.run("slot_grade", {"idea_id": prod["iid"], "slot": 3, "grade": "A"}, "this is a nice one", prod["iid"])
    line = h.run("slot_grade", {"idea_id": prod["iid"], "slot": 3, "grade": "C+", "note": "catalog"},
                 "slot 3 is a C+, too catalog", prod["iid"])
    assert "Recorded C+" in line and prod_chat.grade_words("slot 3 is a c+") == {"C+"}
    assert "slot_grade" in __import__("app.assistant", fromlist=["x"]).SYSTEM_PROMPT


def test_templates_graded_below_b_minus_are_not_auto_picked(tmp_path):
    psd = tmp_path / "T.psd"
    t = {"psd": psd, "wired": False, "manifest": {}}
    assert stp.auto_pick_ok(t)
    stp.add_grade(psd, {"idea_id": 3, "slot": 16, "grade": "C"})
    assert not stp.auto_pick_ok(t)
    stp.add_grade(psd, {"idea_id": 4, "slot": 16, "grade": "A"})
    assert stp.auto_pick_ok(t)                                            # mean (2.0 + 4.0) / 2 = 3.0 >= B-


def test_vision_describe_v2_upgrades_a_v1_cache_once(prod, board):
    _tags(prod)
    _run(prod, recorder([]))                                            # slot 3 now has an image: a fixed slot
    name = _rec(prod)["production"]["slots"]["3"]["file"]
    n = []

    def vision(prompt, images=None):
        n.append(prompt)
        return json.dumps({"3": {"prop_families": ["plants", "nonsense"], "light_type": "overcast_flat",
                                 "warm_sun": False, "lived_in": "tidy"}})
    v1 = {name: {"descriptor": {"slot": 3}, "file": name, "from": "measured"}}        # cached before the addendum
    ctx = splan.context(prod["con"], prod["S"], prod["iid"], vision, v1)
    assert len(n) == 1 and "prop_families" in n[0]
    d = ctx["fixed_desc"][3]
    assert d["prop_families"] == ["plants"] and d["light_type"] == "overcast_flat" and d["warm_sun"] is False
    ctx2 = splan.context(prod["con"], prod["S"], prod["iid"], vision, ctx["fixed_cache"])
    assert len(n) == 1 and ctx2["fixed_desc"][3]["light_type"] == "overcast_flat"
