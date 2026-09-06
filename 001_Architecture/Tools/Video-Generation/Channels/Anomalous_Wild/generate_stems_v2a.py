#!/usr/bin/env python3
"""
generate_stems_v2a.py — Video-to-audio (v2a) ambience/SFX bed generator.

EXPERIMENTAL alternative to generate_stems.py (ElevenLabs text->SFX). Instead of
describing each stem blind, this feeds actual picture-locked video segments through
a video-to-audio model (fal.ai Mirelo SFX v1.6 by default) so the generated Foley /
ambience is conditioned on on-screen motion, then crossfade-concatenates the
per-segment audio into one continuous bed on the master timeline.

Non-destructive: only reads the source render; writes everything under a work dir.

Reads:   Data/v2a_segment_map.json   (list of {id, start_s, end_s, prompt})
Input:   --source <picture-locked render>  (audio is ignored / stripped)
Outputs: <workdir>/seg_XX.mp4         (Mirelo result videos)
         <workdir>/seg_XX.wav         (extracted, leveled audio)
         <workdir>/v2a_bed.mp3        (full crossfaded bed, matched to timeline)

Usage:
  python3 generate_stems_v2a.py <production_folder> \
      --source Renders/FULL13_RevisionRound1_R2_xfades.mp4 \
      --workdir Assembly/V2A [--segments s1 s3] [--model mirelo] [--skip-existing]

fal.ai Mirelo SFX v1.6 (mirelo-ai/sfx1.6/video-to-video):
  duration <= 60s (values >10 use sliding-window extended generation),
  num_samples 1-4, optional text_prompt. Billed in GPU compute-seconds (cheap).
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path.home() / ".env-secrets")
# ~/.env-secrets stores the fal key as FAL.AI_API_KEY (dot preserved by dotenv);
# fal_client expects FAL_KEY.
_FAL_KEY = os.getenv("FAL_KEY") or os.getenv("FAL_AI_API_KEY") or os.getenv("FAL.AI_API_KEY")
if _FAL_KEY:
    os.environ["FAL_KEY"] = _FAL_KEY

import fal_client  # noqa: E402

MODELS = {
    "mirelo": "mirelo-ai/sfx1.6/video-to-video",
    "mmaudio": "fal-ai/mmaudio-v2",
}


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise RuntimeError(f"cmd failed: {' '.join(map(str, cmd))}\n{r.stderr[-1500:]}")
    return r


def ffprobe_dur(path):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", str(path)])
    return float(r.stdout.strip())


def cut_segment(source, start_s, end_s, out_path):
    """Re-encoded cut, video only (audio stripped), downscaled + bitrate-capped so
    the upload to fal is fast. Mirelo only needs the motion, not 1080p detail."""
    dur = round(end_s - start_s, 3)
    run(["ffmpeg", "-y", "-ss", f"{start_s:.3f}", "-i", str(source), "-t", f"{dur:.3f}",
         "-an", "-vf", "scale=1280:-2", "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "23", "-maxrate", "4M", "-bufsize", "8M", "-g", "60",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out_path)])
    return dur


def mirelo_sfx(model_id, video_url, prompt, duration_s, seed=None):
    args = {
        "video_url": video_url,
        "duration": min(round(duration_s, 2), 60.0),
        "num_samples": 1,
    }
    if prompt:
        args["text_prompt"] = prompt
    if seed is not None:
        args["seed"] = seed
    result = fal_client.subscribe(model_id, arguments=args, with_logs=False)
    return _first_media_url(result)


def _first_media_url(result):
    """Pull a media URL out of a fal result, tolerating dict/list/str shapes."""
    for key in ("video", "audio", "video_with_audio", "output"):
        v = result.get(key)
        if isinstance(v, str) and v.startswith("http"):
            return v
        if isinstance(v, dict) and v.get("url"):
            return v["url"]
        if isinstance(v, list) and v and isinstance(v[0], dict) and v[0].get("url"):
            return v[0]["url"]
    for key in ("videos", "audios", "outputs"):
        v = result.get(key)
        if isinstance(v, list) and v:
            if isinstance(v[0], dict) and v[0].get("url"):
                return v[0]["url"]
            if isinstance(v[0], str):
                return v[0]
    raise RuntimeError(f"no media url in fal response: {result!r}")


def mmaudio(model_id, video_url, prompt, duration_s, seed=None):
    args = {"video_url": video_url, "duration": min(round(duration_s, 2), 30.0)}
    if prompt:
        args["prompt"] = prompt
    if seed is not None:
        args["seed"] = seed
    result = fal_client.subscribe(model_id, arguments=args, with_logs=False)
    return _first_media_url(result)


def download(url, out_path):
    import requests
    r = requests.get(url, timeout=300)
    r.raise_for_status()
    out_path.write_bytes(r.content)


def extract_level_audio(in_media, out_wav, target_lufs=-24.0):
    """Extract audio, loudnorm to a review-friendly bed level, 48k stereo wav."""
    run(["ffmpeg", "-y", "-i", str(in_media), "-vn",
         "-af", f"loudnorm=I={target_lufs}:TP=-3:LRA=11",
         "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(out_wav)])


def crossfade_concat(wavs, out_path, xfade_s=0.35):
    if len(wavs) == 1:
        run(["ffmpeg", "-y", "-i", str(wavs[0]), "-c:a", "libmp3lame", "-b:a", "192k",
             str(out_path)])
        return
    inputs = []
    for w in wavs:
        inputs += ["-i", str(w)]
    # chain acrossfade
    filt = []
    prev = "[0:a]"
    for i in range(1, len(wavs)):
        out = f"[a{i}]" if i < len(wavs) - 1 else "[out]"
        filt.append(f"{prev}[{i}:a]acrossfade=d={xfade_s}:c1=tri:c2=tri{out}")
        prev = f"[a{i}]"
    run(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filt),
         "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "192k", str(out_path)])


def fit_duration(in_mp3, target_s, out_mp3):
    """Pad with silence or trim so the bed exactly matches the timeline length."""
    cur = ffprobe_dur(in_mp3)
    if abs(cur - target_s) < 0.05:
        run(["cp", str(in_mp3), str(out_mp3)])
        return
    if cur < target_s:
        run(["ffmpeg", "-y", "-i", str(in_mp3), "-af",
             f"apad=whole_dur={target_s:.3f},afade=t=out:st={target_s-0.5:.3f}:d=0.5",
             "-c:a", "libmp3lame", "-b:a", "192k", str(out_mp3)])
    else:
        run(["ffmpeg", "-y", "-i", str(in_mp3), "-t", f"{target_s:.3f}", "-af",
             f"afade=t=out:st={target_s-0.5:.3f}:d=0.5",
             "-c:a", "libmp3lame", "-b:a", "192k", str(out_mp3)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("production_folder")
    ap.add_argument("--source", required=True, help="picture-locked render (audio ignored)")
    ap.add_argument("--segment-map", default="Data/v2a_segment_map.json")
    ap.add_argument("--workdir", default="Assembly/V2A")
    ap.add_argument("--model", choices=list(MODELS), default="mirelo")
    ap.add_argument("--segments", nargs="+", help="only these segment ids")
    ap.add_argument("--skip-existing", action="store_true",
                    help="reuse seg_XX.mp4 already downloaded")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--bed-lufs", type=float, default=-24.0)
    args = ap.parse_args()

    root = Path(args.production_folder).resolve()
    src = (root / args.source) if not Path(args.source).is_absolute() else Path(args.source)
    if not src.exists():
        src = Path(args.source).resolve()
    if not src.exists():
        sys.exit(f"source not found: {src}")

    seg_map_path = root / args.segment_map
    segs = json.loads(seg_map_path.read_text())["segments"]
    if args.segments:
        segs = [s for s in segs if s["id"] in args.segments]

    wd = root / args.workdir
    wd.mkdir(parents=True, exist_ok=True)

    if not os.environ.get("FAL_KEY"):
        sys.exit("FAL_KEY missing — check ~/.env-secrets")

    model_id = MODELS[args.model]
    timeline_end = max(s["end_s"] for s in json.loads(seg_map_path.read_text())["segments"])
    print(f"=== v2a bed — {args.model} ({model_id}) — {len(segs)} segments ===")

    leveled = []
    for s in segs:
        sid = s["id"]
        seg_mp4 = wd / f"seg_{sid}.mp4"
        seg_wav = wd / f"seg_{sid}.wav"
        dur = s["end_s"] - s["start_s"]
        print(f"\n[{sid}] {s['start_s']:.2f}–{s['end_s']:.2f}s ({dur:.2f}s)")

        if not (args.skip_existing and seg_mp4.exists()):
            cut = wd / f"_cut_{sid}.mp4"
            actual = cut_segment(src, s["start_s"], s["end_s"], cut)
            print(f"  cut {actual:.2f}s → uploading")
            url = fal_client.upload_file(str(cut))
            print(f"  → {args.model} …")
            fn = mmaudio if args.model == "mmaudio" else mirelo_sfx
            out_url = fn(model_id, url, s.get("prompt", ""), dur, seed=args.seed)
            download(out_url, seg_mp4)
            cut.unlink(missing_ok=True)
            print(f"  saved {seg_mp4.name} ({seg_mp4.stat().st_size // 1000} KB)")
        else:
            print(f"  SKIP gen — {seg_mp4.name} exists")

        extract_level_audio(seg_mp4, seg_wav, target_lufs=args.bed_lufs)
        leveled.append(seg_wav)

    if args.segments:
        print("\n(partial run — not rebuilding full bed)")
        return

    raw_bed = wd / "v2a_bed_raw.mp3"
    final_bed = wd / "v2a_bed.mp3"
    crossfade_concat(leveled, raw_bed)
    fit_duration(raw_bed, timeline_end, final_bed)
    print(f"\n✓ bed: {final_bed}  ({ffprobe_dur(final_bed):.2f}s, target {timeline_end:.2f}s)")


if __name__ == "__main__":
    main()
