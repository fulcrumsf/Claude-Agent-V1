"""The slot-set planner inside Production (plan tests 11.2, 11.3, 11.4, 11.9 + the panel / route): briefs are stored
in production.set_plan, Generate sends the saved prompt, approved slots and templates are never touched, and without a
usable plan everything is exactly as before. kie.ai, PhotoCraft, SAM and the model are faked (no credits)."""
import hashlib
import json
import random

import pytest

from app import prints, production, room_slots as rs, scene_templates as stp, slot_planner as splan
from test_scene_templates import prod  # noqa: F401  (fixture reuse)
from test_prints import approved_idea, env, fake_upscayl  # noqa: F401
from test_slot_planner import scene_for


def _rec(prod):
    return prints._record(prod["con"], prints.listing_for(prod["con"], prod["iid"])["id"])


def _put_plan(prod, set_plan):
    con = prod["con"]
    lid = prints.listing_for(con, prod["iid"])["id"]
    rec = prints._record(con, lid)
    rec.setdefault("production", {})["set_plan"] = set_plan
    prints._save_record(con, lid, rec)


def _brief(slot, room="Living room", **kw):
    raw = {"slot": slot, "source": "new", "print_size": "12x16", "shot": "medium", "setting": "sideboard_top",
           "display": "lean_on_surface", "presentation": "frame", "frame_finish": "walnut_frame",
           "camera_side": "left", "camera_height": "counter", "lens": "lens_normal", "light_style": "soft_direct",
           "light_from": "left", "shadow": "soft", "depth_of_field": "deep_focus",
           "wall": {"name": "warm white", "hex": "#F2EEE6", "treatment": "limewash"}, "floor": "oak planks",
           "furniture": {"style": "midcentury_teak", "colour": "teak", "family": "mid_wood"}, "house": "london_flat",
           "buyer": "reader", "props": ["a stoneware vase"], "scene": scene_for(slot)}
    raw.update(kw)
    ctx = {"slot": slot, "room": room, "decor": "Modern", "ratios": list(rs.RATIOS)}
    b = splan.normalise(raw, ctx)
    b["lint"] = splan.lint(b, ctx)
    assert b["lint"]["pass"], b["lint"]["why"]
    b.update(prompt=splan.assemble(b), rev=1, edited_by="planner", history=[], stale=False, attempts=[])
    return b


def _hashes(root):
    return {str(p): hashlib.sha1(p.read_bytes()).hexdigest() for p in sorted(root.rglob("template.json"))}


def stub_ask(calls=None):
    """A planner stub: one brief per open slot named in the prompt (valid for its room), else the vision answer."""
    def ask(prompt, images=None):
        if calls is not None:
            calls.append(prompt)
        if "Slots in image order" in prompt:                     # the fixed-slot vision describe
            return "{}"
        data = json.loads(prompt.split("Inputs:\n", 1)[1].split("\n\n", 1)[0])
        out = []
        for i, o in enumerate(data["open_slots"]):
            setting = next(s for s, v in o["settings"].items() if "medium" in v["scales"])
            disp = o["settings"][setting]["displays"][0]
            out.append({"slot": o["slot"], "source": "new", "print_size": ["12x16", "16x20", "A3", "10x15", "12x18",
                                                                          "15x20", "12x15", "11x14"][i % 8],
                        "shot": "medium", "setting": setting, "display": disp, "presentation": "frame",
                        "frame_finish": "walnut_frame", "camera_side": ("left", "right", "front")[i % 3],
                        "camera_height": "eye", "lens": "lens_normal", "light_style": "soft_direct",
                        "light_from": "left", "shadow": "soft", "depth_of_field": "deep_focus",
                        "wall": {"name": "white", "hex": "#F2EEE6", "treatment": "plain_paint"}, "floor": "oak",
                        "furniture": {"style": "modern_minimal", "colour": "oak", "family": "light_wood"},
                        "house": "london_flat", "buyer": "reader", "props": ["a vase"], "scene": scene_for(i)})
        return json.dumps({"briefs": out})
    return ask


# ---------- 11.4 fallback: no usable plan = exactly today's random look ----------

