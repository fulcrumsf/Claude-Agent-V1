#!/usr/bin/env python3
"""Create a non-destructive Director's Packet scaffold from a scene spec."""

import argparse
import json
from datetime import date
from pathlib import Path


REQUIRED = ("project_id", "scene_id", "scene_purpose")
SUBDIRS = ("References/Characters", "References/Props", "References/Environment", "Diagrams", "Storyboards")


def build_manifest(spec: dict) -> dict:
    missing = [key for key in REQUIRED if not spec.get(key)]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")
    manifest = dict(spec)
    manifest.setdefault("schema_version", "1.0")
    manifest.setdefault("status", "draft")
    manifest.setdefault("version", 1)
    manifest.setdefault("parent_version", None)
    manifest.setdefault("revision_reason", None)
    manifest.setdefault("assets", [])
    manifest.setdefault("validation", {"blocking_findings": [], "warnings": [], "checked_at": None})
    manifest.setdefault("extensions", {})
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scene_json", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    spec = json.loads(args.scene_json.read_text())
    manifest = build_manifest(spec)
    args.out.mkdir(parents=True, exist_ok=True)
    for subdir in SUBDIRS:
        (args.out / subdir).mkdir(parents=True, exist_ok=True)
    (args.out / "Director-Packet-Manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    brief = [
        f"# {manifest['scene_id']} Director's Packet",
        "",
        f"**Purpose:** {manifest['scene_purpose']}",
        f"**Created:** {date.today().isoformat()}",
        "",
        "This packet is a planning reference. Video generation and approval are downstream responsibilities.",
        "",
    ]
    (args.out / "Scene-Brief.md").write_text("\n".join(brief))
    print(args.out / "Director-Packet-Manifest.json")


if __name__ == "__main__":
    main()
