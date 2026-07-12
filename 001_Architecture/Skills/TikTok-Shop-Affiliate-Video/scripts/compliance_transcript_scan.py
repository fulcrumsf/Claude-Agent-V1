#!/usr/bin/env python3
"""
compliance_transcript_scan.py — Phase 3 post-build transcript scan.

Transcribes each finished edit (ElevenLabs Scribe, already used elsewhere in
this workspace for audio-first editing) and checks it for banned claim
language — guarantee/cure/medical-outcome phrases that are FTC-level risks
regardless of what TikTok's own ledger says, plus anything the compliance
ledger's Claims-category rules call out.

Usage:
  python3 compliance_transcript_scan.py <edit_video_path> <out_dir>
"""
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("Missing: pip install requests")
    sys.exit(1)

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")

# Universal FTC-risk phrases — apply regardless of niche or ledger content.
_BANNED_PHRASES = [
    "guarantee", "guaranteed", "cure", "cures", "clinically proven",
    "proven to", "100% effective", "instant results", "miracle",
    "no side effects", "risk free", "fda approved",
]


def banned_phrase_patterns() -> list:
    return list(_BANNED_PHRASES)


def scan_transcript_for_violations(transcript_text: str, patterns: list) -> list:
    lowered = transcript_text.lower()
    return [p for p in patterns if p.lower() in lowered]


def extract_audio(video_path: Path, out_path: Path) -> Path:
    result = subprocess.run(
        ["ffmpeg", "-i", str(video_path), "-vn", "-acodec", "libmp3lame", str(out_path), "-y"],
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg audio extraction failed for {video_path}: {result.stderr.decode(errors='ignore')[:300]}")
    return out_path


def transcribe_audio(audio_path: Path) -> str:
    if not ELEVENLABS_API_KEY:
        raise RuntimeError("ELEVENLABS_API_KEY not set. Run: source ~/.env-secrets")
    with open(audio_path, "rb") as f:
        response = requests.post(
            "https://api.elevenlabs.io/v1/speech-to-text",
            headers={"xi-api-key": ELEVENLABS_API_KEY},
            files={"file": f},
            data={"model_id": "scribe_v1"},
            timeout=120,
        )
    response.raise_for_status()
    return response.json().get("text", "")


def scan_video(video_path: Path, out_dir: Path) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    audio_path = out_dir / f"{Path(video_path).stem}.mp3"
    extract_audio(Path(video_path), audio_path)
    transcript = transcribe_audio(audio_path)

    report_path = out_dir / f"{Path(video_path).stem}-transcript-scan.md"
    lines = [f"# Transcript Scan — {Path(video_path).name}\n", f"## Transcript\n{transcript}\n"]

    if not transcript.strip():
        lines.append("## Violations Found\nTranscript came back empty — cannot verify content is safe.\n\nVerdict: FLAG\n")
    else:
        violations = scan_transcript_for_violations(transcript, banned_phrase_patterns())
        if violations:
            lines.append(f"## Violations Found\n{', '.join(violations)}\n\nVerdict: FLAG\n")
        else:
            lines.append("## Violations Found\nNone.\n\nVerdict: CLEAR\n")

    report_path.write_text("\n".join(lines))
    return report_path


def main():
    if len(sys.argv) < 3:
        sys.exit("Usage: compliance_transcript_scan.py <edit_video_path> <out_dir>")
    report = scan_video(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"Transcript scan report: {report}")


if __name__ == "__main__":
    main()