@pytest.mark.parametrize("plan", [None, {"status": "failed", "briefs": {}}])
def test_without_a_usable_plan_generate_sends_the_random_look_prompt(prod, monkeypatch, plan):
    c, iid = prod["c"], prod["iid"]
    c.post(f"/ikigai/api/production/{iid}/tags", json={"rooms": ["Living room"], "styles": ["Mid Century"]})
    if plan is not None:
        _put_plan(prod, plan)
    real = rs.pick_look
    monkeypatch.setattr(rs, "pick_look", lambda room, decor, seed=None, override=None, version=None:
                        real(room, decor, seed=4242 if seed is None else seed, override=override, version=version))
    p = c.get(f"/ikigai/api/production/{iid}/panel").json()
    assert p["slots"][0]["random_look"] and p["set_plan"]["status"] in ("none", "failed")
    c.post(f"/ikigai/api/production/{iid}/slots/3/generate", json={})
    card = p["slots"][0]
    want = rs.scene_prompt("Living room", card["decor"], card["ratio"], look=real("Living room", card["decor"], seed=4242))
    assert prod["gen"][0]["prompt"] == want
    srec = _rec(prod)["production"]["slots"]["3"]
    assert "brief_rev" not in srec
    man = json.loads(((stp.library(prod["S"]) / srec["template"]).parent / "template.json").read_text())
    assert man["look"]["seed"] == 4242 and "brief" not in man and "marker" not in man


# ---------- 11.9 run_slot with a brief ----------

def test_generate_with_a_new_brief_sends_its_prompt_and_saves_the_brief(prod, monkeypatch):
    c, iid = prod["c"], prod["iid"]
    c.post(f"/ikigai/api/production/{iid}/tags", json={"rooms": ["Living room"], "styles": ["Mid Century"]})
    b = _brief(3, print_size="12x16")                      # 3x4 (the card's own plan said something else)
    _put_plan(prod, {"version": 1, "status": "ready", "briefs": {"3": b}})
    seen = {}
    real_build = stp.build_psd

    def spy(scene, ratio, work, settings=None, **kw):
        seen.update(ratio=ratio, **kw)
        return real_build(scene, ratio, work, settings, **kw)
    monkeypatch.setattr(stp, "build_psd", spy)
    p = c.get(f"/ikigai/api/production/{iid}/panel").json()
    card = p["slots"][0]
    assert card["brief"]["facts"] == "12x16 · medium · sideboard top · 3x4" and card["brief"]["usable"]
    assert card["ratio"] == "3x4" and not card["random_look"] and card["next"]["kind"] == "new"
    q0 = p["queue"][0]          # controls addendum F: rows also carry engine, reference mode and the upper bound
    assert {k: q0[k] for k in ("slot", "source", "credits", "planned")} == {"slot": 3, "source": "new", "credits": 18,
                                                                          "planned": True}
    assert q0["engine"] == "nano-banana-pro" and q0["upper"] == 18 and q0["gate"] == "trusted"
    c.post(f"/ikigai/api/production/{iid}/slots/3/generate", json={})
    assert prod["gen"][0]["prompt"] == b["prompt"]
    assert seen["ratio"] == "3x4" and seen["presentation"] == "frame" and "marker" not in seen   # orange: old call
    rec = _rec(prod)
    srec = rec["production"]["slots"]["3"]
    assert srec["brief_rev"] == 1 and srec["brief_source"] == "new" and srec["ratio"] == "3x4"
    man = json.loads(((stp.library(prod["S"]) / srec["template"]).parent / "template.json").read_text())
    assert "look" not in man and man["brief"]["print_size"] == "12x16" and man["prompt"] == b["prompt"]
    assert "/003_Ratio_3x4/" in "/" + srec["template"]
    att = rec["production"]["set_plan"]["briefs"]["3"]["attempts"]
    assert len(att) == 1 and att[0]["result"] in ("built", "gate_fail") and att[0]["rev"] == 1
    # a later run keeps brief_rev on the replaced slot record (the record is rebuilt from `out`)
    c.post(f"/ikigai/api/production/{iid}/slots/3/generate", json={})
    assert _rec(prod)["production"]["slots"]["3"]["brief_rev"] == 1


def test_a_warm_wall_brief_builds_with_the_blue_marker(prod, monkeypatch):
    c, iid = prod["c"], prod["iid"]
    c.post(f"/ikigai/api/production/{iid}/tags", json={"rooms": ["Living room"], "styles": ["Mid Century"]})
    b = _brief(3, wall={"name": "terracotta", "hex": "#C8643C", "treatment": "plaster"}, frame_finish="black_frame")
    assert b["marker"] == "blue" and "pale sky blue" in b["prompt"]
    _put_plan(prod, {"version": 1, "status": "ready", "briefs": {"3": b}})
    seen = {}
    real_build = stp.build_psd
    monkeypatch.setattr(stp, "build_psd", lambda scene, ratio, work, settings=None, **kw:
                        seen.update(kw) or real_build(scene, ratio, work, settings, **kw))
    c.post(f"/ikigai/api/production/{iid}/slots/3/generate", json={})
    assert seen.get("marker") == "blue"
    srec = _rec(prod)["production"]["slots"]["3"]
    man = json.loads(((stp.library(prod["S"]) / srec["template"]).parent / "template.json").read_text())
    assert man["marker"] == "blue"


