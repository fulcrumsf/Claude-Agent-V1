# POV Text Overlay Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Composite per-scene text captions ("WAKING UP AS A ___", "FETCHING WATER FROM THE WELL", etc.) onto the assembled `Final_vN.mp4`, using the existing Remotion project's established composition-registry pattern, driven by a Python wrapper that stays consistent with the rest of this pipeline.

**Architecture:** Two new Remotion (TypeScript/React) files in the existing `002_Content-Creation/Video_Editor/003_Remotion/` project — a `POVCaption` component (the visual caption card: white text, centered, drop shadow, fade in/out, per the style guide's conventions) and a `POVShort` composition (background video via `OffthreadVideo` + timed caption overlays), registered in the existing `Root.tsx` alongside the project's other compositions (e.g. `NeonParcelTitleOverlay`, which is the closest existing precedent — same 9:16 aspect ratio). A new Python module, `text_overlay.py`, in the pipeline's skill folder builds the caption-timing props JSON, manages the `public/` symlink the Remotion project's existing render scripts already use (see `render_bioluminescence.sh` for the established pattern), and invokes `npx remotion render` via subprocess — the same CLI-first, subprocess-driven approach every other generation step in this pipeline already uses.

**Tech Stack:** TypeScript/React (Remotion, existing project — no new dependencies), Python 3 (`text_overlay.py`), `pytest` (Python-testable parts only — see the TDD note below).

## Global Constraints

- Skill folder for the Python wrapper: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/` (already exists — add `text_overlay.py` and its tests here, alongside `assembly.py`, `beat_planning.py`, `shot_list_builder.py`, `image_generation.py`, `video_generation.py`, `audio_extraction.py`, `music_generation.py`, `generate_foley.py`, `foley_config.py`, `POV_Style_Guide.md`, `SKILL.md`).
- Remotion project location (already exists, do not relocate or restructure): `002_Content-Creation/Video_Editor/003_Remotion/`. New component files go in `src/remotion/video-components/` alongside `NeonParcelTitleOverlay.tsx`, `SceneOverlay.tsx`, etc. The new composition is registered in the existing `src/remotion/Root.tsx` (add to, do not restructure the existing `<Composition>` list).
- Aspect ratio/resolution: 1080×1920 (9:16), matching `NeonParcelTitleOverlay`'s existing composition and this pipeline's video generation spec.
- Caption style per `POV_Style_Guide.md`'s "Text overlay conventions" section: white text, centered, drop shadow present, one caption per vignette/scene, appears at the scene's cut and stays for the scene's duration. Opening premise text ("POV: You Wake Up As A ___") is larger/more prominent than per-vignette labels.
- **TDD note — this plan's tests apply Python-only.** The two Remotion/TSX tasks (Task 1, Task 2) have no existing test convention in this project (confirmed: zero `.test.tsx`/`.spec.tsx` files exist anywhere under `003_Remotion/src/`) — visual/animation React components in this codebase are verified via `npx remotion studio` (interactive preview) or a still-frame render, not automated tests. Do not invent a testing framework for these two tasks; follow the existing convention (write the component, verify visually via a still render, move on). Tasks 3-4 (the Python wrapper) follow the same strict TDD process as every other Python module in this pipeline.
- No hardcoded output paths in the Python wrapper — every function takes paths as parameters.
- All external calls in the Python wrapper (subprocess, filesystem) must be mockable in tests — no test may require a live Remotion render except the final manual smoke-test task.
- No new directories may be created beyond what's explicitly confirmed in this plan. If execution surfaces a need for another new folder, stop and ask Tony first.
- This plan does NOT cover: YouTube trend-research ideation, YouTube package, or Blotato upload — separate later plans.

---

### Task 1: POVCaption component

**Files:**
- Create: `002_Content-Creation/Video_Editor/003_Remotion/src/remotion/video-components/POVCaption.tsx`

**Interfaces:**
- Produces: `POVCaption` React component (props: `text: string`, `startS: number`, `durationS: number`, `variant: "title" | "label"`) and a `POVCaptionData` / `TimedCaption` TypeScript interface (`{ text: string; startS: number; durationS: number; variant: "title" | "label" }`) — both consumed by Task 2's `POVShort` composition.

- [ ] **Step 1: Write the component**

```tsx
// POVCaption.tsx
import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate } from "remotion";

export interface TimedCaption {
  text: string;
  startS: number;
  durationS: number;
  variant: "title" | "label";
}

const FADE_FRAMES = 8;

