from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from video_generation import generate_video


def test_generate_video_calls_wavespeed_with_seedance_params(tmp_path):
    output_path = tmp_path / "scene1.mp4"
    mock_result = MagicMock(returncode=0)

    with patch("video_generation.subprocess.run", return_value=mock_result) as mock_run:
        output_path.touch()  # simulate wavespeed writing directly to the requested path
        result = generate_video(
            "https://example.com/scene1.png",
            "POV walking down a dirt road. Sound: footsteps, birds. - No dialogue, no spoken words, no voiceover, no lip sync, no music, no on-screen text.",
            output_path,
        )

    mock_run.assert_called_once_with(
        [
            "wavespeed", "run", "bytedance/seedance-v1.5-pro/image-to-video",
            "-i", "image=https://example.com/scene1.png",
            "-i", "prompt=POV walking down a dirt road. Sound: footsteps, birds. - No dialogue, no spoken words, no voiceover, no lip sync, no music, no on-screen text.",
            "-i", "duration=5",
            "-i", "resolution=1080p",
            "-i", "aspect_ratio=9:16",
            "-i", "generate_audio=true",
            "--download", str(output_path),
        ],
        check=True, capture_output=True, text=True,
    )
    assert result == output_path


def test_generate_video_normalizes_multi_output_download(tmp_path):
    output_path = tmp_path / "scene1.mp4"
    candidate_1 = tmp_path / "scene1-1.mp4"
    candidate_2 = tmp_path / "scene1-2.mp4"

    def fake_wavespeed_run(*args, **kwargs):
        candidate_1.write_bytes(b"candidate-one")
        candidate_2.write_bytes(b"candidate-two")
        return MagicMock(returncode=0)

    with patch("video_generation.subprocess.run", side_effect=fake_wavespeed_run):
        result = generate_video("https://example.com/scene1.png", "a prompt", output_path)

    assert result == output_path
    assert output_path.exists()
    assert output_path.read_bytes() == b"candidate-one"
    assert not candidate_2.exists()


def test_generate_video_raises_when_no_output_found(tmp_path):
    output_path = tmp_path / "scene1.mp4"

    with patch("video_generation.subprocess.run", return_value=MagicMock(returncode=0)):
        with pytest.raises(FileNotFoundError):
            generate_video("https://example.com/scene1.png", "a prompt", output_path)
