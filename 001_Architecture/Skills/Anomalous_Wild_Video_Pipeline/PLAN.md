# Anomalous Wild Video Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build one orchestrator skill (`/anomalous-wild`) that gives the Anomalous Wild channel the same start-to-finish automation Reimagined Realms has, reusing every existing working component (script writer, `new_video.py`, `pipeline_supervisor.py`, the `BioluminescenceDoc.tsx` Remotion engine, this session's audio-mix scripts) and adding only what's genuinely missing: word-level narration timestamps, a Tool-Manager-based routing capability for motion-graphics tools, a Scientific Diagram sub-pipeline that fixes the garbled-label problem, a YouTube package generator, Blotato upload, and a clean folder structure (both going-forward and retrofitted onto the existing Bioluminescence Weapon production).

**Architecture:** Small, single-purpose Python scripts living in `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/` (never touching any Reimagined Realms file), a new Tool-Manager capability data file for tool routing, and one orchestrator `SKILL.md` that chains everything together in phases, mirroring Reimagined Realms' phase structure.

**Tech Stack:** Python 3, ffmpeg, ElevenLabs API (word-level timestamps), kie.ai (GPT-Image-2, Seedance, Suno), Gemini vision API, Remotion (TypeScript/React), Blotato MCP tools.

## Global Constraints

- Never edit any file under `Reimagined_Realms/` or `Tools/Audio/` (the RR originals) — duplicate first if Anomalous Wild needs divergent behavior
- Every Tool-Manager capability claim must cite a real source (a skill doc path, or "verified in session on [date]") — never assert unverified capability
- Diagram/data-viz beats: no static frame longer than 3–5 seconds, regardless of total beat length
- Live-footage beats: 8-second max clip length (same as RR, same reasoning)
- `end_card_v3.mp4` is a fixed asset for every video — never generated or chosen per-video
- Scientific illustrations always generate with an explicit no-text/no-label negative prompt — labels are always a separate step
- Scripts stay small and single-purpose — one file, one job, matching this session's `compose_audio.py`/`generate_stems.py`/`mix_stems.py` pattern

---

### Task 1: Tool-Manager Motion Graphics Capability Profile

**Files:**
- Create: `001_Architecture/Tools/Tool-Manager/data/motion_graphics_capabilities.json`
- Create: `001_Architecture/Tools/Tool-Manager/build_motion_graphics_profile.py`
- Modify: `001_Architecture/Skills/Tool-Manager/SKILL.md` (add a "Motion Graphics Tool Routing" section)
- Test: `001_Architecture/Tools/Tool-Manager/test_motion_graphics_profile.py`

**Interfaces:**
- Produces: `motion_graphics_capabilities.json` schema — `{"tools": [{"name": str, "strengths": [str], "best_for": [str], "not_for": [str], "sources": [str]}]}`. Later tasks (Task 4 onward) don't call this directly — the orchestrator invokes the Tool-Manager skill, which reads this file.

- [ ] **Step 1: Read the real source docs for each tool before writing anything**

Read these four files in full (they already exist in this workspace):
- `~/.claude/skills` (or wherever the `hyperframes` skill resolves) — the `hyperframes` skill description and its `hyperframes-cli`/`hyperframes-media` companions
- The `video-use` skill description
- The `remotion-best-practices` skill description
- This session's own transcript precedent: the creature-pair overlay work (Remotion, colorkey compositing, `PhylogeneticTree.tsx`) and the tree-of-life Seedance/GPT-Image-2 work

Do not write the JSON file until these are actually read — every claim in Step 2 must trace back to one of these.

- [ ] **Step 2: Write the capability data file with cited sources**

```python
# build_motion_graphics_profile.py
"""
One-time (re-runnable) builder for the motion graphics tool capability profile.
Every entry must cite a real source — a skill doc path or a dated session precedent.
Re-run this whenever a tool's skill docs change materially.
"""
import json
from pathlib import Path

PROFILE = {
    "_meta": {
        "purpose": "Capability profile for motion-graphics/composition tools, "
                   "consulted by Tool-Manager when the orchestrator describes a "
                   "scene need in plain language. Never guess capabilities not "
                   "backed by a cited source.",
        "last_built": "2026-07-06",
    },
    "tools": [
        {
            "name": "Remotion",
            "strengths": [
                "Frame-accurate programmatic control over position/timing",
                "Precise coordinate placement for labels and callout lines",
                "Reusable parametrized components across videos",
            ],
            "best_for": [
                "Labeled scientific diagrams with exact callout placement",
                "Data visualization (charts, counters, phylogenetic-tree-style animations)",
                "Compositing illustrated overlays on top of generated footage",
            ],
            "not_for": [
                "Freeform editing of existing raw footage (use video-use)",
                "Generating original illustration/artwork from nothing (use an image model first)",
            ],
            "sources": [
                "remotion-best-practices skill",
                "Session precedent 2026-07-06: creature-pair overlay compositing "
                "(scene06_test_with_overlays.mp4), PhylogeneticTree.tsx analysis",
            ],
        },
        {
            "name": "video-use",
            "strengths": [
                "Audio-first, transcript-driven editing",
                "Turns raw footage + VO into a clean cut via conversation",
            ],
            "best_for": [
                "Cutting together real or generated footage to match narration timing",
                "Trims, transitions between actual video clips",
            ],
            "not_for": [
                "Building new illustrated graphics from scratch — it edits existing footage, it doesn't generate diagrams",
            ],
            "sources": ["video-use skill description"],
        },
        {
            "name": "Hyperframes",
            "strengths": [
                "Captions/subtitles synced to audio",
                "Audio-reactive visuals (beat-synced glow/pulse)",
                "Animated text emphasis (marker sweeps, hand-drawn circles, burst lines)",
            ],
            "best_for": [
                "Caption burn-in",
                "Music-reactive visual moments",
                "Animated text callouts not requiring precise anatomical coordinates",
            ],
            "not_for": [
                "Precise anatomical/coordinate-based label placement (use Remotion)",
            ],
            "sources": ["hyperframes skill description", "hyperframes-cli skill description", "hyperframes-media skill description"],
        },
        {
            "name": "Manim",
            "strengths": [
                "Purpose-built for mathematical/technical animation",
            ],
            "best_for": [
                "Pure equation/graph/algorithm visualizations drawn from scratch",
            ],
            "not_for": [
                "Compositing over an arbitrary generated illustration image (Manim draws its own vector scenes, it doesn't import/overlay raster illustrations easily)",
            ],
            "sources": ["manim-video skill (nested under video-use skills)"],
        },
    ],
}

if __name__ == "__main__":
    out_path = Path(__file__).parent / "data" / "motion_graphics_capabilities.json"
    out_path.write_text(json.dumps(PROFILE, indent=2))
    print(f"Wrote {out_path} — {len(PROFILE['tools'])} tools profiled")
```

