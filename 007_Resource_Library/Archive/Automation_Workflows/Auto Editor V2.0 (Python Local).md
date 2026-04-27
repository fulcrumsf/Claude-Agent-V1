---
Category: Automation
tags:
  - video-editing
  - ffmpeg
  - whisper-ai
  - make-com
  - google-colab
  - shorts
  - python
  - workflow
Difficulty: Intermediate
Description: Master documentation for Auto Shorts Editor V2.0 - FFmpeg + Whisper AI video editing automation with Make + Google Colab
---

# 📖 Master Documentation for Your Video Editing Automation

This document serves as a **full reference** for your **Make + Google Colab + FFmpeg + Whisper AI automation workflow**. If you ever return later, you can copy and paste this into any ChatGPT session to continue exactly where you left off.

---

## **🔹 Project Overview**

### **🎯 Goal**

Automate the process of **editing short-form videos** using **Make, Google Colab, FFmpeg, and Whisper AI**, eliminating the need for Adobe Premiere.

This workflow ensures:

✅ **Correct video structure:** A preview image + video + background music.

✅ **Automatic caption generation** using Whisper AI.

✅ **Final edited video stored back in Google Drive.**

---

## **🔹 Tools Used & Their Responsibilities**

|Tool|Purpose|
|---|---|
|**Make Automation**|Detects new RAW folders, extracts filenames, triggers Google Colab, and uploads final results to Google Drive.|
|**Google Colab**|Runs the Python script to process videos using FFmpeg and generate captions using Whisper AI.|
|**FFmpeg**|Adds transitions, scales images, fades audio, and stitches video clips together.|
|**Whisper AI**|Converts video speech to text and outputs a `.srt` subtitle file.|

---

## **🔹 File & Folder Structure**

Your Google Drive follows this format:

```
ReimaginedRealms (Master Folder)
    ├── 000091_Video_Title (Subfolder for each video)
        ├── RAW (Holds all original files)
            ├── video.mp4  (Unedited video from AI)
            ├── image.jpg  (Preview thumbnail with title overlay)
            ├── audio.mp3  (Background music)
        ├── 000091_Video_Title.mp4  (Final edited video)
        ├── 000091_Video_Title.srt  (Closed captions)
        ├── 000091_Video_Title.txt  (Metadata)

```

✅ **Each RAW folder contains exactly:**

- 1 **image** (`.jpg` or `.png`)
- 1 **video** (`.mp4` or `.mov`)
- 1 **audio file** (`.mp3`, `.aac`, or `.wav`)
- These files must **remain grouped together** during processing.

---

## **🔹 Video Editing Rules**

Each video is structured as follows:

### **🎬 Timeline & Transitions**

|Element|Timing|Action|
|---|---|---|
|**Image Display**|0.00s → 1.00s|Shows for 1 second|
|**Cross Dissolve Transition**|0.50s → 0.70s|Fades from image to video|
|**Zoom-in Effect**|0.00s → 1.00s|Image scales from **100% to 105%**|
|**Video Plays**|1.00s → End|Full length of original video|

### **🎵 Audio Rules**

|Element|Timing|Action|
|---|---|---|
|**Background Music**|Entire video duration|Adjusted to fit full timeline|
|**Fade-in**|0.00s → 0.50s|Gradual volume increase|
|**Fade-out**|Last 0.50s|Gradual volume decrease|
|**Audio Volume**|Entire video|Set between **-18dB and -21dB**|

### **🎤 Subtitle Rules**

- **Stylized captions** are already burned into the AI-generated video.
- **Whisper AI generates** a `.srt` subtitle file for **standard closed captions**.
- The `.srt` is stored **next to the final video** in Google Drive.

---

## **🔹 Workflow Step-by-Step Breakdown**

Each RAW folder must be **processed separately**, ensuring files don’t mix.

### **🔹 Step 1: Make Detects a New RAW Folder**

✅ **Module Used:** Google Drive - **Search for Files/Folders**

- Looks for **newly created RAW folders** inside the parent project folder.
- **Extracts the following information:**
    - **Folder Name** (used to name the final output files)
    - **File Paths** for:
        - **Image** (`.jpg` or `.png`)
        - **Video** (`.mp4` or `.mov`)
        - **Audio** (`.mp3`, `.aac`, `.wav`)
- **Triggers Google Colab** to process these files.

---

### **🔹 Step 2: Make Sends Files to Google Colab**

✅ **Module Used:** Make API Call

- Sends extracted **file paths** to a **Google Colab notebook** via an **HTTP request**.
- Google Colab starts processing the files.

---

### **🔹 Step 3: Google Colab Processes the Video**

✅ **Python Script Running in Google Colab**

The script performs the following **FFmpeg** tasks:

1️⃣ **Load the image, video, and audio** from Google Drive.

2️⃣ **Process Video with FFmpeg:**

- Trim **image** to **1 second**.
- **Apply cross dissolve** (fades image → video).
- **Apply zoom-in effect** (100% → 105% scale).
- **Apply fade-in/out to background music**.
- **Cut background music** to match video length. 3️⃣ **Run Whisper AI to generate subtitles** 4️⃣ **Save the final video and `.srt` file** to Google Drive.

---

### **🔹 Step 4: Make Uploads Final Files to Google Drive**

✅ **Module Used:** Google Drive - **Upload a File**

- Moves the final video + subtitle file into the **parent folder**.
- Deletes or archives the RAW folder after processing.

