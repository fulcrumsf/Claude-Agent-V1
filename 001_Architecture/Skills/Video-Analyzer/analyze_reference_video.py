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
- Full verbatim transcript of any spoken narration, dialogue, or voiceover in this scene, word for word (write "no speech" if none) — this matters most for tutorial/instructional videos where the spoken explanation IS the content
- Any on-screen text or overlay style (placement, sizing, drop shadow, timing)
- Continuity and physics anomalies: character identity/appearance morphing mid-shot (face, build, clothing, or props changing inconsistently), directionally impossible or contradictory motion (e.g. a subject appearing to walk backwards relative to the direction the shot establishes, or reversing travel direction without cause), limb/object warping or duplication, and any other physically implausible movement. Call out the specific timestamp within the scene where each anomaly occurs, and describe exactly what looks wrong.
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
        config=types.GenerateContentConfig(max_output_tokens=65536),
    )

    finish_reason = response.candidates[0].finish_reason if response.candidates else None
    if finish_reason is not None and finish_reason.name == "MAX_TOKENS":
        print(
            f"⚠️  Gemini response was truncated (hit MAX_TOKENS at 65536). "
            f"Analysis is incomplete — raise --threshold to reduce scene count, "
            f"or split the video into shorter segments.",
        )

    return response.text or ""

def write_analysis_md(out_dir: Path, scenes: list[tuple[float, float]], gemini_output: str) -> Path:
    out_dir = Path(out_dir)
    lines = [
        f"_ffmpeg detected {len(scenes)} raw scene cuts; "
        f"see Gemini's narrative breakdown below for the actual scene structure._",
        "",
        gemini_output,
    ]

    analysis_path = out_dir / "ANALYSIS.md"
    analysis_path.write_text("\n".join(lines))
    return analysis_path


def main(url: str, out: str, threshold: float = 0.3) -> None:
    out_dir = Path(out)
    video_path = download_video(url, out_dir)
    scenes = detect_scenes(video_path, threshold)
    gemini_output = analyze_video_narrative(video_path, scenes)
    write_analysis_md(out_dir, scenes, gemini_output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze a reference video's style, pacing, and narrative context.")
    parser.add_argument("url", help="YouTube URL to analyze")
    parser.add_argument("--out", required=True, help="Output folder for Video.mp4 and ANALYSIS.md")
    parser.add_argument(
        "--threshold", type=float, default=0.3,
        help="ffmpeg scene-cut sensitivity (0-1). Lower = more cuts detected. "
             "Default 0.3 works for edited footage; raise to ~0.45-0.6 for screen "
             "recordings/tutorials with lots of small UI/cursor changes that aren't real cuts, "
             "to avoid an oversized scene list that can truncate Gemini's response.",
    )
    args = parser.parse_args()
    main(args.url, args.out, args.threshold)
