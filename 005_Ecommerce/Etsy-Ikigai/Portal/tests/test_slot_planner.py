"""Slot-set planner (Pipeline_Docs/Slot_Set_Planner_Plan.md + Tony's decisions 2026-11-19): lint, prompt assembly,
the set check, the planner loop with canned replies, the library swap. No model, no credits."""
import json
import re

import pytest

from app import room_slots as rs, slot_planner as sp

SCENE = ("A quiet bedroom in a London flat with a pale oak nightstand under a soft linen curtain. A small stoneware cup "
         "and two cloth-bound books with plain covers sit beside the piece. The bed linen is crumpled white and oat, a "
         "wool throw folded at its foot. The floor is pale oak planks with a jute runner, and the window frame is "
         "painted the same calm white as the skirting. Dried grasses lean in a clay jug at the far edge of the "
         "picture, well clear of the frame.")
assert 60 <= len(SCENE.split()) <= 160


def brief(slot=16, room="Bedroom", **kw):
    raw = {"slot": slot, "source": "new", "print_size": "5x7", "shot": "tight", "setting": "nightstand",
           "display": "standing_on_surface", "presentation": "mat", "frame_finish": "walnut_frame",
           "camera_side": "left", "camera_height": "surface", "lens": "lens_normal", "light_style": "soft_direct",
           "light_from": "left", "shadow": "soft", "depth_of_field": "soft_background",
           "wall": {"name": "warm white", "hex": "#F2EEE6", "treatment": "limewash"}, "floor": "pale oak planks",
           "furniture": {"style": "scandi_light_oak", "colour": "oak", "family": "light_wood"},
           "house": "london_flat", "buyer": "gift_buyer", "props": ["small stoneware cup", "two plain books"],
           "scene": SCENE}
    for k, v in kw.items():
        raw[k] = v
    ctx = {"slot": slot, "room": room, "decor": "Japandi", "ratios": list(rs.RATIOS)}
    b = sp.normalise(raw, ctx)
    b["lint"] = sp.lint(b, ctx)
    return b


def why(b):
    return " | ".join(b["lint"]["why"])


# ---------- 11.5 lint ----------

def test_a_good_brief_passes_and_code_derives_ratio_scale_family_marker():
    b = brief()
    assert b["lint"]["pass"], why(b)
    assert (b["ratio"], b["scale"]) == ("iso", "small")
    assert b["wall"]["family"] == "white_cream" and b["marker"] == "orange"


def test_unknown_keys_and_rationale_are_dropped_and_the_model_marker_is_ignored():
    b = brief(why="because it is perfect", rationale="x", marker="blue")
    assert "why" not in b and "rationale" not in b and b["marker"] == "orange"


@pytest.mark.parametrize("hx", ["#C8643C", "#FFCBA4", "#D8C3A0", "#FF7F50", "#D4A017", "#4A0404", "#8B5A2B"])
def test_warm_walls_are_allowed_and_get_the_blue_marker(hx):
    b = brief(wall={"name": "warm wall", "hex": hx, "treatment": "plaster"}, frame_finish="black_frame")
    assert b["marker"] == "blue", hx
    assert not any("marker" in w for w in b["lint"]["why"]), why(b)
    assert "pale sky blue" in sp.assemble(b) and "orange" not in sp.assemble(b)


@pytest.mark.parametrize("hx", ["#2F5D62", "#1F4E9E", "#046307", "#5B2A4E", "#F4F1EA", "#CFC8BD", "#9CAF88"])
def test_cool_and_neutral_walls_keep_the_orange_marker(hx):
    b = brief(wall={"name": "w", "hex": hx, "treatment": "plain_paint"}, frame_finish="white_frame")
    assert b["marker"] == "orange"
    assert rs._PRINT_AREA in sp.assemble(b) if b["lint"]["pass"] else True


