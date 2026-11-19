"""Room-slot planning (app/room_slots.py): Tony's picks first, art-to-room compatibility, popularity ratios."""
import pytest

from app import room_slots as rs

ALL = {r: list(rs.RATIOS) for r in rs.ETSY_ROOMS + rs.SCENE_ONLY_ROOMS if rs.ROOM_FOLDER.get(r)}
ALL.update({"Kids": ["iso"], "Nursery": ["iso"], "Creative space": ["iso"]})


def test_tony_picks_come_first_in_his_order_and_agent_fills_up_to_19():
    p = rs.plan(["Office", "Bedroom"], ["Mid Century"], "mid-century gouache goat among plum blossoms", "mid",
                available=ALL)
    # slot map 2026-11-10: rooms are slot 3 then 9-19 (4-8 are fixed images, never a room)
    assert [s["slot"] for s in p] == ([3] + list(range(9, 20)))[:len(p)] and len(p) <= 12
    assert not {s["slot"] for s in p} & {1, 2, 4, 5, 6, 7, 8, 20}
    assert [(s["room"], s["by"]) for s in p[:2]] == [("Office", "tony"), ("Bedroom", "tony")]
    assert all(s["by"] == "agent" for s in p[2:])
    assert p == rs.plan(["Office", "Bedroom"], ["Mid Century"], "mid-century gouache goat among plum blossoms", "mid",
                        available=ALL)                                  # deterministic


def test_only_etsy_rooms_and_at_most_five_picks_count():
    p = rs.plan(["Hallway", "Office", "Bedroom", "Bathroom", "Kids", "Dorm", "Laundry"], [], "x", available=ALL)
    tony = [s["room"] for s in p if s["by"] == "tony"]
    assert tony == ["Office", "Bedroom", "Bathroom", "Kids", "Dorm"]     # Hallway not on Etsy's list; max 5


def test_cyberpunk_art_never_goes_in_laundry_kitchen_or_nursery():
    p = rs.plan([], ["Game Room"], "neon cyberpunk tokyo gamer city at night", "dark", available=ALL)
    rooms = {s["room"] for s in p}
    assert "Game room" in rooms and not rooms & {"Laundry", "Kitchen & dining", "Nursery", "Kids", "Bathroom"}


def test_food_art_leads_with_kitchens_and_repeats_with_different_decor():
    p = rs.plan([], ["Food-Drink"], "coffee and lemons kitchen poster", "light", available=ALL)
    kitchens = [s for s in p if s["room"] == "Kitchen & dining"]
    assert p[0]["room"] == "Kitchen & dining" and len(kitchens) >= 2
    assert len({s["decor"] for s in kitchens}) == len(kitchens)          # same room, different look each time


def test_fewer_cards_rather_than_padding():
    # only two rooms have a template folder: the agent may not invent the others, so the plan is short
    p = rs.plan([], [], "a cat reading", "mid", available={"Living room": ["2x3"], "Bedroom": ["2x3"]})
    assert 0 < len(p) < 12 and {s["room"] for s in p} <= {"Living room", "Bedroom"}


def test_ratios_follow_popularity_and_folders():
    p = rs.plan([], ["Trendy"], "a cat reading a book", "mid", available=ALL)
    counts = {r: sum(s["ratio"] == r for s in p) for r in rs.RATIOS}
    assert counts["2x3"] >= counts["3x4"] >= counts["iso"] and counts["2x3"] >= counts["4x5"] >= counts["11x14"]
    assert all(s["ratio"] == "iso" for s in p if s["room"] in ("Kids", "Nursery"))   # only the ISO tree has that room
    assert rs.ratio_targets(12) == {"2x3": 4, "3x4": 3, "4x5": 3, "iso": 1, "11x14": 1}


def test_locked_slot_keeps_its_room_when_the_plan_changes():
    locked = {9: {"room": "Bathroom", "decor": "Minimal", "ratio": "3x4"}}
    p = rs.plan(["Living room"], [], "x", available=ALL, locked=locked)
    s9 = next(s for s in p if s["slot"] == 9)
    assert (s9["room"], s9["decor"], s9["ratio"], s9["locked"]) == ("Bathroom", "Minimal", "3x4", True)


def test_scene_prompt_follows_tonys_recipe_and_never_names_the_art():
    t = rs.scene_prompt("Bathroom", "Japandi", "iso", presentation="frame")
    assert t.startswith("Photorealistic japandi bathroom interior featuring one vertical piece of wall art (ISO ratio).")
    for must in ("Camera: ", "no other picture frames", "No people", "No lamps", "onion-skin orange",
                 "no mat, no matte border"):
        assert must in t
    assert "white insert" not in t


