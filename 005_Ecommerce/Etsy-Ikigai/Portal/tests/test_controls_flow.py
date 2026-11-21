"""Controls addendum inside Production (tests E.5, F.4, G, C.5): live prefs, the room engine per slot, the per-engine
room check, Generate all with its estimate / key / cap / stops / cancel, and the A/B variants on the batch runner.
kie.ai, fal, WaveSpeed, PhotoCraft, SAM, OCR and the model are faked: nothing spends a credit."""
import json
from pathlib import Path

import pytest

from app import engines, prefs, prints, production, scene_templates as stp, slot_planner as splan
from test_prints import approved_idea, env, fake_upscayl  # noqa: F401
from test_scene_templates import prod, scene  # noqa: F401
from test_realism_flow import board, pv2_brief  # noqa: F401
from test_slot_planner_flow import _brief, _put_plan, _rec


def _tags(prod):
    prod["c"].post(f"/ikigai/api/production/{prod['iid']}/tags",
                   json={"rooms": ["Living room"], "styles": ["Mid Century"]})


def _plan(prod, slots=(3, 9, 10, 12)):
    _put_plan(prod, {"version": 1, "status": "ready", "briefs": {str(s): _brief(s) for s in slots}})


def _panel(prod):
    return prod["c"].get(f"/ikigai/api/production/{prod['iid']}/panel").json()


# ---------- G: prefs ----------

def test_prefs_default_from_settings_saved_validated_and_on_the_panel(prod):
    c, con, S = prod["c"], prod["con"], prod["S"]
    _tags(prod)
    assert prefs.all_prefs(con, S) == {"reference_share": 80, "reference_closeness": 60, "scene_engine": "nbpro",
                                       "generate_all_cap": 120}
    assert c.post("/ikigai/api/prefs", json={"key": "reference_share", "value": 70}).json()["reference_share"] == 70
    assert c.post("/ikigai/api/prefs", json={"key": "reference_share", "value": 75}).status_code == 422   # step 10
    assert c.post("/ikigai/api/prefs", json={"key": "reference_closeness", "value": 101}).status_code == 422
    assert c.post("/ikigai/api/prefs", json={"key": "scene_engine", "value": "no-such"}).status_code == 422
    assert c.post("/ikigai/api/prefs", json={"key": "scene_engine", "value": "nbpro"}).json()["scene_engine"] == \
        "nano-banana-pro"
    p = _panel(prod)
    assert p["prefs"]["reference_share"] == 70 and p["engine"]["engine_id"] == "nano-banana-pro"
    assert [e["label"] for e in p["room_engines"]][:2] == ["GPT Image 2.6", "Ideogram 3"]
    assert "settings.json" not in json.dumps(p)


# ---------- E: room engine per slot ----------

def test_engine_resolution_order_and_nbpro_is_the_same_call(prod):
    con, S, iid = prod["con"], prod["S"], prod["iid"]
    _tags(prod)
    rec = _rec(prod)
    assert production.slot_engine(con, S, rec, 3)["engine_id"] == "nano-banana-pro"           # the setting
    prefs.put(con, "scene_engine", "ideogram-3")
    assert production.slot_engine(con, S, rec, 3)["engine_id"] == "ideogram-3"                # panel default
    production.set_slot_engine(con, S, iid, 3, "flux-3")
    assert production.slot_engine(con, S, _rec(prod), 3)["engine_id"] == "flux-3"            # card pick wins
    production.set_slot_engine(con, S, iid, 3, None)
    prefs.put(con, "scene_engine", "nano-banana-pro")
    _plan(prod, (3,))
    production.start_slot(con, S, iid, 3)
    production.run_slot(con, S, iid, 3, None, prod["c"].app and None or _gen(prod))
    assert prod["gen"][-1]["engine"] == "nbpro"                                                # today's call
    srec = _rec(prod)["production"]["slots"]["3"]
    man = json.loads(((stp.library(S) / srec["template"]).parent / "template.json").read_text())
    assert man["engine"] == "nbpro" and man["engine_id"] == "nano-banana-pro" and man["engine_provider"] == "kie"
    assert man["cost_measured"] is True and srec["engine_id"] == "nano-banana-pro"


def _gen(prod, model="nano-banana-pro"):
    calls = prod["gen"]

    def gen(engine, out, prompt, aspect, res, ref_imgs=()):
        calls.append({"engine": engine, "prompt": prompt, "aspect": aspect, "res": res, "ref_imgs": list(ref_imgs)})
        scene(Path(out))
        return {"out": out, "model": model, "credits": 10.0 if engine != "nbpro" else 18.0, "left": 700.0}
    return gen


