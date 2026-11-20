"""Scene look v2 (Tony 2026-11-19, app/room_slots.py): camera, lens, focus, foreground, display, composition, walls,
floor, furniture, frame finish and 12 photographer personas, from Research/Etsy_Mockup_Look_Findings.md. Checks the
weights, replay, v1 compatibility, the pipeline-safety rules and that '3/4 corner' only appears when picked."""
import hashlib
import random
import re
from collections import Counter

import pytest

from app import room_slots as rs

NEW_AXES = ("display", "camera_height", "camera_angle", "distance", "lens", "foreground", "depth_of_field",
            "composition", "wall_palette", "wall_treatment", "floor", "furniture_finish", "frame_finish")
ROOMS = list(rs.ROOM_WORDS)
DECORS = list(rs.DECOR_WORDS) + ["Japandi_Minimalist", "Wabi_Sabi", "Whatever_New_Style"]


def test_v2_has_every_research_axis_and_12_personas_under_the_old_key():
    assert rs.LOOK_VERSION == 2
    assert set(rs.LOOK_ORDER) == set(rs.LOOK_AXES) and len(rs.LOOK_ORDER) == len(set(rs.LOOK_ORDER))
    for a in NEW_AXES + ("light_style", "photographer", "time_of_day", "season", "sun_direction"):
        assert a in rs.LOOK_AXES, a
    assert len(rs.LOOK_AXES["photographer"]) == 12
    names = [k for opts in rs.LOOK_AXES.values() for k in opts]
    assert len(names) == len(set(names))                       # nudges key on option names: no clashes
    for table in (rs.PERSONA_NUDGE,):
        assert set(table) == set(rs.LOOK_AXES["photographer"])
        assert all(k in names for n in table.values() for k in n)
    assert rs.LOOK_AXES["lens"]["lens_short_tele"][0] <= 10    # telephoto never observed: rare, untested


def test_weights_follow_the_sqrt_flattening_rule():
    """weight = round(10*sqrt(p)) of the research blend (documented in room_slots); spot-check, plus exceptions."""
    blend = {("camera_angle", "straight_on"): 48, ("camera_angle", "three_quarter_left"): 7,
             ("camera_height", "low"): 32, ("distance", "close"): 35, ("display", "floor_lean"): 27,
             ("wall_palette", "warm_white"): 31, ("frame_finish", "oak_frame"): 48, ("frame_finish", "black_frame"): 11,
             ("lens", "lens_normal"): 75, ("depth_of_field", "deep_focus"): 78}
    for (axis, k), p in blend.items():
        assert rs.LOOK_AXES[axis][k][0] == round(10 * p ** 0.5), (axis, k)
    w = rs.look_weights("Living room", "Unstyled", "camera_angle")
    assert 0.2 < w["straight_on"] < 0.4 and w["three_quarter_left"] + w["three_quarter_right"] > 0.15


def test_sampled_frequencies_match_look_weights():
    n = 6000
    looks = [rs.pick_look("Living room", "Unstyled", seed=s) for s in range(n)]
    want = rs.look_weights("Living room", "Unstyled", "display", {"photographer": "warm_lifestyle_creator"})
    sub = [lk for lk in looks if lk["photographer"] == "warm_lifestyle_creator"]
    got = Counter(lk["display"] for lk in sub)
    for k, p in want.items():
        assert abs(got[k] / len(sub) - p) < 0.06, (k, got[k] / len(sub), p)
    # wall palette depends only on the persona among earlier picks
    sub = [lk for lk in looks if lk["photographer"] == "editorial_minimal"]
    want = rs.look_weights("Living room", "Unstyled", "wall_palette", {"photographer": "editorial_minimal"})
    got = Counter(lk["wall_palette"] for lk in sub)
    for k, p in want.items():
        assert abs(got[k] / len(sub) - p) < 0.07, (k, got[k] / len(sub), p)
    # the overall spread is real: no axis is a near-constant any more
    for axis in NEW_AXES:
        top = Counter(lk[axis] for lk in looks).most_common(1)[0][1] / n
        assert top < 0.75, (axis, top)
    assert Counter(lk["camera_angle"] for lk in looks)["straight_on"] / n < 0.4


def test_replay_from_saved_seed_and_override():
    a = rs.pick_look("Office", "Modern", seed=777)
    assert a == rs.pick_look("Office", "Modern", seed=777) and a["version"] == 2
    assert rs.pick_look("Office", "Modern", seed=a["seed"], override=a) == {**a, "overridden": sorted(rs.LOOK_ORDER)}
    p = rs.scene_prompt("Office", "Modern", "3x4", look=a)
    assert p == rs.scene_prompt("Office", "Modern", "3x4", look=rs.pick_look("Office", "Modern", seed=777))
    with pytest.raises(ValueError):
        rs.pick_look("Office", "Modern", override={"camera_angle": "dutch_tilt"})
    with pytest.raises(ValueError):
        rs.pick_look("Office", "Modern", seed=1, version=9)


