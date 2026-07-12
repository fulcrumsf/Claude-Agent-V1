#!/usr/bin/env python3
"""
check_tos_freshness.py — Phase 2 live freshness check.

The 18 local TOS files have no captured/source-date metadata, so they cannot
be assumed current. This pulls TikTok's currently-published policy pages
(via the Firecrawl CLI, per the workspace's CLI-first rule) and diffs them
against the last snapshot, flagging anything that changed for manual ledger
reconciliation. Never auto-edits Compliance-Ledger.md — a human/agent reviews
the diff and updates the ledger with a new dated entry.

Usage:
  python3 check_tos_freshness.py <neon_parcel_folder> [--category Health]
"""
import json
import subprocess
import sys
from datetime import date, datetime
from difflib import unified_diff
from pathlib import Path

ALWAYS_ESCALATE_CATEGORIES = {"health", "beauty", "weight-management", "supplements", "skincare"}
DEFAULT_THRESHOLD_DAYS = 14


def should_refresh(last_verified: str | None, category: str | None, threshold_days: int = DEFAULT_THRESHOLD_DAYS) -> bool:
    if category:
        normalized = category.strip().lower()
        if any(keyword in normalized for keyword in ALWAYS_ESCALATE_CATEGORIES):
            return True
    if not last_verified:
        return True
    last_date = datetime.fromisoformat(last_verified).date()
    return (date.today() - last_date).days > threshold_days


def diff_snapshots(old_text: str, new_text: str) -> list:
    diff = unified_diff(
        old_text.splitlines(keepends=True),
        new_text.splitlines(keepends=True),
        lineterm="",
    )
    return [line for line in diff if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))]


def fetch_snapshot(url: str) -> str:
    result = subprocess.run(
        ["firecrawl", "scrape", url, "--only-main-content", "--format", "markdown"],
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f"firecrawl scrape failed for {url}: {result.stderr[:300]}")
    return result.stdout


def load_last_verified(freshness_log_path: Path) -> str | None:
    if not freshness_log_path.exists():
        return None
    for line in reversed(freshness_log_path.read_text().splitlines()):
        if line.startswith("## ") and "VERIFIED" in line:
            return line[3:].split(" — ")[0].strip()
    return None


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: check_tos_freshness.py <neon_parcel_folder> [--category Health]")
    neon_parcel_dir = Path(sys.argv[1]).resolve()
    category = None
    if "--category" in sys.argv:
        category = sys.argv[sys.argv.index("--category") + 1]

    freshness_log = neon_parcel_dir / "Compliance-Freshness-Log.md"
    last_verified = load_last_verified(freshness_log)

    if not should_refresh(last_verified, category):
        print(f"Ledger last verified {last_verified}, within {DEFAULT_THRESHOLD_DAYS}-day threshold. Skipping live check.")
        return

    sources_path = neon_parcel_dir / "Compliance-Sources.json"
    sources = json.loads(sources_path.read_text())

    snapshot_dir = neon_parcel_dir / "Compliance-Snapshots" / date.today().isoformat()
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    changed = []
    failed = []
    for knowledge_id, url in sources.items():
        print(f"Fetching {url} ...")
        try:
            new_text = fetch_snapshot(url)
        except RuntimeError as e:
            print(f"  FAILED: {e}")
            failed.append((knowledge_id, url, str(e)))
            continue

        new_path = snapshot_dir / f"{knowledge_id}.md"
        new_path.write_text(new_text)

        prior_snapshots = sorted((neon_parcel_dir / "Compliance-Snapshots").glob(f"*/{knowledge_id}.md"))
        prior_snapshots = [p for p in prior_snapshots if p != new_path]
        if prior_snapshots:
            old_text = prior_snapshots[-1].read_text()
            diffs = diff_snapshots(old_text, new_text)
            if diffs:
                changed.append((knowledge_id, url, diffs))

    succeeded_count = len(sources) - len(failed)
    with open(freshness_log, "a") as f:
        if succeeded_count > 0:
            f.write(f"\n## {date.today().isoformat()} — VERIFIED\n")
        else:
            f.write(f"\n## {date.today().isoformat()} — ALL FETCHES FAILED\n")
        f.write(f"Checked {len(sources)} source URL(s) ({succeeded_count} succeeded, {len(failed)} failed).\n")
        if failed:
            f.write(f"**{len(failed)} source(s) failed to fetch — retry needed:**\n")
            for knowledge_id, url, error in failed:
                f.write(f"- `{knowledge_id}` ({url}): {error[:200]}\n")
        if changed:
            f.write(f"**{len(changed)} source(s) changed — review required before trusting the ledger for affected rules:**\n")
            for knowledge_id, url, diffs in changed:
                f.write(f"- `{knowledge_id}` ({url}): {len(diffs)} changed line(s)\n")
        if not changed and not failed:
            f.write("No changes detected.\n")

    if failed:
        print(f"WARNING: {len(failed)} source(s) failed to fetch. See {freshness_log}")
    if changed:
        print(f"REVIEW NEEDED: {len(changed)} source(s) changed. See {freshness_log}")
    if not changed and not failed:
        print("No changes detected. Ledger confirmed current.")


if __name__ == "__main__":
    main()
