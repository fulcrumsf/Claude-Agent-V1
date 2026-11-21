"""pv2 briefs (realism addendum 3-5, tests 8.1.4-8.1.6): lived-in lint, references, compact prompt texts that keep every
rule, set-wide repeat limits, reference validation and the planner loop with canned replies. No model, no credits."""
import json
import re

import pytest

from app import room_slots as rs, slot_planner as sp

SCENE2 = ("A rented 1970s condo bedroom with a hand-me-down pine dresser beside a white flat-pack shelf. A denim jacket "
          "hangs over the back of a vintage chair, and a half-finished mug of tea sits on the dresser next to keys in "
          "a small enamel bowl. The bedding is rumpled oat linen, the rug sits slightly askew on worn oak floorboards, "
          "and a radiator runs under the window. A charging cable trails from a power outlet near the skirting board, "
          "which is scuffed at one corner. Folded laundry waits in a neat pile at the foot of the bed, below the "
          "frame's bottom edge.")


def ref_entry(rid="0024", display="hung", shot="medium", side="left", light="overcast_flat", height="eye",
              lens="lens_normal", lived="lived_in"):
    return {"id": rid, "usable": True, "camera_side": side, "uses": [], "grades": [],
            "tags": {"display_group": display, "shot": shot, "camera_height": height, "lens": lens,
                     "light_type": light, "lived_in": lived}}


def b2(slot=16, room="Bedroom", refs=None, **kw):
    raw = {"pv": 2, "slot": slot, "source": "new", "print_size": "12x16", "shot": "medium", "setting": "dresser_top",
           "display": "hung_over_furniture", "presentation": "frame", "frame_finish": "walnut_frame",
           "camera_side": "right", "camera_height": "counter", "lens": "lens_normal", "light_type": "overcast_flat",
           "light_from": "left", "depth_of_field": "deep_focus",
           "wall": {"name": "warm white", "hex": "#F2EEE6", "treatment": "plaster"}, "floor": "worn oak boards",
           "furniture": {"style": "eclectic_mix", "colour": "pine", "family": "light_wood"}, "house": "condo_1970s",
           "buyer": "reader", "props": ["a denim jacket", "a half-finished mug", "keys in an enamel bowl",
                                       "folded laundry"],
           "scene": SCENE2, "occupant": "a nurse who works night shifts", "lived_in": "lived_in",
           "window": {"covering": "venetian_blind", "view": "street"}, "photo_style": "phone_snapshot",
           "reference": "0024"}
    raw.update(kw)
    ctx = {"slot": slot, "room": room, "decor": "Modern", "ratios": list(rs.RATIOS)}
    b = sp.normalise(raw, ctx)
    refs = [ref_entry()] if refs is None else refs
    sp.apply_reference(b, next((e for e in refs if e["id"] == b.get("reference")), None))
    b["lint"] = sp.lint(b, dict(ctx, refs=refs))
    return b


def why(b):
    return " | ".join(b["lint"]["why"])


# ---------- normalise / lint / derive ----------

def test_a_good_pv2_brief_passes_and_derives_light_and_camera():
    b = b2()
    assert b["lint"]["pass"], why(b)
    assert b["pv"] == 2 and b["light_style"] == "soft_even" and b["shadow"] == "soft"
    assert b["camera_side"] == "left" and b["camera_height"] == "eye" and b["lens"] == "lens_normal"   # from the ref
    assert b["ref_use"] == ["camera", "lens", "composition", "character", "light"]
    f = b2(reference_flip=True)
    assert f["camera_side"] == "right"
    assert "light" not in b2(light_type="north_light_even")["ref_use"]


def test_a_reference_camera_height_is_fixed_up_for_the_display():
    b = b2(display="lean_on_surface", refs=[ref_entry(height="surface")])
    assert b["camera_height"] == "surface"
    b = b2(display="hung_over_furniture", refs=[ref_entry(height="surface")])
    assert b["camera_height"] == "counter" and b["lint"]["pass"], why(b)


