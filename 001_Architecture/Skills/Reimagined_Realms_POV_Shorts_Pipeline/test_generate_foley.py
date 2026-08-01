import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from generate_foley import upload_video

def test_upload_video_calls_wavespeed_and_returns_url(tmp_path):
    video_path = tmp_path / "clip.mp4"
    video_path.touch()

    mock_result = MagicMock(
        returncode=0,
        stdout=json.dumps({"url": "https://d1q70pf5vjeyhc.cloudfront.net/media/abc/clip.mp4"}),
    )

    with patch("generate_foley.subprocess.run", return_value=mock_result) as mock_run:
        result = upload_video(video_path)

    mock_run.assert_called_once_with(
        ["wavespeed", "upload", str(video_path), "--json"],
        check=True, capture_output=True, text=True,
    )
    assert result == "https://d1q70pf5vjeyhc.cloudfront.net/media/abc/clip.mp4"
