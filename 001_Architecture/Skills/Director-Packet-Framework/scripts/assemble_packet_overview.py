#!/usr/bin/env python3
"""Write a human-readable packet overview and optionally assemble image references."""

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    lines = [f"# Director's Packet Overview: {manifest.get('scene_id', 'Unnamed Scene')}", ""]
    lines += [f"**Purpose:** {manifest.get('scene_purpose', 'Not specified')}", f"**Status:** `{manifest.get('status', 'draft')}`", ""]
    lines += ["## References", ""]
    for asset in manifest.get("assets", []):
        ordinal = asset.get("reference_ordinal", "")
        lines.append(f"- `{asset.get('role', 'unclassified')}` {ordinal}: `{asset.get('path', 'missing')}`")
    lines += ["", "## Scene Notes", "", manifest.get("visual_style", "No visual style supplied.")]
    (args.manifest.parent / "Director-Packet-Overview.md").write_text("\n".join(lines) + "\n")
    print(args.manifest.parent / "Director-Packet-Overview.md")


if __name__ == "__main__":
    main()
