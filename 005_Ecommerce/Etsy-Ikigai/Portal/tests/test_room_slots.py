"""Room-slot planning (app/room_slots.py): Tony's picks first, art-to-room compatibility, popularity ratios."""
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
    for must in ("Camera angle: 3/4 corner", "no other frames", "No people", "No lamps", "onion-skin orange",
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
    t = rs.scene_prompt("Living room", "Modern", "2x3", presentation="frame")
    assert "black only occasionally" in t


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