---

## **🔹 Make Automation Modules Needed**

**1️⃣ Google Drive - Search for Files/Folders**

🔹 **Finds new RAW folders** inside the main project folder.

**2️⃣ Router (Conditional Logic for File Processing)**

🔹 Ensures that each RAW folder is processed separately.

**3️⃣ Make API Call (Triggers Google Colab)**

🔹 Sends the extracted **file paths** for processing.

**4️⃣ Google Drive - Upload a File**

🔹 Moves the **final edited video + subtitles** into the correct folder.

---

## **🔹 Questions You Answered (Integrated into the Plan)**

1️⃣ **Each RAW folder is unique** and must be processed separately.

2️⃣ **Each folder will contain exactly** one image, one video, and one audio file.

3️⃣ **Whisper AI** will be run wherever it's easiest—**either in Make via API or in Google Colab**.

4️⃣ **Final video & captions** will be saved inside the **parent folder** of the RAW folder.

---

## **⚙️ Next Steps**

✅ **1. Build the Google Colab script** (FFmpeg processing + Whisper AI integration).

✅ **2. Define the Make scenario modules & logic**.

✅ **3. Connect Make to Google Colab & Google Drive**.

---

### **🎯 Final Checkpoint Before Coding**

📌 **Does this cover every step of what you need?**

📌 **Anything missing before I start writing the Python script?**

### **Automated Video Processing Workflow for Reimagined Realms**

This document outlines the automated workflow for processing short-form vertical videos using AI-generated assets and Adobe Premiere.

---

## **1. Overview of the Workflow**

- AI tools generate a **[video]** (vertical short-form content with burned-in captions).
- AI tools generate a **[beginning image]** (thumbnail-style overlay for the first second of the video).
- A **[background music/audio]** file is selected manually from Artlist.
- The **[video]**, **[beginning image]**, and **[audio]** are brought into **Adobe Premiere** for editing.
- The final exported **[video]** is saved inside a structured file system.

---

## **2. Editing Process in FFmpeg**

### **A. Timeline Setup**

1. Import the **[video]**, **[beginning image]**, and **[audio]**
2. Place the **[beginning image]** at the **start of the timeline** and trim it to **1 second**.
3. Place the **[video]** **immediately after** the **[beginning image]**.

### **B. Animation Effects**

1. Set a keyframe at **Frame 1** of the timeline for the **[beginning image]** at **100% scale**.
2. Set another keyframe at the **1-second mark**, increasing scale to **105%** (to create a subtle zoom-in effect).
3. Apply a **cross dissolve** transition:
    - Starts at **0.5s**.
    - Ends at **1.2s**.

### **C. Audio Adjustments**

1. Import the **[audio]** file and place it under the **[video]**.
2. Reduce the **[audio]** level to **18dB to -21dB**.
3. Trim the **[audio]** to match the total length of the **[beginning image]** and **[video]**.
4. Apply **fade-in** to the **[audio]** at **0.5s**.
5. Apply **fade-out** to the **[audio]** **0.5s before the end**.

### **D. Export Settings**

1. **Resolution**: **1080x1920 (9:16 vertical)**.
2. **Frame rate**: Match source.
3. **Exported file name**: Matches the **subfolder name** in the project structure.

---

## 3. Whisper AI

### **A. Captions**

1. Whisper will transcribe and **generate** general captions as an **.srt file**.
2. Upload the .srt into the correct folder on Google Drive

## **3. File Structure**

### **A. Master Folder (Top-Level)**

Each YouTube channel has its own **Master Folder**.

Example:

📂 **ReimaginedRealms**

### **B. Subfolder (Unique for Each Video)**

Each **video project** has its own **subfolder** inside the **Master Folder**.

Example:

📂 **000091_Name_of_the_video_that_matches_the_title_of_video**

### **C. Raw Assets (Inside Each Subfolder)**

The **RAW** folder holds the original AI-generated files before editing.

Example:

📂 **000091_Name_of_the_video_that_matches_the_title_of_video**

📂 **RAW**

📄 **Name_of_the_video_that_matches_the_title_of_video.mp4** _(AI-generated video)_

📄 **Name_of_the_video_that_matches_the_title_of_video.jpg** _(Beginning Image)_

📄 **Background_Music.mp3** _(Artlist music track)_

### **D. Finished Exports (Inside Each Subfolder)**

Once the video is edited, it is exported back into the **same subfolder**, alongside metadata and captions.

Example:

📂 **000091_Name_of_the_video_that_matches_the_title_of_video**

📄 **Name_of_the_video_that_matches_the_title_of_video.mp4** _(Final Edited Video)_

📄 **Name_of_the_video_that_matches_the_title_of_video.srt** _(Captions for accessibility)_

📄 **Name_of_the_video_that_matches_the_title_of_video.txt** _(Metadata file)_

### **Current Make Automation Setup March 20, 2025**

Here is a detailed step-by-step breakdown of your **Google Drive automation workflow in Make (Integromat)** along with an explanation of your **current progress, file structure, and intended outcome**. You can feed this into GPT later when you return.

---

# **📌 Current Workflow Summary**

The purpose of this workflow is to **automate file retrieval and processing from Google Drive**, specifically to:

1. **Search for new project folders** inside `Draft_to_Final`.
2. **Locate the "RAW" subfolder** inside each new project folder.
3. **Identify files in the RAW folder** (images, videos, or audio).
4. **Route them into different categories** (image, video, audio).
5. **Download those files for further processing.**

