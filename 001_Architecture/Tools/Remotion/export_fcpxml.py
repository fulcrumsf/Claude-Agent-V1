#!/usr/bin/env python3
"""
tools/export_fcpxml.py

Exports a Final Cut Pro XML (FCPXML 1.9) timeline.

TWO MODES
─────────
1. Legacy (no args) — hardcoded bioluminescence_weapon timeline:
     python3 tools/export_fcpxml.py

2. JSON-driven (new videos) — reads beat_sheet.json + auto-discovers clips:
     python3 tools/export_fcpxml.py --video-dir outputs/002_anomalous_wild/002_firefly_squid

   Expects inside <video-dir>:
     002_audio/beat_sheet.json   ← written by audio_tts.py
     001_scenes/<scene_id>/      ← video_looped.mp4 or image.png per scene variant
     (OR scene clips at <video-dir>/<scene_id>/ for old-style layout)

   Outputs:
     <video-dir>/<slug>.fcpxml   ← relative paths, portable folder

Media paths are always relative to the FCPXML file — move the entire
video folder and FCP / Premiere will resolve all media automatically.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from math import gcd

# ─── Config ───────────────────────────────────────────────────────────────────

FPS     = 30
VIDEO_W = 1920
VIDEO_H = 1080

OUT_DIR  = Path("outputs/001_anomalous_wild/bioluminescence_weapon")
OUT_FILE = OUT_DIR / "001_bioluminescence_weapon.fcpxml"

# ─── Types ────────────────────────────────────────────────────────────────────

@dataclass
class Clip:
    kind:      str           # "video" | "image" | "gap"
    name:      str
    cut_start: float         # seconds relative to scene start
    cut_end:   float
    file:      str | None    # relative path from OUT_DIR; None for gaps

@dataclass
class Scene:
    scene_id:   str
    start_s:    float        # absolute timeline start
    audio_file: str | None   # relative path from OUT_DIR
    audio_dur:  float
    clips:      list[Clip] = field(default_factory=list)

# ─── Time helper ──────────────────────────────────────────────────────────────

def ft(seconds: float) -> str:
    """Seconds → FCPXML rational time string (frame-accurate, 30fps base)."""
    frames = round(seconds * FPS)
    if frames == 0:
        return "0s"
    # 100/3000s per frame is the standard 30fps FCPXML timebase
    n, d = frames * 100, 3000
    g = gcd(n, d); n //= g; d //= g
    return f"{n}s" if d == 1 else f"{n}/{d}s"

# ─── Timeline constants (from BioluminescenceDoc.tsx) ─────────────────────────

_AUDIO_DUR: list[tuple[str, float]] = [
    ("scene_01", 14.0),
    ("scene_02",  3.0),   # TITLE_CARD_S — Remotion-only, no media
    ("scene_03", 19.8),
    ("scene_04", 21.2),
    ("scene_05", 40.2),
    ("scene_06", 36.7),
    ("scene_07", 53.4),
    ("scene_08", 54.8),
    ("scene_09", 48.2),
    ("scene_10", 49.1),
    ("scene_11", 67.7),
]

T: dict[str, float] = {}
_t = 0.0
for _k, _d in _AUDIO_DUR:
    T[_k] = _t
    _t += _d
TOTAL_DUR = _t      # 408.1 s

C3 = 49.1 / 3       # CLIP_THIRD_S ≈ 16.367 s

# ─── Scene definitions ────────────────────────────────────────────────────────

def v(name: str, a: float, b: float, f: str) -> Clip:
    return Clip("video", name, a, b, f)

def img(name: str, a: float, b: float, f: str) -> Clip:
    return Clip("image", name, a, b, f)

def gap(name: str, a: float, b: float) -> Clip:
    return Clip("gap", name, a, b, None)


SCENES: list[Scene] = [

    # ── SCENE 01 — Anglerfish Hook ──────────────────────────────────────────
    Scene("scene_01", T["scene_01"], "scene_01/audio.mp3", 14.0, [
        v("scene_01",  0,   5,   "scene_01/video_looped.mp4"),
        v("scene_01b", 5,  10,   "scene_01b/video_looped.mp4"),
        v("scene_01c", 10, 14,   "scene_01c/video_looped.mp4"),
    ]),

    # ── SCENE 02 — Remotion Title Card (no media) ────────────────────────────
    Scene("scene_02", T["scene_02"], None, 0.0, [
        gap("[Remotion] BioluminescenceTitleCard", 0, 3),
    ]),

    # ── SCENE 03 — Ocean Descent ─────────────────────────────────────────────
    Scene("scene_03", T["scene_03"], "scene_03/audio.mp3", 19.8, [
        v("scene_03b", 0,    4,   "scene_03b/video_looped.mp4"),
        v("scene_03c", 4,    8,   "scene_03c/video_looped.mp4"),
        v("scene_03",  8,   12,   "scene_03/video_looped.mp4"),
        v("scene_03d", 12,  16,   "scene_03d/video_looped.mp4"),
        v("scene_03e", 16,  19.8, "scene_03e/video_looped.mp4"),
    ]),

    # ── SCENE 04 — Dinoflagellates ───────────────────────────────────────────
    Scene("scene_04", T["scene_04"], "scene_04/audio.mp3", 21.2, [
        v("scene_04b", 0,    4,   "scene_04b/video_looped.mp4"),
        v("scene_04c", 4,    8,   "scene_04c/video_looped.mp4"),
        v("scene_04",  8,   13,   "scene_04/video_looped.mp4"),
        v("scene_04d", 13,  17,   "scene_04d/video_looped.mp4"),
        img("scene_04e", 17, 21.2, "scene_04e/image.png"),
    ]),

    # ── SCENE 05 — Luciferase Chemistry ─────────────────────────────────────
    Scene("scene_05", T["scene_05"], "scene_05/audio.mp3", 40.2, [
        v("scene_05b",    0,    5,   "scene_05b/video_looped.mp4"),
        v("scene_05c",    5,   10,   "scene_05c/video_looped.mp4"),
        v("scene_05",    10,   17,   "scene_05/video_looped.mp4"),
        img("scene_05e", 17,   25,   "scene_05e/image.png"),
        v("scene_05d",   25,   31,   "scene_05d/video_looped.mp4"),
        v("scene_05f",   31,   36,   "scene_05f/video_looped.mp4"),
        v("scene_05c_r", 36,   40.2, "scene_05c/video_looped.mp4"),   # reuse
    ]),

    # ── SCENE 06 — Phylogenetic Tree (Remotion + audio) ─────────────────────
    Scene("scene_06", T["scene_06"], "scene_06/audio.mp3", 36.7, [
        gap("[Remotion] PhylogeneticTree", 0, 36.7),
    ]),

    # ── SCENE 07 — Anglerfish Deep Dive ─────────────────────────────────────
    Scene("scene_07", T["scene_07"], "scene_07/audio.mp3", 53.4, [
        v("scene_07b",    0,    5,   "scene_07b/video_looped.mp4"),
        v("scene_07",     5,    9,   "scene_07/video_looped.mp4"),
        v("scene_07c",    9,   13,   "scene_07c/video_looped.mp4"),
        v("scene_07d",   13,   17,   "scene_07d/video_looped.mp4"),
        img("scene_07e", 17,   22,   "scene_07e/image.png"),
        v("scene_07f",   22,   27,   "scene_07f/video_looped.mp4"),
        v("scene_07g",   27,   31,   "scene_07g/video_looped.mp4"),
        v("scene_07h",   31,   36,   "scene_07h/video_looped.mp4"),
        v("scene_07i",   36,   41,   "scene_07i/video_looped.mp4"),
        v("scene_07j",   41,   46,   "scene_07j/video_looped.mp4"),
        img("scene_07k", 46,   50,   "scene_07k/image.png"),
        v("scene_07b_r", 50,   53.4, "scene_07b/video_looped.mp4"),   # reuse
    ]),

    # ── SCENE 08 — Bobtail Squid ─────────────────────────────────────────────
    Scene("scene_08", T["scene_08"], "scene_08/audio.mp3", 54.8, [
        v("scene_08b",    0,    5,   "scene_08b/video_looped.mp4"),
        v("scene_08",     5,   10,   "scene_08/video_looped.mp4"),
        v("scene_08c",   10,   15,   "scene_08c/video_looped.mp4"),
        v("scene_08d",   15,   20,   "scene_08d/video_looped.mp4"),
        img("scene_08h", 20,   26,   "scene_08h/image.png"),
        v("scene_08e",   26,   32,   "scene_08e/video_looped.mp4"),
        v("scene_08f",   32,   37,   "scene_08f/video_looped.mp4"),
        img("scene_08i", 37,   43,   "scene_08i/image.png"),
        v("scene_08g",   43,   48,   "scene_08g/video_looped.mp4"),
        v("scene_08e_r", 48,   54.8, "scene_08e/video_looped.mp4"),   # reuse
    ]),

    # ── SCENE 09 — Dragonfish ────────────────────────────────────────────────
    Scene("scene_09", T["scene_09"], "scene_09/audio.mp3", 48.2, [
        v("scene_09b",    0,    5,   "scene_09b/video_looped.mp4"),
        v("scene_09c",    5,    9,   "scene_09c/video_looped.mp4"),
        v("scene_09",     9,   14,   "scene_09/video_looped.mp4"),
        v("scene_09d",   14,   18,   "scene_09d/video_looped.mp4"),
        img("scene_09e", 18,   24,   "scene_09e/image.png"),
        img("scene_09f", 24,   30,   "scene_09f/image.png"),
        v("scene_09g",   30,   37,   "scene_09g/video_looped.mp4"),
        v("scene_09h",   37,   42,   "scene_09h/video_looped.mp4"),
        v("scene_09i",   42,   48.2, "scene_09i/video_looped.mp4"),
    ]),

    # ── SCENE 10 — Quick-cut triptych (10a / 10b / 10c) ─────────────────────
    # One audio track (scene_10a/audio.mp3) covers all 49.1s.
    Scene("scene_10", T["scene_10"], "scene_10a/audio.mp3", 49.1, [
        # 10a — Firefly Squid (0 → C3)
        v("scene_10a2", 0,           4.1,      "scene_10a2/video_looped.mp4"),
        v("scene_10a",  4.1,         8.2,      "scene_10a/video_looped.mp4"),
        v("scene_10a3", 8.2,         12.3,     "scene_10a3/video_looped.mp4"),
        v("scene_10a4", 12.3,        C3,       "scene_10a4/video_looped.mp4"),
        # 10b — Siphonophore (C3 → C3*2)
        v("scene_10b",  C3,          C3+4.1,   "scene_10b/video_looped.mp4"),
        v("scene_10b2", C3+4.1,      C3+8.2,   "scene_10b2/video_looped.mp4"),
        v("scene_10b3", C3+8.2,      C3+12.3,  "scene_10b3/video_looped.mp4"),
        v("scene_10b4", C3+12.3,     C3*2,     "scene_10b4/video_looped.mp4"),
        # 10c — Jellyfish Decoy (C3*2 → 49.1)
        v("scene_10c2", C3*2,        C3*2+4.1, "scene_10c2/video_looped.mp4"),
        v("scene_10c3", C3*2+4.1,    C3*2+8.2, "scene_10c3/video_looped.mp4"),
        v("scene_10c",  C3*2+8.2,    C3*2+12.3,"scene_10c/video_looped.mp4"),
        v("scene_10c4", C3*2+12.3,   49.1,     "scene_10c4/video_looped.mp4"),
    ]),

    # ── SCENE 11 — Convergent Evolution / Europa ─────────────────────────────
    Scene("scene_11", T["scene_11"], "scene_11/audio.mp3", 67.7, [
        v("scene_11b",    0,    5,   "scene_11b/video_looped.mp4"),
        v("scene_11c",    5,   10,   "scene_11c/video_looped.mp4"),
        v("scene_11d",   10,   15,   "scene_11d/video_looped.mp4"),
        v("scene_11e",   15,   20,   "scene_11e/video_looped.mp4"),
        v("scene_11f",   20,   28,   "scene_11f/video_looped.mp4"),
        v("scene_11g",   28,   35,   "scene_11g/video_looped.mp4"),
        v("scene_11h",   35,   43,   "scene_11h/video_looped.mp4"),
        v("scene_11",    43,   50,   "scene_11/video_looped.mp4"),
        img("scene_11i", 50,   56,   "scene_11i/image.png"),
        img("scene_11j", 56,   61,   "scene_11j/image.png"),
        img("scene_11k", 61,   66,   "scene_11k/image.png"),
        v("scene_11m",   66,   67.7, "scene_11m/video_looped.mp4"),
    ]),
]

# ─── Asset registry ───────────────────────────────────────────────────────────

def collect_assets() -> tuple[dict[str, str], list[tuple[str, str, str]]]:
    """
    Walk all scenes and return:
      file_to_id  : { file_rel_path: asset_id }
      asset_list  : [ (asset_id, file_rel_path, kind) ]  kind = video|image|audio
    Assets are de-duplicated; first occurrence wins.
    """
    seen: dict[str, str] = {}
    ordered: list[tuple[str, str, str]] = []
    counter = [2]  # r1 is the format; use list so inner func can mutate

    def register(file_rel: str, kind: str) -> str:
        if file_rel not in seen:
            aid = f"r{counter[0]}"; counter[0] += 1
            seen[file_rel] = aid
            ordered.append((aid, file_rel, kind))
        return seen[file_rel]

    for sc in SCENES:
        for clip in sc.clips:
            frel = clip.file
            if frel is not None:
                k = "image" if frel.endswith(".png") else "video"
                register(frel, k)
        af = sc.audio_file
        if af is not None:
            register(af, "audio")

    return seen, ordered

# ─── FCPXML builder ───────────────────────────────────────────────────────────

def build_fcpxml() -> str:
    file_to_id, asset_list = collect_assets()
    lines: list[str] = []

    # ── Prolog ──────────────────────────────────────────────────────────────
    lines += [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!DOCTYPE fcpxml>',
        '<fcpxml version="1.9">',
        '',
    ]

    # ── Resources ───────────────────────────────────────────────────────────
    lines += [
        '  <resources>',
        f'    <format id="r1" name="FFVideoFormat1080p30" frameDuration="100/3000s"'
        f' width="{VIDEO_W}" height="{VIDEO_H}" colorSpace="1-1-1 (Rec. 709)"/>',
        '',
    ]

    for (aid, frel, kind) in asset_list:
        name = Path(frel).parent.name + ("_audio" if kind == "audio" else "")
        src  = f"./{frel}"
        if kind == "audio":
            lines.append(
                f'    <asset id="{aid}" name="{name}" src="{src}"'
                f' start="0s" duration="999s" hasVideo="0" hasAudio="1"'
                f' audioSources="1" audioChannels="2" audioRate="44100">'
            )
        elif kind == "image":
            lines.append(
                f'    <asset id="{aid}" name="{name}" src="{src}"'
                f' start="0s" duration="999s" hasVideo="1" hasAudio="0">'
            )
        else:
            lines.append(
                f'    <asset id="{aid}" name="{name}" src="{src}"'
                f' start="0s" duration="999s" hasVideo="1" hasAudio="0" format="r1">'
            )
        lines.append(f'      <media-rep kind="original-media" src="{src}"/>')
        lines.append(f'    </asset>')

    lines += ['  </resources>', '']

    # ── Library / Event / Project ────────────────────────────────────────────
    lines += [
        '  <library location=".">',
        '    <event name="Bioluminescence Weapon">',
        '      <project name="001_bioluminescence_weapon">',
        f'        <sequence format="r1" duration="{ft(TOTAL_DUR)}"'
        f' tcStart="0s" tcFormat="NDF" audioLayout="stereo" audioRate="48k">',
        '          <spine>',
        '',
    ]

    # ── Spine ────────────────────────────────────────────────────────────────
    for sc in SCENES:
        lines.append(f'            <!-- ── {sc.scene_id.upper()} ── -->')

        for idx, clip in enumerate(sc.clips):
            abs_start = sc.start_s + clip.cut_start
            clip_dur  = clip.cut_end - clip.cut_start
            is_first  = (idx == 0)

            audio_file = sc.audio_file
            if clip.kind == "gap":
                open_tag = (
                    f'            <gap name="{clip.name}"'
                    f' offset="{ft(abs_start)}" duration="{ft(clip_dur)}"'
                )
                if is_first and audio_file is not None:
                    aud_id = file_to_id[audio_file]
                    lines.append(open_tag + ">")
                    lines.append(
                        f'              <asset-clip ref="{aud_id}" lane="-1"'
                        f' offset="0s" duration="{ft(sc.audio_dur)}"'
                        f' start="0s" name="{sc.scene_id}_audio" audioRole="dialogue"/>'
                    )
                    lines.append("            </gap>")
                else:
                    lines.append(open_tag + "/>")

            else:
                frel   = clip.file
                assert frel is not None
                vid_id = file_to_id[frel]
                open_tag = (
                    f'            <asset-clip ref="{vid_id}" name="{clip.name}"'
                    f' offset="{ft(abs_start)}" duration="{ft(clip_dur)}" start="0s"'
                )
                if is_first and audio_file is not None:
                    aud_id = file_to_id[audio_file]
                    lines.append(open_tag + ">")
                    lines.append(
                        f'              <asset-clip ref="{aud_id}" lane="-1"'
                        f' offset="0s" duration="{ft(sc.audio_dur)}"'
                        f' start="0s" name="{sc.scene_id}_audio" audioRole="dialogue"/>'
                    )
                    lines.append("            </asset-clip>")
                else:
                    lines.append(open_tag + "/>")

        lines.append("")

    lines += [
        '          </spine>',
        '        </sequence>',
        '      </project>',
        '    </event>',
        '  </library>',
        '',
        '</fcpxml>',
    ]

    return "\n".join(lines)

# ─── JSON-driven builder (new videos) ────────────────────────────────────────

def _find_scene_clips(video_dir: Path, scene_id: str) -> list[tuple[str, str]]:
    """
    Discover clip files for a scene_id and its lettered variants
    (scene_01, scene_01b, scene_01c, ...).

    Looks in:
      <video_dir>/001_scenes/<scene_id>/   (new folder structure)
      <video_dir>/<scene_id>/              (legacy flat structure)

    Returns list of (clip_name, rel_path_from_video_dir) sorted alphabetically.
    rel_path uses forward slashes for FCPXML compatibility.
    """
    clips = []
    for base in (video_dir / "001_scenes", video_dir):
        if not base.exists():
            continue
        # Collect all subdirs that match scene_id + optional letter suffix
        for subdir in sorted(base.iterdir()):
            if not subdir.is_dir():
                continue
            name = subdir.name
            # Must exactly match scene_id or scene_id + single lowercase letter
            if name == scene_id or (
                name.startswith(scene_id) and
                len(name) == len(scene_id) + 1 and
                name[-1].isalpha() and name[-1].islower()
            ):
                for candidate in ("video_looped.mp4", "video.mp4", "image.png"):
                    fpath = subdir / candidate
                    if fpath.exists():
                        rel = str(fpath.relative_to(video_dir)).replace("\\", "/")
                        clips.append((name, rel))
                        break
    return clips


def scenes_from_beat_sheet(video_dir: Path) -> tuple[list[Scene], float]:
    """
    Build Scene objects from beat_sheet.json + auto-discovered clip files.

    Searches for beat_sheet.json in:
      <video_dir>/002_audio/beat_sheet.json   (new structure)
      <video_dir>/003_docs/beat_sheet.json    (alt location)
      <video_dir>/beat_sheet.json             (legacy flat)
    """
    beat_sheet_path: Path | None = None
    for candidate in (
        video_dir / "002_audio" / "beat_sheet.json",
        video_dir / "003_docs"  / "beat_sheet.json",
        video_dir / "beat_sheet.json",
    ):
        if candidate.exists():
            beat_sheet_path = candidate
            break

    if beat_sheet_path is None:
        raise FileNotFoundError(
            f"beat_sheet.json not found in {video_dir}.\n"
            f"Run: python3 tools/audio_tts.py <script.md> {video_dir}/002_audio"
        )
    assert beat_sheet_path is not None  # narrow for type checker

    beat_sheet = json.loads(beat_sheet_path.read_text(encoding="utf-8"))
    scenes: list[Scene] = []
    cumulative = 0.0

    for entry in beat_sheet:
        scene_id  = entry["scene_id"]
        duration  = float(entry.get("duration_s", 0.0))
        audio_rel = entry.get("audio_file")  # relative to 002_audio/

        # Resolve audio path relative to video_dir
        audio_file: str | None = None
        if audio_rel:
            # beat_sheet.json stores paths relative to the audio_dir
            audio_dir_candidates = [
                video_dir / "002_audio" / audio_rel,
                video_dir / audio_rel,
            ]
            for apath in audio_dir_candidates:
                if apath.exists():
                    audio_file = str(apath.relative_to(video_dir)).replace("\\", "/")
                    break

        # Discover clips for this scene
        raw_clips = _find_scene_clips(video_dir, scene_id)
        clips: list[Clip] = []

        if raw_clips:
            seg_dur = duration / len(raw_clips)
            for i, (clip_name, rel) in enumerate(raw_clips):
                cut_s = round(i * seg_dur, 3)           # type: ignore[call-overload]
                cut_e = round((i + 1) * seg_dur, 3) if i < len(raw_clips) - 1 else duration  # type: ignore[call-overload]
                kind  = "image" if rel.endswith(".png") else "video"
                clips.append(Clip(kind, clip_name, cut_s, cut_e, rel))
        else:
            # No clips found — insert a gap placeholder
            clips.append(Clip("gap", f"[no media] {scene_id}", 0, duration, None))
            print(f"  ⚠ No clips found for {scene_id} — inserted gap")

        scenes.append(Scene(scene_id, cumulative, audio_file, duration, clips))
        cumulative += duration

    return scenes, cumulative


def export_from_dir(video_dir: Path) -> None:
    """JSON-driven export for a new-style video folder."""
    video_dir = video_dir.resolve()
    if not video_dir.exists():
        print(f"Error: video directory not found: {video_dir}")
        return

    print(f"Building FCPXML from: {video_dir}")
    scenes, total_dur = scenes_from_beat_sheet(video_dir)

    slug     = video_dir.name
    out_file = video_dir / f"{slug}.fcpxml"

    # Temporarily swap the global SCENES list for the builder
    original_scenes = list(SCENES)
    SCENES.clear()
    SCENES.extend(scenes)

    try:
        xml = build_fcpxml_dynamic(scenes, total_dur)
    finally:
        SCENES.clear()
        SCENES.extend(original_scenes)

    out_file.write_text(xml, encoding="utf-8")
    total_clips = sum(len(sc.clips) for sc in scenes)
    total_audio = sum(1 for sc in scenes if sc.audio_file)
    size_kb     = out_file.stat().st_size / 1024

    print(f"✓ FCPXML written: {out_file}")
    print(f"  Total duration    : {total_dur:.1f}s  ({total_dur/60:.1f} min)")
    print(f"  Scenes            : {len(scenes)}")
    print(f"  Video/image clips : {total_clips}")
    print(f"  Audio tracks      : {total_audio}")
    print(f"  File size         : {size_kb:.1f} KB")


def build_fcpxml_dynamic(scenes: list[Scene], total_dur: float) -> str:
    """Build FCPXML XML string from an explicit scenes list + total duration."""
    # Collect assets
    seen = {}
    ordered = []
    counter = [2]

    def register(file_rel: str, kind: str) -> str:
        if file_rel not in seen:
            aid = f"r{counter[0]}"; counter[0] += 1
            seen[file_rel] = aid
            ordered.append((aid, file_rel, kind))
        return seen[file_rel]

    for sc in scenes:
        for clip in sc.clips:
            if clip.file is not None:
                k = "image" if clip.file.endswith(".png") else "video"
                register(clip.file, k)
        if sc.audio_file is not None:
            register(sc.audio_file, "audio")

    lines: list[str] = []
    lines += [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!DOCTYPE fcpxml>',
        '<fcpxml version="1.9">',
        '',
        '  <resources>',
        f'    <format id="r1" name="FFVideoFormat1080p30" frameDuration="100/3000s"'
        f' width="{VIDEO_W}" height="{VIDEO_H}" colorSpace="1-1-1 (Rec. 709)"/>',
        '',
    ]

    for (aid, frel, kind) in ordered:
        name = Path(frel).parent.name + ("_audio" if kind == "audio" else "")
        src  = f"./{frel}"
        if kind == "audio":
            lines.append(
                f'    <asset id="{aid}" name="{name}" src="{src}"'
                f' start="0s" duration="999s" hasVideo="0" hasAudio="1"'
                f' audioSources="1" audioChannels="2" audioRate="44100">'
            )
        elif kind == "image":
            lines.append(
                f'    <asset id="{aid}" name="{name}" src="{src}"'
                f' start="0s" duration="999s" hasVideo="1" hasAudio="0">'
            )
        else:
            lines.append(
                f'    <asset id="{aid}" name="{name}" src="{src}"'
                f' start="0s" duration="999s" hasVideo="1" hasAudio="0" format="r1">'
            )
        lines.append(f'      <media-rep kind="original-media" src="{src}"/>')
        lines.append(f'    </asset>')

    project_name = "exported_video"
    lines += [
        '  </resources>',
        '',
        '  <library location=".">',
        f'    <event name="{project_name}">',
        f'      <project name="{project_name}">',
        f'        <sequence format="r1" duration="{ft(total_dur)}"'
        f' tcStart="0s" tcFormat="NDF" audioLayout="stereo" audioRate="48k">',
        '          <spine>',
        '',
    ]

    for sc in scenes:
        lines.append(f'            <!-- ── {sc.scene_id.upper()} ── -->')
        for idx, clip in enumerate(sc.clips):
            abs_start = sc.start_s + clip.cut_start
            clip_dur  = clip.cut_end - clip.cut_start
            is_first  = (idx == 0)
            audio_file = sc.audio_file

            if clip.kind == "gap":
                open_tag = (
                    f'            <gap name="{clip.name}"'
                    f' offset="{ft(abs_start)}" duration="{ft(clip_dur)}"'
                )
                if is_first and audio_file is not None:
                    aud_id = seen[audio_file]
                    lines.append(open_tag + ">")
                    lines.append(
                        f'              <asset-clip ref="{aud_id}" lane="-1"'
                        f' offset="0s" duration="{ft(sc.audio_dur)}"'
                        f' start="0s" name="{sc.scene_id}_audio" audioRole="dialogue"/>'
                    )
                    lines.append("            </gap>")
                else:
                    lines.append(open_tag + "/>")
            else:
                frel   = clip.file
                assert frel is not None
                vid_id = seen[frel]
                open_tag = (
                    f'            <asset-clip ref="{vid_id}" name="{clip.name}"'
                    f' offset="{ft(abs_start)}" duration="{ft(clip_dur)}" start="0s"'
                )
                if is_first and audio_file is not None:
                    aud_id = seen[audio_file]
                    lines.append(open_tag + ">")
                    lines.append(
                        f'              <asset-clip ref="{aud_id}" lane="-1"'
                        f' offset="0s" duration="{ft(sc.audio_dur)}"'
                        f' start="0s" name="{sc.scene_id}_audio" audioRole="dialogue"/>'
                    )
                    lines.append("            </asset-clip>")
                else:
                    lines.append(open_tag + "/>")
        lines.append("")

    lines += [
        '          </spine>',
        '        </sequence>',
        '      </project>',
        '    </event>',
        '  </library>',
        '',
        '</fcpxml>',
    ]
    return "\n".join(lines)


# ─── Main ─────────────────────────────────────────────────────────────────────

import json  # needed by scenes_from_beat_sheet


def main() -> None:
    import sys

    if "--video-dir" in sys.argv:
        idx = sys.argv.index("--video-dir")
        video_dir = Path(sys.argv[idx + 1])
        export_from_dir(video_dir)
        return

    # Legacy: hardcoded bioluminescence_weapon timeline
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    xml = build_fcpxml()
    OUT_FILE.write_text(xml, encoding="utf-8")

    total_clips = sum(len(sc.clips) for sc in SCENES)
    total_audio = sum(1 for sc in SCENES if sc.audio_file)
    size_kb     = OUT_FILE.stat().st_size / 1024

    print(f"FCPXML written: {OUT_FILE}")
    print(f"  Total duration    : {TOTAL_DUR:.1f}s  ({TOTAL_DUR/60:.1f} min)")
    print(f"  Video/image clips : {total_clips}")
    print(f"  Audio tracks      : {total_audio}")
    print(f"  File size         : {size_kb:.1f} KB")
    print()
    print("Import into Adobe Premiere Pro:")
    print("  File → Import → select 001_bioluminescence_weapon.fcpxml")
    print("  If media paths break after moving the folder, Premiere will")
    print("  prompt to locate. Point it at the bioluminescence_weapon/ folder")
    print("  and all clips relink automatically (same relative structure).")


if __name__ == "__main__":
    main()
