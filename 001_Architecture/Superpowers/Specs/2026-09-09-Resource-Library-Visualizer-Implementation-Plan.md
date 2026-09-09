# Resource Library Visualizer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A local browser gallery ("Lightroom for screenshots") for reviewing, culling, and fixing the `007_Resource_Library` note collection.

**Architecture:** A single-process Flask server scans `007_Resource_Library/` on startup, pairs each note with its co-located sibling image, and exposes a small JSON API. A dependency-free single-page HTML app renders a Notion-style card grid, filter bars, a slide-over detail view, bulk Delete / Re-run-AI actions, and a per-card comment queue. Deletes move files to `~/Desktop/delete/`; comments and edit requests append to `~/Desktop/Resource_Library_Review/Review_Queue.md`.

**Tech Stack:** Python 3.13, Flask, PyYAML (frontmatter parsing), Pillow (thumbnails), markdown-it-py (`markdown_it`, Obsidian-style render), pytest (tests). All present except pytest.

**Spec:** `001_Architecture/Superpowers/Specs/2026-09-09-Resource-Library-Visualizer-Design.md`

## Global Constraints

- Scope is `007_Resource_Library/` only — never read or write outside it (except the two output dirs below).
- The tool never deletes: it moves to `~/Desktop/delete/<relative-path>`.
- The tool never commits to git.
- No `localStorage` as source of truth — the `.md` files and the queue file are authoritative; the browser holds only transient filter/selection state.
- Image↔note pairing is by co-location: same folder, same filename stem. No index file, no `![[...]]` resolver as the primary mechanism (body-embed parse is a fallback only).
- Frontmatter contract fields (from `001_Architecture/Skills/ingest/SKILL.md`): `title`, `type`, `form`, `summary`, `url`, `tags` (lowercase YAML block list).
- Workspace file-naming: Title_Case for new dirs; Python files stay as named here.
- Server port: `8756`. Thumbnail cache: `~/.cache/rl_visualizer/thumbs/` (outside repo).
- `WORKSPACE = "/Users/tonymacbook2025/Documents/Agent-OS"`, `RESOURCE_LIB = f"{WORKSPACE}/007_Resource_Library"`.

## File Structure

```
001_Architecture/Tools/Resource-Library-Visualizer/
├── config.py     # paths, port, constants
├── notes.py      # frontmatter parse + note scan + image pairing + card metadata
├── detect.py     # source-label / vision-risk / md-glyph-color heuristics (pure fns)
├── thumbs.py     # thumbnail cache generation; youtube poster URL
├── render.py     # markdown -> Obsidian-style HTML for the detail view
├── queue.py      # Review Queue append / delete-log / finalize
├── actions.py    # move-to-delete, rewrite-note-fields
├── serve.py      # Flask app: routes wiring all of the above + opens browser
├── app.html      # the single-page app (inline CSS/JS)
├── requirements.txt
└── README.md
tests/resource_library_visualizer/
├── conftest.py       # builds a temp RL fixture tree
├── test_detect.py
├── test_notes.py
├── test_thumbs.py
├── test_render.py
├── test_queue.py
├── test_actions.py
└── test_serve.py
```

---

### Task 1: Scaffold + config + dependencies

**Files:**
- Create: `001_Architecture/Tools/Resource-Library-Visualizer/requirements.txt`
- Create: `001_Architecture/Tools/Resource-Library-Visualizer/config.py`
- Create: `001_Architecture/Tools/Resource-Library-Visualizer/README.md`
- Create: `tests/resource_library_visualizer/__init__.py` (empty)

**Interfaces:**
- Produces: `config.WORKSPACE`, `config.RESOURCE_LIB`, `config.PORT`, `config.THUMB_CACHE`, `config.DELETE_DIR`, `config.QUEUE_DIR`, `config.QUEUE_FILE`, `config.THUMB_W`, `config.CATEGORY_FOLDERS` (list[str]), `config.IMG_EXT` (tuple).

- [ ] **Step 1: Install pytest**

Run: `python3 -m pip install --user pytest`
Expected: succeeds; `python3 -m pytest --version` prints a version.

- [ ] **Step 2: Write `requirements.txt`**

```
flask>=3.0
PyYAML>=6.0
Pillow>=10.0
markdown-it-py>=3.0
pytest>=8.0
```

- [ ] **Step 3: Write `config.py`**

```python
import os

WORKSPACE = "/Users/tonymacbook2025/Documents/Agent-OS"
RESOURCE_LIB = os.path.join(WORKSPACE, "007_Resource_Library")

PORT = 8756
THUMB_W = 280
IMG_EXT = (".png", ".jpg", ".jpeg", ".webp", ".gif")

THUMB_CACHE = os.path.expanduser("~/.cache/rl_visualizer/thumbs")
DELETE_DIR = os.path.expanduser("~/Desktop/delete")
QUEUE_DIR = os.path.expanduser("~/Desktop/Resource_Library_Review")
QUEUE_FILE = os.path.join(QUEUE_DIR, "Review_Queue.md")

# Top-level category folders shown as folder-filter buttons / pills.
CATEGORY_FOLDERS = [
    "Project_Ideas", "Prompts", "Research", "Tools", "Tutorials",
    "Workflows", "Models", "Docs", "Design_Inspiration", "Personal",
    "Investments", "Videos", "Archive", "Undetermined", "OpenAI_History",
]

# Filenames (case-insensitive substring / exact) that mark a structural .md
STRUCTURAL_MARKERS = ("review", "log", "registry", "directory", "agents",
                      "readme", "index", "_map", "manifest")
```

- [ ] **Step 4: Write `README.md`**

```markdown
# Resource Library Visualizer

Local browser gallery for reviewing / culling `007_Resource_Library`.

## Run

    python3 001_Architecture/Tools/Resource-Library-Visualizer/serve.py

Opens http://localhost:8756 in your browser.

## What it does

- Grid of every note that has an image or a YouTube video, newest first.
- Filter by folder, source type, or tag.
- Click a card -> the note rendered Obsidian-style.
- Select cards -> **Delete** (moves note + image to `~/Desktop/delete/`) or
  **Re-run AI**.
- Per card: **Edit** fields, **Re-run AI**, **Add Comment**.
- Comments + edit requests append to
  `~/Desktop/Resource_Library_Review/Review_Queue.md`; **Finalize Queue**
  seals a batch to hand to the agent.

Nothing is ever hard-deleted and nothing is committed to git.
```

- [ ] **Step 5: Create empty `tests/resource_library_visualizer/__init__.py`**

- [ ] **Step 6: Verify imports**

Run: `python3 -c "import flask, yaml, PIL, markdown_it; print('ok')"`
Expected: prints `ok`.

- [ ] **Step 7: Commit**

```bash
git add 001_Architecture/Tools/Resource-Library-Visualizer tests/resource_library_visualizer
git commit -m "feat(rl-visualizer): scaffold + config"
```

---

### Task 2: `detect.py` — source-label / vision-risk / glyph-color heuristics

**Files:**
- Create: `001_Architecture/Tools/Resource-Library-Visualizer/detect.py`
- Test: `tests/resource_library_visualizer/test_detect.py`

**Interfaces:**
- Consumes: `config.STRUCTURAL_MARKERS`.
- Produces:
  - `youtube_id(text: str) -> str | None` — first YouTube id found in a string.
  - `detect_source(fm: dict, body: str, filename: str, has_image: bool) -> tuple[str | None, bool]` — returns `(source_label, vision_risk)` where `source_label` ∈ `{"YouTube","Screenshot","Bookmark",None}`.
  - `is_structural(filename: str) -> bool`.
  - `glyph_color(fm: dict, folder: str) -> str` — hex color string.

- [ ] **Step 1: Write the failing tests**

```python
# tests/resource_library_visualizer/test_detect.py
from importlib import import_module
detect = import_module(
    "001_Architecture.Tools.Resource-Library-Visualizer.detect")  # see conftest note
```

Because the tool dir is not an importable package path, tests load modules by
file path. Use this helper instead (put in `conftest.py` in Task 6's step, but
define here too for now):

