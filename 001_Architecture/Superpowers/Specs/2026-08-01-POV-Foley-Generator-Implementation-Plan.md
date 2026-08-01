# POV Foley/SFX Generator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone, swappable Foley/SFX generator for the Reimagined Realms POV Shorts Pipeline — takes any local video clip and produces a synced Foley/ambient audio track via either Mirelo SFX or Sonilo SFX (WaveSpeed), with the model choice controlled by a single config value so Tony's upcoming A/B test can be locked in with a one-line change.

**Architecture:** Two small functions in one module: `upload_video()` uploads a local clip to WaveSpeed's CDN via the `wavespeed` CLI and returns its URL; `generate_foley()` uses that URL to invoke either model via `wavespeed run ... --download`, writing the resulting audio file to a caller-specified path. Model selection is a single dict lookup keyed by one module-level constant. A CLI entrypoint wires it together. This is independent of the rest of the POV Shorts Pipeline (no beat planning, image gen, or video gen required) — it operates on any existing video file, including the real reference clips already downloaded by the Video-Analyzer skill.

**Tech Stack:** Python 3, the `wavespeed` CLI (already installed at `/opt/homebrew/bin/wavespeed`, already authenticated via `WAVESPEED_API_KEY` in `~/.env-secrets`), `pytest`.

## Global Constraints

- Skill folder: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/` (already exists, confirmed with Tony — contains `POV_Style_Guide.md`; add new files here, do not create a different folder).
- Plan/spec docs live in `001_Architecture/Superpowers/Specs/` (confirmed with Tony).
- **The Foley model MUST be swappable via a single config value.** A module-level constant `FOLEY_MODEL` (one of `"mirelo"` or `"sonilo"`) selects the model through a dict lookup. Changing the default after the A/B test means editing exactly one line — no code restructuring, no touching call sites.
- Model IDs (confirmed live against the `wavespeed` CLI, do not substitute other values): `"mirelo"` → `"mirelo-ai/sfx-v1/video-to-audio"`, `"sonilo"` → `"sonilo/v1/video-to-sfx"`.
- No hardcoded input/output paths anywhere — every function takes paths as parameters, the CLI takes them as arguments.
- All external calls (the `wavespeed` CLI) must be mockable in tests — no test may require live network/API access except the final manual smoke-test task.
- No new directories may be created beyond what's explicitly confirmed in this plan. If execution surfaces a need for another new folder, stop and ask Tony first.
- Do not build the rest of the POV Shorts Pipeline (beat planning, shot list, cost estimator, image/video generation, assembly, text overlay, YouTube package, Blotato upload) in this plan — those are separate, later plans per the approved design spec at `001_Architecture/Superpowers/Specs/2026-08-01-RR-POV-Shorts-Pipeline-Design.md`.

---

### Task 1: Foley model config + video upload function

**Files:**
- Create: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/foley_config.py`
- Create: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/generate_foley.py`
- Create: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/test_generate_foley.py`

**Interfaces:**
- Produces: `FOLEY_MODEL: str` and `FOLEY_MODELS: dict[str, str]` (in `foley_config.py`); `upload_video(video_path: Path) -> str` (in `generate_foley.py`) — uploads a local file via the `wavespeed` CLI and returns its CDN URL, used by Task 2

- [ ] **Step 1: Write `foley_config.py`**

```python
# The single swap point for the Foley A/B test: change this one line, nothing else,
# to switch the default model once Tony picks a winner.
FOLEY_MODEL = "mirelo"

FOLEY_MODELS = {
    "mirelo": "mirelo-ai/sfx-v1/video-to-audio",
    "sonilo": "sonilo/v1/video-to-sfx",
}
```

- [ ] **Step 2: Write the failing test for `upload_video`**

```python
# test_generate_foley.py
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from generate_foley import upload_video

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
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline && python3 -m pytest test_generate_foley.py::test_upload_video_calls_wavespeed_and_returns_url -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'generate_foley'`

- [ ] **Step 4: Write minimal implementation**

```python
# generate_foley.py
import argparse
import json
import subprocess
from pathlib import Path
from foley_config import FOLEY_MODEL, FOLEY_MODELS

def upload_video(video_path: Path) -> str:
    result = subprocess.run(
        ["wavespeed", "upload", str(video_path), "--json"],
        check=True, capture_output=True, text=True,
    )
    return json.loads(result.stdout)["url"]
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python3 -m pytest test_generate_foley.py::test_upload_video_calls_wavespeed_and_returns_url -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/foley_config.py 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/generate_foley.py 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/test_generate_foley.py
git commit -m "POV Foley Generator: config + upload_video"
```

