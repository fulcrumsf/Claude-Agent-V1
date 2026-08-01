# Video-Analyzer Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reusable `/video-analyzer` skill that downloads any YouTube video, detects its scene boundaries, runs Gemini native video analysis for narrative/historical context per scene, and writes a merged `ANALYSIS.md` to a caller-specified folder.

**Architecture:** One Python script (`analyze_reference_video.py`) with four pure-ish functions (download, scene-detect, Gemini-analyze, merge-to-markdown) wired together by a thin CLI entrypoint, plus a `SKILL.md` that documents the command for Claude to invoke. External calls (yt-dlp subprocess, ffmpeg/ffprobe subprocess, Gemini API) are mocked in unit tests; a real end-to-end smoke test against one of Tony's two actual reference videos is the final validation task.

**Tech Stack:** Python 3, `google-genai` SDK, `yt-dlp` CLI (already installed), `ffmpeg`/`ffprobe` CLI, `pytest`, `python-dotenv` (existing `config.py` pattern).

## Global Constraints

- Skill folder: `001_Architecture/Skills/Video-Analyzer/` (confirmed with Tony — do not rename or relocate).
- Plan/spec docs live in `001_Architecture/Superpowers/Specs/` (confirmed with Tony).
- Command name: `/video-analyzer` — must not collide with the existing `/analyze-video` command (different tool, different purpose — leave that one untouched).
- No hardcoded output paths anywhere in the script — the caller always supplies `--out <folder>`.
- No new directories may be created beyond what's explicitly confirmed in this plan (`001_Architecture/Skills/Video-Analyzer/`). If execution surfaces a need for another new folder, stop and ask Tony first.
- Gemini API key comes from the existing `config.py` pattern (`GEMINI_API_KEY` or `GOOGLE_API_KEY` env var via `~/.env-secrets`) — do not invent a new key-loading mechanism.
- All external calls (yt-dlp, ffmpeg, ffprobe, Gemini) must be mockable in tests — no test may require live network/API access except the final manual smoke-test task.

---

### Task 1: Skill scaffold + download function

**Files:**
- Create: `001_Architecture/Skills/Video-Analyzer/SKILL.md`
- Create: `001_Architecture/Skills/Video-Analyzer/analyze_reference_video.py`
- Create: `001_Architecture/Skills/Video-Analyzer/test_analyze_reference_video.py`
- Create: `001_Architecture/Skills/Video-Analyzer/config.py`

**Interfaces:**
- Produces: `download_video(url: str, out_dir: Path) -> Path` — downloads via yt-dlp, returns path to `<out_dir>/Video.mp4`

- [ ] **Step 1: Write `config.py`** (copy of the established pattern, scoped to this skill so it has no cross-folder import dependency)

```python
import os
from pathlib import Path
from dotenv import load_dotenv

HOME_SECRETS = Path.home() / ".env-secrets"
load_dotenv(HOME_SECRETS)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY / GOOGLE_API_KEY is not set.")
```

- [ ] **Step 2: Write the failing test for `download_video`**

```python
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
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd 001_Architecture/Skills/Video-Analyzer && python3 -m pytest test_analyze_reference_video.py::test_download_video_calls_yt_dlp_and_returns_path -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'analyze_reference_video'`

- [ ] **Step 4: Write minimal implementation**

```python
# analyze_reference_video.py
import argparse
import subprocess
from pathlib import Path

def download_video(url: str, out_dir: Path) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    video_path = out_dir / "Video.mp4"
    subprocess.run(
        ["yt-dlp", "-f", "mp4", "-o", str(video_path), url],
        check=True, capture_output=True,
    )
    return video_path
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python3 -m pytest test_analyze_reference_video.py::test_download_video_calls_yt_dlp_and_returns_path -v`
Expected: PASS

- [ ] **Step 6: Write `SKILL.md`**