```python
import importlib.util, pathlib
TOOL = pathlib.Path("001_Architecture/Tools/Resource-Library-Visualizer")

def load(name):
    spec = importlib.util.spec_from_file_location(name, TOOL / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

detect = load("detect")

def test_youtube_id_from_watch_url():
    assert detect.youtube_id("see https://www.youtube.com/watch?v=Xi9zyPTgJL8 now") == "Xi9zyPTgJL8"

def test_youtube_id_from_short_url():
    assert detect.youtube_id("https://youtu.be/G7gK8H6u7Rs?si=abc") == "G7gK8H6u7Rs"

def test_youtube_id_none():
    assert detect.youtube_id("no video here") is None

def test_source_youtube_from_body():
    label, risk = detect.detect_source({}, "watch https://youtu.be/G7gK8H6u7Rs", "App-Building.md", False)
    assert label == "YouTube"
    assert risk is False

def test_source_screenshot_iphone_is_vision_risk():
    label, risk = detect.detect_source(
        {"original_filename": "IMG_8710.PNG"}, "", "Live-Explore.md", True)
    assert label == "Screenshot"
    assert risk is True

def test_source_screenshot_from_tag():
    label, risk = detect.detect_source(
        {"tags": ["screenshot", "video"]}, "", "Foo.md", True)
    assert label == "Screenshot"

def test_source_bookmark_from_web_clip():
    fm = {"source": "https://example.com/page", "url": "https://example.com/page"}
    label, risk = detect.detect_source(fm, "# Example\nclipped article body", "Example.md", True)
    assert label == "Bookmark"

def test_is_structural():
    assert detect.is_structural("Dedup-Review.md") is True
    assert detect.is_structural("rename_log.md") is True
    assert detect.is_structural("OpenCode.md") is False

def test_glyph_color_is_hex():
    c = detect.glyph_color({"type": "tool-doc"}, "Tools")
    assert c.startswith("#") and len(c) == 7
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/resource_library_visualizer/test_detect.py -v`
Expected: FAIL — `detect.py` has no such attributes.

- [ ] **Step 3: Write `detect.py`**

```python
import re

YT_RE = re.compile(
    r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([A-Za-z0-9_-]{11})")

# imported lazily to avoid package-path issues
def _markers():
    import importlib.util, pathlib
    p = pathlib.Path(__file__).with_name("config.py")
    spec = importlib.util.spec_from_file_location("rlv_config", p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m.STRUCTURAL_MARKERS

STRUCTURAL_MARKERS = _markers()

GLYPH_PALETTE = {
    "structural": "#6b7280",   # gray-blue
    "tools":      "#2563eb",   # blue
    "models":     "#7c3aed",   # violet
    "tutorials":  "#059669",   # green
    "research":   "#d97706",   # amber
    "prompts":    "#db2777",   # pink
    "workflows":  "#0891b2",   # cyan
    "default":    "#9ca3af",   # neutral
}


def youtube_id(text):
    if not text:
        return None
    m = YT_RE.search(text)
    return m.group(1) if m else None


def is_structural(filename):
    stem = filename.lower().rsplit(".", 1)[0]
    return any(mk in stem for mk in STRUCTURAL_MARKERS)


def detect_source(fm, body, filename, has_image):
    fm = fm or {}
    tags = [str(t).lower() for t in (fm.get("tags") or [])]
    haystack = " ".join(str(fm.get(k, "")) for k in ("url", "source")) + " " + (body or "")

    if youtube_id(haystack):
        return "YouTube", False

    orig = str(fm.get("original_filename", ""))
    if re.match(r"IMG_\d+\.(png|jpe?g)$", orig, re.I):
        return "Screenshot", True

    src = str(fm.get("source", ""))
    if src.startswith("http") and has_image:
        return "Bookmark", False

    if "screenshot" in tags or has_image:
        return "Screenshot", bool(orig)

    return None, False


def glyph_color(fm, folder):
    if is_structural(str(fm.get("_filename", ""))):
        return GLYPH_PALETTE["structural"]
    key = (folder or "").lower()
    for name in ("tools", "models", "tutorials", "research", "prompts", "workflows"):
        if name in key:
            return GLYPH_PALETTE[name]
    t = str(fm.get("type", "")).lower()
    if "system" in t or "architecture" in t or "config" in t:
        return GLYPH_PALETTE["structural"]
    return GLYPH_PALETTE["default"]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/resource_library_visualizer/test_detect.py -v`
Expected: PASS (9 tests).

- [ ] **Step 5: Commit**

```bash
git add 001_Architecture/Tools/Resource-Library-Visualizer/detect.py tests/resource_library_visualizer/test_detect.py
git commit -m "feat(rl-visualizer): source-label + glyph heuristics"
```

---

### Task 3: `notes.py` — frontmatter parse, note scan, image pairing, card metadata

**Files:**
- Create: `001_Architecture/Tools/Resource-Library-Visualizer/notes.py`
- Test: `tests/resource_library_visualizer/test_notes.py`

**Interfaces:**
- Consumes: `config.*`, `detect.detect_source`, `detect.youtube_id`, `detect.glyph_color`, `detect.is_structural`.
- Produces:
  - `parse_note(path: str) -> tuple[dict, str]` — `(frontmatter_dict, body_str)`; tolerant of missing/invalid frontmatter (returns `({}, full_text)`).
  - `find_sibling_image(md_path: str) -> str | None` — absolute path to same-stem image, else `None`.
  - `first_embed_image(body: str, md_dir: str) -> str | None` — fallback: resolve first `![[x]]` / `![](x)` to an absolute path that exists.
  - `build_index(root: str = config.RESOURCE_LIB) -> list[dict]` — list of card dicts (schema below), sorted by `ingested_at` desc.
  - Card dict schema: `{path, abspath, title, summary, folder, tags(list), kind("image"|"youtube"|"text"), image_abspath(str|None), youtube_id(str|None), source_label, vision_risk(bool), glyph_color, ingested_at(str), has_image(bool)}`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/resource_library_visualizer/test_notes.py
import importlib.util, pathlib, textwrap
TOOL = pathlib.Path("001_Architecture/Tools/Resource-Library-Visualizer")

def load(name):
    spec = importlib.util.spec_from_file_location(name, TOOL / f"{name}.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

notes = load("notes")


def test_parse_note_valid(tmp_path):
    p = tmp_path / "A.md"
    p.write_text('---\ntitle: "A"\ntags:\n  - x\n---\nbody here\n')
    fm, body = notes.parse_note(str(p))
    assert fm["title"] == "A"
    assert fm["tags"] == ["x"]
    assert body.strip() == "body here"


def test_parse_note_no_frontmatter(tmp_path):
    p = tmp_path / "B.md"
    p.write_text("# just markdown\n")
    fm, body = notes.parse_note(str(p))
    assert fm == {}
    assert "just markdown" in body


def test_find_sibling_image(tmp_path):
    (tmp_path / "OpenCode.md").write_text("x")
    (tmp_path / "OpenCode.png").write_bytes(b"\x89PNG")
    got = notes.find_sibling_image(str(tmp_path / "OpenCode.md"))
    assert got == str(tmp_path / "OpenCode.png")


def test_find_sibling_image_missing(tmp_path):
    (tmp_path / "Lonely.md").write_text("x")
    assert notes.find_sibling_image(str(tmp_path / "Lonely.md")) is None


def test_build_index_pairs_and_sorts(tmp_path):
    d = tmp_path / "Tools"
    d.mkdir()
    (d / "New.md").write_text('---\ntitle: "New"\nsummary: "s"\nenriched: 2026-09-05\n---\nx')
    (d / "New.png").write_bytes(b"\x89PNG\r\n")
    (d / "Old.md").write_text('---\ntitle: "Old"\ncreated: 2026-01-01\n---\nhttps://youtu.be/abcdefghijk')
    idx = notes.build_index(str(tmp_path))
    assert [c["title"] for c in idx] == ["New", "Old"]        # newest first
    assert idx[0]["kind"] == "image"
    assert idx[1]["kind"] == "youtube"
    assert idx[1]["youtube_id"] == "abcdefghijk"


def test_build_index_text_only_note(tmp_path):
    d = tmp_path / "Tools"; d.mkdir()
    (d / "Dedup-Review.md").write_text('---\ntitle: "Dedup Review"\n---\nno image no video')
    idx = notes.build_index(str(tmp_path))
    assert idx[0]["kind"] == "text"
    assert idx[0]["glyph_color"].startswith("#")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/resource_library_visualizer/test_notes.py -v`
Expected: FAIL — no `notes.py`.

- [ ] **Step 3: Write `notes.py`**

```python
import os, re, glob, importlib.util, pathlib
import yaml

_here = pathlib.Path(__file__).parent

def _load(name):
    spec = importlib.util.spec_from_file_location(f"rlv_{name}", _here / f"{name}.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m

config = _load("config")
detect = _load("detect")

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.S)
EMBED_RE = re.compile(r"!\[\[([^\]|]+?\.(?:png|jpe?g|webp|gif))", re.I)
MD_IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)]+?\.(?:png|jpe?g|webp|gif))\)", re.I)