function useCaptionVisibility(startS: number, durationS: number) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const startFrame = Math.round(startS * fps);
  const endFrame = Math.round((startS + durationS) * fps);

  const opacity = interpolate(
    frame,
    [startFrame, startFrame + FADE_FRAMES, endFrame - FADE_FRAMES, endFrame],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  return { opacity, visible: frame >= startFrame && frame < endFrame };
}

export const POVCaption: React.FC<{
  text: string;
  startS: number;
  durationS: number;
  variant: "title" | "label";
}> = ({ text, startS, durationS, variant }) => {
  const { opacity, visible } = useCaptionVisibility(startS, durationS);
  if (!visible && opacity === 0) return null;

  const isTitle = variant === "title";

  return (
    <div
      style={{
        position: "absolute",
        top: isTitle ? "42%" : undefined,
        bottom: isTitle ? undefined : 140,
        left: "50%",
        transform: "translateX(-50%)",
        opacity,
        maxWidth: "88%",
        textAlign: "center",
        pointerEvents: "none",
        color: "#FFFFFF",
        fontFamily: "'Arial', 'Helvetica Neue', sans-serif",
        fontWeight: 700,
        letterSpacing: "0.02em",
        textTransform: "uppercase",
        fontSize: isTitle ? 64 : 40,
        lineHeight: 1.2,
        textShadow: "0 2px 10px rgba(0,0,0,0.85), 0 4px 24px rgba(0,0,0,0.6)",
      }}
    >
      {text}
    </div>
  );
};
```

- [ ] **Step 2: Verify visually**

This component has no automated test (see the plan's TDD note). Verify it renders correctly by starting Remotion Studio and checking the component visually once Task 2 wires it into a composition — do not attempt to preview `POVCaption` in isolation, since it requires a `VideoConfig`/frame context Remotion Studio only provides inside a registered `<Composition>`. Defer visual verification to Task 2's Step 2.

- [ ] **Step 3: Commit**

```bash
git add 002_Content-Creation/Video_Editor/003_Remotion/src/remotion/video-components/POVCaption.tsx
git commit -m "POV pipeline: add POVCaption Remotion component"
```

---

### Task 2: POVShort composition + Root.tsx registration

**Files:**
- Create: `002_Content-Creation/Video_Editor/003_Remotion/src/remotion/video-components/POVShort.tsx`
- Modify: `002_Content-Creation/Video_Editor/003_Remotion/src/remotion/Root.tsx`

**Interfaces:**
- Consumes: `POVCaption`, `TimedCaption` (Task 1)
- Produces: `POVShort` React component (props: `backgroundVideoFile: string` — a `staticFile()`-relative filename inside the production's `public/` symlink; `captions: TimedCaption[]`), registered as composition id `"POVShort"` in `Root.tsx`. Used by Task 4's `render_text_overlay()` via the `remotion render POVShort ...` CLI invocation.

- [ ] **Step 1: Write the composition**

```tsx
// POVShort.tsx
import React from "react";
import { AbsoluteFill, OffthreadVideo, staticFile, Composition } from "remotion";
import { POVCaption, TimedCaption } from "./POVCaption";

export const POVShort: React.FC<{
  backgroundVideoFile: string;
  captions: TimedCaption[];
}> = ({ backgroundVideoFile, captions }) => (
  <AbsoluteFill style={{ backgroundColor: "#000" }}>
    <OffthreadVideo src={staticFile(backgroundVideoFile)} />
    {captions.map((c, i) => (
      <POVCaption key={i} text={c.text} startS={c.startS} durationS={c.durationS} variant={c.variant} />
    ))}
  </AbsoluteFill>
);
```

- [ ] **Step 2: Register the composition in Root.tsx**

Add this import near the other `video-components` imports (alongside `NeonParcelTitleOverlay`):

```tsx
import { POVShort } from "./video-components/POVShort";
```

Add this `<Composition>` block near the other 9:16 composition (`NeonParcelTitleOverlay`), inside the existing `<>...</>` fragment — do not remove or reorder any existing compositions:

```tsx
{/* Reimagined Realms POV Shorts — text overlay pass over an assembled Final_vN.mp4 */}
<Composition
  id="POVShort"
  component={POVShort}
  durationInFrames={1560}
  fps={24}
  width={1080}
  height={1920}
  defaultProps={{
    backgroundVideoFile: "Final_v1.mp4",
    captions: [
      { text: "POV: WAKING UP AS A ___", startS: 0, durationS: 4, variant: "title" as const },
    ],
  }}
