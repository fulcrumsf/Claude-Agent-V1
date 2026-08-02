import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from assembly import concatenate_videos, measure_lufs, calculate_gain, mix_and_normalize

def test_concatenate_videos_writes_filelist_and_calls_ffmpeg_concat(tmp_path):
    clip1 = tmp_path / "C01.mp4"
    clip2 = tmp_path / "C02.mp4"
    clip1.touch()
    clip2.touch()
    output_path = tmp_path / "Video_Stitched.mp4"

    mock_result = MagicMock(returncode=0)

    with patch("assembly.subprocess.run", return_value=mock_result) as mock_run:
        result = concatenate_videos([clip1, clip2], output_path)

    assert result == output_path

    # A concat filelist file must have been written alongside the output, listing both clips
    filelist_path = output_path.parent / f"_concat_filelist_{output_path.stem}.txt"
    assert filelist_path.exists()
    filelist_content = filelist_path.read_text()
    assert f"file '{clip1}'" in filelist_content
    assert f"file '{clip2}'" in filelist_content

    mock_run.assert_called_once_with(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(filelist_path),
            "-map", "0:v:0", "-an", "-c:v", "copy", str(output_path),
        ],
        check=True, capture_output=True, text=True,
    )


def test_concatenate_videos_raises_on_empty_list(tmp_path):
    output_path = tmp_path / "Video_Stitched.mp4"

    with patch("assembly.subprocess.run") as mock_run:
        with pytest.raises(ValueError):
            concatenate_videos([], output_path)

    # Must fail fast, before ever touching ffmpeg or writing a filelist
    mock_run.assert_not_called()
    filelist_path = output_path.parent / f"_concat_filelist_{output_path.stem}.txt"
    assert not filelist_path.exists()


def test_concatenate_videos_uses_unique_filelist_per_output(tmp_path):
    clip1 = tmp_path / "C01.mp4"
    clip2 = tmp_path / "C02.mp4"
    clip1.touch()
    clip2.touch()

    output_a = tmp_path / "Video_A.mp4"
    output_b = tmp_path / "Video_B.mp4"

    mock_result = MagicMock(returncode=0)

    with patch("assembly.subprocess.run", return_value=mock_result):
        concatenate_videos([clip1, clip2], output_a)
        concatenate_videos([clip1, clip2], output_b)

    filelist_a = output_a.parent / f"_concat_filelist_{output_a.stem}.txt"
    filelist_b = output_b.parent / f"_concat_filelist_{output_b.stem}.txt"

    # Different outputs in the same directory must not share a filelist name
    assert filelist_a != filelist_b
    assert filelist_a.exists()
    assert filelist_b.exists()


def test_measure_lufs_parses_input_i_from_loudnorm_json(tmp_path):
    audio_path = tmp_path / "track.mp3"
    audio_path.touch()

    loudnorm_json = '{"input_i" : "-21.86", "input_tp" : "-3.0", "input_lra" : "5.0", "input_thresh" : "-32.0", "output_i" : "-16.0", "output_tp" : "-1.5", "output_lra" : "5.0", "output_thresh" : "-26.0", "normalization_type" : "dynamic", "target_offset" : "0.0"}'
    mock_result = MagicMock(returncode=0, stdout="", stderr=f"some ffmpeg log lines\n{loudnorm_json}\nmore log lines")

    with patch("assembly.subprocess.run", return_value=mock_result) as mock_run:
        result = measure_lufs(audio_path)

    called_cmd = mock_run.call_args[0][0]
    assert called_cmd[0] == "ffmpeg"
    assert "loudnorm=I=-16:LRA=11:TP=-1.5:print_format=json" in " ".join(called_cmd)
    assert result == -21.86


def test_calculate_gain_returns_correct_linear_multiplier():
    # gain_db = target - measured = -14.0 - (-21.86) = 7.86
    # volume_linear = 10 ** (7.86 / 20) ≈ 2.4717...
    result = calculate_gain(measured_lufs=-21.86, target_lufs=-14.0)
    assert abs(result - 2.4717241450) < 0.001


def test_mix_and_normalize_measures_both_tracks_and_mixes_with_calculated_gains(tmp_path):
    foley_path = tmp_path / "Ambient_Foley_Full.mp3"
    music_path = tmp_path / "Music_Fitted.mp3"
    output_path = tmp_path / "Final_Audio.mp3"

    with patch("assembly.measure_lufs", side_effect=[-21.86, -28.0]) as mock_measure, \
         patch("assembly.subprocess.run", return_value=MagicMock(returncode=0)) as mock_run:
        result = mix_and_normalize(foley_path, music_path, output_path, target_lufs=-14.0)

    assert result == output_path
    assert mock_measure.call_count == 2
    mock_measure.assert_any_call(foley_path)
    mock_measure.assert_any_call(music_path)

    ffmpeg_call = mock_run.call_args[0][0]
    assert ffmpeg_call[0] == "ffmpeg"
    assert str(foley_path) in ffmpeg_call
    assert str(music_path) in ffmpeg_call
    assert "amix" in " ".join(ffmpeg_call)
