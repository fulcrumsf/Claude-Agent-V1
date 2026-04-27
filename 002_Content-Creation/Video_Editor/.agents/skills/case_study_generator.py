"""
Case Study Generator
====================
Fetches a YouTube video's metadata, downloads it, extracts 3 screenshots (beginning/middle/end),
sends the video to Gemini for a content case study analysis, and saves everything into the
appropriate channel's case_studies/ folder.

Usage:
    python tools/case_study_generator.py <youtube_url> <channel_folder>

    channel_folder options:
        001_anomalous_wild, 002_neonparcel, 003_reimaginedrealms, 004_kingdoms_and_conquerors,
        005_glyphary, 006_polyoculis, 007_robotto_gato, 008_borednomad, 009_unomascreative,
        010_room_portal, 011_ikigaidigitalstudio, 012_business_origin_stories

Example:
    python tools/case_study_generator.py "https://youtube.com/watch?v=XXXX" 001_anomalous_wild
"""

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import requests
from google import genai
from google.genai import types

# Add tools dir to path for config import
sys.path.insert(0, str(Path(__file__).parent))
from config import GEMINI_API_KEY, YOUTUBE_DATA_API_KEY

BASE_DIR = Path(__file__).parent.parent
CHANNELS_DIR = BASE_DIR / "references" / "channels"

CHANNEL_FOLDERS = [
    "001_anomalous_wild",
    "002_neonparcel",
    "003_reimaginedrealms",
    "004_kingdoms_and_conquerors",
    "005_glyphary",
    "006_polyoculis",
    "007_robotto_gato",
    "008_borednomad",
    "009_unomascreative",
    "010_room_portal",
    "011_ikigaidigitalstudio",
    "012_business_origin_stories",
]

CASE_STUDY_PROMPT = """
Analyze this YouTube video as a case study for a content creator looking to understand what makes it successful and how to apply its lessons.

Provide a detailed, structured breakdown covering:

## 1. HOOK ANALYSIS (First 15 Seconds)
- Exactly what happens in the first 3 seconds — word for word if spoken
- Why this hook works: curiosity gap / shock / identity / visual
- What keeps the viewer watching past the hook
- Hook type: Question / Statement / Visual / Promise / Pattern interrupt

## 2. CONTENT STRUCTURE
- Outline the full video arc with timestamps (approx): intro → build → payoff → CTA
- How many "micro-payoffs" are delivered before the final reveal
- Pacing rhythm: fast/slow, talking-speed, cut frequency
- Any re-engagement moments used mid-video (e.g., "but wait...", "here's where it gets weird")

## 3. WHY IT WORKS (Retention Mechanics)
- Primary retention driver: education / entertainment / novelty / emotion / identity
- What psychological hooks are used (curiosity gap, FOMO, parasocial, aspiration, outrage)
- What makes a viewer want to share this specifically
- What makes them want to watch the NEXT video immediately after

## 4. TITLE & THUMBNAIL ANALYSIS
- What does the title promise? Does the video deliver?
- What visual element in the thumbnail generates the click?
- Thumbnail strategy: curiosity / emotion / authority / contrast / character
- What makes this title/thumbnail combination click-worthy vs generic

## 5. PRODUCTION ANALYSIS
- Visual style: animation / live / AI / screen record / talking head / hybrid
- Audio quality and music strategy — how it serves the mood
- Graphics, text overlays, b-roll — what role they play
- Budget estimate: low / medium / high production

## 6. WHAT TO REPLICATE
- Top 3 specific techniques to apply directly to a similar video
- What format or structure could be templated and reused across videos
- What tone or voice makes this creator feel trustworthy or compelling

## 7. WHAT TO AVOID
- Any weaknesses or moments where the video loses momentum
- Anything that wouldn't translate well to AI-generated content

## 8. AI PRODUCTION NOTES
- If recreating the style with AI tools (Kling, Veo 3, ElevenLabs, etc.), what would the prompts need to capture?
- What visual elements would be hardest to replicate with AI?
- Recommended production pipeline for a similar video

## 9. VIRAL SCORE (1–10 each)
- Hook strength: /10
- Retention structure: /10
- Shareability: /10
- Production quality: /10
- Overall case study score: /10

## 10. ONE-LINE SUMMARY
A single sentence capturing the core lesson this video teaches about YouTube success.
"""


