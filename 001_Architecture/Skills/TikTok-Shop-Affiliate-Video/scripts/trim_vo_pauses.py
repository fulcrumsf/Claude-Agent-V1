#!/usr/bin/env python3
"""
trim_vo_pauses.py — VO pause cleanup for TikTok Shop Affiliate Video pipeline.

Raw VO recordings often have overlong pauses (several seconds of dead air
between sentences). This shrinks every pause longer than MIN_TRIM_S down to a
natural conversational length, WITHOUT the two failure modes a naive hard cut
produces:

  1. Clicks/pops — a hard concat edit at a silence boundary creates a sample
     discontinuity that's audible as a pop. Fixed with a short (15ms) fade
     at every join.
  2. Clipped words — ffmpeg's silencedetect boundary can land a few ms inside
     a word's trailing/leading consonant (soft "t", "s", "sh" sounds are
     quiet enough to trigger the -30dB threshold before the word actually
     ends). Fixed with a safety padding margin (120ms) kept as real audio on
     both sides of every cut, so trims only ever remove genuine dead air.

Always run this BEFORE normalize_loudness.py (Step 5a.5) in the main skill
workflow — trim first, then normalize the trimmed file.

Usage:
    python3 trim_vo_pauses.py <input_vo.mp3> <output_trimmed.wav>

Verification (run after, on any new source, before trusting the output):
    # 1. Zero discontinuities check — count sample-to-sample jumps > 8000
    #    (out of a 16-bit ±32768 range) in the output; should be 0.
    # 2. Re-transcribe (whisper) the output and diff against the original
    #    transcript — every sentence should still be complete, no words
    #    should have gone missing at former pause boundaries.
"""
import sys
import subprocess
import re

TARGET_PAUSE_S = 0.35    # natural conversational pause to leave behind
MIN_TRIM_S = 0.5         # only shrink gaps longer than this
PAD_S = 0.12              # keep this much real audio on each side of a cut (safety margin)
FADE_S = 0.015            # 15ms fade at each join to prevent clicks


def get_duration(path):
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())


def detect_silences(path):
    result = subprocess.run(
        ["ffmpeg", "-i", path, "-af", "silencedetect=noise=-30dB:d=0.5", "-f", "null", "-"],
        capture_output=True, text=True
    )
    starts, ends = [], []
    for line in result.stderr.splitlines():
        if "silence_start:" in line:
            starts.append(float(line.split("silence_start:")[1].strip()))
        elif "silence_end:" in line:
            m = re.search(r"silence_end:\s*([\d.]+)", line)
            if m:
                ends.append(float(m.group(1)))
    return list(zip(starts, ends))


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 trim_vo_pauses.py <input_vo.mp3> <output_trimmed.wav>")
        sys.exit(1)

    in_path, out_path = sys.argv[1], sys.argv[2]
    duration = get_duration(in_path)
    silences = detect_silences(in_path)

    to_shrink = []
    for s, e in silences:
        e = min(e, duration)
        gap_len = e - s
        if gap_len < MIN_TRIM_S:
            continue
        if s <= 0.05:
            cut_end = max(0.0, e - PAD_S)
            to_shrink.append((0.0, cut_end, TARGET_PAUSE_S, "lead"))
        elif e >= duration - 0.05:
            cut_start = min(duration, s + PAD_S)
            to_shrink.append((cut_start, duration, 0.0, "trail"))
        else:
            cut_start = s + PAD_S
            cut_end = e - PAD_S
            if cut_end <= cut_start:
                continue
            to_shrink.append((cut_start, cut_end, TARGET_PAUSE_S, "mid"))

    filters = []
    concat_inputs = []
    cursor = 0.0
    idx = 0

    def add_speech_segment(a, b, fade_in, fade_out):
        nonlocal idx
        label = f"a{idx}"
        seg_len = b - a
        chain = f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS"
        fade_parts = []
        if fade_in and seg_len > FADE_S:
            fade_parts.append(f"afade=t=in:st=0:d={FADE_S}")
        if fade_out and seg_len > FADE_S:
            fade_parts.append(f"afade=t=out:st={max(0, seg_len - FADE_S)}:d={FADE_S}")
        if fade_parts:
            chain += "," + ",".join(fade_parts)
        chain += f"[{label}]"
        filters.append(chain)
        concat_inputs.append(f"[{label}]")
        idx += 1

    for cut_start, cut_end, keep_pause, kind in to_shrink:
        if cut_start > cursor:
            fade_in = cursor > 0.05
            add_speech_segment(cursor, cut_start, fade_in, True)
        if keep_pause > 0:
            label = f"s{idx}"
            filters.append(f"anullsrc=r=44100:cl=stereo:d={keep_pause}[{label}]")
            concat_inputs.append(f"[{label}]")
            idx += 1
        cursor = cut_end

    if cursor < duration:
        fade_in = cursor > 0.05
        add_speech_segment(cursor, duration, fade_in, False)

    filter_complex = ";".join(filters) + ";" + "".join(concat_inputs) + f"concat=n={len(concat_inputs)}:v=0:a=1[out]"

    cmd = ["ffmpeg", "-y", "-i", in_path, "-filter_complex", filter_complex,
           "-map", "[out]", out_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("FFMPEG ERROR:", result.stderr[-2000:])
        sys.exit(1)

    new_duration = get_duration(out_path)
    print(f"Original: {duration:.1f}s -> Trimmed: {new_duration:.1f}s")
    print(f"Shrunk {len(to_shrink)} gaps, {len(concat_inputs)} total segments")


if __name__ == "__main__":
    main()
