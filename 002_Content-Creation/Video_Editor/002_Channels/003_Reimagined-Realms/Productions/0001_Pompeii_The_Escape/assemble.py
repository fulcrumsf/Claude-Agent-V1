#!/usr/bin/env python3
"""
assemble.py — Pompeii: The Escape — Final Assembly Pipeline

Phases:
  1. Trim/loop each clip to beatmap target duration
  2. Concatenate clips → raw_video.mp4
  3. Concatenate narration → narration.mp3
  4. Generate Suno music via kie.ai ($0.06)
  5. Mix audio: narration + ducked music
  6. Color grade + merge → graded.mp4
  7. Caption overlay → final.mp4

Usage:
  python3 assemble.py                    # full run
  python3 assemble.py --skip-suno        # use existing music.mp3
  python3 assemble.py --phase 5          # resume from phase N
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests

# ── Paths ─────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent
BEATMAP = ROOT / "Data" / "Beatmap.json"
CLIPS_DIR = ROOT / "Video_Clips"
AUDIO_DIR = ROOT / "Narration_Audio"
TMP = ROOT / "Assembly"
TMP.mkdir(exist_ok=True)

OUT_RAW_VIDEO = TMP / "raw_video.mp4"
OUT_NARRATION = TMP / "narration.mp3"
OUT_MUSIC = TMP / "music.mp3"
OUT_MIXED = TMP / "mixed_audio.mp3"
OUT_GRADED = TMP / "graded.mp4"
OUT_FINAL = ROOT / "final.mp4"

# ── Env loader ────────────────────────────────────────────────────────────────

def _load_env_secrets():
    result = subprocess.run(
        "source ~/.env-secrets && echo $KIE_API_KEY",
        shell=True, executable="/bin/zsh", capture_output=True, text=True
    )
    key = result.stdout.strip()
    if key:
        os.environ["KIE_API_KEY"] = key
    return key


def kie_headers():
    key = os.environ.get("KIE_API_KEY") or _load_env_secrets()
    if not key:
        sys.exit("ERROR: KIE_API_KEY not found in environment or ~/.env-secrets")
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}


# ── ffmpeg helper ─────────────────────────────────────────────────────────────

def run(cmd, label=""):
    print(f"  {'[' + label + '] ' if label else ''}{' '.join(str(c) for c in cmd[:6])}...", flush=True)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr[-2000:])
        sys.exit(f"ERROR: ffmpeg failed for {label}")


# ── Phase 1: Trim / loop clips ────────────────────────────────────────────────

def phase_trim_clips(beatmap, overwrite=False, only_clips=None):
    print("\n── Phase 1: Trim/loop clips ──")
    trimmed_dir = TMP / "trimmed"
    trimmed_dir.mkdir(exist_ok=True)

    all_beats = []
    for act in beatmap["acts"]:
        all_beats.extend(act["sub_beats"])

    trimmed_paths = []
    for beat in all_beats:
        clip_num = int(beat["clip"][1:])
        target = min(beat["target_final_duration_s"], 8.0)

        # Find matching file
        candidates = list(CLIPS_DIR.glob(f"C{clip_num:02d}_*.mp4"))
        if not candidates:
            sys.exit(f"ERROR: No clip found for {beat['clip']}")
        src = candidates[0]

        out = trimmed_dir / f"C{clip_num:02d}.mp4"
        trimmed_paths.append(out)

        force = overwrite and (only_clips is None or beat["clip"].upper() in only_clips)
        if out.exists() and not force:
            print(f"  {out.name} already exists — skipping", flush=True)
            continue

        # stream_loop handles both trim (target < actual) and loop (target > actual)
        run([
            "ffmpeg", "-y",
            "-stream_loop", "-1",
            "-i", str(src),
            "-t", str(target),
            "-c:v", "libx264", "-crf", "18", "-preset", "fast",
            "-pix_fmt", "yuv420p",
            "-an",   # clips have no audio
            str(out)
        ], label=out.name)

    return trimmed_paths


# ── Phase 2: Concatenate clips ────────────────────────────────────────────────

def phase_concat_video(trimmed_paths, overwrite=False):
    print("\n── Phase 2: Concatenate clips → raw_video.mp4 ──")
    if OUT_RAW_VIDEO.exists() and not overwrite:
        print("  raw_video.mp4 exists — skipping")
        return

    concat_file = TMP / "concat_video.txt"
    with open(concat_file, "w") as f:
        for p in trimmed_paths:
            f.write(f"file '{p}'\n")

    run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(OUT_RAW_VIDEO)
    ], label="concat video")


# ── Phase 3: Concatenate narration ───────────────────────────────────────────

def phase_concat_narration():
    print("\n── Phase 3: Concatenate narration → narration.mp3 ──")
    if OUT_NARRATION.exists():
        print("  narration.mp3 exists — skipping")
        return

    scene_files = sorted(AUDIO_DIR.glob("Scene_*.mp3"))
    if not scene_files:
        sys.exit("ERROR: No Scene_*.mp3 files found in Narration_Audio/")

    concat_file = TMP / "concat_audio.txt"
    with open(concat_file, "w") as f:
        for p in scene_files:
            f.write(f"file '{p}'\n")

    run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(OUT_NARRATION)
    ], label="concat narration")


# ── Phase 4: Generate Suno music ─────────────────────────────────────────────

SUNO_PROMPT = (
    "Cinematic orchestral documentary score, ancient Rome, 79 AD, "
    "somber and majestic, strings and brass, building tension then melancholic resolution, "
    "no lyrics, no vocals, pure instrumental"
)
SUNO_TAGS = "cinematic orchestral dark historical documentary instrumental strings brass ancient"


def phase_suno_music():
    print("\n── Phase 4: Generate Suno music ──")
    if OUT_MUSIC.exists():
        print("  music.mp3 exists — skipping")
        return

    print("  Requesting Suno track from kie.ai ($0.06)...")
    payload = {
        "prompt": SUNO_PROMPT,
        "customMode": True,
        "instrumental": True,
        "model": "V4",
        "style": SUNO_TAGS,
        "title": "Pompeii The Escape Score",
        "negativeTags": "vocals, lyrics, singing, speech",
        "callBackUrl": "https://example.com/callback",
    }

    resp = requests.post(
        "https://api.kie.ai/api/v1/generate",
        headers=kie_headers(), json=payload, timeout=30
    )
    resp.raise_for_status()
    data = resp.json()
    print(f"  API response: {data}")

    # Response may nest data under a 'data' key or return taskId at root
    inner = data.get("data") or data
    task_id = inner.get("taskId") or inner.get("task_id")
    if not task_id:
        sys.exit(f"ERROR: No taskId in response: {data}")

    print(f"  taskId={task_id} — polling...")
    status_url = f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}"

    for attempt in range(60):
        time.sleep(15)
        poll_resp = requests.get(status_url, headers=kie_headers(), timeout=15).json()
        block = poll_resp.get("data") or poll_resp
        state = block.get("state")
        flag = block.get("successFlag")

        if state == "success" or flag == 1:
            url = None
            try:
                # Suno returns a JSON array of MP3 URLs in resultJson
                result_raw = block.get("resultJson", "")
                result = json.loads(result_raw) if result_raw else {}
                if isinstance(result, list):
                    # Pick the longest track (highest LRA = most dynamic) by probing all URLs
                    best_url, best_dur = None, 0
                    for candidate_url in result:
                        try:
                            probe = subprocess.run(
                                ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                                 "-of", "csv=p=0", candidate_url],
                                capture_output=True, text=True, timeout=15
                            )
                            dur = float(probe.stdout.strip() or 0)
                            if dur > best_dur:
                                best_dur, best_url = dur, candidate_url
                        except Exception:
                            pass
                    url = best_url or (result[0] if result else None)
                else:
                    url = (result.get("resultUrls") or [None])[0] or result.get("url")
            except Exception:
                pass
            url = url or block.get("url")
            if not url:
                sys.exit(f"ERROR: No URL in result: {block}")

            print(f"  Downloading from {url}")
            r = requests.get(url, stream=True, timeout=120)
            r.raise_for_status()
            with open(OUT_MUSIC, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            print(f"  ✓ music.mp3 saved ({OUT_MUSIC.stat().st_size / 1_000_000:.1f} MB)")
            return
        elif state == "fail" or flag in [2, 3]:
            sys.exit(f"ERROR: Suno generation failed: {block}")
        else:
            print(f"  [{attempt+1}] {state} — waiting...", flush=True)

    sys.exit("ERROR: Suno timed out after 15 minutes")


# ── Phase 5: Mix audio ────────────────────────────────────────────────────────

def phase_mix_audio():
    print("\n── Phase 5: Mix audio ──")
    if OUT_MIXED.exists():
        print("  mixed_audio.mp3 exists — skipping")
        return

    # Duck music to 14% volume under narration; music fades out at end of narration
    run([
        "ffmpeg", "-y",
        "-i", str(OUT_NARRATION),
        "-i", str(OUT_MUSIC),
        "-filter_complex",
        "[1:a]volume=0.14[music];[0:a][music]amix=inputs=2:duration=first:dropout_transition=3[mix]",
        "-map", "[mix]",
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(OUT_MIXED)
    ], label="mix audio")


# ── Phase 6: Color grade + merge audio ───────────────────────────────────────

def phase_grade():
    print("\n── Phase 6: Color grade + merge ──")
    if OUT_GRADED.exists():
        print("  graded.mp4 exists — skipping")
        return

    # Subtle cinematic grade: slight contrast lift, desaturate a touch (ash/dust feel)
    # eq: contrast=1.08, saturation=0.88, brightness=-0.02, gamma_r=1.04 (slight warm)
    run([
        "ffmpeg", "-y",
        "-i", str(OUT_RAW_VIDEO),
        "-i", str(OUT_MIXED),
        "-filter_complex",
        "[0:v]eq=contrast=1.08:saturation=0.88:brightness=-0.02:gamma_r=1.04[graded]",
        "-map", "[graded]",
        "-map", "1:a",
        "-c:v", "libx264", "-crf", "17", "-preset", "slow",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(OUT_GRADED)
    ], label="grade + merge")


# ── Phase 7: Caption overlay ──────────────────────────────────────────────────

CAPTION_LINE1 = r"18\,000 people. 2\,000 bodies."
CAPTION_LINE2 = r"Where did the rest go?"

FONT_SIZE = 46
SHADOW = "shadowcolor=black@0.85:shadowx=3:shadowy=3"


def phase_caption():
    print("\n── Phase 7: Caption overlay → final.mp4 ──")
    if OUT_FINAL.exists():
        print("  final.mp4 exists — skipping")
        return

    # Two caption lines stacked, shown 0.4s–3.4s
    caption_filter = (
        f"[0:v]"
        f"drawtext=text='{CAPTION_LINE1}'"
        f":fontsize={FONT_SIZE}:fontcolor=white@0.95"
        f":x=(w-text_w)/2:y=h*0.82"
        f":{SHADOW}"
        f":enable='between(t,0.4,3.4)',"
        f"drawtext=text='{CAPTION_LINE2}'"
        f":fontsize={FONT_SIZE}:fontcolor=white@0.95"
        f":x=(w-text_w)/2:y=h*0.82+{FONT_SIZE + 10}"
        f":{SHADOW}"
        f":enable='between(t,0.4,3.4)'"
        f"[v]"
    )

    run([
        "ffmpeg", "-y",
        "-i", str(OUT_GRADED),
        "-filter_complex", caption_filter,
        "-map", "[v]",
        "-map", "0:a",
        "-c:v", "libx264", "-crf", "17", "-preset", "slow",
        "-c:a", "copy",
        str(OUT_FINAL)
    ], label="caption overlay")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-suno", action="store_true",
                        help="Skip Suno generation (use existing Assembly/music.mp3)")
    parser.add_argument("--phase", type=int, default=1,
                        help="Start from phase N (1–7)")
    parser.add_argument("--stop-phase", type=int, default=7,
                        help="Stop after phase N (inclusive)")
    parser.add_argument("--overwrite", action="store_true",
                        help="Force re-trim and re-concat even if output files already exist")
    parser.add_argument("--clips", type=str, default=None,
                        help="Comma-separated clip IDs to overwrite (e.g. C20,C21). "
                             "Only meaningful with --overwrite. Omit to overwrite all clips.")
    args = parser.parse_args()

    only_clips = None
    if args.overwrite and args.clips:
        only_clips = {c.strip().upper() for c in args.clips.split(",")}

    beatmap = json.loads(BEATMAP.read_text())
    beatmap = dict(beatmap)  # already a dict from json.loads

    start = args.phase

    trimmed_paths = None

    stop = args.stop_phase

    if start <= 1 <= stop:
        trimmed_paths = phase_trim_clips(beatmap, overwrite=args.overwrite, only_clips=only_clips)
    else:
        # Rebuild path list for later phases
        all_beats = []
        for act in beatmap["acts"]:
            all_beats.extend(act["sub_beats"])
        trimmed_paths = [TMP / "trimmed" / f"C{int(b['clip'][1:]):02d}.mp4" for b in all_beats]

    if start <= 2 <= stop:
        phase_concat_video(trimmed_paths, overwrite=args.overwrite)

    if start <= 3 <= stop:
        phase_concat_narration()

    if start <= 4 <= stop:
        if args.skip_suno:
            if not OUT_MUSIC.exists():
                sys.exit("ERROR: --skip-suno set but Assembly/music.mp3 not found")
            print("\n── Phase 4: Suno — skipped (using existing music.mp3) ──")
        else:
            phase_suno_music()

    if start <= 5 <= stop:
        phase_mix_audio()

    if start <= 6 <= stop:
        phase_grade()

    if start <= 7 <= stop:
        phase_caption()

    if stop >= 7 and OUT_FINAL.exists():
        print(f"\n✓ Assembly complete → {OUT_FINAL}")
        size_mb = OUT_FINAL.stat().st_size / 1_000_000
        print(f"  File size: {size_mb:.1f} MB")
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(OUT_FINAL)],
            capture_output=True, text=True
        )
        dur = float(result.stdout.strip() or 0)
        print(f"  Duration: {dur:.1f}s ({int(dur//60)}:{int(dur%60):02d})")
    else:
        print(f"\n✓ Phases 1–{stop} complete.")


if __name__ == "__main__":
    main()
