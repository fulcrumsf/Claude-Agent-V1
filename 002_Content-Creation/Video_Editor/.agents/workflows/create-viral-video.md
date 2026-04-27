---
description: Create a viral video from an idea, including storyboarding, generation, and uploading to YouTube.
---

# Viral Video Creation Workflow

> **Prerequisites — Do NOT start this workflow directly.**
> This workflow is called by `session-start.md` after context has been established.
> The following session variables must already be set before Step 1:
> - `CHANNEL` — which channel this is for
> - `CHANNEL_BIBLE` — channel bible loaded (or confirmed not available)
> - `FORMAT` — short / medium / long
> - `DURATION` — target duration
> - `ASPECT_RATIO` — 16:9 or 9:16
> - `RECURRING_CHARACTERS` — character sheets complete (if applicable)
> - `PROJECT_ID` — new or continuing
>
> If any of these are missing, stop and run `session-start.md` first.

---

## Step 1: Research & Ideation

1. Take the user's topic/idea from the session context (already collected in `session-start.md`).
2. Use the `mcp_blotato_blotato_create_source` tool with `sourceType: perplexity-query`.
   Ask Perplexity: *"Find 3 specific, highly contrarian, and viral angles for a [FORMAT] video about [TOPIC] for a [CHANNEL] audience. The angles should be unique and hook the viewer immediately."*
3. Present the 3 angles to the user using `notify_user` and ask them which one they want to proceed with.
   **DO NOT move to Step 2 until they choose.**

---

## Step 2: Script Writing

1. Once the user selects an angle, write the script.

