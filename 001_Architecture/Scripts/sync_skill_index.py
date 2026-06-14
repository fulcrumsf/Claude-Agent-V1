#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import sys
import argparse
from datetime import date, datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ARCH_ROOT = PROJECT_ROOT / "001_Architecture"
SKILLS_ROOT = ARCH_ROOT / "Skills"
INDEX_PATH = SKILLS_ROOT / "Skill-Index.md"


def _read_hook_payload() -> dict:
    if sys.stdin.isatty():
        return {}
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except Exception:
        return {}


def _collect_paths(value, out: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"file_path", "filePath", "path"} and isinstance(child, str):
                out.append(child)
            else:
                _collect_paths(child, out)
    elif isinstance(value, list):
        for item in value:
            _collect_paths(item, out)


def _is_relevant_event(payload: dict) -> bool:
    if not payload:
        return True
    paths: list[str] = []
    _collect_paths(payload, paths)
    if not paths:
        return True
    relevant_roots = [
        str(SKILLS_ROOT),
        str(PROJECT_ROOT / "GEMINI.md"),
        str(PROJECT_ROOT / "AGENTS.md"),
        str(PROJECT_ROOT / "CLAUDE.md"),
    ]
    return any(
        any(path.startswith(root) for root in relevant_roots)
        for path in paths
    )


def _extract_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        return {}
    frontmatter = match.group(1)
    result: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def _clean_summary(text: str, limit: int = 180) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rstrip() + "…"


def _read_skill_summary(skill_path: Path) -> tuple[str, str]:
    text = skill_path.read_text(encoding="utf-8", errors="ignore")
    fm = _extract_frontmatter(text)
    name = fm.get("name") or skill_path.parent.name
    description = fm.get("description") or ""
    if not description:
        heading_match = re.search(r"^#\s+(.+)$", text, re.M)
        description = heading_match.group(1) if heading_match else ""
    return name, _clean_summary(description)


def build_index() -> str:
    rows: list[tuple[str, str, str]] = []
    skill_paths = []
    for root, dirs, files in os.walk(SKILLS_ROOT, followlinks=True):
        dirs[:] = [d for d in dirs if d != ".git"]
        for f in files:
            if f == "SKILL.md":
                skill_paths.append(Path(root) / f)
    for skill_path in sorted(skill_paths):
        if ".git" in skill_path.parts:
            continue
        if skill_path.parent.name == ".system":
            continue
        name, summary = _read_skill_summary(skill_path)
        rel_path = skill_path.relative_to(PROJECT_ROOT).as_posix()
        rows.append((name, summary, rel_path))

    generated_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    today = date.today().isoformat()

    lines = [
        "---",
        'title: "Skill Index"',
        "type: registry",
        "category: architecture",
        "tags:",
        "  - agents",
        "  - skills",
        "  - registry",
        f"created: {today}",
        "source: local",
        "generated_by: sync_skill_index.py",
        "---",
        "",
        "# Skill Index",
        "",
        f"Generated: {generated_at}",
        "",
        "This file is generated from `001_Architecture/Skills/**/SKILL.md` and is the shared discovery layer for Claude, Codex, and Gemini in this workspace.",
        "",
        "## How To Use",
        "",
        "1. Read the index first when choosing a skill.",
        "2. Open the matching `SKILL.md` file.",
        "3. If the skill file changes, rerun the sync script or let the hook regenerate this index automatically.",
        "",
        "## Skills",
        "",
        "| Skill | Summary | Path |",
        "| --- | --- | --- |",
    ]

    for name, summary, rel_path in rows:
        lines.append(f"| {name} | {summary} | `{rel_path}` |")

    lines.extend(["", "## Notes", "", "- Canonical skill files live in `001_Architecture/Skills/`.", "- This registry exists so Gemini and other agents can discover skills without guessing.", ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Regenerate the workspace skill index.")
    parser.add_argument("--force", action="store_true", help="Regenerate even if the hook payload does not look relevant.")
    args = parser.parse_args()

    payload = _read_hook_payload()
    if not args.force and not _is_relevant_event(payload):
        return 0
    content = build_index()
    INDEX_PATH.write_text(content + "\n", encoding="utf-8")
    print(f"Wrote {INDEX_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