---

# **📂 Google Drive File Structure**

You have a structured **folder system** for your project files:

- **Root Folder:** `Draft_to_Final`
    - Contains **multiple subfolders** for different projects.
    - Each project subfolder has a unique name (e.g., `0096_Library_of_Alexandria_Survives`).
    - Inside each project folder, there is a **RAW** folder.
    - The **RAW** folder contains **image, video, or audio files**.

**Example File Structure:**

```
My Drive
└── Reimagined Realms
    └── Draft_to_Final
        ├── 0096_Library_of_Alexandria_Survives
        │   └── RAW
        │       ├── image1.jpg
        │       ├── video1.mp4
        │       └── audio1.mp3
        ├── 0097_Genghis_Khan_Conquers_Europe
        │   └── RAW
        │       ├── image2.png
        │       ├── video2.mov
        │       └── audio2.wav

```

- **Each new project folder name is unique.**
- **Each RAW folder contains media files that need to be processed.**

---

# **🛠 Workflow Breakdown (Step-by-Step)**

## **1️⃣ Google Drive 13 - Search for Files/Folders**

- **Function:** Identifies new project folders inside `Draft_to_Final`.
- **Search Query:** Looks for folders inside the parent folder **Draft_to_Final**.
- **Expected Output:** A list of project folders inside `Draft_to_Final` (e.g., `0096_Library_of_Alexandria_Survives`, `0097_Genghis_Khan_Conquers_Europe`).

### ✅ **Current Progress**

- This module **successfully runs and returns valid folders** inside `Draft_to_Final`.

---

## **2️⃣ Router 5 - Directs Each Folder to the Next Step**

- **Function:** Sends each project folder to the next step for further processing.

---

## **3️⃣ Google Drive 14 - Search for "RAW" Folder in Each Project**

- **Function:** Searches inside each project folder to find the **RAW subfolder**.
- **Search Query:** Looks for a folder named `"RAW"` inside each project folder found by Google Drive 13.
- **Expected Output:** The **File ID** of the RAW folder inside each project folder.

### ✅ **Current Progress**

- This module **successfully finds the RAW folders inside project folders**.

---

## **4️⃣ Google Drive 16 - Search for Media Files in RAW Folder**

- **Function:** Searches inside the `RAW` folder for **image, video, or audio files**.
- **Search Query:** Filters files based on their **mime type**:
    - Images: `image/*`
    - Videos: `video/*`
    - Audio: `audio/*`
- **Expected Output:** A list of files inside the RAW folder.

### ✅ **Current Progress**

- Google Drive 16 **successfully retrieves files** inside the RAW folder.

---

## **5️⃣ Router 15 - Sorts Files into Categories**

- **Function:** Categorizes files into three types:
    - **Images** → Sent to **Google Drive 9** for downloading.
    - **Videos** → Sent to **Google Drive 8** for downloading.
    - **Audio** → Sent to **Google Drive 7** for downloading.

### ✅ **Current Progress**

- Router **correctly classifies files** based on mime type.

---

## **6️⃣ Google Drive 9, 8, 7 - Download Files**

- **Function:** Downloads the respective **image, video, or audio files** from the RAW folder.
- **Issue:** Google Drive 9 is **throwing a BundleValidationError**.
    - This suggests that **the File ID is missing or not mapped correctly** from Google Drive 16.

### ❌ **Current Problem**

- **Google Drive 9 is missing the File ID.**
- This happens because:
    1. Google Drive 16 **may not be returning valid file data**.
    2. The File ID **may not be mapped correctly** from Google Drive 16 → Google Drive 9.

---

# **📌 Plan for Fixing When You Return**

When you come back, **this is the first thing to troubleshoot**:

### ✅ **Step 1: Verify Google Drive 16’s Output**

- Run **Google Drive 16 alone** and check:
    - Does it return **at least one valid file**?
    - Does it have a **File ID** in the output?

If **Google Drive 16 is empty**, then:

- Either **no matching files exist** in the RAW folder.
- Or the **query is filtering out everything**.

---

### ✅ **Step 2: Fix File ID Mapping in Google Drive 9**

- Edit **Google Drive 9 (Download File)**.
- Find the **"File ID"** field.
- **Manually map it** to **Google Drive 16’s File ID**.
    - Click on the mapping icon.
    - Choose `"File ID"` from **Google Drive 16’s output**.

🔹 **Why?**

- Right now, it looks like **no File ID is mapped**, which is causing the error.

---

# **📌 Summary of Your Current Progress**

1️⃣ Google Drive 13 **finds project folders** inside `Draft_to_Final`. ✅

2️⃣ Google Drive 14 **finds the RAW subfolder** inside each project folder. ✅

3️⃣ Google Drive 16 **finds images, videos, and audio files inside RAW**. ✅

4️⃣ Router 15 **categorizes files** into image, video, or audio. ✅

5️⃣ Google Drive 9, 8, 7 **should download files** but **Google Drive 9 has a missing File ID issue**. ❌

### **🛠 Next Steps When You Return**

1. **Check Google Drive 16 output** – Does it return File IDs?
2. **Fix File ID mapping in Google Drive 9** – Ensure it's mapped correctly.
3. **Test again** and check if the **downloads work**.

---

# **🚀 Next Steps for GPT to Help You**

