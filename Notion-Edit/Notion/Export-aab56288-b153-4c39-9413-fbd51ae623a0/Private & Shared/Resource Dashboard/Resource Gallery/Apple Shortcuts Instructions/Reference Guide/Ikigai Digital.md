---
Category: Ikigai Digital
---
# Generate Asset Folders

> [!important]
> 
> Shell Command inside the Apple Shortcut
> 
> # ✅ **What This Script Does (Plain English)**
> 
> - It **moves into the folder** you selected (the `$1` argument).
> 
> - If it can’t open that folder, it **stops immediately**.
> 
> - Inside that folder, it **creates a set of standard subfolders** used for your workflow:
>     
>     - **01-Printables**
>     
>     - **02-Thumbnails**
>     
>     - **03-Etsy Images**
>     
>     - **04-Google Drive**
>     
>     - **Originals**
>     
>     - **Reference**
>     
> 
> - If any of these folders already exist, they are simply **left in place**.
> 
> - This helps keep every project organized the exact same way.
> 
> ---
> 
> # 📄 **Step-By-Step (Human-Friendly)**
> 
> 1. You run the script and pass in a folder.
> 
> 1. The script enters that folder.
> 
> 1. It builds your standard folder structure for new art/printable projects.
> 
> 1. Everything is now clean and ready for you to drop assets in the correct places.
> 
> ---
> 
> # 🎯 **Use Case**
> 
> Perfect for quickly setting up a **new Etsy/printable project folder template** with all your required subfolders ready to go.
> 
> ---
# Ikigai Single Crops 2:3 Ratio 7200x10800px

> [!important]
> 
> Script in _**Automations/IkigaiDigital/ikigai_cropper_fixed.py**_
> 
> # ✅ **ikigai_cropper_fixed.py — What It Does**
> 
> This script takes **one image** you select and automatically creates **multiple perfectly cropped, printable versions** in all your standard Ikigai wall-art sizes.
> 
> It outputs everything into your fixed folder:
> 
> **Desktop → Ikigai Process**
> 
> ---
> 
> # 📄 **Plain-English Summary**
> 
> - Opens a file picker asking you to choose **one image**.
> 
> - Automatically creates 5 different **print-ready crops** of that image:
>     
>     - **2x3 ratio** (24×36 in)
>     
>     - **4x5 ratio** (24×30 in)
>     
>     - **11x14 in**
>     
>     - **3x4 ratio** (18×24 in)
>     
>     - **ISO A1** (23.4×33.1 in)
>     
> 
> - Each size is exported at **high resolution** (thousands of pixels).
> 
> - Crops are centered so the subject stays balanced.
> 
> - Saves all final images into **Ikigai Process** on your Desktop.
> 
> - Automatically creates the output folder if it doesn’t exist.
> 
> ---
> 
> # 🔧 **Step-By-Step (Human-Friendly)**
> 
> 1. You run the script (or via Apple Shortcut).
> 
> 1. A window opens → you pick one image file.
> 
> 1. The script loads the image.
> 
> 1. For each target print size:
>     
>     - Calculates the correct crop
>     
>     - Crops the image while preserving as much content as possible
>     
>     - Exports a perfectly sized, print-ready version
>     
> 
> 1. Puts all exported versions into:
>     
>     **~/Desktop/Ikigai Process**
>     
> 
> 1. Done.
> 
> ---
> 
> # 🎯 **Use Case (Why You Use This Script)**
> 
> This is your **Ikigai wall-art auto-sizer**, used for:
> 
> - Etsy printable sets
> 
> - Digital downloads
> 
> - Your 5-size bundle workflow
> 
> - Ensuring perfect aspect ratios for all print formats
> 
> It eliminates manual cropping in Photoshop and ensures your output is always consistent, professional, and ready to upload.
> 
> ---
# Ikigai Thumbnail Process

