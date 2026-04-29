---
Category: ComfyUI
tags:
  - nodes
  - reference
  - cheat-sheet
  - inpainting
  - yolo
  - detection
Difficulty: Intermediate
Description: Confirmed working ComfyUI nodes on setup - detection, inpainting, mask utilities, conditioning
---

# 🧭 ComfyUI Node Map (Confirmed Working on Your Setup)

---

### 🔍 Detection (YOLOv8 / Object Detection)

- **UltralyticsModelLoader**
- **CustomUltralyticsModelLoader**
- **UltralyticsInference**
- **BBoxToXYWH**
- **BBoxToCoco**
- **UltralyticsVisualization**
- **ToolYoloCropper** ✅ _(Generates mask from YOLO boxes)_

---

### 🧽 Inpainting (LaMa-style / Mask-based)

- **Load Inpaint Model** ✅ _(Loads LaMa or MAT model)_
- **Inpaint (using Model)** ✅ _(Runs inpainting based on mask)_
- **Fill Masked Area** ✅ _(Simple image fill without diffusion)_
- **Blur Masked Area** ✅ _(Soft blur within mask)_
- **Expand Mask** ✅ _(Grows the mask around its edges)_
- **Denoise to Compositing Mask** ✅ _(Helps blend results)_

---

### 🎭 Mask & Utility

- **ImageColorToMask** ✅ _(Converts specific color to binary mask)_
- **ToolYoloCropper** ✅ _(YOLO detection to mask/crop)_

---

### 🧠 Conditioning / Latent / VAE

- **VAE Encode (for Inpainting)** ✅
- **VAE Encode & Inpaint Conditioning** ✅
- **InpaintModelConditioning** ✅

---

### 🧪 Optional / Experimental

- **Apply Fooocus Inpaint**
- **Load Fooocus Inpaint**
- **ControlNetInpaintingAliMamaApply**
- **WanFunInpaintToVideo**

---

Let me know anytime you need to cross-reference this list during tutorial building. I’ll stick to these names exactly.