---

### Task 2: `generate_foley` function + CLI entrypoint + SKILL.md

**Files:**
- Modify: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/generate_foley.py`
- Modify: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/test_generate_foley.py`
- Create: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/SKILL.md`

**Interfaces:**
- Consumes: `upload_video(video_path: Path) -> str` (Task 1), `FOLEY_MODEL: str`, `FOLEY_MODELS: dict[str, str]` (Task 1's `foley_config.py`)
- Produces: `generate_foley(video_path: Path, output_path: Path, prompt: str = "", model: str | None = None) -> Path` — the function later tasks (and Tony's A/B test) call directly; `main(video: str, out: str, prompt: str = "", model: str | None = None) -> None` — CLI entrypoint

- [ ] **Step 1: Write the failing tests**

```python
def test_generate_foley_uploads_then_runs_model_and_downloads_output(tmp_path):
    video_path = tmp_path / "clip.mp4"
    video_path.touch()
    output_path = tmp_path / "clip_foley.wav"

    mock_run_result = MagicMock(returncode=0)

    with patch("generate_foley.upload_video", return_value="https://example.com/clip.mp4") as mock_upload, \
         patch("generate_foley.subprocess.run", return_value=mock_run_result) as mock_run:

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

        generate_foley(video_path, output_path, model="sonilo")

    called_cmd = mock_run.call_args[0][0]
    assert "sonilo/v1/video-to-sfx" in called_cmd


def test_main_wires_generate_foley(tmp_path):
    with patch("generate_foley.generate_foley") as mock_generate:
        mock_generate.return_value = tmp_path / "out.wav"
        main(str(tmp_path / "clip.mp4"), str(tmp_path / "out.wav"), prompt="water sloshing", model="mirelo")

    mock_generate.assert_called_once_with(
        Path(str(tmp_path / "clip.mp4")), Path(str(tmp_path / "out.wav")), "water sloshing", "mirelo",
    )
```

(Add `from generate_foley import generate_foley, main` to the test file's imports.)

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest test_generate_foley.py -v -k "generate_foley or main_wires"`
Expected: FAIL with `ImportError: cannot import name 'generate_foley'`

- [ ] **Step 3: Write minimal implementation**

```python
def generate_foley(video_path: Path, output_path: Path, prompt: str = "", model: str | None = None) -> Path:
    model_id = FOLEY_MODELS[model or FOLEY_MODEL]
    video_url = upload_video(video_path)

    cmd = ["wavespeed", "run", model_id, "-i", f"video={video_url}"]
    if prompt:
        cmd += ["-i", f"prompt={prompt}"]
    cmd += ["--download", str(output_path)]

    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return output_path


def main(video: str, out: str, prompt: str = "", model: str | None = None) -> None:
    generate_foley(Path(video), Path(out), prompt, model)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate synced Foley/SFX audio for a video clip via a swappable model (Mirelo or Sonilo)."
    )
    parser.add_argument("video", help="Path to local video clip")
    parser.add_argument("--out", required=True, help="Output audio file path")
    parser.add_argument("--prompt", default="", help="Optional text hint guiding the sound effect generation")
    parser.add_argument(
        "--model", choices=["mirelo", "sonilo"], default=None,
        help="Override the default FOLEY_MODEL (from foley_config.py) for this single call",
    )
    args = parser.parse_args()
    main(args.video, args.out, args.prompt, args.model)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest test_generate_foley.py -v`
Expected: All tests PASS

- [ ] **Step 5: Write `SKILL.md`**

```markdown
---
name: reimagined-realms-pov-shorts-pipeline
description: Use when building Reimagined Realms POV Shorts (vertical historical "day in the life" videos with no dialogue). This skill folder currently contains the Foley/SFX generator sub-component only — beat planning, image/video generation, assembly, and publishing are separate, later plans. Foley invocation — python3 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/generate_foley.py <video_path> --out <audio_output_path> [--prompt "text hint"] [--model mirelo|sonilo]
---

# Reimagined Realms POV Shorts Pipeline

Vertical (9:16), historical "day in the life" POV videos with no dialogue for the Reimagined Realms channel. See the full design at `001_Architecture/Superpowers/Specs/2026-08-01-RR-POV-Shorts-Pipeline-Design.md` and the distilled reference conventions at `POV_Style_Guide.md` in this folder.

## Foley/SFX Generator (built)

`generate_foley.py` takes any local video clip and produces a synced Foley/ambient audio track via either Mirelo SFX or Sonilo SFX (both on WaveSpeed) — used per-clip in the pipeline's sound design phase, and standalone for Tony's A/B model comparison.

**Usage:**

```bash
python3 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/generate_foley.py \
  "<video_path>" --out "<audio_output_path>" --prompt "footsteps on straw" --model mirelo
