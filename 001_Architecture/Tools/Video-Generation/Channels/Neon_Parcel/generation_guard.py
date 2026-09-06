#!/usr/bin/env python3
"""Preflight guard for one paid provider task per Neon Parcel shot version."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RETRYABLE = {"provider_failed", "corrupt_output"}


def _load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"generation log does not exist: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("generation log must be a JSON object")
    return value


def _assets(log: dict[str, Any]) -> list[dict[str, Any]]:
    assets = log.setdefault("assets", [])
    if not isinstance(assets, list):
        raise ValueError("generation log assets must be a list")
    return assets


def check_allowed(
    log_path: Path,
    shot_id: str,
    version: str,
    prompt_file: Path,
    retry_reason: str | None = None,
) -> dict[str, Any]:
    """Raise on unsafe submission; return prompt hash and matching records otherwise."""
    if not prompt_file.is_file():
        raise ValueError(f"exact prompt must be archived before submission: {prompt_file}")
    if not re.search(r"(?:^|[-_])v\d+(?:[-_.]|$)", version, re.IGNORECASE):
        raise ValueError(f"paid generation version must be explicit, such as v3 or v4: {version}")
    if retry_reason and retry_reason not in RETRYABLE and not retry_reason.startswith("tony_revision:"):
        raise ValueError("retry reason must be provider_failed, corrupt_output, or tony_revision:<note>")

    log = _load(log_path)
    matches = [
        item for item in _assets(log)
        if item.get("shot_id") == shot_id and item.get("version") == version
    ]
    blocking = [item for item in matches if item.get("status") in {"reserved", "submitting", "submitted", "pending", "success"}]
    if blocking:
        ids = ", ".join(str(item.get("task_id", "unassigned")) for item in blocking)
        raise ValueError(f"paid task already exists for {shot_id} {version}: {ids}")
    if matches and not retry_reason:
        raise ValueError(f"shot/version has a prior attempt; an explicit permitted retry reason is required: {shot_id} {version}")

    prompt_hash = hashlib.sha256(prompt_file.read_bytes()).hexdigest()
    return {"shot_id": shot_id, "version": version, "prompt_file": str(prompt_file), "prompt_sha256": prompt_hash, "prior_attempts": len(matches)}


def reserve(log_path: Path, shot_id: str, version: str, prompt_file: Path, model: str, retry_reason: str | None = None) -> dict[str, Any]:
    record = check_allowed(log_path, shot_id, version, prompt_file, retry_reason)
    record.update({"model": model, "status": "reserved", "reserved_at": datetime.now(timezone.utc).isoformat()})
    log = _load(log_path)
    _assets(log).append(record)
    log_path.write_text(json.dumps(log, indent=2) + "\n", encoding="utf-8")
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    parser.add_argument("shot_id")
    parser.add_argument("version")
    parser.add_argument("prompt_file", type=Path)
    parser.add_argument("--model", required=True)
    parser.add_argument("--retry-reason")
    parser.add_argument("--reserve", action="store_true")
    args = parser.parse_args()
    result = reserve(args.log, args.shot_id, args.version, args.prompt_file, args.model, args.retry_reason) if args.reserve else check_allowed(args.log, args.shot_id, args.version, args.prompt_file, args.retry_reason)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
