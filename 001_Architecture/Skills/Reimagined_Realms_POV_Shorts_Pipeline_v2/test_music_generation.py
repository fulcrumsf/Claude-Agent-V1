import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from music_generation import submit_music_task, poll_music_task, download_music, generate_music, fit_music_to_duration

def test_submit_music_task_calls_kie_cli_and_returns_task_id():
    mock_result = MagicMock(
        returncode=0,
        stdout=json.dumps({"success": True, "task_id": "music123", "message": "Music generation task created successfully"}),
    )

    with patch("music_generation.subprocess.run", return_value=mock_result) as mock_run:
        result = submit_music_task("gentle medieval folk ambient instrumental", instrumental=True, model="V4_5")

    mock_run.assert_called_once_with(
        [
            "kie-cli", "suno_generate_music",
            "--prompt", "gentle medieval folk ambient instrumental",
            "--customMode", "false",
            "--instrumental", "true",
            "--model", "V4_5",
            "--json",
        ],
        check=True, capture_output=True, text=True,
    )
    assert result == "music123"


def test_poll_music_task_returns_first_url_on_uppercase_success_status():
    # Real kie-cli Suno output uses "SUCCESS" (uppercase) — different casing than
    # image generation's "success". Comparison must be case-insensitive.
    completed_result = MagicMock(
        returncode=0,
        stdout=json.dumps({
            "status": "SUCCESS",
            "result_urls": ["https://example.com/track1.mp3", "https://example.com/track2.mp3"],
        }),
    )

    with patch("music_generation.subprocess.run", return_value=completed_result) as mock_run, \
         patch("music_generation.time.sleep") as mock_sleep:
        result = poll_music_task("music123", poll_interval_seconds=20.0, max_attempts=12)

    mock_run.assert_called_once_with(
        ["kie-cli", "get_task_status", "--task_id", "music123", "--json"],
        check=True, capture_output=True, text=True,
    )
    mock_sleep.assert_not_called()
    assert result == "https://example.com/track1.mp3"


def test_poll_music_task_raises_on_lowercase_fail_status():
    failed_result = MagicMock(
        returncode=0,
        stdout=json.dumps({"status": "fail", "result_urls": [], "error": "generation error"}),
    )

    with patch("music_generation.subprocess.run", return_value=failed_result), \
         patch("music_generation.time.sleep"):
        import pytest
        with pytest.raises(RuntimeError, match="generation error"):
            poll_music_task("music123", poll_interval_seconds=20.0, max_attempts=12)


def test_poll_music_task_raises_timeout_after_max_attempts():
    generating_result = MagicMock(returncode=0, stdout=json.dumps({"status": "PENDING", "result_urls": []}))

    with patch("music_generation.subprocess.run", return_value=generating_result), \
         patch("music_generation.time.sleep"):
        import pytest
        with pytest.raises(TimeoutError):
            poll_music_task("music123", poll_interval_seconds=20.0, max_attempts=3)


def test_download_music_writes_response_content(tmp_path):
    output_path = tmp_path / "Music_Full.mp3"
    mock_response = MagicMock(content=b"fake-mp3-bytes")
    mock_response.raise_for_status = MagicMock()

    with patch("music_generation.requests.get", return_value=mock_response) as mock_get:
        result = download_music("https://example.com/track1.mp3", output_path)

    mock_get.assert_called_once_with("https://example.com/track1.mp3", timeout=60)
    assert result == output_path
    assert output_path.read_bytes() == b"fake-mp3-bytes"


def test_generate_music_wires_submit_poll_download(tmp_path):
    output_path = tmp_path / "Music_Full.mp3"

    with patch("music_generation.submit_music_task", return_value="music123") as mock_submit, \
         patch("music_generation.poll_music_task", return_value="https://example.com/track1.mp3") as mock_poll, \
         patch("music_generation.download_music", return_value=output_path) as mock_download:
        result = generate_music("gentle medieval folk ambient instrumental", output_path, instrumental=True, model="V4_5")

    mock_submit.assert_called_once_with("gentle medieval folk ambient instrumental", True, "V4_5")
    mock_poll.assert_called_once_with("music123")
    mock_download.assert_called_once_with("https://example.com/track1.mp3", output_path)
    assert result == output_path