def slugify(text: str) -> str:
    """Convert a string to a safe folder name."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "_", text)
    text = re.sub(r"^-+|-+$", "", text)
    return str(text)[:80]  # type: ignore[index]


def extract_video_id(url: str) -> str | None:
    """Extract YouTube video ID from URL."""
    patterns = [
        r"(?:v=|youtu\.be/|shorts/)([a-zA-Z0-9_-]{11})",
        r"embed/([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def fetch_youtube_metadata(video_id: str) -> dict:
    """Fetch video metadata from YouTube Data API v3."""
    if not YOUTUBE_DATA_API_KEY:
        print("WARNING: YOUTUBE_DATA_API_KEY not set — skipping metadata fetch.")
        return {}

    params = {
        "part": "snippet,statistics,contentDetails",
        "id": video_id,
        "key": YOUTUBE_DATA_API_KEY,
    }
    resp = requests.get("https://www.googleapis.com/youtube/v3/videos", params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    if not data.get("items"):
        print(f"WARNING: No YouTube metadata found for video ID: {video_id}")
        return {}

    item = data["items"][0]
    snippet = item.get("snippet", {})
    stats = item.get("statistics", {})
    details = item.get("contentDetails", {})

    # Parse ISO 8601 duration to seconds
    duration_iso = details.get("duration", "PT0S")
    duration_seconds = parse_iso_duration(duration_iso)

    return {
        "title": snippet.get("title", ""),
        "channel_name": snippet.get("channelTitle", ""),
        "channel_id": snippet.get("channelId", ""),
        "published_at": snippet.get("publishedAt", ""),
        "description": snippet.get("description", "")[:800],  # trim long descriptions
        "tags": snippet.get("tags", []),
        "category_id": snippet.get("categoryId", ""),
        "view_count": int(stats.get("viewCount", 0)),
        "like_count": int(stats.get("likeCount", 0)),
        "comment_count": int(stats.get("commentCount", 0)),
        "duration_seconds": duration_seconds,
        "duration_iso": duration_iso,
    }


def parse_iso_duration(iso: str) -> int:
    """Parse ISO 8601 duration (PT4M33S) to total seconds."""
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso)
    if not match:
        return 0
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds


def download_video(url: str, output_dir: Path) -> Path | None:
    """Download video using yt-dlp. Returns path to downloaded file."""
    output_template = str(output_dir / "%(id)s.%(ext)s")
    cmd = [
        "yt-dlp",
        "--format", "bestvideo[height<=720]+bestaudio/best[height<=720]",
        "--merge-output-format", "mp4",
        "--output", output_template,
        "--no-playlist",
        "--quiet",
        url,
    ]
    print(f"Downloading video (720p max)...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"yt-dlp error: {result.stderr}")
        return None

    # Find the downloaded file
    for f in output_dir.iterdir():
        if f.suffix in (".mp4", ".mkv", ".webm"):
            return f
    return None


def extract_frames(video_path: Path, duration_seconds: int, output_dir: Path) -> dict[str, Path]:
    """Extract frames using FFmpeg.

    Long-form (> 60s): 10 frames evenly distributed from 5% to 95%.
    Short-form (≤ 60s): 3 frames at 10%, 50%, 85%.
    """
    ffmpeg = "/opt/homebrew/bin/ffmpeg"
    if not Path(ffmpeg).exists():
        ffmpeg = "ffmpeg"  # fall back to PATH

    frames = {}
    if duration_seconds > 60:
        positions = [0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95]
        labels = [f"frame_{i+1:02d}" for i in range(len(positions))]
        timestamps = {label: int(duration_seconds * pct) for label, pct in zip(labels, positions)}
    else:
        timestamps = {
            "beginning": int(duration_seconds * 0.10),
            "middle": int(duration_seconds * 0.50),
            "end": int(duration_seconds * 0.85),
        }

    for label, ts in timestamps.items():
        out_path = output_dir / f"screenshot_{label}.jpg"
        cmd = [
            ffmpeg, "-y",
            "-ss", str(ts),
            "-i", str(video_path),
            "-frames:v", "1",
            "-q:v", "2",
            str(out_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 and out_path.exists():
            frames[label] = out_path
            print(f"  Frame extracted: {label} (t={ts}s) → {out_path.name}")
        else:
            print(f"  WARNING: Failed to extract {label} frame: {str(result.stderr)[:200]}")  # type: ignore[index]

    return frames


def analyze_with_gemini(url: str) -> str:
    """Send YouTube URL to Gemini for case study analysis."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set. Add GEMINI_API_KEY or GOOGLE_API_KEY to your .env file.")

    client = genai.Client(api_key=GEMINI_API_KEY)

    print("Sending video to Gemini for case study analysis (20–90 seconds)...")

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=types.Content(
            parts=[
                types.Part(file_data=types.FileData(file_uri=url)),
                types.Part(text=CASE_STUDY_PROMPT),
            ]
        ),
    )
    return response.text


