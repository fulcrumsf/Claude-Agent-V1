import json
import subprocess
from unittest.mock import patch, MagicMock
import pytest
from video_generation import submit_video_task, poll_video_task, download_video, generate_video, trim_to_best_window


def test_submit_video_task_calls_kie_cli_with_seedance_2_params_and_returns_task_id():
    mock_result = MagicMock(returncode=0, stdout=json.dumps({"task_id": "vid123"}))

    with patch("video_generation.subprocess.run", return_value=mock_result) as mock_run:
        result = submit_video_task(
            "POV walking down a dirt road. Sound: footsteps, birds. - No dialogue, no spoken words, no voiceover, no lip sync, no music, no on-screen text.",
            first_frame_url="https://example.com/scene_first_frame.png",
        )

    mock_run.assert_called_once_with(
        [
            "kie-cli", "bytedance_seedance_video",
            "--prompt", "POV walking down a dirt road. Sound: footsteps, birds. - No dialogue, no spoken words, no voiceover, no lip sync, no music, no on-screen text.",
            "--mode", "standard",
            "--duration", "5",
            "--resolution", "720p",
            "--aspect_ratio", "9:16",
            "--generate_audio", "true",
            "--json",
            "--first_frame_url", "https://example.com/scene_first_frame.png",
        ],
        check=True, capture_output=True, text=True,
    )
    assert result == "vid123"


def test_submit_video_task_raises_when_both_first_frame_and_reference_urls_given():
    with pytest.raises(ValueError, match="mutually exclusive"):
        submit_video_task(
            "a prompt",
            first_frame_url="https://example.com/scene_first_frame.png",
            reference_image_urls=["https://example.com/character_sheet.png"],
        )


def test_submit_video_task_accepts_reference_image_urls_alone():
    mock_result = MagicMock(returncode=0, stdout=json.dumps({"task_id": "vid123"}))

    with patch("video_generation.subprocess.run", return_value=mock_result) as mock_run:
        submit_video_task("a prompt", reference_image_urls=["https://example.com/character_sheet.png"])

    call_cmd = mock_run.call_args[0][0]
    assert "--reference_image_urls" in call_cmd
    assert "--first_frame_url" not in call_cmd


def test_submit_video_task_retries_on_transient_failure_then_succeeds():
    fail_result = MagicMock()
    success_result = MagicMock(returncode=0, stdout=json.dumps({"task_id": "vid123"}))

    call_error = subprocess.CalledProcessError(1, ["kie-cli"], output="", stderr="rate limited")

    with patch("video_generation.subprocess.run", side_effect=[call_error, success_result]) as mock_run, \
         patch("video_generation.time.sleep") as mock_sleep:
        result = submit_video_task("a prompt", first_frame_url="https://example.com/scene_first_frame.png")

    assert result == "vid123"
    assert mock_run.call_count == 2
    mock_sleep.assert_called_once()


def test_submit_video_task_raises_after_exhausting_retries():
    call_error = subprocess.CalledProcessError(1, ["kie-cli"], output="", stderr="rate limited")

    with patch("video_generation.subprocess.run", side_effect=call_error) as mock_run, \
         patch("video_generation.time.sleep"):
        with pytest.raises(subprocess.CalledProcessError):
            submit_video_task("a prompt", first_frame_url="https://example.com/scene_first_frame.png")

    assert mock_run.call_count == 3


def test_poll_video_task_returns_url_on_completion():
    completed_result = MagicMock(
        returncode=0,
        stdout=json.dumps({"status": "completed", "result_urls": ["https://example.com/scene1.mp4"]}),
    )

    with patch("video_generation.subprocess.run", return_value=completed_result) as mock_run, \
         patch("video_generation.time.sleep") as mock_sleep:
        result = poll_video_task("vid123", poll_interval_seconds=15.0, max_attempts=24)

    mock_run.assert_called_once_with(
        ["kie-cli", "get_task_status", "--task_id", "vid123", "--json"],
        check=True, capture_output=True, text=True,
    )
    mock_sleep.assert_not_called()
    assert result == "https://example.com/scene1.mp4"


def test_poll_video_task_accepts_raw_success_status():
    success_result = MagicMock(
        returncode=0,
        stdout=json.dumps({"status": "success", "result_urls": ["https://example.com/scene1.mp4"]}),
    )

    with patch("video_generation.subprocess.run", return_value=success_result), \
         patch("video_generation.time.sleep") as mock_sleep:
        result = poll_video_task("vid123")

    mock_sleep.assert_not_called()
    assert result == "https://example.com/scene1.mp4"


def test_poll_video_task_raises_on_failed_status():
    failed_result = MagicMock(
        returncode=0,
        stdout=json.dumps({"status": "failed", "result_urls": [], "error": "content policy violation"}),
    )

    with patch("video_generation.subprocess.run", return_value=failed_result), \
         patch("video_generation.time.sleep"):
        with pytest.raises(RuntimeError, match="content policy violation"):
            poll_video_task("vid123")


