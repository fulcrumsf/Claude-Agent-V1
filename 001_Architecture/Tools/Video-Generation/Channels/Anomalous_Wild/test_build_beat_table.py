from build_beat_table import build_beat_table

def test_live_footage_beat_gets_8s_cap():
    words = [{"word": "hello", "start_s": 0.0, "end_s": 9.5}]
    beats = build_beat_table([{"scene_id": "scene_01", "words": words, "routing": "live_footage"}])
    assert beats[0]["routing"] == "live_footage"
    assert beats[0]["max_clip_s"] == 8.0

def test_diagram_beat_has_no_length_cap_but_has_static_rule():
    words = [{"word": "worm", "start_s": 0.0, "end_s": 16.2}]
    beats = build_beat_table([{"scene_id": "scene_04", "words": words, "routing": "diagram"}])
    assert beats[0]["max_clip_s"] is None
    assert beats[0]["max_static_s"] == 5.0

def test_beat_start_end_derived_from_words():
    words = [{"word": "a", "start_s": 1.0, "end_s": 1.2}, {"word": "b", "start_s": 1.2, "end_s": 3.4}]
    beats = build_beat_table([{"scene_id": "scene_02", "words": words, "routing": "diagram"}])
    assert beats[0]["start_s"] == 1.0
    assert beats[0]["end_s"] == 3.4
