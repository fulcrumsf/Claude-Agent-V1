---
Category: Audio
---
## **What This Script Does (Simple Summary)**
- Looks inside a specific **audio folder** on your computer.
- Finds every **MP3 or WAV file** in that folder.
- For each audio file, it:
    
    - Loads the audio
    
    - Measures qualities like tempo, loudness, pitch, energy, etc
    
    - Packs all those measurements into a structured report
    
- Saves a **JSON file** for each audio file into a separate output folder.
- The JSON file becomes a “profile” of the audio’s characteristics.
- Prints a confirmation in the console each time it finishes analyzing a file.
---
## **Step-By-Step (Plain English)**
1. **Open the audio folder** you set inside the script.
1. **Check every file** and only pick ones that are MP3 or WAV.
1. For each usable file:
    
    - Open it
    
    - Break the audio into pieces
    
    - Analyze its sound qualities
    
    - Convert all results into a friendly JSON object
    
1. **Save the analysis** as a JSON file with the same name as the audio.
1. Put that JSON into your **json_outputs** folder.
1. Print a message telling you the file was analyzed.
---