def test_marker_lint_never_blue_on_blue_and_never_wrong_side():
    b = brief(wall={"name": "deep teal", "hex": "#2F5D62", "treatment": "plain_paint"}, frame_finish="white_frame")
    b["marker"] = "blue"
    assert any("blue insert marker on a teal blue wall" in w for w in sp.lint(b)["why"])
    b = brief(wall={"name": "terracotta", "hex": "#C8643C", "treatment": "plaster"}, frame_finish="black_frame")
    b["marker"] = "orange"
    assert any("needs the blue insert marker" in w for w in sp.lint(b)["why"])


def test_lint_rejections():
    assert any("does not stand out" in w for w in sp.lint(brief(
        wall={"name": "ivory", "hex": "#B5AFA5", "treatment": "plain_paint"}, frame_finish="oak_frame"))["why"])
    assert any("never shown as a tight" in w or "does not fit nightstand" in w
               for w in brief(print_size="24x36")["lint"]["why"])
    assert any("canvas only for medium" in w for w in brief(presentation="canvas")["lint"]["why"])
    assert any("not in the size chart" in w for w in brief(print_size="7x9")["lint"]["why"])
    bad = brief(scene=SCENE.replace("A small stoneware cup", "A sleeping cat, a woman's hand and a poster"))
    assert any("names" in w and "cat" in w for w in bad["lint"]["why"])
    assert any("words" in w for w in brief(scene="Too short.")["lint"]["why"])
    assert any("1 to 3 small props" in w for w in brief(props=[])["lint"]["why"])
    assert any("keystones" in w for w in brief(setting="dresser_top", display="hung_over_furniture",
                                               camera_height="low")["lint"]["why"])
    assert any("wide lens" in w for w in brief(lens="lens_wide")["lint"]["why"])
    assert any("blush walls" in w for w in brief(
        wall={"name": "blush", "hex": "#E3B5B0", "treatment": "plain_paint"}, frame_finish="gold_frame")["lint"]["why"])
    pan = brief(print_size="16x24", shot="medium", setting="over_bed", display="hung_over_furniture",
                camera_height="eye", presentation="frame", props=["a linen throw"],
                wall={"name": "sage", "hex": "#9CAF88", "treatment": "panelled"}, frame_finish="white_frame")
    assert any("panelling only behind hung art" in w for w in pan["lint"]["why"])
    ok = brief(print_size="16x24", shot="medium", setting="over_bed", display="hung_over_furniture",
               camera_height="eye", presentation="frame", props=["a linen throw"], frame_finish="white_frame",
               wall={"name": "sage", "hex": "#9CAF88", "treatment": "panelled"},
               scene=SCENE + " The art is centred inside one larger panel.")
    assert ok["lint"]["pass"], why(ok)


def test_ratio_without_a_room_folder_and_setting_from_another_room_are_rejected():
    ctx = {"slot": 16, "room": "Kids", "decor": "Kids", "ratios": ["iso"]}
    b = sp.normalise({**brief(), "print_size": "8x10", "setting": "nightstand"}, ctx)
    w = " | ".join(sp.lint(b, ctx)["why"])
    assert "no Kids folder" in w and "setting for Kids" in w


def test_assembled_prompt_has_every_fixed_block_and_says_portrait_frame_in_a_4_3_photo():
    b = brief()
    t = sp.assemble(b)
    assert t.startswith("Photorealistic interior photograph in a 4:3 landscape picture format, showing one portrait")
    for must in (SCENE, rs._PRINT_AREA, rs.LOOK_GUARD, sp.PLAN_GUARD_FRAME, sp.CLOSING, "5x7 print (5 x 7 in, 12.7 x "
                 "17.8 cm)", "45 to 65% of the picture height", "slim easel back", "coffee cup",
                 sp.CAMERA_SIDE_TEXT["left"], sp.LIGHT_FROM_TEXT["left"]):
        assert must in t, must
    assert "vertical (portrait) photograph" not in t                       # the v2 wording is never used here
    assert sp.ORIENTATION == "portrait"
    assert all(sp.size_in(s)[0] <= sp.size_in(s)[1] for s in sp.SIZE_INDEX)   # portrait only, no landscape sizes