# captured from the pre-v2 code (commit c4d18f2e) before the change: v1 looks must replay byte-identically
V1 = {("Bedroom", "Japandi", 42): ({"light_style": "dappled", "photographer": "magazine", "time_of_day": "morning",
                                    "season": "spring", "sun_direction": "side_window"},
                                   ["2319b79b7c3a29e32d11b21d3002404572250de4", "e8381e1272564cb9a674244aa5cfcdbc93eac78d",
                                    "c28b0dae4db2f724c1010a1da9b36e876fb30a3a", "5eb42ff123772fcacedca4644d76dadb5d9b65df"]),
      ("Office", "Modern", 123456): ({"light_style": "golden_low", "photographer": "lifestyle",
                                      "time_of_day": "late_afternoon", "season": "autumn",
                                      "sun_direction": "facing_sun"},
                                     ["f28ea3090e9b34917989e54010585b3201a3289c",
                                      "bf5b227e415e14d2c3c7a7eb8442bdf9f9b0124c",
                                      "bd0b41047e775cfee08a4fb637752ea2be0dfdc5",
                                      "d549ce0710a3c5aa149ee63887d15fc28b59b292"])}


def test_old_v1_looks_still_replay_exactly():
    for (room, decor, seed), (picks, hashes) in V1.items():
        saved = {"version": 1, "seed": seed, **picks}                          # as written in an old template.json
        assert rs.pick_look(room, decor, seed=seed, version=1) == saved          # seed-only replay
        replay = rs.pick_look(room, decor, seed=saved["seed"], override=saved)  # template_build.run's replay path
        assert {k: replay[k] for k in saved} == saved and replay["version"] == 1
        for kind, h in zip(("frame", "mat", "canvas", "canvas_bare"), hashes):
            t = rs.scene_prompt(room, decor, "3x4", presentation=kind, look=saved)
            assert hashlib.sha1(t.encode()).hexdigest() == h, kind
            assert "Camera angle: 3/4 corner" in t                              # v1's fixed angle, by design
    with pytest.raises(ValueError):                                             # v2 personas are not v1 options
        rs.pick_look("Bedroom", "Japandi", override={"version": 1, "photographer": "japandi_calm"})


# captured from the v2 code (commit 37a24938, 2026-11-19) BEFORE the slot-set planner was built: v2 looks and the
# Templates-tab preview must replay byte-identically (Slot_Set_Planner_Plan.md test 11.1). key -> (look sha1, prompt
# sha1 for frame, mat, canvas, canvas_bare)
V2 = {("Bedroom", "Japandi", "3x4", 42): ("d864bae37ff732bb4847c3d471070f767eb85383",
                                          ["9294be76002ea1d5c26ae89181e02f36234010cb",
                                           "36a4ab285568629e4ca04493bf097868592cc254",
                                           "c1186e57389c5e0e2aaea2076defafb28e1d8e1a",
                                           "065a5d03be0fadf8b4add05bbb9a9fd8b4ef091e"]),
      ("Office", "Modern", "2x3", 123456): ("f08ad1f77ae77ba29884b5b0245f84b2301ce88e",
                                            ["5b9309506bc7b4bf5e600fbe3853a082e435b5e8",
                                             "6f9e1f6048b6f4679deeae843186e4fe2d1c6599",
                                             "46888daeb302e74f9954fa7744e086af75e62994",
                                             "2334f18e7d0c99715899a6a9ccb874d907fab107"]),
      ("Living room", "Mid_Century", "4x5", 7): ("827b840395e47e43a123b7997fc0160a738241f2",
                                                 ["87466faf44dad462deb06897959ff400cc516ed4",
                                                  "eb5f745e3c012f0f7830ca70874c18b48ad6880b",
                                                  "dd56cd79dc65f8440cdb9182f616c413c34858b5",
                                                  "81411ae669e8e40a2b0ae54683321d470812e295"]),
      ("Kitchen & dining", "Rustic_Farmhouse", "iso", 99): ("412dbbc68b23a112a9c1ce27c6eacccd6a4dd2a8",
                                                            ["f511909dba507637ec7eec60b132e817e4da51bd",
                                                             "7e41734d83fcf270f109919d3cce3dc8b0524f0d",
                                                             "77039bd5e3ba7a78a803410ff6f66328cd69abfd",
                                                             "410a3a630c51362c7fdd081c5a46c9a7adee7be1"])}
