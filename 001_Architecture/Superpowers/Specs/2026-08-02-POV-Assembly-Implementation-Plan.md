# POV Assembly Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn a set of per-scene Seedance clips (each with native audio already embedded) into a fully mixed, YouTube-loudness-normalized, versioned final video — concatenate video, extract/stitch each clip's native audio, generate and fit one Suno music track to the runtime, mix and normalize, then mux video+audio into `Final_vN.mp4`.

**Architecture:** Three small modules in the existing skill folder. `audio_extraction.py` pulls each clip's embedded audio into its own file and stitches them into one track. `music_generation.py` wraps kie-cli's Suno submit/poll/download flow (same async pattern as `image_generation.py`, but Suno's real status string is `"SUCCESS"` in a different case than image generation's `"success"` — this plan's poller does a case-insensitive check from the start, learning from the bug already found in `image_generation.py`) and fits the resulting track (Suno always returns tracks far longer than our ~65s target) to the video's exact runtime via trim-or-loop. `assembly.py` owns video concatenation, LUFS measurement/gain calculation (the exact formula already locked for the long-form Reimagined Realms pipeline — see Global Constraints), the foley+music mix, and the final video+audio mux into a versioned `Final_vN.mp4`.

**Tech Stack:** Python 3, `kie-cli` (Suno, already installed), `ffmpeg`/`ffprobe`, `requests`, `pytest`.

## Global Constraints

- Skill folder: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/` (already exists — contains `POV_Style_Guide.md`, `SKILL.md`, `foley_config.py`, `generate_foley.py`, `beat_planning.py`, `shot_list_builder.py`, `image_generation.py`, `video_generation.py`, and their tests; add new files here, do not create a different folder or relocate existing ones).
- Plan/spec docs live in `001_Architecture/Superpowers/Specs/` (confirmed with Tony).
- **LUFS target: -14 LUFS integrated, true peak <= -1 dBTP** for the final mixed audio (YouTube standard, per the design spec) — measured via `ffmpeg -af loudnorm=I=-16:LRA=11:TP=-1.5:print_format=json -f null -`, reading `input_i` from the JSON output as the measured LUFS, then `gain_db = target_lufs - measured_lufs` and `volume_linear = 10 ** (gain_db / 20)` — this is the exact formula already locked and proven for the long-form Reimagined Realms pipeline's audio mix (never guess a static volume multiplier).
- kie-cli/Suno's real completion status string is `"SUCCESS"` (uppercase) — do not assume it matches image generation's `"success"` (lowercase) casing; compare case-insensitively (`status.lower() in ("completed", "success")` / `status.lower() in ("failed", "fail")`) so future task-type status-string variations don't silently time out the same way `image_generation.py`'s bug did.
- Suno's `result_urls` (or `audio_files`) always returns at least 2 candidate tracks with durations far exceeding our ~65s video target (confirmed live: 199.92s and 322.28s in one real test call) — always use the first candidate, and always fit it to the target duration via trim-or-loop before mixing; never assume Suno respects a requested duration.
- Deliverables/asset packaging structure (already locked in the design spec):
  ```
  Productions/000X_Title/
  ├── Final_v1.mp4                     ← baked master (versioned: v1, v2, v3... per iteration)
  └── Assets/
      ├── Images/
      ├── Video_Clips/
      ├── Clip_Audio/                  ← native audio extracted from each Seedance clip, one per scene
      ├── Video_Stitched.mp4           ← all clips concatenated, video-only/silent
      ├── Ambient_Foley_Full.mp3       ← all per-scene extracted audio stitched into one track
      └── Music_Full.mp3               ← Suno track, fit to the video's exact runtime
  ```
- No hardcoded output paths — every function takes paths as parameters.
- All external calls (ffmpeg, ffprobe, kie-cli, network downloads) must be mockable in tests — no test may require live network/API access except the final manual smoke-test task.
- No new directories may be created beyond what's explicitly confirmed in this plan. If execution surfaces a need for another new folder, stop and ask Tony first.
- This plan does NOT cover: text overlay (Remotion), YouTube package, or Blotato upload — separate later plans.

---

### Task 1: Video concatenation (silent)

**Files:**
- Create: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/assembly.py`
- Create: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/test_assembly.py`

**Interfaces:**
- Produces: `concatenate_videos(video_paths: list[Path], output_path: Path) -> Path` — concatenates a list of video clips (video stream only, no audio) into one silent video, used by the pipeline's assembly step and Task 6's final mux

- [ ] **Step 1: Write the failing test**

```python
# test_assembly.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline && python3 -m pytest test_assembly.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'assembly'`

- [ ] **Step 3: Write minimal implementation**

```python
# assembly.py
import subprocess
from pathlib import Path

def concatenate_videos(video_paths: list[Path], output_path: Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    filelist_path = output_path.parent / "_concat_filelist.txt"
    filelist_path.write_text("\n".join(f"file '{Path(p)}'" for p in video_paths))

    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(filelist_path),
            "-map", "0:v:0", "-an", "-c:v", "copy", str(output_path),
        ],
        check=True, capture_output=True, text=True,
    )
    return output_path
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest test_assembly.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/assembly.py 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/test_assembly.py
git commit -m "POV pipeline: add concatenate_videos"
```

---

### Task 2: Audio extraction and stitching

**Files:**
- Create: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/audio_extraction.py`
- Create: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/test_audio_extraction.py`

**Interfaces:**
- Produces: `extract_audio(video_path: Path, output_path: Path) -> Path` — pulls a clip's embedded audio into its own mp3 file; `stitch_audio_files(audio_paths: list[Path], output_path: Path) -> Path` — concatenates a list of audio files into one track. Both used by the pipeline's assembly step (per-scene `Clip_Audio/` files, then `Ambient_Foley_Full.mp3`).

- [ ] **Step 1: Write the failing tests**

```python
# test_audio_extraction.py
from pathlib import Path
from unittest.mock import patch, MagicMock
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
    filelist_path = output_path.parent / "_audio_concat_filelist.txt"
    assert filelist_path.exists()
    filelist_content = filelist_path.read_text()
    assert f"file '{audio1}'" in filelist_content
    assert f"file '{audio2}'" in filelist_content

    mock_run.assert_called_once_with(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(filelist_path), "-c", "copy", str(output_path)],
        check=True, capture_output=True, text=True,
    )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest test_audio_extraction.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'audio_extraction'`

- [ ] **Step 3: Write minimal implementation**

```python
# audio_extraction.py
import subprocess
from pathlib import Path

def extract_audio(video_path: Path, output_path: Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        ["ffmpeg", "-y", "-i", str(video_path), "-vn", "-c:a", "libmp3lame", str(output_path)],
        check=True, capture_output=True, text=True,
    )
    return output_path


def stitch_audio_files(audio_paths: list[Path], output_path: Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    filelist_path = output_path.parent / "_audio_concat_filelist.txt"
    filelist_path.write_text("\n".join(f"file '{Path(p)}'" for p in audio_paths))

    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(filelist_path), "-c", "copy", str(output_path)],
        check=True, capture_output=True, text=True,
    )
    return output_path
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest test_audio_extraction.py -v`
Expected: Both tests PASS

- [ ] **Step 5: Commit**

```bash
git add 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/audio_extraction.py 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/test_audio_extraction.py
git commit -m "POV pipeline: add extract_audio and stitch_audio_files"
```

---

### Task 3: Music generation (Suno via kie-cli)

**Files:**
- Create: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/music_generation.py`
- Create: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/test_music_generation.py`

**Interfaces:**
- Produces: `submit_music_task(prompt: str, instrumental: bool = True, model: str = "V4_5") -> str` (task ID); `poll_music_task(task_id: str, poll_interval_seconds: float = 20.0, max_attempts: int = 12) -> str` (returns the first candidate's audio URL, raises `RuntimeError` on failure, `TimeoutError` after max attempts — status comparison is case-insensitive per Global Constraints); `download_music(url: str, output_path: Path) -> Path`; `generate_music(prompt: str, output_path: Path, instrumental: bool = True, model: str = "V4_5") -> Path` (orchestrates submit → poll → download). Used by Task 4's duration-fitting step.

- [ ] **Step 1: Write the failing tests**

```python
# test_music_generation.py
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from music_generation import submit_music_task, poll_music_task, download_music, generate_music

def test_submit_music_task_calls_kie_cli_and_returns_task_id():
    mock_result = MagicMock(
        returncode=0,
        stdout=json.dumps({"success": True, "task_id": "music123", "message": "Music generation task created successfully"}),
    )

    with patch("music_generation.subprocess.run", return_value=mock_result) as mock_run:
        result = submit_music_task("gentle medieval folk ambient instrumental", instrumental=True, model="V4_5")

    mock_run.assert_called_once_with(
        [
            "kie-cli", "suno_generate_music",
            "--prompt", "gentle medieval folk ambient instrumental",
            "--customMode", "false",
            "--instrumental", "true",
            "--model", "V4_5",
            "--json",
        ],
        check=True, capture_output=True, text=True,
    )
    assert result == "music123"


def test_poll_music_task_returns_first_url_on_uppercase_success_status():
    # Real kie-cli Suno output uses "SUCCESS" (uppercase) — different casing than
    # image generation's "success". Comparison must be case-insensitive.
    completed_result = MagicMock(
        returncode=0,
        stdout=json.dumps({
            "status": "SUCCESS",
            "result_urls": ["https://example.com/track1.mp3", "https://example.com/track2.mp3"],
        }),
    )

    with patch("music_generation.subprocess.run", return_value=completed_result) as mock_run, \
         patch("music_generation.time.sleep") as mock_sleep:
        result = poll_music_task("music123", poll_interval_seconds=20.0, max_attempts=12)

    mock_run.assert_called_once_with(
        ["kie-cli", "get_task_status", "--task_id", "music123", "--json"],
        check=True, capture_output=True, text=True,
    )
    mock_sleep.assert_not_called()
    assert result == "https://example.com/track1.mp3"


def test_poll_music_task_raises_on_lowercase_fail_status():
    failed_result = MagicMock(
        returncode=0,
        stdout=json.dumps({"status": "fail", "result_urls": [], "error": "generation error"}),
    )

    with patch("music_generation.subprocess.run", return_value=failed_result), \
         patch("music_generation.time.sleep"):
        import pytest
        with pytest.raises(RuntimeError, match="generation error"):
            poll_music_task("music123", poll_interval_seconds=20.0, max_attempts=12)


def test_poll_music_task_raises_timeout_after_max_attempts():
    generating_result = MagicMock(returncode=0, stdout=json.dumps({"status": "PENDING", "result_urls": []}))

    with patch("music_generation.subprocess.run", return_value=generating_result), \
         patch("music_generation.time.sleep"):
        import pytest
        with pytest.raises(TimeoutError):
            poll_music_task("music123", poll_interval_seconds=20.0, max_attempts=3)


def test_download_music_writes_response_content(tmp_path):
    output_path = tmp_path / "Music_Full.mp3"
    mock_response = MagicMock(content=b"fake-mp3-bytes")
    mock_response.raise_for_status = MagicMock()

    with patch("music_generation.requests.get", return_value=mock_response) as mock_get:
        result = download_music("https://example.com/track1.mp3", output_path)

    mock_get.assert_called_once_with("https://example.com/track1.mp3", timeout=60)
    assert result == output_path
    assert output_path.read_bytes() == b"fake-mp3-bytes"


def test_generate_music_wires_submit_poll_download(tmp_path):
    output_path = tmp_path / "Music_Full.mp3"

    with patch("music_generation.submit_music_task", return_value="music123") as mock_submit, \
         patch("music_generation.poll_music_task", return_value="https://example.com/track1.mp3") as mock_poll, \
         patch("music_generation.download_music", return_value=output_path) as mock_download:
        result = generate_music("gentle medieval folk ambient instrumental", output_path, instrumental=True, model="V4_5")

    mock_submit.assert_called_once_with("gentle medieval folk ambient instrumental", True, "V4_5")
    mock_poll.assert_called_once_with("music123")
    mock_download.assert_called_once_with("https://example.com/track1.mp3", output_path)
    assert result == output_path
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest test_music_generation.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'music_generation'`

- [ ] **Step 3: Write minimal implementation**

```python
# music_generation.py
import json
import subprocess
import time
import requests
from pathlib import Path

def submit_music_task(prompt: str, instrumental: bool = True, model: str = "V4_5") -> str:
    result = subprocess.run(
        [
            "kie-cli", "suno_generate_music",
            "--prompt", prompt,
            "--customMode", "false",
            "--instrumental", "true" if instrumental else "false",
            "--model", model,
            "--json",
        ],
        check=True, capture_output=True, text=True,
    )
    return json.loads(result.stdout)["task_id"]


def poll_music_task(task_id: str, poll_interval_seconds: float = 20.0, max_attempts: int = 12) -> str:
    for attempt in range(max_attempts):
        if attempt > 0:
            time.sleep(poll_interval_seconds)

        result = subprocess.run(
            ["kie-cli", "get_task_status", "--task_id", task_id, "--json"],
            check=True, capture_output=True, text=True,
        )
        data = json.loads(result.stdout)
        status = (data.get("status") or "").lower()

        if status in ("completed", "success"):
            return data["result_urls"][0]
        if status in ("failed", "fail"):
            raise RuntimeError(f"Music generation task {task_id} failed: {data.get('error')}")

    raise TimeoutError(f"Music generation task {task_id} did not complete within {max_attempts} attempts")


def download_music(url: str, output_path: Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    response = requests.get(url, timeout=60)
    response.raise_for_status()
    output_path.write_bytes(response.content)
    return output_path


def generate_music(prompt: str, output_path: Path, instrumental: bool = True, model: str = "V4_5") -> Path:
    task_id = submit_music_task(prompt, instrumental, model)
    music_url = poll_music_task(task_id)
    return download_music(music_url, Path(output_path))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest test_music_generation.py -v`
Expected: All 6 tests PASS

- [ ] **Step 5: Commit**

```bash
git add 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/music_generation.py 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/test_music_generation.py
git commit -m "POV pipeline: add Suno music generation with case-insensitive status handling"
```

---

### Task 4: Fit music to target duration

**Files:**
- Modify: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/music_generation.py`
- Modify: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/test_music_generation.py`

**Interfaces:**
- Produces: `fit_music_to_duration(music_path: Path, output_path: Path, target_seconds: float) -> Path` — if the track is already `<= target_seconds`, copies unchanged; if longer, trims to the first `target_seconds` (music, unlike video, doesn't need a "best window" heuristic — the opening bars work fine for a background bed); if shorter, loops it with `ffmpeg`'s `-stream_loop` to cover the target duration then trims to the exact length. Used by the pipeline's assembly step before mixing.

- [ ] **Step 1: Write the failing tests**

```python
def test_fit_music_to_duration_copies_unchanged_when_already_short_enough(tmp_path):
    music_path = tmp_path / "Music_Full.mp3"
    music_path.write_bytes(b"fake-mp3-data")
    output_path = tmp_path / "Music_Fitted.mp3"

    probe_result = MagicMock(returncode=0, stdout="65.0\n", stderr="")  # duration exactly equals target_seconds

    with patch("music_generation.subprocess.run", return_value=probe_result) as mock_run:
        result = fit_music_to_duration(music_path, output_path, target_seconds=65.0)

    assert result == output_path
    assert output_path.read_bytes() == b"fake-mp3-data"
    assert mock_run.call_count == 1
    assert mock_run.call_args[0][0][0] == "ffprobe"


def test_fit_music_to_duration_trims_when_longer(tmp_path):
    music_path = tmp_path / "Music_Full.mp3"
    output_path = tmp_path / "Music_Fitted.mp3"

    probe_result = MagicMock(returncode=0, stdout="200.0\n", stderr="")

    def fake_subprocess_run(cmd, **kwargs):
        if cmd[0] == "ffprobe":
            return probe_result
        output_path.touch()
        return MagicMock(returncode=0)

    with patch("music_generation.subprocess.run", side_effect=fake_subprocess_run) as mock_run:
        result = fit_music_to_duration(music_path, output_path, target_seconds=65.0)

    assert result == output_path
    ffmpeg_call = mock_run.call_args_list[1][0][0]
    assert ffmpeg_call[0] == "ffmpeg"
    assert "-t" in ffmpeg_call and ffmpeg_call[ffmpeg_call.index("-t") + 1] == "65.0"
    assert "-stream_loop" not in ffmpeg_call


def test_fit_music_to_duration_loops_when_shorter(tmp_path):
    music_path = tmp_path / "Music_Full.mp3"
    output_path = tmp_path / "Music_Fitted.mp3"

    probe_result = MagicMock(returncode=0, stdout="30.0\n", stderr="")

    def fake_subprocess_run(cmd, **kwargs):
        if cmd[0] == "ffprobe":
            return probe_result
        output_path.touch()
        return MagicMock(returncode=0)

    with patch("music_generation.subprocess.run", side_effect=fake_subprocess_run) as mock_run:
        result = fit_music_to_duration(music_path, output_path, target_seconds=65.0)

    assert result == output_path
    ffmpeg_call = mock_run.call_args_list[1][0][0]
    assert ffmpeg_call[0] == "ffmpeg"
    assert "-stream_loop" in ffmpeg_call
    assert "-t" in ffmpeg_call and ffmpeg_call[ffmpeg_call.index("-t") + 1] == "65.0"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest test_music_generation.py -v -k fit_music_to_duration`
Expected: FAIL with `ImportError: cannot import name 'fit_music_to_duration'`

- [ ] **Step 3: Write minimal implementation**

Three distinct branches: exactly at target -> copy unchanged; longer -> trim; shorter -> loop then trim.

```python
import shutil

def fit_music_to_duration(music_path: Path, output_path: Path, target_seconds: float) -> Path:
    music_path = Path(music_path)
    output_path = Path(output_path)

    duration_result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(music_path)],
        check=True, capture_output=True, text=True,
    )
    duration = float(duration_result.stdout.strip())

    if duration == target_seconds:
        shutil.copy(music_path, output_path)
        return output_path

    if duration > target_seconds:
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(music_path), "-t", str(target_seconds), "-c", "copy", str(output_path)],
            check=True, capture_output=True, text=True,
        )
        return output_path

    # duration < target_seconds: loop the track to cover the target, then trim to the exact length
    subprocess.run(
        ["ffmpeg", "-y", "-stream_loop", "-1", "-i", str(music_path), "-t", str(target_seconds),
         "-c:a", "libmp3lame", str(output_path)],
        check=True, capture_output=True, text=True,
    )
    return output_path
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest test_music_generation.py -v`
Expected: All 9 tests PASS (6 from Task 3 + 3 new)

- [ ] **Step 5: Commit**

```bash
git add 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/music_generation.py 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/test_music_generation.py
git commit -m "POV pipeline: add fit_music_to_duration with correct trim/loop/exact three-way logic"
```

---

### Task 5: LUFS measurement, gain calculation, and audio mix

**Files:**
- Modify: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/assembly.py`
- Modify: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/test_assembly.py`

**Interfaces:**
- Consumes: nothing directly from Task 1 (independent functions in the same module)
- Produces: `measure_lufs(audio_path: Path) -> float` — runs the loudnorm measurement pass, returns `input_i` as the measured LUFS; `calculate_gain(measured_lufs: float, target_lufs: float) -> float` — returns the linear volume multiplier per the locked formula; `mix_and_normalize(foley_path: Path, music_path: Path, output_path: Path, target_lufs: float = -14.0) -> Path` — measures both tracks, calculates each one's gain to hit the target, mixes them with `ffmpeg`'s `amix` filter at the calculated volumes. Used by Task 6's final mux.

- [ ] **Step 1: Write the failing tests**

```python
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
    # volume_linear = 10 ** (7.86 / 20) ≈ 2.4768...
    result = calculate_gain(measured_lufs=-21.86, target_lufs=-14.0)
    assert abs(result - 2.4768932744) < 0.001


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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest test_assembly.py -v -k "measure_lufs or calculate_gain or mix_and_normalize"`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Write minimal implementation**

```python
import re

def measure_lufs(audio_path: Path) -> float:
    result = subprocess.run(
        ["ffmpeg", "-i", str(audio_path), "-af", "loudnorm=I=-16:LRA=11:TP=-1.5:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    match = re.search(r'"input_i"\s*:\s*"(-?[\d.]+)"', result.stderr)
    return float(match.group(1))


def calculate_gain(measured_lufs: float, target_lufs: float) -> float:
    gain_db = target_lufs - measured_lufs
    return 10 ** (gain_db / 20)


def mix_and_normalize(foley_path: Path, music_path: Path, output_path: Path, target_lufs: float = -14.0) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    foley_lufs = measure_lufs(foley_path)
    music_lufs = measure_lufs(music_path)

    foley_gain = calculate_gain(foley_lufs, target_lufs)
    music_gain = calculate_gain(music_lufs, target_lufs - 9.0)  # music sits ~9dB under foley, per the style guide's sound-design bed convention

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(foley_path), "-i", str(music_path),
            "-filter_complex",
            f"[0:a]volume={foley_gain}[a0];[1:a]volume={music_gain}[a1];[a0][a1]amix=inputs=2:duration=longest[aout]",
            "-map", "[aout]", str(output_path),
        ],
        check=True, capture_output=True, text=True,
    )
    return output_path
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest test_assembly.py -v`
Expected: All 4 tests PASS (1 from Task 1 + 3 new)

- [ ] **Step 5: Commit**

```bash
git add 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/assembly.py 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/test_assembly.py
git commit -m "POV pipeline: add measure_lufs, calculate_gain, and mix_and_normalize"
```

---

### Task 6: Final mux + versioning + SKILL.md update

**Files:**
- Modify: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/assembly.py`
- Modify: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/test_assembly.py`
- Modify: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/SKILL.md`

**Interfaces:**
- Consumes: nothing new directly (uses plain ffmpeg muxing)
- Produces: `get_next_version(production_dir: Path) -> int` — scans for existing `Final_v*.mp4` files and returns the next version number (1 if none exist); `mux_final(video_path: Path, audio_path: Path, production_dir: Path) -> Path` — muxes silent video + mixed audio into `<production_dir>/Final_v<N>.mp4` using `get_next_version()`, returns the path

- [ ] **Step 1: Write the failing tests**

```python
def test_get_next_version_returns_1_when_no_existing_finals(tmp_path):
    assert get_next_version(tmp_path) == 1


def test_get_next_version_returns_next_after_existing_finals(tmp_path):
    (tmp_path / "Final_v1.mp4").touch()
    (tmp_path / "Final_v2.mp4").touch()
    assert get_next_version(tmp_path) == 3


def test_mux_final_writes_versioned_output(tmp_path):
    video_path = tmp_path / "Video_Stitched.mp4"
    audio_path = tmp_path / "Final_Audio.mp3"
    video_path.touch()
    audio_path.touch()

    with patch("assembly.subprocess.run", return_value=MagicMock(returncode=0)) as mock_run:
        result = mux_final(video_path, audio_path, tmp_path)

    assert result == tmp_path / "Final_v1.mp4"
    ffmpeg_call = mock_run.call_args[0][0]
    assert ffmpeg_call[0] == "ffmpeg"
    assert str(video_path) in ffmpeg_call
    assert str(audio_path) in ffmpeg_call
    assert str(tmp_path / "Final_v1.mp4") in ffmpeg_call
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest test_assembly.py -v -k "get_next_version or mux_final"`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Write minimal implementation**

```python
def get_next_version(production_dir: Path) -> int:
    production_dir = Path(production_dir)
    existing = list(production_dir.glob("Final_v*.mp4"))
    if not existing:
        return 1

    versions = []
    for path in existing:
        match = re.search(r"Final_v(\d+)\.mp4", path.name)
        if match:
            versions.append(int(match.group(1)))

    return max(versions, default=0) + 1


def mux_final(video_path: Path, audio_path: Path, production_dir: Path) -> Path:
    production_dir = Path(production_dir)
    version = get_next_version(production_dir)
    output_path = production_dir / f"Final_v{version}.mp4"

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(video_path), "-i", str(audio_path),
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "copy", "-c:a", "aac", "-shortest",
            str(output_path),
        ],
        check=True, capture_output=True, text=True,
    )
    return output_path
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest test_assembly.py -v`
Expected: All 7 tests PASS (4 from Task 5 + 3 new)

- [ ] **Step 5: Update SKILL.md**

Add a new section documenting assembly, updating both the body AND the frontmatter `description` field in the same commit (per the pattern already established as mandatory for this skill folder after two prior mistakes where only one was updated):

```markdown
## Assembly (built)

**Video concatenation:** `concatenate_videos(video_paths, output_path)` in `assembly.py` — concatenates per-scene clips (video-only, audio stripped) into `Video_Stitched.mp4`.

**Audio extraction:** `extract_audio(video_path, output_path)` and `stitch_audio_files(audio_paths, output_path)` in `audio_extraction.py` — pulls each clip's native Seedance audio into `Clip_Audio/`, then stitches into `Ambient_Foley_Full.mp3`.

**Music:** `generate_music(prompt, output_path)` in `music_generation.py` — Suno via kie-cli (note: real status strings are case-varying, e.g. `"SUCCESS"` vs image generation's `"success"` — comparisons are case-insensitive). `fit_music_to_duration(music_path, output_path, target_seconds)` trims (if longer) or loops (if shorter) the track to the video's exact runtime.

**Mix + normalize:** `measure_lufs`, `calculate_gain`, `mix_and_normalize` in `assembly.py` — measures foley and music LUFS via `ffmpeg loudnorm`, calculates each track's gain to hit -14 LUFS (foley) / -23 LUFS (music, ~9dB under foley per the style guide's bed convention), mixes via `amix`.

**Final mux:** `get_next_version` and `mux_final` in `assembly.py` — muxes the silent stitched video with the mixed audio into a versioned `Final_vN.mp4` (never overwrites a prior version).

## Not yet built (updated)

YouTube trend-research ideation, text overlay (Remotion), YouTube package, and Blotato upload — each is a separate implementation plan.
```

Update the frontmatter `description` to mention assembly is now also built, alongside the existing capabilities.

- [ ] **Step 6: Commit**

```bash
git add 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/assembly.py 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/test_assembly.py 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/SKILL.md
git commit -m "POV pipeline: add get_next_version, mux_final, and document assembly in SKILL.md (body + frontmatter)"
```

---

### Task 7: Manual smoke test — real end-to-end assembly

**Files:** none created/modified — this is a validation-only task producing output artifacts under a folder Tony confirms.

- [ ] **Step 1: Ask Tony for the production folder and confirm which clips to use**

Do not default to a path. If Tony has already provided a real subject and Tasks from the beat-planning/image/video-generation plans have produced real per-scene clips for it, use those. Otherwise, propose reusing `Productions/0002_POV_Smoke_Test/scene_video_raw.mp4` (already generated) duplicated 2-3 times as stand-in clips purely to validate the assembly mechanics, and ask Tony to confirm before running.

- [ ] **Step 2: Run the full assembly chain on the confirmed clips**

```bash
python3 -c "
from pathlib import Path
import sys
sys.path.insert(0, '001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline')
from assembly import concatenate_videos, mix_and_normalize, mux_final
from audio_extraction import extract_audio, stitch_audio_files
from music_generation import generate_music, fit_music_to_duration

production_dir = Path('<confirmed production folder>')
assets_dir = production_dir / 'Assets'
clips = [<confirmed list of clip Paths>]

# Video
video_stitched = concatenate_videos(clips, assets_dir / 'Video_Stitched.mp4')

# Audio extraction + stitching
clip_audio_paths = []
for i, clip in enumerate(clips, start=1):
    audio_path = extract_audio(clip, assets_dir / 'Clip_Audio' / f'C{i:02d}_audio.mp3')
    clip_audio_paths.append(audio_path)
foley_full = stitch_audio_files(clip_audio_paths, assets_dir / 'Ambient_Foley_Full.mp3')

# Music
music_raw = generate_music('<a mood/genre prompt matching the subject>', assets_dir / 'Music_Raw.mp3')
import subprocess
duration_result = subprocess.run(
    ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', str(video_stitched)],
    check=True, capture_output=True, text=True,
)
video_duration = float(duration_result.stdout.strip())
music_fitted = fit_music_to_duration(music_raw, assets_dir / 'Music_Full.mp3', video_duration)

# Mix + mux
final_audio = mix_and_normalize(foley_full, music_fitted, assets_dir / 'Final_Audio.mp3')
final_video = mux_final(video_stitched, final_audio, production_dir)
print('Final video:', final_video)
"
```

- [ ] **Step 3: Verify and report**

Confirm every intermediate and final artifact exists and is valid via `ffprobe` (durations, codecs, file sizes). Measure the final `Final_vN.mp4`'s actual audio LUFS (`ffmpeg -i Final_vN.mp4 -af loudnorm=print_format=json -f null -`) and confirm it lands close to -14 LUFS integrated. If a command fails, diagnose whether it's a bug in this plan's code (fix it, add/update a test covering what broke, run the full test suite to confirm no regressions, commit) versus an environment/API issue (report the raw error).

- [ ] **Step 4: Commit any fixes discovered in Step 3, then stop**

Do not proceed to text overlay, YouTube package, or Blotato upload in this task — this plan ends once a real `Final_vN.mp4` is produced end to end with correctly normalized audio.

---

## Self-Review Notes

- **Spec coverage:** video concatenation (silent) ✅ (Task 1), audio extraction + stitching ✅ (Task 2), music generation via Suno with the case-insensitive status lesson applied from the start ✅ (Task 3), fitting music to the video's exact duration (trim/loop, never assume Suno respects a requested length) ✅ (Task 4), LUFS-measured mix per the locked formula (never a static guess) ✅ (Task 5), versioned final mux (`Final_vN.mp4`, never overwritten) ✅ (Task 6), real end-to-end validation ✅ (Task 7). Text overlay, YouTube package, and Blotato upload are explicitly out of scope and called out in the SKILL.md update.
- **Type consistency:** `Path` used consistently for all path parameters across `assembly.py`, `audio_extraction.py`, and `music_generation.py`; `target_seconds`/`target_lufs` are `float` consistently; `mux_final`'s dependency on `get_next_version` matches exactly (`int` return, used directly in the output filename).
- **Placeholder scan:** no TBDs; every step has runnable code and an exact command with expected output. Task 4's trim/loop/copy logic is a clean three-way branch (exact match / longer / shorter) with a corresponding fix to its first test's scenario (duration now set exactly equal to the target, not merely below it, so all three branches are genuinely distinct and independently tested). Task 7's `<confirmed production folder>`/`<confirmed list of clip Paths>` are intentional runtime confirmation gates (Step 1 requires asking Tony first), not plan placeholders.
