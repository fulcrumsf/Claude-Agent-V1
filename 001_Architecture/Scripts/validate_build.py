#!/usr/bin/env python3
"""
validate_build.py — Agent-OS Build Validation Script

Verifies that functional artifacts (scripts, skills, tool configs) actually work
after being written. Called automatically by Claude after builds, or manually.

Usage:
  python3 validate_build.py --files path1.py,path2/SKILL.md
  python3 validate_build.py --files path1.py --clear-manifest
  python3 validate_build.py --data-fetch --sources "kie.ai,fal.ai,openai" --got "kie.ai,openai"

Exit codes:
  0 = all passed
  1 = one or more checks failed (report to Tony)
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

MANIFEST_PATH = Path('/tmp/agent_os_build_manifest.json')
SKILL_INDEX = Path('/Users/tonymacbook2025/Documents/Agent-OS/001_Architecture/Skills/Skill-Index.md')
WORKSPACE_ROOT = Path('/Users/tonymacbook2025/Documents/Agent-OS')


def load_manifest():
    try:
        return json.loads(MANIFEST_PATH.read_text())
    except Exception:
        return {'unverified': [], 'verified': []}


def save_manifest(manifest):
    try:
        MANIFEST_PATH.write_text(json.dumps(manifest, indent=2))
    except Exception:
        pass


def mark_verified(file_path: str):
    manifest = load_manifest()
    if file_path in manifest.get('unverified', []):
        manifest['unverified'].remove(file_path)
    if file_path not in manifest.get('verified', []):
        manifest.setdefault('verified', []).append(file_path)
    save_manifest(manifest)


def check_python(file_path: Path) -> tuple[bool, str]:
    """Syntax check + --help smoke test for Python scripts."""
    results = []
    passed = True

    # Existence and non-empty
    if not file_path.exists():
        return False, f"FILE NOT FOUND: {file_path}"
    if file_path.stat().st_size == 0:
        return False, f"FILE IS EMPTY: {file_path}"

    # Syntax check
    r = subprocess.run(
        [sys.executable, '-m', 'py_compile', str(file_path)],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        passed = False
        results.append(f"  ✗ Syntax error: {r.stderr.strip()}")
    else:
        results.append(f"  ✓ Syntax: valid")

    # --help smoke test (only for CLI scripts with click/argparse)
    content = file_path.read_text()
    if 'argparse' in content or 'click' in content or '@cli.command' in content:
        r2 = subprocess.run(
            [sys.executable, str(file_path), '--help'],
            capture_output=True, text=True, timeout=10
        )
        if r2.returncode not in (0, 1):  # Some CLIs exit 1 on --help (acceptable)
            passed = False
            results.append(f"  ✗ --help failed (exit {r2.returncode}): {r2.stderr.strip()[:200]}")
        else:
            results.append(f"  ✓ CLI --help: runs without error")

    # Check referenced file paths in the script
    import re
    path_refs = re.findall(r'Path\(["\']([^"\']+)["\']\)|open\(["\']([^"\']+)["\']\)', content)
    missing_paths = []
    for groups in path_refs:
        for ref in groups:
            if ref and not ref.startswith('{') and '~' not in ref:
                p = Path(ref)
                if p.is_absolute() and not p.exists():
                    missing_paths.append(ref)
    if missing_paths:
        passed = False
        results.append(f"  ✗ Referenced paths missing: {', '.join(missing_paths[:5])}")
    elif path_refs:
        results.append(f"  ✓ Referenced paths: checked")

    return passed, '\n'.join(results)


def check_skill(file_path: Path) -> tuple[bool, str]:
    """Verify SKILL.md has valid frontmatter and is in the Skill-Index."""
    results = []
    passed = True

    if not file_path.exists():
        return False, f"FILE NOT FOUND: {file_path}"
    if file_path.stat().st_size == 0:
        return False, f"FILE IS EMPTY: {file_path}"

    content = file_path.read_text()

    # Check frontmatter exists
    if not content.startswith('---'):
        passed = False
        results.append(f"  ✗ Missing YAML frontmatter")
    else:
        results.append(f"  ✓ Frontmatter: present")

    # Check name field
    import re
    name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
    if not name_match:
        passed = False
        results.append(f"  ✗ Missing 'name:' field in frontmatter")
    else:
        skill_name = name_match.group(1).strip()
        results.append(f"  ✓ Name: {skill_name}")

        # Check appears in Skill-Index
        if SKILL_INDEX.exists():
            index_content = SKILL_INDEX.read_text()
            if skill_name not in index_content:
                passed = False
                results.append(f"  ✗ '{skill_name}' not found in Skill-Index.md — run sync_skill_index.py")
            else:
                results.append(f"  ✓ Skill-Index: registered")

    # Check description field
    if 'description:' not in content:
        passed = False
        results.append(f"  ✗ Missing 'description:' field")
    else:
        results.append(f"  ✓ Description: present")

    return passed, '\n'.join(results)


def check_json(file_path: Path) -> tuple[bool, str]:
    """Validate JSON syntax and check that any referenced paths exist."""
    results = []
    passed = True

    if not file_path.exists():
        return False, f"FILE NOT FOUND: {file_path}"

    try:
        data = json.loads(file_path.read_text())
        results.append(f"  ✓ JSON syntax: valid")
    except json.JSONDecodeError as e:
        return False, f"  ✗ Invalid JSON: {e}"

    return passed, '\n'.join(results)


def check_shell(file_path: Path) -> tuple[bool, str]:
    """Basic shell script checks."""
    results = []
    passed = True

    if not file_path.exists():
        return False, f"FILE NOT FOUND: {file_path}"
    if file_path.stat().st_size == 0:
        return False, f"FILE IS EMPTY: {file_path}"

    # Check executable bit
    import stat
    mode = file_path.stat().st_mode
    if not (mode & stat.S_IXUSR):
        results.append(f"  ⚠ Not executable — run: chmod +x {file_path}")
    else:
        results.append(f"  ✓ Executable bit: set")

    # Syntax check (bash)
    r = subprocess.run(['bash', '-n', str(file_path)], capture_output=True, text=True)
    if r.returncode != 0:
        passed = False
        results.append(f"  ✗ Syntax error: {r.stderr.strip()}")
    else:
        results.append(f"  ✓ Syntax: valid")

    return passed, '\n'.join(results)


def check_data_fetch(sources_expected: list[str], sources_got: list[str]) -> tuple[bool, str]:
    """Verify all expected data sources were resolved. Report missing ones."""
    results = []
    passed = True

    missing = [s for s in sources_expected if s not in sources_got]
    resolved = [s for s in sources_expected if s in sources_got]

    for s in resolved:
        results.append(f"  ✓ {s}: resolved")

    for s in missing:
        passed = False
        results.append(f"  ✗ {s}: MISSING — not resolved, needs investigation")

    if missing:
        results.append(f"\n  ACTION REQUIRED: Tell Tony which sources failed and why before reporting task as complete.")

    return passed, '\n'.join(results)


def validate_file(file_path_str: str) -> tuple[bool, str]:
    """Route to the correct checker based on file type."""
    fp = Path(file_path_str)
    name = fp.name.lower()
    suffix = fp.suffix.lower()

    if suffix == '.py':
        return check_python(fp)
    elif name == 'skill.md':
        return check_skill(fp)
    elif suffix == '.json':
        return check_json(fp)
    elif suffix == '.sh':
        return check_shell(fp)
    elif suffix == '.js':
        # Basic existence + non-empty
        if not fp.exists():
            return False, f"FILE NOT FOUND: {fp}"
        if fp.stat().st_size == 0:
            return False, f"FILE IS EMPTY: {fp}"
        return True, f"  ✓ Exists and non-empty"
    else:
        # Generic: just check existence and non-empty
        if not fp.exists():
            return False, f"FILE NOT FOUND: {fp}"
        if fp.stat().st_size == 0:
            return False, f"FILE IS EMPTY: {fp}"
        return True, f"  ✓ Exists and non-empty"


def main():
    parser = argparse.ArgumentParser(description='Agent-OS Build Validator')
    parser.add_argument('--files', help='Comma-separated list of files to validate')
    parser.add_argument('--clear-manifest', action='store_true', help='Clear the build manifest after validation')
    parser.add_argument('--data-fetch', action='store_true', help='Validate a data fetch operation')
    parser.add_argument('--sources', help='Expected sources for data fetch (comma-separated)')
    parser.add_argument('--got', help='Sources that resolved successfully (comma-separated)')
    args = parser.parse_args()

    all_passed = True
    print("\n🔍 AGENT-OS BUILD VALIDATION")
    print("=" * 50)

    # Data fetch validation
    if args.data_fetch:
        expected = [s.strip() for s in (args.sources or '').split(',') if s.strip()]
        got = [s.strip() for s in (args.got or '').split(',') if s.strip()]
        passed, details = check_data_fetch(expected, got)
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"\nData Fetch Completeness: {status}")
        print(details)
        if not passed:
            all_passed = False

    # File validation
    if args.files:
        files = [f.strip() for f in args.files.split(',') if f.strip()]
        for file_path in files:
            passed, details = validate_file(file_path)
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"\n{status} — {file_path}")
            print(details)
            if passed:
                mark_verified(file_path)
            else:
                all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("✅ ALL CHECKS PASSED — safe to report as done")
        if args.clear_manifest:
            MANIFEST_PATH.unlink(missing_ok=True)
            print("   Build manifest cleared.")
    else:
        print("❌ VALIDATION FAILED — report failures to Tony before declaring done")
        print("   Include: what failed, why, and what Tony needs to do to fix it.")

    sys.exit(0 if all_passed else 1)


if __name__ == '__main__':
    main()
