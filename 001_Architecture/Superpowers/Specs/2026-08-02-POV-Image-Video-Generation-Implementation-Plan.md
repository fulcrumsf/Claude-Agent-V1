# POV Image & Video Generation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the two generation wrappers the POV Shorts Pipeline needs to turn a shot list into real assets — an image for each scene (GPT-Image-2 via kie.ai) and a video clip for each scene (Seedance 1.5 Pro via WaveSpeed, native audio, trimmed to a 5-second window if generated longer).

**Architecture:** `image_generation.py` wraps kie.ai's async task API (`kie-cli gpt_image_2` submit → `kie-cli get_task_status` poll → download) via subprocess, matching the proven submit/poll/download pattern already live in this repo. `video_generation.py` wraps the WaveSpeed CLI's synchronous `run --download` call for `bytedance/seedance-v1.5-pro/image-to-video` with `generate_audio=true` — the exact model/platform/parameters already validated in a live A/B test earlier this session (Seedance's native audio won against two dedicated Foley models) — reusing the same multi-output-candidate-normalization pattern already built and tested in `generate_foley.py`. A third function trims any clip longer than 5s to a 5-second window via ffprobe/ffmpeg.

**Tech Stack:** Python 3, `kie-cli` (installed, `KIE_API_KEY` in `~/.env-secrets`), `wavespeed` CLI (installed, `WAVESPEED_API_KEY` in `~/.env-secrets`), `ffmpeg`/`ffprobe` (installed), `requests` (for image download), `pytest`.

## Global Constraints

- Skill folder: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/` (already exists — contains `POV_Style_Guide.md`, `SKILL.md`, `foley_config.py`, `generate_foley.py`, `beat_planning.py`, `shot_list_builder.py`, and their tests; add new files here, do not create a different folder or relocate existing ones).
- Plan/spec docs live in `001_Architecture/Superpowers/Specs/` (confirmed with Tony).
- Image generation: GPT-Image-2 via kie.ai, model id `"gpt-image-2-text-to-image"` (confirmed live via `kie-cli gpt_image_2`), aspect ratio `9:16` (vertical POV format), resolution `1K` per the locked cost estimate.
- Video generation: Seedance 1.5 Pro via WaveSpeed, model id `"bytedance/seedance-v1.5-pro/image-to-video"` (confirmed live via `wavespeed schema`), `generate_audio=true`, `aspect_ratio=9:16`, `resolution=1080p`, `duration=5` — this exact model/platform/parameter combination is what won the live Mirelo-vs-Sonilo-vs-Seedance-native A/B test earlier this session; do not substitute a different model without re-validating.
- Every video prompt passed to Seedance MUST be built via `shot_list_builder.build_video_prompt()` (already built, hardened against dialogue-quote bypasses across 2 fix rounds) — never hand-assemble a Seedance prompt string directly in this plan's new code.
- Clips longer than 5 seconds must be trimmed to the best 5-second window, not a default 0-5s cut (per Tony's explicit instruction). This plan's heuristic: the middle 5-second window (skips likely slow-start/slow-end motion at the clip's edges) — document this as a heuristic, not true creative/motion-aware judgment; a future improvement could use motion detection to pick a better window.
- No hardcoded output paths — every function takes paths as parameters.
- All external calls (kie-cli, wavespeed, ffmpeg/ffprobe, network downloads) must be mockable in tests — no test may require live network/API access except the final manual smoke-test task.
- No new directories may be created beyond what's explicitly confirmed in this plan. If execution surfaces a need for another new folder, stop and ask Tony first.
- This plan does NOT cover: YouTube trend-research ideation, sound design/assembly (beyond what's already built), text overlay, YouTube package, or Blotato upload.

---

### Task 1: Image generation — submit + poll

**Files:**
- Create: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/image_generation.py`
- Create: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/test_image_generation.py`

**Interfaces:**
- Produces: `submit_image_task(prompt: str, aspect_ratio: str = "9:16", resolution: str = "1K") -> str` (returns a task ID); `poll_image_task(task_id: str, poll_interval_seconds: float = 15.0, max_attempts: int = 12) -> str` (returns the completed image URL, raises `RuntimeError` if the task fails, raises `TimeoutError` if it never completes within the attempt budget). Both used by Task 2's `generate_image`.

- [ ] **Step 1: Write the failing test for `submit_image_task`**

```python
# test_image_generation.py
import json
from unittest.mock import patch, MagicMock
from image_generation import submit_image_task

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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline && python3 -m pytest test_image_generation.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'image_generation'`

- [ ] **Step 3: Write minimal implementation**

```python
# image_generation.py
import json
import subprocess
import time

def submit_image_task(prompt: str, aspect_ratio: str = "9:16", resolution: str = "1K") -> str:
    result = subprocess.run(
        [
            "kie-cli", "gpt_image_2",
            "--prompt", prompt,
            "--aspect_ratio", aspect_ratio,
            "--resolution", resolution,
            "--json",
        ],
        check=True, capture_output=True, text=True,
    )
    return json.loads(result.stdout)["task_id"]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest test_image_generation.py -v`
Expected: PASS

- [ ] **Step 5: Write the failing tests for `poll_image_task`**

```python
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
```

(Add `import pytest` and `from image_generation import poll_image_task` to the test file's imports.)

- [ ] **Step 6: Run tests to verify they fail**

Run: `python3 -m pytest test_image_generation.py -v -k poll_image_task`
Expected: FAIL with `ImportError: cannot import name 'poll_image_task'`

- [ ] **Step 7: Write minimal implementation**

```python
def poll_image_task(task_id: str, poll_interval_seconds: float = 15.0, max_attempts: int = 12) -> str:
    for attempt in range(max_attempts):
        if attempt > 0:
            time.sleep(poll_interval_seconds)

        result = subprocess.run(
            ["kie-cli", "get_task_status", "--task_id", task_id, "--json"],
            check=True, capture_output=True, text=True,
        )
        data = json.loads(result.stdout)
        status = data.get("status")

        if status == "completed":
            return data["result_urls"][0]
        if status == "failed":
            raise RuntimeError(f"Image generation task {task_id} failed: {data.get('error')}")

    raise TimeoutError(f"Image generation task {task_id} did not complete within {max_attempts} attempts")
```

- [ ] **Step 8: Run tests to verify they pass**

Run: `python3 -m pytest test_image_generation.py -v`
Expected: All 5 tests PASS

- [ ] **Step 9: Commit**

```bash
git add 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/image_generation.py 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/test_image_generation.py
git commit -m "POV pipeline: add image generation submit + poll"
```

---

### Task 2: Image download + orchestration + CLI

**Files:**
- Modify: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/image_generation.py`
- Modify: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/test_image_generation.py`

**Interfaces:**
- Consumes: `submit_image_task(prompt, aspect_ratio, resolution) -> str`, `poll_image_task(task_id, ...) -> str` (Task 1)
- Produces: `download_image(url: str, output_path: Path) -> Path`; `generate_image(prompt: str, output_path: Path, aspect_ratio: str = "9:16", resolution: str = "1K") -> Path` — orchestrates submit → poll → download, used by the pipeline's per-scene generation loop; `main(prompt, out, aspect_ratio="9:16", resolution="1K") -> None` — CLI entrypoint

- [ ] **Step 1: Write the failing tests**

```python
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

    mock_submit.assert_called_once_with("a medieval hut interior at dawn", "9:16", "1K")
    mock_poll.assert_called_once_with("abc123")
    mock_download.assert_called_once_with("https://example.com/image.png", output_path)
    assert result == output_path


def test_main_wires_generate_image(tmp_path):
    output_path = tmp_path / "scene1.png"
    with patch("image_generation.generate_image") as mock_generate:
        mock_generate.return_value = output_path
        main("a medieval hut interior at dawn", str(output_path), aspect_ratio="9:16", resolution="1K")

    mock_generate.assert_called_once_with(
        "a medieval hut interior at dawn", Path(str(output_path)), "9:16", "1K",
    )
```

(Add `from image_generation import download_image, generate_image, main` and `from pathlib import Path` to the test file's imports.)

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest test_image_generation.py -v -k "download_image or generate_image or main_wires"`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Write minimal implementation**

```python
import argparse
import requests
from pathlib import Path

def download_image(url: str, output_path: Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    response = requests.get(url, timeout=30)
    response.raise_for_status()
    output_path.write_bytes(response.content)
    return output_path


def generate_image(prompt: str, output_path: Path, aspect_ratio: str = "9:16", resolution: str = "1K") -> Path:
    task_id = submit_image_task(prompt, aspect_ratio, resolution)
    image_url = poll_image_task(task_id)
    return download_image(image_url, Path(output_path))


def main(prompt: str, out: str, aspect_ratio: str = "9:16", resolution: str = "1K") -> None:
    generate_image(prompt, Path(out), aspect_ratio, resolution)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a POV scene image via GPT-Image-2 (kie.ai).")
    parser.add_argument("prompt", help="Image prompt")
    parser.add_argument("--out", required=True, help="Output image file path")
    parser.add_argument("--aspect_ratio", default="9:16", choices=["auto", "1:1", "9:16", "16:9", "4:3", "3:4"])
    parser.add_argument("--resolution", default="1K", choices=["1K", "2K", "4K"])
    args = parser.parse_args()
    main(args.prompt, args.out, args.aspect_ratio, args.resolution)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest test_image_generation.py -v`
Expected: All 8 tests PASS (5 from Task 1 + 3 new)

- [ ] **Step 5: Commit**

```bash
git add 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/image_generation.py 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/test_image_generation.py
git commit -m "POV pipeline: add download_image, generate_image, and CLI entrypoint"
```

---

### Task 3: Video generation via Seedance (native audio)

**Files:**
- Create: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/video_generation.py`
- Create: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/test_video_generation.py`

**Interfaces:**
- Produces: `generate_video(image_url: str, video_prompt: str, output_path: Path, duration: int = 5, resolution: str = "1080p", aspect_ratio: str = "9:16") -> Path` — used by Task 4's trim step and the pipeline's per-scene generation loop; `main(image_url, prompt, out, duration=5, resolution="1080p", aspect_ratio="9:16") -> None` — CLI entrypoint. `video_prompt` must already be the output of `shot_list_builder.build_video_prompt()` — this function does not call it internally (the shot list is built once, ahead of generation, and its prompts are read back for each generation call).

- [ ] **Step 1: Write the failing tests**

```python
# test_video_generation.py
from pathlib import Path
from unittest.mock import patch, MagicMock
from video_generation import generate_video

def test_generate_video_calls_wavespeed_with_seedance_params(tmp_path):
    output_path = tmp_path / "scene1.mp4"
    mock_result = MagicMock(returncode=0)

    with patch("video_generation.subprocess.run", return_value=mock_result) as mock_run:
        output_path.touch()  # simulate wavespeed writing directly to the requested path
        result = generate_video(
            "https://example.com/scene1.png",
            "POV walking down a dirt road. Sound: footsteps, birds. - No dialogue, no spoken words, no voiceover, no lip sync, no music, no on-screen text.",
            output_path,
        )

    mock_run.assert_called_once_with(
        [
            "wavespeed", "run", "bytedance/seedance-v1.5-pro/image-to-video",
            "-i", "image=https://example.com/scene1.png",
            "-i", "prompt=POV walking down a dirt road. Sound: footsteps, birds. - No dialogue, no spoken words, no voiceover, no lip sync, no music, no on-screen text.",
            "-i", "duration=5",
            "-i", "resolution=1080p",
            "-i", "aspect_ratio=9:16",
            "-i", "generate_audio=true",
            "--download", str(output_path),
        ],
        check=True, capture_output=True, text=True,
    )
    assert result == output_path


def test_generate_video_normalizes_multi_output_download(tmp_path):
    output_path = tmp_path / "scene1.mp4"
    candidate_1 = tmp_path / "scene1-1.mp4"
    candidate_2 = tmp_path / "scene1-2.mp4"

    def fake_wavespeed_run(*args, **kwargs):
        candidate_1.write_bytes(b"candidate-one")
        candidate_2.write_bytes(b"candidate-two")
        return MagicMock(returncode=0)

    with patch("video_generation.subprocess.run", side_effect=fake_wavespeed_run):
        result = generate_video("https://example.com/scene1.png", "a prompt", output_path)

    assert result == output_path
    assert output_path.exists()
    assert output_path.read_bytes() == b"candidate-one"
    assert not candidate_2.exists()


def test_generate_video_raises_when_no_output_found(tmp_path):
    output_path = tmp_path / "scene1.mp4"

    with patch("video_generation.subprocess.run", return_value=MagicMock(returncode=0)):
        with pytest.raises(FileNotFoundError):
            generate_video("https://example.com/scene1.png", "a prompt", output_path)
```

(Add `import pytest` to the test file's imports.)

- [ ] **Step 2: Run test to verify it fails**

Run: `cd 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline && python3 -m pytest test_video_generation.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'video_generation'`

- [ ] **Step 3: Write minimal implementation**

```python
# video_generation.py
import subprocess
from pathlib import Path

SEEDANCE_MODEL = "bytedance/seedance-v1.5-pro/image-to-video"


def generate_video(
    image_url: str,
    video_prompt: str,
    output_path: Path,
    duration: int = 5,
    resolution: str = "1080p",
    aspect_ratio: str = "9:16",
) -> Path:
    output_path = Path(output_path)

    cmd = [
        "wavespeed", "run", SEEDANCE_MODEL,
        "-i", f"image={image_url}",
        "-i", f"prompt={video_prompt}",
        "-i", f"duration={duration}",
        "-i", f"resolution={resolution}",
        "-i", f"aspect_ratio={aspect_ratio}",
        "-i", "generate_audio=true",
        "--download", str(output_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)

    if not output_path.exists():
        candidates = sorted(output_path.parent.glob(f"{output_path.stem}-*{output_path.suffix}"))
        if not candidates:
            raise FileNotFoundError(
                f"No output found at {output_path} or as a numbered candidate after wavespeed run"
            )
        candidates[0].rename(output_path)
        for extra in candidates[1:]:
            extra.unlink()

    return output_path


def main(image_url: str, prompt: str, out: str, duration: int = 5, resolution: str = "1080p", aspect_ratio: str = "9:16") -> None:
    generate_video(image_url, prompt, Path(out), duration, resolution, aspect_ratio)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate a POV scene video clip via Seedance 1.5 Pro (native audio).")
    parser.add_argument("image_url", help="Public URL of the reference image")
    parser.add_argument("prompt", help="Video prompt (must already include the negative-prompt closer)")
    parser.add_argument("--out", required=True, help="Output video file path")
    parser.add_argument("--duration", type=int, default=5)
    parser.add_argument("--resolution", default="1080p", choices=["480p", "720p", "1080p"])
    parser.add_argument("--aspect_ratio", default="9:16")
    args = parser.parse_args()
    main(args.image_url, args.prompt, args.out, args.duration, args.resolution, args.aspect_ratio)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest test_video_generation.py -v`
Expected: All 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/video_generation.py 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/test_video_generation.py
git commit -m "POV pipeline: add generate_video via Seedance 1.5 Pro with native audio"
```

---

### Task 4: Trim-to-best-5s-window + SKILL.md update

**Files:**
- Modify: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/video_generation.py`
- Modify: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/test_video_generation.py`
- Modify: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/SKILL.md`

**Interfaces:**
- Consumes: nothing from Task 3 directly (independent function in the same module)
- Produces: `trim_to_best_window(video_path: Path, output_path: Path, target_seconds: float = 5.0) -> Path` — if the clip is already `<= target_seconds`, copies it unchanged to `output_path`; if longer, trims to the middle `target_seconds`-length window via ffmpeg. Used by the pipeline's per-scene generation loop after every `generate_video()` call.

- [ ] **Step 1: Write the failing tests**

```python
def test_trim_to_best_window_copies_unchanged_when_already_short_enough(tmp_path):
    video_path = tmp_path / "scene1.mp4"
    video_path.write_bytes(b"fake-video-data")
    output_path = tmp_path / "scene1_trimmed.mp4"

    probe_result = MagicMock(returncode=0, stdout="4.5\n", stderr="")

    with patch("video_generation.subprocess.run", return_value=probe_result) as mock_run:
        result = trim_to_best_window(video_path, output_path, target_seconds=5.0)

    assert result == output_path
    assert output_path.read_bytes() == b"fake-video-data"
    # Only ffprobe was called (to check duration) — no ffmpeg trim needed since 4.5s <= 5.0s
    assert mock_run.call_count == 1
    assert mock_run.call_args[0][0][0] == "ffprobe"


def test_trim_to_best_window_trims_middle_window_when_longer(tmp_path):
    video_path = tmp_path / "scene1.mp4"
    output_path = tmp_path / "scene1_trimmed.mp4"

    probe_result = MagicMock(returncode=0, stdout="9.0\n", stderr="")

    def fake_subprocess_run(cmd, **kwargs):
        if cmd[0] == "ffprobe":
            return probe_result
        # cmd[0] == "ffmpeg": simulate it writing the trimmed output file
        output_path.touch()
        return MagicMock(returncode=0)

    with patch("video_generation.subprocess.run", side_effect=fake_subprocess_run) as mock_run:
        result = trim_to_best_window(video_path, output_path, target_seconds=5.0)

    assert result == output_path
    assert mock_run.call_count == 2
    ffmpeg_call = mock_run.call_args_list[1][0][0]
    assert ffmpeg_call[0] == "ffmpeg"
    # duration=9.0, target=5.0 -> middle window starts at (9.0-5.0)/2 = 2.0s
    assert "-ss" in ffmpeg_call and ffmpeg_call[ffmpeg_call.index("-ss") + 1] == "2.0"
    assert "-t" in ffmpeg_call and ffmpeg_call[ffmpeg_call.index("-t") + 1] == "5.0"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest test_video_generation.py -v -k trim_to_best_window`
Expected: FAIL with `ImportError: cannot import name 'trim_to_best_window'`

- [ ] **Step 3: Write minimal implementation**

```python
import shutil

def trim_to_best_window(video_path: Path, output_path: Path, target_seconds: float = 5.0) -> Path:
    video_path = Path(video_path)
    output_path = Path(output_path)

    duration_result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)],
        check=True, capture_output=True, text=True,
    )
    duration = float(duration_result.stdout.strip())

    if duration <= target_seconds:
        shutil.copy(video_path, output_path)
        return output_path

    # Heuristic: take the middle window, skipping likely slow-start/slow-end motion
    # at the clip's edges. This is not motion-aware — a future improvement could use
    # scene/motion detection to pick a genuinely "best" window instead of the geometric middle.
    start_time = round((duration - target_seconds) / 2, 1)
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(video_path), "-ss", str(start_time), "-t", str(target_seconds),
         "-c:v", "libx264", "-c:a", "aac", str(output_path)],
        check=True, capture_output=True, text=True,
    )
    return output_path
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest test_video_generation.py -v`
Expected: All 5 tests PASS (3 from Task 3 + 2 new)

- [ ] **Step 5: Update SKILL.md**

Add a new section documenting the now-built image/video generation, and update "Not yet built":

```markdown
## Image & Video Generation (built)

**Image generation:** `generate_image(prompt, output_path, aspect_ratio="9:16", resolution="1K")` in `image_generation.py` — submits to GPT-Image-2 via `kie-cli gpt_image_2`, polls `kie-cli get_task_status` until completion, downloads the result. CLI: `python3 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/image_generation.py "<prompt>" --out "<path>"`.

**Video generation:** `generate_video(image_url, video_prompt, output_path, duration=5, resolution="1080p", aspect_ratio="9:16")` in `video_generation.py` — runs Seedance 1.5 Pro via `wavespeed run bytedance/seedance-v1.5-pro/image-to-video` with `generate_audio=true` (the model/platform/params validated by the live A/B test that chose Seedance native audio over dedicated Foley models). `video_prompt` must be pre-built via `shot_list_builder.build_video_prompt()` — never hand-assemble it. CLI: `python3 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/video_generation.py "<image_url>" "<prompt>" --out "<path>"`.

**Clip trimming:** `trim_to_best_window(video_path, output_path, target_seconds=5.0)` in the same module — if a generated clip exceeds the target length, trims to the middle window (a heuristic, not motion-aware; a future improvement could pick a genuinely-best window via scene/motion detection). Call this after every `generate_video()` call before using the clip downstream.

## Not yet built (updated)

YouTube trend-research ideation, sound design/assembly beyond what's built, text overlay, YouTube package, and Blotato upload — each is a separate implementation plan.
```

- [ ] **Step 6: Commit**

```bash
git add 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/video_generation.py 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/test_video_generation.py 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/SKILL.md
git commit -m "POV pipeline: add trim_to_best_window and document image/video generation in SKILL.md"
```

---

### Task 5: Manual smoke test — one real image + video, end to end

**Files:** none created/modified — this is a validation-only task producing output artifacts under a folder Tony confirms.

- [ ] **Step 1: Ask Tony where to save the smoke-test outputs**

Do not default to a path. Propose a new folder under `Productions/` (per the design spec's deliverables structure) or ask Tony for a preferred location for this one-off validation run.

- [ ] **Step 2: Generate one real image + video for the "fetching water" scene**

```bash
python3 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/image_generation.py \
  "POV first-person shot of hands carrying a wooden water bucket down a muddy medieval dirt road, other peasants walking past, church steeple in the distance, dawn morning light, historical documentary realism" \
  --out "<confirmed folder>/scene_image.png"
```

Then upload that image to get a public URL (reuse the `wavespeed upload` pattern already used for the Foley A/B test), and generate the video:

```bash
wavespeed upload "<confirmed folder>/scene_image.png" --json
# parse the returned url

python3 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/video_generation.py \
  "<uploaded image url>" \
  "POV walking down a medieval dirt road carrying a wooden bucket of water, water sloshing rhythmically with each step, footsteps on packed dirt, other peasants murmuring indistinctly in the background, birds chirping, handheld camera motion, dawn lighting, historical documentary realism. - No dialogue, no spoken words, no voiceover, no lip sync, no music, no on-screen text." \
  --out "<confirmed folder>/scene_video_raw.mp4"
```

(This exact video prompt matches `shot_list_builder.build_video_prompt()`'s expected output shape — in the real pipeline this string would come from calling that function, not be hand-typed; for this smoke test it's fine to type it directly since the point is testing generation, not the prompt-builder, which already has its own passing test suite.)

- [ ] **Step 3: If the generated clip is longer than 5s, trim it**

```bash
python3 -c "
from pathlib import Path
import sys
sys.path.insert(0, '001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline')
from video_generation import trim_to_best_window
trim_to_best_window(Path('<confirmed folder>/scene_video_raw.mp4'), Path('<confirmed folder>/scene_video_trimmed.mp4'))
"
```

- [ ] **Step 4: Verify and report**

Confirm both the image and the (trimmed, if applicable) video exist and are valid via `ffprobe` (report duration, resolution, video/audio codec, file size). Confirm the video has real synced audio (not silent) matching the sloshing/footsteps/birds described in the prompt, and confirm no dialogue is audible. If a command fails, diagnose whether it's a bug in this plan's code (fix it, add/update a test covering what broke, run the full test suite to confirm no regressions, commit) versus an environment/API issue (report the raw error).

- [ ] **Step 5: Commit any fixes discovered in Step 4, then stop**

Do not proceed to building assembly, text overlay, or any later pipeline phase in this task — this plan ends once image and video generation are proven working end to end on one real scene.

---

## Self-Review Notes

- **Spec coverage:** image generation (GPT-Image-2 via kie.ai) ✅ (Tasks 1-2), video generation (Seedance 1.5 Pro, native audio, matching the validated A/B-test winner) ✅ (Task 3), trim-to-best-5s-window (not a default 0-5s cut) ✅ (Task 4), every video prompt must route through `build_video_prompt()` ✅ (Global Constraints + Task 3's docstring/interface note — enforced by convention since this plan's functions take an already-built prompt string, not raw scene content), no hardcoded paths ✅ (all functions take paths/URLs as parameters), mockable external calls ✅ (all subprocess/network calls mocked in every test except Task 5), real end-to-end validation ✅ (Task 5).
- **Type consistency:** `Path` used consistently for all path parameters across `image_generation.py` and `video_generation.py`; `generate_image`'s and `generate_video`'s signatures match exactly how their respective `main()` functions call them; `trim_to_best_window`'s `target_seconds` type (`float`) is consistent between its default value and the docstring/prompt.
- **Placeholder scan:** no TBDs; every step has runnable code and an exact command with expected output. Task 5's `<confirmed folder>` placeholders are intentional runtime confirmation gates (Step 1 requires asking Tony before running), not plan placeholders.
