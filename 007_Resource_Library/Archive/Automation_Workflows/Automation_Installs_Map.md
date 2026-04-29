---
Category: Automation
tags:
  - system
  - python-environments
  - homebrew
  - comfyui
  - whisper
  - reference
Difficulty: Intermediate
Description: Static reference for Python environments, Homebrew setup, Whisper env, and ComfyUI installs
---

🗓️ _Created: April 5, 2025_

*This is a static file that showed some of my older homebrew environments. Some of this may still be relevant*

---

## 📁 Folder Structure

**~/Documents/Automations/**

- 📂 `Archives/`
    - 📁 `LaMa_Inpainting_Project/`
        - 📁 `Lama/` → Official SAIC LaMa repo clone
            - ✅ Git commit: `786f5936b27fb3dacd2b1ad799e4de968ea697e7` (Feb 5, 2025)
        - 📁 `Models/big-lama/`
            - 📄 `big-lama.ckpt` (410MB) — hard-to-find pre-trained checkpoint model
- 📂 `ShortsEditorAI/`
    - 🧪 `whisper_env/` → Virtual environment (Python 3.11.11) for Whisper transcription
    - ⚠️ `venv/` → Possibly unused or deprecated

---

## 🐍 Python Versions

|Version|Source|Location|
|---|---|---|
|`3.13.2`|Homebrew & Frameworks|`/opt/homebrew/bin/`, `/usr/local/bin/`|
|`3.11.11`|Homebrew|`/opt/homebrew/bin/`|
|`3.10.16`|Homebrew|`/opt/homebrew/bin/`|
|`3.11.11`|venv (Whisper)|`ShortsEditorAI/whisper_env/`|
|`3.13.2`|venv (Remove_Text_From_Image.py)|`ShortsEditorAI/venv/`|

---

## 🧪 Virtual Environments Summary

|Path|Python|Purpose|
|---|---|---|
|`ShortsEditorAI/whisper_env/`|3.11.11|Whisper transcription tools|
|`ShortsEditorAI/venv/`|3.13.2|Possibly unused/test setup|

---

## 🍺 Homebrew

- 📦 Installed: `/opt/homebrew`
- 🔢 Version: `4.4.25`
- 🧼 Clean, Apple Silicon install

---

## 🔍 Whisper Env Packages

Here are notable packages in `whisper_env`:

- 🧠 AI: `torch 2.1.0`, `openai-whisper`, `tiktoken`, `numpy`
- 🔧 Utils: `ffmpeg-python`, `tqdm`, `regex`, `requests`, `dotenv`
- 🌐 Network: `httpx`, `httpcore`, `certifi`
- 🔄 Structure: `pydantic`, `Jinja2`, `sympy`

---

## ✅ Summary

- 🧼 Environments are organized and isolated
- 🍺 Homebrew and Python are cleanly installed in Apple Silicon paths
- 🧠 Whisper environment is stable and production-ready
- 🔒 Archived LaMa repo includes the rare Big LaMa model (`big-lama.ckpt`)

---

## 🧩 Additional System Components (April 5 Update)

| Component                 | Location / Details                                                                    |
| ------------------------- | ------------------------------------------------------------------------------------- |
| ComfyUI                   | `~/Documents/Automations/ComfyUI`                                                     |
| ComfyUI venv              | `~/Documents/Automations/ComfyUI/venv` (Python 3.10.16)                               |
| YOLO Node Extension       | `~/Documents/Automations/ComfyUI/custom_nodes/ComfyUI-YOLO`                           |
| YOLOv8 Model              | `~/Documents/Automations/ComfyUI/models/ultralytics/yolov8n.pt`                       |
| Installed Python Versions | 3.10.16, 3.11.11, 3.13.2 — all in `/opt/homebrew/bin`                                 |
| Whisper Env venv          | `~/Documents/Automations/ShortsEditorAI/whisper_env` (Python 3.11.11)                 |
| ShortsEditorAI venv       | `~/Documents/Automations/ShortsEditorAI/venv` (Python 3.13.2)                         |
| Global Python Packages    | Installed unintentionally — includes `torch`, `openai`, `pillow`, `pytesseract`, etc. |