# test_analyze_reference_video.py
from pathlib import Path
from unittest.mock import patch, MagicMock
from analyze_reference_video import download_video, detect_scenes

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

def test_detect_scenes_parses_ffmpeg_output_into_boundaries(tmp_path):
    video_path = tmp_path / "Video.mp4"
    video_path.touch()

    ffprobe_result = MagicMock(returncode=0, stdout="12.5\n", stderr="")
    ffmpeg_result = MagicMock(
        returncode=0, stdout="",
        stderr=(
            "frame:1 pts_time:3.100 ... showinfo\n"
            "frame:2 pts_time:7.800 ... showinfo\n"
        ),
    )

    with patch("analyze_reference_video.subprocess.run", side_effect=[ffprobe_result, ffmpeg_result]) as mock_run:
        scenes = detect_scenes(video_path)

    assert scenes == [(0.0, 3.1), (3.1, 7.8), (7.8, 12.5)]
    assert mock_run.call_count == 2