@pytest.mark.parametrize("kw,needle", [
    ({"scene": SCENE2 + " It is seen from the left."}, "names the camera"),
    ({"scene": SCENE2 + " A calendar hangs by the door."}, "carry text"),
    ({"scene": SCENE2 + " A stack of books leans on the shelf."}, "books must be described"),
    ({"shot": "tight", "print_size": "5x7", "setting": "nightstand", "display": "standing_on_surface",
      "lived_in": "busy", "props": ["a mug"]}, "busy"),
    ({"frame_finish": "painted_frame", "frame_colour": {"name": "apricot", "hex": "#F5B27A"}}, "too close"),
    ({"scene": SCENE2 + " A lamp glows after dark."}, "night or lamplight"),
    ({"refs_mismatch": True}, "does not fit"),
    ({"occupant": ""}, "occupant"),
    ({"light_type": "blind_stripes", "window": {"covering": "linen_curtains", "view": "trees"}}, "venetian"),
    ({"light_type": "overcast_flat", "scene": SCENE2 + " Sunlight warms the floor."}, "sun words")])
def test_pv2_lint_rules_fail_once_each(kw, needle):
    kw = dict(kw)
    if kw.pop("refs_mismatch", False):
        b = b2(refs=[ref_entry(display="floor")])
    else:
        b = b2(**kw)
    assert not b["lint"]["pass"] and needle in why(b), why(b)


def test_qualified_objects_pass_when_described_unreadable():
    b = b2(scene=SCENE2 + " Two books with plain spines turned away sit on the shelf; a phone lies face down.")
    assert b["lint"]["pass"], why(b)


# ---------- assemble ----------

def test_occupant_never_reaches_the_prompt_and_text_only_has_no_image_clause():
    b = b2()
    p = sp.assemble(b)
    assert "nurse" not in p and "Image 1 is a photograph of a different room" in p
    assert "Image 1" not in sp.assemble(b, ref=False)
    assert "direction and quality of the light" in p
    nl = sp.assemble(b2(light_type="north_light_even"))
    assert "Use the light described below, not the light in Image 1." in nl


@pytest.mark.parametrize("pres", ["frame", "mat", "canvas", "canvas_bare"])
@pytest.mark.parametrize("hx", ["#F2EEE6", "#C8643C"])
@pytest.mark.parametrize("style", ["compact", "full"])
def test_compact_keeps_every_rule(pres, hx, style):
    fin = {"frame": "walnut_frame", "mat": "black_frame", "canvas": "natural_wood_floater", "canvas_bare": "none"}[pres]
    b = b2(presentation=pres, frame_finish=fin, wall={"name": "w", "hex": hx, "treatment": "plaster"})
    b["prompt_style"] = style
    p = sp.assemble(b)
    marker = b["marker"]
    assert sp.MARKER_WORDS.get(marker, rs.INSERT_COLOUR).split(" (")[0] in p
    assert ", ".join(map(str, sp.MARKER_RGB[marker])) in p
    for name, rx in sp.RULES:
        assert re.search(rx, p, re.I), (name, style, pres)
    for rx in sp.RULES_PRESENT[pres]:
        assert re.search(rx, p, re.I), (rx, style, pres)


def _words(t):
    return len(t.split())


@pytest.mark.parametrize("pres", ["frame", "mat"])
def test_compact_word_targets(pres):
    scene = " ".join((SCENE2 + " " + "plain " * 80).split()[:160])
    fin = "walnut_frame" if pres == "frame" else "black_frame"
    b = b2(presentation=pres, frame_finish=fin, scene=scene)
    b["prompt_style"] = "compact"
    for marker in ("orange", "blue"):
        b["marker"] = marker
        colour = rs.INSERT_COLOUR if marker == "orange" else sp.MARKER_WORDS[marker]
        fixed = (sp.PRINT_AREA_C.format(colour=colour, name=marker) + sp.present_text_c(b) + " " + sp.GUARD_C
                 + sp.CLOSING_C)
        assert _words(fixed) <= 190
        assert _words(sp.assemble(b, ref=False)) <= 490
        # the reference clause is the addendum's exact wording (85 words, counted 72 in the plan): +clause only
        assert _words(sp.assemble(b)) - _words(sp.assemble(b, ref=False)) == _words(sp.REF_CLAUSE)
    old = 365                                                         # measured 2026-11-20 (slot 16, frame)
    assert _words(fixed) < old


