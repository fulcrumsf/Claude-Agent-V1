# test_analyze_reference_video.py
from pathlib import Path
from unittest.mock import patch, MagicMock
from analyze_reference_video import download_video

def test_download_video_calls_yt_dlp_and_returns_path(tmp_path):
    with patch("analyze_reference_video.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        result = download_video("https://youtube.com/shorts/abc123", tmp_path)

    expected_path = tmp_path / "Video.mp4"
    mock_run.assert_called_once_with(
        ["yt-dlp", "-f", "mp4", "-o", str(expected_path), "https://youtube.com/shorts/abc123"],
        check=True, capture_output=True,
    )
    assert result == expected_path
