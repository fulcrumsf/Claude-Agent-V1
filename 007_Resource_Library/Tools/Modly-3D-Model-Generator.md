---
title: "Modly 3D Model Generator"
type: tool-doc
category: video-production
tags:
  - 3d-generation
  - local-ai
  - image-to-3d
created: 2026-05-08
source: local
---

[![Modly logo](https://github.com/lightningpixel/modly/raw/main/resources/icons/icon.png)](https://github.com/lightningpixel/modly/blob/main/resources/icons/icon.png)

## Modly

**Local, open source, AI-powered image-to-3D mesh generation.** Turn any photo into a 3D model using open source AI models running entirely on your GPU. Modly is a desktop application for Windows and Linux (macOS coming soon)

[![Modly screenshot](https://github.com/lightningpixel/modly/raw/main/docs/app-screenshot.png)](https://github.com/lightningpixel/modly/blob/main/docs/app-screenshot.png)

---

## Download

Head to the [Releases](https://github.com/lightningpixel/modly/releases/latest) page to download the latest installer for Windows or Linux.

Alternatively, you can clone the repository and run the app directly without installing:

```
# Windows
launcher.bat

# Linux
./launcher.sh
```

---

## Getting started

### 1\. Install JS dependencies

```
npm install
```

### 2\. Set up Python backend

```
cd api
python -m venv .venv
.venv\Scripts\activate     # Windows
source .venv/bin/activate  # Linux / macOS
pip install -r requirements.txt
```

### 3\. Run in development

```
npm run dev
```

---

## Extension system

Modly supports external AI model extensions. Each extension is a GitHub repository containing a `manifest.json` and a `generator.py`.

### Official extensions

| Extension | Model | URL |
| --- | --- | --- |
| [modly-hunyuan3d-mini-extension](https://github.com/lightningpixel/modly-hunyuan3d-mini-extension) | Hunyuan3D 2 Mini | [https://github.com/lightningpixel/modly-hunyuan3d-mini-extension](https://github.com/lightningpixel/modly-hunyuan3d-mini-extension) |
| [modly-hunyuan3d-mini-turbo-extension](https://github.com/lightningpixel/modly-hunyuan3d-mini-turbo-extension) | Hunyuan3D 2 Mini Turbo | [https://github.com/lightningpixel/modly-hunyuan3d-mini-turbo-extension](https://github.com/lightningpixel/modly-hunyuan3d-mini-turbo-extension) |
| [modly-hunyuan3d-mini-fast-extension](https://github.com/lightningpixel/modly-hunyuan3d-mini-fast-extension) | Hunyuan3D 2 Mini Fast | [https://github.com/lightningpixel/modly-hunyuan3d-mini-fast-extension](https://github.com/lightningpixel/modly-hunyuan3d-mini-fast-extension) |
| [modly-triposg-extension](https://github.com/lightningpixel/modly-triposg-extension) | TripoSG | [https://github.com/lightningpixel/modly-triposg-extension](https://github.com/lightningpixel/modly-triposg-extension) |
| [modly-trellis2-gguf-extension](https://github.com/lightningpixel/modly-trellis2-gguf-extension) | Trellis2 GGUF | [https://github.com/lightningpixel/modly-trellis2-gguf-extension](https://github.com/lightningpixel/modly-trellis2-gguf-extension) |

### How to install an extension

**1.** Go to the **Models** page and click **Install from GitHub**.

[![Install from GitHub](https://github.com/lightningpixel/modly/raw/main/docs/install-from-github.png)](https://github.com/lightningpixel/modly/blob/main/docs/install-from-github.png)

**2.** Enter the HTTPS URL of the extension repository and confirm.

**3.** Once the extension is installed, download the model or one of its variants.

[![Install models](https://github.com/lightningpixel/modly/raw/main/docs/install-models.png)](https://github.com/lightningpixel/modly/blob/main/docs/install-models.png)

---

### Community

Join the [Discord server](https://discord.gg/BvjDCvS3yr) to stay up to date with the latest news, report bugs, and share feedback.

---

## License

MIT License — see [LICENSE](https://github.com/lightningpixel/modly/blob/main/LICENSE) for details.

**If you fork this project and build your own app from it, you must credit the original project and its creator:**

> Based on [Modly](https://github.com/lightningpixel/modly) by [Lightning Pixel](https://github.com/lightningpixel)

This is a requirement of the MIT license attribution clause. Please keep this credit visible in your app's UI or documentation.

[

![Star History Chart](https://camo.githubusercontent.com/3621cb8d9ba0cfa66e1f5b9404e190ae60f532d5af50609c0a6acbb3068d965e/68747470733a2f2f6170692e737461722d686973746f72792e636f6d2f63686172743f7265706f733d6c696768746e696e67706978656c2f6d6f646c7926747970653d74696d656c696e65266c6567656e643d626f74746f6d2d7269676874)

](https://www.star-history.com/?repos=lightningpixel%2Fmodly&type=timeline&legend=top-left)