def test_stale_or_lint_failed_brief_is_not_used(prod):
    c, iid = prod["c"], prod["iid"]
    c.post(f"/ikigai/api/production/{iid}/tags", json={"rooms": ["Living room"], "styles": ["Mid Century"]})
    b = _brief(3)
    _put_plan(prod, {"version": 1, "status": "ready", "briefs": {"3": dict(b, stale=True)}})
    p = c.get(f"/ikigai/api/production/{iid}/panel").json()
    assert p["slots"][0]["random_look"] and p["slots"][0]["brief"]["stale"] and not p["slots"][0]["brief"]["usable"]
    _put_plan(prod, {"version": 1, "status": "ready", "briefs": {"3": dict(b, lint={"pass": False, "why": ["x"]})}})
    assert c.get(f"/ikigai/api/production/{iid}/panel").json()["slots"][0]["random_look"]


def test_library_brief_picks_its_template_and_new_brief_skips_old_matches():
    lib = [{"rel": f"002_Ratio_2x3/001_Living_Rooms/002_Modern/T{i}/T{i}.psd", "name": f"T{i}", "ratio": "2x3",
            "room": "Living Rooms", "style": "Modern", "desc": "", "wired": False, "manifest": None} for i in (1, 2)]
    plan = [{"slot": s, "room": "Living room", "decor": "Modern", "ratio": "2x3"} for s in (8, 9, 10)]
    briefs = {8: {"source": "new"}, 10: {"source": "library", "library_rel": lib[0]["rel"]}}
    picks = production.library_picks(plan, {}, lib, frozenset(), briefs)
    assert picks[8] is None and picks[10]["name"] == "T1" and picks[9]["name"] == "T2"
    assert production.library_picks(plan, {}, lib) == production.library_picks(plan, {}, lib, frozenset(), {})


# ---------- 11.2 / 11.3: the planner never touches approved slots or templates ----------

def test_planner_run_leaves_approved_slots_and_every_template_json_alone(prod):
    c, iid = prod["c"], prod["iid"]
    c.post(f"/ikigai/api/production/{iid}/tags", json={"rooms": ["Living room"], "styles": ["Mid Century"]})
    p = c.post(f"/ikigai/api/production/{iid}/slots/3/generate", json={}).json()
    name = p["slots"][0]["image"]["file"]
    c.post(f"/ikigai/api/production/{iid}/images/{name}", json={"decision": "approved"})
    folder = prod["tmp"] / "Designs" / "00121-Book Club Cat" / "03-Etsy Images"
    before_slot = json.loads(json.dumps(_rec(prod)["production"]["slots"]["3"]))
    mtime = (folder / name).stat().st_mtime_ns
    tj = _hashes(prod["root"])
    calls = []
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from app import studio
    app = FastAPI()
    studio.mount(app, prod["con"], prod["S"], None, ask=lambda p_, s=None: "", spawn=lambda fn, *a: fn(*a),
                 upscayl=fake_upscayl([]), planner_ask=stub_ask(calls))
    c2 = TestClient(app)
    pan = c2.post(f"/ikigai/api/production/{iid}/plan", json={}).json()
    sp = _rec(prod)["production"]["set_plan"]
    assert calls and sp["status"] in ("ready", "needs_attention"), sp.get("message")
    assert "3" not in sp["briefs"] and sp["briefs"]                                # approved slot 3: no brief
    assert _rec(prod)["production"]["slots"]["3"] == before_slot                  # deep-equal
    assert (folder / name).stat().st_mtime_ns == mtime
    assert _hashes(prod["root"]) == tj                                             # no template.json touched
    assert pan["set_plan"]["status"] == sp["status"] and pan["set_plan"]["cost"]["credits_per_scene"] == 18
    cards = {x["slot"]: x for x in pan["slots"]}
    assert cards[9]["brief"]["prompt"] and "Show" not in cards[9]["brief"]["prompt"]
    assert prod["gen"] == [] or len(prod["gen"]) == 1                              # planning never generates


def test_auto_plans_once_and_marks_briefs_stale_when_tags_change(prod):
    iid = prod["iid"]
    S = dict(prod["S"], planner_auto=True)
    calls = []
    ran = []
    spawn = lambda fn, *a: ran.append(fn) or fn(*a)        # noqa: E731
    assert splan.auto(prod["con"], S, iid, spawn, stub_ask(calls))
    n = len(calls)
    assert not splan.auto(prod["con"], S, iid, spawn, stub_ask(calls)) and len(calls) == n   # nothing changed
    production.save_tags(prod["con"], S, iid, ["Bedroom"], ["Mid Century"])
    sp_before = _rec(prod)["production"]["set_plan"]
    assert splan.auto(prod["con"], S, iid, spawn, stub_ask(calls)) and len(calls) > n
    sp = _rec(prod)["production"]["set_plan"]
    assert sp["inputs_key"] != sp_before["inputs_key"] and not any(b.get("stale") for b in sp["briefs"].values())
    assert any(b["rev"] >= 2 for b in sp["briefs"].values())