def test_a_text_only_engine_gets_no_reference_and_is_upscaled_and_checked(prod, monkeypatch):
    con, S, iid = prod["con"], prod["S"], prod["iid"]
    _tags(prod)
    _plan(prod, (3,))
    production.set_slot_engine(con, S, iid, 3, "ideogram-3")
    up = []
    monkeypatch.setattr(stp, "upscale_scene", lambda png, settings=None, min_width=2000: up.append(min_width) or False)
    monkeypatch.setattr(production, "engine_scene_check", lambda *a: {"pass": True, "why": ""})
    production.start_slot(con, S, iid, 3)
    res = production.run_slot(con, S, iid, 3, None, _gen(prod, "ideogram/v3-text-to-image"))
    assert res["kind"] == "done" and prod["gen"][-1]["engine"] == "ideogram-3" and prod["gen"][-1]["ref_imgs"] == []
    assert up == [2000] and engines.room_gate("ideogram-3") == "passed_1"
    srec = _rec(prod)["production"]["slots"]["3"]
    man = json.loads(((stp.library(S) / srec["template"]).parent / "template.json").read_text())
    assert man["engine"] == "ideogram-3" and man["engine_id"] == "ideogram-3"


def test_a_failed_engine_check_flags_the_card_and_offers_nano(prod, monkeypatch):
    con, S, iid = prod["con"], prod["S"], prod["iid"]
    _tags(prod)
    _plan(prod, (3,))
    production.set_slot_engine(con, S, iid, 3, "flux-3")
    monkeypatch.setattr(stp, "upscale_scene", lambda *a, **k: False)
    monkeypatch.setattr(production, "engine_scene_check",
                        lambda *a: {"pass": False, "why": "the blank insert is not flat (painted or textured)"})
    production.start_slot(con, S, iid, 3)
    res = production.run_slot(con, S, iid, 3, None, _gen(prod))
    assert res["kind"] == "flagged" and engines.room_gate("flux-3") == "suspect"
    card = next(c for c in _panel(prod)["slots"] if c["slot"] == 3)
    assert card["image"]["flagged"] and card["engine_fail"]["label"] == "Flux 3"
    r = prod["c"].post(f"/ikigai/api/production/{iid}/slots/3/generate", json={"engine": "nano-banana-pro"})
    assert r.status_code == 200 and prod["gen"][-1]["engine"] == "nbpro"


def test_the_nbpro_generate_scene_path_is_byte_identical_with_the_engine_pref(prod, tmp_path):
    calls = []

    def gen(*a, **kw):
        calls.append((a, kw))
        return {"out": a[1]}
    stp.generate_scene("p", tmp_path / "s.png", {"room_scene_engine": "nbpro"}, gen, engine="nano-banana-pro")
    assert calls[0] == (("nbpro", str(tmp_path / "s.png"), "p", "4:3", "2K"), {})


def test_a_non_kie_engine_goes_through_the_adapter(tmp_path, monkeypatch):
    seen = {}

    class A:
        def generate(self, prompt, out, aspect, res, refs=()):
            seen.update(aspect=aspect, res=res, refs=list(refs))
            Path(out).write_bytes(b"x")
            return {"path": Path(out), "model": "m", "task_id": "t", "credits": 7.0, "usd": 0.035, "provider": "fal"}
    monkeypatch.setattr(engines, "adapter_for", lambda eid, settings=None, use="art", with_refs=False: A())
    r = stp.generate_scene("p", tmp_path / "s.png", {"room_scene_engine": "nbpro"}, None, engine="recraft-4-1")
    assert seen == {"aspect": "4:3", "res": "2K", "refs": []}
    assert r["usd"] == 0.035 and r["provider"] == "fal" and r["out"] == str(tmp_path / "s.png")


# ---------- F: Generate all ----------

def test_estimate_rows_order_totals_and_skips(prod):
    con, S, iid = prod["con"], prod["S"], prod["iid"]
    _tags(prod)
    _plan(prod)
    production.set_slot_engine(con, S, iid, 10, "flux-3")             # untested engine: skipped
    production.set_slot_engine(con, S, iid, 12, "gpt-image-2-6")
    engines.update_status(lambda st: st.setdefault("gpt-image-2-6", {}).setdefault("room", {}).update(gate="trusted"))
    est = prod["c"].get(f"/ikigai/api/production/{iid}/generate-all").json()
    rows = {r["slot"]: r for r in est["rows"]}
    assert [r["slot"] for r in est["rows"]][:4] == [3, 9, 10, 11]
    assert rows[3]["status"] == rows[9]["status"] == "waiting" and rows[3]["upper"] == 18
    assert rows[10]["status"] == "skipped" and "room check" in rows[10]["why"]
    assert rows[11]["status"] == "skipped" and "plan" in rows[11]["why"]          # no brief for that slot
    assert rows[12]["upper"] == 67 and rows[12]["est"] == 17                     # token engine: upper bound
    assert est["total_upper"] == 18 + 18 + 67 and est["cap"] == 120
    assert est["per_engine"]["Nano Banana Pro"]["slots"] == 2


