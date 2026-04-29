"""
tools/audio_tts.py

TTS generation via ElevenLabs with word-level timestamp extraction.

Key functions
─────────────
generate_voiceover(text, output_filename, voice_id)
    → generates MP3, returns output path

generate_voiceover_with_timestamps(text, output_filename, voice_id)
    → generates MP3 + returns word-level alignment list
    → each entry: {"word": str, "start_s": float, "end_s": float}

build_beat_sheet(script_md_path, audio_dir, voice_id)
    → reads a script.md file section-by-section, generates TTS for each scene,
      extracts timestamps, and writes beat_sheet.json to audio_dir

Usage (CLI)
───────────
  python3 tools/audio_tts.py <script.md> <output_audio_dir> [--voice <voice_id>]

  Reads script.md, generates per-scene MP3s, and outputs:
    <output_audio_dir>/narration/scene_XX.mp3   ← one file per scene
    <output_audio_dir>/beat_sheet.json           ← word-level timestamps

beat_sheet.json schema
──────────────────────
[
  {
    "scene_id": "scene_01",
    "audio_file": "narration/scene_01.mp3",
    "duration_s": 12.4,
    "words": [
      {"word": "Deep",   "start_s": 0.0,  "end_s": 0.31},
      {"word": "in",     "start_s": 0.35, "end_s": 0.52},
      ...
    ]
  },
  ...
]
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import requests

from config import ELEVENLABS_API_KEY

# ElevenLabs model that returns word-level alignment
_TTS_MODEL = "eleven_monolingual_v1"
_DEFAULT_VOICE = "kdmDKE6EkgrWrrykO9Qt"  # Brian


# ── Core TTS ─────────────────────────────────────────────────────────────────

def generate_voiceover(
    text: str,
    output_filename: str = "scene_audio.mp3",
    voice_id: str = _DEFAULT_VOICE,
) -> str:
    """Generate TTS MP3 using ElevenLabs. Returns output path."""
    if not ELEVENLABS_API_KEY:
        raise ValueError("ELEVENLABS_API_KEY is missing from .env")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY,
    }
    payload = {
        "text": text,
        "model_id": _TTS_MODEL,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
    }

    preview = text[:80] + ("..." if len(text) > 80 else "")  # type: ignore[index]
    print(f"  Generating TTS: '{preview}'")
    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()

    Path(output_filename).parent.mkdir(parents=True, exist_ok=True)
    with open(output_filename, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

    print(f"  ✓ Saved: {output_filename}")
    return output_filename


# ── TTS + word-level timestamps ───────────────────────────────────────────────

def generate_voiceover_with_timestamps(
    text: str,
    output_filename: str = "scene_audio.mp3",
    voice_id: str = _DEFAULT_VOICE,
) -> tuple[str, list[dict]]:
    """
    Generate TTS MP3 and extract word-level timestamps.

    Uses the ElevenLabs /with-timestamps endpoint which returns both the audio
    (base64-encoded) and an alignment object with character/word timings.

    Returns
    -------
    (audio_path, words)
    words: list of {"word": str, "start_s": float, "end_s": float}
    """
    import base64

    if not ELEVENLABS_API_KEY:
        raise ValueError("ELEVENLABS_API_KEY is missing from .env")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps"
    headers = {
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY,
    }
    payload = {
        "text": text,
        "model_id": _TTS_MODEL,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
    }

    preview = text[:80] + ("..." if len(text) > 80 else "")  # type: ignore[index]
    print(f"  Generating TTS+timestamps: '{preview}'")
    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()

    data = resp.json()

    # Save audio
    audio_b64 = data.get("audio_base64", "")
    Path(output_filename).parent.mkdir(parents=True, exist_ok=True)
    with open(output_filename, "wb") as f:
        f.write(base64.b64decode(audio_b64))
    print(f"  ✓ Saved: {output_filename}")

    # Parse alignment → word-level timestamps
    alignment = data.get("alignment") or data.get("normalized_alignment") or {}
    words = _alignment_to_words(alignment)

    return output_filename, words


def _alignment_to_words(alignment: dict) -> list[dict]:
    """
    Convert ElevenLabs alignment object to a flat list of word timestamps.

    ElevenLabs returns character-level alignment:
      {
        "characters": ["D","e","e","p"," ","i","n",...],
        "character_start_times_seconds": [0.0, 0.05, ...],
        "character_end_times_seconds":   [0.05, 0.1, ...]
      }

    We group consecutive non-space characters into words.
    """
    chars = alignment.get("characters", [])
    starts = alignment.get("character_start_times_seconds", [])
    ends = alignment.get("character_end_times_seconds", [])

    if not chars:
        return []

    words: list[dict] = []
    current_chars: list[str] = []
    current_start: float = 0.0
    current_end: float = 0.0
    in_word: bool = False

    for ch, s, e in zip(chars, starts, ends):
        ch = str(ch)
        s = float(s)
        e = float(e)
        if ch in (" ", "\n", "\t"):
            if in_word:
                words.append({
                    "word": "".join(current_chars),
                    "start_s": round(current_start, 3),  # type: ignore[call-overload]
                    "end_s": round(current_end, 3),       # type: ignore[call-overload]
                })
                current_chars = []
                in_word = False
        else:
            if not in_word:
                current_start = s
                in_word = True
            current_chars.append(ch)
            current_end = e

    # flush last word
    if in_word and current_chars:
        words.append({
            "word": "".join(current_chars),
            "start_s": round(current_start, 3),  # type: ignore[call-overload]
            "end_s": round(current_end, 3),       # type: ignore[call-overload]
        })

    return words


# ── beat_sheet.json builder ───────────────────────────────────────────────────

def build_beat_sheet(
    script_md_path: str | Path,
    audio_dir: str | Path,
    voice_id: str = _DEFAULT_VOICE,
) -> Path:
    """
    Read script.md, generate per-scene TTS, extract timestamps,
    and write beat_sheet.json.

    Script format expected:
      ## Scene 01 — Title
      Narration text here...

      ## Scene 02 — Title
      ...

    Returns the path to beat_sheet.json.
    """
    script_path = Path(script_md_path)
    audio_dir = Path(audio_dir)
    narration_dir = audio_dir / "narration"
    narration_dir.mkdir(parents=True, exist_ok=True)

    script_text = script_path.read_text(encoding="utf-8")
    scenes = _parse_script_scenes(script_text)

    if not scenes:
        print("  ✗ No scenes found in script. Check ## Scene heading format.")
        return audio_dir / "beat_sheet.json"

    beat_sheet = []
    cumulative_offset = 0.0

    for scene in scenes:
        scene_id = scene["scene_id"]
        narration = scene["narration"].strip()
        if not narration:
            print(f"  ⚠ Skipping empty scene: {scene_id}")
            continue

        audio_file = narration_dir / f"{scene_id}.mp3"
        rel_audio = f"narration/{scene_id}.mp3"

        if audio_file.exists():
            print(f"  ✓ Already exists, skipping TTS: {scene_id}")
            # Still need to parse timestamps — re-request
            # Fall through to generate timestamps from existing audio isn't
            # possible without the alignment data, so we re-generate.
            # For idempotency, skip and use a placeholder duration.
            duration_s = _estimate_duration(narration)
            words: list[dict] = []
        else:
            try:
                _, words = generate_voiceover_with_timestamps(
                    narration, str(audio_file), voice_id
                )
                duration_s = words[-1]["end_s"] if words else _estimate_duration(narration)
            except Exception as exc:
                print(f"  ✗ TTS failed for {scene_id}: {exc}")
                # Fallback: generate without timestamps
                try:
                    generate_voiceover(narration, str(audio_file), voice_id)
                except Exception as exc2:
                    print(f"  ✗ Fallback TTS also failed: {exc2}")
                duration_s = _estimate_duration(narration)
                words = []

        # Add global (cumulative) timestamps alongside scene-local ones
        global_words = [
            {
                "word": w["word"],
                "start_s": round(w["start_s"] + cumulative_offset, 3),   # type: ignore[call-overload]
                "end_s": round(w["end_s"] + cumulative_offset, 3),        # type: ignore[call-overload]
                "local_start_s": w["start_s"],
                "local_end_s": w["end_s"],
            }
            for w in words
        ]

        beat_sheet.append({
            "scene_id": scene_id,
            "scene_title": scene.get("title", ""),
            "audio_file": rel_audio,
            "duration_s": round(duration_s, 3),          # type: ignore[call-overload]
            "global_start_s": round(cumulative_offset, 3),  # type: ignore[call-overload]
            "global_end_s": round(cumulative_offset + duration_s, 3),  # type: ignore[call-overload]
            "words": global_words,
        })

        cumulative_offset += duration_s

    beat_sheet_path = audio_dir / "beat_sheet.json"
    beat_sheet_path.write_text(json.dumps(beat_sheet, indent=2, ensure_ascii=False))
    total = round(cumulative_offset, 1)  # type: ignore[call-overload]
    print(f"\n  ✓ beat_sheet.json written — {len(beat_sheet)} scenes, {total}s total")
    print(f"    {beat_sheet_path}")
    return beat_sheet_path


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_script_scenes(text: str) -> list[dict]:
    """
    Split a markdown script into scenes by ## headings.
    Returns list of {"scene_id": str, "title": str, "narration": str}.
    """
    # Match headings like: ## Scene 01 — Deep Ocean
    heading_pattern = re.compile(
        r"^##\s+(?:Scene\s+)?(\d+[a-zA-Z]?)\s*[—\-–]?\s*(.*?)$",
        re.MULTILINE | re.IGNORECASE,
    )
    matches = list(heading_pattern.finditer(text))

    scenes = []
    for i, match in enumerate(matches):
        num = match.group(1).zfill(2)
        title = match.group(2).strip()
        scene_id = f"scene_{num}"

        # Body = text until next heading
        body_start = match.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[body_start:body_end].strip()  # type: ignore[index]

        # Strip markdown formatting from narration
        narration = re.sub(r"\*\*(.+?)\*\*", r"\1", body)   # bold
        narration = re.sub(r"\*(.+?)\*", r"\1", narration)   # italic
        narration = re.sub(r"^#+\s.*$", "", narration, flags=re.MULTILINE)  # subheadings
        narration = re.sub(r"\[.*?\]\(.*?\)", "", narration)  # links
        narration = "\n".join(
            line for line in narration.splitlines()
            if not line.strip().startswith("#")
        ).strip()

        scenes.append({"scene_id": scene_id, "title": title, "narration": narration})

    return scenes


def _estimate_duration(text: str) -> float:
    """Rough duration estimate: ~150 words per minute."""
    word_count = len(text.split())
    return round(word_count / 150 * 60, 1)  # type: ignore[call-overload]


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate TTS narration + beat_sheet.json from a script.md"
    )
    parser.add_argument("script", help="Path to script.md")
    parser.add_argument("audio_dir", help="Output directory (002_audio/)")
    parser.add_argument("--voice", default=_DEFAULT_VOICE, help="ElevenLabs voice ID")
    args = parser.parse_args()

    build_beat_sheet(args.script, args.audio_dir, voice_id=args.voice)