def parse_note(path):
    text = open(path, encoding="utf-8", errors="ignore").read()
    m = FM_RE.match(text)
    if not m:
        return {}, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
        if not isinstance(fm, dict):
            return {}, text
    except yaml.YAMLError:
        return {}, text
    return fm, m.group(2)


def find_sibling_image(md_path):
    stem = os.path.splitext(md_path)[0]
    for ext in config.IMG_EXT:
        if os.path.isfile(stem + ext):
            return stem + ext
    return None


def first_embed_image(body, md_dir):
    for rx in (EMBED_RE, MD_IMG_RE):
        m = rx.search(body or "")
        if not m:
            continue
        name = os.path.basename(m.group(1).strip())
        cand = os.path.join(md_dir, name)
        if os.path.isfile(cand):
            return cand
    return None


def _ingested_at(fm, path):
    for k in ("enriched", "created"):
        v = fm.get(k)
        if v:
            return str(v)[:10]
    return __import__("datetime").date.fromtimestamp(os.path.getmtime(path)).isoformat()


def _folder(rel):
    parts = rel.split(os.sep)
    return parts[0] if len(parts) > 1 else ""


def build_index(root=None):
    root = root or config.RESOURCE_LIB
    cards = []
    for f in glob.glob(os.path.join(root, "**", "*.md"), recursive=True):
        if os.sep + ".git" + os.sep in f or "graphify-out" in f:
            continue
        fm, body = parse_note(f)
        rel = os.path.relpath(f, root)
        folder = _folder(rel)
        img = find_sibling_image(f) or first_embed_image(body, os.path.dirname(f))
        yid = detect.youtube_id(" ".join(str(fm.get(k, "")) for k in ("url", "source")) + " " + body)
        has_image = img is not None
        if has_image:
            kind = "image"
        elif yid:
            kind = "youtube"
        else:
            kind = "text"
        label, risk = detect.detect_source(fm, body, os.path.basename(f), has_image)
        fm_for_glyph = dict(fm); fm_for_glyph["_filename"] = os.path.basename(f)
        tags = [str(t) for t in (fm.get("tags") or []) if t]
        cards.append({
            "path": rel,
            "abspath": f,
            "title": str(fm.get("title") or os.path.splitext(os.path.basename(f))[0]),
            "summary": str(fm.get("summary") or fm.get("ai_description") or ""),
            "folder": folder,
            "tags": tags,
            "kind": kind,
            "image_abspath": img,
            "youtube_id": yid,
            "source_label": label,
            "vision_risk": risk,
            "glyph_color": detect.glyph_color(fm_for_glyph, folder),
            "ingested_at": _ingested_at(fm, f),
            "has_image": has_image,
        })
    cards.sort(key=lambda c: c["ingested_at"], reverse=True)
    return cards
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/resource_library_visualizer/test_notes.py -v`
Expected: PASS (6 tests).

- [ ] **Step 5: Sanity-run against the real library**

Run: `python3 -c "import importlib.util,pathlib; p=pathlib.Path('001_Architecture/Tools/Resource-Library-Visualizer/notes.py'); s=importlib.util.spec_from_file_location('n',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); idx=m.build_index(); print(len(idx),'notes'); import collections; print(collections.Counter(c['kind'] for c in idx))"`
Expected: prints ~4000 notes and a Counter with `image`, `youtube`, `text` counts (image+youtube should be ~1000+).

- [ ] **Step 6: Commit**

```bash
git add 001_Architecture/Tools/Resource-Library-Visualizer/notes.py tests/resource_library_visualizer/test_notes.py
git commit -m "feat(rl-visualizer): note scan + image pairing + card index"
```

---

### Task 4: `thumbs.py` — thumbnail cache + YouTube poster

**Files:**
- Create: `001_Architecture/Tools/Resource-Library-Visualizer/thumbs.py`
- Test: `tests/resource_library_visualizer/test_thumbs.py`

**Interfaces:**
- Consumes: `config.THUMB_CACHE`, `config.THUMB_W`, `config.RESOURCE_LIB`.
- Produces:
  - `thumb_path_for(image_abspath: str) -> str` — deterministic cache path (mirrors relative path under `RESOURCE_LIB`, `.jpg` appended); does NOT generate.
  - `ensure_thumb(image_abspath: str) -> str | None` — generate if missing or stale (source mtime newer), return cache path, or `None` on failure.
  - `youtube_poster_url(video_id: str) -> str` — `https://img.youtube.com/vi/<id>/hqdefault.jpg`.

- [ ] **Step 1: Write the failing tests**

```python
import importlib.util, pathlib
from PIL import Image
TOOL = pathlib.Path("001_Architecture/Tools/Resource-Library-Visualizer")

def load(name):
    spec = importlib.util.spec_from_file_location(name, TOOL / f"{name}.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

thumbs = load("thumbs")


def test_youtube_poster_url():
    assert thumbs.youtube_poster_url("abcdefghijk") == "https://img.youtube.com/vi/abcdefghijk/hqdefault.jpg"


def test_ensure_thumb_generates(tmp_path, monkeypatch):
    monkeypatch.setattr(thumbs.config, "THUMB_CACHE", str(tmp_path / "cache"))
    monkeypatch.setattr(thumbs.config, "RESOURCE_LIB", str(tmp_path))
    src = tmp_path / "Big.png"
    Image.new("RGB", (900, 600), "red").save(src)
    out = thumbs.ensure_thumb(str(src))
    assert out and pathlib.Path(out).is_file()
    assert Image.open(out).width == thumbs.config.THUMB_W


def test_ensure_thumb_cache_hit(tmp_path, monkeypatch):
    monkeypatch.setattr(thumbs.config, "THUMB_CACHE", str(tmp_path / "cache"))
    monkeypatch.setattr(thumbs.config, "RESOURCE_LIB", str(tmp_path))
    src = tmp_path / "X.png"
    Image.new("RGB", (400, 400), "blue").save(src)
    a = thumbs.ensure_thumb(str(src))
    mtime1 = pathlib.Path(a).stat().st_mtime_ns
    b = thumbs.ensure_thumb(str(src))
    assert a == b
    assert pathlib.Path(b).stat().st_mtime_ns == mtime1   # not regenerated
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/resource_library_visualizer/test_thumbs.py -v`
Expected: FAIL — no `thumbs.py`.

- [ ] **Step 3: Write `thumbs.py`**

```python
import os, importlib.util, pathlib
from PIL import Image, ImageOps

_here = pathlib.Path(__file__).parent
def _load(name):
    spec = importlib.util.spec_from_file_location(f"rlv_{name}", _here / f"{name}.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m
config = _load("config")


def youtube_poster_url(video_id):
    return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"


def thumb_path_for(image_abspath):
    try:
        rel = os.path.relpath(image_abspath, config.RESOURCE_LIB)
    except ValueError:
        rel = os.path.basename(image_abspath)
    return os.path.join(config.THUMB_CACHE, rel + ".jpg")


def ensure_thumb(image_abspath):
    if not image_abspath or not os.path.isfile(image_abspath):
        return None
    dst = thumb_path_for(image_abspath)
    if os.path.isfile(dst) and os.path.getmtime(dst) >= os.path.getmtime(image_abspath):
        return dst
    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        im = ImageOps.exif_transpose(Image.open(image_abspath)).convert("RGB")
        if im.width > config.THUMB_W:
            im = im.resize((config.THUMB_W, max(1, round(im.height * config.THUMB_W / im.width))))
        im.save(dst, "JPEG", quality=60)
        return dst
    except Exception:
        return None
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/resource_library_visualizer/test_thumbs.py -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add 001_Architecture/Tools/Resource-Library-Visualizer/thumbs.py tests/resource_library_visualizer/test_thumbs.py
git commit -m "feat(rl-visualizer): thumbnail cache + youtube poster"
```