def test_presentations_mat_canvas_and_the_deterministic_pick():
    m = rs.scene_prompt("Living room", "Victorian", "2x3", presentation="mat")
    assert "WIDE off-white mat" in m and "onion-skin orange" in m
    c = rs.scene_prompt("Living room", "Boho", "4x5", presentation="canvas")
    assert "floater frame" in c and "never black or dark" in c and "stretched gallery canvas" in c
    picks = {rs.presentation_for("Living room", d, r) for d in rs.PRESENTATION_WEIGHTS for r in rs.RATIOS}
    assert picks == {"frame", "mat", "canvas"}
    assert rs.presentation_for("Living room", "Modern", "2x3") == rs.presentation_for("Living room", "Modern", "2x3")
    assert all(rs.presentation_for("Bedroom", "Victorian", r) != "canvas" for r in rs.RATIOS)
    assert all(rs.presentation_for("Kids", "Kids", r) != "mat" for r in rs.RATIOS)


def test_room_slots_are_3_and_9_to_19_and_tonys_picks_fill_3_9_10_11_12():
    assert rs.ROOM_SLOTS == [3, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19] and rs.room_slots({}) == rs.ROOM_SLOTS
    p = rs.plan(["Office", "Bedroom", "Bathroom", "Living room", "Dorm"], [], "x", available=ALL)
    assert [(s["slot"], s["by"]) for s in p[:5]] == [(3, "tony"), (9, "tony"), (10, "tony"), (11, "tony"), (12, "tony")]


def test_frame_prompt_uses_black_only_occasionally():
    # v1 looks keep the old wording; v2 picks the finish, black weighted at the market's 11% (rs.LOOK_AXES)
    v1 = rs.pick_look("Living room", "Modern", seed=3, version=1)
    assert "black only occasionally" in rs.scene_prompt("Living room", "Modern", "2x3", presentation="frame", look=v1)
    assert "black only occasionally" in rs.scene_prompt("Living room", "Modern", "2x3", presentation="frame",
                                                        look=rs.LOOK_AT_BUILD)
    w = rs.look_weights("Living room", "Unstyled", "frame_finish")
    assert w["black_frame"] < 0.25 and max(w, key=w.get) == "oak_frame"


def test_archive_template_moves_files_and_deletes_nothing(tmp_path, monkeypatch):
    import json
    from app import template_build as tb
    lib = tmp_path / "Lib"
    f = lib / "R" / "Room" / "Style"
    f.mkdir(parents=True)
    (f / "A.psd").write_bytes(b"x")
    (f / "A_Preview.png").write_bytes(b"y")
    (f / "template.json").write_text(json.dumps({"psd": "A.psd"}))
    monkeypatch.setattr(tb, "lib", lambda s=None: lib)
    r = tb.archive_template("R/Room/Style/A.psd")
    assert sorted(r["files"]) == ["A.psd", "A_Preview.png", "A_template.json"]
    assert [p.name for p in f.iterdir()] == ["Archive"] and len(list((f / "Archive").iterdir())) == 3


def test_canvas_side_edges_are_white_never_the_face_orange():
    """Tony 2026-11-17: orange side edges let SAM take face + side edge as one shape (art ran onto the side edge)."""
    c = rs.scene_prompt("Living room", "Japandi_Minimalist", "11x14", presentation="canvas")
    assert "Only the FRONT FACE of the canvas is orange" in c and "plain clean WHITE" in c
    assert "orange side edges" not in c and "never black" in c


def test_orange_surface_is_matte_evenly_lit_and_never_tints_its_surroundings():
    """Tony 2026-11-17: the blank bounced orange onto the gap / lip / side edges. Positive wording: dead matte, evenly
    lit, the orange only on the front face, every surface next to it keeps its own colour."""
    for kind in rs.PRESENTATIONS:
        t = rs.scene_prompt("Living room", "Japandi_Minimalist", "11x14", presentation=kind)
        for must in ("dead-matte, non-reflective finish", "one even tone from edge to edge",
                     "evenly lit across its whole face", "glare-free and free of hot spots",
                     "The orange appears only on the front face of the printed area",
                     "every surface next to it keeps its own natural colour"):
            assert must in t, (kind, must)
        assert "no glare, no reflection" not in t               # the old negation list is gone
    f = rs.scene_prompt("Living room", "Modern", "2x3", presentation="frame")
    m = rs.scene_prompt("Living room", "Victorian", "2x3", presentation="mat")
    c = rs.scene_prompt("Living room", "Boho", "4x5", presentation="canvas")
    assert "inner edge keeps the frame's own colour" in f and "museum glass" in f
    assert "mat and its bevel stay their own clean off-white" in m and "museum glass" in m
    assert "stay clean white in the light and neutral grey" in c and "neutral tones of the wood" in c
    assert "museum glass" not in c                               # a canvas has no glazing