def test_a_failed_plan_is_not_retried_by_itself(prod):
    from app.assistant import ChatUnavailable
    iid = prod["iid"]
    S = dict(prod["S"], planner_auto=True)
    n = []

    def down(prompt, images=None):
        n.append(1)
        raise ChatUnavailable("down")
    spawn = lambda fn, *a: fn(*a)                           # noqa: E731
    splan.auto(prod["con"], S, iid, spawn, down)
    assert _rec(prod)["production"]["set_plan"]["status"] == "failed"
    k = len(n)
    assert not splan.auto(prod["con"], S, iid, spawn, down) and len(n) == k


def test_recover_marks_a_planning_left_by_a_restart_failed(prod):
    _put_plan(prod, {"status": "planning", "briefs": {}})
    splan.recover(prod["con"])
    assert _rec(prod)["production"]["set_plan"]["status"] == "failed"


# ---------- 11.10 Studio chat: edit a slot's prompt before credits ----------

def _hooks(prod):
    from app import prod_chat
    return prod_chat.ProdHooks(prod["con"], prod["S"], lambda fn, *a: None)


def test_chat_edit_refusals_success_history_and_revert(prod):
    from app import prod_chat
    c, iid = prod["c"], prod["iid"]
    c.post(f"/ikigai/api/production/{iid}/tags", json={"rooms": ["Living room"], "styles": ["Mid Century"]})
    p = c.post(f"/ikigai/api/production/{iid}/slots/3/generate", json={}).json()
    c.post(f"/ikigai/api/production/{iid}/images/{p['slots'][0]['image']['file']}", json={"decision": "approved"})
    b9 = _brief(9)
    _put_plan(prod, {"version": 1, "status": "ready", "briefs": {"3": _brief(3), "9": b9}, "fixed": {}})
    h = _hooks(prod)
    with pytest.raises(production.ProductionError, match="approved image"):
        h.run("slot_prompt_edit", {"idea_id": iid, "slot": 3, "fields": {"shot": "wide"}}, "x", iid)
    with pytest.raises(production.ProductionError, match="not changed"):
        h.run("slot_prompt_edit", {"idea_id": iid, "slot": 9, "fields": {"print_size": "24x36"}}, "x", iid)
    line = h.run("slot_prompt_edit", {"idea_id": iid, "slot": 9, "scene": scene_for(30),
                                      "fields": {"wall": {"name": "terracotta", "hex": "#C8643C"},
                                                 "frame_finish": "black_frame"}}, "make it terracotta", iid)
    assert "updated" in line and "rev 2" in line
    b = _rec(prod)["production"]["set_plan"]["briefs"]["9"]
    assert b["rev"] == 2 and b["edited_by"] == "chat" and b["marker"] == "blue" and "pale sky blue" in b["prompt"]
    assert b["scene"] == scene_for(30) and b["history"][-1]["rev"] == 1 and b["history"][-1]["brief"]["scene"] == b9["scene"]
    snap = "\n".join(prod_chat.snapshot_lines(prod["con"], prod["S"], iid, open_slot=9))
    assert "slot 09: 12x16 · medium" in snap and "edited in chat" in snap and scene_for(30)[:40] in snap
    line = h.run("slot_prompt_revert", {"idea_id": iid, "slot": 9}, "undo that", iid)
    b = _rec(prod)["production"]["set_plan"]["briefs"]["9"]
    assert "back to its earlier scene" in line and b["scene"] == b9["scene"] and b["prompt"] == b9["prompt"]
    assert b["rev"] == 3 and b["reverted_to"] == 1
    pan = c.get(f"/ikigai/api/production/{iid}/panel").json()
    card9 = next(x for x in pan["slots"] if x["slot"] == 9)
    assert card9["brief"]["edited_by"] == "chat" and card9["brief"]["prompt"] == b9["prompt"]


def test_chat_actions_are_known_to_the_assistant():
    from app import assistant
    assert "slot_prompt_edit" in assistant.ACTIONS and "slot_prompt_revert" in assistant.ACTIONS
    assert "slot_prompt_edit {idea_id, slot, scene?, fields?}" in assistant.SYSTEM_PROMPT
    assert "never explain why" in assistant.SYSTEM_PROMPT
