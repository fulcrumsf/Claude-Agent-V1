"""
CC0/Public domain footage downloader for Anomalous Wild productions.
Uses yt-dlp for YouTube sources and requests for direct URLs.

Usage:
  python3 tools/fetch_cc0_footage.py outputs/001_anomalous_wild/bioluminescence_weapon/cc0_manifest.json
"""
import os
import sys
import json
import subprocess
import requests
from pathlib import Path
from dotenv import load_dotenv

HOME_SECRETS = Path.home() / ".env-secrets"
load_dotenv(HOME_SECRETS)

YT_DLP = "/opt/homebrew/bin/yt-dlp"


def download_youtube(url: str, output_path: Path, max_height: int = 1080) -> bool:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out_template = str(output_path.parent / "video_raw.%(ext)s")

    cmd = [
        YT_DLP,
        "-f", f"bestvideo[height<={max_height}]+bestaudio/best[height<={max_height}]",
        "--merge-output-format", "mp4",
        "-o", out_template,
        "--no-playlist",
        url,
    ]

    print(f"  → Downloading from YouTube: {url[:60]}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ✗ yt-dlp failed: {result.stderr[:300]}")
        return False

    # Rename to video_raw.mp4 if needed
    raw = output_path.parent / "video_raw.mp4"
    if raw.exists():
        print(f"  ✓ Saved: {raw}")
        return True

    print(f"  ✗ Expected video_raw.mp4 not found after download")
    return False


def download_direct(url: str, output_path: Path) -> bool:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"  → Downloading direct: {url[:60]}...")
    resp = requests.get(url, timeout=120, stream=True)
    if not resp.ok:
        print(f"  ✗ HTTP {resp.status_code}")
        return False
    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"  ✓ Saved: {output_path} ({size_mb:.1f} MB)")
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tools/fetch_cc0_footage.py <cc0_manifest.json>")
        sys.exit(1)

    manifest_path = Path(sys.argv[1])
    if not manifest_path.exists():
        print(f"File not found: {manifest_path}")
        sys.exit(1)

    manifest = json.loads(manifest_path.read_text())
    items = manifest.get("footage", [])

    print(f"\n=== CC0 Footage Downloader ===")
    print(f"Items: {len(items)}")
    print()

    success, skipped, failed = 0, 0, []

    for item in items:
        scene_id = item["scene_id"]
        url = item["url"]
        output_folder = Path(item["output_folder"])
        source_type = item.get("source_type", "youtube")  # youtube | direct
        license_type = item.get("license", "unknown")

        print(f"[{scene_id}] {license_type} — {url[:60]}...")

        # Check if video already exists for this scene
        existing = list(output_folder.glob("video*.mp4"))
        if existing:
            print(f"  ✓ Already have footage, skipping")
            skipped += 1
            continue

        if source_type == "youtube":
            ok = download_youtube(url, output_folder / "video_raw.mp4")
        else:
            ok = download_direct(url, output_folder / "video_raw.mp4")

        if ok:
            success += 1
        else:
            failed.append(scene_id)

    print(f"\n=== Done ===")
    print(f"Downloaded: {success} | Skipped (existing): {skipped} | Failed: {failed}")


if __name__ == "__main__":
    main()
