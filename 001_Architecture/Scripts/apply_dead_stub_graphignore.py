"""
Write triage bucket 3 (dead stubs) into the root .graphifyignore so the
Resource Library graph rebuild skips them. Files are NOT touched or moved -
they stay fully usable in Obsidian, they just don't become graph nodes.

Idempotent: rewrites the delimited block between the two markers each run,
so re-running after a fresh triage keeps the list current.

Reads:  007_Resource_Library/_Stub_Triage.json
Writes: .graphifyignore  (block between the AUTO markers)

Usage:
  python3 apply_dead_stub_graphignore.py
  python3 apply_dead_stub_graphignore.py --dry-run
"""
import os
import json
import argparse
from datetime import datetime

WORKSPACE = "/Users/tonymacbook2025/Documents/Agent-OS"
TRIAGE = os.path.join(WORKSPACE, "007_Resource_Library", "_Stub_Triage.json")
IGNORE = os.path.join(WORKSPACE, ".graphifyignore")

BEGIN = "# >>> AUTO: 007_Resource_Library dead stubs (apply_dead_stub_graphignore.py) >>>"
END = "# <<< AUTO: 007_Resource_Library dead stubs <<<"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    triage = json.load(open(TRIAGE))
    dead = sorted(x["note"] for x in triage["bucket3_dead"])
    reasons = triage.get("dead_reasons", {})

    block = [
        BEGIN,
        f"# {len(dead)} near-empty notes with no salvageable signal - generated {datetime.now().strftime('%Y-%m-%d')}",
        f"# reasons: {reasons}",
        "# Excluded from the graph only. Still present + searchable in the vault.",
        "# Regenerate: python3 001_Architecture/Scripts/resource_library_stub_triage.py"
        " && python3 001_Architecture/Scripts/apply_dead_stub_graphignore.py",
    ]
    block += [f"007_Resource_Library/{p}" for p in dead]
    block.append(END)
    block_text = "\n".join(block) + "\n"

    current = open(IGNORE).read() if os.path.exists(IGNORE) else ""
    if BEGIN in current and END in current:
        pre = current.split(BEGIN)[0].rstrip("\n")
        post = current.split(END)[1].lstrip("\n")
        new = f"{pre}\n\n{block_text}\n{post}".rstrip("\n") + "\n"
    else:
        new = current.rstrip("\n") + "\n\n" + block_text

    if args.dry_run:
        print(f"[dry] would write {len(dead)} dead-stub paths into {IGNORE}")
        print("\n".join(block[:6]) + "\n  ...")
        return

    open(IGNORE, "w").write(new)
    print(f"wrote {len(dead)} dead-stub exclusions into {IGNORE}")


if __name__ == "__main__":
    main()