---

### Task 5: `render.py` — Obsidian-style markdown → HTML

**Files:**
- Create: `001_Architecture/Tools/Resource-Library-Visualizer/render.py`
- Test: `tests/resource_library_visualizer/test_render.py`

**Interfaces:**
- Consumes: `markdown_it`.
- Produces:
  - `render_body(body: str, note_rel_dir: str) -> str` — HTML. Transforms applied BEFORE markdown-it:
    - `![[name.png]]` → `<img src="/img?path=<note_rel_dir>/name.png">`
    - bare YouTube URL on its own line, or `![[...youtube...]]` → `<iframe>` embed
    - `[[Wiki Link]]` / `[[Wiki Link|alias]]` → `<span class="wikilink">alias</span>`
    - `> [!type] Title` callout blocks → `<div class="callout callout-type"><b>Title</b>…</div>`
  - `frontmatter_html(fm: dict) -> str` — a `<dl>` of key/value pairs, `url` rendered as a link.

- [ ] **Step 1: Write the failing tests**

```python
import importlib.util, pathlib
TOOL = pathlib.Path("001_Architecture/Tools/Resource-Library-Visualizer")
def load(name):
    spec = importlib.util.spec_from_file_location(name, TOOL / f"{name}.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod
render = load("render")


def test_embed_image_becomes_img_tag():
    out = render.render_body("![[Shot-1.png]]", "Tools")
    assert '<img src="/img?path=Tools/Shot-1.png"' in out


def test_youtube_url_becomes_iframe():
    out = render.render_body("https://youtu.be/abcdefghijk", "Tutorials")
    assert "<iframe" in out and "abcdefghijk" in out


def test_wikilink_alias_rendered():
    out = render.render_body("see [[Some Note|that note]] ok", "Tools")
    assert "that note" in out and "[[" not in out


def test_callout_block():
    out = render.render_body("> [!info] Heads up\n> body text", "Tools")
    assert "callout" in out and "Heads up" in out


def test_frontmatter_html_links_url():
    out = render.frontmatter_html({"title": "A", "url": "https://x.com"})
    assert '<a href="https://x.com"' in out
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/resource_library_visualizer/test_render.py -v`
Expected: FAIL — no `render.py`.

- [ ] **Step 3: Write `render.py`**

```python
import re, html
from markdown_it import MarkdownIt

_md = MarkdownIt("commonmark", {"html": False, "linkify": True, "breaks": True})

YT = re.compile(r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([A-Za-z0-9_-]{11})")


def _embeds(body, note_rel_dir):
    def img_sub(m):
        name = m.group(1).strip().split("|")[0]
        if YT.search(name):
            vid = YT.search(name).group(1)
            return f'\n<iframe class="yt" src="https://www.youtube.com/embed/{vid}" allowfullscreen></iframe>\n'
        return f'\n<img src="/img?path={html.escape(note_rel_dir)}/{html.escape(name)}" loading="lazy">\n'
    body = re.sub(r"!\[\[([^\]]+?)\]\]", img_sub, body)

    def yt_line(m):
        return f'\n<iframe class="yt" src="https://www.youtube.com/embed/{m.group(1)}" allowfullscreen></iframe>\n'
    body = re.sub(r"^\s*https?://\S*" + YT.pattern + r"\S*\s*$", yt_line, body, flags=re.M)

    def wl(m):
        inner = m.group(1)
        alias = inner.split("|", 1)[1] if "|" in inner else inner
        return f'<span class="wikilink">{html.escape(alias)}</span>'
    body = re.sub(r"\[\[([^\]]+?)\]\]", wl, body)
    return body


def _callouts(body):
    lines = body.split("\n")
    out, i = [], 0
    while i < len(lines):
        m = re.match(r">\s*\[!(\w+)\]\s*(.*)", lines[i])
        if not m:
            out.append(lines[i]); i += 1; continue
        typ, title = m.group(1).lower(), m.group(2).strip()
        i += 1
        inner = []
        while i < len(lines) and lines[i].startswith(">"):
            inner.append(lines[i].lstrip("> ").rstrip())
            i += 1
        body_html = _md.render("\n".join(inner)) if inner else ""
        out.append(f'<div class="callout callout-{typ}"><b>{html.escape(title)}</b>{body_html}</div>')
    return "\n".join(out)


def render_body(body, note_rel_dir):
    body = _embeds(body or "", note_rel_dir)
    body = _callouts(body)
    return _md.render(body)


def frontmatter_html(fm):
    rows = []
    for k, v in (fm or {}).items():
        if k == "url" and isinstance(v, str) and v.startswith("http"):
            val = f'<a href="{html.escape(v)}" target="_blank">{html.escape(v)}</a>'
        elif isinstance(v, list):
            val = ", ".join(html.escape(str(x)) for x in v)
        else:
            val = html.escape(str(v))
        rows.append(f"<dt>{html.escape(str(k))}</dt><dd>{val}</dd>")
    return "<dl class='fm'>" + "".join(rows) + "</dl>"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/resource_library_visualizer/test_render.py -v`
Expected: PASS (5 tests). If `test_youtube_url_becomes_iframe` fails on the regex, simplify the line-match to `re.sub(YT, yt_line_by_id, body)` operating on whole-body and assert the id appears — adjust test accordingly.

- [ ] **Step 5: Commit**

```bash
git add 001_Architecture/Tools/Resource-Library-Visualizer/render.py tests/resource_library_visualizer/test_render.py
git commit -m "feat(rl-visualizer): obsidian-style markdown render"
```

---

### Task 6: `queue.py` — Review Queue append / delete-log / finalize + shared `conftest.py`

**Files:**
- Create: `001_Architecture/Tools/Resource-Library-Visualizer/queue.py`
- Create: `tests/resource_library_visualizer/conftest.py`
- Test: `tests/resource_library_visualizer/test_queue.py`

**Interfaces:**
- Consumes: `config.QUEUE_FILE`, `config.QUEUE_DIR`.
- Produces:
  - `add_comment(note_path: str, text: str) -> None` — append a `- [ ] COMMENT  <path>` entry (+ indented quote) under the current open batch.
  - `log_delete(note_path: str) -> None` — append a `- [x] DELETE  <path>  (moved …)` entry.
  - `finalize() -> str` — replace the open batch header with a `FINALIZED <ts> (N comments, M deletes)` header, start a fresh open batch, return the finalized batch text.
  - `_ensure_open_batch() -> None` — internal; creates the file + an `## Batch — open (started <ts>)` header if absent.
- `conftest.py` provides: `load` fixture-free helper (module import by path) and a `rl_fixture` fixture (temp RL tree with 3 notes) reused by Task 7 and Task 8.

- [ ] **Step 1: Write `conftest.py`**

```python
import importlib.util, pathlib
import pytest
from PIL import Image

TOOL = pathlib.Path("001_Architecture/Tools/Resource-Library-Visualizer")

def load(name):
    spec = importlib.util.spec_from_file_location(name, TOOL / f"{name}.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

@pytest.fixture
def rl_fixture(tmp_path):
    root = tmp_path / "007_Resource_Library"
    (root / "Tools").mkdir(parents=True)
    (root / "Tools" / "OpenCode.md").write_text(
        '---\ntitle: "OpenCode"\nsummary: "A CLI"\nurl: "https://opencode.dev"\n'
        'tags:\n  - ai\n  - github-repo\nenriched: 2026-09-05\n---\n![[OpenCode.png]]\n')
    Image.new("RGB", (600, 400), "green").save(root / "Tools" / "OpenCode.png")
    (root / "Tools" / "MisLabel.md").write_text(
        '---\ntitle: "Photoshop Plugin"\nsummary: "wrong"\noriginal_filename: "IMG_8710.PNG"\n'
        'tags:\n  - screenshot\ncreated: 2026-08-01\n---\n![[MisLabel.png]]\n')
    Image.new("RGB", (500, 500), "blue").save(root / "Tools" / "MisLabel.png")
    (root / "Tutorials").mkdir()
    (root / "Tutorials" / "Vid.md").write_text(
        '---\ntitle: "Vid"\ncreated: 2026-07-01\n---\nhttps://youtu.be/abcdefghijk\n')
    return root
```