def test_scene_light_is_not_forced_soft_only_the_art_surface_is_even():
    """Tony 2026-11-17: direct window light with soft-edged but clearly visible shadows is welcome (Bedroom Wabi);
    never ask for a flat or diffused scene, only the printed surface is evenly lit."""
    soft = rs.pick_look("Bedroom", "Japandi", seed=1, override={"light_style": "soft_direct"})
    for kind in rs.PRESENTATIONS:
        t = rs.scene_prompt("Bedroom", "Japandi", "3x4", presentation=kind, look=soft)
        assert "direct window light with soft-edged, clearly visible shadows" in t
        for light in rs.LOOK_AXES["light_style"]:              # no light style asks for a flat, diffused scene
            t = rs.scene_prompt("Bedroom", "Japandi", "3x4", presentation=kind,
                                look=rs.pick_look("Bedroom", "Japandi", seed=2, override={"light_style": light}))
            for gone in ("naturally diffused", "never harsh", "diffuse shadow", "only a soft, light"):
                assert gone not in t, (kind, light, gone)
    c = rs.scene_prompt("Living room", "Boho", "4x5", presentation="canvas")
    assert "follows the room's light direction" in c


# ---------- light and photographer variety (Tony 2026-11-17) ----------
ALL_ROOMS = list(rs.ROOM_WORDS)
ALL_DECORS = list(rs.DECOR_WORDS) + ["Japandi_Minimalist", "Wabi_Sabi", "Whatever_New_Style"]


def test_look_weights_are_respected_over_many_seeds():
    from collections import Counter
    n = 6000
    looks = [rs.pick_look("Living room", "Unstyled", seed=s) for s in range(n)]
    for axis in ("light_style", "photographer"):                   # picked first: unconditional (room gates only)
        want = rs.look_weights("Living room", "Unstyled", axis)
        got = Counter(lk[axis] for lk in looks)
        for k, p in want.items():
            assert abs(got[k] / n - p) < 0.03, (axis, k, got[k] / n, p)
    lightw = rs.look_weights("Living room", "Unstyled", "light_style")
    assert max(lightw, key=lightw.get) == "soft_direct" and lightw["soft_direct"] >= 0.3     # Tony's favourite
    # a later axis follows its conditional weights (here: time of day after a soft-direct light pick)
    sub = [lk for lk in looks if lk["light_style"] == "soft_direct"]
    want = rs.look_weights("Living room", "Unstyled", "time_of_day", {"light_style": "soft_direct"})
    got = Counter(lk["time_of_day"] for lk in sub)
    for k, p in want.items():
        assert abs(got[k] / len(sub) - p) < 0.05, (k, got[k] / len(sub), p)
    # every option of every axis that is not gated out for this room/decor shows up
    for axis, opts in rs.LOOK_AXES.items():
        assert {lk[axis] for lk in looks} == set(rs.look_weights("Living room", "Unstyled", axis)), axis


def test_look_is_deterministic_with_a_seed_random_without_and_replayable():
    a = rs.pick_look("Bedroom", "Japandi", seed=42)
    assert a == rs.pick_look("Bedroom", "Japandi", seed=42) and a["seed"] == 42 and a["version"] == rs.LOOK_VERSION
    assert rs.scene_prompt("Bedroom", "Japandi", "3x4", look=a) == rs.scene_prompt("Bedroom", "Japandi", "3x4", look=a)
    seeds = {rs.pick_look("Bedroom", "Japandi")["seed"] for _ in range(20)}
    assert len(seeds) > 15                                         # normal builds: genuinely random
    replay = rs.pick_look("Bedroom", "Japandi", override=a)        # a recorded look replays exactly
    assert all(replay[x] == a[x] for x in rs.LOOK_ORDER)
    one = rs.pick_look("Bedroom", "Japandi", seed=42, override={"photographer": "editorial_minimal"})
    assert one["photographer"] == "editorial_minimal" and one["overridden"] == ["photographer"]
    assert one["light_style"] == a["light_style"]                  # forcing one axis leaves the earlier draws alone
    with pytest.raises(ValueError):
        rs.pick_look("Bedroom", "Japandi", override={"light_style": "neon"})