2. **Apply the channel's story arc** from the loaded channel bible.
   - If Anomalous Wild: follow **THE ANOMALOUS ARC™** (Glitch Hook → Setup → Tease #1 → Context Loop → Tease #2 → Reward → Hook Forward)
   - If no channel bible: use the default arc: Hook → Context → Reward → CTA

3. **Respect format and duration:**
   - Use the session's `DURATION` to pace the script — estimate ~125–150 words per minute of narration
   - Short-form: Compressed arc, one main fact, no more than 150 words total
   - Medium-form: Full arc, 600–1,800 words
   - Long-form: Multi-arc, chapter structured, 2,000–6,000 words

4. **Apply channel voice rules** from the channel bible (narrator tone, forbidden words, language style).

5. Present the script to the user for approval using `notify_user` with `BlockedOnUser: true`.

---

## Step 3: Storyboard & Scene Prompts

1. Break the approved script into discrete scenes. Use the scene count estimate from session setup.
   - Scene count = estimated total duration (seconds) ÷ average scene length
   - Max scenes per generation batch: 20 (split into batches if longer)

2. For each scene, define:
   - **Scene number** and **duration** (seconds)
   - **Voiceover text** (exact words from script)
   - **Visual description** (what happens visually — separate from the generation prompt)
   - **Model selection** (which model to use — refer to `references/docs/Prompt-best-practices.md` decision matrix)
   - **Generation prompt** (the final API-ready prompt)

3. **Writing generation prompts — rules:**
   - Always prefix or include the correct aspect ratio for the chosen model
   - **16:9:** Veo 3.1 → `aspect_ratio: "16:9"` | Kling 3.0 → `aspect_ratio: "16:9", mode: "pro"` | Sora 2 → `aspect_ratio: "landscape"`
   - **9:16:** Veo 3.1 → `aspect_ratio: "9:16"` | Kling 3.0 → `aspect_ratio: "9:16", mode: "pro"` | Sora 2 → `aspect_ratio: "portrait"`
   - If `RECURRING_CHARACTERS = yes`: include the character's CANONICAL DESCRIPTION (from their character record file) in EVERY scene prompt that features them — never shorten it
   - If using Kling 3.0 with element references: include `@[CHARACTER_LABEL]` in each relevant prompt and attach the `kling_elements` block from the character record
   - Follow all model-specific prompt guidelines from `references/docs/Prompt-best-practices.md`

4. **Storyboard table format:**

| # | Duration | VO Text | Model | Prompt |
|---|---|---|---|---|
| 1 | 5s | "This animal..." | Veo 3.1 | `[full prompt]` |
| 2 | 7s | "What's remarkable..." | Kling 3.0 | `[full prompt]` |

5. Present the complete storyboard to the user for approval using `notify_user` with `BlockedOnUser: true`.
   **DO NOT begin generation until approved.**

---

## Step 4: Project Setup

1. If continuing a project, the `PROJECT_ID` is already set. Skip to Step 5.

2. If new project, ask the user for:
   - A sequential 4-digit Project ID (e.g., `0003`)
   - A short Project Name in Snake_Case (e.g., `Mantis_Shrimp_Punch`)
   - Full ID = `<ID>-<Project_Name>` (e.g., `0003-Mantis_Shrimp_Punch`)

   **DO NOT proceed until the user confirms the project ID.**

3. Create the project output directory:
   ```bash
   mkdir -p references/outputs/<ID>-<Project_Name>
   ```

4. Create a scene directory for each scene:
   ```bash
   mkdir -p references/outputs/<ID>-<Project_Name>/scene_1
   # ... repeat for each scene
   ```

5. Save the approved storyboard as:
   `references/outputs/<ID>-<Project_Name>/storyboard.md`

---

## Step 5: Generation

Process each scene sequentially. For each scene:

### 5a. Generate Audio (TTS)
```bash
python tools/audio_tts.py "Exact voiceover text" "references/outputs/<ID>-<Project_Name>/scene_X/audio.mp3"
```
Wait for completion before starting video generation for that scene.

### 5b. Generate Video
Select the correct tool call based on the model chosen in the storyboard:

**Veo 3.1:**
```bash
python tools/kie_video_gen.py "[PROMPT]" "references/outputs/<ID>-<Project_Name>/scene_X/video.mp4" "veo3"
```

**Kling 3.0 (single shot):**
```bash
python tools/kie_video_gen.py "[PROMPT]" "references/outputs/<ID>-<Project_Name>/scene_X/video.mp4" "kling-3.0/video"
```

**Kling 3.0 (with element references):**
```bash
python tools/kie_video_gen.py "[PROMPT]" "references/outputs/<ID>-<Project_Name>/scene_X/video.mp4" "kling-3.0/video" --elements "references/characters/[CHARACTER_LABEL]/character.md"
```

**Wan 2.6:**
```bash
python tools/kie_video_gen.py "[PROMPT]" "references/outputs/<ID>-<Project_Name>/scene_X/video.mp4" "wan/2-6-text-to-video"
```

**Sora 2:**
```bash
python tools/kie_video_gen.py "[PROMPT]" "references/outputs/<ID>-<Project_Name>/scene_X/video.mp4" "sora-2-text-to-video"
```

Wait synchronously for each video generation to complete before proceeding to the next scene.

### 5c. Stitch Final Video
Once all scenes are generated:
```bash
python tools/video_stitcher.py \
  references/outputs/<ID>-<Project_Name>/scene_1 \
  references/outputs/<ID>-<Project_Name>/scene_2 \
  [... all scenes ...] \
  -o references/outputs/<ID>-<Project_Name>/<ID>-<Project_Name>.mp4
```

---

## Step 6: Thumbnail Generation

1. Write a thumbnail prompt using channel visual style from the channel bible.
   - For Anomalous Wild: dark background, single hero animal, electric cyan/amber palette, glitch effect hint, max 3 words of text on image
   - Use `references/docs/Prompt-best-practices.md` → Nano Banana 2 section for guidance

2. Generate thumbnail using Nano Banana 2:
   ```bash
   python tools/nano_banana_gen.py "[THUMBNAIL PROMPT]" "references/outputs/<ID>-<Project_Name>/thumbnail.jpg" --aspect_ratio "16:9" --resolution "4K"
   ```

3. Generate YouTube metadata:
   - **Title:** Viral, curiosity-gap driven, max 60 characters, channel SEO keywords
   - **Description:** Hook + 3 key facts + subscribe CTA + channel keywords
   - **Tags:** 15–20 tags using channel's core SEO keywords

4. Present thumbnail + metadata to user for approval.

---

## Step 7: Upload & Publish

1. Upload the final video to a public URL via kie.ai file uploader (required by Blotato):
   ```bash
   python tools/kie_file_upload.py "references/outputs/<ID>-<Project_Name>/<ID>-<Project_Name>.mp4"
   # Returns public URL
   ```

2. Get the YouTube account ID:
   ```
   mcp_blotato_blotato_list_accounts
   ```

3. Create the YouTube post:
   ```
   mcp_blotato_blotato_create_post
   ```
   With: `accountId`, `videoUrl` (public URL from step 1), `title`, `description`, `tags`

---

## Step 8: Completion

Share the final summary with the user:

---

**Video complete!**

- Project: `<ID>-<Project_Name>`
- Final video: `references/outputs/<ID>-<Project_Name>/<ID>-<Project_Name>.mp4`
- Thumbnail: `references/outputs/<ID>-<Project_Name>/thumbnail.jpg`
- YouTube: [post URL if available]
- Scenes generated: [N]
- Total duration: [duration]

---
