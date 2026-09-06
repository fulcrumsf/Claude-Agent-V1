#!/usr/bin/env python3
"""Run structured storyboard inspection through Gemini vision."""

from __future__ import annotations

import argparse
import base64
import io
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from storyboard_contract import validate_spec
from storyboard_qa import build_inspection_prompt


DEFAULT_MODEL = "gemini-2.5-flash"
SUPPORTED_MIME_TYPES = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}
MAX_IMAGE_DIMENSION = 512


class ProviderResponseError(ValueError):
    """A provider response failed parsing while retaining the raw response."""

    def __init__(self, message: str, raw_response: dict[str, Any]):
        super().__init__(message)
        self.raw_response = raw_response


def build_request(spec: dict[str, Any], image_path: Path, model: str | None = None) -> dict[str, Any]:
    validate_spec(spec)
    image_path = Path(image_path)
    mime_type = SUPPORTED_MIME_TYPES.get(image_path.suffix.lower())
    if not mime_type:
        raise ValueError(f"unsupported storyboard image type: {image_path.suffix or 'none'}")
    if not image_path.is_file():
        raise FileNotFoundError(f"storyboard image does not exist: {image_path}")
    image_bytes = image_path.read_bytes()
    output_mime = mime_type
    try:
        from PIL import Image
        with Image.open(io.BytesIO(image_bytes)) as image:
            if max(image.size) > MAX_IMAGE_DIMENSION:
                image.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION), Image.Resampling.LANCZOS)
                buffer = io.BytesIO()
                image.convert("RGB").save(buffer, format="JPEG", quality=55, optimize=True)
                image_bytes = buffer.getvalue()
                output_mime = "image/jpeg"
    except (ImportError, OSError):
        pass
    image_data = base64.b64encode(image_bytes).decode("ascii")
    return {
        "contents": [{"parts": [
            {"text": build_inspection_prompt(spec)},
            {"inline_data": {"mime_type": output_mime, "data": image_data}},
        ]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0},
        "model": model or os.environ.get("GEMINI_VISION_MODEL", DEFAULT_MODEL),
    }


def _extract_report(response: dict[str, Any]) -> dict[str, Any]:
    try:
        text = response["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as error:
        raise ValueError("Gemini response has no assistant content") from error
    if text.startswith("```"):
        text = text.strip("`").removeprefix("json").strip()
    try:
        report = json.loads(text)
    except json.JSONDecodeError as error:
        raise ValueError(f"Gemini assistant content is not valid JSON: {error}") from error
    if not isinstance(report, dict):
        raise ValueError("Gemini assistant JSON must be an object")
    return report


def inspect_storyboard(spec: dict[str, Any], image_path: Path, *, api_key: str | None = None, model: str | None = None, timeout: int = 60) -> tuple[dict[str, Any], dict[str, Any]]:
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY is required for live storyboard inspection")
    payload = build_request(spec, image_path, model=model)
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{payload.pop('model')}:generateContent?key={key}"
    request = urllib.request.Request(endpoint, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw_response = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Gemini HTTP {error.code}: {body[:500]}") from error
    except (urllib.error.URLError, TimeoutError) as error:
        raise RuntimeError(f"Gemini request failed: {error}") from error
    if not isinstance(raw_response, dict):
        raise ValueError("Gemini response must be a JSON object")
    try:
        report = _extract_report(raw_response)
    except ValueError as error:
        raise ProviderResponseError(str(error), raw_response) from error
    return report, raw_response


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("candidate_image", type=Path)
    parser.add_argument("--model")
    parser.add_argument("--raw-out", type=Path)
    parser.add_argument("--report-out", type=Path)
    args = parser.parse_args()
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    report, raw = inspect_storyboard(spec, args.candidate_image, model=args.model)
    if args.raw_out:
        args.raw_out.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")
    if args.report_out:
        args.report_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    else:
        print(json.dumps(report, indent=2))