- [ ] **Step 2: Write the failing tests**

```python
from conftest import load

def _q(monkeypatch, tmp_path):
    queue = load("queue")
    monkeypatch.setattr(queue.config, "QUEUE_DIR", str(tmp_path))
    monkeypatch.setattr(queue.config, "QUEUE_FILE", str(tmp_path / "Review_Queue.md"))
    return queue


def test_add_comment_creates_batch_and_entry(monkeypatch, tmp_path):
    q = _q(monkeypatch, tmp_path)
    q.add_comment("Tools/MisLabel.md", "should be a github repo not a plugin")
    txt = open(q.config.QUEUE_FILE).read()
    assert "## Batch — open" in txt
    assert "- [ ] COMMENT  Tools/MisLabel.md" in txt
    assert "should be a github repo" in txt


def test_log_delete_entry(monkeypatch, tmp_path):
    q = _q(monkeypatch, tmp_path)
    q.log_delete("Research/Old.md")
    txt = open(q.config.QUEUE_FILE).read()
    assert "- [x] DELETE   Research/Old.md" in txt


def test_finalize_seals_and_reopens(monkeypatch, tmp_path):
    q = _q(monkeypatch, tmp_path)
    q.add_comment("A.md", "x")
    q.log_delete("B.md")
    sealed = q.finalize()
    txt = open(q.config.QUEUE_FILE).read()
    assert "FINALIZED" in txt and "(1 comments, 1 deletes)" in txt
    assert txt.count("## Batch — open") == 1          # a fresh one was opened
    assert "COMMENT  A.md" in sealed
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `python3 -m pytest tests/resource_library_visualizer/test_queue.py -v`
Expected: FAIL — no `queue.py`.

- [ ] **Step 4: Write `queue.py`**

```python
import os, re, importlib.util, pathlib
from datetime import datetime

_here = pathlib.Path(__file__).parent
def _load(name):
    spec = importlib.util.spec_from_file_location(f"rlv_{name}", _here / f"{name}.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m
config = _load("config")

OPEN_HDR = "## Batch — open (started {ts})\n"


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def _read():
    try:
        return open(config.QUEUE_FILE, encoding="utf-8").read()
    except FileNotFoundError:
        return ""


def _write(txt):
    os.makedirs(config.QUEUE_DIR, exist_ok=True)
    open(config.QUEUE_FILE, "w", encoding="utf-8").write(txt)


def _ensure_open_batch():
    txt = _read()
    if "## Batch — open" not in txt:
        txt = (txt + ("\n" if txt and not txt.endswith("\n") else "")
               + OPEN_HDR.format(ts=_now()))
        _write(txt)


def add_comment(note_path, text):
    _ensure_open_batch()
    entry = f"\n- [ ] COMMENT  {note_path}\n      \"{text.strip()}\"\n"
    _write(_read() + entry)


def log_delete(note_path):
    _ensure_open_batch()
    entry = f"\n- [x] DELETE   {note_path}  (moved to {config.DELETE_DIR} {_now()})\n"
    _write(_read() + entry)


def finalize():
    _ensure_open_batch()
    txt = _read()
    start = txt.index("## Batch — open")
    batch = txt[start:]
    comments = batch.count("- [ ] COMMENT")
    deletes = batch.count("] DELETE")
    sealed_hdr = f"## Batch — FINALIZED {_now()}  ({comments} comments, {deletes} deletes)\n"
    new = txt[:start] + sealed_hdr + batch[batch.index("\n") + 1:]
    new = new.rstrip() + "\n\n" + OPEN_HDR.format(ts=_now())
    _write(new)
    return sealed_hdr + batch[batch.index("\n") + 1:]
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m pytest tests/resource_library_visualizer/test_queue.py -v`
Expected: PASS (3 tests). Adjust the exact spacing assertions in the test if the string format differs (`DELETE   ` has 3 spaces).

- [ ] **Step 6: Commit**

```bash
git add 001_Architecture/Tools/Resource-Library-Visualizer/queue.py tests/resource_library_visualizer/conftest.py tests/resource_library_visualizer/test_queue.py
git commit -m "feat(rl-visualizer): review queue + shared test fixture"
```

---

### Task 7: `actions.py` — move-to-delete + rewrite-note-fields

**Files:**
- Create: `001_Architecture/Tools/Resource-Library-Visualizer/actions.py`
- Test: `tests/resource_library_visualizer/test_actions.py`

**Interfaces:**
- Consumes: `config.RESOURCE_LIB`, `config.DELETE_DIR`, `config.IMG_EXT`, `notes.parse_note`, `notes.find_sibling_image`, `queue.log_delete`.
- Produces:
  - `move_to_delete(note_rel_path: str) -> list[str]` — moves the `.md` + every same-stem sibling image into `DELETE_DIR/<note_rel_path dir>/`; returns list of moved absolute destinations; calls `queue.log_delete`.
  - `rewrite_note(note_rel_path: str, fields: dict) -> None` — updates frontmatter keys among `{title, summary, url, tags}` (tags accepts a list or comma string) and, if `fields["body"]` present, replaces the body. Preserves key order; adds a key if missing. Leaves other frontmatter untouched.

- [ ] **Step 1: Write the failing tests**

```python
from conftest import load

def _mod(monkeypatch, root):
    actions = load("actions")
    monkeypatch.setattr(actions.config, "RESOURCE_LIB", str(root))
    monkeypatch.setattr(actions.config, "DELETE_DIR", str(root.parent / "delete"))
    monkeypatch.setattr(actions.queue, "log_delete", lambda *a, **k: None)
    return actions


def test_move_to_delete_takes_note_and_image(monkeypatch, rl_fixture):
    a = _mod(monkeypatch, rl_fixture)
    moved = a.move_to_delete("Tools/OpenCode.md")
    assert not (rl_fixture / "Tools" / "OpenCode.md").exists()
    assert not (rl_fixture / "Tools" / "OpenCode.png").exists()
    assert any(p.endswith("OpenCode.md") for p in moved)
    assert (rl_fixture.parent / "delete" / "Tools" / "OpenCode.png").exists()


def test_rewrite_note_fixes_fields(monkeypatch, rl_fixture):
    a = _mod(monkeypatch, rl_fixture)
    a.rewrite_note("Tools/MisLabel.md", {
        "title": "Cool GitHub Repo",
        "summary": "Actually an unrelated OSS project.",
        "url": "https://github.com/foo/bar",
        "tags": "github-repo, oss",
    })
    fm, body = load("notes").parse_note(str(rl_fixture / "Tools" / "MisLabel.md"))
    assert fm["title"] == "Cool GitHub Repo"
    assert fm["url"] == "https://github.com/foo/bar"
    assert fm["tags"] == ["github-repo", "oss"]
    assert fm["original_filename"] == "IMG_8710.PNG"   # untouched


def test_rewrite_note_replaces_body(monkeypatch, rl_fixture):
    a = _mod(monkeypatch, rl_fixture)
    a.rewrite_note("Tutorials/Vid.md", {"body": "new body\n"})
    _, body = load("notes").parse_note(str(rl_fixture / "Tutorials" / "Vid.md"))
    assert body.strip() == "new body"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/resource_library_visualizer/test_actions.py -v`
Expected: FAIL — no `actions.py`.

- [ ] **Step 3: Write `actions.py`**

```python
import os, re, shutil, importlib.util, pathlib
import yaml

_here = pathlib.Path(__file__).parent
def _load(name):
    spec = importlib.util.spec_from_file_location(f"rlv_{name}", _here / f"{name}.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m
config = _load("config")
notes = _load("notes")
queue = _load("queue")

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.S)


def move_to_delete(note_rel_path):
    src_md = os.path.join(config.RESOURCE_LIB, note_rel_path)
    dst_dir = os.path.join(config.DELETE_DIR, os.path.dirname(note_rel_path))
    os.makedirs(dst_dir, exist_ok=True)
    moved = []
    stem = os.path.splitext(src_md)[0]
    candidates = [src_md] + [stem + e for e in config.IMG_EXT]
    for src in candidates:
        if os.path.isfile(src):
            dst = os.path.join(dst_dir, os.path.basename(src))
            shutil.move(src, dst)
            moved.append(dst)
    queue.log_delete(note_rel_path)
    return moved


def _coerce_tags(v):
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    return [t.strip() for t in str(v).split(",") if t.strip()]


def rewrite_note(note_rel_path, fields):
    path = os.path.join(config.RESOURCE_LIB, note_rel_path)
    text = open(path, encoding="utf-8").read()
    m = FM_RE.match(text)
    fm_text, body = (m.group(1), m.group(2)) if m else ("", text)
    fm = yaml.safe_load(fm_text) or {} if fm_text else {}
    if not isinstance(fm, dict):
        fm = {}
    for key in ("title", "summary", "url"):
        if key in fields and fields[key] is not None:
            fm[key] = str(fields[key])
    if "tags" in fields and fields["tags"] is not None:
        fm["tags"] = _coerce_tags(fields["tags"])
    if fields.get("body") is not None:
        body = fields["body"]
        if not body.endswith("\n"):
            body += "\n"
    new_fm = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True).strip()
    open(path, "w", encoding="utf-8").write(f"---\n{new_fm}\n---\n{body}")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/resource_library_visualizer/test_actions.py -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add 001_Architecture/Tools/Resource-Library-Visualizer/actions.py tests/resource_library_visualizer/test_actions.py
