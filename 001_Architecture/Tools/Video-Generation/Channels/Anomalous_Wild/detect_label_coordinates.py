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
    try:
        if text.startswith("```"):
            fence_parts = text.split("```")
            if len(fence_parts) < 2:
                raise ValueError("malformed code fence (odd fence count)")
            text = fence_parts[1].removeprefix("json").strip()
        result = json.loads(text)
    except (json.JSONDecodeError, ValueError) as e:
        snippet = text[:500]
        sys.exit(
            f"ERROR: failed to parse Gemini response as JSON for image "
            f"'{image_path}': {e}\n--- raw response snippet ---\n{snippet}"
        )

    if not isinstance(result, dict) or not isinstance(result.get("labels"), list):
        sys.exit(
            f"ERROR: unexpected response shape from Gemini for image "
            f"'{image_path}' — expected {{\"labels\": [...]}}, got: {result!r}"
        )

    for entry in result["labels"]:
        if not isinstance(entry, dict) or "feature" not in entry or "confidence" not in entry:
            sys.exit(
                f"ERROR: malformed label entry from Gemini for image "
                f"'{image_path}' — each entry needs 'feature' and 'confidence': {entry!r}"
            )
        # Structural enforcement of the "never guess" rule: strip any
        # coordinates the model may have attached to a not_found entry,
        # regardless of whether the prompt was obeyed.
        if entry.get("confidence") == "not_found":
            entry.pop("x_pct", None)
            entry.pop("y_pct", None)

    return result


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
