#!/usr/bin/env python3
"""Daily check: flag any Plans/ file not yet referenced in the to-do list.

Mechanical only — never decides priority, never moves/archives/deletes anything.
Scans 001_Architecture/Plans/ (top level, not Archive/), and for each .md file
whose filename doesn't appear anywhere in Ongoing-Agent-OS-To-Do-List.md,
appends it to that file's "New plans detected" section for Tony to triage.
"""

import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLANS_DIR = ROOT / "001_Architecture" / "Plans"
TODO_FILE = ROOT / "001_Architecture" / "Ongoing-Agent-OS-To-Do-List.md"
LOG_FILE = ROOT / "001_Architecture" / "Scripts" / "sync_plans_to_todo.log"

SECTION_HEADER = "## \U0001F195 New plans detected (auto, needs Tony's priority call)"
SECTION_INTRO = (
    "Added automatically by `sync_plans_to_todo.py` (daily cron, 6am local). "
    "Mechanical only — presence check, not a read of the plan's content. "
    "Move an entry up into \"Top priority\" once Tony has set its priority, "
    "and delete the line here when that's done."
)


def log(msg: str) -> None:
    ts = date.today().isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")


def main() -> int:
    if not PLANS_DIR.is_dir():
        log(f"ERROR: Plans dir not found at {PLANS_DIR}")
        return 1
    if not TODO_FILE.is_file():
        log(f"ERROR: to-do list not found at {TODO_FILE}")
        return 1

    todo_text = TODO_FILE.read_text()

    plan_files = sorted(
        p for p in PLANS_DIR.glob("*.md") if p.name.lower() != "readme.md"
    )

    missing = [p for p in plan_files if p.name not in todo_text]

    if not missing:
        log(f"No new plans. Checked {len(plan_files)} file(s).")
        return 0

    new_lines = []
    for p in missing:
        title_match = re.search(r"^#\s+(.+)$", p.read_text(errors="ignore"), re.M)
        title = title_match.group(1).strip() if title_match else p.stem
        new_lines.append(
            f"- **{title}** (`{p.name}`, detected {date.today().isoformat()}) — not yet reviewed or prioritized."
        )

    if SECTION_HEADER in todo_text:
        # Append under the existing section's intro line, before the next "---" or "##".
        idx = todo_text.index(SECTION_HEADER)
        after_intro = todo_text.index("\n", todo_text.index(SECTION_INTRO, idx))
        rest = todo_text[after_intro + 1:]
        next_break = re.search(r"\n(---|\n##)", rest)
        insert_at = after_intro + 1 + (next_break.start() if next_break else len(rest))
        existing_block = todo_text[after_intro + 1:insert_at]
        # Skip filenames already flagged in this section specifically.
        truly_new = [
            line for line, p in zip(new_lines, missing) if p.name not in existing_block
        ]
        if not truly_new:
            log(f"{len(missing)} file(s) missing from main list but already flagged in section.")
            return 0
        updated_block = existing_block.rstrip("\n") + "\n" + "\n".join(truly_new) + "\n"
        todo_text = todo_text[: after_intro + 1] + updated_block + todo_text[insert_at:]
        added = truly_new
    else:
        block = f"\n{SECTION_HEADER}\n\n{SECTION_INTRO}\n\n" + "\n".join(new_lines) + "\n\n---\n"
        # Insert right after the "Top priority" section if present, else at top after the header bullets.
        marker = "## Top priority"
        if marker in todo_text:
            insert_idx = todo_text.index("\n---", todo_text.index(marker))
            insert_idx = todo_text.index("\n", insert_idx + 1) + 1
            todo_text = todo_text[:insert_idx] + block + todo_text[insert_idx:]
        else:
            todo_text = todo_text + block
        added = new_lines

    TODO_FILE.write_text(todo_text)
    log(f"Added {len(added)} new plan(s): {[p.name for p in missing]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
