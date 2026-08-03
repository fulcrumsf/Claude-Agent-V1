import json
from pathlib import Path
from text_overlay import build_caption_props, write_props_file

def test_build_caption_props_converts_snake_case_to_camel_case():
    captions = [
        {"text": "POV: WAKING UP AS A PYRAMID BUILDER", "start_s": 0, "duration_s": 4, "variant": "title"},
        {"text": "FETCHING WATER", "start_s": 4, "duration_s": 5, "variant": "label"},
    ]

    result = build_caption_props("Final_v1.mp4", captions, fps=24)

    assert result == {
        "backgroundVideoFile": "Final_v1.mp4",
        "captions": [
            {"text": "POV: WAKING UP AS A PYRAMID BUILDER", "startS": 0, "durationS": 4, "variant": "title"},
            {"text": "FETCHING WATER", "startS": 4, "durationS": 5, "variant": "label"},
        ],
    }


def test_write_props_file_writes_valid_json(tmp_path):
    props = {"backgroundVideoFile": "Final_v1.mp4", "captions": []}
    output_path = tmp_path / "props.json"

    result = write_props_file(props, output_path)

    assert result == output_path
    assert json.loads(output_path.read_text()) == props
