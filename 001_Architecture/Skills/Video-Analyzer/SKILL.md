---
name: video-analyzer
description: Use when Tony wants to reverse-engineer the style, pacing, editing, or narrative content of any reference video for any channel or project. Triggers on "analyze this video", "break down this video's style", "what's happening in this video scene by scene", or any request to understand a reference video before building something styled after it. Command: /video-analyzer <youtube_url> --out <folder>
---

# Video-Analyzer

Downloads a YouTube video, detects scene boundaries, and runs Gemini native video analysis to describe not just what's visually in each scene but the narrative/historical context (era, role, activity — e.g. "POV of a shackled pyramid worker eating porridge," not just "person eating"). Produces a per-scene `ANALYSIS.md` plus the downloaded `Video.mp4`, both written to a folder the caller specifies — this skill has no fixed output location and no channel-specific logic, so it works identically for any project.

## Usage

```bash
python3 001_Architecture/Skills/Video-Analyzer/analyze_reference_video.py "<youtube_url>" --out "<folder>"
```

Writes `<folder>/Video.mp4` and `<folder>/ANALYSIS.md`.

## Output format

`ANALYSIS.md` has one section per detected scene:

```markdown
## Scene 1 [0.0s-4.2s]
[Gemini's narrative/visual/context/sound/camera description for this scene]

## Scene 2 [4.2s-9.0s]
...
```
