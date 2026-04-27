---
description: Extract frames from a reference video at 0.5-second intervals using FFmpeg, saving as JPEGs into a frames/ subfolder. Use this skill to build a visual timeline of a reference video before writing scene prompts.
trigger: User wants to analyze a reference video frame-by-frame, or after downloading a video with download-video.md.
---

# Skill: Extract Reference Frames

Use this skill after a reference video has been downloaded (or provided locally) to extract still frames for visual analysis. Once frames are extracted, Claude can look at each image directly and build accurate, beat-by-beat generation prompts.

## Prerequisites
- `ffmpeg` installed at `/opt/homebrew/bin/ffmpeg`
- A source video exists at `references/inputs/<ID>-<Short_Name>/source.mp4`

## Step 1: Create the frames folder

```bash
mkdir -p "references/inputs/<ID>-<Short_Name>/frames"
```

## Step 2: Extract frames at 0.5s intervals

```bash
/opt/homebrew/bin/ffmpeg -i "references/inputs/<ID>-<Short_Name>/source.mp4" \
  -vf "fps=2" \
  -q:v 2 \
  "references/inputs/<ID>-<Short_Name>/frames/frame_%04d.jpg" \
  -y
```

- `fps=2` = 1 frame every 0.5 seconds
- `-q:v 2` = high quality JPEG (scale 1–31, lower = better)
- Files are named `frame_0001.jpg`, `frame_0002.jpg`, etc.
- Frame number × 0.5 = timestamp in seconds (frame_0006 = 3.0s)

## Step 3: Confirm extraction

```bash
ls "references/inputs/<ID>-<Short_Name>/frames/" | wc -l
```

Report the total frame count and calculated video duration to the user.

## Step 4: Analyze the frames

Read each frame image in sequence using the Read tool. For each frame, note:
- What the subject is doing
- The camera angle and framing
- Any expression change or reaction
- The moment the comedic beat lands (if applicable)

Build a **visual timeline** in this format:

```
FRAME TIMELINE: <ID>-<Short_Name>
Source: [URL or filename]
Total frames: [N] | Duration: [N]s

t=0.0s  [frame_0001] — cat sitting on counter, looking left
t=0.5s  [frame_0002] — cat notices toaster, head tilts
t=1.0s  [frame_0003] — cat leans toward toaster, eyes wide
t=1.5s  [frame_0004] — cat raises paw
t=2.0s  [frame_0005] — cat batting toaster rapidly, mouth open
...
```

## Step 5: Write scene prompts from the timeline

Use the timeline to write generation prompts grounded in the actual visual beats:
- Identify where the setup ends and the punchline begins
- Note the exact expression at the peak funny moment
- Use the camera angle observed in frames for prompt direction
- Specify the beat sequence: "First 1s: [setup]. Then: [action]. Final beat: [reaction]."

## Notes
- At 0.5s intervals a 30-second video produces ~60 frames — manageable to read in one pass
- For longer videos (>60s), consider `fps=1` (1 frame per second) to reduce frame count
- Frames are read-only reference assets — never delete them mid-session
- The frame number → timestamp formula: `timestamp = (frame_number - 1) × 0.5`
- After analysis, save the visual timeline to `references/inputs/<ID>-<Short_Name>/timeline.md`
