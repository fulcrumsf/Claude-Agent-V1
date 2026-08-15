# test_storyboard_generation.py
import json
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from storyboard_generation import (
    build_reference_sheet_note,
    build_panel_prompt,
    generate_storyboard_panel,
    generate_storyboard,
    compose_contact_sheet,
    main,
)


def test_build_reference_sheet_note_lists_labels():
    note = build_reference_sheet_note([
        "Main Character Sheet",
        "Ludus Interior Environment Sheet, panel labeled SCENE 3",
    ])

    assert "Main Character Sheet" in note
    assert "Ludus Interior Environment Sheet, panel labeled SCENE 3" in note
    assert "Reference images are attached in full, uncropped" in note


def test_build_reference_sheet_note_empty_when_no_labels():
    assert build_reference_sheet_note(None) == ""
    assert build_reference_sheet_note([]) == ""


def test_build_panel_prompt_includes_pov_lock_by_default():
    prompt = build_panel_prompt("Worker wakes up in a mud-brick hut")

    assert "their own face, the back of their own head, their own shoulder, or their own back" in prompt
    assert "Worker wakes up in a mud-brick hut" in prompt
    assert "No text, no numbers, no labels, no captions" in prompt


def test_build_panel_prompt_omits_pov_lock_when_disabled():
    prompt = build_panel_prompt("A detective enters a foggy crime scene", pov_lock=False)

    assert "their own face, the back of their own head, their own shoulder, or their own back" not in prompt
    assert "A detective enters a foggy crime scene" in prompt


def test_generate_storyboard_panel_calls_generate_image_with_9x16(tmp_path):
    output_path = tmp_path / "Panel_01.png"

    with patch("storyboard_generation.generate_image", return_value=output_path) as mock_generate:
        result = generate_storyboard_panel("Worker wakes up", output_path, resolution="2K")

    assert result == output_path
    call_args = mock_generate.call_args[0]
    assert "Worker wakes up" in call_args[0]
    assert call_args[1] == output_path
    assert call_args[2] == "9:16"
    assert call_args[3] == "2K"


def test_generate_storyboard_writes_one_panel_per_beat(tmp_path):
    beats = [
        {"index": 1, "description": "Worker wakes up"},
        {"index": 2, "description": "Worker eats breakfast"},
    ]

    with patch("storyboard_generation.generate_storyboard_panel") as mock_panel:
        mock_panel.side_effect = lambda desc, path, *a, **kw: Path(path)
        result = generate_storyboard(beats, tmp_path)

    assert result == [tmp_path / "Scenes" / "Panel_01.png", tmp_path / "Scenes" / "Panel_02.png"]
    assert mock_panel.call_count == 2


def test_generate_storyboard_creates_scenes_subfolder(tmp_path):
    beats = [{"index": 1, "description": "Worker wakes up"}]

    with patch("storyboard_generation.generate_storyboard_panel") as mock_panel:
        mock_panel.side_effect = lambda desc, path, *a, **kw: Path(path)
        generate_storyboard(beats, tmp_path)

    assert (tmp_path / "Scenes").is_dir()


def test_generate_storyboard_uses_per_beat_input_urls_and_sheet_labels(tmp_path):
    beats = [
        {"index": 1, "description": "Worker wakes up"},
        {
            "index": 2,
            "description": "Worker enters the Colosseum tunnel",
            "input_urls": ["https://example.com/colosseum_sheet.png"],
            "sheet_labels": ["Colosseum Environment Sheet, panel labeled SCENE 2"],
        },
    ]

    with patch("storyboard_generation.generate_storyboard_panel") as mock_panel:
        mock_panel.side_effect = lambda desc, path, *a, **kw: Path(path)
        generate_storyboard(beats, tmp_path, input_urls=["https://example.com/default_sheet.png"])

    first_call_args = mock_panel.call_args_list[0][0]
    second_call_args = mock_panel.call_args_list[1][0]
    assert first_call_args[4] == ["https://example.com/default_sheet.png"]
    assert first_call_args[5] is None
    assert second_call_args[4] == ["https://example.com/colosseum_sheet.png"]
    assert second_call_args[5] == ["Colosseum Environment Sheet, panel labeled SCENE 2"]


def test_compose_contact_sheet_raises_on_mismatched_lengths(tmp_path):
    panel = tmp_path / "Panel_01.png"
    Image.new("RGB", (10, 10)).save(panel)

    try:
        compose_contact_sheet([panel], ["one", "two"], tmp_path / "Contact_Sheet.png")
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_compose_contact_sheet_writes_grid_image(tmp_path):
    panel_paths = []
    for i in range(5):
        p = tmp_path / f"Panel_{i:02d}.png"
        Image.new("RGB", (100, 178), color=(i * 10, 0, 0)).save(p)
        panel_paths.append(p)
    captions = [f"Scene {i}: something happens" for i in range(5)]

    output_path = tmp_path / "Contact_Sheet.png"
    result = compose_contact_sheet(panel_paths, captions, output_path, columns=4)

    assert result == output_path
    assert output_path.exists()
    with Image.open(output_path) as sheet:
        # 5 panels at 4 columns -> 2 rows
        assert sheet.size[0] == 4 * 270
        assert sheet.size[1] == 2 * (int(270 * 16 / 9) + 50)


def test_main_generates_panels_and_contact_sheet(tmp_path):
    beats_json_path = tmp_path / "Beat_Table.json"
    beats = [
        {"index": 1, "description": "Worker wakes up"},
        {"index": 2, "description": "Worker eats breakfast"},
    ]
    beats_json_path.write_text(json.dumps(beats))
    out_dir = tmp_path / "storyboard"

    with patch("storyboard_generation.generate_storyboard") as mock_generate, \
         patch("storyboard_generation.compose_contact_sheet") as mock_compose:
        mock_generate.return_value = [out_dir / "Panel_01.png", out_dir / "Panel_02.png"]

        main(str(beats_json_path), str(out_dir))

    mock_generate.assert_called_once_with(beats, Path(str(out_dir)), True, "2K", None)
    mock_compose.assert_called_once()
    captions_arg = mock_compose.call_args[0][1]
    assert captions_arg == ["Scene 1: Worker wakes up", "Scene 2: Worker eats breakfast"]
