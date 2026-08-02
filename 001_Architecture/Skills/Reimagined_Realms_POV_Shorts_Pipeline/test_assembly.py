from pathlib import Path
from unittest.mock import patch, MagicMock
from assembly import concatenate_videos

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
    filelist_path = output_path.parent / "_concat_filelist.txt"
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
