import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from generate_foley import upload_video, generate_foley, main

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


def test_generate_foley_uploads_then_runs_model_and_downloads_output(tmp_path):
    video_path = tmp_path / "clip.mp4"
    video_path.touch()
    output_path = tmp_path / "clip_foley.wav"

    mock_run_result = MagicMock(returncode=0)

    with patch("generate_foley.upload_video", return_value="https://example.com/clip.mp4") as mock_upload, \
         patch("generate_foley.subprocess.run", return_value=mock_run_result) as mock_run:

        output_path.touch()  # simulate wavespeed writing the exact requested path
        result = generate_foley(video_path, output_path, prompt="footsteps on straw")

    mock_upload.assert_called_once_with(video_path)
    mock_run.assert_called_once_with(
        [
            "wavespeed", "run", "mirelo-ai/sfx-v1/video-to-audio",
            "-i", "video=https://example.com/clip.mp4",
            "-i", "prompt=footsteps on straw",
            "--download", str(output_path),
        ],
        check=True, capture_output=True, text=True,
    )
    assert result == output_path


def test_generate_foley_respects_model_override(tmp_path):
    video_path = tmp_path / "clip.mp4"
    video_path.touch()
    output_path = tmp_path / "clip_foley.wav"

    with patch("generate_foley.upload_video", return_value="https://example.com/clip.mp4"), \
         patch("generate_foley.subprocess.run", return_value=MagicMock(returncode=0)) as mock_run:

        output_path.touch()  # simulate wavespeed writing the exact requested path
        generate_foley(video_path, output_path, model="sonilo")

    called_cmd = mock_run.call_args[0][0]
    assert "sonilo/v1/video-to-sfx" in called_cmd
    assert "prompt=" not in " ".join(called_cmd)


def test_generate_foley_normalizes_multi_output_download(tmp_path):
    # Models like Mirelo can return multiple candidate outputs; wavespeed then
    # writes "{stem}-1{suffix}", "{stem}-2{suffix}", ... instead of the exact
    # path passed to --download. generate_foley must recover by taking the
    # first candidate and renaming it to the requested output_path, cleaning
    # up the rest.
    video_path = tmp_path / "clip.mp4"
    video_path.touch()
    output_path = tmp_path / "clip_foley.wav"

    def fake_run(cmd, **kwargs):
        (tmp_path / "clip_foley-1.wav").write_bytes(b"first")
        (tmp_path / "clip_foley-2.wav").write_bytes(b"second")
        return MagicMock(returncode=0)

    with patch("generate_foley.upload_video", return_value="https://example.com/clip.mp4"), \
         patch("generate_foley.subprocess.run", side_effect=fake_run):

        result = generate_foley(video_path, output_path, model="mirelo")

    assert result == output_path
    assert output_path.exists()
    assert output_path.read_bytes() == b"first"
    assert not (tmp_path / "clip_foley-1.wav").exists()
    assert not (tmp_path / "clip_foley-2.wav").exists()


def test_generate_foley_raises_when_no_output_found(tmp_path):
    video_path = tmp_path / "clip.mp4"
    video_path.touch()
    output_path = tmp_path / "clip_foley.wav"

    with patch("generate_foley.upload_video", return_value="https://example.com/clip.mp4"), \
         patch("generate_foley.subprocess.run", return_value=MagicMock(returncode=0)):

        try:
            generate_foley(video_path, output_path, model="mirelo")
            assert False, "expected FileNotFoundError"
        except FileNotFoundError:
            pass


def test_main_wires_generate_foley(tmp_path):
    with patch("generate_foley.generate_foley") as mock_generate:
        mock_generate.return_value = tmp_path / "out.wav"
        main(str(tmp_path / "clip.mp4"), str(tmp_path / "out.wav"), prompt="water sloshing", model="mirelo")

    mock_generate.assert_called_once_with(
        Path(str(tmp_path / "clip.mp4")), Path(str(tmp_path / "out.wav")), "water sloshing", "mirelo",
    )
