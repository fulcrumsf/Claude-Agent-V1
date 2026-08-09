import pytest

from beat_planning import scenes_needed_for_floor, write_beat_table

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

def test_scenes_needed_for_floor_raises_on_non_positive_seconds_per_scene():
    with pytest.raises(ValueError):
        scenes_needed_for_floor(10, seconds_per_scene=0)

def test_write_beat_table_creates_data_folder_and_json(tmp_path):
    beats = [
        {"index": 1, "description": "Waking up in a rustic hut, dawn light.", "camera_fixed": True},
        {"index": 2, "description": "Walking down a dirt road carrying a water bucket.", "camera_fixed": False},
    ]

    result_path = write_beat_table(tmp_path, beats)

    assert result_path == tmp_path / "Data" / "Beat_Table.json"
    assert result_path.exists()

    import json
    saved = json.loads(result_path.read_text())
    assert saved == beats