/>
```

(The `durationInFrames: 1560` default is a placeholder for the Studio preview default only — 65 seconds at 24fps — the real render always overrides this via `--props` at render time per Task 4's `render_text_overlay()`, which computes the actual duration from the real background video.)

- [ ] **Step 3: Verify visually**

Run: `cd 002_Content-Creation/Video_Editor/003_Remotion && npx remotion studio`
Open the `POVShort` composition in the Studio UI. Confirm the caption text renders white, centered, with a visible drop shadow, and fades in/out smoothly. This is a manual visual check — there is no automated assertion for this step (see the plan's TDD note).

- [ ] **Step 4: Commit**

```bash
git add 002_Content-Creation/Video_Editor/003_Remotion/src/remotion/video-components/POVShort.tsx 002_Content-Creation/Video_Editor/003_Remotion/src/remotion/Root.tsx
git commit -m "POV pipeline: add POVShort composition, register in Root.tsx"
```

---

### Task 3: Caption props construction (Python)

**Files:**
- Create: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/text_overlay.py`
- Create: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/test_text_overlay.py`

**Interfaces:**
- Produces: `build_caption_props(background_video_file: str, captions: list[dict], fps: int = 24) -> dict` — assembles the exact props dict shape `POVShort` expects (`{"backgroundVideoFile": ..., "captions": [...]}`), used by Task 3's `write_props_file`. Each caption dict has keys `"text"`, `"start_s"`, `"duration_s"`, `"variant"` (`"title"` or `"label"`) — note the Python-side snake_case keys are converted to the TSX component's camelCase keys (`startS`, `durationS`) inside this function, so callers never have to think about the naming convention mismatch. `write_props_file(props: dict, output_path: Path) -> Path` — writes the props dict as JSON to disk.

- [ ] **Step 1: Write the failing tests**

```python
# test_text_overlay.py
import json
from pathlib import Path
from text_overlay import build_caption_props, write_props_file

def test_build_caption_props_converts_snake_case_to_camel_case():
    captions = [
        {"text": "POV: WAKING UP AS A PYRAMID BUILDER", "start_s": 0, "duration_s": 4, "variant": "title"},
        {"text": "FETCHING WATER", "start_s": 4, "duration_s": 5, "variant": "label"},
    ]

    result = build_caption_props("Final_v1.mp4", captions, fps=24)

    assert result == {
        "backgroundVideoFile": "Final_v1.mp4",
        "captions": [
            {"text": "POV: WAKING UP AS A PYRAMID BUILDER", "startS": 0, "durationS": 4, "variant": "title"},
            {"text": "FETCHING WATER", "startS": 4, "durationS": 5, "variant": "label"},
        ],
    }


def test_write_props_file_writes_valid_json(tmp_path):
    props = {"backgroundVideoFile": "Final_v1.mp4", "captions": []}
    output_path = tmp_path / "props.json"

    result = write_props_file(props, output_path)

    assert result == output_path
    assert json.loads(output_path.read_text()) == props
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline && python3 -m pytest test_text_overlay.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'text_overlay'`

- [ ] **Step 3: Write minimal implementation**

```python
# text_overlay.py
import json
from pathlib import Path

def build_caption_props(background_video_file: str, captions: list[dict], fps: int = 24) -> dict:
    return {
        "backgroundVideoFile": background_video_file,
        "captions": [
            {
                "text": c["text"],
                "startS": c["start_s"],
                "durationS": c["duration_s"],
                "variant": c["variant"],
            }
            for c in captions
        ],
    }


def write_props_file(props: dict, output_path: Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(props, indent=2))
    return output_path
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest test_text_overlay.py -v`
Expected: All 2 tests PASS

- [ ] **Step 5: Commit**

```bash
git add 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/text_overlay.py 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/test_text_overlay.py
git commit -m "POV pipeline: add build_caption_props and write_props_file"
```

---

### Task 4: Public symlink + render invocation (Python) + SKILL.md update

**Files:**
- Modify: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/text_overlay.py`
- Modify: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/test_text_overlay.py`
- Modify: `001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/SKILL.md`

**Interfaces:**
- Consumes: `write_props_file(props, output_path) -> Path` (Task 3)
- Produces: `ensure_public_symlink(production_dir: Path, symlink_name: str) -> Path` — creates (if missing) a symlink at `002_Content-Creation/Video_Editor/003_Remotion/public/<symlink_name>` pointing to `production_dir`, matching the existing convention already used by `render_bioluminescence.sh`; returns the symlink path. `render_text_overlay(props_path: Path, output_path: Path) -> Path` — invokes `npx remotion render POVShort <output_path> --props=<props_path> --codec h264` via subprocess from the Remotion project directory, returns `output_path`.

- [ ] **Step 1: Write the failing tests**

```python
def test_ensure_public_symlink_creates_symlink_when_missing(tmp_path):
    production_dir = tmp_path / "Productions" / "0003_Pyramid_Builder"
    production_dir.mkdir(parents=True)

    remotion_public_dir = tmp_path / "003_Remotion" / "public"
    remotion_public_dir.mkdir(parents=True)

    with patch("text_overlay.REMOTION_PUBLIC_DIR", remotion_public_dir):
        result = ensure_public_symlink(production_dir, "0003_pyramid_builder")

    expected_symlink = remotion_public_dir / "0003_pyramid_builder"
    assert result == expected_symlink
    assert expected_symlink.is_symlink()
    assert expected_symlink.resolve() == production_dir.resolve()