When you return, **copy this entire document** into GPT, and it will know:

- **How your workflow is structured**.
- **Where you left off**.
- **How to troubleshoot the issue**.

Let me know if you need **any clarifications** before you pivot away! 🚀

---

### Custom GPT Instruction for Auto Shorts Edit - Locally Run Script

---

## 🧠 Shorts Video Editor - Instruction Set Bible (v1.0)

This is the full master document that defines the **structure, behavior, logic, naming conventions, and error handling** for the Shorts Editor Automation Script (FFmpeg + Whisper AI).

---

### 📁 Folder Structure Example (REFERENCE ONLY – NOT AUTO-GENERATED)

```
/Users/tonymacbook2025/Documents/Projects/ShortsEditorAI
├── 000091_Mongol_Empire
│   ├── RAW
│   │   ├── image.jpg
│   │   ├── video.mp4
│   │   ├── audio.mp3
│   ├── 000091_Mongol_Empire.mp4 ✅
│   ├── 000091_Mongol_Empire.srt ✅
│   ├── 000091_Mongol_Empire.txt ✅

```

> ✅ All outputs are saved in the same folder as the parent folder of RAW or ASSETS ❌ The script will not create any folders on your behalf ✅ You only need to select the parent folder manually

---

### 🧾 File Validation Rules

- RAW folder can be named `RAW` or `ASSETS`
- There must be **exactly one** of each:
    - 🎥 1 video file
    - 🎵 1 audio file
    - 🖼️ 1 image file

If any of the following happens, the folder is **skipped and logged**:

|Condition|Action|Log Reason|
|---|---|---|
|Multiple image files|Skip|"More than one image file detected"|
|Multiple video files|Skip|"More than one video file detected"|
|Multiple audio files|Skip|"More than one audio file detected"|
|Missing image/audio/video|Skip|"Missing required file: [type]"|
|Both RAW and ASSETS exist|Skip|"Both RAW and ASSETS found"|

---

### 🧹 File Sanitization Rules

- All filenames are sanitized:
    - Replace spaces & special characters with `_`
    - Example: `The Mongol Empire?.jpg` → `The_Mongol_Empire_.jpg`
- Output file names will always match the **name of the parent folder**
    - Example:
        - Folder: `000091_Mongol_Empire`
        - Outputs: `000091_Mongol_Empire.mp4`, `.srt`, `.txt`

---

### 🎬 FFmpeg Video Editing Rules

1. **Timeline Setup**:
    - 1 second image intro
    - Video plays after image
2. **Zoom-in on image**:
    - From 100% to 105% between `0.0s → 1.0s`
3. **Cross-dissolve Transition**:
    - Starts at `0.5s` → Ends at `1.2s`
4. **Audio Processing**:
    - Volume lowered to -18dB to -21dB
    - Audio trimmed to match final video length (image + video)
    - Audio fades in at 0.5s and fades out 0.5s before end
5. **Audio Too Short?**
    - ✅ Pad with silence to match video
    - ❌ Do NOT loop
    - ❌ Skip if no audio or invalid format

---

### 🧠 Whisper AI Transcription Rules

- Only processes videos **already rendered by FFmpeg**
- **Never reads files from RAW/ASSETS**
- Captions saved as `.srt` with same base filename as video
- If Whisper fails:
    - ✅ Skip captions
    - ✅ Still log video as processed
    - 📝 Log reason: `"Failed to generate captions"`

---

### 📄 SEO .TXT Output Rules

- Generated for each project that finishes successfully
- Output is saved alongside `.mp4` and `.srt` files
- Logic auto-detects context from `.srt`

**📌 Two Niches:**

1. **Reimagined Realms**
    - Triggers: history, mythology, legends, alternate timelines
2. **The Brain Blueprint**
    - Triggers: psychology, neuroscience, human behavior

**📄 Format Example:**

```
TITLE: [Auto-generated 70-char title]

DESCRIPTION:
[1000-char summary based on transcript, optimized for niche]

HASHTAGS:
#AlternateHistory #WhatIfHistory #ImaginedHistory

KEYWORDS:
[comma,separated,keyword,list]

```

---

### 🚀 Batch Processing

- You select the **master folder** that contains subfolders (video projects)
- Script walks through each subfolder
- For each folder:
    - FFmpeg runs first
    - Successful outputs sent to Whisper
- At end: shows a log like this:

```
=== PROCESSING COMPLETE ===
✅ Processed:
- 00091_Mongol_Empire
- 00094_Human_Memory

❌ Skipped:
- 00092_Egyptian_Warriors (Reason: Missing [image file])
- 00093_Atlantis_Myths (Reason: Both RAW & ASSETS found)

⚠️ Whisper Failed:
- 00091_Mongol_Empire (Reason: Failed to generate captions)

```

---

### 🪵 Logging

Each skipped or failed item is logged. Whisper logs are separate from FFmpeg logs.

---

### 🛑 Things Script Will NOT Do

- ❌ Create folders automatically
- ❌ Modify files outside the selected project folder
- ❌ Combine projects into a single video
- ❌ Run Whisper before FFmpeg is done

---

### ✅ Script Input Behavior

- Prompts user to select either:
    - Single `RAW` folder to process 1 project
    - Master folder to run batch mode
- Output filename = **name of parent folder** (auto)
- Script checks all rules **before** starting any render

---

### 📂 Example Folder States

Valid folder:

