### Terminal Prompt to List Python System Map
```jsx
(
echo "## 🐍 Python Environment Overview ($(date +%B\ %Y))"
echo -e "\n### 🧱 Installed Python Versions"
which -a python python3 2>/dev/null
ls -1 /opt/homebrew/Cellar/python@* 2>/dev/null
echo -e "\n### 📦 Virtual Environments"
find ~/Documents -type d \( -name 'venv' -o -name '.venv' \) 2>/dev/null
echo -e "\n### 🌐 Global pip3 Packages"
/opt/homebrew/bin/pip3 list 2>/dev/null
echo -e "\n### 📦 ComfyUI venv Packages"
~/Documents/Automations/ComfyUI/venv/bin/pip list 2>/dev/null
echo -e "\n### 📦 ShortsEditorAI venv Packages"
~/Documents/Automations/ShortsEditorAI/venv/bin/pip list 2>/dev/null
) > ~/Desktop/envinfo.md && echo "✅ Full env info saved to ~/Desktop/envinfo.md"
```
---
# 🐍 Python Environment Overview (June 2025)
---
## 🧱 Installed Python Versions
### 🔹 /opt/homebrew/bin/python3
- **Version**: 3.13.3 (Homebrew)
- **Tkinter**: ✅
- **User Site-Packages**:`/Users/tonymacbook2025/Library/Python/3.13/lib/python/site-packages`
- **Packages**:
    
    - pip 25.0
    
    - wheel 0.45.1
    
---
### 🔹 /Library/Frameworks/Python.framework/Versions/3.13/bin/python3
- **Version**: 3.13.2 (Framework)
- **Tkinter**: ✅
- **Packages**:
    
    - torch 2.6.0
    
    - torchvision, torchaudio
    
    - pandas, pillow, opencv-python
    
    - openai, transformers
    
    - pytesseract, moviepy, httpx, fsspec
    
---
### 🔹 /usr/local/bin/python3
- **Version**: 3.13.2 (Alias)
- **Tkinter**: ✅
- **Packages**: _(identical to Framework install above)_
---
### 🔹 /usr/bin/python3
- **Version**: 3.9.6 (System Python)
- **Tkinter**: ✅
- **Packages**:
    
    - pip 21.2.4
    
    - setuptools 58.0.4
    
    - altgraph, future, macholib
    
---
## 📦 Virtual Environments
### 🔸 ComfyUI venv
- **Path**: `/Users/tonymacbook2025/Documents/Automations/ComfyUI/venv`
- **Python**: 3.10.17
- **Key Packages**:
    
    - torch, torchvision, torchaudio
    
    - opencv-python, numpy, scipy, matplotlib, seaborn
    
    - huggingface-hub, transformers, kornia
    
    - rembg, transparent-background, segment-anything
    
    - ultralytics, timm, PIL (11.1.0)
    
---
### 🔸 ShortsEditorAI venv
- **Path**: `/Users/tonymacbook2025/Documents/Automations/ShortsEditorAI/venv`
- **Python**: (Likely 3.11+)
- **Key Packages**:
    
    - openai, opencv-python, pillow
    
    - pytesseract, pydantic, python-dotenv
    
    - httpx, tqdm, numpy
    
---
## ✅ Highlights
- ✅ Tkinter support confirmed across all environments
- ✅ Pillow + OpenCV installed where needed
- ✅ No system conflicts
- ✅ Clean venv structure by project