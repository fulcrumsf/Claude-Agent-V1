#!/usr/bin/env python3
"""Inspect a local video with Gemini using dense, timestamped sampling.

This tool reports evidence only. It never approves or rejects a production
asset; the agent and Tony make the final review decision.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

from google import genai
from google.genai import types


DEFAULT_MODEL = "gemini-3.7-flash"
DEFAULT_FPS = 3.0

REPORT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "overall_confidence": {"type": "number"},
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "timestamp": {"type": "string"},
                    "category": {"type": "string"},
                    "severity": {"type": "string"},
                    "observation": {"type": "string"},
                    "confidence": {"type": "number"},
                },
                "required": ["timestamp", "category", "severity", "observation", "confidence"],
            },
        },
    },
    "required": ["summary", "overall_confidence", "findings"],
}


INSPECTION_PROMPT = """Inspect this video for a human production review. Return JSON only using the supplied schema.

Review the entire timeline at the supplied frame rate. Report concrete timestamped evidence, not guesses. Check:
- subject count and identity continuity; duplicate, missing, or morphing people/animals
- object continuity and physical connections, including where water, hoses, tools, or other effects originate
- chronology and causality: whether each action happens before its consequence
- spatial geometry, entrances, exits, paths, barriers, contact, scale, and physically possible movement
- character eyelines and gestures: whether a person looks or points at the subject's actual current location
- camera continuity: locked-off versus moving camera, cuts, alternate views, and impossible viewpoint changes
- audio anomalies such as music, commercial-style scoring, duplicate voices, or unexplained speech

Every finding must include a timestamp such as 00:04, a category, severity (error, warning, or note), a concise observation, and confidence from 0 to 1. If a requested detail is uncertain, say so explicitly. Do not issue an approval or rejection decision; this is evidence for an agent-led manual review."""


def _api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY or GOOGLE_API_KEY is required")
    return key


def _wait_for_file(client: genai.Client, uploaded: Any, timeout_s: int = 180) -> Any:
    deadline = time.monotonic() + timeout_s
    current = uploaded
    while getattr(getattr(current, "state", None), "name", None) == "PROCESSING":
        if time.monotonic() >= deadline:
            raise TimeoutError("Gemini file processing timed out")
        time.sleep(2)
        current = client.files.get(name=current.name)
    state = getattr(getattr(current, "state", None), "name", None)
    if state == "FAILED":
        raise RuntimeError(f"Gemini file processing failed: {current}")
    return current


def inspect_video(
    video_path: Path,
    *,
    model: str | None = None,
    fps: float = DEFAULT_FPS,
    api_key: str | None = None,
) -> dict[str, Any]:
    """Upload and inspect a video with direct Gemini static processing."""
    video_path = Path(video_path)
    if not video_path.is_file():
        raise FileNotFoundError(video_path)
    if not 0 < fps <= 24:
        raise ValueError("fps must be greater than 0 and no more than 24")

    client = genai.Client(api_key=api_key or _api_key())
    uploaded = _wait_for_file(client, client.files.upload(file=str(video_path)))
    video_part = types.Part(
        file_data=types.FileData(file_uri=uploaded.uri, mime_type=uploaded.mime_type or "video/mp4"),
        video_metadata=types.VideoMetadata(fps=fps),
    )
    response = client.models.generate_content(
        model=model or os.environ.get("GEMINI_VIDEO_MODEL", DEFAULT_MODEL),
        contents=[types.Content(role="user", parts=[video_part, types.Part(text=INSPECTION_PROMPT)])],
        config=types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json",
            response_json_schema=REPORT_SCHEMA,
            max_output_tokens=8192,
        ),
    )
    if not response.text:
        raise RuntimeError("Gemini returned an empty video inspection")
    report = json.loads(response.text)
    if not isinstance(report, dict):
        raise ValueError("Gemini video inspection must be a JSON object")
    return {
        "provider": "gemini_direct",
        "model": model or os.environ.get("GEMINI_VIDEO_MODEL", DEFAULT_MODEL),
        "processing_mode": "static",
        "sampling_fps": fps,
        "video": str(video_path),
        "report": report,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--model")
    parser.add_argument("--fps", type=float, default=float(os.environ.get("GEMINI_VIDEO_INSPECTION_FPS", DEFAULT_FPS)))
    args = parser.parse_args()
    result = inspect_video(args.video, model=args.model, fps=args.fps)
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
