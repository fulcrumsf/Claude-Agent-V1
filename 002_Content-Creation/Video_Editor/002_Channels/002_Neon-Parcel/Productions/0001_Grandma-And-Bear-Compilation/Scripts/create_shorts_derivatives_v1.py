#!/usr/bin/env python3
"""Create a temporary Shorts review candidate from the approved master."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "Assembly/Versions/v5/Neon-Parcel-Grandma-And-Bear-Compilation-Music-Endscreen-Review-v1.mp4"
OUT_DIR = ROOT / "Shorts/Versions/v2"

SHORT = {
    "part": 3,
    "title_lines": ["Ridiculous Grandma and Bear", "Encounters, Part Three"],
    "start_s": 97.512,
    "duration_s": 32.256,
    "shots": ["Shot-10", "Shot-11", "Shot-12"],
    "file": "Neon-Parcel-Grandma-And-Bear-Short-Part-3-Test-v2.mp4",
}


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def probe_duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(result.stdout.strip())


def make_overlay(title_lines: list[str], output: Path) -> None:
    if output.exists():
        return
    image = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    # Centered, brief, and kept inside platform-safe margins.
    draw.rounded_rectangle((95, 710, 985, 930), radius=24, fill=(0, 0, 0, 120))
    font_path = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
    fonts = [ImageFont.truetype(str(font_path), 58), ImageFont.truetype(str(font_path), 70)]
    y_values = [750, 835]
    for line, font, y in zip(title_lines, fonts, y_values):
        bbox = draw.textbbox((0, 0), line, font=font)
        x = (1080 - (bbox[2] - bbox[0])) / 2
        draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
    image.save(output)


def make_filter() -> str:
    # Crop x positions are after scaling the 1920x1080 master to 3414x1920.
    # These points use denser visual sampling: open on the introduced subject,
    # then glide toward the revealed/punchline subject or the interaction group.
    x_expr = (
        "if(lt(t,2.5),420,"
        "if(lt(t,7.0),420+(t-2.5)*(1020-420)/4.5,"
        "if(lt(t,10.08),1020+(t-7.0)*(1540-1020)/3.08,"
        "if(lt(t,13.0),1900,"
        "if(lt(t,17.5),1900-(t-13.0)*(1900-1460)/4.5,"
        "if(lt(t,20.16),1460,"
        "if(lt(t,23.5),1320,"
        "if(lt(t,27.5),1320-(t-23.5)*(1320-1120)/4.0,1120))))))))"
    )
    return f"scale=-2:1920,crop=1080:1920:x='{x_expr}':y=0,fps=30,setsar=1"


def main() -> None:
    if not MASTER.is_file():
        raise FileNotFoundError(MASTER)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = OUT_DIR / "shorts-manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = {
            "version": "v1",
            "source_master": str(MASTER),
            "source_master_duration_s": round(probe_duration(MASTER), 3),
            "policy": {
                "aspect_ratio": "9:16",
                "target_duration_seconds": 60,
                "target_is_soft": True,
                "complete_clip_boundaries_only": True,
                "opening_overlay_seconds": 1,
                "exclude_longform_end_screen": True,
            },
            "shorts": [],
        }
    output = OUT_DIR / SHORT["file"]
    overlay = OUT_DIR / f"Short-Part-{SHORT['part']}-Overlay-v2.png"
    if output.exists():
        raise FileExistsError(output)
    make_overlay(SHORT["title_lines"], overlay)
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-y",
            "-ss",
            f"{SHORT['start_s']:.3f}",
            "-t",
            f"{SHORT['duration_s']:.3f}",
            "-i",
            str(MASTER),
            "-loop",
            "1",
            "-i",
            str(overlay),
            "-filter_complex",
            f"[0:v]{make_filter()}[base];[1:v]trim=duration=1,setpts=PTS-STARTPTS[ov];[base][ov]overlay=0:0:enable='lt(t,1)'[vout]",
            "-map",
            "[vout]",
            "-map",
            "0:a",
            "-t",
            f"{SHORT['duration_s']:.3f}",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            str(output),
        ]
    )
    manifest["shorts"].append(
        {
            "part": SHORT["part"],
            "title_overlay": " ".join(SHORT["title_lines"]),
            "file": str(output),
            "shots": SHORT["shots"],
            "source_start_s": SHORT["start_s"],
            "duration_s": round(probe_duration(output), 3),
            "status": "review_candidate",
            "overlay_file": str(overlay),
            "reframe": "manual shot-window crop inspired by auto-reframe",
        }
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(OUT_DIR)


if __name__ == "__main__":
    main()
