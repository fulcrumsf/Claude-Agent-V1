# test_image_generation.py
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from image_generation import submit_image_task, poll_image_task, download_image, generate_image, main


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


def test_poll_image_task_returns_url_on_real_kie_cli_success_status():
    # Real kie-cli --json output for gpt-image-2 tasks surfaces the raw upstream
    # API state ("success"/"fail"/"waiting"), not the normalized "completed"/
    # "failed" strings the CLI's own docs suggest. Regression coverage for the
    # 2026-08-02 smoke test where poll_image_task timed out against a task that
    # had actually already completed successfully.
    success_result = MagicMock(
        returncode=0,
        stdout=json.dumps({"status": "success", "result_urls": ["https://example.com/image.png"]}),
    )

    with patch("image_generation.subprocess.run", return_value=success_result), \
         patch("image_generation.time.sleep") as mock_sleep:
        result = poll_image_task("abc123", poll_interval_seconds=15.0, max_attempts=12)

    mock_sleep.assert_not_called()
    assert result == "https://example.com/image.png"


def test_poll_image_task_raises_on_real_kie_cli_fail_status():
    fail_result = MagicMock(
        returncode=0,
        stdout=json.dumps({"status": "fail", "result_urls": [], "error": "content policy violation"}),
    )

    with patch("image_generation.subprocess.run", return_value=fail_result), \
         patch("image_generation.time.sleep"):
        with pytest.raises(RuntimeError, match="content policy violation"):
            poll_image_task("abc123", poll_interval_seconds=15.0, max_attempts=12)


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


def test_download_image_writes_response_content_to_path(tmp_path):
    output_path = tmp_path / "scene1.png"
    mock_response = MagicMock(content=b"fake-png-bytes")
    mock_response.raise_for_status = MagicMock()

    with patch("image_generation.requests.get", return_value=mock_response) as mock_get:
        result = download_image("https://example.com/image.png", output_path)

    mock_get.assert_called_once_with("https://example.com/image.png", timeout=30)
    assert result == output_path
    assert output_path.read_bytes() == b"fake-png-bytes"


def test_generate_image_wires_submit_poll_download(tmp_path):
    output_path = tmp_path / "scene1.png"

    with patch("image_generation.submit_image_task", return_value="abc123") as mock_submit, \
         patch("image_generation.poll_image_task", return_value="https://example.com/image.png") as mock_poll, \
         patch("image_generation.download_image", return_value=output_path) as mock_download:
        result = generate_image("a medieval hut interior at dawn", output_path, aspect_ratio="9:16", resolution="1K")

    mock_submit.assert_called_once_with("a medieval hut interior at dawn", "9:16", "1K", None)
    mock_poll.assert_called_once_with("abc123")
    mock_download.assert_called_once_with("https://example.com/image.png", output_path)
    assert result == output_path


def test_generate_image_passes_input_urls_through_to_submit(tmp_path):
    output_path = tmp_path / "sheet.png"

    with patch("image_generation.submit_image_task", return_value="abc123") as mock_submit, \
         patch("image_generation.poll_image_task", return_value="https://example.com/sheet.png"), \
         patch("image_generation.download_image", return_value=output_path):
        generate_image(
            "character sheet grid", output_path, aspect_ratio="1:1", resolution="2K",
            input_urls=["https://example.com/ref1.png", "https://example.com/ref2.png"],
        )

    mock_submit.assert_called_once_with(
        "character sheet grid", "1:1", "2K",
        ["https://example.com/ref1.png", "https://example.com/ref2.png"],
    )


def test_submit_image_task_includes_input_urls_flags_when_provided():
    mock_result = MagicMock(returncode=0, stdout=json.dumps({"task_id": "abc123"}))

    with patch("image_generation.subprocess.run", return_value=mock_result) as mock_run:
        submit_image_task(
            "character sheet grid", aspect_ratio="1:1", resolution="2K",
            input_urls=["https://example.com/ref1.png", "https://example.com/ref2.png"],
        )

    mock_run.assert_called_once_with(
        [
            "kie-cli", "gpt_image_2",
            "--prompt", "character sheet grid",
            "--aspect_ratio", "1:1",
            "--resolution", "2K",
            "--json",
            "--input_urls", "https://example.com/ref1.png",
            "--input_urls", "https://example.com/ref2.png",
        ],
        check=True, capture_output=True, text=True,
    )


def test_main_wires_generate_image(tmp_path):
    output_path = tmp_path / "scene1.png"
    with patch("image_generation.generate_image") as mock_generate:
        mock_generate.return_value = output_path
        main("a medieval hut interior at dawn", str(output_path), aspect_ratio="9:16", resolution="1K")

    mock_generate.assert_called_once_with(
        "a medieval hut interior at dawn", Path(str(output_path)), "9:16", "1K", None,
    )