def test_canvas_compact_fixed_blocks_stay_under_270():
    b = b2(presentation="canvas", frame_finish="natural_wood_floater", print_size="16x20")
    fixed = (sp.PRINT_AREA_C.format(colour=rs.INSERT_COLOUR, name="orange") + sp.present_text_c(b) + " "
             + sp.GUARD_C + sp.CLOSING_C)
    assert _words(fixed) <= 270


# ---------- check_set: repeat limits ----------

def _d(slot, **kw):
    b = b2(slot=slot, **kw)
    return b


def test_the_16_plus_19_photograph_fails_the_composition_signature_on_the_later_slot():
    fixed16 = sp.descriptor(b2(slot=16, light_type="golden_low", reference=None, refs=[]))
    b19 = b2(slot=19, light_type="golden_low", reference=None, refs=[], scene=SCENE2.replace("rented", "small"))
    b19.update({k: fixed16[k] for k in sp.COMP_KEYS})
    chk = sp.check_set({19: b19}, {16: fixed16}, order=rs.ROOM_SLOTS)
    assert any(f["rule"] == "composition" and f["slots"] == [19] for f in chk["failures"]), chk["failures"]


def test_dried_stems_once_passes_twice_fails_and_fixed_alone_never_fails():
    s1 = SCENE2 + " Dried grasses lean in a clay jug at the edge."
    one = sp.check_set({16: b2(slot=16, scene=s1)}, {}, order=rs.ROOM_SLOTS)
    assert not any(f["rule"] == "props" and "dried" in f["text"] for f in one["failures"])
    two = sp.check_set({16: b2(slot=16, scene=s1), 17: b2(slot=17, scene=s1.replace("rented", "small"))}, {},
                       order=rs.ROOM_SLOTS)
    hit = [f for f in two["failures"] if f["rule"] == "props" and "dried" in f["text"]]
    assert hit and hit[0]["slots"] == [17]
    fx = {13: dict(sp.descriptor(b2(slot=13, scene=s1)), slot=13), 14: dict(sp.descriptor(b2(slot=14, scene=s1)), slot=14)}
    clean = sp.check_set({16: b2(slot=16)}, fx, order=rs.ROOM_SLOTS)
    assert not any(f["rule"] == "props" and "dried" in f["text"] for f in clean["failures"])
    more = sp.check_set({16: b2(slot=16, scene=s1)}, fx, order=rs.ROOM_SLOTS)
    f = [x for x in more["failures"] if x["rule"] == "props" and "dried" in x["text"]]
    assert f and f[0]["slots"] == [16] and "already appears in fixed slots 13, 14" in f[0]["text"]


def test_reference_reuse_warm_sun_and_lived_in_mix():
    a, b = b2(slot=16), b2(slot=17, scene=SCENE2.replace("rented", "small"))
    chk = sp.check_set({16: a, 17: b}, {}, order=rs.ROOM_SLOTS)
    assert any(f["rule"] == "reference" and f["slots"] == [17] for f in chk["failures"])
    gold = {s: b2(slot=s, light_type="golden_low", reference=None, refs=[], scene=SCENE2 + f" {w}.")
            for s, w in ((16, "Calm"), (17, "Quiet"))}
    chk = sp.check_set(gold, {}, order=rs.ROOM_SLOTS)
    assert any(f["rule"] == "light" and "golden" in f["text"] and f["slots"] == [17] for f in chk["failures"])
    tidy = {s: b2(slot=s, lived_in="lived_in", reference=None, refs=[], scene=SCENE2 + f" {w}.")
            for s, w in ((16, "Calm"), (17, "Quiet"), (18, "Still"))}
    chk = sp.check_set(tidy, {}, order=rs.ROOM_SLOTS)
    assert any(f["rule"] == "lived_in" and "tidy" in f["text"] for f in chk["failures"])