git commit -m "feat(rl-visualizer): delete-move + note field rewrite"
```

---

### Task 8: `actions.py` — Re-run AI wrapper

**Files:**
- Modify: `001_Architecture/Tools/Resource-Library-Visualizer/actions.py`
- Test: `tests/resource_library_visualizer/test_actions.py` (add cases)

**Interfaces:**
- Consumes: `001_Architecture/Scripts/process_image_ingest.py` (the Vision re-analysis path).
- Produces:
  - `rerun_ai(note_rel_path: str, vision_fn=None) -> dict` — returns `{"before": {...}, "after": {...}, "applied": False}`. `vision_fn(image_abspath) -> dict` is injectable for tests; default imports and calls the real one from `process_image_ingest`. Does NOT write — the server decides whether to apply via `rewrite_note`.
  - `estimate_rerun_cost(n: int) -> float` — `n * 0.01` (rough Vision $/call), for the confirm dialog.

- [ ] **Step 1: Inspect the real ingest script**

Run: `grep -nE "def |vision|analyze|client|gpt-|gemini|model" 001_Architecture/Scripts/process_image_ingest.py | head -40`
Expected: identify the function that takes an image path and returns frontmatter/description. Note its name and signature in a comment in `actions.py`. If no cleanly callable function exists, `rerun_ai`'s default `vision_fn` should `raise NotImplementedError("wire process_image_ingest.analyze_image")` — the injectable path still lets the server + tests work, and the wiring becomes a follow-up.

- [ ] **Step 2: Write the failing tests**

```python
def test_rerun_ai_returns_before_after(monkeypatch, rl_fixture):
    a = _mod(monkeypatch, rl_fixture)
    fake = lambda img: {"title": "Corrected Title", "summary": "fixed", "tags": ["github-repo"]}
    out = a.rerun_ai("Tools/MisLabel.md", vision_fn=fake)
    assert out["before"]["title"] == "Photoshop Plugin"
    assert out["after"]["title"] == "Corrected Title"
    assert out["applied"] is False


def test_estimate_rerun_cost():
    a = load("actions")
    assert a.estimate_rerun_cost(10) == 0.10
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `python3 -m pytest tests/resource_library_visualizer/test_actions.py -k rerun -v`
Expected: FAIL — no `rerun_ai`.

- [ ] **Step 4: Add to `actions.py`**

```python
def estimate_rerun_cost(n):
    return round(n * 0.01, 2)


def _default_vision(image_abspath):
    import importlib.util, pathlib
    p = pathlib.Path(config.WORKSPACE) / "001_Architecture/Scripts/process_image_ingest.py"
    spec = importlib.util.spec_from_file_location("pii", p)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    # TODO(wiring): confirmed function name from Step 1 grep goes here.
    if hasattr(mod, "analyze_image"):
        return mod.analyze_image(image_abspath)
    raise NotImplementedError("wire process_image_ingest vision entrypoint")


def rerun_ai(note_rel_path, vision_fn=None):
    vision_fn = vision_fn or _default_vision
    path = os.path.join(config.RESOURCE_LIB, note_rel_path)
    before, _ = notes.parse_note(path)
    img = notes.find_sibling_image(path)
    after_raw = vision_fn(img) if img else {}
    after = dict(before)
    for k in ("title", "summary", "url", "tags"):
        if k in after_raw and after_raw[k]:
            after[k] = after_raw[k]
    return {"before": before, "after": after, "applied": False}
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m pytest tests/resource_library_visualizer/test_actions.py -v`
Expected: PASS (5 tests total in file).

- [ ] **Step 6: Commit**

```bash
git add 001_Architecture/Tools/Resource-Library-Visualizer/actions.py tests/resource_library_visualizer/test_actions.py
git commit -m "feat(rl-visualizer): re-run-AI wrapper + cost estimate"
```

---

### Task 9: `serve.py` — Flask app wiring all endpoints

**Files:**
- Create: `001_Architecture/Tools/Resource-Library-Visualizer/serve.py`
- Test: `tests/resource_library_visualizer/test_serve.py`

**Interfaces:**
- Consumes: every module above.
- Produces:
  - `create_app() -> flask.Flask` — factory (so tests get a client without binding the port).
  - Routes: `GET /`, `GET /api/notes`, `GET /api/note`, `GET /thumb`, `GET /img`, `PATCH /api/note`, `POST /api/delete`, `POST /api/rerun-ai`, `POST /api/comment`, `POST /api/queue/finalize`, `GET /api/filters` (folders present + top-8 tags).
  - `main()` — builds app, opens `http://localhost:8756`, runs.
- Index is built once at startup and cached on `app.config["INDEX"]`; `POST /api/delete` and `PATCH` mutate the cached list in place so the grid stays consistent without a full rescan. `GET /api/notes?refresh=1` forces a rescan.

- [ ] **Step 1: Write the failing tests**

```python
import json
from conftest import load

def _client(monkeypatch, rl_fixture, tmp_path):
    serve = load("serve")
    for mod_name in ("config",):
        pass
    # point every module's config at the fixture
    for m in (serve.notes.config, serve.thumbs.config, serve.actions.config, serve.queue.config, serve.config):
        monkeypatch.setattr(m, "RESOURCE_LIB", str(rl_fixture))
        monkeypatch.setattr(m, "THUMB_CACHE", str(tmp_path / "thumbs"))
        monkeypatch.setattr(m, "DELETE_DIR", str(tmp_path / "delete"))
        monkeypatch.setattr(m, "QUEUE_DIR", str(tmp_path / "rev"))
        monkeypatch.setattr(m, "QUEUE_FILE", str(tmp_path / "rev" / "Review_Queue.md"))
    app = serve.create_app()
    app.testing = True
    return app.test_client()


def test_notes_endpoint_lists_cards(monkeypatch, rl_fixture, tmp_path):
    c = _client(monkeypatch, rl_fixture, tmp_path)
    r = c.get("/api/notes")
    data = r.get_json()
    titles = [x["title"] for x in data]
    assert "OpenCode" in titles and "Vid" in titles


def test_note_detail_renders_body(monkeypatch, rl_fixture, tmp_path):
    c = _client(monkeypatch, rl_fixture, tmp_path)
    r = c.get("/api/note", query_string={"path": "Tutorials/Vid.md"})
    d = r.get_json()
    assert "<iframe" in d["body_html"]
    assert "abcdefghijk" in d["body_html"]


def test_delete_moves_and_updates_index(monkeypatch, rl_fixture, tmp_path):
    c = _client(monkeypatch, rl_fixture, tmp_path)
    r = c.post("/api/delete", json={"paths": ["Tools/OpenCode.md"]})
    assert r.get_json()["ok"] is True
    assert not (rl_fixture / "Tools" / "OpenCode.md").exists()
    remaining = [x["path"] for x in c.get("/api/notes").get_json()]
    assert "Tools/OpenCode.md" not in remaining


def test_patch_note_writes_fields(monkeypatch, rl_fixture, tmp_path):
    c = _client(monkeypatch, rl_fixture, tmp_path)
    r = c.patch("/api/note", json={"path": "Tools/MisLabel.md", "title": "Fixed"})
    assert r.get_json()["ok"] is True
    fm, _ = load("notes").parse_note(str(rl_fixture / "Tools" / "MisLabel.md"))
    assert fm["title"] == "Fixed"


def test_comment_and_finalize(monkeypatch, rl_fixture, tmp_path):
    c = _client(monkeypatch, rl_fixture, tmp_path)
    c.post("/api/comment", json={"path": "Tools/MisLabel.md", "text": "retag please"})
    r = c.post("/api/queue/finalize")
    assert "FINALIZED" in r.get_json()["batch"]


def test_filters_endpoint(monkeypatch, rl_fixture, tmp_path):
    c = _client(monkeypatch, rl_fixture, tmp_path)
    d = c.get("/api/filters").get_json()
    assert "Tools" in d["folders"]
    assert isinstance(d["top_tags"], list)


def test_index_serves_html(monkeypatch, rl_fixture, tmp_path):
    c = _client(monkeypatch, rl_fixture, tmp_path)
    r = c.get("/")
    assert r.status_code == 200 and b"<title>" in r.data
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/resource_library_visualizer/test_serve.py -v`
Expected: FAIL — no `serve.py`.

