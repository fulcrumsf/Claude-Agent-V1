# test_image_generation.py
import json
from unittest.mock import patch, MagicMock

import pytest

from image_generation import submit_image_task, poll_image_task


def test_submit_image_task_calls_kie_cli_and_returns_task_id():
    mock_result = MagicMock(
        returncode=0,
        stdout=json.dumps({
            "success": True,
            "task_id": "abc123",
            "message": "GPT Image 2 Text-to-Image task created successfully",
        }),
    )

    with patch("image_generation.subprocess.run", return_value=mock_result) as mock_run:
        result = submit_image_task("a medieval hut interior at dawn", aspect_ratio="9:16", resolution="1K")

    mock_run.assert_called_once_with(
        [
            "kie-cli", "gpt_image_2",
            "--prompt", "a medieval hut interior at dawn",
            "--aspect_ratio", "9:16",
            "--resolution", "1K",
            "--json",
        ],
        check=True, capture_output=True, text=True,
    )
    assert result == "abc123"


def test_poll_image_task_returns_url_on_completion():
    completed_result = MagicMock(
        returncode=0,
        stdout=json.dumps({"status": "completed", "result_urls": ["https://example.com/image.png"]}),
    )

    with patch("image_generation.subprocess.run", return_value=completed_result) as mock_run, \
         patch("image_generation.time.sleep") as mock_sleep:
        result = poll_image_task("abc123", poll_interval_seconds=15.0, max_attempts=12)

    mock_run.assert_called_once_with(
        ["kie-cli", "get_task_status", "--task_id", "abc123", "--json"],
        check=True, capture_output=True, text=True,
    )
    mock_sleep.assert_not_called()
    assert result == "https://example.com/image.png"


def test_poll_image_task_polls_while_generating_then_completes():
    generating_result = MagicMock(returncode=0, stdout=json.dumps({"status": "generating", "result_urls": []}))
    completed_result = MagicMock(
        returncode=0,
        stdout=json.dumps({"status": "completed", "result_urls": ["https://example.com/image.png"]}),
    )

    with patch("image_generation.subprocess.run", side_effect=[generating_result, completed_result]) as mock_run, \
         patch("image_generation.time.sleep") as mock_sleep:
        result = poll_image_task("abc123", poll_interval_seconds=15.0, max_attempts=12)

    assert mock_run.call_count == 2
    mock_sleep.assert_called_once_with(15.0)
    assert result == "https://example.com/image.png"


def test_poll_image_task_raises_on_failed_status():
    failed_result = MagicMock(returncode=0, stdout=json.dumps({"status": "failed", "result_urls": [], "error": "content policy violation"}))

    with patch("image_generation.subprocess.run", return_value=failed_result), \
         patch("image_generation.time.sleep"):
        with pytest.raises(RuntimeError, match="content policy violation"):
            poll_image_task("abc123", poll_interval_seconds=15.0, max_attempts=12)


def test_poll_image_task_raises_timeout_after_max_attempts():
    generating_result = MagicMock(returncode=0, stdout=json.dumps({"status": "generating", "result_urls": []}))

    with patch("image_generation.subprocess.run", return_value=generating_result), \
         patch("image_generation.time.sleep"):
        with pytest.raises(TimeoutError):
            poll_image_task("abc123", poll_interval_seconds=15.0, max_attempts=3)
