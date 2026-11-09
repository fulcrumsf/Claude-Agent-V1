"""Room-slot planning (app/room_slots.py): Tony's picks first, art-to-room compatibility, popularity ratios."""
from app import room_slots as rs

ALL = {r: list(rs.RATIOS) for r in rs.ETSY_ROOMS + rs.SCENE_ONLY_ROOMS if rs.ROOM_FOLDER.get(r)}
ALL.update({"Kids": ["iso"], "Nursery": ["iso"], "Creative space": ["iso"]})


def test_tony_picks_come_first_in_his_order_and_agent_fills_up_to_19():
    p = rs.plan(["Office", "Bedroom"], ["Mid Century"], "mid-century gouache goat among plum blossoms", "mid",
                available=ALL)
    assert [s["slot"] for s in p] == list(range(8, 8 + len(p))) and len(p) <= 12
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
    t = rs.scene_prompt("Bathroom", "Japandi", "iso")
    assert t.startswith("Photorealistic japandi bathroom interior featuring one vertical picture frame with a blank "
                        "white insert (ISO ratio).")
    for must in ("Camera angle: 3/4 corner", "no other frames", "No people", "No lamps"):
        assert must in t
