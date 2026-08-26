#!/usr/bin/env python3
"""
check_naming_convention.py — validates file/folder names against the
workspace file-naming convention documented in Agent-OS/CLAUDE.md:

  - No spaces — use `_` or `-` as word separators
  - Capitalize the first letter of every word: Video_Pipeline_PDR.md
  - Acronyms stay fully uppercase: MCP_Gateway_Controller
  - .py files are exempt (other scripts may reference them by current name)

Built 2026-08-16 after a real, repeated violation: scene-id-derived folder/file
names (scene_02, scene_05b.png) got created directly from internal lowercase
identifiers without translation to this convention, on more than one
occasion in the same session. This script exists so that check happens
mechanically instead of depending on either Tony or the agent remembering
to do it by hand every time.

Usage:
  python3 check_naming_convention.py <path> [<path> ...]
  python3 check_naming_convention.py --stdin   # read newline-separated paths from stdin

Exit code 0 = all paths pass. Exit code 1 = at least one violation found
(violations are printed to stdout either way).
"""
import re
import sys

EXEMPT_EXTENSIONS = {".py"}

# Standard Claude Code skill bundled-resource folder names (skill-creator spec):
# scripts/, references/, assets/ are lowercase by that external convention,
# already used this way in Character-Sheet-Generation, Prop-Sheet-Generation,
# and Environment-Sheet-Generation before this checker existed. Renaming them
# to Title_Case would break skill tooling that expects the lowercase names,
# not fix a real violation — so they're exempted as a whole path segment.
EXEMPT_SEGMENTS = {"scripts", "references", "assets"}

# A segment is "clean" if every underscore/dash/space-delimited word starts
# with an uppercase letter (or is a fully-uppercase acronym), contains no
# spaces, and uses only letters/digits/underscore/dash/period within itself.
WORD_RE = re.compile(r"^[A-Z0-9][a-zA-Z0-9]*$|^[A-Z0-9]+$")


def check_segment(segment: str) -> list[str]:
    """Returns a list of violation messages for one path segment (file or folder name)."""
    violations = []

    if segment in EXEMPT_SEGMENTS:
        return violations

    if " " in segment:
        violations.append(f"contains a space: {segment!r}")

    # Split the stem (ignore a single trailing extension) into words on _ and -
    if "." in segment and not segment.startswith("."):
        stem, _, ext = segment.rpartition(".")
    else:
        stem, ext = segment, ""

    if ext.lower() in {e.lstrip(".") for e in EXEMPT_EXTENSIONS}:
        return violations  # .py files exempt entirely

    words = re.split(r"[_\-]", stem)
    for w in words:
        if not w:
            continue  # tolerate double separators rather than double-flagging
        if not WORD_RE.match(w):
            violations.append(
                f"word {w!r} in {segment!r} doesn't start with a capital letter "
                f"(expected Title_Case_With_Underscores, e.g. 'Scene_02' not 'scene_02')"
            )

    return violations


WORKSPACE_ROOT_MARKER = "/Documents/Agent-OS/"  # the real repo root, as a literal path anchor
SKIP_PREFIXES = ("/private/tmp/", "/tmp/")  # scratchpad space — explicitly not workspace content


def check_path(path: str) -> list[str]:
    """Checks path segments that fall inside the real Agent-OS workspace tree
    — never the OS-level prefix (home directory, username, etc.), and never
    scratchpad/temp paths, neither of which this convention governs.

    Built 2026-08-16, fixed same day: an earlier version matched "Agent-OS"
    as a loose path segment, which also matched inside sanitized scratchpad
    directory names like ".../-Users-tonymacbook2025-Documents-Agent-OS/..."
    (a single dash-joined segment, not a real path boundary) and incorrectly
    flagged temp files that were never subject to this convention."""
    violations = []

    if path.startswith(SKIP_PREFIXES):
        return violations

    if WORKSPACE_ROOT_MARKER in path:
        path = path.split(WORKSPACE_ROOT_MARKER, 1)[1]
    # If the marker isn't present, this is either a relative path already
    # inside the repo (check it as-is) or a path outside the workspace
    # entirely that happens not to match SKIP_PREFIXES — checking it as-is
    # is the safer default over silently skipping an unrecognized path.

    parts = [p for p in path.strip("/").split("/") if p]
    for segment in parts:
        for v in check_segment(segment):
            violations.append(f"{path}: {v}")
    return violations


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--stdin":
        paths = [line.strip() for line in sys.stdin if line.strip()]
    else:
        paths = sys.argv[1:]

    if not paths:
        sys.exit("Usage: check_naming_convention.py <path> [<path> ...]  |  --stdin")

    all_violations = []
    for path in paths:
        all_violations.extend(check_path(path))

    if all_violations:
        print("❌ NAMING CONVENTION VIOLATIONS:")
        for v in all_violations:
            print(f"  - {v}")
        sys.exit(1)
    else:
        print(f"✅ All {len(paths)} path(s) pass the naming convention.")
        sys.exit(0)


if __name__ == "__main__":
    main()
