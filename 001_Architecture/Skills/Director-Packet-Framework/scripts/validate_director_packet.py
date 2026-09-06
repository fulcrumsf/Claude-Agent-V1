#!/usr/bin/env python3
"""Validate packet references and manifest consistency without changing assets."""

import argparse
import json
from datetime import date
from pathlib import Path


def validate(manifest_path: Path) -> tuple[list[str], list[str]]:
    manifest = json.loads(manifest_path.read_text())
    root = manifest_path.parent
    blocking: list[str] = []
    warnings: list[str] = []
    assets = manifest.get("assets", [])
    ordinals = [asset.get("reference_ordinal") for asset in assets if asset.get("reference_ordinal")]
    duplicates = sorted({ordinal for ordinal in ordinals if ordinals.count(ordinal) > 1})
    if duplicates:
        blocking.append(f"Duplicate reference ordinals: {', '.join(duplicates)}")
    for index, asset in enumerate(assets, 1):
        path = asset.get("path")
        if not path:
            blocking.append(f"Asset {index} has no path")
            continue
        resolved = Path(path) if Path(path).is_absolute() else root / path
        if asset.get("required", True) and not resolved.exists():
            blocking.append(f"Required asset does not exist: {path}")
        elif not asset.get("required", True) and not resolved.exists():
            warnings.append(f"Optional asset does not exist: {path}")
    for key in ("characters", "environment", "beats"):
        if not manifest.get(key):
            warnings.append(f"No {key} listed")
    if not (root / "Storyboards").exists():
        blocking.append("Storyboards directory is missing")
    return blocking, warnings


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    blocking, warnings = validate(args.manifest)
    manifest = json.loads(args.manifest.read_text())
    manifest["validation"] = {"blocking_findings": blocking, "warnings": warnings, "checked_at": date.today().isoformat()}
    manifest["status"] = "needs_revision" if blocking else "ready_for_review"
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n")
    report = [f"# Validation Report", "", f"**Status:** `{manifest['status']}`", ""]
    report += ["## Blocking Findings", ""] + ([f"- {item}" for item in blocking] or ["- None"])
    report += ["", "## Warnings", ""] + ([f"- {item}" for item in warnings] or ["- None"])
    (args.manifest.parent / "Validation-Report.md").write_text("\n".join(report) + "\n")
    print(manifest["status"])
    raise SystemExit(1 if blocking else 0)


if __name__ == "__main__":
    main()
