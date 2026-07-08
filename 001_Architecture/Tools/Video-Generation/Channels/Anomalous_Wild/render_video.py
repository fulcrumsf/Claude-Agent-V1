#!/usr/bin/env python3
"""
render_video.py — Versioned video renderer for Reimagined Realms productions.

Every render gets a version folder (V1, V2, V3...). Audio tracks are kept
completely separate — stems, narration, and music are individual files that
get mixed at render time. This means you can always bring any track into a
video editor and adjust levels independently.

Version folder contains:
  Assembly/
    V1/
      0001_Pompeii_The_Escape_V1.mp4   final video (all tracks baked in)
      stems_mix.mp3                     SFX bed — independent track copy
      narration.mp3                     VO — independent track copy
      render_notes.md                   what's in this version, levels used
    V2/
      0001_Pompeii_The_Escape_V2.mp4   (+ music added)
      stems_mix.mp3
      narration.mp3
      music.mp3                         Suno — independent track copy
      render_notes.md
    RENDER_LOG.md                       master index of all versions

Usage:
  # V1 — stems + narration only
  python3 render_video.py <production_folder> \\
      --stems Assembly/stems_mix.mp3 \\
      --narration Assembly/narration.mp3

  # V2 — add Suno music
  python3 render_video.py <production_folder> \\
      --stems Assembly/stems_mix.mp3 \\
      --narration Assembly/narration.mp3 \\
      --music Assembly/music.mp3 \\
      --music-vol 0.12 \\
      --note "Added Suno music bed"

  # Force version tag
  python3 render_video.py <production_folder> --stems ... --narration ... --version V3
"""

import argparse
import datetime
import shutil
import subprocess
import sys
from pathlib import Path


COLOR_GRADE = "eq=contrast=1.08:saturation=0.88:brightness=-0.02:gamma_r=1.04"


def next_version(assembly_dir: Path) -> str:
    existing = [d.name for d in assembly_dir.iterdir() if d.is_dir() and d.name.startswith("V")]
    nums = []
    for name in existing:
        try:
            nums.append(int(name[1:]))
        except ValueError:
            pass
    return f"V{max(nums) + 1}" if nums else "V1"


def probe_duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    )
    return float(result.stdout.strip() or 0)


def update_render_log(assembly_dir: Path, version: str, note: str, tracks: list[str], outputs: list[str]):
    log_path  = assembly_dir / "RENDER_LOG.md"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    entry  = f"\n## {version} — {timestamp}\n"
    entry += f"**Note:** {note}\n\n"
    entry += f"**Tracks in mix:** {', '.join(tracks)}\n\n"
    entry += "**Outputs:**\n"
    for o in outputs:
        entry += f"- `{o}`\n"
    entry += "\n---"

    if log_path.exists():
        log_path.write_text(log_path.read_text() + entry)
    else:
        log_path.write_text(
            "# Render Log\n\nEach version is a complete snapshot. "
            "All audio tracks are saved separately per version.\n" + entry
        )


def resolve(production_root: Path, path_str: str) -> Path:
    p = Path(path_str)
    return p if p.is_absolute() else production_root / p


