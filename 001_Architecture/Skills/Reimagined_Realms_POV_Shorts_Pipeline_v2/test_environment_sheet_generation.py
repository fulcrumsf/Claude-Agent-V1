# test_environment_sheet_generation.py
import json
from pathlib import Path
from unittest.mock import patch

from environment_sheet_generation import build_environment_sheet_prompt, generate_environment_sheet, main


def test_build_environment_sheet_prompt_labels_one_panel_per_scene():
    scene_angles = [
        {"scene": 1, "description": "POV lying on the cot looking toward the door"},
        {"scene": 2, "description": "POV sitting on the cot looking toward the opposite wall"},
    ]
    prompt = build_environment_sheet_prompt("a gladiator ludus cell", scene_angles)

    assert "a gladiator ludus cell" in prompt
    assert "SCENE 1: POV lying on the cot looking toward the door" in prompt
    assert "SCENE 2: POV sitting on the cot looking toward the opposite wall" in prompt
    assert "2 panels" in prompt


def test_build_environment_sheet_prompt_enforces_people_less_and_no_reuse():
    prompt = build_environment_sheet_prompt("a corridor", [{"scene": 1, "description": "walking forward"}])

    assert "NO people, NO hands, NO arms" in prompt
    assert "No panel may reuse another panel's exact framing" in prompt


def test_build_environment_sheet_prompt_reserves_label_margin():
    prompt = build_environment_sheet_prompt("a corridor", [{"scene": 1, "description": "walking forward"}])

    assert "the label must never overlap or cover any part of the panel's own image content" in prompt


def test_generate_environment_sheet_calls_generate_image_with_built_prompt(tmp_path):
    output_path = tmp_path / "environment_sheet.png"
    scene_angles = [{"scene": 1, "description": "an empty corridor"}]

    with patch("environment_sheet_generation.generate_image", return_value=output_path) as mock_generate:
        result = generate_environment_sheet(
            "ludus corridor", scene_angles, output_path,
            aspect_ratio="16:9", resolution="4K",
        )

    assert result == output_path
    call_args = mock_generate.call_args[0]
    assert "SCENE 1: an empty corridor" in call_args[0]
    assert call_args[1] == output_path
    assert call_args[2] == "16:9"
    assert call_args[3] == "4K"


def test_generate_environment_sheet_passes_input_urls_through(tmp_path):
    output_path = tmp_path / "environment_sheet.png"
    scene_angles = [{"scene": 1, "description": "an empty room"}]

    with patch("environment_sheet_generation.generate_image", return_value=output_path) as mock_generate:
        generate_environment_sheet(
            "a room", scene_angles, output_path,
            input_urls=["https://example.com/ref1.png"],
        )

    assert mock_generate.call_args[0][4] == ["https://example.com/ref1.png"]


def test_main_reads_location_json_and_wires_generate_environment_sheet(tmp_path):
    output_path = tmp_path / "environment_sheet.png"
    location_json_path = tmp_path / "Location.json"
    data = {
        "location": "ludus cell",
        "scenes": [{"scene": 1, "description": "lying on the cot"}],
    }
    location_json_path.write_text(json.dumps(data))

    with patch("environment_sheet_generation.generate_environment_sheet") as mock_generate:
        mock_generate.return_value = output_path
        main(str(location_json_path), str(output_path), aspect_ratio="16:9", resolution="4K")

    mock_generate.assert_called_once_with(
        "ludus cell", data["scenes"], Path(str(output_path)), "16:9", "4K", None,
    )
