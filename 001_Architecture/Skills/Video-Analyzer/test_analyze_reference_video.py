# test_analyze_reference_video.py
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from analyze_reference_video import download_video, detect_scenes, analyze_video_narrative

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

def test_analyze_video_narrative_uploads_file_and_prompts_with_scene_list(tmp_path):
    video_path = tmp_path / "Video.mp4"
    video_path.touch()
    scenes = [(0.0, 3.1), (3.1, 7.8)]

    mock_file = MagicMock(name="uploaded_file", state=MagicMock(name="ACTIVE"))
    mock_file.state.name = "ACTIVE"
    mock_response = MagicMock(text="## Scene 1\nWaking up...\n## Scene 2\nWalking...")

    with patch("analyze_reference_video.genai.Client") as MockClient:
        client_instance = MockClient.return_value
        client_instance.files.upload.return_value = mock_file
        client_instance.files.get.return_value = mock_file
        client_instance.models.generate_content.return_value = mock_response

        result = analyze_video_narrative(video_path, scenes)

    assert result == mock_response.text
    client_instance.files.upload.assert_called_once_with(file=str(video_path))
    call_kwargs = client_instance.models.generate_content.call_args.kwargs
    assert "0.0s-3.1s" in str(call_kwargs["contents"])
    assert "3.1s-7.8s" in str(call_kwargs["contents"])

def test_analyze_video_narrative_raises_on_failed_upload_state(tmp_path):
    video_path = tmp_path / "Video.mp4"
    video_path.touch()
    scenes = [(0.0, 3.1)]

    mock_file = MagicMock(name="uploaded_file", state=MagicMock(name="FAILED"), error="quota exceeded")
    mock_file.state.name = "FAILED"

    with patch("analyze_reference_video.genai.Client") as MockClient:
        client_instance = MockClient.return_value
        client_instance.files.upload.return_value = mock_file

        with pytest.raises(RuntimeError, match="Gemini file upload failed"):
            analyze_video_narrative(video_path, scenes)

    client_instance.models.generate_content.assert_not_called()