- [ ] **Step 3: Write `serve.py`**

```python
import os, io, collections, importlib.util, pathlib, webbrowser, threading
from flask import Flask, request, jsonify, send_file, Response, abort

_here = pathlib.Path(__file__).parent
def _load(name):
    spec = importlib.util.spec_from_file_location(f"rlv_{name}", _here / f"{name}.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m
config = _load("config")
notes = _load("notes")
thumbs = _load("thumbs")
render = _load("render")
queue = _load("queue")
actions = _load("actions")

APP_HTML = (_here / "app.html").read_text(encoding="utf-8")


def _safe_abs(rel):
    p = os.path.normpath(os.path.join(config.RESOURCE_LIB, rel))
    if not p.startswith(os.path.realpath(config.RESOURCE_LIB) + os.sep) and p != config.RESOURCE_LIB:
        # allow when RESOURCE_LIB itself isn't realpath-normalized (tests use tmp_path)
        if not p.startswith(config.RESOURCE_LIB + os.sep):
            abort(400)
    return p


def _card_public(c):
    d = {k: c[k] for k in ("path", "title", "summary", "folder", "tags", "kind",
                           "source_label", "vision_risk", "glyph_color",
                           "ingested_at", "youtube_id")}
    if c["kind"] == "image" and c["image_abspath"]:
        d["thumb"] = "/thumb?path=" + c["path"]
    elif c["kind"] == "youtube" and c["youtube_id"]:
        d["thumb"] = thumbs.youtube_poster_url(c["youtube_id"])
    else:
        d["thumb"] = None
    return d


def create_app():
    app = Flask(__name__)
    app.config["INDEX"] = notes.build_index()

    def idx():
        return app.config["INDEX"]

    @app.get("/")
    def home():
        return Response(APP_HTML, mimetype="text/html")

    @app.get("/api/notes")
    def api_notes():
        if request.args.get("refresh"):
            app.config["INDEX"] = notes.build_index()
        return jsonify([_card_public(c) for c in idx()])

    @app.get("/api/filters")
    def api_filters():
        folders = sorted({c["folder"] for c in idx() if c["folder"]})
        tag_counts = collections.Counter(t for c in idx() for t in c["tags"])
        return jsonify({"folders": folders,
                        "top_tags": [t for t, _ in tag_counts.most_common(8)]})

    @app.get("/api/note")
    def api_note():
        rel = request.args["path"]
        ab = _safe_abs(rel)
        fm, body = notes.parse_note(ab)
        return jsonify({
            "path": rel,
            "frontmatter": fm,
            "frontmatter_html": render.frontmatter_html(fm),
            "body_html": render.render_body(body, os.path.dirname(rel)),
        })

    @app.get("/thumb")
    def thumb():
        c = next((x for x in idx() if x["path"] == request.args["path"]), None)
        if not c or not c["image_abspath"]:
            abort(404)
        t = thumbs.ensure_thumb(c["image_abspath"])
        if not t:
            abort(404)
        return send_file(t, mimetype="image/jpeg")

    @app.get("/img")
    def img():
        ab = _safe_abs(request.args["path"])
        if not os.path.isfile(ab):
            abort(404)
        return send_file(ab)

    @app.patch("/api/note")
    def patch_note():
        body = request.get_json(force=True)
        rel = body.pop("path")
        actions.rewrite_note(rel, body)
        for c in idx():
            if c["path"] == rel:
                fm, nb = notes.parse_note(os.path.join(config.RESOURCE_LIB, rel))
                c["title"] = str(fm.get("title") or c["title"])
                c["summary"] = str(fm.get("summary") or "")
                c["tags"] = [str(t) for t in (fm.get("tags") or [])]
        return jsonify({"ok": True})

    @app.post("/api/delete")
    def delete():
        paths = request.get_json(force=True)["paths"]
        moved = {}
        for p in paths:
            moved[p] = actions.move_to_delete(p)
        app.config["INDEX"] = [c for c in idx() if c["path"] not in set(paths)]
        return jsonify({"ok": True, "moved": moved})

    @app.post("/api/rerun-ai")
    def rerun():
        body = request.get_json(force=True)
        paths = body["paths"] if "paths" in body else [body["path"]]
        results = {}
        for p in paths:
            try:
                results[p] = actions.rerun_ai(p)
            except NotImplementedError as e:
                results[p] = {"error": str(e)}
        return jsonify({"ok": True, "results": results,
                        "est_cost": actions.estimate_rerun_cost(len(paths))})

    @app.post("/api/comment")
    def comment():
        b = request.get_json(force=True)
        queue.add_comment(b["path"], b["text"])
        return jsonify({"ok": True})

    @app.post("/api/queue/finalize")
    def finalize():
        return jsonify({"ok": True, "batch": queue.finalize()})

    return app


def main():
    app = create_app()
    url = f"http://localhost:{config.PORT}"
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    print(f"Resource Library Visualizer -> {url}  ({len(app.config['INDEX'])} notes)")
    app.run(port=config.PORT, debug=False)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/resource_library_visualizer/test_serve.py -v`
Expected: PASS (7 tests). If `_safe_abs` rejects tmp_path fixtures, relax it as shown (the fixture root is not under the real `RESOURCE_LIB`).

- [ ] **Step 5: Commit**

```bash
git add 001_Architecture/Tools/Resource-Library-Visualizer/serve.py tests/resource_library_visualizer/test_serve.py
git commit -m "feat(rl-visualizer): flask server wiring all endpoints"
```

---

### Task 10: `app.html` — the single-page app

**Files:**
- Create: `001_Architecture/Tools/Resource-Library-Visualizer/app.html`
- Test: manual (checklist below) + a JS-syntax smoke check.