> [!important]
> 
> Script in _**Automations/IkigaiDigital/ikigai_thumbnail.py**_
> 
> # ✅ **ikigai_thumbnail.py — What It Does**
> 
> This script takes a folder of large/high-resolution images and creates a **72 DPI thumbnail version** of each one.
> 
> It works on an entire folder at once, and organizes all thumbnails into a new subfolder called:
> 
> **_thumbnails**
> 
> inside the same directory.
> 
> ---
> 
> # 📄 **Plain-English Summary**
> 
> - Opens a Finder popup asking you to pick any folder of images.
> 
> - Scans the folder for supported image types (JPG, PNG, TIFF, etc.).
> 
> - Creates a new folder called **_thumbnails**.
> 
> - For each image:
>     
>     - Converts it to **72 DPI**
>     
>     - Keeps the original filename
>     
>     - Adds **_TN** before the file extension
>     
>     - Saves it inside the _thumbnails folder
>     
> 
> - Prints progress for each converted image.
> 
> - Ends with a “All images processed” message.
> 
> ---
> 
> # 🔧 **Step-By-Step (Human-Friendly)**
> 
> 1. You run the script (via Python or Apple Shortcuts).
> 
> 1. A Finder dialog appears → you pick a folder of images.
> 
> 1. The script automatically creates a folder named:
>     
>     **/your-folder/_thumbnails**
>     
> 
> 1. For each original image it:
>     
>     - Opens it
>     
>     - Converts it to 72 DPI
>     
>     - Resizes according to the script’s logic (keeps image dimensions, just exports at 72 DPI)
>     
>     - Saves a new version named:
>         
>         **filename_TN.jpg** or **filename_TN.png**
>         
>     
> 
> 1. Prints each thumbnail created.
> 
> 1. Shows a final success checkmark.
> 
> ---
> 
> # 🎯 **Use Case (Why You Use This Script)**
> 
> Great for:
> 
> - Etsy listing thumbnails
> 
> - Website image optimization
> 
> - Light versions for Previews / PDFs
> 
> - Large galleries that need quick smaller previews
> 
> - Speeding up upload times and storage usage
> 
> This is your **bulk thumbnail converter** for Ikigai workflows.
> 
> ---
# Batch Listing Mockups 01-03

> [!important]
> 
> Script in _**Automations/IkigaiDigital/Ikigai_mockup_launcher.py**_
> 
> # ✅ **Ikigai_mockup_launcher.py — What It Does**
> 
> This is your **one-click launcher** for creating Ikigai mockups.
> 
> It bridges **Photoshop**, your **JSX automation**, and your **video renderer** so they run in the correct order automatically.
> 
> ---
> 
> # 📄 **Plain-English Summary**
> 
> - Opens a file picker asking you to choose **one artwork image**.
> 
> - Saves the path of that artwork into a small temporary text file.
> 
> - Uses AppleScript to launch **Photoshop** and run your JSX file:
>     
>     **Ikigai_Batch_StaticOnly.jsx**
>     
> 
> - The JSX uses the artwork to generate your **static mockups**.
> 
> - Waits a few seconds for Photoshop to finish.
> 
> - Then launches your Python video renderer script:
>     
>     **Ikigai_Video_Renderer.py**
>     
> 
> - That script generates the **animated mockups**.
> 
> - Ends after kicking off both processes successfully.
> 
> ---
> 
> # 🔧 **Step-By-Step (Human-Friendly)**
> 
> 1. You run the launcher (or trigger it from Shortcuts).
> 
> 1. A Finder dialog appears → you choose your artwork file.
> 
> 1. Script writes the artwork’s path into:
>     
>     **tmp_artwork_path.txt**
>     
> 
> 1. Script tells Photoshop to open and run your JSX automation.
>     
>     - JSX reads the artwork path
>     
>     - Inserts artwork into your mockup templates
>     
>     - Generates all static mockup images
>     
> 
> 1. Script waits ~5 seconds to let Photoshop settle.
> 
> 1. Script launches your Python video renderer.
>     
>     - Creates video mockups
>     
> 
> 1. Terminal prints confirmations for every step.
> 
> ---
> 
> # 🎯 **Use Case (Why You Use This Script)**
> 
> This script is your **Ikigai Mockup Master Button**, used for:
> 
> - Running Photoshop static mockup generation
> 
> - Followed immediately by video mockup creation
> 
> - Starting everything from a single click
> 
> - Avoiding manual launching of JSX + Python steps
> 
> - Making your Apple Shortcut workflow seamless
> 
> Perfect for Etsy, Printify, or large-batch mockup automation.
# Zoom Detail Mockup