def test_ensure_public_symlink_leaves_existing_symlink_untouched(tmp_path):
    production_dir = tmp_path / "Productions" / "0003_Pyramid_Builder"
    production_dir.mkdir(parents=True)

    remotion_public_dir = tmp_path / "003_Remotion" / "public"
    remotion_public_dir.mkdir(parents=True)
    existing_symlink = remotion_public_dir / "0003_pyramid_builder"
    existing_symlink.symlink_to(production_dir)

    with patch("text_overlay.REMOTION_PUBLIC_DIR", remotion_public_dir):
        result = ensure_public_symlink(production_dir, "0003_pyramid_builder")

    assert result == existing_symlink
    assert existing_symlink.is_symlink()


def test_render_text_overlay_calls_remotion_cli(tmp_path):
    props_path = tmp_path / "props.json"
    output_path = tmp_path / "Final_v2.mp4"
    props_path.touch()

    mock_result = MagicMock(returncode=0)

    with patch("text_overlay.subprocess.run", return_value=mock_result) as mock_run:
        result = render_text_overlay(props_path, output_path)

    assert result == output_path
    mock_run.assert_called_once_with(
        ["npx", "remotion", "render", "POVShort", str(output_path), f"--props={props_path}", "--codec", "h264"],
        cwd=str(REMOTION_PROJECT_DIR),
        check=True, capture_output=True, text=True,
    )
```

(Add `from unittest.mock import patch, MagicMock` and `from text_overlay import ensure_public_symlink, render_text_overlay, REMOTION_PROJECT_DIR` to the test file's imports.)

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest test_text_overlay.py -v -k "ensure_public_symlink or render_text_overlay"`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Write minimal implementation**

```python
import subprocess

REMOTION_PROJECT_DIR = Path("/Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/003_Remotion")
REMOTION_PUBLIC_DIR = REMOTION_PROJECT_DIR / "public"


def ensure_public_symlink(production_dir: Path, symlink_name: str) -> Path:
    production_dir = Path(production_dir)
    symlink_path = REMOTION_PUBLIC_DIR / symlink_name

    if not symlink_path.is_symlink():
        symlink_path.symlink_to(production_dir)

    return symlink_path


def render_text_overlay(props_path: Path, output_path: Path) -> Path:
    props_path = Path(props_path)
    output_path = Path(output_path)

    subprocess.run(
        ["npx", "remotion", "render", "POVShort", str(output_path), f"--props={props_path}", "--codec", "h264"],
        cwd=str(REMOTION_PROJECT_DIR),
        check=True, capture_output=True, text=True,
    )
    return output_path
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest test_text_overlay.py -v`
Expected: All 5 tests PASS (2 from Task 3 + 3 new)

- [ ] **Step 5: Update SKILL.md**

Update BOTH the frontmatter `description` AND the body in the same commit (this skill folder has had two prior instances of only-body-updated causing a stale frontmatter, each requiring a follow-up fix round — do not repeat that a third time). Add to the body:

```markdown
## Text Overlay (built)

Composites per-scene captions onto an assembled `Final_vN.mp4` using the Remotion project at `002_Content-Creation/Video_Editor/003_Remotion/` (component: `POVCaption.tsx`, composition: `POVShort.tsx`, registered in `Root.tsx`).

**Python wrapper** (`text_overlay.py`): `build_caption_props(background_video_file, captions, fps=24)` converts snake_case caption dicts (`text`/`start_s`/`duration_s`/`variant`) into the camelCase props shape the Remotion composition expects, `write_props_file(props, output_path)` writes them to disk, `ensure_public_symlink(production_dir, symlink_name)` creates the `003_Remotion/public/<name>` symlink the composition reads its background video from (matching the existing `render_bioluminescence.sh` convention), `render_text_overlay(props_path, output_path)` invokes `npx remotion render POVShort ...` via subprocess.

Caption text/timing is decided by the orchestrating Claude session at runtime per scene (same pattern as beat planning and shot list generation) — this module only handles the mechanical props/symlink/render plumbing, never the creative wording.

## Not yet built (updated)

YouTube trend-research ideation, YouTube package, and Blotato upload — each is a separate implementation plan.
```