def test_key_mismatch_cap_stop_and_no_auto_approval(prod):
    c, con, S, iid = prod["c"], prod["con"], prod["S"], prod["iid"]
    _tags(prod)
    _plan(prod)
    est = c.get(f"/ikigai/api/production/{iid}/generate-all").json()
    assert c.post(f"/ikigai/api/production/{iid}/generate-all", json={"key": "stale"}).status_code == 422
    assert prod["gen"] == []
    r = c.post(f"/ikigai/api/production/{iid}/generate-all", json={"key": est["key"], "cap": 40})
    assert r.status_code == 200
    b = production.batch_state()
    assert not b["running"] and [x["status"] for x in b["rows"] if x["slot"] in (3, 9, 10)] == ["done", "done", "skipped"]
    assert "capped at 40" in b["stop_reason"] and len(prod["gen"]) == 2
    rec = _rec(prod)
    assert not (rec.get("mockup_approvals") or {})                             # nothing approved
    assert "2 made" in rec["production"]["batches"][-1]["report"] and "Spent 36" in rec["production"]["batches"][-1]["report"]
    assert prefs.get(con, S, "generate_all_cap") == 40


def test_a_hard_failure_stops_and_a_slot_failure_continues(prod, monkeypatch):
    c, con, S, iid = prod["c"], prod["con"], prod["S"], prod["iid"]
    _tags(prod)
    _plan(prod)
    n = {"i": 0}
    real = production.run_slot

    def flaky(con_, s_, idea, slot, tpl=None, gen=None, **kw):
        n["i"] += 1
        if slot == 3:
            production._job.update(running=False)
            return {"kind": "failed", "hard": False, "network": False, "credits": 18.0, "usd": None,
                    "why": "the scene has no clean blank frame insert"}
        if slot == 9:
            production._job.update(running=False)
            return {"kind": "failed", "hard": True, "network": False, "credits": None, "usd": None,
                    "why": "kie.ai refused the job: insufficient credits"}
        return real(con_, s_, idea, slot, tpl, gen, **kw)
    monkeypatch.setattr(production, "run_slot", flaky)
    est = c.get(f"/ikigai/api/production/{iid}/generate-all").json()
    c.post(f"/ikigai/api/production/{iid}/generate-all", json={"key": est["key"]})
    rows = {r["slot"]: r for r in production.batch_state()["rows"]}
    assert rows[3]["status"] == "failed" and rows[9]["status"] == "failed"
    assert rows[10]["status"] == "skipped" and "Stopped after slot 9" in rows[10]["why"]
    assert n["i"] == 2 and production.batch_state()["spent"] == 18.0


def test_cancel_stops_after_the_running_slot_and_cards_are_refused_during_a_batch(prod, monkeypatch):
    c, con, S, iid = prod["c"], prod["con"], prod["S"], prod["iid"]
    _tags(prod)
    _plan(prod)
    real = production.run_slot
    seen = []

    def spy(con_, s_, idea, slot, tpl=None, gen=None, **kw):
        seen.append(slot)
        r = c.post(f"/ikigai/api/production/{iid}/slots/12/generate", json={})
        assert r.status_code == 422 and "Generate all is running" in r.json()["detail"]
        production.cancel_batch()
        return real(con_, s_, idea, slot, tpl, gen, **kw)
    monkeypatch.setattr(production, "run_slot", spy)
    est = c.get(f"/ikigai/api/production/{iid}/generate-all").json()
    c.post(f"/ikigai/api/production/{iid}/generate-all", json={"key": est["key"]})
    b = production.batch_state()
    assert seen == [3] and b["rows"][0]["status"] == "done" and "Cancelled" in b["stop_reason"]


def test_approved_slots_are_never_touched_and_recover_marks_interrupted(prod):
    c, con, S, iid = prod["c"], prod["con"], prod["S"], prod["iid"]
    _tags(prod)
    _plan(prod, (3,))
    production.start_slot(con, S, iid, 3)
    production.run_slot(con, S, iid, 3, None, _gen(prod))
    name = _rec(prod)["production"]["slots"]["3"]["file"]
    c.post(f"/ikigai/api/production/{iid}/images/{name}", json={"decision": "approved"})
    before = json.dumps(_rec(prod)["production"]["slots"]["3"], sort_keys=True)
    _plan(prod, (9,))
    est = c.get(f"/ikigai/api/production/{iid}/generate-all").json()
    assert 3 not in [r["slot"] for r in est["rows"]]
    c.post(f"/ikigai/api/production/{iid}/generate-all", json={"key": est["key"]})
    assert json.dumps(_rec(prod)["production"]["slots"]["3"], sort_keys=True) == before
    lid = prints.listing_for(con, iid)["id"]
    rec = prints._record(con, lid)
    rec["production"]["batch_live"] = {"rows": [{"slot": 9, "status": "running"}], "spent": 0}
    prints._save_record(con, lid, rec)
    production.recover(con)
    last = _rec(prod)["production"]["batches"][-1]
    assert last["status"] == "interrupted" and last["rows"][0]["status"] == "skipped"
    assert "batch_live" not in _rec(prod)["production"]


