This workflow covers both The Brain Blueprint & Reimagined Realms
# Raw Video to Parent Folder

> [!important]
> 
> # RAW Video to Parent Folder
> 
> Script in _**Automations/ShortsEditorAI/00_Video_Rename_From_Folder.sh**_
> 
> ---
> 
> # ✅ **Plain-English Summary**
> 
> - You pick a **main folder** using a folder picker.
> 
> - The script looks inside every folder **inside** that main folder.
> 
> - For each subfolder, it looks for a **RAW** folder.
> 
> - Inside each RAW folder, it finds **the first video file** (MP4, MOV, MKV).
> 
> - It **renames** that video so the filename matches the **parent folder name**.
> 
> - The file keeps its original extension.
> 
> - Everything happens automatically for every subfolder.
> 
> ---
> 
> # 📄 **Step-By-Step (Human-friendly)**
> 
> 1. A popup asks you:
>     
>     **“Select the parent folder containing your video folders.”**
>     
> 
> 1. The script scans every folder inside the one you chose.
> 
> 1. For each folder:
>     
>     - It checks if there is a subfolder named **RAW**.
>     
>     - It finds the **first video** inside RAW.
>     
> 
> 1. It renames that video to:
>     
>     **ParentFolderName.extension**
>     
>     (example: `00123_Time_Piece.mp4`)
>     
> 
> 1. If there is no video or no RAW folder, it prints a warning.
> 
> 1. Moves on to the next folder automatically.
> 
> ---
> 
> # 🧠 **Use Case (Why You’d Use This Shortcut)**
> 
> Perfect for workflows where each project folder contains one RAW video, and you want all videos cleanly named based on their folder names.
> 
> ---
> 
> If you want, I can convert this into a **Notion-ready template** or a **Shortcuts-friendly notes block** formatted exactly for your folders.
# ScreenShot Video Master

> [!important]
> 
> Script in _**Automations/ShortsEditorAI/00_Master_Screenshot_Video.sh**_
> 
> ---
> 
> # ✅ **Plain-English Summary**
> 
> - You choose a **main folder** using a folder picker.
> 
> - The script looks inside every subfolder of that main folder.
> 
> - For each subfolder, it checks for a **RAW** folder.
> 
> - Inside each RAW folder, it finds **all videos** (MP4, MOV, MKV).
> 
> - For every video, it takes a **screenshot at the 1-second mark**.
> 
> - It saves that screenshot as a **1080x1920 JPG** next to the video.
> 
> - Each screenshot is named after the video (same name, `.jpg` extension).
> 
> ---
> 
> # 📄 **Step-By-Step (Human-Friendly)**
> 
> 1. A popup asks you:
>     
>     **“Select the base folder containing your video subfolders.”**
>     
> 
> 1. The script scans through all folders inside the one you selected.
> 
> 1. For each folder:
>     
>     - Looks for a subfolder named **RAW**.
>     
>     - Inside RAW, finds every video (mp4/mov/mkv).
>     
> 
> 1. For each video:
>     
>     - Takes a frame exactly at **00:00:01**
>     
>     - Automatically resizes and pads it to **vertical 1080x1920**
>     
>     - Saves the result as `.jpg` in the same RAW folder
>     
> 
> 1. Repeats this for every video in every folder.
> 
> ---
> 
> # 🎯 **Use Case (Why You’d Use This Shortcut)**
> 
> Perfect for workflows where each project’s RAW video needs a **vertical thumbnail/screenshot** to feed into:
> 
> - AI video tools
> 
> - Image-to-video models
> 
> - Thumbnail pipelines
> 
> - Batch workflows
> 
> - ComfyUI / n8n / FFmpeg automation
> 
> ---
> 
> If you'd like, I can create:
> 
> - A formatted **Notion cheat-sheet section**,
> 
> - A standardized **Shortcut Notes block**, or
> 
> - A combined **“Folder Notes” shortcut template** for all your scripts.
> 
>   
# 1st Step Thumbnail Rename

