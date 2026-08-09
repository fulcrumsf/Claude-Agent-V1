# test_prop_sheet_generation.py
import json
from pathlib import Path
from unittest.mock import patch

from prop_sheet_generation import build_prop_sheet_prompt, generate_prop_sheet, main


def test_build_prop_sheet_prompt_includes_front_back_and_held_panels():
    props = [
        {
            "name": "Scutum Shield",
            "front": "curved rectangular shield, red field, bronze wing motif",
            "back": "wooden interior with a horizontal grip bar and forearm strap",
            "held_left": "gripped by a left forearm threaded through the strap, seen from behind",
        }
    ]
    prompt = build_prop_sheet_prompt(props)

    assert "Scutum Shield — Front:" in prompt
    assert "Scutum Shield — Back:" in prompt
    assert "Scutum Shield — Held from POV (Left Hand):" in prompt
    assert "no hands, no people" in prompt


def test_build_prop_sheet_prompt_omits_back_and_held_when_not_provided():
    props = [{"name": "Coin", "front": "a bronze Roman coin"}]
    prompt = build_prop_sheet_prompt(props)

    assert "Coin — Front:" in prompt
    assert "Coin — Back:" not in prompt
    assert "Coin — Held from POV (Left Hand):" not in prompt
    assert "Coin — Held from POV (Right Hand):" not in prompt


def test_build_prop_sheet_prompt_handles_multiple_props():
    props = [
        {"name": "Gladius Sword", "front": "a short sword", "held_right": "gripped in a right fist"},
        {"name": "Scutum Shield", "front": "a shield", "back": "the strap side"},
    ]
    prompt = build_prop_sheet_prompt(props)

    assert "Gladius Sword — Front:" in prompt
    assert "Gladius Sword — Held from POV (Right Hand):" in prompt
    assert "Scutum Shield — Front:" in prompt
    assert "Scutum Shield — Back:" in prompt


def test_build_prop_sheet_prompt_supports_both_hands_for_same_prop():
    props = [{"name": "Torch", "front": "a lit torch", "held_left": "gripped in left fist", "held_right": "gripped in right fist"}]
    prompt = build_prop_sheet_prompt(props)

    assert "Torch — Held from POV (Left Hand):" in prompt
    assert "Torch — Held from POV (Right Hand):" in prompt


def test_build_prop_sheet_prompt_reserves_label_margin():
    prompt = build_prop_sheet_prompt([{"name": "Sword", "front": "a blade"}])

    assert "the label must never overlap or cover any part of the panel's own image content" in prompt


def test_generate_prop_sheet_calls_generate_image_with_built_prompt(tmp_path):
    output_path = tmp_path / "prop_sheet.png"
    props = [{"name": "Sword", "front": "a blade"}]

    with patch("prop_sheet_generation.generate_image", return_value=output_path) as mock_generate:
        result = generate_prop_sheet(props, output_path, aspect_ratio="16:9", resolution="2K")

    assert result == output_path
    call_args = mock_generate.call_args[0]
    assert "Sword — Front:" in call_args[0]
    assert call_args[1] == output_path
    assert call_args[2] == "16:9"
    assert call_args[3] == "2K"


def test_generate_prop_sheet_passes_input_urls_through(tmp_path):
    output_path = tmp_path / "prop_sheet.png"
    props = [{"name": "Sword", "front": "a blade"}]

    with patch("prop_sheet_generation.generate_image", return_value=output_path) as mock_generate:
        generate_prop_sheet(props, output_path, input_urls=["https://example.com/main_character.png"])

    assert mock_generate.call_args[0][4] == ["https://example.com/main_character.png"]


def test_main_reads_props_json_and_wires_generate_prop_sheet(tmp_path):
    output_path = tmp_path / "prop_sheet.png"
    props_json_path = tmp_path / "Props.json"
    props = [{"name": "Sword", "front": "a blade"}]
    props_json_path.write_text(json.dumps(props))

    with patch("prop_sheet_generation.generate_prop_sheet") as mock_generate:
        mock_generate.return_value = output_path
        main(str(props_json_path), str(output_path), aspect_ratio="16:9", resolution="2K")

    mock_generate.assert_called_once_with(
        props, Path(str(output_path)), "16:9", "2K", None,
    )