# ---------- C.5: A/B closeness ----------

def test_ab_plans_three_variants_free_and_generates_with_place_false(prod, board, monkeypatch):
    c, con, S, iid = prod["c"], prod["con"], prod["S"], prod["iid"]
    _tags(prod)
    b = pv2_brief(slot=3)
    _put_plan(prod, {"version": 1, "status": "ready", "briefs": {"3": b}})
    entry = {"reference": "0901", "engine": "nano-banana-pro", "engine_label": "Nano Banana Pro", "credits_each": 18,
             "status": "planned", "variants": {}}
    for v in (20, 60, 100):
        vb = dict(b, ref_closeness=v, ref_band=splan.band_of(v))
        vb["prompt"] = splan.assemble(vb)
        entry["variants"][str(v)] = vb
    splan._save(con, iid, lambda sp: sp.setdefault("abtest", {}).__setitem__("3", entry))
    assert prod["gen"] == []                                                  # planning spent nothing
    est = c.get(f"/ikigai/api/production/{iid}/slots/3/abtest/estimate").json()
    assert est["total_upper"] == 54 and [r["label"] for r in est["rows"]] == ["closeness 20", "closeness 60",
                                                                              "closeness 100"]
    before = json.dumps(_rec(prod)["production"]["slots"].get("3"), sort_keys=True)
    c.post(f"/ikigai/api/production/{iid}/slots/3/abtest/generate", json={"key": est["key"]})
    assert len(prod["gen"]) == 3 and "do not copy individual objects" in prod["gen"][2]["prompt"]
    assert json.dumps(_rec(prod)["production"]["slots"].get("3"), sort_keys=True) == before        # slot untouched
    ab = _panel(prod)["abtest"]["3"]
    files = [v["result"]["file"] for v in ab["variants"].values()]
    assert all(f.startswith("AB_03_") for f in files)
    folder = production._images_dir(S, prints.listing_for(con, iid))
    assert all((folder / "Archive" / f).is_file() for f in files)
    c.post(f"/ikigai/api/production/{iid}/slots/3/abtest/place", json={"value": 60})
    srec = _rec(prod)["production"]["slots"]["3"]
    assert srec["ab"] == {"value": 60} and (folder / srec["file"]).is_file()
    assert not (_rec(prod).get("mockup_approvals") or {}).get(srec["file"])          # pending, never approved


def test_plan_variants_uses_one_reference_three_closeness_values_and_spends_nothing(prod, board):
    con, S, iid = prod["con"], prod["S"], prod["iid"]
    _tags(prod)
    b = pv2_brief(slot=3)
    _put_plan(prod, {"version": 1, "status": "ready", "briefs": {"3": b}})
    asked = []

    def ask(prompt, images=None):
        asked.append(prompt)
        raw = {k: v for k, v in b.items() if k not in ("lint", "prompt", "rev", "history", "attempts", "edited_by",
                                                     "stale", "ref_use", "marker")}
        return json.dumps({"briefs": [dict(raw, reference="0901")], "registers_ok": ["ordinary_apartment"]})
    entry = splan.plan_variants(con, S, iid, 3, ask)
    assert len(asked) == 3 and prod["gen"] == []
    assert "20 of 100 (essence)" in asked[0] and "100 of 100 (close)" in asked[2]
    assert {v["reference"] for v in entry["variants"].values()} == {"0901"}
    assert [v["ref_band"] for v in entry["variants"].values()] == ["essence", "balanced", "close"]
    assert splan.get_plan(_rec(prod))["abtest"]["3"]["status"] == "planned"


def test_a_plan_records_the_controls_it_was_made_with(prod):
    from test_slot_planner_flow import stub_ask
    con, S, iid = prod["con"], prod["S"], prod["iid"]
    _tags(prod)
    prefs.put(con, "reference_share", 60)
    splan.run(con, S, iid, ask=stub_ask())
    sp = splan.get_plan(_rec(prod))
    assert sp["controls"]["share"] == 60 and sp["controls"]["closeness"] == 60
    prefs.put(con, "reference_closeness", 30)
    pv = _panel(prod)["set_plan"]
    assert pv["controls_changed"] is True                    # a slider change never re-plans by itself
