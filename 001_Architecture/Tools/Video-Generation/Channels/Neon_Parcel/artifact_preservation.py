#!/usr/bin/env python3
"""Non-destructive artifact handling for paid video pipeline outputs."""

from __future__ import annotations

import re
import shutil
from pathlib import Path


VERSION_PATTERN = re.compile(r"(?:^|[-_])v\d+(?:[-_.]|$)", re.IGNORECASE)


def require_versioned_path(path: Path) -> Path:
    """Reject unversioned or already-existing output paths before any write."""
    path = Path(path)
    if not VERSION_PATTERN.search(path.stem):
        raise ValueError(f"output path must contain a version such as v3 or v4: {path}")
    if path.exists():
        raise FileExistsError(f"refusing to overwrite existing artifact: {path}")
    return path


def archive_existing(source: Path, archive_dir: Path) -> Path | None:
    """Move one superseded artifact to a collision-safe archive location."""
    source = Path(source)
    if not source.exists():
        return None
    archive_dir = Path(archive_dir)
    archive_dir.mkdir(parents=True, exist_ok=True)
    destination = archive_dir / source.name
    if destination.exists():
        raise FileExistsError(f"refusing to overwrite archived artifact: {destination}")
    shutil.move(str(source), str(destination))
    return destination


def archive_superseded(paths: list[Path], archive_dir: Path) -> list[Path]:
    """Archive all existing superseded paths without deleting or replacing files."""
    archived: list[Path] = []
    for path in paths:
        destination = archive_existing(path, archive_dir)
        if destination is not None:
            archived.append(destination)
    return archived