> [!important]
> 
> Script in **Automations/ShortsEditorAI/01_Thumbnail_Rename_Filename.py**  
> 
> ---
> 
> # ✅ **Plain-English Summary**
> 
> - You choose a folder using a popup window.
> 
> - The script looks for **image files** (PNG/JPG/JPEG) in that folder.
> 
> - It cleans the filenames by removing ugly characters, symbols, or formatting.
> 
> - Sends the cleaned name to the OpenAI API to generate a **better, human-readable title**.
> 
> - Renames the image file to that new title.
> 
> - Keeps the same file extension.
> 
> - Creates a log file on your Desktop showing:
>     
>     - Old name
>     
>     - Cleaned name
>     
>     - AI-generated final name
>     
> 
> - Shows pop-up messages for success or errors.
> 
> ---
> 
> # 📄 **Step-By-Step (Human-Friendly)**
> 
> 1. A folder picker opens — you choose the folder containing your **thumbnail images**.
> 
> 1. Script finds all `.png`, `.jpg`, `.jpeg` files.
> 
> 1. For each image:
>     
>     - Cleans the filename (removes characters like `_`, , numbers, brackets, etc.).
>     
>     - Sends that cleaned name to OpenAI to generate a **proper thumbnail title**.
>     
>     - Renames the file with this new title.
>     
> 
> 1. Writes a log file to your Desktop:
>     
>     **Thumbnail Image Renamer.txt**
>     
> 
> 1. Shows a success popup telling you everything is done.
> 
> ---
> 
> # 🎯 **Use Case (Why You’d Use This Shortcut)**
> 
> Great for batching renames of:
> 
> - AI-generated thumbnails
> 
> - Video thumbnails
> 
> - Social media images
> 
> - Assets needing human-readable names
> 
> - Images that will be fed into your **ComfyUI / n8n** automated process
> 
> Keeps your filenames clean, searchable, and nicely titled.
> 
> ---
> 
> If you want, I can generate a matching **Notion cheat-sheet card** or a **Shortcuts Notes template** you can paste inside your Notion folder.
> 
>   
# 2nd Step Thumbnail Gen

> [!important]
> 
> Script in **Automations/Photoshop/Scripts:02_ThumbnailProcessor_V5.1.jsx**
> 
> # ✅ **Plain-English Summary**
> 
> - Opens a popup letting you choose **batch mode** (process many) or **single mode** (process one).
> 
> - Uses your **Thumbnail Template.psd** to generate final thumbnail images.
> 
> - Finds the correct **RAW / ASSET / ASSETS** folder in each project folder.
> 
> - Finds exactly **one image** that has **NOT** already been processed (no `_DONE` in its name).
> 
> - Automatically inserts that image into the Photoshop template.
> 
> - Runs your **Generative Fill action** in Photoshop.
> 
> - Updates the **title text** using the image filename (split into vertical stacked text).
> 
> - Exports the finished thumbnail as **_DONE.jpg**.
> 
> - Moves the original image into an **Intermediate** subfolder.
> 
> - Logs everything into a text file on your Desktop.
> 
> - Closes the PSD and repeats for each folder in batch mode.
> 
> ---
> 
> # 📄 **Step-By-Step (Human-Friendly)**
> 
> ### **A) If you choose BATCH MODE**
> 
> 1. A folder picker appears → choose a **MASTER folder** containing multiple project folders.
> 
> 1. Script scans each project folder:
>     
>     - Identifies **RAW**, **Asset**, or **Assets** folder
>     
>     - Finds **1 image** inside it
>     
>     - Skips if there are none or more than one
>     
> 
> 1. For each valid folder:
>     
>     - Opens your **Thumbnail_Template.psd**
>     
>     - Inserts the selected image into the “Place Image Here” layer
>     
>     - Runs your Photoshop Generative Fill action
>     
>     - Opens the “Title” smart object and updates the text based on the filename
>     
>     - Exports a final JPG with `_DONE.jpg` added to the name
>     
>     - Moves the original image into an **Intermediate** folder
>     
>     - Logs all actions
>     
> 
> ### **B) If you choose SINGLE MODE**
> 
> 1. You choose one image manually.
> 
> 1. It processes it exactly the same way as above.
> 
> ---
> 
> # 🎯 **Use Case (Why You Use This Script)**
> 
> Perfect for your automated YouTube/TikTok/Shorts pipeline where:
> 
> - Each video folder contains one thumbnail image
> 
> - You want to quickly generate consistent, editable Photoshop thumbnails
> 
> - You want auto-text based on the image filename
> 
> - You want clean exports + organized originals
> 
> - You run this manually or inside Apple Shortcuts as part of your automation stack
# 3rd Step Auto Edit>SRT>TXT