V2_PREVIEW = "c4c1a8aa016ced51af463d02326c3d7e70bcfc31"     # scene_prompt(Living room, Modern, 2x3, LOOK_AT_BUILD)
V2_PRESENTATIONS = ['frame', 'frame', 'mat', 'mat', 'mat', 'frame', 'canvas', 'canvas', 'frame', 'frame', 'canvas',
                    'canvas', 'frame', 'canvas', 'canvas', 'canvas', 'frame', 'mat', 'frame', 'mat']


def test_v2_looks_and_prompts_replay_byte_identically():
    for (room, decor, ratio, seed), (look_h, hashes) in V2.items():
        lk = rs.pick_look(room, decor, seed=seed)
        assert hashlib.sha1(repr(sorted(lk.items())).encode()).hexdigest() == look_h, (room, decor)
        replay = rs.pick_look(room, decor, seed=lk["seed"], override=lk)
        for kind, h in zip(("frame", "mat", "canvas", "canvas_bare"), hashes):
            for look in (lk, replay):
                t = rs.scene_prompt(room, decor, ratio, presentation=kind, look=look)
                assert hashlib.sha1(t.encode()).hexdigest() == h, (room, kind)
    t = rs.scene_prompt("Living room", "Modern", "2x3", look=rs.LOOK_AT_BUILD)
    assert hashlib.sha1(t.encode()).hexdigest() == V2_PREVIEW
    assert [rs.presentation_for(r, d, q) for r in ("Bedroom", "Office") for d in ("Japandi", "Modern")
            for q in rs.RATIOS] == V2_PRESENTATIONS


def test_live_templates_replay_their_saved_prompt():
    """Every live template with a saved look (v1 or v2) gives back exactly its saved prompt (test 11.2)."""
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parents[2] / "Room_Templates" / "Portrait_Templates"
    files = [f for f in root.glob("**/template.json") if "Archive" not in f.parts] if root.is_dir() else []
    looks = [(f, json.loads(f.read_text())) for f in files]
    looks = [(f, m) for f, m in looks if m.get("look")]
    if not looks:
        pytest.skip("no live template library here")
    for f, m in looks:
        lk = rs.pick_look(m["room"], m["decor"], seed=m["look"]["seed"], override=m["look"])
        kinds = ("canvas", "canvas_bare") if m.get("presentation") == "canvas" else (m.get("presentation") or "frame",)
        assert any(rs.scene_prompt(m["room"], m["decor"], m["ratio"], presentation=k, look=lk) == m["prompt"]
                   for k in kinds), f.parent.name


def _problems(lk, room, decor):
    """Independent restatement of the hard rules (not reusing _look_fits)."""
    bad = []
    d, h, a, dist = lk["display"], lk["camera_height"], lk["camera_angle"], lk["distance"]
    wall, frame = lk["wall_palette"], lk["frame_finish"]
    if d == "floor_lean" and h == "counter": bad.append("floor lean at counter height")
    if h == "counter" and d not in ("lean_on_furniture", "hung_over_furniture"): bad.append("counter w/o furniture")
    if h == "low" and d in ("hung_over_furniture", "hung_bare_wall") and dist == "close": bad.append("low+close hung")
    if a == "through_doorway" and (dist == "close" or lk["composition"] != "centred"
                                   or lk["foreground"] != "clear_foreground"): bad.append("doorway")
    if lk["wall_treatment"] == "panelled" and d not in ("hung_over_furniture", "hung_bare_wall"):
        bad.append("panelling behind a leaning frame")
    if lk["foreground"] == "throw_or_rug" and d == "floor_lean": bad.append("rug into frame")
    if lk["depth_of_field"] == "soft_foreground" and lk["foreground"] == "clear_foreground": bad.append("soft fg")
    if lk["depth_of_field"] == "soft_background" and (a in ("straight_on", "through_doorway") or dist == "close"):
        bad.append("soft bg on the art wall")
    if lk["composition"] == "offset_furniture" and d not in ("hung_over_furniture", "lean_on_furniture"):
        bad.append("offset w/o furniture")
    if lk["composition"] == "beside_window" and lk["sun_direction"] == "facing_sun": bad.append("window")
    if lk["lens"] == "lens_wide" and dist == "close": bad.append("wide lens close")
    if lk["lens"] == "lens_short_tele" and dist == "wide": bad.append("tele wide")
    if wall == "blush" and frame not in ("black_frame", "walnut_frame"): bad.append("blush frame")
    pale = wall in ("ivory_cream", "greige", "blush") or (wall == "warm_white" and lk["wall_treatment"] == "limewash")
    if frame == "oak_frame" and pale: bad.append("oak on pale warm wall")
    if frame == "white_frame" and wall in ("warm_white", "ivory_cream", "soft_grey"): bad.append("white on white")
    if frame in ("black_frame", "walnut_frame") and wall == "deep_moody": bad.append("dark on dark")
    if lk["photographer"] == "playful_nursery" and room not in ("Kids", "Nursery"): bad.append("nursery persona")
    if lk["photographer"] == "trendy_girl_apartment" and room == "Office": bad.append("trendy office")
    if frame == "gold_frame" and not any(rs.decor_matches(x, decor) for x in rs._VINTAGE_DECORS):
        bad.append("gold outside vintage")
    if lk["light_style"] == "golden_low" and lk["time_of_day"] not in ("late_afternoon", "golden_hour"):
        bad.append("golden light at the wrong time")
    return bad