def test_fit_music_to_duration_copies_unchanged_when_exactly_at_target(tmp_path):
    music_path = tmp_path / "Music_Full.mp3"
    music_path.write_bytes(b"fake-mp3-data")
    output_path = tmp_path / "Music_Fitted.mp3"

    probe_result = MagicMock(returncode=0, stdout="65.0\n", stderr="")  # duration exactly equals target_seconds

    with patch("music_generation.subprocess.run", return_value=probe_result) as mock_run:
        result = fit_music_to_duration(music_path, output_path, target_seconds=65.0)

    assert result == output_path
    assert output_path.read_bytes() == b"fake-mp3-data"
    assert mock_run.call_count == 1
    assert mock_run.call_args[0][0][0] == "ffprobe"


def test_fit_music_to_duration_copies_unchanged_when_within_tolerance(tmp_path):
    # Real ffprobe output for generated audio almost never matches a clean target
    # exactly (e.g. 64.98 vs a 65.0 target) — the copy path must still trigger
    # within a small tolerance instead of always falling through to trim/loop.
    music_path = tmp_path / "Music_Full.mp3"
    music_path.write_bytes(b"fake-mp3-data")
    output_path = tmp_path / "Music_Fitted.mp3"

    probe_result = MagicMock(returncode=0, stdout="64.98\n", stderr="")

    with patch("music_generation.subprocess.run", return_value=probe_result) as mock_run:
        result = fit_music_to_duration(music_path, output_path, target_seconds=65.0)

    assert result == output_path
    assert output_path.read_bytes() == b"fake-mp3-data"
    assert mock_run.call_count == 1
    assert mock_run.call_args[0][0][0] == "ffprobe"


def test_fit_music_to_duration_loops_when_just_outside_tolerance(tmp_path):
    # 64.3 vs target 65.0 is 0.7s away — outside the 0.5s tolerance — so this
    # must NOT hit the copy branch; it should fall through to the loop branch
    # (duration < target_seconds).
    music_path = tmp_path / "Music_Full.mp3"
    output_path = tmp_path / "Music_Fitted.mp3"

    probe_result = MagicMock(returncode=0, stdout="64.3\n", stderr="")

    def fake_subprocess_run(cmd, **kwargs):
        if cmd[0] == "ffprobe":
            return probe_result
        output_path.touch()
        return MagicMock(returncode=0)

    with patch("music_generation.subprocess.run", side_effect=fake_subprocess_run) as mock_run:
        result = fit_music_to_duration(music_path, output_path, target_seconds=65.0)

    assert result == output_path
    assert mock_run.call_count == 2
    ffmpeg_call = mock_run.call_args_list[1][0][0]
    assert ffmpeg_call[0] == "ffmpeg"
    assert "-stream_loop" in ffmpeg_call
    assert "-t" in ffmpeg_call and ffmpeg_call[ffmpeg_call.index("-t") + 1] == "65.0"


def test_fit_music_to_duration_trims_when_longer(tmp_path):
    music_path = tmp_path / "Music_Full.mp3"
    output_path = tmp_path / "Music_Fitted.mp3"

    probe_result = MagicMock(returncode=0, stdout="200.0\n", stderr="")

    def fake_subprocess_run(cmd, **kwargs):
        if cmd[0] == "ffprobe":
            return probe_result
        output_path.touch()
        return MagicMock(returncode=0)

    with patch("music_generation.subprocess.run", side_effect=fake_subprocess_run) as mock_run:
        result = fit_music_to_duration(music_path, output_path, target_seconds=65.0)

    assert result == output_path
    ffmpeg_call = mock_run.call_args_list[1][0][0]
    assert ffmpeg_call[0] == "ffmpeg"
    assert "-t" in ffmpeg_call and ffmpeg_call[ffmpeg_call.index("-t") + 1] == "65.0"
    assert "-stream_loop" not in ffmpeg_call


def test_fit_music_to_duration_loops_when_shorter(tmp_path):
    music_path = tmp_path / "Music_Full.mp3"
    output_path = tmp_path / "Music_Fitted.mp3"

    probe_result = MagicMock(returncode=0, stdout="30.0\n", stderr="")

    def fake_subprocess_run(cmd, **kwargs):
        if cmd[0] == "ffprobe":
            return probe_result
        output_path.touch()
        return MagicMock(returncode=0)

    with patch("music_generation.subprocess.run", side_effect=fake_subprocess_run) as mock_run:
        result = fit_music_to_duration(music_path, output_path, target_seconds=65.0)

    assert result == output_path
    ffmpeg_call = mock_run.call_args_list[1][0][0]
    assert ffmpeg_call[0] == "ffmpeg"
    assert "-stream_loop" in ffmpeg_call
    assert "-t" in ffmpeg_call and ffmpeg_call[ffmpeg_call.index("-t") + 1] == "65.0"