def test_entry_and_hallway_settings_are_filed_under_living_room():
    assert "entry_console" in sp.ROOM_SETTINGS["Living room"] and "hallway_wall" in sp.ROOM_SETTINGS["Living room"]
    assert rs.ROOM_FOLDER["Living room"] == "living_rooms"


# ---------- 11.6 check_set ----------

GOOD = [  # 12 briefs that vary on every axis
    dict(print_size="5x7", shot="tight", setting="nightstand", display="standing_on_surface", presentation="mat",
         frame_finish="walnut_frame", camera_side="left", light_style="soft_direct", light_from="left", shadow="soft",
         wall={"name": "white", "hex": "#F2EEE6", "treatment": "limewash"}, house="london_flat", buyer="gift_buyer",
         furniture={"style": "scandi_light_oak", "colour": "oak", "family": "light_wood"}),
    dict(print_size="16x24", shot="medium", setting="over_bed", display="hung_over_furniture", presentation="frame",
         frame_finish="black_frame", camera_side="front", camera_height="eye", light_style="soft_even",
         light_from="right", shadow="hard", props=["a linen throw"],
         wall={"name": "sage", "hex": "#9CAF88", "treatment": "plain_paint"}, house="english_cottage",
         buyer="reader", furniture={"style": "rustic_farmhouse", "colour": "pine", "family": "mid_wood"}),
]


def _b(slot, room, **kw):
    return brief(slot, room, **kw)