def test_poll_video_task_raises_timeout_after_max_attempts():
    generating_result = MagicMock(returncode=0, stdout=json.dumps({"status": "generating", "result_urls": []}))

    with patch("video_generation.subprocess.run", return_value=generating_result), \
         patch("video_generation.time.sleep"):
        with pytest.raises(TimeoutError):
            poll_video_task("vid123", poll_interval_seconds=1.0, max_attempts=2)


def test_download_video_writes_response_content_to_path(tmp_path):
    output_path = tmp_path / "scene1.mp4"
    mock_response = MagicMock(content=b"fake-mp4-bytes")
    mock_response.raise_for_status = MagicMock()

    with patch("video_generation.requests.get", return_value=mock_response) as mock_get:
        result = download_video("https://example.com/scene1.mp4", output_path)

    mock_get.assert_called_once_with("https://example.com/scene1.mp4", timeout=60)
    assert result == output_path
    assert output_path.read_bytes() == b"fake-mp4-bytes"


def test_generate_video_wires_submit_poll_download(tmp_path):
    output_path = tmp_path / "scene1.mp4"

    with patch("video_generation.submit_video_task", return_value="vid123") as mock_submit, \
         patch("video_generation.poll_video_task", return_value="https://example.com/scene1.mp4") as mock_poll, \
         patch("video_generation.download_video", return_value=output_path) as mock_download:
        result = generate_video("a prompt", output_path, first_frame_url="https://example.com/scene1_first_frame.png")

    mock_submit.assert_called_once_with(
        "a prompt", "https://example.com/scene1_first_frame.png", None, 5, "720p", "9:16",
    )
    mock_poll.assert_called_once_with("vid123")
    mock_download.assert_called_once_with("https://example.com/scene1.mp4", output_path)
    assert result == output_path


def test_submit_video_task_includes_first_frame_url_when_provided():
    mock_result = MagicMock(returncode=0, stdout=json.dumps({"task_id": "vid123"}))

    with patch("video_generation.subprocess.run", return_value=mock_result) as mock_run:
        submit_video_task("a prompt", first_frame_url="https://example.com/shot_02_panel.png")

    call_cmd = mock_run.call_args[0][0]
    assert "--first_frame_url" in call_cmd
    assert call_cmd[call_cmd.index("--first_frame_url") + 1] == "https://example.com/shot_02_panel.png"


def test_submit_video_task_omits_first_frame_url_when_not_provided():
    mock_result = MagicMock(returncode=0, stdout=json.dumps({"task_id": "vid123"}))

    with patch("video_generation.subprocess.run", return_value=mock_result) as mock_run:
        submit_video_task("a prompt", reference_image_urls=["https://example.com/character_sheet.png"])

    call_cmd = mock_run.call_args[0][0]
    assert "--first_frame_url" not in call_cmd


def test_generate_video_passes_first_frame_url_through(tmp_path):
    output_path = tmp_path / "scene1.mp4"

    with patch("video_generation.submit_video_task", return_value="vid123") as mock_submit, \
         patch("video_generation.poll_video_task", return_value="https://example.com/scene1.mp4"), \
         patch("video_generation.download_video", return_value=output_path):
        generate_video(
            "a prompt", output_path,
            first_frame_url="https://example.com/shot_02_panel.png",
        )

    mock_submit.assert_called_once_with(
        "a prompt", "https://example.com/shot_02_panel.png", None, 5, "720p", "9:16",
    )


def test_trim_to_best_window_copies_unchanged_when_already_short_enough(tmp_path):
    video_path = tmp_path / "scene1.mp4"
    video_path.write_bytes(b"fake-video-data")
    output_path = tmp_path / "scene1_trimmed.mp4"

    probe_result = MagicMock(returncode=0, stdout="4.5\n", stderr="")

    with patch("video_generation.subprocess.run", return_value=probe_result) as mock_run:
        result = trim_to_best_window(video_path, output_path, target_seconds=5.0)

    assert result == output_path
    assert output_path.read_bytes() == b"fake-video-data"
    assert mock_run.call_count == 1
    assert mock_run.call_args[0][0][0] == "ffprobe"


def test_trim_to_best_window_trims_middle_window_when_longer(tmp_path):
    video_path = tmp_path / "scene1.mp4"
    output_path = tmp_path / "scene1_trimmed.mp4"

    probe_result = MagicMock(returncode=0, stdout="9.0\n", stderr="")

    def fake_subprocess_run(cmd, **kwargs):
        if cmd[0] == "ffprobe":
            return probe_result
        output_path.touch()
        return MagicMock(returncode=0)

    with patch("video_generation.subprocess.run", side_effect=fake_subprocess_run) as mock_run:
        result = trim_to_best_window(video_path, output_path, target_seconds=5.0)

    assert result == output_path
    assert mock_run.call_count == 2
    ffmpeg_call = mock_run.call_args_list[1][0][0]
    assert ffmpeg_call[0] == "ffmpeg"
    assert "-ss" in ffmpeg_call and ffmpeg_call[ffmpeg_call.index("-ss") + 1] == "2.0"
    assert "-t" in ffmpeg_call and ffmpeg_call[ffmpeg_call.index("-t") + 1] == "5.0"