def test_pv1_sets_never_get_the_new_rules():
    from test_slot_planner import brief
    one, two = brief(slot=16), brief(slot=17)
    rules = {f["rule"] for f in sp.check_set({16: one, 17: two}, {}, order=rs.ROOM_SLOTS)["failures"]}
    assert not rules & {"props", "composition", "reference", "windows", "lived_in", "photo", "frames", "region", "night"}


# ---------- reference validation ----------

def test_invalid_and_duplicate_references_are_reassigned_by_code():
    refs = [ref_entry("0023"), ref_entry("0024"), ref_entry("0025", display="floor"), ref_entry("0026"),
            ref_entry("0027"), ref_entry("0042")]
    bs = {16: b2(slot=16, reference="0024", refs=refs), 17: b2(slot=17, reference="0024", refs=refs),
          18: b2(slot=18, reference="9999", refs=refs), 19: b2(slot=19, reference="0025", refs=refs)}
    notes = sp.validate_references(bs, {"0042"}, refs, rs.ROOM_SLOTS)
    got = {s: b["reference"] for s, b in bs.items()}
    assert got == {16: "0024", 17: "0023", 18: "0026", 19: "0027"}
    assert len(notes) == 3 and all("code picked" in n for n in notes)
    assert not any(b["reference_reused"] for b in bs.values())


def test_fewer_references_than_slots_reuse_the_least_used():
    refs = [ref_entry("0023"), ref_entry("0024")]
    bs = {s: b2(slot=s, reference="0024", refs=refs) for s in (16, 17, 18)}
    sp.validate_references(bs, set(), refs, rs.ROOM_SLOTS)
    assert [bs[s]["reference"] for s in (16, 17, 18)][:2] == ["0024", "0023"] and bs[18]["reference_reused"]
    chk = sp.check_set(bs, {}, order=rs.ROOM_SLOTS)
    assert not any(f["rule"] == "reference" for f in chk["failures"])        # a forced reuse is not blamed


def test_no_fitting_reference_goes_text_only():
    b = b2(reference="0024", refs=[ref_entry(display="floor")])
    bs = {16: b}
    notes = sp.validate_references(bs, set(), [ref_entry(display="floor")], rs.ROOM_SLOTS)
    assert b["reference"] is None and "text-only" in notes[0]
    assert "Image 1" not in sp.assemble(dict(b, ref_use=[]))


# ---------- planner loop ----------

def _ctx(refs):
    from test_slot_planner import _ctx as ctx1
    ctx, _ = ctx1()
    ctx = dict(ctx, refs=refs, fixed_refs=[], graded=[{"kind": "bad", "grade": "C-", "note": "catalog look",
                                                        "scene": "x"}])
    return ctx


def stub_v2(calls):
    def ask(prompt, images=None):
        calls.append(prompt)
        data = json.loads(prompt.split("Inputs:\n", 1)[1].split("\n\n", 1)[0])
        out = []
        sizes = ["12x16", "16x20", "A3", "10x15", "12x18", "15x20", "12x15", "11x14", "18x24", "20x30", "A2", "24x30"]
        lights = ["overcast_flat", "north_light_even", "hard_diagonal_sun", "rainy_day", "dusk_lamp_mix",
                  "morning_soft_sun", "golden_low", "north_light_even"]
        for i, o in enumerate(data["open_slots"]):
            setting = next(s for s, v in o["settings"].items() if "hung_over_furniture" in v["displays"]
                           and "medium" in v["scales"])
            out.append({"pv": 2, "slot": o["slot"], "source": "new", "print_size": sizes[i % len(sizes)],
                        "shot": "medium", "setting": setting, "display": "hung_over_furniture",
                        "presentation": "frame", "frame_finish": "walnut_frame", "camera_side": "left",
                        "camera_height": "eye", "lens": "lens_normal", "light_type": lights[i % len(lights)],
                        "light_from": "left", "depth_of_field": "deep_focus",
                        "wall": {"name": "white", "hex": "#F2EEE6", "treatment": "plain_paint"}, "floor": "oak",
                        "furniture": {"style": "eclectic_mix", "colour": "oak", "family": "light_wood"},
                        "house": "condo_1970s", "buyer": "reader", "props": ["a mug"], "occupant": "a teacher",
                        "lived_in": "tidy", "window": {"covering": "no_window_in_view", "view": "none"},
                        "photo_style": "phone_snapshot", "reference": "0024",
                        "scene": SCENE2.replace("rented", f"rented {i}")})
        return json.dumps({"briefs": out})
    return ask


