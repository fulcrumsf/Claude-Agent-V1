#!/usr/bin/env python3
"""
generate_suno_music.py — Suno background score generator for Anomalous Wild productions.

Duplicated from the Suno phase of Reimagined Realms' assemble.py (Phase 4) and
adapted into a standalone script for the Anomalous Wild channel. The Reimagined
Realms assemble.py itself is untouched.

Usage:
  python3 generate_suno_music.py <output_mp3_path> "<prompt>" "<style_tags>"

Suno returns ~2 tracks per generation. BOTH are saved next to <output_mp3_path>
as <stem>_v1.mp3 / <stem>_v2.mp3 (in API order), and <output_mp3_path> itself is
written as a copy of the longest one. A <stem>_suno.json sidecar records the
prompt, style tags, taskId, and per-track metadata — so the generation is always
reproducible / auditable (2026-09-03: Tony — always save both, always save the
prompt).
"""

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import requests


def kie_headers():
    result = subprocess.run(
        "source ~/.env-secrets && echo $KIE_API_KEY",
        shell=True, executable="/bin/zsh", capture_output=True, text=True,
    )
    key = result.stdout.strip()
    if not key:
        sys.exit("ERROR: KIE_API_KEY not found in ~/.env-secrets")
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}


def generate_suno_music(prompt, style_tags, out_music: Path, title="Anomalous Wild Score"):
    if out_music.exists():
        print(f"  {out_music.name} exists — skipping")
        return

    print("  Requesting Suno track from kie.ai ($0.06)...")
    payload = {
        "prompt": prompt,
        "customMode": True,
        "instrumental": True,
        "model": "V4",
        "style": style_tags,
        "title": title,
        "negativeTags": "vocals, lyrics, singing, speech",
        "callBackUrl": "https://example.com/callback",
    }

    resp = requests.post("https://api.kie.ai/api/v1/generate", headers=kie_headers(), json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    print(f"  API response: {data}")

    inner = data.get("data") or data
    task_id = inner.get("taskId") or inner.get("task_id")
    if not task_id:
        sys.exit(f"ERROR: No taskId in response: {data}")

    print(f"  taskId={task_id} — polling...")
    # NOTE: kie.ai's Suno endpoint uses a DIFFERENT poll path/response shape than the
    # generic image/video jobs API (confirmed against 007_Resource_Library/Docs/
    # Video_Editor/Kie.ai_API/Suno_Text_to_Music.md). Using /api/v1/jobs/recordInfo
    # here (as RR's assemble.py phase_suno_music does) returns "recordInfo is null" —
    # this looks like a latent bug in assemble.py too, flagged separately, not fixed there.
    status_url = f"https://api.kie.ai/api/v1/generate/record-info?taskId={task_id}"

    for attempt in range(60):
        time.sleep(15)
        poll_resp = requests.get(status_url, headers=kie_headers(), timeout=15).json()
        block = poll_resp.get("data") or poll_resp
        status = block.get("status")

        if status == "SUCCESS":
            suno_data = (block.get("response") or {}).get("sunoData", [])
            if not suno_data:
                sys.exit(f"ERROR: SUCCESS but no sunoData: {block}")

            out_music = Path(out_music)
            out_music.parent.mkdir(parents=True, exist_ok=True)
            stem = out_music.with_suffix("")

            # Save EVERY track Suno returned (usually 2), in API order.
            saved = []
            for i, track in enumerate(suno_data, start=1):
                url = track.get("audioUrl")
                if not url:
                    print(f"  ⚠ track {i} has no audioUrl, skipping")
                    continue
                dest = Path(f"{stem}_v{i}.mp3")
                print(f"  Downloading track {i} ({track.get('duration', '?')}s) → {dest.name}")
                r = requests.get(url, stream=True, timeout=120)
                r.raise_for_status()
                with open(dest, "wb") as f:
                    for chunk in r.iter_content(8192):
                        f.write(chunk)
                saved.append((dest, track))

            if not saved:
                sys.exit(f"ERROR: no downloadable tracks in result: {block}")

            # out_music itself = a copy of the longest track (the default pick).
            best_dest, _ = max(saved, key=lambda st: st[1].get("duration", 0))
            shutil.copyfile(best_dest, out_music)

            # Sidecar: prompt + style + taskId + per-track metadata — always saved.
            sidecar = Path(f"{stem}_suno.json")
            sidecar.write_text(json.dumps({
                "prompt": prompt,
                "style_tags": style_tags,
                "title": title,
                "negative_tags": "vocals, lyrics, singing, speech",
                "model": "V4",
                "task_id": task_id,
                "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "default_pick": best_dest.name,
                "tracks": [
                    {"file": d.name, "suno_id": t.get("id"),
                     "duration_s": t.get("duration"), "audio_url": t.get("audioUrl"),
                     "title": t.get("title")}
                    for d, t in saved
                ],
            }, indent=2))

            for d, t in saved:
                print(f"  ✓ {d.name} ({d.stat().st_size / 1_000_000:.1f} MB, {t.get('duration', '?')}s)")
            print(f"  ✓ {out_music.name} = copy of {best_dest.name} (longest)")
            print(f"  ✓ {sidecar.name} (prompt + metadata)")
            return
        elif status == "FAILED":
            sys.exit(f"ERROR: Suno generation failed: {block}")
        else:
            print(f"  [{attempt+1}] {status or 'processing'} — waiting...", flush=True)

    sys.exit("ERROR: Suno timed out after 15 minutes")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit("Usage: generate_suno_music.py <output_mp3_path> \"<prompt>\" \"<style_tags>\"")
    generate_suno_music(sys.argv[2], sys.argv[3], Path(sys.argv[1]))