def test_no_forbidden_combination_in_2000_random_picks():
    rng = random.Random(2026)
    forbidden_walls = re.compile(r"\b(orange|peach\w*|apricot|terracotta|coral|rust)\b", re.I)
    for i in range(2000):
        room, decor, ratio = rng.choice(ROOMS), rng.choice(DECORS), rng.choice(rs.RATIOS)
        lk = rs.pick_look(room, decor, seed=rng.randrange(2 ** 32))
        assert not _problems(lk, room, decor), (room, decor, lk, _problems(lk, room, decor))
        assert not forbidden_walls.search(rs.look_text(lk, room)), lk           # look words never name orange tones
        kind = rng.choice(("frame", "mat", "canvas", "canvas_bare"))
        t = rs.scene_prompt(room, decor, ratio, presentation=kind, look=lk)
        assert ("3/4 corner" in t) == lk["camera_angle"].startswith("three_quarter"), (lk["camera_angle"], kind)
        assert "slight 3/4 view" not in t
        for must in (rs.LOOK_GUARD.strip(), rs.LOOK_GUARD_FRAME.strip(), rs.WAINSCOT_RULE,
                     "evenly lit across its whole face", "dead-matte"):
            assert must in t, must
        if lk["display"] in ("floor_lean", "lean_on_furniture"):                 # no hung-art wording on a lean
            for gone in ("hangs in a", "hung directly on the wall", "stands off the wall", "hangs on the wall"):
                assert gone not in t, (gone, kind)
        if kind in ("frame", "mat"):
            assert rs.LOOK_AXES["frame_finish"][lk["frame_finish"]][1] in t
        else:                                                                    # canvas keeps its own floater/no frame
            assert rs.LOOK_AXES["frame_finish"][lk["frame_finish"]][1] not in t and "mat border" not in t
        if kind == "canvas" and (lk["wall_palette"] in ("ivory_cream", "greige", "blush") or
                                 (lk["wall_palette"] == "warm_white" and lk["wall_treatment"] == "limewash")):
            assert "clearly darker than the wall" in t
        if kind == "frame":
            assert "no mat, no matte border" in t


def test_new_phrases_are_positive_and_props_trio_is_gone():
    words = " ".join(v[1] for a in NEW_AXES for v in rs.LOOK_AXES[a].values()) + " ".join(
        v[1] for v in rs.LOOK_AXES["photographer"].values()) + rs.LOOK_GUARD_FRAME
    assert not re.search(r"\b(no|not|never|without|avoid|don't)\b", words, re.I)
    assert not re.search(r"\blamps?\b", words, re.I)                             # standing no-random-lamps rule
    assert "a throw casually draped, a book left open, a cup" not in words
    assert "3/4 corner" not in rs.scene_prompt("Living room", "Modern", "2x3", look=rs.LOOK_AT_BUILD)


def test_gates_and_nudges_steer_by_room_and_decor():
    assert "playful_nursery" in rs.look_weights("Nursery", "Kids", "photographer")
    assert "playful_nursery" not in rs.look_weights("Living room", "Modern", "photographer")
    assert set(rs.look_weights("Game room", "Gamer", "photographer")) == set(rs._GAMER_PERSONAS)
    assert "gold_frame" in rs.look_weights("Living room", "Victorian", "frame_finish")
    assert "gold_frame" not in rs.look_weights("Living room", "Gamer", "frame_finish")
    assert rs.look_weights("Living room", "Mid_Century", "photographer")["midcentury_magazine"] > \
        rs.look_weights("Living room", "Modern", "photographer")["midcentury_magazine"]
    assert rs.look_weights("Kitchen & dining", "Modern", "camera_height")["counter"] > \
        rs.look_weights("Living room", "Modern", "camera_height")["counter"]