def test_planner_prompt_carries_references_sheet_and_capped_grades():
    refs = [ref_entry("0023"), ref_entry("0024")]
    ctx = dict(_ctx(refs), has_sheet=True, has_ref_sheet=True)
    p = sp.planner_prompt(ctx)
    assert "Image 3 is the sheet of reference photographs" in p and '"references"' in p
    assert "tonys_past_grades" in p and "never copy a scene" in p
    assert "lived in" in sp.SYSTEM_PROMPT and "Photography taste" not in sp.SYSTEM_PROMPT
    assert "Photography taste" in sp.SYSTEM_PROMPT_V1


def test_planner_loop_reassigns_duplicate_references_and_logs_them():
    refs = [ref_entry(f"00{i}") for i in range(23, 40)]
    ctx = _ctx(refs)
    calls = []
    res = sp.plan_set(ctx, stub_v2(calls), {"planner_rounds": 1}, log=lambda *_: None)
    picked = [b.get("reference") for b in res["briefs"].values() if b["source"] == "new"]
    assert picked and len(set(picked)) == len(picked)
    assert res["ref_notes"] and all(b["pv"] == 2 for b in res["briefs"].values() if b["source"] == "new")
    assert all("Image 1 is a photograph" in b["prompt"] for b in res["briefs"].values() if b.get("prompt"))


def test_graded_examples_good_first_bad_capped(monkeypatch, tmp_path):
    from app import scene_templates as stp
    lib = []
    for i, g in enumerate(["C", "C-", "A", "B+", "C+"]):
        d = tmp_path / f"T{i}"
        d.mkdir()
        (d / "T.psd").write_bytes(b"")
        stp.add_grade(d / "T.psd", {"idea_id": 3, "slot": 16 + i, "grade": g, "note": f"n{i}"})
        lib.append({"psd": d / "T.psd", "wired": False, "manifest": {"created": f"2026-11-2{i}",
                                                                      "brief": {"scene": "word " * 30, "shot": "medium"}}})
    monkeypatch.setattr(stp, "library_templates", lambda settings=None: lib)
    ex = sp.graded_examples({})
    assert [e["kind"] for e in ex] == ["good", "good", "bad", "bad"] and ex[0]["grade"] == "A" and ex[2]["grade"] == "C-"
    assert len(sp.graded_examples({}, cap_words=40)) < 4


def test_flip_fix_mirrors_a_reference_to_balance_the_camera_side():
    refs = [ref_entry(f"00{i}", side="right") for i in range(23, 30)]
    ctx = _ctx(refs)
    fixed = {k: dict(v, camera_side="right") for k, v in ctx["fixed_desc"].items()}
    ctx["fixed_desc"] = fixed
    hung = {"Kids": "over_kids_bed", "Bedroom": "over_bed", "Office": "over_desk", "Kitchen & dining": "over_dining_table"}
    cur = {o["slot"]: b2(slot=o["slot"], room=o["room"], reference=f"00{23 + i}", refs=refs, setting=hung[o["room"]],
                         scene=SCENE2.replace("rented", f"rented {i}")) for i, o in enumerate(ctx["open"])}
    chk = sp.check_set(cur, fixed, ctx["order"], None, 2)
    assert any(f["rule"] == "camera" for f in chk["failures"])
    assert all(b["lint"]["pass"] for b in cur.values()), [b["lint"]["why"] for b in cur.values()]
    new, chk2 = sp.flip_fix(cur, ctx, chk, log=lambda *_: None)
    assert sp.total_blame(chk2) < sp.total_blame(chk)
    assert any(b["reference_flip"] and b["camera_side"] == "left" for b in new.values())
