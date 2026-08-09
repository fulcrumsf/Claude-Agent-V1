# test_character_sheet_generation.py
from pathlib import Path
from unittest.mock import patch

from character_sheet_generation import build_character_sheet_prompt, generate_character_sheet, main


def test_build_character_sheet_prompt_includes_description_and_grid_structure():
    prompt = build_character_sheet_prompt("muscular Egyptian laborer, olive skin, shaved head")

    assert "muscular Egyptian laborer, olive skin, shaved head" in prompt
    assert "front view" in prompt
    assert "hands and forearms" in prompt
    assert "consistency reference" in prompt


def test_generate_character_sheet_calls_generate_image_with_built_prompt(tmp_path):
    output_path = tmp_path / "character_sheet.png"

    with patch("character_sheet_generation.generate_image", return_value=output_path) as mock_generate:
        result = generate_character_sheet(
            "muscular Egyptian laborer, olive skin, shaved head", output_path,
            aspect_ratio="1:1", resolution="2K",
        )

    assert result == output_path
    call_args = mock_generate.call_args[0]
    assert "muscular Egyptian laborer, olive skin, shaved head" in call_args[0]
    assert call_args[1] == output_path
    assert call_args[2] == "1:1"
    assert call_args[3] == "2K"


def test_generate_character_sheet_passes_input_urls_through(tmp_path):
    output_path = tmp_path / "character_sheet.png"

    with patch("character_sheet_generation.generate_image", return_value=output_path) as mock_generate:
        generate_character_sheet(
            "muscular Egyptian laborer", output_path,
            input_urls=["https://example.com/ref1.png"],
        )

    assert mock_generate.call_args[0][4] == ["https://example.com/ref1.png"]


def test_build_character_sheet_prompt_includes_role_for_background_character():
    prompt = build_character_sheet_prompt("wiry older dockworker", role="a background worker")

    assert "a background worker" in prompt
    assert "wiry older dockworker" in prompt


def test_generate_character_sheet_passes_role_into_prompt(tmp_path):
    output_path = tmp_path / "background_worker_sheet.png"

    with patch("character_sheet_generation.generate_image", return_value=output_path) as mock_generate:
        generate_character_sheet(
            "wiry older dockworker", output_path, role="a background worker",
        )

    assert "a background worker" in mock_generate.call_args[0][0]


def test_main_wires_generate_character_sheet(tmp_path):
    output_path = tmp_path / "character_sheet.png"
    with patch("character_sheet_generation.generate_character_sheet") as mock_generate:
        mock_generate.return_value = output_path
        main("muscular Egyptian laborer", str(output_path), aspect_ratio="1:1", resolution="2K")

    mock_generate.assert_called_once_with(
        "muscular Egyptian laborer", Path(str(output_path)), "the main character", "1:1", "2K", None,
    )
