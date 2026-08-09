---
name: video-analyzer
description: Use when Tony wants to reverse-engineer the style, pacing, editing, or narrative content of any reference video for any channel or project. Triggers on "analyze this video", "break down this video's style", "what's happening in this video scene by scene", or any request to understand a reference video before building something styled after it. Invocation: python3 001_Architecture/Skills/Video-Analyzer/analyze_reference_video.py <youtube_url> --out <folder>
---

# Video-Analyzer

Downloads a YouTube video, detects scene boundaries, and runs Gemini native video analysis to describe not just what's visually in each scene but the narrative/historical context (era, role, activity — e.g. "POV of a shackled pyramid worker eating porridge," not just "person eating"). Produces a per-scene `ANALYSIS.md` plus the downloaded `Video.mp4`, both written to a folder the caller specifies — this skill has no fixed output location and no channel-specific logic, so it works identically for any project.

## Usage

```bash
python3 001_Architecture/Skills/Video-Analyzer/analyze_reference_video.py "<youtube_url>" --out "<folder>" [--threshold 0.3]
```

Writes `<folder>/Video.mp4` and `<folder>/ANALYSIS.md`.

`--threshold` (default `0.3`) controls ffmpeg's scene-cut sensitivity — lower detects more cuts. The default suits normally-edited footage. For screen recordings/tutorials with lots of small UI/cursor changes that aren't real cuts, raise it to ~0.45-0.6, or ffmpeg over-detects cuts, which can make the per-scene prompt to Gemini large enough that its response hits the token cap and gets truncated before covering the whole video (confirmed happening on an 11-minute tutorial at the 0.3 default — 287 raw cuts detected, response truncated at the 6:34 mark). If `ANALYSIS.md` still looks cut off after raising the threshold, the script also now sets `max_output_tokens=65536` and prints a `⚠️ Gemini response was truncated` warning to stdout when it hits that cap — the next fix if this happens again is splitting the video into shorter segments.

## Output format

`ANALYSIS.md` starts with one summary line noting how many raw scene cuts ffmpeg detected, followed directly by Gemini's own narrative breakdown (which has its own `## Scene N [start-end]` headers per the analysis prompt — these do not necessarily line up 1:1 with ffmpeg's raw cut count, since Gemini groups by narrative beat rather than raw cut):

```markdown
_ffmpeg detected 7 raw scene cuts; see Gemini's narrative breakdown below for the actual scene structure._

## Scene 1 [0.0s-4.2s]
[Gemini's narrative/visual/context/sound/camera description for this scene]

## Scene 2 [4.2s-9.0s]
...
```
