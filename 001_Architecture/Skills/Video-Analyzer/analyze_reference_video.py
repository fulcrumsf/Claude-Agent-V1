# analyze_reference_video.py
import argparse
import re
import subprocess
import time
from pathlib import Path

from google import genai
from google.genai import types

from config import GEMINI_API_KEY

NARRATIVE_PROMPT_TEMPLATE = """
Analyze this video scene-by-scene for the following pre-detected time ranges: {scene_ranges}

For each scene, describe (as one markdown section per scene, headed "## Scene N [start-end]"):
- Visual description (subjects, setting, framing)
- What is actually happening — narrative and historical/contextual meaning (era, role, activity — e.g. "POV of a shackled pyramid worker eating porridge," not just "person eating")
- Camera type and motion (e.g. static, handheld POV, tracking)
- Sound design cues audible or implied (foley, ambient, music, dialogue presence)
- Any on-screen text or overlay style (placement, sizing, drop shadow, timing)
"""

def download_video(url: str, out_dir: Path) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    video_path = out_dir / "Video.mp4"
    subprocess.run(
        ["yt-dlp", "-f", "mp4", "-o", str(video_path), url],
        check=True, capture_output=True,
    )
    return video_path

def detect_scenes(video_path: Path, threshold: float = 0.3) -> list[tuple[float, float]]:
    duration_result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)],
        check=True, capture_output=True, text=True,
    )
    duration = float(duration_result.stdout.strip())

    scene_result = subprocess.run(
        ["ffmpeg", "-i", str(video_path), "-filter:v",
         f"select='gt(scene,{threshold})',showinfo", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    cut_points = [float(m) for m in re.findall(r"pts_time:([\d.]+)", scene_result.stderr)]

    boundaries = [0.0] + sorted(cut_points) + [duration]
    return [(boundaries[i], boundaries[i + 1]) for i in range(len(boundaries) - 1)]

MAX_UPLOAD_POLL_ATTEMPTS = 30
UPLOAD_POLL_INTERVAL_SECONDS = 2

def analyze_video_narrative(video_path: Path, scenes: list[tuple[float, float]]) -> str:
    client = genai.Client(api_key=GEMINI_API_KEY)
    uploaded = client.files.upload(file=str(video_path))

    attempts = 0
    while uploaded.state.name == "PROCESSING":
        attempts += 1
        if attempts > MAX_UPLOAD_POLL_ATTEMPTS:
            raise TimeoutError(
                f"Gemini file upload did not become ACTIVE within "
                f"{MAX_UPLOAD_POLL_ATTEMPTS * UPLOAD_POLL_INTERVAL_SECONDS}s "
                f"(last state: {uploaded.state.name})"
            )
        time.sleep(UPLOAD_POLL_INTERVAL_SECONDS)
        uploaded = client.files.get(name=uploaded.name)

    if uploaded.state.name == "FAILED":
        raise RuntimeError(f"Gemini file upload failed: {getattr(uploaded, 'error', uploaded)}")

    scene_ranges = ", ".join(f"{start}s-{end}s" for start, end in scenes)
    prompt = NARRATIVE_PROMPT_TEMPLATE.format(scene_ranges=scene_ranges)

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=types.Content(parts=[
            types.Part(file_data=types.FileData(file_uri=str(uploaded.uri), mime_type=str(uploaded.mime_type))),
            types.Part(text=prompt),
        ]),
    )
    return response.text
