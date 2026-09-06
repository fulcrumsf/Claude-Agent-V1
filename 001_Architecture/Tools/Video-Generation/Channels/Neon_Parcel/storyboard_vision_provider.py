#!/usr/bin/env python3
"""Run structured storyboard inspection through an OpenRouter vision model."""

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

from storyboard_qa import build_inspection_prompt
from storyboard_contract import validate_spec


API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "qwen/qwen3.5-flash-02-23"
SUPPORTED_MIME_TYPES = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}
MAX_IMAGE_DIMENSION = 512


class ProviderResponseError(ValueError):
    """A provider response failed parsing while retaining the raw response."""

    def __init__(self, message: str, raw_response: dict[str, Any]):
        super().__init__(message)
        self.raw_response = raw_response


def _image_data_uri(image_path: Path) -> str:
    suffix = image_path.suffix.lower()
    mime_type = SUPPORTED_MIME_TYPES.get(suffix)
    if not mime_type:
        raise ValueError(f"unsupported storyboard image type: {suffix or 'none'}")
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
    encoded = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{output_mime};base64,{encoded}"


def build_request(spec: dict[str, Any], image_path: Path, model: str | None = None) -> dict[str, Any]:
    """Build the exact provider request without making a network call."""
    validate_spec(spec)
    image_path = Path(image_path)
    return {
        "model": model or os.environ.get("OPENROUTER_VISION_MODEL", DEFAULT_MODEL),
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": build_inspection_prompt(spec)},
                    {"type": "image_url", "image_url": {"url": _image_data_uri(image_path)}},
                ],
            }
        ],
    }


def _extract_report(response: dict[str, Any]) -> dict[str, Any]:
    try:
        content = response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as error:
        raise ValueError("OpenRouter response has no assistant content") from error
    if isinstance(content, list):
        content = "".join(
            part.get("text", "") for part in content if isinstance(part, dict) and isinstance(part.get("text"), str)
        )
    if not isinstance(content, str) or not content.strip():
        raise ValueError("OpenRouter assistant content is empty")
    if content.startswith("```"):
        content = content.strip("`").removeprefix("json").strip()
    try:
        report = json.loads(content)
    except json.JSONDecodeError as error:
        raise ValueError(f"OpenRouter assistant content is not valid JSON: {error}") from error
    if not isinstance(report, dict):
        raise ValueError("OpenRouter assistant JSON must be an object")
    return report


def inspect_storyboard(
    spec: dict[str, Any],
    image_path: Path,
    *,
    api_key: str | None = None,
    model: str | None = None,
    timeout: int = 60,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Call OpenRouter and return (parsed_report, raw_provider_response)."""
    key = api_key or os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY is required for live storyboard inspection")
    payload = build_request(spec, Path(image_path), model=model)
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
            "HTTP-Referer": "https://openrouter.ai/",
            "X-OpenRouter-Title": "Agent-OS Neon Parcel Storyboard QA",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw_response = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenRouter HTTP {error.code}: {body[:500]}") from error
    except (urllib.error.URLError, TimeoutError) as error:
        raise RuntimeError(f"OpenRouter request failed: {error}") from error
    if not isinstance(raw_response, dict):
        raise ValueError("OpenRouter response must be a JSON object")
    try:
        report = _extract_report(raw_response)
    except ValueError as error:
        raise ProviderResponseError(str(error), raw_response) from error
    return report, raw_response


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("candidate_image", type=Path)
    parser.add_argument("--model")
    parser.add_argument("--raw-out", type=Path)
    parser.add_argument("--report-out", type=Path)
    parser.add_argument("--dry-run", action="store_true", help="print request metadata without calling OpenRouter")
    args = parser.parse_args()
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    request = build_request(spec, args.candidate_image, model=args.model)
    if args.dry_run:
        image_url = request["messages"][0]["content"][1]["image_url"]["url"]
        print(json.dumps({"model": request["model"], "image_bytes": len(image_url), "dry_run": True}, indent=2))
        return
    report, raw_response = inspect_storyboard(spec, args.candidate_image, model=args.model)
    if args.raw_out:
        args.raw_out.parent.mkdir(parents=True, exist_ok=True)
        args.raw_out.write_text(json.dumps(raw_response, indent=2) + "\n", encoding="utf-8")
    rendered = json.dumps(report, indent=2) + "\n"
    if args.report_out:
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        args.report_out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