```
📁 00091_Mongol_Empire
└── 📁 RAW
    ├── image.jpg
    ├── video.mp4
    └── audio.mp3

```

Invalid (multiple audio):

```
📁 00092_Egyptian_Warriors
└── 📁 RAW
    ├── image.jpg
    ├── video.mp4
    ├── audio1.mp3
    └── audio2.wav

```

---

### **🔹 Updated Logic Before Running FFmpeg**

Before processing any `RAW` or `Assets` folder, the script will:

1. **Check if a completed video file already exists** in the **parent folder** of `RAW` or `Assets`.
2. If a **video file is found**, **skip that folder entirely** (assuming the project is already done).
3. If **no video file is found**, proceed with FFmpeg processing.

---

### **🔹 How This Works in Practice**

### **Example Folder Structure**

```
📂 My Cool Test Folder  <-- (YOU SELECT THIS FOLDER)
   ├── 📂 0108_Immortal_Pharaoh
   │     ├── 📂 RAW ✅  (Contains image, video, audio)
   │     ├── 0108_Immortal_Pharaoh.mp4 ✅  <-- (Already exists, script SKIPS this folder)
   │
   ├── 📂 0110_Ancient_Greece
   │     ├── 📂 RAW ✅  (Contains image, video, audio)
   │     ├── [NO EXISTING VIDEO]  <-- (Script processes this folder)
   │
   ├── 📂 0112_Unfinished_Project
   │     ├── 📂 RAW ❌ (Missing video file, script logs error and skips)

```

---

### **🚀 Next Step: Updating the Script**

I will now modify the script to:

- **Scan the master folder** for all subfolders.
- **Skip any subfolder** that already has a finished `.mp4` file.
- **Log the skipped folders** so you know which ones were ignored.

💡 **Anything else before I proceed?**

---

✅ This document is the **single source of truth** for all automation logic. ❗ Any updates must be clearly noted, versioned, and confirmed.

### Current Python Script March 22,2025

### **Script Overview and Current Progress**

1. **Goal of the Script**:
    - Process **image**, **video**, and **audio** files from the selected **RAW** folder, apply editing effects, and produce a final video.
    - **Image stays on screen for 1 second** at the start.
    - Combine **image** and **video** using FFmpeg.
    - **Generate captions** using Whisper AI from the edited video.
    - **Handle common errors** (missing files, invalid formats, etc.) gracefully.
2. **Key Features**:
    - **Image duration**: The image file stays visible for exactly **1 second**.
    - **File Structure**:
        - The script looks for a **RAW** folder containing **one image**, **one video**, and **one audio** file.
    - **Folder walk-through and RAW detection**: Scans each subfolder of a selected **Master Folder** for **RAW** folders.
    - **Error handling**: If files are missing or extra files are found, the script alerts the user and halts.
    - **Auto clean-up**: Removes `.DS_Store` and `temp_*.mp4` files after export.
    - **Export settings**:
        - Video **format**: **MP4** (H.264 codec, AAC audio codec).
        - Resolution: **1080x1920** (vertical, 9:16 ratio).
    - **File naming convention**: User-defined filenames for output video and captions.
3. **Functions to be Implemented**:
    - **Image duration**: The image should stay on the timeline for exactly **1 second** (not 5 seconds).
    - **Caption generation**: Whisper AI will generate captions from the final video.
4. **Script Workflow**:
    - **Step 1**: User selects a **Master Folder**.
    - **Step 2**: The script processes each subfolder, checking for the **RAW** folder with the necessary files.
    - **Step 3**: Image is displayed for **1 second** at the start of the video.
    - **Step 4**: Video and audio are combined.
    - **Step 5**: The script generates captions using Whisper AI.
    - **Step 6**: Clean-up of temporary files (e.g., `.DS_Store`, `temp_*.mp4`).
5. **Progress**:
    - **Successfully identified and processed subfolders**.
    - **Error handling in place** (missing files and folder structure errors).
    - **FFmpeg command** is set to ensure **1-second image duration** and **correct video output format**.
    - **Captions generated** using Whisper AI and exported as `.srt` files.
    - **Folder clean-up** (removes `.DS_Store`, and temp video files).

---

This outline reflects everything we’ve worked on. You can copy and paste this into a new chat, and we can continue building upon it or make necessary adjustments!

### Progress March 22 @ 6PM - Finish SRT to TXT

## 💡 What’s Next (Starting Fresh Tomorrow):

### 🔁 Rebuild `SRT_to_TXT_Description.py` to:

- ✅ Auto-classify the channel via GPT based on .srt content
- ✅ Generate **all output content** (title, description, etc.) using GPT
- ✅ Format and save output as `.txt` with same name as parent folder
- ✅ Fully follow your saved SEO formatting rules

---

## 🔄 Optional for Tomorrow:

- 🧠 Add **batching support**: Process 3–5 `.srt` files in one GPT call to reduce API cost
- 🧪 Add better parsing logic to split and save each `.txt` correctly after batch response
- 📂 Ensure outputs are saved cleanly with sanitized filenames

---

## 🔧 Ready-to-Go Inputs Tomorrow:

- ✅ `.srt` files already uploaded and tested
- ✅ Instruction Set already saved in Config
- ✅ GPT is pre-trained with your SEO formatting logic and tone

---

### 🛠️ No Dependencies Needed Tomorrow