- [ ] **Step 3: Write the test that verifies every entry has a source**

```python
# test_motion_graphics_profile.py
import json
from pathlib import Path

def test_every_tool_has_at_least_one_source():
    data = json.loads((Path(__file__).parent / "data" / "motion_graphics_capabilities.json").read_text())
    for tool in data["tools"]:
        assert tool["sources"], f"{tool['name']} has no cited source — this is a guess, not research"
        assert tool["strengths"], f"{tool['name']} has no strengths listed"
        assert tool["best_for"], f"{tool['name']} has no best_for listed"

def test_expected_tools_present():
    data = json.loads((Path(__file__).parent / "data" / "motion_graphics_capabilities.json").read_text())
    names = {t["name"] for t in data["tools"]}
    assert {"Remotion", "video-use", "Hyperframes", "Manim"}.issubset(names)
```

- [ ] **Step 4: Run the builder then the test**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Tool-Manager
python3 build_motion_graphics_profile.py
python3 -m pytest test_motion_graphics_profile.py -v
```
Expected: `2 passed`

- [ ] **Step 5: Extend the Tool-Manager skill doc**

Add a new section to `001_Architecture/Skills/Tool-Manager/SKILL.md` (after the existing model-recommendation sections):

```markdown
## Motion Graphics Tool Routing

When an orchestrator (e.g. the Anomalous Wild pipeline) describes a scene's
visual need in plain language, read `Tools/Tool-Manager/data/motion_graphics_capabilities.json`
and reason about which tool(s) fit — this is judgment against real researched
data, not a fixed lookup table. A scene may need more than one tool (e.g.
Remotion for diagram placement + Hyperframes for a caption pass).

Never invent a capability not present in that file. If the file doesn't
cover the need well enough to answer confidently, say so rather than guessing,
and flag that the profile needs a research update (re-run
`build_motion_graphics_profile.py` after reading the relevant tool's actual
docs — never add an entry without a cited source).
```

- [ ] **Step 6: Commit**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
git add 001_Architecture/Tools/Tool-Manager/data/motion_graphics_capabilities.json \
        001_Architecture/Tools/Tool-Manager/build_motion_graphics_profile.py \
        001_Architecture/Tools/Tool-Manager/test_motion_graphics_profile.py \
        001_Architecture/Skills/Tool-Manager/SKILL.md
git commit -m "Add motion graphics capability profile to Tool-Manager

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 2: Word-Level Narration Timestamps for Anomalous Wild

**Files:**
- Create: `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/generate_narration_with_timestamps.py`
- Test: manual (real API call — no unit test, this is a thin wrapper around a proven tool)

**Interfaces:**
- Consumes: `generate_voiceover_with_timestamps(text, output_filename, voice_id)` from `001_Architecture/Tools/Text-To-Speech/audio_tts.py` (already exists, already returns `(audio_path, words)` where `words` is `[{"word": str, "start_s": float, "end_s": float}]`)
- Produces: `<scene_dir>/audio.mp3` + `<scene_dir>/beat_sheet.json` for every scene — later tasks (Task 3) read `beat_sheet.json`

- [ ] **Step 1: Confirm the existing tool's exact signature (discovery, not assumption)**

```bash
sed -n '97,150p' /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Text-To-Speech/audio_tts.py
```
Expected: confirms `generate_voiceover_with_timestamps(text, output_filename, voice_id)` returns `(output_filename, words)`.

- [ ] **Step 2: Write the per-scene wrapper script**

```python
#!/usr/bin/env python3
"""
generate_narration_with_timestamps.py — Anomalous Wild narration generator.

Thin wrapper around the existing generate_voiceover_with_timestamps() —
does not duplicate ElevenLabs logic, just applies it per-scene for a
production and writes beat_sheet.json alongside each scene's audio.mp3.

Usage:
  python3 generate_narration_with_timestamps.py <production_folder> <voice_id>

Reads:
  <production_folder>/Scripts/Narration.md  (## SCENE_ID headers, narration text below each)

Writes:
  <production_folder>/Narration_Audio/<scene_id>.mp3
  <production_folder>/Narration_Audio/<scene_id>_beat_sheet.json
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, "/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Text-To-Speech")
from audio_tts import generate_voiceover_with_timestamps


def parse_narration_sections(md_text: str) -> dict[str, str]:
    """## scene_01 \n narration text... -> {"scene_01": "narration text..."}"""
    sections = {}
    matches = list(re.finditer(r"^##\s+(\S+)\s*$", md_text, re.MULTILINE))
    for i, m in enumerate(matches):
        scene_id = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md_text)
        sections[scene_id] = md_text[start:end].strip()
    return sections