def test_room_and_decor_nudges_never_zero_any_option():
    lo, hi = rs.LOOK_NUDGE_RANGE
    for room in ALL_ROOMS:
        for decor in ALL_DECORS:
            for axis, opts in rs.LOOK_AXES.items():
                w = rs.look_weights(room, decor, axis)              # no earlier picks: every ungated option open
                open_ = {k for k in opts if rs._look_gate(room, decor, axis, k)}
                assert set(w) == open_ and all(p > 0 for p in w.values()), (room, decor, axis)
                base = {k: v for k, v in rs.look_weights("Unstyled_Room", "Unstyled", axis).items() if k in open_}
                base = {k: v / sum(base.values()) for k, v in base.items()}   # same option set as w (gates)
                for k in open_ & set(base):   # nudges move the odds, within the clamp, and never remove an option
                    assert w[k] / base[k] > lo * lo * 0.9 and w[k] / base[k] < hi * hi * 1.1, (room, decor, k)
    for nudges in list(rs.LOOK_NUDGE_DECOR.values()) + list(rs.LOOK_NUDGE_ROOM.values()):
        assert all(m > 0 for m in nudges.values())
        assert all(any(k in opts for opts in rs.LOOK_AXES.values()) for k in nudges)    # no typo'd option names
    assert rs.look_weights("Living room", "Boho", "light_style")["dappled"] > \
        rs.look_weights("Living room", "Modern", "light_style")["dappled"]           # nudges do something


def test_look_combinations_make_physical_sense():
    for s in range(3000):
        lk = rs.pick_look("Living room", "Mid_Century", seed=s)
        if lk["light_style"] == "golden_low":
            assert lk["time_of_day"] in ("late_afternoon", "golden_hour")
        else:
            assert lk["time_of_day"] != "golden_hour"
        if lk["time_of_day"] == "late_afternoon" and lk["light_style"] == "golden_low":
            assert lk["season"] in ("autumn", "winter")
        if lk["light_style"] == "soft_even":
            assert lk["sun_direction"] != "facing_sun"
        else:
            assert lk["sun_direction"] != "away_from_sun"


def test_prompt_carries_the_picks_in_positive_words_and_the_guardrails_always():
    import re
    for s in range(300):
        lk = rs.pick_look("Living room", "Boho", seed=s)
        for kind in rs.PRESENTATIONS:
            t = rs.scene_prompt("Living room", "Boho", "4x5", presentation=kind, look=lk)
            assert rs.LOOK_AXES["light_style"][lk["light_style"]][1] in t
            assert rs.LOOK_AXES["photographer"][lk["photographer"]][1] in t
            assert rs.LOOK_AXES["time_of_day"][lk["time_of_day"]][1] in t
            assert rs.LOOK_AXES["sun_direction"][lk["sun_direction"]][1] in t
            assert any(p in t for p in rs.LOOK_AXES["season"][lk["season"]][1])
            for must in (rs.LOOK_GUARD.strip(), "evenly lit across its whole face", "one consistent direction",
                         "The orange appears only on the front face", "No people", "no other picture frames",
                         rs.LOOK_GUARD_FRAME.strip(),
                         rs.WAINSCOT_RULE):
                assert must in t, (s, kind, must)
            if kind == "canvas":
                assert "plain clean WHITE" in t and "never black or dark" in t
            if kind == "frame":
                assert rs.LOOK_AXES["frame_finish"][lk["frame_finish"]][1] in t
    look_words = " ".join(v[1] if isinstance(v[1], str) else " ".join(v[1])
                          for opts in rs.LOOK_AXES.values() for v in opts.values()) + rs.LOOK_GUARD
    assert not re.search(r"\b(no|not|never|without|avoid|don't)\b", look_words, re.I)   # positive wording only
    assert "people" not in look_words.lower() and "person" not in look_words.lower()


def test_gap_preview_says_the_look_is_picked_at_build_time():
    t = rs.scene_prompt("Bedroom", "Japandi", "2x3", look=rs.LOOK_AT_BUILD)
    assert "picked at random when Build this is clicked" in t and rs.LOOK_GUARD.strip() in t
    assert t.startswith("Photorealistic japandi bedroom interior")
