# test_analyze_reference_video.py
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from analyze_reference_video import download_video, detect_scenes, analyze_video_narrative, write_analysis_md, main

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

def test_analyze_video_narrative_polls_while_processing_then_active(tmp_path):
    video_path = tmp_path / "Video.mp4"
    video_path.touch()
    scenes = [(0.0, 3.1)]

    processing_file = MagicMock(name="uploaded_file_processing")
    processing_file.state.name = "PROCESSING"

    active_file = MagicMock(name="uploaded_file_active")
    active_file.state.name = "ACTIVE"

    mock_response = MagicMock(text="## Scene 1\nWaking up...")

    with patch("analyze_reference_video.genai.Client") as MockClient, \
         patch("analyze_reference_video.time.sleep") as mock_sleep:
        client_instance = MockClient.return_value
        client_instance.files.upload.return_value = processing_file
        client_instance.files.get.return_value = active_file
        client_instance.models.generate_content.return_value = mock_response

        result = analyze_video_narrative(video_path, scenes)

    assert result == mock_response.text
    client_instance.files.get.assert_called_once_with(name=processing_file.name)
    mock_sleep.assert_called_once()

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

def test_write_analysis_md_writes_summary_line_and_gemini_output(tmp_path):
    scenes = [(0.0, 3.1), (3.1, 7.8)]
    gemini_output = "## Scene 1 [0.0s-3.1s]\nScene 1 text here.\n\n## Scene 2 [3.1s-7.8s]\nScene 2 text here."

    result_path = write_analysis_md(tmp_path, scenes, gemini_output)

    assert result_path == tmp_path / "ANALYSIS.md"
    content = result_path.read_text()
    assert "ffmpeg detected 2 raw scene cuts" in content
    assert gemini_output in content

    # No fabricated index headers should be written beyond what gemini_output
    # itself contains — every "## Scene" header present must come from
    # gemini_output's own text, not a duplicate header block written by
    # write_analysis_md.
    header_lines = [line for line in content.splitlines() if line.startswith("## Scene")]
    gemini_header_lines = [line for line in gemini_output.splitlines() if line.startswith("## Scene")]
    assert header_lines == gemini_header_lines


def test_main_wires_download_detect_analyze_and_write(tmp_path):
    with patch("analyze_reference_video.download_video") as mock_download, \
         patch("analyze_reference_video.detect_scenes") as mock_detect, \
         patch("analyze_reference_video.analyze_video_narrative") as mock_analyze, \
         patch("analyze_reference_video.write_analysis_md") as mock_write:

        mock_download.return_value = tmp_path / "Video.mp4"
        mock_detect.return_value = [(0.0, 5.0)]
        mock_analyze.return_value = "analysis text"
        mock_write.return_value = tmp_path / "ANALYSIS.md"

        main("https://youtube.com/shorts/abc123", str(tmp_path))

    mock_download.assert_called_once_with("https://youtube.com/shorts/abc123", tmp_path)
    mock_detect.assert_called_once_with(tmp_path / "Video.mp4")
    mock_analyze.assert_called_once_with(tmp_path / "Video.mp4", [(0.0, 5.0)])
    mock_write.assert_called_once_with(tmp_path, [(0.0, 5.0)], "analysis text")