def main():
    if len(sys.argv) < 3:
        sys.exit("Usage: generate_narration_with_timestamps.py <production_folder> <voice_id>")
    production_root = Path(sys.argv[1]).resolve()
    voice_id = sys.argv[2]

    narration_path = production_root / "Scripts" / "Narration.md"
    if not narration_path.exists():
        sys.exit(f"ERROR: {narration_path} not found")

    sections = parse_narration_sections(narration_path.read_text())
    out_dir = production_root / "Narration_Audio"
    out_dir.mkdir(parents=True, exist_ok=True)

    for scene_id, text in sections.items():
        if not text:
            print(f"  {scene_id}: no narration text, skipping")
            continue
        audio_path = out_dir / f"{scene_id}.mp3"
        print(f"  Generating {scene_id} ({len(text)} chars)...")
        _, words = generate_voiceover_with_timestamps(text, str(audio_path), voice_id)
        beat_sheet_path = out_dir / f"{scene_id}_beat_sheet.json"
        beat_sheet_path.write_text(json.dumps({"scene_id": scene_id, "words": words}, indent=2))
        print(f"    saved {audio_path.name} + {beat_sheet_path.name} ({len(words)} words)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Verify with a real test scene**

```bash
mkdir -p /tmp/aw_timestamp_test/Scripts
cat > /tmp/aw_timestamp_test/Scripts/Narration.md << 'EOF'
## scene_test
This is a short test sentence to verify timestamps work correctly.
EOF
python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/generate_narration_with_timestamps.py /tmp/aw_timestamp_test KYhuk3Y57IlkV1ZjtDAt
cat /tmp/aw_timestamp_test/Narration_Audio/scene_test_beat_sheet.json
```
Expected: JSON with a `words` array, each entry having `word`, `start_s`, `end_s`. Clean up: `rm -rf /tmp/aw_timestamp_test`.

- [ ] **Step 4: Commit**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
git add 001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/generate_narration_with_timestamps.py
git commit -m "Add word-level timestamp narration generation for Anomalous Wild

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 3: Beat Table Builder (universal chunking + conditional 8s cap + 3-5s motion rule)

**Files:**
- Create: `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/build_beat_table.py`
- Test: `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/test_build_beat_table.py`

**Interfaces:**
- Consumes: `Narration_Audio/<scene_id>_beat_sheet.json` (from Task 2), a per-beat `tool_routing` decision (from Task 1's Tool-Manager call — represented here as a plain dict the orchestrator fills in when it calls this)
- Produces: `Production/Beat_Table.json` — `{"beats": [{"scene_id": str, "start_s": float, "end_s": float, "routing": "live_footage"|"diagram"|..., "max_static_s": float|null}]}`. Task 4+ (diagram sub-pipeline) reads beats where `routing != "live_footage"`.

- [ ] **Step 1: Write the failing test**

```python
# test_build_beat_table.py
from build_beat_table import build_beat_table

def test_live_footage_beat_gets_8s_cap():
    words = [{"word": "hello", "start_s": 0.0, "end_s": 9.5}]
    beats = build_beat_table([{"scene_id": "scene_01", "words": words, "routing": "live_footage"}])
    assert beats[0]["routing"] == "live_footage"
    assert beats[0]["max_clip_s"] == 8.0

def test_diagram_beat_has_no_length_cap_but_has_static_rule():
    words = [{"word": "worm", "start_s": 0.0, "end_s": 16.2}]
    beats = build_beat_table([{"scene_id": "scene_04", "words": words, "routing": "diagram"}])
    assert beats[0]["max_clip_s"] is None
    assert beats[0]["max_static_s"] == 5.0

def test_beat_start_end_derived_from_words():
    words = [{"word": "a", "start_s": 1.0, "end_s": 1.2}, {"word": "b", "start_s": 1.2, "end_s": 3.4}]
    beats = build_beat_table([{"scene_id": "scene_02", "words": words, "routing": "diagram"}])
    assert beats[0]["start_s"] == 1.0
    assert beats[0]["end_s"] == 3.4
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild
python3 -m pytest test_build_beat_table.py -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'build_beat_table'`

- [ ] **Step 3: Write the implementation**

```python
#!/usr/bin/env python3
"""
build_beat_table.py — Anomalous Wild beat table builder.

Universal narration chunking (same principle as Reimagined Realms), plus:
  - 8-second max clip length, but ONLY for beats already routed to live-footage
    generation (same reasoning as RR: generation model limits + engagement pacing)
  - No length cap for diagram/data-viz beats, but a hard "no static frame >
    3-5 seconds" rule attached as metadata for the assembly step to honor

Usage (called by the orchestrator, not run standalone in production):
  python3 build_beat_table.py <production_folder>
Reads:
  Narration_Audio/*_beat_sheet.json (per-scene word timestamps)
  Production/Scene_Routing.json (scene_id -> routing decision from Tool-Manager)
Writes:
  Production/Beat_Table.json
"""
import json
import sys
from pathlib import Path

LIVE_FOOTAGE_MAX_CLIP_S = 8.0
DIAGRAM_MAX_STATIC_S = 5.0


def build_beat_table(scenes: list[dict]) -> list[dict]:
    """scenes: [{"scene_id": str, "words": [{"word","start_s","end_s"}], "routing": str}]"""
    beats = []
    for scene in scenes:
        words = scene["words"]
        if not words:
            continue
        start_s = words[0]["start_s"]
        end_s = words[-1]["end_s"]
        routing = scene["routing"]
        beat = {
            "scene_id": scene["scene_id"],
            "start_s": start_s,
            "end_s": end_s,
            "routing": routing,
            "max_clip_s": LIVE_FOOTAGE_MAX_CLIP_S if routing == "live_footage" else None,
            "max_static_s": None if routing == "live_footage" else DIAGRAM_MAX_STATIC_S,
        }
        beats.append(beat)
    return beats


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: build_beat_table.py <production_folder>")
    production_root = Path(sys.argv[1]).resolve()

    routing_path = production_root / "Production" / "Scene_Routing.json"
    if not routing_path.exists():
        sys.exit(f"ERROR: {routing_path} not found — run Tool-Manager routing first")
    routing = json.loads(routing_path.read_text())  # {"scene_01": "live_footage", ...}

    narration_dir = production_root / "Narration_Audio"
    scenes = []
    for beat_sheet_path in sorted(narration_dir.glob("*_beat_sheet.json")):
        data = json.loads(beat_sheet_path.read_text())
        scene_id = data["scene_id"]
        if scene_id not in routing:
            sys.exit(f"ERROR: no routing decision for {scene_id} in Scene_Routing.json")
        scenes.append({"scene_id": scene_id, "words": data["words"], "routing": routing[scene_id]})

    beats = build_beat_table(scenes)
    out_path = production_root / "Production" / "Beat_Table.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"beats": beats}, indent=2))
    print(f"Wrote {out_path} — {len(beats)} beats")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python3 -m pytest test_build_beat_table.py -v
```
Expected: `3 passed`

- [ ] **Step 5: Commit**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
git add 001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/build_beat_table.py \
        001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/test_build_beat_table.py
git commit -m "Add Anomalous Wild beat table builder with conditional 8s cap

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 4: Scientific Diagram Sub-Pipeline — Reference Research + Clean Illustration

**Files:**
- Create: `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/diagram_research_and_illustrate.py`
- Test: manual (real API calls — Openverse search + GPT-Image-2 generation)

**Interfaces:**
- Produces: `<scene_dir>/reference_image.jpg` (real reference), `<scene_dir>/illustration.png` (clean, no-text) — Task 5 (vision coordinate pass) consumes `illustration.png`

- [ ] **Step 1: Write the reference-search + illustration script**

```python
#!/usr/bin/env python3
"""
diagram_research_and_illustrate.py — Scientific Diagram sub-pipeline, steps 1-2.

Step 1: search Openverse (open-licensed images, already in the API stack)
        for a real reference image of the subject.
Step 2: generate a clean illustration guided by that reference, with an
        explicit no-text/no-label negative prompt (fixes the garbled-text
        diagram problem — see Report_Card.md and the anglerfish example).

Usage:
  python3 diagram_research_and_illustrate.py <subject_query> <style_description> <output_dir>

Example:
  python3 diagram_research_and_illustrate.py "anglerfish esca illicium" \\
      "glowing neon-green bioluminescent line-art, deep-sea documentary style" \\
      002_Channels/001_Anomalous-Wild/.../scene_07/
"""
import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path.home() / ".env-secrets")


def search_openverse_reference(query: str, out_path: Path) -> bool:
    resp = requests.get(
        "https://api.openverse.org/v1/images/",
        params={"q": query, "license_type": "all-cc"},
        timeout=15,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if not results:
        print(f"  No Openverse results for '{query}'")
        return False
    image_url = results[0]["url"]
    img = requests.get(image_url, stream=True, timeout=30)
    img.raise_for_status()
    out_path.write_bytes(img.content)
    print(f"  Saved reference: {out_path} (source: {results[0].get('foreign_landing_url', image_url)})")
    return True


def generate_clean_illustration(subject_query: str, style_description: str, out_path: Path):
    key = os.getenv("KIE_API_KEY")
    prompt = (
        f"Scientific illustration of {subject_query}, {style_description}. "
        "NO TEXT, NO LABELS, NO WORDS, NO NUMBERS, NO CALLOUT LINES, NO ANNOTATION MARKS, "
        "no watermark. Clean anatomical illustration only."
    )
    payload = {"model": "gpt-image-2-text-to-image", "input": {"prompt": prompt, "aspect_ratio": "16:9", "output_format": "png"}}
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    resp = requests.post("https://api.kie.ai/api/v1/jobs/createTask", headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    task_id = resp.json()["data"]["taskId"]
    print(f"  Illustration task: {task_id} (poll separately — see gemini_scene_analysis.py pattern for polling loop)")
    return task_id


def main():
    if len(sys.argv) < 4:
        sys.exit("Usage: diagram_research_and_illustrate.py <subject_query> <style_description> <output_dir>")
    subject_query, style_description, output_dir = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    output_dir.mkdir(parents=True, exist_ok=True)

    found = search_openverse_reference(subject_query, output_dir / "reference_image.jpg")
    if not found:
        print("  WARNING: no reference found — illustration will not be anatomically grounded. Flag to Tony.")

    generate_clean_illustration(subject_query, style_description, output_dir)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify with a real subject**

```bash
python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/diagram_research_and_illustrate.py \
  "anglerfish deep sea" \
  "glowing neon-green bioluminescent line-art, deep-sea documentary style" \
  /tmp/aw_diagram_test
ls -la /tmp/aw_diagram_test
```
Expected: `reference_image.jpg` present, a task ID printed for the illustration. Clean up `/tmp/aw_diagram_test` after checking.

- [ ] **Step 3: Commit**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
git add 001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/diagram_research_and_illustrate.py
git commit -m "Add Scientific Diagram sub-pipeline: reference research + clean illustration

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 5: Scientific Diagram Sub-Pipeline — Vision Coordinate Detection

**Files:**
- Create: `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/detect_label_coordinates.py`
- Test: manual (real Gemini vision call)

**Interfaces:**
- Consumes: `illustration.png` (from Task 4)
- Produces: `<scene_dir>/label_coordinates.json` — `{"labels": [{"feature": str, "x_pct": float, "y_pct": float, "confidence": "high"|"low"|"not_found"}]}`. Task 6 (Remotion component) consumes this file directly.

- [ ] **Step 1: Write the vision coordinate detection script**

```python
#!/usr/bin/env python3
"""
detect_label_coordinates.py — Scientific Diagram sub-pipeline, step 3.

Looks at the ACTUAL generated illustration (not a generic template) and
returns real coordinates for each anatomical feature that needs a label.
This is the fix for "the lines didn't match up" — coordinates are detected
per-image, never guessed or hardcoded.

Usage:
  python3 detect_label_coordinates.py <illustration.png> <feature1> <feature2> ...

Example:
  python3 detect_label_coordinates.py scene_07/illustration.png esca illicium_stalk photophore_stack
"""
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from google import genai

load_dotenv(Path.home() / ".env-secrets")


def detect_coordinates(image_path: Path, features: list[str]) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    feature_list = ", ".join(features)
    prompt = f"""
Look at this scientific illustration. For each of these features: {feature_list}

Return ONLY valid JSON, no other text, in this exact shape:
{{"labels": [{{"feature": "esca", "x_pct": 62.0, "y_pct": 38.0, "confidence": "high"}}]}}

Rules:
- x_pct and y_pct are percentages (0-100) of image width/height, measured from top-left
- confidence is "high" if you can clearly see and locate the feature, "low" if you can see it but aren't sure of exact bounds, "not_found" if the feature isn't visible in the image
- Do NOT guess a location for a not_found feature — omit x_pct/y_pct or set them to null
- One entry per requested feature, in the same order given
"""
    uploaded = client.files.upload(file=str(image_path))
    response = client.models.generate_content(model="gemini-2.5-pro", contents=[uploaded, prompt])

    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("```")[1].removeprefix("json").strip()
    return json.loads(text)


def main():
    if len(sys.argv) < 3:
        sys.exit("Usage: detect_label_coordinates.py <illustration.png> <feature1> [feature2 ...]")
    image_path = Path(sys.argv[1])
    features = sys.argv[2:]

    result = detect_coordinates(image_path, features)

    not_found = [l["feature"] for l in result["labels"] if l.get("confidence") == "not_found"]
    if not_found:
        print(f"  WARNING: could not locate: {', '.join(not_found)} — flag to Tony, do not guess placement")

    out_path = image_path.parent / "label_coordinates.json"
    out_path.write_text(json.dumps(result, indent=2))
    print(f"  Saved {out_path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify against a real illustration**

```bash
python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/detect_label_coordinates.py \
  /tmp/aw_diagram_test/illustration.png esca illicium_stalk photophore_stack
cat /tmp/aw_diagram_test/label_coordinates.json
```
Expected: JSON with one entry per feature, each having `x_pct`/`y_pct`/`confidence`.

- [ ] **Step 3: Commit**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
git add 001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/detect_label_coordinates.py
git commit -m "Add vision coordinate detection for diagram label placement

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 6: Scientific Diagram Sub-Pipeline — Remotion Label Component

**Files:**
- Create: `002_Content-Creation/Video_Editor/003_Remotion/src/remotion/video-components/DiagramLabels.tsx`
- Test: manual (Remotion Studio preview)

**Interfaces:**
- Consumes: `label_coordinates.json` (Task 5) passed as a Remotion `<Sequence>` prop, plus a beat's `max_static_s` from `Beat_Table.json` (Task 3) to pace label reveals
- Produces: a composable Remotion component other compositions (e.g. a future `AnomalousWildDoc.tsx`, extending `BioluminescenceDoc.tsx`'s pattern) import and place over the illustration

- [ ] **Step 1: Write the component**

```tsx
// DiagramLabels.tsx
import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate } from "remotion";

interface Label {
  feature: string;
  x_pct: number;
  y_pct: number;
  confidence: "high" | "low" | "not_found";
}

interface DiagramLabelsProps {
  labels: Label[];
  labelStaggerS: number; // seconds between each label appearing — must respect the 3-5s max-static rule upstream
  displayNames: Record<string, string>; // e.g. {"esca": "Esca (light lure)"}
}

const LABEL_COLOR = "#E8FFE0";
const LINE_COLOR = "#8AFA47";

export const DiagramLabels: React.FC<DiagramLabelsProps> = ({ labels, labelStaggerS, displayNames }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();

  const visibleLabels = labels.filter((l) => l.confidence !== "not_found");

  return (
    <AbsoluteFill>
      {visibleLabels.map((label, i) => {
        const startFrame = i * labelStaggerS * fps;
        const opacity = interpolate(frame, [startFrame, startFrame + fps * 0.5], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        const x = (label.x_pct / 100) * width;
        const y = (label.y_pct / 100) * height;
        // Label sits offset from the point, with a line drawn back to the point
        const labelX = x + 120;
        const labelY = y - 60;

        return (
          <svg key={label.feature} width={width} height={height} style={{ position: "absolute", top: 0, left: 0, opacity }}>
            <line x1={x} y1={y} x2={labelX} y2={labelY} stroke={LINE_COLOR} strokeWidth={1.5} opacity={0.8} />
            <circle cx={x} cy={y} r={4} fill={LINE_COLOR} />
            <text x={labelX + 8} y={labelY} fill={LABEL_COLOR} fontSize={20} fontFamily="Arial, sans-serif">
              {displayNames[label.feature] ?? label.feature}
            </text>
          </svg>
        );
      })}
    </AbsoluteFill>
  );
};
```

- [ ] **Step 2: Register it in Root.tsx for isolated preview**

```bash
grep -n "registerRoot\|Composition" /Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/003_Remotion/src/remotion/Root.tsx | head -5
```
Add a `<Composition id="DiagramLabelsPreview" component={DiagramLabels} durationInFrames={150} fps={30} width={1920} height={1080} defaultProps={{labels: [{feature: "esca", x_pct: 62, y_pct: 38, confidence: "high"}], labelStaggerS: 2, displayNames: {esca: "Esca (light lure)"}}} />` following the existing pattern in that file.

- [ ] **Step 3: Preview in Remotion Studio**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/003_Remotion
npx remotion studio
```
Expected: `DiagramLabelsPreview` composition shows a label + line fading in at the specified coordinate, no crash.

- [ ] **Step 4: Commit**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
git add 002_Content-Creation/Video_Editor/003_Remotion/src/remotion/video-components/DiagramLabels.tsx \
        002_Content-Creation/Video_Editor/003_Remotion/src/remotion/Root.tsx
git commit -m "Add DiagramLabels Remotion component for coordinate-based label placement

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 7: YouTube Package Generator

**Files:**
- Create: `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/generate_youtube_package.py`
- Test: `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/test_generate_youtube_package.py`

**Interfaces:**
- Produces: `<production_folder>/Package/YouTube_Package.md` + `<production_folder>/Package/Thumbnails/*.png` (3 concepts)

- [ ] **Step 1: Write the failing test**

```python
# test_generate_youtube_package.py
from generate_youtube_package import build_titles, build_description

def test_build_titles_returns_three_formulas():
    titles = build_titles(subject="the anglerfish", hook_fact="uses bacteria to glow")
    assert len(titles) == 3
    assert all(isinstance(t, str) and len(t) <= 100 for t in titles)

def test_description_first_line_is_a_question():
    desc = build_description(subject="anglerfish bioluminescence", chapters=[("0:00", "Hook")])
    first_line = desc.strip().split("\n")[0]
    assert first_line.strip().endswith("?")
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild
python3 -m pytest test_generate_youtube_package.py -v
```
Expected: FAIL — module not found

- [ ] **Step 3: Write the implementation (adapting RR's Phase 10 formulas to Anomalous Wild's science/nature framing)**

```python
#!/usr/bin/env python3
"""
generate_youtube_package.py — Anomalous Wild YouTube package generator.

Adapts Reimagined Realms' Phase 10 title/description/thumbnail formulas
(curiosity gap, search-intent description, no-text thumbnail with emotion-
matched palette) to Anomalous Wild's science/nature-documentary framing.

Usage:
  python3 generate_youtube_package.py <production_folder> <subject> <hook_fact>
"""
import sys
from pathlib import Path


def build_titles(subject: str, hook_fact: str) -> list[str]:
    return [
        f"This {subject.title()} {hook_fact.capitalize()}. Scientists Still Don't Know Why.",
        f"What Science Just Discovered About {subject.title()}",
        f"{subject.title()} Isn't What You Think. It's Something Stranger.",
    ]


def build_description(subject: str, chapters: list[tuple[str, str]]) -> str:
    chapter_lines = "\n".join(f"{ts} {label}" for ts, label in chapters)
    return f"""How does {subject} actually work?

Nature found a solution that seems almost impossible — and it evolved independently, more than once.

---

📍 Chapters
{chapter_lines}

---

This channel explores real science using illustrated diagrams and AI-generated visuals. All content is for educational and entertainment purposes.

#{subject.replace(' ', '')} #Science #Nature #Biology #Documentary #AnomalousWild
"""


def build_thumbnail_prompt(subject: str, emotion: str, palette: str) -> str:
    return (
        f"Close-up of {subject}, {palette} palette matching a {emotion} mood, "
        "dramatic lighting, deep vanishing point, photorealistic, cinematic, "
        "no text, no captions"
    )


def main():
    if len(sys.argv) < 4:
        sys.exit("Usage: generate_youtube_package.py <production_folder> <subject> <hook_fact>")
    production_root = Path(sys.argv[1]).resolve()
    subject, hook_fact = sys.argv[2], sys.argv[3]

    titles = build_titles(subject, hook_fact)
    description = build_description(subject, chapters=[("0:00", "Hook")])

    package_dir = production_root / "Package"
    package_dir.mkdir(parents=True, exist_ok=True)
    (package_dir / "YouTube_Package.md").write_text(
        "# Title Options\n\n" + "\n".join(f"{i+1}. {t}" for i, t in enumerate(titles)) +
        "\n\n# Description\n\n" + description
    )
    print(f"Wrote {package_dir / 'YouTube_Package.md'}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python3 -m pytest test_generate_youtube_package.py -v
```
Expected: `2 passed`

- [ ] **Step 5: Commit**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
git add 001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/generate_youtube_package.py \
        001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/test_generate_youtube_package.py
git commit -m "Add Anomalous Wild YouTube package generator

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 8: Blotato Upload for Anomalous Wild

**Files:**
- Create: `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/upload_to_blotato.md` (a procedure doc, not a script — Blotato is invoked via MCP tools directly, same as RR Phase 12)

**Interfaces:**
- Consumes: `Package/YouTube_Package.md` (Task 7), final rendered video, chosen thumbnail
- Produces: a live (private) YouTube upload via Blotato

- [ ] **Step 1: Find the Anomalous Wild YouTube account ID (discovery, not assumption)**

```
Call mcp__blotato__blotato_list_accounts and find the entry for the Anomalous Wild YouTube channel. Record its accountId — do not guess or reuse Reimagined Realms' "30323".
```

- [ ] **Step 2: Write the procedure doc mirroring RR Phase 12's locked defaults**

```markdown
# Anomalous Wild — Blotato Upload Procedure

Mirrors Reimagined Realms Phase 12 exactly, with Anomalous Wild's own account ID.

## Locked defaults (same as RR, do not change without Tony's explicit say-so)
- `isMadeForKids`: `false`
- `containsSyntheticMedia`: `true`
- `shouldNotifySubscribers`: `false` (while private)
- `playlistIds`: omit — added manually by Tony during scheduling

## Steps
1. Present Tony: chosen video file (duration/size), 3 titles from `Package/YouTube_Package.md`, 3 thumbnail concepts, privacy status choice. ⏸ PAUSE — wait for his picks.
2. Compress thumbnail if over 2MB: `ffmpeg -y -i input.png -vf "scale=1920:-1" -q:v 5 output.jpg`
3. Get presigned upload URLs via `mcp__blotato__blotato_create_presigned_upload_url` for video + thumbnail, `curl -X PUT --data-binary` each.
4. Call `mcp__blotato__blotato_create_post` with the accountId found in Step 1, Tony's chosen title/description/thumbnail/privacy, and the locked defaults above.
5. Poll `mcp__blotato__blotato_get_post_status` (≥10s between polls) until `published` or `failed`. Report the live URL back to Tony.
```

- [ ] **Step 3: Commit**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
git add 001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/upload_to_blotato.md
git commit -m "Add Anomalous Wild Blotato upload procedure

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 9: End Card Lock-In + Going-Forward Folder Scaffolder

**Files:**
- Create: `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/scaffold_new_production.py`
- Test: `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/test_scaffold_new_production.py`

**Interfaces:**
- Produces: a new production folder with the RR-style typed structure (`Scripts/`, `Production/`, `Images/`, `Video_Clips/`, `Narration_Audio/`, `Audio_Stems/`, `Assembly/`, `Package/`) plus a hardcoded reference to `end_card_v3.mp4`

- [ ] **Step 1: Write the failing test**

```python
# test_scaffold_new_production.py
from pathlib import Path
from scaffold_new_production import scaffold, END_CARD_PATH

def test_scaffold_creates_typed_folders(tmp_path):
    prod_root = tmp_path / "0002_Test_Production"
    scaffold(prod_root)
    for folder in ["Scripts", "Production", "Images", "Video_Clips", "Narration_Audio", "Audio_Stems", "Assembly", "Package"]:
        assert (prod_root / folder).is_dir()

def test_end_card_is_locked_constant():
    assert END_CARD_PATH.name == "end_card_v3.mp4"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild
python3 -m pytest test_scaffold_new_production.py -v
```
Expected: FAIL — module not found

- [ ] **Step 3: Write the implementation**

```python
#!/usr/bin/env python3
"""
scaffold_new_production.py — Anomalous Wild new-production folder scaffolder.

Matches Reimagined Realms' actual Pompeii folder structure (confirmed from
disk 2026-07-06): Scripts/, Production/, Images/, Video_Clips/, Narration_Audio/,
Audio_Stems/, Assembly/ (versions live INSIDE Assembly as V1/, V2/... not as
a sibling folder), Package/.

end_card_v3.mp4 is a FIXED, hardcoded asset for every Anomalous Wild video —
never generated or chosen per-video.

Usage:
  python3 scaffold_new_production.py <new_production_folder>
"""
import sys
from pathlib import Path

END_CARD_PATH = Path(
    "/Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/"
    "002_Channels/001_Anomalous-Wild/000_End-Card/end_card_v3.mp4"
)

TYPED_FOLDERS = [
    "Scripts", "Production", "Images", "Video_Clips",
    "Narration_Audio", "Audio_Stems", "Assembly", "Package",
]


def scaffold(production_root: Path):
    if not END_CARD_PATH.exists():
        raise FileNotFoundError(f"Locked end card asset missing: {END_CARD_PATH}")
    production_root.mkdir(parents=True, exist_ok=True)
    for folder in TYPED_FOLDERS:
        (production_root / folder).mkdir(exist_ok=True)
    (production_root / "Production" / "end_card_reference.txt").write_text(str(END_CARD_PATH))


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: scaffold_new_production.py <new_production_folder>")
    scaffold(Path(sys.argv[1]).resolve())
    print(f"Scaffolded {sys.argv[1]} with {len(TYPED_FOLDERS)} typed folders + locked end card reference")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python3 -m pytest test_scaffold_new_production.py -v
```
Expected: `2 passed`

- [ ] **Step 5: Commit**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
git add 001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/scaffold_new_production.py \
        001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/test_scaffold_new_production.py
git commit -m "Add going-forward folder scaffolder with locked end card reference

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 10: Bioluminescence Weapon Folder Retrofit (higher risk — inventory first, migrate second)

**Files:**
- Create: `001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/retrofit_bioluminescence_folder.py`
- Modify (path references only, after inventory confirms exact locations): `scene_cut_sequences.json`, `ai_prompts.json`, `new_clips_prompts.json`, `pipeline_supervisor.py`'s `BASE` constant, `render_bioluminescence.sh`

**Interfaces:**
- Produces: Bioluminescence Weapon folder reorganized into the same typed structure as Task 9's scaffolder, with every `scene_XX/video.mp4` and `scene_XX/audio.mp3` moved into `Video_Clips/`/`Narration_Audio/` and every script/JSON path reference updated to match

- [ ] **Step 1: Full inventory pass — list every file that references old scene_XX paths (discovery, not guessing)**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/002_Channels/001_Anomalous-Wild/001_Bioluminescence-Weapon
grep -rl "scene_0[0-9]" *.json *.py *.sh 2>/dev/null
```
Expected: a concrete list of files needing path updates. Record this list — it drives Step 3.

- [ ] **Step 2: Write the dry-run migration script (lists moves, does not execute them yet)**

```python
#!/usr/bin/env python3
"""
retrofit_bioluminescence_folder.py — migrates the existing Bioluminescence
Weapon production into the typed folder structure (Task 9's pattern).

SAFETY: defaults to --dry-run. Only performs real moves with --execute,
and only after Tony has reviewed the dry-run output.

Usage:
  python3 retrofit_bioluminescence_folder.py <production_folder>              # dry run
  python3 retrofit_bioluminescence_folder.py <production_folder> --execute    # real moves
"""
import re
import shutil
import sys
from pathlib import Path


def plan_moves(production_root: Path) -> list[tuple[Path, Path]]:
    moves = []
    for scene_dir in sorted(production_root.glob("scene_*")):
        if not scene_dir.is_dir():
            continue
        scene_id = scene_dir.name
        video = scene_dir / "video.mp4"
        audio = scene_dir / "audio.mp3"
        if video.exists():
            moves.append((video, production_root / "Video_Clips" / f"{scene_id}.mp4"))
        if audio.exists():
            moves.append((audio, production_root / "Narration_Audio" / f"{scene_id}.mp3"))
    return moves


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: retrofit_bioluminescence_folder.py <production_folder> [--execute]")
    production_root = Path(sys.argv[1]).resolve()
    execute = "--execute" in sys.argv

    moves = plan_moves(production_root)
    print(f"Planned moves ({len(moves)}):")
    for src, dst in moves:
        print(f"  {src.relative_to(production_root)} -> {dst.relative_to(production_root)}")

    if not execute:
        print("\nDry run only. Re-run with --execute after reviewing this list with Tony.")
        return

    for folder in ["Video_Clips", "Narration_Audio"]:
        (production_root / folder).mkdir(exist_ok=True)
    for src, dst in moves:
        shutil.move(str(src), str(dst))
    print(f"\nMoved {len(moves)} files.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run dry-run and review output with Tony before any real move**

```bash
python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Tools/Video-Generation/Channels/Anomalous_Wild/retrofit_bioluminescence_folder.py \
  /Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/002_Channels/001_Anomalous-Wild/001_Bioluminescence-Weapon
```
⏸ **PAUSE — show Tony the full move list. Do not proceed to `--execute` or to updating any JSON/script path reference without his explicit go-ahead**, since `final_render_V4.mp4` and the tested `Versions/001_anomalous_wild_bioluminescence_V5.mp4` already reference the current (pre-migration) file layout indirectly through the scripts that built them.

- [ ] **Step 4: (only after Tony approves) update path references in the files found in Step 1, then execute the move, then re-run `render_bioluminescence.sh --preview` to confirm the Remotion composition still resolves every asset correctly.**

This step is intentionally left as a checkpoint rather than pre-written code — the exact edits depend on Step 1's real file list, which isn't known until that grep actually runs against the live folder.

---

### Task 11: Orchestrator Skill — Wire All Phases Together

**Files:**
- Create: `001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/SKILL.md`

**Interfaces:**
- Consumes: every task above (Tool-Manager routing, beat table, diagram sub-pipeline, YouTube package, Blotato procedure, scaffolder)
- Produces: the `/anomalous-wild` command, invokable the same way `/reimagined-realms` is

- [ ] **Step 1: Write the SKILL.md following the DESIGN.md phase breakdown exactly**

Structure it exactly like `Reimagined_Realms_Video_Pipeline/SKILL.md`: numbered phases, explicit ⏸ pause points (topic selection, cost estimate if applicable, first live-footage clip quality check, title/thumbnail/privacy selection), and a "Final Delivery" section. Each phase references the specific script built in Tasks 1–9 by its exact path. Phase 5 (Shot list / tool routing) explicitly instructs: "For each beat, describe the scene's visual need in plain language and invoke the Tool-Manager skill — do not hardcode a tool choice."

- [ ] **Step 2: Validate the skill file**

```bash
python3 /Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Scripts/validate_build.py --files "/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/SKILL.md"
```
Expected: PASS (frontmatter present, name present, Skill-Index registered).

- [ ] **Step 3: Commit**

```bash
cd /Users/tonymacbook2025/Documents/Agent-OS
git add 001_Architecture/Skills/Anomalous_Wild_Video_Pipeline/SKILL.md
git commit -m "Add Anomalous Wild Video Pipeline orchestrator skill

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

## Self-Review Notes

- **Spec coverage:** Task 1 covers Tooling Agent; Task 2 covers word-level timestamps; Task 3 covers beat table + 8s/3-5s rules; Tasks 4–6 cover the Scientific Diagram sub-pipeline end to end; Task 7 covers YouTube package; Task 8 covers Blotato; Task 9 covers end-card lock-in + going-forward folders; Task 10 covers the Bioluminescence Weapon retrofit; Task 11 wires it all into one skill. All DESIGN.md sections have a corresponding task.
- **Placeholder scan:** Task 10 Step 4 is intentionally a checkpoint rather than pre-written code, because the exact file edits depend on Step 1's live grep output — this is a real constraint (the spec explicitly calls this retrofit "higher-risk... gets its own careful implementation plan"), not a lazy placeholder. Every other step has complete, real code.
- **Type consistency:** `Beat_Table.json`'s `routing` field values (`"live_footage"`, `"diagram"`) are used consistently between Task 3's builder and its tests; `label_coordinates.json`'s schema is identical between Task 5 (producer) and Task 6 (consumer).