You’re already inside your `whisper_env`, and all required libraries (e.g., `openai`, `os`, `re`, `tkinter`) are ready to go.

---

### 💾 Script Name in Progress:

`SRT_to_TXT_Description.py`

(Will be upgraded to use GPT for everything.)

---

Copy & paste this into your Notion, and we’ll hit the ground running tomorrow.

Sleep well, your automation empire awaits 😎💡

### Progress March 25 @ 11AM - ComfyUI Installed

### Update This: 5️⃣ ### Remove Text From Image

### Continue Mar 25 @2pm ChatGPT

### ****OLD****5️⃣ Remove Text From Image (OCR → Mask → ComfyUI Prep)

### Continue April 7@3pm ChatGPT

### Continue April 11@5:21pm ChatGPT

### Continue April 13@ 1:20pm ChatGPT

### Continue April 13 @ 4:53pm ChatGPT

### Terminal Commands

**Auto Shorts Editor V2**

<aside> 🎬

python3 /Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Auto_Shorts_Editor_V2.py

</aside>

---

**Activate and Run Whisper Transcription**

<aside> 🗣

source ~/Documents/Automations/ShortsEditorAI/whisper_env/bin/activate python3 /Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Whisper_Transcribe_SRT_V1.py

</aside>

**Active Whisper Environment**

<aside> 💡

source /Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/whisper_env/bin/activate

</aside>

**Run Whisper Script Once inside Whisper Environment**

<aside> 👟

python3 /Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Whisper_Transcribe_SRT_V1.py

</aside>

---

**Activate Whisper and Run SRT to TXT**

<aside> 📝

source ~/Documents/Automations/ShortsEditorAI/whisper_env/bin/activate python3 ~/Documents/Automations/ShortsEditorAI/SRT_to_TXT_Description_V3.0.py

</aside>

**Active Whisper Environment**

<aside> 💡

source /Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/whisper_env/bin/activate

</aside>

**Run SRT to TXT Script Once inside Whisper Environment**

<aside> 👟

python3 /Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/SRT_to_TXT_Description_V3.0.py

</aside>

### Terminal Cheatsheet

## 🚀 **Auto Shorts Editor V2.0 – Daily Workflow Commands**

---

### 🧬 **Activate the Whisper Environment**

`source ~/whisper_env/bin/activate`

### ❎ **Exit the Whisper Environment**

`deactivate`

### 📂 **Go to Project Folder**

`cd /Users/tonymacbook2025/Documents/Projects/ShortsEditorAI/`

### ✏️ **Edit Script (from inside folder)**

`nano Auto_Shorts_Editor_V2.py`

### ✏️ **Edit Script (from anywhere)**

`nano /Users/tonymacbook2025/Documents/Projects/ShortsEditorAI/Auto_Shorts_Editor_V2.py`

### 🏃 **Run Script**

`python3 Auto_Shorts_Editor_V2.py`

---

## ⚙️ **General Terminal Commands**

---

### 🧪 **Check If You’re Inside an Environment**

`which python`