def main():
    parser = argparse.ArgumentParser(description="Versioned video renderer — keeps all audio tracks separate")
    parser.add_argument("production_folder")
    parser.add_argument("--video",       default="Assembly/raw_video.mp4")
    parser.add_argument("--stems",       default="Assembly/stems_mix.mp3",
                        help="SFX stems track (default: Assembly/stems_mix.mp3)")
    parser.add_argument("--narration",   default="Assembly/narration.mp3",
                        help="Narration/VO track (default: Assembly/narration.mp3)")
    parser.add_argument("--music",       default=None,
                        help="Music track (optional, e.g. Assembly/music.mp3)")
    parser.add_argument("--stems-vol",   type=float, default=1.0,
                        help="Stems volume multiplier (default: 1.0 — already LUFS-corrected)")
    parser.add_argument("--narration-vol", type=float, default=1.0,
                        help="Narration volume multiplier (default: 1.0)")
    parser.add_argument("--music-vol",   type=float, default=0.12,
                        help="Music volume multiplier (default: 0.12 — sits under VO)")
    parser.add_argument("--version",     default=None,
                        help="Force version tag e.g. V2 (default: auto-increment)")
    parser.add_argument("--note",        default="",
                        help="Short note describing what changed in this version")
    parser.add_argument("--duck",         action="store_true",
                        help="Duck stems under narration via sidechain compression (~4dB reduction when VO speaks)")
    parser.add_argument("--no-grade",    action="store_true",
                        help="Skip color grade (faster, for audio-only iteration)")
    args = parser.parse_args()

    production_root = Path(args.production_folder).resolve()
    assembly_dir    = production_root / "Assembly"
    assembly_dir.mkdir(exist_ok=True)

    video_path     = resolve(production_root, args.video)
    stems_path     = resolve(production_root, args.stems)
    narration_path = resolve(production_root, args.narration)
    music_path     = resolve(production_root, args.music) if args.music else None

    for label, p in [("video", video_path), ("stems", stems_path), ("narration", narration_path)]:
        if not p.exists():
            sys.exit(f"ERROR: {label} not found: {p}")
    if music_path and not music_path.exists():
        sys.exit(f"ERROR: music not found: {music_path}")

    version     = args.version or next_version(assembly_dir)
    version_dir = assembly_dir / version
    version_dir.mkdir(exist_ok=True)

    prod_name = production_root.name
    video_out = version_dir / f"{prod_name}_{version}.mp4"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    has_music = music_path is not None
    tracks_in_mix = ["stems", "narration"] + (["music"] if has_music else [])
    note = args.note or f"Tracks: {', '.join(tracks_in_mix)}"

    print(f"\n=== Render — {prod_name} | {version} ===")
    print(f"    Stems:     {stems_path.name}  vol={args.stems_vol}")
    print(f"    Narration: {narration_path.name}  vol={args.narration_vol}")
    if has_music:
        print(f"    Music:     {music_path.name}  vol={args.music_vol}")
    print(f"    Grade:     {'off' if args.no_grade else 'on'}")
    print(f"    Output:    {version}/{video_out.name}\n")

    # Build ffmpeg filter_complex
    inputs = [
        "-i", str(video_path),
        "-i", str(stems_path),
        "-i", str(narration_path),
    ]
    if has_music:
        inputs += ["-i", str(music_path)]

    if args.no_grade:
        video_filter = "[0:v]null[graded]"
        vcodec = ["-c:v", "copy"]
    else:
        video_filter = f"[0:v]{COLOR_GRADE}[graded]"
        vcodec = ["-c:v", "libx264", "-crf", "17", "-preset", "slow"]

    n_audio = 3 if has_music else 2
    audio_filters = [
        f"[1:a]volume={args.stems_vol}[stems_leveled]",
        f"[2:a]volume={args.narration_vol}[vo_leveled]",
    ]
    if has_music:
        audio_filters.append(f"[3:a]volume={args.music_vol}[music]")

    if args.duck:
        # Split VO into two copies: one triggers sidechain compression, one goes into the mix.
        # sidechaincompress ducks stems ~4dB when VO is speaking.
        # threshold=0.015 catches even quiet VO; ratio=4 gives ~4dB reduction;
        # attack=150ms smooth entry, release=800ms gradual return (natural feel).
        audio_filters.append("[vo_leveled]asplit=2[vo_sidechain][vo_mix]")
        audio_filters.append(
            "[stems_leveled][vo_sidechain]"
            "sidechaincompress=threshold=0.015:ratio=4:attack=150:release=800:makeup=1"
            "[stems_ducked]"
        )
        stems_out = "[stems_ducked]"
        vo_out    = "[vo_mix]"
    else:
        stems_out = "[stems_leveled]"
        vo_out    = "[vo_leveled]"

    mix_inputs = f"{stems_out}{vo_out}" + ("[music]" if has_music else "")
    audio_filters.append(f"{mix_inputs}amix=inputs={n_audio}:normalize=0[mix]")

    filter_complex = ";".join([video_filter] + audio_filters)

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[graded]",
        "-map", "[mix]",
        *vcodec,
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(video_out),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr[-3000:])
        sys.exit("ERROR: ffmpeg render failed")

    size_mb = video_out.stat().st_size / 1_000_000
    dur     = probe_duration(video_out)
    print(f"  ✓ {video_out.name} ({size_mb:.1f} MB, {dur:.1f}s)")

    # Copy each source track independently into the version folder
    copied_tracks = []
    for src in [stems_path, narration_path] + ([music_path] if has_music else []):
        dst = version_dir / src.name
        shutil.copy2(src, dst)
        print(f"  ✓ {dst.name} copied ({dst.stat().st_size / 1_000_000:.1f} MB)")
        copied_tracks.append(dst.name)

    # Write render_notes.md
    notes  = f"# {version} — {prod_name}\n\n"
    notes += f"**Rendered:** {timestamp}\n"
    notes += f"**Note:** {note}\n\n"
    notes += "## Audio tracks (all independent — import individually into any editor)\n\n"
    notes += "| File | Role | Volume |\n|------|------|--------|\n"
    notes += f"| `{stems_path.name}` | SFX bed (LUFS-normalized, 21 per-scene clips) | {args.stems_vol} |\n"
    notes += f"| `{narration_path.name}` | Narration / VO | {args.narration_vol} |\n"
    if has_music:
        notes += f"| `{music_path.name}` | Music bed (Suno) | {args.music_vol} |\n"
    notes += f"\n## Final video\n\n| File | Size | Duration |\n|------|------|----------|\n"
    notes += f"| `{video_out.name}` | {size_mb:.1f} MB | {dur:.1f}s |\n\n"
    notes += f"## Color grade\n\n`{COLOR_GRADE}`\n"
    (version_dir / "render_notes.md").write_text(notes)
    print(f"  ✓ render_notes.md written")

    outputs = [f"{version}/{video_out.name}"] + [f"{version}/{t}" for t in copied_tracks]
    update_render_log(assembly_dir, version, note, tracks_in_mix, outputs)
    print(f"  ✓ RENDER_LOG.md updated\n")
    print(f"=== {version} complete — Assembly/{version}/ ===")


if __name__ == "__main__":
    main()