**Interfaces:**
- Consumes: the server API from Task 9.
- Produces: no code other modules import. A `<title>` tag must be present (Task 9's `test_index_serves_html` checks it).

Layout / behavior (build to this — code is yours, keep CSS+JS inline, no CDN):

- **Header (sticky):** app title + live count ("N shown · M selected"). Search box (title/filename contains).
- **Filter row 1 — Folders:** a toggle button per folder from `/api/filters`.
- **Filter row 2 — Source:** `YouTube` / `Screenshot` / `Bookmark` toggles.
- **Filter row 3 — Tags:** the 8 buttons from `top_tags`.
- **Text-only toggle:** "Show text-only notes" (default OFF → filter out `kind === "text"`).
- **Action bar (shows when ≥1 selected):** a `<select>` — `Delete` / `Re-run AI` — plus an **Apply** button, and **Clear selection**.
- **Grid:** `repeat(auto-fill, minmax(220px, 1fr))`. Each card:
  - thumbnail (`<img loading=lazy>` from `card.thumb`; for `kind==="text"` render a `<div>` glyph box filled with `card.glyph_color` + a monospace ".md"). Play-triangle overlay when `kind==="youtube"`.
  - title (bold, 2-line clamp), summary (3-line clamp, muted).
  - footer line 1: folder pill (background tinted from a hashed palette).
  - footer line 2: up to 2 tag pills (soft palette — see below).
  - footer line 3: source label pill right-aligned; `Screenshot` in amber `#d97706`, `YouTube` in red `#dc2626`, `Bookmark` in blue `#2563eb`. If `vision_risk`, add a tiny "⚠" before the label.
  - click card body → open detail; click the checkbox (top-left, appears on hover / when any selected) → toggle selection.
- **Soft tag palette:** cycle `['#e0e7ff','#fce7f3','#dcfce7','#fef9c3','#ffedd5','#f3e8ff']` with matching darker text, keyed by a hash of the tag string (stable colors).
- **Detail slide-over (right, ~60% width, Esc closes):**
  - frontmatter block (`frontmatter_html`), then `body_html`.
  - buttons: **Edit**, **Re-run AI**, **Add Comment**, **Delete**.
  - **Edit** → swaps the frontmatter block for inputs (title / summary / url / tags) + a body `<textarea>`; **Save** → `PATCH /api/note` → reload detail + patch the card in the grid.
  - **Add Comment** → `<textarea>` + Send → `POST /api/comment` → toast "queued".
  - **Re-run AI** → confirm (`est_cost`) → `POST /api/rerun-ai` → show before/after `<pre>` diff → **Apply** (calls `PATCH /api/note` with the `after` fields) or **Discard**.
- **Queue button (header, right):** "Finalize Queue" → confirm → `POST /api/queue/finalize` → modal with the returned batch text, a Copy button, and a Download button (`Blob`, `a.download`).
- **After Delete** (card or detail): remove the card(s) from the DOM immediately; close detail if open on a deleted note.
- Theme: `color-scheme: light dark`; dark-mode via `@media (prefers-color-scheme: dark)`. Match the seed page's visual language (`build_image_cull.py`).

- [ ] **Step 1: Build `app.html`** to the spec above.

- [ ] **Step 2: JS syntax smoke check**

Run: `python3 - <<'EOF'
import re, pathlib
h = pathlib.Path("001_Architecture/Tools/Resource-Library-Visualizer/app.html").read_text()
assert "<title>" in h, "missing <title>"
m = re.search(r"<script>(.*)</script>", h, re.S)
assert m, "no inline script"
open("/tmp/_rlv_app.js","w").write(m.group(1))
print("script chars:", len(m.group(1)))
EOF
node --check /tmp/_rlv_app.js`
Expected: prints char count, `node --check` reports no syntax errors. (If `node` absent, skip — the manual test in Task 11 covers it.)

- [ ] **Step 3: Run the full test suite**

Run: `python3 -m pytest tests/resource_library_visualizer/ -v`
Expected: all green.

- [ ] **Step 4: Commit**

```bash
git add 001_Architecture/Tools/Resource-Library-Visualizer/app.html
git commit -m "feat(rl-visualizer): single-page browser app"
```

---

### Task 11: End-to-end manual test + docs + TOOLBOX

**Files:**
- Modify: `001_Architecture/Tools/Resource-Library-Visualizer/README.md` (add a "Known limits" section)
- Modify: `/Users/tonymacbook2025/Documents/Agent-OS/TOOLBOX.md` (add the tool)
- Modify: `007_Resource_Library/Directory.md` (one line: the review tool exists)

- [ ] **Step 1: Launch against the real library**

Run: `python3 001_Architecture/Tools/Resource-Library-Visualizer/serve.py`
Expected: browser opens `http://localhost:8756`; grid populates with the image/YouTube notes, newest first.

- [ ] **Step 2: Walk the success criteria** (from the spec). Verify each, note failures:
  - grid loads in one page, thumbnails lazy-load
  - folder / source / tag filters update the grid instantly
  - select ~10 cards → Delete → gone from grid, present in `~/Desktop/delete/`
  - open a `vision_risk` note → Edit title/url/tags → Save → re-open → persisted; check the `.md` on disk
  - Add Comment → Finalize Queue → `~/Desktop/Resource_Library_Review/Review_Queue.md` has the batch
  - detail view renders inline images + a YouTube embed
  - text-only toggle reveals `.md` glyph cards with sensible colors

- [ ] **Step 3: Fix anything broken**, re-run `python3 -m pytest tests/resource_library_visualizer/ -v`, commit fixes.

- [ ] **Step 4: Restore any test-deleted notes**

Run: `ls ~/Desktop/delete/` — move anything deleted during testing back into `007_Resource_Library/` (or confirm with Tony they're genuine culls). The tool is for real use, not the test's leftovers.

- [ ] **Step 5: Update `TOOLBOX.md`**

Add under the appropriate section:

```markdown
- **Resource Library Visualizer** — local browser gallery for reviewing/culling
  `007_Resource_Library` image notes. Run
  `python3 001_Architecture/Tools/Resource-Library-Visualizer/serve.py`
  (→ localhost:8756). Cull → `~/Desktop/delete/`; comments/edits →
  `~/Desktop/Resource_Library_Review/Review_Queue.md`.
```

- [ ] **Step 6: Add "Known limits" to README** — heuristic source labels (~90%), `Re-run AI` wiring status from Task 8 Step 1, no in-app git.

- [ ] **Step 7: Final commit**

```bash
git add 001_Architecture/Tools/Resource-Library-Visualizer TOOLBOX.md 007_Resource_Library/Directory.md tests/resource_library_visualizer
git commit -m "feat(rl-visualizer): docs + toolbox + e2e verification"
```

---

## Self-Review

**Spec coverage:**

| Spec section | Task |
|---|---|
| Local server, endpoints | 9 |
| Browser SPA | 10 |
| Co-location pairing (+ embed fallback) | 3 |
| Thumbnail cache | 4 |
| YouTube poster frames | 4, 10 |
| Card anatomy (3-line footer, pills, source label) | 10 |
| Source-label / vision-risk / glyph-color heuristics | 2 |
| Filters (folder / source / top-8 tags) + search | 9 (`/api/filters`), 10 |
| Default sort newest-first | 3 |
| Detail view Obsidian-style render | 5, 9, 10 |
| Delete → `~/Desktop/delete/` + card vanishes | 7, 9, 10 |
| Structured inline Edit | 7, 9, 10 |
| Re-run AI (+ cost confirm) | 8, 9, 10 |
| Add Comment | 6, 9, 10 |
| Review Queue file + Finalize | 6, 9, 10 |
| Text-only toggle + glyph cards | 3, 10 |
| Never delete / never commit / scope guard | Global Constraints, `_safe_abs`, `move_to_delete` |
| File layout | File Structure |

No gaps found.

**Placeholder scan:** One deliberate `TODO(wiring)` in Task 8 Step 4 — it is explicitly scoped in Task 8 Step 1 (inspect `process_image_ingest.py`, wire the confirmed function name, or fall back to the injectable path). The injectable `vision_fn` keeps every test and the server functional regardless. Acceptable and bounded.

**Type consistency:** Card dict keys are defined in Task 3 and consumed unchanged in Tasks 4/9/10. `rewrite_note(note_rel_path, fields)`, `move_to_delete(note_rel_path)`, `rerun_ai(note_rel_path, vision_fn)`, `add_comment(note_path, text)`, `log_delete(note_path)`, `finalize()`, `ensure_thumb`, `thumb_path_for`, `youtube_poster_url`, `render_body(body, note_rel_dir)`, `frontmatter_html(fm)` — all referenced with consistent names/arity across tasks and in `serve.py`.

## Notes for the executor

- Modules import their siblings by file path (`importlib`), not as a package, because the tool dir name (`Resource-Library-Visualizer`) has hyphens and isn't on `sys.path`. Tests do the same via `conftest.load`. Keep this pattern — do not add `__init__.py` to the tool dir or rename it.
- Run the whole suite (`python3 -m pytest tests/resource_library_visualizer/ -v`) at the end of every task, not just the task's own file.
- This is real-data software: after Task 11 testing, make sure no genuine library notes were lost to test deletes.