> [!important]
> 
> Script in _**Automations/ShortsEditorAI/Master_Controller_V1.9.py**_
> 
> # ✅ **Plain-English Summary**
> 
> - Pops open a window asking you to choose a folder or video directory.
> 
> - Lets you choose whether you want **Single Mode** (one video) or **Batch Mode** (many).
> 
> - Lets you choose which **channel workflow** you’re running (Reimagined Realms, etc.).
> 
> - Activates your custom **Whisper virtual environment**.
> 
> - Automatically runs a sequence of other automation scripts stored in your Master Controller folder.
> 
> - Handles the full pipeline:
>     
>     - Extracts audio
>     
>     - Transcribes using Whisper
>     
>     - Cleans subtitles
>     
>     - Generates titles/descriptions/tags
>     
>     - Passes metadata into text-generation scripts
>     
>     - Builds Reimagined Realms narration scripts
>     
> 
> - Keeps a running log on your Desktop.
> 
> - Shows a final “processing complete” message when all sub-scripts have finished.
> 
> ---
> 
> # 📄 **Step-By-Step (Human-Friendly)**
> 
> ### **1. User chooses a main folder**
> 
> A window opens asking you to select:
> 
> - A **single video folder**, or
> 
> - A **master folder containing multiple videos**.
> 
> ### **2. User picks the workflow mode**
> 
> You choose:
> 
> - **Single Mode** → processes one video
> 
> - **Batch Mode** → processes every video subfolder
> 
> ### **3. User picks the channel type**
> 
> Options might be like:
> 
> - Reimagined Realms
> 
> - Neon Parcels
> 
> - Other channel presets
>     
>     The script adjusts the workflow based on this.
>     
> 
> ### **4. Script activates Whisper environment**
> 
> Loads the `.env` file and activates your Whisper Python environment so transcription tools run correctly.
> 
> ### **5. Master Controller launches sub-scripts one by one**
> 
> Depending on mode and channel, it kicks off scripts such as:
> 
> - Audio extractor
> 
> - Whisper transcription
> 
> - Subtitle cleaner
> 
> - TXT-to-Narration generator
> 
> - Metadata generator (titles/descriptions/tags)
> 
> - Reimagined TXTs, Single or Batch versions
> 
> - Any additional automation scripts in your workflow
> 
> Each sub-script is run using **subprocess**, so they execute in order.
> 
> ### **6. Creates a Desktop log file**
> 
> Tracks everything the controller is doing so you have a full audit trail.
> 
> ### **7. Shows final completion message**
> 
> Once all sub-scripts finish, it prints/logs:
> 
> **“Master Controller processing complete.”**
> 
> ---
> 
> # 🎯 **Use Case (Why You Use This Script)**
> 
> This is your **main automation brain** for video processing.
> 
> It centralizes and simplifies:
> 
> - Transcription
> 
> - Script generation
> 
> - Metadata creation
> 
> - Batch video workflows
> 
> - Reimagined Realms narration pipeline
> 
> You run _one_ script instead of manually running 6–10 different scripts.
> 
> ---