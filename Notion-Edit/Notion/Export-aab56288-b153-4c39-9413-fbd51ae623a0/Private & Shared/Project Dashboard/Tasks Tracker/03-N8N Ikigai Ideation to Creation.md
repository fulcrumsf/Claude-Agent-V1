---
Status: Done
Priority: High
Task type:
  - Automation
Effort level: Medium
"Priority #": P1
---
### **Idea-to-Production Workflow (Automation #2)**
- **Idea tracker** to manually select and attach a token from the previous workflow.
- **Production trigger** automation to auto-create the image file based on the attached token.
- **Automation to upload image URL** to the sheet for tracking.
- **Status check logic (“Status = Get?”)** to verify readiness.
- **Download-to-Drive automation** for finalized files.
- **Listing Creator** creates listing based on image then logs it to a Google Sheet
- **Google Upload** automatically saves the image to the Google folder
## 🧩 **Workflow 2: Idea-to-Production Automation**
### **1. Manual Idea Selection**
- [ ] **Tool:** Google Sheet or Notion (manual step)
- [ ] **Trigger:** Row status changed to “Ready for Production”
- [ ] **Action:** Workflow triggers when a new “Ready” idea is added
- [ ] **Output:** Idea ID + Token reference
### **2. Auto-Create Image File**
- [ ] **Tool:** ComfyUI / Custom API / Local node
- [ ] **Action:** Generate image based on token + idea details
- [ ] **Output:** New image file URL
### **3. Upload URL to Sheet**
- [ ] **Tool:** Google Sheets or Baserow
- [ ] **Action:** Update the same idea row with the generated image URL
- [ ] **Output:** Updated sheet row
### **4. Status Check**
- [ ] **Tool:** IF node
- [ ] **Condition:** Check if “Status = Get?” or “Image Ready”
- [ ] **Output:** True → continue to next step
### **5. Download to Drive**
- [ ] **Tool:** Google Drive node
- [ ] **Action:** Download or copy generated image to designated production folder
- [ ] **Output:** File stored on Drive
### **6. Create Google Listing**
- [ ] **Tool:** Google Business Profile API or Google Sheets (if listings tracked there)
- [ ] **Action:** Post or record listing with title, description, and image link
- [ ] **Output:** Listing URL or confirmation
---
## 🖐️ **Manual / Semi-Automated Steps**
### **1. Save Locally**
- [ ] **Tool:** Manual
- [ ] **Action:** Download final image batch from Drive to local system
- [ ] **Output:** Local image storage
### **2. Final Upload to Drive**
- [ ] **Tool:** Google Drive node (optional automation)
- [ ] **Action:** Move local or completed images into the “Final Drive” folder
- [ ] **Output:** Organized final archive
---
Would you like me to output this as a **structured n8n build doc** (YAML/JSON flow outline) so you can directly import or reference it while building?
## Supporting files
[](https://www.notion.soundefined)
[](https://www.notion.soundefined)
[](https://www.notion.soundefined)