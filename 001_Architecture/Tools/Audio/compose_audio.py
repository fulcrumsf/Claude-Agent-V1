#!/usr/bin/env python3
"""
compose_audio.py — Vision-based per-scene audio composer for Reimagined Realms productions.

Reads:
  Data/Beatmap.json                    per-clip timing (acts, clips, durations)
  Assembly/gemini_scene_analysis.md    second-by-second visual scene descriptions
  Scripts/Narration.md                 narration sections (VO duck flagging)
  Assembly/Frames/                     1fps JPGs (used with --reanalyze for fresh Gemini pass)

Outputs:
  Data/audio_briefs.json               human-readable per-scene audio brief per clip
  Data/per_scene_stem_map.json         per-clip stem map compatible with generate_stems.py
  Data/fcpxml_placement.json           FCPXML-ready timing structure for Premiere / FCP

Usage:
  python3 compose_audio.py <production_folder>
  python3 compose_audio.py <production_folder> --reanalyze   # sends frames to Gemini for fresh analysis
  python3 compose_audio.py <production_folder> --dry-run     # print briefs without writing files
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Scene classification → audio design rules
# ---------------------------------------------------------------------------

# Maps Beatmap act labels to scene class
ACT_TO_CLASS = {
    "Hook":             "Establishing",
    "Rising Crisis":    "RisingAction",
    "Peak Crisis":      "PeakTension",
    "Climax":           "Climax",
    "Resolution":       "Resolution",
    "Outro + CTA":      "Outro",
    "Outro":            "Outro",
}

# Per-class audio design defaults
SCENE_CLASS_DEFAULTS = {
    "Establishing": {
        "music_texture": "soft melodic underscore, single sustained tone",
        "volume": 0.8,
        "has_music_duck": True,
    },
    "RisingAction": {
        "music_texture": "low riser + percussive undercurrent",
        "volume": 0.75,
        "has_music_duck": True,
    },
    "PeakTension": {
        "music_texture": "high riser landing to impact hit",
        "volume": 0.9,
        "has_music_duck": False,
    },
    "Climax": {
        "music_texture": "harmonic swell, emotional score",
        "volume": 0.7,
        "has_music_duck": True,
    },
    "Resolution": {
        "music_texture": "gentle melodic resolution, warm texture",
        "volume": 0.65,
        "has_music_duck": True,
    },
    "Outro": {
        "music_texture": "fade to near-silence, ambient only",
        "volume": 0.5,
        "has_music_duck": True,
    },
}

# Fade curve applied to all clips — hsin = half-sine = S-curve (ease-in/ease-out bezier)
FADE_CURVE = "hsin"


def crossfade_s_for_duration(duration_s: float) -> float:
    """Crossfade duration proportional to clip length. Longer clips = longer blend."""
    if duration_s < 5.0:
        return 0.5
    if duration_s < 10.0:
        return 1.0
    return 1.5

# Hardcoded per-clip SFX prompts derived from Gemini scene analysis
# Keyed by clip ID. Any clip without an entry falls back to class defaults.
CLIP_SFX_PROMPTS = {
    "C1":  "ancient Roman city ambience from above, distant crowd hum and marketplace murmur, merchants calling, lively city energy, warm golden morning air, birds in the background",
    "C2":  "abrupt cut to near-silence, low mournful wind blowing across empty ruins, fine ash and dust skittering across cobblestones, haunting desolation",
    "C3":  "eerie wind whistling through ancient stone ruins at sunset, loose pebbles rolling on cobblestones, lonely echo, melancholic emptiness",
    "C4":  "muted dusty interior room tone, gentle wind coming through a cracked stone window, soft sound of dust settling, the feeling of frozen time",
    "C5":  "deep powerful volcanic rumble growing beneath the earth, gentle Mediterranean sea waves, distant panicked crowd murmur starting, creaking wooden boat hulls, oars splashing",
    "C6":  "close volcanic roar, percussive rain of small volcanic rocks and lapilli hitting cobblestone streets and terracotta rooftops, panicked crowd gasps and screams",
    "C7":  "persistent deep volcanic rumble as background, urgent hurrying footsteps on stone cobblestones, heavy labored breathing, wind carrying ash and debris",
    "C8":  "mass exodus cacophony on cobblestone roads, dozens of hurrying footsteps, horse hooves clattering rhythmically, wooden cart wheels rumbling and squeaking, donkeys braying, harness jingling, shouting voices, volcanic bass rumble underneath",
    "C9":  "mournful howling wind sweeping through empty desolate cobblestone streets, faint distant clinking of abandoned pottery moved by the wind, the haunting quiet after catastrophe",
    "C10": "deafening volcanic eruption at full intensity, massive explosive booms, sharp cracks of volcanic lightning, hiss and roar of lava rivers, apocalyptic natural power, overwhelming and visceral",
    "C11": "immense pyroclastic surge, continuous jet-engine roar of superheated gas and ash at tremendous speed, crackling fire, cracking and splintering of buildings being obliterated, unstoppable wall of destruction",
    "C12": "vast empty wind blowing across a landscape buried under volcanic ash, immense desolate moan, the profound silence of death, low haunting gusts over emptiness",
    "C13": "exhausted ash-covered survivors shuffling slowly through debris, footsteps heavy in deep ash, labored pained breathing, weak coughing, low somber wind",
    "C14": "near silence, muted ambient sounds, faint footsteps in the background, cold wind whistling slowly around massive stone columns, a quiet stifled sob in the distance",
    "C15": "ethereal low drone, slowed muffled footsteps and cloth rustle, surreal dreamlike quality, shell-shocked and heavy, as if time itself has slowed",
    "C16": "quiet indoor room tone, gentle sunlight atmosphere, very faint distant breeze, subtle creak of ancient wood, contemplative scholarly stillness",
    "C17": "near complete silence, very subtle museum room tone, a single low sustained somber musical note barely audible, profound respectful quiet around the dead",
    "C18": "gentle warm evening breeze through ancient stone ruins, crickets beginning to chirp at dusk, faint gravel texture underfoot, peaceful and timeless",
    "C19": "slow wind brushing across a weathered stone wall, ancient and still, quiet reverence, the sound of centuries passing",
    "C20": "gentle Mediterranean water lapping, low hum of a distant modern motorboat, faint seabird call, serene contemporary peace",
    "C21": "quiet night ambience, soft cricket chorus, a very gentle low wind, eternal peaceful silence under the stars",
}


# ---------------------------------------------------------------------------
# Gemini scene analysis parser
# ---------------------------------------------------------------------------

def parse_gemini_analysis(md_text: str) -> dict[str, dict]:
    """Parse gemini_scene_analysis.md into {start_s: {end_s, emotional_tone, natural_sounds, description}}."""
    scenes = {}
    block_pattern = re.compile(
        r"\*\*\[(\d+):(\d+)[–\-](\d+):(\d+)\]\*\*.*?"
        r"(?:\*\*Emotional tone:\*\*\s*(.+?))?(?:\n|$)"
        r"(?:.*?\*\*Natural sounds:\*\*\s*(.+?))?(?:\n\n|\Z)",
        re.DOTALL,
    )
    for m in block_pattern.finditer(md_text):
        try:
            start_s = int(m.group(1)) * 60 + int(m.group(2))
            end_s   = int(m.group(3)) * 60 + int(m.group(4))
            scenes[start_s] = {
                "end_s": end_s,
                "emotional_tone": (m.group(5) or "").strip(),
                "natural_sounds": (m.group(6) or "").strip(),
            }
        except Exception:
            pass
    return scenes


def find_scene_for_clip(start_s: float, end_s: float, scenes: dict) -> dict:
    """Return the gemini scene entry whose range overlaps most with [start_s, end_s]."""
    best = {}
    best_overlap = 0.0
    for sc_start, sc in scenes.items():
        sc_end = sc["end_s"]
        overlap = min(end_s, sc_end) - max(start_s, sc_start)
        if overlap > best_overlap:
            best_overlap = overlap
            best = sc
    return best


# ---------------------------------------------------------------------------
# Narration section parser
# ---------------------------------------------------------------------------

def parse_narration_sections(md_text: str) -> list[str]:
    """Return list of narration section headers (e.g. ['01 Hook', '02 Rising Crisis', ...])."""
    return re.findall(r"^##\s+(.+)$", md_text, re.MULTILINE)


def narration_section_for_act(act_label: str, narration_sections: list[str]) -> str:
    """Map act label to the closest narration section name."""
    label_lower = act_label.lower()
    for section in narration_sections:
        if any(word in section.lower() for word in label_lower.split()):
            return section
    return narration_sections[0] if narration_sections else ""


# ---------------------------------------------------------------------------
# Reanalyze via Gemini (optional)
# ---------------------------------------------------------------------------

def load_gemini_api_key() -> str:
    result = subprocess.run(
        "source ~/.env-secrets && echo $GEMINI_API_KEY",
        shell=True, executable="/bin/zsh", capture_output=True, text=True,
    )
    key = result.stdout.strip()
    if key:
        os.environ["GEMINI_API_KEY"] = key
    return os.environ.get("GEMINI_API_KEY", "")


def reanalyze_with_gemini(frames_dir: Path, _production_root: Path) -> str:
    """Send 1fps frames to Gemini and return updated scene analysis markdown."""
    try:
        import google.generativeai as genai
    except ImportError:
        sys.exit("ERROR: google-generativeai not installed. Run: pip install google-generativeai")

    api_key = load_gemini_api_key()
    if not api_key:
        sys.exit("ERROR: GEMINI_API_KEY not found in ~/.env-secrets")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    frame_paths = sorted(frames_dir.glob("frame_*.jpg"))
    if not frame_paths:
        sys.exit(f"ERROR: No frames found in {frames_dir}")

    print(f"  Sending {len(frame_paths)} frames to Gemini for analysis...", flush=True)

    parts = []
    for i, fp in enumerate(frame_paths):
        parts.append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": fp.read_bytes(),
            }
        })
        parts.append(f"[Frame at {i}s]")

    parts.append(
        "You are an audio composer's assistant. For each frame above (1 per second), "
        "provide a second-by-second scene description formatted as:\n\n"
        "**[M:SS–M:SS]**\n"
        "- **In frame:** ...\n"
        "- **Emotional tone:** ...\n"
        "- **Natural sounds:** ...\n\n"
        "Group consecutive seconds with the same visual scene into one block. "
        "Focus on what an audio composer needs: emotional tone, natural sound sources, "
        "ambience characteristics, and any significant visual transitions."
    )

    response = model.generate_content(parts)
    return response.text


# ---------------------------------------------------------------------------
# Audio brief builder
# ---------------------------------------------------------------------------

def build_audio_brief(
    clip_id: str,
    act_label: str,
    start_s: float,
    end_s: float,
    scene: dict,
    narration_section: str,
) -> dict:
    scene_class = ACT_TO_CLASS.get(act_label, "Establishing")
    defaults = SCENE_CLASS_DEFAULTS[scene_class]
    duration_s = round(end_s - start_s, 3)
    xfade_s = crossfade_s_for_duration(duration_s)

    # Use hardcoded per-clip prompt if available, otherwise fall back to natural_sounds from Gemini
    sfx_prompt = CLIP_SFX_PROMPTS.get(
        clip_id,
        scene.get("natural_sounds", f"{act_label.lower()} ambience and atmosphere"),
    )

    return {
        "clip_id": clip_id,
        "act": act_label,
        "scene_class": scene_class,
        "in_s": start_s,
        "out_s": end_s,
        "duration_s": duration_s,
        # crossfade_s: how much this clip bleeds past out_s into the next clip
        # ElevenLabs generates (duration_s + crossfade_s) so there's real audio to fade from
        "crossfade_s": xfade_s,
        "fade_in_s": xfade_s,
        "fade_out_s": xfade_s,
        "fade_curve": FADE_CURVE,
        "narration_section": narration_section,
        "has_narration": True,
        "music_texture": defaults["music_texture"],
        "has_music_duck": defaults["has_music_duck"],
        "sfx_prompt": sfx_prompt,
        "emotional_tone": scene.get("emotional_tone", ""),
        "volume": defaults["volume"],
    }


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------

def build_per_scene_stem_map(production: str, briefs: list[dict], total_duration_s: float) -> dict:
    """Convert audio briefs to generate_stems.py-compatible stem map.

    out_s is extended by crossfade_s so ElevenLabs generates the extra tail
    audio needed for the S-curve fade to blend into the next clip.
    """
    stems = []
    for b in briefs:
        stems.append({
            "id": b["clip_id"].lower(),
            "label": f"{b['clip_id']} — {b['act']}",
            "description": b["emotional_tone"] or b["act"],
            "prompt": b["sfx_prompt"],
            "in_s": b["in_s"],
            # Extend past video boundary so there's real audio to fade out from
            "out_s": round(b["out_s"] + b["crossfade_s"], 3),
            "fade_in_s": b["fade_in_s"],
            "fade_out_s": b["fade_out_s"],
            "fade_curve": b["fade_curve"],
            "volume": b["volume"],
            "scene_class": b["scene_class"],
            "has_music_duck": b["has_music_duck"],
        })
    return {
        "production": production,
        "source": "compose_audio.py (vision-based per-scene)",
        "note": "Per-clip stems — one SFX clip per video clip. out_s extended by crossfade_s for S-curve bleed.",
        "total_duration_s": total_duration_s,
        "total_clips": len(stems),
        "stems": stems,
    }


def build_fcpxml_placement(production: str, briefs: list[dict], fps: float = 25.0) -> dict:
    """Build FCPXML-ready placement data. Each audio clip placed on its own lane."""
    LANE_MAP = {
        "Establishing": 1,
        "RisingAction": 2,
        "PeakTension": 3,
        "Climax": 3,
        "Resolution": 1,
        "Outro": 1,
    }

    clips = []
    for b in briefs:
        start_frame = round(b["in_s"] * fps)
        dur_frames   = round(b["duration_s"] * fps)
        clips.append({
            "clip_id":    b["clip_id"],
            "asset_file": f"Audio_Stems/{b['clip_id'].lower()}.mp3",
            "lane":       LANE_MAP.get(b["scene_class"], 1),
            "offset_s":   b["in_s"],
            "offset_frames": start_frame,
            "duration_s":    b["duration_s"],
            "duration_frames": dur_frames,
            "fade_in_s":  b["fade_in_s"],
            "fade_out_s": b["fade_out_s"],
            "volume_db":  round(20 * __import__("math").log10(b["volume"]), 1),
            "has_music_duck": b["has_music_duck"],
            "scene_class": b["scene_class"],
        })

    return {
        "production": production,
        "fps": fps,
        "total_clips": len(clips),
        "audio_tracks": {
            "1": "Ambience / Establishing / Resolution",
            "2": "Rising Action / Tension Build",
            "3": "Peak Tension / Impact",
        },
        "clips": clips,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Compose per-scene audio briefs for video productions")
    parser.add_argument("production_folder", help="Path to production folder")
    parser.add_argument("--reanalyze", action="store_true",
                        help="Re-run Gemini vision analysis on Assembly/Frames/ instead of using cached analysis")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print briefs to stdout without writing output files")
    args = parser.parse_args()

    production_root = Path(args.production_folder).resolve()
    if not production_root.exists():
        sys.exit(f"ERROR: Folder not found: {production_root}")

    # --- Load Beatmap ---
    beatmap_path = production_root / "Data" / "Beatmap.json"
    if not beatmap_path.exists():
        sys.exit(f"ERROR: Beatmap.json not found at {beatmap_path}")
    beatmap = json.loads(beatmap_path.read_text())
    production_name = beatmap.get("topic", production_root.name)

    # --- Load / generate scene analysis ---
    analysis_path = production_root / "Assembly" / "gemini_scene_analysis.md"
    frames_dir    = production_root / "Assembly" / "Frames"

    if args.reanalyze:
        if not frames_dir.exists():
            sys.exit(f"ERROR: Frames directory not found: {frames_dir}\nRun: ffmpeg -i raw_video.mp4 -vf fps=1 Frames/frame_%04d.jpg")
        print("\n=== Reanalyzing frames with Gemini... ===", flush=True)
        analysis_md = reanalyze_with_gemini(frames_dir, production_root)
        analysis_path.write_text(analysis_md)
        print(f"  ✓ Saved fresh analysis → {analysis_path.name}", flush=True)
    else:
        if not analysis_path.exists():
            sys.exit(
                f"ERROR: {analysis_path.name} not found.\n"
                "Run with --reanalyze to generate it, or ensure Gemini analysis was run in a prior phase."
            )
        analysis_md = analysis_path.read_text()

    # --- Load Narration ---
    narration_path = production_root / "Scripts" / "Narration.md"
    narration_sections = []
    if narration_path.exists():
        narration_sections = parse_narration_sections(narration_path.read_text())

    # --- Parse scene analysis ---
    scenes = parse_gemini_analysis(analysis_md)

    # --- Build per-clip audio briefs ---
    briefs = []
    for act in beatmap["acts"]:
        act_label = act["label"]
        narration_section = narration_section_for_act(act_label, narration_sections)
        for sub in act["sub_beats"]:
            clip_id  = sub["clip"]
            start_s  = round(sub["start_ms"] / 1000, 3)
            end_s    = round(sub["end_ms"]   / 1000, 3)
            scene    = find_scene_for_clip(start_s, end_s, scenes)
            brief    = build_audio_brief(clip_id, act_label, start_s, end_s, scene, narration_section)
            briefs.append(brief)

    # --- Print summary ---
    print(f"\n=== Audio Composer — {production_name} | {len(briefs)} clips ===\n")
    for b in briefs:
        duck = " [DUCK]" if b["has_music_duck"] else ""
        print(f"  {b['clip_id']:4s}  {b['in_s']:6.2f}s–{b['out_s']:6.2f}s  "
              f"{b['scene_class']:14s}  vol={b['volume']:.2f}{duck}")
        print(f"       SFX: {b['sfx_prompt'][:90]}...")
        print()

    if args.dry_run:
        print("=== Dry run — no files written ===")
        return

    # --- Write outputs ---
    data_dir = production_root / "Data"
    data_dir.mkdir(exist_ok=True)

    briefs_path = data_dir / "audio_briefs.json"
    briefs_path.write_text(json.dumps({"production": production_name, "clips": briefs}, indent=2))
    print(f"  ✓ {briefs_path.name} ({len(briefs)} clips)")

    stem_map = build_per_scene_stem_map(production_name, briefs, beatmap["total_duration_ms"] / 1000)
    stem_map_path = data_dir / "per_scene_stem_map.json"
    stem_map_path.write_text(json.dumps(stem_map, indent=2))
    print(f"  ✓ {stem_map_path.name} ({len(briefs)} stems)")

    fcpxml = build_fcpxml_placement(production_name, briefs)
    fcpxml_path = data_dir / "fcpxml_placement.json"
    fcpxml_path.write_text(json.dumps(fcpxml, indent=2))
    print(f"  ✓ {fcpxml_path.name}")

    print(f"\n=== Done. Next: run generate_stems.py with per_scene_stem_map.json ===")
    print(f"  python3 generate_stems.py {production_root} --stems-file Data/per_scene_stem_map.json")


if __name__ == "__main__":
    main()
