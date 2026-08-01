from beat_planning import scenes_needed_for_floor

def test_scenes_needed_for_floor_returns_zero_when_already_at_floor():
    # 13 scenes * 5s = 65s, exactly at floor
    assert scenes_needed_for_floor(13) == 0

def test_scenes_needed_for_floor_returns_zero_when_above_floor():
    # 14 scenes * 5s = 70s, above floor
    assert scenes_needed_for_floor(14) == 0

def test_scenes_needed_for_floor_returns_positive_count_when_below_floor():
    # 12 scenes * 5s = 60s, below the 65s floor -> need 1 more scene to reach 65s
    assert scenes_needed_for_floor(12) == 1

def test_scenes_needed_for_floor_respects_custom_params():
    # 10 scenes * 4s = 40s, floor 50s -> need 3 more scenes (13*4=52s >= 50s)
    assert scenes_needed_for_floor(10, seconds_per_scene=4.0, floor_seconds=50.0) == 3
