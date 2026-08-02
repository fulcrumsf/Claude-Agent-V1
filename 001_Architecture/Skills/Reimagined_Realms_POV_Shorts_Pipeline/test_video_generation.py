from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from video_generation import generate_video, trim_to_best_window


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


def test_trim_to_best_window_copies_unchanged_when_already_short_enough(tmp_path):
    video_path = tmp_path / "scene1.mp4"
    video_path.write_bytes(b"fake-video-data")
    output_path = tmp_path / "scene1_trimmed.mp4"

    probe_result = MagicMock(returncode=0, stdout="4.5\n", stderr="")

    with patch("video_generation.subprocess.run", return_value=probe_result) as mock_run:
        result = trim_to_best_window(video_path, output_path, target_seconds=5.0)

    assert result == output_path
    assert output_path.read_bytes() == b"fake-video-data"
    # Only ffprobe was called (to check duration) — no ffmpeg trim needed since 4.5s <= 5.0s
    assert mock_run.call_count == 1
    assert mock_run.call_args[0][0][0] == "ffprobe"


def test_trim_to_best_window_trims_middle_window_when_longer(tmp_path):
    video_path = tmp_path / "scene1.mp4"
    output_path = tmp_path / "scene1_trimmed.mp4"

    probe_result = MagicMock(returncode=0, stdout="9.0\n", stderr="")

    def fake_subprocess_run(cmd, **kwargs):
        if cmd[0] == "ffprobe":
            return probe_result
        # cmd[0] == "ffmpeg": simulate it writing the trimmed output file
        output_path.touch()
        return MagicMock(returncode=0)

    with patch("video_generation.subprocess.run", side_effect=fake_subprocess_run) as mock_run:
        result = trim_to_best_window(video_path, output_path, target_seconds=5.0)

    assert result == output_path
    assert mock_run.call_count == 2
    ffmpeg_call = mock_run.call_args_list[1][0][0]
    assert ffmpeg_call[0] == "ffmpeg"
    # duration=9.0, target=5.0 -> middle window starts at (9.0-5.0)/2 = 2.0s
    assert "-ss" in ffmpeg_call and ffmpeg_call[ffmpeg_call.index("-ss") + 1] == "2.0"
    assert "-t" in ffmpeg_call and ffmpeg_call[ffmpeg_call.index("-t") + 1] == "5.0"