- [ ] **Step 6: Commit**

```bash
git add 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/text_overlay.py 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/test_text_overlay.py 001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline/SKILL.md
git commit -m "POV pipeline: add ensure_public_symlink, render_text_overlay, document text overlay in SKILL.md (body + frontmatter)"
```

---

### Task 5: Manual smoke test — real render with captions over a real video

**Files:** none created/modified — this is a validation-only task producing output artifacts under a folder Tony confirms.

- [ ] **Step 1: Ask Tony for the production folder and confirm which video/captions to use**

Do not default to a path. If a real assembled `Final_vN.mp4` exists from an actual production by this point, use it with 2-3 real captions matching its content. Otherwise, propose reusing `Productions/0002_POV_Smoke_Test/scene_video_raw.mp4` with 1-2 placeholder captions purely to validate the render mechanics, and confirm with Tony before running.

- [ ] **Step 2: Run the full text-overlay chain on the confirmed video**

```bash
python3 -c "
from pathlib import Path
import sys
sys.path.insert(0, '001_Architecture/Skills/Reimagined_Realms_POV_Shorts_Pipeline')
from text_overlay import build_caption_props, write_props_file, ensure_public_symlink, render_text_overlay

production_dir = Path('<confirmed production folder>')
symlink_name = '<confirmed short symlink name, e.g. 0002_pov_smoke_test>'
ensure_public_symlink(production_dir, symlink_name)

captions = [
    {'text': 'POV: YOU WAKE UP AS A ___', 'start_s': 0, 'duration_s': 4, 'variant': 'title'},
    {'text': 'FETCHING WATER FROM THE WELL', 'start_s': 4, 'duration_s': 5, 'variant': 'label'},
]
props = build_caption_props(f'{symlink_name}/<confirmed video filename>', captions, fps=24)
props_path = write_props_file(props, production_dir / 'Assets' / 'overlay_props.json')

output_path = render_text_overlay(props_path, production_dir / 'Final_v2.mp4')
print('Rendered:', output_path)
"
```

- [ ] **Step 3: Verify and report**

Confirm the rendered output exists and is valid via `ffprobe` (duration, resolution, codecs, file size). Visually inspect at least a few frames (e.g. via `ffmpeg -ss <time> -i <output> -frames:v 1 <frame.png>` at a few timestamps) to confirm captions appear at the expected times, are legibly white/centered/drop-shadowed, and the background video/audio plays through correctly underneath. If a command fails, diagnose whether it's a bug in this plan's code (fix it, add/update a test covering what broke if it's in the Python wrapper, run the full test suite to confirm no regressions, commit) versus an environment/tooling issue (report the raw error).

- [ ] **Step 4: Commit any fixes discovered in Step 3, then stop**

Do not proceed to YouTube package or Blotato upload in this task — this plan ends once a real caption-overlaid video is proven working end to end.

---

## Self-Review Notes

- **Spec coverage:** caption component matching style guide conventions (white, centered, drop shadow, title vs. label sizing) ✅ (Task 1), composition compositing background video + captions ✅ (Task 2), props construction with the snake_case→camelCase conversion isolated in one place ✅ (Task 3), symlink management matching the existing project convention + render invocation ✅ (Task 4), real end-to-end validation ✅ (Task 5). The plan explicitly departs from pytest-everywhere for Tasks 1-2 with a stated reason (no existing TSX test convention in this project) rather than silently skipping tests — flagged in Global Constraints, not hidden.
- **Type consistency:** `TimedCaption`'s TSX shape (`text`, `startS`, `durationS`, `variant`) matches exactly what `build_caption_props` (Python) constructs; `text_overlay.py`'s functions all take `Path`-typed path parameters consistently; `render_text_overlay`'s CLI invocation matches the composition id (`"POVShort"`) registered in Task 2 exactly.
- **Placeholder scan:** no TBDs; every step has runnable code and an exact command with expected output. Task 5's `<confirmed production folder>`/`<confirmed short symlink name>`/`<confirmed video filename>` are intentional runtime confirmation gates (Step 1 requires asking Tony first), not plan placeholders.
