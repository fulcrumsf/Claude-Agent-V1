---
Description: Takes videos from Google Drive and automates the video editing to a finished product with .SRT file
Status: In Progress
tags:
  - Video
Related Database: Document Storage
---
[[Archive]]
### Terminal Commands
**Auto Shorts Editor V2**

> [!important]
> 
> python3 /Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Auto_Shorts_Editor_V2.py
---
**Activate and Run Whisper Transcription**

> [!important]
> 
> source ~/Documents/Automations/ShortsEditorAI/whisper_env/bin/activate  
> python3 /Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Whisper_Transcribe_SRT_V1.py
**Active Whisper Environment**

> [!important]
> 
> source /Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/whisper_env/bin/activate
**Run Whisper Script Once inside Whisper Environment**

> [!important]
> 
> python3 /Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/Whisper_Transcribe_SRT_V1.py
---
**Activate Whisper and Run SRT to TXT**

> [!important]
> 
> source ~/Documents/Automations/ShortsEditorAI/whisper_env/bin/activate  
> python3 ~/Documents/Automations/ShortsEditorAI/SRT_to_TXT_Description_V3.0.py
**Active Whisper Environment**

> [!important]
> 
> source /Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/whisper_env/bin/activate
**Run SRT to TXT Script Once inside Whisper Environment**

> [!important]
> 
> python3 /Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/SRT_to_TXT_Description_V3.0.py
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
|   |   |   |
|---|---|---|
|Condition|Action|Reason|
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
HASHTAGS: \#WhatIfHistory \#BrainScience
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
    
    1. `Transcribe_SRT.py`
    
    1. `SRT_to_TXT.py`
    
- Each script runs independently but in sequence
- Logs skipped folders and errors per module
✅ Modular structure = less bugs
✅ Easy to test each part
---
5️⃣ ### Remove Text From Image  
**Script Name: `Remove_Text_From_Image.py`  
** Function: Detects and removes text from images. Saves a cleaned version of the image with `_BEGINNING_IMAGE` suffix. Optionally moves the original to an `/OLD` subfolder for backup.
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
✅ All output filenames must be auto-named:  
    - For video/text scripts, use subfolder name (e.g., 0108_Project.mp4)  
    - For image scripts, use original filename with suffix (e.g., Gengis_Khan_BEGINNING_IMAGE.jpg)
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
|   |   |   |
|---|---|---|
|Condition|Action|Reason|
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
- *Status: Broke ❌**Script Name:** `05_SRT_to_TXT_Description_V3.0.py {Batch Mode}` `05_SRT_to_TXT_Description_V3.0-SINGLE-MODE_FINAL_LOCKED.py`**Function:** Converts `.srt` captions into a `.txt` file with SEO metadata.
### Rules:
- Prompts user to select a **Master Folder**
- Scans each subfolder:
    
    - Runs only if `.srt` exists AND no `.txt` exists yet
    
✅ Output Format: `ParentFolderName.txt`
✅ Content:
```
TITLE: [Auto-generated title]
DESCRIPTION: [SEO-optimized summary]
HASHTAGS: \#WhatIfHistory \#BrainScience
KEYWORDS: comma,separated,keywords
```
📌 Follows niche-detection rules from transcript contents.
---
## ⚠️ Important Script Behavior Rules
✅ All folder selection must be done using GUI prompts (no hardcoded paths)
✅ All output filenames must be auto-named:  
    - For video/text scripts, use subfolder name (e.g., 0108_Project.mp4)  
    - For image scripts, use original filename with suffix (e.g., Gengis_Khan_BEGINNING_IMAGE.jpg)
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
1. ✅ Cross-reference any logic that appears unclear with **uploaded reference files**
1. ❌ **Do not strip, refactor, or “clean up” working code** — even if it seems redundant or verbose
1. ✅ Assume downstream dependencies (e.g. `.jsx` overlay, SEO parsers) rely on current structure
1. ✅ Confirm use of critical tools like OpenAI before removing or replacing related logic

> Summary: If it's not broken — don't touch it. Ask first.
> 
> These scripts are part of a tested automation chain, not standalone experiments.
---