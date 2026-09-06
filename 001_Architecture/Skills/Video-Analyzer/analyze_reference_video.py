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

PRODUCTION_ANALYSIS_APPENDIX = """

This is a production-analysis request for a reference video. In addition to the
scene description above, analyze it as an editor studying material for an
original production. Do not recommend copying the source. Extract reusable,
abstract patterns only.

For every detected scene, also include:
- Exact clip boundary confidence: high, medium, or low, and why
- Editorial beat: setup, action, payoff, reaction, transition, or other
- What makes the moment entertaining, including mismatch, surprise, timing,
  escalation, facial-expression irony, physical failure, or social context
- Whether the moment works without narration; if not, what editorial context
  would help without merely describing the obvious
- Whether there is in-scene dialogue; distinguish on-camera, off-camera,
  background, camera-holder, and narrator speech
- If dialogue is present, describe approximate speaker age, vocal tone,
  energy, accent/dialect when audible, emotional attitude, and the exact line
- Music analysis: presence/absence, genre, instruments, tempo, mood, structure,
  transitions, and how the music supports the visual joke or payoff
- Sound-effect analysis: impact hits, whooshes, stings, bass interrupts,
  comedic accents, sound bridges, silence, and their approximate timestamps
- Retention mechanics: hook, pattern interrupts, cut rhythm, escalation,
  curiosity gaps, and payoff placement
- A concise reusable pattern stated abstractly, without copying the source's
  animal, setting, wording, choreography, or distinctive expression

After the scene sections, add these sections:
## Production Summary
## Editorial Beat Map
## Music and Sound Design Profile
## Reusable Humor and Retention Patterns
## Originality Boundaries

The Originality Boundaries section must list what should change when using this
video only as inspiration. Do not treat the source video's exact dialogue,
sequence, framing, soundtrack, or choreography as reusable.
"""

def download_video(url: str, out_dir: Path) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    video_path = out_dir / "Video.mp4"
    command = ["yt-dlp", "-f", "mp4", "-o", str(video_path), url]
    try:
        subprocess.run(command, check=True, capture_output=True)
    except subprocess.CalledProcessError:
        # Some YouTube uploads expose MP4 video and audio as separate streams;
        # fall back to an explicit compatible pair before reporting failure.
        fallback = [
            "yt-dlp",
            "-f",
            "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]",
            "--merge-output-format",
            "mp4",
            "-o",
            str(video_path),
            url,
        ]
        subprocess.run(fallback, check=True, capture_output=True)
    return video_path

def extract_keyframes(video_path: Path, out_dir: Path, threshold: float = 0.3) -> Path:
    """Extracts one full-resolution still per detected scene change, for reading
    on-screen text (prompts, settings panels, toggles) that Gemini's native video
    understanding often can't read reliably at its default sampling rate/resolution."""
    keyframes_dir = Path(out_dir) / "Keyframes"
    keyframes_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(video_path),
         "-vf", f"select='gt(scene,{threshold})'",
         "-vsync", "vfr",
         str(keyframes_dir / "%03d.jpg")],
        capture_output=True,
    )
    if not list(keyframes_dir.glob("*.jpg")):
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(video_path), "-vframes", "1",
             str(keyframes_dir / "001.jpg")],
            capture_output=True,
        )
    return keyframes_dir

def extract_dense_keyframes(video_path: Path, out_dir: Path, interval_s: float = 0.5) -> Path:
    """Extracts one full-resolution still every `interval_s` seconds, regardless of whether
    ffmpeg detects a scene change. extract_keyframes() (scene-cut-based) is built for grabbing
    one representative frame per scene to read on-screen text/prompts — it misses anything that
    drifts gradually WITHIN a single continuous shot (no hard cut for ffmpeg to detect), which is
    exactly how a POV camera can drift into a third-person view mid-generation without ever
    producing a "scene change." Use this mode specifically for continuity/fault auditing — walking
    every ~0.5-1s of a shot to catch a drift a scene-cut sample would fall right through the gaps of.
    Written to a separate Dense_Keyframes/ folder so it doesn't collide with the scene-cut set."""
    dense_dir = Path(out_dir) / "Dense_Keyframes"
    dense_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(video_path),
         "-vf", f"fps=1/{interval_s}",
         str(dense_dir / "%04d.jpg")],
        capture_output=True,
    )
    return dense_dir

def transcribe_with_whisper(video_path: Path, out_dir: Path) -> Path:
    """Runs local Whisper transcription (free, no API cost) as an accurate,
    independent word-for-word transcript alongside Gemini's own audio interpretation."""
    out_dir = Path(out_dir)
    subprocess.run(
        ["whisper", str(video_path), "--model", "base",
         "--output_format", "srt", "--output_dir", str(out_dir)],
        capture_output=True,
    )
    srt_output = out_dir / f"{video_path.stem}.srt"
    transcript_path = out_dir / "Transcript.srt"
    if srt_output.exists():
        srt_output.rename(transcript_path)
    return transcript_path

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

def analyze_video_narrative(
    video_path: Path,
    scenes: list[tuple[float, float]],
    profile: str = "standard",
) -> str:
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
    if profile == "production":
        prompt += PRODUCTION_ANALYSIS_APPENDIX
    elif profile != "standard":
        raise ValueError(f"Unknown analysis profile: {profile}")

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


def main(
    url: str,
    out: str,
    threshold: float = 0.3,
    dense_interval: float | None = None,
    profile: str = "standard",
) -> None:
    out_dir = Path(out)
    video_path = download_video(url, out_dir)
    scenes = detect_scenes(video_path, threshold)
    # Preserve the original call shape for the default profile so existing
    # integrations and tests remain compatible.
    if profile == "standard":
        gemini_output = analyze_video_narrative(video_path, scenes)
    else:
        gemini_output = analyze_video_narrative(video_path, scenes, profile)
    write_analysis_md(out_dir, scenes, gemini_output)
    extract_keyframes(video_path, out_dir, threshold)
    transcribe_with_whisper(video_path, out_dir)
    if dense_interval is not None:
        extract_dense_keyframes(video_path, out_dir, dense_interval)


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
    parser.add_argument(
        "--dense-interval", type=float, default=None,
        help="If set, also extracts a full-resolution frame every N seconds (regardless of scene "
             "cuts) into Dense_Keyframes/, for continuity/fault auditing where a defect can drift "
             "gradually within a single continuous shot and fall through the gaps between "
             "scene-cut keyframes. Off by default (adds significant frame count/review time) — "
             "e.g. 0.5-1.0 for a thorough per-second audit.",
    )
    parser.add_argument(
        "--profile", choices=("standard", "production"), default="standard",
        help="Analysis depth. 'production' adds editorial beat, music, sound-effect, "
             "dialogue, retention, and originality-boundary analysis.",
    )
    args = parser.parse_args()
    main(args.url, args.out, args.threshold, args.dense_interval, args.profile)
