---
name: video-analyzer
description: Use when Tony wants to reverse-engineer the style, pacing, editing, or narrative content of any reference video for any channel or project. Triggers on "analyze this video", "break down this video's style", "what's happening in this video scene by scene", or any request to understand a reference video before building something styled after it. Invocation: python3 001_Architecture/Skills/Video-Analyzer/analyze_reference_video.py <youtube_url> --out <folder>
---

# Video-Analyzer

Downloads a YouTube video and builds a complete, three-source understanding of it — narrative/motion (Gemini native video), exact word-for-word speech (local Whisper), and exact on-screen visual content like pasted prompts or settings panels (full-resolution FFmpeg keyframes, read directly by the invoking agent). No single source alone gives full human-level understanding: Gemini's native video sampling reads motion/narrative well but often can't read small on-screen text; Whisper gives an accurate independent transcript; the keyframes are the only source with full-resolution stills good enough to read a pasted prompt or a settings toggle shown on screen. Output is written to a folder the caller specifies — this skill has no fixed output location and no channel-specific logic, so it works identically for any project.

## Usage

```bash
python3 001_Architecture/Skills/Video-Analyzer/analyze_reference_video.py "<youtube_url>" --out "<folder>" [--threshold 0.3] [--dense-interval 0.5] [--profile standard|production]
```

Writes `<folder>/Video.mp4`, `<folder>/ANALYSIS.md`, `<folder>/Transcript.srt`, and `<folder>/Keyframes/001.jpg, 002.jpg, ...`. If `--dense-interval` is set, also writes `<folder>/Dense_Keyframes/0001.jpg, 0002.jpg, ...`.

`--profile production` is an optional global analysis mode for video-production
case studies. It preserves the same files and workflow, but asks Gemini to
add clip-boundary confidence, editorial beats, humor mechanics, dialogue
placement and speaker direction, music and sound-effect details, retention
patterns, reusable abstractions, and originality boundaries. The default
`standard` profile is unchanged for existing projects.

**`--dense-interval` — for continuity/fault auditing, not general use.** The default `Keyframes/` set only captures ffmpeg-detected scene *cuts* — it's built for reading on-screen text within each distinct scene, and it has a real blind spot: a defect that drifts gradually *within* one continuous shot (no hard cut) falls straight through the gap between two scene-cut keyframes. Confirmed case: a POV camera that started correctly first-person and drifted into a third-person view partway through a single uncut shot was invisible in the scene-cut `Keyframes/` set, but obvious once every ~1 second of that shot was pulled via `--dense-interval 0.5`. Use this flag when auditing a render for continuity/POV-lock/identity-drift faults specifically — leave it off for a normal case-study run (it adds a large number of frames and proportionally more review time).

`--threshold` (default `0.3`) controls ffmpeg's scene-cut sensitivity for both the Gemini scene ranges and the keyframe extraction — lower detects more cuts. The default suits normally-edited footage. For screen recordings/tutorials with lots of small UI/cursor changes that aren't real cuts, raise it to ~0.45-0.6, or ffmpeg over-detects cuts, which can make the per-scene prompt to Gemini large enough that its response hits the token cap and gets truncated before covering the whole video (confirmed happening on an 11-minute tutorial at the 0.3 default — 287 raw cuts detected, response truncated at the 6:34 mark). If `ANALYSIS.md` still looks cut off after raising the threshold, the script also now sets `max_output_tokens=65536` and prints a `⚠️ Gemini response was truncated` warning to stdout when it hits that cap — the next fix if this happens again is splitting the video into shorter segments. A higher threshold also keeps the keyframe count sane on long tutorials (no need for a fixed "one frame per second" — only real scene/screen changes get captured).

## Output format

`ANALYSIS.md` starts with one summary line noting how many raw scene cuts ffmpeg detected, followed directly by Gemini's own narrative breakdown (which has its own `## Scene N [start-end]` headers per the analysis prompt — these do not necessarily line up 1:1 with ffmpeg's raw cut count, since Gemini groups by narrative beat rather than raw cut):

```markdown
_ffmpeg detected 7 raw scene cuts; see Gemini's narrative breakdown below for the actual scene structure._

## Scene 1 [0.0s-4.2s]
[Gemini's narrative/visual/context/sound/camera description for this scene]

## Scene 2 [4.2s-9.0s]
...
```

`Transcript.srt` is Whisper's independent, timestamped, word-for-word transcription of the audio track (local, free, no API cost) — use it to double-check or supplement Gemini's own in-scene transcript when the two disagree on what was actually said.

`Keyframes/` holds one full-resolution `.jpg` per detected scene change, numbered sequentially (`001.jpg`, `002.jpg`, ...) — these are NOT sent to any API. They exist specifically to be read directly by the invoking agent's own vision.

## Mandatory follow-up step: read the keyframes yourself

The goal of this skill is to understand the video as completely as a human watching it would — not just "what happened" but everything visible on screen that carries real information. Gemini's native video analysis alone is not enough for this: it reads motion and narrative well but frequently can't read small on-screen text, and it doesn't stop to study a frame the way a human would pause a tutorial to actually look at something. After the script finishes, the invoking agent MUST use the Read tool to view every file in `Keyframes/` directly (full resolution, not Gemini's description of them) and extract everything relevant, which is broader than just text:
- **Exact on-screen text** — a prompt someone pastes into a text box (capture it verbatim; this is real-world validated prompt language from someone who has iterated on it, more valuable than any generic prompting guide), settings panels, toggles, sliders, menu selections, labels, values, file names
- **Visual concepts and composition** — how a reference sheet, character sheet, storyboard grid, or UI layout is actually structured (panel count and arrangement, what angles/views are included, spacing, what's included vs. left out)
- **Visual style and quality** — art style, lighting, level of detail, consistency (or inconsistency) between frames, anything about how something looks that a written description would flatten or lose
- **Anything else meaningfully visible** — treat this as "what would I notice if I paused the video here," not a fixed checklist

Append findings as a new `## On-Screen Content (from keyframe review)` section to `ANALYSIS.md`, one entry per keyframe where something worth capturing appears (skip keyframes with nothing relevant — don't pad the section). This step cannot be scripted — it requires the agent's own vision on the raw keyframes, not a description of them, and is not optional even when Gemini's narrative pass already seems thorough.
