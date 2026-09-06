#!/usr/bin/env python3
"""
assemble.py — Reimagined Realms — Universal Assembly Pipeline

Reads production-specific config from:
  <production_folder>/Production/assemble_config.json

  Required fields:
    suno_prompt    — Suno music description for this video
    suno_tags      — Suno style tags
    caption_line1  — First line of on-screen text hook
    caption_line2  — Second line of on-screen text hook

Phases:
  1. Trim/loop each clip to beatmap target duration (hard cap: 8s)
  2. Concatenate clips → raw_video.mp4
  3. Concatenate narration → narration.mp3
  4. Generate Suno music via kie.ai ($0.06)
  5. Mix audio: narration + ducked music (legacy — prefer render_video.py for full mix)
  6. Color grade + merge → graded.mp4
  7. Caption overlay → final.mp4

Usage:
  python3 assemble.py <production_folder>
  python3 assemble.py <production_folder> --skip-suno
  python3 assemble.py <production_folder> --phase 2 --stop-phase 2
  python3 assemble.py <production_folder> --overwrite --clips C20,C21
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests

# ── CTA / end-screen constants (locked 2026-07-04) ────────────────────────────

CTA_AUDIO_PATH = Path(
    "/Users/tonymacbook2025/Documents/Agent-OS/002_Content-Creation/Video_Editor/"
    "002_Channels/003_Reimagined-Realms/Brand_Assets/CTA/cta_follow_reimagined_realms.mp3"
)
CTA_GAP_SECONDS = 1.5  # silence between end of story narration and start of CTA audio


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

MAX_FINAL_DURATION_S = 8.0  # Hard cap — never exceed 8s per clip


def phase_trim_clips(beatmap, tmp, clips_dir, overwrite=False, only_clips=None):
    print("\n── Phase 1: Trim/loop clips ──")
    trimmed_dir = tmp / "trimmed"
    trimmed_dir.mkdir(exist_ok=True)

    all_beats = []
    for act in beatmap["acts"]:
        all_beats.extend(act["sub_beats"])

    trimmed_paths = []
    for beat in all_beats:
        clip_num = int(beat["clip"][1:])
        target = min(beat["target_final_duration_s"], MAX_FINAL_DURATION_S)

        candidates = list(clips_dir.glob(f"C{clip_num:02d}_*.mp4"))
        if not candidates:
            sys.exit(f"ERROR: No clip found for {beat['clip']}")
        src = candidates[0]

        out = trimmed_dir / f"C{clip_num:02d}.mp4"
        trimmed_paths.append(out)

        force = overwrite and (only_clips is None or beat["clip"].upper() in only_clips)
        if out.exists() and not force:
            print(f"  {out.name} already exists — skipping", flush=True)
            continue

        run([
            "ffmpeg", "-y",
            "-stream_loop", "-1",
            "-i", str(src),
            "-t", str(target),
            "-c:v", "libx264", "-crf", "18", "-preset", "fast",
            "-pix_fmt", "yuv420p",
            "-an",
            str(out)
        ], label=out.name)

    return trimmed_paths


# ── Phase 2: Concatenate clips ────────────────────────────────────────────────

def phase_concat_video(trimmed_paths, tmp, out_raw_video, overwrite=False):
    print("\n── Phase 2: Concatenate clips → raw_video.mp4 ──")
    if out_raw_video.exists() and not overwrite:
        print("  raw_video.mp4 exists — skipping")
        return

    concat_file = tmp / "concat_video.txt"
    with open(concat_file, "w") as f:
        for p in trimmed_paths:
            f.write(f"file '{p}'\n")

    run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(out_raw_video)
    ], label="concat video")


# ── Phase 3: Concatenate narration ───────────────────────────────────────────

# Never hard-concat VO. Every scene join gets a 20ms fade-out/fade-in pair so the
# mp3 splice can't pop (2026-09-02, Glass Frog 0003 Block C / P6). A fade *pair*
# (not a crossfade) keeps each scene's duration exact, so downstream timing that
# assumes narration length == sum(scene mp3 lengths) still holds.
NARRATION_JOIN_FADE_S = 0.02


def _audio_duration_s(path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    )
    return float(out.stdout.strip())


def build_narration_concat_filter(durations, fade_s: float = NARRATION_JOIN_FADE_S) -> str:
    """filter_complex for concatenating N narration mp3s with edge-faded joins.

    Each input is resampled to 44.1k mono, gets an `fade_s` fade-in at its head
    and an `fade_s` fade-out at its tail, then all are concatenated. The head fade
    on scene 1 and the tail fade on the final scene fall on the VO's own silent
    edges, so they're inaudible no-ops; every *internal* join is now a clean
    fade-out→fade-in instead of a raw bitstream splice.
    """
    n = len(durations)
    parts = []
    for i, d in enumerate(durations):
        fade_out_start = max(0.0, d - fade_s)
        parts.append(
            f"[{i}:a]aresample=44100,aformat=channel_layouts=mono,"
            f"afade=t=in:st=0:d={fade_s},"
            f"afade=t=out:st={fade_out_start:.4f}:d={fade_s}[a{i}]"
        )
    labels = "".join(f"[a{i}]" for i in range(n))
    parts.append(f"{labels}concat=n={n}:v=0:a=1[out]")
    return ";".join(parts)


def phase_concat_narration(audio_dir, tmp, out_narration):
    print("\n── Phase 3: Concatenate narration → narration.mp3 ──")
    if out_narration.exists():
        print("  narration.mp3 exists — skipping")
        return

    scene_files = sorted(audio_dir.glob("Scene_*.mp3"))
    if not scene_files:
        sys.exit("ERROR: No Scene_*.mp3 files found in Narration_Audio/")

    if not CTA_AUDIO_PATH.exists():
        sys.exit(
            f"ERROR: CTA audio asset not found: {CTA_AUDIO_PATH}\n"
            f"       This is a required channel-wide asset — see Brand_Assets/CTA/"
        )

    story_narration = tmp / "narration_story.mp3"

    durations = [_audio_duration_s(p) for p in scene_files]
    inputs = []
    for p in scene_files:
        inputs += ["-i", str(p)]

    run([
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", build_narration_concat_filter(durations),
        "-map", "[out]",
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(story_narration)
    ], label="concat narration (story only, edge-faded joins)")

    # Append gap + static CTA audio. Resample/normalize both inputs so the concat
    # filter works regardless of source sample rate — story narration is
    # concatenated ElevenLabs mp3s, CTA is a separately-rendered fixed asset.
    run([
        "ffmpeg", "-y",
        "-i", str(story_narration),
        "-i", str(CTA_AUDIO_PATH),
        "-filter_complex",
        f"[0:a]aresample=44100,aformat=channel_layouts=mono[a0];"
        f"anullsrc=r=44100:cl=mono:d={CTA_GAP_SECONDS}[gap];"
        f"[1:a]aresample=44100,aformat=channel_layouts=mono,"
        f"afade=t=in:st=0:d={NARRATION_JOIN_FADE_S}[a2];"
        f"[a0][gap][a2]concat=n=3:v=0:a=1[out]",
        "-map", "[out]",
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(out_narration)
    ], label="append CTA to narration")


# ── Phase 4: Generate Suno music ─────────────────────────────────────────────

def phase_suno_music(suno_prompt, suno_tags, out_music):
    print("\n── Phase 4: Generate Suno music ──")
    if out_music.exists():
        print("  music.mp3 exists — skipping")
        return

    print("  Requesting Suno track from kie.ai ($0.06)...")
    payload = {
        "prompt": suno_prompt,
        "customMode": True,
        "instrumental": True,
        "model": "V4",
        "style": suno_tags,
        "title": "Reimagined Realms Score",
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
                result_raw = block.get("resultJson", "")
                result = json.loads(result_raw) if result_raw else {}
                if isinstance(result, list):
                    # Suno returns array of URLs — pick longest by duration
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
            with open(out_music, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            print(f"  ✓ music.mp3 saved ({out_music.stat().st_size / 1_000_000:.1f} MB)")
            return
        elif state == "fail" or flag in [2, 3]:
            sys.exit(f"ERROR: Suno generation failed: {block}")
        else:
            print(f"  [{attempt+1}] {state} — waiting...", flush=True)

    sys.exit("ERROR: Suno timed out after 15 minutes")


# ── Phase 5: Mix audio ────────────────────────────────────────────────────────

def phase_mix_audio(out_narration, out_music, out_mixed):
    print("\n── Phase 5: Mix audio ──")
    if out_mixed.exists():
        print("  mixed_audio.mp3 exists — skipping")
        return

    run([
        "ffmpeg", "-y",
        "-i", str(out_narration),
        "-i", str(out_music),
        "-filter_complex",
        "[1:a]volume=0.14[music];[0:a][music]amix=inputs=2:duration=first:dropout_transition=3[mix]",
        "-map", "[mix]",
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(out_mixed)
    ], label="mix audio")


# ── Phase 6: Color grade + merge ─────────────────────────────────────────────

COLOR_GRADE = "eq=contrast=1.08:saturation=0.88:brightness=-0.02:gamma_r=1.04"


def phase_grade(out_raw_video, out_mixed, out_graded):
    print("\n── Phase 6: Color grade + merge ──")
    if out_graded.exists():
        print("  graded.mp4 exists — skipping")
        return

    run([
        "ffmpeg", "-y",
        "-i", str(out_raw_video),
        "-i", str(out_mixed),
        "-filter_complex",
        f"[0:v]{COLOR_GRADE}[graded]",
        "-map", "[graded]",
        "-map", "1:a",
        "-c:v", "libx264", "-crf", "17", "-preset", "slow",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(out_graded)
    ], label="grade + merge")


# ── Phase 7: Caption overlay ──────────────────────────────────────────────────

FONT_SIZE = 46
SHADOW = "shadowcolor=black@0.85:shadowx=3:shadowy=3"


def phase_caption(caption_line1, caption_line2, out_graded, out_final):
    print("\n── Phase 7: Caption overlay → final.mp4 ──")
    if out_final.exists():
        print("  final.mp4 exists — skipping")
        return

    caption_filter = (
        f"[0:v]"
        f"drawtext=text='{caption_line1}'"
        f":fontsize={FONT_SIZE}:fontcolor=white@0.95"
        f":x=(w-text_w)/2:y=h*0.82"
        f":{SHADOW}"
        f":enable='between(t,0.4,3.4)',"
        f"drawtext=text='{caption_line2}'"
        f":fontsize={FONT_SIZE}:fontcolor=white@0.95"
        f":x=(w-text_w)/2:y=h*0.82+{FONT_SIZE + 10}"
        f":{SHADOW}"
        f":enable='between(t,0.4,3.4)'"
        f"[v]"
    )

    run([
        "ffmpeg", "-y",
        "-i", str(out_graded),
        "-filter_complex", caption_filter,
        "-map", "[v]",
        "-map", "0:a",
        "-c:v", "libx264", "-crf", "17", "-preset", "slow",
        "-c:a", "copy",
        str(out_final)
    ], label="caption overlay")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Reimagined Realms universal assembly pipeline"
    )
    parser.add_argument("production_folder",
                        help="Path to production folder (e.g. .../0001_Pompeii_The_Escape)")
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

    root = Path(args.production_folder).resolve()
    if not root.exists():
        sys.exit(f"ERROR: Production folder not found: {root}")

    # Load production config
    config_path = root / "Production" / "assemble_config.json"
    if not config_path.exists():
        sys.exit(f"ERROR: Production config not found: {config_path}\n"
                 f"       Create Production/assemble_config.json with keys:\n"
                 f"       suno_prompt, suno_tags, caption_line1, caption_line2")
    config = json.loads(config_path.read_text())

    suno_prompt   = config["suno_prompt"]
    suno_tags     = config["suno_tags"]
    caption_line1 = config["caption_line1"]
    caption_line2 = config["caption_line2"]

    # Derive all paths from production root
    beatmap_path  = root / "Data" / "Beatmap.json"
    clips_dir     = root / "Video_Clips"
    audio_dir     = root / "Narration_Audio"
    tmp           = root / "Assembly"
    tmp.mkdir(exist_ok=True)

    out_raw_video = tmp / "raw_video.mp4"
    out_narration = tmp / "narration.mp3"
    out_music     = tmp / "music.mp3"
    out_mixed     = tmp / "mixed_audio.mp3"
    out_graded    = tmp / "graded.mp4"
    out_final     = root / "final.mp4"

    beatmap    = json.loads(beatmap_path.read_text())
    only_clips = None
    if args.overwrite and args.clips:
        only_clips = {c.strip().upper() for c in args.clips.split(",")}

    start = args.phase
    stop  = args.stop_phase

    trimmed_paths = None

    if start <= 1 <= stop:
        trimmed_paths = phase_trim_clips(
            beatmap, tmp, clips_dir,
            overwrite=args.overwrite, only_clips=only_clips
        )
    else:
        all_beats = []
        for act in beatmap["acts"]:
            all_beats.extend(act["sub_beats"])
        trimmed_paths = [tmp / "trimmed" / f"C{int(b['clip'][1:]):02d}.mp4" for b in all_beats]

    if start <= 2 <= stop:
        phase_concat_video(trimmed_paths, tmp, out_raw_video, overwrite=args.overwrite)

    if start <= 3 <= stop:
        phase_concat_narration(audio_dir, tmp, out_narration)

    if start <= 4 <= stop:
        if args.skip_suno:
            if not out_music.exists():
                sys.exit("ERROR: --skip-suno set but Assembly/music.mp3 not found")
            print("\n── Phase 4: Suno — skipped (using existing music.mp3) ──")
        else:
            phase_suno_music(suno_prompt, suno_tags, out_music)

    if start <= 5 <= stop:
        phase_mix_audio(out_narration, out_music, out_mixed)

    if start <= 6 <= stop:
        phase_grade(out_raw_video, out_mixed, out_graded)

    if start <= 7 <= stop:
        phase_caption(caption_line1, caption_line2, out_graded, out_final)

    if stop >= 7 and out_final.exists():
        print(f"\n✓ Assembly complete → {out_final}")
        size_mb = out_final.stat().st_size / 1_000_000
        print(f"  File size: {size_mb:.1f} MB")
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(out_final)],
            capture_output=True, text=True
        )
        dur = float(result.stdout.strip() or 0)
        print(f"  Duration: {dur:.1f}s ({int(dur//60)}:{int(dur%60):02d})")
    else:
        print(f"\n✓ Phases {start}–{stop} complete.")


if __name__ == "__main__":
    main()
