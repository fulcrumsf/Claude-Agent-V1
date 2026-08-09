import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from text_overlay import (
    build_caption_props, write_props_file, ensure_public_symlink, render_text_overlay,
    measure_video_duration_seconds, REMOTION_PROJECT_DIR,
)

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


def test_build_caption_props_includes_duration_in_frames_when_provided():
    captions = [{"text": "TITLE", "start_s": 0, "duration_s": 4, "variant": "title"}]

    result = build_caption_props("Final_v1.mp4", captions, duration_in_frames=1579)

    assert result["durationInFrames"] == 1579


def test_build_caption_props_omits_duration_in_frames_when_not_provided():
    captions = [{"text": "TITLE", "start_s": 0, "duration_s": 4, "variant": "title"}]

    result = build_caption_props("Final_v1.mp4", captions)

    assert "durationInFrames" not in result


def test_measure_video_duration_seconds_parses_ffprobe_output(tmp_path):
    video_path = tmp_path / "Final_v1.mp4"
    mock_result = MagicMock(returncode=0, stdout="65.785075\n")

    with patch("text_overlay.subprocess.run", return_value=mock_result) as mock_run:
        result = measure_video_duration_seconds(video_path)

    mock_run.assert_called_once_with(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)],
        check=True, capture_output=True, text=True,
    )
    assert result == 65.785075


def test_write_props_file_writes_valid_json(tmp_path):
    props = {"backgroundVideoFile": "Final_v1.mp4", "captions": []}
    output_path = tmp_path / "props.json"

    result = write_props_file(props, output_path)

    assert result == output_path
    assert json.loads(output_path.read_text()) == props


def test_ensure_public_symlink_creates_symlink_when_missing(tmp_path):
    production_dir = tmp_path / "Productions" / "0003_Pyramid_Builder"
    production_dir.mkdir(parents=True)

    remotion_public_dir = tmp_path / "003_Remotion" / "public"
    remotion_public_dir.mkdir(parents=True)

    with patch("text_overlay.REMOTION_PUBLIC_DIR", remotion_public_dir):
        result = ensure_public_symlink(production_dir, "0003_pyramid_builder")

    expected_symlink = remotion_public_dir / "0003_pyramid_builder"
    assert result == expected_symlink
    assert expected_symlink.is_symlink()
    assert expected_symlink.resolve() == production_dir.resolve()


def test_ensure_public_symlink_leaves_existing_symlink_untouched(tmp_path):
    production_dir = tmp_path / "Productions" / "0003_Pyramid_Builder"
    production_dir.mkdir(parents=True)

    remotion_public_dir = tmp_path / "003_Remotion" / "public"
    remotion_public_dir.mkdir(parents=True)
    existing_symlink = remotion_public_dir / "0003_pyramid_builder"
    existing_symlink.symlink_to(production_dir)

    with patch("text_overlay.REMOTION_PUBLIC_DIR", remotion_public_dir):
        result = ensure_public_symlink(production_dir, "0003_pyramid_builder")

    assert result == existing_symlink
    assert existing_symlink.is_symlink()


def test_render_text_overlay_calls_remotion_cli(tmp_path):
    props_path = tmp_path / "props.json"
    output_path = tmp_path / "Final_v2.mp4"
    props_path.touch()

    mock_result = MagicMock(returncode=0)

    with patch("text_overlay.subprocess.run", return_value=mock_result) as mock_run:
        result = render_text_overlay(props_path, output_path)

    assert result == output_path
    mock_run.assert_called_once_with(
        ["npx", "remotion", "render", "POVShort", str(output_path), f"--props={props_path}", "--codec", "h264"],
        cwd=str(REMOTION_PROJECT_DIR),
        check=True, capture_output=True, text=True,
    )
