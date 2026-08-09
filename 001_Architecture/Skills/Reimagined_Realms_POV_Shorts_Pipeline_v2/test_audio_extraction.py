from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from audio_extraction import extract_audio, stitch_audio_files


def test_extract_audio_calls_ffmpeg_and_returns_output_path(tmp_path):
    video_path = tmp_path / "C01.mp4"
    video_path.touch()
    output_path = tmp_path / "C01_audio.mp3"

    mock_result = MagicMock(returncode=0)

    with patch("audio_extraction.subprocess.run", return_value=mock_result) as mock_run:
        result = extract_audio(video_path, output_path)

    mock_run.assert_called_once_with(
        ["ffmpeg", "-y", "-i", str(video_path), "-vn", "-c:a", "libmp3lame", str(output_path)],
        check=True, capture_output=True, text=True,
    )
    assert result == output_path


def test_stitch_audio_files_writes_filelist_and_calls_ffmpeg_concat(tmp_path):
    audio1 = tmp_path / "C01_audio.mp3"
    audio2 = tmp_path / "C02_audio.mp3"
    audio1.touch()
    audio2.touch()
    output_path = tmp_path / "Ambient_Foley_Full.mp3"

    mock_result = MagicMock(returncode=0)

    with patch("audio_extraction.subprocess.run", return_value=mock_result) as mock_run:
        result = stitch_audio_files([audio1, audio2], output_path)

    assert result == output_path
    # Unique filelist name based on output_path.stem (proactive hardening from Task 1 pattern)
    filelist_path = output_path.parent / f"_audio_concat_filelist_{output_path.stem}.txt"
    assert filelist_path.exists()
    filelist_content = filelist_path.read_text()
    assert f"file '{audio1}'" in filelist_content
    assert f"file '{audio2}'" in filelist_content

    mock_run.assert_called_once_with(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(filelist_path), "-c", "copy", str(output_path)],
        check=True, capture_output=True, text=True,
    )


def test_stitch_audio_files_raises_on_empty_list(tmp_path):
    """Proactive hardening: guard against empty audio_paths list before writing filelist"""
    output_path = tmp_path / "Ambient_Foley_Full.mp3"

    with pytest.raises(ValueError, match="audio_paths must not be empty"):
        stitch_audio_files([], output_path)

    # Verify no filelist was created
    filelist_path = output_path.parent / f"_audio_concat_filelist_{output_path.stem}.txt"
    assert not filelist_path.exists()


def test_stitch_audio_files_unique_filelist_names(tmp_path):
    """Verify unique filelist naming prevents collision (proactive hardening from Task 1)"""
    audio1 = tmp_path / "C01_audio.mp3"
    audio1.touch()
    output1 = tmp_path / "Ambient_Foley_Full.mp3"
    output2 = tmp_path / "Ambient_Foley_Backup.mp3"

    mock_result = MagicMock(returncode=0)

    with patch("audio_extraction.subprocess.run", return_value=mock_result):
        stitch_audio_files([audio1], output1)
        stitch_audio_files([audio1], output2)

    filelist1 = output1.parent / f"_audio_concat_filelist_{output1.stem}.txt"
    filelist2 = output2.parent / f"_audio_concat_filelist_{output2.stem}.txt"

    # Both filelists should exist with different names
    assert filelist1.exists()
    assert filelist2.exists()
    assert filelist1.name != filelist2.name
    assert filelist1.name == "_audio_concat_filelist_Ambient_Foley_Full.txt"
    assert filelist2.name == "_audio_concat_filelist_Ambient_Foley_Backup.txt"
