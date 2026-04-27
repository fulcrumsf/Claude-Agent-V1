---
description: Analyze a YouTube or public video URL using Google Gemini to extract visual style, humor patterns, camera work, and AI-ready prompt recreation guides. Use this skill whenever you need to understand a reference video before generating new content.
trigger: User provides a YouTube URL or video link as a reference for a new video project.
---

# Skill: Analyze Video with Gemini

Use this skill when the user provides a reference video (YouTube URL or public video link) and wants you to understand its style, humor, camera work, or pacing before generating new content.

## When to Use
- User shares a YouTube link as a style reference
- User says "make it look like this video" or "recreate the vibe of this"
- During `session-start.md` if the user provides a reference URL
- During `create-viral-video.md` Step 3 (storyboard) when a reference video was provided

## Prerequisites
- `GEMINI_API_KEY` or `GOOGLE_API_KEY` must be set in `.env`
- `google-genai` package must be installed: `pip install google-genai` (NOT the deprecated `google-generativeai`)
- The tool `tools/gemini_video_analysis.py` must exist

## Step 1: Run the Analysis

```bash
cd "/Users/tonymacbook2025/Documents/App Building/Video Editor"
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 tools/gemini_video_analysis.py "[VIDEO_URL]" -o "references/research/[PROJECT_ID]-video-analysis.md"
```

If no project ID exists yet, save to:
```bash
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 tools/gemini_video_analysis.py "[VIDEO_URL]" -o "references/research/video-analysis-temp.md"
```

Create the output directory if it doesn't exist:
```bash
mkdir -p references/research
```

## Step 2: Parse the Analysis Output

The analysis returns 7 structured sections. Extract and use each as follows:

| Section | How to Use |
|---|---|
| **Overall Style & Aesthetic** | Sets the visual tone for ALL scene prompts in the project |
| **Camera Work** | Defines the camera direction vocabulary for prompts |
| **Scene-by-Scene Breakdown** | Gives you concrete action ideas and timing references |
| **Humor Analysis** | Informs the storyboard arc — what type of comedy to aim for |
| **Subject Behavior** | Tells you what physical behaviors/expressions to prompt for |
| **Lighting & Environment** | Sets the lighting language for prompts |
| **Prompt Recreation Guide** | 3 ready-to-use example prompts — use as starting templates |

## Step 3: Store Analysis as Project Context

After running the analysis, create a summary block in your session context:

```
REFERENCE_VIDEO: [URL]
VISUAL_STYLE: [1-line summary from Section 1]
CAMERA_STYLE: [1-line summary from Section 2]
HUMOR_TYPE: [1-line summary from Section 4]
PROMPT_TEMPLATES: [3 example prompts from Section 7]
ANALYSIS_FILE: references/research/[filename].md
```

## Step 4: Apply to Scene Prompts

When writing storyboard prompts, reference the analysis:
- Start from the Prompt Recreation Guide examples (Section 7) as templates
- Apply the Camera Work vocabulary (Section 2) to every scene
- Match the Lighting & Environment style (Section 6)
- Design subject behaviors (Section 5) to hit the Humor Analysis patterns (Section 4)

## Notes

- Gemini can analyze YouTube URLs, YouTube Shorts, and most public video URLs directly
- Analysis takes 20–60 seconds depending on video length
- If the video is private or geo-restricted, Gemini will return an error — ask the user for a different URL or a downloaded file
- For downloaded video files, pass the local file path instead of a URL (Gemini will use the Files API automatically via the SDK)
- The model used is `gemini-3-flash-preview` — sufficient for style/humor analysis. Upgrade to `gemini-3-pro-preview` in the tool if deeper analysis is needed.
- `GOOGLE_API_KEY` must be added to your `.env` file. Get it from: https://aistudio.google.com/app/apikey
- Always run scripts with `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3` — that's where `google-genai` and other packages are installed.