def build_case_study_md(url: str, video_id: str, meta: dict, gemini_analysis: str, frames: dict) -> str:
    """Assemble the final case_study.md content."""
    frame_lines = [
        f"![{label.replace('_', ' ').title()}](screenshot_{label}.jpg)"
        for label in frames
    ]
    frame_section = "\n".join(frame_lines) + ("\n" if frame_lines else "")

    tags_str = ", ".join(meta.get("tags", [])[:15]) or "—"

    lines = [
        f"# Case Study: {meta.get('title', url)}",
        "",
        "## Video Metadata",
        "",
        f"| Field | Value |",
        f"|---|---|",
        f"| **URL** | {url} |",
        f"| **Video ID** | {video_id} |",
        f"| **Channel** | {meta.get('channel_name', '—')} |",
        f"| **Published** | {meta.get('published_at', '—')[:10]} |",
        f"| **Duration** | {meta.get('duration_iso', '—')} ({meta.get('duration_seconds', 0)}s) |",
        f"| **Views** | {meta.get('view_count', 0):,} |",
        f"| **Likes** | {meta.get('like_count', 0):,} |",
        f"| **Comments** | {meta.get('comment_count', 0):,} |",
        f"| **Tags** | {tags_str} |",
        "",
        "### Description (excerpt)",
        "",
        f"> {meta.get('description', '—')}",
        "",
        "---",
        "",
        "## Screenshots",
        "",
        frame_section,
        "---",
        "",
        "## Gemini Case Study Analysis",
        "",
        gemini_analysis,
    ]
    return "\n".join(lines)


def run(url: str, channel_folder: str) -> None:
    # Validate channel
    if channel_folder not in CHANNEL_FOLDERS:
        print(f"ERROR: Unknown channel folder '{channel_folder}'")
        print(f"Valid options: {', '.join(CHANNEL_FOLDERS)}")
        sys.exit(1)

    # Extract video ID
    video_id = extract_video_id(url)
    if not video_id:
        print(f"ERROR: Could not extract video ID from URL: {url}")
        sys.exit(1)
    assert video_id is not None  # narrowing for type checker

    print(f"\n=== Case Study Generator ===")
    print(f"Video ID : {video_id}")
    print(f"Channel  : {channel_folder}")
    print()

    # Fetch metadata
    print("Fetching YouTube metadata...")
    meta = fetch_youtube_metadata(video_id)
    title = meta.get("title") or f"video_{video_id}"
    duration_seconds = meta.get("duration_seconds", 0)
    print(f"Title    : {title}")
    print(f"Duration : {duration_seconds}s")

    # Build output folder
    folder_name = slugify(title) or video_id
    case_study_dir = CHANNELS_DIR / channel_folder / "case_studies" / folder_name
    case_study_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output   : {case_study_dir}")
    print()

    # Gemini analysis (uses the YouTube URL directly — no download needed for this step)
    gemini_analysis = analyze_with_gemini(url)

    # Download video + extract frames
    frames = {}
    if duration_seconds > 0:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            print("\nDownloading video for frame extraction...")
            video_file = download_video(url, tmp_path)
            if video_file:
                print("Extracting frames...")
                frames = extract_frames(video_file, duration_seconds, case_study_dir)
            else:
                print("WARNING: Video download failed — skipping frame extraction.")
    else:
        print("WARNING: Duration unknown — skipping frame extraction.")

    # Build and save case_study.md
    md_content = build_case_study_md(url, video_id, meta, gemini_analysis, frames)
    md_path = case_study_dir / "case_study.md"
    md_path.write_text(md_content, encoding="utf-8")
    print(f"\nCase study saved: {md_path}")

    # Summary
    print("\n=== Done ===")
    print(f"Folder   : {case_study_dir}")
    print(f"Files    :")
    for f in sorted(case_study_dir.iterdir()):
        size = f.stat().st_size
        print(f"  {f.name} ({size:,} bytes)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a YouTube video case study with screenshots and Gemini analysis."
    )
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument(
        "channel_folder",
        help=f"Channel folder name. Options: {', '.join(CHANNEL_FOLDERS)}",
    )
    args = parser.parse_args()
    run(args.url, args.channel_folder)
