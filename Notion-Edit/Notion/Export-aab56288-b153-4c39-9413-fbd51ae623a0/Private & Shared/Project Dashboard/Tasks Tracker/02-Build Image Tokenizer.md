---
Status: Done
Priority: High
Task type:
  - Automation
Effort level: Medium
Description: Change to Google Drive
"Priority #": P1
---
### **1. Image Tokenization Workflow (Automation #1)**
- **Image folder** in Google Drive to collect new images for tokenization.
- **Rube/n8n automation** to tokenize each image automatically.
- **Rename** automatically names the image based on the token with underscores
- **Google Sheet (or Baserow table)** to log the generated token and image info.
- **File labeling and moving automation** to organize tokenized images into their proper folders.
- **Database entry creation process** to record new image data after labeling.
## ⚙️ **Workflow 1: Image Tokenization Automation**
### **1. Image Folder Watcher**
- [ ] **Tool:** Google Drive Trigger
- [ ] **Trigger:** New file added to designated “Image Upload” folder
- [ ] **Action:** Start the workflow
- [ ] **Output:** File metadata (name, path, URL)
### **2. Tokenization Step**
- [ ] **Tool:** HTTP Request or Rube webhook
- [ ] **Action:** Send the image file (or URL) to the tokenization service
- [ ] **Output:** Token ID or metadata returned
### **3. Log Token in Sheet**
- [ ] **Tool:** Google Sheets node (or Baserow “Create Record”)
- [ ] **Action:** Add a row with image name, URL, and token value
- [ ] **Output:** Updated sheet record
### **4. Label & Move Image**
- [ ] **Tool:** Google Drive
- [ ] **Action:** Rename or label file with token prefix and move it to the “Tokenized” folder
- [ ] **Output:** Updated file in new location
### **5. Create Database Entry**
- [ ] **Tool:** Notion, Baserow, or Postgres node
- [ ] **Action:** Insert new row/page with image metadata and token info
- [ ] **Output:** Structured database record for reference in the next workflow
---
## Supporting files
[](https://www.notion.soundefined)
[](https://www.notion.soundefined)
[](https://www.notion.soundefined)
Excellent — here’s a **build plan for n8n**, organized by workflow and showing the **tool, trigger, actions, and outputs** for each automation.
---