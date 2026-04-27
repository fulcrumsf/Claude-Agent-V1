---
description: Download a YouTube (or other public) video using yt-dlp and save it into a numbered input asset folder. Use this skill whenever the user provides a video URL they want to use as reference footage.
trigger: User provides a YouTube URL and wants to download it as a local reference video.
---

# Skill: Download Reference Video

Use this skill when the user provides a YouTube URL (or other public video URL) and wants it saved locally as a reference asset.

## Prerequisites
- `yt-dlp` installed at `/Library/Frameworks/Python.framework/Versions/3.13/bin/yt-dlp`
- Node.js installed at `/opt/homebrew/bin/node` (required for YouTube JS challenge solving)
- yt-dlp global config at `~/.config/yt-dlp/config` includes:
  ```
  --js-runtimes node:/opt/homebrew/bin/node
  --remote-components ejs:github
  ```
  These flags are applied automatically — no need to pass them manually.
- `references/inputs/` directory exists (create if needed)

## Step 1: Determine the next project ID

Check what already exists in `references/inputs/` to get the next sequential 4-digit ID:
```bash
ls references/inputs/ 2>/dev/null | grep -E '^[0-9]{4}-' | sort | tail -1
```

If no folders exist yet, start at `0001`.

## Step 2: Ask the user for a short name

Ask: *"What's a short Snake_Case name for this video? (e.g. `Funny_Cats_Compilation`)"*

Full folder name = `<ID>-<Short_Name>` (e.g. `0001-Funny_Cats_Compilation`)

**DO NOT proceed until the user confirms the name.**

## Step 3: Create the asset folder

```bash
mkdir -p "references/inputs/<ID>-<Short_Name>"
```

## Step 4: Download the video

Download at 720p MP4, saved as `source.mp4` inside the asset folder:

```bash
/Library/Frameworks/Python.framework/Versions/3.13/bin/yt-dlp \
  -f "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best[height<=720]" \
  --merge-output-format mp4 \
  -o "references/inputs/<ID>-<Short_Name>/source.mp4" \
  "[URL]"
```

## Step 5: Confirm and report

After download completes, confirm:
```bash
ls -lh "references/inputs/<ID>-<Short_Name>/source.mp4"
```

Report the file size and duration to the user.

## Step 6: Offer to extract frames

Ask the user: *"Do you want me to extract frames now for visual analysis?"*

If yes, run the `extract-frames.md` skill on `references/inputs/<ID>-<Short_Name>/source.mp4`.

## Notes
- yt-dlp handles YouTube, YouTube Shorts, TikTok, Instagram Reels, and most public video URLs
- If a video is age-restricted or private, yt-dlp will return an error — ask the user for a different URL
- Always cap at 720p — higher resolution is unnecessary for frame extraction and wastes disk space
- The `source.mp4` naming is fixed so the `extract-frames.md` skill always knows where to find it