```markdown
---
name: video-analyzer
description: Use when Tony wants to reverse-engineer the style, pacing, editing, or narrative content of any reference video for any channel or project. Triggers on "analyze this video", "break down this video's style", "what's happening in this video scene by scene", or any request to understand a reference video before building something styled after it. Command: /video-analyzer <youtube_url> --out <folder>
---

# Video-Analyzer

Downloads a YouTube video, detects scene boundaries, and runs Gemini native video analysis to describe not just what's visually in each scene but the narrative/historical context (era, role, activity — e.g. "POV of a shackled pyramid worker eating porridge," not just "person eating"). Produces a per-scene `ANALYSIS.md` plus the downloaded `Video.mp4`, both written to a folder the caller specifies — this skill has no fixed output location and no channel-specific logic, so it works identically for any project.

## Usage

```bash
python3 001_Architecture/Skills/Video-Analyzer/analyze_reference_video.py "<youtube_url>" --out "<folder>"
```

Writes `<folder>/Video.mp4` and `<folder>/ANALYSIS.md`.

## Output format

`ANALYSIS.md` has one section per detected scene:

```markdown
## Scene 1 [0.0s-4.2s]
[Gemini's narrative/visual/context/sound/camera description for this scene]

## Scene 2 [4.2s-9.0s]
...
```
```

- [ ] **Step 7: Commit**

```bash
git add 001_Architecture/Skills/Video-Analyzer/SKILL.md 001_Architecture/Skills/Video-Analyzer/analyze_reference_video.py 001_Architecture/Skills/Video-Analyzer/test_analyze_reference_video.py 001_Architecture/Skills/Video-Analyzer/config.py
git commit -m "Video-Analyzer: scaffold skill + download_video"
```

---

### Task 2: Scene detection

**Files:**
- Modify: `001_Architecture/Skills/Video-Analyzer/analyze_reference_video.py`
- Modify: `001_Architecture/Skills/Video-Analyzer/test_analyze_reference_video.py`

**Interfaces:**
- Consumes: nothing from Task 1 directly (independent function), but shares the module
- Produces: `detect_scenes(video_path: Path) -> list[tuple[float, float]]` — list of `(start_seconds, end_seconds)` scene boundaries covering the full video duration, used by Task 3 and Task 4

- [ ] **Step 1: Write the failing test**

```python
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
```

(Add `from analyze_reference_video import detect_scenes` to the test file's imports.)

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest test_analyze_reference_video.py::test_detect_scenes_parses_ffmpeg_output_into_boundaries -v`
Expected: FAIL with `ImportError: cannot import name 'detect_scenes'`

- [ ] **Step 3: Write minimal implementation**

```python
import re

def detect_scenes(video_path: Path, threshold: float = 0.3) -> list[tuple[float, float]]:
    duration_result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)],
        check=True, capture_output=True, text=True,
    )
    duration = float(duration_result.stdout.strip())

    scene_result = subprocess.run(
        ["ffmpeg", "-i", str(video_path), "-filter:v",
         f"select='gt(scene,{threshold})',showinfo", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    cut_points = [float(m) for m in re.findall(r"pts_time:([\d.]+)", scene_result.stderr)]

    boundaries = [0.0] + sorted(cut_points) + [duration]
    return [(boundaries[i], boundaries[i + 1]) for i in range(len(boundaries) - 1)]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest test_analyze_reference_video.py::test_detect_scenes_parses_ffmpeg_output_into_boundaries -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add 001_Architecture/Skills/Video-Analyzer/analyze_reference_video.py 001_Architecture/Skills/Video-Analyzer/test_analyze_reference_video.py
git commit -m "Video-Analyzer: add detect_scenes"
```

---

### Task 3: Gemini narrative analysis

**Files:**
- Modify: `001_Architecture/Skills/Video-Analyzer/analyze_reference_video.py`
- Modify: `001_Architecture/Skills/Video-Analyzer/test_analyze_reference_video.py`

**Interfaces:**
- Consumes: `scenes: list[tuple[float, float]]` (Task 2's return type), `video_path: Path` (Task 1's return type)
- Produces: `analyze_video_narrative(video_path: Path, scenes: list[tuple[float, float]]) -> str` — raw text response from Gemini, one described section per scene, used by Task 4

- [ ] **Step 1: Write the failing test**

```python
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
```

(Add `from analyze_reference_video import analyze_video_narrative` to imports.)

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest test_analyze_reference_video.py::test_analyze_video_narrative_uploads_file_and_prompts_with_scene_list -v`
Expected: FAIL with `ImportError: cannot import name 'analyze_video_narrative'`

- [ ] **Step 3: Write minimal implementation**

```python
import time
from google import genai
from google.genai import types
from config import GEMINI_API_KEY

NARRATIVE_PROMPT_TEMPLATE = """
Analyze this video scene-by-scene for the following pre-detected time ranges: {scene_ranges}

For each scene, describe (as one markdown section per scene, headed "## Scene N [start-end]"):
- Visual description (subjects, setting, framing)
- What is actually happening — narrative and historical/contextual meaning (era, role, activity — e.g. "POV of a shackled pyramid worker eating porridge," not just "person eating")
- Camera type and motion (e.g. static, handheld POV, tracking)
- Sound design cues audible or implied (foley, ambient, music, dialogue presence)
- Any on-screen text or overlay style (placement, sizing, drop shadow, timing)
"""

def analyze_video_narrative(video_path: Path, scenes: list[tuple[float, float]]) -> str:
    client = genai.Client(api_key=GEMINI_API_KEY)
    uploaded = client.files.upload(file=str(video_path))
    while uploaded.state.name == "PROCESSING":
        time.sleep(2)
        uploaded = client.files.get(name=uploaded.name)

    scene_ranges = ", ".join(f"{start}s-{end}s" for start, end in scenes)
    prompt = NARRATIVE_PROMPT_TEMPLATE.format(scene_ranges=scene_ranges)

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=types.Content(parts=[
            types.Part(file_data=types.FileData(file_uri=uploaded.uri, mime_type=uploaded.mime_type)),
            types.Part(text=prompt),
        ]),
    )
    return response.text
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest test_analyze_reference_video.py::test_analyze_video_narrative_uploads_file_and_prompts_with_scene_list -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add 001_Architecture/Skills/Video-Analyzer/analyze_reference_video.py 001_Architecture/Skills/Video-Analyzer/test_analyze_reference_video.py
git commit -m "Video-Analyzer: add analyze_video_narrative"
```

---

### Task 4: Merge to ANALYSIS.md + CLI entrypoint

**Files:**
- Modify: `001_Architecture/Skills/Video-Analyzer/analyze_reference_video.py`
- Modify: `001_Architecture/Skills/Video-Analyzer/test_analyze_reference_video.py`

**Interfaces:**
- Consumes: `scenes: list[tuple[float, float]]` (Task 2), `gemini_output: str` (Task 3's return type)
- Produces: `write_analysis_md(out_dir: Path, scenes: list[tuple[float, float]], gemini_output: str) -> Path` — writes and returns path to `ANALYSIS.md`; `main()` — CLI entrypoint wiring Tasks 1-4 together

- [ ] **Step 1: Write the failing test**

```python
def test_write_analysis_md_writes_scene_headers_and_content(tmp_path):
    scenes = [(0.0, 3.1), (3.1, 7.8)]
    gemini_output = "Scene 1 text here.\n\nScene 2 text here."

    result_path = write_analysis_md(tmp_path, scenes, gemini_output)

    assert result_path == tmp_path / "ANALYSIS.md"
    content = result_path.read_text()
    assert "## Scene 1 [0.0s-3.1s]" in content
    assert "## Scene 2 [3.1s-7.8s]" in content
    assert gemini_output in content


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
```

(Add `from analyze_reference_video import write_analysis_md, main` to imports.)

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest test_analyze_reference_video.py -v -k "write_analysis_md or main_wires"`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Write minimal implementation**

```python
def write_analysis_md(out_dir: Path, scenes: list[tuple[float, float]], gemini_output: str) -> Path:
    out_dir = Path(out_dir)
    lines = []
    for i, (start, end) in enumerate(scenes, start=1):
        lines.append(f"## Scene {i} [{start}s-{end}s]")
    lines.append("")
    lines.append(gemini_output)

    analysis_path = out_dir / "ANALYSIS.md"
    analysis_path.write_text("\n".join(lines))
    return analysis_path


def main(url: str, out: str) -> None:
    out_dir = Path(out)
    video_path = download_video(url, out_dir)
    scenes = detect_scenes(video_path)
    gemini_output = analyze_video_narrative(video_path, scenes)
    write_analysis_md(out_dir, scenes, gemini_output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze a reference video's style, pacing, and narrative context.")
    parser.add_argument("url", help="YouTube URL to analyze")
    parser.add_argument("--out", required=True, help="Output folder for Video.mp4 and ANALYSIS.md")
    args = parser.parse_args()
    main(args.url, args.out)
```

Note: this `write_analysis_md` is intentionally simple — it doesn't try to split `gemini_output` per scene (Gemini's own response already contains its own `## Scene N` headers per the prompt in Task 3, so the scene boundary lines here are a structural index above the full response, not a per-scene split). If real output from Task 6's smoke test shows Gemini's headers and this index conflict or duplicate confusingly, that's a one-line follow-up fix to `write_analysis_md`, not a redesign.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest test_analyze_reference_video.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add 001_Architecture/Skills/Video-Analyzer/analyze_reference_video.py 001_Architecture/Skills/Video-Analyzer/test_analyze_reference_video.py
git commit -m "Video-Analyzer: add write_analysis_md, main, and CLI entrypoint"
```

---

### Task 5: Register skill in Skill-Index and verify dependencies

**Files:**
- Modify: `001_Architecture/Skills/Skill-Index.md` (via existing sync script — do not hand-edit)
- Read only: `001_Architecture/Tools/Video-Generation/Generic_Tools/config.py` (reference, not modified)

- [ ] **Step 1: Confirm `google-genai` and `python-dotenv` are installed for whichever Python environment this script will run under**

Run: `python3 -c "import google.genai, dotenv; print('ok')"`
Expected: `ok`. If `ImportError`, install with `pip3 install google-genai python-dotenv` before continuing (ask Tony first if this requires a new virtualenv/venv folder — do not create one unannounced per the directory rule).

- [ ] **Step 2: Regenerate the skill index so `/video-analyzer` is discoverable**

Run: `python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/sync_skill_index.py`
Expected: Script completes without error; `git diff 001_Architecture/Skills/Skill-Index.md` shows a new `video-analyzer` entry.

- [ ] **Step 3: Commit**

```bash
git add 001_Architecture/Skills/Skill-Index.md
git commit -m "Video-Analyzer: register in Skill-Index"
```

---

### Task 6: Manual smoke test against Tony's two real reference videos

**Files:** none created/modified — this is a validation-only task producing output artifacts under a folder Tony confirms.

- [ ] **Step 1: Ask Tony where to save the two real analysis outputs**

Do not default to a path. Confirm the exact output folder (e.g. under the future POV pipeline's `References/` folder, once that pipeline folder exists — or a temporary location Tony names now).

- [ ] **Step 2: Run the skill against both reference videos**

```bash
python3 001_Architecture/Skills/Video-Analyzer/analyze_reference_video.py \
  "https://www.youtube.com/shorts/rHwmFBwwkdU" --out "<folder confirmed in Step 1>/Ref1"

python3 001_Architecture/Skills/Video-Analyzer/analyze_reference_video.py \
  "https://www.youtube.com/shorts/-9NP4vwIy3Q" --out "<folder confirmed in Step 1>/Ref2"
```

- [ ] **Step 3: Read both `ANALYSIS.md` outputs and present a summary to Tony**

Confirm the narrative/historical-context descriptions read as intended (era, role, activity — not just object lists) before treating this skill as done. If the output quality is off (e.g. Gemini describes objects but misses "this is a POV of an enslaved worker," or scene boundaries are too granular/coarse), that's feedback to fix in `analyze_reference_video.py`, not a sign to add scope elsewhere.

- [ ] **Step 4: Commit any fixes discovered in Step 3, then stop — do not proceed to building the POV Style Guide or the pipeline itself in this task**

The POV Style Guide synthesis and the Reimagined Realms POV Shorts Pipeline are separate plans per the brainstorming decomposition — this plan ends once `/video-analyzer` is proven working against both real reference videos.

---

## Self-Review Notes

- **Spec coverage:** yt-dlp download ✓ (Task 1), scene segmentation ✓ (Task 2), Gemini narrative analysis with era/role/activity framing ✓ (Task 3), merged per-scene `ANALYSIS.md` ✓ (Task 4), caller-specified output folder (no hardcoded paths) ✓ (all tasks take `out_dir`/`--out` as a parameter), stateless/no channel-specific logic ✓ (verified no Reimagined-Realms-specific code anywhere in the script), real-video validation ✓ (Task 6).
- **Type consistency:** `Path` used consistently for `video_path`/`out_dir` across all four functions; `scenes` is always `list[tuple[float, float]]`; `main(url: str, out: str)` matches the CLI's `args.url`/`args.out` types.
- **Placeholder scan:** no TBDs; every step has runnable code and an exact command with expected output.