```

**Swapping the default model:** edit `FOLEY_MODEL` in `foley_config.py` — that's the only line that needs to change after the A/B test picks a winner. `--model` on the CLI overrides the default for a single call without touching the config file (useful for the A/B test itself, running both models against the same clip).

## Not yet built

Beat planning, shot list generation, cost estimation, image/video generation, assembly, text overlay, YouTube package, and Blotato upload — each is a separate implementation plan per the design spec's phase list.
```

- [ ] **Step 6: Commit**

```bash
git add 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/generate_foley.py 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/test_generate_foley.py 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/SKILL.md
git commit -m "POV Foley Generator: add generate_foley, CLI entrypoint, and SKILL.md"
```

---

### Task 3: Register skill in Skill-Index

**Files:**
- Modify: `001_Architecture/Skills/Skill-Index.md` (via existing sync script — do not hand-edit)

- [ ] **Step 1: Regenerate the skill index**

Run: `python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/sync_skill_index.py`
Expected: Script completes without error; `git diff 001_Architecture/Skills/Skill-Index.md` shows a new `reimagined-realms-pov-shorts-pipeline` entry (the description references the Foley generator's current scope).

- [ ] **Step 2: Commit**

```bash
git add 001_Architecture/Skills/Skill-Index.md
git commit -m "POV Foley Generator: register skill in Skill-Index"
```

---

### Task 4: Manual A/B smoke test — Mirelo vs Sonilo on a real clip

**Files:** none created/modified — this is a validation-only task, and is the actual deliverable Tony asked for (the A/B comparison itself).

- [ ] **Step 1: Confirm the test clip and output locations with Tony before running**

Do not default to a path. Propose using the already-downloaded real reference clip from the Video-Analyzer smoke test — `002_Content-Creation/Video_Editor/002_Channels/003_Reimagined-Realms/Case_Studies/001_POV_Medieval_Peasant/Video.mp4` (a real ~40s POV Short, already on disk, no new generation needed) — and ask where Tony wants the two output audio files saved (e.g. alongside that same video, or a new location he names).

- [ ] **Step 2: Run both models against the same clip**

```bash
python3 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/generate_foley.py \
  "<confirmed clip path>" --out "<confirmed output dir>/mirelo_test.wav" \
  --prompt "medieval village ambience: crackling fire, footsteps, water sloshing, birds" --model mirelo

python3 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/generate_foley.py \
  "<confirmed clip path>" --out "<confirmed output dir>/sonilo_test.wav" \
  --prompt "medieval village ambience: crackling fire, footsteps, water sloshing, birds" --model sonilo
```

- [ ] **Step 3: Present both outputs to Tony for a listen, and report which model produced which file clearly labeled**

Do not pick a winner yourself — this is explicitly Tony's call per the pipeline design spec's A/B test protocol.

- [ ] **Step 4: Once Tony picks a winner, update `FOLEY_MODEL` in `foley_config.py` to match and commit**

```python
FOLEY_MODEL = "mirelo"  # or "sonilo" — updated after Tony's A/B test decision
```

```bash
git add 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/foley_config.py
git commit -m "POV Foley Generator: lock in <mirelo|sonilo> as default per Tony's A/B test result"
```

---

## Self-Review Notes

- **Spec coverage:** swappable Foley model via single config constant ✅ (Task 1's `foley_config.py`, Global Constraints), video upload ✅ (Task 1), Foley generation via either model ✅ (Task 2), CLI usability ✅ (Task 2), real A/B test on real content ✅ (Task 4), no hardcoded paths ✅ (all functions take paths as parameters), mockable external calls ✅ (all `wavespeed` CLI calls go through `subprocess.run`, mocked in every test except Task 4).
- **Type consistency:** `video_path`/`output_path` are `Path` throughout `generate_foley.py`; `model` is `str | None` consistently between `generate_foley()` and `main()`; `FOLEY_MODELS` keys (`"mirelo"`, `"sonilo"`) match the CLI's `--model` choices and Task 4's usage exactly.
- **Placeholder scan:** no TBDs; every step has runnable code and an exact command with expected output. Task 4's paths are intentionally left as `<confirmed clip path>` placeholders in the plan text because Task 4's own Step 1 requires asking Tony for them before running — this is a genuine runtime confirmation gate, not a plan placeholder.