def _word(n):
    return "vel" + "".join(chr(97 + (n // 26 ** k) % 26) for k in range(3))


def scene_for(i, extra=""):
    """A distinct 70+ word scene per index (its content words are its own; only the frame words repeat)."""
    return " ".join(f"A {_word(i * 40 + 3 * k)} {_word(i * 40 + 3 * k + 1)} beside the {_word(i * 40 + 3 * k + 2)}."
                    for k in range(12)) + " Everything is calm, tidy and photographed in natural daylight." + extra


def _set12():
    rows = [
        (3, "Living room", dict(print_size="24x36", shot="wide", setting="over_sofa", display="hung_over_furniture",
                                presentation="canvas", camera_side="front", camera_height="eye", light_style="golden_low",
                                light_from="left", shadow="soft", props=["a wool throw"],
                                wall={"name": "deep teal", "hex": "#2F5D62", "treatment": "plain_paint"},
                                house="brownstone", buyer="big_wall_decorator",
                                furniture={"style": "midcentury_teak", "colour": "teak", "family": "mid_wood"})),
        (9, "Living room", dict(print_size="A3", shot="medium", setting="sideboard_top", display="lean_on_surface",
                                presentation="frame", frame_finish="black_frame", camera_side="right",
                                camera_height="counter", light_style="crisp_direct", light_from="right", shadow="hard",
                                props=["a stoneware vase"],
                                wall={"name": "white", "hex": "#F4F1EA", "treatment": "plaster"}, house="paris_apartment",
                                buyer="reader", furniture={"style": "parisian_vintage", "colour": "walnut",
                                                           "family": "dark_wood"})),
        (10, "Bedroom", GOOD[0]),
        (11, "Office", dict(print_size="8x10", shot="tight", setting="desk_top", display="lean_on_surface",
                            presentation="frame", frame_finish="oak_frame", camera_side="right", camera_height="surface",
                            light_style="dappled", light_from="right", shadow="hard", props=["a brass pen pot"],
                            wall={"name": "navy", "hex": "#1F3A5F", "treatment": "plain_paint"}, house="nyc_loft",
                            buyer="desk_or_bookshelf_person",
                            furniture={"style": "industrial_metal", "colour": "black", "family": "black"})),
        (12, "Living room", dict(print_size="20x30", shot="wide", setting="floor_beside_chair", display="floor_lean",
                                 presentation="canvas_bare", camera_side="left", camera_height="low",
                                 light_style="soft_even", light_from="left", shadow="soft", props=["a boucle chair"],
                                 wall={"name": "terracotta", "hex": "#C8643C", "treatment": "plaster"},
                                 house="southwestern_adobe", buyer="first_home_buyer",
                                 furniture={"style": "boho_rattan", "colour": "cane", "family": "rattan_cane"})),
        (13, "Bedroom", GOOD[1]),
        (14, "Office", dict(print_size="12x16", shot="medium", setting="over_desk", display="hung_over_furniture",
                            presentation="mat", frame_finish="walnut_frame", camera_side="left", camera_height="eye",
                            light_style="soft_direct", light_from="right", shadow="soft", props=["a desk lamp base"],
                            wall={"name": "greige", "hex": "#CFC8BD", "treatment": "wood_slat"},
                            house="scandinavian_house", buyer="small_space_renter",
                            furniture={"style": "japandi_low_wood", "colour": "ash", "family": "light_wood"})),
        (15, "Living room", dict(print_size="22x28", shot="wide", setting="mantel", display="hung_over_furniture",
                                 presentation="frame", frame_finish="walnut_frame", camera_side="right",
                                 camera_height="eye", light_style="golden_low", light_from="left", shadow="hard",
                                 props=["a brass candlestick"],
                                 wall={"name": "warm grey", "hex": "#8A8580", "treatment": "panelled"},
                                 scene=SCENE + " The art is centred inside one larger panel.",
                                 house="english_cottage", buyer="parent",
                                 furniture={"style": "classic_traditional", "colour": "marble", "family": "painted_white"})),
        (16, "Kids", dict(print_size="A5", shot="tight", setting="toy_shelf", display="shelf_ledge", presentation="mat",
                          frame_finish="white_frame", camera_side="left", camera_height="surface",
                          light_style="soft_even", light_from="left", shadow="soft", props=["a knitted toy"],
                          wall={"name": "dusty blue", "hex": "#8FA9C2", "treatment": "wallpaper"},
                          house="suburban_colonial", buyer="parent",
                          furniture={"style": "kids_painted", "colour": "mint", "family": "painted_colour"})),
        (17, "Bedroom", dict(print_size="12x15", shot="medium", setting="dresser_top", display="lean_on_surface",
                             presentation="frame", frame_finish="walnut_frame", camera_side="front",
                             camera_height="seated", light_style="dappled", light_from="left", shadow="soft",
                             props=["dried stems in a jug"],
                             wall={"name": "blush", "hex": "#E3C9C4", "treatment": "plain_paint"},
                             house="coastal_cottage", buyer="cat_lover",
                             furniture={"style": "coastal_painted", "colour": "white", "family": "painted_white"})),
        (18, "Office", dict(print_size="18x24", shot="wide", setting="floor_lean", display="floor_lean",
                            presentation="canvas", camera_side="right", camera_height="low", light_style="crisp_direct",
                            light_from="right", shadow="hard", props=["a plant"],
                            wall={"name": "olive", "hex": "#5E6B3A", "treatment": "brick"}, house="midcentury_ranch",
                            buyer="big_wall_decorator",
                            furniture={"style": "modern_minimal", "colour": "white", "family": "upholstered_neutral"})),
        (19, "Kitchen & dining", dict(print_size="4x6", shot="tight", setting="open_shelf", display="shelf_ledge",
                                      presentation="mat", frame_finish="black_frame", camera_side="front",
                                      camera_height="counter", light_style="soft_direct", light_from="right",
                                      shadow="soft", props=["a ceramic jug"],
                                      wall={"name": "white tile", "hex": "#EDEBE6", "treatment": "tile"},
                                      house="japanese_home", buyer="small_space_renter",
                                      furniture={"style": "eclectic_mix", "colour": "teak", "family": "mid_wood"})),
    ]
    out = {}
    for slot, room, kw in rows:
        kw = dict(kw)
        extra = " The art is centred inside one larger panel." if kw["wall"]["treatment"] == "panelled" else ""
        kw["scene"] = scene_for(len(out), extra)
        out[slot] = _b(slot, room, **kw)
    return out


def test_a_hand_built_varied_set_of_12_passes():
    s = _set12()
    bad = {k: why(b) for k, b in s.items() if not b["lint"]["pass"]}
    assert not bad, bad
    chk = sp.check_set(s, {}, rs.ROOM_SLOTS, max_tight=None)
    assert chk["pass"], chk["failures"]


def test_twelve_identical_briefs_fail_with_blame_on_open_slots_only():
    s = {k: brief(k) for k in rs.ROOM_SLOTS}
    chk = sp.check_set(s, {}, rs.ROOM_SLOTS)
    rules = {f["rule"] for f in chk["failures"]}
    assert {"scale", "camera", "setting", "similar", "neighbours", "sizes"} <= rules
    fixed = {k: sp.descriptor(b) for k, b in list(s.items())[:8]}
    opens = dict(list(s.items())[8:])
    chk = sp.check_set(opens, fixed, rs.ROOM_SLOTS)
    assert set(chk["blame"]) == set(opens) and all(f["slots"] and set(f["slots"]) <= set(opens)
                                                   for f in chk["failures"])


def _book_club_fixed():
    """8 approved large 2x3 wall pieces (Book Club Cat slots 3, 9-15); unknown fields stay None."""
    fx = {}
    for i, s in enumerate([3, 9, 10, 11, 12, 13, 14, 15]):
        d = {k: None for k in sp.descriptor({})}
        d.update(slot=s, scale="large", shot="wide", ratio="2x3" if s != 13 else "11x14",
                 camera_side=("left", "right", "front")[i % 3], light_from=("left", "right")[i % 2])
        fx[s] = d
    return fx


def test_book_club_case_open_slots_must_be_small_medium_and_add_missing_ratios():
    fx = _book_club_fixed()
    s = _set12()
    good = {16: s[16], 17: s[17], 18: _b(18, "Office", **{**json.loads(json.dumps({
        "print_size": "12x16", "shot": "medium", "setting": "over_desk", "display": "hung_over_furniture",
        "presentation": "mat", "frame_finish": "black_frame", "camera_side": "right", "camera_height": "eye",
        "light_style": "golden_low", "light_from": "right", "shadow": "hard", "props": ["a brass tray"],
        "wall": {"name": "warm white", "hex": "#F1ECE2", "treatment": "plaster"}, "house": "nyc_loft",
        "buyer": "reader", "furniture": {"style": "industrial_metal", "colour": "steel", "family": "metal"}}))}),
        19: s[19]}
    good[19] = _b(19, "Nursery", **{**{k: v for k, v in {
        "print_size": "A4", "shot": "tight", "setting": "dresser_top", "display": "lean_on_surface",
        "presentation": "frame", "frame_finish": "oak_frame", "camera_side": "left", "camera_height": "surface",
        "light_style": "crisp_direct", "light_from": "left", "shadow": "soft", "props": ["a knitted toy"],
        "wall": {"name": "sage", "hex": "#8E9E80", "treatment": "plain_paint"}, "house": "english_cottage",
        "buyer": "parent", "furniture": {"style": "kids_painted", "colour": "white",
                                         "family": "painted_white"}}.items()}})
    avail = {16: ["iso"], 17: list(rs.RATIOS), 18: list(rs.RATIOS), 19: ["iso"]}
    chk = sp.check_set(good, fx, rs.ROOM_SLOTS, avail, max_tight=2)
    assert not [f for f in chk["failures"] if f["rule"] in ("scale", "ratio")], chk["failures"]
    bad = dict(good)
    bad[17] = _b(17, "Bedroom", **{**{"print_size": "16x24", "shot": "medium", "setting": "dresser_top",
                                      "display": "lean_on_surface", "presentation": "frame",
                                      "frame_finish": "walnut_frame", "camera_side": "front", "camera_height": "seated",
                                      "light_style": "dappled", "light_from": "left", "shadow": "soft",
                                      "props": ["dried stems"], "house": "coastal_cottage", "buyer": "cat_lover",
                                      "wall": {"name": "blush", "hex": "#E3C9C4", "treatment": "plain_paint"},
                                      "furniture": {"style": "coastal_painted", "colour": "white",
                                                    "family": "painted_white"}}})
    chk = sp.check_set(bad, fx, rs.ROOM_SLOTS, avail, max_tight=2)
    assert any(f["rule"] == "ratio" and 17 in f["slots"] for f in chk["failures"])   # another 2x3 on a 2x3-heavy set
    large = {**good, **{17: _b(17, "Bedroom", **{**{
        "print_size": "24x32", "shot": "wide", "setting": "over_bed", "display": "hung_over_furniture",
        "presentation": "canvas", "camera_side": "front", "camera_height": "eye", "light_style": "dappled",
        "light_from": "left", "shadow": "soft", "props": ["a throw"], "house": "coastal_cottage", "buyer": "cat_lover",
        "wall": {"name": "white", "hex": "#F4F1EA", "treatment": "plain_paint"},
        "furniture": {"style": "coastal_painted", "colour": "white", "family": "painted_white"}}}),
        18: _b(18, "Office", **{**{
            "print_size": "24x30", "shot": "wide", "setting": "floor_lean", "display": "floor_lean",
            "presentation": "canvas", "camera_side": "right", "camera_height": "low", "light_style": "golden_low",
            "light_from": "right", "shadow": "hard", "props": ["a plant"], "house": "nyc_loft", "buyer": "reader",
            "wall": {"name": "olive", "hex": "#5E6B3A", "treatment": "brick"},
            "furniture": {"style": "industrial_metal", "colour": "steel", "family": "metal"}}})}}
    chk = sp.check_set(large, fx, rs.ROOM_SLOTS, avail, max_tight=2)
    assert any(f["rule"] == "scale" for f in chk["failures"])        # 8 fixed large: open slots go small / medium


def test_neighbour_rule_and_unknown_fixed_fields_never_count_as_equal():
    a, b = brief(16), brief(17, setting="dresser_top", display="lean_on_surface")
    chk = sp.check_set({16: a, 17: b}, {}, [16, 17])
    assert any(f["rule"] == "neighbours" and f["slots"] == [17] for f in chk["failures"])
    unknown = {k: None for k in sp.descriptor({})}
    assert sp.similarity(unknown, dict(unknown)) == 0.0


def test_tight_cap_until_the_first_tight_scene_is_proven():
    s = {16: brief(16), 17: brief(17, print_size="A5", setting="dresser_top", display="lean_on_surface"),
         18: brief(18, print_size="4x6", setting="nightstand")}
    chk = sp.check_set(s, {}, [16, 17, 18], max_tight=2)
    assert any(f["rule"] == "tight" and f["slots"] == [18] for f in chk["failures"])


# ---------- 11.7 planner loop with canned replies ----------

def _ctx():
    s = _set12()
    fx = {k: sp.descriptor(b) for k, b in s.items() if k not in (16, 17, 18, 19)}
    rooms = {16: "Kids", 17: "Bedroom", 18: "Office", 19: "Kitchen & dining"}
    return {"open": [{"slot": k, "room": rooms[k], "decor": "Japandi", "ratios": list(rs.RATIOS), "library": []}
                     for k in (16, 17, 18, 19)],
            "fixed": {str(k): v for k, v in fx.items()}, "fixed_desc": fx, "order": rs.ROOM_SLOTS, "images": [],
            "design": {"title": "t"}, "credits_per_scene": 18, "max_tight": 2}, s


def _raw(b):
    return {k: b.get(k) for k in sp.KEEP if k in b} | {"why": "because"}


def test_round_two_rewrites_only_the_blamed_slots_and_passes():
    ctx, s = _ctx()
    first = {k: _raw(s[k]) for k in (16, 17, 18, 19)}
    first[17] = dict(first[16], slot=17)                               # 17 copies 16: a close pair + same setting
    prompts = []

    def ask(prompt, images=None):
        prompts.append(prompt)
        if len(prompts) == 1:
            return "```json\n" + json.dumps({"briefs": list(first.values())}) + "\n```"
        assert "Rewrite ONLY slots" in prompt and "17" in prompt.split("Rewrite ONLY slots")[1]
        return json.dumps({"briefs": [_raw(s[17])]})
    res = sp.plan_set(ctx, ask, {"planner_rounds": 3}, log=lambda *_: None)
    assert res["status"] == "ready", res.get("message")
    assert res["rounds"] == 2 and len(prompts) == 2
    assert res["briefs"]["17"]["setting"] == s[17]["setting"]
    assert all("why" not in b for b in res["briefs"].values())
    assert res["cost"] == {"library": 0, "new": 4, "credits_per_scene": 18, "credits": 72, "usd": 0.36}
    assert all(b["prompt"] == sp.assemble(b) for b in res["briefs"].values())


def test_malformed_json_is_retried_once():
    ctx, s = _ctx()
    calls = []

    def ask(prompt, images=None):
        calls.append(prompt)
        if len(calls) == 1:
            return "Sure! Here is the plan: {not json"
        return json.dumps({"briefs": [_raw(s[k]) for k in (16, 17, 18, 19)]})
    res = sp.plan_set(ctx, ask, {}, log=lambda *_: None)
    assert res["status"] == "ready" and "not valid JSON" in calls[1]


def test_never_passing_replies_stop_after_the_rounds_and_keep_the_best_set():
    ctx, s = _ctx()
    same = [dict(_raw(s[16]), slot=k) for k in (16, 17, 18, 19)]
    n = []

    def ask(prompt, images=None):
        n.append(1)
        return json.dumps({"briefs": same})
    res = sp.plan_set(ctx, ask, {"planner_rounds": 2}, log=lambda *_: None)
    assert len(n) == 3 and res["status"] == "needs_attention" and res["message"]
    assert res["check"]["failures"]


def test_planner_down_gives_a_failed_plan():
    from app.assistant import ChatUnavailable
    ctx, _ = _ctx()

    def ask(prompt, images=None):
        raise ChatUnavailable("The scene planner could not answer just now")
    res = sp.plan_set(ctx, ask, {}, log=lambda *_: None)
    assert res["status"] == "failed" and "could not answer" in res["message"]


# ---------- 11.8 library-first swap ----------

def test_library_swap_replaces_a_new_brief_when_it_fits_and_costs_drop():
    ctx, s = _ctx()
    cand = {"rel": "002_Ratio_2x3/005_Office/x/T.psd", "name": "T", "ratio": "3x4", "decor": "Modern", "desc": "",
            "meta": {"shot": "wide", "art_h_frac": 0.25, "camera_side": "left", "light_from": "left",
                     "presentation": "frame", "wall_lab": [70.0, -20.0, 5.0]}}
    clash = dict(cand, rel="clash.psd", meta=dict(cand["meta"], shot="medium"))
    ctx["open"][2]["library"] = [clash, cand]

    def ask(prompt, images=None):
        return json.dumps({"briefs": [_raw(s[k]) for k in (16, 17, 18, 19)]})
    res = sp.plan_set(ctx, ask, {}, log=lambda *_: None)
    b18 = res["briefs"]["18"]
    assert b18["source"] == "library" and b18["library_rel"] == cand["rel"]     # same shot (wide), unused
    assert res["cost"]["new"] == 3 and res["cost"]["credits"] == 54


def test_parse_accepts_fences_and_slot_dicts():
    assert set(sp.parse('noise ```json\n{"briefs": {"16": {"print_size": "5x7"}}}\n``` more')) == {16}
    with pytest.raises(ValueError):
        sp.parse("no json here")
    assert re.search(r"Return only the JSON object", sp.planner_prompt(_ctx()[0]))