(If the result contains `whisper_env`, you're in.)

### 🧹 **Remove .DS_Store Files**

`find . -name '.DS_Store' -delete`

### 🗂️ **List All .py Files in Current Folder**

`ls *.py`

### 🔄 **Rename a Python Script**

`mv old_name.py new_name.py`

### 📦 **Check If FFmpeg Is Installed**

`which ffmpeg`

### 🪪 **Check Python Version**

`python3 --version`

### 🗣️ **(Coming Soon) Run Whisper on a File Manually**

`whisper your_video.mp4 --model medium --output_format srt`

### Master Instruction Set V2.0 - March 24

# 🎬 Shorts Editor AI – Instruction Set v2.0

_(Modular System with Example-Only Paths – Do Not Hardcode)_

This is the master logic document that defines the behavior, structure, and automation flow of the Shorts Video Editing pipeline. It is built to allow scripts to run **individually or as a sequence**, with **no fixed directories** — all folder selection is **manual or user-triggered**.

---

## 📁 Project Structure — EXAMPLE ONLY

```
📂 [MASTER_FOLDER]          ← (You select this)
├── 📂 0108_Mongol_Empire   ← Parent folder (name used for output filenames)
│   ├── 📂 RAW or ASSETS     ← Contains 1 image, 1 video, 1 audio
│   │   ├── image.jpg
│   │   ├── video.mp4
│   │   ├── audio.mp3
│   ├── 0108_Mongol_Empire.mp4 ✅
│   ├── 0108_Mongol_Empire.srt ✅
│   ├── 0108_Mongol_Empire.txt ✅

```

> 🧠 EXAMPLE ONLY – DO NOT HARDCODE PATHS LIKE /Users/...
> 
> All scripts must prompt the user to select the working folder at runtime.

---

## 📦 File Validation Rules (Shared Across Scripts)

|Condition|Action|Reason|
|---|---|---|
|More than one image/video/audio|❌ Skip|"Multiple [type] files detected"|
|Missing any required file|❌ Skip|"Missing required file: [type]"|
|Both RAW and ASSETS exist|❌ Skip|"Both RAW and ASSETS found"|
|Output already exists|⏭️ Skip|"Output file already exists"|

---

## 🧠 Script Modules Overview

Each module below is its own Python script and is run manually or by a controller script.

---

## 1️⃣ Auto Shorts Video Edit Script V2.0

**Script Name:** `Auto_Shorts_Editor_V2.py`

**Function:** Combines image, video, and background audio into a short video.

### Features:

- Prompts user to select a **Master Folder**
- Searches each subfolder for RAW or ASSETS
- Validates and combines:
    - Image (1 sec intro)
    - Video (voiceover included)
    - Audio (background music mixed at ~-18 to -21 dB)
- Outputs `.mp4` named after parent folder
- Skips folders already containing an `.mp4` with matching name

✅ Output Format: `ParentFolderName.mp4`

✅ Uses `ffmpeg`, 1080x1920, H.264, AAC, faststart

❌ No zoom, transitions, or captioning included in this version

---

## 2️⃣ Whisper Transcribe Script (.srt)

**Script Name:** `Whisper_Transcribe_SRT_V1.py`

**Function:** Uses Whisper to generate subtitle files from final videos.

### Rules:

- Prompts user to select a **Master Folder**
- For each subfolder:
    - Only transcribes if `.mp4` exists AND matches the subfolder name
    - Skips if `.srt` already exists

✅ Output Format: `ParentFolderName.srt`

✅ Transcriptions are Whisper `.srt` format with timestamps

❌ Never reads files from RAW or ASSETS

---

## 3️⃣ SRT to TXT (SEO Metadata Generator)

**Script Name:** `SRT_to_TXT_Description_V2.0.py`

**Function:** Converts `.srt` captions into a `.txt` file with SEO metadata.

### Rules:

- Prompts user to select a **Master Folder**
- Scans each subfolder:
    - Runs only if `.srt` exists AND no `.txt` exists yet

✅ Output Format: `ParentFolderName.txt`

✅ Content:

```
TITLE: [Auto-generated title]
DESCRIPTION: [SEO-optimized summary]
HASHTAGS: #WhatIfHistory #BrainScience
KEYWORDS: comma,separated,keywords

```

📌 Follows niche-detection rules from transcript contents.

---

## 4️⃣ Run All in Sequence (Master Controller)

**Script Name:** `Master_Controller.py`

**Function:** Runs the three scripts above in order (modular, not merged).

### Behavior:

- Presents simple UI (menu or buttons)
- Runs:
    1. `Auto_Shorts_Editor_V2.py`
    2. `Transcribe_SRT.py`
    3. `SRT_to_TXT.py`
- Each script runs independently but in sequence
- Logs skipped folders and errors per module

✅ Modular structure = less bugs

✅ Easy to test each part

---

5️⃣ ### Remove Text From Image **Script Name: `Remove_Text_From_Image.py` ** Function: Detects and removes text from images. Saves a cleaned version of the image with `_BEGINNING_IMAGE` suffix. Optionally moves the original to an `/OLD` subfolder for backup.

### Modes:

- ✅ Batch Mode: Selects a **Master Folder** → scans all subfolders → processes RAW or ASSETS
- ✅ Single Folder Mode: Allows user to select **just one subfolder** via GUI
- ✅ GUI prompt asks: _"Process entire Master Folder (batch)?"_

### Image Logic:

- Looks for `RAW` or `ASSETS` subfolder (but **not both**)
- Finds **exactly one** `.jpg`, `.jpeg`, or `.png` inside
- ❌ Skips if none or more than one
- ❌ Skips if cleaned version already exists
- ✅ Saves cleaned image in **same folder** as original, named like:`OriginalName_BEGINNING_IMAGE.jpg`
- ✅ Moves original image to new `/OLD` folder (created if not exists)

### Output Example:

```
📂 Project_0101
├── 📂 RAW
│   ├── Gengis_Khan.jpg ← original (moved to /OLD)
│   ├── Gengis_Khan_BEGINNING_IMAGE.jpg ← cleaned version
│   ├── 📂 OLD
│   │   └── Gengis_Khan.jpg

```

---

## 🖥️ Terminal Menu UI (Example Only)

```
Welcome to Shorts Video Automation

Choose a script to run:
A) Auto Shorts Video Edit V2.0
B) Whisper Transcribe .SRT
C) SRT to TXT (SEO Title and Description)
D) Run All in Sequence
E) Remove Text From Image

```

Or future GUI version (as shown in design image) with clickable buttons.

---

## ⚠️ Important Script Behavior Rules

✅ All folder selection must be done using GUI prompts (no hardcoded paths)

✅ All output filenames must be auto-named:     - For video/text scripts, use subfolder name (e.g., 0108_Project.mp4)     - For image scripts, use original filename with suffix (e.g., Gengis_Khan_BEGINNING_IMAGE.jpg)

✅ Scripts must skip processing if outputs already exist

❌ Never assume file names, directory names, or folder structure beyond what is described

❌ Do NOT hardcode paths like /Users/tonymacbook2025/...

---

### Instruction Set V3.0 Backup from April 14 2025

# 🎬 Shorts Editor AI – Instruction Set v3.0

_(Modular System with Example-Only Paths – Do Not Hardcode)_

This is the master logic document that defines the behavior, structure, and automation flow of the Shorts Video Editing pipeline. It is built to allow scripts to run **individually or as a sequence**, with **no fixed directories** — all folder selection is **manual or user-triggered**.

---

## 📁 Project Structure — EXAMPLE ONLY

```
📂 [MASTER_FOLDER]          ← (You select this)
├── 📂 0108_Mongol_Empire   ← Parent folder (name used for output filenames)
│   ├── 📂 RAW or ASSETS     ← Contains 1 image, 1 video, 1 audio
│   │   ├── image.jpg
│   │   ├── video.mp4
│   │   ├── audio.mp3
│   ├── 0108_Mongol_Empire.mp4 ✅
│   ├── 0108_Mongol_Empire.srt ✅
│   ├── 0108_Mongol_Empire.txt ✅

```

> 🧠 EXAMPLE ONLY – DO NOT HARDCODE PATHS LIKE /Users/...
> 
> All scripts must prompt the user to select the working folder at runtime.

---

## 📦 File Validation Rules (Shared Across Scripts)

|Condition|Action|Reason|
|---|---|---|
|More than one image/video/audio|❌ Skip|"Multiple [type] files detected"|
|Missing any required file|❌ Skip|"Missing required file: [type]"|
|Both RAW and ASSETS exist|❌ Skip|"Both RAW and ASSETS found"|
|Output already exists|⏭️ Skip|"Output file already exists"|

---

## 🧠 Script Modules Overview

Each module below is its own Python script and is run manually or by a controller script.

## 1️⃣ 01_Thumbnail_Rename_Filename.py {Single and Batch}

- *Status: Working with Apple Shortcut and Python ✅

—-

## 2️⃣ 02_ThumbnailProcessor_V5.1.jsx {Single and Batch}

- *Status: Working with Apple Shortcut and Photoshop ✅

---

## 3️⃣ Auto Shorts Video Edit Script V2.0

- *Status: Working with Apple Shortcut and Python ✅

**Script Name:** `03_Auto_Shorts_Editor_V2.py {Batch Mode}` `03_Auto_Shorts_Editor_V2.5-SINGLE_MODE.py`**Function:** Combines image, video, and background audio into a short video.

### Features:

- Prompts user to select a **Master Folder**
- Searches each subfolder for RAW or ASSETS
- Validates and combines:
    - Image (1 sec intro)
    - Video (voiceover included)
    - Audio (background music mixed at ~-18 to -21 dB)
- Outputs `.mp4` named after parent folder
- Skips folders already containing an `.mp4` with matching name

✅ Output Format: `ParentFolderName.mp4`

✅ Uses `ffmpeg`, 1080x1920, H.264, AAC, faststart

❌ No zoom, transitions, or captioning included in this version

---

## 4️⃣ Whisper Transcribe Script (.srt)

- *Status: Broke ❌

**Script Name:** `04_Whisper_Transcribe_SRT_V1.5-SINGLE_MODE.py``04_Whisper_Transcribe_SRT_V1.py {Batch Mode}`**Function:** Uses Whisper to generate subtitle files from final videos.

### Rules:

- Prompts user to select a **Master Folder**
- For each subfolder:
    - Only transcribes if `.mp4` exists AND matches the subfolder name
    - Skips if `.srt` already exists

✅ Output Format: `ParentFolderName.srt`

✅ Transcriptions are Whisper `.srt` format with timestamps

❌ Never reads files from RAW or ASSETS

---

## 5️⃣ SRT to TXT (SEO Metadata Generator)

- *Status: Broke ❌ **Script Name:** `05_SRT_to_TXT_Description_V3.0.py {Batch Mode}` `05_SRT_to_TXT_Description_V3.0-SINGLE-MODE_FINAL_LOCKED.py`**Function:** Converts `.srt` captions into a `.txt` file with SEO metadata.

### Rules:

- Prompts user to select a **Master Folder**
- Scans each subfolder:
    - Runs only if `.srt` exists AND no `.txt` exists yet

✅ Output Format: `ParentFolderName.txt`

✅ Content:

```
TITLE: [Auto-generated title]
DESCRIPTION: [SEO-optimized summary]
HASHTAGS: #WhatIfHistory #BrainScience
KEYWORDS: comma,separated,keywords

```

📌 Follows niche-detection rules from transcript contents.

---

## ⚠️ Important Script Behavior Rules

✅ All folder selection must be done using GUI prompts (no hardcoded paths)

✅ All output filenames must be auto-named:     - For video/text scripts, use subfolder name (e.g., 0108_Project.mp4)     - For image scripts, use original filename with suffix (e.g., Gengis_Khan_BEGINNING_IMAGE.jpg)

✅ Scripts must skip processing if outputs already exist

❌ Never assume file names, directory names, or folder structure beyond what is described

❌ Do NOT hardcode paths like /Users/tonymacbook2025/... (Unless it is needed for script to run, but ask permission first)

✅ Ask clarifying questions in the information you have conflicts with any logic to preform your task and make sure you are 95% sure you can complete your task before proceeding.

---

## 📌 Source-of-Truth Reference Policy (MANDATORY)

> 🧠 ALWAYS refer to uploaded scripts and config files as the source of truth.
> 
> These files represent validated, fully tested logic. Never assume simplification is safe.

### 🔒 Edit Policy:

1. ✅ Only make changes that are **explicitly requested**
2. ✅ Cross-reference any logic that appears unclear with **uploaded reference files**
3. ❌ **Do not strip, refactor, or “clean up” working code** — even if it seems redundant or verbose
4. ✅ Assume downstream dependencies (e.g. `.jsx` overlay, SEO parsers) rely on current structure
5. ✅ Confirm use of critical tools like OpenAI before removing or replacing related logic

> Summary: If it's not broken — don't touch it. Ask first.
> 
> These scripts are part of a tested automation chain, not standalone experiments.

---