> [!important]
> 
> Script in _**Automations/IkigaiDigital/Ikigai_detail_zoom_launcher.py**_
> 
> # ✅ **Ikigai_detail_zoom_launcher.py — What It Does**
> 
> This script launches your **Ikigai Zoom Mockup** workflow.
> 
> It sends an artwork file into Photoshop, which then runs your **Ikigai_Zoom_Mockup.jsx** to generate **close-up zoom detail mockup images**.
> 
> ---
> 
> # 📄 **Plain-English Summary**
> 
> - Shows a Finder window asking you to choose **one artwork file**.
> 
> - Saves the chosen artwork path into a small text file that the JSX script reads.
> 
> - Sends a command to Photoshop via AppleScript to open and run your JSX:
>     
>     **Ikigai_Zoom_Mockup.jsx**
>     
> 
> - Photoshop uses your templates to generate zoomed-in detail shots of your art.
> 
> - The Python script ends once Photoshop has started processing.
> 
> ---
> 
> # 🔧 **Step-By-Step (Human-Friendly)**
> 
> 1. You run the launcher (or call it from an Apple Shortcut).
> 
> 1. A file picker opens → you select an artwork PNG/JPG.
> 
> 1. The script saves that file path to:
>     
>     **ikigai_detail_zoom_launcher.txt**
>     
> 
> 1. The script commands Photoshop to launch and run your Zoom Mockup JSX.
> 
> 1. The JSX script:
>     
>     - Reads the artwork path
>     
>     - Inserts your artwork into the mockup template
>     
>     - Generates your **zoom-in detail mockups**
>     
> 
> 1. The launcher exits once Photoshop starts working.
> 
> ---
> 
> # 🎯 **Use Case (Why You Use This Script)**
> 
> This is your **Zoom Detail Mockup Launcher** for Ikigai:
> 
> - Creates close-up Etsy detail images
> 
> - Automates Photoshop mockup templates
> 
> - Works alongside your main Ikigai mockup launcher
> 
> - Used when you need zoomed-in product shots for listings
> 
> - Keeps your workflow fast and consistent
# Tokenize Image Compress

> [!important]
> 
> Script in _**Automations/IkigaiDigital/Tokenized_Image_Compressor.py**_
# ✅ **Tokenized_Image_Compressor.py — What It Does**
This script takes a folder of **screenshots or images** and converts them into **lightweight, optimized 72-DPI JPEGs**.
It’s designed to quickly shrink file sizes for uploads, tokens, previews, or workflow automation.
---
# 📄 **Plain-English Summary**
- A Finder window opens asking you to pick **a folder of images**.
- Creates a new folder inside it called:
    
    **_compressed**
    
- For every PNG, TIFF, or JPG in the folder:
    
    - Converts it to **JPEG**
    
    - Sets the DPI to **72**
    
    - Applies **optimized JPEG compression** (quality 85)
    
    - Saves the converted version into the _compressed folder
    
    - Keeps the same filename (but `.jpg`)
    
- Skips any files it can’t read.
- Prints each conversion result and shows a final summary.
---
# 🔧 **Step-By-Step (Human-Friendly)**
1. You run the script (or through a Shortcut).
1. You select a folder with images or screenshots.
1. The script creates inside it:
    
    **/your-folder/_compressed**
    
1. For each image it:
    
    - Opens it
    
    - Converts it to JPEG
    
    - Sets DPI = 72
    
    - Applies compression
    
    - Saves optimized version
    
1. Shows progress for each file.
1. Ends with “Done! Optimized JPEGs saved in: _compressed”.
---
# 🎯 **Use Case (Why You Use This Script)**
This is your **Image Size Optimizer** for:
- Prepping assets for tokenization
- Compressing screenshots used in automation
- Previews for Sora / Kling / AI workflows
- Making lighter images for Notion or Google Drive
- Batch compressing assets before upload
- Quickly shrinking large PNGs
It standardizes everything at 72 DPI and creates small, fast-loading JPEGs.